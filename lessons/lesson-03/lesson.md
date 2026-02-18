# Lesson 3: Quantum Fields and the Mode Vacuum

## Overview

Quantum field theory promotes the oscillator story of Lessons 1 and 2 to infinite dimensions. Every momentum mode $\mathbf{k}$ of a free field gets its own oscillator, and the ground state of the entire field -- the **mode vacuum** $|0\rangle$ -- is the product of all individual oscillator ground states. This state has definite momentum-space properties (zero particles in every mode) but is maximally nonlocal in position space. Its energy density, computed naively, diverges quartically with the ultraviolet cutoff, producing the famous $10^{123}$ discrepancy with observation.

Everything in this lesson is **[PROVEN]** standard quantum field theory, except where explicitly noted.

## 3.1 From One Oscillator to a Field

A classical real scalar field $\phi(\mathbf{x}, t)$ of mass $m$ obeys the Klein-Gordon equation:

$$
(\partial_\mu\partial^\mu + m^2)\phi = 0
$$

(in natural units $c = \hbar = 1$). The general solution is a superposition of plane waves. We decompose:

$$
\phi(\mathbf{x}, t) = \int \frac{d^3k}{(2\pi)^3}\,\frac{1}{\sqrt{2\omega_\mathbf{k}}}\left(a_\mathbf{k}\,e^{i\mathbf{k}\cdot\mathbf{x} - i\omega_\mathbf{k}t} + a_\mathbf{k}^*\,e^{-i\mathbf{k}\cdot\mathbf{x} + i\omega_\mathbf{k}t}\right)
$$

where

$$
\omega_\mathbf{k} = \sqrt{|\mathbf{k}|^2 + m^2}
$$

is the dispersion relation. Each mode $\mathbf{k}$ oscillates independently at its own frequency $\omega_\mathbf{k}$. Classically, the Fourier coefficients $a_\mathbf{k}$ are complex numbers. **[PROVEN]**

## 3.2 Quantization: One Oscillator Per Mode

Upon quantization, the coefficients become operators:

$$
a_\mathbf{k} \to \hat{a}_\mathbf{k}, \qquad a_\mathbf{k}^* \to \hat{a}_\mathbf{k}^\dagger
$$

with commutation relations:

$$
[\hat{a}_\mathbf{k}, \hat{a}_{\mathbf{k}'}^\dagger] = (2\pi)^3\,\delta^{(3)}(\mathbf{k} - \mathbf{k}')
$$

$$
[\hat{a}_\mathbf{k}, \hat{a}_{\mathbf{k}'}] = 0, \qquad [\hat{a}_\mathbf{k}^\dagger, \hat{a}_{\mathbf{k}'}^\dagger] = 0
$$

Each mode $\mathbf{k}$ is an independent quantum harmonic oscillator with frequency $\omega_\mathbf{k}$. The field has become an infinite collection of oscillators. **[PROVEN]**

The quantum field operator is:

$$
\hat{\phi}(\mathbf{x}, t) = \int \frac{d^3k}{(2\pi)^3}\,\frac{1}{\sqrt{2\omega_\mathbf{k}}}\left(\hat{a}_\mathbf{k}\,e^{i\mathbf{k}\cdot\mathbf{x} - i\omega_\mathbf{k}t} + \hat{a}_\mathbf{k}^\dagger\,e^{-i\mathbf{k}\cdot\mathbf{x} + i\omega_\mathbf{k}t}\right)
$$

## 3.3 The Mode Vacuum

The mode vacuum $|0\rangle$ is defined as the state annihilated by every annihilation operator:

$$
\hat{a}_\mathbf{k}|0\rangle = 0 \qquad \text{for all } \mathbf{k}
$$

It is the product of the ground states of all individual mode oscillators:

$$
|0\rangle = \bigotimes_\mathbf{k} |0_\mathbf{k}\rangle
$$

In the mode vacuum, every oscillator is in its ground state. There are zero particles in every mode. The particle number is definite: $\hat{n}_\mathbf{k}|0\rangle = 0$ for all $\mathbf{k}$. **[PROVEN]**

## 3.4 Properties of the Mode Vacuum

### Definite in Momentum Space

The mode vacuum has exact properties in momentum space:
- Zero particles in every mode $\mathbf{k}$
- Definite number ($n_\mathbf{k} = 0$) in every mode
- No fluctuations in particle number per mode

This is its defining feature: it is "empty" mode by mode. **[PROVEN]**

### Indefinite in Position Space

The field amplitude $\hat{\phi}(\mathbf{x})$ at any spatial point is uncertain:

$$
\langle 0|\hat{\phi}(\mathbf{x})|0\rangle = 0
$$

$$
\langle 0|\hat{\phi}(\mathbf{x})^2|0\rangle = \int \frac{d^3k}{(2\pi)^3}\,\frac{1}{2\omega_\mathbf{k}} \neq 0
$$

The field has zero mean but nonzero variance. It fluctuates at every point. The mode vacuum has definite particle number (zero) in every momentum mode, but the field value at a given point in space is uncertain. This is the field-theoretic analog of the position-momentum complementarity familiar from single-particle quantum mechanics. **[PROVEN]**

### Nonlocal Entanglement: The Reeh-Schlieder Theorem

The mode vacuum is highly entangled across spatial regions. The **Reeh-Schlieder theorem** states:

> For any bounded open region $\mathcal{O}$ of spacetime, the set of states $\{A|0\rangle : A \in \mathcal{A}(\mathcal{O})\}$ (where $\mathcal{A}(\mathcal{O})$ is the algebra of observables localized in $\mathcal{O}$) is dense in the full Hilbert space.

In plain language: by acting on the vacuum with operators localized in any bounded region, you can approximate any state in the entire Hilbert space to arbitrary precision. This is only possible because the vacuum is entangled with everything else. **[PROVEN]**

Consequences:
- The vacuum entanglement between any two spacelike-separated regions is nonzero
- The reduced density matrix of any bounded region has full rank
- The entanglement entropy of a region scales with its boundary area (area law)
- No bounded region is in a pure state when the rest of the field is traced out

The Reeh-Schlieder theorem applies to any state satisfying the **spectrum condition** (energy-momentum support in the forward light cone). The mode vacuum satisfies this condition by construction. **[PROVEN]**

### Poincare Invariance

The mode vacuum is the unique state invariant under the Poincare group (translations, rotations, and Lorentz boosts). Every inertial observer sees the same vacuum. This is a consequence of the uniqueness theorem for the vacuum representation of the Poincare group. **[PROVEN]**

## 3.5 The Vacuum Energy Density

The Hamiltonian of the free scalar field is:

$$
H = \int \frac{d^3k}{(2\pi)^3}\,\hbar\omega_\mathbf{k}\left(\hat{a}_\mathbf{k}^\dagger\hat{a}_\mathbf{k} + \frac{1}{2}\right)
$$

The vacuum expectation value is:

$$
\langle 0|H|0\rangle = \int \frac{d^3k}{(2\pi)^3}\,\frac{1}{2}\hbar\omega_\mathbf{k} \cdot V
$$

where $V$ is the spatial volume (from the delta function at zero). The vacuum energy density is:

$$
\rho_0 = \frac{1}{2}\int \frac{d^3k}{(2\pi)^3}\,\hbar\omega_\mathbf{k}
$$

## 3.6 The Divergence

The integral diverges. Imposing a hard UV cutoff at $|\mathbf{k}| = \Lambda$:

$$
\rho_0 = \frac{1}{2}\int_0^{\Lambda} \frac{4\pi k^2\,dk}{(2\pi)^3}\,\omega_k
$$

For $\Lambda \gg m$ (the massless limit dominates), with $\omega_k \approx k$ (in natural units):

$$
\rho_0 \approx \frac{1}{2}\cdot\frac{4\pi}{(2\pi)^3}\int_0^{\Lambda} k^3\,dk = \frac{\Lambda^4}{16\pi^2}
$$

This is a quartically divergent integral. The energy density grows as the fourth power of the cutoff. **[PROVEN]**

More carefully, for a massive field:

$$
\rho_0 = \frac{1}{4\pi^2}\int_0^{\Lambda} k^2\sqrt{k^2 + m^2}\,dk
$$

$$
= \frac{\Lambda^4}{16\pi^2}\left[1 + O(m^2/\Lambda^2)\right]
$$

The mass correction is subdominant for $\Lambda \gg m$. **[PROVEN]**

## 3.7 The "Worst Prediction in Physics"

Setting $\Lambda$ to the Planck scale $M_{\text{Pl}} = \sqrt{\hbar c/G} \approx 1.22 \times 10^{19}$ GeV:

$$
\rho_0 \sim \frac{M_{\text{Pl}}^4}{16\pi^2} \sim 10^{113}\;\text{J/m}^3
$$

The observed dark energy density is:

$$
\rho_\Lambda^{\text{obs}} \sim 5.4 \times 10^{-10}\;\text{J/m}^3
$$

The ratio:

$$
\frac{\rho_0}{\rho_\Lambda^{\text{obs}}} \sim 10^{123}
$$

This is the cosmological constant problem as traditionally stated. The zero-point energy of quantum fields, computed with a Planck-scale cutoff, exceeds the observed vacuum energy by 123 orders of magnitude. **[PROVEN]** in the sense that both the calculation and the observation are correct. What is not proven is that this ratio represents a genuine physical discrepancy -- that depends on whether the mode vacuum energy density is the right quantity to compare with gravity.

## 3.8 Normal Ordering

The standard response in particle physics is **normal ordering**: redefine the Hamiltonian as

$$
:H: = H - \langle 0|H|0\rangle
$$

so that $\langle 0|:H:|0\rangle = 0$ by construction. This amounts to putting all creation operators to the left of all annihilation operators, eliminating the zero-point energy.

In particle physics, where we measure energy differences, this works perfectly. The Lamb shift, the Casimir effect, and particle scattering amplitudes all involve differences in vacuum energy, not absolute values.

But in general relativity, all energy gravitates. Einstein's equation is:

$$
G_{\mu\nu} = 8\pi G\,\langle T_{\mu\nu}\rangle
$$

There is no freedom to choose a zero of energy. Subtracting $\langle 0|T_{\mu\nu}|0\rangle$ by hand is not a physical operation -- it is a statement that we do not know the correct absolute energy of the vacuum. **[FRAMEWORK]** -- the status of normal ordering in the presence of gravity is not settled.

## 3.9 The Scale of the Problem

It is worth emphasizing that the cosmological constant problem is not merely about the Planck scale. Even with more conservative cutoffs, the discrepancy is enormous:

- **Planck scale** ($\Lambda \sim 10^{19}$ GeV): $\rho_0/\rho_\Lambda^{\text{obs}} \sim 10^{123}$
- **Electroweak scale** ($\Lambda \sim 246$ GeV): $\rho_0/\rho_\Lambda^{\text{obs}} \sim 10^{55}$
- **QCD scale** ($\Lambda \sim 200$ MeV): $\rho_0/\rho_\Lambda^{\text{obs}} \sim 10^{41}$

The problem persists at every energy scale. Even if we trust quantum field theory only up to 200 MeV -- below the scale of nuclear physics -- the predicted vacuum energy is still 41 orders of magnitude too large. This makes it clear that the issue is not about exotic Planck-scale physics but about a fundamental aspect of how vacuum energy is computed. **[PROVEN]**

## 3.10 What the Mode Vacuum Is and Is Not

The mode vacuum is:
- The unique Poincare-invariant state of the free field **[PROVEN]**
- A state with definite particle number (zero) in every mode **[PROVEN]**
- Maximally entangled across spatial regions **[PROVEN]**
- The correct vacuum for particle physics calculations **[PROVEN]**

The mode vacuum gives:
- A divergent energy density requiring regularization **[PROVEN]**
- A $10^{123}$ discrepancy with observation when cutoff at the Planck scale **[PROVEN]**
- No definite field amplitude at any point in space **[PROVEN]**

Whether the mode vacuum is the right state for computing the gravitational vacuum energy is a question we will address in Lessons 4 and 5.

## Summary of Key Results

| Result | Status |
|--------|--------|
| Field decomposition into oscillator modes | [PROVEN] |
| $[\hat{a}_\mathbf{k}, \hat{a}_{\mathbf{k}'}^\dagger] = (2\pi)^3\delta^{(3)}(\mathbf{k} - \mathbf{k}')$ | [PROVEN] |
| Mode vacuum: $\hat{a}_\mathbf{k}\|0\rangle = 0$ for all $\mathbf{k}$ | [PROVEN] |
| Vacuum energy density: $\rho_0 \sim \Lambda^4/(16\pi^2)$ | [PROVEN] |
| Planck cutoff gives $\rho_0 \sim 10^{113}$ J/m$^3$ | [PROVEN] |
| Reeh-Schlieder: vacuum is nonlocally entangled | [PROVEN] |
| Mode vacuum is unique Poincare-invariant state | [PROVEN] |
| Normal ordering is unsatisfying in the presence of gravity | [FRAMEWORK] |

## Looking Ahead

The mode vacuum $|0\rangle$ is the standard vacuum of quantum field theory -- and it works magnificently for particle physics. But its energy density diverges, it has no well-defined local energy, and when compared to gravitational observations it fails by 123 orders of magnitude.

Lesson 4 introduces a different construction: the **cell vacuum** $|\Omega\rangle$, built by tiling space into Compton-wavelength cells and placing each in a coherent state with $|\alpha|^2 = 1/2$. This state has definite position-space energy (one $mc^2$ per cell), is a product state with no entanglement, and gives a finite energy density $\rho = m^4c^5/\hbar^3$ with no cutoff needed.

The stage is set for the central question of this course: when gravity asks "what is the energy density of the vacuum?", which vacuum should answer?
