"""
Staged Binocular Pseudo-Labeling Experiment
=============================================
Tests whether FORCED VIEWPOINT DIVERSITY + STAGED cross-labeling can
decontaminate pseudo-labels, fixing the failure of naive dual-model PL.

Previous experiment (pseudolabel_validation.py) FAILED at dual-model PL
because both models trained on IDENTICAL data learned IDENTICAL representations.
Two eyes in the same socket = no parallax.

The fix: force different viewpoints. Give each model a DIFFERENT view of the
data so they develop genuinely different representations with different error
patterns. Then cross-labeling becomes meaningful -- where Model A is confused,
Model B may be confident (and vice versa).

Four diversity methods tested:
  1. Feature Split -- Eye A sees LEFT half, Eye B sees RIGHT half of image
  2. Data Split -- Eye A trains on samples 0-49, Eye B on samples 50-99
  3. Architecture Split -- Eye A = LogisticRegression, Eye B = MLP
  4. Feature Transform Split -- Eye A = raw pixels, Eye B = PCA features

Three stages (mirroring human binocular vision development):
  Stage 1: Eyes develop independently (monocular)
  Stage 2: Eyes learn to coordinate (cross-labeling with staged weight)
  Stage 3: Mind sees (ensemble evaluation)

Dataset: sklearn digits (8x8 images, 10 classes, 1797 samples)
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

warnings.filterwarnings("ignore")

# ==============================================================================
# Constants
# ==============================================================================
N_LABELED = 100
N_UNLABELED = 1000
N_TEST = 500
N_CLASSES = 10
N_SEEDS = 5           # 5 seeds for speed (< 5 min target)
N_FEATURES = 64       # 8x8 digits
CONFIDENCE_THRESHOLD = 0.9
ROUND_VALUES = [1, 2, 3, 5, 8]
ALPHA_VALUES = [0.2, 0.4, 0.6, 0.8, 1.0]

# Cross-label weight schedule: start at 0.3, increase by 0.15 per round, cap at 1.0
def cross_label_weight(round_idx):
    """Staged weight for cross-labels: 0.3, 0.45, 0.6, 0.75, 0.9, 1.0..."""
    return min(1.0, 0.3 + 0.15 * round_idx)


# ==============================================================================
# Data Loading
# ==============================================================================
def load_digits_data():
    """Load sklearn digits dataset."""
    from sklearn.datasets import load_digits
    digits = load_digits()
    X = digits.data.astype(np.float64)
    y = digits.target.astype(np.int64)
    # Standardize
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
    print(f"Loaded sklearn digits: {X.shape[0]} samples, {X.shape[1]} features, {N_CLASSES} classes")
    return X, y


def split_data(X, y, rng):
    """Split into labeled, unlabeled, test with stratification."""
    n = len(y)
    remaining_idx = list(range(n))
    rng.shuffle(remaining_idx)

    # Stratified labeled selection
    labeled_idx = []
    per_class = max(2, N_LABELED // N_CLASSES)
    for c in range(N_CLASSES):
        class_idx = [i for i in remaining_idx if y[i] == c]
        take = min(per_class, len(class_idx))
        labeled_idx.extend(class_idx[:take])

    used = set(labeled_idx)
    rest = [i for i in remaining_idx if i not in used]
    rng.shuffle(rest)
    need = N_LABELED - len(labeled_idx)
    if need > 0:
        labeled_idx.extend(rest[:need])
        rest = rest[need:]

    n_unlab = min(N_UNLABELED, len(rest) - N_TEST)
    unlabeled_idx = rest[:n_unlab]
    test_idx = rest[n_unlab:n_unlab + N_TEST]

    return (X[labeled_idx], y[labeled_idx],
            X[unlabeled_idx], y[unlabeled_idx],
            X[test_idx], y[test_idx])


# ==============================================================================
# Model Wrappers (sklearn-based for reliability)
# ==============================================================================
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.decomposition import PCA
from sklearn.random_projection import GaussianRandomProjection


def safe_predict_proba(model, X, n_classes=N_CLASSES):
    """Get predicted probabilities aligned to all n_classes classes.

    Handles models that may not have seen all classes during training,
    which causes predict_proba to return fewer columns.
    """
    probs = model.predict_proba(X)
    if probs.shape[1] == n_classes:
        return probs
    # Align to full class set
    full_probs = np.zeros((X.shape[0], n_classes))
    for i, c in enumerate(model.classes_):
        full_probs[:, int(c)] = probs[:, i]
    return full_probs


def make_logreg(seed):
    """Create a LogisticRegression model."""
    return LogisticRegression(
        max_iter=500, C=1.0, solver="lbfgs",
        random_state=seed, n_jobs=1
    )


def make_mlp(seed):
    """Create an MLP with 1 hidden layer."""
    return MLPClassifier(
        hidden_layer_sizes=(100,), max_iter=500, solver="adam",
        random_state=seed, early_stopping=False
    )


def train_model(model, X, y, sample_weight=None):
    """Train model, return trained model."""
    model.fit(X, y, sample_weight=sample_weight) if sample_weight is not None else model.fit(X, y)
    return model


def get_proba(model, X):
    """Get predicted probabilities."""
    return model.predict_proba(X)


def get_predictions(model, X):
    """Get predicted class labels."""
    return model.predict(X)


def get_accuracy(model, X, y):
    """Get classification accuracy."""
    return np.mean(model.predict(X) == y)


# ==============================================================================
# Viewpoint Diversity Methods
# ==============================================================================
def feature_split_views(X):
    """Split features: Eye A = left half (cols 0-3), Eye B = right half (cols 4-7).
    For 8x8 digit images, this is a literal left/right split."""
    # Reshape to 8x8 to split columns
    n = X.shape[0]
    imgs = X.reshape(n, 8, 8)
    X_A = imgs[:, :, :4].reshape(n, -1)  # Left half: 8x4 = 32 features
    X_B = imgs[:, :, 4:].reshape(n, -1)  # Right half: 8x4 = 32 features
    return X_A, X_B


def data_split_views(X_lab, y_lab):
    """Split labeled data: Eye A gets first half, Eye B gets second half."""
    n = len(y_lab)
    mid = n // 2
    return (X_lab[:mid], y_lab[:mid]), (X_lab[mid:], y_lab[mid:])


def feature_transform_view(X, rng, n_components=32):
    """Transform features: Eye B gets PCA-transformed view."""
    pca = PCA(n_components=n_components, random_state=rng.randint(10000))
    X_B = pca.fit_transform(X)
    return X_B, pca


# ==============================================================================
# Error Correlation Measurement
# ==============================================================================
def compute_error_correlation(preds_A, preds_B, y_true):
    """Compute correlation between error patterns of two models.

    Returns: correlation coefficient between binary error vectors.
    Low correlation = good parallax potential.
    """
    errors_A = (preds_A != y_true).astype(float)
    errors_B = (preds_B != y_true).astype(float)

    if errors_A.std() < 1e-10 or errors_B.std() < 1e-10:
        return 1.0  # degenerate case

    return np.corrcoef(errors_A, errors_B)[0, 1]


def compute_complementary_errors(preds_A, preds_B, y_true):
    """Measure how complementary the errors are.

    Returns dict with:
    - both_right: fraction where both correct
    - both_wrong: fraction where both wrong
    - A_right_B_wrong: fraction where A correct, B wrong
    - A_wrong_B_right: fraction where A wrong, B correct
    """
    correct_A = preds_A == y_true
    correct_B = preds_B == y_true
    n = len(y_true)
    return {
        "both_right": np.sum(correct_A & correct_B) / n,
        "both_wrong": np.sum(~correct_A & ~correct_B) / n,
        "A_right_B_wrong": np.sum(correct_A & ~correct_B) / n,
        "A_wrong_B_right": np.sum(~correct_A & correct_B) / n,
    }


# ==============================================================================
# Pseudo-Label Generation
# ==============================================================================
def generate_pseudo_labels(model, X, threshold=CONFIDENCE_THRESHOLD):
    """Generate pseudo-labels with confidence thresholding.

    Returns: labels, confidences, boolean mask of above-threshold samples.
    """
    probs = safe_predict_proba(model, X)
    confidences = probs.max(axis=1)
    labels = np.argmax(probs, axis=1)
    mask = confidences >= threshold
    return labels, confidences, mask


# ==============================================================================
# Staged Binocular Protocol
# ==============================================================================
def run_baseline(X_lab, y_lab, X_test, y_test, seed):
    """Baseline: single model, labeled data only."""
    model = make_logreg(seed)
    model.fit(X_lab, y_lab)
    return get_accuracy(model, X_test, y_test)


def run_standard_pl(X_lab, y_lab, X_unlab, y_unlab_true, X_test, y_test,
                    alpha, n_rounds, seed):
    """Standard pseudo-labeling: single model, self-labeling."""
    model = make_logreg(seed)
    model.fit(X_lab, y_lab)

    accs = []
    pl_accs = []

    for r in range(n_rounds):
        labels, confs, mask = generate_pseudo_labels(model, X_unlab)
        n_conf = mask.sum()
        if n_conf == 0:
            accs.append(get_accuracy(model, X_test, y_test))
            pl_accs.append(0.0)
            continue

        conf_idx = np.where(mask)[0]
        n_use = max(1, int(alpha * len(conf_idx)))
        rng_sel = np.random.RandomState(seed * 100 + r)
        sel = rng_sel.choice(conf_idx, size=n_use, replace=False)

        X_pl = X_unlab[sel]
        y_pl = labels[sel]
        pl_acc = np.mean(y_pl == y_unlab_true[sel])

        X_train = np.vstack([X_lab, X_pl])
        y_train = np.concatenate([y_lab, y_pl])

        model = make_logreg(seed + r + 1)
        model.fit(X_train, y_train)

        accs.append(get_accuracy(model, X_test, y_test))
        pl_accs.append(pl_acc)

    return accs, pl_accs


def run_naive_dual(X_lab, y_lab, X_unlab, y_unlab_true, X_test, y_test,
                   alpha, n_rounds, seed):
    """Naive dual: two identical models, same data, cross-labeling.
    Expected to fail (same as previous experiment)."""
    model_A = make_logreg(seed)
    model_B = make_logreg(seed + 1000)
    model_A.fit(X_lab, y_lab)
    model_B.fit(X_lab, y_lab)

    accs = []
    error_corrs = []

    for r in range(n_rounds):
        # Cross-label
        labels_A, confs_A, mask_A = generate_pseudo_labels(model_A, X_unlab)
        labels_B, confs_B, mask_B = generate_pseudo_labels(model_B, X_unlab)

        w = cross_label_weight(r)

        # Eye A retrains on labeled + Eye B's pseudo-labels
        conf_B_idx = np.where(mask_B)[0]
        n_use_B = max(1, int(alpha * len(conf_B_idx))) if len(conf_B_idx) > 0 else 0

        # Eye B retrains on labeled + Eye A's pseudo-labels
        conf_A_idx = np.where(mask_A)[0]
        n_use_A = max(1, int(alpha * len(conf_A_idx))) if len(conf_A_idx) > 0 else 0

        if n_use_B > 0:
            rng_sel = np.random.RandomState(seed * 100 + r)
            sel_B = rng_sel.choice(conf_B_idx, size=n_use_B, replace=False)
            X_pl_A = X_unlab[sel_B]
            y_pl_A = labels_B[sel_B]
            X_train_A = np.vstack([X_lab, X_pl_A])
            y_train_A = np.concatenate([y_lab, y_pl_A])
            sw_A = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl_A), w)])
        else:
            X_train_A = X_lab
            y_train_A = y_lab
            sw_A = None

        if n_use_A > 0:
            rng_sel = np.random.RandomState(seed * 100 + r + 50)
            sel_A = rng_sel.choice(conf_A_idx, size=n_use_A, replace=False)
            X_pl_B = X_unlab[sel_A]
            y_pl_B = labels_A[sel_A]
            X_train_B = np.vstack([X_lab, X_pl_B])
            y_train_B = np.concatenate([y_lab, y_pl_B])
            sw_B = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl_B), w)])
        else:
            X_train_B = X_lab
            y_train_B = y_lab
            sw_B = None

        model_A = make_logreg(seed + r + 1)
        model_B = make_logreg(seed + r + 1001)
        model_A.fit(X_train_A, y_train_A, sample_weight=sw_A)
        model_B.fit(X_train_B, y_train_B, sample_weight=sw_B)

        # Ensemble
        probs_A = safe_predict_proba(model_A, X_test)
        probs_B = safe_predict_proba(model_B, X_test)
        ensemble_preds = np.argmax(probs_A + probs_B, axis=1)
        acc = np.mean(ensemble_preds == y_test)
        accs.append(acc)

        # Error correlation
        preds_A = model_A.predict(X_test)
        preds_B = model_B.predict(X_test)
        error_corrs.append(compute_error_correlation(preds_A, preds_B, y_test))

    return accs, error_corrs


def run_feature_split_binocular(X_lab, y_lab, X_unlab, y_unlab_true,
                                 X_test, y_test, alpha, n_rounds, seed):
    """Feature-split binocular: Eye A sees left half, Eye B sees right half.
    Staged cross-labeling with increasing weight."""

    # Create feature-split views for all data
    X_lab_A, X_lab_B = feature_split_views(X_lab)
    X_unlab_A, X_unlab_B = feature_split_views(X_unlab)
    X_test_A, X_test_B = feature_split_views(X_test)
    X_test_full = X_test  # For full-feature ensemble

    # Stage 1: Train independently
    model_A = make_logreg(seed)
    model_B = make_logreg(seed + 1000)
    model_A.fit(X_lab_A, y_lab)
    model_B.fit(X_lab_B, y_lab)

    acc_A_indep = get_accuracy(model_A, X_test_A, y_test)
    acc_B_indep = get_accuracy(model_B, X_test_B, y_test)

    # Initial error correlation
    preds_A = model_A.predict(X_test_A)
    preds_B = model_B.predict(X_test_B)
    init_error_corr = compute_error_correlation(preds_A, preds_B, y_test)
    comp = compute_complementary_errors(preds_A, preds_B, y_test)

    # Stage 2: Cross-labeling rounds
    accs = []
    error_corrs = [init_error_corr]
    pl_accs_A = []
    pl_accs_B = []

    for r in range(n_rounds):
        # Eye A pseudo-labels from its view
        labels_A, confs_A, mask_A = generate_pseudo_labels(model_A, X_unlab_A)
        # Eye B pseudo-labels from its view
        labels_B, confs_B, mask_B = generate_pseudo_labels(model_B, X_unlab_B)

        w = cross_label_weight(r)

        # Eye A retrains on: its labeled data + Eye B's pseudo-labels
        conf_B_idx = np.where(mask_B)[0]
        n_use_B = max(1, int(alpha * len(conf_B_idx))) if len(conf_B_idx) > 0 else 0

        # Eye B retrains on: its labeled data + Eye A's pseudo-labels
        conf_A_idx = np.where(mask_A)[0]
        n_use_A = max(1, int(alpha * len(conf_A_idx))) if len(conf_A_idx) > 0 else 0

        if n_use_B > 0:
            rng_sel = np.random.RandomState(seed * 100 + r)
            sel_B = rng_sel.choice(conf_B_idx, size=n_use_B, replace=False)
            # Eye A gets Eye B's labels, but applied to Eye A's features
            X_pl_A = X_unlab_A[sel_B]
            y_pl_A = labels_B[sel_B]
            pl_acc_B_on_sel = np.mean(labels_B[sel_B] == y_unlab_true[sel_B])

            X_train_A = np.vstack([X_lab_A, X_pl_A])
            y_train_A = np.concatenate([y_lab, y_pl_A])
            sw_A = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl_A), w)])
        else:
            X_train_A = X_lab_A
            y_train_A = y_lab
            sw_A = None
            pl_acc_B_on_sel = 0.0

        if n_use_A > 0:
            rng_sel = np.random.RandomState(seed * 100 + r + 50)
            sel_A = rng_sel.choice(conf_A_idx, size=n_use_A, replace=False)
            X_pl_B = X_unlab_B[sel_A]
            y_pl_B = labels_A[sel_A]
            pl_acc_A_on_sel = np.mean(labels_A[sel_A] == y_unlab_true[sel_A])

            X_train_B = np.vstack([X_lab_B, X_pl_B])
            y_train_B = np.concatenate([y_lab, y_pl_B])
            sw_B = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl_B), w)])
        else:
            X_train_B = X_lab_B
            y_train_B = y_lab
            sw_B = None
            pl_acc_A_on_sel = 0.0

        model_A = make_logreg(seed + r + 1)
        model_B = make_logreg(seed + r + 1001)
        model_A.fit(X_train_A, y_train_A, sample_weight=sw_A)
        model_B.fit(X_train_B, y_train_B, sample_weight=sw_B)

        # Stage 3: Ensemble (combine both views)
        probs_A = safe_predict_proba(model_A, X_test_A)
        probs_B = safe_predict_proba(model_B, X_test_B)
        ensemble_preds = np.argmax(probs_A + probs_B, axis=1)
        acc = np.mean(ensemble_preds == y_test)
        accs.append(acc)

        # Error correlation after this round
        preds_A_r = model_A.predict(X_test_A)
        preds_B_r = model_B.predict(X_test_B)
        error_corrs.append(compute_error_correlation(preds_A_r, preds_B_r, y_test))

        pl_accs_A.append(pl_acc_A_on_sel)
        pl_accs_B.append(pl_acc_B_on_sel)

    return {
        "accs": accs,
        "error_corrs": error_corrs,
        "init_error_corr": init_error_corr,
        "acc_A_indep": acc_A_indep,
        "acc_B_indep": acc_B_indep,
        "complementary": comp,
        "pl_accs_A": pl_accs_A,
        "pl_accs_B": pl_accs_B,
    }


def run_data_split_binocular(X_lab, y_lab, X_unlab, y_unlab_true,
                              X_test, y_test, alpha, n_rounds, seed):
    """Data-split binocular: Eye A trains on first half of labeled, Eye B on second."""

    (X_A, y_A), (X_B, y_B) = data_split_views(X_lab, y_lab)

    # Stage 1: Train independently on different subsets
    model_A = make_logreg(seed)
    model_B = make_logreg(seed + 1000)
    model_A.fit(X_A, y_A)
    model_B.fit(X_B, y_B)

    acc_A_indep = get_accuracy(model_A, X_test, y_test)
    acc_B_indep = get_accuracy(model_B, X_test, y_test)

    preds_A = model_A.predict(X_test)
    preds_B = model_B.predict(X_test)
    init_error_corr = compute_error_correlation(preds_A, preds_B, y_test)
    comp = compute_complementary_errors(preds_A, preds_B, y_test)

    # Stage 2: Cross-labeling
    accs = []
    error_corrs = [init_error_corr]
    pl_accs_A = []
    pl_accs_B = []

    for r in range(n_rounds):
        labels_A, confs_A, mask_A = generate_pseudo_labels(model_A, X_unlab)
        labels_B, confs_B, mask_B = generate_pseudo_labels(model_B, X_unlab)

        w = cross_label_weight(r)

        # Eye A: its labeled subset + Eye B's pseudo-labels
        conf_B_idx = np.where(mask_B)[0]
        n_use_B = max(1, int(alpha * len(conf_B_idx))) if len(conf_B_idx) > 0 else 0

        conf_A_idx = np.where(mask_A)[0]
        n_use_A = max(1, int(alpha * len(conf_A_idx))) if len(conf_A_idx) > 0 else 0

        if n_use_B > 0:
            rng_sel = np.random.RandomState(seed * 100 + r)
            sel_B = rng_sel.choice(conf_B_idx, size=n_use_B, replace=False)
            X_pl_for_A = X_unlab[sel_B]
            y_pl_for_A = labels_B[sel_B]
            pl_acc_B = np.mean(labels_B[sel_B] == y_unlab_true[sel_B])
            X_train_A = np.vstack([X_A, X_pl_for_A])
            y_train_A = np.concatenate([y_A, y_pl_for_A])
            sw_A = np.concatenate([np.ones(len(y_A)), np.full(len(y_pl_for_A), w)])
        else:
            X_train_A, y_train_A, sw_A = X_A, y_A, None
            pl_acc_B = 0.0

        if n_use_A > 0:
            rng_sel = np.random.RandomState(seed * 100 + r + 50)
            sel_A = rng_sel.choice(conf_A_idx, size=n_use_A, replace=False)
            X_pl_for_B = X_unlab[sel_A]
            y_pl_for_B = labels_A[sel_A]
            pl_acc_A = np.mean(labels_A[sel_A] == y_unlab_true[sel_A])
            X_train_B = np.vstack([X_B, X_pl_for_B])
            y_train_B = np.concatenate([y_B, y_pl_for_B])
            sw_B = np.concatenate([np.ones(len(y_B)), np.full(len(y_pl_for_B), w)])
        else:
            X_train_B, y_train_B, sw_B = X_B, y_B, None
            pl_acc_A = 0.0

        model_A = make_logreg(seed + r + 1)
        model_B = make_logreg(seed + r + 1001)
        model_A.fit(X_train_A, y_train_A, sample_weight=sw_A)
        model_B.fit(X_train_B, y_train_B, sample_weight=sw_B)

        probs_A = safe_predict_proba(model_A, X_test)
        probs_B = safe_predict_proba(model_B, X_test)
        ensemble_preds = np.argmax(probs_A + probs_B, axis=1)
        acc = np.mean(ensemble_preds == y_test)
        accs.append(acc)

        preds_A_r = model_A.predict(X_test)
        preds_B_r = model_B.predict(X_test)
        error_corrs.append(compute_error_correlation(preds_A_r, preds_B_r, y_test))

        pl_accs_A.append(pl_acc_A)
        pl_accs_B.append(pl_acc_B)

    return {
        "accs": accs,
        "error_corrs": error_corrs,
        "init_error_corr": init_error_corr,
        "acc_A_indep": acc_A_indep,
        "acc_B_indep": acc_B_indep,
        "complementary": comp,
        "pl_accs_A": pl_accs_A,
        "pl_accs_B": pl_accs_B,
    }


def run_architecture_split_binocular(X_lab, y_lab, X_unlab, y_unlab_true,
                                      X_test, y_test, alpha, n_rounds, seed):
    """Architecture-split binocular: Eye A = LogReg, Eye B = MLP.
    Same data, different inductive biases."""

    # Stage 1: Train independently
    model_A = make_logreg(seed)
    model_B = make_mlp(seed + 1000)
    model_A.fit(X_lab, y_lab)
    model_B.fit(X_lab, y_lab)

    acc_A_indep = get_accuracy(model_A, X_test, y_test)
    acc_B_indep = get_accuracy(model_B, X_test, y_test)

    preds_A = model_A.predict(X_test)
    preds_B = model_B.predict(X_test)
    init_error_corr = compute_error_correlation(preds_A, preds_B, y_test)
    comp = compute_complementary_errors(preds_A, preds_B, y_test)

    # Stage 2: Cross-labeling
    accs = []
    error_corrs = [init_error_corr]
    pl_accs_A = []
    pl_accs_B = []

    for r in range(n_rounds):
        labels_A, confs_A, mask_A = generate_pseudo_labels(model_A, X_unlab)
        labels_B, confs_B, mask_B = generate_pseudo_labels(model_B, X_unlab)

        w = cross_label_weight(r)

        conf_B_idx = np.where(mask_B)[0]
        n_use_B = max(1, int(alpha * len(conf_B_idx))) if len(conf_B_idx) > 0 else 0
        conf_A_idx = np.where(mask_A)[0]
        n_use_A = max(1, int(alpha * len(conf_A_idx))) if len(conf_A_idx) > 0 else 0

        if n_use_B > 0:
            rng_sel = np.random.RandomState(seed * 100 + r)
            sel_B = rng_sel.choice(conf_B_idx, size=n_use_B, replace=False)
            X_pl_for_A = X_unlab[sel_B]
            y_pl_for_A = labels_B[sel_B]
            pl_acc_B = np.mean(labels_B[sel_B] == y_unlab_true[sel_B])
            X_train_A = np.vstack([X_lab, X_pl_for_A])
            y_train_A = np.concatenate([y_lab, y_pl_for_A])
            sw_A = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl_for_A), w)])
        else:
            X_train_A, y_train_A, sw_A = X_lab, y_lab, None
            pl_acc_B = 0.0

        if n_use_A > 0:
            rng_sel = np.random.RandomState(seed * 100 + r + 50)
            sel_A = rng_sel.choice(conf_A_idx, size=n_use_A, replace=False)
            X_pl_for_B = X_unlab[sel_A]
            y_pl_for_B = labels_A[sel_A]
            pl_acc_A = np.mean(labels_A[sel_A] == y_unlab_true[sel_A])
            X_train_B = np.vstack([X_lab, X_pl_for_B])
            y_train_B = np.concatenate([y_lab, y_pl_for_B])
            sw_B = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl_for_B), w)])
        else:
            X_train_B, y_train_B, sw_B = X_lab, y_lab, None
            pl_acc_A = 0.0

        model_A = make_logreg(seed + r + 1)
        model_B = make_mlp(seed + r + 1001)
        model_A.fit(X_train_A, y_train_A, sample_weight=sw_A)
        model_B.fit(X_train_B, y_train_B, sample_weight=sw_B)

        probs_A = safe_predict_proba(model_A, X_test)
        probs_B = safe_predict_proba(model_B, X_test)
        ensemble_preds = np.argmax(probs_A + probs_B, axis=1)
        acc = np.mean(ensemble_preds == y_test)
        accs.append(acc)

        preds_A_r = model_A.predict(X_test)
        preds_B_r = model_B.predict(X_test)
        error_corrs.append(compute_error_correlation(preds_A_r, preds_B_r, y_test))

        pl_accs_A.append(pl_acc_A)
        pl_accs_B.append(pl_acc_B)

    return {
        "accs": accs,
        "error_corrs": error_corrs,
        "init_error_corr": init_error_corr,
        "acc_A_indep": acc_A_indep,
        "acc_B_indep": acc_B_indep,
        "complementary": comp,
        "pl_accs_A": pl_accs_A,
        "pl_accs_B": pl_accs_B,
    }


def run_feature_transform_binocular(X_lab, y_lab, X_unlab, y_unlab_true,
                                     X_test, y_test, alpha, n_rounds, seed):
    """Feature-transform binocular: Eye A = raw pixels, Eye B = PCA features."""

    rng = np.random.RandomState(seed)

    # Fit PCA on labeled + unlabeled (unsupervised, no label leakage)
    X_fit = np.vstack([X_lab, X_unlab])
    pca = PCA(n_components=32, random_state=seed)
    pca.fit(X_fit)

    X_lab_B = pca.transform(X_lab)
    X_unlab_B = pca.transform(X_unlab)
    X_test_B = pca.transform(X_test)

    # Stage 1: Train independently
    model_A = make_logreg(seed)
    model_B = make_logreg(seed + 1000)
    model_A.fit(X_lab, y_lab)        # Raw features
    model_B.fit(X_lab_B, y_lab)      # PCA features

    acc_A_indep = get_accuracy(model_A, X_test, y_test)
    acc_B_indep = get_accuracy(model_B, X_test_B, y_test)

    preds_A = model_A.predict(X_test)
    preds_B = model_B.predict(X_test_B)
    init_error_corr = compute_error_correlation(preds_A, preds_B, y_test)
    comp = compute_complementary_errors(preds_A, preds_B, y_test)

    # Stage 2: Cross-labeling
    accs = []
    error_corrs = [init_error_corr]
    pl_accs_A = []
    pl_accs_B = []

    for r in range(n_rounds):
        # Eye A pseudo-labels from raw features
        labels_A, confs_A, mask_A = generate_pseudo_labels(model_A, X_unlab)
        # Eye B pseudo-labels from PCA features
        labels_B, confs_B, mask_B = generate_pseudo_labels(model_B, X_unlab_B)

        w = cross_label_weight(r)

        conf_B_idx = np.where(mask_B)[0]
        n_use_B = max(1, int(alpha * len(conf_B_idx))) if len(conf_B_idx) > 0 else 0
        conf_A_idx = np.where(mask_A)[0]
        n_use_A = max(1, int(alpha * len(conf_A_idx))) if len(conf_A_idx) > 0 else 0

        # Eye A retrains with Eye B's labels (applied to raw features)
        if n_use_B > 0:
            rng_sel = np.random.RandomState(seed * 100 + r)
            sel_B = rng_sel.choice(conf_B_idx, size=n_use_B, replace=False)
            X_pl_for_A = X_unlab[sel_B]  # Raw features for model A
            y_pl_for_A = labels_B[sel_B]
            pl_acc_B = np.mean(labels_B[sel_B] == y_unlab_true[sel_B])
            X_train_A = np.vstack([X_lab, X_pl_for_A])
            y_train_A = np.concatenate([y_lab, y_pl_for_A])
            sw_A = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl_for_A), w)])
        else:
            X_train_A, y_train_A, sw_A = X_lab, y_lab, None
            pl_acc_B = 0.0

        # Eye B retrains with Eye A's labels (applied to PCA features)
        if n_use_A > 0:
            rng_sel = np.random.RandomState(seed * 100 + r + 50)
            sel_A = rng_sel.choice(conf_A_idx, size=n_use_A, replace=False)
            X_pl_for_B = X_unlab_B[sel_A]  # PCA features for model B
            y_pl_for_B = labels_A[sel_A]
            pl_acc_A = np.mean(labels_A[sel_A] == y_unlab_true[sel_A])
            X_train_B = np.vstack([X_lab_B, X_pl_for_B])
            y_train_B = np.concatenate([y_lab, y_pl_for_B])
            sw_B = np.concatenate([np.ones(len(y_lab)), np.full(len(y_pl_for_B), w)])
        else:
            X_train_B, y_train_B, sw_B = X_lab_B, y_lab, None
            pl_acc_A = 0.0

        model_A = make_logreg(seed + r + 1)
        model_B = make_logreg(seed + r + 1001)
        model_A.fit(X_train_A, y_train_A, sample_weight=sw_A)
        model_B.fit(X_train_B, y_train_B, sample_weight=sw_B)

        probs_A = safe_predict_proba(model_A, X_test)
        probs_B = safe_predict_proba(model_B, X_test_B)
        ensemble_preds = np.argmax(probs_A + probs_B, axis=1)
        acc = np.mean(ensemble_preds == y_test)
        accs.append(acc)

        preds_A_r = model_A.predict(X_test)
        preds_B_r = model_B.predict(X_test_B)
        error_corrs.append(compute_error_correlation(preds_A_r, preds_B_r, y_test))

        pl_accs_A.append(pl_acc_A)
        pl_accs_B.append(pl_acc_B)

    return {
        "accs": accs,
        "error_corrs": error_corrs,
        "init_error_corr": init_error_corr,
        "acc_A_indep": acc_A_indep,
        "acc_B_indep": acc_B_indep,
        "complementary": comp,
        "pl_accs_A": pl_accs_A,
        "pl_accs_B": pl_accs_B,
    }


# ==============================================================================
# Main Experiment
# ==============================================================================
def run_experiment():
    print("=" * 80)
    print("STAGED BINOCULAR PSEUDO-LABELING EXPERIMENT")
    print("=" * 80)
    print()
    print("Hypothesis: Forced viewpoint diversity + staged cross-labeling")
    print("enables decontamination that naive dual-model PL cannot achieve.")
    print()

    t_start = time.time()

    X_all, y_all = load_digits_data()

    print(f"Split: {N_LABELED} labeled, {N_UNLABELED} unlabeled, {N_TEST} test")
    print(f"Seeds: {N_SEEDS}, Rounds: {ROUND_VALUES}, Alphas: {ALPHA_VALUES}")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"Cross-label weight schedule: {[cross_label_weight(r) for r in range(max(ROUND_VALUES))]}")
    print()

    # Storage
    # For each method x alpha x seed, store final accuracy (at max rounds)
    methods = ["Baseline", "Standard PL", "Naive Dual",
               "Feature-Split", "Data-Split", "Arch-Split", "Transform-Split"]
    n_methods = len(methods)
    n_alphas = len(ALPHA_VALUES)
    max_rounds = max(ROUND_VALUES)

    # final_accs[method_idx, alpha_idx, seed] = final test accuracy
    final_accs = np.zeros((n_methods, n_alphas, N_SEEDS))

    # per_round_accs[method_idx, alpha_idx, seed, round] = test accuracy at that round
    per_round_accs = np.full((n_methods, n_alphas, N_SEEDS, max_rounds), np.nan)

    # error_corrs_init[method_idx, seed] = initial error correlation (before cross-labeling)
    # (only for methods 2-6 which have two models)
    error_corrs_init = np.full((n_methods, N_SEEDS), np.nan)

    # pl_accs[method_idx, alpha_idx, seed, round] = pseudo-label accuracy
    pl_accs_store = np.full((n_methods, n_alphas, N_SEEDS, max_rounds), np.nan)

    # Complementary error data
    complementary_data = {}

    for seed in range(N_SEEDS):
        rng = np.random.RandomState(seed * 137 + 42)
        X_lab, y_lab, X_unlab, y_unlab, X_test, y_test = split_data(X_all, y_all, rng)

        print(f"--- Seed {seed+1}/{N_SEEDS} ---")

        for ai, alpha in enumerate(ALPHA_VALUES):
            # ---- Baseline ----
            base_acc = run_baseline(X_lab, y_lab, X_test, y_test, seed)
            final_accs[0, ai, seed] = base_acc
            for r in range(max_rounds):
                per_round_accs[0, ai, seed, r] = base_acc

            # ---- Standard PL ----
            std_accs, std_pl_accs = run_standard_pl(
                X_lab, y_lab, X_unlab, y_unlab, X_test, y_test,
                alpha, max_rounds, seed
            )
            if std_accs:
                final_accs[1, ai, seed] = std_accs[-1]
                for r in range(len(std_accs)):
                    per_round_accs[1, ai, seed, r] = std_accs[r]
                    pl_accs_store[1, ai, seed, r] = std_pl_accs[r]

            # ---- Naive Dual ----
            naive_accs, naive_ecorrs = run_naive_dual(
                X_lab, y_lab, X_unlab, y_unlab, X_test, y_test,
                alpha, max_rounds, seed
            )
            if naive_accs:
                final_accs[2, ai, seed] = naive_accs[-1]
                for r in range(len(naive_accs)):
                    per_round_accs[2, ai, seed, r] = naive_accs[r]
                if naive_ecorrs:
                    error_corrs_init[2, seed] = naive_ecorrs[0]

            # ---- Feature-Split Binocular ----
            fs_res = run_feature_split_binocular(
                X_lab, y_lab, X_unlab, y_unlab, X_test, y_test,
                alpha, max_rounds, seed
            )
            final_accs[3, ai, seed] = fs_res["accs"][-1] if fs_res["accs"] else base_acc
            for r in range(len(fs_res["accs"])):
                per_round_accs[3, ai, seed, r] = fs_res["accs"][r]
                pl_accs_store[3, ai, seed, r] = np.mean([fs_res["pl_accs_A"][r], fs_res["pl_accs_B"][r]])
            error_corrs_init[3, seed] = fs_res["init_error_corr"]
            if ai == 0:
                complementary_data[("Feature-Split", seed)] = fs_res["complementary"]

            # ---- Data-Split Binocular ----
            ds_res = run_data_split_binocular(
                X_lab, y_lab, X_unlab, y_unlab, X_test, y_test,
                alpha, max_rounds, seed
            )
            final_accs[4, ai, seed] = ds_res["accs"][-1] if ds_res["accs"] else base_acc
            for r in range(len(ds_res["accs"])):
                per_round_accs[4, ai, seed, r] = ds_res["accs"][r]
                pl_accs_store[4, ai, seed, r] = np.mean([ds_res["pl_accs_A"][r], ds_res["pl_accs_B"][r]])
            error_corrs_init[4, seed] = ds_res["init_error_corr"]
            if ai == 0:
                complementary_data[("Data-Split", seed)] = ds_res["complementary"]

            # ---- Architecture-Split Binocular ----
            as_res = run_architecture_split_binocular(
                X_lab, y_lab, X_unlab, y_unlab, X_test, y_test,
                alpha, max_rounds, seed
            )
            final_accs[5, ai, seed] = as_res["accs"][-1] if as_res["accs"] else base_acc
            for r in range(len(as_res["accs"])):
                per_round_accs[5, ai, seed, r] = as_res["accs"][r]
                pl_accs_store[5, ai, seed, r] = np.mean([as_res["pl_accs_A"][r], as_res["pl_accs_B"][r]])
            error_corrs_init[5, seed] = as_res["init_error_corr"]
            if ai == 0:
                complementary_data[("Arch-Split", seed)] = as_res["complementary"]

            # ---- Feature-Transform Binocular ----
            ft_res = run_feature_transform_binocular(
                X_lab, y_lab, X_unlab, y_unlab, X_test, y_test,
                alpha, max_rounds, seed
            )
            final_accs[6, ai, seed] = ft_res["accs"][-1] if ft_res["accs"] else base_acc
            for r in range(len(ft_res["accs"])):
                per_round_accs[6, ai, seed, r] = ft_res["accs"][r]
                pl_accs_store[6, ai, seed, r] = np.mean([ft_res["pl_accs_A"][r], ft_res["pl_accs_B"][r]])
            error_corrs_init[6, seed] = ft_res["init_error_corr"]
            if ai == 0:
                complementary_data[("Transform-Split", seed)] = ft_res["complementary"]

        elapsed = time.time() - t_start
        print(f"  Completed in {elapsed:.1f}s total")

    total_time = time.time() - t_start
    print(f"\nAll experiments complete in {total_time:.1f}s")
    print()

    # ==================================================================
    # Analysis
    # ==================================================================
    print("=" * 80)
    print("STAGE 1: ERROR CORRELATION (THE KEY DIAGNOSTIC)")
    print("=" * 80)
    print()
    print("Low error correlation = good parallax potential = cross-labeling should help")
    print()

    div_methods = ["Naive Dual", "Feature-Split", "Data-Split", "Arch-Split", "Transform-Split"]
    div_indices = [2, 3, 4, 5, 6]

    print(f"  {'Method':<20s}  {'Error Corr':>12s}  {'Parallax?':>10s}")
    print(f"  {'-'*20}  {'-'*12}  {'-'*10}")

    mean_error_corrs = {}
    for name, idx in zip(div_methods, div_indices):
        vals = error_corrs_init[idx]
        valid = vals[~np.isnan(vals)]
        if len(valid) > 0:
            mean_ec = valid.mean()
            mean_error_corrs[name] = mean_ec
            parallax = "YES" if mean_ec < 0.5 else ("SOME" if mean_ec < 0.7 else "NO")
            print(f"  {name:<20s}  {mean_ec:12.3f}  {parallax:>10s}")
    print()

    # Complementary error analysis
    print("COMPLEMENTARY ERROR ANALYSIS (averaged across seeds):")
    print(f"  {'Method':<20s}  {'Both Right':>12s}  {'Both Wrong':>12s}  {'A ok B err':>12s}  {'A err B ok':>12s}")
    print(f"  {'-'*20}  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*12}")

    for name in ["Feature-Split", "Data-Split", "Arch-Split", "Transform-Split"]:
        br, bw, ar, aw = [], [], [], []
        for seed in range(N_SEEDS):
            key = (name, seed)
            if key in complementary_data:
                d = complementary_data[key]
                br.append(d["both_right"])
                bw.append(d["both_wrong"])
                ar.append(d["A_right_B_wrong"])
                aw.append(d["A_wrong_B_right"])
        if br:
            print(f"  {name:<20s}  {np.mean(br):12.3f}  {np.mean(bw):12.3f}  {np.mean(ar):12.3f}  {np.mean(aw):12.3f}")
    print()

    # ==================================================================
    print("=" * 80)
    print("STAGE 2: TEST ACCURACY BY METHOD AND ALPHA")
    print("=" * 80)
    print()

    # Print table
    header = f"  {'Method':<20s}" + "".join(f"  a={a:.1f}" for a in ALPHA_VALUES) + "  Mean"
    print(header)
    print("  " + "-" * (len(header) - 2))

    method_means = np.zeros((n_methods, n_alphas))
    method_stds = np.zeros((n_methods, n_alphas))

    for mi, name in enumerate(methods):
        row = f"  {name:<20s}"
        for ai in range(n_alphas):
            mean = final_accs[mi, ai].mean()
            method_means[mi, ai] = mean
            method_stds[mi, ai] = final_accs[mi, ai].std()
            row += f"  {mean:.3f}"
        row += f"  {method_means[mi].mean():.3f}"
        print(row)
    print()

    # ==================================================================
    print("=" * 80)
    print("STAGE 3: IMPROVEMENT OVER STANDARD PL")
    print("=" * 80)
    print()

    print(f"  {'Method':<20s}" + "".join(f"  a={a:.1f}" for a in ALPHA_VALUES) + "  Mean")
    print("  " + "-" * 80)

    improvements = np.zeros((n_methods, n_alphas))
    for mi, name in enumerate(methods):
        if mi <= 1:
            continue  # Skip baseline and standard PL
        row = f"  {name:<20s}"
        for ai in range(n_alphas):
            imp = (method_means[mi, ai] - method_means[1, ai]) * 100
            improvements[mi, ai] = imp
            row += f"  {imp:+.1f}%"
        row += f"  {improvements[mi].mean():+.1f}%"
        print(row)
    print()

    # ==================================================================
    # Statistical significance
    print("=" * 80)
    print("STATISTICAL SIGNIFICANCE (paired t-test vs Standard PL)")
    print("=" * 80)
    print()

    sig_results = {}
    for mi, name in enumerate(methods):
        if mi <= 1:
            continue
        for ai, alpha in enumerate(ALPHA_VALUES):
            diffs = final_accs[mi, ai] - final_accs[1, ai]
            t_stat = diffs.mean() / (diffs.std() / np.sqrt(N_SEEDS) + 1e-12)
            significant = abs(t_stat) > 2.776  # t_{4, 0.025} for 5 seeds
            sig_results[(name, alpha)] = {
                "t_stat": t_stat,
                "significant": significant,
                "mean_diff": diffs.mean(),
            }

    print(f"  {'Method':<20s}" + "".join(f"  a={a:.1f}" for a in ALPHA_VALUES))
    print("  " + "-" * 70)
    for mi, name in enumerate(methods):
        if mi <= 1:
            continue
        row = f"  {name:<20s}"
        for ai, alpha in enumerate(ALPHA_VALUES):
            sr = sig_results[(name, alpha)]
            marker = " **" if sr["significant"] else "   "
            row += f"  {sr['mean_diff']*100:+.1f}{marker}"
        print(row)
    print("  (** = p < 0.05)")
    print()

    # ==================================================================
    # Per-round analysis for best method
    print("=" * 80)
    print("PER-ROUND ACCURACY (alpha=0.6, showing learning over time)")
    print("=" * 80)
    print()

    ai_show = 2  # alpha=0.6
    print(f"  {'Method':<20s}" + "".join(f"  R{r+1:d}" for r in range(max_rounds)))
    print("  " + "-" * 60)
    for mi, name in enumerate(methods):
        row = f"  {name:<20s}"
        for r in range(max_rounds):
            vals = per_round_accs[mi, ai_show, :, r]
            valid = vals[~np.isnan(vals)]
            if len(valid) > 0:
                row += f"  {valid.mean():.3f}"
            else:
                row += f"  {'N/A':>5s}"
        print(row)
    print()

    # ==================================================================
    # Summary verdict
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    print()

    # Find best binocular method
    binocular_indices = [3, 4, 5, 6]
    binocular_names = ["Feature-Split", "Data-Split", "Arch-Split", "Transform-Split"]

    best_bino_improvement = -999
    best_bino_name = ""
    best_bino_alpha = 0

    any_sig = False
    n_sig = 0

    for mi, name in zip(binocular_indices, binocular_names):
        for ai, alpha in enumerate(ALPHA_VALUES):
            imp = improvements[mi, ai]
            if imp > best_bino_improvement:
                best_bino_improvement = imp
                best_bino_name = name
                best_bino_alpha = alpha
            sr = sig_results.get((name, alpha))
            if sr and sr["significant"] and sr["mean_diff"] > 0:
                any_sig = True
                n_sig += 1

    # Also check naive dual
    naive_mean_imp = improvements[2].mean()

    print(f"Best binocular method: {best_bino_name} at alpha={best_bino_alpha:.1f}")
    print(f"  Improvement over Standard PL: {best_bino_improvement:+.2f}%")
    print(f"  Naive dual mean improvement: {naive_mean_imp:+.2f}%")
    print(f"  Significant improvements: {n_sig}/{len(binocular_indices)*n_alphas}")
    print()

    # Error correlation diagnostic
    lowest_ec_name = min(mean_error_corrs, key=mean_error_corrs.get)
    lowest_ec = mean_error_corrs[lowest_ec_name]

    print(f"Lowest error correlation: {lowest_ec_name} ({lowest_ec:.3f})")
    print()

    if best_bino_improvement > 3.0:
        print(">>> STRONG SUCCESS: Binocular beats Standard PL by >3%")
    elif any_sig:
        print(f">>> MODERATE SUCCESS: {n_sig} significant improvements found")
    elif lowest_ec > 0.7:
        print(">>> INFORMATIVE FAILURE: Error correlation too high across all methods")
        print("    The digits dataset may not have enough structure for viewpoint parallax.")
    else:
        print(">>> FAILURE: Low error correlation achieved but no accuracy improvement.")
        print("    The parallax exists but cross-labeling doesn't exploit it.")

    print()

    # ==================================================================
    # Plotting
    # ==================================================================
    print("Generating plots...")

    fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    fig.suptitle("Staged Binocular Pseudo-Labeling: Viewpoint Diversity for Decontamination",
                 fontsize=14, fontweight="bold", y=0.98)

    colors_methods = {
        "Baseline": "#808080",
        "Standard PL": "#4169E1",
        "Naive Dual": "#DC143C",
        "Feature-Split": "#228B22",
        "Data-Split": "#FF8C00",
        "Arch-Split": "#9932CC",
        "Transform-Split": "#20B2AA",
    }

    # ---- Panel 1: Error Correlation Bar Chart ----
    ax = axes[0, 0]
    bar_names = []
    bar_vals = []
    bar_colors = []
    for name in div_methods:
        if name in mean_error_corrs:
            bar_names.append(name)
            bar_vals.append(mean_error_corrs[name])
            bar_colors.append(colors_methods.get(name, "#333333"))

    bars = ax.bar(range(len(bar_names)), bar_vals, color=bar_colors, alpha=0.8, edgecolor="black")
    ax.set_xticks(range(len(bar_names)))
    ax.set_xticklabels(bar_names, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Error Correlation")
    ax.set_title("1. Error Correlation Between Eyes\n(lower = more parallax potential)")
    ax.axhline(y=0.5, color="gray", linestyle="--", linewidth=1, alpha=0.5, label="Threshold")
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3, axis="y")
    for bar, val in zip(bars, bar_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.legend(fontsize=8)

    # ---- Panel 2: Test Accuracy vs Alpha (THE MONEY PLOT) ----
    ax = axes[0, 1]
    for mi, name in enumerate(methods):
        means = method_means[mi]
        stds = method_stds[mi]
        color = colors_methods.get(name, "#333333")
        ls = "--" if name in ["Baseline", "Naive Dual"] else "-"
        marker = "o" if name in ["Feature-Split", "Data-Split", "Arch-Split", "Transform-Split"] else "s"
        ax.errorbar(ALPHA_VALUES, means, yerr=stds, marker=marker, color=color,
                    linewidth=2 if "Split" in name else 1.5, linestyle=ls,
                    capsize=3, label=name, markersize=5)
    ax.set_xlabel("Alpha (contamination fraction)")
    ax.set_ylabel("Test Accuracy")
    ax.set_title("2. Test Accuracy vs Alpha (THE MONEY PLOT)")
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.3)

    # ---- Panel 3: Test Accuracy vs Round (best binocular at alpha=0.6) ----
    ax = axes[1, 0]
    ai_show = 2  # alpha = 0.6
    rounds_x = np.arange(1, max_rounds + 1)
    for mi, name in enumerate(methods):
        vals = per_round_accs[mi, ai_show]  # (N_SEEDS, max_rounds)
        valid_mask = ~np.isnan(vals)
        means_r = []
        stds_r = []
        for r in range(max_rounds):
            v = vals[:, r]
            v = v[~np.isnan(v)]
            if len(v) > 0:
                means_r.append(v.mean())
                stds_r.append(v.std())
            else:
                means_r.append(np.nan)
                stds_r.append(0)
        means_r = np.array(means_r)
        stds_r = np.array(stds_r)
        color = colors_methods.get(name, "#333333")
        ls = "--" if name in ["Baseline", "Naive Dual"] else "-"
        valid_r = ~np.isnan(means_r)
        if valid_r.any():
            ax.plot(rounds_x[valid_r], means_r[valid_r], marker="o", color=color,
                    linewidth=1.5, linestyle=ls, label=name, markersize=4)
    ax.set_xlabel("Round")
    ax.set_ylabel("Test Accuracy")
    ax.set_title(f"3. Accuracy vs Round (alpha={ALPHA_VALUES[ai_show]:.1f})")
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.3)

    # ---- Panel 4: Pseudo-label accuracy (Eye A vs Eye B vs combined) ----
    ax = axes[1, 1]
    ai_show = 2  # alpha=0.6
    for mi, name in zip([3, 5, 6], ["Feature-Split", "Arch-Split", "Transform-Split"]):
        pl_vals = pl_accs_store[mi, ai_show]  # (N_SEEDS, max_rounds)
        means_pl = []
        for r in range(max_rounds):
            v = pl_vals[:, r]
            v = v[~np.isnan(v)]
            if len(v) > 0:
                means_pl.append(v.mean())
            else:
                means_pl.append(np.nan)
        means_pl = np.array(means_pl)
        valid_r = ~np.isnan(means_pl)
        color = colors_methods.get(name, "#333333")
        if valid_r.any():
            ax.plot(rounds_x[valid_r], means_pl[valid_r], marker="o", color=color,
                    linewidth=1.5, label=name, markersize=4)

    # Standard PL pseudo-label accuracy for comparison
    std_pl = pl_accs_store[1, ai_show]
    means_std_pl = []
    for r in range(max_rounds):
        v = std_pl[:, r]
        v = v[~np.isnan(v)]
        if len(v) > 0:
            means_std_pl.append(v.mean())
        else:
            means_std_pl.append(np.nan)
    means_std_pl = np.array(means_std_pl)
    valid_r = ~np.isnan(means_std_pl)
    if valid_r.any():
        ax.plot(rounds_x[valid_r], means_std_pl[valid_r], marker="s", color="#4169E1",
                linewidth=1.5, linestyle="--", label="Standard PL", markersize=4)

    ax.set_xlabel("Round")
    ax.set_ylabel("Pseudo-label Accuracy")
    ax.set_title(f"4. Pseudo-label Quality (alpha={ALPHA_VALUES[ai_show]:.1f})")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ---- Panel 5: Improvement over Standard PL (bar chart) ----
    ax = axes[2, 0]
    bino_methods = ["Naive Dual", "Feature-Split", "Data-Split", "Arch-Split", "Transform-Split"]
    bino_indices = [2, 3, 4, 5, 6]
    x = np.arange(len(bino_methods))
    width = 0.15

    for ai_off, ai in enumerate(range(n_alphas)):
        vals = [improvements[mi, ai] for mi in bino_indices]
        offset = (ai_off - n_alphas/2 + 0.5) * width
        alpha_str = f"a={ALPHA_VALUES[ai]:.1f}"
        ax.bar(x + offset, vals, width, label=alpha_str, alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(bino_methods, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Improvement over Standard PL (%)")
    ax.set_title("5. Improvement by Method and Alpha")
    ax.axhline(y=0, color="black", linewidth=1)
    ax.legend(fontsize=7, ncol=3)
    ax.grid(True, alpha=0.3, axis="y")

    # ---- Panel 6: Heatmap -- diversity method x alpha -> improvement ----
    ax = axes[2, 1]
    heatmap_data = np.zeros((len(bino_methods), n_alphas))
    for i, mi in enumerate(bino_indices):
        for ai in range(n_alphas):
            heatmap_data[i, ai] = improvements[mi, ai]

    im = ax.imshow(heatmap_data, cmap="RdYlGn", aspect="auto",
                   vmin=min(-3, heatmap_data.min()), vmax=max(3, heatmap_data.max()))
    ax.set_xticks(range(n_alphas))
    ax.set_xticklabels([f"{a:.1f}" for a in ALPHA_VALUES])
    ax.set_yticks(range(len(bino_methods)))
    ax.set_yticklabels(bino_methods, fontsize=8)
    ax.set_xlabel("Alpha")
    ax.set_title("6. Improvement Heatmap (% over Standard PL)")

    # Add text annotations
    for i in range(len(bino_methods)):
        for j in range(n_alphas):
            val = heatmap_data[i, j]
            color = "white" if abs(val) > (heatmap_data.max() - heatmap_data.min()) * 0.4 else "black"
            ax.text(j, i, f"{val:+.1f}", ha="center", va="center", fontsize=8,
                    fontweight="bold", color=color)

    plt.colorbar(im, ax=ax, label="Improvement (%)")

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_path = os.path.join(script_dir, "staged_binocular_results.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to: {plot_path}")
    plt.close()

    print()
    print(f"Total runtime: {total_time:.1f}s")
    print()

    return {
        "final_accs": final_accs,
        "method_means": method_means,
        "improvements": improvements,
        "mean_error_corrs": mean_error_corrs,
    }


if __name__ == "__main__":
    results = run_experiment()
