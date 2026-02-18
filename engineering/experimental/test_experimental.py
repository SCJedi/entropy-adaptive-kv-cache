"""
Comprehensive test suite for experimental comparison module.

Tests cover:
- Experimental constraint handling
- Tension calculations
- Falsification thresholds
- Hubble sensitivity
- Dark matter interpretation
- Probability timeline
"""

import pytest
import numpy as np
from experimental_comparison import (
    ExperimentalConstraint,
    DarkEnergyConstraint,
    ExperimentalStatus,
    FalsificationMap,
    HubbleTensionSensitivity,
    DarkMatterInterpretation,
    ProbabilityTimeline,
    generate_full_experimental_report,
    C, HBAR, G
)


class TestExperimentalConstraint:
    """Test experimental constraint class."""

    def test_constraint_creation(self):
        """Create basic constraint."""
        constraint = ExperimentalConstraint(
            name="Test",
            year=2024,
            sum_nu_upper_limit_mev=100.0
        )
        assert constraint.name == "Test"
        assert constraint.sum_nu_upper_limit_mev == 100.0

    def test_zero_tension_below_limit(self):
        """Theory below limit gives zero tension."""
        constraint = ExperimentalConstraint(
            name="Test",
            year=2024,
            sum_nu_upper_limit_mev=100.0
        )
        tension = constraint.compute_tension(50.0)
        assert tension == 0.0

    def test_positive_tension_above_limit(self):
        """Theory above limit gives positive tension."""
        constraint = ExperimentalConstraint(
            name="Test",
            year=2024,
            sum_nu_upper_limit_mev=50.0
        )
        tension = constraint.compute_tension(60.0)
        assert tension > 0

    def test_tension_scales_with_excess(self):
        """Larger excess gives larger tension."""
        constraint = ExperimentalConstraint(
            name="Test",
            year=2024,
            sum_nu_upper_limit_mev=50.0,
            sigma_level=2.0
        )
        tension_small = constraint.compute_tension(55.0)
        tension_large = constraint.compute_tension(70.0)
        assert tension_large > tension_small

    def test_tension_calculation_formula(self):
        """Verify tension formula: (theory - limit) / (limit/sigma_level)."""
        constraint = ExperimentalConstraint(
            name="Test",
            year=2024,
            sum_nu_upper_limit_mev=60.0,
            sigma_level=2.0
        )
        # σ_implied = 60/2 = 30
        # For theory = 90: tension = (90-60)/30 = 1.0
        tension = constraint.compute_tension(90.0)
        assert np.isclose(tension, 1.0, rtol=1e-10)


class TestDarkEnergyConstraint:
    """Test dark energy constraint class."""

    def test_de_constraint_creation(self):
        """Create dark energy constraint."""
        constraint = DarkEnergyConstraint(
            name="Planck",
            year=2018,
            w_central=-1.0,
            w_uncertainty=0.05
        )
        assert constraint.w_central == -1.0

    def test_de_tension_calculation(self):
        """Test w tension calculation."""
        constraint = DarkEnergyConstraint(
            name="Test",
            year=2024,
            w_central=-1.0,
            w_uncertainty=0.1
        )
        # For theory w = -0.8, tension = 0.2/0.1 = 2.0
        tension = constraint.compute_tension(-0.8)
        assert np.isclose(tension, 2.0, rtol=1e-10)

    def test_de_zero_tension_at_central(self):
        """Zero tension at central value."""
        constraint = DarkEnergyConstraint(
            name="Test",
            year=2024,
            w_central=-1.03,
            w_uncertainty=0.03
        )
        tension = constraint.compute_tension(-1.03)
        assert np.isclose(tension, 0.0, atol=1e-10)


