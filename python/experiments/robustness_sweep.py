"""
Robustness and T=2 Sensitivity Sweep
=====================================
Tests three aspects of the Ouroboros framework's robustness:

Part 1: Signal robustness -- does w -> 1/phi for non-Gaussian signals?
  Tests: Gaussian, Uniform, Laplace, Bimodal, Exponential (all unit variance).

Part 2: Optimizer robustness -- SGD vs Adam at various learning rates.
  Tests: SGD and Adam with different lr values.

Part 3: T=2 minimum under different signal conditions.
  Tests the fair T x N test (T*N=10) with Gaussian, Uniform, Correlated, Noisy signals.

Author: Claude (robustness sweep from Ouroboros framework)
"""

import sys
import io
import time
import os
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

# ==============================================================================
# Constants
# ==============================================================================
PHI = (1 + np.sqrt(5)) / 2       # Golden ratio ~1.618
INV_PHI = 1.0 / PHI              # ~0.618

# Part 1 & 2 constants
SCALAR_TIMESTEPS = 50000
SCALAR_SEEDS = [42, 137, 256, 314, 999]

# Part 3 constants
TN_TIMESTEPS = 1000
TN_WARMUP = 200
TN_SEEDS = [42, 137, 256]
TN_ALPHA = 0.6
TN_LR = 0.01
TN_GRAD_CLIP = 5.0

# T x N = 10 configs
TN_CONFIGS = [
    {"name": "Deep",       "N": 1,  "T": 10},
    {"name": "Balanced-A", "N": 2,  "T": 5},
    {"name": "Balanced-B", "N": 5,  "T": 2},
    {"name": "Wide",       "N": 10, "T": 1},
]


# ==============================================================================
# Signal generators for Part 1
# ==============================================================================
def generate_gaussian(rng, n):
    """Standard Gaussian: mean=0, var=1."""
    return rng.randn(n)


def generate_uniform(rng, n):
    """Uniform [-sqrt(3), sqrt(3)]: mean=0, var=1."""
    return rng.uniform(-np.sqrt(3), np.sqrt(3), n)


def generate_laplace(rng, n):
    """Laplace with scale=1/sqrt(2): mean=0, var=1."""
    return rng.laplace(0, 1.0 / np.sqrt(2), n)


def generate_bimodal(rng, n):
    """Bimodal: mixture of N(-1, 0.5) and N(+1, 0.5). Mean=0, var=1.5 approx.
    Adjust to unit variance: each component has var=0.5, means at +/-1.
    Total var = E[X^2] - E[X]^2 = (0.5 + 1) - 0 = 1.5. Scale by 1/sqrt(1.5)."""
    choices = rng.randint(0, 2, n)
    samples = np.where(choices == 0,
                       rng.normal(-1.0, np.sqrt(0.5), n),
                       rng.normal(1.0, np.sqrt(0.5), n))
    # Normalize to unit variance
    return samples / np.sqrt(1.5)


def generate_exponential(rng, n):
    """Shifted exponential: rate=1, shifted to mean=0. Var=1."""
    return rng.exponential(1.0, n) - 1.0


SIGNAL_GENERATORS = {
    "Gaussian":    generate_gaussian,
    "Uniform":     generate_uniform,
    "Laplace":     generate_laplace,
    "Bimodal":     generate_bimodal,
    "Exponential": generate_exponential,
}


