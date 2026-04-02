"""
Entropy-Adaptive TurboQuant: Phase 1 Experiments
=================================================
Tests per-head bit allocation and per-head quantization skipping
for TurboQuant KV cache compression on GPT-2.

Builds on combined_compression.py — reuses TurboQuant classes,
metrics, generation, and monkey-patch mechanism.

Configurations tested:
  1. uniform_3bit          — baseline: all heads at 3-bit
  2. uniform_4bit          — baseline: all heads at 4-bit
  3. adaptive_3bit_conservative — per-head bits, avg 3, alpha=0.25
  4. adaptive_3bit_aggressive   — per-head bits, avg 3, alpha=0.50
  5. adaptive_4bit_conservative — per-head bits, avg 4, alpha=0.25
  6. skip_top3_uniform_3bit     — skip 3 lowest-H2 heads, rest 3-bit
  7. skip_top3_adaptive_3bit    — skip 3 + adaptive for rest
  8. combined_best              — skip 3 + adaptive 4-bit conservative

Expected runtime: ~30-45 minutes on CPU
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
from typing import Dict, List, Optional, Tuple, Set

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
# IMPORT TURBOQUANT CLASSES FROM combined_compression.py
###############################################################################

# We import the core classes and functions to avoid code duplication
sys.path.insert(0, str(Path(__file__).resolve().parent))
from combined_compression import (
    LloydMaxQuantizer,
    RandomRotation,
    QJLResidualCorrector,
    TurboQuantVectorQuantizer,
    load_gpt2_and_data,
    compute_bleu,
    compute_rouge_l,
    compute_metrics,
    collect_head_entropies,
    verify_turboquant,
    _compression_state,
)


###############################################################################
# ENTROPY-ADAPTIVE BIT ALLOCATION
###############################################################################

def compute_optimal_bits(head_entropies: Dict[Tuple[int, int], float],
                         avg_bits: float,
                         alpha: float = 0.25,
                         min_bits: int = 2,
                         max_bits: int = 5,
                         n_layers: int = 12,
                         n_heads: int = 12) -> Dict[Tuple[int, int], int]:
    """
    Compute per-head bit allocation using the entropy-adaptive formula:
        b_h = b_bar + alpha * (H_bar - H_2(h))

    Low-entropy heads (concentrated attention) get MORE bits because
    quantization error passes through at full magnitude.

    Args:
        head_entropies: {(layer, head): entropy_bits}
        avg_bits: target average bits per head
        alpha: scaling factor (0.25 conservative, 0.50 aggressive)
        min_bits, max_bits: clamp range
        n_layers, n_heads: model dimensions

    Returns:
        {(layer, head): allocated_bits}
    """
    all_ents = list(head_entropies.values())
    H_bar = np.mean(all_ents)

    # Phase 1: compute continuous allocations
    continuous = {}
    for (layer, head), ent in head_entropies.items():
        b_h = avg_bits + alpha * (H_bar - ent)
        b_h = max(min_bits, min(max_bits, b_h))
        continuous[(layer, head)] = b_h

    # Phase 2: round to integers
    rounded = {k: int(round(v)) for k, v in continuous.items()}

    # Phase 3: budget correction
    total_budget = len(head_entropies) * avg_bits
    current_total = sum(rounded.values())
    deficit = int(round(total_budget - current_total))

    if deficit != 0:
        # Sort by how close to a rounding boundary each head is
        # (i.e., heads where rounding was a close call)
        fractional_parts = {k: abs(continuous[k] - rounded[k]) for k in continuous}

        if deficit > 0:
            # Need more bits — round up heads that were closest to rounding up
            candidates = sorted(
                [k for k in rounded if rounded[k] < max_bits],
                key=lambda k: fractional_parts[k]
            )
            for i in range(min(deficit, len(candidates))):
                rounded[candidates[i]] += 1
        else:
            # Need fewer bits — round down heads that were closest to rounding down
            candidates = sorted(
                [k for k in rounded if rounded[k] > min_bits],
                key=lambda k: fractional_parts[k]
            )
            for i in range(min(-deficit, len(candidates))):
                rounded[candidates[i]] -= 1

    return rounded


def identify_skip_heads(head_entropies: Dict[Tuple[int, int], float],
                        max_skip_fraction: float = 0.15,
                        max_skip_count: int = None) -> Set[Tuple[int, int]]:
    """
    Identify heads that should skip quantization (keep at fp16).

    Selects heads with lowest entropy (highest error sensitivity) up to
    max_skip_fraction of total heads.

    Args:
        head_entropies: {(layer, head): entropy_bits}
        max_skip_fraction: maximum fraction of heads to skip
        max_skip_count: if specified, overrides fraction-based limit

    Returns:
        Set of (layer, head) tuples to skip
    """
    total_heads = len(head_entropies)
    if max_skip_count is not None:
        max_skip = max_skip_count
    else:
        max_skip = int(total_heads * max_skip_fraction)

    # Sort by entropy ascending (lowest first = highest error contribution)
    sorted_heads = sorted(head_entropies.items(), key=lambda x: x[1])

    skip_set = set()
    for (layer, head), ent in sorted_heads[:max_skip]:
        skip_set.add((layer, head))

    return skip_set


def compute_adaptive_bits_with_skip(
    head_entropies: Dict[Tuple[int, int], float],
    skip_heads: Set[Tuple[int, int]],
    target_avg_bits: float,
    alpha: float = 0.25,
    min_bits: int = 2,
    max_bits: int = 5,
) -> Dict[Tuple[int, int], int]:
    """
    Compute per-head bit allocation AFTER accounting for skipped heads.

    Skipped heads use 16 bits, so remaining heads must use fewer bits
    to maintain the overall budget.

    Returns:
        {(layer, head): bits} — skipped heads get 16, others get adaptive allocation
    """
    total_heads = len(head_entropies)
    total_budget = total_heads * target_avg_bits
    skip_cost = len(skip_heads) * 16
    remaining_budget = total_budget - skip_cost
    remaining_heads = total_heads - len(skip_heads)

    if remaining_heads <= 0 or remaining_budget <= 0:
        # Edge case: can't skip that many
        return {k: int(round(target_avg_bits)) for k in head_entropies}

    adj_avg = remaining_budget / remaining_heads
    adj_avg = max(min_bits, min(max_bits, adj_avg))

    # Get entropies for non-skipped heads only
    non_skip_ents = {k: v for k, v in head_entropies.items() if k not in skip_heads}

    # Allocate bits for non-skipped heads
    non_skip_bits = compute_optimal_bits(
        non_skip_ents, adj_avg, alpha, min_bits, max_bits
    )

    # Combine
    result = {}
    for k in head_entropies:
        if k in skip_heads:
            result[k] = 16  # fp16, no quantization
        else:
            result[k] = non_skip_bits[k]

    return result


###############################################################################
# MODIFIED QUANTIZATION LAYER (supports per-head bits and skipping)
###############################################################################

def _quantize_kv_layer_adaptive(
    key_states: torch.Tensor,
    value_states: torch.Tensor,
    layer_idx: int,
    per_head_bits: Dict[Tuple[int, int], int],
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Apply TurboQuant with per-head bit allocation to K and V tensors.
    Heads assigned 16 bits are skipped (kept as-is).
    """
    state = _compression_state
    batch, n_heads, seq_len, head_dim = key_states.shape

    new_keys = torch.zeros_like(key_states)
    new_values = torch.zeros_like(value_states)

    for h in range(n_heads):
        n_bits = per_head_bits.get((layer_idx, h), state['n_bits'])

        if n_bits >= 16:
            # Skip quantization — keep original
            new_keys[0, h] = key_states[0, h]
            new_values[0, h] = value_states[0, h]
            continue

        # Get or create TurboQuant object
        cache_key = (layer_idx, h, n_bits)
        if cache_key not in state['tq_cache']:
            seed = GLOBAL_SEED + layer_idx * 100 + h * 10 + n_bits
            state['tq_cache'][cache_key] = TurboQuantVectorQuantizer(
                dim=head_dim, n_bits=n_bits,
                m_projections=state['m_projections'],
                seed=seed, use_qjl=state['use_qjl']
            )
        tq = state['tq_cache'][cache_key]

        k_vecs = key_states[0, h]
        v_vecs = value_states[0, h]

        k_compressed = tq.compress(k_vecs)
        v_compressed = tq.compress(v_vecs)

        new_keys[0, h] = tq.decompress(k_compressed)
        new_values[0, h] = tq.decompress(v_compressed)

    return new_keys, new_values


