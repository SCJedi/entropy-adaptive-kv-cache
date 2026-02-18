#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast Reproducibility Test: Variance Across Random Seeds

Tests whether OuroborosExact gives more consistent results across random seeds.
Optimized for CPU - smaller network, fewer epochs.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
import time
import sys
import os
from typing import Dict, List

# Unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

def log(msg):
    print(msg, flush=True)

# ============================================================================
# ACTIVATION FUNCTIONS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2
OPTIMAL_LAMBDA = 0.2955977425220668

class OuroborosExact(nn.Module):
    def __init__(self):
        super().__init__()
        self.lam = OPTIMAL_LAMBDA

    def forward(self, x):
        s = torch.sigmoid(x)
        return x * (self.lam + (1 - self.lam) * s)

class Swish(nn.Module):
    def forward(self, x):
        return x * torch.sigmoid(x)

class Mish(nn.Module):
    def forward(self, x):
        return x * torch.tanh(torch.nn.functional.softplus(x))

CRITICAL_SCALES = {
    'OuroborosExact': 1.3820,
    'Swish': 1.6233,
    'Mish': 1.4448,
    'ReLU': 1.4142,
    'GELU': 1.4811,
}

# ============================================================================
# NETWORK
# ============================================================================

class DeepMLP(nn.Module):
    def __init__(self, activation_name: str, depth: int = 10, width: int = 128):
        super().__init__()

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

        scale = CRITICAL_SCALES[activation_name]

        layers = []
        input_layer = nn.Linear(28 * 28, width)
        nn.init.normal_(input_layer.weight, mean=0, std=scale / np.sqrt(28 * 28))
        nn.init.zeros_(input_layer.bias)
        layers.append(input_layer)

        for _ in range(depth - 1):
            layer = nn.Linear(width, width)
            nn.init.normal_(layer.weight, mean=0, std=scale / np.sqrt(width))
            nn.init.zeros_(layer.bias)
            layers.append(layer)

        self.layers = nn.ModuleList(layers)

        self.output_layer = nn.Linear(width, 10)
        nn.init.normal_(self.output_layer.weight, mean=0, std=1.0 / np.sqrt(width))
        nn.init.zeros_(self.output_layer.bias)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        for layer in self.layers:
            x = layer(x)
            x = self.activation(x)
        return self.output_layer(x)

# ============================================================================
# TRAINING
# ============================================================================

def set_seed(seed: int):
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def run_experiment(activation_name: str, seed: int, epochs: int,
                   train_loader, test_loader, device, depth, width) -> float:
    set_seed(seed)
    model = DeepMLP(activation_name, depth=depth, width=width).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        for data, target in train_loader:
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

    # Test
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)

    return 100.0 * correct / total

# ============================================================================
# MAIN
# ============================================================================