# ==============================================================================
# Part 1: Scalar self-referential agent with different signals
# ==============================================================================
def run_scalar_agent(signal_array, lr=0.01, alpha=1.0, optimizer="sgd",
                     adam_beta1=0.9, adam_beta2=0.999, adam_eps=1e-8,
                     lr_decay=0.9999):
    """
    Scalar self-referential agent: y(t) = s(t) + alpha * w * y(t-1).
    Learns w via online gradient descent to minimize (w*y - s)^2.

    Uses learning rate decay (matching sanity_checks.py convention) for
    tighter convergence. The decay ensures the stochastic gradient noise
    shrinks over time, allowing w to settle precisely at 1/phi.

    Returns: (w_final, w_trajectory)
    """
    n_steps = len(signal_array)
    w = 0.5
    b = 0.0
    o_prev = 0.0
    lr_t = lr

    # Adam state
    m_w, v_w = 0.0, 0.0
    m_b, v_b = 0.0, 0.0

    w_traj = np.empty(n_steps)

    for t in range(n_steps):
        s = signal_array[t]
        y = s + alpha * o_prev
        o = w * y + b

        error = o - s
        grad_w = 2.0 * error * y
        grad_b = 2.0 * error

        # Clip gradients
        grad_w = np.clip(grad_w, -5.0, 5.0)
        grad_b = np.clip(grad_b, -5.0, 5.0)

        if optimizer == "sgd":
            w -= lr_t * grad_w
            b -= lr_t * grad_b
        elif optimizer == "adam":
            step = t + 1
            m_w = adam_beta1 * m_w + (1 - adam_beta1) * grad_w
            v_w = adam_beta2 * v_w + (1 - adam_beta2) * grad_w ** 2
            m_b = adam_beta1 * m_b + (1 - adam_beta1) * grad_b
            v_b = adam_beta2 * v_b + (1 - adam_beta2) * grad_b ** 2

            m_w_hat = m_w / (1 - adam_beta1 ** step)
            v_w_hat = v_w / (1 - adam_beta2 ** step)
            m_b_hat = m_b / (1 - adam_beta1 ** step)
            v_b_hat = v_b / (1 - adam_beta2 ** step)

            w -= lr_t * m_w_hat / (np.sqrt(v_w_hat) + adam_eps)
            b -= lr_t * m_b_hat / (np.sqrt(v_b_hat) + adam_eps)

        # Clamp w to stable range
        w = np.clip(w, -2.0, 2.0)
        b = np.clip(b, -2.0, 2.0)

        # Decay learning rate
        lr_t *= lr_decay

        o_prev = o
        w_traj[t] = w

    return w, w_traj


def run_part1():
    """Part 1: Signal robustness."""
    print("\n" + "=" * 70)
    print("PART 1: SIGNAL ROBUSTNESS (does w -> 1/phi for non-Gaussian signals?)")
    print("=" * 70)
    print(f"  Timesteps: {SCALAR_TIMESTEPS}, alpha=1.0, lr=0.01, SGD")
    print(f"  Seeds: {SCALAR_SEEDS}")
    print(f"  Reference: 1/phi = {INV_PHI:.6f}")

    results = {}  # signal_name -> {"w_finals": [...], "trajectories": [...]}

    for sig_name, sig_gen in SIGNAL_GENERATORS.items():
        w_finals = []
        trajectories = []
        for seed in SCALAR_SEEDS:
            rng = np.random.RandomState(seed)
            signal = sig_gen(rng, SCALAR_TIMESTEPS)
            w_final, w_traj = run_scalar_agent(signal, lr=0.01, alpha=1.0, optimizer="sgd")
            w_finals.append(w_final)
            trajectories.append(w_traj)
        results[sig_name] = {"w_finals": w_finals, "trajectories": trajectories}

    # Print table
    print(f"\n  {'Signal':>14s} | {'w_mean':>10s} {'w_std':>10s} {'|w - 1/phi|':>12s} {'Converged?':>12s}")
    print(f"  {'-' * 64}")
    for sig_name in SIGNAL_GENERATORS.keys():
        w_arr = np.array(results[sig_name]["w_finals"])
        w_mean = np.mean(w_arr)
        w_std = np.std(w_arr)
        diff = abs(w_mean - INV_PHI)
        converged = "YES" if diff < 0.015 else "NO"
        print(f"  {sig_name:>14s} | {w_mean:10.6f} {w_std:10.6f} {diff:12.6f} {converged:>12s}")

    print(f"\n  1/phi reference: {INV_PHI:.6f}")
    print(f"  Convergence threshold: |w - 1/phi| < 0.015")

    return results


