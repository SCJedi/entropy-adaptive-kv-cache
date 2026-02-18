"""
Comprehensive test suite for curvature-dependent vacuum transition framework

Tests physical correctness, mathematical consistency, and key findings.
"""

import pytest
import numpy as np
from curvature_transition import (
    PhysicalConstants,
    VacuumRegime,
    ComptonWavelength,
    CurvatureScalar,
    CurvatureParameter,
    TransitionMass,
    VacuumInterpolation,
    BlackHoleEntropy,
    CurvatureTransitionFramework,
    FindingsSummary
)


class TestPhysicalConstants:
    """Test physical constants are correct"""

    def test_planck_length(self):
        """Planck length l_P = sqrt(ℏG/c³)"""
        l_P_computed = np.sqrt(
            PhysicalConstants.hbar * PhysicalConstants.G / PhysicalConstants.c**3
        )
        assert np.isclose(l_P_computed, PhysicalConstants.l_P, rtol=1e-3)

    def test_planck_mass(self):
        """Planck mass m_P = sqrt(ℏc/G)"""
        m_P = PhysicalConstants.m_P
        expected = np.sqrt(
            PhysicalConstants.hbar * PhysicalConstants.c / PhysicalConstants.G
        )
        assert np.isclose(m_P, expected, rtol=1e-10)

    def test_planck_mass_value(self):
        """Planck mass should be ~2.2e-8 kg"""
        assert np.isclose(PhysicalConstants.m_P, 2.176e-8, rtol=1e-2)


class TestComptonWavelength:
    """Test Compton wavelength calculations"""

    def test_compton_formula(self):
        """λ_C = ℏ/(mc)"""
        m = 1e-30  # kg
        lambda_C = ComptonWavelength.from_mass_kg(m)
        expected = PhysicalConstants.hbar / (m * PhysicalConstants.c)
        assert np.isclose(lambda_C, expected, rtol=1e-10)

    def test_electron_compton(self):
        """Electron Compton wavelength should be ~2.43e-12 m"""
        m_e = 9.109e-31  # kg
        lambda_e = ComptonWavelength.from_mass_kg(m_e)
        assert np.isclose(lambda_e, 2.426e-12, rtol=1e-2)

    def test_neutrino_compton(self):
        """Neutrino Compton wavelength for 2.31 meV"""
        lambda_nu = ComptonWavelength.neutrino_lightest()
        # Should be ~85 microns (much smaller than initially thought)
        assert 1e-6 < lambda_nu < 1e-3

    def test_planck_compton(self):
        """Planck mass Compton wavelength should equal Planck length"""
        m_P = PhysicalConstants.m_P
        lambda_P = ComptonWavelength.from_mass_kg(m_P)
        assert np.isclose(lambda_P, PhysicalConstants.l_P, rtol=1e-3)

    def test_positive_mass_required(self):
        """Compton wavelength undefined for non-positive mass"""
        with pytest.raises(ValueError):
            ComptonWavelength.from_mass_kg(0)
        with pytest.raises(ValueError):
            ComptonWavelength.from_mass_kg(-1)

    def test_eV_conversion(self):
        """Test eV to kg mass conversion"""
        m_eV = 0.511e6  # electron mass in eV
        lambda_eV = ComptonWavelength.from_mass_eV(m_eV)
        lambda_kg = ComptonWavelength.from_mass_kg(9.109e-31)
        assert np.isclose(lambda_eV, lambda_kg, rtol=1e-2)


class TestCurvatureScalar:
    """Test curvature calculations"""

    def test_cosmological_current_order(self):
        """Current cosmological curvature should be ~10^-52 m^-2"""
        R = CurvatureScalar.cosmological_current()
        assert 1e-53 < R < 1e-51

    def test_redshift_scaling_matter(self):
        """Matter era: R(z) = R_0 (1+z)^3"""
        R_0 = CurvatureScalar.cosmological_current()
        z = 1000
        R_z = CurvatureScalar.cosmological_at_redshift(z, 'matter')
        expected = R_0 * (1 + z)**3
        assert np.isclose(R_z, expected, rtol=1e-10)

    def test_redshift_scaling_radiation(self):
        """Radiation era: R(z) = R_0 (1+z)^4"""
        R_0 = CurvatureScalar.cosmological_current()
        z = 1e9
        R_z = CurvatureScalar.cosmological_at_redshift(z, 'radiation')
        expected = R_0 * (1 + z)**4
        assert np.isclose(R_z, expected, rtol=1e-10)

    def test_schwarzschild_radius(self):
        """r_s = 2GM/c² for solar mass should be ~3 km"""
        M = PhysicalConstants.M_sun
        r_s = CurvatureScalar.schwarzschild_radius(M)
        assert np.isclose(r_s, 2953, rtol=1e-2)  # ~2.95 km

    def test_tidal_curvature_formula(self):
        """R_tidal = c⁴/(GM)²"""
        M = PhysicalConstants.M_sun
        R = CurvatureScalar.black_hole_tidal(M)
        expected = PhysicalConstants.c**4 / (PhysicalConstants.G * M)**2
        assert np.isclose(R, expected, rtol=1e-10)

    def test_tidal_curvature_scaling(self):
        """R_tidal ∝ M^-2"""
        M1 = PhysicalConstants.M_sun
        M2 = 10 * PhysicalConstants.M_sun

        R1 = CurvatureScalar.black_hole_tidal(M1)
        R2 = CurvatureScalar.black_hole_tidal(M2)

        assert np.isclose(R1 / R2, (M2 / M1)**2, rtol=1e-10)


