# Verified Results Ledger

## Rigorous Team Verification Session
**Date**: February 1, 2026
**Team**: Feynman (lead), Kovacs, Park, Santos, Nakamura, Brennan

---

## FORMAT

```
CLAIM: [statement]
TESTED BY: [who]
METHOD: [how they tested it]
RESULT: [what they found]
VERDICT: VERIFIED / REFUTED / INCONCLUSIVE / PARTIALLY CORRECT
NOTES: [details, caveats]
```

---

## SECTION 1: CORE MATHEMATICS

---

CLAIM: rho = m^4 c^5 / hbar^3 is the unique power-law combination of (m, c, hbar) with dimensions of energy density.
TESTED BY: Park
METHOD: Solved the 3x3 linear system for exponents. Checked determinant of coefficient matrix.
RESULT: a=4, b=5, d=-3. Determinant = -1 (nonzero). Solution is unique.
VERDICT: **VERIFIED**
NOTES: Uniqueness holds ONLY within {m, c, hbar}. Including G opens a one-parameter family (e.g., G*m^2*c^4/hbar^2). The coefficient K=1 is fixed by the construction, not by dimensional analysis. Any K*m^4*c^5/hbar^3 with dimensionless K has correct dimensions.

---

CLAIM: For a coherent state |alpha> with |alpha|^2 = 1/2, the energy is E = hbar*omega (one quantum).
TESTED BY: Park, Kovacs
METHOD: Park: algebraic proof from <alpha|H|alpha> = hbar*omega*(|alpha|^2 + 1/2). Kovacs: numerical verification.
RESULT: hbar*omega*(0.5 + 0.5) = hbar*omega. Exact.
VERDICT: **VERIFIED**
NOTES: Standard quantum mechanics textbook result. No subtlety.

---

CLAIM: |alpha|^2 = 1/2 is uniquely determined by the energy constraint E = hbar*omega at frequency omega = mc^2/hbar.
TESTED BY: Park
METHOD: Algebraic: set hbar*omega*(|alpha|^2 + 1/2) = hbar*omega, solve for |alpha|^2.
RESULT: |alpha|^2 = 1/2 follows from algebra alone. No optimization needed.
VERDICT: **VERIFIED** (as algebraic determination)
NOTES: The "variational uniqueness" claim is a narrower result: among minimum-uncertainty product states at fixed energy, the coherent state minimizes Var[T_00] over squeezed states. But the basic determination is algebraic, not variational.

---

CLAIM: The frequency identification omega = mc^2/hbar is derived from first principles.
TESTED BY: Park
METHOD: Checked whether omega = mc^2/hbar follows from any physical principle.
RESULT: It is the zero-momentum mode frequency of a massive scalar field. It's the simplest choice but NOT the unique choice.
VERDICT: **PARTIALLY CORRECT** -- it's a natural ansatz, not a derivation.
NOTES: Other choices exist (mean frequency, spectral average). The framework treats this as an input, not an output. Correctly labeled as "ansatz" in the knowledge base.

---

CLAIM: <0|Omega> = exp(-N/4) -> 0 as N -> infinity.
TESTED BY: Park, Nakamura
METHOD: Park: verified single-mode overlap <0|alpha> = exp(-|alpha|^2/2) and N-cell product formula. Nakamura: checked entanglement implications.
RESULT: Calculation correct in regularized setting. In continuum: states are unitarily inequivalent (stronger result).
VERDICT: **VERIFIED**
NOTES: Reeh-Schlieder concern resolved -- the spectrum condition fails for the cell vacuum, so the theorem doesn't apply. Same evasion mechanism as thermal states.

---

CLAIM: rho_cell / rho_mode = 16 pi^2 at the Compton cutoff (massless dispersion).
TESTED BY: Kovacs, Park
METHOD: Kovacs: independent numerical computation. Park: algebraic derivation.
RESULT: Ratio = 157.914 = 16 pi^2 to 6 significant figures. EXACT.
VERDICT: **VERIFIED**
NOTES: For massive fields at Compton cutoff, ratio is ~103 (correction factor ~1.54). The 16 pi^2 is a geometric phase-space factor, not a fundamental constant.

---