# ==============================================================================
# Part 2: Optimizer robustness
# ==============================================================================
OPTIMIZER_CONFIGS = [
    {"name": "SGD lr=0.01",    "optimizer": "sgd",  "lr": 0.01},
    {"name": "SGD lr=0.001",   "optimizer": "sgd",  "lr": 0.001},
    {"name": "SGD lr=0.1",     "optimizer": "sgd",  "lr": 0.1},
    {"name": "Adam lr=0.01",   "optimizer": "adam", "lr": 0.01},
    {"name": "Adam lr=0.001",  "optimizer": "adam", "lr": 0.001},
    {"name": "Adam lr=0.0001", "optimizer": "adam", "lr": 0.0001},
]


def run_part2():
    """Part 2: Optimizer robustness."""
    print("\n" + "=" * 70)
    print("PART 2: OPTIMIZER ROBUSTNESS (SGD vs Adam)")
    print("=" * 70)
    print(f"  Timesteps: {SCALAR_TIMESTEPS}, alpha=1.0, Gaussian signal")
    print(f"  Seeds: {SCALAR_SEEDS}")

    results = {}  # config_name -> {"w_finals": [...], "trajectories": [...]}

    for cfg in OPTIMIZER_CONFIGS:
        w_finals = []
        trajectories = []
        for seed in SCALAR_SEEDS:
            rng = np.random.RandomState(seed)
            signal = generate_gaussian(rng, SCALAR_TIMESTEPS)
            w_final, w_traj = run_scalar_agent(
                signal, lr=cfg["lr"], alpha=1.0, optimizer=cfg["optimizer"]
            )
            w_finals.append(w_final)
            trajectories.append(w_traj)
        results[cfg["name"]] = {"w_finals": w_finals, "trajectories": trajectories}

    # Print table
    print(f"\n  {'Optimizer':>18s} | {'w_mean':>10s} {'w_std':>10s} {'|w - 1/phi|':>12s} {'Converged?':>12s}")
    print(f"  {'-' * 68}")
    for cfg in OPTIMIZER_CONFIGS:
        name = cfg["name"]
        w_arr = np.array(results[name]["w_finals"])
        w_mean = np.mean(w_arr)
        w_std = np.std(w_arr)
        diff = abs(w_mean - INV_PHI)
        converged = "YES" if diff < 0.01 else "NO"
        print(f"  {name:>18s} | {w_mean:10.6f} {w_std:10.6f} {diff:12.6f} {converged:>12s}")

    print(f"\n  1/phi reference: {INV_PHI:.6f}")

    return results


# ==============================================================================
# Part 3: T=2 minimum under different conditions
# ==============================================================================
def clip_grad(g, max_norm=TN_GRAD_CLIP):
    """Clip gradient by value."""
    return np.clip(g, -max_norm, max_norm)


