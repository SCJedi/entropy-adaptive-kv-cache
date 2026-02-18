# Attack Plan: Deriving (or Refuting) w = -1 for the Cell Vacuum

**Date**: February 1, 2026
**Status**: Plan for two independent teams
**Priority**: Highest tractable problem (I x T = 63, see 06_problem_selection.md)
**Goal**: Compute the equation of state parameter w = <p>/<rho> for the cell vacuum and determine whether w = -1

---

## 0. Executive Summary of the Problem

The cell vacuum |Omega> is a product of coherent states with |alpha|^2 = 1/2, one per Compton cell (hbar/mc)^3. The total energy per cell is mc^2, giving rho = m^4 c^5/hbar^3.

For the cell vacuum to serve as a cosmological constant, we need T_mu_nu = -rho g_mu_nu, i.e., w = p/rho = -1.

**The obstruction**: The stress-energy of a coherent state decomposes as:
```
<T_mu_nu>_Omega = <T_mu_nu>_reference + T_mu_nu^classical[f]
```

The classical displacement field f has spatial gradients on scale lambda_C within each cell. These gradients generate positive pressure. The previous team (02_curved_spacetime.md, Section 5.7) computed that the classical part alone gives w = -2/3.

**The question**: Does the full quantum calculation -- classical displacement plus quantum fluctuations, with proper renormalization -- give w = -1?

---

## 1. Precise Definition of the Calculation

### 1.1 The State

**Primary definition (Minkowski, for Steps A-D)**:

The cell vacuum on Minkowski spacetime is the state omega_Omega on the Weyl algebra W(S, sigma) defined by:
```
omega_Omega(W(g)) = omega_0(W(g)) * exp(i sigma(f_total, g))
```

where:
- omega_0 is the Fock vacuum (mode vacuum) state on W(S, sigma)
- f_total = sum_n f_n is the total classical displacement field
- f_n is a smooth Klein-Gordon solution localized to cell C_n
- The amplitude of each f_n is fixed by |alpha|^2 = 1/2, giving field amplitude phi_0 = mc/sqrt(2 hbar) per cell (see Section 4.4 of 02_curved_spacetime.md)
- sigma(f, g) is the symplectic form on the solution space

**Alternative definition (single-cell, for detailed computation)**:

For a single cell of volume V = lambda_C^3 = (hbar/mc)^3, the state is the coherent state |alpha> with |alpha|^2 = 1/2 of the single-mode oscillator:
```
a_cell = sqrt(m omega_C / (2 hbar)) phi_cell + i pi_cell / sqrt(2 m hbar omega_C)
```
with omega_C = mc^2/hbar. Here phi_cell and pi_cell are the field and conjugate momentum smeared over the cell volume.

**For FRW (Step E)**:

On FRW ds^2 = -c^2 dt^2 + a(t)^2 dx^2, the cell vacuum is the Weyl displacement of the adiabatic vacuum of order >= 4 (which is Hadamard), with the same local construction in each proper-volume Compton cell of fixed size lambda_C^3.

### 1.2 The Operator

The stress-energy tensor operator for a real massive scalar field with minimal coupling (xi = 0):
```
T_mu_nu = nabla_mu phi nabla_nu phi - (1/2) g_mu_nu (nabla^alpha phi nabla_alpha phi + m^2 c^2 phi^2 / hbar^2)
```

**Renormalized expectation value** (Hadamard point-splitting):
```
<T_mu_nu(x)>_ren = lim_{y -> x} D_mu_nu(x,y) [W_Omega(x,y) - H(x,y)] + geometric counterterms
```

where:
- W_Omega(x,y) = omega_Omega(phi(x) phi(y)) is the two-point function of the cell vacuum
- H(x,y) is the Hadamard parametrix
- D_mu_nu is the point-split differential operator corresponding to the classical T_mu_nu
- Geometric counterterms include terms proportional to g_mu_nu, G_mu_nu, etc. (Wald ambiguity)

For a coherent state displaced from the mode vacuum:
```
W_Omega(x,y) = W_0(x,y) + F(x) F(y)
```

where W_0 is the Fock vacuum two-point function and F(x) = omega_Omega(phi(x)) is the one-point function (classical displacement field). This decomposition is proven in the AQFT construction (Theorem 5.3 of 01_aqft_foundations.md).

### 1.3 The Spacetime

**Primary**: Minkowski spacetime (Steps A-D). This is where the detailed mode calculations are tractable.

**Secondary**: Spatially flat FRW (Step E). The key question is whether the adiabatic expansion introduces corrections that shift w.

**Not needed**: General curved spacetime. The self-consistency analysis (02_curved_spacetime.md, Section 7) shows R lambda_C^2 ~ 10^{-69}, so Minkowski is an excellent approximation.

### 1.4 The Renormalization Scheme

