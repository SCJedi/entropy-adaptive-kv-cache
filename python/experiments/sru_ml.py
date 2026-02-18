"""
Self-Referential Unit (SRU) as ML Primitive
============================================
Tests whether self-referential loops can serve as computational primitives
in neural networks, and whether golden-ratio structure provides useful
inductive bias.

Architecture:
    SRU unit: y_i(t) = input_i + w_self_i * h_i(t-1), h_i(t) = tanh(y_i(t))
    SRU Network: Input -> W_in -> SRU Layer (T steps) -> W_out -> prediction
    Baseline: Input -> W1 -> tanh -> W2 -> prediction (matched param count)

Two tasks:
    A) Standard regression (sin(x) + noise) -- does SRU work at all?
    B) Self-referential prediction -- SRU advantage at high contamination?

Key questions:
    1. Does w_self converge to 1/phi (~0.618) or 0.525?
    2. Does T (unroll depth) affect convergence target?
    3. Does SRU outperform baseline on self-referential tasks?

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
PHI = (1 + np.sqrt(5)) / 2       # Golden ratio ~1.618
INV_PHI = 1.0 / PHI              # ~0.618
TRUE_OPT = 0.525                  # System-aware optimum from Ouroboros theory

N_SRU = 16          # SRU hidden units
N_BASELINE = 21     # Baseline hidden units (matched param count: 21+21+21+1=64)
DEFAULT_T = 5       # Default SRU unroll steps

# Task A
N_TRAIN = 500
N_TEST = 200
N_EPOCHS = 200
BATCH_SIZE = 32
LR_INIT = 0.01
MOMENTUM = 0.9

# Task B
N_TIMESTEPS = 1000
ALPHA_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
ONLINE_LR = 0.005

# T sweep
T_VALUES = [3, 5, 10, 20]

SEEDS = [42, 137, 256]
GRAD_CLIP = 5.0


# ==============================================================================
# Utility functions
# ==============================================================================
def set_seed(seed):
    np.random.seed(seed)


def clip_grad(g, max_norm=GRAD_CLIP):
    """Clip gradient by global norm."""
    norm = np.sqrt(np.sum(g ** 2))
    if norm > max_norm:
        g = g * (max_norm / norm)
    return g


# ==============================================================================
# SRU Network
# ==============================================================================
class SRUNetwork:
    """
    Self-Referential Unit network.
    Input (1) -> W_in (1 x N_SRU) + b_in -> SRU Layer (T steps) -> W_out (N_SRU x 1) + b_out -> output
    Parameters: N_SRU + N_SRU + N_SRU + N_SRU + 1 = 4*N_SRU + 1 = 65
    """

    def __init__(self, n_hidden=N_SRU, T=DEFAULT_T, init_w_self=None):
        self.n = n_hidden
        self.T = T

        # Xavier initialization
        scale_in = np.sqrt(2.0 / (1 + n_hidden))
        scale_out = np.sqrt(2.0 / (n_hidden + 1))

        self.W_in = np.random.randn(1, n_hidden) * scale_in
        self.b_in = np.zeros(n_hidden)
        self.W_out = np.random.randn(n_hidden, 1) * scale_out
        self.b_out = np.zeros(1)

        # The self-referential weights -- initialize near 1/phi
        if init_w_self is not None:
            self.w_self = np.full(n_hidden, init_w_self)
        else:
            self.w_self = np.random.uniform(0.4, 0.8, n_hidden)

        # Momentum buffers
        self.v_W_in = np.zeros_like(self.W_in)
        self.v_b_in = np.zeros_like(self.b_in)
        self.v_w_self = np.zeros_like(self.w_self)
        self.v_W_out = np.zeros_like(self.W_out)
        self.v_b_out = np.zeros_like(self.b_out)

        # Cache for forward/backward
        self.h_history = None
        self.input_to_sru = None
        self.x_input = None

    def forward(self, x):
        """
        Forward pass.
        x: (batch, 1)
        Returns: (batch, 1) predictions
        """
        batch = x.shape[0]
        self.x_input = x

        # Input layer: (batch, 1) @ (1, n) + (n,) -> (batch, n)
        self.input_to_sru = x @ self.W_in + self.b_in

        # SRU recurrence over T steps
        # h_history[0] = zeros (initial state)
        # h_history[t] for t=1..T is the state after t steps
        self.h_history = np.zeros((self.T + 1, batch, self.n))

        for t in range(self.T):
            y = self.input_to_sru + self.w_self[np.newaxis, :] * self.h_history[t]
            self.h_history[t + 1] = np.tanh(y)

        # Output layer: (batch, n) @ (n, 1) + (1,) -> (batch, 1)
        output = self.h_history[self.T] @ self.W_out + self.b_out
        return output

    def backward(self, d_output):
        """
        Backward pass with BPTT through the SRU recurrence.
        d_output: (batch, 1) -- gradient of loss w.r.t. output
        """
        batch = d_output.shape[0]

        # Output layer gradients
        d_W_out = self.h_history[self.T].T @ d_output / batch  # (n, 1)
        d_b_out = np.mean(d_output, axis=0)                     # (1,)

        # Gradient flowing back into SRU final state
        d_h = d_output @ self.W_out.T  # (batch, n)

        # BPTT through SRU recurrence
        d_W_in = np.zeros_like(self.W_in)
        d_b_in = np.zeros_like(self.b_in)
        d_w_self = np.zeros_like(self.w_self)

        for t in range(self.T - 1, -1, -1):
            # Through tanh: d_y = d_h * (1 - h_{t+1}^2)
            d_y = d_h * (1.0 - self.h_history[t + 1] ** 2)  # (batch, n)

            # Accumulate w_self gradient: d_w_self += sum_batch(d_y * h_t)
            d_w_self += np.sum(d_y * self.h_history[t], axis=0) / batch

            # Input layer gradient accumulation
            # d_y flows to input_to_sru (same at every step)
            d_input_to_sru = d_y  # (batch, n)
            d_W_in += (self.x_input.T @ d_input_to_sru) / batch
            d_b_in += np.mean(d_input_to_sru, axis=0)

            # Propagate back through self-referential connection
            d_h = d_y * self.w_self[np.newaxis, :]  # (batch, n)

        return {
            'W_in': clip_grad(d_W_in),
            'b_in': clip_grad(d_b_in),
            'w_self': clip_grad(d_w_self),
            'W_out': clip_grad(d_W_out),
            'b_out': clip_grad(d_b_out),
        }

    def update(self, grads, lr, momentum=MOMENTUM):
        """SGD with momentum."""
        self.v_W_in = momentum * self.v_W_in - lr * grads['W_in']
        self.v_b_in = momentum * self.v_b_in - lr * grads['b_in']
        self.v_w_self = momentum * self.v_w_self - lr * grads['w_self']
        self.v_W_out = momentum * self.v_W_out - lr * grads['W_out']
        self.v_b_out = momentum * self.v_b_out - lr * grads['b_out']

        self.W_in += self.v_W_in
        self.b_in += self.v_b_in
        self.w_self += self.v_w_self
        self.W_out += self.v_W_out
        self.b_out += self.v_b_out

    def param_count(self):
        return self.W_in.size + self.b_in.size + self.w_self.size + self.W_out.size + self.b_out.size


# ==============================================================================
# Baseline Network
# ==============================================================================
class BaselineNetwork:
    """
    Standard 1-hidden-layer network.
    Input (1) -> W1 (1 x N) + b1 -> tanh -> W2 (N x 1) + b2 -> output
    Parameters: N + N + N + 1 = 3*N + 1
    """

    def __init__(self, n_hidden=N_BASELINE):
        self.n = n_hidden

        scale1 = np.sqrt(2.0 / (1 + n_hidden))
        scale2 = np.sqrt(2.0 / (n_hidden + 1))

        self.W1 = np.random.randn(1, n_hidden) * scale1
        self.b1 = np.zeros(n_hidden)
        self.W2 = np.random.randn(n_hidden, 1) * scale2
        self.b2 = np.zeros(1)

        # Momentum buffers
        self.v_W1 = np.zeros_like(self.W1)
        self.v_b1 = np.zeros_like(self.b1)
        self.v_W2 = np.zeros_like(self.W2)
        self.v_b2 = np.zeros_like(self.b2)

        # Cache
        self.x_input = None
        self.hidden_pre = None
        self.hidden = None

    def forward(self, x):
        """Forward pass. x: (batch, 1) -> (batch, 1)"""
        self.x_input = x
        self.hidden_pre = x @ self.W1 + self.b1   # (batch, n)
        self.hidden = np.tanh(self.hidden_pre)      # (batch, n)
        output = self.hidden @ self.W2 + self.b2    # (batch, 1)
        return output

    def backward(self, d_output):
        """Backward pass."""
        batch = d_output.shape[0]

        d_W2 = self.hidden.T @ d_output / batch
        d_b2 = np.mean(d_output, axis=0)

        d_hidden = d_output @ self.W2.T
        d_pre = d_hidden * (1.0 - self.hidden ** 2)

        d_W1 = self.x_input.T @ d_pre / batch
        d_b1 = np.mean(d_pre, axis=0)

        return {
            'W1': clip_grad(d_W1),
            'b1': clip_grad(d_b1),
            'W2': clip_grad(d_W2),
            'b2': clip_grad(d_b2),
        }

    def update(self, grads, lr, momentum=MOMENTUM):
        """SGD with momentum."""
        self.v_W1 = momentum * self.v_W1 - lr * grads['W1']
        self.v_b1 = momentum * self.v_b1 - lr * grads['b1']
        self.v_W2 = momentum * self.v_W2 - lr * grads['W2']
        self.v_b2 = momentum * self.v_b2 - lr * grads['b2']

        self.W1 += self.v_W1
        self.b1 += self.v_b1
        self.W2 += self.v_W2
        self.b2 += self.v_b2

    def param_count(self):
        return self.W1.size + self.b1.size + self.W2.size + self.b2.size


# ==============================================================================
# Training utilities
# ==============================================================================
def mse_loss(pred, target):
    """Mean squared error and its gradient."""
    diff = pred - target
    loss = np.mean(diff ** 2)
    grad = 2.0 * diff / diff.shape[0]  # will be divided by batch in backward
    # Actually backward expects gradient of loss w.r.t. output, already averaged
    grad = 2.0 * diff
    return loss, grad


def r_squared(pred, target):
    """R-squared metric."""
    ss_res = np.sum((target - pred) ** 2)
    ss_tot = np.sum((target - np.mean(target)) ** 2)
    if ss_tot < 1e-12:
        return 0.0
    return 1.0 - ss_res / ss_tot


def lr_schedule(epoch, total_epochs, lr_init=LR_INIT):
    """Cosine annealing learning rate schedule."""
    return lr_init * 0.5 * (1 + np.cos(np.pi * epoch / total_epochs))


# ==============================================================================
# Task A: Standard Regression (sin(x) + noise)
# ==============================================================================
def generate_sin_data(n_samples, noise_std=0.1, x_range=(-np.pi, np.pi), rng=None):
    """Generate sin(x) + noise regression data."""
    if rng is None:
        rng = np.random.RandomState()
    x = rng.uniform(x_range[0], x_range[1], (n_samples, 1))
    y = np.sin(x) + noise_std * rng.randn(n_samples, 1)
    return x, y


def run_task_a(seed=42, T=DEFAULT_T, verbose=True):
    """
    Run Task A: sin(x) regression.
    Returns dict with training curves, w_self trajectory, final metrics.
    """
    set_seed(seed)
    rng = np.random.RandomState(seed)

    # Generate data
    x_train, y_train = generate_sin_data(N_TRAIN, rng=rng)
    x_test, y_test = generate_sin_data(N_TEST, rng=rng)

    # Create networks
    set_seed(seed)
    sru = SRUNetwork(T=T)
    set_seed(seed + 1000)
    baseline = BaselineNetwork()

    if verbose:
        print(f"  SRU params: {sru.param_count()}, Baseline params: {baseline.param_count()}")

    # Training records
    sru_train_loss = []
    sru_test_loss = []
    baseline_train_loss = []
    baseline_test_loss = []
    w_self_trajectory = []

    n_batches = max(1, N_TRAIN // BATCH_SIZE)

    for epoch in range(N_EPOCHS):
        lr = lr_schedule(epoch, N_EPOCHS)

        # Shuffle training data
        idx = rng.permutation(N_TRAIN)
        x_shuffled = x_train[idx]
        y_shuffled = y_train[idx]

        epoch_loss_sru = 0.0
        epoch_loss_base = 0.0

        for b in range(n_batches):
            start = b * BATCH_SIZE
            end = min(start + BATCH_SIZE, N_TRAIN)
            xb = x_shuffled[start:end]
            yb = y_shuffled[start:end]

            # SRU forward/backward
            pred_sru = sru.forward(xb)
            loss_sru, grad_sru = mse_loss(pred_sru, yb)
            grads_sru = sru.backward(grad_sru)
            sru.update(grads_sru, lr)
            epoch_loss_sru += loss_sru

            # Baseline forward/backward
            pred_base = baseline.forward(xb)
            loss_base, grad_base = mse_loss(pred_base, yb)
            grads_base = baseline.backward(grad_base)
            baseline.update(grads_base, lr)
            epoch_loss_base += loss_base

        # Record
        sru_train_loss.append(epoch_loss_sru / n_batches)
        baseline_train_loss.append(epoch_loss_base / n_batches)

        # Test loss
        pred_sru_test = sru.forward(x_test)
        loss_sru_test, _ = mse_loss(pred_sru_test, y_test)
        sru_test_loss.append(loss_sru_test)

        pred_base_test = baseline.forward(x_test)
        loss_base_test, _ = mse_loss(pred_base_test, y_test)
        baseline_test_loss.append(loss_base_test)

        w_self_trajectory.append(sru.w_self.copy())

    # Final metrics
    pred_sru_final = sru.forward(x_test)
    pred_base_final = baseline.forward(x_test)

    results = {
        'sru_train_loss': np.array(sru_train_loss),
        'sru_test_loss': np.array(sru_test_loss),
        'baseline_train_loss': np.array(baseline_train_loss),
        'baseline_test_loss': np.array(baseline_test_loss),
        'w_self_trajectory': np.array(w_self_trajectory),  # (epochs, n_sru)
        'w_self_final': sru.w_self.copy(),
        'sru_test_mse': float(mse_loss(pred_sru_final, y_test)[0]),
        'baseline_test_mse': float(mse_loss(pred_base_final, y_test)[0]),
        'sru_r2': float(r_squared(pred_sru_final, y_test)),
        'baseline_r2': float(r_squared(pred_base_final, y_test)),
        'sru_train_gap': float(sru_test_loss[-1] - sru_train_loss[-1]),
        'baseline_train_gap': float(baseline_test_loss[-1] - baseline_train_loss[-1]),
        'T': T,
        'seed': seed,
    }

    return results


# ==============================================================================
# Task B: Self-Referential Prediction
# ==============================================================================
def generate_signal(n_steps, rng=None):
    """Generate a smooth, predictable signal as sum of sinusoids."""
    if rng is None:
        rng = np.random.RandomState()
    t = np.arange(n_steps, dtype=float)
    # Sum of 3 sinusoids with incommensurate frequencies
    s = (0.5 * np.sin(2 * np.pi * t / 50.0)
         + 0.3 * np.sin(2 * np.pi * t / 31.0 + 0.7)
         + 0.2 * np.sin(2 * np.pi * t / 17.0 + 1.3))
    return s


def run_task_b_single(alpha, seed=42, T=DEFAULT_T):
    """
    Run Task B for a single alpha value.
    Online learning: at each step, agent predicts s(t) from contaminated y(t).
    y(t) = s(t) + alpha * agent_prediction(t-1)
    """
    set_seed(seed)
    rng = np.random.RandomState(seed)

    signal = generate_signal(N_TIMESTEPS, rng=rng)

    # Create networks
    set_seed(seed)
    sru = SRUNetwork(n_hidden=N_SRU, T=T)
    set_seed(seed + 1000)
    baseline = BaselineNetwork(n_hidden=N_BASELINE)

    # Online learning state
    sru_prev_pred = 0.0
    base_prev_pred = 0.0

    sru_errors = []
    base_errors = []
    w_self_online = []

    warmup = 100  # Don't measure first 100 steps

    for t in range(N_TIMESTEPS):
        s_t = signal[t]

        # Contaminated observations
        y_sru = s_t + alpha * sru_prev_pred
        y_base = s_t + alpha * base_prev_pred

        # Forward pass (single sample)
        x_sru = np.array([[y_sru]])
        x_base = np.array([[y_base]])

        pred_sru = sru.forward(x_sru)
        pred_base = baseline.forward(x_base)

        sru_pred_val = float(pred_sru[0, 0])
        base_pred_val = float(pred_base[0, 0])

        # True signal is revealed -- compute error
        sru_err = (sru_pred_val - s_t) ** 2
        base_err = (base_pred_val - s_t) ** 2

        if t >= warmup:
            sru_errors.append(sru_err)
            base_errors.append(base_err)

        # Online SGD update: target is s_t
        target = np.array([[s_t]])

        loss_sru, grad_sru = mse_loss(pred_sru, target)
        grads_sru = sru.backward(grad_sru)
        sru.update(grads_sru, ONLINE_LR, momentum=0.0)  # No momentum for online

        loss_base, grad_base = mse_loss(pred_base, target)
        grads_base = baseline.backward(grad_base)
        baseline.update(grads_base, ONLINE_LR, momentum=0.0)

        sru_prev_pred = sru_pred_val
        base_prev_pred = base_pred_val

        if t % 100 == 0:
            w_self_online.append(sru.w_self.copy())

    return {
        'alpha': alpha,
        'sru_mse': np.mean(sru_errors),
        'baseline_mse': np.mean(base_errors),
        'w_self_final': sru.w_self.copy(),
        'w_self_mean': float(np.mean(sru.w_self)),
        'w_self_online': np.array(w_self_online) if w_self_online else None,
        'seed': seed,
    }


# ==============================================================================
# Main experiment runners
# ==============================================================================
def run_all_task_a(verbose=True):
    """Run Task A across all seeds."""
    if verbose:
        print("\n" + "=" * 70)
        print("TASK A: Standard Regression (sin(x) + noise)")
        print("=" * 70)

    all_results = []
    for seed in SEEDS:
        if verbose:
            print(f"\n  Seed {seed}...")
        result = run_task_a(seed=seed, T=DEFAULT_T, verbose=verbose)
        all_results.append(result)

    return all_results


def run_all_task_b(verbose=True):
    """Run Task B across all alpha values and seeds."""
    if verbose:
        print("\n" + "=" * 70)
        print("TASK B: Self-Referential Prediction")
        print("=" * 70)

    all_results = {}
    for alpha in ALPHA_VALUES:
        if verbose:
            print(f"\n  alpha = {alpha:.1f}...")
        seed_results = []
        for seed in SEEDS:
            result = run_task_b_single(alpha, seed=seed, T=DEFAULT_T)
            seed_results.append(result)
        all_results[alpha] = seed_results

    return all_results


def run_t_sweep(verbose=True):
    """Run Task A across different T values."""
    if verbose:
        print("\n" + "=" * 70)
        print("T SWEEP: Effect of unroll depth on w_self convergence")
        print("=" * 70)

    all_results = {}
    for T in T_VALUES:
        if verbose:
            print(f"\n  T = {T}...")
        seed_results = []
        for seed in SEEDS:
            result = run_task_a(seed=seed, T=T, verbose=False)
            seed_results.append(result)
        all_results[T] = seed_results

    return all_results


# ==============================================================================
# Analysis and printing
# ==============================================================================
def print_task_a_results(results):
    """Print Task A results table."""
    print("\n" + "-" * 70)
    print("TASK A RESULTS: sin(x) Regression")
    print("-" * 70)
    print(f"{'Seed':>6} {'SRU MSE':>10} {'Base MSE':>10} {'SRU R2':>8} {'Base R2':>8} {'w_self mean':>12} {'w_self std':>11}")
    print("-" * 70)

    sru_mses = []
    base_mses = []
    sru_r2s = []
    base_r2s = []
    all_w_self = []

    for r in results:
        w_mean = np.mean(r['w_self_final'])
        w_std = np.std(r['w_self_final'])
        print(f"{r['seed']:>6} {r['sru_test_mse']:>10.6f} {r['baseline_test_mse']:>10.6f} "
              f"{r['sru_r2']:>8.4f} {r['baseline_r2']:>8.4f} {w_mean:>12.6f} {w_std:>11.6f}")
        sru_mses.append(r['sru_test_mse'])
        base_mses.append(r['baseline_test_mse'])
        sru_r2s.append(r['sru_r2'])
        base_r2s.append(r['baseline_r2'])
        all_w_self.extend(r['w_self_final'].tolist())

    print("-" * 70)
    print(f"{'MEAN':>6} {np.mean(sru_mses):>10.6f} {np.mean(base_mses):>10.6f} "
          f"{np.mean(sru_r2s):>8.4f} {np.mean(base_r2s):>8.4f} "
          f"{np.mean(all_w_self):>12.6f} {np.std(all_w_self):>11.6f}")

    print(f"\n  Reference values: 1/phi = {INV_PHI:.6f}, True optimum = {TRUE_OPT:.6f}")
    mean_w = np.mean(all_w_self)
    print(f"  w_self mean = {mean_w:.6f}")
    print(f"  Distance to 1/phi: {abs(mean_w - INV_PHI):.6f}")
    print(f"  Distance to 0.525: {abs(mean_w - TRUE_OPT):.6f}")

    # Generalization gap
    sru_gaps = [r['sru_train_gap'] for r in results]
    base_gaps = [r['baseline_train_gap'] for r in results]
    print(f"\n  Generalization gap (test - train MSE):")
    print(f"    SRU:      {np.mean(sru_gaps):.6f} +/- {np.std(sru_gaps):.6f}")
    print(f"    Baseline: {np.mean(base_gaps):.6f} +/- {np.std(base_gaps):.6f}")


def print_task_b_results(results):
    """Print Task B results table."""
    print("\n" + "-" * 70)
    print("TASK B RESULTS: Self-Referential Prediction")
    print("-" * 70)
    print(f"{'alpha':>6} {'SRU MSE':>10} {'Base MSE':>10} {'Ratio':>8} {'SRU better?':>12} {'w_self mean':>12}")
    print("-" * 70)

    for alpha in ALPHA_VALUES:
        seed_results = results[alpha]
        sru_mse = np.mean([r['sru_mse'] for r in seed_results])
        base_mse = np.mean([r['baseline_mse'] for r in seed_results])
        w_mean = np.mean([r['w_self_mean'] for r in seed_results])

        ratio = sru_mse / base_mse if base_mse > 1e-12 else float('inf')
        better = "YES" if sru_mse < base_mse else "no"

        print(f"{alpha:>6.1f} {sru_mse:>10.6f} {base_mse:>10.6f} "
              f"{ratio:>8.4f} {better:>12} {w_mean:>12.6f}")

    print("-" * 70)

    # Summary
    high_alpha = [a for a in ALPHA_VALUES if a >= 0.5]
    sru_wins_high = 0
    for a in high_alpha:
        sru_mse = np.mean([r['sru_mse'] for r in results[a]])
        base_mse = np.mean([r['baseline_mse'] for r in results[a]])
        if sru_mse < base_mse:
            sru_wins_high += 1

    print(f"\n  SRU wins at high alpha (>=0.5): {sru_wins_high}/{len(high_alpha)}")
    print(f"  Reference: 1/phi = {INV_PHI:.6f}, True optimum = {TRUE_OPT:.6f}")


def print_t_sweep_results(results):
    """Print T sweep results table."""
    print("\n" + "-" * 70)
    print("T SWEEP RESULTS: Effect of Unroll Depth on w_self")
    print("-" * 70)
    print(f"{'T':>4} {'w_self mean':>12} {'w_self std':>11} {'dist(1/phi)':>12} {'dist(0.525)':>12} {'SRU MSE':>10} {'R2':>8}")
    print("-" * 70)

    for T in T_VALUES:
        seed_results = results[T]
        all_w = np.concatenate([r['w_self_final'] for r in seed_results])
        w_mean = np.mean(all_w)
        w_std = np.std(all_w)
        mse_mean = np.mean([r['sru_test_mse'] for r in seed_results])
        r2_mean = np.mean([r['sru_r2'] for r in seed_results])

        print(f"{T:>4} {w_mean:>12.6f} {w_std:>11.6f} "
              f"{abs(w_mean - INV_PHI):>12.6f} {abs(w_mean - TRUE_OPT):>12.6f} "
              f"{mse_mean:>10.6f} {r2_mean:>8.4f}")

    print("-" * 70)
    print(f"  Reference: 1/phi = {INV_PHI:.6f}, True optimum = {TRUE_OPT:.6f}")

    # Check prediction: small T -> 1/phi, large T -> 0.525
    small_T_results = results[T_VALUES[0]]
    large_T_results = results[T_VALUES[-1]]
    small_w = np.mean(np.concatenate([r['w_self_final'] for r in small_T_results]))
    large_w = np.mean(np.concatenate([r['w_self_final'] for r in large_T_results]))

    print(f"\n  T={T_VALUES[0]} mean w_self: {small_w:.6f} (closer to {'1/phi' if abs(small_w - INV_PHI) < abs(small_w - TRUE_OPT) else '0.525'})")
    print(f"  T={T_VALUES[-1]} mean w_self: {large_w:.6f} (closer to {'1/phi' if abs(large_w - INV_PHI) < abs(large_w - TRUE_OPT) else '0.525'})")


# ==============================================================================
# Plotting
# ==============================================================================
def create_plots(task_a_results, task_b_results, t_sweep_results):
    """Generate 8-panel results plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(4, 2, figsize=(14, 20))
    fig.suptitle("Self-Referential Unit (SRU) as ML Primitive", fontsize=14, fontweight='bold')

    # Colors
    c_sru = '#2196F3'
    c_base = '#FF5722'
    c_phi = '#4CAF50'
    c_opt = '#9C27B0'

    # --- Panel 1: Task A training curves ---
    ax = axes[0, 0]
    for r in task_a_results:
        ax.plot(r['sru_train_loss'], color=c_sru, alpha=0.3, linewidth=0.8)
        ax.plot(r['baseline_train_loss'], color=c_base, alpha=0.3, linewidth=0.8)
    # Mean curves
    mean_sru = np.mean([r['sru_train_loss'] for r in task_a_results], axis=0)
    mean_base = np.mean([r['baseline_train_loss'] for r in task_a_results], axis=0)
    ax.plot(mean_sru, color=c_sru, linewidth=2, label='SRU')
    ax.plot(mean_base, color=c_base, linewidth=2, label='Baseline')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Training MSE')
    ax.set_title('Task A: Training Curves')
    ax.legend()
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)

    # --- Panel 2: w_self trajectories ---
    ax = axes[0, 1]
    for r in task_a_results:
        traj = r['w_self_trajectory']  # (epochs, n_sru)
        for i in range(traj.shape[1]):
            ax.plot(traj[:, i], color=c_sru, alpha=0.1, linewidth=0.5)
        ax.plot(np.mean(traj, axis=1), color=c_sru, linewidth=1.5, alpha=0.5)
    # Mean across all
    all_traj = np.mean([r['w_self_trajectory'] for r in task_a_results], axis=0)
    ax.plot(np.mean(all_traj, axis=1), color='black', linewidth=2, label='Grand mean')
    ax.axhline(y=INV_PHI, color=c_phi, linestyle='--', linewidth=1.5, label=f'1/phi = {INV_PHI:.3f}')
    ax.axhline(y=TRUE_OPT, color=c_opt, linestyle=':', linewidth=1.5, label=f'True opt = {TRUE_OPT:.3f}')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('w_self')
    ax.set_title('Task A: w_self Trajectories')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # --- Panel 3: Task B MSE vs alpha (THE MONEY PLOT) ---
    ax = axes[1, 0]
    alphas = np.array(ALPHA_VALUES)
    sru_mses = []
    base_mses = []
    sru_stds = []
    base_stds = []
    for a in ALPHA_VALUES:
        sru_vals = [r['sru_mse'] for r in task_b_results[a]]
        base_vals = [r['baseline_mse'] for r in task_b_results[a]]
        sru_mses.append(np.mean(sru_vals))
        base_mses.append(np.mean(base_vals))
        sru_stds.append(np.std(sru_vals))
        base_stds.append(np.std(base_vals))

    sru_mses = np.array(sru_mses)
    base_mses = np.array(base_mses)
    sru_stds = np.array(sru_stds)
    base_stds = np.array(base_stds)

    ax.errorbar(alphas, sru_mses, yerr=sru_stds, color=c_sru, marker='o', linewidth=2,
                capsize=3, label='SRU')
    ax.errorbar(alphas, base_mses, yerr=base_stds, color=c_base, marker='s', linewidth=2,
                capsize=3, label='Baseline')
    ax.set_xlabel('alpha (self-reference strength)')
    ax.set_ylabel('Test MSE')
    ax.set_title('Task B: MSE vs alpha (Money Plot)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- Panel 4: Relative advantage vs alpha ---
    ax = axes[1, 1]
    # Relative advantage = (baseline - sru) / baseline * 100
    with np.errstate(divide='ignore', invalid='ignore'):
        advantage = np.where(base_mses > 1e-12,
                             (base_mses - sru_mses) / base_mses * 100,
                             0.0)
    ax.bar(alphas, advantage, width=0.08, color=c_sru, alpha=0.7, edgecolor='black')
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_xlabel('alpha (self-reference strength)')
    ax.set_ylabel('SRU advantage (%)')
    ax.set_title('Task B: SRU Relative Advantage')
    ax.grid(True, alpha=0.3, axis='y')

    # --- Panel 5: w_self histogram ---
    ax = axes[2, 0]
    all_w_self = []
    for r in task_a_results:
        all_w_self.extend(r['w_self_final'].tolist())
    for a in ALPHA_VALUES:
        for r in task_b_results[a]:
            all_w_self.extend(r['w_self_final'].tolist())
    for T in T_VALUES:
        for r in t_sweep_results[T]:
            all_w_self.extend(r['w_self_final'].tolist())

    ax.hist(all_w_self, bins=40, color=c_sru, alpha=0.7, edgecolor='black', density=True)
    ax.axvline(x=INV_PHI, color=c_phi, linestyle='--', linewidth=2, label=f'1/phi = {INV_PHI:.3f}')
    ax.axvline(x=TRUE_OPT, color=c_opt, linestyle=':', linewidth=2, label=f'True opt = {TRUE_OPT:.3f}')
    ax.set_xlabel('w_self')
    ax.set_ylabel('Density')
    ax.set_title('w_self Distribution (All Experiments)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- Panel 6: w_self vs alpha (Task B) ---
    ax = axes[2, 1]
    w_means = []
    w_stds = []
    for a in ALPHA_VALUES:
        ws = [r['w_self_mean'] for r in task_b_results[a]]
        w_means.append(np.mean(ws))
        w_stds.append(np.std(ws))

    ax.errorbar(alphas, w_means, yerr=w_stds, color=c_sru, marker='o', linewidth=2, capsize=3)
    ax.axhline(y=INV_PHI, color=c_phi, linestyle='--', linewidth=1.5, label=f'1/phi = {INV_PHI:.3f}')
    ax.axhline(y=TRUE_OPT, color=c_opt, linestyle=':', linewidth=1.5, label=f'True opt = {TRUE_OPT:.3f}')
    ax.set_xlabel('alpha (self-reference strength)')
    ax.set_ylabel('Mean w_self')
    ax.set_title('Task B: w_self vs alpha')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # --- Panel 7: T sweep w_self convergence ---
    ax = axes[3, 0]
    t_vals = []
    t_w_means = []
    t_w_stds = []
    for T in T_VALUES:
        all_w = np.concatenate([r['w_self_final'] for r in t_sweep_results[T]])
        t_vals.append(T)
        t_w_means.append(np.mean(all_w))
        t_w_stds.append(np.std(all_w))

    ax.errorbar(t_vals, t_w_means, yerr=t_w_stds, color=c_sru, marker='o', linewidth=2,
                capsize=3, markersize=8)
    ax.axhline(y=INV_PHI, color=c_phi, linestyle='--', linewidth=1.5, label=f'1/phi = {INV_PHI:.3f}')
    ax.axhline(y=TRUE_OPT, color=c_opt, linestyle=':', linewidth=1.5, label=f'True opt = {TRUE_OPT:.3f}')
    ax.set_xlabel('T (unroll steps)')
    ax.set_ylabel('Mean w_self')
    ax.set_title('T Sweep: w_self vs Unroll Depth')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(T_VALUES)

    # --- Panel 8: Generalization gap vs alpha ---
    ax = axes[3, 1]
    # For Task B we use the error after warmup as "test" and first 100 as "train" proxy
    # Actually, let's use Task A generalization gap across T values
    sru_gaps = []
    base_gaps = []
    for T in T_VALUES:
        sg = np.mean([r['sru_train_gap'] for r in t_sweep_results[T]])
        bg = np.mean([r['baseline_train_gap'] for r in t_sweep_results[T]])
        sru_gaps.append(sg)
        base_gaps.append(bg)

    x_pos = np.arange(len(T_VALUES))
    width = 0.35
    ax.bar(x_pos - width/2, sru_gaps, width, color=c_sru, alpha=0.7, label='SRU', edgecolor='black')
    ax.bar(x_pos + width/2, base_gaps, width, color=c_base, alpha=0.7, label='Baseline', edgecolor='black')
    ax.set_xlabel('T (unroll steps)')
    ax.set_ylabel('Generalization Gap (test - train MSE)')
    ax.set_title('Generalization Gap vs T')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(t) for t in T_VALUES])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sru_ml_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 70)
    print("SRU ML EXPERIMENT: Self-Referential Unit as ML Primitive")
    print("=" * 70)
    print(f"  SRU hidden units: {N_SRU}")
    print(f"  Baseline hidden units: {N_BASELINE}")
    print(f"  Default T (unroll steps): {DEFAULT_T}")
    print(f"  Seeds: {SEEDS}")
    print(f"  Reference: 1/phi = {INV_PHI:.6f}, True optimum = {TRUE_OPT:.6f}")

    t_start = time.time()

    # ---- Task A ----
    t0 = time.time()
    task_a_results = run_all_task_a(verbose=True)
    print(f"\n  Task A completed in {time.time() - t0:.1f}s")
    print_task_a_results(task_a_results)

    # Check for NaN
    any_nan = False
    for r in task_a_results:
        if np.isnan(r['sru_test_mse']) or np.isnan(r['baseline_test_mse']):
            print("  WARNING: NaN detected in Task A!")
            any_nan = True

    # ---- Task B ----
    t0 = time.time()
    task_b_results = run_all_task_b(verbose=True)
    print(f"\n  Task B completed in {time.time() - t0:.1f}s")
    print_task_b_results(task_b_results)

    # Check for NaN
    for a in ALPHA_VALUES:
        for r in task_b_results[a]:
            if np.isnan(r['sru_mse']) or np.isnan(r['baseline_mse']):
                print(f"  WARNING: NaN detected in Task B at alpha={a}!")
                any_nan = True

    # ---- T Sweep ----
    t0 = time.time()
    t_sweep_results = run_t_sweep(verbose=True)
    print(f"\n  T sweep completed in {time.time() - t0:.1f}s")
    print_t_sweep_results(t_sweep_results)

    # ---- Summary ----
    total_time = time.time() - t_start
    print("\n" + "=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)
    print(f"  Total runtime: {total_time:.1f}s")
    print(f"  Any NaN/divergence: {'YES' if any_nan else 'No'}")

    # Key findings
    all_w_task_a = np.concatenate([r['w_self_final'] for r in task_a_results])
    mean_w_a = np.mean(all_w_task_a)
    print(f"\n  KEY FINDINGS:")
    print(f"  1. Task A w_self mean: {mean_w_a:.6f}")
    print(f"     Closer to: {'1/phi' if abs(mean_w_a - INV_PHI) < abs(mean_w_a - TRUE_OPT) else '0.525'}")

    # Task B: count SRU wins
    sru_wins = 0
    total_alphas = len(ALPHA_VALUES)
    for a in ALPHA_VALUES:
        sru_mse = np.mean([r['sru_mse'] for r in task_b_results[a]])
        base_mse = np.mean([r['baseline_mse'] for r in task_b_results[a]])
        if sru_mse < base_mse:
            sru_wins += 1

    print(f"  2. Task B: SRU wins {sru_wins}/{total_alphas} alpha values")

    high_alpha_wins = 0
    high_alpha_count = 0
    for a in ALPHA_VALUES:
        if a >= 0.5:
            high_alpha_count += 1
            sru_mse = np.mean([r['sru_mse'] for r in task_b_results[a]])
            base_mse = np.mean([r['baseline_mse'] for r in task_b_results[a]])
            if sru_mse < base_mse:
                high_alpha_wins += 1
    print(f"     SRU wins at high alpha (>=0.5): {high_alpha_wins}/{high_alpha_count}")

    # T sweep: gradient
    small_w = np.mean(np.concatenate([r['w_self_final'] for r in t_sweep_results[T_VALUES[0]]]))
    large_w = np.mean(np.concatenate([r['w_self_final'] for r in t_sweep_results[T_VALUES[-1]]]))
    print(f"  3. T sweep: T={T_VALUES[0]} w_self={small_w:.6f}, T={T_VALUES[-1]} w_self={large_w:.6f}")
    print(f"     Trend: {'increasing with T' if large_w > small_w else 'decreasing with T'}")

    # Success criteria check
    print(f"\n  SUCCESS CRITERIA CHECK:")
    mean_r2 = np.mean([r['sru_r2'] for r in task_a_results])
    print(f"  [{'PASS' if mean_r2 > 0.5 else 'FAIL'}] SRU R2 > 0.5 on Task A: R2 = {mean_r2:.4f}")
    w_std = np.std(all_w_task_a)
    print(f"  [{'PASS' if w_std < 0.5 else 'FAIL'}] w_self converges (std < 0.5): std = {w_std:.4f}")
    close_to_phi = abs(mean_w_a - INV_PHI) < 0.15
    close_to_opt = abs(mean_w_a - TRUE_OPT) < 0.15
    print(f"  [{'PASS' if close_to_phi else 'FAIL'}] w_self near 1/phi (within 0.15): dist = {abs(mean_w_a - INV_PHI):.4f}")
    print(f"  [{'PASS' if close_to_opt else 'FAIL'}] w_self near 0.525 (within 0.15): dist = {abs(mean_w_a - TRUE_OPT):.4f}")
    print(f"  [{'PASS' if high_alpha_wins > 0 else 'FAIL'}] SRU advantage at high alpha: {high_alpha_wins}/{high_alpha_count}")

    # ---- Plots ----
    create_plots(task_a_results, task_b_results, t_sweep_results)

    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
