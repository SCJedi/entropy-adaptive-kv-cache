"""
Comprehensive tests for the Temporal Coherence Cost module.

Tests verify:
- Per-mode stationarity cost (zero-point energy)
- Mode sum with cutoff gives expected scaling
- Renormalized coherence cost properties
- Holographic formula reproduces critical density
- Margolus-Levitin bound computed correctly
- Information excess computed correctly
- All energy densities are physical (positive, finite)
- Dimensional analysis checks
- Comparison with observed dark energy density
"""

import numpy as np
import pytest
from temporal_coherence import (
    # Constants
    HBAR, C, G, EV_TO_J, H0_SI, HUBBLE_TIME, HUBBLE_LENGTH,
    PLANCK_LENGTH, PLANCK_MASS, PLANCK_ENERGY,
    RHO_DE_OBSERVED, RHO_CRIT, M_NU1_KG, M_NU1_EV,
    # Classes
    PerModeStationarityCost,
    FullFieldModeSumCost,
    RenormalizedCoherenceCost,
    HolographicDarkEnergy,
    MargolusLevitinBound,
    VacuumPersistenceAmplitude,
    InformationExcess,
    ScaleAnalysis,
    compute_all_densities,
)


# ===========================================================================
# Constants sanity checks
# ===========================================================================
class TestConstants:
    """Verify physical constants are reasonable."""

    def test_hbar_value(self):
        assert 1.05e-34 < HBAR < 1.06e-34

    def test_c_value(self):
        assert 2.997e8 < C < 2.998e8

    def test_G_value(self):
        assert 6.67e-11 < G < 6.68e-11

    def test_H0_value(self):
        """H0 ~ 2.2e-18 s^-1."""
        assert 2.1e-18 < H0_SI < 2.3e-18

    def test_hubble_time(self):
        """T_H ~ 4.5e17 s ~ 14 Gyr."""
        assert 4e17 < HUBBLE_TIME < 5e17

    def test_hubble_length(self):
        """L_H ~ 1.4e26 m."""
        assert 1.3e26 < HUBBLE_LENGTH < 1.5e26

    def test_planck_length(self):
        """l_P ~ 1.6e-35 m."""
        assert 1.5e-35 < PLANCK_LENGTH < 1.7e-35

    def test_rho_crit(self):
        """rho_crit ~ 8e-10 J/m^3."""
        assert 5e-10 < RHO_CRIT < 1.2e-9

    def test_rho_de_observed(self):
        assert 5e-10 < RHO_DE_OBSERVED < 7e-10

    def test_neutrino_mass(self):
        """m_nu1 ~ 2.31 meV."""
        m_eV = M_NU1_KG * C**2 / EV_TO_J
        assert abs(m_eV - 2.31e-3) / 2.31e-3 < 0.01


# ===========================================================================
# 1. Per-Mode Stationarity Cost
# ===========================================================================
class TestPerModeStationarityCost:

    @pytest.fixture
    def pmc(self):
        return PerModeStationarityCost()

    def test_zero_point_energy(self, pmc):
        """E_0 = hbar omega / 2."""
        omega = 1e12  # rad/s
        E0 = pmc.zero_point_energy(omega)
        expected = 0.5 * HBAR * omega
        assert abs(E0 - expected) / expected < 1e-15

    def test_coherent_state_energy(self, pmc):
        """E = hbar omega (|alpha|^2 + 1/2)."""
        omega = 1e12
        alpha_sq = 3.0
        E = pmc.coherent_state_energy(omega, alpha_sq)
        expected = HBAR * omega * 3.5
        assert abs(E - expected) / expected < 1e-15

    def test_stationarity_cost_equals_zpe(self, pmc):
        """Stationarity cost = zero-point energy."""
        omega = 5e15
        assert pmc.stationarity_cost(omega) == pmc.zero_point_energy(omega)

    def test_w_ground_state_is_zero(self, pmc):
        """Ground state gives w=0 (virial theorem)."""
        assert pmc.w_ground_state() == 0.0

    def test_w_coherent_state_is_zero(self, pmc):
        """Coherent state gives w=0 (virial theorem)."""
        assert pmc.w_coherent_state() == 0.0

    def test_zero_point_energy_positive(self, pmc):
        """ZPE is positive for any positive frequency."""
        for omega in [1.0, 1e10, 1e30]:
            assert pmc.zero_point_energy(omega) > 0

    def test_zero_point_scales_linearly(self, pmc):
        """E_0 is linear in omega."""
        E1 = pmc.zero_point_energy(1e12)
        E2 = pmc.zero_point_energy(2e12)
        assert abs(E2 / E1 - 2.0) < 1e-14


