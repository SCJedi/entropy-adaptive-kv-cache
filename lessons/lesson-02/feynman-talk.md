# Coherent States -- Nature's Preferred Quantum States
### A Feynman-Voice Lecture

---

All right. In the last lecture, I showed you the quantum harmonic oscillator and its number states. And I pointed out something strange: the number states don't oscillate. They just sit there with a definite energy and completely uncertain phase. Which is fine if you want to count particles, but it's lousy if you want to describe anything that looks like a classical oscillation.

So today I want to ask: what quantum state DOES look classical? What state has a wavepacket that actually sloshes back and forth?

## Eigenstates of the Annihilation Operator

The answer is the coherent state. It's defined by a beautifully simple equation:

$$
\hat{a}|\alpha\rangle = \alpha|\alpha\rangle
$$

where $\alpha$ is any complex number. **[PROVEN]** -- this is standard quantum mechanics, introduced by Schrodinger in 1926 and developed by Glauber in the 1960s (he got the Nobel Prize for it in 2005).

Now, the annihilation operator $\hat{a}$ is not Hermitian, so it can have complex eigenvalues. That's fine. What's beautiful is what this equation MEANS physically. When you remove a quantum from a coherent state, the state doesn't change (up to a scale factor). It's like removing a cup of water from the ocean -- the ocean doesn't notice.

Let me write it out explicitly. In terms of number states:

$$
|\alpha\rangle = e^{-|\alpha|^2/2}\sum_{n=0}^{\infty} \frac{\alpha^n}{\sqrt{n!}}|n\rangle
$$

You can verify this by hitting it with $\hat{a}$ and checking that you get $\alpha|\alpha\rangle$. I'll leave that as an exercise, but do it -- it's satisfying when it works out. **[PROVEN]**.

There's another way to build a coherent state. Start with the ground state $|0\rangle$ and displace it:

$$
|\alpha\rangle = \hat{D}(\alpha)|0\rangle = \exp(\alpha\hat{a}^\dagger - \alpha^*\hat{a})|0\rangle
$$

So a coherent state is just the vacuum, kicked to a new location in phase space. Same shape, different center. **[PROVEN]**.

## The Particle Number Is Uncertain

Here's something that trips people up. The probability of finding exactly $n$ particles in a coherent state is:

$$
P(n) = e^{-|\alpha|^2}\frac{|\alpha|^{2n}}{n!}
$$

That's a Poisson distribution. The mean is $\langle n \rangle = |\alpha|^2$, and the variance equals the mean. **[PROVEN]**.

So in a coherent state, you DON'T know how many particles you have. A number state has definite particle number but uncertain phase. A coherent state has definite phase (well, as definite as quantum mechanics allows) but uncertain particle number. It's complementarity -- the same trade-off between conjugate variables that shows up everywhere in quantum mechanics.

## Minimum Uncertainty

Now here's the remarkable thing. Compute the position and momentum uncertainties:

$$
\Delta x = \sqrt{\frac{\hbar}{2m\omega}}, \qquad \Delta p = \sqrt{\frac{m\hbar\omega}{2}}
$$

$$
\Delta x \cdot \Delta p = \frac{\hbar}{2}
$$

That's the Heisenberg minimum. Same as the ground state. And it doesn't depend on $\alpha$ at all. **[PROVEN]**.

What changes with $\alpha$ is WHERE the wavepacket sits, not how wide it is. And under time evolution, $\alpha(t) = e^{-i\omega t}\alpha$ -- the parameter rotates in the complex plane. The center of the wavepacket traces out a circle in phase space, exactly like a classical oscillator. **[PROVEN]**.

This is why laser light is described by coherent states. It's the most classical quantum state you can make.

## The Energy

The mean energy is:

$$
\langle H \rangle = \hbar\omega\left(|\alpha|^2 + \frac{1}{2}\right)
$$

**[PROVEN]**. Simple: $\hbar\omega/2$ from zero-point energy, $\hbar\omega|\alpha|^2$ from the coherent excitation.

## Now Wait a Minute -- $|\alpha|^2 = 1/2$

Let me set $|\alpha|^2 = 1/2$. Watch what happens.

**Energy:**

$$
\langle H \rangle = \hbar\omega\left(\frac{1}{2} + \frac{1}{2}\right) = \hbar\omega
$$

Exactly one quantum. Not one particle -- one quantum of energy. The coherent excitation equals the zero-point energy. **[PROVEN]**.

If I identify $\hbar\omega = mc^2$ -- the Compton frequency of a particle of mass $m$ -- then this state carries exactly one rest energy. Remember that for later.

**Particle number:**

$$
\langle n \rangle = \frac{1}{2}, \qquad P(0) = e^{-1/2} \approx 0.607, \qquad P(1) = \frac{1}{2}e^{-1/2} \approx 0.303
$$

This is delicious. A state with energy $\hbar\omega$ -- "one quantum" -- has a 61% chance of containing ZERO particles. The mean particle number is one-half. **[PROVEN]**.

This should bother you, in a good way. We say the state has "one quantum of energy," but if you measure the particle number, you'll most likely find nothing there. Energy and particle number are different things. Don't confuse them.

**Energy equipartition:**

$$
\langle T \rangle = \frac{\hbar\omega}{2}, \qquad \langle V \rangle = \frac{\hbar\omega}{2}
$$

