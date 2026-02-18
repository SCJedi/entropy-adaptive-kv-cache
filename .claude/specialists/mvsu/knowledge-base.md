# Knowledge Base: MVSU Specialist

## Overview

Self-referential decontamination using inhibitory dual-channel architectures. When a system's output feeds back into its training data, a single model cannot separate signal from its own echo. The MVSU pattern — two architecturally different models with learned negative cross-connections — solves this by parallax.

**Core insight:** One equation, two unknowns (signal + contamination) = unsolvable. Two channels with different contamination histories = two equations = solvable through inhibitory subtraction.

## Key Definitions

**Self-referential contamination:** The model's output influences its future training data. The data distribution depends on the model itself. Examples: RLHF (reward model trains on model outputs), synthetic data (model trains on own generations), recommendations (user behavior shaped by recommendations).

**Feedback loop types:**
- Direct: output → same model's input (autoregressive generation, self-play)
- Indirect: output → environment → input (RLHF, recommendations, market impact)

**MVSU (Minimum Viable Stable Unit):** Two channels with inhibitory cross-connections. The minimum architecture that does not catastrophically degrade through self-referential feedback.

**Inhibitory cross-connection (w_cross):** Learned negative weight between channels. Each channel subtracts a fraction of the other channel's output. Implements parallax decontamination: where channels agree = signal, where they disagree = contamination.

**Architectural diversity vs seed diversity:** Different model architectures (Linear + MLP, CNN + RNN) provide genuine parallax. Different random seeds on same architecture converge to same contamination pattern (proven for linear case, verified on real tasks). **Architecture diversity is essential.**

**The self-consistency equation:** kw² + w - 1 = 0. Characterizes where SGD converges in self-referential systems. For k=1 (linear, single feedback loop), w = 1/φ = 0.618 (golden ratio). For k neighbors, w = (-1 + sqrt(1+4k))/(2k).

**Decontamination vs ensemble averaging:** Ensembles average predictions (dilutes contamination). MVSU subtracts contamination (cancels it). RLHF experiment: ensemble +0.010, MVSU +0.037. The extra +0.027 is specifically from inhibition.

## Core Theory

### The Self-Consistency Equation

When an agent observes y(t) = s(t) + α·pred(t-1) and updates via SGD:

1. Variance of observation: Var(y) = 1/(1 - w²)
2. Optimal filter: w = Cov(s,y)/Var(y) = 1 - w²
3. Rearranging: w² + w - 1 = 0
4. Solution: w = 1/φ = 0.618

**Evidence tier: Proven.** Verified across 17 experiments, 3+ seeds, multiple distributions (Gaussian, uniform, Laplace, bimodal, exponential), multiple optimizers (SGD, Adam at various learning rates). Maximum deviation from 1/φ: 0.013 (2.1%).

### Why One Model Fails

A single model observing contaminated data has one equation and two unknowns:
- Unknown 1: true signal s(t)
- Unknown 2: contamination α·pred(t-1)
- Equation: y(t) = signal + contamination

The data processing inequality: information lost at this bottleneck is irrecoverable. No amount of capacity, depth, or training data fixes this structural problem.

### Why Two Models with Inhibition Succeed

Two channels A and B with different architectures:
- Channel A: y_A(t) = s(t) + α·w_A·y_A(t-1)
- Channel B: y_B(t) = s(t) + α·w_B·y_B(t-1)

With different initial conditions or inductive biases, the contamination terms α·w_A·y_A and α·w_B·y_B are partially independent. Now we have two equations and two unknowns.

**Inhibitory cross-connection:**
```
pred_A = raw_A - w_cross * raw_B
pred_B = raw_B - w_cross * raw_A
```

Where channels agree (high correlation in raw predictions) = shared signal.
Where channels disagree = channel-specific contamination.
Subtraction amplifies signal, cancels disagreement.

**Evidence tier: Proven.** Ablation study: removing inhibition causes 97.4% R^2 collapse. Dual channels WITHOUT inhibition perform identically to single channel (both R^2 = 0.009). w_cross converges to negative values in all 17 experiments: typically -0.26 for linear toy setting, -0.6 to -0.8 for RLHF setting.

### The Myopic vs System-Aware Gap