###############################################################################
# PATCHED ATTENTION FORWARD (supports adaptive mode)
###############################################################################

def patched_eager_attention_forward_adaptive(module, query, key, value, attention_mask, **kwargs):
    """Modified eager attention with adaptive per-head quantization."""
    state = _compression_state

    if state['active'] and state['mode'] in ('adaptive_quant',):
        layer_idx = state['layer_counter']
        per_head_bits = state.get('per_head_bits', {})
        key, value = _quantize_kv_layer_adaptive(key, value, layer_idx, per_head_bits)
    elif state['active'] and state['mode'] in ('quantization',):
        # Uniform quantization — use the standard path
        layer_idx = state['layer_counter']
        from combined_compression import _quantize_kv_layer
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

    if state['active']:
        state['layer_counter'] += 1

    attn_output = torch.matmul(attn_weights, value)
    attn_output = attn_output.transpose(1, 2)

    return attn_output, attn_weights


def install_adaptive_patch(model):
    """Install the adaptive attention patch."""
    import transformers.models.gpt2.modeling_gpt2 as gpt2_module
    gpt2_module.ALL_ATTENTION_FUNCTIONS["eager"] = patched_eager_attention_forward_adaptive
    print("  Adaptive attention patch installed")


###############################################################################
# GENERATION / PERPLEXITY WITH ADAPTIVE QUANT
###############################################################################

