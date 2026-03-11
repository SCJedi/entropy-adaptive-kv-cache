# KV Cache Compression: Confirmation Test Results

**Date:** 2026-03-10
**Model:** GPT-2 small (124M parameters)
**Script:** `python/experiments/kv_cache_confirm.py`
**Runtime:** 3.7 minutes (CPU)

## Purpose

Independent validation of entropy-adaptive KV cache compression using:
- 20 diverse hand-crafted prompts (not WikiText-2)
- Actual autoregressive text generation (30 tokens per prompt)
- BLEU, ROUGE-L, exact token match, and perplexity metrics
- Entropy profile stability across different prompt sets

## Key Finding

**Entropy-adaptive compression produces coherent text at 2x compression and degrades gracefully at 5x.** It substantially outperforms the sink+recent baseline at both compression levels.

## Generation Quality (vs Full KV Cache)

| Strategy | BLEU | ROUGE-L | Token Match |
|---|---|---|---|
| entropy_2x (keep 50%) | 0.407 +/- 0.319 | 0.542 +/- 0.267 | 0.333 +/- 0.323 |
| entropy_5x (keep 20%) | 0.158 +/- 0.081 | 0.287 +/- 0.138 | 0.090 +/- 0.080 |
| sink_recent_2x | 0.158 +/- 0.138 | 0.227 +/- 0.127 | 0.062 +/- 0.063 |
| sink_recent_5x | 0.080 +/- 0.061 | 0.110 +/- 0.076 | 0.033 +/- 0.045 |

**At 2x compression**, entropy-adaptive achieves:
- 2.6x higher BLEU than sink+recent (0.407 vs 0.158)
- 2.4x higher ROUGE-L (0.542 vs 0.227)
- 5.4x higher exact token match rate (33.3% vs 6.2%)

**At 5x compression**, entropy-adaptive matches sink+recent 2x:
- BLEU: 0.158 vs 0.158 (equal)
- ROUGE-L: 0.287 vs 0.227 (27% better)
- Entropy-adaptive at 5x roughly equals sink+recent at 2x in generation quality

## Perplexity

| Strategy | Mean PPL | Median PPL | Ratio to Full |
|---|---|---|---|
| full (baseline) | 5.8 | 5.7 | 1.00x |
| entropy_2x | 6.5 | 6.1 | 1.13x |
| entropy_5x | 10.9 | 9.8 | 1.88x |
| sink_recent_2x | 14.6 | 14.4 | 2.52x |
| sink_recent_5x | 65.2 | 59.2 | 11.25x |

**Entropy-adaptive 2x adds only 13% perplexity** (5.8 -> 6.5). This is a remarkably small cost for halving the KV cache.

**Entropy-adaptive 5x (1.88x PPL ratio) still outperforms sink+recent 2x (2.52x PPL ratio)** -- meaning entropy-adaptive at 5x compression is better than the naive baseline at only 2x compression.

Sink+recent degrades catastrophically at 5x (65.2 PPL, 11x baseline).

## Entropy Profile Stability

Head entropy patterns are highly stable across different prompt sets:

| Metric | Value |
|---|---|
| Rank correlation between calibration sets | 0.975 |
| Mean absolute entropy difference | 0.169 bits |
| Max absolute entropy difference | 0.646 bits |
| Entropy range (cal set 1) | 0.09 - 5.03 bits |
| Entropy range (cal set 2) | 0.06 - 5.04 bits |

**Correlation of 0.975 confirms that head entropy profiles are an intrinsic property of the model**, not an artifact of particular input text. The same heads are consistently sparse or dense regardless of prompt content.

## Qualitative Examples

**Prompt: "The theory of general relativity predicts that"**
- full: "the universe is a continuous, continuous, and continuous universe..."
- entropy_2x: "the universe is a continuous, continuous, and continuous universe..." (identical)
- entropy_5x: "the universe is a 'superposition' of the two forces..." (different but coherent)

**Prompt: "A neural network processes information by"**
- full: "learning to recognize and respond to stimuli..."
- entropy_2x: "using a neural network to process information from a single input..." (different phrasing, coherent)
- entropy_5x: "which we can be trained..." (grammatically weaker but still topical)

## Interpretation

1. **Entropy-adaptive compression works.** At 2x, roughly a third of generated tokens are identical to the uncompressed baseline, and over half the tokens appear in the longest common subsequence (ROUGE-L 0.54). The text remains coherent and on-topic.

2. **The advantage over naive baselines is large.** Entropy-adaptive allocates more cache budget to high-entropy (broad attention) heads and less to low-entropy (sparse/focused) heads. This is fundamentally better than uniformly keeping sink + recent tokens.

3. **Head entropy is a stable signal.** With 0.975 rank correlation across disjoint prompt sets, calibration can be done once and reused. No per-input recalibration needed.

4. **5x compression is the practical limit for generation.** BLEU drops from 0.41 to 0.16 and perplexity nearly doubles. The text is still grammatical but diverges significantly from the full-cache output. For applications where approximate meaning preservation suffices (e.g., draft generation, retrieval), 5x may still be acceptable.

5. **2x compression is nearly free for perplexity.** Only 13% PPL increase suggests that roughly half of KV cache entries carry minimal information for next-token prediction. This aligns with the entropy theory: low-entropy heads are performing nearly deterministic lookups that survive aggressive pruning.

## Data

Full results: `python/experiments/plots/kv_confirm_results.json`
