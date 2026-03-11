"""
ML Insights Test: 6 Independent Tests for Practical ML Insights
================================================================
Each test produces a clear YES/NO answer about whether golden cascade
research yielded an actionable insight for ML practitioners.

Tests:
1. Consensus vs Ensemble — is consensus more than ensembling?
2. Settling Generalizes — does test-time settling help standard networks?
3. Surprise as Confidence — does surprise predict correctness better than softmax?
4. Surprise as OOD Detector — does surprise detect OOD better than softmax?
5. Golden Decay Rate — is 0.618 optimal for running average decay?
6. Surprise-Gated LR — does surprise-gated LR beat standard schedules?
"""

import sys
import io

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

import math
import json
import time
import os
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1.0 / PHI          # 0.61803...
INV_PHI2 = 1.0 / PHI ** 2    # 0.38197...

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# MNIST Loading & PCA (shared across all tests)
# ---------------------------------------------------------------------------

def load_mnist(n_train=10000, n_test=2000):
    import torch
    import torchvision
    import torchvision.transforms as transforms

    transform = transforms.Compose([transforms.ToTensor()])
    train_ds = torchvision.datasets.MNIST(
        root="./data", train=True, download=True, transform=transform
    )
    test_ds = torchvision.datasets.MNIST(
        root="./data", train=False, download=True, transform=transform
    )

    def to_numpy(dataset, n):
        images, labels = [], []
        for i in range(min(n, len(dataset))):
            img, lbl = dataset[i]
            images.append(img.numpy().flatten())
            labels.append(lbl)
        return np.array(images, dtype=np.float64), np.array(labels, dtype=int)

    X_train, y_train = to_numpy(train_ds, n_train)
    X_test, y_test = to_numpy(test_ds, n_test)
    return X_train, y_train, X_test, y_test


def fit_pca(X, n_components):
    mean = X.mean(axis=0)
    X_centered = X - mean
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    components = Vt[:n_components]
    return mean, components


def transform_pca(X, mean, components):
    return (X - mean) @ components.T


def prepare_data():
    """Load MNIST, PCA to 50, normalize. Returns Z_train, y_train, Z_test, y_test."""
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)
    pca_mean, pca_comp = fit_pca(X_train, 50)
    Z_train = transform_pca(X_train, pca_mean, pca_comp)
    Z_test = transform_pca(X_test, pca_mean, pca_comp)
    z_max = np.abs(Z_train).max()
    Z_train = Z_train / z_max
    Z_test = Z_test / z_max
    return Z_train, y_train, Z_test, y_test


# ---------------------------------------------------------------------------
# Standard Neural Network (ReLU + backprop, numpy)
# ---------------------------------------------------------------------------

class StandardNetwork:
    """Simple feedforward network with ReLU and backprop. Pure numpy."""

    def __init__(self, layer_sizes, seed=42):
        self.rng = np.random.default_rng(seed)
        self.layer_sizes = layer_sizes
        self.weights = []
        self.biases = []
        for i in range(len(layer_sizes) - 1):
            scale = np.sqrt(2.0 / layer_sizes[i])
            self.weights.append(self.rng.normal(0, scale, (layer_sizes[i], layer_sizes[i+1])))
            self.biases.append(np.zeros(layer_sizes[i+1]))

    def forward(self, x):
        """Forward pass, caching activations for backprop."""
        self.activations = [x.copy()]
        self.pre_activations = []
        h = x
        for i, (W, b) in enumerate(zip(self.weights, self.biases)):
            z = h @ W + b
            self.pre_activations.append(z)
            if i < len(self.weights) - 1:
                h = np.maximum(0, z)  # ReLU
            else:
                # Output: softmax
                e = np.exp(z - z.max())
                h = e / e.sum()
            self.activations.append(h)
        return h

    def predict(self, x):
        out = self.forward(x)
        return int(np.argmax(out)), out

    def train_step(self, x, y, lr=0.01):
        """One step of backprop with cross-entropy loss."""
        out = self.forward(x)
        target = np.zeros(self.layer_sizes[-1])
        target[y] = 1.0

        # Output error (softmax + cross-entropy = simple gradient)
        delta = out - target

        for i in range(len(self.weights) - 1, -1, -1):
            dW = np.outer(self.activations[i], delta)
            db = delta
            self.weights[i] -= lr * np.clip(dW, -1, 1)
            self.biases[i] -= lr * np.clip(db, -1, 1)

            if i > 0:
                delta = (self.weights[i] @ delta) * (self.pre_activations[i-1] > 0).astype(float)

    def get_softmax_entropy(self, x):
        out = self.forward(x)
        out = np.clip(out, 1e-10, 1.0)
        return -np.sum(out * np.log(out))

    def get_max_softmax(self, x):
        out = self.forward(x)
        return float(np.max(out))


# ---------------------------------------------------------------------------
# Consensus Network (from cell_soup_consensus.py, simplified)
# ---------------------------------------------------------------------------

