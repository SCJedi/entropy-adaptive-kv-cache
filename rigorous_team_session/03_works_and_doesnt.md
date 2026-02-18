# What Works and What Doesn't

## Rigorous Team Verification Session -- Definitive Assessment
**Date**: February 1, 2026
**Team**: Feynman (lead), Kovacs, Park, Santos, Nakamura, Brennan

---

## WORKS

### W-1: Dimensional Uniqueness of rho = m^4 c^5 / hbar^3
**Evidence**: The 3x3 linear system has unique solution a=4, b=5, d=-3. Determinant = -1.
**Strength**: Mathematical proof, no loopholes within {m, c, hbar}.
**Caveat**: Including G opens a one-parameter family. Coefficient K=1 is from construction, not from dimensional analysis.
**Verified by**: Park (proof), Kovacs (numerical sensitivity analysis).

### W-2: Coherent State Construction at |alpha|^2 = 1/2
**Evidence**: Standard QM gives E = hbar*omega*(|alpha|^2 + 1/2). For |alpha|^2 = 1/2: E = hbar*omega = mc^2.
**Strength**: Textbook quantum mechanics. Algebraically forced by energy constraint.
**Verified by**: Park (algebraic proof), Kovacs (numerical).

### W-3: Orthogonality / Unitary Inequivalence of Mode and Cell Vacua
**Evidence**: <0|Omega> = exp(-N/4) -> 0. In continuum: unitarily inequivalent by Shale-Stinespring.
**Strength**: Rigor A. Multiple proof methods agree.
**Verified by**: Park, Nakamura.

### W-4: Cell Vacuum as Legitimate AQFT State
**Evidence**: Well-defined state on Weyl algebra. Satisfies positivity, normalization, Hadamard. Same mathematical family as thermal and SSB vacua.
**Strength**: Rigor A (finite), Rigor B (infinite). Standard AQFT methods.
**Verified by**: Park (proof review).

### W-5: Reeh-Schlieder Evasion
**Evidence**: Cell vacuum breaks Poincare invariance (preferred lattice). Spectrum condition fails. Reeh-Schlieder hypotheses not met.
**Strength**: Same evasion mechanism as thermal states. No controversy.
**Verified by**: Park, Nakamura.

### W-6: Hadamard Condition Satisfied
**Evidence**: W_Omega(x,y) = W_0(x,y) + F(x)F(y), F smooth. UV singularity structure unchanged.
**Strength**: Rigor A. Enables renormalized T_mu_nu computation.
**Verified by**: Park.

### W-7: Self-Consistency on Curved Spacetime (10^{-69})
**Evidence**: Backreaction correction delta_rho/rho ~ R*lambda_C^2 ~ 3.6 x 10^{-69}. Stable fixed point.
**Strength**: Valid for all post-nucleosynthesis cosmology.
**Verified by**: Park, Santos.

### W-8: Self-Duality Theorem (Three Forms)
**Evidence**: Legendre self-duality of x^2/2. Fourier self-duality of exp(-x^2/2). Energy equipartition in coherent states. All connected; uniqueness proven.
**Strength**: Rigor A. Genuine mathematical insight connecting framework to fundamental structures.
**Verified by**: Park.

### W-9: Numerical Robustness of Predictions
**Evidence**: Sum = 60.8 +/- 0.7 meV is stable under Hubble tension (< 1 meV variation), oscillation parameter updates (< 0.5% change), and different calculation methods.
**Strength**: Fourth-root scaling (m ~ rho^{1/4}) provides natural insensitivity to input uncertainties.
**Verified by**: Kovacs (full error propagation).

### W-10: Falsifiability
**Evidence**: Specific predictions with no free parameters: Sum ~ 61 meV, normal ordering, w = -1. Will be tested by CMB-S4, JUNO, DUNE, Euclid within ~10 years.
**Strength**: Rare in theoretical physics. Framework cannot accommodate Sum < 58 meV or inverted ordering.
**Verified by**: Santos (experimental roadmap), Brennan (no escape hatch).

### W-11: Honest Self-Assessment in Documentation
**Evidence**: Knowledge base explicitly retires circular claims, demotes failed conjectures, flags biggest gaps, quantifies experimental tension.
**Strength**: Intellectual integrity. Framework investigators confronted weaknesses rather than hiding them.
**Verified by**: Brennan (adversarial review of documentation).

### W-12: Code Correctness
**Evidence**: All code (constants.py, coherent_states.py, vacuum_energy.py) independently verified.
**Strength**: No bugs, correct constants, results match analytical formulas to machine precision.
**Verified by**: Kovacs.

---

## DOESN'T WORK