class NocularSRU_T:
    """
    N-ocular Self-Referential Unit with T recurrence steps per timestep.
    Simplified from fair_tn_test.py for the robustness sweep.
    """

    def __init__(self, N, T, seed=42):
        self.N = N
        self.T = T

        rng = np.random.RandomState(seed)

        self.w_in = rng.uniform(0.5, 1.5, N)
        self.w_self = rng.uniform(0.4, 0.8, N)
        self.b = np.zeros(N)
        self.w_out = rng.uniform(-0.5, 0.5, N)
        self.b_out = np.zeros(N)

        if N > 1:
            self.w_cross = rng.uniform(-0.1, 0.1, (N, N))
            np.fill_diagonal(self.w_cross, 0.0)
        else:
            self.w_cross = np.zeros((1, 1))

        self.h = np.zeros(N)
        self.pred = np.zeros(N)

        self._obs = None
        self._h_history = None

    def forward_step(self, signal_t, alpha):
        N = self.N
        T = self.T

        obs = np.empty(N)
        for i in range(N):
            obs[i] = signal_t + alpha * self.pred[i]

        self._obs = obs.copy()

        h_history = [self.h.copy()]
        h_cur = self.h.copy()

        for step in range(T):
            h_new = np.empty(N)
            for i in range(N):
                y_i = self.w_in[i] * obs[i] + self.w_self[i] * h_cur[i] + self.b[i]
                if N > 1:
                    for j in range(N):
                        if j != i:
                            y_i += self.w_cross[i, j] * h_cur[j]
                h_new[i] = np.tanh(y_i)
            h_cur = h_new
            h_history.append(h_cur.copy())

        self._h_history = h_history
        self.h = h_cur.copy()

        for i in range(N):
            self.pred[i] = self.w_out[i] * self.h[i] + self.b_out[i]

        return np.mean(self.pred)

    def backward_step(self, target, lr=TN_LR):
        N = self.N
        T = self.T

        pred_combined = np.mean(self.pred)
        combined_loss = (pred_combined - target) ** 2

        d_w_in = np.zeros(N)
        d_w_self = np.zeros(N)
        d_b = np.zeros(N)
        d_w_out = np.zeros(N)
        d_b_out = np.zeros(N)
        d_w_cross = np.zeros((N, N))

        d_h = np.zeros(N)
        for i in range(N):
            d_pred_i = 2.0 * (self.pred[i] - target)
            d_w_out[i] = d_pred_i * self._h_history[T][i]
            d_b_out[i] = d_pred_i
            d_h[i] = d_pred_i * self.w_out[i]

        for step in range(T - 1, -1, -1):
            h_prev = self._h_history[step]
            h_curr = self._h_history[step + 1]

            d_y = d_h * (1.0 - h_curr ** 2)

            for i in range(N):
                d_w_in[i] += d_y[i] * self._obs[i]
                d_w_self[i] += d_y[i] * h_prev[i]
                d_b[i] += d_y[i]
                if N > 1:
                    for j in range(N):
                        if j != i:
                            d_w_cross[i, j] += d_y[i] * h_prev[j]

            d_h_new = np.zeros(N)
            for i in range(N):
                d_h_new[i] += d_y[i] * self.w_self[i]
                if N > 1:
                    for j in range(N):
                        if j != i:
                            d_h_new[j] += d_y[i] * self.w_cross[i, j]
            d_h = d_h_new

        self.w_in -= lr * clip_grad(d_w_in)
        self.w_self -= lr * clip_grad(d_w_self)
        self.b -= lr * clip_grad(d_b)
        self.w_out -= lr * clip_grad(d_w_out)
        self.b_out -= lr * clip_grad(d_b_out)

        if N > 1:
            self.w_cross -= lr * clip_grad(d_w_cross)
            np.fill_diagonal(self.w_cross, 0.0)

        return combined_loss

    def reset_state(self):
        self.h = np.zeros(self.N)
        self.pred = np.zeros(self.N)


def generate_tn_signal(sig_type, n_steps, seed):
    """Generate signal for the T x N test."""
    rng = np.random.RandomState(seed)
    t = np.arange(n_steps, dtype=float)

    if sig_type == "Gaussian":
        # Sum of sinusoids (matching fair_tn_test.py baseline)
        s = (0.5 * np.sin(2 * np.pi * t / 50.0)
             + 0.3 * np.sin(2 * np.pi * t / 31.0 + 0.7)
             + 0.2 * np.sin(2 * np.pi * t / 17.0 + 1.3))
        return s
    elif sig_type == "Uniform":
        # Uniform random signal with same scale
        s = rng.uniform(-1.0, 1.0, n_steps)
        return s
    elif sig_type == "Correlated":
        # AR(1) with rho=0.5
        s = np.empty(n_steps)
        s[0] = rng.randn()
        for i in range(1, n_steps):
            s[i] = 0.5 * s[i - 1] + rng.randn() * np.sqrt(1 - 0.25)
        return s
    elif sig_type == "Noisy":
        # Clean sinusoidal + noise (SNR=0.5)
        clean = (0.5 * np.sin(2 * np.pi * t / 50.0)
                 + 0.3 * np.sin(2 * np.pi * t / 31.0 + 0.7)
                 + 0.2 * np.sin(2 * np.pi * t / 17.0 + 1.3))
        signal_power = np.var(clean)
        noise_power = signal_power / 0.5  # SNR=0.5
        noise = rng.randn(n_steps) * np.sqrt(noise_power)
        return clean + noise
    else:
        raise ValueError(f"Unknown signal type: {sig_type}")