class ConsensusLayer:
    def __init__(self, input_size, n_positions, K=3, decay=INV_PHI,
                 use_golden_cascade=True, rng=None):
        self.input_size = input_size
        self.n_positions = n_positions
        self.K = K
        self.decay = decay
        self.complement = 1.0 - decay
        self.use_golden_cascade = use_golden_cascade

        if rng is None:
            rng = np.random.default_rng(42)
        self.rng = rng

        scale = np.sqrt(2.0 / input_size)
        self.W = rng.normal(0, scale, size=(input_size, n_positions))
        self.b = np.zeros(n_positions)

        self.running_avg = np.zeros((n_positions, K))
        self.cell_offsets = rng.normal(0, 0.1, size=(n_positions, K))

        self.input_activations = None
        self.position_outputs = None
        self.position_surprises = None
        self.cell_outputs = None
        self.cell_surprises = None
        self.pre_activation = None

    def reset_cells(self):
        self.running_avg = self.cell_offsets.copy()

    def forward(self, x):
        self.input_activations = x.copy()
        pre_act = x @ self.W + self.b
        pre_act = np.clip(pre_act, -5, 5)
        self.pre_activation = pre_act

        cell_outputs = np.zeros((self.n_positions, self.K))
        cell_surprises = np.zeros((self.n_positions, self.K))

        for k in range(self.K):
            if self.use_golden_cascade:
                obs = pre_act
                surprise = obs - self.running_avg[:, k]
                output = self.running_avg[:, k] + np.tanh(surprise)
                self.running_avg[:, k] = (self.decay * self.running_avg[:, k] +
                                          self.complement * output)
            else:
                output = np.tanh(pre_act)
                surprise = pre_act - self.running_avg[:, k]
                self.running_avg[:, k] = output

            cell_outputs[:, k] = output
            cell_surprises[:, k] = surprise

        # Consensus: inverse-surprise-weighted mean
        abs_surp = np.abs(cell_surprises)
        weights = 1.0 / (abs_surp + 1e-6)
        weights = weights / weights.sum(axis=1, keepdims=True)
        position_outputs = np.sum(weights * cell_outputs, axis=1)

        position_surprises = np.mean(abs_surp, axis=1)

        self.position_outputs = position_outputs
        self.position_surprises = position_surprises
        self.cell_outputs = cell_outputs
        self.cell_surprises = cell_surprises

        return position_outputs


class ConsensusNetwork:
    def __init__(self, layer_sizes, K=3, decay=INV_PHI,
                 use_golden_cascade=True, seed=42):
        self.rng = np.random.default_rng(seed)
        self.layer_sizes = layer_sizes
        self.K = K
        self.layers = []

        for i in range(len(layer_sizes) - 1):
            layer = ConsensusLayer(
                input_size=layer_sizes[i],
                n_positions=layer_sizes[i + 1],
                K=K, decay=decay,
                use_golden_cascade=use_golden_cascade,
                rng=self.rng,
            )
            self.layers.append(layer)

    def reset(self):
        for layer in self.layers:
            layer.reset_cells()

    def forward(self, x, T_settle=5):
        self.reset()
        for t in range(T_settle):
            h = x.copy()
            for layer in self.layers:
                h = layer.forward(h)
        return h

    def predict(self, x, T_settle=5):
        self.forward(x, T_settle=T_settle)
        surprises = self.layers[-1].position_surprises
        outputs = self.layers[-1].position_outputs
        return int(np.argmax(outputs)), surprises.copy(), outputs.copy()

    def get_all_surprises(self):
        """Get mean surprise across all layers."""
        return np.mean([np.mean(l.position_surprises) for l in self.layers])

    def train_step(self, x, y, lr=0.01, T_settle=5):
        """Pseudo-backprop training (all_supervised mode)."""
        self.forward(x, T_settle=T_settle)

        target = np.zeros(self.layers[-1].n_positions)
        target[y] = 1.0
        output_error = self.layers[-1].position_outputs - target

        for layer_idx in range(len(self.layers) - 1, -1, -1):
            layer = self.layers[layer_idx]
            prev_act = layer.input_activations

            if layer_idx == len(self.layers) - 1:
                error = output_error
            else:
                next_layer = self.layers[layer_idx + 1]
                error = next_layer.W @ next_error
                mean_surp = np.mean(layer.cell_surprises, axis=1)
                deriv = 1.0 - np.tanh(mean_surp) ** 2
                error = error * deriv

            next_error = error
            dW = np.outer(prev_act, error)
            db = error
            layer.W -= lr * np.clip(dW, -1, 1)
            layer.b -= lr * np.clip(db, -1, 1)


def train_consensus_network(Z_train, y_train, K=3, decay=INV_PHI, epochs=10,
                             lr=0.01, T_settle=5, seed=42, verbose=False):
    """Train a consensus network and return it."""
    net = ConsensusNetwork([50, 32, 16, 10], K=K, decay=decay, seed=seed)
    n = len(Z_train)
    for epoch in range(epochs):
        perm = np.random.RandomState(seed + epoch).permutation(n)
        for idx in perm:
            net.train_step(Z_train[idx], y_train[idx], lr=lr, T_settle=T_settle)
        if verbose:
            print(f"    Epoch {epoch+1}/{epochs} done", flush=True)
    return net


def eval_consensus(net, Z, y, T_settle=5):
    """Evaluate consensus network accuracy."""
    correct = 0
    for i in range(len(Z)):
        pred, _, _ = net.predict(Z[i], T_settle=T_settle)
        if pred == y[i]:
            correct += 1
    return correct / len(Z)


def train_standard_network(Z_train, y_train, epochs=10, lr=0.01, seed=42, verbose=False):
    """Train a standard ReLU network."""
    net = StandardNetwork([50, 32, 16, 10], seed=seed)
    n = len(Z_train)
    for epoch in range(epochs):
        perm = np.random.RandomState(seed + epoch).permutation(n)
        for idx in perm:
            net.train_step(Z_train[idx], y_train[idx], lr=lr)
        if verbose:
            print(f"    Epoch {epoch+1}/{epochs} done", flush=True)
    return net


