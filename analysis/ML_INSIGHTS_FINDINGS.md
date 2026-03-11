# Practical ML Insights from Golden Cascade Research

**Date:** 2026-03-09
**Experiment:** `python/experiments/ml_insights_test.py`
**Results:** `python/experiments/plots/ml_insights_results.json`
**Plot:** `python/experiments/plots/ml_insights.png`

---

## Executive Summary

After 20 phases of golden cascade research, we ran 6 rigorous tests to extract practical ML insights. Each test compared a golden cascade mechanism against a standard ML baseline with matched architectures and datasets (MNIST, PCA to 50, [50->32->16->10]).

**Result: 2 YES, 0 PARTIAL, 4 NO.** Two mechanisms showed value, but with important caveats.

---

## Insights That Survived Testing

### 1. Settling (Test-Time Iterative Refinement) Is Unique to Stateful Neurons

**What:** Running a consensus network forward multiple times (T=5 vs T=1) produces a +49.4pp accuracy gain. A standard ReLU network gains nothing from repeated forward passes (-0.2pp).

**Evidence (3 seeds):**
- Standard network: 40.7% -> 40.5% (1 pass -> 5 passes), gain: -0.2pp
- Consensus network: 9.9% -> 59.2% (T=1 -> T=5), gain: +49.4pp

**Why it works:** The running average mechanism in golden cascade cells creates a stateful nonlinearity. Each settling step refines the internal prediction, and the cell output converges to a better fixed point. Standard ReLU neurons are stateless -- re-running them produces the same output.

**Practical implication:** If you use stateful neurons (EMA-based, recurrent, or any neuron with internal memory), test-time settling can be a free accuracy boost. This is related to but distinct from existing "test-time compute" approaches (which typically modify the input or use separate refinement networks). The key insight: **neurons with running averages benefit from iterative inference, neurons without them don't.**

**Caveat:** The consensus network's T=1 accuracy is very low (9.9%) because it was TRAINED with T=5 settling. A fair comparison would train separate models at each T. The finding is more about "stateful neurons need settling" than "settling improves any network."

### 2. Surprise-Gated Learning Rate Stabilizes Training

**What:** Using surprise (prediction error) to gate the learning rate -- `lr_effective = base_lr * clip(surprise / threshold, 0.1, 2.0)` -- beats both fixed and cosine LR schedules.

**Evidence (3 seeds):**
- Fixed LR: 59.2% (mean, but 17.3% on one seed -- catastrophic instability)
- Cosine LR: 80.2%
- Surprise-gated: 83.0%

**Why it works (honest assessment):** The "YES" verdict is partly driven by fixed LR catastrophically failing on one seed (17.3% vs 81.5% on another). Surprise-gating prevented this collapse because when the network is confused (high surprise), it learns aggressively, and when it has already learned something (low surprise), it reduces the learning rate. This acts as a natural **adaptive learning rate** that responds to the network's internal state rather than an external schedule.

**Comparison with cosine:** Surprise-gated (83.0%) beat cosine (80.2%) by 2.8pp. This is meaningful but modest. The bigger win is the **stability**: surprise-gated had no catastrophic failures across seeds (82.3%, 81.4%, 85.4%) while fixed LR had one (81.5%, 78.9%, 17.3%).

**Practical implication:** Using a network's internal surprise/prediction-error as a learning rate signal could serve as a stabilizer. This is conceptually similar to existing adaptive methods (Adam's per-parameter adaptation, gradient clipping) but operates at the sample level: "how surprising is this example to the network right now?" If very surprising, learn more. If not, learn less.

**This is a WEAK YES.** The improvement over cosine is small (2.8pp). The real finding is stability, not peak performance.

---

## Insights That Failed Testing

### 3. Consensus Is Just Ensembling (Test 1: NO)

**What we hoped:** K=5 consensus (multiple neurons per position sharing input) might outperform ensembling 5 independent networks.

**What we found:**
- Consensus K=5: 71.4% +/- 3.8%
- Ensemble of 5 independent K=1: 81.8% +/- 0.8%
- Single K=1: 75.9%

**Why it failed:** The ensemble was dramatically better (+10.4pp). Independent networks with different random initializations explore more of the loss landscape than cells sharing the same weight matrix. Consensus with K>1 is strictly WORSE than standard ensembling because:
1. K cells share the same weight matrix W -- they're less diverse than independent networks
2. The inverse-surprise weighting adds overhead without benefit
3. Independent networks can be trained in parallel

**Verdict:** If you want the benefit of multiple models, use standard ensembling. Consensus adds nothing.

### 4. Surprise Is Not a Useful Confidence Signal (Test 3: NO)

**What we hoped:** After supervised training, surprise (prediction error of golden cascade cells) might correlate with prediction correctness better than softmax entropy.

