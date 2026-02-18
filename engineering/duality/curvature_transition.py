"""
Curvature-Dependent Vacuum Transition Framework

Investigates the transition between cell vacuum and mode vacuum descriptions
based on the curvature criterion: R·λ_C² ~ O(1)

Key Questions:
1. Does this resolve the black hole entropy tension?
2. Is the transition smooth or discontinuous?
3. What are the observable predictions?
"""

import numpy as np
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


# Physical Constants (SI units)
class PhysicalConstants:
    """Fundamental physical constants in SI units"""
    hbar = 1.054571817e-34  # J·s
    c = 2.99792458e8  # m/s
    G = 6.67430e-11  # m³/(kg·s²)
    M_sun = 1.989e30  # kg
    l_P = 1.616e-35  # m (Planck length)
    H_0 = 2.2e-18  # s⁻¹ (Hubble constant)
    eV_to_J = 1.602176634e-19  # J/eV
    eV_to_kg = 1.78266192e-36  # kg/eV (via E=mc²)

    # Derived
    t_P = l_P / c  # Planck time
    m_P = np.sqrt(hbar * c / G)  # Planck mass


class VacuumRegime(Enum):
    """Classification of vacuum state based on curvature"""
    CELL_VACUUM = "cell"  # R·λ_C² << 1, product state, w=0
    TRANSITION = "transition"  # R·λ_C² ~ O(1)
    MODE_VACUUM = "mode"  # R·λ_C² >> 1, entangled, w=-1


@dataclass
class CurvatureAnalysis:
    """Results of curvature parameter analysis"""
    R: float  # Ricci scalar curvature (m⁻²)
    lambda_C: float  # Compton wavelength (m)
    xi: float  # Dimensionless curvature parameter R·λ_C²
    regime: VacuumRegime  # Vacuum regime classification
    description: str  # Physical context


@dataclass
class InterpolatingState:
    """One-parameter family interpolating between vacua"""
    lambda_param: float  # Interpolation parameter (0=mode, 1=cell)
    alpha_squared: float  # |α|² for displacement
    energy_density: float  # ρ(λ) in J/m³
    overlap_with_mode: float  # |⟨0|Ψ(λ)⟩|²
    w: float  # Equation of state parameter
    is_product_state: bool  # True if factorizable


class ComptonWavelength:
    """Compute Compton wavelength for particles"""

    @staticmethod
    def from_mass_kg(m: float) -> float:
        """
        Compton wavelength λ_C = ℏ/(mc)

        Args:
            m: Mass in kg

        Returns:
            Compton wavelength in meters
        """
        if m <= 0:
            raise ValueError("Mass must be positive")
        return PhysicalConstants.hbar / (m * PhysicalConstants.c)

    @staticmethod
    def from_mass_eV(m_eV: float) -> float:
        """
        Compton wavelength from mass in eV

        Args:
            m_eV: Mass in eV

        Returns:
            Compton wavelength in meters
        """
        m_kg = m_eV * PhysicalConstants.eV_to_kg
        return ComptonWavelength.from_mass_kg(m_kg)

    @staticmethod
    def neutrino_lightest() -> float:
        """Lightest neutrino mass eigenstate: 2.31 meV"""
        return ComptonWavelength.from_mass_eV(2.31e-3)


