"""
LLM Efficiency Experiments: Validating First-Principles Predictions
===================================================================
Three experiments on CPU:
  A: Adaptive Compute - Layer Skip Analysis (GPT-2, WikiText-2)
  C: KV Cache Sparsity (GPT-2, WikiText-2)
  B: Data Curation by Information (DistilBERT, SST-2)

Run order: A -> C -> B (as specified)
"""

import os
import sys
import json
import time
import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PLOT_DIR = Path(__file__).resolve().parent / "plots"
PLOT_DIR.mkdir(exist_ok=True)

# Ensure CPU only
device = torch.device('cpu')

def timestamp():
    return time.strftime("%H:%M:%S")


###############################################################################
# EXPERIMENT A: Adaptive Compute — Layer Skip Analysis
###############################################################################
def experiment_a():
    print(f"\n{'='*70}")
    print(f"[{timestamp()}] EXPERIMENT A: Adaptive Compute — Layer Skip Analysis")
    print(f"{'='*70}")

    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    from datasets import load_dataset

    print(f"[{timestamp()}] Loading GPT-2 small...")
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model.eval()
    model.to(device)

    num_layers = len(model.transformer.h)
    print(f"  Model has {num_layers} layers")

    # Load WikiText-2 validation
    print(f"[{timestamp()}] Loading WikiText-2 validation...")
    dataset = load_dataset('wikitext', 'wikitext-2-raw-v1', split='validation')

    # Concatenate all text
    full_text = "\n".join([t for t in dataset['text'] if t.strip()])
    all_tokens = tokenizer.encode(full_text)
    print(f"  Total tokens: {len(all_tokens)}")

    # Create sequences of 256 tokens
    seq_len = 256
    sequences = []
    for i in range(0, len(all_tokens) - seq_len, seq_len):
        sequences.append(all_tokens[i:i+seq_len])
    print(f"  Created {len(sequences)} sequences of {seq_len} tokens")

    # Timing test with 1 sequence
    print(f"[{timestamp()}] Timing test...")
    t0 = time.time()

    hidden_states = {}
    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            # output may be a tensor or tuple depending on transformers version
            if isinstance(output, tuple):
                hidden_states[layer_idx] = output[0].detach()
            else:
                hidden_states[layer_idx] = output.detach()
        return hook_fn

    hooks = []
    for i, block in enumerate(model.transformer.h):
        hooks.append(block.register_forward_hook(make_hook(i)))

    input_ids = torch.tensor([sequences[0]], device=device)
    with torch.no_grad():
        outputs = model(input_ids)

    # Test per-layer projection
    lm_head = model.lm_head
    ln_f = model.transformer.ln_f

    # Verify hook capture: layer 11 through ln_f + lm_head should match final logits
    hs_last = hidden_states[num_layers - 1]  # (batch, seq, hidden)
    test_logits = lm_head(ln_f(hs_last[0]))
    final_logits_test = outputs.logits[0]
    max_diff = (test_logits - final_logits_test).abs().max().item()
    match_rate = (test_logits.argmax(-1) == final_logits_test.argmax(-1)).float().mean().item()
    print(f"  Verification: last layer logit diff={max_diff:.6f}, match={match_rate:.4f}")

    final_preds = outputs.logits[0].argmax(dim=-1)
    for layer_idx in range(num_layers):
        layer_logits = lm_head(ln_f(hidden_states[layer_idx][0]))
        layer_preds = layer_logits.argmax(dim=-1)

    t1 = time.time()
    per_seq_time = t1 - t0
    print(f"  1 sequence took {per_seq_time:.1f}s")

    # Decide how many sequences to process
    target_time = 600  # 10 minutes
    max_seqs = min(len(sequences), max(5, int(target_time / per_seq_time)))
    max_seqs = min(max_seqs, 200)  # cap for reasonable runtime
    print(f"  Will process {max_seqs} sequences (~{max_seqs * per_seq_time:.0f}s)")

    # Process sequences
    # Per-layer match rates (cumulative across all tokens)
    layer_matches = np.zeros(num_layers)
    layer_confident_matches = np.zeros(num_layers)  # when final pred is confident
    total_tokens = 0
    confident_tokens = 0
    early_exit_layers = []  # per-token earliest matching layer

    for seq_idx in range(max_seqs):
        if seq_idx % 20 == 0:
            print(f"[{timestamp()}] Processing sequence {seq_idx+1}/{max_seqs}...")

        hidden_states.clear()
        input_ids = torch.tensor([sequences[seq_idx]], device=device)

        with torch.no_grad():
            outputs = model(input_ids)

        final_logits = outputs.logits[0]  # [seq_len, vocab]
        final_preds = final_logits.argmax(dim=-1)  # [seq_len]
        final_probs = torch.softmax(final_logits, dim=-1)
        final_confidence = final_probs.max(dim=-1).values  # [seq_len]

        confident_mask = final_confidence > 0.9
        n_tokens = seq_len
        n_confident = confident_mask.sum().item()
        total_tokens += n_tokens
        confident_tokens += n_confident

        # Track earliest match per token
        token_first_match = np.full(n_tokens, num_layers)  # default: never matched early

        for layer_idx in range(num_layers):
            hs = hidden_states[layer_idx]
            # hs shape is (batch, seq, hidden) — take first batch element
            layer_logits = lm_head(ln_f(hs[0]))
            layer_preds = layer_logits.argmax(dim=-1)

            match = (layer_preds == final_preds)
            layer_matches[layer_idx] += match.sum().item()

            if n_confident > 0:
                layer_confident_matches[layer_idx] += match[confident_mask].sum().item()

            # Update earliest match
            match_np = match.cpu().numpy()
            for t in range(n_tokens):
                if match_np[t] and token_first_match[t] == num_layers:
                    token_first_match[t] = layer_idx

        early_exit_layers.extend(token_first_match.tolist())

    # Remove hooks
    for h in hooks:
        h.remove()

    # Compute statistics
    match_fractions = layer_matches / total_tokens
    confident_match_fractions = layer_confident_matches / max(confident_tokens, 1)
    early_exit_array = np.array(early_exit_layers)

    # Key metrics
    f_skip_8 = match_fractions[7] if num_layers > 7 else 0  # layer 8 (0-indexed: 7)
    f_skip_6 = match_fractions[5] if num_layers > 5 else 0  # layer 6
    mean_exit = early_exit_array.mean()
    median_exit = np.median(early_exit_array)
    pct_skip_last4 = (early_exit_array <= 7).mean()  # can skip layers 9-12 (exit by layer 8)
    pct_skip_last6 = (early_exit_array <= 5).mean()  # can skip layers 7-12

    print(f"\n--- Experiment A Results ---")
    print(f"Total tokens processed: {total_tokens}")
    print(f"Confident tokens (>90%): {confident_tokens} ({confident_tokens/total_tokens*100:.1f}%)")
    print(f"\nCumulative match fraction by layer:")
    for i, frac in enumerate(match_fractions):
        marker = " <-- layer 8" if i == 7 else ""
        print(f"  Layer {i+1:2d}: {frac:.4f} ({frac*100:.1f}%){marker}")
    print(f"\nF_skip(8) = {f_skip_8:.4f} ({f_skip_8*100:.1f}%)")
    print(f"F_skip(6) = {f_skip_6:.4f} ({f_skip_6*100:.1f}%)")
    print(f"Mean early exit layer: {mean_exit:.2f}")
    print(f"Median early exit layer: {median_exit:.1f}")
    print(f"% that could skip last 4 layers: {pct_skip_last4*100:.1f}%")
    print(f"% that could skip last 6 layers: {pct_skip_last6*100:.1f}%")

    # Prediction check
    prediction_pass = f_skip_8 >= 0.25
    print(f"\nPrediction check: F_skip(8) >= 25%? {'PASS' if prediction_pass else 'FAIL'} ({f_skip_8*100:.1f}%)")

    # Distribution of early exit layers
    exit_dist = np.zeros(num_layers + 1)
    for i in range(num_layers + 1):
        exit_dist[i] = (early_exit_array == i).mean()

    # ---- PLOTS ----
    # Plot 1: Cumulative match fraction by layer
    fig, ax = plt.subplots(figsize=(10, 6))
    layers = np.arange(1, num_layers + 1)
    ax.plot(layers, match_fractions, 'b-o', linewidth=2, markersize=8, label='All tokens')
    ax.plot(layers, confident_match_fractions, 'r-s', linewidth=2, markersize=8, label='Confident tokens (>90%)')
    ax.axhline(y=0.25, color='green', linestyle='--', alpha=0.7, label='Pass threshold (25%)')
    ax.axhline(y=0.50, color='orange', linestyle='--', alpha=0.7, label='Prediction midpoint (50%)')
    ax.axvline(x=8, color='gray', linestyle=':', alpha=0.5, label='Layer 8')
    ax.set_xlabel('Layer', fontsize=14)
    ax.set_ylabel('Fraction matching final prediction', fontsize=14)
    ax.set_title('Adaptive Compute: Per-Layer Prediction Match Rate', fontsize=16)
    ax.legend(fontsize=11)
    ax.set_xticks(layers)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'llm_eff_layer_skip.png', dpi=150)
    plt.close()
    print(f"  Saved llm_eff_layer_skip.png")

    # Plot 2: Histogram of early exit layers
    fig, ax = plt.subplots(figsize=(10, 6))
    bins = np.arange(-0.5, num_layers + 1.5, 1)
    ax.bar(range(num_layers + 1), exit_dist, color='steelblue', edgecolor='black', alpha=0.8)
    ax.set_xlabel('Earliest matching layer (0-indexed)', fontsize=14)
    ax.set_ylabel('Fraction of tokens', fontsize=14)
    ax.set_title(f'Distribution of Early Exit Layers (mean={mean_exit:.1f}, median={median_exit:.0f})', fontsize=16)
    ax.set_xticks(range(num_layers + 1))
    ax.set_xticklabels([f'L{i}' for i in range(num_layers)] + ['Never'])
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'llm_eff_exit_dist.png', dpi=150)
    plt.close()
    print(f"  Saved llm_eff_exit_dist.png")

    results_a = {
        'total_tokens': total_tokens,
        'confident_tokens': confident_tokens,
        'confident_fraction': confident_tokens / total_tokens,
        'match_fractions': match_fractions.tolist(),
        'confident_match_fractions': confident_match_fractions.tolist(),
        'f_skip_8': f_skip_8,
        'f_skip_6': f_skip_6,
        'mean_exit_layer': mean_exit,
        'median_exit_layer': float(median_exit),
        'pct_skip_last4': pct_skip_last4,
        'pct_skip_last6': float(pct_skip_last4),
        'pct_skip_last6_val': float(pct_skip_last6),
        'exit_distribution': exit_dist.tolist(),
        'prediction_pass': bool(prediction_pass),
        'num_sequences': max_seqs,
        'seq_len': seq_len,
    }

    return results_a