**What we found:**
- Surprise AUROC: 0.495 (near random, d=0.282)
- Softmax entropy AUROC: 0.574

**Why it failed:** The surprise signal measures how well each cell can predict its own input -- not how confident the network is about classification. After supervised training, the weight matrices encode task-relevant features, but the cell-level surprise (obs - running_avg) doesn't track classification uncertainty. Softmax entropy, which directly measures output distribution spread, is a better (though still weak) confidence signal.

### 5. Surprise Is Not a Useful OOD Detector (Test 4: NO)

**What we hoped:** Surprise would be higher for out-of-distribution inputs (trained on digits 0-7, tested on 8-9).

**What we found:**
- Surprise AUROC: 0.471 (WORSE than random)
- Entropy AUROC: 0.729
- Max-softmax AUROC: 0.728

**Why it failed:** Surprise was almost identical for ID and OOD inputs. The golden cascade cells' running averages calibrate to new inputs within the settling steps, regardless of whether those inputs are in-distribution. The cells are too adaptive -- they quickly accommodate any input, destroying the OOD signal. Standard softmax entropy was far superior for OOD detection.

### 6. The Golden Ratio (0.618) Is Not an Optimal Decay Rate (Test 5: NO)

**What we hoped:** The golden ratio decay rate (0.618) would be optimal for the running average mechanism.

**What we found:**
| Decay | Accuracy (mean +/- std) |
|-------|------------------------|
| 0.3   | 12.5% +/- 1.2% |
| 0.5   | 15.1% +/- 8.1% |
| 0.618 | 57.8% +/- 30.1% |
| 0.7   | 80.8% +/- 3.2% |
| 0.9   | 86.1% +/- 0.6% |

**Why it failed:** Higher decay rates (slower adaptation) perform better because they provide more stable representations. Decay 0.9 was best AND most stable (0.6% std vs 30.1% for 0.618). The golden ratio is not special -- it's actually in an unstable regime where small perturbations cause large performance swings.

**Practical implication (REVERSE insight):** If using EMA-based neurons, use a HIGH decay rate (0.9+). The golden ratio 0.618 is too aggressive and unstable.

---

## Summary: What 20 Phases Taught Us About ML

### The Honest Assessment

After 20 phases of research on golden cascade neurons, the core hypothesis -- that biologically-inspired surprise-minimization dynamics can improve ML -- is **mostly falsified**:

1. **Surprise-minimization as a learning rule is useless** (43.9% = random features). Phase A proved this conclusively.

2. **Surprise-minimization as an inference mechanism is also useless** (this experiment). Surprise doesn't correlate with correctness, doesn't detect OOD, and doesn't outperform standard softmax-based methods.

3. **The golden ratio has no practical value** as a hyperparameter for these dynamics. Higher decay rates are better and more stable.

4. **Consensus (K>1) is just worse-than-standard ensembling.** The shared weight matrix limits diversity.

### What DID We Learn

Two modest findings survived:

1. **Stateful neurons need settling; stateless ones don't.** This is architecturally informative: if you design networks with internal state (EMA, running averages, recurrent connections), budget compute for settling at inference time. This is a design principle, not a performance improvement.

2. **Surprise-gated learning rate provides training stability.** Using a network's own prediction error to modulate learning rate prevents catastrophic training failures. The effect is modest (+2.8pp over cosine) but the stability benefit is real. This connects to the broader insight that **adaptive learning rates that respond to per-sample difficulty are valuable** -- which is known (curriculum learning, self-paced learning) but rarely implemented at the neuron level.

### The Meta-Lesson

The research arc taught us more about **what doesn't transfer from biology to ML** than what does:

- Self-organizing cell soup dynamics produce beautiful emergent behavior but don't solve classification
- Predictive coding / surprise minimization is an elegant theory but produces no useful gradient toward task performance
- The golden ratio appears in many natural systems but doesn't confer special properties on neural network dynamics
- Biological plausibility and ML performance are largely orthogonal concerns

The two positive findings (settling for stateful neurons, surprise-gated LR stability) are interesting but modest. They don't justify building golden cascade networks -- a standard ReLU network with Adam optimizer will outperform all of this.

**If you're building ML systems and read nothing else: use standard architectures with standard optimizers. None of the golden cascade mechanisms improve on backprop + Adam + ReLU for classification.**

---

## Appendix: Experimental Details

- **Dataset:** MNIST, 10K train, 2K test, PCA to 50 dimensions, normalized
- **Architecture:** [50->32->16->10] for all tests
- **Seeds:** 42, 123, 789 (3 seeds per test for statistics)
- **Training:** 10 epochs, lr=0.01 base, pseudo-backprop (all_supervised)
- **Consensus:** K=3 default, T_settle=5, no room, golden cascade enabled
- **Total runtime:** ~33 minutes (1971 seconds)
