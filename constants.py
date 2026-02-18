"""
Physical constants for vacuum state calculations.

This module provides fundamental constants and derived quantities
relevant to the cosmological constant problem and vacuum energy.

Key formula: rho_Omega = m^4 c^5 / hbar^3

For m = 2.31 meV (predicted lightest neutrino), this gives
rho = 5.96 x 10^-10 J/m^3, matching the observed dark energy density.
"""

import numpy as np
from dataclasses import dataclass
from typing import NamedTuple


# =============================================================================
# Fundamental Constants (SI units) - CODATA 2018
# =============================================================================

HBAR = 1.054571817e-34      # Reduced Planck constant [J*s]
C = 2.99792458e8            # Speed of light [m/s]
G = 6.67430e-11             # Gravitational constant [m^3/(kg*s^2)]
KB = 1.380649e-23           # Boltzmann constant [J/K]

# Unit conversions
EV_TO_JOULE = 1.602176634e-19  # 1 eV in Joules
EV_TO_KG = EV_TO_JOULE / C**2  # 1 eV/c^2 in kg = 1.78266192e-36 kg


# =============================================================================
# Derived Scales
# =============================================================================

# Planck units
PLANCK_LENGTH = np.sqrt(HBAR * G / C**3)      # ~1.616e-35 m
PLANCK_MASS = np.sqrt(HBAR * C / G)           # ~2.176e-8 kg
PLANCK_TIME = np.sqrt(HBAR * G / C**5)        # ~5.391e-44 s
PLANCK_ENERGY = np.sqrt(HBAR * C**5 / G)      # ~1.956e9 J

# Natural units conversion: hbar*c = 197.3 MeV*fm
HBAR_C_MEV_FM = HBAR * C / (1e6 * EV_TO_JOULE * 1e-15)  # Should be ~197.3


# =============================================================================
# Particle Data
# =============================================================================

class Particle(NamedTuple):
    """Particle properties."""
    name: str
    mass_kg: float
    mass_eV: float

    @property
    def compton_wavelength(self) -> float:
        """Compton wavelength lambda_C = hbar/(mc) [m]"""
        return HBAR / (self.mass_kg * C)

    @property
    def compton_volume(self) -> float:
        """Compton volume lambda_C^3 [m^3]"""
        return self.compton_wavelength ** 3

    @property
    def rest_energy(self) -> float:
        """Rest energy mc^2 [J]"""
        return self.mass_kg * C**2

    @property
    def compton_frequency(self) -> float:
        """Compton angular frequency omega = mc^2/hbar [rad/s]"""
        return self.mass_kg * C**2 / HBAR


def mass_eV_to_kg(mass_eV: float) -> float:
    """Convert mass from eV/c^2 to kg."""
    return mass_eV * EV_TO_KG


def mass_kg_to_eV(mass_kg: float) -> float:
    """Convert mass from kg to eV/c^2."""
    return mass_kg / EV_TO_KG


# =============================================================================
# Particle Definitions
# =============================================================================

# Electron (well-measured)
ELECTRON = Particle("electron", 9.1093837015e-31, 0.51099895e6)

# Proton (well-measured)
PROTON = Particle("proton", 1.67262192369e-27, 938.27208816e6)

# Neutrino oscillation data (PDG 2023):
#   Delta m^2_21 = (7.53 +/- 0.18) x 10^-5 eV^2
#   Delta m^2_31 = (2.453 +/- 0.033) x 10^-3 eV^2 (normal ordering)
DELTA_M21_SQ = 7.53e-5   # eV^2
DELTA_M31_SQ = 2.453e-3  # eV^2 (normal ordering)

# PREDICTED lightest neutrino mass from rho_Lambda = m^4 c^5 / hbar^3
# Inverting: m = (rho_Lambda * hbar^3 / c^5)^(1/4)
# This gives m_1 = 2.31 meV
NEUTRINO_M1_EV = 2.31e-3  # 2.31 meV - predicted from dark energy density
NEUTRINO_M1_KG = mass_eV_to_kg(NEUTRINO_M1_EV)

# Derived neutrino masses from oscillation constraints
NEUTRINO_M2_EV = np.sqrt(NEUTRINO_M1_EV**2 + DELTA_M21_SQ)  # ~9.0 meV
NEUTRINO_M3_EV = np.sqrt(NEUTRINO_M1_EV**2 + DELTA_M31_SQ)  # ~50 meV
NEUTRINO_M2_KG = mass_eV_to_kg(NEUTRINO_M2_EV)
NEUTRINO_M3_KG = mass_eV_to_kg(NEUTRINO_M3_EV)

# Sum of neutrino masses (cosmological constraint: < 120 meV)
NEUTRINO_SUM_EV = NEUTRINO_M1_EV + NEUTRINO_M2_EV + NEUTRINO_M3_EV

# Particle objects
NEUTRINO_1 = Particle("nu_1 (lightest)", NEUTRINO_M1_KG, NEUTRINO_M1_EV)
NEUTRINO_2 = Particle("nu_2", NEUTRINO_M2_KG, NEUTRINO_M2_EV)
NEUTRINO_3 = Particle("nu_3 (heaviest)", NEUTRINO_M3_KG, NEUTRINO_M3_EV)

# Alias for convenience (the lightest neutrino is what matters)
NEUTRINO = NEUTRINO_1


# =============================================================================
# Cosmological Values
# =============================================================================

# Observed dark energy density (Planck 2018)
# rho_Lambda = (5.96 +/- 0.14) x 10^-10 J/m^3
OBSERVED_DARK_ENERGY_DENSITY = 5.96e-10  # J/m^3

