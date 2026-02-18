#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Activation Benchmark: OuroborosExact vs Standard Activations on Real Learning

Test whether OuroborosExact (tuned to critical scale = 3-phi) performs better
than standard activations on FashionMNIST classification with DEEP networks.

Activations tested:
1. OuroborosExact - f(x) = x * (lambda + (1-lambda) * sigmoid(x)), lambda = 0.375706
2. Swish/SiLU - f(x) = x * sigmoid(x)
3. Mish - f(x) = x * tanh(softplus(x))
4. ReLU - f(x) = max(0, x)
5. GELU - Gaussian Error Linear Unit

Each activation uses its OWN optimal critical scale for initialization.

Author: Claude (Anthropic)
Date: 2026-02-08
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision
import torchvision.transforms as transforms
import time
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio = 1.618033988749895
THREE_MINUS_PHI = 3 - PHI   # Target critical scale = 1.3819660112501051

# Lambda for OuroborosExact (from ouroboros_exact.py derivation)
OUROBOROS_LAMBDA = 0.375706395625264

# Critical scales for each activation (from theoretical analysis)
# These are sqrt(1/E[f'(x)^2]) for x ~ N(0,1)
CRITICAL_SCALES = {
    'OuroborosExact': THREE_MINUS_PHI,  # 1.3820
    'ReLU': np.sqrt(2),                  # 1.4142 (He init)
    'Swish': 1.6233,                     # From numerical computation
    'Mish': 1.4448,                      # From numerical computation
    'GELU': 1.4811,                      # From numerical computation
}

# ============================================================================
# ACTIVATION MODULES
# ============================================================================

class OuroborosExact(nn.Module):
    """OuroborosExact activation with optimal lambda for critical scale = (3-phi)."""
    def __init__(self):
        super().__init__()
        self.lam = OUROBOROS_LAMBDA

    def forward(self, x):
        s = torch.sigmoid(x)
        gate = self.lam + (1 - self.lam) * s
        return x * gate


class Swish(nn.Module):
    """Standard Swish/SiLU activation."""
    def forward(self, x):
        return x * torch.sigmoid(x)


class Mish(nn.Module):
    """Mish activation."""
    def forward(self, x):
        return x * torch.tanh(nn.functional.softplus(x))


class ReLUActivation(nn.Module):
    """ReLU activation wrapper."""
    def forward(self, x):
        return torch.relu(x)


class GELUActivation(nn.Module):
    """GELU activation wrapper."""
    def forward(self, x):
        return nn.functional.gelu(x)


ACTIVATION_CLASSES = {
    'OuroborosExact': OuroborosExact,
    'Swish': Swish,
    'Mish': Mish,
    'ReLU': ReLUActivation,
    'GELU': GELUActivation,
}

# ============================================================================
# NETWORK ARCHITECTURE
# ============================================================================

def create_mlp(depth, width, activation_name, input_dim=784, output_dim=10):
    """
    Build MLP with proper critical initialization for each activation.

    Args:
        depth: Number of hidden layers
        width: Width of each hidden layer
        activation_name: Name of activation function
        input_dim: Input dimension (784 for MNIST)
        output_dim: Output dimension (10 for classification)

    Returns:
        nn.Sequential model
    """
    activation_class = ACTIVATION_CLASSES[activation_name]
    critical_scale = CRITICAL_SCALES[activation_name]

    layers = []

    # Input layer
    input_layer = nn.Linear(input_dim, width)
    # Initialize with critical scale
    nn.init.normal_(input_layer.weight, mean=0, std=critical_scale / np.sqrt(input_dim))
    nn.init.zeros_(input_layer.bias)
    layers.append(input_layer)
    layers.append(activation_class())

    # Hidden layers
    for _ in range(depth - 1):
        hidden_layer = nn.Linear(width, width)
        nn.init.normal_(hidden_layer.weight, mean=0, std=critical_scale / np.sqrt(width))
        nn.init.zeros_(hidden_layer.bias)
        layers.append(hidden_layer)
        layers.append(activation_class())

    # Output layer (no activation)
    output_layer = nn.Linear(width, output_dim)
    nn.init.normal_(output_layer.weight, mean=0, std=1.0 / np.sqrt(width))
    nn.init.zeros_(output_layer.bias)
    layers.append(output_layer)

    return nn.Sequential(*layers)


# ============================================================================
# TRAINING AND EVALUATION
# ============================================================================

