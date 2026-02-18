"""
Fair T x N Test
===============
Tests depth vs width under a FIXED compute budget (T x N = constant).

Previous binocular_sru.py showed monocular-wide (N=1, T=10) beat binocular (N=2, T=1),
but that was unfair: 10 compute units vs 2. This test matches total compute.

Question: Given a fixed compute budget, is it better to:
  - Think deeply (large T, small N = chain-of-thought)?
  - Consult diverse perspectives (small T, large N = mixture-of-experts)?

Prediction: At high contamination (alpha), diverse perspectives should become
relatively more valuable because single-viewpoint bottleneck limits deep reflection.

Architecture: N-ocular SRU with T recurrence steps per timestep.
  For each unit i, at each timestep:
    obs_i(t) = s(t) + alpha * pred_i(t-1)
    for step in range(T):
        y_i = input_i + w_self_i * h_i_prev + SUM_j(w_cross_ij * h_j_prev) + b_i
        h_i = tanh(y_i)
    pred_i(t) = w_out_i * h_i(T) + b_out_i
    pred_combined(t) = mean of pred_i(t)

BPTT through T steps with gradient flowing through both self and cross connections.

Author: Claude (fair T x N test from Ouroboros framework)
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

N_TIMESTEPS = 5000
WARMUP = 500
LR = 0.005
GRAD_CLIP = 5.0

ALPHA_VALUES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
SEEDS = [42, 137, 256]

# T x N = 10 configs
CONFIGS_10 = [
    {"name": "Deep",       "N": 1,  "T": 10},
    {"name": "Balanced-A", "N": 2,  "T": 5},
    {"name": "Balanced-B", "N": 5,  "T": 2},
    {"name": "Wide",       "N": 10, "T": 1},
]

# T x N = 20 configs
CONFIGS_20 = [
    {"name": "Deep-20",       "N": 1,  "T": 20},
    {"name": "Balanced-20A",  "N": 2,  "T": 10},
    {"name": "Balanced-20B",  "N": 4,  "T": 5},
    {"name": "Balanced-20C",  "N": 10, "T": 2},
    {"name": "Wide-20",       "N": 20, "T": 1},
]


# ==============================================================================
# Utility functions
# ==============================================================================
def set_seed(seed):
    np.random.seed(seed)


def clip_grad(g, max_norm=GRAD_CLIP):
    """Clip gradient by value."""
    return np.clip(g, -max_norm, max_norm)


def generate_signal(n_steps):
    """Generate smooth signal as sum of 3 sinusoids with incommensurate frequencies."""
    t = np.arange(n_steps, dtype=float)
    s = (0.5 * np.sin(2 * np.pi * t / 50.0)
         + 0.3 * np.sin(2 * np.pi * t / 31.0 + 0.7)
         + 0.2 * np.sin(2 * np.pi * t / 17.0 + 1.3))
    return s


def param_count(N):
    """Total parameters for N units: N^2 + 3N + 1."""
    return N * N + 3 * N + 1


# ==============================================================================
# N-ocular SRU with T recurrence steps and BPTT
# ==============================================================================
class NocularSRU_T:
    """
    N-ocular Self-Referential Unit with T recurrence steps per timestep.

    N units, each with T steps of recurrence:
      obs_i(t) = s(t) + alpha * pred_i(t-1)
      h[0] = h_from_previous_timestep
      for step in range(T):
          y_i = w_in_i * obs_i + w_self_i * h[step][i]
                + SUM_j!=i(w_cross_ij * h[step][j]) + b_i
          h[step+1][i] = tanh(y_i)
      pred_i(t) = w_out_i * h[T][i] + b_out_i

    BPTT through T steps with gradient flowing through both self and cross.
    """

    def __init__(self, N, T, seed=42):
        self.N = N
        self.T = T

        rng = np.random.RandomState(seed)

        # Per-unit parameters
        self.w_in = rng.uniform(0.5, 1.5, N)
        self.w_self = rng.uniform(0.4, 0.8, N)
        self.b = np.zeros(N)
        self.w_out = rng.uniform(-0.5, 0.5, N)
        self.b_out = np.zeros(N)

        # Cross-connection weights: w_cross[i, j] = weight from unit j to unit i
        if N > 1:
            self.w_cross = rng.uniform(-0.1, 0.1, (N, N))
            np.fill_diagonal(self.w_cross, 0.0)
        else:
            self.w_cross = np.zeros((1, 1))

        # State (persists across timesteps)
        self.h = np.zeros(N)
        self.pred = np.zeros(N)

        # Cache for backward pass
        self._obs = None
        self._h_history = None  # list of T+1 arrays, each shape (N,)

    def forward_step(self, signal_t, alpha):
        """
        One timestep: T recurrence steps, then output.
        Returns: combined prediction (mean of per-unit predictions).
        """
        N = self.N
        T = self.T

        # Each unit gets its own contaminated observation
        obs = np.empty(N)
        for i in range(N):
            obs[i] = signal_t + alpha * self.pred[i]

        self._obs = obs.copy()

        # T steps of recurrence
        h_history = [self.h.copy()]  # h_history[0] = h from previous timestep
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

        # Per-unit predictions from final hidden state
        for i in range(N):
            self.pred[i] = self.w_out[i] * self.h[i] + self.b_out[i]

        # Combined prediction
        return np.mean(self.pred)

    def backward_step(self, target):
        """
        BPTT through T recurrence steps.
        Each unit independently minimizes its OWN per-unit loss: (pred_i - target)^2.
        Returns: combined loss (for evaluation).
        """
        N = self.N
        T = self.T

        pred_combined = np.mean(self.pred)
        combined_loss = (pred_combined - target) ** 2

        # Gradient accumulators
        d_w_in = np.zeros(N)
        d_w_self = np.zeros(N)
        d_b = np.zeros(N)
        d_w_out = np.zeros(N)
        d_b_out = np.zeros(N)
        d_w_cross = np.zeros((N, N))

        # Per-unit output gradients
        # loss_i = (pred_i - target)^2
        # pred_i = w_out_i * h_final_i + b_out_i
        d_h = np.zeros(N)  # gradient w.r.t. h at current BPTT step
        for i in range(N):
            d_pred_i = 2.0 * (self.pred[i] - target)
            d_w_out[i] = d_pred_i * self._h_history[T][i]
            d_b_out[i] = d_pred_i
            d_h[i] = d_pred_i * self.w_out[i]

        # BPTT through T steps (backward from step T-1 to step 0)
        for step in range(T - 1, -1, -1):
            h_prev = self._h_history[step]      # input to this step
            h_curr = self._h_history[step + 1]  # output of this step

            # Through tanh: d_y_i = d_h_i * (1 - h_curr_i^2)
            d_y = d_h * (1.0 - h_curr ** 2)

            # Accumulate parameter gradients
            for i in range(N):
                d_w_in[i] += d_y[i] * self._obs[i]
                d_w_self[i] += d_y[i] * h_prev[i]
                d_b[i] += d_y[i]
                if N > 1:
                    for j in range(N):
                        if j != i:
                            d_w_cross[i, j] += d_y[i] * h_prev[j]

            # Propagate gradient backward through ALL connections
            d_h_new = np.zeros(N)
            for i in range(N):
                d_h_new[i] += d_y[i] * self.w_self[i]  # self-loop
                if N > 1:
                    for j in range(N):
                        if j != i:
                            # Gradient from unit i flows to unit j via w_cross[i,j]
                            d_h_new[j] += d_y[i] * self.w_cross[i, j]
            d_h = d_h_new

        # Clip and update
        self.w_in -= LR * clip_grad(d_w_in)
        self.w_self -= LR * clip_grad(d_w_self)
        self.b -= LR * clip_grad(d_b)
        self.w_out -= LR * clip_grad(d_w_out)
        self.b_out -= LR * clip_grad(d_b_out)

        if N > 1:
            self.w_cross -= LR * clip_grad(d_w_cross)
            np.fill_diagonal(self.w_cross, 0.0)

        return combined_loss

    def reset_state(self):
        """Reset hidden states and predictions."""
        self.h = np.zeros(self.N)
        self.pred = np.zeros(self.N)


# ==============================================================================
# Run a single condition
# ==============================================================================
def run_single(N, T, alpha, seed):
    """
    Run a single experiment condition.
    Returns dict with MSE, w_self, w_cross, and final weights.
    """
    set_seed(seed)
    signal = generate_signal(N_TIMESTEPS)

    model = NocularSRU_T(N=N, T=T, seed=seed)

    errors = []

    for t in range(N_TIMESTEPS):
        s_t = signal[t]

        # Forward
        pred = model.forward_step(s_t, alpha)

        # Error (for evaluation)
        err = (pred - s_t) ** 2
        if t >= WARMUP:
            errors.append(err)

        # Backward (online SGD)
        model.backward_step(s_t)

    mse = np.mean(errors)

    result = {
        'N': N,
        'T': T,
        'TxN': T * N,
        'alpha': alpha,
        'seed': seed,
        'mse': float(mse),
        'params': param_count(N),
        'w_self_mean': float(np.mean(model.w_self)),
    }

    if N > 1:
        off_diag = []
        for i in range(N):
            for j in range(N):
                if i != j:
                    off_diag.append(model.w_cross[i, j])
        result['w_cross_mean'] = float(np.mean(off_diag))
    else:
        result['w_cross_mean'] = 0.0

    return result


# ==============================================================================
# Main sweep
# ==============================================================================
def run_sweep(configs, budget_name):
    """Run all configs x alphas x seeds for a given T x N budget."""
    total = len(configs) * len(ALPHA_VALUES) * len(SEEDS)
    print(f"\n{'=' * 70}")
    print(f"T x N = {budget_name} SWEEP ({total} runs)")
    print(f"{'=' * 70}")

    results = {}  # (name, alpha, seed) -> result
    count = 0

    for cfg in configs:
        name = cfg['name']
        N = cfg['N']
        T = cfg['T']
        print(f"  Config: {name} (N={N}, T={T}, params={param_count(N)})...", end="", flush=True)
        t0 = time.time()

        for alpha in ALPHA_VALUES:
            for seed in SEEDS:
                r = run_single(N, T, alpha, seed)
                r['config_name'] = name
                results[(name, alpha, seed)] = r
                count += 1

        elapsed = time.time() - t0
        print(f" done ({elapsed:.1f}s)")

    print(f"  Sweep complete: {count} runs")
    return results


# ==============================================================================
# Analysis
# ==============================================================================
def analyze_sweep(results, configs, budget_name):
    """Analyze results for one budget level."""
    print(f"\n{'-' * 70}")
    print(f"RESULTS: T x N = {budget_name}")
    print(f"{'-' * 70}")

    config_names = [c['name'] for c in configs]

    # Table: Config vs alpha, showing mean MSE
    header = f"{'Config':>14} {'N':>3} {'T':>3} {'Params':>6}"
    for alpha in ALPHA_VALUES:
        header += f"  {'a=' + format(alpha, '.1f'):>8}"
    print(header)
    print("-" * (26 + 10 * len(ALPHA_VALUES)))

    mse_by_config_alpha = {}  # (name, alpha) -> mean_mse

    for cfg in configs:
        name = cfg['name']
        N = cfg['N']
        T = cfg['T']
        row = f"{name:>14} {N:>3} {T:>3} {param_count(N):>6}"
        for alpha in ALPHA_VALUES:
            mses = [results[(name, alpha, s)]['mse'] for s in SEEDS]
            mean_mse = np.mean(mses)
            mse_by_config_alpha[(name, alpha)] = mean_mse
            row += f"  {mean_mse:>8.6f}"
        print(row)

    # Best config per alpha
    print(f"\n  BEST CONFIG PER ALPHA (T x N = {budget_name}):")
    best_per_alpha = {}
    for alpha in ALPHA_VALUES:
        best_name = None
        best_mse = float('inf')
        for cfg in configs:
            name = cfg['name']
            mse = mse_by_config_alpha[(name, alpha)]
            if mse < best_mse:
                best_mse = mse
                best_name = name
        best_per_alpha[alpha] = best_name
        # Find the deep config for comparison
        deep_name = config_names[0]  # First config is always Deep
        deep_mse = mse_by_config_alpha[(deep_name, alpha)]
        wide_name = config_names[-1]  # Last is always Wide
        wide_mse = mse_by_config_alpha[(wide_name, alpha)]
        print(f"    alpha={alpha:.1f}: BEST = {best_name:>14} (MSE={best_mse:.6f})"
              f"  | Deep={deep_mse:.6f}, Wide={wide_mse:.6f}")

    # Deep vs Wide comparison
    print(f"\n  DEEP vs WIDE (T x N = {budget_name}):")
    deep_name = config_names[0]
    wide_name = config_names[-1]
    for alpha in ALPHA_VALUES:
        deep_mse = mse_by_config_alpha[(deep_name, alpha)]
        wide_mse = mse_by_config_alpha[(wide_name, alpha)]
        diff = deep_mse - wide_mse  # positive means wide wins
        pct = diff / deep_mse * 100 if deep_mse > 1e-12 else 0
        winner = "WIDE" if diff > 0 else "DEEP"
        print(f"    alpha={alpha:.1f}: Deep={deep_mse:.6f}, Wide={wide_mse:.6f}, "
              f"diff={diff:+.6f} ({pct:+.1f}%) -> {winner} wins")

    # w_self and w_cross
    print(f"\n  WEIGHT ANALYSIS (T x N = {budget_name}):")
    print(f"  {'Config':>14} {'N':>3} {'T':>3} {'w_self':>10} {'w_cross':>10}")
    print(f"  {'-' * 44}")
    w_self_by_config = {}
    w_cross_by_config = {}
    for cfg in configs:
        name = cfg['name']
        N = cfg['N']
        ws_all = []
        wc_all = []
        for alpha in ALPHA_VALUES:
            for seed in SEEDS:
                r = results[(name, alpha, seed)]
                ws_all.append(r['w_self_mean'])
                wc_all.append(r['w_cross_mean'])
        ws_mean = np.mean(ws_all)
        wc_mean = np.mean(wc_all)
        w_self_by_config[name] = ws_mean
        w_cross_by_config[name] = wc_mean
        print(f"  {name:>14} {N:>3} {cfg['T']:>3} {ws_mean:>10.6f} {wc_mean:>10.6f}")
    print(f"  {'1/phi ref':>14} {'':>3} {'':>3} {INV_PHI:>10.6f}")

    return mse_by_config_alpha, best_per_alpha, w_self_by_config, w_cross_by_config


def find_crossover(mse_10, mse_20, configs_10, configs_20):
    """Analyze the crossover point where wide beats deep."""
    print(f"\n{'-' * 70}")
    print("CROSSOVER ANALYSIS: Where does Wide beat Deep?")
    print(f"{'-' * 70}")

    for budget_name, mse_data, configs in [("10", mse_10, configs_10), ("20", mse_20, configs_20)]:
        deep_name = configs[0]['name']
        wide_name = configs[-1]['name']
        print(f"\n  T x N = {budget_name}: MSE(Deep) - MSE(Wide)")
        print(f"  {'alpha':>6} {'Deep MSE':>10} {'Wide MSE':>10} {'Diff':>12} {'Winner':>8}")
        print(f"  {'-' * 52}")

        crossover_found = False
        prev_diff = None
        for alpha in ALPHA_VALUES:
            deep_mse = mse_data[(deep_name, alpha)]
            wide_mse = mse_data[(wide_name, alpha)]
            diff = deep_mse - wide_mse  # positive = wide wins
            winner = "WIDE" if diff > 0 else "DEEP"
            print(f"  {alpha:>6.1f} {deep_mse:>10.6f} {wide_mse:>10.6f} {diff:>+12.6f} {winner:>8}")

            if prev_diff is not None and prev_diff <= 0 and diff > 0:
                # Linear interpolation for crossover alpha
                a_prev = ALPHA_VALUES[ALPHA_VALUES.index(alpha) - 1]
                a_cross = a_prev + (0 - prev_diff) / (diff - prev_diff) * (alpha - a_prev)
                print(f"  >>> CROSSOVER at approximately alpha = {a_cross:.3f}")
                crossover_found = True
            prev_diff = diff

        if not crossover_found:
            if prev_diff is not None and prev_diff > 0:
                print(f"  >>> Wide wins at ALL tested alphas for T x N = {budget_name}")
            elif prev_diff is not None and prev_diff <= 0:
                print(f"  >>> Deep wins at ALL tested alphas for T x N = {budget_name}")


# ==============================================================================
# Plotting
# ==============================================================================
def create_plots(results_10, results_20, configs_10, configs_20,
                 mse_10, mse_20, w_self_10, w_cross_10, w_self_20, w_cross_20):
    """Generate 3x2 results plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(3, 2, figsize=(14, 18))
    fig.suptitle("Fair T x N Test: Depth vs Width Under Fixed Compute Budget",
                 fontsize=14, fontweight='bold')

    # Color palette for alpha values
    cmap = plt.cm.viridis
    alpha_colors = {a: cmap(i / (len(ALPHA_VALUES) - 1)) for i, a in enumerate(ALPHA_VALUES)}

    # Config colors
    config_cmap = plt.cm.tab10

    # ---- Panel 1: MSE vs N for T x N = 10 ----
    ax = axes[0, 0]
    n_vals_10 = [c['N'] for c in configs_10]
    for alpha in ALPHA_VALUES:
        mses = [mse_10[(c['name'], alpha)] for c in configs_10]
        ax.plot(n_vals_10, mses, 'o-', color=alpha_colors[alpha],
                label=f'a={alpha:.1f}', linewidth=1.5, markersize=6)
    ax.set_xlabel('N (number of units)')
    ax.set_ylabel('MSE')
    ax.set_title('Panel 1: MSE vs N (T x N = 10)')
    ax.set_yscale('log')
    ax.set_xticks(n_vals_10)
    ax.set_xticklabels([f"N={c['N']}\nT={c['T']}" for c in configs_10], fontsize=8)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # ---- Panel 2: MSE vs N for T x N = 20 ----
    ax = axes[0, 1]
    n_vals_20 = [c['N'] for c in configs_20]
    for alpha in ALPHA_VALUES:
        mses = [mse_20[(c['name'], alpha)] for c in configs_20]
        ax.plot(n_vals_20, mses, 'o-', color=alpha_colors[alpha],
                label=f'a={alpha:.1f}', linewidth=1.5, markersize=6)
    ax.set_xlabel('N (number of units)')
    ax.set_ylabel('MSE')
    ax.set_title('Panel 2: MSE vs N (T x N = 20)')
    ax.set_yscale('log')
    ax.set_xticks(n_vals_20)
    ax.set_xticklabels([f"N={c['N']}\nT={c['T']}" for c in configs_20], fontsize=8)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # ---- Panel 3: Optimal config per alpha (bar chart) ----
    ax = axes[1, 0]
    # For T x N = 10, show which N minimizes MSE at each alpha
    bar_width = 0.35
    x_pos = np.arange(len(ALPHA_VALUES))

    # For budget=10
    optimal_n_10 = []
    for alpha in ALPHA_VALUES:
        best_mse = float('inf')
        best_n = 1
        for cfg in configs_10:
            mse = mse_10[(cfg['name'], alpha)]
            if mse < best_mse:
                best_mse = mse
                best_n = cfg['N']
        optimal_n_10.append(best_n)

    # For budget=20
    optimal_n_20 = []
    for alpha in ALPHA_VALUES:
        best_mse = float('inf')
        best_n = 1
        for cfg in configs_20:
            mse = mse_20[(cfg['name'], alpha)]
            if mse < best_mse:
                best_mse = mse
                best_n = cfg['N']
        optimal_n_20.append(best_n)

    ax.bar(x_pos - bar_width / 2, optimal_n_10, bar_width, label='TxN=10',
           color='#2196F3', alpha=0.7, edgecolor='black')
    ax.bar(x_pos + bar_width / 2, optimal_n_20, bar_width, label='TxN=20',
           color='#FF5722', alpha=0.7, edgecolor='black')
    ax.set_xlabel('alpha')
    ax.set_ylabel('Optimal N')
    ax.set_title('Panel 3: Optimal N per Alpha')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'{a:.1f}' for a in ALPHA_VALUES])
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    # ---- Panel 4: MSE(Deep) - MSE(Wide) vs alpha (crossover plot) ----
    ax = axes[1, 1]
    for budget_name, mse_data, configs in [("10", mse_10, configs_10), ("20", mse_20, configs_20)]:
        deep_name = configs[0]['name']
        wide_name = configs[-1]['name']
        diffs = []
        for alpha in ALPHA_VALUES:
            deep_mse = mse_data[(deep_name, alpha)]
            wide_mse = mse_data[(wide_name, alpha)]
            diffs.append(deep_mse - wide_mse)
        color = '#2196F3' if budget_name == "10" else '#FF5722'
        ax.plot(ALPHA_VALUES, diffs, 'o-', color=color,
                label=f'TxN={budget_name}', linewidth=2, markersize=6)

    ax.axhline(y=0, color='black', linewidth=1, linestyle='-')
    ax.set_xlabel('alpha (contamination strength)')
    ax.set_ylabel('MSE(Deep) - MSE(Wide)')
    ax.set_title('Panel 4: Crossover (>0 means Wide wins)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.fill_between(ALPHA_VALUES, 0, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 0.01,
                     alpha=0.05, color='green', label='_nolegend_')

    # ---- Panel 5: w_self mean vs config ----
    ax = axes[2, 0]
    names_10 = [c['name'] for c in configs_10]
    ws_vals_10 = [w_self_10[n] for n in names_10]
    names_20 = [c['name'] for c in configs_20]
    ws_vals_20 = [w_self_20[n] for n in names_20]

    x1 = np.arange(len(names_10))
    x2 = np.arange(len(names_20)) + len(names_10) + 1  # offset
    all_x = np.concatenate([x1, x2])
    all_vals = ws_vals_10 + ws_vals_20
    all_labels = names_10 + names_20
    colors_bar = ['#2196F3'] * len(names_10) + ['#FF5722'] * len(names_20)

    ax.bar(all_x, all_vals, color=colors_bar, alpha=0.7, edgecolor='black')
    ax.axhline(y=INV_PHI, color='#FF9800', linestyle='--', linewidth=2, label=f'1/phi = {INV_PHI:.3f}')
    ax.set_xlabel('Config')
    ax.set_ylabel('Mean w_self')
    ax.set_title('Panel 5: w_self vs Config')
    ax.set_xticks(all_x)
    ax.set_xticklabels(all_labels, rotation=45, ha='right', fontsize=7)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    # ---- Panel 6: w_cross mean vs config ----
    ax = axes[2, 1]
    # Only configs with N > 1
    names_10_cross = [c['name'] for c in configs_10 if c['N'] > 1]
    wc_vals_10 = [w_cross_10[n] for n in names_10_cross]
    names_20_cross = [c['name'] for c in configs_20 if c['N'] > 1]
    wc_vals_20 = [w_cross_20[n] for n in names_20_cross]

    x1 = np.arange(len(names_10_cross))
    x2 = np.arange(len(names_20_cross)) + len(names_10_cross) + 1
    all_x = np.concatenate([x1, x2])
    all_vals = wc_vals_10 + wc_vals_20
    all_labels = names_10_cross + names_20_cross
    colors_bar = ['#2196F3'] * len(names_10_cross) + ['#FF5722'] * len(names_20_cross)

    ax.bar(all_x, all_vals, color=colors_bar, alpha=0.7, edgecolor='black')
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax.set_xlabel('Config')
    ax.set_ylabel('Mean w_cross')
    ax.set_title('Panel 6: w_cross vs Config')
    ax.set_xticks(all_x)
    ax.set_xticklabels(all_labels, rotation=45, ha='right', fontsize=7)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fair_tn_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 70)
    print("FAIR T x N TEST")
    print("Depth vs Width Under Fixed Compute Budget")
    print("=" * 70)
    print(f"  Alpha values: {ALPHA_VALUES}")
    print(f"  Seeds: {SEEDS}")
    print(f"  Timesteps: {N_TIMESTEPS}, Warmup: {WARMUP}, LR: {LR}")
    print(f"  Reference: 1/phi = {INV_PHI:.6f}")

    print(f"\n  T x N = 10 configs:")
    for cfg in CONFIGS_10:
        print(f"    {cfg['name']:>14}: N={cfg['N']:>2}, T={cfg['T']:>2}, "
              f"TxN={cfg['N']*cfg['T']:>3}, params={param_count(cfg['N'])}")

    print(f"\n  T x N = 20 configs:")
    for cfg in CONFIGS_20:
        print(f"    {cfg['name']:>14}: N={cfg['N']:>2}, T={cfg['T']:>2}, "
              f"TxN={cfg['N']*cfg['T']:>3}, params={param_count(cfg['N'])}")

    t_start = time.time()

    # ---- T x N = 10 sweep ----
    results_10 = run_sweep(CONFIGS_10, "10")

    # ---- T x N = 20 sweep ----
    results_20 = run_sweep(CONFIGS_20, "20")

    # ---- Analysis ----
    mse_10, best_10, w_self_10, w_cross_10 = analyze_sweep(results_10, CONFIGS_10, "10")
    mse_20, best_20, w_self_20, w_cross_20 = analyze_sweep(results_20, CONFIGS_20, "20")

    # ---- Crossover analysis ----
    find_crossover(mse_10, mse_20, CONFIGS_10, CONFIGS_20)

    # ---- Grand summary ----
    total_time = time.time() - t_start
    print(f"\n{'=' * 70}")
    print("GRAND SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total runtime: {total_time:.1f}s")

    # Key question: depth vs width?
    print(f"\n  THE KEY QUESTION: Given fixed compute, depth or width?")
    print(f"  {'=' * 60}")

    for budget_name, mse_data, configs in [("10", mse_10, CONFIGS_10), ("20", mse_20, CONFIGS_20)]:
        deep_name = configs[0]['name']
        wide_name = configs[-1]['name']
        print(f"\n  T x N = {budget_name}:")
        deep_wins = 0
        wide_wins = 0
        balanced_wins = 0
        for alpha in ALPHA_VALUES:
            best_name = None
            best_mse = float('inf')
            for cfg in configs:
                mse = mse_data[(cfg['name'], alpha)]
                if mse < best_mse:
                    best_mse = mse
                    best_name = cfg['name']
            if best_name == deep_name:
                deep_wins += 1
            elif best_name == wide_name:
                wide_wins += 1
            else:
                balanced_wins += 1
            print(f"    alpha={alpha:.1f}: winner = {best_name}")
        print(f"    Score: Deep={deep_wins}, Balanced={balanced_wins}, Wide={wide_wins}")

    # Prediction check: does wide become relatively better at high alpha?
    print(f"\n  PREDICTION CHECK: Does width become relatively better at high alpha?")
    print(f"  {'=' * 60}")
    for budget_name, mse_data, configs in [("10", mse_10, CONFIGS_10), ("20", mse_20, CONFIGS_20)]:
        deep_name = configs[0]['name']
        wide_name = configs[-1]['name']
        diff_low = mse_data[(deep_name, 0.0)] - mse_data[(wide_name, 0.0)]
        diff_high = mse_data[(deep_name, 1.0)] - mse_data[(wide_name, 1.0)]
        # If diff increases (becomes more positive or less negative), wide improved relative to deep
        shift = diff_high - diff_low
        print(f"  T x N = {budget_name}:")
        print(f"    Diff(Deep-Wide) at alpha=0.0: {diff_low:+.6f}")
        print(f"    Diff(Deep-Wide) at alpha=1.0: {diff_high:+.6f}")
        print(f"    Shift: {shift:+.6f} ({'width gains' if shift > 0 else 'depth gains'})")
        if shift > 0:
            print(f"    PREDICTION CONFIRMED: Width becomes relatively better at high alpha")
        else:
            print(f"    PREDICTION FAILED: Depth maintains or increases advantage at high alpha")

    # Parameter count discussion
    print(f"\n  PARAMETER COUNT NOTE:")
    print(f"  {'=' * 60}")
    for cfg in CONFIGS_10 + CONFIGS_20:
        print(f"    {cfg['name']:>14}: N={cfg['N']:>2}, T={cfg['T']:>2}, params={param_count(cfg['N']):>4}")
    print(f"\n  Wide configs have MORE parameters (N^2 scaling).")
    print(f"  If Deep wins despite fewer params, depth genuinely matters.")
    print(f"  If Wide wins, could be params advantage, not just viewpoint diversity.")

    # ---- Plots ----
    create_plots(results_10, results_20, CONFIGS_10, CONFIGS_20,
                 mse_10, mse_20, w_self_10, w_cross_10, w_self_20, w_cross_20)

    print(f"\n{'=' * 70}")
    print("EXPERIMENT COMPLETE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