### D-1: Mass Selection Mechanism (CRITICAL)
**Evidence against**: The formula rho = m^4 c^5/hbar^3 applies to EVERY massive particle. If all species contribute, the total is dominated by the heaviest (top quark: 10^{33} J/m^3). Even neutrinos alone: m_3 contributes 2 x 10^5 times more than m_1. No mechanism excludes heavier species. All proposed explanations (IR dominance, phase transition, hierarchical decoupling) are unformalized hand-waving.
**Severity**: POTENTIALLY FATAL. Without a mass selection mechanism, the framework's prediction is wrong by > 10^{35} orders of magnitude.
**What would resolve it**: A derivation showing that cell vacua for heavier species are unstable, don't couple to gravity, or are cancelled by interactions.

### D-2: Black Hole Entropy (CRITICAL)
**Evidence against**: Cell vacuum has S = 0 (zero entanglement) for any bipartition, including across black hole horizons. Bekenstein-Hawking gives S = A/(4 l_P^2) ~ 10^{76} for a solar-mass BH. This is not a quantitative discrepancy -- it's zero vs a large number.
**Severity**: EXISTENTIAL. If the entanglement interpretation of BH entropy is correct, the framework is inconsistent.
**What would resolve it**: A concrete non-entanglement mechanism for BH entropy, or a formalized "scale-dependent vacuum" with the cell vacuum at cosmological scales and the mode vacuum near BH horizons.

### D-3: QCD/Higgs/Electroweak Vacuum Energy (CRITICAL)
**Evidence against**: The QCD condensate contributes ~ 10^{-3} J/m^3 (finite, well-understood). The Higgs potential and electroweak symmetry breaking contribute ~ 10^8 J/m^3 (finite, well-understood). These exceed the observed dark energy density by 7-18 orders of magnitude. The framework does not address them AT ALL.
**Severity**: SEVERE. The "category error" argument addresses the divergent zero-point piece but not these finite Standard Model contributions. The full cosmological constant problem requires explaining all of them.
**What would resolve it**: Either (a) a demonstration that these contributions don't gravitate (radical but possible), or (b) an extension of the cell vacuum construction to non-perturbative QFT sectors.

### D-4: w = -1 Not Derived (SERIOUS)
**Evidence against**: On curved spacetime, the classical displacement field gives w = -2/3 (positive pressure from spatial gradients). The quantum zero-point contribution is needed for w = -1 but depends on the renormalization prescription. No rigorous computation exists.
**Severity**: SERIOUS but potentially tractable. The calculation is well-defined (Hadamard point-splitting) and could be done.
**What would resolve it**: A complete <T_ij> computation for the cell vacuum on FRW spacetime.

### D-5: Category Error Is Overstated (MODERATE)
**Evidence against**: <0|T_00(x)|0> is divergent, not undefined. The mode vacuum IS a normalizable state in Fock space. The analogy to <p|x|p> is illustrative but not exact (<p|x|p> involves a non-normalizable state). Standard renormalization handles divergences. The "category error" framing implies the calculation is illegitimate, but it's the standard approach to QFT with well-understood divergences.
**Severity**: MODERATE. The physical insight (mode vacuum has no position structure) is correct. The framing as "category error" oversells it.
**What would resolve it**: Reframing as "the mode vacuum is not the appropriate state for computing gravitational vacuum energy" rather than "the calculation is a category error."

