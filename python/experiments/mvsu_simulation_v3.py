"""
MVSU Simulation Test v3: RK4 vs Adams-Bashforth 4 -- Thorough Cross-Correction
================================================================================
Building on v2's finding that RK4 vs AB4 showed 1.6x improvement via MVSU
cross-correction. The key insight: RK4 (single-step, 4 intermediate evaluations)
and AB4 (multi-step, uses derivative history) have structurally different truncation
errors, giving genuinely orthogonal error directions -- exactly what MVSU needs.

This version:
  - Accuracy-matches the two integrators (AB4 with substeps if needed, or ABM predictor-corrector)
  - Computes error CORRELATION between channels (the key diagnostic)
  - Fine w_cross sweep from -0.5 to 1.5
  - Online-learned w_cross via gradient descent
  - MVSU + damped noisy measurements at multiple beta values
  - Comprehensive metrics and 5 diagnostic plots

Author: Claude (MVSU Simulation Experiment v3)
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
from matplotlib.gridspec import GridSpec


# =============================================================================
# Kepler Orbit: Exact Solution
# =============================================================================

def kepler_eccentric_anomaly(M, e, tol=1e-14, max_iter=200):
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


def rk4_step(state, dt, mu):
    """Classical 4th-order Runge-Kutta."""
    k1 = deriv(state, mu)
    k2 = deriv(state + 0.5 * dt * k1, mu)
    k3 = deriv(state + 0.5 * dt * k2, mu)
    k4 = deriv(state + dt * k3, mu)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def ab4_step(state, dt, mu, f_history):
    """Adams-Bashforth 4-step explicit method.

    y_{n+1} = y_n + (dt/24)(55*f_n - 59*f_{n-1} + 37*f_{n-2} - 9*f_{n-3})

    f_history = [f_{n-3}, f_{n-2}, f_{n-1}, f_n] (oldest to newest)
    """
    fn_3, fn_2, fn_1, fn = f_history
    return state + (dt / 24.0) * (55*fn - 59*fn_1 + 37*fn_2 - 9*fn_3)


def abm4_step(state, dt, mu, f_history):
    """Adams-Bashforth-Moulton 4th-order predictor-corrector.

    Predictor (AB4): y*_{n+1} = y_n + (dt/24)(55*f_n - 59*f_{n-1} + 37*f_{n-2} - 9*f_{n-3})
    Corrector (AM4): y_{n+1} = y_n + (dt/24)(9*f*_{n+1} + 19*f_n - 5*f_{n-1} + f_{n-2})

    The corrector uses the predicted value to evaluate f*_{n+1}, then corrects.
    This is PECE mode (Predict-Evaluate-Correct-Evaluate).
    """
    fn_3, fn_2, fn_1, fn = f_history
    # Predict
    y_pred = state + (dt / 24.0) * (55*fn - 59*fn_1 + 37*fn_2 - 9*fn_3)
    # Evaluate at predicted point
    f_pred = deriv(y_pred, mu)
    # Correct
    y_corr = state + (dt / 24.0) * (9*f_pred + 19*fn - 5*fn_1 + fn_2)
    return y_corr


# =============================================================================
# Integration runners
# =============================================================================

def run_rk4(state0, dt, n_steps, mu):
    """Run RK4 for n_steps."""
    n = n_steps + 1
    states = np.zeros((n, 4))
    states[0] = state0.copy()
    for i in range(n_steps):
        states[i + 1] = rk4_step(states[i], dt, mu)
    return states


def run_ab4(state0, dt, n_steps, mu):
    """Run AB4 with RK4 bootstrap for first 3 steps."""
    n = n_steps + 1
    states = np.zeros((n, 4))
    states[0] = state0.copy()

    # Bootstrap with RK4 for 3 steps
    f_hist = [deriv(state0, mu)]
    for i in range(min(3, n_steps)):
        states[i + 1] = rk4_step(states[i], dt, mu)
        f_hist.append(deriv(states[i + 1], mu))

    # AB4 for remaining steps
    for i in range(3, n_steps):
        states[i + 1] = ab4_step(states[i], dt, mu, f_hist)
        f_hist.pop(0)
        f_hist.append(deriv(states[i + 1], mu))

    return states


def run_abm4(state0, dt, n_steps, mu):
    """Run ABM4 (predictor-corrector) with RK4 bootstrap for first 3 steps."""
    n = n_steps + 1
    states = np.zeros((n, 4))
    states[0] = state0.copy()

    # Bootstrap with RK4 for 3 steps
    f_hist = [deriv(state0, mu)]
    for i in range(min(3, n_steps)):
        states[i + 1] = rk4_step(states[i], dt, mu)
        f_hist.append(deriv(states[i + 1], mu))

    # ABM4 for remaining steps
    for i in range(3, n_steps):
        states[i + 1] = abm4_step(states[i], dt, mu, f_hist)
        f_hist.pop(0)
        f_hist.append(deriv(states[i + 1], mu))

    return states


def run_ab4_substep(state0, dt_outer, n_steps, mu, sub_factor=2):
    """Run AB4 with substeps to improve accuracy.

    Takes sub_factor substeps of size dt_outer/sub_factor for each outer step.
    Records state only at outer step boundaries for comparison with RK4.
    """
    dt_inner = dt_outer / sub_factor
    n_inner_total = n_steps * sub_factor
    n = n_steps + 1
    states = np.zeros((n, 4))
    states[0] = state0.copy()

    # Bootstrap with RK4 for first 3 inner steps
    cur = state0.copy()
    f_hist = [deriv(cur, mu)]
    for i in range(min(3, n_inner_total)):
        cur = rk4_step(cur, dt_inner, mu)
        f_hist.append(deriv(cur, mu))
        # Record at outer step boundaries
        if (i + 1) % sub_factor == 0:
            outer_idx = (i + 1) // sub_factor
            if outer_idx < n:
                states[outer_idx] = cur.copy()

    # AB4 for remaining inner steps
    inner_step = min(3, n_inner_total)
    for i in range(inner_step, n_inner_total):
        cur = ab4_step(cur, dt_inner, mu, f_hist)
        f_hist.pop(0)
        f_hist.append(deriv(cur, mu))
        if (i + 1) % sub_factor == 0:
            outer_idx = (i + 1) // sub_factor
            if outer_idx < n:
                states[outer_idx] = cur.copy()

    return states


# =============================================================================
# MVSU Cross-Correction
# =============================================================================

def mvsu_combine(state_A, state_B, w_cross):
    """MVSU cross-corrected output.

    output = state_A + w_cross * (state_A - state_B)

    w_cross = 0:   pure A
    w_cross = -1:  pure B
    w_cross = -0.5: simple average
    w_cross > 0:   extrapolate AWAY from B (use disagreement as error signal)

    The MVSU hypothesis: if A's error is correlated with (A-B), then we can
    use the disagreement to partially cancel A's error.
    """
    return state_A + w_cross * (state_A - state_B)


# =============================================================================
# Error and Correlation Diagnostics
# =============================================================================

def compute_pos_error(states, true_states):
    """Position error magnitude over time."""
    return np.sqrt((states[:, 0] - true_states[:, 0])**2 +
                   (states[:, 1] - true_states[:, 1])**2)


def compute_error_vectors(states, true_states):
    """Position error vectors (x,y) over time."""
    return states[:, :2] - true_states[:, :2]


def compute_error_correlation(err_vec_A, err_vec_B):
    """Compute correlation between error vectors at each timestep.

    Returns:
      - per-step correlation (cosine similarity of error vectors)
      - overall Pearson correlation of error magnitudes
      - overall vector correlation (correlation of flattened error components)
    """
    n = len(err_vec_A)

    # Per-step cosine similarity
    cos_sim = np.zeros(n)
    for i in range(n):
        a = err_vec_A[i]
        b = err_vec_B[i]
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a > 1e-20 and norm_b > 1e-20:
            cos_sim[i] = np.dot(a, b) / (norm_a * norm_b)
        else:
            cos_sim[i] = 0.0

    # Overall Pearson correlation of error magnitudes
    mag_A = np.sqrt(err_vec_A[:, 0]**2 + err_vec_A[:, 1]**2)
    mag_B = np.sqrt(err_vec_B[:, 0]**2 + err_vec_B[:, 1]**2)
    if np.std(mag_A) > 1e-20 and np.std(mag_B) > 1e-20:
        mag_corr = np.corrcoef(mag_A, mag_B)[0, 1]
    else:
        mag_corr = 1.0

    # Component-wise Pearson correlation (x errors, y errors)
    if np.std(err_vec_A[:, 0]) > 1e-20 and np.std(err_vec_B[:, 0]) > 1e-20:
        x_corr = np.corrcoef(err_vec_A[:, 0], err_vec_B[:, 0])[0, 1]
    else:
        x_corr = 1.0
    if np.std(err_vec_A[:, 1]) > 1e-20 and np.std(err_vec_B[:, 1]) > 1e-20:
        y_corr = np.corrcoef(err_vec_A[:, 1], err_vec_B[:, 1])[0, 1]
    else:
        y_corr = 1.0

    return {
        'cosine_per_step': cos_sim,
        'magnitude_correlation': mag_corr,
        'x_correlation': x_corr,
        'y_correlation': y_corr,
        'mean_cosine': np.mean(cos_sim[1:]),  # skip step 0 (zero error)
    }


# =============================================================================
# Damped measurement integration
# =============================================================================

def run_rk4_damped(state0, dt, n_steps, mu, true_states, beta,
                   measurement_interval, noise_sigma=0.0, rng=None):
    """Run RK4 with damped ground truth updates (no MVSU, single channel)."""
    n = n_steps + 1
    states = np.zeros((n, 4))
    states[0] = state0.copy()
    cur = state0.copy()

    for i in range(n_steps):
        cur = rk4_step(cur, dt, mu)
        states[i + 1] = cur.copy()

        if (i + 1) % measurement_interval == 0 and beta > 0:
            meas = true_states[i + 1].copy()
            if noise_sigma > 0 and rng is not None:
                meas[0] += rng.normal(0, noise_sigma)
                meas[1] += rng.normal(0, noise_sigma)
                meas[2] += rng.normal(0, noise_sigma * 0.1)
                meas[3] += rng.normal(0, noise_sigma * 0.1)
            cur += beta * (meas - cur)
            states[i + 1] = cur.copy()

    return states


def run_mvsu_damped_ab4(state0, dt, n_steps, mu, true_states, w_cross, beta,
                        measurement_interval, noise_sigma=0.0, rng=None,
                        use_abm=False, sub_factor=1):
    """Run RK4 + AB4/ABM4 with MVSU cross-correction and damped measurements.

    Both channels integrate independently. At measurement points, both are
    nudged toward (possibly noisy) ground truth. MVSU combines at each step.

    For AB4: after a measurement nudge, we re-bootstrap the derivative history
    from the nudged state (using RK4 for 3 mini-steps forward/backward).
    Actually, simpler: we just update f_history with the new derivative at
    the nudged state. The next few AB4 steps will use a mix of pre- and
    post-nudge derivatives, which is imperfect but workable.
    """
    n = n_steps + 1
    output = np.zeros((n, 4))
    output[0] = state0.copy()

    ch_A = state0.copy()  # RK4 channel
    ch_B = state0.copy()  # AB4/ABM4 channel

    dt_inner = dt / sub_factor if sub_factor > 1 else dt
    step_fn = abm4_step if use_abm else ab4_step

    # Bootstrap AB4 derivative history
    f_hist = [deriv(state0, mu)]
    bootstrap_done = False
    bootstrap_count = 0

    for i in range(n_steps):
        # RK4 channel: one step
        ch_A = rk4_step(ch_A, dt, mu)

        # AB4/ABM4 channel
        if sub_factor > 1:
            # Multiple substeps
            for s in range(sub_factor):
                inner_total = i * sub_factor + s
                if inner_total < 3:
                    ch_B = rk4_step(ch_B, dt_inner, mu)
                    f_hist.append(deriv(ch_B, mu))
                    bootstrap_count = inner_total + 1
                else:
                    if not bootstrap_done and len(f_hist) >= 4:
                        bootstrap_done = True
                    if bootstrap_done:
                        ch_B = step_fn(ch_B, dt_inner, mu, f_hist[-4:])
                        f_hist.append(deriv(ch_B, mu))
                    else:
                        ch_B = rk4_step(ch_B, dt_inner, mu)
                        f_hist.append(deriv(ch_B, mu))
        else:
            if i < 3:
                ch_B = rk4_step(ch_B, dt, mu)
                f_hist.append(deriv(ch_B, mu))
            else:
                if len(f_hist) >= 4:
                    ch_B = step_fn(ch_B, dt, mu, f_hist[-4:])
                else:
                    ch_B = rk4_step(ch_B, dt, mu)
                f_hist.append(deriv(ch_B, mu))

        output[i + 1] = mvsu_combine(ch_A, ch_B, w_cross)

        # Damped measurement update
        if (i + 1) % measurement_interval == 0 and beta > 0:
            meas = true_states[i + 1].copy()
            if noise_sigma > 0 and rng is not None:
                meas[0] += rng.normal(0, noise_sigma)
                meas[1] += rng.normal(0, noise_sigma)
                meas[2] += rng.normal(0, noise_sigma * 0.1)
                meas[3] += rng.normal(0, noise_sigma * 0.1)

            ch_A += beta * (meas - ch_A)
            ch_B += beta * (meas - ch_B)

            # Reset AB4 derivative history after nudge
            f_hist = [deriv(ch_B, mu)]
            # Re-bootstrap: next 3 steps will use RK4
            bootstrap_done = False
            bootstrap_count = 0
            # But we need at least 4 entries in f_hist for AB4
            # We'll accumulate them over the next 3 steps

            output[i + 1] = mvsu_combine(ch_A, ch_B, w_cross)

    return output


def run_online_mvsu(state0, dt, n_steps, mu, true_states,
                    learning_rate=0.1, lookback=50, use_abm=False,
                    sub_factor=1):
    """Run MVSU with online-learned w_cross via gradient descent on recent error.

    Every `lookback` steps, estimate the gradient of error w.r.t. w_cross
    using the recent history, and update w_cross. Uses NORMALIZED gradient
    to handle the tiny error magnitudes at 4th-order accuracy.

    Channel B uses AB4/ABM4 with optional substeps to match the accuracy
    of Channel A (RK4).
    """
    n = n_steps + 1
    output = np.zeros((n, 4))
    w_cross_history = np.zeros(n)
    output[0] = state0.copy()

    ch_A = state0.copy()  # RK4
    ch_B = state0.copy()  # AB4/ABM4

    step_fn = abm4_step if use_abm else ab4_step
    dt_inner = dt / sub_factor if sub_factor > 1 else dt

    f_hist = [deriv(state0, mu)]
    w_cross = 0.0  # Start neutral (pure RK4)
    w_cross_history[0] = w_cross

    # Store recent channel states for gradient estimation
    recent_A = []
    recent_B = []
    recent_true = []

    bootstrap_done = False

    for i in range(n_steps):
        ch_A = rk4_step(ch_A, dt, mu)

        # Channel B with substeps
        if sub_factor > 1:
            for s in range(sub_factor):
                inner_total = i * sub_factor + s
                if inner_total < 3:
                    ch_B = rk4_step(ch_B, dt_inner, mu)
                    f_hist.append(deriv(ch_B, mu))
                else:
                    if len(f_hist) >= 4:
                        ch_B = step_fn(ch_B, dt_inner, mu, f_hist[-4:])
                    else:
                        ch_B = rk4_step(ch_B, dt_inner, mu)
                    f_hist.append(deriv(ch_B, mu))
        else:
            if i < 3:
                ch_B = rk4_step(ch_B, dt, mu)
                f_hist.append(deriv(ch_B, mu))
            else:
                if len(f_hist) >= 4:
                    ch_B = step_fn(ch_B, dt, mu, f_hist[-4:])
                else:
                    ch_B = rk4_step(ch_B, dt, mu)
                f_hist.append(deriv(ch_B, mu))

        output[i + 1] = mvsu_combine(ch_A, ch_B, w_cross)
        w_cross_history[i + 1] = w_cross

        recent_A.append(ch_A[:2].copy())
        recent_B.append(ch_B[:2].copy())
        recent_true.append(true_states[i + 1, :2].copy())

        # Online gradient descent on w_cross every `lookback` steps
        if (i + 1) % lookback == 0 and len(recent_A) >= lookback:
            # Analytic optimal: minimize sum |A + w*(A-B) - T|^2 over recent window
            # d/dw [ |A + w*(A-B) - T|^2 ] = 0
            # sum[ (A-T) . (A-B) + w * |A-B|^2 ] = 0
            # w* = -sum[ (A-T) . (A-B) ] / sum[ |A-B|^2 ]
            numerator = 0.0
            denominator = 0.0
            for j in range(-lookback, 0):
                a = np.array(recent_A[j])
                b = np.array(recent_B[j])
                t = np.array(recent_true[j])
                err_A = a - t  # RK4 error
                diff = a - b   # disagreement
                numerator += np.dot(err_A, diff)
                denominator += np.dot(diff, diff)

            if denominator > 1e-30:
                w_optimal_local = -numerator / denominator
                # Exponential moving average toward local optimal
                w_cross = (1 - learning_rate) * w_cross + learning_rate * w_optimal_local
                w_cross = np.clip(w_cross, -1.5, 1.5)

            # Keep only recent history
            recent_A = recent_A[-lookback:]
            recent_B = recent_B[-lookback:]
            recent_true = recent_true[-lookback:]

    return output, w_cross_history


# =============================================================================
# Main Simulation
# =============================================================================

def run_simulation(n_orbits=20, steps_per_orbit=200, e=0.3):
    """Run all conditions and collect metrics."""

    a = 1.0
    mu = 1.0
    T = 2.0 * np.pi * np.sqrt(a**3 / mu)
    n_steps = n_orbits * steps_per_orbit
    dt = T * n_orbits / n_steps

    print(f"Kepler Orbit Parameters:")
    print(f"  Semi-major axis a = {a}")
    print(f"  Eccentricity e = {e}")
    print(f"  Period T = {T:.6f}")
    print(f"  n_orbits = {n_orbits}, steps/orbit = {steps_per_orbit}")
    print(f"  Total steps = {n_steps}, dt = {dt:.8f}")
    print()

    # Initial conditions at periapsis
    x0 = a * (1.0 - e)
    y0 = 0.0
    vx0 = 0.0
    vy0 = np.sqrt(mu * (1.0 + e) / (a * (1.0 - e)))
    state0 = np.array([x0, y0, vx0, vy0])
    E0 = orbital_energy(state0, mu)

    print(f"  Initial state: [{x0:.6f}, {y0:.6f}, {vx0:.6f}, {vy0:.6f}]")
    print(f"  Initial energy: {E0:.10f} (expected: {-mu/(2*a):.10f})")
    print()

    # Pre-compute true solution
    n = n_steps + 1
    times = np.linspace(0, T * n_orbits, n)
    true_states = np.zeros((n, 4))
    true_states[0] = state0
    for i in range(1, n):
        true_states[i] = np.array(kepler_true_state(times[i], a, e, mu))

    measurement_interval = 50  # every 50 steps as specified

    # =====================================================================
    # Step 1: Run the integrators and assess accuracy
    # =====================================================================

    print("=" * 100)
    print("STEP 1: INTEGRATOR ACCURACY COMPARISON")
    print("=" * 100)
    print()

    print("  Running RK4...")
    rk4_states = run_rk4(state0, dt, n_steps, mu)
    rk4_err = compute_pos_error(rk4_states, true_states)
    rk4_mean = np.mean(rk4_err)
    print(f"    Mean error: {rk4_mean:.10e}")
    print(f"    Final error: {rk4_err[-1]:.10e}")
    print()

    print("  Running AB4 (same dt)...")
    ab4_states = run_ab4(state0, dt, n_steps, mu)
    ab4_err = compute_pos_error(ab4_states, true_states)
    ab4_mean = np.mean(ab4_err)
    print(f"    Mean error: {ab4_mean:.10e}")
    print(f"    Final error: {ab4_err[-1]:.10e}")
    print(f"    Ratio AB4/RK4: {ab4_mean/rk4_mean:.2f}x")
    print()

    print("  Running ABM4 predictor-corrector (same dt)...")
    abm4_states = run_abm4(state0, dt, n_steps, mu)
    abm4_err = compute_pos_error(abm4_states, true_states)
    abm4_mean = np.mean(abm4_err)
    print(f"    Mean error: {abm4_mean:.10e}")
    print(f"    Final error: {abm4_err[-1]:.10e}")
    print(f"    Ratio ABM4/RK4: {abm4_mean/rk4_mean:.2f}x")
    print()

    print("  Running AB4 with 2x substeps...")
    ab4_sub2_states = run_ab4_substep(state0, dt, n_steps, mu, sub_factor=2)
    ab4_sub2_err = compute_pos_error(ab4_sub2_states, true_states)
    ab4_sub2_mean = np.mean(ab4_sub2_err)
    print(f"    Mean error: {ab4_sub2_mean:.10e}")
    print(f"    Ratio AB4-2x/RK4: {ab4_sub2_mean/rk4_mean:.2f}x")
    print()

    # Choose best Channel B: whichever is closest to RK4 accuracy
    candidates = {
        'AB4': (ab4_states, ab4_mean, ab4_err),
        'ABM4': (abm4_states, abm4_mean, abm4_err),
        'AB4-2x': (ab4_sub2_states, ab4_sub2_mean, ab4_sub2_err),
    }

    # Pick the one whose accuracy ratio to RK4 is closest to 1.0
    best_name = min(candidates.keys(), key=lambda k: abs(np.log(candidates[k][1] / rk4_mean)))
    chB_states, chB_mean, chB_err = candidates[best_name]

    # But also report all for transparency
    print(f"  ACCURACY MATCHING SUMMARY:")
    for name, (_, mean_e, _) in candidates.items():
        ratio = mean_e / rk4_mean
        marker = " <-- SELECTED" if name == best_name else ""
        print(f"    {name:>8}: ratio to RK4 = {ratio:.4f}x{marker}")
    print()
    print(f"  Selected Channel B: {best_name} (ratio {chB_mean/rk4_mean:.4f}x to RK4)")
    print()

    # Also keep all for comparison in w_cross sweep
    use_abm_flag = (best_name == 'ABM4')
    sub_factor_flag = 2 if best_name == 'AB4-2x' else 1

    # =====================================================================
    # Step 2: ERROR CORRELATION ANALYSIS (Key Diagnostic)
    # =====================================================================

    print("=" * 100)
    print("STEP 2: ERROR CORRELATION ANALYSIS (KEY DIAGNOSTIC)")
    print("=" * 100)
    print()

    err_vec_rk4 = compute_error_vectors(rk4_states, true_states)
    err_vec_chB = compute_error_vectors(chB_states, true_states)

    corr = compute_error_correlation(err_vec_rk4, err_vec_chB)

    print(f"  Error vector analysis (RK4 vs {best_name}):")
    print(f"    Mean cosine similarity:  {corr['mean_cosine']:.6f}")
    print(f"    Magnitude correlation:   {corr['magnitude_correlation']:.6f}")
    print(f"    X-component correlation: {corr['x_correlation']:.6f}")
    print(f"    Y-component correlation: {corr['y_correlation']:.6f}")
    print()

    mc = corr['mean_cosine']
    if mc > 0.9:
        corr_assessment = "HIGH (>0.9): Errors are nearly parallel. Cross-correction has LIMITED potential."
    elif mc > 0.7:
        corr_assessment = "MODERATE-HIGH (0.7-0.9): Some angle between errors. Modest cross-correction possible."
    elif mc > 0.3:
        corr_assessment = "MODERATE (0.3-0.7): Significant angular diversity. GOOD cross-correction potential."
    else:
        corr_assessment = "LOW (<0.3): Nearly orthogonal errors. EXCELLENT cross-correction potential."

    print(f"  CORRELATION ASSESSMENT: {corr_assessment}")
    print()

    # Also check for ALL candidate pairs
    print(f"  Cross-correlation for ALL candidate pairs:")
    for name, (states_cand, _, _) in candidates.items():
        ev = compute_error_vectors(states_cand, true_states)
        c = compute_error_correlation(err_vec_rk4, ev)
        print(f"    RK4 vs {name:>8}: cos_sim={c['mean_cosine']:.4f}, "
              f"mag_corr={c['magnitude_correlation']:.4f}")
    print()

    # =====================================================================
    # Step 3: W_CROSS SWEEP
    # =====================================================================

    print("=" * 100)
    print("STEP 3: W_CROSS SWEEP (fine, 100 points)")
    print("=" * 100)
    print()

    # Formulation: pos_mvsu = pos_RK4 + w_cross * (pos_RK4 - pos_chB)
    # w_cross = 0: pure RK4
    # w_cross = -1: pure chB
    # w_cross = -0.5: average
    # w_cross > 0: extrapolate away from chB

    w_vals = np.linspace(-1.5, 1.5, 301)
    w_errors = np.zeros(len(w_vals))

    for wi, wc in enumerate(w_vals):
        combined = mvsu_combine(rk4_states, chB_states, wc)
        w_errors[wi] = np.mean(compute_pos_error(combined, true_states))

    best_wi = np.argmin(w_errors)
    best_wc = w_vals[best_wi]
    best_wc_err = w_errors[best_wi]

    # Key reference points
    idx_0 = np.argmin(np.abs(w_vals))      # w=0, pure RK4
    idx_m1 = np.argmin(np.abs(w_vals + 1))  # w=-1, pure chB
    idx_m05 = np.argmin(np.abs(w_vals + 0.5))  # w=-0.5, average

    err_rk4_only = w_errors[idx_0]
    err_chB_only = w_errors[idx_m1]
    err_average = w_errors[idx_m05]

    print(f"  w_cross =  0.00 (pure RK4):    {err_rk4_only:.10e}")
    print(f"  w_cross = -1.00 (pure {best_name:>5}):  {err_chB_only:.10e}")
    print(f"  w_cross = -0.50 (average):      {err_average:.10e}")
    print(f"  w_cross = {best_wc:+.4f} (OPTIMAL):    {best_wc_err:.10e}")
    print()

    imp_rk4 = err_rk4_only / best_wc_err if best_wc_err > 0 else float('inf')
    imp_chB = err_chB_only / best_wc_err if best_wc_err > 0 else float('inf')
    imp_avg = err_average / best_wc_err if best_wc_err > 0 else float('inf')

    print(f"  Improvement over RK4:     {imp_rk4:.4f}x")
    print(f"  Improvement over {best_name:>5}:   {imp_chB:.4f}x")
    print(f"  Improvement over average: {imp_avg:.4f}x")
    print()

    # Is the optimal w_cross actually nonzero and in the interior?
    # Interior means not at the boundary of the sweep range
    is_nonzero = abs(best_wc) > 0.01
    is_interior = -1.4 < best_wc < 1.4
    beats_both = best_wc_err < min(err_rk4_only, err_chB_only)
    beats_avg = best_wc_err < err_average

    print(f"  Optimal w_cross is nonzero (|w| > 0.01)?  {is_nonzero} (w={best_wc:.4f})")
    print(f"  Optimal w_cross is interior?               {is_interior}")
    print(f"  MVSU beats BOTH individual integrators?    {beats_both}")
    print(f"  MVSU beats simple average?                 {beats_avg}")
    print()

    if is_nonzero and beats_both:
        print("  >>> THE MVSU PRINCIPLE IS WORKING: The disagreement between RK4 and")
        print(f"  >>> {best_name} contains extractable information about the true solution.")
        if best_wc > 0:
            print(f"  >>> w_cross > 0 means: extrapolating AWAY from {best_name} helps.")
            print(f"  >>> Interpretation: RK4's error has a component in the direction of")
            print(f"  >>> (RK4 - {best_name}), so subtracting that component improves accuracy.")
        else:
            print(f"  >>> w_cross < 0 means: moving TOWARD {best_name} from RK4 helps.")
    elif beats_avg and not beats_both:
        print("  >>> PARTIAL: w_cross helps vs average, but the sweep mostly selects")
        print("  >>> the better integrator rather than extracting cross-information.")
    else:
        print("  >>> NO CROSS-CORRECTION BENEFIT found in the w_cross sweep.")
    print()

    # Do the sweep for all 3 candidate pairs for comparison
    print(f"  W_CROSS SWEEP FOR ALL CANDIDATE PAIRS:")
    all_pair_results = {}
    for name, (states_cand, _, _) in candidates.items():
        w_errs_cand = np.zeros(len(w_vals))
        for wi, wc in enumerate(w_vals):
            combined = mvsu_combine(rk4_states, states_cand, wc)
            w_errs_cand[wi] = np.mean(compute_pos_error(combined, true_states))

        best_w_cand = w_vals[np.argmin(w_errs_cand)]
        best_e_cand = np.min(w_errs_cand)
        imp_cand = err_rk4_only / best_e_cand if best_e_cand > 0 else float('inf')
        all_pair_results[name] = (w_vals, w_errs_cand, best_w_cand, best_e_cand)

        print(f"    RK4 vs {name:>8}: optimal w={best_w_cand:+.4f}, "
              f"error={best_e_cand:.6e}, improvement over RK4: {imp_cand:.4f}x")
    print()

    # =====================================================================
    # Step 4: MVSU OPTIMAL output
    # =====================================================================

    mvsu_opt_states = mvsu_combine(rk4_states, chB_states, best_wc)
    mvsu_opt_err = compute_pos_error(mvsu_opt_states, true_states)

    # Simple average
    avg_states = mvsu_combine(rk4_states, chB_states, -0.5)
    avg_err = compute_pos_error(avg_states, true_states)

    # =====================================================================
    # Step 5: ONLINE-LEARNED W_CROSS
    # =====================================================================

    print("=" * 100)
    print("STEP 5: ONLINE-LEARNED W_CROSS (gradient descent)")
    print("=" * 100)
    print()

    # Note: online learning uses ground truth for gradient, which is "cheating"
    # in a real scenario. But it demonstrates the principle. In practice you'd
    # use the disagreement magnitude as a proxy.
    online_states, online_wc_hist = run_online_mvsu(
        state0, dt, n_steps, mu, true_states,
        learning_rate=0.3, lookback=50, use_abm=use_abm_flag,
        sub_factor=sub_factor_flag)
    online_err = compute_pos_error(online_states, true_states)

    print(f"  Online w_cross: started at 0.0")
    print(f"  Online w_cross final value: {online_wc_hist[-1]:.6f}")
    print(f"  Online w_cross mean (after burn-in): {np.mean(online_wc_hist[n_steps//4:]):.6f}")
    print(f"  Sweep optimal w_cross: {best_wc:.6f}")
    print(f"  Online mean error: {np.mean(online_err):.10e}")
    print(f"  Improvement over RK4: {rk4_mean / np.mean(online_err):.4f}x")
    print()

    # =====================================================================
    # Step 6: DAMPED NOISY MEASUREMENTS
    # =====================================================================

    print("=" * 100)
    print("STEP 6: DAMPED NOISY MEASUREMENTS")
    print("=" * 100)
    print()

    noise_sigma = 0.01
    n_trials = 15

    print(f"  Noise sigma = {noise_sigma} (position), {noise_sigma*0.1} (velocity)")
    print(f"  Measurement interval: every {measurement_interval} steps")
    print(f"  {n_trials} trials per condition, averaged")
    print()

    betas_test = [0.38, 0.62, 0.80]

    # Condition 6-8: MVSU + damped noisy measurements at various beta
    mvsu_damp_results = {}
    for beta_val in betas_test:
        trial_errs = []
        trial_states = None
        for trial in range(n_trials):
            rng = np.random.RandomState(42 + trial)
            out = run_mvsu_damped_ab4(
                state0, dt, n_steps, mu, true_states, best_wc, beta=beta_val,
                measurement_interval=measurement_interval,
                noise_sigma=noise_sigma, rng=rng, use_abm=use_abm_flag,
                sub_factor=sub_factor_flag)
            trial_errs.append(np.mean(compute_pos_error(out, true_states)))
            if trial == 0:
                trial_states = out
        mvsu_damp_results[beta_val] = {
            'mean': np.mean(trial_errs),
            'std': np.std(trial_errs),
            'states': trial_states,
            'err': compute_pos_error(trial_states, true_states),
        }

    # Condition 9: RK4 + damped noisy measurements only (no MVSU)
    rk4_damp_results = {}
    for beta_val in betas_test:
        trial_errs = []
        trial_states = None
        for trial in range(n_trials):
            rng = np.random.RandomState(42 + trial)
            out = run_rk4_damped(
                state0, dt, n_steps, mu, true_states, beta=beta_val,
                measurement_interval=measurement_interval,
                noise_sigma=noise_sigma, rng=rng)
            trial_errs.append(np.mean(compute_pos_error(out, true_states)))
            if trial == 0:
                trial_states = out
        rk4_damp_results[beta_val] = {
            'mean': np.mean(trial_errs),
            'std': np.std(trial_errs),
            'states': trial_states,
            'err': compute_pos_error(trial_states, true_states),
        }

    # Also do a fine beta sweep for the plot
    beta_sweep = np.linspace(0.05, 1.0, 40)
    mvsu_beta_sweep_errs = np.zeros(len(beta_sweep))
    rk4_beta_sweep_errs = np.zeros(len(beta_sweep))

    for bi, bv in enumerate(beta_sweep):
        # MVSU + damp (single trial for sweep, seed=42)
        rng = np.random.RandomState(42)
        out_mvsu = run_mvsu_damped_ab4(
            state0, dt, n_steps, mu, true_states, best_wc, beta=bv,
            measurement_interval=measurement_interval,
            noise_sigma=noise_sigma, rng=rng, use_abm=use_abm_flag,
            sub_factor=sub_factor_flag)
        mvsu_beta_sweep_errs[bi] = np.mean(compute_pos_error(out_mvsu, true_states))

        # RK4 + damp (single trial for sweep, seed=42)
        rng = np.random.RandomState(42)
        out_rk4d = run_rk4_damped(
            state0, dt, n_steps, mu, true_states, beta=bv,
            measurement_interval=measurement_interval,
            noise_sigma=noise_sigma, rng=rng)
        rk4_beta_sweep_errs[bi] = np.mean(compute_pos_error(out_rk4d, true_states))

    best_mvsu_beta = beta_sweep[np.argmin(mvsu_beta_sweep_errs)]
    best_rk4_beta = beta_sweep[np.argmin(rk4_beta_sweep_errs)]

    print(f"  {'Condition':<35} {'Mean Err':>14} {'Std':>14}")
    print(f"  {'-'*65}")
    for bv in betas_test:
        print(f"  MVSU+Damp(beta={bv:.2f})               {mvsu_damp_results[bv]['mean']:>14.8e} {mvsu_damp_results[bv]['std']:>14.8e}")
    for bv in betas_test:
        print(f"  RK4+Damp(beta={bv:.2f})                {rk4_damp_results[bv]['mean']:>14.8e} {rk4_damp_results[bv]['std']:>14.8e}")
    print()
    print(f"  Beta sweep optimal (MVSU+Damp):  beta={best_mvsu_beta:.4f}")
    print(f"  Beta sweep optimal (RK4+Damp):   beta={best_rk4_beta:.4f}")
    print()

    # Does MVSU+Damp beat RK4+Damp at the same beta?
    print(f"  MVSU+Damp vs RK4+Damp comparison (same beta, noisy):")
    for bv in betas_test:
        ratio = rk4_damp_results[bv]['mean'] / mvsu_damp_results[bv]['mean']
        better = "MVSU wins" if ratio > 1 else "RK4 wins"
        print(f"    beta={bv:.2f}: MVSU={mvsu_damp_results[bv]['mean']:.6e}, "
              f"RK4={rk4_damp_results[bv]['mean']:.6e}, ratio={ratio:.4f}x ({better})")
    print()

    # =====================================================================
    # COMPREHENSIVE RESULTS TABLE
    # =====================================================================

    print("=" * 100)
    print("COMPREHENSIVE RESULTS TABLE")
    print("=" * 100)
    print()

    conditions = [
        ("1. RK4 only", rk4_states, rk4_err),
        (f"2. {best_name} only", chB_states, chB_err),
        ("3. Simple average", avg_states, avg_err),
        (f"4. MVSU optimal (w={best_wc:.4f})", mvsu_opt_states, mvsu_opt_err),
        ("5. Online-learned w_cross", online_states, online_err),
        (f"6. MVSU+Damp(beta=0.38,noisy)", mvsu_damp_results[0.38]['states'], mvsu_damp_results[0.38]['err']),
        (f"7. MVSU+Damp(beta=0.62,noisy)", mvsu_damp_results[0.62]['states'], mvsu_damp_results[0.62]['err']),
        (f"8. MVSU+Damp(beta=0.80,noisy)", mvsu_damp_results[0.80]['states'], mvsu_damp_results[0.80]['err']),
        (f"9. RK4+Damp(beta=0.62,noisy)", rk4_damp_results[0.62]['states'], rk4_damp_results[0.62]['err']),
    ]

    hdr = f"  {'#':<3} {'Condition':<35} {'Mean Err':>14} {'Final Err':>14} {'Max Err':>14} {'vs RK4':>10}"
    print(hdr)
    print(f"  {'-'*95}")

    for label, states, err in conditions:
        mean_e = np.mean(err)
        final_e = err[-1]
        max_e = np.max(err)
        ratio = rk4_mean / mean_e if mean_e > 0 else float('inf')
        print(f"  {label:<38} {mean_e:>14.8e} {final_e:>14.8e} {max_e:>14.8e} {ratio:>10.4f}x")

    print()

    # Ranking
    sorted_conds = sorted(conditions, key=lambda c: np.mean(c[2]))
    print("  Ranking by mean position error:")
    for rank, (label, _, err) in enumerate(sorted_conds):
        print(f"    {rank+1}. {label}: {np.mean(err):.8e}")
    print()

    # =====================================================================
    # KEY METRICS SUMMARY
    # =====================================================================

    print("=" * 100)
    print("KEY METRICS SUMMARY")
    print("=" * 100)
    print()

    print(f"  Error Correlation (RK4 vs {best_name}):")
    print(f"    Mean cosine similarity:     {corr['mean_cosine']:.6f}")
    print(f"    Magnitude Pearson corr:     {corr['magnitude_correlation']:.6f}")
    print()

    print(f"  Optimal w_cross:              {best_wc:.6f}")
    print(f"  Improvement factor over RK4:  {imp_rk4:.6f}x")
    print(f"  Improvement over {best_name:>5}:      {imp_chB:.6f}x")
    print(f"  Improvement over average:     {imp_avg:.6f}x")
    print()

    print(f"  Online-learned w_cross (final): {online_wc_hist[-1]:.6f}")
    print(f"  Online improvement over RK4:    {rk4_mean / np.mean(online_err):.6f}x")
    print()

    print(f"  Best beta (MVSU+Damp, noisy):   {best_mvsu_beta:.4f}")
    print(f"  Best beta (RK4+Damp, noisy):    {best_rk4_beta:.4f}")
    print()

    # =====================================================================
    # HONEST ASSESSMENT
    # =====================================================================

    print("=" * 100)
    print("HONEST ASSESSMENT")
    print("=" * 100)
    print()

    # 1. Cross-correction
    print("  1. CROSS-CORRECTION (the central MVSU claim):")
    if beats_both and imp_rk4 > 1.05:
        if imp_rk4 > 2.0:
            verdict = "STRONG SUCCESS"
        elif imp_rk4 > 1.2:
            verdict = "MODERATE SUCCESS"
        else:
            verdict = "WEAK SUCCESS"
        print(f"     VERDICT: {verdict}")
        print(f"     The optimal w_cross = {best_wc:.4f} yields {imp_rk4:.2f}x improvement over RK4.")
        print(f"     The disagreement between RK4 and {best_name} DOES contain extractable")
        print(f"     information about the true solution's location.")
    elif beats_avg:
        print(f"     VERDICT: PARTIAL")
        print(f"     w_cross helps vs naive average but doesn't beat the better individual integrator.")
    else:
        print(f"     VERDICT: FAILED")
        print(f"     No meaningful cross-correction benefit found.")
    print()

    # 2. Error correlation
    print("  2. ERROR CORRELATION:")
    print(f"     Mean cosine similarity: {corr['mean_cosine']:.4f}")
    if corr['mean_cosine'] > 0.9:
        print(f"     DIAGNOSIS: Too correlated. Errors point in the same direction.")
        print(f"     Cross-correction has minimal room to work.")
    elif corr['mean_cosine'] > 0.7:
        print(f"     DIAGNOSIS: Moderately correlated. Some orthogonal component exists.")
    elif corr['mean_cosine'] > 0.3:
        print(f"     DIAGNOSIS: Good diversity. Significant orthogonal error components.")
    else:
        print(f"     DIAGNOSIS: Nearly orthogonal. Ideal for cross-correction.")
    print()

    # 3. Is AB4 just too bad?
    print(f"  3. ACCURACY MATCHING:")
    ratio_chB_rk4 = chB_mean / rk4_mean
    if ratio_chB_rk4 > 10:
        print(f"     WARNING: {best_name} is {ratio_chB_rk4:.1f}x worse than RK4.")
        print(f"     This is the same problem as v1 Euler/Verlet. One channel is mostly noise.")
    elif ratio_chB_rk4 > 3:
        print(f"     CAUTION: {best_name} is {ratio_chB_rk4:.1f}x worse than RK4.")
        print(f"     Not ideal but the channels are at least in the same order of magnitude.")
    else:
        print(f"     GOOD: {best_name} is within {ratio_chB_rk4:.2f}x of RK4.")
        print(f"     Channels are well-matched in accuracy.")
    print()

    # 4. Damping
    print(f"  4. DAMPED MEASUREMENTS:")
    print(f"     Best beta (MVSU+Damp): {best_mvsu_beta:.4f}")
    print(f"     Best beta (RK4+Damp):  {best_rk4_beta:.4f}")
    if best_mvsu_beta < 0.95 or best_rk4_beta < 0.95:
        print(f"     CONFIRMED: Damping below 1.0 helps with noisy measurements.")
    else:
        print(f"     NOT CONFIRMED: Full snap (beta~1.0) appears optimal even with noise.")
    print()

    # 5. Overall
    print(f"  5. OVERALL HONEST SUMMARY:")
    print(f"     RK4 mean error:          {rk4_mean:.6e}")
    print(f"     {best_name:>5} mean error:        {chB_mean:.6e}")
    print(f"     Best MVSU mean error:    {best_wc_err:.6e}")
    print(f"     Cross-correction factor: {imp_rk4:.4f}x over RK4")
    print()

    # =====================================================================
    # PLOTS
    # =====================================================================

    print("Generating plots...")
    orbit_fracs = times / T

    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.30)
    fig.suptitle(f"MVSU Simulation v3: RK4 vs {best_name}, Kepler Orbit (e={e}, {n_orbits} orbits)",
                 fontsize=14, y=0.98)

    # ---- Plot 1: Error over time for main conditions ----
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.semilogy(orbit_fracs, rk4_err + 1e-20, 'r-', lw=1.2, label='RK4', alpha=0.8)
    ax1.semilogy(orbit_fracs, chB_err + 1e-20, 'b-', lw=1.2, label=best_name, alpha=0.8)
    ax1.semilogy(orbit_fracs, avg_err + 1e-20, 'c--', lw=1.0, label='Average', alpha=0.7)
    ax1.semilogy(orbit_fracs, mvsu_opt_err + 1e-20, 'g-', lw=1.5,
                 label=f'MVSU (w={best_wc:.3f})', alpha=0.9)
    ax1.semilogy(orbit_fracs, online_err + 1e-20, 'm--', lw=1.0,
                 label='Online w_cross', alpha=0.7)
    ax1.set_xlabel('Orbits')
    ax1.set_ylabel('Position Error')
    ax1.set_title('Position Error vs Time (Main Conditions)')
    ax1.legend(fontsize=7, loc='upper left')
    ax1.grid(True, alpha=0.3)

    # ---- Plot 2: w_cross sweep ----
    ax2 = fig.add_subplot(gs[0, 1])
    for name, (wv, we, bw, be) in all_pair_results.items():
        ls = '-' if name == best_name else '--'
        alpha = 1.0 if name == best_name else 0.6
        ax2.plot(wv, we, ls=ls, lw=1.2, label=f'RK4 vs {name}', alpha=alpha)

    ax2.axvline(x=0, color='red', ls=':', alpha=0.5, label='w=0 (pure RK4)')
    ax2.axvline(x=-1, color='blue', ls=':', alpha=0.5, label=f'w=-1 (pure {best_name})')
    ax2.axvline(x=-0.5, color='cyan', ls=':', alpha=0.5, label='w=-0.5 (average)')
    ax2.scatter([best_wc], [best_wc_err], color='green', s=100, zorder=5,
                label=f'Optimal w={best_wc:.3f}')
    ax2.set_xlabel('w_cross')
    ax2.set_ylabel('Mean Position Error')
    ax2.set_title('w_cross Sweep: Error vs Cross-Correction Weight')
    ax2.legend(fontsize=6, loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')

    # ---- Plot 3: Error correlation over time ----
    ax3 = fig.add_subplot(gs[1, 0])
    # Smooth the per-step cosine similarity
    cos_per_step = corr['cosine_per_step']
    window = steps_per_orbit // 2
    if len(cos_per_step) > window:
        cos_smooth = np.convolve(cos_per_step, np.ones(window)/window, mode='valid')
        orbit_smooth = orbit_fracs[:len(cos_smooth)]
    else:
        cos_smooth = cos_per_step
        orbit_smooth = orbit_fracs

    ax3.plot(orbit_fracs[1:], cos_per_step[1:], 'b-', alpha=0.15, lw=0.5, label='Per-step')
    ax3.plot(orbit_smooth, cos_smooth, 'r-', lw=1.5, label=f'Smoothed ({window}-step)')
    ax3.axhline(y=corr['mean_cosine'], color='green', ls='--', lw=1.0,
                label=f'Mean = {corr["mean_cosine"]:.3f}')
    ax3.axhline(y=0.9, color='gray', ls=':', alpha=0.5, label='High corr (0.9)')
    ax3.axhline(y=0.3, color='gray', ls=':', alpha=0.5, label='Low corr (0.3)')
    ax3.set_xlabel('Orbits')
    ax3.set_ylabel('Cosine Similarity of Error Vectors')
    ax3.set_title(f'Error Correlation: RK4 vs {best_name}')
    ax3.legend(fontsize=7)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(-1.1, 1.1)

    # ---- Plot 4: Beta sweep with noisy measurements ----
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(beta_sweep, mvsu_beta_sweep_errs, 'g-o', lw=1.5, ms=3,
             label='MVSU+Damp (noisy)')
    ax4.plot(beta_sweep, rk4_beta_sweep_errs, 'r-s', lw=1.5, ms=3,
             label='RK4+Damp (noisy)')
    ax4.axvline(x=0.38, color='blue', ls='--', alpha=0.4, label='beta=0.38')
    ax4.axvline(x=0.62, color='orange', ls='--', alpha=0.4, label='beta=0.62')
    ax4.axvline(x=best_mvsu_beta, color='green', ls=':', alpha=0.6,
                label=f'MVSU best={best_mvsu_beta:.2f}')
    ax4.axvline(x=best_rk4_beta, color='red', ls=':', alpha=0.6,
                label=f'RK4 best={best_rk4_beta:.2f}')
    ax4.set_xlabel('Beta (damping rate)')
    ax4.set_ylabel('Mean Position Error')
    ax4.set_title(f'Beta Sweep: MVSU+Damp vs RK4+Damp (noise sigma={noise_sigma})')
    ax4.legend(fontsize=6)
    ax4.grid(True, alpha=0.3)
    ax4.set_yscale('log')

    # ---- Plot 5: Trajectories ----
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.plot(true_states[:, 0], true_states[:, 1], 'k-', lw=2, label='True', alpha=0.8)
    ax5.plot(rk4_states[:, 0], rk4_states[:, 1], 'r-', lw=0.6, label='RK4', alpha=0.4)
    ax5.plot(chB_states[:, 0], chB_states[:, 1], 'b-', lw=0.6, label=best_name, alpha=0.4)
    ax5.plot(mvsu_opt_states[:, 0], mvsu_opt_states[:, 1], 'g-', lw=1.0,
             label=f'MVSU (w={best_wc:.3f})', alpha=0.6)
    ax5.set_xlabel('x')
    ax5.set_ylabel('y')
    ax5.set_title('Orbital Trajectories')
    ax5.legend(fontsize=8)
    ax5.set_aspect('equal')
    ax5.grid(True, alpha=0.3)

    # ---- Plot 6: Online w_cross evolution ----
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.plot(orbit_fracs, online_wc_hist, 'purple', lw=1.0, label='Online w_cross')
    ax6.axhline(y=best_wc, color='green', ls='--', lw=1.5,
                label=f'Sweep optimal ({best_wc:.4f})')
    ax6.axhline(y=0, color='gray', ls=':', alpha=0.5, label='w=0 (pure RK4)')
    ax6.set_xlabel('Orbits')
    ax6.set_ylabel('w_cross value')
    ax6.set_title('Online-Learned w_cross Over Time')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)

    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "mvsu_simulation_v3_results.png")
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    print(f"  Plot saved to: {outpath}")
    plt.close()

    return {
        'best_wc': best_wc,
        'imp_rk4': imp_rk4,
        'imp_chB': imp_chB,
        'imp_avg': imp_avg,
        'correlation': corr,
        'best_name': best_name,
    }


if __name__ == "__main__":
    print("=" * 100)
    print("MVSU SIMULATION TEST v3: RK4 vs Adams-Bashforth 4 (Thorough)")
    print("Structural error diversity: single-step (RK4) vs multi-step (AB4/ABM4)")
    print("=" * 100)
    print()

    t_start = time.time()
    results = run_simulation(n_orbits=20, steps_per_orbit=200, e=0.3)
    elapsed = time.time() - t_start

    print()
    print("=" * 100)
    print(f"SIMULATION COMPLETE ({elapsed:.1f}s)")
    print("=" * 100)
