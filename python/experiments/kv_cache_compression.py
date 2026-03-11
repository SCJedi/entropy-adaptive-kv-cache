"""
KV Cache Compression Experiments
=================================
Building on measured 85.3% attention sparsity (Experiment C), test actual
compression strategies and measure impact on generation quality.

Three experiments:
  1. KV Eviction Strategies Comparison (5 strategies x multiple compression levels)
  2. Per-Head Sparsity Analysis (head type clustering)
  3. Quality vs Compression Pareto Frontier

Hardware: CPU only (GPT-2 small)
Expected runtime: ~30 minutes total
"""

import os
import sys
import json
import time
import numpy as np
import torch
import torch.nn as nn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PLOT_DIR = Path(__file__).resolve().parent / "plots"
PLOT_DIR.mkdir(exist_ok=True)

device = torch.device('cpu')

def timestamp():
    return time.strftime("%H:%M:%S")


def load_gpt2_and_data(num_seqs=50, seq_len=128):
    """Load GPT-2 small with eager attention and WikiText-2 validation data."""
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    from datasets import load_dataset

    print(f"[{timestamp()}] Loading GPT-2 small (eager attention)...")
    model = GPT2LMHeadModel.from_pretrained('gpt2', attn_implementation='eager')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
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
# EVICTION MASK GENERATORS
# Each takes attention weights (heads, seq, seq) and returns a binary mask
###############################################################################

def mask_recent_k(attn_weights, keep_ratio):
    """Keep only the K most recent tokens per query position."""
    n_heads, seq_len, _ = attn_weights.shape
    mask = torch.zeros_like(attn_weights)
    for pos in range(seq_len):
        context_len = pos + 1
        k = max(1, int(context_len * keep_ratio))
        start = max(0, context_len - k)
        mask[:, pos, start:context_len] = 1.0
    return mask


def mask_sink_recent(attn_weights, keep_ratio):
    """Keep first token (attention sink) + K most recent tokens."""
    n_heads, seq_len, _ = attn_weights.shape
    mask = torch.zeros_like(attn_weights)
    for pos in range(seq_len):
        context_len = pos + 1
        k = max(1, int(context_len * keep_ratio))
        # Always keep position 0 (sink)
        mask[:, pos, 0] = 1.0
        # Keep last (k-1) recent positions
        recent_k = max(1, k - 1)
        start = max(0, context_len - recent_k)
        mask[:, pos, start:context_len] = 1.0
    return mask


def mask_heavy_hitter(attn_weights, keep_ratio):
    """Keep tokens with highest cumulative attention (H2O-style).
    Uses the attention weights themselves to determine importance."""
    n_heads, seq_len, _ = attn_weights.shape
    mask = torch.zeros_like(attn_weights)
    # Cumulative attention score per head per position
    cum_attn = torch.zeros(n_heads, seq_len, device=attn_weights.device)
    for pos in range(seq_len):
        context_len = pos + 1
        k = max(1, int(context_len * keep_ratio))
        # Update cumulative attention
        cum_attn[:, :context_len] += attn_weights[:, pos, :context_len]
        if context_len <= k:
            mask[:, pos, :context_len] = 1.0
        else:
            for h in range(n_heads):
                _, topk_idx = cum_attn[h, :context_len].topk(k)
                mask[h, pos, topk_idx] = 1.0
    return mask


def mask_entropy_adaptive(attn_weights, keep_ratio, head_entropies=None,
                          layer_idx=0, num_heads=12):
    """Per-head adaptive: sparse heads get fewer KV entries, dense heads more."""
    n_heads, seq_len, _ = attn_weights.shape
    mask = torch.zeros_like(attn_weights)

    for h in range(n_heads):
        # Determine per-head budget
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
# Replace eager_attention_forward to apply eviction masks after softmax
###############################################################################

# Global state for the eviction experiment
_eviction_state = {
    'active': False,
    'strategy': None,       # 'recent_k', 'sink_recent', 'heavy_hitter', 'entropy_adaptive'
    'keep_ratio': 1.0,
    'head_entropies': None,
    'layer_counter': 0,     # Reset before each forward pass
}