def generate_adaptive(model, input_ids: torch.Tensor, max_new_tokens: int = 20,
                      mode: str = None, n_bits: int = 4,
                      per_head_bits: Dict = None) -> torch.Tensor:
    """
    Autoregressive generation with adaptive per-head quantization.
    mode: None (baseline), 'quantization' (uniform), 'adaptive_quant' (per-head)
    """
    state = _compression_state

    generated = input_ids.clone()

    for step in range(max_new_tokens):
        if mode is not None:
            state['active'] = True
            state['mode'] = mode
            state['n_bits'] = n_bits
            state['layer_counter'] = 0
            state['use_qjl'] = True
            if per_head_bits is not None:
                state['per_head_bits'] = per_head_bits
        else:
            state['active'] = False

        with torch.no_grad():
            outputs = model(generated)

        state['active'] = False

        next_token_logits = outputs.logits[0, -1, :]
        next_token = next_token_logits.argmax(dim=-1, keepdim=True)
        generated = torch.cat([generated, next_token.unsqueeze(0)], dim=-1)

    return generated


def compute_perplexity_adaptive(model, input_ids: torch.Tensor,
                                mode: str = None, n_bits: int = 4,
                                per_head_bits: Dict = None) -> float:
    """Compute perplexity with adaptive quantization."""
    state = _compression_state

    if mode is not None:
        state['active'] = True
        state['mode'] = mode
        state['n_bits'] = n_bits
        state['layer_counter'] = 0
        state['use_qjl'] = True
        if per_head_bits is not None:
            state['per_head_bits'] = per_head_bits
    else:
        state['active'] = False

    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)

    state['active'] = False
    loss = outputs.loss.item()
    return math.exp(loss)


###############################################################################
# EXPERIMENT CONFIGS
###############################################################################

