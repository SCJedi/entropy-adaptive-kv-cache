# Golden Ratio in Self-Gating Neural Networks: Structural Investigation

**Date:** 2026-02-09
**Status:** Complete — Outcome 3 (null result for standard activations; tautological for Ouroboros)

## Executive Summary

The hypothesis that self-gating activations (GELU, Mish, Swish) produce the palindromic quadratic D² - 3D + 1 = 0 from the Ouroboros framework is **not supported**. The proximity of GELU's empirical critical scale (~1.382) to 3-φ (1.38197) is a finite-width/finite-depth artifact not reproduced by mean-field theory at any level.

## 1. The Hypothesis

The Ouroboros framework derives D² - 3D + 1 = 0 from self-referential DOF counting, yielding φ² as a solution and (3-φ) as a stability exponent. Self-gating ML activations f(x) = x·g(x) are also self-referential (the signal gates itself). The hypothesis: this shared self-referential structure produces the same palindromic quadratic, making (3-φ) the critical initialization scale.

## 2. Three Theoretical Regimes Tested

### Regime A: Simplified Critical Scale (χ₁ = 1 at fixed q = 1)

The simplest criticality condition: σ_w = 1/√E[f'(z)² | z ~ N(0,1)].

| Activation | σ_w_crit | |Δ(3-φ)| | T | D_eff | D²-3D+1 | D+1/D |
|---|---|---|---|---|---|---|
| GELU | 1.4811 | 0.099 | 0.425 | 2.352 | -0.525 | 2.777 |
| Swish | 1.6233 | 0.241 | 0.356 | 2.811 | +0.468 | 3.167 |
| Mish | 1.4448 | 0.063 | 0.452 | 2.211 | -0.745 | 2.663 |
| Ouroboros(λ=0.3757) | **1.38197** | **0.000004** | 0.514 | 1.944 | -1.053 | 2.459 |

**Reference:** 3-φ = 1.381966, φ²/5 = 0.523607

**Key findings:**
- GELU: σ_w = 1.481, **not** 1.382. Off by 7%.
- Swish: σ_w = 1.623, off by 17%.
- Mish: σ_w = 1.445, off by 5%.
- Ouroboros: σ_w = 1.38197, matching 3-φ to 6 decimal places — **but λ=0.3757 was chosen to make this happen** (see `ouroboros_exact.py`: λ was tuned so E[f'²] = 1/(3-φ)²).
- The palindromic test D²-3D+1 = 0 fails for ALL activations (values range from -1.05 to +0.47).
- The gated variance fraction T ≠ φ²/5 for any activation (closest: Ouroboros at T=0.514 vs 0.524).

### Regime B: Full MFT (Forward Fixed Point + χ₁ = 1 Simultaneously)

For zero-bias self-gating activations, the forward variance map q → σ_w² · E[f(z)²|z~N(0,q)] has:
- Ratio R(q) = E[f²|q]/q increasing monotonically from ~0.25 (q→0) to ~0.5 (q→∞)
- A non-trivial fixed point only when σ_w² ∈ (2, 4), but it is **always unstable** (map slope > 1)
- χ₁ > 1 at every finite fixed point
- The only joint solution has q* → ∞, σ_w → √2 (the ReLU limit)

**Result:** The full MFT critical point is **degenerate** for GELU, Swish, and Mish. There is no finite self-consistent (q*, σ_w) satisfying both forward and backward criticality. The critical initialization is σ_w = √2 ≈ 1.414, identical to ReLU — not activation-specific and not phi-related.

### Regime C: Finite-Depth Lyapunov Trajectory

Starting from q₀ = σ_w² (unit-variance input through first layer), iterating for L layers:

| Activation | L=5 | L=10 | L=30 | L=100 | L→∞ |
|---|---|---|---|---|---|
| GELU | 1.415 | 1.423 | 1.458 | 1.468 | ~1.468 |
| Swish | 1.487 | 1.512 | 1.553 | 1.559 | ~1.559 |
| Mish | 1.418 | 1.420 | 1.436 | 1.451 | ~1.451 |
| Ouroboros | 1.346 | 1.349 | 1.360 | 1.372 | ~1.374 |

**Result:** None of these match 3-φ = 1.382. They converge to activation-specific values intermediate between √2 and the Regime A values. The trajectory dynamics involve a bifurcation at the unstable forward fixed point, not a smooth Lyapunov zero.

## 3. Where Did "1.382" Come From?

The earlier empirical finding (in `phi_criticality_experiment.py`) measured the gradient norm Lyapunov zero-crossing for GELU networks at depth=30, width=256 using PyTorch. This gave ~1.382.

But the MFT prediction for GELU at L=30 is **1.458**, not 1.382. The discrepancy is ~5%. Possible sources:
1. **Finite-width corrections** (N=256 is far from infinite)
2. **Gradient norm definition** (includes forward variance effects, not just backward χ₁)
3. **Statistical fluctuations** in the empirical measurement
4. **Nonlinear interactions** between forward/backward propagation at finite width

The 1.382 value matches 3-φ to 0.02%, but this precision is illusory given the ~5% discrepancy between empirical and theoretical predictions.

## 4. Why the Palindromic Quadratic Does NOT Arise

For f(x) = x·g(x), the forward criticality decomposition gives:

**E[f'(z)²] = E[g²] + 2·E[z·g·g'] + E[z²·g'²]**

This decomposes χ₁ into: gate transmission (E[g²]), cross-coupling (2E[zgg']), and gate sensitivity (E[z²g'²]). For the palindromic quadratic to arise, one would need:

**D_eff = 1/T where T = E[u²g(√q·u)²]**

to satisfy D² - 3D + 1 = 0, i.e., D + 1/D = 3.

The actual values of D + 1/D:
| GELU | Swish | Mish | Ouroboros |
|---|---|---|---|
| 2.777 | 3.167 | 2.663 | 2.459 |

None equal 3. The palindromic structure requires a specific relationship between the gate's tail behavior and the Gaussian measure that none of these gates produce. The GELU gate (Gaussian CDF) is the "wrong shape" — its transition width and tail decay don't produce the palindromic self-consistency.

## 5. What IS the Actual Structure?

At the simplified critical point (Regime A), the key identity is simply:

**σ_w² · E[f'(z)² | z ~ N(0, 1)] = 1**

This is one equation in one unknown. There is no second constraint that forces the palindromic quadratic. The Ouroboros D² - 3D + 1 = 0 comes from TWO self-consistency conditions (D observes D observers creating a second-order equation). The ML criticality has only ONE condition.

The "self-referential" nature of f(x) = x·g(x) is a different kind of self-reference from the Ouroboros DOF counting. In GELU, x gates itself — but this is a pointwise operation on a scalar. In the Ouroboros framework, D counts itself — a logical self-reference that generates the quadratic through the fixed-point equation D = D_obs + D_dof(D). These produce different algebra.

## 6. Assessment of the Ouroboros Activation

The Ouroboros activation f(x) = x·(λ + (1-λ)·σ(x)) achieves σ_w = 3-φ by **construction**: λ was numerically tuned so that E[f'²|N(0,1)] = 1/(3-φ)² exactly. This is a design choice, not a discovery. The activation doesn't satisfy the palindromic quadratic (D+1/D = 2.46 ≠ 3), and at the full MFT level, its true critical point is σ_w ≈ 1.324 (not 3-φ).

## 7. Proven Results vs. Conjectures

### Proven (numerically verified to machine precision):
- E[GELU'(z)² | z~N(0,1)] = 0.4559 (not φ²/5 = 0.5236)
- The simplified critical scale for GELU is 1.481 (not 3-φ = 1.382)
- The full MFT critical point for all zero-bias self-gating activations is σ_w = √2, q* → ∞
- The palindromic quadratic D²-3D+1=0 is not satisfied by any tested activation at any operating point

### Falsified:
- ~~5T ≈ φ² across activations~~ — 5T ranges from 1.78 (Swish) to 2.57 (Ouroboros); φ² = 2.618
- ~~The palindromic quadratic holds for self-gating activations~~ — D+1/D ranges from 2.46 to 3.17; not 3
- ~~σ_w_crit = 3-φ for GELU~~ — MFT gives 1.468-1.481; empirical 1.382 is a finite-size effect

### Open:
- Why does the finite-width empirical value happen to be near 3-φ? Is this a O(1/√N) correction with a coefficient that involves φ, or a coincidence?
- At what width N does the empirical critical scale converge to the MFT prediction?

## 8. Conclusion

**Outcome 3: No consistent relationship.** The golden ratio does not emerge structurally from the criticality conditions of self-gating neural network activations. The observed empirical proximity of GELU's critical scale to 3-φ is a finite-size effect not captured by mean-field theory. The Ouroboros activation achieves σ_w = 3-φ by parameter tuning, not from structural necessity.

The self-referential structure of f(x) = x·g(x) is qualitatively different from the Ouroboros self-referential DOF counting. Both involve self-reference, but they produce different mathematical constraints: one equation (ML criticality) vs. a palindromic quadratic (Ouroboros). The coincidence of (3-φ) is numerical, not algebraic.

## Appendix: Verification Checks

All numerical results verified by:
- χ₁ = σ_w² · E[f'²] = 1.000000 at all Regime A critical points (by construction)
- Gauss-Hermite quadrature with 100 points (converged to >10 digits for smooth integrands)
- Forward fixed-point residuals < 10⁻¹² where applicable
- Cross-checked E[GELU'²|N(0,1)] against direct scipy.integrate.quad: agreement to 10⁻¹⁰

## Appendix: Reproducibility

All results produced by: `python/phi_ml_investigation.py`
Runtime: ~1-2 minutes on Core i7
Dependencies: numpy, scipy (standard scientific Python stack)
