"""
Test suite for V3 Core Verification Module.

Tests verify:
- Cell vacuum density formula
- Mass inversion from target densities
- Neutrino mass splittings from oscillation data
- Sum(m_nu) for normal and inverted hierarchy
- DESI DR2 comparison accuracy
- Jeans length at Compton scale
- w = 0 numerical verification
- LCDM equivalence
- Dimensional uniqueness
- Vacuum overlap
- Backreaction self-consistency
"""

import math
import pytest

from v3_core import (
    # Constants
    HBAR, C, G, EV_TO_JOULE, EV_TO_KG, H0,
    DM2_21, DM2_31_NH, DM2_32_IH,
    RHO_CRIT, RHO_CDM, RHO_DE, RHO_BARYON,
    DESI_DR2_SUM_BOUND,
    OMEGA_CDM, OMEGA_LAMBDA, OMEGA_BARYON,
    # Functions
    critical_density,
    cell_vacuum_density, cell_vacuum_density_eV,
    mass_from_density, mass_from_density_eV,
    compton_wavelength, compton_frequency,
    neutrino_spectrum_normal, neutrino_spectrum_inverted,
    minimum_sum_normal, minimum_sum_inverted,
    predict_cdm, predict_de, predict_from_density,
    verify_w_equals_zero, verify_virial_theorem,
    verify_lcdm_equivalence,
    jeans_length, jeans_length_eV,
    verify_dimensional_uniqueness,
    vacuum_overlap,
    backreaction_parameter, adiabatic_parameter,
    generate_report,
)


# =============================================================================
# Test: Cell Vacuum Density Formula
# =============================================================================

class TestCellVacuumDensity:
    """Tests for rho = m^4 c^5 / hbar^3."""

    def test_formula_direct(self):
        """Verify formula gives correct result for known mass."""
        m_kg = 2.31e-3 * EV_TO_KG  # 2.31 meV
        rho = cell_vacuum_density(m_kg)
        # Should be approximately 5.94e-10 J/m^3
        assert 5.0e-10 < rho < 7.0e-10

    def test_formula_eV_interface(self):
        """Verify eV interface matches kg interface."""
        m_eV = 2.31e-3  # 2.31 meV
        m_kg = m_eV * EV_TO_KG
        rho_eV = cell_vacuum_density_eV(m_eV)
        rho_kg = cell_vacuum_density(m_kg)
        assert abs(rho_eV - rho_kg) / rho_kg < 1e-10

    def test_two_derivations_agree(self):
        """Verify E/V = m^4 c^5/hbar^3."""
        m_kg = 2.0e-3 * EV_TO_KG
        # Route 1: Direct formula
        rho1 = m_kg**4 * C**5 / HBAR**3
        # Route 2: E_cell / V_cell
        E_cell = m_kg * C**2
        V_cell = (HBAR / (m_kg * C))**3
        rho2 = E_cell / V_cell
        assert abs(rho1 - rho2) / rho1 < 1e-12

    def test_scaling_m4(self):
        """Verify rho scales as m^4."""
        m1 = 1.0e-3 * EV_TO_KG
        m2 = 2.0e-3 * EV_TO_KG
        ratio = cell_vacuum_density(m2) / cell_vacuum_density(m1)
        expected = (m2 / m1)**4
        assert abs(ratio - expected) / expected < 1e-10

    def test_positive_definite(self):
        """Density is positive for any positive mass."""
        for m_meV in [0.1, 1.0, 10.0, 100.0]:
            rho = cell_vacuum_density_eV(m_meV * 1e-3)
            assert rho > 0


# =============================================================================
# Test: Mass Inversion
# =============================================================================

