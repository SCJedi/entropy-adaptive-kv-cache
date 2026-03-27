"""
Combined Entropy-Adaptive Eviction + TurboQuant KV Cache Compression
=====================================================================
Tests three compression approaches on GPT-2 (CPU, eager attention):
  1. Entropy-adaptive eviction only (from kv_cache_compression.py)
  2. TurboQuant-style vector quantization only
  3. Combined: eviction + quantization

TurboQuant implementation:
  Stage 1: Random rotation (QR of Gaussian) + Lloyd-Max scalar quantization
  Stage 2: QJL residual correction via random sign projections

Hardware: CPU only (GPT-2 small)
Expected runtime: ~45-60 minutes
"""

import os
import sys
import json
import time
import math
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PLOT_DIR = Path(__file__).resolve().parent / "plots"
PLOT_DIR.mkdir(exist_ok=True)

device = torch.device('cpu')

# Reproducibility
GLOBAL_SEED = 42
torch.manual_seed(GLOBAL_SEED)
np.random.seed(GLOBAL_SEED)


def timestamp():
    return time.strftime("%H:%M:%S")


###############################################################################
# DATA LOADING (reused pattern from kv_cache_compression.py)
###############################################################################

def load_gpt2_and_data(num_seqs=30, seq_len=128):
    """Load GPT-2 small with eager attention and WikiText-2 validation data."""
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    from datasets import load_dataset

    print(f"[{timestamp()}] Loading GPT-2 small (eager attention)...")
    model = GPT2LMHeadModel.from_pretrained('gpt2', attn_implementation='eager')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    model.to(device)

    print(f"[{timestamp()}] Loading WikiText-2 validation...")
    dataset = load_dataset('wikitext', 'wikitext-2-raw-v1', split='validation')
    full_text = "\n".join([t for t in dataset['text'] if t.strip()])
    all_tokens = tokenizer.encode(full_text)

    sequences = []
    for i in range(0, len(all_tokens) - seq_len, seq_len):
        sequences.append(all_tokens[i:i + seq_len])
    sequences = sequences[:num_seqs]

    print(f"  {len(sequences)} sequences of {seq_len} tokens")
    return model, tokenizer, sequences


###############################################################################
# TURBOQUANT: LLOYD-MAX SCALAR QUANTIZER
###############################################################################

class LloydMaxQuantizer:
    """
    Lloyd-Max optimal scalar quantizer for N(0, sigma^2) distribution.
    Precomputes centroids for 2, 3, 4 bit widths via iterative Lloyd algorithm.
    """

    def __init__(self, seed=42):
        self.rng = np.random.RandomState(seed)
        self.codebooks = {}  # (n_bits, sigma) -> (boundaries, centroids)

    def _lloyd_iteration(self, n_levels: int, sigma: float,
                         max_iter: int = 200, n_samples: int = 100000) -> Tuple[np.ndarray, np.ndarray]:
        """Run Lloyd's algorithm to find optimal centroids for N(0, sigma^2)."""
        samples = self.rng.normal(0, sigma, n_samples)
        samples.sort()

        # Initialize centroids uniformly across [-3*sigma, 3*sigma]
        centroids = np.linspace(-2.5 * sigma, 2.5 * sigma, n_levels)

        for _ in range(max_iter):
            # Assignment step: find boundaries (midpoints between centroids)
            boundaries = (centroids[:-1] + centroids[1:]) / 2.0

            # Update step: compute new centroids as conditional expectations
            new_centroids = np.zeros(n_levels)
            counts = np.zeros(n_levels)

            # Assign each sample to nearest centroid
            indices = np.digitize(samples, boundaries)  # 0..n_levels-1

            for k in range(n_levels):
                mask = (indices == k)
                if mask.sum() > 0:
                    new_centroids[k] = samples[mask].mean()
                    counts[k] = mask.sum()
                else:
                    new_centroids[k] = centroids[k]

            if np.allclose(centroids, new_centroids, atol=1e-8):
                break
            centroids = new_centroids

        boundaries = (centroids[:-1] + centroids[1:]) / 2.0
        return boundaries, centroids

    def get_codebook(self, n_bits: int, sigma: float) -> Tuple[np.ndarray, np.ndarray]:
        """Get or compute Lloyd-Max codebook for given bit-width and sigma."""
        key = (n_bits, round(sigma, 6))
        if key not in self.codebooks:
            n_levels = 2 ** n_bits
            boundaries, centroids = self._lloyd_iteration(n_levels, sigma)
            self.codebooks[key] = (boundaries, centroids)
        return self.codebooks[key]

    def quantize(self, x: np.ndarray, n_bits: int, sigma: float) -> Tuple[np.ndarray, np.ndarray]:
        """Quantize array x. Returns (indices, centroids_used)."""
        boundaries, centroids = self.get_codebook(n_bits, sigma)
        indices = np.digitize(x, boundaries).astype(np.int16)
        return indices, centroids

    def dequantize(self, indices: np.ndarray, n_bits: int, sigma: float) -> np.ndarray:
        """Dequantize indices back to values."""
        _, centroids = self.get_codebook(n_bits, sigma)
        return centroids[indices]


###############################################################################
# TURBOQUANT: RANDOM ROTATION
###############################################################################

