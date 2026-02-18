"""
Self-Referential Prediction Experiment
=======================================
Tests Ouroboros optimization predictions by examining a predictor that
influences what it predicts.

Model:
    x_{t+1} = (1-alpha)*f(x_t) + alpha*P(x_t) + sigma*noise_t

Where:
    - f(x_t) is natural dynamics (logistic, sine, tent maps)
    - P(x_t) is the agent's prediction
    - alpha controls self-reference strength
    - The agent minimizes prediction error via online SGD

Key question: Does prediction quality vs alpha deviate from the null
hypothesis (1-alpha)^2 scaling in phi-related ways?

Author: Claude (experiment design from Ouroboros framework)
"""

import sys
import io
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

# ==============================================================================
# Constants
# ==============================================================================
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ~1.618
INV_PHI = 1.0 / PHI          # ~0.618
INV_PHI2 = 1.0 / PHI**2      # ~0.382

SIGMA = 0.05           # Noise scale
N_STEPS = 20000        # Total time steps per run
BURN_IN = 5000         # Steps before measurement
N_MEASURE = N_STEPS - BURN_IN
ALPHA_VALUES = np.linspace(0, 1, 21)
SEEDS = [42, 137, 256, 314, 999]
MLP_SEEDS = [42, 137, 256]  # Fewer seeds for MLP (slower)
LR_LINEAR = 0.01       # Learning rate for linear predictor
LR_MLP = 0.003         # Learning rate for MLP predictor
MLP_HIDDEN = 16         # Hidden units in MLP


# ==============================================================================
# Natural dynamics
# ==============================================================================
def logistic_map(x):
    """Logistic map with r=3.7 (chaotic regime)."""
    return 3.7 * x * (1.0 - x)

def sine_map(x):
    """Sine map: sin(pi * x)."""
    return np.sin(np.pi * x)

def tent_map(x):
    """Tent map: 1 - 2*|x - 0.5|."""
    return 1.0 - 2.0 * abs(x - 0.5)

DYNAMICS = {
    "Logistic (r=3.7)": logistic_map,
    "Sine": sine_map,
    "Tent": tent_map,
}


# ==============================================================================
# Simulation - Linear Predictor (optimized tight loop)
# ==============================================================================
def run_linear(dynamics_fn, alpha, seed):
    """
    Run simulation with linear predictor P(x) = w*x + b.

    Gradient accounting for self-reference:
        loss = (x_next - P(x_t))^2 = ((1-alpha)*(f(x_t) - P(x_t)) + noise)^2
        d(loss)/d(P) = -2*(1-alpha)*(x_next - P(x_t))
    """
    rng = np.random.RandomState(seed)

    # Initialize predictor
    w = rng.normal(0, 0.1)
    b = rng.normal(0, 0.1)

    # Pre-generate all noise
    all_noise = SIGMA * rng.randn(N_STEPS)

    x = 0.5
    one_minus_alpha = 1.0 - alpha
    lr = LR_LINEAR

    # Storage for measurement phase
    pred_sum = 0.0
    pred_sq_sum = 0.0
    actual_sum = 0.0
    actual_sq_sum = 0.0
    error_sq_sum = 0.0
    n_meas = 0

    for t in range(N_STEPS):
        pred = w * x + b
        f_x = dynamics_fn(x)
        x_next = one_minus_alpha * f_x + alpha * pred + all_noise[t]

        # Clamp to [0, 1]
        if x_next < 0.0:
            x_next = 0.0
        elif x_next > 1.0:
            x_next = 1.0

        # Update predictor with self-reference-aware gradient
        error = x_next - pred
        grad_factor = -2.0 * one_minus_alpha * error
        w -= lr * grad_factor * x
        b -= lr * grad_factor

        # Record during measurement phase
        if t >= BURN_IN:
            error_sq_sum += error * error
            actual_sum += x_next
            actual_sq_sum += x_next * x_next
            n_meas += 1

        x = x_next

    # Compute metrics
    mse = error_sq_sum / n_meas
    mean_actual = actual_sum / n_meas
    var_actual = actual_sq_sum / n_meas - mean_actual * mean_actual

    if var_actual > 1e-12:
        r2 = 1.0 - mse / var_actual
        oracle_r2 = 1.0 - SIGMA**2 / var_actual
    else:
        r2 = 0.0
        oracle_r2 = 0.0

    normalized = r2 / oracle_r2 if oracle_r2 > 1e-12 else 0.0

    return {"r2": r2, "mse": mse, "var": var_actual, "oracle_r2": oracle_r2, "normalized": normalized}


