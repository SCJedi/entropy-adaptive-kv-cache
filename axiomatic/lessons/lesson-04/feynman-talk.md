# The Mode Vacuum — Standard QFT's Ground State
### A Feynman-Voice Lecture

---

All right, we've got the axioms. Now let's see what happens when you try to build a vacuum state using the standard approach from quantum field theory. This is the mode vacuum — the ground state you find in every textbook, the foundation of the Standard Model, the starting point for every Feynman diagram you've ever drawn.

And it's wrong.

Not wrong in the sense that it doesn't work for calculations — it works brilliantly for scattering amplitudes and particle interactions. But wrong in the sense that it has *infinite energy density*, and therefore cannot be the physical vacuum of the real world.

Let me show you why.

## Fock Space: The Standard Framework

Here's how you build quantum field theory in the textbook approach. You start with a field — could be the electromagnetic field, the electron field, the Higgs field, whatever. You decompose it into modes, one for each momentum $\mathbf{k}$. Each mode is a harmonic oscillator, just like we studied in Lesson 1.

For each mode $\mathbf{k}$, you define two operators:

- **Annihilation operator** $a_{\mathbf{k}}$: removes one quantum from mode $\mathbf{k}$
- **Creation operator** $a^\dagger_{\mathbf{k}}$: adds one quantum to mode $\mathbf{k}$

They satisfy the commutation relation:

