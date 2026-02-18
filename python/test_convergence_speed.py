#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convergence Speed Test: OuroborosExact vs Standard Activations

Tests whether OuroborosExact reaches target accuracy faster than other activations.

Hypothesis: Stable gradient flow -> more efficient learning -> faster convergence

Setup:
- Dataset: FashionMNIST
- Network: 20-layer MLP, width 256, no BatchNorm
- Each activation uses its own critical init scale
- Optimizer: Adam, LR=1e-3
- Epochs: 20

Activations tested:
- OuroborosExact (scale=1.3820)
- Swish (scale=1.6233)
- Mish (scale=1.4448)
- ReLU (scale=1.4142)
- GELU (scale=1.4811)
"""

import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import numpy as np
import time
import warnings
warnings.filterwarnings('ignore')

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# =============================================================================
# CONSTANTS
# =============================================================================

PHI = (1 + np.sqrt(5)) / 2
THREE_MINUS_PHI = 3 - PHI  # 1.3819660112501051

# Critical initialization scales for each activation
CRITICAL_SCALES = {
    'OuroborosExact': 1.3820,  # (3 - phi)
    'Swish': 1.6233,
    'Mish': 1.4448,
    'ReLU': 1.4142,  # sqrt(2)
    'GELU': 1.4811,
}

# =============================================================================
# ACTIVATION FUNCTIONS
# =============================================================================

# Optimal lambda for OuroborosExact (computed from ouroboros_exact.py)
OPTIMAL_LAMBDA = 0.2356466428397881

class OuroborosExact(nn.Module):
    """
    Exact (3-phi) critical scale activation.
    f(x) = x * (lambda + (1-lambda) * sigmoid(x))
    """
    def __init__(self):
        super().__init__()
        self.lam = OPTIMAL_LAMBDA

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
        return x * torch.tanh(F.softplus(x))


# ReLU and GELU are available from torch.nn

# =============================================================================
# MODEL DEFINITION
# =============================================================================

class DeepMLP(nn.Module):
    """
    Deep MLP with specified activation and critical initialization.

    Args:
        input_dim: Input dimension
        hidden_dim: Hidden layer dimension
        output_dim: Output dimension (10 for FashionMNIST)
        num_layers: Number of layers
        activation_class: Activation class to use
        critical_scale: Critical initialization scale for this activation
    """
    def __init__(self, input_dim=784, hidden_dim=256, output_dim=10,
                 num_layers=20, activation_class=None, critical_scale=1.0):
        super().__init__()

        self.layers = nn.ModuleList()
        self.activations = nn.ModuleList()

        # Input layer
        self.layers.append(nn.Linear(input_dim, hidden_dim))

        # Hidden layers
        for _ in range(num_layers - 2):
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))

        # Output layer
        self.layers.append(nn.Linear(hidden_dim, output_dim))

        # Activations (one per hidden layer, not for output)
        for _ in range(num_layers - 1):
            if activation_class == nn.ReLU:
                self.activations.append(nn.ReLU())
            elif activation_class == nn.GELU:
                self.activations.append(nn.GELU())
            else:
                self.activations.append(activation_class())

        # Apply critical initialization
        self._init_weights(critical_scale)

    def _init_weights(self, scale):
        """Initialize weights with critical scale."""
        for layer in self.layers:
            fan_in = layer.weight.shape[1]
            std = scale / np.sqrt(fan_in)
            nn.init.normal_(layer.weight, mean=0, std=std)
            nn.init.zeros_(layer.bias)

    def forward(self, x):
        # Flatten input
        x = x.view(x.size(0), -1)

        # Forward through layers with activations
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x)
            x = self.activations[i](x)

        # Output layer (no activation)
        x = self.layers[-1](x)
        return x


# =============================================================================
# TRAINING FUNCTIONS
# =============================================================================

def train_epoch(model, train_loader, optimizer, device):
    """Train for one epoch, return average loss."""
    model.train()
    total_loss = 0
    n_batches = 0

    for data, target in train_loader:
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
        loss = F.cross_entropy(output, target)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / n_batches


def evaluate(model, test_loader, device):
    """Evaluate model, return accuracy."""
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += (pred == target).sum().item()
            total += target.size(0)

    return 100 * correct / total


def train_model(activation_name, activation_class, critical_scale,
                train_loader, test_loader, device, num_epochs=20, lr=1e-3):
    """
    Train a model with given activation and return training history.

    Returns:
        dict with keys: 'train_loss', 'test_acc', 'epochs_to_80', 'epochs_to_85'
    """
    model = DeepMLP(
        input_dim=784,
        hidden_dim=256,
        output_dim=10,
        num_layers=20,
        activation_class=activation_class,
        critical_scale=critical_scale
    ).to(device)

    optimizer = optim.Adam(model.parameters(), lr=lr)

    history = {
        'train_loss': [],
        'test_acc': [],
        'epochs_to_80': None,
        'epochs_to_85': None,
    }

    for epoch in range(1, num_epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, device)
        test_acc = evaluate(model, test_loader, device)

        history['train_loss'].append(train_loss)
        history['test_acc'].append(test_acc)

        # Track epochs to reach thresholds
        if history['epochs_to_80'] is None and test_acc >= 80:
            history['epochs_to_80'] = epoch
        if history['epochs_to_85'] is None and test_acc >= 85:
            history['epochs_to_85'] = epoch

    return history


# =============================================================================
# MAIN TEST
# =============================================================================

def main():
    print("CONVERGENCE SPEED TEST", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}", flush=True)
    print(flush=True)

    # Data loading
    print("Loading FashionMNIST...")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.2860,), (0.3530,))  # FashionMNIST stats
    ])

    train_dataset = datasets.FashionMNIST(
        root='./data', train=True, download=True, transform=transform
    )
    test_dataset = datasets.FashionMNIST(
        root='./data', train=False, download=True, transform=transform
    )

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False, num_workers=0)

    print(f"Training samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    print()

    # Define activations to test
    activations = {
        'OuroborosExact': OuroborosExact,
        'Swish': Swish,
        'Mish': Mish,
        'ReLU': nn.ReLU,
        'GELU': nn.GELU,
    }

    # Train all activations
    print("Training 20-layer MLPs (width=256, no BatchNorm)...")
    print("Optimizer: Adam, LR=1e-3, Epochs: 20")
    print("-" * 70)
    print()

    results = {}

    for name, act_class in activations.items():
        scale = CRITICAL_SCALES[name]
        print(f"Training {name} (scale={scale:.4f})...", flush=True)

        start_time = time.time()
        history = train_model(
            name, act_class, scale,
            train_loader, test_loader, device,
            num_epochs=20, lr=1e-3
        )
        elapsed = time.time() - start_time

        results[name] = history
        final_acc = history['test_acc'][-1]
        print(f"  Done in {elapsed:.1f}s (final acc: {final_acc:.1f}%)", flush=True)

    print()

    # Print results
    print("=" * 70)
    print()
    print("EPOCHS TO REACH TARGET ACCURACY:")
    print(f"{'Activation':<18} {'80% acc':<12} {'85% acc':<12} {'Final acc':<12}")
    print("-" * 70)

    for name in activations.keys():
        history = results[name]
        e80 = history['epochs_to_80']
        e85 = history['epochs_to_85']
        final = history['test_acc'][-1]

        e80_str = str(e80) if e80 is not None else "N/A"
        e85_str = str(e85) if e85 is not None else "N/A"

        print(f"{name:<18} {e80_str:<12} {e85_str:<12} {final:.1f}%")

    print()
    print("=" * 70)
    print()
    print("LEARNING CURVES (accuracy per epoch):")

    # Header
    header = f"{'Epoch':<8}"
    for name in activations.keys():
        header += f"{name:<16}"
    print(header)
    print("-" * 70)

    # Each epoch
    for epoch in range(20):
        row = f"{epoch+1:<8}"
        for name in activations.keys():
            acc = results[name]['test_acc'][epoch]
            row += f"{acc:.1f}%{'':<11}"
        print(row)

    print()
    print("=" * 70)
    print()

    # Determine winner (fastest to 85%)
    fastest_85 = None
    fastest_85_epoch = float('inf')

    for name, history in results.items():
        e85 = history['epochs_to_85']
        if e85 is not None and e85 < fastest_85_epoch:
            fastest_85_epoch = e85
            fastest_85 = name

    if fastest_85:
        print(f"WINNER (fastest to 85%): {fastest_85} (epoch {fastest_85_epoch})")
    else:
        # Find highest final accuracy
        best_name = max(results.keys(), key=lambda n: results[n]['test_acc'][-1])
        best_acc = results[best_name]['test_acc'][-1]
        print(f"No activation reached 85%. Best final accuracy: {best_name} ({best_acc:.1f}%)")

    print()

    # Additional analysis: training loss curves
    print("=" * 70)
    print()
    print("TRAINING LOSS (final epoch):")
    print("-" * 70)
    for name in activations.keys():
        final_loss = results[name]['train_loss'][-1]
        print(f"  {name:<18}: {final_loss:.4f}")

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
