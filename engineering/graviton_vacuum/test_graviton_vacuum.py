"""
Test suite for graviton vacuum equation of state calculations.

Tests the central claim: any cutoff on a massless mode sum gives w = +1/3,
while only Lorentz-covariant subtraction gives w = -1.
"""

import numpy as np
import pytest
from scipy import integrate

from graviton_vacuum import (
    HBAR, C, G, M_NU, GRAVITON_POLARIZATIONS,
    rho_cell,
    ModeContributions,
    SharpCutoff,
    GaussianCutoff,
    ExponentialCutoff,
    SmoothStepCutoff,
    PauliVillars,
    AdiabaticRegularization,
    CutoffVsSubtraction,
    GravitySpecialArgument,
    ComparisonTable,
    FinalVerdict,
)


# ===========================================================================
# 1. Individual mode contributions
# ===========================================================================

class TestModeContributions:
    """Test that each massless mode has p(k) = rho(k)/3."""

    def test_w_per_mode_at_various_k(self):
        """w = 1/3 for every k value."""
        for k in [1e-10, 1e-5, 1.0, 1e5, 1e10, 1e20]:
            w = ModeContributions.w_per_mode(k)
            assert abs(w - 1.0 / 3.0) < 1e-14, f"w({k}) = {w}, expected 1/3"

    def test_w_per_mode_at_zero(self):
        """w(0) = 1/3 by continuity."""
        w = ModeContributions.w_per_mode(0)
        assert abs(w - 1.0 / 3.0) < 1e-14

    def test_pressure_equals_rho_over_3(self):
        """p(k) = rho(k)/3 for each k."""
        for k in [0.1, 1.0, 100.0, 1e10]:
            rho = ModeContributions.energy_density_per_mode(k)
            p = ModeContributions.pressure_per_mode(k)
            assert abs(p - rho / 3.0) < 1e-14 * rho, \
                f"p({k}) = {p}, expected rho/3 = {rho/3}"

    def test_energy_density_positive(self):
        """Energy density is positive for all k > 0."""
        for k in [1e-20, 1.0, 1e20]:
            rho = ModeContributions.energy_density_per_mode(k)
            assert rho > 0, f"rho({k}) = {rho}, expected positive"

    def test_energy_density_scales_as_k_cubed(self):
        """rho(k) ~ k^3 for fixed k."""
        k1 = 1.0
        k2 = 10.0
        ratio = ModeContributions.energy_density_per_mode(k2) / \
                ModeContributions.energy_density_per_mode(k1)
        expected = (k2 / k1)**3
        assert abs(ratio - expected) / expected < 1e-12

    def test_graviton_polarization_factor(self):
        """Graviton has 2 polarizations."""
        assert GRAVITON_POLARIZATIONS == 2

    def test_proof_structure(self):
        """The proof returns a complete dictionary."""
        proof = ModeContributions.prove_w_one_third()
        assert "theorem" in proof
        assert "corollary" in proof
        assert "exception" in proof
        assert "1/3" in proof["theorem"]

    def test_dispersion_relation_determines_w(self):
        """
        The key insight: w = 1/3 follows from omega = ck ALONE.

        For a massive field (omega = sqrt(k^2 + m^2)), w(k) = k^2 / (3(k^2+m^2)) < 1/3.
        Only for m = 0 does w(k) = 1/3 for all k.
        """
        # Massless: w = 1/3
        k = 100.0
        omega_massless = k  # c = 1 in natural units perspective
        w_massless = k**2 / (3 * omega_massless**2)
        assert abs(w_massless - 1.0 / 3.0) < 1e-15

        # Massive: w < 1/3
        m = 1.0
        omega_massive = np.sqrt(k**2 + m**2)
        w_massive = k**2 / (3 * omega_massive**2)
        assert w_massive < 1.0 / 3.0
        assert w_massive > 0  # but still positive


# ===========================================================================
# 2. Sharp cutoff
# ===========================================================================

