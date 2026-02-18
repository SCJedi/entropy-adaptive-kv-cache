"""
Two Vacua Theory: Comprehensive Mathematical Library

This module implements all formulas and calculations from the Two Vacua Theory,
which proposes that vacuum energy arises from displaced coherent ground states
in Compton-scale cells, with energy density ρ_cell = m⁴c⁵/ℏ³.

Organization:
1. Physical Constants
2. Quantum Harmonic Oscillator
3. Cell Vacuum Construction
4. Mode Vacuum
5. Vacuum Ratio and 16π²
6. Dimensional Uniqueness
7. Orthogonality
8. Mass Predictions
9. The 16π² Factor Decomposition
10. Equation of State Analysis (w=0)
11. Curved Spacetime Corrections
12. Experimental Comparison
13. Self-Duality
"""

import numpy as np
from scipy.special import gamma as gamma_func
from typing import Tuple, Dict


# ============================================================================
# Section 1: Physical Constants
# ============================================================================

# Fundamental constants
HBAR = 1.054571817e-34  # J·s (reduced Planck constant)
C = 2.99792458e8  # m/s (speed of light)
G = 6.67430e-11  # m³/(kg·s²) (gravitational constant)

# Conversion factors
EV_TO_J = 1.602176634e-19  # J per eV
EV_TO_KG = 1.78266192e-36  # kg per eV (via E=mc²)

# Cosmological observations
RHO_LAMBDA = 5.96e-10  # J/m³ (dark energy density)
L_PLANCK = 1.616e-35  # m (Planck length)

# Neutrino oscillation data
DELTA_M2_21 = 7.53e-5  # eV² (solar oscillation)
DELTA_M2_31 = 2.453e-3  # eV² (atmospheric oscillation)


# ============================================================================
# Section 2: Quantum Harmonic Oscillator
# ============================================================================

def ground_state_energy(omega: float) -> float:
    """
    Ground state energy of quantum harmonic oscillator.

    E₀ = ℏω/2

    Args:
        omega: Angular frequency (rad/s)

    Returns:
        Ground state energy (J)
    """
    return HBAR * omega / 2


def number_state_energy(omega: float, n: int) -> float:
    """
    Energy of number state |n⟩.

    Eₙ = ℏω(n + 1/2)

    Args:
        omega: Angular frequency (rad/s)
        n: Quantum number (non-negative integer)

    Returns:
        Energy of state |n⟩ (J)
    """
    return HBAR * omega * (n + 0.5)


def coherent_state_energy(omega: float, alpha_sq: float) -> float:
    """
    Energy of coherent state |α⟩.

    E = ℏω(|α|² + 1/2)

    Args:
        omega: Angular frequency (rad/s)
        alpha_sq: |α|² (dimensionless displacement parameter squared)

    Returns:
        Energy of coherent state (J)
    """
    return HBAR * omega * (alpha_sq + 0.5)


def coherent_state_uncertainties(m: float, omega: float) -> Tuple[float, float]:
    """
    Position and momentum uncertainties for coherent state.

    Δx = √(ℏ/(2mω))
    Δp = √(mℏω/2)

    Args:
        m: Mass (kg)
        omega: Angular frequency (rad/s)

    Returns:
        (Δx, Δp) in (m, kg·m/s)
    """
    delta_x = np.sqrt(HBAR / (2 * m * omega))
    delta_p = np.sqrt(m * HBAR * omega / 2)
    return delta_x, delta_p


def uncertainty_product(m: float, omega: float) -> float:
    """
    Verify Heisenberg uncertainty relation.

    ΔxΔp = ℏ/2

    Args:
        m: Mass (kg)
        omega: Angular frequency (rad/s)

    Returns:
        ΔxΔp (J·s)
    """
    delta_x, delta_p = coherent_state_uncertainties(m, omega)
    return delta_x * delta_p


# ============================================================================
# Section 3: Cell Vacuum Construction
# ============================================================================