$$
[a_{\mathbf{k}}, a^\dagger_{\mathbf{k}'}] = \delta_{\mathbf{k}\mathbf{k}'}
$$

**[ESTABLISHED]**. This is just the harmonic oscillator algebra, repeated for each mode.

Now you define the vacuum. What's the lowest-energy state? The state where there are no quanta in any mode. The state annihilated by all the annihilation operators:

$$
a_{\mathbf{k}} |0\rangle_{\text{mode}} = 0 \quad \text{for all } \mathbf{k}
$$

**[ESTABLISHED]**. This is the mode vacuum. It's the ground state of the free-field Hamiltonian. You can't go lower — if you try to apply $a_{\mathbf{k}}$ again, you get zero.

Excited states are built by applying creation operators. One particle: $a^\dagger_{\mathbf{k}} |0\rangle$. Two particles: $a^\dagger_{\mathbf{k}_1} a^\dagger_{\mathbf{k}_2} |0\rangle$. And so on. The full state space — called Fock space — is the span of all these states.

This is the standard construction. It's in every QFT textbook. And it has a fatal flaw.

## The Energy of the Mode Vacuum

Each mode $\mathbf{k}$ is a harmonic oscillator with frequency $\omega_k$. From Lesson 1, we know the ground state energy of a single oscillator is $\hbar\omega/2$. So the total energy of the mode vacuum is the sum over all modes:

$$
E_0^{\text{mode}} = \sum_{\mathbf{k}} \frac{1}{2} \hbar \omega_k
$$

For a massless field, $\omega_k = c|\mathbf{k}|$. So:

$$
E_0^{\text{mode}} = \sum_{\mathbf{k}} \frac{1}{2} \hbar c |\mathbf{k}|
$$

Now, in a box of volume $V$, the allowed momenta are discrete: $\mathbf{k} = (2\pi/L)(n_x, n_y, n_z)$, where $L = V^{1/3}$. As $V \to \infty$, the sum becomes an integral:

$$
\frac{1}{V} \sum_{\mathbf{k}} \to \int \frac{d^3k}{(2\pi)^3}
$$

The energy density is:

$$
\rho_{\text{mode}} = \frac{E_0^{\text{mode}}}{V} = \int \frac{d^3k}{(2\pi)^3} \frac{1}{2} \hbar c |\mathbf{k}|
$$

Switch to spherical coordinates: $d^3k = 4\pi k^2 dk$, where $k = |\mathbf{k}|$:

$$
\rho_{\text{mode}} = \frac{1}{2} \hbar c \int_0^{\infty} \frac{4\pi k^2}{(2\pi)^3} k \, dk = \frac{\hbar c}{4\pi^2} \int_0^{\infty} k^3 \, dk
$$

And there's your problem. This integral diverges. The integrand is $k^3$, which grows without bound. Integrate from $0$ to $\infty$ and you get infinity. **[PROVEN]**.

The mode vacuum has *infinite* energy density.

## The UV Cutoff

Okay, you say, we can't integrate to infinity. Let's put in a cutoff. In the real world, there's some shortest meaningful length scale — maybe the Planck length, maybe the lattice spacing in a discretized version of the theory. Let's call it $a$.

On a lattice with spacing $a$, the shortest wavelength is $\lambda_{\text{min}} = 2a$ (Nyquist limit), which corresponds to a maximum momentum:

$$
k_{\text{max}} = \frac{2\pi}{\lambda_{\text{min}}} = \frac{\pi}{a}
$$

Now the integral becomes:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{4\pi^2} \int_0^{\pi/a} k^3 \, dk = \frac{\hbar c}{4\pi^2} \cdot \frac{1}{4} \left(\frac{\pi}{a}\right)^4
$$

Simplify:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \left(\frac{\pi}{a}\right)^4
$$

**[PROVEN]**. This is exact for a massless field on a lattice with spacing $a$.

Now, what happens as you make $a$ smaller? As you refine your lattice and approach the continuum?

$$
\lim_{a \to 0} \rho_{\text{mode}}(a) = \lim_{a \to 0} \frac{\hbar c}{16\pi^2} \cdot \frac{\pi^4}{a^4} = \infty
$$

The energy density diverges. Quartically. As $a^{-4}$. **[PROVEN]**.

The mode vacuum does not satisfy axiom A1. It does not have a well-defined continuum limit.

## The Numbers

Let's plug in real numbers and see how bad this is. Set $a = \ell_{\text{Planck}} \approx 1.6 \times 10^{-35}$ m — the Planck length, the smallest length scale where we trust physics as we know it.

Using $\hbar c \approx 2 \times 10^{-26}$ J·m:

$$
\rho_{\text{mode}}(\ell_{\text{Planck}}) \approx \frac{2 \times 10^{-26}}{16\pi^2} \cdot \left(\frac{\pi}{1.6 \times 10^{-35}}\right)^4
$$

Crunch the numbers and you get:

$$
\rho_{\text{mode}} \sim 10^{113} \, \text{J/m}^3
$$

**[PROVEN]**. This is the "worst prediction in physics."

Compare this to the observed dark energy density:

$$
\rho_{\text{obs}} \approx 6 \times 10^{-10} \, \text{J/m}^3
$$

The ratio is:

$$
\frac{\rho_{\text{mode}}}{\rho_{\text{obs}}} \sim 10^{123}
$$

One hundred and twenty-three orders of magnitude. That's not a small discrepancy. That's not even close. That's spectacularly, catastrophically wrong.

And this isn't some obscure corner of the theory. This is the *vacuum* — the ground state, the starting point for everything. If the vacuum energy is off by 123 orders of magnitude, something is fundamentally broken.

## What About Mass?

Maybe you're thinking: "Wait, that was for a massless field. What if the field has mass $m$?"

Good question. For a massive field, the dispersion relation is:

$$
\omega_k = c\sqrt{k^2 + (mc/\hbar)^2}
$$

At high $k$ (where $k \gg mc/\hbar$), this behaves like $\omega_k \approx ck$, so you get the same quartic divergence. At low $k$ (where $k \ll mc/\hbar$), it behaves like $\omega_k \approx mc^2/\hbar$, which is finite but still contributes to the vacuum energy.

The full result is:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \left(\frac{\pi}{a}\right)^4 \left[1 + 2(ma)^2 + O((ma)^4)\right]
$$

**[PROVEN]**. The leading divergence is the same: $\sim a^{-4}$. The mass gives a subleading correction, but it doesn't eliminate the divergence.

So no, mass doesn't save you.

## The Standard Fix: Renormalization

All right, so the mode vacuum has infinite energy density. How does standard QFT deal with this?

Simple: subtract it away. Define the **normal-ordered Hamiltonian**:

$$
{:}H{:} = H - \langle 0 | H | 0 \rangle
$$

This is the Hamiltonian with the vacuum energy subtracted. Now:

$$
\langle 0 | {:}H{:} | 0 \rangle = 0
$$

The vacuum has zero energy. Problem solved!

...or is it?

Look, normal ordering works *brilliantly* for calculating scattering amplitudes. When you compute the probability that two particles scatter off each other, you only care about energy *differences*, not absolute energies. Subtracting a constant (even an infinite constant) from the Hamiltonian doesn't change those differences. So for particle physics, normal ordering is perfectly fine.

But for the vacuum energy — the cosmological constant — it's not fine. You're not computing a difference anymore. You're asking: "What is the energy density of empty space?" And if you subtract infinity to get zero, you haven't answered the question. You've just hidden it.

## Why This Is Not Just a Coordinate Choice

Someone might say: "The zero of energy is arbitrary. We can define the vacuum to have zero energy. What's the problem?"

The problem is gravity. In non-gravitational physics, sure, the zero of energy is arbitrary. You can add any constant to the Hamiltonian and the dynamics doesn't change. But in general relativity, *energy density gravitates*. The Einstein field equations are:

$$
G_{\mu\nu} = 8\pi G \, T_{\mu\nu}
$$

where $T_{\mu\nu}$ is the stress-energy tensor, which includes the vacuum energy density $\rho_{\text{vac}}$. If $\rho_{\text{vac}} = \infty$, then spacetime is infinitely curved. The universe doesn't exist.

So you can't just subtract the infinity and declare victory. Gravity forces you to confront the absolute value of the vacuum energy. And the mode vacuum gives infinity, which is unphysical.

## What the Mode Vacuum Does Right

Before we completely dismiss the mode vacuum, let me point out what it does right. It has some beautiful mathematical properties.

**Lorentz invariance:** The mode vacuum looks the same in all inertial frames. If you boost to a moving frame, the vacuum is still the vacuum. **[ESTABLISHED]**. This is because the definition $a_{\mathbf{k}} |0\rangle = 0$ is Lorentz-covariant: a boost changes the modes $\mathbf{k} \to \mathbf{k}'$, but the condition "annihilate all modes" is the same in every frame.

**Translation invariance:** The vacuum looks the same everywhere in space and at all times. It respects the fundamental symmetries of spacetime. **[ESTABLISHED]**.

**Maximal entanglement:** If you partition space into two regions $A$ and $B$, the mode vacuum is maximally entangled across the boundary. The entanglement entropy scales with the boundary area:

$$
S_A \sim c_1 \cdot \frac{A}{a^2}
$$

**[ESTABLISHED]**. This is the area law for entanglement entropy. It's a deep property related to holography and the structure of spacetime.

So the mode vacuum is mathematically elegant. It respects all the symmetries. It's the unique Lorentz-invariant, translation-invariant state in Fock space.

But it has infinite energy density. And that makes it unphysical.

## The Mode Vacuum Fails the Axioms

Let's check the mode vacuum against the seven axioms from Lesson 3.

**P (Propagator Composition):** Does time evolution compose? Yes. The mode vacuum is a stationary state — it's the ground state of the Hamiltonian — so $U(t)|0\rangle = e^{-iE_0 t/\hbar}|0\rangle$, and composition works. **[ESTABLISHED]**.

**Q (Unitarity):** Is time evolution unitary? Yes. $U^\dagger U = I$. No problem. **[ESTABLISHED]**.

**M' (Measurement Consistency):** Does the Born rule apply? Do probabilities sum to 1? Yes. The mode vacuum is a normalized state, and all observables are well-defined (on a lattice). **[ESTABLISHED]**.

**L (Locality):** Are spacelike-separated regions non-signaling? Yes. Operations on region $A$ don't affect statistics on region $B$ if they're spacelike-separated. **[ESTABLISHED]**.

**A0 (Existence):** Does every bounded region have a finite-dimensional state space? On a lattice with finite volume, yes. In the continuum, this becomes tricky — the Hilbert space is infinite-dimensional — but let's give the mode vacuum the benefit of the doubt. **[ARGUABLY YES]**.

**A1 (Refinability):** Do observables converge as $a \to 0$? **NO.** The energy density diverges as $a^{-4}$. The entanglement entropy diverges as $a^{-2}$. The mode vacuum does not have a well-defined continuum limit. **[FAILS]**.

**F (Finiteness):** Are observables finite without renormalization? **NO.** The energy density is infinite. You must subtract it away to get finite answers. **[FAILS]**.

So the mode vacuum satisfies four (or five) of the seven axioms, but it fails A1 and F. And those are the crucial ones for the vacuum energy problem.

## What This Means

The mode vacuum is a *computational* tool, not a *physical* state. It's the right starting point for calculating scattering amplitudes, where only energy differences matter. But it's the wrong state for asking about absolute energy density.

If we demand that the physical vacuum satisfy all seven axioms — including A1 and F — then the mode vacuum is disqualified. We need a different state.

That state is the coherent vacuum, which we'll construct in Lesson 5.

## Why Doesn't Everyone See This?

You might be wondering: if the mode vacuum has infinite energy density, why do physicists use it?

Two reasons.

First, for most purposes, it works. Scattering amplitudes, particle interactions, quantum corrections to forces — these all involve energy *differences*, and the mode vacuum gives the right answers for differences. The infinite vacuum energy cancels out in the calculations.

Second, the attitude has been: "Well, the vacuum energy is infinite, but we can subtract it away. As long as we only compute observable quantities (which are differences), we're fine."

And that's true — for non-gravitational physics. But when you couple QFT to gravity, the absolute vacuum energy matters. It sources the cosmological constant. And if you predict $\rho \sim 10^{113}$ J/m$^3$ when the observed value is $\rho \sim 10^{-10}$ J/m$^3$, you have a problem.

The axiomatic framework says: the problem is that we chose the wrong vacuum. The mode vacuum is mathematically elegant, but physically incorrect. There's a different state — satisfying all seven axioms — that gives a finite vacuum energy. That's the coherent vacuum.

## Looking Ahead

In Lesson 5, we'll construct the coherent vacuum. Instead of $a_{\mathbf{k}} |0\rangle = 0$, we'll build the vacuum as a product of coherent states, one for each mode. Each coherent state will be the special state $|\alpha = 1/\sqrt{2}\rangle$ from Lesson 2 — the state with energy $\hbar\omega$ and maximal duality symmetry.

We'll compute the energy density of the coherent vacuum and show that:

$$
\lim_{a \to 0} \rho_{\text{coherent}}(a) = \text{finite}
$$

The coherent vacuum satisfies axiom A1. It has a well-defined continuum limit. And it gives a finite prediction for the vacuum energy, without any subtraction.

The mode vacuum is elegant but wrong. The coherent vacuum is less symmetric but right. Let's build it.

---

*Summary of evidence tiers:*
- *Fock space construction: **[ESTABLISHED]***
- *Energy density divergence: **[PROVEN]** — $\rho \sim a^{-4}$*
- *Mode vacuum fails A1 and F: **[PROVEN]***
- *Lorentz invariance and entanglement: **[ESTABLISHED]***
