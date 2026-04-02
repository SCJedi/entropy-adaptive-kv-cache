# Entropy-Adaptive TurboQuant: Theory and Derivations

## Phase 1: Per-Head Bit Allocation and Quantization Skipping

---

## 1. Per-Head Bit Allocation — Rigorous Derivation

### 1.1 Setup

Consider a transformer with H attention heads. Each head h has an attention entropy H_2(h) measured in bits, capturing how diffuse or concentrated its attention pattern is. When we quantize the KV cache for head h at b_h bits per element, the output error for that head is:

```
E[||epsilon_h||^2] = sigma_q^2(b_h) * d * 2^(-H_2(h))
```

The `2^(-H_2(h))` factor arises because low-entropy (concentrated) heads pass quantization error through with higher magnitude — the error on the few attended tokens is weighted heavily. High-entropy (diffuse) heads average out quantization error across many tokens.

The Lloyd-Max MSE at b bits for a Gaussian source with variance sigma^2 follows the rate-distortion bound:

```
sigma_q^2(b) ≈ c * sigma^2 * 2^(-2b)
```

where c is a constant depending on the quantizer (for Lloyd-Max optimal quantization, c ≈ (pi*sqrt(3)/2) * 2^(-2b) but the 2^(-2b) scaling dominates).

### 1.2 Optimization Problem

Given a total bit budget B_total = H * b_bar (where b_bar is the target average bits), we want:

```
minimize   sum_h  d * c * sigma^2 * 2^(-2*b_h) * 2^(-H_2(h))
subject to sum_h b_h = B_total = H * b_bar
           b_h >= b_min, b_h <= b_max  (practical bounds)
```

### 1.3 Lagrangian Solution

Form the Lagrangian:

```
L = sum_h  d*c*sigma^2 * 2^(-2*b_h) * 2^(-H_2(h)) + lambda * (sum_h b_h - B_total)
```

Taking the derivative with respect to b_h and setting to zero:

```
dL/db_h = d*c*sigma^2 * (-2*ln(2)) * 2^(-2*b_h) * 2^(-H_2(h)) + lambda = 0
```

Therefore:

```
2^(-2*b_h) * 2^(-H_2(h)) = lambda / (2*ln(2)*d*c*sigma^2) = K  (constant for all h)
```

Taking log_2 of both sides:

```
-2*b_h - H_2(h) = log_2(K)
b_h = -(H_2(h) + log_2(K)) / 2
```

Summing over all H heads and using the constraint sum_h b_h = H * b_bar:

```
H * b_bar = -(1/2) * sum_h H_2(h) - (H/2) * log_2(K)
```

Solving for log_2(K):

```
log_2(K) = -2*b_bar - H_bar_2
```

where H_bar_2 = (1/H) * sum_h H_2(h) is the mean entropy.

Substituting back:

```
b_h = -(H_2(h) + (-2*b_bar - H_bar_2)) / 2
b_h = b_bar + (H_bar_2 - H_2(h)) / 2
```

**Result:**
```
b_h* = b_bar + (H_bar_2 - H_2(h)) / 2
```

