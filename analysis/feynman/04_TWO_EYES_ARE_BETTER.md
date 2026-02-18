# Why You Need Two Eyes to See Yourself

*Binocular vision, negative cross-connections, and why thinking harder from one viewpoint is the worst strategy.*

---

## Start with Biology

Close one eye. Now try to thread a needle. Hard, right? Open both eyes. Easy.

Why? Each eye sees the needle from a slightly different angle. Neither view alone tells you the depth -- but the *difference* between the two views does. Your brain subtracts one image from the other, and what survives the subtraction is the depth information that was invisible to either eye alone.

This is parallax. Two slightly different observations of the same thing, combined by subtraction, revealing what neither could see alone.

Now here's the question that started this part of the investigation: does the same principle work for self-referential contamination? If one agent can't tell signal from echo, can two agents -- each hearing their own slightly different echo -- subtract out the echo and recover the signal?

---

## The Binocular Experiment

We built a system with N units, each observing the same signal but with independent contamination. Each unit sees:

    y_i(t) = s(t) + alpha * w_self * y_i(t-1) + w_cross * y_j(t-1)

where w_cross is a learnable weight connecting units. The units share their states through cross-connections, then the final prediction is the average of all units' outputs.

We expected w_cross to be *positive* -- units cooperatively sharing information. We expected the advantage to be dramatic at N = 2, like binocular vision.

---

## The Surprise: Cross-Connections Learn Negative Weights

Every single experiment, across all numbers of units, all contamination levels, all training configurations, the cross-connection weight w_cross converges to a *negative* value.

| N (units) | w_cross (mean) | Standard deviation |
|-----------|---------------|-------------------|
| 2 | -0.259 | 0.041 |
| 3 | -0.230 | 0.058 |
| 4 | -0.216 | 0.063 |
| 8 | -0.197 | 0.071 |

The units don't share information. They *subtract* each other's output.

And this makes perfect sense once you think about it the right way. Each unit sees: signal + its own contamination. The other unit sees: signal + *its* own contamination. The signal is the same in both observations. The contamination is different (each unit has its own echo history). So if you subtract one unit's output from the other, the common signal cancels partially, but the *different* contamination cancels even more. The subtraction isolates what's shared (signal) from what's different (echo).

This is exactly parallax. The two eyes don't agree on where the needle is because each eye has its own angular bias. Subtracting out what differs (the angular bias) reveals what's shared (the actual needle position).

The negative sign is the subtraction. The value -0.26 (not -1.0) reflects optimal weighting: you don't subtract the full other-eye signal, you subtract just enough to cancel the contamination without destroying too much of the shared signal.

---

## Does This Persist at Depth?

Maybe the negative cross-connections are a single-layer artifact. We tested with 1, 2, and 3 processing layers:

| Architecture | Layer 1 w_cross | Layer 2 w_cross | Layer 3 w_cross |
|-------------|----------------|----------------|----------------|
| 1-layer | -0.165 | -- | -- |
| 2-layer | -0.130 | -0.180 | -- |
| 3-layer | -0.083 | -0.181 | -0.189 |

Negative at *every* layer. And the magnitude *increases* with depth -- deeper layers perform progressively stronger decontamination. The first layer does a light subtraction; deeper layers do heavier cleaning, as if refining what the earlier layers started.

Also notice: when you add more layers, the first layer's cross-connection weakens (from -0.165 to -0.083). The deeper layers take over the decontamination work, allowing the first layer to focus more on signal.

---

## The Fair Test: Depth vs. Width

Here's the big question. Given a fixed computational budget, is it better to think deeply from one viewpoint, or think briefly from many viewpoints?

We held total compute constant at T * N = 10 (where T is processing depth and N is number of units) and tested four configurations:

| Config | N | T | Strategy |
|--------|---|---|----------|
| Deep | 1 | 10 | One perspective, deep reflection |
| Balanced-A | 2 | 5 | Two perspectives, moderate depth |
| Balanced-B | 5 | 2 | Five perspectives, minimal depth |
| Wide | 10 | 1 | Ten perspectives, no depth |

The result was unambiguous:

| Config | alpha=0.0 | alpha=0.4 | alpha=0.8 | alpha=1.0 |
|--------|-----------|-----------|-----------|-----------|
| Deep (N=1, T=10) | 0.0067 | 0.0115 | 0.0189 | 0.0235 |
| Balanced-A (N=2, T=5) | 0.0062 | 0.0099 | 0.0161 | 0.0200 |
| **Balanced-B (N=5, T=2)** | **0.0055** | **0.0070** | **0.0103** | **0.0125** |
| Wide (N=10, T=1) | 0.0060 | 0.0073 | 0.0103 | 0.0128 |

(Lower MSE is better.)

**Balanced-B wins at every contamination level.** Score across all conditions: Deep = 0 wins, Balanced = 12 wins, Wide = 0 wins. We also tested T * N = 20 with five configurations. Same result: the T = 2 balanced configuration always won.

The deep configuration -- one agent thinking hard for 10 steps -- was the *worst* strategy. Not just a little worse. 19-47% worse than balanced. Thinking harder from a single contaminated viewpoint has sharply diminishing returns. Each additional step of reflection contaminates the signal further, and without a second viewpoint, you can't tell reflection from reality.

---

## Why Balanced Beats Wide

The wide configuration (N = 10, T = 1) is close to balanced but not quite as good. Why?

Because T = 2 provides exactly one integration step. At T = 1, each unit outputs its prediction immediately. At T = 2, each unit first receives cross-connection information from the other units, then uses that information to refine its output. That one step of integration -- "let me check what the other eyes are seeing before I commit" -- is genuinely valuable.

Balanced-B (N = 5, T = 2) has 41 parameters. Wide (N = 10, T = 1) has 131 parameters. Despite having 3x fewer parameters, balanced wins. The architecture matters more than the parameter count.

---

## The Parallax-Competence Tradeoff

Before you rush off to add a second model to everything, there's a critical constraint.

We tried several ways to create two diverse viewpoints for a classification task:

| Diversity method | Error correlation | Individual accuracy | Ensemble vs. single model |
|-----------------|-------------------|--------------------|-----------------------------|
| Feature-split (each eye sees half the pixels) | 0.18 (excellent parallax) | ~60% (crippled) | -8.4% (worse) |
| Data-split (each eye sees half the data) | -0.87 (maximum parallax) | ~70% (weak) | -1.5% (worse) |
| Architecture-split (linear + MLP, full data) | ~0.45 (moderate parallax) | ~90% (full strength) | +0.6% (best) |

The methods that create the *most* parallax do so by *crippling each eye*. Feature-split gives beautiful decorrelation -- the eyes make completely different mistakes -- but each eye only sees half the image and is individually terrible. The parallax is "expensive": you bought diversity by sacrificing competence.

Architecture-split is the only method where both eyes see all the data but have different inductive biases. Each eye is strong on its own. The parallax comes for free, from the structural difference between a linear model and an MLP.

**The rule:** Both eyes must be strong. You can't sacrifice eye quality for eye diversity. Diversity must come from different ways of seeing, not from restricting what each eye sees.

This is why random initialization failed (as we discussed in Document 3). Two identical linear models converge to the same optimum -- they develop the same "visual cortex" regardless of where they started. Only genuinely different architectures maintain the independent perspectives that make parallax possible.

---

## What This Means for Machine Learning

The punchline for practitioners is sharp: **don't think harder from one perspective -- think briefly from many perspectives.**

Chain-of-thought reasoning (one model, many steps) is the "deep" strategy. It's the worst for self-referential problems. Ensemble methods with cross-evaluation (multiple models, one or two steps) are the "balanced" strategy. They're the best.

Positive cross-connections -- where models reinforce each other's conclusions -- are actively harmful. They amplify contamination. Think of it as groupthink: if two people with the same bias agree with each other, they become *more* confident in their shared mistake, not less.

Negative cross-connections -- where models *challenge* each other's conclusions -- are the mechanism of decontamination. Each model subtracts the other's bias. This is the scientific method in miniature: you don't validate a hypothesis by having its proponents agree with each other; you validate it by having critics look for what's wrong.

---

**The key insight:** When a system is contaminated by its own echo, the way to decontaminate is not to think harder (more depth) but to look from more angles (more width) with subtractive cross-connections that cancel echo while preserving signal. The cross-connections learn to be negative -- implementing subtraction, not addition -- because two contaminated views of the same signal reveal the signal through their difference, not their sum.