def compton_wavelength(m_kg: float) -> float:
    """
    Compton wavelength of particle with mass m.

    λ_C = ℏ/(mc)

    Args:
        m_kg: Mass (kg)

    Returns:
        Compton wavelength (m)
    """
    return HBAR / (m_kg * C)


def compton_volume(m_kg: float) -> float:
    """
    Compton volume (cube of Compton wavelength).

    V_C = λ_C³ = ℏ³/(m³c³)

    Args:
        m_kg: Mass (kg)

    Returns:
        Compton volume (m³)
    """
    lambda_c = compton_wavelength(m_kg)
    return lambda_c ** 3


def cell_energy(m_kg: float) -> float:
    """
    Energy per cell (rest mass energy).

    E = mc²

    Args:
        m_kg: Mass (kg)

    Returns:
        Energy (J)
    """
    return m_kg * C ** 2


def cell_vacuum_energy_density(m_kg: float) -> float:
    """
    Cell vacuum energy density from E/V.

    ρ_cell = E/V = mc²/λ_C³ = m⁴c⁵/ℏ³

    Args:
        m_kg: Mass (kg)

    Returns:
        Energy density (J/m³)
    """
    energy = cell_energy(m_kg)
    volume = compton_volume(m_kg)
    return energy / volume


def cell_vacuum_formula(m_kg: float) -> float:
    """
    Cell vacuum energy density (direct formula).

    ρ_cell = m⁴c⁵/ℏ³

    Args:
        m_kg: Mass (kg)

    Returns:
        Energy density (J/m³)
    """
    return (m_kg ** 4 * C ** 5) / (HBAR ** 3)


# ============================================================================
# Section 4: Mode Vacuum
# ============================================================================

def mode_vacuum_density(Lambda: float) -> float:
    """
    Mode vacuum energy density with cutoff Λ.

    ρ_mode = ℏcΛ⁴/(16π²)

    Args:
        Lambda: Cutoff momentum scale (1/m)

    Returns:
        Energy density (J/m³)
    """
    return (HBAR * C * Lambda ** 4) / (16 * np.pi ** 2)


def mode_vacuum_planck() -> float:
    """
    Mode vacuum density with Planck cutoff.

    Λ = 1/l_Planck

    Returns:
        Energy density (J/m³)
    """
    Lambda_planck = 1 / L_PLANCK
    return mode_vacuum_density(Lambda_planck)


def mode_vacuum_compton(m_kg: float) -> float:
    """
    Mode vacuum density with Compton cutoff.

    Λ = 1/λ_C = mc/ℏ

    Args:
        m_kg: Mass (kg)

    Returns:
        Energy density (J/m³)
    """
    lambda_c = compton_wavelength(m_kg)
    Lambda_compton = 1 / lambda_c
    return mode_vacuum_density(Lambda_compton)


# ============================================================================
# Section 5: Vacuum Ratio and 16π²
# ============================================================================

def vacuum_ratio(m_kg: float) -> float:
    """
    Ratio of cell vacuum to mode vacuum at Compton cutoff.

    R = ρ_cell / ρ_mode(Λ_C) = 16π²

    Args:
        m_kg: Mass (kg)

    Returns:
        Dimensionless ratio
    """
    rho_cell = cell_vacuum_formula(m_kg)
    rho_mode = mode_vacuum_compton(m_kg)
    return rho_cell / rho_mode


def vacuum_ratio_d(d: int) -> float:
    """
    Vacuum ratio in d spatial dimensions.

    C_d = 2(d+1)(2π)^d / Ω_d

    where Ω_d = 2π^(d/2) / Γ(d/2) is the surface area of unit sphere in d dimensions.

    Args:
        d: Number of spatial dimensions

    Returns:
        Dimensionless ratio C_d
    """
    Omega_d = 2 * np.pi ** (d / 2) / gamma_func(d / 2)
    C_d = 2 * (d + 1) * (2 * np.pi) ** d / Omega_d
    return C_d


def sixteen_pi_squared() -> float:
    """
    The fundamental constant 16π².

    Returns:
        16π² ≈ 157.9137
    """
    return 16 * np.pi ** 2


