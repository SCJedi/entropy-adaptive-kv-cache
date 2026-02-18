"""
Pseudo-Labeling with Over-Relaxation: Real ML Validation
=========================================================
Tests whether the self-referential theory (kw^2 + w - 1 = 0, the 8.3%
self-ignorance gap, over-relaxation fix) predicts real improvements on
a real ML task.

Pseudo-labeling is a genuine self-referential ML technique:
  1. Train model on labeled data
  2. Use model to label unlabeled data (pseudo-labels)
  3. Retrain on labeled + pseudo-labeled data
  4. Repeat -- the model trains on its own predictions

The contamination parameter alpha = fraction of training data that is
pseudo-labeled. This is EXACTLY the self-referential framework.

Three fixes tested:
  - Standard pseudo-labeling (myopic, omega=1.0)
  - Over-relaxed pseudo-labeling (Fix 1: omega > 1.0 sample weight)
  - Dual-model pseudo-labeling (Fix 2: cross-labeling)

Dataset: sklearn digits (8x8 images, 10 classes, 1797 samples) if
available, else synthetic digit-like data via numpy.

All from scratch with numpy (no sklearn dependency).
"""

import sys
import io
import time
import os
import warnings
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

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ==============================================================================
# Constants
# ==============================================================================
PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1.0 / PHI

N_LABELED = 100
N_UNLABELED = 1000
N_TEST = 500
N_CLASSES = 10
N_SEEDS = 10
N_ROUNDS = 5
CONFIDENCE_THRESHOLD = 0.7
LR = 0.05
N_EPOCHS = 120
BATCH_SIZE = 64
REG_LAMBDA = 1e-4  # L2 regularization

ALPHA_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
OMEGA_VALUES = [1.0, 1.05, 1.1, 1.15, 1.2, 1.3, 1.5, 1.8, 2.0]


# ==============================================================================
# Data Loading
# ==============================================================================
def load_digits_data():
    """Load sklearn digits if available, else generate synthetic data."""
    try:
        from sklearn.datasets import load_digits
        digits = load_digits()
        X = digits.data.astype(np.float64)
        y = digits.target.astype(np.int64)
        print(f"Loaded sklearn digits: {X.shape[0]} samples, {X.shape[1]} features, {N_CLASSES} classes")
        return X, y
    except ImportError:
        pass

    # Synthetic classification data with GOLDILOCKS difficulty:
    # - Baseline accuracy ~70-80% with 100 labeled samples
    # - 3 pairs of confusable classes (0-1, 2-3, 4-5) + 4 easy classes (6-9)
    # - Model can be confident AND wrong on confusable pairs
    # - This is critical: pseudo-label contamination only matters when
    #   confident wrong labels exist
    print("sklearn not available. Generating Goldilocks-difficulty synthetic data...")
    rng = np.random.RandomState(999)
    n_total = 1800
    n_features = 20
    n_classes = N_CLASSES
    signal_scale = 3.0
    noise_base = 1.0

    # Create class centroids using sinusoidal patterns
    centroids = np.zeros((n_classes, n_features))
    for c in range(n_classes):
        for f in range(n_features):
            centroids[c, f] = np.sin(2 * np.pi * c * (f + 1) / n_classes) * signal_scale

    # Make 3 pairs VERY confusable (classes 0-1, 2-3, 4-5)
    # These pairs will generate confident-but-wrong pseudo-labels
    for i in [0, 2, 4]:
        mid = 0.5 * (centroids[i] + centroids[i + 1])
        centroids[i] = mid + 0.15 * (centroids[i] - mid)
        centroids[i + 1] = mid + 0.15 * (centroids[i + 1] - mid)

    X_list, y_list = [], []
    for c in range(n_classes):
        n_c = n_total // n_classes
        noise_scale = noise_base + 0.2 * np.sin(c)
        noise = rng.randn(n_c, n_features) * noise_scale
        X_c = centroids[c] + noise
        X_list.append(X_c)
        y_list.append(np.full(n_c, c, dtype=np.int64))

    X = np.vstack(X_list)
    y = np.concatenate(y_list)

    # Shuffle
    idx = rng.permutation(len(y))
    X, y = X[idx], y[idx]

    # Standardize to zero mean, unit variance per feature
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    # Verify difficulty
    check_rng = np.random.RandomState(42)
    check_W = check_rng.randn(n_features, n_classes) * 0.01
    check_b = np.zeros(n_classes)
    check_W, check_b = train_logistic(X[:100], y[:100], W_init=check_W,
                                       b_init=check_b, n_epochs=200, rng=check_rng)
    check_acc = accuracy(X[500:1000], y[500:1000], check_W, check_b)
    print(f"Generated synthetic data: {X.shape[0]} samples, {n_features} features, {n_classes} classes")
    print(f"  3 confusable pairs (0-1, 2-3, 4-5) + 4 easy classes (6-9)")
    print(f"  Difficulty check: {check_acc:.3f} accuracy (target: 0.70-0.80)")

    return X, y