class RandomRotation:
    """
    Random orthogonal rotation matrix via QR decomposition of Gaussian matrix.
    One rotation per head dimension, cached and seeded for reproducibility.
    """

    def __init__(self, dim: int, seed: int = 42):
        self.dim = dim
        rng = np.random.RandomState(seed)
        # Generate random Gaussian matrix and compute QR
        G = rng.randn(dim, dim).astype(np.float32)
        Q, R = np.linalg.qr(G)
        # Ensure deterministic sign (Haar measure fix)
        d = np.diag(R)
        sign = np.sign(d)
        sign[sign == 0] = 1
        Q = Q * sign[np.newaxis, :]
        self.Q = torch.from_numpy(Q)        # (dim, dim)
        self.Q_inv = self.Q.T               # Orthogonal, so inverse = transpose

    def rotate(self, x: torch.Tensor) -> torch.Tensor:
        """Apply rotation: x @ Q. x shape: (..., dim)"""
        return x @ self.Q

    def inverse_rotate(self, x: torch.Tensor) -> torch.Tensor:
        """Apply inverse rotation: x @ Q^T"""
        return x @ self.Q_inv


###############################################################################
# TURBOQUANT: QJL RESIDUAL CORRECTION (Stage 2)
###############################################################################

class QJLResidualCorrector:
    """
    Quantized Johnson-Lindenstrauss residual correction.
    Projects residuals through random Gaussian matrix, stores only signs (1 bit each).
    Uses sign bits to correct inner product estimation.
    """

    def __init__(self, dim: int, m_projections: int = 64, seed: int = 42):
        self.dim = dim
        self.m = m_projections
        rng = np.random.RandomState(seed)
        # Random projection matrix scaled by 1/sqrt(m)
        self.proj = torch.from_numpy(
            rng.randn(dim, m_projections).astype(np.float32) / math.sqrt(m_projections)
        )

    def encode(self, residual: torch.Tensor) -> torch.Tensor:
        """Encode residual into sign bits. residual: (..., dim) -> (..., m) signs."""
        projected = residual @ self.proj  # (..., m)
        return (projected >= 0).to(torch.int8)  # 1 bit per projection

    def correct_inner_product(self, sign_bits: torch.Tensor,
                              query: torch.Tensor,
                              residual_norms: torch.Tensor) -> torch.Tensor:
        """
        Estimate <residual, query> from sign bits.
        sign_bits: (n_tokens, m), query: (dim,), residual_norms: (n_tokens,)
        Returns: (n_tokens,) estimated inner products.
        """
        # Project query
        q_proj = query @ self.proj  # (m,)
        # Sign agreement gives direction, scale by residual norm
        signs_float = 2.0 * sign_bits.float() - 1.0  # {-1, +1}
        q_signs = (2.0 * (q_proj >= 0).float() - 1.0)  # {-1, +1}
        agreement = (signs_float * q_signs.unsqueeze(0)).mean(dim=-1)  # (n_tokens,)
        # Scale by norms (approximate)
        q_norm = query.norm()
        correction = agreement * residual_norms * q_norm * math.sqrt(math.pi / 2)
        return correction


###############################################################################
# TURBOQUANT: FULL VECTOR QUANTIZER
###############################################################################

class TurboQuantVectorQuantizer:
    """
    Complete TurboQuant pipeline: Random Rotation + Lloyd-Max + QJL Residual.

    Usage:
        tq = TurboQuantVectorQuantizer(dim=64, n_bits=4)
        compressed = tq.compress(kv_vectors)
        reconstructed = tq.decompress(compressed)
    """

    def __init__(self, dim: int, n_bits: int = 4, m_projections: int = 64,
                 seed: int = 42, use_qjl: bool = True):
        self.dim = dim
        self.n_bits = n_bits
        self.use_qjl = use_qjl

        self.rotation = RandomRotation(dim, seed=seed)
        self.lloyd = LloydMaxQuantizer(seed=seed)
        self.qjl = QJLResidualCorrector(dim, m_projections, seed=seed + 1) if use_qjl else None

        # Precompute codebook for expected sigma after rotation
        # After rotation of vectors from a trained model, coordinates are roughly
        # N(0, sigma^2) where sigma depends on the vector norms.
        # We'll estimate sigma from the data during compress.

    def compress(self, vectors: torch.Tensor) -> dict:
        """
        Compress a batch of vectors.
        vectors: (n_tokens, dim) float32
        Returns dict with compressed representation.
        """
        n_tokens, dim = vectors.shape
        assert dim == self.dim

        # Stage 1: Rotate
        rotated = self.rotation.rotate(vectors)  # (n_tokens, dim)

        # Always estimate sigma from the actual rotated KV data.
        # Round to 2 decimal places so similar sigmas share cached codebooks.
        sigma_raw = float(rotated.std().item())
        if sigma_raw < 1e-8:
            sigma_raw = 1e-4
        sigma = round(sigma_raw, 2)

        # Quantize each coordinate independently
        rot_np = rotated.numpy()
        indices, centroids = self.lloyd.quantize(rot_np.ravel(), self.n_bits, sigma)
        indices = indices.reshape(n_tokens, dim)

        # Reconstruct from stage 1
        recon_np = self.lloyd.dequantize(indices.ravel(), self.n_bits, sigma).reshape(n_tokens, dim)
        recon_rotated = torch.from_numpy(recon_np.astype(np.float32))
        stage1_recon = self.rotation.inverse_rotate(recon_rotated)

        result = {
            'indices': indices,           # int16, (n_tokens, dim)
            'sigma': sigma,
            'n_bits': self.n_bits,
            'n_tokens': n_tokens,
        }

        # Stage 2: QJL residual correction
        if self.use_qjl:
            residual = vectors - stage1_recon  # (n_tokens, dim)
            sign_bits = self.qjl.encode(residual)   # (n_tokens, m)
            residual_norms = residual.norm(dim=-1)    # (n_tokens,)
            result['sign_bits'] = sign_bits
            result['residual_norms'] = residual_norms
            result['stage1_recon'] = stage1_recon
        else:
            result['stage1_recon'] = stage1_recon

        return result

    def decompress(self, compressed: dict) -> torch.Tensor:
        """Decompress back to full vectors (stage 1 reconstruction only for now)."""
        indices = compressed['indices']
        sigma = compressed['sigma']
        n_tokens = compressed['n_tokens']

        recon_np = self.lloyd.dequantize(indices.ravel(), self.n_bits, sigma)
        recon_np = recon_np.reshape(n_tokens, self.dim).astype(np.float32)
        recon_rotated = torch.from_numpy(recon_np)
        return self.rotation.inverse_rotate(recon_rotated)

    def memory_bytes(self, compressed: dict) -> int:
        """Estimate memory usage of compressed representation."""
        n_tokens = compressed['n_tokens']
        # Indices: n_bits per coordinate
        index_bits = n_tokens * self.dim * self.n_bits
        # QJL sign bits
        qjl_bits = 0
        if 'sign_bits' in compressed:
            qjl_bits = compressed['sign_bits'].numel()  # 1 bit each
            qjl_bits += n_tokens * 32  # residual norms (float32)
        # Codebook overhead (negligible)
        codebook_bits = (2 ** self.n_bits) * 32  # float32 centroids
        total_bits = index_bits + qjl_bits + codebook_bits
        return total_bits // 8

    def original_memory_bytes(self, n_tokens: int) -> int:
        """Memory for uncompressed float32 vectors."""
        return n_tokens * self.dim * 4  # float32 = 4 bytes


