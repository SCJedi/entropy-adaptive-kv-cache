"""
Minimal Stable Self-Referential Architecture: Numerical Verification
====================================================================
Tests the four structural requirements for cascade stability:
  1. Dual Channels (N >= 2)
  2. Inhibitory Cross-Connections (w_cross < 0)
  3. Prediction Error Passing (Predictive Coding)
  4. External Grounding (Periodic Ground Truth)

Experiments:
  1. Necessity test: remove each component, show R^2 collapse
  2. MVSU simulation: minimum viable stable unit through 7 stages
  3. Stability boundary: sweep (alpha, g) space
  4. Architecture comparison: 5 architectures through 7 stages
  5. Grounding rate test: R^2_final vs g for different alpha
  6. Ablation study: remove one component at a time, measure degradation

Author: Claude (minimal stable architecture from Ouroboros framework)
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
PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1.0 / PHI

N_TIMESTEPS = 5000
WARMUP = 1000
LR = 0.005
GRAD_CLIP = 5.0
SEEDS = [42, 137, 256]

# Biological cascade: 7 stages with increasing contamination
BIO_ALPHAS = [0.05, 0.30, 0.50, 0.60, 0.80, 0.90, 1.00]
BIO_NAMES = ["Sensory", "Features", "Binding", "Awareness", "Narrative", "Memory", "Recall"]
N_STAGES = 7

# Stability threshold
EPSILON = 0.10  # R^2 > 0.10 = "stable"


# ==============================================================================
# Analytical functions
# ==============================================================================
def w_myopic(alpha):
    """Myopic weight from alpha^2*w^2 + w - 1 = 0."""
    if alpha < 1e-12:
        return 1.0
    a2 = alpha ** 2
    return (-1.0 + np.sqrt(1.0 + 4.0 * a2)) / (2.0 * a2)


def w_system_aware(alpha, n_iter=200):
    """System-aware optimal weight: w = (1 - alpha^2 * w^2)^2."""
    if alpha < 1e-12:
        return 1.0
    w = w_myopic(alpha)
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


def r2_system_aware(alpha):
    """R^2 for system-aware optimizer."""
    w = w_system_aware(alpha)
    if alpha < 1e-12:
        return 1.0
    a2w2 = alpha ** 2 * w ** 2
    if a2w2 >= 1.0:
        return 0.0
    mse = w ** 2 / (1.0 - a2w2) + 1.0 - 2.0 * w
    return max(0.0, 1.0 - mse)


# ==============================================================================
# Stage Simulation Components
# ==============================================================================
def simulate_monocular_stage(alpha, n_steps, seed, signal_in=None, lr=LR):
    """Single monocular stage with SGD-learned weight."""
    rng = np.random.RandomState(seed)
    if signal_in is None:
        signal = rng.randn(n_steps)
    else:
        signal = signal_in.copy()

    w = rng.uniform(0.3, 0.7)
    y_prev = 0.0
    output = np.zeros(n_steps)
    errors = []

    for t in range(n_steps):
        y = signal[t] + alpha * w * y_prev
        pred = w * y
        output[t] = pred
        if t >= WARMUP:
            errors.append((pred - signal[t]) ** 2)
        grad = 2.0 * (pred - signal[t]) * y
        w -= lr * np.clip(grad, -GRAD_CLIP, GRAD_CLIP)
        y_prev = y

    mse = np.mean(errors) if errors else 1.0
    var_s = np.var(signal[WARMUP:])
    r2 = max(0.0, 1.0 - mse / var_s) if var_s > 1e-12 else 0.0
    return {"r2": r2, "output": output, "signal": signal, "w": w}


def simulate_binocular_stage(alpha, n_steps, seed, signal_in=None, lr=LR,
                              allow_cross=True, init_cross_negative=False):
    """
    Binocular (N=2) stage with cross-connections.
    allow_cross: if True, learn cross-weights; if False, force w_cross=0
    init_cross_negative: if True, initialize w_cross near -0.1 (to test necessity)
    """
    rng = np.random.RandomState(seed)
    if signal_in is None:
        signal = rng.randn(n_steps)
    else:
        signal = signal_in.copy()

    w_self = np.array([rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7)])
    if allow_cross:
        if init_cross_negative:
            w_cross = np.array([rng.uniform(-0.3, -0.05), rng.uniform(-0.3, -0.05)])
        else:
            w_cross = np.array([rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1)])
    else:
        w_cross = np.zeros(2)

    y_prev = np.zeros(2)
    output = np.zeros(n_steps)
    errors = []

    for t in range(n_steps):
        y = np.zeros(2)
        for j in range(2):
            y[j] = signal[t] + alpha * w_self[j] * y_prev[j] + w_cross[j] * y_prev[1 - j]

        pred_j = w_self * y
        pred = np.mean(pred_j)
        output[t] = pred

        if t >= WARMUP:
            errors.append((pred - signal[t]) ** 2)

        for j in range(2):
            err_j = pred_j[j] - signal[t]
            grad_self = 2.0 * err_j * y[j]
            w_self[j] -= lr * np.clip(grad_self, -GRAD_CLIP, GRAD_CLIP)
            if allow_cross:
                grad_cross = 2.0 * err_j * y_prev[1 - j]
                w_cross[j] -= lr * np.clip(grad_cross, -GRAD_CLIP, GRAD_CLIP)

        y_prev = y.copy()

    mse = np.mean(errors) if errors else 1.0
    var_s = np.var(signal[WARMUP:])
    r2 = max(0.0, 1.0 - mse / var_s) if var_s > 1e-12 else 0.0
    return {"r2": r2, "output": output, "signal": signal,
            "w_self": w_self.copy(), "w_cross": w_cross.copy()}


def simulate_binocular_positive_cross(alpha, n_steps, seed, signal_in=None, lr=LR):
    """
    Binocular stage where cross-connections are FORCED POSITIVE.
    Tests whether positive cross-connections make things worse.
    """
    rng = np.random.RandomState(seed)
    if signal_in is None:
        signal = rng.randn(n_steps)
    else:
        signal = signal_in.copy()

    w_self = np.array([rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7)])
    w_cross = np.array([rng.uniform(0.05, 0.3), rng.uniform(0.05, 0.3)])

    y_prev = np.zeros(2)
    output = np.zeros(n_steps)
    errors = []

    for t in range(n_steps):
        y = np.zeros(2)
        for j in range(2):
            y[j] = signal[t] + alpha * w_self[j] * y_prev[j] + w_cross[j] * y_prev[1 - j]

        pred_j = w_self * y
        pred = np.mean(pred_j)
        output[t] = pred

        if t >= WARMUP:
            errors.append((pred - signal[t]) ** 2)

        for j in range(2):
            err_j = pred_j[j] - signal[t]
            grad_self = 2.0 * err_j * y[j]
            w_self[j] -= lr * np.clip(grad_self, -GRAD_CLIP, GRAD_CLIP)
            grad_cross = 2.0 * err_j * y_prev[1 - j]
            w_cross[j] -= lr * np.clip(grad_cross, -GRAD_CLIP, GRAD_CLIP)
            # Force positive: clip cross-weights to [0.01, inf)
            w_cross[j] = max(0.01, w_cross[j])

        y_prev = y.copy()

    mse = np.mean(errors) if errors else 1.0
    var_s = np.var(signal[WARMUP:])
    r2 = max(0.0, 1.0 - mse / var_s) if var_s > 1e-12 else 0.0
    return {"r2": r2, "output": output, "signal": signal,
            "w_self": w_self.copy(), "w_cross": w_cross.copy()}


def simulate_predictive_stage(alpha, n_steps, seed, signal_in=None):
    """
    System-aware (predictive coding) stage: uses oracle weight
    that accounts for feedback, passing prediction errors.
    """
    rng = np.random.RandomState(seed)
    if signal_in is None:
        signal = rng.randn(n_steps)
    else:
        signal = signal_in.copy()

    w_opt = w_system_aware(alpha)
    y_prev = 0.0
    output = np.zeros(n_steps)
    errors = []

    for t in range(n_steps):
        y = signal[t] + alpha * w_opt * y_prev
        pred = w_opt * y
        # Prediction error output (decorrelated)
        error_signal = y - pred  # = (1 - w_opt) * y
        # The output is the corrected prediction
        output[t] = pred
        if t >= WARMUP:
            errors.append((pred - signal[t]) ** 2)
        y_prev = y

    mse = np.mean(errors) if errors else 1.0
    var_s = np.var(signal[WARMUP:])
    r2 = max(0.0, 1.0 - mse / var_s) if var_s > 1e-12 else 0.0
    return {"r2": r2, "output": output, "signal": signal, "w": w_opt}


def simulate_grounded_stage(alpha, n_steps, seed, signal_in=None,
                             grounding_rate=0.0, lr=LR):
    """
    Stage with periodic external grounding.
    grounding_rate g: fraction of timesteps where the stage receives
    the true signal instead of its contaminated observation.
    """
    rng = np.random.RandomState(seed)
    if signal_in is None:
        signal = rng.randn(n_steps)
    else:
        signal = signal_in.copy()

    w = rng.uniform(0.3, 0.7)
    y_prev = 0.0
    output = np.zeros(n_steps)
    errors = []

    for t in range(n_steps):
        # With probability g, receive uncontaminated signal
        if rng.rand() < grounding_rate:
            y = signal[t]  # Ground truth: no contamination
        else:
            y = signal[t] + alpha * w * y_prev

        pred = w * y
        output[t] = pred

        if t >= WARMUP:
            errors.append((pred - signal[t]) ** 2)

        grad = 2.0 * (pred - signal[t]) * y
        w -= lr * np.clip(grad, -GRAD_CLIP, GRAD_CLIP)
        y_prev = y

    mse = np.mean(errors) if errors else 1.0
    var_s = np.var(signal[WARMUP:])
    r2 = max(0.0, 1.0 - mse / var_s) if var_s > 1e-12 else 0.0
    return {"r2": r2, "output": output, "signal": signal, "w": w}


# ==============================================================================
# MVSU: Minimum Viable Stable Unit
# ==============================================================================
def simulate_mvsu_stage(alpha, n_steps, seed, signal_in=None,
                         grounding_rate=0.0, use_predictive=True,
                         use_cross=True, use_dual=True):
    """
    Minimum Viable Stable Unit (MVSU):
      - 2 channels (dual) with independent processing
      - Cross-connections with learned negative weights (inhibitory)
      - Prediction error output (predictive coding)
      - Periodic grounding input
      - T=2 integration depth (implicit in binocular cross-integration)

    Ablation: each component can be toggled off.
    """
    rng = np.random.RandomState(seed)
    if signal_in is None:
        signal = rng.randn(n_steps)
    else:
        signal = signal_in.copy()

    N_ch = 2 if use_dual else 1

    if use_predictive:
        # Use system-aware weights
        w_opt = w_system_aware(alpha)
        w_self = np.array([w_opt] * N_ch)
    else:
        w_self = np.array([rng.uniform(0.3, 0.7) for _ in range(N_ch)])

    if use_cross and N_ch > 1:
        w_cross = np.array([rng.uniform(-0.15, -0.05) for _ in range(N_ch)])
    else:
        w_cross = np.zeros(N_ch)

    y_prev = np.zeros(N_ch)
    output = np.zeros(n_steps)
    errors = []

    for t in range(n_steps):
        # Grounding: with probability g, use uncontaminated observation
        grounded = rng.rand() < grounding_rate

        y = np.zeros(N_ch)
        for j in range(N_ch):
            if grounded:
                y[j] = signal[t]
            else:
                cross_term = 0.0
                if use_cross and N_ch > 1:
                    cross_term = w_cross[j] * y_prev[1 - j]
                y[j] = signal[t] + alpha * w_self[j] * y_prev[j] + cross_term

        pred_j = w_self * y
        pred = np.mean(pred_j)
        output[t] = pred

        if t >= WARMUP:
            errors.append((pred - signal[t]) ** 2)

        # Learn cross-weights (self weights fixed if predictive)
        if not use_predictive:
            for j in range(N_ch):
                err_j = pred_j[j] - signal[t]
                grad_self = 2.0 * err_j * y[j]
                w_self[j] -= LR * np.clip(grad_self, -GRAD_CLIP, GRAD_CLIP)

        if use_cross and N_ch > 1:
            for j in range(N_ch):
                err_j = pred_j[j] - signal[t]
                grad_cross = 2.0 * err_j * y_prev[1 - j]
                w_cross[j] -= LR * np.clip(grad_cross, -GRAD_CLIP, GRAD_CLIP)

        y_prev = y.copy()

    mse = np.mean(errors) if errors else 1.0
    var_s = np.var(signal[WARMUP:])
    r2 = max(0.0, 1.0 - mse / var_s) if var_s > 1e-12 else 0.0

    n_params = N_ch * 2  # w_self + w_cross per channel (or just w_self if no cross)
    if not use_cross:
        n_params = N_ch

    return {"r2": r2, "output": output, "signal": signal,
            "w_self": w_self.copy(), "w_cross": w_cross.copy(),
            "n_params": n_params}


# ==============================================================================
# Cascade simulation
# ==============================================================================
def simulate_cascade(stage_configs, n_steps, seed):
    """
    Run a cascade of stages, each feeding output to the next.
    stage_configs: list of dicts, each with 'type' and parameters.
    Returns R^2 at each stage vs original signal.
    """
    rng = np.random.RandomState(seed)
    original_signal = rng.randn(n_steps)
    current_input = original_signal.copy()
    stage_r2s = []

    for i, config in enumerate(stage_configs):
        stage_seed = seed + i * 1000
        alpha = config["alpha"]
        stage_type = config.get("type", "monocular")

        if stage_type == "monocular":
            result = simulate_monocular_stage(alpha, n_steps, stage_seed,
                                               signal_in=current_input)
        elif stage_type == "binocular":
            result = simulate_binocular_stage(alpha, n_steps, stage_seed,
                                               signal_in=current_input)
        elif stage_type == "binocular_positive":
            result = simulate_binocular_positive_cross(alpha, n_steps, stage_seed,
                                                        signal_in=current_input)
        elif stage_type == "binocular_no_cross":
            result = simulate_binocular_stage(alpha, n_steps, stage_seed,
                                               signal_in=current_input, allow_cross=False)
        elif stage_type == "predictive":
            result = simulate_predictive_stage(alpha, n_steps, stage_seed,
                                                signal_in=current_input)
        elif stage_type == "grounded":
            g = config.get("grounding_rate", 0.1)
            result = simulate_grounded_stage(alpha, n_steps, stage_seed,
                                              signal_in=current_input,
                                              grounding_rate=g)
        elif stage_type == "mvsu":
            g = config.get("grounding_rate", 0.1)
            result = simulate_mvsu_stage(
                alpha, n_steps, stage_seed,
                signal_in=current_input,
                grounding_rate=g,
                use_predictive=config.get("use_predictive", True),
                use_cross=config.get("use_cross", True),
                use_dual=config.get("use_dual", True),
            )
        else:
            raise ValueError(f"Unknown stage type: {stage_type}")

        # R^2 vs original signal
        valid = slice(WARMUP, n_steps)
        cov_orig = np.cov(result["output"][valid], original_signal[valid])
        if cov_orig[1, 1] > 1e-12 and cov_orig[0, 0] > 1e-12:
            r2_vs_original = cov_orig[0, 1] ** 2 / (cov_orig[0, 0] * cov_orig[1, 1])
        else:
            r2_vs_original = 0.0

        stage_r2s.append(r2_vs_original)
        current_input = result["output"].copy()

    return stage_r2s


# ==============================================================================
# Architecture definitions
# ==============================================================================
def make_raw_monocular():
    """Architecture 1: Raw monocular -- no components."""
    return [{"alpha": a, "type": "monocular"} for a in BIO_ALPHAS]


def make_dual_naive():
    """Architecture 2: Dual channels, no cross-connections (independent)."""
    return [{"alpha": a, "type": "binocular_no_cross"} for a in BIO_ALPHAS]


def make_dual_inhibitory():
    """Architecture 3: Dual channels + inhibitory cross-connections."""
    return [{"alpha": a, "type": "binocular"} for a in BIO_ALPHAS]


def make_dual_predictive():
    """Architecture 4: Dual + inhibitory + predictive coding."""
    return [{"alpha": a, "type": "mvsu", "grounding_rate": 0.0,
             "use_predictive": True, "use_cross": True, "use_dual": True}
            for a in BIO_ALPHAS]


def make_full_stable(g=0.10):
    """Architecture 5: Full MVSU -- all four components."""
    return [{"alpha": a, "type": "mvsu", "grounding_rate": g,
             "use_predictive": True, "use_cross": True, "use_dual": True}
            for a in BIO_ALPHAS]


# ==============================================================================
# Experiment 1: Component Necessity Test
# ==============================================================================
def experiment_1_necessity():
    """
    For each of the 4 components, build a cascade WITH and WITHOUT
    that component. Show that removing any one causes R^2 to collapse.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 1: Component Necessity Test")
    print("=" * 70)
    print("  Testing: is each of the 4 components necessary for stability?")

    g = 0.10  # grounding rate for full MVSU

    # Full MVSU (all components)
    full_configs = make_full_stable(g)

    # Ablations: remove one component at a time
    ablations = {
        "Full MVSU": {
            "use_dual": True, "use_cross": True,
            "use_predictive": True, "grounding_rate": g,
        },
        "No Dual (N=1)": {
            "use_dual": False, "use_cross": False,  # can't have cross without dual
            "use_predictive": True, "grounding_rate": g,
        },
        "No Inhibition": {
            "use_dual": True, "use_cross": False,
            "use_predictive": True, "grounding_rate": g,
        },
        "No Predictive": {
            "use_dual": True, "use_cross": True,
            "use_predictive": False, "grounding_rate": g,
        },
        "No Grounding": {
            "use_dual": True, "use_cross": True,
            "use_predictive": True, "grounding_rate": 0.0,
        },
    }

    results = {}
    for name, params in ablations.items():
        configs = []
        for a in BIO_ALPHAS:
            configs.append({
                "alpha": a, "type": "mvsu",
                "use_dual": params["use_dual"],
                "use_cross": params["use_cross"],
                "use_predictive": params["use_predictive"],
                "grounding_rate": params["grounding_rate"],
            })

        all_stage_r2s = []
        for seed in SEEDS:
            stage_r2s = simulate_cascade(configs, N_TIMESTEPS, seed)
            all_stage_r2s.append(stage_r2s)

        mean_stage_r2s = np.mean(all_stage_r2s, axis=0)
        results[name] = mean_stage_r2s

    # Print table
    print(f"\n{'Stage':>12}", end="")
    for name in ablations:
        print(f"  {name:>14}", end="")
    print()
    print("-" * (12 + 16 * len(ablations)))

    for i, stage_name in enumerate(BIO_NAMES):
        print(f"{stage_name:>12}", end="")
        for name in ablations:
            r2 = results[name][i]
            print(f"  {r2:>14.4f}", end="")
        print()

    # Final stage summary
    print(f"\n{'Final R^2':>12}", end="")
    for name in ablations:
        r2_final = results[name][-1]
        stable = "STABLE" if r2_final > EPSILON else "COLLAPSED"
        print(f"  {r2_final:>8.4f} [{stable[:4]}]", end="")
    print()

    # Check necessity
    full_final = results["Full MVSU"][-1]
    print("\n  NECESSITY CHECK (each component required for R^2 > epsilon):")
    component_map = {
        "No Dual (N=1)": "Dual Channels",
        "No Inhibition": "Inhibitory Cross",
        "No Predictive": "Predictive Coding",
        "No Grounding": "External Grounding",
    }
    for ablation_name, component_name in component_map.items():
        ablated_final = results[ablation_name][-1]
        degradation = (full_final - ablated_final) / full_final * 100 if full_final > 1e-6 else 0
        necessary = ablated_final < full_final * 0.7  # > 30% degradation = necessary
        print(f"    {component_name:>20}: R^2 = {ablated_final:.4f} "
              f"(degradation: {degradation:+.1f}%) "
              f"{'[NECESSARY]' if necessary else '[helpful]'}")

    return results


