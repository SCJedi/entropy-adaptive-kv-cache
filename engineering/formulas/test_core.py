"""
Comprehensive Test Suite for Two Vacua Theory Core Verification
================================================================

This test suite provides 40+ pytest tests covering every claim in the
core_verification module. Each test is independent and checks a specific
physical or mathematical property.

Run with: pytest test_core.py -v
"""

import pytest
import numpy as np
from core_verification import (
    # Constants
    HBAR, C, G, EV_TO_KG, PLANCK_LENGTH, RHO_LAMBDA_OBSERVED,
    DELTA_M21_SQ, DELTA_M31_SQ,
    # Verification functions
    verify_dimensional_uniqueness,
    compute_cell_vacuum_density,
    compute_neutrino_prediction,
    mode_vacuum_massless_integral,
    mode_vacuum_massive_integral,
    verify_16pi2_factor,
    compute_Cd,
    verify_Cd_dimensions,
    compute_orthogonality,
    find_N_for_overlap_threshold,
    predict_neutrino_masses,
    verify_coherent_state_energy,
    verify_minimum_uncertainty,
    number_state_density,
    compute_discrepancy_magnitude,
    verify_legendre_duality,
    verify_gaussian_fourier_duality,
    verify_coherent_equipartition,
    sensitivity_analysis,
    run_all_verifications,
)


# =============================================================================
# TESTS: DIMENSIONAL UNIQUENESS
# =============================================================================

def test_dimensional_solution_exists():
    """Test that the dimensional analysis system has a solution."""
    result = verify_dimensional_uniqueness()
    assert result['is_unique'], "Dimensional system should have unique solution"


def test_dimensional_solution_values():
    """Test that the solution is exactly (4, 5, -3)."""
    result = verify_dimensional_uniqueness()
    assert result['a'] == 4, "Mass exponent should be 4"
    assert result['b'] == 5, "Speed of light exponent should be 5"
    assert result['d'] == -3, "ℏ exponent should be -3"


def test_dimensional_determinant_nonzero():
    """Test that determinant is non-zero (guarantees uniqueness)."""
    result = verify_dimensional_uniqueness()
    assert abs(result['determinant']) > 1e-10, "Determinant must be non-zero"


def test_dimensional_matches_expected():
    """Test that solution matches the expected formula."""
    result = verify_dimensional_uniqueness()
    assert result['matches_expected'], "Solution should match m⁴c⁵/ℏ³"


# =============================================================================
# TESTS: CELL VACUUM ENERGY DENSITY
# =============================================================================

def test_cell_vacuum_two_routes_match():
    """Test that both routes to ρ_cell give identical results."""
    m_test = 2.31e-3 * EV_TO_KG
    result = compute_cell_vacuum_density(m_test)
    assert result['routes_match'], "Both computational routes must agree"


def test_cell_vacuum_route1():
    """Test route 1: ρ = E/V = mc²/λ_C³"""
    m_test = 2.31e-3 * EV_TO_KG
    result = compute_cell_vacuum_density(m_test)

    E = result['energy_per_cell']
    V = result['cell_volume']
    rho_expected = E / V

    assert np.isclose(result['rho_route1'], rho_expected, rtol=1e-12)


def test_cell_vacuum_route2():
    """Test route 2: ρ = m⁴c⁵/ℏ³"""
    m_test = 2.31e-3 * EV_TO_KG
    result = compute_cell_vacuum_density(m_test)

    rho_expected = m_test**4 * C**5 / HBAR**3

    assert np.isclose(result['rho_route2'], rho_expected, rtol=1e-12)


def test_neutrino_mass_gives_correct_density():
    """Test that m₁ = 2.31 meV gives ρ ≈ 5.96e-10 J/m³"""
    result = compute_neutrino_prediction(2.31)
    assert result['verified'], "Should match observed dark energy"
    assert result['percent_error'] < 0.5, "Should be within 0.5%"


