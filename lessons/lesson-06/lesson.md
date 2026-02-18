# Lesson 6: The Numbers -- Predictions and the 16pi^2 Factor

## Overview

The cell vacuum energy density $\rho = m^4 c^5 / \hbar^3$ is determined entirely by one free parameter: the mass $m$. This lesson examines the numerical predictions that emerge from this formula, the geometric origin of the $16\pi^2$ factor in the mode vacuum calculation, and the neutrino mass spectrum that follows from identifying $m$ with the lightest neutrino. We pay careful attention to what is genuinely predicted, what is extracted circularly from observation, and what has been demoted from earlier claims.

## 6.1 Dimensional Uniqueness: The 3x3 System

The formula $\rho = m^4 c^5 / \hbar^3$ is not one choice among many. It is the *unique* power-law combination of mass $m$, speed of light $c$, and reduced Planck constant $\hbar$ that has the dimensions of energy density. **[PROVEN]**

Here is the proof. We seek $\rho = m^a \, c^b \, \hbar^d$ with dimensions of energy density: $[\rho] = M L^{-1} T^{-2}$ in SI base units. The dimensional equations are:

$$
[m^a] = M^a, \quad [c^b] = L^b T^{-b}, \quad [\hbar^d] = M^d L^{2d} T^{-d}
$$

Matching dimensions:

$$
\text{Mass:} \quad a + d = 1
$$

$$
\text{Length:} \quad b + 2d = -1
$$

$$
\text{Time:} \quad -b - d = -2
$$

This is a $3 \times 3$ linear system with determinant $-1$ (nonzero), so the solution is unique:

$$
d = -3, \quad b = 5, \quad a = 4
$$

Therefore:

$$
\rho = K \cdot m^4 c^5 / \hbar^3
$$

where $K$ is a dimensionless constant that dimensional analysis alone cannot fix. The cell vacuum construction sets $K = 1$ (one quantum $mc^2$ per Compton cell of volume $\lambda_C^3$). **[PROVEN]**

**Important caveat:** The uniqueness applies to the power-law exponents. The dimensionless prefactor $K$ is a physical input from the construction, not determined by dimensional analysis. Different physical models could give different values of $K$.

## 6.2 The 16pi^2 Factor -- Geometric, Not Fundamental

In the mode vacuum calculation (Lesson 3), the energy density with UV cutoff $\Lambda$ is:

$$
\rho_{\text{mode}} = \frac{\hbar c \, \Lambda^4}{16\pi^2}
$$

The factor $16\pi^2$ arises from the angular integration in three spatial dimensions. Specifically, the volume element in $k$-space is $d^3k = 4\pi k^2 \, dk$ (the $4\pi$ is the solid angle $\Omega_3$ of the 2-sphere), and the radial integral together with the factors of $2\pi$ from the Fourier transform produces:

$$
\frac{1}{(2\pi)^3} \cdot 4\pi \cdot \frac{1}{4} = \frac{1}{16\pi^2}
$$

**[PROVEN]**

### The d-dimensional generalization

In $d$ spatial dimensions, the ratio of cell vacuum to mode vacuum energy density (at the Compton cutoff, with massless dispersion) is:

$$
C_d = \frac{2(d+1)(2\pi)^d}{\Omega_d}
$$

where $\Omega_d = 2\pi^{d/2}/\Gamma(d/2)$ is the surface area of the unit $(d-1)$-sphere. **[PROVEN]**

Evaluating:

| $d$ | $C_d$ | Value |
|-----|--------|-------|
| 1 | $4\pi$ | 12.57 |
| 2 | $12\pi$ | 37.70 |
| 3 | $16\pi^2$ | 157.91 |

The factor $16\pi^2$ is the $d = 3$ member of a dimension-dependent family. It is a geometric factor -- a property of the integration measure in three-dimensional $k$-space -- not a fundamental constant of nature. **[DEMOTED]**

Previous claims that $16\pi^2$ served as a "fundamental constant connecting the two vacua" or as a "self-dual" bridge between conjugate descriptions have been retired.

### Massive field correction

