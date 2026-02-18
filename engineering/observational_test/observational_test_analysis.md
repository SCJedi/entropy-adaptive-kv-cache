# Observational Test Analysis: LCDM vs Two Vacua Framework

## Summary

The Two Vacua framework proposes replacing the standard LCDM components with:
- **Cell vacuum** (w = 0) in place of cold dark matter (CDM)
- **Wald ambiguity** (w = -1) in place of the cosmological constant (Lambda)
- **Graviton vacuum** (w = +1/3) as additional dark radiation

This analysis computes observational consequences and compares to data. The results are mixed: the cell vacuum is a viable CDM replacement at all observable scales, but the graviton vacuum prediction is **catastrophically ruled out** by existing data.

## 1. Does the Two Vacua Model Reproduce LCDM at Background Level?

### Without the graviton vacuum: YES, exactly.

When Omega_cell = Omega_CDM and Omega_Wald = Omega_Lambda, and the graviton vacuum is set to zero, the Two Vacua expansion history is **mathematically identical** to LCDM. This is verified numerically to machine precision (relative error < 10^-10 at all redshifts).

The reason is simple: both the cell vacuum and CDM have w = 0, so both dilute as a^-3. Both the Wald ambiguity and Lambda have w = -1, so both are constant. The Friedmann equation is identical.

### With the graviton vacuum: NO, drastically different.

The graviton vacuum with rho_grav = rho_cell / (8 pi^2) gives:

| Parameter | Value |
|---|---|
| Omega_grav | 0.0033 |
| Omega_rad (standard) | 9.2 x 10^-5 |
| Ratio Omega_grav/Omega_rad | 36 |
| Delta N_eff | **267** |
| Planck bound (95% CL) | Delta N_eff < 0.3 |

**The graviton vacuum prediction exceeds the Planck N_eff bound by a factor of ~900.** This is not a marginal tension -- it is a catastrophic failure. The graviton vacuum at the predicted level would:

- Triple H(z) at z ~ 1100 (CMB epoch)
- Completely change the CMB power spectrum
- Alter Big Bang nucleosynthesis (ruled out by primordial helium abundance)
- Modify the matter-radiation equality epoch (observed via CMB peak structure)

**Evidence tier: OBSERVATIONALLY EXCLUDED with very high confidence (> 10 sigma).**

## 2. Perturbation-Level Differences: Cell Vacuum vs CDM

### Sound speed and clustering

| Property | Standard CDM | Cell Vacuum |
|---|---|---|
| Equation of state w | 0 | 0 |
| Classical sound speed c_s | 0 | 0 (product state) |
| Quantum Jeans length | N/A (particle) | ~5 x 10^11 m = 1.5 x 10^-8 kpc |
| Clusters at galaxy scales? | Yes | Yes |
| Clusters at sub-mm scales? | Yes | Suppressed below Compton wavelength (~0.085 mm) |

The cell vacuum is a product state of independent coherent oscillators. Because there are no inter-cell correlations (product state), perturbations do not propagate between cells, giving an effective classical sound speed of zero -- identical to CDM.

Quantum pressure introduces a Jeans length of order ~5 x 10^11 meters (~3000 AU). This is far below any astrophysical scale where structure formation is observed. The cell vacuum clusters identically to CDM at all observable scales.

**Evidence tier: Cell vacuum and CDM are observationally indistinguishable in structure formation at currently accessible scales.** The sub-mm scale difference is many orders of magnitude below any foreseeable probe.

### Velocity dispersion and halo profiles

Standard CDM predicts cuspy halo profiles (NFW profile). The cell vacuum, being a coherent oscillation, might produce slightly different halo profiles at the core scale. However, the core scale is set by the Compton wavelength (~0.085 mm), which is vastly below the resolution of any astronomical observation. The classical (> mm scale) behavior is identical to CDM.

## 3. Is the Dark Radiation Prediction Testable?

Yes, it is testable, and it is **already tested and ruled out**.

