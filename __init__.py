"""
Vacuum Physics: Cosmological Constant Category Error

This package implements the physics of vacuum states and demonstrates
that the cosmological constant "problem" (10^123 discrepancy) arises
from a category error: using a momentum-space state to answer a
position-space question.

KEY FORMULA:
    rho_Omega = m^4 * c^5 / hbar^3

For m = 2.31 meV (predicted lightest neutrino):
    rho = 5.94 x 10^-10 J/m^3 = observed dark energy density

Modules:
    constants: Physical constants, particle data, core formulas
    coherent_states: Coherent state physics and uncertainty relations
    vacuum_energy: Mode vacuum and cell vacuum calculations
    visualization: Plotting tools for demonstrations
    demo: Main demonstration script

Quick usage:
    >>> from vacuum_physics import CellVacuumCalculator, NEUTRINO_1
    >>> cell = CellVacuumCalculator(NEUTRINO_1.mass_kg)
    >>> print(f"Energy density: {cell.energy_density:.2e} J/m^3")
    Energy density: 5.94e-10 J/m^3  # Matches observed dark energy!

    >>> from vacuum_physics import OBSERVED_DARK_ENERGY_DENSITY
    >>> ratio = cell.energy_density / OBSERVED_DARK_ENERGY_DENSITY
    >>> print(f"Ratio to observed: {ratio:.4f}")  # Should be ~1.0
    Ratio to observed: 0.9962

Key insight:
    |0> (mode vacuum): answers "are there particles?" - for QFT/scattering
    |Omega> (cell vacuum): answers "what energy is here?" - for gravity

    Gravity needs the second. Using the first gives divergence.
    Use the right state and you get the right answer.
"""

from .constants import (
    # Fundamental constants
    HBAR, C, G, KB,
    EV_TO_JOULE, EV_TO_KG,

    # Planck scales
    PLANCK_LENGTH, PLANCK_MASS, PLANCK_ENERGY, PLANCK_TIME,

    # Particles
    ELECTRON, PROTON,
    NEUTRINO, NEUTRINO_1, NEUTRINO_2, NEUTRINO_3,
    NEUTRINO_M1_EV, NEUTRINO_M2_EV, NEUTRINO_M3_EV, NEUTRINO_SUM_EV,
    DELTA_M21_SQ, DELTA_M31_SQ,

    # Cosmological values
    OBSERVED_DARK_ENERGY_DENSITY,

    # Core functions
    compton_wavelength, compton_frequency,
    cell_vacuum_energy_density, mode_vacuum_energy_density,
    mode_vacuum_compton_cutoff, mass_from_energy_density,
    mass_eV_to_kg, mass_kg_to_eV,

    # Particle class
    Particle,
)

from .coherent_states import (
    CoherentState,
    CellVacuumState,
)

from .vacuum_energy import (
    ModeVacuumCalculator,
    CellVacuumCalculator,
    compare_vacua,
    demonstrate_category_error,
    analyze_complementarity,
    show_16pi2_origin,
)

__version__ = "1.0.0"
__author__ = "Vacuum Physics Module"

__all__ = [
    # Constants
    'HBAR', 'C', 'G', 'KB',
    'EV_TO_JOULE', 'EV_TO_KG',
    'PLANCK_LENGTH', 'PLANCK_MASS', 'PLANCK_ENERGY', 'PLANCK_TIME',

    # Particles
    'ELECTRON', 'PROTON', 'Particle',
    'NEUTRINO', 'NEUTRINO_1', 'NEUTRINO_2', 'NEUTRINO_3',
    'NEUTRINO_M1_EV', 'NEUTRINO_M2_EV', 'NEUTRINO_M3_EV', 'NEUTRINO_SUM_EV',
    'DELTA_M21_SQ', 'DELTA_M31_SQ',

    # Cosmological
    'OBSERVED_DARK_ENERGY_DENSITY',

    # Functions
    'compton_wavelength', 'compton_frequency',
    'cell_vacuum_energy_density', 'mode_vacuum_energy_density',
    'mode_vacuum_compton_cutoff', 'mass_from_energy_density',
    'mass_eV_to_kg', 'mass_kg_to_eV',

    # Classes
    'CoherentState', 'CellVacuumState',
    'ModeVacuumCalculator', 'CellVacuumCalculator',

    # Analysis functions
    'compare_vacua', 'demonstrate_category_error',
    'analyze_complementarity', 'show_16pi2_origin',
]
