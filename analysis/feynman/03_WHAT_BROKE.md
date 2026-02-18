# Null Results, or: Nature Doesn't Care About Elegance

*Seven predictions that failed, and what we learned from each one. The experiment was the judge, and the judge said no.*

---

## Why This Chapter Matters

The most important thing in science isn't the discoveries. It's the honesty about failures. Anybody can find a pattern and tell a story about why it's deep. The hard part is running the experiment that could kill your beautiful theory -- and reporting the results when it does.

We had a beautiful theory. The golden ratio appears in self-referential optimization! It's universal! It cascades through hierarchies! It survives nonlinearity! Nature is elegant!

Nature didn't get the memo.

---

## Failure 1: The Golden Ratio Doesn't Survive Nonlinearity

**What we predicted:** The equation w^2 + w - 1 = 0 gives w = 1/phi for a linear agent. Real neural networks use ReLU, sigmoid, tanh. We hoped phi would survive -- maybe the activation function just scales things, and the golden ratio would peek through.

**What happened:** ReLU gives an effective gain of 0.394. Sigmoid gives 0.384. Both are close to 1/phi^2 = 0.382, which got us excited for about ten minutes.

**Why it failed:** We dug into the ReLU math. The key fact is that Cov(max(0, u), u) = 1/2 for standard normal u -- half-rectification cuts the covariance exactly in half. The self-consistency equation becomes k * w^2 + w - 1 = 0 where k = (pi - 1)/(2*pi) = 0.341. That k involves *pi*, from the Gaussian integral over the positive half-line. Not phi. Pi.

The sigmoid story is similar but messier: k = 0.330, a numerical constant with no clean closed form. The closeness of 0.384 to 1/phi^2 = 0.382 is a coincidence -- you'd need k = phi^3 = 4.236 for exact 1/phi^2, but the actual k is 0.330.

**The lesson:** The golden ratio was a special case. It appears when k = 1 (linear activation), and k = 1 is the simplest possible case. The moment you use a realistic activation function, k changes, and the specific root changes with it. What survives is the *form* of the equation -- kw^2 + w - 1 = 0 -- not the specific value 1/phi.

---

## Failure 2: The Self-Referential Unit Has No Structural Advantage

**What we predicted:** If self-reference is the key phenomenon, then an architecture that *explicitly represents* self-reference should have an advantage. We built a Self-Referential Unit (SRU) with a shared w_self parameter that models the feedback loop directly. Surely structure helps?

**What happened:** Against a parameter-matched baseline with free hidden units:

| Contamination (alpha) | SRU R^2 | Baseline R^2 | SRU wins? |
|----------------------|---------|-------------|-----------|
| 0.0 | 0.970 | 0.970 | Tie |
| 0.3 | 0.913 | 0.927 | No (-0.014) |
| 0.7 | 0.791 | 0.815 | No (-0.024) |
| 1.0 | 0.595 | 0.726 | No (-0.131) |

The SRU *loses*. At alpha = 1, it loses by a factor of 2.5.

**Why it failed:** The shared w_self constraint forces all 16 hidden units to use the same self-referential weight. The baseline has 21 free units that can individually learn optimal recurrent dependencies for different aspects of the signal. Forcing all units to agree on a single self-reference parameter is a *constraint*, not an advantage. Flexible parameters adapt better than rigid structure.

**The lesson:** Knowing that self-reference exists doesn't help if your representation of it is too rigid. The system needs to be flexible enough to handle self-reference in its own way.

---

## Failure 3: The Degrees-of-Freedom Step Function Doesn't Manifest

**What we predicted:** Two observers should see a discrete jump in capability over one observer, analogous to how two eyes give you depth perception that one eye fundamentally cannot. We predicted a gain ratio of MSE(N=1)/MSE(N=2) = 2.5 -- a sharp step function.

**What happened:** The gain ratio was 1.05 at alpha = 0 and crept up to 1.27 at alpha = 1. Gradual and smooth. Nowhere near 2.5.