# ==============================================================================
# Simulation - MLP Predictor
# ==============================================================================
def run_mlp(dynamics_fn, alpha, seed):
    """
    Run simulation with MLP predictor: 1 hidden layer, tanh activation.
    Input: scalar x -> output: scalar P(x)
    """
    rng = np.random.RandomState(seed)
    hidden = MLP_HIDDEN

    # Initialize MLP weights
    W1 = rng.normal(0, 0.5, size=hidden)
    b1 = np.zeros(hidden)
    W2 = rng.normal(0, 0.5 / np.sqrt(hidden), size=hidden)
    b2 = 0.0

    # Pre-allocate
    z1 = np.empty(hidden)
    a1 = np.empty(hidden)
    da1 = np.empty(hidden)
    dz1 = np.empty(hidden)

    all_noise = SIGMA * rng.randn(N_STEPS)

    x = 0.5
    one_minus_alpha = 1.0 - alpha
    lr = LR_MLP
    max_grad = 1.0

    error_sq_sum = 0.0
    actual_sum = 0.0
    actual_sq_sum = 0.0
    n_meas = 0

    for t in range(N_STEPS):
        # Forward pass
        np.multiply(W1, x, out=z1)
        np.add(z1, b1, out=z1)
        np.tanh(z1, out=a1)
        pred = np.dot(W2, a1) + b2

        f_x = dynamics_fn(x)
        x_next = one_minus_alpha * f_x + alpha * pred + all_noise[t]

        if x_next < 0.0:
            x_next = 0.0
        elif x_next > 1.0:
            x_next = 1.0

        # Backward pass with self-reference correction
        error = x_next - pred
        dloss_dpred = -2.0 * one_minus_alpha * error

        # Output layer gradients
        dW2 = dloss_dpred * a1
        db2_val = dloss_dpred
        np.multiply(dloss_dpred, W2, out=da1)

        # Through tanh
        np.multiply(a1, a1, out=dz1)
        np.subtract(1.0, dz1, out=dz1)
        np.multiply(da1, dz1, out=dz1)

        # Input layer gradients
        dW1 = dz1 * x
        db1_grad = dz1

        # Clip
        np.clip(dW1, -max_grad, max_grad, out=dW1)
        np.clip(db1_grad, -max_grad, max_grad, out=db1_grad)
        np.clip(dW2, -max_grad, max_grad, out=dW2)
        db2_val = min(max(db2_val, -max_grad), max_grad)

        # Update
        W1 -= lr * dW1
        b1 -= lr * db1_grad
        W2 -= lr * dW2
        b2 -= lr * db2_val

        if t >= BURN_IN:
            error_sq_sum += error * error
            actual_sum += x_next
            actual_sq_sum += x_next * x_next
            n_meas += 1

        x = x_next

    mse = error_sq_sum / n_meas
    mean_actual = actual_sum / n_meas
    var_actual = actual_sq_sum / n_meas - mean_actual * mean_actual

    if var_actual > 1e-12:
        r2 = 1.0 - mse / var_actual
        oracle_r2 = 1.0 - SIGMA**2 / var_actual
    else:
        r2 = 0.0
        oracle_r2 = 0.0

    normalized = r2 / oracle_r2 if oracle_r2 > 1e-12 else 0.0

    return {"r2": r2, "mse": mse, "var": var_actual, "oracle_r2": oracle_r2, "normalized": normalized}