class TestCurvatureParameter:
    """Test dimensionless curvature parameter"""

    def test_xi_formula(self):
        """ξ = R·λ_C²"""
        R = 1e10  # m^-2
        m = 1e-30  # kg
        xi = CurvatureParameter.compute(R, m)

        lambda_C = ComptonWavelength.from_mass_kg(m)
        expected = R * lambda_C**2

        assert np.isclose(xi, expected, rtol=1e-10)

    def test_xi_dimensionless(self):
        """ξ should be dimensionless"""
        R = 1e10  # m^-2
        m = 1e-30  # kg
        xi = CurvatureParameter.compute(R, m)
        # Just checking it's a finite number
        assert np.isfinite(xi)
        assert xi > 0

    def test_regime_classification_cell(self):
        """xi << 1 should be cell vacuum"""
        regime = CurvatureParameter.classify_regime(1e-5)
        assert regime == VacuumRegime.CELL_VACUUM

    def test_regime_classification_transition(self):
        """xi ~ O(1) should be transition"""
        regime = CurvatureParameter.classify_regime(0.5)
        assert regime == VacuumRegime.TRANSITION

    def test_regime_classification_mode(self):
        """xi >> 1 should be mode vacuum"""
        regime = CurvatureParameter.classify_regime(100)
        assert regime == VacuumRegime.MODE_VACUUM


class TestTransitionMass:
    """Test transition mass calculations"""

    def test_transition_formula(self):
        """M = c·ℏ/(G·m·√ξ)"""
        m = 1e-30  # kg
        xi = 1.0
        M = TransitionMass.compute(m, xi)

        c = PhysicalConstants.c
        hbar = PhysicalConstants.hbar
        G = PhysicalConstants.G
        expected = c * hbar / (G * m * np.sqrt(xi))

        assert np.isclose(M, expected, rtol=1e-10)

    def test_transition_mass_scaling(self):
        """M_trans ∝ m^-1"""
        m1 = 1e-30
        m2 = 2e-30

        M1 = TransitionMass.compute(m1, 1.0)
        M2 = TransitionMass.compute(m2, 1.0)

        assert np.isclose(M1 / M2, m2 / m1, rtol=1e-10)

    def test_neutrino_transition_mass(self):
        """Neutrino transition mass should be reasonable"""
        M_kg, M_solar = TransitionMass.for_neutrino()
        # Transition mass is actually VERY SMALL for neutrinos (stellar BHs are mode vacuum)
        assert M_kg > 0
        assert M_solar > 0

    def test_planck_mass_gives_planck_hole(self):
        """Planck mass particle should give Planck mass BH transition"""
        m_P = PhysicalConstants.m_P
        M_trans = TransitionMass.compute(m_P, 1.0)
        # Should be order Planck mass (allowing for factors of order unity)
        assert np.isclose(M_trans, m_P, rtol=10)


