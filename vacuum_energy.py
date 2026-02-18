"""
Vacuum Energy Calculations

This module implements both approaches to vacuum energy:

1. MODE VACUUM |0>: The standard QFT calculation
   - Sum over all momentum modes: rho = integral d^3k/(2pi)^3 * hbar*omega_k/2
   - DIVERGENT: requires cutoff, gives ~10^113 J/m^3 at Planck scale
   - Asks: "Are there particles?" (momentum-space question)

2. CELL VACUUM |Omega>: The local structure approach
   - Product of coherent states: |Omega> = tensor_n |alpha_n>
   - FINITE: rho = m^4*c^5/hbar^3
   - Asks: "What energy is here?" (position-space question)

The 10^123 discrepancy arises from asking a position-space question
(what gravity needs) using a momentum-space state (mode vacuum).

Key Result:
    For m = 2.31 meV (lightest neutrino), cell vacuum gives
    rho = 5.96 x 10^-10 J/m^3, matching observed dark energy.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
try:
    from .constants import (
        HBAR, C, G, PLANCK_LENGTH, PLANCK_ENERGY,
        NEUTRINO, NEUTRINO_1, NEUTRINO_2, NEUTRINO_3,
        ELECTRON, PROTON, OBSERVED_DARK_ENERGY_DENSITY,
        cell_vacuum_energy_density, mode_vacuum_energy_density,
        mode_vacuum_compton_cutoff, mass_from_energy_density,
        mass_kg_to_eV, EV_TO_KG
    )
except ImportError:
    from constants import (
        HBAR, C, G, PLANCK_LENGTH, PLANCK_ENERGY,
        NEUTRINO, NEUTRINO_1, NEUTRINO_2, NEUTRINO_3,
        ELECTRON, PROTON, OBSERVED_DARK_ENERGY_DENSITY,
        cell_vacuum_energy_density, mode_vacuum_energy_density,
        mode_vacuum_compton_cutoff, mass_from_energy_density,
        mass_kg_to_eV, EV_TO_KG
    )


# =============================================================================
# MODE VACUUM: The Standard (Divergent) Calculation
# =============================================================================

@dataclass
class ModeVacuumCalculator:
    """
    Calculate vacuum energy density using the mode expansion.

    The mode vacuum |0> is defined by: a_k|0> = 0 for all k

    Each mode contributes zero-point energy hbar*omega_k/2, giving:
        rho = integral d^3k/(2pi)^3 * hbar*omega_k/2

    For relativistic modes (omega_k = c|k|):
        rho = hbar*c*k_max^4 / (16*pi^2)

    This DIVERGES as k_max -> infinity. With a Planck cutoff, you get ~10^113 J/m^3.
    """

    # Cutoff wavenumber (default: Planck scale)
    k_cutoff: float = 1.0 / PLANCK_LENGTH

    def zero_point_energy_per_mode(self, k: float) -> float:
        """
        Zero-point energy for a single mode with wavenumber k.

        E = hbar*omega/2 = hbar*c*|k|/2  (for massless field)
        """
        omega = C * abs(k)
        return HBAR * omega / 2

    def mode_density(self, k: float) -> float:
        """
        Density of states in k-space: d^3k/(2pi)^3 = 4*pi*k^2*dk/(2pi)^3

        Number of modes per unit k = 4*pi*k^2/(2pi)^3 = k^2/(2*pi^2)
        """
        return k**2 / (2 * np.pi**2)

    def energy_density_integrand(self, k: float) -> float:
        """
        Integrand for energy density: (modes per dk) x (energy per mode)

        drho/dk = [k^2/(2*pi^2)] x [hbar*c*k/2] = hbar*c*k^3/(4*pi^2)
        """
        return HBAR * C * k**3 / (4 * np.pi**2)

    def energy_density_with_cutoff(self, k_max: Optional[float] = None) -> float:
        """
        Total vacuum energy density with momentum cutoff.

        rho = integral_0^k_max dk * hbar*c*k^3/(4*pi^2)
            = hbar*c*k_max^4/(16*pi^2)

        This is the "naive" calculation that gives the 10^123 problem.
        """
        if k_max is None:
            k_max = self.k_cutoff
        return mode_vacuum_energy_density(k_max)

    def energy_density_planck_cutoff(self) -> float:
        """
        Energy density with Planck scale cutoff.

        k_max = 1/L_Planck ~ 6.2 x 10^34 m^-1
        rho ~ 10^111 J/m^3

        This is the infamous "worst prediction in physics".
        """
        k_planck = 1.0 / PLANCK_LENGTH
        return self.energy_density_with_cutoff(k_planck)

    def energy_density_compton_cutoff(self, mass_kg: float) -> float:
        """
        Energy density with Compton wavelength cutoff.

        k_max = m*c/hbar
        rho = m^4*c^5 / (16*pi^2*hbar^3)

        This is 16*pi^2 ~ 158 times smaller than cell vacuum.
        """
        return mode_vacuum_compton_cutoff(mass_kg)

    def show_divergence(self, num_points: int = 10) -> None:
        """
        Demonstrate how energy density grows with cutoff.

        The dependence is rho ~ k_max^4, showing the quartic divergence.
        """
        print("=" * 70)
        print("MODE VACUUM DIVERGENCE: rho = hbar*c*k^4 / (16*pi^2)")
        print("=" * 70)
        print(f"\n{'Cutoff scale':<20} {'k_max (m^-1)':<15} {'rho (J/m^3)':<15}")
        print("-" * 50)

        # Various cutoff scales
        scales = [
            ("Atomic (A)", 1e10),
            ("Nuclear (fm)", 1e15),
            ("QCD (100 MeV)", 5e14),
            ("Electroweak (GeV)", 5e15),
            ("GUT (10^16 GeV)", 5e31),
            ("Planck", 1/PLANCK_LENGTH),
        ]

        for name, k_max in scales:
            rho = self.energy_density_with_cutoff(k_max)
            print(f"{name:<20} {k_max:<15.2e} {rho:<15.2e}")

        print(f"\nObserved rho_Lambda = {OBSERVED_DARK_ENERGY_DENSITY:.2e} J/m^3")
        print(f"Planck cutoff rho   = {self.energy_density_planck_cutoff():.2e} J/m^3")
        print(f"Discrepancy: 10^{np.log10(self.energy_density_planck_cutoff() / OBSERVED_DARK_ENERGY_DENSITY):.0f}")


# =============================================================================
# CELL VACUUM: The Finite Calculation
# =============================================================================

@dataclass
class CellVacuumCalculator:
    """
    Calculate vacuum energy density using the cell decomposition.

    The cell vacuum |Omega> = tensor_n |alpha_n> with |alpha|^2 = 1/2

    Each cell of size lambda_C contains energy mc^2:
        rho = mc^2/lambda_C^3 = m^4*c^5/hbar^3

    This is FINITE and well-defined. No cutoff needed.
    """

    mass: float  # Mass scale determining cell size [kg]

    @property
    def compton_wavelength(self) -> float:
        """Cell size lambda_C = hbar/(mc)"""
        return HBAR / (self.mass * C)

    @property
    def compton_volume(self) -> float:
        """Cell volume lambda_C^3"""
        return self.compton_wavelength ** 3

    @property
    def energy_per_cell(self) -> float:
        """Energy in one cell: mc^2"""
        return self.mass * C**2

    @property
    def energy_density(self) -> float:
        """
        Cell vacuum energy density.

        rho = mc^2/lambda_C^3 = m^4*c^5/hbar^3

        For m = 2.31 meV (lightest neutrino): rho = 5.96 x 10^-10 J/m^3
        This matches the observed dark energy density!
        """
        return cell_vacuum_energy_density(self.mass)

    @property
    def mass_eV(self) -> float:
        """Mass in eV/c^2"""
        return mass_kg_to_eV(self.mass)

    @classmethod
    def from_energy_density(cls, target_rho: float) -> 'CellVacuumCalculator':
        """
        Find the mass scale that gives a target energy density.

        Given rho = m^4*c^5/hbar^3, solve for m:
            m = (rho*hbar^3/c^5)^(1/4)
        """
        mass = mass_from_energy_density(target_rho)
        return cls(mass=mass)


# =============================================================================
# COMPARISON: The Category Error
# =============================================================================

def compare_vacua(mass_kg: float, particle_name: str = "particle") -> dict:
    """
    Compare mode vacuum and cell vacuum calculations.

    This demonstrates the 16*pi^2 ratio and the category error.
    """
    mode_calc = ModeVacuumCalculator()
    cell_calc = CellVacuumCalculator(mass=mass_kg)

    # Mode vacuum with Compton cutoff
    rho_mode_compton = mode_calc.energy_density_compton_cutoff(mass_kg)

    # Cell vacuum (finite)
    rho_cell = cell_calc.energy_density

    # The ratio should be 16*pi^2
    ratio = rho_cell / rho_mode_compton

    results = {
        "particle": particle_name,
        "mass_kg": mass_kg,
        "mass_eV": mass_kg_to_eV(mass_kg),
        "rho_cell": rho_cell,
        "rho_mode_compton": rho_mode_compton,
        "ratio": ratio,
        "expected_ratio": 16 * np.pi**2,
        "compton_wavelength": cell_calc.compton_wavelength,
    }

    return results


def demonstrate_category_error():
    """
    Show that the cosmological constant "problem" is a category error.

    The mode vacuum answers: "Are there particles?"
    The cell vacuum answers: "What energy is here?"

    Gravity asks the second question. Using the first state gives nonsense.
    """
    print("=" * 70)
    print("THE COSMOLOGICAL CONSTANT CATEGORY ERROR")
    print("=" * 70)

    print("""
    +------------------------------------------------------------------+
    |  GRAVITY ASKS:    "What is the energy density at point x?"       |
    |  This is a POSITION-SPACE question.                              |
    |                                                                  |
    |  MODE VACUUM |0>: Has no definite position structure.            |
    |                   Modes span all space: Delta_x = infinity       |
    |                   Answer: DIVERGENT (infinity or 10^113 cutoff)  |
    |                                                                  |
    |  CELL VACUUM |Omega>: Has definite position structure.           |
    |                   Cells are localized: Delta_x = lambda_C        |
    |                   Answer: FINITE (m^4*c^5/hbar^3)                |
    +------------------------------------------------------------------+
    """)

    print("\n" + "-" * 70)
    print("NUMERICAL COMPARISON")
    print("-" * 70)

    mode_calc = ModeVacuumCalculator()
    rho_planck = mode_calc.energy_density_planck_cutoff()

    print(f"\nMode vacuum (Planck cutoff):  rho = {rho_planck:.2e} J/m^3")
    print(f"Observed dark energy:         rho = {OBSERVED_DARK_ENERGY_DENSITY:.2e} J/m^3")
    print(f"Discrepancy: 10^{np.log10(rho_planck/OBSERVED_DARK_ENERGY_DENSITY):.0f}")

    print("\n" + "-" * 70)
    print("CELL VACUUM WITH NEUTRINO MASSES")
    print("-" * 70)

    print(f"\n{'Neutrino':<15} {'Mass (meV)':<12} {'rho (J/m^3)':<15} {'rho/rho_obs':<12}")
    print("-" * 55)

    for nu in [NEUTRINO_1, NEUTRINO_2, NEUTRINO_3]:
        cell = CellVacuumCalculator(mass=nu.mass_kg)
        ratio = cell.energy_density / OBSERVED_DARK_ENERGY_DENSITY
        print(f"{nu.name:<15} {nu.mass_eV*1e3:<12.2f} {cell.energy_density:<15.2e} {ratio:<12.4f}")

    # Exact match
    exact_match = CellVacuumCalculator.from_energy_density(OBSERVED_DARK_ENERGY_DENSITY)
    print(f"\n{'Required mass':<15} {exact_match.mass_eV*1e3:<12.2f} {OBSERVED_DARK_ENERGY_DENSITY:<15.2e} {'1.0000':<12}")

    print(f"""
    +------------------------------------------------------------------+
    |  The lightest neutrino mass m_1 = 2.31 meV gives                 |
    |  rho = 5.94 x 10^-10 J/m^3 -- matching observed dark energy!     |
    |                                                                  |
    |  The "10^123 problem" was asking the wrong question.             |
    |  Nothing needs to cancel. Just use the right state.              |
    +------------------------------------------------------------------+
    """)


def analyze_complementarity():
    """
    Demonstrate the conjugate structure between |0> and |Omega>.

    This is Fourier uncertainty at the level of vacuum states:
    - |0>: Definite k (momentum), indefinite x (position)
    - |Omega>: Indefinite k (momentum), definite x (position)
    """
    print("=" * 70)
    print("COMPLEMENTARITY STRUCTURE: |0> vs |Omega>")
    print("=" * 70)

    print("""
    +--------------------+---------------------+---------------------+
    | Property           | Mode Vacuum |0>     | Cell Vacuum |Omega> |
    +--------------------+---------------------+---------------------+
    | Definition         | a_k|0> = 0 for all k| |Omega> = prod|a_n> |
    | Momentum structure | DEFINITE            | INDEFINITE          |
    | Position structure | INDEFINITE          | DEFINITE            |
    | Entanglement       | Nonlocal (all space)| Local (product)     |
    | Local energy <T00> | DIVERGENT (inf)     | FINITE (m^4c^5/h^3) |
    | Question answered  | "Particles present?"| "Energy here?"      |
    | Appropriate for    | Scattering (QFT)    | Gravity (GR)        |
    +--------------------+---------------------+---------------------+
    |                                                                |
    |   These are CONJUGATE states, like position and momentum       |
    |   eigenstates. You cannot use one to answer questions          |
    |   appropriate to the other without getting nonsense.           |
    |                                                                |
    |   <p|x|p> = undefined     <-->     <0|T_00(x)|0> = infinity    |
    |                                                                |
    +----------------------------------------------------------------+
    """)

    # Quantitative comparison
    print("\nQuantitative comparison for lightest neutrino (m_1 = 2.31 meV):")

    cell = CellVacuumCalculator(mass=NEUTRINO_1.mass_kg)
    mode = ModeVacuumCalculator()

    print(f"  Compton wavelength lambda_C = {cell.compton_wavelength:.3e} m")
    print(f"  Cell vacuum rho   = {cell.energy_density:.3e} J/m^3 (FINITE)")
    print(f"  Mode vacuum rho   = {mode.energy_density_compton_cutoff(NEUTRINO_1.mass_kg):.3e} J/m^3 (with Compton cutoff)")
    print(f"  Ratio cell/mode   = {cell.energy_density/mode.energy_density_compton_cutoff(NEUTRINO_1.mass_kg):.2f} = 16*pi^2")

    print(f"\n  Mode vacuum |0>: each mode e^(ikx) extends over ALL SPACE")
    print(f"  Cell vacuum |Omega>: each cell is localized to lambda_C = {cell.compton_wavelength:.2e} m")


def show_16pi2_origin():
    """
    Explain the origin of the factor 16*pi^2 between cell and mode vacua.
    """
    print("=" * 70)
    print("ORIGIN OF THE FACTOR 16*pi^2")
    print("=" * 70)

    print("""
    Cell vacuum energy density:
        rho_cell = mc^2 / lambda_C^3 = m^4*c^5 / hbar^3

    Mode vacuum energy density (Compton cutoff k = mc/hbar):
        rho_mode = integral_0^{mc/hbar} d^3k/(2pi)^3 * hbar*c*k/2
                 = hbar*c/(2) * 4pi/(2pi)^3 * integral k^3 dk
                 = hbar*c/(4pi^2) * (mc/hbar)^4 / 4
                 = m^4*c^5 / (16*pi^2 * hbar^3)

    Ratio:
        rho_cell / rho_mode = 16*pi^2 ~ 158

    Physical interpretation:
    - Factor (2pi)^3: Fourier transform normalization (mode vs cell counting)
    - Factor 2: Zero-point (1/2 hbar*omega) vs full quantum (hbar*omega)
    - Factor 1/pi: Spherical integration geometry
    """)

    # Numerical verification
    cell = CellVacuumCalculator(mass=NEUTRINO_1.mass_kg)
    mode = ModeVacuumCalculator()
    rho_mode = mode.energy_density_compton_cutoff(NEUTRINO_1.mass_kg)

    print(f"\nNumerical verification (m = 2.31 meV):")
    print(f"  rho_cell = {cell.energy_density:.4e} J/m^3")
    print(f"  rho_mode = {rho_mode:.4e} J/m^3")
    print(f"  Ratio    = {cell.energy_density/rho_mode:.4f}")
    print(f"  16*pi^2  = {16*np.pi**2:.4f}")


if __name__ == "__main__":
    # Show the divergence of mode vacuum
    mode_calc = ModeVacuumCalculator()
    mode_calc.show_divergence()

    print("\n")

    # Demonstrate the category error
    demonstrate_category_error()

    print("\n")

    # Show the 16*pi^2 factor
    show_16pi2_origin()

    print("\n")

    # Analyze complementarity
    analyze_complementarity()
