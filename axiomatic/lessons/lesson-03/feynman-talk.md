# The Seven Axioms
### A Feynman-Voice Lecture

---

Look, we need to talk about axioms. I know, I know — the word "axiom" sounds like something from a Euclid textbook, all dusty and formal. But here's the thing: every theory has rules. Quantum mechanics has rules. Relativity has rules. And if you want to understand why the vacuum energy problem is a problem — and not just some technical annoyance we can sweep under the rug — you need to understand what rules quantum field theory is supposed to follow, and where the standard approach breaks them.

## The Game Has Rules

When you build a physical theory, you start with axioms — foundational principles that define what the theory *is*. For quantum mechanics, the axioms are things like "states evolve unitarily" and "probabilities sum to 1" and "measurement outcomes obey the Born rule." These aren't optional. They're the rules of the game. Break them and you don't have quantum mechanics anymore.

Now, quantum field theory inherits most of its axioms from quantum mechanics. Time evolution composes. Probability is conserved. Measurements work. Locality is respected. All good. But here's what's missing: *there is no axiom that says physical observables must be finite.*

And that's a problem. Because the mode vacuum — the ground state of standard QFT — has *infinite* energy density. And when you get infinity as an answer, you know something is wrong.

## The Seven Axioms

Let me lay them out for you. Seven rules. The first four are established — rock solid, confirmed by a century of experiments. The last three are what I'm calling the "framework axioms" — they're new, they're proposed to close the gap, and they're the key to fixing the vacuum energy problem.

### The Established Four

**P: Propagator Composition**

Time evolution composes. If a system evolves from time $t_0$ to $t_1$, and then from $t_1$ to $t_2$, the total evolution from $t_0$ to $t_2$ is the product:

$$
U(t_2, t_0) = U(t_2, t_1) \cdot U(t_1, t_0)
$$

**[ESTABLISHED]**. This is just the statement that dynamics is consistent. The future depends on the present, not on how you mentally divided up the time interval.

**Q: Unitarity**

Probability is conserved. The evolution operator is unitary:

$$
U^\dagger U = I
$$

**[ESTABLISHED]**. Without this, the norm of quantum states changes over time, and the Born rule gives probabilities that don't sum to 1. Information is created or destroyed. Unitarity is foundational.

**M': Measurement Consistency**

Measurements obey the Born rule. Probabilities sum to 1:

$$
\sum_i P(a_i) = 1
$$

Post-measurement states are normalizable. **[ESTABLISHED]**. This is the link between theory and experiment. Without it, you can't make predictions.

**L: Locality**

Operations on region $A$ don't affect statistics on spacelike-separated region $B$:

$$
[\hat{O}_A, \hat{O}_B] = 0
$$

for spacelike-separated $A$ and $B$. **[ESTABLISHED]**. No faster-than-light signaling. Required by relativity. Confirmed by Bell inequality tests.

These four are non-negotiable. Drop any of them and the theory falls apart.

### The Framework Three

Now here's where it gets interesting.

**A0: Existence**

Every bounded spatial region $R$ gets a finite-dimensional Hilbert space $H_R$ and a density matrix $\rho_R$.

**[FRAMEWORK]**. Why is this an axiom? Because in standard QFT on a continuum, the Hilbert space for any region is infinite-dimensional — one degree of freedom per point in space, and there are infinitely many points. That leads to UV divergences. A0 says: no, the true theory assigns *finite*-dimensional state spaces to bounded regions. You shouldn't need infinite information to describe a finite volume of space.

This is consistent with holographic principles — the Bekenstein bound says the entropy of a region scales with its surface area, not its volume. But it's not a standard assumption in QFT. Hence: **[FRAMEWORK]**.

**A1: Refinability**

Physics must converge as you refine your lattice. If you discretize space with lattice spacing $a$, and then make $a$ smaller, physical observables must approach finite limits:

$$
\lim_{a \to 0} \langle O \rangle_a = \text{finite}
$$

**[FRAMEWORK]**. This is the requirement that the continuum limit *exists*. If observables diverge as $a \to 0$, then you don't have a theory of continuous spacetime — you just have an infinite family of lattice theories with no limiting behavior. And the real world doesn't have a visible lattice, so if you introduce a lattice as a regularization tool, the limit $a \to 0$ must be well-defined.

