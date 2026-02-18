"""
Tests for the Alpha Framework: Axiomatic Vacuum Selection.

Comprehensive test suite verifying:
- Each axiom for each vacuum state
- The full gauntlet
- That mode vacuum fails exactly A1 and F
- That cell vacuum passes everything
- Quantitative scaling behavior
- The selection principle
"""

import numpy as np
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from engineering.axiomatic.alpha_framework import (
    # Classes
    ModeVacuum, CellVacuum, VacuumState,
    AxiomResult, AxiomVerdict, GauntletResult,
    # Axiom checkers
    check_a0_existence, check_a1_refinement,
    check_propagator_composition, check_unitarity,
    check_measurement_consistency, check_locality,
    check_finiteness,
    # Gauntlet
    run_full_gauntlet, axiomatic_selection,
    ALL_AXIOM_CHECKS,
    # Analysis
    refinement_scaling_analysis, entanglement_scaling_analysis,
    comparison_report,
    # Constants
    HBAR, C, M_DEFAULT, LAMBDA_C, RHO_CELL,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mode_vacuum():
    return ModeVacuum()

@pytest.fixture
def cell_vacuum():
    return CellVacuum()

@pytest.fixture
def mode_gauntlet(mode_vacuum):
    return run_full_gauntlet(mode_vacuum)

@pytest.fixture
def cell_gauntlet(cell_vacuum):
    return run_full_gauntlet(cell_vacuum)


# =============================================================================
# Test: Physical Constants
# =============================================================================

class TestConstants:
    """Verify physical constants are consistent."""

    def test_hbar_value(self):
        assert abs(HBAR - 1.054571817e-34) < 1e-43

    def test_c_value(self):
        assert abs(C - 2.99792458e8) < 1.0

    def test_lambda_c_positive(self):
        assert LAMBDA_C > 0

    def test_lambda_c_order_of_magnitude(self):
        # Compton wavelength for meV neutrino ~ 10^-4 m
        assert 1e-5 < LAMBDA_C < 1e-2

    def test_rho_cell_positive(self):
        assert RHO_CELL > 0

    def test_rho_cell_formula(self):
        """rho = m^4 * c^5 / hbar^3"""
        expected = M_DEFAULT**4 * C**5 / HBAR**3
        assert abs(RHO_CELL / expected - 1.0) < 1e-10


# =============================================================================
# Test: Mode Vacuum Properties
# =============================================================================

class TestModeVacuumProperties:
    """Test physical properties of the mode vacuum."""

    def test_name(self, mode_vacuum):
        assert "Mode" in mode_vacuum.name or "mode" in mode_vacuum.name

    def test_infinite_dimensional(self, mode_vacuum):
        """Fock space is infinite-dimensional."""
        dim = mode_vacuum.hilbert_space_dimension(10 * LAMBDA_C)
        assert dim is None

    def test_density_matrix_trace(self, mode_vacuum):
        assert abs(mode_vacuum.density_matrix_trace(10 * LAMBDA_C) - 1.0) < 1e-12

    def test_equation_of_state(self, mode_vacuum):
        """Mode vacuum: w = -1."""
        assert abs(mode_vacuum.equation_of_state() - (-1.0)) < 1e-10

    def test_not_product_state(self, mode_vacuum):
        assert not mode_vacuum.is_product_state()

    def test_energy_density_positive(self, mode_vacuum):
        rho = mode_vacuum.energy_density(LAMBDA_C)
        assert rho > 0

    def test_energy_density_increases_with_refinement(self, mode_vacuum):
        """Finer lattice -> higher energy density (UV divergence)."""
        rho_coarse = mode_vacuum.energy_density(LAMBDA_C)
        rho_fine = mode_vacuum.energy_density(LAMBDA_C / 2)
        assert rho_fine > rho_coarse

    def test_energy_density_divergence_scaling(self, mode_vacuum):
        """rho ~ 1/a^4 for small a."""
        a1 = LAMBDA_C / 10
        a2 = LAMBDA_C / 20
        rho1 = mode_vacuum.energy_density(a1)
        rho2 = mode_vacuum.energy_density(a2)
        # ratio should be approximately (a1/a2)^(-4) = 2^4 = 16
        # Using analytic for cleaner scaling
        rho1_a = mode_vacuum.energy_density_analytic(a1)
        rho2_a = mode_vacuum.energy_density_analytic(a2)
        ratio = rho2_a / rho1_a
        expected_ratio = (a1 / a2)**4  # = 16
        assert abs(ratio / expected_ratio - 1.0) < 0.01

    def test_analytic_vs_numerical_scaling(self, mode_vacuum):
        """Analytic 1/a^4 approximation matches numerical at small a."""
        a = LAMBDA_C / 100  # Well into UV regime
        rho_num = mode_vacuum.energy_density(a)
        rho_ana = mode_vacuum.energy_density_analytic(a)
        # Should agree to within ~10% in deep UV
        ratio = rho_num / rho_ana
        assert 0.8 < ratio < 1.5

    def test_entanglement_entropy_positive(self, mode_vacuum):
        area = (10 * LAMBDA_C)**2
        S = mode_vacuum.entanglement_entropy(area, LAMBDA_C)
        assert S > 0

    def test_entanglement_entropy_diverges(self, mode_vacuum):
        """S ~ A/a^2, diverges as cutoff shrinks."""
        area = (10 * LAMBDA_C)**2
        S1 = mode_vacuum.entanglement_entropy(area, LAMBDA_C)
        S2 = mode_vacuum.entanglement_entropy(area, LAMBDA_C / 10)
        assert S2 > S1
        # Ratio should be ~100 (since a^2 in denominator, 10x smaller -> 100x bigger)
        assert S2 / S1 > 50


# =============================================================================
# Test: Cell Vacuum Properties
# =============================================================================

class TestCellVacuumProperties:
    """Test physical properties of the cell vacuum."""

    def test_name(self, cell_vacuum):
        assert "Cell" in cell_vacuum.name or "cell" in cell_vacuum.name

    def test_finite_dimensional(self, cell_vacuum):
        """Each cell has finite-dimensional Hilbert space."""
        dim = cell_vacuum.hilbert_space_dimension(10 * LAMBDA_C)
        assert dim is not None
        assert isinstance(dim, int)
        assert dim > 0

    def test_density_matrix_trace(self, cell_vacuum):
        assert abs(cell_vacuum.density_matrix_trace(10 * LAMBDA_C) - 1.0) < 1e-12

    def test_equation_of_state(self, cell_vacuum):
        """Cell vacuum: w = 0."""
        assert abs(cell_vacuum.equation_of_state()) < 1e-10

    def test_is_product_state(self, cell_vacuum):
        assert cell_vacuum.is_product_state()

    def test_zero_pressure(self, cell_vacuum):
        assert abs(cell_vacuum.pressure()) < 1e-20

    def test_energy_density_value(self, cell_vacuum):
        """rho = m^4 c^5 / hbar^3."""
        expected = M_DEFAULT**4 * C**5 / HBAR**3
        assert abs(cell_vacuum.energy_density(LAMBDA_C) / expected - 1.0) < 1e-10

    def test_energy_density_independent_of_lattice(self, cell_vacuum):
        """Energy density is constant regardless of lattice spacing."""
        rho_1 = cell_vacuum.energy_density(LAMBDA_C)
        rho_2 = cell_vacuum.energy_density(LAMBDA_C / 2)
        rho_3 = cell_vacuum.energy_density(LAMBDA_C / 10)
        rho_4 = cell_vacuum.energy_density(LAMBDA_C / 100)
        assert abs(rho_1 - rho_2) < 1e-20
        assert abs(rho_1 - rho_3) < 1e-20
        assert abs(rho_1 - rho_4) < 1e-20

    def test_zero_entanglement(self, cell_vacuum):
        """Product state has zero entanglement entropy."""
        area = (10 * LAMBDA_C)**2
        S = cell_vacuum.entanglement_entropy(area, LAMBDA_C)
        assert S == 0.0

    def test_zero_entanglement_any_cutoff(self, cell_vacuum):
        """Entanglement is zero regardless of cutoff."""
        area = (10 * LAMBDA_C)**2
        for cutoff_ratio in [1.0, 0.5, 0.1, 0.01]:
            S = cell_vacuum.entanglement_entropy(area, cutoff_ratio * LAMBDA_C)
            assert S == 0.0

    def test_coherent_state_amplitudes(self, cell_vacuum):
        """Coherent state amplitudes form a valid distribution."""
        amps = cell_vacuum.coherent_state_amplitudes(50)
        # Probabilities should sum to ~1
        probs = amps**2
        assert abs(np.sum(probs) - 1.0) < 1e-6

    def test_coherent_state_overlap_decreases(self, cell_vacuum):
        """Overlap with Fock vacuum decreases exponentially with N."""
        overlaps = [cell_vacuum.coherent_state_overlap_with_fock_vacuum(N)
                     for N in [1, 10, 100, 1000]]
        # Each should be smaller than the previous
        for i in range(len(overlaps) - 1):
            assert overlaps[i+1] < overlaps[i]
        # For large N, overlap should be negligible
        assert overlaps[-1] < 1e-50

    def test_num_cells_in_region(self, cell_vacuum):
        """Region size determines number of cells."""
        n = cell_vacuum.num_cells_in_region(10 * LAMBDA_C)
        assert n == 10

    def test_partial_trace_consistency(self, cell_vacuum):
        """Product state: partial trace is trivially consistent."""
        assert cell_vacuum.partial_trace_consistency(10) == 0.0


# =============================================================================
# Test: Axiom A0 - Existence
# =============================================================================

class TestAxiomA0:
    """Test the existence axiom for both vacua."""

    def test_mode_vacuum_passes(self, mode_vacuum):
        result = check_a0_existence(mode_vacuum)
        assert result.passed
        assert result.axiom_label == "A0"

    def test_cell_vacuum_passes(self, cell_vacuum):
        result = check_a0_existence(cell_vacuum)
        assert result.passed

    def test_mode_vacuum_infinite_dim(self, mode_vacuum):
        result = check_a0_existence(mode_vacuum)
        assert result.evidence["hilbert_dim"] == "infinite"

    def test_cell_vacuum_finite_dim(self, cell_vacuum):
        result = check_a0_existence(cell_vacuum)
        assert isinstance(result.evidence["hilbert_dim"], int)

    def test_both_have_valid_trace(self, mode_vacuum, cell_vacuum):
        r_mode = check_a0_existence(mode_vacuum)
        r_cell = check_a0_existence(cell_vacuum)
        assert abs(r_mode.evidence["density_matrix_trace"] - 1.0) < 1e-10
        assert abs(r_cell.evidence["density_matrix_trace"] - 1.0) < 1e-10


# =============================================================================
# Test: Axiom A1 - Refinability
# =============================================================================

class TestAxiomA1:
    """Test the refinability axiom."""

    def test_mode_vacuum_fails(self, mode_vacuum):
        result = check_a1_refinement(mode_vacuum)
        assert not result.passed
        assert result.axiom_label == "A1"

    def test_cell_vacuum_passes(self, cell_vacuum):
        result = check_a1_refinement(cell_vacuum)
        assert result.passed

    def test_mode_vacuum_divergent_exponent(self, mode_vacuum):
        result = check_a1_refinement(mode_vacuum)
        # Scaling exponent should be approximately -4 (rho ~ a^{-4})
        exp = result.evidence["scaling_exponent"]
        assert exp < -3.0  # Should be close to -4

    def test_cell_vacuum_constant_exponent(self, cell_vacuum):
        result = check_a1_refinement(cell_vacuum)
        # Scaling exponent should be ~0 (constant)
        exp = result.evidence["scaling_exponent"]
        assert abs(exp) < 0.5

    def test_mode_vacuum_density_ratios_large(self, mode_vacuum):
        result = check_a1_refinement(mode_vacuum)
        max_ratio = result.evidence["max_ratio"]
        assert max_ratio > 10  # Divergent ratios

    def test_cell_vacuum_density_ratios_unity(self, cell_vacuum):
        result = check_a1_refinement(cell_vacuum)
        ratios = result.evidence["density_ratios"]
        for r in ratios:
            assert abs(r - 1.0) < 1e-10  # All ratios = 1


# =============================================================================
# Test: Axiom P - Propagator Composition
# =============================================================================

class TestAxiomP:
    """Test propagator composition."""

    def test_mode_vacuum_passes(self, mode_vacuum):
        result = check_propagator_composition(mode_vacuum)
        assert result.passed
        assert result.axiom_label == "P"

    def test_cell_vacuum_passes(self, cell_vacuum):
        result = check_propagator_composition(cell_vacuum)
        assert result.passed

    def test_composition_error_small(self, mode_vacuum, cell_vacuum):
        for v in [mode_vacuum, cell_vacuum]:
            result = check_propagator_composition(v)
            assert result.evidence["composition_error"] < 1e-10


# =============================================================================
# Test: Axiom Q - Unitarity
# =============================================================================

class TestAxiomQ:
    """Test unitarity."""

    def test_mode_vacuum_passes(self, mode_vacuum):
        result = check_unitarity(mode_vacuum)
        assert result.passed
        assert result.axiom_label == "Q"

    def test_cell_vacuum_passes(self, cell_vacuum):
        result = check_unitarity(cell_vacuum)
        assert result.passed

    def test_unitarity_error_small(self, mode_vacuum, cell_vacuum):
        for v in [mode_vacuum, cell_vacuum]:
            result = check_unitarity(v)
            assert result.evidence["max_unitarity_error"] < 1e-10

    def test_cell_vacuum_qho_unitarity_explicit(self, cell_vacuum):
        """Explicitly check U^dag U = I for QHO evolution matrix."""
        omega_C = M_DEFAULT * C**2 / HBAR
        t = 2.3 / omega_C
        U = cell_vacuum._qho_evolution_matrix(t, dim=10)
        product = U.conj().T @ U
        assert np.allclose(product, np.eye(10), atol=1e-12)


# =============================================================================
# Test: Axiom M' - Measurement Consistency
# =============================================================================

class TestAxiomMPrime:
    """Test measurement consistency."""

    def test_mode_vacuum_passes(self, mode_vacuum):
        result = check_measurement_consistency(mode_vacuum)
        assert result.passed
        assert result.axiom_label == "M'"

    def test_cell_vacuum_passes(self, cell_vacuum):
        result = check_measurement_consistency(cell_vacuum)
        assert result.passed

    def test_probability_sums_near_one(self, mode_vacuum, cell_vacuum):
        for v in [mode_vacuum, cell_vacuum]:
            result = check_measurement_consistency(v)
            for s in result.evidence["probability_sums"]:
                assert abs(s - 1.0) < 1e-4

    def test_cell_vacuum_poisson_distribution(self, cell_vacuum):
        """Coherent state yields Poisson statistics."""
        alpha_sq = abs(cell_vacuum.alpha)**2
        # Mean of Poisson should be |alpha|^2
        n = np.arange(200)
        log_probs = -alpha_sq + 2 * n * np.log(abs(cell_vacuum.alpha)) \
                    - np.array([sum(np.log(np.arange(1, k+1))) if k > 0 else 0.0 for k in n])
        probs = np.exp(log_probs)
        mean = np.sum(n * probs)
        assert abs(mean - alpha_sq) < 0.01


# =============================================================================
# Test: Axiom L - Locality
# =============================================================================

class TestAxiomL:
    """Test locality (no-signaling)."""

    def test_mode_vacuum_passes(self, mode_vacuum):
        result = check_locality(mode_vacuum)
        assert result.passed
        assert result.axiom_label == "L"

    def test_cell_vacuum_passes(self, cell_vacuum):
        result = check_locality(cell_vacuum)
        assert result.passed

    def test_cell_vacuum_product_state(self, cell_vacuum):
        result = check_locality(cell_vacuum)
        assert result.evidence["is_product_state"] is True

    def test_mode_vacuum_not_product(self, mode_vacuum):
        result = check_locality(mode_vacuum)
        assert result.evidence["is_product_state"] is False

    def test_cell_vacuum_zero_entropy(self, cell_vacuum):
        result = check_locality(cell_vacuum)
        assert result.evidence["entanglement_entropy"] == 0.0

    def test_mode_vacuum_nonzero_entropy(self, mode_vacuum):
        result = check_locality(mode_vacuum)
        assert result.evidence["entanglement_entropy"] > 0


# =============================================================================
# Test: Axiom F - Finiteness
# =============================================================================

class TestAxiomF:
    """Test finiteness."""

    def test_mode_vacuum_fails(self, mode_vacuum):
        result = check_finiteness(mode_vacuum)
        assert not result.passed
        assert result.axiom_label == "F"

    def test_cell_vacuum_passes(self, cell_vacuum):
        result = check_finiteness(cell_vacuum)
        assert result.passed

    def test_mode_vacuum_cutoff_dependent(self, mode_vacuum):
        result = check_finiteness(mode_vacuum)
        assert result.evidence["cutoff_dependent"]

    def test_cell_vacuum_cutoff_independent(self, cell_vacuum):
        result = check_finiteness(cell_vacuum)
        assert not result.evidence["cutoff_dependent"]

    def test_cell_vacuum_energy_density_value(self, cell_vacuum):
        result = check_finiteness(cell_vacuum)
        expected = M_DEFAULT**4 * C**5 / HBAR**3
        actual = result.evidence["energy_density_J_m3"]
        assert abs(actual / expected - 1.0) < 1e-10

    def test_cell_vacuum_w_zero(self, cell_vacuum):
        result = check_finiteness(cell_vacuum)
        assert abs(result.evidence["equation_of_state_w"]) < 1e-10

    def test_mode_vacuum_w_minus_one(self, mode_vacuum):
        result = check_finiteness(mode_vacuum)
        assert abs(result.evidence["equation_of_state_w"] + 1.0) < 1e-10


# =============================================================================
# Test: Full Gauntlet
# =============================================================================

class TestFullGauntlet:
    """Test the complete axiom gauntlet."""

    def test_mode_vacuum_fails_gauntlet(self, mode_gauntlet):
        assert not mode_gauntlet.all_passed

    def test_cell_vacuum_passes_gauntlet(self, cell_gauntlet):
        assert cell_gauntlet.all_passed

    def test_mode_vacuum_fails_exactly_a1_and_f(self, mode_gauntlet):
        failures = set(mode_gauntlet.failures)
        assert failures == {"A1", "F"}

    def test_mode_vacuum_passes_others(self, mode_gauntlet):
        passes = set(mode_gauntlet.passes)
        assert passes == {"A0", "P", "Q", "M'", "L"}

    def test_cell_vacuum_passes_all(self, cell_gauntlet):
        assert len(cell_gauntlet.failures) == 0
        assert len(cell_gauntlet.passes) == 7

    def test_all_seven_axioms_checked(self, mode_gauntlet, cell_gauntlet):
        assert len(mode_gauntlet.results) == 7
        assert len(cell_gauntlet.results) == 7

    def test_gauntlet_summary_is_string(self, mode_gauntlet):
        summary = mode_gauntlet.summary()
        assert isinstance(summary, str)
        assert "FAIL" in summary

    def test_gauntlet_result_labels(self, mode_gauntlet):
        expected_labels = {"A0", "A1", "P", "Q", "M'", "L", "F"}
        assert set(mode_gauntlet.results.keys()) == expected_labels


# =============================================================================
# Test: Axiom Selection Principle
# =============================================================================

class TestSelectionPrinciple:
    """Test the axiomatic selection principle."""

    def test_cell_vacuum_is_unique_survivor(self):
        mode = ModeVacuum()
        cell = CellVacuum()
        survivors = axiomatic_selection([mode, cell])
        assert len(survivors) == 1
        assert isinstance(survivors[0], CellVacuum)

    def test_mode_vacuum_eliminated(self):
        mode = ModeVacuum()
        cell = CellVacuum()
        survivors = axiomatic_selection([mode, cell])
        for s in survivors:
            assert not isinstance(s, ModeVacuum)

    def test_selection_with_only_mode(self):
        mode = ModeVacuum()
        survivors = axiomatic_selection([mode])
        assert len(survivors) == 0  # No survivors

    def test_selection_with_only_cell(self):
        cell = CellVacuum()
        survivors = axiomatic_selection([cell])
        assert len(survivors) == 1


# =============================================================================
# Test: Quantitative Scaling
# =============================================================================

class TestQuantitativeScaling:
    """Test quantitative behavior of physical observables."""

    def test_mode_vacuum_fourth_power_divergence(self):
        """Energy density scales as 1/a^4."""
        mode = ModeVacuum()
        analysis = refinement_scaling_analysis(mode)
        # Scaling exponent should be approximately -4
        assert analysis["scaling_exponent"] < -3.5
        assert analysis["diverges"]

    def test_cell_vacuum_constant_density(self):
        """Energy density is constant (scaling exponent ~ 0)."""
        cell = CellVacuum()
        analysis = refinement_scaling_analysis(cell)
        assert abs(analysis["scaling_exponent"]) < 0.1
        assert not analysis["diverges"]

    def test_mode_vacuum_entanglement_diverges(self):
        """Entanglement entropy diverges as cutoff shrinks."""
        mode = ModeVacuum()
        analysis = entanglement_scaling_analysis(mode)
        assert analysis["diverges"]
        assert analysis["max_entropy"] > 100 * analysis["min_entropy"]

    def test_cell_vacuum_entanglement_zero(self):
        """Entanglement entropy is identically zero."""
        cell = CellVacuum()
        analysis = entanglement_scaling_analysis(cell)
        assert analysis["max_entropy"] == 0.0
        assert analysis["min_entropy"] == 0.0
        assert not analysis["diverges"]

    def test_mode_density_at_specific_spacings(self):
        """Check mode vacuum density at specific lattice spacings."""
        mode = ModeVacuum()
        # At a = lambda_C
        rho_1 = mode.energy_density(LAMBDA_C)
        # At a = lambda_C / 10
        rho_10 = mode.energy_density(LAMBDA_C / 10)
        # Ratio should be approximately 10^4 = 10000
        ratio = rho_10 / rho_1
        assert ratio > 1000  # At least 3 orders of magnitude increase

    def test_cell_density_at_specific_spacings(self):
        """Check cell vacuum density is constant at all spacings."""
        cell = CellVacuum()
        spacings = [LAMBDA_C, LAMBDA_C/2, LAMBDA_C/10, LAMBDA_C/100]
        densities = [cell.energy_density(a) for a in spacings]
        for d in densities:
            assert abs(d - densities[0]) < 1e-20

    def test_energy_density_ratio_at_compton_cutoff(self):
        """Compare mode and cell density at Compton cutoff."""
        mode = ModeVacuum()
        cell = CellVacuum()
        rho_mode = mode.energy_density(LAMBDA_C)
        rho_cell = cell.energy_density(LAMBDA_C)
        # Both should be positive
        assert rho_mode > 0
        assert rho_cell > 0


# =============================================================================
# Test: AxiomResult Structure
# =============================================================================

class TestAxiomResultStructure:
    """Test the result data structures."""

    def test_axiom_result_has_required_fields(self, mode_vacuum):
        result = check_a0_existence(mode_vacuum)
        assert hasattr(result, "axiom_name")
        assert hasattr(result, "axiom_label")
        assert hasattr(result, "verdict")
        assert hasattr(result, "evidence")
        assert hasattr(result, "explanation")

    def test_axiom_result_passed_property(self):
        result = AxiomResult(
            axiom_name="Test", axiom_label="T",
            verdict=AxiomVerdict.PASS, evidence={}, explanation=""
        )
        assert result.passed is True

    def test_axiom_result_failed_property(self):
        result = AxiomResult(
            axiom_name="Test", axiom_label="T",
            verdict=AxiomVerdict.FAIL, evidence={}, explanation=""
        )
        assert result.passed is False

    def test_axiom_result_repr(self, mode_vacuum):
        result = check_a0_existence(mode_vacuum)
        r = repr(result)
        assert "A0" in r
        assert "PASS" in r

    def test_gauntlet_result_summary(self, cell_gauntlet):
        summary = cell_gauntlet.summary()
        assert "ALL PASSED" in summary

    def test_gauntlet_result_failures_list(self, mode_gauntlet):
        assert "A1" in mode_gauntlet.failures
        assert "F" in mode_gauntlet.failures

    def test_evidence_is_dict(self, mode_vacuum):
        for _, check_fn in ALL_AXIOM_CHECKS:
            result = check_fn(mode_vacuum)
            assert isinstance(result.evidence, dict)


# =============================================================================
# Test: Comparison Report
# =============================================================================

class TestComparisonReport:
    """Test the comparison report generation."""

    def test_report_is_string(self):
        report = comparison_report()
        assert isinstance(report, str)

    def test_report_contains_both_vacua(self):
        report = comparison_report()
        assert "Mode" in report
        assert "Cell" in report

    def test_report_contains_selection_principle(self):
        report = comparison_report()
        assert "SELECTION PRINCIPLE" in report

    def test_report_contains_all_axioms(self):
        report = comparison_report()
        for label, _ in ALL_AXIOM_CHECKS:
            assert label in report

    def test_report_identifies_failures(self):
        report = comparison_report()
        assert "FAIL" in report

    def test_report_mentions_dark_matter(self):
        report = comparison_report()
        assert "dark matter" in report.lower() or "w=0" in report or "w = 0" in report


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_small_lattice_spacing(self):
        mode = ModeVacuum()
        # Very small spacing should give very large density
        rho = mode.energy_density(LAMBDA_C / 1000)
        assert rho > mode.energy_density(LAMBDA_C) * 1e6

    def test_very_large_lattice_spacing(self):
        cell = CellVacuum()
        # Large spacing should still give same density
        rho = cell.energy_density(100 * LAMBDA_C)
        assert abs(rho - cell.rho) < 1e-20

    def test_different_neutrino_masses(self):
        """Framework works with different mass parameters."""
        from engineering.axiomatic.alpha_framework import M_NU_NEW
        mode_new = ModeVacuum(mass=M_NU_NEW)
        cell_new = CellVacuum(mass=M_NU_NEW)
        g_mode = run_full_gauntlet(mode_new)
        g_cell = run_full_gauntlet(cell_new)
        # Same qualitative results regardless of mass
        assert not g_mode.all_passed
        assert g_cell.all_passed
        assert set(g_mode.failures) == {"A1", "F"}

    def test_single_cell_region(self):
        cell = CellVacuum()
        n = cell.num_cells_in_region(LAMBDA_C)
        assert n >= 1

    def test_zero_time_evolution(self):
        """U(0) = I."""
        cell = CellVacuum()
        U = cell._qho_evolution_matrix(0.0, dim=5)
        # Should be diagonal with phases exp(-i * omega * (n+0.5) * 0) = 1
        assert np.allclose(U, np.eye(5), atol=1e-12)

    def test_propagator_composition_at_equal_times(self):
        """U(t,t) = I, so U(t2,t0) = U(t2,t)*U(t,t0) = U(t2,t0)."""
        cell = CellVacuum()
        omega_C = M_DEFAULT * C**2 / HBAR
        t = 1.0 / omega_C
        error = cell.propagator_composition_error(0, t, t)
        assert error < 1e-10


# =============================================================================
# Test: Physics Implications
# =============================================================================

class TestPhysicsImplications:
    """Test that the framework produces physically meaningful results."""

    def test_cell_vacuum_is_dark_matter_candidate(self):
        """w = 0 means pressureless dust = cold dark matter."""
        cell = CellVacuum()
        assert cell.equation_of_state() == 0.0

    def test_mode_vacuum_is_dark_energy_like(self):
        """w = -1 means cosmological constant = dark energy."""
        mode = ModeVacuum()
        assert mode.equation_of_state() == -1.0

    def test_axioms_select_dark_matter_over_dark_energy(self):
        """The selection principle picks w=0 over w=-1."""
        mode = ModeVacuum()
        cell = CellVacuum()
        survivors = axiomatic_selection([mode, cell])
        assert len(survivors) == 1
        assert survivors[0].equation_of_state() == 0.0  # w=0 selected

    def test_cell_vacuum_energy_density_cosmological_scale(self):
        """Cell vacuum energy density is in the right ballpark for cosmology."""
        cell = CellVacuum()
        rho = cell.energy_density(LAMBDA_C)
        # Should be ~10^-10 J/m^3 (cosmological scale)
        assert 1e-12 < rho < 1e-6

    def test_orthogonality_of_vacua(self):
        """Cell and mode vacua become orthogonal for many cells."""
        cell = CellVacuum()
        overlap = cell.coherent_state_overlap_with_fock_vacuum(1000)
        assert overlap < 1e-100  # Effectively zero


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
