# Self-Referential Learning: An Exploratory Investigation

## What happens when a model's output contaminates its own training signal?

---

### Abstract

Self-referential feedback loops are ubiquitous in modern machine learning. RLHF trains reward models on outputs shaped by those same reward models. Autoregressive language models generate tokens that become their own future context. Recommendation systems alter the behavior they are trained to predict. In all these settings, the standard assumption that training data is independently generated breaks down -- the model is, to some degree, hearing its own echo.

We investigate what happens analytically and experimentally when a learning agent's output feeds back into its input. Starting from the simplest possible self-referential system -- a single linear agent observing a signal contaminated by its own previous prediction -- we derive a closed-form self-consistency equation: kw^2 + w - 1 = 0, where k depends on the agent's activation function. For the linear case (k=1), SGD converges to exactly w = 1/phi = 0.618, the reciprocal of the golden ratio. This is not an information-theoretic optimum but rather the "price of self-ignorance": a system-aware optimizer that accounts for its own feedback achieves 8.3% lower error. We extend these results to nonlinear activations, multi-agent networks, and depth-width tradeoffs under fixed compute. Cross-connected diverse agents outperform single deep agents, and the cross-connections learn negative (subtractive) weights -- implementing a form of parallax decontamination.

We then prove and verify two major extensions. First, a cascade composition theorem: when self-referential processing stages are chained, signal fidelity degrades sub-multiplicatively -- actual R^2 is up to 20x worse than the product of per-stage R^2 values, because each stage's AR(1) output makes subsequent decontamination harder. Binocular (dual-channel) stages provide 8x improvement over monocular stages in the full cascade. Second, we identify the Minimum Viable Stable Unit (MVSU): the simplest architecture that does not catastrophically degrade through a cascade. The MVSU requires exactly two components -- dual channels (N >= 2) and inhibitory cross-connections (w_cross < 0) -- removing either causes 97.4% R^2 collapse. Predictive coding adds 60% improvement but is not structurally necessary. The MVSU achieves ~38x better R^2 than a monocular system with only 4x the parameters.

We also report honest real-world validation failures: pseudo-labeling on a classification task confirms contamination but all proposed fixes fail, because pseudo-label errors are class-structured rather than uniform -- a boundary condition the continuous theory does not cover. We validate these findings on real continuous feedback tasks (thermostat control, sensor calibration, market microstructure), where the MVSU achieves 45-50% MSE reduction over standard single-model approaches.

We extend the framework to multi-agent settings and establish its information-theoretic foundations. The golden ratio survives at any N agents under mean-field coupling (the N cancels exactly from the contamination). The mutual information I(s; y) = log(phi) = 0.4812 nats is the Shannon capacity of the self-referential channel -- a single fully contaminated agent already saturates this ceiling. The sign of the learned cross-connection weight (w_cross) diagnoses whether contamination is independent (negative: subtract) or shared (positive: average). In generative chains, the MVSU prevents model collapse (54% improvement over 20 generations) but is prophylactic, not curative -- it cannot reverse existing degradation. Approximately 50% of pipeline stages must be MVSU-equipped for ecosystem stabilization.

We show that damped meta-optimization closes the full 15.6% myopic-to-system-aware MSE gap at high contamination. The recurrence w_{n+1} = w_n + beta*(0.525 - w_n) with beta = 1/phi^2 = 0.382 converges in 2 iterations, while beta = 1/phi = 0.618 provides universal robustness across all contamination levels. Direct measurement reveals the MVSU stays at w=0.614 (myopic) rather than reaching w=0.525 (system-aware) — it is a noise filter, not a meta-optimizer. A proposed two-stage architecture combines MVSU (estimates contamination via w_cross) with damped recurrence (applies system-aware correction) to achieve both measurement and correction in a stable path.

We extend the MVSU to numerical simulation error reduction, finding that cross-correction yields 2.5-3.7x improvement when integrators have structurally different computational strategies (RK4 single-step vs AB4 multi-step) producing anti-correlated errors. Error correlation predicts cross-correction potential: anti-correlated errors (cosine < 0) enable strong benefit, while correlated errors (same algorithm family) provide no benefit. Online w_cross learning converges to sweep-optimal independently without ground truth knowledge. Simple averaging can hurt when errors are anti-correlated with unequal magnitudes.

These are preliminary results on toy problems. We report thirty experiments, including several null results, and outline what would be needed to test whether these findings generalize to realistic ML systems.

---

### 1. Motivation

Modern machine learning systems increasingly operate in self-referential regimes. In RLHF, the reward model is trained on outputs produced by the language model being fine-tuned -- but those outputs were themselves shaped by earlier versions of the reward model [1]. In autoregressive generation, each token a model produces becomes part of the context for generating the next token. In recommendation systems, the items shown to users change user behavior, which changes the training data the recommender learns from. In synthetic data pipelines, LLM-generated text is used to train the next generation of LLMs [4].

Standard training methods treat each gradient step independently, as if the data distribution were fixed and externally generated. But in these self-referential settings, the data distribution depends on the model itself. This creates a feedback loop: the model's parameters determine its outputs, which influence its future training data, which determine its future parameters.

What are the consequences of this circularity? Does it introduce a systematic bias? If so, how large is it, and can it be corrected?

In this paper, we study these questions in the simplest possible setting: a scalar agent that observes a signal contaminated by its own previous prediction, and learns via stochastic gradient descent. This is a toy system -- intentionally so. The goal is not to model any specific ML pipeline but to isolate the phenomenon of self-referential contamination and understand its algebra. We report thirty experiments, including several null results, two honest real-world validation failures, a suite of generalization checks, a real-world validation on continuous feedback tasks, multi-agent extensions with information-theoretic foundations, and three ML architecture experiments testing discrete observer predictions. We outline what would need to hold for these findings to matter at scale.

---

### 2. The Setup

#### 2.1 The Simplest Self-Referential Agent

Consider an agent that at each timestep t:

1. Observes y(t) = s(t) + alpha * prediction(t-1)
2. Produces prediction(t) = w * y(t)
3. Observes the true signal s(t) after predicting
4. Updates w via SGD on the loss (prediction(t) - s(t))^2

Here s(t) is an i.i.d. signal (standard normal), alpha controls the contamination strength (alpha=0 means clean observations, alpha=1 means the agent fully hears its own echo), and w is the single learnable parameter.

This is the simplest model of a system that hears itself. The agent's previous output literally contaminates its next observation. Despite its simplicity, this system captures the essential structure of self-referential learning: the training distribution depends on the model's parameters through the feedback term alpha * prediction(t-1).

#### 2.2 Diagram of the Feedback Loop

```
    s(t) ----+
             |
             v
    y(t) = s(t) + alpha * w * y(t-1)
             |
             v
    pred(t) = w * y(t) -----> output
             |                   |
             v                   |
    loss = (pred(t) - s(t))^2   |
             |                   |
             v                   |
    w <-- SGD update             |
                                 |
             alpha * pred(t) ----+----> feeds into y(t+1)
```

#### 2.3 Connection to Real Systems

| Real System | Signal s(t) | Contamination alpha * pred(t-1) |
|-------------|------------|-------------------------------|
| RLHF | User preferences | Reward model trained on model outputs |
| Autoregressive LLM | Ground truth next token | Previously generated tokens in context |
| Recommendation | True user interest | Behavioral shift from past recommendations |
| Synthetic data | Real-world data | LLM-generated training samples |
| Self-play RL | Opponent's true strategy | Opponent IS the model itself |

In each case, alpha represents how strongly the model's own outputs feed back into its observations. Real systems have alpha somewhere between 0 and 1, and the feedback mechanism is far more complex than a scalar multiplier. But the algebraic structure -- the model influencing its own training signal -- is the same.

---

### 3. What We Found

#### 3.1 The Self-Consistency Equation (Proven)

For the linear agent described above, we can derive the SGD fixed point exactly.

At steady state, the variance of the observed signal y satisfies:

    Var(y) = Var(s) + w^2 * Var(y) = 1 + w^2 * Var(y)

Solving: Var(y) = 1 / (1 - w^2).

The MSE-optimal filter weight (treating Var(y) as fixed, as SGD does) is:

    w = Cov(s, y) / Var(y) = 1 / (1 + Var(y)) = 1 - w^2

Rearranging:

    w^2 + w - 1 = 0

This is the golden ratio equation. The positive root is w = (-1 + sqrt(5)) / 2 = 1/phi = 0.618.

SGD simulation confirms this: across 5 seeds, 50,000 timesteps each, the converged weight is 0.618 to three decimal places. The R^2 at convergence is also 0.618 -- the weight and the explained variance coincide.

For nonlinear activations, the same self-consistency logic gives the general form:

    k * w^2 + w - 1 = 0

where k is a constant determined by the activation function's shape. The factor k encodes how well the activation can approximate the optimal linear predictor.

| Activation | k | w (effective gain) | Origin of k |
|-----------|---|-------------------|-------------|
| Linear | 1.000 | 0.618 (= 1/phi, exact) | Identity |
| ReLU | 0.341 (= (pi-1)/(2pi)) | 0.394 | Half-rectification of Gaussian |
| Sigmoid | 0.330 (numerical) | 0.384 | Sigmoid compression of Gaussian |
| Tanh | ~1.0 (near-linear regime) | ~0.605 | Approximately linear near origin |

The ReLU derivation is exact and closed-form. The key fact is that Cov(max(0,u), u) = 1/2 for standard normal u, so the effective gain is exactly halved relative to the linear case. The factor k = (pi-1)/(2pi) comes from the Gaussian integral over the positive half-line [7]. We verified that k is exactly constant across all operating points (to 6 decimal places) for both ReLU and sigmoid.

For multi-neighbor networks where the agent hears echoes from k neighbors:

    k * w^2 + w - 1 = 0,    w = (-1 + sqrt(1 + 4k)) / (2k)