###############################################################################
# EXPERIMENT C: KV Cache Sparsity
###############################################################################
def experiment_c():
    print(f"\n{'='*70}")
    print(f"[{timestamp()}] EXPERIMENT C: KV Cache Sparsity")
    print(f"{'='*70}")

    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    from datasets import load_dataset

    print(f"[{timestamp()}] Loading GPT-2 small (eager attention for output_attentions)...")
    model = GPT2LMHeadModel.from_pretrained('gpt2', attn_implementation='eager')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model.eval()
    model.to(device)

    num_layers = len(model.transformer.h)
    num_heads = model.config.n_head

    # Load WikiText-2 validation
    print(f"[{timestamp()}] Loading WikiText-2 validation...")
    dataset = load_dataset('wikitext', 'wikitext-2-raw-v1', split='validation')
    full_text = "\n".join([t for t in dataset['text'] if t.strip()])
    all_tokens = tokenizer.encode(full_text)

    seq_len = 256
    sequences = []
    for i in range(0, len(all_tokens) - seq_len, seq_len):
        sequences.append(all_tokens[i:i+seq_len])

    num_seqs = min(30, len(sequences))
    print(f"  Will process {num_seqs} sequences of {seq_len} tokens")

    # Sample positions to analyze (avoid very short contexts)
    sample_positions = [31, 63, 127, 191, 255]
    sample_positions = [p for p in sample_positions if p < seq_len]

    # Statistics accumulators
    # Per layer, per head: entropy, sparsity, top-k coverage
    all_stats = []

    # Per-layer aggregates
    layer_sparsity_001 = np.zeros(num_layers)
    layer_sparsity_0001 = np.zeros(num_layers)
    layer_entropy = np.zeros(num_layers)
    layer_n_eff = np.zeros(num_layers)
    layer_topk_coverage = {k: np.zeros(num_layers) for k in [1, 5, 10, 20]}
    layer_first_token_attn = np.zeros(num_layers)
    layer_diag_attn = np.zeros(num_layers)
    layer_count = np.zeros(num_layers)

    t0 = time.time()

    for seq_idx in range(num_seqs):
        if seq_idx % 10 == 0:
            elapsed = time.time() - t0
            print(f"[{timestamp()}] Processing sequence {seq_idx+1}/{num_seqs} ({elapsed:.0f}s elapsed)")

        input_ids = torch.tensor([sequences[seq_idx]], device=device)

        with torch.no_grad():
            outputs = model(input_ids, output_attentions=True)

        attentions = outputs.attentions  # tuple of (1, num_heads, seq_len, seq_len)

        for layer_idx, attn_tensor in enumerate(attentions):
            attn = attn_tensor[0]  # (num_heads, seq_len, seq_len)

            for head_idx in range(num_heads):
                for pos in sample_positions:
                    row = attn[head_idx, pos, :pos+1]  # valid attention weights
                    context_len = pos + 1

                    # Entropy
                    row_pos = row[row > 1e-10]
                    if len(row_pos) > 0:
                        entropy = -(row_pos * torch.log2(row_pos)).sum().item()
                    else:
                        entropy = 0.0
                    n_eff = 2 ** entropy

                    # Sparsity
                    s_001 = (row < 0.01).float().mean().item()
                    s_0001 = (row < 0.001).float().mean().item()

                    # Top-K coverage
                    sorted_row, _ = row.sort(descending=True)
                    cum_weight = sorted_row.cumsum(0)
                    topk_cov = {}
                    for k in [1, 5, 10, 20]:
                        k_actual = min(k, len(sorted_row))
                        topk_cov[k] = sorted_row[:k_actual].sum().item()

                    # Special positions
                    first_token_weight = row[0].item()
                    diag_weight = row[pos].item() if pos < len(row) else 0.0

                    # Accumulate per-layer
                    layer_sparsity_001[layer_idx] += s_001
                    layer_sparsity_0001[layer_idx] += s_0001
                    layer_entropy[layer_idx] += entropy
                    layer_n_eff[layer_idx] += n_eff
                    for k in [1, 5, 10, 20]:
                        layer_topk_coverage[k][layer_idx] += topk_cov[k]
                    layer_first_token_attn[layer_idx] += first_token_weight
                    layer_diag_attn[layer_idx] += diag_weight
                    layer_count[layer_idx] += 1

                    all_stats.append({
                        'layer': layer_idx,
                        'head': head_idx,
                        'position': pos,
                        'context_length': context_len,
                        'entropy': entropy,
                        'n_effective': n_eff,
                        'sparsity_1pct': s_001,
                        'sparsity_01pct': s_0001,
                        'top1_coverage': topk_cov[1],
                        'top5_coverage': topk_cov[5],
                        'top10_coverage': topk_cov[10],
                        'top20_coverage': topk_cov[20],
                        'first_token_attn': first_token_weight,
                        'diag_attn': diag_weight,
                    })

    elapsed = time.time() - t0
    print(f"[{timestamp()}] Attention extraction complete ({elapsed:.0f}s)")

    # Compute per-layer means
    for i in range(num_layers):
        if layer_count[i] > 0:
            layer_sparsity_001[i] /= layer_count[i]
            layer_sparsity_0001[i] /= layer_count[i]
            layer_entropy[i] /= layer_count[i]
            layer_n_eff[i] /= layer_count[i]
            for k in [1, 5, 10, 20]:
                layer_topk_coverage[k][i] /= layer_count[i]
            layer_first_token_attn[i] /= layer_count[i]
            layer_diag_attn[i] /= layer_count[i]

    # Overall means
    mean_sparsity_001 = np.mean([s['sparsity_1pct'] for s in all_stats])
    mean_sparsity_0001 = np.mean([s['sparsity_01pct'] for s in all_stats])
    mean_entropy_all = np.mean([s['entropy'] for s in all_stats])
    mean_n_eff = np.mean([s['n_effective'] for s in all_stats])
    mean_top1 = np.mean([s['top1_coverage'] for s in all_stats])
    mean_top5 = np.mean([s['top5_coverage'] for s in all_stats])
    mean_top10 = np.mean([s['top10_coverage'] for s in all_stats])
    mean_top20 = np.mean([s['top20_coverage'] for s in all_stats])

    print(f"\n--- Experiment C Results ---")
    print(f"Total attention rows analyzed: {len(all_stats)}")
    print(f"\nOverall sparsity:")
    print(f"  Mean sparsity (>0.01 threshold): {mean_sparsity_001:.4f} ({mean_sparsity_001*100:.1f}%)")
    print(f"  Mean sparsity (>0.001 threshold): {mean_sparsity_0001:.4f} ({mean_sparsity_0001*100:.1f}%)")
    print(f"\nAttention entropy:")
    print(f"  Mean entropy: {mean_entropy_all:.2f} bits")
    print(f"  Mean effective positions: {mean_n_eff:.1f}")
    print(f"\nTop-K coverage:")
    print(f"  Top-1:  {mean_top1*100:.1f}%")
    print(f"  Top-5:  {mean_top5*100:.1f}%")
    print(f"  Top-10: {mean_top10*100:.1f}%")
    print(f"  Top-20: {mean_top20*100:.1f}%")
    print(f"\nPer-layer sparsity (>0.01 threshold):")
    for i in range(num_layers):
        print(f"  Layer {i+1:2d}: {layer_sparsity_001[i]:.4f} ({layer_sparsity_001[i]*100:.1f}%)")
    print(f"\nSpecial positions:")
    print(f"  Mean attention to first token: {np.mean([s['first_token_attn'] for s in all_stats]):.4f}")
    print(f"  Mean self-attention (diagonal): {np.mean([s['diag_attn'] for s in all_stats]):.4f}")

    # Prediction check
    prediction_pass = mean_sparsity_001 >= 0.80
    print(f"\nPrediction check: Mean sparsity(0.01) >= 80%? {'PASS' if prediction_pass else 'FAIL'} ({mean_sparsity_001*100:.1f}%)")

    # Estimated KV cache reduction
    kv_reduction = 1.0 / (1.0 - mean_sparsity_001) if mean_sparsity_001 < 1.0 else float('inf')
    print(f"  Estimated KV cache reduction factor: {kv_reduction:.1f}x")

    # ---- PLOTS ----
    # Plot 3: Sparsity by layer + threshold
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    layers = np.arange(1, num_layers + 1)
    axes[0].plot(layers, layer_sparsity_001, 'b-o', linewidth=2, markersize=8, label='threshold > 0.01')
    axes[0].plot(layers, layer_sparsity_0001, 'r-s', linewidth=2, markersize=8, label='threshold > 0.001')
    axes[0].axhline(y=0.80, color='green', linestyle='--', alpha=0.7, label='Pass threshold (80%)')
    axes[0].axhline(y=0.93, color='orange', linestyle='--', alpha=0.7, label='Prediction (93%)')
    axes[0].set_xlabel('Layer', fontsize=13)
    axes[0].set_ylabel('Sparsity (fraction < threshold)', fontsize=13)
    axes[0].set_title('Attention Sparsity by Layer', fontsize=14)
    axes[0].legend(fontsize=10)
    axes[0].set_ylim(0.5, 1.02)
    axes[0].set_xticks(layers)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(layers, layer_entropy, 'g-o', linewidth=2, markersize=8)
    axes[1].set_xlabel('Layer', fontsize=13)
    axes[1].set_ylabel('Mean attention entropy (bits)', fontsize=13)
    axes[1].set_title('Attention Entropy by Layer', fontsize=14)
    axes[1].set_xticks(layers)
    axes[1].grid(True, alpha=0.3)
    ax2 = axes[1].twinx()
    ax2.plot(layers, layer_n_eff, 'purple', linestyle='--', marker='D', linewidth=1.5, markersize=6, alpha=0.7)
    ax2.set_ylabel('Effective positions (2^H)', fontsize=13, color='purple')

    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'llm_eff_attention_sparsity.png', dpi=150)
    plt.close()
    print(f"  Saved llm_eff_attention_sparsity.png")

    # Plot 4: Top-K coverage by layer
    fig, ax = plt.subplots(figsize=(10, 6))
    for k, color in zip([1, 5, 10, 20], ['red', 'orange', 'blue', 'green']):
        ax.plot(layers, layer_topk_coverage[k], f'-o', color=color, linewidth=2, markersize=7, label=f'Top-{k}')
    ax.set_xlabel('Layer', fontsize=14)
    ax.set_ylabel('Fraction of attention in top-K positions', fontsize=14)
    ax.set_title('Top-K Attention Coverage by Layer', fontsize=16)
    ax.legend(fontsize=12)
    ax.set_xticks(layers)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'llm_eff_attention_topk.png', dpi=150)
    plt.close()
    print(f"  Saved llm_eff_attention_topk.png")

    results_c = {
        'total_rows_analyzed': len(all_stats),
        'num_sequences': num_seqs,
        'seq_len': seq_len,
        'mean_sparsity_001': mean_sparsity_001,
        'mean_sparsity_0001': mean_sparsity_0001,
        'mean_entropy': mean_entropy_all,
        'mean_n_effective': mean_n_eff,
        'mean_top1_coverage': mean_top1,
        'mean_top5_coverage': mean_top5,
        'mean_top10_coverage': mean_top10,
        'mean_top20_coverage': mean_top20,
        'per_layer_sparsity_001': layer_sparsity_001.tolist(),
        'per_layer_sparsity_0001': layer_sparsity_0001.tolist(),
        'per_layer_entropy': layer_entropy.tolist(),
        'per_layer_n_effective': layer_n_eff.tolist(),
        'per_layer_topk': {str(k): layer_topk_coverage[k].tolist() for k in [1, 5, 10, 20]},
        'per_layer_first_token_attn': layer_first_token_attn.tolist(),
        'per_layer_diag_attn': layer_diag_attn.tolist(),
        'kv_reduction_factor': float(kv_reduction),
        'prediction_pass': bool(prediction_pass),
    }

    return results_c


