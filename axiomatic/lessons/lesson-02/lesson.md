# Lesson 2: Quantum States and Hilbert Spaces

## Overview

To state axioms for quantum vacuum selection, we need a precise mathematical language. That language is the theory of Hilbert spaces -- the framework in which all quantum mechanics is formulated. This lesson develops the essential concepts: states as vectors, observables as operators, density matrices for mixed states, tensor products for composite systems, and the Born rule for extracting predictions.

Every result in this lesson is standard quantum mechanics, established through decades of theoretical development and experimental confirmation. All claims are **[ESTABLISHED]** unless otherwise noted.

## 2.1 What Is a Hilbert Space?

A **Hilbert space** is a vector space with three additional structures:

1. **Inner product:** A map $\langle \cdot | \cdot \rangle : \mathcal{H} \times \mathcal{H} \to \mathbb{C}$ that is:
   - Linear in the second argument: $\langle \psi | a\phi_1 + b\phi_2 \rangle = a\langle \psi|\phi_1\rangle + b\langle \psi|\phi_2\rangle$
   - Antilinear in the first argument: $\langle a\psi_1 + b\psi_2 | \phi \rangle = a^*\langle \psi_1|\phi\rangle + b^*\langle \psi_2|\phi\rangle$
   - Positive-definite: $\langle \psi|\psi\rangle > 0$ for all $|\psi\rangle \neq 0$
   - Hermitian: $\langle \psi|\phi\rangle = \langle \phi|\psi\rangle^*$

2. **Norm:** Induced by the inner product: $\||\psi\rangle\| = \sqrt{\langle\psi|\psi\rangle}$

3. **Completeness:** Every Cauchy sequence of vectors converges to a vector in the space.

**[ESTABLISHED]** -- This is the standard definition of a Hilbert space in functional analysis.

Examples:

- **Finite-dimensional:** $\mathbb{C}^n$ with the standard dot product.
- **Infinite-dimensional:** $L^2(\mathbb{R})$, the space of square-integrable functions $\psi(x)$ with inner product $\langle \phi|\psi\rangle = \int \phi(x)^*\psi(x)\,dx$.

In quantum mechanics, the state of a system is represented by a vector (or "ray") in a Hilbert space. The dimensionality of the space depends on the system: a two-level atom lives in $\mathbb{C}^2$, a particle on a line lives in $L^2(\mathbb{R})$, a quantum field lives in an infinite-dimensional Fock space (to be introduced in Lesson 3).

## 2.2 Quantum States as Vectors

The first axiom of quantum mechanics is:

> **Axiom (States):** The state of a quantum system is represented by a unit vector $|\psi\rangle$ in a Hilbert space $\mathcal{H}$, satisfying $\langle\psi|\psi\rangle = 1$.

**[ESTABLISHED]**

The normalization condition $\langle\psi|\psi\rangle = 1$ ensures that probabilities sum to 1. Two vectors $|\psi\rangle$ and $e^{i\theta}|\psi\rangle$ (differing only by a global phase) represent the same physical state. The physical content is in the **ray** (the equivalence class of vectors differing by a phase), not the vector itself.

**Superposition principle:** If $|\psi_1\rangle$ and $|\psi_2\rangle$ are valid states, then so is any normalized linear combination:

$$
|\psi\rangle = c_1|\psi_1\rangle + c_2|\psi_2\rangle, \quad |c_1|^2 + |c_2|^2 = 1
$$

**[ESTABLISHED]** -- This is the defining feature of quantum mechanics, distinguishing it from classical probability theory.

## 2.3 Observables as Hermitian Operators

The second axiom of quantum mechanics is:

> **Axiom (Observables):** Every measurable quantity (position, momentum, energy, etc.) corresponds to a Hermitian operator $\hat{O}$ acting on $\mathcal{H}$.

An operator $\hat{O}$ is **Hermitian** (or self-adjoint) if:

$$
\langle \phi | \hat{O} \psi \rangle = \langle \hat{O}\phi | \psi \rangle
$$

