# Logic Primitives vs. Abstraction: Where Composition Beats Enumeration

## Context

This discussion originated from examining Kory Becker's AI-Programmer project — a system that uses genetic algorithms to evolve programs written in BrainFuck (a Turing-complete language with only 8 symbols: `> < + - . , [ ]`). The AI-Programmer project includes fitness classes for evolving logical AND, OR, and XOR programs. This raised a fundamental question: **why would you evolve something that is already a definition?**

---

## The Core Argument: Logic Gates Are Axioms, Not Solutions

The fundamental logic gates:

| Gate | Symbol | Operation | Output is 1 when... |
|------|--------|-----------|---------------------|
| **AND** | `∧` | A · B | Both inputs are 1 |
| **OR** | `∨` | A + B | At least one input is 1 |
| **NOT** | `¬` | ¬A | Input is 0 (inverts) |
| **NAND** | `⊼` | ¬(A · B) | NOT both inputs are 1 |
| **NOR** | `⊽` | ¬(A + B) | Neither input is 1 |
| **XOR** | `⊕` | A ⊕ B | Inputs differ |
| **XNOR** | `⊙` | ¬(A ⊕ B) | Inputs are the same |

Key structural facts:
- **NOT, AND, OR** are the three primitive gates — all others are compositions of these
- **NAND** alone is **universal** — any gate can be built from NAND gates only
- **NOR** is also universal on its own
- Physically, gates are transistors (MOSFETs). NOT = 2 transistors, NAND = 4, NOR = 4

**Evolving these functions is silly.** They are structurally identical to their definitions. They are discrete. There is nothing to optimize. A logic gate IS its truth table — there is no shorter representation, no better implementation, no hidden structure to discover. Evolving AND is like evolving the number 2. It's already the floor.

---

## The Real Question: Where Does Abstraction Mathematically Beat Discrete Math?

The interesting question is not "can we evolve AND?" but rather: **at what point does composing primitives into abstract structures outperform simply enumerating all discrete possibilities?**

### The Enumeration Wall

For small input spaces, a lookup table (pure discrete math) always wins:

- AND with 2 inputs = 4 rows in the truth table. Done. No abstraction needed.
- 3 inputs = 8 rows. Still trivial.
- 10 inputs = 1,024 rows. Manageable.

But combinatorial explosion kills enumeration fast:

- **n inputs → 2^n rows** in a truth table
- **2^(2^n) possible boolean functions** over n inputs
- At n = 6: 2^64 ≈ 1.8 × 10^19 possible functions
- At n = 7: 2^128 ≈ 3.4 × 10^38 possible functions
- At n = 64: more possible functions than atoms in the observable universe

This is the **enumeration wall** — the point where discrete math physically cannot represent the space.

### The Composition Advantage

Composed primitives exploit **structure** in the target function:

A 64-input parity check:
- **Lookup table**: 2^64 rows (~18 quintillion entries)
- **Composed XOR chain**: 63 XOR gates

A 64-input majority vote:
- **Lookup table**: 2^64 rows
- **Sorting network + threshold**: O(n log n) gates

The tradeoff is:

```
Discrete enumeration:   O(2^n) space,    O(1) lookup time
Composed primitives:    O(f(n)) space,   O(g(n)) compute time
```

Where f(n) and g(n) depend on the **compressibility** of the target function.

**Abstraction pays off when the target function has compressible structure** — patterns, symmetries, repetition, locality. Which most real-world functions do.

---

## The Environment Where Abstraction Wins

The key insight: **abstraction wins in any domain where the target function's Kolmogorov complexity is much smaller than its truth table.**

Kolmogorov complexity K(f) = the length of the shortest program that computes f.

- If K(f) ≈ 2^n (the truth table size), the function is incompressible. No abstraction helps. Enumeration is optimal.
- If K(f) << 2^n, the function has structure. Composition of primitives can exploit that structure.

Most functions encountered in nature, engineering, and computation are **highly compressible**:
- Physics: governed by low-dimensional differential equations
- Images: massive pixel spaces with local correlations
- Language: combinatorial token sequences with grammatical/semantic structure
- Biology: DNA encodes organisms vastly more complex than the raw bit count

The universe appears to be **structurally biased toward compressible functions**. Incompressible functions exist in far greater number (by counting arguments) but almost never arise in practice.

---

## Infinite-Dimensional Growth: Why Neural Networks Work

The intuition extends naturally to infinite-dimensional composition:

> "Infinite-dimensional growth and connections of these primitives being evolved by fitness to perform function cheaply and with high fidelity."

This is precisely what neural networks are. A neural network is:

1. **Layers of composed threshold gates** — each neuron computes a weighted sum followed by a nonlinearity (a generalized logic gate operating on continuous rather than binary values)
2. **Evolved by fitness** — the loss function IS the fitness function; gradient descent IS the evolutionary pressure
3. **Performing function cheaply** — a trained network approximates functions that would require exponentially large lookup tables
4. **With high fidelity** — universal approximation theorems guarantee that sufficiently wide/deep networks can approximate any continuous function to arbitrary precision