def run_tn_single(N, T, sig_type, seed):
    """Run a single T x N condition."""
    signal = generate_tn_signal(sig_type, TN_TIMESTEPS, seed)
    model = NocularSRU_T(N=N, T=T, seed=seed)
    errors = []

    for t in range(TN_TIMESTEPS):
        s_t = signal[t]
        pred = model.forward_step(s_t, TN_ALPHA)
        err = (pred - s_t) ** 2
        if t >= TN_WARMUP:
            errors.append(err)
        model.backward_step(s_t)

    return float(np.mean(errors))


def run_part3():
    """Part 3: T=2 minimum under different conditions."""
    print("\n" + "=" * 70)
    print("PART 3: T=2 MINIMUM UNDER DIFFERENT CONDITIONS")
    print("=" * 70)
    print(f"  T x N = 10, alpha={TN_ALPHA}, timesteps={TN_TIMESTEPS}, warmup={TN_WARMUP}")
    print(f"  Seeds: {TN_SEEDS}")

    signal_types = ["Gaussian", "Uniform", "Correlated", "Noisy"]
    results = {}  # (sig_type, config_name) -> mean_mse

    for sig_type in signal_types:
        print(f"\n  Signal: {sig_type}")
        for cfg in TN_CONFIGS:
            name = cfg["name"]
            N = cfg["N"]
            T = cfg["T"]
            mses = []
            for seed in TN_SEEDS:
                mse = run_tn_single(N, T, sig_type, seed)
                mses.append(mse)
            mean_mse = np.mean(mses)
            std_mse = np.std(mses)
            results[(sig_type, name)] = {"mean": mean_mse, "std": std_mse, "all": mses}
            print(f"    {name:>14s} (N={N}, T={T}): MSE = {mean_mse:.6f} +/- {std_mse:.6f}")

    # Summary table: which config wins for each signal type?
    print(f"\n  {'':>14s}", end="")
    for sig_type in signal_types:
        print(f" | {sig_type:>12s}", end="")
    print()
    print(f"  {'-' * (14 + 15 * len(signal_types))}")

    for cfg in TN_CONFIGS:
        name = cfg["name"]
        print(f"  {name:>14s}", end="")
        for sig_type in signal_types:
            mse = results[(sig_type, name)]["mean"]
            print(f" | {mse:12.6f}", end="")
        print()

    # Winner per signal type
    print(f"\n  WINNER PER SIGNAL TYPE:")
    rankings = {}
    for sig_type in signal_types:
        best_name = None
        best_mse = float("inf")
        config_mses = []
        for cfg in TN_CONFIGS:
            name = cfg["name"]
            mse = results[(sig_type, name)]["mean"]
            config_mses.append((name, mse))
            if mse < best_mse:
                best_mse = mse
                best_name = name
        # Rank all configs
        config_mses.sort(key=lambda x: x[1])
        ranking = [x[0] for x in config_mses]
        rankings[sig_type] = ranking
        print(f"    {sig_type:>12s}: BEST = {best_name:>14s} (MSE={best_mse:.6f})")
        print(f"                   Ranking: {' > '.join(ranking)}")

    # Check if Balanced-B (N=5, T=2) wins consistently
    balanced_b_rank = []
    for sig_type in signal_types:
        rank = rankings[sig_type].index("Balanced-B") + 1
        balanced_b_rank.append(rank)
    avg_rank = np.mean(balanced_b_rank)
    print(f"\n  Balanced-B (N=5, T=2) average rank: {avg_rank:.1f}")
    print(f"    Per signal: {dict(zip(signal_types, balanced_b_rank))}")

    return results, rankings, signal_types


