"""
Sarah's Blind Spot Experiment: Non-Stationary Alpha (Drifting Contamination)
============================================================================
Every prior experiment uses FIXED alpha. But in real ML systems, alpha drifts:
- RLHF: synthetic fraction grows as more model outputs enter RM training pool
- Synthetic data: AI content in web crawls increases over time
- Recommendations: feedback loop tightens as user behavior adapts

Question 1: Does the system TRACK the moving fixed point w*(alpha)?
Question 2: Is there a CRITICAL DRIFT RATE above which tracking fails?
Question 3: Does MVSU handle drift better than monocular?
Question 4: Does w_cross flip sign during drift (topology change)?

Design:
  - Alpha starts at 0.1 (mostly clean), linearly increases to 1.0 (fully self-referential)
  - Drift rates: slow (over 50K steps), medium (10K), fast (2K), instant (step function)
  - Compare: monocular SGD vs. MVSU (arch-diverse dual channel)
  - Measure: tracking error = |w_converged - w*(alpha_current)|
  - Also test: alpha that oscillates (seasonal contamination patterns)

This is the scenario every ML practitioner faces. Nobody runs at fixed alpha.

Author: Sarah Chen (the blind spot probe)
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

np.random.seed(42)

# ============================================================
# Core self-referential agent (from network_selfref.py lineage)
# ============================================================

def w_star(alpha):
    """Theoretical optimal weight for contamination level alpha."""
    if alpha < 1e-10:
        return 1.0
    # From kw^2 + w - 1 = 0 with k = alpha^2 (effective self-contamination)
    # For the simple echo model: w^2 + w - 1 = 0 at alpha=1 -> w = 1/phi
    # At general alpha: observation = s + alpha * w * y_prev
    # Var(y) = 1 + alpha^2 * w^2 * Var(y) -> Var(y) = 1/(1 - alpha^2 * w^2)
    # Optimal: w = 1 / (1 + alpha^2 * Var(y)) ... but let's just solve
    # the self-consistency: w = 1/(1 + alpha^2/(1 - alpha^2*w^2))
    # -> w(1 + alpha^2/(1-alpha^2*w^2)) = 1
    # -> w + alpha^2*w/(1-alpha^2*w^2) = 1
    # -> w(1-alpha^2*w^2) + alpha^2*w = 1-alpha^2*w^2
    # -> w - alpha^2*w^3 + alpha^2*w = 1 - alpha^2*w^2
    # This is messy. Use the standard form: for the isolated echo agent,
    # the self-consistency at alpha gives: alpha^2*w^2 + w - 1 = 0
    # -> w = (-1 + sqrt(1 + 4*alpha^2)) / (2*alpha^2)
    disc = 1 + 4 * alpha**2
    return (-1 + np.sqrt(disc)) / (2 * alpha**2)


def run_drifting_alpha_monocular(alpha_schedule, n_steps, lr=0.01, lr_decay=0.99999):
    """Single agent tracking a drifting alpha."""
    w = 0.5  # Initial weight
    h_prev = 0.0

    w_history = []
    alpha_history = []
    tracking_errors = []

    for t in range(n_steps):
        alpha = alpha_schedule(t, n_steps)

        # Generate signal and contaminated observation
        s = np.random.randn()
        y = s + alpha * w * h_prev

        # Agent output
        h = w * y

        # SGD update: minimize (h - s)^2
        # d/dw (w*y - s)^2 = 2*(w*y - s)*y
        error = h - s
        grad = 2 * error * y

        current_lr = lr * (lr_decay ** t)
        w -= current_lr * grad
        w = np.clip(w, -2.0, 2.0)

        h_prev = h

        # Record
        if t % 100 == 0:
            w_theory = w_star(max(alpha, 0.01))
            w_history.append(w)
            alpha_history.append(alpha)
            tracking_errors.append(abs(w - w_theory))

    return np.array(w_history), np.array(alpha_history), np.array(tracking_errors)


def run_drifting_alpha_mvsu(alpha_schedule, n_steps, lr=0.01, lr_decay=0.99999):
    """MVSU (2 channels, architecture-diverse) tracking drifting alpha."""
    # Channel A: linear (w_a)
    # Channel B: nonlinear (w_b with tanh)
    w_a = 0.5
    w_b = 0.5
    w_cross = 0.0  # Learned cross-connection
    h_a_prev = 0.0
    h_b_prev = 0.0

    w_cross_history = []
    w_history = []  # Effective combined weight
    alpha_history = []
    tracking_errors = []

    for t in range(n_steps):
        alpha = alpha_schedule(t, n_steps)

        s = np.random.randn()

        # Both channels see the same contaminated signal
        # but with different observation noise
        noise_a = 0.1 * np.random.randn()
        noise_b = 0.1 * np.random.randn()

        y_a = s + alpha * w_a * h_a_prev + noise_a
        y_b = s + alpha * w_b * h_b_prev + noise_b

        # Channel A: linear + cross-inhibition
        h_a = w_a * y_a + w_cross * h_b_prev
        # Channel B: tanh + cross-inhibition (different architecture)
        h_b = np.tanh(w_b * y_b) + w_cross * h_a_prev

        # Combined prediction
        pred = 0.5 * (h_a + h_b)

        # SGD updates
        error_a = h_a - s
        error_b = h_b - s

        grad_wa = 2 * error_a * y_a
        grad_wb = 2 * error_b * y_b * (1 - np.tanh(w_b * y_b)**2)  # tanh derivative
        grad_wcross = 2 * (error_a * h_b_prev + error_b * h_a_prev)

        current_lr = lr * (lr_decay ** t)
        w_a -= current_lr * grad_wa
        w_b -= current_lr * grad_wb
        w_cross -= current_lr * 0.5 * grad_wcross  # Slower cross learning

        w_a = np.clip(w_a, -2.0, 2.0)
        w_b = np.clip(w_b, -2.0, 2.0)
        w_cross = np.clip(w_cross, -2.0, 2.0)

        h_a_prev = h_a
        h_b_prev = h_b

        if t % 100 == 0:
            w_eff = 0.5 * (w_a + np.tanh(w_b))  # Approximate effective weight
            w_theory = w_star(max(alpha, 0.01))
            w_history.append(w_eff)
            alpha_history.append(alpha)
            tracking_errors.append(abs(w_eff - w_theory))
            w_cross_history.append(w_cross)

    return (np.array(w_history), np.array(alpha_history),
            np.array(tracking_errors), np.array(w_cross_history))


# ============================================================
# Alpha schedules (the drift patterns)
# ============================================================

def make_linear_drift(rate_name):
    """Alpha drifts from 0.1 to 1.0 over the full run."""
    def schedule(t, n_total):
        frac = t / n_total
        if rate_name == "slow":
            return 0.1 + 0.9 * frac
        elif rate_name == "medium":
            return 0.1 + 0.9 * min(1.0, frac * 5)  # Reaches 1.0 at 20% of run
        elif rate_name == "fast":
            return 0.1 + 0.9 * min(1.0, frac * 25)  # Reaches 1.0 at 4% of run
        elif rate_name == "instant":
            return 1.0 if t > 100 else 0.1
    return schedule

def make_oscillating():
    """Alpha oscillates between 0.2 and 0.9 (seasonal contamination)."""
    def schedule(t, n_total):
        return 0.55 + 0.35 * np.sin(2 * np.pi * t / (n_total / 5))
    return schedule

def make_sudden_reversal():
    """Alpha goes 0.1 -> 1.0 -> 0.1 (contamination then cleanup)."""
    def schedule(t, n_total):
        frac = t / n_total
        if frac < 0.33:
            return 0.1 + 0.9 * (frac / 0.33)
        elif frac < 0.66:
            return 1.0
        else:
            return 1.0 - 0.9 * ((frac - 0.66) / 0.34)
    return schedule


# ============================================================
# Run the experiment
# ============================================================

print("=" * 70)
print("SARAH'S BLIND SPOT: Non-Stationary Alpha (Drifting Contamination)")
print("=" * 70)
print()

N_STEPS = 50000
N_SEEDS = 5

# ---- Experiment 1: Linear drift at different rates ----
print("EXPERIMENT 1: Linear drift (alpha 0.1 -> 1.0) at different rates")
print("-" * 60)

drift_rates = ["slow", "medium", "fast", "instant"]
results_mono = {}
results_mvsu = {}

for rate in drift_rates:
    mono_errors_all = []
    mvsu_errors_all = []
    mvsu_wcross_all = []

    for seed in range(N_SEEDS):
        np.random.seed(seed * 100 + 7)
        schedule = make_linear_drift(rate)

        w_m, a_m, err_m = run_drifting_alpha_monocular(schedule, N_STEPS)
        mono_errors_all.append(err_m)

        np.random.seed(seed * 100 + 7)
        w_v, a_v, err_v, wc_v = run_drifting_alpha_mvsu(schedule, N_STEPS)
        mvsu_errors_all.append(err_v)
        mvsu_wcross_all.append(wc_v)

    mono_mean = np.mean(mono_errors_all, axis=0)
    mvsu_mean = np.mean(mvsu_errors_all, axis=0)
    wcross_mean = np.mean(mvsu_wcross_all, axis=0)

    results_mono[rate] = mono_mean
    results_mvsu[rate] = (mvsu_mean, wcross_mean)

    # Report: mean tracking error over full run
    mono_total = np.mean(mono_mean)
    mvsu_total = np.mean(mvsu_mean)
    improvement = (mono_total - mvsu_total) / mono_total * 100

    # Tracking error in last 20% (after alpha is high)
    n_pts = len(mono_mean)
    last_20 = slice(int(0.8 * n_pts), n_pts)
    mono_late = np.mean(mono_mean[last_20])
    mvsu_late = np.mean(mvsu_mean[last_20])

    # w_cross in first vs last quarter
    wcross_early = np.mean(wcross_mean[:n_pts//4])
    wcross_late = np.mean(wcross_mean[3*n_pts//4:])

    print(f"  {rate:>8s}: Mono tracking err = {mono_total:.4f}, "
          f"MVSU = {mvsu_total:.4f}, improvement = {improvement:+.1f}%")
    print(f"           Late-run (last 20%): Mono = {mono_late:.4f}, MVSU = {mvsu_late:.4f}")
    print(f"           w_cross: early = {wcross_early:+.3f}, late = {wcross_late:+.3f}")

print()

# ---- Experiment 2: Oscillating alpha ----
print("EXPERIMENT 2: Oscillating alpha (seasonal contamination)")
print("-" * 60)

osc_mono_errors = []
osc_mvsu_errors = []
osc_wcross = []

for seed in range(N_SEEDS):
    np.random.seed(seed * 200 + 13)
    schedule = make_oscillating()

    w_m, a_m, err_m = run_drifting_alpha_monocular(schedule, N_STEPS)
    osc_mono_errors.append(err_m)

    np.random.seed(seed * 200 + 13)
    w_v, a_v, err_v, wc_v = run_drifting_alpha_mvsu(schedule, N_STEPS)
    osc_mvsu_errors.append(err_v)
    osc_wcross.append(wc_v)

osc_mono_mean = np.mean(osc_mono_errors, axis=0)
osc_mvsu_mean = np.mean(osc_mvsu_errors, axis=0)
osc_wcross_mean = np.mean(osc_wcross, axis=0)

mono_total = np.mean(osc_mono_mean)
mvsu_total = np.mean(osc_mvsu_mean)
improvement = (mono_total - mvsu_total) / mono_total * 100

# Check if w_cross oscillates with alpha
n_pts = len(osc_wcross_mean)
# Split into 5 oscillation periods
period_len = n_pts // 5
wcross_by_period = []
for p in range(5):
    start = p * period_len
    end = (p + 1) * period_len
    wcross_by_period.append(np.mean(osc_wcross_mean[start:end]))

print(f"  Mean tracking error: Mono = {mono_total:.4f}, MVSU = {mvsu_total:.4f}, "
      f"improvement = {improvement:+.1f}%")
print(f"  w_cross by oscillation period: {[f'{x:+.3f}' for x in wcross_by_period]}")

# Check correlation between alpha and w_cross
alpha_at_samples = np.array([make_oscillating()(t * 100, N_STEPS) for t in range(n_pts)])
corr = np.corrcoef(alpha_at_samples[:len(osc_wcross_mean)], osc_wcross_mean)[0, 1]
print(f"  Correlation(alpha, w_cross) = {corr:+.3f}")

print()

# ---- Experiment 3: Sudden reversal (contamination then cleanup) ----
print("EXPERIMENT 3: Sudden reversal (alpha: 0.1 -> 1.0 -> 0.1)")
print("-" * 60)

rev_mono_errors = []
rev_mvsu_errors = []
rev_w_mono = []
rev_w_mvsu = []
rev_wcross = []

for seed in range(N_SEEDS):
    np.random.seed(seed * 300 + 17)
    schedule = make_sudden_reversal()

    w_m, a_m, err_m = run_drifting_alpha_monocular(schedule, N_STEPS)
    rev_mono_errors.append(err_m)
    rev_w_mono.append(w_m)

    np.random.seed(seed * 300 + 17)
    w_v, a_v, err_v, wc_v = run_drifting_alpha_mvsu(schedule, N_STEPS)
    rev_mvsu_errors.append(err_v)
    rev_w_mvsu.append(w_v)
    rev_wcross.append(wc_v)

rev_mono_mean = np.mean(rev_mono_errors, axis=0)
rev_mvsu_mean = np.mean(rev_mvsu_errors, axis=0)
rev_wcross_mean = np.mean(rev_wcross, axis=0)
rev_w_mono_mean = np.mean(rev_w_mono, axis=0)
rev_w_mvsu_mean = np.mean(rev_w_mvsu, axis=0)

# Split into three phases
n_pts = len(rev_mono_mean)
phase1 = slice(0, n_pts // 3)           # Rising alpha
phase2 = slice(n_pts // 3, 2 * n_pts // 3)  # Plateau at alpha=1
phase3 = slice(2 * n_pts // 3, n_pts)   # Falling alpha

mono_p1 = np.mean(rev_mono_mean[phase1])
mono_p2 = np.mean(rev_mono_mean[phase2])
mono_p3 = np.mean(rev_mono_mean[phase3])
mvsu_p1 = np.mean(rev_mvsu_mean[phase1])
mvsu_p2 = np.mean(rev_mvsu_mean[phase2])
mvsu_p3 = np.mean(rev_mvsu_mean[phase3])

# KEY TEST: Does w recover after alpha drops back down?
w_mono_early = np.mean(rev_w_mono_mean[:n_pts//10])   # w at start (alpha ~0.1)
w_mono_end = np.mean(rev_w_mono_mean[9*n_pts//10:])    # w at end (alpha ~0.1 again)
w_mvsu_early = np.mean(rev_w_mvsu_mean[:n_pts//10])
w_mvsu_end = np.mean(rev_w_mvsu_mean[9*n_pts//10:])

w_theory_low = w_star(0.1)
w_theory_high = w_star(1.0)

print(f"  Phase 1 (rising): Mono err = {mono_p1:.4f}, MVSU err = {mvsu_p1:.4f}")
print(f"  Phase 2 (plateau): Mono err = {mono_p2:.4f}, MVSU err = {mvsu_p2:.4f}")
print(f"  Phase 3 (falling): Mono err = {mono_p3:.4f}, MVSU err = {mvsu_p3:.4f}")
print()
print(f"  RECOVERY TEST (w after alpha returns to 0.1):")
print(f"    w*(alpha=0.1) = {w_theory_low:.4f}, w*(alpha=1.0) = {w_theory_high:.4f}")
print(f"    Mono:  w_start = {w_mono_early:.4f}, w_end = {w_mono_end:.4f}, "
      f"recovery gap = {abs(w_mono_end - w_theory_low):.4f}")
print(f"    MVSU:  w_start = {w_mvsu_early:.4f}, w_end = {w_mvsu_end:.4f}, "
      f"recovery gap = {abs(w_mvsu_end - w_theory_low):.4f}")
print(f"    w_cross: Phase1 = {np.mean(rev_wcross_mean[phase1]):+.3f}, "
      f"Phase2 = {np.mean(rev_wcross_mean[phase2]):+.3f}, "
      f"Phase3 = {np.mean(rev_wcross_mean[phase3]):+.3f}")

print()

# ---- Experiment 4: Hysteresis test ----
print("EXPERIMENT 4: Hysteresis (does drift direction matter?)")
print("-" * 60)

def make_up_drift(t, n_total):
    return 0.1 + 0.9 * (t / n_total)

def make_down_drift(t, n_total):
    return 1.0 - 0.9 * (t / n_total)

hyst_up_errors = []
hyst_down_errors = []
hyst_up_w = []
hyst_down_w = []

for seed in range(N_SEEDS):
    np.random.seed(seed * 400 + 23)
    w_up, a_up, err_up = run_drifting_alpha_monocular(make_up_drift, N_STEPS)
    hyst_up_errors.append(err_up)
    hyst_up_w.append(w_up)

    np.random.seed(seed * 400 + 23)
    w_down, a_down, err_down = run_drifting_alpha_monocular(make_down_drift, N_STEPS)
    hyst_down_errors.append(err_down)
    hyst_down_w.append(w_down)

hyst_up_mean = np.mean(hyst_up_errors, axis=0)
hyst_down_mean = np.mean(hyst_down_errors, axis=0)

# At the midpoint (alpha ~ 0.55), compare the two directions
midpoint = len(hyst_up_mean) // 2
window = len(hyst_up_mean) // 10
mid_slice = slice(midpoint - window, midpoint + window)

up_at_mid = np.mean(hyst_up_mean[mid_slice])
down_at_mid = np.mean(hyst_down_mean[mid_slice])

# Effective w at midpoint
up_w_mid = np.mean(np.mean(hyst_up_w, axis=0)[mid_slice])
down_w_mid = np.mean(np.mean(hyst_down_w, axis=0)[mid_slice])
w_theory_mid = w_star(0.55)

print(f"  At alpha ~ 0.55 (midpoint):")
print(f"    Rising alpha:  w = {up_w_mid:.4f}, tracking error = {up_at_mid:.4f}")
print(f"    Falling alpha: w = {down_w_mid:.4f}, tracking error = {down_at_mid:.4f}")
print(f"    w*(0.55) = {w_theory_mid:.4f}")
print(f"    Hysteresis gap = {abs(up_w_mid - down_w_mid):.4f} "
      f"({'SIGNIFICANT' if abs(up_w_mid - down_w_mid) > 0.03 else 'negligible'})")

# Overall comparison
up_total = np.mean(hyst_up_mean)
down_total = np.mean(hyst_down_mean)
print(f"  Overall tracking error: Rising = {up_total:.4f}, Falling = {down_total:.4f}")
asym = (up_total - down_total) / max(up_total, down_total) * 100
print(f"  Asymmetry = {asym:+.1f}% ({'rising is harder' if asym > 0 else 'falling is harder'})")

print()

# ---- Experiment 5: Critical drift rate ----
print("EXPERIMENT 5: Critical drift rate (when does tracking fail?)")
print("-" * 60)

# Define tracking failure as mean error > 0.1
drift_durations = [500, 1000, 2000, 5000, 10000, 20000, 50000]
failure_results = []

for dur in drift_durations:
    def make_schedule(t, n_total, _dur=dur):
        # Alpha goes from 0.1 to 1.0 over _dur steps, then stays at 1.0
        if t < _dur:
            return 0.1 + 0.9 * (t / _dur)
        return 1.0

    dur_errors = []
    for seed in range(N_SEEDS):
        np.random.seed(seed * 500 + 31)
        _, _, err = run_drifting_alpha_monocular(make_schedule, N_STEPS)
        dur_errors.append(err)

    mean_err = np.mean(dur_errors, axis=0)
    # Mean tracking error during the drift phase
    drift_pts = min(dur // 100, len(mean_err))
    drift_err = np.mean(mean_err[:max(1, drift_pts)])
    # Mean tracking error during the settled phase (last 20%)
    settled_err = np.mean(mean_err[int(0.8*len(mean_err)):])

    failure_results.append((dur, drift_err, settled_err))

    status = "FAILED" if drift_err > 0.10 else "OK"
    print(f"  Drift over {dur:>6d} steps: drift-phase error = {drift_err:.4f}, "
          f"settled error = {settled_err:.4f} [{status}]")

print()

# ---- Summary ----
print("=" * 70)
print("SUMMARY OF KEY FINDINGS")
print("=" * 70)
print()

# Compute overall MVSU advantage
for rate in drift_rates:
    mono_mean = np.mean(results_mono[rate])
    mvsu_mean, wcross_mean = results_mvsu[rate]
    mvsu_total = np.mean(mvsu_mean)
    improvement = (mono_mean - mvsu_total) / mono_mean * 100

    # Get w_cross trend
    n_pts = len(wcross_mean)
    wc_start = np.mean(wcross_mean[:n_pts//4])
    wc_end = np.mean(wcross_mean[3*n_pts//4:])

    print(f"  {rate:>8s} drift: MVSU advantage = {improvement:+.1f}%, "
          f"w_cross drift: {wc_start:+.3f} -> {wc_end:+.3f}")

# Hysteresis verdict
print(f"\n  Hysteresis: {abs(up_w_mid - down_w_mid):.4f} gap at alpha=0.55")
if abs(up_w_mid - down_w_mid) > 0.03:
    print("  >>> HYSTERESIS DETECTED: drift direction matters!")
    print("  >>> The system carries 'memory' of past contamination levels")
else:
    print("  >>> No significant hysteresis: system tracks well regardless of direction")

# Recovery verdict
recovery_gap_mono = abs(w_mono_end - w_theory_low)
recovery_gap_mvsu = abs(w_mvsu_end - w_theory_low)
print(f"\n  Recovery from contamination:")
print(f"    Mono recovery gap: {recovery_gap_mono:.4f}")
print(f"    MVSU recovery gap: {recovery_gap_mvsu:.4f}")
if recovery_gap_mono > 0.05:
    print("  >>> RECOVERY FAILURE: Monocular does NOT fully recover from high alpha")
else:
    print("  >>> Monocular recovers adequately")

# w_cross dynamics
print(f"\n  w_cross dynamics during oscillation:")
print(f"    Correlation with alpha: {corr:+.3f}")
if abs(corr) > 0.3:
    print("  >>> w_cross TRACKS alpha: cross-weight adapts to contamination level")
else:
    print("  >>> w_cross is STATIC: cross-weight does not respond to alpha changes")

# Critical drift rate
print(f"\n  Critical drift rate:")
for dur, d_err, s_err in failure_results:
    if d_err > 0.10:
        rate_per_step = 0.9 / dur
        print(f"  >>> Tracking breaks at drift rate {rate_per_step:.5f}/step "
              f"(alpha traverses 0.1->1.0 in {dur} steps)")
        break
else:
    print("  >>> No tracking failure detected at any tested rate")

print()
print("Experiment complete.")
