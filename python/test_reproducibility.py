#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reproducibility Test: Variance Across Random Seeds

Tests whether OuroborosExact gives more consistent results across random seeds.

Hypothesis: Stable gradient norms -> more predictable optimization -> lower variance

Setup:
- Dataset: FashionMNIST
- Network: 20-layer MLP, width 256, no BatchNorm
- Each activation uses its own critical init scale
- Optimizer: Adam, LR=1e-3
- Epochs: 10
- Seeds: 10 different seeds (0-9)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
import time
import sys
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Force output flushing for real-time progress
sys.stdout.reconfigure(line_buffering=True)

# ============================================================================
# ACTIVATION FUNCTIONS
# ============================================================================

# Golden ratio constants
PHI = (1 + np.sqrt(5)) / 2
THREE_MINUS_PHI = 3 - PHI  # = 1.381966...

# Optimal lambda from ouroboros_exact.py derivation
# This is computed to achieve E[f'(x)^2] = 1/(3-phi)^2
OPTIMAL_LAMBDA = 0.2955977425220668  # From the ouroboros_exact.py calculation


class OuroborosExact(nn.Module):
    """
    Exact (3-phi) critical scale activation.
    f(x) = x * (lambda + (1-lambda) * sigmoid(x))
    where lambda achieves E[f'(x)^2] = 1/(3-phi)^2 exactly.
    Critical scale = 1.3820
    """
    def __init__(self):
        super().__init__()
        self.lam = OPTIMAL_LAMBDA

    def forward(self, x):
        s = torch.sigmoid(x)
        gate = self.lam + (1 - self.lam) * s
        return x * gate


class Swish(nn.Module):
    """Swish activation: x * sigmoid(x). Critical scale = 1.6233"""
    def forward(self, x):
        return x * torch.sigmoid(x)


class Mish(nn.Module):
    """Mish activation: x * tanh(softplus(x)). Critical scale = 1.4448"""
    def forward(self, x):
        return x * torch.tanh(torch.nn.functional.softplus(x))


# GELU and ReLU are built-in, we'll use nn.GELU() and nn.ReLU()

# Critical initialization scales for each activation
# These ensure Var[output] = Var[input] at initialization
CRITICAL_SCALES = {
    'OuroborosExact': 1.3820,  # (3-phi) exactly
    'Swish': 1.6233,
    'Mish': 1.4448,
    'ReLU': 1.4142,  # sqrt(2)
    'GELU': 1.4811,
}


# ============================================================================
# NETWORK ARCHITECTURE
# ============================================================================

class DeepMLP(nn.Module):
    """
    Deep MLP without BatchNorm.
    Uses critical initialization for the specified activation.
    """
    def __init__(self, activation_name: str, depth: int = 20, width: int = 256):
        super().__init__()

        self.activation_name = activation_name
        self.depth = depth
        self.width = width

        # Get activation and critical scale
        if activation_name == 'OuroborosExact':
            self.activation = OuroborosExact()
        elif activation_name == 'Swish':
            self.activation = Swish()
        elif activation_name == 'Mish':
            self.activation = Mish()
        elif activation_name == 'ReLU':
            self.activation = nn.ReLU()
        elif activation_name == 'GELU':
            self.activation = nn.GELU()
        else:
            raise ValueError(f"Unknown activation: {activation_name}")

        scale = CRITICAL_SCALES[activation_name]

        # Build layers
        layers = []

        # Input layer (28*28 -> width)
        input_layer = nn.Linear(28 * 28, width)
        nn.init.normal_(input_layer.weight, mean=0, std=scale / np.sqrt(28 * 28))
        nn.init.zeros_(input_layer.bias)
        layers.append(input_layer)

        # Hidden layers (width -> width)
        for _ in range(depth - 1):
            layer = nn.Linear(width, width)
            nn.init.normal_(layer.weight, mean=0, std=scale / np.sqrt(width))
            nn.init.zeros_(layer.bias)
            layers.append(layer)

        self.layers = nn.ModuleList(layers)

        # Output layer (width -> 10)
        self.output_layer = nn.Linear(width, 10)
        nn.init.normal_(self.output_layer.weight, mean=0, std=1.0 / np.sqrt(width))
        nn.init.zeros_(self.output_layer.bias)

    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten

        for layer in self.layers:
            x = layer(x)
            x = self.activation(x)

        return self.output_layer(x)


