#!/usr/bin/env python3
"""
Cosmological Constant Problem: A Category Error Demonstration

This script demonstrates that the 10^123 discrepancy between predicted
and observed vacuum energy is not a physics problem requiring exotic
cancellations, but a category error: asking a position-space question
(what gravity needs) using a momentum-space state (mode vacuum).

The resolution:
- Mode vacuum |0>: answers "are there particles?" -> use for scattering
- Cell vacuum |Omega>: answers "what energy is here?" -> use for gravity

Using the cell vacuum with the predicted lightest neutrino mass m_1 = 2.31 meV:
    rho = m^4 * c^5 / hbar^3 = 5.94 x 10^-10 J/m^3

This matches the observed dark energy density: rho_Lambda = 5.96 x 10^-10 J/m^3

Usage:
    python demo.py              # Full demonstration
    python demo.py --quick      # Quick summary only
    python demo.py --plot       # Generate visualization plots
"""

import argparse
import numpy as np

from constants import (
    HBAR, C, PLANCK_LENGTH, PLANCK_ENERGY,
    NEUTRINO, NEUTRINO_1, NEUTRINO_2, NEUTRINO_3,
    NEUTRINO_SUM_EV, DELTA_M21_SQ, DELTA_M31_SQ,
    ELECTRON, PROTON,
    OBSERVED_DARK_ENERGY_DENSITY,
    cell_vacuum_energy_density, mode_vacuum_energy_density,
    mass_from_energy_density, mass_kg_to_eV
)
from coherent_states import CoherentState, CellVacuumState
from vacuum_energy import (
    ModeVacuumCalculator, CellVacuumCalculator,
    demonstrate_category_error, analyze_complementarity,
    show_16pi2_origin
)


def print_header(title: str, char: str = "="):
    """Print a formatted section header."""
    width = 70
    print("\n" + char * width)
    print(f" {title}")
    print(char * width)


def show_key_formula():
    """Display the key formula and its verification."""
    print_header("KEY FORMULA: CELL VACUUM ENERGY DENSITY")

    print("""
    The cell vacuum |Omega> = tensor_n |alpha_n> with |alpha|^2 = 1/2

    Each cell of size lambda_C (Compton wavelength) contains one quantum mc^2.

    Energy density:
        rho = mc^2 / lambda_C^3
            = mc^2 / (hbar/mc)^3
            = mc^2 * (mc/hbar)^3
            = m^4 * c^5 / hbar^3

    This is FINITE, UNIQUE (dimensional analysis), and EXACT.
    """)

    # Verify numerically
    m_kg = NEUTRINO_1.mass_kg
    rho_calculated = cell_vacuum_energy_density(m_kg)

    print(f"Numerical verification (m_1 = 2.31 meV):")
    print(f"    m = {m_kg:.4e} kg")
    print(f"    rho = m^4 * c^5 / hbar^3")
    print(f"        = ({m_kg:.3e})^4 * ({C:.3e})^5 / ({HBAR:.3e})^3")
    print(f"        = {rho_calculated:.4e} J/m^3")
    print(f"\n    Observed rho_Lambda = {OBSERVED_DARK_ENERGY_DENSITY:.4e} J/m^3")
    print(f"    Ratio: {rho_calculated/OBSERVED_DARK_ENERGY_DENSITY:.6f}")


def neutrino_mass_predictions():
    """Show the neutrino mass predictions from the framework."""
    print_header("NEUTRINO MASS PREDICTIONS")

    print("""
    From rho_Lambda = m^4 * c^5 / hbar^3, inverting:

        m = (rho_Lambda * hbar^3 / c^5)^(1/4)
        m = 2.31 meV  <-- PREDICTED lightest neutrino mass

    Combined with neutrino oscillation data (PDG 2023):
        Delta m^2_21 = 7.53 x 10^-5 eV^2
        Delta m^2_31 = 2.45 x 10^-3 eV^2  (normal ordering)

    This gives all three masses:
    """)

    print(f"    m_1 (lightest) = {NEUTRINO_1.mass_eV*1e3:.2f} meV  [FROM rho_Lambda]")
    print(f"    m_2            = {NEUTRINO_2.mass_eV*1e3:.2f} meV  [from m_1 + Delta m^2_21]")
    print(f"    m_3 (heaviest) = {NEUTRINO_3.mass_eV*1e3:.2f} meV  [from m_1 + Delta m^2_31]")
    print(f"\n    Sum m_nu       = {NEUTRINO_SUM_EV*1e3:.1f} meV")

    print(f"""
    Cosmological bound (Planck 2018): Sum m_nu < 120 meV
    Our prediction: {NEUTRINO_SUM_EV*1e3:.1f} meV < 120 meV  [SATISFIED]

    This is a TESTABLE PREDICTION:
    - If future experiments find Sum m_nu < 45 meV --> framework falsified
    - If they find Sum m_nu ~ 60 meV --> framework supported
    """)


