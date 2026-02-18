# Lesson 1: What Are Axioms and Why Physics Needs Them

## Overview

Axioms are the foundational rules that define what counts as a valid theory before you start computing. Physics has always operated on axioms -- whether explicitly stated (as in Euclid's geometry or Newton's mechanics) or implicitly assumed (as in much of modern field theory). Understanding what axioms are, why we need them, and how changing them alters the entire structure of a theory is essential to the project of this course: defining a consistent set of axioms for vacuum selection in quantum field theory.

This lesson is primarily historical and conceptual. Every historical claim here is **[ESTABLISHED]** -- documented in the history of mathematics and physics.

## 1.1 Euclid's Geometry: The Original Axiomatic System

The axiomatic method began with Euclid around 300 BCE. His *Elements* established geometry not as a collection of scattered facts, but as a logical edifice built from five axioms (or "postulates"):

1. A straight line can be drawn between any two points.
2. A finite straight line can be extended continuously.
3. A circle can be drawn with any center and radius.
4. All right angles are equal to one another.
5. **The parallel postulate:** If a line crosses two other lines and makes the interior angles on one side less than two right angles, then the two lines will meet on that side if extended far enough.

The first four are simple and self-evident. The fifth is different -- more complex, less intuitive, and for two millennia mathematicians tried to prove it from the first four. They failed. **[ESTABLISHED]**

## 1.2 Non-Euclidean Geometry: What Happens When You Change the Axioms

In the 19th century, Gauss, Bolyai, Lobachevsky, and Riemann discovered that you could replace the parallel postulate with a different axiom and get a logically consistent geometry -- just a different one. **[ESTABLISHED]**

- **Hyperbolic geometry** (Bolyai-Lobachevsky): Through a point not on a line, infinitely many parallel lines can be drawn. The angles of a triangle sum to less than 180°. This geometry describes surfaces with constant negative curvature, like a saddle.

- **Elliptic geometry** (Riemann): No parallel lines exist; all lines eventually meet. The angles of a triangle sum to more than 180°. This geometry describes surfaces with constant positive curvature, like a sphere.

All three geometries are internally consistent. Which one describes physical space? That's an empirical question. Einstein showed in 1915 that spacetime has non-Euclidean geometry -- specifically, Riemannian geometry with variable curvature determined by mass-energy. **[ESTABLISHED]**

The lesson: axioms define the structure of the theory. Change the axioms, and you change the theory entirely. Consistency is not the same as truth; a set of axioms can be internally consistent but fail to describe reality.

## 1.3 Newton's Laws as Axioms

Newton's *Principia* (1687) is another axiomatic system, though Newton didn't call it that. His three laws of motion are axioms:

1. A body at rest stays at rest, and a body in motion stays in uniform motion, unless acted upon by a force.
2. $\mathbf{F} = m\mathbf{a}$.
3. For every action, there is an equal and opposite reaction.

From these three axioms, plus the law of universal gravitation, Newton derived the motion of planets, the tides, the precession of the equinoxes, and the trajectories of projectiles. The entire structure of classical mechanics follows deductively. **[ESTABLISHED]**

But these axioms are not eternal truths. At high speeds, they fail -- special relativity replaces them. In strong gravitational fields, they fail again -- general relativity replaces them. In the atomic regime, they fail catastrophically -- quantum mechanics replaces them.

The axioms worked brilliantly within their domain of validity, but they were approximations, not fundamental truths. This raises a critical question: what axioms underlie quantum field theory?

## 1.4 The Axiomatic Crisis in Mathematics

In the early 20th century, mathematics faced a foundational crisis. Cantor's set theory had produced paradoxes -- most famously, Russell's paradox (1901):

> Consider the set of all sets that do not contain themselves. Does it contain itself?

If it does, then by definition it doesn't. If it doesn't, then by definition it does. Contradiction. **[ESTABLISHED]**

This revealed that naive set theory was inconsistent. David Hilbert responded with an ambitious program: formalize all of mathematics in a rigorous axiomatic system, prove that the system is consistent (contains no contradictions), and prove that it is complete (every true statement can be proven within it). **[ESTABLISHED]**

In 1931, Kurt Gödel shattered this dream with his incompleteness theorems:

1. **First incompleteness theorem:** In any consistent formal system powerful enough to encode arithmetic, there exist true statements that cannot be proven within the system.
2. **Second incompleteness theorem:** No consistent formal system can prove its own consistency.

**[ESTABLISHED]** -- These are mathematical theorems, proven rigorously.

The upshot: any axiomatic system rich enough to be interesting will either be incomplete (some truths are unprovable) or inconsistent (it contains contradictions). You cannot have both completeness and consistency.

