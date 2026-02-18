# Phi Initialization Experiment Results

**Date:** 2026-02-07
**Experiment:** Testing φ-related neural network weight initialization scales
**Hypothesis:** Ouroboros framework predicts φ ≈ 1.618 or 1/φ ≈ 0.618 should be optimal at critical points of self-referential systems (neural networks with training feedback)

---

## Executive Summary

**Result:** INCONCLUSIVE - Phi-based initialization performs comparably to standard methods.

**Key Finding:** All initialization methods tested (standard, phi-based, and controls) achieved similar final test accuracy (98.77% - 98.93%), with differences within noise. The best phi-based method (phi_v3 = 1.618) tied for first place with LeCun initialization, but the advantage is not statistically significant.

**Verdict:** This experiment does NOT provide strong evidence for or against the framework prediction. The task may have been too easy (all methods converged well), or initialization effects may be secondary compared to architecture and optimization for this problem.

---

## Experimental Setup

### Architecture
- **Network:** Feedforward 784 → 256 → 128 → 10
- **Activations:** ReLU + Dropout (0.3)
- **Loss:** CrossEntropyLoss
- **Optimizer:** Adam (lr=0.001)

### Dataset
- **Source:** Synthetic (MNIST unavailable - torchvision not installed)
- **Type:** Non-linear 10-class classification with limited data
- **Samples:** 2,000 total (1,400 train, 600 test)
- **Features:** 784 dimensions
- **Difficulty:** Moderate (non-linear decision boundaries, high noise, limited training data)

### Initialization Methods Tested

| Method | Scale Function | Value @ fan_in=256 | Type |
|--------|---------------|-------------------|------|
| xavier | sqrt(2/(fan_in + fan_out)) | 0.0789 | Standard |
| he | sqrt(2/fan_in) | 0.0884 | Standard |
| lecun | sqrt(1/fan_in) | 0.0625 | Standard |
| phi | (1/φ)/sqrt(fan_in) | 0.0386 | Phi-based |
| phi_v2 | sqrt(1/φ²)/sqrt(fan_in) | 0.0386 | Phi-based |
| phi_v3 | φ/sqrt(fan_in) | 0.1011 | Phi-based |
| small | 0.3/sqrt(fan_in) | 0.0188 | Control (too small) |
| large | 2.0/sqrt(fan_in) | 0.1250 | Control (too large) |

### Experimental Protocol
- **Seeds:** 5 independent runs per initialization
- **Epochs:** 30 per run
- **Device:** CPU (CUDA unavailable)
- **Duration:** ~45 minutes total

---

## Results

### Summary Table

| Rank | Method | Test Accuracy (%) | Conv (epochs) | Init Grad Mean | Init Grad Std |
|------|--------|-------------------|---------------|----------------|---------------|
| 1 | lecun | 98.93 ± 0.31 | 1.0 ± 0.0 | 0.00010 | 0.00814 |
| 2 | phi_v3 | 98.93 ± 0.37 | 1.0 ± 0.0 | 0.00086 | 0.02496 |
| 3 | phi | 98.87 ± 0.29 | 1.0 ± 0.0 | -0.00001 | 0.00308 |
| 4 | phi_v2 | 98.87 ± 0.29 | 1.0 ± 0.0 | -0.00001 | 0.00308 |
| 5 | large | 98.87 ± 0.22 | 1.0 ± 0.0 | 0.00147 | 0.04041 |
| 6 | xavier | 98.83 ± 0.35 | 1.0 ± 0.0 | 0.00035 | 0.01350 |
| 7 | he | 98.83 ± 0.28 | 1.0 ± 0.0 | 0.00055 | 0.01803 |
| 8 | small | 98.77 ± 0.17 | 1.0 ± 0.0 | -0.00000 | 0.00076 |

**Note:** φ ≈ 1.618034, 1/φ ≈ 0.618034

### Performance by Category

| Category | Methods | Mean Accuracy | Range |
|----------|---------|---------------|-------|
| Phi-based | phi, phi_v2, phi_v3 | 98.89% | 98.87% - 98.93% |
| Standard | xavier, he, lecun | 98.87% | 98.83% - 98.93% |
| Control | small, large | 98.82% | 98.77% - 98.87% |

**Difference (Phi vs Standard):** +0.02% (not statistically significant)

### Training Curves

All methods converged extremely fast (convergence epoch = 1.0 for all methods), indicating the task became too easy after adding regularization. All initialization methods achieved >90% of final accuracy within the first epoch.

**Observation:** This suggests initialization effects are minimal for this particular problem once the network is large enough and regularized.

---

## Analysis

### Does φ-based initialization outperform standard methods?

**No clear advantage.** The results show:

1. **Best phi-based method (phi_v3 = 1.618):** Tied for 1st place with LeCun
2. **Other phi methods (phi, phi_v2 = 0.618):** Ranked 3rd-4th, within 0.06% of best
3. **Mean phi performance:** Marginally better than standard (+0.02%), well within noise

### Statistical Significance

With standard deviations of 0.17% - 0.37% and only 5 seeds per method, the differences between top methods are NOT statistically significant. The 0.17% spread between best and worst methods is comparable to the error bars.

### Initial Gradient Health

All initialization methods produced healthy initial gradients:
- No NaN or Inf values
- Gradient means near zero (good)
- Gradient standard deviations in reasonable range (0.00076 - 0.04041)

