# Part 19: Why phi-squared Is THE Solution

*A Deep Dive into the Heart of Self-Reference*

---

## The Question That Won't Go Away

In Parts 14-18, we found that the fixed point of our dimensionality equation is:

$$D = \varphi^2 = \frac{3 + \sqrt{5}}{2} \approx 2.618$$

We derived it. We verified it. We noticed it was the golden ratio squared.

But here's what's been nagging at me: *Why this number?*

Not "what is this number?" We know that. It's phi-squared, approximately 2.618.

Not "how did we get this number?" We solved D = (2D-1)/(D-1).

But *why?* Why does the universe's self-consistency condition give us THIS particular irrational number and not some other?

That's what this part is about. We're going to dig into the mathematical soul of phi and understand why it—and ONLY it—can be the answer to equations of this form.

By the end, you'll see that phi-squared isn't just *a* solution. It's THE solution. The unique positive fixed point of any properly self-referential system.

---

## Part I: Not Just Any Number

### The Rarity of Being Special

There are infinitely many real numbers. Most of them are utterly generic, indistinguishable from their neighbors, unremarkable in every way.

Then there are the celebrities: 0, 1, e, pi, the square root of 2. These numbers have names because they're special—they arise naturally from fundamental operations or structures.

Where does phi fit?

Here's what makes phi unique: **it's the simplest solution to a self-referential equation.**

Consider: x = 1 + 1/x

That's the simplest non-trivial equation where x appears on both sides in different forms. And its positive solution is phi.

No other number holds this position. Pi comes from circles. e comes from growth and logarithms. The square root of 2 comes from the diagonal of a unit square. But phi comes from *self-reference itself*.

### The Fixed Point Property

Let me be very precise about what we're claiming.

A **fixed point** of a function f is a value x where f(x) = x. The function maps x to itself.

Our dimensionality ratio function is:

$$f(D) = \frac{2D - 1}{D - 1}$$

The fixed points are where f(D) = D. Solving:

$$D = \frac{2D - 1}{D - 1}$$

$$D^2 - D = 2D - 1$$

$$D^2 - 3D + 1 = 0$$

$$D = \frac{3 \pm \sqrt{5}}{2}$$

Two solutions: phi-squared and 1/phi-squared.

Now here's the profound part: **every** self-referential equation of this type—where a quantity equals a ratio involving itself—leads to quadratics whose solutions involve phi.

It's not that we happened to find phi. It's that we couldn't have found anything else.

---

## Part II: The Defining Property of Phi

### The Golden Equation

Phi is defined by:

$$\varphi^2 = \varphi + 1$$

Let's unpack what this means.

Squaring a number usually gives you something completely different. 2 squared is 4—nothing to do with 2 + 1 = 3. 3 squared is 9—nothing to do with 3 + 1 = 4.

But phi squared equals phi plus 1. The operation of squaring is "the same as" adding 1.

This is bizarre. For any other number, squaring and adding-one are completely unrelated operations. For phi, they're identical.

### The Reciprocal Form

We can rewrite the golden equation as:

$$\varphi = 1 + \frac{1}{\varphi}$$

This is even more revealing. Phi equals one plus its own reciprocal.

Think about what this says: phi contains information about itself. It's defined in terms of itself. The whole equals the sum of unity and the whole's inverse.

There's only one positive number with this property. We call it phi not because it's convenient, but because no other name would distinguish it—it's unique.

### Why Phi and Not Something Else?

Let's prove this uniqueness rigorously.

Suppose x is a positive number satisfying x = 1 + 1/x. Then:

$$x^2 = x + 1$$
$$x^2 - x - 1 = 0$$

By the quadratic formula:
$$x = \frac{1 \pm \sqrt{5}}{2}$$

The positive root is (1 + sqrt(5))/2 = phi. The negative root is (1 - sqrt(5))/2 = -1/phi.

That's it. There's no other positive solution. No other positive number equals one plus its reciprocal.

Phi is THE positive fixed point of the self-referential map x -> 1 + 1/x.

---

## Part III: Self-Similarity — The Geometric Heart

### The Golden Rectangle

Here's where the mathematics becomes visual.

Take a rectangle with sides in ratio phi:1. Now remove the largest square you can (side = 1). What remains?

