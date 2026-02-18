"""
Comprehensive test suite for AQFT verification module.

Tests cover:
- Orthogonality computations
- Unitary inequivalence criteria
- Hadamard condition preservation
- Curved spacetime consistency
- Parker particle creation
- Entanglement properties
- Black hole entropy tension
"""

import pytest
import numpy as np
from aqft_verification import (
    OrthogonalityVerification,
    UnitaryInequivalence,
    HadamardCondition,
    CurvedSpacetimeSelfConsistency,
    ParkerParticleCreation,
    EntanglementVerification,
    BlackHoleEntropyTension,
    VacuumParameters,
    generate_full_verification_report,
    HBAR, C, G, L_PLANCK
)


class TestVacuumParameters:
    """Test vacuum parameter calculations."""

    def test_default_neutrino_mass(self):
        params = VacuumParameters()
        assert params.neutrino_mass_mev == 2.31

    def test_mass_conversion(self):
        params = VacuumParameters(neutrino_mass_mev=2.31)
        # 2.31 meV = 2.31e-3 * 1.6e-19 J = 3.696e-22 J
        # m = E/c² ~ 4.1e-39 kg
        assert 3e-39 < params.neutrino_mass_kg < 5e-39

    def test_compton_wavelength(self):
        params = VacuumParameters(neutrino_mass_mev=2.31)
        # λ_C = ℏ/(mc) ~ 0.085 mm for 2.31 meV
        assert 5e-5 < params.compton_wavelength < 1.5e-4

    def test_frequency_positive(self):
        params = VacuumParameters(neutrino_mass_mev=2.31)
        assert params.frequency > 0


class TestOrthogonalityVerification:
    """Test orthogonality between vacua."""

    def test_overlap_single_cell(self):
        """Single cell with α=1/√2 gives exp(-1/4)."""
        overlap = OrthogonalityVerification.compute_overlap(1)
        expected = np.exp(-0.25)
        assert np.isclose(overlap, expected, rtol=1e-10)

    def test_overlap_decreases_with_N(self):
        """Overlap should decrease exponentially with N."""
        overlap_10 = OrthogonalityVerification.compute_overlap(10)
        overlap_100 = OrthogonalityVerification.compute_overlap(100)
        assert overlap_100 < overlap_10

    def test_overlap_exponential_decay(self):
        """Verify exp(-N/4) scaling."""
        N = 20
        alpha = 1/np.sqrt(2)
        overlap = OrthogonalityVerification.compute_overlap(N, alpha)
        expected = np.exp(-N * alpha**2 / 2)
        assert np.isclose(overlap, expected, rtol=1e-10)

    def test_epsilon_threshold(self):
        """Find N where overlap < machine epsilon."""
        N_threshold = OrthogonalityVerification.find_epsilon_threshold(1e-16)
        overlap = OrthogonalityVerification.compute_overlap(N_threshold)
        assert overlap < 1e-16

    def test_epsilon_threshold_reasonable(self):
        """N threshold should be reasonable (~295 for alpha=1/sqrt(2))."""
        N_threshold = OrthogonalityVerification.find_epsilon_threshold(1e-16)
        assert 200 < N_threshold < 400

    def test_generate_decay_data_shape(self):
        """Decay data should have correct shape."""
        n_vals, overlaps = OrthogonalityVerification.generate_decay_data(100)
        assert len(n_vals) == 100
        assert len(overlaps) == 100

    def test_decay_data_monotonic(self):
        """Overlaps should monotonically decrease."""
        n_vals, overlaps = OrthogonalityVerification.generate_decay_data(50)
        assert np.all(np.diff(overlaps) < 0)

    def test_different_alpha_values(self):
        """Test with different displacement values."""
        alpha_small = 0.1
        alpha_large = 1.0
        overlap_small = OrthogonalityVerification.compute_overlap(10, alpha_small)
        overlap_large = OrthogonalityVerification.compute_overlap(10, alpha_large)
        # Larger α gives smaller overlap
        assert overlap_large < overlap_small


