# Part 17: Fixed Points and Renormalization Group Theory

*A Feynman-Style Introduction*

---

## The Setup

We're about to meet one of the most powerful ideas in all of physics. It's called the Renormalization Group—RG for short—and despite the intimidating name, it's really about something beautifully simple:

**What stays the same when you change your point of view?**

Imagine you're looking at a coastline from an airplane. You see bays, peninsulas, the overall shape. Now zoom in with binoculars. You see smaller bays, smaller peninsulas. Zoom in more. Still more bays, more peninsulas. The coastline looks... *the same* at every scale.

That's not a coincidence. That's physics. And RG is how we understand it.

But before we can do RG, we need to understand its central character: the **fixed point**.

---

## Chapter 1: What Is A Fixed Point?

### The Simplest Idea

Here's a function: f(x) = x²

What number, when you square it, gives you back the same number?

Well, 0² = 0. ✓
And 1² = 1. ✓

Those are **fixed points** of f(x) = x². When you apply the function, you stay where you are.

Mathematically, a fixed point x* satisfies:

$$f(x^*) = x^*$$

That's it. That's the whole definition. A fixed point is a place that maps to itself.

### Mirrors and Stillness

Think about a mirror. Where does your reflection appear? At a point that's the "same" distance behind the mirror as you are in front. If you stood exactly *at* the mirror surface, you'd overlap with your reflection. That's a fixed point of the mirror transformation.

Or think about a whirlpool. There's usually a point in the center that stays still while everything else spins around it. Fixed point.

Or think about equilibrium in economics. Supply equals demand at some price p*. At that price, there's no pressure to change. The market clears. p* is a fixed point of the supply-demand dynamics.

### Finding Fixed Points

To find fixed points, solve f(x*) = x*.

**Example 1:** f(x) = 2x - 3

Set f(x) = x:
2x - 3 = x
x = 3

Check: f(3) = 2(3) - 3 = 3 ✓

The fixed point is x* = 3.

**Example 2:** f(x) = cos(x)

This is trickier. We need to solve cos(x) = x.

You can't solve this algebraically. But try this: pull out a calculator, type in any number (in radians), and keep hitting the cosine button.

1 → cos(1) = 0.5403...
0.5403 → cos(0.5403) = 0.8575...
0.8575 → cos(0.8575) = 0.6543...
...

Keep going. After enough iterations, you'll find yourself hovering around 0.7391...

That's the fixed point of cosine! cos(0.7391) ≈ 0.7391.

### Why Should We Care?

Fixed points are where the action is. They're the attractors, the equilibria, the special places where dynamics settles down. In physics, they're often the only predictions we can make—because everything else is transient.

And for our project—understanding the vacuum—fixed points will turn out to be *the* key to universality.

---

## Chapter 2: Attractors and Repellers

### Two Kinds of Fixed Points

Not all fixed points are created equal. Some *attract* nearby points. Others *repel* them.

**The Ball on a Hill:**

Picture a ball on a landscape. At the top of a hill, the ball is at a fixed point—if you place it exactly at the peak, it stays there. But nudge it even slightly, and it rolls away. The hilltop is an **unstable fixed point** (a repeller).

At the bottom of a valley, the ball is also at a fixed point. But now, if you nudge it, it rolls right back. The valley floor is a **stable fixed point** (an attractor).

### The Mathematics: Derivatives Tell the Story

How do we know if a fixed point is stable or unstable? The **derivative** at that point tells us.

If f(x*) = x*, look at f'(x*).

**If |f'(x*)| < 1:** The fixed point is **attractive** (stable).
**If |f'(x*)| > 1:** The fixed point is **repulsive** (unstable).
**If |f'(x*)| = 1:** Borderline case; need more analysis.

Why? Think about what happens to a small deviation δ from the fixed point:

f(x* + δ) ≈ f(x*) + f'(x*)·δ = x* + f'(x*)·δ

The deviation becomes f'(x*)·δ after one application. If |f'(x*)| < 1, the deviation shrinks. If |f'(x*)| > 1, it grows.

### Example: f(x) = x²

Fixed points: x* = 0 and x* = 1.