def get_adaptive_configs(head_entropies, n_layers=12, n_heads=12):
    """Define all experiment configurations for entropy-adaptive TurboQuant."""

    # Identify skip candidates (top 3 lowest entropy)
    skip_heads = identify_skip_heads(head_entropies, max_skip_count=3)
    print(f"\n  Skip heads ({len(skip_heads)}):")
    for (l, h) in sorted(skip_heads):
        print(f"    L{l}_H{h}: H2={head_entropies[(l, h)]:.4f}")

    configs = []

    # 1. Uniform 3-bit baseline
    configs.append({
        'name': 'uniform_3bit',
        'mode': 'quantization',
        'n_bits': 3,
        'per_head_bits': None,  # uniform
        'description': 'Uniform 3-bit (baseline)',
        'effective_avg_bits': 3.0,
    })

    # 2. Uniform 4-bit baseline
    configs.append({
        'name': 'uniform_4bit',
        'mode': 'quantization',
        'n_bits': 4,
        'per_head_bits': None,
        'description': 'Uniform 4-bit (baseline)',
        'effective_avg_bits': 4.0,
    })

    # 3. Adaptive 3-bit conservative (alpha=0.25)
    bits_3c = compute_optimal_bits(head_entropies, avg_bits=3.0, alpha=0.25,
                                    n_layers=n_layers, n_heads=n_heads)
    configs.append({
        'name': 'adaptive_3bit_conservative',
        'mode': 'adaptive_quant',
        'n_bits': 3,
        'per_head_bits': bits_3c,
        'description': 'Adaptive 3-bit (alpha=0.25)',
        'effective_avg_bits': np.mean(list(bits_3c.values())),
    })

    # 4. Adaptive 3-bit aggressive (alpha=0.50)
    bits_3a = compute_optimal_bits(head_entropies, avg_bits=3.0, alpha=0.50,
                                    n_layers=n_layers, n_heads=n_heads)
    configs.append({
        'name': 'adaptive_3bit_aggressive',
        'mode': 'adaptive_quant',
        'n_bits': 3,
        'per_head_bits': bits_3a,
        'description': 'Adaptive 3-bit (alpha=0.50)',
        'effective_avg_bits': np.mean(list(bits_3a.values())),
    })

    # 5. Adaptive 4-bit conservative (alpha=0.25)
    bits_4c = compute_optimal_bits(head_entropies, avg_bits=4.0, alpha=0.25,
                                    n_layers=n_layers, n_heads=n_heads)
    configs.append({
        'name': 'adaptive_4bit_conservative',
        'mode': 'adaptive_quant',
        'n_bits': 4,
        'per_head_bits': bits_4c,
        'description': 'Adaptive 4-bit (alpha=0.25)',
        'effective_avg_bits': np.mean(list(bits_4c.values())),
    })

    # 6. Skip top 3 + uniform 3-bit
    skip_uniform_bits = {}
    for k in head_entropies:
        if k in skip_heads:
            skip_uniform_bits[k] = 16
        else:
            skip_uniform_bits[k] = 3
    total_heads = len(head_entropies)
    eff_avg_6 = (len(skip_heads) * 16 + (total_heads - len(skip_heads)) * 3) / total_heads
    configs.append({
        'name': 'skip_top3_uniform_3bit',
        'mode': 'adaptive_quant',
        'n_bits': 3,
        'per_head_bits': skip_uniform_bits,
        'description': 'Skip 3 lowest-H2 heads + uniform 3-bit',
        'effective_avg_bits': eff_avg_6,
    })

    # 7. Skip top 3 + adaptive 3-bit
    bits_skip_adaptive = compute_adaptive_bits_with_skip(
        head_entropies, skip_heads, target_avg_bits=3.0, alpha=0.25
    )
    configs.append({
        'name': 'skip_top3_adaptive_3bit',
        'mode': 'adaptive_quant',
        'n_bits': 3,
        'per_head_bits': bits_skip_adaptive,
        'description': 'Skip 3 + adaptive 3-bit (alpha=0.25)',
        'effective_avg_bits': np.mean(list(bits_skip_adaptive.values())),
    })

    # 8. Combined best: skip 3 + adaptive 4-bit conservative
    bits_combined = compute_adaptive_bits_with_skip(
        head_entropies, skip_heads, target_avg_bits=4.0, alpha=0.25
    )
    configs.append({
        'name': 'combined_best',
        'mode': 'adaptive_quant',
        'n_bits': 4,
        'per_head_bits': bits_combined,
        'description': 'Skip 3 + adaptive 4-bit (alpha=0.25)',
        'effective_avg_bits': np.mean(list(bits_combined.values())),
    })

    # Print allocation summaries
    print("\n  Bit allocation summaries:")
    for cfg in configs:
        name = cfg['name']
        eff = cfg['effective_avg_bits']
        cr = 16.0 / eff
        if cfg['per_head_bits'] is not None:
            bits_vals = list(cfg['per_head_bits'].values())
            dist = {b: bits_vals.count(b) for b in sorted(set(bits_vals))}
            print(f"    {name}: avg={eff:.2f} bits, {cr:.2f}x compression, dist={dist}")
        else:
            print(f"    {name}: avg={eff:.2f} bits, {cr:.2f}x compression (uniform)")

    return configs


###############################################################################
# EXPERIMENT RUNNER
###############################################################################

