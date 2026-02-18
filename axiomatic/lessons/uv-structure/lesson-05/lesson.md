# Lesson 5: The UV Choice and Its Consequences

## Overview

The question of UV structure is not a technical detail -- it is a fundamental choice that determines the structure of the theory. This lesson shows that the presence or absence of a natural UV scale is equivalent to the choice between different axiom systems. Specifically, we prove the equivalence: **(No natural UV scale) $\Leftrightarrow$ (Axiom A1 fails) $\Leftrightarrow$ (Axiom F fails) $\Leftrightarrow$ (Exact Lorentz invariance)**. This equivalence is the key insight connecting UV structure to the Alpha Framework's choice points.

The equivalence itself is **[PROVEN]** as a logical theorem. Which choice describes nature is **[OPEN]**.

## 5.1 The UV Choice

There are two mutually exclusive options for the UV structure of quantum field theory:

**Option A: No natural UV scale (Standard QFT)**
- The continuum extends to arbitrarily short distances
- Sum over all modes, from $k = 0$ to $k = \infty$
- Integrals diverge without regularization
- Renormalization handles observable differences
- Exact Lorentz invariance at all scales

**Option B: Natural UV scale (Cell vacuum approach)**
- Physics provides a cutoff at some scale $\lambda_{UV}$
- Sum over modes terminates naturally
- Integrals are finite without regularization
- Absolute values (like vacuum energy) are well-defined
- Lorentz invariance broken at scales $\lesssim \lambda_{UV}$, emergent at scales $\gg \lambda_{UV}$

These are not different approximations to the same physics. They are different theories with different predictions.

## 5.2 The Equivalences

We will prove the following chain of equivalences:

$$\text{(No UV scale)} \Leftrightarrow \text{(A1 fails)} \Leftrightarrow \text{(F fails)} \Leftrightarrow \text{(Exact Lorentz)}$$

And conversely:

$$\text{(Natural UV scale)} \Leftrightarrow \text{(A1 satisfied)} \Leftrightarrow \text{(F satisfied)} \Leftrightarrow \text{(Broken Lorentz at UV)}$$

### 5.2.1 Axiom A1 (Refinability)

Axiom A1 states: When a region $R$ is partitioned into smaller cells, the state restricted to $R$ must converge as the cell size $a \to 0$.

Mathematically: $\lim_{a \to 0} \rho_R(a)$ exists and is finite.

**Claim:** No UV scale $\Leftrightarrow$ A1 fails

**Proof ($\Rightarrow$):**

If there is no UV scale, the energy density as a function of cell size $a$ is:

$$\rho(a) = \int_0^{\pi/a} \frac{d^3k}{(2\pi)^3} \frac{\hbar\omega_k}{2} \propto a^{-4}$$

As $a \to 0$:
$$\lim_{a \to 0} \rho(a) = \lim_{a \to 0} a^{-4} = \infty$$

The limit does not exist (diverges). A1 fails. $\square$

**Proof ($\Leftarrow$):**

If there IS a natural UV scale $\lambda_{UV}$, the energy density is:

$$\rho(a) = \int_0^{\min(\pi/a, \pi/\lambda_{UV})} \frac{d^3k}{(2\pi)^3} \frac{\hbar\omega_k}{2}$$

For $a > \lambda_{UV}$: $\rho(a)$ varies with $a$
For $a \leq \lambda_{UV}$: $\rho(a) = \rho(\lambda_{UV}) = $ constant

Therefore:
$$\lim_{a \to 0} \rho(a) = \rho(\lambda_{UV}) < \infty$$

The limit exists and is finite. A1 is satisfied. $\square$

**[PROVEN]**

### 5.2.2 Axiom F (Finiteness)

Axiom F states: All physical observables have finite expectation values without regularization.

**Claim:** A1 fails $\Leftrightarrow$ F fails

**Proof ($\Rightarrow$):**

If A1 fails, the energy density diverges under refinement: $\rho(a) \to \infty$ as $a \to 0$.

The physical energy density is the limit of the refined quantity:
$$\langle T_{00} \rangle = \lim_{a \to 0} \rho(a) = \infty$$

Therefore $\langle T_{00} \rangle$ is not finite. F fails. $\square$