CLAIM: The d-dimensional ratio is C_d = 2(d+1)(2pi)^d / Omega_d.
TESTED BY: Park
METHOD: Verified for d=1,2,3.
RESULT: C_1 = 4pi, C_2 = 12pi, C_3 = 16pi^2. All correct.
VERDICT: **VERIFIED**
NOTES: New formula from AQFT investigation (Team 4). Demotes 16pi^2 from "fundamental constant" to "d=3 case of geometric formula."

---

CLAIM: The neutrino mass spectrum is m_1 = 2.31 meV, m_2 = 8.98 meV, m_3 = 49.58 meV, Sum = 60.87 meV (PDG 2023).
TESTED BY: Kovacs
METHOD: Independent calculation from scratch using PDG 2023 and NuFIT 6.0 oscillation parameters, multiple H_0 values.
RESULT: All numbers confirmed. Sum = 60.8 +/- 0.7 meV across parameter ranges.
VERDICT: **VERIFIED**
NOTES: The extraction of m_1 from rho_Lambda is CIRCULAR. The non-circular predictions are m_2, m_3, Sum (using independent oscillation data), normal ordering, and w = -1.

---

CLAIM: Self-duality: f(x) = x^2/2 is its own Fenchel conjugate; exp(-x^2/2) is a fixed point of the Fourier transform; coherent states have equal position and momentum energy contributions.
TESTED BY: Park
METHOD: Verified all three forms. Checked uniqueness among power functions and Schwartz functions.
RESULT: All three correct. Uniqueness proven.
VERDICT: **VERIFIED**
NOTES: These are standard mathematical results elevated to physical significance by the framework. The connection is real and proven.

---

CLAIM: The cell vacuum is a legitimate AQFT state.
TESTED BY: Park
METHOD: Reviewed the Weyl algebra construction from 05_final_synthesis.md.
RESULT: Positivity, normalization, Hadamard condition all satisfied. Rigor A for finite volume, Rigor B for infinite.
VERDICT: **VERIFIED**
NOTES: Falls into the same mathematical family as thermal states and broken-symmetry vacua. Well-established in AQFT.

---

CLAIM: The cell vacuum satisfies the Hadamard condition.
TESTED BY: Park
METHOD: Reviewed two-point function W_Omega(x,y) = W_0(x,y) + F(x)F(y).
RESULT: F is smooth (from Schwartz test functions in Weyl algebra). UV singularity structure unchanged. Hadamard condition preserved.
VERDICT: **VERIFIED**
NOTES: Allows renormalized T_mu_nu computation via standard Hadamard point-splitting.

---

CLAIM: Self-consistency on curved spacetime: correction delta_rho/rho ~ 3.6 x 10^{-69}.
TESTED BY: Santos (checked cosmological parameters), Park (checked the estimate)
METHOD: Computed R*lambda_C^2 for de Sitter spacetime sourced by the cell vacuum energy.
RESULT: Correction is extraordinarily small at all cosmological epochs. Flat-space calculation is a stable fixed point.
VERDICT: **VERIFIED**
NOTES: Valid for all post-nucleosynthesis cosmology. Breaks down only at temperatures far above electroweak scale.

---

CLAIM: Parker particle creation is negligible: adiabatic parameter ~ 6.2 x 10^{-31}.
TESTED BY: Park
METHOD: Reviewed the adiabatic parameter estimate H*lambda_C/c.
RESULT: ~ 10^{-31}. Bogoliubov coefficient ~ 10^{-62}. Completely negligible.
VERDICT: **VERIFIED**

---

CLAIM: Zero entanglement in the cell vacuum for any bipartition.
TESTED BY: Nakamura
METHOD: Traced over complement of any subset A; obtained pure reduced state.
RESULT: S_A = 0 exactly. Mutual information I(A:B) = 0 for all disjoint A, B.
VERDICT: **VERIFIED**
NOTES: Trivially true from product state. Corrections from physical cell overlaps are exp(-10^{31}), effectively zero.

---

## SECTION 2: PHYSICAL CLAIMS

---