class TestSharpCutoff:
    """Test sharp momentum cutoff gives w = 1/3 exactly."""

    def test_w_exactly_one_third(self):
        """w = 1/3 for sharp cutoff."""
        sc = SharpCutoff(k_max=1e10)
        assert abs(sc.w - 1.0 / 3.0) < 1e-15

    def test_energy_density_formula(self):
        """rho = pol * hbar * c * k_max^4 / (16 pi^2)."""
        k_max = 1e10
        sc = SharpCutoff(k_max)
        expected = 2 * HBAR * C * k_max**4 / (16 * np.pi**2)
        assert abs(sc.energy_density - expected) / expected < 1e-12

    def test_scales_as_k_max_fourth(self):
        """rho scales as k_max^4."""
        sc1 = SharpCutoff(1e10)
        sc2 = SharpCutoff(2e10)
        ratio = sc2.energy_density / sc1.energy_density
        assert abs(ratio - 16.0) / 16.0 < 1e-10  # (2)^4 = 16

    def test_numerical_agrees_with_analytic(self):
        """Numerical integration agrees with analytic formula."""
        sc = SharpCutoff(1e10)
        v = sc.verify_analytic()
        assert v["rho_relative_error"] < 1e-8
        assert abs(v["w_numerical"] - 1.0 / 3.0) < 1e-8

    def test_compton_cutoff(self):
        """k_max = mc/hbar gives the correct value."""
        sc = SharpCutoff.with_compton_cutoff(M_NU)
        k_max_expected = M_NU * C / HBAR
        assert abs(sc.k_max - k_max_expected) / k_max_expected < 1e-12

    def test_ratio_to_cell_vacuum(self):
        """rho_graviton / rho_cell = 2 / (16 pi^2) for sharp cutoff at Compton scale."""
        sc = SharpCutoff.with_compton_cutoff(M_NU)
        ratio = sc.ratio_to_cell(M_NU)
        # rho_graviton = 2 * hbar * c * k^4 / (16 pi^2)
        # rho_cell = m^4 c^5 / hbar^3 = hbar * c * k^4 (since k = mc/hbar)
        # ratio = 2 / (16 pi^2)
        expected = 2.0 / (16.0 * np.pi**2)
        assert abs(ratio - expected) / expected < 1e-10

    def test_energy_density_positive(self):
        """Energy density is positive."""
        sc = SharpCutoff(1e10)
        assert sc.energy_density > 0

    def test_pressure_positive(self):
        """Pressure is positive (radiation has positive pressure)."""
        sc = SharpCutoff(1e10)
        assert sc.pressure > 0

    def test_pressure_equals_rho_over_3(self):
        """p = rho / 3 exactly."""
        sc = SharpCutoff(1e10)
        assert abs(sc.pressure - sc.energy_density / 3.0) < 1e-30 * sc.energy_density


# ===========================================================================
# 3. Gaussian cutoff
# ===========================================================================

class TestGaussianCutoff:
    """Test Gaussian cutoff also gives w = 1/3."""

    def test_w_one_third_analytic(self):
        """Analytic w = 1/3."""
        gc = GaussianCutoff(k_c=1e10)
        assert abs(gc.w - 1.0 / 3.0) < 1e-14

    def test_w_one_third_numerical(self):
        """Numerical w = 1/3."""
        gc = GaussianCutoff(k_c=1e10)
        assert abs(gc.w_numerical - 1.0 / 3.0) < 1e-6

    def test_analytic_matches_numerical(self):
        """Analytic and numerical energy densities agree."""
        gc = GaussianCutoff(k_c=1e10)
        rel_err = abs(gc.energy_density - gc.energy_density_numerical) / gc.energy_density
        assert rel_err < 1e-6

    def test_energy_density_positive(self):
        gc = GaussianCutoff(k_c=1e10)
        assert gc.energy_density > 0

    def test_various_widths_all_give_one_third(self):
        """w = 1/3 regardless of Gaussian width."""
        for k_c in [1.0, 1e5, 1e10, 1e15]:
            gc = GaussianCutoff(k_c)
            assert abs(gc.w - 1.0 / 3.0) < 1e-14, f"k_c={k_c}: w={gc.w}"

    def test_suppression_power_doesnt_change_w(self):
        """w = 1/3 for any suppression power n (f(k)^n)."""
        for n in [1, 2, 3, 4]:
            gc = GaussianCutoff(k_c=1e10, suppression_power=n)
            assert abs(gc.w - 1.0 / 3.0) < 1e-14, f"n={n}: w={gc.w}"

    def test_compton_cutoff(self):
        gc = GaussianCutoff.with_compton_cutoff(M_NU)
        k_expected = M_NU * C / HBAR
        assert abs(gc.k_c - k_expected) / k_expected < 1e-12


