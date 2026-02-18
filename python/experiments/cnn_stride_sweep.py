"""
CNN Stride Sweep: Testing phi-Optimal Overlap
==============================================
Tests whether phi-optimal stride (giving ~38.2% overlap between
convolution windows) outperforms other stride values in a CNN.

Theory: The self-referential optimization framework predicts that
overlap = 1/phi^2 ~= 0.382 is optimal because it balances information
extraction (more overlap = more redundant features) against
computational/statistical efficiency (less overlap = fewer parameters
to learn from the same data).

Experiment design:
- Dataset: CIFAR-10 (10 classes, 32x32 color images)
- Multiple kernel sizes (3, 5, 7) with all valid integer strides
- overlap = 1 - stride/kernel_size
- 3 random seeds per configuration for error bars
- 10 epochs per run on GPU, 5 on CPU (enough to see trends)
- Training subset (10k) on CPU for feasibility, full 50k on GPU
- AdaptiveAvgPool2d normalizes spatial dimensions across configs

Independent variable: overlap fraction (1 - stride/kernel_size)
Dependent variable: best test accuracy across epochs

Author: Claude (CNN stride experiment from self-referential optimization)
"""

import sys
import io
import os
import time
import json

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

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
import torchvision
import torchvision.transforms as transforms
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ==============================================================================
# Constants
# ==============================================================================
PHI = (1 + np.sqrt(5)) / 2          # Golden ratio ~1.618
INV_PHI = 1.0 / PHI                 # ~0.618
INV_PHI_SQ = 1.0 / (PHI ** 2)      # ~0.382  (the predicted optimal overlap)

KERNEL_SIZES = [3, 5, 7]
BATCH_SIZE = 128
LEARNING_RATE = 1e-3
SEEDS = [42, 137, 256]

# Adapt to hardware
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device("cuda" if USE_CUDA else "cpu")
NUM_EPOCHS = 10 if USE_CUDA else 3
TRAIN_SUBSET = None if USE_CUDA else 5000   # Use 5k subset on CPU for speed
TEST_SUBSET = None if USE_CUDA else 2000    # Use 2k test subset on CPU
NUM_WORKERS = 2 if USE_CUDA else 0          # Workers=0 avoids Windows mp overhead on CPU

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
PLOT_DIR = os.path.join(SCRIPT_DIR, "plots")
PLOT_PATH = os.path.join(PLOT_DIR, "cnn_stride_sweep.png")
RESULTS_PATH = os.path.join(SCRIPT_DIR, "cnn_stride_sweep_results.json")

# ==============================================================================
# Model
# ==============================================================================
class StrideCNN(nn.Module):
    """Simple CNN where kernel_size and stride are controlled parameters."""

    def __init__(self, kernel_size, stride):
        super().__init__()
        pad = kernel_size // 2

        ch1 = 32 if USE_CUDA else 16
        ch2 = 64 if USE_CUDA else 32
        fc_hidden = 256 if USE_CUDA else 128

        self.features = nn.Sequential(
            nn.Conv2d(3, ch1, kernel_size=kernel_size, stride=stride, padding=pad),
            nn.BatchNorm2d(ch1),
            nn.ReLU(inplace=True),
            nn.Conv2d(ch1, ch2, kernel_size=kernel_size, stride=stride, padding=pad),
            nn.BatchNorm2d(ch2),
            nn.ReLU(inplace=True),
        )
        self.pool = nn.AdaptiveAvgPool2d(4)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(ch2 * 4 * 4, fc_hidden),
            nn.ReLU(inplace=True),
            nn.Linear(fc_hidden, 10),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        x = self.classifier(x)
        return x


# ==============================================================================
# Training / Evaluation
# ==============================================================================
def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * inputs.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(targets).sum().item()
        total += targets.size(0)
    return total_loss / total, correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, targets in loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            total_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(targets).sum().item()
            total += targets.size(0)
    return total_loss / total, correct / total


