# Temporal Coherence Cost: Dark Energy as the Price of Stationarity

**Date**: 2026-02-04
**Status**: Investigation Complete
**Parent Investigation**: Two Vacua Framework

---

## 1. The Hypothesis

Dark energy's defining feature is that its energy density is constant in time. The equation of state w = -1 is the ONLY value giving rho = const in an expanding universe (since rho proportional to a^{-3(1+w)}).

The cell vacuum oscillates at the Compton frequency (w = 0). The mode vacuum is stationary (w = -1). The hypothesis: **dark energy is the energy cost of temporal stationarity** -- the price a quantum field pays to NOT oscillate.

## 2. Formulation-by-Formulation Assessment

### 2.1 Per-Mode Stationarity Cost

**Formulation**: For a single QHO mode at frequency omega, the minimum energy for a stationary (time-independent) state is E_0 = hbar omega / 2 (the zero-point energy).

**Result**: w = 0 for both ground state and coherent state (virial theorem). The per-mode stationarity cost does NOT change the equation of state.

**Evidence Tier**: [PROVEN] -- The virial theorem is exact for the quantum harmonic oscillator.

**Verdict**: Per-mode stationarity cost is real but irrelevant to dark energy. It does not produce w = -1.

### 2.2 Full-Field Mode Sum with UV Cutoff

**Formulation**: Sum zero-point energies over all modes up to a cutoff Lambda:

    rho_mode(Lambda) = (hbar / (4 pi^2)) * integral_0^Lambda dk k^2 omega_k

With Compton cutoff (Lambda = mc/hbar): rho ~ m^4 c^5 / (16 pi^2 hbar^3), which is 1/(16 pi^2) times the cell vacuum density.

With Planck cutoff: rho ~ 10^{113} J/m^3 (the "worst prediction in physics").

**Result**: The mode sum is UV-divergent. Any finite cutoff gives a cutoff-dependent answer. Lorentz invariance forces T_uv proportional to g_uv (hence w = -1) for the sum, but the MAGNITUDE is not determined.

**Evidence Tier**: [FRAMEWORK] -- The Lorentz invariance argument for w = -1 is rigorous. The magnitude is undetermined.

**Verdict**: This formulation correctly identifies WHY the mode vacuum has w = -1 (Lorentz invariance of the mode sum), but fails to predict the magnitude. It reduces to the cosmological constant problem.

### 2.3 Renormalized Coherence Cost (Mode - Cell)

**Formulation**: Delta_rho = rho_mode - rho_cell. With Compton cutoff, this is negative (cell > mode by a factor of 16 pi^2).

**Result**: The raw difference is cutoff-dependent and negative at the Compton scale. In Wald's renormalization framework, the vacuum stress-energy has an undetermined ambiguity proportional to g_uv. The "coherence cost" is absorbed into this ambiguity.

**Evidence Tier**: [FRAMEWORK] -- Wald's result (1994) is mathematically rigorous.

**Verdict**: **This IS the cosmological constant problem restated in different language.** The coherence cost is the renormalization ambiguity. It is a free parameter, not a prediction.

### 2.4 Holographic Dark Energy

**Formulation** (Li 2004): rho_DE = 3c^2 / (8 pi G L^2) where L is an IR length scale.

With L = c/H0 (Hubble radius):
    rho_holo = 3 H0^2 c^2 / (8 pi G) = rho_crit ~ 7.8 x 10^{-10} J/m^3

**Result**: This gives the RIGHT order of magnitude. Ratio to observed: ~1.3 (since rho_DE ~ 0.7 rho_crit).

**BUT**: This is a TAUTOLOGY. The formula rho = 3H0^2 c^2 / (8 pi G) IS the Friedmann equation for a flat universe. It says "the dark energy density is of order the critical density," which is just the observational statement that Omega_DE ~ 0.7. No new physics.

With L = future event horizon (Li 2004): this does give a dynamical model with w ~ -1 that can differ from a cosmological constant, but the model has a free parameter (the coefficient "c" in rho = 3c^2 M_P^2 / L^2) that must be fit to data.

**Evidence Tier**: [FRAMEWORK] for the mathematical structure; [CONJECTURED] for the physical interpretation.

**Verdict**: The holographic approach reproduces the right scale but contains a circular element (Friedmann equation) and a free parameter (the coefficient). It does not EXPLAIN the value of rho_DE.

### 2.5 Margolus-Levitin Coherence Bound

**Formulation**: Minimum energy for temporal coherence over timescale tau:
    E_min = pi hbar / (2 tau)

Minimum density for Hubble-time coherence:
    rho_ML = pi hbar H0^4 / (2 c^3) ~ 10^{-130} J/m^3

**Result**: Too small by ~120 orders of magnitude.

**Evidence Tier**: [PROVEN] as a quantum information bound; [FAILS] as an explanation of dark energy.