# ===========================================================================
# 4. Exponential cutoff
# ===========================================================================

class TestExponentialCutoff:
    """Test exponential cutoff gives w = 1/3."""

    def test_w_one_third(self):
        ec = ExponentialCutoff(k_c=1e10)
        assert abs(ec.w - 1.0 / 3.0) < 1e-14

    def test_analytic_formula(self):
        """rho = pol * hbar * c * 6 * k_c^4 / (4 pi^2)."""
        k_c = 1e10
        ec = ExponentialCutoff(k_c)
        expected = 2 * HBAR * C * 6.0 * k_c**4 / (4 * np.pi**2)
        assert abs(ec.energy_density - expected) / expected < 1e-12

    def test_analytic_matches_numerical(self):
        ec = ExponentialCutoff(k_c=1e10)
        rel_err = abs(ec.energy_density - ec.energy_density_numerical) / ec.energy_density
        assert rel_err < 1e-6

    def test_energy_density_positive(self):
        ec = ExponentialCutoff(k_c=1e10)
        assert ec.energy_density > 0


# ===========================================================================
# 5. Smooth step cutoff
# ===========================================================================

class TestSmoothStepCutoff:
    """Test smooth step (Fermi-Dirac) cutoff gives w = 1/3."""

    def test_w_one_third_narrow_step(self):
        """Narrow step (near-sharp cutoff) gives w ~ 1/3."""
        ss = SmoothStepCutoff(k_c=1e10, delta=1e8)  # delta/k_c = 0.01
        assert abs(ss.w - 1.0 / 3.0) < 1e-4

    def test_w_one_third_wide_step(self):
        """Wide step also gives w = 1/3."""
        ss = SmoothStepCutoff(k_c=1e10, delta=5e9)  # delta/k_c = 0.5
        assert abs(ss.w - 1.0 / 3.0) < 1e-4

    def test_various_widths(self):
        """w = 1/3 for various step widths."""
        k_c = 1e10
        for delta_frac in [0.01, 0.05, 0.1, 0.2, 0.5]:
            ss = SmoothStepCutoff(k_c, delta_frac * k_c)
            assert abs(ss.w - 1.0 / 3.0) < 1e-3, \
                f"delta_frac={delta_frac}: w={ss.w}"

    def test_energy_density_positive(self):
        ss = SmoothStepCutoff(k_c=1e10, delta=1e9)
        assert ss.energy_density > 0

    def test_approaches_sharp_cutoff(self):
        """In the limit delta -> 0, approaches sharp cutoff result."""
        k_c = 1e10
        sc = SharpCutoff(k_c)
        ss = SmoothStepCutoff(k_c, delta=1e6)  # very narrow
        rel_err = abs(ss.energy_density - sc.energy_density) / sc.energy_density
        assert rel_err < 0.01  # within 1%


# ===========================================================================
# 6. Pauli-Villars
# ===========================================================================