def run_adaptive_experiment(model, tokenizer, sequences, head_entropies, configs,
                            num_seqs=8, gen_tokens=20):
    """Run all adaptive experiment configurations."""
    print(f"\n{'=' * 70}")
    print(f"[{timestamp()}] RUNNING ENTROPY-ADAPTIVE TURBOQUANT EXPERIMENT")
    print(f"{'=' * 70}")
    print(f"  {len(configs)} configs, {num_seqs} sequences, {gen_tokens} gen tokens")

    seq_len = len(sequences[0])
    results = {}

    # Generate baseline references
    print(f"\n[{timestamp()}] Generating baseline references...")
    baseline_generations = []
    baseline_perplexities = []
    t0 = time.time()

    for seq_idx in range(num_seqs):
        if seq_idx % 2 == 0:
            print(f"  Baseline seq {seq_idx + 1}/{num_seqs} ({time.time() - t0:.0f}s)", flush=True)
        input_ids = torch.tensor([sequences[seq_idx]], device=device)

        gen = generate_adaptive(model, input_ids, max_new_tokens=gen_tokens, mode=None)
        baseline_generations.append(gen[0, seq_len:].tolist())

        ppl = compute_perplexity_adaptive(model, input_ids, mode=None)
        baseline_perplexities.append(ppl)

    baseline_ppl = float(np.mean(baseline_perplexities))
    print(f"  Baseline mean perplexity: {baseline_ppl:.2f}")

    # Store baseline
    results['baseline'] = {
        'description': 'Full KV cache (fp16 baseline)',
        'mode': 'baseline',
        'effective_avg_bits': 16.0,
        'compression_ratio': 1.0,
        'bleu': 1.0,
        'rouge_l': 1.0,
        'token_match': 1.0,
        'perplexity': baseline_ppl,
        'perplexity_ratio': 1.0,
        'wall_clock_seconds': 0.0,
    }

    # Run each configuration
    for cfg_idx, cfg in enumerate(configs):
        name = cfg['name']
        mode = cfg['mode']
        n_bits = cfg['n_bits']
        per_head_bits = cfg.get('per_head_bits')
        eff_avg_bits = cfg['effective_avg_bits']

        print(f"\n[{timestamp()}] Config {cfg_idx + 1}/{len(configs)}: {name}")
        print(f"  {cfg['description']} (effective avg: {eff_avg_bits:.2f} bits)")

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
                gen = generate_adaptive(
                    model, input_ids, max_new_tokens=gen_tokens,
                    mode=mode, n_bits=n_bits, per_head_bits=per_head_bits
                )
                hyp_tokens = gen[0, seq_len:].tolist()
                ref_tokens = baseline_generations[seq_idx]

                metrics = compute_metrics(ref_tokens, hyp_tokens)
                all_bleu.append(metrics['bleu'])
                all_rouge.append(metrics['rouge_l'])
                all_match.append(metrics['token_match'])

                ppl = compute_perplexity_adaptive(
                    model, input_ids, mode=mode, n_bits=n_bits,
                    per_head_bits=per_head_bits
                )
                all_ppl.append(ppl)

            except Exception as e:
                print(f"    ERROR on seq {seq_idx}: {e}")
                import traceback
                traceback.print_exc()
                all_bleu.append(0.0)
                all_rouge.append(0.0)
                all_match.append(0.0)
                all_ppl.append(float('inf'))

        wall_clock = time.time() - t_start
        compression_ratio = 16.0 / eff_avg_bits
        mean_ppl = float(np.mean([p for p in all_ppl if p != float('inf')]) if all_ppl else float('inf'))

        results[name] = {
            'description': cfg['description'],
            'mode': mode,
            'effective_avg_bits': float(eff_avg_bits),
            'compression_ratio': float(compression_ratio),
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
              f"Compress={r['compression_ratio']:.2f}x  Time={wall_clock:.1f}s")

    return results


###############################################################################
# RESULTS TABLE
###############################################################################

