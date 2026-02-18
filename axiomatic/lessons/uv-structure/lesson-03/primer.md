# Primer: How Physics Has Handled the UV Problem

## The Four Strategies

Physicists have developed four main approaches to the UV divergence problem:

### 1. Hard Cutoff
Just stop the integral at some maximum momentum $\Lambda$:
$$\rho = \int_0^{\Lambda} \frac{d^3k}{(2\pi)^3} \frac{\hbar\omega_k}{2}$$

Simple, but arbitrary. And it breaks Lorentz invariance -- a maximum momentum picks out a preferred reference frame.

### 2. Dimensional Regularization
Do the integral in $d$ dimensions instead of 4. The divergence appears as a pole at $d = 4$:
$$\rho \sim \frac{1}{d-4} + \text{finite}$$

Preserves symmetries, but just hides the infinity in a pole. You still have to deal with it.

### 3. Renormalization
The key insight: we measure DIFFERENCES, not absolute values. Subtract the vacuum energy from everything:
$$\Delta E = E_{\text{state}} - E_{\text{vacuum}}$$

Both terms are infinite, but the difference is finite. Works beautifully for particle physics (QED predictions match experiment to 12 decimal places).

But gravity couples to ABSOLUTE energy, not differences. For the vacuum energy problem, renormalization doesn't help.

### 4. Natural UV Scales
Maybe physics itself provides a cutoff:
- Crystal lattice spacing (for phonons)
- Compton wavelength (where pair creation kicks in)
- Planck length (where quantum gravity matters)

## The Key Distinction: F-weak vs F-strong

**F-weak predictions** are energy differences: mass splittings, scattering cross-sections, decay rates. Renormalization handles these perfectly.

**F-strong predictions** are absolute values: vacuum energy density, total gravitational mass. Renormalization fails here.

The cosmological constant problem is an F-strong problem. Standard methods don't solve it. That's why the Alpha Framework explores whether there's a natural UV scale that makes the vacuum energy finite without arbitrary subtraction.