The architecture mirrors the argument exactly:
- **Primitives**: individual neurons (weighted sum + activation)
- **Composition**: layers of connected neurons
- **Fitness**: loss function driving weight updates
- **Payoff**: representing functions that would be intractable as discrete tables

### The Critical Difference: Continuous vs. Discrete Primitives

Logic gates operate on {0, 1}. Neurons operate on ℝ (continuous values). This is not a minor detail — it's the key to why neural networks scale:

- Boolean compositions can represent 2^(2^n) functions but require exponentially many gates for most of them
- Continuous compositions can approximate **any** function in L^2 (square-integrable functions on compact subsets of ℝ^n) with polynomially many neurons (Universal Approximation Theorem)

The move from discrete to continuous primitives is what unlocks infinite-dimensional representational power. Continuous activations allow **interpolation** — the network doesn't just memorize discrete input-output pairs, it learns the manifold structure between them.

---

## The Formal Boundary

Where exactly does abstraction beat enumeration? The boundary is determined by:

1. **Input dimensionality (n)**: Higher n → enumeration cost grows as 2^n → abstraction wins faster
2. **Function structure**: More symmetry/pattern → lower Kolmogorov complexity → bigger abstraction advantage
3. **Precision requirements**: Exact computation favors discrete methods; approximate computation favors composed continuous primitives
4. **Available primitives**: Richer primitive sets (continuous activations, attention, convolution) → more efficient compositions

### The Crossover Point

For a boolean function f: {0,1}^n → {0,1}:

- If f requires > O(2^(n/2)) gates in any circuit, enumeration may be competitive
- If f can be computed in O(poly(n)) gates, composition dominates

By circuit complexity theory, **almost all** boolean functions require exponential circuits (Shannon's counting argument). But the functions we actually care about — the ones that arise in nature and engineering — are almost always in the polynomial-circuit class.

This is the deep insight: **the universe selects for compressible structure**. Evolution, physics, information processing — all operate in the regime where abstraction pays off. The incompressible majority of function space is mathematically real but physically irrelevant.

---

## Connection to Evolved Code (BrainFuck Evolution)

Returning to the AI-Programmer project: the interesting results weren't the evolved AND/OR/XOR gates (which are trivial definitions). The interesting results were:

1. **Evolved addition/subtraction** — the system discovered loop-based accumulation patterns that generalize across inputs
2. **Evolved Fibonacci** — hierarchical function composition emerged from evolutionary pressure
3. **The infinite loop exploit** — the system discovered that exploiting interpreter timeout was a cheaper way to produce correct output than actually computing the answer
4. **Junk DNA** — non-functional code persists because it doesn't hurt fitness, paralleling biological evolution exactly

These are all examples of **abstraction emerging from fitness pressure on composed primitives**. The system didn't enumerate all possible input-output pairs — it discovered compressed representations (loops, functions, exploits) that produce correct outputs more efficiently.

The lesson: **don't evolve definitions. Evolve compositions. The payoff is in the emergent structure of connected primitives under selection pressure, not in rediscovering axioms.**

---

## Summary

| Regime | Method | Scales? |
|--------|--------|---------|
| Small n, arbitrary f | Lookup table (discrete) | Yes — trivial |
| Large n, incompressible f | Neither | Nothing works cheaply |
| Large n, structured f | Composed primitives | Yes — this is where abstraction lives |
| Infinite-dimensional, continuous f | Neural networks (evolved continuous primitives) | Yes — universal approximation |

The mathematical payoff of abstraction resides in the gap between a function's Kolmogorov complexity and its truth table size. The wider that gap, the more abstraction wins. Nature, physics, and evolution all operate in regimes where that gap is enormous — which is why brains, circuits, and neural networks all converge on the same strategy: **compose cheap primitives under fitness pressure to approximate expensive functions.**

---

## References

- Becker, K. & Gottschlich, J. (2017). "AI Programmer: Autonomously Creating Software Programs Using Genetic Algorithms." [arXiv:1709.05703](https://arxiv.org/abs/1709.05703)
- Shannon, C. (1949). "The Synthesis of Two-Terminal Switching Circuits." Bell System Technical Journal.
- Cybenko, G. (1989). "Approximation by Superpositions of a Sigmoidal Function." Mathematics of Control, Signals and Systems.
- Hornik, K. (1991). "Approximation Capabilities of Multilayer Feedforward Networks." Neural Networks.
- Li, M. & Vitányi, P. (2008). "An Introduction to Kolmogorov Complexity and Its Applications." Springer.
- Luposchainsky, D. & Boldi, P. — Circuit complexity and Shannon's counting argument
- Real, E. et al. (2020). "AutoML-Zero: Evolving Machine Learning Algorithms From Scratch." [arXiv:2003.03384](https://arxiv.org/abs/2003.03384)