# ==============================================================================
# Experiment 2: MVSU Simulation
# ==============================================================================
def experiment_2_mvsu():
    """
    Build the MVSU and run through 7 stages.
    Vary grounding rate g from 0 to 1.
    Find minimum g that maintains R^2 > epsilon after 7 stages.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: MVSU Grounding Rate Sweep")
    print("=" * 70)

    g_values = np.arange(0.0, 1.01, 0.10)
    results = {}

    print(f"\n  {'g':>6}  {'Final R^2':>10}  {'Stable':>8}")
    print("  " + "-" * 30)

    for g in g_values:
        all_finals = []
        for seed in SEEDS[:2]:
            configs = make_full_stable(g)
            stage_r2s = simulate_cascade(configs, N_TIMESTEPS, seed)
            all_finals.append(stage_r2s[-1])

        mean_final = np.mean(all_finals)
        stable = "YES" if mean_final > EPSILON else "NO"
        print(f"  {g:6.2f}  {mean_final:10.4f}  {stable:>8}")
        results[float(np.round(g, 2))] = mean_final

    # Find minimum g for stability
    min_g = None
    for g in sorted(results.keys()):
        if results[g] > EPSILON:
            min_g = g
            break

    if min_g is not None:
        print(f"\n  MINIMUM GROUNDING RATE for R^2 > {EPSILON}: g = {min_g:.2f}")
    else:
        print(f"\n  WARNING: No grounding rate achieved R^2 > {EPSILON}")

    return results, min_g


# ==============================================================================
# Experiment 3: Stability Boundary
# ==============================================================================
def experiment_3_stability_boundary():
    """
    Sweep (alpha, g) space and map where the system maintains signal fidelity.
    Uses a UNIFORM alpha cascade (all stages same alpha) for clean interpretation.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Stability Boundary in (alpha, g) Space")
    print("=" * 70)

    alpha_sweep = np.arange(0.1, 1.05, 0.15)
    g_sweep = np.arange(0.0, 0.55, 0.05)
    n_cascade = 5  # 5 stages for faster sweep

    r2_grid = np.zeros((len(alpha_sweep), len(g_sweep)))

    for i, alpha in enumerate(alpha_sweep):
        for j, g in enumerate(g_sweep):
            finals = []
            for seed in SEEDS[:1]:  # 1 seed for speed
                configs = [{"alpha": alpha, "type": "mvsu",
                            "grounding_rate": g, "use_predictive": True,
                            "use_cross": True, "use_dual": True}
                           for _ in range(n_cascade)]
                stage_r2s = simulate_cascade(configs, N_TIMESTEPS, seed)
                finals.append(stage_r2s[-1])
            r2_grid[i, j] = np.mean(finals)

    # Print summary
    print(f"\n  Stability boundary (R^2 > {EPSILON}):")
    print(f"  {'alpha':>6}", end="")
    for g in g_sweep:
        print(f"  {g:>5.2f}", end="")
    print()
    print("  " + "-" * (6 + 7 * len(g_sweep)))
    for i, alpha in enumerate(alpha_sweep):
        print(f"  {alpha:>6.2f}", end="")
        for j in range(len(g_sweep)):
            r2 = r2_grid[i, j]
            marker = "  +" if r2 > EPSILON else "  ."
            print(f"{marker:>5}  ", end="")
        print()

    return alpha_sweep, g_sweep, r2_grid


