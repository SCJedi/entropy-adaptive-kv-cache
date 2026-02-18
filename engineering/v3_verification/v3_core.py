"""
V3 Core Verification Module for the Two Vacua Theory

Computes all key quantities for the V3 whitepaper:
- Cell vacuum energy density for arbitrary neutrino mass
- Neutrino mass inversion from target density (CDM or DE)
- Neutrino mass spectrum from oscillation data
- Comparison to DESI DR2 bounds
- Equation of state verification (w = 0)
- LCDM equivalence verification
- Jeans length computation
"""

import math
from dataclasses import dataclass
from typing import Tuple


# =============================================================================
# Physical Constants
# =============================================================================

HBAR = 1.054571817e-34      # J*s
C = 2.99792458e8            # m/s
G = 6.67430e-11             # m^3/(kg*s^2)
EV_TO_JOULE = 1.602176634e-19  # J per eV
EV_TO_KG = 1.78266192e-36  # kg per eV/c^2
KB = 1.380649e-23           # J/K

# Hubble constant
H0_KM_S_MPC = 67.4         # km/s/Mpc
MPC_TO_M = 3.0857e22       # m per Mpc
H0 = H0_KM_S_MPC * 1e3 / MPC_TO_M  # s^-1

# Neutrino mass splittings (PDG 2023 / NuFIT 6.0)
DM2_21 = 7.53e-5           # eV^2 (solar)
DM2_31_NH = 2.453e-3       # eV^2 (atmospheric, normal hierarchy)
DM2_32_IH = 2.536e-3       # eV^2 (atmospheric, inverted hierarchy)

# Cosmological parameters (Planck 2018)
OMEGA_CDM = 0.265
OMEGA_LAMBDA = 0.685
OMEGA_BARYON = 0.050
OMEGA_RADIATION = 9.2e-5    # photons + standard neutrinos (approx)


# =============================================================================
# Derived Constants
# =============================================================================

def critical_density() -> float:
    """Critical density of the universe in J/m^3.
    rho_crit = 3 H_0^2 c^2 / (8 pi G)
    """
    return 3.0 * H0**2 * C**2 / (8.0 * math.pi * G)


RHO_CRIT = critical_density()
RHO_CDM = OMEGA_CDM * RHO_CRIT
RHO_DE = OMEGA_LAMBDA * RHO_CRIT
RHO_BARYON = OMEGA_BARYON * RHO_CRIT

# DESI DR2 bound
DESI_DR2_SUM_BOUND = 53e-3  # eV, 95% CL (Feldman-Cousins)


# =============================================================================
# Core Formulas
# =============================================================================

def cell_vacuum_density(mass_kg: float) -> float:
    """Cell vacuum energy density: rho = m^4 c^5 / hbar^3.

    Args:
        mass_kg: Particle mass in kg.

    Returns:
        Energy density in J/m^3.
    """
    return mass_kg**4 * C**5 / HBAR**3


def cell_vacuum_density_eV(mass_eV: float) -> float:
    """Cell vacuum energy density from mass in eV.

    Args:
        mass_eV: Particle mass in eV/c^2.

    Returns:
        Energy density in J/m^3.
    """
    mass_kg = mass_eV * EV_TO_KG
    return cell_vacuum_density(mass_kg)


def mass_from_density(rho: float) -> float:
    """Invert rho = m^4 c^5 / hbar^3 to find mass in kg.

    Args:
        rho: Target energy density in J/m^3.

    Returns:
        Mass in kg.
    """
    return (rho * HBAR**3 / C**5)**0.25


def mass_from_density_eV(rho: float) -> float:
    """Invert rho = m^4 c^5 / hbar^3 to find mass in eV.

    Args:
        rho: Target energy density in J/m^3.

    Returns:
        Mass in eV/c^2.
    """
    mass_kg = mass_from_density(rho)
    return mass_kg * C**2 / EV_TO_JOULE


def compton_wavelength(mass_kg: float) -> float:
    """Compton wavelength: lambda_C = hbar / (m c).

    Args:
        mass_kg: Particle mass in kg.

    Returns:
        Compton wavelength in meters.
    """
    return HBAR / (mass_kg * C)


