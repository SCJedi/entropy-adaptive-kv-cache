# Why Does the UV Cause Problems?
### A Feynman-Voice Lecture

---

All right, now we get to the ugly stuff. I told you last time that the UV -- the short wavelengths, the high energies -- can't be ignored because you have to sum over all modes. Now let me show you what happens when you actually do that sum. It's not pretty.

## The Zero-Point Energy

Let's start with something simple. Take a single harmonic oscillator -- a mass on a spring, or one mode of an electromagnetic field, or whatever. Quantum mechanics tells you the energy levels are:

$$E_n = \hbar\omega\left(n + \frac{1}{2}\right)$$

The ground state, $n = 0$, has energy $\hbar\omega/2$. Not zero. There's always something there -- the "zero-point energy."

Why? The uncertainty principle. You can't have both position and momentum be exactly zero. If you tried to freeze the oscillator completely, you'd violate $\Delta x \Delta p \geq \hbar/2$. So there's always some jiggling, and that jiggling has energy.

For one mode, this is fine. It's a small, finite amount of energy. No problem.

## The Sum

But a quantum field isn't one oscillator. It's infinitely many. One for each mode, for each possible wavelength. And you have to add up all their zero-point energies:

$$E_{\text{total}} = \sum_{\text{all } \mathbf{k}} \frac{1}{2}\hbar\omega_{\mathbf{k}}$$

In the continuum limit, this sum becomes an integral:

$$\rho = \int \frac{d^3k}{(2\pi)^3} \frac{\hbar\omega_k}{2}$$

Let me actually compute this thing for a massless field, where $\omega_k = ck$. Go to spherical coordinates:

$$\rho = \int_0^{\Lambda} \frac{4\pi k^2 dk}{(2\pi)^3} \cdot \frac{\hbar ck}{2}$$

The $4\pi k^2$ comes from the surface area of a sphere in $k$-space. The integral becomes:

$$\rho = \frac{\hbar c}{4\pi^2} \int_0^{\Lambda} k^3 dk = \frac{\hbar c \Lambda^4}{16\pi^2}$$

Look at that. The energy density goes as $\Lambda^4$. Fourth power of the cutoff. If you let $\Lambda$ go to infinity, the energy density blows up. Diverges. Goes to infinity.

## Why Does It Diverge?

Here's the physics of why this happens. Two things work together to make the divergence:

**First:** there are MORE modes at high $k$. Think about it. In a shell of radius $k$ and thickness $dk$ in momentum space, the number of modes is proportional to the volume of that shell, which goes like $k^2 dk$. More high-frequency modes than low-frequency modes.

**Second:** each mode contributes MORE energy at high $k$. The zero-point energy is $\hbar\omega/2$, and for a relativistic dispersion, $\omega = ck$, so the energy per mode grows with $k$.

Multiply them together: $(k^2) \times (k) = k^3$. Integrate that: $\int k^3 dk = k^4/4$. Divergent.

This is called a "quartic divergence" because it goes as the fourth power of the cutoff. It's the worst kind of divergence you can have.

## The Numbers

Okay, let's plug in some numbers. What if we cut off the integral at the Planck scale? That's the scale where quantum gravity presumably takes over, so maybe we shouldn't trust field theory beyond that.

The Planck cutoff is $\Lambda_P \sim 10^{19}$ GeV in energy units, or about $10^{35}$ inverse meters in wave number. Plug that in:

$$\rho_{\text{Planck}} \sim \frac{\hbar c \Lambda_P^4}{16\pi^2} \sim 10^{113} \text{ J/m}^3$$

Now what's the observed energy density of the universe? The dark energy that's accelerating cosmic expansion? It's about:

$$\rho_{\text{observed}} \sim 10^{-10} \text{ J/m}^3$$

The ratio? **$10^{123}$**.

That's a 1 followed by 123 zeros. A trillion trillion trillion trillion trillion trillion trillion trillion trillion trillion. It's not a discrepancy of a factor of 2 or 10 or even a million. It's the worst prediction in the history of science.

## It's Not a Math Trick

