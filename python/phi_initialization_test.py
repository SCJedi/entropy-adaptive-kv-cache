"""
Phi Initialization Experiment for Neural Networks

Tests the Ouroboros framework prediction that φ-related initialization scales
should be optimal at critical points of self-referential systems (neural networks
with training feedback).

Compares 8 initialization methods:
- Standard: Xavier, He, LeCun
- Phi-based: 1/φ, sqrt(1/φ²), φ
- Controls: Small (0.3), Large (2.0)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
import time
from pathlib import Path

# Constants
PHI = 1.618033988749895  # Golden ratio
INV_PHI = 1.0 / PHI      # ≈ 0.618
SQRT_INV_PHI_SQ = np.sqrt(1.0 / (PHI * PHI))  # ≈ 0.618


class TestNet(nn.Module):
    """Simple feedforward network with custom initialization."""

    def __init__(self, input_size, hidden1, hidden2, output_size, scale_fn):
        super(TestNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden1)
        self.fc2 = nn.Linear(hidden1, hidden2)
        self.fc3 = nn.Linear(hidden2, output_size)
        self.dropout = nn.Dropout(0.3)  # Add regularization

        # Apply custom initialization
        self._custom_init(scale_fn)

    def _custom_init(self, scale_fn):
        """Initialize weights with custom scale function."""
        for layer in [self.fc1, self.fc2, self.fc3]:
            fan_in = layer.weight.shape[1]
            fan_out = layer.weight.shape[0]
            scale = scale_fn(fan_in, fan_out)
            nn.init.normal_(layer.weight, mean=0.0, std=scale)
            nn.init.zeros_(layer.bias)

    def forward(self, x):
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.dropout(torch.relu(self.fc2(x)))
        return self.fc3(x)

    def get_gradient_stats(self):
        """Compute gradient statistics for all parameters."""
        grad_values = []
        for param in self.parameters():
            if param.grad is not None:
                grad_values.append(param.grad.detach().cpu().numpy().flatten())

        if len(grad_values) == 0:
            return {'mean': 0.0, 'std': 0.0, 'has_nan': False, 'has_inf': False}

        all_grads = np.concatenate(grad_values)
        return {
            'mean': float(np.mean(all_grads)),
            'std': float(np.std(all_grads)),
            'has_nan': bool(np.isnan(all_grads).any()),
            'has_inf': bool(np.isinf(all_grads).any())
        }


# Define initialization scale functions
SCALES = {
    'xavier': lambda fan_in, fan_out: np.sqrt(2.0 / (fan_in + fan_out)),
    'he': lambda fan_in, fan_out: np.sqrt(2.0 / fan_in),
    'lecun': lambda fan_in, fan_out: np.sqrt(1.0 / fan_in),
    'phi': lambda fan_in, fan_out: INV_PHI / np.sqrt(fan_in),           # 1/φ ≈ 0.618
    'phi_v2': lambda fan_in, fan_out: SQRT_INV_PHI_SQ / np.sqrt(fan_in),  # sqrt(1/φ²) ≈ 0.618
    'phi_v3': lambda fan_in, fan_out: PHI / np.sqrt(fan_in),            # φ ≈ 1.618
    'small': lambda fan_in, fan_out: 0.3 / np.sqrt(fan_in),             # Control: too small
    'large': lambda fan_in, fan_out: 2.0 / np.sqrt(fan_in),             # Control: too large
}


def create_synthetic_dataset(n_samples=2000, n_features=784, n_classes=10):
    """Create synthetic dataset if MNIST unavailable.

    Creates a harder classification problem with:
    - Limited training data (makes initialization critical)
    - Non-linear decision boundaries
    - High noise level
    """
    print("Creating synthetic dataset (MNIST fallback)...")
    print("  Creating limited-data, non-linear classification task...")

    # Create cluster centers in a lower-dimensional space
    latent_dim = 15
    cluster_centers = np.random.randn(n_classes, latent_dim).astype(np.float32) * 2.5

    # Generate random projection matrix
    projection = np.random.randn(latent_dim, n_features).astype(np.float32) / np.sqrt(latent_dim)

    # Generate samples
    X = np.zeros((n_samples, n_features), dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.int64)

    for i in range(n_samples):
        # Assign random class
        y[i] = np.random.randint(0, n_classes)

        # Generate point near cluster center with substantial noise
        latent = cluster_centers[y[i]] + np.random.randn(latent_dim).astype(np.float32) * 2.0

        # Project to high-dimensional space
        X[i] = latent @ projection

        # Add independent noise to make task harder
        X[i] += np.random.randn(n_features).astype(np.float32) * 0.5

    # Add non-linear transformations to make decision boundary harder
    X = X + 0.15 * np.sin(X * 1.5) + 0.1 * np.cos(X * 3.0)

    # Normalize
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    # Split train/test (smaller train set to stress initialization)
    n_train = int(0.7 * n_samples)
    indices = np.random.permutation(n_samples)
    train_idx, test_idx = indices[:n_train], indices[n_train:]

    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    return X_train, y_train, X_test, y_test


def load_dataset():
    """Load MNIST or fallback to synthetic data."""
    try:
        from torchvision import datasets, transforms

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])

        train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
        test_dataset = datasets.MNIST('./data', train=False, transform=transform)

        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
        test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

        print("Using MNIST dataset")
        return train_loader, test_loader, 'MNIST'

    except ImportError:
        print("torchvision not available, using synthetic data")
        X_train, y_train, X_test, y_test = create_synthetic_dataset()

        train_dataset = torch.utils.data.TensorDataset(
            torch.from_numpy(X_train),
            torch.from_numpy(y_train)
        )
        test_dataset = torch.utils.data.TensorDataset(
            torch.from_numpy(X_test),
            torch.from_numpy(y_test)
        )

        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
        test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

        return train_loader, test_loader, 'Synthetic'


def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for batch_idx, (data, target) in enumerate(dataloader):
        data, target = data.to(device), target.to(device)

        # Flatten images
        data = data.view(data.size(0), -1)

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += target.size(0)

    avg_loss = total_loss / len(dataloader)
    accuracy = 100. * correct / total
    return avg_loss, accuracy


def evaluate(model, dataloader, criterion, device):
    """Evaluate model on test set."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for data, target in dataloader:
            data, target = data.to(device), target.to(device)
            data = data.view(data.size(0), -1)

            output = model(data)
            loss = criterion(output, target)

            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)

    avg_loss = total_loss / len(dataloader)
    accuracy = 100. * correct / total
    return avg_loss, accuracy