CLAIM: The cosmological constant "problem" is a category error.
TESTED BY: Park, Brennan
METHOD: Park: analyzed mathematical precision of the claim. Brennan: tested against standard renormalization.
RESULT: The divergent zero-point energy IS related to using a momentum-space state for a position-space question. But the post-renormalization finite contributions (QCD, Higgs, electroweak) are not addressed.
VERDICT: **PARTIALLY CORRECT**
NOTES: The insight that the mode vacuum has no position structure is physically correct. Calling it a "category error" is overstated. The framework addresses the divergent piece but not the finite SM contributions.

---

CLAIM: The cell vacuum energy density matches the observed dark energy density.
TESTED BY: Kovacs, Santos, Brennan
METHOD: Independent computation and circularity analysis.
RESULT: The "match" rho_cell(m_1) ~ rho_Lambda is circular. m_1 was derived from rho_Lambda via the formula.
VERDICT: **REFUTED** (as a prediction). **VERIFIED** (as arithmetic -- the formula is self-consistent).
NOTES: The knowledge base correctly identifies and retires this claim. The "0.4% match" is meaningless.

---

CLAIM: Sum(m_nu) = 60.5-61.0 meV is a genuine non-circular prediction.
TESTED BY: Brennan, Santos
METHOD: Circularity analysis; experimental comparison.
RESULT: This IS non-circular (uses rho_Lambda as input + independent oscillation data). Currently in 1.5-2 sigma tension with DESI DR2 (< 53 meV at 95% CL).
VERDICT: **VERIFIED** as non-circular. **UNDER TENSION** experimentally.
NOTES: The prediction is dominated by oscillation data (m_3 ~ 50 meV from delta_m^2_31). The framework's specific contribution (m_1 = 2.3 meV) is relatively small. Any normal-ordering model with nonzero m_1 predicts similar Sum.

---

CLAIM: Normal mass ordering is required by the framework.
TESTED BY: Santos
METHOD: Checked NuFIT 6.0, experimental status.
RESULT: Normal ordering favored at ~2.5-3 sigma. JUNO will test at > 3 sigma by ~2027.
VERDICT: **CONSISTENT** (prediction matches current data; not yet definitive)

---

CLAIM: w = -1 exactly (cosmological constant equation of state).
TESTED BY: Park, Santos
METHOD: Park: checked derivation status. Santos: compared with current data.
RESULT: w = -1 is NOT DERIVED from the framework on curved spacetime. Classical part gives w = -2/3. Current data (w = -1.03 +/- 0.04) is consistent but DESI hints at w(z) evolution.
VERDICT: **INCONCLUSIVE** -- Prediction is stated but not derived. Data is currently consistent.

---

CLAIM: Only the lightest neutrino mass contributes to the cosmological constant.
TESTED BY: Brennan, Kovacs
METHOD: Computed rho_cell for all SM particles. Analyzed mass selection problem.
RESULT: No mechanism excludes heavier species. If all species contribute, total is dominated by top quark (10^{33} J/m^3), catastrophically wrong. Even neutrinos alone: m_3 contributes 2 x 10^5 times more than m_1.
VERDICT: **REFUTED** (as currently stated -- no justification provided)
NOTES: This is the framework's BIGGEST problem. Without a mass selection mechanism, the total vacuum energy is wrong by > 10^{35} orders of magnitude. This was flagged in the knowledge base as the "biggest conceptual gap" but the severity may be understated.

---

CLAIM: The cell vacuum resolves the black hole entropy problem.
TESTED BY: Nakamura
METHOD: Compared cell vacuum entanglement (zero) with Bekenstein-Hawking (A/4l_P^2).
RESULT: Irreconcilable as stated. Zero entanglement gives zero entanglement entropy across any surface, including horizons.
VERDICT: **REFUTED** (as a complete framework). The cell vacuum CREATES a new BH entropy problem rather than resolving the existing one.
NOTES: Possible resolutions (scale-dependent vacuum, non-entanglement entropy) are speculative and unformalized. This is existential for the framework.

---

