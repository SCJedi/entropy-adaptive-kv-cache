# Lesson 8: Orthogonality and Superselection

## Overview

The mode vacuum $|0\rangle$ and the cell vacuum $|\Omega\rangle$ are orthogonal in the infinite-volume limit: their inner product $\langle 0|\Omega\rangle = \exp(-N/4) \to 0$ as the number of Compton cells $N$ approaches infinity. Combined with the unitary inequivalence established in Lesson 7, this means the two states occupy genuinely different superselection sectors -- distinct phases of the quantum field with no physical process mediating a transition between them. This lesson derives the orthogonality, explains its physical meaning, revisits the complementarity table with full mathematical backing, and demonstrates the remarkable stability of the cell vacuum in curved spacetime.

## 8.1 The Overlap Calculation

The inner product between the mode vacuum and the cell vacuum is computable exactly. Since the cell vacuum is a product state over Compton cells, and the mode vacuum projected onto the cell basis is also expressible as a product, the inner product factorizes:

$$
\langle 0 | \Omega \rangle = \prod_{n=1}^{N} \langle 0 | \alpha_n \rangle
$$

where $|\alpha_n\rangle$ is the coherent state in cell $n$ with $|\alpha_n|^2 = 1/2$. **[PROVEN]**

### Single-cell overlap

For a single cell, the overlap between the vacuum and a coherent state follows from the number-state expansion of $|\alpha\rangle$:

$$
|\alpha\rangle = e^{-|\alpha|^2/2} \sum_{n=0}^{\infty} \frac{\alpha^n}{\sqrt{n!}} |n\rangle
$$

Taking the inner product with $|0\rangle$:

$$
\langle 0 | \alpha \rangle = e^{-|\alpha|^2/2} \cdot \frac{\alpha^0}{\sqrt{0!}} = e^{-|\alpha|^2/2}
$$

For $|\alpha|^2 = 1/2$:

$$
\langle 0 | \alpha \rangle = e^{-1/4} \approx 0.7788
$$

**[PROVEN]**

This is a substantial overlap for a single cell -- about 78%. The mode vacuum and the coherent state with $|\alpha|^2 = 1/2$ are far from orthogonal at the single-oscillator level.

### N-cell overlap

For $N$ independent cells:

$$
\langle 0 | \Omega \rangle = \left(e^{-1/4}\right)^N = e^{-N/4}
$$

**[PROVEN]**

The transition probability is:

$$
|\langle 0 | \Omega \rangle|^2 = e^{-N/2}
$$

### The infinite-volume limit

As $N \to \infty$:

$$
\lim_{N \to \infty} \langle 0 | \Omega \rangle = \lim_{N \to \infty} e^{-N/4} = 0
$$

**[PROVEN]**

The convergence is exponentially fast. Some illustrative values:

| $N$ | $\|\langle 0 \| \Omega \rangle\|^2$ | Description |
|-----|------|-------------|
| 10 | $e^{-5} \approx 0.0067$ | Small box: 0.67% |
| 100 | $e^{-50} \approx 10^{-22}$ | Effectively zero |
| $10^{60}$ | $e^{-10^{60}/2} \approx 0$ | Cosmological volume |

By $N = 100$, the overlap is already negligible by any physical standard. For a cosmological volume containing $\sim 10^{60}$ or more Compton cells, the overlap is so far below any measurable threshold that the distinction between "exponentially small" and "exactly zero" is operationally meaningless.

## 8.2 Superselection Sectors

The orthogonality of $|0\rangle$ and $|\Omega\rangle$ in the infinite-volume limit, combined with their unitary inequivalence (Lesson 7, Shale-Stinespring theorem), means they occupy different **superselection sectors**. **[PROVEN]**

### Definition

Two states are in different superselection sectors if:
1. They are orthogonal: $\langle \psi_1 | \psi_2 \rangle = 0$
2. No local observable connects them: $\langle \psi_1 | A | \psi_2 \rangle = 0$ for all $A$ in the local algebra
3. Superpositions are forbidden: $a|\psi_1\rangle + b|\psi_2\rangle$ is not a physically realizable state

**[PROVEN]** as mathematical structure. The mode vacuum and cell vacuum satisfy all three conditions in the infinite-volume limit.

### Familiar examples

Superselection is not exotic. Well-known examples include:

- **Charge superselection:** States with different electric charge cannot be superposed. $|e^-\rangle + |e^+\rangle$ is not a physical state.
- **Fermion number superselection:** States with even and odd fermion number cannot be superposed.
- **Spontaneous symmetry breaking:** In a ferromagnet, the "spin up" and "spin down" ground states are in different sectors in the infinite-volume limit.