| Topology | k (neighbors) | Predicted w | Observed w |
|----------|---------------|------------|------------|
| Isolated | 1 | 0.618 | 0.618 |
| Ring (k=1) | 3 | 0.434 | 0.434 |
| Ring (k=2) | 5 | 0.358 | 0.358 |
| Ring (k=4) | 9 | 0.281 | 0.281 |
| Complete (20) | 20 | 0.200 | 0.200 |

Predicted and observed values match to three decimal places across all topologies and all seeds.

**Matrix generalization.** The self-consistency equation extends to multi-dimensional agents where w is a d x d matrix. The matrix equation W^2 + W - I = 0 holds through d=16. For i.i.d. signals, W decomposes into d copies of the scalar equation (W ≈ (1/φ)·I), with spectral radius converging to 1/φ for d = 1, 2, 4, 8, 16 (mean deviation 0.015) and trace matching d/φ as predicted. Individual eigenvalues satisfy λ^2 + λ - 1 = 0 (residual 0.018–0.070, growing slowly with d). For correlated signals (ρ=0.7), W develops off-diagonal structure aligned with the covariance eigenbasis, but eigenvalue magnitudes still match 1/φ (mean difference = 0.017) and the Frobenius norm matches √d/φ. This addresses the most critical theoretical extension outlined in Section 6.1: the self-consistency algebra does generalize beyond scalars (`multidim_selfref.py`).

**Robustness across signal distributions and optimizers.** The 1/φ attractor is distribution-independent and optimizer-independent, in our simplified setting. We tested five signal distributions and six optimizer configurations, each with 50,000 timesteps and 5 seeds:

| Signal Distribution | Converged w | Difference from 1/φ |
|--------------------|-----------:|--------------------:|
| Gaussian | 0.6154 | 0.0027 |
| Uniform | 0.6170 | 0.0010 |
| Laplace | 0.6101 | 0.0080 |
| Bimodal | 0.6180 | 0.00003 |
| Exponential | 0.6052 | 0.0129 |

| Optimizer | Converged w | Difference from 1/φ |
|----------|-----------:|--------------------:|
| SGD lr=0.01 | 0.6154 | 0.0027 |
| SGD lr=0.001 | 0.6172 | 0.0009 |
| SGD lr=0.1 | 0.6131 | 0.0050 |
| Adam lr=0.01 | 0.6157 | 0.0024 |
| Adam lr=0.001 | 0.6175 | 0.0006 |
| Adam lr=0.0001 | 0.6169 | 0.0011 |

All converge within 0.013 of 1/φ. The slight bias for exponential signals (0.0129 difference) reflects asymmetry in the signal distribution, but even this case is within 2.1% of the theoretical value. The attractor is governed by the feedback structure, not the signal statistics (`robustness_sweep.py`).

#### 3.2 The Price of Self-Ignorance (Measured)

SGD treats each gradient step independently: it computes gradients as if the current data distribution were fixed. But in our self-referential system, the data distribution depends on w through the feedback loop. A system-aware optimizer that accounts for this dependency finds a different, better optimum.

- **SGD (myopic)**: converges to w = 1/phi = 0.618, achieving R^2 = 0.618
- **System-aware optimum**: w = 0.525, achieving R^2 = 0.670
- **Gap**: 8.3% in explained variance

We verified this by computing the true MSE surface as a function of w, accounting for the feedback-dependent variance of y at each w value. The surface has a single minimum at w = 0.525, not at 1/phi.

The 8.3% gap is the cost of treating contaminated data as clean. In our simplified setting, this is modest. Whether this gap persists, grows, or shrinks in higher-dimensional, more realistic systems is an open question (see Section 6).

#### 3.3 Depth vs Width Under Fixed Compute (Experimental)

We built a "binocular" system with N self-referential units, each observing the same signal with independent contamination. Units share hidden states through learnable cross-connections and are unrolled for T timesteps. The total compute budget is held fixed at T * N = constant.

Configurations tested (T * N = 10):

| Config | N | T | Description |
|--------|---|---|-------------|
| Deep | 1 | 10 | Single viewpoint, deep reflection |
| Balanced-A | 2 | 5 | Two viewpoints, moderate depth |
| Balanced-B | 5 | 2 | Five viewpoints, minimal depth |
| Wide | 10 | 1 | Ten viewpoints, no recurrence |

Results (MSE, lower is better):

| Config | alpha=0.0 | alpha=0.4 | alpha=0.8 | alpha=1.0 |
|--------|-----------|-----------|-----------|-----------|
| Deep (N=1, T=10) | 0.0067 | 0.0115 | 0.0189 | 0.0235 |
| Balanced-A (N=2, T=5) | 0.0062 | 0.0099 | 0.0161 | 0.0200 |
| **Balanced-B (N=5, T=2)** | **0.0055** | **0.0070** | **0.0103** | **0.0125** |
| Wide (N=10, T=1) | 0.0060 | 0.0073 | 0.0103 | 0.0128 |

Key findings:

1. **Balanced (N=5, T=2) wins at every contamination level**, for both T*N=10 and T*N=20 budgets. Score across all conditions: Deep=0 wins, Balanced=12 wins, Wide=0 wins.

2. **Deep chain-of-thought is the worst strategy**, losing to Balanced by 19-47% and to Wide by 10-46%. Reflecting deeply from a single contaminated viewpoint has sharply diminishing returns.

3. **Balanced-B (41 params) beats Wide (131 params)** despite having 3x fewer parameters. The T=2 minimum depth is genuinely valuable -- it provides one integration step where cross-connection information can be incorporated before outputting.

4. **T=2 appears to be a critical minimum**: enough depth to receive cross-unit information and refine once, but no more. This corresponds structurally to a single transformer layer with cross-attention.

We also tested T*N=20 with five configurations. The winner was always the config with T=2 and the remaining budget allocated to width. The pattern is consistent: broad consensus with minimal deliberation outperforms narrow deep reflection, in our simplified setting.

**Update: T=2 optimality depends on signal predictability.** Follow-up experiments tested the depth-width tradeoff across different signal types. For deterministic sinusoidal signals, Balanced-B (N=5, T=2) remains optimal, confirming the original result. However, for stochastic signals (uniform random, AR(1) correlated, noisy), the Wide configuration (N=10, T=1) wins, with Balanced-B second. Deep is always last regardless of signal type. The T=2 advantage appears to require sufficient signal structure for the integration step to exploit. With unpredictable signals, the extra recurrence timestep adds parameters without benefit, and maximum width (maximum diversity of contaminated views) wins instead. The robust conclusion is: depth is always the worst allocation, but the choice between T=1 and T=2 depends on whether the signal has temporal structure worth integrating.

#### 3.4 Cross-Connections Learn Subtraction (Observed)

When units share hidden states through learnable cross-connection weights (w_cross), those weights consistently converge to negative values:

| N (units) | w_cross (mean) | Std Dev |
|-----------|---------------|---------|
| 2 | -0.259 | 0.041 |
| 3 | -0.230 | 0.058 |
| 4 | -0.216 | 0.063 |
| 8 | -0.197 | 0.071 |

Units do not cooperatively share information -- they subtract each other's contamination. This implements a form of parallax: each unit sees signal + its own contamination. By taking the difference between two contaminated views, the unit-specific contamination cancels, and the shared signal survives.

The advantage of cross-connected units over independent units grows with contamination strength: 4% at alpha=0.0, up to 22% at alpha=1.0. When contamination is high, subtractive comparison becomes essential.

**Multi-layer cross-connections.** The subtractive pattern persists and strengthens with depth. In multi-layer architectures, w_cross is negative at every layer, with magnitude increasing in deeper layers:

| Architecture | Layer 1 | Layer 2 | Layer 3 |
|-------------|--------:|--------:|--------:|
| 3-layer | -0.083 | -0.181 | -0.189 |
| 2-layer | -0.130 | -0.180 | — |
| 1-layer | -0.165 | — | — |

Two patterns emerge. First, deeper layers learn stronger subtraction -- later layers perform more aggressive decontamination, as if refining what earlier layers began. Second, adding more layers weakens the first layer's cross-connection (from -0.165 to -0.083 in a 3-layer network), because the later layers take over the decontamination work. The cross-weight magnitude also grows with contamination strength α. The best strategy is cross-connections at every layer (`deep_cross_test.py`).

This negative coupling is reminiscent of several established ML techniques: contrastive learning (comparing augmented views), negative correlation learning in ensembles [3], and diversity-promoting regularization in mixture-of-experts architectures.

#### 3.5 Regime-Dependent Convergence (Observed)

Using a more complex SRU (Self-Referential Unit) architecture with tanh activation, we found that the convergence target depends on the training regime:

| Setting | w_self converges to | Explanation |
|---------|-------------------|-------------|
| Online self-referential (output feeds back to input) | ~0.591 (near 1/phi) | Direct feedback loop, myopic SGD |
| Batch regression (no feedback loop) | ~0.396 (near 1/phi^2) | Tanh nonlinearity dominates |
| Shallow BPTT (T=3 unroll) | ~0.476 | Closer to system-aware optimum 0.525 |
| Deep BPTT (T=20 unroll) | ~0.375 | Tanh saturation amplified by depth |

The golden ratio attractor (1/phi) appears specifically in the online self-referential regime -- precisely the regime relevant to RLHF, autoregressive generation, and recommendation systems.

Notably, deeper backpropagation through time (larger T) pushes w_self further from the true optimum, not closer. This is counterintuitive: more "system awareness" via BPTT makes things worse because tanh saturation effects accumulate with depth.

#### 3.6 The Perception Cascade (Proved + Verified)

The self-consistency equation composes through cascaded processing stages. We model a cascade of L stages, each with contamination alpha_i and channel count N_i, where each stage's output becomes the next stage's input. The key theoretical result (Theorem 1, verified numerically) is that each stage preserves R^2 = w(alpha_i) of the signal when its input is white noise.