def test_neutrino_mass_ratio_to_observation():
    """Test ratio of computed to observed density."""
    result = compute_neutrino_prediction(2.31)
    assert 0.995 < result['ratio'] < 1.005, "Ratio should be very close to 1"


# =============================================================================
# TESTS: MODE VACUUM ENERGY DENSITY
# =============================================================================

def test_mode_vacuum_massless_closed_form():
    """Test closed form ρ = ℏcΛ⁴/(16π²)"""
    k_cutoff = 1e15  # Some test cutoff
    result = mode_vacuum_massless_integral(k_cutoff)

    expected = HBAR * C * k_cutoff**4 / (16 * np.pi**2)
    assert np.isclose(result['rho_closed_form'], expected, rtol=1e-12)


def test_mode_vacuum_massless_integral_matches_closed():
    """Test that numerical integral matches closed form."""
    k_cutoff = 1e15
    result = mode_vacuum_massless_integral(k_cutoff)
    assert result['formulas_match'], "Numerical integral must match closed form"


def test_mode_vacuum_integral_convergence():
    """Test that numerical integration converges (small error)."""
    k_cutoff = 1e15
    result = mode_vacuum_massless_integral(k_cutoff)

    relative_error = result['integration_error'] / result['rho_numerical']
    assert relative_error < 1e-6, "Integration error should be negligible"


def test_mode_vacuum_massive_runs():
    """Test that massive mode vacuum computation runs without error."""
    m_test = 2.31e-3 * EV_TO_KG
    k_cutoff = m_test * C / HBAR
    result = mode_vacuum_massive_integral(m_test, k_cutoff)

    assert result['rho_massive'] > 0, "Density should be positive"
    assert result['verified'], "Integration should converge"


def test_mode_vacuum_massive_correction_factor():
    """Test that massive correction factor is > 1 (more energy)."""
    m_test = 2.31e-3 * EV_TO_KG
    k_cutoff = m_test * C / HBAR
    result = mode_vacuum_massive_integral(m_test, k_cutoff)

    assert result['correction_factor'] > 1.0, "Massive case should have higher energy"


# =============================================================================
# TESTS: THE 16π² FACTOR
# =============================================================================

def test_16pi2_factor_massless():
    """Test that ρ_cell/ρ_mode = 16π² for massless dispersion."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_16pi2_factor(m_test)

    assert result['massless_verified'], "Ratio should equal 16π²"


def test_16pi2_numerical_value():
    """Test the numerical value of 16π²."""
    expected = 16 * np.pi**2
    assert np.isclose(expected, 157.9137, rtol=1e-4), "16π² ≈ 158"


def test_16pi2_massive_correction():
    """Test that massive dispersion modifies the ratio (correction ≠ 1)."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_16pi2_factor(m_test)

    # Massive dispersion gives a correction factor
    # For neutrino masses, this is approximately 0.595
    correction = result['massive_correction']
    assert 0.5 < correction < 0.7, f"Correction factor should be ≈ 0.60, got {correction:.2f}"


