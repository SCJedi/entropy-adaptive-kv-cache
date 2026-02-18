# The Quantum Harmonic Oscillator
### A Feynman-Voice Lecture

---

Look, I want to start at the very beginning, because if you don't understand the harmonic oscillator, you don't understand quantum field theory. And if you don't understand quantum field theory, you have no business talking about vacuum energy. So let's get this right.

## The Thing That Won't Sit Still

Here's a ball on a spring. You pull it, it oscillates. The energy is kinetic plus potential:

$$
E = \frac{p^2}{2m} + \frac{1}{2}m\omega^2 x^2
$$

Simple. And classically, you can bring this thing to rest. Set $x = 0$, set $p = 0$, and the energy is exactly zero. The ball just sits there. Nothing moves. **[PROVEN]** -- this is freshman mechanics.

Now quantize it. And everything changes.

## The Commutator That Ruins Everything

When you go quantum, $x$ and $p$ become operators, and they don't commute:

$$
[\hat{x}, \hat{p}] = i\hbar
$$

That's the uncertainty principle, right there in algebraic form. **[PROVEN]** -- this is the foundation of quantum mechanics, confirmed by every experiment since 1927.

Now here's the trick. Define two new operators:

$$
\hat{a} = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} + \frac{i\hat{p}}{m\omega}\right), \qquad \hat{a}^\dagger = \sqrt{\frac{m\omega}{2\hbar}}\left(\hat{x} - \frac{i\hat{p}}{m\omega}\right)
$$

Do the algebra -- and I mean actually do it, don't just nod -- and you get:

$$
[\hat{a}, \hat{a}^\dagger] = 1
$$

**[PROVEN]**. It's just arithmetic, following from $[\hat{x}, \hat{p}] = i\hbar$.

Now rewrite the Hamiltonian in terms of these operators:

$$
H = \hbar\omega\left(\hat{a}^\dagger\hat{a} + \frac{1}{2}\right)
$$

See that $\frac{1}{2}$? That's not something I put in by hand. It comes from the commutator. When you expand $\hat{a}^\dagger\hat{a}$, you get the Hamiltonian minus $\hbar\omega/2$. The ordering of operators matters because they don't commute. That half is the price you pay for quantum mechanics.

## The Ladder

Define $\hat{n} = \hat{a}^\dagger\hat{a}$. The eigenstates of $\hat{n}$ are $|n\rangle$ with eigenvalue $n = 0, 1, 2, \ldots$, and the energies are:

$$
E_n = \hbar\omega\left(n + \frac{1}{2}\right)
$$

**[PROVEN]**. Equally spaced. Each step up adds exactly one quantum of energy $\hbar\omega$. That's why $\hat{a}^\dagger$ is called the creation operator -- it creates a quantum -- and $\hat{a}$ is the annihilation operator, because it destroys one.

The ladder has a bottom rung. The ground state $|0\rangle$ satisfies $\hat{a}|0\rangle = 0$. You can't go lower. And its energy is:

$$
E_0 = \frac{1}{2}\hbar\omega
$$

Not zero. Half a quantum. **[PROVEN]**.

## Why You Can't Get to Zero

Now wait a minute, someone says. Can't you just subtract that half off? Define a new Hamiltonian $H' = H - \hbar\omega/2$ and be done with it?

For a single oscillator, sure. The zero of energy is arbitrary in non-gravitational physics. But let me show you why the zero-point energy is *real*, not just a bookkeeping artifact.

Compute the uncertainties in the ground state:

$$
\Delta x = \sqrt{\frac{\hbar}{2m\omega}}, \qquad \Delta p = \sqrt{\frac{m\hbar\omega}{2}}
$$

Multiply them:

$$
\Delta x \cdot \Delta p = \frac{\hbar}{2}
$$

That's the absolute minimum allowed by the uncertainty principle. The ground state is as close to "sitting still" as quantum mechanics permits. And even at this minimum, the energy is $\hbar\omega/2$. **[PROVEN]**.

Here's the physical picture. The particle can't sit at $x = 0$ with $p = 0$ because that would mean $\Delta x = 0$ and $\Delta p = 0$ simultaneously. So it jiggles. It has to. Those jiggles have kinetic energy (from the momentum fluctuations) and potential energy (from the position fluctuations). Add them up and you get $\hbar\omega/2$.

In fact, let me show you something nice. In the ground state:

$$
\langle T \rangle = \frac{\hbar\omega}{4}, \qquad \langle V \rangle = \frac{\hbar\omega}{4}
$$

Exactly equal. Half the zero-point energy is kinetic, half is potential. This is the virial theorem for the harmonic oscillator. **[PROVEN]**. Remember this -- it'll come back in Lesson 2 when we talk about energy equipartition.

## One Oscillator Is Fine. Infinitely Many Are Not.

Here's where the trouble starts. Suppose you have $N$ independent oscillators, with frequencies $\omega_1, \omega_2, \ldots, \omega_N$. Total ground state energy:

$$
E_0^{\text{total}} = \sum_{k=1}^{N} \frac{1}{2}\hbar\omega_k
$$

For $N = 1$, this is tiny. For $N = 100$, still manageable. But in quantum field theory -- and we'll get to this properly in Lesson 3 -- every momentum mode of a field is its own oscillator. And there are infinitely many momentum modes.