def train_and_evaluate(model, train_loader, test_loader, epochs=10, lr=0.001, device='cpu'):
    """
    Train model and collect metrics.

    Returns:
        dict with:
            - loss_curve: list of training losses per epoch
            - train_acc_curve: list of training accuracies per epoch
            - test_acc: final test accuracy
            - grad_norms: list of gradient norm statistics per epoch
            - training_time: total training time in seconds
            - converged: True if loss decreased meaningfully
    """
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    loss_curve = []
    train_acc_curve = []
    grad_norms = []

    start_time = time.time()

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        epoch_grad_norms = []

        for batch_idx, (data, target) in enumerate(train_loader):
            data = data.view(data.size(0), -1).to(device)  # Flatten
            target = target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)

            # Check for NaN
            if torch.isnan(loss):
                return {
                    'loss_curve': loss_curve,
                    'train_acc_curve': train_acc_curve,
                    'test_acc': 0.0,
                    'grad_norms': grad_norms,
                    'training_time': time.time() - start_time,
                    'converged': False,
                    'diverged': True,
                }

            loss.backward()

            # Collect gradient norms
            total_grad_norm = 0
            for p in model.parameters():
                if p.grad is not None:
                    total_grad_norm += p.grad.norm().item() ** 2
            epoch_grad_norms.append(np.sqrt(total_grad_norm))

            # Gradient clipping to prevent explosion
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)

            optimizer.step()

            total_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()

        avg_loss = total_loss / len(train_loader)
        train_acc = 100. * correct / total
        avg_grad_norm = np.mean(epoch_grad_norms)

        loss_curve.append(avg_loss)
        train_acc_curve.append(train_acc)
        grad_norms.append({
            'mean': avg_grad_norm,
            'std': np.std(epoch_grad_norms),
            'max': np.max(epoch_grad_norms),
            'min': np.min(epoch_grad_norms),
        })

    training_time = time.time() - start_time

    # Evaluate on test set
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in test_loader:
            data = data.view(data.size(0), -1).to(device)
            target = target.to(device)
            output = model(data)
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()

    test_acc = 100. * correct / total

    # Check if training converged (loss decreased by at least 20%)
    converged = len(loss_curve) >= 2 and loss_curve[-1] < loss_curve[0] * 0.8

    return {
        'loss_curve': loss_curve,
        'train_acc_curve': train_acc_curve,
        'test_acc': test_acc,
        'grad_norms': grad_norms,
        'training_time': training_time,
        'converged': converged,
        'diverged': False,
    }


# ============================================================================
# BENCHMARK
# ============================================================================

