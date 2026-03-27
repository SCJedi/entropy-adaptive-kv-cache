# Combined Compression Theory: Entropy-Adaptive Eviction + TurboQuant Vector Quantization

**Date:** 2026-03-27
**Status:** Theoretical analysis guiding experiment design
**Prerequisite reading:** KV_CACHE_FINDINGS.md, KV_CACHE_PAPER.md

---

## 1. Multiplicative Compression Bounds

### 1.1 Setup

Let the full KV cache for a single head store $n$ vectors of dimension $d$ at $b_0 = 16$ bits per element. The uncompressed memory is:

$$M_0 = n \cdot d \cdot b_0$$

**Token eviction** at ratio $R_e$ keeps $n / R_e$ tokens (each still at full precision).
**Vector quantization** at ratio $R_q$ keeps all tokens but reduces each vector from $b_0$ to $b_0 / R_q$ bits.

Applied independently:
- Eviction only: $M_e = (n / R_e) \cdot d \cdot b_0 = M_0 / R_e$
- Quantization only: $M_q = n \cdot d \cdot (b_0 / R_q) = M_0 / R_q$

### 1.2 Combined Ratio: When Is It Multiplicative?

Applying eviction first, then quantizing the survivors:

$$M_{combined} = \frac{n}{R_e} \cdot d \cdot \frac{b_0}{R_q} = \frac{M_0}{R_e \cdot R_q}$$

**The combined compression ratio is exactly $R_e \times R_q$ in memory.** This is an arithmetic identity -- it holds unconditionally because the two techniques operate on orthogonal axes (token count vs. bits per vector). There is no "interaction term" in the memory equation.

However, the *quality* interaction is nontrivial. Let the quality degradation from each technique be:

$$\Delta Q_{combined} = \Delta Q_e + \Delta Q_q + \Delta Q_{interaction}$$

The interaction term $\Delta Q_{interaction}$ can be positive (synergistic damage) or negative (mutual mitigation). We analyze this below.

### 1.3 The Quality Interaction Term

Define quality via KL divergence from uncompressed outputs: $D_{KL}(P_{full} \| P_{compressed})$.

**Claim:** The interaction term is generally *positive* (synergistic damage) but small when both techniques are mild.

**Argument:** Let $A$ be the full attention matrix (post-softmax), $V$ the full value matrix. The output is $O = AV$.

- Eviction replaces $A$ with $\tilde{A}$ (masked + renormalized), keeping $V$ intact: $O_e = \tilde{A}V$
- Quantization replaces $V$ with $\hat{V}$ (quantized), keeping $A$ intact: $O_q = A\hat{V}$
- Combined: $O_{eq} = \tilde{A}\hat{V}$

The total error is:

$$O_{eq} - O = \tilde{A}\hat{V} - AV = (\tilde{A} - A)\hat{V} + A(\hat{V} - V) + (\tilde{A} - A)(\hat{V} - V) - (\tilde{A} - A)V + (\tilde{A} - A)\hat{V}$$

Simplifying directly:

$$O_{eq} - O = \underbrace{(\tilde{A} - A)V}_{\text{eviction error}} + \underbrace{A(\hat{V} - V)}_{\text{quantization error}} + \underbrace{(\tilde{A} - A)(\hat{V} - V)}_{\text{interaction}}$$

The interaction term $(\tilde{A} - A)(\hat{V} - V)$ is the product of the eviction perturbation to attention and the quantization perturbation to values. Its Frobenius norm is bounded by:

$$\|(\tilde{A} - A)(\hat{V} - V)\|_F \leq \|\tilde{A} - A\|_F \cdot \|\hat{V} - V\|_F$$

This is the product of the individual error norms -- small when both are small (sub-multiplicative). At moderate compression (2x eviction, 3-bit quantization), both perturbations are small, so the interaction is second-order.

**Key insight:** The interaction term is $O(\epsilon_e \cdot \epsilon_q)$ where $\epsilon_e, \epsilon_q$ are the individual error magnitudes. When both are small (say 5% each), the interaction is ~0.25%, negligible. When both are large (say 30% each), the interaction is ~9%, non-negligible.

### 1.4 Per-Head Interaction Structure

Because entropy-adaptive eviction assigns different budgets to different heads, the interaction term varies by head:

- **Low-entropy (sink) heads:** Aggressive eviction ($R_e^{(h)}$ large), few survivors, quantization error is applied to fewer vectors. The interaction term is large per-vector but summed over few vectors.
- **High-entropy (diffuse) heads:** Conservative eviction ($R_e^{(h)}$ small), many survivors, quantization error is distributed across many vectors. The interaction term is small per-vector, summed over many vectors.

This suggests the interaction is roughly constant across heads, which is favorable -- there are no "catastrophic interaction" heads.

---

## 2. Entropy-Informed Bit Allocation

### 2.1 The Central Question

Does a high-entropy (diffuse) attention head tolerate MORE or LESS quantization noise in its KV vectors?

### 2.2 Derivation

Consider a single query position attending to $n$ keys. The attention output for head $h$ is:

$$o_h = \sum_{i=1}^{n} a_i^{(h)} v_i$$

where $a_i^{(h)}$ are the attention weights (summing to 1). When values are quantized with error $\delta_i = \hat{v}_i - v_i$, the output error is:

$$\epsilon_h = \sum_{i=1}^{n} a_i^{(h)} \delta_i$$

Assuming quantization errors are i.i.d. with $\mathbb{E}[\delta_i] = 0$ and $\text{Var}[\delta_i] = \sigma_q^2 I$, the expected squared error in the output is:

$$\mathbb{E}[\|\epsilon_h\|^2] = \sigma_q^2 \cdot d \cdot \sum_{i=1}^{n} (a_i^{(h)})^2$$

The quantity $\sum_i (a_i^{(h)})^2$ is the *collision probability* of the attention distribution, which is related to Renyi entropy of order 2:

$$H_2(h) = -\log_2 \sum_i (a_i^{(h)})^2$$

So: $\sum_i (a_i)^2 = 2^{-H_2(h)}$.

Therefore:

$$\boxed{\mathbb{E}[\|\epsilon_h\|^2] = \sigma_q^2 \cdot d \cdot 2^{-H_2(h)}}$$

### 2.3 Interpretation

**High-entropy heads are MORE tolerant of quantization noise.** A diffuse attention distribution averages over many value vectors, so per-vector quantization errors cancel out (law of large numbers effect). A focused head puts all weight on one or two vectors, so quantization error passes through with full magnitude.

Quantitatively, for GPT-2:
- A sink head with $H_2 \approx 0$ has output error $\approx \sigma_q^2 \cdot d$ (full exposure)
- A diffuse head with $H_2 \approx 5$ has output error $\approx \sigma_q^2 \cdot d / 32$ (32x attenuation)

**This is the opposite of what a naive intuition might suggest.** One might think "diffuse heads spread information across many tokens, so each token matters, so quantization of each matters." But the math says the opposite: spreading attention across many tokens provides a natural averaging that suppresses per-vector noise.

### 2.4 Optimal Bit Allocation Across Heads

Given a total bit budget $B_{total}$ across $H$ heads, we want to minimize total output error. If head $h$ is allocated $b_h$ bits per element, and the Lloyd-Max quantization error at $b$ bits satisfies $\sigma_q^2(b) \approx c \cdot 2^{-2b}$ (standard rate-distortion bound for Gaussian sources), then:

$$\text{Total error} = \sum_h d \cdot c \cdot 2^{-2b_h} \cdot 2^{-H_2(h)}$$

Minimizing subject to $\sum_h b_h = B_{total}$ via Lagrange multipliers:

$$\frac{\partial}{\partial b_h}\left[ c \cdot d \cdot 2^{-2b_h - H_2(h)} + \lambda b_h \right] = 0$$

$$-2 \ln 2 \cdot c \cdot d \cdot 2^{-2b_h - H_2(h)} + \lambda = 0$$

$$2b_h + H_2(h) = \text{const} \quad \Rightarrow \quad b_h = \bar{b} - \frac{H_2(h)}{2} + \frac{\bar{H}_2}{2}$$

where $\bar{b} = B_{total}/H$ and $\bar{H}_2$ is the mean Renyi entropy.

$$\boxed{b_h^* = \bar{b} + \frac{\bar{H}_2 - H_2(h)}{2}}$$

**Translation:** Allocate MORE bits to low-entropy (focused) heads and FEWER bits to high-entropy (diffuse) heads. Each bit of Renyi entropy difference corresponds to a half-bit reallocation.