def print_results_table(results: dict):
    """Print comparison table sorted by compression ratio."""
    print(f"\n{'=' * 110}")
    print(f"ENTROPY-ADAPTIVE TURBOQUANT RESULTS")
    print(f"{'=' * 110}")

    header = (f"{'Config':<35s} {'AvgBits':>7s} {'Compress':>8s} {'BLEU':>8s} "
              f"{'ROUGE-L':>8s} {'Match':>8s} {'PPL ratio':>10s} {'Time(s)':>8s}")
    print(header)
    print("-" * 110)

    sorted_names = sorted(results.keys(),
                          key=lambda k: results[k].get('compression_ratio', 1.0))

    for name in sorted_names:
        r = results[name]
        eff_bits = r.get('effective_avg_bits', 16.0)
        ppl_str = f"{r['perplexity_ratio']:.3f}" if r['perplexity_ratio'] < 100 else ">100"
        print(f"{name:<35s} {eff_bits:>6.2f}b {r['compression_ratio']:>7.2f}x "
              f"{r['bleu']:>8.4f} {r['rouge_l']:>8.4f} {r['token_match']:>8.4f} "
              f"{ppl_str:>10s} {r['wall_clock_seconds']:>8.1f}")

    print("-" * 110)

    # Compare adaptive vs uniform at same bit budget
    print("\n=== Improvement Analysis ===")

    # 3-bit comparisons
    u3 = results.get('uniform_3bit', {})
    for name in ['adaptive_3bit_conservative', 'adaptive_3bit_aggressive',
                 'skip_top3_uniform_3bit', 'skip_top3_adaptive_3bit']:
        r = results.get(name, {})
        if u3 and r:
            bleu_delta = r.get('bleu', 0) - u3.get('bleu', 0)
            ppl_delta = r.get('perplexity_ratio', 1) - u3.get('perplexity_ratio', 1)
            print(f"  {name} vs uniform_3bit: BLEU {bleu_delta:+.4f}, PPL_ratio {ppl_delta:+.4f}")

    # 4-bit comparisons
    u4 = results.get('uniform_4bit', {})
    for name in ['adaptive_4bit_conservative', 'combined_best']:
        r = results.get(name, {})
        if u4 and r:
            bleu_delta = r.get('bleu', 0) - u4.get('bleu', 0)
            ppl_delta = r.get('perplexity_ratio', 1) - u4.get('perplexity_ratio', 1)
            print(f"  {name} vs uniform_4bit: BLEU {bleu_delta:+.4f}, PPL_ratio {ppl_delta:+.4f}")


###############################################################################
# MAIN
###############################################################################

def main():
    print(f"{'=' * 70}")
    print(f"ENTROPY-ADAPTIVE TURBOQUANT — PHASE 1")
    print(f"Per-Head Bit Allocation + Quantization Skipping")
    print(f"{'=' * 70}")
    print(f"Start time: {timestamp()}")
    print(f"Device: {device}")
    t_total = time.time()

    # Verify TurboQuant
    if not verify_turboquant():
        print("ABORTING: TurboQuant verification failed.")
        return None

    # Load model and data
    model, tokenizer, sequences = load_gpt2_and_data(num_seqs=10, seq_len=128)

    # Configure state
    _compression_state['head_dim'] = model.config.n_embd // model.config.n_head
    _compression_state['n_heads'] = model.config.n_head
    _compression_state['m_projections'] = 64

    # Install adaptive patch
    install_adaptive_patch(model)

    # Collect head entropies
    head_entropies = collect_head_entropies(model, sequences, num_seqs=5, seq_len=128)

    # Pre-compute TurboQuant objects
    print(f"\n[{timestamp()}] Pre-computing TurboQuant objects...")
    t_precompute = time.time()
    head_dim = _compression_state['head_dim']
    n_heads = _compression_state['n_heads']
    n_layers = model.config.n_layer

    all_bits = {2, 3, 4, 5}  # Include 5-bit for adaptive configs
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
                tq_obj.lloyd = lloyd_shared
                tq_cache[cache_key] = tq_obj
    _compression_state['tq_cache'] = tq_cache
    print(f"  Pre-computed {len(tq_cache)} TurboQuant objects in {time.time() - t_precompute:.1f}s")

    # Get experiment configs
    configs = get_adaptive_configs(head_entropies, n_layers=n_layers, n_heads=n_heads)

    # Run experiments
    num_seqs = min(8, len(sequences))
    gen_tokens = 20
    results = run_adaptive_experiment(
        model, tokenizer, sequences, head_entropies,
        configs, num_seqs=num_seqs, gen_tokens=gen_tokens
    )

    # Print results
    print_results_table(results)

    # Save results
    results_path = PLOT_DIR / 'entropy_adaptive_turboquant_results.json'
    serializable = {}
    for k, v in results.items():
        serializable[k] = {sk: (float(sv) if isinstance(sv, (np.floating, float)) else sv)
                           for sk, sv in v.items()}

    output = {
        'experiment': 'entropy_adaptive_turboquant_phase1',
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
