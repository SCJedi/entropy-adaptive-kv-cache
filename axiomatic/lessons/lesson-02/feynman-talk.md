# Quantum States and Hilbert Spaces
### A Feynman-Voice Lecture

---

All right, now we're going to talk about the mathematics of quantum mechanics. I know, I know -- you wanted to hear about vacuum energy and cosmology, not linear algebra. But here's the thing: if you don't understand Hilbert spaces, density matrices, and tensor products, you can't even state the axioms for vacuum selection, let alone check whether they work. So we're going to do this properly.

And don't worry -- this is all standard quantum mechanics. Everything in this lesson is **[ESTABLISHED]** -- textbook material, confirmed by millions of experiments. No speculation. Just the tools we need.

## What's a Hilbert Space?

A Hilbert space is just a vector space with an inner product. That's it.

Remember vector spaces from linear algebra? You've got vectors, you can add them, you can multiply them by numbers (scalars). In quantum mechanics, the vectors represent states of a system, and the scalars are complex numbers.

An inner product is a way to measure angles and lengths. For two vectors $|\psi\rangle$ and $|\phi\rangle$, the inner product $\langle\psi|\phi\rangle$ is a complex number. It tells you how much the vectors "overlap."

Key properties:

- $\langle\psi|\psi\rangle$ is real and positive (it's the squared length of $|\psi\rangle$).
- $\langle\psi|\phi\rangle = \langle\phi|\psi\rangle^*$ (conjugate symmetry).
- If $\langle\psi|\phi\rangle = 0$, the vectors are orthogonal.

We normalize states so that $\langle\psi|\psi\rangle = 1$. This ensures probabilities add up to 1. **[ESTABLISHED]**

## States as Vectors

The first axiom of quantum mechanics is:

> The state of a quantum system is represented by a unit vector $|\psi\rangle$ in a Hilbert space.

**[ESTABLISHED]**

For a two-level system (like a spin or a qubit), the Hilbert space is $\mathbb{C}^2$ -- just two complex dimensions. For a particle moving on a line, the Hilbert space is infinite-dimensional: it's the space of all square-integrable functions $\psi(x)$, with inner product:

$$\langle\phi|\psi\rangle = \int_{-\infty}^{\infty} \phi(x)^* \psi(x)\,dx$$

For a quantum field, the Hilbert space is even bigger -- we'll get to that in Lesson 3.

Now, here's an important point: two vectors differing only by a phase represent the same physical state. If $|\psi\rangle$ and $e^{i\theta}|\psi\rangle$ give the same predictions for every measurement, they're the same state. The physical content is in the *ray* (the equivalence class under phase), not the vector itself. **[ESTABLISHED]**

## Superposition

Quantum mechanics has a feature that classical probability doesn't: **superposition**. If $|\psi_1\rangle$ and $|\psi_2\rangle$ are valid states, then so is any normalized linear combination:

$$|\psi\rangle = c_1|\psi_1\rangle + c_2|\psi_2\rangle$$

where $|c_1|^2 + |c_2|^2 = 1$. **[ESTABLISHED]**

This is not "the system is in state $|\psi_1\rangle$ with probability $|c_1|^2$ and state $|\psi_2\rangle$ with probability $|c_2|^2$." It's a genuinely new kind of state. The system is in both states at once, and the relative phase between $c_1$ and $c_2$ matters. That phase leads to interference effects, like in the double-slit experiment.

Superposition is the signature of quantum mechanics. It's why the theory is so weird -- and so powerful.

## Observables as Operators

Measurable quantities -- position, momentum, energy, spin -- are represented by **operators** acting on the Hilbert space. Specifically, **Hermitian operators**. **[ESTABLISHED]**

An operator $\hat{O}$ is Hermitian if $\hat{O}^\dagger = \hat{O}$, where the dagger means "take the complex conjugate and transpose." Equivalently:

$$\langle\phi|\hat{O}\psi\rangle = \langle\hat{O}\phi|\psi\rangle$$

for all $|\psi\rangle$ and $|\phi\rangle$.

Why Hermitian? Because Hermitian operators have real eigenvalues, and measurement outcomes are real numbers. If you allowed non-Hermitian operators, you'd predict complex measurement results, which is nonsense.

The spectral theorem -- a theorem of linear algebra -- says that every Hermitian operator has a complete set of orthonormal eigenvectors with real eigenvalues:

$$\hat{O}|o_i\rangle = o_i|o_i\rangle, \quad \langle o_i|o_j\rangle = \delta_{ij}$$

**[PROVEN]** -- this is pure math.

## The Born Rule

Now we connect the math to experiment. When you measure observable $\hat{O}$ on a system in state $|\psi\rangle$, you get one of the eigenvalues $o_i$. Which one? The Born rule tells you:

> The probability of getting outcome $o_i$ is $P(o_i) = |\langle o_i|\psi\rangle|^2$.

**[ESTABLISHED]** -- confirmed in countless experiments.

After measurement, the state "collapses" to $|o_i\rangle$ (in the Copenhagen interpretation, at least -- but we won't get into interpretational debates here).

The expectation value -- the average you'd get if you repeated the measurement many times -- is:

$$\langle\hat{O}\rangle = \langle\psi|\hat{O}|\psi\rangle = \sum_i o_i |\langle o_i|\psi\rangle|^2$$

This is one of the most precisely tested formulas in all of physics.

## Pure States and Density Matrices

So far I've talked about **pure states** -- states represented by a single vector $|\psi\rangle$. But not every quantum system is in a pure state. Sometimes you have a statistical mixture.

Suppose the system is in state $|\psi_i\rangle$ with probability $p_i$ (where $\sum_i p_i = 1$). This is called a **mixed state**, and it's described by a **density matrix**:

$$\hat{\rho} = \sum_i p_i |\psi_i\rangle\langle\psi_i|$$

**[ESTABLISHED]**

For a pure state $|\psi\rangle$, the density matrix is just $\hat{\rho} = |\psi\rangle\langle\psi|$.

Properties of density matrices:

- Hermitian: $\hat{\rho}^\dagger = \hat{\rho}$
- Positive: all eigenvalues are $\geq 0$
- Normalized: $\text{Tr}(\hat{\rho}) = 1$
- Pure iff idempotent: $\hat{\rho}^2 = \hat{\rho}$ if and only if $\hat{\rho} = |\psi\rangle\langle\psi|$

**[ESTABLISHED]**

The last property is the key test: if $\hat{\rho}^2 = \hat{\rho}$, the state is pure. Otherwise, it's mixed.

## The Von Neumann Entropy

How mixed is a state? The **von Neumann entropy** measures this:

$$S = -\text{Tr}(\hat{\rho}\,\ln\hat{\rho})$$

**[ESTABLISHED]**

For a pure state, $S = 0$ -- no uncertainty. For a maximally mixed state in a $d$-dimensional space (where $\hat{\rho} = \frac{1}{d}\mathbb{1}$), $S = \ln d$ -- maximum uncertainty.

This is the quantum version of Shannon entropy. It quantifies how much information you're missing about the state.

## Composite Systems: Tensor Products

Now suppose you have two quantum systems, $A$ and $B$. How do you describe the combined system?

The answer is the **tensor product**: $\mathcal{H}_{AB} = \mathcal{H}_A \otimes \mathcal{H}_B$. **[ESTABLISHED]**

If $\{|a_i\rangle\}$ is a basis for $\mathcal{H}_A$ and $\{|b_j\rangle\}$ is a basis for $\mathcal{H}_B$, then the basis for $\mathcal{H}_{AB}$ is $\{|a_i\rangle \otimes |b_j\rangle\}$. We usually write this as $|a_i, b_j\rangle$ or just $|a_i b_j\rangle$.

Example: two spin-1/2 particles. Each has a two-dimensional Hilbert space with basis $\{|\uparrow\rangle, |\downarrow\rangle\}$. The combined system has a four-dimensional Hilbert space with basis:

$$|\uparrow\uparrow\rangle, \quad |\uparrow\downarrow\rangle, \quad |\downarrow\uparrow\rangle, \quad |\downarrow\downarrow\rangle$$

Got it? Good.

## Entanglement

Here's where things get interesting. A state of the combined system is called a **product state** if it can be written as:

$$|\psi_{AB}\rangle = |\psi_A\rangle \otimes |\psi_B\rangle$$

In a product state, the subsystems are independent. Measuring one doesn't affect the other.

But most states are not product states. They're **entangled**. **[ESTABLISHED]**

The classic example is the singlet state:

$$|\Psi^-\rangle = \frac{1}{\sqrt{2}}\left(|\uparrow\downarrow\rangle - |\downarrow\uparrow\rangle\right)$$

This cannot be written as $|\psi_A\rangle \otimes |\psi_B\rangle$ for any choice of $|\psi_A\rangle$ and $|\psi_B\rangle$. The two spins are entangled. If you measure the first spin and get $\uparrow$, the second spin is instantly in state $\downarrow$, even if it's a light-year away.

This is the spooky action at a distance Einstein worried about. But it's real. It's been confirmed in experiments thousands of times. Entanglement is the signature feature of quantum mechanics. **[ESTABLISHED]**

## Reduced Density Matrices

Suppose you have a composite system $AB$ in some state $\hat{\rho}_{AB}$, and you only have access to subsystem $A$. What can you say?

You compute the **reduced density matrix** by tracing over subsystem $B$:

$$\hat{\rho}_A = \text{Tr}_B(\hat{\rho}_{AB})$$

**[ESTABLISHED]**

This contains all the information you can extract from measurements on $A$ alone.

Here's a key fact: even if $|\psi_{AB}\rangle$ is a pure state (so $\hat{\rho}_{AB}$ is pure), the reduced density matrix $\hat{\rho}_A$ can be mixed. This happens exactly when the state is entangled.

Example: the singlet state $|\Psi^-\rangle$ is pure. But the reduced density matrix of particle $A$ is:

$$\hat{\rho}_A = \frac{1}{2}(|\uparrow\rangle\langle\uparrow| + |\downarrow\rangle\langle\downarrow|) = \frac{1}{2}\mathbb{1}$$

This is maximally mixed. Each individual particle is in a completely uncertain state, even though the total system is in a definite pure state. That's entanglement for you. **[ESTABLISHED]**

## The Uncertainty Principle

You've probably heard of the Heisenberg uncertainty principle:

$$\Delta x \cdot \Delta p \geq \frac{\hbar}{2}$$

This is a special case of a general result. For any two observables $\hat{A}$ and $\hat{B}$:

$$\Delta A \cdot \Delta B \geq \frac{1}{2}|\langle[\hat{A}, \hat{B}]\rangle|$$

**[PROVEN]** -- this is the Robertson-Schrödinger uncertainty relation.

Here $\Delta A = \sqrt{\langle\hat{A}^2\rangle - \langle\hat{A}\rangle^2}$ is the standard deviation, and $[\hat{A}, \hat{B}] = \hat{A}\hat{B} - \hat{B}\hat{A}$ is the commutator.

For position and momentum, $[\hat{x}, \hat{p}] = i\hbar$, so:

$$\Delta x \cdot \Delta p \geq \frac{\hbar}{2}$$

This is not about measurement disturbance. It's about the state itself. No state -- pure or mixed -- can have zero uncertainty in both $x$ and $p$ simultaneously.

States that saturate this bound, achieving $\Delta x \cdot \Delta p = \hbar/2$ exactly, are called **minimum-uncertainty states**. The ground state of the harmonic oscillator is one. Coherent states are another. We'll see these in Lessons 3 and beyond.

## Unitary Evolution

Between measurements, quantum states evolve according to the Schrödinger equation:

$$i\hbar\frac{d}{dt}|\psi(t)\rangle = \hat{H}|\psi(t)\rangle$$

**[ESTABLISHED]**

The solution is:

$$|\psi(t)\rangle = e^{-i\hat{H}t/\hbar}|\psi(0)\rangle$$

The operator $\hat{U}(t) = e^{-i\hat{H}t/\hbar}$ is **unitary**: $\hat{U}^\dagger\hat{U} = \mathbb{1}$. Unitary operators preserve the norm, so $\langle\psi(t)|\psi(t)\rangle = 1$ for all $t$.

If $|\psi\rangle$ is an energy eigenstate -- $\hat{H}|E\rangle = E|E\rangle$ -- then:

$$|\psi(t)\rangle = e^{-iEt/\hbar}|E\rangle$$

The state picks up only a global phase. It doesn't change physically. That's why energy eigenstates are called **stationary states**.

## Symmetries and Unitary Transformations

Symmetries in quantum mechanics are represented by unitary operators (or anti-unitary, for time reversal). **[ESTABLISHED]**

Examples:

- Spatial translation by $\mathbf{a}$: $\hat{U}(\mathbf{a}) = e^{-i\mathbf{p}\cdot\mathbf{a}/\hbar}$
- Time translation by $t$: $\hat{U}(t) = e^{-i\hat{H}t/\hbar}$
- Rotation by angle $\theta$ about axis $\mathbf{n}$: $\hat{U}(\theta,\mathbf{n}) = e^{-i\mathbf{J}\cdot\mathbf{n}\theta/\hbar}$

By Noether's theorem, every continuous symmetry corresponds to a conserved quantity. Translation symmetry gives conservation of momentum. Time translation symmetry gives conservation of energy. Rotational symmetry gives conservation of angular momentum. **[ESTABLISHED]**

This is important for vacuum selection, because one of the axioms we'll propose is that the vacuum must be invariant under Poincaré transformations (spacetime translations and Lorentz boosts). That's Axiom 2.

## Trace and Basis Independence

The trace of an operator is defined as:

$$\text{Tr}(\hat{O}) = \sum_i \langle i|\hat{O}|i\rangle$$

for any orthonormal basis $\{|i\rangle\}$. **[ESTABLISHED]**

The key fact is that the trace is **basis-independent**. It doesn't matter which basis you use to compute it -- you always get the same answer. **[PROVEN]** (This is a theorem of linear algebra.)

This is why expectation values $\langle\hat{O}\rangle = \text{Tr}(\hat{\rho}\,\hat{O})$ and the von Neumann entropy $S = -\text{Tr}(\hat{\rho}\,\ln\hat{\rho})$ are physical -- they don't depend on arbitrary choices of basis.

## Why This Matters for Vacuum Selection

All right, you might be wondering: why do I need to know all this to understand vacuum energy?

Here's why. The seven axioms we're going to propose constrain the vacuum state using these concepts:

- **Axiom 1:** The vacuum is a state in the Fock space (a Hilbert space built from tensor products -- we'll define this in Lesson 3).
- **Axiom 2:** The vacuum is invariant under Poincaré transformations (unitary symmetries).
- **Axiom 3:** The vacuum has the lowest energy eigenvalue (spectrum condition).
- **Axiom 6:** The vacuum is a pure state, so $S(\hat{\rho}_0) = 0$.

These constraints are all formulated in the language of Hilbert spaces, density matrices, operators, and unitary transformations. Without this mathematical framework, we couldn't even state the axioms, let alone solve them.

So this lesson is the foundation. It's the vocabulary we need to talk precisely about vacuum selection.

## Summary

Let me recap the key points:

- **Hilbert space:** Vector space with an inner product. States are unit vectors.
- **Observables:** Hermitian operators with real eigenvalues.
- **Born rule:** $P(o_i) = |\langle o_i|\psi\rangle|^2$ for pure states, $P(o_i) = \text{Tr}(\hat{\rho}\,|o_i\rangle\langle o_i|)$ for mixed states.
- **Density matrices:** $\hat{\rho} = \sum_i p_i|\psi_i\rangle\langle\psi_i|$. Pure iff $\hat{\rho}^2 = \hat{\rho}$.
- **Entropy:** $S = -\text{Tr}(\hat{\rho}\,\ln\hat{\rho})$. Pure states have $S = 0$.
- **Tensor products:** For composite systems, $\mathcal{H}_{AB} = \mathcal{H}_A \otimes \mathcal{H}_B$.
- **Entanglement:** States that can't be written as $|\psi_A\rangle \otimes |\psi_B\rangle$.
- **Uncertainty principle:** $\Delta A \cdot \Delta B \geq \frac{1}{2}|\langle[\hat{A},\hat{B}]\rangle|$.
- **Unitary evolution:** $|\psi(t)\rangle = e^{-i\hat{H}t/\hbar}|\psi(0)\rangle$.

Everything here is **[ESTABLISHED]** -- standard quantum mechanics, confirmed by experiments ranging from atomic spectroscopy to quantum computers.

## What's Next

In Lesson 3, we apply this framework to quantum fields. A field is an infinite collection of harmonic oscillators, one for each momentum mode. The Hilbert space is the **Fock space**, built by taking tensor products of all the individual oscillator spaces.

The vacuum is the ground state of this infinite-dimensional system. But here's the thing: there are multiple candidates for what "ground state" means. The standard choice is the **mode vacuum** -- every oscillator in its ground state. But that's not the only possibility.

The axioms will select one.

---

*All material in this lesson: [ESTABLISHED] -- standard quantum mechanics, extensively tested and confirmed.*
