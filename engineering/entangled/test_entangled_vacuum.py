"""
Test Suite for Entangled Cell Vacuum Equation of State

Tests verify the key results:
1. At kappa=0, cells are independent with w=0
2. Entanglement entropy increases with coupling
3. Gradient energy contributes POSITIVE pressure (not negative)
4. w is non-negative for all coupling strengths (on the lattice)
5. w approaches 1/3 (radiation, 3D) or 1 (stiff, 1D) for large coupling
6. The virial theorem gives w=0 for any harmonic system (mode by mode)
7. Two-cell system matches exact results
8. Dispersion relation matches continuum QFT at low k
9. Energy decomposition is self-consistent
"""

import numpy as np
import pytest
from entangled_vacuum import (
    HBAR, C, M_ELECTRON,
    TwoCoupledCells,
    CellChain,
    QFTConnection,
    w_limits_analysis,
    compute_full_investigation,
)


# ===========================================================================
# 1. Two Coupled Cells — Basic Properties
# ===========================================================================
class TestTwoCellBasics:
    """Basic properties of the two-cell system."""

    def test_uncoupled_frequencies_equal(self):
        """At kappa=0, both normal modes have the same frequency."""
        tc = TwoCoupledCells(kappa=0.0)
        assert abs(tc.omega_plus - tc.omega_minus) < 1e-10 * tc.omega

    def test_uncoupled_ground_energy(self):
        """At kappa=0, E_0 = hbar*omega (two half-quanta)."""
        tc = TwoCoupledCells(kappa=0.0)
        expected = HBAR * tc.omega
        assert abs(tc.ground_state_energy - expected) / expected < 1e-12

    def test_coupled_omega_minus_increases(self):
        """omega_- = omega*sqrt(1+4*kappa) increases with kappa."""
        for kappa in [0.1, 0.5, 1.0, 5.0]:
            tc = TwoCoupledCells(kappa=kappa)
            expected = tc.omega * np.sqrt(1.0 + 4.0 * kappa)
            assert abs(tc.omega_minus - expected) / expected < 1e-12

    def test_omega_plus_unchanged(self):
        """Center-of-mass frequency is always omega regardless of coupling."""
        for kappa in [0.0, 0.1, 1.0, 10.0]:
            tc = TwoCoupledCells(kappa=kappa)
            assert abs(tc.omega_plus - tc.omega) / tc.omega < 1e-12

    def test_ground_energy_increases_with_coupling(self):
        """Ground state energy increases with coupling strength."""
        energies = []
        for kappa in [0.0, 0.1, 0.5, 1.0, 5.0]:
            tc = TwoCoupledCells(kappa=kappa)
            energies.append(tc.ground_state_energy)
        assert all(energies[i] < energies[i+1] for i in range(len(energies)-1))

    def test_coupling_energy_zero_at_kappa_zero(self):
        """No extra energy from coupling at kappa=0."""
        tc = TwoCoupledCells(kappa=0.0)
        assert abs(tc.coupling_energy) < 1e-10 * HBAR * tc.omega

    def test_coupling_energy_positive(self):
        """Coupling always adds energy (zero-point of higher-frequency mode)."""
        for kappa in [0.1, 0.5, 1.0]:
            tc = TwoCoupledCells(kappa=kappa)
            assert tc.coupling_energy > 0


# ===========================================================================
# 2. Two Coupled Cells — Entanglement
# ===========================================================================
class TestTwoCellEntanglement:
    """Entanglement entropy of the two-cell system."""

    def test_no_entanglement_at_kappa_zero(self):
        """Product state at kappa=0: S=0."""
        tc = TwoCoupledCells(kappa=0.0)
        S = tc.entanglement_entropy()
        assert abs(S) < 1e-12

    def test_entanglement_increases_with_coupling(self):
        """Entanglement entropy is monotonically increasing with kappa."""
        S_values = []
        for kappa in [0.01, 0.1, 0.5, 1.0, 5.0]:
            tc = TwoCoupledCells(kappa=kappa)
            S_values.append(tc.entanglement_entropy())
        assert all(S_values[i] < S_values[i+1] for i in range(len(S_values)-1))

    def test_entanglement_positive_for_nonzero_coupling(self):
        """Any nonzero coupling produces entanglement."""
        for kappa in [0.01, 0.1, 1.0]:
            tc = TwoCoupledCells(kappa=kappa)
            assert tc.entanglement_entropy() > 0

    def test_squeezing_parameter_consistent(self):
        """Squeezing parameter should be consistent with entanglement."""
        for kappa in [0.1, 0.5, 1.0]:
            tc = TwoCoupledCells(kappa=kappa)
            r = tc.squeezing_parameter()
            assert r > 0
            # Larger coupling → larger squeezing
        r_values = [TwoCoupledCells(kappa=k).squeezing_parameter() for k in [0.1, 1.0, 10.0]]
        assert all(r_values[i] < r_values[i+1] for i in range(len(r_values)-1))