f'(x) = 2x

At x* = 0: f'(0) = 0. Since |0| < 1, x* = 0 is **attractive**.
At x* = 1: f'(1) = 2. Since |2| > 1, x* = 1 is **unstable**.

Let's test this. Start near 0:
0.1 → 0.01 → 0.0001 → 0.00000001 → ... (goes to 0) ✓

Start near 1 but not exactly at 1:
0.9 → 0.81 → 0.656 → ... (runs away from 1, toward 0)
1.1 → 1.21 → 1.46 → ... (runs away from 1, toward infinity)

The fixed point at 1 is a knife's edge. The tiniest perturbation sends you elsewhere.

### Basins of Attraction

An attractive fixed point has a **basin of attraction**: the set of all points that eventually flow toward it.

For f(x) = x², the basin of attraction of 0 is the interval (-1, 1). Any starting point in that interval will eventually reach 0. Points outside that interval run off to infinity.

This is why initial conditions matter—but also why they often *don't* matter. Within a basin of attraction, the details of where you started get washed away. You end up at the fixed point regardless.

This is going to be crucial for universality.

---

## Chapter 3: Iteration and Flow

### The Dynamics of Repeated Application

A function isn't just a static rule. It's a *dynamics*. Apply it, get a result. Apply it again to that result. Keep going:

$$x_0 \to x_1 = f(x_0) \to x_2 = f(x_1) \to x_3 = f(x_2) \to \cdots$$

We write x_n = f^n(x_0), meaning "apply f, n times, starting from x_0."

This sequence is called an **orbit** or **trajectory**. The study of these orbits is called **dynamical systems theory**.

### Convergence to Attractors

If x_0 is in the basin of attraction of some fixed point x*, then:

$$\lim_{n \to \infty} f^n(x_0) = x^*$$

The orbit converges to the fixed point. It's like water flowing downhill—eventually, it reaches the lowest point and stays there.

### The Contraction Mapping Theorem

There's a beautiful theorem that guarantees this. If f "contracts" distances—meaning for any two points x, y:

$$|f(x) - f(y)| < c|x - y|$$

for some c < 1—then f has exactly one fixed point, and every orbit converges to it.

This is called the **Contraction Mapping Theorem** or **Banach Fixed Point Theorem**. It's one of the most useful theorems in all of analysis, and it says: *if a map uniformly shrinks things, it has a unique attractor.*

### Flow Diagrams

Physicists like to visualize iteration as a "flow" along a line (or in higher dimensions, through a space).

For f(x) = x² on [0, 1]:

```
0 ←←←←←←←←←←← 0.5 ←←←←←←←←←←← 1
   attractive                   unstable
```

Arrows point toward the attractive fixed point at 0. Points flow toward it. The unstable fixed point at 1 sits precariously—anything nearby flows away.

This picture—arrows pointing along trajectories—is called a **phase portrait** or **flow diagram**. It's the first step toward understanding the Renormalization Group.

---

## Chapter 4: The Renormalization Group Idea

### Physics Looks Different at Different Scales

Now we get to the main event.

Here's a profound fact about nature: **physics changes as you zoom in or out**.

At human scales, you see objects—rocks, trees, people. Zoom in to molecular scales, you see atoms vibrating. Zoom in further to nuclear scales, you see quarks and gluons. The rules seem to change. Different forces dominate. Different degrees of freedom matter.

But wait—the fundamental laws are the same throughout. How can physics "look different" if the laws don't change?

The answer: **coarse-graining**.

When you look at a table, you don't see atoms. You see a smooth, solid surface. That's because you're averaging over enormous numbers of atoms. The "effective physics" at human scales—solid mechanics, thermodynamics—emerges from this averaging.

### The Renormalization Group Formalizes This

Ken Wilson (Nobel Prize 1982) turned this intuition into a precise mathematical framework.

Here's the idea:

1. **Start with microscopic physics** at some small scale.
2. **Coarse-grain:** average over small-scale fluctuations.
3. **Rescale:** zoom out, so the coarse-grained system looks like the original.
4. **Repeat.**