def eval_standard(net, Z, y):
    """Evaluate standard network accuracy."""
    correct = 0
    for i in range(len(Z)):
        pred, _ = net.predict(Z[i])
        if pred == y[i]:
            correct += 1
    return correct / len(Z)


# ---------------------------------------------------------------------------
# Test 1: Consensus vs Ensemble
# ---------------------------------------------------------------------------

def test_consensus_vs_ensemble(Z_train, y_train, Z_test, y_test):
    """Is consensus (K=5) more than just ensembling 5 independent networks?"""
    print("\n" + "="*60)
    print("TEST 1: Consensus vs Ensemble")
    print("="*60)

    results = {'seeds': [], 'consensus_acc': [], 'ensemble_acc': [], 'single_acc': []}

    for seed in [42, 123, 789]:
        print(f"  Seed {seed}:", flush=True)

        # Train K=5 consensus network
        print(f"    Training K=5 consensus...", flush=True)
        net_consensus = train_consensus_network(
            Z_train, y_train, K=5, epochs=10, lr=0.01, T_settle=5, seed=seed
        )
        acc_consensus = eval_consensus(net_consensus, Z_test, y_test, T_settle=5)
        print(f"    Consensus K=5: {acc_consensus:.4f}", flush=True)

        # Train 5 independent K=1 networks and ensemble
        print(f"    Training 5 independent K=1 networks...", flush=True)
        ensemble_nets = []
        for i in range(5):
            net_i = train_consensus_network(
                Z_train, y_train, K=1, epochs=10, lr=0.01, T_settle=5, seed=seed + i * 100
            )
            ensemble_nets.append(net_i)

        # Ensemble: average output activations, then argmax
        ensemble_correct = 0
        for j in range(len(Z_test)):
            avg_out = np.zeros(10)
            for net_i in ensemble_nets:
                _, _, outputs = net_i.predict(Z_test[j], T_settle=5)
                avg_out += outputs
            avg_out /= 5
            if np.argmax(avg_out) == y_test[j]:
                ensemble_correct += 1
        acc_ensemble = ensemble_correct / len(Z_test)
        print(f"    Ensemble of 5: {acc_ensemble:.4f}", flush=True)

        # Single K=1 baseline
        acc_single = eval_consensus(ensemble_nets[0], Z_test, y_test, T_settle=5)
        print(f"    Single K=1: {acc_single:.4f}", flush=True)

        results['seeds'].append(seed)
        results['consensus_acc'].append(acc_consensus)
        results['ensemble_acc'].append(acc_ensemble)
        results['single_acc'].append(acc_single)

    mean_consensus = np.mean(results['consensus_acc'])
    mean_ensemble = np.mean(results['ensemble_acc'])
    mean_single = np.mean(results['single_acc'])
    std_consensus = np.std(results['consensus_acc'])
    std_ensemble = np.std(results['ensemble_acc'])

    diff = mean_consensus - mean_ensemble
    results['mean_consensus'] = mean_consensus
    results['mean_ensemble'] = mean_ensemble
    results['mean_single'] = mean_single
    results['std_consensus'] = std_consensus
    results['std_ensemble'] = std_ensemble
    results['diff'] = diff

    # Verdict
    if diff > 0.02:
        verdict = "YES"
        desc = f"Consensus beats ensemble by {diff:.1%} -- shared-input diversity adds value beyond ensembling"
    elif diff > -0.02:
        verdict = "NO"
        desc = f"Consensus ~ ensemble (diff={diff:.1%}) -- it's just ensembling, nothing new"
    else:
        verdict = "NO"
        desc = f"Ensemble beats consensus by {-diff:.1%} -- standard ensembling is better"

    results['verdict'] = verdict
    results['description'] = desc
    print(f"\n  INSIGHT: [{verdict}] {desc}")
    print(f"  Consensus: {mean_consensus:.4f} +/- {std_consensus:.4f}")
    print(f"  Ensemble:  {mean_ensemble:.4f} +/- {std_ensemble:.4f}")
    print(f"  Single:    {mean_single:.4f}")
    return results


# ---------------------------------------------------------------------------
# Test 2: Settling Generalizes
# ---------------------------------------------------------------------------

