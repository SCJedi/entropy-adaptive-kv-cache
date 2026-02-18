"""
MVSU Real-World Demo: Self-Referential Decontamination on Continuous Feedback Tasks
======================================================================================
Demonstrates the Minimum Viable Stable Unit on three tasks where predictions
contaminate observations — the core self-referential problem.

Task 1: Thermostat Control
  - True temp follows sinusoidal daily cycle + noise
  - Heater responds to model predictions: predicting "cold" warms the room
  - observation(t) = true_temp(t) + alpha * heater_response(prediction(t-1))

Task 2: Sensor Calibration with Drift
  - True signal is slowly drifting (random walk + smooth trend)
  - Sensor auto-calibrates based on model's recent predictions
  - observation(t) = true_signal(t) + calibration_offset(t)

Task 3: Market Microstructure
  - True value follows Ornstein-Uhlenbeck mean-reverting process
  - Model's prediction moves the observed price (market impact)
  - price(t) = true_value(t) + gamma * (prediction(t-1) - true_value(t))

Methods compared:
  1. Monocular — single predictor, standard SGD
  2. MVSU (same init) — dual channel, same architecture, different random init
  3. MVSU (arch split) — dual channel, linear + MLP
  4. Oracle — system-aware predictor that knows contamination strength

Author: Claude (Ouroboros framework, Experiment 16)
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

# Add parent directory to path for mvsu import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from mvsu import MVSUPredictor, LinearPredictor, MLPPredictor

# ==========================================================================
# Constants
# ==========================================================================
N_TIMESTEPS = 2000
WARMUP = 400
LR = 0.01
GRAD_CLIP = 5.0
N_SEEDS = 10
SEEDS = list(range(42, 42 + N_SEEDS))
CONTAMINATION_STRENGTHS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# Feature construction: use a window of recent observations
WINDOW = 5  # features = [obs(t), obs(t-1), ..., obs(t-WINDOW+1)]
D_IN = WINDOW
D_OUT = 1


# ==========================================================================
# Feature construction
# ==========================================================================
def make_features(obs_history, t):
    """Construct feature vector from observation history at time t."""
    features = np.zeros(WINDOW)
    for i in range(WINDOW):
        idx = t - i
        if idx >= 0:
            features[i] = obs_history[idx]
    return features


# ==========================================================================
# Oracle predictor (knows the contamination structure)
# ==========================================================================
class OraclePredictor:
    """System-aware predictor that knows the contamination strength.

    Uses the optimal weight from w = (1 - alpha^2 * w^2)^2 and
    applies decontamination correction to its prediction.
    """

    def __init__(self, d_in, d_out, alpha, seed=None):
        self.alpha = alpha
        self.base = LinearPredictor(d_in, d_out, seed=seed)
        # Compute system-aware optimal downweighting
        self.w_sys = self._compute_w_sys(alpha)
        self._last_x = None
        self.d_in = d_in
        self.d_out = d_out

    def _compute_w_sys(self, alpha, n_iter=200):
        """w_sys = (1 - alpha^2 * w^2)^2 fixed point."""
        if alpha < 1e-12:
            return 1.0
        w = 0.618  # start at myopic
        for _ in range(n_iter):
            a2w2 = alpha ** 2 * w ** 2
            if a2w2 >= 1.0:
                w *= 0.9
                continue
            w_new = (1.0 - a2w2) ** 2
            if abs(w_new - w) < 1e-12:
                break
            w = 0.5 * w + 0.5 * w_new
        return w

    def predict(self, x):
        x = np.asarray(x, dtype=float).ravel()
        self._last_x = x
        raw = self.base.predict(x)
        # Apply system-aware correction: scale down to account for contamination
        return raw * self.w_sys

    def update(self, grad_output, lr=0.01, grad_clip=5.0):
        # Scale gradient through w_sys
        self.base.update(grad_output * self.w_sys, lr=lr, grad_clip=grad_clip)

    def copy(self, seed=None):
        new = OraclePredictor(self.d_in, self.d_out, self.alpha, seed=seed)
        return new


# ==========================================================================
# Task generators
# ==========================================================================
def generate_thermostat(n_steps, alpha, predictions, rng):
    """Thermostat control with heater feedback.

    True temperature: sinusoidal daily cycle + noise
    Heater: responds to prediction — if model predicts cold, heater warms up
    observation(t) = true_temp(t) + alpha * heater_response(t)
    heater_response(t) = gain * max(0, target - prediction(t-1))

    Returns: (observations, true_temps)
    """
    t = np.arange(n_steps)
    # True temperature: sinusoidal + slow drift + noise
    true_temp = (20.0 + 5.0 * np.sin(2 * np.pi * t / 200.0)
                 + 2.0 * np.sin(2 * np.pi * t / 47.0 + 0.5)
                 + rng.randn(n_steps) * 0.5)

    target_temp = 22.0  # thermostat target
    heater_gain = 3.0   # heater strength

    observations = np.zeros(n_steps)
    for i in range(n_steps):
        # Heater response: if model predicted cold, heat up
        if i > 0 and predictions[i - 1] is not None:
            pred = predictions[i - 1]
            # Heater tries to push toward target based on prediction
            heater = heater_gain * np.clip(target_temp - pred, 0, 5.0)
        else:
            heater = 0.0
        observations[i] = true_temp[i] + alpha * heater

    return observations, true_temp


def generate_sensor(n_steps, alpha, predictions, rng):
    """Sensor calibration with drift feedback.

    True signal: random walk + smooth trend
    Calibration offset: drifts based on prediction-observation mismatch
    observation(t) = true_signal(t) + calibration_offset(t)
    calibration_offset(t) += beta * (prediction(t-1) - observation(t-1))

    Returns: (observations, true_signals)
    """
    # True signal: smooth drift + random walk
    true_signal = np.zeros(n_steps)
    true_signal[0] = rng.randn() * 0.5
    for i in range(1, n_steps):
        true_signal[i] = true_signal[i - 1] + 0.02 * np.sin(2 * np.pi * i / 300.0) + rng.randn() * 0.1

    # Calibration drift
    cal_offset = 0.0
    observations = np.zeros(n_steps)
    for i in range(n_steps):
        observations[i] = true_signal[i] + cal_offset
        if i > 0 and predictions[i - 1] is not None:
            # Auto-calibration feedback: sensor adjusts based on prediction error
            cal_offset += alpha * 0.05 * (predictions[i - 1] - observations[i - 1])

    return observations, true_signal


def generate_market(n_steps, alpha, predictions, rng):
    """Market microstructure with price impact.

    True value: Ornstein-Uhlenbeck mean-reverting process
    Price impact: prediction moves the observed price toward itself
    price(t) = true_value(t) + gamma * (prediction(t-1) - true_value(t))

    Returns: (observations, true_values)
    """
    # OU process: dV = theta * (mu - V) * dt + sigma * dW
    theta = 0.1    # mean reversion speed
    mu = 100.0     # long-run mean
    sigma = 1.0    # volatility

    true_value = np.zeros(n_steps)
    true_value[0] = mu + rng.randn() * 2.0
    for i in range(1, n_steps):
        true_value[i] = (true_value[i - 1]
                         + theta * (mu - true_value[i - 1])
                         + sigma * rng.randn())

    observations = np.zeros(n_steps)
    for i in range(n_steps):
        if i > 0 and predictions[i - 1] is not None:
            # Market impact: price gets pulled toward prediction
            impact = alpha * (predictions[i - 1] - true_value[i])
        else:
            impact = 0.0
        observations[i] = true_value[i] + impact

    return observations, true_value


# ==========================================================================
# Run a single experiment
# ==========================================================================
def run_single(task_fn, alpha, method, seed):
    """Run one method on one task at one contamination level.

    Args:
        task_fn: one of generate_thermostat, generate_sensor, generate_market
        alpha: contamination strength
        method: 'monocular', 'mvsu_same', 'mvsu_arch', 'oracle'
        seed: random seed

    Returns: dict with mse, predictions, true_signal, observations, w_cross_history
    """
    rng = np.random.RandomState(seed)

    # Create predictor
    if method == 'monocular':
        predictor = LinearPredictor(D_IN, D_OUT, seed=seed)
        is_mvsu = False
    elif method == 'mvsu_same':
        base_A = LinearPredictor(D_IN, D_OUT, seed=seed)
        base_B = LinearPredictor(D_IN, D_OUT, seed=seed + 1000)
        predictor = MVSUPredictor(base_A, base_B, w_cross_init=-0.1)
        is_mvsu = True
    elif method == 'mvsu_arch':
        base_A = LinearPredictor(D_IN, D_OUT, seed=seed)
        base_B = MLPPredictor(D_IN, D_OUT, d_hidden=16, seed=seed + 2000)
        predictor = MVSUPredictor(base_A, base_B, w_cross_init=-0.1)
        is_mvsu = True
    elif method == 'oracle':
        predictor = OraclePredictor(D_IN, D_OUT, alpha=alpha, seed=seed)
        is_mvsu = False
    else:
        raise ValueError(f"Unknown method: {method}")

    # We need to generate the task online (predictions feed back into observations)
    predictions_list = [None] * N_TIMESTEPS
    obs_history = np.zeros(N_TIMESTEPS)
    true_signal = np.zeros(N_TIMESTEPS)
    pred_values = np.zeros(N_TIMESTEPS)
    w_cross_history = []

    # Pre-generate task data incrementally
    # We need step-by-step generation since predictions affect observations
    # Generate the full true signal first, then compute observations online
    t_arr = np.arange(N_TIMESTEPS)

    if task_fn == generate_thermostat:
        # Pre-generate true temperature
        raw_true = (20.0 + 5.0 * np.sin(2 * np.pi * t_arr / 200.0)
                    + 2.0 * np.sin(2 * np.pi * t_arr / 47.0 + 0.5)
                    + rng.randn(N_TIMESTEPS) * 0.5)
        target_temp = 22.0
        heater_gain = 3.0
        for t in range(N_TIMESTEPS):
            # Compute observation with feedback
            if t > 0 and predictions_list[t - 1] is not None:
                heater = heater_gain * np.clip(target_temp - predictions_list[t - 1], 0, 5.0)
            else:
                heater = 0.0
            obs_history[t] = raw_true[t] + alpha * heater
            true_signal[t] = raw_true[t]

            # Make features and predict
            features = make_features(obs_history, t)
            if is_mvsu:
                pred = predictor.predict(features)
            else:
                pred = predictor.predict(features)
            pred_val = float(pred.ravel()[0]) if hasattr(pred, 'ravel') else float(pred)
            predictions_list[t] = pred_val
            pred_values[t] = pred_val

            # Update predictor (target is the true signal)
            target = np.array([true_signal[t]])
            if is_mvsu:
                predictor.update(features, target, lr=LR, grad_clip=GRAD_CLIP)
            else:
                error = pred.ravel() - target
                grad = 2.0 * error
                predictor.update(grad, lr=LR, grad_clip=GRAD_CLIP)

            if is_mvsu and t % 20 == 0:
                w_cross_history.append(predictor.w_cross_value)

    elif task_fn == generate_sensor:
        # Pre-generate true signal
        raw_true = np.zeros(N_TIMESTEPS)
        raw_true[0] = rng.randn() * 0.5
        for i in range(1, N_TIMESTEPS):
            raw_true[i] = raw_true[i - 1] + 0.02 * np.sin(2 * np.pi * i / 300.0) + rng.randn() * 0.1

        cal_offset = 0.0
        for t in range(N_TIMESTEPS):
            obs_history[t] = raw_true[t] + cal_offset
            true_signal[t] = raw_true[t]

            features = make_features(obs_history, t)
            if is_mvsu:
                pred = predictor.predict(features)
            else:
                pred = predictor.predict(features)
            pred_val = float(pred.ravel()[0]) if hasattr(pred, 'ravel') else float(pred)
            predictions_list[t] = pred_val
            pred_values[t] = pred_val

            target = np.array([true_signal[t]])
            if is_mvsu:
                predictor.update(features, target, lr=LR, grad_clip=GRAD_CLIP)
            else:
                error = pred.ravel() - target
                grad = 2.0 * error
                predictor.update(grad, lr=LR, grad_clip=GRAD_CLIP)

            if is_mvsu and t % 20 == 0:
                w_cross_history.append(predictor.w_cross_value)

            # Update calibration offset for next step
            if t > 0:
                cal_offset += alpha * 0.05 * (predictions_list[t - 1] - obs_history[t - 1])

    elif task_fn == generate_market:
        # OU process
        theta = 0.1
        mu_val = 100.0
        sigma = 1.0
        raw_true = np.zeros(N_TIMESTEPS)
        raw_true[0] = mu_val + rng.randn() * 2.0
        for i in range(1, N_TIMESTEPS):
            raw_true[i] = (raw_true[i - 1] + theta * (mu_val - raw_true[i - 1]) + sigma * rng.randn())

        for t in range(N_TIMESTEPS):
            true_signal[t] = raw_true[t]
            if t > 0 and predictions_list[t - 1] is not None:
                impact = alpha * (predictions_list[t - 1] - raw_true[t])
            else:
                impact = 0.0
            obs_history[t] = raw_true[t] + impact

            features = make_features(obs_history, t)
            if is_mvsu:
                pred = predictor.predict(features)
            else:
                pred = predictor.predict(features)
            pred_val = float(pred.ravel()[0]) if hasattr(pred, 'ravel') else float(pred)
            predictions_list[t] = pred_val
            pred_values[t] = pred_val

            target = np.array([true_signal[t]])
            if is_mvsu:
                predictor.update(features, target, lr=LR, grad_clip=GRAD_CLIP)
            else:
                error = pred.ravel() - target
                grad = 2.0 * error
                predictor.update(grad, lr=LR, grad_clip=GRAD_CLIP)

            if is_mvsu and t % 20 == 0:
                w_cross_history.append(predictor.w_cross_value)

    # Compute MSE on true signal (post-warmup)
    valid = slice(WARMUP, N_TIMESTEPS)
    errors = (pred_values[valid] - true_signal[valid]) ** 2
    mse = float(np.mean(errors))
    var_true = float(np.var(true_signal[valid]))
    r2 = max(0.0, 1.0 - mse / var_true) if var_true > 1e-12 else 0.0

    return {
        'mse': mse,
        'r2': r2,
        'predictions': pred_values,
        'true_signal': true_signal,
        'observations': obs_history,
        'w_cross_history': w_cross_history,
    }


# ==========================================================================
# Run all experiments
# ==========================================================================
def run_all():
    """Run all tasks x methods x contamination levels x seeds."""
    tasks = {
        'Thermostat': generate_thermostat,
        'Sensor': generate_sensor,
        'Market': generate_market,
    }
    methods = ['monocular', 'mvsu_same', 'mvsu_arch', 'oracle']
    method_labels = {
        'monocular': 'Monocular',
        'mvsu_same': 'MVSU (same arch)',
        'mvsu_arch': 'MVSU (arch split)',
        'oracle': 'Oracle',
    }

    all_results = {}  # (task, method, alpha, seed) -> result dict

    total_runs = len(tasks) * len(methods) * len(CONTAMINATION_STRENGTHS) * N_SEEDS
    count = 0

    for task_name, task_fn in tasks.items():
        for method in methods:
            for alpha in CONTAMINATION_STRENGTHS:
                for seed in SEEDS:
                    result = run_single(task_fn, alpha, method, seed)
                    all_results[(task_name, method, alpha, seed)] = result
                    count += 1
                    if count % 50 == 0:
                        print(f"  Progress: {count}/{total_runs} runs ({100*count/total_runs:.0f}%)")

    return all_results, tasks, methods, method_labels


# ==========================================================================
# Analysis and tables
# ==========================================================================
def print_tables(all_results, tasks, methods, method_labels):
    """Print comprehensive results tables."""

    for task_name in tasks:
        print(f"\n{'='*70}")
        print(f"TASK: {task_name}")
        print(f"{'='*70}")

        # MSE table
        print(f"\n  MSE vs Contamination Strength:")
        header = f"  {'alpha':>6}"
        for m in methods:
            header += f"  {method_labels[m]:>16}"
        print(header)
        print("  " + "-" * (6 + 18 * len(methods)))

        for alpha in CONTAMINATION_STRENGTHS:
            row = f"  {alpha:>6.1f}"
            for m in methods:
                mses = [all_results[(task_name, m, alpha, s)]['mse'] for s in SEEDS]
                mean_mse = np.mean(mses)
                row += f"  {mean_mse:>16.4f}"
            print(row)

        # R^2 table
        print(f"\n  R^2 vs Contamination Strength:")
        header = f"  {'alpha':>6}"
        for m in methods:
            header += f"  {method_labels[m]:>16}"
        print(header)
        print("  " + "-" * (6 + 18 * len(methods)))

        for alpha in CONTAMINATION_STRENGTHS:
            row = f"  {alpha:>6.1f}"
            for m in methods:
                r2s = [all_results[(task_name, m, alpha, s)]['r2'] for s in SEEDS]
                mean_r2 = np.mean(r2s)
                row += f"  {mean_r2:>16.4f}"
            print(row)

        # MVSU improvement over monocular
        print(f"\n  MVSU Improvement over Monocular (% MSE reduction):")
        header = f"  {'alpha':>6}  {'MVSU(same)':>12}  {'MVSU(arch)':>12}"
        print(header)
        print("  " + "-" * 38)
        for alpha in CONTAMINATION_STRENGTHS:
            mono_mse = np.mean([all_results[(task_name, 'monocular', alpha, s)]['mse'] for s in SEEDS])
            mvsu_same_mse = np.mean([all_results[(task_name, 'mvsu_same', alpha, s)]['mse'] for s in SEEDS])
            mvsu_arch_mse = np.mean([all_results[(task_name, 'mvsu_arch', alpha, s)]['mse'] for s in SEEDS])
            if mono_mse > 1e-12:
                imp_same = (mono_mse - mvsu_same_mse) / mono_mse * 100
                imp_arch = (mono_mse - mvsu_arch_mse) / mono_mse * 100
            else:
                imp_same = 0.0
                imp_arch = 0.0
            print(f"  {alpha:>6.1f}  {imp_same:>+11.1f}%  {imp_arch:>+11.1f}%")

    # Summary across all tasks
    print(f"\n{'='*70}")
    print("CROSS-TASK SUMMARY")
    print(f"{'='*70}")

    print(f"\n  Mean MVSU improvement (%) at high contamination (alpha >= 0.6):")
    for task_name in tasks:
        improvements_same = []
        improvements_arch = []
        for alpha in [0.6, 0.8, 1.0]:
            mono = np.mean([all_results[(task_name, 'monocular', alpha, s)]['mse'] for s in SEEDS])
            same = np.mean([all_results[(task_name, 'mvsu_same', alpha, s)]['mse'] for s in SEEDS])
            arch = np.mean([all_results[(task_name, 'mvsu_arch', alpha, s)]['mse'] for s in SEEDS])
            if mono > 1e-12:
                improvements_same.append((mono - same) / mono * 100)
                improvements_arch.append((mono - arch) / mono * 100)
        mean_imp_same = np.mean(improvements_same)
        mean_imp_arch = np.mean(improvements_arch)
        print(f"    {task_name:>12}: MVSU(same)={mean_imp_same:+.1f}%, MVSU(arch)={mean_imp_arch:+.1f}%")

    # w_cross convergence summary
    print(f"\n  w_cross final values (MVSU same arch, alpha=0.8, first seed):")
    for task_name in tasks:
        result = all_results[(task_name, 'mvsu_same', 0.8, SEEDS[0])]
        wc_hist = result.get('w_cross_history', [])
        if wc_hist:
            wc_final = wc_hist[-1]
            print(f"    {task_name:>12}: w_cross = {wc_final:.4f} ({'NEGATIVE' if wc_final < 0 else 'POSITIVE'})")


# ==========================================================================
# Plotting
# ==========================================================================
def create_plots(all_results, tasks, methods, method_labels):
    """Generate 3x3 results plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(3, 3, figsize=(18, 15))
    fig.suptitle("MVSU Real-World Demo: Self-Referential Decontamination",
                 fontsize=14, fontweight='bold')

    colors = {
        'monocular': '#FF5722',
        'mvsu_same': '#2196F3',
        'mvsu_arch': '#4CAF50',
        'oracle': '#9C27B0',
    }
    task_list = list(tasks.keys())
    alphas = np.array(CONTAMINATION_STRENGTHS)

    for row_idx, task_name in enumerate(task_list):
        # ---- Column 1: MSE vs contamination strength ----
        ax = axes[row_idx, 0]
        for m in methods:
            mse_means = []
            mse_stds = []
            for alpha in CONTAMINATION_STRENGTHS:
                mses = [all_results[(task_name, m, alpha, s)]['mse'] for s in SEEDS]
                mse_means.append(np.mean(mses))
                mse_stds.append(np.std(mses) / np.sqrt(N_SEEDS))
            ax.errorbar(alphas, mse_means, yerr=mse_stds,
                        fmt='o-', color=colors[m], label=method_labels[m],
                        linewidth=2, markersize=5, capsize=3)
        ax.set_xlabel('Contamination strength')
        ax.set_ylabel('MSE (vs true signal)')
        ax.set_title(f'{task_name}: MSE vs Contamination')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # ---- Column 2: Example trajectory at alpha=0.6 ----
        ax = axes[row_idx, 1]
        alpha_show = 0.6
        seed_show = SEEDS[0]

        # Get results for this condition
        r_mono = all_results[(task_name, 'monocular', alpha_show, seed_show)]
        r_mvsu = all_results[(task_name, 'mvsu_same', alpha_show, seed_show)]

        # Plot a window of 200 timesteps after warmup
        t_start = WARMUP + 200
        t_end = min(t_start + 300, N_TIMESTEPS)
        t_range = np.arange(t_start, t_end)

        ax.plot(t_range, r_mono['true_signal'][t_start:t_end],
                'k-', linewidth=1.5, label='True signal', alpha=0.8)
        ax.plot(t_range, r_mono['observations'][t_start:t_end],
                '--', color='gray', linewidth=1, label='Observation', alpha=0.5)
        ax.plot(t_range, r_mono['predictions'][t_start:t_end],
                '-', color=colors['monocular'], linewidth=1, label='Monocular', alpha=0.7)
        ax.plot(t_range, r_mvsu['predictions'][t_start:t_end],
                '-', color=colors['mvsu_same'], linewidth=1, label='MVSU', alpha=0.7)
        ax.set_xlabel('Timestep')
        ax.set_ylabel('Value')
        ax.set_title(f'{task_name}: Trajectory (alpha={alpha_show})')
        ax.legend(fontsize=6, loc='upper right')
        ax.grid(True, alpha=0.3)

        # ---- Column 3: w_cross learned value (or summary for last row) ----
        if row_idx < 2:
            # w_cross vs contamination strength
            ax = axes[row_idx, 2]
            for alpha in CONTAMINATION_STRENGTHS:
                wc_finals = []
                for s in SEEDS:
                    r = all_results[(task_name, 'mvsu_same', alpha, s)]
                    wc_hist = r.get('w_cross_history', [])
                    if wc_hist:
                        wc_finals.append(wc_hist[-1])
                if wc_finals:
                    ax.scatter([alpha] * len(wc_finals), wc_finals,
                               color=colors['mvsu_same'], alpha=0.3, s=15)

            # Mean w_cross line
            wc_means = []
            for alpha in CONTAMINATION_STRENGTHS:
                wc_all = []
                for s in SEEDS:
                    r = all_results[(task_name, 'mvsu_same', alpha, s)]
                    wc_hist = r.get('w_cross_history', [])
                    if wc_hist:
                        wc_all.append(wc_hist[-1])
                wc_means.append(np.mean(wc_all) if wc_all else -0.1)
            ax.plot(alphas, wc_means, 'o-', color=colors['mvsu_same'],
                    linewidth=2, markersize=6, label='Mean w_cross')
            ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            ax.axhline(y=-0.1, color='red', linestyle=':', alpha=0.5, label='Init (-0.1)')
            ax.set_xlabel('Contamination strength')
            ax.set_ylabel('Learned w_cross')
            ax.set_title(f'{task_name}: w_cross vs Contamination')
            ax.legend(fontsize=7)
            ax.grid(True, alpha=0.3)
        else:
            # Summary panel: MVSU improvement across all tasks
            ax = axes[row_idx, 2]
            bar_width = 0.12
            x_pos = np.arange(len(CONTAMINATION_STRENGTHS))

            for t_idx, t_name in enumerate(task_list):
                improvements = []
                for alpha in CONTAMINATION_STRENGTHS:
                    mono = np.mean([all_results[(t_name, 'monocular', alpha, s)]['mse'] for s in SEEDS])
                    best_mvsu = min(
                        np.mean([all_results[(t_name, 'mvsu_same', alpha, s)]['mse'] for s in SEEDS]),
                        np.mean([all_results[(t_name, 'mvsu_arch', alpha, s)]['mse'] for s in SEEDS])
                    )
                    if mono > 1e-12:
                        imp = (mono - best_mvsu) / mono * 100
                    else:
                        imp = 0.0
                    improvements.append(imp)
                offset = (t_idx - 1) * bar_width
                task_colors = ['#FF9800', '#2196F3', '#4CAF50']
                ax.bar(x_pos + offset, improvements, bar_width,
                       label=t_name, color=task_colors[t_idx], alpha=0.7, edgecolor='black')

            ax.axhline(y=0, color='black', linewidth=1)
            ax.axhline(y=5, color='red', linestyle='--', alpha=0.5, label='>5% target')
            ax.set_xticks(x_pos)
            ax.set_xticklabels([f'{a:.1f}' for a in CONTAMINATION_STRENGTHS])
            ax.set_xlabel('Contamination strength')
            ax.set_ylabel('MVSU Improvement (%)')
            ax.set_title('Summary: Best MVSU Improvement vs Monocular')
            ax.legend(fontsize=7)
            ax.grid(True, alpha=0.3, axis='y')

            # Also add w_cross panel for Market task
            # We already have this row's w_cross info — add it as text annotation
            wc_text = "Market w_cross: "
            for alpha in [0.0, 0.4, 0.8]:
                wc_all = []
                for s in SEEDS:
                    r = all_results[('Market', 'mvsu_same', alpha, s)]
                    wc_hist = r.get('w_cross_history', [])
                    if wc_hist:
                        wc_all.append(wc_hist[-1])
                if wc_all:
                    wc_text += f"a={alpha}: {np.mean(wc_all):.3f}  "
            ax.text(0.02, 0.02, wc_text, transform=ax.transAxes, fontsize=6,
                    verticalalignment='bottom', style='italic')

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "mvsu_real_demo_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==========================================================================
# Success evaluation
# ==========================================================================
def evaluate_success(all_results, tasks):
    """Evaluate against success criteria."""
    print(f"\n{'='*70}")
    print("SUCCESS EVALUATION")
    print(f"{'='*70}")

    # Count tasks where MVSU beats monocular by >5% at high contamination
    tasks_with_advantage = 0
    w_cross_negative = 0
    improvement_grows = 0

    for task_name in tasks:
        # Best MVSU improvement at high contamination (alpha >= 0.6)
        improvements_high = []
        for alpha in [0.6, 0.8, 1.0]:
            mono = np.mean([all_results[(task_name, 'monocular', alpha, s)]['mse'] for s in SEEDS])
            best_mvsu = min(
                np.mean([all_results[(task_name, 'mvsu_same', alpha, s)]['mse'] for s in SEEDS]),
                np.mean([all_results[(task_name, 'mvsu_arch', alpha, s)]['mse'] for s in SEEDS])
            )
            if mono > 1e-12:
                imp = (mono - best_mvsu) / mono * 100
            else:
                imp = 0.0
            improvements_high.append(imp)

        mean_imp_high = np.mean(improvements_high)
        if mean_imp_high > 5.0:
            tasks_with_advantage += 1
            print(f"  [PASS] {task_name}: Mean improvement at high contamination = {mean_imp_high:.1f}% (> 5%)")
        else:
            print(f"  [    ] {task_name}: Mean improvement at high contamination = {mean_imp_high:.1f}% (< 5%)")

        # w_cross convergence
        wc_finals = []
        for s in SEEDS:
            r = all_results[(task_name, 'mvsu_same', 0.8, s)]
            wc_hist = r.get('w_cross_history', [])
            if wc_hist:
                wc_finals.append(wc_hist[-1])
        if wc_finals and np.mean(wc_finals) < 0:
            w_cross_negative += 1
            print(f"  [PASS] {task_name}: w_cross converges negative ({np.mean(wc_finals):.4f})")
        elif wc_finals:
            print(f"  [    ] {task_name}: w_cross NOT negative ({np.mean(wc_finals):.4f})")

        # Improvement grows with contamination
        imp_low = []
        imp_high2 = []
        for alpha in [0.0, 0.2]:
            mono = np.mean([all_results[(task_name, 'monocular', alpha, s)]['mse'] for s in SEEDS])
            best = min(
                np.mean([all_results[(task_name, 'mvsu_same', alpha, s)]['mse'] for s in SEEDS]),
                np.mean([all_results[(task_name, 'mvsu_arch', alpha, s)]['mse'] for s in SEEDS])
            )
            if mono > 1e-12:
                imp_low.append((mono - best) / mono * 100)
        for alpha in [0.8, 1.0]:
            mono = np.mean([all_results[(task_name, 'monocular', alpha, s)]['mse'] for s in SEEDS])
            best = min(
                np.mean([all_results[(task_name, 'mvsu_same', alpha, s)]['mse'] for s in SEEDS]),
                np.mean([all_results[(task_name, 'mvsu_arch', alpha, s)]['mse'] for s in SEEDS])
            )
            if mono > 1e-12:
                imp_high2.append((mono - best) / mono * 100)

        if imp_low and imp_high2 and np.mean(imp_high2) > np.mean(imp_low):
            improvement_grows += 1
            print(f"  [PASS] {task_name}: Improvement grows with contamination "
                  f"(low={np.mean(imp_low):.1f}%, high={np.mean(imp_high2):.1f}%)")
        else:
            low_val = np.mean(imp_low) if imp_low else 0
            high_val = np.mean(imp_high2) if imp_high2 else 0
            print(f"  [    ] {task_name}: Improvement does NOT grow "
                  f"(low={low_val:.1f}%, high={high_val:.1f}%)")

    print(f"\n  OVERALL VERDICT:")
    if tasks_with_advantage >= 2 and w_cross_negative >= 2 and improvement_grows >= 2:
        print(f"  >>> STRONG SUCCESS: MVSU beats monocular on {tasks_with_advantage}/3 tasks, "
              f"w_cross negative on {w_cross_negative}/3, improvement grows on {improvement_grows}/3")
    elif tasks_with_advantage >= 1:
        print(f"  >>> MODERATE SUCCESS: MVSU beats monocular on {tasks_with_advantage}/3 tasks")
    else:
        print(f"  >>> INFORMATIVE FAILURE: MVSU does not clearly beat monocular")
        print(f"       Tasks with >5% improvement: {tasks_with_advantage}/3")
        print(f"       w_cross negative: {w_cross_negative}/3")
        print(f"       Improvement grows with contamination: {improvement_grows}/3")

        # Root cause analysis
        print(f"\n  ROOT CAUSE ANALYSIS:")
        for task_name in tasks:
            mono_mses = {a: np.mean([all_results[(task_name, 'monocular', a, s)]['mse'] for s in SEEDS])
                         for a in CONTAMINATION_STRENGTHS}
            oracle_mses = {a: np.mean([all_results[(task_name, 'oracle', a, s)]['mse'] for s in SEEDS])
                           for a in CONTAMINATION_STRENGTHS}
            # Does contamination actually hurt? Compare alpha=0 to alpha=1
            mono_0 = mono_mses[0.0]
            mono_1 = mono_mses[1.0]
            oracle_1 = oracle_mses[1.0]
            contamination_impact = (mono_1 - mono_0) / mono_0 * 100 if mono_0 > 1e-12 else 0
            oracle_gap = (mono_1 - oracle_1) / mono_1 * 100 if mono_1 > 1e-12 else 0
            print(f"    {task_name}:")
            print(f"      Contamination impact (MSE increase alpha=0->1): {contamination_impact:+.1f}%")
            print(f"      Oracle gap at alpha=1 (room for improvement): {oracle_gap:.1f}%")
            if contamination_impact < 10:
                print(f"      -> Contamination has MINIMAL impact. Task may not be strongly self-referential.")
            if oracle_gap < 5:
                print(f"      -> Oracle provides little advantage. Monocular may already be near-optimal.")