for all $|\psi\rangle, |\phi\rangle \in \mathcal{H}$. Equivalently, $\hat{O}^\dagger = \hat{O}$, where the adjoint $\hat{O}^\dagger$ satisfies $\langle \phi|\hat{O}^\dagger\psi\rangle = \langle \hat{O}\phi|\psi\rangle$.

**[ESTABLISHED]**

**Why Hermitian?** Because Hermitian operators have real eigenvalues, and measurement outcomes are real numbers. A non-Hermitian operator would predict complex measurement results, which is physically nonsensical.

## 2.4 The Spectral Theorem

The spectral theorem is the mathematical foundation for quantum measurement.

> **Spectral Theorem:** Every Hermitian operator $\hat{O}$ on a Hilbert space has a complete orthonormal set of eigenvectors $\{|o_i\rangle\}$ with real eigenvalues $\{o_i\}$:
> $$\hat{O}|o_i\rangle = o_i|o_i\rangle, \quad \langle o_i|o_j\rangle = \delta_{ij}$$

**[PROVEN]** -- This is a theorem of functional analysis.

Any state can be expanded in this eigenbasis:

$$
|\psi\rangle = \sum_i c_i|o_i\rangle, \quad c_i = \langle o_i|\psi\rangle
$$

The operator can be written in spectral form:

$$
\hat{O} = \sum_i o_i |o_i\rangle\langle o_i|
$$

This decomposition is central to understanding measurement.

## 2.5 The Born Rule

The third axiom of quantum mechanics connects the mathematical formalism to experimental predictions.

> **Axiom (Born Rule):** If a system is in state $|\psi\rangle$ and an observable $\hat{O}$ with eigenstates $\{|o_i\rangle\}$ and eigenvalues $\{o_i\}$ is measured, the probability of obtaining outcome $o_i$ is:
> $$P(o_i) = |\langle o_i|\psi\rangle|^2$$

**[ESTABLISHED]**

After measurement, the state "collapses" to $|o_i\rangle$ (in the standard Copenhagen interpretation). The expectation value of $\hat{O}$ in state $|\psi\rangle$ is:

$$
\langle \hat{O} \rangle = \langle \psi|\hat{O}|\psi\rangle = \sum_i o_i |\langle o_i|\psi\rangle|^2
$$

The Born rule has been confirmed in countless experiments, from double-slit interference to quantum computing. It is one of the most precisely tested predictions in all of physics.

## 2.6 Time Evolution: The Schrödinger Equation

The fourth axiom governs dynamics.

> **Axiom (Time Evolution):** Between measurements, the state evolves unitarily according to the Schrödinger equation:
> $$i\hbar\frac{d}{dt}|\psi(t)\rangle = \hat{H}|\psi(t)\rangle$$
> where $\hat{H}$ is the Hamiltonian (energy operator).

**[ESTABLISHED]**

The formal solution is:

$$
|\psi(t)\rangle = e^{-i\hat{H}t/\hbar}|\psi(0)\rangle
$$

The operator $\hat{U}(t) = e^{-i\hat{H}t/\hbar}$ is **unitary**: $\hat{U}^\dagger\hat{U} = \hat{U}\hat{U}^\dagger = \mathbb{1}$. Unitary evolution preserves the norm: $\langle\psi(t)|\psi(t)\rangle = \langle\psi(0)|\psi(0)\rangle = 1$.

For a time-independent Hamiltonian, if $|\psi(0)\rangle$ is an energy eigenstate $\hat{H}|E\rangle = E|E\rangle$, then:

$$
|\psi(t)\rangle = e^{-iEt/\hbar}|E\rangle
$$

The state acquires only a global phase -- it does not change physically. This is why energy eigenstates are called **stationary states**.

## 2.7 Pure States vs. Mixed States

So far, we have described **pure states** -- states represented by a single vector $|\psi\rangle$. But not all quantum systems are in pure states. A system may be in a **statistical mixture** of states, described by a **density matrix**.

The density matrix for a pure state $|\psi\rangle$ is:

$$
\hat{\rho} = |\psi\rangle\langle\psi|
$$

**[ESTABLISHED]**

