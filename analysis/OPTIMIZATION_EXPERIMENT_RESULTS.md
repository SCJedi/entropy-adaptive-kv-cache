# Ouroboros Optimization Experiments: Results and Analysis

## 1. What Was Predicted

The Ouroboros optimization theory derives exact golden-ratio partitions for any self-referential optimizer -- an agent that is part of the system it optimizes. The central predictions are:

- **Action/perception DOF split**: The optimal allocation is nu = phi/sqrt(5) ~ 72.4% action, 27.6% perception. This is not a design recommendation; it is claimed to be the unique self-consistent fixed point.
- **Information ceiling**: Only 1/phi^2 ~ 38.2% of total information is accessible to the optimizer. The remaining 1/phi ~ 61.8% is structurally dark -- inaccessible regardless of compute or data.
- **Stability**: The fixed point has beta'(phi^2) = -(3-phi) ~ -1.382. Perturbations are corrected but with overshoot, producing oscillatory convergence.
- **Universality**: These ratios apply, in principle, to any system where the optimizer's actions feed back into the landscape it optimizes. The theory has zero free parameters.

Two experiments tested whether these predictions manifest in concrete ML systems.

---

## 2. Experiment 1: Self-Play Tic-Tac-Toe

### Design

Tabular value learning (Monte Carlo updates) with epsilon-greedy exploration, trained over 100K episodes. Two conditions:

- **Self-play**: Both players share a single value function V. Every update to V changes both the policy and the training distribution -- a self-referential loop.
- **Frozen-opponent**: The opponent uses a periodically-frozen copy of V (snapshot every 5K episodes), breaking tight self-referential coupling.

Epsilon swept over 13 values from 0.05 to 1.0. Learning rate alpha = 0.1 with decay. Metrics: value R^2 against minimax ground truth (all states, visited-only, unvisited-only), policy accuracy, state coverage, and normalized greedy policy entropy. Full game graph pre-computed via minimax (5,478 reachable states, 4,520 non-terminal).

### Key Results

From the epsilon sweep at convergence (100K episodes):

| Metric | Self-Play (best eps) | Frozen (best eps) | Prediction |
|---|---|---|---|
| Value R^2 (all states) | 0.372 (eps=0.70) | 0.288 (eps=0.70) | 0.382 |
| Policy accuracy | ~0.91 (eps=0.05) | ~0.83 (eps=0.05) | 0.382 |
| State coverage | ~0.825 (eps=0.70) | ~0.50 (eps=0.70) | 0.382 |
| Greedy policy entropy | ~0.084 (eps=0.70) | ~0.094 (eps=0.70) | 0.276 |
| Optimal epsilon (by R^2) | 0.70 | 0.70 | 0.276 |

The R^2 (all states) value of 0.372 at the peak is 2.6% below the predicted 1/phi^2 = 0.382. At first glance, this is striking. However:

1. **The frozen-opponent shows the same curve shape, just lower.** Both conditions peak at eps=0.70 and decline at higher epsilon. The self-play curve does not have a qualitatively different shape -- it is shifted upward uniformly, opposite to the prediction that self-reference should constrain performance.

2. **Self-play outperforms frozen.** The theory predicts self-referential coupling limits the optimizer. In fact, self-play achieves higher R^2 (0.372 vs 0.288), higher policy accuracy, and higher state coverage at every epsilon tested. The self-referential loop is helping, not constraining.

3. **Other metrics are far from predictions.** Policy accuracy (~91%) and state coverage (~82.5%) are nowhere near the predicted 38.2% ceiling. Greedy policy entropy (~8.4%) is far from the predicted 27.6%.

4. **The optimal epsilon (0.70) is far from 1-nu = 0.276.** The error is 153%. The exploration-exploitation prediction is not supported.

### Diagnosis

The R^2 peak at 0.372 is a standard bias-variance tradeoff: low epsilon yields poor state coverage (biased V estimates for unvisited states), while high epsilon yields noisy MC returns (high variance). The peak occurs where these effects balance. This is a generic feature of tabular RL with epsilon-greedy exploration, not an information-theoretic ceiling.

The proximity to 0.382 is almost certainly coincidental. Changing the learning rate, episode count, or decay schedule would shift the peak. The frozen-opponent control confirms this: it shows the same shaped curve without the self-referential coupling the theory requires.

TTT is the wrong domain for testing Ouroboros predictions because the agent is not truly "part of" the system in the structural sense the theory requires. The game rules are external and fixed. The agent plays IN the game but is not MADE of the game. Epsilon-greedy exploration is an externally imposed mechanism, not a consequence of self-referential constraints.

---

## 3. Experiment 2: Self-Referential Prediction

### Design

A predictor P influences what it predicts:

