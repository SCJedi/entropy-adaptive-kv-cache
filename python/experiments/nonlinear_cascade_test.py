"""
Nonlinear Cascade Test
======================
Two experiments testing the robustness and compositional behavior of the
self-referential golden ratio (1/phi) fixed point.

Experiment 1: Nonlinearity Test
    Does the SGD fixed point w ~ 1/phi survive when the agent uses nonlinear
    output functions (tanh, ReLU, sigmoid, quadratic) instead of linear?

Experiment 2: Cascade Test
    In a two-agent hierarchy (A feeds B), does Agent B converge to
    1/phi^2 = 0.382 (cascade), 0.5 (k=2 family), or something else?
    Tests simultaneous, developmental, and echo-subtraction variants.

Author: Claude (experiment design from Ouroboros framework)
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
INV_PHI = 1.0 / PHI            # ~0.618
INV_PHI2 = 1.0 / PHI**2        # ~0.382

N_STEPS = 50000
BURN_IN = 10000
N_MEASURE = N_STEPS - BURN_IN
LR_INIT = 0.01
LR_DECAY = 0.9999
SEEDS = [42, 137, 256, 314, 999]

# True MSE-optimal values (from empiricist analysis)
TRUE_OPT_W = 0.525
TRUE_OPT_R2 = 0.670


# ==============================================================================
# Activation functions and their derivatives
# ==============================================================================
def sigmoid(x):
    """Numerically stable sigmoid."""
    return np.where(x >= 0,
                    1.0 / (1.0 + np.exp(-x)),
                    np.exp(x) / (1.0 + np.exp(x)))


def sigmoid_deriv(x):
    s = sigmoid(x)
    return s * (1.0 - s)


# ==============================================================================
# Experiment 1: Nonlinearity Test
# ==============================================================================
def run_nonlinear_agent(nonlinearity, seed):
    """
    Run a single self-referential agent with specified nonlinearity.

    Agent model:
        y(t) = s(t) + o(t-1)
        o(t) = f(y(t); params)
        Loss = (o(t) - s(t))^2

    Returns: dict with effective_gain, r_squared, learned params, etc.
    """
    rng = np.random.RandomState(seed)
    signals = rng.randn(N_STEPS)

    # Initialize parameters based on nonlinearity
    if nonlinearity == "linear":
        # o = w*y + b
        w = 0.5
        b = 0.0
        params = {"w": w, "b": b}
    elif nonlinearity == "tanh":
        # o = a*tanh(w*y + b)
        a = 1.0
        w = 0.5
        b = 0.0
        params = {"a": a, "w": w, "b": b}
    elif nonlinearity == "relu":
        # o = a*max(0, w*y + b)
        a = 1.0
        w = 0.5
        b = 0.0
        params = {"a": a, "w": w, "b": b}
    elif nonlinearity == "sigmoid_act":
        # o = a*sigmoid(w*y + b)
        a = 2.0  # Scale to cover range
        w = 0.5
        b = 0.0
        params = {"a": a, "w": w, "b": b}
    elif nonlinearity == "quadratic":
        # o = a*y^2 + w*y + b
        a = 0.0  # Start with zero quadratic
        w = 0.5
        b = 0.0
        params = {"a": a, "w": w, "b": b}
    else:
        raise ValueError(f"Unknown nonlinearity: {nonlinearity}")

    o_prev = 0.0
    lr = LR_INIT

    # Measurement accumulators
    o_vals = []
    y_vals = []
    s_vals = []
    err_sq_sum = 0.0
    s_sq_sum = 0.0

    for t in range(N_STEPS):
        s = signals[t]
        y = s + o_prev

        # Forward pass
        if nonlinearity == "linear":
            w, b_val = params["w"], params["b"]
            o = w * y + b_val
        elif nonlinearity == "tanh":
            a_val, w, b_val = params["a"], params["w"], params["b"]
            z = w * y + b_val
            o = a_val * np.tanh(z)
        elif nonlinearity == "relu":
            a_val, w, b_val = params["a"], params["w"], params["b"]
            z = w * y + b_val
            o = a_val * max(0.0, z)
        elif nonlinearity == "sigmoid_act":
            a_val, w, b_val = params["a"], params["w"], params["b"]
            z = w * y + b_val
            sz = sigmoid(np.array([z]))[0]
            o = a_val * sz
        elif nonlinearity == "quadratic":
            a_val, w, b_val = params["a"], params["w"], params["b"]
            o = a_val * y * y + w * y + b_val

        # Clamp output to prevent divergence
        o = np.clip(o, -10.0, 10.0)

        error = o - s

        # Backward pass: compute gradients
        if nonlinearity == "linear":
            grad_w = 2.0 * error * y
            grad_b = 2.0 * error
            grad_w = np.clip(grad_w, -5.0, 5.0)
            grad_b = np.clip(grad_b, -5.0, 5.0)
            params["w"] -= lr * grad_w
            params["b"] -= lr * grad_b
        elif nonlinearity == "tanh":
            z = params["w"] * y + params["b"]
            th = np.tanh(z)
            dtanh = 1.0 - th * th
            # do/da = tanh(z), do/dw = a*dtanh*y, do/db = a*dtanh
            grad_a = 2.0 * error * th
            grad_w = 2.0 * error * params["a"] * dtanh * y
            grad_b = 2.0 * error * params["a"] * dtanh
            for g_name, g_val in [("a", grad_a), ("w", grad_w), ("b", grad_b)]:
                g_val = np.clip(g_val, -5.0, 5.0)
                params[g_name] -= lr * g_val
        elif nonlinearity == "relu":
            z = params["w"] * y + params["b"]
            relu_active = 1.0 if z > 0 else 0.0
            grad_a = 2.0 * error * max(0.0, z)
            grad_w = 2.0 * error * params["a"] * relu_active * y
            grad_b = 2.0 * error * params["a"] * relu_active
            for g_name, g_val in [("a", grad_a), ("w", grad_w), ("b", grad_b)]:
                g_val = np.clip(g_val, -5.0, 5.0)
                params[g_name] -= lr * g_val
        elif nonlinearity == "sigmoid_act":
            z = params["w"] * y + params["b"]
            sz = sigmoid(np.array([z]))[0]
            dsig = sz * (1.0 - sz)
            grad_a = 2.0 * error * sz
            grad_w = 2.0 * error * params["a"] * dsig * y
            grad_b = 2.0 * error * params["a"] * dsig
            for g_name, g_val in [("a", grad_a), ("w", grad_w), ("b", grad_b)]:
                g_val = np.clip(g_val, -5.0, 5.0)
                params[g_name] -= lr * g_val
        elif nonlinearity == "quadratic":
            grad_a = 2.0 * error * y * y
            grad_w = 2.0 * error * y
            grad_b = 2.0 * error
            for g_name, g_val in [("a", grad_a), ("w", grad_w), ("b", grad_b)]:
                g_val = np.clip(g_val, -5.0, 5.0)
                params[g_name] -= lr * g_val

        # Clamp parameters
        for k in params:
            params[k] = np.clip(params[k], -5.0, 5.0)

        lr *= LR_DECAY

        # Measurement
        if t >= BURN_IN:
            o_vals.append(o)
            y_vals.append(y)
            s_vals.append(s)
            err_sq_sum += error * error
            s_sq_sum += s * s

        o_prev = o

    o_arr = np.array(o_vals)
    y_arr = np.array(y_vals)
    s_arr = np.array(s_vals)

    # R^2 = 1 - MSE/Var(s)
    mse = err_sq_sum / N_MEASURE
    var_s = s_sq_sum / N_MEASURE
    r2 = 1.0 - mse / var_s

    # Effective gain: slope of o vs y (linear regression)
    y_mean = np.mean(y_arr)
    o_mean = np.mean(o_arr)
    effective_gain = np.sum((y_arr - y_mean) * (o_arr - o_mean)) / np.sum((y_arr - y_mean)**2)

    return {
        "nonlinearity": nonlinearity,
        "effective_gain": effective_gain,
        "r_squared": r2,
        "params": dict(params),
        "mse": mse,
    }


def experiment1_nonlinearity():
    """Run Experiment 1: Nonlinearity test across all activation types."""
    print("=" * 70)
    print("EXPERIMENT 1: NONLINEARITY TEST")
    print("=" * 70)
    print(f"Does the SGD fixed point w ~ 1/phi = {INV_PHI:.4f} survive nonlinearity?")
    print()

    nonlinearities = ["linear", "tanh", "relu", "sigmoid_act", "quadratic"]
    display_names = {
        "linear": "Linear",
        "tanh": "Tanh",
        "relu": "ReLU",
        "sigmoid_act": "Sigmoid",
        "quadratic": "Quadratic",
    }

    results = {}

    for nl in nonlinearities:
        gains = []
        r2s = []
        all_params = []

        for seed in SEEDS:
            res = run_nonlinear_agent(nl, seed)
            gains.append(res["effective_gain"])
            r2s.append(res["r_squared"])
            all_params.append(res["params"])

        results[nl] = {
            "gains": np.array(gains),
            "r2s": np.array(r2s),
            "all_params": all_params,
            "display_name": display_names[nl],
        }

        g_mean, g_std = np.mean(gains), np.std(gains)
        r2_mean, r2_std = np.mean(r2s), np.std(r2s)

        # Average parameters
        avg_params = {}
        for k in all_params[0]:
            avg_params[k] = np.mean([p[k] for p in all_params])

        print(f"  {display_names[nl]:12s}: gain = {g_mean:.4f} +/- {g_std:.4f}, "
              f"R^2 = {r2_mean:.4f} +/- {r2_std:.4f}, "
              f"params = {{{', '.join(f'{k}={v:.4f}' for k, v in avg_params.items())}}}")

    print()
    print(f"  Reference: 1/phi = {INV_PHI:.4f}, true MSE-optimal w = {TRUE_OPT_W:.3f}")
    print(f"  Reference: 1/phi R^2 = {INV_PHI:.4f}, true optimal R^2 = {TRUE_OPT_R2:.3f}")
    print()

    # Verdict
    linear_gain = np.mean(results["linear"]["gains"])
    all_close_to_phi = True
    for nl in nonlinearities:
        g = np.mean(results[nl]["gains"])
        if abs(g - INV_PHI) > 0.05:
            all_close_to_phi = False

    if all_close_to_phi:
        print("  VERDICT: 1/phi SURVIVES nonlinearity - effective gain ~ 0.618 for all types")
    else:
        print("  VERDICT: 1/phi does NOT universally survive - nonlinearity shifts the fixed point")
        for nl in nonlinearities:
            g = np.mean(results[nl]["gains"])
            diff = g - INV_PHI
            print(f"    {display_names[nl]:12s}: delta from 1/phi = {diff:+.4f}")

    print()
    return results


# ==============================================================================
# Experiment 2: Cascade Test
# ==============================================================================
def run_cascade_simultaneous(seed):
    """
    Variant A: Both agents learn simultaneously.
    Agent A: y_A = s + o_A_prev, output o_A = w_A * y_A
    Agent B: y_B = o_A + o_B_prev, output o_B = w_B * y_B, tries to recover o_A
    """
    rng = np.random.RandomState(seed)
    signals = rng.randn(N_STEPS)

    w_A, b_A = 0.5, 0.0
    w_B, b_B = 0.5, 0.0
    o_A_prev, o_B_prev = 0.0, 0.0

    lr = LR_INIT

    # Measurement
    err_A_sq, s_sq = 0.0, 0.0
    err_B_sq, oA_sq = 0.0, 0.0
    meas = 0

    for t in range(N_STEPS):
        s = signals[t]

        # Agent A
        y_A = s + o_A_prev
        o_A = w_A * y_A + b_A
        o_A = np.clip(o_A, -10.0, 10.0)
        err_A = o_A - s

        # Agent B: tries to recover o_A from y_B = o_A + o_B_prev
        y_B = o_A + o_B_prev
        o_B = w_B * y_B + b_B
        o_B = np.clip(o_B, -10.0, 10.0)
        err_B = o_B - o_A  # B's target is o_A

        # SGD updates
        grad_wA = np.clip(2.0 * err_A * y_A, -5.0, 5.0)
        grad_bA = np.clip(2.0 * err_A, -5.0, 5.0)
        grad_wB = np.clip(2.0 * err_B * y_B, -5.0, 5.0)
        grad_bB = np.clip(2.0 * err_B, -5.0, 5.0)

        w_A -= lr * grad_wA
        b_A -= lr * grad_bA
        w_B -= lr * grad_wB
        b_B -= lr * grad_bB

        w_A = np.clip(w_A, -2.0, 2.0)
        b_A = np.clip(b_A, -2.0, 2.0)
        w_B = np.clip(w_B, -2.0, 2.0)
        b_B = np.clip(b_B, -2.0, 2.0)

        lr *= LR_DECAY

        if t >= BURN_IN:
            meas += 1
            err_A_sq += err_A * err_A
            s_sq += s * s
            err_B_sq += err_B * err_B
            oA_sq += o_A * o_A

        o_A_prev = o_A
        o_B_prev = o_B

    mse_A = err_A_sq / meas
    var_s = s_sq / meas
    r2_A = 1.0 - mse_A / var_s if var_s > 1e-10 else 0.0

    mse_B = err_B_sq / meas
    var_oA = oA_sq / meas
    r2_B = 1.0 - mse_B / var_oA if var_oA > 1e-10 else 0.0

    return {"w_A": w_A, "w_B": w_B, "r2_A": r2_A, "r2_B": r2_B, "b_A": b_A, "b_B": b_B}


def run_cascade_developmental(seed):
    """
    Variant B: Developmental (sequential) learning.
    Phase 1 (25K steps): Agent A learns alone.
    Phase 2 (25K steps): A frozen at learned weight; B connects and learns.
    """
    rng = np.random.RandomState(seed)
    signals = rng.randn(N_STEPS)

    # Phase 1: Agent A alone
    w_A, b_A = 0.5, 0.0
    o_A_prev = 0.0
    lr = LR_INIT

    phase1_end = N_STEPS // 2  # 25K

    for t in range(phase1_end):
        s = signals[t]
        y_A = s + o_A_prev
        o_A = w_A * y_A + b_A
        o_A = np.clip(o_A, -10.0, 10.0)
        err_A = o_A - s

        grad_w = np.clip(2.0 * err_A * y_A, -5.0, 5.0)
        grad_b = np.clip(2.0 * err_A, -5.0, 5.0)
        w_A -= lr * grad_w
        b_A -= lr * grad_b
        w_A = np.clip(w_A, -2.0, 2.0)
        b_A = np.clip(b_A, -2.0, 2.0)
        lr *= LR_DECAY
        o_A_prev = o_A

    w_A_frozen = w_A
    b_A_frozen = b_A

    # Phase 2: A frozen, B learns
    w_B, b_B = 0.5, 0.0
    o_B_prev = 0.0
    # Continue lr from where phase 1 left off

    err_A_sq, s_sq_sum = 0.0, 0.0
    err_B_sq, oA_sq = 0.0, 0.0
    meas = 0

    burn_in_phase2 = phase1_end + BURN_IN // 2  # 5K burn-in for phase 2

    for t in range(phase1_end, N_STEPS):
        s = signals[t]

        # Agent A (frozen)
        y_A = s + o_A_prev
        o_A = w_A_frozen * y_A + b_A_frozen
        o_A = np.clip(o_A, -10.0, 10.0)
        err_A = o_A - s

        # Agent B
        y_B = o_A + o_B_prev
        o_B = w_B * y_B + b_B
        o_B = np.clip(o_B, -10.0, 10.0)
        err_B = o_B - o_A  # B tries to recover o_A

        grad_wB = np.clip(2.0 * err_B * y_B, -5.0, 5.0)
        grad_bB = np.clip(2.0 * err_B, -5.0, 5.0)
        w_B -= lr * grad_wB
        b_B -= lr * grad_bB
        w_B = np.clip(w_B, -2.0, 2.0)
        b_B = np.clip(b_B, -2.0, 2.0)
        lr *= LR_DECAY

        if t >= burn_in_phase2:
            meas += 1
            err_A_sq += err_A * err_A
            s_sq_sum += s * s
            err_B_sq += err_B * err_B
            oA_sq += o_A * o_A

        o_A_prev = o_A
        o_B_prev = o_B

    mse_A = err_A_sq / max(meas, 1)
    var_s = s_sq_sum / max(meas, 1)
    r2_A = 1.0 - mse_A / var_s if var_s > 1e-10 else 0.0

    mse_B = err_B_sq / max(meas, 1)
    var_oA = oA_sq / max(meas, 1)
    r2_B = 1.0 - mse_B / var_oA if var_oA > 1e-10 else 0.0

    return {"w_A": w_A_frozen, "w_B": w_B, "r2_A": r2_A, "r2_B": r2_B,
            "b_A": b_A_frozen, "b_B": b_B}


def run_cascade_echo_subtraction(seed):
    """
    Variant C: Developmental with echo subtraction.
    Phase 1: A learns alone (25K steps).
    Phase 2: A frozen. B first learns to subtract its own echo, then processes
    the cleaned signal to recover the ORIGINAL signal s(t) (not o_A).

    B has two sub-weights:
        w_self: learns to predict its own echo contribution
        w_ext: processes the cleaned signal

    y_B(t) = o_A(t) + o_B(t-1)
    y_clean(t) = y_B(t) - w_self * o_B(t-1)  [approximately = o_A(t)]
    o_B(t) = w_ext * y_clean(t) + b_B
    Target: s(t) (the ORIGINAL signal)
    """
    rng = np.random.RandomState(seed)
    signals = rng.randn(N_STEPS)

    # Phase 1: Agent A alone
    w_A, b_A = 0.5, 0.0
    o_A_prev = 0.0
    lr = LR_INIT

    phase1_end = N_STEPS // 2

    for t in range(phase1_end):
        s = signals[t]
        y_A = s + o_A_prev
        o_A = w_A * y_A + b_A
        o_A = np.clip(o_A, -10.0, 10.0)
        err_A = o_A - s

        grad_w = np.clip(2.0 * err_A * y_A, -5.0, 5.0)
        grad_b = np.clip(2.0 * err_A, -5.0, 5.0)
        w_A -= lr * grad_w
        b_A -= lr * grad_b
        w_A = np.clip(w_A, -2.0, 2.0)
        b_A = np.clip(b_A, -2.0, 2.0)
        lr *= LR_DECAY
        o_A_prev = o_A

    w_A_frozen = w_A
    b_A_frozen = b_A

    # Phase 2: A frozen, B learns with echo subtraction
    w_self = 0.5  # echo subtraction weight
    w_ext = 0.5   # external signal processing weight
    b_B = 0.0
    o_B_prev = 0.0

    err_sq_sum = 0.0
    s_sq_sum = 0.0
    meas = 0

    burn_in_phase2 = phase1_end + BURN_IN // 2

    for t in range(phase1_end, N_STEPS):
        s = signals[t]

        # Agent A (frozen)
        y_A = s + o_A_prev
        o_A = w_A_frozen * y_A + b_A_frozen
        o_A = np.clip(o_A, -10.0, 10.0)

        # Agent B with echo subtraction
        y_B = o_A + o_B_prev
        y_clean = y_B - w_self * o_B_prev  # subtract estimated self-echo
        o_B = w_ext * y_clean + b_B
        o_B = np.clip(o_B, -10.0, 10.0)

        # B's target is s(t) - the ORIGINAL signal
        err_B = o_B - s

        # Gradients for w_self, w_ext, b_B
        # o_B = w_ext * (y_B - w_self * o_B_prev) + b_B
        # do_B/dw_ext = y_clean
        # do_B/dw_self = w_ext * (-o_B_prev)
        # do_B/db_B = 1
        grad_w_ext = np.clip(2.0 * err_B * y_clean, -5.0, 5.0)
        grad_w_self = np.clip(2.0 * err_B * w_ext * (-o_B_prev), -5.0, 5.0)
        grad_b_B = np.clip(2.0 * err_B, -5.0, 5.0)

        w_ext -= lr * grad_w_ext
        w_self -= lr * grad_w_self
        b_B -= lr * grad_b_B

        w_ext = np.clip(w_ext, -2.0, 2.0)
        w_self = np.clip(w_self, -2.0, 2.0)
        b_B = np.clip(b_B, -2.0, 2.0)

        lr *= LR_DECAY

        if t >= burn_in_phase2:
            meas += 1
            err_sq_sum += err_B * err_B
            s_sq_sum += s * s

        o_A_prev = o_A
        o_B_prev = o_B

    mse_B = err_sq_sum / max(meas, 1)
    var_s = s_sq_sum / max(meas, 1)
    r2_B = 1.0 - mse_B / var_s if var_s > 1e-10 else 0.0

    # Effective w_B for comparison: the overall gain from input to output
    # In the echo subtraction model, the effective gain depends on both w_self and w_ext
    effective_w_B = w_ext  # The gain on the cleaned signal

    return {"w_A": w_A_frozen, "w_B": effective_w_B, "w_self": w_self, "w_ext": w_ext,
            "r2_A": None, "r2_B": r2_B, "b_A": b_A_frozen, "b_B": b_B}


def run_cascade_control_no_selfloop(seed):
    """
    Control 1: Agent B with no self-loop. y_B = o_A only. Should give w_B = 1.0.
    """
    rng = np.random.RandomState(seed)
    signals = rng.randn(N_STEPS)

    # Agent A learns first (same as developmental)
    w_A, b_A = 0.5, 0.0
    o_A_prev = 0.0
    lr = LR_INIT
    phase1_end = N_STEPS // 2

    for t in range(phase1_end):
        s = signals[t]
        y_A = s + o_A_prev
        o_A = w_A * y_A + b_A
        o_A = np.clip(o_A, -10.0, 10.0)
        err_A = o_A - s
        grad_w = np.clip(2.0 * err_A * y_A, -5.0, 5.0)
        grad_b = np.clip(2.0 * err_A, -5.0, 5.0)
        w_A -= lr * grad_w
        b_A -= lr * grad_b
        w_A = np.clip(w_A, -2.0, 2.0)
        b_A = np.clip(b_A, -2.0, 2.0)
        lr *= LR_DECAY
        o_A_prev = o_A

    w_A_frozen = w_A
    b_A_frozen = b_A

    # Phase 2: B with no self-loop
    w_B, b_B = 0.5, 0.0

    err_B_sq, oA_sq = 0.0, 0.0
    meas = 0
    burn_in_phase2 = phase1_end + BURN_IN // 2

    for t in range(phase1_end, N_STEPS):
        s = signals[t]
        y_A = s + o_A_prev
        o_A = w_A_frozen * y_A + b_A_frozen
        o_A = np.clip(o_A, -10.0, 10.0)

        # B sees ONLY o_A (no self-loop)
        y_B = o_A
        o_B = w_B * y_B + b_B
        o_B = np.clip(o_B, -10.0, 10.0)
        err_B = o_B - o_A

        grad_wB = np.clip(2.0 * err_B * y_B, -5.0, 5.0)
        grad_bB = np.clip(2.0 * err_B, -5.0, 5.0)
        w_B -= lr * grad_wB
        b_B -= lr * grad_bB
        w_B = np.clip(w_B, -2.0, 2.0)
        b_B = np.clip(b_B, -2.0, 2.0)
        lr *= LR_DECAY

        if t >= burn_in_phase2:
            meas += 1
            err_B_sq += err_B * err_B
            oA_sq += o_A * o_A

        o_A_prev = o_A

    mse_B = err_B_sq / max(meas, 1)
    var_oA = oA_sq / max(meas, 1)
    r2_B = 1.0 - mse_B / var_oA if var_oA > 1e-10 else 0.0

    return {"w_A": w_A_frozen, "w_B": w_B, "r2_A": None, "r2_B": r2_B,
            "b_A": b_A_frozen, "b_B": b_B}


def run_cascade_control_independent(seed):
    """
    Control 2: Agent B with independent signal (no connection to A).
    y_B = s_B + o_B_prev. Should give w_B = 1/phi (same as isolated agent).
    """
    rng = np.random.RandomState(seed)
    signals_B = rng.randn(N_STEPS)

    w_B, b_B = 0.5, 0.0
    o_B_prev = 0.0
    lr = LR_INIT

    err_sq, s_sq = 0.0, 0.0
    meas = 0

    for t in range(N_STEPS):
        s_B = signals_B[t]
        y_B = s_B + o_B_prev
        o_B = w_B * y_B + b_B
        o_B = np.clip(o_B, -10.0, 10.0)
        err_B = o_B - s_B

        grad_wB = np.clip(2.0 * err_B * y_B, -5.0, 5.0)
        grad_bB = np.clip(2.0 * err_B, -5.0, 5.0)
        w_B -= lr * grad_wB
        b_B -= lr * grad_bB
        w_B = np.clip(w_B, -2.0, 2.0)
        b_B = np.clip(b_B, -2.0, 2.0)
        lr *= LR_DECAY

        if t >= BURN_IN:
            meas += 1
            err_sq += err_B * err_B
            s_sq += s_B * s_B

        o_B_prev = o_B

    mse_B = err_sq / max(meas, 1)
    var_s = s_sq / max(meas, 1)
    r2_B = 1.0 - mse_B / var_s if var_s > 1e-10 else 0.0

    return {"w_A": None, "w_B": w_B, "r2_A": None, "r2_B": r2_B, "b_B": b_B}


def experiment2_cascade():
    """Run Experiment 2: Cascade test with all variants."""
    print("=" * 70)
    print("EXPERIMENT 2: CASCADE TEST")
    print("=" * 70)
    print(f"Does Agent B converge to 1/phi^2={INV_PHI2:.4f}, 0.5, or 1/phi={INV_PHI:.4f}?")
    print()

    variants = {
        "Simultaneous": run_cascade_simultaneous,
        "Developmental": run_cascade_developmental,
        "Echo-Subtract": run_cascade_echo_subtraction,
        "Ctrl: No Loop": run_cascade_control_no_selfloop,
        "Ctrl: Independent": run_cascade_control_independent,
    }

    results = {}

    for name, func in variants.items():
        wA_list, wB_list, r2A_list, r2B_list = [], [], [], []
        extra_data = []

        for seed in SEEDS:
            res = func(seed)
            if res["w_A"] is not None:
                wA_list.append(res["w_A"])
            wB_list.append(res["w_B"])
            if res.get("r2_A") is not None:
                r2A_list.append(res["r2_A"])
            r2B_list.append(res["r2_B"])
            extra_data.append(res)

        results[name] = {
            "wA": np.array(wA_list) if wA_list else None,
            "wB": np.array(wB_list),
            "r2A": np.array(r2A_list) if r2A_list else None,
            "r2B": np.array(r2B_list),
            "extra": extra_data,
        }

        wB_mean, wB_std = np.mean(wB_list), np.std(wB_list)
        r2B_mean, r2B_std = np.mean(r2B_list), np.std(r2B_list)

        wA_str = ""
        if wA_list:
            wA_str = f"w_A = {np.mean(wA_list):.4f}, "

        r2A_str = ""
        if r2A_list:
            r2A_str = f"R2_A = {np.mean(r2A_list):.4f}, "

        # Extra params for echo subtraction
        extra_str = ""
        if name == "Echo-Subtract":
            w_self_avg = np.mean([d.get("w_self", 0) for d in extra_data])
            w_ext_avg = np.mean([d.get("w_ext", 0) for d in extra_data])
            extra_str = f", w_self={w_self_avg:.4f}, w_ext={w_ext_avg:.4f}"

        print(f"  {name:20s}: {wA_str}w_B = {wB_mean:.4f} +/- {wB_std:.4f}, "
              f"{r2A_str}R2_B = {r2B_mean:.4f} +/- {r2B_std:.4f}{extra_str}")

    print()
    print(f"  Reference values: 1/phi^2 = {INV_PHI2:.4f}, 0.5, 1/phi = {INV_PHI:.4f}")
    print()

    # Analysis
    print("  ANALYSIS:")
    for name in ["Simultaneous", "Developmental", "Echo-Subtract"]:
        wB = np.mean(results[name]["wB"])
        closest_val = min([(INV_PHI2, "1/phi^2"), (0.5, "0.5"), (INV_PHI, "1/phi")],
                          key=lambda x: abs(wB - x[0]))
        print(f"    {name:20s}: w_B={wB:.4f}, closest to {closest_val[1]}={closest_val[0]:.4f} "
              f"(delta={wB - closest_val[0]:+.4f})")

    print()
    return results


# ==============================================================================
# Plotting
# ==============================================================================
def create_plots(exp1_results, exp2_results):
    """Create the 4-panel figure."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Nonlinear & Cascade Self-Reference Tests", fontsize=14, fontweight="bold")

    # Color palette
    colors = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63", "#9C27B0"]

    # ── Panel 1: Nonlinearity - Effective Gain ──
    ax = axes[0, 0]
    nl_names = ["linear", "tanh", "relu", "sigmoid_act", "quadratic"]
    display_labels = ["Linear", "Tanh", "ReLU", "Sigmoid", "Quadratic"]
    gains_means = [np.mean(exp1_results[nl]["gains"]) for nl in nl_names]
    gains_stds = [np.std(exp1_results[nl]["gains"]) for nl in nl_names]

    x = np.arange(len(nl_names))
    bars = ax.bar(x, gains_means, yerr=gains_stds, capsize=5, color=colors,
                  edgecolor="black", linewidth=0.5, alpha=0.85)
    ax.axhline(y=INV_PHI, color="red", linestyle="--", linewidth=1.5, label=f"1/phi = {INV_PHI:.3f}")
    ax.axhline(y=TRUE_OPT_W, color="blue", linestyle=":", linewidth=1.5, label=f"True opt = {TRUE_OPT_W:.3f}")
    ax.set_xticks(x)
    ax.set_xticklabels(display_labels, fontsize=9)
    ax.set_ylabel("Effective Gain")
    ax.set_title("Exp 1: Effective Gain by Nonlinearity")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(0, max(gains_means) * 1.4)

    # Add value labels on bars
    for bar, mean_val in zip(bars, gains_means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{mean_val:.3f}", ha="center", va="bottom", fontsize=8)

    # ── Panel 2: Nonlinearity - R^2 ──
    ax = axes[0, 1]
    r2_means = [np.mean(exp1_results[nl]["r2s"]) for nl in nl_names]
    r2_stds = [np.std(exp1_results[nl]["r2s"]) for nl in nl_names]

    bars = ax.bar(x, r2_means, yerr=r2_stds, capsize=5, color=colors,
                  edgecolor="black", linewidth=0.5, alpha=0.85)
    ax.axhline(y=INV_PHI, color="red", linestyle="--", linewidth=1.5, label=f"1/phi = {INV_PHI:.3f}")
    ax.axhline(y=TRUE_OPT_R2, color="blue", linestyle=":", linewidth=1.5, label=f"True opt R2 = {TRUE_OPT_R2:.3f}")
    ax.set_xticks(x)
    ax.set_xticklabels(display_labels, fontsize=9)
    ax.set_ylabel("R-squared")
    ax.set_title("Exp 1: R-squared by Nonlinearity")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(0, max(r2_means) * 1.4)

    for bar, mean_val in zip(bars, r2_means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{mean_val:.3f}", ha="center", va="bottom", fontsize=8)

    # ── Panel 3: Cascade - w_B ──
    ax = axes[1, 0]
    cascade_names = ["Simultaneous", "Developmental", "Echo-Subtract", "Ctrl: No Loop", "Ctrl: Independent"]
    cascade_labels = ["Simul.", "Develop.", "Echo-Sub.", "No Loop", "Indep."]

    wB_means = [np.mean(exp2_results[n]["wB"]) for n in cascade_names]
    wB_stds = [np.std(exp2_results[n]["wB"]) for n in cascade_names]

    x2 = np.arange(len(cascade_names))
    bars = ax.bar(x2, wB_means, yerr=wB_stds, capsize=5, color=colors,
                  edgecolor="black", linewidth=0.5, alpha=0.85)
    ax.axhline(y=INV_PHI2, color="green", linestyle="-.", linewidth=1.5, label=f"1/phi^2 = {INV_PHI2:.3f}")
    ax.axhline(y=0.5, color="orange", linestyle=":", linewidth=1.5, label="0.5")
    ax.axhline(y=INV_PHI, color="red", linestyle="--", linewidth=1.5, label=f"1/phi = {INV_PHI:.3f}")
    ax.set_xticks(x2)
    ax.set_xticklabels(cascade_labels, fontsize=9)
    ax.set_ylabel("w_B (weight)")
    ax.set_title("Exp 2: Agent B Weight by Variant")
    ax.legend(loc="upper right", fontsize=7)
    ax.set_ylim(0, max(max(wB_means) * 1.4, 1.1))

    for bar, mean_val in zip(bars, wB_means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{mean_val:.3f}", ha="center", va="bottom", fontsize=8)

    # ── Panel 4: Cascade - R^2_B ──
    ax = axes[1, 1]
    r2B_means = [np.mean(exp2_results[n]["r2B"]) for n in cascade_names]
    r2B_stds = [np.std(exp2_results[n]["r2B"]) for n in cascade_names]

    bars = ax.bar(x2, r2B_means, yerr=r2B_stds, capsize=5, color=colors,
                  edgecolor="black", linewidth=0.5, alpha=0.85)
    ax.axhline(y=INV_PHI2, color="green", linestyle="-.", linewidth=1.5, label=f"1/phi^2 = {INV_PHI2:.3f}")
    ax.axhline(y=0.5, color="orange", linestyle=":", linewidth=1.5, label="0.5")
    ax.axhline(y=INV_PHI, color="red", linestyle="--", linewidth=1.5, label=f"1/phi = {INV_PHI:.3f}")
    ax.set_xticks(x2)
    ax.set_xticklabels(cascade_labels, fontsize=9)
    ax.set_ylabel("R-squared (B)")
    ax.set_title("Exp 2: Agent B R-squared by Variant")
    ax.legend(loc="upper right", fontsize=7)
    ax.set_ylim(0, max(max(r2B_means) * 1.4, 1.1))

    for bar, mean_val in zip(bars, r2B_means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{mean_val:.3f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "nonlinear_cascade_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Plots saved to: {out_path}")
    return out_path


# ==============================================================================
# Main
# ==============================================================================
def main():
    t0 = time.time()

    print()
    print("Nonlinear & Cascade Self-Reference Tests")
    print("=" * 70)
    print(f"Parameters: {N_STEPS} steps, {BURN_IN} burn-in, {len(SEEDS)} seeds")
    print(f"LR: {LR_INIT} with {LR_DECAY} decay per step")
    print()

    # Experiment 1
    exp1_results = experiment1_nonlinearity()
    t1 = time.time()
    print(f"  [Exp 1 completed in {t1 - t0:.1f}s]")
    print()

    # Experiment 2
    exp2_results = experiment2_cascade()
    t2 = time.time()
    print(f"  [Exp 2 completed in {t2 - t1:.1f}s]")
    print()

    # Create plots
    print("-" * 70)
    print("GENERATING PLOTS")
    print("-" * 70)
    create_plots(exp1_results, exp2_results)

    # Final summary
    t_total = time.time() - t0
    print()
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"  Total runtime: {t_total:.1f}s")
    print()

    # Experiment 1 summary
    print("  Experiment 1 - Nonlinearity:")
    nl_names = ["linear", "tanh", "relu", "sigmoid_act", "quadratic"]
    display_names = ["Linear", "Tanh", "ReLU", "Sigmoid", "Quadratic"]
    print(f"    {'Type':12s}  {'Eff. Gain':>10s}  {'R^2':>10s}  {'vs 1/phi':>10s}")
    print(f"    {'-'*12}  {'-'*10}  {'-'*10}  {'-'*10}")
    for nl, dn in zip(nl_names, display_names):
        g = np.mean(exp1_results[nl]["gains"])
        r2 = np.mean(exp1_results[nl]["r2s"])
        delta = g - INV_PHI
        print(f"    {dn:12s}  {g:10.4f}  {r2:10.4f}  {delta:+10.4f}")

    print()

    # Experiment 2 summary
    print("  Experiment 2 - Cascade:")
    cascade_names = ["Simultaneous", "Developmental", "Echo-Subtract", "Ctrl: No Loop", "Ctrl: Independent"]
    print(f"    {'Variant':20s}  {'w_B':>8s}  {'R2_B':>8s}  {'vs 1/phi^2':>10s}  {'vs 0.5':>8s}  {'vs 1/phi':>8s}")
    print(f"    {'-'*20}  {'-'*8}  {'-'*8}  {'-'*10}  {'-'*8}  {'-'*8}")
    for name in cascade_names:
        wB = np.mean(exp2_results[name]["wB"])
        r2B = np.mean(exp2_results[name]["r2B"])
        d1 = wB - INV_PHI2
        d2 = wB - 0.5
        d3 = wB - INV_PHI
        print(f"    {name:20s}  {wB:8.4f}  {r2B:8.4f}  {d1:+10.4f}  {d2:+8.4f}  {d3:+8.4f}")

    print()

    # Key conclusions
    print("  KEY FINDINGS:")

    # Exp 1 conclusion
    linear_gain = np.mean(exp1_results["linear"]["gains"])
    nonlinear_gains = [np.mean(exp1_results[nl]["gains"]) for nl in ["tanh", "relu", "sigmoid_act", "quadratic"]]
    max_deviation = max(abs(g - INV_PHI) for g in nonlinear_gains)

    if max_deviation < 0.05:
        print(f"    1. phi SURVIVES nonlinearity: all effective gains within 0.05 of 1/phi")
    elif max_deviation < 0.10:
        print(f"    1. phi APPROXIMATELY survives: max deviation = {max_deviation:.4f}")
    else:
        print(f"    1. phi does NOT survive: max deviation = {max_deviation:.4f}")
        for nl, dn in zip(["tanh", "relu", "sigmoid_act", "quadratic"],
                          ["Tanh", "ReLU", "Sigmoid", "Quadratic"]):
            g = np.mean(exp1_results[nl]["gains"])
            if abs(g - INV_PHI) > 0.05:
                print(f"       {dn}: gain = {g:.4f} (delta = {g - INV_PHI:+.4f})")

    # Exp 2 conclusion
    simul_wB = np.mean(exp2_results["Simultaneous"]["wB"])
    devel_wB = np.mean(exp2_results["Developmental"]["wB"])
    echo_wB = np.mean(exp2_results["Echo-Subtract"]["wB"])

    print(f"    2. Cascade results:")
    print(f"       Simultaneous:  w_B = {simul_wB:.4f} (predicted: 1/phi = {INV_PHI:.4f})")
    print(f"       Developmental: w_B = {devel_wB:.4f}")
    print(f"       Echo-Subtract: w_B = {echo_wB:.4f}")

    ctrl_noloop = np.mean(exp2_results["Ctrl: No Loop"]["wB"])
    ctrl_indep = np.mean(exp2_results["Ctrl: Independent"]["wB"])
    print(f"       Controls: No-Loop w_B = {ctrl_noloop:.4f} (expected: 1.0), "
          f"Independent w_B = {ctrl_indep:.4f} (expected: {INV_PHI:.4f})")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
