# Inhibitory Dual-Channel Decontamination

**A practical guide to detecting and removing self-referential contamination in learning systems.**

When a model's output feeds back into its own training data, it poisons its own learning. This document explains why that happens, why one model cannot fix it alone, and how two models with a learned negative cross-connection solve the problem. An ML engineer should be able to implement this from this document alone.

---

## 1. The Problem

Machine learning systems increasingly operate in closed loops. A reward model scores outputs, those outputs enter the preference dataset, and the reward model retrains on data its own judgments helped create. A language model generates synthetic training data, and the next model generation trains on it. A recommendation engine surfaces items, users click on them because they were surfaced, and the clicks become training signal.

In all these cases, the model's output contaminates its future input. The model cannot distinguish genuine signal from its own echo. Standard SGD treats every gradient as if the data were independently generated, but in a feedback loop, the data distribution depends on the model itself. The result: the model converges to a suboptimal fixed point, systematically underestimating the true correction at each step. This is not a statistical problem -- more data does not fix it, because the contamination is structural. It manifests as reward hacking in RLHF, mode collapse in synthetic data pipelines, filter bubbles in recommendations, strategy collapse in self-play, and self-reinforcing bias in LLM self-evaluation.

The core mathematical fact: a single model observing its own contaminated output has one equation and two unknowns (the true signal and the contamination). It is structurally impossible for it to separate them.

---

## 2. The Principle

The fix requires two things: **two architecturally different models** and **a learned negative cross-connection** between them. This is not an ensemble. Averaging two models dilutes contamination but does not cancel it. Cross-subtraction cancels it.

The intuition is parallax. Two eyes at slightly different positions see the same object from different angles. The difference between their views reveals depth -- information neither eye has alone. Two models with different architectures develop different error patterns when exposed to the same contaminated signal. The shared component of their outputs is true signal. The part where they diverge is contamination artifact. A negative cross-weight subtracts the divergence, amplifying the agreement.

The critical insight from 17 experiments: the cross-weight must be **learned, not set by hand**, and it must be **negative**. When trained end-to-end, the cross-weight reliably converges to a negative value (approximately -0.26 in the linear toy setting, -0.6 to -0.8 in the RLHF bridge test). The magnitude tells you how much contamination existed. You do not need to know the contamination level in advance -- the system discovers it.

Why not just average? In controlled experiments, the dual-channel system with inhibitory cross-connections (MVSU) outperformed the naive ensemble (same two models, averaged) by +0.027 in correlation with ground truth. The ensemble captured less than a third of the available improvement. The remaining two-thirds came specifically from the negative cross-weight.

---

## 3. Why It Works -- The Reasoning

### The mathematical origin

When a linear predictor with weight w observes a signal contaminated by fraction alpha of its own previous prediction, the Wiener filter self-consistency condition yields:

```
alpha^2 * w^2 + w - 1 = 0
```

For full self-referential coupling (alpha = 1), the positive root is w = 1/phi = 0.618, where phi is the golden ratio. The predictor retains only 61.8% of the correction it should apply -- the remaining 38.2% is lost to self-contamination. This equation was verified to three decimal places across five signal distributions (Gaussian, uniform, Laplace, bimodal, exponential), six optimizer configurations, and matrix dimensions up to d=16. The bias is structural, not statistical: it persists regardless of dataset size, learning rate, or training duration.

### Why one model fails

A single model observes y(t) = s(t) + alpha * w * y(t-1), where s(t) is the true signal and the second term is self-contamination. The model has access only to y(t). It needs to recover s(t), but s(t) and the contamination term are confounded in y(t). One equation, two unknowns. No amount of capacity (wider layers, more parameters) resolves this -- a wider monocular system still has one observation channel and cannot separate what it sees from what it generated.

### Why two models with different architectures succeed

With two models receiving the same contaminated observation, you gain a second equation. Model A produces prediction A, contaminated by A's specific error pattern. Model B produces prediction B, contaminated by B's specific error pattern. If the architectures are sufficiently different, the error patterns are partially independent. The true signal is the part both models agree on. The contamination is the part where they diverge. Cross-subtraction removes the divergent contamination while preserving the common signal.

### Why inhibition is necessary

Without the negative cross-connection, dual channels are **useless**. In ablation experiments, removing the inhibitory coupling caused R-squared to collapse from 0.70 to 0.018 -- a 97.4% degradation, identical to running a single model. The reason: without cross-connections forcing differentiation, both channels receive the same gradient signal and converge to identical weights. They produce identical predictions with identical contamination. No diversity, no parallax, no decontamination. Positive cross-connections are even worse (R-squared = 0.008), because they amplify each channel's contamination into the other.

