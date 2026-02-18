"""
Comprehensive tests for the 4D spacetime cell vacuum construction.

Tests verify all four approaches (phase-randomized, temporal Casimir,
cosmological, Euclidean path integral) and confirm the central result:
w = 0 regardless of temporal cellularization.
"""

import numpy as np
import pytest
from spacetime_cell_vacuum import (
    PhaseRandomizedState,
    TemporalCasimir,
    CosmologicalTemporalCell,
    EuclideanPathIntegral,
    FourDimensionalCell,
    TemporalCellComparison,
    NegativePressureAnalysis,
    run_full_analysis,
    HBAR, C, G, K_B, EV_TO_J, H0_SI,
    M_NEUTRINO, M_ELECTRON,
)


# ===========================================================================
# 1. Phase-Randomized State Tests
# ===========================================================================
class TestPhaseRandomizedState:

    def test_poisson_weights_normalization(self):
        """Poisson weights sum to 1."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        norm = pr.verify_normalization(n_max=50)
        assert abs(norm - 1.0) < 1e-12, f"Normalization = {norm}, expected 1"

    def test_poisson_weights_normalization_various_alpha(self):
        """Normalization holds for various alpha^2 values."""
        for a2 in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
            pr = PhaseRandomizedState(alpha_squared=a2)
            norm = pr.verify_normalization(n_max=100)
            assert abs(norm - 1.0) < 1e-10, (
                f"Normalization = {norm} for alpha^2 = {a2}"
            )

    def test_poisson_P0(self):
        """P(0) = e^{-1/2} for alpha^2 = 1/2."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        P0 = pr.poisson_weight(0)
        expected = np.exp(-0.5)
        assert abs(P0 - expected) < 1e-14, f"P(0) = {P0}, expected {expected}"

    def test_poisson_P1(self):
        """P(1) = e^{-1/2} * 1/2 for alpha^2 = 1/2."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        P1 = pr.poisson_weight(1)
        expected = np.exp(-0.5) * 0.5
        assert abs(P1 - expected) < 1e-14

    def test_poisson_P2(self):
        """P(2) = e^{-1/2} * (1/2)^2 / 2! for alpha^2 = 1/2."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        P2 = pr.poisson_weight(2)
        expected = np.exp(-0.5) * 0.25 / 2
        assert abs(P2 - expected) < 1e-14

    def test_mean_occupation_equals_alpha_squared(self):
        """<n> = |alpha|^2."""
        for a2 in [0.1, 0.5, 1.0, 3.0]:
            pr = PhaseRandomizedState(alpha_squared=a2)
            mean_n = pr.mean_occupation(n_max=100)
            assert abs(mean_n - a2) < 1e-8, (
                f"<n> = {mean_n}, expected {a2}"
            )

    def test_entropy_positive(self):
        """Von Neumann entropy is positive for mixed state."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        S = pr.von_neumann_entropy()
        assert S > 0, f"Entropy = {S}, should be positive for mixed state"

    def test_entropy_increases_with_alpha(self):
        """Entropy increases with |alpha|^2 (more spread in Fock space)."""
        entropies = []
        for a2 in [0.1, 0.5, 1.0, 2.0, 5.0]:
            pr = PhaseRandomizedState(alpha_squared=a2)
            entropies.append(pr.von_neumann_entropy())
        for i in range(len(entropies) - 1):
            assert entropies[i] < entropies[i + 1], (
                f"Entropy not monotonically increasing: {entropies}"
            )

    def test_entropy_value_alpha_half(self):
        """Check specific entropy value for alpha^2 = 1/2."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        S = pr.von_neumann_entropy()
        # Compute expected: -sum P(n) ln P(n)
        # P(0) ~ 0.6065, P(1) ~ 0.3033, P(2) ~ 0.0758, ...
        weights = pr.poisson_weights(50)
        expected = -np.sum(weights[weights > 0] * np.log(weights[weights > 0]))
        assert abs(S - expected) < 1e-12

    def test_fock_state_w_zero(self):
        """w = 0 for every Fock state."""
        pr = PhaseRandomizedState()
        for n in range(20):
            assert pr.fock_state_w(n) == 0.0

    def test_equation_of_state_w_zero(self):
        """w = 0 for the phase-randomized state."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        assert pr.equation_of_state_w() == 0.0

    def test_equation_of_state_w_zero_any_alpha(self):
        """w = 0 regardless of alpha^2."""
        for a2 in [0.01, 0.1, 0.5, 1.0, 10.0, 100.0]:
            pr = PhaseRandomizedState(alpha_squared=a2)
            assert pr.equation_of_state_w() == 0.0

    def test_stress_energy_pressure_zero(self):
        """Pressure is zero for the mixed state."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        result = pr.stress_energy_mixed_state(M_NEUTRINO)
        assert result["pressure"] == 0.0
        assert result["w"] == 0.0

    def test_stress_energy_energy_positive(self):
        """Energy density is positive."""
        pr = PhaseRandomizedState(alpha_squared=0.5)
        result = pr.stress_energy_mixed_state(M_NEUTRINO)
        assert result["energy_density"] > 0

    def test_energy_density_matches_coherent_state(self):
        """
        Time-averaged energy density equals coherent state energy density.
        Time-averaging does NOT change the mean energy.
        """
        pr = PhaseRandomizedState(alpha_squared=0.5)
        mass = M_NEUTRINO
        omega = mass * C**2 / HBAR
        lambda_C = HBAR / (mass * C)
        V_cell = lambda_C**3

        # Coherent state energy density
        E_coh = HBAR * omega * (0.5 + 0.5)  # |alpha|^2 + 1/2 = 1
        rho_coh = E_coh / V_cell

        # Phase-randomized energy density
        rho_avg = pr.energy_density_per_cell(mass)

        assert abs(rho_avg - rho_coh) / rho_coh < 1e-12