# ===========================================================================
# 3. Two Coupled Cells — Equation of State
# ===========================================================================
class TestTwoCellEOS:
    """Equation of state for the two-cell system."""

    def test_w_virial_always_zero(self):
        """Virial theorem gives w=0 for any harmonic system."""
        for kappa in [0.0, 0.1, 0.5, 1.0, 10.0]:
            tc = TwoCoupledCells(kappa=kappa)
            assert tc.w_virial_per_mode() == 0.0

    def test_w_qft_zero_at_kappa_zero(self):
        """QFT stress tensor gives w=0 when there's no coupling."""
        tc = TwoCoupledCells(kappa=0.0)
        w = tc.w_qft_stress_tensor()
        assert abs(w) < 1e-12

    def test_w_qft_positive_for_nonzero_coupling(self):
        """QFT stress tensor gives w > 0 for any coupling > 0."""
        for kappa in [0.01, 0.1, 0.5, 1.0, 5.0]:
            tc = TwoCoupledCells(kappa=kappa)
            w = tc.w_qft_stress_tensor()
            assert w > 0, f"kappa={kappa}: w={w} should be positive"

    def test_w_qft_bounded_below_one(self):
        """QFT w should be bounded by 1 in 1D."""
        for kappa in [0.1, 1.0, 10.0, 100.0]:
            tc = TwoCoupledCells(kappa=kappa)
            w = tc.w_qft_stress_tensor()
            assert w < 1.0 + 1e-10, f"kappa={kappa}: w={w} exceeds 1"

    def test_w_qft_increases_with_coupling(self):
        """w increases monotonically with coupling."""
        w_values = []
        for kappa in [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]:
            tc = TwoCoupledCells(kappa=kappa)
            w_values.append(tc.w_qft_stress_tensor())
        assert all(w_values[i] <= w_values[i+1] + 1e-10 for i in range(len(w_values)-1))

    def test_w_never_negative(self):
        """w is NEVER negative — entanglement cannot give negative pressure on lattice."""
        for kappa in [0.0, 0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 50.0]:
            tc = TwoCoupledCells(kappa=kappa)
            w = tc.w_qft_stress_tensor()
            assert w >= -1e-12, f"kappa={kappa}: w={w} is negative!"


# ===========================================================================
# 4. Two Coupled Cells — Energy Decomposition
# ===========================================================================
class TestTwoCellEnergyDecomposition:
    """Energy decomposition consistency checks."""

    def test_energy_decomposition_consistent(self):
        """T + V_onsite + V_coupling = E_total."""
        for kappa in [0.0, 0.1, 0.5, 1.0, 5.0]:
            tc = TwoCoupledCells(kappa=kappa)
            decomp = tc.energy_decomposition()
            assert decomp["consistency_error"] < 1e-10, \
                f"kappa={kappa}: consistency error = {decomp['consistency_error']}"

    def test_fractions_sum_to_one(self):
        """Energy fractions sum to 1."""
        for kappa in [0.0, 0.1, 1.0]:
            tc = TwoCoupledCells(kappa=kappa)
            decomp = tc.energy_decomposition()
            total_frac = decomp["T_fraction"] + decomp["V_onsite_fraction"] + decomp["V_coupling_fraction"]
            assert abs(total_frac - 1.0) < 1e-10

    def test_virial_holds_in_decomposition(self):
        """Virial theorem: T = V_onsite + V_coupling."""
        for kappa in [0.1, 0.5, 1.0, 5.0]:
            tc = TwoCoupledCells(kappa=kappa)
            decomp = tc.energy_decomposition()
            virial_error = abs(decomp["T_kinetic"] - decomp["V_onsite"] - decomp["V_coupling"])
            scale = decomp["E_total"]
            assert virial_error / scale < 1e-10

    def test_no_coupling_energy_at_kappa_zero(self):
        """V_coupling = 0 at kappa=0."""
        tc = TwoCoupledCells(kappa=0.0)
        decomp = tc.energy_decomposition()
        assert abs(decomp["V_coupling"]) < 1e-10 * decomp["E_total"]

    def test_coupling_fraction_increases_with_kappa(self):
        """Coupling energy fraction increases with kappa."""
        fracs = []
        for kappa in [0.01, 0.1, 0.5, 1.0, 5.0]:
            tc = TwoCoupledCells(kappa=kappa)
            decomp = tc.energy_decomposition()
            fracs.append(decomp["V_coupling_fraction"])
        assert all(fracs[i] <= fracs[i+1] + 1e-10 for i in range(len(fracs)-1))


