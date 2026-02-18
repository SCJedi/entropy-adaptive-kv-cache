# Degrees of Freedom and Equipartition: Can Statistical Mechanics Explain 5/2?

## The Observation

From Planck 2018:
- Omega_Lambda / Omega_DM = 2.58 +/- 0.08
- The ratio 5/2 = 2.500 lies within 1 sigma

**Question**: Does the 5/2 ratio have a thermodynamic origin?

---

## 1. Classical Equipartition Theorem

### 1.1 The Standard Result

Each quadratic DOF contributes (1/2)kT to thermal energy:
```
E = (f/2) kT
```

| System | DOF | Energy |
|--------|-----|--------|
| Monatomic gas (3D translation) | 3 | (3/2)kT |
| Diatomic gas (trans + rotation) | 5 | (5/2)kT |
| Diatomic at high T (+ vibration) | 7 | (7/2)kT |

The 5/2 appears in diatomic specific heat: C_v = (5/2)R

### 1.2 Why Not Vacuum Energy?

Equipartition requires:
1. Thermal equilibrium at T > 0
2. Quadratic DOF in the Hamiltonian
3. Ergodic dynamics

The cell vacuum has:
- Zero temperature (ground state)
- Zero entropy (pure product state)
- No thermal fluctuations

**Conclusion**: Classical equipartition does not apply to the cell vacuum.

---

## 2. Quantum Corrections

### 2.1 Zero-Point Energy

The quantum oscillator has E = hbar*omega*(n + 1/2). At T = 0:
- Classical equipartition: E = 0
- Quantum reality: E = (1/2)hbar*omega

Zero-point energy is NOT subject to equipartition.

### 2.2 Mode Counting Instead of Thermal DOF

At T = 0, DOF counting becomes mode counting:
- Mode vacuum: infinite modes -> infinity
- Cell vacuum: one mode per Compton cell -> finite

**Key insight**: Ground state physics is about mode structure, not thermal distribution.

---

## 3. de Sitter Temperature

### 3.1 The Gibbons-Hawking Temperature

de Sitter space has horizon temperature:
```
T_dS = hbar*c*sqrt(Lambda/3) / (2*pi*k_B)
```

For Lambda = 1.1 x 10^-52 m^-2:
```
T_dS = 2.2 x 10^-30 K
```

Extraordinarily cold - far below any measurable temperature.

### 3.2 Equipartition at T_dS?

If equipartition applied at T_dS:
```
E_DOF = (1/2)*k_B*T_dS = 1.5 x 10^-53 J
```

To match rho_Lambda = 5.2 x 10^-10 J/m^3:
```
V_cell = E_DOF / rho_Lambda = 2.9 x 10^-44 m^3
Length scale: l = 3 x 10^-15 m (femtometer!)
```

This is nuclear scale, not Compton scale (~0.1 mm). **Wrong by 11 orders of magnitude.**

**Conclusion**: de Sitter equipartition gives the wrong scale.

---

## 4. Vacuum as Zero-Entropy System

### 4.1 Cell Vacuum Properties

- |Omega> = product state over cells
- Entropy: S = 0 (pure state)
- Temperature: undefined

### 4.2 Equipartition Requires Entropy

Equipartition follows from the canonical ensemble:
```
<E_i> = integral E_i * exp(-beta*H) dGamma / Z
```

For S = 0: No microcanonical distribution exists. No averaging over microstates.

**Conclusion**: Equipartition is inapplicable to pure states.

---

## 5. Partition Function Approach

### 5.1 At T -> 0

The partition function is dominated by the ground state:
```
Z -> exp(-beta*E_0)
```

### 5.2 Ratio of Partition Functions?

Could rho_Lambda / rho_cell = Z_Lambda / Z_cell?

Both depend on the same beta. The energy difference matters, not the ratio.

No natural way to get 5/2 from partition function structure.

---

## 6. DOF Counting in Field Theory

### 6.1 Mode Vacuum

A free scalar field: one complex amplitude per mode k.
Total: infinity (continuous spectrum).

### 6.2 Cell Vacuum

One mode per Compton cell:
- Each cell: 2 real DOF (field quadratures x, p)
- Or: 1 coherent state parameter (|alpha|^2 = 1/2)

### 6.3 Could 5/2 Come from DOF Structure?

Hypothesis: Lambda involves 5 DOF, cell vacuum involves 2.

**But what "rotates" in vacuum?** The diatomic analogy (3 trans + 2 rot) has no vacuum counterpart.

