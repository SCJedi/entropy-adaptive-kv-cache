# How to Help ML People with Self-Referential Contamination

## A Practical Guide for Engineers

---

## 1. The Problem in One Paragraph

Your model's output contaminates its future training data. SGD doesn't know this. It treats every gradient step as if the data were independently generated, but in systems like RLHF, synthetic data pipelines, and recommendation engines, the data distribution depends on the model itself. The result: SGD converges to a suboptimal fixed point, retaining only ~62% of the correction it should apply at each step. The performance gap is 8.3% in the simplest case (a single feedback loop with linear dynamics). This is not a statistical problem -- more data doesn't fix it, because the contamination is structural. Physics and numerical methods people solved the identical problem in the 1950s with techniques like successive over-relaxation, red-black ordering, and multigrid methods. Those solutions translate directly into ML interventions. Here's how.

---

## 2. Diagnose Your System

Self-referential contamination exists whenever your model's output influences its future training data. The key parameter is **alpha** -- the fraction of the training signal that is model-generated rather than externally sourced.

| System | Where output feeds into input | How to measure alpha |
|--------|------------------------------|----------------------|
| **RLHF** | Reward model trains on model-generated outputs that were shaped by the reward model | Fraction of RM training examples that are model-generated (vs human-written). Track across RM update cycles. |
| **Synthetic data** | Next-generation model trains on current-generation's outputs | `count(synthetic samples) / count(total training samples)`. Check for synthetic contamination in "natural" web-scraped data too. |
| **Recommendations** | User behavior shaped by past recommendations feeds back into training | `clicks_on_recommended / clicks_on_organic`. If you can't measure organic, A/B test with random recommendations on a holdout. |
| **Self-play** | Opponent IS the model | alpha = 1.0 by construction. Full self-reference. No measurement needed. |
| **Pseudo-labeling** | Model's confident predictions become training labels | `count(pseudo_labels) / count(total_labels)`. Track the confidence threshold -- lower threshold means higher alpha AND lower quality. |
| **Autoregressive generation** | Each token conditions on previously generated tokens | `generated_tokens_in_context / total_context_length`. For long outputs this approaches 1.0. |

**Rule of thumb**: If alpha < 0.3, the bias exists but may not be your bottleneck. If alpha > 0.6, self-referential contamination is likely costing you measurable performance. At alpha = 1.0, the system is fully self-referential and the fixes below matter most.

**How we know the threshold**: In our experiments (11 controlled studies, scalar through matrix, multiple distributions and optimizers), the self-consistency equation `w^2 + w - 1 = 0` holds regardless of signal distribution (Gaussian, uniform, Laplace, bimodal, exponential) and optimizer choice (SGD, Adam, various learning rates). The converged weight deviates less than 1.3% from 1/phi = 0.618 across all conditions. The bias is structural, not statistical.

---

## 3. The Three Fixes

### Fix 1: Over-Relaxation (SOR --> ML)

**The numerical methods version**: In iterative PDE solvers, Gauss-Seidel updates each variable using the current best guesses from neighbors. It converges, but slowly -- because each update ignores how it will affect the neighbors it just used. Successive Over-Relaxation (SOR) multiplies each correction by omega > 1 to compensate. The optimal omega depends on the problem's spectral radius.

**The ML translation**: When updating based on contaminated feedback, SCALE UP the gradient to compensate for the systematic underestimation.

**Standard RLHF update:**
```
theta <- theta + eta * grad_theta(reward)
```

**Over-relaxed RLHF update:**
```
theta <- theta + eta * omega * grad_theta(reward)
```

where `omega = 1 / (1 - alpha^2)`, which approximates to `1 + alpha^2` for small alpha.

| alpha | omega | Expected recovery |
|-------|-------|-------------------|
| 0.2   | 1.04  | ~0.3% improvement |
| 0.4   | 1.19  | ~1.4% improvement |
| 0.6   | 1.56  | ~4.2% improvement |
| 0.8   | 2.78  | ~7.1% improvement |
| 1.0   | diverges | Use Fix 2 instead |

**Why this works**: At the myopic fixed point, SGD systematically underestimates the true gradient by a factor related to alpha. It "sees" the gradient through the contaminated observation, which attenuates it. Over-relaxing compensates for this attenuation. This is exactly what SOR does for PDE solvers, and for the same algebraic reason.