class CurvatureScalar:
    """Compute Ricci scalar curvature for various spacetimes"""

    @staticmethod
    def cosmological_current() -> float:
        """
        Current cosmological curvature: R ~ 12H₀²/c²

        Returns:
            Ricci scalar in m⁻²
        """
        H_0 = PhysicalConstants.H_0
        c = PhysicalConstants.c
        return 12 * H_0**2 / c**2

    @staticmethod
    def cosmological_at_redshift(z: float, era: str = 'matter') -> float:
        """
        Cosmological curvature at redshift z

        Args:
            z: Redshift
            era: 'matter' (R ∝ (1+z)³) or 'radiation' (R ∝ (1+z)⁴)

        Returns:
            Ricci scalar in m⁻²
        """
        R_0 = CurvatureScalar.cosmological_current()
        if era == 'matter':
            return R_0 * (1 + z)**3
        elif era == 'radiation':
            return R_0 * (1 + z)**4
        else:
            raise ValueError("Era must be 'matter' or 'radiation'")

    @staticmethod
    def black_hole_tidal(M: float) -> float:
        """
        Tidal curvature at black hole horizon

        For Schwarzschild BH, the Ricci scalar R = 0 everywhere (vacuum solution),
        but the Kretschmann scalar K = 48G²M²/(c⁴r⁶) characterizes tidal forces.

        At the horizon r = r_s = 2GM/c², the relevant curvature scale is:
        R_tidal ~ c⁴/(GM)²

        This is the curvature "felt" by an infalling observer.

        Args:
            M: Black hole mass in kg

        Returns:
            Tidal curvature scale in m⁻²
        """
        G = PhysicalConstants.G
        c = PhysicalConstants.c
        return c**4 / (G * M)**2

    @staticmethod
    def schwarzschild_radius(M: float) -> float:
        """Schwarzschild radius r_s = 2GM/c²"""
        return 2 * PhysicalConstants.G * M / PhysicalConstants.c**2


class CurvatureParameter:
    """Compute dimensionless curvature parameter ξ = R·λ_C²"""

    @staticmethod
    def compute(R: float, m: float) -> float:
        """
        Compute ξ = R·λ_C²

        Args:
            R: Ricci scalar curvature (m⁻²)
            m: Particle mass (kg)

        Returns:
            Dimensionless curvature parameter
        """
        lambda_C = ComptonWavelength.from_mass_kg(m)
        return R * lambda_C**2

    @staticmethod
    def classify_regime(xi: float,
                       threshold_low: float = 0.01,
                       threshold_high: float = 1.0) -> VacuumRegime:
        """
        Classify vacuum regime based on ξ

        Args:
            xi: Curvature parameter
            threshold_low: Below this is cell vacuum
            threshold_high: Above this is mode vacuum

        Returns:
            Vacuum regime classification
        """
        if xi < threshold_low:
            return VacuumRegime.CELL_VACUUM
        elif xi > threshold_high:
            return VacuumRegime.MODE_VACUUM
        else:
            return VacuumRegime.TRANSITION


class TransitionMass:
    """Find black hole mass where transition occurs"""

    @staticmethod
    def compute(m_particle: float, xi_transition: float = 1.0) -> float:
        """
        Find M_BH such that R_tidal(M_BH) · λ_C² = ξ_transition

        R_tidal = c⁴/(GM)²
        λ_C = ℏ/(mc)

        ξ = c⁴/(GM)² · ℏ²/(mc)²

        Solving for M:
        M² = c⁴ℏ² / (G² m² c² ξ)
        M = c ℏ / (G m √ξ)

        Args:
            m_particle: Particle mass (kg)
            xi_transition: Transition criterion (default 1.0)

        Returns:
            Transition mass in kg
        """
        c = PhysicalConstants.c
        hbar = PhysicalConstants.hbar
        G = PhysicalConstants.G

        M = c * hbar / (G * m_particle * np.sqrt(xi_transition))
        return M

    @staticmethod
    def for_neutrino(xi_transition: float = 1.0) -> Tuple[float, float]:
        """
        Transition mass for lightest neutrino (2.31 meV)

        Returns:
            (M in kg, M in solar masses)
        """
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        M = TransitionMass.compute(m_nu, xi_transition)
        M_solar = M / PhysicalConstants.M_sun
        return M, M_solar