# ===========================================================================
# 2. Full-Field Mode Sum
# ===========================================================================
class TestFullFieldModeSum:

    def test_massless_analytic(self):
        """Massless mode sum: rho = hbar c k^4 / (16 pi^2)."""
        fms = FullFieldModeSumCost(mass_kg=0.0)
        k = 1e10  # m^-1
        rho_analytic = fms.mode_sum_density_massless_analytic(k)
        expected = HBAR * C * k**4 / (16.0 * np.pi**2)
        assert abs(rho_analytic - expected) / expected < 1e-14

    def test_massless_numeric_matches_analytic(self):
        """Numerical integration matches analytic for massless case."""
        fms = FullFieldModeSumCost(mass_kg=0.0, n_points=50000)
        k = 1e10
        rho_numeric = fms.mode_sum_density(k)
        rho_analytic = fms.mode_sum_density_massless_analytic(k)
        rel_err = abs(rho_numeric - rho_analytic) / rho_analytic
        assert rel_err < 1e-4, f"Relative error {rel_err} too large"

    def test_k4_scaling(self):
        """Mode sum scales as k^4 for massless field."""
        fms = FullFieldModeSumCost(mass_kg=0.0)
        k1 = 1e10
        k2 = 2e10
        rho1 = fms.mode_sum_density_massless_analytic(k1)
        rho2 = fms.mode_sum_density_massless_analytic(k2)
        assert abs(rho2 / rho1 - 16.0) < 1e-10  # (2)^4 = 16

    def test_compton_cutoff_order_of_magnitude(self):
        """Mode sum at Compton cutoff ~ m^4 c^5 / hbar^3 (up to factors)."""
        fms = FullFieldModeSumCost(M_NU1_KG, n_points=50000)
        rho_mode = fms.compton_cutoff_density()
        rho_cell = M_NU1_KG**4 * C**5 / HBAR**3
        # Should be within a factor (16 pi^2 ~ 158)
        ratio = rho_cell / rho_mode
        assert 10 < ratio < 500, f"Ratio cell/mode = {ratio}, expected ~158"

    def test_planck_cutoff_enormous(self):
        """Planck cutoff gives rho ~ 10^113 J/m^3."""
        fms = FullFieldModeSumCost(mass_kg=0.0)
        rho = fms.planck_cutoff_density()
        log_rho = np.log10(rho)
        assert 110 < log_rho < 115, f"log10(rho_Planck) = {log_rho}"

    def test_density_positive_definite(self):
        """Mode sum density is always positive."""
        for m in [0.0, M_NU1_KG, 9.1e-31]:
            fms = FullFieldModeSumCost(m, n_points=5000)
            k = 1e10
            assert fms.mode_sum_density(k) > 0

    def test_massive_greater_than_massless(self):
        """Massive field mode sum > massless at same cutoff."""
        fms_massive = FullFieldModeSumCost(9.1e-31, n_points=10000)
        fms_massless = FullFieldModeSumCost(0.0, n_points=10000)
        k = 1e15  # well above electron Compton
        rho_m = fms_massive.mode_sum_density(k)
        rho_0 = fms_massless.mode_sum_density(k)
        assert rho_m > rho_0


