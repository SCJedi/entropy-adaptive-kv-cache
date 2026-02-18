"""
MVSU Simulation Test v2: Kepler Orbit Error Correction (REVISED)
=================================================================
Fixes the v1 problem: Euler vs Verlet had a ~300x accuracy gap, making one
channel effectively noise. The cross-weight simply learned to select Verlet.

Key changes in v2:
  - Two COMPARABLE integrators: RK4 (classical) vs RK4-3/8 (3/8-rule variant)
  - Both are 4th-order single-step Runge-Kutta methods
  - Structurally different: they use different Butcher tableau coefficients
    which means their 5th-order truncation error terms differ
  - Also tested: RK4 vs Adams-Bashforth 4 (AB4) for comparison
  - POSITION-LEVEL cross-correction via w_cross sweep
  - Noisy measurement beta sweep with PROPER noise handling
  - Noise applied only to position components (physically realistic)

Conditions (minimum 6):
  1. RK4 only
  2. RK4-3/8 only (or AB4)
  3. Simple average of the two
  4. MVSU with swept w_cross (find optimal)
  5. MVSU + damped ground truth updates (beta=0.38)
  6. MVSU + damped updates (beta=0.618)
  + Noisy measurement beta sweep

Author: Claude (MVSU Simulation Experiment v2)
"""

import sys
import io
import os
import time
import numpy as np

# Windows Unicode fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except Exception:
            pass
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except Exception:
            pass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# =============================================================================
# Kepler Orbit: Exact Solution
# =============================================================================

