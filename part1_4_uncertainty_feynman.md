# Part 1.4: Uncertainty Relations and Coherent States

## The Heisenberg Uncertainty Principle

Now we come to one of the most famous results in all of quantum mechanics. It's called the **Heisenberg uncertainty principle**, and it says something profound about the limits of what we can know.

Here it is:

$$\Delta x \cdot \Delta p \geq \frac{\hbar}{2}$$

We read this as: "delta-x times delta-p is greater than or equal to h-bar over two."

Let me explain each piece:

- **Δx** - "delta x" - is the uncertainty in position. It measures how spread out the particle's position is. If you were to measure where the particle is many times (on identically prepared systems), Δx tells you how much those measurements would scatter.

- **Δp** - "delta p" - is the uncertainty in momentum. Same idea: how spread out are the momentum values you'd measure?

- **ℏ/2** - "h-bar over two" - is a tiny but nonzero number. It's about 5 × 10⁻³⁵ joule-seconds. Small, but definitely not zero!

The inequality says: *you cannot know both position and momentum with arbitrary precision*. The product of their uncertainties has a floor. Nature simply won't let you do better than ℏ/2.

---

## What Does "≥" Really Mean?

Now here's something important that often gets glossed over. The symbol "≥" - "greater than or equal to" - contains two possibilities:

1. **Greater than**: Δx·Δp > ℏ/2
2. **Equal to**: Δx·Δp = ℏ/2

Most quantum states satisfy the first case. They're *worse* than the minimum. Their uncertainties multiply to something bigger than ℏ/2, sometimes much bigger!

Think about it this way. Suppose I have a particle in some arbitrary quantum state. I compute Δx and Δp. I multiply them together. What do I get?

Almost always, I get something like:

$$\Delta x \cdot \Delta p = 3\hbar, \quad \text{or} \quad 10\hbar, \quad \text{or} \quad 47\hbar$$

The uncertainty principle guarantees I won't get less than ℏ/2, but it says nothing about how much *more* I might get. Most states are sloppy. They have more uncertainty than they need to.

But some states are special. Some states achieve:

$$\Delta x \cdot \Delta p = \frac{\hbar}{2} \quad \text{exactly!}$$

These are called **minimum uncertainty states**. They saturate the bound. They're as precise as the laws of physics allow.

And here's the beautiful punch line: *coherent states are minimum uncertainty states*.

---

## Computing Δx for a Coherent State

Let's prove this. We need to compute Δx and Δp for a coherent state and show their product equals exactly ℏ/2.

First, what is Δx mathematically? It's the standard deviation:

$$\Delta x = \sqrt{\langle \hat{x}^2 \rangle - \langle \hat{x} \rangle^2}$$

We read this as: "delta-x equals the square root of the expectation value of x-hat-squared minus the expectation value of x-hat, all squared."

Let me unpack this:

- **⟨x̂⟩** - "expectation value of x-hat" - is the average position
- **⟨x̂²⟩** - "expectation value of x-hat-squared" - is the average of position squared
- The difference ⟨x̂²⟩ - ⟨x̂⟩² measures the spread

For a coherent state |α⟩, we need to compute both terms.

### Step 1: Express x̂ in Terms of Creation and Annihilation Operators

Recall that we can write the position operator as:

$$\hat{x} = \sqrt{\frac{\hbar}{2m\omega}}(\hat{a} + \hat{a}^\dagger)$$

We read this as: "x-hat equals the square root of h-bar over two-m-omega, times the quantity a-hat plus a-hat-dagger."

Let me define a shorthand for the coefficient:

$$x_0 = \sqrt{\frac{\hbar}{2m\omega}}$$

This is "x-zero" or "x-naught" - it has dimensions of length and sets the natural length scale of the oscillator. So:

$$\hat{x} = x_0(\hat{a} + \hat{a}^\dagger)$$

### Step 2: Compute ⟨x̂⟩