# ===========================================================================
# 2. Temporal Casimir Effect Tests
# ===========================================================================
class TestTemporalCasimir:

    def test_compton_frequency(self):
        """omega_C = mc^2/hbar."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        expected = M_ELECTRON * C**2 / HBAR
        assert abs(tc.omega_compton - expected) / expected < 1e-14

    def test_compton_period(self):
        """tau_C = 2*pi/omega."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        expected = 2 * np.pi / tc.omega_compton
        assert abs(tc.tau_compton - expected) / expected < 1e-14

    def test_temporal_mode_spacing_matches_qho(self):
        """Temporal mode spacing equals QHO level spacing."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        result = tc.temporal_modes_match_qho(n_max=20)
        assert result["spacing_match"], "Mode spacings should match"

    def test_temporal_mode_spacing_value(self):
        """Spacing = hbar*omega."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        result = tc.temporal_modes_match_qho()
        expected = HBAR * tc.omega_compton
        assert abs(result["spacing_value"] - expected) / expected < 1e-14

    def test_temporal_E0_is_zero(self):
        """Temporal construction gives E_0 = 0 (no zero-point)."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        result = tc.temporal_modes_match_qho()
        assert result["temporal_E0"] == 0.0

    def test_qho_E0_is_half_hbar_omega(self):
        """QHO gives E_0 = hbar*omega/2."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        result = tc.temporal_modes_match_qho()
        expected = HBAR * tc.omega_compton / 2
        assert abs(result["qho_E0"] - expected) / expected < 1e-14

    def test_spatial_casimir_negative(self):
        """Spatial Casimir energy is negative."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        rho = tc.spatial_casimir_energy_density(tc.lambda_compton)
        assert rho < 0

    def test_temporal_casimir_negative(self):
        """Temporal Casimir energy (by analogy) is negative."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        result = tc.temporal_casimir_at_compton()
        assert result["temporal_casimir_negative"]

    def test_temporal_casimir_small_fraction(self):
        """Temporal Casimir energy is a small fraction of cell energy."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        result = tc.temporal_casimir_at_compton()
        assert abs(result["ratio"]) < 0.01, (
            f"Ratio = {result['ratio']}, should be << 1"
        )

    def test_spatial_casimir_formula(self):
        """Verify Casimir formula: rho = -pi^2 hbar c / (720 L^4)."""
        tc = TemporalCasimir(mass=M_ELECTRON)
        L = 1e-6  # 1 micron
        rho = tc.spatial_casimir_energy_density(L)
        expected = -np.pi**2 * HBAR * C / (720 * L**4)
        assert abs(rho - expected) / abs(expected) < 1e-14


# ===========================================================================
# 3. Cosmological Temporal Cell Tests
# ===========================================================================
class TestCosmologicalTemporalCell:

    def test_gibbons_hawking_temperature(self):
        """T_GH = hbar*H/(2*pi*k_B)."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        T_GH = ctc.gibbons_hawking_temperature()
        expected = HBAR * H0_SI / (2 * np.pi * K_B)
        assert abs(T_GH - expected) / expected < 1e-14
        # Order of magnitude: ~10^{-30} K
        assert 1e-31 < T_GH < 1e-29

    def test_compton_temperature(self):
        """T_C = mc^2/(2*pi*k_B)."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        T_C = ctc.compton_temperature()
        expected = M_NEUTRINO * C**2 / (2 * np.pi * K_B)
        assert abs(T_C - expected) / expected < 1e-14

    def test_temperature_ratio_tiny(self):
        """T_GH/T_C = H/omega_C << 1."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        ratio = ctc.temperature_ratio()
        assert ratio < 1e-25, f"Ratio = {ratio}, should be << 1"

    def test_parker_creation_zero(self):
        """Parker creation rate is effectively zero for m >> H."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        rate = ctc.parker_creation_rate()
        assert rate == 0.0, "Parker rate should be zero (exponentially suppressed)"

    def test_parker_energy_zero(self):
        """Parker energy density is zero."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        rho = ctc.parker_energy_density()
        assert rho == 0.0

    def test_GH_energy_tiny(self):
        """Gibbons-Hawking energy density is negligibly small."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        rho_GH = ctc.gibbons_hawking_energy_density()
        rho_DE = ctc.observed_dark_energy_density()
        assert rho_GH < rho_DE * 1e-100, (
            f"rho_GH = {rho_GH}, should be << rho_DE = {rho_DE}"
        )

    def test_dark_energy_density_order(self):
        """Observed dark energy density ~ 5e-10 J/m^3."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        rho_DE = ctc.observed_dark_energy_density()
        assert 1e-10 < rho_DE < 1e-9

    def test_cosmological_casimir_tiny(self):
        """Temporal Casimir at Hubble scale is negligibly small."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        result = ctc.cosmological_temporal_casimir()
        assert not result["is_correct_order"]
        ratio = result["ratio"]
        assert ratio < 1e-100, f"Ratio = {ratio}, should be << 1"

    def test_compare_energy_scales(self):
        """Full comparison runs and has correct ordering."""
        ctc = CosmologicalTemporalCell(mass=M_NEUTRINO)
        result = ctc.compare_energy_scales()
        assert result["rho_cell_vacuum"] > 0
        assert result["rho_gibbons_hawking"] > 0
        assert result["rho_parker"] == 0.0
        assert result["rho_dark_energy_observed"] > 0


# ===========================================================================
# 4. Euclidean Path Integral Tests
# ===========================================================================
class TestEuclideanPathIntegral:

    def test_compton_temperature(self):
        """T_compton = hbar*omega/(2*pi*k_B)."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        T = epi.T_compton
        expected = HBAR * epi.omega / (2 * np.pi * K_B)
        assert abs(T - expected) / expected < 1e-14

    def test_beta_compton(self):
        """beta = 2*pi/omega."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        expected = 2 * np.pi / epi.omega
        assert abs(epi.beta_compton - expected) / expected < 1e-14

    def test_free_energy_below_zero_point(self):
        """Free energy < zero-point energy (thermal correction is negative)."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        F = epi.qho_free_energy(epi.T_compton)
        E0 = HBAR * epi.omega / 2
        assert F < E0, "Free energy should be less than zero-point energy"

    def test_thermal_energy_above_zero_point(self):
        """Thermal energy > zero-point energy."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        E = epi.qho_energy_thermal(epi.T_compton)
        E0 = HBAR * epi.omega / 2
        assert E > E0, "Thermal energy should exceed zero-point"

    def test_bose_einstein_at_compton_temp(self):
        """n_BE = 1/(e^{2*pi} - 1) at Compton temperature."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        result = epi.free_energy_at_compton_temperature()
        expected_nBE = 1.0 / (np.exp(2 * np.pi) - 1)
        assert abs(result["bose_einstein_occupation"] - expected_nBE) < 1e-10

    def test_thermal_correction_small(self):
        """Thermal correction at Compton T is << 1."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        result = epi.free_energy_at_compton_temperature()
        assert abs(result["relative_correction"]) < 0.01

    def test_pressure_zero_at_compton_temp(self):
        """Pressure = 0 even at Compton temperature."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        p = epi.qho_pressure_thermal(epi.T_compton)
        assert p == 0.0

    def test_w_zero_at_any_temperature(self):
        """w = 0 at ANY temperature."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        for T in [1e-10, 1.0, 1e5, 1e10, 1e20]:
            w = epi.w_at_any_temperature(T)
            assert w == 0.0, f"w = {w} at T = {T}, expected 0"

    def test_high_temperature_limit(self):
        """High temperature limit gives correct properties."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        result = epi.high_temperature_limit()
        assert result["high_T_w"] == 0.0
        assert result["low_T_w"] == 0.0
        assert result["all_T_w"] == 0.0

    def test_free_energy_low_T_limit(self):
        """At very low T, free energy -> hbar*omega/2."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        T_low = 1e-30  # Extremely cold
        F = epi.qho_free_energy(T_low)
        E0 = HBAR * epi.omega / 2
        assert abs(F - E0) / E0 < 1e-10

    def test_energy_high_T_classical(self):
        """At very high T, energy -> k_B*T (classical equipartition)."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        T_high = 1e30  # Extremely hot
        E = epi.qho_energy_thermal(T_high)
        expected = K_B * T_high  # Classical limit
        # Should agree to within hbar*omega/2 (zero-point correction)
        assert abs(E - expected) / expected < 0.01