# ==============================================================================
# Aggregation helper
# ==============================================================================
def aggregate_seeds(seed_results):
    """Compute mean and std for each metric across seeds."""
    metrics = {}
    for key in ["r2", "mse", "var", "oracle_r2", "normalized"]:
        vals = [r[key] for r in seed_results]
        metrics[f"{key}_mean"] = np.mean(vals)
        metrics[f"{key}_std"] = np.std(vals)
    return metrics


# ==============================================================================
# Main experiment
# ==============================================================================
def run_experiment():
    """Run full alpha sweep across all dynamics and predictor types."""

    results = {}

    print("=" * 78)
    print("SELF-REFERENTIAL PREDICTION EXPERIMENT")
    print("=" * 78)
    print(f"  Model: x_{{t+1}} = (1-alpha)*f(x_t) + alpha*P(x_t) + sigma*noise_t")
    print(f"  Time steps: {N_STEPS} (burn-in: {BURN_IN}, measurement: {N_MEASURE})")
    print(f"  Noise sigma: {SIGMA}")
    print(f"  Alpha values: {len(ALPHA_VALUES)} points from 0.0 to 1.0")
    print(f"  Seeds (linear): {SEEDS}")
    print(f"  Seeds (MLP): {MLP_SEEDS}")
    print(f"  Dynamics: {', '.join(DYNAMICS.keys())}")
    print(f"  Predictors: Linear, MLP ({MLP_HIDDEN} hidden units)")
    n_linear = len(DYNAMICS) * len(ALPHA_VALUES) * len(SEEDS)
    n_mlp = len(DYNAMICS) * len(ALPHA_VALUES) * len(MLP_SEEDS)
    print(f"  Total runs: {n_linear} linear + {n_mlp} MLP = {n_linear + n_mlp}")
    print(f"  phi constants: 1/phi = {INV_PHI:.6f}, 1/phi^2 = {INV_PHI2:.6f}")
    print()
    sys.stdout.flush()

    t_start = time.time()

    # --- Linear predictor runs ---
    print("Running linear predictor...")
    sys.stdout.flush()
    combo = 0
    for dyn_name, dyn_fn in DYNAMICS.items():
        for alpha in ALPHA_VALUES:
            combo += 1
            seed_results = [run_linear(dyn_fn, alpha, s) for s in SEEDS]
            results[(dyn_name, "Linear", alpha)] = aggregate_seeds(seed_results)

        elapsed = time.time() - t_start
        print(f"  {dyn_name}: done ({elapsed:.1f}s)")
        sys.stdout.flush()

    # --- MLP predictor runs ---
    print("Running MLP predictor...")
    sys.stdout.flush()
    for dyn_name, dyn_fn in DYNAMICS.items():
        for alpha in ALPHA_VALUES:
            seed_results = [run_mlp(dyn_fn, alpha, s) for s in MLP_SEEDS]
            results[(dyn_name, "MLP", alpha)] = aggregate_seeds(seed_results)

        elapsed = time.time() - t_start
        print(f"  {dyn_name}: done ({elapsed:.1f}s)")
        sys.stdout.flush()

    elapsed = time.time() - t_start
    print(f"\nAll runs completed in {elapsed:.1f}s")
    print()
    sys.stdout.flush()

    return results