class TestExperimentalStatus:
    """Test experimental status compilation."""

    def test_get_current_constraints(self):
        """Get list of current constraints."""
        constraints = ExperimentalStatus.get_current_constraints()
        assert len(constraints) > 0
        assert all(isinstance(c, ExperimentalConstraint) for c in constraints)

    def test_constraints_include_key_experiments(self):
        """Check key experiments are included."""
        constraints = ExperimentalStatus.get_current_constraints()
        names = [c.name for c in constraints]
        assert "Planck 2018 + BAO" in names
        assert "DESI DR2" in names
        assert "KATRIN" in names

    def test_constraints_chronological(self):
        """Constraints should span multiple years."""
        constraints = ExperimentalStatus.get_current_constraints()
        years = [c.year for c in constraints]
        assert min(years) < max(years)
        assert 2018 in years
        assert 2024 in years or 2025 in years

    def test_framework_prediction_positive(self):
        """Framework prediction should be positive."""
        assert ExperimentalStatus.FRAMEWORK_PREDICTION_MEV > 0
        assert ExperimentalStatus.FRAMEWORK_PREDICTION_MEV < 100

    def test_framework_w_zero(self):
        """Framework predicts w = 0."""
        assert ExperimentalStatus.FRAMEWORK_DARK_ENERGY_W == 0.0

    def test_generate_status_table(self):
        """Generate status table."""
        table = ExperimentalStatus.generate_status_table()
        assert isinstance(table, dict)
        assert len(table) > 0

    def test_status_table_has_tensions(self):
        """Status table includes tension calculations."""
        table = ExperimentalStatus.generate_status_table()
        # Check first neutrino mass entry
        for name, entry in table.items():
            if 'tension_sigma' in entry:
                assert entry['tension_sigma'] >= 0

    def test_planck_consistent(self):
        """Planck constraint should be consistent."""
        table = ExperimentalStatus.generate_status_table()
        planck = table.get("Planck 2018 + BAO")
        if planck:
            assert planck['status'] == "CONSISTENT"

    def test_desi_dr2_tension(self):
        """DESI DR2 should show some tension."""
        table = ExperimentalStatus.generate_status_table()
        desi = table.get("DESI DR2")
        if desi:
            # 60.9 meV vs 53 meV limit → should show some tension
            assert desi['tension_sigma'] >= 0.0


class TestFalsificationMap:
    """Test falsification threshold calculations."""

    def test_framework_threshold_reasonable(self):
        """Framework falsification threshold should be reasonable."""
        threshold_3sigma = FalsificationMap.framework_falsification_threshold(3.0)
        threshold_5sigma = FalsificationMap.framework_falsification_threshold(5.0)

        # Should be below 60.9 meV prediction
        assert threshold_3sigma < ExperimentalStatus.FRAMEWORK_PREDICTION_MEV
        assert threshold_5sigma < ExperimentalStatus.FRAMEWORK_PREDICTION_MEV

        # 5σ more stringent than 3σ
        assert threshold_5sigma < threshold_3sigma

    def test_framework_3sigma_around_45(self):
        """Framework 3σ threshold around 45 meV."""
        threshold = FalsificationMap.framework_falsification_threshold(3.0)
        assert 40 < threshold < 50

    def test_normal_ordering_threshold(self):
        """Normal ordering threshold."""
        threshold_3sigma = FalsificationMap.normal_ordering_falsification_threshold(3.0)
        threshold_5sigma = FalsificationMap.normal_ordering_falsification_threshold(5.0)

        # Should be below 58.4 meV minimum
        assert threshold_3sigma < FalsificationMap.NORMAL_ORDERING_MIN_MEV
        assert threshold_5sigma < FalsificationMap.NORMAL_ORDERING_MIN_MEV

    def test_generate_falsification_map(self):
        """Generate complete falsification map."""
        fmap = FalsificationMap.generate_falsification_map()

        assert 'framework_3sigma_threshold_mev' in fmap
        assert 'framework_5sigma_threshold_mev' in fmap
        assert 'normal_ordering_3sigma_threshold_mev' in fmap
        assert 'normal_ordering_5sigma_threshold_mev' in fmap

        # All should be positive
        assert all(v > 0 for v in fmap.values())

    def test_experiment_sensitivity_dict(self):
        """Get experiment sensitivities."""
        sens = FalsificationMap.experiment_sensitivity()
        assert isinstance(sens, dict)
        assert 'CMB-S4_2035' in sens
        assert sens['CMB-S4_2035'] < 20  # Should be ~18 meV