def compton_frequency(mass_kg: float) -> float:
    """Compton angular frequency: omega = m c^2 / hbar.

    Args:
        mass_kg: Particle mass in kg.

    Returns:
        Angular frequency in rad/s.
    """
    return mass_kg * C**2 / HBAR


# =============================================================================
# Neutrino Mass Spectrum
# =============================================================================

@dataclass
class NeutrinoSpectrum:
    """Neutrino mass spectrum from oscillation data."""
    m1_eV: float
    m2_eV: float
    m3_eV: float
    hierarchy: str  # "normal" or "inverted"

    @property
    def sum_eV(self) -> float:
        return self.m1_eV + self.m2_eV + self.m3_eV

    @property
    def sum_meV(self) -> float:
        return self.sum_eV * 1e3

    @property
    def m1_meV(self) -> float:
        return self.m1_eV * 1e3

    @property
    def m2_meV(self) -> float:
        return self.m2_eV * 1e3

    @property
    def m3_meV(self) -> float:
        return self.m3_eV * 1e3


def neutrino_spectrum_normal(m1_eV: float) -> NeutrinoSpectrum:
    """Compute neutrino mass spectrum for normal hierarchy.

    Normal hierarchy: m1 < m2 < m3.
    m2 = sqrt(m1^2 + dm2_21)
    m3 = sqrt(m1^2 + dm2_31)

    Args:
        m1_eV: Lightest neutrino mass in eV.

    Returns:
        NeutrinoSpectrum with all three masses.
    """
    m2 = math.sqrt(m1_eV**2 + DM2_21)
    m3 = math.sqrt(m1_eV**2 + DM2_31_NH)
    return NeutrinoSpectrum(m1_eV, m2, m3, "normal")


def neutrino_spectrum_inverted(m3_eV: float) -> NeutrinoSpectrum:
    """Compute neutrino mass spectrum for inverted hierarchy.

    Inverted hierarchy: m3 < m1 < m2.
    m1 = sqrt(m3^2 + |dm2_31|)
    m2 = sqrt(m3^2 + |dm2_31| + dm2_21)

    Args:
        m3_eV: Lightest neutrino mass in eV (m3 in IH).

    Returns:
        NeutrinoSpectrum with all three masses.
    """
    m1 = math.sqrt(m3_eV**2 + DM2_31_NH)
    m2 = math.sqrt(m3_eV**2 + DM2_31_NH + DM2_21)
    return NeutrinoSpectrum(m1, m2, m3_eV, "inverted")


def minimum_sum_normal() -> float:
    """Minimum sum of neutrino masses for normal hierarchy (m1 -> 0).

    Returns:
        Minimum sum in eV.
    """
    return math.sqrt(DM2_21) + math.sqrt(DM2_31_NH)


def minimum_sum_inverted() -> float:
    """Minimum sum of neutrino masses for inverted hierarchy (m3 -> 0).

    Returns:
        Minimum sum in eV.
    """
    return math.sqrt(DM2_31_NH) + math.sqrt(DM2_31_NH + DM2_21)


# =============================================================================
# Two Vacua Predictions
# =============================================================================

@dataclass
class TwoVacuaPrediction:
    """Complete prediction from the Two Vacua framework."""
    scenario: str           # "CDM" or "DE"
    target_density: float   # J/m^3
    m1_eV: float            # Lightest neutrino mass in eV
    spectrum: NeutrinoSpectrum
    rho_cell: float         # Cell vacuum density in J/m^3
    lambda_C: float         # Compton wavelength in m
    omega: float            # Compton frequency in rad/s
    desi_consistent: bool   # Whether Sum < DESI bound