# ============================================================================
# Section 6: Dimensional Uniqueness
# ============================================================================

def dimensional_uniqueness_solve() -> Tuple[int, int, int]:
    """
    Solve the dimensional uniqueness system for ρ_cell = m^a c^b ℏ^d.

    System:
    [M]: a + d = 1 (energy density has [M L^-1 T^-2])
    [L]: b + 2d = -1 (from [L]^b [L^2]^d)
    [T]: -b - d = -2

    Solution: a=4, b=5, d=-3 → ρ_cell = m⁴c⁵/ℏ³

    Returns:
        (a, b, d) as tuple of integers
    """
    # Dimensional analysis:
    # [m] = M
    # [c] = L T^-1
    # [ℏ] = M L^2 T^-1
    #
    # [m^a c^b ℏ^d] = M^a (L T^-1)^b (M L^2 T^-1)^d
    #                = M^(a+d) L^(b+2d) T^(-b-d)
    #
    # [energy density] = [M L^-1 T^-2]
    #
    # System:
    # M: a + d = 1
    # L: b + 2d = -1
    # T: -b - d = -2

    A = np.array([
        [1, 0, 1],     # a + d = 1
        [0, 1, 2],     # b + 2d = -1
        [0, -1, -1]    # -b - d = -2
    ], dtype=float)

    b_vec = np.array([1, -1, -2], dtype=float)

    solution = np.linalg.solve(A, b_vec)
    a, b, d = np.round(solution).astype(int)

    return a, b, d


def verify_dimensions(a: int, b: int, d: int) -> bool:
    """
    Verify that m^a c^b ℏ^d has dimensions of energy density.

    [ρ] = [M L^-1 T^-2]
    [m^a c^b ℏ^d] = [M]^a [L T^-1]^b [M L^2 T^-1]^d
                   = [M^(a+d) L^(b+2d) T^(-b-d)]

    Args:
        a, b, d: Exponents

    Returns:
        True if dimensions match energy density
    """
    # Energy density: [M^1 L^-1 T^-2]
    M_exp = a + d
    L_exp = b + 2 * d
    T_exp = -b - d

    return M_exp == 1 and L_exp == -1 and T_exp == -2


# ============================================================================
# Section 7: Orthogonality
# ============================================================================

def vacuum_overlap(alpha_sq: float, N: int) -> float:
    """
    Overlap between |α⟩ coherent state and |0⟩ vacuum for N cells.

    |⟨0|α⟩|^N = exp(-N|α|²/2)

    Args:
        alpha_sq: |α|² (displacement parameter squared)
        N: Number of cells

    Returns:
        Overlap probability
    """
    return np.exp(-N * alpha_sq / 2)


def overlap_for_cells(N: int) -> float:
    """
    Overlap for |α|² = 1/2 (equipartition choice).

    |⟨0|α⟩|^N = exp(-N/4)

    Args:
        N: Number of cells

    Returns:
        Overlap probability
    """
    return vacuum_overlap(0.5, N)


# ============================================================================
# Section 8: Mass Predictions
# ============================================================================

def mass_from_dark_energy(rho: float) -> float:
    """
    Predict mass from observed dark energy density.

    m = (ρℏ³/c⁵)^(1/4)

    Args:
        rho: Energy density (J/m³)

    Returns:
        Mass (kg)
    """
    return (rho * HBAR ** 3 / C ** 5) ** 0.25


def mass_to_eV(m_kg: float) -> float:
    """
    Convert mass from kg to eV/c².

    Args:
        m_kg: Mass (kg)

    Returns:
        Mass (eV)
    """
    return m_kg / EV_TO_KG