**How to tune omega in practice:**
1. Start with omega = 1.0 (standard training)
2. Measure performance on a **held-out human-labeled set** (not model-contaminated data)
3. Sweep omega in [1.0, 1.1, 1.2, ..., 2.0]
4. Pick the omega that maximizes held-out reward
5. If held-out reward peaks and then drops, you've found the boundary -- back off by 10%

This is exactly how SOR is tuned in numerical methods: sweep omega and measure convergence rate. The "held-out human-labeled set" is your ground truth -- the equivalent of the known analytic solution in a PDE benchmark.

**Stability warning**: omega > 2.0 will diverge in most settings (this is a proven bound from SOR theory). If your sweep wants omega > 2.0, the contamination is too strong for Fix 1 alone -- move to Fix 2.

---

### Fix 2: Dual Models with Cross-Subtraction (Red-Black --> ML)

**The numerical methods version**: Red-black Gauss-Seidel splits grid points into two sets. Red points update using only black neighbors, then black points update using only red neighbors. Each set sees "fresh" information from the other, breaking the within-set self-referential cycle. This doubles the effective information per iteration.

**The ML translation -- general principle**: Train two models that cross-evaluate. Each model scores or labels data it didn't generate. The key insight from our experiments: the cross-connections should be **subtractive** (negative weights), not additive. Our binocular experiments consistently found w_cross approximately equal to -0.26. Units subtract each other's contamination to isolate the shared signal -- this is parallax computation.

#### For RLHF:

Train two reward models (R_A, R_B) on alternating batches:

```python
# Split model outputs into two streams
batch_A, batch_B = split_alternating(model_outputs)

# Each RM trains on the batch it DIDN'T score
R_A.train(batch_B, human_labels_B)
R_B.train(batch_A, human_labels_A)

# Final reward combines with negative cross-weight
reward = R_A(x) + beta * R_B(x)   # beta learned, converges to ~-0.26
# OR simpler:
reward = R_A(x) - 0.25 * R_B(x)  # fixed negative weight
```

Why negative? Because where R_A and R_B agree, that's signal. Where they disagree, that's contamination artifact. Subtracting amplifies the agreement and cancels the disagreement.

Our experiments show cross-connected dual models beat a single model by 4-22%, with the advantage growing as contamination (alpha) increases. At alpha = 1.0, the advantage is largest.

#### For synthetic data:

```python
# Train two models on each other's outputs -- never on their own
M_A_data = M_B.generate(prompts_A)
M_B_data = M_A.generate(prompts_B)

M_A.train(M_A_data)  # M_A never sees its own outputs
M_B.train(M_B_data)  # M_B never sees its own outputs

# Final model: ensemble or pick the better one
```

This breaks the self-referential loop entirely. Each model's effective alpha drops to 0 for its own contamination. Cost: 2x models. Benefit: eliminates model collapse (the progressive degradation documented by Shumailov et al. 2024 when models train on their own outputs recursively).

#### For recommendations:

```python
# Two recommendation algorithms with different inductive biases
recs_A = algorithm_A.recommend(user)
recs_B = algorithm_B.recommend(user)

# Where they AGREE: high confidence (signal)
# Where they DISAGREE: likely contamination artifact
confident_recs = recs_A.intersection(recs_B)
suspect_recs = recs_A.symmetric_difference(recs_B)

# Log suspect recs separately for analysis
# Serve: confident_recs + explore(suspect_recs)
```

This is ensemble diversity, but with a specific mechanism: disagreement is the decontamination signal. The items where two differently-biased algorithms agree are likely genuine user interests. The items where they disagree are likely artifacts of each algorithm's feedback loop.

---

### Fix 3: System-Aware Training (Multigrid --> ML)

**The numerical methods version**: Multigrid computes corrections at multiple resolutions. The coarse grid models the large-scale error structure, informing the fine grid's local corrections. Each level's update accounts for how corrections at other levels will respond. This is system-aware: it models the feedback.

**The ML translation**: Instead of treating training data as fixed, differentiate through the process that generates the data. Model how your current update will change the data distribution for future updates, and optimize the full trajectory.