def test_settling_generalizes(Z_train, y_train, Z_test, y_test):
    """Does test-time settling help standard networks too?"""
    print("\n" + "="*60)
    print("TEST 2: Settling Generalizes to Standard Networks?")
    print("="*60)

    results = {'seeds': [], 'standard_1pass': [], 'standard_5pass': [],
               'consensus_T1': [], 'consensus_T5': []}

    for seed in [42, 123, 789]:
        print(f"  Seed {seed}:", flush=True)

        # Train standard ReLU network
        print(f"    Training standard network...", flush=True)
        std_net = train_standard_network(Z_train, y_train, epochs=10, lr=0.01, seed=seed)

        # Evaluate with 1 forward pass
        acc_1pass = eval_standard(std_net, Z_test, y_test)
        print(f"    Standard 1-pass: {acc_1pass:.4f}", flush=True)

        # Evaluate with 5 forward passes (self-recurrent: add residual connection)
        # For a standard network, "settling" means: run forward pass, take output,
        # feed it back as residual addition to intermediate layers
        correct_5pass = 0
        for j in range(len(Z_test)):
            # Pass 1: normal
            out = std_net.forward(Z_test[j])
            # Passes 2-5: add output as soft residual to input
            for t in range(4):
                # Create modified input: original + scaled output feedback
                feedback = np.zeros(50)
                # Map 10-d output back to 50-d input space using transpose of last weight
                feedback[:10] = out * 0.1  # small residual
                modified_input = Z_test[j] + feedback
                out = std_net.forward(modified_input)
            if np.argmax(out) == y_test[j]:
                correct_5pass += 1
        acc_5pass = correct_5pass / len(Z_test)
        print(f"    Standard 5-pass (residual): {acc_5pass:.4f}", flush=True)

        # Consensus network at T=1 and T=5
        print(f"    Training consensus network...", flush=True)
        cons_net = train_consensus_network(
            Z_train, y_train, K=3, epochs=10, lr=0.01, T_settle=5, seed=seed
        )
        acc_T1 = eval_consensus(cons_net, Z_test, y_test, T_settle=1)
        acc_T5 = eval_consensus(cons_net, Z_test, y_test, T_settle=5)
        print(f"    Consensus T=1: {acc_T1:.4f}", flush=True)
        print(f"    Consensus T=5: {acc_T5:.4f}", flush=True)

        results['seeds'].append(seed)
        results['standard_1pass'].append(acc_1pass)
        results['standard_5pass'].append(acc_5pass)
        results['consensus_T1'].append(acc_T1)
        results['consensus_T5'].append(acc_T5)

    mean_1p = np.mean(results['standard_1pass'])
    mean_5p = np.mean(results['standard_5pass'])
    mean_T1 = np.mean(results['consensus_T1'])
    mean_T5 = np.mean(results['consensus_T5'])
    std_diff = mean_5p - mean_1p
    cons_diff = mean_T5 - mean_T1

    results['mean_standard_1pass'] = mean_1p
    results['mean_standard_5pass'] = mean_5p
    results['mean_consensus_T1'] = mean_T1
    results['mean_consensus_T5'] = mean_T5
    results['standard_settling_gain'] = std_diff
    results['consensus_settling_gain'] = cons_diff

    if cons_diff > 0.01 and std_diff < 0.01:
        verdict = "YES"
        desc = f"Settling helps consensus (+{cons_diff:.1%}) but not standard (+{std_diff:.1%}) -- running avg mechanism is key"
    elif std_diff > 0.01:
        verdict = "PARTIAL"
        desc = f"Settling helps both: standard +{std_diff:.1%}, consensus +{cons_diff:.1%} -- general test-time compute insight"
    else:
        verdict = "NO"
        desc = f"Settling gain is small for both (standard +{std_diff:.1%}, consensus +{cons_diff:.1%})"

    results['verdict'] = verdict
    results['description'] = desc
    print(f"\n  INSIGHT: [{verdict}] {desc}")
    print(f"  Standard: {mean_1p:.4f} -> {mean_5p:.4f} (gain: {std_diff:+.4f})")
    print(f"  Consensus: {mean_T1:.4f} -> {mean_T5:.4f} (gain: {cons_diff:+.4f})")
    return results


# ---------------------------------------------------------------------------
# Test 3: Surprise as Confidence Signal
# ---------------------------------------------------------------------------

def test_surprise_confidence(Z_train, y_train, Z_test, y_test):
    """Does surprise predict correctness better than softmax entropy?"""
    print("\n" + "="*60)
    print("TEST 3: Surprise as Confidence Signal")
    print("="*60)

    results = {'seeds': [], 'surprise_auroc': [], 'entropy_auroc': [],
               'surprise_cohens_d': []}

    for seed in [42, 123, 789]:
        print(f"  Seed {seed}:", flush=True)

        # Train consensus network
        cons_net = train_consensus_network(
            Z_train, y_train, K=3, epochs=10, lr=0.01, T_settle=5, seed=seed
        )

        # Train standard network for softmax baseline
        std_net = train_standard_network(Z_train, y_train, epochs=10, lr=0.01, seed=seed)

        surprises_correct = []
        surprises_incorrect = []
        all_surprises = []
        all_correct = []
        all_entropies = []
        all_correct_std = []

        for j in range(len(Z_test)):
            # Consensus: surprise
            pred, surp, out = cons_net.predict(Z_test[j], T_settle=5)
            mean_surp = float(np.mean(surp))
            is_correct = (pred == y_test[j])
            all_surprises.append(mean_surp)
            all_correct.append(is_correct)
            if is_correct:
                surprises_correct.append(mean_surp)
            else:
                surprises_incorrect.append(mean_surp)

            # Standard: softmax entropy
            entropy = std_net.get_softmax_entropy(Z_test[j])
            pred_std, _ = std_net.predict(Z_test[j])
            all_entropies.append(entropy)
            all_correct_std.append(pred_std == y_test[j])

        # Cohen's d for surprise
        if surprises_correct and surprises_incorrect:
            m1 = np.mean(surprises_correct)
            m2 = np.mean(surprises_incorrect)
            s1 = np.std(surprises_correct)
            s2 = np.std(surprises_incorrect)
            pooled_std = np.sqrt((s1**2 + s2**2) / 2)
            cohens_d = abs(m2 - m1) / (pooled_std + 1e-10)
        else:
            cohens_d = 0.0

        # AUROC for surprise (higher surprise = predicted incorrect)
        surprise_auroc = compute_auroc(all_surprises, [not c for c in all_correct])
        # AUROC for entropy (higher entropy = predicted incorrect)
        entropy_auroc = compute_auroc(all_entropies, [not c for c in all_correct_std])

        print(f"    Surprise AUROC: {surprise_auroc:.4f}, Cohen's d: {cohens_d:.4f}")
        print(f"    Entropy AUROC:  {entropy_auroc:.4f}")

        results['seeds'].append(seed)
        results['surprise_auroc'].append(surprise_auroc)
        results['entropy_auroc'].append(entropy_auroc)
        results['surprise_cohens_d'].append(cohens_d)

    mean_s_auroc = np.mean(results['surprise_auroc'])
    mean_e_auroc = np.mean(results['entropy_auroc'])
    mean_d = np.mean(results['surprise_cohens_d'])

    results['mean_surprise_auroc'] = mean_s_auroc
    results['mean_entropy_auroc'] = mean_e_auroc
    results['mean_cohens_d'] = mean_d

    if mean_s_auroc > mean_e_auroc + 0.02:
        verdict = "YES"
        desc = f"Surprise AUROC ({mean_s_auroc:.3f}) beats entropy ({mean_e_auroc:.3f}) -- practical confidence tool"
    elif mean_s_auroc > 0.6 and mean_d > 0.3:
        verdict = "PARTIAL"
        desc = f"Surprise works (AUROC={mean_s_auroc:.3f}, d={mean_d:.3f}) but doesn't beat entropy ({mean_e_auroc:.3f})"
    else:
        verdict = "NO"
        desc = f"Surprise AUROC={mean_s_auroc:.3f} (d={mean_d:.3f}) -- not a useful confidence signal"

    results['verdict'] = verdict
    results['description'] = desc
    print(f"\n  INSIGHT: [{verdict}] {desc}")
    return results