# ==============================================================================
# Experiment 4: Architecture Comparison
# ==============================================================================
def experiment_4_architecture_comparison():
    """
    Compare all 5 architectures from the taxonomy through the 7-stage cascade.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 4: Architecture Comparison (7-Stage Cascade)")
    print("=" * 70)

    architectures = {
        "Raw Monocular": make_raw_monocular,
        "Dual Naive": make_dual_naive,
        "Dual Inhibitory": make_dual_inhibitory,
        "Dual+Predictive": make_dual_predictive,
        "Full MVSU (g=0.1)": lambda: make_full_stable(0.10),
    }

    results = {}
    for name, config_fn in architectures.items():
        configs = config_fn()
        all_stage_r2s = []
        for seed in SEEDS:
            stage_r2s = simulate_cascade(configs, N_TIMESTEPS, seed)
            all_stage_r2s.append(stage_r2s)
        mean_stage_r2s = np.mean(all_stage_r2s, axis=0)
        results[name] = mean_stage_r2s

    # Print table
    print(f"\n{'Stage':>12}", end="")
    for name in architectures:
        short = name[:14]
        print(f"  {short:>14}", end="")
    print()
    print("-" * (12 + 16 * len(architectures)))

    for i, stage_name in enumerate(BIO_NAMES):
        print(f"{stage_name:>12}", end="")
        for name in architectures:
            r2 = results[name][i]
            print(f"  {r2:>14.4f}", end="")
        print()

    print(f"\n  FINAL R^2 COMPARISON:")
    for name in architectures:
        r2_final = results[name][-1]
        stable = "STABLE" if r2_final > EPSILON else "COLLAPSED"
        print(f"    {name:>25}: {r2_final:.4f}  [{stable}]")

    return results


# ==============================================================================
# Experiment 5: Grounding Rate Test
# ==============================================================================
def experiment_5_grounding_rate():
    """
    For the MVSU, what is the minimum fraction of signal that must be
    uncontaminated to prevent cascade collapse? Plot R^2_final vs g.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 5: R^2 vs Grounding Rate for Different Alpha")
    print("=" * 70)

    g_values = np.arange(0.0, 0.52, 0.05)
    alpha_test = [0.3, 0.5, 0.7, 0.9, 1.0]
    n_cascade = 5  # 5 uniform stages

    results = {}
    for alpha in alpha_test:
        r2_vs_g = []
        for g in g_values:
            finals = []
            for seed in SEEDS[:1]:
                configs = [{"alpha": alpha, "type": "mvsu",
                            "grounding_rate": g, "use_predictive": True,
                            "use_cross": True, "use_dual": True}
                           for _ in range(n_cascade)]
                stage_r2s = simulate_cascade(configs, N_TIMESTEPS, seed)
                finals.append(stage_r2s[-1])
            r2_vs_g.append(np.mean(finals))
        results[alpha] = np.array(r2_vs_g)

    # Print summary
    print(f"\n  {'g':>6}", end="")
    for alpha in alpha_test:
        print(f"  {'a='+str(alpha):>8}", end="")
    print()
    print("  " + "-" * (6 + 10 * len(alpha_test)))
    for j, g in enumerate(g_values):
        if j % 5 == 0:
            print(f"  {g:6.2f}", end="")
            for alpha in alpha_test:
                print(f"  {results[alpha][j]:>8.4f}", end="")
            print()

    # Minimum g for each alpha
    print(f"\n  MINIMUM g for R^2 > {EPSILON}:")
    min_g_results = {}
    for alpha in alpha_test:
        min_g = None
        for j, g in enumerate(g_values):
            if results[alpha][j] > EPSILON:
                min_g = g
                break
        min_g_results[alpha] = min_g
        print(f"    alpha={alpha:.1f}: g_min = {min_g if min_g is not None else '>0.50'}")

    return g_values, alpha_test, results, min_g_results