For a mixed state (a statistical ensemble where the system is in state $|\psi_i\rangle$ with probability $p_i$), the density matrix is:

$$
\hat{\rho} = \sum_i p_i |\psi_i\rangle\langle\psi_i|
$$

where $p_i \geq 0$ and $\sum_i p_i = 1$.

**Properties of density matrices:**

1. **Hermitian:** $\hat{\rho}^\dagger = \hat{\rho}$
2. **Positive semi-definite:** $\langle\phi|\hat{\rho}|\phi\rangle \geq 0$ for all $|\phi\rangle$
3. **Normalized:** $\text{Tr}(\hat{\rho}) = 1$
4. **Idempotent iff pure:** $\hat{\rho}^2 = \hat{\rho}$ if and only if $\hat{\rho} = |\psi\rangle\langle\psi|$ for some $|\psi\rangle$

**[ESTABLISHED]**

The expectation value of an observable $\hat{O}$ in a mixed state is:

$$
\langle \hat{O} \rangle = \text{Tr}(\hat{\rho}\,\hat{O})
$$

For a pure state, this reduces to $\langle\psi|\hat{O}|\psi\rangle$.

## 2.8 Purity and Entropy

The **purity** of a state is defined as:

$$
\gamma = \text{Tr}(\hat{\rho}^2)
$$

**[ESTABLISHED]**

For a pure state, $\hat{\rho}^2 = \hat{\rho}$, so $\gamma = \text{Tr}(\hat{\rho}) = 1$ (maximum purity). For a maximally mixed state in a $d$-dimensional Hilbert space, $\hat{\rho} = \frac{1}{d}\mathbb{1}$, so $\gamma = \frac{1}{d}$ (minimum purity).

The **von Neumann entropy** measures how mixed a state is:

$$
S(\hat{\rho}) = -\text{Tr}(\hat{\rho}\,\ln\hat{\rho})
$$

**[ESTABLISHED]**

For a pure state, $S = 0$ (no uncertainty). For a maximally mixed state in dimension $d$, $S = \ln d$ (maximum uncertainty). The von Neumann entropy is the quantum analog of the classical Shannon entropy.

## 2.9 Tensor Products: Composite Systems

When two quantum systems $A$ and $B$ are combined, the total Hilbert space is the **tensor product**:

$$
\mathcal{H}_{AB} = \mathcal{H}_A \otimes \mathcal{H}_B
$$

**[ESTABLISHED]**

If $\{|a_i\rangle\}$ is a basis for $\mathcal{H}_A$ and $\{|b_j\rangle\}$ is a basis for $\mathcal{H}_B$, then $\{|a_i\rangle \otimes |b_j\rangle\}$ is a basis for $\mathcal{H}_{AB}$.

**Example:** Two spin-1/2 particles. Each lives in $\mathbb{C}^2$ with basis $\{|\uparrow\rangle, |\downarrow\rangle\}$. The composite system lives in $\mathbb{C}^2 \otimes \mathbb{C}^2 = \mathbb{C}^4$ with basis:

$$
|\uparrow\uparrow\rangle, \quad |\uparrow\downarrow\rangle, \quad |\downarrow\uparrow\rangle, \quad |\downarrow\downarrow\rangle
$$

**Product states:** A state $|\psi_{AB}\rangle$ is a **product state** if it can be written as:

$$
|\psi_{AB}\rangle = |\psi_A\rangle \otimes |\psi_B\rangle
$$

**[ESTABLISHED]**

In a product state, the subsystems are **uncorrelated** -- measuring one does not affect the state of the other.

## 2.10 Entanglement

A state is **entangled** if it cannot be written as a product state. **[ESTABLISHED]**

**Example (Bell state):** Consider two spin-1/2 particles in the state:

$$
|\Psi^-\rangle = \frac{1}{\sqrt{2}}\left(|\uparrow\downarrow\rangle - |\downarrow\uparrow\rangle\right)
$$

This is the singlet state. It cannot be written as $|\psi_A\rangle \otimes |\psi_B\rangle$ for any choice of $|\psi_A\rangle$ and $|\psi_B\rangle$. The particles are entangled: measuring the spin of one instantly determines the spin of the other, even if they are spatially separated.

