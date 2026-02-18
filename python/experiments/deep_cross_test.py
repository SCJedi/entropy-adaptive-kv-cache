"""
Deep Cross-Connection Test
==========================
Tests whether the negative w_cross pattern holds in multi-layer networks.

Background:
  In single-layer binocular SRU experiments, cross-connection weights consistently
  converge to NEGATIVE values (w_cross ~ -0.26). This implements "parallax
  decontamination": units subtract each other's contamination.

  Question: does this pattern emerge in deeper (multi-layer) architectures too?

Architecture: Multi-Layer Cross-Connected Network
  Layer 1: N units, each with w_self_1 and w_cross_1 connections
           h_i_1 = tanh(input_i + w_self_1 * h_i_1(t-1) + w_cross_1 * mean(h_j_1(t-1) for j!=i))
  Layer 2: N units, each with w_self_2 and w_cross_2 connections
           h_i_2 = tanh(h_i_1 + w_self_2 * h_i_2(t-1) + w_cross_2 * mean(h_j_1 for j!=i))
  [Optional Layer 3 for depth=3]
  Output: mean of all units' final layer hidden states -> linear -> prediction

Test configurations:
  1. 1 layer (baseline, should reproduce w_cross ~ -0.26)
  2. 2 layers -- do both layers learn negative w_cross?
  3. 3 layers -- does the pattern persist with more depth?
  4. 2 layers, cross only at layer 1 -- does decontamination need to happen early?
  5. 2 layers, cross only at layer 2 -- or late?

Author: Claude (deep cross-connection test from Ouroboros framework)
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

N_UNITS = 4                       # Number of units (fixed)
T_RECUR = 3                       # Timesteps of recurrence per input (fixed)
N_TIMESTEPS = 1000                # Online learning steps
WARMUP = 200                      # Skip first steps for MSE eval
LR = 0.01
GRAD_CLIP = 5.0

ALPHA_VALUES = [0.3, 0.6, 1.0]
SEEDS = [42, 137, 256]

# Architecture configurations:
# Each config specifies number of layers and which layers have cross-connections
ARCH_CONFIGS = [
    {"name": "1-layer",        "n_layers": 1, "cross_layers": [True]},
    {"name": "2-layer-both",   "n_layers": 2, "cross_layers": [True, True]},
    {"name": "3-layer-all",    "n_layers": 3, "cross_layers": [True, True, True]},
    {"name": "2-layer-L1only", "n_layers": 2, "cross_layers": [True, False]},
    {"name": "2-layer-L2only", "n_layers": 2, "cross_layers": [False, True]},
]

TRAJ_RECORD_INTERVAL = 10  # Record weight trajectories every N steps


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
# Multi-Layer Cross-Connected Network
# ==============================================================================
class DeepCrossNetwork:
    """
    Multi-layer cross-connected recurrent network.

    Each layer L has N units with:
      - w_self[L]: self-recurrent weight (scalar, shared across units in layer)
      - w_cross[L]: cross-connection weight (scalar, shared across units in layer)
      - Per-unit hidden state h[L][i]

    Forward pass for unit i at layer L:
      input_L = (obs_i if L==0, else h[L-1][i])
      pre_act = input_L + w_self[L] * h[L][i](t-1) + w_cross[L] * mean(h_j for j!=i)
      h[L][i] = tanh(pre_act)

    The cross-connections at layer L connect to the SAME layer's previous hidden
    states (lateral recurrent connections), not to the layer below.

    Output: mean(h[final_layer]) -> w_out -> prediction
    """

    def __init__(self, n_layers, cross_layers, N=N_UNITS, seed=42):
        """
        n_layers: number of layers
        cross_layers: list of bool, whether each layer has cross-connections
        N: number of units per layer
        """
        self.n_layers = n_layers
        self.cross_layers = cross_layers
        self.N = N

        rng = np.random.RandomState(seed)

        # Per-layer weights (shared across units within a layer)
        self.w_self = [rng.uniform(0.4, 0.8) for _ in range(n_layers)]
        self.w_cross = [rng.uniform(-0.1, 0.1) if cross_layers[L] else 0.0
                        for L in range(n_layers)]

        # Output layer: linear from mean of final hidden states
        self.w_out = rng.uniform(-0.5, 0.5)
        self.b_out = 0.0

        # Hidden states: one per layer, per unit
        # h[L] is shape (N,)
        self.h = [np.zeros(N) for _ in range(n_layers)]

        # Per-unit predictions (for contamination)
        self.pred = np.zeros(N)

        # Cache for backward pass
        self._cache = None

    def forward_step(self, signal_t, alpha):
        """
        One timestep forward pass through all layers.

        Each unit i observes: obs_i = signal_t + alpha * pred_i(t-1)
        Then processes through layers sequentially.

        Returns: combined prediction (mean of per-unit final layer outputs -> linear)
        """
        N = self.N

        # Each unit gets its own contaminated observation
        obs = np.array([signal_t + alpha * self.pred[i] for i in range(N)])

        # Save previous hidden states
        h_prev = [h.copy() for h in self.h]

        # Cache for backward: store inputs and outputs at each layer
        layer_inputs = []    # input to each layer (before activation)
        layer_pre_act = []   # pre-activation values
        layer_outputs = []   # post-activation (tanh) values

        current_input = obs.copy()

        for L in range(self.n_layers):
            layer_inputs.append(current_input.copy())

            # Compute pre-activation for each unit
            pre_act = np.zeros(N)
            for i in range(N):
                pre_act[i] = current_input[i] + self.w_self[L] * h_prev[L][i]

                if self.cross_layers[L] and N > 1:
                    # Mean of other units' PREVIOUS hidden states in this layer
                    cross_sum = 0.0
                    for j in range(N):
                        if j != i:
                            cross_sum += h_prev[L][j]
                    cross_mean = cross_sum / (N - 1)
                    pre_act[i] += self.w_cross[L] * cross_mean

            layer_pre_act.append(pre_act.copy())

            # Activation
            h_new = np.tanh(pre_act)
            layer_outputs.append(h_new.copy())
            self.h[L] = h_new.copy()

            # Next layer's input is this layer's output
            current_input = h_new.copy()

        # Output: mean of final layer hidden states -> linear
        final_h = self.h[-1]
        mean_h = np.mean(final_h)
        pred_combined = self.w_out * mean_h + self.b_out

        # Per-unit predictions (for contamination at next step)
        # Each unit's contribution to the prediction
        for i in range(N):
            self.pred[i] = self.w_out * final_h[i] + self.b_out

        # Save cache
        self._cache = {
            'obs': obs,
            'h_prev': h_prev,
            'layer_inputs': layer_inputs,
            'layer_pre_act': layer_pre_act,
            'layer_outputs': layer_outputs,
            'final_h': final_h,
            'mean_h': mean_h,
            'pred_combined': pred_combined,
        }

        return pred_combined

    def backward_step(self, target):
        """
        Backpropagation through the multi-layer network.

        Loss = (pred_combined - target)^2
        where pred_combined = w_out * mean(h_final) + b_out

        Returns: loss value
        """
        N = self.N
        cache = self._cache

        pred = cache['pred_combined']
        loss = (pred - target) ** 2

        # d_loss / d_pred
        d_pred = 2.0 * (pred - target)

        # d_pred / d_w_out, d_b_out
        d_w_out = d_pred * cache['mean_h']
        d_b_out = d_pred

        # d_pred / d_mean_h
        d_mean_h = d_pred * self.w_out

        # d_mean_h / d_h_final[i] = 1/N for each unit
        d_h_final = np.full(N, d_mean_h / N)

        # Backprop through layers (from last to first)
        d_h_current = d_h_final.copy()

        d_w_self_all = [0.0] * self.n_layers
        d_w_cross_all = [0.0] * self.n_layers

        for L in range(self.n_layers - 1, -1, -1):
            h_out = cache['layer_outputs'][L]
            h_prev_L = cache['h_prev'][L]
            inp_L = cache['layer_inputs'][L]

            # Through tanh: d_pre_act[i] = d_h[i] * (1 - h_out[i]^2)
            d_pre_act = d_h_current * (1.0 - h_out ** 2)

            # Gradient for w_self[L]: sum over units of d_pre_act[i] * h_prev[L][i]
            d_w_self_L = 0.0
            for i in range(N):
                d_w_self_L += d_pre_act[i] * h_prev_L[i]
            d_w_self_all[L] = d_w_self_L

            # Gradient for w_cross[L]: sum over units of d_pre_act[i] * mean(h_prev[L][j] for j!=i)
            if self.cross_layers[L] and N > 1:
                d_w_cross_L = 0.0
                for i in range(N):
                    cross_sum = 0.0
                    for j in range(N):
                        if j != i:
                            cross_sum += h_prev_L[j]
                    cross_mean = cross_sum / (N - 1)
                    d_w_cross_L += d_pre_act[i] * cross_mean
                d_w_cross_all[L] = d_w_cross_L

            # Gradient flowing to previous layer's output (= this layer's input)
            d_input_L = d_pre_act.copy()  # d_pre_act / d_input = 1

            # Pass gradient to previous layer
            if L > 0:
                d_h_current = d_input_L
            # (If L == 0, gradient flows to obs which we don't optimize)

        # Update weights
        self.w_out -= LR * float(clip_grad(np.array([d_w_out]))[0])
        self.b_out -= LR * float(clip_grad(np.array([d_b_out]))[0])

        for L in range(self.n_layers):
            self.w_self[L] -= LR * float(clip_grad(np.array([d_w_self_all[L]]))[0])
            if self.cross_layers[L]:
                self.w_cross[L] -= LR * float(clip_grad(np.array([d_w_cross_all[L]]))[0])

        return loss

    def reset_state(self):
        """Reset all hidden states and predictions."""
        for L in range(self.n_layers):
            self.h[L] = np.zeros(self.N)
        self.pred = np.zeros(self.N)


# ==============================================================================
# Run a single condition
# ==============================================================================
def run_single(arch_config, alpha, seed):
    """
    Run a single experiment condition.
    Returns dict with MSE, per-layer w_self, per-layer w_cross, and trajectories.
    """
    set_seed(seed)
    signal = generate_signal(N_TIMESTEPS)

    n_layers = arch_config['n_layers']
    cross_layers = arch_config['cross_layers']

    model = DeepCrossNetwork(n_layers=n_layers, cross_layers=cross_layers,
                             N=N_UNITS, seed=seed)

    errors = []
    w_cross_traj = {L: [] for L in range(n_layers)}  # per-layer trajectories
    w_self_traj = {L: [] for L in range(n_layers)}

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

        # Record trajectories
        if t % TRAJ_RECORD_INTERVAL == 0:
            for L in range(n_layers):
                w_self_traj[L].append(model.w_self[L])
                w_cross_traj[L].append(model.w_cross[L])

    mse = np.mean(errors) if errors else float('inf')

    result = {
        'arch': arch_config['name'],
        'n_layers': n_layers,
        'alpha': alpha,
        'seed': seed,
        'mse': float(mse),
        'w_self_final': [model.w_self[L] for L in range(n_layers)],
        'w_cross_final': [model.w_cross[L] for L in range(n_layers)],
        'w_self_traj': w_self_traj,
        'w_cross_traj': w_cross_traj,
        'cross_layers': cross_layers,
    }

    return result


# ==============================================================================
# Main sweep
# ==============================================================================
def run_all():
    """Run all architecture configs x alphas x seeds."""
    total = len(ARCH_CONFIGS) * len(ALPHA_VALUES) * len(SEEDS)
    print(f"\nRunning {total} experiments...")
    print(f"  Architectures: {[c['name'] for c in ARCH_CONFIGS]}")
    print(f"  Alphas: {ALPHA_VALUES}")
    print(f"  Seeds: {SEEDS}")
    print(f"  N={N_UNITS} units, T={T_RECUR} recurrence steps, {N_TIMESTEPS} online steps")

    results = {}  # (arch_name, alpha, seed) -> result
    count = 0

    for arch in ARCH_CONFIGS:
        t0 = time.time()
        print(f"  {arch['name']:>16} ...", end="", flush=True)
        for alpha in ALPHA_VALUES:
            for seed in SEEDS:
                r = run_single(arch, alpha, seed)
                results[(arch['name'], alpha, seed)] = r
                count += 1
        elapsed = time.time() - t0
        print(f" done ({elapsed:.1f}s)")

    print(f"  All {count} runs complete.")
    return results


# ==============================================================================
# Analysis
# ==============================================================================
def analyze_results(results):
    """Comprehensive analysis of w_cross patterns across architectures and layers."""
    print("\n" + "=" * 80)
    print("ANALYSIS: Negative w_cross in Deeper Architectures")
    print("=" * 80)

    # ---- Table 1: w_cross by layer for each architecture (averaged over alpha and seeds) ----
    print("\n" + "-" * 80)
    print("TABLE 1: w_cross final values by layer (averaged over alpha and seeds)")
    print("-" * 80)
    max_layers = max(c['n_layers'] for c in ARCH_CONFIGS)
    header = f"{'Architecture':>16}"
    for L in range(max_layers):
        header += f"  {'w_cross_L'+str(L+1):>12}"
    print(header)
    print("-" * (16 + 14 * max_layers))

    for arch in ARCH_CONFIGS:
        row = f"{arch['name']:>16}"
        for L in range(max_layers):
            if L < arch['n_layers']:
                vals = []
                for alpha in ALPHA_VALUES:
                    for seed in SEEDS:
                        r = results[(arch['name'], alpha, seed)]
                        vals.append(r['w_cross_final'][L])
                mean_val = np.mean(vals)
                std_val = np.std(vals)
                row += f"  {mean_val:>+7.4f}+/-{std_val:.3f}"
            else:
                row += f"  {'---':>12}"
        print(row)

    # ---- Table 2: w_self by layer for each architecture ----
    print("\n" + "-" * 80)
    print("TABLE 2: w_self final values by layer (averaged over alpha and seeds)")
    print("-" * 80)
    header = f"{'Architecture':>16}"
    for L in range(max_layers):
        header += f"  {'w_self_L'+str(L+1):>12}"
    print(header)
    print("-" * (16 + 14 * max_layers))

    for arch in ARCH_CONFIGS:
        row = f"{arch['name']:>16}"
        for L in range(max_layers):
            if L < arch['n_layers']:
                vals = []
                for alpha in ALPHA_VALUES:
                    for seed in SEEDS:
                        r = results[(arch['name'], alpha, seed)]
                        vals.append(r['w_self_final'][L])
                mean_val = np.mean(vals)
                std_val = np.std(vals)
                row += f"  {mean_val:>+7.4f}+/-{std_val:.3f}"
            else:
                row += f"  {'---':>12}"
        print(row)

    # ---- Table 3: MSE by architecture and alpha ----
    print("\n" + "-" * 80)
    print("TABLE 3: MSE by architecture and alpha")
    print("-" * 80)
    header = f"{'Architecture':>16}"
    for alpha in ALPHA_VALUES:
        header += f"  {'a='+format(alpha,'.1f'):>10}"
    header += f"  {'Mean':>10}"
    print(header)
    print("-" * (16 + 12 * (len(ALPHA_VALUES) + 1)))

    mse_by_arch_alpha = {}
    for arch in ARCH_CONFIGS:
        row = f"{arch['name']:>16}"
        all_mses = []
        for alpha in ALPHA_VALUES:
            mses = [results[(arch['name'], alpha, s)]['mse'] for s in SEEDS]
            mean_mse = np.mean(mses)
            mse_by_arch_alpha[(arch['name'], alpha)] = mean_mse
            all_mses.append(mean_mse)
            row += f"  {mean_mse:>10.6f}"
        row += f"  {np.mean(all_mses):>10.6f}"
        print(row)

    # ---- Table 4: w_cross by layer for 2-layer config, broken down by alpha ----
    print("\n" + "-" * 80)
    print("TABLE 4: w_cross vs alpha for 2-layer-both config (per layer)")
    print("-" * 80)
    print(f"{'Alpha':>8} {'w_cross_L1':>12} {'w_cross_L2':>12} {'w_self_L1':>12} {'w_self_L2':>12}")
    print("-" * 60)

    for alpha in ALPHA_VALUES:
        wc1_vals, wc2_vals, ws1_vals, ws2_vals = [], [], [], []
        for seed in SEEDS:
            r = results[("2-layer-both", alpha, seed)]
            wc1_vals.append(r['w_cross_final'][0])
            wc2_vals.append(r['w_cross_final'][1])
            ws1_vals.append(r['w_self_final'][0])
            ws2_vals.append(r['w_self_final'][1])
        print(f"{alpha:>8.1f} {np.mean(wc1_vals):>+12.6f} {np.mean(wc2_vals):>+12.6f} "
              f"{np.mean(ws1_vals):>+12.6f} {np.mean(ws2_vals):>+12.6f}")

    # ---- Key findings ----
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    # 1. Is w_cross negative at ALL layers?
    print("\n  1. IS w_cross NEGATIVE AT EACH LAYER?")
    print("  " + "-" * 60)
    for arch in ARCH_CONFIGS:
        for L in range(arch['n_layers']):
            if arch['cross_layers'][L]:
                vals = []
                for alpha in ALPHA_VALUES:
                    for seed in SEEDS:
                        r = results[(arch['name'], alpha, seed)]
                        vals.append(r['w_cross_final'][L])
                mean_val = np.mean(vals)
                is_neg = mean_val < 0
                print(f"    {arch['name']:>16} Layer {L+1}: w_cross = {mean_val:>+.6f} "
                      f"{'[NEGATIVE]' if is_neg else '[POSITIVE]'}")

    # 2. Does depth change the magnitude?
    print("\n  2. DOES DEPTH CHANGE w_cross MAGNITUDE?")
    print("  " + "-" * 60)
    # Compare 1-layer vs 2-layer-both layer 1 vs 3-layer-all layer 1
    for arch_name in ["1-layer", "2-layer-both", "3-layer-all"]:
        vals = []
        for alpha in ALPHA_VALUES:
            for seed in SEEDS:
                r = results[(arch_name, alpha, seed)]
                vals.append(r['w_cross_final'][0])
        mean_val = np.mean(vals)
        print(f"    {arch_name:>16} Layer 1: |w_cross| = {abs(mean_val):.6f}")

    # For multi-layer: compare across layers
    for arch_name in ["2-layer-both", "3-layer-all"]:
        arch = [c for c in ARCH_CONFIGS if c['name'] == arch_name][0]
        vals_by_layer = []
        for L in range(arch['n_layers']):
            if arch['cross_layers'][L]:
                vals = []
                for alpha in ALPHA_VALUES:
                    for seed in SEEDS:
                        r = results[(arch_name, alpha, seed)]
                        vals.append(abs(r['w_cross_final'][L]))
                vals_by_layer.append((L, np.mean(vals)))
        print(f"    {arch_name}: ", end="")
        for L, mag in vals_by_layer:
            print(f"L{L+1}={mag:.4f}  ", end="")
        if len(vals_by_layer) > 1:
            decreases = all(vals_by_layer[i][1] > vals_by_layer[i+1][1]
                           for i in range(len(vals_by_layer)-1))
            print(f"{'[DECREASING with depth]' if decreases else '[NOT monotonically decreasing]'}")
        else:
            print()

    # 3. Does decontamination need to happen early or late?
    print("\n  3. DOES DECONTAMINATION NEED TO HAPPEN AT A SPECIFIC LAYER?")
    print("  " + "-" * 60)
    for alpha in ALPHA_VALUES:
        l1_mse = mse_by_arch_alpha.get(("2-layer-L1only", alpha), float('inf'))
        l2_mse = mse_by_arch_alpha.get(("2-layer-L2only", alpha), float('inf'))
        both_mse = mse_by_arch_alpha.get(("2-layer-both", alpha), float('inf'))
        best = "BOTH" if both_mse <= min(l1_mse, l2_mse) else ("L1-ONLY" if l1_mse < l2_mse else "L2-ONLY")
        print(f"    alpha={alpha:.1f}: L1-only={l1_mse:.6f}, L2-only={l2_mse:.6f}, "
              f"Both={both_mse:.6f} -> BEST: {best}")

    # 4. Overall MSE ranking
    print("\n  4. OVERALL MSE RANKING (averaged over alpha):")
    print("  " + "-" * 60)
    arch_mean_mse = []
    for arch in ARCH_CONFIGS:
        all_mses = [mse_by_arch_alpha[(arch['name'], a)] for a in ALPHA_VALUES]
        arch_mean_mse.append((arch['name'], np.mean(all_mses)))
    arch_mean_mse.sort(key=lambda x: x[1])
    for rank, (name, mse) in enumerate(arch_mean_mse, 1):
        print(f"    {rank}. {name:>16}: MSE = {mse:.6f}")

    return mse_by_arch_alpha


# ==============================================================================
# Plotting
# ==============================================================================
def create_plots(results, mse_by_arch_alpha):
    """Generate 2x3 results plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle("Deep Cross-Connection Test: Does Negative w_cross Hold in Multi-Layer Networks?",
                 fontsize=13, fontweight='bold')

    # Color palette
    arch_colors = {
        "1-layer": "#2196F3",
        "2-layer-both": "#FF5722",
        "3-layer-all": "#4CAF50",
        "2-layer-L1only": "#9C27B0",
        "2-layer-L2only": "#FF9800",
    }
    layer_colors = ["#2196F3", "#FF5722", "#4CAF50"]  # L1, L2, L3

    # ---- Panel 1: w_cross by layer for each depth config (bar chart, with zero line) ----
    ax = axes[0, 0]
    # Grouped bar chart: one group per architecture, bars per layer
    arch_names = [c['name'] for c in ARCH_CONFIGS]
    max_layers = 3
    bar_width = 0.2
    x_positions = np.arange(len(arch_names))

    for L in range(max_layers):
        vals = []
        for arch in ARCH_CONFIGS:
            if L < arch['n_layers'] and arch['cross_layers'][L]:
                layer_vals = []
                for alpha in ALPHA_VALUES:
                    for seed in SEEDS:
                        r = results[(arch['name'], alpha, seed)]
                        layer_vals.append(r['w_cross_final'][L])
                vals.append(np.mean(layer_vals))
            else:
                vals.append(0.0)  # No cross at this layer or layer doesn't exist

        # Only plot bars where the layer exists and has cross-connections
        mask = []
        for arch in ARCH_CONFIGS:
            mask.append(L < arch['n_layers'] and arch['cross_layers'][L])

        x_off = x_positions + (L - 1) * bar_width
        bar_vals = [v if m else 0 for v, m in zip(vals, mask)]
        bar_colors = [layer_colors[L] if m else 'lightgray' for m in mask]
        bars = ax.bar(x_off, bar_vals, bar_width, color=bar_colors, edgecolor='black',
                      alpha=0.8, label=f'Layer {L+1}' if L == 0 or any(
                          c['n_layers'] > L for c in ARCH_CONFIGS) else None)

    ax.axhline(y=0, color='black', linewidth=1.5)
    ax.axhline(y=-0.26, color='red', linewidth=1, linestyle='--', alpha=0.5,
               label='w_cross ~ -0.26 (baseline)')
    ax.set_xlabel('Architecture')
    ax.set_ylabel('w_cross (mean)')
    ax.set_title('Panel 1: w_cross by Layer')
    ax.set_xticks(x_positions)
    ax.set_xticklabels([c['name'] for c in ARCH_CONFIGS], rotation=30, ha='right', fontsize=7)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis='y')

    # ---- Panel 2: w_self by layer for each depth config ----
    ax = axes[0, 1]
    for L in range(max_layers):
        vals = []
        for arch in ARCH_CONFIGS:
            if L < arch['n_layers']:
                layer_vals = []
                for alpha in ALPHA_VALUES:
                    for seed in SEEDS:
                        r = results[(arch['name'], alpha, seed)]
                        layer_vals.append(r['w_self_final'][L])
                vals.append(np.mean(layer_vals))
            else:
                vals.append(np.nan)

        x_off = x_positions + (L - 1) * bar_width
        valid = [not np.isnan(v) for v in vals]
        bar_vals = [v if vld else 0 for v, vld in zip(vals, valid)]
        bar_colors = [layer_colors[L] if vld else 'lightgray' for vld in valid]
        ax.bar(x_off, bar_vals, bar_width, color=bar_colors, edgecolor='black',
               alpha=0.8, label=f'Layer {L+1}')

    ax.axhline(y=INV_PHI, color='orange', linewidth=2, linestyle='--',
               label=f'1/phi = {INV_PHI:.3f}')
    ax.set_xlabel('Architecture')
    ax.set_ylabel('w_self (mean)')
    ax.set_title('Panel 2: w_self by Layer')
    ax.set_xticks(x_positions)
    ax.set_xticklabels([c['name'] for c in ARCH_CONFIGS], rotation=30, ha='right', fontsize=7)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis='y')

    # ---- Panel 3: MSE by architecture (grouped by alpha) ----
    ax = axes[0, 2]
    n_arch = len(ARCH_CONFIGS)
    n_alpha = len(ALPHA_VALUES)
    bar_width_3 = 0.15
    x_pos_3 = np.arange(n_arch)

    for i, alpha in enumerate(ALPHA_VALUES):
        mses = [mse_by_arch_alpha[(c['name'], alpha)] for c in ARCH_CONFIGS]
        offset = (i - n_alpha / 2 + 0.5) * bar_width_3
        ax.bar(x_pos_3 + offset, mses, bar_width_3, label=f'a={alpha:.1f}',
               alpha=0.8, edgecolor='black')

    ax.set_xlabel('Architecture')
    ax.set_ylabel('MSE')
    ax.set_title('Panel 3: MSE by Architecture & Alpha')
    ax.set_xticks(x_pos_3)
    ax.set_xticklabels([c['name'] for c in ARCH_CONFIGS], rotation=30, ha='right', fontsize=7)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis='y')

    # ---- Panel 4: w_cross vs alpha for each layer (2-layer config) ----
    ax = axes[1, 0]
    for L in range(2):
        vals = []
        stds = []
        for alpha in ALPHA_VALUES:
            layer_vals = []
            for seed in SEEDS:
                r = results[("2-layer-both", alpha, seed)]
                layer_vals.append(r['w_cross_final'][L])
            vals.append(np.mean(layer_vals))
            stds.append(np.std(layer_vals))
        ax.errorbar(ALPHA_VALUES, vals, yerr=stds, fmt='o-', color=layer_colors[L],
                    label=f'Layer {L+1}', linewidth=2, capsize=4, markersize=6)

    ax.axhline(y=0, color='black', linewidth=1)
    ax.axhline(y=-0.26, color='red', linewidth=1, linestyle='--', alpha=0.5,
               label='w_cross ~ -0.26')
    ax.set_xlabel('Alpha (contamination strength)')
    ax.set_ylabel('w_cross')
    ax.set_title('Panel 4: w_cross vs Alpha (2-layer-both)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- Panel 5: Training trajectories of w_cross for layer 1 vs layer 2 ----
    ax = axes[1, 1]
    # Use alpha=0.6 as representative
    target_alpha = 0.6
    for seed in SEEDS:
        r = results[("2-layer-both", target_alpha, seed)]
        t_axis = np.arange(len(r['w_cross_traj'][0])) * TRAJ_RECORD_INTERVAL

        ax.plot(t_axis, r['w_cross_traj'][0], color=layer_colors[0], alpha=0.6,
                linewidth=1.5,
                label='Layer 1 w_cross' if seed == SEEDS[0] else None)
        ax.plot(t_axis, r['w_cross_traj'][1], color=layer_colors[1], alpha=0.6,
                linewidth=1.5, linestyle='--',
                label='Layer 2 w_cross' if seed == SEEDS[0] else None)

    ax.axhline(y=0, color='black', linewidth=1)
    ax.axhline(y=-0.26, color='red', linewidth=1, linestyle='--', alpha=0.3,
               label='~-0.26 reference')
    ax.set_xlabel('Training Step')
    ax.set_ylabel('w_cross')
    ax.set_title(f'Panel 5: w_cross Trajectories (2-layer, alpha={target_alpha})')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ---- Panel 6: Heatmap: architecture x alpha -> MSE ----
    ax = axes[1, 2]
    arch_names_short = [c['name'] for c in ARCH_CONFIGS]
    heatmap_data = np.zeros((len(ARCH_CONFIGS), len(ALPHA_VALUES)))
    for i, arch in enumerate(ARCH_CONFIGS):
        for j, alpha in enumerate(ALPHA_VALUES):
            heatmap_data[i, j] = mse_by_arch_alpha[(arch['name'], alpha)]

    im = ax.imshow(heatmap_data, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(ALPHA_VALUES)))
    ax.set_xticklabels([f'{a:.1f}' for a in ALPHA_VALUES])
    ax.set_yticks(range(len(ARCH_CONFIGS)))
    ax.set_yticklabels(arch_names_short, fontsize=8)
    ax.set_xlabel('Alpha')
    ax.set_ylabel('Architecture')
    ax.set_title('Panel 6: MSE Heatmap (Architecture x Alpha)')

    # Add text annotations
    for i in range(len(ARCH_CONFIGS)):
        for j in range(len(ALPHA_VALUES)):
            val = heatmap_data[i, j]
            color = 'white' if val > np.median(heatmap_data) else 'black'
            ax.text(j, i, f'{val:.4f}', ha='center', va='center', fontsize=7, color=color)

    fig.colorbar(im, ax=ax, shrink=0.8, label='MSE')

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep_cross_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 80)
    print("DEEP CROSS-CONNECTION TEST")
    print("Does the negative w_cross pattern hold in multi-layer networks?")
    print("=" * 80)
    print(f"  N = {N_UNITS} units, T = {T_RECUR} recurrence timesteps")
    print(f"  Online learning: {N_TIMESTEPS} steps, LR = {LR}, warmup = {WARMUP}")
    print(f"  Alphas: {ALPHA_VALUES}")
    print(f"  Seeds: {SEEDS}")
    print(f"  Architectures:")
    for arch in ARCH_CONFIGS:
        cross_str = ", ".join(
            f"L{L+1}={'cross' if arch['cross_layers'][L] else 'no-cross'}"
            for L in range(arch['n_layers'])
        )
        print(f"    {arch['name']:>16}: {arch['n_layers']} layers ({cross_str})")
    print(f"  Reference: 1/phi = {INV_PHI:.6f}")

    t_start = time.time()

    # ---- Run all experiments ----
    results = run_all()

    # ---- Analysis ----
    mse_by_arch_alpha = analyze_results(results)

    # ---- Plots ----
    create_plots(results, mse_by_arch_alpha)

    # ---- Final summary ----
    total_time = time.time() - t_start
    print(f"\n{'=' * 80}")
    print(f"EXPERIMENT COMPLETE in {total_time:.1f}s")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
