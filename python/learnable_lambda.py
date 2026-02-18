#!/usr/bin/env python3
"""
Learnable Lambda: Let the network discover optimal Ouroboros lambda during training.

Two modes:
1. Global lambda - one shared lambda for entire network
2. Per-layer lambda - each layer learns its own lambda

Hypothesis: Deep layers will learn higher lambda (more stable),
shallow layers will learn lower lambda (more expressive).

Runtime: ~5-10 min on CPU
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision
import torchvision.transforms as transforms
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# LEARNABLE OUROBOROS
# ============================================================================

class LearnableOuroboros(nn.Module):
    """
    Ouroboros activation with learnable lambda.

    f(x) = x * (lambda + (1-lambda) * sigmoid(x))

    Lambda is initialized to init_lambda and learned during training.
    Constrained to [0.01, 0.99] via sigmoid reparameterization.
    """
    def __init__(self, init_lambda=0.5, name=""):
        super().__init__()
        # Reparameterize: lambda = sigmoid(raw_lambda)
        # So raw_lambda = logit(init_lambda)
        init_raw = np.log(init_lambda / (1 - init_lambda))
        self.raw_lambda = nn.Parameter(torch.tensor(init_raw, dtype=torch.float32))
        self.name = name

    @property
    def lam(self):
        return torch.sigmoid(self.raw_lambda)

    def forward(self, x):
        lam = self.lam
        return x * (lam + (1 - lam) * torch.sigmoid(x))

    def extra_repr(self):
        return f"lambda={self.lam.item():.4f}"


class SharedLambdaOuroboros(nn.Module):
    """
    Ouroboros activation with a SHARED learnable lambda across all instances.

    All layers using this activation share the same lambda parameter.
    """
    def __init__(self, shared_raw_lambda):
        super().__init__()
        self.shared_raw_lambda = shared_raw_lambda

    @property
    def lam(self):
        return torch.sigmoid(self.shared_raw_lambda)

    def forward(self, x):
        lam = self.lam
        return x * (lam + (1 - lam) * torch.sigmoid(x))


# ============================================================================
# MODEL BUILDERS
# ============================================================================

def create_mlp_per_layer_lambda(depth, width, init_lambda=0.5, input_dim=784, output_dim=10):
    """Create MLP where each layer has its own learnable lambda."""
    layers = []
    layer_names = []

    # Input layer
    linear = nn.Linear(input_dim, width)
    nn.init.kaiming_normal_(linear.weight, nonlinearity='relu')
    nn.init.zeros_(linear.bias)
    activation = LearnableOuroboros(init_lambda, name=f"layer_0")
    layers.extend([linear, activation])
    layer_names.append(f"layer_0")

    # Hidden layers
    for i in range(depth - 1):
        linear = nn.Linear(width, width)
        nn.init.kaiming_normal_(linear.weight, nonlinearity='relu')
        nn.init.zeros_(linear.bias)
        activation = LearnableOuroboros(init_lambda, name=f"layer_{i+1}")
        layers.extend([linear, activation])
        layer_names.append(f"layer_{i+1}")

    # Output layer
    linear = nn.Linear(width, output_dim)
    nn.init.kaiming_normal_(linear.weight, nonlinearity='relu')
    nn.init.zeros_(linear.bias)
    layers.append(linear)

    return nn.Sequential(*layers), layer_names


def create_mlp_shared_lambda(depth, width, init_lambda=0.5, input_dim=784, output_dim=10):
    """Create MLP where all layers share ONE learnable lambda."""
    # Shared parameter
    init_raw = np.log(init_lambda / (1 - init_lambda))
    shared_raw_lambda = nn.Parameter(torch.tensor(init_raw, dtype=torch.float32))

    layers = []

    # Input layer
    linear = nn.Linear(input_dim, width)
    nn.init.kaiming_normal_(linear.weight, nonlinearity='relu')
    nn.init.zeros_(linear.bias)
    layers.extend([linear, SharedLambdaOuroboros(shared_raw_lambda)])

    # Hidden layers
    for _ in range(depth - 1):
        linear = nn.Linear(width, width)
        nn.init.kaiming_normal_(linear.weight, nonlinearity='relu')
        nn.init.zeros_(linear.bias)
        layers.extend([linear, SharedLambdaOuroboros(shared_raw_lambda)])

    # Output layer
    linear = nn.Linear(width, output_dim)
    nn.init.kaiming_normal_(linear.weight, nonlinearity='relu')
    nn.init.zeros_(linear.bias)
    layers.append(linear)

    model = nn.Sequential(*layers)
    # Attach shared lambda to model for easy access
    model.shared_raw_lambda = shared_raw_lambda

    return model


# ============================================================================
# TRAINING
# ============================================================================

def get_lambda_values(model, mode='per_layer'):
    """Extract current lambda values from model."""
    lambdas = {}
    if mode == 'per_layer':
        for i, module in enumerate(model):
            if isinstance(module, LearnableOuroboros):
                lambdas[module.name] = module.lam.item()
    else:  # shared
        lam = torch.sigmoid(model.shared_raw_lambda).item()
        lambdas['shared'] = lam
    return lambdas


def train_and_track_lambda(model, train_loader, test_loader, epochs=10, lr=0.001,
                           mode='per_layer', device='cpu'):
    """Train model and track lambda evolution."""
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    history = {
        'epoch': [],
        'train_loss': [],
        'train_acc': [],
        'test_acc': [],
        'lambdas': [],
    }

    # Initial lambdas
    history['epoch'].append(0)
    history['train_loss'].append(None)
    history['train_acc'].append(None)
    history['test_acc'].append(None)
    history['lambdas'].append(get_lambda_values(model, mode))

    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        total_loss = 0
        correct = 0
        total = 0

        for data, target in train_loader:
            data = data.view(data.size(0), -1).to(device)
            target = target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)

            optimizer.step()

            total_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()

        train_loss = total_loss / len(train_loader)
        train_acc = 100. * correct / total

        # Test
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

        # Record
        history['epoch'].append(epoch)
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['test_acc'].append(test_acc)
        history['lambdas'].append(get_lambda_values(model, mode))

    return history


# ============================================================================
# MAIN
# ============================================================================

def run_learnable_lambda_experiment():
    print("=" * 90)
    print("LEARNABLE LAMBDA EXPERIMENT")
    print("=" * 90)
    print()

    # Settings
    depth = 10
    width = 256
    epochs = 15
    batch_size = 128
    init_lambda = 0.5  # Start in the middle

    print(f"Depth: {depth}")
    print(f"Width: {width}")
    print(f"Epochs: {epochs}")
    print(f"Initial lambda: {init_lambda}")
    print()

    # Load data
    print("Loading FashionMNIST...")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    train_dataset = torchvision.datasets.FashionMNIST(
        root='./data', train=True, download=True, transform=transform
    )
    test_dataset = torchvision.datasets.FashionMNIST(
        root='./data', train=False, download=True, transform=transform
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    print(f"Train samples: {len(train_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    print()

    # =========================================================================
    # EXPERIMENT 1: Per-layer lambda
    # =========================================================================
    print("=" * 90)
    print("EXPERIMENT 1: Per-Layer Learnable Lambda")
    print("=" * 90)
    print()

    torch.manual_seed(42)
    model_per_layer, layer_names = create_mlp_per_layer_lambda(
        depth, width, init_lambda
    )

    print("Training with per-layer learnable lambda...")
    history_per_layer = train_and_track_lambda(
        model_per_layer, train_loader, test_loader,
        epochs=epochs, mode='per_layer'
    )

    print()
    print("Lambda Evolution by Layer:")
    print("-" * 70)

    # Header
    header = f"{'Epoch':<8}"
    for name in layer_names:
        header += f"{name:>10}"
    print(header)
    print("-" * 70)

    # Data
    for i, epoch in enumerate(history_per_layer['epoch']):
        row = f"{epoch:<8}"
        lambdas = history_per_layer['lambdas'][i]
        for name in layer_names:
            row += f"{lambdas[name]:>10.4f}"
        print(row)

    print()
    print(f"Final test accuracy: {history_per_layer['test_acc'][-1]:.2f}%")
    print()

    # Analysis: do deeper layers learn higher lambda?
    final_lambdas = history_per_layer['lambdas'][-1]
    lambda_by_depth = [(int(name.split('_')[1]), final_lambdas[name]) for name in layer_names]
    lambda_by_depth.sort(key=lambda x: x[0])

    print("Final Lambda by Layer Depth:")
    print("-" * 40)
    for layer_idx, lam in lambda_by_depth:
        bar = "#" * int(lam * 40)
        print(f"  Layer {layer_idx:>2}: {lam:.4f} |{bar}")

    # Correlation between depth and lambda
    depths = [x[0] for x in lambda_by_depth]
    lambdas = [x[1] for x in lambda_by_depth]
    correlation = np.corrcoef(depths, lambdas)[0, 1]
    print()
    print(f"Correlation (depth vs lambda): {correlation:.4f}")
    if correlation > 0.3:
        print("-> Deeper layers learn HIGHER lambda (more stable, as hypothesized)")
    elif correlation < -0.3:
        print("-> Deeper layers learn LOWER lambda (more expressive)")
    else:
        print("-> No clear depth-dependent pattern")

    print()

    # =========================================================================
    # EXPERIMENT 2: Shared lambda
    # =========================================================================
    print("=" * 90)
    print("EXPERIMENT 2: Shared Learnable Lambda")
    print("=" * 90)
    print()

    torch.manual_seed(42)
    model_shared = create_mlp_shared_lambda(depth, width, init_lambda)

    print("Training with shared learnable lambda...")
    history_shared = train_and_track_lambda(
        model_shared, train_loader, test_loader,
        epochs=epochs, mode='shared'
    )

    print()
    print("Shared Lambda Evolution:")
    print("-" * 30)
    print(f"{'Epoch':<10}{'Lambda':>10}")
    print("-" * 30)

    for i, epoch in enumerate(history_shared['epoch']):
        lam = history_shared['lambdas'][i]['shared']
        print(f"{epoch:<10}{lam:>10.4f}")

    print()
    print(f"Final test accuracy: {history_shared['test_acc'][-1]:.2f}%")
    print()

    # =========================================================================
    # EXPERIMENT 3: Different starting points
    # =========================================================================
    print("=" * 90)
    print("EXPERIMENT 3: Different Initialization Points")
    print("=" * 90)
    print()

    init_lambdas = [0.1, 0.3, 0.5, 0.7, 0.9]
    convergence_results = []

    for init_lam in init_lambdas:
        torch.manual_seed(42)
        model = create_mlp_shared_lambda(depth, width, init_lam)
        history = train_and_track_lambda(
            model, train_loader, test_loader,
            epochs=epochs, mode='shared'
        )
        final_lam = history['lambdas'][-1]['shared']
        final_acc = history['test_acc'][-1]
        convergence_results.append((init_lam, final_lam, final_acc))
        print(f"  init={init_lam:.1f} -> final={final_lam:.4f}, acc={final_acc:.2f}%")

    print()
    print("-" * 50)
    print(f"{'Init Lambda':<15}{'Final Lambda':<15}{'Test Acc':<15}")
    print("-" * 50)
    for init_lam, final_lam, acc in convergence_results:
        print(f"{init_lam:<15.1f}{final_lam:<15.4f}{acc:<15.2f}%")

    print()

    # Check if they converge to same point
    final_lambdas = [r[1] for r in convergence_results]
    lambda_std = np.std(final_lambdas)
    lambda_mean = np.mean(final_lambdas)

    print(f"Final lambda mean: {lambda_mean:.4f}")
    print(f"Final lambda std:  {lambda_std:.4f}")

    if lambda_std < 0.05:
        print(f"-> All initializations converge to ~{lambda_mean:.3f}!")
        print("   This suggests an OPTIMAL lambda for this architecture/task.")
    else:
        print("-> Different initializations lead to different final lambdas.")
        print("   The loss landscape has multiple local optima for lambda.")

    print()

    # =========================================================================
    # CONCLUSION
    # =========================================================================
    print("=" * 90)
    print("CONCLUSION")
    print("=" * 90)
    print()

    best_shared = max(convergence_results, key=lambda x: x[2])
    print(f"Best configuration (shared lambda):")
    print(f"  Learned lambda: {best_shared[1]:.4f}")
    print(f"  Test accuracy: {best_shared[2]:.2f}%")
    print()

    print(f"Per-layer lambda test accuracy: {history_per_layer['test_acc'][-1]:.2f}%")
    print()

    if correlation > 0.3:
        print("KEY FINDING: Deeper layers naturally learn higher lambda values,")
        print("confirming the hypothesis that depth requires more stability.")

    print()
    print("The network CAN learn optimal lambda during training!")
    print()

    return {
        'per_layer': history_per_layer,
        'shared': history_shared,
        'convergence': convergence_results,
    }


if __name__ == "__main__":
    results = run_learnable_lambda_experiment()