class VacuumInterpolation:
    """Interpolating state family between mode and cell vacuum"""

    @staticmethod
    def compute_state(lambda_param: float,
                     alpha_squared: float,
                     m: float) -> InterpolatingState:
        """
        Compute properties of interpolating state |Ψ(λ)⟩

        State: |Ψ(λ)⟩ = D(λα) |0⟩ for a single cell

        CRITICAL FINDING: D(λα) creates a DISPLACED coherent state, which is
        still a product state across cells for ANY λ > 0. The entanglement
        structure is DISCONTINUOUS:
        - λ = 0: mode vacuum, entangled (area-law entropy)
        - λ > 0: displaced state, product (zero entanglement)

        This is NOT a smooth transition in entanglement!

        Args:
            lambda_param: Interpolation parameter (0=mode, 1=cell)
            alpha_squared: |α|² for full cell vacuum displacement
            m: Particle mass (kg)

        Returns:
            InterpolatingState with computed properties
        """
        c = PhysicalConstants.c
        hbar = PhysicalConstants.hbar

        # Energy density for single cell
        # ρ = m⁴c⁵/ℏ³ · (λ²|α|² + 1/2)
        # Zero-point: (1/2) term
        # Displacement: λ²|α|² term
        prefactor = m**4 * c**5 / hbar**3
        rho_zp = prefactor * 0.5
        rho_disp = prefactor * lambda_param**2 * alpha_squared
        rho_total = rho_zp + rho_disp

        # Overlap with mode vacuum: |⟨0|Ψ(λ)⟩|² = exp(-λ²|α|²)
        overlap = np.exp(-lambda_param**2 * alpha_squared)

        # Equation of state parameter
        # Zero-point energy: w = -1 (Lorentz invariant)
        # Displacement energy: w = 0 (time-averaged oscillation)
        # Combined: w = (p_zp + p_disp) / (ρ_zp + ρ_disp)
        #              = (-ρ_zp + 0) / (ρ_zp + ρ_disp)
        #              = -ρ_zp / rho_total
        w = -rho_zp / rho_total if rho_total > 0 else -1.0

        # Product state check: True for any λ > 0
        # At λ = 0, we have the mode vacuum which IS entangled
        is_product = (lambda_param > 0)

        return InterpolatingState(
            lambda_param=lambda_param,
            alpha_squared=alpha_squared,
            energy_density=rho_total,
            overlap_with_mode=overlap,
            w=w,
            is_product_state=is_product
        )

    @staticmethod
    def equation_of_state_scan(alpha_squared: float,
                               m: float,
                               n_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Scan w(λ) across interpolation parameter

        Returns:
            (lambda_values, w_values)
        """
        lambda_values = np.linspace(0, 1, n_points)
        w_values = np.zeros(n_points)

        for i, lam in enumerate(lambda_values):
            state = VacuumInterpolation.compute_state(lam, alpha_squared, m)
            w_values[i] = state.w

        return lambda_values, w_values


class BlackHoleEntropy:
    """Entropy calculations for black hole horizons"""

    @staticmethod
    def bekenstein_hawking(M: float) -> float:
        """
        Bekenstein-Hawking entropy: S = A/(4l_P²) = 4πG²M²/(ℏc)

        Args:
            M: Black hole mass (kg)

        Returns:
            Entropy in units of k_B (dimensionless)
        """
        G = PhysicalConstants.G
        hbar = PhysicalConstants.hbar
        c = PhysicalConstants.c

        return 4 * np.pi * G**2 * M**2 / (hbar * c)

    @staticmethod
    def mode_vacuum_entropy(M: float, cutoff: float) -> float:
        """
        Mode vacuum entanglement entropy with UV cutoff ε

        S ~ A/(4ε²) where A = 4πr_s²

        Args:
            M: Black hole mass (kg)
            cutoff: UV cutoff length (m)

        Returns:
            Entropy in units of k_B
        """
        r_s = CurvatureScalar.schwarzschild_radius(M)
        A = 4 * np.pi * r_s**2
        return A / (4 * cutoff**2)

    @staticmethod
    def entropy_with_compton_cutoff(M: float, m_particle: float) -> Tuple[float, float, float]:
        """
        Mode vacuum entropy using Compton wavelength as cutoff

        CRITICAL TEST: Does λ_C naturally give Planck-scale entropy?

        Args:
            M: Black hole mass (kg)
            m_particle: Particle mass providing cutoff (kg)

        Returns:
            (S with Compton cutoff, S_BH, ratio S/S_BH)
        """
        lambda_C = ComptonWavelength.from_mass_kg(m_particle)
        S_compton = BlackHoleEntropy.mode_vacuum_entropy(M, lambda_C)
        S_BH = BlackHoleEntropy.bekenstein_hawking(M)

        ratio = S_compton / S_BH

        return S_compton, S_BH, ratio


class CurvatureTransitionFramework:
    """Main analysis framework"""

    def __init__(self, m_particle: float):
        """
        Initialize framework with particle mass

        Args:
            m_particle: Particle mass in kg (default: lightest neutrino)
        """
        self.m_particle = m_particle
        self.lambda_C = ComptonWavelength.from_mass_kg(m_particle)

    def analyze_curvature(self, R: float, description: str) -> CurvatureAnalysis:
        """
        Analyze curvature parameter for given spacetime

        Args:
            R: Ricci scalar curvature (m⁻²)
            description: Physical context description

        Returns:
            CurvatureAnalysis object
        """
        xi = CurvatureParameter.compute(R, self.m_particle)
        regime = CurvatureParameter.classify_regime(xi)

        return CurvatureAnalysis(
            R=R,
            lambda_C=self.lambda_C,
            xi=xi,
            regime=regime,
            description=description
        )

    def analyze_black_hole(self, M: float) -> Dict:
        """
        Complete black hole analysis

        Args:
            M: Black hole mass (kg)

        Returns:
            Dictionary with all analysis results
        """
        # Curvature analysis
        R_tidal = CurvatureScalar.black_hole_tidal(M)
        r_s = CurvatureScalar.schwarzschild_radius(M)

        xi = CurvatureParameter.compute(R_tidal, self.m_particle)
        regime = CurvatureParameter.classify_regime(xi)

        # Entropy analysis
        S_compton, S_BH, entropy_ratio = BlackHoleEntropy.entropy_with_compton_cutoff(
            M, self.m_particle
        )

        return {
            'mass_kg': M,
            'mass_solar': M / PhysicalConstants.M_sun,
            'schwarzschild_radius_m': r_s,
            'tidal_curvature': R_tidal,
            'xi': xi,
            'regime': regime,
            'lambda_C': self.lambda_C,
            'S_BH': S_BH,
            'S_compton_cutoff': S_compton,
            'entropy_ratio': entropy_ratio,
            'compton_vs_planck': self.lambda_C / PhysicalConstants.l_P
        }

    def find_transition_mass(self, xi_transition: float = 1.0) -> Dict:
        """
        Find black hole mass where vacuum transition occurs

        Args:
            xi_transition: Transition criterion

        Returns:
            Dictionary with transition mass and analysis
        """
        M_trans = TransitionMass.compute(self.m_particle, xi_transition)
        analysis = self.analyze_black_hole(M_trans)

        return {
            'transition_mass_kg': M_trans,
            'transition_mass_solar': M_trans / PhysicalConstants.M_sun,
            'xi_at_transition': analysis['xi'],
            'regime': analysis['regime'],
            'analysis': analysis
        }

    def cosmological_survey(self) -> Dict[str, CurvatureAnalysis]:
        """
        Survey of cosmological epochs

        Returns:
            Dictionary of analyses for different epochs
        """
        analyses = {}

        # Current universe
        R_now = CurvatureScalar.cosmological_current()
        analyses['current'] = self.analyze_curvature(R_now, "Current universe (z=0)")

        # Matter-dominated (recombination)
        R_matter = CurvatureScalar.cosmological_at_redshift(1000, 'matter')
        analyses['recombination'] = self.analyze_curvature(
            R_matter, "Recombination (z=1000, matter-dominated)"
        )

        # Radiation-dominated (early universe)
        R_radiation = CurvatureScalar.cosmological_at_redshift(1e9, 'radiation')
        analyses['early_radiation'] = self.analyze_curvature(
            R_radiation, "Early radiation era (z=10^9)"
        )

        return analyses

    def black_hole_mass_scan(self,
                            masses_solar: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Scan black hole masses

        Args:
            masses_solar: Array of masses in solar masses

        Returns:
            Dictionary of arrays with results
        """
        n = len(masses_solar)
        results = {
            'masses_solar': masses_solar,
            'masses_kg': masses_solar * PhysicalConstants.M_sun,
            'xi': np.zeros(n),
            'entropy_ratio': np.zeros(n),
            'regime': []
        }

        for i, M_solar in enumerate(masses_solar):
            M_kg = M_solar * PhysicalConstants.M_sun
            analysis = self.analyze_black_hole(M_kg)

            results['xi'][i] = analysis['xi']
            results['entropy_ratio'][i] = analysis['entropy_ratio']
            results['regime'].append(analysis['regime'])

        return results


class FindingsSummary:
    """Summarize key findings of the framework"""

    @staticmethod
    def entanglement_discontinuity() -> str:
        """Report on entanglement structure discontinuity"""
        return """
CRITICAL FINDING: Entanglement Discontinuity

The interpolating state family |Psi(lambda)> = D(lambda*alpha)|0> exhibits a
DISCONTINUOUS entanglement structure:

- lambda = 0 (mode vacuum): State is |0>, which is entangled across modes
  Entanglement entropy: S ~ A/eps^2 (area law)

- lambda > 0 (any displacement): State is D(lambda*alpha)|0> = tensor_n D(lambda*alpha_n)|0_n>
  This is a PRODUCT state across cells
  Entanglement entropy: S = 0

IMPLICATION: The transition is NOT smooth in entanglement. There is a
discontinuous jump at lambda = 0. This suggests the transition is more like a
phase transition than a smooth crossover.

The equation of state w(lambda) DOES interpolate smoothly from -1 to a value
approaching 0 as lambda increases (though it asymptotes to -1/2 for alpha^2=1/2, not 0).

The true w=0 for cell vacuum comes from TIME AVERAGING the oscillating
displacement, not from the static displaced state.
"""

    @staticmethod
    def entropy_tension_resolution(m_particle: float = 2.31e-3 * PhysicalConstants.eV_to_kg) -> str:
        """Report on whether entropy tension is resolved"""

        lambda_C = ComptonWavelength.from_mass_kg(m_particle)
        l_P = PhysicalConstants.l_P
        ratio = lambda_C / l_P

        # For solar mass BH
        M = PhysicalConstants.M_sun
        S_compton, S_BH, entropy_ratio = BlackHoleEntropy.entropy_with_compton_cutoff(M, m_particle)

        return f"""
CRITICAL FINDING: Entropy Tension NOT Resolved

Question: Does using Compton wavelength as UV cutoff reproduce S_BH?

For particle mass m = 2.31 meV (lightest neutrino):
  lambda_C = {lambda_C:.3e} m
  l_P = {l_P:.3e} m
  lambda_C/l_P = {ratio:.3e}

The Compton wavelength is {ratio:.0e} times LARGER than the Planck length.

For mode vacuum entropy S ~ A/(4*eps^2) with eps = lambda_C:
  S/S_BH = (l_P/lambda_C)^2 = {1/ratio**2:.3e}

The entropy is MUCH SMALLER than Bekenstein-Hawking by a factor of ~{1/ratio**2:.0e}.

CONCLUSION: The naive transition picture with Compton-scale cutoff does NOT
reproduce the correct black hole entropy. The cutoff would need to be Planck
scale, which requires m ~ m_Planck, NOT m ~ meV.

This is a FAILURE of the framework to resolve the entropy tension.

Possible resolutions:
1. Different particle mass dominates near horizon (effective m ~ m_P?)
2. Transition criterion is wrong (not R*lambda_C^2 ~ 1)
3. Entanglement entropy formula needs modification
4. Multiple species contribute (sum over all Standard Model?)
"""

    @staticmethod
    def regime_predictions(M_trans_solar: float) -> str:
        """Observable predictions from regime classification"""
        return f"""
PREDICTIONS: Vacuum Regime Classification

Transition mass: M_trans ~ {M_trans_solar:.2e} M_sun

CELL VACUUM REGIME (M >> M_trans):
- Supermassive black holes (M > 10^6 M_sun)
- xi << 1, weak curvature
- Vacuum is product state, zero entanglement
- w = 0 (time-averaged)
- Horizon dynamics may differ from mode vacuum expectation

MODE VACUUM REGIME (M << M_trans):
- Stellar and intermediate mass BHs (M < 10^3 M_sun)
- xi >> 1, strong curvature
- Vacuum is entangled, area-law entropy
- w = -1 (Lorentz invariant)
- Standard semiclassical gravity applies

TRANSITION REGIME (M ~ M_trans):
- Discontinuous change in vacuum structure
- Neither description fully valid
- May exhibit anomalous properties

TESTABLE: Do supermassive BH horizons behave differently than stellar BHs
in ways consistent with different vacuum structures?
"""


def run_comprehensive_analysis():
    """Run full analysis suite"""

    # Initialize for neutrino
    m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
    framework = CurvatureTransitionFramework(m_nu)

    print("=" * 80)
    print("CURVATURE-DEPENDENT VACUUM TRANSITION ANALYSIS")
    print("=" * 80)
    print(f"\nParticle mass: 2.31 meV (lightest neutrino)")
    print(f"Compton wavelength: {framework.lambda_C:.3e} m")
    print(f"Planck length: {PhysicalConstants.l_P:.3e} m")
    print(f"lambda_C/l_P: {framework.lambda_C/PhysicalConstants.l_P:.3e}")

    # Cosmological survey
    print("\n" + "=" * 80)
    print("COSMOLOGICAL EPOCHS")
    print("=" * 80)
    cosmo = framework.cosmological_survey()
    for name, analysis in cosmo.items():
        print(f"\n{analysis.description}:")
        print(f"  R = {analysis.R:.3e} m^-2")
        print(f"  xi = {analysis.xi:.3e}")
        print(f"  Regime: {analysis.regime.value}")

    # Transition mass
    print("\n" + "=" * 80)
    print("VACUUM TRANSITION MASS")
    print("=" * 80)
    trans = framework.find_transition_mass()
    print(f"Transition at xi = 1:")
    print(f"  M_trans = {trans['transition_mass_solar']:.3e} M_sun")
    print(f"  M_trans = {trans['transition_mass_kg']:.3e} kg")

    # Black hole scan
    print("\n" + "=" * 80)
    print("BLACK HOLE MASS SURVEY")
    print("=" * 80)
    masses = np.logspace(0, 9, 10)  # 1 to 10⁹ solar masses
    scan = framework.black_hole_mass_scan(masses)

    print(f"\n{'M (M_sun)':<15} {'xi':<15} {'S/S_BH':<15} {'Regime':<15}")
    print("-" * 60)
    for i in range(len(masses)):
        print(f"{scan['masses_solar'][i]:<15.2e} {scan['xi'][i]:<15.3e} "
              f"{scan['entropy_ratio'][i]:<15.3e} {scan['regime'][i].value:<15}")

    # Equation of state interpolation
    print("\n" + "=" * 80)
    print("EQUATION OF STATE INTERPOLATION")
    print("=" * 80)
    alpha_sq = 0.5
    lambda_vals, w_vals = VacuumInterpolation.equation_of_state_scan(alpha_sq, m_nu, 11)

    print(f"\nFor alpha^2 = {alpha_sq}:")
    print(f"{'lambda':<10} {'w':<10} {'Product State?':<15}")
    print("-" * 35)
    for lam, w in zip(lambda_vals, w_vals):
        state = VacuumInterpolation.compute_state(lam, alpha_sq, m_nu)
        print(f"{lam:<10.1f} {w:<10.4f} {str(state.is_product_state):<15}")

    # Key findings
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    print(FindingsSummary.entanglement_discontinuity())
    print(FindingsSummary.entropy_tension_resolution(m_nu))
    print(FindingsSummary.regime_predictions(trans['transition_mass_solar']))

    return framework, cosmo, trans, scan


if __name__ == '__main__':
    framework, cosmo, trans, scan = run_comprehensive_analysis()