def compute_auroc(scores, labels):
    """Compute AUROC. Higher score should predict True label."""
    scores = np.array(scores)
    labels = np.array(labels, dtype=bool)

    if labels.sum() == 0 or labels.sum() == len(labels):
        return 0.5

    # Sort by score descending
    desc_idx = np.argsort(-scores)
    sorted_labels = labels[desc_idx]

    # Compute TPR and FPR at each threshold
    n_pos = labels.sum()
    n_neg = len(labels) - n_pos

    tp = 0
    fp = 0
    tpr_prev = 0
    fpr_prev = 0
    auc = 0.0

    for i in range(len(sorted_labels)):
        if sorted_labels[i]:
            tp += 1
        else:
            fp += 1
        tpr = tp / n_pos
        fpr = fp / n_neg
        # Trapezoid rule
        auc += (fpr - fpr_prev) * (tpr + tpr_prev) / 2
        tpr_prev = tpr
        fpr_prev = fpr

    return auc


# ---------------------------------------------------------------------------
# Test 4: Surprise as OOD Detector
# ---------------------------------------------------------------------------

def test_surprise_ood(Z_train, y_train, Z_test, y_test):
    """Does surprise detect OOD better than softmax entropy?"""
    print("\n" + "="*60)
    print("TEST 4: Surprise as OOD Detector")
    print("="*60)

    results = {'seeds': [], 'surprise_auroc': [], 'entropy_auroc': [],
               'max_softmax_auroc': []}

    for seed in [42, 123, 789]:
        print(f"  Seed {seed}:", flush=True)

        # Train on digits 0-7, test on 8-9 as OOD
        mask_train = y_train <= 7
        mask_test_id = y_test <= 7
        mask_test_ood = y_test >= 8

        Z_tr = Z_train[mask_train]
        y_tr = y_train[mask_train]

        # Train consensus network
        cons_net = train_consensus_network(
            Z_tr, y_tr, K=3, epochs=10, lr=0.01, T_settle=5, seed=seed
        )
        # Train standard network
        std_net = train_standard_network(Z_tr, y_tr, epochs=10, lr=0.01, seed=seed)

        # Evaluate surprise and entropy on ID and OOD
        all_surprises = []
        all_entropies = []
        all_max_softmax = []
        all_is_ood = []

        Z_test_combined = np.concatenate([Z_test[mask_test_id], Z_test[mask_test_ood]])
        is_ood = np.concatenate([np.zeros(mask_test_id.sum()), np.ones(mask_test_ood.sum())])

        for j in range(len(Z_test_combined)):
            # Surprise (all layers)
            pred, surp, out = cons_net.predict(Z_test_combined[j], T_settle=5)
            mean_surp = cons_net.get_all_surprises()
            all_surprises.append(mean_surp)

            # Entropy
            entropy = std_net.get_softmax_entropy(Z_test_combined[j])
            all_entropies.append(entropy)

            # Max softmax (lower = more likely OOD)
            max_sm = std_net.get_max_softmax(Z_test_combined[j])
            all_max_softmax.append(-max_sm)  # negate so higher = more OOD

            all_is_ood.append(bool(is_ood[j]))

        surprise_auroc = compute_auroc(all_surprises, all_is_ood)
        entropy_auroc = compute_auroc(all_entropies, all_is_ood)
        max_sm_auroc = compute_auroc(all_max_softmax, all_is_ood)

        n_id = mask_test_id.sum()
        n_ood = mask_test_ood.sum()
        mean_surp_id = np.mean(all_surprises[:n_id])
        mean_surp_ood = np.mean(all_surprises[n_id:])

        print(f"    ID surprise: {mean_surp_id:.4f}, OOD surprise: {mean_surp_ood:.4f}")
        print(f"    Surprise AUROC: {surprise_auroc:.4f}")
        print(f"    Entropy AUROC:  {entropy_auroc:.4f}")
        print(f"    Max-softmax AUROC: {max_sm_auroc:.4f}")

        results['seeds'].append(seed)
        results['surprise_auroc'].append(surprise_auroc)
        results['entropy_auroc'].append(entropy_auroc)
        results['max_softmax_auroc'].append(max_sm_auroc)

    mean_s = np.mean(results['surprise_auroc'])
    mean_e = np.mean(results['entropy_auroc'])
    mean_m = np.mean(results['max_softmax_auroc'])

    results['mean_surprise_auroc'] = mean_s
    results['mean_entropy_auroc'] = mean_e
    results['mean_max_softmax_auroc'] = mean_m

    best_baseline = max(mean_e, mean_m)
    if mean_s > best_baseline + 0.02:
        verdict = "YES"
        desc = f"Surprise AUROC ({mean_s:.3f}) beats baselines (entropy={mean_e:.3f}, max-sm={mean_m:.3f})"
    elif mean_s > 0.8:
        verdict = "PARTIAL"
        desc = f"Surprise works (AUROC={mean_s:.3f}) but doesn't beat baselines (entropy={mean_e:.3f}, max-sm={mean_m:.3f})"
    else:
        verdict = "NO"
        desc = f"Surprise AUROC ({mean_s:.3f}) not useful for OOD (baselines: entropy={mean_e:.3f}, max-sm={mean_m:.3f})"

    results['verdict'] = verdict
    results['description'] = desc
    print(f"\n  INSIGHT: [{verdict}] {desc}")
    return results