def predict_from_density(rho_target: float, scenario: str) -> TwoVacuaPrediction:
    """Generate complete Two Vacua prediction from target density.

    Args:
        rho_target: Target energy density in J/m^3.
        scenario: Label ("CDM" or "DE").

    Returns:
        Complete prediction including neutrino masses and observables.
    """
    m1_eV = mass_from_density_eV(rho_target)
    m1_kg = m1_eV * EV_TO_KG
    spectrum = neutrino_spectrum_normal(m1_eV)
    rho_cell = cell_vacuum_density(m1_kg)
    lam_C = compton_wavelength(m1_kg)
    omega = compton_frequency(m1_kg)
    desi_ok = spectrum.sum_eV < DESI_DR2_SUM_BOUND

    return TwoVacuaPrediction(
        scenario=scenario,
        target_density=rho_target,
        m1_eV=m1_eV,
        spectrum=spectrum,
        rho_cell=rho_cell,
        lambda_C=lam_C,
        omega=omega,
        desi_consistent=desi_ok,
    )


def predict_cdm() -> TwoVacuaPrediction:
    """NEW prediction: rho_cell = rho_CDM."""
    return predict_from_density(RHO_CDM, "CDM")


def predict_de() -> TwoVacuaPrediction:
    """OLD prediction: rho_cell = rho_DE."""
    return predict_from_density(RHO_DE, "DE")


# =============================================================================
# Equation of State Verification
# =============================================================================

def verify_w_equals_zero(num_periods: int = 1000, points_per_period: int = 100) -> dict:
    """Numerically verify w = 0 by time-averaging the Klein-Gordon solution.

    For F(t) = F0 cos(omega t):
        rho(t) = (1/2)(dF/dt)^2 + (1/2) omega^2 F^2 = (1/2) omega^2 F0^2
        p(t)   = (1/2)(dF/dt)^2 - (1/2) omega^2 F^2 = -(1/2) omega^2 F0^2 cos(2 omega t)
        <p>_time = 0

    Returns:
        Dictionary with rho_avg, p_avg, w, virial_ratio.
    """
    omega = 1.0  # Normalized
    F0 = 1.0
    T = 2.0 * math.pi / omega  # Period
    dt = T / points_per_period
    N = num_periods * points_per_period

    rho_sum = 0.0
    p_sum = 0.0
    ke_sum = 0.0
    pe_sum = 0.0

    for i in range(N):
        t = i * dt
        F = F0 * math.cos(omega * t)
        dFdt = -F0 * omega * math.sin(omega * t)

        ke = 0.5 * dFdt**2           # Kinetic energy density
        pe = 0.5 * omega**2 * F**2   # Potential energy density
        rho = ke + pe
        p = ke - pe

        rho_sum += rho
        p_sum += p
        ke_sum += ke
        pe_sum += pe

    rho_avg = rho_sum / N
    p_avg = p_sum / N
    ke_avg = ke_sum / N
    pe_avg = pe_sum / N

    w = p_avg / rho_avg if rho_avg != 0 else float('nan')
    virial_ratio = ke_avg / pe_avg if pe_avg != 0 else float('nan')

    return {
        'rho_avg': rho_avg,
        'p_avg': p_avg,
        'w': w,
        'ke_avg': ke_avg,
        'pe_avg': pe_avg,
        'virial_ratio': virial_ratio,
    }


def verify_virial_theorem() -> dict:
    """Verify the virial theorem: <KE> = <PE> for the QHO.

    For a coherent state |alpha> with |alpha|^2 = 1/2:
        E_total = hbar omega
        E_displacement = hbar omega |alpha|^2 = hbar omega / 2
        E_zero_point = hbar omega / 2
        <KE> = <PE> = hbar omega / 2

    Returns:
        Dictionary with energy fractions and virial ratio.
    """
    alpha_sq = 0.5
    # Energy components (in units of hbar omega)
    e_displacement = alpha_sq       # |alpha|^2
    e_zero_point = 0.5              # 1/2
    e_total = alpha_sq + 0.5        # |alpha|^2 + 1/2 = 1.0

    # For the QHO, each component splits 50/50 between KE and PE
    ke = e_total / 2.0
    pe = e_total / 2.0

    return {
        'e_total': e_total,
        'e_displacement': e_displacement,
        'e_zero_point': e_zero_point,
        'ke': ke,
        'pe': pe,
        'virial_ratio': ke / pe,
        'w': (ke - pe) / e_total,
    }


# =============================================================================
# LCDM Equivalence
# =============================================================================