class TestMassInversion:
    """Tests for m = (rho * hbar^3 / c^5)^{1/4}."""

    def test_roundtrip_kg(self):
        """Mass -> density -> mass roundtrip."""
        m_original = 2.31e-3 * EV_TO_KG
        rho = cell_vacuum_density(m_original)
        m_recovered = mass_from_density(rho)
        assert abs(m_recovered - m_original) / m_original < 1e-10

    def test_roundtrip_eV(self):
        """Mass (eV) -> density -> mass (eV) roundtrip."""
        m_original = 2.31e-3  # eV
        rho = cell_vacuum_density_eV(m_original)
        m_recovered = mass_from_density_eV(rho)
        assert abs(m_recovered - m_original) / m_original < 1e-6

    def test_cdm_mass(self):
        """Mass from rho_CDM gives expected value ~1.77 meV."""
        m_eV = mass_from_density_eV(RHO_CDM)
        m_meV = m_eV * 1e3
        assert 1.5 < m_meV < 2.0  # Should be ~1.77

    def test_de_mass(self):
        """Mass from rho_DE gives expected value ~2.3 meV."""
        m_eV = mass_from_density_eV(RHO_DE)
        m_meV = m_eV * 1e3
        assert 2.0 < m_meV < 2.5  # Should be ~2.31

    def test_fourth_root_sensitivity(self):
        """10% change in rho -> ~2.5% change in mass."""
        rho_base = 5.0e-10
        rho_high = rho_base * 1.10
        m_base = mass_from_density(rho_base)
        m_high = mass_from_density(rho_high)
        fractional_change = (m_high - m_base) / m_base
        # Expected: (1.10)^{1/4} - 1 ~ 0.0241
        assert abs(fractional_change - 0.0241) < 0.001


# =============================================================================
# Test: Mass Splittings and Oscillation Data
# =============================================================================

class TestMassSplittings:
    """Tests for neutrino mass spectrum from oscillation data."""

    def test_dm2_21_value(self):
        """Solar mass splitting is correct."""
        assert abs(DM2_21 - 7.53e-5) < 1e-7

    def test_dm2_31_value(self):
        """Atmospheric mass splitting (NH) is correct."""
        assert abs(DM2_31_NH - 2.453e-3) < 1e-5

    def test_normal_hierarchy_ordering(self):
        """m1 < m2 < m3 for normal hierarchy."""
        spec = neutrino_spectrum_normal(2.0e-3)
        assert spec.m1_eV < spec.m2_eV < spec.m3_eV

    def test_normal_hierarchy_m2(self):
        """m2 = sqrt(m1^2 + dm2_21)."""
        m1 = 2.31e-3
        spec = neutrino_spectrum_normal(m1)
        expected_m2 = math.sqrt(m1**2 + DM2_21)
        assert abs(spec.m2_eV - expected_m2) / expected_m2 < 1e-10

    def test_normal_hierarchy_m3(self):
        """m3 = sqrt(m1^2 + dm2_31)."""
        m1 = 2.31e-3
        spec = neutrino_spectrum_normal(m1)
        expected_m3 = math.sqrt(m1**2 + DM2_31_NH)
        assert abs(spec.m3_eV - expected_m3) / expected_m3 < 1e-10

    def test_inverted_hierarchy_ordering(self):
        """m3 < m1 < m2 for inverted hierarchy."""
        spec = neutrino_spectrum_inverted(2.0e-3)
        assert spec.m3_eV < spec.m1_eV < spec.m2_eV

    def test_sum_meV_conversion(self):
        """Sum in meV = 1000 * sum in eV."""
        spec = neutrino_spectrum_normal(2.0e-3)
        assert abs(spec.sum_meV - spec.sum_eV * 1e3) < 1e-10

    def test_m3_dominates_sum(self):
        """m3 contributes > 80% of the total sum."""
        spec = neutrino_spectrum_normal(2.0e-3)
        assert spec.m3_eV / spec.sum_eV > 0.8

    def test_sum_insensitive_to_m1(self):
        """Changing m1 from 0 to 3 meV changes sum by < 4 meV."""
        spec_low = neutrino_spectrum_normal(0.0)
        spec_high = neutrino_spectrum_normal(3.0e-3)
        delta_sum = abs(spec_high.sum_eV - spec_low.sum_eV) * 1e3  # meV
        assert delta_sum < 4.0