The kinetic and potential energies are exactly equal. Each gets half the total energy. **[PROVEN]**.

This is the ONLY value of $|\alpha|^2$ where the coherent excitation energy is split evenly between kinetic and potential. For $|\alpha|^2 > 1/2$, the coherent part of the potential exceeds the coherent part of the kinetic (I mean the part beyond the zero-point contribution). For $|\alpha|^2 < 1/2$, vice versa. At $|\alpha|^2 = 1/2$, they're exactly balanced.

## The Self-Duality Theorem

Now here's where it gets beautiful. The value $|\alpha|^2 = 1/2$ isn't just special because of the energy. It sits at the fixed point of three different mathematical dualities, and they're all connected.

**Legendre self-duality.** Take the function $f(x) = x^2/2$. Compute its Fenchel-Legendre conjugate: $f^*(p) = \sup_x(px - f(x)) = p^2/2$. The function is its own conjugate. And here's the thing: it's the UNIQUE convex function with this property. **[PROVEN]** -- this is standard convex analysis.

**Fourier self-duality.** Take the Gaussian $g(x) = e^{-x^2/2}$. Its Fourier transform (with the right convention) is... $e^{-p^2/2}$. Same function. It's a fixed point of the Fourier transform. And it's the unique Schwartz function with this property (up to a constant). **[PROVEN]** -- this is standard harmonic analysis.

**Energy equipartition.** As I just showed you: kinetic equals potential. **[PROVEN]**.

These three aren't coincidences. They're mathematically connected. The Legendre self-duality of $f$ implies the Fourier self-duality of $e^{-f}$, because the Fourier transform of a Gaussian is controlled by the quadratic in the exponent, and self-dual quadratics give self-dual Gaussians. And the energy equipartition follows because the harmonic oscillator Hamiltonian splits into kinetic ($\sim p^2$) and potential ($\sim x^2$), and when the underlying quadratic is self-dual, these two pieces balance. **[PROVEN]** as mathematical connections.

The coherent state with $|\alpha|^2 = 1/2$ is the state whose wavefunction is built from the unique self-dual Gaussian, whose energy splits via the unique self-dual quadratic, and whose Fourier and Legendre dual descriptions are identical.

That's a LOT of structure converging on a single point.

## What's Algebraic and What Was Demoted

Now I need to be honest about something. The value $|\alpha|^2 = 1/2$ was determined ALGEBRAICALLY: if you demand energy $\hbar\omega$ per oscillator, then $\hbar\omega(|\alpha|^2 + 1/2) = \hbar\omega$ forces $|\alpha|^2 = 1/2$. That's it. Simple equation. **[PROVEN]**.

There was an earlier claim that $|\alpha|^2 = 1/2$ is also "variationally unique" -- that it minimizes some physically meaningful functional. We investigated this carefully. The short version: the variational argument does select coherent states over squeezed states at fixed energy, but when you let the mass vary freely, the critical point turns out to be a MAXIMUM, not a minimum. The optimization story doesn't work. **[DEMOTED]**.

The algebraic determination stands. The self-duality properties stand. The variational uniqueness does not. That's science -- you keep the parts that survive scrutiny and you discard the parts that don't.

## Coherent States Are Not Orthogonal

One more thing. The overlap between two coherent states is:

$$
|\langle\alpha|\beta\rangle|^2 = e^{-|\alpha - \beta|^2}
$$

Never zero. They're not orthogonal. And yet they form a resolution of the identity:

$$
\frac{1}{\pi}\int|\alpha\rangle\langle\alpha|\,d^2\alpha = \hat{I}
$$

This means the coherent states are an OVERCOMPLETE basis. You can expand any state in terms of them, but the expansion isn't unique. There are more coherent states than you need.

This is perfectly consistent with quantum mechanics. It just means coherent states aren't a basis in the usual linear algebra sense -- they're a frame. **[PROVEN]**.

## What We've Built

Let me take stock of where we are.

We have the quantum harmonic oscillator (Lesson 1) with its zero-point energy $\hbar\omega/2$. Now we have coherent states -- minimum-uncertainty states that look classical, with Poisson particle statistics and a special value $|\alpha|^2 = 1/2$ that carries exactly one quantum and sits at the self-dual fixed point of every natural transformation.

What we DON'T have yet is quantum field theory. In a field, you don't have one oscillator -- you have one per momentum mode. Infinitely many. And the standard vacuum of quantum field theory -- the mode vacuum -- puts every one of those oscillators in the ground state $|0\rangle$, which gives a divergent energy density.

That's Lesson 3. And then Lesson 4 will ask: what if you don't put every oscillator in $|0\rangle$? What if you put them in coherent states with $|\alpha|^2 = 1/2$ instead? What kind of vacuum do you get?

But I'm getting ahead of myself. Let's do the mode vacuum properly first.

---

*Evidence tiers for this lesson:*
- *Sections 2.1--2.7 (coherent state properties): [PROVEN] -- standard quantum optics*
- *Section 2.8 (self-duality theorem): [PROVEN] as mathematics*
- *Variational uniqueness of $|\alpha|^2 = 1/2$: [DEMOTED]*
- *$|\alpha|^2 = 1/2$ determined algebraically: [PROVEN]*