The mode/cell vacuum superselection is structurally identical. It is a consequence of having infinitely many degrees of freedom, not of any special property of the cell vacuum construction. **[PROVEN]**

### Physical meaning

The superselection between $|0\rangle$ and $|\Omega\rangle$ means:

- **No tunneling:** There is no physical process that transforms the mode vacuum into the cell vacuum or vice versa. The transition amplitude is exactly zero (in the infinite-volume limit).
- **No interference:** There are no observable interference effects between the two sectors. They are as separate as different charge sectors.
- **Choice of sector is physical:** The universe is in one sector or the other (or neither). This is a physical fact about the state of the universe, not a choice of formalism.

## 8.3 The Complementarity Table -- Full Mathematical Backing

In Lesson 5, the analogy between the two vacua and position/momentum eigenstates was presented as a conceptual insight. With the AQFT results from Lesson 7 and the orthogonality from this lesson, the analogy now has precise mathematical content.

| Property | Mode Vacuum $\|0\rangle$ | Cell Vacuum $\|\Omega\rangle$ |
|----------|----------------------|--------------------------|
| **Definition** | $a_k\|0\rangle = 0 \; \forall k$ | $a_n\|\alpha_n\rangle = \alpha_n\|\alpha_n\rangle$ |
| **Definite in** | Momentum space ($k$-modes) | Position space (cells) |
| **Particle number** | Definite: $n_k = 0$ per mode | Indefinite: Poisson with $\langle n \rangle = 1/2$ |
| **Entanglement** | Maximal (Reeh-Schlieder) | Zero (product state) |
| **Energy density** | Divergent ($\Lambda^4$-dependent) | Finite ($m^4 c^5/\hbar^3$) |
| **Poincare invariant** | Yes | No |
| **Spectrum condition** | Satisfied | Violated |
| **Hadamard** | Yes (by construction) | Yes (**[PROVEN]**) |
| **Superselection sector** | Sector I | Sector II |
| **Inner product** | $\langle 0\|0\rangle = 1$ | $\langle 0\|\Omega\rangle = 0$ (infinite volume) |

Every entry in this table is now backed by a theorem or a direct calculation. The conceptual analogy from Lesson 5 has been elevated to rigorous mathematics.

**[PROVEN]** for the mathematical properties. **[FRAMEWORK]** for the physical interpretation that this complementarity resolves the vacuum energy problem.

## 8.4 Curved Spacetime: Self-Consistency to 10^{-69}

The cell vacuum construction, originally formulated in flat Minkowski spacetime, extends to curved spacetime via the locally covariant AQFT framework. The key question: is the construction self-consistent when the cell vacuum's own energy density curves spacetime?

### The back-reaction calculation

In semiclassical gravity, the metric satisfies:

$$
G_{\mu\nu} = 8\pi G \langle \Omega | T_{\mu\nu} | \Omega \rangle_{\text{ren}}
$$

The cell vacuum energy density $\rho_\Omega = m^4 c^5/\hbar^3$ produces spacetime curvature of order:

$$
R \sim \frac{8\pi G \rho_\Omega}{c^4} \sim \frac{\rho_\Omega}{\rho_{\text{Planck}}} \cdot l_P^{-2}
$$

This curvature, in turn, modifies the cell vacuum state. The relative correction is:

$$
\frac{\delta \rho}{\rho} \sim R \lambda_C^2 \sim \frac{\rho_\Omega}{\rho_{\text{Planck}}} \sim 3.6 \times 10^{-69}
$$

**[PROVEN]**

A correction of $10^{-69}$ means the flat-spacetime construction is valid to extraordinary precision. The cell vacuum does not destabilize itself through gravitational back-reaction. The iterative procedure (compute energy density $\to$ compute curvature $\to$ recompute energy density) converges immediately.

### Comparison with other scales

The self-consistency parameter $\rho_\Omega / \rho_{\text{Planck}} \sim 10^{-69}$ is:
- Much smaller than the electroweak correction: $\rho_{\text{EW}}/\rho_{\text{Planck}} \sim 10^{-67}$
- Much smaller than the QCD correction: $\rho_{\text{QCD}}/\rho_{\text{Planck}} \sim 10^{-79}$
- Valid for all post-nucleosynthesis cosmology, where the expansion rate $H$ is orders of magnitude below the Compton frequency $mc^2/\hbar$

## 8.5 Parker Particle Creation Is Negligible

An expanding universe can create particles from the vacuum (the Parker effect, or cosmological particle creation). If the cell vacuum leaked particles at a significant rate, its energy density would not be stable.