This has an intuitive interpretation:
- Heads with entropy BELOW the mean (more concentrated) get MORE bits (they're more sensitive to quantization error)
- Heads with entropy ABOVE the mean (more diffuse) get FEWER bits (errors average out)

### 1.4 Practical Scaling

The theoretical formula gives a scaling factor of 1/2 (0.5 bits of allocation per bit of entropy difference). In practice, we introduce a tunable scaling parameter alpha:

```
b_h = b_bar + alpha * (H_bar_2 - H_2(h))
```

We test two values:
- **Conservative**: alpha = 0.25 (half the theoretical optimum)
- **Aggressive**: alpha = 0.50 (the theoretical optimum)

### 1.5 Integer Rounding and Budget Constraint

Since TurboQuant only supports integer bit widths in {2, 3, 4, 5}:

1. Compute continuous b_h from the formula
2. Clamp to [2, 5]
3. Round to nearest integer
4. Check if sum_h round(b_h) == B_total
5. If over budget: find heads with smallest |b_h - floor(b_h)| and round down
6. If under budget: find heads with smallest |b_h - ceil(b_h)| and round up

In practice, for GPT-2 with 144 heads, rounding errors tend to average out.

---

## 2. Per-Head Quantization Skipping — Theory

### 2.1 Motivation

For a head with very low entropy (H_2 << 1), the attention is concentrated on 1-2 tokens. Quantization error on those tokens passes through with nearly full magnitude. The output error for such a head is:

```
E[||epsilon_h||^2] ≈ c * sigma^2 * 2^(-2*b) * d * 2^(-H_2(h))
```

When H_2(h) -> 0, the error term 2^(-H_2(h)) -> 1, meaning this head contributes maximal error per quantization level.

### 2.2 Skip Decision

Skipping quantization for head h means:
- **Cost**: (16 - b_bar) extra bits per element (keeping fp16 instead of b_bar-bit)
- **Benefit**: eliminates quantization error for this head entirely

The benefit is proportional to:
```
delta_error_h = c * sigma^2 * 2^(-2*b_bar) * d * 2^(-H_2(h))
```

We should skip the heads with the largest error contributions, subject to a budget constraint.

### 2.3 Threshold Derivation

A head should be skipped when its error contribution exceeds the average:

```
2^(-H_2(h)) > (1/H) * sum_j 2^(-H_2(j))
```

For a rough threshold, if we assume most heads have entropy near H_bar and a few have very low entropy:

```
2^(-H_2(h)) >> 2^(-H_bar)
=> H_2(h) << H_bar
```

The naive threshold H_2 < log_2(H) (= 3.58 for 12 heads) would skip too many heads. Instead, we use a **budget-constrained approach**:

1. Rank all heads by error contribution: 2^(-H_2(h)) (descending, i.e., lowest H_2 first)
2. Skip heads greedily until the skipped fraction exceeds max_skip_fraction (default 15%)
3. This naturally selects the heads where skipping provides the most benefit

### 2.4 Effective Compression with Skipping

If K heads are skipped out of H total:
```
avg_bits_effective = (K * 16 + (H - K) * b_bar) / H
compression_ratio = 16 / avg_bits_effective
```

For K=3 out of 144 at b_bar=3: avg_bits = 3.27, compression = 4.89x (vs 5.33x uniform 3-bit).

---

## 3. Empirical Entropy Distributions

### 3.1 GPT-2 Small (12 layers x 12 heads = 144 heads)

| Statistic | Value |
|-----------|-------|
| Mean H_2 | 2.7767 |
| Std H_2 | 1.3030 |
| Min H_2 | 0.0265 (L4_H11) |
| Max H_2 | 5.9478 (L0_H11) |
| Median H_2 | 2.4984 |
| Range ratio | 224x (2^max / 2^min) |

**Key observation**: GPT-2 has extremely wide entropy distribution (std/mean = 0.47). This means per-head allocation has large potential benefit.

**Lowest 10 entropy heads (skip candidates):**

| Head | H_2 (bits) | Error weight 2^(-H_2) |
|------|-----------|----------------------|
| L4_H11 | 0.027 | 0.982 |
| L7_H2 | 0.336 | 0.792 |
| L5_H1 | 0.394 | 0.762 |
| L0_H3 | 0.729 | 0.604 |
| L6_H9 | 0.769 | 0.587 |
| L0_H1 | 0.882 | 0.543 |
| L7_H10 | 0.926 | 0.527 |
| L6_H1 | 1.068 | 0.477 |
| L5_H6 | 1.140 | 0.454 |
| L8_H1 | 1.155 | 0.450 |

These heads concentrate >50% of attention on 1-2 tokens. L4_H11 (H_2=0.027) is essentially a "sink" head.

### 3.2 Per-Head Bit Allocation Results

**At average 3-bit target:**

| Config | Scaling | Bit Distribution (2/3/4/5) | Effective Avg |
|--------|---------|---------------------------|---------------|
| Conservative | 0.25 | 18/121/5/0 | 2.91 |
| Aggressive | 0.50 | 26/86/32/0 | 3.04 |

**At average 4-bit target:**

| Config | Scaling | Bit Distribution (2/3/4/5) | Effective Avg |
|--------|---------|---------------------------|---------------|
| Conservative | 0.25 | 0/18/121/5 | 3.91 |
| Aggressive | 0.50 | 4/22/86/32 | 4.01 |

### 3.3 Predicted Error Reduction (Theoretical)

Using the MSE model E[error_h] proportional to 2^(-2*b_h) * 2^(-H_2(h)):

| Configuration | vs Uniform 3-bit |
|---------------|-----------------|
| Adaptive 3-bit (alpha=0.25) | -5.2% error |
| Adaptive 3-bit (alpha=0.50) | -26.6% error |
| Skip top 3 + uniform 3-bit | -8.7% error |
| Skip top 3 + adaptive 3-bit (0.25) | -7.3% error |

**Note**: The aggressive scaling (0.50) predicts much larger gains because it more aggressively shifts bits to the high-error low-entropy heads. However, real-world gains may be smaller because:
1. The Gaussian rate-distortion model is approximate
2. Rounding to integers limits granularity
3. Head interactions (cross-head attention patterns) are not captured

### 3.4 Qwen3.5-4B (8 full-attention layers x 16 heads = 128 heads)

| Statistic | Value |
|-----------|-------|
| Mean H_2 | 3.2263 |
| Std H_2 | 0.6020 |
| Min H_2 | 0.3142 (L31_H9) |
| Max H_2 | 4.1148 (L3_H5) |
| Median H_2 | 3.3634 |

Qwen has a tighter entropy distribution (CV=0.19 vs GPT-2's 0.47), suggesting per-head allocation will provide less benefit. However, L31_H9 and L31_H12 are strong skip candidates with H_2 < 1.0.

---

## 4. Combined Strategy: Skip + Adaptive

The recommended combined approach:

1. **Identify skip heads**: Select K heads with lowest H_2 where K <= max_skip_fraction * H
2. **Adjust budget**: Remaining (H-K) heads share the budget minus the skip overhead
3. **Allocate bits**: Apply the formula b_h = b_bar_adj + alpha * (H_bar_adj - H_2(h)) to remaining heads
4. **Budget correction**: b_bar_adj accounts for the extra bits consumed by skipped heads

For 3 skipped heads at 3-bit target:
```
B_total = 144 * 3 = 432 bits
Skip cost = 3 * 16 = 48 bits
Remaining budget = 432 - 48 = 384 bits
b_bar_adj = 384 / 141 = 2.72 bits (for remaining heads)
```

This makes remaining heads work slightly harder (2.72 avg instead of 3.0) to preserve the overall compression ratio.

---

## 5. Experiment Design

We test 8 configurations on GPT-2:

1. **uniform_3bit**: Baseline uniform 3-bit quantization
2. **uniform_4bit**: Baseline uniform 4-bit quantization
3. **adaptive_3bit_conservative**: Per-head bits, avg 3, alpha=0.25
4. **adaptive_3bit_aggressive**: Per-head bits, avg 3, alpha=0.50
5. **adaptive_4bit_conservative**: Per-head bits, avg 4, alpha=0.25
6. **skip_top3_uniform_3bit**: Skip 3 lowest-entropy heads, rest at 3-bit
7. **skip_top3_adaptive_3bit**: Skip 3 + adaptive allocation for rest
8. **combined_best**: Skip top 3 + adaptive 4-bit conservative for rest

Metrics: BLEU, ROUGE-L, token match vs baseline generation, perplexity ratio, effective compression ratio.