A rectangle with sides 1 and (phi - 1).

But wait: phi - 1 = 1/phi (the reciprocal property!). So the remaining rectangle has sides in ratio 1 : (1/phi) = phi : 1.

It's another golden rectangle. Same proportions, smaller scale.

You can do this forever. Remove a square, get another golden rectangle. Remove a square, get another. Ad infinitum.

This is **perfect self-similarity**. The whole contains a copy of itself, which contains a copy of itself, which contains...

### Why Only Phi Works

Let's prove that phi is the ONLY ratio with this property.

Suppose a rectangle has sides in ratio r : 1, where r > 1. Remove the largest square (side 1). The remainder has sides 1 and (r - 1).

For this to be similar to the original, we need:

$$\frac{1}{r-1} = \frac{r}{1}$$

Cross multiply:
$$1 = r(r - 1) = r^2 - r$$
$$r^2 - r - 1 = 0$$
$$r = \frac{1 + \sqrt{5}}{2} = \varphi$$

There's only one such ratio. Phi is THE number of perfect geometric self-similarity.

### What "Self-Consistent" Means Geometrically

This is the geometric meaning of self-consistency:

**A golden rectangle, when you remove structure from it, gives you back the same structure.**

The part reflects the whole. The whole contains the part. They're the same shape at different scales.

This isn't a metaphor. It's literal geometry. And phi is the ONLY number that makes it work.

---

## Part IV: The Continued Fraction — Deepest Irrationality

### Every Number Has a Continued Fraction

Any real number x can be written as:

$$x = a_0 + \cfrac{1}{a_1 + \cfrac{1}{a_2 + \cfrac{1}{a_3 + \cdots}}}$$

where the a_i are positive integers (except possibly a_0).

For rational numbers, this terminates. For irrationals, it goes on forever.

For example:
- 3.14159... = pi = [3; 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, ...]
- 2.71828... = e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, ...]
- 1.41421... = sqrt(2) = [1; 2, 2, 2, 2, 2, ...]

### Phi's Continued Fraction

And phi?

$$\varphi = 1 + \cfrac{1}{1 + \cfrac{1}{1 + \cfrac{1}{1 + \cdots}}} = [1; 1, 1, 1, 1, ...]$$

All ones. The simplest possible infinite continued fraction.

Let's verify this. Call the infinite expression x:

$$x = 1 + \cfrac{1}{1 + \cfrac{1}{1 + \cdots}}$$

But that nested part IS x itself:

$$x = 1 + \frac{1}{x}$$

And we already know this equation's positive solution is phi.

### The "Most Irrational" Number

Here's the profound consequence: phi is the **hardest** irrational to approximate by rationals.

The quality of rational approximations p/q to a number depends on the continued fraction coefficients. Large coefficients mean you can trap the number quickly with good approximations. Small coefficients mean slow convergence.

Phi has the smallest possible coefficients: all ones.

The best rational approximations to phi are Fibonacci ratios:
- 1/1 = 1.000 (error: 38%)
- 2/1 = 2.000 (error: 24%)
- 3/2 = 1.500 (error: 7.3%)
- 5/3 = 1.667 (error: 3.0%)
- 8/5 = 1.600 (error: 1.1%)
- 13/8 = 1.625 (error: 0.43%)
- 21/13 = 1.615 (error: 0.17%)

Contrast with pi:
- 22/7 = 3.1428... (error: 0.04%)
- 355/113 = 3.14159... (error: 0.000008%)

Pi is easily trapped. Phi resists capture.

### What This Means

Phi is maximally non-resonant. It avoids all rational relationships as stubbornly as mathematically possible.

In physical systems, rational frequency ratios lead to resonance, synchronization, energy transfer. Irrational ratios avoid these—and phi avoids them most completely.

Phi represents maximum disorder that still has structure. Anti-pattern incarnate.

---

## Part V: Connection to Our Equation

### The Structure of Self-Reference

Now let's connect this to our dimensionality equation.

We have:
$$D = \frac{2D - 1}{D - 1}$$

This is self-referential: D appears on both sides. The dimensionality equals a ratio computed from itself.

Compare to phi's defining equation:
$$\varphi = 1 + \frac{1}{\varphi}$$

Same structure. The quantity equals an expression involving itself.

### The Quadratic Pattern