def split_data(X, y, rng):
    """Split into labeled, unlabeled, and test sets."""
    n = len(y)
    idx = rng.permutation(n)

    # Stratified split: ensure each class represented in labeled set
    labeled_idx = []
    remaining_idx = list(range(n))
    rng.shuffle(remaining_idx)

    # First, pick at least a few per class for labeled set
    per_class = max(2, N_LABELED // N_CLASSES)
    for c in range(N_CLASSES):
        class_idx = [i for i in remaining_idx if y[i] == c]
        take = min(per_class, len(class_idx))
        labeled_idx.extend(class_idx[:take])

    # Fill rest of labeled quota randomly from remaining
    used = set(labeled_idx)
    rest = [i for i in remaining_idx if i not in used]
    rng.shuffle(rest)
    need = N_LABELED - len(labeled_idx)
    if need > 0:
        labeled_idx.extend(rest[:need])
        rest = rest[need:]

    # From rest, split into unlabeled and test
    n_unlab = min(N_UNLABELED, len(rest) - N_TEST)
    unlabeled_idx = rest[:n_unlab]
    test_idx = rest[n_unlab:n_unlab + N_TEST]

    X_lab, y_lab = X[labeled_idx], y[labeled_idx]
    X_unlab, y_unlab = X[unlabeled_idx], y[unlabeled_idx]  # y_unlab for measuring PL accuracy
    X_test, y_test = X[test_idx], y[test_idx]

    return X_lab, y_lab, X_unlab, y_unlab, X_test, y_test


# ==============================================================================
# Logistic Regression (Softmax, from scratch)
# ==============================================================================
def softmax(logits):
    """Numerically stable softmax."""
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp_s = np.exp(shifted)
    return exp_s / exp_s.sum(axis=1, keepdims=True)


def predict_proba(X, W, b):
    """Compute class probabilities."""
    logits = X @ W + b
    return softmax(logits)


def predict(X, W, b):
    """Predict class labels."""
    probs = predict_proba(X, W, b)
    return np.argmax(probs, axis=1)


def accuracy(X, y, W, b):
    """Compute classification accuracy."""
    preds = predict(X, W, b)
    return np.mean(preds == y)


def cross_entropy_loss(X, y, W, b, sample_weights=None):
    """Cross-entropy loss with optional sample weights and L2 reg."""
    probs = predict_proba(X, W, b)
    n = len(y)
    # Clip for numerical stability
    probs_clipped = np.clip(probs, 1e-12, 1.0)
    log_probs = np.log(probs_clipped)

    # Per-sample loss
    losses = -log_probs[np.arange(n), y]

    if sample_weights is not None:
        loss = np.sum(losses * sample_weights) / np.sum(sample_weights)
    else:
        loss = np.mean(losses)

    # L2 regularization
    loss += 0.5 * REG_LAMBDA * np.sum(W * W)
    return loss


def train_logistic(X, y, W_init=None, b_init=None, n_epochs=N_EPOCHS,
                   lr=LR, sample_weights=None, rng=None):
    """Train logistic regression with mini-batch SGD.

    sample_weights: per-sample weight array (for over-relaxation).
    """
    n, d = X.shape
    if W_init is not None:
        W = W_init.copy()
        b = b_init.copy()
    else:
        if rng is None:
            rng = np.random.RandomState(42)
        W = rng.randn(d, N_CLASSES) * 0.01
        b = np.zeros(N_CLASSES)

    if sample_weights is None:
        sample_weights = np.ones(n)

    for epoch in range(n_epochs):
        # Shuffle
        idx = rng.permutation(n) if rng else np.random.permutation(n)

        for start in range(0, n, BATCH_SIZE):
            end = min(start + BATCH_SIZE, n)
            batch_idx = idx[start:end]
            X_b = X[batch_idx]
            y_b = y[batch_idx]
            sw_b = sample_weights[batch_idx]
            bs = len(y_b)

            # Forward
            probs = predict_proba(X_b, W, b)

            # Gradient of cross-entropy
            grad_probs = probs.copy()
            grad_probs[np.arange(bs), y_b] -= 1.0  # (bs, C)

            # Apply sample weights
            weighted_grad = grad_probs * sw_b[:, None]  # (bs, C)

            # Gradients
            dW = (X_b.T @ weighted_grad) / np.sum(sw_b) + REG_LAMBDA * W
            db = weighted_grad.sum(axis=0) / np.sum(sw_b)

            # Update
            W -= lr * dW
            b -= lr * db

    return W, b


# ==============================================================================
# Pseudo-Labeling Engine
# ==============================================================================
def generate_pseudo_labels(X_unlab, W, b, threshold=CONFIDENCE_THRESHOLD):
    """Generate pseudo-labels for unlabeled data.

    Returns: pseudo_labels, confidences, mask (which samples are above threshold)
    """
    probs = predict_proba(X_unlab, W, b)
    confidences = probs.max(axis=1)
    pseudo_labels = np.argmax(probs, axis=1)
    mask = confidences >= threshold

    return pseudo_labels, confidences, mask


def run_standard_pseudolabeling(X_lab, y_lab, X_unlab, y_unlab_true,
                                 X_test, y_test, alpha, omega=1.0,
                                 n_rounds=N_ROUNDS, rng=None):
    """Run pseudo-labeling with given alpha (contamination) and omega (over-relaxation).

    Returns dict with per-round metrics.
    """
    if rng is None:
        rng = np.random.RandomState(42)

    n_features = X_lab.shape[1]
    W = rng.randn(n_features, N_CLASSES) * 0.01
    b = np.zeros(N_CLASSES)

    results = {
        "test_acc": [],
        "pl_acc": [],       # accuracy of pseudo-labels (vs true labels)
        "n_pl": [],         # number of pseudo-labels used
        "train_acc": [],
    }

    # Initial training on labeled data only
    W, b = train_logistic(X_lab, y_lab, W_init=W, b_init=b,
                          n_epochs=N_EPOCHS, rng=rng)

    for round_i in range(n_rounds):
        # Generate pseudo-labels
        pl_labels, pl_conf, pl_mask = generate_pseudo_labels(X_unlab, W, b)

        # How many confident pseudo-labels?
        n_confident = pl_mask.sum()

        if n_confident == 0:
            # No confident predictions -- use labeled only
            results["test_acc"].append(accuracy(X_test, y_test, W, b))
            results["pl_acc"].append(0.0)
            results["n_pl"].append(0)
            results["train_acc"].append(accuracy(X_lab, y_lab, W, b))
            continue

        # Select alpha-fraction of confident pseudo-labels
        confident_idx = np.where(pl_mask)[0]
        n_use = max(1, int(alpha * len(confident_idx)))
        selected_idx = rng.choice(confident_idx, size=n_use, replace=False)

        X_pl = X_unlab[selected_idx]
        y_pl = pl_labels[selected_idx]

        # Measure pseudo-label accuracy
        pl_acc = np.mean(y_pl == y_unlab_true[selected_idx])

        # Combine labeled + pseudo-labeled
        X_train = np.vstack([X_lab, X_pl])
        y_train = np.concatenate([y_lab, y_pl])

        # Sample weights: labeled=1.0, pseudo-labeled=omega
        sw = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl), omega)])

        # Retrain from current weights (warm start)
        W, b = train_logistic(X_train, y_train, W_init=W, b_init=b,
                              n_epochs=N_EPOCHS // 2, sample_weights=sw, rng=rng)

        results["test_acc"].append(accuracy(X_test, y_test, W, b))
        results["pl_acc"].append(pl_acc)
        results["n_pl"].append(n_use)
        results["train_acc"].append(accuracy(X_train, y_train, W, b))

    return results


def run_dual_model_pseudolabeling(X_lab, y_lab, X_unlab, y_unlab_true,
                                   X_test, y_test, alpha,
                                   n_rounds=N_ROUNDS, rng=None):
    """Run dual-model pseudo-labeling (Fix 2).

    Two models: M_A and M_B.
    M_A pseudo-labels for M_B, M_B pseudo-labels for M_A.
    Neither trains on its own pseudo-labels.
    """
    if rng is None:
        rng = np.random.RandomState(42)

    n_features = X_lab.shape[1]

    # Initialize two models differently
    W_A = rng.randn(n_features, N_CLASSES) * 0.01
    b_A = np.zeros(N_CLASSES)
    W_B = rng.randn(n_features, N_CLASSES) * 0.01
    b_B = np.zeros(N_CLASSES)

    results = {
        "test_acc": [],
        "pl_acc": [],
        "n_pl": [],
        "train_acc": [],
    }

    # Initial training on labeled data
    W_A, b_A = train_logistic(X_lab, y_lab, W_init=W_A, b_init=b_A,
                               n_epochs=N_EPOCHS, rng=rng)
    W_B, b_B = train_logistic(X_lab, y_lab, W_init=W_B, b_init=b_B,
                               n_epochs=N_EPOCHS, rng=rng)

    for round_i in range(n_rounds):
        # M_A generates pseudo-labels for M_B
        pl_A, conf_A, mask_A = generate_pseudo_labels(X_unlab, W_A, b_A)
        # M_B generates pseudo-labels for M_A
        pl_B, conf_B, mask_B = generate_pseudo_labels(X_unlab, W_B, b_B)

        # Select alpha-fraction of confident labels from each
        n_conf_A = mask_A.sum()
        n_conf_B = mask_B.sum()

        if n_conf_A == 0 and n_conf_B == 0:
            acc_avg = 0.5 * (accuracy(X_test, y_test, W_A, b_A) +
                             accuracy(X_test, y_test, W_B, b_B))
            results["test_acc"].append(acc_avg)
            results["pl_acc"].append(0.0)
            results["n_pl"].append(0)
            results["train_acc"].append(0.0)
            continue

        # For model B: use A's pseudo-labels
        if n_conf_A > 0:
            conf_A_idx = np.where(mask_A)[0]
            n_use_A = max(1, int(alpha * len(conf_A_idx)))
            sel_A = rng.choice(conf_A_idx, size=n_use_A, replace=False)
            X_pl_for_B = X_unlab[sel_A]
            y_pl_for_B = pl_A[sel_A]
            X_train_B = np.vstack([X_lab, X_pl_for_B])
            y_train_B = np.concatenate([y_lab, y_pl_for_B])
        else:
            X_train_B = X_lab.copy()
            y_train_B = y_lab.copy()
            sel_A = np.array([], dtype=int)

        # For model A: use B's pseudo-labels
        if n_conf_B > 0:
            conf_B_idx = np.where(mask_B)[0]
            n_use_B = max(1, int(alpha * len(conf_B_idx)))
            sel_B = rng.choice(conf_B_idx, size=n_use_B, replace=False)
            X_pl_for_A = X_unlab[sel_B]
            y_pl_for_A = pl_B[sel_B]
            X_train_A = np.vstack([X_lab, X_pl_for_A])
            y_train_A = np.concatenate([y_lab, y_pl_for_A])
        else:
            X_train_A = X_lab.copy()
            y_train_A = y_lab.copy()
            sel_B = np.array([], dtype=int)

        # Retrain
        W_A, b_A = train_logistic(X_train_A, y_train_A, W_init=W_A, b_init=b_A,
                                   n_epochs=N_EPOCHS // 2, rng=rng)
        W_B, b_B = train_logistic(X_train_B, y_train_B, W_init=W_B, b_init=b_B,
                                   n_epochs=N_EPOCHS // 2, rng=rng)

        # Ensemble prediction for test accuracy
        probs_A = predict_proba(X_test, W_A, b_A)
        probs_B = predict_proba(X_test, W_B, b_B)
        ensemble_preds = np.argmax(probs_A + probs_B, axis=1)
        test_acc = np.mean(ensemble_preds == y_test)

        # Pseudo-label accuracy: average of both
        pl_acc_parts = []
        if len(sel_A) > 0:
            pl_acc_parts.append(np.mean(pl_A[sel_A] == y_unlab_true[sel_A]))
        if len(sel_B) > 0:
            pl_acc_parts.append(np.mean(pl_B[sel_B] == y_unlab_true[sel_B]))
        pl_acc = np.mean(pl_acc_parts) if pl_acc_parts else 0.0

        n_pl = (len(sel_A) if len(sel_A) > 0 else 0) + (len(sel_B) if len(sel_B) > 0 else 0)

        results["test_acc"].append(test_acc)
        results["pl_acc"].append(pl_acc)
        results["n_pl"].append(n_pl)
        results["train_acc"].append(0.5 * (accuracy(X_train_A, y_train_A, W_A, b_A) +
                                            accuracy(X_train_B, y_train_B, W_B, b_B)))

    return results


# ==============================================================================
# Main Experiment
# ==============================================================================
def run_experiment():
    """Run the full pseudo-labeling validation experiment."""
    print("=" * 80)
    print("PSEUDO-LABELING WITH OVER-RELAXATION: REAL ML VALIDATION")
    print("=" * 80)
    print()

    t_start = time.time()

    # Load data
    X_all, y_all = load_digits_data()

    # Standardize features (zero mean, unit variance)
    X_mean = X_all.mean(axis=0)
    X_std = X_all.std(axis=0) + 1e-8
    X_all = (X_all - X_mean) / X_std

    print(f"Data shape: {X_all.shape}, Classes: {np.unique(y_all)}")
    print(f"Labeled: {N_LABELED}, Unlabeled: {N_UNLABELED}, Test: {N_TEST}")
    print(f"Seeds: {N_SEEDS}, Rounds: {N_ROUNDS}")
    print(f"Alpha values: {ALPHA_VALUES}")
    print(f"Omega values: {OMEGA_VALUES}")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print()

    # Storage for results
    # baseline_accs[seed] = accuracy
    baseline_accs = np.zeros(N_SEEDS)

    # standard_accs[alpha_idx, seed] = final test accuracy
    standard_accs = np.zeros((len(ALPHA_VALUES), N_SEEDS))
    standard_pl_accs = np.zeros((len(ALPHA_VALUES), N_SEEDS, N_ROUNDS))

    # overrelax_accs[alpha_idx, omega_idx, seed] = final test accuracy
    overrelax_accs = np.zeros((len(ALPHA_VALUES), len(OMEGA_VALUES), N_SEEDS))

    # dual_accs[alpha_idx, seed] = final test accuracy
    dual_accs = np.zeros((len(ALPHA_VALUES), N_SEEDS))
    dual_pl_accs = np.zeros((len(ALPHA_VALUES), N_SEEDS, N_ROUNDS))

    # Per-round tracking for standard method (alpha=0.5 as representative)
    standard_per_round = np.zeros((len(ALPHA_VALUES), N_SEEDS, N_ROUNDS))
    standard_pl_per_round = np.zeros((len(ALPHA_VALUES), N_SEEDS, N_ROUNDS))

    # Per-round tracking for dual method
    dual_per_round = np.zeros((len(ALPHA_VALUES), N_SEEDS, N_ROUNDS))
    dual_pl_per_round = np.zeros((len(ALPHA_VALUES), N_SEEDS, N_ROUNDS))

    total_configs = N_SEEDS * (1 + len(ALPHA_VALUES) * (1 + len(OMEGA_VALUES)) + len(ALPHA_VALUES))
    config_count = 0

    for seed in range(N_SEEDS):
        rng = np.random.RandomState(seed * 137 + 42)

        # Split data
        X_lab, y_lab, X_unlab, y_unlab_true, X_test, y_test = split_data(X_all, y_all, rng)

        # === Baseline: no pseudo-labeling ===
        W_init = rng.randn(X_lab.shape[1], N_CLASSES) * 0.01
        b_init = np.zeros(N_CLASSES)
        W_base, b_base = train_logistic(X_lab, y_lab, W_init=W_init.copy(),
                                         b_init=b_init.copy(), rng=rng)
        baseline_accs[seed] = accuracy(X_test, y_test, W_base, b_base)
        config_count += 1

        # === Standard pseudo-labeling (omega=1.0) for each alpha ===
        for ai, alpha in enumerate(ALPHA_VALUES):
            rng_std = np.random.RandomState(seed * 137 + 42 + ai * 7)
            res = run_standard_pseudolabeling(
                X_lab, y_lab, X_unlab, y_unlab_true, X_test, y_test,
                alpha=alpha, omega=1.0, rng=rng_std
            )
            if res["test_acc"]:
                standard_accs[ai, seed] = res["test_acc"][-1]
                for r in range(min(N_ROUNDS, len(res["test_acc"]))):
                    standard_per_round[ai, seed, r] = res["test_acc"][r]
                    standard_pl_per_round[ai, seed, r] = res["pl_acc"][r]
            else:
                standard_accs[ai, seed] = baseline_accs[seed]

            config_count += 1

            # === Over-relaxed pseudo-labeling for each omega ===
            for oi, omega in enumerate(OMEGA_VALUES):
                rng_or = np.random.RandomState(seed * 137 + 42 + ai * 7 + oi * 3)
                res_or = run_standard_pseudolabeling(
                    X_lab, y_lab, X_unlab, y_unlab_true, X_test, y_test,
                    alpha=alpha, omega=omega, rng=rng_or
                )
                if res_or["test_acc"]:
                    overrelax_accs[ai, oi, seed] = res_or["test_acc"][-1]
                else:
                    overrelax_accs[ai, oi, seed] = baseline_accs[seed]

                config_count += 1

            # === Dual-model pseudo-labeling ===
            rng_dual = np.random.RandomState(seed * 137 + 42 + ai * 13)
            res_dual = run_dual_model_pseudolabeling(
                X_lab, y_lab, X_unlab, y_unlab_true, X_test, y_test,
                alpha=alpha, rng=rng_dual
            )
            if res_dual["test_acc"]:
                dual_accs[ai, seed] = res_dual["test_acc"][-1]
                for r in range(min(N_ROUNDS, len(res_dual["test_acc"]))):
                    dual_per_round[ai, seed, r] = res_dual["test_acc"][r]
                    dual_pl_per_round[ai, seed, r] = res_dual["pl_acc"][r]
            else:
                dual_accs[ai, seed] = baseline_accs[seed]

            config_count += 1

        elapsed = time.time() - t_start
        pct = config_count / total_configs * 100
        print(f"  Seed {seed+1}/{N_SEEDS} complete ({pct:.0f}%, {elapsed:.1f}s elapsed)")

    total_time = time.time() - t_start
    print(f"\nAll experiments complete in {total_time:.1f}s")
    print()

    # ==================================================================
    # Analysis
    # ==================================================================
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    # Baseline
    base_mean = baseline_accs.mean()
    base_std = baseline_accs.std()
    print(f"BASELINE (no pseudo-labeling, alpha=0):")
    print(f"  Test accuracy: {base_mean:.4f} +/- {base_std:.4f}")
    print()

    # Standard pseudo-labeling
    print("STANDARD PSEUDO-LABELING (omega=1.0):")
    print(f"  {'Alpha':>6s}  {'Test Acc':>10s}  {'vs Base':>10s}  {'p<0.05?':>8s}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*8}")
    for ai, alpha in enumerate(ALPHA_VALUES):
        mean = standard_accs[ai].mean()
        std = standard_accs[ai].std()
        diff = mean - base_mean
        # Simple paired t-test approximation
        diffs = standard_accs[ai] - baseline_accs
        t_stat = diffs.mean() / (diffs.std() / np.sqrt(N_SEEDS) + 1e-12)
        # Two-tailed p-value approximation (normal for N>=10)
        significant = abs(t_stat) > 2.26  # t_{9, 0.025}
        sig_str = "YES" if significant else "no"
        print(f"  {alpha:6.1f}  {mean:10.4f}  {diff:+10.4f}  {sig_str:>8s}")
    print()

    # Over-relaxation results
    print("OVER-RELAXED PSEUDO-LABELING:")
    print(f"  {'Alpha':>6s}  {'Best w':>8s}  {'Best Acc':>10s}  {'vs Std':>10s}  {'vs Base':>10s}  {'Sig?':>5s}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*5}")

    optimal_omegas = np.zeros(len(ALPHA_VALUES))
    optimal_improvements = np.zeros(len(ALPHA_VALUES))

    for ai, alpha in enumerate(ALPHA_VALUES):
        # Find best omega for this alpha
        mean_accs = overrelax_accs[ai].mean(axis=1)  # (n_omega,)
        best_oi = np.argmax(mean_accs)
        best_omega = OMEGA_VALUES[best_oi]
        best_acc = mean_accs[best_oi]

        optimal_omegas[ai] = best_omega
        std_mean = standard_accs[ai].mean()
        vs_std = best_acc - std_mean
        vs_base = best_acc - base_mean
        optimal_improvements[ai] = vs_std

        # Significance test: best omega vs standard (omega=1.0)
        diffs = overrelax_accs[ai, best_oi] - standard_accs[ai]
        t_stat = diffs.mean() / (diffs.std() / np.sqrt(N_SEEDS) + 1e-12)
        significant = abs(t_stat) > 2.26
        sig_str = "YES" if significant else "no"

        print(f"  {alpha:6.1f}  {best_omega:8.2f}  {best_acc:10.4f}  {vs_std:+10.4f}  {vs_base:+10.4f}  {sig_str:>5s}")
    print()

    # Dual-model results
    print("DUAL-MODEL PSEUDO-LABELING (Fix 2):")
    print(f"  {'Alpha':>6s}  {'Test Acc':>10s}  {'vs Std':>10s}  {'vs Base':>10s}  {'Sig?':>5s}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*5}")
    for ai, alpha in enumerate(ALPHA_VALUES):
        mean = dual_accs[ai].mean()
        std_mean = standard_accs[ai].mean()
        vs_std = mean - std_mean
        vs_base = mean - base_mean

        diffs = dual_accs[ai] - standard_accs[ai]
        t_stat = diffs.mean() / (diffs.std() / np.sqrt(N_SEEDS) + 1e-12)
        significant = abs(t_stat) > 2.26
        sig_str = "YES" if significant else "no"

        print(f"  {alpha:6.1f}  {mean:10.4f}  {vs_std:+10.4f}  {vs_base:+10.4f}  {sig_str:>5s}")
    print()

    # Theory comparison: optimal omega vs 1 + alpha^2
    print("THEORY COMPARISON: Optimal omega vs 1 + alpha^2:")
    print(f"  {'Alpha':>6s}  {'Opt w':>8s}  {'Theory':>8s}  {'Match?':>8s}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}")
    for ai, alpha in enumerate(ALPHA_VALUES):
        theory = 1.0 + alpha ** 2
        opt = optimal_omegas[ai]
        match = abs(opt - theory) < 0.15
        match_str = "~YES" if match else "no"
        print(f"  {alpha:6.1f}  {opt:8.2f}  {theory:8.2f}  {match_str:>8s}")
    print()

    # Summary assessment
    print("=" * 80)
    print("SUMMARY ASSESSMENT")
    print("=" * 80)

    # Test 1: Does contamination hurt?
    high_alpha_acc = standard_accs[-1].mean()  # alpha=0.9
    contam_drop = base_mean - high_alpha_acc
    contam_hurts = contam_drop > 0.01
    print(f"\n1. Does contamination hurt (alpha=0.9 vs baseline)?")
    print(f"   Baseline: {base_mean:.4f}, alpha=0.9: {high_alpha_acc:.4f}, drop: {contam_drop:.4f}")
    print(f"   -> {'YES, contamination degrades performance' if contam_hurts else 'NO, contamination does not hurt (unexpected)'}")

    # Test 2: Does over-relaxation help?
    or_helps_count = 0
    for ai in range(len(ALPHA_VALUES)):
        mean_accs = overrelax_accs[ai].mean(axis=1)
        best_oi = np.argmax(mean_accs)
        if OMEGA_VALUES[best_oi] > 1.0 and mean_accs[best_oi] > standard_accs[ai].mean() + 0.005:
            or_helps_count += 1
    print(f"\n2. Does over-relaxation (omega>1) improve accuracy?")
    print(f"   Helps at {or_helps_count}/{len(ALPHA_VALUES)} alpha values")
    print(f"   -> {'YES, over-relaxation helps' if or_helps_count >= 3 else 'MIXED/NO results'}")

    # Test 3: Does optimal omega track 1 + alpha^2?
    theory_omegas = np.array([1.0 + a**2 for a in ALPHA_VALUES])
    correlation = np.corrcoef(optimal_omegas, theory_omegas)[0, 1]
    print(f"\n3. Does optimal omega track 1 + alpha^2?")
    print(f"   Correlation between optimal omega and 1+alpha^2: {correlation:.3f}")
    print(f"   -> {'YES, good match' if correlation > 0.5 else 'WEAK/NO match'}")

    # Test 4: Does dual-model beat single?
    dual_wins = 0
    for ai in range(len(ALPHA_VALUES)):
        if dual_accs[ai].mean() > standard_accs[ai].mean() + 0.005:
            dual_wins += 1
    print(f"\n4. Does dual-model beat single-model?")
    print(f"   Dual wins at {dual_wins}/{len(ALPHA_VALUES)} alpha values")
    print(f"   -> {'YES, dual model helps' if dual_wins >= 3 else 'MIXED/NO results'}")

    # Test 5: Improvement magnitude
    max_improvement = optimal_improvements.max() * 100
    mean_improvement = optimal_improvements[optimal_improvements > 0].mean() * 100 if any(optimal_improvements > 0) else 0
    print(f"\n5. Improvement magnitude from over-relaxation:")
    print(f"   Max improvement: {max_improvement:.2f}%")
    print(f"   Mean improvement (where positive): {mean_improvement:.2f}%")
    target_range = 3.0 <= max_improvement <= 10.0
    print(f"   -> {'IN PREDICTED RANGE (3-10%)' if target_range else f'Outside predicted range'}")

    # Overall verdict
    tests_passed = sum([contam_hurts, or_helps_count >= 3, correlation > 0.5,
                        dual_wins >= 3, target_range])
    print(f"\n{'='*80}")
    if tests_passed >= 4:
        print("VERDICT: STRONG SUCCESS -- Theory validates on real ML task")
    elif tests_passed >= 2:
        print("VERDICT: MODERATE SUCCESS -- Partial validation of theory")
    else:
        print("VERDICT: HONEST FAILURE -- Theory does not transfer to this setting")
    print(f"Tests passed: {tests_passed}/5")
    print(f"{'='*80}")
    print()

    # ==================================================================
    # Plotting
    # ==================================================================
    print("Generating plots...")

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle("Pseudo-Labeling with Over-Relaxation: Self-Referential Theory Validation",
                 fontsize=14, fontweight="bold", y=0.98)

    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(ALPHA_VALUES)))

    # ---- Panel 1: Test accuracy vs alpha (standard, omega=1.0) ----
    ax = axes[0, 0]
    std_means = standard_accs.mean(axis=1)
    std_stds = standard_accs.std(axis=1)
    ax.axhline(y=base_mean, color="gray", linestyle="--", linewidth=1.5,
               label=f"Baseline (no PL): {base_mean:.3f}")
    ax.fill_between(ALPHA_VALUES, base_mean - base_std, base_mean + base_std,
                    alpha=0.1, color="gray")
    ax.errorbar(ALPHA_VALUES, std_means, yerr=std_stds, marker="o", color="steelblue",
                linewidth=2, capsize=4, label="Standard PL (w=1.0)")
    ax.set_xlabel("Alpha (contamination fraction)")
    ax.set_ylabel("Test Accuracy")
    ax.set_title("1. Contamination Effect")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- Panel 2: Test accuracy vs omega for each alpha (MONEY PLOT) ----
    ax = axes[0, 1]
    for ai, alpha in enumerate(ALPHA_VALUES):
        if alpha in [0.1, 0.3, 0.5, 0.7, 0.9]:  # Show subset for readability
            means = overrelax_accs[ai].mean(axis=1)
            ax.plot(OMEGA_VALUES, means, marker="s", color=colors[ai],
                    linewidth=1.5, label=f"a={alpha:.1f}", markersize=4)
    ax.axvline(x=1.0, color="gray", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlabel("Omega (over-relaxation weight)")
    ax.set_ylabel("Test Accuracy")
    ax.set_title("2. Over-Relaxation Effect (MONEY PLOT)")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # ---- Panel 3: Optimal omega vs alpha with theory ----
    ax = axes[0, 2]
    ax.plot(ALPHA_VALUES, optimal_omegas, "bo-", linewidth=2, markersize=8,
            label="Empirical optimal w")
    theory_line = [1.0 + a**2 for a in ALPHA_VALUES]
    ax.plot(ALPHA_VALUES, theory_line, "r--", linewidth=2,
            label="Theory: w = 1 + a^2")
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Optimal Omega")
    ax.set_title(f"3. Theory vs Empirical (corr={correlation:.2f})")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # ---- Panel 4: Standard vs Dual vs Over-Relaxed ----
    ax = axes[1, 0]
    width = 0.25
    x = np.arange(len(ALPHA_VALUES))

    # Best over-relaxed for each alpha
    best_or_means = np.zeros(len(ALPHA_VALUES))
    for ai in range(len(ALPHA_VALUES)):
        mean_accs = overrelax_accs[ai].mean(axis=1)
        best_or_means[ai] = mean_accs.max()

    ax.bar(x - width, std_means, width, label="Standard", color="steelblue", alpha=0.8)
    ax.bar(x, best_or_means, width, label="Over-relaxed (best w)", color="darkorange", alpha=0.8)
    ax.bar(x + width, dual_accs.mean(axis=1), width, label="Dual-model", color="forestgreen", alpha=0.8)
    ax.axhline(y=base_mean, color="gray", linestyle="--", linewidth=1, label="Baseline")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{a:.1f}" for a in ALPHA_VALUES], fontsize=7)
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Test Accuracy")
    ax.set_title("4. All Methods Compared")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis="y")

    # ---- Panel 5: Pseudo-label accuracy vs round ----
    ax = axes[1, 1]
    # Show for alpha=0.3, 0.5, 0.7
    for ai, alpha in enumerate(ALPHA_VALUES):
        if alpha in [0.3, 0.5, 0.7]:
            # Standard
            rounds = np.arange(1, N_ROUNDS + 1)
            pl_std_mean = standard_pl_per_round[ai].mean(axis=0)
            pl_dual_mean = dual_pl_per_round[ai].mean(axis=0)
            ax.plot(rounds, pl_std_mean, marker="o", color=colors[ai],
                    linewidth=1.5, label=f"Std a={alpha:.1f}")
            ax.plot(rounds, pl_dual_mean, marker="^", color=colors[ai],
                    linewidth=1.5, linestyle="--", label=f"Dual a={alpha:.1f}")
    ax.set_xlabel("Round")
    ax.set_ylabel("Pseudo-label Accuracy")
    ax.set_title("5. PL Accuracy Over Rounds")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # ---- Panel 6: Improvement from best fix vs alpha ----
    ax = axes[1, 2]
    # Improvement of best over-relaxed over standard
    or_improvement = (best_or_means - std_means) * 100
    # Improvement of dual over standard
    dual_improvement = (dual_accs.mean(axis=1) - std_means) * 100

    ax.plot(ALPHA_VALUES, or_improvement, "o-", color="darkorange", linewidth=2,
            label="Over-relaxation improvement")
    ax.plot(ALPHA_VALUES, dual_improvement, "^-", color="forestgreen", linewidth=2,
            label="Dual-model improvement")
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=1)
    ax.axhline(y=8.3, color="red", linestyle=":", linewidth=1,
               label="Theory prediction: 8.3%")
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Improvement over Standard (%)")
    ax.set_title("6. Practical Impact")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Save
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_path = os.path.join(script_dir, "pseudolabel_validation_results.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to: {plot_path}")
    plt.close()

    # ==================================================================
    # Detailed omega sweep table
    # ==================================================================
    print()
    print("=" * 80)
    print("DETAILED OMEGA SWEEP (mean test accuracy across seeds)")
    print("=" * 80)
    header = f"  {'Alpha':>6s}" + "".join(f"  w={w:.2f}" for w in OMEGA_VALUES)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for ai, alpha in enumerate(ALPHA_VALUES):
        row = f"  {alpha:6.1f}"
        means = overrelax_accs[ai].mean(axis=1)
        best_oi = np.argmax(means)
        for oi, omega in enumerate(OMEGA_VALUES):
            marker = " *" if oi == best_oi else "  "
            row += f"  {means[oi]:.4f}{marker}"
        print(row)
    print("  (* = best omega for this alpha)")
    print()

    return {
        "baseline": base_mean,
        "standard_accs": std_means,
        "overrelax_accs": overrelax_accs,
        "dual_accs": dual_accs.mean(axis=1),
        "optimal_omegas": optimal_omegas,
        "tests_passed": tests_passed,
    }


if __name__ == "__main__":
    results = run_experiment()