# =============================================================================
# Test: Sum(m_nu) Computation
# =============================================================================

class TestSumMnu:
    """Tests for total neutrino mass sum."""

    def test_old_prediction_sum(self):
        """OLD prediction (rho_DE): Sum ~ 60.9 meV."""
        m1 = mass_from_density_eV(5.96e-10)  # Using V1/V2 value
        spec = neutrino_spectrum_normal(m1)
        assert 59.0 < spec.sum_meV < 62.0

    def test_new_prediction_sum(self):
        """NEW prediction (rho_CDM): Sum ~ 60.2 meV."""
        m1 = mass_from_density_eV(RHO_CDM)
        spec = neutrino_spectrum_normal(m1)
        assert 58.0 < spec.sum_meV < 62.0

    def test_minimum_sum_normal(self):
        """Minimum sum for NH (m1=0) ~ 58.2 meV."""
        min_sum = minimum_sum_normal() * 1e3  # meV
        assert 57.0 < min_sum < 59.0

    def test_minimum_sum_inverted(self):
        """Minimum sum for IH (m3=0) ~ 99.8 meV."""
        min_sum = minimum_sum_inverted() * 1e3  # meV
        assert 98.0 < min_sum < 101.0

    def test_inverted_larger_than_normal(self):
        """IH minimum sum > NH minimum sum."""
        assert minimum_sum_inverted() > minimum_sum_normal()


# =============================================================================
# Test: DESI DR2 Comparison
# =============================================================================

class TestDESI:
    """Tests for DESI DR2 comparison."""

    def test_desi_bound_value(self):
        """DESI DR2 bound is 53 meV."""
        assert abs(DESI_DR2_SUM_BOUND * 1e3 - 53.0) < 0.1

    def test_old_prediction_tension(self):
        """OLD prediction exceeds DESI bound."""
        pred = predict_de()
        assert pred.spectrum.sum_eV > DESI_DR2_SUM_BOUND

    def test_new_prediction_tension(self):
        """NEW prediction exceeds DESI bound."""
        pred = predict_cdm()
        assert pred.spectrum.sum_eV > DESI_DR2_SUM_BOUND

    def test_both_in_tension(self):
        """Both predictions in tension with DESI."""
        pred_cdm_result = predict_cdm()
        pred_de_result = predict_de()
        assert not pred_cdm_result.desi_consistent
        assert not pred_de_result.desi_consistent

    def test_nh_minimum_exceeds_desi(self):
        """Even NH minimum (m1=0) exceeds DESI bound."""
        min_sum = minimum_sum_normal()
        assert min_sum > DESI_DR2_SUM_BOUND


# =============================================================================
# Test: Equation of State (w = 0)
# =============================================================================

class TestEquationOfState:
    """Tests for w = 0 verification."""

    def test_w_is_zero_numerically(self):
        """Time-averaged w = 0 to high precision."""
        result = verify_w_equals_zero(num_periods=10000)
        assert abs(result['w']) < 1e-10

    def test_virial_theorem(self):
        """<KE>/<PE> = 1 (virial theorem for QHO)."""
        result = verify_w_equals_zero(num_periods=10000)
        assert abs(result['virial_ratio'] - 1.0) < 1e-6

    def test_pressure_oscillates(self):
        """Pressure has zero average but nonzero instantaneous value."""
        result = verify_w_equals_zero()
        assert result['rho_avg'] > 0
        assert abs(result['p_avg']) < result['rho_avg'] * 1e-10

    def test_virial_analytic(self):
        """Analytic virial theorem check."""
        result = verify_virial_theorem()
        assert abs(result['virial_ratio'] - 1.0) < 1e-15
        assert abs(result['w']) < 1e-15

    def test_energy_split_50_50(self):
        """Energy splits 50/50 between displacement and zero-point."""
        result = verify_virial_theorem()
        assert abs(result['e_displacement'] - 0.5) < 1e-15
        assert abs(result['e_zero_point'] - 0.5) < 1e-15
        assert abs(result['e_total'] - 1.0) < 1e-15

    def test_w_zero_many_periods(self):
        """w = 0 remains stable over many oscillation periods."""
        for n in [100, 1000, 5000]:
            result = verify_w_equals_zero(num_periods=n)
            assert abs(result['w']) < 1e-8