For GPT-2 with $H_2$ range of roughly 0-5 bits:
- Sink heads ($H_2 \approx 0$): allocate $\bar{b} + 1.4$ bits above average
- Diffuse heads ($H_2 \approx 5$): allocate $\bar{b} - 1.1$ bits below average

If the average is 3 bits: sink heads get ~4.4 bits, diffuse heads get ~1.9 bits. This is a significant reallocation.

### 2.5 The Counter-Intuitive Synergy

Entropy-adaptive eviction gives diffuse heads MORE tokens (because they need broad context). The bit allocation analysis says diffuse heads need FEWER bits per token (because averaging suppresses noise). These effects push in opposite directions on memory:

- Diffuse head: many tokens x few bits per token
- Focused head: few tokens x many bits per token

This partial cancellation means the combined approach achieves **better quality per bit than either alone**, because it exploits the complementary structure of the error sources.

---

## 3. Quality Interaction Model: Eviction Before Quantization

### 3.1 How Eviction Changes the Value Distribution

When we evict tokens from the KV cache, the *statistical distribution* of the surviving value vectors changes. This matters because Lloyd-Max quantization is optimal for a specific input distribution.

**Token selection effect:** Entropy-adaptive eviction keeps tokens with the highest attention weight for each head. These are not random samples from the value distribution -- they are *informationally selected* samples.

Consider what token eviction does, stratified by head type:

**Sink heads (49.3% of GPT-2 heads):** Keep primarily position 0 and a handful of high-attention tokens. The surviving distribution is very concentrated -- essentially one dominant vector plus a few outliers. This is a *low-variance, potentially multi-modal* distribution.

**Diffuse heads (16.7%):** Keep most tokens (high entropy = large budget). The surviving distribution closely matches the original. Minimal distortion to the distribution.

**Positional/selective heads:** Keep tokens from specific positions (recent or topk). The surviving distribution may have different statistics from the full sequence -- e.g., recent tokens may have systematically different value vectors from early tokens.

### 3.2 Impact on Lloyd-Max Quantization

Lloyd-Max scalar quantization is optimal for the distribution it was trained on. TurboQuant applies a random rotation before Lloyd-Max quantization, which makes the marginal distribution of each rotated coordinate approximately Gaussian (by the central limit theorem, since rotation mixes many coordinates).

**Key question:** Does eviction change the post-rotation marginal distribution enough to degrade Lloyd-Max optimality?

After random rotation $R$, each coordinate of $Rv_i$ is a linear combination of all coordinates of $v_i$. The marginal distribution depends on the mean and covariance of the value vectors.

**Eviction effects on the rotated distribution:**

1. **Mean shift:** Evicted tokens may have different means from survivors. If eviction preferentially keeps high-attention tokens, and these correlate with specific value patterns, the post-eviction mean shifts. The rotation preserves this shift in the rotated coordinates, potentially moving the distribution relative to the Lloyd-Max levels. **Effect: small bias, increases with eviction aggressiveness.**

2. **Variance change:** Two competing effects:
   - If eviction removes low-importance (typically low-magnitude) tokens, the surviving set may have HIGHER variance. More spread = worse quantization at fixed bit rate.
   - If eviction clusters tokens (e.g., only recent tokens), the surviving set may have LOWER variance. Less spread = better quantization.

   Empirically, for attention-weighted eviction (keeping high-attention tokens), the effect depends on whether high-attention tokens are more or less varied than the full set. For sink heads, survivors are highly clustered (dominated by position 0). For diffuse heads, survivors are representative.

3. **Non-Gaussianity:** The random rotation's CLT effect depends on having many independent coordinates mixed. With fewer surviving tokens, the effective dimensionality of the value matrix decreases, potentially making the post-rotation distribution less Gaussian. However, the rotation is applied per-vector (mixing coordinates of a single vector), not across tokens, so the number of surviving tokens doesn't affect the CLT argument.

**Conclusion:** The random rotation in TurboQuant largely insulates Lloyd-Max from the distributional changes caused by eviction. The primary risk is a variance change, which can be addressed by recalibrating the Lloyd-Max levels on the post-eviction distribution (a cheap operation).

### 3.3 QJL Residual Correction After Eviction

TurboQuant's second stage uses Quantized Johnson-Lindenstrauss (QJL) projections to correct residual errors. The QJL projection preserves inner products with probabilistic guarantees:

$$|\langle q, \hat{k}_i \rangle - \langle q, k_i \rangle| \leq \epsilon \|q\| \|k_i\|$$