This does not mean mathematics collapses. It means we must accept axiomatic systems as useful tools, not absolute foundations. We choose axioms that are consistent with known results, lead to fruitful predictions, and avoid known paradoxes -- but we cannot prove they are "the right axioms" in any absolute sense.

## 1.5 Why Physics Needs Axioms

Physics is not mathematics. We do not prove that nature obeys certain laws; we propose laws, derive their consequences, and test them against experiment. But even this process requires axioms -- unstated assumptions about what constitutes a valid physical theory.

Consider quantum mechanics. The standard axioms are:

1. Physical states are vectors $|\psi\rangle$ in a Hilbert space, normalized so that $\langle\psi|\psi\rangle = 1$.
2. Observables are Hermitian operators acting on the Hilbert space.
3. Measurement of an observable yields one of its eigenvalues, with probability given by the Born rule: $P(\lambda) = |\langle\lambda|\psi\rangle|^2$.
4. Between measurements, the state evolves unitarily: $|\psi(t)\rangle = e^{-iHt/\hbar}|\psi(0)\rangle$.

These are not derived from anything more fundamental -- they are the axioms. They define what "quantum mechanics" means. **[ESTABLISHED]** in the sense that these are the standard postulates taught in every quantum mechanics textbook.

Now consider quantum field theory (QFT). What are the axioms? This is where things get murky.

## 1.6 The Problem in Quantum Field Theory

In QFT, we quantize fields -- objects with a value at every point in space. Each momentum mode becomes a harmonic oscillator, and the ground state (the "vacuum") is the product of all the individual oscillator ground states.

But there are infinitely many modes. Summing the zero-point energies $\frac{1}{2}\hbar\omega$ over all modes gives a divergent result:

$$
E_0 = \sum_{\mathbf{k}} \frac{1}{2}\hbar\omega_{\mathbf{k}} \to \infty
$$

This is not a calculation error -- it is a direct consequence of standard QFT. **[PROVEN]** in the sense that the integral diverges as the cutoff is removed.

Renormalization allows us to subtract infinities and compute observable differences, but it does not tell us the value of the vacuum energy density. When we try to connect QFT to cosmology (where the vacuum energy contributes to the cosmological constant), we predict a value $10^{123}$ times larger than observed. **[OBSERVATIONAL DISCREPANCY]**

The standard response is "there must be new physics at the Planck scale that cuts this off." But this is a hope, not a derivation. The real issue is deeper: QFT as currently formulated does not have a well-defined prescription for selecting the vacuum state when infinitely many states are available.

We need axioms.

## 1.7 Consistency vs. Truth

Here is the central lesson from the history of axioms: consistency does not imply truth.

Euclidean geometry is internally consistent. Every theorem follows logically from the axioms. But physical space is not Euclidean -- it is curved. Euclidean geometry is a beautiful, rigorous, logically flawless system that happens to be wrong about the universe.

Similarly, we can write down many axiomatic systems for quantum field theory. Some will be internally consistent but fail to match experiment. Others may match current experiments but break down at higher energies or in cosmological contexts. The goal is to find axioms that are:

1. **Internally consistent** -- they do not lead to contradictions.
2. **Empirically adequate** -- they match all known observations.
3. **Predictive** -- they make novel, testable predictions.
4. **Well-defined** -- they provide unambiguous answers to questions like "what is the vacuum energy density?"

This is the task of axiomatic quantum field theory.

## 1.8 The Wightman Axioms: A Partial Success

In the 1950s, Arthur Wightman formulated a set of axioms for relativistic QFT. The key axioms include: **[ESTABLISHED]**

1. **Hilbert space structure:** States form a Hilbert space with a vacuum state $|0\rangle$.
2. **Relativistic covariance:** There exists a unitary representation of the Poincaré group acting on states.
3. **Spectrum condition:** The energy-momentum operator $P^\mu$ has spectrum in the forward light cone ($P^0 \geq 0$ and $P^2 \geq 0$).
4. **Locality:** Operators at spacelike-separated points commute (or anticommute for fermions).
5. **Vacuum uniqueness:** The vacuum $|0\rangle$ is the unique state annihilated by all annihilation operators, and it is Poincaré-invariant.

These axioms exclude many pathologies (negative energies, acausal propagation, multiple inequivalent vacua). But they do not solve the cosmological constant problem. The vacuum energy is still formally infinite, and the axioms provide no mechanism for selecting a finite value.

The Wightman axioms are a major achievement -- they provide a rigorous framework for relativistic QFT. But they are not sufficient for our purposes. We need axioms that constrain the vacuum state itself.

## 1.9 What We're Going to Do in This Course

This course proposes seven axioms for vacuum selection:

1. **Hilbert Space Structure** (Wightman Axiom I)
2. **Relativistic Covariance** (Wightman Axiom II)
3. **Spectrum Condition** (Wightman Axiom III, modified)
4. **Locality** (Wightman Axiom IV)
5. **Discrete Translational Symmetry** (new)
6. **Entropy Minimization** (new)
7. **Finite Energy Density** (new, cosmological)

The first four are standard. The last three are novel constraints designed specifically to address the vacuum selection problem. We will define them rigorously, justify them physically, and investigate their consequences.

The central claim of this course is that these seven axioms uniquely select a particular vacuum state -- the "cell vacuum" -- which has finite energy density, matches all low-energy experiments, and makes testable predictions at higher energies.

Whether this claim is correct is an open question. The axioms are proposed, not proven. But they are precise, falsifiable, and grounded in well-established physics. That makes them worth investigating.

## 1.10 The Difference Between Axioms and Hypotheses

An axiom is a foundational assumption that defines the structure of a theory. A hypothesis is a proposed explanation for a specific phenomenon, subject to testing and revision.

Newton's second law $\mathbf{F} = m\mathbf{a}$ is an axiom of classical mechanics. The inverse-square law of gravity $F = Gm_1m_2/r^2$ is a hypothesis (later elevated to an axiom, and later still replaced by general relativity).

In this course, the seven axioms define what we mean by a "valid vacuum state" in QFT. They are not hypotheses about the vacuum -- they are the criteria by which we judge candidate vacua. Once the axioms are in place, the task is deductive: which vacuum states satisfy all seven axioms? If only one does, then that is the vacuum of our universe (assuming the axioms are correct). If many do, then additional constraints are needed. If none do, then the axioms are inconsistent and must be revised.

This is the axiomatic method applied to quantum field theory.

## 1.11 Why Axioms Can Fail

Axioms are not guaranteed to be correct. They can fail in (at least) three ways:

1. **Internal inconsistency:** The axioms contradict each other. (Example: If we demanded both $E_{\text{vac}} = 0$ exactly and $E_{\text{vac}} = \sum_k \frac{1}{2}\hbar\omega_k$ for infinitely many modes, we would have an inconsistency.)

2. **Empirical failure:** The axioms are consistent but predict something that contradicts observation. (Example: Euclidean geometry is consistent, but spacetime is not Euclidean.)

3. **Incompleteness:** The axioms are consistent with observations but do not uniquely determine the answer to an important question. (Example: The Wightman axioms do not determine the vacuum energy density.)

The seven axioms proposed in this course could fail in any of these ways. Testing for internal consistency is a mathematical task. Testing for empirical adequacy requires comparing predictions to experiment. Testing for completeness requires checking that the axioms sufficiently constrain the space of possible vacua.

This is why axioms must be stated precisely and their consequences derived rigorously. Only then can we determine whether they succeed or fail.

## 1.12 Axioms vs. Principles

A principle is a heuristic guide -- a general insight that suggests the form of a theory but is not itself a precise rule. Examples:

- **The equivalence principle** (general relativity): Locally, gravitational acceleration is indistinguishable from acceleration in flat spacetime. This guided Einstein to develop GR, but the axioms of GR are the Einstein field equations, not the equivalence principle itself.

- **The correspondence principle** (quantum mechanics): Quantum predictions must reduce to classical predictions in the limit $\hbar \to 0$ or $n \to \infty$. This is a useful guide, but the axioms of QM are the Hilbert space postulates and the Born rule, not the correspondence principle.

Principles inspire axioms. Axioms define theories.

In this course, we will invoke principles (such as "the vacuum should be the state of minimum energy consistent with symmetries") to motivate axioms (such as "the vacuum must satisfy the spectrum condition"). But the axioms are what matter. They are the precise, testable rules.

## 1.13 The Role of Symmetry in Axiomatic Systems