**Why it failed:** Geometric parallax (two eyes triangulating a point in space) involves discrete degrees of freedom -- you either can or cannot triangulate. Information parallax (two models decontaminating each other's echo) involves continuous statistical improvement. Each additional perspective adds partial decontamination, not a phase transition. There's no magic threshold at N = 2.

**The lesson:** The analogy between spatial parallax and information parallax is real but continuous, not discrete. Two eyes are better than one, but by 17-27%, not by 250%.

---

## Failure 4: Cascade Prediction Fails

**What we predicted:** If a single self-referential loop gives w = 1/phi, then a second level (an agent observing the first agent's output, plus its own echo) should give w = 1/phi^2. Self-referential discounts should compound multiplicatively across levels.

**What happened:** The second-level agent converged to w = 0.534 -- closest to 0.5, not to 1/phi^2 = 0.382.

**Why it failed:** The second-level agent sees *two* contamination sources: Agent A's output and its own echo. That's k = 2 in our general equation kw^2 + w - 1 = 0, which gives w = (-1 + sqrt(9))/4 = 0.5. Not a cascade of 1/phi -- just the k = 2 member of the same family. Self-referential discounts don't compound multiplicatively; each level solves its own self-consistency equation with its own effective k.

**The lesson:** Hierarchical self-reference is not iterated self-reference. Each level faces its own neighborhood of contamination sources and finds its own fixed point.

---

## Failure 5: Pseudo-Labeling Validation (1 out of 5 tests passed)

**What we predicted:** Pseudo-labeling (where a model generates training labels for itself) is self-referential. We predicted that over-relaxation (omega > 1) and dual-model cross-labeling would improve performance, just as they do in our toy system.

**What happened:**

| Test | Prediction | Outcome |
|------|-----------|---------|
| Contamination confirmed | Accuracy degrades with alpha | PASSED |
| Over-relaxation helps | omega = 1.0 best at all alpha | FAILED |
| Optimal omega tracks formula | No correlation | FAILED |
| Dual-model beats single | No improvement | FAILED |
| Total improvement from any fix | Expected 3-10% | Actual 0.36% | FAILED |

**Why it failed:** Pseudo-label errors are *class-structured*. When the model confuses digit 4 with digit 9, it does so systematically -- the errors cluster on specific digit pairs. Our theory assumes *uniform*, *continuous* contamination: signal plus Gaussian noise. A scalar correction omega amplifies correct and incorrect pseudo-labels equally. When the contamination has structure (class-specific error patterns), scalar decontamination can't work.

**The lesson:** The theory requires continuous, uniform contamination. Classification with discrete, class-structured errors violates this assumption. The boundary of applicability is sharp and non-negotiable.

---

## Failure 6: Random Initialization Diversity Is Insufficient

**What we predicted:** If two models are better than one (see Document 4), maybe we just need to start them at different random points and they'll develop different enough perspectives.

**What happened:** Two identical linear models with different random initializations performed 53-83% *worse* than a single model on all three real-world tasks (thermostat, sensor, market). Not just no improvement -- active degradation.

**Why it failed:** Linear models with different starting points converge to the *same* optimum. The loss landscape has a single basin. The two "eyes" end up seeing identically, but now the cross-connections are trying to subtract something that's exactly the same -- which just subtracts signal. Random initialization does not create genuine diversity; it only creates temporary diversity that vanishes as training progresses.

**The lesson:** Diversity must come from different inductive biases (different architectures), not different starting points. A linear model and an MLP see the world differently because they *are* different -- not because they started at different random numbers.

---

## Failure 7: T=2 Is Signal-Dependent

**What we predicted:** Given fixed compute, the optimal allocation is always T = 2 (two processing steps) with the rest of the budget spent on width (more independent perspectives). We found this consistently in our initial experiments.

**What happened:** For *deterministic* signals (like a sine wave), T = 2 wins. For *stochastic* signals (random noise, AR(1) processes), T = 1 (maximum width, no depth) wins. The "one integration step" of T = 2 adds parameters without benefit when there's nothing temporally predictable to integrate.

**Why it failed:** The T = 2 advantage comes from integrating cross-connection information over one processing step. If the signal has temporal structure, that integration captures useful information. If the signal is pure noise, the integration step has nothing to work with and the extra parameters just add overfitting.

**The lesson:** "Depth beyond T = 2 is always wasteful" remains robust across all signal types. But the choice between T = 1 and T = 2 depends on whether your signal has temporal structure. The deep (T >> 2) strategy is always worst.

---

## The Pattern in the Failures

Look at what survived and what didn't:

**Survived:** The equation kw^2 + w - 1 = 0. The general form holds for all activations, all topologies, all signal distributions, all optimizers. The family is robust.

**Didn't survive:** The specific value 1/phi. The cascade multiplication. The step function at N = 2. The transfer to classification. The structural advantage of explicit self-reference.

Every failure has the same root cause: we took a result that was exactly true in the simplest possible system and assumed it would generalize without change. It didn't. The *form* generalized (quadratic self-consistency with different k). The *specific values and behaviors* didn't.

That's how science works. You find something clean in a toy system. You test it in harder systems. Some of it survives, transformed. Most of it breaks. The pieces that survive are the real physics. The pieces that break tell you where the boundaries are.

---

**The key insight:** The golden ratio is a special case, not a universal law. The general self-consistency equation kw^2 + w - 1 = 0 is robust across all tested conditions, but the specific value 1/phi appears only for the simplest case (linear, single-loop, k = 1). Every attempt to find phi in more complex settings -- nonlinear activations, cascaded hierarchies, classification tasks -- failed. What survives is the algebraic structure, not the elegant number.