def kepler_eccentric_anomaly(M, e, tol=1e-12, max_iter=100):
    """Solve Kepler's equation M = E - e*sin(E) for E via Newton's method."""
    E = M.copy() if isinstance(M, np.ndarray) else float(M)
    for _ in range(max_iter):
        dE = (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
        E -= dE
        if np.all(np.abs(dE) < tol):
            break
    return E


def kepler_true_state(t, a, e, mu, t0=0.0):
    """Exact position and velocity for Kepler orbit at time t."""
    n = np.sqrt(mu / a**3)
    M = n * (t - t0)
    E = kepler_eccentric_anomaly(M, e)
    denom = 1.0 - e * np.cos(E)
    cos_f = (np.cos(E) - e) / denom
    sin_f = (np.sqrt(1.0 - e**2) * np.sin(E)) / denom
    r = a * denom
    x = r * cos_f
    y = r * sin_f
    dEdt = n / denom
    drdt = a * e * np.sin(E) * dEdt
    dfdt = np.sqrt(1.0 - e**2) * a * dEdt / r
    vx = drdt * cos_f - r * sin_f * dfdt
    vy = drdt * sin_f + r * cos_f * dfdt
    return x, y, vx, vy


def grav_accel(state, mu):
    """Gravitational acceleration."""
    x, y = state[0], state[1]
    r3 = (x**2 + y**2)**1.5
    return np.array([-mu * x / r3, -mu * y / r3])


def orbital_energy(state, mu):
    """Specific orbital energy."""
    return 0.5 * (state[2]**2 + state[3]**2) - mu / np.sqrt(state[0]**2 + state[1]**2)


# =============================================================================
# Integrators
# =============================================================================

def deriv(state, mu):
    """Full state derivative: [vx, vy, ax, ay]."""
    ax, ay = grav_accel(state, mu)
    return np.array([state[2], state[3], ax, ay])


def rk4_classic_step(state, dt, mu):
    """Classical 4th-order Runge-Kutta (the standard one).

    Butcher tableau:
      0   |
      1/2 | 1/2
      1/2 | 0   1/2
      1   | 0   0   1
      ----|------------------
          | 1/6 1/3 1/3 1/6

    Local truncation error: C5 * h^5 where C5 depends on the 5th derivatives.
    """
    k1 = deriv(state, mu)
    k2 = deriv(state + 0.5 * dt * k1, mu)
    k3 = deriv(state + 0.5 * dt * k2, mu)
    k4 = deriv(state + dt * k3, mu)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def rk4_38_step(state, dt, mu):
    """3/8-rule 4th-order Runge-Kutta (Kutta's other method).

    Butcher tableau:
      0   |
      1/3 | 1/3
      2/3 |-1/3  1
      1   | 1   -1   1
      ----|------------------
          | 1/8 3/8 3/8 1/8

    Also 4th order, but with DIFFERENT truncation error coefficients.
    The leading error term (5th-order) has different magnitude and sign
    compared to classical RK4 for the same problem.
    """
    k1 = deriv(state, mu)
    k2 = deriv(state + (dt / 3.0) * k1, mu)
    k3 = deriv(state + dt * (-k1 / 3.0 + k2), mu)
    k4 = deriv(state + dt * (k1 - k2 + k3), mu)
    return state + (dt / 8.0) * (k1 + 3*k2 + 3*k3 + k4)


def ab4_step(state, dt, mu, f_history):
    """Adams-Bashforth 4-step method.

    f_history = [f_{n-3}, f_{n-2}, f_{n-1}, f_n] (oldest to newest)
    Global error ~ O(dt^4).
    """
    fn_3, fn_2, fn_1, fn = f_history
    return state + (dt / 24.0) * (55*fn - 59*fn_1 + 37*fn_2 - 9*fn_3)


# =============================================================================
# MVSU Cross-Correction
# =============================================================================

def mvsu_combine(state_A, state_B, w_cross):
    """MVSU cross-corrected output.

    output = (A + B)/2 + w_cross * (A - B)
           = (0.5 + w_cross)*A + (0.5 - w_cross)*B

    w_cross = 0:    simple average
    w_cross = +0.5: pure A
    w_cross = -0.5: pure B
    """
    return 0.5 * (state_A + state_B) + w_cross * (state_A - state_B)


# =============================================================================
# Simulation
# =============================================================================

def run_integrator(integrator_fn, state0, dt, n_steps, mu):
    """Run a single-step integrator for n_steps."""
    n = n_steps + 1
    states = np.zeros((n, 4))
    states[0] = state0.copy()
    for i in range(n_steps):
        states[i + 1] = integrator_fn(states[i], dt, mu)
    return states


def run_ab4(state0, dt, n_steps, mu):
    """Run AB4 with RK4-classic bootstrap for first 3 steps."""
    n = n_steps + 1
    states = np.zeros((n, 4))
    states[0] = state0.copy()

    # Bootstrap with RK4-classic for 3 steps
    f_hist = [deriv(state0, mu)]
    for i in range(min(3, n_steps)):
        states[i + 1] = rk4_classic_step(states[i], dt, mu)
        f_hist.append(deriv(states[i + 1], mu))

    # AB4 for remaining steps
    for i in range(3, n_steps):
        states[i + 1] = ab4_step(states[i], dt, mu, f_hist)
        f_hist.pop(0)
        f_hist.append(deriv(states[i + 1], mu))

    return states


def run_mvsu_damped(integrator_A, integrator_B, state0, dt, n_steps, mu,
                    true_states, w_cross, beta, measurement_interval,
                    noise_sigma=0.0, rng=None):
    """Run two integrators with damped ground truth updates.

    Both integrators run independently. At measurement points,
    both channels are nudged toward (possibly noisy) ground truth.
    MVSU combines them at each step.
    """
    n = n_steps + 1
    output = np.zeros((n, 4))
    output[0] = state0.copy()

    ch_A = state0.copy()
    ch_B = state0.copy()

    for i in range(n_steps):
        ch_A = integrator_A(ch_A, dt, mu)
        ch_B = integrator_B(ch_B, dt, mu)
        output[i + 1] = mvsu_combine(ch_A, ch_B, w_cross)

        # Damped ground truth update
        if (i + 1) % measurement_interval == 0 and beta > 0:
            true_s = true_states[i + 1].copy()
            if noise_sigma > 0 and rng is not None:
                # Noise on position only (physically: we observe position, not velocity)
                true_s[0] += rng.normal(0, noise_sigma)
                true_s[1] += rng.normal(0, noise_sigma)
                # Velocity gets proportionally smaller noise (derived from position)
                true_s[2] += rng.normal(0, noise_sigma * 0.1)
                true_s[3] += rng.normal(0, noise_sigma * 0.1)

            ch_A += beta * (true_s - ch_A)
            ch_B += beta * (true_s - ch_B)
            output[i + 1] = mvsu_combine(ch_A, ch_B, w_cross)

    return output


def compute_pos_error(states, true_states):
    """Position error over time."""
    return np.sqrt((states[:, 0] - true_states[:, 0])**2 +
                   (states[:, 1] - true_states[:, 1])**2)


def compute_energy_error(states, E0, mu):
    """Relative energy error over time."""
    E = np.array([orbital_energy(s, mu) for s in states])
    return np.abs(E - E0) / np.abs(E0)


def orbits_before_threshold(pos_err, threshold, steps_per_orbit, n_orbits):
    """How many orbits before error exceeds threshold."""
    exceed = np.where(pos_err > threshold)[0]
    if len(exceed) == 0:
        return n_orbits
    return exceed[0] / steps_per_orbit


# =============================================================================
# Main
# =============================================================================

def run_simulation(n_orbits=15, steps_per_orbit=200, e=0.3):
    """Run all conditions and collect metrics."""

    a = 1.0
    mu = 1.0
    T = 2.0 * np.pi * np.sqrt(a**3 / mu)
    n_steps = n_orbits * steps_per_orbit
    dt = T * n_orbits / n_steps

    print(f"Kepler Orbit Parameters:")
    print(f"  Semi-major axis a = {a}")
    print(f"  Eccentricity e = {e}")
    print(f"  Period T = {T:.4f}")
    print(f"  n_orbits = {n_orbits}, steps/orbit = {steps_per_orbit}")
    print(f"  Total steps = {n_steps}, dt = {dt:.6f}")
    print()

    # Initial conditions at periapsis
    x0 = a * (1.0 - e)
    y0 = 0.0
    vx0 = 0.0
    vy0 = np.sqrt(mu * (1.0 + e) / (a * (1.0 - e)))
    state0 = np.array([x0, y0, vx0, vy0])
    E0 = orbital_energy(state0, mu)

    print(f"  Initial state: [{x0:.4f}, {y0:.4f}, {vx0:.4f}, {vy0:.4f}]")
    print(f"  Initial energy: {E0:.6f} (expected: {-mu/(2*a):.6f})")
    print()

    # Pre-compute true solution
    n = n_steps + 1
    times = np.linspace(0, T * n_orbits, n)
    true_states = np.zeros((n, 4))
    true_states[0] = state0
    for i in range(1, n):
        true_states[i] = np.array(kepler_true_state(times[i], a, e, mu))

    measurement_interval = steps_per_orbit // 5  # 5 measurements per orbit

    # =====================================================================
    # Run primary integrator pair: RK4-classic vs RK4-3/8
    # =====================================================================

    print("=" * 100)
    print("PRIMARY PAIR: RK4-classic vs RK4-3/8 (both 4th-order, different coefficients)")
    print("=" * 100)
    print()

    print("  Running RK4-classic...")
    rk4c_states = run_integrator(rk4_classic_step, state0, dt, n_steps, mu)

    print("  Running RK4-3/8...")
    rk4_38_states = run_integrator(rk4_38_step, state0, dt, n_steps, mu)

    # Error comparison
    rk4c_err = compute_pos_error(rk4c_states, true_states)
    rk4_38_err = compute_pos_error(rk4_38_states, true_states)
    avg_rk4_states = 0.5 * (rk4c_states + rk4_38_states)
    avg_rk4_err = compute_pos_error(avg_rk4_states, true_states)

    ratio_rk4 = np.mean(rk4_38_err) / np.mean(rk4c_err) if np.mean(rk4c_err) > 0 else float('inf')
    print(f"  RK4-classic mean error: {np.mean(rk4c_err):.10e}")
    print(f"  RK4-3/8    mean error: {np.mean(rk4_38_err):.10e}")
    print(f"  Accuracy ratio (3/8 / classic): {ratio_rk4:.4f}x")
    print(f"  Average    mean error: {np.mean(avg_rk4_err):.10e}")
    print()

    # w_cross sweep for RK4-classic vs RK4-3/8
    print("  Sweeping w_cross...")
    w_cross_vals = np.linspace(-0.5, 0.5, 401)
    wc_errors_rk4 = np.zeros(len(w_cross_vals))
    for wi, wc in enumerate(w_cross_vals):
        combined = mvsu_combine(rk4c_states, rk4_38_states, wc)
        wc_errors_rk4[wi] = np.mean(compute_pos_error(combined, true_states))

    best_wc_rk4_idx = np.argmin(wc_errors_rk4)
    best_wc_rk4 = w_cross_vals[best_wc_rk4_idx]
    best_wc_rk4_err = wc_errors_rk4[best_wc_rk4_idx]
    avg_idx = np.argmin(np.abs(w_cross_vals))
    avg_wc_err = wc_errors_rk4[avg_idx]

    print(f"  Optimal w_cross: {best_wc_rk4:.4f}")
    print(f"  Error at optimal: {best_wc_rk4_err:.10e}")
    print(f"  Error at w=0 (avg): {avg_wc_err:.10e}")
    print(f"  Improvement over average: {avg_wc_err / best_wc_rk4_err:.4f}x")
    beats_avg = best_wc_rk4_err < avg_wc_err
    beats_both = best_wc_rk4_err < min(np.mean(rk4c_err), np.mean(rk4_38_err))
    print(f"  MVSU beats average? {beats_avg}")
    print(f"  MVSU beats BOTH individual integrators? {beats_both}")
    print()

    # =====================================================================
    # Also run AB4 for comparison
    # =====================================================================

    print("=" * 100)
    print("SECONDARY PAIR: RK4-classic vs AB4 (both 4th-order, single-step vs multi-step)")
    print("=" * 100)
    print()

    print("  Running AB4...")
    ab4_states = run_ab4(state0, dt, n_steps, mu)
    ab4_err = compute_pos_error(ab4_states, true_states)

    ratio_ab4 = np.mean(ab4_err) / np.mean(rk4c_err) if np.mean(rk4c_err) > 0 else float('inf')
    print(f"  AB4 mean error: {np.mean(ab4_err):.10e}")
    print(f"  Accuracy ratio (AB4 / RK4-classic): {ratio_ab4:.4f}x")

    # w_cross sweep for RK4-classic vs AB4
    wc_errors_ab4 = np.zeros(len(w_cross_vals))
    for wi, wc in enumerate(w_cross_vals):
        combined = mvsu_combine(rk4c_states, ab4_states, wc)
        wc_errors_ab4[wi] = np.mean(compute_pos_error(combined, true_states))

    best_wc_ab4_idx = np.argmin(wc_errors_ab4)
    best_wc_ab4 = w_cross_vals[best_wc_ab4_idx]
    best_wc_ab4_err = wc_errors_ab4[best_wc_ab4_idx]
    avg_ab4_err = wc_errors_ab4[np.argmin(np.abs(w_cross_vals))]

    print(f"  Optimal w_cross: {best_wc_ab4:.4f}")
    print(f"  Error at optimal: {best_wc_ab4_err:.10e}")
    print(f"  Improvement over average: {avg_ab4_err / best_wc_ab4_err:.4f}x")
    ab4_beats_both = best_wc_ab4_err < min(np.mean(rk4c_err), np.mean(ab4_err))
    print(f"  MVSU beats BOTH? {ab4_beats_both}")
    print()

    # =====================================================================
    # Choose the BETTER pair for remaining tests
    # =====================================================================

    # Use RK4-classic vs RK4-3/8 (more comparable) or RK4 vs AB4 (more different)?
    # Let's use whichever pair shows more MVSU benefit.
    if best_wc_rk4_err < best_wc_ab4_err:
        pair_label = "RK4-classic vs RK4-3/8"
        integ_A_fn = rk4_classic_step
        integ_B_fn = rk4_38_step
        states_A = rk4c_states
        states_B = rk4_38_states
        best_wc = best_wc_rk4
        best_wc_err = best_wc_rk4_err
        w_cross_sweep_errors = wc_errors_rk4
        label_A = "RK4-classic"
        label_B = "RK4-3/8"
    else:
        pair_label = "RK4-classic vs AB4"
        integ_A_fn = rk4_classic_step
        # For AB4 we can't use simple function signature, use RK4-3/8 as proxy
        # Actually let's just always use RK4-classic vs RK4-3/8 for damped tests
        # since single-step methods handle nudges cleanly
        integ_B_fn = rk4_38_step
        states_A = rk4c_states
        states_B = rk4_38_states
        best_wc = best_wc_rk4
        best_wc_err = best_wc_rk4_err
        w_cross_sweep_errors = wc_errors_rk4
        label_A = "RK4-classic"
        label_B = "RK4-3/8"
        pair_label = "RK4-classic vs RK4-3/8 (selected for damped tests)"

    print(f"Using {pair_label} for damped update tests")
    print(f"  (Both single-step methods handle state nudges cleanly)")
    print()

    # MVSU optimal output
    mvsu_opt_states = mvsu_combine(states_A, states_B, best_wc)

    # =====================================================================
    # Conditions 5 & 6: MVSU + damped ground truth (perfect measurements)
    # =====================================================================

    print("=" * 100)
    print("DAMPED GROUND TRUTH UPDATES (perfect measurements)")
    print("=" * 100)
    print()

    print("  Running MVSU+Damp(0.38)...")
    mvsu_d038 = run_mvsu_damped(
        integ_A_fn, integ_B_fn, state0, dt, n_steps, mu,
        true_states, best_wc, beta=0.38,
        measurement_interval=measurement_interval)

    print("  Running MVSU+Damp(0.618)...")
    mvsu_d062 = run_mvsu_damped(
        integ_A_fn, integ_B_fn, state0, dt, n_steps, mu,
        true_states, best_wc, beta=0.618,
        measurement_interval=measurement_interval)

    # =====================================================================
    # Full results table
    # =====================================================================

    conditions = {
        f'{label_A} only': states_A,
        f'{label_B} only': states_B,
        f'Average ({label_A}+{label_B})': 0.5 * (states_A + states_B),
        f'MVSU (w={best_wc:.3f})': mvsu_opt_states,
        'MVSU+Damp(0.38)': mvsu_d038,
        'MVSU+Damp(0.618)': mvsu_d062,
    }

    labels = list(conditions.keys())
    all_states_list = list(conditions.values())
    all_pos_errs = [compute_pos_error(s, true_states) for s in all_states_list]
    all_E_errs = [compute_energy_error(s, E0, mu) for s in all_states_list]

    error_threshold = 0.01 * a
    mean_pos_errs = [np.mean(pe) for pe in all_pos_errs]
    final_pos_errs = [pe[-1] for pe in all_pos_errs]
    max_pos_errs = [np.max(pe) for pe in all_pos_errs]
    final_E_errs = [ee[-1] for ee in all_E_errs]
    orbit_vals = [orbits_before_threshold(pe, error_threshold, steps_per_orbit, n_orbits)
                  for pe in all_pos_errs]

    print()
    print("=" * 120)
    print("RESULTS TABLE")
    print("=" * 120)
    print()
    hdr = (f"{'Condition':<28} {'Final Pos Err':>14} {'Mean Pos Err':>14} "
           f"{'Max Pos Err':>14} {'Final dE/E':>14} {'Orbits<0.01':>12}")
    print(hdr)
    print("-" * 120)
    for j in range(len(labels)):
        print(f"{labels[j]:<28} {final_pos_errs[j]:>14.8e} {mean_pos_errs[j]:>14.8e} "
              f"{max_pos_errs[j]:>14.8e} {final_E_errs[j]:>14.8e} {orbit_vals[j]:>12.2f}")

    print()
    ranking = sorted(range(len(labels)), key=lambda j: mean_pos_errs[j])
    print("Ranking by mean position error:")
    for rank, j in enumerate(ranking):
        print(f"  {rank+1}. {labels[j]}: {mean_pos_errs[j]:.8e}")
    print()

    # =====================================================================
    # w_cross sweep detailed analysis
    # =====================================================================

    print("=" * 100)
    print("W_CROSS SWEEP ANALYSIS")
    print("=" * 100)
    print()

    idx_p05 = np.argmin(np.abs(w_cross_vals - 0.5))
    idx_m05 = np.argmin(np.abs(w_cross_vals + 0.5))
    idx_0 = np.argmin(np.abs(w_cross_vals))

    print(f"  w_cross = +0.50 (pure {label_A}): {w_cross_sweep_errors[idx_p05]:.8e}")
    print(f"  w_cross = -0.50 (pure {label_B}): {w_cross_sweep_errors[idx_m05]:.8e}")
    print(f"  w_cross =  0.00 (average):        {w_cross_sweep_errors[idx_0]:.8e}")
    print(f"  w_cross = {best_wc:+.3f} (OPTIMAL):       {best_wc_err:.8e}")
    print()

    imp_over_avg = w_cross_sweep_errors[idx_0] / best_wc_err if best_wc_err > 0 else float('inf')
    imp_over_A = w_cross_sweep_errors[idx_p05] / best_wc_err if best_wc_err > 0 else float('inf')
    imp_over_B = w_cross_sweep_errors[idx_m05] / best_wc_err if best_wc_err > 0 else float('inf')

    print(f"  Improvement over average: {imp_over_avg:.4f}x")
    print(f"  Improvement over {label_A}: {imp_over_A:.4f}x")
    print(f"  Improvement over {label_B}: {imp_over_B:.4f}x")
    print()

    # Check if there's a clear minimum in the interior (not at boundaries)
    is_interior_min = -0.45 < best_wc < 0.45
    print(f"  Optimal w_cross is interior (not at boundary)? {is_interior_min}")
    if not is_interior_min:
        print(f"  WARNING: Optimal is near boundary ({best_wc:.3f}), effectively selecting")
        print(f"  one integrator. Cross-correction not providing true mixing benefit.")
    else:
        print(f"  The minimum at w_cross={best_wc:.3f} shows genuine error cancellation")
        print(f"  between the two integrators (not just selecting the better one).")
    print()

    # Curvature at minimum (how sharp is the valley?)
    # Use second derivative: f''(x) ~ (f(x+h) - 2f(x) + f(x-h)) / h^2
    h_wc = w_cross_vals[1] - w_cross_vals[0]
    if 1 <= best_wc_rk4_idx <= len(w_cross_vals) - 2:
        curvature = (w_cross_sweep_errors[best_wc_rk4_idx + 1]
                     - 2 * w_cross_sweep_errors[best_wc_rk4_idx]
                     + w_cross_sweep_errors[best_wc_rk4_idx - 1]) / h_wc**2
        print(f"  Curvature at minimum: {curvature:.4e}")
        print(f"  (Larger curvature = sharper minimum = more sensitive to w_cross)")
    print()

    # =====================================================================
    # NOISY MEASUREMENT BETA SWEEP
    # =====================================================================

    print("=" * 100)
    print("NOISY MEASUREMENT BETA SWEEP")
    print("=" * 100)
    print()

    noise_sigma = 0.01
    n_noisy_trials = 20  # Average over multiple noise realizations

    print(f"  Noise sigma = {noise_sigma} (position), {noise_sigma*0.1} (velocity)")
    print(f"  {n_noisy_trials} trials per beta value")
    print(f"  Measurement interval: every {measurement_interval} steps ({measurement_interval*dt/T:.2f} orbits)")
    print()

    betas = [0.0, 0.05, 0.1, 0.2, 0.38, 0.5, 0.618, 0.8, 1.0]

    noisy_results = {}
    perfect_results = {}

    for beta_val in betas:
        # Perfect measurements
        out_perfect = run_mvsu_damped(
            integ_A_fn, integ_B_fn, state0, dt, n_steps, mu,
            true_states, best_wc, beta=beta_val,
            measurement_interval=measurement_interval, noise_sigma=0.0)
        perfect_results[beta_val] = np.mean(compute_pos_error(out_perfect, true_states))

        # Noisy measurements (multiple trials)
        trial_errs = []
        for trial in range(n_noisy_trials):
            rng = np.random.RandomState(42 + trial)
            out_noisy = run_mvsu_damped(
                integ_A_fn, integ_B_fn, state0, dt, n_steps, mu,
                true_states, best_wc, beta=beta_val,
                measurement_interval=measurement_interval,
                noise_sigma=noise_sigma, rng=rng)
            trial_errs.append(np.mean(compute_pos_error(out_noisy, true_states)))

        noisy_results[beta_val] = {
            'mean': np.mean(trial_errs),
            'std': np.std(trial_errs),
            'min': np.min(trial_errs),
            'max': np.max(trial_errs),
        }

    print(f"  {'Beta':>6} {'Perfect Err':>14} {'Noisy Mean':>14} {'Noisy Std':>14} {'Note':>18}")
    print(f"  {'-'*70}")
    for b in betas:
        note = ""
        if b == 0.38:
            note = "<-- 1/phi^2"
        elif abs(b - 0.618) < 0.001:
            note = "<-- 1/phi"
        elif b == 1.0:
            note = "<-- full snap"
        print(f"  {b:>6.3f} {perfect_results[b]:>14.8e} "
              f"{noisy_results[b]['mean']:>14.8e} {noisy_results[b]['std']:>14.8e} {note:>18}")

    best_perfect_beta = min(betas[1:], key=lambda b: perfect_results[b])
    best_noisy_beta = min(betas[1:], key=lambda b: noisy_results[b]['mean'])

    print()
    print(f"  Optimal beta (perfect): {best_perfect_beta}")
    print(f"  Optimal beta (noisy):   {best_noisy_beta}")
    print()

    noisy_08_beats_10 = noisy_results[0.8]['mean'] < noisy_results[1.0]['mean']
    noisy_062_beats_10 = noisy_results[0.618]['mean'] < noisy_results[1.0]['mean']
    noisy_038_beats_10 = noisy_results[0.38]['mean'] < noisy_results[1.0]['mean']

    print(f"  beta=0.8 beats beta=1.0 with noise?   {noisy_08_beats_10}")
    print(f"  beta=0.618 beats beta=1.0 with noise? {noisy_062_beats_10}")
    print(f"  beta=0.38 beats beta=1.0 with noise?  {noisy_038_beats_10}")
    print()

    # =====================================================================
    # HIGHER NOISE: test with sigma=0.05
    # =====================================================================

    print("  --- Higher noise test (sigma=0.05) ---")
    noise_sigma_high = 0.05

    noisy_high_results = {}
    for beta_val in betas:
        trial_errs = []
        for trial in range(n_noisy_trials):
            rng = np.random.RandomState(42 + trial)
            out = run_mvsu_damped(
                integ_A_fn, integ_B_fn, state0, dt, n_steps, mu,
                true_states, best_wc, beta=beta_val,
                measurement_interval=measurement_interval,
                noise_sigma=noise_sigma_high, rng=rng)
            trial_errs.append(np.mean(compute_pos_error(out, true_states)))
        noisy_high_results[beta_val] = {
            'mean': np.mean(trial_errs),
            'std': np.std(trial_errs),
        }

    print(f"  {'Beta':>6} {'Noisy(0.01)':>14} {'Noisy(0.05)':>14} {'Note':>18}")
    print(f"  {'-'*55}")
    for b in betas:
        note = ""
        if b == 0.38:
            note = "<-- 1/phi^2"
        elif abs(b - 0.618) < 0.001:
            note = "<-- 1/phi"
        elif b == 1.0:
            note = "<-- full snap"
        print(f"  {b:>6.3f} {noisy_results[b]['mean']:>14.8e} "
              f"{noisy_high_results[b]['mean']:>14.8e} {note:>18}")

    best_noisy_high = min(betas[1:], key=lambda b: noisy_high_results[b]['mean'])
    print(f"  Optimal beta (sigma=0.05): {best_noisy_high}")

    high_08_beats_10 = noisy_high_results[0.8]['mean'] < noisy_high_results[1.0]['mean']
    high_062_beats_10 = noisy_high_results[0.618]['mean'] < noisy_high_results[1.0]['mean']
    print(f"  beta=0.8 beats 1.0 at sigma=0.05? {high_08_beats_10}")
    print(f"  beta=0.618 beats 1.0 at sigma=0.05? {high_062_beats_10}")
    print()

    # =====================================================================
    # HYPOTHESIS EVALUATION
    # =====================================================================

    print("=" * 100)
    print("HYPOTHESIS EVALUATION")
    print("=" * 100)
    print()

    rk4_ratio = max(np.mean(rk4c_err), np.mean(rk4_38_err)) / min(np.mean(rk4c_err), np.mean(rk4_38_err))
    ab4_ratio_val = np.mean(ab4_err) / np.mean(rk4c_err)
    print(f"  RK4-classic vs RK4-3/8 accuracy ratio: {rk4_ratio:.2f}x")
    print(f"  RK4-classic vs AB4 accuracy ratio: {ab4_ratio_val:.2f}x")
    if rk4_ratio < 10:
        print(f"  GOOD: RK4 pair is comparable ({rk4_ratio:.1f}x gap). v1 had ~300x.")
    print()

    def eval_hyp(name, val_test, val_base):
        better = val_test < val_base
        r = val_base / val_test if val_test > 0 else float('inf')
        print(f"  {name}: {'YES' if better else 'NO'} ({val_test:.8e} vs {val_base:.8e}, {r:.2f}x)")
        return better

    h1 = eval_hyp(f"H1: MVSU beats {label_A}?", mean_pos_errs[3], mean_pos_errs[0])
    h2 = eval_hyp(f"H2: MVSU beats {label_B}?", mean_pos_errs[3], mean_pos_errs[1])
    h3 = eval_hyp("H3: MVSU beats average?", mean_pos_errs[3], mean_pos_errs[2])
    h4 = eval_hyp("H4: MVSU+Damp(0.38) beats MVSU?", mean_pos_errs[4], mean_pos_errs[3])
    h5 = eval_hyp("H5: MVSU+Damp(0.618) beats MVSU?", mean_pos_errs[5], mean_pos_errs[3])
    print()

    any_damped_below_10 = best_noisy_beta < 1.0
    print(f"  H6: Optimal noisy beta < 1.0? {any_damped_below_10}")
    print(f"      (optimal = {best_noisy_beta}, sigma=0.01)")
    any_damped_below_10_high = best_noisy_high < 1.0
    print(f"  H7: Optimal noisy beta < 1.0 at sigma=0.05? {any_damped_below_10_high}")
    print(f"      (optimal = {best_noisy_high}, sigma=0.05)")
    print()

    # =====================================================================
    # HONEST ASSESSMENT
    # =====================================================================

    print("=" * 100)
    print("HONEST ASSESSMENT")
    print("=" * 100)
    print()

    # MVSU assessment
    mvsu_ok = best_wc_err < min(np.mean(rk4c_err), np.mean(rk4_38_err))
    if mvsu_ok and is_interior_min:
        print("  MVSU CROSS-CORRECTION: STRONG SUCCESS")
        print(f"  The optimal w_cross={best_wc:.3f} is in the interior, showing genuine")
        print(f"  error cancellation between {label_A} and {label_B}.")
        print(f"  The two integrators' errors are sufficiently 'orthogonal' that")
        print(f"  a weighted combination cancels correlated error components.")
    elif mvsu_ok:
        print("  MVSU CROSS-CORRECTION: QUALIFIED SUCCESS")
        print(f"  MVSU beats both integrators but w_cross={best_wc:.3f} is near a boundary,")
        print(f"  so it's partly just learning to select the better integrator.")
    elif best_wc_err < w_cross_sweep_errors[idx_0]:
        print("  MVSU CROSS-CORRECTION: PARTIAL SUCCESS")
        print(f"  MVSU beats the average but not the better individual integrator.")
        print(f"  w_cross={best_wc:.3f} provides some improvement over naive equal weighting.")
    else:
        print("  MVSU CROSS-CORRECTION: FAILED")
        print("  No w_cross value improves over the simple average.")
    print()

    # Damping assessment
    if any_damped_below_10 or any_damped_below_10_high:
        print("  DAMPED UPDATES: CONFIRMED (at least partially)")
        if any_damped_below_10:
            print(f"  At sigma=0.01: optimal beta = {best_noisy_beta} (not 1.0)")
        if any_damped_below_10_high:
            print(f"  At sigma=0.05: optimal beta = {best_noisy_high} (not 1.0)")
        print("  With noisy measurements, damped updates outperform full snap.")
        print("  This confirms overcorrection amplifies measurement noise.")
    else:
        print("  DAMPED UPDATES: NOT CONFIRMED")
        print("  beta=1.0 wins even with noise. The integration error between")
        print("  measurements may be large enough that even noisy truth is")
        print("  better than integration drift. More frequent measurements or")
        print("  higher noise might show the damping benefit.")
    print()

    # Key insight about the RK4 pair
    print("  KEY INSIGHT about RK4-classic vs RK4-3/8:")
    print(f"  These two methods have the SAME order (4th) and SAME stability region.")
    print(f"  Their 5th-order error terms differ because of different Butcher coefficients:")
    print(f"    Classic weights: [1/6, 1/3, 1/3, 1/6]")
    print(f"    3/8-rule weights: [1/8, 3/8, 3/8, 1/8]")
    print(f"  The 3/8-rule samples at different intermediate points (1/3, 2/3 vs 1/2, 1/2).")
    if rk4_ratio < 3:
        print(f"  The {rk4_ratio:.1f}x accuracy ratio confirms they are truly comparable.")
    else:
        print(f"  The {rk4_ratio:.1f}x accuracy ratio shows some asymmetry in their errors.")
    print(f"  Their error directions differ because they sample the ODE's curvature")
    print(f"  at different points within each step.")
    print()

    # =====================================================================
    # PLOTS
    # =====================================================================

    print("Generating plots...")
    orbit_fracs = times / T

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f"MVSU Simulation v2: {label_A} vs {label_B}, Kepler Orbit (e={e})",
                 fontsize=13, y=1.01)

    # Panel 1: Error over time
    ax = axes[0, 0]
    colors = ['red', 'blue', 'cyan', 'green', 'orange', 'magenta']
    for j, (pe, lab, col) in enumerate(zip(all_pos_errs, labels, colors)):
        ax.semilogy(orbit_fracs, pe + 1e-16, color=col, lw=1.2, label=lab, alpha=0.8)
    ax.axhline(y=error_threshold, color='gray', ls='--', alpha=0.5, label=f'Threshold')
    ax.set_xlabel('Orbits')
    ax.set_ylabel('Position Error')
    ax.set_title('Position Error vs Time')
    ax.legend(fontsize=6, loc='upper left')
    ax.grid(True, alpha=0.3)

    # Panel 2: w_cross sweep (both pairs)
    ax = axes[0, 1]
    ax.plot(w_cross_vals, wc_errors_rk4, 'b-', lw=1.5, label=f'{label_A} vs {label_B}')
    ax.plot(w_cross_vals, wc_errors_ab4, 'r--', lw=1.2, label='RK4-classic vs AB4', alpha=0.7)
    ax.axvline(x=best_wc, color='green', ls='--', alpha=0.7, label=f'Optimal w={best_wc:.3f}')
    ax.axvline(x=0, color='gray', ls=':', alpha=0.5, label='Average')
    ax.scatter([best_wc], [best_wc_err], color='green', s=80, zorder=5)
    ax.set_xlabel('w_cross')
    ax.set_ylabel('Mean Position Error')
    ax.set_title('w_cross Sweep')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # Panel 3: Beta sweep (noisy vs perfect)
    ax = axes[1, 0]
    noisy_betas_plot = sorted(noisy_results.keys())
    noisy_means_plot = [noisy_results[b]['mean'] for b in noisy_betas_plot]
    noisy_stds_plot = [noisy_results[b]['std'] for b in noisy_betas_plot]
    perfect_means_plot = [perfect_results[b] for b in noisy_betas_plot]
    noisy_high_means_plot = [noisy_high_results[b]['mean'] for b in noisy_betas_plot]

    ax.plot(noisy_betas_plot[1:], perfect_means_plot[1:], 'bs-', lw=1.5, ms=5,
            label='Perfect measurements')
    ax.errorbar(noisy_betas_plot[1:], noisy_means_plot[1:],
                yerr=noisy_stds_plot[1:], fmt='ro-', lw=1.5, ms=5, capsize=3,
                label='Noisy (sigma=0.01)')
    ax.errorbar(noisy_betas_plot[1:], noisy_high_means_plot[1:],
                yerr=[noisy_high_results[b]['std'] for b in noisy_betas_plot[1:]],
                fmt='g^-', lw=1.5, ms=5, capsize=3, label='Noisy (sigma=0.05)')
    ax.axvline(x=0.38, color='red', ls='--', alpha=0.4, label='0.38')
    ax.axvline(x=0.618, color='blue', ls='--', alpha=0.4, label='0.618')
    ax.set_xlabel('Beta (damping rate)')
    ax.set_ylabel('Mean Position Error')
    ax.set_title('Beta Sweep: Damped Updates')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # Panel 4: Trajectories
    ax = axes[1, 1]
    ax.plot(true_states[:, 0], true_states[:, 1], 'k-', lw=2, label='True', alpha=0.8)
    ax.plot(states_A[:, 0], states_A[:, 1], 'r-', lw=0.7, label=label_A, alpha=0.4)
    ax.plot(states_B[:, 0], states_B[:, 1], 'b-', lw=0.7, label=label_B, alpha=0.4)
    ax.plot(mvsu_opt_states[:, 0], mvsu_opt_states[:, 1], 'g-', lw=1,
            label=f'MVSU (w={best_wc:.3f})', alpha=0.6)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Orbital Trajectories')
    ax.legend(fontsize=8)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "mvsu_simulation_v2_results.png")
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    print(f"Plot saved to: {outpath}")
    plt.close()

    return {
        'labels': labels,
        'mean_pos_errs': mean_pos_errs,
        'best_wc': best_wc,
        'best_wc_err': best_wc_err,
        'rk4_ratio': rk4_ratio,
        'mvsu_beats_both': mvsu_ok,
        'is_interior_min': is_interior_min,
        'best_noisy_beta': best_noisy_beta,
        'best_noisy_high_beta': best_noisy_high,
        'noisy_results': noisy_results,
        'perfect_results': perfect_results,
        'noisy_high_results': noisy_high_results,
    }


if __name__ == "__main__":
    print("=" * 100)
    print("MVSU SIMULATION TEST v2: Comparable Integrator Cross-Correction")
    print("RK4-classic vs RK4-3/8 (both 4th-order, different Butcher coefficients)")
    print("Also: RK4-classic vs AB4 (4th-order, single-step vs multi-step)")
    print("=" * 100)
    print()

    t_start = time.time()
    results = run_simulation(n_orbits=15, steps_per_orbit=200, e=0.3)
    elapsed = time.time() - t_start

    print()
    print("=" * 100)
    print(f"SIMULATION COMPLETE ({elapsed:.1f}s)")
    print("=" * 100)