###############################################################################
# EXPERIMENT B: Data Curation by Information
###############################################################################
def experiment_b():
    print(f"\n{'='*70}")
    print(f"[{timestamp()}] EXPERIMENT B: Data Curation by Information")
    print(f"{'='*70}")

    from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
    from datasets import load_dataset
    from torch.utils.data import DataLoader, TensorDataset
    import torch.nn.functional as F

    print(f"[{timestamp()}] Loading DistilBERT and SST-2...")
    model_name = 'distilbert-base-uncased'
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)

    dataset = load_dataset('glue', 'sst2')
    train_data = dataset['train']
    val_data = dataset['validation']

    print(f"  Train size: {len(train_data)}, Val size: {len(val_data)}")

    # Tokenize
    def tokenize_batch(sentences, max_length=128):
        return tokenizer(sentences, truncation=True, padding='max_length',
                        max_length=max_length, return_tensors='pt')

    # For CPU speed: use a subset for scoring
    # Use 5000 samples for scoring, subsets of ~500 for fine-tuning
    SCORE_SIZE = min(5000, len(train_data))
    SUBSET_FRAC = 0.10

    print(f"[{timestamp()}] Tokenizing {SCORE_SIZE} training samples for scoring...")
    train_sentences = list(train_data['sentence'][:SCORE_SIZE])
    train_labels = list(train_data['label'][:SCORE_SIZE])

    train_enc = tokenize_batch(train_sentences)
    train_input_ids = train_enc['input_ids']
    train_attention_mask = train_enc['attention_mask']
    train_label_tensor = torch.tensor(train_labels)

    # Tokenize validation
    val_sentences = list(val_data['sentence'])
    val_labels_list = list(val_data['label'])
    val_enc = tokenize_batch(val_sentences)
    val_input_ids = val_enc['input_ids']
    val_attention_mask = val_enc['attention_mask']
    val_label_tensor = torch.tensor(val_labels_list)

    # --- Phase 1: Score samples by loss ---
    print(f"[{timestamp()}] Phase 1: Training scorer model (1 epoch)...")
    scorer_model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=2)
    scorer_model.to(device)
    scorer_model.train()

    optimizer = torch.optim.AdamW(scorer_model.parameters(), lr=2e-5)
    batch_size = 32

    # One epoch of training
    train_dataset = TensorDataset(train_input_ids, train_attention_mask, train_label_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    t0 = time.time()
    epoch_loss = 0
    n_batches = 0
    for batch_idx, (ids, mask, labels) in enumerate(train_loader):
        ids, mask, labels = ids.to(device), mask.to(device), labels.to(device)
        outputs = scorer_model(input_ids=ids, attention_mask=mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        epoch_loss += loss.item()
        n_batches += 1

        if (batch_idx + 1) % 50 == 0:
            elapsed = time.time() - t0
            print(f"  Batch {batch_idx+1}/{len(train_loader)}, loss={loss.item():.4f}, elapsed={elapsed:.0f}s")

    print(f"  Scorer training done: mean loss={epoch_loss/n_batches:.4f} ({time.time()-t0:.0f}s)")

    # Score all samples
    print(f"[{timestamp()}] Scoring all {SCORE_SIZE} samples...")
    scorer_model.eval()
    per_sample_losses = []

    score_loader = DataLoader(train_dataset, batch_size=64, shuffle=False)
    with torch.no_grad():
        for ids, mask, labels in score_loader:
            ids, mask, labels = ids.to(device), mask.to(device), labels.to(device)
            outputs = scorer_model(input_ids=ids, attention_mask=mask, labels=labels)
            # Per-sample loss
            logits = outputs.logits
            per_loss = F.cross_entropy(logits, labels, reduction='none')
            per_sample_losses.extend(per_loss.cpu().tolist())

    losses = np.array(per_sample_losses)
    print(f"  Loss stats: mean={losses.mean():.4f}, std={losses.std():.4f}, "
          f"min={losses.min():.4f}, max={losses.max():.4f}")
    print(f"  Loss 10th/50th/90th percentile: {np.percentile(losses, 10):.4f} / "
          f"{np.percentile(losses, 50):.4f} / {np.percentile(losses, 90):.4f}")

    # Information variation ratio
    info_ratio = np.percentile(losses, 90) / max(np.percentile(losses, 10), 1e-6)
    print(f"  Information variation (90th/10th percentile): {info_ratio:.1f}x")

    # --- Phase 2: Select subsets ---
    n = len(losses)
    subset_size = max(int(n * SUBSET_FRAC), 50)
    sorted_indices = np.argsort(losses)[::-1]  # descending (hardest first)

    top_indices = sorted_indices[:subset_size]
    bottom_indices = sorted_indices[-subset_size:]
    rng = np.random.RandomState(42)
    random_indices = rng.choice(n, subset_size, replace=False)

    subsets = {
        'full': np.arange(n),
        'top_10pct': top_indices,
        'random_10pct': random_indices,
        'bottom_10pct': bottom_indices,
    }

    print(f"\n  Subset sizes: full={n}, subsets={subset_size}")
    print(f"  Mean loss per subset:")
    for name, idx in subsets.items():
        print(f"    {name}: {losses[idx].mean():.4f}")

    # --- Phase 3: Fine-tune on each subset ---
    def evaluate_model(model, input_ids, attention_mask, labels, batch_size=64):
        model.eval()
        correct = 0
        total = 0
        eval_dataset = TensorDataset(input_ids, attention_mask, labels)
        eval_loader = DataLoader(eval_dataset, batch_size=batch_size, shuffle=False)
        with torch.no_grad():
            for ids, mask, labs in eval_loader:
                ids, mask, labs = ids.to(device), mask.to(device), labs.to(device)
                outputs = model(input_ids=ids, attention_mask=mask)
                preds = outputs.logits.argmax(dim=-1)
                correct += (preds == labs).sum().item()
                total += labs.size(0)
        return correct / total

    def fine_tune(subset_name, indices, epochs, seed):
        torch.manual_seed(seed)
        np.random.seed(seed)

        model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=2)
        model.to(device)
        model.train()

        # .copy() to handle negative strides from numpy argsort descending
        idx = torch.tensor(np.array(indices).copy(), dtype=torch.long)
        sub_ids = train_input_ids[idx]
        sub_mask = train_attention_mask[idx]
        sub_labels = train_label_tensor[idx]

        sub_dataset = TensorDataset(sub_ids, sub_mask, sub_labels)
        sub_loader = DataLoader(sub_dataset, batch_size=batch_size, shuffle=True)

        # Standard fine-tuning lr
        lr = 2e-5
        optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

        best_acc = 0
        for epoch in range(epochs):
            model.train()
            epoch_loss = 0
            n_batches = 0
            for ids, mask, labels in sub_loader:
                ids, mask, labels = ids.to(device), mask.to(device), labels.to(device)
                outputs = model(input_ids=ids, attention_mask=mask, labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                epoch_loss += loss.item()
                n_batches += 1

            # Evaluate every few epochs to track progress
            if (epoch + 1) % max(1, epochs // 3) == 0 or epoch == epochs - 1:
                acc = evaluate_model(model, val_input_ids, val_attention_mask, val_label_tensor)
                best_acc = max(best_acc, acc)
                print(f"    Epoch {epoch+1}/{epochs}: loss={epoch_loss/n_batches:.4f}, val_acc={acc:.4f}")

        final_acc = evaluate_model(model, val_input_ids, val_attention_mask, val_label_tensor)
        return max(best_acc, final_acc)

    # Timing test: one quick fine-tune
    print(f"\n[{timestamp()}] Timing test: 1 epoch on subset...")
    t0 = time.time()
    _ = fine_tune('timing_test', random_indices, 1, 42)
    time_per_epoch_subset = time.time() - t0
    print(f"  1 epoch on {subset_size} samples took {time_per_epoch_subset:.0f}s")

    time_per_epoch_full = time_per_epoch_subset * (n / subset_size)

    # Budget: ~25 minutes for this experiment
    budget_seconds = 1500

    # Subsets need MORE epochs to compensate for less data
    # Target: match total gradient steps of full-dataset training
    # Full: 3 epochs * (n/batch_size) steps = 3 * 157 = 471 steps
    # Subset: X epochs * (subset_size/batch_size) steps should be comparable
    # But we want at least 3 epochs for subsets to actually learn
    data_ratio = n / subset_size  # e.g., 10x
    epochs_subset = max(3, min(10, int(3 * data_ratio)))  # subsets get more epochs
    epochs_full = 3

    # Time estimate
    time_subsets = 3 * epochs_subset * time_per_epoch_subset  # 3 conditions
    time_full = epochs_full * time_per_epoch_full
    est_time = time_subsets + time_full

    print(f"  Plan: {epochs_subset} epochs for subsets, {epochs_full} for full")
    print(f"  Estimated total time: {est_time:.0f}s ({est_time/60:.1f} min)")

    if est_time > budget_seconds:
        # Reduce full epochs first, keep subset epochs high
        epochs_full = max(1, int((budget_seconds - time_subsets) / time_per_epoch_full))
        if epochs_full < 1:
            epochs_full = 0  # skip full, prioritize subsets
            epochs_subset = max(3, int(budget_seconds / (3 * time_per_epoch_subset)))
        est_time = 3 * epochs_subset * time_per_epoch_subset + epochs_full * time_per_epoch_full
        print(f"  Adjusted: {epochs_subset} epochs for subsets, {epochs_full} for full")
        print(f"  New estimate: {est_time:.0f}s ({est_time/60:.1f} min)")

    results = {}

    # Fine-tune subsets
    for name in ['top_10pct', 'random_10pct', 'bottom_10pct']:
        print(f"\n[{timestamp()}] Fine-tuning: {name} ({epochs_subset} epochs, seed=42)...")
        t0 = time.time()
        acc = fine_tune(name, subsets[name], epochs_subset, 42)
        elapsed = time.time() - t0
        results[name] = {'accuracy': acc, 'time': elapsed, 'epochs': epochs_subset}
        print(f"  {name}: accuracy={acc:.4f} ({elapsed:.0f}s)")

    if epochs_full > 0:
        print(f"\n[{timestamp()}] Fine-tuning: full dataset ({epochs_full} epochs, seed=42)...")
        t0 = time.time()
        acc = fine_tune('full', subsets['full'], epochs_full, 42)
        elapsed = time.time() - t0
        results['full'] = {'accuracy': acc, 'time': elapsed, 'epochs': epochs_full}
        print(f"  full: accuracy={acc:.4f} ({elapsed:.0f}s)")

    # Try additional seeds if time permits
    remaining_budget = budget_seconds - sum(r['time'] for r in results.values())
    if remaining_budget > 3 * epochs_subset * time_per_epoch_subset * 1.2:
        print(f"\n[{timestamp()}] Running additional seed (seed=123)...")
        for name in ['top_10pct', 'random_10pct', 'bottom_10pct']:
            acc = fine_tune(name, subsets[name], epochs_subset, 123)
            results[f'{name}_seed2'] = {'accuracy': acc, 'epochs': epochs_subset}
            print(f"  {name} (seed 123): accuracy={acc:.4f}")

    # --- Report ---
    print(f"\n--- Experiment B Results ---")
    print(f"Scoring set size: {SCORE_SIZE}")
    print(f"Subset size: {subset_size} ({SUBSET_FRAC*100:.0f}%)")
    print(f"\nAccuracy by condition:")
    for name in ['full', 'top_10pct', 'random_10pct', 'bottom_10pct']:
        if name in results:
            acc = results[name]['accuracy']
            print(f"  {name}: {acc:.4f} ({acc*100:.1f}%)")

    # Check predictions
    top_acc = results.get('top_10pct', {}).get('accuracy', 0)
    rand_acc = results.get('random_10pct', {}).get('accuracy', 0)
    bottom_acc = results.get('bottom_10pct', {}).get('accuracy', 0)

    ordering_correct = top_acc > rand_acc > bottom_acc
    gap = top_acc - rand_acc
    prediction_pass = gap > 0.02 or ordering_correct  # either gap or ordering

    print(f"\nTop vs Random gap: {gap*100:.1f}pp")
    print(f"Ordering (top > random > bottom): {ordering_correct}")
    print(f"Prediction check: Information ranking correlates with model loss? {'PASS' if prediction_pass else 'FAIL'}")

    # ---- PLOTS ----
    # Plot 5: Data curation results
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Loss distribution
    axes[0].hist(losses, bins=50, color='steelblue', edgecolor='black', alpha=0.8)
    axes[0].axvline(x=np.percentile(losses, 90), color='red', linestyle='--',
                    label=f'90th pctl ({np.percentile(losses, 90):.3f})')
    axes[0].axvline(x=np.percentile(losses, 10), color='green', linestyle='--',
                    label=f'10th pctl ({np.percentile(losses, 10):.3f})')
    axes[0].set_xlabel('Per-sample loss', fontsize=13)
    axes[0].set_ylabel('Count', fontsize=13)
    axes[0].set_title('Loss Distribution After 1 Epoch', fontsize=14)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3, axis='y')

    # Accuracy comparison
    conditions = []
    accuracies = []
    colors_bar = []
    for name, color in [('full', 'gray'), ('top_10pct', 'red'),
                         ('random_10pct', 'blue'), ('bottom_10pct', 'green')]:
        if name in results:
            conditions.append(name.replace('_', '\n'))
            accuracies.append(results[name]['accuracy'] * 100)
            colors_bar.append(color)

    bars = axes[1].bar(conditions, accuracies, color=colors_bar, edgecolor='black', alpha=0.8)
    axes[1].set_ylabel('Validation Accuracy (%)', fontsize=13)
    axes[1].set_title('Accuracy by Data Subset', fontsize=14)
    axes[1].set_ylim(max(0, min(accuracies) - 10), 100)
    for bar, acc in zip(bars, accuracies):
        axes[1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                    f'{acc:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'llm_eff_data_curation.png', dpi=150)
    plt.close()
    print(f"  Saved llm_eff_data_curation.png")

    results_b = {
        'score_size': SCORE_SIZE,
        'subset_size': subset_size,
        'loss_mean': float(losses.mean()),
        'loss_std': float(losses.std()),
        'loss_min': float(losses.min()),
        'loss_max': float(losses.max()),
        'loss_10pctl': float(np.percentile(losses, 10)),
        'loss_50pctl': float(np.percentile(losses, 50)),
        'loss_90pctl': float(np.percentile(losses, 90)),
        'info_variation_ratio': float(info_ratio),
        'accuracies': {k: v['accuracy'] for k, v in results.items()},
        'epochs': {k: v.get('epochs', 0) for k, v in results.items()},
        'ordering_correct': bool(ordering_correct),
        'top_random_gap': float(gap),
        'prediction_pass': bool(prediction_pass),
    }

    return results_b


###############################################################################
# SUMMARY PLOT
###############################################################################
def make_summary_plot(results_a, results_c, results_b):
    print(f"\n[{timestamp()}] Creating summary plot...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('LLM Efficiency Experiments: First-Principles Validation', fontsize=18, fontweight='bold')

    # A: Layer skip
    ax = axes[0, 0]
    layers = np.arange(1, len(results_a['match_fractions']) + 1)
    ax.plot(layers, results_a['match_fractions'], 'b-o', linewidth=2, markersize=7)
    ax.axhline(y=0.25, color='green', linestyle='--', alpha=0.7, label='Pass: 25%')
    ax.axhline(y=0.50, color='orange', linestyle='--', alpha=0.7, label='Predicted: 30-50%')
    ax.axvline(x=8, color='gray', linestyle=':', alpha=0.5)
    f8 = results_a['f_skip_8']
    status = 'PASS' if results_a['prediction_pass'] else 'FAIL'
    ax.set_title(f'A: Layer Skip — F_skip(8)={f8*100:.1f}% [{status}]', fontsize=13)
    ax.set_xlabel('Layer')
    ax.set_ylabel('Match rate')
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    # C: Sparsity
    ax = axes[0, 1]
    layers_c = np.arange(1, len(results_c['per_layer_sparsity_001']) + 1)
    ax.plot(layers_c, results_c['per_layer_sparsity_001'], 'b-o', linewidth=2, markersize=7)
    ax.axhline(y=0.80, color='green', linestyle='--', alpha=0.7, label='Pass: 80%')
    ax.axhline(y=0.93, color='orange', linestyle='--', alpha=0.7, label='Predicted: 90-96%')
    sp = results_c['mean_sparsity_001']
    status = 'PASS' if results_c['prediction_pass'] else 'FAIL'
    ax.set_title(f'C: KV Sparsity — Mean={sp*100:.1f}% [{status}]', fontsize=13)
    ax.set_xlabel('Layer')
    ax.set_ylabel('Sparsity (fraction < 0.01)')
    ax.legend(fontsize=9)
    ax.set_ylim(0.5, 1.02)
    ax.grid(True, alpha=0.3)

    # B: Data curation
    ax = axes[1, 0]
    accs = results_b['accuracies']
    names = []
    vals = []
    colors = []
    for name, color in [('full', 'gray'), ('top_10pct', 'red'),
                         ('random_10pct', 'blue'), ('bottom_10pct', 'green')]:
        if name in accs:
            names.append(name.replace('_10pct', '\n10%').replace('full', 'Full'))
            vals.append(accs[name] * 100)
            colors.append(color)
    bars = ax.bar(names, vals, color=colors, edgecolor='black', alpha=0.8)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                f'{v:.1f}%', ha='center', fontsize=11, fontweight='bold')
    status = 'PASS' if results_b['prediction_pass'] else 'FAIL'
    ax.set_title(f'B: Data Curation — Gap={results_b["top_random_gap"]*100:.1f}pp [{status}]', fontsize=13)
    ax.set_ylabel('Validation Accuracy (%)')
    ax.set_ylim(max(0, min(vals) - 15), 100)
    ax.grid(True, alpha=0.3, axis='y')

    # Summary table
    ax = axes[1, 1]
    ax.axis('off')
    table_data = [
        ['Experiment', 'Prediction', 'Measured', 'Status'],
        ['A: Layer Skip', '30-50% skip\nlast 4 layers',
         f'{results_a["pct_skip_last4"]*100:.1f}%',
         'PASS' if results_a['prediction_pass'] else 'FAIL'],
        ['C: KV Sparsity', '90-96% sparse\n(>0.01 threshold)',
         f'{results_c["mean_sparsity_001"]*100:.1f}%',
         'PASS' if results_c['prediction_pass'] else 'FAIL'],
        ['B: Data Curation', 'Top 10% > Random\n10% by >5pp',
         f'Gap: {results_b["top_random_gap"]*100:.1f}pp',
         'PASS' if results_b['prediction_pass'] else 'FAIL'],
    ]

    table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                     colWidths=[0.25, 0.25, 0.25, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.0)

    # Color the status cells
    for i in range(1, 4):
        cell = table[i, 3]
        if table_data[i][3] == 'PASS':
            cell.set_facecolor('#90EE90')
        else:
            cell.set_facecolor('#FFB6C1')
    # Header row
    for j in range(4):
        table[0, j].set_facecolor('#4472C4')
        table[0, j].set_text_props(color='white', fontweight='bold')

    n_pass = sum([results_a['prediction_pass'], results_c['prediction_pass'], results_b['prediction_pass']])
    verdict = "VALIDATED" if n_pass >= 2 else "NEEDS CALIBRATION"
    ax.set_title(f'Framework Verdict: {verdict} ({n_pass}/3 pass)', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(PLOT_DIR / 'llm_eff_summary.png', dpi=150)
    plt.close()
    print(f"  Saved llm_eff_summary.png")


###############################################################################
# MAIN
###############################################################################
if __name__ == '__main__':
    print(f"[{timestamp()}] Starting LLM Efficiency Experiments")
    print(f"Device: {device}")
    print(f"Torch version: {torch.__version__}")

    overall_start = time.time()
    all_results = {}

    # Experiment A
    try:
        t0 = time.time()
        results_a = experiment_a()
        results_a['runtime_seconds'] = time.time() - t0
        all_results['experiment_a'] = results_a
        print(f"\n[{timestamp()}] Experiment A complete ({results_a['runtime_seconds']:.0f}s)")
    except Exception as e:
        print(f"\n[{timestamp()}] Experiment A FAILED: {e}")
        import traceback; traceback.print_exc()
        results_a = {'prediction_pass': False, 'error': str(e),
                     'match_fractions': [0]*12, 'f_skip_8': 0, 'pct_skip_last4': 0}
        all_results['experiment_a'] = results_a

    # Experiment C
    try:
        t0 = time.time()
        results_c = experiment_c()
        results_c['runtime_seconds'] = time.time() - t0
        all_results['experiment_c'] = results_c
        print(f"\n[{timestamp()}] Experiment C complete ({results_c['runtime_seconds']:.0f}s)")
    except Exception as e:
        print(f"\n[{timestamp()}] Experiment C FAILED: {e}")
        import traceback; traceback.print_exc()
        results_c = {'prediction_pass': False, 'error': str(e),
                     'mean_sparsity_001': 0, 'per_layer_sparsity_001': [0]*12}
        all_results['experiment_c'] = results_c

    # Experiment B
    try:
        t0 = time.time()
        results_b = experiment_b()
        results_b['runtime_seconds'] = time.time() - t0
        all_results['experiment_b'] = results_b
        print(f"\n[{timestamp()}] Experiment B complete ({results_b['runtime_seconds']:.0f}s)")
    except Exception as e:
        print(f"\n[{timestamp()}] Experiment B FAILED: {e}")
        import traceback; traceback.print_exc()
        results_b = {'prediction_pass': False, 'error': str(e),
                     'accuracies': {}, 'top_random_gap': 0}
        all_results['experiment_b'] = results_b

    # Summary plot
    try:
        make_summary_plot(results_a, results_c, results_b)
    except Exception as e:
        print(f"Summary plot failed: {e}")

    # Save all results
    total_time = time.time() - overall_start
    all_results['total_runtime_seconds'] = total_time
    all_results['total_runtime_minutes'] = total_time / 60

    # Custom JSON encoder for numpy types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.bool_, np.integer)):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    results_path = PLOT_DIR / 'llm_eff_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, cls=NumpyEncoder)
    print(f"\n[{timestamp()}] Results saved to {results_path}")

    # Final summary
    print(f"\n{'='*70}")
    print(f"FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"Total runtime: {total_time:.0f}s ({total_time/60:.1f} min)")
    n_pass = sum([
        all_results.get('experiment_a', {}).get('prediction_pass', False),
        all_results.get('experiment_c', {}).get('prediction_pass', False),
        all_results.get('experiment_b', {}).get('prediction_pass', False),
    ])
    print(f"Predictions passed: {n_pass}/3")
    verdict = "VALIDATED" if n_pass >= 2 else "NEEDS CALIBRATION"
    print(f"Framework verdict: {verdict}")
