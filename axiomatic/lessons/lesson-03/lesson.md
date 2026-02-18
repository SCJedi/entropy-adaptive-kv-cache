# Lesson 3: The Seven Axioms

## Overview

Every physical theory rests on axioms — foundational principles that define what the theory *is* and constrain what it can predict. Standard quantum field theory (QFT) inherits most of its axioms from quantum mechanics and special relativity, but leaves one critical question unaddressed: *What ensures that physical observables remain finite as we refine our description of spacetime?*

The axiomatic vacuum selection framework extends the standard axioms with three new principles:

- **A0 (Existence)**: Every bounded spatial region has a finite-dimensional state space.
- **A1 (Refinability)**: Physics converges as we refine our lattice; observables do not diverge.
- **F (Finiteness)**: All physical observables are finite without regularization.

Combined with the four established axioms of quantum mechanics — **P (Propagator Composition)**, **Q (Unitarity)**, **M' (Measurement Consistency)**, and **L (Locality)** — these seven axioms form a complete specification of what we demand from a well-defined quantum field theory.

This lesson states each axiom precisely, explains why it is necessary, and shows what pathologies arise when it is violated. By the end, you will see that the mode vacuum of standard QFT satisfies six of the seven axioms but *fails* axiom A1. That failure is not a technicality — it is the root of the vacuum energy problem.

## 3.1 The Four Established Axioms

The first four axioms are inherited from the standard formulation of quantum mechanics and have been tested exhaustively for nearly a century. Every result in this section is **[ESTABLISHED]** — confirmed by experiment and universally accepted.

### P: Propagator Composition

**Statement:** Time evolution operators compose. If a system evolves from time $t_0$ to $t_1$, then from $t_1$ to $t_2$, the total evolution from $t_0$ to $t_2$ is the product:

$$
U(t_2, t_0) = U(t_2, t_1) \cdot U(t_1, t_0)
$$

**Why it's necessary:** Without composition, time evolution would depend on the path taken through intermediate times. Physics would not have a consistent notion of "the future state" given "the present state." Dynamics would be undefined.

**Evidence tier:** **[ESTABLISHED]**. This is the defining property of a group representation of time translations. It follows from the existence of a Hamiltonian generating time evolution. Confirmed in every dynamical system ever measured.

### Q: Unitarity

**Statement:** Time evolution preserves probability. The evolution operator $U$ is unitary:

$$
U^\dagger U = U U^\dagger = I
$$

**Why it's necessary:** Probability must sum to 1. If $U$ were not unitary, the norm of quantum states would change over time, and the Born rule would give probabilities that do not sum to 1. Information would be created or destroyed.

**Evidence tier:** **[ESTABLISHED]**. Conservation of probability is foundational to quantum mechanics. Violated only in open systems (where the environment carries away information) or in phenomenological models of decoherence. For isolated systems, confirmed to extraordinary precision in experiments ranging from neutron interferometry to atomic clocks.

### M': Measurement Consistency

**Statement:** Measurement outcomes obey the Born rule. Given a state $|\psi\rangle$ and an observable $A$ with eigenstates $|a_i\rangle$, the probability of outcome $a_i$ is:

$$
P(a_i) = |\langle a_i|\psi\rangle|^2
$$

These probabilities sum to 1:

$$
\sum_i P(a_i) = 1
$$

After measurement yielding outcome $a_i$, the state collapses to $|a_i\rangle$ (or a normalizable superposition within the eigenspace if degenerate).

**Why it's necessary:** Without the Born rule, quantum mechanics has no connection to experiment. Measurement is the interface between theory and observation. The requirement that probabilities sum to 1 and that post-measurement states are normalizable ensures that the theory is internally consistent — you can make predictions, perform measurements, and continue making predictions afterward.

**Evidence tier:** **[ESTABLISHED]**. The Born rule has been tested in countless experiments, from photon polarization measurements to Bell inequality violations to quantum computing experiments. No deviation has ever been observed.

### L: Locality (No-Signaling)

**Statement:** Operations on a spatial region $A$ cannot instantaneously affect measurement statistics in a spacelike-separated region $B$. Formally, if regions $A$ and $B$ are outside each other's light cones, then:

$$
[\hat{O}_A, \hat{O}_B] = 0
$$