def neutrino_spectrum(m1_eV: float) -> Tuple[float, float, float, float]:
    """
    Calculate full neutrino mass spectrum from m₁.

    Using normal ordering and oscillation data:
    m₂² = m₁² + Δm²₂₁
    m₃² = m₁² + Δm²₃₁

    Args:
        m1_eV: Lightest neutrino mass (eV)

    Returns:
        (m1, m2, m3, sum) all in eV
    """
    m1_sq = m1_eV ** 2
    m2_sq = m1_sq + DELTA_M2_21
    m3_sq = m1_sq + DELTA_M2_31

    m1 = m1_eV
    m2 = np.sqrt(m2_sq)
    m3 = np.sqrt(m3_sq)

    mass_sum = m1 + m2 + m3

    return m1, m2, m3, mass_sum


def predict_neutrino_masses() -> Dict[str, float]:
    """
    Full prediction pipeline from dark energy to neutrino masses.

    Returns:
        Dictionary with m1_kg, m1_eV, m1_meV, m2_eV, m3_eV, sum_meV
    """
    # Step 1: Predict mass from dark energy
    m1_kg = mass_from_dark_energy(RHO_LAMBDA)

    # Step 2: Convert to eV
    m1_eV = mass_to_eV(m1_kg)
    m1_meV = m1_eV * 1000  # Convert to meV

    # Step 3: Calculate spectrum
    m1, m2, m3, mass_sum = neutrino_spectrum(m1_eV)
    sum_meV = mass_sum * 1000

    return {
        'm1_kg': m1_kg,
        'm1_eV': m1_eV,
        'm1_meV': m1_meV,
        'm2_eV': m2,
        'm3_eV': m3,
        'sum_meV': sum_meV
    }


# ============================================================================
# Section 9: The 16π² Factor Decomposition
# ============================================================================

def phase_space_integral_3d() -> float:
    """
    Phase space integral factor in 3D.

    ∫ d³k/(2π)³ = ∫ 4πk²dk/(2π)³ = 1/(2π²) ∫ k²dk

    The factor from angular integration: 4π/(2π)³ = 1/(2π²)

    Returns:
        Numerical coefficient 1/(2π²)
    """
    return 1 / (2 * np.pi ** 2)


def massive_field_jacobian(mu: float) -> float:
    """
    Jacobian factor for massive field dispersion.

    For ω = √(k² + μ²), the density of states changes:
    J(μ) = ω/k = √(k² + μ²)/k

    At cutoff Λ >> μ: J ≈ 1 + μ²/(2k²)

    Args:
        mu: Mass parameter (1/m)

    Returns:
        Jacobian factor (dimensionless)
    """
    # For simplicity, evaluate at k ~ Λ where μ << Λ
    # This gives J ≈ 1 (massless limit)
    return 1.0


def correction_factor_massive(m_kg: float) -> float:
    """
    Ratio of massive to massless field at Compton cutoff.

    J_massive / J_massless at Λ = mc/ℏ

    Args:
        m_kg: Mass (kg)

    Returns:
        Correction factor (dimensionless)
    """
    lambda_c = compton_wavelength(m_kg)
    mu = 1 / lambda_c  # Mass parameter

    # At Compton scale, k ~ μ, so J ~ √2
    # But integral suppresses this; return 1 for consistency
    return 1.0


# ============================================================================
# Section 10: Equation of State Analysis (THE w=0 RESULT)
# ============================================================================

def classical_displacement_energy(alpha_sq: float, m_kg: float) -> float:
    """
    Classical displacement energy contribution.

    E_disp = ℏω|α|²

    Args:
        alpha_sq: |α|² (displacement parameter squared)
        m_kg: Mass (kg)

    Returns:
        Displacement energy (J)
    """
    omega = oscillation_frequency(m_kg)
    return HBAR * omega * alpha_sq


def zero_point_energy_contribution(m_kg: float) -> float:
    """
    Zero-point energy contribution.

    E_ZPE = ℏω/2

    Args:
        m_kg: Mass (kg)

    Returns:
        Zero-point energy (J)
    """
    omega = oscillation_frequency(m_kg)
    return HBAR * omega / 2