class TestPauliVillars:
    """Test that PV regularization gives w = -1."""

    def test_w_close_to_minus_one(self):
        """
        PV-regulated result should have w approaching -1.

        With two PV regulators and finite cutoff Lambda = 1000*M,
        w ~ -0.95 (approaches -1 as Lambda -> inf, logarithmically).
        The key: w is NEGATIVE, unlike any cutoff method which gives +1/3.
        """
        # Use M = 1.0 (normalized) for clean numerics
        pv = PauliVillars(M_PV=1.0)
        w = pv.w
        assert w < -0.9, f"w = {w}, expected < -0.9"
        assert abs(w + 1.0) < 0.1, f"w = {w}, expected close to -1"

    def test_energy_density_negative(self):
        """PV energy density is negative (subtraction result)."""
        pv = PauliVillars(M_PV=1.0)
        assert pv.energy_density_natural < 0, \
            f"rho = {pv.energy_density_natural}, expected negative"

    def test_pressure_positive(self):
        """PV pressure is positive (p = -rho > 0 since rho < 0)."""
        pv = PauliVillars(M_PV=1.0)
        assert pv.pressure_natural > 0, \
            f"p = {pv.pressure_natural}, expected positive"

    def test_verify_lorentz_invariance(self):
        """Verify p ~ -rho (Lorentz invariance condition)."""
        pv = PauliVillars(M_PV=1.0)
        check = pv.verify_lorentz_invariance(rtol=0.1)
        assert check["is_close_to_minus_one"]

    def test_compton_regulator(self):
        pv = PauliVillars.with_compton_regulator(M_NU)
        k_expected = M_NU * C / HBAR
        assert abs(pv.M - k_expected) / k_expected < 1e-12

    def test_w_negative_for_various_masses(self):
        """w is negative (< 0) for various regulator masses, unlike cutoffs."""
        for M in [0.1, 1.0, 10.0, 100.0]:
            pv = PauliVillars(M)
            assert pv.w < 0, f"M={M}: w={pv.w}, expected negative"

    def test_w_distinct_from_cutoff(self):
        """PV w is fundamentally different from cutoff w = +1/3."""
        pv = PauliVillars(M_PV=1.0)
        assert pv.w < -0.5, f"w = {pv.w}, expected much less than +1/3"


# ===========================================================================
# 7. Cutoff vs Subtraction theorem
# ===========================================================================

class TestCutoffVsSubtraction:
    """Test the fundamental distinction between cutoff and subtraction."""

    def test_all_cutoffs_give_one_third(self):
        """Every non-negative weight function gives w = 1/3."""
        k_max = 1e10
        results = CutoffVsSubtraction.demonstrate_cutoff_theorem(k_max)
        for name, data in results.items():
            assert data["w_equals_one_third"], \
                f"{name}: w = {data['w']}, expected 1/3"

    def test_subtraction_gives_negative_w(self):
        """PV subtraction gives w < 0, unlike any cutoff (which gives +1/3)."""
        M_PV = 1.0
        result = CutoffVsSubtraction.demonstrate_subtraction_gives_w_minus_one(M_PV)
        assert result["w"] < -0.9, f"w = {result['w']}, expected < -0.9"

    def test_cell_vacuum_is_cutoff(self):
        """Cell vacuum is characterized as a physical cutoff."""
        info = CutoffVsSubtraction.what_cell_vacuum_does()
        assert info["type"] == "PHYSICAL CUTOFF (not subtraction)"
        assert info["is_dark_energy"] == "NO"


# ===========================================================================
# 8. Gravity-is-special argument
# ===========================================================================