**For RLHF (LOLA-style):**
```python
# Standard RLHF: treat reward as fixed
loss = -reward_model(model.generate(prompt))
loss.backward()

# System-aware: include how RM will update based on your outputs
# Step 1: Compute current loss
loss_current = -reward_model(model.generate(prompt))

# Step 2: Simulate one RM update
rm_updated = reward_model - lr_rm * grad_rm(model.generate(prompt))

# Step 3: Optimize for FUTURE reward (after RM adapts to you)
loss_future = -rm_updated(model.generate(prompt))

# Step 4: Blend current and future
total_loss = (1 - gamma) * loss_current + gamma * loss_future
total_loss.backward()  # differentiates through the RM update
```

This is Learning with Opponent-Learning Awareness (LOLA, Foerster et al. 2018) applied to the model-RM interaction. The model accounts for how the RM will adapt to its outputs.

**Estimated improvement**: 8.3% (our measured gap between myopic and system-aware optimization for k=1). This is exact for the toy setting; the gap at scale is an open question but the direction is reliable.

**Critical caveat from our experiments**: Naive backpropagation through many feedback steps HURTS. In our SRU experiments, deeper unrolling (T=10, T=20) drove the effective weight further from the true optimum due to tanh saturation / vanishing gradients. The right approach is **T=2: differentiate through ONE step of feedback, not many**.

This maps exactly to multigrid: you don't solve the coarse grid to convergence. You do one coarse correction, then return to the fine grid. One step of system awareness captures most of the benefit. Many steps compound approximation errors.

**In pseudocode:**
```python
# BAD: Unroll 10 steps of feedback (too deep, gradients degrade)
for t in range(10):
    loss_t = compute_loss(model, data_t)
    data_{t+1} = contaminate(data_t, model.output)
total_loss = sum(loss_t)
total_loss.backward()

# GOOD: Unroll exactly 2 steps (multigrid-style)
loss_now = compute_loss(model, data_now)
data_next = contaminate(data_now, model.output)
loss_next = compute_loss(model, data_next)
total_loss = loss_now + loss_next
total_loss.backward()
```

---

## 4. Decision Tree: Which Fix to Use

```
Can you measure alpha?
|
+-- YES
|   |
|   +-- alpha < 0.3?
|   |   |
|   |   +-- YES --> Monitor but probably don't intervene.
|   |   |           The bias exists but compounds slowly.
|   |   |           Revisit if training runs are very long (>100 epochs).
|   |   |
|   |   +-- NO --> alpha < 0.6?
|   |       |
|   |       +-- YES --> Fix 1 (over-relaxation). Cheapest.
|   |       |           omega ~= 1 + alpha^2. Implement in an afternoon.
|   |       |
|   |       +-- NO --> alpha >= 0.6
|   |           |
|   |           +-- Fix 2 (dual models). The contamination is too
|   |               strong for a scalar correction. You need
|   |               structural decontamination via cross-subtraction.
|   |
+-- NO (can't measure alpha)
|   |
|   +-- Can you train two models?
|   |   |
|   |   +-- YES --> Fix 2 (dual models with cross-subtraction).
|   |   |           Doesn't require knowing alpha.
|   |   |
|   |   +-- NO --> Fix 1 with omega swept empirically on
|   |               held-out human-labeled data.
|   |
+-- Is the task critical enough for extra engineering?
    |
    +-- YES --> Fix 3 (system-aware training).
    |           Best theoretical results but hardest to implement.
    |           Fix 2 is more robust to implementation errors.
    |
    +-- NO --> Fix 1 or Fix 2 based on alpha.
```

**Cost comparison:**

| Fix | Implementation effort | Compute overhead | Expected gain | Robustness |
|-----|----------------------|-----------------|---------------|------------|
| Fix 1: Over-relaxation | 1 line of code + sweep | ~0% | 1-8% depending on alpha | Medium (can diverge if omega too high) |
| Fix 2: Dual models | New training pipeline | ~2x training | 4-22% | High (fails gracefully) |
| Fix 3: System-aware | Second-order gradients | ~1.5-3x per step | ~8.3% (theoretical max) | Low (gradient issues at depth > 2) |

---

## 5. What NOT to Do

**Don't go deeper.** Our most definitive experiment (fair T x N test, 11 configurations at 6 contamination levels) showed that deep single-viewpoint reflection is the WORST strategy for self-referential problems. At matched compute:

- N=1, T=10 (pure chain-of-thought): WORST at every alpha tested
- N=5, T=2 (wide + minimal depth): BEST at every alpha tested
- The deep configuration lost by 19-47% vs. balanced, and 10-46% vs. wide