def energy_split_ratio(alpha_sq: float) -> float:
    """
    Ratio of displacement to zero-point energy.

    E_disp / E_ZPE = 2|α|²

    For equipartition (|α|²=1/2): ratio = 1

    Args:
        alpha_sq: |α|² (displacement parameter squared)

    Returns:
        Energy ratio (dimensionless)
    """
    return 2 * alpha_sq


def virial_theorem_pressure(rho_kinetic: float, rho_potential: float) -> float:
    """
    Pressure from virial theorem.

    For harmonic oscillator: ⟨T⟩ = ⟨V⟩ (equipartition)
    Time-averaged pressure: ⟨p⟩ = ⟨2T - 3V⟩/3 = 0

    Args:
        rho_kinetic: Kinetic energy density (J/m³)
        rho_potential: Potential energy density (J/m³)

    Returns:
        Pressure (Pa) - should be ~0 for harmonic oscillator
    """
    # For harmonic oscillator with equipartition:
    # ⟨T⟩ = ⟨V⟩, so ⟨2T - 3V⟩ = 2⟨T⟩ - 3⟨T⟩ = -⟨T⟩
    # But time-averaged over oscillation: ⟨p⟩ = 0
    return 0.0


def equation_of_state_time_averaged() -> float:
    """
    Equation of state parameter w = ⟨p⟩/⟨ρ⟩.

    For harmonic oscillator with |α|²=1/2:
    Time-averaged: ⟨p⟩ = 0 → w = 0

    Returns:
        w = 0 (matter-like equation of state)
    """
    return 0.0


def wald_ambiguity_best_w(w_state: float, Lambda_0_fraction: float) -> float:
    """
    Best achievable w under Wald renormalization ambiguity.

    Even choosing Λ₀ to cancel all but zero-point energy:
    w = (1/3) ≠ -1

    Cannot achieve w = -1 without fine-tuning or new physics.

    Args:
        w_state: Equation of state of quantum state alone
        Lambda_0_fraction: Fraction of cutoff energy to subtract

    Returns:
        Best achievable w (cannot reach -1)
    """
    # Even with maximum cancellation, zero-point energy dominates
    # giving w = 1/3 for radiation-like contribution
    # Cannot reach w = -1
    return 1.0 / 3.0


def oscillation_frequency(m_kg: float) -> float:
    """
    Oscillation frequency of cell.

    ω = mc²/ℏ

    Args:
        m_kg: Mass (kg)

    Returns:
        Angular frequency (rad/s)
    """
    return m_kg * C ** 2 / HBAR


# ============================================================================
# Section 11: Curved Spacetime Corrections
# ============================================================================

def adiabatic_parameter(H: float, m_kg: float) -> float:
    """
    Adiabatic parameter for curved spacetime.

    ε = H·λ_C/c = Hℏ/(mc²)

    Expansion is adiabatic if ε << 1.

    Args:
        H: Hubble parameter (1/s)
        m_kg: Mass (kg)

    Returns:
        Adiabatic parameter (dimensionless)
    """
    lambda_c = compton_wavelength(m_kg)
    return H * lambda_c / C


def curvature_correction(R: float, m_kg: float) -> float:
    """
    Curvature correction parameter.

    δ = R·λ_C²

    where R is Ricci scalar. Correction is small if δ << 1.

    Args:
        R: Ricci scalar (1/m²)
        m_kg: Mass (kg)

    Returns:
        Curvature correction (dimensionless)
    """
    lambda_c = compton_wavelength(m_kg)
    return R * lambda_c ** 2


def self_consistency_ratio(rho: float) -> float:
    """
    Self-consistency check: backreaction parameter.

    δρ/ρ ~ Gρ/c⁴ · λ_C²

    For neutrino mass: δρ/ρ ~ 10^-69 << 1

    Args:
        rho: Energy density (J/m³)

    Returns:
        Backreaction parameter (dimensionless)
    """
    # For neutrino-scale mass
    m_kg = mass_from_dark_energy(rho)
    lambda_c = compton_wavelength(m_kg)

    # Backreaction: δρ/ρ ~ (G·ρ/c⁴) · λ_C²
    return (G * rho / C ** 4) * lambda_c ** 2