# ==========================================================================
# Main
# ==========================================================================
def main():
    print("=" * 70)
    print("MVSU REAL-WORLD DEMO")
    print("Self-Referential Decontamination on Continuous Feedback Tasks")
    print("=" * 70)
    print(f"  Timesteps: {N_TIMESTEPS}, Warmup: {WARMUP}")
    print(f"  Seeds: {N_SEEDS} ({SEEDS[0]}..{SEEDS[-1]})")
    print(f"  Learning rate: {LR}")
    print(f"  Feature window: {WINDOW}")
    print(f"  Contamination strengths: {CONTAMINATION_STRENGTHS}")
    print(f"  Methods: Monocular, MVSU(same arch), MVSU(arch split), Oracle")
    print()

    t_start = time.time()

    # Run all experiments
    print("Running experiments...")
    all_results, tasks, methods_list, method_labels = run_all()
    run_time = time.time() - t_start
    print(f"  All runs complete in {run_time:.1f}s")

    # Analysis
    print_tables(all_results, tasks, methods_list, method_labels)

    # Success evaluation
    evaluate_success(all_results, tasks)

    # Plots
    print("\nGenerating plots...")
    create_plots(all_results, tasks, methods_list, method_labels)

    total_time = time.time() - t_start
    print(f"\nTotal runtime: {total_time:.1f}s")
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