def main():
    log("=" * 70)
    log("REPRODUCIBILITY TEST: Variance Across Random Seeds")
    log("=" * 70)
    log("")

    # Fast configuration for CPU
    # ~30-40s per run = ~25-30 minutes total
    NUM_SEEDS = 10
    EPOCHS = 3
    BATCH_SIZE = 512
    DEPTH = 8
    WIDTH = 64

    log("Configuration:")
    log(f"  Dataset:    FashionMNIST")
    log(f"  Network:    {DEPTH}-layer MLP, width {WIDTH}, no BatchNorm")
    log(f"  Optimizer:  Adam, LR=1e-3")
    log(f"  Epochs:     {EPOCHS}")
    log(f"  Seeds:      {NUM_SEEDS} (0-{NUM_SEEDS-1})")
    log(f"  Batch size: {BATCH_SIZE}")
    log("")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    log(f"Device: {device}")
    log("")

    # Load data
    log("Loading FashionMNIST...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    train_dataset = datasets.FashionMNIST(
        root=data_dir, train=True, download=False, transform=transform
    )
    test_dataset = datasets.FashionMNIST(
        root=data_dir, train=False, download=False, transform=transform
    )

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    log(f"  Train: {len(train_dataset)}, Test: {len(test_dataset)}")
    log("")

    activations = ['OuroborosExact', 'Swish', 'Mish', 'ReLU', 'GELU']

    log("Critical init scales:")
    for act in activations:
        log(f"  {act:15}: {CRITICAL_SCALES[act]:.4f}")
    log("")

    # Run experiments
    log("=" * 70)
    log("RUNNING EXPERIMENTS")
    log("=" * 70)
    log("")

    results: Dict[str, List[float]] = {act: [] for act in activations}

    total_runs = len(activations) * NUM_SEEDS
    run_count = 0
    start_time = time.time()

    for seed in range(NUM_SEEDS):
        log(f"Seed {seed}:")
        for activation in activations:
            run_count += 1
            run_start = time.time()

            acc = run_experiment(
                activation, seed, EPOCHS, train_loader, test_loader,
                device, DEPTH, WIDTH
            )
            results[activation].append(acc)

            run_time = time.time() - run_start
            elapsed = time.time() - start_time
            eta = (elapsed / run_count) * (total_runs - run_count)

            log(f"  {activation:15}: {acc:5.2f}%  ({run_time:.1f}s, ETA: {eta/60:.1f}min)")
        log("")

    total_time = time.time() - start_time

    # Results
    log("")
    log("=" * 70)
    log(f"REPRODUCIBILITY TEST ({NUM_SEEDS} seeds)")
    log("=" * 70)
    log("")

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

    log(f"{'Activation':<18} {'Mean Acc':>10} {'Std':>10} {'Min':>10} {'Max':>10} {'CV':>10}")
    log("-" * 70)
    for act in activations:
        s = stats[act]
        log(f"{act:<18} {s['mean']:>9.2f}% {s['std']:>9.2f}% {s['min']:>9.2f}% {s['max']:>9.2f}% {s['cv']:>9.2f}%")
    log("")

    # Individual runs
    log("INDIVIDUAL RUNS:")
    header = f"{'Seed':<6}"
    for act in activations:
        header += f" {act:>15}"
    log(header)
    log("-" * (6 + 16 * len(activations)))

    for seed in range(NUM_SEEDS):
        row = f"{seed:<6}"
        for act in activations:
            row += f" {results[act][seed]:>14.2f}%"
        log(row)
    log("")

    # Winners
    lowest_std = min(activations, key=lambda a: stats[a]['std'])
    highest_mean = max(activations, key=lambda a: stats[a]['mean'])
    lowest_cv = min(activations, key=lambda a: stats[a]['cv'])

    log("=" * 70)
    log("WINNERS")
    log("=" * 70)
    log(f"WINNER (lowest std):             {lowest_std} (std = {stats[lowest_std]['std']:.2f}%)")
    log(f"WINNER (lowest CV):              {lowest_cv} (CV = {stats[lowest_cv]['cv']:.2f}%)")
    log(f"WINNER (highest mean accuracy):  {highest_mean} (mean = {stats[highest_mean]['mean']:.2f}%)")
    log("")

    # Hypothesis
    log("=" * 70)
    log("HYPOTHESIS EVALUATION")
    log("=" * 70)
    log("")
    log("Hypothesis: Stable gradient norms -> more predictable optimization")
    log("            -> lower variance across runs")
    log("")

    ranked_by_var = sorted(activations, key=lambda a: stats[a]['std'])
    log("Activations ranked by variance (lowest to highest):")
    for i, act in enumerate(ranked_by_var, 1):
        log(f"  {i}. {act:<18} std={stats[act]['std']:.3f}%  CV={stats[act]['cv']:.3f}%")
    log("")

    ouro_rank = ranked_by_var.index('OuroborosExact') + 1
    if ouro_rank == 1:
        log("RESULT: OuroborosExact has the LOWEST variance across seeds.")
        log("        This SUPPORTS the hypothesis.")
    elif ouro_rank <= 2:
        log(f"RESULT: OuroborosExact ranked #{ouro_rank} in variance.")
        log("        This PARTIALLY SUPPORTS the hypothesis.")
    else:
        log(f"RESULT: OuroborosExact ranked #{ouro_rank} in variance.")
        log("        This does NOT strongly support the hypothesis.")

    log("")
    log(f"Total time: {total_time/60:.1f} minutes")
    log("")

if __name__ == "__main__":
    main()