### Why architectural diversity matters more than random seed diversity

Same architecture with different random seeds produces correlated contamination patterns. In the linear setting, this is provable: same architecture means same inductive bias means same contamination direction. The cross-subtraction has nothing to subtract. In experiments, architectural diversity provided 2-5x more disagreement signal than seed diversity. For nonlinear networks, different seeds may provide some diversity due to symmetry breaking, but architectural diversity is the safer bet and is what the experiments validated.

### The evidence

Seventeen experiments across varying architectures, depths, contamination levels, and task types. Three random seeds each. The learned cross-weight converged to approximately -0.26 across all conditions in the linear setting. The RLHF bridge test (20 iterations, 3 seeds, 4 conditions) showed the MVSU outperforming single models by +0.037 in ground-truth reward correlation and outperforming naive ensembles by +0.027. The cross-weight learned to -0.6 to -0.8, indicating 60-80% contamination overlap being subtracted. On continuous feedback tasks (thermostat control, sensor calibration, market microstructure), the MVSU achieved 45-50% improvement over single-model baselines.

### Where it does NOT work

Classification with class-structured errors: when contamination is discrete and class-aligned rather than continuous and additive, the cross-subtraction mechanism breaks down. Problems without feedback loops: if the model's output does not influence its future training data, there is no self-referential contamination to remove. The dual-channel setup degrades gracefully to a mildly expensive ensemble, but provides no decontamination benefit. Single-use predictions with no retraining cycle also fall outside the scope.

---

## 4. The Recipe -- Step by Step

### Step 1: Identify the feedback loop

Draw your system as a diagram. Follow any arrow from your model's output back toward its input. Specifically ask: Does my model's prediction influence the data it will be retrained on? Does my model's action change the environment it observes? Does my model's output appear, directly or indirectly, in its future input? If yes to any of these, you have self-referential contamination. Proceed.

### Step 2: Build Model A

This is your primary model -- whatever you would normally use. A transformer reward model, a collaborative filtering recommender, a neural trajectory predictor. Train it as usual. This becomes Channel A.

### Step 3: Build Model B

Model B must be **structurally different** from Model A. Not just a different random seed -- a different architecture with a different inductive bias.

Good pairs (different inductive biases, different error patterns):
- Transformer + MLP
- CNN + RNN
- Collaborative filtering + content-based
- Physics-based model + learned model
- Deep narrow network + shallow wide network

Acceptable pairs (some structural diversity):
- Same architecture, different depth (4-layer vs. 12-layer)
- Same architecture family, different activation functions

Bad pairs (correlated error patterns, minimal decontamination):
- Same architecture, different random seeds
- Same architecture, different learning rates

The reason: same architecture equals same inductive bias equals same contamination direction. Cross-subtraction requires something different to subtract.

### Step 4: Add the cross-connection

A single learned scalar weight, initialized at -0.1, connecting each model's output to the other:

```python
w_cross = -0.1  # Initialize slightly negative as a hint

output_A = model_A(input)
output_B = model_B(input)
combined = output_A + w_cross * output_B
```

The initialization at -0.1 gives gradient descent a hint about the sign, speeding convergence. The exact initial value matters less than the sign. This is three lines of code on top of your existing training loop.

### Step 5: Combined prediction

The full combination with separate decontaminated channels:

```python
decontaminated_A = raw_A - w_cross * raw_B
decontaminated_B = raw_B - w_cross * raw_A
output = 0.5 * (decontaminated_A + decontaminated_B)
```

Or equivalently in the simpler formulation: `output = output_A + w_cross * output_B`.

### Step 6: Train end-to-end

Train both models and w_cross simultaneously using your standard loss function and optimizer. The models learn to produce useful predictions; w_cross learns how much contamination to subtract. No hand-tuning required. The system finds its own optimal inhibition level through gradient descent.

### Step 7: Monitor w_cross

The learned cross-weight is your contamination diagnostic:

| w_cross value | Interpretation |
|---------------|----------------|
| Near 0 | Minimal contamination, or models too similar to detect it |
| -0.1 to -0.3 | Moderate contamination; inhibition providing mild benefit |
| -0.3 to -0.6 | Significant contamination; inhibition essential |
| -0.6 to -0.8 | Heavy contamination (observed in RLHF); inhibition critical |
| Below -1.0 | Something is wrong; models may be adversarial |