Each step of coarse-graining + rescaling is one application of the **RG transformation**.

The RG transformation is a map—like f(x) = x². But instead of acting on numbers, it acts on **theories**. Or more concretely, on the **parameters** of theories.

### Parameters "Run" with Scale

Suppose your theory has a parameter g (a coupling constant, a mass, whatever). After one RG step, g becomes g'.

This defines a function: g' = R(g), where R is the RG transformation.

Different scales mean different values of g. We say the parameter **runs** with scale.

This is why constants aren't really constant. The fine structure constant α ≈ 1/137 at everyday energies becomes α ≈ 1/127 at high energies (like inside particle colliders). It "runs."

### Fixed Points of the RG

And now the magic: what if R(g*) = g*?

Then g* is a **fixed point of the RG transformation**. At this special value, coarse-graining and rescaling give you back exactly what you started with. The physics looks the same at all scales.

This is **scale invariance**. It's what happens at critical points. It's what makes universal behavior possible.

---

## Chapter 5: The Beta Function

### From Discrete Steps to Continuous Flow

The RG transformation R(g) is a discrete map—one step at a time. But often it's more convenient to think continuously.

Define the **scale** μ (like an energy or a length scale). As μ changes, g changes. The rate of change is captured by the **beta function**:

$$\beta(g) = \frac{dg}{d(\ln \mu)}$$