# ===========================================================================
# 3. Renormalized Coherence Cost
# ===========================================================================
class TestRenormalizedCoherenceCost:

    @pytest.fixture
    def rcc(self):
        return RenormalizedCoherenceCost(M_NU1_KG)

    def test_cell_vacuum_density(self, rcc):
        """Cell vacuum density matches m^4 c^5 / hbar^3."""
        expected = M_NU1_KG**4 * C**5 / HBAR**3
        assert abs(rcc.cell_vacuum_density() - expected) / expected < 1e-12

    def test_cell_vacuum_near_observed(self, rcc):
        """Cell vacuum density ~ observed dark energy for nu mass."""
        rho = rcc.cell_vacuum_density()
        ratio = rho / RHO_DE_OBSERVED
        assert 0.5 < ratio < 2.0, f"Ratio {ratio}, expected ~1"

    def test_mode_greater_than_zero(self, rcc):
        """Mode vacuum density (Compton cutoff) is positive."""
        assert rcc.mode_vacuum_density_compton_cutoff() > 0

    def test_ratio_mode_to_cell(self, rcc):
        """rho_mode / rho_cell ~ 1/(16 pi^2) at Compton cutoff."""
        ratio = rcc.raw_coherence_cost_ratio()
        expected = 1.0 / (16.0 * np.pi**2)  # ~ 0.00633
        # Numerical integration not exact, allow tolerance
        assert 0.001 < ratio < 0.1, f"Ratio {ratio}, expected ~{expected:.4f}"

    def test_raw_cost_negative(self, rcc):
        """
        Raw coherence cost is NEGATIVE (mode < cell at Compton cutoff).
        This means the cell vacuum has MORE energy than the mode vacuum
        when both are cut off at the same scale.
        """
        delta = rcc.raw_coherence_cost()
        assert delta < 0, f"Delta rho = {delta}, expected negative"

    def test_wald_ambiguity_restates_cc_problem(self, rcc):
        """Wald ambiguity means coherence cost is undetermined."""
        wald = rcc.wald_ambiguity_statement()
        assert "undetermined" in wald["result"].lower() or "free" in wald["implication"].lower()
        assert "RESTATES" in wald["verdict"] or "restate" in wald["verdict"].lower()


# ===========================================================================
# 4. Holographic Dark Energy
# ===========================================================================
class TestHolographicDarkEnergy:

    def test_holographic_hubble_equals_critical(self):
        """rho_holo(L=c/H0) = rho_crit exactly."""
        proof = HolographicDarkEnergy.holographic_density_equals_critical()
        assert proof["is_friedmann"]
        assert abs(proof["ratio"] - 1.0) < 1e-6

    def test_holographic_right_order_of_magnitude(self):
        """Holographic density ~ observed dark energy."""
        rho = HolographicDarkEnergy.holographic_density_hubble()
        ratio = rho / RHO_DE_OBSERVED
        assert 0.5 < ratio < 3.0, f"Ratio {ratio}, expected ~1.3"

    def test_holographic_scales_as_L_minus_2(self):
        """rho ~ 1/L^2."""
        L1 = 1e26
        L2 = 2e26
        rho1 = HolographicDarkEnergy.holographic_density(L1)
        rho2 = HolographicDarkEnergy.holographic_density(L2)
        assert abs(rho1 / rho2 - 4.0) < 1e-10

    def test_holographic_positive(self):
        """Holographic density is positive."""
        assert HolographicDarkEnergy.holographic_density(1e20) > 0

    def test_future_horizon_gives_omega_de(self):
        """Future horizon formula gives rho ~ Omega_DE * rho_crit."""
        rho_f = HolographicDarkEnergy.holographic_density_future_horizon(0.7)
        # Should be ~ 0.7 * rho_crit
        expected = 0.7 * RHO_CRIT
        ratio = rho_f / expected
        assert 0.5 < ratio < 2.0, f"Ratio {ratio}, expected ~1"

    def test_comparison_with_observed(self):
        """Comparison dictionary has correct keys."""
        comp = HolographicDarkEnergy.comparison_with_observed()
        assert "rho_holographic_hubble_J_per_m3" in comp
        assert "rho_observed_J_per_m3" in comp
        assert comp["rho_observed_J_per_m3"] == RHO_DE_OBSERVED


