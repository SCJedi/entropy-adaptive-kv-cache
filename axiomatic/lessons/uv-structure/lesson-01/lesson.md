# Lesson 1: What Is UV Structure?

## Overview

Physics operates across an enormous range of scales, from the Planck length ($10^{-35}$ m) to the observable universe ($10^{26}$ m) -- a span of 61 orders of magnitude. Understanding how physics at small scales connects to physics at large scales is one of the central challenges of theoretical physics. The terms "UV" (ultraviolet) and "IR" (infrared) come from optics but have become the standard vocabulary for discussing this scale hierarchy in quantum field theory.

This lesson establishes the fundamental relationship between wavelength, energy, and distance scales, explains why small-scale physics matters for large-scale predictions, and introduces the concept of "UV completion" -- what happens to a theory as you probe smaller and smaller distances.

All claims in this lesson are **[ESTABLISHED]** -- standard results in quantum mechanics and relativity.

## 1.1 The UV-IR Vocabulary

The terms "ultraviolet" and "infrared" originated in optics, referring to light beyond the visible spectrum:
- **Ultraviolet (UV)**: shorter wavelengths than visible light, higher frequencies
- **Infrared (IR)**: longer wavelengths than visible light, lower frequencies

In quantum field theory, these terms have been generalized:

| Term | Wavelength | Energy | Distance | Regime |
|------|------------|--------|----------|--------|
| **UV** | Short | High | Small | Quantum, microscopic |
| **IR** | Long | Low | Large | Classical, macroscopic |

The reason for this vocabulary is the fundamental relationship between wavelength, frequency, and energy. **[ESTABLISHED]**

## 1.2 The Energy-Wavelength Relation

The connection between wavelength and energy is one of the most important relationships in quantum physics. It comes from two equations:

**De Broglie relation** (wave-particle duality):
$$p = \frac{h}{\lambda} = \frac{\hbar \cdot 2\pi}{\lambda}$$

**Relativistic energy-momentum relation** (for massless particles):
$$E = pc$$

Combining these for a photon:
$$E = \frac{hc}{\lambda}$$

This is the central equation: **energy is inversely proportional to wavelength**.

For massive particles with momentum $p \ll mc$:
$$E \approx mc^2 + \frac{p^2}{2m} = mc^2 + \frac{h^2}{2m\lambda^2}$$

The key insight: **shorter wavelengths mean higher energies**. To probe small distances, you need high-energy probes. This is why particle accelerators must reach higher and higher energies to explore smaller and smaller scales. **[ESTABLISHED]**

## 1.3 The Compton Wavelength: Where Quantum Field Theory Begins

For any massive particle, there is a characteristic length scale called the Compton wavelength:

$$\lambda_C = \frac{\hbar}{mc}$$

This is the wavelength where the energy of a photon ($E = hc/\lambda$) equals the rest mass energy of the particle ($E = mc^2$). At wavelengths shorter than $\lambda_C$:
- Photons have enough energy to create particle-antiparticle pairs
- You cannot localize a particle more precisely than $\lambda_C$ without creating new particles
- Single-particle quantum mechanics breaks down; quantum field theory is required

**Numerical examples:**

| Particle | Mass | Compton wavelength $\lambda_C$ |
|----------|------|-------------------------------|
| Electron | 0.511 MeV/$c^2$ | $2.43 \times 10^{-12}$ m |
| Proton | 938 MeV/$c^2$ | $1.32 \times 10^{-15}$ m |
| Lightest neutrino | ~2 meV/$c^2$ | ~$1 \times 10^{-4}$ m = 0.1 mm |
| Planck mass | $1.22 \times 10^{19}$ GeV/$c^2$ | $1.62 \times 10^{-35}$ m |

The Compton wavelength marks the boundary between non-relativistic quantum mechanics (scales $\gg \lambda_C$) and relativistic quantum field theory (scales $\lesssim \lambda_C$). **[ESTABLISHED]**

## 1.4 The de Broglie Wavelength: Where Quantum Effects Appear

For a particle with momentum $p$, the de Broglie wavelength is:

$$\lambda_{dB} = \frac{h}{p}$$

This is the scale at which quantum wave effects become important for that particle. When the de Broglie wavelength is:
- Much smaller than the system size: classical behavior
- Comparable to or larger than the system size: quantum behavior

For a thermal particle at temperature $T$:
$$\lambda_{dB} \sim \frac{h}{\sqrt{2\pi m k_B T}}$$