**Observation:** Even the "control" methods (small=0.3, large=2.0) didn't cause gradient pathologies, suggesting the network architecture and optimizer are robust.

### Convergence Speed

All methods converged in 1 epoch to 90% of final accuracy. This indicates:
- The task is relatively easy for all tested scales
- Initialization differences are masked by strong optimizer (Adam)
- Need harder task or different architecture to amplify initialization effects

---

## Interpretation

### Does this support or refute the framework prediction?

**Neither strongly.**

**Arguments that this is inconclusive (not a refutation):**

1. **Task too easy:** All methods converged immediately, washing out initialization effects
2. **Adam optimizer:** Adaptive learning rates may compensate for initialization differences
3. **Regularization:** Dropout may have dominated over initialization effects
4. **Synthetic data:** The dataset may not have the structure that requires edge-of-chaos initialization
5. **Limited scope:** Only tested one architecture, one task, one optimizer

**Arguments that this weakens the prediction:**

1. **No dramatic advantage:** If φ were truly optimal, we'd expect clearer separation
2. **phi_v3 (1.618) best, not 1/φ (0.618):** Framework predicts 1/φ ≈ 0.618, but phi=1.618 performed slightly better
3. **Competitive with standard:** Standard methods (Xavier, He, LeCun) are already optimized empirically; matching them is not surprising

### What would constitute stronger evidence?

**For the prediction:**
- φ-based methods outperform standard by >1% (multiple standard deviations)
- Advantage appears consistently across multiple architectures/tasks
- Advantage is largest on "critical" tasks (edge of chaos complexity)

**Against the prediction:**
- φ-based methods consistently underperform standard methods
- No task can be found where φ initialization helps

### Current status: Inconclusive

The prediction is **not falsified**, but **not validated** either. This is a null result with all methods performing similarly.

---

## Limitations

1. **Synthetic dataset:** MNIST unavailable (torchvision not installed), used synthetic data which may not have realistic structure
2. **Task difficulty:** Even with regularization and limited data, the task converged too fast
3. **Single architecture:** Only tested one feedforward network size
4. **Single optimizer:** Only tested Adam (adaptive methods may hide initialization effects)
5. **Limited seeds:** 5 seeds per method gives large error bars
6. **CPU-only:** Slow execution limited experiment scope

---

## Recommendations for Future Work

To properly test the phi initialization hypothesis:

1. **Use real datasets:** MNIST, CIFAR-10, or ImageNet
2. **Test harder architectures:**
   - Very deep networks (ResNet-50+) where initialization matters more
   - Recurrent networks (LSTM, GRU) which are more sensitive to initialization
   - Transformers at scale
3. **Use SGD without momentum:** Adaptive optimizers (Adam) may mask initialization effects
4. **Vary task difficulty:** Test on tasks at different complexity levels
5. **More seeds:** Use 20-50 seeds for statistical significance
6. **Measure critical behavior:**
   - Track gradient flow through layers
   - Measure effective rank of representations
   - Look for signatures of criticality (power laws, etc.)
7. **Compare to "edge of chaos" initialization papers:** There's existing literature on critical initialization in RNNs

---

## Conclusion

**This experiment does NOT provide evidence that φ-related initialization scales are superior to standard methods (Xavier, He, LeCun) for neural networks.**

**Key findings:**
1. Phi-based initialization (0.618, 1.618) performs **comparably** to standard methods
2. Best phi method (phi_v3 = 1.618) tied for first, but within noise
3. All methods achieved similar final accuracy (98.77% - 98.93%)
4. All methods converged extremely fast (1 epoch), suggesting task too easy

**Honest assessment:**
- The Ouroboros prediction is **NOT SUPPORTED** by this experiment
- However, experiment limitations (synthetic data, easy task, single architecture) mean we **CANNOT CONCLUDE** the prediction is wrong
- A null result: initialization doesn't matter much for this particular problem

**Practical implication:**
If using PyTorch on CPU with simple feedforward networks and Adam optimizer, standard initialization (He, Xavier, LeCun) works fine. No need to use phi-based initialization unless working on:
- Very deep networks
- Recurrent architectures
- Tasks at critical complexity
- Situations where every 0.1% matters

**For the framework:**
This is a **weak test** that neither confirms nor denies the edge-of-chaos prediction. Need harder experiments to properly evaluate the hypothesis.

---

## Appendices

### A. Raw Data

Full results saved to: `C:\Users\ericl\Documents\Projects\vacuum_physics\python\phi_init_results.json`

### B. Code

Experiment code: `C:\Users\ericl\Documents\Projects\vacuum_physics\python\phi_initialization_test.py`
Analysis code: `C:\Users\ericl\Documents\Projects\vacuum_physics\python\analyze_results.py`

### C. Reproducibility

```bash
cd C:\Users\ericl\Documents\Projects\vacuum_physics\python
python phi_initialization_test.py  # Run experiment (30-60 min)
python analyze_results.py         # Analyze results
```

Requirements:
- PyTorch 2.8.0+ (CPU)
- NumPy
- Python 3.13

### D. Key Constants

- Golden ratio: φ = 1.618033988749895
- Inverse: 1/φ = 0.618033988749895
- Square: φ² = 2.618033988749895

---

**Generated:** 2026-02-07
**Experiment Duration:** ~45 minutes
**Total Runs:** 40 (8 methods × 5 seeds)
**Code Status:** Working, tested, reproducible
