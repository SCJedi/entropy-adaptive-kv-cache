"""
Test Suite for Squeezed Cell Vacuum Equation of State

Tests verify the central result: w = 0 for ALL squeezed coherent states
of a massive scalar field (QHO virial theorem).

Test categories:
1. Coherent state limit (r=0): recover known cell vacuum results
2. Squeezed vacuum (alpha=0): w=0
3. General squeezed coherent: w=0 for all r
4. Virial theorem for arbitrary states
5. Energy density increases with squeezing
6. Time-averaged pressure vanishes for all r
7. Numerical verification by explicit time integration
8. Uncertainty relations preserved
9. Edge cases and consistency checks
"""

import numpy as np
import pytest
from squeezed_vacuum import (
    HBAR, C, M_ELECTRON,
    SqueezedCoherentState,
    SqueezedStressEnergy,
    VirialTheoremQHO,
    EnergyDensityComparison,
    SqueezedUncertainty,
    WZeroUniversality,
    NumericalVerification,
    compute_full_analysis,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_time_array(se: SqueezedStressEnergy, n_periods=100, pts_per_period=1000):
    """Create a time array spanning n_periods with high resolution."""
    n_total = n_periods * pts_per_period
    return np.linspace(0, n_periods * se.period, n_total, endpoint=False)


# ---------------------------------------------------------------------------
# 1. Coherent state limit (r=0)
# ---------------------------------------------------------------------------
class TestCoherentStateLimit:
    """When r=0, squeezed state reduces to coherent state."""

    def test_mean_particle_number_r0(self):
        """For r=0: <n> = |alpha|^2"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=0.0)
        assert abs(state.mean_n - 0.5) < 1e-15

    def test_no_extra_particles_r0(self):
        """For r=0: sinh^2(0) = 0, no squeeze particles"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=0.0)
        assert state.n_squeeze == 0.0

    def test_anomalous_correlator_r0(self):
        """For r=0: anomalous correlator vanishes"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=0.0)
        assert abs(state.anomalous_correlator) < 1e-15

    def test_a_squared_expectation_r0(self):
        """For r=0: <a^2> = alpha^2"""
        alpha = np.sqrt(0.5)
        state = SqueezedCoherentState(alpha=alpha, r=0.0)
        expected = alpha ** 2
        assert abs(state.a_squared_expectation - expected) < 1e-15

    def test_energy_density_r0(self):
        """For r=0, |alpha|^2=1/2: rho = hbar*omega"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=0.0)
        se = SqueezedStressEnergy(state=state)
        rho_expected = HBAR * se.omega * 1.0  # (0.5 + 0.5)
        rho_computed = se.energy_density_analytic()
        assert abs(rho_computed - rho_expected) / rho_expected < 1e-12

    def test_w_zero_r0(self):
        """w = 0 for coherent state (known result)"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=0.0)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=200)
        w = se.w_time_averaged(t)
        assert abs(w) < 1e-6, f"w = {w}, expected 0"


# ---------------------------------------------------------------------------
# 2. Squeezed vacuum (alpha=0)
# ---------------------------------------------------------------------------
class TestSqueezedVacuum:
    """Squeezed vacuum: S(r)|0> (no displacement)."""

    def test_mean_n_squeezed_vacuum(self):
        """<n> = sinh^2(r) for squeezed vacuum"""
        for r in [0.1, 0.5, 1.0, 2.0]:
            state = SqueezedCoherentState(alpha=0.0, r=r)
            expected = np.sinh(r) ** 2
            assert abs(state.mean_n - expected) < 1e-12

    def test_energy_squeezed_vacuum(self):
        """rho = hbar*omega*(sinh^2(r) + 1/2) for squeezed vacuum"""
        for r in [0.5, 1.0, 2.0]:
            state = SqueezedCoherentState(alpha=0.0, r=r)
            se = SqueezedStressEnergy(state=state)
            rho_expected = HBAR * se.omega * (np.sinh(r) ** 2 + 0.5)
            rho_computed = se.energy_density_analytic()
            assert abs(rho_computed - rho_expected) / rho_expected < 1e-12

    def test_w_zero_squeezed_vacuum(self):
        """w = 0 for squeezed vacuum at several r values"""
        for r in [0.1, 0.5, 1.0, 1.5, 2.0]:
            state = SqueezedCoherentState(alpha=0.0, r=r)
            se = SqueezedStressEnergy(state=state)
            t = make_time_array(se, n_periods=200)
            w = se.w_time_averaged(t)
            assert abs(w) < 1e-5, f"r={r}: w = {w}, expected 0"

    def test_anomalous_correlator_squeezed_vacuum(self):
        """<a^2> = -(1/2)*sinh(2r) for squeezed vacuum (theta=0)"""
        for r in [0.5, 1.0, 2.0]:
            state = SqueezedCoherentState(alpha=0.0, r=r)
            expected = -0.5 * np.sinh(2 * r)
            assert abs(state.a_squared_expectation - expected) < 1e-12


# ---------------------------------------------------------------------------
# 3. General squeezed coherent: w=0 for all r
# ---------------------------------------------------------------------------
class TestGeneralSqueezedCoherent:
    """w = 0 for general squeezed coherent states."""

    @pytest.mark.parametrize("r", [0.0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 3.0])
    def test_w_zero_real_alpha(self, r):
        """w = 0 for real alpha, varying r"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=r)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=300)
        w = se.w_time_averaged(t)
        assert abs(w) < 1e-4, f"r={r}: w = {w}"

    @pytest.mark.parametrize("r", [0.5, 1.0, 2.0])
    def test_w_zero_complex_alpha(self, r):
        """w = 0 for complex alpha"""
        alpha = np.sqrt(0.25) * np.exp(1j * np.pi / 4)  # |alpha|^2 = 0.25
        state = SqueezedCoherentState(alpha=alpha, r=r)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=300)
        w = se.w_time_averaged(t)
        assert abs(w) < 1e-4, f"r={r}: w = {w}"

    @pytest.mark.parametrize("theta", [0, np.pi / 4, np.pi / 2, np.pi, 3 * np.pi / 2])
    def test_w_zero_varying_theta(self, theta):
        """w = 0 for different squeezing angles"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=1.0, theta=theta)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=300)
        w = se.w_time_averaged(t)
        assert abs(w) < 1e-4, f"theta={theta}: w = {w}"

    def test_w_zero_large_alpha(self):
        """w = 0 even for large displacement"""
        state = SqueezedCoherentState(alpha=10.0, r=1.0)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=300)
        w = se.w_time_averaged(t)
        assert abs(w) < 1e-4, f"w = {w}"


# ---------------------------------------------------------------------------
# 4. Virial theorem for arbitrary states
# ---------------------------------------------------------------------------
class TestVirialTheorem:
    """Test the virial theorem <T>_t = <V>_t for various states."""

    def test_virial_coherent(self):
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=0.0)
        result = VirialTheoremQHO.verify_for_squeezed_state(state)
        assert result["virial_holds"], f"Virial error: {result['virial_relative_error']}"

    def test_virial_squeezed(self):
        for r in [0.5, 1.0, 2.0]:
            state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=r)
            result = VirialTheoremQHO.verify_for_squeezed_state(state)
            assert result["virial_holds"], f"r={r}: virial error = {result['virial_relative_error']}"

    def test_virial_squeezed_vacuum(self):
        state = SqueezedCoherentState(alpha=0.0, r=1.5)
        result = VirialTheoremQHO.verify_for_squeezed_state(state)
        assert result["virial_holds"]

    def test_virial_fock_states(self):
        for n in [0, 1, 5, 50]:
            result = VirialTheoremQHO.verify_for_fock_state(n)
            assert result["w"] == 0.0
            assert result["pressure_amplitude"] == 0.0

    def test_virial_thermal_states(self):
        for n_bar in [0.01, 1.0, 100.0]:
            result = VirialTheoremQHO.verify_for_thermal_state(n_bar)
            assert result["w"] == 0.0

    def test_general_proof_structure(self):
        proof = VirialTheoremQHO.general_proof_summary()
        assert "PROVEN" in proof["evidence_tier"]
        assert proof["scope"].startswith("ALL")


# ---------------------------------------------------------------------------
# 5. Energy density increases with squeezing
# ---------------------------------------------------------------------------
class TestEnergyDensityIncrease:
    """Energy density grows as sinh^2(r) with squeezing."""

    def test_rho_increases_monotonically(self):
        """rho must increase with r"""
        edc = EnergyDensityComparison()
        r_values = np.linspace(0, 3, 100)
        rho_values = np.array([edc.rho_squeezed(r) for r in r_values])
        assert np.all(np.diff(rho_values) > 0), "Energy density must increase with r"

    def test_rho_ratio_formula(self):
        """rho_squeezed/rho_coherent = 1 + sinh^2(r)/(|alpha|^2 + 1/2)"""
        edc = EnergyDensityComparison(alpha_sq=0.5)
        for r in [0.5, 1.0, 2.0]:
            ratio = edc.energy_ratio(r)
            expected = 1.0 + np.sinh(r) ** 2 / (0.5 + 0.5)
            assert abs(ratio - expected) / expected < 1e-12

    def test_extra_energy_from_squeezing(self):
        """Delta_rho = hbar*omega*sinh^2(r)"""
        edc = EnergyDensityComparison()
        for r in [0.5, 1.0, 2.0]:
            delta = edc.extra_energy_from_squeezing(r)
            expected = HBAR * edc.omega * np.sinh(r) ** 2
            assert abs(delta - expected) / expected < 1e-12

    def test_r0_ratio_is_one(self):
        """At r=0, squeezed = coherent"""
        edc = EnergyDensityComparison()
        assert abs(edc.energy_ratio(0.0) - 1.0) < 1e-15

    def test_large_r_exponential_growth(self):
        """For large r, rho ~ (1/4)*e^{2r} * hbar*omega"""
        edc = EnergyDensityComparison(alpha_sq=0.5)
        r = 5.0
        ratio = edc.energy_ratio(r)
        approx = np.sinh(r) ** 2 / 1.0  # alpha_sq + 0.5 = 1.0
        # sinh(r)^2 ~ (1/4)*e^{2r} for large r
        assert ratio > 1000, f"Should grow exponentially, got ratio={ratio}"


# ---------------------------------------------------------------------------
# 6. Time-averaged pressure vanishes for all r
# ---------------------------------------------------------------------------
class TestPressureVanishes:
    """The time-averaged pressure is zero for all squeezing parameters."""

    @pytest.mark.parametrize("r", [0.0, 0.5, 1.0, 2.0, 3.0])
    def test_pressure_time_average_zero(self, r):
        """<p>_t = 0"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=r)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=500)
        p_avg = np.mean(se.pressure(t))
        rho_avg = np.mean(se.energy_density(t))
        relative = abs(p_avg) / rho_avg
        assert relative < 1e-5, f"r={r}: |<p>|/rho = {relative}"

    def test_pressure_analytic_matches_direct(self):
        """Analytic pressure formula matches direct computation"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=1.0)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=10, pts_per_period=10000)
        p_direct = se.pressure(t)
        p_analytic = se.pressure_analytic(t)
        scale = se.pressure_amplitude()
        if scale > 0:
            max_error = np.max(np.abs(p_direct - p_analytic)) / scale
            assert max_error < 1e-10, f"Pressure mismatch: max relative error = {max_error}"

    def test_pressure_oscillates_but_averages_zero(self):
        """Pressure oscillates at 2*omega but time-averages to zero"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=1.5)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=10, pts_per_period=10000)
        p = se.pressure(t)

        # Should oscillate (nonzero amplitude)
        assert np.max(np.abs(p)) > 0, "Pressure should oscillate"

        # But average to zero
        t_long = make_time_array(se, n_periods=500)
        p_long = se.pressure(t_long)
        assert abs(np.mean(p_long)) / np.max(np.abs(p)) < 1e-4

    def test_energy_density_time_independent(self):
        """rho(t) should be constant (oscillating parts cancel)"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=1.0)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=10, pts_per_period=10000)
        rho = se.energy_density(t)
        relative_variation = np.std(rho) / np.mean(rho)
        assert relative_variation < 1e-10, f"rho varies by {relative_variation}"


# ---------------------------------------------------------------------------
# 7. Numerical verification by explicit time integration
# ---------------------------------------------------------------------------
class TestNumericalIntegration:
    """Brute-force numerical verification with high resolution."""

    def test_numerical_w_coherent(self):
        """Numerical w for coherent state"""
        result = NumericalVerification.compute_w_numerical(
            alpha=np.sqrt(0.5), r=0.0, n_periods=500
        )
        assert abs(result["w"]) < 1e-5

    def test_numerical_w_squeezed(self):
        """Numerical w for squeezed state"""
        result = NumericalVerification.compute_w_numerical(
            alpha=np.sqrt(0.5), r=1.5, n_periods=500
        )
        assert abs(result["w"]) < 1e-4

    def test_numerical_w_large_squeeze(self):
        """Numerical w for large squeezing"""
        result = NumericalVerification.compute_w_numerical(
            alpha=np.sqrt(0.5), r=3.0, n_periods=500
        )
        assert abs(result["w"]) < 1e-3  # Larger tolerance for large r (bigger oscillations)

    def test_numerical_sweep(self):
        """Sweep over r: all w should be zero"""
        r_values = np.linspace(0, 2, 11)
        result = NumericalVerification.sweep_squeezing_parameter(
            r_values=r_values, n_periods=300
        )
        assert result["all_w_zero"], f"max |w| = {result['max_|w|']}"
        assert result["rho_increases_with_r"]

    def test_rho_matches_analytic(self):
        """Numerical rho matches analytic formula"""
        for r in [0.0, 0.5, 1.0, 2.0]:
            result = NumericalVerification.compute_w_numerical(
                alpha=np.sqrt(0.5), r=r, n_periods=200
            )
            rel_error = abs(result["rho_avg"] - result["rho_analytic"]) / result["rho_analytic"]
            assert rel_error < 1e-8, f"r={r}: rho mismatch = {rel_error}"

    def test_energy_time_independence(self):
        """Energy density should not vary in time"""
        for r in [0.0, 1.0, 2.0]:
            result = NumericalVerification.compute_w_numerical(
                alpha=np.sqrt(0.5), r=r, n_periods=200
            )
            assert result["rho_relative_variation"] < 1e-10, \
                f"r={r}: rho variation = {result['rho_relative_variation']}"


# ---------------------------------------------------------------------------
# 8. Uncertainty relations
# ---------------------------------------------------------------------------
class TestUncertaintyRelations:
    """Squeezed states preserve minimum uncertainty."""

    @pytest.mark.parametrize("r", [0.0, 0.5, 1.0, 2.0, 5.0])
    def test_minimum_uncertainty_preserved(self, r):
        su = SqueezedUncertainty(r=r)
        result = su.verify_minimum_uncertainty()
        assert result["is_minimum_uncertainty"], \
            f"r={r}: relative error = {result['relative_error']}"

    def test_phi_squeezed_pi_stretched(self):
        """For r>0: Delta_phi decreases, Delta_pi increases"""
        su_0 = SqueezedUncertainty(r=0.0)
        su_1 = SqueezedUncertainty(r=1.0)
        assert su_1.delta_phi() < su_0.delta_phi()
        assert su_1.delta_pi() > su_0.delta_pi()

    def test_squeeze_ratios(self):
        """Delta_phi(r)/Delta_phi(0) = e^{-r}"""
        for r in [0.5, 1.0, 2.0]:
            su = SqueezedUncertainty(r=r)
            su0 = SqueezedUncertainty(r=0.0)
            ratio = su.delta_phi() / su0.delta_phi()
            assert abs(ratio - np.exp(-r)) < 1e-12


# ---------------------------------------------------------------------------
# 9. Edge cases and consistency
# ---------------------------------------------------------------------------
class TestEdgeCases:
    """Edge cases and consistency checks."""

    def test_vacuum_state_energy(self):
        """Unsqueezed vacuum |0>: rho = hbar*omega/2"""
        state = SqueezedCoherentState(alpha=0.0, r=0.0)
        se = SqueezedStressEnergy(state=state)
        rho = se.energy_density_analytic()
        expected = HBAR * se.omega * 0.5
        assert abs(rho - expected) / expected < 1e-15

    def test_w_analytic_always_zero(self):
        """The analytic w is always exactly 0"""
        state = SqueezedCoherentState(alpha=5.0 + 3j, r=2.5, theta=1.7)
        se = SqueezedStressEnergy(state=state)
        assert se.w_analytic() == 0.0

    def test_phi_squared_positive(self):
        """<phi^2(t)> must be positive for all t"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=2.0)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=10, pts_per_period=10000)
        phi2 = se.phi_squared(t)
        assert np.all(phi2 > 0), "phi^2 must be positive"

    def test_pi_squared_positive(self):
        """<pi^2(t)> must be positive for all t"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=2.0)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=10, pts_per_period=10000)
        pi2 = se.pi_squared(t)
        assert np.all(pi2 > 0), "pi^2 must be positive"

    def test_pressure_bounded(self):
        """| p(t) | <= rho for all t (energy conditions)"""
        state = SqueezedCoherentState(alpha=np.sqrt(0.5), r=1.5)
        se = SqueezedStressEnergy(state=state)
        t = make_time_array(se, n_periods=10, pts_per_period=10000)
        p = se.pressure(t)
        rho = se.energy_density(t)
        # p oscillates between -rho and +rho for the QHO
        assert np.all(np.abs(p) <= rho * (1 + 1e-10)), \
            "|p| > rho violates dominant energy condition"

    def test_symmetry_r_negative(self):
        """S(-r) is equivalent to squeezing in the conjugate direction.
        Physics (w, rho) should be the same as S(r) with theta shifted."""
        state_pos = SqueezedCoherentState(alpha=np.sqrt(0.5), r=1.0, theta=0.0)
        state_neg = SqueezedCoherentState(alpha=np.sqrt(0.5), r=-1.0, theta=0.0)
        # sinh^2(r) = sinh^2(-r), so energy density is the same
        se_pos = SqueezedStressEnergy(state=state_pos)
        se_neg = SqueezedStressEnergy(state=state_neg)
        assert abs(se_pos.energy_density_analytic() - se_neg.energy_density_analytic()) < 1e-20

    def test_state_catalog_completeness(self):
        """Catalog should cover major state types"""
        catalog = WZeroUniversality.catalog_of_states()
        required_states = ["coherent", "squeezed", "Fock", "thermal", "arbitrary"]
        for state_name in required_states:
            found = any(state_name.lower() in key.lower() for key in catalog.keys())
            assert found, f"Missing state type: {state_name}"
        # All should have w=0
        for key, val in catalog.items():
            assert val["w"] == 0, f"{key} has w={val['w']}"

    def test_what_breaks_w_zero_nonempty(self):
        """Should list conditions that break w=0"""
        breaks = WZeroUniversality.what_breaks_w_zero()
        assert len(breaks) >= 3, "Should list multiple mechanisms"

    def test_full_analysis_runs(self):
        """Smoke test: full analysis completes without error"""
        results = compute_full_analysis(
            r_values=np.array([0.0, 0.5, 1.0])
        )
        assert "virial_verification" in results
        assert "numerical_sweep" in results
        assert results["numerical_sweep"]["all_w_zero"]


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