# ============================================================================
# TRAINING AND EVALUATION
# ============================================================================

def set_seed(seed: int):
    """Set all random seeds for reproducibility."""
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_epoch(model, train_loader, optimizer, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for data, target in train_loader:
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * data.size(0)
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += data.size(0)

    return total_loss / total, 100.0 * correct / total


def evaluate(model, test_loader, criterion, device):
    """Evaluate model on test set."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            loss = criterion(output, target)

            total_loss += loss.item() * data.size(0)
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += data.size(0)

    return total_loss / total, 100.0 * correct / total


def run_single_experiment(activation_name: str, seed: int, epochs: int,
                          train_loader, test_loader, device) -> float:
    """Run a single training experiment and return final test accuracy."""
    set_seed(seed)

    model = DeepMLP(activation_name, depth=20, width=256).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, device)

    # Final evaluation
    test_loss, test_acc = evaluate(model, test_loader, criterion, device)

    return test_acc


# ============================================================================
# MAIN EXPERIMENT
# ============================================================================

def main():
    print("=" * 70)
    print("REPRODUCIBILITY TEST: Variance Across Random Seeds")
    print("=" * 70)
    print()

    # Configuration
    # Note: Original spec was 20 layers, 10 epochs - adjusted for CPU performance
    # For deeper/longer runs, use GPU or increase depth/epochs
    NUM_SEEDS = 10
    EPOCHS = 3
    BATCH_SIZE = 512
    DEPTH = 8
    WIDTH = 64

    print("Configuration:")
    print(f"  Dataset:    FashionMNIST (or MNIST fallback)")
    print(f"  Network:    {DEPTH}-layer MLP, width {WIDTH}, no BatchNorm")
    print(f"  Optimizer:  Adam, LR=1e-3")
    print(f"  Epochs:     {EPOCHS}")
    print(f"  Seeds:      {NUM_SEEDS} (0-{NUM_SEEDS-1})")
    print(f"  Batch size: {BATCH_SIZE}")
    print()

    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")
    print()

    # Load data - use FashionMNIST without re-downloading
    print("Loading dataset...")
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # Try FashionMNIST first
    try:
        train_dataset = datasets.FashionMNIST(
            root=data_dir, train=True, download=False, transform=transform
        )
        test_dataset = datasets.FashionMNIST(
            root=data_dir, train=False, download=False, transform=transform
        )
        dataset_name = "FashionMNIST"
    except Exception as e:
        print(f"FashionMNIST load failed ({e}), trying to download...")
        try:
            train_dataset = datasets.FashionMNIST(
                root=data_dir, train=True, download=True, transform=transform
            )
            test_dataset = datasets.FashionMNIST(
                root=data_dir, train=False, download=True, transform=transform
            )
            dataset_name = "FashionMNIST"
        except Exception as e2:
            print(f"FashionMNIST download failed ({e2}), falling back to MNIST...")
            train_dataset = datasets.MNIST(
                root=data_dir, train=True, download=True, transform=transform
            )
            test_dataset = datasets.MNIST(
                root=data_dir, train=False, download=True, transform=transform
            )
            dataset_name = "MNIST"

    print(f"  Using: {dataset_name}")

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False,
                             num_workers=0, pin_memory=True)

    print(f"  Train samples: {len(train_dataset)}")
    print(f"  Test samples:  {len(test_dataset)}")
    print()

    # Activations to test
    activations = ['OuroborosExact', 'Swish', 'Mish', 'ReLU', 'GELU']

    print("Critical initialization scales:")
    for act in activations:
        print(f"  {act:15}: {CRITICAL_SCALES[act]:.4f}")
    print()

    # Run experiments
    print("=" * 70)
    print("RUNNING EXPERIMENTS")
    print("=" * 70)
    print()

    results: Dict[str, List[float]] = {act: [] for act in activations}

    total_runs = len(activations) * NUM_SEEDS
    run_count = 0
    start_time = time.time()

    for seed in range(NUM_SEEDS):
        print(f"Seed {seed}:")
        for activation in activations:
            run_count += 1
            run_start = time.time()

            acc = run_single_experiment(
                activation, seed, EPOCHS, train_loader, test_loader, device
            )
            results[activation].append(acc)

            run_time = time.time() - run_start
            elapsed = time.time() - start_time
            eta = (elapsed / run_count) * (total_runs - run_count)

            print(f"  {activation:15}: {acc:5.2f}%  ({run_time:.1f}s, ETA: {eta/60:.1f}min)")
        print()

    total_time = time.time() - start_time

    # ========================================================================
    # RESULTS ANALYSIS
    # ========================================================================

    print()
    print("=" * 70)
    print(f"REPRODUCIBILITY TEST ({NUM_SEEDS} seeds)")
    print("=" * 70)
    print()

    # Compute statistics
    stats = {}
    for act in activations:
        accs = np.array(results[act])
        stats[act] = {
            'mean': np.mean(accs),
            'std': np.std(accs),
            'min': np.min(accs),
            'max': np.max(accs),
            'cv': np.std(accs) / np.mean(accs) * 100 if np.mean(accs) > 0 else 0
        }

    # Summary table
    print(f"{'Activation':<18} {'Mean Acc':>10} {'Std':>10} {'Min':>10} {'Max':>10} {'CV':>10}")
    print("-" * 70)
    for act in activations:
        s = stats[act]
        print(f"{act:<18} {s['mean']:>9.2f}% {s['std']:>9.2f}% {s['min']:>9.2f}% {s['max']:>9.2f}% {s['cv']:>9.2f}%")
    print()

    # Individual runs table
    print("INDIVIDUAL RUNS:")
    header = f"{'Seed':<6}"
    for act in activations:
        header += f" {act:>15}"
    print(header)
    print("-" * (6 + 16 * len(activations)))

    for seed in range(NUM_SEEDS):
        row = f"{seed:<6}"
        for act in activations:
            row += f" {results[act][seed]:>14.2f}%"
        print(row)
    print()

    # Winners
    lowest_std = min(activations, key=lambda a: stats[a]['std'])
    highest_mean = max(activations, key=lambda a: stats[a]['mean'])
    lowest_cv = min(activations, key=lambda a: stats[a]['cv'])

    print("=" * 70)
    print("WINNERS")
    print("=" * 70)
    print(f"WINNER (lowest variance/std):    {lowest_std} (std = {stats[lowest_std]['std']:.2f}%)")
    print(f"WINNER (lowest CV):              {lowest_cv} (CV = {stats[lowest_cv]['cv']:.2f}%)")
    print(f"WINNER (highest mean accuracy):  {highest_mean} (mean = {stats[highest_mean]['mean']:.2f}%)")
    print()

    # Hypothesis evaluation
    print("=" * 70)
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)
    print()
    print("Hypothesis: Stable gradient norms -> more predictable optimization")
    print("            -> lower variance across runs")
    print()

    # Rank by variance
    ranked_by_var = sorted(activations, key=lambda a: stats[a]['std'])
    print("Activations ranked by variance (lowest to highest):")
    for i, act in enumerate(ranked_by_var, 1):
        print(f"  {i}. {act:<18} std={stats[act]['std']:.3f}%  CV={stats[act]['cv']:.3f}%")
    print()

    # Check if OuroborosExact has lowest variance
    ouro_rank = ranked_by_var.index('OuroborosExact') + 1
    if ouro_rank == 1:
        print("RESULT: OuroborosExact has the LOWEST variance across seeds.")
        print("        This SUPPORTS the hypothesis that stable gradient norms")
        print("        lead to more reproducible training.")
    elif ouro_rank <= 2:
        print(f"RESULT: OuroborosExact ranked #{ouro_rank} in variance.")
        print("        This PARTIALLY SUPPORTS the hypothesis.")
    else:
        print(f"RESULT: OuroborosExact ranked #{ouro_rank} in variance.")
        print("        This does NOT support the hypothesis strongly.")

    print()
    print(f"Total experiment time: {total_time/60:.1f} minutes")
    print()

    # Return results for potential further analysis
    return results, stats


if __name__ == "__main__":
    main()