with high probability, where $\hat{k}_i$ is the quantized key and $\epsilon$ depends on the projection dimension.

After eviction, the QJL correction is applied only to surviving tokens. This is strictly beneficial: fewer tokens means the QJL projection dimension can be allocated more generously per token within the same memory budget, OR the same per-token accuracy can be achieved with less memory.

$$\text{QJL memory} \propto n_{survivors} \cdot m_{projection}$$

If we keep the total QJL memory fixed, eviction allows increasing $m_{projection}$ by factor $R_e$, reducing $\epsilon$ by $\sqrt{R_e}$.

### 3.4 Order of Operations

**Evict first, then quantize** is strictly preferable to quantize first, then evict:

1. **Eviction decisions use attention weights**, which depend on inner products $\langle q, k \rangle$. If keys are quantized first, the inner products are approximate, leading to suboptimal eviction decisions.

2. **Quantizing fewer vectors is cheaper.** At $n/R_e$ survivors instead of $n$, both the rotation and Lloyd-Max steps run $R_e$ times faster.

3. **Lloyd-Max calibration** on the post-eviction distribution is more accurate (matches the actual distribution being quantized).

---

## 4. Theoretical Pareto Frontier

### 4.1 Problem Formulation

Given a total memory budget $B$ (in bits), sequence length $n$, dimension $d$, and $H$ attention heads, find the allocation $(R_e^{(h)}, b^{(h)})$ for each head $h$ that minimizes total output error:

$$\min_{R_e^{(h)}, b^{(h)}} \sum_h \mathcal{L}_h(R_e^{(h)}, b^{(h)})$$

subject to:

$$\sum_h \frac{n}{R_e^{(h)}} \cdot d \cdot b^{(h)} \leq B$$

where $\mathcal{L}_h$ is the output error for head $h$.

### 4.2 Error Model Per Head

From Sections 1-2, the error for head $h$ has three components:

$$\mathcal{L}_h = \underbrace{\mathcal{L}_h^{(e)}(R_e^{(h)})}_{\text{eviction}} + \underbrace{d \cdot c \cdot 2^{-2b^{(h)}} \cdot 2^{-H_2(h)}}_{\text{quantization}} + \underbrace{O(\epsilon_e \cdot \epsilon_q)}_{\text{interaction}}$$

The eviction error depends on head type. From the empirical Pareto data (entropy-adaptive, KL divergence):

| Keep ratio $r$ | Compression $R_e$ | KL divergence |
|---|---|---|
| 1.00 | 1.0x | 0.002 |
| 0.50 | 2.0x | 0.026 |
| 0.30 | 3.3x | 0.081 |
| 0.20 | 5.0x | 0.150 |
| 0.10 | 10x | 0.589 |

This is well-approximated by a power law:

$$\mathcal{L}^{(e)}(R_e) \approx \alpha \cdot R_e^{\beta}$$

Fitting to the data: $\alpha \approx 0.005$, $\beta \approx 1.6$. (Verified: $0.005 \times 2^{1.6} = 0.015$ vs actual 0.026; $0.005 \times 10^{1.6} = 0.20$ vs actual 0.59. The fit is rough but captures the order of magnitude.)

A better fit uses the form $\mathcal{L}^{(e)}(R_e) \approx \alpha (R_e - 1)^{\beta}$:
- $\alpha \approx 0.026$, $\beta \approx 1.4$ gives: at $R_e=2$: $0.026 \times 1.0 = 0.026$ (exact); at $R_e=10$: $0.026 \times 9^{1.4} = 0.026 \times 17.4 = 0.45$ (vs 0.59, reasonable).

### 4.3 Optimal Split: Closed-Form Approximation

Ignoring per-head variation and the interaction term, the total error for a single head is:

$$\mathcal{L}(R_e, b) = \alpha (R_e - 1)^{\beta} + \gamma \cdot 2^{-2b}$$

where $\gamma = d \cdot c \cdot 2^{-H_2}$ absorbs head-specific constants.

The memory per head is $M = (n/R_e) \cdot d \cdot b$. Given budget $B_h$:

$$b = \frac{B_h \cdot R_e}{n \cdot d}$$

Substituting:

$$\mathcal{L}(R_e) = \alpha (R_e - 1)^{\beta} + \gamma \cdot 2^{-2 B_h R_e / (nd)}$$

Taking the derivative and setting to zero:

$$\alpha \beta (R_e - 1)^{\beta - 1} = \gamma \cdot \frac{2B_h \ln 2}{nd} \cdot 2^{-2 B_h R_e / (nd)}$$

This has no closed-form solution in general, but we can characterize the regimes:

**Regime 1: Eviction-cheap, quantization-expensive** ($\beta < 2$, which is our case with $\beta \approx 1.4$).
Eviction error grows sub-quadratically while quantization error decreases exponentially with freed bits. This means **moderate eviction + moderate quantization is optimal** -- neither extreme dominates.

**Regime 2: Budget is large** ($B_h / (nd) \gg 1$, meaning many bits available).
The exponential term dominates, and the optimum has $R_e$ close to 1 (minimal eviction, use bits for precision). Eviction is unnecessary when you have plenty of bits.

**Regime 3: Budget is tight** ($B_h / (nd) \ll 16$, aggressive compression needed).
Here eviction provides more bang-per-bit because $\beta < 2$ means the eviction error curve is concave, so the first few 'x' of eviction are cheap in quality. Meanwhile, going from 3-bit to 2-bit quantization costs much more quality than going from 16-bit to 3-bit.

### 4.4 Numerical Optimization for GPT-2

Using GPT-2 parameters ($n=128$, $d=64$, $H=144$ heads, $b_0=16$ bits):

Full cache per head: $128 \times 64 \times 16 = 131,072$ bits.
Total full cache: $144 \times 131,072 \approx 18.9$ Mbit $\approx 2.36$ MB.

For a target total compression of 10x (budget = 0.236 MB):

We need to distribute $R_e \times R_q = 10$ across the two techniques. Candidate splits:

| $R_e$ (eviction) | $R_q$ (quantization) | Bits/element | Eviction KL | Est. quant error | Notes |
|---|---|---|---|---|---|
| 1x | 5.3x (3-bit) | 3.0 | 0.000 | moderate | Pure quantization |
| 2x | 5.0x (3.2-bit) | 3.2 | 0.026 | moderate | Mild eviction |
| 2x | 5.3x (3-bit) | 3.0 | 0.026 | moderate | Sweet spot candidate |
| 3.3x | 3.0x (5.3-bit) | 5.3 | 0.081 | low | More eviction, higher precision |
| 5x | 2.0x (8-bit) | 8.0 | 0.150 | very low | Heavy eviction, mild quantization |
| 10x | 1x (16-bit) | 16.0 | 0.589 | 0 | Pure eviction |

**Analysis:** The sweet spot is where marginal quality loss from more eviction equals marginal quality loss from fewer bits. Given that:

- Eviction from 2x to 3.3x costs KL +0.055 (from 0.026 to 0.081)
- Quantization from 5-bit to 3-bit costs roughly comparable quality (TurboQuant reports cosine similarity 0.9945 at 3-bit, implying small but nonexistent KL data)
- The averaging effect (Section 2) means quantization damage is further attenuated for diffuse heads

**Predicted optimum for 10x total:** $R_e \approx 2\text{--}3x$ eviction + $R_q \approx 3\text{--}5x$ quantization (3-5 bits per element).

### 4.5 The Pareto Frontier Shape

The combined Pareto frontier is the lower envelope of all $(R_e, R_q)$ pairs achieving total compression $R = R_e \times R_q$. Because the two error sources are approximately additive (Section 1.3) and the eviction error is convex in $R_e$ while quantization error is convex in $R_q$, the combined frontier is also convex.

At each total compression $R$, the optimal split minimizes:

$$\alpha(R_e - 1)^{1.4} + \gamma \cdot 2^{-2 \cdot 16/R_q}$$

subject to $R_e \cdot R_q = R$.

Substituting $R_q = R / R_e$:

$$\min_{R_e \in [1, R]} \alpha(R_e - 1)^{1.4} + \gamma \cdot 2^{-32 R_e / R}$$

The boundary cases: $R_e = 1$ (pure quantization) vs $R_e = R$ (pure eviction). The interior optimum exists when neither boundary is minimal, which occurs at moderate total compression (4x-20x range).

---

## 5. Predicted Sweet Spots and Experiment Design

### 5.1 Configurations to Test

Based on the theory, the following grid explores the interesting region of the combined Pareto frontier:

**Tier 1: Primary candidates (highest priority)**