for all observables $\hat{O}_A$ localized in $A$ and $\hat{O}_B$ localized in $B$.

**Why it's necessary:** Without locality, you could send signals faster than light. Build a detector in region $B$, perform measurements in region $A$, and transmit information instantaneously by choosing which measurement to perform. This violates causality and leads to logical paradoxes (the "grandfather paradox" of time travel).

**Evidence tier:** **[ESTABLISHED]**. Locality is a foundational principle of relativity. Quantum mechanics is locally causal: measurement choices in $A$ do not affect measurement outcomes in spacelike-separated $B$, even though $A$ and $B$ may be entangled. Confirmed by Bell inequality tests and quantum communication experiments.

---

## 3.2 The Three Framework Axioms

The next three axioms are *not* established principles inherited from quantum mechanics. They are **[FRAMEWORK]** — proposed as necessary conditions for a well-defined QFT with finite observables. They are motivated by physical reasoning and consistency requirements, but they go beyond the standard formulation.

### A0: Existence

**Statement:** Every bounded spatial region $R$ is associated with a finite-dimensional Hilbert space $H_R$ and a density matrix $\rho_R$ representing the local state. Observables on $R$ are Hermitian operators on $H_R$.

**Why it's necessary:** Without A0, there is no state to work with. A quantum theory must assign a state space to every region of space. The requirement that $H_R$ be finite-dimensional when $R$ is bounded ensures that the local state is well-defined — you are not required to specify an infinite amount of information to describe a finite region.

**Evidence tier:** **[FRAMEWORK]**. In standard QFT on a lattice with finite cutoff, $H_R$ is finite-dimensional (one degree of freedom per lattice site). In the continuum limit, $H_R$ becomes infinite-dimensional, which causes technical difficulties (UV divergences). A0 proposes that the true theory — after all cutoffs are removed — still assigns finite-dimensional spaces to bounded regions. This is consistent with holographic principles (Bekenstein bound, AdS/CFT) but is not a standard assumption in QFT.

**What breaks if you drop it:** Without A0, you cannot define the state of a region. The theory has no starting point.

### A1: Refinability (Finite Continuum Limit)

**Statement:** Physics must be independent of the lattice spacing $a$ used to discretize spacetime. As $a \to 0$, physical observables must *converge* to finite values:

$$
\lim_{a \to 0} \langle O \rangle_a = \text{finite}
$$

where $\langle O \rangle_a$ is the expectation value of observable $O$ on a lattice with spacing $a$.

More precisely: if you partition a region $R$ into subregions $\{R_i\}$, the global state $\rho_R$ must be recoverable (via some trace operation) from the states $\{\rho_{R_i}\}$ on the subregions. As you refine the partition (make the subregions smaller), the recovered global state must converge.

**Why it's necessary:** If observables diverge as $a \to 0$, then physics depends on the arbitrary choice of cutoff. You never reach a continuum theory — you just have an infinite family of lattice theories with no consistent limit. The world does not come with a built-in lattice; if a lattice is needed to regulate the theory, then the limit $a \to 0$ must exist and be finite.

**Evidence tier:** **[FRAMEWORK]**. This is the requirement that QFT have a well-defined continuum limit. In renormalizable QFT, *differences* of energies converge (because you tune counterterms), but the *absolute* energy density diverges. A1 demands that *all* physical observables — including energy density $\rho$, pressure $p$, and particle number density $n$ — converge to finite values. This is a stronger requirement than renormalizability.

**What breaks if you drop it:** Without A1, the continuum limit does not exist. Physics depends on how finely you discretize space, and there is no objective answer to "What is the energy density of the vacuum?" The theory is not predictive.

**Connection to the vacuum energy problem:** The mode vacuum $|0\rangle_{\text{mode}}$ *fails* A1. Its energy density diverges as:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \cdot \left(\frac{\pi}{a}\right)^4 \cdot [1 + O(ma)]
$$

As $a \to 0$, $\rho \to \infty$. This is not a failure of quantum mechanics — it is a failure of the mode vacuum to satisfy A1. The axiomatic framework proposes that the physical vacuum must be a *different* state, one for which $\lim_{a \to 0} \rho_a$ is finite.

### F: Finiteness