SGD treats each gradient step as if data distribution were fixed. But distribution depends on model through feedback. Result: systematic bias.

- **Myopic optimum:** w = 1/φ = 0.618, R² = 0.618
- **System-aware optimum:** w = 0.525, R² = 0.670
- **Gap:** 8.3% in explained variance

This is the "price of self-ignorance" — the cost of treating contaminated data as clean.

**Evidence tier: Verified.** Exact calculation matches simulation on toy setting. Not tested at scale. The 8.3% value is specific to k=1, α=1. General principle (myopic ≠ optimal) is robust.

### The Golden Ratio as Myopic Fixed Point

For k=1 (single linear self-referential loop), the positive root of w² + w - 1 = 0 is:

w = (-1 + √5)/2 = 1/φ ≈ 0.618034

**Domain of validity:** Linear agents, single feedback loop, additive contamination. The exact value 1/φ does NOT transfer to:
- Nonlinear activations (ReLU: w ≈ 0.394, involves π not φ)
- Multiple feedback paths (k > 1: w decreases with k)
- Structured contamination (classification errors)

**What does transfer:** The self-consistency equation form kw² + w - 1 = 0, the concept of a myopic fixed point distinct from the true optimum, and the architectural principle (dual + inhibition).

**Evidence tier: Proven** for the linear case. **Established** that the quantitative equation does not transfer to nonlinear systems. **Verified** that the architectural principle does transfer (RLHF experiment).

### Where the Equation Applies and Where It Doesn't

**Applies (continuous additive feedback):**
- Regression with feedback
- Continuous control (thermostat, sensor calibration)
- Market impact (trading algorithms)
- RLHF (reward signals are continuous)
- Density estimation, time-series forecasting
- Any setting where contamination is: continuous, additive, approximately uniform

**Does NOT apply (structured or discrete feedback):**
- Classification with class-structured errors (pseudo-labeling FAILED)
- Discrete decisions with correlated errors
- Feedback that is multiplicative or nonlinear in complex ways
- Adversarial contamination (the model structure is exploited)

**Evidence tier: Verified** via honest null result (Experiment 12: pseudo-labeling failure).

## The Recipe: 5-Step Practical Method

From the applications roadmap and validated on real continuous feedback tasks:

### Step 1: Identify Feedback Loop

Draw your system. If any arrow goes from output back to input, you have self-referential contamination.

Diagnostic questions:
- Does your model's prediction influence data it will retrain on?
- Does your model's action change the environment it observes?
- Does your model's output appear (directly/indirectly) in future input?

**Estimate α (contamination strength):**
- RLHF: fraction of RM training data that is model-generated
- Synthetic data: count(synthetic)/count(total)
- Recommendations: clicks_on_recommended / clicks_on_organic
- Self-play: α = 1.0 by definition
- Pseudo-labeling: count(pseudo_labels)/count(total_labels)

**Rule of thumb:** α < 0.3 = monitor; α ∈ [0.3, 0.6] = intervene; α ≥ 0.6 = MVSU essential.

### Step 2: Build Two Structurally Different Models

**Critical:** Different architectures, not different seeds.

**Good pairs:**
- Transformer + MLP
- CNN + RNN
- Linear + MLP (simplest, proven on real tasks)
- Collaborative filtering + content-based
- Physics model + learned model
- Deep narrow + shallow wide

**Acceptable pairs:**
- Same architecture, different depth (4-layer vs 12-layer)
- Same architecture, different width (64-hidden vs 256-hidden)

**Bad pairs (proven to fail):**
- Same architecture, different random seeds
- Same architecture, different learning rates
- Feature-split (cripples individual models)
- Data-split (cripples individual models)

**Evidence tier: Verified.** Experiment 16: same-architecture different-seed performed 53-83% WORSE than single model on all three real-world tasks. Architecture-split (linear + MLP) achieved 45-50% improvement.

### Step 3: Add Learned Cross-Subtraction Weight

```python
# Initialize
w_cross = -0.1  # Slightly negative hint

# Forward pass
output_A = model_A(input)
output_B = model_B(input)
combined = output_A + w_cross * output_B

# Update w_cross via gradient descent on held-out loss
# or: w_cross = 0.9 * w_cross + 0.1 * (-cov(A,B)/var(B))
```