**Primary**: Hadamard point-splitting subtraction. Standard recipe:
1. Compute W_Omega(x,y)
2. Compute H(x,y) (Hadamard parametrix, determined by geometry and mass)
3. Subtract: W_reg(x,y) = W_Omega(x,y) - H(x,y)
4. Apply D_mu_nu and take coincidence limit
5. Add geometric counterterms (Wald ambiguity)

**Cross-check**: Adiabatic regularization (subtract WKB expansion to 4th adiabatic order). On Minkowski, this reduces to standard normal ordering.

**On Minkowski specifically**: The Hadamard subtraction is equivalent to normal ordering, so:
```
<T_mu_nu>_ren = <Omega| :T_mu_nu: |Omega> + (Wald ambiguity terms)
```

where :T_mu_nu: denotes normal ordering with respect to the Fock vacuum.

---

## 2. Step-by-Step Calculation Plan

### Step A: Compute <Omega|T_mu_nu|Omega> in Minkowski for a Single Cell

**Objective**: Compute all components of <T_mu_nu> for the coherent state |alpha> (|alpha|^2 = 1/2) of a single oscillator mode in a box of size lambda_C.

**Sub-steps**:

**A1. Set up the single-cell mode decomposition**
- Consider a cubic box of side L = lambda_C = hbar/(mc) with periodic boundary conditions
- Allowed wavevectors: k_i = 2 pi n_i / L for integers n_i
- The "cell mode" is the k = 0 mode (zero momentum, frequency omega_0 = mc^2/hbar)
- Higher modes have k != 0 with omega_k = c sqrt(|k|^2 + m^2 c^2/hbar^2)

**A2. Define the coherent state precisely**
- The cell vacuum displaces ONLY the k = 0 mode: a_0 |alpha> = alpha |alpha> with |alpha|^2 = 1/2
- All other modes are in their ground state: a_k |0_k> = 0 for k != 0
- Total state: |Omega_cell> = |alpha>_0 tensor |0>_{k!=0}

**CRITICAL QUESTION**: Is the cell vacuum constructed by displacing only the k = 0 mode, or does the localized coherent state involve a superposition of modes? The framework says "coherent state localized to cell n." A state localized to a finite region necessarily involves multiple k-modes. This must be resolved before proceeding.

**Two sub-cases to compute**:

**Case 1: Homogeneous displacement (k = 0 mode only)**
- The displacement field F(x) = F_0 = constant within the cell
- No spatial gradients: nabla F = 0
- Classical stress-energy: T_00^cl = (1/2) m^2 c^4 F_0^2/hbar^2, T_ij^cl = -(1/2) m^2 c^4 F_0^2/hbar^2 delta_ij
- This gives w_classical = -1 for the classical part
- Total: w = -1 (since zero-point part also gives w = -1 by Lorentz invariance)

**Case 2: Localized displacement (wavepacket involving multiple modes)**
- F(x) is a wavepacket localized to one cell, with spatial extent ~ lambda_C
- Necessarily involves k-modes up to k ~ mc/hbar
- Has spatial gradients: |nabla F|^2 ~ F_0^2 / lambda_C^2 = F_0^2 m^2 c^2/hbar^2
- Previous team computed: w_classical = -2/3 for this case

**This is THE key fork in the calculation. The two cases give different answers.**

**A3. Compute T_mu_nu for Case 1 (homogeneous displacement)**
```
<T_00>_cell = (1/2) m^2 c^4 F_0^2/hbar^2 + <0|T_00|0>_ren
            = rho_classical + rho_quantum

<T_ij>_cell = -(1/2) m^2 c^4 F_0^2/hbar^2 delta_ij + <0|T_ij|0>_ren
```

With normal ordering on Minkowski, <0|:T_mu_nu:|0> = 0. But the Wald ambiguity allows:
```
<0|T_mu_nu|0>_ren = Lambda_0 g_mu_nu
```
for arbitrary Lambda_0.

If Lambda_0 is chosen so that total rho = m^4 c^5/hbar^3, then w = -1 trivially (since both parts are proportional to g_mu_nu).

**A4. Compute T_mu_nu for Case 2 (localized displacement)**

This is the non-trivial computation. Need:
```
F(x) = sum_{k} c_k e^{ik.x} / sqrt(V)
```
where c_k are chosen so F(x) is localized to one cell with total energy:
```
E_displacement = integral_cell [(1/2)(nabla F)^2 c^2 + (1/2) m^2 c^4 F^2/hbar^2] d^3x = mc^2/2
```
(The displacement contributes half the total energy; zero-point contributes the other half.)

Compute:
```
T_00^cl = (1/2) c^2 (nabla F)^2 + (1/2) m^2 c^4 F^2/hbar^2
T_ij^cl = c^2 (partial_i F)(partial_j F) - (1/2) delta_ij [c^2 (nabla F)^2 + m^2 c^4 F^2/hbar^2]
```

Average over the cell (assuming isotropy of gradients):
```
<partial_i F partial_j F>_cell = (1/3) delta_ij <|nabla F|^2>_cell
```

Then compute p_cl/rho_cl. The previous team found this gives -2/3.

**A5. Compute the quantum fluctuation contribution**

