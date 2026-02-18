"""
Dropout Rate Sweep Experiment
==============================
Tests whether dropout rate p = 1/phi^2 ~ 0.382 is optimal or near-optimal
for generalization.

Hypothesis: The golden ratio fraction 1/phi^2 ~ 0.382 represents an optimal
regularization strength, balancing information retention (~62%) with noise
injection (~38%) at the edge of chaos.

Architecture: MLP with 2 hidden layers + dropout.
    Input(784) -> Linear(512) -> BN -> ReLU -> Dropout(p)
              -> Linear(256) -> BN -> ReLU -> Dropout(p)
              -> Linear(10)
Only the dropout rate p varies across configs.

Sweep: [0.0, 0.1, 0.2, 0.25, 0.3, 0.35, 0.382, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]
Seeds: 3 per config for error bars
Epochs: 30 per config
Dataset: CIFAR-10 (3k balanced train subset, full 10k test for final eval)

NOTE: Uses MLP with data subset for CPU feasibility.
MLPs overfit more easily than CNNs, making dropout differences MORE pronounced.
Dropout was originally designed for fully-connected layers (Srivastava et al. 2014).

Author: Claude (phi-optimal dropout investigation)
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

import os
import time
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Constants
PHI = (1 + np.sqrt(5)) / 2
INV_PHI2 = 1.0 / PHI**2  # ~0.3820

DROPOUT_RATES = [0.0, 0.1, 0.2, 0.25, 0.3, 0.35, 0.382, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7]
SEEDS = [42, 137, 256]
NUM_EPOCHS = 30
LEARNING_RATE = 1e-3
TRAIN_SUBSET = 3000  # Balanced: 300 per class

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
PLOTS_DIR = os.path.join(SCRIPT_DIR, "plots")
RESULTS_FILE = os.path.join(SCRIPT_DIR, "plots", "dropout_sweep_results.json")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# Device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DropoutMLP(nn.Module):
    """MLP with configurable dropout rate for CIFAR-10.

    Architecture:
    - Flatten 3x32x32 = 3072 input dims
    - Hidden layer 1: 512 units with BN + ReLU + Dropout
    - Hidden layer 2: 256 units with BN + ReLU + Dropout
    - Output: 10 classes
    """

    def __init__(self, input_dim=3072, dropout_rate=0.5):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(256, 10),
        )

    def forward(self, x):
        return self.net(x)


def load_cifar10_tensors():
    """Load CIFAR-10 and precompute tensors for fast training."""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])

    trainset = torchvision.datasets.CIFAR10(
        root=DATA_DIR, train=True, download=True, transform=transform
    )
    testset = torchvision.datasets.CIFAR10(
        root=DATA_DIR, train=False, download=True, transform=transform
    )

    # Extract balanced subset for training (300 per class)
    rng = np.random.RandomState(999)
    per_class = TRAIN_SUBSET // 10
    indices = []
    targets = np.array(trainset.targets)
    for c in range(10):
        class_idx = np.where(targets == c)[0]
        chosen = rng.choice(class_idx, per_class, replace=False)
        indices.extend(chosen.tolist())
    rng.shuffle(indices)

    # Pre-load ALL data into tensors (avoids DataLoader overhead)
    print("  Pre-loading training data into tensors...", flush=True)
    train_x = torch.stack([trainset[i][0] for i in indices])  # (3000, 3, 32, 32)
    train_y = torch.tensor([trainset[i][1] for i in indices])

    print("  Pre-loading test data into tensors...", flush=True)
    test_x = torch.stack([testset[i][0] for i in range(len(testset))])
    test_y = torch.tensor([testset[i][1] for i in range(len(testset))])

    return train_x.to(DEVICE), train_y.to(DEVICE), test_x.to(DEVICE), test_y.to(DEVICE)


def train_one_epoch(model, train_x, train_y, criterion, optimizer):
    """Train for one epoch on full batch. Return (loss, accuracy)."""
    model.train()
    optimizer.zero_grad()
    outputs = model(train_x)
    loss = criterion(outputs, train_y)
    loss.backward()
    optimizer.step()

    _, predicted = outputs.max(1)
    accuracy = 100.0 * predicted.eq(train_y).sum().item() / train_y.size(0)
    return loss.item(), accuracy


def evaluate(model, test_x, test_y, criterion):
    """Evaluate model on full test set. Return (loss, accuracy)."""
    model.eval()
    with torch.no_grad():
        # Process in chunks to avoid memory issues
        chunk_size = 2000
        total_loss = 0.0
        correct = 0
        total = test_x.size(0)
        for i in range(0, total, chunk_size):
            x_chunk = test_x[i:i+chunk_size]
            y_chunk = test_y[i:i+chunk_size]
            outputs = model(x_chunk)
            loss = criterion(outputs, y_chunk)
            total_loss += loss.item() * x_chunk.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(y_chunk).sum().item()

    return total_loss / total, 100.0 * correct / total


def run_single_config(dropout_rate, seed, train_x, train_y, test_x, test_y):
    """Train one model with given dropout rate and seed. Return results dict."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    model = DropoutMLP(input_dim=3072, dropout_rate=dropout_rate).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_test_acc = 0.0
    best_test_loss = float("inf")
    best_epoch = 0
    best_train_acc = 0.0

    for epoch in range(NUM_EPOCHS):
        train_loss, train_acc = train_one_epoch(model, train_x, train_y, criterion, optimizer)
        test_loss, test_acc = evaluate(model, test_x, test_y, criterion)

        if test_acc > best_test_acc:
            best_test_acc = test_acc
            best_test_loss = test_loss
            best_epoch = epoch + 1
            best_train_acc = train_acc

    # Final epoch stats
    final_test_loss, final_test_acc = evaluate(model, test_x, test_y, criterion)
    model.train()
    with torch.no_grad():
        outputs = model(train_x)
        _, predicted = outputs.max(1)
        final_train_acc = 100.0 * predicted.eq(train_y).sum().item() / train_y.size(0)

    return {
        "dropout_rate": dropout_rate,
        "seed": seed,
        "best_test_acc": best_test_acc,
        "best_test_loss": best_test_loss,
        "best_epoch": best_epoch,
        "best_train_acc": best_train_acc,
        "train_test_gap": best_train_acc - best_test_acc,
        "final_train_acc": final_train_acc,
        "final_test_acc": final_test_acc,
        "final_gap": final_train_acc - final_test_acc,
    }