Here's the kicker: **the mode vacuum fails A1**. Its energy density diverges as:

$$
\rho_{\text{mode}}(a) \sim \frac{\hbar c}{a^4}
$$

As $a \to 0$, this blows up. The mode vacuum does not have a well-defined continuum limit. That's not a technicality — that's a fundamental failure.

**F: Finiteness**

All physical observables — energy density $\rho$, pressure $p$, particle number density $n$ — are finite *without regularization or renormalization*:

$$
\rho < \infty, \quad p < \infty, \quad n < \infty
$$

**[FRAMEWORK]**. This is the requirement that the theory give measurable predictions without subtracting infinities. Renormalization "fixes" divergent observables by subtraction, but subtraction is not explanation. F says: the vacuum must have finite energy density *before* any subtractions. If your vacuum gives $\rho = \infty$, you have the wrong vacuum.

Again, the mode vacuum fails. Its energy density is infinite. The usual response is: "That's fine, we subtract it away and work only with energy differences." But that's dodging the question. F says: no, the absolute energy density must be finite.

## Why Each Axiom Is Necessary

Let me show you what breaks if you drop one of these axioms.

**Drop P:** Time evolution is inconsistent. The state at time $t_2$ depends on whether you evolved directly from $t_0$, or stopped at an intermediate time. Dynamics is undefined.

**Drop Q:** Probability is not conserved. The norm of states changes. Probabilities don't sum to 1. You lose the Born rule.

**Drop M':** Measurement doesn't work. You can't connect theory to experiment. Quantum mechanics has no empirical content.

**Drop L:** Faster-than-light signaling. Alice does something in region $A$, Bob sees it instantly in spacelike-separated region $B$. Causality is violated. Relativity is violated.

**Drop A0:** There's no state to describe. You can't write down a quantum state for a region. The theory has no starting point.

**Drop A1:** No continuum limit. Physics depends on the arbitrary cutoff $a$. You have a family of lattice theories, but no limit as $a \to 0$. And the world doesn't have a built-in lattice, so this is a failure.

**Drop F:** Infinite observables. The vacuum has infinite energy density. You must introduce renormalization to subtract it away. This works pragmatically, but it's conceptually unsatisfying. You never actually answer the question: "What is the energy density of the vacuum?"

## A1 Is the Key

Of the seven axioms, A1 is the one that distinguishes the axiomatic framework from standard QFT. Standard QFT accepts divergent bare quantities. You compute the energy density of the mode vacuum, get $\rho \sim a^{-4}$, and say: "That's fine, we'll subtract it. Only energy *differences* are physical."

A1 rejects this. It says: no, the energy density of the vacuum must be finite, *without subtraction*. If your chosen vacuum gives $\rho \to \infty$ as $a \to 0$, then you've chosen the wrong vacuum. There exists a different state — one that satisfies all seven axioms — and *that* is the physical vacuum.

This is not an arbitrary demand. It's the requirement that the continuum limit exist. If physics depends on the cutoff, you don't have a theory of continuous spacetime.

## The Mode Vacuum Fails

Let me be very clear about this. The mode vacuum — the ground state of standard QFT, defined by $a_k |0\rangle = 0$ for all modes $k$ — satisfies six of the seven axioms. It satisfies P (time evolution composes), Q (unitarity), M' (measurements work), L (locality), arguably A0 (local states exist on a lattice), and even F on a lattice (observables are finite for fixed $a > 0$).

But it *fails* A1. Its energy density diverges quartically with the cutoff:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \cdot \left(\frac{\pi}{a}\right)^4 \cdot [1 + O(ma)]
$$

As $a \to 0$, this goes to infinity. The mode vacuum does not have a well-defined continuum limit. **[PROVEN]** — this is a straightforward calculation, and we'll do it explicitly in Lesson 4.

So the mode vacuum is not the physical vacuum. It's mathematically elegant — Lorentz-invariant, maximally entangled, invariant under all the symmetries you want. But it fails A1, and therefore it's not the right vacuum for a theory that is supposed to describe the real world.