The quantum part is:
```
<T_mu_nu>_quantum = <0| :T_mu_nu: |0>_cell + Wald ambiguity
```

For a SINGLE cell with periodic boundary conditions, the normal-ordered vacuum energy density is:
```
<:T_00:> = (1/V) sum_{k != 0} hbar omega_k / 2 - (renormalization subtraction)
```

This is ZERO in dimensional regularization / zeta-function regularization on Minkowski. But it is ambiguous up to the Wald constant Lambda_0.

**Key question**: Is there a NATURAL (non-arbitrary) way to fix the quantum contribution in the single-cell setting?

**A6. Combine classical + quantum and compute w**

```
w = [p_classical + p_quantum] / [rho_classical + rho_quantum]
```

For Case 1: w = -1 (trivially, if quantum part is proportional to g_mu_nu)
For Case 2: w = [(-2/3) rho_cl + w_q rho_q] / [rho_cl + rho_q]

If rho_cl = rho_q = rho/2 and w_q = -1:
```
w = [(-2/3)(rho/2) + (-1)(rho/2)] / rho = (-1/3 - 1/2) = -5/6
```

If rho_cl = rho_q = rho/2 and w_q is chosen to make w = -1:
```
-1 = [(-2/3)(rho/2) + w_q (rho/2)] / rho
-1 = -1/3 + w_q/2
w_q = -4/3
```

Can the quantum part have w_q = -4/3? This requires p_q = -4/3 rho_q, which is more negative than a cosmological constant. Is this physically permissible? The Wald ambiguity only adds terms proportional to g_mu_nu (giving w = -1). So w_q = -1 from the ambiguity, giving w = -5/6. Unless there are additional quantum contributions.

**THIS IS THE CRUX. If Case 2 is correct and the quantum fluctuations give w_q = -1, then w = -5/6, NOT -1.**

---

### Step B: Sum/Average Over Cells

**Objective**: Determine whether inter-cell effects modify w.

**B1. Isolated cell vs. periodic lattice**
- For a periodic lattice of identical cells, the field configuration is periodic with period lambda_C
- This is different from a single isolated cell
- For a periodic homogeneous displacement (Case 1 on a lattice): F = constant everywhere. No gradients. w = -1.
- For a periodic localized displacement (Case 2 on a lattice): F(x) is periodic with sharp features at cell boundaries

**B2. The periodic lattice as a Bloch-like problem**
- If the cell vacuum is a product of IDENTICAL coherent states, the total displacement is periodic
- Periodic displacement -> can be decomposed into discrete Fourier components at the reciprocal lattice vectors G = 2 pi n / lambda_C
- The "gradient energy" at cell boundaries contributes to the pressure

**B3. Edge effects and the continuum limit**
- For a smooth cell decomposition (using smooth partition of unity), there are no sharp boundaries
- The smoothing function chi_n(x) introduces gradients of order 1/lambda_C
- These gradient contributions to T_ij are real and must be accounted for

**B4. The averaging theorem**
- For a homogeneous, isotropic state at scales >> lambda_C, the spatially averaged stress-energy must take the perfect fluid form:
  ```
  <T_mu_nu>_avg = (rho + p/c^2) u_mu u_nu + p g_mu_nu
  ```
- The question is: what are the averaged rho and p?

---

### Step C: Separate Classical Displacement from Quantum Fluctuations

**Objective**: Rigorously decompose <T_mu_nu> into parts and track w for each.

**C1. The exact decomposition (proven result)**
```
<T_mu_nu>_Omega = <T_mu_nu>_0 + T_mu_nu^classical[F]
```

where:
- <T_mu_nu>_0 = renormalized stress-energy of the reference (Fock) vacuum
- T_mu_nu^classical[F] = classical stress-energy of the displacement field F

This decomposition is exact for coherent states. The cross terms vanish because omega_0(phi(x)) = 0.

**C2. Equation of state of each part**

Part 1: <T_mu_nu>_0 (reference vacuum)
- On Minkowski with normal ordering: <:T_mu_nu:>_0 = 0
- With Wald ambiguity: <T_mu_nu>_0 = Lambda_0 g_mu_nu -> w_0 = -1 for any Lambda_0

Part 2: T_mu_nu^classical[F] (displacement field)
- Depends entirely on the profile of F(x)
- For F = constant (homogeneous): w_cl = -1
- For F localized to cells with gradients: w_cl = -2/3 (previous result)

**C3. The energy partition**
- Coherent state energy: E = hbar omega (|alpha|^2 + 1/2) = hbar omega
- Displacement energy: E_cl = hbar omega |alpha|^2 = hbar omega / 2
- Zero-point energy: E_zp = hbar omega / 2
- Each contributes exactly half the total

**C4. Key insight: the displacement field profile determines everything**