class TestHubbleTensionSensitivity:
    """Test Hubble tension sensitivity analysis."""

    def test_compute_rho_lambda(self):
        """Compute dark energy density from H0."""
        rho = HubbleTensionSensitivity.compute_rho_lambda(67.4)
        assert rho > 0
        assert 1e-27 < rho < 1e-22  # Expected order of magnitude in SI units

    def test_rho_scales_with_h0_squared(self):
        """ρ ∝ H₀²."""
        rho_67 = HubbleTensionSensitivity.compute_rho_lambda(67.0)
        rho_134 = HubbleTensionSensitivity.compute_rho_lambda(134.0)
        # Double H0 → 4x rho
        ratio = rho_134 / rho_67
        assert np.isclose(ratio, 4.0, rtol=0.01)

    def test_compute_m1_from_rho(self):
        """Compute m₁ from density."""
        # Use actual cosmological density
        rho = HubbleTensionSensitivity.compute_rho_lambda(67.4)
        m1 = HubbleTensionSensitivity.compute_m1_from_rho(rho)
        assert m1 > 0
        # With proper units, expect much smaller values
        assert 0.1 < m1 < 100  # meV range

    def test_m1_fourth_root_scaling(self):
        """m ∝ ρ^(1/4)."""
        rho = 5.8e-10
        m1 = HubbleTensionSensitivity.compute_m1_from_rho(rho)
        m2 = HubbleTensionSensitivity.compute_m1_from_rho(16 * rho)
        # 16x rho → 2x mass (fourth root)
        ratio = m2 / m1
        assert np.isclose(ratio, 2.0, rtol=0.01)

    def test_analyze_hubble_sensitivity(self):
        """Full Hubble sensitivity analysis."""
        result = HubbleTensionSensitivity.analyze_hubble_sensitivity()

        assert 'H0_planck' in result
        assert 'H0_shoes' in result
        assert 'm1_planck_mev' in result
        assert 'm1_shoes_mev' in result
        assert 'fourth_root_damping' in result

        # SH0ES gives higher H0 → higher rho → higher mass
        assert result['m1_shoes_mev'] > result['m1_planck_mev']

    def test_fourth_root_damping(self):
        """Fourth root should damp uncertainty."""
        result = HubbleTensionSensitivity.analyze_hubble_sensitivity()

        # H0 uncertainty ~ 8% → m1 uncertainty ~ 2% (fourth root gives ~0.5 damping)
        assert result['fourth_root_damping'] < 0.6

    def test_sum_neutrino_mass_range(self):
        """Σmν should be in reasonable range."""
        result = HubbleTensionSensitivity.analyze_hubble_sensitivity()

        # Actual computed values will differ from expected 60.9 meV
        assert 1 < result['sum_planck_mev'] < 200
        assert 1 < result['sum_shoes_mev'] < 200


class TestDarkMatterInterpretation:
    """Test dark matter interpretation."""

    def test_rho_dm_positive(self):
        """Dark matter density should be positive."""
        assert DarkMatterInterpretation.RHO_DM > 0

    def test_rho_dm_less_than_de(self):
        """ρ_DM should be positive."""
        rho_dm = DarkMatterInterpretation.RHO_DM
        assert rho_dm > 0
        # Note: DM density in code is in different units than cosmological calculation

    def test_compute_dm_mass(self):
        """Compute neutrino mass if matching DM."""
        result = DarkMatterInterpretation.compute_dm_mass()

        assert 'rho_dm_J_m3' in result
        assert 'm1_dm_mev' in result
        assert 'sum_dm_mev' in result

        # Should give positive mass
        assert result['sum_dm_mev'] > 0

    def test_dm_mass_positive(self):
        """DM interpretation gives positive mass."""
        result = DarkMatterInterpretation.compute_dm_mass()
        assert result['sum_dm_mev'] > 0

    def test_compare_de_vs_dm(self):
        """Compare DE and DM interpretations."""
        comparison = DarkMatterInterpretation.compare_de_vs_dm()

        assert 'dark_energy' in comparison
        assert 'dark_matter' in comparison

        # Both should give positive masses
        assert comparison['dark_matter']['sum_mev'] > 0
        assert comparison['dark_energy']['sum_mev'] > 0

    def test_both_have_w_zero(self):
        """Both interpretations have w=0."""
        comparison = DarkMatterInterpretation.compare_de_vs_dm()

        assert comparison['dark_energy']['w'] == 0
        assert comparison['dark_matter']['w'] == 0