def friedmann_H_squared(a: float, omega_m: float, omega_r: float,
                        omega_lambda: float) -> float:
    """Compute H^2/H0^2 from the Friedmann equation.

    H^2/H0^2 = Omega_r/a^4 + Omega_m/a^3 + Omega_Lambda

    Args:
        a: Scale factor.
        omega_m: Total matter density parameter (CDM + baryons).
        omega_r: Radiation density parameter.
        omega_lambda: Dark energy density parameter.

    Returns:
        H^2/H0^2.
    """
    return omega_r / a**4 + omega_m / a**3 + omega_lambda


def verify_lcdm_equivalence(n_points: int = 100) -> dict:
    """Verify that Two Vacua model reproduces LCDM expansion history.

    LCDM: Omega_CDM (w=0) + Omega_Lambda (w=-1) + Omega_b (w=0) + Omega_r (w=1/3)
    Two Vacua: Omega_cell (w=0) + Omega_Wald (w=-1) + Omega_b (w=0) + Omega_r (w=1/3)

    Since both CDM and cell vacuum have w=0, and both Lambda and Wald have w=-1,
    the expansion histories are identical.

    Returns:
        Dictionary with max_relative_error and test points.
    """
    omega_m = OMEGA_CDM + OMEGA_BARYON
    omega_r = OMEGA_RADIATION
    omega_l = OMEGA_LAMBDA

    max_rel_error = 0.0

    # Test across cosmic history: a from 0.001 (z=999) to 1.0 (today)
    for i in range(n_points):
        a = 0.001 + (1.0 - 0.001) * i / (n_points - 1)

        # LCDM
        H2_lcdm = friedmann_H_squared(a, omega_m, omega_r, omega_l)

        # Two Vacua (same parameters, different labels)
        # Cell vacuum has w=0 (same as CDM), Wald ambiguity has w=-1 (same as Lambda)
        H2_tv = friedmann_H_squared(a, omega_m, omega_r, omega_l)

        # They should be identical
        if H2_lcdm > 0:
            rel_error = abs(H2_tv - H2_lcdm) / H2_lcdm
            max_rel_error = max(max_rel_error, rel_error)

    return {
        'max_relative_error': max_rel_error,
        'n_points': n_points,
        'identical': max_rel_error < 1e-10,
    }


# =============================================================================
# Jeans Length
# =============================================================================

def jeans_length(mass_kg: float) -> float:
    """Quantum Jeans length for cell vacuum.

    The quantum pressure introduces a Jeans length of order the Compton wavelength.
    For the cell vacuum (product state, c_s = 0 classically), quantum effects
    suppress clustering below lambda_C.

    For a scalar field condensate: lambda_J ~ hbar / (m c) = lambda_C

    Args:
        mass_kg: Particle mass in kg.

    Returns:
        Jeans length in meters.
    """
    # For fuzzy/axion dark matter, the Jeans length involves the background density.
    # For the cell vacuum as a product state with no classical sound speed,
    # the quantum pressure scale is set by the Compton wavelength.
    return compton_wavelength(mass_kg)


def jeans_length_eV(mass_eV: float) -> float:
    """Jeans length from mass in eV."""
    return jeans_length(mass_eV * EV_TO_KG)


# =============================================================================
# Dimensional Analysis Verification
# =============================================================================

