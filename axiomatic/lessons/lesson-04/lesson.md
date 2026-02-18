# Lesson 4: The Mode Vacuum — Standard QFT's Ground State

## Overview

The mode vacuum is the ground state of standard quantum field theory. It is constructed by applying the formalism of Fock space: start with an "empty" state $|0\rangle$, define creation and annihilation operators $a^\dagger_k$ and $a_k$ for each momentum mode $k$, and declare the vacuum to be the state annihilated by all $a_k$:

$$
a_k |0\rangle_{\text{mode}} = 0 \quad \text{for all } k
$$

This state is mathematically elegant. It is Lorentz-invariant — the same in all inertial frames. It is the unique state invariant under all spatial and temporal translations. It is maximally entangled across all spatial bipartitions. And it is the foundation of every QFT textbook.

But it has a fatal flaw: its energy density is infinite.

This lesson constructs the mode vacuum step by step, computes its energy density explicitly, and demonstrates the divergence. We will see that the energy density scales as $\rho_{\text{mode}} \sim a^{-4}$, where $a$ is the lattice spacing. As $a \to 0$ (the continuum limit), $\rho \to \infty$. The mode vacuum does not satisfy axiom A1 (Refinability). It does not have a well-defined continuum limit.

By the end of this lesson, you will understand why the mode vacuum is not the physical vacuum, and why an alternative — the coherent vacuum — is necessary.

## 4.1 Fock Space: The Framework of Standard QFT

In quantum mechanics, the state space is a Hilbert space $\mathcal{H}$ of normalizable wavefunctions. In quantum field theory, the state space is **Fock space** — a Hilbert space built from the vacuum by applying creation operators.

### 4.1.1 The Vacuum State

We start with a single state $|0\rangle$, called the **vacuum**. This is not "empty space" in the classical sense — it is the *lowest-energy state* of the quantum field. Think of it as the quantum analog of a spring at rest: it has irreducible zero-point energy, but no excitations above that baseline.

The vacuum is normalized:

$$
\langle 0 | 0 \rangle = 1
$$

**[ESTABLISHED]**. This is the starting point of Fock space.

### 4.1.2 Creation and Annihilation Operators

For each momentum mode $\mathbf{k}$, we define two operators:

- **Annihilation operator** $a_{\mathbf{k}}$: lowers the occupation number of mode $\mathbf{k}$ by 1.
- **Creation operator** $a^\dagger_{\mathbf{k}}$: raises the occupation number of mode $\mathbf{k}$ by 1.

These operators satisfy the canonical commutation relations:

$$
[a_{\mathbf{k}}, a^\dagger_{\mathbf{k}'}] = \delta_{\mathbf{k}\mathbf{k}'}
$$

$$
[a_{\mathbf{k}}, a_{\mathbf{k}'}] = 0, \quad [a^\dagger_{\mathbf{k}}, a^\dagger_{\mathbf{k}'}] = 0
$$

**[ESTABLISHED]**. These are the fundamental commutation relations for a free bosonic field. They follow from the canonical quantization of the field $\phi(x)$ and its conjugate momentum $\pi(x)$.

### 4.1.3 The Mode Vacuum Definition

The mode vacuum $|0\rangle_{\text{mode}}$ is defined by the requirement that it is annihilated by all annihilation operators:

$$
a_{\mathbf{k}} |0\rangle_{\text{mode}} = 0 \quad \text{for all } \mathbf{k}
$$

This is the lowest-energy state of the field. You cannot remove any quanta — the state is already at the bottom of the ladder. **[ESTABLISHED]**.

### 4.1.4 Excited States

Higher-energy states are constructed by applying creation operators to the vacuum:

- **One-particle states:** $|\mathbf{k}\rangle = a^\dagger_{\mathbf{k}} |0\rangle$ (one quantum in mode $\mathbf{k}$)
- **Two-particle states:** $|\mathbf{k}_1, \mathbf{k}_2\rangle = a^\dagger_{\mathbf{k}_1} a^\dagger_{\mathbf{k}_2} |0\rangle$ (one quantum in each of modes $\mathbf{k}_1$, $\mathbf{k}_2$)
- **General $n$-particle states:** $a^\dagger_{\mathbf{k}_1} \cdots a^\dagger_{\mathbf{k}_n} |0\rangle$

The full Fock space is the direct sum of all $n$-particle sectors:

$$
\mathcal{F} = \bigoplus_{n=0}^{\infty} \mathcal{H}_n
$$

where $\mathcal{H}_0 = \text{span}\{|0\rangle\}$ is the vacuum sector, $\mathcal{H}_1$ is the one-particle sector, etc.

**[ESTABLISHED]**. This is the standard construction of Fock space for a free field.

---

## 4.2 The Field Decomposition

A scalar quantum field $\hat{\phi}(x)$ is an operator-valued function on spacetime. In the momentum basis, it decomposes into a sum over modes:

$$
\hat{\phi}(x) = \int \frac{d^3k}{(2\pi)^3} \frac{1}{\sqrt{2\omega_k V}} \left[ a_{\mathbf{k}} e^{i\mathbf{k} \cdot \mathbf{x}} + a^\dagger_{\mathbf{k}} e^{-i\mathbf{k} \cdot \mathbf{x}} \right]
$$

where:

- $\omega_k = \sqrt{|\mathbf{k}|^2 c^2 + m^2 c^4/\hbar^2}$ is the energy of a quantum with momentum $\hbar \mathbf{k}$.
- $V$ is the volume of the box (we work in a finite box and take $V \to \infty$ later).
- The integral is over all allowed momentum modes $\mathbf{k}$.

**[ESTABLISHED]**. This is the mode decomposition of a free scalar field. Each mode $\mathbf{k}$ acts like an independent harmonic oscillator with frequency $\omega_k$.

### 4.2.1 The Harmonic Oscillator Analogy

For each mode $\mathbf{k}$, the field behaves like a quantum harmonic oscillator with:

- **Frequency:** $\omega_k = \sqrt{|\mathbf{k}|^2 c^2 + m^2 c^4/\hbar^2}$
- **Ground state energy:** $E_{0,k} = \frac{1}{2} \hbar \omega_k$
- **Annihilation operator:** $a_{\mathbf{k}}$ (lowers energy by $\hbar \omega_k$)
- **Creation operator:** $a^\dagger_{\mathbf{k}}$ (raises energy by $\hbar \omega_k$)

The total Hamiltonian is the sum over all modes:

$$
H = \sum_{\mathbf{k}} \hbar \omega_k \left( a^\dagger_{\mathbf{k}} a_{\mathbf{k}} + \frac{1}{2} \right)
$$

**[ESTABLISHED]**. This follows from canonical quantization of the free field.

The vacuum energy is the sum of zero-point energies:

$$
E_0^{\text{mode}} = \sum_{\mathbf{k}} \frac{1}{2} \hbar \omega_k
$$

For finite $V$ and a finite cutoff on $|\mathbf{k}|$, this is finite. But in the continuum limit ($V \to \infty$ and cutoff $\Lambda \to \infty$), it diverges.

---

## 4.3 Energy Density of the Mode Vacuum

Let us compute the energy density explicitly. We work in a cubic box of volume $V = L^3$ with periodic boundary conditions. The allowed momentum modes are:

$$
\mathbf{k} = \frac{2\pi}{L}(n_x, n_y, n_z), \quad n_x, n_y, n_z \in \mathbb{Z}
$$

The sum over modes becomes:

$$
E_0^{\text{mode}} = \sum_{\mathbf{k}} \frac{1}{2} \hbar \omega_k = V \sum_{\mathbf{k}} \frac{1}{2V} \hbar \omega_k
$$

In the limit $V \to \infty$, the sum becomes an integral:

$$
\frac{1}{V} \sum_{\mathbf{k}} \to \int \frac{d^3k}{(2\pi)^3}
$$

Thus the energy density is:

$$
\rho_{\text{mode}} = \frac{E_0^{\text{mode}}}{V} = \int \frac{d^3k}{(2\pi)^3} \frac{1}{2} \hbar \omega_k
$$

**[ESTABLISHED]**. This is the standard expression for the energy density of the mode vacuum.

### 4.3.1 The Massless Case

For a massless field ($m = 0$), the dispersion relation is $\omega_k = c|\mathbf{k}|$. The energy density becomes:

$$
\rho_{\text{mode}} = \int \frac{d^3k}{(2\pi)^3} \frac{1}{2} \hbar c |\mathbf{k}|
$$

Switch to spherical coordinates: $d^3k = 4\pi k^2 dk$, where $k = |\mathbf{k}|$. Then:

$$
\rho_{\text{mode}} = \int_0^{\infty} \frac{4\pi k^2 dk}{(2\pi)^3} \frac{1}{2} \hbar c k = \frac{\hbar c}{4\pi^2} \int_0^{\infty} k^3 dk
$$

This integral diverges. The integrand grows as $k^3$, so the integral is quartically divergent. **[PROVEN]**.

### 4.3.2 Introducing a UV Cutoff

To regulate the divergence, we impose an ultraviolet (UV) cutoff: we integrate only up to $k_{\text{max}} = \pi/a$, where $a$ is the lattice spacing. (On a lattice, the shortest wavelength is $\lambda_{\text{min}} = 2a$, corresponding to $k_{\text{max}} = 2\pi/\lambda_{\text{min}} = \pi/a$.)

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{4\pi^2} \int_0^{\pi/a} k^3 dk = \frac{\hbar c}{4\pi^2} \cdot \frac{1}{4} \left(\frac{\pi}{a}\right)^4
$$

Simplifying:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \left(\frac{\pi}{a}\right)^4
$$

**[PROVEN]**. This is an exact result for a massless field on a lattice with spacing $a$.

As $a \to 0$, $\rho_{\text{mode}} \sim a^{-4} \to \infty$. The energy density diverges quartically. The mode vacuum does not satisfy axiom A1 (Refinability).

### 4.3.3 The Massive Case

For a massive field ($m > 0$), the dispersion relation is $\omega_k = c\sqrt{k^2 + (mc/\hbar)^2}$. The integral becomes:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{4\pi^2} \int_0^{\pi/a} k^2 \sqrt{k^2 + (mc/\hbar)^2} \, dk
$$

At high $k$ (where $k \gg mc/\hbar$), the integrand behaves as $k^3$, so the divergence is still quartic. At low $k$ (where $k \ll mc/\hbar$), the integrand behaves as $k^2 \cdot (mc/\hbar) = (mc/\hbar) k^2$, which is convergent but still grows with the cutoff.

The full result (evaluating the integral) is:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \left(\frac{\pi}{a}\right)^4 \left[ 1 + 2(ma)^2 + O((ma)^4) \right]
$$

**[PROVEN]**. The leading divergence is the same as the massless case: $\sim a^{-4}$. The mass term gives a subleading correction.

### 4.3.4 Numerical Estimate

Let us plug in numbers. Set $a = \ell_{\text{Planck}} \approx 1.6 \times 10^{-35}$ m (the Planck length, the smallest meaningful length scale). For a massless field:

$$
\rho_{\text{mode}}(\ell_{\text{Planck}}) = \frac{\hbar c}{16\pi^2} \left(\frac{\pi}{\ell_{\text{Planck}}}\right)^4
$$

Using $\hbar c \approx 2 \times 10^{-26}$ J·m and $\ell_{\text{Planck}} \approx 1.6 \times 10^{-35}$ m:

$$
\rho_{\text{mode}} \sim 10^{113} \, \text{J/m}^3
$$

**[PROVEN]**. This is the famous "worst prediction in physics."

The observed dark energy density is $\rho_{\text{obs}} \approx 6 \times 10^{-10}$ J/m$^3$. The ratio is:

$$
\frac{\rho_{\text{mode}}}{\rho_{\text{obs}}} \sim 10^{123}
$$

This is the cosmological constant problem — or, more precisely, this is what you get if you assume the mode vacuum is the physical vacuum.

---

## 4.4 Properties of the Mode Vacuum

Despite its infinite energy density, the mode vacuum has several elegant mathematical properties. Let us examine them.

### 4.4.1 Lorentz Invariance

The mode vacuum is invariant under Lorentz transformations. In any inertial frame, the vacuum is defined by $a_{\mathbf{k}} |0\rangle = 0$ for all $\mathbf{k}$. A Lorentz boost changes the momentum modes (a mode $\mathbf{k}$ in one frame becomes a different mode $\mathbf{k}'$ in the boosted frame), but the *definition* of the vacuum remains the same: annihilate all modes.

Formally, if $U(\Lambda)$ is the unitary operator representing a Lorentz transformation $\Lambda$, then:

$$
U(\Lambda) |0\rangle_{\text{mode}} = |0\rangle_{\text{mode}}
$$

**[ESTABLISHED]**. The mode vacuum is the unique Lorentz-invariant state in Fock space.

This is one of the reasons the mode vacuum is so attractive: it respects the fundamental symmetry of special relativity.

### 4.4.2 Maximal Entanglement

Partition space into two regions $A$ and $B$. The reduced density matrix of region $A$ is:

$$
\rho_A = \text{Tr}_B(|0\rangle_{\text{mode}} \langle 0|)
$$

The entanglement entropy is:

$$
S_A = -\text{Tr}(\rho_A \log \rho_A)
$$

For the mode vacuum, $S_A$ diverges with the cutoff:

$$
S_A \sim c_1 \cdot \frac{A}{a^2}
$$

where $A$ is the area of the boundary between regions $A$ and $B$, and $c_1$ is a numerical constant. This is the **area law** for entanglement entropy. **[ESTABLISHED]**.

The divergence $S_A \sim a^{-2}$ is a consequence of short-distance correlations across the boundary. As $a \to 0$, the entanglement entropy grows without bound. The mode vacuum is maximally entangled across all spatial bipartitions.

### 4.4.3 Invariance Under Translations

The mode vacuum is invariant under spatial translations. If $\hat{T}(\mathbf{d})$ is the operator that translates the field by $\mathbf{d}$, then:

$$
\hat{T}(\mathbf{d}) |0\rangle_{\text{mode}} = |0\rangle_{\text{mode}}
$$

Similarly, it is invariant under time translations (it is a stationary state — the ground state of the Hamiltonian). **[ESTABLISHED]**.

This is again a mathematical virtue: the vacuum respects all the symmetries of spacetime.

---

## 4.5 Renormalization: The Standard Fix

In standard QFT, the infinite vacuum energy is "fixed" by renormalization. The idea is simple: redefine the zero of energy so that the vacuum has zero energy by fiat.

Define the **normal-ordered Hamiltonian**:

$$
{:}H{:} = H - \langle 0 | H | 0 \rangle = \sum_{\mathbf{k}} \hbar \omega_k \, a^\dagger_{\mathbf{k}} a_{\mathbf{k}}
$$

This is the Hamiltonian with the zero-point energy subtracted away. The vacuum now has zero energy:

$$
\langle 0 | {:}H{:} | 0 \rangle = 0
$$

**[ESTABLISHED]**. Normal ordering is the standard prescription in QFT.

But here's the problem: **normal ordering does not eliminate the divergence; it hides it**. The vacuum energy is still infinite — we've just agreed to call it zero. If we couple the field to gravity (where absolute energy matters, not just energy differences), the infinite vacuum energy reappears as the cosmological constant. And we have no explanation for why it should be small.

Renormalization works brilliantly for computing scattering amplitudes and particle interactions, where only energy *differences* matter. But it does not solve the vacuum energy problem. It sweeps it under the rug.

---

## 4.6 Why the Mode Vacuum Fails Axiom A1

Let us be explicit. Axiom A1 (Refinability) states:

$$
\lim_{a \to 0} \langle O \rangle_a = \text{finite}
$$

for all physical observables $O$. We have computed:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \left(\frac{\pi}{a}\right)^4
$$

As $a \to 0$:

$$
\lim_{a \to 0} \rho_{\text{mode}}(a) = \infty
$$

The mode vacuum *fails* A1. The energy density does not converge as we refine the lattice. **[PROVEN]**.

Similarly, the entanglement entropy diverges:

$$
\lim_{a \to 0} S_A(a) = \infty
$$

The mode vacuum does not have a well-defined continuum limit for these observables.

### 4.6.1 But Renormalized Quantities Converge

Someone might object: "Wait, if we normal-order the Hamiltonian, the energy density is zero, which is finite. Doesn't that satisfy A1?"

No. Axiom A1 demands that *physical* observables converge, not subtracted observables. Normal ordering is a mathematical trick — it redefines the zero of energy by subtracting $\langle 0 | H | 0 \rangle$. But that subtracted quantity is itself divergent. You are subtracting infinity to get zero, which is not the same as having a finite result before subtraction.

Axiom F (Finiteness) makes this explicit: observables must be finite *without regularization or renormalization*. The mode vacuum fails F as well.

---

## 4.7 Summary of Key Results

| Property | Mode Vacuum Result | Status |
|----------|-------------------|--------|
| Definition | $a_{\mathbf{k}} \|0\rangle = 0$ for all $\mathbf{k}$ | [ESTABLISHED] |
| Lorentz invariance | $U(\Lambda) \|0\rangle = \|0\rangle$ | [ESTABLISHED] |
| Energy density (massless) | $\rho(a) = \frac{\hbar c}{16\pi^2} \left(\frac{\pi}{a}\right)^4$ | [PROVEN] |
| Divergence | $\rho(a) \sim a^{-4} \to \infty$ as $a \to 0$ | [PROVEN] |
| Entanglement entropy | $S_A \sim \frac{A}{a^2} \to \infty$ | [ESTABLISHED] |
| Satisfies axioms P, Q, M', L | Yes | [ESTABLISHED] |
| Satisfies axiom A1 | No — $\rho$ diverges | [PROVEN] |
| Satisfies axiom F | No — $\rho = \infty$ | [PROVEN] |

---

## 4.8 What This Means

The mode vacuum is mathematically elegant. It is Lorentz-invariant, translation-invariant, and the unique ground state of the free-field Hamiltonian. It is the foundation of every QFT textbook and the starting point for perturbative calculations.

But it has infinite energy density. It does not satisfy axiom A1 (the continuum limit does not exist for $\rho$) or axiom F (observables are not finite without renormalization). If we demand that the physical vacuum satisfy all seven axioms, then the mode vacuum is not the physical vacuum.

This is not a condemnation of the mode vacuum as a computational tool. For calculating scattering amplitudes, where only energy differences matter, the mode vacuum and its associated Fock space are extraordinarily effective. But for questions about the *absolute* energy density of the vacuum — the cosmological constant — the mode vacuum gives a divergent, unphysical answer.

The axiomatic framework proposes that there exists a different vacuum state — one that satisfies all seven axioms, including A1 and F. That state is the **coherent vacuum**, constructed in Lesson 5.

---

## 4.9 Looking Ahead

In Lesson 5, we will construct the coherent vacuum. Instead of defining the vacuum by $a_{\mathbf{k}} |0\rangle = 0$, we will define it as a product of coherent states, one for each mode $\mathbf{k}$. Each coherent state will be the special state $|\alpha = 1/\sqrt{2}\rangle$ from Lesson 2 — the state with energy $\hbar\omega$ and maximal duality symmetry.

We will compute the energy density of the coherent vacuum and show that:

$$
\lim_{a \to 0} \rho_{\text{coherent}}(a) = \text{finite}
$$

The coherent vacuum satisfies axiom A1. It has a well-defined continuum limit. And it produces a finite prediction for the vacuum energy density, without any subtraction or renormalization.

The mode vacuum is the wrong vacuum. The coherent vacuum is the right one. Let's see why.