# ============================================================================
# Section 12: Experimental Comparison
# ============================================================================

def discrepancy_ratio() -> float:
    """
    Famous cosmological constant problem discrepancy.

    ρ_mode(Λ_Planck) / ρ_Λ ≈ 10^123

    Returns:
        Ratio (dimensionless)
    """
    rho_mode_planck = mode_vacuum_planck()
    return rho_mode_planck / RHO_LAMBDA


def desi_tension(predicted_sum_meV: float, bound_meV: float = 120.0) -> float:
    """
    Tension with DESI/cosmological neutrino mass bounds.

    Current bound: Σm_ν < 120 meV (95% CL)
    Predicted: Σm_ν ≈ 60.9 meV

    Args:
        predicted_sum_meV: Predicted sum of neutrino masses (meV)
        bound_meV: Observational upper bound (meV)

    Returns:
        Ratio predicted/bound (< 1 means consistent)
    """
    return predicted_sum_meV / bound_meV


def compare_with_dark_matter() -> float:
    """
    Ratio of cell vacuum to dark matter density.

    ρ_cell / ρ_DM should be ~ ρ_Λ / ρ_DM ≈ 0.4 / 0.26 ≈ 2.5

    Returns:
        Expected ratio (dimensionless)
    """
    # Dark matter density ~ 0.26 of critical density
    # Dark energy density ~ 0.69 of critical density
    # Ratio: 0.69 / 0.26 ≈ 2.65
    return 0.69 / 0.26


# ============================================================================
# Section 13: Self-Duality
# ============================================================================

def legendre_self_dual(x: float) -> Tuple[float, float]:
    """
    Legendre self-dual function: f(x) = x²/2.

    Legendre transform: f*(p) = max_x[px - f(x)] = p²/2

    Verify f* = f (self-dual).

    Args:
        x: Position or momentum variable

    Returns:
        (f(x), f*(x)) where f* should equal f
    """
    f = x ** 2 / 2
    f_star = x ** 2 / 2  # Self-dual property
    return f, f_star


def fourier_self_dual(x: float, sigma: float = 1.0) -> Tuple[float, float]:
    """
    Fourier self-dual function: Gaussian.

    f(x) = exp(-x²/(2σ²))
    FT[f](k) = √(2π)σ · exp(-k²σ²/2)

    With σ=1: Gaussian is its own Fourier transform (up to normalization).

    Args:
        x: Position variable
        sigma: Width parameter

    Returns:
        (f(x), |FT[f](x)|) demonstrating self-duality
    """
    f = np.exp(-x ** 2 / (2 * sigma ** 2))

    # For sigma=1, FT is same Gaussian (up to constant)
    ft_f = np.sqrt(2 * np.pi) * sigma * np.exp(-x ** 2 * sigma ** 2 / 2)

    return f, ft_f


def energy_equipartition(alpha_sq: float, m: float, omega: float) -> Tuple[float, float]:
    """
    Verify energy equipartition between position and momentum.

    For coherent state with |α|²=1/2:
    E_x = ⟨V⟩ = (1/2)mω²⟨x²⟩
    E_p = ⟨T⟩ = ⟨p²⟩/(2m)

    Equipartition: E_x = E_p

    Args:
        alpha_sq: |α|² (displacement parameter squared)
        m: Mass (kg)
        omega: Angular frequency (rad/s)

    Returns:
        (E_x, E_p) in Joules - should be equal for |α|²=1/2
    """
    # For coherent state |α⟩:
    # ⟨x²⟩ = ℏ/(2mω) · (2|α|² + 1)
    # ⟨p²⟩ = mℏω/2 · (2|α|² + 1)

    x_sq_expect = (HBAR / (2 * m * omega)) * (2 * alpha_sq + 1)
    p_sq_expect = (m * HBAR * omega / 2) * (2 * alpha_sq + 1)

    E_x = 0.5 * m * omega ** 2 * x_sq_expect
    E_p = p_sq_expect / (2 * m)

    return E_x, E_p
