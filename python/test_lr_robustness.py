#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Rate Robustness Test

Tests whether OuroborosExact works across a wider range of learning rates
than other activation functions.

Hypothesis: Stable gradient norms -> works at more learning rates -> easier to tune

Setup:
- Dataset: FashionMNIST
- Network: 10-layer MLP, width 128, no BatchNorm
- Each activation uses its own critical init scale
- Optimizer: Adam
- Epochs: 3 (enough to see if it's training)

Author: Claude (Anthropic)
Date: 2026-02-08
"""

import sys
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def log(msg):
    """Print with flush for real-time output."""
    print(msg, flush=True)

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
THREE_MINUS_PHI = 3 - PHI   # 1.3820

# Critical initialization scales for each activation
# Computed as sigma_crit = 1 / sqrt(E[f'(x)^2])
CRITICAL_SCALES = {
    'OuroborosExact': 1.3820,  # (3-phi), derived analytically
    'Swish': 1.6233,           # Computed numerically
    'Mish': 1.4448,            # Computed numerically
    'ReLU': 1.4142,            # sqrt(2), He initialization
    'GELU': 1.4811,            # Computed numerically
}

# Learning rates to test (4 orders of magnitude)
LEARNING_RATES = [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1]

# Network configuration - reduced for faster CPU execution
DEPTH = 10
WIDTH = 128
EPOCHS = 3
BATCH_SIZE = 256

# ============================================================================
# ACTIVATION FUNCTIONS
# ============================================================================

# Optimal lambda for OuroborosExact (computed in ouroboros_exact.py)
OUROBOROS_LAMBDA = 0.23568240832306636


class OuroborosExact(nn.Module):
    """
    Exact (3-phi) critical scale activation.
    f(x) = x * (lambda + (1-lambda) * sigmoid(x))
    """
    def __init__(self):
        super().__init__()
        self.lam = OUROBOROS_LAMBDA

    def forward(self, x):
        s = torch.sigmoid(x)
        gate = self.lam + (1 - self.lam) * s
        return x * gate


class Swish(nn.Module):
    """Swish activation: f(x) = x * sigmoid(x)"""
    def forward(self, x):
        return x * torch.sigmoid(x)


class Mish(nn.Module):
    """Mish activation: f(x) = x * tanh(softplus(x))"""
    def forward(self, x):
        return x * torch.tanh(nn.functional.softplus(x))


# ============================================================================
# NETWORK ARCHITECTURE
# ============================================================================

class DeepMLP(nn.Module):
    """
    Deep MLP with configurable activation and critical initialization.
    No BatchNorm - tests raw activation stability.
    """
    def __init__(self, input_dim, hidden_dim, output_dim, depth,
                 activation_class, critical_scale):
        super().__init__()

        self.layers = nn.ModuleList()
        self.activations = nn.ModuleList()

        # Input layer
        self.layers.append(nn.Linear(input_dim, hidden_dim))
        self.activations.append(activation_class())

        # Hidden layers
        for _ in range(depth - 2):
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))
            self.activations.append(activation_class())

        # Output layer
        self.layers.append(nn.Linear(hidden_dim, output_dim))

        # Apply critical initialization
        self._init_weights(critical_scale)

    def _init_weights(self, critical_scale):
        """Initialize weights at criticality for the given activation."""
        for layer in self.layers:
            fan_in = layer.weight.shape[1]
            std = critical_scale / np.sqrt(fan_in)
            nn.init.normal_(layer.weight, mean=0.0, std=std)
            nn.init.zeros_(layer.bias)

    def forward(self, x):
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x)
            x = self.activations[i](x)
        x = self.layers[-1](x)
        return x


# ============================================================================
# DATA LOADING
# ============================================================================

def load_fashionmnist():
    """Load FashionMNIST dataset."""
    try:
        from torchvision import datasets, transforms

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.2860,), (0.3530,))  # FashionMNIST stats
        ])

        train_dataset = datasets.FashionMNIST(
            './data', train=True, download=True, transform=transform
        )
        test_dataset = datasets.FashionMNIST(
            './data', train=False, download=True, transform=transform
        )

        train_loader = torch.utils.data.DataLoader(
            train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0
        )
        test_loader = torch.utils.data.DataLoader(
            test_dataset, batch_size=1000, shuffle=False, num_workers=0
        )

        return train_loader, test_loader

    except ImportError:
        raise ImportError("torchvision required. Install with: pip install torchvision")


# ============================================================================
# TRAINING AND EVALUATION
# ============================================================================

def train_and_evaluate(activation_name, activation_class, critical_scale,
                       learning_rate, train_loader, test_loader, device):
    """
    Train network for EPOCHS and return final test accuracy.
    Returns (accuracy, diverged, learned) tuple.
    """
    torch.manual_seed(42)
    np.random.seed(42)

    # Create model
    model = DeepMLP(
        input_dim=784,
        hidden_dim=WIDTH,
        output_dim=10,
        depth=DEPTH,
        activation_class=activation_class,
        critical_scale=critical_scale
    ).to(device)

    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    diverged = False
    final_accuracy = 0.0

    for epoch in range(EPOCHS):
        # Training
        model.train()
        for data, target in train_loader:
            data = data.to(device).view(data.size(0), -1)
            target = target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)

            # Check for divergence
            if torch.isnan(loss) or torch.isinf(loss) or loss.item() > 10:
                diverged = True
                break

            loss.backward()
            optimizer.step()

        if diverged:
            break

    # Final evaluation
    if not diverged:
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for data, target in test_loader:
                data = data.to(device).view(data.size(0), -1)
                target = target.to(device)
                output = model(data)
                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)
        final_accuracy = 100.0 * correct / total

    learned = final_accuracy > 10.0  # Better than random (10 classes)

    return final_accuracy, diverged, learned


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def run_experiment():
    """Run the full learning rate robustness experiment."""
    log("=" * 70)
    log("LEARNING RATE ROBUSTNESS TEST")
    log("=" * 70)
    log("")
    log(f"Configuration:")
    log(f"  Dataset: FashionMNIST")
    log(f"  Network: {DEPTH}-layer MLP, width {WIDTH}, no BatchNorm")
    log(f"  Epochs: {EPOCHS}")
    log(f"  Optimizer: Adam")
    log(f"  Learning rates: {len(LEARNING_RATES)} values from {LEARNING_RATES[0]:.0e} to {LEARNING_RATES[-1]:.0e}")
    log("")

    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    log(f"Device: {device}")
    log("")

    log("Loading FashionMNIST...")
    train_loader, test_loader = load_fashionmnist()
    log("Done.")
    log("")

    # Activation classes
    activations = {
        'OuroborosExact': OuroborosExact,
        'Swish': Swish,
        'Mish': Mish,
        'ReLU': nn.ReLU,
        'GELU': nn.GELU,
    }

    # Store results
    results = {name: {} for name in activations}

    # Run experiments
    for act_name in activations:
        log(f"Testing {act_name} (scale={CRITICAL_SCALES[act_name]:.4f})...")

        for lr in LEARNING_RATES:
            acc, diverged, learned = train_and_evaluate(
                activation_name=act_name,
                activation_class=activations[act_name],
                critical_scale=CRITICAL_SCALES[act_name],
                learning_rate=lr,
                train_loader=train_loader,
                test_loader=test_loader,
                device=device
            )

            results[act_name][lr] = {
                'accuracy': acc,
                'diverged': diverged,
                'learned': learned
            }

            status = "FAIL" if diverged else f"{acc:.1f}%"
            log(f"  LR={lr:.0e}: {status}")

        log("")

    return results


def print_results_table(results):
    """Print formatted results table."""
    log("=" * 70)
    log("RESULTS TABLE")
    log("=" * 70)
    log("")

    # Header
    header = "                    "
    for lr in LEARNING_RATES:
        header += f" {lr:.0e}"
    log(header)

    # Data rows
    for act_name in results:
        row = f"{act_name:18s}"
        for lr in LEARNING_RATES:
            r = results[act_name][lr]
            if r['diverged']:
                row += "   FAIL"
            else:
                row += f"  {r['accuracy']:5.1f}"
        log(row)

    log("")


def analyze_working_ranges(results):
    """Analyze and print working LR ranges for each activation."""
    log("=" * 70)
    log("WORKING LR RANGE ANALYSIS (accuracy > 50%)")
    log("=" * 70)
    log("")

    ranges = {}

    for act_name in results:
        working_lrs = []
        for lr in LEARNING_RATES:
            r = results[act_name][lr]
            if not r['diverged'] and r['accuracy'] > 50.0:
                working_lrs.append(lr)

        if working_lrs:
            min_lr = min(working_lrs)
            max_lr = max(working_lrs)
            # Count orders of magnitude
            orders = np.log10(max_lr / min_lr)
            ranges[act_name] = {
                'min': min_lr,
                'max': max_lr,
                'orders': orders,
                'count': len(working_lrs)
            }
            log(f"  {act_name:18s}: {min_lr:.0e} to {max_lr:.0e} ({orders:.1f} orders of magnitude)")
        else:
            ranges[act_name] = {'orders': 0, 'count': 0}
            log(f"  {act_name:18s}: No working LRs found")

    log("")

    # Find winner
    best_name = max(ranges, key=lambda x: ranges[x]['orders'])
    log(f"WINNER: {best_name} (widest working range)")
    log("")

    return ranges


def analyze_peak_performance(results):
    """Find peak accuracy for each activation."""
    log("=" * 70)
    log("PEAK PERFORMANCE")
    log("=" * 70)
    log("")

    for act_name in results:
        best_acc = 0.0
        best_lr = None
        for lr in LEARNING_RATES:
            r = results[act_name][lr]
            if not r['diverged'] and r['accuracy'] > best_acc:
                best_acc = r['accuracy']
                best_lr = lr

        if best_lr:
            log(f"  {act_name:18s}: {best_acc:.1f}% at LR={best_lr:.0e}")
        else:
            log(f"  {act_name:18s}: No successful runs")

    log("")


def main():
    """Main entry point."""
    results = run_experiment()
    print_results_table(results)
    analyze_working_ranges(results)
    analyze_peak_performance(results)

    log("=" * 70)
    log("EXPERIMENT COMPLETE")
    log("=" * 70)


if __name__ == '__main__':
    main()