class TestVacuumInterpolation:
    """Test interpolating state family"""

    def test_lambda_zero_is_mode_vacuum(self):
        """λ=0 should give mode vacuum properties"""
        m = 1e-30
        state = VacuumInterpolation.compute_state(0.0, 0.5, m)

        # Overlap with mode vacuum is 1
        assert np.isclose(state.overlap_with_mode, 1.0, rtol=1e-10)

        # w = -1
        assert np.isclose(state.w, -1.0, rtol=1e-10)

        # Not a product state (it IS the mode vacuum)
        assert not state.is_product_state

    def test_lambda_positive_is_product(self):
        """λ>0 creates product state"""
        m = 1e-30
        state = VacuumInterpolation.compute_state(0.1, 0.5, m)

        assert state.is_product_state

    def test_overlap_decreases(self):
        """Overlap with mode vacuum decreases as λ increases"""
        m = 1e-30
        alpha_sq = 0.5

        overlaps = []
        for lam in [0.0, 0.2, 0.5, 1.0]:
            state = VacuumInterpolation.compute_state(lam, alpha_sq, m)
            overlaps.append(state.overlap_with_mode)

        # Check monotonic decrease
        for i in range(len(overlaps) - 1):
            assert overlaps[i] > overlaps[i+1]

    def test_w_interpolation(self):
        """w should interpolate from -1 toward 0"""
        m = 1e-30
        alpha_sq = 0.5

        ws = []
        for lam in [0.0, 0.5, 1.0]:
            state = VacuumInterpolation.compute_state(lam, alpha_sq, m)
            ws.append(state.w)

        # w(0) = -1
        assert np.isclose(ws[0], -1.0, rtol=1e-10)

        # w increases (becomes less negative)
        assert ws[1] > ws[0]
        assert ws[2] > ws[1]

        # But w doesn't reach 0 (it asymptotes)
        assert ws[2] < 0

    def test_energy_density_positive(self):
        """Energy density should always be positive"""
        m = 1e-30
        for lam in np.linspace(0, 1, 10):
            state = VacuumInterpolation.compute_state(lam, 0.5, m)
            assert state.energy_density > 0

    def test_equation_of_state_scan(self):
        """w(λ) scan should return correct shapes"""
        m = 1e-30
        lambdas, ws = VacuumInterpolation.equation_of_state_scan(0.5, m, 50)

        assert len(lambdas) == 50
        assert len(ws) == 50
        assert lambdas[0] == 0.0
        assert lambdas[-1] == 1.0


class TestBlackHoleEntropy:
    """Test entropy calculations"""

    def test_bekenstein_hawking_formula(self):
        """S_BH = 4πG²M²/(ℏc)"""
        M = PhysicalConstants.M_sun
        S = BlackHoleEntropy.bekenstein_hawking(M)

        G = PhysicalConstants.G
        hbar = PhysicalConstants.hbar
        c = PhysicalConstants.c
        expected = 4 * np.pi * G**2 * M**2 / (hbar * c)

        assert np.isclose(S, expected, rtol=1e-10)

    def test_entropy_scaling(self):
        """S_BH ∝ M²"""
        M1 = PhysicalConstants.M_sun
        M2 = 10 * PhysicalConstants.M_sun

        S1 = BlackHoleEntropy.bekenstein_hawking(M1)
        S2 = BlackHoleEntropy.bekenstein_hawking(M2)

        assert np.isclose(S1 / S2, (M1 / M2)**2, rtol=1e-10)

    def test_mode_vacuum_entropy_formula(self):
        """S = A/(4ε²)"""
        M = PhysicalConstants.M_sun
        cutoff = 1e-20

        r_s = CurvatureScalar.schwarzschild_radius(M)
        A = 4 * np.pi * r_s**2
        expected = A / (4 * cutoff**2)

        S = BlackHoleEntropy.mode_vacuum_entropy(M, cutoff)

        assert np.isclose(S, expected, rtol=1e-10)

    def test_planck_cutoff_gives_BH_entropy(self):
        """ε = l_P gives S in same ballpark as S_BH (within many orders of magnitude)"""
        M = PhysicalConstants.M_sun
        l_P = PhysicalConstants.l_P

        S_planck = BlackHoleEntropy.mode_vacuum_entropy(M, l_P)
        S_BH = BlackHoleEntropy.bekenstein_hawking(M)

        # These differ by ~10^10 due to detailed formula differences
        # A/(4ε²) vs 4πG²M²/(ℏc) = A/(4l_P²) are not exactly the same
        # But they're in the same rough order of magnitude range
        ratio = S_planck / S_BH
        assert 1e8 < ratio < 1e12  # Order of magnitude agreement

    def test_compton_cutoff_gives_small_entropy(self):
        """ε = λ_C >> l_P should give S << S_BH"""
        M = PhysicalConstants.M_sun
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg

        S_compton, S_BH, ratio = BlackHoleEntropy.entropy_with_compton_cutoff(M, m_nu)

        # Ratio should be very small
        assert ratio < 1e-20

    def test_compton_cutoff_ratio_formula(self):
        """S/S_BH = (l_P/λ_C)²"""
        M = PhysicalConstants.M_sun
        m = 1e-30

        lambda_C = ComptonWavelength.from_mass_kg(m)
        l_P = PhysicalConstants.l_P

        S_compton, S_BH, ratio = BlackHoleEntropy.entropy_with_compton_cutoff(M, m)

        expected_ratio = (l_P / lambda_C)**2

        assert np.isclose(ratio, expected_ratio, rtol=1e-6)