def test_16pi2_compton_cutoff():
    """Test that Compton cutoff is k = mc/ℏ."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_16pi2_factor(m_test)

    expected_k = m_test * C / HBAR
    assert np.isclose(result['k_compton'], expected_k, rtol=1e-12)


# =============================================================================
# TESTS: C_d IN d DIMENSIONS
# =============================================================================

def test_Cd_dimension_1():
    """Test C_1 = 4π."""
    C_1 = compute_Cd(1)
    assert np.isclose(C_1, 4 * np.pi, rtol=1e-10), "C_1 should equal 4π"


def test_Cd_dimension_2():
    """Test C_2 = 12π."""
    C_2 = compute_Cd(2)
    assert np.isclose(C_2, 12 * np.pi, rtol=1e-10), "C_2 should equal 12π"


def test_Cd_dimension_3():
    """Test C_3 = 16π²."""
    C_3 = compute_Cd(3)
    assert np.isclose(C_3, 16 * np.pi**2, rtol=1e-10), "C_3 should equal 16π²"


def test_Cd_dimension_dependent():
    """Test that C_d varies with dimension (not fundamental)."""
    results = verify_Cd_dimensions()

    C_values = [results[d]['C_d'] for d in [1, 2, 3, 4, 5]]

    # All should be different
    assert len(set([round(C, 6) for C in C_values])) == 5, "C_d should vary with d"


def test_Cd_all_verified():
    """Test that all C_d verifications pass."""
    results = verify_Cd_dimensions()

    for d in [1, 2, 3]:
        assert results[d]['verified'], f"C_{d} verification failed"


# =============================================================================
# TESTS: ORTHOGONALITY
# =============================================================================

def test_orthogonality_single_cell():
    """Test ⟨0|α⟩ = exp(-|α|²/2) for single cell."""
    result = compute_orthogonality(N=1, alpha_sq=0.5)

    expected = np.exp(-0.5 / 2)
    assert np.isclose(result['overlap_single'], expected, rtol=1e-12)


def test_orthogonality_N_cells():
    """Test ⟨0|Ω⟩ = exp(-N|α|²/2) for N cells."""
    N = 100
    result = compute_orthogonality(N=N, alpha_sq=0.5)

    expected = np.exp(-N * 0.5 / 2)
    assert np.isclose(result['overlap_N'], expected, rtol=1e-12)


def test_orthogonality_exponential_decay():
    """Test that overlap decays exponentially with N."""
    results = [compute_orthogonality(N) for N in [1, 10, 100]]

    overlaps = [r['overlap_N'] for r in results]

    # Each should be smaller than the last
    assert overlaps[0] > overlaps[1] > overlaps[2], "Should decay with N"


def test_orthogonality_threshold():
    """Test finding N for overlap < 10^-100."""
    threshold = 1e-100
    N = find_N_for_overlap_threshold(threshold)

    # Verify it works
    overlap = np.exp(-N * 0.5 / 2)
    assert overlap < threshold, "Should reach threshold"


def test_orthogonality_formula_match():
    """Test that computed overlap matches formula."""
    N = 1000
    result = compute_orthogonality(N)

    assert result['verified'], "Formula should match computation"


# =============================================================================
# TESTS: NEUTRINO MASS PREDICTIONS
# =============================================================================

def test_neutrino_m1_extraction():
    """Test m₁ = (ρℏ³/c⁵)^(1/4) formula."""
    result = predict_neutrino_masses()

    # Manual calculation
    m1_expected = (RHO_LAMBDA_OBSERVED * HBAR**3 / C**5)**0.25
    m1_eV_expected = m1_expected / EV_TO_KG * 1e3

    assert np.isclose(result['m1_meV'], m1_eV_expected, rtol=1e-10)


def test_neutrino_m1_value():
    """Test that m₁ ≈ 2.31 meV."""
    result = predict_neutrino_masses()
    assert 2.30 < result['m1_meV'] < 2.32, "m₁ should be ≈ 2.31 meV"


def test_neutrino_m2_from_oscillation():
    """Test m₂ = √(m₁² + Δm²₂₁)."""
    result = predict_neutrino_masses()

    m1_eV = result['m1_meV'] / 1e3
    m2_expected = np.sqrt(m1_eV**2 + DELTA_M21_SQ) * 1e3

    assert np.isclose(result['m2_meV'], m2_expected, rtol=1e-10)


def test_neutrino_m3_from_oscillation():
    """Test m₃ = √(m₁² + Δm²₃₁)."""
    result = predict_neutrino_masses()

    m1_eV = result['m1_meV'] / 1e3
    m3_expected = np.sqrt(m1_eV**2 + DELTA_M31_SQ) * 1e3

    assert np.isclose(result['m3_meV'], m3_expected, rtol=1e-10)


def test_neutrino_sum_bound():
    """Test that Σmν < 120 meV (cosmological bound)."""
    result = predict_neutrino_masses()
    assert result['sum_meV'] < 120, "Sum should satisfy cosmological bound"


def test_neutrino_sum_value():
    """Test that Σmν ≈ 60.9 meV."""
    result = predict_neutrino_masses()
    assert 60 < result['sum_meV'] < 62, "Sum should be ≈ 60.9 meV"


# =============================================================================
# TESTS: COHERENT STATE PROPERTIES
# =============================================================================

def test_coherent_energy_formula():
    """Test E = ℏω(|α|² + 1/2)."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_coherent_state_energy(m_test, alpha_sq=0.5)

    omega = m_test * C**2 / HBAR
    expected = HBAR * omega * (0.5 + 0.5)

    assert np.isclose(result['E_coherent'], expected, rtol=1e-12)


