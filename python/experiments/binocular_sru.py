"""
Binocular SRU Experiment
========================
Tests whether multiple self-referential units with cross-connections
exhibit a step-function improvement analogous to binocular vision.

Key insight: A single SRU is a monocular observer (2 DOF) -- it sees signal
contaminated by its own echo and can't disentangle them. Two cross-connected
SRUs form a binocular observer (5 DOF) -- each sees different contamination,
and the "parallax" (difference in contamination) reveals the true signal.

Predictions:
  1. Step function: MSE drops sharply N=1->N=2, plateaus for N>=3
  2. Cross-connections matter: binocular > independent (averaged) > monocular
  3. Viewpoint > parameters: binocular > monocular-wide (T=10)
  4. w_self near 1/phi regardless of N
  5. Binocular advantage grows with alpha (contamination strength)

Author: Claude (binocular observer experiment from Ouroboros framework)
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

N_VALUES = [1, 2, 3, 4, 6, 8]
ALPHA_VALUES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
SEEDS = [42, 137, 256]


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


# ==============================================================================
# N-ocular SRU
# ==============================================================================
class NocularSRU:
    """
    N-ocular Self-Referential Unit.

    N units, each with:
      y_i(t) = w_in_i * obs_i(t) + w_self_i * h_i(t-1) + SUM_j(w_cross_ij * h_j(t-1)) + b_i
      h_i(t) = tanh(y_i(t))
      pred_i(t) = w_out_i * h_i(t) + b_out_i

    Each unit has ITS OWN contaminated observation:
      obs_i(t) = s(t) + alpha * pred_i(t-1)

    Combined prediction: mean of pred_i(t)
    """

    def __init__(self, N, allow_cross=True, seed=42):
        """
        N: number of units
        allow_cross: if False, w_cross is forced to 0 (independent mode)
        """
        self.N = N
        self.allow_cross = allow_cross

        rng = np.random.RandomState(seed)

        # Per-unit parameters
        self.w_in = rng.uniform(0.5, 1.5, N)       # input weights
        self.w_self = rng.uniform(0.4, 0.8, N)      # self-referential weights
        self.b = np.zeros(N)                          # biases
        self.w_out = rng.uniform(-0.5, 0.5, N)      # output weights
        self.b_out = np.zeros(N)                      # output biases

        # Cross-connection weights: w_cross[i, j] = weight from unit j to unit i
        # Diagonal is 0 (that's w_self)
        if N > 1 and allow_cross:
            self.w_cross = rng.uniform(-0.1, 0.1, (N, N))
            np.fill_diagonal(self.w_cross, 0.0)
        else:
            self.w_cross = np.zeros((N, N))

        # State
        self.h = np.zeros(N)          # hidden state
        self.pred = np.zeros(N)       # per-unit predictions

        # Cache for backward pass
        self._obs = None
        self._y = None
        self._h_prev = None
        self._h_new = None

    def forward_step(self, signal_t, alpha):
        """
        One timestep of online processing.

        signal_t: true signal value at time t
        alpha: contamination strength

        Returns: combined prediction
        """
        N = self.N

        # Each unit gets its own contaminated observation
        obs = np.zeros(N)
        for i in range(N):
            obs[i] = signal_t + alpha * self.pred[i]

        # Save for backward
        self._obs = obs.copy()
        self._h_prev = self.h.copy()

        # Forward: compute new hidden states
        y = np.zeros(N)
        for i in range(N):
            y[i] = self.w_in[i] * obs[i] + self.w_self[i] * self.h[i] + self.b[i]
            if self.allow_cross and N > 1:
                for j in range(N):
                    if j != i:
                        y[i] += self.w_cross[i, j] * self.h[j]

        h_new = np.tanh(y)

        self._y = y.copy()
        self._h_new = h_new.copy()

        # Update state
        self.h = h_new

        # Per-unit predictions
        for i in range(N):
            self.pred[i] = self.w_out[i] * self.h[i] + self.b_out[i]

        # Combined prediction
        pred_combined = np.mean(self.pred)
        return pred_combined

    def backward_step(self, target):
        """
        Compute gradients for one timestep and update weights.

        Each unit independently minimizes its OWN per-unit loss:
          loss_i = (pred_i - target)^2

        This gives each unit the full gradient signal regardless of N.
        The combined prediction (mean) is only used for evaluation.

        Cross-connections let units share hidden state information, but
        each unit's learning is driven by its own prediction error.

        target: true signal value s(t)
        Returns: combined loss (for evaluation)
        """
        N = self.N
        pred_combined = np.mean(self.pred)
        combined_loss = (pred_combined - target) ** 2

        # Per-unit gradients
        d_w_in = np.zeros(N)
        d_w_self = np.zeros(N)
        d_b = np.zeros(N)
        d_w_out = np.zeros(N)
        d_b_out = np.zeros(N)
        d_w_cross = np.zeros((N, N))

        for i in range(N):
            # Per-unit loss: (pred_i - target)^2
            d_pred_i = 2.0 * (self.pred[i] - target)

            # pred_i = w_out_i * h_i + b_out_i
            d_w_out[i] = d_pred_i * self._h_new[i]
            d_b_out[i] = d_pred_i

            # d_h_i from output
            d_h_i = d_pred_i * self.w_out[i]

            # Through tanh: d_y_i = d_h_i * (1 - h_i^2)
            d_y_i = d_h_i * (1.0 - self._h_new[i] ** 2)

            # Gradients of y_i w.r.t. parameters
            d_w_in[i] = d_y_i * self._obs[i]
            d_w_self[i] = d_y_i * self._h_prev[i]
            d_b[i] = d_y_i

            # Cross-connection gradients
            if self.allow_cross and N > 1:
                for j in range(N):
                    if j != i:
                        d_w_cross[i, j] = d_y_i * self._h_prev[j]

        # Clip and update
        self.w_in -= LR * clip_grad(d_w_in)
        self.w_self -= LR * clip_grad(d_w_self)
        self.b -= LR * clip_grad(d_b)
        self.w_out -= LR * clip_grad(d_w_out)
        self.b_out -= LR * clip_grad(d_b_out)

        if self.allow_cross and N > 1:
            self.w_cross -= LR * clip_grad(d_w_cross)
            np.fill_diagonal(self.w_cross, 0.0)  # enforce no self-loop via cross

        return combined_loss

    def reset_state(self):
        """Reset hidden states and predictions."""
        self.h = np.zeros(self.N)
        self.pred = np.zeros(self.N)


class MonocularWideSRU:
    """
    Monocular SRU with T=10 internal recurrence steps.
    1 unit, but runs T steps of recurrence per timestep.
    Tests whether more compute (vs more viewpoints) helps.
    """

    def __init__(self, T=10, seed=42):
        self.T = T

        rng = np.random.RandomState(seed)
        self.w_in = rng.uniform(0.5, 1.5)
        self.w_self = rng.uniform(0.4, 0.8)
        self.b = 0.0
        self.w_out = rng.uniform(-0.5, 0.5)
        self.b_out = 0.0

        # State
        self.h = 0.0
        self.pred_val = 0.0

        # Cache for backward
        self._obs = None
        self._h_history = None  # T+1 entries

    def forward_step(self, signal_t, alpha):
        """One timestep with T internal recurrence steps."""
        obs = signal_t + alpha * self.pred_val
        self._obs = obs

        # T steps of recurrence
        h_history = [self.h]
        h_cur = self.h
        for _ in range(self.T):
            y = self.w_in * obs + self.w_self * h_cur + self.b
            h_cur = np.tanh(y)
            h_history.append(h_cur)

        self._h_history = h_history
        self.h = h_cur
        self.pred_val = self.w_out * self.h + self.b_out
        return self.pred_val

    def backward_step(self, target):
        """BPTT through T recurrence steps."""
        loss = (self.pred_val - target) ** 2
        d_pred = 2.0 * (self.pred_val - target)

        d_w_out = d_pred * self.h
        d_b_out = d_pred
        d_h = d_pred * self.w_out

        # BPTT through T steps
        d_w_in = 0.0
        d_w_self = 0.0
        d_b_val = 0.0

        for t in range(self.T - 1, -1, -1):
            h_next = self._h_history[t + 1]
            h_cur = self._h_history[t]
            d_y = d_h * (1.0 - h_next ** 2)
            d_w_in += d_y * self._obs
            d_w_self += d_y * h_cur
            d_b_val += d_y
            d_h = d_y * self.w_self  # propagate back

        # Clip and update
        self.w_in -= LR * float(np.clip(d_w_in, -GRAD_CLIP, GRAD_CLIP))
        self.w_self -= LR * float(np.clip(d_w_self, -GRAD_CLIP, GRAD_CLIP))
        self.b -= LR * float(np.clip(d_b_val, -GRAD_CLIP, GRAD_CLIP))
        self.w_out -= LR * float(np.clip(d_w_out, -GRAD_CLIP, GRAD_CLIP))
        self.b_out -= LR * float(np.clip(d_b_out, -GRAD_CLIP, GRAD_CLIP))

        return loss

    def reset_state(self):
        self.h = 0.0
        self.pred_val = 0.0


# ==============================================================================
# Run a single condition
# ==============================================================================
def run_single(N, alpha, seed, allow_cross=True, use_wide=False, T_wide=10):
    """
    Run a single experiment condition.

    Returns dict with MSE, w_self, w_cross, and trajectories.
    """
    set_seed(seed)
    signal = generate_signal(N_TIMESTEPS)

    if use_wide:
        model = MonocularWideSRU(T=T_wide, seed=seed)
    else:
        model = NocularSRU(N=N, allow_cross=allow_cross, seed=seed)

    errors = []
    w_self_traj = []
    w_cross_traj = []

    for t in range(N_TIMESTEPS):
        s_t = signal[t]

        # Forward
        pred = model.forward_step(s_t, alpha)

        # Error
        err = (pred - s_t) ** 2
        if t >= WARMUP:
            errors.append(err)

        # Backward (online SGD)
        model.backward_step(s_t)

        # Record trajectories every 50 steps
        if t % 50 == 0:
            if use_wide:
                w_self_traj.append(model.w_self)
            else:
                w_self_traj.append(model.w_self.copy())
                if N > 1 and allow_cross:
                    # Collect off-diagonal cross weights
                    cross_vals = []
                    for i in range(N):
                        for j in range(N):
                            if i != j:
                                cross_vals.append(model.w_cross[i, j])
                    w_cross_traj.append(np.array(cross_vals))

    mse = np.mean(errors)

    result = {
        'N': N,
        'alpha': alpha,
        'seed': seed,
        'mse': float(mse),
        'allow_cross': allow_cross,
        'use_wide': use_wide,
        'w_self_traj': w_self_traj,
        'w_cross_traj': w_cross_traj,
    }

    if use_wide:
        result['w_self_final'] = float(model.w_self)
        result['w_self_mean'] = float(model.w_self)
        result['w_cross_mean'] = 0.0
    else:
        result['w_self_final'] = model.w_self.copy()
        result['w_self_mean'] = float(np.mean(model.w_self))
        if N > 1 and allow_cross:
            off_diag = []
            for i in range(N):
                for j in range(N):
                    if i != j:
                        off_diag.append(model.w_cross[i, j])
            result['w_cross_mean'] = float(np.mean(off_diag))
            result['w_cross_final'] = model.w_cross.copy()
        else:
            result['w_cross_mean'] = 0.0
            result['w_cross_final'] = None

    return result


# ==============================================================================
# Main sweep
# ==============================================================================
def run_n_sweep():
    """Run the N sweep: N in {1,2,3,4,6,8} x alpha x seeds."""
    print("\n" + "=" * 70)
    print("N SWEEP: MSE vs Number of Units")
    print("=" * 70)

    results = {}  # (N, alpha, seed) -> result
    total = len(N_VALUES) * len(ALPHA_VALUES) * len(SEEDS)
    count = 0

    for N in N_VALUES:
        for alpha in ALPHA_VALUES:
            for seed in SEEDS:
                r = run_single(N, alpha, seed, allow_cross=True)
                results[(N, alpha, seed)] = r
                count += 1
                if count % 18 == 0:
                    print(f"  Progress: {count}/{total} runs completed...")

    print(f"  N sweep complete: {count} runs")
    return results


def run_controls():
    """Run the control conditions at each alpha."""
    print("\n" + "=" * 70)
    print("CONTROLS: Monocular vs Binocular vs Independent vs Wide")
    print("=" * 70)

    controls = {}  # (variant, alpha, seed) -> result
    count = 0

    for alpha in ALPHA_VALUES:
        for seed in SEEDS:
            # Monocular (N=1)
            r_mono = run_single(1, alpha, seed, allow_cross=True)
            controls[('monocular', alpha, seed)] = r_mono

            # Binocular (N=2, cross)
            r_bino = run_single(2, alpha, seed, allow_cross=True)
            controls[('binocular', alpha, seed)] = r_bino

            # Independent (N=2, no cross)
            r_indep = run_single(2, alpha, seed, allow_cross=False)
            controls[('independent', alpha, seed)] = r_indep

            # Monocular-wide (N=1, T=10)
            r_wide = run_single(1, alpha, seed, allow_cross=True, use_wide=True, T_wide=10)
            controls[('monocular-wide', alpha, seed)] = r_wide

            count += 4

    print(f"  Controls complete: {count} runs")
    return controls


# ==============================================================================
# Analysis
# ==============================================================================
def analyze_n_sweep(results):
    """Analyze N sweep results."""
    print("\n" + "-" * 70)
    print("N SWEEP RESULTS")
    print("-" * 70)

    # Table: N vs alpha, showing mean MSE
    header = f"{'N':>4}"
    for alpha in ALPHA_VALUES:
        header += f"  {'a='+format(alpha,'.1f'):>8}"
    print(header)
    print("-" * (4 + 10 * len(ALPHA_VALUES)))

    mse_by_n_alpha = {}  # (N, alpha) -> [mse values across seeds]

    for N in N_VALUES:
        row = f"{N:>4}"
        for alpha in ALPHA_VALUES:
            mses = [results[(N, alpha, s)]['mse'] for s in SEEDS]
            mean_mse = np.mean(mses)
            mse_by_n_alpha[(N, alpha)] = mses
            row += f"  {mean_mse:>8.6f}"
        print(row)

    # Performance gain table: MSE(N=1)/MSE(N)
    print("\n" + "-" * 70)
    print("PERFORMANCE GAIN: MSE(N=1) / MSE(N)")
    print("-" * 70)
    header = f"{'N':>4}"
    for alpha in ALPHA_VALUES:
        header += f"  {'a='+format(alpha,'.1f'):>8}"
    print(header)
    print("-" * (4 + 10 * len(ALPHA_VALUES)))

    for N in N_VALUES:
        row = f"{N:>4}"
        for alpha in ALPHA_VALUES:
            mse_1 = np.mean(mse_by_n_alpha[(1, alpha)])
            mse_n = np.mean(mse_by_n_alpha[(N, alpha)])
            if mse_n > 1e-12:
                gain = mse_1 / mse_n
            else:
                gain = float('inf')
            row += f"  {gain:>8.3f}"
        print(row)

    # The key gain ratio at N=2
    print("\n  KEY GAIN RATIOS (MSE(1)/MSE(2)):")
    for alpha in ALPHA_VALUES:
        mse_1 = np.mean(mse_by_n_alpha[(1, alpha)])
        mse_2 = np.mean(mse_by_n_alpha[(2, alpha)])
        gain = mse_1 / mse_2 if mse_2 > 1e-12 else float('inf')
        print(f"    alpha={alpha:.1f}: gain = {gain:.4f}")

    # w_self table
    print("\n" + "-" * 70)
    print("w_self MEAN vs N (averaged across alpha and seeds)")
    print("-" * 70)
    print(f"{'N':>4} {'w_self mean':>12} {'w_self std':>11} {'dist(1/phi)':>12}")
    print("-" * 45)
    for N in N_VALUES:
        all_w = []
        for alpha in ALPHA_VALUES:
            for s in SEEDS:
                r = results[(N, alpha, s)]
                if isinstance(r['w_self_final'], np.ndarray):
                    all_w.extend(r['w_self_final'].tolist())
                else:
                    all_w.append(r['w_self_final'])
        w_mean = np.mean(all_w)
        w_std = np.std(all_w)
        print(f"{N:>4} {w_mean:>12.6f} {w_std:>11.6f} {abs(w_mean - INV_PHI):>12.6f}")

    # w_cross table
    print("\n" + "-" * 70)
    print("w_cross MEAN vs N (averaged across alpha and seeds)")
    print("-" * 70)
    print(f"{'N':>4} {'w_cross mean':>13} {'w_cross std':>12}")
    print("-" * 35)
    for N in N_VALUES:
        if N == 1:
            print(f"{N:>4} {'N/A':>13} {'N/A':>12}")
            continue
        all_wc = []
        for alpha in ALPHA_VALUES:
            for s in SEEDS:
                r = results[(N, alpha, s)]
                wc = r['w_cross_mean']
                all_wc.append(wc)
        wc_mean = np.mean(all_wc)
        wc_std = np.std(all_wc)
        print(f"{N:>4} {wc_mean:>13.6f} {wc_std:>12.6f}")

    return mse_by_n_alpha


def analyze_controls(controls):
    """Analyze control conditions."""
    print("\n" + "-" * 70)
    print("CONTROL COMPARISON: Monocular vs Binocular vs Independent vs Wide")
    print("-" * 70)

    variants = ['monocular', 'binocular', 'independent', 'monocular-wide']
    header = f"{'alpha':>6}"
    for v in variants:
        header += f"  {v:>14}"
    print(header)
    print("-" * (6 + 16 * len(variants)))

    control_mses = {}  # (variant, alpha) -> mean_mse

    for alpha in ALPHA_VALUES:
        row = f"{alpha:>6.1f}"
        for v in variants:
            mses = [controls[(v, alpha, s)]['mse'] for s in SEEDS]
            mean_mse = np.mean(mses)
            control_mses[(v, alpha)] = mean_mse
            row += f"  {mean_mse:>14.6f}"
        print(row)

    # Analysis
    print("\n  COMPARISON ANALYSIS:")
    print("  " + "-" * 60)

    bino_beats_mono = 0
    bino_beats_indep = 0
    bino_beats_wide = 0
    indep_beats_mono = 0

    for alpha in ALPHA_VALUES:
        mono = control_mses[('monocular', alpha)]
        bino = control_mses[('binocular', alpha)]
        indep = control_mses[('independent', alpha)]
        wide = control_mses[('monocular-wide', alpha)]

        if bino < mono:
            bino_beats_mono += 1
        if bino < indep:
            bino_beats_indep += 1
        if bino < wide:
            bino_beats_wide += 1
        if indep < mono:
            indep_beats_mono += 1

    n_alpha = len(ALPHA_VALUES)
    print(f"  Binocular beats monocular:     {bino_beats_mono}/{n_alpha}")
    print(f"  Binocular beats independent:   {bino_beats_indep}/{n_alpha}")
    print(f"  Binocular beats monocular-wide:{bino_beats_wide}/{n_alpha}")
    print(f"  Independent beats monocular:   {indep_beats_mono}/{n_alpha}")

    # Binocular advantage percentage
    print("\n  BINOCULAR ADVANTAGE (% improvement over monocular):")
    for alpha in ALPHA_VALUES:
        mono = control_mses[('monocular', alpha)]
        bino = control_mses[('binocular', alpha)]
        if mono > 1e-12:
            adv = (mono - bino) / mono * 100
        else:
            adv = 0.0
        print(f"    alpha={alpha:.1f}: {adv:>7.2f}%")

    return control_mses


# ==============================================================================
# Plotting
# ==============================================================================
def create_plots(n_sweep_results, controls, mse_by_n_alpha, control_mses):
    """Generate 4x2 results plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(4, 2, figsize=(14, 22))
    fig.suptitle("Binocular SRU Experiment: Observer DOF Step Function",
                 fontsize=14, fontweight='bold')

    # Color palette
    cmap = plt.cm.viridis
    alpha_colors = {a: cmap(i / (len(ALPHA_VALUES) - 1)) for i, a in enumerate(ALPHA_VALUES)}
    c_mono = '#FF5722'
    c_bino = '#2196F3'
    c_indep = '#4CAF50'
    c_wide = '#9C27B0'
    c_phi = '#FF9800'

    # ---- Panel 1: MSE vs N (THE STEP FUNCTION PLOT) ----
    ax = axes[0, 0]
    for alpha in ALPHA_VALUES:
        mses = [np.mean(mse_by_n_alpha[(N, alpha)]) for N in N_VALUES]
        ax.plot(N_VALUES, mses, 'o-', color=alpha_colors[alpha],
                label=f'a={alpha:.1f}', linewidth=1.5, markersize=5)
    ax.set_xlabel('N (number of units)')
    ax.set_ylabel('MSE (log scale)')
    ax.set_title('Panel 1: MSE vs N -- Step Function Test')
    ax.set_yscale('log')
    ax.set_xticks(N_VALUES)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.axvline(x=2, color='gray', linestyle=':', alpha=0.5, linewidth=1)

    # ---- Panel 2: Performance gain MSE(1)/MSE(N) vs N ----
    ax = axes[0, 1]
    for alpha in ALPHA_VALUES:
        mse_1 = np.mean(mse_by_n_alpha[(1, alpha)])
        gains = []
        for N in N_VALUES:
            mse_n = np.mean(mse_by_n_alpha[(N, alpha)])
            gains.append(mse_1 / mse_n if mse_n > 1e-12 else 1.0)
        ax.plot(N_VALUES, gains, 'o-', color=alpha_colors[alpha],
                label=f'a={alpha:.1f}', linewidth=1.5, markersize=5)
    ax.axhline(y=5/2, color='gray', linestyle='--', alpha=0.5, label='5/2 = 2.5')
    ax.set_xlabel('N (number of units)')
    ax.set_ylabel('Performance Gain MSE(1)/MSE(N)')
    ax.set_title('Panel 2: Gain Saturation Test')
    ax.set_xticks(N_VALUES)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.axvline(x=2, color='gray', linestyle=':', alpha=0.5, linewidth=1)

    # ---- Panel 3: MSE vs alpha: controls comparison ----
    ax = axes[1, 0]
    alphas = np.array(ALPHA_VALUES)
    variants = [('monocular', c_mono, 'o-'), ('binocular', c_bino, 's-'),
                ('independent', c_indep, '^-'), ('monocular-wide', c_wide, 'D-')]
    for vname, color, marker in variants:
        mses = [control_mses[(vname, a)] for a in ALPHA_VALUES]
        ax.plot(alphas, mses, marker, color=color, label=vname, linewidth=2, markersize=6)
    ax.set_xlabel('alpha (contamination strength)')
    ax.set_ylabel('MSE')
    ax.set_title('Panel 3: Control Comparison')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- Panel 4: w_self mean vs N ----
    ax = axes[1, 1]
    for alpha in [0.0, 0.4, 0.8]:
        w_means = []
        w_stds = []
        for N in N_VALUES:
            ws = []
            for s in SEEDS:
                r = n_sweep_results[(N, alpha, s)]
                if isinstance(r['w_self_final'], np.ndarray):
                    ws.extend(r['w_self_final'].tolist())
                else:
                    ws.append(r['w_self_final'])
            w_means.append(np.mean(ws))
            w_stds.append(np.std(ws))
        ax.errorbar(N_VALUES, w_means, yerr=w_stds, fmt='o-',
                    color=alpha_colors[alpha], label=f'a={alpha:.1f}',
                    linewidth=1.5, capsize=3)
    ax.axhline(y=INV_PHI, color=c_phi, linestyle='--', linewidth=2, label=f'1/phi = {INV_PHI:.3f}')
    ax.set_xlabel('N (number of units)')
    ax.set_ylabel('Mean w_self')
    ax.set_title('Panel 4: w_self vs N')
    ax.set_xticks(N_VALUES)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- Panel 5: w_cross mean vs N ----
    ax = axes[2, 0]
    for alpha in [0.0, 0.4, 0.8]:
        wc_means = []
        wc_stds = []
        ns_plot = [N for N in N_VALUES if N > 1]
        for N in ns_plot:
            wcs = []
            for s in SEEDS:
                r = n_sweep_results[(N, alpha, s)]
                wcs.append(r['w_cross_mean'])
            wc_means.append(np.mean(wcs))
            wc_stds.append(np.std(wcs))
        ax.errorbar(ns_plot, wc_means, yerr=wc_stds, fmt='o-',
                    color=alpha_colors[alpha], label=f'a={alpha:.1f}',
                    linewidth=1.5, capsize=3)
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax.set_xlabel('N (number of units)')
    ax.set_ylabel('Mean w_cross')
    ax.set_title('Panel 5: Cross-Connection Weights vs N')
    ax.set_xticks([N for N in N_VALUES if N > 1])
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- Panel 6: Binocular advantage vs alpha ----
    ax = axes[2, 1]
    advantages = []
    for alpha in ALPHA_VALUES:
        mono = control_mses[('monocular', alpha)]
        bino = control_mses[('binocular', alpha)]
        if mono > 1e-12:
            adv = (mono - bino) / mono * 100
        else:
            adv = 0.0
        advantages.append(adv)

    colors_bar = [c_bino if a > 0 else 'gray' for a in advantages]
    ax.bar(alphas, advantages, width=0.12, color=colors_bar, alpha=0.7, edgecolor='black')
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_xlabel('alpha (contamination strength)')
    ax.set_ylabel('Binocular Advantage (%)')
    ax.set_title('Panel 6: Binocular Advantage vs Alpha')
    ax.grid(True, alpha=0.3, axis='y')

    # ---- Panel 7: w_self + w_cross histogram for binocular ----
    ax = axes[3, 0]
    all_w_self_bino = []
    all_w_cross_bino = []
    all_w_sum_bino = []
    for alpha in ALPHA_VALUES:
        for s in SEEDS:
            r = n_sweep_results[(2, alpha, s)]
            if isinstance(r['w_self_final'], np.ndarray):
                for w in r['w_self_final']:
                    all_w_self_bino.append(w)
            if r['w_cross_final'] is not None:
                for i in range(2):
                    for j in range(2):
                        if i != j:
                            all_w_cross_bino.append(r['w_cross_final'][i, j])
                # w_self + sum(w_cross) for each unit
                for i in range(2):
                    w_sum = r['w_self_final'][i]
                    for j in range(2):
                        if i != j:
                            w_sum += r['w_cross_final'][i, j]
                    all_w_sum_bino.append(w_sum)

    bins = 30
    ax.hist(all_w_self_bino, bins=bins, alpha=0.6, color=c_bino, label='w_self', density=True)
    ax.hist(all_w_cross_bino, bins=bins, alpha=0.6, color=c_indep, label='w_cross', density=True)
    ax.hist(all_w_sum_bino, bins=bins, alpha=0.6, color=c_wide, label='w_self + w_cross', density=True)
    ax.axvline(x=INV_PHI, color=c_phi, linestyle='--', linewidth=2, label=f'1/phi = {INV_PHI:.3f}')
    ax.set_xlabel('Weight value')
    ax.set_ylabel('Density')
    ax.set_title('Panel 7: Weight Distribution (Binocular, all alpha)')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ---- Panel 8: Convergence trajectories for binocular at alpha=0.6 ----
    ax = axes[3, 1]
    target_alpha = 0.6
    for s in SEEDS:
        r = n_sweep_results[(2, target_alpha, s)]
        traj = r['w_self_traj']
        if len(traj) > 0:
            # traj is list of arrays
            traj_arr = np.array(traj)  # (n_records, N)
            t_axis = np.arange(len(traj_arr)) * 50
            for i in range(traj_arr.shape[1]):
                ax.plot(t_axis, traj_arr[:, i], color=c_bino, alpha=0.5, linewidth=1,
                        label='w_self' if (s == SEEDS[0] and i == 0) else None)

        ctraj = r['w_cross_traj']
        if len(ctraj) > 0:
            ctraj_arr = np.array(ctraj)  # (n_records, N*(N-1))
            t_axis = np.arange(len(ctraj_arr)) * 50
            for i in range(ctraj_arr.shape[1]):
                ax.plot(t_axis, ctraj_arr[:, i], color=c_indep, alpha=0.5, linewidth=1,
                        linestyle='--',
                        label='w_cross' if (s == SEEDS[0] and i == 0) else None)

    ax.axhline(y=INV_PHI, color=c_phi, linestyle='--', linewidth=2, label=f'1/phi = {INV_PHI:.3f}')
    ax.set_xlabel('Timestep')
    ax.set_ylabel('Weight value')
    ax.set_title(f'Panel 8: Weight Trajectories (N=2, alpha={target_alpha})')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "binocular_sru_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 70)
    print("BINOCULAR SRU EXPERIMENT")
    print("Observer DOF Step Function Test")
    print("=" * 70)
    print(f"  N values: {N_VALUES}")
    print(f"  Alpha values: {ALPHA_VALUES}")
    print(f"  Seeds: {SEEDS}")
    print(f"  Timesteps: {N_TIMESTEPS}, Warmup: {WARMUP}, LR: {LR}")
    print(f"  Reference: 1/phi = {INV_PHI:.6f}")

    t_start = time.time()

    # ---- N Sweep ----
    t0 = time.time()
    n_sweep_results = run_n_sweep()
    print(f"  N sweep completed in {time.time() - t0:.1f}s")

    # ---- Controls ----
    t0 = time.time()
    controls = run_controls()
    print(f"  Controls completed in {time.time() - t0:.1f}s")

    # ---- Analysis ----
    mse_by_n_alpha = analyze_n_sweep(n_sweep_results)
    control_mses = analyze_controls(controls)

    # ---- Summary ----
    total_time = time.time() - t_start
    print("\n" + "=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)
    print(f"  Total runtime: {total_time:.1f}s")

    # Key prediction checks
    print("\n  KEY PREDICTION CHECKS:")
    print("  " + "-" * 60)

    # 1. Step function: MSE(N=1) >> MSE(N=2) ~ MSE(N=3+)
    print("\n  1. STEP FUNCTION (MSE drop N=1 -> N=2 vs N=2 -> N=3):")
    for alpha in [0.0, 0.4, 0.8]:
        mse_1 = np.mean(mse_by_n_alpha[(1, alpha)])
        mse_2 = np.mean(mse_by_n_alpha[(2, alpha)])
        mse_3 = np.mean(mse_by_n_alpha[(3, alpha)])
        drop_12 = (mse_1 - mse_2) / mse_1 * 100 if mse_1 > 1e-12 else 0
        drop_23 = (mse_2 - mse_3) / mse_2 * 100 if mse_2 > 1e-12 else 0
        is_step = drop_12 > 2 * drop_23  # N=1->2 drop should be much larger
        print(f"    alpha={alpha:.1f}: drop(1->2)={drop_12:.1f}%, drop(2->3)={drop_23:.1f}% "
              f"{'[STEP]' if is_step else '[gradual]'}")

    # 2. Cross-connections matter
    print("\n  2. CROSS-CONNECTIONS MATTER (binocular vs independent):")
    for alpha in ALPHA_VALUES:
        bino = control_mses[('binocular', alpha)]
        indep = control_mses[('independent', alpha)]
        diff_pct = (indep - bino) / indep * 100 if indep > 1e-12 else 0
        print(f"    alpha={alpha:.1f}: bino={bino:.6f}, indep={indep:.6f}, "
              f"cross advantage={diff_pct:.1f}% {'[YES]' if bino < indep else '[NO]'}")

    # 3. Viewpoint > parameters
    print("\n  3. VIEWPOINT > PARAMETERS (binocular vs monocular-wide):")
    for alpha in ALPHA_VALUES:
        bino = control_mses[('binocular', alpha)]
        wide = control_mses[('monocular-wide', alpha)]
        diff_pct = (wide - bino) / wide * 100 if wide > 1e-12 else 0
        print(f"    alpha={alpha:.1f}: bino={bino:.6f}, wide={wide:.6f}, "
              f"viewpoint advantage={diff_pct:.1f}% {'[YES]' if bino < wide else '[NO]'}")

    # 4. Gain ratio at N=2
    print("\n  4. GAIN RATIO MSE(1)/MSE(2):")
    gains = []
    for alpha in ALPHA_VALUES:
        mse_1 = np.mean(mse_by_n_alpha[(1, alpha)])
        mse_2 = np.mean(mse_by_n_alpha[(2, alpha)])
        gain = mse_1 / mse_2 if mse_2 > 1e-12 else 1.0
        gains.append(gain)
        print(f"    alpha={alpha:.1f}: gain = {gain:.4f}")
    mean_gain = np.mean(gains)
    print(f"    MEAN gain = {mean_gain:.4f}")
    print(f"    5/2 = {5/2:.4f}, phi = {PHI:.4f}, 1/phi = {INV_PHI:.4f}")

    # 5. w_self convergence
    print("\n  5. w_self CONVERGENCE:")
    all_w = []
    for N in N_VALUES:
        ws = []
        for alpha in ALPHA_VALUES:
            for s in SEEDS:
                r = n_sweep_results[(N, alpha, s)]
                if isinstance(r['w_self_final'], np.ndarray):
                    ws.extend(r['w_self_final'].tolist())
                else:
                    ws.append(r['w_self_final'])
        w_mean = np.mean(ws)
        all_w.extend(ws)
        print(f"    N={N}: w_self mean = {w_mean:.6f}, dist(1/phi) = {abs(w_mean - INV_PHI):.6f}")
    grand_mean = np.mean(all_w)
    print(f"    Grand mean: {grand_mean:.6f}, dist(1/phi) = {abs(grand_mean - INV_PHI):.6f}")

    # 6. Binocular advantage grows with alpha
    print("\n  6. BINOCULAR ADVANTAGE vs ALPHA:")
    advantages = []
    for alpha in ALPHA_VALUES:
        mono = control_mses[('monocular', alpha)]
        bino = control_mses[('binocular', alpha)]
        adv = (mono - bino) / mono * 100 if mono > 1e-12 else 0
        advantages.append(adv)
    # Check if advantage generally increases with alpha
    # Simple: is the advantage at alpha=1.0 > advantage at alpha=0.0?
    grows = advantages[-1] > advantages[0]
    print(f"    alpha=0.0: {advantages[0]:.2f}%")
    print(f"    alpha=1.0: {advantages[-1]:.2f}%")
    print(f"    Grows with alpha: {'YES' if grows else 'NO'}")

    # ---- Pass/Fail Summary ----
    print("\n" + "=" * 70)
    print("PASS/FAIL SUMMARY")
    print("=" * 70)

    # Step function check (averaged over alpha)
    step_count = 0
    for alpha in ALPHA_VALUES:
        mse_1 = np.mean(mse_by_n_alpha[(1, alpha)])
        mse_2 = np.mean(mse_by_n_alpha[(2, alpha)])
        mse_3 = np.mean(mse_by_n_alpha[(3, alpha)])
        drop_12 = (mse_1 - mse_2) / mse_1 * 100 if mse_1 > 1e-12 else 0
        drop_23 = (mse_2 - mse_3) / mse_2 * 100 if mse_2 > 1e-12 else 0
        if drop_12 > 2 * drop_23 and drop_12 > 5:
            step_count += 1

    bino_wins = sum(1 for a in ALPHA_VALUES if control_mses[('binocular', a)] < control_mses[('independent', a)])
    view_wins = sum(1 for a in ALPHA_VALUES if control_mses[('binocular', a)] < control_mses[('monocular-wide', a)])
    w_near_phi = abs(grand_mean - INV_PHI) < 0.15

    print(f"  [{'PASS' if step_count >= 3 else 'FAIL'}] Step function in MSE at N=2: {step_count}/{len(ALPHA_VALUES)} alphas show step")
    print(f"  [{'PASS' if bino_wins >= 3 else 'FAIL'}] Cross-connections matter: binocular wins {bino_wins}/{len(ALPHA_VALUES)}")
    print(f"  [{'PASS' if view_wins >= 3 else 'FAIL'}] Viewpoint > parameters: binocular beats wide {view_wins}/{len(ALPHA_VALUES)}")
    print(f"  [{'PASS' if w_near_phi else 'FAIL'}] w_self near 1/phi: grand mean = {grand_mean:.6f}, dist = {abs(grand_mean - INV_PHI):.6f}")
    print(f"  [{'PASS' if grows else 'FAIL'}] Binocular advantage grows with alpha")

    # ---- Plots ----
    create_plots(n_sweep_results, controls, mse_by_n_alpha, control_mses)

    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