# ===========================================================================
# 5. 4D Cell Volume Tests
# ===========================================================================
class TestFourDimensionalCell:

    def test_lambda_C(self):
        """lambda_C = hbar/(mc)."""
        fdc = FourDimensionalCell(mass=M_ELECTRON)
        expected = HBAR / (M_ELECTRON * C)
        assert abs(fdc.lambda_C - expected) / expected < 1e-14

    def test_tau_C(self):
        """tau_C = 2*pi*hbar/(mc^2)."""
        fdc = FourDimensionalCell(mass=M_ELECTRON)
        expected = 2 * np.pi * HBAR / (M_ELECTRON * C**2)
        assert abs(fdc.tau_C - expected) / expected < 1e-14

    def test_V4D_over_lambda4(self):
        """V_4D / lambda_C^4 = 2*pi."""
        fdc = FourDimensionalCell(mass=M_ELECTRON)
        ratio = fdc.V_4D_in_lambda_units
        assert abs(ratio - 2 * np.pi) < 1e-10, (
            f"V_4D/lambda^4 = {ratio}, expected 2*pi"
        )

    def test_action_per_cell_is_h(self):
        """
        Action per 4D cell = h (Planck constant) for |alpha|^2 = 1/2.

        S = E * tau_C = hbar*omega * (2*pi/omega) = 2*pi*hbar = h
        """
        fdc = FourDimensionalCell(mass=M_ELECTRON)
        S = fdc.action_per_4D_cell(alpha_squared=0.5)
        h = 2 * np.pi * HBAR
        assert abs(S - h) / h < 1e-12, (
            f"Action = {S}, expected h = {h}"
        )

    def test_action_over_hbar_is_2pi(self):
        """S/hbar = 2*pi for |alpha|^2 = 1/2."""
        fdc = FourDimensionalCell(mass=M_ELECTRON)
        ratio = fdc.action_in_hbar_units(alpha_squared=0.5)
        assert abs(ratio - 2 * np.pi) < 1e-12

    def test_action_mass_independent(self):
        """The action S = h is independent of mass (for |alpha|^2 = 1/2)."""
        h = 2 * np.pi * HBAR
        for mass in [M_NEUTRINO, M_ELECTRON, 1e-20, 1e-30]:
            fdc = FourDimensionalCell(mass=mass)
            S = fdc.action_per_4D_cell(alpha_squared=0.5)
            assert abs(S - h) / h < 1e-10, (
                f"Action = {S} for mass = {mass}, expected h = {h}"
            )

    def test_w_3D_zero(self):
        """3D cell gives w = 0."""
        fdc = FourDimensionalCell(mass=M_ELECTRON)
        result = fdc.compare_3D_vs_4D()
        assert result["w_3D_cell"] == 0.0

    def test_w_4D_zero(self):
        """4D cell gives w = 0."""
        fdc = FourDimensionalCell(mass=M_ELECTRON)
        result = fdc.compare_3D_vs_4D()
        assert result["w_4D_cell"] == 0.0