# ===========================================================================
# 5. Margolus-Levitin Bound
# ===========================================================================
class TestMargolusLevitinBound:

    def test_min_energy_formula(self):
        """E_min = pi hbar / (2 tau)."""
        tau = 1.0  # 1 second
        E = MargolusLevitinBound.min_energy_for_timescale(tau)
        expected = np.pi * HBAR / 2.0
        assert abs(E - expected) / expected < 1e-14

    def test_min_energy_hubble(self):
        """E_min for Hubble time is very small."""
        E = MargolusLevitinBound.min_energy_hubble_time()
        assert E > 0
        assert E < 1e-50  # very small

    def test_density_far_too_small(self):
        """ML density << observed dark energy."""
        ratio = MargolusLevitinBound.ratio_to_observed()
        assert ratio < 1e-100, f"Ratio {ratio}, should be << 1"

    def test_log10_ratio(self):
        """Log10 ratio ~ -120."""
        log_r = MargolusLevitinBound.log10_ratio_to_observed()
        assert -130 < log_r < -110, f"log10(ratio) = {log_r}"

    def test_density_analytic_matches_numeric(self):
        """Analytic and numeric (via E/V) forms agree."""
        rho_analytic = MargolusLevitinBound.min_density_analytic()
        rho_numeric = MargolusLevitinBound.min_density_hubble()
        # They differ by factors of pi etc. from sphere volume formula
        # Both should be extremely small
        assert rho_analytic > 0
        assert rho_numeric > 0
        # Same order of magnitude
        log_ratio = abs(np.log10(rho_analytic / rho_numeric))
        assert log_ratio < 2, f"Log ratio {log_ratio} too large"

    def test_density_positive(self):
        rho = MargolusLevitinBound.min_density_analytic()
        assert rho > 0


# ===========================================================================
# 6. Vacuum Persistence Amplitude
# ===========================================================================
class TestVacuumPersistenceAmplitude:

    def test_phase_rate(self):
        """Phase rate = E / hbar."""
        E = 1.0  # 1 Joule
        rate = VacuumPersistenceAmplitude.phase_accumulation_rate(E)
        assert abs(rate - 1.0 / HBAR) / (1.0 / HBAR) < 1e-14

    def test_total_phase(self):
        """Total phase = E * T / hbar."""
        E = HBAR  # so phase = T
        phase = VacuumPersistenceAmplitude.total_phase_hubble(E)
        assert abs(phase - HUBBLE_TIME) / HUBBLE_TIME < 1e-10

    def test_min_energy_one_radian(self):
        """E_min = hbar * H0."""
        E = VacuumPersistenceAmplitude.min_energy_for_one_radian()
        expected = HBAR * H0_SI
        assert abs(E - expected) / expected < 1e-14

    def test_density_too_small(self):
        """Phase density << observed."""
        ratio = VacuumPersistenceAmplitude.ratio_to_observed()
        assert ratio < 1e-100

    def test_same_scale_as_ml(self):
        """Vacuum persistence density ~ ML density (up to factors of pi)."""
        rho_phase = VacuumPersistenceAmplitude.min_density_from_phase()
        rho_ml = MargolusLevitinBound.min_density_analytic()
        log_ratio = abs(np.log10(rho_phase / rho_ml))
        assert log_ratio < 1, f"Phase and ML differ by 10^{log_ratio}"