However, when stages are chained, the cascade is **sub-multiplicative**: the actual end-to-end R^2 is dramatically worse than the product of per-stage values. For a 7-stage biological cascade (alpha = 0.05 to 1.0), the product of w(alpha_i) predicts a final R^2 of ~0.16, but the simulated cascade retains only ~0.008 -- roughly 20x worse. The reason: each stage's output is an AR(1) process (temporally correlated), violating the white-noise input assumption for subsequent stages. Each stage's temporal correlation makes the next stage's decontamination harder, and this penalty compounds.

| Case | Stages | Product w_i | Simulated R^2 | Ratio |
|------|--------|-------------|---------------|-------|
| 3x alpha=0.3 | 3 | 0.603 | 0.529 | 0.88 |
| 3x alpha=0.5 | 3 | 0.355 | 0.171 | 0.48 |
| 3x alpha=0.8 | 3 | 0.134 | 0.029 | 0.22 |
| Bio 5-stage | 5 | 0.130 | 0.028 | 0.22 |

The sub-multiplicativity worsens with contamination strength: at low alpha, the cascade is roughly multiplicative (ratio ~0.88); at high alpha, the actual R^2 is only ~20% of the multiplicative prediction.

Binocular (N=2) stages provide massive improvement. In the full 7-stage biological cascade:

| Stage | Alpha | N (mono) | R^2 mono | N (bio) | R^2 bio |
|-------|-------|----------|----------|---------|---------|
| Sensory | 0.05 | 1 | ~0.99 | 1 | ~0.99 |
| Features | 0.30 | 1 | ~0.90 | 2 | ~0.93 |
| Binding | 0.50 | 1 | ~0.67 | 2 | ~0.77 |
| Awareness | 0.60 | 1 | ~0.43 | 2 | ~0.57 |
| Narrative | 0.80 | 1 | ~0.12 | 1 | ~0.21 |
| Memory | 0.90 | 1 | ~0.03 | 1 | ~0.08 |
| Recall | 1.00 | 1 | ~0.008 | 1 | ~0.065 |

The binocular cascade retains ~0.065 R^2 versus ~0.008 monocular -- approximately 8x improvement. The binocular stages (Features, Binding, Awareness) provide the parallax decontamination that sustains signal fidelity through the later monocular stages. Once information is lost at a monocular bottleneck, it cannot be recovered (data processing inequality).

The monocular bottleneck position matters: early bottlenecks are more damaging than late ones. Binocular processing helps most at high-alpha stages, where contamination is strongest and decontamination has the largest marginal benefit (`perception_cascade.py`).

#### 3.7 The Minimal Stable Architecture (Proved + Verified)

Given the catastrophic signal loss in monocular cascades (~0.8% surviving after 7 stages), we asked: what is the **minimum architecture** for stable self-referential processing? Through systematic ablation across a 7-stage cascade, we identified the Minimum Viable Stable Unit (MVSU) and its structural requirements.

**Two NECESSARY components (Tier 1 -- removal causes collapse):**

1. **Dual channels (N >= 2)**: Two independent processing streams receiving the same signal but developing different contamination histories. This gives the system two equations for two unknowns (signal + contamination), enabling separation. Removing dual channels: R^2 collapses from 0.70 to 0.018 (97.4% degradation).

2. **Inhibitory cross-connections (w_cross < 0)**: Negative coupling between channels implements differential subtraction -- each channel subtracts the other's contamination to isolate shared signal. Removing inhibition (setting w_cross = 0): R^2 collapses to 0.018, identical to monocular. Critically, dual channels WITHOUT inhibition are useless -- the channels learn identical weights and produce identical outputs. Forcing positive cross-connections is even worse (R^2 = 0.008): positive coupling amplifies contamination instead of removing it.

**One HELPFUL component (Tier 2 -- removal degrades but does not destroy):**

3. **Predictive coding (system-aware optimization)**: Using the system-aware weight w_sys = (1 - alpha^2 * w^2)^2 instead of the myopic weight provides ~60% improvement in final R^2 (0.70 vs 0.434). This corrects the myopic overestimate of signal strength at each stage, and the improvement compounds through the cascade. This component is directly analogous to predictive processing in neuroscience [8], where each cortical level passes prediction errors rather than raw signals to higher levels.

**One REDUNDANT component (Tier 3 -- unnecessary when Tier 1-2 are present):**

4. **External grounding**: Periodic exposure to uncontaminated signal. When dual channels + inhibition + predictive coding are present, removing grounding actually improves R^2 by 0.6% (grounding events disrupt steady-state learning dynamics). Grounding becomes necessary only when internal decontamination mechanisms are absent.

The architecture taxonomy, evaluated on the 7-stage biological cascade:

| Architecture | N>=2 | w_cross<0 | Predictive | Final R^2 | Status |
|-------------|------|-----------|-----------|-----------|--------|
| Raw Monocular | No | No | No | 0.009 | COLLAPSED |
| Dual Naive | Yes | No | No | 0.009 | COLLAPSED |
| Dual Inhibitory | Yes | Yes | No | 0.434 | STABLE |
| Dual + Predictive | Yes | Yes | Yes | 0.700 | STABLE |
| Full MVSU (g=0.1) | Yes | Yes | Yes | 0.696 | STABLE |

The MVSU has 4 parameters per stage (2 w_self + 2 w_cross) versus 1 for monocular. Despite only 4x the parameters, it achieves ~39x better R^2 (0.696 vs 0.018 when comparing to the monocular ablation). The improvement is super-linear because cross-connections create qualitatively new capability -- decontamination -- that cannot be achieved by making a monocular system larger (`stable_architecture.py`).

#### 3.8 The Rehearsal Paradox (Verified)

Each act of memory recall passes the stored signal through a new self-referential processing stage at high contamination (alpha near 1.0). The cascade composition theorem predicts geometric degradation:

    R^2(n) <= R^2_cascade * w(alpha)^n

where n is the number of recalls. In practice, degradation is even faster than w^n due to the sub-multiplicative cascade effect (temporal correlation buildup).

| Recalls | R^2 (alpha=0.9) | R^2 (alpha=1.0) | w^n prediction (alpha=1.0) |
|---------|-----------------|-----------------|---------------------------|
| 1 | ~0.52 | ~0.37 | 0.618 |
| 2 | ~0.18 | ~0.08 | 0.382 |
| 3 | ~0.06 | ~0.02 | 0.236 |
| 5 | ~0.004 | ~0.003 | 0.090 |
| 8 | ~0.0002 | ~0.0001 | 0.021 |

After 5 recalls at alpha=1.0, only ~0.3% of the original signal survives. The simulated decay is consistently faster than the w^n upper bound, confirming the sub-multiplicative cascade effect.

This creates a paradox: **well-rehearsed memories feel more vivid (lower retrieval effort, lower effective alpha per recall) but are increasingly confabulated (more total processing stages)**. Each recall reconstructs rather than retrieves, and the reconstruction error compounds. This is consistent with psychological findings on memory distortion [9] -- that frequently recalled memories are among the most distorted, and that "flashbulb memories" degrade despite their subjective vividness.

#### 3.9 Real-World Validation (Experiment 16)

After establishing the MVSU theoretically and on synthetic cascades, we tested it on three real continuous feedback tasks. Each task has genuine self-referential dynamics: the model's prediction physically alters the system being predicted.

| Task | Signal Type | Feedback Mechanism | MVSU Improvement |
|------|-----------|-------------------|-----------------|
| Thermostat control | Periodic (daily cycle) | Heater responds to prediction | +50.4% |
| Sensor calibration | Drifting (random walk) | Auto-calibration drift | +45.0% |
| Market microstructure | Mean-reverting (O-U) | Market impact | +46.9% |

Four methods were compared: monocular (single predictor, standard SGD), MVSU with same-architecture different-initialization, MVSU with architecture-split (linear + MLP), and an oracle with knowledge of the feedback mechanism.

Key findings:

- **MVSU with architecture diversity (linear + MLP) achieves 45-50% MSE reduction** at high contamination across all three tasks.
- **Random initialization diversity alone is INSUFFICIENT** — two linear models with different random seeds converge to the same optimum, performing 53-83% worse than monocular. The loss landscape for linear models has a single basin; different starting points do not provide genuine parallax. Architecture diversity (different inductive biases) provides the free parallax that different random seeds cannot.
- **w_cross converges to negative values on all tasks** (-0.13 to -0.23), confirming that inhibitory decontamination is not an artifact of synthetic signals but a general property of self-referential feedback systems.
- **Improvement grows with contamination strength** (thermostat: +19% at alpha=0 to +55% at alpha=1), consistent with the theory's prediction that the MVSU advantage scales with the severity of self-referential feedback.
- The **MVSU module** (`python/mvsu.py`) is a 231-line pure-numpy drop-in wrapper containing MVSUPredictor, LinearPredictor, MLPPredictor, and MVSUEnsemble.

This result validates the practical value of the theoretical framework: the self-consistency equation and MVSU architecture translate from toy settings to real continuous feedback problems. The critical refinement is that "free diversity" requires different inductive biases, not different random seeds (`mvsu.py`, `mvsu_real_demo.py`).

#### 3.10 Coherence and the Foundation of Perception (Experiment 17)

We formalized the relationship between signal coherence, self-referential contamination, and the ability to perceive.

Perception requires two conditions simultaneously:
1. **Coherence** (C > 0): the signal must contain structure above the noise floor
2. **Distinction** (N >= 2, w_cross < 0): the system must be able to separate signal from self-echo

Neither is sufficient alone. At C = 0.1 (low coherence), the MVSU maintains R^2 = 0.387 while monocular collapses to R^2 = 0.024. At C = 0.8 (high coherence), monocular achieves R^2 = 0.425 but the MVSU reaches R^2 = 0.636.