# ===========================================================================
# 6. Temporal Cell Size Comparison Tests
# ===========================================================================
class TestTemporalCellComparison:

    def test_compton_n_BE(self):
        """n_BE at Compton period = 1/(e^{2*pi} - 1)."""
        tcc = TemporalCellComparison(mass=M_ELECTRON)
        n_BE = tcc.bose_einstein_n(tcc.tau_compton)
        expected = 1.0 / (np.exp(2 * np.pi) - 1)
        assert abs(n_BE - expected) / expected < 1e-10

    def test_hubble_n_BE_zero(self):
        """n_BE at Hubble time is effectively zero."""
        tcc = TemporalCellComparison(mass=M_ELECTRON)
        n_BE = tcc.bose_einstein_n(tcc.tau_hubble)
        assert n_BE == 0.0 or n_BE < 1e-300

    def test_planck_n_BE_large(self):
        """n_BE at Planck time is large (high-T limit)."""
        tcc = TemporalCellComparison(mass=M_ELECTRON)
        n_BE = tcc.bose_einstein_n(tcc.tau_planck)
        assert n_BE > 1, f"n_BE = {n_BE}, should be >> 1 at Planck scale"

    def test_all_scales_w_zero(self):
        """w = 0 at all temporal cell scales."""
        tcc = TemporalCellComparison(mass=M_ELECTRON)
        results = tcc.compare_all_scales()
        for name in ["compton", "planck", "hubble"]:
            assert results[name]["w"] == 0.0, (
                f"w = {results[name]['w']} at {name} scale, expected 0"
            )

    def test_all_give_w_zero_flag(self):
        """Summary flag confirms all scales give w = 0."""
        tcc = TemporalCellComparison(mass=M_ELECTRON)
        results = tcc.compare_all_scales()
        assert results["summary"]["all_give_w_zero"]

    def test_effective_temperature_compton(self):
        """T at Compton period = mc^2/(2*pi*k_B)."""
        tcc = TemporalCellComparison(mass=M_ELECTRON)
        T = tcc.effective_temperature(tcc.tau_compton)
        expected = HBAR / (K_B * tcc.tau_compton)
        assert abs(T - expected) / expected < 1e-14