The prediction rho_grav = rho_cell/(8 pi^2), with Omega_cell ~ 0.27, gives Omega_grav ~ 0.003. This is 36 times larger than the total standard radiation density. Planck constrains N_eff = 2.99 +/- 0.17, meaning at most Delta N_eff ~ 0.3 of extra radiation is allowed.

**The graviton vacuum would need to be suppressed by a factor of ~900 to be compatible with Planck.** This means either:

1. The graviton vacuum does not exist as a cosmological component
2. The relationship rho_grav/rho_cell = 1/(8 pi^2) does not hold cosmologically
3. The graviton vacuum has a different equation of state than w = +1/3
4. Some mechanism suppresses it relative to the naive prediction

## 4. What Observations Could Distinguish Cell Vacuum from Particle CDM?

### Currently: nothing at background or linear perturbation level.

Both have w = 0, both cluster identically above ~0.1 mm scales.

### In principle:

1. **Sub-millimeter gravity experiments**: The cell vacuum has a Compton wavelength of ~0.085 mm. Below this scale, the vacuum structure differs from particle CDM. Current tests of gravity reach ~50 micrometers, approaching but not yet probing the relevant scale.

2. **Dark matter direct detection**: CDM particles interact (weakly) with normal matter. The cell vacuum, being a coherent oscillation of the quantum field vacuum, has no particle-like interactions beyond gravity. If CDM is ever detected in a direct detection experiment, the cell vacuum interpretation would be ruled out.

3. **Neutrino mass measurement**: The framework predicts rho_cell = m^4 c^5/hbar^3 with m = lightest neutrino mass. The formula gives rho_cell ~ 5.94 x 10^-10 J/m^3. However, this matches the dark ENERGY density (~5.3 x 10^-10 J/m^3), not the dark MATTER density (~2.0 x 10^-10 J/m^3). The ratio is:
   - rho_cell / rho_DE ~ 1.12 (close match)
   - rho_cell / rho_DM ~ 2.97 (factor of 3 mismatch)

   This is a problem: the formula was originally developed to match dark energy density, but the EOS analysis showed w = 0, not w = -1. The cell vacuum density matches the wrong cosmological component.

4. **The total dark sector density**: rho_cell + rho_Wald should equal rho_DM + rho_Lambda. If rho_cell ~ 5.94e-10 (from the formula), then rho_Wald ~ rho_total - rho_cell - rho_baryons. This gives a specific prediction for the Wald ambiguity.

## 5. If Omega_Wald = Omega_Lambda, is the Wald Ambiguity Just Relabeling?

### Mostly yes, with some nuance.

The Wald ambiguity in curved spacetime QFT is mathematically identical to the cosmological constant. Both appear as Lambda * g_uv in the stress-energy tensor. Both have w = -1. Both are constant in time. The Wald ambiguity IS the cosmological constant, viewed through the lens of renormalization theory.