def plot_results(summary, plots_dir):
    """Create accuracy and gap plots."""
    rates = [s["dropout_rate"] for s in summary]
    mean_acc = [s["mean_test_acc"] for s in summary]
    std_acc = [s["std_test_acc"] for s in summary]
    mean_gap = [s["mean_gap"] for s in summary]
    std_gap = [s["std_gap"] for s in summary]

    # --- Plot 1: Test Accuracy vs Dropout Rate ---
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(rates, mean_acc, yerr=std_acc, fmt="o-", capsize=4, linewidth=2,
                markersize=6, color="steelblue", label="Mean test accuracy")

    # Mark phi-optimal
    ax.axvline(x=INV_PHI2, color="red", linestyle="--", linewidth=1.5, alpha=0.8,
               label=f"1/phi^2 = {INV_PHI2:.4f}")
    # Mark common default
    ax.axvline(x=0.5, color="gray", linestyle=":", linewidth=1.5, alpha=0.7,
               label="Common default = 0.5")

    # Mark the best
    best_idx = np.argmax(mean_acc)
    ax.scatter([rates[best_idx]], [mean_acc[best_idx]], color="gold", s=200,
               zorder=5, edgecolors="black", linewidth=2, label=f"Best: p={rates[best_idx]}")

    ax.set_xlabel("Dropout Rate (p)", fontsize=13)
    ax.set_ylabel("Test Accuracy (%)", fontsize=13)
    ax.set_title("CIFAR-10 Test Accuracy vs Dropout Rate\n"
                 f"(MLP, {NUM_EPOCHS} epochs, {len(SEEDS)} seeds, {TRAIN_SUBSET} train samples)",
                 fontsize=14)
    ax.legend(loc="best", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(rates)
    ax.set_xticklabels([f"{r:.3f}" if r == 0.382 else f"{r:.2f}" for r in rates],
                       rotation=45, ha="right")
    plt.tight_layout()
    path1 = os.path.join(plots_dir, "dropout_sweep_accuracy.png")
    plt.savefig(path1, dpi=150)
    plt.close()
    print(f"Saved: {path1}")

    # --- Plot 2: Train-Test Gap vs Dropout Rate ---
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(rates, mean_gap, yerr=std_gap, fmt="s-", capsize=4, linewidth=2,
                markersize=6, color="darkorange", label="Mean train-test gap")

    ax.axvline(x=INV_PHI2, color="red", linestyle="--", linewidth=1.5, alpha=0.8,
               label=f"1/phi^2 = {INV_PHI2:.4f}")
    ax.axvline(x=0.5, color="gray", linestyle=":", linewidth=1.5, alpha=0.7,
               label="Common default = 0.5")

    # Mark the smallest positive gap (best generalization)
    pos_gaps = [(i, g) for i, g in enumerate(mean_gap) if g >= 0]
    if pos_gaps:
        best_gap_idx = min(pos_gaps, key=lambda x: x[1])[0]
    else:
        best_gap_idx = np.argmin(np.abs(mean_gap))
    ax.scatter([rates[best_gap_idx]], [mean_gap[best_gap_idx]], color="limegreen", s=200,
               zorder=5, edgecolors="black", linewidth=2,
               label=f"Smallest gap: p={rates[best_gap_idx]}")

    ax.set_xlabel("Dropout Rate (p)", fontsize=13)
    ax.set_ylabel("Train - Test Accuracy Gap (%)", fontsize=13)
    ax.set_title("CIFAR-10 Overfitting Gap vs Dropout Rate\n"
                 f"(lower = better generalization, {len(SEEDS)} seeds)", fontsize=14)
    ax.legend(loc="best", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(rates)
    ax.set_xticklabels([f"{r:.3f}" if r == 0.382 else f"{r:.2f}" for r in rates],
                       rotation=45, ha="right")
    plt.tight_layout()
    path2 = os.path.join(plots_dir, "dropout_sweep_gap.png")
    plt.savefig(path2, dpi=150)
    plt.close()
    print(f"Saved: {path2}")


def analyze_results(summary):
    """Statistical analysis of the sweep results."""
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    rates = [s["dropout_rate"] for s in summary]
    mean_accs = [s["mean_test_acc"] for s in summary]
    std_accs = [s["std_test_acc"] for s in summary]
    mean_gaps = [s["mean_gap"] for s in summary]

    # 1. Best dropout rate by accuracy
    best_idx = np.argmax(mean_accs)
    print(f"\n1. Best dropout rate (highest mean test accuracy):")
    print(f"   p = {rates[best_idx]:.3f}, accuracy = {mean_accs[best_idx]:.2f}% +/- {std_accs[best_idx]:.2f}%")

    # 2. Is 0.382 within 1 std of best?
    phi_idx = rates.index(0.382)
    phi_acc = mean_accs[phi_idx]
    phi_std = std_accs[phi_idx]
    best_acc = mean_accs[best_idx]
    best_std = std_accs[best_idx]

    within_1std = abs(phi_acc - best_acc) <= (phi_std + best_std)
    print(f"\n2. Is p=0.382 within 1 std of best?")
    print(f"   p=0.382: {phi_acc:.2f}% +/- {phi_std:.2f}%")
    print(f"   Best (p={rates[best_idx]:.3f}): {best_acc:.2f}% +/- {best_std:.2f}%")
    print(f"   Difference: {abs(phi_acc - best_acc):.2f}%, Combined std: {phi_std + best_std:.2f}%")
    print(f"   Within 1 std: {'YES' if within_1std else 'NO'}")

    # 3. Smallest train-test gap
    best_gap_idx = np.argmin(np.abs(mean_gaps))
    print(f"\n3. Smallest train-test gap:")
    print(f"   p = {rates[best_gap_idx]:.3f}, gap = {mean_gaps[best_gap_idx]:.2f}%")

    # 4. Compare 0.382 vs 0.5
    p5_idx = rates.index(0.5)
    p5_acc = mean_accs[p5_idx]
    p5_std = std_accs[p5_idx]
    print(f"\n4. Statistical comparison: p=0.382 vs p=0.5")
    print(f"   p=0.382: {phi_acc:.2f}% +/- {phi_std:.2f}%")
    print(f"   p=0.500: {p5_acc:.2f}% +/- {p5_std:.2f}%")
    diff = phi_acc - p5_acc
    se = np.sqrt(phi_std**2 / len(SEEDS) + p5_std**2 / len(SEEDS))
    if se > 0:
        t_stat = diff / se
        print(f"   Difference: {diff:+.2f}%")
        print(f"   t-statistic: {t_stat:.2f} (positive = 0.382 better)")
        print(f"   |t| > 2 suggests significance: {'YES' if abs(t_stat) > 2 else 'NO'}")
    else:
        print(f"   Difference: {diff:+.2f}% (zero variance, no t-test possible)")

    # 5. Rank p=0.382
    sorted_indices = np.argsort(mean_accs)[::-1]
    phi_rank = list(sorted_indices).index(phi_idx) + 1
    print(f"\n5. Rank of p=0.382 among {len(rates)} configs: #{phi_rank}")

    # Overall verdict
    print(f"\n{'=' * 80}")
    print("VERDICT")
    print("=" * 80)
    if phi_rank == 1:
        print("p = 1/phi^2 = 0.382 is THE optimal dropout rate in this experiment.")
    elif within_1std:
        print(f"p = 1/phi^2 = 0.382 is NEAR-OPTIMAL (rank #{phi_rank}, within 1 std of best).")
    else:
        print(f"p = 1/phi^2 = 0.382 is NOT optimal (rank #{phi_rank}, outside 1 std of best).")

    if diff > 0:
        print(f"p = 0.382 outperforms the common default p = 0.5 by {diff:.2f}%.")
    else:
        print(f"p = 0.382 underperforms the common default p = 0.5 by {-diff:.2f}%.")


def main():
    t_global = time.time()
    print("=" * 80)
    print("DROPOUT RATE SWEEP EXPERIMENT")
    print(f"Testing whether dropout ~ 1/phi^2 ~ {INV_PHI2:.4f} is optimal")
    print("=" * 80)
    print(f"Device: {DEVICE}")
    print(f"Architecture: MLP (3072 -> 512 -> 256 -> 10) with BN + Dropout")
    print(f"Dropout rates: {DROPOUT_RATES}")
    print(f"Seeds: {SEEDS}")
    print(f"Epochs per config: {NUM_EPOCHS}")
    print(f"Training: {TRAIN_SUBSET} samples (full-batch), Test: 10000 samples")
    print(f"Total runs: {len(DROPOUT_RATES) * len(SEEDS)}")
    print(flush=True)

    # Load data into tensors (avoids DataLoader overhead)
    print("\nLoading CIFAR-10 into tensors...", flush=True)
    train_x, train_y, test_x, test_y = load_cifar10_tensors()
    print(f"  Train: {train_x.shape}, Test: {test_x.shape}")
    print(flush=True)

    # Quick timing test
    print("Timing one run (30 epochs)...", flush=True)
    torch.manual_seed(0)
    test_model = DropoutMLP(input_dim=3072, dropout_rate=0.5).to(DEVICE)
    test_crit = nn.CrossEntropyLoss()
    test_opt = optim.Adam(test_model.parameters(), lr=LEARNING_RATE)
    t0 = time.time()
    for _ in range(NUM_EPOCHS):
        train_one_epoch(test_model, train_x, train_y, test_crit, test_opt)
        evaluate(test_model, test_x, test_y, test_crit)
    timing_run = time.time() - t0
    est_total = timing_run * len(DROPOUT_RATES) * len(SEEDS)
    print(f"  One run: {timing_run:.1f}s, Estimated total: {est_total/60:.1f} min")
    del test_model, test_crit, test_opt
    print(flush=True)

    # Run all configs
    all_results = []
    total_runs = len(DROPOUT_RATES) * len(SEEDS)
    run_count = 0
    t_start = time.time()

    for dr in DROPOUT_RATES:
        for seed in SEEDS:
            run_count += 1
            sys.stdout.write(f"[{run_count}/{total_runs}] p={dr:.3f} s={seed} ... ")
            sys.stdout.flush()
            t0 = time.time()
            result = run_single_config(dr, seed, train_x, train_y, test_x, test_y)
            elapsed = time.time() - t0
            print(f"acc={result['best_test_acc']:.2f}% gap={result['train_test_gap']:.1f}% "
                  f"final_gap={result['final_gap']:.1f}% {elapsed:.0f}s", flush=True)
            all_results.append(result)

        # Print ETA after each dropout rate
        elapsed_total = time.time() - t_start
        done_frac = run_count / total_runs
        if done_frac > 0:
            eta = elapsed_total / done_frac - elapsed_total
            print(f"  --- {run_count}/{total_runs} done, ETA: {eta/60:.1f} min ---", flush=True)

    total_time = time.time() - t_start
    print(f"\nTotal training time: {total_time:.1f}s ({total_time/60:.1f} min)", flush=True)

    # Save raw results
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Raw results saved to: {RESULTS_FILE}")

    # Aggregate by dropout rate
    summary = []
    for dr in DROPOUT_RATES:
        runs = [r for r in all_results if r["dropout_rate"] == dr]
        accs = [r["best_test_acc"] for r in runs]
        losses = [r["best_test_loss"] for r in runs]
        gaps = [r["train_test_gap"] for r in runs]
        final_gaps = [r["final_gap"] for r in runs]
        summary.append({
            "dropout_rate": dr,
            "mean_test_acc": np.mean(accs),
            "std_test_acc": np.std(accs),
            "mean_test_loss": np.mean(losses),
            "std_test_loss": np.std(losses),
            "mean_gap": np.mean(gaps),
            "std_gap": np.std(gaps),
            "mean_final_gap": np.mean(final_gaps),
        })

    # Print summary table
    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Dropout':>10s} | {'Test Acc (%)':>14s} | {'Test Loss':>14s} | {'Train-Test Gap (%)':>18s} | {'Final Gap':>10s}")
    print("-" * 80)
    for s in summary:
        marker = " <-- 1/phi^2" if s["dropout_rate"] == 0.382 else ""
        marker = " <-- default" if s["dropout_rate"] == 0.5 else marker
        print(f"{s['dropout_rate']:>10.3f} | "
              f"{s['mean_test_acc']:>6.2f} +/- {s['std_test_acc']:<5.2f} | "
              f"{s['mean_test_loss']:>6.4f} +/- {s['std_test_loss']:<6.4f} | "
              f"{s['mean_gap']:>6.2f} +/- {s['std_gap']:<5.2f} | "
              f"{s['mean_final_gap']:>6.2f}{marker}")

    # Plot results
    print("\nGenerating plots...", flush=True)
    plot_results(summary, PLOTS_DIR)

    # Analysis
    analyze_results(summary)

    print(f"\nTotal wall time: {(time.time() - t_global)/60:.1f} min")


if __name__ == "__main__":
    main()