def test_coherent_energy_equals_mc2():
    """Test that for |α|²=1/2, E = mc²."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_coherent_state_energy(m_test, alpha_sq=0.5)

    assert result['energy_match'], "Energy should equal mc²"


def test_coherent_energy_split():
    """Test that displacement and zero-point energies are equal for |α|²=1/2."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_coherent_state_energy(m_test, alpha_sq=0.5)

    assert result['split_equal'], "Energies should split equally"
    assert np.isclose(result['E_displacement'], result['E_zero_point'], rtol=1e-12)


def test_minimum_uncertainty_bound():
    """Test that Δx·Δp = ℏ/2 (minimum uncertainty)."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_minimum_uncertainty(m_test)

    assert result['saturates_bound'], "Should saturate uncertainty bound"


def test_minimum_uncertainty_value():
    """Test numerical value of Δx·Δp."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_minimum_uncertainty(m_test)

    assert np.isclose(result['product'], HBAR / 2, rtol=1e-12)


# =============================================================================
# TESTS: NUMBER STATE COMPARISON
# =============================================================================

def test_number_state_n1_factor():
    """Test that |n=1⟩ gives ρ = (3/2)m⁴c⁵/ℏ³."""
    m_test = 2.31e-3 * EV_TO_KG
    result = number_state_density(m_test, n=1)

    assert result['verified'], "Factor should be 3/2"
    assert np.isclose(result['factor'], 1.5, rtol=1e-12)


def test_number_state_n0_factor():
    """Test that |n=0⟩ gives ρ = (1/2)m⁴c⁵/ℏ³."""
    m_test = 2.31e-3 * EV_TO_KG
    result = number_state_density(m_test, n=0)

    assert np.isclose(result['factor'], 0.5, rtol=1e-12)


def test_number_state_rules_out():
    """Test that number states don't match observation."""
    m_test = 2.31e-3 * EV_TO_KG

    # n=1 gives 1.5x too much energy
    result = number_state_density(m_test, n=1)
    rho_n1 = result['rho_number']

    # Should NOT match observation
    ratio = rho_n1 / RHO_LAMBDA_OBSERVED
    assert not np.isclose(ratio, 1.0, rtol=0.1), "n=1 should not match"


# =============================================================================
# TESTS: DISCREPANCY MAGNITUDE
# =============================================================================

def test_discrepancy_exponent_range():
    """Test that log₁₀(ρ_Planck/ρ_Λ) ∈ [120, 126]."""
    result = compute_discrepancy_magnitude()
    assert result['verified'], "Exponent should be in valid range"


def test_discrepancy_approximate_123():
    """Test that discrepancy is approximately 10^123."""
    result = compute_discrepancy_magnitude()

    exponent = result['log10_ratio']
    assert 120 < exponent < 126, f"Should be ~123, got {exponent:.1f}"


def test_discrepancy_mode_vacuum_huge():
    """Test that mode vacuum at Planck scale is enormous."""
    result = compute_discrepancy_magnitude()

    assert result['rho_mode_planck'] > 1e110, "Should be > 10^110 J/m³"


# =============================================================================
# TESTS: SELF-DUALITY
# =============================================================================