**What the relabeling accomplishes:**
- It identifies the physical origin of Lambda: it is the renormalization ambiguity in defining the stress-energy tensor on curved spacetime, not a dynamical quantity.
- It explains why Lambda is constant (it's a boundary condition, not a field configuration).
- It explains why we cannot compute Lambda from first principles (it's a renormalization parameter).

**What it does NOT accomplish:**
- It does not predict the VALUE of Lambda.
- It does not explain the coincidence problem (why Omega_Lambda ~ Omega_m today).
- It does not solve the fine-tuning problem (why Lambda is so small compared to Planck density).

**Evidence tier: Theoretical reinterpretation, not new physics.** The Wald ambiguity provides a cleaner conceptual framework for the cosmological constant but makes no new testable predictions about dark energy.

## 6. What SPECIFIC Predictions Differ Between Two Vacua and LCDM?

### Prediction 1: Cell vacuum replaces CDM (w = 0)
- **Test**: Structure formation at all scales
- **Status**: Consistent with observations (indistinguishable from CDM)
- **Evidence tier**: UNTESTABLE at current precision. No falsifiable difference.

### Prediction 2: rho_cell = m^4 c^5 / hbar^3 relates DM density to neutrino mass
- **Test**: Measure lightest neutrino mass
- **Problem**: The formula gives rho ~ 5.94e-10 J/m^3, which is ~3x the observed DM density. For this to work as a CDM replacement, m would need to be ~1.7 meV (not 2.31 meV) to match Omega_CDM * rho_crit.
- **Status**: Factor of 3 discrepancy with the intended CDM role; close match to rho_DE instead.
- **Evidence tier**: TENSION. The formula value doesn't naturally match the component it's supposed to replace.

### Prediction 3: rho_grav / rho_cell = 1/(8 pi^2) (dark radiation)
- **Test**: CMB N_eff measurement
- **Status**: **RULED OUT by factor ~900.** Delta N_eff ~ 267 vs Planck bound of 0.3.
- **Evidence tier**: FALSIFIED with > 10 sigma significance.

### Prediction 4: Wald ambiguity = cosmological constant (w = -1)
- **Test**: None (this is a relabeling)
- **Status**: Consistent by construction
- **Evidence tier**: Tautological; adds no testable content.

## 7. Honest Assessment: Does This Add Genuine Physical Content?

### What genuinely works:
1. The cell vacuum is a valid quantum state with w = 0 (rigorously established).
2. It clusters like CDM at all observable scales (verified computationally).
3. The identification of the mode vacuum vs cell vacuum as a category error is pedagogically valuable and mathematically correct.
4. The Wald ambiguity provides a cleaner understanding of the cosmological constant's origin.

### What does not work:
1. **The graviton vacuum prediction is falsified.** rho_grav/rho_cell = 1/(8 pi^2) with Omega_cell ~ 0.27 gives Delta N_eff ~ 267, ruled out by a factor of 900.
2. **The density formula doesn't match CDM.** rho_cell = m^4 c^5/hbar^3 ~ 5.94e-10 J/m^3 is 3x the CDM density. It actually matches the dark energy density better, but the state has w = 0, not w = -1.
3. **No falsifiable prediction distinguishes the cell vacuum from standard CDM.** At all observable scales, the cell vacuum and CDM are identical.
4. **The cosmological constant is not explained**, only relabeled as the Wald ambiguity.

### Overall verdict:

The Two Vacua framework, at the level of cosmological observations, reduces to LCDM with:
- A conceptual reinterpretation of CDM (coherent field oscillation instead of particles)
- A conceptual reinterpretation of Lambda (Wald ambiguity instead of vacuum energy)
- One falsified prediction (graviton vacuum dark radiation)
- One tension (density formula matches rho_DE, not rho_DM)

The framework adds genuine insight at the **conceptual level** (the category error between mode vacuum and cell vacuum is a real observation about QFT). It does NOT add falsifiable predictions that distinguish it from LCDM, except for the graviton vacuum contribution, which is ruled out.

The value of the framework is primarily **interpretive** -- providing a physical mechanism (coherent oscillations) for what CDM is made of, and identifying the cosmological constant as a renormalization ambiguity. But neither of these interpretive shifts produces observable consequences that differ from LCDM.

## Numerical Summary

| Quantity | LCDM | Two Vacua | Difference |
|---|---|---|---|
| H(z=0)/H0 | 1.000 | 1.000 | < 0.5% |
| H(z=1)/H0 | 1.732 | ~1.745 | ~0.8% |
| H(z=1100)/H0 | ~33150 | ~104000 | ~3x (ruled out) |
| d_L(z=1) | standard | ~identical | < 1% |
| w_eff (dark energy only, z=0) | -1.000 | -0.994 | 0.6% |
| Best-fit single w | -1.000 | -0.964 | 3.6% |
| D(z=1)/D(z=0) | 0.608 | ~0.608 | < 1% |
| Delta N_eff | 0 | 267 | **RULED OUT** |
| Jeans length | 0 (particle) | 1.5e-8 kpc | Unobservable |

---

*Analysis produced by computational verification. All claims supported by numerical calculation in `observational_constraints.py` with test coverage in `test_observational_constraints.py`. 57/57 tests passing.*