class TestUnitaryInequivalence:
    """Test unitary inequivalence via Shale-Stinespring."""

    def test_divergent_norm_linear(self):
        """Divergent case: ||α||² = N/2."""
        N = 100
        norm_sq = UnitaryInequivalence.displacement_norm_squared(N)
        assert np.isclose(norm_sq, N/2, rtol=1e-10)

    def test_divergent_norm_increases(self):
        """Norm should increase linearly with N."""
        norm_100 = UnitaryInequivalence.displacement_norm_squared(100)
        norm_1000 = UnitaryInequivalence.displacement_norm_squared(1000)
        assert norm_1000 > norm_100
        assert np.isclose(norm_1000 / norm_100, 10, rtol=1e-10)

    def test_convergent_case_approaches_limit(self):
        """Convergent case should approach π²/12."""
        limit = np.pi**2 / 12
        norm_100 = UnitaryInequivalence.convergent_case_norm_squared(100)
        norm_10000 = UnitaryInequivalence.convergent_case_norm_squared(10000)
        # Should be monotonically approaching limit
        assert norm_10000 > norm_100
        assert norm_10000 < limit
        # Should be close to limit for large N
        assert np.isclose(norm_10000, limit, rtol=1e-3)

    def test_convergent_norm_bounded(self):
        """Convergent norm should stay bounded."""
        norm = UnitaryInequivalence.convergent_case_norm_squared(100000)
        assert norm < 1.0

    def test_shale_stinespring_criterion_met(self):
        """For N > 1000, divergent norm >> 1, criterion met."""
        norm = UnitaryInequivalence.displacement_norm_squared(1000)
        assert norm > 100  # Far exceeds any finite bound


class TestHadamardCondition:
    """Test Hadamard condition preservation."""

    def test_correction_basic(self):
        """Basic correction computation."""
        x = np.linspace(0, 1, 100)
        cell_pos = np.array([0.5])
        cell_amp = np.array([1.0])
        F_x = HadamardCondition.two_point_function_correction(
            x, cell_pos, cell_amp, 0.1
        )
        assert len(F_x) == len(x)
        assert np.all(np.isfinite(F_x))

    def test_correction_peaked_at_cell(self):
        """Correction should be peaked at cell position."""
        x = np.linspace(0, 1, 1000)
        cell_pos = np.array([0.5])
        cell_amp = np.array([1.0])
        F_x = HadamardCondition.two_point_function_correction(
            x, cell_pos, cell_amp, 0.01
        )
        # Find peak location
        peak_idx = np.argmax(F_x)
        peak_pos = x[peak_idx]
        assert np.isclose(peak_pos, 0.5, atol=0.01)

    def test_multiple_cells_superposition(self):
        """Multiple cells should give superposition."""
        x = np.linspace(0, 1, 500)
        cell_pos = np.array([0.3, 0.7])
        cell_amp = np.array([1.0, 1.0])
        F_x = HadamardCondition.two_point_function_correction(
            x, cell_pos, cell_amp, 0.05
        )
        # Should have two peaks
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(F_x, height=0.5)
        assert len(peaks) >= 2

    def test_smoothness_verification(self):
        """Verify smoothness metrics are computed."""
        x = np.linspace(0, 1, 1000)
        cell_pos = np.array([0.5])
        cell_amp = np.array([1.0])
        F_x = HadamardCondition.two_point_function_correction(
            x, cell_pos, cell_amp, 0.1
        )
        metrics = HadamardCondition.verify_smoothness(x, F_x)

        assert 'max_F' in metrics
        assert 'max_dF' in metrics
        assert 'max_d2F' in metrics
        assert bool(metrics['continuity']) is True
        assert bool(metrics['differentiability']) is True

    def test_smoothness_all_finite(self):
        """All derivatives should be finite."""
        x = np.linspace(0, 1, 500)
        cell_pos = np.array([0.25, 0.75])
        cell_amp = np.ones(2)
        F_x = HadamardCondition.two_point_function_correction(
            x, cell_pos, cell_amp, 0.05
        )
        metrics = HadamardCondition.verify_smoothness(x, F_x)

        assert np.isfinite(metrics['max_F'])
        assert np.isfinite(metrics['max_dF'])
        assert np.isfinite(metrics['max_d2F'])


