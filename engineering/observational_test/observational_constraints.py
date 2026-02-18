"""
Observational Constraints on Dark Energy: LCDM vs Two Vacua Framework

This module computes cosmological observables for both the standard LCDM model
and the Two Vacua framework, then quantifies the differences.

Standard LCDM:
    H^2(z) = H0^2 [Omega_b (1+z)^3 + Omega_CDM (1+z)^3
                   + Omega_rad (1+z)^4 + Omega_Lambda]

Two Vacua framework:
    H^2(z) = H0^2 [Omega_b (1+z)^3 + Omega_cell (1+z)^3
                   + Omega_grav (1+z)^4 + Omega_rad (1+z)^4 + Omega_Wald]

Key insight: if Omega_cell = Omega_CDM and Omega_Wald = Omega_Lambda, the two
models are IDENTICAL at the background cosmology level. Differences appear only
in perturbations (structure formation) and via the dark radiation component
(graviton vacuum contributing to N_eff).

Physical constants and values from Planck 2018 + PDG 2023.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from scipy.integrate import quad, solve_ivp
from scipy.optimize import minimize_scalar

# ---------------------------------------------------------------------------
# Physical constants (SI)
# ---------------------------------------------------------------------------
HBAR = 1.054571817e-34      # J s
C = 2.99792458e8            # m/s
G = 6.67430e-11             # m^3 kg^-1 s^-2
K_B = 1.380649e-23          # J/K
EV_TO_J = 1.602176634e-19   # J per eV
MPC_TO_M = 3.0857e22        # meters per Megaparsec

# Hubble constant
H0_KM_S_MPC = 67.4          # km/s/Mpc (Planck 2018)
H0_SI = H0_KM_S_MPC * 1e3 / MPC_TO_M  # s^-1

# CMB temperature
T_CMB = 2.7255  # K (FIRAS measurement)

# Critical density: rho_crit = 3 H0^2 c^2 / (8 pi G)
# Note: 3 H0^2 / (8 pi G) gives kg/m^3; multiply by c^2 for J/m^3
RHO_CRIT = 3.0 * H0_SI**2 * C**2 / (8.0 * np.pi * G)  # J/m^3 ~ 8.5e-10

# Photon energy density from CMB temperature
# rho_gamma = (pi^2/15) * (kB T)^4 / (hbar c)^3
RHO_GAMMA = (np.pi**2 / 15.0) * (K_B * T_CMB)**4 / (HBAR * C)**3

# Standard neutrino contribution (3 massless neutrinos, standard N_eff = 3.044)
# rho_nu = N_eff * (7/8) * (4/11)^(4/3) * rho_gamma
N_EFF_STANDARD = 3.044
RHO_NU_FACTOR = (7.0 / 8.0) * (4.0 / 11.0)**(4.0 / 3.0)  # per species
RHO_RAD_TOTAL = RHO_GAMMA * (1.0 + N_EFF_STANDARD * RHO_NU_FACTOR)

# Omega_rad from photons + standard neutrinos
OMEGA_RAD = RHO_RAD_TOTAL / RHO_CRIT  # ~ 9.1e-5

# Speed of light in km/s for convenience
C_KM_S = C / 1e3


# ---------------------------------------------------------------------------
# Cosmological Parameters
# ---------------------------------------------------------------------------
@dataclass
class LCDMParams:
    """Standard LCDM cosmological parameters (Planck 2018 best-fit)."""
    H0: float = H0_SI           # Hubble constant [s^-1]
    Omega_b: float = 0.0493     # Baryon density parameter
    Omega_CDM: float = 0.2607   # Cold dark matter density parameter
    Omega_rad: float = OMEGA_RAD  # Radiation (photons + neutrinos)
    # Omega_Lambda derived from flatness: 1 - Omega_b - Omega_CDM - Omega_rad

    @property
    def Omega_Lambda(self) -> float:
        return 1.0 - self.Omega_b - self.Omega_CDM - self.Omega_rad

    @property
    def Omega_m(self) -> float:
        """Total matter density parameter."""
        return self.Omega_b + self.Omega_CDM


@dataclass
class TwoVacuaParams:
    """
    Two Vacua framework cosmological parameters.

    Components:
    - Baryons: standard (w = 0, dilutes as a^-3)
    - Cell vacuum: replaces CDM (w = 0, dilutes as a^-3)
    - Graviton vacuum: dark radiation (w = +1/3, dilutes as a^-4)
    - Wald ambiguity: cosmological constant (w = -1, constant)
    - Standard radiation: photons + neutrinos (w = +1/3, dilutes as a^-4)

    The graviton vacuum energy density is rho_grav = rho_cell / (8 pi^2).
    """
    H0: float = H0_SI
    Omega_b: float = 0.0493
    Omega_cell: float = 0.2607      # Same as Omega_CDM (w=0 component)
    Omega_rad: float = OMEGA_RAD    # Standard photons + neutrinos
    Omega_Wald: float = None        # Set from flatness if None

    # The graviton vacuum prediction: rho_grav = rho_cell / (8 pi^2)
    # This adds dark radiation beyond the standard model neutrinos
    _graviton_ratio: float = field(default=1.0 / (8.0 * np.pi**2), repr=False)

    def __post_init__(self):
        if self.Omega_Wald is None:
            # Flatness: sum of all Omega = 1
            # Omega_grav = Omega_cell / (8 pi^2)
            grav = self.Omega_cell * self._graviton_ratio
            self.Omega_Wald = (1.0 - self.Omega_b - self.Omega_cell
                               - grav - self.Omega_rad)

    @property
    def Omega_grav(self) -> float:
        """Graviton vacuum density parameter: Omega_cell / (8 pi^2)."""
        return self.Omega_cell * self._graviton_ratio

    @property
    def Omega_m(self) -> float:
        """Total matter-like density (baryons + cell vacuum)."""
        return self.Omega_b + self.Omega_cell

    @property
    def Omega_rad_total(self) -> float:
        """Total radiation-like density (standard + graviton vacuum)."""
        return self.Omega_rad + self.Omega_grav


# ---------------------------------------------------------------------------
# Expansion Rate H(z)
# ---------------------------------------------------------------------------
def H_squared_LCDM(z: np.ndarray, params: LCDMParams = None) -> np.ndarray:
    """
    Compute H^2(z) / H0^2 for standard LCDM.

    H^2/H0^2 = Omega_m (1+z)^3 + Omega_rad (1+z)^4 + Omega_Lambda
    """
    if params is None:
        params = LCDMParams()
    zp1 = 1.0 + np.asarray(z, dtype=float)
    return (params.Omega_m * zp1**3
            + params.Omega_rad * zp1**4
            + params.Omega_Lambda)


def H_squared_TwoVacua(z: np.ndarray, params: TwoVacuaParams = None) -> np.ndarray:
    """
    Compute H^2(z) / H0^2 for the Two Vacua framework.

    H^2/H0^2 = (Omega_b + Omega_cell)(1+z)^3
              + (Omega_rad + Omega_grav)(1+z)^4
              + Omega_Wald
    """
    if params is None:
        params = TwoVacuaParams()
    zp1 = 1.0 + np.asarray(z, dtype=float)
    return ((params.Omega_b + params.Omega_cell) * zp1**3
            + (params.Omega_rad + params.Omega_grav) * zp1**4
            + params.Omega_Wald)


def H_ratio(z: np.ndarray,
            lcdm: LCDMParams = None,
            tv: TwoVacuaParams = None) -> np.ndarray:
    """
    Compute H_TwoVacua(z) / H_LCDM(z).

    Deviations from 1.0 indicate observable differences.
    """
    h2_lcdm = H_squared_LCDM(z, lcdm)
    h2_tv = H_squared_TwoVacua(z, tv)
    return np.sqrt(h2_tv / h2_lcdm)


# ---------------------------------------------------------------------------
# Distances
# ---------------------------------------------------------------------------
def comoving_distance(z_max: float, H_squared_func, params, n_points: int = 1000) -> float:
    """
    Comoving distance: chi(z) = c * integral_0^z dz' / H(z')

    Returns distance in meters.
    """
    def integrand(z):
        return 1.0 / np.sqrt(H_squared_func(z, params))

    result, _ = quad(integrand, 0, z_max, limit=100)
    return (C / params.H0) * result


def luminosity_distance(z: float, H_squared_func, params) -> float:
    """
    Luminosity distance: d_L = (1+z) * chi(z)

    For a flat universe. Returns distance in meters.
    """
    chi = comoving_distance(z, H_squared_func, params)
    return (1.0 + z) * chi


def angular_diameter_distance(z: float, H_squared_func, params) -> float:
    """
    Angular diameter distance: d_A = chi(z) / (1+z)

    For a flat universe. Returns distance in meters.
    """
    chi = comoving_distance(z, H_squared_func, params)
    return chi / (1.0 + z)


def distance_modulus(z: float, H_squared_func, params) -> float:
    """
    Distance modulus: mu = 5 log10(d_L / 10 pc)

    This is what Type Ia supernovae actually measure.
    """
    d_L = luminosity_distance(z, H_squared_func, params)
    d_L_pc = d_L / 3.0857e16  # convert meters to parsecs
    return 5.0 * np.log10(d_L_pc / 10.0)


# ---------------------------------------------------------------------------
# Vectorized distance computations
# ---------------------------------------------------------------------------
def luminosity_distance_array(z_array: np.ndarray, H_squared_func, params) -> np.ndarray:
    """Compute d_L(z) for an array of redshifts."""
    return np.array([luminosity_distance(z, H_squared_func, params) for z in z_array])


def angular_diameter_distance_array(z_array: np.ndarray, H_squared_func, params) -> np.ndarray:
    """Compute d_A(z) for an array of redshifts."""
    return np.array([angular_diameter_distance(z, H_squared_func, params) for z in z_array])


# ---------------------------------------------------------------------------
# Effective Equation of State
# ---------------------------------------------------------------------------
def w_eff_TwoVacua(z: np.ndarray, params: TwoVacuaParams = None) -> np.ndarray:
    """
    Effective equation of state for the Two Vacua dark sector.

    The dark sector consists of: cell vacuum (w=0), graviton vacuum (w=+1/3),
    Wald ambiguity (w=-1).

    w_eff(z) = sum_i [w_i * rho_i(z)] / sum_i [rho_i(z)]

    where the sum is over dark sector components only (not baryons or
    standard radiation, which are accounted for separately by cosmologists).

    This is what a cosmologist would infer as the "dark energy equation of state"
    if they fit the expansion history assuming standard baryons + radiation +
    a single dark component.
    """
    if params is None:
        params = TwoVacuaParams()

    zp1 = 1.0 + np.asarray(z, dtype=float)

    # Dark sector components at redshift z (in units of rho_crit today)
    rho_cell = params.Omega_cell * zp1**3       # w = 0
    rho_grav = params.Omega_grav * zp1**4        # w = +1/3
    rho_Wald = params.Omega_Wald * np.ones_like(zp1)  # w = -1

    rho_dark_total = rho_cell + rho_grav + rho_Wald

    # Pressure-weighted: w_eff = sum(w_i * rho_i) / sum(rho_i)
    w_eff = (0.0 * rho_cell + (1.0/3.0) * rho_grav + (-1.0) * rho_Wald) / rho_dark_total

    return w_eff


def w_eff_dark_energy_only(z: np.ndarray, params: TwoVacuaParams = None) -> np.ndarray:
    """
    What a cosmologist reports as 'w' after subtracting matter.

    Cosmologists fit: H^2 = H0^2 [Omega_m (1+z)^3 + Omega_rad (1+z)^4 + Omega_DE f(z)]

    where Omega_m includes ALL matter-like components. If the cell vacuum
    is indistinguishable from CDM, it gets absorbed into Omega_m.

    The residual 'dark energy' then includes ONLY:
    - Wald ambiguity (w = -1)
    - Graviton vacuum (w = +1/3)

    w_DE(z) = [(-1) * rho_Wald + (1/3) * rho_grav] / [rho_Wald + rho_grav]
    """
    if params is None:
        params = TwoVacuaParams()

    zp1 = 1.0 + np.asarray(z, dtype=float)

    rho_grav = params.Omega_grav * zp1**4
    rho_Wald = params.Omega_Wald * np.ones_like(zp1)

    rho_DE = rho_Wald + rho_grav
    w_DE = (-1.0 * rho_Wald + (1.0/3.0) * rho_grav) / rho_DE

    return w_DE


# ---------------------------------------------------------------------------
# Single-w Fitting
# ---------------------------------------------------------------------------
def fit_single_w(z_array: np.ndarray, params_tv: TwoVacuaParams = None,
                 params_lcdm: LCDMParams = None) -> Dict[str, float]:
    """
    Fit the Two Vacua expansion history with a single-w dark energy model.

    Model: H^2/H0^2 = Omega_m (1+z)^3 + Omega_rad (1+z)^4
                     + Omega_DE (1+z)^{3(1+w)}

    Fit for w that minimizes chi^2 of H(z) residuals.

    If the Two Vacua model with Omega_cell = Omega_CDM exactly reproduces LCDM,
    fitting w should return w = -1.

    But if the graviton vacuum adds nontrivial dark radiation, the best-fit w
    may deviate slightly from -1.
    """
    if params_tv is None:
        params_tv = TwoVacuaParams()
    if params_lcdm is None:
        params_lcdm = LCDMParams()

    # Target: H^2/H0^2 from Two Vacua at each z
    H2_target = H_squared_TwoVacua(z_array, params_tv)

    # The matter and radiation that the fitter assumes (standard values)
    Omega_m_fit = params_lcdm.Omega_m
    Omega_rad_fit = params_lcdm.Omega_rad
    Omega_DE_fit = 1.0 - Omega_m_fit - Omega_rad_fit

    def chi2(w):
        zp1 = 1.0 + z_array
        H2_model = (Omega_m_fit * zp1**3
                     + Omega_rad_fit * zp1**4
                     + Omega_DE_fit * zp1**(3.0 * (1.0 + w)))
        return np.sum((H2_model - H2_target)**2 / H2_target**2)

    result = minimize_scalar(chi2, bounds=(-2.0, 0.0), method='bounded')

    return {
        "best_fit_w": result.x,
        "chi2_min": result.fun,
        "chi2_at_w_minus_1": chi2(-1.0),
        "w_deviation_from_minus_1": result.x - (-1.0),
    }


# ---------------------------------------------------------------------------
# Residuals Between Models
# ---------------------------------------------------------------------------
def distance_residuals(z_array: np.ndarray,
                       lcdm: LCDMParams = None,
                       tv: TwoVacuaParams = None) -> Dict[str, np.ndarray]:
    """
    Compute fractional residuals in distances between LCDM and Two Vacua.

    |d_L_TV - d_L_LCDM| / d_L_LCDM  and similar for d_A.
    """
    if lcdm is None:
        lcdm = LCDMParams()
    if tv is None:
        tv = TwoVacuaParams()

    dL_lcdm = luminosity_distance_array(z_array, H_squared_LCDM, lcdm)
    dL_tv = luminosity_distance_array(z_array, H_squared_TwoVacua, tv)

    dA_lcdm = angular_diameter_distance_array(z_array, H_squared_LCDM, lcdm)
    dA_tv = angular_diameter_distance_array(z_array, H_squared_TwoVacua, tv)

    return {
        "z": z_array,
        "dL_fractional_residual": np.abs(dL_tv - dL_lcdm) / dL_lcdm,
        "dA_fractional_residual": np.abs(dA_tv - dA_lcdm) / dA_lcdm,
        "dL_LCDM": dL_lcdm,
        "dL_TwoVacua": dL_tv,
        "dA_LCDM": dA_lcdm,
        "dA_TwoVacua": dA_tv,
    }


# ---------------------------------------------------------------------------
# N_eff Prediction from Graviton Vacuum
# ---------------------------------------------------------------------------
def delta_N_eff(params: TwoVacuaParams = None) -> Dict[str, float]:
    """
    Compute the effective number of extra neutrino species from the
    graviton vacuum dark radiation.

    N_eff is defined via: rho_rad = rho_gamma [1 + N_eff * (7/8)(4/11)^{4/3}]

    The graviton vacuum adds: Delta_rho = rho_cell / (8 pi^2)

    At recombination (z ~ 1100), the graviton vacuum energy density is:
        rho_grav(z) = Omega_grav * rho_crit * (1+z)^4

    One neutrino species has energy density:
        rho_1nu(z) = (7/8)(4/11)^{4/3} * rho_gamma * (1+z)^4 / (1+z_gamma)^4

    But both scale as (1+z)^4, so the ratio is redshift-independent:
        Delta_N_eff = Omega_grav / [Omega_gamma * (7/8)(4/11)^{4/3}]

    where Omega_gamma = rho_gamma / rho_crit.
    """
    if params is None:
        params = TwoVacuaParams()

    Omega_gamma = RHO_GAMMA / RHO_CRIT

    # Energy density of one neutrino species (in Omega units)
    Omega_1nu = Omega_gamma * RHO_NU_FACTOR

    # Delta N_eff from graviton vacuum
    dN = params.Omega_grav / Omega_1nu

    # Planck 2018 constraint: N_eff = 2.99 +/- 0.17
    # So Delta N_eff < 0.3 at 95% CL
    planck_bound = 0.3

    return {
        "Omega_grav": params.Omega_grav,
        "Omega_gamma": Omega_gamma,
        "Omega_1nu": Omega_1nu,
        "Delta_N_eff": dN,
        "N_eff_total": N_EFF_STANDARD + dN,
        "Planck_bound_95CL": planck_bound,
        "within_Planck_bound": dN < planck_bound,
        "detectable_by_CMB_S4": dN > 0.06,  # CMB-S4 target sensitivity
    }


# ---------------------------------------------------------------------------
# Jeans Analysis for Cell Vacuum
# ---------------------------------------------------------------------------
def jeans_analysis(mass_eV: float = 2.31e-3) -> Dict[str, float]:
    """
    Jeans analysis for the cell vacuum.

    Standard CDM: pressureless (c_s = 0), clusters gravitationally at all scales.

    Cell vacuum: product state of independent coherent states.
    - No inter-cell interactions (product state) => c_s_classical = 0
    - Quantum pressure from uncertainty principle gives a quantum Jeans length

    Quantum Jeans length (for fuzzy/wave dark matter):
        lambda_J = (pi / G rho)^{1/4} * (hbar / m)^{1/2}

    But for the cell vacuum interpreted as dust-like oscillating field,
    the effective sound speed is:
        c_s^2 = delta_p / delta_rho

    For a coherent oscillation with omega >> H, the effective sound speed
    at scales >> Compton wavelength is c_s = 0 (same as CDM).

    The quantum Jeans length is of order the Compton wavelength:
        lambda_J_quantum ~ hbar / (m c) = lambda_Compton

    For m = 2.31 meV: lambda_Compton ~ 0.085 mm
    All astrophysical structures are vastly larger => clusters like CDM.
    """
    mass_kg = mass_eV * EV_TO_J / C**2

    # Compton wavelength
    lambda_C = HBAR / (mass_kg * C)

    # Mean dark matter density today (cosmological average)
    rho_DM = 0.2607 * RHO_CRIT  # ~ 2e-10 J/m^3

    # Convert to mass density for Jeans analysis: rho_mass = rho_DM / c^2
    rho_mass = rho_DM / C**2  # kg/m^3

    # Classical sound speed: 0 (product state, no interactions)
    c_s_classical = 0.0

    # Quantum Jeans length for a wave/fuzzy dark matter particle.
    # For a scalar field of mass m in a background of density rho,
    # the quantum Jeans length is (Hu, Barkana & Gruzinov 2000):
    #
    #   lambda_J = (pi^2 hbar^2 / (G m^2 rho_mass))^{1/4}
    #
    # This is the scale below which quantum pressure prevents collapse.
    # For m ~ meV, this is extremely small.
    lambda_J = (np.pi**2 * HBAR**2 / (G * mass_kg**2 * rho_mass))**0.25

    # Compare to galaxy scales
    kpc_in_m = 3.0857e19  # meters per kiloparsec

    # Key comparison masses for fuzzy DM literature
    # Standard fuzzy DM: m ~ 10^-22 eV gives lambda_J ~ 1 kpc
    # Cell vacuum: m ~ 2.31 meV = 2.31e-3 eV -- MUCH heavier
    # Heavier mass => much smaller Jeans length
    mass_ratio = mass_eV / 1e-22  # ratio to standard fuzzy DM mass

    return {
        "mass_eV": mass_eV,
        "mass_kg": mass_kg,
        "lambda_Compton_m": lambda_C,
        "lambda_Compton_mm": lambda_C * 1e3,
        "c_s_classical": c_s_classical,
        "lambda_Jeans_m": lambda_J,
        "lambda_Jeans_kpc": lambda_J / kpc_in_m,
        "lambda_Compton_kpc": lambda_C / kpc_in_m,
        "galaxy_scale_kpc": 10.0,  # typical galaxy ~ 10 kpc
        "clusters_like_CDM_above_Compton": True,
        "mass_ratio_to_fuzzy_DM": mass_ratio,
        "suppression_scale_much_below_observable": lambda_J / kpc_in_m < 1.0,  # < 1 kpc
        "conclusion": (
            f"Jeans length ~ {lambda_J:.2e} m, Compton wavelength ~ {lambda_C:.2e} m. "
            f"Both far below any astrophysical scale. "
            f"Cell vacuum clusters identically to CDM at all observable scales."
        ),
    }


# ---------------------------------------------------------------------------
# Linear Growth Factor D(z)
# ---------------------------------------------------------------------------
def growth_factor(z_array: np.ndarray, H_squared_func, params,
                  Omega_m: float = None) -> np.ndarray:
    """
    Compute the linear growth factor D(z) by solving the growth equation.

    Uses the standard integral formula (Heath 1977):
    D(a) proportional to E(a) * integral_0^a da' / [a' E(a')]^3

    where E(a) = H(a)/H0.  Normalized so D(z=0) = 1.
    """
    if Omega_m is None:
        if isinstance(params, LCDMParams):
            Omega_m = params.Omega_m
        elif isinstance(params, TwoVacuaParams):
            Omega_m = params.Omega_m

    z_arr = np.asarray(z_array, dtype=float)
    D_values = np.zeros_like(z_arr)

    def _E(z_val):
        return np.sqrt(float(H_squared_func(z_val, params)))

    def _integrand(a_prime):
        if a_prime < 1e-30:
            return 0.0
        z_prime = 1.0 / a_prime - 1.0
        E = _E(z_prime)
        return 1.0 / (a_prime * E)**3

    # Compute D(a=1) for normalization
    integral_0, _ = quad(_integrand, 1e-6, 1.0, limit=200)
    E_0 = _E(0.0)
    D_at_z0 = (5.0 / 2.0) * Omega_m * E_0 * integral_0

    for i, z in enumerate(z_arr):
        a = 1.0 / (1.0 + z)
        if a < 1e-6:
            # In matter-dominated era, D ~ a
            D_values[i] = a
            continue
        integral_a, _ = quad(_integrand, 1e-6, a, limit=200)
        E_a = _E(z)
        D_unnorm = (5.0 / 2.0) * Omega_m * E_a * integral_a
        D_values[i] = D_unnorm / D_at_z0 if D_at_z0 != 0 else 0.0

    return D_values


def growth_factor_ratio(z_array: np.ndarray,
                        lcdm: LCDMParams = None,
                        tv: TwoVacuaParams = None) -> np.ndarray:
    """
    Compute D_TwoVacua(z) / D_LCDM(z).

    Deviations from 1.0 indicate perturbation-level differences.
    """
    if lcdm is None:
        lcdm = LCDMParams()
    if tv is None:
        tv = TwoVacuaParams()

    D_lcdm = growth_factor(z_array, H_squared_LCDM, lcdm)
    D_tv = growth_factor(z_array, H_squared_TwoVacua, tv)

    # Avoid division by zero
    mask = D_lcdm != 0
    ratio = np.ones_like(z_array)
    ratio[mask] = D_tv[mask] / D_lcdm[mask]

    return ratio


# ---------------------------------------------------------------------------
# Can Current Data Distinguish the Models?
# ---------------------------------------------------------------------------
def distinguishability_analysis(lcdm: LCDMParams = None,
                                tv: TwoVacuaParams = None) -> Dict:
    """
    Quantify whether current observational data can distinguish
    LCDM from the Two Vacua framework.

    Current observational precision:
    - Type Ia SNe: d_L measured to ~1% at z < 1
    - BAO: d_A and H(z) measured to ~1-2% at z ~ 0.1-2.5
    - CMB: integrated distances to ~0.1%
    - f sigma_8: growth rate to ~5-10%
    - N_eff: constrained to +/- 0.17 (Planck), target +/- 0.06 (CMB-S4)
    """
    if lcdm is None:
        lcdm = LCDMParams()
    if tv is None:
        tv = TwoVacuaParams()

    z_test = np.array([0.0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 1100.0])

    # H(z) ratio
    h_ratio = H_ratio(z_test, lcdm, tv)
    max_H_deviation = np.max(np.abs(h_ratio - 1.0))

    # Distance residuals (skip z=0)
    z_dist = z_test[z_test > 0.01]
    residuals = distance_residuals(z_dist, lcdm, tv)
    max_dL_residual = np.max(residuals["dL_fractional_residual"])
    max_dA_residual = np.max(residuals["dA_fractional_residual"])

    # N_eff
    neff = delta_N_eff(tv)

    # Growth factor
    z_growth = np.array([0.0, 0.3, 0.5, 1.0, 2.0])
    D_ratio = growth_factor_ratio(z_growth, lcdm, tv)
    max_D_deviation = np.max(np.abs(D_ratio - 1.0))

    # Single-w fit
    z_fit = np.linspace(0.01, 2.0, 100)
    w_fit = fit_single_w(z_fit, tv, lcdm)

    # Observational precision thresholds
    sne_precision = 0.01          # 1% in d_L
    bao_precision = 0.01          # 1% in d_A, H(z)
    cmb_precision = 0.001         # 0.1% in integrated distance
    fsigma8_precision = 0.05      # 5% in growth rate
    neff_planck = 0.17            # Planck N_eff uncertainty (1 sigma)
    neff_cmbs4 = 0.06             # CMB-S4 target

    return {
        "max_H_deviation": max_H_deviation,
        "max_dL_residual": max_dL_residual,
        "max_dA_residual": max_dA_residual,
        "max_growth_deviation": max_D_deviation,
        "Delta_N_eff": neff["Delta_N_eff"],
        "best_fit_w": w_fit["best_fit_w"],
        "w_deviation": w_fit["w_deviation_from_minus_1"],

        "H_detectable_by_BAO": max_H_deviation > bao_precision,
        "dL_detectable_by_SNe": max_dL_residual > sne_precision,
        "dA_detectable_by_BAO": max_dA_residual > bao_precision,
        "growth_detectable": max_D_deviation > fsigma8_precision,
        "Neff_detectable_Planck": neff["Delta_N_eff"] > neff_planck,
        "Neff_detectable_CMBS4": neff["Delta_N_eff"] > neff_cmbs4,

        "background_level_identical": (max_H_deviation < 1e-3 and
                                        max_dL_residual < 1e-3),
        "perturbation_differences_exist": max_D_deviation > 1e-6,

        "observational_thresholds": {
            "SNe_dL_percent": sne_precision * 100,
            "BAO_percent": bao_precision * 100,
            "CMB_percent": cmb_precision * 100,
            "fsigma8_percent": fsigma8_precision * 100,
            "Neff_Planck_1sigma": neff_planck,
            "Neff_CMBS4_1sigma": neff_cmbs4,
        },
    }


# ---------------------------------------------------------------------------
# Cell Vacuum Physical Properties
# ---------------------------------------------------------------------------
def cell_vacuum_properties(mass_eV: float = 2.31e-3) -> Dict[str, float]:
    """
    Physical properties of the cell vacuum as a dark matter candidate.

    rho_cell = m^4 c^5 / hbar^3

    This predicts a specific relationship between the dark matter density
    and the lightest neutrino mass, which is testable.
    """
    mass_kg = mass_eV * EV_TO_J / C**2
    rho_cell = mass_kg**4 * C**5 / HBAR**3

    # Observed dark matter density
    rho_DM_observed = 0.2607 * RHO_CRIT  # Omega_CDM * rho_crit ~ 2e-10 J/m^3

    # Observed dark energy density
    rho_DE_observed = 0.6900 * RHO_CRIT  # Omega_Lambda * rho_crit ~ 5.3e-10 J/m^3

    # Predicted vs observed: the formula rho_cell ~ 5.94e-10 is closer to rho_DE
    # than to rho_DM. In the Two Vacua framework, the cell vacuum is ASSIGNED
    # to the CDM role (Omega_cell = Omega_CDM as a model parameter), while the
    # formula value is a separate prediction about the mass scale.
    ratio_to_DM = rho_cell / rho_DM_observed
    ratio_to_DE = rho_cell / rho_DE_observed
    ratio = ratio_to_DM

    # Compton wavelength
    lambda_C = HBAR / (mass_kg * C)

    # Oscillation frequency
    omega = mass_kg * C**2 / HBAR

    # Ratio to Hubble rate
    omega_over_H0 = omega / H0_SI

    return {
        "mass_eV": mass_eV,
        "rho_cell_J_m3": rho_cell,
        "rho_DM_observed_J_m3": rho_DM_observed,
        "rho_DE_observed_J_m3": rho_DE_observed,
        "density_ratio_to_DM": ratio_to_DM,
        "density_ratio_to_DE": ratio_to_DE,
        "density_ratio": ratio,
        "lambda_Compton_m": lambda_C,
        "lambda_Compton_mm": lambda_C * 1e3,
        "omega_rad_s": omega,
        "omega_over_H0": omega_over_H0,
        "oscillates_much_faster_than_expansion": omega_over_H0 > 1e10,
        "equation_of_state": "w = 0 (pressureless dust)",
        "clusters_like_CDM": True,
        "sound_speed": 0.0,
    }


# ---------------------------------------------------------------------------
# Graviton Vacuum Ratio
# ---------------------------------------------------------------------------
def graviton_vacuum_ratio_prediction() -> Dict[str, float]:
    """
    The Two Vacua framework predicts rho_grav / rho_cell = 1/(8 pi^2).

    This is a SPECIFIC NUMERICAL prediction with no free parameters.
    """
    ratio_predicted = 1.0 / (8.0 * np.pi**2)

    # In terms of cosmological parameters
    Omega_cell = 0.2607
    Omega_grav_predicted = Omega_cell * ratio_predicted

    # Dark radiation in N_eff units
    neff = delta_N_eff()

    return {
        "ratio_predicted": ratio_predicted,
        "ratio_value": f"1/(8 pi^2) = {ratio_predicted:.6f}",
        "Omega_grav_predicted": Omega_grav_predicted,
        "Delta_N_eff_predicted": neff["Delta_N_eff"],
        "testable": True,
        "test_method": "CMB N_eff measurement (Planck, CMB-S4)",
    }


# ---------------------------------------------------------------------------
# Main: Run All Analyses
# ---------------------------------------------------------------------------
def run_full_analysis() -> Dict:
    """Run all observational constraint analyses and return results."""
    results = {}

    lcdm = LCDMParams()
    tv = TwoVacuaParams()

    # 1. Parameter comparison
    results["LCDM_params"] = {
        "Omega_b": lcdm.Omega_b,
        "Omega_CDM": lcdm.Omega_CDM,
        "Omega_Lambda": lcdm.Omega_Lambda,
        "Omega_rad": lcdm.Omega_rad,
        "Omega_total": lcdm.Omega_b + lcdm.Omega_CDM + lcdm.Omega_Lambda + lcdm.Omega_rad,
    }

    results["TwoVacua_params"] = {
        "Omega_b": tv.Omega_b,
        "Omega_cell": tv.Omega_cell,
        "Omega_Wald": tv.Omega_Wald,
        "Omega_grav": tv.Omega_grav,
        "Omega_rad": tv.Omega_rad,
        "Omega_total": tv.Omega_b + tv.Omega_cell + tv.Omega_Wald + tv.Omega_grav + tv.Omega_rad,
    }

    # 2. H(z) comparison
    z_test = np.linspace(0, 5, 50)
    results["H_ratio"] = {
        "z": z_test.tolist(),
        "ratio": H_ratio(z_test, lcdm, tv).tolist(),
        "max_deviation": float(np.max(np.abs(H_ratio(z_test, lcdm, tv) - 1.0))),
    }

    # 3. Effective equation of state
    z_eos = np.linspace(0, 3, 100)
    results["w_eff"] = {
        "z": z_eos.tolist(),
        "w_dark_sector": w_eff_TwoVacua(z_eos, tv).tolist(),
        "w_dark_energy_only": w_eff_dark_energy_only(z_eos, tv).tolist(),
        "w_at_z0": float(w_eff_dark_energy_only(np.array([0.0]), tv)[0]),
    }

    # 4. N_eff prediction
    results["N_eff"] = delta_N_eff(tv)

    # 5. Jeans analysis
    results["Jeans"] = jeans_analysis()

    # 6. Cell vacuum properties
    results["cell_vacuum"] = cell_vacuum_properties()

    # 7. Graviton ratio prediction
    results["graviton_ratio"] = graviton_vacuum_ratio_prediction()

    # 8. Single-w fit
    z_fit = np.linspace(0.01, 2.0, 100)
    results["single_w_fit"] = fit_single_w(z_fit, tv, lcdm)

    # 9. Distinguishability
    results["distinguishability"] = distinguishability_analysis(lcdm, tv)

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("OBSERVATIONAL CONSTRAINTS: LCDM vs TWO VACUA")
    print("=" * 70)

    results = run_full_analysis()

    # Parameters
    print("\n--- LCDM Parameters ---")
    for k, v in results["LCDM_params"].items():
        print(f"  {k}: {v:.6f}")

    print("\n--- Two Vacua Parameters ---")
    for k, v in results["TwoVacua_params"].items():
        print(f"  {k}: {v:.6f}")

    # H(z) comparison
    print(f"\n--- H(z) Comparison ---")
    print(f"  Max |H_TV/H_LCDM - 1|: {results['H_ratio']['max_deviation']:.2e}")

    # Effective w
    print(f"\n--- Effective Equation of State ---")
    print(f"  w_DE at z=0: {results['w_eff']['w_at_z0']:.6f}")

    # N_eff
    print(f"\n--- N_eff Prediction ---")
    neff = results["N_eff"]
    print(f"  Omega_grav: {neff['Omega_grav']:.6e}")
    print(f"  Delta N_eff: {neff['Delta_N_eff']:.4f}")
    print(f"  Within Planck bound: {neff['within_Planck_bound']}")
    print(f"  Detectable by CMB-S4: {neff['detectable_by_CMB_S4']}")

    # Jeans
    print(f"\n--- Jeans Analysis ---")
    jeans = results["Jeans"]
    print(f"  Compton wavelength: {jeans['lambda_Compton_mm']:.4f} mm")
    print(f"  Jeans length: {jeans['lambda_Jeans_m']:.2e} m")
    print(f"  Clusters like CDM: {jeans['clusters_like_CDM_above_Compton']}")

    # Single-w fit
    print(f"\n--- Single-w Fit ---")
    wfit = results["single_w_fit"]
    print(f"  Best-fit w: {wfit['best_fit_w']:.6f}")
    print(f"  Deviation from -1: {wfit['w_deviation_from_minus_1']:.2e}")

    # Distinguishability
    print(f"\n--- Distinguishability ---")
    dist = results["distinguishability"]
    print(f"  Background-level identical: {dist['background_level_identical']}")
    print(f"  Max H deviation: {dist['max_H_deviation']:.2e}")
    print(f"  Max d_L residual: {dist['max_dL_residual']:.2e}")
    print(f"  Delta N_eff: {dist['Delta_N_eff']:.4f}")
    print(f"  N_eff detectable (Planck): {dist['Neff_detectable_Planck']}")
    print(f"  N_eff detectable (CMB-S4): {dist['Neff_detectable_CMBS4']}")

    # Graviton ratio
    print(f"\n--- Graviton Vacuum Ratio ---")
    gr = results["graviton_ratio"]
    print(f"  Predicted ratio: {gr['ratio_value']}")
    print(f"  Delta N_eff: {gr['Delta_N_eff_predicted']:.4f}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("""
  WITHOUT the graviton vacuum, Two Vacua reproduces LCDM exactly:
    - Cell vacuum (w=0) replaces CDM (w=0) -- identical expansion
    - Wald ambiguity (w=-1) replaces Lambda (w=-1) -- identical expansion

  WITH the graviton vacuum, there is a MAJOR discrepancy:
    - Omega_grav ~ 0.003 >> Omega_rad ~ 9e-5
    - Delta N_eff ~ 267, vs Planck bound of 0.3
    - The graviton vacuum prediction is RULED OUT by a factor of ~900

  TESTABLE PREDICTIONS:
  1. rho_cell = m^4 c^5 / hbar^3 (but gives 3x rho_CDM, closer to rho_DE)
  2. rho_grav / rho_cell = 1/(8 pi^2) -- FALSIFIED by N_eff measurements
  3. Cell vacuum clusters like CDM at all observable scales (untestable)

  WHAT THE FRAMEWORK DOES NOT EXPLAIN:
  - The VALUE of the Wald ambiguity (cosmological constant)
  - Why rho_cell formula gives rho_DE, not rho_CDM
    """)