### D-6: No Dynamical Content (MODERATE)
**Evidence against**: The framework is a static construction, not a theory with equations of motion. There is no action principle, no Hamiltonian from which the cell vacuum emerges as a ground state, no dynamical mechanism for selecting the cell vacuum over other states. It's a "solution looking for an equation" (Brennan).
**Severity**: MODERATE but conceptually important. A construction that gives the right number is less compelling than a theory that derives the right number.
**What would resolve it**: Deriving the cell vacuum from a physical principle (e.g., showing it's the ground state of an effective gravitational-sector Hamiltonian).

### D-7: Predictions Not Uniquely Distinguishable (MODERATE)
**Evidence against**: Any model with normal ordering and m_1 ~ 1-5 meV predicts Sum ~ 59-64 meV. The framework's testable predictions overlap heavily with generic normal-ordering scenarios. The truly distinctive prediction (m_1 = 2.3 meV specifically) is untestable with current or near-future technology.
**Severity**: MODERATE. The framework IS more specific than "generic normal ordering" but can't demonstrate this experimentally.
**What would resolve it**: Technology to measure m_1 directly at the meV scale.

---

## UNKNOWN (What Would Resolve It)

### U-1: The Circularity Boundary
**Question**: Where exactly does the circular reasoning end and the non-circular predictions begin?
**Current status**: The rho_Lambda -> m_1 extraction is circular. Sum, ordering, w are non-circular. But Sum is dominated by oscillation-data-determined m_3, making the framework's specific contribution (m_1 = 2.3 meV) empirically invisible.
**What would resolve it**: Independent measurement of m_1 at meV precision.

### U-2: DESI DR2 Tension
**Question**: Will the Sum < 53 meV bound strengthen or weaken?
**Current status**: 1.5-2 sigma tension. Shared with all normal-ordering models.
**What would resolve it**: DESI DR3+ (2026-2028), Euclid (2025-2030), CMB-S4 (2030s).

### U-3: Whether 40% or 17% Is the Right Probability
**Question**: Previous internal assessments gave ~40%; our team gives ~17%. Which is more accurate?
**Current status**: The discrepancy arises because our team weighted the mass selection, QCD/Higgs, and BH entropy problems more heavily.
**What would resolve it**: Any progress on the CRITICAL problems (D-1 through D-3).

### U-4: Formal Duality Between the Two Vacua
**Question**: Is there a mathematical duality (not necessarily Fenchel) relating the mode and cell vacua?
**Current status**: Fenchel duality failed. The structural analogy (position vs momentum) is genuine but not formalized. Perhaps an AQFT-internal duality exists.
**What would resolve it**: New mathematical approach beyond convex analysis.

### U-5: Self-Duality as Selection Criterion
**Question**: Does the self-duality of coherent states EXPLAIN why nature selects the cell vacuum, or is it merely a property of the selected construction?
**Current status**: Self-duality is proven. Its role as a selector is conjectured.
**What would resolve it**: A theorem showing that self-dual states are uniquely selected by some physical criterion.

### U-6: Energy Density from AQFT
**Question**: Can omega_Omega(T_00^{ren}) be computed via Hadamard point-splitting?
**Current status**: The state is Hadamard, so the computation is well-defined. But Wald's axioms leave a cosmological constant ambiguity. The framework's rho = m^4 c^5/hbar^3 amounts to fixing this ambiguity.
**What would resolve it**: Completing the AQFT computation and seeing if the renormalization condition has a natural physical motivation.

### U-7: Interaction Effects
**Question**: How do interactions (QED, QCD, electroweak) modify the cell vacuum construction?
**Current status**: Completely unexplored. The construction uses free fields.
**What would resolve it**: Extension to interacting field theories, even perturbatively.

---

## INDIVIDUAL PROBABILITY ASSESSMENTS

| Team Member | Role | Probability | Primary Reasoning |
|-------------|------|-------------|-------------------|
| Dr. Park | Math Physicist | 15-20% | No derivation from physical principle; construction is ad hoc |
| Dr. Kovacs | Computational | 25-30% | Numerics solid; mass selection is the killer |
| Dr. Santos | Experimental | 20-25% | DESI tension; predictions not uniquely distinguishable |
| Dr. Nakamura | Quantum Info | 10-15% | Black hole entropy nearly fatal |
| Dr. Brennan | Devil's Advocate | 5-10% | Multiple fatal problems (mass selection, QCD/Higgs, BH entropy) |
| Feynman | Team Lead | 15-20% | Insight is real; implementation has severe gaps |

### Mean: ~17%
### Median: ~17.5%
### Range: 5-30%

---

## CONSENSUS VIEW

The Two Vacua framework is a **mathematically rigorous, internally consistent, and refreshingly honest** theoretical proposal. Its strengths are real:

- The dimensional analysis is unique
- The AQFT foundations are solid
- The self-duality structure is elegant
- The predictions are sharp and falsifiable with no free parameters
- The documentation is admirably self-critical

Its weaknesses are also real and severe:

- **Mass selection**: No mechanism to exclude heavier species. This alone makes the total prediction wrong by > 10^{35} orders of magnitude.
- **Black hole entropy**: Zero entanglement contradicts Bekenstein-Hawking. Existential threat.
- **QCD/Higgs**: Finite vacuum energy contributions of 10^{-3} to 10^8 J/m^3 are completely unaddressed.
- **w = -1**: Not derived on curved spacetime.
- **No dynamical content**: The framework is a construction, not a theory.

The **consensus probability of ~17%** is LOWER than previous internal assessments (~40%) because:
1. This team applied broader scrutiny, especially to the finite SM vacuum energy contributions
2. The mass selection problem was examined quantitatively (heavier neutrinos alone contribute 10^5 x more)
3. The black hole entropy problem was given greater weight
4. The non-uniqueness of the testable predictions (overlap with generic normal ordering) was identified

The framework will be **decisively tested within ~10 years** by CMB-S4 (Sum sensitivity ~ 15-20 meV), Euclid (Sum ~ 30 meV), JUNO (mass ordering > 3 sigma), and DUNE (ordering 5 sigma). If Sum ~ 61 meV is detected, the probability assessment would increase substantially. If Sum < 50 meV at > 3 sigma, the framework is dead.

---

## WHAT SURVIVES REGARDLESS

Even if the specific framework fails, the following insights are independently valuable:

1. **The mode vacuum has no position structure**: This is established physics. Its implications for gravitational vacuum energy deserve more attention.
2. **The cell vacuum is a legitimate AQFT state**: This extends the zoo of known well-defined states and may be useful for other purposes.
3. **The self-duality of coherent states**: This mathematical structure connects Legendre, Fourier, and quantum mechanical dualities in a proven, unified way.
4. **The d-dimensional ratio formula**: C_d = 2(d+1)(2pi)^d/Omega_d is a new, proven result.
5. **The falsifiability standard**: A framework that makes specific, parameter-free predictions and documents its own failures sets a standard for theoretical honesty.