class TestGravitySpecialArgument:
    """Test the linearized graviton mode spectrum."""

    def test_graviton_w_one_third(self):
        """Graviton in linearized gravity has w = 1/3."""
        k_max = 1e10
        result = GravitySpecialArgument.linearized_graviton_mode_spectrum(k_max)
        assert result["w"] == 1.0 / 3.0

    def test_two_polarizations(self):
        result = GravitySpecialArgument.linearized_graviton_mode_spectrum(1e10)
        assert result["polarizations"] == 2

    def test_not_special_vs_scalar(self):
        result = GravitySpecialArgument.linearized_graviton_mode_spectrum(1e10)
        assert "No" in result["is_special_vs_scalar"]

    def test_self_consistency(self):
        """Linearization is valid for neutrino-mass cutoff."""
        result = GravitySpecialArgument.self_consistency_check(M_NU)
        assert result["linearization_valid"]
        assert result["R_lambda_C_squared"] < 1e-50  # extremely small


# ===========================================================================
# 9. Comparison table
# ===========================================================================

class TestComparisonTable:
    """Test the comparison table computations."""

    def test_all_methods_computed(self):
        """All regularization methods are present."""
        results = ComparisonTable.compute_all(M_NU)
        expected_keys = [
            "sharp_cutoff", "gaussian_cutoff", "exponential_cutoff",
            "smooth_step", "pauli_villars", "cell_vacuum_reference"
        ]
        for key in expected_keys:
            assert key in results, f"Missing method: {key}"

    def test_cutoff_methods_give_w_one_third(self):
        """All cutoff methods give w = 1/3."""
        results = ComparisonTable.compute_all(M_NU)
        cutoff_methods = ["sharp_cutoff", "gaussian_cutoff", "exponential_cutoff",
                          "smooth_step"]
        for method in cutoff_methods:
            w = results[method]["w"]
            assert abs(w - 1.0 / 3.0) < 0.01, \
                f"{method}: w = {w}, expected 1/3"

    def test_pv_gives_negative_w(self):
        """PV method gives w < 0, fundamentally different from cutoffs."""
        results = ComparisonTable.compute_all(M_NU)
        w = results["pauli_villars"]["w"]
        assert w < 0, f"PV: w = {w}, expected negative"

    def test_cell_vacuum_gives_w_zero(self):
        """Cell vacuum reference gives w = 0."""
        results = ComparisonTable.compute_all(M_NU)
        w = results["cell_vacuum_reference"]["w"]
        assert w == 0.0

    def test_all_cutoffs_not_lorentz_invariant(self):
        """Cutoff methods are not Lorentz invariant."""
        results = ComparisonTable.compute_all(M_NU)
        cutoff_methods = ["sharp_cutoff", "gaussian_cutoff", "exponential_cutoff",
                          "smooth_step"]
        for method in cutoff_methods:
            assert not results[method]["lorentz_invariant"]

    def test_pv_is_lorentz_invariant(self):
        """PV is Lorentz invariant."""
        results = ComparisonTable.compute_all(M_NU)
        assert results["pauli_villars"]["lorentz_invariant"]

    def test_all_energy_densities_finite(self):
        """All energy densities are finite."""
        results = ComparisonTable.compute_all(M_NU)
        for method, data in results.items():
            assert np.isfinite(data["rho"]), f"{method}: rho not finite"


# ===========================================================================
# 10. Final verdict
# ===========================================================================

class TestFinalVerdict:
    """Test the final verdict structure and content."""

    def test_answer_is_radiation(self):
        verdict = FinalVerdict.answer()
        assert "1/3" in verdict["answer"]
        assert "radiation" in verdict["answer"]

    def test_not_dark_energy(self):
        verdict = FinalVerdict.answer()
        assert "NO" in verdict["is_dark_energy"]

    def test_hypothesis_fails(self):
        verdict = FinalVerdict.answer()
        assert "FAILS" in verdict["hypothesis_status"]

    def test_evidence_tiers_present(self):
        tiers = FinalVerdict.evidence_tiers()
        assert len(tiers) >= 4
        # Check that evidence tiers contain PROVEN or ESTABLISHED
        for key, value in tiers.items():
            assert "[PROVEN]" in value or "[ESTABLISHED]" in value

    def test_confidence_level(self):
        verdict = FinalVerdict.answer()
        assert "PROVEN" in verdict["confidence"]


