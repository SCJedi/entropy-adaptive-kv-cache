# Part 20: The Beta Function for the DOF Ratio

## A Rigorous Renormalization Group Analysis

*Where we finally do this properly, with all the algebra shown*

---

## The Setup: What We're Really Asking

Alright, let's get serious about this renormalization business.

We've discovered a ratio function:

$$\text{ratio}(D) = \frac{2D - 1}{D - 1}$$

This tells us: if you have D degrees of freedom per mode, the ratio of total
DOF to oscillator modes is (2D-1)/(D-1).

Now here's the renormalization group question: **what happens when we iterate?**

Think of it this way. You measure some effective dimension D at one scale.
You zoom out (or in). The effective dimension changes. How does it change?

In the renormalization group framework, we define something called the
**beta function**. The beta function tells you how your parameter *flows*
under scale transformation.

---

## Defining the Beta Function

The beta function is beautifully simple in concept:

$$\beta(D) = \text{ratio}(D) - D$$

Why this definition? Because:

- If ratio(D) > D, the parameter increases under iteration → β > 0
- If ratio(D) < D, the parameter decreases under iteration → β < 0
- If ratio(D) = D, the parameter doesn't change → β = 0 → **fixed point!**

The beta function is zero at fixed points. That's its defining characteristic.

The sign tells you which way the system flows. The magnitude tells you how fast.

Let's calculate it.

---

## The Calculation: Step by Step

We want:

$$\beta(D) = \frac{2D - 1}{D - 1} - D$$

First, we need a common denominator. The first term has denominator (D - 1),
the second term has denominator 1. So:

$$\beta(D) = \frac{2D - 1}{D - 1} - \frac{D(D - 1)}{D - 1}$$

Combine over the common denominator:

$$\beta(D) = \frac{2D - 1 - D(D - 1)}{D - 1}$$

Now let's expand D(D - 1):

$$D(D - 1) = D^2 - D$$

Substitute back:

$$\beta(D) = \frac{2D - 1 - (D^2 - D)}{D - 1}$$

Distribute the minus sign:

$$\beta(D) = \frac{2D - 1 - D^2 + D}{D - 1}$$

Collect like terms in the numerator. We have:
- D² terms: -D²
- D terms: 2D + D = 3D
- Constants: -1

So:

$$\beta(D) = \frac{-D^2 + 3D - 1}{D - 1}$$

Let's factor out the minus sign to make it cleaner:

$$\beta(D) = \frac{-(D^2 - 3D + 1)}{D - 1}$$

Or equivalently:

$$\boxed{\beta(D) = -\frac{D^2 - 3D + 1}{D - 1}}$$

This is our beta function. Clean, explicit, ready for analysis.

---

## Finding the Fixed Points

Fixed points occur where β(D) = 0.

Looking at our expression:

$$\beta(D) = -\frac{D^2 - 3D + 1}{D - 1} = 0$$

