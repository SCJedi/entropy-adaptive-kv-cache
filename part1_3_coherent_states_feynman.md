# Coherent States |α⟩: The "Most Classical" Quantum States

## The Big Question: Can Quantum Mechanics Look Classical?

Now here's something that really puzzled physicists for a long time. We have this quantum harmonic oscillator with its discrete energy levels, its number states |n⟩ - "ket n" - and all this fuzzy quantum uncertainty. But wait! When I look at a pendulum swinging, or a mass bouncing on a spring, it doesn't look quantized at all. It looks perfectly smooth and classical.

So we ask: *Is there some quantum state that behaves as classically as possible?*

The answer is **yes** - and these remarkable states are called **coherent states**, written |α⟩ - "ket alpha" - where α is a complex number. They were discovered by Schrödinger himself, but their importance wasn't fully appreciated until Glauber used them to describe laser light in the 1960s. (He got the Nobel Prize for it!)

---

## What Makes Coherent States Special?

### The Defining Property: Eigenstates of the Annihilation Operator

Here's the key idea. Remember our annihilation operator â - "a-hat" - that destroys one quantum of energy? For most states, â gives you a complicated mess. But coherent states are special:

$$\boxed{\hat{a}|\alpha\rangle = \alpha|\alpha\rangle}$$

Read this aloud: "a-hat acting on ket-alpha gives alpha times ket-alpha."

This is an **eigenvalue equation**! The coherent state |α⟩ is an eigenstate of â with eigenvalue α.

Now you might say, "Wait a minute, Feynman! You told me â lowers the number of quanta. How can any state come back unchanged (up to a constant)?"

Excellent question! The answer is that |α⟩ is a very special superposition of *all* number states. When â acts, it shuffles things around in just the right way that the overall state stays the same shape, just multiplied by α.

### Why a Complex Number?

The eigenvalue α is complex: α = |α|e^(iφ) - "alpha equals magnitude-alpha times e-to-the-i-phi." This complex number encodes *two* pieces of information:

- **|α|** (the magnitude): Related to the amplitude of oscillation
- **φ** (the phase): Related to where in the oscillation cycle we are

Just like a classical oscillator needs *two* numbers (position AND velocity, or equivalently amplitude AND phase), a coherent state needs a complex number with two components!

---

## Building Coherent States from Number States

### The Expansion Formula

Now let's figure out what |α⟩ actually looks like. We want to expand it in terms of the number states |n⟩:

$$|\alpha\rangle = \sum_{n=0}^{\infty} c_n |n\rangle$$

Read this: "Ket-alpha equals the sum over n from zero to infinity of c-sub-n times ket-n."

To find the coefficients c_n, we use the overlap ⟨n|α⟩ - "bracket n alpha" - which tells us "how much of state |n⟩ is contained in state |α⟩."