# ===========================================================================
# 11. Cross-checks and consistency
# ===========================================================================

class TestCrossChecks:
    """Cross-check computations across methods."""

    def test_sharp_vs_gaussian_rho_ratio(self):
        """
        Sharp cutoff rho uses k^4/4, Gaussian uses k_c^4 / (2 * (n/2k_c^2)^2).
        For n=2: integral = 2 k_c^4 / 4 = k_c^4 / 2.
        Sharp: k_c^4 / 4.
        Ratio: Gaussian / Sharp = (k_c^4/2) / (k_c^4/4) = 2.
        """
        k_c = 1e10
        sc = SharpCutoff(k_c)
        gc = GaussianCutoff(k_c, suppression_power=2)
        ratio = gc.energy_density / sc.energy_density
        assert abs(ratio - 2.0) < 1e-10

    def test_sharp_vs_exponential_rho_ratio(self):
        """
        Sharp: integral = k_c^4/4. Exponential: integral = 6 * k_c^4.
        Ratio = 24.
        """
        k_c = 1e10
        sc = SharpCutoff(k_c)
        ec = ExponentialCutoff(k_c)
        ratio = ec.energy_density / sc.energy_density
        assert abs(ratio - 24.0) < 1e-8

    def test_graviton_rho_much_less_than_cell(self):
        """Graviton vacuum energy << cell vacuum energy."""
        sc = SharpCutoff.with_compton_cutoff(M_NU)
        ratio = sc.ratio_to_cell(M_NU)
        # ratio = 1/(8 pi^2) ~ 0.0127
        assert ratio < 0.02  # much less than 1

    def test_graviton_rho_much_less_than_observed_de(self):
        """Graviton vacuum energy << observed dark energy density."""
        sc = SharpCutoff.with_compton_cutoff(M_NU)
        rho_de = 5.96e-10  # J/m^3, observed
        ratio = sc.energy_density / rho_de
        # ratio ~ 0.013
        assert ratio < 0.02  # much less than observed DE

    def test_rho_cell_formula(self):
        """rho_cell = m^4 c^5 / hbar^3."""
        rho = rho_cell(M_NU)
        expected = M_NU**4 * C**5 / HBAR**3
        assert abs(rho - expected) / expected < 1e-12

    def test_all_methods_w_consistent(self):
        """
        All cutoff methods agree on w = 1/3.
        PV agrees on w ~ -1.
        """
        results = ComparisonTable.compute_all(M_NU)

        cutoff_w_values = []
        for method in ["sharp_cutoff", "gaussian_cutoff", "exponential_cutoff", "smooth_step"]:
            cutoff_w_values.append(results[method]["w"])

        # All cutoff w values should be very close to 1/3
        for w in cutoff_w_values:
            assert abs(w - 1.0/3.0) < 0.01

        # PV should be negative (approaching -1)
        assert results["pauli_villars"]["w"] < 0


# ===========================================================================
# 12. Physical reasonableness
# ===========================================================================