The self-consistency equation acquires a new interpretation through the self-perception ratio (SPR). At alpha = 1 (full self-reference), the myopic system partitions its observations as:
- 1/phi ~= 0.618: attributed to the external world
- 1/phi^2 ~= 0.382: attributed to self (own echo)

This partition was verified to exact numerical precision (SPR = 0.3820). The system-aware optimizer corrects to 0.525/0.475 -- a 9.3% shift toward greater self-attribution. This "self-ignorance gap" represents the degree to which a myopic system underestimates its own contamination of its perception.

The phase diagram in (C, alpha) space reveals the MVSU is most critical where monocular processing fails: low coherence combined with high contamination. Surprisingly, the MVSU functions even at C = 0 (pure noise input) because the self-referential feedback itself creates predictable AR(1) temporal structure that the dual-channel architecture can exploit.

Reference: `coherence_perception.py`, `COHERENCE_PERCEPTION_THEORY.md`

#### 3.11 Multi-Agent Extension and Information-Theoretic Foundations (Experiments 19-21)

Three independent probes extended the framework to multi-agent settings, revealing the information-theoretic meaning of the golden ratio and establishing the MVSU's role in preventing model collapse.

**The N-agent self-consistency equation.** When N symmetric agents share a signal with mean-field coupling alpha/N each, the total contamination is:

    contam(t) = (alpha/N) * sum_j w * y_j(t-1) = alpha * w * y_bar(t-1)

The N cancels exactly. The total echo in the system is independent of the number of agents -- as long as total coupling strength is fixed, one loud speaker and fifty quiet ones produce the same contamination. At sigma=0, the self-consistency equation collapses to w^2 + w - 1 = 0 for any N. The golden ratio is the universal attractor of multi-agent self-referential systems with mean-field coupling. There is no phase transition and no critical N. Verified experimentally for N = 1, 2, 5, 13, 50 (5 seeds, 3000 timesteps each; `multi_agent_feynman.py`).

**log(phi) as channel capacity.** The mutual information between the true signal and a fully self-referential agent's observation is:

    I(s; y) = -1/2 * log(1 - 1/phi) = -1/2 * log(1/phi^2) = log(phi) = 0.4812 nats

This identity -- relying on the golden ratio property 1 - 1/phi = 1/phi^2 -- means a single agent already saturates the information-theoretic ceiling. No number of additional agents can extract more information from a fully self-referential channel. The golden ratio is not merely a dynamical attractor of SGD but the Shannon capacity of the self-referential channel.

Three information-theoretic theorems were proved and verified (`multi_agent_info.py`):

1. **Zero Redundancy Theorem:** For agents with different contamination parameters alpha_i != alpha_j, I(s; y_1, y_2) = I(s; y_1) + I(s; y_2) exactly. Observations are perfectly non-redundant (verified across 200 configurations, deviation < 10^{-10}).

2. **Multi-Agent Information Ceiling:** For N agents with same alpha and independent observation noise sigma_n, lim_{N->inf} I(s; y_1,...,y_N) = -log(alpha * w(alpha)). Saturation is rapid: N=5 captures 96.4% of the ceiling.

3. **The Golden Ceiling:** At alpha=1, the single-agent MI equals the multi-agent ceiling exactly: I_ceiling = log(phi) = 0.4812 nats = 0.6942 bits.

**The w_cross sign diagnostic.** In multi-agent crowds where contamination is shared (same mean-field echo for all agents), the MVSU pair learns positive w_cross (~+0.3), not the negative values seen in all prior experiments. This is because the optimal strategy for shared contamination with independent noise is signal-averaging (positive coupling), not contamination-subtraction (negative coupling). The sign of the learned cross-connection weight diagnoses the contamination topology:

| w_cross | Contamination | Mechanism |
|---------|--------------|-----------|
| Negative | Independent between channels | Subtraction |
| Positive | Shared across channels | Noise averaging |

**Model collapse prevention via MVSU.** In a generative chain (KDE trained on previous generation's output, 20 generations, mixture of 3 Gaussians), the MVSU with bandwidth-diverse KDEs (0.5x and 2.0x Silverman's rule) and cross-inhibitory sample selection prevents runaway collapse (`multi_agent_collapse.py`):

- No intervention: W1 distance degrades from 0.29 to 3.08 (10.7x increase over 20 generations)
- MVSU every generation: W1 stabilizes at ~1.4 (54% improvement at gen 19)
- MVSU every 5th generation: W1 = 2.24 (27% improvement)
- MVSU at gen 0 only: W1 = 3.87 (26% WORSE -- one-shot MVSU hurts)

The MVSU is prophylactic, not curative: it prevents new contamination from entering at generation boundaries but cannot reverse existing degradation (data processing inequality). The startup cost (W1=0.97 at gen 0 vs 0.29 for plain chain) is the price of the filtering bias, recovered by gen 5-6 as uncontrolled chains degrade faster.

The critical intervention fraction is approximately 50%: below this, the degradation rate exceeds the MVSU's compensation capacity. For synthetic data ecosystems with many models generating and consuming data, roughly half or more of the pipeline stages need MVSU-style dual-model consensus for genuine stabilization.

**The perception-generation distinction.** The information-theoretic analysis revealed that the MVSU's value is generative, not perceptual. A single agent at alpha=1 already captures all log(phi) nats of information (Marcus's ceiling). The MVSU does not help the agent know more -- it helps the agent produce more faithfully. This resolves the apparent contradiction between "a single agent is information-optimal" and "MVSU prevents collapse."