The initialization at -0.1 speeds convergence by hinting at the sign. Exact value matters less than the sign.

### Step 4: Train End-to-End

Train both models and w_cross simultaneously. Standard loss (MSE for regression, reward accuracy for RLHF). No hand-tuning required. The system finds its own optimal inhibition level.

**Important:** Train on uncontaminated held-out data if possible. For RLHF: held-out human preferences, NOT reward model scores.

### Step 5: Monitor w_cross

w_cross is your contamination diagnostic.

| w_cross value | Interpretation |
|---------------|----------------|
| Near 0 | Minimal contamination (or models too similar) |
| -0.1 to -0.3 | Moderate contamination; inhibition providing benefit |
| -0.3 to -0.6 | Significant contamination; inhibition essential |
| -0.6 to -0.8 | Heavy contamination (RLHF level); inhibition critical |
| Below -1.0 | Something wrong; models may be adversarial |

**If w_cross stays near zero:** Either no significant feedback contamination (good), or models too similar (try more architectural diversity).

**If w_cross goes negative:** It's working. More negative = more contamination detected and removed.

## Applications Reference

### High-Confidence Applications (Evidence Tier: Verified or High)

| Application | Feedback Loop | Model A | Model B | Expected Benefit | Difficulty | Tier |
|------------|---------------|---------|---------|------------------|------------|------|
| RLHF | RM trains on model outputs | Transformer reward head | MLP reward head | +3-5% reward accuracy | 1-2 weeks | **Verified** |
| Thermostat control | Heater responds to prediction | Linear | MLP | +50% MSE reduction | 1 week | **Verified** |
| Sensor calibration | Auto-calibration drift | Linear | MLP | +45% MSE reduction | 1 week | **Verified** |
| Market microstructure | Trading creates market impact | Linear | MLP | +47% MSE reduction | 1 week | **Verified** |
| LLM self-evaluation (RLAIF) | Model judges own outputs | LLM_A evals LLM_B outputs | LLM_B evals LLM_A outputs | Reduced self-reinforcing bias | 1-2 weeks | High (same mechanism as RLHF) |

### Medium-Confidence Applications (Evidence Tier: Established or Conjectured)

| Application | Feedback Loop | Model A | Model B | Expected Benefit | Difficulty | Tier |
|------------|---------------|---------|---------|------------------|------------|------|
| Synthetic data | Model trains on own generations | Model_A generates for Model_B | Model_B generates for Model_A | Delayed model collapse | 2-4 weeks | Medium-High |
| Recommendations | Users shaped by past recs | Collaborative filtering | Content-based | Improved diversity | 2-4 weeks | Medium |
| Self-play RL | Agent plays itself | Agent A plays B | Agent B plays A | Reduced strategy collapse | 2-4 weeks | Medium |
| Active learning | Model selects what to label | ResNet uncertainty | ViT uncertainty | 30-50% faster coverage | 1 week | Medium-High |
| Ad ranking | Click data from shown ads | Deep CTR model | Simple logistic | 1-3% ROI improvement | 4-8 weeks | Medium |
| Autonomous driving | AV predictions change traffic | Physics-based trajectory | Learned behavior | Better mixed-traffic prediction | 8-16 weeks | Low-Medium |

## Diagnostic Signals

### Primary Signal: w_cross < -0.1

**Meaning:** Contamination detected and being removed.

**Interpretation guide:**
- Linear toy setting: typically converges to -0.26
- RLHF setting: converges to -0.6 to -0.8
- Real continuous tasks: converges to -0.13 to -0.23

Magnitude indicates contamination severity. More negative = more contamination overlap between channels = more aggressive subtraction needed.

### Secondary Signal: MVSU > Ensemble Average

Compare three baselines:
1. Single model (parameter-matched: 2x hidden units)
2. Ensemble average (same two models, w_cross = 0)
3. MVSU (same two models, learned w_cross)

**If MVSU beats ensemble:** Inhibition is doing real work beyond capacity increase.

**RLHF results:** Single +0.000, Ensemble +0.010, MVSU +0.037.
The +0.027 gap between ensemble and MVSU is the decontamination benefit.

### Tertiary Signal: Performance Gap Grows with Feedback Strength