def test_legendre_self_dual():
    """Test that f(x)=x²/2 is its own Legendre conjugate."""
    result = verify_legendre_duality()
    assert result['verified'], "f(x)=x²/2 should be self-dual"


def test_gaussian_fourier_self_dual():
    """Test that Gaussian FFT has high correlation with itself."""
    result = verify_gaussian_fourier_duality()
    assert result['verified'], "Gaussian should be self-dual under FFT"
    assert result['correlation'] > 0.99, "Correlation should be very high"


def test_coherent_equipartition():
    """Test energy equipartition in coherent state."""
    m_test = 2.31e-3 * EV_TO_KG
    result = verify_coherent_equipartition(m_test, alpha_sq=0.5)

    assert result['verified'], "Should have equipartition"
    assert result['kinetic_verified'], "Kinetic energy should be mc²/2"
    assert result['potential_verified'], "Potential energy should be mc²/2"


# =============================================================================
# TESTS: SENSITIVITY ANALYSIS
# =============================================================================

def test_sensitivity_fourth_root_scaling():
    """Test that m ∝ ρ^(1/4) scaling holds."""
    result = sensitivity_analysis()
    assert result['verified'], "Scaling should be 1/4"


def test_sensitivity_scaling_ratio():
    """Test that scaling ratio ≈ 0.25."""
    result = sensitivity_analysis()

    assert 0.23 < result['scaling_ratio'] < 0.27, "Should be ≈ 0.25"


def test_sensitivity_reduced_uncertainty():
    """Test that mass uncertainty < density uncertainty."""
    result = sensitivity_analysis()

    assert result['m_uncertainty_pct'] < result['rho_uncertainty_pct'], \
        "Mass uncertainty should be smaller (4th root)"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

def test_all_verifications_pass():
    """Integration test: run all verifications and check they pass."""
    results = run_all_verifications()

    passed = sum(1 for r in results if r.verified)
    total = len(results)

    assert passed == total, f"Only {passed}/{total} verifications passed"


def test_verification_result_structure():
    """Test that VerificationResult objects have required attributes."""
    results = run_all_verifications()

    for result in results:
        assert hasattr(result, 'name'), "Should have name"
        assert hasattr(result, 'verified'), "Should have verified status"
        assert hasattr(result, 'details'), "Should have details dict"
        # numpy bool is also acceptable (from np.isclose etc.)
        assert isinstance(result.verified, (bool, np.bool_)), "verified should be bool"


def test_verification_count():
    """Test that we have at least 15 major verifications."""
    results = run_all_verifications()
    assert len(results) >= 15, "Should have at least 15 verifications"


# =============================================================================
# PHYSICS CONSISTENCY TESTS
# =============================================================================

def test_constants_codata_2018():
    """Test that fundamental constants match CODATA 2018."""
    assert np.isclose(HBAR, 1.054571817e-34, rtol=1e-10)
    assert np.isclose(C, 2.99792458e8, rtol=1e-15)
    assert np.isclose(G, 6.67430e-11, rtol=1e-6)


def test_planck_length_value():
    """Test Planck length calculation."""
    l_P_expected = np.sqrt(HBAR * G / C**3)
    assert np.isclose(PLANCK_LENGTH, l_P_expected, rtol=1e-10)


def test_ev_conversion():
    """Test eV to kg conversion."""
    expected = 1.602176634e-19 / C**2
    assert np.isclose(EV_TO_KG, expected, rtol=1e-15)


def test_observed_density_positive():
    """Test that observed dark energy density is positive."""
    assert RHO_LAMBDA_OBSERVED > 0, "Density must be positive"


def test_oscillation_data_positive():
    """Test that neutrino oscillation data is positive."""
    assert DELTA_M21_SQ > 0, "Δm²₂₁ must be positive"
    assert DELTA_M31_SQ > 0, "Δm²₃₁ must be positive"
    assert DELTA_M31_SQ > DELTA_M21_SQ, "Δm²₃₁ > Δm²₂₁ (normal ordering)"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