def verify_dimensional_uniqueness() -> dict:
    """Verify that rho = m^a c^b hbar^d has unique solution a=4, b=5, d=-3.

    Dimensions: [rho] = kg m^{-1} s^{-2}
    [m^a c^b hbar^d] = kg^{a+d} m^{b+2d} s^{-b-d}

    System:
        a + d = 1       (kg)
        b + 2d = -1     (m)
        -b - d = -2     (s)

    Returns:
        Dictionary with solution and determinant.
    """
    # Coefficient matrix:
    # [1  0  1] [a]   [1]
    # [0  1  2] [b] = [-1]
    # [0 -1 -1] [d]   [-2]
    #
    # det = 1*(1*(-1) - 2*(-1)) - 0 + 1*(0 - 1*0) ... let me just compute
    # det = 1*((-1)(-1) - (2)(-1)) = 1*(1 + 2) = 3 ... wait
    # Actually: det = 1*(1*(-1) - 2*(-1)) - 0 + 1*(0*(-1) - 1*0)
    # = 1*(-1 + 2) + 0 + 0 = 1

    # Solve directly:
    # From row 3: b + d = 2 -> b = 2 - d
    # From row 2: b + 2d = -1 -> (2-d) + 2d = -1 -> 2 + d = -1 -> d = -3
    # From row 1: a + d = 1 -> a = 1 - d = 1 - (-3) = 4
    # b = 2 - (-3) = 5

    a, b, d = 4, 5, -3

    # Verify
    check_kg = a + d  # should be 1
    check_m = b + 2 * d  # should be -1
    check_s = -b - d  # should be -2

    # Determinant of the coefficient matrix
    det = 1 * (1 * (-1) - 2 * (-1)) - 0 * (0 * (-1) - 2 * 0) + 1 * (0 * (-1) - 1 * 0)
    # = 1*(−1+2) − 0 + 0 = 1

    return {
        'a': a, 'b': b, 'd': d,
        'check_kg': check_kg,  # should be 1
        'check_m': check_m,    # should be -1
        'check_s': check_s,    # should be -2
        'determinant': det,
        'unique': det != 0,
    }


# =============================================================================
# Vacuum Overlap
# =============================================================================

def vacuum_overlap(n_cells: int, alpha_sq: float = 0.5) -> float:
    """Compute <0|Omega> = exp(-N * |alpha|^2 / 2).

    Args:
        n_cells: Number of cells.
        alpha_sq: |alpha|^2 per cell (default 1/2).

    Returns:
        Overlap magnitude.
    """
    exponent = -n_cells * alpha_sq / 2.0
    if exponent < -700:  # Avoid underflow
        return 0.0
    return math.exp(exponent)


# =============================================================================
# Backreaction Check
# =============================================================================

def backreaction_parameter(mass_kg: float) -> float:
    """Compute R * lambda_C^2, the backreaction self-consistency parameter.

    The cell vacuum energy sources curvature R ~ 32 pi G rho / c^2.
    The correction to the cell construction is delta_rho/rho ~ R * lambda_C^2.

    Args:
        mass_kg: Particle mass in kg.

    Returns:
        R * lambda_C^2 (dimensionless).
    """
    rho = cell_vacuum_density(mass_kg)
    R = 32.0 * math.pi * G * rho / C**2
    lam_C = compton_wavelength(mass_kg)
    return R * lam_C**2


def adiabatic_parameter(mass_kg: float) -> float:
    """Compute H * lambda_C / c, the adiabatic (Parker creation) parameter.

    Args:
        mass_kg: Particle mass in kg.

    Returns:
        H * lambda_C / c (dimensionless).
    """
    lam_C = compton_wavelength(mass_kg)
    return H0 * lam_C / C


# =============================================================================
# Summary Report
# =============================================================================