Train across multiple α values. Plot MVSU advantage vs α.

**Expected pattern:** Advantage should increase with α. At α ≈ 0, MVSU ≈ ensemble (no contamination to remove). At α → 1, MVSU advantage maximizes.

**If pattern doesn't appear:** Either contamination isn't the bottleneck, or models aren't diverse enough.

## Known Limitations

### Where MVSU Does NOT Work

**Classification with structured errors (Evidence: Verified Failure):**
When model confuses class 3 with class 8 systematically, errors are correlated within class pairs. MVSU assumes uniform continuous contamination. Class-structured errors violate this. Experiment 12 (pseudo-labeling) confirmed: all fixes failed.

**Solution:** Use MVSU only for continuous-signal tasks (regression, density estimation, control, reward modeling with continuous rewards).

### Quantitative Equation Does Not Transfer to Nonlinear Systems

The exact value 1/φ = 0.618 applies only to linear case. ReLU gives 0.394 (involves π). Sigmoid gives 0.384. The architectural principle (dual + inhibition) transfers; the numbers don't.

**What to use:** Let w_cross learn. Don't hard-code -0.26. The system finds its own optimal inhibition level.

### Same-Seed Models Fail (Evidence: Verified)

Experiment 16: two linear models with different random seeds performed 53-83% WORSE than single model. Linear loss landscape has single basin. Different starting points converge to same optimum. No parallax.

**Solution:** Architectural diversity required. Linear + MLP, or transformer + MLP, or different depths/widths.

### Not Tested at Scale (>1B Parameters)

All experimental validation used:
- Scalar/matrix agents (dimensions ≤ 16)
- Small networks (≤ 100 parameters)
- GPT-2 scale RLHF (planned but not yet run)

**Open question:** Does the 8.3% gap persist, grow, or vanish with overparameterization?

## Evidence Tiers

**Proven (17+ experiments, 3+ seeds, distribution/optimizer independent):**
- Self-consistency equation kw² + w - 1 = 0 for linear case
- w = 1/φ for k=1, verified to 0.013 max deviation
- Matrix generalization W² + W - I = 0 through d=16
- Dual channels necessary (97.4% collapse without)
- Inhibitory cross-connections necessary (97.4% collapse without)
- w_cross reliably learns negative values (-0.26 typical, -0.6 to -0.8 in RLHF)

**Verified (tested in specific experiments with clear positive results):**
- MVSU beats ensemble on RLHF (+0.027 beyond capacity)
- MVSU achieves 45-50% improvement on real continuous tasks (thermostat, sensor, market)
- Architecture diversity essential; random seed diversity fails
- Predictive coding adds 60% improvement but not structurally necessary
- Sub-multiplicative cascade degradation (20x worse than product)
- Negative w_cross at all depths, magnitude increases with depth

**Established (supported by theory and partial experiments):**
- 8.3% myopic vs system-aware gap for k=1, α=1
- External grounding redundant when dual+inhibition present
- Cascade theorem (stages compound sub-multiplicatively)
- w_cross as contamination diagnostic

**Conjectured (theoretical prediction, untested or failed in specific settings):**
- The exact 8.3% gap persists at scale (untested)
- Quantitative equation for nonlinear activations (tested: FAILS, values change but form survives)
- Classification applications (tested: FAILS for class-structured errors)
- Transformer attention develops inhibitory patterns spontaneously (untested)

## Reference Implementation

Location: `python/mvsu.py` (231 lines, pure numpy)

### Classes

**LinearPredictor:** y = W @ x + b. Basic linear predictor with gradient descent update.

**MLPPredictor:** hidden = tanh(W1 @ x + b1); y = W2 @ hidden + b2. Two-layer MLP with tanh activation.

**MVSUPredictor:** Core MVSU wrapper. Takes two predictors (or creates second via `.copy()`), implements cross-inhibitory decontamination.

**MVSUEnsemble:** Generalizes to N >= 2 channels with pairwise inhibitory connections.

### Usage Example