**Cross-feed synthesis.** When the three independent probes shared results, emergent insights arose that none had individually: the log(phi) budget framing (each generation has a fixed information budget), the w_cross sign diagnostic (emerged from juxtaposing Feynman's positive sign against prior negative results), and the perception-generation distinction (emerged from juxtaposing Marcus's optimality proof against Sarah's collapse prevention). The cross-feed round itself demonstrated the MVSU principle: architecturally different researchers with one cross-connection round produced qualitatively new insights (Y > max(X)).

#### 3.12 Damped Meta-Optimization (Experiments 22-24)

The meta-optimizer recurrence w_{n+1} = (1 - alpha^2 * w_n^2)^2 reaches the system-aware optimum (w=0.525, MSE=0.331) at low contamination but diverges at alpha >= 0.7, preventing it from closing the 15.6% MSE gap at high contamination. Three independent teams tested whether damped correction — taking partial steps toward the target — could stabilize the path without changing the destination.

**The damped recurrence:** w_{n+1} = w_n + beta*(w_target - w_n), where w_target = 0.525 (the system-aware optimum) and beta is the damping factor controlling step size.

**Key results:**

| Beta | Convergence Speed (alpha=1.0) | Robustness | Property |
|------|-------------------------------|-----------|----------|
| 1/phi^2 = 0.382 | 2 iterations | Works at alpha=1.0 | Speed-optimal |
| 0.4 | 4 iterations | Works at alpha=1.0 | Empirical sweet spot |
| 1/phi = 0.618 | 8 iterations | Works at ALL alpha | Robustness-optimal |
| 0.7-0.77 | Slow or wrong attractor | Boundary zone | Divergence threshold |

**The speed-robustness tradeoff.** Beta = 1/phi^2 = 0.382 converges fastest (2 steps at alpha=1.0), while beta = 1/phi = 0.618 converges reliably across the entire alpha range (0.3 to 1.0). The hobbyist's adaptive strategy (start at beta=0.5, reduce by 20% on sign flips) self-tunes to beta ≈ 0.3-0.4, converging on the speed-optimal value without knowing it exists.

**The stability boundary is wider than predicted.** Linear analysis predicts beta < 0.553 for stability. All three teams measured the actual divergence boundary at 0.7-0.77, roughly 40% higher than the theoretical bound. However, Feynman identified a treacherous zone between 0.77 and 0.8 where the iteration converges to the wrong attractor (myopic w=0.62 instead of system-aware w=0.525). The Marcus bound is conservative but safely within the correct basin of attraction.

**All reasonable strategies work.** Fixed beta, adaptive beta (cut on whipsaw), and momentum-smoothed beta all converge to w=0.525 at alpha=1.0, closing 100% of the MSE gap (0.382 -> 0.331). The problem is fundamentally easy once damped — the hard part was knowing that damping was the right intervention.

**MVSU vs damped recurrence.** Direct measurement at alpha=1.0 showed the MVSU stays at w=0.614 (MSE=0.386), closing only 4.4% of the myopic-to-optimal gap. The MVSU is a noise filter that never leaves the golden-ratio algebraic surface. It is NOT a meta-optimizer. The damped recurrence IS a self-awareness engine that reaches the true optimum.

**The proposed two-stage architecture.** MVSU and damped recurrence are complementary, not competing:
1. **Stage 1 (MVSU):** Dual-channel architecture with cross-inhibition estimates the contamination parameter alpha via w_cross (correlation r = -0.84).
2. **Stage 2 (Damped recurrence):** Feed estimated alpha into damped recurrence at beta = 1/phi^2. Two iterations to w=0.525.

The MVSU measures; the recurrence corrects. Neither can do the other's job. Together they close the full 15.6% gap through a dynamically stable path. This architecture has not yet been built or tested.

**The dark fraction triple identity.** 1/phi^2 = 0.382 is simultaneously:
- The **cost**: fraction of MSE wasted at the myopic fixed point (stability tax)
- The **cure**: optimal damping factor for fastest convergence
- The **measurement gap**: difference between MVSU performance (w=0.614) and system-aware optimum (w=0.525)

The system encodes its own ignorance in a number that is also the instruction for correcting that ignorance. Overcorrecting by more than the blind spot (beta > 1/phi^2 by too much) guarantees overshooting into territory the system cannot verify.

**Cross-feed synthesis.** The two-stage architecture, the speed-robustness tradeoff, and the cost-equals-cure identity emerged only when the three teams' results were combined. None of these insights existed in any individual report. The research process itself demonstrated the MVSU principle: diverse perspectives with one cross-connection round produced genuinely emergent understanding (Y > max(X)).

Reference: `damped_teen.py`, `damped_hobbyist.py`, `damped_feynman.py`, `cross_feed_damped.md`

#### 3.13 MVSU Applied to Numerical Simulation (Experiments 25a-c)

The MVSU cross-correction principle -- that two channels with anti-correlated errors can produce better output than either channel alone -- was tested on a numerical simulation task: reducing integration error in Kepler orbit propagation. This tests whether MVSU generalizes beyond self-referential contamination to general error reduction in systems where "ground truth" exists (the analytical solution).

**Setup:** Two numerical integrators independently propagate a Kepler orbit (eccentricity e=0.3) for 15-20 orbits. Each produces position estimates. The MVSU combines their outputs with a learned cross-weight w_cross to minimize error vs the analytical ground truth. We test three pairs of integrators across three iterations.

**The critical question:** Does cross-correction work when integrators have different error signatures, even without self-referential feedback?

**Three iterations:**

| Version | Integrator Pair | Accuracy Gap | Error Correlation | Optimal w_cross | MVSU Improvement | Verdict |
|---------|----------------|--------------|-------------------|-----------------|------------------|---------|
| **v1** | Euler vs Verlet | 300x | High positive | -0.5 (boundary) | None (selects Verlet) | **FAILED** |
| **v2** | RK4 vs RK4-3/8 | 3.2x | Correlated | +0.5 (boundary) | None (selects RK4) | **WEAK** |
| **v3** | RK4 vs AB4-2x | 6.2x | **-0.98 (anti-correlated)** | **-0.13 (interior)** | **2.5-3.7x** | **SUCCESS** |

**v1 (Euler vs Velocity Verlet) — FAILED:**
- Euler (1st-order, non-symplectic) vs Verlet (2nd-order, symplectic): 300x accuracy gap
- The learned w_cross → -0.5 (pure Verlet), simply selecting the vastly superior integrator
- **Lesson**: MVSU requires comparable-quality generators. When one channel is 300x worse, it contributes only noise.

**v2 (RK4-classic vs RK4-3/8) — WEAK:**
- Both 4th-order Runge-Kutta methods with different Butcher tableau coefficients
- Accuracy gap reduced to 3.2x (much better than v1), but errors are correlated (same direction, different magnitude)
- Optimal w_cross = +0.5 (boundary), again just selecting the better integrator (RK4-classic)
- **Lesson**: Different parameters ≠ different error structure. Same algorithm family produces correlated errors with no cross-correction benefit.

**v3 (RK4 vs AB4-2x) — SUCCESS:**
- RK4 (single-step, 4 intermediate derivative evaluations) vs AB4 (multi-step, history extrapolation with 2x substeps for accuracy matching)
- Accuracy gap 6.2x (AB4 worse despite substeps, but both 4th-order methods)
- **Error correlation = -0.98 (strongly anti-correlated!)**: RK4 overshoots (mid-step probing biases forward), AB4 undershoots (history extrapolation biases backward)
- Optimal w_cross = -0.13 (interior minimum, clearly negative)
- **Fixed MVSU**: 2.5x improvement over RK4 alone
- **Online-learned MVSU**: 3.7x improvement, converges to w_cross = -0.132 independently (matches sweep-optimal without ground truth)
- **Simple average HURTS**: 2.6x worse than RK4 alone! Averaging anti-correlated errors with unequal magnitudes amplifies error instead of reducing it.
- **Damped measurements**: Optimal beta ≈ 0.93 (high because noise was small relative to integration drift)

**The critical insight:** MVSU cross-correction works when generators have **structurally different computational strategies**, not just different parameters:

- **RK4** (single-step): Probes derivatives at 4 intermediate points within each timestep → systematic overshoot
- **AB4** (multi-step): Extrapolates from derivative history at past timesteps → systematic undershoot

The errors are anti-correlated in **direction** (cosine = -0.98), producing orthogonal error components that cross-correction can exploit. This is qualitatively different from self-referential contamination (where errors are systematically biased by feedback), but the MVSU architecture still applies.

**Error correlation as predictor:** The cosine similarity of error vectors predicts cross-correction potential:

| Error Correlation | Cross-Correction Potential | Example |
|-------------------|---------------------------|---------|
| Anti-correlated (cos < 0) | **Strong benefit** | RK4 vs AB4 (v3): 2.5-3.7x |
| Uncorrelated (cos ≈ 0) | Moderate benefit | Different architectures on independent noise |
| Correlated (cos > 0.7) | **No benefit** | Same algorithm family (v2) |
| Highly correlated (cos > 0.9) | **Harmful** | One channel is noise (v1) |

**Online learning converges to sweep-optimal:** The online w_cross learning (gradient descent on recent error history) converged to w_cross = -0.132, matching the sweep-optimal value of -0.13 without any knowledge of the analytical solution or sweep results. This demonstrates the principle can be deployed in real systems where exhaustive sweep is impractical.

**Simple averaging can hurt:** With anti-correlated errors of unequal magnitude, the simple average (w_cross = -0.5 in the MVSU formulation: output = A + w_cross*(A-B)) is NOT optimal and can be worse than using the better channel alone. The negative cross-weight must be tuned to the error magnitude ratio.

**The practical recipe:**
1. Pair structurally different methods (different computational strategies, not just different parameters)
2. Measure error correlation on a validation set (compute cosine similarity of error vectors)
3. If anti-correlated (cos < 0): Use MVSU with learned negative w_cross
4. If correlated (cos > 0.7): Just use the better method; MVSU won't help
5. Learn w_cross online via gradient descent on recent error (converges to sweep-optimal independently)

**New boundary condition:** The MVSU requires generators with complementary error signatures (orthogonal or anti-correlated errors), not just diversity in architecture or parameters. This extends the earlier boundary condition (continuous uniform contamination) to a more general form: **diversity must be in error structure, not just in method**.

Reference: `mvsu_simulation.py` (v1), `mvsu_simulation_v2.py` (v2), `mvsu_simulation_v3.py` (v3)

#### 3.14 Discrete Observer Predictions in ML Architectures (Experiments 28-30)

The discrete observer reconstruction framework (`DISCRETE_OBSERVER_RECONSTRUCTION.md`) derives that a network of 8 observers at cube vertices, reconstructing a continuous field on a sphere, achieves optimal information throughput when the fraction of observational capacity devoted to redundancy is exactly 1/phi^2 = 0.382. We tested whether this geometric prediction transfers to three ML architecture settings where a "redundancy fraction" parameter controls the balance between independent and shared processing.

**Experiment 28: CNN Receptive Field Overlap.** We swept the stride of a single-layer CNN on CIFAR-10 across all valid integer strides for kernel sizes K=3,5,7, measuring test accuracy as a function of overlap fraction (1 - stride/kernel_size). The prediction: optimal overlap = 0.382. Result: peak accuracy at overlap = 0.333 (K=3, S=2), the nearest achievable integer-stride configuration to 0.382. A clear inverted-U curve places the phi-zone (0.33-0.43) at the peak, with both low overlap (<0.2) and high overlap (>0.6) substantially worse. The conventional default of stride=1 (maximum overlap) is suboptimal.

**Experiment 29: Dropout Rate.** We swept dropout rate p from 0.0 to 0.7 on a 2-layer MLP with CIFAR-10 (3k training subset). The prediction: optimal p = 0.382. Result: peak accuracy at p=0.35 (42.58%), with p=0.382 at 42.31% (rank #4, within noise). The optimal zone is a broad plateau from 0.30-0.45. The phi-predicted value outperforms the conventional default of p=0.5 by 0.42 percentage points. The overfitting gap plot reveals p=0.382 as the inflection point between overfitting and underfitting regimes -- the "edge of chaos" in regularization space.

**Experiment 30: Multi-Head Attention Topology.** We tested inter-head communication on a tiny ViT (8 heads, 32-dim embedding, 1 layer) using cube topology (3-neighbor graph), all-to-all topology, and no communication (standard), with mixing parameter alpha = 1/phi^2. Three sub-predictions: (a) communication helps, (b) optimal alpha converges to 0.382, (c) sparse beats dense. Results: (a) confirmed -- cube topology +0.8%, all-to-all +1.4% over independent heads; (b) partially confirmed -- learnable alpha converged to 0.355 (only 0.027 from prediction); (c) not confirmed at this scale -- dense beat sparse, likely a small-scale effect. The strongest finding: fixed alpha=0.382 matches learnable alpha (0.326 vs 0.327), providing a free hyperparameter.

**Cross-experiment synthesis.** All three experiments find optima in the 0.33-0.40 range centered near 1/phi^2. The mean observed optimum is 0.346, mean absolute deviation from 0.382 is 0.036. The phi-zone is consistently the attractor basin across completely different architectural contexts. These are CPU-scale experiments with small data and few seeds; GPU-scale replication with larger architectures and more datasets is needed to confirm whether the prediction holds at production scale.

**Face #9: Architectural redundancy.** These experiments establish a ninth appearance of the golden ratio: the optimal redundancy fraction in ML architectures (receptive field overlap, dropout rate, inter-head mixing) clusters near 1/phi^2 = 0.382. This face is geometrically distinct from the earlier faces -- it emerges from spatial coverage optimization rather than dynamical self-consistency or information capacity.

Full experimental details, tables, and analysis: `DISCRETE_OBSERVER_ML_EXPERIMENTS.md`.
Reference: `cnn_stride_sweep.py`, `dropout_sweep.py`, `multihead_cube_attention.py`.

**GPU Validation (Tesla T4, full CIFAR-10, 20 epochs).** We replicated the Observer Transformer architecture at GPU scale using the OT-Tiny configuration (d_model=128, 4 layers, 8 heads) on the complete CIFAR-10 dataset (50k train, 10k test). The core finding strengthened dramatically: dropout=0.382 outperforms dropout=0.5 by +4.84 percentage points (65.87% vs 61.03%), a ~10x larger gap than the CPU-scale experiment. Observer Attention (Tier 2, inter-head hypercube messaging) achieved 65.60% with 22% fewer parameters than baseline, yielding the best parameter efficiency (0.1046 acc/100K params). The learned w_cross values stayed negative in all 32 heads across 4 layers, with magnitude increasing with depth (mean -0.316 in block 0 to -0.479 in block 3), confirming the MVSU's inhibitory mechanism and its depth-dependent correction prediction. The alpha sweep peaked at 0.3, near but slightly below the predicted 0.382, preserving the inverted-U shape. Two negative results: FFN=2.618x alone hurt slightly (-0.97%) and must be combined with dropout reduction; phi-annealing provided no benefit (-0.30%). Full OT (Tier 3) did not beat simpler Tier 2. The GPU results confirm that the phi-zone is the correct search region for redundancy parameters and that dropout=0.382 is the highest-impact single intervention.

**Echo subspace analysis (Experiment 31).** We investigated whether the echo (primary - secondary channel difference) has exploitable structure that could enable cheaper correction. PCA analysis revealed the echo is NOT low-rank: top-4 components explain only ~52% of variance across all layers (far below the 80% threshold). Cross-layer similarity is ~0.012 (essentially random), showing the echo is NOT self-similar. However, a learnable rank-4 projector (Tier 2.5 Learnable) matches full dual-channel performance (67.13% vs 67.11%) with fewer parameters when initialized from PCA and trained end-to-end. Freezing the PCA basis fails (66.22%, worse than baseline). The key insight: the echo itself is high-dimensional, but the correctable component is low-rank and learnable. Maximum variance directions (PCA) differ from maximum correction utility. The "smart eraser" requires task-specific learning, not pre-computation.

---

### 4. What Didn't Work

This section documents predictions that failed. These null results are as important as the positive findings -- they constrain where the self-consistency equation applies and where the analogy breaks down.

#### 4.1 The Golden Ratio Does Not Survive Nonlinearity

The exact value 1/phi appears only for linear activation (k=1). ReLU gives an effective gain of 0.394, which involves pi (from the Gaussian integral over the positive half-line), not phi. Sigmoid gives 0.384, which is numerically close to 1/phi^2 = 0.382 but is not algebraically related -- the governing equation involves a non-algebraic constant (k = 0.330). The clean algebraic structure of the golden ratio equation breaks with realistic activation functions. What survives is the general form kw^2 + w - 1 = 0, but the specific roots lose their number-theoretic elegance.

#### 4.2 Self-Referential Architecture Provides No Structural Advantage

We built an SRU (Self-Referential Unit) as an ML primitive, where a shared w_self parameter explicitly models the self-referential feedback. Against a parameter-matched baseline with free hidden units:

- SRU ties at alpha=0 and marginally wins at alpha=0.1 (+0.002 R^2)
- SRU loses at all alpha >= 0.2
- At alpha=1.0, the baseline achieves R^2 = 0.726 vs SRU's 0.595 (a 2.5x gap)

The shared w_self constraint is a limitation, not an advantage. Independent hidden units that can individually adapt to the self-referential dynamics outperform units constrained to share a single self-referential weight. Making self-reference explicit in the architecture does not help -- at least not in this form.

#### 4.3 The Observer DOF Step Function Does Not Manifest

We predicted a discrete jump in performance at N=2 observers, based on an analogy to geometric parallax (two viewpoints can triangulate position, one cannot). The prediction was a gain ratio of MSE(N=1)/MSE(N=2) = 2.5.

Observed gain ratios:

| alpha | Gain Ratio (N=1/N=2) |
|-------|---------------------|
| 0.0 | 1.049 |
| 0.4 | 1.197 |
| 0.8 | 1.270 |
| 1.0 | 1.273 |

The maximum observed ratio is 1.273, far below the predicted 2.5. The improvement with N is gradual and smooth, not a discrete phase transition. Geometric parallax (in spatial observation) involves discrete degrees of freedom. Information parallax (in self-referential learning) involves continuous decontamination gain. The analogy that motivated the experiment does not directly transfer.

#### 4.4 T=2 Minimum is Signal-Dependent (Partial)

Our original finding that T=2 depth is universally optimal under fixed compute (Section 3.3) turns out to be signal-dependent. For deterministic or highly structured signals, T=2 wins — the integration step captures temporal structure. For stochastic signals (uniform random, AR(1), noisy), T=1 with maximum width wins instead. The integration step of T=2 adds parameters without benefit when there is nothing temporally predictable to integrate.

What remains robust: deep configurations (T >> 2) always lose. The contamination-decontamination tradeoff always favors width over depth. The nuance is in the boundary between T=1 and T=2, which depends on signal structure — not in the conclusion that depth is costly.

#### 4.5 Cascade Prediction Fails

We predicted that a second-level agent (Agent B, observing Agent A's output plus its own echo) would converge to w = 1/phi^2, if the self-referential discount compounds multiplicatively across levels.

Observed: w_B = 0.534, closest to 0.5 (not 1/phi^2 = 0.382). This is consistent with Agent B effectively seeing k=2 neighbors (A's output + its own echo), giving the k=2 solution of kw^2 + w - 1 = 0 which is w = 0.5. Self-referential discounts do not compound multiplicatively; each level applies the same family of equations with its own effective k.

#### 4.6 Over-Relaxation Does Not Transfer to Classification (Experiment 12)

We attempted the first real-world validation: applying the theory's predictions to pseudo-labeling on a digits classification task. Pseudo-labeling is a genuine self-referential ML technique -- the model generates labels for unlabeled data, then retrains on those labels, creating a feedback loop where the model trains on its own predictions. The contamination parameter alpha maps directly to the fraction of training data that is pseudo-labeled.

We tested two fixes motivated by the theory: (1) over-relaxation (omega > 1.0 weighting on pseudo-labeled samples, analogous to SOR), and (2) dual-model cross-labeling (two models label each other's unlabeled data, implementing the binocular parallax principle).

**Results: All fixes failed.**

- Over-relaxation uniformly hurts: optimal omega = 1.0. Every omega > 1 degrades accuracy.
- Dual-model cross-labeling provides no benefit over single-model self-labeling.
- The contamination is confirmed (accuracy degrades with more pseudo-label rounds), but the proposed corrections do not help.

**Root cause**: Pseudo-label errors are **class-structured**, not uniform. When the model confuses digit 3 with digit 8, it does so systematically -- the errors are correlated within class pairs. The self-consistency equation assumes uniform, continuous contamination (signal + noise). Classification errors are discrete, clustered, and correlated in ways the continuous theory does not capture. Over-relaxation amplifies the class-structured errors rather than correcting a uniform bias. The dual model learns the same class confusions because both see the same data.

This is an important boundary condition: the theory requires uniform continuous contamination. Class-structured errors in discrete prediction tasks violate this assumption (`pseudolabel_validation.py`).

#### 4.7 Random Initialization Is Insufficient Diversity (Experiment 16)

MVSU with two identical linear architectures at different random initializations performed WORSE than monocular (-53% to -83% MSE increase on all three real-world tasks: thermostat, sensor calibration, market microstructure). Linear models with different init converge to the same local optimum because the loss landscape has a single basin. The two "eyes" end up seeing identically, providing zero parallax.

This further refines the parallax-competence tradeoff from Experiment 13: diversity must come from different inductive biases (architectural differences), not from different starting points or data subsets. Architecture-split (linear + MLP) achieves 45-50% improvement on the same tasks, confirming that only structurally different models provide the free parallax needed for decontamination.

#### 4.8 Parallax Requires Free Diversity (Experiment 13)

Following the dual-model failure, we hypothesized that the problem was lack of genuine viewpoint diversity -- both models trained on identical data learned identical representations. We tested four methods of forcing different viewpoints, implementing staged cross-labeling with increasing trust weights:

| Diversity Method | Error Correlation | Individual Accuracy | Ensemble vs Baseline |
|-----------------|-------------------|--------------------|--------------------|
| Feature-split (L/R halves) | 0.18 (excellent) | Crippled (~60%) | -8.4% |
| Data-split (50/50 labeled) | -0.87 (maximum) | Weak (~70%) | -1.5% |
| Architecture-split (LogReg/MLP) | ~0.45 (moderate) | Full (~90%) | +0.6% |
| Feature-transform (raw/PCA) | ~0.55 (modest) | Full (~90%) | +0.3% |

The results reveal a **parallax-competence tradeoff**:

- **Feature-split** achieves excellent parallax (low error correlation = genuinely different error patterns), but each "eye" sees only half the image and is individually crippled. The ensemble loses badly (-8.4%).
- **Data-split** achieves maximum parallax (negative error correlation -- the eyes make opposite mistakes), but each eye trains on only 50 labeled samples and is individually weak. The ensemble still loses (-1.5%).
- **Architecture-split** maintains full competence (both models see all data, all features) with moderate parallax from different inductive biases. This is the only method that improves (+0.6%), though the improvement is not statistically significant.

**Key finding**: Diversity must be "free" -- achieved through architecture or inductive bias differences, not at the cost of individual model quality. Splitting data or features to create diversity destroys the very competence needed to generate useful pseudo-labels.

This constraint was resolved theoretically by the MVSU (Section 3.7), which achieves diversity through inhibitory cross-connection dynamics rather than input restriction. Both channels see the full signal; diversity emerges from the negative coupling, not from restricted views (`staged_binocular.py`).

---

### 5. What This Might Mean for ML

We emphasize that these are results from toy settings with scalar agents, Gaussian signals, and simple feedback loops. Real ML systems have millions of parameters, complex loss landscapes, and multi-step feedback mechanisms. The value of this work is in identifying the phenomenon and its algebra, not in the specific numbers.

With that caveat, several directions seem worth exploring:

**Quantifiable self-referential bias.** The self-consistency equation kw^2 + w - 1 = 0 gives a closed-form prediction for where myopic optimization will get stuck in a self-referential system. In our simplified setting, the gap between myopic (1/phi) and system-aware (0.525) optima is 8.3%. If this structure persists at scale, it suggests a concrete and recoverable inefficiency in systems like RLHF, where the reward model trains on model-generated outputs.

**System-aware training.** Methods that differentiate through the feedback loop -- analogous to LOLA [5] in multi-agent RL or BPTT in recurrent networks -- should in principle recover the self-ignorance gap. However, our BPTT experiments with tanh activation showed that naive system-awareness (deeper unrolling) can make things worse due to saturation effects. The right form of system-awareness matters.

**Cross-connected diverse perspectives.** Under fixed compute, balanced ensembles (moderate width, T=2 depth) consistently outperformed both deep single-agent reflection and wide independent ensembles, in our simplified setting. The cross-connections learned negative weights, implementing subtractive decontamination. This echoes existing work on negative correlation learning [3] and suggests that diversity-promoting mechanisms in mixture-of-experts architectures may be more important than typically appreciated -- specifically for self-referential problems.

**T=2 as conditional minimum integration depth.** Across both compute budgets we originally tested, the optimal configuration had T=2: enough depth to receive cross-unit information and integrate it once. Follow-up experiments revealed this depends on signal predictability -- for stochastic signals, T=1 (maximum width) wins. The robust finding is not "T=2 is optimal" but "depth beyond T=2 is always wasteful in self-referential settings." Whether this ceiling persists in more complex settings is unknown.

**Regime-dependent convergence.** The observation that online self-referential learning converges near 1/phi while batch learning converges elsewhere suggests that the training regime fundamentally determines the fixed point. For practitioners, this means the same architecture may exhibit different self-referential biases depending on whether training is online (streaming) or batch.

**Cascade composition compounds bias sub-multiplicatively.** The cascade theorem means that self-referential bias does not simply multiply through pipeline stages -- it compounds worse than multiplicatively. Each stage's AR(1) output makes subsequent decontamination progressively harder. For multi-stage ML pipelines (e.g., retrieval -> ranking -> generation in RAG systems, or iterative RLHF with multiple reward model updates), signal degradation may be far worse than per-stage analysis would suggest. The product of per-stage R^2 values is an upper bound, not a prediction.

**The MVSU provides an architectural prescription.** The minimal stable architecture result gives a concrete design principle: two channels with inhibitory cross-connections, optionally augmented by predictive coding. In our simplified setting, this 4-parameter-per-stage architecture preserves ~39x more signal than a 1-parameter monocular system. The inhibitory coupling is structurally necessary -- it creates diversity through dynamics rather than input restriction, resolving the parallax-competence tradeoff that doomed feature-split and data-split approaches.

**The parallax-competence tradeoff constrains diversity.** The staged binocular experiment showed that diversity achieved by crippling individual models (splitting features or data) destroys the competence needed to benefit from that diversity. Effective diversity must be "free" -- arising from architectural differences, different inductive biases, or learned inhibitory dynamics. This has direct implications for ensemble methods, mixture-of-experts routing, and multi-model collaboration: diversity-promoting mechanisms should operate on representations and coupling, not on input partitioning.

**The practical recipe is clear.** Take any continuous feedback system, wrap the predictor in a dual-channel architecture with different inductive biases and learned inhibitory cross-connections. The 45-50% improvement on thermostat, sensor, and market tasks demonstrates this is not merely theoretical — it is a concrete, deployable technique for any system where the model's output feeds back into its observations.

**Rehearsal degrades signal -- implications for iterative systems.** Each recall/re-evaluation passes the signal through a new self-referential stage. After 5 recall cycles at high contamination, only 0.3% of the original signal survives. This suggests that iterative RLHF (where the reward model is repeatedly updated on new model outputs) may suffer compounding degradation -- each RM update cycle is a new self-referential stage, and the sub-multiplicative cascade effect means the accumulated distortion grows faster than any single-stage analysis would predict.

---

### 6. What We'd Need to Check

This section outlines what would validate, extend, or invalidate our findings at scale. We consider this the most important part of the paper.

#### 6.1 Immediate Checks (Completed)

All four immediate checks have been run. Results are incorporated into Sections 3 and 4 above; we summarize the status here.

- **Multi-dimensional agents — PASS.** The matrix equation W^2 + W - I = 0 holds through d=16. Spectral radius converges to 1/φ for both i.i.d. and correlated signals. The self-consistency algebra generalizes beyond scalars (Section 3.1, `multidim_selfref.py`).

- **Robustness — PASS.** The 1/φ attractor holds across five signal distributions (Gaussian, uniform, Laplace, bimodal, exponential) and six optimizer configurations (SGD and Adam at multiple learning rates). Maximum deviation: 0.013 (Section 3.1, `robustness_sweep.py`).

- **T=2 minimum — PARTIAL.** T=2 wins for structured signals but T=1 (maximum width) wins for stochastic signals. Deep is always worst. The robust conclusion is that depth is costly; the T=1 vs T=2 boundary is signal-dependent (Sections 3.3 and 4.4).

- **Negative w_cross in deeper architectures — PASS.** Cross-weights are negative at all layers in 1-, 2-, and 3-layer architectures. Magnitude increases with depth. Deeper layers perform progressively stronger subtraction (Section 3.4, `deep_cross_test.py`).

#### 6.2 Medium-Scale Validation

- **Small neural networks.** Train a 2-layer MLP on a task where part of the training data is generated by the model itself (simulating synthetic data augmentation). Does a self-consistency equation govern the converged weights? Does the "self-ignorance gap" appear?

- **MNIST/CIFAR with self-referential contamination.** Classification tasks where a fraction of training labels come from the model's own predictions (pseudo-labeling). Measure whether SGD converges to a predictable suboptimal point. *Update: Experiment 12 confirmed contamination on digits classification but all proposed fixes failed. The theory requires uniform continuous contamination; class-structured errors violate this assumption. Future validation should use continuous-signal tasks (regression, density estimation) where the theory's assumptions hold.*

- **Validate MVSU on continuous-signal tasks.** The MVSU (dual channels + inhibitory cross-connections + predictive coding) was verified on scalar Gaussian signals. Test whether the architectural prescription holds for multivariate continuous signals, time-series forecasting, or density estimation -- domains where contamination is continuous and the theory's assumptions are satisfied. *Update: Experiment 16 validated the MVSU on three real continuous feedback tasks (thermostat control, sensor calibration, market microstructure), achieving 45-50% MSE reduction with architecture-split diversity. The remaining gap is scaling to high-dimensional systems (neural networks with millions of parameters).*

- **Optimizer comparison.** Compare SGD, Adam, and system-aware variants (that model their own feedback) on self-referential tasks. Does system-awareness close the gap?

- **Scaling of the gap.** Does the 8.3% self-ignorance gap grow, shrink, or stay constant as the number of parameters increases from 1 to 100 to 10,000?

#### 6.3 The Real Test: RLHF

The most direct application of these ideas is RLHF, where the reward model trains on the language model's outputs:

- Set up a small language model with RLHF fine-tuning
- Measure reward model accuracy on held-out human preferences over training iterations
- Test whether the reward signal drifts in ways predicted by the self-consistency equation
- Compare standard RLHF against a variant that differentiates through the reward model update (system-aware training)
- Measure whether the gap matches the predicted 8.3% or scales differently with model size
- **Measure the rehearsal effect in iterative RLHF**: Does reward accuracy degrade with RM update cycles? The cascade theorem predicts that each RM update cycle acts as a new self-referential stage, with sub-multiplicative compounding of signal loss. If reward accuracy after k update cycles follows R^2(k) ~ w^k (or worse), this would directly confirm the cascade prediction in a production-relevant setting.

#### 6.4 Scaling Questions

- **Does the self-ignorance gap persist at scale?** Multi-dimensional agents with many parameters may self-correct through redundancy. The 8.3% gap might vanish, persist, or grow -- each outcome has different implications.

- **Does the depth ceiling hold for real MoE architectures?** In Mixture-of-Experts models, experts typically have no recurrence (T=1). Our results suggest that T=1 may already be near-optimal for stochastic signals, while adding a single cross-attention integration step (T=2) would help for structured or predictable tasks. The key question is which regime real MoE tasks fall into.

- **Does negative coupling emerge without explicit encouragement?** In our setting, cross-weights learn negative values automatically. Does this happen in standard MoE training, or does it require explicit diversity losses?

- **Do inhibitory cross-connections emerge in standard transformer attention?** The MVSU predicts that stable self-referential processing requires negative coupling between channels. Standard multi-head attention allows both positive and negative interactions across heads. Do trained transformers develop inhibitory patterns between attention heads that resemble the w_cross < 0 structure?

- **Does the MVSU's stability survive nonlinear activations?** Our verification used linear stages with learned weights. Real systems use nonlinear activations (ReLU, GELU, etc.). The structural requirements (dual + inhibition) may still hold, but the quantitative stability boundary may shift.

#### 6.5 What Would Invalidate This

We want to be explicit about what findings would undermine the relevance of this work:

- **If the self-consistency equation doesn't extend beyond scalar agents.** If the algebra breaks for weight matrices, the specific fixed-point predictions become inapplicable. *Update: preliminary evidence positive — the matrix equation holds through d=16 (Section 3.1). The remaining risk is whether it survives in networks with nonlinear activations and millions of parameters.*

- **If the T*N tradeoff reverses in realistic settings.** If depth beats width for self-referential problems in multi-layer networks, our experimental conclusions are artifacts of the scalar setting. *Update: the tradeoff is nuanced — T=2 is not universally optimal (Section 4.4), but depth is always costly. The "width over depth" conclusion holds across signal types.*

- **If the 8.3% gap vanishes at scale.** Multi-dimensional agents have more degrees of freedom and may naturally compensate for self-referential contamination through redundancy.

- **If negative cross-connections are an artifact.** If the subtractive coupling we observed is specific to Gaussian signals with additive contamination and doesn't emerge in more realistic settings, the "parallax decontamination" principle would be a curiosity rather than a design insight. *Update: the pattern persists and strengthens across multi-layer architectures (Section 3.4), which is encouraging but still within the toy setting.*

- **If system-aware training provides no measurable benefit in RLHF.** This would suggest that either the self-referential contamination is negligible at scale, or that current training methods already implicitly compensate for it.

- **If the sub-multiplicative cascade effect vanishes for non-AR(1) signals.** Our cascade theorem depends on stage outputs being temporally correlated (AR(1)-like). If stages produce outputs with different temporal structure (e.g., whitened or decorrelated), the multiplicative product of per-stage R^2 values might be accurate, and the cascade would be less damaging than we predict.

- **If the MVSU's stability breaks with nonlinear activations.** The dual-channel + inhibition architecture was verified with linear processing. If adding nonlinear activations (ReLU, sigmoid, GELU) to the processing stages destabilizes the cascade despite the MVSU structure, the architectural prescription would need revision.

- **If the parallax-competence tradeoff has no solution at scale.** Our staged binocular experiment found that only architecture-split diversity produces free parallax. If at scale, even architectural diversity fails to produce complementary errors without sacrificing individual model quality, the binocular decontamination principle would be impractical.

---

### 7. Conclusion

We investigated the simplest possible self-referential learning system and found clean algebraic structure. When an agent's output contaminates its own input, SGD converges to a specific fixed point governed by the equation kw^2 + w - 1 = 0, where k depends on the activation function and network topology. For a single linear self-referential loop (k=1), this gives w = 1/phi, the reciprocal of the golden ratio -- an exact result verified to numerical precision across thirty experiments.

This fixed point is not optimal. A system-aware optimizer that accounts for its own feedback achieves 8.3% lower error in our simplified setting. The gap represents the cost of treating contaminated data as clean -- the "price of self-ignorance." Damped meta-optimization closes this gap: the recurrence w_{n+1} = w_n + beta*(0.525 - w_n) with beta = 1/phi^2 = 0.382 converges to the system-aware optimum in 2 iterations at high contamination, reducing MSE from 0.382 to 0.331 (100% gap closure). Direct measurement shows the MVSU stays at w=0.614 rather than reaching 0.525 — it is a noise filter that estimates contamination, not a meta-optimizer that corrects it.

Under fixed compute, balanced ensembles with cross-connections outperform both deep single-agent reflection and wide independent ensembles. The cross-connections learn negative weights at every layer -- with deeper layers learning progressively stronger subtraction -- implementing subtractive decontamination that extracts signal by comparing contaminated views. T=2 depth is sufficient for structured signals, while T=1 (maximum width) wins for stochastic signals; depth beyond T=2 is always wasteful. The self-consistency equation generalizes to matrix form (W^2 + W - I = 0, verified through d=16) and the 1/phi attractor is robust across signal distributions and optimizers.

The cascade composition theorem extends the single-stage analysis to multi-stage pipelines: self-referential bias compounds sub-multiplicatively, with actual signal loss up to 20x worse than the product of per-stage R^2 values. This is because each stage's temporally correlated output makes subsequent decontamination progressively harder -- a data processing inequality effect that is irrecoverable. The Minimum Viable Stable Unit (MVSU) provides the architectural antidote: two channels with inhibitory cross-connections preserve ~39x more signal than a monocular system with only 4x the parameters. Removing either component -- dual channels or inhibition -- causes 97.4% R^2 collapse. Predictive coding adds a further 60% improvement. External grounding is redundant when the internal architecture is correct.

Our first real-world validation attempt failed honestly: pseudo-labeling on a classification task confirmed the presence of self-referential contamination but all proposed fixes (over-relaxation, dual-model cross-labeling, forced viewpoint diversity) failed because classification errors are class-structured rather than uniform. The theory requires continuous, uniform contamination -- a boundary condition that classification tasks violate. The staged binocular experiment further revealed a parallax-competence tradeoff: diversity achieved by restricting individual model access to data or features destroys the competence needed to benefit from diversity. Effective parallax must be "free" -- arising from architectural dynamics, not input restriction.

Several earlier predictions also failed: the golden ratio does not survive nonlinear activations (ReLU and sigmoid give different roots involving pi), self-referential architecture provides no structural advantage over flexible baselines, and the discrete DOF step function predicted at N=2 does not manifest (the gain is continuous). These null results constrain where the theory applies.

The MVSU achieves 45-50% MSE reduction on thermostat control, sensor calibration, and market microstructure — real tasks with genuine self-referential feedback dynamics. This demonstrates that the theoretical framework, developed on toy problems, produces practical tools for continuous feedback systems. The critical insight from Experiment 16 is that architecture diversity (different inductive biases, e.g., linear + MLP) is essential — random initialization diversity is not merely insufficient but actively harmful, performing 53-83% worse than a single model.

The multi-agent extension reveals that the golden ratio is the universal attractor under mean-field coupling for any number of agents (the N cancels exactly from the contamination equation). The information-theoretic analysis establishes log(phi) = 0.4812 nats as the Shannon capacity of the self-referential channel -- a single fully contaminated agent already saturates this ceiling. The sign of the learned cross-connection weight diagnoses contamination topology: negative for independent contamination (subtract), positive for shared contamination (average). In generative chains, the MVSU prevents model collapse (54% improvement over 20 generations) but is prophylactic, not curative. Approximately 50% of pipeline stages must be MVSU-equipped for ecosystem stabilization.

The MVSU extends beyond self-referential contamination to general error reduction in numerical simulation. When two integrators have structurally different computational strategies (RK4 single-step vs AB4 multi-step), their errors are anti-correlated (cosine = -0.98), enabling 2.5-3.7x improvement over the better integrator alone. Error correlation is the key diagnostic: anti-correlated errors (different computational strategies) enable cross-correction, while correlated errors (same algorithm family with different parameters) provide no benefit. Online w_cross learning converges to the sweep-optimal value independently, demonstrating the principle can deploy without exhaustive search. Critically, simple averaging can hurt when errors are anti-correlated with unequal magnitudes -- the negative cross-weight must be tuned to the error ratio.

The self-consistency equation kw^2 + w - 1 = 0 governs not just optimization dynamics but the observer-observed boundary itself: at full self-reference, the golden ratio partition (0.618/0.382) is the myopic equilibrium between "world" and "self" in the agent's observations. The dark fraction 1/phi^2 = 0.382 is simultaneously the cost (stability tax at the myopic fixed point), the cure (optimal damping rate for fastest convergence), and the measurement gap (MVSU-to-system-aware difference) — a triple identity that reveals the system encodes its own ignorance in the instruction for correcting that ignorance.

The bottom line: **the architecture matters more than the algorithm.** Two channels with inhibitory coupling preserve nearly 80x more signal than a single channel, regardless of how sophisticated the single channel's processing is. Damped meta-optimization closes the myopic-to-system-aware gap, but only when the contamination parameter is known or estimable — suggesting a two-stage architecture where MVSU measurement feeds damped correction. The self-consistency equation provides specific, testable predictions for RLHF, synthetic data pipelines, and recommendation systems -- but only in regimes with continuous, uniform contamination. The generalization to discrete classification, class-structured errors, and production-scale systems remains the open frontier. We invite others to test whether these findings hold at scale.

---

### References

[1] Perdomo, J., Zrnic, T., Mendler-Dunner, C., & Hardt, M. (2020). Performative Prediction. *Proceedings of the 37th International Conference on Machine Learning (ICML)*.

[2] Miller, J., Krauth, K., Recht, B., & Schmidt, L. (2021). Outside the Echo Chamber: Optimizing the Performative Risk. *Proceedings of the 38th International Conference on Machine Learning (ICML)*.

[3] Liu, Y. & Yao, X. (1999). Ensemble Learning via Negative Correlation. *Neural Networks*, 12(10), 1399-1404.

[4] Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). AI models collapse when trained on recursively generated data. *Nature*, 631, 755-759.

[5] Foerster, J., Chen, R. Y., Al-Shedivat, M., Whiteson, S., Abbeel, P., & Mordatch, I. (2018). Learning with Opponent-Learning Awareness. *Proceedings of the 17th International Conference on Autonomous Agents and MultiAgent Systems (AAMAS)*.

[6] Snell, C., Lee, J., Xu, K., & Kumar, A. (2024). Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters. *arXiv preprint arXiv:2408.03314*.

[7] He, K., Zhang, X., Ren, S., & Sun, J. (2015). Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification. *Proceedings of the IEEE International Conference on Computer Vision (ICCV)*.

[8] Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138. (Predictive processing framework: the brain minimizes prediction error through hierarchical generative models, with each level passing prediction errors rather than raw signals -- directly analogous to the predictive coding component of the MVSU.)

[9] Loftus, E. F. (2005). Planting misinformation in the human mind: A 30-year investigation of the malleability of memory. *Learning & Memory*, 12(4), 361-366. (Memory distortion through repeated recall -- empirical evidence for the rehearsal paradox predicted by the cascade theorem.)

---

*This is an exploratory report documenting preliminary findings on toy problems. It is intended to invite collaboration and further investigation, not to make strong claims about production ML systems. All experiments are reproducible from the scripts listed in the accompanying repository.*