Since the quantum part (Part 1) has w = -1 regardless of renormalization (it's proportional to g_mu_nu up to the Wald ambiguity), the only way to get w != -1 is from Part 2 (the classical displacement field). And Part 2 gives w = -1 if and only if F has no spatial gradients.

**Therefore: w = -1 if and only if the coherent state displacement is spatially homogeneous within each cell.**

---

### Step D: Identify the Equation of State

**Objective**: Determine w precisely, resolving the Case 1 vs Case 2 ambiguity.

**D1. The fundamental question**

What IS the classical field configuration F(x) of the cell vacuum?

**Option D1a: F(x) = constant (zero-mode displacement)**
- Each cell is displaced in the k = 0 mode only
- F is spatially uniform within each cell
- nabla F = 0 (except at cell boundaries, which are measure-zero)
- w_classical = -1
- Total w = -1

**Option D1b: F(x) = localized wavepacket**
- The coherent state is localized to one cell using a smooth cutoff chi_n(x)
- F(x) = phi_0 * chi_n(x) where chi_n has support in cell n
- nabla F ~ phi_0 / lambda_C != 0
- w_classical = -2/3
- Total w = -5/6 (if quantum part is w = -1 with equal energy share)

**Option D1c: F(x) involves the lowest confined mode of the cell**
- Like a particle-in-a-box ground state wavefunction
- F(x) = phi_0 * cos(pi x/L) * cos(pi y/L) * cos(pi z/L) (in the cell)
- Spatial gradients present but with specific structure
- w_classical must be computed explicitly for this profile

**D2. Which option is physically correct?**

This is the decisive interpretive question. Arguments for each:

**For D1a (homogeneous, w = -1)**:
- The simplest choice: "one quantum in the zero-momentum mode of the cell"
- The cell vacuum was originally described as "one quantum mc^2 per cell" where the quantum has the rest-frame frequency omega = mc^2/hbar, which is the k = 0 mode
- If the cell has periodic boundary conditions, the k = 0 mode is the lowest energy mode
- No localization is needed because the cell already provides the spatial domain
- The displacement is not "localized to the cell" -- it IS the cell's zero mode

**For D1b/c (localized, w = -2/3 or similar)**:
- The cell vacuum is described as "localized to cell n"
- In the AQFT Weyl algebra formulation, the displacement f_n is constructed using a smearing function supported in cell n
- A function supported in a finite region must have nonzero spatial gradients (Paley-Wiener theorem: spatially compact functions have nonzero Fourier components at all k)
- The f_n are not zero-mode displacements -- they involve a spread of momenta

**D3. Resolution strategy**

Both teams must independently:

1. Compute w for Option D1a explicitly (should give -1)
2. Compute w for Option D1b explicitly (should give ~ -2/3)
3. Compute w for Option D1c explicitly
4. Determine which option correctly represents the cell vacuum construction
5. If D1a: w = -1 and the framework is validated (for this question)
6. If D1b/D1c: compute the exact w and determine whether any quantum correction can restore w = -1

**D4. The mode-counting argument**

For a massive field in a box of size L = lambda_C:
- The k = 0 mode has energy mc^2 (for |alpha|^2 = 1/2 coherent state)
- The number of sub-Compton modes is approximately 1 (the cell is one Compton wavelength)
- So the "cell vacuum" is essentially a single-mode coherent state in the zero mode
- This supports Option D1a

**D5. The Weyl algebra argument**

In the curved-spacetime Weyl algebra formulation (02_curved_spacetime.md, Section 4):
- The displacement is f_n = E(chi_n) where chi_n is supported in cell n
- E is the causal propagator, which smears chi_n along the light cone
- f_n as a Klein-Gordon solution has support beyond cell n
- But the key question is: what is the ENERGY distribution of f_n?
- If chi_n is chosen as a smooth, slowly varying function over the cell, then f_n is dominated by the k ~ 0 component (rest-mass mode)
- The gradient energy is O(m^2 c^2/hbar^2 * lambda_C^2) ~ O(1) relative to the mass energy -- NOT negligible

This suggests Option D1b/D1c may be forced by the Weyl algebra construction.

**D6. Critical test: compute w for a concrete cell vacuum wavefunction**

Choose a specific F(x) and compute w explicitly. Proposed choice:

For a single cell [0, L]^3 with L = lambda_C:
```
F(x) = phi_0 * prod_{i=1}^3 sqrt(2/L) sin(pi x_i / L)
```
(ground state of box with Dirichlet boundaries)

The normalization gives:
```
integral_cell F^2 d^3x = phi_0^2 * V * (2/L)^3 * (L/2)^3 = phi_0^2 V
```

The gradient:
```
|nabla F|^2 = phi_0^2 * (pi/L)^2 * 3 * (2/L)^3 * ... [compute explicitly]
```

Average ratio:
```
<|nabla F|^2> / <m^2 c^2 F^2/hbar^2> = (pi/L)^2 * (3 * average of cos^2) / (m^2 c^2/hbar^2 * average of sin^2)
```

Since L = hbar/(mc), we get (pi mc/hbar)^2 / (m^2 c^2/hbar^2) = pi^2 ~ 10.

This gives gradient energy ~ pi^2 times mass energy, not comparable! Check: this means the localized wavefunction has MUCH more gradient energy than mass energy, which would give a very different w.

**This needs careful numerical calculation.**

---

### Step E: Check on FRW Background

**Objective**: Determine whether cosmological expansion modifies w.

**E1. Adiabatic expansion**
- The adiabatic parameter is H lambda_C / c ~ 10^{-31} (from Section 6.3 of 02_curved_spacetime.md)
- Corrections to mode functions are O(H/omega_C)^2 ~ 10^{-62}
- These are utterly negligible

**E2. Conformal coupling vs minimal coupling**
- For minimally coupled (xi = 0) massive field: trace anomaly contributes curvature terms to <T_mu_mu>
- For conformal coupling (xi = 1/6): trace anomaly is different
- The framework uses minimal coupling (standard for massive scalars)
- The trace anomaly correction to w is of order (H/omega_C)^4 ~ 10^{-124} -- negligible

**E3. Time-dependent cell construction**
- Cells maintain fixed proper volume lambda_C^3 as universe expands
- New cells are "created" to fill expanding space
- Energy density rho = mc^2/lambda_C^3 = constant -> consistent with w = -1
- But this is the thermodynamic argument, not the stress-energy computation
- The stress-energy computation should agree, and any discrepancy signals an error

**E4. Bogoliubov mixing**
- Cosmological expansion mixes positive and negative frequency modes
- For massive fields with omega >> H, the Bogoliubov coefficient |beta_k|^2 ~ (H/omega_C)^2 ~ 10^{-62}
- Particle creation is negligible
- The cell vacuum is adiabatically stable

**Conclusion for Step E**: FRW corrections are at most O(10^{-60}) and can be ignored. The Minkowski calculation determines w to all physically relevant precision.

---

### Step F: Assess Renormalization Scheme Dependence

**Objective**: Determine how sensitive w is to the renormalization prescription.

**F1. The Wald ambiguity for T_mu_nu**

The renormalized <T_mu_nu> is determined up to:
```
<T_mu_nu> -> <T_mu_nu> + alpha_1 g_mu_nu + alpha_2 G_mu_nu + alpha_3 I_mu_nu + alpha_4 J_mu_nu
```

On Minkowski spacetime, G_mu_nu = R_mu_nu = 0, so only the alpha_1 g_mu_nu term survives.

**Key point**: The alpha_1 g_mu_nu term has w = -1 by construction (it's a cosmological constant). Therefore, the Wald ambiguity CANNOT change w away from -1 -- it can only add a w = -1 component.

**This means**: If the unambiguous part (the classical displacement) gives w != -1, the ambiguity cannot fix it. The value of w for the classical displacement is renormalization-scheme-independent.

**F2. Scheme comparison**
- Normal ordering (Minkowski): <:T_mu_nu:>_0 = 0
- Hadamard subtraction (Minkowski): same as normal ordering (Minkowski IS the reference)
- Adiabatic regularization (FRW, 4th order): agrees with Hadamard to O(R^2) corrections
- Zeta function: may differ by finite local terms proportional to g_mu_nu

All schemes agree on the STATE-DEPENDENT part. They differ only in the geometric (state-independent) counterterms, which are all proportional to g_mu_nu on Minkowski.

**F3. Conclusion**

w is renormalization-scheme-INDEPENDENT (on Minkowski). The Wald ambiguity adds only w = -1 contributions. The classical displacement's equation of state is unambiguous. If the displacement gives w = -2/3, no renormalization scheme can change this to w = -1.

**THIS IS A CRITICAL RESULT. If confirmed, it means w = -1 requires the displacement to be spatially homogeneous (Case 1 / Option D1a).**

---

## 3. Key Technical Challenges

### Challenge 1: What is the displacement field profile?

The cell vacuum construction says "coherent state |alpha> with |alpha|^2 = 1/2 localized to cell n." But "localized to cell n" is ambiguous:

**(a)** If it means "the k = 0 mode of the cell's mode decomposition" -> F = constant -> w = -1
**(b)** If it means "a wavepacket with support in cell n" -> F has gradients -> w != -1
**(c)** If it means "the Weyl algebra displacement using a test function in cell n" -> same as (b)

Resolving this ambiguity is the #1 priority. Both teams must address it independently.

### Challenge 2: The Hadamard subtraction reference

The Hadamard subtraction uses H(x,y) as the reference. On Minkowski, this is equivalent to normal ordering with respect to |0>. The result:
```
<T_mu_nu>_Omega - <T_mu_nu>_0 = T_mu_nu^classical[F]
```

is scheme-independent. But the ABSOLUTE value <T_mu_nu>_Omega depends on the scheme. Since gravity couples to the absolute value, this matters for the energy density but NOT for the equation of state w (since w is a ratio and the scheme-dependent part has w = -1).

### Challenge 3: Cell boundary effects

At cell boundaries, the displacement field must match between adjacent cells. For a product state, each cell is independent, so:
- If each cell has F = constant (Case 1), the field is discontinuous at boundaries
- If each cell has F = localized wavepacket (Case 2), the field goes to zero at boundaries
- Discontinuities would produce delta-function gradient energy at boundaries

The smooth Weyl algebra construction (using smooth partition of unity) avoids discontinuities but introduces gradient energy.

### Challenge 4: The massive field propagator

For a massive scalar field, the Wightman function is:
```
W_0(x,y) = integral d^3k/(2pi)^3 * 1/(2 omega_k) * e^{-i omega_k (t-t') + ik.(x-y)}
```

with omega_k = c sqrt(k^2 + m^2 c^2/hbar^2).

The mass makes the integrals more complex than the massless case. For the stress-energy, one needs:
```
D_mu_nu W_0 = nabla_mu nabla_nu' W_0 - (1/2) g_mu_nu [g^{alpha beta} nabla_alpha nabla_beta' W_0 + m^2 c^2 W_0/hbar^2]
```

evaluated at coincidence. This involves regularized sums over modes.

### Challenge 5: Reconciling the oscillator picture with the field picture

In the oscillator picture: each cell contains one quantum mc^2 in a harmonic oscillator with omega = mc^2/hbar. The zero-point energy of this oscillator has p = -E (w = -1). Total: w = -1.

In the field picture: the coherent state has a classical displacement with spatial profile. The stress-energy depends on the profile. If the profile has gradients, w != -1.

These pictures should agree. The discrepancy arises from the meaning of "localization" and whether the oscillator mode is spatially uniform or localized.

---

## 4. Success Criteria

### 4.1 What constitutes success?

| Outcome | Meaning | Action |
|---------|---------|--------|
| w = -1 exactly | Cell vacuum IS a cosmological constant | Framework's key prediction validated |
| w = -1 + O(R lambda_C^2) | w = -1 up to curvature corrections of 10^{-69} | Essentially the same as w = -1 |
| w = -1 + O(numerical coefficient) where coefficient is small | w close to -1 but not exact | Partial success; compute the coefficient precisely |
| w = -2/3 or -5/6 | Classical gradients dominate; quantum cannot restore w = -1 | Framework has a problem; must reinterpret the cell vacuum |
| w depends on renormalization scheme | Ambiguous result | The question is ill-posed without additional input |

### 4.2 Precision needed

Observational constraint: w = -1.03 +/- 0.03 (DESI DR2 + Planck). Therefore:
- w must be within [-1.06, -1.00] to be consistent with data
- w = -2/3 = -0.67 is EXCLUDED by >10 sigma
- w = -5/6 = -0.83 is EXCLUDED by >5 sigma
- w = -0.95 would be in ~3 sigma tension

**Bottom line**: w must be very close to -1. Values of w > -0.9 definitively falsify the framework.

### 4.3 What constitutes definitive failure?

1. **w = -2/3 unavoidably**: If the localized displacement (Case 2) is the correct interpretation AND no quantum correction shifts w to -1, the framework fails to produce a cosmological constant.

2. **w is scheme-dependent (between -2/3 and -1)**: If the answer depends on an arbitrary choice, the framework loses predictive power for w.

3. **The calculation is ill-defined**: If the stress-energy computation for the cell vacuum is ambiguous beyond the Wald terms, the framework has a foundational problem.

---

## 5. Verification Checkpoints

### Checkpoint 1: Does the zero-point part give w = -1?

**Expected**: Yes. The mode vacuum's renormalized stress-energy on Minkowski is proportional to g_mu_nu (by Lorentz invariance of the vacuum + Wald ambiguity form). Therefore the zero-point part contributes w_0 = -1.

**Verify by**: Computing <0|:T_mu_nu:|0> using mode sums in a box. Should give zero (normal ordered). Adding the Wald term gives Lambda_0 g_mu_nu with w = -1.

### Checkpoint 2: Does the displacement part give w = -2/3?

**Expected** (for localized Case 2): Yes, per the previous team's calculation. But verify:

For a static, localized displacement F(x) in a cell:
```
rho_cl = (1/2) c^2 |nabla F|^2 + (1/2) m^2 c^4 F^2/hbar^2
p_cl = (1/3)[c^2 |nabla F|^2 - 3((1/2) c^2 |nabla F|^2 + (1/2) m^2 c^4 F^2/hbar^2)]
     = (1/3) c^2 |nabla F|^2 - (1/2) c^2 |nabla F|^2 - (1/2) m^2 c^4 F^2/hbar^2
     = -(1/6) c^2 |nabla F|^2 - (1/2) m^2 c^4 F^2/hbar^2
```

Wait -- this doesn't immediately give -2/3. Let me redo. Using <partial_i F partial_j F> = (1/3) delta_ij |nabla F|^2:
```
T_ij = (partial_i F)(partial_j F) c^2 - (1/2) delta_ij [c^2 |nabla F|^2 + m^2 c^4 F^2/hbar^2]

<T_ij>_avg = (1/3) delta_ij c^2 |nabla F|^2 - (1/2) delta_ij [c^2 |nabla F|^2 + m^2 c^4 F^2/hbar^2]
           = delta_ij [c^2 |nabla F|^2/3 - c^2 |nabla F|^2/2 - m^2 c^4 F^2/(2 hbar^2)]
           = delta_ij [-c^2 |nabla F|^2/6 - m^2 c^4 F^2/(2 hbar^2)]

p = (1/3) T_ii = -c^2 |nabla F|^2/6 - m^2 c^4 F^2/(2 hbar^2)
```

Now if |nabla F|^2 ~ m^2 c^2 F^2/hbar^2 (gradient energy ~ mass energy):
```
rho = c^2 * m^2 c^2 F^2/(2 hbar^2) + m^2 c^4 F^2/(2 hbar^2) = m^2 c^4 F^2/hbar^2

p = -m^2 c^4 F^2/(6 hbar^2) - m^2 c^4 F^2/(2 hbar^2) = -2 m^2 c^4 F^2/(3 hbar^2)

w = p/rho = -2/3
```

**Confirmed**: w = -2/3 for the classical displacement when gradient energy equals mass energy.

**For homogeneous Case 1** (|nabla F| = 0):
```
rho = m^2 c^4 F^2/(2 hbar^2)
p = -m^2 c^4 F^2/(2 hbar^2)
w = -1
```

**Confirmed**: w = -1 for homogeneous displacement.

### Checkpoint 3: What is the ratio of displacement to zero-point energy?

**Expected**: Exactly 1:1.
```
E_displacement = hbar omega |alpha|^2 = hbar omega / 2 = mc^2/2
E_zero-point = hbar omega / 2 = mc^2/2
```

This is an algebraic identity for coherent states with |alpha|^2 = 1/2.

### Checkpoint 4: What does the sum give?

**For Case 1 (homogeneous)**:
```
w_total = [(-1)(mc^2/2) + (-1)(mc^2/2)] / mc^2 = -1
```

**For Case 2 (localized, equal gradient and mass energy)**:
```
w_total = [(-2/3)(mc^2/2) + (-1)(mc^2/2)] / mc^2
        = (-1/3 - 1/2) = -5/6
```

**For Case 2 (localized, with different gradient/mass ratio r = |nabla F|^2/(m^2 c^2 F^2/hbar^2))**:
```
rho_cl = (1/2)(1+r) m^2 c^4 F^2/hbar^2
p_cl = -(1/2)(r/3 + 1) m^2 c^4 F^2/hbar^2   [check this]

Actually: p_cl = -r/6 * m^2 c^4 F^2/hbar^2 * c^{-2}...
```

The calculation needs to be done carefully with consistent units. This is exactly what the teams should do.

---

## 6. Team Assignments

### Team Alpha: The Single-Cell Quantum Calculation

**Approach**: Treat the cell vacuum as a quantum oscillator problem. Work in the canonical quantization formalism in a box of size lambda_C.

**Specific tasks**:
1. Set up the Klein-Gordon field in a box [0, L]^3, L = lambda_C, with periodic boundary conditions
2. Identify the mode decomposition: k = 2pi n/L, omega_k = c sqrt(k^2 + m^2 c^2/hbar^2)
3. Define the coherent state for the k = 0 mode (Case 1) with |alpha|^2 = 1/2
4. Compute <T_mu_nu> exactly (all components) by mode sums
5. For the k = 0 coherent state, verify w = -1
6. Define a localized coherent state (Case 2) using a Gaussian or box wavefunction
7. Compute <T_mu_nu> for the localized state
8. Determine which definition is consistent with the cell vacuum construction's physical premises
9. Compute w for the physically correct state
10. Write up with full derivation

**Key question Team Alpha must answer**: "In a box of size lambda_C, what is the stress-energy of a coherent state with |alpha|^2 = 1/2 and energy mc^2, defined in the physically correct way?"

### Team Beta: The AQFT/Weyl Algebra Calculation

**Approach**: Use the Weyl algebra formulation on Minkowski spacetime. Work with the displacement field f_total and the Hadamard subtraction.

**Specific tasks**:
1. Define the cell vacuum using the Weyl algebra displacement: omega_Omega(W(g)) = omega_0(W(g)) exp(i sigma(f_total, g))
2. Specify f_total concretely: what Klein-Gordon solution represents the cell vacuum displacement?
3. Compute the two-point function W_Omega(x,y) = W_0(x,y) + F(x)F(y)
4. Compute the Hadamard-subtracted stress-energy using point-splitting
5. Evaluate all components of <T_mu_nu>_ren
6. Compute w = <T_ii>/(3 <T_00>)
7. Analyze the dependence on the choice of f_total (sensitivity to the displacement field profile)
8. Determine whether any choice of f_total is singled out by the cell vacuum construction
9. If w != -1, determine whether FRW corrections can help
10. Write up with full derivation

**Key question Team Beta must answer**: "In the Weyl algebra formulation, what is the stress-energy of the cell vacuum state, and does it give T_mu_nu proportional to g_mu_nu?"

---

## 7. Decisive Question Both Teams Must Resolve

Both teams must independently answer the SAME central question:

> **Is the cell vacuum displacement field spatially homogeneous within each cell (F = constant), or does it have spatial gradients (F varies on scale lambda_C)?**

If F = constant: w = -1. The framework is vindicated.
If F varies: w != -1 (likely ~ -2/3 to -5/6). The framework has a serious problem.

**The arguments for F = constant**:
- The cell oscillator has frequency omega = mc^2/hbar, which is the rest-frame (k = 0) frequency
- A coherent state of the k = 0 mode is spatially uniform
- The "one quantum per cell" counting uses the total cell energy, not a localized wavepacket
- The harmonic oscillator analogy (ground state with one quantum) refers to the normal mode, not a localized excitation

**The arguments for F varying**:
- The Weyl algebra construction uses f_n = E(chi_n) where chi_n has compact support in cell n
- A function with compact spatial support must have nonzero gradients (and even nonzero k-components)
- The product state structure (cells independent) requires F to vanish outside each cell
- If F = constant in every cell, the total F = constant everywhere, and there is no cell structure at all

**THIS IS THE KEY TENSION**:
- If F = constant everywhere, there are no cells. The "cell vacuum" is just a uniformly displaced vacuum. It's a legitimate coherent state, but the cell structure is invisible.
- If F varies cell by cell, the cell structure is real but gradients shift w away from -1.

**Possible resolution**: The cell vacuum is DEFINED by the product state structure, which is a statement about the quantum state (factorization of the density matrix), NOT about the classical displacement field profile. The displacement field is spatially uniform (F = constant), but the state factorizes because each cell's oscillator is in a coherent state independently. The cell structure is in the quantum correlations (or lack thereof -- product state), not in the classical field.

**If this resolution is correct**: F = constant, w = -1, and the cell structure manifests only in the absence of inter-cell entanglement, not in spatial variation of the field.

**Both teams must evaluate this resolution critically and independently.**

---

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| w = -1 trivially (Case 1) | 40% | High (positive) | Verify that Case 1 is the correct interpretation; check for hidden assumptions |
| w = -2/3 definitively (Case 2) | 25% | High (negative) | Explore whether reinterpretation of cell vacuum can recover w = -1 |
| w depends on interpretation (Case 1 vs Case 2 ambiguous) | 25% | Medium | This IS the research output -- clarifying the interpretation is valuable |
| Calculation error | 10% | Variable | Two independent teams cross-check |
| The problem is fundamentally ill-posed | 5% | High | Report clearly what additional input is needed |

---

## 9. Timeline and Deliverables

### Phase 1: Setup and Checkpoint Verification (first 30%)
- Both teams set up their formalism
- Verify Checkpoints 1-3 independently
- Report any discrepancies

### Phase 2: Core Calculation (next 40%)
- Team Alpha: compute <T_mu_nu> in the box/oscillator formalism
- Team Beta: compute <T_mu_nu> in the Weyl algebra formalism
- Both teams resolve the F = constant vs F = varying question

### Phase 3: Synthesis and Verification (final 30%)
- Compare results between teams
- Resolve any discrepancies
- Compute w to maximal precision
- Assess scheme dependence (Step F)
- Write final report

### Deliverables
1. **From each team**: Full derivation of <T_mu_nu> for the cell vacuum
2. **From each team**: Explicit value of w with error analysis
3. **Joint**: Resolution of the displacement field profile question
4. **Joint**: Assessment of whether w = -1 is derived, assumed, or refuted

---

## 10. References

1. Wald, R.M. (1994). *Quantum Field Theory in Curved Spacetime and Black Hole Thermodynamics*. Chicago.
2. Hollands, S. and Wald, R.M. (2001). "Local Wald Entropy in Higher Derivative Gravity." Classical and Quantum Gravity.
3. Birrell, N.D. and Davies, P.C.W. (1982). *Quantum Fields in Curved Space*. Cambridge.
4. Parker, L. and Toms, D. (2009). *Quantum Field Theory in Curved Spacetime*. Cambridge.
5. Kay, B.S. and Wald, R.M. (1991). "Theorems on the uniqueness and thermal properties of stationary, nonsingular, quasifree states." Phys. Rep. 207, 49-136.
6. Brunetti, R., Fredenhagen, K., and Verch, R. (2003). "The generally covariant locality principle -- A new paradigm for local quantum field theory." Commun. Math. Phys. 237, 31-68.
7. This project's AQFT construction: 01_aqft_foundations.md
8. This project's curved spacetime analysis: 02_curved_spacetime.md
9. This project's problem selection: 06_problem_selection.md
10. Knowledge base: .claude/specialists/two-vacua-feynman/knowledge-base.md

---

**Plan prepared**: February 1, 2026
**Status**: Ready for team execution
**Critical path**: Resolving the displacement field profile question (Section 7) determines everything else.
