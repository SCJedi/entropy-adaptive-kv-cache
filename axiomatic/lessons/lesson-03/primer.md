# Primer: The Seven Axioms

## The Big Idea

Every theory has rules. Quantum mechanics has rules about how states evolve, how measurements work, and how probability is conserved. These rules are called axioms — foundational principles that define what the theory *is*.

Standard quantum field theory (QFT) inherits most of its axioms from quantum mechanics, but it has a gap: there is no rule that says physical observables — like the energy density of empty space — must be *finite*. The mode vacuum (standard QFT's ground state) has infinite energy density. The usual fix is to subtract the infinity away and work only with energy differences. That works for calculations, but it is conceptually unsatisfying.

The axiomatic framework proposes three new axioms to close this gap:

- **A0 (Existence)**: Every bounded region of space has a finite-dimensional state.
- **A1 (Refinability)**: As you make your description finer (smaller lattice spacing), observables must converge to finite values, not diverge.
- **F (Finiteness)**: Energy density, pressure, and particle number must be finite without subtraction.

Add these to the four established axioms of quantum mechanics (time evolution composes, probability is conserved, measurements work, and no faster-than-light signaling), and you get seven rules that any vacuum state must satisfy.

The mode vacuum satisfies six of the seven. It fails A1: its energy density diverges as you refine the lattice. This failure is the root of the vacuum energy problem.

## The Four Established Axioms

These are non-negotiable. They are the core of quantum mechanics, confirmed by a century of experiments.

**P (Propagator Composition):** If a system evolves from time $t_0$ to $t_1$, then from $t_1$ to $t_2$, the total evolution is the product: $U(t_2, t_0) = U(t_2, t_1) \cdot U(t_1, t_0)$. This is just the statement that time evolution is consistent.

**Q (Unitarity):** Probability is conserved. The evolution operator $U$ satisfies $U^\dagger U = I$. Without this, the Born rule would give probabilities that do not sum to 1.

**M' (Measurement Consistency):** Measurements obey the Born rule. Probabilities sum to 1. Post-measurement states are normalizable. This is the link between theory and experiment.

**L (Locality):** Operations in region $A$ cannot affect statistics in a spacelike-separated region $B$. No faster-than-light signaling. This is required by relativity.

## The Three Framework Axioms

These are new. They are not standard assumptions in QFT, but they are necessary if you want finite, measurable predictions.

**A0 (Existence):** Every bounded spatial region gets a finite-dimensional Hilbert space. You do not need infinite information to describe a finite region. (This is consistent with holographic principles like the Bekenstein bound.)

**A1 (Refinability):** Physics must converge as you refine your lattice. If you compute the energy density on a lattice with spacing $a$, and then make $a$ smaller, the result must approach a finite limit — not blow up. Formally: $\lim_{a \to 0} \langle O \rangle_a = \text{finite}$.

**F (Finiteness):** Energy density $\rho$, pressure $p$, particle number $n$ must all be finite without renormalization. No infinities to subtract. The vacuum must give measurable values directly.

## Why A1 Is Key

The mode vacuum — the ground state of standard QFT — has energy density:

$$
\rho_{\text{mode}}(a) \sim \frac{\hbar c}{a^4}
$$

As $a \to 0$, this diverges. The mode vacuum *fails* axiom A1. It does not have a well-defined continuum limit.

Renormalization "fixes" this by subtracting the divergent part and working only with energy differences. But subtraction is not explanation. A1 says: no, the vacuum energy density must be finite *before* subtraction. If your vacuum gives a divergent result, you have the wrong vacuum.

The coherent vacuum (constructed in later lessons) satisfies A1. Its energy density is finite for all $a > 0$, and the limit $a \to 0$ exists.

## What Comes Next

Lesson 4 will show you the mode vacuum in detail: how it is constructed (Fock space, creation and annihilation operators), why it is Lorentz-invariant, and why its energy density diverges. We will compute the divergence explicitly and see that it is not a technicality — it is a fundamental property of the mode vacuum.

Then, in Lesson 5, we will construct the coherent vacuum and show that it satisfies all seven axioms, including A1 and F.
