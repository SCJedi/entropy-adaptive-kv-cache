"""
Comprehensive tests for the cell vacuum equation of state verification.

Tests confirm that the cell vacuum gives w = 0 (pressureless dust),
NOT w = -1 (dark energy). This is the most critical finding of the
Two Vacua investigation.
"""

import numpy as np
import pytest
from equation_of_state import (
    KGOscillator,
    StressEnergy,
    VirialTheorem,
    WaldAmbiguity,
    EnergySplit,
    AxionComparison,
    NoTproportionalToG,
    DarkMatterComparison,
    M_ELECTRON,
    HBAR,
    C,
    H0_SI,
    EV_TO_J,
    run_full_verification,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def electron_oscillator():
    """KG oscillator with electron mass, unit amplitude."""
    return KGOscillator(mass=M_ELECTRON, amplitude=1.0)


@pytest.fixture
def time_array(electron_oscillator):
    """Time array spanning 100 oscillation periods with high resolution."""
    osc = electron_oscillator
    dt = osc.period / 5000
    return np.arange(0, 100 * osc.period, dt)


@pytest.fixture
def stress_energy(electron_oscillator):
    return StressEnergy(electron_oscillator)


@pytest.fixture
def virial(electron_oscillator):
    return VirialTheorem(electron_oscillator)


# ===========================================================================
# 1. Klein-Gordon Oscillation Tests
# ===========================================================================
class TestKleinGordonOscillation:

    def test_compton_frequency(self, electron_oscillator):
        """omega = mc^2/hbar for the electron."""
        expected = M_ELECTRON * C**2 / HBAR
        assert abs(electron_oscillator.omega - expected) / expected < 1e-14

    def test_oscillation_period(self, electron_oscillator):
        """T = 2pi/omega."""
        expected = 2 * np.pi / electron_oscillator.omega
        assert abs(electron_oscillator.period - expected) / expected < 1e-14

    def test_field_is_cosine(self, electron_oscillator):
        """F(t) = F0 cos(omega t)."""
        t = np.array([0, electron_oscillator.period / 4,
                       electron_oscillator.period / 2])
        F = electron_oscillator.field(t)
        F0 = electron_oscillator.amplitude
        assert abs(F[0] - F0) < 1e-14 * F0         # cos(0) = 1
        assert abs(F[1]) < 1e-10 * F0               # cos(pi/2) = 0
        assert abs(F[2] + F0) < 1e-10 * F0          # cos(pi) = -1

    def test_field_dot_is_neg_sine(self, electron_oscillator):
        """dF/dt = -F0 omega sin(omega t)."""
        osc = electron_oscillator
        t = np.array([0, osc.period / 4])
        Fdot = osc.field_dot(t)
        assert abs(Fdot[0]) < 1e-10  # sin(0) = 0
        expected_quarter = -osc.amplitude * osc.omega  # sin(pi/2) = 1
        assert abs(Fdot[1] - expected_quarter) / abs(expected_quarter) < 1e-10

    def test_equation_of_motion_residual(self, electron_oscillator):
        """d^2F/dt^2 + omega^2 F = 0, verified numerically."""
        osc = electron_oscillator
        dt = osc.period / 10000
        t = np.arange(0, 10 * osc.period, dt)
        residual = osc.verify_eom(t, dt)
        # Finite difference error should be small (O(dt^2))
        assert residual < 1e-4, f"EOM residual {residual} too large"

    def test_different_masses(self):
        """EOM holds for various masses."""
        for mass_factor in [0.1, 1.0, 10.0, 100.0]:
            mass = mass_factor * M_ELECTRON
            osc = KGOscillator(mass=mass, amplitude=1.0)
            dt = osc.period / 10000
            t = np.arange(0, 10 * osc.period, dt)
            residual = osc.verify_eom(t, dt)
            assert residual < 1e-4, f"EOM failed for mass factor {mass_factor}"


# ===========================================================================
# 2. Stress-Energy Tensor Tests
# ===========================================================================
class TestStressEnergy:

    def test_energy_density_positive(self, stress_energy, time_array):
        """Energy density is always positive."""
        rho = stress_energy.energy_density(time_array)
        assert np.all(rho > 0), "Energy density must be positive"

    def test_energy_density_constant(self, stress_energy, time_array):
        """Energy density is constant for the oscillating solution."""
        rho = stress_energy.energy_density(time_array)
        # rho = (1/2) F0^2 omega^2 [sin^2 + cos^2] = (1/2) F0^2 omega^2
        expected = 0.5 * stress_energy.oscillator.amplitude**2 * \
                   stress_energy.oscillator.omega**2
        rel_err = np.max(np.abs(rho - expected)) / expected
        assert rel_err < 1e-10, f"Energy density not constant: rel_err={rel_err}"

    def test_pressure_oscillates(self, stress_energy, time_array):
        """Pressure oscillates between positive and negative values."""
        p = stress_energy.pressure(time_array)
        assert np.any(p > 0), "Pressure should be positive at some times"
        assert np.any(p < 0), "Pressure should be negative at some times"

    def test_pressure_cos2wt_form(self, stress_energy, time_array):
        """Pressure = -(F0^2 omega^2 / 2) cos(2 omega t)."""
        error = stress_energy.verify_pressure_form(time_array)
        assert error < 1e-10, f"Pressure form error: {error}"

    def test_w_equals_zero_THE_CRITICAL_TEST(self, stress_energy, time_array):
        """
        THE CRITICAL TEST: w = <p>/<rho> = 0.

        This is the most important result of the entire investigation.
        The cell vacuum behaves as pressureless dust, not dark energy.
        """
        w = stress_energy.equation_of_state_w(time_array)
        assert abs(w) < 1e-6, (
            f"CRITICAL FAILURE: w = {w}, expected 0. "
            f"Cell vacuum should be pressureless dust (w=0), not dark energy (w=-1)."
        )

    def test_w_zero_many_periods(self):
        """w = 0 regardless of how many periods we average over."""
        for n in [10, 100, 1000]:
            osc = KGOscillator(mass=M_ELECTRON, amplitude=1.0)
            dt = osc.period / 5000
            t = np.arange(0, n * osc.period, dt)
            se = StressEnergy(osc)
            w = se.equation_of_state_w(t)
            assert abs(w) < 1e-4, f"w={w} at {n} periods, expected 0"

    def test_w_zero_different_amplitudes(self):
        """w = 0 regardless of field amplitude."""
        for amp in [0.001, 1.0, 1000.0, 1e10]:
            osc = KGOscillator(mass=M_ELECTRON, amplitude=amp)
            dt = osc.period / 5000
            t = np.arange(0, 100 * osc.period, dt)
            se = StressEnergy(osc)
            w = se.equation_of_state_w(t)
            assert abs(w) < 1e-5, f"w={w} for amplitude {amp}, expected 0"

    def test_w_not_minus_one(self, stress_energy, time_array):
        """w is definitively NOT -1 (dark energy)."""
        w = stress_energy.equation_of_state_w(time_array)
        assert abs(w - (-1.0)) > 0.9, (
            f"w = {w} is too close to -1. "
            f"Cell vacuum is NOT dark energy."
        )


# ===========================================================================
# 3. Virial Theorem Tests
# ===========================================================================
class TestVirialTheorem:

    def test_virial_kinetic_equals_potential(self, virial, time_array):
        """<kinetic> = <potential> (virial theorem)."""
        result = virial.verify_virial(time_array)
        assert result["relative_difference"] < 1e-6, (
            f"Virial theorem violated: rel_diff = {result['relative_difference']}"
        )

    def test_virial_implies_zero_pressure(self, virial, time_array):
        """<p> = <KE> - <PE> = 0 from the virial theorem."""
        result = virial.verify_virial(time_array)
        avg_rho = result["avg_kinetic"] + result["avg_potential"]
        w_from_virial = result["pressure_from_virial"] / avg_rho
        assert abs(w_from_virial) < 1e-6, (
            f"Virial gives w = {w_from_virial}, expected 0"
        )

    def test_kinetic_and_potential_positive(self, virial, time_array):
        """Both kinetic and potential are positive on average."""
        result = virial.verify_virial(time_array)
        assert result["avg_kinetic"] > 0
        assert result["avg_potential"] > 0


# ===========================================================================
# 4. Wald Ambiguity Tests
# ===========================================================================
class TestWaldAmbiguity:

    def test_w_zero_at_zero_lambda(self):
        """w = 0 when Lambda_0 = 0 (no renormalization ambiguity)."""
        w = WaldAmbiguity.total_w(rho_state=1.0, lambda_0=0.0)
        assert w == 0.0

    def test_w_minus_half_at_equal_split(self):
        """w = -1/2 when Lambda_0 = rho_state (50/50)."""
        w = WaldAmbiguity.total_w(rho_state=1.0, lambda_0=1.0)
        assert abs(w - (-0.5)) < 1e-15

    def test_w_approaches_minus_one_at_large_lambda(self):
        """w -> -1 as Lambda_0 -> infinity, but never reaches it."""
        w = WaldAmbiguity.total_w(rho_state=1.0, lambda_0=1e10)
        assert w > -1.0, "w must be strictly greater than -1"
        assert abs(w - (-1.0)) < 1e-9, "w should be very close to -1"

    def test_w_never_equals_minus_one(self):
        """w = -1 is mathematically impossible for finite Lambda_0."""
        # Use moderate ratios to avoid floating-point rounding to exactly -1
        ratios = np.logspace(-10, 15, 100000)
        w_values = WaldAmbiguity.w_vs_lambda_ratio(ratios)
        assert np.all(w_values > -1.0), "w must be strictly > -1 for all finite ratios"
        # Also verify analytically: w = -r/(1+r), and 1+r > 0 for r >= 0,
        # so w = -1 + 1/(1+r), which is > -1 for all finite r.
        assert np.all(w_values >= -1.0 + 1e-16)

    def test_w_monotonically_decreasing(self):
        """w decreases monotonically as Lambda_0/rho increases."""
        ratios = np.linspace(0, 100, 10001)
        w_values = WaldAmbiguity.w_vs_lambda_ratio(ratios)
        diffs = np.diff(w_values)
        assert np.all(diffs <= 0), "w must decrease with increasing Lambda ratio"

    def test_proof_w_minus_one_requires_zero_rho(self):
        """Algebraic proof that w=-1 needs rho_state=0."""
        proof = WaldAmbiguity.prove_w_minus_one_requires_pure_cc()
        assert "rho_state = 0" in proof["statement"]
        assert "impossible" in proof["conclusion"]

    def test_best_achievable_w(self):
        """Best dark-energy-like w at equal split is -1/2."""
        w_best = WaldAmbiguity.best_achievable_w_at_equal_split()
        assert w_best == -0.5


# ===========================================================================
# 5. Energy Split Tests
# ===========================================================================
class TestEnergySplit:

    def test_5050_split_exact(self):
        """For |alpha|^2 = 1/2, displacement = zero-point energy exactly."""
        es = EnergySplit(mass=M_ELECTRON, alpha_squared=0.5)
        result = es.verify_split()
        assert result["is_5050"], "50/50 split must be exact"

    def test_total_equals_mc2(self):
        """Total energy = mc^2 for |alpha|^2 = 1/2."""
        es = EnergySplit(mass=M_ELECTRON, alpha_squared=0.5)
        result = es.verify_split()
        assert result["total_equals_mc2"], "Total energy must equal mc^2"

    def test_displacement_fraction_half(self):
        """Displacement fraction is exactly 1/2."""
        es = EnergySplit(mass=M_ELECTRON, alpha_squared=0.5)
        result = es.verify_split()
        assert abs(result["displacement_fraction"] - 0.5) < 1e-15

    def test_zero_point_fraction_half(self):
        """Zero-point fraction is exactly 1/2."""
        es = EnergySplit(mass=M_ELECTRON, alpha_squared=0.5)
        result = es.verify_split()
        assert abs(result["zero_point_fraction"] - 0.5) < 1e-15

    def test_energy_split_different_masses(self):
        """50/50 split holds for any mass."""
        for mass_factor in [1e-3, 1.0, 1e3, 1e6]:
            mass = mass_factor * M_ELECTRON
            es = EnergySplit(mass=mass, alpha_squared=0.5)
            result = es.verify_split()
            assert result["is_5050"], f"50/50 split failed for mass factor {mass_factor}"
            assert result["total_equals_mc2"], f"E != mc^2 for factor {mass_factor}"


# ===========================================================================
# 6. Axion Dark Matter Comparison Tests
# ===========================================================================
class TestAxionComparison:

    def test_frequency_2_31meV(self):
        """omega ~ 5.3e12 rad/s for m = 2.31 meV."""
        omega = AxionComparison.oscillation_frequency(2.31e-3)
        # 2.31 meV = 2.31e-3 eV
        expected = 2.31e-3 * EV_TO_J / HBAR
        assert abs(omega - expected) / expected < 1e-10
        # Order of magnitude check
        assert 1e12 < omega < 1e13

    def test_omega_over_H0_enormous(self):
        """omega/H0 ~ 10^30, vastly faster than expansion."""
        ratio = AxionComparison.frequency_ratio(2.31e-3)
        assert ratio > 1e28, f"Ratio {ratio} not large enough"
        assert ratio < 1e32, f"Ratio {ratio} unexpectedly large"

    def test_adiabatic_condition(self):
        """Adiabatic condition omega >> H is satisfied."""
        assert AxionComparison.adiabatic_condition_met(2.31e-3)

    def test_adiabatic_for_electron_mass(self):
        """Even for the much heavier electron, omega >> H."""
        mass_eV = M_ELECTRON * C**2 / EV_TO_J  # ~511 keV
        assert AxionComparison.adiabatic_condition_met(mass_eV)

    def test_gravity_sees_time_average(self):
        """
        Since omega/H >> 1, gravity averages over oscillations.
        Therefore gravity sees <p> = 0, i.e., w = 0.
        """
        ratio = AxionComparison.frequency_ratio(2.31e-3)
        # Number of oscillations per Hubble time
        n_oscillations = ratio / (2 * np.pi)
        assert n_oscillations > 1e28, (
            f"Only {n_oscillations} oscillations per Hubble time, "
            f"need >> 1 for time averaging to apply"
        )


# ===========================================================================
# 7. No T ~ g Tests
# ===========================================================================
class TestNoTproportionalToG:

    def test_oscillating_not_T_prop_g(self):
        """Homogeneous oscillating field does NOT have T ~ g."""
        result = NoTproportionalToG.test_homogeneous_oscillating(
            M_ELECTRON, 1.0, n_periods=50
        )
        assert not result["T_proportional_to_g"]
        assert abs(result["w_average"]) < 1e-4

    def test_static_uniform_not_kg_solution(self):
        """Static uniform field gives w=-1 but is NOT a KG solution."""
        result = NoTproportionalToG.test_static_uniform(M_ELECTRON, 1.0)
        assert abs(result["w"] - (-1.0)) < 1e-15, "Static should give w=-1"
        assert not result["is_kg_solution"], "Static is not a KG solution"

    def test_wavepacket_positive_w(self):
        """Wavepacket has w >= 0, never -1."""
        result = NoTproportionalToG.test_wavepacket(
            M_ELECTRON, 1.0, sigma=1e-10
        )
        assert not result["T_proportional_to_g"]
        assert result["gradient_energy_positive"]

    def test_standing_wave_positive_w(self):
        """Standing wave has w > 0."""
        osc = KGOscillator(mass=M_ELECTRON, amplitude=1.0)
        k = osc.omega * 0.5  # sub-Compton wavenumber
        result = NoTproportionalToG.test_standing_wave(
            M_ELECTRON, 1.0, k=k, L=2*np.pi/k
        )
        assert not result["T_proportional_to_g"]
        assert result["w_parallel"] > 0
        assert result["w_parallel"] < 1.0

    def test_algebraic_proof(self):
        """Algebraic proof is logically complete."""
        proof = NoTproportionalToG.algebraic_proof()
        assert "F = 0" in proof["step3"]
        assert "No nontrivial" in proof["conclusion"]

    def test_standing_wave_w_formula(self):
        """w = k^2/(k^2 + m^2) for standing wave."""
        omega = M_ELECTRON * C**2 / HBAR
        for k_ratio in [0.1, 0.5, 1.0, 2.0, 10.0]:
            k = k_ratio * omega
            result = NoTproportionalToG.test_standing_wave(
                M_ELECTRON, 1.0, k=k, L=2*np.pi/k
            )
            expected_w = k**2 / (k**2 + omega**2)
            assert abs(result["w_parallel"] - expected_w) < 1e-10


# ===========================================================================
# 8. Dark Matter Comparison Tests
# ===========================================================================
class TestDarkMatterComparison:

    # The mass that gives rho ~ 5.94e-10 J/m^3 is about 2.31 meV,
    # NOT the electron mass. The formula rho = m^4 c^5 / hbar^3 is
    # strongly mass-dependent.
    MASS_2_31_MEV = 2.31e-3 * EV_TO_J / C**2  # 2.31 meV in kg

    def test_cell_vacuum_density_for_axion_mass(self):
        """Cell vacuum density ~ 5.94e-10 J/m^3 for m = 2.31 meV."""
        rho = DarkMatterComparison.cell_vacuum_density(self.MASS_2_31_MEV)
        assert 1e-10 < rho < 1e-8, f"rho = {rho}, expected ~5.94e-10"

    def test_cell_vacuum_density_electron_mass(self):
        """Cell vacuum density for electron mass is much larger."""
        rho = DarkMatterComparison.cell_vacuum_density(M_ELECTRON)
        # Electron is ~2.2e5 times heavier than 2.31 meV
        # rho scales as m^4, so ~(2.2e5)^4 ~ 2.3e21 times larger
        assert rho > 1e20, f"rho = {rho}, should be very large for electron"

    def test_dark_matter_density(self):
        """Observed DM density ~ 2.4e-10 J/m^3."""
        rho_dm = DarkMatterComparison.observed_dark_matter_density()
        assert abs(rho_dm - 2.4e-10) < 1e-11

    def test_ratio_around_2_5_for_axion_mass(self):
        """Cell vacuum / DM density ratio ~ 2.5 for m = 2.31 meV."""
        ratio = DarkMatterComparison.density_ratio(self.MASS_2_31_MEV)
        assert 0.5 < ratio < 10.0, f"Ratio {ratio}, expected order-of-magnitude match"

    def test_same_equation_of_state(self):
        """Both cell vacuum and dark matter have w = 0."""
        result = DarkMatterComparison.compute_comparison(self.MASS_2_31_MEV)
        assert result["cell_vacuum_w"] == 0
        assert result["same_eos_as_dark_matter"]

    def test_order_of_magnitude_match(self):
        """Densities match to within an order of magnitude for axion mass."""
        result = DarkMatterComparison.compute_comparison(self.MASS_2_31_MEV)
        assert result["density_order_of_magnitude_match"]

    def test_mass_for_dm_density(self):
        """The mass that gives exactly the DM density is in the meV range."""
        rho_dm = DarkMatterComparison.observed_dark_matter_density()
        m = DarkMatterComparison.mass_for_target_density(rho_dm)
        m_eV = m * C**2 / EV_TO_J
        # Should be in the meV range
        assert 1e-4 < m_eV < 1e-2, f"m = {m_eV} eV, expected ~meV range"


# ===========================================================================
# Integration / Full Pipeline Tests
# ===========================================================================
class TestFullVerification:

    def test_full_pipeline_runs(self):
        """Full verification pipeline completes without error."""
        results = run_full_verification(
            mass=M_ELECTRON, amplitude=1.0, n_periods=50
        )
        assert "w_time_averaged" in results
        assert "virial" in results
        assert "energy_split" in results

    def test_full_pipeline_w_zero(self):
        """Full pipeline confirms w = 0."""
        results = run_full_verification(
            mass=M_ELECTRON, amplitude=1.0, n_periods=50
        )
        assert abs(results["w_time_averaged"]) < 1e-4

    def test_full_pipeline_virial(self):
        """Full pipeline confirms virial theorem."""
        results = run_full_verification(
            mass=M_ELECTRON, amplitude=1.0, n_periods=50
        )
        assert results["virial"]["relative_difference"] < 1e-4

    def test_full_pipeline_wald(self):
        """Full pipeline confirms Wald ambiguity cannot give w = -1."""
        results = run_full_verification(
            mass=M_ELECTRON, amplitude=1.0, n_periods=50
        )
        assert results["wald_never_reaches_minus_one"]

    def test_full_pipeline_energy_split(self):
        """Full pipeline confirms 50/50 energy split."""
        results = run_full_verification(
            mass=M_ELECTRON, amplitude=1.0, n_periods=50
        )
        assert results["energy_split"]["is_5050"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
