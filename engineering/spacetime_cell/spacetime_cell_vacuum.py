"""
4D Spacetime Cell Vacuum Construction

Investigates whether extending the cell vacuum from a 3D spatial tiling
to a 4D spacetime tiling (with temporal cells of size tau_C = 1/omega)
changes the equation of state from w=0.

Four approaches are analyzed:
1. Phase-randomized (time-averaged) cell state
2. Temporal Casimir effect from temporal boundaries
3. Cosmological temporal cell (Hubble-scale temporal boundaries)
4. Euclidean path integral with temporal periodicity

Key finding: None of these approaches changes w from 0 to -1.
The 4D cell construction is either equivalent to the 3D one (Approach 1),
reproduces standard QHO quantization (Approach 2), gives tiny corrections
(Approach 4), or requires external input like expansion rate (Approach 3).
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from scipy.special import factorial

# ---------------------------------------------------------------------------
# Physical constants (SI)
# ---------------------------------------------------------------------------
HBAR = 1.054571817e-34      # J s
C = 2.99792458e8            # m/s
G = 6.67430e-11             # m^3 kg^-1 s^-2
K_B = 1.380649e-23          # J/K
EV_TO_J = 1.602176634e-19   # J per eV
H0_SI = 2.195e-18           # Hubble constant in s^-1 (67.4 km/s/Mpc)

# Lightest neutrino mass estimate (normal hierarchy, lightest ~ 0)
# Use a representative value for the cell vacuum
M_NEUTRINO = 0.05 * EV_TO_J / C**2   # ~50 meV in kg (upper bound)
M_ELECTRON = 9.1093837015e-31          # kg


# ===========================================================================
# 1. Phase-Randomized (Time-Averaged) Cell State
# ===========================================================================
@dataclass
class PhaseRandomizedState:
    """
    Time-averaging a coherent state |alpha> over one oscillation period
    produces a phase-randomized mixed state diagonal in the Fock basis:

        rho_avg = sum_n P(n) |n><n|

    where P(n) = e^{-|alpha|^2} |alpha|^{2n} / n!  (Poisson distribution)

    For |alpha|^2 = 1/2 (the cell vacuum):
        P(0) = e^{-1/2} ~ 0.6065
        P(1) = e^{-1/2}/2 ~ 0.3033
        P(2) = e^{-1/2}/8 ~ 0.0758
        ...

    This state has NONZERO von Neumann entropy (it is mixed).
    However, since each Fock state |n> has w=0, the mixture also has w=0.
    """
    alpha_squared: float = 0.5  # |alpha|^2

    def poisson_weight(self, n: int) -> float:
        """P(n) = e^{-|alpha|^2} |alpha|^{2n} / n!"""
        lam = self.alpha_squared
        return np.exp(-lam) * lam**n / factorial(n, exact=True)

    def poisson_weights(self, n_max: int = 20) -> np.ndarray:
        """Array of Poisson weights P(0), P(1), ..., P(n_max)."""
        ns = np.arange(n_max + 1)
        lam = self.alpha_squared
        # Use log to avoid overflow for large n
        log_weights = -lam + ns * np.log(lam) - np.array(
            [sum(np.log(np.arange(1, k + 1))) if k > 0 else 0.0 for k in ns]
        )
        return np.exp(log_weights)

    def verify_normalization(self, n_max: int = 50) -> float:
        """sum P(n) should equal 1."""
        weights = self.poisson_weights(n_max)
        return float(np.sum(weights))

    def von_neumann_entropy(self, n_max: int = 50) -> float:
        """
        S = -sum_n P(n) ln P(n)

        For the coherent state (pure state), S = 0.
        For the phase-randomized state, S > 0.
        """
        weights = self.poisson_weights(n_max)
        # Filter out zeros to avoid log(0)
        nonzero = weights[weights > 0]
        return float(-np.sum(nonzero * np.log(nonzero)))

    def mean_occupation(self, n_max: int = 50) -> float:
        """<n> = |alpha|^2"""
        weights = self.poisson_weights(n_max)
        ns = np.arange(len(weights))
        return float(np.sum(ns * weights))

    def energy_density_per_cell(self, mass: float, n_max: int = 50) -> float:
        """
        <E> / V_cell = sum_n P(n) * hbar*omega*(n+1/2) / V_cell

        where V_cell = lambda_C^3 = (hbar/(mc))^3.

        <E> = hbar*omega*(<n> + 1/2) = hbar*omega*(|alpha|^2 + 1/2)

        This is IDENTICAL to the coherent state energy — time-averaging
        does not change the mean energy.
        """
        omega = mass * C**2 / HBAR
        lambda_C = HBAR / (mass * C)
        V_cell = lambda_C**3
        mean_E = HBAR * omega * (self.alpha_squared + 0.5)
        return mean_E / V_cell

    def fock_state_w(self, n: int) -> float:
        """
        Equation of state for Fock state |n>.

        For a QHO Fock state:
        - E_n = hbar*omega*(n + 1/2)
        - <T> = <V> = E_n/2  (virial theorem for energy eigenstates)
        - p = (<T> - <V>)/V = 0

        Therefore w = p/rho = 0 for ALL Fock states.
        """
        # The kinetic and potential energies are equal for any eigenstate
        # of the harmonic oscillator, by the virial theorem.
        return 0.0

    def equation_of_state_w(self, n_max: int = 50) -> float:
        """
        w for the phase-randomized mixed state.

        Since w = 0 for each Fock state |n>, and the mixed state is
        rho = sum_n P(n) |n><n|, the total w is:

        w = sum_n P(n) * w_n / sum_n P(n) * rho_n  ... but all w_n = 0.

        More precisely:
        <p> = sum_n P(n) * p_n = sum_n P(n) * 0 = 0
        <rho> = sum_n P(n) * rho_n > 0
        w = 0/rho = 0

        Time-averaging does NOT change w.
        """
        return 0.0

    def stress_energy_mixed_state(self, mass: float, n_max: int = 50) -> Dict:
        """
        Compute <T_mu_nu> for the phase-randomized state.

        For each Fock state |n>:
            rho_n = hbar*omega*(n+1/2) / V_cell
            p_n = 0

        Mixed state:
            <rho> = sum P(n) * rho_n = hbar*omega*(<n>+1/2) / V_cell
            <p> = 0
            w = 0
        """
        omega = mass * C**2 / HBAR
        lambda_C = HBAR / (mass * C)
        V_cell = lambda_C**3

        weights = self.poisson_weights(n_max)
        ns = np.arange(len(weights))

        # Energy per Fock state
        E_n = HBAR * omega * (ns + 0.5)
        rho_n = E_n / V_cell

        # Weighted averages
        avg_rho = float(np.sum(weights * rho_n))
        avg_p = 0.0  # Each Fock state has p=0

        return {
            "energy_density": avg_rho,
            "pressure": avg_p,
            "w": 0.0,
            "von_neumann_entropy": self.von_neumann_entropy(n_max),
            "mean_occupation": float(np.sum(ns * weights)),
        }


# ===========================================================================
# 2. Temporal Casimir Effect
# ===========================================================================
@dataclass
class TemporalCasimir:
    """
    Analyze the effect of temporal boundaries separated by tau.

    In the standard (spatial) Casimir effect, two plates at distance L
    modify the mode spectrum, producing an energy shift:
        E_Casimir ~ -pi^2 hbar c / (720 L^3)  per unit area

    By analogy, temporal "boundaries" at intervals tau quantize the
    energy spectrum. For a massive scalar field with mass m:
    - Free spectrum: E = sqrt(k^2 + m^2) (continuous k)
    - With temporal period tau: omega_n = 2*pi*n/tau (discrete)

    If tau = 2*pi/omega_C (one Compton period):
        omega_n = n * omega_C
    This is EXACTLY the QHO spectrum E_n = n*hbar*omega_C (up to zero-point).

    Therefore: temporal cells of Compton period size reproduce the
    standard quantization and add nothing new.
    """
    mass: float  # kg

    @property
    def omega_compton(self) -> float:
        """Compton angular frequency."""
        return self.mass * C**2 / HBAR

    @property
    def tau_compton(self) -> float:
        """Compton period tau_C = 2*pi/omega."""
        return 2 * np.pi / self.omega_compton

    @property
    def lambda_compton(self) -> float:
        """Compton wavelength lambda_C = hbar/(mc)."""
        return HBAR / (self.mass * C)

    def temporal_mode_energies(self, tau: float, n_max: int = 10) -> np.ndarray:
        """
        Energy eigenvalues for modes with temporal period tau.

        omega_n = 2*pi*n/tau for n = 0, 1, 2, ...
        E_n = hbar * omega_n = 2*pi*n*hbar/tau
        """
        ns = np.arange(n_max + 1)
        return 2 * np.pi * ns * HBAR / tau

    def compton_period_modes(self, n_max: int = 10) -> np.ndarray:
        """Modes when tau = tau_C. Should match QHO spectrum."""
        return self.temporal_mode_energies(self.tau_compton, n_max)

    def qho_spectrum(self, n_max: int = 10) -> np.ndarray:
        """Standard QHO energy levels E_n = hbar*omega*(n+1/2)."""
        ns = np.arange(n_max + 1)
        return HBAR * self.omega_compton * (ns + 0.5)

    def temporal_modes_match_qho(self, n_max: int = 10) -> Dict:
        """
        Compare temporal cell modes with QHO spectrum.

        The temporal modes give E_n = n*hbar*omega (no zero-point).
        The QHO gives E_n = (n+1/2)*hbar*omega.

        The SPACING is identical: Delta_E = hbar*omega in both cases.
        The only difference is the zero-point energy, which the temporal
        cell construction misses (it gives E_0 = 0, not hbar*omega/2).

        This means temporal cellularization at the Compton scale
        reproduces the standard quantization scheme.
        """
        temporal = self.compton_period_modes(n_max)
        qho = self.qho_spectrum(n_max)

        # Spacings
        temporal_spacings = np.diff(temporal)
        qho_spacings = np.diff(qho)

        spacing_match = np.allclose(temporal_spacings, qho_spacings, rtol=1e-12)

        return {
            "temporal_E0": float(temporal[0]),
            "qho_E0": float(qho[0]),
            "zero_point_from_temporal": float(temporal[0]),
            "zero_point_from_qho": float(qho[0]),
            "spacing_match": spacing_match,
            "spacing_value": float(HBAR * self.omega_compton),
            "conclusion": (
                "Temporal cells at Compton period reproduce QHO level spacing. "
                "The only difference is the zero-point energy. "
                "No new physics from temporal cellularization at this scale."
            ),
        }

    def spatial_casimir_energy_density(self, L: float) -> float:
        """
        Standard Casimir energy density between plates at distance L.

        rho_Casimir = -pi^2 hbar c / (720 L^4)

        Negative (attractive force between plates).
        """
        return -np.pi**2 * HBAR * C / (720 * L**4)

    def temporal_casimir_energy_density(self, tau: float) -> float:
        """
        Temporal Casimir energy density by analogy with spatial case.

        Replace L -> c*tau (temporal boundary separation in spatial units):
        rho_temporal ~ -pi^2 hbar c / (720 (c*tau)^4)
                     = -pi^2 hbar / (720 c^3 tau^4)

        This is a FORMAL ANALOGY. The temporal Casimir effect is not
        rigorously established in the same way as the spatial one.
        The sign, in particular, is uncertain.

        [CONJECTURED] — formal analogy, not derived from first principles.
        """
        return -np.pi**2 * HBAR / (720 * C**3 * tau**4)

    def temporal_casimir_at_compton(self) -> Dict:
        """
        Evaluate the temporal Casimir energy at tau = tau_C.

        rho_temporal = -pi^2 hbar / (720 c^3 tau_C^4)

        Compare with the cell vacuum energy density:
        rho_cell = m^4 c^5 / hbar^3
        """
        tau = self.tau_compton
        rho_temporal = self.temporal_casimir_energy_density(tau)
        rho_cell = self.mass**4 * C**5 / HBAR**3

        return {
            "rho_temporal_casimir": rho_temporal,
            "rho_cell_vacuum": rho_cell,
            "ratio": rho_temporal / rho_cell if rho_cell != 0 else float('nan'),
            "temporal_casimir_negative": rho_temporal < 0,
            "note": (
                "The temporal Casimir energy is a formal analogy. "
                "Even if it exists, it is a tiny fraction of the cell energy. "
                "Its equation of state is w = -1 (Casimir energy is Lorentz "
                "invariant in the spatial case), but its magnitude is "
                "suppressed by pi^2/720 relative to the cell energy."
            ),
        }

    def temporal_casimir_w(self) -> float:
        """
        Equation of state for temporal Casimir energy.

        By analogy with the spatial Casimir effect, which gives w = -1/3
        for parallel plates (not w = -1!), the temporal analog would give
        a different value depending on the geometry.

        For the spatial Casimir effect in 3+1D:
        - Between parallel plates: w_perp = -1/3 (1D confinement)
        - In a box: depends on geometry

        The temporal "Casimir" effect confines in the time direction.
        The stress-energy of the Casimir effect depends on which direction
        is confined:
            T_mu_nu ~ diag(rho, p_x, p_y, p_z)

        For temporal confinement, by formal analogy with spatial:
            The confined direction is time itself, so the "pressure"
            interpretation changes. The Casimir energy between temporal
            boundaries contributes to energy density but the pressure
            depends on how the energy responds to spatial expansion.

        For a Lorentz-invariant vacuum energy: w = -1.
        For the Casimir effect between spatial plates: w = -1/3 along plates.

        The temporal Casimir energy, if it exists, has uncertain w.
        We use w = -1 as an upper bound on negative pressure.

        [CONJECTURED] — equation of state for temporal Casimir is not established.
        """
        return -1.0  # Formal upper bound


# ===========================================================================
# 3. Cosmological Temporal Cell
# ===========================================================================
@dataclass
class CosmologicalTemporalCell:
    """
    What if the temporal cell size is cosmological (T ~ 1/H0) rather
    than the Compton period?

    This connects to:
    - Gibbons-Hawking temperature of de Sitter space
    - Parker particle creation in expanding spacetime
    - The cosmological horizon as a "temporal boundary"
    """
    mass: float  # particle mass in kg
    H: float = H0_SI  # Hubble rate in s^-1

    @property
    def omega_compton(self) -> float:
        return self.mass * C**2 / HBAR

    @property
    def hubble_time(self) -> float:
        """T_H = 1/H in seconds."""
        return 1.0 / self.H

    @property
    def compton_period(self) -> float:
        return 2 * np.pi / self.omega_compton

    def gibbons_hawking_temperature(self) -> float:
        """
        T_GH = hbar * H / (2 * pi * k_B)

        The de Sitter horizon radiates at this temperature.
        For H = H0: T_GH ~ 2.7e-30 K (absurdly small).
        """
        return HBAR * self.H / (2 * np.pi * K_B)

    def compton_temperature(self) -> float:
        """
        T_Compton = mc^2 / (2*pi*k_B)

        The temperature corresponding to the Compton energy.
        """
        return self.mass * C**2 / (2 * np.pi * K_B)

    def temperature_ratio(self) -> float:
        """
        T_GH / T_Compton = hbar*H / (mc^2) = H / omega_C

        This is the ratio of the Hubble rate to the Compton frequency.
        For any particle physics mass, this is incredibly tiny (~10^{-30}).
        """
        return self.H / self.omega_compton

    def parker_creation_rate(self) -> float:
        """
        Parker particle creation rate for a massive scalar in de Sitter.

        For m >> H (adiabatic regime, which always holds for real particles):
        Gamma ~ H * exp(-2*pi*m*c^2 / (hbar*H))
              = H * exp(-2*pi*omega_C / H)

        This is exponentially suppressed: exp(-2*pi * 10^30) ~ 0.

        [PROVEN] — standard result in quantum field theory in curved spacetime.
        """
        exponent = -2 * np.pi * self.omega_compton / self.H
        # This exponent is ~ -10^{31}, so the result is effectively zero.
        # We cap to avoid underflow
        if exponent < -700:
            return 0.0
        return self.H * np.exp(exponent)

    def parker_energy_density(self) -> float:
        """
        Energy density from Parker-created particles.

        rho_Parker ~ Gamma * (hbar*omega_C) / (lambda_C^3)

        Since Gamma ~ 0 for m >> H, this is negligibly small.
        """
        Gamma = self.parker_creation_rate()
        omega = self.omega_compton
        lambda_C = HBAR / (self.mass * C)
        return Gamma * HBAR * omega / lambda_C**3

    def gibbons_hawking_energy_density(self) -> float:
        """
        Energy density of the Gibbons-Hawking thermal bath.

        For a thermal bath at temperature T:
        rho = (pi^2 / 30) * k_B^4 * T^4 / (hbar^3 * c^3)

        At T_GH:
        rho_GH = (pi^2/30) * (hbar*H)^4 / ((2*pi)^4 * hbar^3 * c^3)
               = H^4 * hbar / (960 * pi^2 * c^3)

        [PROVEN] — standard result, but magnitude is negligible.
        """
        T = self.gibbons_hawking_temperature()
        return (np.pi**2 / 30) * K_B**4 * T**4 / (HBAR**3 * C**3)

    def observed_dark_energy_density(self) -> float:
        """
        rho_DE ~ 3 * H0^2 * c^2 / (8*pi*G) * Omega_Lambda

        where Omega_Lambda ~ 0.685.
        """
        rho_crit = 3 * self.H**2 * C**2 / (8 * np.pi * G)
        return 0.685 * rho_crit

    def compare_energy_scales(self) -> Dict:
        """
        Compare various energy densities:
        1. Cell vacuum: rho_cell = m^4 c^5 / hbar^3
        2. Gibbons-Hawking thermal: rho_GH ~ H^4 hbar / c^3
        3. Parker creation: exponentially suppressed
        4. Observed dark energy: ~5.3e-10 J/m^3
        """
        rho_cell = self.mass**4 * C**5 / HBAR**3
        rho_GH = self.gibbons_hawking_energy_density()
        rho_Parker = self.parker_energy_density()
        rho_DE = self.observed_dark_energy_density()

        return {
            "rho_cell_vacuum": rho_cell,
            "rho_gibbons_hawking": rho_GH,
            "rho_parker": rho_Parker,
            "rho_dark_energy_observed": rho_DE,
            "ratio_GH_to_DE": rho_GH / rho_DE if rho_DE > 0 else float('nan'),
            "ratio_cell_to_DE": rho_cell / rho_DE if rho_DE > 0 else float('nan'),
            "GH_temperature_K": self.gibbons_hawking_temperature(),
            "compton_temperature_K": self.compton_temperature(),
            "temperature_ratio": self.temperature_ratio(),
            "conclusion": (
                "The Gibbons-Hawking energy density is ~120 orders of magnitude "
                "below the observed dark energy. Parker creation is exactly zero "
                "for particle physics masses (exponentially suppressed). "
                "The cosmological temporal cell does not produce dark energy."
            ),
        }

    def cosmological_temporal_casimir(self) -> Dict:
        """
        Temporal Casimir energy with tau = 1/H (Hubble time).

        rho_temporal ~ -pi^2 hbar / (720 c^3 (1/H)^4)
                     = -pi^2 hbar H^4 / (720 c^3)

        This is of order hbar*H^4/c^3, which is the same order as
        the Gibbons-Hawking energy density.

        Compare with observed dark energy:
        rho_DE ~ H^2 c^2 / G ~ H^2 M_Planck^2 c^2

        The ratio:
        rho_temporal / rho_DE ~ hbar H^2 / (G c) ~ (l_P * H/c)^2

        where l_P is the Planck length. This is ~10^{-122}, which is
        the cosmological constant problem itself!

        [FRAMEWORK] — the temporal Casimir approach reproduces the
        cosmological constant problem rather than solving it.
        """
        tau = 1.0 / self.H
        rho_temporal = -np.pi**2 * HBAR * self.H**4 / (720 * C**3)
        rho_DE = self.observed_dark_energy_density()

        return {
            "rho_temporal_casimir_hubble": rho_temporal,
            "rho_dark_energy": rho_DE,
            "ratio": abs(rho_temporal) / rho_DE if rho_DE > 0 else float('nan'),
            "is_correct_order": False,  # Off by ~120 orders of magnitude
            "note": (
                "The temporal Casimir energy at the Hubble scale is of order "
                "hbar*H^4/c^3 ~ 10^{-132} J/m^3, which is ~10^{-122} times "
                "the observed dark energy. This is the cosmological constant "
                "problem restated, not solved."
            ),
        }


# ===========================================================================
# 4. Euclidean Path Integral Construction
# ===========================================================================
@dataclass
class EuclideanPathIntegral:
    """
    In the Euclidean path integral, temporal periodicity beta defines
    a temperature T = hbar / (k_B * beta).

    A 4D cell with temporal extent tau_cell defines an effective
    temperature T_cell = hbar / (k_B * tau_cell).

    For tau_cell = tau_C = 2*pi/omega (Compton period):
    T_cell = hbar*omega / (2*pi*k_B) = mc^2 / (2*pi*k_B)

    This is the "Compton temperature" of the particle.
    """
    mass: float  # kg

    @property
    def omega(self) -> float:
        return self.mass * C**2 / HBAR

    @property
    def beta_compton(self) -> float:
        """Euclidean time period = 2*pi/omega (Compton period)."""
        return 2 * np.pi / self.omega

    @property
    def T_compton(self) -> float:
        """Temperature corresponding to Compton period."""
        return HBAR * self.omega / (2 * np.pi * K_B)

    def qho_free_energy(self, T: float) -> float:
        """
        Free energy of a quantum harmonic oscillator at temperature T.

        F = k_B T * ln(2 sinh(hbar*omega / (2*k_B*T)))

        Or equivalently:
        F = hbar*omega/2 + k_B T * ln(1 - exp(-hbar*omega/(k_B*T)))

        The first term is the zero-point energy.
        The second term is the thermal correction (always negative).
        """
        x = HBAR * self.omega / (K_B * T)
        if x > 500:
            # Low temperature limit: F ~ hbar*omega/2 + k_B*T*exp(-x)
            return HBAR * self.omega / 2 + K_B * T * np.exp(-x)
        if x < 1e-10:
            # High temperature limit: F ~ k_B*T*ln(x) = k_B*T*ln(hbar*omega/(k_B*T))
            return K_B * T * np.log(x)
        return HBAR * self.omega / 2 + K_B * T * np.log(1 - np.exp(-x))

    def qho_energy_thermal(self, T: float) -> float:
        """
        Thermal energy of QHO at temperature T.

        <E> = hbar*omega * (1/2 + n_BE)

        where n_BE = 1/(exp(hbar*omega/(k_B*T)) - 1) is the Bose-Einstein
        occupation number.
        """
        x = HBAR * self.omega / (K_B * T)
        if x > 500:
            n_BE = np.exp(-x)
        else:
            n_BE = 1.0 / (np.expm1(x))
        return HBAR * self.omega * (0.5 + n_BE)

    def qho_pressure_thermal(self, T: float) -> float:
        """
        Pressure of a QHO in a cell at temperature T.

        For energy eigenstates, p = 0 (virial theorem).
        Thermal state is a mixture of energy eigenstates:
        rho_thermal = sum_n p(n) |n><n|  where p(n) ~ exp(-E_n/k_BT)

        Since EACH energy eigenstate has p = 0, the thermal mixture
        ALSO has p = 0.

        This is the key result: thermal QHO still gives w = 0.

        [PROVEN] — follows from virial theorem applied to each Fock state.
        """
        return 0.0

    def free_energy_at_compton_temperature(self) -> Dict:
        """
        Evaluate QHO free energy at T = T_compton.

        At T = hbar*omega/(2*pi*k_B), the argument of the exponential is
        hbar*omega/(k_B*T) = 2*pi.

        F = hbar*omega/2 + (hbar*omega/(2*pi)) * ln(1 - e^{-2*pi})
          = hbar*omega/2 + (hbar*omega/(2*pi)) * ln(0.001867)
          = hbar*omega/2 - hbar*omega/(2*pi) * 6.283
          Wait, let me compute carefully.

        ln(1 - e^{-2*pi}) = ln(1 - 0.001867) = ln(0.998133) = -0.001869

        F = hbar*omega/2 + (hbar*omega/(2*pi)) * (-0.001869)
          = hbar*omega * (0.5 - 0.001869/(2*pi))
          = hbar*omega * (0.5 - 0.000298)
          = hbar*omega * 0.499702
        """
        T = self.T_compton
        F = self.qho_free_energy(T)
        E = self.qho_energy_thermal(T)
        p = self.qho_pressure_thermal(T)

        # Thermal correction magnitude
        x = 2 * np.pi  # hbar*omega/(k_B*T)
        thermal_correction = K_B * T * np.log(1 - np.exp(-x))
        relative_correction = thermal_correction / (HBAR * self.omega / 2)

        lambda_C = HBAR / (self.mass * C)
        V_cell = lambda_C**3

        return {
            "temperature_K": T,
            "x_parameter": x,
            "free_energy_J": F,
            "thermal_energy_J": E,
            "zero_point_energy_J": HBAR * self.omega / 2,
            "thermal_correction_J": thermal_correction,
            "relative_correction": relative_correction,
            "energy_density": E / V_cell,
            "pressure": p,
            "w": 0.0,  # p/rho = 0 even at finite temperature
            "bose_einstein_occupation": 1.0 / np.expm1(x),
            "conclusion": (
                "The Euclidean path integral at the Compton temperature gives "
                "a tiny thermal correction (~0.03%) to the zero-point energy, "
                "but the equation of state remains w = 0 because the thermal "
                "state is still a mixture of Fock states, each with w = 0."
            ),
        }

    def w_at_any_temperature(self, T: float) -> float:
        """
        w for a QHO at ANY temperature T.

        Since the thermal state is a Gibbs state:
        rho = (1/Z) * sum_n exp(-E_n/(k_BT)) |n><n|

        and each |n><n| has w = 0, the thermal state has w = 0.

        This holds for ALL temperatures, from T=0 to T=infinity.

        [PROVEN] — follows from virial theorem for each eigenstate.
        """
        return 0.0

    def high_temperature_limit(self) -> Dict:
        """
        At very high temperature T >> hbar*omega/k_B:
        - <E> -> k_B*T (classical equipartition)
        - w still = 0

        At very low temperature T << hbar*omega/k_B:
        - <E> -> hbar*omega/2 (zero-point energy)
        - w still = 0

        w = 0 at ALL temperatures for a massive scalar QHO.
        """
        return {
            "high_T_energy": "k_B * T (classical limit)",
            "high_T_w": 0.0,
            "low_T_energy": "hbar*omega/2 (quantum ground state)",
            "low_T_w": 0.0,
            "all_T_w": 0.0,
            "reason": (
                "The virial theorem for the harmonic oscillator gives "
                "<T> = <V> for EVERY energy eigenstate, at EVERY energy. "
                "Since pressure = (<T> - <V>)/V = 0 for each eigenstate, "
                "any statistical mixture (thermal or otherwise) also has p = 0."
            ),
        }


# ===========================================================================
# 5. 4D Cell Volume and Energy Counting
# ===========================================================================
@dataclass
class FourDimensionalCell:
    """
    A 4D spacetime cell with spatial size lambda_C and temporal size tau_C.

    4D cell volume: V_4D = lambda_C^3 * (c * tau_C)
                         = lambda_C^3 * lambda_C
                         = lambda_C^4

    where we use c*tau_C = c * 2*pi/omega = 2*pi*hbar/(mc) = 2*pi*lambda_C.

    Actually: c*tau_C = c * (2*pi/(mc^2/hbar)) = 2*pi*hbar/(mc) = 2*pi*lambda_C.

    So V_4D = lambda_C^3 * 2*pi*lambda_C = 2*pi * lambda_C^4.
    """
    mass: float

    @property
    def lambda_C(self) -> float:
        """Compton wavelength."""
        return HBAR / (self.mass * C)

    @property
    def tau_C(self) -> float:
        """Compton period."""
        return 2 * np.pi * HBAR / (self.mass * C**2)

    @property
    def V_3D(self) -> float:
        """3D cell volume = lambda_C^3."""
        return self.lambda_C**3

    @property
    def V_4D(self) -> float:
        """4D cell spacetime volume = lambda_C^3 * c*tau_C."""
        return self.lambda_C**3 * C * self.tau_C

    @property
    def V_4D_in_lambda_units(self) -> float:
        """V_4D / lambda_C^4 = 2*pi (the temporal cell adds a factor of 2*pi)."""
        return self.V_4D / self.lambda_C**4

    def energy_per_3D_cell(self, alpha_squared: float = 0.5) -> float:
        """
        Energy in a 3D cell with coherent state |alpha>.
        E = hbar*omega*(|alpha|^2 + 1/2)
        """
        omega = self.mass * C**2 / HBAR
        return HBAR * omega * (alpha_squared + 0.5)

    def action_per_4D_cell(self, alpha_squared: float = 0.5) -> float:
        """
        Action in a 4D cell = Energy * temporal_extent.

        S = E * tau_C = hbar*omega*(|alpha|^2 + 1/2) * (2*pi/omega)
          = 2*pi*hbar*(|alpha|^2 + 1/2)

        For |alpha|^2 = 1/2: S = 2*pi*hbar = h (one Planck quantum of action!)

        This is a remarkable numerological coincidence.
        """
        E = self.energy_per_3D_cell(alpha_squared)
        return E * self.tau_C

    def action_in_hbar_units(self, alpha_squared: float = 0.5) -> float:
        """S / hbar = 2*pi*(|alpha|^2 + 1/2). For |alpha|^2=1/2: S/hbar = 2*pi."""
        return self.action_per_4D_cell(alpha_squared) / HBAR

    def energy_density_3D(self, alpha_squared: float = 0.5) -> float:
        """Energy density in 3D cell: rho = E / V_3D."""
        return self.energy_per_3D_cell(alpha_squared) / self.V_3D

    def action_density_4D(self, alpha_squared: float = 0.5) -> float:
        """Action density in 4D cell: s = S / V_4D."""
        return self.action_per_4D_cell(alpha_squared) / self.V_4D

    def compare_3D_vs_4D(self) -> Dict:
        """
        Full comparison between 3D and 4D cell constructions.
        """
        omega = self.mass * C**2 / HBAR

        return {
            "lambda_C_m": self.lambda_C,
            "tau_C_s": self.tau_C,
            "V_3D_m3": self.V_3D,
            "V_4D_m4": self.V_4D,
            "V_4D_over_lambda4": self.V_4D_in_lambda_units,
            "energy_per_cell_J": self.energy_per_3D_cell(),
            "action_per_cell_J_s": self.action_per_4D_cell(),
            "action_over_hbar": self.action_in_hbar_units(),
            "action_over_h": self.action_in_hbar_units() / (2 * np.pi),
            "energy_density_J_per_m3": self.energy_density_3D(),
            "action_density_J_s_per_m4": self.action_density_4D(),
            "w_3D_cell": 0.0,
            "w_4D_cell": 0.0,
            "conclusion": (
                "The 4D cell construction gives the same w = 0 as the 3D "
                "construction. The action per 4D cell is exactly h (Planck "
                "constant) for |alpha|^2 = 1/2, which is numerologically "
                "interesting but does not change the physics."
            ),
        }


# ===========================================================================
# 6. Comparison of Temporal Cell Sizes
# ===========================================================================
@dataclass
class TemporalCellComparison:
    """
    Compare the physics for different temporal cell sizes:
    1. Compton period: tau = 2*pi/omega_C ~ 10^{-21} s
    2. Planck time: tau = t_P ~ 5.4e-44 s
    3. Hubble time: tau = 1/H0 ~ 4.6e17 s
    """
    mass: float

    @property
    def omega_C(self) -> float:
        return self.mass * C**2 / HBAR

    @property
    def tau_compton(self) -> float:
        return 2 * np.pi / self.omega_C

    @property
    def tau_planck(self) -> float:
        return np.sqrt(HBAR * G / C**5)

    @property
    def tau_hubble(self) -> float:
        return 1.0 / H0_SI

    def effective_temperature(self, tau: float) -> float:
        """T = hbar / (k_B * tau)"""
        return HBAR / (K_B * tau)

    def bose_einstein_n(self, tau: float) -> float:
        """
        Bose-Einstein occupation at effective temperature T(tau).
        n_BE = 1 / (exp(hbar*omega/(k_B*T)) - 1) = 1 / (exp(omega*tau) - 1)

        For tau = tau_C: omega*tau = 2*pi, n_BE = 1/(e^{2*pi}-1) ~ 0.00187
        For tau >> tau_C: omega*tau >> 1, n_BE ~ exp(-omega*tau) ~ 0
        For tau << tau_C: omega*tau << 1, n_BE ~ k_BT/(hbar*omega) >> 1
        """
        x = self.omega_C * tau
        if x > 500:
            return np.exp(-x)
        return 1.0 / np.expm1(x)

    def thermal_energy_correction(self, tau: float) -> float:
        """
        Energy correction from finite temporal cell size.

        Delta_E = hbar*omega * n_BE(tau)

        This is the energy above the zero-point from the effective
        temperature of the temporal cell.
        """
        return HBAR * self.omega_C * self.bose_einstein_n(tau)

    def compare_all_scales(self) -> Dict:
        """Compare temporal cells at different scales."""
        scales = {
            "compton": self.tau_compton,
            "planck": self.tau_planck,
            "hubble": self.tau_hubble,
        }

        results = {}
        for name, tau in scales.items():
            T = self.effective_temperature(tau)
            n_BE = self.bose_einstein_n(tau)
            dE = self.thermal_energy_correction(tau)
            E0 = HBAR * self.omega_C / 2

            results[name] = {
                "tau_s": tau,
                "T_K": T,
                "n_BE": n_BE,
                "delta_E_J": dE,
                "delta_E_relative": dE / E0 if E0 > 0 else 0,
                "w": 0.0,  # w = 0 at any temperature
            }

        results["summary"] = {
            "compton_n_BE": results["compton"]["n_BE"],
            "planck_n_BE": results["planck"]["n_BE"],
            "hubble_n_BE": results["hubble"]["n_BE"],
            "all_give_w_zero": True,
            "conclusion": (
                "At the Compton scale, n_BE ~ 0.002 (tiny thermal correction). "
                "At the Planck scale, n_BE ~ k_BT_P/(hbar*omega) >> 1 (high T, "
                "classical limit). At the Hubble scale, n_BE ~ 0 (ground state). "
                "In ALL cases, w = 0 because the virial theorem holds for each "
                "energy eigenstate independently of temperature."
            ),
        }

        return results


# ===========================================================================
# 7. Can ANY 4D Construction Give w < 0?
# ===========================================================================
class NegativePressureAnalysis:
    """
    Systematic analysis of whether ANY version of 4D cellularization
    can produce w < 0 with finite energy density.

    Short answer: NO, for the massive scalar field in flat space.

    The only ways to get w < 0 are:
    1. Wald renormalization ambiguity (adds a cosmological constant term)
    2. Spatial Casimir effect (boundary conditions in spatial directions)
    3. Curved spacetime effects (but these don't come from cellularization)
    """

    @staticmethod
    def virial_theorem_proof() -> Dict:
        """
        The virial theorem for a harmonic oscillator:
            <T> = <V>  for any eigenstate |n>

        This means p = (<T> - <V>)/V = 0 for each eigenstate.

        Any statistical mixture (thermal, phase-randomized, etc.)
        of eigenstates therefore has p = 0, hence w = 0.

        This is INDEPENDENT of:
        - The temperature (thermal state at any T gives w=0)
        - The mixture weights (any P(n) gives w=0)
        - Temporal boundary conditions (don't affect the virial theorem)
        - The cell size (virial theorem is a property of the potential)

        [PROVEN] — mathematical theorem, not subject to approximation.
        """
        return {
            "theorem": "<kinetic> = <potential> for QHO eigenstates",
            "consequence": "p = 0 for each eigenstate",
            "extension": "p = 0 for ANY mixture of eigenstates",
            "independence": [
                "Independent of temperature",
                "Independent of mixture weights",
                "Independent of temporal boundaries",
                "Independent of cell size",
            ],
            "conclusion": (
                "The virial theorem guarantees w = 0 for a massive scalar QHO "
                "in any state that is diagonal in the energy basis. Since "
                "time-averaging and thermal states are both diagonal in the "
                "energy basis, no temporal cellularization can change w."
            ),
            "evidence_tier": "PROVEN",
        }

    @staticmethod
    def loophole_analysis() -> Dict:
        """
        Are there any loopholes that could give w < 0?

        1. Spatial Casimir effect: YES, can give w < 0 in the confined
           direction. But this is a spatial boundary effect, not temporal.
           And for the cell vacuum with cell size = lambda_C, the Casimir
           energy is already accounted for in the QHO quantization.

        2. Temporal Casimir effect: UNCERTAIN. The formal analogy suggests
           it could give negative energy density, but:
           - The magnitude is tiny (suppressed by pi^2/720)
           - The interpretation of "temporal boundaries" is unclear
           - No rigorous derivation exists for the temporal case

        3. Interacting fields: If cells interact across temporal boundaries,
           there could be interference effects. But the cell vacuum
           construction assumes independent cells.

        4. Curved spacetime: An expanding universe breaks time-translation
           invariance, which could change the virial theorem. But this is
           an external effect, not from cellularization.

        5. Non-equilibrium states: States that are NOT diagonal in the
           energy basis (e.g., squeezed states) CAN have w != 0 at
           individual moments. But time-averaging always gives w = 0
           for a massive QHO.
        """
        return {
            "loophole_1_spatial_casimir": {
                "can_give_w_negative": True,
                "relevant_to_4D_cell": False,
                "reason": "Spatial boundaries, not temporal",
                "tier": "PROVEN",
            },
            "loophole_2_temporal_casimir": {
                "can_give_w_negative": "Unknown",
                "relevant_to_4D_cell": True,
                "reason": "Formal analogy only, no rigorous derivation",
                "magnitude": "Suppressed by pi^2/720 relative to cell energy",
                "tier": "CONJECTURED",
            },
            "loophole_3_cell_interactions": {
                "can_give_w_negative": "Possibly",
                "relevant_to_4D_cell": True,
                "reason": "Temporal correlations between adjacent time-cells",
                "tier": "CONJECTURED",
            },
            "loophole_4_curved_spacetime": {
                "can_give_w_negative": True,
                "relevant_to_4D_cell": False,
                "reason": "External effect from expansion, not cellularization",
                "tier": "FRAMEWORK",
            },
            "loophole_5_non_equilibrium": {
                "can_give_w_negative": "Instantaneously yes, time-averaged no",
                "relevant_to_4D_cell": False,
                "reason": "Time-averaging over the temporal cell restores w=0",
                "tier": "PROVEN",
            },
            "overall_conclusion": (
                "No known mechanism within the 4D cell construction changes "
                "w from 0. The virial theorem is too robust. The only paths "
                "to w < 0 involve either (a) adding a Wald cosmological "
                "constant term, or (b) spatial Casimir effects from "
                "boundaries, or (c) curved spacetime physics."
            ),
        }


# ===========================================================================
# Convenience: Run All Analyses
# ===========================================================================
def run_full_analysis(mass: float = M_NEUTRINO) -> Dict:
    """Run all four approaches and the comparison analyses."""
    results = {}

    # 1. Phase-randomized state
    pr = PhaseRandomizedState(alpha_squared=0.5)
    results["phase_randomized"] = pr.stress_energy_mixed_state(mass)

    # 2. Temporal Casimir
    tc = TemporalCasimir(mass=mass)
    results["temporal_casimir"] = tc.temporal_casimir_at_compton()
    results["temporal_modes_vs_qho"] = tc.temporal_modes_match_qho()

    # 3. Cosmological temporal cell
    ctc = CosmologicalTemporalCell(mass=mass)
    results["cosmological"] = ctc.compare_energy_scales()
    results["cosmological_casimir"] = ctc.cosmological_temporal_casimir()

    # 4. Euclidean path integral
    epi = EuclideanPathIntegral(mass=mass)
    results["euclidean"] = epi.free_energy_at_compton_temperature()

    # 5. 4D cell comparison
    fdc = FourDimensionalCell(mass=mass)
    results["4d_cell"] = fdc.compare_3D_vs_4D()

    # 6. Temporal cell size comparison
    tcc = TemporalCellComparison(mass=mass)
    results["temporal_comparison"] = tcc.compare_all_scales()

    # 7. Negative pressure analysis
    results["negative_pressure"] = NegativePressureAnalysis.virial_theorem_proof()
    results["loopholes"] = NegativePressureAnalysis.loophole_analysis()

    return results


if __name__ == "__main__":
    results = run_full_analysis()

    print("=" * 70)
    print("4D SPACETIME CELL VACUUM ANALYSIS")
    print("=" * 70)

    # Phase-randomized state
    pr = results["phase_randomized"]
    print(f"\n1. PHASE-RANDOMIZED STATE")
    print(f"   w = {pr['w']}")
    print(f"   von Neumann entropy = {pr['von_neumann_entropy']:.4f}")
    print(f"   Mean occupation = {pr['mean_occupation']:.4f}")

    # Temporal Casimir
    tc = results["temporal_casimir"]
    print(f"\n2. TEMPORAL CASIMIR EFFECT")
    print(f"   rho_temporal = {tc['rho_temporal_casimir']:.4e} J/m^3")
    print(f"   rho_cell = {tc['rho_cell_vacuum']:.4e} J/m^3")
    print(f"   ratio = {tc['ratio']:.4e}")

    # Cosmological
    cs = results["cosmological"]
    print(f"\n3. COSMOLOGICAL TEMPORAL CELL")
    print(f"   rho_GH = {cs['rho_gibbons_hawking']:.4e} J/m^3")
    print(f"   rho_DE = {cs['rho_dark_energy_observed']:.4e} J/m^3")
    print(f"   ratio GH/DE = {cs['ratio_GH_to_DE']:.4e}")

    # Euclidean
    eu = results["euclidean"]
    print(f"\n4. EUCLIDEAN PATH INTEGRAL")
    print(f"   T_compton = {eu['temperature_K']:.4e} K")
    print(f"   n_BE = {eu['bose_einstein_occupation']:.6f}")
    print(f"   thermal correction = {eu['relative_correction']:.6f}")
    print(f"   w = {eu['w']}")

    # 4D cell
    fd = results["4d_cell"]
    print(f"\n5. 4D CELL PROPERTIES")
    print(f"   Action/hbar = {fd['action_over_hbar']:.6f} (should be 2*pi)")
    print(f"   Action/h = {fd['action_over_h']:.6f} (should be 1)")
    print(f"   w (3D) = {fd['w_3D_cell']}")
    print(f"   w (4D) = {fd['w_4D_cell']}")

    print("\n" + "=" * 70)
    print("CONCLUSION: 4D cellularization does NOT change w from 0.")
    print("The virial theorem guarantees w = 0 for any mixture of")
    print("QHO eigenstates, regardless of temporal boundaries.")
    print("=" * 70)