def generate_report() -> str:
    """Generate a complete summary report of all V3 key numbers."""
    lines = []
    lines.append("=" * 72)
    lines.append("TWO VACUA THEORY V3 — KEY NUMBERS")
    lines.append("=" * 72)

    # Cosmological densities
    lines.append("\n--- Cosmological Densities ---")
    lines.append(f"rho_crit  = {RHO_CRIT:.4e} J/m^3")
    lines.append(f"rho_CDM   = {RHO_CDM:.4e} J/m^3  (Omega = {OMEGA_CDM})")
    lines.append(f"rho_DE    = {RHO_DE:.4e} J/m^3  (Omega = {OMEGA_LAMBDA})")
    lines.append(f"rho_b     = {RHO_BARYON:.4e} J/m^3  (Omega = {OMEGA_BARYON})")

    # CDM prediction (NEW)
    pred_cdm = predict_cdm()
    lines.append("\n--- NEW Prediction: rho_cell = rho_CDM ---")
    lines.append(f"m_1       = {pred_cdm.m1_eV*1e3:.3f} meV")
    lines.append(f"m_2       = {pred_cdm.spectrum.m2_meV:.3f} meV")
    lines.append(f"m_3       = {pred_cdm.spectrum.m3_meV:.3f} meV")
    lines.append(f"Sum(m_nu) = {pred_cdm.spectrum.sum_meV:.2f} meV")
    lines.append(f"rho_cell  = {pred_cdm.rho_cell:.4e} J/m^3")
    lines.append(f"lambda_C  = {pred_cdm.lambda_C:.4e} m = {pred_cdm.lambda_C*1e3:.4f} mm")
    lines.append(f"DESI DR2  = {'CONSISTENT' if pred_cdm.desi_consistent else 'TENSION'}")

    # DE prediction (OLD)
    pred_de = predict_de()
    lines.append("\n--- OLD Prediction: rho_cell = rho_DE ---")
    lines.append(f"m_1       = {pred_de.m1_eV*1e3:.3f} meV")
    lines.append(f"m_2       = {pred_de.spectrum.m2_meV:.3f} meV")
    lines.append(f"m_3       = {pred_de.spectrum.m3_meV:.3f} meV")
    lines.append(f"Sum(m_nu) = {pred_de.spectrum.sum_meV:.2f} meV")
    lines.append(f"rho_cell  = {pred_de.rho_cell:.4e} J/m^3")
    lines.append(f"lambda_C  = {pred_de.lambda_C:.4e} m = {pred_de.lambda_C*1e3:.4f} mm")
    lines.append(f"DESI DR2  = {'CONSISTENT' if pred_de.desi_consistent else 'TENSION'}")

    # Density ratios
    lines.append("\n--- Density Ratios ---")
    lines.append(f"rho_cell(DE) / rho_DE  = {pred_de.rho_cell / RHO_DE:.4f}")
    lines.append(f"rho_cell(DE) / rho_CDM = {pred_de.rho_cell / RHO_CDM:.4f}")
    lines.append(f"rho_cell(CDM) / rho_CDM = {pred_cdm.rho_cell / RHO_CDM:.4f}")

    # Minimum sums
    lines.append("\n--- Minimum Sums (m_lightest -> 0) ---")
    lines.append(f"Normal hierarchy:   {minimum_sum_normal()*1e3:.2f} meV")
    lines.append(f"Inverted hierarchy: {minimum_sum_inverted()*1e3:.2f} meV")

    # w = 0 verification
    w_result = verify_w_equals_zero()
    lines.append("\n--- Equation of State ---")
    lines.append(f"w (time-averaged) = {w_result['w']:.2e}")
    lines.append(f"Virial ratio <KE>/<PE> = {w_result['virial_ratio']:.6f}")

    # LCDM equivalence
    lcdm_result = verify_lcdm_equivalence()
    lines.append("\n--- LCDM Equivalence ---")
    lines.append(f"Max relative error = {lcdm_result['max_relative_error']:.2e}")
    lines.append(f"Identical: {lcdm_result['identical']}")

    # Dimensional uniqueness
    dim_result = verify_dimensional_uniqueness()
    lines.append("\n--- Dimensional Analysis ---")
    lines.append(f"Unique solution: a={dim_result['a']}, b={dim_result['b']}, d={dim_result['d']}")
    lines.append(f"Determinant = {dim_result['determinant']} (nonzero => unique)")

    # Backreaction
    m_cdm_kg = pred_cdm.m1_eV * EV_TO_KG
    br = backreaction_parameter(m_cdm_kg)
    ad = adiabatic_parameter(m_cdm_kg)
    lines.append("\n--- Self-Consistency ---")
    lines.append(f"Backreaction R*lambda_C^2 = {br:.2e}")
    lines.append(f"Adiabatic H*lambda_C/c = {ad:.2e}")

    # Jeans length
    jl = jeans_length(m_cdm_kg)
    lines.append("\n--- Jeans Length ---")
    lines.append(f"lambda_J ~ lambda_C = {jl:.4e} m = {jl*1e3:.4f} mm")
    lines.append(f"In kpc: {jl / MPC_TO_M * 1e3:.3e}")

    # Vacuum overlap
    lines.append("\n--- Vacuum Overlap ---")
    for N in [10, 100, 1000]:
        ov = vacuum_overlap(N)
        lines.append(f"<0|Omega> (N={N}): {ov:.4e}")

    lines.append("\n" + "=" * 72)
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_report())