## The Coherent Vacuum Succeeds

Here's the punchline. There exists a different vacuum state, constructed from coherent states of the field modes (we'll build it in Lesson 5), for which:

$$
\lim_{a \to 0} \rho_{\text{coherent}}(a) = \text{finite}
$$

This state satisfies all seven axioms. It has finite energy density, finite pressure, finite particle number. It respects all the symmetries. It evolves unitarily. It gives consistent measurement outcomes. And it has a well-defined continuum limit.

That's the coherent vacuum. And that's the central claim of the axiomatic framework: the physical vacuum is not the mode vacuum, it's the coherent vacuum.

## The Cosmological Constant Problem, Reframed

The cosmological constant problem is usually stated as: "Why is the observed vacuum energy $\rho_{\text{obs}} \approx 6 \times 10^{-10}$ J/m$^3$ so much smaller than the predicted value $\rho_{\text{QFT}} \sim 10^{113}$ J/m$^3$?"

But this assumes that $\rho_{\text{QFT}}$ *is* the prediction of quantum field theory. It's not. It's the prediction of quantum field theory *with the mode vacuum*. And if the mode vacuum violates axiom A1, then it's not the physical vacuum, and its energy density is not the physical prediction.

The axiomatic framework reframes the problem as:

**"What is the vacuum state that satisfies all seven axioms, and what is its energy density?"**

That's a well-posed question. The answer is: the coherent vacuum, and its energy density is finite. Whether that finite value matches $\rho_{\text{obs}}$ is a separate question, which we'll address in later lessons. But the first step is establishing that a finite, A1-satisfying vacuum exists.

## What We've Established

Let me summarize what's proven and what's framework.

The first four axioms — P, Q, M', L — are **[ESTABLISHED]**. Standard quantum mechanics. Confirmed by a century of experiments. Non-negotiable.

The next three axioms — A0, A1, F — are **[FRAMEWORK]**. They're proposed as necessary conditions for a well-defined QFT with finite observables. They're motivated by physical reasoning, but they're not part of the standard formulation.

The mode vacuum satisfies P, Q, M', L (and arguably A0 and F on a lattice), but it *fails* A1. This is **[PROVEN]** — we'll compute the divergence explicitly next lesson.

The coherent vacuum satisfies all seven, including A1. This is **[PREDICTED]** by the axiomatic framework — we'll construct it and verify this in Lesson 5.

## The Rules of the Game

Here's the bottom line. The seven axioms are the rules of the game. They define what a vacuum state must satisfy to be physically acceptable. The mode vacuum breaks the rules. The coherent vacuum follows the rules.

That's not a value judgment — it's a statement about mathematical properties. The mode vacuum has infinite energy density. The coherent vacuum has finite energy density. One satisfies A1, one doesn't.

And if you want a quantum field theory that produces finite, measurable predictions for all observables — not just energy differences, but absolute energy density — then you need a vacuum that satisfies all seven axioms.

The mode vacuum isn't it. The coherent vacuum is.

## What Comes Next

In Lesson 4, we'll construct the mode vacuum explicitly. We'll see why it's Lorentz-invariant, why it's maximally entangled, and why its energy density diverges quartically. We'll compute the divergence, not as an abstract claim, but as a concrete result. You'll see exactly where the $a^{-4}$ comes from and why renormalization is needed to hide it.

Then, in Lesson 5, we'll build the coherent vacuum. We'll show that it satisfies all seven axioms. We'll compute its energy density and verify that the continuum limit exists. And we'll see why this state — not the mode vacuum — is the physical ground state of quantum field theory.

The axioms are the foundation. The mode vacuum is the wrong building. The coherent vacuum is the right one. Let's see why.

---

*Summary of evidence tiers:*
- *Axioms P, Q, M', L: **[ESTABLISHED]** — standard quantum mechanics*
- *Axioms A0, A1, F: **[FRAMEWORK]** — proposed extensions*
- *Mode vacuum fails A1: **[PROVEN]** — energy density diverges as $a^{-4}$*
- *Coherent vacuum satisfies A1: **[PREDICTED]** — to be demonstrated*