# ===========================================================================
# 5. N-Cell Chain — Basic Properties
# ===========================================================================
class TestChainBasics:
    """Basic properties of the N-cell chain."""

    def test_uncoupled_energy(self):
        """At kappa=0, E = (N/2)*hbar*omega."""
        N = 50
        chain = CellChain(N=N, kappa=0.0)
        expected = 0.5 * N * HBAR * chain.omega
        assert abs(chain.ground_state_energy() - expected) / expected < 1e-12

    def test_all_modes_equal_at_kappa_zero(self):
        """At kappa=0, all normal mode frequencies = omega."""
        chain = CellChain(N=50, kappa=0.0)
        freqs = chain.mode_frequencies()
        assert np.all(np.abs(freqs - chain.omega) < 1e-10 * chain.omega)

    def test_dispersion_relation_at_k_zero(self):
        """omega(k=0) = omega for any kappa."""
        for kappa in [0.0, 0.5, 1.0]:
            chain = CellChain(N=100, kappa=kappa)
            freqs = chain.mode_frequencies()
            assert abs(freqs[0] - chain.omega) / chain.omega < 1e-12

    def test_mode_frequencies_increase_with_k(self):
        """Mode frequencies increase from k=0 to k=N/2."""
        chain = CellChain(N=100, kappa=0.5)
        freqs = chain.mode_frequencies()
        # First half should be increasing
        half = len(freqs) // 2
        assert np.all(np.diff(freqs[:half+1]) >= -1e-10 * chain.omega)

    def test_max_frequency(self):
        """Maximum frequency = omega*sqrt(1+4*kappa) at k=N/2."""
        for kappa in [0.1, 0.5, 1.0, 5.0]:
            chain = CellChain(N=100, kappa=kappa)
            freqs = chain.mode_frequencies()
            expected_max = chain.omega * np.sqrt(1.0 + 4.0 * kappa)
            assert abs(np.max(freqs) - expected_max) / expected_max < 1e-6

    def test_energy_increases_with_coupling(self):
        """Ground state energy increases with coupling."""
        energies = []
        for kappa in [0.0, 0.1, 0.5, 1.0, 5.0]:
            chain = CellChain(N=50, kappa=kappa)
            energies.append(chain.ground_state_energy())
        assert all(energies[i] < energies[i+1] for i in range(len(energies)-1))


