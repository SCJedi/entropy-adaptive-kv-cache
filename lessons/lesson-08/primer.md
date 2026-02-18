# Primer: Orthogonality and Superselection

## The Big Idea

The mode vacuum $|0\rangle$ and the cell vacuum $|\Omega\rangle$ are orthogonal: their inner product goes to zero as the number of Compton cells grows to infinity. This means they live in different superselection sectors -- genuinely distinct phases of the quantum field, as separate as states with different electric charge. No physical process can transform one into the other. This is not a defect of the construction; it is a deep structural feature with precise mathematical content.

## The Overlap Vanishes

The calculation is straightforward. Each Compton cell in the cell vacuum is in a coherent state $|\alpha\rangle$ with $|\alpha|^2 = 1/2$. The overlap of a single coherent state with the vacuum is:

$$
\langle 0|\alpha\rangle = e^{-|\alpha|^2/2} = e^{-1/4} \approx 0.779
$$

That is about 78% -- a substantial overlap for one cell. But for $N$ independent cells, the overlaps multiply:

$$
\langle 0|\Omega\rangle = (e^{-1/4})^N = e^{-N/4}
$$

For $N = 10$: the transition probability is $e^{-5} \approx 0.7\%$. For $N = 100$: it is $e^{-50} \approx 10^{-22}$. For a cosmological volume with $N \sim 10^{60}$: it is $e^{-10^{60}/4}$, a number so small it has no physical meaning beyond "exactly zero for all practical purposes."

The exponential convergence is relentless. Each additional cell multiplies the overlap by 0.779, and the product crashes to zero. **[PROVEN]**

## Superselection: What It Means

Two states in different superselection sectors cannot be superposed, cannot interfere, and cannot be connected by any local observable. The universe must be in one sector or the other -- there is no "a little bit of both."

This is not exotic. Familiar examples include charge superselection (you cannot superpose an electron and a positron) and the infinite-volume limit of spontaneous symmetry breaking (a ferromagnet must choose spin-up or spin-down). The mode/cell vacuum superselection is structurally identical, arising from the infinite number of degrees of freedom in a quantum field. **[PROVEN]**

The physical implication is stark: if the universe is in the cell vacuum sector, it has always been there and always will be. There is no tunneling, no phase transition, no dynamical process that crosses sector boundaries. The choice of sector is a fact about the initial conditions of the universe.

## The Complementarity Table

With the AQFT results from Lesson 7 and the orthogonality proven here, the analogy between the two vacua and position/momentum eigenstates now has rigorous mathematical backing:

- The mode vacuum has definite properties in momentum space (zero particles per mode) but divergent energy in position space.
- The cell vacuum has definite properties in position space (finite energy per cell) but indefinite momentum-space properties.
- They are orthogonal and live in different superselection sectors, just as $|x\rangle$ and $|p\rangle$ are orthogonal (in the distributional sense) and emphasize complementary aspects of the same system.

Every entry in the comparison table -- particle number, entanglement, energy density, Poincare invariance, spectrum condition, Hadamard status -- is backed by a theorem or a direct calculation. **[PROVEN]**

## Curved Spacetime Stability

Two results establish the robustness of the cell vacuum in an expanding universe:

**Self-consistency:** The cell vacuum's energy density $\rho_\Omega$ curves spacetime, which modifies the cells, which changes $\rho_\Omega$. This feedback loop converges immediately: the correction is of order $\rho_\Omega/\rho_{\text{Planck}} \sim 10^{-69}$. The flat-spacetime construction is valid to 69 decimal places. **[PROVEN]**

**Particle creation:** The expanding universe can create particles from the vacuum (the Parker effect), but the rate is controlled by the adiabatic parameter $\epsilon \sim H/(mc^2/\hbar) \sim 10^{-31}$. Particle creation is exponentially suppressed. The cell vacuum does not evaporate into radiation on cosmological timescales. **[PROVEN]**

These numbers -- $10^{-69}$ and $10^{-31}$ -- are striking. They mean the construction is not fragile. It does not require fine-tuning or special conditions to survive in a realistic cosmological setting.

## Key Takeaways

1. **Orthogonality is exponentially fast.** The overlap $e^{-N/4}$ vanishes long before you reach cosmological volumes. By $N = 100$ cells, the states are effectively orthogonal.

2. **Superselection is real and structural.** The two vacua are as distinct as states with different charge. No physical process connects them.

3. **The complementarity table is now rigorous.** Every entry has mathematical backing from the AQFT construction and the orthogonality calculation.

4. **Curved spacetime is no threat.** Self-consistency to $10^{-69}$ and negligible particle creation ($\epsilon \sim 10^{-31}$) mean the construction is stable and robust.

5. **The interpretation remains open.** Are the two vacua "complementary descriptions" of the same physics, or is one simply wrong? The mathematics cannot answer this. Experiment must.

## What Comes Next

The mathematical beauty of Lessons 7 and 8 is real. The cell vacuum is a legitimate, stable, orthogonal state with rigorous mathematical foundations. But Lesson 9 delivers difficult news: two independent calculations show that the cell vacuum has equation of state $w = 0$ (pressureless dust), not $w = -1$ (cosmological constant). The mathematics survives. The dark energy interpretation does not.