# ===========================================================================
# 7. Negative Pressure Analysis Tests
# ===========================================================================
class TestNegativePressureAnalysis:

    def test_virial_theorem_proven(self):
        """Virial theorem proof is at PROVEN tier."""
        result = NegativePressureAnalysis.virial_theorem_proof()
        assert result["evidence_tier"] == "PROVEN"

    def test_virial_independence(self):
        """Virial theorem is independent of temperature, etc."""
        result = NegativePressureAnalysis.virial_theorem_proof()
        assert len(result["independence"]) >= 4

    def test_loopholes_analyzed(self):
        """All loopholes are analyzed."""
        result = NegativePressureAnalysis.loophole_analysis()
        assert "loophole_1_spatial_casimir" in result
        assert "loophole_2_temporal_casimir" in result
        assert "loophole_3_cell_interactions" in result
        assert "loophole_4_curved_spacetime" in result
        assert "loophole_5_non_equilibrium" in result

    def test_spatial_casimir_can_be_negative(self):
        """Spatial Casimir CAN give negative pressure (but not from temporal)."""
        result = NegativePressureAnalysis.loophole_analysis()
        assert result["loophole_1_spatial_casimir"]["can_give_w_negative"] is True
        assert result["loophole_1_spatial_casimir"]["relevant_to_4D_cell"] is False

    def test_overall_conclusion_negative(self):
        """Overall: no known mechanism gives w < 0 from 4D cells."""
        result = NegativePressureAnalysis.loophole_analysis()
        assert "No known mechanism" in result["overall_conclusion"]