# ===========================================================================
# 7. Information Excess
# ===========================================================================
class TestInformationExcess:

    @pytest.fixture
    def info(self):
        return InformationExcess(M_NU1_KG)

    def test_volumetric_information_positive(self, info):
        assert info.volumetric_information() > 0

    def test_holographic_information_positive(self, info):
        assert info.holographic_information() > 0

    def test_holographic_exceeds_volumetric(self, info):
        """
        For Hubble-sized region with neutrino Compton cells (lambda_C ~ 85um),
        holographic bound far exceeds volumetric info.
        The holographic bound is NOT saturated.
        """
        assert info.holographic_information() > info.volumetric_information()

    def test_information_excess_negative(self, info):
        """Information excess is negative (holographic not saturated)."""
        assert info.information_excess() < 0

    def test_information_deficit_positive(self, info):
        """Information deficit is positive."""
        assert info.information_deficit() > 0

    def test_volumetric_scaling(self):
        """I_vol scales as R^3 / lambda_C^3."""
        info1 = InformationExcess(M_NU1_KG, region_size=1e20)
        info2 = InformationExcess(M_NU1_KG, region_size=2e20)
        ratio = info2.volumetric_information() / info1.volumetric_information()
        assert abs(ratio - 8.0) < 0.01  # (2R)^3 / R^3 = 8

    def test_holographic_scaling(self):
        """I_bdy scales as R^2 / l_P^2."""
        info1 = InformationExcess(M_NU1_KG, region_size=1e20)
        info2 = InformationExcess(M_NU1_KG, region_size=2e20)
        ratio = info2.holographic_information() / info1.holographic_information()
        assert abs(ratio - 4.0) < 0.01  # (2R)^2 / R^2 = 4

    def test_energy_per_bit_hubble(self, info):
        """E_bit = hbar * H0."""
        E = info.energy_per_bit_hubble()
        assert abs(E - HBAR * H0_SI) / (HBAR * H0_SI) < 1e-14

    def test_energy_per_bit_ds(self, info):
        """E_bit(dS) = hbar H0 / (2 pi)."""
        E = info.energy_per_bit_temperature()
        expected = HBAR * H0_SI / (2.0 * np.pi)
        assert abs(E - expected) / expected < 1e-14

    def test_excess_density_is_finite(self, info):
        """Absolute excess energy density is finite and positive."""
        rho = info.excess_energy_density_ml()
        assert np.isfinite(rho)
        assert rho > 0  # uses abs(Delta_I)

    def test_information_ratio_small(self, info):
        """Volumetric info << holographic for Hubble region with nu mass."""
        ratio = info.information_ratio()
        # I_vol << I_bdy for neutrino Compton cells
        assert ratio < 1.0

    def test_excess_density_order_of_magnitude(self, info):
        """
        The excess density with ML energy per bit.
        rho_excess = (I_vol - I_bdy) * hbar*H0 / V
                   ~ (V/lambda_C^3) * hbar*H0 / V
                   = hbar * H0 / lambda_C^3

        This is ~ hbar * H0 * (mc/hbar)^3 = m^3 c^3 H0 / hbar^2
        For m = 2.31 meV:
        ~ (4.1e-39)^3 * (3e8)^3 * 2.2e-18 / (1.05e-34)^2
        Should check if this is anywhere near rho_DE.
        """
        rho = info.excess_energy_density_ml()
        # Just verify it's finite and we can compute the ratio
        ratio = rho / RHO_DE_OBSERVED
        assert np.isfinite(ratio)


