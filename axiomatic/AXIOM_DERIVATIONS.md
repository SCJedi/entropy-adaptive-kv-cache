# Can the Seven Axioms Be Derived?

## The Question

For each of the seven axioms (A0, A1, P, Q, M', L, F), we ask:
- Can it be **derived** from something more fundamental?
- Can it be **proven** mathematically?
- Is it **forced** by elimination of alternatives?
- Or is it an **irreducible assumption**?

---

## Axiom Q: Unitarity

**Statement**: Time evolution preserves inner products. U†U = I.

### Status: DERIVABLE from probability conservation

**Proof**:

1. Assume probabilities must sum to 1 at all times (this is what "probability" means)
2. The probability of outcome i is P_i = |⟨i|ψ⟩|²
3. Total probability: Σᵢ P_i = Σᵢ |⟨i|ψ⟩|² = ⟨ψ|ψ⟩ = 1 (normalization)
4. After time evolution |ψ⟩ → U|ψ⟩, we need ⟨ψ|U†U|ψ⟩ = 1 for all |ψ⟩
5. This requires U†U = I

**Conclusion**: Q is derivable from "probabilities sum to 1" — which is definitional for probability theory.

**Can you deny Q?** Only by abandoning probability as a concept. Non-unitary evolution means probability isn't conserved, which means you're not doing probability theory anymore.

**Derivation strength**: FORCED by the definition of probability.

---

## Axiom P: Propagator Composition

**Statement**: U(t₂,t₀) = U(t₂,t₁)·U(t₁,t₀)

### Status: DERIVABLE from the definition of time evolution

**Proof**:

1. U(t,t₀) is defined as "the operator that evolves states from t₀ to t"
2. Evolving from t₀ to t₂ via t₁ means: first evolve to t₁, then evolve to t₂
3. In equations: |ψ(t₂)⟩ = U(t₂,t₁)|ψ(t₁)⟩ = U(t₂,t₁)U(t₁,t₀)|ψ(t₀)⟩
4. But also: |ψ(t₂)⟩ = U(t₂,t₀)|ψ(t₀)⟩
5. Therefore: U(t₂,t₀) = U(t₂,t₁)U(t₁,t₀)

**Conclusion**: P is derivable from "time evolution means evolving through intermediate times."

**Can you deny P?** Only if the result depends on how you subdivide the time interval — which would mean time evolution isn't well-defined.

**Derivation strength**: FORCED by the definition of deterministic time evolution.

---

## Axiom M': Measurement Consistency

**Statement**: Born rule probabilities sum to 1; post-measurement states are valid states.

### Status: PARTIALLY DERIVABLE, partially definitional

**The Born Rule itself**: P(i) = |⟨i|ψ⟩|²

This is NOT derivable from pure mathematics. It's the bridge between the mathematical formalism (Hilbert space) and empirical reality (measurement outcomes).

Gleason's theorem comes close: IF you demand that probabilities depend only on the state and the projector, and are non-contextual, THEN the only consistent assignment is the Born rule.

**Gleason's Theorem** (1957):

For Hilbert space dimension ≥ 3, if a function μ assigns probabilities to subspaces such that:
- μ(H) = 1 (total probability is 1)
- μ(⊕ᵢ Hᵢ) = Σᵢ μ(Hᵢ) for orthogonal subspaces

Then there exists a density matrix ρ such that μ(P) = Tr(ρP) for all projectors P.

**What Gleason proves**: The FORM of the Born rule (trace of ρ times projector) is the unique probability assignment satisfying basic consistency.

**What Gleason doesn't prove**: That measurement outcomes ARE probabilistic, or that this ρ EXISTS.

**Probabilities summing to 1**: This follows from ⟨ψ|ψ⟩ = 1 and completeness of the basis:
$$\sum_i P(i) = \sum_i |\langle i|\psi\rangle|^2 = \sum_i \langle\psi|i\rangle\langle i|\psi\rangle = \langle\psi|\left(\sum_i |i\rangle\langle i|\right)|\psi\rangle = \langle\psi|\psi\rangle = 1$$

**Post-measurement states being valid**: If |i⟩ is an eigenstate, it's already in the Hilbert space. This is definitional.

**Derivation strength**:
- Probabilities sum to 1: FORCED by completeness + normalization
- Born rule form: FORCED by Gleason's theorem (given non-contextuality)
- Born rule existence: IRREDUCIBLE ASSUMPTION (the measurement postulate)

---

## Axiom L: Locality / No-Signaling

**Statement**: Operations on region A don't affect measurement statistics on spacelike-separated region B.

### Status: DERIVABLE from special relativity + causality

**Proof sketch**:

1. Special relativity: no information travels faster than light
2. If Alice's operation on A changed Bob's statistics on B (spacelike separated), Bob could detect this
3. This would allow faster-than-light signaling
4. Contradiction with (1)
5. Therefore: operations on A cannot change statistics on B

**More formally** (in quantum mechanics):

For a product state ρ_AB = ρ_A ⊗ ρ_B:
- Any operation on A: ρ_A → ρ'_A
- State on B: Tr_A(ρ'_A ⊗ ρ_B) = ρ_B (unchanged)

For an entangled state, the no-signaling theorem proves:
$$\text{Tr}_A\left[(O_A \otimes I_B)\rho_{AB}(O_A^\dagger \otimes I_B)\right] = \text{Tr}_A(\rho_{AB}) = \rho_B$$

Alice's operation (any O_A) leaves Bob's reduced state unchanged.

**Can you deny L?** Only by allowing faster-than-light signaling, which contradicts special relativity and leads to causal paradoxes.

**Derivation strength**: FORCED by special relativity + causality.

---

## Axiom A0: Existence

**Statement**: Every bounded region R has a Hilbert space H_R and a density matrix ρ_R.

### Status: PARTIALLY DEFINITIONAL, partially forced

**The Hilbert space structure**: This is essentially the definition of "quantum theory." A theory with states, superposition, and probabilities naturally leads to Hilbert space (via the C*-algebra → GNS construction).

**Why Hilbert space?**

1. States should form a vector space (superposition principle)
2. Probabilities require a norm (|ψ|² = probability)
3. Observables should have real eigenvalues (Hermitian operators)
4. Completeness is needed for limits to exist

These requirements force Hilbert space structure. This is not so much "derived" as "what quantum theory means."

**Finite-dimensional?** This is the strong form. Standard QFT uses infinite-dimensional Fock space. The finite-dimensional requirement is an ADDITIONAL assumption motivated by:
- Wanting A1 (refinability) to be satisfiable
- Bekenstein bound (finite entropy in finite region)
- Quantum gravity intuitions (finite degrees of freedom in finite volume)

**Derivation strength**:
- Hilbert space structure: DEFINITIONAL (what "quantum" means)
- Density matrices exist: FORCED by mixed states being possible
- Finite-dimensional: ADDITIONAL ASSUMPTION (motivated but not forced)

---

## Axiom A1: Refinability

**Statement**: As lattice spacing a → 0, physical observables converge (not diverge).

### Status: NOT DERIVABLE — this is a substantive physical claim

**Why A1 is NOT forced by logic**:

You could imagine a universe where physics depends on your lattice choice. The answer for ⟨T₀₀⟩ could legitimately depend on how fine your grid is. This isn't logically contradictory.

**Why A1 is physically motivated**:

1. **Operational argument**: If your predictions depend on arbitrary discretization choices, you're not predicting physics — you're predicting computational artifacts.

2. **Empirical argument**: All successful physics theories have continuum limits. Classical mechanics, electromagnetism, general relativity, thermodynamics — all work in the continuum.

3. **Computability argument**: If refining your lattice changes your answer by a factor of 10,000, you can never trust any computation.

**Why A1 might fail**:

If physics has a fundamental discreteness (Planck scale, string length), then refinement below that scale is meaningless. A1 would fail not because the theory is wrong, but because the question is ill-posed.

**The cell vacuum's relationship to A1**:

The cell vacuum satisfies A1 with a NATURAL CUTOFF at the Compton wavelength. Refinement below λ_C doesn't add new physics — it's already at the fundamental scale. So A1 is satisfied trivially: the observable IS constant under refinement.

**Derivation strength**:
- NOT DERIVABLE from pure logic
- MOTIVATED by operational, empirical, and computability considerations
- Could be VIOLATED if physics has fundamental discreteness
- SATISFIED TRIVIALLY if there's a natural cutoff (as in cell vacuum)

---

## Axiom F: Finiteness

**Statement**: Physical observables are finite without regularization or renormalization.

### Status: NOT DERIVABLE — this is the key choice point

**Why F is NOT forced by logic**:

Renormalization shows you can extract finite predictions from formally infinite theories. The Standard Model predicts g-2 to 12 decimal places despite having divergent integrals. So F-strong is not REQUIRED for empirical success.

**Why F is physically motivated**:

1. **Naive expectation**: A physical theory should output numbers, not "infinity" or "depends on cutoff."

2. **Gravity requires F-strong**: Einstein's equations need finite T_μν. You can't feed infinity to the right-hand side.

3. **Conceptual cleanliness**: If every prediction requires subtracting infinity, the theory doesn't stand on its own.

**Why F might be too strong**:

1. **Renormalization works**: For particle physics, F-weak suffices. All predictions are differences.

2. **Absolute vacuum energy might be unobservable**: If only differences matter, F-strong is unnecessary.

3. **Many successful theories violate F-strong**: The Standard Model, QED, QCD all have divergent vacuum energies.

**The key insight**:

F is not derivable because it's a CHOICE about what "prediction" means:
- If "prediction" means "finite number for absolute quantities" → F-strong required
- If "prediction" means "finite number for differences" → F-weak suffices

**Derivation strength**:
- NOT DERIVABLE from pure logic
- NOT DERIVABLE from empirical success (renormalization shows F-weak suffices for particle physics)
- REQUIRED by gravity (F-strong needed for Einstein equations)
- A CHOICE POINT in foundations of QFT

---

## Summary Table

| Axiom | Can it be derived? | From what? | Strength |
|-------|-------------------|------------|----------|
| **Q** (Unitarity) | YES | Probability conservation | FORCED |
| **P** (Propagator) | YES | Definition of time evolution | FORCED |
| **M'** (Measurement) | PARTIALLY | Gleason's theorem + completeness | Born rule existence is IRREDUCIBLE |
| **L** (Locality) | YES | Special relativity + causality | FORCED |
| **A0** (Existence) | PARTIALLY | Definition of quantum theory | Finite-dim is ADDITIONAL |
| **A1** (Refinability) | NO | — | MOTIVATED but not forced |
| **F** (Finiteness) | NO | — | CHOICE POINT |

---

## The Hierarchy of Justification

**Tier 1: Derivable / Forced**
- Q, P, L: These follow from basic definitions and special relativity
- Denying them leads to immediate contradictions (probability not conserved, FTL signaling, time evolution inconsistent)

**Tier 2: Partially Derivable**
- M': Gleason's theorem forces the FORM, but the existence of measurement is assumed
- A0: Hilbert space is definitional, but finite-dimensionality is an additional assumption

**Tier 3: Motivated but Not Forced**
- A1: Refinability is operationally motivated but could fail if physics is discrete
- F: Finiteness is conceptually clean but empirically unnecessary for particle physics

---

## The Deep Question

Why do we have SEVEN axioms and not fewer?

**Could we derive some from others?**

- Q from P? No. Propagator composition doesn't imply unitarity. You could have consistent non-unitary evolution.
- P from Q? No. Unitarity doesn't imply composition. You need both independently.
- L from Q? No. Unitarity is about probability conservation, not spatial locality.
- A1 from F? Almost — if F-strong holds, A1 is easier to satisfy. But they're logically independent.
- F from A1? No. You could have convergent but infinite limits.

**The irreducible core**:

After all derivations, we're left with:
1. The measurement postulate (that quantum mechanics connects to experiment)
2. A choice about finiteness (F-strong vs F-weak)
3. A choice about discreteness (is there a fundamental scale?)

These are the genuine choice points. Everything else follows.

---

## What This Means for the Framework

**The strong axioms (Q, P, L, M')**: These are essentially forced. Any theory we'd call "quantum mechanics" satisfies them. The mode vacuum and cell vacuum both pass these.

**The choice axioms (A0-strong, A1, F)**: These are where we have freedom. The Alpha Framework CHOOSES to include them, which selects the cell vacuum.

**The alternative**: You could weaken A1 and F to allow the mode vacuum. This is what standard QFT does (implicitly). The cost is:
- You can only answer F-weak questions
- You need renormalization for every calculation
- Gravity becomes problematic

**The tradeoff is now explicit**:

| Choice | A1/F Status | Vacuum Selected | What You Get | What You Lose |
|--------|-------------|-----------------|--------------|---------------|
| Include A1+F | Required | Cell vacuum | F-strong answers, no renormalization needed | Lorentz invariance below λ_C |
| Weaken A1+F | Optional | Mode vacuum | Lorentz invariance | F-strong answers, need renormalization |

Neither choice is "right" or "wrong." They're different tools for different questions.

---

## Conclusion

**Derivable (no choice)**:
- Q: from probability conservation
- P: from definition of time evolution
- L: from special relativity

**Partially derivable**:
- M': Gleason gives form, existence is assumed
- A0: Hilbert space is definitional, finite-dim is extra

**Not derivable (genuine choices)**:
- A1: motivated by operationalism, not forced
- F: the key fork in the road

The Alpha Framework makes a CHOICE to include A1 and F. This choice is defensible, motivated, and has clear consequences. But it IS a choice, not a derivation.

The value of the framework is making this choice EXPLICIT rather than hiding it in technical definitions.