CLAIM: Finite QCD and Higgs vacuum energy contributions are addressed by the framework.
TESTED BY: Santos, Brennan
METHOD: Reviewed framework documents for treatment of non-perturbative contributions.
RESULT: The framework has nothing to say about QCD condensate (~10^{-3} J/m^3), Higgs VEV (~10^8 J/m^3), or electroweak contributions. These are listed as "OPEN" problems with no proposed resolution.
VERDICT: **REFUTED** (the framework does not address these contributions)
NOTES: Even if the cell vacuum correctly treats zero-point energy, the cosmological constant problem in its full form requires explaining why QCD, Higgs, and electroweak vacuum energies don't gravitate at their natural scales.

---

## SECTION 3: DEMOTED CLAIMS (previously verified as failed)

---

CLAIM: Legendre-Fenchel duality formally relates the two vacua.
TESTED BY: (Previously by AQFT Team 4)
METHOD: Attempted to construct explicit duality.
RESULT: Cell vacuum energy is a number; Fenchel conjugate is a function. Category error in the conjecture itself.
VERDICT: **REFUTED** (previously; confirmed in this session)

---

CLAIM: 16 pi^2 is a fundamental constant analogous to 1/2 in the uncertainty principle.
TESTED BY: (Previously by AQFT Team 4)
METHOD: Computed C_d in arbitrary dimension.
RESULT: C_d depends on d, dispersion relation, and cutoff convention. Not universal.
VERDICT: **REFUTED** (previously; confirmed in this session). Geometric factor, not fundamental constant.

---

CLAIM: 10^{123} is a duality gap in convex optimization.
TESTED BY: (Previously by AQFT Team 4)
METHOD: Attempted to construct primal-dual optimization structure.
RESULT: No formal structure exists. Ratio depends on arbitrary Planck cutoff.
VERDICT: **REFUTED** (previously; confirmed in this session)

---

CLAIM: De Sitter entropy from Compton cell counting gives 10^{122}.
TESTED BY: (Previously verified)
METHOD: Computed (R_H/lambda_C)^2.
RESULT: Gives 10^{60}, not 10^{122}. Gap of 10^{62}.
VERDICT: **REFUTED** (previously; confirmed in this session)

---

CLAIM: Poisson entropy at lambda = 1/2 is 0.72 nats.
TESTED BY: (Previously corrected)
METHOD: Exact Poisson entropy calculation.
RESULT: 0.826 nats = 1.19 bits (not 0.72 nats).
VERDICT: **REFUTED** (original value; corrected value VERIFIED)

---

## SECTION 4: CODE VERIFICATION

---

CLAIM: constants.py correctly implements physical constants and the cell vacuum formula.
TESTED BY: Kovacs
METHOD: Independent implementation from scratch; compared outputs.
RESULT: All constants correct (CODATA 2018, exact post-2019 SI). Cell vacuum formula matches to machine precision.
VERDICT: **VERIFIED**
NOTES: OBSERVED_DARK_ENERGY_DENSITY = 5.96e-10 corresponds to H_0 ~ 72 km/s/Mpc. Should note this is one value in a range.

---

CLAIM: coherent_states.py correctly implements coherent state physics.
TESTED BY: Kovacs
METHOD: Verified uncertainty product, energy, wavefunction against analytical formulas.
RESULT: All properties correct. Uncertainty product = hbar/2 to machine precision.
VERDICT: **VERIFIED**

---

CLAIM: vacuum_energy.py correctly computes mode and cell vacuum energy densities.
TESTED BY: Kovacs
METHOD: Independent calculation; compared all outputs.
RESULT: All computations correct. 16 pi^2 ratio exact to 6 significant figures.
VERDICT: **VERIFIED**
NOTES: The demonstrate_category_error() function presents the framework uncritically without flagging the circularity of the rho match. demo.py has the same issue. The verified findings documents are more honest than the code.

---

## SUMMARY STATISTICS

| Category | Verified | Partially Correct | Refuted | Inconclusive |
|----------|----------|-------------------|---------|--------------|
| Core Mathematics | 14 | 1 | 0 | 0 |
| Physical Claims | 2 | 1 | 3 | 1 |
| Previously Demoted | 0 | 0 | 5 | 0 |
| Code | 3 | 0 | 0 | 0 |
| **Total** | **19** | **2** | **8** | **1** |

**Bottom line**: The mathematics is solid. The physics has significant unresolved problems. The code is correct but uncritical.