def analyze_results(results):
    """Analyze and print results tables."""

    # =========================================================================
    # Table 1: R^2 vs alpha for each dynamics (linear predictor)
    # =========================================================================
    print("=" * 78)
    print("TABLE 1: Prediction R^2 vs Alpha (Linear Predictor)")
    print("=" * 78)

    for dyn_name in DYNAMICS.keys():
        print(f"\n--- {dyn_name} ---")
        print(f"{'Alpha':>7s}  {'R^2':>12s}  {'Oracle R^2':>12s}  {'Normalized':>12s}  {'Null Hyp':>10s}  {'Residual':>10s}")
        print("-" * 72)

        norm_alpha0 = results[(dyn_name, "Linear", 0.0)]["normalized_mean"]

        for alpha in ALPHA_VALUES:
            m = results[(dyn_name, "Linear", alpha)]
            null_hyp = (1 - alpha)**2 * norm_alpha0
            residual = m["normalized_mean"] - null_hyp

            marker = ""
            if abs(alpha - INV_PHI2) < 0.03:
                marker = " <-- 1/phi^2"
            elif abs(alpha - INV_PHI) < 0.03:
                marker = " <-- 1/phi"

            print(f"{alpha:7.3f}  "
                  f"{m['r2_mean']:8.4f}+/-{m['r2_std']:.4f}"
                  f"  {m['oracle_r2_mean']:8.4f}+/-{m['oracle_r2_std']:.4f}"
                  f"  {m['normalized_mean']:8.4f}+/-{m['normalized_std']:.4f}"
                  f"  {null_hyp:10.4f}"
                  f"  {residual:+10.4f}"
                  f"{marker}")

    # =========================================================================
    # Table 2: Summary across dynamics
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 2: Summary Across Dynamics (Linear Predictor)")
    print("=" * 78)

    print(f"\n{'Dynamics':<18s} {'Crit alpha':>10s} {'R^2(a=0)':>10s} "
          f"{'R^2(a=.382)':>11s} {'R^2(a=.618)':>11s} {'R^2(a=1)':>10s}")
    print("-" * 78)

    for dyn_name in DYNAMICS.keys():
        # Find critical alpha where normalized quality drops below 0.5
        crit_alpha = 1.0
        for alpha in ALPHA_VALUES:
            m = results[(dyn_name, "Linear", alpha)]
            if m["normalized_mean"] < 0.5:
                crit_alpha = alpha
                break

        r2_0 = results[(dyn_name, "Linear", 0.0)]["r2_mean"]

        a_382 = ALPHA_VALUES[np.argmin(np.abs(ALPHA_VALUES - INV_PHI2))]
        a_618 = ALPHA_VALUES[np.argmin(np.abs(ALPHA_VALUES - INV_PHI))]

        r2_382 = results[(dyn_name, "Linear", a_382)]["r2_mean"]
        r2_618 = results[(dyn_name, "Linear", a_618)]["r2_mean"]
        r2_1 = results[(dyn_name, "Linear", 1.0)]["r2_mean"]

        print(f"{dyn_name:<18s} {crit_alpha:10.3f} {r2_0:10.4f} "
              f"{r2_382:11.4f} {r2_618:11.4f} {r2_1:10.4f}")

    # =========================================================================
    # Table 3: Linear vs MLP comparison
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 3: Linear vs MLP Predictor Comparison")
    print("=" * 78)

    for dyn_name in DYNAMICS.keys():
        print(f"\n--- {dyn_name} ---")
        print(f"{'Alpha':>7s}  {'Linear R^2':>12s}  {'MLP R^2':>12s}  {'Lin Norm':>10s}  {'MLP Norm':>10s}  {'Diff':>8s}")
        print("-" * 66)

        for alpha in ALPHA_VALUES[::2]:
            ml = results[(dyn_name, "Linear", alpha)]
            mm = results[(dyn_name, "MLP", alpha)]
            diff = mm["normalized_mean"] - ml["normalized_mean"]

            print(f"{alpha:7.3f}  "
                  f"{ml['r2_mean']:8.4f}+/-{ml['r2_std']:.3f}"
                  f"  {mm['r2_mean']:8.4f}+/-{mm['r2_std']:.3f}"
                  f"  {ml['normalized_mean']:10.4f}"
                  f"  {mm['normalized_mean']:10.4f}"
                  f"  {diff:+8.4f}")

    # =========================================================================
    # Table 4: Ouroboros predictions comparison
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 4: Comparison with Ouroboros Predictions")
    print("=" * 78)

    print(f"\nKey phi constants:")
    print(f"  1/phi^2 = {INV_PHI2:.6f}")
    print(f"  1/phi   = {INV_PHI:.6f}")
    print(f"  phi     = {PHI:.6f}")

    print(f"\nNull hypothesis: Normalized quality = (1-alpha)^2 * quality(alpha=0)")
    print(f"  At alpha=1/phi^2 ({INV_PHI2:.3f}): null = (1-{INV_PHI2:.3f})^2 = {(1-INV_PHI2)**2:.6f} = (1/phi)^2 = {INV_PHI**2:.6f}")
    print(f"  At alpha=1/phi   ({INV_PHI:.3f}):  null = (1-{INV_PHI:.3f})^2  = {(1-INV_PHI)**2:.6f} = (1/phi^2)^2 = {INV_PHI2**2:.6f}")

    print(f"\nNote: (1 - 1/phi^2) = 1/phi, and (1 - 1/phi) = 1/phi^2.")
    print(f"  So the null hypothesis has inherent phi structure in its (1-alpha)^2 scaling")
    print(f"  when evaluated at phi-related alpha values. This is mathematical, not physical.")

    a_382 = ALPHA_VALUES[np.argmin(np.abs(ALPHA_VALUES - INV_PHI2))]
    a_618 = ALPHA_VALUES[np.argmin(np.abs(ALPHA_VALUES - INV_PHI))]

    print(f"\n{'Dynamics':<18s} | {'Actual norm(a~.382)':>18s} {'Null(a~.382)':>14s} {'Resid':>8s} | "
          f"{'Actual norm(a~.618)':>18s} {'Null(a~.618)':>14s} {'Resid':>8s}")
    print("-" * 110)

    for dyn_name in DYNAMICS.keys():
        norm_0 = results[(dyn_name, "Linear", 0.0)]["normalized_mean"]

        m382 = results[(dyn_name, "Linear", a_382)]
        null_382 = (1 - a_382)**2 * norm_0
        res_382 = m382["normalized_mean"] - null_382

        m618 = results[(dyn_name, "Linear", a_618)]
        null_618 = (1 - a_618)**2 * norm_0
        res_618 = m618["normalized_mean"] - null_618

        print(f"{dyn_name:<18s} | "
              f"{m382['normalized_mean']:18.6f} {null_382:14.6f} {res_382:+8.4f} | "
              f"{m618['normalized_mean']:18.6f} {null_618:14.6f} {res_618:+8.4f}")

    # =========================================================================
    # Detailed residual analysis
    # =========================================================================
    print("\n" + "=" * 78)
    print("RESIDUAL ANALYSIS: Actual Normalized Quality - Null Hypothesis")
    print("=" * 78)

    all_rms_residuals = []

    for dyn_name in DYNAMICS.keys():
        print(f"\n--- {dyn_name} (Linear Predictor) ---")
        norm_0 = results[(dyn_name, "Linear", 0.0)]["normalized_mean"]

        max_resid = -np.inf
        max_resid_alpha = 0
        min_resid = np.inf
        min_resid_alpha = 0

        residuals = []
        for alpha in ALPHA_VALUES:
            m = results[(dyn_name, "Linear", alpha)]
            null = (1 - alpha)**2 * norm_0
            resid = m["normalized_mean"] - null
            residuals.append(resid)

            if resid > max_resid:
                max_resid = resid
                max_resid_alpha = alpha
            if resid < min_resid:
                min_resid = resid
                min_resid_alpha = alpha

        residuals = np.array(residuals)
        rms = np.sqrt(np.mean(residuals**2))
        all_rms_residuals.append(rms)

        print(f"  Max positive residual: {max_resid:+.6f} at alpha = {max_resid_alpha:.3f}")
        print(f"  Max negative residual: {min_resid:+.6f} at alpha = {min_resid_alpha:.3f}")
        print(f"  Mean absolute residual: {np.mean(np.abs(residuals)):.6f}")
        print(f"  RMS residual: {rms:.6f}")

    # =========================================================================
    # Phase transition analysis
    # =========================================================================
    print("\n" + "=" * 78)
    print("PHASE TRANSITION ANALYSIS")
    print("=" * 78)

    for dyn_name in DYNAMICS.keys():
        print(f"\n--- {dyn_name} ---")
        norms = []
        for alpha in ALPHA_VALUES:
            norms.append(results[(dyn_name, "Linear", alpha)]["normalized_mean"])
        norms = np.array(norms)

        # Compute discrete derivative (slope of normalized quality)
        d_norms = np.diff(norms) / np.diff(ALPHA_VALUES)
        alpha_mid = (ALPHA_VALUES[:-1] + ALPHA_VALUES[1:]) / 2

        # Find steepest descent
        min_idx = np.argmin(d_norms)
        print(f"  Steepest decline at alpha ~ {alpha_mid[min_idx]:.3f} (slope = {d_norms[min_idx]:.4f})")

        # Second derivative (curvature) - inflection points
        if len(d_norms) > 1:
            d2_norms = np.diff(d_norms) / np.diff(alpha_mid)
            alpha_mid2 = (alpha_mid[:-1] + alpha_mid[1:]) / 2

            # Sign changes in second derivative = inflection points
            sign_changes = []
            for i in range(len(d2_norms) - 1):
                if d2_norms[i] * d2_norms[i+1] < 0:
                    sign_changes.append(alpha_mid2[i])

            if sign_changes:
                print(f"  Inflection points at alpha ~ {[f'{a:.3f}' for a in sign_changes]}")
            else:
                print(f"  No clear inflection points detected")

    # =========================================================================
    # Honest assessment
    # =========================================================================
    print("\n" + "=" * 78)
    print("HONEST ASSESSMENT")
    print("=" * 78)

    mean_rms = np.mean(all_rms_residuals)

    print(f"\n1. NULL HYPOTHESIS CHECK:")
    print(f"   Mean RMS residual across dynamics: {mean_rms:.6f}")
    if mean_rms < 0.05:
        print(f"   --> Residuals are SMALL (<0.05). The (1-alpha)^2 null hypothesis explains")
        print(f"       most of the variation. Self-reference reduces signal as (1-alpha)^2,")
        print(f"       which is the expected algebraic result from the model structure.")
    else:
        print(f"   --> Residuals are SIGNIFICANT (>0.05). There are meaningful deviations")
        print(f"       from the null hypothesis that require explanation.")

    print(f"\n2. PHI-RELATED STRUCTURE:")
    for dyn_name in DYNAMICS.keys():
        norm_0 = results[(dyn_name, "Linear", 0.0)]["normalized_mean"]
        residuals = []
        for alpha in ALPHA_VALUES:
            m = results[(dyn_name, "Linear", alpha)]
            null = (1 - alpha)**2 * norm_0
            residuals.append(m["normalized_mean"] - null)
        residuals = np.array(residuals)

        idx_382 = np.argmin(np.abs(ALPHA_VALUES - INV_PHI2))
        idx_618 = np.argmin(np.abs(ALPHA_VALUES - INV_PHI))

        resid_382 = residuals[idx_382]
        resid_618 = residuals[idx_618]
        resid_std = np.std(residuals[1:-1])

        print(f"\n   {dyn_name}:")
        print(f"     Residual at alpha~0.382: {resid_382:+.6f} ({resid_382/resid_std if resid_std > 1e-12 else 0:+.2f} sigma)")
        print(f"     Residual at alpha~0.618: {resid_618:+.6f} ({resid_618/resid_std if resid_std > 1e-12 else 0:+.2f} sigma)")

    print(f"\n3. LINEAR vs MLP CEILING:")
    for dyn_name in DYNAMICS.keys():
        lin_norms = []
        mlp_norms = []
        for alpha in ALPHA_VALUES:
            lin_norms.append(results[(dyn_name, "Linear", alpha)]["normalized_mean"])
            mlp_norms.append(results[(dyn_name, "MLP", alpha)]["normalized_mean"])
        lin_norms = np.array(lin_norms)
        mlp_norms = np.array(mlp_norms)
        mean_diff = np.mean(mlp_norms - lin_norms)
        max_diff = np.max(np.abs(mlp_norms - lin_norms))
        print(f"   {dyn_name}: MLP - Linear mean diff = {mean_diff:+.4f}, max |diff| = {max_diff:.4f}")

    # Check if MLP and linear follow similar curves (structural constraint)
    print(f"\n   If MLP and linear have similar normalized quality vs alpha curves,")
    print(f"   the ceiling is STRUCTURAL (from self-reference), not about predictor capacity.")

    print(f"\n4. MATHEMATICAL NOTE:")
    print(f"   The null hypothesis (1-alpha)^2 has INHERENT phi structure:")
    print(f"   - At alpha = 1/phi^2: (1-alpha)^2 = (1/phi)^2 = 1/phi^2 = {INV_PHI2:.6f}")
    print(f"   - At alpha = 1/phi:   (1-alpha)^2 = (1/phi^2)^2 = 1/phi^4 = {1/PHI**4:.6f}")
    print(f"   Any apparent phi-structure in R^2 vs alpha could simply reflect")
    print(f"   the phi-structure inherent in (1-alpha)^2 evaluated at phi points,")
    print(f"   which is algebraic, not physical.")

    print(f"\n5. OVERALL VERDICT:")
    if mean_rms < 0.03:
        print(f"   The data closely follows the null hypothesis (1-alpha)^2 * R^2(alpha=0).")
        print(f"   There is NO evidence of phi-specific structure beyond what the null")
        print(f"   hypothesis algebraically produces. The self-referential dynamics reduce")
        print(f"   predictability exactly as the model structure dictates: effective signal")
        print(f"   scales as (1-alpha)^2, which is a straightforward consequence of the")
        print(f"   linear mixing model, not evidence for Ouroboros optimization.")
    elif mean_rms < 0.10:
        print(f"   There are MODERATE deviations from the null hypothesis. These could")
        print(f"   reflect nonlinear learning dynamics, predictor adaptation effects, or")
        print(f"   genuine self-referential structure. Further analysis with more seeds")
        print(f"   and longer runs would help distinguish signal from noise.")
    else:
        print(f"   There are LARGE deviations from the null hypothesis. The (1-alpha)^2")
        print(f"   model does NOT fully explain the data. Whether this reflects phi-related")
        print(f"   structure or other nonlinear effects requires careful analysis.")

    return results