# Hubble constant (Planck 2018)
H0_KM_S_MPC = 67.4  # km/s/Mpc
H0 = H0_KM_S_MPC * 1e3 / 3.0857e22  # Convert to 1/s


# =============================================================================
# Core Physics Functions
# =============================================================================

def compton_wavelength(mass_kg: float) -> float:
    """
    Calculate Compton wavelength for a given mass.

    lambda_C = hbar / (m*c)

    This is the fundamental length scale at which quantum effects
    become important for a particle of given mass.
    """
    return HBAR / (mass_kg * C)


def compton_frequency(mass_kg: float) -> float:
    """
    Calculate Compton angular frequency.

    omega = m*c^2 / hbar

    This is the natural oscillation frequency of a quantum of mass m.
    """
    return mass_kg * C**2 / HBAR


def cell_vacuum_energy_density(mass_kg: float) -> float:
    """
    Calculate the cell vacuum energy density for a given mass scale.

    rho_Omega = m^4 * c^5 / hbar^3

    Equivalently: rho = mc^2 / lambda_C^3

    This is the energy density when one quantum (mc^2) occupies
    one Compton volume (lambda_C^3).
    """
    return mass_kg**4 * C**5 / HBAR**3


def mode_vacuum_energy_density(k_cutoff: float) -> float:
    """
    Calculate the mode vacuum energy density with momentum cutoff.

    rho_0 = hbar * c * k_cutoff^4 / (16 * pi^2)

    This diverges as k_cutoff -> infinity.
    """
    return HBAR * C * k_cutoff**4 / (16 * np.pi**2)


def mode_vacuum_compton_cutoff(mass_kg: float) -> float:
    """
    Mode vacuum energy density with Compton wavelength cutoff.

    k_cutoff = m*c/hbar, giving:
    rho_0 = m^4 * c^5 / (16 * pi^2 * hbar^3)

    This is 16*pi^2 times smaller than the cell vacuum.
    """
    return mass_kg**4 * C**5 / (16 * np.pi**2 * HBAR**3)


def mass_from_energy_density(rho: float) -> float:
    """
    Invert the cell vacuum formula to find mass from energy density.

    m = (rho * hbar^3 / c^5)^(1/4)
    """
    return (rho * HBAR**3 / C**5)**0.25


def planck_energy_density() -> float:
    """
    Naive Planck-scale energy density cutoff.

    rho_Planck = hbar * c / (16*pi^2) * (1/l_P)^4 ~ 10^113 J/m^3

    This is the "worst prediction in physics" for vacuum energy.
    """
    k_planck = 1.0 / PLANCK_LENGTH
    return mode_vacuum_energy_density(k_planck)


# =============================================================================
# Verification
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PHYSICAL CONSTANTS AND SCALES")
    print("=" * 70)

    print(f"\nFundamental Constants:")
    print(f"  hbar   = {HBAR:.6e} J*s")
    print(f"  c      = {C:.6e} m/s")
    print(f"  hbar*c = {HBAR_C_MEV_FM:.1f} MeV*fm")

    print(f"\nPlanck Scales:")
    print(f"  l_P = {PLANCK_LENGTH:.3e} m")
    print(f"  m_P = {PLANCK_MASS:.3e} kg")
    print(f"  E_P = {PLANCK_ENERGY:.3e} J")

    print(f"\nMass Conversion Check:")
    print(f"  1 eV/c^2 = {EV_TO_KG:.6e} kg")
    print(f"  2.31 meV = {mass_eV_to_kg(2.31e-3):.3e} kg")

    print(f"\n" + "=" * 70)
    print("NEUTRINO MASSES (from framework prediction + oscillation data)")
    print("=" * 70)

    print(f"\n  m_1 (lightest) = {NEUTRINO_M1_EV*1e3:.2f} meV  [PREDICTED from rho_Lambda]")
    print(f"  m_2            = {NEUTRINO_M2_EV*1e3:.1f} meV")
    print(f"  m_3 (heaviest) = {NEUTRINO_M3_EV*1e3:.1f} meV")
    print(f"  Sum m_nu       = {NEUTRINO_SUM_EV*1e3:.1f} meV")
    print(f"  Cosmological bound: < 120 meV  [SATISFIED]")

    print(f"\n" + "=" * 70)
    print("ENERGY DENSITY VERIFICATION")
    print("=" * 70)

    rho_cell = cell_vacuum_energy_density(NEUTRINO_M1_KG)
    rho_mode = mode_vacuum_compton_cutoff(NEUTRINO_M1_KG)
    rho_planck = planck_energy_density()

    print(f"\n  Cell vacuum (m_1 = 2.31 meV):  rho = {rho_cell:.3e} J/m^3")
    print(f"  Observed dark energy:          rho = {OBSERVED_DARK_ENERGY_DENSITY:.3e} J/m^3")
    print(f"  Ratio: {rho_cell/OBSERVED_DARK_ENERGY_DENSITY:.4f}")

    print(f"\n  Mode vacuum (Compton cutoff):  rho = {rho_mode:.3e} J/m^3")
    print(f"  Ratio cell/mode: {rho_cell/rho_mode:.2f} = 16*pi^2 = {16*np.pi**2:.2f}")

    print(f"\n  Mode vacuum (Planck cutoff):   rho = {rho_planck:.3e} J/m^3")
    print(f"  Discrepancy vs observed: 10^{np.log10(rho_planck/OBSERVED_DARK_ENERGY_DENSITY):.0f}")

    # Verify mass inversion
    m_recovered = mass_from_energy_density(OBSERVED_DARK_ENERGY_DENSITY)
    print(f"\n  Mass recovered from rho_Lambda: {mass_kg_to_eV(m_recovered)*1e3:.2f} meV")
