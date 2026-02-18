# Primer: Mathematical Rigor -- The AQFT Construction

## The Big Idea

The cell vacuum is not a handwave or a heuristic. It has been rigorously constructed within algebraic quantum field theory (AQFT), the most mathematically precise formulation of QFT. The construction proves that the cell vacuum is a legitimate quantum state, that it has well-defined energy density, and that it lives in a fundamentally different sector of the theory from the standard mode vacuum. These are the strongest results in the Two Vacua Theory -- proven mathematics, not speculative physics.

But a crucial distinction applies: AQFT is *hospitable* to the cell vacuum, not *generative*. The framework accepts the cell vacuum as valid. It does not tell us that nature chose it.

## What Is AQFT?

Algebraic quantum field theory flips the usual construction. Instead of starting with a Hilbert space and building operators, AQFT starts with an abstract algebra of observables (the Weyl algebra) and treats quantum states as mathematical functionals on this algebra. A state $\omega$ assigns an expectation value $\omega(A)$ to each observable $A$.

The advantage: different states can produce different, unitarily inequivalent Hilbert space representations of the same algebra. In ordinary quantum mechanics with finitely many degrees of freedom, this cannot happen (the Stone-von Neumann theorem guarantees uniqueness). But quantum field theory has infinitely many degrees of freedom, and inequivalent representations are a fundamental feature, not a pathology. **[PROVEN]**

## Four Key Results

### 1. The cell vacuum is a legitimate state

The cell vacuum defines a positive, normalized linear functional on the Weyl algebra. In finite volume, this is straightforward. In infinite volume, it requires the theory of infinite tensor products, but the construction converges because the displacement parameters are uniformly bounded. **[PROVEN]**

### 2. Reeh-Schlieder does not block it

The Reeh-Schlieder theorem says that any state satisfying the spectrum condition (energy-momentum in the forward light cone) must be entangled across all spatial regions. The cell vacuum is a product state with zero entanglement. Contradiction?

No. The cell vacuum violates the spectrum condition -- it has definite spatial structure and is not Poincare-invariant. Since the theorem's hypothesis fails, the theorem does not apply. The cell vacuum is free to be unentangled.

This is not exotic. Thermal states (the most physically important non-vacuum states in QFT) violate the spectrum condition in exactly the same way. The cell vacuum is in good company. **[PROVEN]**

### 3. Unitary inequivalence

The mode vacuum $|0\rangle$ and the cell vacuum $|\Omega\rangle$ are unitarily inequivalent: no unitary transformation connects them. The Shale-Stinespring theorem provides the criterion: the norm of the displacement $\|\alpha\|^2 = N/2$ diverges as the number of cells $N \to \infty$, violating the Hilbert-Schmidt condition.

Physically, this means the two states live in different superselection sectors. You cannot continuously deform one into the other. They inhabit genuinely different Hilbert spaces. **[PROVEN]**

### 4. Hadamard condition satisfied

For a state to have a well-defined renormalized stress-energy tensor, its short-distance singularity structure must match the standard form (the Hadamard condition). The cell vacuum's two-point function is:

$$W_\Omega = W_0 + F \cdot F$$

where $W_0$ is the mode vacuum two-point function (Hadamard by construction) and $F$ is a smooth function (the field expectation value in the cell vacuum). Since $F \cdot F$ adds no singularity, the Hadamard condition is preserved. **[PROVEN]**

This means the standard renormalization machinery works for the cell vacuum. The energy density $\langle T_{\mu\nu} \rangle_{\text{ren}}$ is well-defined.

## Hospitable, Not Generative

This distinction is the single most important conceptual point of this lesson.

AQFT proves that the cell vacuum *exists* as a mathematically legitimate state. It does not prove that nature *chose* this state. The algebra of observables admits many states -- infinitely many, in fact. The cell vacuum is one of them. AQFT cannot tell you which one is physically realized. That requires experiment.

**[FRAMEWORK]** for the physical identification; **[PROVEN]** for the mathematical existence.

## Key Takeaways

1. **Mathematical legitimacy is established.** The cell vacuum passes every test AQFT demands: well-defined state, Hadamard, renormalized stress-energy.

2. **It lives in a different world from the mode vacuum.** Unitary inequivalence means these are genuinely distinct states in different superselection sectors.

3. **The Reeh-Schlieder evasion is standard.** Same mechanism as thermal states -- physically reasonable, not pathological.

4. **AQFT accepts but does not select.** It proves existence, not physical relevance. The cell vacuum is valid; it is not uniquely preferred.

5. **These results survive regardless.** Even if the numerical predictions from Lesson 6 fail, the AQFT construction remains proven mathematics.

## What Comes Next

Lesson 8 explores the orthogonality of the two vacua: $\langle 0 | \Omega \rangle = e^{-N/4} \to 0$ as the number of cells grows, placing them in different superselection sectors. The curved spacetime results ($10^{-69}$ self-consistency) build toward the dramatic reversal in Lesson 9.