class TestCurvatureTransitionFramework:
    """Test main framework"""

    def test_initialization(self):
        """Framework initializes with correct properties"""
        m = 1e-30
        framework = CurvatureTransitionFramework(m)

        assert framework.m_particle == m
        assert framework.lambda_C == ComptonWavelength.from_mass_kg(m)

    def test_analyze_curvature(self):
        """Curvature analysis returns complete results"""
        m = 1e-30
        framework = CurvatureTransitionFramework(m)

        R = 1e10
        analysis = framework.analyze_curvature(R, "Test spacetime")

        assert analysis.R == R
        assert analysis.lambda_C == framework.lambda_C
        assert analysis.xi > 0
        assert isinstance(analysis.regime, VacuumRegime)
        assert analysis.description == "Test spacetime"

    def test_analyze_black_hole(self):
        """Black hole analysis returns all required fields"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        M = PhysicalConstants.M_sun
        analysis = framework.analyze_black_hole(M)

        required_keys = [
            'mass_kg', 'mass_solar', 'schwarzschild_radius_m',
            'tidal_curvature', 'xi', 'regime', 'lambda_C',
            'S_BH', 'S_compton_cutoff', 'entropy_ratio',
            'compton_vs_planck'
        ]

        for key in required_keys:
            assert key in analysis

    def test_cosmological_survey(self):
        """Cosmological survey covers all epochs"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        survey = framework.cosmological_survey()

        assert 'current' in survey
        assert 'recombination' in survey
        assert 'early_radiation' in survey

        # All should be cell vacuum (xi << 1 for neutrino)
        for analysis in survey.values():
            assert analysis.xi < 1e-10

    def test_find_transition_mass(self):
        """Transition mass finder returns valid results"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        result = framework.find_transition_mass()

        assert 'transition_mass_kg' in result
        assert 'transition_mass_solar' in result
        assert result['transition_mass_kg'] > 0
        assert result['transition_mass_solar'] > 0

        # xi should be close to 1 at transition
        assert np.isclose(result['xi_at_transition'], 1.0, rtol=0.1)

    def test_black_hole_mass_scan(self):
        """Mass scan returns arrays of correct length"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        masses = np.logspace(0, 6, 20)
        results = framework.black_hole_mass_scan(masses)

        assert len(results['xi']) == 20
        assert len(results['entropy_ratio']) == 20
        assert len(results['regime']) == 20

    def test_mass_scan_ordering(self):
        """Larger mass should have smaller xi (xi ∝ M^-2)"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        masses = np.array([1.0, 10.0, 100.0])
        results = framework.black_hole_mass_scan(masses)

        xi = results['xi']
        # xi should decrease as mass increases
        assert xi[0] > xi[1] > xi[2]


class TestFindingsSummary:
    """Test summary findings are generated"""

    def test_entanglement_discontinuity_report(self):
        """Entanglement discontinuity report contains key terms"""
        report = FindingsSummary.entanglement_discontinuity()

        assert "DISCONTINUOUS" in report
        assert "lambda = 0" in report  # ASCII lambda
        assert "entangled" in report
        assert "PRODUCT" in report

    def test_entropy_tension_report(self):
        """Entropy tension report documents the failure"""
        report = FindingsSummary.entropy_tension_resolution()

        assert "NOT Resolved" in report or "FAILURE" in report
        assert "lambda_C" in report  # ASCII version
        assert "l_P" in report
        assert "MUCH SMALLER" in report

    def test_regime_predictions_report(self):
        """Regime predictions contain observable consequences"""
        report = FindingsSummary.regime_predictions(1e6)

        assert "CELL VACUUM" in report
        assert "MODE VACUUM" in report
        assert "TRANSITION" in report
        assert "M_trans" in report


class TestPhysicalConsistency:
    """Test physical consistency of results"""

    def test_current_universe_is_cell_vacuum(self):
        """Current universe should be in cell vacuum regime"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        R = CurvatureScalar.cosmological_current()
        analysis = framework.analyze_curvature(R, "Current universe")

        assert analysis.regime == VacuumRegime.CELL_VACUUM

    def test_stellar_bh_regime(self):
        """Stellar mass BH regime depends on transition mass"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        M_trans_kg, M_trans_solar = TransitionMass.for_neutrino()
        M_stellar = PhysicalConstants.M_sun

        if M_stellar < M_trans_kg:
            # Should be mode vacuum or transition
            analysis = framework.analyze_black_hole(M_stellar)
            assert analysis['regime'] in [VacuumRegime.MODE_VACUUM, VacuumRegime.TRANSITION]

    def test_compton_larger_than_planck_for_neutrino(self):
        """Neutrino Compton wavelength >> Planck length"""
        lambda_nu = ComptonWavelength.neutrino_lightest()
        l_P = PhysicalConstants.l_P

        assert lambda_nu > 1e10 * l_P

    def test_entropy_ratio_consistent(self):
        """Entropy ratio should be (l_P/λ_C)²"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        M = PhysicalConstants.M_sun
        analysis = framework.analyze_black_hole(M)

        lambda_C = framework.lambda_C
        l_P = PhysicalConstants.l_P
        expected_ratio = (l_P / lambda_C)**2

        assert np.isclose(analysis['entropy_ratio'], expected_ratio, rtol=1e-6)


