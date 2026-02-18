# Lesson 1: The Quantum Harmonic Oscillator

## Overview

The quantum harmonic oscillator is the universal building block of quantum field theory. Every free field decomposes into independent oscillators, one per momentum mode. Understanding why the ground state energy is nonzero -- and what that implies when you have infinitely many oscillators -- is the first step toward the vacuum energy problem.

This lesson is entirely standard quantum mechanics. Every result here is **[PROVEN]** -- mathematically demonstrated and experimentally confirmed.

## 1.1 The Classical Starting Point

A classical harmonic oscillator has Hamiltonian

$$
H = \frac{p^2}{2m} + \frac{1}{2}m\omega^2 x^2
$$

where $m$ is the mass, $\omega$ the angular frequency, $x$ the displacement, and $p$ the momentum. The motion is sinusoidal: $x(t) = A\cos(\omega t + \phi)$. The energy can be any non-negative value, and in particular it can be exactly zero when $x = 0$ and $p = 0$ simultaneously. **[PROVEN]**

Quantization changes this fundamentally.

## 1.2 Canonical Quantization

We promote $x$ and $p$ to operators satisfying the canonical commutation relation:

$$
[\hat{x}, \hat{p}] = i\hbar
$$

This single relation -- a direct consequence of the structure of quantum mechanics -- is the seed from which all zero-point energy grows. It encodes the uncertainty principle in algebraic form: if $\hat{x}$ and $\hat{p}$ commuted, we could simultaneously know both position and momentum with arbitrary precision, and the ground state energy could be zero. Because they do not commute, the ground state retains irreducible fluctuations. **[PROVEN]**

The commutation relation can be derived from the canonical quantization prescription -- replacing Poisson brackets with commutators -- or taken as an axiom. Either way, it has been confirmed by every precision experiment in atomic, molecular, and condensed matter physics for nearly a century.

## 1.3 Creation and Annihilation Operators

Rather than working with $\hat{x}$ and $\hat{p}$ directly, we define the annihilation and creation operators:

$$
\hat{a} = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} + \frac{i\hat{p}}{m\omega}\right)
$$

$$
\hat{a}^\dagger = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} - \frac{i\hat{p}}{m\omega}\right)
$$

These are not Hermitian (they are not observables), but they are enormously useful. From $[\hat{x}, \hat{p}] = i\hbar$, a direct calculation yields:

$$
[\hat{a}, \hat{a}^\dagger] = 1
$$

This is the fundamental commutation relation for the oscillator algebra. **[PROVEN]**

The inverse relations are:

$$
\hat{x} = \sqrt{\frac{\hbar}{2m\omega}}(\hat{a} + \hat{a}^\dagger), \qquad \hat{p} = i\sqrt{\frac{m\hbar\omega}{2}}(\hat{a}^\dagger - \hat{a})
$$

## 1.4 The Hamiltonian in Operator Form

Substituting into the Hamiltonian:

$$
H = \hbar\omega\left(\hat{a}^\dagger \hat{a} + \frac{1}{2}\right)
$$

We define the **number operator** $\hat{n} = \hat{a}^\dagger \hat{a}$, so:

$$
H = \hbar\omega\left(\hat{n} + \frac{1}{2}\right)
$$

The $+\frac{1}{2}$ is not a convention. It is forced by the commutation relation. If you try to write $H = \hbar\omega\,\hat{a}^\dagger\hat{a}$ (without the half), you get a different operator that does not equal $\frac{p^2}{2m} + \frac{1}{2}m\omega^2 x^2$. The zero-point energy is algebraically mandatory. **[PROVEN]**

## 1.5 Number States and Energy Eigenvalues

The eigenstates of $\hat{n}$ are the **number states** (or Fock states) $|n\rangle$, satisfying:

$$
\hat{n}|n\rangle = n|n\rangle, \qquad n = 0, 1, 2, \ldots
$$

The energy eigenvalues are therefore:

$$
E_n = \hbar\omega\left(n + \frac{1}{2}\right)
$$

The ladder operators act as:

$$
\hat{a}^\dagger|n\rangle = \sqrt{n+1}\,|n+1\rangle \qquad \text{(creation: adds one quantum)}
$$

$$
\hat{a}|n\rangle = \sqrt{n}\,|n-1\rangle \qquad \text{(annihilation: removes one quantum)}
$$