Using the eigenvalue equation â|α⟩ = α|α⟩ and working out the algebra (which I'll spare you), we get this beautiful result:

$$\boxed{|\alpha\rangle = e^{-|\alpha|^2/2} \sum_{n=0}^{\infty} \frac{\alpha^n}{\sqrt{n!}} |n\rangle}$$

Read this aloud: "Ket-alpha equals e-to-the-minus-alpha-magnitude-squared-over-two, times the sum over n of alpha-to-the-n over square-root-of-n-factorial, times ket-n."

Let me unpack this:
- **e^(-|α|²/2)**: This is a normalization factor to ensure ⟨α|α⟩ = 1
- **αⁿ/√n!**: This determines how much of each number state contributes
- The sum goes to infinity - *every* number state contributes!

### The Probability Distribution

What's the probability of finding exactly n quanta in a coherent state? We compute |⟨n|α⟩|² - "magnitude-bracket-n-alpha-squared":

$$P(n) = |\langle n|\alpha\rangle|^2 = e^{-|\alpha|^2} \frac{|\alpha|^{2n}}{n!}$$

Read this: "P of n equals e-to-the-minus-alpha-magnitude-squared times alpha-magnitude-to-the-2n over n-factorial."

Wait - I recognize this! This is a **Poisson distribution** with mean |α|²!

If you've studied probability, you know the Poisson distribution describes random, independent events - like radioactive decays, or phone calls at a switchboard. It's absolutely remarkable that nature gives us this beautiful mathematical form.

The average number of quanta is:
$$\langle \hat{n} \rangle = |\alpha|^2$$

Read this: "The expectation value of n-hat equals alpha-magnitude-squared."

So if |α| = 3, the average number of quanta is 9, but sometimes you'll find 7, sometimes 11, occasionally 15 - distributed according to Poisson statistics.

---

## The Energy of Coherent States

### Calculating the Expectation Value

Remember our Hamiltonian Ĥ = ℏω(n̂ + ½). What's the average energy of a coherent state?

$$\langle \alpha|\hat{H}|\alpha\rangle = \hbar\omega\left(\langle \alpha|\hat{n}|\alpha\rangle + \frac{1}{2}\right)$$

Read this: "Bracket-alpha-H-hat-alpha equals h-bar-omega times bracket-alpha-n-hat-alpha plus one-half."

We just found that ⟨n̂⟩ = |α|², so:

$$\boxed{\langle \alpha|\hat{H}|\alpha\rangle = \hbar\omega\left(|\alpha|^2 + \frac{1}{2}\right)}$$

Read this: "The average energy equals h-bar-omega times alpha-magnitude-squared plus one-half."

Notice that:
- When α = 0, we get E = ℏω/2 - that's just the vacuum state!
- As |α| grows, the energy increases like |α|² - just as you'd expect classically

The ½ is the irreducible zero-point energy, always there, riding along with whatever classical-looking oscillation we have.

---

## Why Are They "Most Classical"?

### Position and Momentum Expectation Values

Here's where it gets really beautiful. For a coherent state, the expectation values of position and momentum are:

$$\langle \alpha|\hat{x}|\alpha\rangle = \sqrt{\frac{2\hbar}{m\omega}} \text{Re}(\alpha)$$

$$\langle \alpha|\hat{p}|\alpha\rangle = \sqrt{2m\hbar\omega} \text{Im}(\alpha)$$

Read these: "The expectation value of x-hat is proportional to the real part of alpha" and "the expectation value of p-hat is proportional to the imaginary part of alpha."

The complex number α encodes the classical position and momentum!

### Time Evolution

Now the magic happens. Under time evolution:

$$|\alpha(t)\rangle = |e^{-i\omega t}\alpha\rangle$$

Read this: "Ket-alpha-of-t equals ket of e-to-the-minus-i-omega-t times alpha."

The complex number α just rotates in the complex plane with angular frequency ω! This means:

- ⟨x̂⟩ oscillates like cos(ωt)
- ⟨p̂⟩ oscillates like sin(ωt)
- The state oscillates back and forth **exactly like a classical harmonic oscillator**!

### Minimum Uncertainty

The uncertainties in position and momentum for a coherent state are:

$$\Delta x \cdot \Delta p = \frac{\hbar}{2}$$

This is the **minimum allowed by the uncertainty principle**! The coherent state has the least possible quantum fuzziness while still being consistent with quantum mechanics.

The vacuum state |0⟩ also saturates this bound. In fact, |0⟩ *is* a coherent state - it's |α⟩ with α = 0!

---

## The Physical Picture

Let me paint you a picture. Imagine the phase space - a graph with position x on one axis and momentum p on the other.

For a classical oscillator, the state is a single point that traces out a circle as time passes.

For a coherent state:
- The state is a **fuzzy blob** (the quantum uncertainty)
- The center of the blob traces out that same classical circle
- The blob doesn't spread out or change shape - it stays a minimum-uncertainty blob forever

This is why coherent states are "most classical" - they're as close to a classical point particle as quantum mechanics allows, oscillating in a perfect circle through phase space with minimum fuzziness.

---

## Why Physicists Love Coherent States

### They Describe Laser Light!

A laser produces coherent light - light in a coherent state. Unlike thermal light (from a lightbulb) where the number of photons fluctuates wildly, laser light has Poisson-distributed photon numbers. This is why lasers are so useful for precision measurements.

### They're Mathematically Beautiful

The coherent states form an **overcomplete basis** - there are more of them than we need, but they tile the phase space beautifully. They satisfy:

$$\frac{1}{\pi}\int |\alpha\rangle\langle\alpha| d^2\alpha = 1$$

Read this: "One over pi times the integral of ket-alpha-bra-alpha over the complex plane equals the identity."

### They Connect Quantum and Classical

Coherent states are where quantum mechanics shakes hands with classical mechanics. The correspondence principle says that for large quantum numbers, we should recover classical behavior. Coherent states with large |α| show us exactly how this works.

---

## Summary: The Remarkable Coherent States

| Property | Formula | Meaning |
|----------|---------|---------|
| Eigenvalue equation | â\|α⟩ = α\|α⟩ | Defining property |
| Expansion | \|α⟩ = e^(-\|α\|²/2) Σₙ (αⁿ/√n!) \|n⟩ | Superposition of all number states |
| Number distribution | P(n) = e^(-\|α\|²) \|α\|^(2n)/n! | Poisson distribution |
| Average number | ⟨n̂⟩ = \|α\|² | Mean of Poisson |
| Average energy | ⟨Ĥ⟩ = ℏω(\|α\|² + ½) | Classical energy + zero-point |
| Uncertainty | Δx·Δp = ℏ/2 | Minimum uncertainty |

---

## The Deep Insight

Here's what I want you to take away. Quantum mechanics isn't just about discreteness and uncertainty - it's about the *structure* of how states combine. The coherent states show us that within this quantum structure, there's room for states that behave almost classically.

The vacuum |0⟩ isn't empty - it's buzzing with zero-point energy. And when we add coherent excitations to the vacuum, we get states that oscillate like classical particles while still carrying that irreducible quantum fuzziness.

This is the harmony of physics: the classical world we see every day emerging naturally from the quantum substrate underneath, with coherent states serving as the bridge between the two.

*"The universe is not only queerer than we suppose, but queerer than we* can *suppose - yet it's also more elegant than we ever imagined."*

---

**Next: We'll explore squeezed states, where we can trade uncertainty in one variable for uncertainty in another - pushing the boundaries of what quantum mechanics allows!**