###############################################################################
# EVICTION MASKS (from kv_cache_compression.py)
###############################################################################

def mask_entropy_adaptive(attn_weights, keep_ratio, head_entropies=None,
                          layer_idx=0, num_heads=12):
    """Per-head adaptive: sparse heads get fewer KV entries, dense heads more."""
    n_heads, seq_len, _ = attn_weights.shape
    mask = torch.zeros_like(attn_weights)

    for h in range(n_heads):
        if head_entropies is not None:
            mean_ent = np.mean(list(head_entropies.values()))
            key = (layer_idx, h)
            this_ent = head_entropies.get(key, mean_ent)
            if mean_ent > 0:
                scale = max(0.3, min(2.5, this_ent / mean_ent))
                adj_ratio = min(1.0, keep_ratio * scale)
            else:
                adj_ratio = keep_ratio
        else:
            adj_ratio = keep_ratio

        for pos in range(seq_len):
            context_len = pos + 1
            k = max(1, int(context_len * adj_ratio))
            if context_len <= k:
                mask[h, pos, :context_len] = 1.0
            else:
                _, topk_idx = attn_weights[h, pos, :context_len].topk(k)
                mask[h, pos, topk_idx] = 1.0
    return mask


###############################################################################
# MONKEY-PATCH MECHANISM
###############################################################################

# Global state for experiments
_compression_state = {
    'active': False,
    'mode': None,           # 'eviction', 'quantization', 'combined', 'entropy_quant'
    'keep_ratio': 1.0,
    'head_entropies': None,
    'layer_counter': 0,
    'n_bits': 4,
    'tq_cache': {},         # layer_idx -> TurboQuantVectorQuantizer instances
    'head_dim': 64,
    'n_heads': 12,
    'use_qjl': True,
    'm_projections': 64,
    # Entropy-informed quantization settings
    'entropy_quant_direction': 'high_fewer',  # 'high_fewer' or 'high_more'
    'entropy_quant_bits_range': (2, 4),       # (min_bits, max_bits)
}


def _get_per_head_bits(layer_idx: int, n_heads: int) -> List[int]:
    """
    Compute per-head bit allocation based on entropy.
    high_fewer: high-entropy heads get fewer bits (they're already noisy)
    high_more: high-entropy heads get more bits (they carry more info)
    """
    state = _compression_state
    head_entropies = state['head_entropies']
    direction = state['entropy_quant_direction']
    min_bits, max_bits = state['entropy_quant_bits_range']

    if head_entropies is None:
        return [state['n_bits']] * n_heads

    # Collect entropies for this layer
    ents = []
    for h in range(n_heads):
        key = (layer_idx, h)
        ents.append(head_entropies.get(key, 0.0))

    ents = np.array(ents)
    if ents.max() - ents.min() < 1e-6:
        return [state['n_bits']] * n_heads

    # Normalize to [0, 1]
    ent_norm = (ents - ents.min()) / (ents.max() - ents.min())

    bits_list = []
    for en in ent_norm:
        if direction == 'high_fewer':
            # High entropy -> fewer bits
            bits = max_bits - en * (max_bits - min_bits)
        else:
            # High entropy -> more bits
            bits = min_bits + en * (max_bits - min_bits)
        bits_list.append(int(round(max(min_bits, min(max_bits, bits)))))

    return bits_list