# ===========================================================================
# 6. N-Cell Chain — Equation of State
# ===========================================================================
class TestChainEOS:
    """Equation of state for the N-cell chain."""

    def test_w_virial_always_zero(self):
        """Virial theorem: w=0 for any coupling."""
        for kappa in [0.0, 0.5, 1.0, 10.0]:
            chain = CellChain(N=50, kappa=kappa)
            assert chain.w_virial() == 0.0

    def test_w_qft_1d_zero_at_kappa_zero(self):
        """No coupling → w=0."""
        chain = CellChain(N=50, kappa=0.0)
        assert abs(chain.w_qft_1d()) < 1e-12

    def test_w_qft_3d_zero_at_kappa_zero(self):
        """No coupling → w=0."""
        chain = CellChain(N=50, kappa=0.0)
        assert abs(chain.w_qft_3d_isotropic()) < 1e-12

    def test_w_qft_1d_positive(self):
        """1D QFT w is positive for nonzero coupling."""
        for kappa in [0.01, 0.1, 0.5, 1.0, 5.0]:
            chain = CellChain(N=50, kappa=kappa)
            w = chain.w_qft_1d()
            assert w > 0, f"kappa={kappa}: w_1d={w}"

    def test_w_qft_3d_positive(self):
        """3D QFT w is positive for nonzero coupling."""
        for kappa in [0.01, 0.1, 0.5, 1.0, 5.0]:
            chain = CellChain(N=50, kappa=kappa)
            w = chain.w_qft_3d_isotropic()
            assert w > 0, f"kappa={kappa}: w_3d={w}"

    def test_w_3d_bounded_by_one_third(self):
        """3D isotropic w is bounded by 1/3 (radiation limit)."""
        for kappa in [0.1, 1.0, 10.0, 100.0]:
            chain = CellChain(N=50, kappa=kappa)
            w = chain.w_qft_3d_isotropic()
            assert w < 1.0/3.0 + 1e-6, f"kappa={kappa}: w_3d={w} exceeds 1/3"

    def test_w_1d_bounded_by_one(self):
        """1D w is bounded by 1 (stiff matter limit)."""
        for kappa in [0.1, 1.0, 10.0, 100.0]:
            chain = CellChain(N=50, kappa=kappa)
            w = chain.w_qft_1d()
            assert w < 1.0 + 1e-6, f"kappa={kappa}: w_1d={w} exceeds 1"

    def test_w_3d_increases_with_coupling(self):
        """w increases monotonically with coupling strength."""
        w_values = []
        for kappa in [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]:
            chain = CellChain(N=50, kappa=kappa)
            w_values.append(chain.w_qft_3d_isotropic())
        assert all(w_values[i] <= w_values[i+1] + 1e-10 for i in range(len(w_values)-1))

    def test_w_never_negative_3d(self):
        """w is NEVER negative in 3D — central result."""
        for kappa in [0.0, 0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 50.0, 100.0]:
            chain = CellChain(N=50, kappa=kappa)
            w = chain.w_qft_3d_isotropic()
            assert w >= -1e-10, f"kappa={kappa}: w={w} is negative!"

    def test_w_approaches_one_third_for_large_kappa(self):
        """For very large kappa, w → 1/3 in 3D."""
        chain = CellChain(N=50, kappa=1000.0)
        w = chain.w_qft_3d_isotropic()
        assert abs(w - 1.0/3.0) < 0.01, f"w={w}, expected ~1/3"

    def test_w_approaches_one_for_large_kappa_1d(self):
        """For very large kappa, w → 1 in 1D."""
        chain = CellChain(N=50, kappa=1000.0)
        w = chain.w_qft_1d()
        assert abs(w - 1.0) < 0.01, f"w={w}, expected ~1"


# ===========================================================================
# 7. N-Cell Chain — Energy Decomposition
# ===========================================================================
class TestChainEnergyDecomposition:
    """Energy decomposition for the chain."""

    def test_decomposition_consistent(self):
        """T + V_onsite + V_coupling = E_total."""
        for kappa in [0.0, 0.1, 0.5, 1.0]:
            chain = CellChain(N=50, kappa=kappa)
            decomp = chain.energy_decomposition()
            assert decomp["consistency_error"] < 1e-10

    def test_virial_theorem_chain(self):
        """T = V_onsite + V_coupling for any coupling."""
        for kappa in [0.1, 0.5, 1.0, 5.0]:
            chain = CellChain(N=50, kappa=kappa)
            decomp = chain.energy_decomposition()
            virial_error = abs(decomp["T_kinetic"] - decomp["V_onsite"] - decomp["V_coupling"])
            assert virial_error / decomp["E_total"] < 1e-10

    def test_coupling_energy_grows_with_kappa(self):
        """Coupling (gradient) energy fraction increases with kappa."""
        fracs = []
        for kappa in [0.01, 0.1, 0.5, 1.0, 5.0]:
            chain = CellChain(N=50, kappa=kappa)
            decomp = chain.energy_decomposition()
            fracs.append(decomp["V_coupling_fraction"])
        assert all(fracs[i] <= fracs[i+1] + 1e-10 for i in range(len(fracs)-1))


# ===========================================================================
# 8. N-Cell Chain — Entanglement
# ===========================================================================
class TestChainEntanglement:
    """Entanglement entropy in the chain."""

    def test_no_entanglement_at_kappa_zero(self):
        """Product state at kappa=0."""
        chain = CellChain(N=20, kappa=0.0)
        S = chain.entanglement_entropy_bipartite(n_A=10)
        assert abs(S) < 1e-10

    def test_entanglement_positive_for_nonzero_coupling(self):
        """Nonzero coupling → nonzero entanglement."""
        chain = CellChain(N=20, kappa=0.5)
        S = chain.entanglement_entropy_bipartite(n_A=10)
        assert S > 0

    def test_entanglement_increases_with_coupling(self):
        """More coupling → more entanglement."""
        S_values = []
        for kappa in [0.1, 0.5, 1.0, 5.0]:
            chain = CellChain(N=20, kappa=kappa)
            S = chain.entanglement_entropy_bipartite(n_A=5)
            S_values.append(S)
        assert all(S_values[i] < S_values[i+1] for i in range(len(S_values)-1))