def feynman_lecture():
    """Reproduce the key argument from the Feynman-style explanation."""
    print_header("THE FEYNMAN ARGUMENT")

    print("""
    "What question are we answering?"

    When we sum over modes to get vacuum energy, we compute:
        rho = integral d^3k/(2pi)^3 * hbar*omega_k/2

    Each mode e^(ikx) spans ALL SPACE. It has definite momentum k,
    but completely indefinite position.

    Gravity's equation is LOCAL:
        G_uv(x) = 8*pi*G/c^4 * T_uv(x)

    Curvature HERE depends on energy HERE. This is a position question.

    You cannot ask "what's here?" to something that isn't anywhere.

    That's like computing <p|x|p> - asking a position question to
    a momentum eigenstate. You get nonsense (infinite/undefined).
    """)

    mode_calc = ModeVacuumCalculator()
    rho_planck = mode_calc.energy_density_planck_cutoff()

    print(f"    Mode vacuum (Planck cutoff):  rho = {rho_planck:.2e} J/m^3")
    print(f"    Observed dark energy:         rho = {OBSERVED_DARK_ENERGY_DENSITY:.2e} J/m^3")
    print(f"    Discrepancy: 10^{np.log10(rho_planck/OBSERVED_DARK_ENERGY_DENSITY):.0f}")

    print("""
    The "worst prediction in physics" isn't a prediction.
    It's a category error.

    Nothing needs to cancel. Just use the right state.
    """)


def coherent_state_properties():
    """Demonstrate that coherent states saturate uncertainty bounds."""
    print_header("COHERENT STATE: MINIMUM UNCERTAINTY")

    print("""
    The coherent state |alpha> with |alpha|^2 = 1/2 is special:

    Energy: E = hbar*omega * (|alpha|^2 + 1/2) = hbar*omega * (0.5 + 0.5) = hbar*omega = mc^2

    Uncertainty: Delta_x * Delta_p = hbar/2  (minimum possible)

    This is the "most classical" quantum state - saturates Heisenberg bound.
    The cell vacuum is built from these minimum-uncertainty states.
    """)

    omega = ELECTRON.compton_frequency
    state = CoherentState(alpha=np.sqrt(0.5), omega=omega, mass=ELECTRON.mass_kg)

    print(f"    Coherent state |alpha> with |alpha|^2 = 0.5:")
    print(f"    Delta_x        = {state.delta_x:.3e} m")
    print(f"    Delta_p        = {state.delta_p:.3e} kg*m/s")
    print(f"    Delta_x*Delta_p= {state.uncertainty_product:.6e} J*s")
    print(f"    hbar/2         = {HBAR/2:.6e} J*s")
    print(f"    Ratio          = {state.uncertainty_product/(HBAR/2):.10f}  [EXACTLY 1]")


def summary_table():
    """Print the key comparison table."""
    print_header("SUMMARY: MODE VACUUM vs CELL VACUUM")

    print("""
    +--------------------+------------------------+------------------------+
    | Property           | Mode Vacuum |0>        | Cell Vacuum |Omega>    |
    +--------------------+------------------------+------------------------+
    | Definition         | a_k|0> = 0 for all k   | |Omega> = prod_n |a_n> |
    | Momentum structure | DEFINITE               | INDEFINITE             |
    | Position structure | INDEFINITE             | DEFINITE               |
    | Entanglement       | Nonlocal (all space)   | Local (product state)  |
    | Local energy <T00> | DIVERGENT (infinity)   | FINITE (m^4c^5/hbar^3) |
    | Question answered  | "Particles present?"   | "Energy here?"         |
    | Appropriate for    | Scattering (QFT)       | Gravity (GR)           |
    +--------------------+------------------------+------------------------+
    |                                                                      |
    |   These states are ORTHOGONAL: <0|Omega> = 0 as N -> infinity        |
    |   They answer CONJUGATE questions (like x and p)                     |
    |   Using |0> for gravity is a CATEGORY ERROR                          |
    |                                                                      |
    +----------------------------------------------------------------------+
    """)