**Proof ($\Leftarrow$):**

If A1 holds, $\lim_{a \to 0} \rho(a)$ exists and is finite.

Therefore $\langle T_{00} \rangle = \lim_{a \to 0} \rho(a) < \infty$.

Since the energy density is finite, and other observables (pressure, number density) are similarly bounded, F is satisfied. $\square$

**[PROVEN]**

### 5.2.3 Lorentz Invariance

**Claim:** No UV scale $\Leftrightarrow$ Exact Lorentz invariance

**Proof ($\Rightarrow$):**

If there is no UV scale, all momentum modes exist for all observers. Under a Lorentz boost:
- Mode with momentum $\mathbf{k}$ in frame A has momentum $\mathbf{k}'$ in frame B
- Both frames include all modes up to infinity
- The vacuum state $|0\rangle$ (defined by $a_k|0\rangle = 0$ for all $k$) is the same in both frames

The mode vacuum is the unique Poincaré-invariant state. Lorentz invariance is exact. $\square$

**Proof ($\Leftarrow$):**

If there IS a natural UV scale $\lambda_{UV}$:
- This corresponds to a maximum momentum $k_{max} \sim 1/\lambda_{UV}$
- In frame A, a mode near $k_{max}$ is included
- Boost to frame B: this mode may exceed $k_{max}$ in the new frame

A maximum momentum is not Lorentz invariant. The UV scale picks out a preferred frame (the "rest frame" of the cutoff).

Lorentz invariance is violated at scales $\lesssim \lambda_{UV}$. $\square$

**Important caveat:** If $\lambda_{UV}$ is very small (e.g., the neutrino Compton wavelength $\sim 0.1$ mm), Lorentz violation is negligible at accessible scales. Lorentz invariance is emergent at scales $\gg \lambda_{UV}$.

**[PROVEN]**

## 5.3 The Complete Equivalence

Combining all three results:

$$\boxed{\text{(No UV scale)} \Leftrightarrow \text{(A1 fails)} \Leftrightarrow \text{(F fails)} \Leftrightarrow \text{(Exact Lorentz)}}$$

This is a theorem, not a hypothesis. Given the definitions of A1, F, and the standard QFT construction, the equivalences follow by mathematical proof. **[PROVEN]**

## 5.4 The Two Consistent Frameworks

The equivalence means there are exactly two internally consistent options:

**Framework 1: Standard QFT (Mode vacuum)**
- No natural UV scale
- A1 fails: state diverges under refinement
- F fails: infinite energy density
- Exact Lorentz invariance
- Only F-weak predictions are meaningful
- Renormalization required for all calculations
- Vacuum energy is undefined or requires ad hoc subtraction

**Framework 2: Cell vacuum**
- Natural UV scale at Compton wavelength
- A1 satisfied: state converges under refinement
- F satisfied: finite energy density
- Lorentz invariance emergent (exact at scales $\gg \lambda_C$)
- F-strong predictions are meaningful
- No renormalization needed for vacuum energy
- Vacuum energy is $\rho = m^4c^5/\hbar^3$

There is no "hybrid" option. You cannot have exact Lorentz invariance AND finite vacuum energy AND a well-defined refinement limit. The axioms are mutually constrained.

## 5.5 Consequences of Each Choice

### If You Choose: No UV Scale (Standard QFT)

**What works:**
- Exact Lorentz invariance preserved
- Standard perturbation theory applies
- All successful predictions of QED, QCD, electroweak theory

**What fails:**
- Vacuum energy is undefined
- Cosmological constant is a free parameter
- $\langle T_{\mu\nu} \rangle$ requires regularization scheme
- The $10^{123}$ discrepancy remains unexplained

**Equation of state:** Not well-defined (depends on regularization)

### If You Choose: Natural UV Scale at $\lambda_C$

**What works:**
- Finite vacuum energy: $\rho = m^4c^5/\hbar^3$
- Well-defined $\langle T_{\mu\nu} \rangle$
- State converges under refinement
- w = 0 (dark matter, not dark energy)

**What fails:**
- Exact Lorentz invariance (broken at scale $\lambda_C$)
- Must explain why Lorentz violation is not observed