Now, you might think: "Surely this is just a computational artifact. Surely physicists have figured out how to handle this."

Sort of. There's a procedure called renormalization. The basic idea is that we only ever measure DIFFERENCES in energy. So we define a "renormalized" Hamiltonian:

$$:H: = H - \langle 0|H|0\rangle$$

We subtract the infinite vacuum energy by definition. Now $\langle 0|:H:|0\rangle = 0$. Problem solved, right?

Wrong. Here's why.

Gravity doesn't care about your subtractions. Einstein's equation says spacetime curvature is proportional to the stress-energy tensor:

$$G_{\mu\nu} = 8\pi G \langle T_{\mu\nu}\rangle$$

Gravity couples to the ABSOLUTE energy density, not differences. If the vacuum has $10^{113}$ joules per cubic meter, gravity should curve spacetime accordingly. The universe should be wrapped up into a ball so tight that nothing we recognize could exist.

But it doesn't. The actual curvature of the universe corresponds to something like $10^{-10}$ J/m$^3$. So either the vacuum energy really is tiny, or something is canceling it to 123 decimal places, or we're calculating the wrong thing entirely.

## The Refinement Problem

Here's another way to see how bad this is. Suppose you partition space into cells of size $a$ and use $\Lambda = \pi/a$ as your cutoff. The energy density is:

$$\rho(a) \propto a^{-4}$$

Now refine your description. Make the cells 10 times smaller: $a \to a/10$.

$$\rho(a/10) = 10^4 \cdot \rho(a) = 10,000 \times \rho(a)$$

The energy density goes UP by a factor of 10,000! Make the cells 100 times smaller, it goes up by $10^8$. A million times smaller, $10^{24}$.

This is completely backwards. If you have a well-defined physical state, describing it more precisely should give you a more accurate picture of the SAME state. The energy density should converge, not diverge.

The mode vacuum FAILS this test. It gets worse the more finely you try to describe it. That's not a physical state -- it's a pathology.

## The Historical Parallel

You know, we've seen this before. In the late 1800s, physicists tried to calculate the energy density of blackbody radiation. Classical physics said each mode gets energy $k_B T$ (equipartition), and there are more high-frequency modes than low. Add them up: infinity.

They called it the "ultraviolet catastrophe." It was a crisis. Classical physics was predicting that any warm object should emit infinite energy as radiation. Obviously wrong.

Planck's solution was to introduce quantization. High-frequency modes can't be excited at low temperatures because the energy steps are too big. Only low-frequency modes contribute significantly. The sum converges.

But here's the thing: that fix doesn't work for the vacuum energy. The zero-point energy is ALWAYS there, regardless of temperature. There's no thermal suppression of high-frequency modes. The UV catastrophe is back, and this time Planck's trick doesn't save us.

## What It Means

Let me be clear about what we're facing. This isn't a problem of not knowing some constant, or needing better measurements. The theoretical prediction is off by 123 orders of magnitude. There's no fine-tuning that can fix this. There's no "small correction" that makes it work.

Either:
1. There's some mechanism that cancels the vacuum energy to extreme precision (supersymmetry? But we don't see it, and even if we did, it would still be off by ~60 orders of magnitude)
2. The subtraction procedure is actually correct and we just don't understand what we're subtracting (possible, but unsatisfying)
3. We're calculating the vacuum energy of the WRONG vacuum state

That third option is what this course explores. Maybe the mode vacuum -- the state where every mode is in its ground state -- isn't the physical vacuum. Maybe the physical vacuum is something else, something with finite energy density that doesn't diverge under refinement.

We'll get to that. But first, the next lesson looks at how physics has tried to handle the UV problem with various strategies -- cutoffs, regularization, renormalization. None of them completely work, but understanding them is essential for seeing why a different approach might be needed.

---

*Mathematical claims (the divergence, the $\Lambda^4$ scaling, the numerical magnitude): [PROVEN]. The cosmological constant discrepancy: [ESTABLISHED]. The interpretation and proposed solutions: [FRAMEWORK] or [OPEN].*