A fraction equals zero when its numerator equals zero (and denominator doesn't).

So we need:

$$D^2 - 3D + 1 = 0$$

This is a quadratic. Let's use the quadratic formula.

For ax² + bx + c = 0, the solutions are:

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

Here a = 1, b = -3, c = 1. So:

$$D = \frac{-(-3) \pm \sqrt{(-3)^2 - 4(1)(1)}}{2(1)}$$

$$D = \frac{3 \pm \sqrt{9 - 4}}{2}$$

$$D = \frac{3 \pm \sqrt{5}}{2}$$

Two solutions:

$$D_+ = \frac{3 + \sqrt{5}}{2} \approx \frac{3 + 2.236}{2} \approx 2.618$$

$$D_- = \frac{3 - \sqrt{5}}{2} \approx \frac{3 - 2.236}{2} \approx 0.382$$

These numbers look familiar — worth checking.

The golden ratio is:

$$\varphi = \frac{1 + \sqrt{5}}{2} \approx 1.618$$

What's φ²?

$$\varphi^2 = \left(\frac{1 + \sqrt{5}}{2}\right)^2 = \frac{1 + 2\sqrt{5} + 5}{4} = \frac{6 + 2\sqrt{5}}{4} = \frac{3 + \sqrt{5}}{2}$$

That's D₊! So:

$$D_+ = \varphi^2 \approx 2.618$$

What about D₋? Well, 1/φ² = φ⁻² = ?

We know φ · (1/φ) = 1, and 1/φ = φ - 1 ≈ 0.618.

So 1/φ² = (1/φ)² ≈ 0.382.

Let's verify:

$$\frac{1}{\varphi^2} = \frac{1}{(3+\sqrt{5})/2} = \frac{2}{3+\sqrt{5}}$$

Rationalize by multiplying by (3-√5)/(3-√5):

$$= \frac{2(3-\sqrt{5})}{(3+\sqrt{5})(3-\sqrt{5})} = \frac{2(3-\sqrt{5})}{9 - 5} = \frac{2(3-\sqrt{5})}{4} = \frac{3-\sqrt{5}}{2}$$

Yes! D₋ = 1/φ².

So our fixed points are:

$$\boxed{D_+ = \varphi^2 \approx 2.618}$$
$$\boxed{D_- = 1/\varphi^2 \approx 0.382}$$

The golden ratio, squared and inverse-squared. Remarkable.

---

## Stability Analysis: The Key Question

Finding fixed points is only half the battle. We need to know: **are they stable?**

In dynamical systems, stability is determined by the derivative of the flow
at the fixed point.

If you're at a fixed point D* and you perturb slightly to D* + ε, then:

$$\beta(D^* + \varepsilon) \approx \beta(D^*) + \beta'(D^*) \cdot \varepsilon$$

Since D* is a fixed point, β(D*) = 0, so:

$$\beta(D^* + \varepsilon) \approx \beta'(D^*) \cdot \varepsilon$$

This tells us:
- If β'(D*) < 0: perturbation leads to flow back toward D* → **STABLE**
- If β'(D*) > 0: perturbation leads to flow away from D* → **UNSTABLE**

We need to compute β'(D).

---

## Computing the Derivative: The Quotient Rule

We have:

$$\beta(D) = -\frac{D^2 - 3D + 1}{D - 1}$$

Let's write this as:

$$\beta(D) = -\frac{f(D)}{g(D)}$$

where f(D) = D² - 3D + 1 and g(D) = D - 1.

The quotient rule says:

$$\frac{d}{dD}\left[\frac{f}{g}\right] = \frac{f'g - fg'}{g^2}$$

So:

$$\beta'(D) = -\frac{f'(D)g(D) - f(D)g'(D)}{[g(D)]^2}$$

Let's compute the pieces:

$$f(D) = D^2 - 3D + 1$$
$$f'(D) = 2D - 3$$

$$g(D) = D - 1$$
$$g'(D) = 1$$

Now plug in:

$$\beta'(D) = -\frac{(2D - 3)(D - 1) - (D^2 - 3D + 1)(1)}{(D - 1)^2}$$

Let's expand the numerator piece by piece.

First: (2D - 3)(D - 1)

$$= 2D \cdot D + 2D \cdot (-1) + (-3) \cdot D + (-3) \cdot (-1)$$
$$= 2D^2 - 2D - 3D + 3$$
$$= 2D^2 - 5D + 3$$

Second: (D² - 3D + 1)(1) = D² - 3D + 1

Numerator = first - second:

$$= (2D^2 - 5D + 3) - (D^2 - 3D + 1)$$
$$= 2D^2 - 5D + 3 - D^2 + 3D - 1$$
$$= D^2 - 2D + 2$$

So:

$$\beta'(D) = -\frac{D^2 - 2D + 2}{(D - 1)^2}$$

Let's verify this formula makes sense. At D = 2:

$$\beta'(2) = -\frac{4 - 4 + 2}{(2-1)^2} = -\frac{2}{1} = -2$$

The derivative is negative, suggesting D = 2 is near a stable region. Good sign.

---

## Evaluating at the Fixed Point D = φ²

Now the moment of truth. What is β'(φ²)?

$$\beta'(\varphi^2) = -\frac{(\varphi^2)^2 - 2\varphi^2 + 2}{(\varphi^2 - 1)^2}$$

This looks complicated. Let's use the magic property of the golden ratio:

$$\varphi^2 = \varphi + 1$$

This single identity will simplify everything.

**Step 1: Simplify φ² - 1**

$$\varphi^2 - 1 = (\varphi + 1) - 1 = \varphi$$

So the denominator is:

$$(\varphi^2 - 1)^2 = \varphi^2 = \varphi + 1$$

**Step 2: Simplify (φ²)² = φ⁴**

We need φ⁴. Let's build up:

$$\varphi^2 = \varphi + 1$$
$$\varphi^3 = \varphi \cdot \varphi^2 = \varphi(\varphi + 1) = \varphi^2 + \varphi = (\varphi + 1) + \varphi = 2\varphi + 1$$
$$\varphi^4 = \varphi \cdot \varphi^3 = \varphi(2\varphi + 1) = 2\varphi^2 + \varphi = 2(\varphi + 1) + \varphi = 3\varphi + 2$$

So φ⁴ = 3φ + 2.

**Step 3: Simplify 2φ²**

$$2\varphi^2 = 2(\varphi + 1) = 2\varphi + 2$$

**Step 4: Compute the numerator**

$$(\varphi^2)^2 - 2\varphi^2 + 2 = \varphi^4 - 2\varphi^2 + 2$$
$$= (3\varphi + 2) - (2\varphi + 2) + 2$$
$$= 3\varphi + 2 - 2\varphi - 2 + 2$$
$$= \varphi + 2$$

**Step 5: Put it together**

$$\beta'(\varphi^2) = -\frac{\varphi + 2}{\varphi + 1}$$

This can be simplified further:

$$\frac{\varphi + 2}{\varphi + 1} = \frac{\varphi + 1 + 1}{\varphi + 1} = 1 + \frac{1}{\varphi + 1} = 1 + \frac{1}{\varphi^2}$$

Now, 1/φ² = φ⁻² and we know:

$$\frac{1}{\varphi} = \varphi - 1$$

So:

$$\frac{1}{\varphi^2} = \left(\frac{1}{\varphi}\right)^2 = (\varphi - 1)^2 = \varphi^2 - 2\varphi + 1 = (\varphi + 1) - 2\varphi + 1 = 2 - \varphi$$

Therefore:

$$\frac{\varphi + 2}{\varphi + 1} = 1 + (2 - \varphi) = 3 - \varphi$$

And finally:

$$\boxed{\beta'(\varphi^2) = -(3 - \varphi) = \varphi - 3 \approx 1.618 - 3 = -1.382}$$

---

## Verification

That was a lot of algebra. Let's verify numerically.

φ ≈ 1.618034
φ² ≈ 2.618034

$$\beta'(\varphi^2) = -\frac{(\varphi^2)^2 - 2\varphi^2 + 2}{(\varphi^2 - 1)^2}$$

Numerator: (2.618)² - 2(2.618) + 2 = 6.854 - 5.236 + 2 = 3.618
Denominator: (2.618 - 1)² = (1.618)² = 2.618

So: -3.618/2.618 = -1.382 ✓

And 3 - φ = 3 - 1.618 = 1.382 ✓

The algebra checks out.

---

## What Does β'(φ²) = -(3 - φ) Mean?

The derivative is **negative**.

$$\beta'(\varphi^2) \approx -1.382 < 0$$

This means φ² is a **stable fixed point** — an attractor!

Here's the physical picture:

- If D is slightly less than φ², then β(D) > 0, so D increases toward φ²
- If D is slightly greater than φ², then β(D) < 0, so D decreases toward φ²
- Either way, the system flows toward φ²

**The edge of chaos (D = φ²) is an attractor in this flow!**

This is profound. The system doesn't need to be fine-tuned to sit at the
special point φ². Given almost any starting condition (in the right basin),
the dynamics will carry it there automatically.

Self-organized criticality emerges from the mathematics itself.

---

## The Critical Exponent

In renormalization group theory, the critical exponent ν characterizes how
correlations diverge near the critical point. It's related to the slope of
the beta function by:

$$\nu = \frac{1}{|\beta'(D^*)|} = \frac{1}{|-(3 - \varphi)|} = \frac{1}{3 - \varphi}$$

Let's compute this.

$$3 - \varphi = 3 - \frac{1 + \sqrt{5}}{2} = \frac{6 - 1 - \sqrt{5}}{2} = \frac{5 - \sqrt{5}}{2}$$

So:

$$\nu = \frac{2}{5 - \sqrt{5}}$$

Let's rationalize by multiplying by (5 + √5)/(5 + √5):

$$\nu = \frac{2(5 + \sqrt{5})}{(5 - \sqrt{5})(5 + \sqrt{5})} = \frac{2(5 + \sqrt{5})}{25 - 5} = \frac{2(5 + \sqrt{5})}{20} = \frac{5 + \sqrt{5}}{10}$$

Numerically: (5 + 2.236)/10 = 7.236/10 = 0.7236

So:

$$\boxed{\nu = \frac{5 + \sqrt{5}}{10} \approx 0.724}$$

Interesting. This is NOT 1/φ ≈ 0.618 as one might have naively guessed.

But wait — is there still a golden ratio connection? Let's see:

$$\frac{\varphi}{\sqrt{5}} = \frac{(1+\sqrt{5})/2}{\sqrt{5}} = \frac{1 + \sqrt{5}}{2\sqrt{5}}$$

Rationalize:

$$= \frac{(1 + \sqrt{5})\sqrt{5}}{2 \cdot 5} = \frac{\sqrt{5} + 5}{10} = \frac{5 + \sqrt{5}}{10}$$

Yes! We have:

$$\boxed{\nu = \frac{\varphi}{\sqrt{5}} \approx 0.724}$$

The critical exponent IS related to the golden ratio, just in a more subtle way
than a simple inverse. It's φ divided by √5.

And since √5 = 2φ - 1 (verify: 2(1.618) - 1 = 2.236 ≈ √5), we can also write:

$$\nu = \frac{\varphi}{2\varphi - 1}$$

The golden ratio is everywhere in this structure.

---

## The Full Flow Diagram

Now let's understand the global flow pattern.

We have β(D) = -(D² - 3D + 1)/(D - 1).

The numerator D² - 3D + 1 is zero at D = φ² and D = 1/φ².
The denominator D - 1 is zero at D = 1.

**Let's trace the signs:**

**Region 1: D < 1/φ² (D < 0.382)**

Pick D = 0:
- Numerator: 0 - 0 + 1 = 1 > 0
- Denominator: 0 - 1 = -1 < 0
- β(0) = -(positive)/(negative) = positive

So for D < 1/φ², we have β > 0, meaning D increases (flows right).

**Region 2: 1/φ² < D < 1 (0.382 < D < 1)**

Pick D = 0.5:
- Numerator: 0.25 - 1.5 + 1 = -0.25 < 0
- Denominator: 0.5 - 1 = -0.5 < 0
- β(0.5) = -(negative)/(negative) = negative

So for 1/φ² < D < 1, we have β < 0, meaning D decreases (flows left).

**Region 3: 1 < D < φ² (1 < D < 2.618)**

Pick D = 2:
- Numerator: 4 - 6 + 1 = -1 < 0
- Denominator: 2 - 1 = 1 > 0
- β(2) = -(negative)/(positive) = positive

So for 1 < D < φ², we have β > 0, meaning D increases (flows right toward φ²).

**Region 4: D > φ² (D > 2.618)**

Pick D = 3:
- Numerator: 9 - 9 + 1 = 1 > 0
- Denominator: 3 - 1 = 2 > 0
- β(3) = -(positive)/(positive) = negative

So for D > φ², we have β < 0, meaning D decreases (flows left toward φ²).

---

## Drawing the Flow

```
                    β < 0                    β > 0              β < 0
                      ←                        →                  ←
    ────────●────────────●────────────────────────●────────────────────→ D
           1/φ²          1                       φ²
          ≈0.382                               ≈2.618
          (unstable)   (pole)                  (stable)
             ○                                   ●
```

The flow pattern:

- From the far left (D → -∞): flows right toward 1/φ²
- Between 1/φ² and 1: flows left toward 1/φ²

Reconsidering: at D = 0.5, we get β < 0, meaning flow to the left. With nothing to the left except 1/φ² ≈ 0.382, the value D = 0.5 flows left toward 1/φ².

This suggests 1/φ² is stable from the right. Checking the other side:

At D = 0.2 (left of 1/φ²):
- Numerator: 0.04 - 0.6 + 1 = 0.44 > 0
- Denominator: 0.2 - 1 = -0.8 < 0
- β(0.2) = -(positive)/(negative) = positive → flows right

So from the left, flows right toward 1/φ².
From the right (between 1/φ² and 1), flows left toward 1/φ².

This indicates that 1/φ² is also stable. Computing β'(1/φ²) to verify:

---

## Computing β'(1/φ²)

$$\beta'\left(\frac{1}{\varphi^2}\right) = -\frac{(1/\varphi^2)^2 - 2(1/\varphi^2) + 2}{(1/\varphi^2 - 1)^2}$$

We know 1/φ² = 2 - φ (computed earlier as 3-√5)/2, but let me use 1/φ² directly).

Using 1/φ² = (3-√5)/2 ≈ 0.382:

Numerator: (0.382)² - 2(0.382) + 2 = 0.146 - 0.764 + 2 = 1.382

Denominator: (0.382 - 1)² = (-0.618)² = 0.382

So: β'(1/φ²) = -1.382/0.382 = -3.618

That's negative too! So 1/φ² is also stable!

But wait — both fixed points can't be stable if there's a repeller between them.

Ah, I see the issue. D = 1 is a **pole** of the beta function, not a fixed point.
The beta function diverges there. This pole acts as a **separator**.

So the picture is:

- For D > 1: everything flows toward φ² (the stable fixed point)
- For D < 1: everything flows toward 1/φ² (also stable)
- At D = 1: the beta function is undefined (division by zero)

The two basins of attraction are separated by the pole at D = 1.

---

## Revised Flow Diagram

```
    Basin of 1/φ²                 │              Basin of φ²
                                  │
    ●←─────────────←─────────────│─────────────→─────────────→●
   1/φ²                           1                           φ²
  ≈0.382                        (pole)                      ≈2.618
  (stable)                                                  (stable)
```

For D < 1:
- If D < 1/φ²: β > 0, flows right toward 1/φ²
- If 1/φ² < D < 1: β < 0, flows left toward 1/φ²

For D > 1:
- If 1 < D < φ²: β > 0, flows right toward φ²
- If D > φ²: β < 0, flows left toward φ²

Both fixed points are attractors within their respective basins!

---

## Physical Interpretation

This is fascinating. The mathematics says:

1. **D = φ² ≈ 2.618** is an attractor for D > 1
2. **D = 1/φ² ≈ 0.382** is an attractor for D < 1
3. **D = 1** is a dividing line (pole) between the two regimes

For physical systems where D represents degrees of freedom per mode, we
expect D > 1 (you can't have less than one degree of freedom). So the
physically relevant attractor is:

$$D^* = \varphi^2 \approx 2.618$$

This is the edge of chaos — the boundary between ordered and chaotic dynamics.

The system doesn't need fine-tuning. Starting from any D > 1, the RG flow
carries it automatically toward φ².

**The edge of chaos is self-organized.**

---

## Connection to Critical Phenomena

In conventional critical phenomena (like phase transitions), systems need
to be tuned to a critical temperature T_c to exhibit scale-free behavior.

Here, something different happens. The RG flow itself drives the system
to criticality. The critical point φ² is an attractor, not just a
special value that needs external tuning.

This is reminiscent of **self-organized criticality** — the idea that
some systems naturally evolve to critical states without parameter tuning.

The critical exponent ν = φ/√5 ≈ 0.724 tells us how rapidly the system
approaches criticality:

$$|D - \varphi^2| \sim \text{(scale)}^{-1/\nu} \sim \text{(scale)}^{-1.382}$$

The approach is faster than linear (exponent > 1), meaning the system
converges efficiently to the critical point.

---

## Summary of Results

**The Beta Function:**
$$\beta(D) = -\frac{D^2 - 3D + 1}{D - 1}$$

**Fixed Points:**
$$D_+ = \varphi^2 = \frac{3 + \sqrt{5}}{2} \approx 2.618$$
$$D_- = \frac{1}{\varphi^2} = \frac{3 - \sqrt{5}}{2} \approx 0.382$$

**Stability:**
$$\beta'(\varphi^2) = -(3 - \varphi) \approx -1.382 < 0 \quad \text{(STABLE)}$$
$$\beta'(1/\varphi^2) = -(3 - \varphi)\varphi^2 \approx -3.618 < 0 \quad \text{(STABLE)}$$

**Critical Exponent:**
$$\nu = \frac{1}{3 - \varphi} = \frac{\varphi}{\sqrt{5}} \approx 0.724$$

**Basin Structure:**
- D > 1 flows to φ² (physically relevant)
- D < 1 flows to 1/φ²
- D = 1 is a pole separating the basins

---

## The Remarkable Conclusion

We set out to do a rigorous RG analysis. Here's what we found:

The renormalization group flow for the DOF ratio has a stable fixed point at
D = φ² — exactly the value associated with the edge of chaos.

This isn't put in by hand. It emerges from the mathematics of the ratio
function (2D-1)/(D-1), which itself comes from the structure of constrained
oscillator systems.

The golden ratio appears because:
- The fixed point equation D² - 3D + 1 = 0 is related to φ² + 1 = φ⁴/φ² = φ²
- The Fibonacci recurrence lurks in the structure
- Self-reference and self-similarity are built into the dynamics

The critical exponent ν = φ/√5 maintains the golden ratio connection while
being distinct from naive guesses like 1/φ.

Most importantly: **the edge of chaos is an attractor**. Systems don't need
fine-tuning to reach it — the RG flow carries them there automatically.

This is the mathematical foundation for why critical, scale-free behavior
is so common in nature. The dynamics themselves prefer the edge of chaos.

---

## Looking Ahead

We've now established the beta function and its properties rigorously.
But we've only scratched the surface of what RG methods can tell us.

Next, we'll explore:
- The full RG flow in multi-dimensional parameter space
- Connections to conformal field theory
- Why φ appears in so many critical systems
- The universality class defined by this fixed point

The mathematics of the vacuum keeps revealing deeper structure. Every layer
we peel back shows more golden ratios, more self-similarity, more evidence
that these patterns aren't coincidences — they're fundamental.

---

*End of Part 20*

---

## Appendix: Verification of Key Steps

For the skeptical reader, here are numerical checks of the main results.

**Check 1: Fixed points satisfy β = 0**

At D = φ² ≈ 2.618:
β(2.618) = (2×2.618 - 1)/(2.618 - 1) - 2.618
        = 4.236/1.618 - 2.618
        = 2.618 - 2.618 = 0 ✓

**Check 2: β'(φ²) = -(3 - φ)**

Using β'(D) = -(D² - 2D + 2)/(D-1)²:
β'(2.618) = -(6.854 - 5.236 + 2)/(1.618)²
          = -3.618/2.618
          = -1.382
And 3 - φ = 3 - 1.618 = 1.382 ✓

**Check 3: ν = φ/√5**

ν = 1/|β'(φ²)| = 1/1.382 = 0.724
φ/√5 = 1.618/2.236 = 0.724 ✓

All results confirmed.