class TestCurvedSpacetimeSelfConsistency:
    """Test curved spacetime backreaction."""

    def test_backreaction_correction_small(self):
        """Correction should be very small for neutrino mass."""
        params = VacuumParameters(neutrino_mass_mev=2.31)
        m = params.neutrino_mass_kg
        rho = m**4 * C**3 / HBAR**3
        lambda_c = params.compton_wavelength

        correction = CurvedSpacetimeSelfConsistency.backreaction_correction(
            rho, lambda_c
        )
        assert correction < 1e-59

    def test_fixed_point_verification(self):
        """Verify fixed point is stable."""
        result = CurvedSpacetimeSelfConsistency.verify_fixed_point(2.31)

        assert 'delta_rho_over_rho' in result
        assert result['delta_rho_over_rho'] < 1e-59
        assert result['is_stable_fixed_point'] is True

    def test_lambda_c_correct_scale(self):
        """Compton wavelength should be ~0.085 mm for 2.31 meV."""
        result = CurvedSpacetimeSelfConsistency.verify_fixed_point(2.31)
        lambda_c = result['lambda_c_m']
        assert 5e-5 < lambda_c < 1.5e-4

    def test_rho_cell_positive(self):
        """Energy density should be positive."""
        result = CurvedSpacetimeSelfConsistency.verify_fixed_point(2.31)
        assert result['rho_cell_J_m3'] > 0

    def test_curvature_positive(self):
        """Curvature R should be positive."""
        result = CurvedSpacetimeSelfConsistency.verify_fixed_point(2.31)
        assert result['R_m2'] > 0


class TestParkerParticleCreation:
    """Test Parker particle creation suppression."""

    def test_adiabatic_parameter_small(self):
        """Adiabatic parameter should be tiny."""
        epsilon = ParkerParticleCreation.adiabatic_parameter(2.31)
        assert epsilon < 1e-20

    def test_bogoliubov_coefficient_tiny(self):
        """Bogoliubov coefficient should be negligible."""
        epsilon = ParkerParticleCreation.adiabatic_parameter(2.31)
        beta_sq = ParkerParticleCreation.bogoliubov_coefficient(epsilon)
        assert beta_sq < 1e-40

    def test_suppression_verification(self):
        """Verify creation is suppressed."""
        result = ParkerParticleCreation.verify_suppression(2.31)

        assert result['epsilon'] < 1e-20
        assert result['beta_squared'] < 1e-40
        assert result['is_negligible'] is True

    def test_epsilon_scaling(self):
        """ε should scale as H·λ_C/c."""
        params = VacuumParameters(neutrino_mass_mev=2.31)
        lambda_c = params.compton_wavelength
        H = 2.2e-18

        epsilon = ParkerParticleCreation.adiabatic_parameter(2.31, H)
        expected = H * lambda_c / C
        assert np.isclose(epsilon, expected, rtol=1e-10)

    def test_hubble_dependence(self):
        """ε should scale linearly with Hubble."""
        eps_1 = ParkerParticleCreation.adiabatic_parameter(2.31, 1e-18)
        eps_2 = ParkerParticleCreation.adiabatic_parameter(2.31, 2e-18)
        assert np.isclose(eps_2 / eps_1, 2.0, rtol=1e-10)


class TestEntanglementVerification:
    """Test entanglement properties."""

    def test_product_state_zero_entropy(self):
        """Product state always has zero entropy."""
        for N in [1, 10, 100, 1000]:
            S = EntanglementVerification.product_state_entropy(N)
            assert S == 0.0

    def test_mode_vacuum_area_law(self):
        """Mode vacuum should have area-law scaling."""
        S_10 = EntanglementVerification.mode_vacuum_entropy(10, 1e-10, 1.0)
        S_100 = EntanglementVerification.mode_vacuum_entropy(100, 1e-10, 1.0)
        # Should scale with area
        assert S_100 > S_10

    def test_contrast_computation(self):
        """Compute entanglement contrast."""
        result = EntanglementVerification.compute_contrast(1000)

        assert result['cell_vacuum_entropy'] == 0.0
        assert result['mode_vacuum_entropy'] > 0
        assert result['entropy_contrast'] > 0

    def test_surface_area_scaling(self):
        """Surface area should scale as N^(2/3) for 3D."""
        result_8 = EntanglementVerification.compute_contrast(8, dimension=3)
        result_1000 = EntanglementVerification.compute_contrast(1000, dimension=3)

        # 8 cells: 2³ → surface ~ 6·4 = 24
        # 1000 cells: 10³ → surface ~ 6·100 = 600
        assert result_8['surface_area_cells'] < result_1000['surface_area_cells']

    def test_mode_entropy_uv_dependence(self):
        """Mode entropy should diverge as ε → 0."""
        S_large_eps = EntanglementVerification.mode_vacuum_entropy(100, 1e-5, 1.0)
        S_small_eps = EntanglementVerification.mode_vacuum_entropy(100, 1e-10, 1.0)
        assert S_small_eps > S_large_eps