# ---------------------------------------------------------------------------
# Test 5: Golden Decay Rate
# ---------------------------------------------------------------------------

def test_golden_decay(Z_train, y_train, Z_test, y_test):
    """Is 0.618 optimal for running average decay?"""
    print("\n" + "="*60)
    print("TEST 5: Golden Ratio Decay Rate")
    print("="*60)

    decay_rates = [0.3, 0.5, 0.618, 0.7, 0.9]
    results = {'decay_rates': decay_rates, 'accuracies': {str(d): [] for d in decay_rates}}

    for seed in [42, 123, 789]:
        print(f"  Seed {seed}:", flush=True)
        for decay in decay_rates:
            net = train_consensus_network(
                Z_train, y_train, K=3, decay=decay, epochs=10,
                lr=0.01, T_settle=5, seed=seed
            )
            acc = eval_consensus(net, Z_test, y_test, T_settle=5)
            results['accuracies'][str(decay)].append(acc)
            print(f"    decay={decay:.3f}: {acc:.4f}", flush=True)

    # Find best
    mean_accs = {}
    for d in decay_rates:
        mean_accs[d] = np.mean(results['accuracies'][str(d)])

    best_decay = max(mean_accs, key=mean_accs.get)
    best_acc = mean_accs[best_decay]
    golden_acc = mean_accs[0.618]
    golden_std = np.std(results['accuracies']['0.618'])

    results['mean_accuracies'] = {str(d): mean_accs[d] for d in decay_rates}
    results['std_accuracies'] = {str(d): float(np.std(results['accuracies'][str(d)])) for d in decay_rates}
    results['best_decay'] = best_decay
    results['best_acc'] = best_acc
    results['golden_acc'] = golden_acc

    if best_decay == 0.618 and best_acc - sorted(mean_accs.values())[-2] > 0.005:
        verdict = "YES"
        desc = f"0.618 is optimal ({golden_acc:.4f}) -- golden ratio has practical value as default decay"
    elif abs(golden_acc - best_acc) < 0.01:
        verdict = "WEAK"
        desc = f"0.618 ({golden_acc:.4f}) is competitive but not uniquely best (best={best_decay}: {best_acc:.4f})"
    else:
        verdict = "NO"
        desc = f"0.618 ({golden_acc:.4f}) is not optimal; best={best_decay} ({best_acc:.4f})"

    results['verdict'] = verdict
    results['description'] = desc
    print(f"\n  INSIGHT: [{verdict}] {desc}")
    for d in decay_rates:
        m = mean_accs[d]
        s = np.std(results['accuracies'][str(d)])
        marker = " <-- golden" if d == 0.618 else (" <-- best" if d == best_decay else "")
        print(f"  decay={d:.3f}: {m:.4f} +/- {s:.4f}{marker}")
    return results


# ---------------------------------------------------------------------------
# Test 6: Surprise-Gated Learning Rate
# ---------------------------------------------------------------------------