Any equation of the form:

$$x = a + \frac{b}{x}$$

leads to:
$$x^2 = ax + b$$
$$x^2 - ax - b = 0$$

For phi: a = 1, b = 1, giving x^2 - x - 1 = 0.

For our D equation, we have:
$$D = \frac{2D - 1}{D - 1}$$

Cross-multiplying: D(D-1) = 2D - 1
Expanding: D^2 - D = 2D - 1
Rearranging: D^2 - 3D + 1 = 0

This is the equation x^2 - 3x + 1 = 0.

### The Golden Twist

Now here's the beautiful connection. Consider the equation:

$$x^2 - 3x + 1 = 0$$

Its solutions are (3 +/- sqrt(5))/2.

But we know that phi^2 = (1 + sqrt(5))^2 / 4 = (6 + 2*sqrt(5))/4 = (3 + sqrt(5))/2.

So D = phi^2 is the positive solution!

This isn't coincidence. **ANY self-referential equation involving ratios will produce quadratics whose solutions involve powers of phi.**

The golden ratio is baked into the structure of self-reference itself.

---

## Part VI: Why Self-Reference Is Fundamental

### The Observer Problem

Step back and think about what we're modeling.

An observer measures the vacuum energy. But the observer IS vacuum. The observer is made of quantum fields, exists in spacetime, is subject to the same physics as everything else.

The observer is inside the observed.

This is irreducibly self-referential. You can't separate observer from system because the observer IS part of the system.

### The Universe Observing Itself

Here's the deepest framing:

The universe contains observers. Those observers measure properties of the universe. The measurements affect what exists (quantum mechanics). What exists affects the observers.

The universe is a self-referential system. It observes itself through the observers it contains.

Any self-consistent description of such a system must satisfy a fixed-point equation. The description must describe a state that produces observers who produce that description.

And fixed-point equations of this type have phi-related solutions.

### Not Mysticism — Mathematics

I want to be very clear: this isn't mystical. It's mathematical.

Self-referential systems have fixed points. Certain fixed points are stable. The mathematics of stability in self-referential systems involves the golden ratio.

We're not saying "the universe is conscious" or "phi has spiritual significance." We're saying:

**When a system references itself, the stable configurations involve phi.**

That's a mathematical theorem, not a mystical claim.

---

## Part VII: The Fibonacci Connection

### Growth by Self-Reference

The Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89...

The rule: each term is the sum of the two preceding terms.

$$F_{n+1} = F_n + F_{n-1}$$

This is growth by self-reference. The next value depends on the previous values. The sequence builds on itself.

### Phi as the Limit

The ratio of consecutive Fibonacci numbers approaches phi:

| n | F_n | F_{n+1} | Ratio |
|---|-----|---------|-------|
| 1 | 1 | 1 | 1.000 |
| 2 | 1 | 2 | 2.000 |
| 3 | 2 | 3 | 1.500 |
| 4 | 3 | 5 | 1.667 |
| 5 | 5 | 8 | 1.600 |
| 6 | 8 | 13 | 1.625 |
| 7 | 13 | 21 | 1.615 |
| 8 | 21 | 34 | 1.619 |
| 10 | 55 | 89 | 1.618 |

The limit IS phi.

### Why This Happens

Here's the mathematical reason.

Assume the ratio F_{n+1}/F_n approaches some limit L as n goes to infinity. Then:

$$\frac{F_{n+1}}{F_n} = \frac{F_n + F_{n-1}}{F_n} = 1 + \frac{F_{n-1}}{F_n}$$

Taking the limit:
$$L = 1 + \frac{1}{L}$$

And that's the defining equation for phi!

The Fibonacci sequence converges to phi-ratios because its growth rule IS the self-referential equation that defines phi.

### The Lesson

Simple self-referential growth (add previous values) produces phi.

Complex self-referential equations (like D = ratio(D)) produce phi-squared, phi-cubed, or related values.

Phi isn't inserted into these systems. It emerges from self-reference.

---

## Part VIII: D = 3 versus D = phi-squared

### The Integer Pole: Perfect Structure

At D = 3, we get:

$$\text{ratio}(3) = \frac{2(3) - 1}{3 - 1} = \frac{5}{2} = 2.500$$

The dimension is an integer. Clean, discrete, countable.