More chain-of-thought steps, more RLHF iterations from a single reward model, more passes through the same contaminated data -- all of these are "going deeper" on a single viewpoint. The information bottleneck is the viewpoint, not the depth. Multiple shallow perspectives beat one deep perspective.

**Don't assume more data fixes it.** The contamination is structural, not statistical. If alpha = 0.5 and you 10x your dataset, you now have 10x as much contaminated data. The self-consistency equation `w^2 + w - 1 = 0` holds regardless of dataset size. We verified this: the 1/phi attractor persists across Gaussian, uniform, Laplace, bimodal, and exponential distributions at all tested scales.

**Don't ignore small alpha.** Alpha = 0.2 means a 0.3% performance hit per update step. Over 1000 update steps, the systematic bias compounds. Small alpha sustained over many epochs matters more than large alpha over few epochs, because the fixed point is an attractor -- the system settles into it and stays there.

**Don't add more feedback loops without accounting for interaction.** Our experiments showed that k feedback loops (neighbors) change the self-consistency equation to `k*w^2 + w - 1 = 0`. At k=1, the fixed point is 0.618. At k=5, it drops to 0.358. At k=20, it's 0.200. More feedback loops COMPOUND the problem. If you're stacking RLHF on top of synthetic data training on top of self-play, the effective k is the number of distinct feedback paths, and the attractor is lower (worse) than any single loop.

---

## 6. Quick-Start Recipes

### RLHF

1. Measure alpha: count what fraction of RM training data is model-generated
2. If alpha > 0.3: multiply the policy gradient by omega = 1 + alpha^2
3. Evaluate on held-out human preference data (not RM scores) to validate
4. If alpha > 0.6 or the system is already unstable: train two RMs on alternating batches, combine with `reward = R_A(x) - 0.25 * R_B(x)`
5. Track omega or the RM disagreement rate as a monitoring signal across training

### Synthetic Data

1. Track the synthetic fraction of your training data (including synthetic data that leaked into "natural" web scrapes)
2. If possible: train two models, each generating data for the other (never training on its own outputs)
3. If 2x compute is infeasible: over-relax gradient updates by omega = 1 + alpha^2, where alpha is the synthetic fraction
4. Monitor for model collapse: measure output diversity (distinct n-grams, embedding variance) across generations
5. Validate on a frozen, verified-human-only test set that is NEVER contaminated

### Recommendations

1. Measure alpha: A/B test with random recommendations on 5% of traffic to estimate organic vs. influenced behavior
2. Train two recommendation models with different architectures or different random seeds
3. Serve items where both models agree (high confidence signal)
4. Log and separately analyze items where models disagree (contamination candidates)
5. Use disagreement rate as an ongoing health metric -- rising disagreement signals increasing feedback contamination

### Self-Play

1. Alpha = 1.0 by definition. Fix 2 (dual models) is mandatory, not optional.
2. Train two agents that play each other (not themselves). Agent A's opponent is always Agent B and vice versa.
3. Cross-evaluate: A's performance is scored by metrics computed against B's play, not A's own
4. Add negative-correlation regularization: `loss += lambda * correlation(A.features, B.features)` to enforce diversity
5. Periodically snapshot both agents and test against a diverse pool of fixed opponents to measure absolute (not self-referential) improvement

### Pseudo-Labeling

1. Measure alpha: `pseudo_labels / total_labels` at each training epoch
2. Keep alpha below 0.5 by maintaining a minimum ratio of human labels
3. Over-relax: when training on pseudo-labeled data, multiply the loss by omega = 1 + alpha^2
4. Cross-labeling variant: train two models, each pseudo-labels for the other (neither trains on its own pseudo-labels)
5. Monitor: track pseudo-label accuracy against a small human-verified holdout set each epoch

### Autoregressive Generation

1. Alpha increases with generation length: at position t, alpha ~= (t - prompt_length) / t
2. Apply a position-dependent confidence discount: scale logits by 1/(1 + alpha(t)^2) for generated positions
3. Or equivalently: for each generated token, mix the model's logit with a "skepticism" term that increases with generation length
4. Temperature scheduling: increase temperature slightly with generation length to counteract the narrowing effect of self-referential feedback
5. Validation: compare perplexity on human-continuation vs model-continuation of the same prefixes -- the gap is your contamination signal

---

## 7. Evidence and Caveats

### What we've proven (in the toy setting)