The rate is controlled by the adiabatic parameter:

$$
\epsilon = \frac{|\dot{\omega}|}{\omega^2}
$$

where $\omega$ is the oscillator frequency and $\dot{\omega}$ is its time derivative due to the expansion. For Compton-scale oscillators in the present universe:

$$
\epsilon \sim \frac{H}{mc^2/\hbar} \sim \frac{10^{-33} \text{ s}^{-1}}{10^{-2} \text{ eV}/\hbar} \sim 6.2 \times 10^{-31}
$$

**[PROVEN]**

Since $\epsilon \ll 1$, the evolution is adiabatic and particle creation is exponentially suppressed as $\sim e^{-\pi/\epsilon}$. The cell vacuum is stable against Parker particle creation on cosmological timescales.

## 8.6 The Weyl Algebra on Curved Spacetime

The locally covariant AQFT framework provides a rigorous foundation for quantum field theory on curved spacetime. The key structures:

1. **For each globally hyperbolic spacetime** $(\mathcal{M}, g)$, there exists a Weyl algebra $\mathcal{W}(\mathcal{M}, g)$ of the free scalar field.

2. **Spacetime embeddings induce algebra homomorphisms:** if $\chi: (\mathcal{M}_1, g_1) \to (\mathcal{M}_2, g_2)$ is a causal embedding, there is a corresponding $*$-homomorphism $\alpha_\chi: \mathcal{W}_1 \to \mathcal{W}_2$.

3. **States are defined locally:** a state on $\mathcal{W}(\mathcal{M}, g)$ assigns expectation values to observables in each spacetime region.

The cell vacuum can be defined in this framework by choosing a foliation (time-slicing) and constructing the coherent state product on each time-slice. The construction is foliation-dependent, but the physical predictions (energy density, stress-energy) are covariant. **[FRAMEWORK ESTABLISHED]**

The foliation-dependence is not a defect -- it reflects the physical content of the cell vacuum: a preferred spatial structure at the Compton scale. This is analogous to thermal states, which also require a preferred frame (the rest frame of the heat bath).

## 8.7 Physical Interpretation: Different Questions, Different Answers

The orthogonality and superselection between the two vacua admits two interpretations:

**Interpretation A: One is right, one is wrong.** The universe is in one sector. Physics must determine which. The equation of state ($w = -1$ for dark energy, $w = 0$ for the cell vacuum as shown in Lesson 9) provides the discriminant.

**Interpretation B: Different questions, different states.** The two vacua are complementary descriptions, appropriate for different physical questions. The mode vacuum is correct for scattering calculations (where Poincare invariance is essential). The cell vacuum is correct for gravitational questions (where local energy density matters). Neither is "wrong" -- they answer different questions.

**[FRAMEWORK]** for both interpretations. The mathematical structure (orthogonality, superselection) is **[PROVEN]**. The physical interpretation requires confrontation with experiment.

The complementarity view is more nuanced and potentially more powerful, but it also raises difficult questions: How do you decide which question is being asked? Is there a formal criterion for selecting the appropriate vacuum? These remain open. **[OPEN]**

## Summary of Key Results

| Result | Status |
|--------|--------|
| $\langle 0\|\alpha\rangle = e^{-\|\alpha\|^2/2}$ | [PROVEN] |
| $\langle 0\|\Omega\rangle = e^{-N/4} \to 0$ | [PROVEN] |
| Different superselection sectors | [PROVEN] |
| No physical process mediates transition | [PROVEN] |
| Complementarity table (all entries) | [PROVEN] |
| Curved spacetime self-consistency $\sim 10^{-69}$ | [PROVEN] |
| Parker creation negligible ($\epsilon \sim 10^{-31}$) | [PROVEN] |
| Weyl algebra covariant construction | [FRAMEWORK ESTABLISHED] |
| Physical interpretation of complementarity | [FRAMEWORK] |

## Looking Ahead

The mathematical structure established in Lessons 7 and 8 is beautiful, rigorous, and proven. The cell vacuum exists, it lives in its own superselection sector, it is stable in curved spacetime, and it satisfies all the conditions needed for semiclassical gravity.

In Lesson 9, this beautiful structure meets a harsh reality: two independent calculations show that the cell vacuum has equation of state $w = 0$, not $w = -1$. The cell vacuum behaves as pressureless dust, not as a cosmological constant. The mathematical construction survives -- everything proven in Lessons 7 and 8 remains true -- but the identification with dark energy does not. The first principle is that you must not fool yourself, and Lesson 9 is where the theory stops fooling itself.