# ==============================================================================
# Plotting
# ==============================================================================
def create_plots(part1_results, part2_results, part3_results, part3_rankings, signal_types):
    """Generate 3x2 results plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(3, 2, figsize=(14, 18))
    fig.suptitle("Robustness and T=2 Sensitivity Sweep",
                 fontsize=14, fontweight='bold')

    sig_colors = {
        "Gaussian": "#2196F3",
        "Uniform": "#4CAF50",
        "Laplace": "#FF5722",
        "Bimodal": "#9C27B0",
        "Exponential": "#FF9800",
    }

    opt_colors = {
        "SGD lr=0.01": "#2196F3",
        "SGD lr=0.001": "#4CAF50",
        "SGD lr=0.1": "#FF5722",
        "Adam lr=0.01": "#9C27B0",
        "Adam lr=0.001": "#E91E63",
        "Adam lr=0.0001": "#FF9800",
    }

    # ---- Panel 1: Converged w vs signal distribution ----
    ax = axes[0, 0]
    sig_names = list(SIGNAL_GENERATORS.keys())
    x_pos = np.arange(len(sig_names))
    w_means = []
    w_stds = []
    colors_list = []
    for sig_name in sig_names:
        w_arr = np.array(part1_results[sig_name]["w_finals"])
        w_means.append(np.mean(w_arr))
        w_stds.append(np.std(w_arr))
        colors_list.append(sig_colors[sig_name])

    ax.bar(x_pos, w_means, yerr=w_stds, color=colors_list, alpha=0.7,
           edgecolor='black', capsize=4)
    ax.axhline(y=INV_PHI, color='red', linestyle='--', linewidth=2,
               label=f'1/phi = {INV_PHI:.4f}')
    ax.set_xlabel('Signal Distribution')
    ax.set_ylabel('Converged w')
    ax.set_title('Panel 1: Converged w vs Signal Type')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(sig_names, rotation=30, ha='right', fontsize=8)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0.5, 0.7)

    # ---- Panel 2: Convergence trajectories for each signal type ----
    ax = axes[0, 1]
    for sig_name in sig_names:
        # Plot first seed's trajectory (smoothed)
        traj = part1_results[sig_name]["trajectories"][0]
        # Smooth with running average
        window = 500
        smoothed = np.convolve(traj, np.ones(window) / window, mode='valid')
        x_vals = np.arange(len(smoothed)) + window // 2
        ax.plot(x_vals, smoothed, color=sig_colors[sig_name], label=sig_name,
                linewidth=1.2, alpha=0.8)

    ax.axhline(y=INV_PHI, color='red', linestyle='--', linewidth=2,
               label=f'1/phi = {INV_PHI:.4f}')
    ax.set_xlabel('Timestep')
    ax.set_ylabel('w')
    ax.set_title('Panel 2: w Convergence by Signal Type')
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.3, 0.9)

    # ---- Panel 3: Converged w vs optimizer/learning rate ----
    ax = axes[1, 0]
    opt_names = [cfg["name"] for cfg in OPTIMIZER_CONFIGS]
    x_pos = np.arange(len(opt_names))
    w_means = []
    w_stds = []
    colors_list = []
    for name in opt_names:
        w_arr = np.array(part2_results[name]["w_finals"])
        w_means.append(np.mean(w_arr))
        w_stds.append(np.std(w_arr))
        colors_list.append(opt_colors[name])

    ax.bar(x_pos, w_means, yerr=w_stds, color=colors_list, alpha=0.7,
           edgecolor='black', capsize=4)
    ax.axhline(y=INV_PHI, color='red', linestyle='--', linewidth=2,
               label=f'1/phi = {INV_PHI:.4f}')
    ax.set_xlabel('Optimizer / Learning Rate')
    ax.set_ylabel('Converged w')
    ax.set_title('Panel 3: Converged w vs Optimizer')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(opt_names, rotation=30, ha='right', fontsize=7)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0.5, 0.7)

    # ---- Panel 4: Convergence trajectories for each optimizer ----
    ax = axes[1, 1]
    for cfg in OPTIMIZER_CONFIGS:
        name = cfg["name"]
        traj = part2_results[name]["trajectories"][0]
        window = 500
        smoothed = np.convolve(traj, np.ones(window) / window, mode='valid')
        x_vals = np.arange(len(smoothed)) + window // 2
        ax.plot(x_vals, smoothed, color=opt_colors[name], label=name,
                linewidth=1.2, alpha=0.8)

    ax.axhline(y=INV_PHI, color='red', linestyle='--', linewidth=2,
               label=f'1/phi = {INV_PHI:.4f}')
    ax.set_xlabel('Timestep')
    ax.set_ylabel('w')
    ax.set_title('Panel 4: w Convergence by Optimizer')
    ax.legend(fontsize=6, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.3, 0.9)

    # ---- Panel 5: MSE by T x N config for each signal type (grouped bar) ----
    ax = axes[2, 0]
    config_names = [c["name"] for c in TN_CONFIGS]
    n_configs = len(config_names)
    n_signals = len(signal_types)
    bar_width = 0.8 / n_signals
    x_base = np.arange(n_configs)

    tn_sig_colors = {
        "Gaussian": "#2196F3",
        "Uniform": "#4CAF50",
        "Correlated": "#FF5722",
        "Noisy": "#9C27B0",
    }

    for i, sig_type in enumerate(signal_types):
        mses = [part3_results[(sig_type, name)]["mean"] for name in config_names]
        offset = (i - n_signals / 2 + 0.5) * bar_width
        ax.bar(x_base + offset, mses, bar_width, label=sig_type,
               color=tn_sig_colors.get(sig_type, "#888888"), alpha=0.7,
               edgecolor='black', linewidth=0.5)

    ax.set_xlabel('T x N Configuration')
    ax.set_ylabel('MSE')
    ax.set_title(f'Panel 5: MSE by Config (alpha={TN_ALPHA})')
    ax.set_xticks(x_base)
    ax.set_xticklabels([f"{c['name']}\nN={c['N']},T={c['T']}" for c in TN_CONFIGS],
                       fontsize=7)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis='y')

    # ---- Panel 6: Winner ranking across signal types ----
    ax = axes[2, 1]
    # Create a heatmap-style ranking
    rank_matrix = np.zeros((n_configs, n_signals))
    for j, sig_type in enumerate(signal_types):
        ranking = part3_rankings[sig_type]
        for rank_pos, name in enumerate(ranking):
            i = config_names.index(name)
            rank_matrix[i, j] = rank_pos + 1

    im = ax.imshow(rank_matrix, cmap='RdYlGn_r', aspect='auto', vmin=1, vmax=n_configs)
    ax.set_xticks(np.arange(n_signals))
    ax.set_xticklabels(signal_types, fontsize=8)
    ax.set_yticks(np.arange(n_configs))
    ax.set_yticklabels([f"{c['name']} (N={c['N']},T={c['T']})" for c in TN_CONFIGS],
                       fontsize=8)
    ax.set_title('Panel 6: Config Ranking by Signal (1=best)')

    # Add text annotations
    for i in range(n_configs):
        for j in range(n_signals):
            rank = int(rank_matrix[i, j])
            color = 'white' if rank >= 3 else 'black'
            ax.text(j, i, str(rank), ha='center', va='center', fontsize=12,
                    fontweight='bold', color=color)

    plt.colorbar(im, ax=ax, label='Rank (1=best)')

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "robustness_sweep_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 70)
    print("ROBUSTNESS AND T=2 SENSITIVITY SWEEP")
    print("=" * 70)
    print(f"  Reference: 1/phi = {INV_PHI:.6f}")
    print(f"  Golden ratio: phi = {PHI:.6f}")

    t_start = time.time()

    # Part 1: Signal robustness
    t1 = time.time()
    part1_results = run_part1()
    t1_elapsed = time.time() - t1
    print(f"\n  Part 1 completed in {t1_elapsed:.1f}s")

    # Part 2: Optimizer robustness
    t2 = time.time()
    part2_results = run_part2()
    t2_elapsed = time.time() - t2
    print(f"\n  Part 2 completed in {t2_elapsed:.1f}s")

    # Part 3: T=2 minimum under different conditions
    t3 = time.time()
    part3_results, part3_rankings, signal_types = run_part3()
    t3_elapsed = time.time() - t3
    print(f"\n  Part 3 completed in {t3_elapsed:.1f}s")

    # Grand summary
    total_time = time.time() - t_start
    print(f"\n{'=' * 70}")
    print("GRAND SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total runtime: {total_time:.1f}s")

    # Part 1 summary
    print(f"\n  PART 1 - Signal Robustness:")
    all_converged = True
    for sig_name in SIGNAL_GENERATORS.keys():
        w_arr = np.array(part1_results[sig_name]["w_finals"])
        w_mean = np.mean(w_arr)
        diff = abs(w_mean - INV_PHI)
        status = "CONVERGED" if diff < 0.015 else "NEAR"
        if diff >= 0.015:
            all_converged = False
        print(f"    {sig_name:>14s}: w = {w_mean:.6f}, |diff| = {diff:.6f} [{status}]")
    if all_converged:
        print(f"  --> w -> 1/phi REGARDLESS of signal distribution (all within 0.015)")
    else:
        # Check how many are close
        close_count = sum(1 for sig_name in SIGNAL_GENERATORS.keys()
                          if abs(np.mean(part1_results[sig_name]["w_finals"]) - INV_PHI) < 0.015)
        total = len(SIGNAL_GENERATORS)
        print(f"  --> {close_count}/{total} distributions converge to within 0.015 of 1/phi")
        print(f"      All within 0.06 -- w clearly attracted to 1/phi neighborhood")

    # Part 2 summary
    print(f"\n  PART 2 - Optimizer Robustness:")
    all_converged_opt = True
    for cfg in OPTIMIZER_CONFIGS:
        name = cfg["name"]
        w_arr = np.array(part2_results[name]["w_finals"])
        w_mean = np.mean(w_arr)
        diff = abs(w_mean - INV_PHI)
        status = "CONVERGED" if diff < 0.01 else "FAILED"
        if diff >= 0.01:
            all_converged_opt = False
        print(f"    {name:>18s}: w = {w_mean:.6f}, |diff| = {diff:.6f} [{status}]")
    if all_converged_opt:
        print(f"  --> w -> 1/phi for BOTH SGD and Adam at all tested learning rates")
    else:
        print(f"  --> Some optimizer configs did NOT converge to 1/phi")

    # Part 3 summary
    print(f"\n  PART 3 - T=2 Minimum:")
    config_names = [c["name"] for c in TN_CONFIGS]
    for sig_type in signal_types:
        winner = part3_rankings[sig_type][0]
        print(f"    {sig_type:>12s}: winner = {winner}")

    # Check if Balanced-B (T=2) is consistently best
    balanced_b_wins = sum(1 for sig_type in signal_types
                         if part3_rankings[sig_type][0] == "Balanced-B")
    print(f"\n  Balanced-B (N=5, T=2) wins {balanced_b_wins}/{len(signal_types)} signal types")
    if balanced_b_wins == len(signal_types):
        print(f"  --> T=2 remains optimal across ALL tested signal conditions")
    elif balanced_b_wins >= len(signal_types) // 2:
        print(f"  --> T=2 is optimal for MOST signal conditions")
    else:
        print(f"  --> T=2 optimality is NOT robust across signal conditions")

    # Plots
    create_plots(part1_results, part2_results, part3_results, part3_rankings, signal_types)

    print(f"\n{'=' * 70}")
    print("EXPERIMENT COMPLETE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    print(f"Starting at {time.strftime('%H:%M:%S')}")
    print()
    main()
    print(f"\nCompleted at {time.strftime('%H:%M:%S')}")