**Statement:** All physical observables — energy density $\rho$, pressure $p$, particle number density $n$, and entanglement entropy $S$ — are finite *without regularization or renormalization*.

$$
\rho < \infty, \quad p < \infty, \quad n < \infty, \quad S < \infty
$$

**Why it's necessary:** Infinite observables are not measurable. A theory that predicts $\rho = \infty$ for the vacuum makes no contact with experiment. Renormalization "fixes" this by subtracting infinities, but subtraction is not explanation. F demands that the theory produce finite values *before* any subtractions are performed.

**Evidence tier:** **[FRAMEWORK]**. In standard QFT, you accept that bare quantities diverge and declare that only renormalized (difference) quantities are physical. F rejects this: it demands that the vacuum state itself have finite energy density, not merely that energy *differences* be finite. This is a philosophical shift — from "infinities are acceptable as long as they cancel" to "infinities indicate the wrong vacuum state."

**What breaks if you drop it:** Without F, you must distinguish between "bare" quantities (infinite) and "physical" quantities (finite differences). This works pragmatically but is conceptually unsatisfying. The vacuum has infinite energy density, which you then subtract away by fiat. F proposes that the right vacuum has finite energy density from the start, with no subtraction needed.

**Connection to the vacuum energy problem:** The mode vacuum has $\rho_{\text{mode}} \to \infty$, violating F. The coherent vacuum (constructed in later lessons) has finite $\rho$ for all lattice spacings $a$, satisfying F.

---

## 3.3 Summary: The Seven Axioms

| Axiom | Name | Statement | Tier |
|-------|------|-----------|------|
| **P** | Propagator Composition | $U(t_2, t_0) = U(t_2, t_1) \cdot U(t_1, t_0)$ | [ESTABLISHED] |
| **Q** | Unitarity | $U^\dagger U = I$ | [ESTABLISHED] |
| **M'** | Measurement Consistency | $\sum_i P(a_i) = 1$; Born rule applies | [ESTABLISHED] |
| **L** | Locality | $[\hat{O}_A, \hat{O}_B] = 0$ for spacelike-separated $A$, $B$ | [ESTABLISHED] |
| **A0** | Existence | Bounded region $R$ gets finite-dimensional $H_R$ | [FRAMEWORK] |
| **A1** | Refinability | $\lim_{a \to 0} \langle O \rangle_a$ is finite | [FRAMEWORK] |
| **F** | Finiteness | $\rho, p, n, S < \infty$ without renormalization | [FRAMEWORK] |