**Example:** At room temperature (300 K), an electron has $\lambda_{dB} \approx 7$ nm. This is why electron microscopes can resolve much finer details than optical microscopes. **[ESTABLISHED]**

## 1.5 The Planck Scale: Where Gravity Becomes Quantum

The Planck length is constructed from the three fundamental constants that govern quantum gravity: $\hbar$ (quantum mechanics), $c$ (relativity), and $G$ (gravity):

$$\lambda_P = \sqrt{\frac{\hbar G}{c^3}} \approx 1.62 \times 10^{-35} \text{ m}$$

The corresponding Planck energy is:
$$E_P = \sqrt{\frac{\hbar c^5}{G}} \approx 1.22 \times 10^{19} \text{ GeV}$$

At the Planck scale:
- Gravitational effects become as strong as quantum effects
- Spacetime itself may become discrete or foamy
- Classical general relativity breaks down
- A theory of quantum gravity is required

We are currently 16 orders of magnitude away from probing the Planck scale directly. The Large Hadron Collider reaches ~$10^4$ GeV; the Planck scale is at ~$10^{19}$ GeV. **[ESTABLISHED]**

## 1.6 The Scale Hierarchy

Physics organizes itself into a hierarchy of scales, each governed by different effective theories:

| Scale | Length | Energy | Dominant physics |
|-------|--------|--------|------------------|
| Planck | $10^{-35}$ m | $10^{19}$ GeV | Quantum gravity |
| GUT | $10^{-31}$ m | $10^{15}$ GeV | Grand unification |
| Electroweak | $10^{-18}$ m | $10^{2}$ GeV | Standard Model |
| Nuclear | $10^{-15}$ m | $1$ GeV | QCD, nuclear physics |
| Atomic | $10^{-10}$ m | $10$ eV | Atomic physics |
| Molecular | $10^{-9}$ m | $0.1$ eV | Chemistry |
| Human | $1$ m | $10^{-9}$ eV | Classical mechanics |
| Cosmic | $10^{26}$ m | $10^{-42}$ eV | Cosmology |

The remarkable fact is that physics at each scale can be understood largely independently of physics at much smaller scales. This is the principle of **decoupling**: high-energy (UV) physics affects low-energy (IR) physics only through a finite number of parameters. **[ESTABLISHED]**

## 1.7 UV Completion: What Happens at Small Scales?

A theory is said to be "UV complete" if it remains valid and well-defined at arbitrarily short distances (high energies). Most theories are NOT UV complete:

**Effective field theories** are valid only up to some energy scale $\Lambda$:
- Fermi theory of weak interactions: valid up to ~100 GeV, fails at higher energies
- Chiral perturbation theory: valid up to ~1 GeV
- General relativity (as a quantum theory): valid up to ~$10^{19}$ GeV

At the scale $\Lambda$, "new physics" must appear to make the theory consistent. This new physics is the "UV completion."

**Examples of UV completion:**
- Fermi theory $\to$ electroweak theory (W and Z bosons appear at ~100 GeV)
- QED $\to$ Standard Model (weak interactions become important at ~100 GeV)
- Standard Model $\to$ ??? (new physics at ~$10^{3}$ to $10^{19}$ GeV)

The question "what is the UV completion of the Standard Model?" is one of the central open problems in particle physics. **[ESTABLISHED]**

## 1.8 Why Small Scales Determine Large Scales

In quantum field theory, physics at all scales contributes to observables. When you calculate a loop diagram in perturbation theory, you must integrate over all momenta:

$$\int_0^{\Lambda} \frac{d^4k}{(2\pi)^4} \times (\text{integrand})$$

If the integral diverges as $\Lambda \to \infty$, you have a UV divergence. This is not a mathematical artifact -- it reflects the physical fact that modes at ALL scales contribute to the observable.

**The key insight:** what happens at small scales (UV) cannot be ignored when calculating physics at large scales (IR). The sum over all modes, from IR to UV, determines the observable value.

This is why UV structure matters: the physics of arbitrarily small scales feeds into predictions at accessible scales through these sums and integrals. **[ESTABLISHED]**

## 1.9 The UV Problem in Brief

The fundamental UV problem is this: if you sum contributions from ALL scales down to zero wavelength, you typically get infinity:

$$\sum_{\text{all modes}} (\text{contribution per mode}) \to \infty$$