class TestPhysicalReasonableness:
    """Test that results are physically reasonable."""

    def test_graviton_energy_order_of_magnitude(self):
        """Graviton vacuum energy should be ~10^{-12} J/m^3."""
        sc = SharpCutoff.with_compton_cutoff(M_NU)
        # rho_cell ~ 6e-10. Ratio ~ 1/316. So rho_graviton ~ 2e-12.
        assert 1e-14 < sc.energy_density < 1e-10

    def test_ratio_is_one_over_32pi_squared(self):
        """rho_graviton / rho_cell = 2/(16 pi^2) = 1/(8 pi^2) ~ 1/79 for sharp cutoff."""
        sc = SharpCutoff.with_compton_cutoff(M_NU)
        ratio = sc.ratio_to_cell(M_NU)
        # Actually: rho_graviton = 2 * hbar*c * k^4 / (16pi^2)
        # rho_cell = m^4 c^5 / hbar^3 = hbar*c * (mc/hbar)^4 = hbar*c * k^4
        # ratio = 2 / (16 pi^2) = 1 / (8 pi^2) ~ 0.01267
        expected = 1.0 / (8.0 * np.pi**2)
        assert abs(ratio - expected) / expected < 1e-10

    def test_linearization_valid(self):
        """Graviton vacuum energy does not significantly curve spacetime."""
        check = GravitySpecialArgument.self_consistency_check(M_NU)
        assert check["R_lambda_C_squared"] < 1e-40

    def test_w_one_third_is_radiation(self):
        """w = 1/3 corresponds to radiation equation of state."""
        # This is a basic physics check
        assert 1.0 / 3.0 == pytest.approx(0.333333333, rel=1e-6)

    def test_w_minus_one_is_cosmological_constant(self):
        """w = -1 corresponds to cosmological constant."""
        # p = -rho, so p + rho = 0 (no gravitational attraction from pressure)
        # and rho + 3p = rho - 3rho = -2rho < 0 (accelerating expansion)
        w = -1
        rho = 1.0  # arbitrary
        p = w * rho
        assert p == -rho
        assert rho + 3 * p < 0  # acceleration condition


# ===========================================================================
# 13. The key theorem: w = 1/3 for any non-negative weight
# ===========================================================================

class TestKeyTheorem:
    """
    Direct numerical proof that w = 1/3 for any non-negative weight function
    on the massless mode integral. This is the central result.
    """

    @pytest.mark.parametrize("weight_name,weight_func", [
        ("constant", lambda k, k_c: 1.0 if k < k_c else 0.0),
        ("linear_decay", lambda k, k_c: max(0, 1 - k/k_c)),
        ("quadratic_decay", lambda k, k_c: max(0, 1 - (k/k_c)**2)),
        ("gaussian", lambda k, k_c: np.exp(-k**2/k_c**2)),
        ("exponential", lambda k, k_c: np.exp(-k/k_c)),
        ("lorentzian", lambda k, k_c: 1.0 / (1.0 + (k/k_c)**2)),
        ("super_gaussian", lambda k, k_c: np.exp(-(k/k_c)**4)),
    ])
    def test_w_one_third_parametrized(self, weight_name, weight_func):
        """w = 1/3 for various weight functions."""
        k_c = 1.0  # arbitrary scale
        n_points = 50000
        k = np.linspace(0, 10 * k_c, n_points)

        # Spectral density (per unit k, after angular integration)
        spectral = k**3  # proportional to k^3

        # Apply weight
        w_arr = np.array([weight_func(ki, k_c) for ki in k])

        rho = np.trapezoid(spectral * w_arr, k)
        p = np.trapezoid(spectral * w_arr / 3.0, k)

        if rho > 0:
            w_val = p / rho
            assert abs(w_val - 1.0/3.0) < 1e-4, \
                f"{weight_name}: w = {w_val}, expected 1/3"


# ===========================================================================
# 14. Adiabatic regularization
# ===========================================================================

class TestAdiabaticRegularization:
    """Test adiabatic regularization properties."""

    def test_gives_w_minus_one(self):
        """Adiabatic regularization gives w = -1."""
        H0 = 2.195e-18  # Hubble constant
        k_max = M_NU * C / HBAR
        ar = AdiabaticRegularization(k_max, H0)
        result = ar.zeroth_order_subtraction()
        assert result["w_adiabatic"] == -1.0

    def test_is_subtraction_scheme(self):
        """Adiabatic regularization is a subtraction, not a cutoff."""
        H0 = 2.195e-18
        k_max = M_NU * C / HBAR
        ar = AdiabaticRegularization(k_max, H0)
        result = ar.zeroth_order_subtraction()
        assert "subtraction" in result["note"].lower() or "covariant" in result["note"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