The first four axioms are the non-negotiable core of quantum mechanics. Violate any of them and you lose the structure of the theory (P, Q, M') or causality (L).

The last three axioms are the proposed extensions. They encode the requirement that the theory produce finite, measurable predictions for all observables. The mode vacuum satisfies P, Q, M', L, and arguably A0, but *fails* A1 and F.

---

## 3.4 What Breaks When You Drop an Axiom

Let's make this concrete. For each axiom, what happens if you remove it?

### Drop P: Time Evolution Is Inconsistent

If $U(t_2, t_0) \neq U(t_2, t_1) \cdot U(t_1, t_0)$, then the state at time $t_2$ depends on whether you evolved directly from $t_0$, or stopped at an intermediate time $t_1$. This is physically absurd: the system does not "know" whether you mentally divided the time interval into pieces. Without P, there is no notion of a unique future state. Dynamics is undefined.

### Drop Q: Probability Is Not Conserved

If $U^\dagger U \neq I$, then $\langle \psi | \psi \rangle$ changes over time. The norm of the state is not preserved. Born rule probabilities $|\langle a_i | \psi \rangle|^2$ do not sum to 1. You lose the probabilistic interpretation of quantum mechanics. Information is created or destroyed.

### Drop M': Measurement Doesn't Work

If the Born rule does not apply, or if probabilities do not sum to 1, or if post-measurement states are not normalizable, then measurement is not a consistent operation. You cannot connect theory to experiment. Quantum mechanics loses its empirical content.

### Drop L: Faster-Than-Light Signaling

If operations in region $A$ affect statistics in spacelike-separated region $B$, you can send signals instantaneously. Alice performs a measurement in $A$, and Bob sees the effect in $B$ before a light signal could travel from $A$ to $B$. This violates relativity. It also leads to causal paradoxes in the presence of closed timelike curves.

### Drop A0: No State to Describe

If regions do not have associated Hilbert spaces and density matrices, you cannot write down a quantum state. There is nothing to apply operators to. The theory has no starting point.

### Drop A1: No Continuum Limit

If observables diverge as $a \to 0$, there is no continuum theory. Physics depends on the arbitrary cutoff $a$. You have a family of lattice theories indexed by $a$, but no limit as $a \to 0$. The world does not have a built-in lattice, so this is a failure of the theory to describe reality.

This is the situation with the mode vacuum: $\rho_{\text{mode}}(a) \sim a^{-4}$ diverges. The mode vacuum does not satisfy A1.

### Drop F: Infinite Observables

If energy density, pressure, or particle number are infinite, the theory predicts unmeasurable quantities. You must introduce renormalization — subtract the infinity and work only with differences. This works pragmatically but is conceptually unsatisfying. F demands that the vacuum have finite observables *before* subtraction.

---

## 3.5 The Axioms in Action: Constraining Vacuum States

A vacuum state $|\Omega\rangle$ is a candidate for the physical ground state of a quantum field. The seven axioms impose constraints on what vacua are acceptable.

### Constraint 1: Must Be a State (A0)

$|\Omega\rangle$ must be a normalizable element of the Hilbert space. Obvious, but non-trivial in infinite-dimensional spaces.

### Constraint 2: Must Evolve Unitarily (P, Q)

$|\Omega\rangle(t) = U(t, 0)|\Omega\rangle(0)$ must satisfy propagator composition and unitarity. If $|\Omega\rangle$ is the ground state of a time-independent Hamiltonian, this is automatic: $U(t, 0) = e^{-iHt/\hbar}$.

### Constraint 3: Must Give Valid Measurement Outcomes (M')

All observables $\hat{O}$ must have finite expectation values $\langle \Omega | \hat{O} | \Omega \rangle$, and the Born rule must yield probabilities summing to 1. This rules out states with pathological measurement properties.

### Constraint 4: Must Respect Locality (L)

$|\Omega\rangle$ can be entangled (and typically is), but operations on region $A$ must not affect statistics on spacelike-separated region $B$. The reduced density matrix $\rho_A = \text{Tr}_B(|\Omega\rangle\langle\Omega|)$ must be locally well-defined.

### Constraint 5: Must Refine Consistently (A1)

As you partition space into finer regions, the state must converge. Observables like $\rho$, $p$, $n$ must have limits as $a \to 0$, and those limits must be finite.

The mode vacuum *fails* this constraint. As $a \to 0$:

$$
\rho_{\text{mode}}(a) = \frac{\hbar c}{16\pi^2} \cdot \left(\frac{\pi}{a}\right)^4 \to \infty
$$

No amount of refinement brings the energy density to a finite value. The mode vacuum does not have a well-defined continuum limit.

### Constraint 6: Must Have Finite Observables (F)

$\langle \Omega | \rho | \Omega \rangle < \infty$, $\langle \Omega | p | \Omega \rangle < \infty$, $\langle \Omega | n | \Omega \rangle < \infty$. The vacuum must produce measurable predictions without subtracting infinities.

Again, the mode vacuum fails: $\rho_{\text{mode}} \to \infty$.

---

## 3.6 Why A1 Is the Key

Of the seven axioms, A1 (Refinability) is the one that distinguishes the axiomatic framework from standard QFT. Let me explain why it is central.

**Standard QFT accepts divergent bare quantities.** You compute the energy density of the mode vacuum, get $\rho \sim \Lambda^4$, and say: "That's fine, we'll subtract it away. Only energy *differences* are physical." This is the renormalization program. It works spectacularly well for computing scattering amplitudes and particle interactions, but it leaves the vacuum energy undefined.

**A1 rejects this.** It says: no, the energy density of the vacuum *must* be finite, without subtraction. If your chosen vacuum state gives $\rho \to \infty$ as $a \to 0$, then you have chosen the wrong vacuum. There exists a different state — one that satisfies all seven axioms, including A1 — and *that* is the physical vacuum.

A1 is not an arbitrary demand. It is the requirement that the continuum limit exist. If physics depends on the cutoff $a$, then you do not have a theory of continuous spacetime — you have a theory of discrete lattices, with no limiting behavior as the lattice is refined. The real world does not have a visible lattice, so if a lattice is introduced as a regularization tool, the limit $a \to 0$ must be well-defined.

**The mode vacuum fails A1.** This is not controversial — it is a proven mathematical fact. The energy density diverges quartically with the cutoff. Renormalization hides this divergence but does not eliminate it.

**The coherent vacuum satisfies A1.** As we will show in later lessons, there exists a vacuum state constructed from coherent states of the field modes, for which:

$$
\lim_{a \to 0} \rho_{\text{coherent}}(a) = \text{finite}
$$

This state satisfies all seven axioms. That is the central claim of the axiomatic framework.

---

## 3.7 A1 and the Cosmological Constant Problem

The cosmological constant problem is often stated as: "Why is the observed vacuum energy density $\rho_{\text{obs}} \approx 6 \times 10^{-10}$ J/m$^3$ so much smaller than the predicted value $\rho_{\text{QFT}} \sim 10^{113}$ J/m$^3$?"

But this framing assumes that $\rho_{\text{QFT}}$ *is* the prediction of quantum field theory. It is not. It is the prediction of quantum field theory *with the mode vacuum*. If the mode vacuum violates axiom A1, then it is not the physical vacuum, and its energy density is not the physical prediction.

The axiomatic framework reframes the cosmological constant problem as:

**"What is the physical vacuum state — the state satisfying all seven axioms — and what is its energy density?"**

This is a well-posed question. The answer (to be derived in later lessons) is:

$$
\rho_{\text{coherent}} = \frac{\hbar c}{16\pi^2 a^4} \cdot f(ma)
$$

where $f(ma)$ is a function that goes to zero as $ma \to 0$ (the massless limit) and to a finite constant as $ma \to \infty$ (the lattice-spacing limit). The key point: $\rho_{\text{coherent}}$ is finite for any fixed $a > 0$, and the $a \to 0$ limit *exists*.

Whether this finite value matches $\rho_{\text{obs}}$ is a separate question (addressed in later lessons). The first step is establishing that a finite, A1-satisfying vacuum exists.

---

## 3.8 Summary of Key Results

| Concept | Result | Tier |
|---------|--------|------|
| Time evolution composes | $U(t_2, t_0) = U(t_2, t_1) \cdot U(t_1, t_0)$ | [ESTABLISHED] |
| Unitarity preserved | $U^\dagger U = I$ | [ESTABLISHED] |
| Born rule applies | $\sum_i P(a_i) = 1$ | [ESTABLISHED] |
| Locality respected | $[\hat{O}_A, \hat{O}_B] = 0$ for spacelike $A$, $B$ | [ESTABLISHED] |
| Finite local state space | Bounded $R$ gets finite-dimensional $H_R$ | [FRAMEWORK] |
| Continuum limit exists | $\lim_{a \to 0} \langle O \rangle_a$ finite | [FRAMEWORK] |
| Observables finite | $\rho, p, n < \infty$ without subtraction | [FRAMEWORK] |
| Mode vacuum fails A1 | $\rho_{\text{mode}}(a) \sim a^{-4} \to \infty$ | [PROVEN] |
| Coherent vacuum satisfies A1 | $\lim_{a \to 0} \rho_{\text{coherent}}(a)$ finite | [PREDICTED] |

---

## 3.9 Looking Ahead

We now have the axioms. The next step is to see *why* the mode vacuum — the ground state of standard QFT — fails axioms A1 and F. Lesson 4 will construct the mode vacuum explicitly, compute its energy density, and demonstrate the $a^{-4}$ divergence. We will also see why the mode vacuum is Lorentz-invariant and maximally entangled — properties that make it mathematically elegant but physically problematic.

Then, in Lesson 5, we will construct the coherent vacuum — a state built from coherent states of the field modes, analogous to the special coherent state $|\alpha = 1/\sqrt{2}\rangle$ from Lesson 2. We will show that this state satisfies all seven axioms, including A1 and F, and that its energy density is finite.

The axioms are the rules of the game. The mode vacuum breaks them. The coherent vacuum obeys them. That is the core of the axiomatic framework.