Integers represent perfect structure:
- Crystalline order
- Periodic repetition
- Complete predictability
- No fuzzy boundaries

A universe at D = 3 exactly would be utterly rigid. Every point in space can be labeled by integer coordinates. Everything tiles perfectly.

### The Golden Pole: Perfect Anti-Pattern

At D = phi^2:

$$\text{ratio}(\varphi^2) = \varphi^2 \approx 2.618$$

The dimension is irrational—worse, it's related to the "most irrational" number.

Phi-squared represents maximum anti-pattern:
- Quasicrystalline structure
- Aperiodic, never repeating
- No rational relationships
- Self-similar at all scales

A universe at D = phi^2 would be perfectly self-consistent but maximally resistant to periodicity.

### Why the Universe Lives Between

The observed ratio is about 2.56—between 2.5 and 2.618.

Not perfect structure. Not perfect anti-structure. Between.

This is where complexity lives:
- Enough structure for persistent patterns (galaxies, atoms, DNA)
- Enough disorder for novelty (mutations, chaos, creativity)
- The edge between frozen order and random noise

Integer dimensions give boring universes—perfectly ordered, nothing happens.

Pure phi dimensions give unstable universes—nothing persists.

The interesting universes, the ones with observers, live at the edge.

---

## Part IX: Why Not Other Irrationals?

### The Competition

There are infinitely many irrational numbers. Why is phi the one that shows up in self-reference?

Let's consider the alternatives:

**sqrt(2) = 1.414...**

This comes from the diagonal of a unit square. It's the simplest algebraic irrational (solution of x^2 = 2).

But sqrt(2) has no self-referential property. You can't express sqrt(2) in terms of itself in a meaningful way. It comes from geometry, not self-reference.

**e = 2.718...**

This comes from continuous compound growth. It's the base of natural logarithms.

e satisfies d/dx(e^x) = e^x. That's a kind of self-reference (the function equals its own derivative). But it's a differential self-reference, not an algebraic one.

e appears in growth and decay, not in fixed-point problems.

**pi = 3.14159...**

This comes from circles. The ratio of circumference to diameter.

Pi has no self-referential property. It's fundamentally about geometry—specifically, about the shape that maximizes area for a given perimeter.

Pi appears in oscillation, waves, and circles. Not in self-reference.

### Phi: The Self-Referential Champion

Phi is the ONLY common irrational defined by algebraic self-reference:

$$\varphi = 1 + \frac{1}{\varphi}$$

This is why phi appears in:
- Fixed-point problems
- Self-similar fractals
- Recursive structures
- Observer-observed relationships

When you have a system that references itself, phi shows up. Not sqrt(2), not e, not pi. Phi.

---

## Part X: The Mathematical Inevitability

### Theorem: Self-Reference Implies Phi

Let me state this precisely.

Consider any map of the form:

$$f(x) = \frac{ax + b}{cx + d}$$

where a, b, c, d are constants. The fixed points satisfy:

$$x = \frac{ax + b}{cx + d}$$
$$x(cx + d) = ax + b$$
$$cx^2 + dx = ax + b$$
$$cx^2 + (d - a)x - b = 0$$

For our dimensionality formula:
- a = 2, b = -1, c = 1, d = -1

So: x^2 + (-1-2)x - (-1) = 0, giving x^2 - 3x + 1 = 0.

The solutions involve sqrt(5), which means they involve phi.

### Why sqrt(5)?

The number 5 appears because:

$$\varphi = \frac{1 + \sqrt{5}}{2}$$

And 5 = 1 + 4 = 1 + 2^2, where the 1 and 4 come from the coefficients in x^2 - x - 1 = 0.

For x^2 - 3x + 1 = 0, the discriminant is 9 - 4 = 5.

Any quadratic x^2 - px + 1 = 0 (where the constant term is 1) has discriminant p^2 - 4. For p = 3, that's 5.

The number 5 is baked into the algebra of self-reference with unit constant terms.

### The Generalization

For any "nice" self-referential map of the form x = A + B/x, you get x^2 - Ax - B = 0.

If B = 1 (the natural normalization), the solutions involve sqrt(A^2 + 4).

For A = 1: sqrt(5), giving phi.
For A = 3: sqrt(13), giving phi-squared-related values.