```python
from mvsu import MVSUPredictor, LinearPredictor

# Create base predictor
base = LinearPredictor(d_in=5, d_out=1)

# Wrap in MVSU (automatically creates second channel with different seed)
mvsu = MVSUPredictor(base, w_cross_init=-0.1)

# Or provide explicit second channel with different architecture
base_A = LinearPredictor(d_in=5, d_out=1, seed=0)
base_B = MLPPredictor(d_in=5, d_out=1, d_hidden=16, seed=1)
mvsu = MVSUPredictor(base_A, base_B, w_cross_init=-0.1)

# Training loop
for t in range(T):
    pred = mvsu.predict(observation)
    loss = mvsu.update(observation, true_signal, lr=0.01)

    # Monitor contamination
    print(f"w_cross = {mvsu.w_cross_value:.3f}")
```

### Key Methods

- `predict(observation)`: Forward pass with cross-inhibitory decontamination
- `update(observation, true_signal, lr)`: Backprop and update all weights including w_cross
- `w_cross_value`: Property returning current inhibition weight (diagnostic)

## Quick Reference: Decision Framework

See `decision-framework.md` for full classification system. Summary:

**Step 1:** Is there a feedback loop? (Direct, indirect, or none)
**Step 2:** Contamination type? (Continuous additive = theory applies fully, discrete/structured = likely fails)
**Step 3:** Architecture options? (Must be structurally different, not just different seeds)
**Step 4:** Configuration (w_cross = -0.1 init, train end-to-end, monitor w_cross trajectory)

**The minimum viable experiment:** Three lines of code (init w_cross = -0.1, compute combined output, update w_cross by gradient descent). If w_cross goes negative, you had contamination. If it stays near zero, you learned something too.

## Parallax-Competence Tradeoff

**Problem:** How to create diverse models without crippling individual competence?

**Failed approaches (Experiment 13):**
- Feature-split (each model sees half the features): excellent parallax, crippled competence (-8.4%)
- Data-split (each model sees half the data): maximum parallax, weak competence (-1.5%)

**Successful approach (Experiment 16):**
- Architecture-split (different inductive biases, both see full data): moderate parallax, full competence (+45-50%)

**Key insight:** Diversity must be "free" — arising from architectural differences or learned dynamics, not from restricting model inputs. MVSU's inhibitory cross-connections create diversity through dynamics, not input restriction.

## Connection to Established Techniques

**Successive Over-Relaxation (SOR):** Numerical methods for self-referential linear systems. Over-relaxation corrects myopic bias by scaling gradient updates by ω > 1. MVSU architectural approach is more robust than scalar over-relaxation.

**Red-black Gauss-Seidel:** Split grid into two sets; each updates using only the other set's values. Breaks within-set self-reference. Direct analog: MVSU channels cross-label/cross-evaluate.

**Multigrid methods:** Coarse grid models large-scale error, informs fine grid. One coarse correction, return to fine grid. Analog: T=2 depth (one integration step), not deep unrolling.

**Instrumental Variables:** Each MVSU channel is an instrument for the other. Channel A's contamination partially independent of B's, conditional on signal. Inhibitory cross-connection implements IV second-stage regression.

**Predictive Coding (neuroscience):** Hierarchical prediction error passing. Each cortical level passes errors, not raw signals. Analog: MVSU with predictive coding component (system-aware optimization).

**Negative Correlation Learning:** Ensemble diversity through anti-correlation. MVSU learns negative correlation automatically through w_cross.

## Cascade Composition and the Rehearsal Effect

**Cascade theorem:** When self-referential stages are chained, degradation is sub-multiplicative. Each stage's AR(1) output (temporally correlated) makes next stage's decontamination harder. Penalty compounds.

**Measured ratio:** Actual R² is ~0.22 of predicted product at high α (5-7 stage cascade).

**Rehearsal effect:** Each memory recall adds a self-referential stage. After n recalls at α ≈ 1, only ~0.3% of original signal survives at n=5. Well-rehearsed memories feel vivid (low per-recall α) but are heavily confabulated (many recall stages).

**Implication for iterative RLHF:** Each RM update cycle is a new self-referential stage. The cascade theorem predicts reward accuracy degradation compounds sub-multiplicatively. After k update cycles: R²(k) ≲ w^k, often much worse.

**MVSU mitigation:** Dual-channel cascade retains ~8x more signal than monocular through 7-stage cascade (R² = 0.065 vs 0.008).