def run_single_config(kernel_size, stride, seed, train_loader, test_loader, device):
    """Train one model configuration and return best test accuracy."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)

    model = StrideCNN(kernel_size, stride).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_test_acc = 0.0
    for epoch in range(NUM_EPOCHS):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        test_loss, test_acc = evaluate(model, test_loader, criterion, device)
        if test_acc > best_test_acc:
            best_test_acc = test_acc

    return best_test_acc


# ==============================================================================
# Generate configurations
# ==============================================================================
def get_configs():
    """Generate (kernel_size, stride, overlap) configurations."""
    configs = []
    for k in KERNEL_SIZES:
        for s in range(1, k + 1):
            overlap = 1.0 - s / k
            configs.append((k, s, overlap))
    return configs


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 70)
    print("CNN Stride Sweep: Testing phi-Optimal Overlap")
    print("=" * 70)
    print(f"phi = {PHI:.6f}")
    print(f"1/phi = {INV_PHI:.6f}")
    print(f"1/phi^2 = {INV_PHI_SQ:.6f}  (predicted optimal overlap)")
    print()

    # Device
    print(f"Device: {DEVICE}")
    if DEVICE.type == "cuda":
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print(f"Epochs per run: {NUM_EPOCHS}")
    if TRAIN_SUBSET:
        print(f"Training subset: {TRAIN_SUBSET} images (CPU mode)")
    print()

    # Data
    print("Loading CIFAR-10...")
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])

    train_set = torchvision.datasets.CIFAR10(
        root=DATA_DIR, train=True, download=True, transform=transform_train
    )
    test_set = torchvision.datasets.CIFAR10(
        root=DATA_DIR, train=False, download=True, transform=transform_test
    )

    # Use subsets on CPU for feasibility
    if TRAIN_SUBSET and TRAIN_SUBSET < len(train_set):
        rng = np.random.RandomState(0)
        indices = rng.choice(len(train_set), TRAIN_SUBSET, replace=False)
        train_set = Subset(train_set, indices)
    if TEST_SUBSET and TEST_SUBSET < len(test_set):
        rng = np.random.RandomState(1)
        indices = rng.choice(len(test_set), TEST_SUBSET, replace=False)
        test_set = Subset(test_set, indices)

    train_loader = DataLoader(
        train_set, batch_size=BATCH_SIZE, shuffle=True,
        num_workers=NUM_WORKERS, pin_memory=(DEVICE.type == "cuda"),
    )
    test_loader = DataLoader(
        test_set, batch_size=BATCH_SIZE, shuffle=False,
        num_workers=NUM_WORKERS, pin_memory=(DEVICE.type == "cuda"),
    )
    print(f"  Train: {len(train_set)} images")
    print(f"  Test:  {len(test_set)} images")
    print()

    # Configurations
    configs = get_configs()
    print(f"Configurations to test: {len(configs)}")
    print(f"Seeds per config: {len(SEEDS)}")
    print(f"Total training runs: {len(configs) * len(SEEDS)}")
    print()

    print("-" * 70)
    print(f"{'K':>3} {'S':>3} {'Overlap':>8}  {'Seed':>5}  {'BestAcc':>8}  {'Time':>7}")
    print("-" * 70)

    # Results storage
    results = []
    total_start = time.time()
    run_count = 0
    total_runs = len(configs) * len(SEEDS)

    for kernel_size, stride, overlap in configs:
        seed_accs = []
        for seed in SEEDS:
            run_count += 1
            t0 = time.time()
            best_acc = run_single_config(
                kernel_size, stride, seed, train_loader, test_loader, DEVICE
            )
            elapsed = time.time() - t0
            seed_accs.append(best_acc)
            print(f"{kernel_size:3d} {stride:3d} {overlap:8.3f}  {seed:5d}  {best_acc:8.4f}  {elapsed:6.1f}s  [{run_count}/{total_runs}]")
            sys.stdout.flush()

        mean_acc = np.mean(seed_accs)
        std_acc = np.std(seed_accs)
        results.append({
            "kernel_size": kernel_size,
            "stride": stride,
            "overlap": round(overlap, 6),
            "mean_acc": round(float(mean_acc), 6),
            "std_acc": round(float(std_acc), 6),
            "accs": [round(a, 6) for a in seed_accs],
        })
        print(f"  --> K={kernel_size} S={stride} overlap={overlap:.3f}: "
              f"mean={mean_acc:.4f} +/- {std_acc:.4f}")
        print()
        sys.stdout.flush()

    total_time = time.time() - total_start
    print(f"\nTotal time: {total_time:.1f}s ({total_time/60:.1f} min)")

    # Save raw results
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {RESULTS_PATH}")

    # ===========================================================================
    # Summary table
    # ===========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'K':>3} {'S':>3} {'Overlap':>8} {'MeanAcc':>9} {'StdAcc':>8} {'Note':>12}")
    print("-" * 55)

    best_result = max(results, key=lambda r: r["mean_acc"])

    for r in sorted(results, key=lambda r: r["overlap"]):
        note = ""
        if abs(r["overlap"] - INV_PHI_SQ) < 0.05:
            note = "<-- 1/phi^2"
        if r is best_result:
            note += " *BEST*"
        print(f"{r['kernel_size']:3d} {r['stride']:3d} {r['overlap']:8.3f} "
              f"{r['mean_acc']:9.4f} {r['std_acc']:8.4f} {note}")

    # ===========================================================================
    # Analysis: group by overlap (collapse across kernel sizes)
    # ===========================================================================
    overlap_to_accs = {}
    for r in results:
        o = r["overlap"]
        overlap_to_accs.setdefault(o, []).append(r["mean_acc"])

    unique_overlaps = sorted(overlap_to_accs.keys())
    overlap_means = [np.mean(overlap_to_accs[o]) for o in unique_overlaps]
    overlap_stds = [np.std(overlap_to_accs[o]) if len(overlap_to_accs[o]) > 1 else 0.0
                    for o in unique_overlaps]

    phi_idx = np.argmin([abs(o - INV_PHI_SQ) for o in unique_overlaps])
    phi_overlap = unique_overlaps[phi_idx]
    phi_acc = overlap_means[phi_idx]

    print(f"\nOverlap closest to 1/phi^2 ({INV_PHI_SQ:.3f}): {phi_overlap:.3f}")
    print(f"  Mean accuracy at that overlap: {phi_acc:.4f}")
    print(f"  Best overall overlap: {unique_overlaps[np.argmax(overlap_means)]:.3f} "
          f"(acc={max(overlap_means):.4f})")

    # ===========================================================================
    # Plot
    # ===========================================================================
    os.makedirs(PLOT_DIR, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Left panel: accuracy vs overlap, colored by kernel size ---
    ax1 = axes[0]
    colors = {3: "#2196F3", 5: "#4CAF50", 7: "#FF9800"}
    markers = {3: "o", 5: "s", 7: "D"}

    for r in results:
        k = r["kernel_size"]
        ax1.errorbar(
            r["overlap"], r["mean_acc"], yerr=r["std_acc"],
            fmt=markers[k], color=colors[k], markersize=8, capsize=3,
            alpha=0.8, label=f"K={k}" if r["stride"] == 1 else "",
        )

    ax1.axvspan(INV_PHI_SQ - 0.03, INV_PHI_SQ + 0.03,
                alpha=0.15, color="red", label=f"1/phi^2 = {INV_PHI_SQ:.3f}")
    ax1.axvline(INV_PHI_SQ, color="red", linestyle="--", alpha=0.6, linewidth=1.5)

    ax1.set_xlabel("Overlap Fraction (1 - stride/kernel)", fontsize=12)
    ax1.set_ylabel("Best Test Accuracy", fontsize=12)
    ax1.set_title("CNN Accuracy vs. Convolution Overlap", fontsize=13)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(-0.05, 1.0)

    # --- Right panel: collapsed across kernel sizes ---
    ax2 = axes[1]
    ax2.errorbar(
        unique_overlaps, overlap_means,
        yerr=overlap_stds,
        fmt="o-", color="#333333", markersize=7, capsize=4, linewidth=1.5,
    )

    ax2.axvspan(INV_PHI_SQ - 0.03, INV_PHI_SQ + 0.03,
                alpha=0.15, color="red")
    ax2.axvline(INV_PHI_SQ, color="red", linestyle="--", alpha=0.6, linewidth=1.5,
                label=f"1/phi^2 = {INV_PHI_SQ:.3f}")

    best_overlap_idx = np.argmax(overlap_means)
    ax2.plot(unique_overlaps[best_overlap_idx], overlap_means[best_overlap_idx],
             "*", color="gold", markersize=20, markeredgecolor="black",
             markeredgewidth=1, zorder=5, label=f"Peak: overlap={unique_overlaps[best_overlap_idx]:.3f}")

    ax2.set_xlabel("Overlap Fraction", fontsize=12)
    ax2.set_ylabel("Mean Accuracy (across kernel sizes)", fontsize=12)
    ax2.set_title("Collapsed Across Kernel Sizes", fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-0.05, 1.0)

    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {PLOT_PATH}")
    plt.close()

    # ===========================================================================
    # Per-kernel-size analysis
    # ===========================================================================
    print("\n" + "=" * 70)
    print("PER-KERNEL-SIZE ANALYSIS")
    print("=" * 70)
    for k in KERNEL_SIZES:
        k_results = [r for r in results if r["kernel_size"] == k]
        best_k = max(k_results, key=lambda r: r["mean_acc"])
        phi_candidates = [r for r in k_results if abs(r["overlap"] - INV_PHI_SQ) < 0.15]
        print(f"\nKernel size {k}:")
        print(f"  Best stride: {best_k['stride']} (overlap={best_k['overlap']:.3f}, "
              f"acc={best_k['mean_acc']:.4f})")
        if phi_candidates:
            closest = min(phi_candidates, key=lambda r: abs(r["overlap"] - INV_PHI_SQ))
            print(f"  Closest to phi-optimal: stride={closest['stride']} "
                  f"(overlap={closest['overlap']:.3f}, acc={closest['mean_acc']:.4f})")
            delta = closest["mean_acc"] - best_k["mean_acc"]
            print(f"  Delta from best: {delta:+.4f}")

    # Final verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    best_overall_acc = best_result["mean_acc"]
    phi_results = [r for r in results if abs(r["overlap"] - INV_PHI_SQ) < 0.1]
    if phi_results:
        best_phi = max(phi_results, key=lambda r: r["mean_acc"])
        gap = best_overall_acc - best_phi["mean_acc"]
        print(f"Best overall: overlap={best_result['overlap']:.3f}, acc={best_overall_acc:.4f}")
        print(f"Best near phi-optimal (overlap~0.382): overlap={best_phi['overlap']:.3f}, "
              f"acc={best_phi['mean_acc']:.4f}")
        print(f"Gap: {gap:.4f} ({gap/best_overall_acc*100:.2f}%)")
        if gap < 0.005:
            print("RESULT: phi-optimal overlap is essentially tied for best!")
        elif gap < 0.01:
            print("RESULT: phi-optimal overlap is competitive (within 1% of best)")
        elif gap < 0.02:
            print("RESULT: phi-optimal overlap is reasonable but not optimal")
        else:
            print("RESULT: phi-optimal overlap does NOT appear special for CNN strides")
    else:
        print("No configurations near phi-optimal overlap were tested.")

    print("\nDone!")


if __name__ == "__main__":
    main()