def test_surprise_gated_lr(Z_train, y_train, Z_test, y_test):
    """Does surprise-gated LR beat standard schedules?"""
    print("\n" + "="*60)
    print("TEST 6: Surprise-Gated Learning Rate")
    print("="*60)

    results = {'seeds': [], 'fixed_acc': [], 'cosine_acc': [],
               'surprise_gated_acc': []}

    base_lr = 0.01
    epochs = 10

    for seed in [42, 123, 789]:
        print(f"  Seed {seed}:", flush=True)
        n = len(Z_train)
        total_steps = n * epochs

        # --- Fixed LR ---
        net_fixed = ConsensusNetwork([50, 32, 16, 10], K=3, seed=seed)
        for epoch in range(epochs):
            perm = np.random.RandomState(seed + epoch).permutation(n)
            for idx in perm:
                net_fixed.train_step(Z_train[idx], y_train[idx], lr=base_lr, T_settle=5)
        acc_fixed = eval_consensus(net_fixed, Z_test, y_test, T_settle=5)
        print(f"    Fixed LR: {acc_fixed:.4f}", flush=True)

        # --- Cosine decay ---
        net_cosine = ConsensusNetwork([50, 32, 16, 10], K=3, seed=seed)
        step = 0
        for epoch in range(epochs):
            perm = np.random.RandomState(seed + epoch).permutation(n)
            for idx in perm:
                lr_cos = base_lr * 0.5 * (1 + math.cos(math.pi * step / total_steps))
                net_cosine.train_step(Z_train[idx], y_train[idx], lr=lr_cos, T_settle=5)
                step += 1
        acc_cosine = eval_consensus(net_cosine, Z_test, y_test, T_settle=5)
        print(f"    Cosine LR: {acc_cosine:.4f}", flush=True)

        # --- Surprise-gated LR ---
        net_surprise = ConsensusNetwork([50, 32, 16, 10], K=3, seed=seed)
        # First pass: estimate surprise threshold from first epoch
        surprise_values = []
        perm0 = np.random.RandomState(seed).permutation(n)
        for idx in perm0[:min(500, n)]:
            net_surprise.forward(Z_train[idx], T_settle=5)
            surprise_values.append(net_surprise.get_all_surprises())
        surprise_threshold = np.mean(surprise_values) + 1e-6

        for epoch in range(epochs):
            perm = np.random.RandomState(seed + epoch).permutation(n)
            for idx in perm:
                # Get surprise before update
                net_surprise.forward(Z_train[idx], T_settle=5)
                mean_surprise = net_surprise.get_all_surprises()
                gate = np.clip(mean_surprise / surprise_threshold, 0.1, 2.0)
                effective_lr = base_lr * gate
                net_surprise.train_step(Z_train[idx], y_train[idx],
                                        lr=effective_lr, T_settle=5)
        acc_surprise = eval_consensus(net_surprise, Z_test, y_test, T_settle=5)
        print(f"    Surprise-gated LR: {acc_surprise:.4f}", flush=True)

        results['seeds'].append(seed)
        results['fixed_acc'].append(acc_fixed)
        results['cosine_acc'].append(acc_cosine)
        results['surprise_gated_acc'].append(acc_surprise)

    mean_fixed = np.mean(results['fixed_acc'])
    mean_cosine = np.mean(results['cosine_acc'])
    mean_surprise = np.mean(results['surprise_gated_acc'])

    results['mean_fixed'] = mean_fixed
    results['mean_cosine'] = mean_cosine
    results['mean_surprise_gated'] = mean_surprise

    best_baseline = max(mean_fixed, mean_cosine)
    if mean_surprise > best_baseline + 0.02:
        verdict = "YES"
        desc = f"Surprise-gated ({mean_surprise:.4f}) beats fixed ({mean_fixed:.4f}) and cosine ({mean_cosine:.4f})"
    elif mean_surprise > best_baseline - 0.01:
        verdict = "PARTIAL"
        desc = f"Surprise-gated ({mean_surprise:.4f}) competitive with baselines (fixed={mean_fixed:.4f}, cosine={mean_cosine:.4f})"
    else:
        verdict = "NO"
        desc = f"Surprise-gated ({mean_surprise:.4f}) doesn't beat baselines (fixed={mean_fixed:.4f}, cosine={mean_cosine:.4f})"

    results['verdict'] = verdict
    results['description'] = desc
    print(f"\n  INSIGHT: [{verdict}] {desc}")
    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

COLORS = ["#61a0ff", "#ff6161", "#61ff8a", "#ffd761", "#ff61d4", "#61ffd4"]

def _styled_fig(nrows, ncols, **kwargs):
    fig, axes = plt.subplots(nrows, ncols, **kwargs)
    fig.patch.set_facecolor("#0e0e1a")
    ax_list = axes.flat if hasattr(axes, "flat") else [axes]
    for ax in ax_list:
        ax.set_facecolor("#12121f")
        ax.tick_params(colors="#aaaacc")
        ax.xaxis.label.set_color("#aaaacc")
        ax.yaxis.label.set_color("#aaaacc")
        ax.title.set_color("#ccccee")
        for spine in ax.spines.values():
            spine.set_edgecolor("#333355")
    return fig, axes