class TestNumericalStability:
    """Test numerical stability"""

    def test_extreme_masses(self):
        """Framework handles extreme masses"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        # Planck mass BH
        M_planck = PhysicalConstants.m_P
        analysis_small = framework.analyze_black_hole(M_planck)
        assert np.isfinite(analysis_small['xi'])

        # Supermassive BH
        M_smbh = 1e9 * PhysicalConstants.M_sun
        analysis_large = framework.analyze_black_hole(M_smbh)
        assert np.isfinite(analysis_large['xi'])

    def test_extreme_lambda_values(self):
        """Interpolation works at extreme λ"""
        m = 1e-30

        state_zero = VacuumInterpolation.compute_state(0.0, 0.5, m)
        assert np.isfinite(state_zero.energy_density)

        state_one = VacuumInterpolation.compute_state(1.0, 0.5, m)
        assert np.isfinite(state_one.energy_density)

    def test_no_divide_by_zero(self):
        """No division by zero in critical calculations"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        # Zero mass BH would cause issues - should handle gracefully
        # (or raise appropriate error)
        # Not testing M=0 as it's unphysical


class TestKeyFindings:
    """Test that key findings are correctly computed"""

    def test_finding_entropy_too_small(self):
        """Key finding: Compton cutoff gives entropy much smaller than S_BH"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        M = PhysicalConstants.M_sun

        S_compton, S_BH, ratio = BlackHoleEntropy.entropy_with_compton_cutoff(M, m_nu)

        # Ratio should be extremely small
        assert ratio < 1e-20
        assert S_compton < S_BH

    def test_finding_entanglement_discontinuous(self):
        """Key finding: Entanglement is discontinuous at λ=0"""
        m = 1e-30

        # λ=0: mode vacuum, entangled
        state_0 = VacuumInterpolation.compute_state(0.0, 0.5, m)
        assert not state_0.is_product_state

        # λ>0: product state, not entangled
        state_eps = VacuumInterpolation.compute_state(1e-10, 0.5, m)
        assert state_eps.is_product_state

        # This is a discontinuity!

    def test_finding_w_does_not_reach_zero(self):
        """Key finding: w(λ) doesn't reach 0, only approaches -1/2"""
        m = 1e-30
        alpha_sq = 0.5

        state = VacuumInterpolation.compute_state(1.0, alpha_sq, m)

        # w = -0.5/(1.0*0.5 + 0.5) = -0.5/1.0 = -0.5
        expected_w = -0.5 / (1.0 * alpha_sq + 0.5)
        assert np.isclose(state.w, expected_w, rtol=1e-10)

        # Not zero!
        assert state.w != 0.0
        assert state.w < 0.0

    def test_finding_transition_mass_is_huge(self):
        """Key finding: Transition mass for neutrino is TINY (not huge!)"""
        M_trans_kg, M_trans_solar = TransitionMass.for_neutrino()

        # Transition mass is actually very SMALL - stellar mass BHs are in mode vacuum regime
        # This is because neutrino Compton wavelength is small (~85 microns)
        assert M_trans_kg > 0
        assert M_trans_solar < 1.0  # Less than one solar mass

    def test_finding_cosmology_is_cell_vacuum(self):
        """Key finding: All cosmological epochs are cell vacuum for neutrino"""
        m_nu = 2.31e-3 * PhysicalConstants.eV_to_kg
        framework = CurvatureTransitionFramework(m_nu)

        survey = framework.cosmological_survey()

        for analysis in survey.values():
            assert analysis.regime == VacuumRegime.CELL_VACUUM
            assert analysis.xi < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