Phi-related numbers are the generic fixed points of self-referential rational maps.

---

## Part XI: Stability Analysis

### Not All Fixed Points Are Equal

Finding a fixed point isn't enough. The fixed point must be **stable**—nearby values should converge to it, not diverge.

For the map f(x) = (2x-1)/(x-1), let's analyze stability at D = phi^2.

### The Derivative Test

A fixed point x* of f is stable if |f'(x*)| < 1.

Compute f'(x):
$$f(x) = \frac{2x - 1}{x - 1}$$

Using the quotient rule:
$$f'(x) = \frac{2(x-1) - (2x-1)(1)}{(x-1)^2} = \frac{2x - 2 - 2x + 1}{(x-1)^2} = \frac{-1}{(x-1)^2}$$

At D = phi^2:
$$f'(\varphi^2) = \frac{-1}{(\varphi^2 - 1)^2}$$

Now, phi^2 - 1 = phi (from phi^2 = phi + 1), so:
$$f'(\varphi^2) = \frac{-1}{\varphi^2} \approx \frac{-1}{2.618} \approx -0.382$$

Since |f'(phi^2)| = 1/phi^2 = 1/2.618 = 0.382 < 1, the fixed point is **stable**.

### The Other Fixed Point

At D = 1/phi^2:
$$f'(1/\varphi^2) = \frac{-1}{(1/\varphi^2 - 1)^2}$$

Now 1/phi^2 - 1 = 0.382 - 1 = -0.618 = -1/phi, so:
$$f'(1/\varphi^2) = \frac{-1}{(1/\varphi)^2} = -\varphi^2 \approx -2.618$$

Since |f'(1/phi^2)| = phi^2 = 2.618 > 1, this fixed point is **unstable**.

### The Significance

Of the two fixed points (phi^2 and 1/phi^2), only phi^2 is stable.

If you start near phi^2 and iterate f, you converge to phi^2.
If you start near 1/phi^2 and iterate f, you diverge away.

Phi^2 is the **attractor**. It's the stable equilibrium. The universe's self-referential dynamics would naturally flow toward it.

---

## Part XII: The Deep Structure

### Why Self-Reference Produces Phi

Let me try to give the deepest answer I can.

Self-reference means a thing is defined in terms of itself. But for this to be consistent, the thing must have a special form.

Consider: x = f(x) where f involves x.