---

## 7. Species Counting Factor

### 7.1 Three Neutrino Species

If Lambda sums over species while cell vacuum selects lightest:
```
rho_Lambda = Sum_i m_i^4 c^5 / hbar^3
rho_cell = m_min^4 c^5 / hbar^3
```

For hierarchical masses: ratio >> 3 (dominated by heaviest).

### 7.2 If Masses Are Comparable

If all three neutrinos contribute equally:
```
Ratio ~ 3
```

Close to 2.5, but not exact.

### 7.3 N_eff from CMB

N_eff = 3.044 (standard cosmology).
```
N_eff - 0.5 = 2.54 (close to 2.58!)
```

But the "-0.5" has no obvious origin.

---

## 8. The Coincidence Problem

### 8.1 Time Evolution

The ratio Omega_Lambda / Omega_DM changes:
- Past: ratio << 1 (matter dominated)
- Today: ratio ~ 2.5
- Future: ratio >> 1 (Lambda dominated)

### 8.2 If 5/2 is Fundamental

If rho_Lambda / rho_cell = 5/2 at formation, but rho_cell dilutes as a^-3:
```
Omega_Lambda / Omega_DM = 5/2 * a^3
```

For this to equal 2.5 today (a = 1): formation was at a = 1 (now).

This suggests 5/2 is NOT the fundamental ratio, but reflects cosmic evolution.

### 8.3 Matter-Lambda Equality

If formation was earlier:
```
2.5 = (a_now / a_form)^3
a_form = 0.74, z_form = 0.35
```

Equality occurred ~4 billion years ago. The 2.5 reflects this timing.

---

## 9. Rigorous Assessment

### 9.1 What Fails

| Approach | Why It Fails |
|----------|--------------|
| Classical equipartition | Requires T > 0, thermal equilibrium |
| Quantum equipartition at T_dS | Wrong length scale by 10^11 |
| Partition function ratios | No mechanism for 5/2 |
| Field theory DOF counting | No clean 5 vs 2 structure |
| Information/entropy ratios | S_cell = 0, ratios undefined |

### 9.2 What Partially Works

| Approach | Result | Gap |
|----------|--------|-----|
| Species counting | N ~ 3 | Why 2.5, not 3? |
| N_eff - 0.5 | 2.54 | Why -0.5? |
| Cosmic evolution | z_eq ~ 0.35 | Why this epoch? |

---

## 10. Conclusions

### 10.1 Negative Result

There is **no statistical mechanics framework** where:
- Lambda emerges from 5 thermodynamic DOF
- Cell vacuum emerges from 2 thermodynamic DOF
- The ratio is naturally 5/2

The similarity to diatomic gas specific heat appears **coincidental**.

### 10.2 Most Likely Interpretation

The ratio Omega_Lambda / Omega_DM ~ 2.5 probably reflects:
1. Both densities set by same scale (m_nu)
2. A species counting factor N ~ 3
3. Cosmic evolution giving exact value at z = 0

### 10.3 Open Questions

1. Why is N ~ 2.5 instead of exactly 3?
2. Is the N_eff - 0.5 = 2.54 connection meaningful?
3. What mechanism connects neutrino number to Lambda?

---

## Evidence Tiers

| Claim | Tier |
|-------|------|
| Classical equipartition requires T > 0 | PROVEN |
| Cell vacuum has S = 0, T undefined | PROVEN |
| de Sitter equipartition gives wrong scale | PROVEN |
| Ratio 5/2 within 1-sigma of observations | PROVEN |
| Species counting gives N ~ 3 | ESTABLISHED |
| 5/2 from thermodynamic DOF | FAILS |
| Connection to diatomic 5/2 heat capacity | COINCIDENTAL |
| Fundamental explanation for 5/2 | OPEN |

---

## Appendix: Key Calculations

### de Sitter Temperature
```
T_dS = hbar*c*sqrt(Lambda/3) / (2*pi*k_B) = 2.2 x 10^-30 K
```

### Equipartition Cell Size at T_dS
```
V = (1/2)*k_B*T_dS / rho_Lambda = 2.9 x 10^-44 m^3
l = 3 x 10^-15 m (nuclear, not Compton)
```

### Species Factor
```
Observed: 2.58
N_species = 3: off by 16%
N_eff - 0.5 = 2.54: off by 1.5%
```

---

*DOF and Equipartition Analysis, February 2026*