For a massive field (the physically relevant case), the dispersion relation is $\omega_k = \sqrt{k^2 c^2 + m^2 c^4/\hbar^2}$, not $\omega_k = c|k|$. At the Compton cutoff $\Lambda = mc/\hbar$, this changes the integral. The corrected ratio is approximately:

$$
C_3^{\text{massive}} \approx \frac{16\pi^2}{1.53} \approx 103
$$

The factor 1.53 is the dispersion correction that arises because the massive modes are slower (lower group velocity) than the massless approximation assumes. **[PROVEN]**

## 6.3 Mass Extraction from Dark Energy

Setting the cell vacuum energy density equal to the observed dark energy density:

$$
\rho_\Omega = m^4 c^5/\hbar^3 = \rho_\Lambda
$$

and solving for $m$:

$$
m = \left(\frac{\rho_\Lambda \hbar^3}{c^5}\right)^{1/4}
$$

Using $\rho_\Lambda \approx 5.96 \times 10^{-10}$ J/m$^3$:

$$
m_1 \approx 2.31 \text{ meV}/c^2
$$

**[FRAMEWORK]**

This is the scale of the lightest neutrino mass, which is suggestive but must be evaluated with extreme care.

## 6.4 The Circularity Warning

Here is where intellectual honesty is non-negotiable.

The extraction in Section 6.3 is **circular by construction**:

1. **Input:** observed $\rho_\Lambda \approx 5.96 \times 10^{-10}$ J/m$^3$
2. **Hypothesis:** $\rho_\Lambda = m^4 c^5 / \hbar^3$
3. **Extraction:** $m_1 = (\rho_\Lambda \hbar^3/c^5)^{1/4} \approx 2.31$ meV
4. **"Match":** $\rho_{\text{cell}} = m_1^4 c^5/\hbar^3 = \rho_\Lambda$ -- guaranteed by step 3

Step 4 is not a prediction. It is an algebraic tautology. The value $m_1$ was *defined* to make $\rho_{\text{cell}} = \rho_\Lambda$.

The "0.4% match" between cell vacuum energy density and observed dark energy density was previously presented as evidence for the theory. **This claim has been retired.** It is circular. **[FRAMEWORK]**

### When does the circularity break?

The prediction becomes non-trivial if and only if:

- **$m_1 \approx 2.31$ meV is independently confirmed** as the mass of the lightest neutrino, through oscillation experiments, cosmological observations, or direct measurement
- **The neutrino mass spectrum** derived from this $m_1$ combined with oscillation data matches observation

The circularity transforms from tautology into genuine prediction at the point where $m_1$ is independently constrained.

## 6.5 The Neutrino Mass Spectrum

Given $m_1 = 2.31$ meV and the measured mass-squared differences from neutrino oscillation experiments, the full spectrum follows:

$$
m_2 = \sqrt{m_1^2 + \Delta m_{21}^2} \approx \sqrt{(2.31)^2 + 75.3} \text{ meV} \approx 9.0 \text{ meV}
$$

$$
m_3 = \sqrt{m_1^2 + \Delta m_{31}^2} \approx \sqrt{(2.31)^2 + 2453} \text{ meV} \approx 49.6 \text{ meV}
$$

where $\Delta m_{21}^2 = 7.53 \times 10^{-5}$ eV$^2$ and $\Delta m_{31}^2 = 2.453 \times 10^{-3}$ eV$^2$ (PDG 2023 values). **[PROVEN]** for the oscillation data; **[FRAMEWORK]** for the prediction.

The total mass sum:

$$
\Sigma m_\nu = m_1 + m_2 + m_3 \approx 2.31 + 9.0 + 49.6 = 60.9 \text{ meV}
$$

**[FRAMEWORK]**

This prediction is genuinely testable. It does not depend on the circular reasoning of the density match -- it is a consequence of combining the extracted $m_1$ with independently measured oscillation parameters. If $\Sigma m_\nu$ is measured at approximately 61 meV, that would be significant evidence (though the $m_1$ input itself was extracted from $\rho_\Lambda$). If $\Sigma m_\nu$ is measured well below 50 meV, the specific value $m_1 = 2.31$ meV would be excluded.