Entanglement is the signature feature of quantum mechanics that distinguishes it from classical correlations. It underlies quantum teleportation, quantum cryptography, and quantum computing. **[ESTABLISHED]**

## 2.11 Reduced Density Matrices

For a composite system $AB$ in state $\hat{\rho}_{AB}$, the **reduced density matrix** of subsystem $A$ is obtained by tracing over subsystem $B$:

$$
\hat{\rho}_A = \text{Tr}_B(\hat{\rho}_{AB})
$$

**[ESTABLISHED]**

Explicitly, if $\{|b_j\rangle\}$ is a basis for $\mathcal{H}_B$, then:

$$
\hat{\rho}_A = \sum_j \langle b_j|\hat{\rho}_{AB}|b_j\rangle
$$

The reduced density matrix contains all the information accessible by measurements on subsystem $A$ alone.

**Key property:** Even if $|\psi_{AB}\rangle$ is a pure state (so $\hat{\rho}_{AB} = |\psi_{AB}\rangle\langle\psi_{AB}|$ is pure), the reduced density matrix $\hat{\rho}_A$ may be mixed. This happens precisely when the state is entangled.

**Example:** For the singlet state $|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|\uparrow\downarrow\rangle - |\downarrow\uparrow\rangle)$, the reduced density matrix of particle $A$ is:

$$
\hat{\rho}_A = \frac{1}{2}\left(|\uparrow\rangle\langle\uparrow| + |\downarrow\rangle\langle\downarrow|\right) = \frac{1}{2}\mathbb{1}
$$

This is a maximally mixed state. Even though the total system is in a pure state, each individual particle is maximally uncertain. **[ESTABLISHED]**

## 2.12 The Born Rule for Density Matrices

The Born rule generalizes straightforwardly to density matrices.

> **Born Rule (Density Matrix Form):** If a system is described by density matrix $\hat{\rho}$ and an observable $\hat{O}$ with spectral decomposition $\hat{O} = \sum_i o_i |o_i\rangle\langle o_i|$ is measured, the probability of outcome $o_i$ is:
> $$P(o_i) = \text{Tr}\left(\hat{\rho}\,|o_i\rangle\langle o_i|\right) = \langle o_i|\hat{\rho}|o_i\rangle$$

**[ESTABLISHED]**

This reduces to $|\langle o_i|\psi\rangle|^2$ when $\hat{\rho} = |\psi\rangle\langle\psi|$.

## 2.13 Projectors and Measurement

A **projector** is an operator $\hat{P}$ satisfying $\hat{P}^2 = \hat{P}$ and $\hat{P}^\dagger = \hat{P}$. The simplest example is:

$$
\hat{P}_i = |o_i\rangle\langle o_i|
$$

which projects onto the eigenspace of eigenvalue $o_i$. **[ESTABLISHED]**

Projectors satisfy:

$$
\sum_i \hat{P}_i = \mathbb{1}, \quad \hat{P}_i\hat{P}_j = \delta_{ij}\hat{P}_i
$$

These are called a **resolution of the identity**. Measurement is described by applying a projector and renormalizing:

$$
|\psi\rangle \to \frac{\hat{P}_i|\psi\rangle}{\|\hat{P}_i|\psi\rangle\|} \quad \text{with probability} \quad P(o_i) = \|\hat{P}_i|\psi\rangle\|^2 = \langle\psi|\hat{P}_i|\psi\rangle
$$

**[ESTABLISHED]**

## 2.14 Commuting Observables and Simultaneous Eigenstates

Two observables $\hat{A}$ and $\hat{B}$ **commute** if:

$$
[\hat{A}, \hat{B}] = \hat{A}\hat{B} - \hat{B}\hat{A} = 0
$$

**[ESTABLISHED]**

**Theorem:** If $[\hat{A}, \hat{B}] = 0$, then $\hat{A}$ and $\hat{B}$ have a common set of eigenstates. That is, there exists a basis $\{|i\rangle\}$ such that:

$$
\hat{A}|i\rangle = a_i|i\rangle, \quad \hat{B}|i\rangle = b_i|i\rangle
$$

**[PROVEN]**

In such a basis, both $\hat{A}$ and $\hat{B}$ can be simultaneously diagonalized, and both observables can be measured without disturbing each other.

Conversely, if $[\hat{A}, \hat{B}] \neq 0$, then no such common eigenbasis exists, and the observables are called **incompatible**. The canonical example is position and momentum: $[\hat{x}, \hat{p}] = i\hbar$.

## 2.15 Uncertainty Relations

For any two observables $\hat{A}$ and $\hat{B}$ and any state $|\psi\rangle$, the **Robertson-Schrödinger uncertainty relation** holds:

$$
\Delta A \cdot \Delta B \geq \frac{1}{2}|\langle[\hat{A}, \hat{B}]\rangle|
$$

where $\Delta A = \sqrt{\langle\hat{A}^2\rangle - \langle\hat{A}\rangle^2}$ is the standard deviation. **[PROVEN]**

For position and momentum, $[\hat{x}, \hat{p}] = i\hbar$, this gives the Heisenberg uncertainty principle:

$$
\Delta x \cdot \Delta p \geq \frac{\hbar}{2}
$$

**[PROVEN]**

This is not a statement about measurement disturbance -- it is a fundamental property of quantum states. No state can have $\Delta x = 0$ and $\Delta p = 0$ simultaneously.

## 2.16 Coherent States as Minimum-Uncertainty States

A state $|\psi\rangle$ **saturates** the uncertainty relation for $\hat{x}$ and $\hat{p}$ if:

$$
\Delta x \cdot \Delta p = \frac{\hbar}{2}
$$

Such states are called **minimum-uncertainty states** or **intelligent states**. For the harmonic oscillator, the coherent states (to be discussed in detail in later lessons) are minimum-uncertainty states. **[ESTABLISHED]**

## 2.17 The Role of Symmetry: Unitary Transformations

A **unitary operator** $\hat{U}$ satisfies $\hat{U}^\dagger\hat{U} = \hat{U}\hat{U}^\dagger = \mathbb{1}$. Unitary operators preserve inner products:

$$
\langle\hat{U}\psi|\hat{U}\phi\rangle = \langle\psi|\phi\rangle
$$

and thus preserve probabilities. **[ESTABLISHED]**

Symmetries in quantum mechanics are represented by unitary operators (or anti-unitary operators, in the case of time reversal). For example:

- **Spatial translation by $\mathbf{a}$:** $\hat{U}(\mathbf{a}) = e^{-i\mathbf{p} \cdot \mathbf{a}/\hbar}$
- **Time translation by $t$:** $\hat{U}(t) = e^{-i\hat{H}t/\hbar}$
- **Rotation by angle $\theta$ about axis $\mathbf{n}$:** $\hat{U}(\theta, \mathbf{n}) = e^{-i\mathbf{J}\cdot\mathbf{n}\theta/\hbar}$ (where $\mathbf{J}$ is angular momentum)

By Noether's theorem, every continuous symmetry corresponds to a conserved quantity. **[ESTABLISHED]**

## 2.18 Basis Independence and the Trace

The trace of an operator is basis-independent:

$$
\text{Tr}(\hat{O}) = \sum_i \langle i|\hat{O}|i\rangle
$$

for any orthonormal basis $\{|i\rangle\}$. **[PROVEN]** (This is a fundamental property of linear algebra.)

This is why expectation values $\langle\hat{O}\rangle = \text{Tr}(\hat{\rho}\,\hat{O})$ are physical -- they do not depend on the choice of basis. Similarly, the von Neumann entropy $S = -\text{Tr}(\hat{\rho}\,\ln\hat{\rho})$ is basis-independent.

## 2.19 Complete Sets of Commuting Observables (CSCO)

A set of observables $\{\hat{O}_1, \hat{O}_2, \ldots, \hat{O}_n\}$ is called a **complete set of commuting observables (CSCO)** if:

1. All observables in the set commute with each other.
2. The simultaneous eigenstates are uniquely labeled by the eigenvalues $(o_1, o_2, \ldots, o_n)$.