# ===========================================================================
# 9. Dispersion Relation
# ===========================================================================
class TestDispersionRelation:
    """Lattice vs continuum dispersion relation."""

    def test_lattice_matches_qft_at_low_k(self):
        """Lattice dispersion matches QFT at low momenta."""
        chain = CellChain(N=200, kappa=0.5)
        a = C / (chain.omega * np.sqrt(2.0 * 0.5))
        # Low k = small fraction of pi/a
        k_low = np.array([0.01, 0.05, 0.1]) * np.pi / a
        omega_lat = chain.dispersion_relation(k_low)
        omega_qft = chain.qft_dispersion(k_low)
        # At low k, they should agree well
        for i in range(len(k_low)):
            rel_error = abs(omega_lat[i] - omega_qft[i]) / omega_qft[i]
            assert rel_error < 0.05, f"k={k_low[i]}: relative error = {rel_error}"

    def test_lattice_deviates_at_high_k(self):
        """Lattice dispersion deviates from QFT at the Brillouin zone edge."""
        chain = CellChain(N=200, kappa=0.5)
        a = C / (chain.omega * np.sqrt(1.0))  # a for kappa=0.5
        k_high = 0.9 * np.pi / a
        omega_lat = chain.dispersion_relation(np.array([k_high]))
        omega_qft = chain.qft_dispersion(np.array([k_high]))
        rel_error = abs(omega_lat[0] - omega_qft[0]) / omega_qft[0]
        # Should deviate significantly at high k
        assert rel_error > 0.01, "Expected significant deviation at high k"


# ===========================================================================
# 10. Per-Mode w Analysis
# ===========================================================================
class TestPerModeW:
    """Per-mode equation of state analysis."""

    def test_w_k0_is_zero(self):
        """The k=0 mode has w=0 (pure mass energy, no gradient)."""
        chain = CellChain(N=50, kappa=0.5)
        w_modes = chain.w_per_mode_qft_3d()
        assert abs(w_modes[0]) < 1e-12

    def test_w_modes_all_nonnegative(self):
        """Every mode has w_k >= 0."""
        chain = CellChain(N=50, kappa=0.5)
        w_modes = chain.w_per_mode_qft_3d()
        assert np.all(w_modes >= -1e-12)

    def test_w_modes_bounded_by_one_third(self):
        """Every mode has w_k <= 1/3 in 3D."""
        chain = CellChain(N=50, kappa=0.5)
        w_modes = chain.w_per_mode_qft_3d()
        assert np.all(w_modes <= 1.0/3.0 + 1e-10)

    def test_w_highest_mode_approaches_one_third(self):
        """For large kappa, the highest mode approaches w = 1/3."""
        chain = CellChain(N=50, kappa=100.0)
        w_modes = chain.w_per_mode_qft_3d()
        # k = N/2 mode (highest frequency)
        w_max = np.max(w_modes)
        assert abs(w_max - 1.0/3.0) < 0.01


# ===========================================================================
# 11. QFT Connection — Key Physics Results
# ===========================================================================
class TestQFTConnection:
    """Tests for the QFT connection analysis."""

    def test_lorentz_argument_structure(self):
        """Lorentz invariance argument should be well-formed."""
        qft = QFTConnection()
        result = qft.lorentz_invariance_argument()
        assert len(result["proof"]) >= 4
        assert "PROVEN" in result["evidence_tier"]

    def test_lattice_gives_positive_w(self):
        """Lattice calculation gives w > 0."""
        qft = QFTConnection(N_cells=50)
        result = qft.why_lattice_gives_positive_w()
        assert result["lattice_w_3d"] > 0

    def test_entanglement_cannot_give_negative_w(self):
        """Central result: entanglement doesn't give w < 0."""
        qft = QFTConnection(N_cells=50)
        result = qft.can_entanglement_give_negative_w()
        assert result["all_w_nonnegative_3d"]
        assert result["w_3d_monotonic_increasing"]
        assert result["w_3d_bounded_by_one_third"]

    def test_compton_spacing_analysis(self):
        """At Compton spacing (kappa=0.5), w should be well-defined and positive."""
        qft = QFTConnection(N_cells=50)
        result = qft.w_at_compton_spacing()
        assert result["w_virial"] == 0
        assert result["w_qft_3d"] > 0
        assert result["w_qft_3d"] < 1.0/3.0 + 1e-6


