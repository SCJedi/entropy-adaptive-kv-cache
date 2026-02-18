"""
Experimental comparison and falsification analysis for Two Vacua Theory.

This module provides:
1. Current experimental status table with sigma tensions
2. Falsification map showing when framework is ruled out
3. Sensitivity to Hubble tension
4. Dark matter interpretation (if w=0 means DM not DE)
5. Probability timeline based on upcoming experiments
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from scipy.stats import norm
import matplotlib.pyplot as plt


# Physical constants
C = 299792458.0  # m/s
HBAR = 1.054571817e-34  # J·s
G = 6.67430e-11  # m³/(kg·s²)
EV_TO_JOULE = 1.602176634e-19
MEV_TO_JOULE = 1e-3 * EV_TO_JOULE


@dataclass
class ExperimentalConstraint:
    """Represents an experimental constraint on neutrino mass sum."""
    name: str
    year: int
    sum_nu_upper_limit_mev: float  # 95% CL upper bound
    confidence_level: float = 0.95
    sigma_level: float = 2.0  # CL expressed as sigma (95% ~ 2σ)
    is_upper_limit: bool = True  # vs detection

    def compute_tension(self, theory_prediction_mev: float) -> float:
        """
        Compute sigma tension between theory and experiment.

        For upper limit: if theory > limit, compute sigma tension.
        Assume Gaussian and extract implied sigma from CL.
        """
        if not self.is_upper_limit:
            # For actual detection, need more info
            return 0.0

        # For upper limit at 95% CL (2σ), implied uncertainty is:
        # σ_implied = limit / 2
        sigma_implied = self.sum_nu_upper_limit_mev / self.sigma_level

        # Tension in sigma
        if theory_prediction_mev > self.sum_nu_upper_limit_mev:
            tension = (theory_prediction_mev - self.sum_nu_upper_limit_mev) / sigma_implied
        else:
            tension = 0.0

        return tension


@dataclass
class DarkEnergyConstraint:
    """Constraint on dark energy equation of state."""
    name: str
    year: int
    w_central: float
    w_uncertainty: float

    def compute_tension(self, theory_w: float) -> float:
        """Compute sigma tension on w."""
        return abs(theory_w - self.w_central) / self.w_uncertainty


class ExperimentalStatus:
    """Current experimental status and comparisons."""

    # Framework prediction: Σmν = 60.9 meV for normal ordering
    FRAMEWORK_PREDICTION_MEV = 60.9

    # Framework dark energy: w = 0 (static cell vacuum)
    FRAMEWORK_DARK_ENERGY_W = 0.0

    @staticmethod
    def get_current_constraints() -> List[ExperimentalConstraint]:
        """Get list of current experimental constraints."""
        return [
            ExperimentalConstraint(
                name="Planck 2018 + BAO",
                year=2018,
                sum_nu_upper_limit_mev=120.0,
                confidence_level=0.95,
                sigma_level=2.0
            ),
            ExperimentalConstraint(
                name="DESI DR1",
                year=2024,
                sum_nu_upper_limit_mev=72.0,
                confidence_level=0.95,
                sigma_level=2.0
            ),
            ExperimentalConstraint(
                name="DESI DR2",
                year=2025,
                sum_nu_upper_limit_mev=53.0,
                confidence_level=0.95,
                sigma_level=2.0
            ),
            ExperimentalConstraint(
                name="DESI DR2 (tightest)",
                year=2025,
                sum_nu_upper_limit_mev=50.0,
                confidence_level=0.95,
                sigma_level=2.0
            ),
            ExperimentalConstraint(
                name="KATRIN",
                year=2025,
                sum_nu_upper_limit_mev=450.0,
                confidence_level=0.95,
                sigma_level=2.0
            ),
        ]

    @staticmethod
    def get_dark_energy_constraints() -> List[DarkEnergyConstraint]:
        """Get dark energy equation of state constraints."""
        return [
            DarkEnergyConstraint(
                name="Planck + DESI 2024",
                year=2024,
                w_central=-1.03,
                w_uncertainty=0.03
            )
        ]

    @staticmethod
    def generate_status_table() -> Dict[str, Dict]:
        """Generate comprehensive status table with tensions."""
        constraints = ExperimentalStatus.get_current_constraints()
        de_constraints = ExperimentalStatus.get_dark_energy_constraints()

        results = {}

        # Neutrino mass constraints
        for constraint in constraints:
            tension = constraint.compute_tension(
                ExperimentalStatus.FRAMEWORK_PREDICTION_MEV
            )

            status = "CONSISTENT"
            if tension > 3.0:
                status = "STRONG TENSION"
            elif tension > 2.0:
                status = "MODERATE TENSION"
            elif tension > 1.0:
                status = "WEAK TENSION"

            results[constraint.name] = {
                'year': constraint.year,
                'limit_mev': constraint.sum_nu_upper_limit_mev,
                'prediction_mev': ExperimentalStatus.FRAMEWORK_PREDICTION_MEV,
                'tension_sigma': tension,
                'status': status
            }

        # Dark energy constraints
        for constraint in de_constraints:
            tension = constraint.compute_tension(
                ExperimentalStatus.FRAMEWORK_DARK_ENERGY_W
            )

            status = "INCONSISTENT" if tension > 2.0 else "WEAK TENSION"

            results[constraint.name + " (w)"] = {
                'year': constraint.year,
                'w_measured': constraint.w_central,
                'w_prediction': ExperimentalStatus.FRAMEWORK_DARK_ENERGY_W,
                'tension_sigma': tension,
                'status': status
            }

        return results

    @staticmethod
    def plot_status_timeline(save_path: str = None) -> plt.Figure:
        """Plot experimental constraints vs time."""
        constraints = ExperimentalStatus.get_current_constraints()

        fig, ax = plt.subplots(figsize=(12, 6))

        years = [c.year for c in constraints if c.name != "KATRIN"]
        limits = [c.sum_nu_upper_limit_mev for c in constraints if c.name != "KATRIN"]
        names = [c.name for c in constraints if c.name != "KATRIN"]

        # Plot limits
        ax.scatter(years, limits, s=100, c='blue', marker='o', zorder=3)
        for year, limit, name in zip(years, limits, names):
            ax.annotate(name, (year, limit), xytext=(5, 5),
                       textcoords='offset points', fontsize=9)

        # Framework prediction
        ax.axhline(y=ExperimentalStatus.FRAMEWORK_PREDICTION_MEV,
                  color='red', linestyle='--', linewidth=2,
                  label='Framework prediction: 60.9 meV')

        # Falsification threshold
        ax.axhline(y=45, color='green', linestyle=':', linewidth=2,
                  label='Falsification threshold: < 45 meV')

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Σmν upper limit (meV, 95% CL)', fontsize=12)
        ax.set_title('Experimental Constraints on Neutrino Mass Sum', fontsize=14)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig


class FalsificationMap:
    """Map out when framework is falsified."""

    # Normal ordering gives Σmν ≥ 58.4 meV
    NORMAL_ORDERING_MIN_MEV = 58.4

    # Framework gives 60.9 meV (3 degenerate neutrinos)
    FRAMEWORK_PREDICTION_MEV = 60.9

    @staticmethod
    def framework_falsification_threshold(sigma_level: float = 3.0) -> float:
        """
        At what bound is framework killed?

        Framework: 60.9 meV
        Kill at 3σ: need limit < 60.9 - 3σ

        Conservative: assume σ ~ 5 meV → need limit < 45 meV
        """
        assumed_sigma_mev = 5.0
        return FalsificationMap.FRAMEWORK_PREDICTION_MEV - sigma_level * assumed_sigma_mev

    @staticmethod
    def normal_ordering_falsification_threshold(sigma_level: float = 5.0) -> float:
        """
        At what bound is normal ordering killed?

        Normal ordering minimum: 58.4 meV
        Kill at 5σ: need limit < 58.4 - 5σ

        Conservative: σ ~ 5 meV → need limit < 33 meV
        But more realistic: limit < 50 meV at high confidence
        """
        assumed_sigma_mev = 2.0
        return FalsificationMap.NORMAL_ORDERING_MIN_MEV - sigma_level * assumed_sigma_mev

    @staticmethod
    def generate_falsification_map() -> Dict[str, float]:
        """Generate falsification thresholds."""
        return {
            'framework_3sigma_threshold_mev': FalsificationMap.framework_falsification_threshold(3.0),
            'framework_5sigma_threshold_mev': FalsificationMap.framework_falsification_threshold(5.0),
            'normal_ordering_3sigma_threshold_mev': FalsificationMap.normal_ordering_falsification_threshold(3.0),
            'normal_ordering_5sigma_threshold_mev': FalsificationMap.normal_ordering_falsification_threshold(5.0),
        }

    @staticmethod
    def experiment_sensitivity() -> Dict[str, float]:
        """Expected sensitivities of upcoming experiments."""
        return {
            'DESI_DR3_2027': 40.0,  # meV
            'Euclid_2030': 30.0,
            'CMB-S4_2035': 18.0,
            'DUNE_2035': None,  # Mass ordering, not sum
            'JUNO_2030': None,  # Mass ordering, not sum
        }


class HubbleTensionSensitivity:
    """Analyze sensitivity to Hubble tension."""

    # Planck value
    H0_PLANCK = 67.4  # km/s/Mpc

    # SH0ES value
    H0_SHOES = 73.0  # km/s/Mpc

    # Omega_Lambda (dark energy density fraction)
    OMEGA_LAMBDA = 0.685

    @staticmethod
    def compute_rho_lambda(H0_km_s_mpc: float) -> float:
        """
        Compute dark energy density.

        ρ_Λ = 3H₀²Ω_Λ/(8πG)

        H0 in km/s/Mpc → convert to SI: 1 km/s/Mpc = 3.24e-20 m/s/m = (3.24e-20 m/s/m)/(3.086e22 m/Mpc) * (1000 m/km)
        Actually: 1 km/s/Mpc = (1000 m/s) / (3.086e22 m) = 3.24e-20 s⁻¹
        But more precisely: 1 km/s/Mpc = 1.022712165e-17 s⁻¹ (includes proper conversion)
        """
        # More precise conversion: 1 km/s/Mpc = 1000 m/s / (3.0857e22 m) = 3.24e-20 s⁻¹
        # But accounting for expansion: H0 ~ 70 km/s/Mpc ≈ 2.27e-18 s⁻¹
        # Proper conversion: 1 km/s/Mpc = 3.241e-20 Hz
        H0_SI = H0_km_s_mpc * 3.2407792896393e-20  # s⁻¹ (proper conversion)
        rho_lambda = 3 * H0_SI**2 * HubbleTensionSensitivity.OMEGA_LAMBDA / (8 * np.pi * G)
        return rho_lambda

    @staticmethod
    def compute_m1_from_rho(rho_lambda: float) -> float:
        """
        Compute m₁ from dark energy density.

        Assuming 3 degenerate neutrinos: ρ = 3·m⁴c³/ℏ³
        Therefore: m = (ρℏ³/(3c³))^(1/4)

        Returns m₁ in meV.
        """
        m_kg = (rho_lambda * HBAR**3 / (3 * C**3))**(1/4)
        m_joule = m_kg * C**2
        m_mev = m_joule / MEV_TO_JOULE
        return m_mev

    @staticmethod
    def analyze_hubble_sensitivity() -> Dict[str, float]:
        """Analyze how m₁ depends on H₀."""
        # Planck
        rho_planck = HubbleTensionSensitivity.compute_rho_lambda(
            HubbleTensionSensitivity.H0_PLANCK
        )
        m1_planck = HubbleTensionSensitivity.compute_m1_from_rho(rho_planck)

        # SH0ES
        rho_shoes = HubbleTensionSensitivity.compute_rho_lambda(
            HubbleTensionSensitivity.H0_SHOES
        )
        m1_shoes = HubbleTensionSensitivity.compute_m1_from_rho(rho_shoes)

        # Fractional uncertainty
        delta_H0 = HubbleTensionSensitivity.H0_SHOES - HubbleTensionSensitivity.H0_PLANCK
        delta_m1 = m1_shoes - m1_planck

        frac_uncertainty_H0 = delta_H0 / HubbleTensionSensitivity.H0_PLANCK
        frac_uncertainty_m1 = delta_m1 / m1_planck

        return {
            'H0_planck': HubbleTensionSensitivity.H0_PLANCK,
            'H0_shoes': HubbleTensionSensitivity.H0_SHOES,
            'rho_planck_J_m3': rho_planck,
            'rho_shoes_J_m3': rho_shoes,
            'm1_planck_mev': m1_planck,
            'm1_shoes_mev': m1_shoes,
            'sum_planck_mev': 3 * m1_planck,
            'sum_shoes_mev': 3 * m1_shoes,
            'frac_uncertainty_H0': frac_uncertainty_H0,
            'frac_uncertainty_m1': frac_uncertainty_m1,
            'fourth_root_damping': frac_uncertainty_m1 / frac_uncertainty_H0
        }

    @staticmethod
    def plot_m1_vs_H0(H0_range: np.ndarray = None) -> plt.Figure:
        """Plot m₁ dependence on H₀."""
        if H0_range is None:
            H0_range = np.linspace(65, 75, 100)

        m1_values = [HubbleTensionSensitivity.compute_m1_from_rho(
                        HubbleTensionSensitivity.compute_rho_lambda(H0))
                     for H0 in H0_range]

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(H0_range, m1_values, 'b-', linewidth=2)

        # Mark Planck and SH0ES
        result = HubbleTensionSensitivity.analyze_hubble_sensitivity()
        ax.scatter([result['H0_planck']], [result['m1_planck_mev']],
                  s=100, c='red', marker='o', label='Planck', zorder=3)
        ax.scatter([result['H0_shoes']], [result['m1_shoes_mev']],
                  s=100, c='green', marker='s', label='SH0ES', zorder=3)

        ax.set_xlabel('H₀ (km/s/Mpc)', fontsize=12)
        ax.set_ylabel('m₁ (meV)', fontsize=12)
        ax.set_title('Neutrino Mass Sensitivity to Hubble Tension', fontsize=14)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        # Add text box
        text = f"Fourth-root damping: {result['fourth_root_damping']:.3f}\n"
        text += f"Δm₁/m₁ ~ {result['frac_uncertainty_m1']:.3f}"
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
               fontsize=10)

        plt.tight_layout()
        return fig


class DarkMatterInterpretation:
    """Analyze if cell vacuum is DM instead of DE (since w=0)."""

    # Dark matter density
    RHO_DM = 2.4e-10  # J/m³ (approximate)

    @staticmethod
    def compute_dm_mass() -> Dict[str, float]:
        """
        If cell vacuum is dark matter:

        Match ρ_DM instead of ρ_Λ
        ρ_DM ~ 2.4e-10 J/m³ (compared to ρ_Λ ~ 5.8e-10 J/m³)
        """
        rho_dm = DarkMatterInterpretation.RHO_DM

        # For 3 degenerate neutrinos
        m_kg = (rho_dm * HBAR**3 / (3 * C**3))**(1/4)
        m_joule = m_kg * C**2
        m_mev = m_joule / MEV_TO_JOULE

        sum_mev = 3 * m_mev

        return {
            'rho_dm_J_m3': rho_dm,
            'm1_dm_mev': m_mev,
            'sum_dm_mev': sum_mev,
            'interpretation': 'Dark Matter' if sum_mev < 55 else 'Dark Energy'
        }

    @staticmethod
    def compare_de_vs_dm() -> Dict[str, Dict]:
        """Compare DE vs DM interpretations."""
        # DE interpretation (H0 = 67.4)
        rho_de = HubbleTensionSensitivity.compute_rho_lambda(67.4)
        m1_de = HubbleTensionSensitivity.compute_m1_from_rho(rho_de)

        # DM interpretation
        dm_result = DarkMatterInterpretation.compute_dm_mass()

        return {
            'dark_energy': {
                'rho_J_m3': rho_de,
                'm1_mev': m1_de,
                'sum_mev': 3 * m1_de,
                'w': 0,
                'status_vs_DESI': 'TENSION' if 3*m1_de > 53 else 'OK'
            },
            'dark_matter': {
                'rho_J_m3': dm_result['rho_dm_J_m3'],
                'm1_mev': dm_result['m1_dm_mev'],
                'sum_mev': dm_result['sum_dm_mev'],
                'w': 0,
                'status_vs_DESI': 'TENSION' if dm_result['sum_dm_mev'] > 53 else 'OK'
            }
        }


class ProbabilityTimeline:
    """Model framework probability over time based on experiments."""

    @dataclass
    class FutureExperiment:
        name: str
        year: int
        sensitivity_mev: float
        will_measure_ordering: bool = False

    @staticmethod
    def get_future_experiments() -> List['ProbabilityTimeline.FutureExperiment']:
        """List of upcoming experiments."""
        return [
            ProbabilityTimeline.FutureExperiment("DESI DR2", 2025, 50.0),
            ProbabilityTimeline.FutureExperiment("JUNO", 2028, 999, will_measure_ordering=True),
            ProbabilityTimeline.FutureExperiment("DESI DR3", 2027, 40.0),
            ProbabilityTimeline.FutureExperiment("Euclid", 2030, 30.0),
            ProbabilityTimeline.FutureExperiment("DUNE", 2032, 999, will_measure_ordering=True),
            ProbabilityTimeline.FutureExperiment("CMB-S4", 2035, 18.0),
        ]

    @staticmethod
    def estimate_survival_probability(sensitivity_mev: float,
                                     prediction_mev: float = 60.9,
                                     uncertainty_mev: float = 3.0) -> float:
        """
        Estimate probability framework survives given sensitivity.

        Assume measurement gets sensitivity_mev as upper limit.
        Framework prediction is 60.9 ± 3 meV.

        P(survive) = P(true value < sensitivity_mev | prediction)
        """
        # Z-score
        z = (sensitivity_mev - prediction_mev) / uncertainty_mev

        # Survival probability
        p_survive = norm.cdf(z)

        return p_survive

    @staticmethod
    def generate_timeline() -> List[Dict]:
        """Generate probability timeline."""
        experiments = ProbabilityTimeline.get_future_experiments()

        timeline = []
        cumulative_prob = 1.0

        for exp in sorted(experiments, key=lambda x: x.year):
            if exp.will_measure_ordering:
                # Ordering measurement doesn't directly constrain sum
                # But rules out inverted ordering → sets floor at 58.4 meV
                event = {
                    'year': exp.year,
                    'experiment': exp.name,
                    'type': 'ordering',
                    'impact': 'Rules out inverted ordering',
                    'cumulative_probability': cumulative_prob
                }
            else:
                # Mass sum constraint
                p_survive = ProbabilityTimeline.estimate_survival_probability(
                    exp.sensitivity_mev
                )

                cumulative_prob *= p_survive

                event = {
                    'year': exp.year,
                    'experiment': exp.name,
                    'type': 'mass_sum',
                    'sensitivity_mev': exp.sensitivity_mev,
                    'survival_probability': p_survive,
                    'cumulative_probability': cumulative_prob
                }

            timeline.append(event)

        return timeline

    @staticmethod
    def plot_probability_timeline() -> plt.Figure:
        """Plot framework survival probability over time."""
        timeline = ProbabilityTimeline.generate_timeline()

        # Extract mass sum experiments
        mass_experiments = [e for e in timeline if e['type'] == 'mass_sum']

        years = [e['year'] for e in mass_experiments]
        probs = [e['cumulative_probability'] for e in mass_experiments]
        names = [e['experiment'] for e in mass_experiments]

        fig, ax = plt.subplots(figsize=(12, 7))

        ax.plot(years, probs, 'b-', linewidth=2, marker='o', markersize=8)

        # Annotate experiments
        for year, prob, name in zip(years, probs, names):
            ax.annotate(name, (year, prob), xytext=(0, 10),
                       textcoords='offset points', fontsize=10,
                       ha='center')

        ax.axhline(y=0.05, color='r', linestyle='--', linewidth=1.5,
                  label='5% threshold (effective falsification)')
        ax.axhline(y=0.5, color='orange', linestyle=':', linewidth=1.5,
                  label='50% survival')

        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Framework Survival Probability', fontsize=12)
        ax.set_title('Two Vacua Theory: Probability Timeline', fontsize=14)
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        # Add critical period shading
        ax.axvspan(2025, 2030, alpha=0.2, color='yellow', label='Critical Period')

        plt.tight_layout()
        return fig


def generate_full_experimental_report() -> Dict:
    """Generate complete experimental comparison report."""
    print("Generating experimental comparison report...")

    report = {
        'current_status': ExperimentalStatus.generate_status_table(),
        'falsification_map': FalsificationMap.generate_falsification_map(),
        'experiment_sensitivities': FalsificationMap.experiment_sensitivity(),
        'hubble_sensitivity': HubbleTensionSensitivity.analyze_hubble_sensitivity(),
        'dm_interpretation': DarkMatterInterpretation.compute_dm_mass(),
        'de_vs_dm_comparison': DarkMatterInterpretation.compare_de_vs_dm(),
        'probability_timeline': ProbabilityTimeline.generate_timeline()
    }

    return report


if __name__ == '__main__':
    print("=" * 80)
    print("EXPERIMENTAL COMPARISON: TWO VACUA THEORY")
    print("=" * 80)

    report = generate_full_experimental_report()

    print("\n" + "=" * 80)
    print("1. CURRENT EXPERIMENTAL STATUS")
    print("=" * 80)

    for name, result in report['current_status'].items():
        if 'limit_mev' in result:
            print(f"\n{name} ({result['year']})")
            print(f"   Limit: {result['limit_mev']} meV")
            print(f"   Prediction: {result['prediction_mev']} meV")
            print(f"   Tension: {result['tension_sigma']:.1f} sigma")
            print(f"   Status: {result['status']}")
        else:
            print(f"\n{name} ({result['year']})")
            print(f"   w measured: {result['w_measured']:.2f}")
            print(f"   w prediction: {result['w_prediction']:.2f}")
            print(f"   Tension: {result['tension_sigma']:.1f} sigma")
            print(f"   Status: {result['status']}")

    print("\n" + "=" * 80)
    print("2. FALSIFICATION MAP")
    print("=" * 80)

    fmap = report['falsification_map']
    print(f"\nFramework killed at 3 sigma: Sum < {fmap['framework_3sigma_threshold_mev']:.1f} meV")
    print(f"Framework killed at 5 sigma: Sum < {fmap['framework_5sigma_threshold_mev']:.1f} meV")
    print(f"Normal ordering killed at 3 sigma: Sum < {fmap['normal_ordering_3sigma_threshold_mev']:.1f} meV")
    print(f"Normal ordering killed at 5 sigma: Sum < {fmap['normal_ordering_5sigma_threshold_mev']:.1f} meV")

    print("\n" + "=" * 80)
    print("3. HUBBLE TENSION SENSITIVITY")
    print("=" * 80)

    hub = report['hubble_sensitivity']
    print(f"\nPlanck (H0 = {hub['H0_planck']:.1f}): Sum = {hub['sum_planck_mev']:.1f} meV")
    print(f"SH0ES (H0 = {hub['H0_shoes']:.1f}): Sum = {hub['sum_shoes_mev']:.1f} meV")
    print(f"Fourth-root damping factor: {hub['fourth_root_damping']:.3f}")
    print(f"Fractional uncertainty in m1: {hub['frac_uncertainty_m1']:.1%}")

    print("\n" + "=" * 80)
    print("4. DARK MATTER INTERPRETATION (w=0)")
    print("=" * 80)

    comparison = report['de_vs_dm_comparison']
    print("\nDark Energy interpretation:")
    print(f"   rho = {comparison['dark_energy']['rho_J_m3']:.2e} J/m^3")
    print(f"   Sum = {comparison['dark_energy']['sum_mev']:.1f} meV")
    print(f"   Status vs DESI DR2: {comparison['dark_energy']['status_vs_DESI']}")

    print("\nDark Matter interpretation:")
    print(f"   rho = {comparison['dark_matter']['rho_J_m3']:.2e} J/m^3")
    print(f"   Sum = {comparison['dark_matter']['sum_mev']:.1f} meV")
    print(f"   Status vs DESI DR2: {comparison['dark_matter']['status_vs_DESI']}")

    print("\n" + "=" * 80)
    print("5. PROBABILITY TIMELINE")
    print("=" * 80)

    for event in report['probability_timeline']:
        if event['type'] == 'mass_sum':
            print(f"\n{event['year']} - {event['experiment']}")
            print(f"   Sensitivity: {event['sensitivity_mev']:.0f} meV")
            print(f"   Survival probability: {event['survival_probability']:.1%}")
            print(f"   Cumulative: {event['cumulative_probability']:.1%}")
        else:
            print(f"\n{event['year']} - {event['experiment']}")
            print(f"   {event['impact']}")

    print("\n" + "=" * 80)