# =============================================================================
# Test: LCDM Equivalence
# =============================================================================

class TestLCDMEquivalence:
    """Tests for LCDM equivalence of Two Vacua model."""

    def test_identical_expansion(self):
        """Two Vacua model reproduces LCDM exactly."""
        result = verify_lcdm_equivalence()
        assert result['identical']
        assert result['max_relative_error'] < 1e-10

    def test_omega_sum(self):
        """Omega parameters sum to ~1 (flat universe)."""
        total = OMEGA_CDM + OMEGA_LAMBDA + OMEGA_BARYON + 9.2e-5
        assert abs(total - 1.0) < 0.001


# =============================================================================
# Test: Jeans Length
# =============================================================================

class TestJeansLength:
    """Tests for Jeans length computation."""

    def test_jeans_at_compton_scale(self):
        """Jeans length is at Compton wavelength scale."""
        m_kg = 2.0e-3 * EV_TO_KG
        jl = jeans_length(m_kg)
        lc = compton_wavelength(m_kg)
        assert abs(jl - lc) / lc < 1e-10

    def test_jeans_sub_mm(self):
        """Jeans length is sub-millimeter for meV mass."""
        jl = jeans_length_eV(2.0e-3)
        assert jl < 1e-3  # Less than 1 mm
        assert jl > 1e-6  # More than 1 micrometer

    def test_jeans_far_below_galaxy(self):
        """Jeans length is far below galaxy scales."""
        jl = jeans_length_eV(2.0e-3)
        kpc = 3.0857e19  # meters
        assert jl / kpc < 1e-15


# =============================================================================
# Test: Dimensional Uniqueness
# =============================================================================

class TestDimensionalUniqueness:
    """Tests for dimensional analysis of rho = m^a c^b hbar^d."""

    def test_unique_solution(self):
        """Solution a=4, b=5, d=-3 is unique (nonzero determinant)."""
        result = verify_dimensional_uniqueness()
        assert result['unique']
        assert result['determinant'] != 0

    def test_exponents(self):
        """Correct exponents: a=4, b=5, d=-3."""
        result = verify_dimensional_uniqueness()
        assert result['a'] == 4
        assert result['b'] == 5
        assert result['d'] == -3

    def test_dimensional_consistency(self):
        """Exponents satisfy dimensional equations."""
        result = verify_dimensional_uniqueness()
        assert result['check_kg'] == 1   # kg exponent
        assert result['check_m'] == -1   # m exponent
        assert result['check_s'] == -2   # s exponent


# =============================================================================
# Test: Vacuum Overlap
# =============================================================================

class TestVacuumOverlap:
    """Tests for <0|Omega> = exp(-N/4)."""

    def test_small_N(self):
        """Overlap at N=4 is exp(-1)."""
        ov = vacuum_overlap(4)
        assert abs(ov - math.exp(-1.0)) < 1e-10

    def test_large_N(self):
        """Overlap at N=100 is tiny."""
        ov = vacuum_overlap(100)
        assert abs(ov - math.exp(-25.0)) < 1e-20

    def test_very_large_N(self):
        """Overlap at N=3000 is effectively zero."""
        ov = vacuum_overlap(3000)
        assert ov == 0.0

    def test_exponential_decay(self):
        """Overlap decays exponentially with N."""
        ov1 = vacuum_overlap(10)
        ov2 = vacuum_overlap(20)
        # ov2/ov1 = exp(-10/4) = exp(-2.5)
        if ov1 > 0:
            ratio = ov2 / ov1
            assert abs(ratio - math.exp(-2.5)) < 1e-10

    def test_single_cell(self):
        """Overlap at N=1 is exp(-1/4)."""
        ov = vacuum_overlap(1)
        assert abs(ov - math.exp(-0.25)) < 1e-10