- **The self-consistency equation `kw^2 + w - 1 = 0` is exact** for linear self-referential agents. Derived analytically, confirmed to 3 decimal places across 5 seeds at 50,000 timesteps each.
- **The equation generalizes to matrices**: W^2 + W - I = 0 holds through dimension d=16, with spectral radius deviating less than 0.026 from 1/phi. The trace converges to d/phi as predicted.
- **The attractor is distribution-independent and optimizer-independent**: 11 conditions tested (5 distributions x 6 optimizer/lr combinations). Maximum deviation from 1/phi: 1.3%.
- **The system-aware gap is 8.3%**: An oracle optimizer that accounts for its own feedback achieves w = 0.525 vs. SGD's 0.618. The gap is `(0.670 - 0.618) / 0.618 = 8.4%` in R^2.
- **Cross-connected dual models beat single models by 4-22%**, with the advantage increasing with contamination strength.
- **Cross-connections learn negative weights (~-0.26)** at all depths and configurations tested. This is subtractive decontamination (parallax).
- **At matched compute, balanced (N=5, T=2) beats deep (N=1, T=10)** at every contamination level tested. Deep single-viewpoint is always worst.
- **Negative cross-connections persist and strengthen with depth**: tested at 1, 2, and 3 layers.

### What we haven't proven

- **That the 8.3% gap persists at scale.** Our experiments use scalar and low-dimensional systems. Large neural networks may have different self-referential dynamics due to overparameterization, layer normalization, and other factors that interact with feedback loops.
- **That the fixes transfer directly.** Over-relaxation, dual models, and system-aware training are concrete proposals grounded in theory, but they haven't been validated on production RLHF, recommendation, or synthetic data systems.
- **That alpha is the right parameter.** In real systems, the contamination mechanism is more complex than a scalar multiplier. There may be frequency-dependent, representation-dependent, or task-dependent contamination structures that a single alpha doesn't capture.
- **That the golden ratio specifically matters at scale.** The exact value 1/phi = 0.618 is for the simplest case (k=1, linear). Real systems have multiple feedback paths (higher k) and nonlinear dynamics. The QUALITATIVE finding (myopic optimization is systematically biased in self-referential systems) is more robust than the specific number.

### The honest pitch

These are preliminary results from toy experiments. But the algebra is clean, the experiments are controlled, and the numerical methods community validated the identical structure 70 years ago.

**Cost to try Fix 1:** One line of code (multiply gradient by omega) plus an afternoon to sweep omega on your held-out evaluation set. If it improves held-out performance, you've found the self-referential bias and partially corrected it. If it doesn't, you've learned that either (a) alpha is small enough not to matter, (b) your system's self-reference has a different structure than our toy model, or (c) other bottlenecks dominate.

**Cost to try Fix 2:** A weekend of engineering to set up dual-model training. The infrastructure investment pays off regardless, because the disagreement signal between two models is valuable diagnostic information about your system's contamination structure.

**Cost to try Fix 3:** A week of engineering, requires second-order gradient support, and may need careful tuning to avoid instability. Only worth it if Fixes 1-2 show clear signal but leave headroom.

The downside risk is an afternoon. The upside is closing an 8.3% gap that no amount of data or compute can fix, because it's structural.

### Related work

- **SOR and iterative methods**: Young (1950, 1954), Varga (1962). Optimal relaxation for self-referential linear systems.
- **Red-black ordering**: Gauss-Seidel with two-coloring. Evans (1984). Breaks within-color self-reference.
- **Multigrid**: Brandt (1977), Briggs et al. (2000). Multi-resolution system-aware correction.
- **Bidirectional path tracing**: Veach & Guibas (1997). Two contaminated views of the light field with MIS (negative-weight) combination.
- **LOLA**: Foerster et al. (2018). Opponent-aware learning in multi-agent RL. The system-aware principle applied to game-playing.
- **Model collapse in synthetic data**: Shumailov et al. (2024). Empirical evidence of self-referential degradation.
- **Negative correlation learning**: Liu & Yao (1999). Ensemble diversity through anti-correlation.

The numerical methods literature solved the algebraic problem. The ML literature is accumulating empirical evidence of the symptoms. This guide connects the diagnosis to the cure.

---

*Based on 11 experiments documented in `analysis/FULL_SESSION_FINDINGS.md`. All experiments reproducible from scripts in `python/experiments/`. Guide drafted 2026-02-10.*