### Normal ordering required

The framework requires normal mass ordering ($m_1 < m_2 < m_3$). If experiments determine that the mass ordering is inverted ($m_3 < m_1 < m_2$), the framework is falsified. Current data from NuFIT 6.0 favors normal ordering at approximately 2.5--3$\sigma$, which is consistent but not yet definitive. JUNO (expected 2026--2027) and DUNE (2030s) will determine the ordering at high significance. **[FRAMEWORK]**

### Current experimental status

The DESI DR2 constraint is $\Sigma m_\nu < 53$ meV at 95% confidence level, which is in 1.5--2$\sigma$ tension with the predicted 60.9 meV. This is not yet falsification (requiring 3--5$\sigma$), but the prediction is under pressure. **[TENSION]**

The falsification criteria are sharp:
- $\Sigma < 45$ meV at $> 3\sigma$: framework killed
- $\Sigma < 58$ meV at $> 5\sigma$: normal ordering with non-negligible $m_1$ killed
- Inverted ordering at $> 5\sigma$: framework killed

## 6.6 The Fourth-Root Shield

One reassuring feature of the formula $m = (\rho_\Lambda \hbar^3/c^5)^{1/4}$ is the fourth root. Uncertainties in $\rho_\Lambda$ are suppressed by a factor of 4 when propagated to $m$:

$$
\frac{\delta m}{m} = \frac{1}{4} \frac{\delta \rho_\Lambda}{\rho_\Lambda}
$$

The Hubble tension (10--15% uncertainty in $H_0$, which feeds into $\rho_\Lambda$) produces only a 2.5--3.5% uncertainty in $m_1$. This gives a robust range $m_1 = 2.24$--$2.34$ meV across the span of current $H_0$ measurements. **[PROVEN]** as a mathematical property of the fourth root.

## 6.7 What Survives the Demotions

This lesson contains results at several evidence tiers. Here is the honest accounting:

**Proven:**
- Dimensional uniqueness of $m^4 c^5/\hbar^3$ (the 3x3 system)
- The $16\pi^2$ factor as a geometric, dimension-dependent quantity
- The $C_d$ formula for arbitrary $d$
- The massive field correction factor of approximately 1.53
- The fourth-root suppression of uncertainties

**Framework (testable but not proven):**
- The identification $\rho_\Lambda = m^4 c^5/\hbar^3$
- The mass extraction $m_1 \approx 2.31$ meV
- The neutrino spectrum prediction $\Sigma \approx 60.9$ meV

**Demoted (tried and failed):**
- $16\pi^2$ as a "fundamental constant"
- The "0.4% match" as evidence (circular)
- Fenchel duality connecting the two vacua
- Variational uniqueness of $|\alpha|^2 = 1/2$

**Tension:**
- DESI DR2 bound ($\Sigma < 53$ meV) vs. prediction ($\Sigma \approx 61$ meV)

## Summary of Key Results

| Result | Status |
|--------|--------|
| $\rho = m^4 c^5/\hbar^3$ unique by dimensional analysis | [PROVEN] |
| $16\pi^2$ is geometric, not fundamental | [DEMOTED] |
| $C_d = 2(d+1)(2\pi)^d/\Omega_d$ | [PROVEN] |
| Massive field correction $\approx 103$ | [PROVEN] |
| $m_1 = (\rho_\Lambda \hbar^3/c^5)^{1/4} \approx 2.31$ meV | [FRAMEWORK] |
| $\Sigma m_\nu \approx 60.9$ meV | [FRAMEWORK] |
| $\rho_{\text{cell}} = \rho_\Lambda$ match is circular | [FRAMEWORK] |
| DESI tension at 1.5--2$\sigma$ | [TENSION] |

## Looking Ahead

The numbers in this lesson stand or fall on experimental test. In Lesson 7, we turn to the mathematical foundations: the algebraic quantum field theory (AQFT) construction that establishes the cell vacuum as a rigorous mathematical object, independent of whether its numerical predictions survive. The AQFT results are the strongest part of the theory -- proven mathematics that does not depend on whether $m_1 = 2.31$ meV or whether $\Sigma = 61$ meV.