| Config | Eviction $R_e$ | Quant bits | Quant $R_q$ | Total $R$ | Rationale |
|---|---|---|---|---|---|
| **A1** | 2x | 4-bit | 4x | **8x** | Conservative both; baseline quality |
| **A2** | 2x | 3-bit | 5.3x | **10.6x** | Sweet spot prediction from Section 4.4 |
| **A3** | 3.3x | 3-bit | 5.3x | **17.5x** | Push eviction further at 3-bit |
| **A4** | 3.3x | 4-bit | 4x | **13.2x** | More eviction, safer quantization |

**Tier 2: Boundary exploration**

| Config | Eviction $R_e$ | Quant bits | Quant $R_q$ | Total $R$ | Rationale |
|---|---|---|---|---|---|
| **B1** | 1x | 3-bit | 5.3x | **5.3x** | Pure TurboQuant, no eviction |
| **B2** | 1x | 4-bit | 4x | **4x** | Pure TurboQuant at 4-bit |
| **B3** | 5x | 4-bit | 4x | **20x** | Heavy eviction + moderate quant |
| **B4** | 5x | 3-bit | 5.3x | **26.5x** | Extreme combined |
| **B5** | 2x | 2-bit | 8x | **16x** | Minimal eviction, extreme quant |

**Tier 3: Per-head adaptive bit allocation**

| Config | Eviction | Bit allocation | Total $R$ | Rationale |
|---|---|---|---|---|
| **C1** | 2x entropy-adaptive | Per-head: 2-5 bits by $H_2$ (mean 3) | ~10x | Full theory from Section 2.4 |
| **C2** | 3.3x entropy-adaptive | Per-head: 2-5 bits by $H_2$ (mean 3) | ~17x | Aggressive eviction + adaptive bits |
| **C3** | 2x entropy-adaptive | Per-head: 2-4 bits by $H_2$ (mean 2.5) | ~13x | Tighter bit budget |

### 5.2 Metrics to Measure

For each configuration, measure:

1. **Exact match rate** vs full-precision full-cache baseline (primary metric)
2. **Top-5 match rate** (softer metric, more sensitive at high compression)
3. **KL divergence** from baseline output distribution (continuous quality measure)
4. **Attention fidelity** as cosine similarity: $\cos(\tilde{A}\hat{V}, AV)$ per head (decomposition metric)
5. **Per-head error contribution**: which heads contribute most to total error (guides further optimization)
6. **Interaction magnitude**: measure $\|\Delta Q_{combined} - \Delta Q_e - \Delta Q_q\|$ directly

### 5.3 Specific Predictions to Validate

1. **Multiplicative memory holds exactly.** Config A2 (2x eviction + 3-bit) should use $\leq 1/(2 \times 5.3) = 9.4\%$ of full cache memory. Verify by counting bits.

2. **Quality interaction is small at moderate compression.** For configs A1-A2, the measured quality loss should satisfy:
   $$\text{KL}_{combined} \leq 1.2 \times (\text{KL}_{eviction\text{-}only} + \text{KL}_{quant\text{-}only})$$
   i.e., the interaction adds at most 20% to the sum of individual degradations.

3. **Per-head adaptive bits beat uniform bits.** Config C1 should outperform A2 at the same total memory, because Section 2.4 shows the optimal bit allocation is non-uniform.

4. **Diffuse heads tolerate quantization better.** Directly measure per-head output error $\|\epsilon_h\|^2$ and verify the $2^{-H_2(h)}$ scaling from Section 2.2. Plot $\log(\|\epsilon_h\|^2 / \sigma_q^2 d)$ vs $H_2(h)$; expect slope $\approx -1$.

5. **Eviction helps quantization.** Config A2 (2x eviction + 3-bit) should have lower KL than B1 (pure 3-bit, no eviction) despite A2 also evicting tokens. This would demonstrate that removing low-attention tokens before quantization improves the quantization quality of survivors (by concentrating the value distribution and allowing better Lloyd-Max calibration).

6. **The optimal split is interior.** For 10x total compression, the combined approach (A2: 2x+5.3x) should beat both B1 (1x+5.3x, pure quant at higher memory) and the pure eviction baseline (10x eviction, KL=0.589). The combined KL should be substantially below 0.589.

### 5.4 Expected Results

Based on the theoretical analysis:

| Config | Total $R$ | Predicted KL range | Confidence |
|---|---|---|---|
| A1 (2x+4bit) | 8x | 0.03 - 0.08 | High (both mild) |
| A2 (2x+3bit) | 10.6x | 0.05 - 0.15 | Medium (depends on TurboQuant 3-bit quality) |
| A3 (3.3x+3bit) | 17.5x | 0.15 - 0.40 | Medium |
| B3 (5x+4bit) | 20x | 0.20 - 0.50 | Medium-low |
| B4 (5x+3bit) | 26.5x | 0.40 - 1.00 | Low (pushing limits) |
| C1 (2x+adaptive) | ~10x | 0.03 - 0.10 | Medium (theory says best) |

**Comparison anchor:** Pure eviction at 10x gives KL=0.589. If config A2 (10.6x combined) achieves KL < 0.15, that is a **4x quality improvement** at the same compression. This would validate the orthogonal compression thesis.

### 5.5 Implementation Notes

1. **Eviction must happen first.** Compute full attention, evict, then quantize survivors. Never quantize before eviction decisions.

2. **Lloyd-Max calibration** should be done on post-eviction value vectors, not full-cache vectors. Use a small calibration set (same 20 sequences used for entropy profiling).

3. **Random rotation matrix** should be fixed (seeded) across all experiments for reproducibility, and shared across tokens within a head (same rotation for all value vectors in a head).

4. **Per-head bit allocation** (Tier 3 configs) requires implementing variable-rate quantization. The simplest approach: round $b_h^*$ to nearest integer in {2, 3, 4, 5} and use fixed-point Lloyd-Max for each rate.

5. **The existing experiment infrastructure** (`kv_cache_compression.py`) already has:
   - Head entropy computation (calibration pass)
   - Four eviction strategies with the entropy-adaptive as best performer
   - Baseline collection and metric computation (exact match, top-5, KL)
   - Monkey-patched attention for eviction masks

   What needs to be added:
   - TurboQuant quantization of value vectors (rotation + Lloyd-Max + QJL)
   - Combined pipeline: evict-then-quantize
   - Per-head adaptive bit allocation
   - Interaction measurement (combined vs sum-of-individual errors)

---

## 6. Summary of Key Theoretical Results

| Result | Section | Implication |
|---|---|---|
| Combined compression is exactly $R_e \times R_q$ in memory | 1.2 | No memory overhead from combining |
| Quality interaction is $O(\epsilon_e \cdot \epsilon_q)$, second-order | 1.3 | Safe to combine at moderate compression |
| Output error scales as $2^{-H_2(h)}$ with head entropy | 2.2 | High-entropy heads tolerate more quantization |
| Optimal bits: $b_h^* = \bar{b} + (\bar{H}_2 - H_2(h))/2$ | 2.4 | Give focused heads more bits, diffuse heads fewer |
| Eviction and bit-allocation push opposite on diffuse heads | 2.5 | Natural balance: many tokens x few bits |
| Random rotation insulates Lloyd-Max from eviction effects | 3.2 | TurboQuant is robust to distribution shift |
| QJL benefits from fewer survivors (higher per-token budget) | 3.3 | Eviction improves quantization residual correction |
| Optimal split for 10x: ~2-3x eviction + 3-5 bit quantization | 4.4 | Interior optimum, not boundary |
| Eviction error is sub-quadratic ($\beta \approx 1.4$) | 4.2 | Mild eviction is cheap; supports combined approach |

---

## Appendix A: Notation Reference

| Symbol | Meaning |
|---|---|
| $R_e$ | Eviction compression ratio (e.g., 2x = keep 50% of tokens) |
| $R_q$ | Quantization compression ratio (e.g., 5.3x = 16-bit to 3-bit) |
| $H_2(h)$ | Renyi entropy of order 2 for head $h$'s attention distribution |
| $b_h$ | Bits per element allocated to head $h$ |
| $\sigma_q^2$ | Mean squared quantization error per element |
| $n$ | Sequence length (number of KV tokens) |
| $d$ | Head dimension |
| $\alpha, \beta$ | Power-law fit parameters for eviction error |
| $\gamma$ | Head-specific quantization sensitivity constant |

## Appendix B: Empirical Data Used

All empirical values in this analysis are from `KV_CACHE_FINDINGS.md` (GPT-2 small, WikiText-2 validation, entropy-adaptive eviction strategy). TurboQuant performance numbers (cosine similarity 0.9945 at 3-bit) are from the technique description provided in the task specification.