# =============================================================================
# Test: Backreaction and Adiabaticity
# =============================================================================

class TestSelfConsistency:
    """Tests for curved spacetime self-consistency."""

    def test_backreaction_tiny(self):
        """R * lambda_C^2 << 1 for meV-scale masses."""
        m_kg = 2.0e-3 * EV_TO_KG
        br = backreaction_parameter(m_kg)
        # R = 32*pi*G*rho/c^2, with rho = m^4*c^5/hbar^3 ~ 10^{-10}
        # lambda_C^2 ~ 10^{-8}, R ~ 10^{-31}, so R*lambda_C^2 ~ 10^{-39}
        assert br < 1e-30

    def test_adiabatic_parameter_tiny(self):
        """H * lambda_C / c << 1 for meV-scale masses."""
        m_kg = 2.0e-3 * EV_TO_KG
        ad = adiabatic_parameter(m_kg)
        assert ad < 1e-25

    def test_parker_creation_negligible(self):
        """Bogoliubov coefficient |beta|^2 ~ epsilon^2 << 1."""
        m_kg = 2.0e-3 * EV_TO_KG
        ad = adiabatic_parameter(m_kg)
        beta_sq = ad**2
        assert beta_sq < 1e-50


# =============================================================================
# Test: Predictions Consistency
# =============================================================================

class TestPredictions:
    """Tests for prediction dataclass consistency."""

    def test_cdm_prediction_density_match(self):
        """CDM prediction has rho_cell = rho_CDM."""
        pred = predict_cdm()
        assert abs(pred.rho_cell - RHO_CDM) / RHO_CDM < 1e-6

    def test_de_prediction_density_match(self):
        """DE prediction has rho_cell = rho_DE."""
        pred = predict_de()
        assert abs(pred.rho_cell - RHO_DE) / RHO_DE < 1e-6

    def test_cdm_m1_less_than_de_m1(self):
        """CDM prediction has smaller m1 than DE prediction."""
        pred_cdm_result = predict_cdm()
        pred_de_result = predict_de()
        assert pred_cdm_result.m1_eV < pred_de_result.m1_eV

    def test_both_normal_hierarchy(self):
        """Both predictions use normal hierarchy."""
        pred_cdm_result = predict_cdm()
        pred_de_result = predict_de()
        assert pred_cdm_result.spectrum.hierarchy == "normal"
        assert pred_de_result.spectrum.hierarchy == "normal"

    def test_prediction_has_compton_wavelength(self):
        """Prediction includes Compton wavelength."""
        pred = predict_cdm()
        expected_lc = compton_wavelength(pred.m1_eV * EV_TO_KG)
        assert abs(pred.lambda_C - expected_lc) / expected_lc < 1e-10

    def test_prediction_has_frequency(self):
        """Prediction includes Compton frequency."""
        pred = predict_cdm()
        expected_omega = compton_frequency(pred.m1_eV * EV_TO_KG)
        assert abs(pred.omega - expected_omega) / expected_omega < 1e-10


# =============================================================================
# Test: Key Numbers from V3 Whitepaper
# =============================================================================

