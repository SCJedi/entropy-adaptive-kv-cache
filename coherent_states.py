"""
Coherent State Physics

Coherent states |α⟩ are the "most classical" quantum states:
- They saturate the Heisenberg uncertainty bound: Δx·Δp = ℏ/2
- They remain coherent under time evolution
- They form an overcomplete basis for Hilbert space

The cell vacuum |Ω⟩ = ⊗ₙ |αₙ⟩ is built from coherent states,
giving it definite local structure suitable for gravitational questions.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional
try:
    from .constants import HBAR, C
except ImportError:
    from constants import HBAR, C


@dataclass
class CoherentState:
    """
    A quantum harmonic oscillator coherent state |α⟩.

    The coherent state is an eigenstate of the annihilation operator:
        a|α⟩ = α|α⟩

    For a harmonic oscillator with mass m and frequency ω:
        - α = √(mω/2ℏ)·x₀ + i·p₀/√(2mωℏ)
        - |α|² = mean occupation number ⟨n⟩

    The special case |α|² = 1/2 gives exactly one quantum of energy
    ℏω when including zero-point energy: E = ℏω(|α|² + 1/2) = ℏω.
    """

    alpha: complex  # Coherent state parameter
    omega: float    # Angular frequency [rad/s]
    mass: float     # Effective mass [kg]

    @property
    def alpha_squared(self) -> float:
        """Mean occupation number ⟨n⟩ = |α|²"""
        return abs(self.alpha) ** 2

    @property
    def mean_energy(self) -> float:
        """
        Mean energy ⟨H⟩ = ℏω(|α|² + 1/2)

        For |α|² = 1/2, this equals exactly ℏω = mc².
        """
        return HBAR * self.omega * (self.alpha_squared + 0.5)

    @property
    def zero_point_energy(self) -> float:
        """Zero-point energy E₀ = ℏω/2"""
        return 0.5 * HBAR * self.omega

    @property
    def length_scale(self) -> float:
        """Characteristic length √(ℏ/mω) of the oscillator"""
        return np.sqrt(HBAR / (self.mass * self.omega))

    @property
    def delta_x(self) -> float:
        """
        Position uncertainty Δx = √(ℏ/2mω)

        For coherent states, this is independent of α.
        """
        return np.sqrt(HBAR / (2 * self.mass * self.omega))

    @property
    def delta_p(self) -> float:
        """
        Momentum uncertainty Δp = √(ℏmω/2)

        For coherent states, this is independent of α.
        """
        return np.sqrt(HBAR * self.mass * self.omega / 2)

    @property
    def uncertainty_product(self) -> float:
        """
        Uncertainty product Δx·Δp

        For coherent states, this exactly equals ℏ/2 (minimum uncertainty).
        """
        return self.delta_x * self.delta_p

    @property
    def saturates_uncertainty(self) -> bool:
        """Check if state saturates the Heisenberg bound."""
        return np.isclose(self.uncertainty_product, HBAR / 2, rtol=1e-10)

    def mean_position(self) -> float:
        """Mean position ⟨x⟩ = √(2ℏ/mω) · Re(α)"""
        return np.sqrt(2 * HBAR / (self.mass * self.omega)) * self.alpha.real

    def mean_momentum(self) -> float:
        """Mean momentum ⟨p⟩ = √(2ℏmω) · Im(α)"""
        return np.sqrt(2 * HBAR * self.mass * self.omega) * self.alpha.imag

    def number_state_probability(self, n: int) -> float:
        """
        Probability to find exactly n quanta: |⟨n|α⟩|² = e^(-|α|²) |α|^(2n) / n!

        Coherent states have Poissonian number statistics.
        """
        from math import factorial
        return np.exp(-self.alpha_squared) * self.alpha_squared**n / factorial(n)

    def wavefunction(self, x: np.ndarray) -> np.ndarray:
        """
        Position-space wavefunction ψ(x) = ⟨x|α⟩

        ψ(x) = (mω/πℏ)^(1/4) exp(-(mω/2ℏ)(x-⟨x⟩)² + i⟨p⟩x/ℏ - i⟨p⟩⟨x⟩/2ℏ)
        """
        x0 = self.mean_position()
        p0 = self.mean_momentum()
        prefactor = (self.mass * self.omega / (np.pi * HBAR)) ** 0.25
        gaussian = np.exp(-self.mass * self.omega / (2 * HBAR) * (x - x0) ** 2)
        phase = np.exp(1j * (p0 * x / HBAR - p0 * x0 / (2 * HBAR)))
        return prefactor * gaussian * phase


@dataclass
class CellVacuumState:
    """
    The cell vacuum |Ω⟩ = ⊗ₙ |αₙ⟩

    Space is divided into cells of size λ_C (Compton wavelength).
    Each cell contains a coherent state with |α|² = 1/2.

    Properties:
    - Product state: no entanglement between cells
    - Definite local energy: mc² per cell
    - Answers position-space questions
    - Appropriate for gravitational physics
    """

    mass: float           # Mass scale (determines cell size) [kg]
    num_cells: int = 1    # Number of cells (for finite systems)

    @property
    def compton_wavelength(self) -> float:
        """Cell size λ_C = ℏ/(mc)"""
        return HBAR / (self.mass * C)

    @property
    def compton_frequency(self) -> float:
        """Natural frequency ω = mc²/ℏ"""
        return self.mass * C**2 / HBAR

    @property
    def cell_volume(self) -> float:
        """Volume of one cell λ_C³"""
        return self.compton_wavelength ** 3

    @property
    def energy_per_cell(self) -> float:
        """
        Energy in each cell: E = ℏω(|α|² + 1/2) = mc²

        With |α|² = 1/2, we get exactly one rest mass energy per cell.
        """
        return self.mass * C**2

    @property
    def energy_density(self) -> float:
        """
        Local energy density ρ = mc²/λ_C³ = m⁴c⁵/ℏ³

        This is FINITE, unlike the mode vacuum calculation.
        """
        return self.energy_per_cell / self.cell_volume

    @property
    def total_energy(self) -> float:
        """Total energy for the system with num_cells cells."""
        return self.num_cells * self.energy_per_cell

    def get_cell_state(self, cell_index: int = 0) -> CoherentState:
        """
        Return the coherent state for a given cell.

        All cells have |α|² = 1/2 (special value giving E = mc²).
        """
        alpha = np.sqrt(0.5)  # |α|² = 1/2
        return CoherentState(
            alpha=alpha,
            omega=self.compton_frequency,
            mass=self.mass
        )


def compare_state_uncertainties():
    """
    Compare uncertainty relations for different state types.

    |State Type          |Δx         |Δp         |Δx·Δp    |
    |--------------------|-----------|-----------|---------|
    |Position eigenstate |0          |∞          |undefined|
    |Coherent state      |√(ℏ/2mω)   |√(ℏmω/2)   |ℏ/2      |
    |Momentum eigenstate |∞          |0          |undefined|
    """
    from constants import ELECTRON

    omega = ELECTRON.mass_kg * C**2 / HBAR  # Compton frequency

    # Create a coherent state
    coherent = CoherentState(alpha=np.sqrt(0.5), omega=omega, mass=ELECTRON.mass_kg)

    print("=" * 60)
    print("UNCERTAINTY COMPARISON")
    print("=" * 60)

    print(f"\nCoherent state |α⟩ with |α|² = 0.5:")
    print(f"  Δx = {coherent.delta_x:.3e} m")
    print(f"  Δp = {coherent.delta_p:.3e} kg·m/s")
    print(f"  Δx·Δp = {coherent.uncertainty_product:.3e} J·s")
    print(f"  ℏ/2   = {HBAR/2:.3e} J·s")
    print(f"  Saturates bound: {coherent.saturates_uncertainty}")

    print(f"\nMean energy: {coherent.mean_energy:.3e} J")
    print(f"mc²:         {ELECTRON.mass_kg * C**2:.3e} J")


if __name__ == "__main__":
    from constants import NEUTRINO, ELECTRON

    compare_state_uncertainties()

    print("\n" + "=" * 60)
    print("CELL VACUUM PROPERTIES")
    print("=" * 60)

    for particle in [NEUTRINO, ELECTRON]:
        cell_vac = CellVacuumState(mass=particle.mass_kg)
        print(f"\n{particle.name.upper()} mass scale:")
        print(f"  Cell size (λ_C):     {cell_vac.compton_wavelength:.3e} m")
        print(f"  Energy per cell:     {cell_vac.energy_per_cell:.3e} J")
        print(f"  Energy density:      {cell_vac.energy_density:.3e} J/m³")

        state = cell_vac.get_cell_state()
        print(f"  |α|² = {state.alpha_squared:.1f}")
        print(f"  Δx·Δp = ℏ/2: {state.saturates_uncertainty}")