# ===========================================================================
# 8. Integration / Full Analysis Tests
# ===========================================================================
class TestFullAnalysis:

    def test_full_analysis_runs(self):
        """Full analysis completes without error."""
        results = run_full_analysis(mass=M_NEUTRINO)
        assert "phase_randomized" in results
        assert "temporal_casimir" in results
        assert "cosmological" in results
        assert "euclidean" in results
        assert "4d_cell" in results
        assert "temporal_comparison" in results
        assert "negative_pressure" in results
        assert "loopholes" in results

    def test_all_approaches_give_w_zero(self):
        """Every approach gives w = 0."""
        results = run_full_analysis(mass=M_NEUTRINO)

        assert results["phase_randomized"]["w"] == 0.0
        assert results["euclidean"]["w"] == 0.0
        assert results["4d_cell"]["w_3D_cell"] == 0.0
        assert results["4d_cell"]["w_4D_cell"] == 0.0

    def test_no_approach_gives_w_minus_one(self):
        """No approach gives w = -1."""
        results = run_full_analysis(mass=M_NEUTRINO)

        assert results["phase_randomized"]["w"] != -1.0
        assert results["euclidean"]["w"] != -1.0
        assert results["4d_cell"]["w_4D_cell"] != -1.0

    def test_phase_randomized_entropy_positive(self):
        """Phase-randomized state has positive entropy."""
        results = run_full_analysis(mass=M_NEUTRINO)
        assert results["phase_randomized"]["von_neumann_entropy"] > 0

    def test_temporal_casimir_tiny(self):
        """Temporal Casimir is a tiny fraction of cell energy."""
        results = run_full_analysis(mass=M_NEUTRINO)
        ratio = results["temporal_casimir"]["ratio"]
        assert abs(ratio) < 0.01


# ===========================================================================
# 9. Numerical Stability Tests
# ===========================================================================
class TestNumericalStability:

    def test_poisson_large_alpha(self):
        """Poisson weights are well-behaved for large alpha^2."""
        pr = PhaseRandomizedState(alpha_squared=50.0)
        norm = pr.verify_normalization(n_max=200)
        assert abs(norm - 1.0) < 1e-6

    def test_poisson_small_alpha(self):
        """Poisson weights are well-behaved for small alpha^2."""
        pr = PhaseRandomizedState(alpha_squared=0.001)
        norm = pr.verify_normalization(n_max=20)
        assert abs(norm - 1.0) < 1e-12

    def test_bose_einstein_large_x(self):
        """n_BE handles very large x (low T) without overflow."""
        tcc = TemporalCellComparison(mass=M_ELECTRON)
        # Very large tau -> very low T -> x very large
        n_BE = tcc.bose_einstein_n(1e30)
        assert n_BE == 0.0 or np.isfinite(n_BE)

    def test_bose_einstein_small_x(self):
        """n_BE handles very small x (high T) correctly."""
        tcc = TemporalCellComparison(mass=M_ELECTRON)
        n_BE = tcc.bose_einstein_n(1e-50)
        assert np.isfinite(n_BE)
        assert n_BE > 0

    def test_free_energy_extreme_temperatures(self):
        """Free energy is well-behaved at extreme temperatures."""
        epi = EuclideanPathIntegral(mass=M_ELECTRON)
        # Very low T
        F_low = epi.qho_free_energy(1e-30)
        assert np.isfinite(F_low)
        # Very high T
        F_high = epi.qho_free_energy(1e30)
        assert np.isfinite(F_high)

    def test_parker_rate_underflow_handled(self):
        """Parker creation rate handles extreme underflow."""
        ctc = CosmologicalTemporalCell(mass=M_ELECTRON)
        rate = ctc.parker_creation_rate()
        assert np.isfinite(rate) or rate == 0.0

    def test_energy_density_different_masses(self):
        """Energy density computed correctly for range of masses."""
        for mass in [1e-35, 1e-30, 1e-25, M_ELECTRON]:
            pr = PhaseRandomizedState(alpha_squared=0.5)
            rho = pr.energy_density_per_cell(mass)
            assert np.isfinite(rho)
            assert rho > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