def patched_eager_attention_forward(module, query, key, value, attention_mask, **kwargs):
    """Modified eager attention that applies eviction masks after softmax."""
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

    # === EVICTION HAPPENS HERE ===
    if _eviction_state['active']:
        strategy = _eviction_state['strategy']
        keep_ratio = _eviction_state['keep_ratio']
        layer_idx = _eviction_state['layer_counter']
        _eviction_state['layer_counter'] += 1

        # attn_weights shape: (batch, heads, seq, seq)
        aw = attn_weights[0]  # (heads, seq, seq)

        if strategy == 'recent_k':
            eviction_mask = mask_recent_k(aw, keep_ratio)
        elif strategy == 'sink_recent':
            eviction_mask = mask_sink_recent(aw, keep_ratio)
        elif strategy == 'heavy_hitter':
            eviction_mask = mask_heavy_hitter(aw, keep_ratio)
        elif strategy == 'entropy_adaptive':
            eviction_mask = mask_entropy_adaptive(
                aw, keep_ratio, _eviction_state['head_entropies'],
                layer_idx, aw.shape[0])
        else:
            eviction_mask = torch.ones_like(aw)

        # Apply mask and renormalize
        masked_aw = aw * eviction_mask
        row_sums = masked_aw.sum(dim=-1, keepdim=True).clamp(min=1e-10)
        masked_aw = masked_aw / row_sums
        attn_weights = masked_aw.unsqueeze(0)  # (1, heads, seq, seq)

    attn_output = torch.matmul(attn_weights, value)
    attn_output = attn_output.transpose(1, 2)

    return attn_output, attn_weights


def install_patch(model):
    """Install the monkey-patched attention forward."""
    import transformers.models.gpt2.modeling_gpt2 as gpt2_module

    # Replace the eager attention function in the global registry
    gpt2_module.ALL_ATTENTION_FUNCTIONS["eager"] = patched_eager_attention_forward
    print("  Attention patch installed")


def run_with_eviction(model, input_ids, strategy, keep_ratio, head_entropies=None):
    """Run a forward pass with the specified eviction strategy active."""
    _eviction_state['active'] = True
    _eviction_state['strategy'] = strategy
    _eviction_state['keep_ratio'] = keep_ratio
    _eviction_state['head_entropies'] = head_entropies
    _eviction_state['layer_counter'] = 0

    with torch.no_grad():
        outputs = model(input_ids, output_attentions=True)

    _eviction_state['active'] = False
    return outputs


def run_baseline(model, input_ids):
    """Run a forward pass with no eviction (baseline)."""
    _eviction_state['active'] = False
    with torch.no_grad():
        outputs = model(input_ids, output_attentions=True)
    return outputs


