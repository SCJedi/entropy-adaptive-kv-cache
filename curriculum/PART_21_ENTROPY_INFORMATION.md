# Part 21: Entropy and Information Theory — The Mathematics of Uncertainty

*"Information is the resolution of uncertainty."* — Claude Shannon

---

## The Strange Question That Started Everything

Here's a puzzle that kept Claude Shannon up at night in the 1940s: How do you measure information?

Not *meaning* — that's philosophy. Shannon wanted something you could calculate. He worked at Bell Labs, where the practical question was: How much can you squeeze through a telephone wire? How do you know when you're using the channel efficiently?

His answer revolutionized not just communications, but physics, biology, neuroscience, and — as we'll see — our understanding of natural selection itself.

The key insight was this: **information is about surprise**.

---

## What Is Information?

### The Reduction of Uncertainty

Imagine I'm going to flip a fair coin and tell you the result. Before I tell you, you're uncertain — it could be heads or tails, 50/50. After I tell you, you know. That transition from uncertainty to certainty *is* information.

Now imagine I'm going to tell you whether the sun rose this morning. Before I tell you, you're... not really uncertain, are you? You already know the sun rose. When I confirm it, you learn nothing. No surprise, no information.

This is Shannon's insight: **Information is the answer to a question you didn't already know.**

The more uncertain you were beforehand, the more information you gain from the answer. The less uncertain, the less information.

### Measuring Surprise

Let's make this quantitative. Suppose an event has probability p of occurring. How surprised should you be when it happens?

Shannon proposed that surprise should be:

```
Surprise = log₂(1/p) = -log₂(p)
```

Why logarithm? Three beautiful reasons:

**1. Rare events are more surprising than common ones.**
If p = 1/2, surprise = log₂(2) = 1
If p = 1/4, surprise = log₂(4) = 2
If p = 1/8, surprise = log₂(8) = 3

Makes sense — a 1-in-8 event is more surprising than a 1-in-2 event.

**2. Surprises add up.**
If two independent things happen, each with probability p₁ and p₂, the combined probability is p₁ × p₂. The combined surprise is:

```
-log₂(p₁ × p₂) = -log₂(p₁) - log₂(p₂)
```

The surprises add! This is exactly what we'd want. Rolling two sixes in a row should be twice as surprising as rolling one six (if dice were fair, anyway).

**3. Certain events have zero surprise.**
If p = 1, surprise = log₂(1) = 0

Learning something you already knew for certain tells you nothing.

### The Bit

We use base-2 logarithms, so surprise is measured in **bits**. One bit is the information gained from a fair coin flip — the answer to one yes/no question where you genuinely didn't know the answer.

Why base 2? You can use any base — base e gives "nats," base 10 gives "bans" — but bits are most intuitive. Every bit answers one binary question.

---

## Entropy: Average Surprise

Now here's the key definition. If you're going to observe a random variable X that can take various values, each with some probability, how much information do you *expect* to gain?

The answer is **entropy**, denoted H(X):

```
H(X) = -Σᵢ pᵢ log₂(pᵢ)
```

This is just the average surprise, weighted by probability. Each outcome i has probability pᵢ and surprise -log₂(pᵢ). We average over all outcomes.

Entropy measures **how uncertain you are before observing X**. High entropy means high uncertainty means lots of expected information when you finally observe.

### The Fair Coin

Let's calculate. A fair coin has two outcomes, each with p = 1/2:

```
H(coin) = -[p(heads)·log₂(p(heads)) + p(tails)·log₂(p(tails))]
        = -[0.5·log₂(0.5) + 0.5·log₂(0.5)]
        = -[0.5·(-1) + 0.5·(-1)]
        = -[-0.5 - 0.5]
        = 1 bit
```

One bit! A fair coin flip gives you exactly one bit of information. This is why Shannon chose base 2 — it makes the math clean for binary questions.

### The Loaded Coin

Now suppose the coin is loaded: 90% heads, 10% tails.

```
H(loaded) = -[0.9·log₂(0.9) + 0.1·log₂(0.1)]
          = -[0.9·(-0.152) + 0.1·(-3.322)]
          = -[-0.137 - 0.332]
          = 0.469 bits
```

Less than half a bit! You already kind of know it's going to be heads, so learning the outcome gives you less information.

### The Certain Outcome

What if the coin always lands heads? p(heads) = 1, p(tails) = 0.

Here we need a convention: 0·log(0) = 0 (this is the limit as p→0).