If w_cross stays near zero: either your system has no significant feedback contamination (good news), or your two models are too architecturally similar (try a more different Model B).

### Step 8: Parameter-matched baseline

Always compare against a single model with the same total parameter count as both models combined. If your dual-channel system has 2x the parameters of Model A, your baseline must be a single model with 2x hidden units. If the single-2x model matches the dual model, your improvement came from capacity, not decontamination. In all experiments, the MVSU consistently beat the parameter-matched single model.

---

## 5. Diagnostic Signals

Three signals tell you the system is working:

**1. w_cross goes and stays negative (below -0.1).** This is the primary signal. A negative learned cross-weight means the system found contamination to subtract. The more negative, the more contamination existed and the more benefit you are getting.

**2. The MVSU outperforms the ensemble average of the same two models.** If you average Model A and Model B without the cross-subtraction, you get a naive ensemble. If the MVSU (with learned negative cross-weight) beats the ensemble, the improvement is from decontamination, not capacity. In RLHF experiments, the MVSU gave +0.037 over single model while the ensemble gave only +0.010.

**3. The performance gap grows with feedback strength.** Early in training (low contamination), the MVSU and single model perform similarly. As the feedback loop tightens and contamination rises, the MVSU's advantage increases. If you plot performance versus iteration count or contamination fraction, the gap should widen.

**If none of these signals appear:** Either there is no feedback loop in your system (verify Step 1), or your two models are not sufficiently architecturally diverse (try a more structurally different Model B), or you are working on a classification problem with class-structured errors (a known limitation).

---

## 6. Application Quick-Reference

| Domain | Feedback Loop | Model A | Model B | Expected Benefit | Difficulty |
|--------|---------------|---------|---------|------------------|------------|
| **RLHF** | Reward model trains on policy outputs shaped by reward model | Transformer reward head | MLP reward head (different depth/width) | +3-5% reward accuracy; w_cross reveals contamination level | Easy (1-2 weeks) |
| **Synthetic Data** | Next-gen model trains on current-gen outputs | Generator model | Different architecture generator | Delayed model collapse; cross-filter identifies collapsing samples | Medium (2-4 weeks) |
| **Recommendations** | Users click on recommended items; clicks retrain model | Collaborative filtering | Content-based filtering | Improved diversity without sacrificing relevance; w_cross quantifies filter bubble | Medium (2-4 weeks) |
| **Active Learning** | Model selects which data to label; selections bias future training | ResNet / CNN | Vision Transformer / different family | 30-50% faster coverage of rare cases; finds unknown unknowns | Easy (1 week) |
| **LLM Self-Eval** | Model judges own outputs; judgments shape future training | LLM-A (e.g., different size) | LLM-B (different architecture or training history) | Reduced self-reinforcing bias; cross-evaluation catches model-specific errors | Easy (1-2 weeks) |
| **Self-Play RL** | Agent plays against itself; alpha = 1.0 by construction | Agent architecture A | Agent architecture B (different network family) | Reduced strategy collapse; agents cannot co-adapt into shared blind spots | Easy-Medium (2-4 weeks) |
| **Financial Trading** | Trading signals move prices; moved prices become training data | Momentum-based model | Mean-reversion model | w_cross measures self-generated market impact; cleaner signal extraction | Medium (4-8 weeks) |
| **Control Systems** | Controller action changes the state the controller observes | Model-predictive controller | PID or different control architecture | Active damping of self-excited oscillations; learned (not hand-tuned) inhibition | Easy (research) / Hard (deployment) |
| **Scientific Instruments** | Measurement device disturbs what it measures | Measurement method A | Measurement method B (different physical principle) | Cross-calibration removes instrument-specific disturbance; quantitative combination rule | Easy (measurements usually already exist) |

---

## 7. Common Mistakes

**Using same architecture with different random seeds.** In the linear setting, this provably fails -- models converge to identical contamination patterns. For deep networks, different seeds provide some diversity, but architectural diversity provides 2-5x more disagreement signal. Use structurally different models.

**Averaging instead of cross-subtracting.** The naive ensemble (average two models) captures some benefit from increased capacity but misses the decontamination. In RLHF experiments: ensemble gave +0.010 over single model; MVSU gave +0.037. The extra +0.027 -- more than two-thirds of the total improvement -- comes from the negative cross-weight. Averaging dilutes contamination. Subtracting cancels it.