def _quantize_kv_layer(key_states: torch.Tensor, value_states: torch.Tensor,
                        layer_idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Apply TurboQuant to K and V tensors for one layer.
    key_states, value_states: (batch, heads, seq_len, head_dim)
    Returns reconstructed (batch, heads, seq_len, head_dim)

    Optimized: uses pre-computed TurboQuant objects. Sigma is estimated
    per-call from the actual rotated KV data (rounded to 2 dp for codebook sharing).
    """
    state = _compression_state
    batch, n_heads, seq_len, head_dim = key_states.shape
    mode = state['mode']

    new_keys = torch.zeros_like(key_states)
    new_values = torch.zeros_like(value_states)

    if mode == 'entropy_quant':
        per_head_bits = _get_per_head_bits(layer_idx, n_heads)
    else:
        per_head_bits = [state['n_bits']] * n_heads

    for h in range(n_heads):
        n_bits = per_head_bits[h]

        # Look up pre-computed quantizer (created in main before experiments)
        cache_key = (layer_idx, h, n_bits)
        if cache_key not in state['tq_cache']:
            # Fallback: create on-the-fly if not pre-computed
            seed = GLOBAL_SEED + layer_idx * 100 + h * 10 + n_bits
            state['tq_cache'][cache_key] = TurboQuantVectorQuantizer(
                dim=head_dim, n_bits=n_bits,
                m_projections=state['m_projections'],
                seed=seed, use_qjl=state['use_qjl']
            )
        tq = state['tq_cache'][cache_key]

        # Quantize keys and values for this head using shared sigma
        k_vecs = key_states[0, h]    # (seq_len, head_dim)
        v_vecs = value_states[0, h]  # (seq_len, head_dim)

        k_compressed = tq.compress(k_vecs)
        v_compressed = tq.compress(v_vecs)

        new_keys[0, h] = tq.decompress(k_compressed)
        new_values[0, h] = tq.decompress(v_compressed)

    return new_keys, new_values


def patched_eager_attention_forward(module, query, key, value, attention_mask, **kwargs):
    """Modified eager attention with eviction and/or quantization."""
    state = _compression_state

    # If quantization is active, quantize key/value before attention
    if state['active'] and state['mode'] in ('quantization', 'combined', 'entropy_quant'):
        layer_idx = state['layer_counter']
        key, value = _quantize_kv_layer(key, value, layer_idx)

    attn_weights = torch.matmul(query, key.transpose(-1, -2))

    if module.scale_attn_weights:
        attn_weights = attn_weights / torch.full(
            [], value.size(-1) ** 0.5, dtype=attn_weights.dtype, device=attn_weights.device
        )

    if module.scale_attn_by_inverse_layer_idx:
        attn_weights = attn_weights / float(module.layer_idx + 1)

    if attention_mask is not None:
        attn_weights = attn_weights + attention_mask

    attn_weights = nn.functional.softmax(attn_weights, dim=-1)
    attn_weights = attn_weights.type(value.dtype)
    attn_weights = module.attn_dropout(attn_weights)

    # Eviction (after softmax)
    if state['active'] and state['mode'] in ('eviction', 'combined'):
        keep_ratio = state['keep_ratio']
        layer_idx = state['layer_counter']

        aw = attn_weights[0]  # (heads, seq, seq)
        eviction_mask = mask_entropy_adaptive(
            aw, keep_ratio, state['head_entropies'],
            layer_idx, aw.shape[0])

        # Apply mask and renormalize
        masked_aw = aw * eviction_mask
        row_sums = masked_aw.sum(dim=-1, keepdim=True).clamp(min=1e-10)
        masked_aw = masked_aw / row_sums
        attn_weights = masked_aw.unsqueeze(0)

    if state['active']:
        state['layer_counter'] += 1

    attn_output = torch.matmul(attn_weights, value)
    attn_output = attn_output.transpose(1, 2)

    return attn_output, attn_weights


def install_patch(model):
    """Install the monkey-patched attention forward."""
    import transformers.models.gpt2.modeling_gpt2 as gpt2_module
    gpt2_module.ALL_ATTENTION_FUNCTIONS["eager"] = patched_eager_attention_forward
    print("  Attention patch installed")


###############################################################################
# GENERATION UTILITIES
###############################################################################

def generate_with_compression(model, input_ids: torch.Tensor, max_new_tokens: int = 50,
                               mode: str = None, keep_ratio: float = 1.0,
                               n_bits: int = 4, head_entropies=None,
                               entropy_quant_direction: str = 'high_fewer',
                               use_qjl: bool = True) -> torch.Tensor:
    """
    Autoregressive generation with specified compression.
    mode: None (baseline), 'eviction', 'quantization', 'combined', 'entropy_quant'
    """
    state = _compression_state
    # NOTE: Do NOT clear tq_cache here — pre-computed quantizers are reused across calls

    generated = input_ids.clone()

    for step in range(max_new_tokens):
        # Configure compression state
        if mode is not None:
            state['active'] = True
            state['mode'] = mode
            state['keep_ratio'] = keep_ratio
            state['n_bits'] = n_bits
            state['head_entropies'] = head_entropies
            state['layer_counter'] = 0
            state['use_qjl'] = use_qjl
            state['entropy_quant_direction'] = entropy_quant_direction
            # NOTE: tq_cache preserved — reuse pre-computed TurboQuant objects
        else:
            state['active'] = False

        with torch.no_grad():
            outputs = model(generated)

        state['active'] = False

        next_token_logits = outputs.logits[0, -1, :]
        next_token = next_token_logits.argmax(dim=-1, keepdim=True)
        generated = torch.cat([generated, next_token.unsqueeze(0)], dim=-1)

    return generated


def compute_perplexity(model, input_ids: torch.Tensor, mode: str = None,
                       keep_ratio: float = 1.0, n_bits: int = 4,
                       head_entropies=None, entropy_quant_direction: str = 'high_fewer',
                       use_qjl: bool = True) -> float:
    """Compute perplexity of input sequence under the (possibly compressed) model."""
    state = _compression_state
    # NOTE: Do NOT clear tq_cache — reuse pre-computed TurboQuant objects

    if mode is not None:
        state['active'] = True
        state['mode'] = mode
        state['keep_ratio'] = keep_ratio
        state['n_bits'] = n_bits
        state['head_entropies'] = head_entropies
        state['layer_counter'] = 0
        state['use_qjl'] = use_qjl
        state['entropy_quant_direction'] = entropy_quant_direction
    else:
        state['active'] = False

    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)

    state['active'] = False
    loss = outputs.loss.item()
    return math.exp(loss)


###############################################################################
# QUALITY METRICS
###############################################################################

def compute_bleu(reference_tokens: List[int], hypothesis_tokens: List[int],
                 max_n: int = 4) -> float:
    """Simple BLEU score (no smoothing) between token sequences."""
    if len(hypothesis_tokens) == 0:
        return 0.0

    # Brevity penalty
    bp = min(1.0, math.exp(1 - len(reference_tokens) / max(len(hypothesis_tokens), 1)))

    # n-gram precisions
    log_avg = 0.0
    n_valid = 0
    for n in range(1, max_n + 1):
        ref_ngrams = defaultdict(int)
        for i in range(len(reference_tokens) - n + 1):
            ng = tuple(reference_tokens[i:i + n])
            ref_ngrams[ng] += 1

        hyp_ngrams = defaultdict(int)
        for i in range(len(hypothesis_tokens) - n + 1):
            ng = tuple(hypothesis_tokens[i:i + n])
            hyp_ngrams[ng] += 1

        matches = 0
        total = 0
        for ng, count in hyp_ngrams.items():
            matches += min(count, ref_ngrams.get(ng, 0))
            total += count

        if total > 0 and matches > 0:
            log_avg += math.log(matches / total)
            n_valid += 1

    if n_valid == 0:
        return 0.0

    return bp * math.exp(log_avg / n_valid)


def compute_rouge_l(reference: List[int], hypothesis: List[int]) -> float:
    """ROUGE-L F1 based on longest common subsequence."""
    if not reference or not hypothesis:
        return 0.0

    m, n = len(reference), len(hypothesis)
    # Optimize: use 1D DP
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if reference[i - 1] == hypothesis[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(curr[j - 1], prev[j])
        prev = curr

    lcs_len = prev[n]
    if lcs_len == 0:
        return 0.0
    prec = lcs_len / n
    recall = lcs_len / m
    return 2 * prec * recall / (prec + recall)


def compute_metrics(ref_tokens: List[int], hyp_tokens: List[int]) -> dict:
    """Compute all quality metrics between reference and hypothesis token lists."""
    # Token match rate
    min_len = min(len(ref_tokens), len(hyp_tokens))
    if min_len == 0:
        match_rate = 0.0
    else:
        matches = sum(1 for a, b in zip(ref_tokens[:min_len], hyp_tokens[:min_len]) if a == b)
        match_rate = matches / min_len

    bleu = compute_bleu(ref_tokens, hyp_tokens)
    rouge_l = compute_rouge_l(ref_tokens, hyp_tokens)

    return {
        'bleu': bleu,
        'rouge_l': rouge_l,
        'token_match': match_rate,
    }


def compute_compression_ratio(mode: str, keep_ratio: float, n_bits: int,
                                head_dim: int = 64) -> float:
    """
    Compute effective compression ratio.
    Full cache = float16 (16 bits per value per dim for K and V).
    """
    original_bits_per_dim = 16  # float16

    if mode == 'eviction':
        # We keep keep_ratio fraction of tokens
        return 1.0 / keep_ratio

    elif mode == 'quantization':
        # Each dim goes from 16 bits to n_bits
        return original_bits_per_dim / n_bits

    elif mode == 'combined':
        # Eviction reduces tokens, quantization reduces bits per dim
        eviction_factor = 1.0 / keep_ratio
        quant_factor = original_bits_per_dim / n_bits
        return eviction_factor * quant_factor

    elif mode == 'entropy_quant':
        # Approximate: average bits across heads
        quant_factor = original_bits_per_dim / n_bits  # n_bits is average
        return quant_factor

    return 1.0


###############################################################################
# HEAD ENTROPY COLLECTION
###############################################################################

def collect_head_entropies(model, sequences, num_seqs=20, seq_len=128):
    """Collect per-head entropy statistics from baseline forward passes."""
    print(f"[{timestamp()}] Collecting per-head entropies...")
    _compression_state['active'] = False

    head_entropies = defaultdict(list)
    num_heads = model.config.n_head

    t0 = time.time()
    for seq_idx in range(min(num_seqs, len(sequences))):
        if seq_idx % 5 == 0:
            print(f"  Sequence {seq_idx + 1}/{min(num_seqs, len(sequences))} "
                  f"({time.time() - t0:.0f}s)")
        input_ids = torch.tensor([sequences[seq_idx]], device=device)

        with torch.no_grad():
            outputs = model(input_ids, output_attentions=True)

        for layer_idx, attn_tensor in enumerate(outputs.attentions):
            attn = attn_tensor[0].detach()  # (heads, seq, seq)
            for head_idx in range(num_heads):
                for pos in [seq_len // 4, seq_len // 2, 3 * seq_len // 4, seq_len - 1]:
                    row = attn[head_idx, pos, :pos + 1]
                    row_pos = row[row > 1e-10]
                    entropy = -(row_pos * torch.log2(row_pos)).sum().item() if len(row_pos) > 0 else 0.0
                    head_entropies[(layer_idx, head_idx)].append(entropy)

    means = {k: float(np.mean(v)) for k, v in head_entropies.items()}
    print(f"  Entropy range: {min(means.values()):.2f} - {max(means.values()):.2f} bits")
    return means


###############################################################################
# EXPERIMENT CONFIGURATIONS
###############################################################################

def get_experiment_configs():
    """Define all experiment configurations."""
    configs = []

    # 1. Full cache baseline
    configs.append({
        'name': 'full_cache',
        'mode': None,
        'keep_ratio': 1.0,
        'n_bits': 16,
        'description': 'Full KV cache (baseline)',
    })

    # 2. Eviction only
    for evict_factor in [2, 4]:
        keep = 1.0 / evict_factor
        configs.append({
            'name': f'eviction_{evict_factor}x',
            'mode': 'eviction',
            'keep_ratio': keep,
            'n_bits': 16,
            'description': f'Entropy-adaptive eviction {evict_factor}x',
        })

    # 3. Quantization only
    for bits in [4, 3, 2]:
        configs.append({
            'name': f'quant_{bits}bit',
            'mode': 'quantization',
            'keep_ratio': 1.0,
            'n_bits': bits,
            'description': f'TurboQuant {bits}-bit quantization',
        })

    # 4. Combined eviction + quantization
    for evict_factor in [2, 3]:
        for bits in [4, 3]:
            keep = 1.0 / evict_factor
            configs.append({
                'name': f'combined_{evict_factor}x_{bits}bit',
                'mode': 'combined',
                'keep_ratio': keep,
                'n_bits': bits,
                'description': f'Eviction {evict_factor}x + TurboQuant {bits}-bit',
            })

    # 5. Entropy-informed quantization (high-entropy -> fewer bits)
    configs.append({
        'name': 'entropy_quant_high_fewer',
        'mode': 'entropy_quant',
        'keep_ratio': 1.0,
        'n_bits': 3,  # average target
        'description': 'Entropy-informed quant (high entropy -> fewer bits)',
        'entropy_quant_direction': 'high_fewer',
    })

    # 6. Entropy-informed quantization (high-entropy -> more bits)
    configs.append({
        'name': 'entropy_quant_high_more',
        'mode': 'entropy_quant',
        'keep_ratio': 1.0,
        'n_bits': 3,  # average target
        'description': 'Entropy-informed quant (high entropy -> more bits)',
        'entropy_quant_direction': 'high_more',
    })

    return configs


###############################################################################
# MAIN EXPERIMENT LOOP
###############################################################################

def run_experiment(model, tokenizer, sequences, head_entropies, configs,
                   num_seqs=30, gen_tokens=50):
    """Run all experiment configurations and collect metrics."""
    print(f"\n{'=' * 70}")
    print(f"[{timestamp()}] RUNNING COMBINED COMPRESSION EXPERIMENT")
    print(f"{'=' * 70}")
    print(f"  {len(configs)} configurations, {num_seqs} sequences, {gen_tokens} gen tokens")

    seq_len = len(sequences[0])
    results = {}

    # Generate baseline references first
    print(f"\n[{timestamp()}] Generating baseline references...")
    baseline_generations = []
    baseline_perplexities = []
    t0 = time.time()

    for seq_idx in range(num_seqs):
        if seq_idx % 2 == 0:
            print(f"  Baseline seq {seq_idx + 1}/{num_seqs} ({time.time() - t0:.0f}s)", flush=True)
        input_ids = torch.tensor([sequences[seq_idx]], device=device)

        gen = generate_with_compression(model, input_ids, max_new_tokens=gen_tokens, mode=None)
        baseline_generations.append(gen[0, seq_len:].tolist())

        ppl = compute_perplexity(model, input_ids, mode=None)
        baseline_perplexities.append(ppl)

    baseline_ppl = float(np.mean(baseline_perplexities))
    print(f"  Baseline mean perplexity: {baseline_ppl:.2f}")

    # Run each configuration
    for cfg_idx, cfg in enumerate(configs):
        name = cfg['name']
        mode = cfg['mode']
        keep_ratio = cfg.get('keep_ratio', 1.0)
        n_bits = cfg.get('n_bits', 4)
        direction = cfg.get('entropy_quant_direction', 'high_fewer')

        print(f"\n[{timestamp()}] Config {cfg_idx + 1}/{len(configs)}: {name}")
        print(f"  {cfg['description']}")

        if mode is None:
            # Baseline already computed
            results[name] = {
                'description': cfg['description'],
                'mode': 'baseline',
                'keep_ratio': 1.0,
                'n_bits': 16,
                'compression_ratio': 1.0,
                'bleu': 1.0,
                'rouge_l': 1.0,
                'token_match': 1.0,
                'perplexity': baseline_ppl,
                'perplexity_ratio': 1.0,
                'wall_clock_seconds': 0.0,
            }
            print(f"  (using cached baseline)")
            continue

        t_start = time.time()
        all_bleu = []
        all_rouge = []
        all_match = []
        all_ppl = []

        for seq_idx in range(num_seqs):
            if seq_idx % 2 == 0:
                elapsed = time.time() - t_start
                print(f"  Seq {seq_idx + 1}/{num_seqs} ({elapsed:.0f}s)", flush=True)

            input_ids = torch.tensor([sequences[seq_idx]], device=device)

            try:
                # Generate
                gen = generate_with_compression(
                    model, input_ids, max_new_tokens=gen_tokens,
                    mode=mode, keep_ratio=keep_ratio, n_bits=n_bits,
                    head_entropies=head_entropies,
                    entropy_quant_direction=direction,
                    use_qjl=True
                )
                hyp_tokens = gen[0, seq_len:].tolist()
                ref_tokens = baseline_generations[seq_idx]

                metrics = compute_metrics(ref_tokens, hyp_tokens)
                all_bleu.append(metrics['bleu'])
                all_rouge.append(metrics['rouge_l'])
                all_match.append(metrics['token_match'])

                # Perplexity
                ppl = compute_perplexity(
                    model, input_ids, mode=mode, keep_ratio=keep_ratio,
                    n_bits=n_bits, head_entropies=head_entropies,
                    entropy_quant_direction=direction, use_qjl=True
                )
                all_ppl.append(ppl)

            except Exception as e:
                print(f"    ERROR on seq {seq_idx}: {e}")
                all_bleu.append(0.0)
                all_rouge.append(0.0)
                all_match.append(0.0)
                all_ppl.append(float('inf'))

        wall_clock = time.time() - t_start
        compression_ratio = compute_compression_ratio(mode, keep_ratio, n_bits)
        mean_ppl = float(np.mean([p for p in all_ppl if p != float('inf')]) if all_ppl else float('inf'))

        results[name] = {
            'description': cfg['description'],
            'mode': mode,
            'keep_ratio': keep_ratio,
            'n_bits': n_bits,
            'compression_ratio': compression_ratio,
            'bleu': float(np.mean(all_bleu)),
            'rouge_l': float(np.mean(all_rouge)),
            'token_match': float(np.mean(all_match)),
            'perplexity': mean_ppl,
            'perplexity_ratio': mean_ppl / baseline_ppl if baseline_ppl > 0 else float('inf'),
            'wall_clock_seconds': wall_clock,
        }

        r = results[name]
        print(f"  BLEU={r['bleu']:.4f}  ROUGE-L={r['rouge_l']:.4f}  "
              f"Match={r['token_match']:.4f}  PPL_ratio={r['perplexity_ratio']:.3f}  "
              f"Compress={r['compression_ratio']:.1f}x  Time={wall_clock:.1f}s")

    return results


###############################################################################
# RESULTS TABLE
###############################################################################

def print_results_table(results: dict):
    """Print a formatted comparison table."""
    print(f"\n{'=' * 100}")
    print(f"COMBINED COMPRESSION RESULTS")
    print(f"{'=' * 100}")

    header = (f"{'Config':<30s} {'Compress':>8s} {'BLEU':>8s} {'ROUGE-L':>8s} "
              f"{'Match':>8s} {'PPL ratio':>10s} {'Time(s)':>8s}")
    print(header)
    print("-" * 100)

    # Sort by compression ratio
    sorted_names = sorted(results.keys(),
                          key=lambda k: results[k]['compression_ratio'])

    for name in sorted_names:
        r = results[name]
        ppl_str = f"{r['perplexity_ratio']:.3f}" if r['perplexity_ratio'] < 100 else ">100"
        print(f"{name:<30s} {r['compression_ratio']:>7.1f}x {r['bleu']:>8.4f} "
              f"{r['rouge_l']:>8.4f} {r['token_match']:>8.4f} {ppl_str:>10s} "
              f"{r['wall_clock_seconds']:>8.1f}")

    print("-" * 100)

    # Find best combined config
    combined = {k: v for k, v in results.items() if 'combined' in k}
    if combined:
        best_combined = max(combined.items(), key=lambda x: x[1]['bleu'])
        print(f"\nBest combined config: {best_combined[0]}")
        print(f"  BLEU={best_combined[1]['bleu']:.4f}, "
              f"Compression={best_combined[1]['compression_ratio']:.1f}x")

    # Compare entropy-informed directions
    eq_fewer = results.get('entropy_quant_high_fewer')
    eq_more = results.get('entropy_quant_high_more')
    if eq_fewer and eq_more:
        print(f"\nEntropy-informed quantization comparison:")
        print(f"  High entropy -> fewer bits: BLEU={eq_fewer['bleu']:.4f}")
        print(f"  High entropy -> more bits:  BLEU={eq_more['bleu']:.4f}")
        winner = "fewer" if eq_fewer['bleu'] >= eq_more['bleu'] else "more"
        print(f"  -> Better: high entropy -> {winner} bits")


###############################################################################
# TURBOQUANT UNIT TESTS
###############################################################################

def verify_turboquant():
    """Quick sanity checks for TurboQuant components."""
    print(f"\n[{timestamp()}] Verifying TurboQuant implementation...")

    dim = 64
    n_tokens = 16

    # Test rotation is orthogonal
    rot = RandomRotation(dim, seed=42)
    identity_check = rot.Q @ rot.Q.T
    eye_err = (identity_check - torch.eye(dim)).abs().max().item()
    print(f"  Rotation orthogonality error: {eye_err:.2e} (should be < 1e-5)")
    assert eye_err < 1e-4, f"Rotation not orthogonal: {eye_err}"

    # Test roundtrip with high bits
    tq = TurboQuantVectorQuantizer(dim=dim, n_bits=4, seed=42, use_qjl=False)
    vectors = torch.randn(n_tokens, dim) * 0.5
    compressed = tq.compress(vectors)
    recon = tq.decompress(compressed)
    mse = ((vectors - recon) ** 2).mean().item()
    rel_err = mse / (vectors ** 2).mean().item()
    print(f"  4-bit roundtrip relative MSE: {rel_err:.4f}")

    # Test 2-bit
    tq2 = TurboQuantVectorQuantizer(dim=dim, n_bits=2, seed=42, use_qjl=False)
    compressed2 = tq2.compress(vectors)
    recon2 = tq2.decompress(compressed2)
    mse2 = ((vectors - recon2) ** 2).mean().item()
    rel_err2 = mse2 / (vectors ** 2).mean().item()
    print(f"  2-bit roundtrip relative MSE: {rel_err2:.4f}")
    assert rel_err2 > rel_err, "2-bit should have higher error than 4-bit"

    # Test compression ratio
    orig_bytes = tq.original_memory_bytes(n_tokens)
    comp_bytes = tq.memory_bytes(compressed)
    print(f"  4-bit compression: {orig_bytes} -> {comp_bytes} bytes "
          f"({orig_bytes / max(comp_bytes, 1):.1f}x)")

    # Test QJL
    tq_qjl = TurboQuantVectorQuantizer(dim=dim, n_bits=4, seed=42, use_qjl=True)
    compressed_qjl = tq_qjl.compress(vectors)
    assert 'sign_bits' in compressed_qjl, "QJL sign bits missing"
    print(f"  QJL sign bits shape: {compressed_qjl['sign_bits'].shape}")

    # Test Lloyd-Max codebook
    lloyd = LloydMaxQuantizer(seed=42)
    bounds, cents = lloyd.get_codebook(2, 1.0)
    print(f"  2-bit codebook: {len(cents)} centroids, bounds={bounds}")
    assert len(cents) == 4, "2-bit should have 4 centroids"
    assert len(bounds) == 3, "2-bit should have 3 boundaries"

    print(f"  All TurboQuant verifications passed.")
    return True


def verify_patch(model, sequences):
    """Verify the monkey-patch actually changes outputs."""
    print(f"\n[{timestamp()}] Verifying attention patch works...")
    input_ids = torch.tensor([sequences[0]], device=device)

    # Baseline
    _compression_state['active'] = False
    with torch.no_grad():
        baseline_out = model(input_ids)
    baseline_logits = baseline_out.logits[0].detach()

    # With quantization
    _compression_state['active'] = True
    _compression_state['mode'] = 'quantization'
    _compression_state['n_bits'] = 2
    _compression_state['layer_counter'] = 0
    _compression_state['tq_cache'] = {}
    _compression_state['use_qjl'] = False
    _compression_state['head_dim'] = model.config.n_embd // model.config.n_head
    _compression_state['n_heads'] = model.config.n_head

    with torch.no_grad():
        quant_out = model(input_ids)
    _compression_state['active'] = False
    quant_logits = quant_out.logits[0].detach()

    diff = (baseline_logits - quant_logits).abs().max().item()
    match_rate = (baseline_logits.argmax(-1) == quant_logits.argmax(-1)).float().mean().item()

    print(f"  Max logit difference (2-bit quant vs full): {diff:.4f}")
    print(f"  Prediction match rate: {match_rate:.4f}")

    if diff < 1e-6:
        print("  WARNING: Patch may not be working! Logits are identical.")
        return False
    else:
        print(f"  Patch verified: logits differ (max diff = {diff:.4f})")
        return True


###############################################################################
# MAIN
###############################################################################

def main():
    print(f"{'=' * 70}")
    print(f"COMBINED ENTROPY-ADAPTIVE EVICTION + TURBOQUANT EXPERIMENT")
    print(f"{'=' * 70}")
    print(f"Start time: {timestamp()}")
    print(f"Device: {device}")
    t_total = time.time()

    # Verify TurboQuant implementation
    if not verify_turboquant():
        print("ABORTING: TurboQuant verification failed.")
        return None

    # Load model and data (reduced for CPU feasibility)
    model, tokenizer, sequences = load_gpt2_and_data(num_seqs=10, seq_len=128)

    # Configure state
    _compression_state['head_dim'] = model.config.n_embd // model.config.n_head
    _compression_state['n_heads'] = model.config.n_head

    # Install attention patch
    install_patch(model)

    # Verify patch works
    if not verify_patch(model, sequences):
        print("ABORTING: Patch verification failed.")
        return None

    # Collect head entropies (reduced for speed)
    head_entropies = collect_head_entropies(model, sequences, num_seqs=5, seq_len=128)

    # Pre-compute TurboQuant objects (rotations, QJL projectors)
    # Sigma will be estimated per-call from actual KV data — no shared sigma needed.
    print(f"\n[{timestamp()}] Pre-computing TurboQuant objects...")
    t_precompute = time.time()
    head_dim = _compression_state['head_dim']
    n_heads = _compression_state['n_heads']
    n_layers = model.config.n_layer  # 12 for GPT-2

    # Pre-create all TurboQuant objects: 12 layers x 12 heads x {2,3,4} bits = up to 432 objects
    # This avoids creating RandomRotation and QJL matrices during the experiment loop.
    # A single shared LloydMaxQuantizer caches codebooks across all TQ objects so that
    # calls with the same (n_bits, rounded_sigma) reuse the same codebook.
    all_bits = {2, 3, 4}  # All bit widths used across configs
    lloyd_shared = LloydMaxQuantizer(seed=GLOBAL_SEED)
    tq_cache = {}
    for layer_idx in range(n_layers):
        for h in range(n_heads):
            for n_bits in all_bits:
                cache_key = (layer_idx, h, n_bits)
                seed = GLOBAL_SEED + layer_idx * 100 + h * 10 + n_bits
                tq_obj = TurboQuantVectorQuantizer(
                    dim=head_dim, n_bits=n_bits,
                    m_projections=_compression_state['m_projections'],
                    seed=seed, use_qjl=True
                )
                # Share the lloyd instance so codebook cache is shared across all objects
                tq_obj.lloyd = lloyd_shared
                tq_cache[cache_key] = tq_obj
    _compression_state['tq_cache'] = tq_cache
    print(f"  Pre-computed {len(tq_cache)} TurboQuant objects in {time.time() - t_precompute:.1f}s")
    print(f"  Sigma will be estimated per-call from actual rotated KV data (rounded to 2dp)")

    # Get experiment configs
    configs = get_experiment_configs()
    print(f"\n  Experiment configurations ({len(configs)} total):")
    for cfg in configs:
        print(f"    - {cfg['name']}: {cfg['description']}")

    # Run experiments (reduced for CPU feasibility)
    num_seqs = min(8, len(sequences))
    gen_tokens = 20
    results = run_experiment(model, tokenizer, sequences, head_entropies,
                             configs, num_seqs=num_seqs, gen_tokens=gen_tokens)

    # Print comparison table
    print_results_table(results)

    # Save results
    results_path = PLOT_DIR / 'combined_compression_results.json'
    serializable = {}
    for k, v in results.items():
        serializable[k] = {sk: (float(sv) if isinstance(sv, (np.floating, float)) else sv)
                           for sk, sv in v.items()}

    output = {
        'experiment': 'combined_entropy_turboquant',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'config': {
            'num_sequences': num_seqs,
            'seq_len': 128,
            'gen_tokens': gen_tokens,
            'model': 'gpt2',
            'device': str(device),
            'seed': GLOBAL_SEED,
        },
        'head_entropies': {f"L{k[0]}_H{k[1]}": v for k, v in head_entropies.items()},
        'results': serializable,
        'runtime_seconds': time.time() - t_total,
    }

    with open(results_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Results saved to {results_path}")

    total_time = time.time() - t_total
    print(f"\n{'=' * 70}")
    print(f"COMPLETE - Total runtime: {total_time / 60:.1f} minutes")
    print(f"{'=' * 70}")

    return results


if __name__ == '__main__':
    results = main()