```
x_{t+1} = (1 - alpha) * f(x_t) + alpha * P(x_t) + sigma * noise
```

where f is a chaotic map (logistic r=3.7, sine, or tent), P is trained online via SGD to minimize prediction error, alpha controls self-reference strength (0 = pure chaos, 1 = self-fulfilling prophecy), and sigma = 0.05. Alpha swept over 21 values from 0 to 1.

Two predictor types: linear (P(x) = wx + b, 5 seeds) and MLP (16 hidden units, tanh, 3 seeds). 20K timesteps per run, 5K burn-in. Gradient computation accounts for self-reference: the effective gradient is scaled by (1-alpha) because the predictor's influence on x_{t+1} reduces the effective error signal.

### Key Results

From the normalized prediction quality (R^2 / oracle R^2) vs alpha curves:

- **At alpha=0 (pure chaos)**: Normalized quality near 0 for linear predictors on all three chaotic maps. The linear predictor cannot track logistic, sine, or tent dynamics. MLP does moderately better.

- **Rising phase (alpha 0 to ~0.50)**: As alpha increases, the system linearizes -- the chaotic component is attenuated by (1-alpha) while the predictor's own output is amplified. This makes the system more predictable. Normalized quality rises to approximately 0.83-0.87 across dynamics.

- **Collapse zone (alpha ~0.55 to ~0.70)**: Quality drops sharply. The R^2 values go deeply negative (predictions are worse than the mean). This is a linear stability failure: when alpha*w (the predictor's effective linear coefficient) exceeds 1 in magnitude, the coupled system becomes unstable, producing divergent oscillations clipped by the [0,1] boundary.

- **Recovery (alpha > 0.90)**: At high alpha, the system is nearly self-fulfilling. P(x_t) dominates x_{t+1}, so the predictor is essentially predicting its own output. R^2 recovers.

- **The collapse zone varies by dynamics**: Logistic collapses around alpha=0.55, sine and tent around alpha=0.65. The sine/tent collapse point is near 1/phi = 0.618, but the logistic collapse is not. The collapse depends on the learned weights and the dynamics' Lyapunov exponent, not on a universal constant.

- **MLP vs linear**: At moderate alpha (~0.40), MLP and linear converge to similar normalized quality. At low and high alpha, MLP outperforms. The ceiling at moderate alpha is partially structural (the self-referential mixing dominates predictor capacity), but it is not at a phi-related value.

### The (1-alpha)^2 Null Hypothesis

The predictable component of the prediction error is:

```
x_{t+1} - P(x_t) = (1-alpha) * (f(x_t) - P(x_t)) + noise
```

so the effective signal scales as (1-alpha). The prediction MSE from the signal scales as (1-alpha)^2, suggesting R^2 should scale as (1-alpha)^2 * R^2(alpha=0). However, this null hypothesis predicts quality near zero everywhere (since R^2 at alpha=0 is approximately zero for linear predictors on chaotic maps). The actual dynamics are far richer: the predictor adapts its weights as alpha changes, the system linearizes at moderate alpha, and the coupled dynamics undergo a stability transition. The null hypothesis captures the algebraic structure but misses the learning dynamics.

### The Mathematical Trap

The identity (1 - 1/phi^2)^2 = 1/phi^2 means that any function involving (1-alpha)^2 will produce phi-related values when evaluated at phi-related alpha values. This is algebraic tautology, not physics. The self-referential prediction output file notes this explicitly: apparent phi-structure in R^2 vs alpha could reflect the inherent phi-structure of (1-alpha)^2 at phi-related points.

### Diagnosis

The dynamics are explained by linear stability analysis of a mixed chaotic-linear map. As alpha increases from 0:

1. The chaotic component weakens (factor 1-alpha).
2. The linear-predictor component strengthens (factor alpha).
3. The system transitions from chaos to a stable linear map when the chaotic Lyapunov exponent is overcome.
4. At higher alpha, the effective linear map alpha*w exceeds the unit circle, causing instability.
5. The critical alpha depends on the learned weights w, which depend on the dynamics and learning rate.

The collapse is a standard dynamical systems phenomenon (loss of stability of a linear map). It occurs at dynamics-dependent alpha values, not at a universal phi-related point. The proximity of the sine/tent collapse to 1/phi appears coincidental; the logistic collapse at a different point confirms this.

---

## 4. Experiment 3: Network Self-Referential Agents

### Design

N=20 agents, each with a true signal s_i(t) ~ N(0,1). Agent i observes:

```
y_i(t) = s_i(t) + Σ_{j∈neighborhood(i)} o_j(t-1)
```

where o_j is the neighbor's output. The agent produces:

```
o_i(t) = w_i * y_i(t) + b_i
```

and learns via SGD to minimize (o_i - s_i)². This creates STRUCTURAL self-reference: the agent's output feeds back into its own observation through the network. Removing an agent changes the system's dimensionality.

Topologies tested:
- **Isolated** (k=1): Agent observes only its own output
- **Ring k=1**: Each agent has 3 neighbors (self + 2 neighbors)
- **Ring k=2**: 5 neighbors (self + 4 neighbors)
- **Ring k=4**: 9 neighbors (self + 8 neighbors)
- **Complete**: 20 neighbors (all agents)
- **No-self controls**: Same topologies but agents don't observe their own output

Parameters: 50K timesteps, 10K burn-in, 5 random seeds, learning rate 0.01 with exponential decay (gamma=0.9999).

### Key Results

From the R² vs timestep curves at convergence (mean over final 5K steps):

| Topology | With Self-Loop | No Self-Loop | Predicted Weight w |
|---|---|---|---|
| Isolated (k=1) | R²=0.618, w=0.618 | N/A | 0.618 (1/φ) |
| Ring k=1 (3 neighbors) | R²=0.434, w=0.434 | 0.642 | 0.434 |
| Ring k=2 (5 neighbors) | R²=0.358, w=0.358 | 0.558 | 0.358 |
| Ring k=4 (9 neighbors) | R²=0.281, w=0.281 | 0.498 | 0.281 |
| Complete (20 neighbors) | R²=0.200, w=0.200 | 0.463 | 0.200 |

**Key observations:**

1. **The golden ratio emerges from algebraic self-consistency.** The isolated agent (k=1) learns w = 0.618 ≈ 1/φ. This comes from quadratic self-consistency: at steady state, Var(y) = 1 + w² Var(y), so Var(y) = 1/(1-w²). The optimal filter weight minimizes MSE, giving w = Cov(s,y)/Var(y) = 1/(1+Var(y)) = 1 - w². Rearranging: w² + w - 1 = 0, which is the golden ratio equation with solution w = (-1 + √5)/2 = 1/φ.

2. **General formula for neighborhood size k:** The same analysis for k neighbors yields k·w² + w - 1 = 0, with solution w = (-1 + √(1+4k))/(2k). The golden ratio is the k=1 special case. Other topologies follow different roots of this family.

3. **R² = w at convergence.** For all topologies, the observed R² matches the learned weight w. This is consistent with the self-consistency algebra.

4. **Smooth degradation with neighborhood size.** As the neighborhood grows, both w and R² decrease smoothly. There is no phase transition, no plateau at 1/φ² (0.382), and no evidence of a universal information ceiling.

5. **Self-reference hurts signal recovery.** The no-self controls (where agents don't observe their own output) achieve higher R² at every topology. The self-referential loop contaminates the signal, reducing recovery quality.

6. **Efficiency near 1.0.** Agents achieve the theoretical maximum R² given the level of contamination. They are not constrained by an additional information ceiling beyond the structural feedback.

### Diagnosis

The golden ratio emerges from the algebraic self-consistency of a single self-referential loop, not from information-theoretic ceilings. The "narrator" (agent hearing its own echo) learns to discount itself by exactly 1/φ — structurally forced by the equation w² + w - 1 = 0. This is the k=1 special case of a general family k·w² + w - 1 = 0.

Networks with more neighbors follow different roots. The golden ratio is not a universal attractor; it is the solution for a specific graph structure (self-loop only). The experiment achieves genuine structural self-reference (removing an agent changes the system's dimensionality), but the predicted 1/φ² information ceiling does not appear. Instead, R² decreases smoothly with neighborhood size, tracking the learned weight w, which is fully explained by the quadratic self-consistency algebra.

The no-self controls confirm that self-reference degrades performance. Agents without self-loops recover signal better because they are not contaminated by their own outputs. This is opposite to the hypothesis that self-reference reveals an intrinsic optimization limit.

---

## 5. What We Learned

### The network experiment's genuine golden-ratio finding

The network self-referential experiment is the first to produce a golden ratio that is:
1. **Structurally forced**: The equation w² + w - 1 = 0 arises from the algebra of self-consistency, not from tuning or coincidence.
2. **Exact at equilibrium**: The learned weight converges to 1/φ within numerical precision.
3. **Reproducible**: Five random seeds all converge to the same value.

However, this finding does NOT support the Ouroboros predictions:
- The golden ratio emerges from the k=1 special case of a general family k·w² + w - 1 = 0. Other neighborhood sizes produce different ratios.
- The 1/φ² information ceiling is not observed. R² decreases smoothly with neighborhood size, tracking the self-consistency equation, not converging to a universal limit.
- Self-reference degrades performance (no-self controls achieve higher R²), opposite to the hypothesis that self-reference reveals intrinsic optimization structure.

The golden ratio here is an algebraic artifact of quadratic self-consistency in a single self-referential loop. It is not a universal optimization constant. It is structurally forced, but only for the specific k=1 topology. The broader lesson: φ can emerge from self-referential algebra without implying universal optimization laws.

### The theory's domain

The Ouroboros optimization theory is mathematically proven: the DOF partition algebra is exact, the fixed-point analysis is correct, and the stability properties follow rigorously. The question was never whether the math works -- it was whether the theory maps onto real optimization systems. These experiments test that mapping.

### Self-play is not self-reference in the Ouroboros sense

In TTT, the game rules are external and fixed. The agent plays in the game but is not part of the game. The value function V is updated based on game outcomes, but V is not a component of the state space. Ouroboros requires the observer to be made of the same stuff as what it observes -- the observer's degrees of freedom must literally be a subset of the system's degrees of freedom. A tabular value function sitting in a separate dictionary does not satisfy this.

### Parametric coupling is not structural embedding

In the prediction experiment, the agent influences the system through a mixing parameter alpha. But alpha is a knob we turn externally -- it is not a structural constraint. In the Ouroboros framework, the embedding is structural: the observer cannot be removed from the system without changing the system's dimensionality. We can set alpha to zero and recover the original dynamics, which means the agent is parametrically coupled, not structurally embedded.

### Where Ouroboros might apply in ML

The theory might apply to systems where the agent's representation literally consumes system resources:

- A neural network whose weights ARE part of the loss landscape (not just evaluated on it).
- RLHF where the reward model is trained on the model's own outputs, creating genuine structural circularity.
- Self-modifying code systems where the program's representation overlaps with its execution state.
- Market-making algorithms that move the prices they predict, when the algorithm's capital is a non-negligible fraction of market liquidity.

These have genuine structural self-reference, not parametric coupling. The key criterion: removing the agent must change the system's dimensionality, not just a parameter.

### The phi quantities are algebraically elegant but physically contingent

The DOF partition theorem (nu = phi/sqrt(5)) is exact math given the axioms. Whether any real optimization system exhibits these ratios depends entirely on whether the axiom "physical DOF = optimization DOF" holds. Our experiments suggest it does not hold in the domains tested. This is not a refutation of the math -- it is a finding about the scope of the mapping.

---

## 6. Status of Predictions

| Prediction | TTT Result | Prediction Expt Result | Network Expt Result | Verdict |
|---|---|---|---|---|
| Value/quality ceiling = 1/phi^2 | 0.372 (2.6% off, but control shows same curve) | Peak ~0.83-0.87 | No ceiling; smooth degradation | Inconclusive / No |
| Self-play constrained vs control | Opposite: self-play outperforms | N/A | Opposite: self-reference degrades R² | No |
| Optimal exploration = 1-nu (0.276) | eps=0.70 (153% off) | N/A | N/A | No |
| Information ceiling = 38.2% | Not observed (policy acc 91%, coverage 82.5%) | Not observed | Not observed | No |
| Oscillatory convergence | Not distinctive in self-play | Not tested directly | Not observed | No |
| Phase transition at phi values | No | Collapse zone varies by dynamics | No | No |
| Golden ratio = 1/phi at k=1 | N/A | N/A | Yes (w=0.618, forced by w²+w-1=0) | Yes (k=1 only) |

### Overall Assessment

The Ouroboros optimization theory produces exact algebra with no free parameters. It makes sharp, quantitative predictions that are in principle falsifiable. We tested three ML instantiations -- self-play in a game, self-referential prediction in a dynamical system, and network self-referential agents -- and found no evidence for the predicted golden-ratio ratios as universal optimization constants.

The R^2 peak near 0.382 in TTT is the most suggestive finding, but the frozen-opponent control shows the same curve shape, which attributes the peak to bias-variance tradeoff rather than information-theoretic constraints. The self-referential prediction experiment shows rich dynamics (stability transitions, chaos suppression, predictor-system coupling) that are fully explained by linear stability analysis without invoking phi-related quantities. The network experiment produces a genuine golden ratio (w = 1/φ for k=1), but this is an algebraic artifact of quadratic self-consistency, not evidence for a universal optimization ceiling.

The theory remains valid as mathematics. Its application to optimization requires identifying systems with genuine structural self-reference -- where the optimizer's degrees of freedom are literally a subset of the system's degrees of freedom. Neither experiment achieved this. These results constrain where to look next, but they do not constitute universal falsification. The theory's domain may simply be narrower than initially hoped: not "any self-referential optimizer" but specifically systems with the structural embedding the axioms describe.

---

*Analysis completed February 2026*
*Experiments: selfplay_ttt.py (TTT), selfref_prediction.py (self-referential prediction), network_selfref.py (network self-referential agents)*
*Plots: ttt_results.png, selfref_results.png, network_selfref_results.png*