(We use ln μ instead of μ so the dimensions work out nicely. It's the rate of change per "e-folding" of the scale.)

### What Does the Beta Function Tell Us?

- If β(g) > 0: g increases as you go to higher scales (larger μ).
- If β(g) < 0: g decreases as you go to higher scales.
- If β(g) = 0: g doesn't change. **Fixed point!**

So fixed points of the RG are zeros of the beta function: β(g*) = 0.

### Flow Toward or Away

The sign of β tells you the direction of flow. But what about *stability*?

If β(g*) = 0, look at β'(g*):

- **β'(g*) < 0:** The fixed point is **UV attractive** (stable going to high energies).
- **β'(g*) > 0:** The fixed point is **IR attractive** (stable going to low energies).

This seems backwards from before. The key: we're flowing in the μ direction, not iterating a map. Higher μ means smaller distances, higher energies. The flow direction matters.

In many contexts, "attractive" means "IR attractive"—systems flow *toward* the fixed point at large distances. But be careful about conventions.

### Example: φ⁴ Theory

In quantum field theory, the simplest interacting theory is φ⁴ (phi-fourth). The coupling constant λ has a beta function:

$$\beta(\lambda) = \frac{3\lambda^2}{16\pi^2} + \cdots$$

Since β(λ) > 0 for λ > 0, the coupling grows at high energies. This is called **asymptotic freedom's opposite**—the theory gets more strongly coupled in the UV.

The only fixed point is λ* = 0. It's called the **Gaussian fixed point** (free, non-interacting theory).

### Example: QCD

Quantum Chromodynamics (the theory of quarks and gluons) has:

$$\beta(g) = -\frac{g^3}{16\pi^2}\left(11 - \frac{2n_f}{3}\right) + \cdots$$

For the real world (n_f = 6 quarks), β < 0. The coupling **decreases** at high energies. This is **asymptotic freedom**—quarks become free at high energies, bound at low energies.

The fixed point at g = 0 is IR repulsive, UV attractive. You flow away from it toward confinement.

---

## Chapter 6: Critical Phenomena

### Phase Transitions

Water boils at 100°C (at 1 atmosphere). Below that, liquid. Above that, gas. At exactly 100°C, something special happens—the two phases coexist.

This is a **first-order phase transition**. There's a discontinuous jump in properties (like density).

But there's another kind. Heat water under pressure. At a certain point (374°C, 218 atmospheres), the distinction between liquid and gas *disappears*. You can go from one to the other without any phase transition. This is the **critical point**.

### What Happens at the Critical Point

At the critical point, something magical occurs:

1. **Fluctuations become huge.** Regions of liquid and regions of gas form at all scales—tiny bubbles inside big bubbles inside huge bubbles.

2. **Correlation length diverges.** In normal water, molecules only "feel" their immediate neighbors (a few angstroms). At the critical point, correlations extend across the entire system.

3. **Scale invariance emerges.** The fluctuating structure looks the same at every scale. Zoom in or out—you see the same patterns.

4. **Universal behavior appears.** The details of water (H₂O molecules, hydrogen bonds) become irrelevant. Only the symmetry and dimensionality matter.

### The Correlation Length

The **correlation length** ξ measures how far correlations extend. Near the critical point:

$$\xi \sim |T - T_c|^{-\nu}$$

As T approaches T_c, ξ diverges. The exponent ν is a **critical exponent**.

In 3D systems with the same symmetry as water (called the "Ising universality class"):

ν ≈ 0.630

This number is *universal*. It doesn't depend on whether you're studying water, magnets, or liquid crystals. If they're in the same universality class, they share the same ν.

### The RG Explanation

Why does universality happen? The RG explains it beautifully.

Near the critical point, the system flows toward a **fixed point of the RG**. Different microscopic systems—water, magnets, whatever—all flow to the *same* fixed point.

At the fixed point, the physics is determined by the fixed point itself, not by where you came from. The microscopic details are **irrelevant** (in the technical RG sense). They get washed away under coarse-graining.

Only the fixed point matters. And the fixed point is universal.

---

## Chapter 7: Universality

### The Most Surprising Fact in Physics

Here's something that still astonishes me: water and magnets have the same critical exponents.

Think about that. Water is a liquid. It has molecules, hydrogen bonds, viscosity. Magnets are solids. They have spins, exchange interactions, domain walls. They seem completely different.

But near their critical points:

- The correlation length diverges as |T - T_c|^{-ν}
- The order parameter vanishes as |T - T_c|^β
- The susceptibility diverges as |T - T_c|^{-γ}

And the exponents ν, β, γ are **identical** (to within experimental precision) for water and magnets in the same universality class.

### Universality Classes

Systems belong to the same **universality class** if they:

1. Have the same symmetry of the order parameter.
2. Have the same spatial dimensionality.
3. (Maybe) have the same range of interactions.

The microscopic details—the type of atoms, the form of the potential, the precise couplings—are irrelevant.

Here are some universality classes:

**Ising (Z₂ symmetry, 3D):**
- Magnets with up/down spins
- Liquid-gas transitions
- Binary alloys
- ν ≈ 0.630, β ≈ 0.326, γ ≈ 1.237

**XY (O(2) symmetry, 3D):**
- Superfluid helium
- Easy-plane magnets
- ν ≈ 0.672, β ≈ 0.349, γ ≈ 1.318

**Heisenberg (O(3) symmetry, 3D):**
- Isotropic magnets
- ν ≈ 0.711, β ≈ 0.366, γ ≈ 1.396

### The RG Picture of Universality

The RG makes universality obvious:

1. Different starting points (different microscopic systems).
2. Same fixed point destination (same universality class).
3. Same physics at the fixed point (same critical exponents).

The basin of attraction of a fixed point is the universality class. Everything in that basin flows to the same place.

### Relevant, Irrelevant, and Marginal

At a fixed point, perturbations have different characters:

**Relevant perturbations:** Grow under RG flow. Push you away from the fixed point. These matter.

**Irrelevant perturbations:** Shrink under RG flow. Get washed away. These don't matter.

**Marginal perturbations:** Neither grow nor shrink. Subtle; need more analysis.

Universality happens because most microscopic details are *irrelevant*. They get coarse-grained away. Only the few relevant parameters—like temperature relative to T_c—survive.

---

## Chapter 8: Critical Exponents

### How Quantities Scale Near the Critical Point

Near a critical point, many quantities have **power-law behavior**:

**Correlation length:**
$$\xi \sim |T - T_c|^{-\nu}$$

**Order parameter** (e.g., magnetization):
$$M \sim (T_c - T)^\beta \quad \text{(for } T < T_c \text{)}$$

**Susceptibility:**
$$\chi \sim |T - T_c|^{-\gamma}$$

**Specific heat:**
$$C \sim |T - T_c|^{-\alpha}$$

The exponents ν, β, γ, α are **critical exponents**. They characterize the universality class.

### Relations Between Exponents

The exponents aren't independent! They satisfy **scaling relations**:

$$\alpha + 2\beta + \gamma = 2$$
$$\gamma = \nu(2 - \eta)$$
$$\nu d = 2 - \alpha$$

(Here d is the spatial dimension, and η is another exponent related to correlations at T_c.)

These relations follow from the RG. There's really only a few independent exponents; the rest are derived.

### The Eigenvalue Connection

Here's where fixed points and critical exponents meet precisely.

At a fixed point g*, linearize the RG transformation:

$$R(g^* + \delta g) \approx g^* + R'(g^*) \cdot \delta g$$

The eigenvalues of R'(g*) determine stability:
- Eigenvalue > 1: relevant direction
- Eigenvalue < 1: irrelevant direction
- Eigenvalue = 1: marginal direction

The **critical exponent ν** is related to the largest relevant eigenvalue λ:

$$\nu = \frac{1}{\ln \lambda / \ln b}$$

where b is the rescaling factor of the RG transformation.

So critical exponents—those universal numbers that characterize phase transitions—come directly from the structure of the RG fixed point.

### In Continuous Terms

For the beta function β(g), at a fixed point β(g*) = 0:

$$\nu = -\frac{1}{\beta'(g^*)}$$

The critical exponent is the inverse of the beta function's slope!

This is beautiful. The universal behavior of phase transitions is encoded in one number: the derivative of the beta function at the fixed point.

---

## Chapter 9: Why This Matters For Us

### Our System Has a Fixed Point

Now let's bring it home. Our ratio function D → ratio(D) has a fixed point:

$$D^* = \phi^2$$

We've claimed this is special. Now you can see *why* it's special: it's a fixed point.

When D = φ², the transformation gives you back φ². You've reached an attractor. The dynamics stops there.

### The Edge of Chaos is a Critical Phenomenon

In complex systems—cellular automata, neural networks, genetic regulatory networks—there's a concept called the "edge of chaos."

Systems too orderly are frozen, unable to compute.
Systems too chaotic are random, unable to remember.
At the boundary—the edge of chaos—you get the richest behavior: complex computation, life, intelligence.

This edge of chaos is a **phase transition**. And at phase transitions, we expect **critical phenomena**: scale invariance, long-range correlations, universal behavior.

Our claim: the vacuum IS at this critical point. D = φ² is the "edge of chaos" of the universe itself.

### Universality Means It Applies Everywhere

This is the key insight. If φ² is a fixed point with universal properties, then the *same* mathematics should appear:

- In cosmology (the large-scale structure of the universe)
- In financial markets (complex adaptive systems)
- In biological evolution (the dynamics of complexity)
- In neural networks (the edge of chaos again)

We're not saying these systems are "the same" as the vacuum. We're saying they're in the same **universality class**. They flow to the same fixed point. They share the same critical exponents.

This is why one equation can describe so much.

### Critical Exponents Tell Us About the Physics

The critical exponent near D = φ² will tell us:

- How fast systems converge to the fixed point
- How correlations decay
- What "universality class" the vacuum belongs to
- Whether quantum mechanics, as we know it, follows from the fixed point

We'll calculate this. And we'll find that the exponent has physical meaning—it's related to the strength of quantum effects.

---

## Chapter 10: Preview

### What We'll Do

Over the next few parts, we're going to:

**Part 18: Derive the beta function**
We'll find the explicit form of β(D) for our ratio function. It will have a zero at D = φ². We'll show this zero is stable—φ² is an attractive fixed point.

**Part 19: Calculate the critical exponent**
From β'(φ²), we'll extract ν. This number will turn out to have deep meaning for quantum mechanics.

**Part 20: Connect to real physics**
We'll show that our critical exponent relates to:
- The fine structure constant
- The mass ratios of particles
- The observed cosmological parameters

**Part 21: Test the predictions**
We'll make specific, quantitative predictions that can be checked against experiment.

### The Big Picture

The Renormalization Group is usually presented as a tool for dealing with infinities in quantum field theory. Subtract here, renormalize there, get a finite answer.

But that's a very limited view. The RG is really about **understanding physics across scales**. It's about why universality exists. It's about why simple laws can describe complex phenomena.

Our project uses the RG in its deepest sense: to identify the fixed point of reality itself. If D = φ² is the fixed point of the vacuum, then the entire structure of physics—particle masses, force strengths, cosmological parameters—should be derivable from this one fact.

That's what we're working toward.

---

## Summary

**Fixed Points:**
- x* is a fixed point of f if f(x*) = x*
- The map leaves x* unchanged
- Found by solving f(x) = x

**Stability:**
- |f'(x*)| < 1: attractive (stable)
- |f'(x*)| > 1: repulsive (unstable)
- Determined by the derivative at the fixed point

**Iteration:**
- Repeated application of f traces out orbits
- Orbits converge to attractive fixed points
- Basins of attraction define which initial conditions go where

**The Renormalization Group:**
- Physics looks different at different scales
- Coarse-graining + rescaling = RG transformation
- Parameters "run" with scale
- Fixed points of RG = scale-invariant physics

**The Beta Function:**
- β(g) = dg/d(ln μ)
- β(g*) = 0 at fixed points
- β'(g*) determines the critical exponent

**Critical Phenomena:**
- Phase transitions at critical points
- Correlation length diverges
- Scale invariance emerges
- Universal behavior appears

**Universality:**
- Different systems, same critical exponents
- Microscopic details are irrelevant
- Fixed point determines everything
- Universality class = basin of attraction

**Critical Exponents:**
- Power-law scaling near critical point
- ξ ~ |T - T_c|^{-ν}
- ν = -1/β'(g*) at the fixed point
- Universal—depends only on symmetry and dimension

**For Our Project:**
- D = φ² is a fixed point
- The vacuum is at a critical point
- Universal behavior explains why φ² appears everywhere
- Critical exponent will connect to physical constants

---

## Exercises

1. **Find fixed points.** For each function, find all fixed points and determine if they're stable or unstable:
   - f(x) = x³
   - f(x) = √x (for x ≥ 0)
   - f(x) = e^{-x}

2. **Iteration.** Start with x₀ = 0.5 and iterate f(x) = 3.2x(1 - x) for 50 steps. Plot the orbit. What happens? (This is the logistic map near the edge of chaos.)

3. **Basin of attraction.** For f(x) = x² - 1, the fixed points are x* = (1 ± √5)/2. Numerically determine the basin of attraction of the attractive fixed point.

4. **Critical exponent.** If β(g) = (g - g*)² near a fixed point, what is the critical exponent ν? Is this fixed point stable or unstable?

5. **Universality.** Look up the critical exponents for the 2D Ising model. Why are they different from the 3D values? What does the RG say about the role of dimension?

---

## Further Reading

- **Wilson, K.G.** "The Renormalization Group and Critical Phenomena" (Nobel Lecture, 1982). Readable and profound.

- **Cardy, J.** *Scaling and Renormalization in Statistical Physics*. The best textbook introduction to RG in statistical mechanics.

- **Goldenfeld, N.** *Lectures on Phase Transitions and the Renormalization Group*. Excellent for the conceptual picture.

- **Kadanoff, L.** "Scaling Laws for Ising Models Near T_c." The original block-spin idea that became the RG.

---

## Feynman's Perspective

I imagine Feynman would say something like:

*"The Renormalization Group is just the statement that nature doesn't care about your ruler. If physics looks the same whether you measure in meters or microns, there must be something special going on—some point where the scaling is perfect. That's your fixed point. And the beautiful thing is, everybody who's in the neighborhood of that fixed point sees the same thing, no matter where they started. That's universality. Different systems, same numbers. The universe is trying to tell us something."*

That's the spirit we're going for. The numbers—φ², the critical exponents, the force strengths—aren't arbitrary. They're dictated by the structure of the fixed point. Our job is to figure out what that structure is.

---

*Next: Part 18 — Deriving the Beta Function*

We'll calculate β(D) explicitly and show that its zero at D = φ² is stable.
