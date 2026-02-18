# Primer: The Mode Vacuum — Standard QFT's Ground State

## The Big Idea

The mode vacuum is the ground state of standard quantum field theory. It is the state you find in every QFT textbook, the starting point for calculating particle interactions, and the foundation of the Standard Model of particle physics.

But it has a fatal flaw: its energy density is infinite.

## How the Mode Vacuum Is Defined

In quantum field theory, every field (like the electromagnetic field or the electron field) decomposes into independent oscillators, one for each momentum mode $\mathbf{k}$. Each mode behaves like a quantum harmonic oscillator from Lesson 1, with creation operator $a^\dagger_{\mathbf{k}}$ and annihilation operator $a_{\mathbf{k}}$.

The mode vacuum $|0\rangle_{\text{mode}}$ is defined as the state annihilated by all annihilation operators:

$$
a_{\mathbf{k}} |0\rangle_{\text{mode}} = 0 \quad \text{for all } \mathbf{k}
$$

This is the lowest-energy state. You cannot remove any quanta — the vacuum is already at the bottom of the ladder.

Excited states are built by applying creation operators: $a^\dagger_{\mathbf{k}} |0\rangle$ creates one particle with momentum $\mathbf{k}$, and so on. The full space of states (Fock space) is built this way.

## The Energy Divergence

The total energy of the mode vacuum is the sum of zero-point energies over all modes:

$$
E_0 = \sum_{\mathbf{k}} \frac{1}{2} \hbar \omega_k
$$

For a massless field, $\omega_k = c|\mathbf{k}|$. The energy density (energy per unit volume) is:

$$
\rho_{\text{mode}} = \int \frac{d^3k}{(2\pi)^3} \frac{1}{2} \hbar c |\mathbf{k}|
$$

This integral diverges. The integrand grows as $k^3$, so the integral is quartically divergent.

To regulate it, we introduce a UV cutoff: integrate only up to $k_{\text{max}} = \pi/a$, where $a$ is a lattice spacing. The result is:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \left(\frac{\pi}{a}\right)^4
$$

As $a \to 0$, this diverges as $a^{-4}$. The mode vacuum does not have a well-defined continuum limit. It fails axiom A1 (Refinability).

## The Standard Fix: Renormalization

In standard QFT, the infinite vacuum energy is "fixed" by renormalization. The idea: redefine the zero of energy so the vacuum has zero energy by fiat. Subtract $\langle 0 | H | 0 \rangle$ from the Hamiltonian and work with the normal-ordered version:

$$
{:}H{:} = H - \langle 0 | H | 0 \rangle
$$

Now $\langle 0 | {:}H{:} | 0 \rangle = 0$. Problem solved?

Not quite. Renormalization hides the divergence but does not eliminate it. The vacuum energy is still infinite — we have just agreed to call it zero. If we couple the field to gravity (where absolute energy matters), the infinite energy reappears. And we have no explanation for why the observed vacuum energy is so small.

Renormalization works brilliantly for computing scattering amplitudes, where only energy *differences* matter. But it does not solve the vacuum energy problem.

## Why the Mode Vacuum Is Mathematically Elegant

Despite its infinite energy, the mode vacuum has several beautiful properties:

1. **Lorentz invariance**: It looks the same in all inertial frames.
2. **Translation invariance**: It looks the same everywhere in space and time.
3. **Maximal entanglement**: It is maximally entangled across all spatial bipartitions (entanglement entropy $S \sim A/a^2$, where $A$ is the boundary area).

These properties make the mode vacuum mathematically appealing. It respects all the symmetries of spacetime.

But physical correctness is not the same as mathematical elegance.

## Why the Mode Vacuum Fails

Axiom A1 (Refinability) demands that physical observables converge as you refine the lattice:

$$
\lim_{a \to 0} \langle O \rangle_a = \text{finite}
$$

The mode vacuum fails this test. Its energy density diverges quartically:

$$
\lim_{a \to 0} \rho_{\text{mode}}(a) = \infty
$$

It does not have a well-defined continuum limit. The mode vacuum is not the physical vacuum.

## What Comes Next

The coherent vacuum (Lesson 5) is a different state, constructed from coherent states of the field modes. It satisfies all seven axioms, including A1 and F (Finiteness). Its energy density is finite for all $a > 0$, and the limit $a \to 0$ exists.

The mode vacuum is wrong. The coherent vacuum is right. That is the central claim of the axiomatic framework.