**Verdict**: The Margolus-Levitin bound is a genuine lower limit on coherence energy, but it is catastrophically far from the observed dark energy density. The "temporal coherence" interpretation at this level is correct physics but irrelevant to dark energy.

### 2.6 Vacuum Persistence Amplitude

**Formulation**: Phase coherence requires E_min ~ hbar H0 per mode. The minimum density is rho ~ hbar H0^4 / c^3, same scale as Margolus-Levitin.

**Result**: Too small by ~120 orders of magnitude.

**Evidence Tier**: [FAILS] as dark energy explanation.

**Verdict**: Same as Margolus-Levitin. The phase argument gives the right dimensional structure but is 10^{120} times too weak.

### 2.7 Information Excess (Volumetric - Holographic) x Energy per Bit

**Formulation**:
- I_vol = V / lambda_C^3 (number of Compton cells in Hubble volume)
- I_bdy = A / (4 l_P^2) (holographic bound on Hubble surface)
- Delta_I = I_vol - I_bdy (information excess)
- rho_excess = Delta_I * E_bit / V where E_bit = hbar H0

**Crucial correction**: For the neutrino mass (lambda_C ~ 85 um), the Compton wavelength is macroscopic. As a result, I_vol << I_bdy for a Hubble-sized region. The holographic bound is NOT saturated -- there is an information DEFICIT, not excess.

Numerically: I_vol ~ 10^91, I_bdy ~ 10^122. The ratio I_vol / I_bdy ~ 10^{-31}.

The "information deficit" D = I_bdy - I_vol ~ I_bdy ~ A_H / (4 l_P^2).

If one uses D instead (energy cost of the unused holographic capacity):
    rho_deficit = D * hbar H0 / V ~ (R^2/l_P^2) * hbar H0 / R^3
               = hbar H0 / (l_P^2 R) for the Hubble region
               ~ hbar H0 / (l_P^2 * c/H0) = hbar H0^2 / (c l_P^2)

This contains the combination H0^2 / l_P^2 = H0^2 c^3 / (hbar G),
giving rho ~ H0^2 c^2 / G, which is the critical density again (Friedmann equation).

**Evidence Tier**: [CONJECTURED] -- the information deficit idea has no rigorous derivation and reduces to the Friedmann equation when worked through.

**Verified numerically**: With de Sitter temperature for E_bit, the deficit energy density equals rho_crit = 7.744e-10 J/m^3 exactly. With ML energy, it's 8x larger. Both are Friedmann in disguise.

**Verdict**: The original hypothesis assumed I_vol >> I_bdy, which is wrong for meV-mass particles. With the correct ordering, the deficit approach recovers rho_crit but this is again the Friedmann equation in disguise.

### 2.8 Scale Analysis

**Question**: What temporal scale tau gives the observed rho_DE?

**Answer**: Inverting rho = hbar omega^4 / c^3 gives omega ~ mc^2/hbar with m ~ 2.31 meV. This is the cell vacuum formula inverted -- it's circular. It says "if you define rho_DE as a coherence cost at some frequency, that frequency is the Compton frequency of a 2.31 meV particle."

The holographic inversion gives L ~ Hubble radius, which is the Friedmann equation.

**Evidence Tier**: [FRAMEWORK] for the mathematics; circular as an explanation.

**Verdict**: The scale analysis does not add new content. It rephrases known relationships.

---

## 3. Key Questions Answered

### Q1: Is there a formulation of "temporal coherence cost" that naturally gives rho_DE ~ H0^2 M_P^2?

**Answer**: Only the holographic formulation, which is the Friedmann equation rewritten. This is a tautology, not a prediction.

The combination H0^2 M_P^2 = H0^2 hbar c / G mixes the Hubble scale (IR) with the Planck scale (UV). No "coherence cost" argument naturally produces this combination from first principles. The Margolus-Levitin and phase arguments give hbar H0^4 / c^3, which is off by a factor of (M_P c / hbar H0)^2 ~ 10^{120}. This missing factor IS the cosmological constant problem.

### Q2: Does the holographic bound (information excess x energy per bit) reproduce observed dark energy?

**Answer**: No. The original hypothesis assumed volumetric information exceeds holographic, but for neutrino-mass particles (lambda_C ~ 85 um), I_bdy >> I_vol by a factor of ~10^31. The holographic bound is not saturated. Using the information deficit instead recovers rho ~ rho_crit, which is the Friedmann equation, not a prediction.

### Q3: Is there a temporal cell size tau* such that the coherence cost gives the right rho? What determines tau*?

**Answer**: Yes: tau* = hbar / (mc^2) where m = (rho_DE hbar^3 / c^5)^{1/4} ~ 2.31 meV. But this is the cell vacuum formula inverted. It says "the right tau is the Compton time of a 2.31 meV particle." Nothing in the coherence cost framework DETERMINES this tau without knowing rho_DE in advance.