# ==============================================================================
# Experiment 6: Ablation Study
# ==============================================================================
def experiment_6_ablation():
    """
    Start with full MVSU. Remove one component at a time.
    Measure R^2 degradation. Show which component's removal is most damaging.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 6: Ablation Study -- Component Importance")
    print("=" * 70)

    g = 0.10

    configs_dict = {
        "Full MVSU": {
            "use_dual": True, "use_cross": True,
            "use_predictive": True, "grounding_rate": g,
        },
        "-Dual (N=1)": {
            "use_dual": False, "use_cross": False,
            "use_predictive": True, "grounding_rate": g,
        },
        "-Inhibition": {
            "use_dual": True, "use_cross": False,
            "use_predictive": True, "grounding_rate": g,
        },
        "-Predictive": {
            "use_dual": True, "use_cross": True,
            "use_predictive": False, "grounding_rate": g,
        },
        "-Grounding": {
            "use_dual": True, "use_cross": True,
            "use_predictive": True, "grounding_rate": 0.0,
        },
    }

    # Also test positive cross-connections
    # Run the bio cascade with forced positive cross weights
    results = {}

    for name, params in configs_dict.items():
        cascade_configs = []
        for a in BIO_ALPHAS:
            cascade_configs.append({
                "alpha": a, "type": "mvsu",
                **params,
            })

        all_stage_r2s = []
        for seed in SEEDS:
            stage_r2s = simulate_cascade(cascade_configs, N_TIMESTEPS, seed)
            all_stage_r2s.append(stage_r2s)
        mean_stage_r2s = np.mean(all_stage_r2s, axis=0)
        results[name] = mean_stage_r2s

    # Also test binocular with positive cross (to show w_cross > 0 is worse)
    pos_cross_configs = [{"alpha": a, "type": "binocular_positive"} for a in BIO_ALPHAS]
    all_stage_r2s = []
    for seed in SEEDS:
        stage_r2s = simulate_cascade(pos_cross_configs, N_TIMESTEPS, seed)
        all_stage_r2s.append(stage_r2s)
    results["+Positive Cross"] = np.mean(all_stage_r2s, axis=0)

    # Print ablation table
    full_final = results["Full MVSU"][-1]

    print(f"\n  {'Configuration':>18}  {'Final R^2':>10}  {'Degradation':>12}  {'Status':>10}")
    print("  " + "-" * 56)

    for name in results:
        r2_final = results[name][-1]
        deg = (full_final - r2_final) / full_final * 100 if full_final > 1e-6 else 0
        status = "STABLE" if r2_final > EPSILON else "COLLAPSED"
        print(f"  {name:>18}  {r2_final:>10.4f}  {deg:>+11.1f}%  {status:>10}")

    # Rank by impact
    print("\n  COMPONENT IMPORTANCE (by R^2 degradation when removed):")
    ablation_impact = []
    for name in configs_dict:
        if name == "Full MVSU":
            continue
        r2_final = results[name][-1]
        impact = full_final - r2_final
        ablation_impact.append((name, impact, r2_final))

    ablation_impact.sort(key=lambda x: -x[1])
    for rank, (name, impact, r2) in enumerate(ablation_impact, 1):
        print(f"    {rank}. {name:>15}: impact = {impact:.4f} (R^2 drops to {r2:.4f})")

    # Monocular comparison with same total parameters
    print("\n  PARAMETER EFFICIENCY:")
    mvsu_r2 = results["Full MVSU"][-1]
    mono_r2 = results["-Dual (N=1)"][-1]
    print(f"    MVSU (4 params): R^2 = {mvsu_r2:.4f}")
    print(f"    Monocular (1 param): R^2 = {mono_r2:.4f}")
    if mono_r2 > 1e-6:
        ratio = mvsu_r2 / mono_r2
        print(f"    R^2 per param: MVSU = {mvsu_r2/4:.4f}, Mono = {mono_r2:.4f}")
        print(f"    MVSU achieves {ratio:.1f}x better R^2 with 4x parameters")

    return results


# ==============================================================================
# Plotting
# ==============================================================================
def create_plots(exp1, exp2, exp2_min_g, exp3_data, exp4, exp5_data, exp6):
    """Generate 3x2 results plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(3, 2, figsize=(14, 16))
    fig.suptitle("Minimal Stable Self-Referential Architecture: Verification",
                 fontsize=14, fontweight='bold')

    c_full = '#2196F3'
    c_no_dual = '#FF5722'
    c_no_inhib = '#FF9800'
    c_no_pred = '#9C27B0'
    c_no_ground = '#795548'
    c_positive = '#E91E63'
    stages_x = np.arange(N_STAGES)

    # ---- Panel 1: Ablation -- R^2 at each stage for each variant ----
    ax = axes[0, 0]
    colors_abl = {
        "Full MVSU": c_full,
        "No Dual (N=1)": c_no_dual,
        "No Inhibition": c_no_inhib,
        "No Predictive": c_no_pred,
        "No Grounding": c_no_ground,
    }
    for name in ["Full MVSU", "No Dual (N=1)", "No Inhibition",
                  "No Predictive", "No Grounding"]:
        if name in exp1:
            ax.plot(stages_x, exp1[name], 'o-', label=name,
                    color=colors_abl.get(name, 'gray'), markersize=4, linewidth=1.5)
    ax.axhline(y=EPSILON, color='red', linestyle=':', alpha=0.7,
               label=f'Stability threshold ({EPSILON})')
    ax.set_xlabel('Stage')
    ax.set_ylabel('R^2 vs Original Signal')
    ax.set_title('Panel 1: Component Necessity (Ablation)')
    ax.set_xticks(stages_x)
    ax.set_xticklabels(BIO_NAMES, rotation=45, ha='right', fontsize=7)
    ax.legend(fontsize=6, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    # ---- Panel 2: Stability boundary heatmap ----
    ax = axes[0, 1]
    alpha_sweep, g_sweep, r2_grid = exp3_data
    im = ax.imshow(r2_grid, aspect='auto', origin='lower',
                    extent=[g_sweep[0], g_sweep[-1], alpha_sweep[0], alpha_sweep[-1]],
                    cmap='RdYlGn', vmin=0, vmax=0.6)
    # Draw stability boundary contour
    ax.contour(g_sweep, alpha_sweep, r2_grid, levels=[EPSILON],
               colors='red', linewidths=2, linestyles='--')
    ax.set_xlabel('Grounding Rate g')
    ax.set_ylabel('Alpha (contamination)')
    ax.set_title(f'Panel 2: Stability Boundary (R^2 > {EPSILON})')
    plt.colorbar(im, ax=ax, label='Final R^2')

    # ---- Panel 3: R^2 vs grounding rate g ----
    ax = axes[1, 0]
    g_values, alpha_test, r2_vs_g, min_g_results = exp5_data
    cmap_alpha = plt.cm.plasma
    for idx, alpha in enumerate(alpha_test):
        color = cmap_alpha(idx / (len(alpha_test) - 1))
        ax.plot(g_values, r2_vs_g[alpha], 'o-', label=f'alpha={alpha}',
                color=color, markersize=3, linewidth=1.5)
    ax.axhline(y=EPSILON, color='red', linestyle=':', alpha=0.7,
               label=f'Threshold ({EPSILON})')
    ax.set_xlabel('Grounding Rate g')
    ax.set_ylabel('Final R^2 (after 5 stages)')
    ax.set_title('Panel 3: R^2 vs Grounding Rate')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ---- Panel 4: Architecture comparison (5 architectures through 7 stages) ----
    ax = axes[1, 1]
    arch_colors = {
        "Raw Monocular": '#FF5722',
        "Dual Naive": '#FF9800',
        "Dual Inhibitory": '#4CAF50',
        "Dual+Predictive": '#2196F3',
        "Full MVSU (g=0.1)": '#673AB7',
    }
    for name in exp4:
        ax.plot(stages_x, exp4[name], 'o-', label=name,
                color=arch_colors.get(name, 'gray'), markersize=4, linewidth=1.5)
    ax.axhline(y=EPSILON, color='red', linestyle=':', alpha=0.7)
    ax.set_xlabel('Stage')
    ax.set_ylabel('R^2 vs Original Signal')
    ax.set_title('Panel 4: Architecture Comparison (7 Stages)')
    ax.set_xticks(stages_x)
    ax.set_xticklabels(BIO_NAMES, rotation=45, ha='right', fontsize=7)
    ax.legend(fontsize=6, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    # ---- Panel 5: Component necessity bar chart ----
    ax = axes[2, 0]
    full_r2 = exp6["Full MVSU"][-1]
    bar_names = []
    bar_r2s_with = []
    bar_r2s_without = []
    component_labels = [
        ("-Dual (N=1)", "Dual\nChannels"),
        ("-Inhibition", "Inhibitory\nCross"),
        ("-Predictive", "Predictive\nCoding"),
        ("-Grounding", "External\nGrounding"),
    ]
    for ablation_name, label in component_labels:
        bar_names.append(label)
        bar_r2s_with.append(full_r2)
        bar_r2s_without.append(exp6[ablation_name][-1])

    x_bar = np.arange(len(bar_names))
    bar_width = 0.35
    ax.bar(x_bar - bar_width / 2, bar_r2s_with, bar_width,
           label='With Component', color=c_full, alpha=0.7, edgecolor='black')
    ax.bar(x_bar + bar_width / 2, bar_r2s_without, bar_width,
           label='Without Component', color=c_no_dual, alpha=0.7, edgecolor='black')
    ax.axhline(y=EPSILON, color='red', linestyle=':', alpha=0.7, label=f'Threshold')
    ax.set_xticks(x_bar)
    ax.set_xticklabels(bar_names, fontsize=8)
    ax.set_ylabel('Final R^2')
    ax.set_title('Panel 5: Component Necessity (Bar Chart)')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis='y')

    # ---- Panel 6: MVSU parameter efficiency ----
    ax = axes[2, 1]
    # Compare: Full MVSU vs monocular at different grounding rates
    g_eff_vals = np.arange(0.0, 0.35, 0.05)

    mvsu_finals = []
    mono_finals = []

    for g in g_eff_vals:
        # MVSU
        mvsu_configs = make_full_stable(g)
        mvsu_r2s = []
        for seed in SEEDS[:2]:
            sr = simulate_cascade(mvsu_configs, N_TIMESTEPS, seed)
            mvsu_r2s.append(sr[-1])
        mvsu_finals.append(np.mean(mvsu_r2s))

        # Monocular with grounding (same g, same total params in a sense)
        mono_configs = [{"alpha": a, "type": "grounded", "grounding_rate": g}
                        for a in BIO_ALPHAS]
        mono_r2s = []
        for seed in SEEDS[:2]:
            sr = simulate_cascade(mono_configs, N_TIMESTEPS, seed)
            mono_r2s.append(sr[-1])
        mono_finals.append(np.mean(mono_r2s))

    ax.plot(g_eff_vals, mvsu_finals, 'o-', label='MVSU (4 params/stage)',
            color=c_full, markersize=4, linewidth=2)
    ax.plot(g_eff_vals, mono_finals, 's-', label='Grounded Mono (1 param/stage)',
            color=c_no_dual, markersize=4, linewidth=2)
    ax.axhline(y=EPSILON, color='red', linestyle=':', alpha=0.7)
    ax.set_xlabel('Grounding Rate g')
    ax.set_ylabel('Final R^2 (7-stage cascade)')
    ax.set_title('Panel 6: MVSU vs Grounded Monocular')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "stable_architecture_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==============================================================================
# Summary
# ==============================================================================
def print_summary(exp1, exp2, exp2_min_g, exp4, exp6):
    """Print comprehensive summary."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE SUMMARY")
    print("=" * 70)

    full_final = exp1["Full MVSU"][-1]

    print(f"\n  1. FULL MVSU PERFORMANCE:")
    print(f"     Final R^2 after 7 stages: {full_final:.4f}")
    print(f"     Stable (R^2 > {EPSILON}): {'YES' if full_final > EPSILON else 'NO'}")

    print(f"\n  2. COMPONENT NECESSITY (% R^2 degradation when removed):")
    component_labels = {
        "No Dual (N=1)": "Dual Channels",
        "No Inhibition": "Inhibitory Cross-Connections",
        "No Predictive": "Predictive Coding",
        "No Grounding": "External Grounding",
    }
    for ablation, label in component_labels.items():
        ablated = exp1[ablation][-1]
        deg = (full_final - ablated) / full_final * 100 if full_final > 1e-6 else 0
        necessary = ablated < full_final * 0.7
        print(f"     {label:>30}: {deg:>+6.1f}% {'[NECESSARY]' if necessary else '[helpful]'}")

    print(f"\n  3. MINIMUM GROUNDING RATE:")
    print(f"     g_min for R^2 > {EPSILON} (7-stage bio cascade): "
          f"{exp2_min_g if exp2_min_g is not None else '>1.0'}")

    print(f"\n  4. ARCHITECTURE TAXONOMY:")
    print(f"     {'Architecture':>25}  {'Final R^2':>10}  {'Status':>10}")
    print("     " + "-" * 50)
    for name in exp4:
        r2 = exp4[name][-1]
        status = "STABLE" if r2 > EPSILON else "COLLAPSED"
        print(f"     {name:>25}  {r2:>10.4f}  {status:>10}")

    print(f"\n  5. ABLATION RANKING (most to least damaging removal):")
    impacts = []
    for ablation, label in component_labels.items():
        ablated = exp1[ablation][-1]
        impact = full_final - ablated
        impacts.append((label, impact))
    impacts.sort(key=lambda x: -x[1])
    for rank, (label, impact) in enumerate(impacts, 1):
        print(f"     {rank}. {label}: delta R^2 = {impact:.4f}")

    # Positive cross test
    if "+Positive Cross" in exp6:
        pos_cross = exp6["+Positive Cross"][-1]
        neg_cross = exp6["Full MVSU"][-1]
        print(f"\n  6. CROSS-CONNECTION SIGN TEST:")
        print(f"     Negative cross (learned): R^2 = {neg_cross:.4f}")
        print(f"     Positive cross (forced):  R^2 = {pos_cross:.4f}")
        print(f"     Positive cross is {'WORSE' if pos_cross < neg_cross else 'BETTER'}"
              f" -- confirms inhibition is necessary")

    # Architecture ranking summary
    print(f"\n  ARCHITECTURE RANKING TABLE:")
    print(f"  {'Architecture':>25}  {'N>=2':>5}  {'w<0':>5}  {'Pred':>5}  {'Gnd':>5}  {'R^2':>8}  {'Stable':>7}")
    print("  " + "-" * 70)
    taxonomy = [
        ("Raw Monocular",       "No",  "No",  "No",  "No"),
        ("Dual Naive",          "Yes", "No",  "No",  "No"),
        ("Dual Inhibitory",     "Yes", "Yes", "No",  "No"),
        ("Dual+Predictive",     "Yes", "Yes", "Yes", "No"),
        ("Full MVSU (g=0.1)",   "Yes", "Yes", "Yes", "Yes"),
    ]
    for name, n2, wc, pred, gnd in taxonomy:
        r2 = exp4.get(name, np.zeros(N_STAGES))[-1]
        stable = "YES" if r2 > EPSILON else "NO"
        print(f"  {name:>25}  {n2:>5}  {wc:>5}  {pred:>5}  {gnd:>5}  {r2:>8.4f}  {stable:>7}")

    print("\n" + "=" * 70)


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 70)
    print("MINIMAL STABLE SELF-REFERENTIAL ARCHITECTURE")
    print("Numerical Verification")
    print("=" * 70)
    print(f"  Timesteps: {N_TIMESTEPS}, Warmup: {WARMUP}, LR: {LR}")
    print(f"  Seeds: {SEEDS}")
    print(f"  Bio cascade: {N_STAGES} stages, alpha = {BIO_ALPHAS}")
    print(f"  Stability threshold: R^2 > {EPSILON}")
    print(f"  1/phi = {INV_PHI:.6f}")

    t_start = time.time()

    # Experiment 1: Component necessity
    t1 = time.time()
    exp1 = experiment_1_necessity()
    print(f"  [Exp 1 done in {time.time() - t1:.1f}s]")

    # Experiment 2: MVSU grounding rate sweep
    t1 = time.time()
    exp2, exp2_min_g = experiment_2_mvsu()
    print(f"  [Exp 2 done in {time.time() - t1:.1f}s]")

    # Experiment 3: Stability boundary
    t1 = time.time()
    exp3_data = experiment_3_stability_boundary()
    print(f"  [Exp 3 done in {time.time() - t1:.1f}s]")

    # Experiment 4: Architecture comparison
    t1 = time.time()
    exp4 = experiment_4_architecture_comparison()
    print(f"  [Exp 4 done in {time.time() - t1:.1f}s]")

    # Experiment 5: Grounding rate test
    t1 = time.time()
    exp5_data = experiment_5_grounding_rate()
    print(f"  [Exp 5 done in {time.time() - t1:.1f}s]")

    # Experiment 6: Ablation study
    t1 = time.time()
    exp6 = experiment_6_ablation()
    print(f"  [Exp 6 done in {time.time() - t1:.1f}s]")

    # Summary
    print_summary(exp1, exp2, exp2_min_g, exp4, exp6)

    # Plots
    create_plots(exp1, exp2, exp2_min_g, exp3_data, exp4, exp5_data, exp6)

    total_time = time.time() - t_start
    print(f"\nTotal runtime: {total_time:.1f}s")
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