```
H(certain) = -[1·log₂(1) + 0·log₂(0)]
           = -[1·0 + 0]
           = 0 bits
```

Zero entropy. No uncertainty. No information gained by observing. You already knew.

### Maximum Entropy

When is entropy maximized? When all outcomes are equally likely!

For n equally likely outcomes, each has probability 1/n:

```
H(max) = -Σᵢ (1/n)·log₂(1/n)
       = -n·(1/n)·log₂(1/n)
       = -log₂(1/n)
       = log₂(n)
```

For 2 outcomes: H(max) = log₂(2) = 1 bit (fair coin)
For 8 outcomes: H(max) = log₂(8) = 3 bits (fair 8-sided die)
For 256 outcomes: H(max) = log₂(256) = 8 bits (random byte)

Maximum entropy = maximum uncertainty = maximum information when you finally observe.

---

## Visualizing Entropy

For a binary variable (two outcomes with probabilities p and 1-p), entropy looks like this:

```
    H(X)
     1 |        ___
       |      _/   \_
       |    _/       \_
       |  _/           \_
       | /               \
     0 |/_________________\_
       0   0.25  0.5  0.75  1
                 p
```

Maximum at p = 0.5 (fair coin), zero at p = 0 or p = 1 (certain outcomes).

This shape matters! It tells us that nature achieves maximum "interestingness" when outcomes are balanced, not when one dominates.

---

## Conditional Entropy

Now things get interesting. Suppose you know something about Y. How much uncertainty remains about X?

**Conditional entropy H(X|Y)** measures the uncertainty in X given that you know Y:

```
H(X|Y) = -Σₓ,ᵧ p(x,y)·log₂(p(x|y))
```

Or equivalently, the average entropy of X across all possible values of Y:

```
H(X|Y) = Σᵧ p(y)·H(X|Y=y)
```

### Key Properties

**1. Knowing something can only reduce uncertainty (or leave it unchanged):**
```
H(X|Y) ≤ H(X)
```

Learning Y can't make you *more* confused about X.