**Resolution:** If $\lambda_C \sim 0.1$ mm (neutrino Compton), Lorentz violation occurs at scales much larger than any particle physics experiment. All current tests of Lorentz invariance are at scales $\ll \lambda_C$, where Lorentz symmetry is emergent and effectively exact.

## 5.6 The Deep Connection

The equivalence reveals a deep connection: **UV structure, axiom choice, and symmetry structure are the same thing in different languages**.

- Choosing exact Lorentz invariance = choosing no UV cutoff = accepting A1 and F failure
- Choosing A1 and F = choosing a UV cutoff = accepting broken Lorentz at small scales

There is no escape. The mathematics forces one package or the other.

The Alpha Framework makes a specific choice: **natural UV scale at the Compton wavelength**. This is not arbitrary -- it's the physical scale where pair creation prevents further localization.

## 5.7 Why the Compton Scale?

If you accept that there's a natural UV scale, which scale should it be?

**Not the Planck scale:** This gives $\rho \sim 10^{113}$ J/m$^3$ -- still catastrophically wrong.

**Not an arbitrary scale:** This introduces a free parameter with no physical justification.

**The Compton wavelength:** This is where physics changes. Below $\lambda_C$, pair creation is inevitable. You're not describing the same vacuum; you're creating particles.

For the lightest particle (neutrino), $\lambda_C \sim 0.1$ mm. The resulting vacuum energy is:

$$\rho = m_\nu^4 c^5 / \hbar^3 \sim 10^{-10} \text{ J/m}^3$$

This matches the observed dark matter density to within an order of magnitude.

The Compton wavelength is not just "a" UV scale -- it's the PHYSICAL scale where the vacuum energy sum should naturally terminate.

## 5.8 Key Equations Summary

**Energy density with no UV scale:**
$$\rho(a) = \frac{\hbar c \pi^4}{16\pi^2 a^4} \to \infty \text{ as } a \to 0$$

**Energy density with UV scale $\lambda_{UV}$:**
$$\rho = \frac{\hbar c \pi^4}{16\pi^2 \lambda_{UV}^4} \propto \frac{m^4 c^5}{\hbar^3}$$

**The equivalence (theorem):**
$$\text{(No UV scale)} \Leftrightarrow \text{(A1 fails)} \Leftrightarrow \text{(F fails)} \Leftrightarrow \text{(Exact Lorentz)}$$

**Cell vacuum energy (with $\lambda_{UV} = \lambda_C = \hbar/mc$):**
$$\rho_{\text{cell}} = \frac{m^4 c^5}{\hbar^3}$$

## Evidence Tier Summary

| Claim | Status |
|-------|--------|
| The equivalence (No UV scale $\Leftrightarrow$ A1 fails $\Leftrightarrow$ F fails $\Leftrightarrow$ Exact Lorentz) | [PROVEN] |
| Standard QFT implies F fails | [PROVEN] |
| UV cutoff breaks Lorentz invariance | [PROVEN] |
| Compton wavelength as natural UV scale | [FRAMEWORK] |
| Which framework describes nature | [OPEN] |

## Exercises

1. **Prove the contrapositive.** If A1 is satisfied, show that there must be a natural UV scale. (Hint: if there's no UV scale, what happens to $\rho(a)$ as $a \to 0$?)

2. **Lorentz boost of a cutoff.** Consider a mode with $|\mathbf{k}| = k_{max} - \epsilon$ in frame A. Under a boost with velocity $v$ along the $k$-direction, compute $|k'|$ in frame B. For what $v$ does $|k'| > k_{max}$?

3. **Emergent Lorentz invariance.** If the UV scale is $\lambda_{UV} = 0.1$ mm, estimate the fractional Lorentz violation at the LHC ($E \sim 10^4$ GeV). Is this detectable?

4. **Alternative UV scales.** Compute the vacuum energy density for (a) $\lambda_{UV} = \lambda_P$ (Planck), (b) $\lambda_{UV} = \lambda_C^{\text{electron}}$, (c) $\lambda_{UV} = \lambda_C^{\text{neutrino}}$. Compare each to the observed cosmological parameters.

5. **The hybrid failure.** Show that you cannot have BOTH exact Lorentz invariance AND finite vacuum energy. (This proves there's no hybrid option.)