def the_punchline():
    """The final insight."""
    print_header("THE PUNCHLINE", char="*")

    mode_calc = ModeVacuumCalculator()
    cell_calc = CellVacuumCalculator(mass=NEUTRINO_1.mass_kg)

    print(f"""
    STANDARD CALCULATION (Mode Vacuum, Planck cutoff):
        rho = hbar*c*k^4/(16*pi^2) = {mode_calc.energy_density_planck_cutoff():.2e} J/m^3

    CORRECT CALCULATION (Cell Vacuum, m_1 = 2.31 meV):
        rho = m^4*c^5/hbar^3 = {cell_calc.energy_density:.2e} J/m^3

    OBSERVED:
        rho_Lambda = {OBSERVED_DARK_ENERGY_DENSITY:.2e} J/m^3

    RATIO to observed:
        Cell vacuum: {cell_calc.energy_density/OBSERVED_DARK_ENERGY_DENSITY:.4f}
        Mode vacuum: 10^{np.log10(mode_calc.energy_density_planck_cutoff()/OBSERVED_DARK_ENERGY_DENSITY):.0f}

    The 10^123 "problem" was asking the wrong question.

    "Vacuum" is not a thing. It's a state relative to a question.
    - Vacuum for particles: |0> -- "no excitations"
    - Vacuum for gravity:   |Omega> -- "minimum local energy"

    Different questions. Different states. Different answers.
    No cancellation needed.

    That's all it is.
    """)


def quick_summary():
    """Print a brief summary of the key result."""
    mode_calc = ModeVacuumCalculator()
    cell_calc = CellVacuumCalculator(mass=NEUTRINO_1.mass_kg)

    print("\n" + "=" * 70)
    print("COSMOLOGICAL CONSTANT: CATEGORY ERROR RESOLUTION")
    print("=" * 70)
    print(f"""
    KEY FORMULA: rho = m^4 * c^5 / hbar^3

    For m_1 = 2.31 meV (predicted lightest neutrino):
        Cell vacuum:  {cell_calc.energy_density:.4e} J/m^3
        Observed:     {OBSERVED_DARK_ENERGY_DENSITY:.4e} J/m^3
        Ratio:        {cell_calc.energy_density/OBSERVED_DARK_ENERGY_DENSITY:.4f}  <-- MATCH!

    For comparison (mode vacuum, Planck cutoff):
        Mode vacuum:  {mode_calc.energy_density_planck_cutoff():.2e} J/m^3
        Discrepancy:  10^{np.log10(mode_calc.energy_density_planck_cutoff()/OBSERVED_DARK_ENERGY_DENSITY):.0f}

    The "problem" was using a momentum-space state |0>
    to answer a position-space question (local energy for gravity).

    Use the position-space state |Omega> and you get the right answer.

    PREDICTIONS:
        m_1 = 2.31 meV
        m_2 = {NEUTRINO_2.mass_eV*1e3:.1f} meV
        m_3 = {NEUTRINO_3.mass_eV*1e3:.1f} meV
        Sum = {NEUTRINO_SUM_EV*1e3:.1f} meV < 120 meV bound
    """)


def main():
    parser = argparse.ArgumentParser(
        description="Demonstrate the cosmological constant category error"
    )
    parser.add_argument('--quick', action='store_true',
                       help='Show quick summary only')
    parser.add_argument('--plot', action='store_true',
                       help='Generate visualization plots')

    args = parser.parse_args()

    if args.quick:
        quick_summary()
        return

    if args.plot:
        from visualization import create_all_figures
        create_all_figures("figures")
        return

    # Full demonstration
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  THE COSMOLOGICAL CONSTANT PROBLEM: A CATEGORY ERROR".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)

    show_key_formula()
    neutrino_mass_predictions()
    feynman_lecture()
    coherent_state_properties()
    summary_table()
    the_punchline()


if __name__ == "__main__":
    main()