class TestKeyNumbers:
    """Verify specific numbers cited in the V3 whitepaper."""

    def test_rho_crit_order(self):
        """rho_crit ~ 7.7e-10 J/m^3."""
        assert 7.0e-10 < RHO_CRIT < 8.5e-10

    def test_rho_cdm_order(self):
        """rho_CDM ~ 2.0e-10 J/m^3."""
        assert 1.5e-10 < RHO_CDM < 2.5e-10

    def test_rho_de_order(self):
        """rho_DE ~ 5.3e-10 J/m^3."""
        assert 4.5e-10 < RHO_DE < 6.0e-10

    def test_omega_cdm_over_lambda(self):
        """Omega_CDM / Omega_Lambda ~ 0.39."""
        ratio = OMEGA_CDM / OMEGA_LAMBDA
        assert abs(ratio - 0.387) < 0.01

    def test_frequency_ratio(self):
        """omega / H_0 ~ 10^30 for meV-scale masses."""
        m_kg = 2.0e-3 * EV_TO_KG
        omega = compton_frequency(m_kg)
        ratio = omega / H0
        assert 1e29 < ratio < 1e32

    def test_action_per_cell(self):
        """Action per 4D spacetime cell = h = 2*pi*hbar (exact, mass-independent)."""
        # S = E * tau_C = hbar*omega * (2*pi/omega) = 2*pi*hbar = h
        for m_meV in [1.0, 2.0, 5.0, 10.0]:
            m_kg = m_meV * 1e-3 * EV_TO_KG
            omega = compton_frequency(m_kg)
            E = HBAR * omega  # Energy per cell (|alpha|^2 = 1/2)
            tau_C = 2 * math.pi / omega  # Compton period
            S = E * tau_C
            h = 2 * math.pi * HBAR
            assert abs(S - h) / h < 1e-10

    def test_discrepancy_exponent(self):
        """Mode vacuum at Planck cutoff gives 10^{~123} discrepancy."""
        l_P = 1.616e-35  # Planck length
        k_P = 1.0 / l_P
        rho_planck = HBAR * C * k_P**4 / (16 * math.pi**2)
        exponent = math.log10(rho_planck / RHO_DE)
        assert 120 < exponent < 126


# =============================================================================
# Test: Report Generation
# =============================================================================

class TestReport:
    """Tests for report generation."""

    def test_report_runs(self):
        """Report generates without error."""
        report = generate_report()
        assert len(report) > 100

    def test_report_contains_key_sections(self):
        """Report contains expected sections."""
        report = generate_report()
        assert "Cosmological Densities" in report
        assert "NEW Prediction" in report
        assert "OLD Prediction" in report
        assert "Equation of State" in report
        assert "LCDM Equivalence" in report
        assert "Jeans Length" in report


# =============================================================================
# Test: Compton Wavelength and Frequency
# =============================================================================

class TestComptonScales:
    """Tests for Compton wavelength and frequency."""

    def test_compton_wavelength_meV(self):
        """Compton wavelength for ~2 meV is ~0.1 mm."""
        m_kg = 2.0e-3 * EV_TO_KG
        lc = compton_wavelength(m_kg)
        assert 0.05e-3 < lc < 0.2e-3  # 0.05 to 0.2 mm

    def test_compton_frequency_meV(self):
        """Compton frequency for ~2 meV is ~10^12 rad/s."""
        m_kg = 2.0e-3 * EV_TO_KG
        omega = compton_frequency(m_kg)
        assert 1e11 < omega < 1e13

    def test_wavelength_frequency_product(self):
        """lambda_C * omega = c (Compton relation)."""
        m_kg = 2.5e-3 * EV_TO_KG
        lc = compton_wavelength(m_kg)
        omega = compton_frequency(m_kg)
        # lambda_C = hbar/(mc), omega = mc^2/hbar
        # lambda_C * omega = c
        assert abs(lc * omega - C) / C < 1e-10

    def test_inverse_mass_scaling(self):
        """Compton wavelength scales as 1/m."""
        m1 = 1.0e-3 * EV_TO_KG
        m2 = 2.0e-3 * EV_TO_KG
        ratio = compton_wavelength(m1) / compton_wavelength(m2)
        assert abs(ratio - 2.0) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