def make_plots(results):
    """Generate plots if matplotlib is available."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    fig.suptitle("Self-Referential Prediction Experiment", fontsize=14, fontweight="bold")

    colors = {"Logistic (r=3.7)": "#2196F3", "Sine": "#4CAF50", "Tent": "#FF5722"}

    # Panel 1: R^2 vs alpha for all dynamics (linear predictor)
    ax = axes[0, 0]
    for dyn_name in DYNAMICS.keys():
        alphas = []
        r2_means = []
        r2_stds = []
        for alpha in ALPHA_VALUES:
            m = results[(dyn_name, "Linear", alpha)]
            alphas.append(alpha)
            r2_means.append(m["r2_mean"])
            r2_stds.append(m["r2_std"])
        alphas = np.array(alphas)
        r2_means = np.array(r2_means)
        r2_stds = np.array(r2_stds)

        ax.plot(alphas, r2_means, "o-", label=dyn_name, color=colors[dyn_name], markersize=3)
        ax.fill_between(alphas, r2_means - r2_stds, r2_means + r2_stds,
                        alpha=0.2, color=colors[dyn_name])

    ax.axvline(INV_PHI2, color="gray", linestyle="--", alpha=0.7, label=f"1/phi^2={INV_PHI2:.3f}")
    ax.axvline(INV_PHI, color="gray", linestyle=":", alpha=0.7, label=f"1/phi={INV_PHI:.3f}")
    ax.set_xlabel("Alpha (self-reference strength)")
    ax.set_ylabel("Prediction R^2")
    ax.set_title("Panel 1: R^2 vs Alpha (Linear Predictor)")
    ax.legend(fontsize=7)
    ax.set_xlim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)

    # Panel 2: Normalized quality vs alpha with null hypothesis
    ax = axes[0, 1]
    for dyn_name in DYNAMICS.keys():
        alphas = []
        norm_means = []
        norm_stds = []
        for alpha in ALPHA_VALUES:
            m = results[(dyn_name, "Linear", alpha)]
            alphas.append(alpha)
            norm_means.append(m["normalized_mean"])
            norm_stds.append(m["normalized_std"])
        alphas = np.array(alphas)
        norm_means = np.array(norm_means)
        norm_stds = np.array(norm_stds)

        ax.plot(alphas, norm_means, "o-", label=dyn_name, color=colors[dyn_name], markersize=3)
        ax.fill_between(alphas, norm_means - norm_stds, norm_means + norm_stds,
                        alpha=0.2, color=colors[dyn_name])

    null_curve = (1 - ALPHA_VALUES)**2
    ax.plot(ALPHA_VALUES, null_curve, "k--", linewidth=2, label="Null: (1-alpha)^2", alpha=0.7)

    ax.axvline(INV_PHI2, color="gray", linestyle="--", alpha=0.5)
    ax.axvline(INV_PHI, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Alpha (self-reference strength)")
    ax.set_ylabel("Normalized Prediction Quality")
    ax.set_title("Panel 2: Normalized Quality vs Alpha")
    ax.legend(fontsize=7)
    ax.set_xlim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)

    # Panel 3: Residual (actual - null hypothesis)
    ax = axes[1, 0]
    for dyn_name in DYNAMICS.keys():
        norm_0 = results[(dyn_name, "Linear", 0.0)]["normalized_mean"]
        alphas = []
        residuals = []
        for alpha in ALPHA_VALUES:
            m = results[(dyn_name, "Linear", alpha)]
            null = (1 - alpha)**2 * norm_0
            alphas.append(alpha)
            residuals.append(m["normalized_mean"] - null)
        alphas = np.array(alphas)
        residuals = np.array(residuals)

        ax.plot(alphas, residuals, "o-", label=dyn_name, color=colors[dyn_name], markersize=3)

    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(INV_PHI2, color="gray", linestyle="--", alpha=0.7, label=f"1/phi^2")
    ax.axvline(INV_PHI, color="gray", linestyle=":", alpha=0.7, label=f"1/phi")
    ax.set_xlabel("Alpha (self-reference strength)")
    ax.set_ylabel("Residual (Actual - Null)")
    ax.set_title("Panel 3: Residual from Null Hypothesis")
    ax.legend(fontsize=7)
    ax.set_xlim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)

    # Panel 4: Linear vs MLP comparison (Logistic map)
    ax = axes[1, 1]
    dyn_name = "Logistic (r=3.7)"
    for pred_name, style, color in [("Linear", "o-", "#2196F3"), ("MLP", "s-", "#E91E63")]:
        alphas = []
        norm_means = []
        norm_stds = []
        for alpha in ALPHA_VALUES:
            m = results[(dyn_name, pred_name, alpha)]
            alphas.append(alpha)
            norm_means.append(m["normalized_mean"])
            norm_stds.append(m["normalized_std"])
        alphas = np.array(alphas)
        norm_means = np.array(norm_means)
        norm_stds = np.array(norm_stds)

        ax.plot(alphas, norm_means, style, label=pred_name, color=color, markersize=3)
        ax.fill_between(alphas, norm_means - norm_stds, norm_means + norm_stds,
                        alpha=0.2, color=color)

    null_curve = (1 - ALPHA_VALUES)**2
    ax.plot(ALPHA_VALUES, null_curve, "k--", linewidth=2, label="Null: (1-alpha)^2", alpha=0.7)

    ax.axvline(INV_PHI2, color="gray", linestyle="--", alpha=0.5)
    ax.axvline(INV_PHI, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Alpha (self-reference strength)")
    ax.set_ylabel("Normalized Prediction Quality")
    ax.set_title(f"Panel 4: Linear vs MLP ({dyn_name})")
    ax.legend(fontsize=7)
    ax.set_xlim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    import os
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selfref_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==============================================================================
# Entry point
# ==============================================================================
if __name__ == "__main__":
    print(f"Starting at {time.strftime('%H:%M:%S')}")
    print()

    results = run_experiment()
    analyze_results(results)
    make_plots(results)

    print(f"\nCompleted at {time.strftime('%H:%M:%S')}")