**Proof that these are the only eigenvalues:** Suppose $H|\psi\rangle = E|\psi\rangle$. Then $H(\hat{a}|\psi\rangle) = (E - \hbar\omega)(\hat{a}|\psi\rangle)$. Repeated application of $\hat{a}$ lowers the energy by $\hbar\omega$ each time. Since $H$ is a sum of squares of Hermitian operators, $E \geq 0$, so the lowering must terminate. It terminates when $\hat{a}|0\rangle = 0$, giving $E_0 = \hbar\omega/2$. All higher states are reached by applying $\hat{a}^\dagger$ repeatedly. **[PROVEN]**

## 1.6 The Ground State

The ground state $|0\rangle$ is defined by:

$$
\hat{a}|0\rangle = 0
$$

This is not "the state with no particles" in some vague sense -- it is the precise mathematical statement that no further lowering is possible. The ground state energy is:

$$
E_0 = \frac{1}{2}\hbar\omega
$$

In position representation, the ground state wavefunction is:

$$
\psi_0(x) = \left(\frac{m\omega}{\pi\hbar}\right)^{1/4} \exp\left(-\frac{m\omega x^2}{2\hbar}\right)
$$

This is a Gaussian centered at $x = 0$, with width $\Delta x = \sqrt{\hbar/(2m\omega)}$. **[PROVEN]**

## 1.7 Why You Cannot Reach Zero Energy

The ground state energy $E_0 = \hbar\omega/2$ is irreducible. This is not a technicality -- it is a direct consequence of the uncertainty principle.

**The uncertainty principle connection:** For the ground state:

$$
\Delta x = \sqrt{\frac{\hbar}{2m\omega}}, \qquad \Delta p = \sqrt{\frac{m\hbar\omega}{2}}
$$

Therefore:

$$
\Delta x \cdot \Delta p = \frac{\hbar}{2}
$$

The ground state **saturates** the Heisenberg bound -- it achieves the minimum uncertainty allowed by quantum mechanics. **[PROVEN]**

Now suppose $E_0 = 0$. This would require both $\langle p^2\rangle = 0$ and $\langle x^2\rangle = 0$ (since both the kinetic and potential energy terms are non-negative). But $\langle p^2\rangle = 0$ implies $\Delta p = 0$ (the particle has definite momentum $p = 0$), and $\langle x^2\rangle = 0$ implies $\Delta x = 0$ (the particle has definite position $x = 0$). This violates $\Delta x \cdot \Delta p \geq \hbar/2$.

Therefore $E_0 = 0$ is impossible. The particle must fluctuate, and those fluctuations carry energy. **[PROVEN]**

## 1.8 The Energy Budget

It is instructive to decompose the ground state energy into kinetic and potential contributions:

$$
\langle T \rangle_0 = \frac{\langle p^2\rangle_0}{2m} = \frac{1}{2}\cdot\frac{\hbar\omega}{2} = \frac{\hbar\omega}{4}
$$

$$
\langle V \rangle_0 = \frac{1}{2}m\omega^2\langle x^2\rangle_0 = \frac{1}{2}\cdot\frac{\hbar\omega}{2} = \frac{\hbar\omega}{4}
$$

The kinetic and potential energies are exactly equal -- each contributes half of $E_0$. This is the quantum virial theorem for the harmonic oscillator. **[PROVEN]**

## 1.9 The Prototype of the Vacuum Energy Problem

Now consider $N$ independent oscillators with frequencies $\omega_k$ (where $k$ labels the modes). The total ground state energy is:

$$
E_0^{\text{total}} = \sum_{k=1}^{N} \frac{1}{2}\hbar\omega_k
$$

For finite $N$, this is a finite number. But quantum field theory has one oscillator per momentum mode, and there are infinitely many modes. If we impose a UV cutoff $\Lambda$ (ignoring modes with $|\mathbf{k}| > \Lambda$) and work in a box of volume $V$, the sum becomes an integral:

$$
E_0^{\text{total}} = V \int_0^{\Lambda} \frac{d^3k}{(2\pi)^3} \frac{1}{2}\hbar\omega_k
$$

For a massless field ($\omega_k = c|\mathbf{k}|$), this gives an energy density:

$$
\rho_0 = \frac{E_0^{\text{total}}}{V} \sim \frac{\hbar c \Lambda^4}{16\pi^2}
$$