def run_benchmark(depths=[10, 20, 50], width=256, epochs=10, batch_size=128,
                  dataset='FashionMNIST', device=None):
    """
    Run full benchmark comparing all activations at various depths.

    Args:
        depths: List of network depths to test
        width: Hidden layer width
        epochs: Training epochs per configuration
        batch_size: Training batch size
        dataset: 'MNIST' or 'FashionMNIST'
        device: 'cpu' or 'cuda'
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print("=" * 80)
    print(f"ACTIVATION BENCHMARK: {dataset} Classification")
    print("=" * 80)
    print()
    print(f"Device: {device}")
    print(f"Network width: {width}")
    print(f"Training epochs: {epochs}")
    print(f"Batch size: {batch_size}")
    print()

    # Load dataset
    print("Loading dataset...")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    if dataset == 'FashionMNIST':
        train_dataset = torchvision.datasets.FashionMNIST(
            root='./data', train=True, download=True, transform=transform
        )
        test_dataset = torchvision.datasets.FashionMNIST(
            root='./data', train=False, download=True, transform=transform
        )
    else:
        train_dataset = torchvision.datasets.MNIST(
            root='./data', train=True, download=True, transform=transform
        )
        test_dataset = torchvision.datasets.MNIST(
            root='./data', train=False, download=True, transform=transform
        )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    print(f"Train samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    print()

    # Print critical scales
    print("-" * 80)
    print("CRITICAL INITIALIZATION SCALES")
    print("-" * 80)
    print()
    for name, scale in CRITICAL_SCALES.items():
        target_diff = abs(scale - THREE_MINUS_PHI)
        print(f"  {name:<16}: {scale:.6f}  (diff from 3-phi: {target_diff:.6f})")
    print()
    print(f"  Target (3-phi):   {THREE_MINUS_PHI:.6f}")
    print()

    # Store all results
    all_results = {}

    activation_names = ['OuroborosExact', 'Swish', 'Mish', 'ReLU', 'GELU']

    for depth in depths:
        print("=" * 80)
        print(f"DEPTH = {depth} LAYERS")
        print("=" * 80)
        print()

        depth_results = {}

        for act_name in activation_names:
            print(f"Training {act_name} (depth={depth})...", end=" ", flush=True)

            # Set seed for reproducibility
            torch.manual_seed(42)
            np.random.seed(42)

            # Create model
            model = create_mlp(depth, width, act_name)

            # Count parameters
            n_params = sum(p.numel() for p in model.parameters())

            # Train and evaluate
            results = train_and_evaluate(model, train_loader, test_loader,
                                        epochs=epochs, lr=0.001, device=device)
            results['n_params'] = n_params

            depth_results[act_name] = results

            # Print status
            if results['diverged']:
                print("DIVERGED")
            elif not results['converged']:
                print(f"unstable (acc={results['test_acc']:.1f}%)")
            else:
                print(f"done (acc={results['test_acc']:.1f}%)")

        all_results[depth] = depth_results

        # Print results table for this depth
        print()
        print("-" * 80)
        print(f"{'Activation':<16} {'Init Scale':>10} {'Test Acc':>10} {'Final Loss':>12} "
              f"{'Grad Norm':>12} {'Status':>10}")
        print("-" * 80)

        for act_name in activation_names:
            r = depth_results[act_name]
            scale = CRITICAL_SCALES[act_name]

            if r['diverged']:
                status = "DIVERGED"
                test_acc = "N/A"
                final_loss = "N/A"
                grad_norm = "N/A"
            else:
                status = "OK" if r['converged'] else "unstable"
                test_acc = f"{r['test_acc']:.2f}%"
                final_loss = f"{r['loss_curve'][-1]:.4f}" if r['loss_curve'] else "N/A"
                grad_norm = f"{r['grad_norms'][-1]['mean']:.4f}" if r['grad_norms'] else "N/A"

            print(f"{act_name:<16} {scale:>10.4f} {test_acc:>10} {final_loss:>12} "
                  f"{grad_norm:>12} {status:>10}")

        print()

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================

    print("=" * 80)
    print("SUMMARY: PERFORMANCE COMPARISON")
    print("=" * 80)
    print()

    # Create summary table
    print(f"{'Depth':<8} ", end="")
    for act_name in activation_names:
        print(f"{act_name:>14} ", end="")
    print()
    print("-" * (8 + 15 * len(activation_names)))

    for depth in depths:
        print(f"{depth:<8} ", end="")
        for act_name in activation_names:
            r = all_results[depth][act_name]
            if r['diverged']:
                print(f"{'DIVERGED':>14} ", end="")
            else:
                print(f"{r['test_acc']:>13.2f}% ", end="")
        print()

    print()

    # Determine winner at each depth
    print("-" * 80)
    print("WINNER AT EACH DEPTH")
    print("-" * 80)
    print()

    for depth in depths:
        valid_results = {name: r for name, r in all_results[depth].items()
                        if not r['diverged']}

        if valid_results:
            winner = max(valid_results.items(), key=lambda x: x[1]['test_acc'])
            print(f"  Depth {depth:>2}: {winner[0]:<16} ({winner[1]['test_acc']:.2f}%)")
        else:
            print(f"  Depth {depth:>2}: ALL DIVERGED")

    print()

    # Overall analysis
    print("-" * 80)
    print("ANALYSIS")
    print("-" * 80)
    print()

    # Average test accuracy across depths (excluding diverged)
    avg_acc = {}
    for act_name in activation_names:
        accs = [all_results[d][act_name]['test_acc']
                for d in depths if not all_results[d][act_name]['diverged']]
        if accs:
            avg_acc[act_name] = np.mean(accs)
        else:
            avg_acc[act_name] = 0.0

    print("Average Test Accuracy (across all depths):")
    for act_name in sorted(avg_acc.keys(), key=lambda x: avg_acc[x], reverse=True):
        if avg_acc[act_name] > 0:
            print(f"  {act_name:<16}: {avg_acc[act_name]:.2f}%")
        else:
            print(f"  {act_name:<16}: ALL DIVERGED")

    print()

    # Check stability (number of depths where training was stable)
    print("Training Stability (converged at N depths):")
    for act_name in activation_names:
        n_stable = sum(1 for d in depths
                      if all_results[d][act_name]['converged']
                      and not all_results[d][act_name]['diverged'])
        print(f"  {act_name:<16}: {n_stable}/{len(depths)} depths")

    print()

    # Gradient health
    print("Final Epoch Gradient Norms (averaged across depths):")
    for act_name in activation_names:
        grad_norms = [all_results[d][act_name]['grad_norms'][-1]['mean']
                     for d in depths
                     if not all_results[d][act_name]['diverged']
                     and all_results[d][act_name]['grad_norms']]
        if grad_norms:
            print(f"  {act_name:<16}: mean={np.mean(grad_norms):.4f}, "
                  f"std={np.std(grad_norms):.4f}")
        else:
            print(f"  {act_name:<16}: N/A (all diverged)")

    print()
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()

    # Find overall best
    if avg_acc:
        best_overall = max(avg_acc.items(), key=lambda x: x[1])
        print(f"Best overall activation: {best_overall[0]} (avg acc: {best_overall[1]:.2f}%)")

        ouro_acc = avg_acc.get('OuroborosExact', 0)
        if ouro_acc > 0:
            if best_overall[0] == 'OuroborosExact':
                print("\nOuroborosExact (with critical scale = 3-phi) WINS the benchmark!")
            else:
                diff = best_overall[1] - ouro_acc
                print(f"\nOuroborosExact achieved {ouro_acc:.2f}%, {diff:.2f}% behind {best_overall[0]}.")
                print("The (3-phi) critical scale may provide stability benefits not captured by accuracy alone.")

    print()

    return all_results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys

    # Use smaller settings if --quick flag is passed
    if '--quick' in sys.argv:
        # Quick test
        results = run_benchmark(
            depths=[10, 20],
            width=128,
            epochs=5,
            batch_size=256,
            dataset='FashionMNIST'
        )
    else:
        # Full benchmark
        results = run_benchmark(
            depths=[10, 20, 50],
            width=256,
            epochs=10,
            batch_size=128,
            dataset='FashionMNIST'
        )
