# Primer: Quantum Fields and the Mode Vacuum

## The Big Idea

A quantum field is an infinite collection of harmonic oscillators -- one for each wavelength (or equivalently, each momentum mode). The "vacuum" of quantum field theory is the state where every one of these oscillators is in its ground state: zero particles in every mode. This is called the **mode vacuum**.

The mode vacuum has a problem. Each oscillator contributes a zero-point energy $\hbar\omega/2$, and there are infinitely many oscillators. The total energy density is infinite. Even if you cut off the sum at the Planck scale (the highest energy that makes physical sense), the predicted vacuum energy density is about $10^{123}$ times larger than what cosmological observations show. This is the cosmological constant problem.

## How Fields Become Oscillators

A real scalar field $\phi(\mathbf{x}, t)$ can be decomposed into plane waves -- oscillations of definite wavelength. Each plane wave has a wavevector $\mathbf{k}$ (specifying its wavelength and direction) and oscillates at frequency $\omega_\mathbf{k} = \sqrt{|\mathbf{k}|^2 + m^2}$, where $m$ is the particle mass (in natural units).

Upon quantization, each mode $\mathbf{k}$ becomes an independent quantum harmonic oscillator with its own creation and annihilation operators $\hat{a}^\dagger_\mathbf{k}$ and $\hat{a}_\mathbf{k}$. The quantum field is just the sum over all these oscillators.

## The Mode Vacuum

The mode vacuum $|0\rangle$ is defined by:

$$\hat{a}_\mathbf{k}|0\rangle = 0 \quad \text{for all } \mathbf{k}$$

It is the state with zero particles in every mode. Its properties include:

- **Definite in momentum space**: every mode has exactly zero particles.
- **Indefinite in position space**: the field fluctuates at every point (the amplitude is uncertain, even though the particle number is certain).
- **Nonlocally entangled**: the famous Reeh-Schlieder theorem says the vacuum is entangled across all spatial regions. Acting with local operators in any bounded region can approximate any state in the entire Hilbert space.
- **Poincare invariant**: every inertial observer sees the same vacuum.

## The Divergence

The vacuum energy density, summing zero-point energies over all modes up to a cutoff $\Lambda$, is:

$$\rho_0 \approx \frac{\Lambda^4}{16\pi^2}$$

Setting $\Lambda$ to the Planck scale gives $\rho_0 \sim 10^{113}$ J/m$^3$. The observed dark energy density is about $5 \times 10^{-10}$ J/m$^3$. The mismatch is a factor of $10^{123}$.

The standard fix in particle physics -- "normal ordering," which subtracts the vacuum energy by hand -- works fine when you only care about energy differences. But general relativity says all energy gravitates. You cannot freely choose the zero of energy when gravity is involved.

## Why This Matters

The mode vacuum is the foundation of all particle physics calculations. Its predictions for the Lamb shift, Casimir effect, and scattering cross-sections are confirmed to extraordinary precision. No one doubts that the mode vacuum is the right state for those questions.

The open question is whether the mode vacuum is the right state for computing the gravitational vacuum energy. The mode vacuum is defined by being "empty" mode by mode in momentum space, but it has no well-defined local energy density -- the integral diverges. Gravity, on the other hand, is a local theory: Einstein's equations need $T_{\mu\nu}(\mathbf{x})$, the energy density at each point in space.

This tension -- a momentum-space vacuum being asked a position-space question -- is the starting point for the alternative construction in Lesson 4.