For a coherent state |α⟩:

$$\langle \hat{x} \rangle = \langle \alpha | \hat{x} | \alpha \rangle = x_0 \langle \alpha | (\hat{a} + \hat{a}^\dagger) | \alpha \rangle$$

Now I use two key facts about coherent states:

- â|α⟩ = α|α⟩ (eigenvalue equation)
- ⟨α|â† = ⟨α|α* (the adjoint relation)

So:

$$\langle \alpha | \hat{a} | \alpha \rangle = \alpha$$
$$\langle \alpha | \hat{a}^\dagger | \alpha \rangle = \alpha^*$$

Therefore:

$$\langle \hat{x} \rangle = x_0(\alpha + \alpha^*)$$

Since α + α* = 2·Re(α), we can also write:

$$\langle \hat{x} \rangle = 2x_0 \, \text{Re}(\alpha)$$

The average position depends on the real part of α. Makes sense!

### Step 3: Compute ⟨x̂²⟩

Now the harder part. We need:

$$\langle \hat{x}^2 \rangle = x_0^2 \langle \alpha | (\hat{a} + \hat{a}^\dagger)^2 | \alpha \rangle$$

Let's expand (â + â†)²:

$$(\hat{a} + \hat{a}^\dagger)^2 = \hat{a}^2 + \hat{a}\hat{a}^\dagger + \hat{a}^\dagger\hat{a} + (\hat{a}^\dagger)^2$$

Now I compute each expectation value. Using â|α⟩ = α|α⟩ and ⟨α|â† = ⟨α|α*:

$$\langle \alpha | \hat{a}^2 | \alpha \rangle = \alpha^2$$

$$\langle \alpha | (\hat{a}^\dagger)^2 | \alpha \rangle = (\alpha^*)^2$$

For the cross terms, I need to be careful about ordering:

$$\langle \alpha | \hat{a}^\dagger \hat{a} | \alpha \rangle = \alpha^* \alpha = |\alpha|^2$$

$$\langle \alpha | \hat{a} \hat{a}^\dagger | \alpha \rangle = \langle \alpha | (\hat{a}^\dagger \hat{a} + 1) | \alpha \rangle = |\alpha|^2 + 1$$

Here I used the commutator [â, â†] = 1, which gives ââ† = â†â + 1.

Adding them all up:

$$\langle (\hat{a} + \hat{a}^\dagger)^2 \rangle = \alpha^2 + |\alpha|^2 + 1 + |\alpha|^2 + (\alpha^*)^2$$

$$= \alpha^2 + (\alpha^*)^2 + 2|\alpha|^2 + 1$$

$$= (\alpha + \alpha^*)^2 + 1$$

So:

$$\langle \hat{x}^2 \rangle = x_0^2 \left[ (\alpha + \alpha^*)^2 + 1 \right]$$

### Step 4: Compute (Δx)²

Now I can find the variance:

$$(\Delta x)^2 = \langle \hat{x}^2 \rangle - \langle \hat{x} \rangle^2$$

$$= x_0^2 \left[ (\alpha + \alpha^*)^2 + 1 \right] - x_0^2 (\alpha + \alpha^*)^2$$

$$= x_0^2$$

Look at that! The α-dependent terms cancel! We get:

$$\boxed{(\Delta x)^2 = x_0^2 = \frac{\hbar}{2m\omega}}$$

And therefore:

$$\Delta x = \sqrt{\frac{\hbar}{2m\omega}}$$

This is remarkable: **the position uncertainty of a coherent state is independent of α**. Whether the state is the vacuum (α = 0) or a highly excited coherent state (large |α|), the uncertainty Δx is always the same!

---

## Computing Δp for a Coherent State

Now let's do the same for momentum. The momentum operator is:

$$\hat{p} = i\sqrt{\frac{m\omega\hbar}{2}}(\hat{a}^\dagger - \hat{a})$$