# ===========================================================================
# 12. Limits Analysis
# ===========================================================================
class TestLimitsAnalysis:
    """Test the theoretical limits summary."""

    def test_limits_structure(self):
        """Limits analysis should cover key cases."""
        limits = w_limits_analysis()
        assert "cell_vacuum_product_state" in limits
        assert "mode_vacuum_lorentz_invariant" in limits
        assert "key_insight" in limits

    def test_cell_vacuum_w_zero(self):
        """Cell vacuum has w=0."""
        limits = w_limits_analysis()
        assert limits["cell_vacuum_product_state"]["w"] == 0

    def test_mode_vacuum_w_minus_one(self):
        """Mode vacuum has w=-1."""
        limits = w_limits_analysis()
        assert limits["mode_vacuum_lorentz_invariant"]["w"] == -1


# ===========================================================================
# 13. Thermodynamic w
# ===========================================================================
class TestThermodynamicW:
    """Thermodynamic equation of state p = -dE/dV."""

    def test_thermodynamic_w_zero_at_kappa_zero_two_cell(self):
        """At kappa=0, thermodynamic w=0."""
        tc = TwoCoupledCells(kappa=0.0)
        w = tc.w_thermodynamic()
        assert abs(w) < 1e-6

    def test_thermodynamic_w_positive_two_cell(self):
        """Thermodynamic w > 0 for nonzero coupling."""
        for kappa in [0.1, 0.5, 1.0]:
            tc = TwoCoupledCells(kappa=kappa)
            w = tc.w_thermodynamic()
            assert w > -1e-6, f"kappa={kappa}: w_thermo={w}"

    def test_thermodynamic_w_positive_chain(self):
        """Thermodynamic w > 0 for the chain."""
        for kappa in [0.1, 0.5, 1.0]:
            chain = CellChain(N=50, kappa=kappa)
            w = chain.w_thermodynamic()
            assert w > -1e-6, f"kappa={kappa}: w_thermo={w}"


# ===========================================================================
# 14. Two-Cell vs Chain Consistency
# ===========================================================================
class TestTwoCellChainConsistency:
    """Two-cell system should match N=2 chain."""

    def test_ground_energy_matches(self):
        """Two-cell and N=2 chain should give same ground state energy."""
        for kappa in [0.0, 0.1, 0.5, 1.0]:
            tc = TwoCoupledCells(kappa=kappa)
            chain = CellChain(N=2, kappa=kappa)
            rel_error = abs(tc.ground_state_energy - chain.ground_state_energy()) / tc.ground_state_energy
            assert rel_error < 1e-10, f"kappa={kappa}: energy mismatch = {rel_error}"

    def test_w_qft_matches(self):
        """QFT w should match between two-cell and N=2 chain (1D)."""
        for kappa in [0.1, 0.5, 1.0]:
            tc = TwoCoupledCells(kappa=kappa)
            chain = CellChain(N=2, kappa=kappa)
            w_tc = tc.w_qft_stress_tensor()
            w_chain = chain.w_qft_1d()
            assert abs(w_tc - w_chain) < 1e-6, \
                f"kappa={kappa}: w_tc={w_tc}, w_chain={w_chain}"


# ===========================================================================
# 15. Smoke Test — Full Investigation
# ===========================================================================
class TestFullInvestigation:
    """Smoke test for the full investigation."""

    def test_full_investigation_runs(self):
        """Full investigation should complete without errors."""
        results = compute_full_investigation(
            N_cells=20,
            kappa_values=np.array([0.0, 0.1, 0.5, 1.0]),
        )
        assert "two_cell" in results
        assert "chain" in results
        assert "qft_lorentz" in results
        assert "limits" in results

    def test_full_investigation_w_nonnegative(self):
        """All w values in full investigation should be non-negative (3D)."""
        results = compute_full_investigation(
            N_cells=20,
            kappa_values=np.array([0.0, 0.1, 0.5, 1.0, 5.0]),
        )
        for ch in results["chain"]:
            assert ch["w_qft_3d"] >= -1e-10, \
                f"kappa={ch['kappa']}: w_3d={ch['w_qft_3d']} is negative"


# ===========================================================================
# Run
# ===========================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