###############################################################################
# EXPERIMENT 1: KV Eviction Strategy Comparison
###############################################################################
def experiment_1(model, tokenizer, sequences):
    print(f"\n{'='*70}")
    print(f"[{timestamp()}] EXPERIMENT 1: KV Eviction Strategy Comparison")
    print(f"{'='*70}")

    num_layers = len(model.transformer.h)
    num_heads = model.config.n_head
    seq_len = len(sequences[0])

    # First pass: collect head entropies for the entropy-adaptive strategy
    print(f"[{timestamp()}] Phase 1: Computing per-head entropies...")
    head_entropies = defaultdict(list)

    t0 = time.time()
    for seq_idx in range(min(20, len(sequences))):
        if seq_idx % 10 == 0:
            print(f"  Sequence {seq_idx+1}/{min(20, len(sequences))} ({time.time()-t0:.0f}s)")
        input_ids = torch.tensor([sequences[seq_idx]], device=device)
        outputs = run_baseline(model, input_ids)

        for layer_idx, attn_tensor in enumerate(outputs.attentions):
            attn = attn_tensor[0].detach()  # (heads, seq, seq)
            for head_idx in range(num_heads):
                for pos in [seq_len // 4, seq_len // 2, 3 * seq_len // 4, seq_len - 1]:
                    row = attn[head_idx, pos, :pos + 1]
                    row_pos = row[row > 1e-10]
                    entropy = -(row_pos * torch.log2(row_pos)).sum().item() if len(row_pos) > 0 else 0.0
                    head_entropies[(layer_idx, head_idx)].append(entropy)

    head_entropy_means = {k: np.mean(v) for k, v in head_entropies.items()}
    print(f"  Head entropy range: {min(head_entropy_means.values()):.2f} - "
          f"{max(head_entropy_means.values()):.2f} bits")

    # Phase 2: Test eviction strategies
    print(f"\n[{timestamp()}] Phase 2: Testing eviction strategies...")

    strategies = ['recent_k', 'sink_recent', 'heavy_hitter', 'entropy_adaptive']
    keep_ratios = [1.0, 0.50, 0.25, 0.10, 0.05]

    # Collect baselines first
    print(f"  Collecting baselines...")
    num_seqs = min(30, len(sequences))
    baseline_preds = []
    baseline_probs = []
    baseline_top5 = []

    for seq_idx in range(num_seqs):
        input_ids = torch.tensor([sequences[seq_idx]], device=device)
        outputs = run_baseline(model, input_ids)
        logits = outputs.logits[0].detach()
        preds = logits.argmax(dim=-1)
        probs = torch.softmax(logits, dim=-1)
        t5 = torch.topk(logits, 5, dim=-1).indices

        baseline_preds.append(preds)
        baseline_probs.append(probs)
        baseline_top5.append(t5)

    results = {}

    for strat_name in strategies:
        results[strat_name] = {}
        for keep_ratio in keep_ratios:
            print(f"  {strat_name} @ {keep_ratio*100:.0f}%...", end=" ", flush=True)
            t_start = time.time()

            total_tokens = 0
            exact_matches = 0
            top5_matches = 0
            kl_divergences = []

            for seq_idx in range(num_seqs):
                input_ids = torch.tensor([sequences[seq_idx]], device=device)
                outputs = run_with_eviction(model, input_ids, strat_name,
                                           keep_ratio, head_entropy_means)
                mod_logits = outputs.logits[0].detach()
                mod_preds = mod_logits.argmax(dim=-1)

                # Compare to baseline
                exact_matches += (mod_preds == baseline_preds[seq_idx]).sum().item()

                mod_top5 = torch.topk(mod_logits, 5, dim=-1).indices
                for t in range(seq_len):
                    if mod_preds[t] in baseline_top5[seq_idx][t]:
                        top5_matches += 1

                mod_probs = torch.softmax(mod_logits, dim=-1)
                kl = torch.sum(baseline_probs[seq_idx] *
                              (torch.log(baseline_probs[seq_idx] + 1e-10) -
                               torch.log(mod_probs + 1e-10)), dim=-1)
                kl_divergences.extend(kl.tolist())
                total_tokens += seq_len

            match_rate = exact_matches / total_tokens
            top5_rate = top5_matches / total_tokens
            mean_kl = np.mean(kl_divergences)
            median_kl = np.median(kl_divergences)

            elapsed = time.time() - t_start
            print(f"match={match_rate:.3f} top5={top5_rate:.3f} "
                  f"KL={mean_kl:.4f} ({elapsed:.1f}s)")

            results[strat_name][keep_ratio] = {
                'exact_match_rate': match_rate,
                'top5_match_rate': top5_rate,
                'mean_kl_divergence': mean_kl,
                'median_kl_divergence': median_kl,
                'total_tokens': total_tokens,
            }

    return results, head_entropy_means


###############################################################################
# EXPERIMENT 2: Per-Head Sparsity Analysis & Head Type Clustering
###############################################################################
def experiment_2(model, tokenizer, sequences):
    print(f"\n{'='*70}")
    print(f"[{timestamp()}] EXPERIMENT 2: Per-Head Sparsity Analysis")
    print(f"{'='*70}")

    num_layers = len(model.transformer.h)
    num_heads = model.config.n_head
    seq_len = len(sequences[0])

    head_stats = defaultdict(lambda: {
        'entropy': [], 'top1_frac': [], 'top5_frac': [], 'top10_frac': [],
        'sink_frac': [], 'self_frac': [], 'local_frac': [],
        'sparsity_001': [],
    })

    t0 = time.time()
    num_seqs_to_use = min(30, len(sequences))
    print(f"  Analyzing {num_seqs_to_use} sequences...")

    for seq_idx in range(num_seqs_to_use):
        if seq_idx % 10 == 0:
            print(f"  Sequence {seq_idx+1}/{num_seqs_to_use} ({time.time()-t0:.0f}s)")
        input_ids = torch.tensor([sequences[seq_idx]], device=device)
        outputs = run_baseline(model, input_ids)

        for layer_idx, attn_tensor in enumerate(outputs.attentions):
            attn = attn_tensor[0].detach()
            for head_idx in range(num_heads):
                for pos in [seq_len // 4, seq_len // 2, 3 * seq_len // 4, seq_len - 1]:
                    row = attn[head_idx, pos, :pos + 1]
                    key = (layer_idx, head_idx)

                    row_pos = row[row > 1e-10]
                    entropy = -(row_pos * torch.log2(row_pos)).sum().item() if len(row_pos) > 0 else 0.0
                    head_stats[key]['entropy'].append(entropy)

                    sorted_row, _ = row.sort(descending=True)
                    head_stats[key]['top1_frac'].append(sorted_row[0].item())
                    head_stats[key]['top5_frac'].append(sorted_row[:min(5, len(sorted_row))].sum().item())
                    head_stats[key]['top10_frac'].append(sorted_row[:min(10, len(sorted_row))].sum().item())

                    head_stats[key]['sink_frac'].append(row[0].item())
                    head_stats[key]['self_frac'].append(row[pos].item() if pos < len(row) else 0.0)

                    local_start = max(0, pos - 5)
                    local_frac = row[local_start:pos + 1].sum().item()
                    head_stats[key]['local_frac'].append(local_frac)

                    s = (row < 0.01).float().mean().item()
                    head_stats[key]['sparsity_001'].append(s)

    head_summary = {}
    for key in head_stats:
        head_summary[key] = {
            metric: np.mean(values) for metric, values in head_stats[key].items()
        }

    # Classify head types
    head_types = {}
    type_counts = defaultdict(int)

    for key, stats in head_summary.items():
        if stats['sink_frac'] > 0.5:
            htype = 'sink'
        elif stats['local_frac'] > 0.7:
            htype = 'positional'
        elif stats['entropy'] < 1.5:
            htype = 'focused'
        elif stats['entropy'] > 4.0:
            htype = 'diffuse'
        elif stats['top5_frac'] > 0.8:
            htype = 'selective'
        else:
            htype = 'mixed'

        head_types[key] = htype
        type_counts[htype] += 1

    total_heads = num_layers * num_heads
    print(f"\n--- Head Type Distribution ---")
    for htype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {htype:12s}: {count:3d} / {total_heads} ({count/total_heads*100:.1f}%)")

    compressible = type_counts.get('sink', 0) + type_counts.get('positional', 0) + \
                   type_counts.get('focused', 0) + type_counts.get('selective', 0)
    print(f"\n  Compressible heads: {compressible}/{total_heads} ({compressible/total_heads*100:.1f}%)")
    print(f"  Hard to compress:  {type_counts.get('diffuse', 0) + type_counts.get('mixed', 0)}/{total_heads}")

    return head_summary, head_types, dict(type_counts)


###############################################################################
# EXPERIMENT 3: Quality vs Compression Pareto Frontier
###############################################################################
def experiment_3(model, tokenizer, sequences, strategy_name, head_entropy_means=None):
    print(f"\n{'='*70}")
    print(f"[{timestamp()}] EXPERIMENT 3: Pareto Frontier ({strategy_name})")
    print(f"{'='*70}")

    seq_len = len(sequences[0])
    retention_rates = [1.0, 0.75, 0.50, 0.40, 0.30, 0.20, 0.15, 0.10, 0.07, 0.05, 0.03]

    num_seqs = min(20, len(sequences))
    print(f"  Testing {len(retention_rates)} retention rates on {num_seqs} sequences")

    # Collect baselines
    print(f"[{timestamp()}] Collecting baselines...")
    baseline_preds_list = []
    baseline_probs_list = []
    baseline_top5_list = []

    for seq_idx in range(num_seqs):
        input_ids = torch.tensor([sequences[seq_idx]], device=device)
        outputs = run_baseline(model, input_ids)
        logits = outputs.logits[0].detach()
        baseline_preds_list.append(logits.argmax(dim=-1))
        baseline_probs_list.append(torch.softmax(logits, dim=-1))
        baseline_top5_list.append(torch.topk(logits, 5, dim=-1).indices)

    pareto_results = {}

    for keep_ratio in retention_rates:
        print(f"  Retention={keep_ratio*100:.0f}%...", end=" ", flush=True)
        t_start = time.time()

        total_tokens = 0
        exact_matches = 0
        top5_matches = 0
        kl_divs = []

        for seq_idx in range(num_seqs):
            input_ids = torch.tensor([sequences[seq_idx]], device=device)
            outputs = run_with_eviction(model, input_ids, strategy_name,
                                       keep_ratio, head_entropy_means)
            mod_logits = outputs.logits[0].detach()
            mod_preds = mod_logits.argmax(dim=-1)

            exact_matches += (mod_preds == baseline_preds_list[seq_idx]).sum().item()
            for t in range(seq_len):
                if mod_preds[t] in baseline_top5_list[seq_idx][t]:
                    top5_matches += 1

            mod_probs = torch.softmax(mod_logits, dim=-1)
            kl = torch.sum(baseline_probs_list[seq_idx] *
                          (torch.log(baseline_probs_list[seq_idx] + 1e-10) -
                           torch.log(mod_probs + 1e-10)), dim=-1)
            kl_divs.extend(kl.tolist())
            total_tokens += seq_len

        match_rate = exact_matches / total_tokens
        top5_rate = top5_matches / total_tokens
        mean_kl = np.mean(kl_divs)

        elapsed = time.time() - t_start
        print(f"match={match_rate:.3f} top5={top5_rate:.3f} KL={mean_kl:.4f} ({elapsed:.1f}s)")

        pareto_results[keep_ratio] = {
            'exact_match_rate': match_rate,
            'top5_match_rate': top5_rate,
            'mean_kl_divergence': mean_kl,
            'compression_ratio': 1.0 / keep_ratio if keep_ratio > 0 else float('inf'),
        }

    return pareto_results


###############################################################################
# PLOTTING
###############################################################################
def plot_strategies(results, save_dir):
    """Plot 1: Eviction strategy comparison."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    colors = {
        'recent_k': '#e74c3c',
        'sink_recent': '#2ecc71',
        'heavy_hitter': '#3498db',
        'entropy_adaptive': '#9b59b6',
    }
    markers = {
        'recent_k': 'o',
        'sink_recent': 's',
        'heavy_hitter': '^',
        'entropy_adaptive': 'D',
    }

    for strat_name in ['recent_k', 'sink_recent', 'heavy_hitter', 'entropy_adaptive']:
        if strat_name not in results:
            continue
        strat_data = results[strat_name]
        ratios = sorted(strat_data.keys())
        match_rates = [strat_data[r]['exact_match_rate'] for r in ratios]
        top5_rates = [strat_data[r]['top5_match_rate'] for r in ratios]
        kl_divs = [strat_data[r]['mean_kl_divergence'] for r in ratios]
        compressions = [1.0 / r for r in ratios]

        label = strat_name.replace('_', ' ').title()
        c = colors[strat_name]
        m = markers[strat_name]

        axes[0].plot(compressions, match_rates, f'-{m}', color=c, label=label,
                    linewidth=2, markersize=8)
        axes[1].plot(compressions, top5_rates, f'-{m}', color=c, label=label,
                    linewidth=2, markersize=8)
        axes[2].plot(compressions, kl_divs, f'-{m}', color=c, label=label,
                    linewidth=2, markersize=8)

    axes[0].set_xlabel('Compression Ratio (x)', fontsize=12)
    axes[0].set_ylabel('Exact Match Rate', fontsize=12)
    axes[0].set_title('Exact Match vs Full KV', fontsize=14)
    axes[0].legend(fontsize=10)
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel('Compression Ratio (x)', fontsize=12)
    axes[1].set_ylabel('Top-5 Match Rate', fontsize=12)
    axes[1].set_title('Top-5 Match vs Full KV', fontsize=14)
    axes[1].set_ylim(-0.05, 1.05)
    axes[1].grid(True, alpha=0.3)

    axes[2].set_xlabel('Compression Ratio (x)', fontsize=12)
    axes[2].set_ylabel('KL Divergence', fontsize=12)
    axes[2].set_title('KL Divergence from Full KV', fontsize=14)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_dir / 'kv_comp_strategies.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved kv_comp_strategies.png")


def plot_head_entropy(head_summary, num_layers, num_heads, save_dir):
    """Plot 3: Per-head entropy heatmap."""
    entropy_map = np.zeros((num_layers, num_heads))
    for (layer, head), stats in head_summary.items():
        entropy_map[layer, head] = stats['entropy']

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(entropy_map, aspect='auto', cmap='viridis')
    ax.set_xlabel('Head Index', fontsize=13)
    ax.set_ylabel('Layer Index', fontsize=13)
    ax.set_title('Attention Entropy per Head (bits)', fontsize=14)
    ax.set_xticks(range(num_heads))
    ax.set_yticks(range(num_layers))
    ax.set_yticklabels([f'L{i+1}' for i in range(num_layers)])
    plt.colorbar(im, ax=ax, label='Entropy (bits)')

    for i in range(num_layers):
        for j in range(num_heads):
            val = entropy_map[i, j]
            color = 'white' if val < entropy_map.mean() else 'black'
            ax.text(j, i, f'{val:.1f}', ha='center', va='center', fontsize=7, color=color)

    plt.tight_layout()
    plt.savefig(save_dir / 'kv_comp_heads.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved kv_comp_heads.png")


def plot_head_types(head_types, type_counts, num_layers, num_heads, save_dir):
    """Plot 4: Head type distribution."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    type_to_int = {'sink': 0, 'positional': 1, 'focused': 2, 'selective': 3,
                   'mixed': 4, 'diffuse': 5}
    type_map = np.zeros((num_layers, num_heads))
    for (layer, head), htype in head_types.items():
        type_map[layer, head] = type_to_int.get(htype, 4)

    from matplotlib.colors import ListedColormap
    colors_list = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12', '#95a5a6', '#8e44ad']
    cmap = ListedColormap(colors_list[:len(type_to_int)])

    im = axes[0].imshow(type_map, aspect='auto', cmap=cmap, vmin=-0.5,
                        vmax=len(type_to_int) - 0.5)
    axes[0].set_xlabel('Head Index', fontsize=13)
    axes[0].set_ylabel('Layer Index', fontsize=13)
    axes[0].set_title('Head Type Classification', fontsize=14)
    axes[0].set_xticks(range(num_heads))
    axes[0].set_yticks(range(num_layers))
    axes[0].set_yticklabels([f'L{i+1}' for i in range(num_layers)])

    cbar = plt.colorbar(im, ax=axes[0], ticks=range(len(type_to_int)))
    cbar.ax.set_yticklabels(list(type_to_int.keys()))

    labels = list(type_counts.keys())
    sizes = list(type_counts.values())
    pie_colors = [colors_list[type_to_int.get(l, 4)] for l in labels]
    axes[1].pie(sizes, labels=labels, colors=pie_colors, autopct='%1.1f%%',
               startangle=140, textprops={'fontsize': 11})
    axes[1].set_title('Head Type Distribution', fontsize=14)

    plt.tight_layout()
    plt.savefig(save_dir / 'kv_comp_head_types.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved kv_comp_head_types.png")


def plot_pareto(pareto_results, save_dir):
    """Plot 2: Pareto frontier."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    rates = sorted(pareto_results.keys(), reverse=True)
    compressions = [pareto_results[r]['compression_ratio'] for r in rates]
    match_rates = [pareto_results[r]['exact_match_rate'] for r in rates]
    top5_rates = [pareto_results[r]['top5_match_rate'] for r in rates]
    kl_divs = [pareto_results[r]['mean_kl_divergence'] for r in rates]

    axes[0].plot(compressions, match_rates, 'b-o', linewidth=2, markersize=8,
                label='Exact match')
    axes[0].plot(compressions, top5_rates, 'g-s', linewidth=2, markersize=8,
                label='Top-5 match')
    axes[0].set_xlabel('Compression Ratio (x)', fontsize=12)
    axes[0].set_ylabel('Match Rate', fontsize=12)
    axes[0].set_title('Quality vs Compression (Pareto Frontier)', fontsize=14)
    axes[0].legend(fontsize=11)
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].grid(True, alpha=0.3)

    # Find and mark the "knee"
    for i, mr in enumerate(match_rates):
        if mr < 0.9:
            axes[0].axvline(x=compressions[i], color='red', linestyle='--', alpha=0.5)
            axes[0].annotate(f'Quality knee\n({compressions[i]:.1f}x)',
                           xy=(compressions[i], mr),
                           xytext=(compressions[i] + 1, mr + 0.1),
                           fontsize=10, color='red',
                           arrowprops=dict(arrowstyle='->', color='red'))
            break

    axes[1].plot(compressions, kl_divs, 'r-^', linewidth=2, markersize=8)
    axes[1].set_xlabel('Compression Ratio (x)', fontsize=12)
    axes[1].set_ylabel('KL Divergence (nats)', fontsize=12)
    axes[1].set_title('Information Loss vs Compression', fontsize=14)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_dir / 'kv_comp_pareto.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved kv_comp_pareto.png")


def plot_match_rate(results, save_dir):
    """Plot 5: Exact match rate comparison across strategies."""
    fig, ax = plt.subplots(figsize=(10, 7))

    keep_ratios = [0.50, 0.25, 0.10, 0.05]
    x = np.arange(len(keep_ratios))
    width = 0.18

    colors = {
        'recent_k': '#e74c3c',
        'sink_recent': '#2ecc71',
        'heavy_hitter': '#3498db',
        'entropy_adaptive': '#9b59b6',
    }

    for i, (strat_name, color) in enumerate(colors.items()):
        if strat_name not in results:
            continue
        strat_data = results[strat_name]
        match_rates = [strat_data.get(r, {}).get('exact_match_rate', 0) for r in keep_ratios]
        label = strat_name.replace('_', ' ').title()
        ax.bar(x + i * width, match_rates, width, label=label, color=color, alpha=0.85)

    ax.set_xlabel('KV Cache Retention Rate', fontsize=12)
    ax.set_ylabel('Exact Match Rate vs Full KV', fontsize=12)
    ax.set_title('Strategy Comparison at Each Compression Level', fontsize=14)
    ax.set_xticks(x + 1.5 * width)
    ax.set_xticklabels([f'{r*100:.0f}%' for r in keep_ratios])
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_dir / 'kv_comp_match_rate.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved kv_comp_match_rate.png")


###############################################################################
# VERIFICATION
###############################################################################
def verify_patch(model, sequences):
    """Verify the monkey-patch actually changes outputs."""
    print(f"\n[{timestamp()}] Verifying attention patch works...")
    seq_len = len(sequences[0])
    input_ids = torch.tensor([sequences[0]], device=device)

    # Baseline
    baseline_out = run_baseline(model, input_ids)
    baseline_logits = baseline_out.logits[0].detach()

    # With aggressive eviction (5% retention, recent_k)
    evicted_out = run_with_eviction(model, input_ids, 'recent_k', 0.05)
    evicted_logits = evicted_out.logits[0].detach()

    diff = (baseline_logits - evicted_logits).abs().max().item()
    match_rate = (baseline_logits.argmax(-1) == evicted_logits.argmax(-1)).float().mean().item()

    print(f"  Max logit difference (5% recent_k vs full): {diff:.4f}")
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
    print(f"{'='*70}")
    print(f"KV CACHE COMPRESSION EXPERIMENTS")
    print(f"{'='*70}")
    print(f"Start time: {timestamp()}")
    t_total = time.time()

    # Load model and data
    model, tokenizer, sequences = load_gpt2_and_data(num_seqs=50, seq_len=128)

    num_layers = len(model.transformer.h)
    num_heads = model.config.n_head

    # Install the monkey-patch
    install_patch(model)

    # Verify it works
    if not verify_patch(model, sequences):
        print("ABORTING: Patch verification failed.")
        return None

    # Experiment 1: Strategy comparison
    exp1_results, head_entropy_means = experiment_1(model, tokenizer, sequences)

    # Experiment 2: Per-head analysis
    head_summary, head_types, type_counts = experiment_2(model, tokenizer, sequences)

    # Determine best strategy from Exp 1 at 10% retention
    best_strategy = None
    best_match = -1
    for strat_name in ['recent_k', 'sink_recent', 'heavy_hitter', 'entropy_adaptive']:
        if strat_name in exp1_results and 0.10 in exp1_results[strat_name]:
            mr = exp1_results[strat_name][0.10]['exact_match_rate']
            if mr > best_match:
                best_match = mr
                best_strategy = strat_name

    print(f"\n[{timestamp()}] Best strategy at 10x compression: {best_strategy} "
          f"(match rate: {best_match:.3f})")

    # Experiment 3: Pareto frontier with entropy-adaptive and best non-adaptive
    exp3_entropy = experiment_3(model, tokenizer, sequences[:20],
                                'entropy_adaptive', head_entropy_means)

    # Also run Pareto for the best non-entropy strategy for comparison
    best_non_entropy = None
    best_ne_match = -1
    for sn in ['recent_k', 'sink_recent', 'heavy_hitter']:
        if sn in exp1_results and 0.10 in exp1_results[sn]:
            mr = exp1_results[sn][0.10]['exact_match_rate']
            if mr > best_ne_match:
                best_ne_match = mr
                best_non_entropy = sn

    if best_non_entropy and best_non_entropy != 'entropy_adaptive':
        exp3_comparison = experiment_3(model, tokenizer, sequences[:20],
                                       best_non_entropy)
    else:
        exp3_comparison = None

    # Plots
    print(f"\n[{timestamp()}] Generating plots...")
    plot_strategies(exp1_results, PLOT_DIR)
    plot_head_entropy(head_summary, num_layers, num_heads, PLOT_DIR)
    plot_head_types(head_types, type_counts, num_layers, num_heads, PLOT_DIR)
    plot_pareto(exp3_entropy, PLOT_DIR)
    plot_match_rate(exp1_results, PLOT_DIR)

    # Compile results
    all_results = {
        'experiment_1_strategies': {},
        'experiment_2_head_types': type_counts,
        'experiment_2_head_entropy_range': {
            'min': float(min(head_entropy_means.values())),
            'max': float(max(head_entropy_means.values())),
            'mean': float(np.mean(list(head_entropy_means.values()))),
        },
        'experiment_3_pareto_entropy_adaptive': {},
        'experiment_3_pareto_comparison': {},
        'best_strategy_at_10x': best_strategy,
        'best_strategy_match_rate': best_match,
        'runtime_seconds': time.time() - t_total,
    }

    for strat_name, strat_data in exp1_results.items():
        all_results['experiment_1_strategies'][strat_name] = {
            str(k): v for k, v in strat_data.items()
        }

    for k, v in exp3_entropy.items():
        all_results['experiment_3_pareto_entropy_adaptive'][str(k)] = v

    if exp3_comparison:
        for k, v in exp3_comparison.items():
            all_results['experiment_3_pareto_comparison'][str(k)] = v
        all_results['pareto_comparison_strategy'] = best_non_entropy

    all_results['experiment_2_head_entropies'] = {
        f"L{k[0]}_H{k[1]}": float(v) for k, v in head_entropy_means.items()
    }

    results_path = PLOT_DIR / 'kv_comp_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  Saved results to {results_path}")

    total_time = time.time() - t_total
    print(f"\n{'='*70}")
    print(f"COMPLETE - Total runtime: {total_time/60:.1f} minutes")
    print(f"{'='*70}")

    return all_results


if __name__ == '__main__':
    results = main()
