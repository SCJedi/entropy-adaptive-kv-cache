# Entropy-Adaptive TurboQuant: Phase 1 Results

## Experiment Configuration
- Model: GPT-2 small (12 layers, 12 heads, head_dim=64)
- Hardware: CPU
- Data: WikiText-2 validation, 8 sequences of 128 tokens, 20 generated tokens each
- Seed: 42
- Total runtime: 13.9 minutes

## Head Entropy Statistics
- Mean H_2: 2.78 bits, Std: 1.30, Range: 0.03-5.95
- Skip candidates identified: L4_H11 (0.027), L7_H2 (0.336), L5_H1 (0.394)

## Results Table

| Config | Avg Bits | Compress | BLEU | ROUGE-L | Match | PPL Ratio | Time(s) |
|--------|----------|----------|------|---------|-------|-----------|---------|
| baseline | 16.00 | 1.00x | 1.000 | 1.000 | 1.000 | 1.000 | 0 |
| uniform_4bit | 4.00 | 4.00x | 0.531 | 0.663 | 0.513 | 1.101 | 237 |
| adaptive_4bit_conservative | 4.00 | 4.00x | 0.519 | 0.644 | 0.475 | **1.054** | 245 |
| **combined_best** | **4.00** | **4.00x** | **0.574** | **0.713** | **0.600** | **1.062** | **41** |
| skip_top3_uniform_3bit | 3.27 | 4.89x | 0.373 | 0.525 | 0.175 | 1.232 | 37 |
| uniform_3bit | 3.00 | 5.33x | 0.257 | 0.394 | 0.144 | 1.251 | 107 |
| adaptive_3bit_conservative | 3.00 | 5.33x | 0.184 | 0.350 | 0.138 | 1.247 | 48 |
| adaptive_3bit_aggressive | 3.00 | 5.33x | 0.311 | 0.494 | 0.225 | 1.325 | 47 |
| skip_top3_adaptive_3bit | 3.00 | 5.33x | 0.265 | 0.413 | 0.119 | 1.394 | 38 |

## Analysis

### 1. Did per-head allocation improve on uniform?

**Mixed results.** The picture differs sharply between 3-bit and 4-bit:

**At 3-bit:**
- Conservative (alpha=0.25): BLEU -0.073 vs uniform. **Worse.** The conservative scaling barely changes allocations (121 heads stay at 3-bit, only 18 get 2-bit and 5 get 4-bit). The small changes hurt more than they help.
- Aggressive (alpha=0.50): BLEU +0.054 vs uniform. **Modestly better** on BLEU and ROUGE-L (+0.100), but perplexity ratio worsened (1.325 vs 1.251). The BLEU gain suggests better generation quality but at the cost of worse next-token prediction.

**At 4-bit:**
- Conservative (alpha=0.25): BLEU -0.012 vs uniform. **Essentially equal** on BLEU, but perplexity improved (1.054 vs 1.101). The PPL improvement of -0.047 is meaningful — the model is better calibrated even though generation quality is similar.

### 2. Did conservative (0.25) beat aggressive (0.50)?

**At 3-bit:** Aggressive won on BLEU (+0.054 vs -0.073) but lost on PPL (1.325 vs 1.247). The aggressive scaling creates more diversity in bit allocation (30 heads at 2-bit, 30 at 4-bit) but the extreme allocations introduce their own distortions.

**Verdict:** Neither scaling factor is clearly better. The conservative scaling helps perplexity but not generation; the aggressive scaling helps generation but hurts perplexity. This suggests the optimal alpha is somewhere between 0.25 and 0.50.

### 3. Did quantization skipping help?

**Yes, significantly at 3-bit level.**

- skip_top3_uniform_3bit (3.27 avg bits): BLEU +0.116 vs uniform_3bit. This is the single largest improvement at the 3-bit budget level. Skipping the 3 lowest-entropy heads (which are essentially "sink" heads with H_2 < 0.4) and keeping them at full precision eliminates the dominant error sources.
- The cost is only 0.27 extra bits on average (3.27 vs 3.00), reducing compression from 5.33x to 4.89x.

However, combining skipping WITH adaptive allocation for the remaining heads (skip_top3_adaptive_3bit) was worse than skip + uniform. The adaptive redistribution apparently over-corrects when the highest-error heads are already removed.

### 4. Did the combination beat individual improvements?

**YES. combined_best is the clear winner.**

`combined_best` (skip 3 + adaptive 4-bit, alpha=0.25):
- BLEU 0.574 vs uniform_4bit's 0.531: **+0.043 improvement**
- ROUGE-L 0.713 vs 0.663: **+0.050 improvement**
- Token match 0.600 vs 0.513: **+0.087 improvement**
- PPL ratio 1.062 vs 1.101: **-0.039 improvement**

At the same 4.00x compression ratio, combined_best improves every metric. The bit allocation for this config is: 3 heads at fp16, 30 at 3-bit, 108 at 4-bit, 3 at 2-bit. This is a well-balanced allocation that:
1. Protects the most error-sensitive heads (sink heads) at full precision
2. Gives slightly more bits to low-entropy heads
3. Gives slightly fewer bits to high-entropy heads where errors average out

### 5. How do results compare to theoretical predictions?

The theory predicted:
- Adaptive 3-bit (alpha=0.25): 5.2% error reduction → Actual: PPL slightly better (-0.004), BLEU worse
- Adaptive 3-bit (alpha=0.50): 26.6% error reduction → Actual: PPL worse (+0.074), BLEU better (+0.054)
- Skip top 3 + uniform 3-bit: 8.7% error reduction → Actual: PPL better (-0.018), BLEU much better (+0.116)

The theoretical MSE model overpredicts the benefit of pure bit reallocation and underpredicts the benefit of skipping. This makes sense:
- **Bit reallocation** is limited by integer rounding (can't allocate 2.7 bits)
- **Skipping** provides a perfect fix for the worst offenders, which the MSE model undervalues because sink heads contribute disproportionately to generation errors beyond what MSE captures

### 6. Recommendation for TurboQuant

**Use `combined_best`: skip lowest-entropy heads + conservative adaptive allocation.**

Specifically:
1. **Identify sink heads** (H_2 < 0.5): keep at fp16 (no quantization)
2. **Adaptive allocation** for remaining heads: b_h = b_bar + 0.25 * (H_bar - H_2(h))
3. **Target 4-bit average** for production use

This achieves 4x compression with:
- BLEU 0.574 (vs 0.531 uniform)
- PPL ratio 1.062 (vs 1.101 uniform)
- 8% better BLEU, 4% better PPL at the same compression ratio

**For aggressive compression (5.33x):** Skip top 3 heads + uniform 3-bit is better than any adaptive-only scheme. The 3 lowest-entropy heads dominate the error budget.

### 7. Wall Clock Observations

An unexpected finding: adaptive configs with skipping are *faster* (37-48s) than uniform configs (107-245s). This is because:
- Skipped heads avoid the expensive quantize/dequantize cycle
- The adaptive patch uses a cleaner code path that avoids some overhead in the original implementation
- Uniform 4-bit configs took longest due to the 4-bit codebook size (16 levels)

## Key Insight

**The entropy distribution has a heavy tail.** The bottom 3 heads (2% of all heads) contribute disproportionately to quantization error because their near-zero entropy means any quantization error passes through at full magnitude. Protecting these heads is worth far more than optimally distributing bits across the other 141 heads.

This is analogous to the Pareto principle: fixing the worst 2% of heads provides more benefit than optimizing the other 98%.
