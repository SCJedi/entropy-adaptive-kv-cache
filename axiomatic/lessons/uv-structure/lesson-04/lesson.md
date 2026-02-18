# Lesson 4: Natural UV Scales in Physics

## Overview

The question of whether physics has a natural ultraviolet scale is not abstract. There are specific length scales where the rules of physics change -- where one description breaks down and another must take over. This lesson examines four natural UV scales: the Planck length, the Compton wavelength, the de Broglie wavelength, and the string length. Each marks a physical threshold where attempting to probe smaller distances fundamentally changes what you're observing.

The Planck, Compton, and de Broglie scales are **[ESTABLISHED]** physics. String theory scales are **[FRAMEWORK]** -- theoretically motivated but experimentally unconfirmed.

## 4.1 The Planck Scale: Quantum Gravity's Threshold

The Planck length is constructed from the three fundamental constants that govern quantum gravity:

$$\lambda_P = \sqrt{\frac{\hbar G}{c^3}} \approx 1.616 \times 10^{-35} \text{ m}$$

**Physical meaning:** At this scale, quantum fluctuations in spacetime geometry become comparable to the geometry itself. The metric tensor $g_{\mu\nu}$ undergoes quantum fluctuations of order 1. Classical general relativity breaks down.

**How to derive it:**

The Schwarzschild radius of a mass $M$ is $r_S = 2GM/c^2$.
The Compton wavelength of a mass $M$ is $\lambda_C = \hbar/Mc$.

Set them equal: when does the Schwarzschild radius equal the Compton wavelength?

$$\frac{2GM}{c^2} = \frac{\hbar}{Mc}$$

Solving for $M$:
$$M = \sqrt{\frac{\hbar c}{2G}} \approx M_P \text{ (Planck mass)}$$

The corresponding length scale is:
$$\lambda_P = \sqrt{\frac{\hbar G}{c^3}}$$

At this mass, a particle is its own black hole. Below this length, the concepts of "particle" and "black hole" are indistinguishable. Spacetime itself becomes fundamentally quantum.

**Associated quantities:**

| Quantity | Symbol | Value |
|----------|--------|-------|
| Planck length | $\lambda_P$ | $1.616 \times 10^{-35}$ m |
| Planck mass | $M_P$ | $2.176 \times 10^{-8}$ kg = $1.22 \times 10^{19}$ GeV/$c^2$ |
| Planck energy | $E_P$ | $1.956 \times 10^9$ J = $1.22 \times 10^{19}$ GeV |
| Planck time | $t_P$ | $5.391 \times 10^{-44}$ s |

**Current experimental status:**

We are approximately 16 orders of magnitude away from the Planck energy:
- LHC: $\sim 10^4$ GeV
- Cosmic rays (highest observed): $\sim 10^{11}$ GeV
- Planck energy: $\sim 10^{19}$ GeV

There is no prospect of directly probing Planck-scale physics with accelerators. However, cosmological observations (primordial gravitational waves, CMB polarization) may carry indirect signatures. **[ESTABLISHED]**

## 4.2 The Compton Wavelength: The Pair Creation Threshold

For any particle of mass $m$, the Compton wavelength is:

$$\lambda_C = \frac{\hbar}{mc}$$

**Physical meaning:** This is the scale where you cannot localize a particle more precisely without creating particle-antiparticle pairs.

**Why pair creation?**

To localize a particle to within $\Delta x$, you need a probe with momentum uncertainty $\Delta p \geq \hbar/\Delta x$ (Heisenberg). For $\Delta x < \lambda_C$:

$$\Delta p > \frac{\hbar}{\lambda_C} = mc$$

The probe energy exceeds $mc^2$, which is enough to create a new particle-antiparticle pair. You're no longer probing the original particle; you're creating new particles.

**Numerical examples:**