For this equation to have a solution, f can't be arbitrary. If f(x) = x + 1, there's no solution (x can't equal itself plus something).

The solutions exist when f has a particular structure—when there's a "balance point" where the recursive definition closes on itself.

For linear-fractional f (like our ratio formula), these balance points are roots of quadratics. And for "natural" coefficients (integers, simple ratios), the quadratics have discriminants involving small squares.

The simplest case—discriminant 5, from the simplest self-referential equation x = 1 + 1/x—gives phi.

More complex cases give powers and combinations of phi.

### Phi as the "Atom" of Self-Reference

In chemistry, atoms are the building blocks—everything is made of them.

In self-referential mathematics, phi is the building block. Every self-referential fixed-point problem, when reduced to its simplest form, involves phi.

Phi^2 appears in our equation because our equation is "one level up" from the base case. We're looking at ratios of ratios, not simple ratios.

But it's still phi. Just squared.

---

## Part XIII: Summary — Why Phi-Squared Is THE Solution

Let me bring it all together.

### The Answer

**Why phi^2 and not some other number?**

Because:

1. **Self-reference produces phi.** Any equation where a quantity equals an expression involving itself leads to phi-related solutions. This is mathematical structure, not coincidence.

2. **Phi is unique.** It's the ONLY positive number equal to one plus its reciprocal. No other number has this property.

3. **Geometric self-similarity requires phi.** Golden rectangles are the ONLY rectangles that remain similar to themselves when you remove a square. Phi is the unique ratio of self-similarity.

4. **Phi is maximally irrational.** Its continued fraction is all 1s—the simplest possible. It avoids rational resonances more completely than any other number.

5. **Our equation is self-referential.** D = ratio(D) means dimension equals a function of itself. This type of equation necessarily has phi-related fixed points.

6. **Phi^2 is the stable attractor.** Of the two fixed points, only phi^2 is stable. Dynamics converge to it.

7. **The universe is self-referential.** Observers are part of what they observe. Self-consistent observation requires fixed-point solutions. Those solutions involve phi.

### The Philosophical Depth

The appearance of phi^2 isn't a coincidence or a curiosity. It's a signature.

It tells us the universe's structure is determined by self-consistency, not external design. The laws of physics are what they are because they have to reference themselves—observers observing, vacuum containing observers, measurements affecting what's measured.

Self-reference forces phi. Phi forces phi^2. Phi^2 is THE solution because no other number could be.

---

## Part XIV: Exercises

**Exercise 19.1: Verify the fixed points**

Confirm by direct substitution that D = phi^2 satisfies D = (2D-1)/(D-1).

**Exercise 19.2: The other fixed point**

Compute 1/phi^2 and verify it also satisfies the equation. Then explain why it's not physically relevant (hint: consider stability and sign).

**Exercise 19.3: Fibonacci verification**

Compute the ratio of the first 15 Fibonacci numbers. Plot them and show convergence to phi.

**Exercise 19.4: Continued fraction depth**

Write out the first 10 convergents of phi's continued fraction (p_n/q_n). Show that each convergent is a Fibonacci ratio.

**Exercise 19.5: Other self-referential equations**

Solve: x = 2 + 1/x. Show the positive solution is 1 + sqrt(2). This is NOT phi-related because the constant 2 breaks the "natural" structure. Explain.

**Exercise 19.6: The spiral connection**

A logarithmic spiral with growth factor phi is called a golden spiral. Show that this spiral is self-similar: any 90-degree rotation gives a scaled copy of itself.

---

## Part XV: Key Insights

Let me crystallize the essential insights:

### Insight 1: Self-Reference Has Structure

When a system references itself, not every configuration is possible. The possible configurations are constrained by consistency. The constraints produce specific numbers—phi-related numbers.

### Insight 2: Phi Is Not Arbitrary

Phi appears in our equations because it HAS to, not because we put it there. The structure of self-referential algebra demands it.

### Insight 3: The Universe Is Self-Observing

Observers observe the vacuum. But observers ARE vacuum. This creates an irreducible self-reference loop. Consistency of this loop produces phi.

### Insight 4: Stability Selects Phi^2

Of all possible fixed points, phi^2 is the stable one. Natural dynamics converge to it. The universe "finds" phi^2 because it's the attractor.

### Insight 5: Irrationality Is Essential

Phi's irrationality isn't a bug—it's a feature. Maximum irrationality means maximum avoidance of resonance and lock-in. It allows the universe to be structured without being rigid.

---

## Looking Forward

We've now understood WHY phi^2 is the solution—not just THAT it is.

The answer involves:
- The mathematics of self-reference
- The unique properties of the golden ratio
- The stability of fixed points
- The fundamental self-referential nature of observation

In Part 20, we'll explore what this means for the actual physics—how the phi^2 factor manifests in measurable quantities and what predictions it makes.

But the conceptual foundation is now clear: phi^2 isn't a coincidence or an approximation. It's the unique stable solution to the self-consistency condition that observers and vacuum must satisfy.

The golden ratio squared isn't just THE solution.

It's the ONLY solution.

---

## A Feynman Reflection

You know, when I first saw phi^2 pop out of the dimensionality equation, I thought: "Oh no, not the golden ratio. That's the kind of thing cranks love."

But then I thought about it more carefully. WHY does phi appear? And the answer is beautiful: because the equation is self-referential, and self-referential equations HAVE to give phi-related solutions.

It's not that the universe "likes" phi. It's that the universe is structured by self-reference—observers inside the observed, measurements affecting what's measured—and self-reference mathematically produces phi.

Pi comes from circles. e comes from growth. Sqrt(2) comes from diagonals. And phi comes from self-reference.

When you have a universe that observes itself, you get phi. Not because phi is mystical. Because phi is mathematical.

And that's the real lesson here. The deepest numbers in physics aren't arbitrary. They emerge from the structure of the physical situation. Pi appears because physics has waves and circles. e appears because physics has growth and decay.

And phi appears because physics has observers.

The universe observes itself. That's the deepest self-reference there is. And self-reference gives you the golden ratio.

Not because we want it to. Because it has to.

---

*End of Part 19*