We read this as: "p-hat equals i times the square root of m-omega-h-bar over two, times the quantity a-hat-dagger minus a-hat."

Define:

$$p_0 = \sqrt{\frac{m\omega\hbar}{2}}$$

This is "p-zero" - the natural momentum scale. So:

$$\hat{p} = ip_0(\hat{a}^\dagger - \hat{a})$$

### Step 1: Compute ⟨p̂⟩

$$\langle \hat{p} \rangle = ip_0 \langle \alpha | (\hat{a}^\dagger - \hat{a}) | \alpha \rangle = ip_0(\alpha^* - \alpha)$$

Since α* - α = -2i·Im(α):

$$\langle \hat{p} \rangle = ip_0 \cdot (-2i) \, \text{Im}(\alpha) = 2p_0 \, \text{Im}(\alpha)$$

The average momentum depends on the imaginary part of α!

### Step 2: Compute ⟨p̂²⟩

$$\langle \hat{p}^2 \rangle = -p_0^2 \langle \alpha | (\hat{a}^\dagger - \hat{a})^2 | \alpha \rangle$$

Expanding (â† - â)²:

$$(\hat{a}^\dagger - \hat{a})^2 = (\hat{a}^\dagger)^2 - \hat{a}^\dagger \hat{a} - \hat{a} \hat{a}^\dagger + \hat{a}^2$$

Using our previous results:

$$\langle (\hat{a}^\dagger - \hat{a})^2 \rangle = (\alpha^*)^2 - |\alpha|^2 - (|\alpha|^2 + 1) + \alpha^2$$

$$= (\alpha^*)^2 + \alpha^2 - 2|\alpha|^2 - 1$$

$$= (\alpha^* - \alpha)^2 - 1$$

So:

$$\langle \hat{p}^2 \rangle = -p_0^2 \left[ (\alpha^* - \alpha)^2 - 1 \right] = p_0^2 \left[ 1 - (\alpha^* - \alpha)^2 \right]$$

Wait, let me be more careful. We have (α* - α)² = (-2i·Im(α))² = -4·Im(α)². So:

$$\langle \hat{p}^2 \rangle = -p_0^2 \left[ -4\,\text{Im}(\alpha)^2 - 1 \right] = p_0^2 \left[ 4\,\text{Im}(\alpha)^2 + 1 \right]$$

### Step 3: Compute (Δp)²

$$(\Delta p)^2 = \langle \hat{p}^2 \rangle - \langle \hat{p} \rangle^2$$

$$= p_0^2 \left[ 4\,\text{Im}(\alpha)^2 + 1 \right] - 4p_0^2 \, \text{Im}(\alpha)^2$$

$$= p_0^2$$

Again, everything α-dependent cancels! We get:

$$\boxed{(\Delta p)^2 = p_0^2 = \frac{m\omega\hbar}{2}}$$

And therefore:

$$\Delta p = \sqrt{\frac{m\omega\hbar}{2}}$$

---

## The Beautiful Result

Now let's multiply our uncertainties:

$$\Delta x \cdot \Delta p = \sqrt{\frac{\hbar}{2m\omega}} \cdot \sqrt{\frac{m\omega\hbar}{2}}$$

$$= \sqrt{\frac{\hbar}{2m\omega} \cdot \frac{m\omega\hbar}{2}}$$

$$= \sqrt{\frac{\hbar^2}{4}}$$

$$= \frac{\hbar}{2}$$

And there it is:

$$\boxed{\Delta x \cdot \Delta p = \frac{\hbar}{2}}$$

**Equality!** Not greater than. Not approximately equal. *Exactly* equal to the minimum allowed by quantum mechanics.

Coherent states saturate the Heisenberg uncertainty bound. They are **minimum uncertainty states**.

---

## Why Is This So Beautiful?

Let me explain why physicists find this result so elegant.