| Particle | Mass | Compton wavelength |
|----------|------|-------------------|
| Electron | 0.511 MeV | $2.43 \times 10^{-12}$ m |
| Proton | 938 MeV | $1.32 \times 10^{-15}$ m |
| W boson | 80.4 GeV | $1.55 \times 10^{-18}$ m |
| Higgs boson | 125 GeV | $9.9 \times 10^{-19}$ m |
| Neutrino (m = 2 meV) | 2 meV | $\sim 10^{-4}$ m = 0.1 mm |
| Neutrino (m = 0.05 eV) | 50 meV | $\sim 4 \times 10^{-6}$ m = 4 $\mu$m |

The remarkable fact: the Compton wavelength of the lightest neutrino is macroscopic (sub-millimeter). This is the largest Compton wavelength of any known particle. **[ESTABLISHED]**

**Physical interpretation:**

Below $\lambda_C$, single-particle quantum mechanics fails. The number of particles is not conserved. You must use quantum field theory, where particles can be created and destroyed.

The Compton wavelength marks the boundary between:
- **Non-relativistic QM** (distances $\gg \lambda_C$): Fixed particle number, Schrödinger equation
- **Relativistic QFT** (distances $\lesssim \lambda_C$): Variable particle number, field operators

**Relevance for UV structure:**

If you try to describe the vacuum at scales smaller than $\lambda_C$, you're not refining your description of the same vacuum -- you're probing a regime where particle creation is inevitable. The vacuum at scale $a < \lambda_C$ is not the same as the vacuum at scale $a > \lambda_C$.

This is why the Compton wavelength is a candidate for a natural UV cutoff for the vacuum energy. **[FRAMEWORK]**

## 4.3 The de Broglie Wavelength: The Quantum Threshold

For a particle with momentum $p$, the de Broglie wavelength is:

$$\lambda_{dB} = \frac{h}{p} = \frac{2\pi\hbar}{p}$$

**Physical meaning:** This is the scale where quantum wave effects become important for that particle.

- If $\lambda_{dB}$ is much smaller than the system size: classical behavior
- If $\lambda_{dB}$ is comparable to or larger than the system size: quantum interference, diffraction, tunneling

**For a thermal particle at temperature $T$:**

$$\lambda_{dB}^{\text{thermal}} = \frac{h}{\sqrt{2\pi m k_B T}}$$

At room temperature (300 K):
- Electron: $\lambda_{dB} \approx 7$ nm
- Proton: $\lambda_{dB} \approx 0.17$ nm
- Atom (mass 50 amu): $\lambda_{dB} \approx 0.05$ nm

**Comparison to Compton wavelength:**

For a non-relativistic particle ($p \ll mc$):
$$\lambda_{dB} = \frac{\hbar}{p} \gg \frac{\hbar}{mc} = \lambda_C$$

The de Broglie wavelength is always larger than the Compton wavelength for non-relativistic particles. As $p \to mc$, they become comparable.

**Relevance for UV structure:**

The de Broglie wavelength is a property of a particle's motion, not of space itself. It tells you when quantum effects matter for a specific particle, but it's not a fundamental length scale of the vacuum. **[ESTABLISHED]**

## 4.4 The String Scale (Speculative)

In string theory, fundamental objects are not point particles but one-dimensional strings. The string length is:

$$l_s = \sqrt{\alpha'} \sim 10^{-34} \text{ to } 10^{-35} \text{ m}$$

where $\alpha'$ is the Regge slope parameter.

**Physical meaning (in string theory):**

Below the string scale, point-particle physics fails. Particles are resolved as extended strings. The concept of "smaller distance" becomes ambiguous due to T-duality (exchanging $R \leftrightarrow \alpha'/R$).

**Current status:**

String theory is a candidate for quantum gravity and grand unification, but:
- No experimental confirmation
- The string scale is not precisely determined (depends on the compactification scheme)
- Could be anywhere from near-Planck to possibly lower

**[FRAMEWORK]** -- theoretically motivated but unconfirmed.

## 4.5 Hierarchy of Natural Scales

The natural UV scales form a hierarchy:

$$\lambda_{dB} \gg \lambda_C \gtrsim l_s \gtrsim \lambda_P$$

More precisely, for everyday particles and measurements:

| Scale | Typical value | What changes below it |
|-------|---------------|----------------------|
| de Broglie | nm to mm (depends on $p$) | Quantum wave effects important |
| Compton | $10^{-12}$ to $10^{-4}$ m | Pair creation possible |
| String | $\sim 10^{-34}$ m (speculative) | Point particles become strings |
| Planck | $10^{-35}$ m | Spacetime becomes quantum |

Each scale marks a physical transition. Below it, you're in a different regime with different rules. **[ESTABLISHED]** for Compton/Planck; **[FRAMEWORK]** for string.

## 4.6 The Compton Scale as Vacuum UV Cutoff

The cell vacuum hypothesis proposes that the Compton wavelength of the lightest particle (the lightest neutrino) provides a natural UV cutoff for the vacuum energy:

$$\lambda_C^{\text{neutrino}} = \frac{\hbar}{m_\nu c} \approx 0.1 \text{ mm (for } m_\nu \approx 2 \text{ meV)}$$

**Why this scale?**

1. **Physical barrier:** Below $\lambda_C$, you cannot describe the vacuum without pair creation. The vacuum energy at smaller scales is not the same physical quantity.

2. **Natural, not arbitrary:** The scale is determined by the particle mass, not imposed by hand.

3. **Largest relevant scale:** The lightest particle has the largest Compton wavelength. It provides the "IR cutoff" for the UV problem -- the scale where the vacuum energy contribution stops.

**Resulting energy density:**

$$\rho = \frac{m^4 c^5}{\hbar^3}$$

For $m = 2$ meV:
$$\rho \approx 6 \times 10^{-10} \text{ J/m}^3$$

This is within an order of magnitude of the observed dark matter density. **[FRAMEWORK]**

## 4.7 Key Equations Summary

**Planck length:**
$$\lambda_P = \sqrt{\frac{\hbar G}{c^3}} \approx 1.62 \times 10^{-35} \text{ m}$$

**Planck mass:**
$$M_P = \sqrt{\frac{\hbar c}{G}} \approx 2.18 \times 10^{-8} \text{ kg}$$

**Planck energy:**
$$E_P = M_P c^2 = \sqrt{\frac{\hbar c^5}{G}} \approx 1.22 \times 10^{19} \text{ GeV}$$

**Compton wavelength:**
$$\lambda_C = \frac{\hbar}{mc}$$

**de Broglie wavelength:**
$$\lambda_{dB} = \frac{h}{p}$$

**Thermal de Broglie wavelength:**
$$\lambda_{dB}^{th} = \frac{h}{\sqrt{2\pi m k_B T}}$$

**String length (speculative):**
$$l_s \sim 10^{-34} \text{ m}$$

## Evidence Tier Summary

| Claim | Status |
|-------|--------|
| Planck scale is where quantum gravity matters | [ESTABLISHED] |
| We cannot probe Planck scale directly | [ESTABLISHED] |
| Compton wavelength marks pair creation threshold | [ESTABLISHED] |
| de Broglie wavelength marks quantum threshold | [ESTABLISHED] |
| String scale | [FRAMEWORK] |
| Compton wavelength as vacuum UV cutoff | [FRAMEWORK] |

## Exercises

1. **Planck scale derivation.** Derive the Planck length by demanding that the Compton wavelength equals the Schwarzschild radius. What mass satisfies this condition?

2. **Compton vs de Broglie.** For an electron moving at 0.1$c$, compute both the Compton wavelength and the de Broglie wavelength. Which is larger? What happens at $v \to c$?

3. **Neutrino Compton wavelength.** For a neutrino with mass 50 meV (the heavier mass eigenstate), compute $\lambda_C$. Compare with the size of an atom, a bacterium, and a human hair.

4. **Energy scale matching.** At what particle mass does the Compton wavelength equal 1 meter? What common particle (if any) has a mass in this range? What would the vacuum energy density be if this were the UV cutoff?

5. **The hierarchy problem.** The ratio $\lambda_P/\lambda_C^{\text{electron}} \approx 10^{23}$. This huge hierarchy between the Planck scale and the electroweak scale is one of the major puzzles in physics. If there were new physics at an intermediate scale $\Lambda$, how would you estimate $\Lambda$ from naturalness arguments?