Symmetry plays a special role in physics. A symmetry is a transformation that leaves the laws of physics unchanged. Symmetries constrain the form of physical theories and often lead directly to conservation laws (Noether's theorem). **[ESTABLISHED]**

In Euclidean geometry, the symmetries are translations, rotations, and reflections. These symmetries follow from the axioms (particularly the axioms that "all points are equivalent" and "all directions are equivalent").

In quantum field theory, the fundamental symmetries are:

- **Poincaré symmetry:** Spacetime translations, rotations, and boosts.
- **Gauge symmetry:** Local phase transformations (in electromagnetism, the weak force, and the strong force).
- **Discrete symmetries:** Charge conjugation $C$, parity $P$, and time reversal $T$.

The Wightman axioms build Poincaré symmetry into the structure of the theory. Axiom 5 in our list introduces a new discrete symmetry: translational invariance on a discrete lattice. This symmetry is not fundamental -- it is emergent, arising from the finite cell size of the cell vacuum. But it plays a crucial role in ensuring that the vacuum energy density is well-defined.

## 1.14 What an Axiomatic Approach Cannot Do

An axiomatic system is a tool, not a magic wand. It cannot:

- **Derive fundamental constants.** No set of axioms will tell you the value of the fine structure constant $\alpha \approx 1/137$ or the mass of the electron. These are inputs, not outputs.

- **Prove its own correctness.** Gödel's second incompleteness theorem ensures that no consistent system can prove its own consistency. The only way to validate axioms is through empirical testing.

- **Predict phenomena outside its domain.** Classical mechanics does not predict quantum effects. Quantum mechanics does not predict spacetime curvature. Each axiomatic system has a limited domain of validity.

What an axiomatic approach *can* do is provide a rigorous framework within which to ask precise questions and derive unambiguous answers. If the axioms are chosen well, the answers will match experiment. If not, the discrepancies will reveal where the axioms need revision.

## 1.15 The Standard Model as an Axiomatic System

The Standard Model of particle physics is, in practice, an axiomatic system. The axioms are:

1. Spacetime is four-dimensional Minkowski space.
2. Matter consists of spin-1/2 fermions (quarks and leptons) in specific representations of the gauge group $SU(3) \times SU(2) \times U(1)$.
3. Forces are mediated by spin-1 gauge bosons (gluons, $W^\pm$, $Z$, photon).
4. Masses arise from spontaneous symmetry breaking via the Higgs field.
5. Dynamics are governed by the Lagrangian density of the Standard Model, which is the most general renormalizable Lagrangian consistent with the gauge symmetries.

These axioms are not written in every textbook, but they are the implicit assumptions. From them, we derive the Feynman rules, compute scattering amplitudes, and predict particle masses, decay rates, and cross sections. The agreement with experiment is spectacular -- the Standard Model is the most precisely tested scientific theory in history. **[ESTABLISHED]**

But the Standard Model is incomplete. It does not include gravity. It does not explain dark matter or dark energy. It does not explain the values of its 19 free parameters (particle masses, coupling constants, mixing angles). And it does not determine the vacuum energy density.

The seven axioms proposed in this course are an attempt to extend the Standard Model framework to answer one of these open questions: the vacuum energy.

## 1.16 Summary: What Axioms Are and Why We Need Them

- **Axioms are foundational rules** that define the structure of a theory before you start calculating.
- **Axioms are not self-evident truths** -- they are choices, subject to empirical validation.
- **Changing the axioms changes the theory entirely.** Non-Euclidean geometry, special relativity, and quantum mechanics all arose by replacing old axioms with new ones.
- **Consistency does not imply truth.** A set of axioms can be internally consistent but fail to describe reality.
- **Physics needs axioms** to define what counts as a valid theory, to exclude pathologies, and to provide unambiguous answers to well-posed questions.
- **QFT currently lacks axioms for vacuum selection.** The Wightman axioms provide a rigorous framework for relativistic QFT, but they do not solve the cosmological constant problem.
- **This course proposes seven axioms** designed specifically to select a unique vacuum state with finite energy density.

The rest of this course will develop the mathematical tools needed to state these axioms precisely (Lessons 2-4), define the axioms themselves (Lesson 5), and investigate their consequences (Lessons 6-7).

## Summary of Evidence Tiers

| Claim | Status |
|-------|--------|
| Euclid formulated five axioms for geometry | [ESTABLISHED] |
| Non-Euclidean geometries are internally consistent | [ESTABLISHED] |
| Spacetime is non-Euclidean (general relativity) | [ESTABLISHED] |
| Newton's laws are axioms of classical mechanics | [ESTABLISHED] |
| Russell's paradox reveals inconsistency in naive set theory | [ESTABLISHED] |
| Gödel's incompleteness theorems | [PROVEN] |
| Standard axioms of quantum mechanics | [ESTABLISHED] |
| Wightman axioms for relativistic QFT | [ESTABLISHED] |
| Sum of zero-point energies diverges | [PROVEN] |
| Cosmological constant discrepancy ($10^{123}$ factor) | [OBSERVATIONAL DISCREPANCY] |

## Looking Ahead

Axioms are abstract rules. To apply them to vacuum selection, we need mathematical tools: Hilbert spaces, quantum states, density matrices, tensor products, entanglement. These are the subjects of Lesson 2.

Once the mathematical framework is in place, we will define quantum fields (Lesson 3), discuss what "vacuum" means in QFT (Lesson 4), state the seven axioms precisely (Lesson 5), derive their consequences (Lesson 6), and investigate the experimental predictions (Lesson 7).
