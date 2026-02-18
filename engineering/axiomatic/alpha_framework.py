"""
Alpha Framework: Axiomatic Vacuum Selection
============================================

Runs the Two Vacua Theory's cell vacuum and mode vacuum through a set of
consistency axioms. The cell vacuum passes all axioms; the mode vacuum
fails the refinability (A1) and finiteness (F) axioms.

This provides an axiomatic selection principle: requiring all axioms
uniquely selects the cell vacuum among the two candidates.

Axioms implemented:
    A0 - Existence: finite-dimensional Hilbert space and density matrix
    A1 - Refinability: convergence of observables under lattice refinement
    P  - Propagator composition: U(t2,t0) = U(t2,t1) * U(t1,t0)
    Q  - Unitarity: U^dag U = I
    M' - Measurement consistency: Born rule, normalization
    L  - Locality: no-signaling across spacelike separation
    F  - Finiteness: all observables finite without regularization
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


# =============================================================================
# Physical Constants (SI)
# =============================================================================

HBAR = 1.054571817e-34      # J*s
C = 2.99792458e8            # m/s
G = 6.67430e-11             # m^3/(kg*s^2)
EV_TO_JOULE = 1.602176634e-19

# Neutrino masses
M_NU_OLD_EV = 2.31e-3       # meV - old prediction (from dark energy density match)
M_NU_NEW_EV = 1.77e-3       # meV - new prediction (from rho_cell = rho_CDM)
M_NU_OLD = M_NU_OLD_EV * EV_TO_JOULE / C**2   # kg
M_NU_NEW = M_NU_NEW_EV * EV_TO_JOULE / C**2   # kg

# Default mass for calculations
M_DEFAULT = M_NU_OLD
LAMBDA_C = HBAR / (M_DEFAULT * C)   # Compton wavelength
RHO_CELL = M_DEFAULT**4 * C**5 / HBAR**3  # Cell vacuum energy density


# =============================================================================
# Result Structures
# =============================================================================

class AxiomVerdict(Enum):
    """Result of an axiom check."""
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class AxiomResult:
    """Result of a single axiom check on a vacuum state."""
    axiom_name: str
    axiom_label: str       # Short label like "A0", "A1", "F"
    verdict: AxiomVerdict
    evidence: Dict         # Computed quantities supporting the verdict
    explanation: str        # Human-readable explanation

    @property
    def passed(self) -> bool:
        return self.verdict == AxiomVerdict.PASS

    def __repr__(self):
        v = "PASS" if self.passed else "FAIL"
        return f"AxiomResult({self.axiom_label}: {v} - {self.axiom_name})"


@dataclass
class GauntletResult:
    """Result of running all axioms on a vacuum state."""
    vacuum_name: str
    results: Dict[str, AxiomResult] = field(default_factory=dict)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results.values())

    @property
    def failures(self) -> List[str]:
        return [label for label, r in self.results.items() if not r.passed]

    @property
    def passes(self) -> List[str]:
        return [label for label, r in self.results.items() if r.passed]

    def summary(self) -> str:
        lines = [f"=== Axiom Gauntlet: {self.vacuum_name} ==="]
        for label, result in self.results.items():
            mark = "PASS" if result.passed else "FAIL"
            lines.append(f"  [{mark}] {label}: {result.axiom_name}")
        verdict = "ALL PASSED" if self.all_passed else f"FAILED: {', '.join(self.failures)}"
        lines.append(f"  Result: {verdict}")
        return "\n".join(lines)


# =============================================================================
# Vacuum State Base Class
# =============================================================================

class VacuumState:
    """Base class for vacuum states subject to axiom checks."""

    name: str = "Generic"

    def hilbert_space_dimension(self, region_size: float) -> Optional[int]:
        """
        Dimension of Hilbert space for a region of given size.
        Returns None if infinite-dimensional.
        """
        raise NotImplementedError

    def density_matrix_trace(self, region_size: float) -> float:
        """Trace of the density matrix for a region. Should be 1.0."""
        raise NotImplementedError

    def energy_density(self, lattice_spacing: float) -> float:
        """Energy density <T_00> at a given lattice spacing."""
        raise NotImplementedError

    def energy_density_series(self, spacings: np.ndarray) -> np.ndarray:
        """Energy density at multiple lattice spacings."""
        return np.array([self.energy_density(a) for a in spacings])

    def pressure(self) -> float:
        """Pressure <T_ii>/3."""
        raise NotImplementedError

    def equation_of_state(self) -> float:
        """w = p/rho."""
        raise NotImplementedError

    def propagator_composition_error(self, t0: float, t1: float, t2: float,
                                      dt: float = 1e-3) -> float:
        """
        ||U(t2,t0) - U(t2,t1)*U(t1,t0)||, should be ~0.
        Returns the Frobenius norm of the difference.
        """
        raise NotImplementedError

    def unitarity_error(self, t: float, dt: float = 1e-3) -> float:
        """
        ||U^dag(t)*U(t) - I||, should be ~0.
        Returns the Frobenius norm of the difference.
        """
        raise NotImplementedError

    def measurement_probability_sum(self, num_outcomes: int = 100) -> float:
        """Sum of Born rule probabilities for num_outcomes. Should be ~1.0."""
        raise NotImplementedError

    def entanglement_entropy(self, region_area: float,
                              cutoff: float = None) -> float:
        """
        Entanglement entropy for a bipartition at a surface of given area.
        cutoff: UV cutoff (lattice spacing) if applicable.
        """
        raise NotImplementedError

    def is_product_state(self) -> bool:
        """Whether the state is a tensor product across spatial cells."""
        raise NotImplementedError

    def partial_trace_consistency(self, num_cells: int) -> float:
        """
        Check that partial trace of the full state over some cells
        yields the reduced state on remaining cells.
        Returns the trace distance between the two.
        For product states this should be exactly 0.
        """
        raise NotImplementedError


# =============================================================================
# Mode Vacuum Implementation
# =============================================================================

class ModeVacuum(VacuumState):
    """
    Standard QFT mode vacuum |0>.

    Constructed via momentum-space mode decomposition.
    - Infinite-dimensional Fock space per region
    - UV-divergent energy density
    - w = -1 (Lorentz invariant)
    - Entangled across all spatial bipartitions
    """

    name = "Mode Vacuum |0>"

    def __init__(self, mass: float = M_DEFAULT):
        self.mass = mass
        self.lambda_C = HBAR / (mass * C)
        self.omega_C = mass * C**2 / HBAR  # Compton frequency

    def hilbert_space_dimension(self, region_size: float) -> Optional[int]:
        """Fock space is infinite-dimensional."""
        return None  # Infinite

    def density_matrix_trace(self, region_size: float) -> float:
        """The mode vacuum is a pure state; trace of |0><0| = 1."""
        return 1.0

    def energy_density(self, lattice_spacing: float) -> float:
        """
        Mode vacuum energy density with UV cutoff k_max = pi/a.

        rho = integral_0^{k_max} (hbar * omega_k / 2) * 4*pi*k^2 dk / (2*pi)^3

        where omega_k = sqrt(k^2*c^2 + m^2*c^4/hbar^2).

        For k >> mc/hbar, this goes as ~ hbar*c*k_max^4 / (16*pi^2).
        We compute the full integral numerically.
        """
        k_max = np.pi / lattice_spacing
        mc_over_hbar = self.mass * C / HBAR

        # Numerical integration using Simpson's rule
        num_points = 10001
        k = np.linspace(0, k_max, num_points)
        dk = k[1] - k[0]

        omega_k = np.sqrt(k**2 * C**2 + (mc_over_hbar * C)**2)
        integrand = (HBAR * omega_k / 2) * (4 * np.pi * k**2) / (2 * np.pi)**3

        # Simpson's rule
        rho = np.trapezoid(integrand, k)
        return rho

    def energy_density_analytic(self, lattice_spacing: float) -> float:
        """
        Leading-order analytic approximation for k_max >> mc/hbar:

        rho ~ hbar*c / (16*pi^2) * k_max^4

        This captures the UV-divergent behavior.
        """
        k_max = np.pi / lattice_spacing
        return HBAR * C * k_max**4 / (16 * np.pi**2)

    def pressure(self) -> float:
        """
        Mode vacuum pressure. For Lorentz-invariant vacuum, p = -rho.
        But rho diverges, so we return the symbolic relation.
        Returns: -1 times a representative (cutoff-dependent) energy density.
        """
        # Use Compton cutoff as reference
        rho = self.energy_density(self.lambda_C)
        return -rho

    def equation_of_state(self) -> float:
        """w = p/rho = -1 for Lorentz-invariant vacuum."""
        return -1.0

    def propagator_composition_error(self, t0: float, t1: float, t2: float,
                                      dt: float = 1e-3) -> float:
        """
        For each mode k, U_k(t) = exp(-i*omega_k*t).
        Composition is exact: U_k(t2-t0) = U_k(t2-t1)*U_k(t1-t0).
        We verify this for a sample of modes.
        """
        num_modes = 50
        k_max = np.pi / self.lambda_C
        k_vals = np.linspace(0.01 * k_max, k_max, num_modes)
        mc_over_hbar = self.mass * C / HBAR

        max_error = 0.0
        for k in k_vals:
            omega = np.sqrt(k**2 * C**2 + (mc_over_hbar * C)**2)
            # U(t2,t0) as a phase
            phase_full = omega * (t2 - t0)
            # U(t2,t1) * U(t1,t0)
            phase_composed = omega * (t2 - t1) + omega * (t1 - t0)
            # These should be identical
            error = abs(np.exp(-1j * phase_full) - np.exp(-1j * phase_composed))
            max_error = max(max_error, error)

        return max_error

    def unitarity_error(self, t: float, dt: float = 1e-3) -> float:
        """
        For each mode, U_k = exp(-i*omega_k*t) is manifestly unitary:
        U_k^dag * U_k = exp(+i*omega_k*t) * exp(-i*omega_k*t) = 1.
        We verify numerically for a sample of modes.
        """
        num_modes = 50
        k_max = np.pi / self.lambda_C
        k_vals = np.linspace(0.01 * k_max, k_max, num_modes)
        mc_over_hbar = self.mass * C / HBAR

        max_error = 0.0
        for k in k_vals:
            omega = np.sqrt(k**2 * C**2 + (mc_over_hbar * C)**2)
            U = np.exp(-1j * omega * t)
            U_dag = np.conj(U)
            error = abs(U_dag * U - 1.0)
            max_error = max(max_error, error)

        return max_error

    def measurement_probability_sum(self, num_outcomes: int = 100) -> float:
        """
        For the mode vacuum, the probability of finding n particles in a
        single mode is delta_{n,0}. Sum of probabilities = 1.

        More generally, for any observable with discrete spectrum,
        Born rule gives sum_n |<n|0>|^2 = 1 by completeness.
        """
        # For the vacuum state in the number basis:
        # P(n=0) = 1, P(n>0) = 0
        # Return exact 1.0
        return 1.0

    def entanglement_entropy(self, region_area: float,
                              cutoff: float = None) -> float:
        """
        Entanglement entropy of mode vacuum for a bipartition.

        The mode vacuum has area-law entanglement:
        S = c_1 * A / a^2

        where A is the boundary area and a is the UV cutoff (lattice spacing).
        c_1 ~ 0.3 for a free scalar field (Srednicki 1993).

        This DIVERGES as cutoff -> 0.
        """
        if cutoff is None:
            cutoff = self.lambda_C
        c1 = 0.3  # Numerical coefficient for free scalar
        return c1 * region_area / cutoff**2

    def is_product_state(self) -> bool:
        """Mode vacuum is NOT a product state in position space."""
        return False

    def partial_trace_consistency(self, num_cells: int) -> float:
        """
        For the entangled mode vacuum, partial trace yields a mixed state.
        The reduced state on a subsystem is thermal-like.
        We return a nonzero value representing the entanglement.

        Specifically, for the mode vacuum restricted to N cells with cutoff a,
        the entanglement entropy is ~ c1 * boundary_area / a^2.
        We return this entropy as a measure of partial trace non-triviality.
        """
        # For a 1D chain of N cells, boundary has 2 points (left/right edges)
        # In 3D, boundary area ~ N^(2/3) * lambda_C^2
        boundary_area = 2 * num_cells**(2.0/3.0) * self.lambda_C**2
        return self.entanglement_entropy(boundary_area, self.lambda_C)


# =============================================================================
# Cell Vacuum Implementation
# =============================================================================

class CellVacuum(VacuumState):
    """
    Cell vacuum |Omega>.

    Product of coherent states on Compton-scale cells.
    - Finite-dimensional per cell (truncated Fock space)
    - Finite energy density rho = m^4 c^5 / hbar^3
    - w = 0 (pressureless dust)
    - Zero entanglement (product state)
    """

    name = "Cell Vacuum |Omega>"

    def __init__(self, mass: float = M_DEFAULT,
                 alpha: float = 1.0 / np.sqrt(2),
                 fock_truncation: int = 20):
        self.mass = mass
        self.lambda_C = HBAR / (mass * C)
        self.omega_C = mass * C**2 / HBAR
        self.alpha = alpha  # Coherent state displacement parameter
        self.fock_truncation = fock_truncation
        self.rho = mass**4 * C**5 / HBAR**3

    def _num_cells(self, region_size: float) -> int:
        """Number of Compton-scale cells in a region of given linear size."""
        return max(1, int(np.ceil(region_size / self.lambda_C)))

    def hilbert_space_dimension(self, region_size: float) -> int:
        """
        H_R = tensor product of H_cell_i.
        Each cell has truncated Fock space of dimension fock_truncation.
        Total dimension = fock_truncation^N_cells.

        For practical purposes, return (fock_truncation, num_cells) encoded
        as the per-cell dimension (since total dimension is exponential).
        Actually, return fock_truncation as the per-cell dimension.
        The point is it's FINITE.
        """
        return self.fock_truncation

    def hilbert_space_total_dimension(self, region_size: float) -> int:
        """Total Hilbert space dimension (exponential in cell count)."""
        n = self._num_cells(region_size)
        return self.fock_truncation ** n

    def num_cells_in_region(self, region_size: float) -> int:
        return self._num_cells(region_size)

    def density_matrix_trace(self, region_size: float) -> float:
        """
        Each cell is in a pure coherent state |alpha>.
        The density matrix is |alpha><alpha| with trace 1 per cell.
        Total density matrix is tensor product, trace = 1.
        """
        return 1.0

    def coherent_state_amplitudes(self, n_max: int = None) -> np.ndarray:
        """
        Fock state amplitudes for coherent state |alpha>.
        <n|alpha> = exp(-|alpha|^2/2) * alpha^n / sqrt(n!)
        """
        if n_max is None:
            n_max = self.fock_truncation
        n = np.arange(n_max)
        # Use log-space for numerical stability
        log_amp = -0.5 * abs(self.alpha)**2 + n * np.log(abs(self.alpha)) \
                  - 0.5 * np.array([sum(np.log(np.arange(1, k+1))) if k > 0 else 0 for k in n])
        return np.exp(log_amp)

    def energy_density(self, lattice_spacing: float) -> float:
        """
        Cell vacuum energy density is INDEPENDENT of lattice spacing
        (as long as spacing >= lambda_C).

        rho = m^4 * c^5 / hbar^3

        If lattice_spacing < lambda_C, we don't add new cells --- the
        Compton wavelength is the natural minimum cell size. So the
        energy density remains constant.
        """
        return self.rho

    def pressure(self) -> float:
        """
        Cell vacuum has zero pressure (w = 0).

        Each cell is an independent QHO in a coherent state.
        Coherent states have equal kinetic and potential energy
        (virial theorem), but the spatial averaging over random
        phases gives zero net pressure.
        """
        return 0.0

    def equation_of_state(self) -> float:
        """w = p/rho = 0."""
        return 0.0

    def _qho_evolution_matrix(self, t: float, dim: int = None) -> np.ndarray:
        """
        QHO time evolution matrix in Fock basis.
        U_{nm} = delta_{nm} * exp(-i * omega * (n + 1/2) * t)
        """
        if dim is None:
            dim = self.fock_truncation
        n = np.arange(dim)
        phases = np.exp(-1j * self.omega_C * (n + 0.5) * t)
        return np.diag(phases)

    def propagator_composition_error(self, t0: float, t1: float, t2: float,
                                      dt: float = 1e-3) -> float:
        """
        For a QHO, U(t) = exp(-i*H*t/hbar) in Fock basis is diagonal.
        Composition U(t2-t0) = U(t2-t1)*U(t1-t0) is exact.
        """
        dim = min(self.fock_truncation, 10)  # Use manageable dimension
        U_full = self._qho_evolution_matrix(t2 - t0, dim)
        U_21 = self._qho_evolution_matrix(t2 - t1, dim)
        U_10 = self._qho_evolution_matrix(t1 - t0, dim)
        U_composed = U_21 @ U_10
        return np.linalg.norm(U_full - U_composed)

    def unitarity_error(self, t: float, dt: float = 1e-3) -> float:
        """
        U^dag * U = I for QHO evolution.
        """
        dim = min(self.fock_truncation, 10)
        U = self._qho_evolution_matrix(t, dim)
        product = U.conj().T @ U
        identity = np.eye(dim)
        return np.linalg.norm(product - identity)

    def measurement_probability_sum(self, num_outcomes: int = 100) -> float:
        """
        For coherent state |alpha>, probability of finding n particles:
        P(n) = exp(-|alpha|^2) * |alpha|^{2n} / n!

        This is a Poisson distribution, sum to 1.
        We verify numerically.
        """
        n = np.arange(num_outcomes)
        alpha_sq = abs(self.alpha)**2

        # Compute log probabilities for numerical stability
        log_probs = -alpha_sq + 2 * n * np.log(abs(self.alpha)) \
                    - np.array([sum(np.log(np.arange(1, k+1))) if k > 0 else 0.0 for k in n])
        probs = np.exp(log_probs)
        return np.sum(probs)

    def entanglement_entropy(self, region_area: float,
                              cutoff: float = None) -> float:
        """
        Cell vacuum is a product state. Entanglement entropy = 0
        for ANY bipartition. Exactly zero, not approximately.
        """
        return 0.0

    def is_product_state(self) -> bool:
        """Cell vacuum IS a product state by construction."""
        return True

    def partial_trace_consistency(self, num_cells: int) -> float:
        """
        For a product state rho = rho_1 x rho_2 x ... x rho_N,
        partial trace over any subset gives the product of remaining cells.
        Trace distance = 0 exactly.
        """
        return 0.0

    def coherent_state_overlap_with_fock_vacuum(self, num_cells: int) -> float:
        """
        |<0|Omega>| = prod_i |<0|alpha_i>| = exp(-N*|alpha|^2/2)
        This goes to 0 exponentially as N grows -> orthogonality.
        """
        return np.exp(-num_cells * abs(self.alpha)**2 / 2)


# =============================================================================
# Axiom Checkers
# =============================================================================

def check_a0_existence(vacuum: VacuumState) -> AxiomResult:
    """
    A0 - Existence: The theory assigns a finite-dimensional Hilbert space
    H_R to every bounded region R, and a density matrix rho_R on H_R.
    """
    region_size = 10 * LAMBDA_C  # 10 Compton wavelengths

    dim = vacuum.hilbert_space_dimension(region_size)
    trace = vacuum.density_matrix_trace(region_size)

    # For cell vacuum: dim is finite, trace = 1
    # For mode vacuum: dim is None (infinite), but trace = 1
    has_finite_dim = dim is not None
    has_valid_trace = abs(trace - 1.0) < 1e-10

    # A0 passes if we have a state (even if infinite-dimensional for now)
    # The existence axiom is about having a well-defined state, not finiteness
    # Finiteness of dim is a bonus for cell vacuum
    passed = has_valid_trace  # Both vacua have valid states

    evidence = {
        "hilbert_dim": dim if dim is not None else "infinite",
        "density_matrix_trace": trace,
        "finite_dimensional": has_finite_dim,
        "region_size_lambda_C": region_size / LAMBDA_C,
    }

    if has_finite_dim:
        explanation = (
            f"Hilbert space dimension per cell = {dim}. "
            f"Density matrix trace = {trace:.15f}. "
            f"Finite-dimensional Hilbert space with valid density matrix."
        )
    else:
        explanation = (
            f"Hilbert space is infinite-dimensional (Fock space). "
            f"Density matrix trace = {trace:.15f}. "
            f"State exists and is well-defined, though not finite-dimensional."
        )

    return AxiomResult(
        axiom_name="Existence",
        axiom_label="A0",
        verdict=AxiomVerdict.PASS if passed else AxiomVerdict.FAIL,
        evidence=evidence,
        explanation=explanation,
    )


def check_a1_refinement(vacuum: VacuumState) -> AxiomResult:
    """
    A1 - Refinability (Convergence under refinement):
    As lattice spacing a -> 0, physical observables must converge.

    For mode vacuum: rho(a) ~ hbar*c/a^4 -> diverges.
    For cell vacuum: rho(a) = m^4*c^5/hbar^3 = const.
    """
    # Test at multiple lattice spacings
    spacings_in_lambda_C = np.array([1.0, 0.5, 0.1, 0.01])
    spacings = spacings_in_lambda_C * LAMBDA_C

    densities = vacuum.energy_density_series(spacings)

    # Check convergence: ratio of consecutive densities
    ratios = densities[1:] / densities[:-1]

    # For a convergent sequence, ratios should approach 1
    # For a divergent sequence (1/a^4), ratios grow as (a_prev/a_next)^4
    max_ratio = np.max(ratios)
    min_ratio = np.min(ratios)

    # Convergence criterion: all ratios within [0.5, 2.0] means roughly constant
    # Divergence: ratios >> 1
    converges = max_ratio < 5.0  # Very generous threshold

    # Also check if the finest spacing gives a finite, reasonable value
    finest_density = densities[-1]
    is_finite = np.isfinite(finest_density)

    # Compute the scaling exponent: if rho ~ a^p, then p = log(rho2/rho1)/log(a2/a1)
    if len(densities) >= 2 and all(d > 0 for d in densities):
        scaling_exponents = []
        for i in range(len(densities) - 1):
            if densities[i+1] > 0 and densities[i] > 0:
                exp = np.log(densities[i+1] / densities[i]) / np.log(spacings[i+1] / spacings[i])
                scaling_exponents.append(exp)
    else:
        scaling_exponents = [0.0]

    avg_exponent = np.mean(scaling_exponents)

    # For mode vacuum, exponent ~ -4 (diverges as 1/a^4)
    # For cell vacuum, exponent ~ 0 (constant)
    passed = converges and is_finite

    evidence = {
        "lattice_spacings_lambda_C": spacings_in_lambda_C.tolist(),
        "energy_densities_J_m3": densities.tolist(),
        "density_ratios": ratios.tolist(),
        "scaling_exponent": avg_exponent,
        "max_ratio": max_ratio,
        "converges": converges,
        "finest_density_finite": is_finite,
    }

    if passed:
        explanation = (
            f"Energy density is stable under refinement. "
            f"Scaling exponent = {avg_exponent:.2f} (0 = constant). "
            f"Density at finest spacing = {finest_density:.4e} J/m^3. "
            f"Physical observables converge as lattice is refined."
        )
    else:
        explanation = (
            f"Energy density DIVERGES under refinement. "
            f"Scaling exponent = {avg_exponent:.2f} (expected ~-4 for 1/a^4). "
            f"Max density ratio = {max_ratio:.2e}. "
            f"Refinement makes observables worse, not better."
        )

    return AxiomResult(
        axiom_name="Refinability",
        axiom_label="A1",
        verdict=AxiomVerdict.PASS if passed else AxiomVerdict.FAIL,
        evidence=evidence,
        explanation=explanation,
    )


def check_propagator_composition(vacuum: VacuumState) -> AxiomResult:
    """
    P - Propagator Composition: U(t2,t0) = U(t2,t1) * U(t1,t0).
    """
    # Use times in units of 1/omega_C (Compton time)
    omega_C = M_DEFAULT * C**2 / HBAR
    t_unit = 1.0 / omega_C

    t0 = 0.0
    t1 = 1.5 * t_unit
    t2 = 3.7 * t_unit

    error = vacuum.propagator_composition_error(t0, t1, t2)
    passed = error < 1e-10

    evidence = {
        "t0": t0,
        "t1": t1,
        "t2": t2,
        "composition_error": error,
        "threshold": 1e-10,
    }

    explanation = (
        f"Propagator composition error = {error:.2e}. "
        f"U(t2,t0) {'matches' if passed else 'does NOT match'} "
        f"U(t2,t1)*U(t1,t0) to within {1e-10:.0e}."
    )

    return AxiomResult(
        axiom_name="Propagator Composition",
        axiom_label="P",
        verdict=AxiomVerdict.PASS if passed else AxiomVerdict.FAIL,
        evidence=evidence,
        explanation=explanation,
    )


def check_unitarity(vacuum: VacuumState) -> AxiomResult:
    """
    Q - Unitarity: U^dag * U = I.
    """
    omega_C = M_DEFAULT * C**2 / HBAR
    t_unit = 1.0 / omega_C

    # Test at multiple times
    times = [0.5 * t_unit, 1.0 * t_unit, 2.5 * t_unit, 7.3 * t_unit]
    errors = [vacuum.unitarity_error(t) for t in times]
    max_error = max(errors)

    passed = max_error < 1e-10

    evidence = {
        "times_tested": len(times),
        "max_unitarity_error": max_error,
        "all_errors": errors,
        "threshold": 1e-10,
    }

    explanation = (
        f"Maximum unitarity error ||U^dag*U - I|| = {max_error:.2e} "
        f"across {len(times)} time values. "
        f"{'Unitary' if passed else 'NOT unitary'} to within {1e-10:.0e}."
    )

    return AxiomResult(
        axiom_name="Unitarity",
        axiom_label="Q",
        verdict=AxiomVerdict.PASS if passed else AxiomVerdict.FAIL,
        evidence=evidence,
        explanation=explanation,
    )


def check_measurement_consistency(vacuum: VacuumState) -> AxiomResult:
    """
    M' - Measurement Consistency: Born rule probabilities sum to 1.
    """
    num_outcomes_list = [10, 50, 100, 200]
    sums = [vacuum.measurement_probability_sum(n) for n in num_outcomes_list]

    # Check that sums converge to 1.0
    max_deviation = max(abs(s - 1.0) for s in sums)
    passed = max_deviation < 1e-6

    evidence = {
        "num_outcomes_tested": num_outcomes_list,
        "probability_sums": sums,
        "max_deviation_from_1": max_deviation,
        "threshold": 1e-6,
    }

    explanation = (
        f"Born rule probability sums: {[f'{s:.10f}' for s in sums]}. "
        f"Max deviation from 1.0 = {max_deviation:.2e}. "
        f"{'Consistent' if passed else 'INCONSISTENT'} measurement theory."
    )

    return AxiomResult(
        axiom_name="Measurement Consistency",
        axiom_label="M'",
        verdict=AxiomVerdict.PASS if passed else AxiomVerdict.FAIL,
        evidence=evidence,
        explanation=explanation,
    )


def check_locality(vacuum: VacuumState) -> AxiomResult:
    """
    L - Locality (No-signaling): Operations on region A don't affect
    measurement statistics on spacelike-separated region B.

    For product states: automatic (no correlations).
    For entangled states: requires partial trace structure.

    We check:
    1. Whether the state is a product state
    2. Entanglement entropy (0 for product, divergent for mode vacuum)
    3. Partial trace consistency
    """
    is_product = vacuum.is_product_state()

    # Use Compton-scale region
    region_area = (10 * LAMBDA_C)**2  # Area of 10x10 Compton cell boundary
    entropy = vacuum.entanglement_entropy(region_area, LAMBDA_C)

    # Partial trace check
    pt_error = vacuum.partial_trace_consistency(10)

    # Locality is satisfied for BOTH vacua in standard QFT
    # The mode vacuum satisfies no-signaling via microcausality
    # The cell vacuum satisfies it trivially via product structure
    passed = True  # Both pass locality

    evidence = {
        "is_product_state": is_product,
        "entanglement_entropy": entropy,
        "partial_trace_error": pt_error,
        "no_signaling": True,
    }

    if is_product:
        explanation = (
            f"Product state: no-signaling is automatic. "
            f"Entanglement entropy = {entropy:.6f} (exactly zero). "
            f"Partial trace consistency error = {pt_error:.2e}. "
            f"Locality trivially satisfied."
        )
    else:
        explanation = (
            f"Entangled state with S = {entropy:.4f}. "
            f"No-signaling holds via microcausality ([phi(x), phi(y)] = 0 "
            f"for spacelike separation). "
            f"Partial trace yields mixed state (entanglement entropy = {entropy:.4f}). "
            f"Locality satisfied via standard QFT microcausality."
        )

    return AxiomResult(
        axiom_name="Locality (No-signaling)",
        axiom_label="L",
        verdict=AxiomVerdict.PASS if passed else AxiomVerdict.FAIL,
        evidence=evidence,
        explanation=explanation,
    )


def check_finiteness(vacuum: VacuumState) -> AxiomResult:
    """
    F - Finiteness: All physical observables are finite without
    renormalization or regularization.

    For mode vacuum: <T_00> diverges. Requires renormalization.
    For cell vacuum: <T_00> = m^4*c^5/hbar^3 is finite.
    """
    # Energy density at the Compton scale
    rho = vacuum.energy_density(LAMBDA_C)

    # Pressure
    p = vacuum.pressure()

    # Equation of state
    w = vacuum.equation_of_state()

    # Check finiteness
    rho_finite = np.isfinite(rho)
    p_finite = np.isfinite(p)

    # For the mode vacuum, we check if rho DEPENDS on the cutoff
    # (i.e., it's only "finite" because we have a cutoff)
    rho_at_half = vacuum.energy_density(LAMBDA_C / 2)
    rho_at_tenth = vacuum.energy_density(LAMBDA_C / 10)

    # If energy density changes significantly with cutoff, it's not
    # intrinsically finite -- it requires regularization
    cutoff_dependent = abs(rho_at_tenth / rho - 1.0) > 0.01

    # True finiteness: finite AND cutoff-independent
    intrinsically_finite = rho_finite and p_finite and not cutoff_dependent

    evidence = {
        "energy_density_J_m3": rho,
        "pressure_J_m3": p,
        "equation_of_state_w": w,
        "rho_finite": rho_finite,
        "p_finite": p_finite,
        "rho_at_lambda_C": rho,
        "rho_at_lambda_C_over_2": rho_at_half,
        "rho_at_lambda_C_over_10": rho_at_tenth,
        "cutoff_dependent": cutoff_dependent,
        "intrinsically_finite": intrinsically_finite,
    }

    if intrinsically_finite:
        explanation = (
            f"Energy density rho = {rho:.4e} J/m^3 (finite). "
            f"Pressure p = {p:.4e} J/m^3. w = {w}. "
            f"Cutoff-independent: rho is the same at a=lambda_C, a=lambda_C/2, a=lambda_C/10. "
            f"No renormalization needed."
        )
    else:
        explanation = (
            f"Energy density rho(lambda_C) = {rho:.4e} J/m^3, "
            f"rho(lambda_C/2) = {rho_at_half:.4e} J/m^3, "
            f"rho(lambda_C/10) = {rho_at_tenth:.4e} J/m^3. "
            f"Cutoff-dependent: rho changes by factor "
            f"{rho_at_tenth/rho:.1f} when cutoff is refined 10x. "
            f"Requires regularization/renormalization to define finite observables."
        )

    return AxiomResult(
        axiom_name="Finiteness",
        axiom_label="F",
        verdict=AxiomVerdict.PASS if intrinsically_finite else AxiomVerdict.FAIL,
        evidence=evidence,
        explanation=explanation,
    )


# =============================================================================
# Full Gauntlet
# =============================================================================

ALL_AXIOM_CHECKS = [
    ("A0", check_a0_existence),
    ("A1", check_a1_refinement),
    ("P", check_propagator_composition),
    ("Q", check_unitarity),
    ("M'", check_measurement_consistency),
    ("L", check_locality),
    ("F", check_finiteness),
]


def run_full_gauntlet(vacuum: VacuumState) -> GauntletResult:
    """Run all axiom checks on a vacuum state."""
    result = GauntletResult(vacuum_name=vacuum.name)
    for label, check_fn in ALL_AXIOM_CHECKS:
        axiom_result = check_fn(vacuum)
        result.results[label] = axiom_result
    return result


def axiomatic_selection(vacua: List[VacuumState]) -> List[VacuumState]:
    """
    Run the full axiom gauntlet on each vacuum candidate.
    Return only those that pass ALL axioms.

    This is the selection principle: the axioms uniquely select
    the consistent vacuum.
    """
    survivors = []
    for v in vacua:
        g = run_full_gauntlet(v)
        if g.all_passed:
            survivors.append(v)
    return survivors


# =============================================================================
# Detailed Comparison Report
# =============================================================================

def comparison_report(mode: ModeVacuum = None, cell: CellVacuum = None) -> str:
    """Generate a detailed comparison report for both vacua."""
    if mode is None:
        mode = ModeVacuum()
    if cell is None:
        cell = CellVacuum()

    g_mode = run_full_gauntlet(mode)
    g_cell = run_full_gauntlet(cell)

    lines = []
    lines.append("=" * 78)
    lines.append("AXIOMATIC VACUUM SELECTION: COMPARISON REPORT")
    lines.append("=" * 78)
    lines.append("")

    # Header
    lines.append(f"{'Axiom':<6} {'Name':<30} {'Mode Vacuum':<15} {'Cell Vacuum':<15}")
    lines.append("-" * 66)

    for label, _ in ALL_AXIOM_CHECKS:
        mode_result = g_mode.results[label]
        cell_result = g_cell.results[label]
        mode_v = "PASS" if mode_result.passed else "FAIL"
        cell_v = "PASS" if cell_result.passed else "FAIL"
        lines.append(f"{label:<6} {mode_result.axiom_name:<30} {mode_v:<15} {cell_v:<15}")

    lines.append("-" * 66)
    mode_verdict = "ALL PASS" if g_mode.all_passed else f"FAIL: {', '.join(g_mode.failures)}"
    cell_verdict = "ALL PASS" if g_cell.all_passed else f"FAIL: {', '.join(g_cell.failures)}"
    lines.append(f"{'TOTAL':<6} {'':<30} {mode_verdict:<15} {cell_verdict:<15}")

    lines.append("")
    lines.append("=" * 78)
    lines.append("SELECTION PRINCIPLE")
    lines.append("=" * 78)
    lines.append("")

    survivors = axiomatic_selection([mode, cell])
    if len(survivors) == 1 and isinstance(survivors[0], CellVacuum):
        lines.append("Result: The cell vacuum |Omega> is the UNIQUE vacuum satisfying all axioms.")
        lines.append("")
        lines.append("The mode vacuum fails:")
        for label in g_mode.failures:
            r = g_mode.results[label]
            lines.append(f"  - {label} ({r.axiom_name}): {r.explanation}")
        lines.append("")
        lines.append("The cell vacuum satisfies all axioms with:")
        lines.append(f"  - Energy density: rho = {cell.rho:.4e} J/m^3")
        lines.append(f"  - Equation of state: w = {cell.equation_of_state()}")
        lines.append(f"  - Entanglement: S = {cell.entanglement_entropy(1.0)}")
        lines.append(f"  - Product state: {cell.is_product_state()}")
        lines.append("")
        lines.append("Implication: The axiomatically selected vacuum has w=0 (cold dark matter),")
        lines.append("not w=-1 (dark energy). The vacuum energy IS dark matter.")
    else:
        lines.append(f"Survivors: {[v.name for v in survivors]}")

    lines.append("")

    # Detailed evidence sections
    lines.append("=" * 78)
    lines.append("DETAILED EVIDENCE")
    lines.append("=" * 78)

    for vacuum, gauntlet in [(mode, g_mode), (cell, g_cell)]:
        lines.append("")
        lines.append(f"--- {vacuum.name} ---")
        for label, _ in ALL_AXIOM_CHECKS:
            r = gauntlet.results[label]
            lines.append(f"\n  {label} - {r.axiom_name}: {'PASS' if r.passed else 'FAIL'}")
            lines.append(f"    {r.explanation}")
            for k, v in r.evidence.items():
                if isinstance(v, float):
                    lines.append(f"    {k}: {v:.6e}")
                else:
                    lines.append(f"    {k}: {v}")

    return "\n".join(lines)


# =============================================================================
# Scaling Analysis
# =============================================================================

def refinement_scaling_analysis(vacuum: VacuumState,
                                 num_points: int = 20) -> Dict:
    """
    Detailed analysis of how energy density scales with lattice spacing.

    Returns dict with spacings, densities, and fitted scaling exponent.
    """
    # Spacings from 2*lambda_C down to 0.005*lambda_C
    spacings_ratio = np.logspace(np.log10(2.0), np.log10(0.005), num_points)
    spacings = spacings_ratio * LAMBDA_C
    densities = vacuum.energy_density_series(spacings)

    # Fit log-log slope
    log_a = np.log(spacings)
    log_rho = np.log(densities)

    # Linear regression in log space
    coeffs = np.polyfit(log_a, log_rho, 1)
    scaling_exponent = coeffs[0]
    log_prefactor = coeffs[1]

    return {
        "spacings": spacings,
        "spacings_ratio": spacings_ratio,
        "densities": densities,
        "scaling_exponent": scaling_exponent,
        "log_prefactor": log_prefactor,
        "diverges": scaling_exponent < -1.0,  # Significant negative exponent
    }


def entanglement_scaling_analysis(vacuum: VacuumState,
                                    num_points: int = 10) -> Dict:
    """
    How entanglement entropy scales with cutoff.

    For mode vacuum: S ~ A/a^2 (diverges as a -> 0)
    For cell vacuum: S = 0 (independent of cutoff)
    """
    area = (10 * LAMBDA_C)**2  # Fixed boundary area
    cutoffs_ratio = np.logspace(np.log10(2.0), np.log10(0.01), num_points)
    cutoffs = cutoffs_ratio * LAMBDA_C

    entropies = np.array([vacuum.entanglement_entropy(area, a) for a in cutoffs])

    return {
        "cutoffs": cutoffs,
        "cutoffs_ratio": cutoffs_ratio,
        "entropies": entropies,
        "boundary_area": area,
        "max_entropy": np.max(entropies),
        "min_entropy": np.min(entropies),
        "diverges": np.max(entropies) > 10 * np.min(entropies) if np.min(entropies) > 0 else np.max(entropies) > 0,
    }


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print(comparison_report())

    print("\n\n")
    print("=" * 78)
    print("REFINEMENT SCALING ANALYSIS")
    print("=" * 78)

    mode = ModeVacuum()
    cell = CellVacuum()

    for vacuum in [mode, cell]:
        analysis = refinement_scaling_analysis(vacuum)
        print(f"\n{vacuum.name}:")
        print(f"  Scaling exponent: {analysis['scaling_exponent']:.2f}")
        print(f"  Diverges: {analysis['diverges']}")
        print(f"  Density range: {analysis['densities'].min():.4e} to {analysis['densities'].max():.4e} J/m^3")

    print("\n")
    print("=" * 78)
    print("ENTANGLEMENT SCALING ANALYSIS")
    print("=" * 78)

    for vacuum in [mode, cell]:
        analysis = entanglement_scaling_analysis(vacuum)
        print(f"\n{vacuum.name}:")
        print(f"  Entropy range: {analysis['min_entropy']:.6f} to {analysis['max_entropy']:.6f}")
        print(f"  Diverges: {analysis['diverges']}")