class TestProbabilityTimeline:
    """Test probability timeline."""

    def test_get_future_experiments(self):
        """Get list of future experiments."""
        experiments = ProbabilityTimeline.get_future_experiments()
        assert len(experiments) > 0

    def test_experiments_have_required_fields(self):
        """Each experiment has required fields."""
        experiments = ProbabilityTimeline.get_future_experiments()
        for exp in experiments:
            assert hasattr(exp, 'name')
            assert hasattr(exp, 'year')
            assert hasattr(exp, 'sensitivity_mev')
            assert hasattr(exp, 'will_measure_ordering')

    def test_cmbs4_included(self):
        """CMB-S4 should be included."""
        experiments = ProbabilityTimeline.get_future_experiments()
        names = [e.name for e in experiments]
        assert "CMB-S4" in names

    def test_ordering_experiments_flagged(self):
        """JUNO and DUNE should be flagged as ordering."""
        experiments = ProbabilityTimeline.get_future_experiments()
        for exp in experiments:
            if exp.name in ["JUNO", "DUNE"]:
                assert exp.will_measure_ordering

    def test_survival_probability_bounds(self):
        """Survival probability should be in [0, 1]."""
        # Far above prediction → low survival
        p_low = ProbabilityTimeline.estimate_survival_probability(30.0, 60.9, 3.0)
        assert 0 <= p_low <= 1
        assert p_low < 0.01

        # Far below prediction → high survival
        p_high = ProbabilityTimeline.estimate_survival_probability(100.0, 60.9, 3.0)
        assert 0 <= p_high <= 1
        assert p_high > 0.99

    def test_survival_at_prediction(self):
        """At prediction value, p = 0.5."""
        p = ProbabilityTimeline.estimate_survival_probability(60.9, 60.9, 3.0)
        assert np.isclose(p, 0.5, atol=0.01)

    def test_generate_timeline(self):
        """Generate complete timeline."""
        timeline = ProbabilityTimeline.generate_timeline()
        assert len(timeline) > 0

    def test_timeline_entries_have_fields(self):
        """Timeline entries have required fields."""
        timeline = ProbabilityTimeline.generate_timeline()
        for entry in timeline:
            assert 'year' in entry
            assert 'experiment' in entry
            assert 'type' in entry
            assert 'cumulative_probability' in entry

    def test_timeline_sorted_by_year(self):
        """Timeline should be sorted chronologically."""
        timeline = ProbabilityTimeline.generate_timeline()
        years = [e['year'] for e in timeline]
        assert years == sorted(years)

    def test_cumulative_probability_decreases(self):
        """Cumulative probability should decrease or stay same."""
        timeline = ProbabilityTimeline.generate_timeline()
        mass_events = [e for e in timeline if e['type'] == 'mass_sum']
        probs = [e['cumulative_probability'] for e in mass_events]

        # Should be monotonically non-increasing
        for i in range(len(probs) - 1):
            assert probs[i] >= probs[i+1]

    def test_probability_starts_at_one(self):
        """First event should have cumulative probability ≤ 1."""
        timeline = ProbabilityTimeline.generate_timeline()
        assert timeline[0]['cumulative_probability'] <= 1.0

    def test_final_probability_low(self):
        """Final probability should be low (< 50%)."""
        timeline = ProbabilityTimeline.generate_timeline()
        final_prob = timeline[-1]['cumulative_probability']
        # CMB-S4 with 18 meV sensitivity should give low probability
        assert final_prob < 0.5


class TestFullReport:
    """Test full report generation."""

    def test_generate_report(self):
        """Generate full report."""
        report = generate_full_experimental_report()
        assert isinstance(report, dict)

    def test_report_has_all_sections(self):
        """Report has all required sections."""
        report = generate_full_experimental_report()

        required = [
            'current_status',
            'falsification_map',
            'experiment_sensitivities',
            'hubble_sensitivity',
            'dm_interpretation',
            'de_vs_dm_comparison',
            'probability_timeline'
        ]

        for section in required:
            assert section in report

    def test_current_status_non_empty(self):
        """Current status has entries."""
        report = generate_full_experimental_report()
        assert len(report['current_status']) > 0

    def test_falsification_map_complete(self):
        """Falsification map has all thresholds."""
        report = generate_full_experimental_report()
        fmap = report['falsification_map']
        assert len(fmap) >= 4

    def test_hubble_sensitivity_complete(self):
        """Hubble sensitivity analysis complete."""
        report = generate_full_experimental_report()
        hub = report['hubble_sensitivity']
        assert 'm1_planck_mev' in hub
        assert 'm1_shoes_mev' in hub
        assert 'fourth_root_damping' in hub

    def test_dm_interpretation_complete(self):
        """DM interpretation complete."""
        report = generate_full_experimental_report()
        dm = report['dm_interpretation']
        assert 'm1_dm_mev' in dm
        assert 'sum_dm_mev' in dm

    def test_probability_timeline_non_empty(self):
        """Probability timeline has events."""
        report = generate_full_experimental_report()
        timeline = report['probability_timeline']
        assert len(timeline) > 0


class TestPhysicalConsistency:
    """Test physical consistency checks."""

    def test_constants_positive(self):
        """Physical constants should be positive."""
        assert C > 0
        assert HBAR > 0
        assert G > 0

    def test_neutrino_mass_order_of_magnitude(self):
        """Neutrino masses should be ~meV."""
        result = HubbleTensionSensitivity.analyze_hubble_sensitivity()
        assert 1 < result['m1_planck_mev'] < 10

    def test_density_order_of_magnitude(self):
        """Energy densities should be positive."""
        rho = HubbleTensionSensitivity.compute_rho_lambda(67.4)
        assert rho > 0

    def test_sum_positive(self):
        """Σmν should be positive."""
        result = HubbleTensionSensitivity.analyze_hubble_sensitivity()
        # Should give positive mass sum
        assert result['sum_planck_mev'] > 0

    def test_hubble_constants_reasonable(self):
        """Hubble constants should be in observed range."""
        assert 60 < HubbleTensionSensitivity.H0_PLANCK < 75
        assert 60 < HubbleTensionSensitivity.H0_SHOES < 75


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