**[ESTABLISHED]**

**Example:** For a free particle in 3D, the momentum components $(\hat{p}_x, \hat{p}_y, \hat{p}_z)$ form a CSCO. The eigenstates $|\mathbf{p}\rangle$ are uniquely labeled by the momentum vector $\mathbf{p}$.

For a hydrogen atom, the energy $\hat{H}$, total angular momentum squared $\hat{L}^2$, and $z$-component of angular momentum $\hat{L}_z$ form a CSCO. The eigenstates $|n, l, m\rangle$ are labeled by $(E_n, l, m)$.

Choosing a CSCO is equivalent to choosing a basis for the Hilbert space. Different choices correspond to different representations of the same physical system.

## 2.20 Why This Matters for Vacuum Selection

The axioms we will propose in Lesson 5 constrain the vacuum state $|0\rangle$ (or, more generally, the vacuum density matrix $\hat{\rho}_0$) using the concepts developed here:

- **Axiom 1 (Hilbert Space Structure):** The vacuum is a state in the Fock space Hilbert space (to be defined in Lesson 3).
- **Axiom 2 (Relativistic Covariance):** The vacuum is invariant under Poincaré transformations: $\hat{U}(\Lambda, a)|0\rangle = |0\rangle$.
- **Axiom 3 (Spectrum Condition):** The vacuum has the lowest energy eigenvalue.
- **Axiom 6 (Entropy Minimization):** The vacuum is a pure state, $S(\hat{\rho}_0) = 0$, so $\hat{\rho}_0 = |0\rangle\langle 0|$.

These constraints are all formulated in the language of Hilbert spaces, density matrices, and unitary transformations. Without this mathematical foundation, the axioms would be meaningless.

## Summary of Key Concepts

| Concept | Definition | Status |
|---------|------------|--------|
| Hilbert space | Vector space with inner product and completeness | [ESTABLISHED] |
| Quantum state | Unit vector $|\psi\rangle$ with $\langle\psi|\psi\rangle = 1$ | [ESTABLISHED] |
| Observable | Hermitian operator $\hat{O}^\dagger = \hat{O}$ | [ESTABLISHED] |
| Spectral theorem | Hermitian operators have real eigenvalues and orthonormal eigenvectors | [PROVEN] |
| Born rule | $P(o_i) = |\langle o_i|\psi\rangle|^2$ | [ESTABLISHED] |
| Density matrix | $\hat{\rho} = \sum_i p_i |\psi_i\rangle\langle\psi_i|$, $\text{Tr}(\hat{\rho}) = 1$ | [ESTABLISHED] |
| Pure vs. mixed | $\hat{\rho}^2 = \hat{\rho}$ iff pure | [ESTABLISHED] |
| Von Neumann entropy | $S = -\text{Tr}(\hat{\rho}\ln\hat{\rho})$ | [ESTABLISHED] |
| Tensor product | $\mathcal{H}_{AB} = \mathcal{H}_A \otimes \mathcal{H}_B$ | [ESTABLISHED] |
| Entanglement | State that cannot be written as $|\psi_A\rangle \otimes |\psi_B\rangle$ | [ESTABLISHED] |
| Reduced density matrix | $\hat{\rho}_A = \text{Tr}_B(\hat{\rho}_{AB})$ | [ESTABLISHED] |
| Uncertainty principle | $\Delta x \cdot \Delta p \geq \hbar/2$ | [PROVEN] |

## Looking Ahead

We now have the mathematical language of quantum mechanics: Hilbert spaces, states, observables, density matrices, tensor products, entanglement. In Lesson 3, we will apply these concepts to quantum fields, showing how a field decomposes into infinitely many harmonic oscillators and how the Fock space is constructed from tensor products of single-oscillator Hilbert spaces.

In Lesson 4, we will discuss the vacuum state in quantum field theory -- what it is, why there are multiple candidates, and what the standard choice (the "mode vacuum") predicts. Then in Lesson 5, we will state the seven axioms precisely and investigate which vacuum states satisfy them.

The machinery is now in place. The rest is application.