# ===========================================================================
# 8. Scale Analysis
# ===========================================================================
class TestScaleAnalysis:

    def test_tau_ansatz_a_positive(self):
        """tau from ansatz (a) is positive."""
        tau = ScaleAnalysis.tau_from_ansatz_a(RHO_DE_OBSERVED)
        assert tau > 0

    def test_omega_ansatz_b_is_compton(self):
        """
        omega from ansatz (b) matches Compton frequency for mass
        derived from cell vacuum formula.
        """
        omega = ScaleAnalysis.omega_from_ansatz_b(RHO_DE_OBSERVED)
        mass = ScaleAnalysis.mass_from_ansatz_b(RHO_DE_OBSERVED)
        omega_compton = mass * C**2 / HBAR
        assert abs(omega - omega_compton) / omega_compton < 1e-10

    def test_mass_ansatz_b_is_neutrino(self):
        """Mass from ansatz (b) is ~ 2.31 meV (neutrino mass)."""
        mass = ScaleAnalysis.mass_from_ansatz_b(RHO_DE_OBSERVED)
        mass_eV = mass * C**2 / EV_TO_J
        # Should be in the meV range
        assert 1e-3 < mass_eV < 5e-3, f"mass = {mass_eV*1e3:.2f} meV"

    def test_L_holographic_is_hubble(self):
        """Holographic scale for rho_DE ~ Hubble radius."""
        L = ScaleAnalysis.L_from_holographic(RHO_DE_OBSERVED)
        ratio = L / HUBBLE_LENGTH
        assert 0.5 < ratio < 2.0, f"L/L_H = {ratio}"

    def test_analyze_observed_de_complete(self):
        """Analysis returns all expected keys."""
        result = ScaleAnalysis.analyze_observed_de()
        assert "ansatz_a" in result
        assert "ansatz_b" in result
        assert "ansatz_c_holographic" in result

    def test_ansatz_b_circular(self):
        """Ansatz (b) is flagged as circular."""
        result = ScaleAnalysis.analyze_observed_de()
        assert "circular" in result["ansatz_b"]["note"].lower()


# ===========================================================================
# 9. Master Comparison
# ===========================================================================
class TestMasterComparison:

    @pytest.fixture
    def results(self):
        return compute_all_densities()

    def test_all_densities_positive(self, results):
        """Every energy density is positive."""
        for key, val in results.items():
            rho = val["rho_J_per_m3"]
            assert rho > 0, f"{key}: rho = {rho} <= 0"

    def test_all_densities_finite(self, results):
        """Every energy density is finite."""
        for key, val in results.items():
            rho = val["rho_J_per_m3"]
            assert np.isfinite(rho), f"{key}: rho = {rho} not finite"

    def test_observed_is_correct(self, results):
        """Observed value matches."""
        assert results["observed"]["rho_J_per_m3"] == RHO_DE_OBSERVED

    def test_cell_vacuum_near_observed(self, results):
        """Cell vacuum (neutrino mass) ~ observed."""
        ratio = results["cell_vacuum"]["ratio_to_observed"]
        assert 0.5 < ratio < 2.0

    def test_holographic_near_observed(self, results):
        """Holographic (Hubble) ~ observed."""
        ratio = results["holographic_hubble"]["ratio_to_observed"]
        assert 0.5 < ratio < 3.0

    def test_ml_far_below_observed(self, results):
        """Margolus-Levitin << observed."""
        ratio = results["margolus_levitin"]["ratio_to_observed"]
        assert ratio < 1e-100

    def test_planck_far_above_observed(self, results):
        """Planck cutoff >> observed (the 10^120 problem)."""
        ratio = results["mode_vacuum_planck"]["ratio_to_observed"]
        assert ratio > 1e100

    def test_cell_vacuum_w_is_zero(self, results):
        """Cell vacuum has w=0."""
        assert results["cell_vacuum"]["w"] == 0

    def test_mode_vacuum_w_is_minus_one(self, results):
        """Mode vacuum has w=-1."""
        assert results["mode_vacuum_compton"]["w"] == -1

    def test_all_keys_present(self, results):
        """All expected formulations are present."""
        expected_keys = [
            "cell_vacuum", "mode_vacuum_compton", "mode_vacuum_planck",
            "holographic_hubble", "holographic_future",
            "margolus_levitin", "vacuum_persistence",
            "information_diff_ml", "information_diff_ds",
            "observed", "critical",
        ]
        for key in expected_keys:
            assert key in results, f"Missing key: {key}"