The uncertainty principle says there's a fundamental limit to precision. You might think: "Okay, but maybe all quantum states are equally imprecise. Maybe they all hit that limit."

But that's not true! Most quantum states are *worse* than the limit. They have more uncertainty than they need to. The universe allows them to be more precise, but they're not.

Coherent states are special because they're *exactly* at the limit. They're as precise as the laws of physics allow. No more uncertainty than absolutely necessary.

And remember: the vacuum |0⟩ is just the coherent state with α = 0. So even the vacuum - *empty space* - saturates the uncertainty bound. The quantum fluctuations of the vacuum are the minimum possible. They can't be reduced.

This is the fundamental noise floor of the universe.

---

## The Phase Space Picture

There's a beautiful way to visualize this. Think of phase space: a two-dimensional space where the horizontal axis is position x and the vertical axis is momentum p.

A classical particle sits at a single point in phase space: definite x, definite p.

A quantum state is a *blob* in phase space. The blob has some width in the x-direction (that's Δx) and some width in the p-direction (that's Δp). The uncertainty principle says:

$$\text{Area of blob} \gtrsim \hbar$$

You can't squeeze the blob below a certain area. If you squeeze it in x, it spreads in p. If you squeeze it in p, it spreads in x. The area is conserved.

For a coherent state, the blob is:
- **Circular** (or very nearly so)
- **Minimum area** (exactly πℏ/2 for a Gaussian)
- **Same size for all α** (the vacuum and excited coherent states have the same blob size)

When α changes, the blob moves around in phase space, but it doesn't change shape or size. This is why coherent states behave classically: they're localized wave packets that maintain their shape as they oscillate.

```
    p
    ↑
    |      ___
    |     /   \     ← Coherent state: circular blob
    |    (  •  )      of minimum area
    |     \___/
    |
    +---------------→ x
```

The center of the blob (marked with •) oscillates in an ellipse as time evolves - just like a classical oscillator! But the blob itself maintains its circular shape and minimum size.

---

## Squeezed States: Breaking the Circle

I should mention: there are other minimum uncertainty states besides coherent states. They're called **squeezed states**.

A squeezed state also satisfies Δx·Δp = ℏ/2, but the uncertainties are *unequal*:

- Squeezed in x: small Δx, large Δp
- Squeezed in p: large Δx, small Δp

In phase space, a squeezed state is an *ellipse* rather than a circle. Same area (minimum), different shape.

Coherent states are the special case where Δx and Δp are balanced:

$$\Delta x = \sqrt{\frac{\hbar}{2m\omega}}, \quad \Delta p = \sqrt{\frac{m\omega\hbar}{2}}$$

These are "equal" in the sense that they're both at their natural scales (x₀ and p₀). The phase space blob is circular.

Squeezed states are useful in precision measurements. If you only care about measuring position very precisely and don't care about momentum, you can squeeze in x and let p be more uncertain. You're still at the quantum limit, but you've redistributed the uncertainty.

---

## Summary

Here's what we've learned:

1. **The Heisenberg uncertainty principle** sets a fundamental limit: Δx·Δp ≥ ℏ/2

2. **Most states don't saturate this bound** - they have more uncertainty than necessary

3. **Coherent states are special**: they achieve Δx·Δp = ℏ/2 exactly

4. **The uncertainties are α-independent**: every coherent state (including the vacuum) has the same Δx and Δp

5. **In phase space**: coherent states are circular blobs of minimum area

6. **This is why coherent states are "classical-like"**: they're as localized as quantum mechanics allows, with balanced uncertainty in position and momentum

The vacuum state, the ground state of the harmonic oscillator, is the simplest example of a minimum uncertainty state. Its fluctuations are the smallest possible. And coherent states - displaced vacuums - inherit this beautiful property.

This is the precision limit of empty space itself.

---

*Next: We'll see how coherent states evolve in time and maintain their minimum uncertainty property forever...*