This happens because:
1. There are MORE modes at high $k$ (the density of states grows as $k^2$)
2. Each mode contributes MORE energy at high $k$ (energy $\sim k$)

The product grows faster than any convergent sum. The integral $\int_0^\infty k^3 dk$ diverges.

Different approaches to this problem:
- **Renormalization:** Accept the infinity, compute differences that are finite
- **Cutoff:** Stop the sum at some maximum $k_{max}$ (but which one?)
- **Natural UV scale:** Physics itself provides a scale where the sum naturally terminates

The third option is what the Alpha Framework investigates. **[ESTABLISHED]** for the problem; **[FRAMEWORK]** for the proposed resolution.

## 1.10 Natural UV Scales

Some physical situations provide a natural UV cutoff without imposing one by hand:

**Crystal lattice:** In a solid, the atomic spacing $a$ provides a natural UV scale. Wavelengths shorter than $a$ do not propagate through the lattice. The Debye cutoff $\omega_D \sim v/a$ naturally limits phonon sums.

**Pair creation threshold:** At the Compton wavelength $\lambda_C = \hbar/mc$, attempts to localize a particle create particle-antiparticle pairs. This is a physical barrier to probing shorter scales with that particle.

**Planck scale:** Quantum gravity effects at $\lambda_P \sim 10^{-35}$ m may fundamentally discretize spacetime, providing an absolute UV cutoff.

The question for any physical system is: **does it have a natural UV scale, or does the continuum extend all the way down?** **[ESTABLISHED]**

## 1.11 Evidence Tier Summary

| Claim | Status |
|-------|--------|
| UV = high energy = short wavelength | [ESTABLISHED] |
| $E = hc/\lambda$ for photons | [ESTABLISHED] |
| Compton wavelength $\lambda_C = \hbar/mc$ | [ESTABLISHED] |
| Planck length $\lambda_P = \sqrt{\hbar G/c^3}$ | [ESTABLISHED] |
| Scale hierarchy from Planck to cosmic | [ESTABLISHED] |
| UV divergences in QFT require treatment | [ESTABLISHED] |
| Principle of decoupling | [ESTABLISHED] |

## 1.12 Key Equations Summary

**Energy-wavelength relation (photon):**
$$E = \frac{hc}{\lambda}$$

**Compton wavelength:**
$$\lambda_C = \frac{\hbar}{mc}$$

**De Broglie wavelength:**
$$\lambda_{dB} = \frac{h}{p}$$

**Planck length:**
$$\lambda_P = \sqrt{\frac{\hbar G}{c^3}} \approx 1.62 \times 10^{-35} \text{ m}$$

**Planck energy:**
$$E_P = \sqrt{\frac{\hbar c^5}{G}} \approx 1.22 \times 10^{19} \text{ GeV} \approx 2 \times 10^9 \text{ J}$$

## 1.13 Looking Ahead

This lesson established what UV and IR mean, and why the physics of small scales matters. The next lesson asks: **why does the UV cause problems?** Specifically, what happens when you sum the zero-point energy of ALL field modes? The answer -- divergence -- is the heart of the cosmological constant problem and the starting point for the Alpha Framework's approach.

## Exercises

1. **Units check.** Verify that $\lambda_P = \sqrt{\hbar G/c^3}$ has units of length. Write out the dimensions of each quantity and show the cancellation.

2. **Compton wavelength calculation.** Compute the Compton wavelength for (a) an electron, (b) a proton, (c) a neutrino with mass 2 meV. Express your answers in meters.

3. **Scale hierarchy.** The Planck length is $10^{-35}$ m and the observable universe is $10^{26}$ m. How many factors of 10 separate them? If each factor of 10 represented 1 cm on a ruler, how long would the ruler need to be?

4. **UV vs IR dominance.** For a massless scalar field, each mode contributes zero-point energy $\hbar\omega_k/2$ where $\omega_k = ck$. Which modes contribute more to the total energy: those with $k < 1$ GeV or those with $k > 1$ GeV? (Hint: count modes in a shell $d^3k = 4\pi k^2 dk$.)

5. **UV completion.** Fermi's theory of beta decay has an interaction term $G_F (\bar{\psi}_e \psi_\nu)(\bar{\psi}_n \psi_p)$ with $G_F \approx 10^{-5}$ GeV$^{-2}$. (a) What are the dimensions of $G_F$? (b) At what energy scale does the dimensionful coupling suggest the theory breaks down? (c) What is the actual UV completion of Fermi theory?