def plot_all_results(all_results, save_path):
    """Create 2x3 grid with one panel per test."""
    fig, axes = _styled_fig(2, 3, figsize=(18, 10))
    fig.suptitle("ML Insights from Golden Cascade Research", color="#eeeeff", fontsize=14)

    # Test 1: Consensus vs Ensemble
    ax = axes[0, 0]
    r = all_results['test1']
    methods = ['Single\nK=1', 'Ensemble\nof 5', 'Consensus\nK=5']
    accs = [r['mean_single'], r['mean_ensemble'], r['mean_consensus']]
    bars = ax.bar(methods, accs, color=[COLORS[0], COLORS[1], COLORS[2]],
                  edgecolor='white', linewidth=0.5)
    ax.set_ylabel('Accuracy')
    ax.set_title(f'Test 1: Consensus vs Ensemble [{r["verdict"]}]')
    ax.set_ylim(0, 1)
    for bar, acc in zip(bars, accs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{acc:.3f}", ha='center', color='#ccccee', fontsize=9)

    # Test 2: Settling
    ax = axes[0, 1]
    r = all_results['test2']
    x = [0, 1, 2, 3]
    labels = ['Std\n1-pass', 'Std\n5-pass', 'Cons\nT=1', 'Cons\nT=5']
    accs = [r['mean_standard_1pass'], r['mean_standard_5pass'],
            r['mean_consensus_T1'], r['mean_consensus_T5']]
    bar_colors = [COLORS[0] + '80', COLORS[0], COLORS[2] + '80', COLORS[2]]
    bars = ax.bar(x, accs, color=bar_colors, edgecolor='white', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel('Accuracy')
    ax.set_title(f'Test 2: Settling [{r["verdict"]}]')
    ax.set_ylim(0, 1)
    for xi, acc in zip(x, accs):
        ax.text(xi, acc + 0.02, f"{acc:.3f}", ha='center', color='#ccccee', fontsize=9)

    # Test 3: Surprise Confidence
    ax = axes[0, 2]
    r = all_results['test3']
    methods = ['Surprise\nAUROC', 'Entropy\nAUROC']
    vals = [r['mean_surprise_auroc'], r['mean_entropy_auroc']]
    bars = ax.bar(methods, vals, color=[COLORS[2], COLORS[1]], edgecolor='white', linewidth=0.5)
    ax.set_ylabel('AUROC')
    ax.set_title(f'Test 3: Confidence [{r["verdict"]}]')
    ax.set_ylim(0, 1)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Random')
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.3f}", ha='center', color='#ccccee', fontsize=9)

    # Test 4: OOD Detection
    ax = axes[1, 0]
    r = all_results['test4']
    methods = ['Surprise', 'Entropy', 'Max-SM']
    vals = [r['mean_surprise_auroc'], r['mean_entropy_auroc'], r['mean_max_softmax_auroc']]
    bars = ax.bar(methods, vals, color=[COLORS[2], COLORS[1], COLORS[3]],
                  edgecolor='white', linewidth=0.5)
    ax.set_ylabel('AUROC')
    ax.set_title(f'Test 4: OOD Detection [{r["verdict"]}]')
    ax.set_ylim(0, 1)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.3f}", ha='center', color='#ccccee', fontsize=9)

    # Test 5: Golden Decay
    ax = axes[1, 1]
    r = all_results['test5']
    decays = r['decay_rates']
    means = [r['mean_accuracies'][str(d)] for d in decays]
    stds = [r['std_accuracies'][str(d)] for d in decays]
    golden_idx = decays.index(0.618)
    bars5 = ax.bar(range(len(decays)), means, yerr=stds, color=COLORS[:len(decays)],
           edgecolor='white', linewidth=0.5, capsize=3)
    bars5[golden_idx].set_edgecolor('#ffd700')
    bars5[golden_idx].set_linewidth(2)
    ax.set_xticks(range(len(decays)))
    ax.set_xticklabels([str(d) for d in decays])
    ax.set_xlabel('Decay Rate')
    ax.set_ylabel('Accuracy')
    ax.set_title(f'Test 5: Decay Rate [{r["verdict"]}]')
    for i, (m, s) in enumerate(zip(means, stds)):
        ax.text(i, m + s + 0.01, f"{m:.3f}", ha='center', color='#ccccee', fontsize=8)

    # Test 6: Surprise-Gated LR
    ax = axes[1, 2]
    r = all_results['test6']
    methods = ['Fixed', 'Cosine', 'Surprise-\nGated']
    vals = [r['mean_fixed'], r['mean_cosine'], r['mean_surprise_gated']]
    bars = ax.bar(methods, vals, color=[COLORS[0], COLORS[1], COLORS[2]],
                  edgecolor='white', linewidth=0.5)
    ax.set_ylabel('Accuracy')
    ax.set_title(f'Test 6: LR Schedule [{r["verdict"]}]')
    ax.set_ylim(0, 1)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.3f}", ha='center', color='#ccccee', fontsize=9)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {save_path}", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t_start = time.time()

    print("=" * 60)
    print("ML INSIGHTS TEST: 6 Tests for Practical ML Insights")
    print("=" * 60)

    # Shared data
    print("\nLoading data...", flush=True)
    Z_train, y_train, Z_test, y_test = prepare_data()
    print(f"  Data ready: train={Z_train.shape}, test={Z_test.shape}", flush=True)

    all_results = {}

    # Test 1: Consensus vs Ensemble
    all_results['test1'] = test_consensus_vs_ensemble(Z_train, y_train, Z_test, y_test)

    # Test 2: Settling Generalizes
    all_results['test2'] = test_settling_generalizes(Z_train, y_train, Z_test, y_test)

    # Test 3: Surprise as Confidence
    all_results['test3'] = test_surprise_confidence(Z_train, y_train, Z_test, y_test)

    # Test 4: Surprise as OOD Detector
    all_results['test4'] = test_surprise_ood(Z_train, y_train, Z_test, y_test)

    # Test 5: Golden Decay Rate
    all_results['test5'] = test_golden_decay(Z_train, y_train, Z_test, y_test)

    # Test 6: Surprise-Gated LR
    all_results['test6'] = test_surprise_gated_lr(Z_train, y_train, Z_test, y_test)

    # Save JSON first (before plot, in case plot fails)
    json_path = os.path.join(PLOTS_DIR, "ml_insights_results.json")

    # Clean results for JSON (remove numpy types)
    def clean_for_json(obj):
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(v) for v in obj]
        elif isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return obj

    with open(json_path, "w") as f:
        json.dump(clean_for_json(all_results), f, indent=2)
    print(f"  Results saved: {json_path}", flush=True)

    # Plot
    print("\nPlotting...", flush=True)
    try:
        plot_all_results(all_results, os.path.join(PLOTS_DIR, "ml_insights.png"))
    except Exception as e:
        print(f"  Plot failed: {e}", flush=True)

    # Final summary
    elapsed = time.time() - t_start
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    verdicts = []
    for i in range(1, 7):
        key = f'test{i}'
        r = all_results[key]
        v = r['verdict']
        d = r['description']
        print(f"  Test {i}: [{v}] {d}")
        verdicts.append(v)

    yes_count = verdicts.count('YES')
    partial_count = verdicts.count('PARTIAL') + verdicts.count('WEAK')
    no_count = verdicts.count('NO')

    print(f"\n  Verdicts: {yes_count} YES, {partial_count} PARTIAL, {no_count} NO")
    print(f"  Total time: {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
