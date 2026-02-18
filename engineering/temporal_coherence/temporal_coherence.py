"""
Temporal Coherence Cost: Dark Energy as the Price of Stationarity

Investigates whether dark energy can be understood as the energy cost
of maintaining temporal stationarity (time-independent expectation values)
across all quantum field modes, constrained by Lorentz invariance.

The core question: the cell vacuum oscillates (w=0), the mode vacuum
is stationary (w=-1). Is dark energy the "price" of that stationarity?

Key formulations explored:
1. Per-mode zero-point energy (stationarity cost per oscillator)
2. Full-field mode sum with UV cutoffs
3. Renormalized coherence cost (mode - cell, regularized)
4. Holographic dark energy (Li 2004): rho = 3c^4 / (8 pi G L^2)
5. Margolus-Levitin coherence bound: E_min ~ hbar / tau
6. Vacuum persistence amplitude phase accumulation
7. Information excess (volumetric - holographic) x energy per bit
8. Scale analysis: what temporal cell size gives the right rho?

Result: The holographic formulation naturally reproduces rho_DE ~ H0^2 M_P^2
(= rho_crit), but this is the Friedmann equation, not new physics. Every
other formulation either gives the wrong scale or reduces to the
cosmological constant problem in a different language.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

# ---------------------------------------------------------------------------
# Physical constants (SI) - consistent with project constants.py
# ---------------------------------------------------------------------------
HBAR = 1.054571817e-34      # J s
C = 2.99792458e8            # m/s
G = 6.67430e-11             # m^3 kg^-1 s^-2
KB = 1.380649e-23           # J/K
EV_TO_J = 1.602176634e-19   # J per eV

# Cosmological
H0_SI = 2.195e-18           # Hubble constant in s^-1 (67.4 km/s/Mpc)
HUBBLE_TIME = 1.0 / H0_SI   # ~4.56e17 s
HUBBLE_LENGTH = C / H0_SI   # ~1.37e26 m

# Planck scales
PLANCK_LENGTH = np.sqrt(HBAR * G / C**3)    # ~1.616e-35 m
PLANCK_MASS = np.sqrt(HBAR * C / G)         # ~2.176e-8 kg
PLANCK_ENERGY = PLANCK_MASS * C**2           # ~1.956e9 J

# Observed values
RHO_DE_OBSERVED = 5.96e-10   # J/m^3 (Planck 2018)
RHO_CRIT = 3 * H0_SI**2 * C**2 / (8 * np.pi * G)  # ~7.8e-10 J/m^3

# Reference mass: lightest neutrino (from Two Vacua prediction)
M_NU1_EV = 2.31e-3          # eV
M_NU1_KG = M_NU1_EV * EV_TO_J / C**2


# ===========================================================================
# 1. Per-Mode Stationarity Cost
# ===========================================================================
@dataclass
class PerModeStationarityCost:
    """
    For a single QHO mode at frequency omega:
    - Coherent state |alpha>: E = hbar*omega*(|alpha|^2 + 1/2), oscillates, w=0
    - Ground state |0>: E_0 = hbar*omega/2, stationary, w=0
    - The zero-point energy IS the minimum cost for stationarity.

    Key result: w=0 for BOTH coherent and ground states (virial theorem).
    The per-mode stationarity cost does NOT change the equation of state.
    """

    def zero_point_energy(self, omega: float) -> float:
        """E_0 = hbar * omega / 2 for a single mode."""
        return 0.5 * HBAR * omega

    def coherent_state_energy(self, omega: float, alpha_sq: float) -> float:
        """E = hbar * omega * (|alpha|^2 + 1/2) for coherent state."""
        return HBAR * omega * (alpha_sq + 0.5)

    def stationarity_cost(self, omega: float) -> float:
        """
        Cost of stationarity = zero-point energy.
        This is the minimum energy a mode must have to be time-independent.
        """
        return self.zero_point_energy(omega)

    def w_ground_state(self) -> float:
        """
        Equation of state for ground state of single QHO.
        By the virial theorem: <KE> = <PE>, so <p> = 0, w = 0.
        """
        return 0.0

    def w_coherent_state(self) -> float:
        """
        Equation of state for coherent state of single QHO.
        Virial theorem still applies: time-averaged <p> = 0, w = 0.
        """
        return 0.0

    def summary(self, omega: float, alpha_sq: float = 0.5) -> Dict:
        """Summary of per-mode costs."""
        return {
            "omega_rad_per_s": omega,
            "E_zero_point_J": self.zero_point_energy(omega),
            "E_coherent_J": self.coherent_state_energy(omega, alpha_sq),
            "stationarity_cost_J": self.stationarity_cost(omega),
            "w_ground_state": self.w_ground_state(),
            "w_coherent_state": self.w_coherent_state(),
            "conclusion": "w=0 for both; stationarity cost does not change EOS",
        }


# ===========================================================================
# 2. Full-Field Mode Sum with Cutoff
# ===========================================================================
class FullFieldModeSumCost:
    """
    Sum zero-point energies over all modes up to a UV cutoff.

    rho_mode(Lambda) = (1 / (2*(2pi)^3)) * integral d^3k * omega_k
                     = (1 / (4 pi^2)) * integral_0^Lambda dk * k^2 * omega_k

    where omega_k = sqrt(k^2 c^2 + m^2 c^4/hbar^2) for massive field,
    or omega_k = c*k for massless.

    The integral is UV-divergent (Lambda -> inf). With finite cutoff,
    it gives rho ~ Lambda^4 (dominant) + m^2 Lambda^2 + ...
    """

    def __init__(self, mass_kg: float = 0.0, n_points: int = 10000):
        self.mass_kg = mass_kg
        self.n_points = n_points
        self.omega_mass = mass_kg * C**2 / HBAR if mass_kg > 0 else 0.0

    def omega_k(self, k: float) -> float:
        """Dispersion relation: omega_k = sqrt(c^2 k^2 + (mc^2/hbar)^2)."""
        return np.sqrt(C**2 * k**2 + self.omega_mass**2)

    def mode_sum_density(self, k_cutoff: float) -> float:
        """
        Numerical integration of zero-point energy density.

        rho = (hbar / (4 pi^2)) * integral_0^{k_cutoff} dk * k^2 * omega_k
        """
        k = np.linspace(0, k_cutoff, self.n_points + 1)
        dk = k[1] - k[0]
        omega = np.sqrt(C**2 * k**2 + self.omega_mass**2)
        integrand = k**2 * omega
        # Trapezoidal integration
        integral = np.trapezoid(integrand, k)
        return HBAR * integral / (4.0 * np.pi**2)

    def mode_sum_density_massless_analytic(self, k_cutoff: float) -> float:
        """
        Analytic result for massless field:
        rho = hbar * c * k_cutoff^4 / (16 pi^2)
        """
        return HBAR * C * k_cutoff**4 / (16.0 * np.pi**2)

    def mode_sum_density_massive_approx(self, k_cutoff: float) -> float:
        """
        Leading-order approximation for massive field with k_cutoff >> mc/hbar:
        rho ~ hbar * c * k_cutoff^4 / (16 pi^2)
            + hbar * (mc/hbar)^2 * c * k_cutoff^2 / (16 pi^2) + ...

        The mass correction is subleading for large cutoff.
        """
        k_m = self.mass_kg * C / HBAR
        return (HBAR * C * k_cutoff**4 / (16.0 * np.pi**2)
                + HBAR * k_m**2 * C * k_cutoff**2 / (16.0 * np.pi**2))

    def compton_cutoff_density(self) -> float:
        """
        Mode sum with cutoff at the Compton scale: k_cutoff = mc/hbar.

        rho_mode(Lambda_C) = (hbar / (4 pi^2)) * int_0^{mc/hbar} dk * k^2 * omega_k

        For a massive field at its own Compton cutoff, this is O(m^4 c^5/hbar^3).
        """
        if self.mass_kg <= 0:
            return 0.0
        k_compton = self.mass_kg * C / HBAR
        return self.mode_sum_density(k_compton)

    def planck_cutoff_density(self) -> float:
        """Mode sum with Planck cutoff: k_cutoff = 1/l_P."""
        k_planck = 1.0 / PLANCK_LENGTH
        return self.mode_sum_density_massless_analytic(k_planck)


# ===========================================================================
# 3. Renormalized Coherence Cost (Mode - Cell)
# ===========================================================================
class RenormalizedCoherenceCost:
    """
    The "coherence cost" = difference between mode vacuum and cell vacuum.

    Cell vacuum: rho_cell = m^4 c^5 / hbar^3  (finite, w=0)
    Mode vacuum: rho_mode = sum of zero-point energies (infinite without cutoff)

    With Compton cutoff:
    Delta_rho = rho_mode(Lambda_C) - rho_cell

    This difference is cutoff-dependent and does NOT resolve the CC problem.
    In Wald's renormalization framework, the vacuum energy has an
    AMBIGUITY proportional to g_uv -- adding any constant to rho is allowed.
    The "coherence cost" is an undetermined parameter.

    This is the cosmological constant problem restated.
    """

    def __init__(self, mass_kg: float):
        self.mass_kg = mass_kg
        self.mode_sum = FullFieldModeSumCost(mass_kg)

    def cell_vacuum_density(self) -> float:
        """rho_cell = m^4 c^5 / hbar^3."""
        return self.mass_kg**4 * C**5 / HBAR**3

    def mode_vacuum_density_compton_cutoff(self) -> float:
        """Mode vacuum with Compton cutoff."""
        return self.mode_sum.compton_cutoff_density()

    def raw_coherence_cost(self) -> float:
        """
        Delta_rho = rho_mode(Lambda_C) - rho_cell

        This is the raw (unrenormalized) cost of stationarity for the
        full field vs the cell vacuum.
        """
        return self.mode_vacuum_density_compton_cutoff() - self.cell_vacuum_density()

    def raw_coherence_cost_ratio(self) -> float:
        """Ratio rho_mode / rho_cell at Compton cutoff."""
        rho_cell = self.cell_vacuum_density()
        if rho_cell == 0:
            return float('inf')
        return self.mode_vacuum_density_compton_cutoff() / rho_cell

    def wald_ambiguity_statement(self) -> Dict:
        """
        In Wald's framework, the renormalized stress tensor has:
        <T_uv>_ren = <T_uv>_finite + C * g_uv

        where C is an undetermined constant (the cosmological constant).
        The "coherence cost" is absorbed into this ambiguity.
        """
        return {
            "framework": "Wald renormalization (1994)",
            "result": "Vacuum energy has undetermined g_uv ambiguity",
            "implication": "Coherence cost is a free parameter, not predicted",
            "verdict": "RESTATES the cosmological constant problem",
        }

    def summary(self) -> Dict:
        rho_cell = self.cell_vacuum_density()
        rho_mode = self.mode_vacuum_density_compton_cutoff()
        delta = self.raw_coherence_cost()
        ratio = self.raw_coherence_cost_ratio()
        return {
            "rho_cell_J_per_m3": rho_cell,
            "rho_mode_compton_cutoff_J_per_m3": rho_mode,
            "delta_rho_J_per_m3": delta,
            "ratio_mode_to_cell": ratio,
            "delta_over_observed": delta / RHO_DE_OBSERVED if delta != 0 else 0,
            "wald": self.wald_ambiguity_statement(),
        }


# ===========================================================================
# 4. Holographic Dark Energy
# ===========================================================================
class HolographicDarkEnergy:
    """
    Holographic dark energy (Li 2004): rho_DE = 3 c^4 / (8 pi G L^2)

    where L is an IR length scale (future event horizon, Hubble radius, etc.)

    In SI units, the Friedmann equation is H^2 = 8 pi G rho / (3 c^2),
    so rho_crit = 3 H0^2 c^2 / (8 pi G).

    With L = c/H0 (Hubble radius):
    rho_holo = 3 c^4 / (8 pi G (c/H0)^2) = 3 H0^2 c^2 / (8 pi G) = rho_crit

    This gives the RIGHT order of magnitude and w ~ -1.

    Physical interpretation: the maximum vacuum energy in a region of
    size L is bounded by the largest black hole that fits (Bekenstein bound).
    """

    @staticmethod
    def holographic_density(L: float) -> float:
        """rho = 3 c^4 / (8 pi G L^2) in SI units [J/m^3]."""
        return 3.0 * C**4 / (8.0 * np.pi * G * L**2)

    @staticmethod
    def holographic_density_hubble() -> float:
        """rho with L = c/H0 = Hubble radius. Equals rho_crit."""
        return HolographicDarkEnergy.holographic_density(HUBBLE_LENGTH)

    @staticmethod
    def holographic_density_equals_critical() -> Dict:
        """
        Verify: rho_holo(L = c/H0) = 3 c^4 / (8piG(c/H0)^2) = 3 H0^2 c^2 / (8piG) = rho_crit.

        This is just the Friedmann equation for a flat universe!
        Not new physics -- a tautology.
        """
        rho_holo = HolographicDarkEnergy.holographic_density_hubble()
        ratio = rho_holo / RHO_CRIT
        return {
            "rho_holographic_J_per_m3": rho_holo,
            "rho_critical_J_per_m3": RHO_CRIT,
            "ratio": ratio,
            "is_friedmann": abs(ratio - 1.0) < 1e-6,
            "verdict": "Holographic DE with Hubble radius IS the Friedmann equation",
        }

    @staticmethod
    def holographic_density_future_horizon(omega_de: float = 0.7) -> float:
        """
        With L = future event horizon (depends on expansion history).

        For de Sitter: L_future ~ c/H0 * 1/sqrt(Omega_DE)
        Approximate: rho ~ Omega_DE * rho_crit

        Li (2004) showed this gives w ~ -1 with the right coefficient.
        """
        L_future = HUBBLE_LENGTH / np.sqrt(omega_de)
        return HolographicDarkEnergy.holographic_density(L_future)

    @staticmethod
    def comparison_with_observed() -> Dict:
        """Compare holographic density with observed dark energy."""
        rho_hubble = HolographicDarkEnergy.holographic_density_hubble()
        rho_future = HolographicDarkEnergy.holographic_density_future_horizon(0.7)
        return {
            "rho_holographic_hubble_J_per_m3": rho_hubble,
            "rho_holographic_future_J_per_m3": rho_future,
            "rho_observed_J_per_m3": RHO_DE_OBSERVED,
            "ratio_hubble_to_observed": rho_hubble / RHO_DE_OBSERVED,
            "ratio_future_to_observed": rho_future / RHO_DE_OBSERVED,
        }


# ===========================================================================
# 5. Margolus-Levitin Coherence Bound
# ===========================================================================
class MargolusLevitinBound:
    """
    The Margolus-Levitin theorem: a quantum system with energy E above
    the ground state can transition between orthogonal states at most
    at rate pi*E / (2*hbar).

    For temporal coherence over timescale tau:
    E_min = pi * hbar / (2 * tau)

    Applied to the Hubble time:
    E_min = pi * hbar / (2 * T_H) ~ pi * hbar * H0 / 2

    The minimum energy DENSITY for coherence over Hubble volume + time:
    rho_ML = E_min / V_Hubble = pi * hbar * H0 / (2 * (c/H0)^3)
           = pi * hbar * H0^4 / (2 * c^3)

    This is MANY orders of magnitude too small to explain dark energy.
    """

    @staticmethod
    def min_energy_for_timescale(tau: float) -> float:
        """E_min = pi * hbar / (2 * tau)."""
        return np.pi * HBAR / (2.0 * tau)

    @staticmethod
    def min_energy_hubble_time() -> float:
        """E_min for coherence over one Hubble time."""
        return MargolusLevitinBound.min_energy_for_timescale(HUBBLE_TIME)

    @staticmethod
    def min_density_hubble() -> float:
        """
        rho_ML = E_min / V_Hubble
               = pi * hbar * H0^4 / (2 * c^3)
        """
        V_hubble = (4.0 / 3.0) * np.pi * HUBBLE_LENGTH**3
        E_min = MargolusLevitinBound.min_energy_hubble_time()
        return E_min / V_hubble

    @staticmethod
    def min_density_analytic() -> float:
        """Analytic form: pi * hbar * H0^4 / (2 * c^3)."""
        return np.pi * HBAR * H0_SI**4 / (2.0 * C**3)

    @staticmethod
    def ratio_to_observed() -> float:
        """How far off is this from the observed dark energy density?"""
        return MargolusLevitinBound.min_density_analytic() / RHO_DE_OBSERVED

    @staticmethod
    def log10_ratio_to_observed() -> float:
        """Log10 of ratio to observed."""
        ratio = MargolusLevitinBound.ratio_to_observed()
        return np.log10(abs(ratio)) if ratio != 0 else float('-inf')

    @staticmethod
    def summary() -> Dict:
        rho_ml = MargolusLevitinBound.min_density_analytic()
        return {
            "E_min_hubble_J": MargolusLevitinBound.min_energy_hubble_time(),
            "rho_ML_J_per_m3": rho_ml,
            "rho_observed_J_per_m3": RHO_DE_OBSERVED,
            "ratio_to_observed": MargolusLevitinBound.ratio_to_observed(),
            "log10_ratio": MargolusLevitinBound.log10_ratio_to_observed(),
            "verdict": "Too small by ~120 orders of magnitude",
        }


# ===========================================================================
# 6. Vacuum Persistence Amplitude
# ===========================================================================
class VacuumPersistenceAmplitude:
    """
    The vacuum persistence amplitude:
    <0|e^{-iHT/hbar}|0> = e^{-iE_0 T/hbar}

    Phase accumulation rate = E_0 / hbar.

    For temporal coherence, phases must be well-defined up to
    the Hubble time T_H = 1/H0.

    Phase uncertainty: Delta_phi ~ E_0 * T_H / hbar must be >> 2 pi
    for the phase to "mean something."

    The minimum energy density for a well-defined phase:
    rho_min ~ hbar / (T_H * V_Hubble) ~ hbar * H0^4 / c^3

    This is the same scale as Margolus-Levitin -- far too small.
    """

    @staticmethod
    def phase_accumulation_rate(E0: float) -> float:
        """Phase rate = E_0 / hbar in rad/s."""
        return E0 / HBAR

    @staticmethod
    def total_phase_hubble(E0: float) -> float:
        """Total phase accumulated over Hubble time."""
        return E0 * HUBBLE_TIME / HBAR

    @staticmethod
    def min_energy_for_one_radian() -> float:
        """Minimum energy to accumulate 1 radian over Hubble time."""
        return HBAR / HUBBLE_TIME  # = hbar * H0

    @staticmethod
    def min_density_from_phase() -> float:
        """
        rho_min = hbar * H0 / V_Hubble = hbar * H0^4 / c^3

        (Up to factors of pi, same as Margolus-Levitin.)
        """
        return HBAR * H0_SI**4 / C**3

    @staticmethod
    def ratio_to_observed() -> float:
        return VacuumPersistenceAmplitude.min_density_from_phase() / RHO_DE_OBSERVED

    @staticmethod
    def summary() -> Dict:
        rho_min = VacuumPersistenceAmplitude.min_density_from_phase()
        return {
            "hbar_H0_J": HBAR * H0_SI,
            "rho_phase_min_J_per_m3": rho_min,
            "rho_observed_J_per_m3": RHO_DE_OBSERVED,
            "ratio_to_observed": VacuumPersistenceAmplitude.ratio_to_observed(),
            "log10_ratio": np.log10(abs(rho_min / RHO_DE_OBSERVED)),
            "verdict": "Too small by ~120 orders of magnitude (same as ML bound)",
        }


# ===========================================================================
# 7. Information Excess: Volumetric - Holographic
# ===========================================================================
class InformationExcess:
    """
    The cell vacuum stores information volumetrically:
    I_vol ~ V / lambda_C^3

    The holographic bound limits information to:
    I_bdy ~ A / (4 l_P^2)

    where A is the boundary area, l_P is the Planck length.

    For the neutrino mass (lambda_C ~ 85 um), the Compton cells are
    macroscopic and I_vol << I_bdy for a Hubble-sized region. The
    holographic bound is NOT saturated. Delta_I = I_vol - I_bdy < 0.

    The "information deficit" D = I_bdy - I_vol represents unused
    holographic capacity. One could hypothesize that this deficit
    has an energy cost, but the resulting density does not match rho_DE.

    If each deficit bit has an energy cost E_bit ~ hbar * H0:
    rho_deficit = D * E_bit / V

    Question: does this match rho_DE?
    """

    def __init__(self, mass_kg: float, region_size: float = None):
        """
        mass_kg: determines the Compton wavelength (cell size)
        region_size: radius of the region (default: Hubble radius)
        """
        self.mass_kg = mass_kg
        self.R = region_size if region_size is not None else HUBBLE_LENGTH
        self.lambda_C = HBAR / (mass_kg * C)

    def volume(self) -> float:
        """Volume of the spherical region."""
        return (4.0 / 3.0) * np.pi * self.R**3

    def area(self) -> float:
        """Surface area of the spherical region."""
        return 4.0 * np.pi * self.R**2

    def volumetric_information(self) -> float:
        """I_vol = V / lambda_C^3 (number of cells)."""
        return self.volume() / self.lambda_C**3

    def holographic_information(self) -> float:
        """I_bdy = A / (4 l_P^2) (Bekenstein-Hawking bound)."""
        return self.area() / (4.0 * PLANCK_LENGTH**2)

    def information_excess(self) -> float:
        """Delta_I = I_vol - I_bdy. Negative when holographic bound not saturated."""
        return self.volumetric_information() - self.holographic_information()

    def information_deficit(self) -> float:
        """D = I_bdy - I_vol. Positive when holographic bound not saturated."""
        return self.holographic_information() - self.volumetric_information()

    def energy_per_bit_hubble(self) -> float:
        """E_bit = hbar * H0 (Margolus-Levitin for Hubble time)."""
        return HBAR * H0_SI

    def energy_per_bit_temperature(self) -> float:
        """
        E_bit = kB * T_dS where T_dS = hbar * H0 / (2 pi kB)
        is the de Sitter temperature.

        E_bit = hbar * H0 / (2 pi) ~ same scale as ML bound.
        """
        return HBAR * H0_SI / (2.0 * np.pi)

    def excess_energy_density_ml(self) -> float:
        """
        rho = |Delta_I| * E_bit(ML) / V

        Where E_bit = hbar * H0.
        Uses absolute value since Delta_I may be negative (deficit).
        """
        delta_I = abs(self.information_excess())
        E_bit = self.energy_per_bit_hubble()
        V = self.volume()
        return delta_I * E_bit / V

    def excess_energy_density_ds(self) -> float:
        """
        rho with de Sitter temperature for E_bit.
        Uses absolute value of information difference.
        """
        delta_I = abs(self.information_excess())
        E_bit = self.energy_per_bit_temperature()
        V = self.volume()
        return delta_I * E_bit / V

    def deficit_energy_density_ml(self) -> float:
        """
        rho_deficit = D * E_bit(ML) / V where D = I_bdy - I_vol.
        Only meaningful when D > 0 (holographic bound not saturated).
        """
        D = self.information_deficit()
        E_bit = self.energy_per_bit_hubble()
        V = self.volume()
        return D * E_bit / V

    def information_ratio(self) -> float:
        """I_vol / I_bdy -- how much the volumetric exceeds holographic."""
        I_bdy = self.holographic_information()
        if I_bdy == 0:
            return float('inf')
        return self.volumetric_information() / I_bdy

    def summary(self) -> Dict:
        I_vol = self.volumetric_information()
        I_bdy = self.holographic_information()
        delta_I = self.information_excess()
        rho_ml = self.excess_energy_density_ml()
        rho_ds = self.excess_energy_density_ds()
        is_deficit = delta_I < 0

        return {
            "region_radius_m": self.R,
            "lambda_C_m": self.lambda_C,
            "I_volumetric": I_vol,
            "I_holographic": I_bdy,
            "log10_I_vol": np.log10(I_vol) if I_vol > 0 else float('-inf'),
            "log10_I_bdy": np.log10(I_bdy) if I_bdy > 0 else float('-inf'),
            "I_excess": delta_I,
            "holographic_not_saturated": is_deficit,
            "I_ratio_vol_to_bdy": self.information_ratio(),
            "rho_abs_diff_ML_J_per_m3": rho_ml,
            "rho_abs_diff_dS_J_per_m3": rho_ds,
            "rho_observed_J_per_m3": RHO_DE_OBSERVED,
            "ratio_ML_to_observed": rho_ml / RHO_DE_OBSERVED,
            "ratio_dS_to_observed": rho_ds / RHO_DE_OBSERVED,
        }


# ===========================================================================
# 8. Scale Analysis: What tau gives rho_DE?
# ===========================================================================
class ScaleAnalysis:
    """
    If rho_DE is a "coherence cost" at some temporal scale tau,
    what is tau?

    Various ansatze:
    (a) rho = hbar / (tau * V_tau) where V_tau = (c*tau)^3
        => rho = hbar / (c^3 * tau^4)
        => tau = (hbar / (c^3 * rho))^{1/4}

    (b) rho = hbar * omega / V_cell where omega = 1/tau, V_cell = (c/omega)^3
        => rho = hbar * omega^4 / c^3
        => omega = (rho * c^3 / hbar)^{1/4}
        This is equivalent to m = (rho * hbar^3 / c^5)^{1/4}
        i.e., the cell vacuum formula inverted.

    (c) Holographic: rho ~ c^2 / (G * L^2)
        => L = c / sqrt(8 pi G rho / 3)
        For rho = rho_DE, L ~ Hubble radius

    Result: ansatz (b) gives omega ~ mc^2/hbar with m ~ 2.31 meV
    (the neutrino mass). This is just the cell vacuum formula inverted --
    circular if we take rho = rho_cell as the definition.
    """

    @staticmethod
    def tau_from_ansatz_a(rho: float) -> float:
        """tau = (hbar / (c^3 * rho))^{1/4}."""
        return (HBAR / (C**3 * rho))**0.25

    @staticmethod
    def omega_from_ansatz_b(rho: float) -> float:
        """omega = (rho * c^3 / hbar)^{1/4}. Same as Compton frequency."""
        return (rho * C**3 / HBAR)**0.25

    @staticmethod
    def mass_from_ansatz_b(rho: float) -> float:
        """m = (rho * hbar^3 / c^5)^{1/4}. The cell vacuum formula inverted."""
        return (rho * HBAR**3 / C**5)**0.25

    @staticmethod
    def L_from_holographic(rho: float) -> float:
        """L = c^2 / sqrt(8 pi G rho / 3) from rho = 3c^4/(8piGL^2)."""
        return C**2 / np.sqrt(8.0 * np.pi * G * rho / 3.0)

    @staticmethod
    def analyze_observed_de() -> Dict:
        """What scales correspond to the observed dark energy density?"""
        rho = RHO_DE_OBSERVED

        tau_a = ScaleAnalysis.tau_from_ansatz_a(rho)
        omega_b = ScaleAnalysis.omega_from_ansatz_b(rho)
        mass_b = ScaleAnalysis.mass_from_ansatz_b(rho)
        mass_b_eV = mass_b * C**2 / EV_TO_J
        L_holo = ScaleAnalysis.L_from_holographic(rho)

        return {
            "rho_target_J_per_m3": rho,
            "ansatz_a": {
                "tau_s": tau_a,
                "tau_description": "hbar/(c^3 rho)^{1/4}",
                "corresponds_to": f"tau = {tau_a:.3e} s",
            },
            "ansatz_b": {
                "omega_rad_per_s": omega_b,
                "mass_kg": mass_b,
                "mass_eV": mass_b_eV,
                "mass_meV": mass_b_eV * 1e3,
                "is_neutrino_mass": abs(mass_b_eV - M_NU1_EV) / M_NU1_EV < 0.1,
                "note": "This IS the cell vacuum formula inverted -- circular",
            },
            "ansatz_c_holographic": {
                "L_m": L_holo,
                "L_over_Hubble_radius": L_holo / HUBBLE_LENGTH,
                "note": "L ~ Hubble radius -- just Friedmann equation",
            },
        }


# ===========================================================================
# 9. Master Comparison Table
# ===========================================================================
def compute_all_densities(mass_kg: float = M_NU1_KG) -> Dict:
    """
    Compute all energy density estimates and compare with observed rho_DE.

    Returns a dictionary with each formulation's density and ratio to observed.
    """
    results = {}

    # Cell vacuum
    rho_cell = mass_kg**4 * C**5 / HBAR**3
    results["cell_vacuum"] = {
        "rho_J_per_m3": rho_cell,
        "ratio_to_observed": rho_cell / RHO_DE_OBSERVED,
        "w": 0,
        "description": "m^4 c^5 / hbar^3 (cell vacuum, w=0)",
    }

    # Mode vacuum with Compton cutoff
    mode_sum = FullFieldModeSumCost(mass_kg)
    rho_mode_compton = mode_sum.compton_cutoff_density()
    results["mode_vacuum_compton"] = {
        "rho_J_per_m3": rho_mode_compton,
        "ratio_to_observed": rho_mode_compton / RHO_DE_OBSERVED,
        "w": -1,
        "description": "Mode sum, Compton cutoff (w=-1 by Lorentz inv.)",
    }

    # Mode vacuum with Planck cutoff
    rho_mode_planck = mode_sum.planck_cutoff_density()
    results["mode_vacuum_planck"] = {
        "rho_J_per_m3": rho_mode_planck,
        "ratio_to_observed": rho_mode_planck / RHO_DE_OBSERVED,
        "w": -1,
        "description": "Mode sum, Planck cutoff -- the 10^120 disaster",
    }

    # Holographic (Hubble radius)
    rho_holo = HolographicDarkEnergy.holographic_density_hubble()
    results["holographic_hubble"] = {
        "rho_J_per_m3": rho_holo,
        "ratio_to_observed": rho_holo / RHO_DE_OBSERVED,
        "w": -1,
        "description": "3c^2/(8 pi G L^2), L=c/H0 -- equals rho_crit (Friedmann eq.)",
    }

    # Holographic (future horizon)
    rho_holo_f = HolographicDarkEnergy.holographic_density_future_horizon(0.7)
    results["holographic_future"] = {
        "rho_J_per_m3": rho_holo_f,
        "ratio_to_observed": rho_holo_f / RHO_DE_OBSERVED,
        "w": "~-1",
        "description": "Holographic with future event horizon (Li 2004)",
    }

    # Margolus-Levitin
    rho_ml = MargolusLevitinBound.min_density_analytic()
    results["margolus_levitin"] = {
        "rho_J_per_m3": rho_ml,
        "ratio_to_observed": rho_ml / RHO_DE_OBSERVED,
        "log10_ratio": np.log10(rho_ml / RHO_DE_OBSERVED),
        "w": "N/A (bound, not EOS)",
        "description": "pi hbar H0^4 / (2 c^3) -- minimum for temporal coherence",
    }

    # Vacuum persistence phase
    rho_phase = VacuumPersistenceAmplitude.min_density_from_phase()
    results["vacuum_persistence"] = {
        "rho_J_per_m3": rho_phase,
        "ratio_to_observed": rho_phase / RHO_DE_OBSERVED,
        "log10_ratio": np.log10(rho_phase / RHO_DE_OBSERVED),
        "w": "N/A",
        "description": "hbar H0^4 / c^3 -- phase coherence minimum",
    }

    # Information difference (ML energy per bit)
    # Note: for neutrino mass, I_bdy >> I_vol (holographic NOT saturated)
    # so Delta_I < 0; we use |Delta_I| for the energy density.
    info = InformationExcess(mass_kg)
    rho_info_ml = info.excess_energy_density_ml()
    results["information_diff_ml"] = {
        "rho_J_per_m3": rho_info_ml,
        "ratio_to_observed": rho_info_ml / RHO_DE_OBSERVED,
        "w": "undetermined",
        "description": "|I_vol - I_bdy| * hbar*H0 / V (deficit for nu mass)",
    }

    # Information difference (de Sitter temperature)
    rho_info_ds = info.excess_energy_density_ds()
    results["information_diff_ds"] = {
        "rho_J_per_m3": rho_info_ds,
        "ratio_to_observed": rho_info_ds / RHO_DE_OBSERVED,
        "w": "undetermined",
        "description": "|I_vol - I_bdy| * kT_dS / V (deficit for nu mass)",
    }

    # Observed
    results["observed"] = {
        "rho_J_per_m3": RHO_DE_OBSERVED,
        "ratio_to_observed": 1.0,
        "w": -1.03,  # Planck 2018 best fit
        "description": "Observed dark energy (Planck 2018)",
    }

    # Critical density
    results["critical"] = {
        "rho_J_per_m3": RHO_CRIT,
        "ratio_to_observed": RHO_CRIT / RHO_DE_OBSERVED,
        "w": "N/A",
        "description": "Critical density 3H0^2 c^2 / (8 pi G)",
    }

    return results


def print_comparison_table(results: Dict = None):
    """Print a formatted comparison table."""
    if results is None:
        results = compute_all_densities()

    print("=" * 90)
    print("TEMPORAL COHERENCE COST: ENERGY DENSITY COMPARISON")
    print("=" * 90)
    print(f"{'Formulation':<30} {'rho (J/m^3)':>14} {'ratio to obs':>14} {'w':>8}")
    print("-" * 90)

    for key, val in results.items():
        rho = val["rho_J_per_m3"]
        ratio = val["ratio_to_observed"]
        w = val["w"]
        desc = val.get("description", key)
        rho_str = f"{rho:.3e}" if isinstance(rho, float) else str(rho)
        ratio_str = f"{ratio:.3e}" if isinstance(ratio, float) else str(ratio)
        w_str = f"{w:.2f}" if isinstance(w, (int, float)) else str(w)
        print(f"{key:<30} {rho_str:>14} {ratio_str:>14} {w_str:>8}")

    print("=" * 90)


# ===========================================================================
# Entry point
# ===========================================================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEMPORAL COHERENCE COST ANALYSIS")
    print("=" * 70)

    # 1. Per-mode
    print("\n--- 1. Per-Mode Stationarity Cost ---")
    pmc = PerModeStationarityCost()
    omega_nu = M_NU1_KG * C**2 / HBAR
    s = pmc.summary(omega_nu)
    for k, v in s.items():
        print(f"  {k}: {v}")

    # 2. Full-field mode sum
    print("\n--- 2. Full-Field Mode Sum ---")
    fms = FullFieldModeSumCost(M_NU1_KG)
    rho_compton = fms.compton_cutoff_density()
    rho_planck = fms.planck_cutoff_density()
    print(f"  rho(Compton cutoff) = {rho_compton:.3e} J/m^3")
    print(f"  rho(Planck cutoff)  = {rho_planck:.3e} J/m^3")

    # 3. Renormalized coherence cost
    print("\n--- 3. Renormalized Coherence Cost ---")
    rcc = RenormalizedCoherenceCost(M_NU1_KG)
    s = rcc.summary()
    for k, v in s.items():
        print(f"  {k}: {v}")

    # 4. Holographic
    print("\n--- 4. Holographic Dark Energy ---")
    s = HolographicDarkEnergy.comparison_with_observed()
    for k, v in s.items():
        print(f"  {k}: {v}")
    proof = HolographicDarkEnergy.holographic_density_equals_critical()
    for k, v in proof.items():
        print(f"  {k}: {v}")

    # 5. Margolus-Levitin
    print("\n--- 5. Margolus-Levitin Bound ---")
    s = MargolusLevitinBound.summary()
    for k, v in s.items():
        print(f"  {k}: {v}")

    # 6. Vacuum persistence
    print("\n--- 6. Vacuum Persistence Amplitude ---")
    s = VacuumPersistenceAmplitude.summary()
    for k, v in s.items():
        print(f"  {k}: {v}")

    # 7. Information excess
    print("\n--- 7. Information Excess ---")
    ie = InformationExcess(M_NU1_KG)
    s = ie.summary()
    for k, v in s.items():
        print(f"  {k}: {v}")

    # 8. Scale analysis
    print("\n--- 8. Scale Analysis ---")
    s = ScaleAnalysis.analyze_observed_de()
    for k, v in s.items():
        print(f"  {k}: {v}")

    # 9. Master comparison
    print("\n")
    print_comparison_table()