# ===========================================================================
# Dimensional Analysis Checks
# ===========================================================================
class TestDimensionalAnalysis:
    """
    Verify dimensional consistency by checking that formulas with
    different but equivalent expressions give the same numerical result.
    """

    def test_critical_density_two_ways(self):
        """rho_crit = 3 H0^2 c^2 / (8 pi G) computed two ways."""
        rho1 = 3.0 * H0_SI**2 * C**2 / (8.0 * np.pi * G)
        # Also: rho_crit = 3 H0^2 / (8 pi G / c^2)
        # using M_P^2 = hbar c / G:
        M_P = PLANCK_MASS
        rho2 = 3.0 * H0_SI**2 * M_P**2 * C**2 / (8.0 * np.pi * HBAR * C)
        # These should agree since M_P^2 = hbar c / G => G = hbar c / M_P^2
        rel_err = abs(rho1 - rho2) / rho1
        assert rel_err < 1e-10, f"Critical density mismatch: {rel_err}"

    def test_cell_vacuum_two_forms(self):
        """rho_cell = m^4 c^5 / hbar^3 = mc^2 / lambda_C^3."""
        m = M_NU1_KG
        rho1 = m**4 * C**5 / HBAR**3
        lambda_C = HBAR / (m * C)
        rho2 = m * C**2 / lambda_C**3
        assert abs(rho1 - rho2) / rho1 < 1e-12

    def test_holographic_equals_friedmann(self):
        """3c^4/(8piG(c/H0)^2) = 3H0^2c^2/(8piG) = rho_crit."""
        L = C / H0_SI
        rho_holo = 3.0 * C**4 / (8.0 * np.pi * G * L**2)
        rho_crit = 3.0 * H0_SI**2 * C**2 / (8.0 * np.pi * G)
        assert abs(rho_holo - rho_crit) / rho_crit < 1e-12

    def test_ml_density_dimensions(self):
        """hbar H0^4 / c^3 has dimensions of J/m^3."""
        # [hbar] = J s, [H0] = 1/s, [c] = m/s
        # [hbar H0^4 / c^3] = J s * s^-4 / (m^3 s^-3) = J s^-3 / (m^3 s^-3) = J/m^3
        # Just verify the numeric result is reasonable
        rho = HBAR * H0_SI**4 / C**3
        assert rho > 0
        assert np.isfinite(rho)


# ===========================================================================
# Edge Cases and Robustness
# ===========================================================================
class TestEdgeCases:

    def test_zero_mass_mode_sum(self):
        """Massless mode sum works."""
        fms = FullFieldModeSumCost(mass_kg=0.0)
        rho = fms.mode_sum_density_massless_analytic(1e10)
        assert rho > 0

    def test_very_small_region(self):
        """Information excess for small region."""
        info = InformationExcess(M_NU1_KG, region_size=1.0)  # 1 meter
        # Holographic info could exceed volumetric for small regions
        # (the holographic bound is not necessarily exceeded)
        assert info.volumetric_information() > 0
        assert info.holographic_information() > 0

    def test_planck_mass_cell_vacuum(self):
        """Cell vacuum with Planck mass gives Planck-scale density."""
        rho = PLANCK_MASS**4 * C**5 / HBAR**3
        # ~ (hbar c / G)^2 * c^5 / hbar^3 = c^7 / (G^2 hbar)
        # This should be enormous
        assert rho > 1e100

    def test_holographic_small_L(self):
        """Holographic density diverges for small L."""
        rho1 = HolographicDarkEnergy.holographic_density(1e10)
        rho2 = HolographicDarkEnergy.holographic_density(1.0)
        assert rho2 > rho1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