**Not running a parameter-matched baseline.** Your dual-channel model has roughly 2x the parameters. Compare against a single model with the same total parameter count. Without this control, you cannot distinguish decontamination benefit from capacity benefit.

**Using a fixed cross-weight instead of learning it.** Setting w_cross = -0.25 (the linear-setting value) works acceptably but is suboptimal. In RLHF, the optimal learned w_cross was -0.6 to -0.8 -- much more aggressive than the linear theory predicts. Nonlinear settings have more contamination overlap. Let the system learn its own cross-weight.

**Using more than two channels.** Two channels is the minimum necessary and close to optimal. Three channels gave marginal improvement at 50% more compute. Four channels gave no additional improvement. The principle is parallax: you need two viewpoints. Additional viewpoints add coordination cost without proportional benefit.

---

## 8. The Evidence Base

The experimental foundation spans 17 controlled experiments, each run with 3 random seeds, across scalar and matrix systems up to dimension d=16.

**What is proven (in the toy setting):** The self-consistency equation kw^2 + w - 1 = 0 is exact for linear self-referential agents, verified to three decimal places. The equation is distribution-independent (Gaussian, uniform, Laplace, bimodal, exponential) and optimizer-independent (SGD, Adam, varying learning rates). Maximum deviation from theoretical prediction: 1.3%. Dual channels with inhibitory cross-connections are structurally necessary -- removing either causes 97.4% R-squared collapse. The learned cross-weight converges to approximately -0.26 across all tested conditions.

**What is validated on a realistic loop:** The RLHF bridge experiment (GPT-2 scale, synthetic preferences, known ground truth, 20 iterations) confirmed that dual reward models with learned inhibitory coupling outperform single reward models (+0.037) and naive ensembles (+0.027). The cross-weight learned to -0.6 to -0.8.

**What remains promising but unproven at scale:** Whether the specific improvement magnitudes transfer to production-scale RLHF, recommendation systems, or synthetic data pipelines. The qualitative finding (structural decontamination via cross-subtraction) is robust across all tested conditions. The quantitative magnitudes may differ at scale.

**Key numbers:** 45-50% improvement on continuous feedback tasks. 97.4% collapse when inhibition removed (ablation). 4-22% improvement range across contamination levels. Cross-weight universally negative across 17 experiments.

---

## 9. Reference Implementation

The file `python/mvsu.py` (232 lines, pure NumPy, no external dependencies) provides a complete implementation.

### Key classes

**`LinearPredictor`** -- A simple linear model (y = Wx + b) with forward pass, gradient update, and a `copy()` method for creating a second channel with different initialization.

**`MLPPredictor`** -- A single-hidden-layer MLP with tanh activation. Same interface as LinearPredictor. Use this as Model B when Model A is a LinearPredictor (or vice versa) to get architectural diversity.

**`MVSUPredictor`** -- The dual-channel inhibitory wrapper. Takes two predictor objects (any class with `predict()` and `update()` methods). Manages the cross-connection weight and routes gradients through the cross-subtraction during backpropagation. If only one predictor is provided, it creates a copy with different initialization automatically.

**`MVSUEnsemble`** -- N-channel generalization with pairwise inhibitory connections. An NxN matrix of cross-weights (diagonal zeroed). Use this only if you have a specific reason to go beyond two channels.

### Usage example

```python
from mvsu import MVSUPredictor, LinearPredictor, MLPPredictor

# Step 1: Create two architecturally different predictors
model_A = LinearPredictor(d_in=5, d_out=1, seed=42)
model_B = MLPPredictor(d_in=5, d_out=1, d_hidden=16, seed=99)

# Step 2: Wrap in MVSU with learned cross-connection
mvsu = MVSUPredictor(model_A, model_B, w_cross_init=-0.1)

# Step 3: Train in your feedback loop
for t in range(num_timesteps):
    observation = get_contaminated_observation()  # contains echo of past predictions
    prediction = mvsu.predict(observation)
    true_signal = get_ground_truth()              # from held-out data
    loss = mvsu.update(observation, true_signal, lr=0.01)

# Step 4: Check the diagnostic
print(f"Learned w_cross: {mvsu.w_cross_value:.3f}")
# If negative: contamination detected and being removed
# If near zero: no feedback contamination (or models too similar)
```

---

*Based on 17 experiments (3 seeds each), the RLHF bridge experiment (20 iterations, 4 conditions), and ablation studies documented in this project's analysis directory. Reference implementation: `python/mvsu.py`. All experimental code available in `python/experiments/`.*