class TestBlackHoleEntropyTension:
    """Test black hole entropy calculations."""

    def test_bekenstein_hawking_positive(self):
        """BH entropy should be positive."""
        S_BH = BlackHoleEntropyTension.bekenstein_hawking_entropy(1.989e30)
        assert S_BH > 0

    def test_bekenstein_hawking_scaling(self):
        """BH entropy should scale as M²."""
        M_solar = 1.989e30
        S_1 = BlackHoleEntropyTension.bekenstein_hawking_entropy(M_solar)
        S_10 = BlackHoleEntropyTension.bekenstein_hawking_entropy(10 * M_solar)
        # S ~ M² → S_10 / S_1 ~ 100
        ratio = S_10 / S_1
        assert 90 < ratio < 110  # Allow some tolerance

    def test_cell_vacuum_always_zero(self):
        """Cell vacuum entropy always zero."""
        for mass in [1e30, 1e31, 1e32]:
            S = BlackHoleEntropyTension.cell_vacuum_entropy(mass)
            assert S == 0.0

    def test_tension_computation(self):
        """Compute tension for 10 solar mass BH."""
        result = BlackHoleEntropyTension.compute_tension(10.0)

        assert result['bekenstein_hawking_entropy'] > 1e70
        assert result['cell_vacuum_entropy'] == 0.0
        assert result['entropy_gap'] > 1e70
        assert result['gap_log10'] > 70

    def test_gap_enormous(self):
        """Gap should be enormous (~10^77)."""
        result = BlackHoleEntropyTension.compute_tension(10.0)
        assert result['gap_log10'] > 70
        assert result['gap_log10'] < 80

    def test_planck_length_correct(self):
        """Verify Planck length is correct."""
        l_p = np.sqrt(HBAR * G / C**3)
        assert np.isclose(L_PLANCK, l_p, rtol=1e-10)
        assert 1e-35 < L_PLANCK < 2e-35


class TestFullVerificationReport:
    """Test complete verification report generation."""

    def test_report_generation(self):
        """Report should generate without errors."""
        report = generate_full_verification_report()
        assert isinstance(report, dict)

    def test_report_has_all_sections(self):
        """Report should have all required sections."""
        report = generate_full_verification_report()

        required_sections = [
            'orthogonality',
            'unitary_inequivalence',
            'hadamard_condition',
            'curved_spacetime',
            'parker_creation',
            'entanglement',
            'black_hole_entropy'
        ]

        for section in required_sections:
            assert section in report

    def test_orthogonality_verified(self):
        """Orthogonality should be verified."""
        report = generate_full_verification_report()
        assert bool(report['orthogonality']['verified']) is True

    def test_unitary_inequivalence_verified(self):
        """Unitary inequivalence should be verified."""
        report = generate_full_verification_report()
        assert report['unitary_inequivalence']['verified'] is True

    def test_hadamard_verified(self):
        """Hadamard condition should be verified."""
        report = generate_full_verification_report()
        assert bool(report['hadamard_condition']['verified']) is True

    def test_fixed_point_stable(self):
        """Curved spacetime fixed point should be stable."""
        report = generate_full_verification_report()
        assert report['curved_spacetime']['is_stable_fixed_point'] is True

    def test_parker_negligible(self):
        """Parker creation should be negligible."""
        report = generate_full_verification_report()
        assert report['parker_creation']['is_negligible'] is True

    def test_bh_tension_catastrophic(self):
        """Black hole entropy gap should be catastrophic."""
        report = generate_full_verification_report()
        assert report['black_hole_entropy']['gap_log10'] > 70


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