### Q4: Does any version of this idea predict w = -1 rather than just postulating it?

**Answer**: Yes, partially. The Lorentz invariance argument is genuine: the stress-energy of the mode vacuum MUST be proportional to g_uv, which forces w = -1. This is [FRAMEWORK]-level physics. However, it does not predict the MAGNITUDE. The per-mode cost gives w = 0 (virial theorem). The field-level sum gives w = -1 (Lorentz invariance) but with undetermined magnitude.

### Q5: Is "dark energy as coherence cost" a new idea or a restatement of the cosmological constant problem?

**Answer**: **Primarily a restatement.** The renormalized coherence cost (Section 2.3) is explicitly the Wald renormalization ambiguity in different language. The holographic version (Section 2.4) is the Friedmann equation in different language. The Margolus-Levitin and phase versions (Sections 2.5-2.6) fail quantitatively.

There is one potentially new element: the information excess approach (Section 2.7) gives a formula rho ~ m^3 c^3 H0 / hbar^2 that mixes the particle physics scale m with the cosmological scale H0 in a specific way. However, this formula does not match observations, and the framework has no rigorous justification.

---

## 4. What IS Genuinely Interesting

Despite the overall negative assessment, several elements are worth noting:

### 4.1 The w = -1 from Lorentz Invariance is Real Physics
[FRAMEWORK] -- The mode vacuum MUST have w = -1 because Lorentz invariance constrains T_uv proportional to g_uv. This is not a postulate but a theorem. The cell vacuum escapes this because it breaks Lorentz invariance (preferred frame from the oscillation). This structural difference between the two vacua is genuine and illuminating.

### 4.2 The Cell Vacuum as Physical Vacuum Changes the Framing
[FRAMEWORK] -- If the cell vacuum (w = 0) is the physical vacuum, then dark energy is NOT the vacuum energy. It must come from something else -- perhaps a genuine cosmological constant (a parameter of the theory) rather than a quantum effect. This is actually a simplification: it separates the vacuum energy problem from the cosmological constant problem.

### 4.3 The Coincidence rho_DE ~ rho_cell Remains Unexplained
[CONJECTURED] -- The fact that rho_DE ~ m_nu^4 c^5 / hbar^3 for m_nu ~ 2.31 meV (a plausible lightest neutrino mass) remains a remarkable numerical coincidence. None of the coherence cost formulations explain WHY this should be so. The cell vacuum formula gives the right magnitude with w = 0, not w = -1. The cosmological constant gives w = -1 but with undetermined magnitude. The coincidence between these two independent quantities is the deepest puzzle.

---

## 5. Evidence Tier Summary

| Formulation | Tier | Status |
|---|---|---|
| Per-mode stationarity cost (w=0) | [PROVEN] | Correct but irrelevant to DE |
| Lorentz invariance forces w=-1 for mode vacuum | [FRAMEWORK] | Correct, explains w but not rho |
| Renormalized coherence cost = Wald ambiguity | [FRAMEWORK] | Restates CC problem |
| Holographic DE (Hubble radius) | [FRAMEWORK] | Tautology (= Friedmann eq.) |
| Holographic DE (future horizon) | [CONJECTURED] | Has free parameter |
| Margolus-Levitin coherence bound | [FAILS] | 10^120 too small |
| Vacuum persistence phase | [FAILS] | 10^120 too small |
| Information deficit x E_bit | [CONJECTURED] | Wrong premise (I_bdy >> I_vol); deficit -> Friedmann |
| Scale analysis (invert cell formula) | [FRAMEWORK] | Circular |

---

## 6. Honest Bottom Line

**The "temporal coherence cost" interpretation of dark energy does not add new physics.** It provides an alternative vocabulary for describing known results:

1. The mode vacuum has w = -1 because of Lorentz invariance (known since at least Zel'dovich 1968).
2. The vacuum energy magnitude is undetermined after renormalization (Wald 1994).
3. The holographic bound gives the right scale because it encodes the Friedmann equation.

**What it does illuminate**: The contrast between cell vacuum (oscillating, w = 0) and mode vacuum (stationary, w = -1) is a clean way to see that the equation of state depends on the symmetry structure of the state, not just the energy. The cell vacuum breaks time-translation symmetry (via oscillation), which removes the Lorentz-invariance constraint that forces w = -1.

**The real question remains**: Why is rho_DE ~ (2 meV)^4 in natural units? The coherence cost framing does not answer this. The cell vacuum formula produces this scale for m ~ 2.31 meV, but with w = 0 instead of w = -1. Whether this numerical coincidence has deep significance or is accidental is the open question that none of these formulations resolve.

---

## 7. Artifacts

- `temporal_coherence.py`: Python module with all computations
- `test_temporal_coherence.py`: Comprehensive test suite
- `temporal_coherence_analysis.md`: This document
