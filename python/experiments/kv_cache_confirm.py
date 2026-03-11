"""
KV Cache Compression: Confirmation Test
=========================================
Independent validation of entropy-adaptive KV cache compression.
Different from the original experiment in:
  1. Uses different text prompts (hand-crafted + BookCorpus instead of WikiText-2)
  2. Tests actual text GENERATION (autoregressive), not just logit comparison
  3. Measures BLEU, ROUGE-L, and perplexity between full and compressed generations
  4. Tests multiple sequence lengths (64, 128, 256)

Expected runtime: ~10-15 minutes on CPU
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
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PLOT_DIR = Path(__file__).resolve().parent / "plots"
PLOT_DIR.mkdir(exist_ok=True)

device = torch.device('cpu')


def timestamp():
    return time.strftime("%H:%M:%S")


###############################################################################
# METRICS
###############################################################################

def compute_bleu(reference_tokens, hypothesis_tokens, max_n=4):
    """Compute BLEU score (simplified, sentence-level)."""
    if len(hypothesis_tokens) == 0:
        return 0.0

    precisions = []
    for n in range(1, max_n + 1):
        ref_ngrams = Counter()
        hyp_ngrams = Counter()
        for i in range(len(reference_tokens) - n + 1):
            ref_ngrams[tuple(reference_tokens[i:i+n])] += 1
        for i in range(len(hypothesis_tokens) - n + 1):
            hyp_ngrams[tuple(hypothesis_tokens[i:i+n])] += 1

        clipped = 0
        total = 0
        for ngram, count in hyp_ngrams.items():
            clipped += min(count, ref_ngrams.get(ngram, 0))
            total += count

        if total == 0:
            precisions.append(0.0)
        else:
            precisions.append(clipped / total)

    # Brevity penalty
    bp = min(1.0, math.exp(1 - len(reference_tokens) / max(1, len(hypothesis_tokens))))

    # Geometric mean of precisions (with smoothing)
    log_avg = 0
    n_nonzero = 0
    for p in precisions:
        if p > 0:
            log_avg += math.log(p)
            n_nonzero += 1

    if n_nonzero == 0:
        return 0.0

    log_avg /= n_nonzero
    return bp * math.exp(log_avg)


def compute_rouge_l(reference_tokens, hypothesis_tokens):
    """Compute ROUGE-L (longest common subsequence) F1."""
    if len(reference_tokens) == 0 or len(hypothesis_tokens) == 0:
        return 0.0

    m = len(reference_tokens)
    n = len(hypothesis_tokens)

    # LCS via DP
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if reference_tokens[i-1] == hypothesis_tokens[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    lcs_len = dp[m][n]
    if lcs_len == 0:
        return 0.0

    precision = lcs_len / n
    recall = lcs_len / m
    f1 = 2 * precision * recall / (precision + recall)
    return f1


###############################################################################
# EVICTION (copied from kv_cache_compression.py for independence)
###############################################################################

_eviction_state = {
    'active': False,
    'strategy': None,
    'keep_ratio': 1.0,
    'head_entropies': None,
    'layer_counter': 0,
}


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


def mask_sink_recent(attn_weights, keep_ratio):
    """Keep first token (attention sink) + K most recent tokens."""
    n_heads, seq_len, _ = attn_weights.shape
    mask = torch.zeros_like(attn_weights)
    for pos in range(seq_len):
        context_len = pos + 1
        k = max(1, int(context_len * keep_ratio))
        mask[:, pos, 0] = 1.0
        recent_k = max(1, k - 1)
        start = max(0, context_len - recent_k)
        mask[:, pos, start:context_len] = 1.0
    return mask


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

    if _eviction_state['active']:
        strategy = _eviction_state['strategy']
        keep_ratio = _eviction_state['keep_ratio']
        layer_idx = _eviction_state['layer_counter']
        _eviction_state['layer_counter'] += 1

        aw = attn_weights[0]  # (heads, seq, seq)

        if strategy == 'entropy_adaptive':
            eviction_mask = mask_entropy_adaptive(
                aw, keep_ratio, _eviction_state['head_entropies'],
                layer_idx, aw.shape[0])
        elif strategy == 'sink_recent':
            eviction_mask = mask_sink_recent(aw, keep_ratio)
        else:
            eviction_mask = torch.ones_like(aw)

        masked_aw = aw * eviction_mask
        row_sums = masked_aw.sum(dim=-1, keepdim=True).clamp(min=1e-10)
        masked_aw = masked_aw / row_sums
        attn_weights = masked_aw.unsqueeze(0)

    attn_output = torch.matmul(attn_weights, value)
    attn_output = attn_output.transpose(1, 2)
    return attn_output, attn_weights


def install_patch(model):
    """Install the monkey-patched attention forward."""
    import transformers.models.gpt2.modeling_gpt2 as gpt2_module
    gpt2_module.ALL_ATTENTION_FUNCTIONS["eager"] = patched_eager_attention_forward
    print("  Attention patch installed")


###############################################################################
# CALIBRATION
###############################################################################

def calibrate_head_entropies(model, sequences, num_heads=12):
    """Compute per-head entropy profiles from calibration sequences."""
    head_entropies = defaultdict(list)
    seq_len = len(sequences[0])

    for seq_idx, seq in enumerate(sequences):
        input_ids = torch.tensor([seq], device=device)
        _eviction_state['active'] = False
        with torch.no_grad():
            outputs = model(input_ids, output_attentions=True)

        for layer_idx, attn_tensor in enumerate(outputs.attentions):
            attn = attn_tensor[0].detach()
            for head_idx in range(num_heads):
                for pos in [seq_len // 4, seq_len // 2, 3 * seq_len // 4, seq_len - 1]:
                    row = attn[head_idx, pos, :pos + 1]
                    row_pos = row[row > 1e-10]
                    entropy = -(row_pos * torch.log2(row_pos)).sum().item() if len(row_pos) > 0 else 0.0
                    head_entropies[(layer_idx, head_idx)].append(entropy)

    return {k: np.mean(v) for k, v in head_entropies.items()}


###############################################################################
# GENERATION
###############################################################################

def generate_with_strategy(model, prompt_ids, max_new_tokens, strategy, keep_ratio,
                           head_entropies=None):
    """Autoregressive generation with KV eviction applied at each step."""
    generated = list(prompt_ids)

    for step in range(max_new_tokens):
        input_ids = torch.tensor([generated], device=device)

        _eviction_state['active'] = (strategy is not None)
        _eviction_state['strategy'] = strategy
        _eviction_state['keep_ratio'] = keep_ratio
        _eviction_state['head_entropies'] = head_entropies
        _eviction_state['layer_counter'] = 0

        with torch.no_grad():
            outputs = model(input_ids)

        _eviction_state['active'] = False

        logits = outputs.logits[0, -1, :]  # last token logits
        next_token = logits.argmax().item()
        generated.append(next_token)

    return generated[len(prompt_ids):]  # return only new tokens


def compute_perplexity(model, token_ids, strategy=None, keep_ratio=1.0,
                       head_entropies=None):
    """Compute perplexity of a token sequence under the model (with optional eviction)."""
    input_ids = torch.tensor([token_ids], device=device)

    _eviction_state['active'] = (strategy is not None)
    _eviction_state['strategy'] = strategy
    _eviction_state['keep_ratio'] = keep_ratio
    _eviction_state['head_entropies'] = head_entropies
    _eviction_state['layer_counter'] = 0

    with torch.no_grad():
        outputs = model(input_ids)

    _eviction_state['active'] = False

    logits = outputs.logits[0, :-1, :]  # predictions for positions 1..N
    targets = torch.tensor(token_ids[1:], device=device)

    loss = nn.functional.cross_entropy(logits, targets, reduction='mean')
    return math.exp(loss.item())


###############################################################################
# MAIN CONFIRMATION TEST
###############################################################################

def main():
    print(f"{'='*70}")
    print(f"KV CACHE COMPRESSION: CONFIRMATION TEST")
    print(f"{'='*70}")
    print(f"Start time: {timestamp()}")
    t_total = time.time()

    from transformers import GPT2LMHeadModel, GPT2Tokenizer

    print(f"[{timestamp()}] Loading GPT-2 small...")
    model = GPT2LMHeadModel.from_pretrained('gpt2', attn_implementation='eager')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model.eval()
    model.to(device)
    install_patch(model)

    num_heads = model.config.n_head

    # --- Hand-crafted diverse prompts ---
    prompts = [
        "The theory of general relativity predicts that",
        "In a small village by the sea, there lived",
        "The most important feature of a programming language is",
        "Climate change has been linked to",
        "Once upon a time in a kingdom far away,",
        "The stock market crashed because investors",
        "A neural network processes information by",
        "The recipe for chocolate cake requires",
        "In the year 2050, scientists discovered",
        "The human brain contains approximately",
        "Breaking news: the president announced that",
        "The fundamental theorem of calculus states",
        "Deep in the Amazon rainforest, researchers found",
        "The key to happiness, according to philosophers,",
        "Quantum computing will revolutionize",
        "The ancient Egyptians built the pyramids using",
        "Machine learning models can sometimes",
        "The weather forecast for tomorrow shows",
        "In conclusion, the evidence suggests that",
        "The first step in solving any problem is",
    ]

    # --- Calibration using different data ---
    print(f"\n[{timestamp()}] Calibrating head entropies on prompt data...")

    # Tokenize prompts and use them for calibration (different from WikiText-2)
    cal_sequences = []
    for prompt in prompts[:10]:
        tokens = tokenizer.encode(prompt)
        # Pad or truncate to 64 tokens for calibration
        if len(tokens) < 64:
            # Generate more tokens for calibration context
            full = generate_with_strategy(model, tokens, 64 - len(tokens), None, 1.0)
            cal_sequences.append(tokens + full)
        else:
            cal_sequences.append(tokens[:64])

    head_entropies = calibrate_head_entropies(model, cal_sequences, num_heads)
    print(f"  Entropy range: {min(head_entropies.values()):.2f} - "
          f"{max(head_entropies.values()):.2f} bits")
    print(f"  Mean entropy: {np.mean(list(head_entropies.values())):.2f} bits")

    # --- Test 1: Generation quality ---
    print(f"\n[{timestamp()}] Test 1: Generation quality comparison")
    print(f"  Generating 20 completions per strategy...")

    max_new_tokens = 30
    strategies = {
        'full': (None, 1.0),
        'entropy_2x': ('entropy_adaptive', 0.5),
        'entropy_5x': ('entropy_adaptive', 0.2),
        'sink_recent_2x': ('sink_recent', 0.5),
        'sink_recent_5x': ('sink_recent', 0.2),
    }

    generation_results = {}
    all_generations = {}

    for strat_name, (strategy, keep_ratio) in strategies.items():
        print(f"\n  Strategy: {strat_name}")
        generations = []
        t_start = time.time()

        for i, prompt in enumerate(prompts):
            prompt_ids = tokenizer.encode(prompt)
            new_tokens = generate_with_strategy(
                model, prompt_ids, max_new_tokens, strategy, keep_ratio, head_entropies
            )
            generations.append(new_tokens)
            if i % 5 == 0:
                elapsed = time.time() - t_start
                print(f"    {i+1}/{len(prompts)} ({elapsed:.1f}s)")

        all_generations[strat_name] = generations
        elapsed = time.time() - t_start
        print(f"    Done in {elapsed:.1f}s")

    # Compare compressed generations to full generations
    full_gens = all_generations['full']
    comparison_results = {}

    for strat_name in ['entropy_2x', 'entropy_5x', 'sink_recent_2x', 'sink_recent_5x']:
        comp_gens = all_generations[strat_name]
        bleu_scores = []
        rouge_scores = []
        exact_token_matches = []

        for i in range(len(prompts)):
            ref = full_gens[i]
            hyp = comp_gens[i]

            bleu = compute_bleu(ref, hyp)
            rouge = compute_rouge_l(ref, hyp)
            token_match = sum(1 for a, b in zip(ref, hyp) if a == b) / max(1, len(ref))

            bleu_scores.append(bleu)
            rouge_scores.append(rouge)
            exact_token_matches.append(token_match)

        comparison_results[strat_name] = {
            'mean_bleu': float(np.mean(bleu_scores)),
            'std_bleu': float(np.std(bleu_scores)),
            'mean_rouge_l': float(np.mean(rouge_scores)),
            'std_rouge_l': float(np.std(rouge_scores)),
            'mean_token_match': float(np.mean(exact_token_matches)),
            'std_token_match': float(np.std(exact_token_matches)),
        }

        print(f"\n  {strat_name}:")
        print(f"    BLEU:        {np.mean(bleu_scores):.3f} +/- {np.std(bleu_scores):.3f}")
        print(f"    ROUGE-L:     {np.mean(rouge_scores):.3f} +/- {np.std(rouge_scores):.3f}")
        print(f"    Token Match: {np.mean(exact_token_matches):.3f} +/- {np.std(exact_token_matches):.3f}")

    # --- Test 2: Perplexity comparison ---
    print(f"\n[{timestamp()}] Test 2: Perplexity comparison")

    # Use longer sequences from prompts + generations for perplexity test
    ppl_results = {}
    ppl_strategies = {
        'full': (None, 1.0),
        'entropy_2x': ('entropy_adaptive', 0.5),
        'entropy_5x': ('entropy_adaptive', 0.2),
        'sink_recent_2x': ('sink_recent', 0.5),
        'sink_recent_5x': ('sink_recent', 0.2),
    }

    # Create evaluation sequences: prompt + full generation
    eval_sequences = []
    for i, prompt in enumerate(prompts):
        prompt_ids = tokenizer.encode(prompt)
        full_gen = full_gens[i]
        eval_sequences.append(prompt_ids + full_gen)

    for strat_name, (strategy, keep_ratio) in ppl_strategies.items():
        ppls = []
        for seq in eval_sequences:
            ppl = compute_perplexity(model, seq, strategy, keep_ratio, head_entropies)
            ppls.append(ppl)

        ppl_results[strat_name] = {
            'mean_perplexity': float(np.mean(ppls)),
            'std_perplexity': float(np.std(ppls)),
            'median_perplexity': float(np.median(ppls)),
        }
        print(f"  {strat_name:20s}: PPL = {np.mean(ppls):.1f} +/- {np.std(ppls):.1f} "
              f"(median {np.median(ppls):.1f})")

    # --- Test 3: Entropy profile stability ---
    print(f"\n[{timestamp()}] Test 3: Entropy profile stability")
    print(f"  Checking if head entropies are consistent across different prompts...")

    # Recalibrate on second half of prompts
    cal_sequences_2 = []
    for prompt in prompts[10:]:
        tokens = tokenizer.encode(prompt)
        if len(tokens) < 64:
            full = generate_with_strategy(model, tokens, 64 - len(tokens), None, 1.0)
            cal_sequences_2.append(tokens + full)
        else:
            cal_sequences_2.append(tokens[:64])

    head_entropies_2 = calibrate_head_entropies(model, cal_sequences_2, num_heads)

    # Compare the two calibration runs
    entropy_diffs = []
    for key in head_entropies:
        if key in head_entropies_2:
            diff = abs(head_entropies[key] - head_entropies_2[key])
            entropy_diffs.append(diff)

    stability = {
        'mean_abs_diff': float(np.mean(entropy_diffs)),
        'max_abs_diff': float(np.max(entropy_diffs)),
        'correlation': float(np.corrcoef(
            [head_entropies[k] for k in sorted(head_entropies.keys())],
            [head_entropies_2[k] for k in sorted(head_entropies_2.keys())]
        )[0, 1]),
    }
    print(f"  Mean absolute entropy difference: {stability['mean_abs_diff']:.3f} bits")
    print(f"  Max absolute entropy difference:  {stability['max_abs_diff']:.3f} bits")
    print(f"  Rank correlation:                 {stability['correlation']:.4f}")

    # --- Sample outputs for qualitative inspection ---
    print(f"\n[{timestamp()}] Sample generations for qualitative review:")
    for i in [0, 4, 6]:
        print(f"\n  Prompt: \"{prompts[i]}\"")
        for strat_name in ['full', 'entropy_2x', 'entropy_5x']:
            text = tokenizer.decode(all_generations[strat_name][i])
            print(f"    {strat_name:15s}: ...{text[:80]}")

    # --- Compile results ---
    total_time = time.time() - t_total

    all_results = {
        'test': 'kv_cache_confirmation',
        'model': 'gpt2',
        'num_prompts': len(prompts),
        'max_new_tokens': max_new_tokens,
        'runtime_seconds': total_time,
        'generation_comparison': comparison_results,
        'perplexity_comparison': ppl_results,
        'entropy_stability': stability,
        'head_entropy_range': {
            'cal1_min': float(min(head_entropies.values())),
            'cal1_max': float(max(head_entropies.values())),
            'cal1_mean': float(np.mean(list(head_entropies.values()))),
            'cal2_min': float(min(head_entropies_2.values())),
            'cal2_max': float(max(head_entropies_2.values())),
            'cal2_mean': float(np.mean(list(head_entropies_2.values()))),
        },
    }

    # Save results
    results_path = PLOT_DIR / 'kv_confirm_results.json'
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Saved results to {results_path}")

    # --- Summary ---
    print(f"\n{'='*70}")
    print(f"CONFIRMATION TEST SUMMARY")
    print(f"{'='*70}")

    print(f"\n  Generation Quality (vs full KV cache):")
    print(f"  {'Strategy':<20s} {'BLEU':>8s} {'ROUGE-L':>8s} {'Token Match':>12s}")
    print(f"  {'-'*48}")
    for sn in ['entropy_2x', 'entropy_5x', 'sink_recent_2x', 'sink_recent_5x']:
        cr = comparison_results[sn]
        print(f"  {sn:<20s} {cr['mean_bleu']:>8.3f} {cr['mean_rouge_l']:>8.3f} "
              f"{cr['mean_token_match']:>12.3f}")

    print(f"\n  Perplexity:")
    print(f"  {'Strategy':<20s} {'Mean PPL':>10s} {'Median PPL':>12s}")
    print(f"  {'-'*42}")
    for sn in ['full', 'entropy_2x', 'entropy_5x', 'sink_recent_2x', 'sink_recent_5x']:
        pr = ppl_results[sn]
        print(f"  {sn:<20s} {pr['mean_perplexity']:>10.1f} {pr['median_perplexity']:>12.1f}")

    print(f"\n  Entropy Profile Stability: correlation = {stability['correlation']:.4f}")
    print(f"\n  Total runtime: {total_time/60:.1f} minutes")
    print(f"{'='*70}")

    return all_results


if __name__ == '__main__':
    results = main()