**2. If Y tells you nothing about X (they're independent):**
```
H(X|Y) = H(X)
```

The uncertainty in X is the same whether or not you know Y.

**3. If Y tells you everything about X:**
```
H(X|Y) = 0
```

No remaining uncertainty.

**4. If you already know X:**
```
H(X|X) = 0
```

Obviously! If you know X, there's no uncertainty about X.

### Example: The Loaded Die

Suppose I have two dice — a fair one and one loaded to always show 6. I pick one at random (50/50) and roll it. Let Y = which die I picked, X = the outcome.

Without knowing Y:
- If fair die (50%): outcomes 1-6 equally likely
- If loaded die (50%): outcome is always 6
- P(X=6) = 0.5·(1/6) + 0.5·1 = 0.583
- P(X=1) = P(X=2) = ... = P(X=5) = 0.5·(1/6) = 0.083 each

Calculate H(X): messy, but around 2.12 bits.

Knowing Y:
- If Y = fair: H(X|Y=fair) = log₂(6) ≈ 2.58 bits
- If Y = loaded: H(X|Y=loaded) = 0 bits

```
H(X|Y) = 0.5·2.58 + 0.5·0 = 1.29 bits
```

Knowing which die I picked reduces your uncertainty from 2.12 bits to 1.29 bits. Makes sense — if you know it's the loaded die, you know exactly what will happen!

---

## Mutual Information: The Information Shared

Here's the beautiful part. The *reduction* in uncertainty about X when you learn Y is called **mutual information**:

```
I(X;Y) = H(X) - H(X|Y)
```

This measures **how much X and Y tell you about each other**.

### Properties That Feel Right

**1. Symmetry:**
```
I(X;Y) = I(Y;X)
```

What X tells you about Y equals what Y tells you about X. This isn't obvious from the definition, but it's true. (Proof: both equal H(X) + H(Y) - H(X,Y))

**2. Non-negativity:**
```
I(X;Y) ≥ 0
```

You can't learn negative information. Knowing Y can't make you *less* informed about X.

**3. Independence means zero mutual information:**
```
If X and Y are independent, I(X;Y) = 0
```

Independent variables tell you nothing about each other.

**4. Perfect correlation means maximum mutual information:**
```
If Y determines X, I(X;Y) = H(X)
```

Y tells you everything about X.

### The Venn Diagram Picture

You can visualize this:

```
    ┌───────────────────┐
    │                   │
    │   H(X|Y)          │
    │           ┌───────┼───────┐
    │           │ I(X;Y)│       │
    │           │       │       │
    └───────────┼───────┘       │
                │    H(Y|X)     │
                │               │
                └───────────────┘

    H(X) = H(X|Y) + I(X;Y)
    H(Y) = H(Y|X) + I(X;Y)
```

The overlap is the shared information. The non-overlapping parts are what each variable knows that the other doesn't.

### Why Mutual Information Matters

This is the fundamental quantity for asking: **Does this signal tell me about that phenomenon?**

- Do symptoms tell me about disease? Measure I(symptoms; disease)
- Does this gene expression tell me about this trait? Measure I(expression; trait)
- Does environmental state tell me about optimal behavior? Measure I(environment; fitness)

That last one is going to be crucial.

---

## The Leap to Physics: Thermodynamic Entropy

Now here's something that puzzled physicists for a century: the entropy formula in thermodynamics looks *exactly* like Shannon's information entropy. Coincidence?

### Boltzmann's Entropy

In 1877, Ludwig Boltzmann defined entropy for a physical system:

```
S = k_B · ln(Ω)
```

Where:
- S is thermodynamic entropy
- k_B is Boltzmann's constant (1.38 × 10⁻²³ J/K)
- Ω is the number of microstates consistent with the macrostate

A microstate is a complete specification of every particle's position and momentum. A macrostate is what we can actually measure — temperature, pressure, volume.

If Ω = 1 (only one way to achieve this macrostate), S = 0.
If Ω is huge (many ways), S is large.

### The Connection

Here's the beautiful link. Suppose we don't know which microstate the system is in, but we know it's equally likely to be in any of the Ω microstates. What's our uncertainty?

```
H = log₂(Ω) bits
```

Convert to natural log and add the constant:

```
S = k_B · ln(Ω) = k_B · ln(2) · log₂(Ω) = k_B · ln(2) · H
```

Boltzmann's entropy is just Shannon's entropy (in the right units) when all microstates are equally likely!

But the connection is deeper. When microstates *aren't* equally likely...

### General Form

If microstate i has probability pᵢ, the thermodynamic entropy is:

```
S = -k_B Σᵢ pᵢ · ln(pᵢ)
```

This is Shannon's entropy (up to units). The same formula!

### Why The Same Formula?

This isn't a coincidence. It's a profound fact about nature:

**Thermodynamic entropy measures our ignorance about the microstate.**

A high-entropy state is one where many microstates could produce what we observe. We're uncertain which one we're in. A low-entropy state is one where few microstates are possible — we're more certain.

The Second Law of Thermodynamics ("entropy always increases") becomes: **our ignorance tends to increase unless we actively gather information.**

Or equivalently: **systems tend toward states consistent with the most microstates** because that's where "most of the volume" is in configuration space.

---

## The Boltzmann Distribution

When a system is in thermal equilibrium at temperature T, which microstates are more probable?

Boltzmann's answer:

```
P(state i) = (1/Z) · exp(-Eᵢ / k_B T)
```

Where:
- Eᵢ is the energy of state i
- T is temperature
- k_B is Boltzmann's constant
- Z is a normalization constant (the "partition function")

### Unpacking This

**Low energy states are more probable than high energy states.** The exponential strongly favors lower energies.

**Temperature controls the spread.** When T is low, almost all probability concentrates in the lowest energy states. When T is high, higher energy states become accessible.

```
Low T:   P ∝ exp(-E/small) = exp(-large) → very peaked at low E
High T:  P ∝ exp(-E/large) = exp(-small) → more spread out
```

### Why This Distribution?

Here's the remarkable fact: **the Boltzmann distribution maximizes entropy subject to a fixed average energy.**

If you only know the average energy of a system, and you want to be maximally uncertain about which microstate it's in (maximum entropy), you get the Boltzmann distribution.

This is the **maximum entropy principle**: nature seems to choose the distribution that's maximally uncertain given the constraints.

### Let's Prove It (Sketch)

We want to maximize:

```
S = -k_B Σᵢ pᵢ ln(pᵢ)
```

Subject to:
- Σᵢ pᵢ = 1 (probabilities sum to 1)
- Σᵢ pᵢ Eᵢ = ⟨E⟩ (average energy is fixed)

Use Lagrange multipliers. Set up:

```
L = -Σᵢ pᵢ ln(pᵢ) - α(Σᵢ pᵢ - 1) - β(Σᵢ pᵢ Eᵢ - ⟨E⟩)
```

Take ∂L/∂pᵢ = 0:

```
-ln(pᵢ) - 1 - α - βEᵢ = 0
ln(pᵢ) = -1 - α - βEᵢ
pᵢ = exp(-1 - α) · exp(-βEᵢ)
```

The first factor is just normalization (1/Z). We get:

```
pᵢ = (1/Z) exp(-βEᵢ)
```

Where β = 1/(k_B T). The Boltzmann distribution!

### Connection to Selection

Here's why this matters for us. In evolution:

- "Energy" becomes "fitness cost" (negative fitness)
- "Temperature" becomes "selection pressure"
- The Boltzmann-like distribution describes how organisms spread across fitness levels

Strong selection (high β, low T) concentrates the population at high fitness.
Weak selection (low β, high T) allows more fitness diversity.

This isn't just an analogy — it's mathematically identical.

---

## Fisher Information: Precision of Estimates

Now we need a different kind of information. Shannon information asks: "How much do I learn by observing?" Fisher information asks: **"How precisely can I estimate a parameter from observations?"**

### The Setup

Suppose you're trying to estimate some parameter θ from data. You observe X, which depends on θ. How much information does X carry about θ?

The **Fisher information** is:

```
I(θ) = E[(∂/∂θ ln p(X|θ))²]
```

Or equivalently:

```
I(θ) = -E[∂²/∂θ² ln p(X|θ)]
```

This is the expected curvature of the log-likelihood.

### Intuition

When the likelihood function is sharply peaked around the true θ, you can estimate θ precisely. Fisher information is high.

When the likelihood is flat, many values of θ are consistent with your observations. Fisher information is low.

```
High Fisher info:          Low Fisher info:
     _                          ___
    /|\                       _/   \_
   / | \                    _/       \_
  /  |  \                  /           \
 /   |   \               _/             \_
     θ                            θ
(sharp peak)              (flat, uncertain)
```

### The Cramér-Rao Bound

Here's the powerful result. If you're trying to estimate θ from observations, the variance of any unbiased estimator is bounded:

```
Var(θ̂) ≥ 1 / I(θ)
```

**You can't estimate θ more precisely than Fisher information allows.**

More Fisher information → smaller possible variance → more precise estimates.

This is fundamental! It tells you the theoretical limit on how well you can know something from data.

### Example: Coin Flips

You flip a coin n times, trying to estimate the probability p of heads. You observe k heads.

The likelihood is:

```
P(k|p) = C(n,k) · p^k · (1-p)^(n-k)
```

Take log:

```
ln P = const + k ln(p) + (n-k) ln(1-p)
```

Differentiate twice with respect to p:

```
d²/dp² ln P = -k/p² - (n-k)/(1-p)²
```

Take expectation (E[k] = np):

```
I(p) = -E[d²/dp² ln P] = np/p² + n(1-p)/(1-p)² = n/p + n/(1-p) = n/[p(1-p)]
```

So Fisher information is:

```
I(p) = n / [p(1-p)]
```

Observations:
- More flips (larger n) → more information
- p near 0.5 → denominator large → less information per flip
- p near 0 or 1 → denominator small → more information per flip

The last point is counterintuitive, but it makes sense: if the coin almost always lands heads, each observation strongly constrains p. If it's fair, outcomes are more variable.

The Cramér-Rao bound says:

```
Var(p̂) ≥ p(1-p)/n
```

For the maximum likelihood estimator (p̂ = k/n), this bound is achieved. We can't do better.

---

## The Information Geometry of Selection

Now we connect everything to selection. This is where information theory meets evolution.

### Selection as Information Transfer

Think about what natural selection does:

1. Environment poses a challenge (what behaviors survive?)
2. Organisms have varying traits
3. Some traits survive better than others
4. The population shifts toward better traits

This is an **information channel**. The environment "sends a signal" about what works, and the population "receives" that signal by changing its composition.

The mutual information I(trait; survival) measures how much the trait tells you about survival — equivalently, how much survival tells you about which traits work.

### Fitness as Information

Here's a key insight: **fitness is the logarithm of survival probability** (in a certain formulation). That means:

```
Fitness ∝ log(survival probability)
```

This isn't arbitrary. It makes fitness additive across generations (geometric growth → arithmetic in logs), and it connects directly to Shannon's measure of information.

When an organism survives, it's giving you information about which traits work. High survival probability → low surprise → low information. Low survival probability → high surprise → high information if it survives.

Selection is the accumulation of information about what works.

### Edge of Chaos Revisited

Remember the edge of chaos from earlier parts? Systems at the boundary between order and chaos have special properties:

- Maximum sensitivity to perturbations
- Maximum computational capability
- Maximum... entropy? Information?

Yes! At the edge of chaos:
- Entropy is intermediate (not minimal like in frozen order, not maximal like in chaos)
- But **information transmission** is maximized

This is because:
- Pure order: signals don't propagate (system is frozen)
- Pure chaos: signals are scrambled (system is random)
- Edge: signals propagate and transform without being destroyed

Selection pushes systems toward the edge because that's where information about the environment can be processed most effectively.

### Fisher Information and Fitness

Fisher information shows up in fitness too. If you're trying to estimate an organism's fitness from observations:

- High Fisher information: fitness is precisely measurable
- Low Fisher information: fitness is uncertain

Why does this matter? Because **selection can only act on fitness to the extent that fitness is measurable**.

If two organisms have almost identical survival probabilities, selection can't distinguish them reliably. Genetic drift dominates. But if their fitnesses are clearly different, selection acts efficiently.

Fisher information quantifies the boundary between these regimes.

---

## Worked Example: Information in a Fitness Landscape

Let's make this concrete. Suppose a trait X determines survival probability:

```
P(survive|X=0) = 0.1
P(survive|X=1) = 0.4
P(survive|X=2) = 0.7
P(survive|X=3) = 0.9
```

And initially the population is uniformly distributed: P(X=i) = 0.25 for each.

**Question 1: What's the initial entropy of X?**

```
H(X) = -4 × (0.25 × log₂(0.25)) = -4 × (0.25 × -2) = 2 bits
```

Maximum entropy — we're completely uncertain about X.

**Question 2: What's the mutual information I(X; survive)?**

First, find P(survive):

```
P(survive) = Σᵢ P(X=i)·P(survive|X=i)
           = 0.25(0.1 + 0.4 + 0.7 + 0.9)
           = 0.25 × 2.1 = 0.525
```

H(survive) = -[0.525·log₂(0.525) + 0.475·log₂(0.475)]
           = -[0.525×(-0.930) + 0.475×(-1.074)]
           = 0.999 bits (essentially 1 bit)

Now H(survive|X):

```
H(survive|X=0) = -[0.1·log₂(0.1) + 0.9·log₂(0.9)] = 0.469 bits
H(survive|X=1) = -[0.4·log₂(0.4) + 0.6·log₂(0.6)] = 0.971 bits
H(survive|X=2) = -[0.7·log₂(0.7) + 0.3·log₂(0.3)] = 0.881 bits
H(survive|X=3) = -[0.9·log₂(0.9) + 0.1·log₂(0.1)] = 0.469 bits

H(survive|X) = 0.25(0.469 + 0.971 + 0.881 + 0.469) = 0.698 bits
```

Mutual information:

```
I(X; survive) = H(survive) - H(survive|X) = 0.999 - 0.698 = 0.301 bits
```

**Interpretation:** Knowing the trait value gives you about 0.3 bits of information about survival. That's how much selection "sees."

**Question 3: After selection, what's the new distribution?**

Among survivors:

```
P(X=i|survive) = P(survive|X=i)·P(X=i) / P(survive)
```

```
P(X=0|survive) = 0.1 × 0.25 / 0.525 = 0.048
P(X=1|survive) = 0.4 × 0.25 / 0.525 = 0.190
P(X=2|survive) = 0.7 × 0.25 / 0.525 = 0.333
P(X=3|survive) = 0.9 × 0.25 / 0.525 = 0.429
```

New entropy:

```
H(X|survive) = -[0.048·log₂(0.048) + 0.190·log₂(0.190) +
                 0.333·log₂(0.333) + 0.429·log₂(0.429)]
             = -[0.048×(-4.38) + 0.190×(-2.40) + 0.333×(-1.59) + 0.429×(-1.22)]
             = 1.71 bits
```

Selection reduced entropy from 2.0 bits to 1.71 bits. The population became more concentrated at high fitness values. Information was gained about what works.

---

## The Mathematical Bridge

Let's connect the two entropies explicitly.

### Shannon Entropy (Information)

```
H = -Σᵢ pᵢ log pᵢ
```

Measures: uncertainty, disorder, information content
Units: bits (log₂) or nats (ln)
Context: communication, statistics, inference

### Boltzmann Entropy (Thermodynamics)

```
S = -k_B Σᵢ pᵢ ln pᵢ = k_B · ln(2) · H
```

Measures: microscopic disorder, heat capacity
Units: Joules per Kelvin
Context: physics, chemistry, statistical mechanics

### The Same Formula!

Up to a constant (k_B · ln 2 ≈ 10⁻²³ J/K/bit), they're identical.

This isn't coincidence. It reflects a deep truth: **both measure the same thing** — the number of yes/no questions needed to specify the exact microstate (for physics) or the exact message (for communication).

Maxwell's demon can't violate thermodynamics because erasing information requires energy — the bit-energy equivalence that emerges from this connection.

---

## Summary: The Information Framework

**Shannon Information:**
- Measures surprise: I(event) = -log₂(P(event))
- Measured in bits
- One bit = one fair coin flip of information

**Entropy:**
- Average surprise: H(X) = -Σ pᵢ log₂ pᵢ
- Maximum when all outcomes equally likely
- Zero when outcome is certain

**Conditional Entropy:**
- Uncertainty in X given Y: H(X|Y)
- Always ≤ H(X)
- Zero if Y determines X

**Mutual Information:**
- I(X;Y) = H(X) - H(X|Y)
- How much X tells you about Y
- Symmetric, non-negative
- Zero for independent variables

**Boltzmann Distribution:**
- P(state) ∝ exp(-E/k_B T)
- Maximum entropy given average energy
- Temperature controls spread

**Fisher Information:**
- Precision of parameter estimation
- Related to likelihood curvature
- Cramér-Rao bound: Var ≥ 1/I

---

## Preview: Fitness Measurability

In the next part, we'll use these tools to address a crucial question:

**When can selection work effectively?**

The answer involves Fisher information about fitness. Selection can only act to the extent that fitness differences are measurable — distinguishable from noise.

This leads to a bound: there's a minimum fitness difference that selection can reliably act on, determined by:
- Population size (more organisms = more measurements)
- Fitness variance (noisier fitness = harder to distinguish)
- Generation time (more generations = more opportunities)

Below this threshold, drift dominates. Above it, selection dominates.

This is the fitness measurability argument: selection's effectiveness is fundamentally limited by information-theoretic constraints on how precisely fitness can be estimated from finite populations.

The edge of chaos, maximum information transmission, fitness measurability — they all connect. Selection is an information-processing system, and information theory tells us its fundamental limits.

---

## Exercises

**Exercise 21.1:** Calculate the entropy of a fair 6-sided die. What about a loaded die where 6 has probability 1/2 and 1-5 each have probability 1/10?

**Exercise 21.2:** If X and Y are jointly distributed with P(X=0,Y=0) = 0.4, P(X=0,Y=1) = 0.1, P(X=1,Y=0) = 0.1, P(X=1,Y=1) = 0.4, calculate H(X), H(Y), H(X|Y), and I(X;Y). Are X and Y independent?

**Exercise 21.3:** Show that mutual information is symmetric: I(X;Y) = I(Y;X). (Hint: Express both in terms of H(X), H(Y), and H(X,Y).)

**Exercise 21.4:** For the Boltzmann distribution P(E) ∝ exp(-E/k_B T), show that the entropy is S = k_B(ln Z + ⟨E⟩/k_B T). (Hint: substitute the distribution into the entropy formula.)

**Exercise 21.5:** You flip a biased coin n times. The probability of heads is p, which you don't know. Derive the Fisher information I(p) and show that the Cramér-Rao bound gives Var(p̂) ≥ p(1-p)/n.

---

## Key Equations

| Concept | Formula | Meaning |
|---------|---------|---------|
| Surprise | -log₂(p) | How unexpected an event is |
| Shannon Entropy | H = -Σ pᵢ log₂ pᵢ | Average uncertainty |
| Conditional Entropy | H(X\|Y) | Uncertainty in X given Y |
| Mutual Information | I(X;Y) = H(X) - H(X\|Y) | Shared information |
| Boltzmann Entropy | S = k_B ln Ω | Thermodynamic disorder |
| Boltzmann Distribution | P ∝ exp(-E/k_B T) | Equilibrium probability |
| Fisher Information | I(θ) = E[(∂ ln p/∂θ)²] | Estimation precision |
| Cramér-Rao Bound | Var(θ̂) ≥ 1/I(θ) | Minimum variance |

---

*Next: Part 22 — Fitness Measurability: The Information Limits of Selection*