Put a UV cutoff $\Lambda$ on the momentum (ignore modes with wavelength shorter than $1/\Lambda$). The energy density is:

$$
\rho_0 = \int_0^{\Lambda} \frac{d^3k}{(2\pi)^3}\,\frac{1}{2}\hbar\omega_k
$$

For a massless field, $\omega_k = c|\mathbf{k}|$, and this integral gives:

$$
\rho_0 \sim \frac{\hbar c\,\Lambda^4}{16\pi^2}
$$

**[PROVEN]** -- this is a straightforward integral.

Now set $\Lambda$ to the Planck scale. You get $\rho_0 \sim 10^{113}$ J/m$^3$. The observed dark energy density is about $6 \times 10^{-10}$ J/m$^3$. The ratio is $10^{123}$.

That's the "worst prediction in physics." **[PROVEN]** in the sense that the calculation is correct. What's not proven is that this calculation is asking the right question -- but that's a story for later lessons.

## This Is Not Just Theory

Now, some of you might be wondering: is this zero-point energy a real thing, or just a mathematical convenience? Let me give you three pieces of evidence.

First, the **Casimir effect**. Take two uncharged metal plates, put them close together in a vacuum. The allowed modes between the plates are restricted -- not all wavelengths fit. So the zero-point energy between the plates is less than the zero-point energy outside. The difference creates a force that pushes the plates together. Measured. Confirmed. Real force from vacuum fluctuations. **[PROVEN]**.

Second, the **Lamb shift**. The energy levels of hydrogen aren't quite where Dirac's equation says they should be. The $2S_{1/2}$ and $2P_{1/2}$ levels, which Dirac predicts to be degenerate, are actually split by about 1057 MHz. The explanation: the electron interacts with the zero-point fluctuations of the electromagnetic field. Measured by Willis Lamb in 1947. It helped launch quantum electrodynamics. **[PROVEN]**.

Third, **molecular spectroscopy**. Diatomic molecules vibrate at quantized energies $E_n = \hbar\omega(n + 1/2)$. The zero-point energy $\hbar\omega/2$ shifts the entire spectrum. You can see it directly in infrared absorption data. **[PROVEN]**.

So zero-point energy is not a bookkeeping trick. It has physical consequences. The question is what happens when you have infinitely many oscillators, which is the quantum field theory situation. We'll get to that.

## Number States Don't Oscillate

One more thing before I let you go. The states $|n\rangle$ are called "number states" because they have a definite number of quanta. But here's the funny thing:

$$
\langle n|\hat{x}|n\rangle = 0, \qquad \langle n|\hat{p}|n\rangle = 0
$$

for every $n$. The average position is zero. The average momentum is zero. This thing isn't oscillating -- it's sitting there, spread out in a symmetric cloud, with a definite amount of energy but no definite phase of oscillation.

That's weird, right? A classical oscillator with energy $E = \hbar\omega(n + 1/2)$ would be swinging back and forth with some amplitude $A = \sqrt{2E/(m\omega^2)}$. But the quantum number state doesn't swing. It has definite energy but completely random phase.

**[PROVEN]**. And it raises a question: is there a quantum state that DOES oscillate like a classical one? A state with a definite phase, with the center of the wavepacket actually moving back and forth?

Yes. It's called a coherent state. And it'll be the star of Lesson 2.

## A Word About Phase Space

Let me paint you a picture that will help later. Think of phase space -- the plane where the horizontal axis is position $x$ and the vertical axis is momentum $p$. A classical oscillator traces an ellipse in this plane, going round and round at frequency $\omega$.

The ground state $|0\rangle$ is a fuzzy blob centered at the origin. It has width $\Delta x$ in the horizontal direction and $\Delta p$ in the vertical direction, and the product $\Delta x \cdot \Delta p = \hbar/2$ is as small as quantum mechanics allows. The blob doesn't move. It just sits there at the origin, vibrating with its irreducible zero-point energy.

A number state $|n\rangle$ is a ring in phase space -- circular symmetry, no preferred direction, no phase. That's why $\langle x\rangle = 0$ and $\langle p\rangle = 0$. The energy is stored in the radius of the ring, but there's no arrow pointing to "where in the cycle" the oscillator is.

A coherent state, which we'll meet in the next lecture, is a blob -- same size as the ground state blob -- but displaced away from the origin. It traces out the classical ellipse as it rotates. Minimum uncertainty, definite phase, classical motion. That's what "most classical" means in quantum mechanics.

This phase-space picture is the right way to think about all of this. Keep it in mind.

## What We've Established

Let me be clear about what's proven and what isn't, because later in this course we're going to venture into territory where the evidence gets thinner, and you'll need to know the difference.

Everything in this lesson is **[PROVEN]**. Standard quantum mechanics. Textbook stuff. Confirmed experimentally in systems ranging from molecular vibrations to superconducting circuits to laser cavities. The commutation relations, the energy spectrum, the zero-point energy, the uncertainty principle saturation, the virial theorem, the divergence of the mode sum -- all of it is rock solid.

The question this course is going to ask is: when you have infinitely many of these oscillators (a quantum field), what is the right way to compute the vacuum energy? Is the mode sum the right calculation? Or is there a different state -- a different kind of vacuum -- that gives a finite, physical answer?

But we're not there yet. First, we need to understand coherent states. That's next.

---

*Every claim in this lesson: [PROVEN] -- standard quantum mechanics, experimentally confirmed.*