As $\Lambda \to \infty$, this diverges. Even at the Planck scale ($\Lambda = M_{\text{Pl}}c/\hbar$), it gives $\rho_0 \sim 10^{113}$ J/m$^3$ -- a factor of $10^{123}$ larger than the observed dark energy density. This is the "worst prediction in physics." **[PROVEN]**

We will return to this problem -- and what it does and does not mean -- in Lessons 3 and 5.

## 1.10 Number States Are Not Classical

An important property of number states: they do not resemble classical oscillations. For any number state $|n\rangle$:

$$
\langle n|\hat{x}|n\rangle = 0, \qquad \langle n|\hat{p}|n\rangle = 0
$$

The expectation values of position and momentum are both zero. A classical oscillator bobs back and forth; a number state does not. Number states have definite energy and definite particle number ($\Delta n = 0$), but completely uncertain phase. They are as far from classical behavior as a harmonic oscillator state can be.

To see this more concretely, consider the state $|1\rangle$ (one quantum). A classical oscillator with energy $E_1 = \frac{3}{2}\hbar\omega$ would swing back and forth with amplitude $A = \sqrt{3\hbar/(m\omega)}$, spending more time near the turning points. But the quantum state $|1\rangle$ has a probability distribution $|\psi_1(x)|^2$ that is symmetric about $x = 0$, with a node at the origin and two peaks. The state does not move -- it is stationary. Its position distribution is time-independent, and its wavefunction acquires only a global phase $e^{-iE_1 t/\hbar}$ under time evolution.

The position variance in a number state grows with $n$:

$$
\langle n|x^2|n\rangle = \frac{\hbar}{2m\omega}(2n + 1)
$$

So higher number states are "wider," but they still do not oscillate. The energy is stored in quantum fluctuations, not in coherent motion. This distinction between energy (which number states have in definite amounts) and motion (which they lack) is central to understanding why number states are useful for counting particles but not for describing classical behavior.

What state does resemble a classical oscillation? That is the subject of Lesson 2. **[PROVEN]**

## 1.11 Experimental Confirmation

The quantum harmonic oscillator is not merely a theoretical construct. Its predictions are confirmed across a remarkable range of physical systems:

- **Molecular vibrations:** Diatomic molecules vibrate at quantized energy levels near equilibrium. The spacing $\hbar\omega$ and zero-point energy $\hbar\omega/2$ are directly measured in infrared spectroscopy. **[PROVEN]**

- **Electromagnetic cavity modes:** Each mode of the electromagnetic field in a resonant cavity is a quantum harmonic oscillator. Superconducting circuit experiments have resolved individual photon number states and directly measured the zero-point fluctuations. **[PROVEN]**

- **Phonons in solids:** Lattice vibrations in crystals are quantized as phonons, with the characteristic equally-spaced energy spectrum $E_n = \hbar\omega(n + 1/2)$. The heat capacity of solids at low temperatures confirms the zero-point energy contribution. **[PROVEN]**

- **The Casimir effect:** Two uncharged conducting plates in vacuum experience an attractive force due to the modification of zero-point fluctuations between them. Measured to percent-level accuracy, this effect directly demonstrates that vacuum fluctuations carry real, measurable energy. **[PROVEN]**

These experiments confirm that zero-point energy is not a mathematical artifact -- it is a physical reality with measurable consequences.

## Summary of Key Results

| Result | Status |
|--------|--------|
| $[\hat{a}, \hat{a}^\dagger] = 1$ | [PROVEN] |
| $E_n = \hbar\omega(n + 1/2)$ | [PROVEN] |
| $E_0 = \hbar\omega/2 > 0$ | [PROVEN] |
| $\Delta x \cdot \Delta p = \hbar/2$ in ground state | [PROVEN] |
| $\langle T\rangle = \langle V\rangle = \hbar\omega/4$ in ground state | [PROVEN] |
| Sum over modes diverges as $\Lambda^4$ | [PROVEN] |

## Looking Ahead

The quantum harmonic oscillator gives us the ground-floor toolkit: creation/annihilation operators, number states, zero-point energy, and the uncertainty principle's role in preventing $E = 0$. In Lesson 2, we will meet the coherent states -- the quantum states that most closely resemble classical oscillations -- and discover that one particular coherent state, with $|\alpha|^2 = 1/2$, has remarkable properties. In Lesson 3, we will see what happens when you have one oscillator per momentum mode: the quantum field and its vacuum.