def compute_initial_gradient_stats(model, dataloader, criterion, device):
    """Compute gradient statistics right after initialization."""
    model.train()

    # Get first batch
    data, target = next(iter(dataloader))
    data, target = data.to(device), target.to(device)
    data = data.view(data.size(0), -1)

    # Forward and backward pass
    output = model(data)
    loss = criterion(output, target)
    loss.backward()

    # Get stats
    return model.get_gradient_stats()


def run_single_experiment(scale_name, scale_fn, train_loader, test_loader,
                         num_epochs, device, seed):
    """Run single experiment with one initialization and seed."""
    # Set seed
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Create model
    model = TestNet(784, 256, 128, 10, scale_fn).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    # Compute initial gradient stats
    init_grad_stats = compute_initial_gradient_stats(model, train_loader, criterion, device)

    # Training loop
    train_losses = []
    train_accs = []
    test_losses = []
    test_accs = []

    start_time = time.time()

    for epoch in range(num_epochs):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, device)
        test_loss, test_acc = evaluate(model, test_loader, criterion, device)

        train_losses.append(train_loss)
        train_accs.append(train_acc)
        test_losses.append(test_loss)
        test_accs.append(test_acc)

        if (epoch + 1) % 5 == 0:
            print(f"  [{scale_name:8s} seed {seed}] Epoch {epoch+1:2d}/{num_epochs}: "
                  f"Train Acc: {train_acc:5.2f}%, Test Acc: {test_acc:5.2f}%")

    elapsed_time = time.time() - start_time

    # Compute convergence speed (epochs to reach 90% of final accuracy)
    final_acc = test_accs[-1]
    target_acc = 0.9 * final_acc
    convergence_epoch = num_epochs
    for i, acc in enumerate(test_accs):
        if acc >= target_acc:
            convergence_epoch = i + 1
            break

    return {
        'scale_name': scale_name,
        'seed': seed,
        'train_losses': train_losses,
        'train_accs': train_accs,
        'test_losses': test_losses,
        'test_accs': test_accs,
        'final_test_acc': test_accs[-1],
        'final_train_acc': train_accs[-1],
        'convergence_epoch': convergence_epoch,
        'init_grad_stats': init_grad_stats,
        'elapsed_time': elapsed_time
    }


def run_full_experiment(num_seeds=5, num_epochs=30):
    """Run complete experiment across all initializations and seeds."""
    print("="*80)
    print("PHI INITIALIZATION EXPERIMENT")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  - Number of seeds: {num_seeds}")
    print(f"  - Epochs per run: {num_epochs}")
    print(f"  - Initialization methods: {len(SCALES)}")
    print(f"  - Golden ratio phi: {PHI:.6f}")
    print(f"  - 1/phi: {INV_PHI:.6f}")
    print()

    # Load dataset
    train_loader, test_loader, dataset_name = load_dataset()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Dataset: {dataset_name}\n")

    # Run experiments
    all_results = {}

    for scale_name, scale_fn in SCALES.items():
        print(f"\nTesting initialization: {scale_name}")
        print("-" * 40)

        results_for_scale = []

        for seed in range(num_seeds):
            result = run_single_experiment(
                scale_name, scale_fn, train_loader, test_loader,
                num_epochs, device, seed
            )
            results_for_scale.append(result)

        all_results[scale_name] = results_for_scale

        # Compute summary statistics
        final_accs = [r['final_test_acc'] for r in results_for_scale]
        conv_epochs = [r['convergence_epoch'] for r in results_for_scale]

        print(f"\n  Summary for {scale_name}:")
        print(f"    Final accuracy: {np.mean(final_accs):.2f}% ± {np.std(final_accs):.2f}%")
        print(f"    Convergence: {np.mean(conv_epochs):.1f} ± {np.std(conv_epochs):.1f} epochs")

    return all_results, dataset_name, num_epochs


def save_results(all_results, dataset_name, num_epochs, output_path):
    """Save results to JSON file."""
    results_data = {
        'dataset': dataset_name,
        'num_epochs': num_epochs,
        'num_seeds': len(next(iter(all_results.values()))),
        'phi': PHI,
        'inv_phi': INV_PHI,
        'results': all_results
    }

    with open(output_path, 'w') as f:
        json.dump(results_data, f, indent=2)

    print(f"\nResults saved to: {output_path}")


def main():
    """Main entry point."""
    # Run experiment
    all_results, dataset_name, num_epochs = run_full_experiment(num_seeds=5, num_epochs=30)

    # Save raw results
    results_path = Path(__file__).parent / 'phi_init_results.json'
    save_results(all_results, dataset_name, num_epochs, results_path)

    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print(f"\nNext step: Analyze results and create report at:")
    print(f"  vacuum_physics/analysis/PHI_INITIALIZATION_RESULTS.md")


if __name__ == '__main__':
    main()
