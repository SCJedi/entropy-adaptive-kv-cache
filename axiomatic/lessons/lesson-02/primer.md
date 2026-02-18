# Primer: Quantum States and Hilbert Spaces

## The Big Idea

Quantum mechanics is formulated in the language of Hilbert spaces. A Hilbert space is just a vector space with an inner product -- a way to measure angles and lengths. The state of a quantum system is a unit vector $|\psi\rangle$ in this space. Observables (measurable quantities like position, momentum, energy) are operators acting on the space. Measurements extract eigenvalues, with probabilities given by the Born rule.

This lesson is pure standard quantum mechanics. If you've taken a quantum course, most of this is review. If not, think of it as the user manual for the mathematical machinery we'll use to state the vacuum selection axioms.

## States and Vectors

In classical mechanics, the state of a particle is specified by its position $\mathbf{r}$ and momentum $\mathbf{p}$. In quantum mechanics, the state is a vector $|\psi\rangle$ in a Hilbert space $\mathcal{H}$, normalized so that $\langle\psi|\psi\rangle = 1$.

The normalization ensures that probabilities sum to 1. Two vectors differing only by a phase, $|\psi\rangle$ and $e^{i\theta}|\psi\rangle$, represent the same physical state.

## Observables and Operators

Every measurable quantity corresponds to a Hermitian operator -- an operator $\hat{O}$ satisfying $\hat{O}^\dagger = \hat{O}$. Hermitian operators have real eigenvalues (because measurement outcomes are real numbers) and orthonormal eigenvectors (by the spectral theorem).

When you measure observable $\hat{O}$ on state $|\psi\rangle$, you get one of the eigenvalues $o_i$ with probability $P(o_i) = |\langle o_i|\psi\rangle|^2$. This is the Born rule.

## Pure States vs. Mixed States

A **pure state** is represented by a single vector $|\psi\rangle$. Its density matrix is $\hat{\rho} = |\psi\rangle\langle\psi|$.

A **mixed state** is a statistical mixture: the system is in state $|\psi_i\rangle$ with probability $p_i$. Its density matrix is $\hat{\rho} = \sum_i p_i |\psi_i\rangle\langle\psi_i|$.

The key signature: $\hat{\rho}^2 = \hat{\rho}$ if and only if the state is pure. For mixed states, $\hat{\rho}^2 \neq \hat{\rho}$.

The von Neumann entropy $S = -\text{Tr}(\hat{\rho}\ln\hat{\rho})$ quantifies mixedness. Pure states have $S = 0$. Maximally mixed states have maximum entropy.

## Composite Systems and Tensor Products

When two systems $A$ and $B$ are combined, the total Hilbert space is the tensor product: $\mathcal{H}_{AB} = \mathcal{H}_A \otimes \mathcal{H}_B$.

If system $A$ has basis $\{|a_i\rangle\}$ and system $B$ has basis $\{|b_j\rangle\}$, the composite system has basis $\{|a_i\rangle \otimes |b_j\rangle\}$.

A **product state** can be written as $|\psi_A\rangle \otimes |\psi_B\rangle$. An **entangled state** cannot. Entanglement is the quintessentially quantum feature: measuring one subsystem instantly affects the other, even across vast distances.

## The Born Rule for Density Matrices

For a system described by density matrix $\hat{\rho}$, the probability of measuring outcome $o_i$ (eigenvalue of $\hat{O}$) is:

$$P(o_i) = \text{Tr}(\hat{\rho}\,|o_i\rangle\langle o_i|)$$

The expectation value is:

$$\langle\hat{O}\rangle = \text{Tr}(\hat{\rho}\,\hat{O})$$

This generalizes the pure-state formula $\langle\psi|\hat{O}|\psi\rangle$.

## Why This Matters

The seven axioms we'll propose for vacuum selection are stated in this language:

- The vacuum is a state (vector or density matrix) in Fock space.
- It has minimum energy (spectrum condition).
- It's invariant under symmetries (Poincaré transformations, discrete translations).
- It's a pure state (entropy minimization: $S = 0$).

Without Hilbert spaces, density matrices, and the Born rule, we couldn't even formulate these constraints. This lesson provides the vocabulary.

## What Comes Next

Lesson 3 applies this framework to quantum fields. A field decomposes into infinitely many harmonic oscillators, one per momentum mode. The Hilbert space is the Fock space -- an infinite tensor product of oscillator Hilbert spaces. The vacuum is the ground state of this infinite-dimensional system.

Then we'll ask: which vacuum? The standard answer is the "mode vacuum" (every oscillator in its ground state). But there are other candidates. The axioms will select one.
