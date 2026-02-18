"""
Entangled Cell Vacuum — Equation of State Investigation

Investigates how inter-cell entanglement modifies the equation of state
of the cell vacuum. The cell vacuum |Omega> = tensor product of coherent
states |alpha> with |alpha|^2 = 1/2 on Compton-scale cells. It has
ZERO entanglement between cells and w = 0 (pressureless dust).

The mode vacuum |0> has maximal area-law entanglement and w = -1.

Key question: does introducing controlled entanglement between cells
via nearest-neighbor coupling change w? Can w interpolate from 0 to -1?

THREE APPROACHES:
1. Two coupled cells — exact Gaussian state analysis
2. N-cell chain with nearest-neighbor coupling — dispersion relation
3. Connection to QFT — continuum limit and Lorentz invariance

KEY RESULTS [FRAMEWORK]:
- For independent oscillators, each mode has w = 0 by the virial theorem.
  This is what the cell vacuum exploits.
- For coupled oscillators (entangled cells), the TOTAL system's virial
  theorem still gives w = 0 for the full Hamiltonian's normal modes.
- However, the QFT stress tensor includes gradient terms that contribute
  to spatial pressure components differently than the mass terms.
- The equation of state w depends on HOW you define pressure:
  (a) Virial theorem (time-avg of T-V per mode): always w = 0
  (b) QFT stress tensor (includes gradient contributions to T_ij):
      w depends on the ratio of gradient to mass energy
  (c) Thermodynamic (p = -dE/dV): depends on UV structure

- In the continuum QFT limit with Lorentz-invariant regularization,
  the vacuum has w = -1 by Lorentz symmetry. But on a lattice, the
  regularization breaks Lorentz invariance and w is NOT -1 in general.

- The cell vacuum (product state, no gradients) has w = 0. Adding
  entanglement/gradients can make w negative but reaching w = -1
  requires the full continuum limit with Lorentz-invariant regularization.

Physics:
- Massive scalar field on a 1D lattice of N cells with spacing a
- On-site frequency omega = mc^2/hbar (Compton frequency)
- Nearest-neighbor coupling kappa from the gradient term (nabla phi)^2
  mapped to the lattice: kappa = c^2/(2*omega^2*a^2) = hbar^2/(2*m^2*c^2*a^2)
- At a = lambda_C = hbar/(mc): kappa = 1/2
- Dispersion: omega_k = omega * sqrt(1 + 4*kappa*sin^2(k*a/2))
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Optional

# ---------------------------------------------------------------------------
# Physical constants (SI)
# ---------------------------------------------------------------------------
HBAR = 1.054571817e-34      # J s
C = 2.99792458e8            # m/s
M_ELECTRON = 9.1093837015e-31  # kg


# ===========================================================================
# 1. Two Coupled Cells — Exact Analysis
# ===========================================================================
@dataclass
class TwoCoupledCells:
    """
    Two harmonic oscillator cells with tunable coupling.

    H = hbar*omega*(a1†a1 + a2†a2 + 1) + kappa*m*omega^2*(x1 - x2)^2

    In normal mode coordinates (center-of-mass and relative):
        x+ = (x1 + x2)/sqrt(2)  →  frequency omega_+ = omega
        x- = (x1 - x2)/sqrt(2)  →  frequency omega_- = omega*sqrt(1 + 4*kappa)

    The coupling only affects the relative mode. The ground state is
    a product state in normal-mode space but an ENTANGLED state in
    cell space (for kappa > 0).

    Parameters:
        mass: particle mass in kg
        kappa: dimensionless coupling strength (>=0)
    """
    mass: float = M_ELECTRON
    kappa: float = 0.0

    @property
    def omega(self) -> float:
        """On-site (Compton) frequency omega = mc^2/hbar."""
        return self.mass * C**2 / HBAR

    @property
    def omega_plus(self) -> float:
        """Center-of-mass mode frequency (unaffected by coupling)."""
        return self.omega

    @property
    def omega_minus(self) -> float:
        """Relative mode frequency: omega * sqrt(1 + 4*kappa)."""
        return self.omega * np.sqrt(1.0 + 4.0 * self.kappa)

    @property
    def ground_state_energy(self) -> float:
        """
        E_0 = (1/2)*hbar*omega_+ + (1/2)*hbar*omega_-
            = (1/2)*hbar*omega * [1 + sqrt(1 + 4*kappa)]
        """
        return 0.5 * HBAR * (self.omega_plus + self.omega_minus)

    @property
    def energy_per_cell(self) -> float:
        """Ground state energy per cell."""
        return self.ground_state_energy / 2.0

    @property
    def uncoupled_ground_energy(self) -> float:
        """Ground state energy at kappa=0: hbar*omega."""
        return HBAR * self.omega

    @property
    def coupling_energy(self) -> float:
        """Extra energy from coupling: E_0(kappa) - E_0(0)."""
        return self.ground_state_energy - self.uncoupled_ground_energy

    def entanglement_entropy(self) -> float:
        """
        Von Neumann entropy S of one cell when tracing over the other,
        for the ground state of the coupled system.

        The ground state is a two-mode squeezed vacuum in the cell basis.
        The squeezing parameter r is determined by the frequency ratio.

        For two coupled oscillators with frequencies omega_+ and omega_-,
        the ground state in the (x1, x2) basis has the form of a
        two-mode squeezed state with effective squeezing parameter:

        tanh(2r) = (omega_- - omega_+) / (omega_- + omega_+)

        For omega_+ = omega, omega_- = omega*sqrt(1+4k):
        tanh(2r) = (sqrt(1+4k) - 1) / (sqrt(1+4k) + 1)

        The entanglement entropy is then:
        S = cosh^2(r) * log(cosh^2(r)) - sinh^2(r) * log(sinh^2(r))
        """
        if self.kappa < 1e-15:
            return 0.0

        sq = np.sqrt(1.0 + 4.0 * self.kappa)
        tanh_2r = (sq - 1.0) / (sq + 1.0)

        # Recover r from tanh(2r)
        if abs(tanh_2r) > 1.0 - 1e-15:
            # Saturated case — very large kappa
            r = 10.0  # effectively infinite squeezing
        else:
            r = 0.5 * np.arctanh(tanh_2r)

        if r < 1e-15:
            return 0.0

        c2 = np.cosh(r)**2
        s2 = np.sinh(r)**2

        # S = cosh^2(r) * ln(cosh^2(r)) - sinh^2(r) * ln(sinh^2(r))
        S = c2 * np.log(c2)
        if s2 > 1e-30:
            S -= s2 * np.log(s2)

        return float(S)

    def squeezing_parameter(self) -> float:
        """
        The effective two-mode squeezing parameter r.

        tanh(2r) = (omega_- - omega_+) / (omega_- + omega_+)
        """
        if self.kappa < 1e-15:
            return 0.0
        sq = np.sqrt(1.0 + 4.0 * self.kappa)
        tanh_2r = (sq - 1.0) / (sq + 1.0)
        if abs(tanh_2r) > 1.0 - 1e-15:
            return 10.0
        return 0.5 * np.arctanh(tanh_2r)

    # -------------------------------------------------------------------
    # Stress-Energy Analysis
    # -------------------------------------------------------------------
    def energy_decomposition(self) -> Dict[str, float]:
        """
        Decompose ground state energy into on-site (mass) and coupling
        (gradient) contributions.

        Total energy: E = (1/2)*hbar*(omega_+ + omega_-)

        On-site contribution (from m^2*phi^2 terms):
            For each normal mode, <V_onsite> = (1/2)*(omega/omega_k)*(1/2)*hbar*omega_k
            ... this requires computing <x_1^2> and <x_2^2> in terms of normal modes.

        More precisely, in the ground state:
            <x_+^2> = hbar/(2*m*omega_+)
            <x_-^2> = hbar/(2*m*omega_-)

        Since x_1 = (x_+ + x_-)/sqrt(2), x_2 = (x_+ - x_-)/sqrt(2):
            <x_1^2> = (1/2)*(<x_+^2> + <x_-^2>) = (hbar/(4*m))*(1/omega_+ + 1/omega_-)
            <x_2^2> = same by symmetry

        On-site potential: V_onsite = (1/2)*m*omega^2*(<x_1^2> + <x_2^2>)
            = (1/2)*m*omega^2 * hbar/(2*m) * (1/omega_+ + 1/omega_-)
            = (hbar*omega^2/4) * (1/omega_+ + 1/omega_-)

        Coupling potential: V_coupling = kappa*m*omega^2*<(x_1-x_2)^2>
            = kappa*m*omega^2 * 2*<x_-^2>
            = kappa*m*omega^2 * 2 * hbar/(2*m*omega_-)
            = kappa*hbar*omega^2/omega_-

        Kinetic energy: T = <p_+^2>/(2m) + <p_-^2>/(2m)
            = (1/2)*(1/2)*hbar*omega_+ + (1/2)*(1/2)*hbar*omega_-
            = (hbar/4)*(omega_+ + omega_-)
        """
        om = self.omega
        om_p = self.omega_plus
        om_m = self.omega_minus

        # Kinetic energy
        T = 0.25 * HBAR * (om_p + om_m)

        # On-site potential energy
        V_onsite = 0.25 * HBAR * om**2 * (1.0/om_p + 1.0/om_m)

        # Coupling potential energy
        V_coupling = self.kappa * HBAR * om**2 / om_m

        # Total
        E_total = T + V_onsite + V_coupling

        # Verify
        E_expected = self.ground_state_energy
        consistency = abs(E_total - E_expected) / E_expected

        return {
            "T_kinetic": T,
            "V_onsite": V_onsite,
            "V_coupling": V_coupling,
            "E_total": E_total,
            "E_expected": E_expected,
            "consistency_error": consistency,
            "T_fraction": T / E_total,
            "V_onsite_fraction": V_onsite / E_total,
            "V_coupling_fraction": V_coupling / E_total,
        }

    def w_virial_per_mode(self) -> float:
        """
        Equation of state from virial theorem applied to each normal mode.

        Each normal mode is an independent QHO. The virial theorem gives
        <T_k> = <V_k> for each mode, so time-averaged pressure from each
        mode is zero: p_k = <T_k> - <V_k> = 0.

        Therefore the total w = 0 by mode-by-mode virial theorem.

        This is ALWAYS true for any system diagonalizable into independent
        normal modes (harmonic system).
        """
        return 0.0

    def w_qft_stress_tensor(self) -> float:
        """
        Equation of state from the QFT stress-energy tensor.

        For a scalar field on a 1D lattice, the stress tensor component
        T_xx (pressure in the lattice direction) includes the gradient
        contribution:

        T_xx = (1/2)*pi^2/m - (1/2)*m*omega^2*phi^2 + (gradient terms)

        The gradient contribution to T_xx is:
        For 1D: T_xx_gradient = +(1/a^2) * (phi_n - phi_{n+1})^2 / 2
        (positive because the gradient energy contributes positively to
        pressure along the gradient direction)

        Wait — this needs careful treatment. In the continuum:
        T_00 = (1/2)dot(phi)^2 + (1/2)(d_x phi)^2 + (1/2)m^2*phi^2
        T_xx = (1/2)dot(phi)^2 + (1/2)(d_x phi)^2 - (1/2)m^2*phi^2

        So the gradient energy appears with the SAME sign in both rho and p!
        This means the gradient energy contributes w = +1 to the pressure
        (like stiff matter), not w = -1.

        For the time-averaged system:
        <T>_t = <V_onsite + V_gradient>_t  (virial for full system)

        The QFT pressure is:
        <p> = <T> - <V_onsite> + <V_gradient>  (NOT T - V_total!)
            = <V_onsite> + <V_gradient> - <V_onsite> + <V_gradient>
            = 2*<V_gradient>

        And rho = <T> + <V_onsite> + <V_gradient> = 2*(<V_onsite> + <V_gradient>)

        So w = p/rho = 2*V_grad / (2*(V_onsite + V_grad)) = V_grad/(V_onsite + V_grad)

        This ranges from 0 (no coupling) to 1 (all gradient energy).
        THIS IS POSITIVE, not negative!

        The resolution: w = -1 for vacuum energy comes from Lorentz
        invariance, which is a property of the REGULARIZATION, not of
        the bare mode sum. On a lattice, Lorentz invariance is broken
        and w is NOT -1.

        Let me compute this properly for the two-cell case.
        """
        decomp = self.energy_decomposition()
        V_onsite = decomp["V_onsite"]
        V_coupling = decomp["V_coupling"]
        T = decomp["T_kinetic"]
        E_total = decomp["E_total"]

        # In the QFT stress tensor for a 1D scalar field:
        # rho = T + V_onsite + V_coupling = E_total
        # p_xx = T + V_coupling - V_onsite
        #
        # The gradient (coupling) term appears with + in T_xx,
        # the mass term appears with - in T_xx.
        #
        # Time-averaged: <T> = <V_total> = <V_onsite + V_coupling>
        # So <p> = <V_onsite + V_coupling> + V_coupling - V_onsite
        #        = 2*V_coupling
        # Wait, need to be more careful.

        # For the two-cell system, T_xx in the QFT sense:
        # T_xx = (1/2)*pi^2/m + (1/2)*(dphi/dx)^2 - (1/2)*m^2*phi^2
        #      ≈ (1/2)*p^2/m + kappa*m*omega^2*(x1-x2)^2 - (1/2)*m*omega^2*x^2
        #
        # Time-averaged over each normal mode (virial: <p^2/(2m)> = <V> for each mode):
        # For the + mode: <T_+> = (1/4)*hbar*omega_+, <V_+> = (1/4)*hbar*omega_+
        # For the - mode: <T_-> = (1/4)*hbar*omega_-, <V_-> = (1/4)*hbar*omega_-
        #
        # But V_- = (1/2)*m*omega_-^2*x_-^2 includes both onsite and coupling parts.
        #
        # Need to decompose V_- back into onsite + coupling contributions.
        # V_- = (1/2)*m*omega^2*x_-^2 + kappa*m*omega^2*2*x_-^2
        #      = (1/2)*m*(omega^2 + 4*kappa*omega^2)*x_-^2
        #      = (1/2)*m*omega_-^2*x_-^2 (yes, consistent)
        #
        # Onsite contribution from - mode: (1/2)*m*omega^2*<x_-^2>
        # Coupling contribution from - mode: 2*kappa*m*omega^2*<x_-^2>
        #
        # <x_-^2> = hbar/(2*m*omega_-)
        # Onsite from -: (1/4)*hbar*omega^2/omega_-
        # Coupling from -: kappa*hbar*omega^2/omega_-

        # QFT pressure (time-averaged, 1D):
        # p = <T_kinetic> + <V_coupling> - <V_onsite>
        p_qft = T + V_coupling - V_onsite
        rho = E_total

        if rho == 0:
            return float('nan')
        return p_qft / rho

    def w_thermodynamic(self, da_frac: float = 1e-6) -> float:
        """
        Equation of state from thermodynamics: p = -dE/dV.

        For 1D with 2 cells at spacing a, V = 2a.
        E = (1/2)*hbar*omega*(1 + sqrt(1 + 4*kappa(a)))

        where kappa(a) = c^2/(2*omega^2*a^2).

        We compute p = -(1/2)*dE/da by finite difference.
        """
        om = self.omega
        a_0 = C / (om)  # Compton wavelength as reference spacing

        # kappa at spacing a: kappa = c^2/(2*omega^2*a^2)
        # We need to express our kappa in terms of a physical spacing
        # kappa = self.kappa means a = c/(omega*sqrt(2*kappa)) if kappa > 0
        if self.kappa < 1e-15:
            return 0.0  # No coupling, no volume dependence of coupling

        a = C / (om * np.sqrt(2.0 * self.kappa))

        def E_of_a(spacing):
            k = C**2 / (2.0 * om**2 * spacing**2)
            return 0.5 * HBAR * om * (1.0 + np.sqrt(1.0 + 4.0 * k))

        da = a * da_frac
        dE_da = (E_of_a(a + da) - E_of_a(a - da)) / (2.0 * da)

        # p = -(1/N)*dE/da = -(1/2)*dE/da (for 2 cells)
        p = -0.5 * dE_da
        rho = self.energy_per_cell

        if abs(rho) < 1e-100:
            return float('nan')
        return p / rho

    def full_analysis(self) -> Dict:
        """Complete analysis of the two-cell coupled system."""
        decomp = self.energy_decomposition()
        return {
            "kappa": self.kappa,
            "omega_plus": self.omega_plus,
            "omega_minus": self.omega_minus,
            "frequency_ratio": self.omega_minus / self.omega_plus,
            "ground_state_energy": self.ground_state_energy,
            "coupling_energy": self.coupling_energy,
            "coupling_energy_fraction": self.coupling_energy / self.ground_state_energy if self.ground_state_energy > 0 else 0,
            "entanglement_entropy": self.entanglement_entropy(),
            "squeezing_parameter": self.squeezing_parameter(),
            "energy_decomposition": decomp,
            "w_virial": self.w_virial_per_mode(),
            "w_qft": self.w_qft_stress_tensor(),
            "w_thermodynamic": self.w_thermodynamic(),
        }


# ===========================================================================
# 2. N-Cell Chain with Nearest-Neighbor Coupling
# ===========================================================================
@dataclass
class CellChain:
    """
    1D chain of N oscillator cells with periodic boundary conditions
    and nearest-neighbor coupling.

    H = sum_n [p_n^2/(2m) + (1/2)*m*omega^2*x_n^2
               + kappa*m*omega^2*(x_n - x_{n+1})^2]

    Normal modes: omega_k = omega * sqrt(1 + 4*kappa*sin^2(pi*k/N))
    for k = 0, 1, ..., N-1 (periodic BC).

    Parameters:
        N: number of cells
        mass: particle mass in kg
        kappa: dimensionless coupling strength
    """
    N: int = 100
    mass: float = M_ELECTRON
    kappa: float = 0.0

    @property
    def omega(self) -> float:
        """On-site frequency."""
        return self.mass * C**2 / HBAR

    def mode_frequencies(self) -> np.ndarray:
        """
        Normal mode frequencies for periodic boundary conditions.

        omega_k = omega * sqrt(1 + 4*kappa*sin^2(pi*k/N))
        for k = 0, 1, ..., N-1
        """
        k = np.arange(self.N)
        return self.omega * np.sqrt(1.0 + 4.0 * self.kappa * np.sin(np.pi * k / self.N)**2)

    def dispersion_relation(self, k_continuous: np.ndarray) -> np.ndarray:
        """
        Continuous dispersion relation omega(k) for comparison with QFT.

        omega(k) = omega * sqrt(1 + 4*kappa*sin^2(k*a/2))

        In the long-wavelength limit (k*a << 1):
        omega(k) ≈ omega * sqrt(1 + kappa*(k*a)^2)

        With a = lambda_C and kappa = 1/2:
        omega(k) ≈ omega * sqrt(1 + (k*lambda_C)^2/2)

        In QFT: omega(k) = sqrt(m^2*c^4/hbar^2 + c^2*k^2)
                          = omega * sqrt(1 + (c*k/omega)^2)
                          = omega * sqrt(1 + (k*lambda_C)^2)

        The lattice dispersion matches QFT at low k when kappa = 1/2 and a = lambda_C,
        up to a factor of 2 in the gradient coefficient (lattice artifact).
        """
        if self.kappa < 1e-15:
            return self.omega * np.ones_like(k_continuous)
        # Assume spacing a such that kappa = c^2/(2*omega^2*a^2)
        a = C / (self.omega * np.sqrt(2.0 * self.kappa)) if self.kappa > 0 else np.inf
        return self.omega * np.sqrt(1.0 + 4.0 * self.kappa * np.sin(k_continuous * a / 2)**2)

    def qft_dispersion(self, k_continuous: np.ndarray) -> np.ndarray:
        """
        QFT continuum dispersion relation for comparison.

        omega(k) = sqrt(m^2*c^4/hbar^2 + c^2*k^2) = omega*sqrt(1 + (c*k/omega)^2)
        """
        return self.omega * np.sqrt(1.0 + (C * k_continuous / self.omega)**2)

    # -------------------------------------------------------------------
    # Ground State Energy
    # -------------------------------------------------------------------
    def ground_state_energy(self) -> float:
        """
        Total ground state energy: E_0 = (1/2)*hbar * sum_k omega_k
        """
        return 0.5 * HBAR * np.sum(self.mode_frequencies())

    def ground_state_energy_per_cell(self) -> float:
        """E_0 per cell."""
        return self.ground_state_energy() / self.N

    def uncoupled_energy(self) -> float:
        """Ground state energy at kappa=0: (N/2)*hbar*omega."""
        return 0.5 * self.N * HBAR * self.omega

    def coupling_energy_total(self) -> float:
        """Extra energy from coupling."""
        return self.ground_state_energy() - self.uncoupled_energy()

    # -------------------------------------------------------------------
    # Energy Decomposition
    # -------------------------------------------------------------------
    def energy_decomposition(self) -> Dict[str, float]:
        """
        Decompose ground state energy into kinetic, on-site potential,
        and coupling potential contributions.

        For each normal mode k with frequency omega_k:
        - Kinetic: <T_k> = (1/4)*hbar*omega_k
        - Total potential: <V_k> = (1/4)*hbar*omega_k

        The on-site potential from mode k is proportional to omega^2/omega_k
        (from <x_k^2> = hbar/(2*m*omega_k)):
        - On-site from k: (1/4)*hbar*omega^2/omega_k
        - Coupling from k: (1/4)*hbar*(omega_k^2 - omega^2)/omega_k
                         = (1/4)*hbar*(omega_k - omega^2/omega_k)

        Summing over all modes:
        T_total = (hbar/4) * sum_k omega_k
        V_onsite_total = (hbar/4) * omega^2 * sum_k (1/omega_k)
        V_coupling_total = (hbar/4) * sum_k (omega_k - omega^2/omega_k)
        """
        freqs = self.mode_frequencies()
        om = self.omega

        T_total = 0.25 * HBAR * np.sum(freqs)
        V_onsite_total = 0.25 * HBAR * om**2 * np.sum(1.0 / freqs)
        V_coupling_total = 0.25 * HBAR * np.sum(freqs - om**2 / freqs)
        E_total = T_total + V_onsite_total + V_coupling_total
        E_expected = self.ground_state_energy()

        return {
            "T_kinetic": T_total,
            "V_onsite": V_onsite_total,
            "V_coupling": V_coupling_total,
            "E_total": E_total,
            "E_expected": E_expected,
            "consistency_error": abs(E_total - E_expected) / E_expected,
            "T_fraction": T_total / E_total,
            "V_onsite_fraction": V_onsite_total / E_total,
            "V_coupling_fraction": V_coupling_total / E_total,
        }

    # -------------------------------------------------------------------
    # Equation of State
    # -------------------------------------------------------------------
    def w_virial(self) -> float:
        """
        Equation of state from virial theorem: always w = 0.

        Each normal mode is an independent QHO with <T_k> = <V_k>.
        Total: <T> = <V>, so <p_virial> = <T> - <V> = 0.

        This is the single-mode virial theorem applied mode by mode.
        """
        return 0.0

    def w_qft_1d(self) -> float:
        """
        Equation of state from the 1D QFT stress tensor.

        For a massive scalar field in 1D, the stress tensor components are:
        T_00 = (1/2)*(dphi/dt)^2 + (1/2)*(dphi/dx)^2 + (1/2)*m^2*phi^2
        T_xx = (1/2)*(dphi/dt)^2 + (1/2)*(dphi/dx)^2 - (1/2)*m^2*phi^2

        Note: the gradient term (dphi/dx)^2 appears with the SAME SIGN in
        both T_00 and T_xx. This means the gradient energy contributes
        POSITIVELY to pressure, with w_gradient = +1.

        Time-averaged ground state values:
        <T_kinetic> = <V_onsite> + <V_coupling>  (virial theorem for full H)

        rho = <T_kinetic> + <V_onsite> + <V_coupling> = 2*(<V_onsite> + <V_coupling>)
        p = <T_kinetic> + <V_coupling> - <V_onsite> = 2*<V_coupling>

        Therefore: w = p/rho = <V_coupling> / (<V_onsite> + <V_coupling>)

        This ranges from 0 (kappa=0) to approaching 1 (kappa >> 1) in 1D.

        CRITICAL: This is POSITIVE w, not negative! In 1D, gradient energy
        contributes positive pressure. The w = -1 result in QFT comes from
        Lorentz invariance of the vacuum, which requires 3+1 dimensions
        and Lorentz-invariant regularization.
        """
        decomp = self.energy_decomposition()
        V_onsite = decomp["V_onsite"]
        V_coupling = decomp["V_coupling"]
        T = decomp["T_kinetic"]
        E_total = decomp["E_total"]

        p = T + V_coupling - V_onsite
        if E_total == 0:
            return float('nan')
        return p / E_total

    def w_qft_3d_isotropic(self) -> float:
        """
        Equation of state for a 3D isotropic case (most physically relevant).

        In 3+1D, the stress tensor for a scalar field:
        T_00 = (1/2)dot(phi)^2 + (1/2)|grad phi|^2 + (1/2)m^2*phi^2
        T_ii = (1/2)dot(phi)^2 - (1/2)|grad phi|^2 - (1/2)m^2*phi^2 + (d_i phi)^2

        For an isotropic state, (d_i phi)^2 = (1/3)|grad phi|^2, so:
        T_ii = (1/2)dot(phi)^2 - (1/2)|grad phi|^2 - (1/2)m^2*phi^2 + (1/3)|grad phi|^2
             = (1/2)dot(phi)^2 - (1/6)|grad phi|^2 - (1/2)m^2*phi^2

        Isotropic pressure: p = (1/3)*sum_i T_ii
        p = (1/2)dot(phi)^2 - (1/6)|grad phi|^2 - (1/2)m^2*phi^2

        So the gradient energy contributes NEGATIVELY in 3D (factor -1/6 vs +1/2 in rho)!

        Time-averaged:
        <T_kin> = <V_onsite + V_gradient>  (virial for full H)

        rho = 2*(<V_onsite> + <V_gradient>)
        p = 2*<V_gradient>*(-1/3) + 0  ... wait, let me redo this carefully.

        Actually, using <dot(phi)^2> = <|grad phi|^2> + <m^2*phi^2> (virial for full KG):
        No — the virial theorem for the full system H gives <T> = <V_total>.

        Let's define:
        E_kin = (1/2)<dot(phi)^2>  [kinetic]
        E_grad = (1/2)<|grad phi|^2>  [gradient]
        E_mass = (1/2)<m^2*phi^2>  [mass/on-site]

        Virial theorem: E_kin = E_mass + E_grad  (for full Hamiltonian's normal modes)

        rho = E_kin + E_grad + E_mass = 2*(E_mass + E_grad)
        p = E_kin - (1/3)*E_grad - E_mass
          = (E_mass + E_grad) - (1/3)*E_grad - E_mass
          = (2/3)*E_grad

        Therefore: w = p/rho = (2/3)*E_grad / (2*(E_mass + E_grad))
                             = E_grad / (3*(E_mass + E_grad))

        This is POSITIVE, ranging from 0 (no gradients) to 1/3 (all gradient).
        w = 1/3 is the radiation equation of state.

        For our lattice with coupling kappa:
        E_grad ↔ V_coupling, E_mass ↔ V_onsite
        """
        decomp = self.energy_decomposition()
        V_onsite = decomp["V_onsite"]
        V_coupling = decomp["V_coupling"]

        denominator = 3.0 * (V_onsite + V_coupling)
        if denominator == 0:
            return 0.0
        return V_coupling / denominator

    def w_thermodynamic(self, da_frac: float = 1e-6) -> float:
        """
        Thermodynamic equation of state: p = -dE/dV.

        For 1D: V = N*a, so p = -(1/N)*dE/da.

        E(a) = (1/2)*hbar * sum_k omega * sqrt(1 + 4*kappa(a)*sin^2(pi*k/N))

        where kappa(a) = c^2/(2*omega^2*a^2).
        """
        if self.kappa < 1e-15:
            return 0.0

        om = self.omega
        a = C / (om * np.sqrt(2.0 * self.kappa))

        def E_of_a(spacing):
            k_arr = np.arange(self.N)
            kap = C**2 / (2.0 * om**2 * spacing**2)
            freqs = om * np.sqrt(1.0 + 4.0 * kap * np.sin(np.pi * k_arr / self.N)**2)
            return 0.5 * HBAR * np.sum(freqs)

        da = a * da_frac
        dE_da = (E_of_a(a + da) - E_of_a(a - da)) / (2.0 * da)

        p = -(1.0 / self.N) * dE_da
        rho = self.ground_state_energy_per_cell()
        if abs(rho) < 1e-100:
            return float('nan')
        return p / rho

    def w_per_mode_qft_3d(self) -> np.ndarray:
        """
        Per-mode contribution to w in 3D isotropic case.

        For mode k with frequency omega_k = omega*sqrt(1 + 4*kappa*sin^2(pi*k/N)):
        The "gradient energy" fraction is:
            f_grad_k = (omega_k^2 - omega^2) / omega_k^2 = 4*kappa*sin^2(pi*k/N) / (1 + 4*kappa*sin^2(pi*k/N))

        This mode contributes to w as:
            w_k = f_grad_k / 3  (since w = E_grad/(3*(E_mass+E_grad)) and E_grad/E_total = f_grad/2)

        Actually, more precisely for mode k:
            rho_k = (1/2)*hbar*omega_k
            E_grad_k = (1/2)*hbar*(omega_k - omega^2/omega_k)/2 ... same as V_coupling_k
            p_k = E_grad_k * (2/3) / (hbar*omega_k/2) ... no

        Let me compute it directly.
        For mode k with zero-point energy hbar*omega_k/2:
            V_onsite_k = (hbar/4)*omega^2/omega_k
            V_coupling_k = (hbar/4)*(omega_k - omega^2/omega_k)
            E_total_k = (hbar/2)*omega_k

        3D isotropic pressure contribution from mode k:
            p_k = (2/3)*V_coupling_k

        w_k = p_k / E_total_k = (2/3)*V_coupling_k / ((hbar/2)*omega_k)
             = (2/3)*(1/4)*(omega_k - omega^2/omega_k) / ((1/2)*omega_k)
             = (1/3)*(1 - omega^2/omega_k^2)
             = (1/3) * 4*kappa*sin^2(pi*k/N) / (1 + 4*kappa*sin^2(pi*k/N))
        """
        k_arr = np.arange(self.N)
        sin2 = np.sin(np.pi * k_arr / self.N)**2
        ratio = 4.0 * self.kappa * sin2 / (1.0 + 4.0 * self.kappa * sin2)
        return ratio / 3.0

    # -------------------------------------------------------------------
    # Entanglement
    # -------------------------------------------------------------------
    def entanglement_entropy_bipartite(self, n_A: int = None) -> float:
        """
        Entanglement entropy between subsystem A (first n_A cells) and
        subsystem B (remaining cells), for the Gaussian ground state.

        For a chain of coupled harmonic oscillators, the ground state is
        a Gaussian state. The entanglement entropy can be computed from
        the symplectic eigenvalues of the reduced covariance matrix.

        For large systems, this scales as the boundary area (area law):
        S ~ log(omega_max/omega_min) for a 1D chain (logarithmic in 1D).

        Here we compute it exactly using the covariance matrix method.
        """
        if n_A is None:
            n_A = self.N // 2

        if self.kappa < 1e-15:
            return 0.0  # Product state, no entanglement

        # Build the covariance matrix for the ground state.
        # For N coupled oscillators with periodic BC, normal modes are
        # plane waves: u_k(n) = exp(2*pi*i*k*n/N) / sqrt(N)
        #
        # Ground state covariance matrix elements:
        # <x_n x_m> = (1/N) * sum_k cos(2*pi*k*(n-m)/N) * hbar/(2*m*omega_k)
        # <p_n p_m> = (1/N) * sum_k cos(2*pi*k*(n-m)/N) * m*hbar*omega_k/2
        # <x_n p_m> = 0 (ground state, symmetric ordering)

        freqs = self.mode_frequencies()
        m = self.mass

        # Build NxN position and momentum correlation matrices
        xx = np.zeros((self.N, self.N))
        pp = np.zeros((self.N, self.N))

        for n in range(self.N):
            for m_idx in range(self.N):
                diff = n - m_idx
                # sum over modes
                cos_vals = np.cos(2.0 * np.pi * np.arange(self.N) * diff / self.N)
                xx[n, m_idx] = np.sum(cos_vals / freqs) / self.N
                pp[n, m_idx] = np.sum(cos_vals * freqs) / self.N

        xx *= HBAR / (2.0 * m)
        pp *= m * HBAR / 2.0

        # Extract subsystem A covariance matrix
        xx_A = xx[:n_A, :n_A]
        pp_A = pp[:n_A, :n_A]

        # Symplectic eigenvalues: eigenvalues of sqrt(xx_A @ pp_A)
        # The entanglement entropy is computed from these.
        M = xx_A @ pp_A
        eigenvalues = np.linalg.eigvalsh(M)
        # Symplectic eigenvalues are sqrt of eigenvalues of xx_A @ pp_A
        # They should be >= (hbar/2)^2 by uncertainty principle
        nu = np.sqrt(np.maximum(eigenvalues, 0))

        # Entanglement entropy in terms of symplectic eigenvalues nu_k:
        # S = sum_k [(nu_k/hbar + 1/2)*log(nu_k/hbar + 1/2)
        #           - (nu_k/hbar - 1/2)*log(nu_k/hbar - 1/2)]
        # where nu_k >= hbar/2
        S = 0.0
        for nu_k in nu:
            nbar = nu_k / HBAR
            if nbar < 0.5 + 1e-12:
                continue  # At the minimum, no contribution
            n_plus = nbar + 0.5
            n_minus = nbar - 0.5
            S += n_plus * np.log(n_plus)
            if n_minus > 1e-15:
                S -= n_minus * np.log(n_minus)

        return float(S)

    # -------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------
    def full_analysis(self) -> Dict:
        """Complete analysis of the N-cell chain."""
        decomp = self.energy_decomposition()
        freqs = self.mode_frequencies()
        w_per_mode = self.w_per_mode_qft_3d()

        # Energy-weighted average of per-mode w
        weights = freqs  # zero-point energy proportional to omega_k
        w_avg = np.average(w_per_mode, weights=weights)

        return {
            "N": self.N,
            "kappa": self.kappa,
            "freq_min": float(np.min(freqs)),
            "freq_max": float(np.max(freqs)),
            "freq_ratio": float(np.max(freqs) / np.min(freqs)),
            "ground_state_energy_per_cell": self.ground_state_energy_per_cell(),
            "coupling_energy_fraction": self.coupling_energy_total() / self.ground_state_energy(),
            "energy_decomposition": decomp,
            "w_virial": self.w_virial(),
            "w_qft_1d": self.w_qft_1d(),
            "w_qft_3d": self.w_qft_3d_isotropic(),
            "w_thermodynamic": self.w_thermodynamic(),
            "w_per_mode_avg_3d": float(w_avg),
            "w_per_mode_range_3d": (float(np.min(w_per_mode)), float(np.max(w_per_mode))),
            "entanglement_entropy": self.entanglement_entropy_bipartite(),
        }


# ===========================================================================
# 3. Connection to QFT — Continuum Limit and Lorentz Invariance
# ===========================================================================
@dataclass
class QFTConnection:
    """
    Connect the lattice results to continuum QFT.

    Key insight: the equation of state of the vacuum depends on the
    REGULARIZATION, not just the bare mode sum.

    - Lattice regularization: breaks Lorentz invariance, gives w >= 0
    - Dimensional regularization: preserves Lorentz invariance, gives w = -1
    - Zeta-function regularization: preserves Lorentz invariance, gives w = -1

    The Lorentz-invariant result w = -1 follows from a SYMMETRY argument:
    if <T_uv> is Lorentz invariant, it must be proportional to g_uv,
    which means p = -rho, so w = -1.

    On the lattice, Lorentz invariance is broken, and the naive mode sum
    gives w > 0. The w = -1 result can only be recovered by adding
    counterterms that restore Lorentz invariance (renormalization).

    Parameters:
        mass: particle mass in kg
        N_cells: number of lattice cells for numerical calculations
    """
    mass: float = M_ELECTRON
    N_cells: int = 200

    @property
    def omega(self) -> float:
        return self.mass * C**2 / HBAR

    def w_vs_coupling(self, kappa_values: np.ndarray,
                      dimension: str = "3d") -> Dict[str, np.ndarray]:
        """
        Compute w as function of coupling strength for the cell chain.

        Parameters:
            kappa_values: array of coupling strengths
            dimension: "1d" or "3d" for the QFT stress tensor formula
        """
        w_values = []
        S_values = []
        coupling_fracs = []

        for kappa in kappa_values:
            chain = CellChain(N=self.N_cells, mass=self.mass, kappa=kappa)
            if dimension == "1d":
                w = chain.w_qft_1d()
            else:
                w = chain.w_qft_3d_isotropic()
            w_values.append(w)

            if kappa > 0 and kappa < 100:
                S_values.append(chain.entanglement_entropy_bipartite(n_A=min(5, self.N_cells // 2)))
            else:
                S_values.append(0.0 if kappa < 1e-15 else float('nan'))

            E_total = chain.ground_state_energy()
            coupling_frac = chain.coupling_energy_total() / E_total if E_total > 0 else 0
            coupling_fracs.append(coupling_frac)

        return {
            "kappa": kappa_values,
            "w": np.array(w_values),
            "entanglement_entropy": np.array(S_values),
            "coupling_energy_fraction": np.array(coupling_fracs),
        }

    def w_at_compton_spacing(self) -> Dict[str, float]:
        """
        At the natural lattice spacing a = lambda_C, kappa = 1/2.

        This is the lattice most analogous to the cell vacuum picture,
        where cells are Compton-sized.
        """
        chain = CellChain(N=self.N_cells, mass=self.mass, kappa=0.5)
        analysis = chain.full_analysis()
        return {
            "lattice_spacing": "Compton wavelength",
            "kappa": 0.5,
            "w_virial": analysis["w_virial"],
            "w_qft_1d": analysis["w_qft_1d"],
            "w_qft_3d": analysis["w_qft_3d"],
            "coupling_energy_fraction": analysis["coupling_energy_fraction"],
            "entanglement_entropy": analysis["entanglement_entropy"],
        }

    def lattice_vs_continuum_dispersion(self, kappa: float = 0.5) -> Dict:
        """
        Compare lattice dispersion relation with continuum QFT.

        In continuum: omega_k = sqrt(m^2 + k^2) [natural units c=hbar=1]
        On lattice: omega_k = omega*sqrt(1 + 4*kappa*sin^2(k*a/2))

        They agree at low k (long wavelengths) and differ at high k
        (short wavelengths ~ lattice spacing).
        """
        chain = CellChain(N=self.N_cells, mass=self.mass, kappa=kappa)
        a = C / (self.omega * np.sqrt(2.0 * kappa)) if kappa > 0 else np.inf
        k_max = np.pi / a if a < np.inf else 1.0
        k_values = np.linspace(0, k_max, 200)

        omega_lattice = chain.dispersion_relation(k_values)
        omega_qft = chain.qft_dispersion(k_values)

        return {
            "k_values": k_values,
            "omega_lattice": omega_lattice,
            "omega_qft": omega_qft,
            "relative_error": np.abs(omega_lattice - omega_qft) / omega_qft,
            "lattice_spacing": a,
            "max_k": k_max,
            "match_at_low_k": float(np.abs(omega_lattice[1] - omega_qft[1]) / omega_qft[1]),
        }

    def lorentz_invariance_argument(self) -> Dict:
        """
        Why Lorentz invariance forces w = -1 for the vacuum.

        The vacuum state |0> is Lorentz invariant: U(Lambda)|0> = |0>.
        Therefore <0|T_uv|0> must be a Lorentz-invariant tensor.
        The only rank-2 Lorentz-invariant tensor (up to scale) is g_uv.
        Therefore <T_uv> = -rho_vac * g_uv, giving p = -rho, w = -1.

        This argument does NOT apply to:
        - The cell vacuum (not Lorentz invariant — it picks out a frame)
        - Lattice regularizations (break Lorentz invariance)
        - Any state with a preferred frame

        It DOES apply to:
        - The Minkowski vacuum |0>
        - Any Lorentz-invariant regularization (dim reg, zeta function)
        """
        return {
            "theorem": "Lorentz invariance of |0> implies <T_uv> = -rho*g_uv",
            "proof": [
                "1. |0> is Lorentz invariant: U(Lambda)|0> = |0>",
                "2. Therefore <T_uv> transforms as a Lorentz tensor",
                "3. A Lorentz-invariant symmetric rank-2 tensor is proportional to g_uv",
                "4. <T_uv> = -rho*g_uv, so T_ii = rho*g_ii = -rho (in -+++ signature)",
                "5. p = T_ii/3 = -rho, hence w = -1",
            ],
            "applies_to": "Minkowski vacuum |0> with Lorentz-invariant regularization",
            "does_not_apply_to": [
                "Cell vacuum (not Lorentz invariant, picks a frame)",
                "Lattice regularization (breaks Lorentz invariance)",
                "Thermal states (break Lorentz invariance)",
                "States with particle content (break Lorentz invariance)",
            ],
            "key_insight": (
                "w = -1 is a property of Lorentz SYMMETRY, not of the mode sum. "
                "The mode sum on a lattice gives w > 0. Lorentz-invariant "
                "regularization effectively adds counterterms that shift w to -1."
            ),
            "evidence_tier": "[PROVEN] — exact symmetry argument, standard QFT result",
        }

    def why_lattice_gives_positive_w(self) -> Dict:
        """
        Explain why the naive lattice mode sum gives w > 0 instead of w = -1.

        The lattice dispersion relation omega_k = omega*sqrt(1 + 4*kappa*sin^2(ka/2))
        has a maximum frequency omega_max = omega*sqrt(1+4*kappa) at k = pi/a.

        For mode k, the fraction of energy in gradients is:
        f_grad(k) = (omega_k^2 - omega^2) / omega_k^2

        For high-k modes (near the UV cutoff): f_grad → 4*kappa/(1+4*kappa),
        and these modes contribute w_k → f_grad/(3) (in 3D).

        The total w is a weighted average over all modes.
        Since all mode contributions are positive, the total w > 0.

        The issue: on the lattice, the UV modes are "wrong" — they don't
        respect Lorentz invariance. In the continuum with proper
        regularization, the UV divergences cancel in a way that leaves
        the Lorentz-invariant result w = -1.
        """
        chain = CellChain(N=self.N_cells, mass=self.mass, kappa=0.5)
        decomp = chain.energy_decomposition()

        return {
            "explanation": (
                "On the lattice, every mode k contributes positive w_k to the "
                "total equation of state. This is because the gradient energy "
                "(which increases with k) always contributes positively to pressure "
                "in the QFT stress tensor. The UV modes near k ~ pi/a dominate "
                "and push w toward +1/3 (radiation) in 3D. This is a lattice "
                "artifact. In the continuum with Lorentz-invariant regularization, "
                "the UV divergences are subtracted in a way that preserves "
                "<T_uv> proportional to g_uv, giving w = -1."
            ),
            "lattice_w_3d": chain.w_qft_3d_isotropic(),
            "gradient_fraction": decomp["V_coupling_fraction"],
            "evidence_tier": "[PROVEN] — standard lattice QFT result",
        }

    def can_entanglement_give_negative_w(self) -> Dict:
        """
        Central question: can entanglement between cells give w < 0?

        ANSWER: NO, not on the lattice with the standard QFT stress tensor.

        In 3D, the QFT formula gives:
            w = V_coupling / (3*(V_onsite + V_coupling)) >= 0

        This is always non-negative because V_coupling >= 0 and V_onsite >= 0.

        The gradient energy (which is the coupling energy on the lattice)
        ALWAYS contributes POSITIVE pressure in the QFT stress tensor
        (in 1D) or weakly positive pressure (in 3D).

        HOWEVER: this does NOT mean entanglement is irrelevant.

        The cell vacuum's w = 0 is CORRECT on the lattice. The mode vacuum's
        w = -1 requires the continuum limit with Lorentz-invariant regularization.
        Entanglement between cells (gradient terms) makes w MORE positive
        (toward radiation w = 1/3), not more negative.

        The w = -1 of the mode vacuum comes from Lorentz invariance, which is
        a symmetry of the REGULARIZED theory, not a property of entanglement alone.
        """
        # Compute w for a range of couplings
        kappas = np.array([0.0, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0])
        w_1d = []
        w_3d = []
        for k in kappas:
            chain = CellChain(N=self.N_cells, mass=self.mass, kappa=k)
            w_1d.append(chain.w_qft_1d())
            w_3d.append(chain.w_qft_3d_isotropic())

        return {
            "answer": "No — entanglement (coupling) makes w MORE positive, not negative.",
            "kappa_values": kappas.tolist(),
            "w_1d": w_1d,
            "w_3d": w_3d,
            "w_1d_monotonic_increasing": all(w_1d[i] <= w_1d[i+1] + 1e-10 for i in range(len(w_1d)-1)),
            "w_3d_monotonic_increasing": all(w_3d[i] <= w_3d[i+1] + 1e-10 for i in range(len(w_3d)-1)),
            "w_3d_bounded_by_one_third": all(w <= 1.0/3.0 + 1e-10 for w in w_3d),
            "w_1d_bounded_by_one": all(w <= 1.0 + 1e-10 for w in w_1d),
            "minimum_w": min(w_3d),
            "all_w_nonnegative_3d": all(w >= -1e-10 for w in w_3d),
            "explanation": (
                "w = V_grad / (3*(V_mass + V_grad)) in 3D. Since V_grad >= 0 "
                "and V_mass >= 0, w >= 0 always. More coupling (more entanglement) "
                "means more gradient energy, which pushes w UPWARD toward 1/3, "
                "not downward toward -1. The w = -1 result requires Lorentz "
                "invariance, not entanglement."
            ),
            "evidence_tier": "[PROVEN] — follows from V_grad >= 0 in the Hamiltonian",
        }


# ===========================================================================
# 4. Summary and Key Results
# ===========================================================================
def w_limits_analysis() -> Dict:
    """
    Analyze the theoretical limits of w for various configurations.
    """
    return {
        "cell_vacuum_product_state": {
            "w": 0,
            "entanglement": "Zero",
            "mechanism": "Virial theorem for independent oscillators",
            "evidence": "[PROVEN]",
        },
        "cell_vacuum_with_coupling_lattice": {
            "w": "0 to 1/3 (3D), 0 to 1 (1D)",
            "entanglement": "Increases with coupling",
            "mechanism": "Gradient energy contributes positive pressure",
            "evidence": "[PROVEN]",
        },
        "mode_vacuum_lorentz_invariant": {
            "w": -1,
            "entanglement": "Maximal (area law)",
            "mechanism": "Lorentz invariance of vacuum forces <T_uv> ∝ g_uv",
            "evidence": "[PROVEN]",
        },
        "lattice_mode_sum_no_renormalization": {
            "w": "Positive, depends on UV cutoff",
            "entanglement": "Area law",
            "mechanism": "Lattice breaks Lorentz invariance, UV modes give positive w",
            "evidence": "[PROVEN]",
        },
        "key_insight": (
            "The relationship between entanglement and w is NOT monotonic in the "
            "expected direction. More entanglement (more coupling/gradient energy) "
            "makes w MORE positive on the lattice. The w = -1 result for the mode "
            "vacuum comes from Lorentz SYMMETRY of the regularized vacuum, not from "
            "entanglement per se. The cell vacuum's w = 0 and the mode vacuum's "
            "w = -1 differ because of Lorentz invariance, not because of entanglement."
        ),
        "resolution_of_the_dichotomy": (
            "The two vacua have different w NOT because of different entanglement, "
            "but because they are defined with different symmetries:\n"
            "- Cell vacuum: defined in position space, breaks Lorentz invariance, w = 0\n"
            "- Mode vacuum: defined in momentum space, preserves Lorentz invariance, w = -1\n"
            "Adding entanglement to the cell vacuum (coupling cells) pushes w toward +1/3 "
            "(radiation), moving it AWAY from -1, not toward it. The only way to get w = -1 "
            "is to have the full Lorentz-invariant vacuum, which requires the continuum limit "
            "with proper regularization."
        ),
    }


def compute_full_investigation(
    mass: float = M_ELECTRON,
    N_cells: int = 100,
    kappa_values: np.ndarray = None,
) -> Dict:
    """
    Run the complete entangled vacuum investigation.
    """
    if kappa_values is None:
        kappa_values = np.array([0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0])

    results = {}

    # 1. Two-cell analysis
    two_cell_results = []
    for kappa in kappa_values:
        tc = TwoCoupledCells(mass=mass, kappa=kappa)
        two_cell_results.append(tc.full_analysis())
    results["two_cell"] = two_cell_results

    # 2. N-cell chain analysis
    chain_results = []
    for kappa in kappa_values:
        chain = CellChain(N=N_cells, mass=mass, kappa=kappa)
        chain_results.append(chain.full_analysis())
    results["chain"] = chain_results

    # 3. QFT connection
    qft = QFTConnection(mass=mass, N_cells=N_cells)
    results["qft_compton"] = qft.w_at_compton_spacing()
    results["qft_lorentz"] = qft.lorentz_invariance_argument()
    results["qft_lattice_positive_w"] = qft.why_lattice_gives_positive_w()
    results["qft_entanglement_negative_w"] = qft.can_entanglement_give_negative_w()

    # 4. Limits analysis
    results["limits"] = w_limits_analysis()

    return results


# ===========================================================================
# CLI Entry Point
# ===========================================================================
if __name__ == "__main__":
    print("=" * 72)
    print("ENTANGLED CELL VACUUM — EQUATION OF STATE INVESTIGATION")
    print("=" * 72)

    results = compute_full_investigation(N_cells=50)

    print("\n--- Two Coupled Cells ---")
    for tc in results["two_cell"]:
        print(f"  kappa={tc['kappa']:.2f}: "
              f"S={tc['entanglement_entropy']:.4f}, "
              f"w_virial={tc['w_virial']:.1f}, "
              f"w_qft={tc['w_qft']:.4f}, "
              f"coupling_frac={tc['coupling_energy_fraction']:.4f}")

    print("\n--- N-Cell Chain (N=50) ---")
    for ch in results["chain"]:
        print(f"  kappa={ch['kappa']:.2f}: "
              f"w_virial={ch['w_virial']:.1f}, "
              f"w_qft_1d={ch['w_qft_1d']:.4f}, "
              f"w_qft_3d={ch['w_qft_3d']:.4f}, "
              f"coupling_frac={ch['coupling_energy_fraction']:.4f}")

    print("\n--- QFT at Compton Spacing (kappa=0.5) ---")
    compton = results["qft_compton"]
    for key, val in compton.items():
        print(f"  {key}: {val}")

    print("\n--- Can Entanglement Give w < 0? ---")
    ent = results["qft_entanglement_negative_w"]
    print(f"  Answer: {ent['answer']}")
    print(f"  All w >= 0 (3D): {ent['all_w_nonnegative_3d']}")
    print(f"  w monotonically increasing with coupling: {ent['w_3d_monotonic_increasing']}")
    print(f"  w bounded by 1/3 (3D): {ent['w_3d_bounded_by_one_third']}")

    print("\n--- Key Results ---")
    limits = results["limits"]
    print(f"  {limits['key_insight']}")

    print("\n" + "=" * 72)
    print("CONCLUSION: Entanglement between cells makes w MORE positive (toward 1/3),")
    print("not more negative (toward -1). The w = -1 of the mode vacuum comes from")
    print("Lorentz symmetry, not from entanglement. The cell vacuum's w = 0 is robust.")
    print("=" * 72)
