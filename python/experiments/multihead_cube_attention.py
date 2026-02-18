"""
Multi-Head Cube-Topology Attention Experiment
==============================================
Tests whether arranging attention heads on a cube topology with sparse
phi-optimal message passing improves classification performance over
standard independent heads.

Theory: The self-referential optimization framework predicts that:
1. Inter-head communication structured on a 3-regular cube graph (8 vertices,
   12 edges, diameter 3) provides optimal information flow between heads.
2. The mixing parameter alpha = 1/phi^2 ~ 0.382 balances local head
   specialization against global coherence.
3. Sparse (3-neighbor) communication outperforms dense (all-to-all) because
   excessive coupling destroys the edge-of-chaos information processing.

Experiment design:
- Dataset: CIFAR-10 (small subset for CPU feasibility)
- Architecture: Tiny ViT (8x8 patches, embed_dim=32, 1 transformer layer)
- 4 configurations:
  1. Standard (independent heads)
  2. Cube topology (learnable alpha, init 0.382)
  3. Cube topology (fixed alpha = 0.382)
  4. All-to-all topology (learnable alpha, init 0.382)
- 3 random seeds per config, 8 epochs each
- Measurements: test accuracy, alpha convergence, training curves

Author: Claude (multi-head attention topology experiment)
"""

import sys
import io
import os
import time
import math

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
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
import torchvision
import torchvision.transforms as transforms
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# Constants
# ============================================================

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ~ 1.618
PHI_INV_SQ = 1.0 / (PHI ** 2)  # 1/phi^2 ~ 0.382

# Cube adjacency: 8 vertices labeled by 3-bit binary strings
# Edges connect vertices differing in exactly 1 bit
CUBE_ADJ = [
    [1, 2, 4],  # 000 -> 001, 010, 100
    [0, 3, 5],  # 001 -> 000, 011, 101
    [0, 3, 6],  # 010 -> 000, 011, 110
    [1, 2, 7],  # 011 -> 001, 010, 111
    [0, 5, 6],  # 100 -> 000, 101, 110
    [1, 4, 7],  # 101 -> 001, 100, 111
    [2, 4, 7],  # 110 -> 010, 100, 111
    [3, 5, 6],  # 111 -> 011, 101, 110
]

# All-to-all adjacency: each head connected to all 7 others
ALLTOALL_ADJ = [
    [j for j in range(8) if j != i] for i in range(8)
]

# Hyperparameters
EMBED_DIM = 32
NUM_HEADS = 8
HEAD_DIM = EMBED_DIM // NUM_HEADS  # 4
NUM_LAYERS = 1
PATCH_SIZE = 8  # 8x8 patches -> 16 patches (much faster attention)
IMG_SIZE = 32
NUM_PATCHES = (IMG_SIZE // PATCH_SIZE) ** 2  # 16
PATCH_DIM = 3 * PATCH_SIZE * PATCH_SIZE  # 192
NUM_CLASSES = 10
MESSAGE_ROUNDS = 3  # Cube diameter = 3

TRAIN_SIZE = 1000
TEST_SIZE = 500
BATCH_SIZE = 128
NUM_EPOCHS = 8
LR = 1e-3
NUM_SEEDS = 3

DEVICE = torch.device("cpu")

# ============================================================
# Custom Multi-Head Attention with Topology
# ============================================================

def build_adjacency_matrix(adj_list, num_nodes):
    """Build a normalized adjacency matrix from an adjacency list.

    Returns a (num_nodes, num_nodes) tensor where row i has 1/degree(i)
    at each neighbor column, and 0 elsewhere. This allows message passing
    via matrix multiplication: neighbor_avg = A @ head_outputs.
    """
    A = torch.zeros(num_nodes, num_nodes)
    for i in range(num_nodes):
        neighbors = adj_list[i]
        for j in neighbors:
            A[i, j] = 1.0 / len(neighbors)
    return A


class TopologyMultiHeadAttention(nn.Module):
    """
    Multi-head attention with optional inter-head message passing.

    topology: None (standard), 'cube', or 'alltoall'
    learnable_alpha: if True, alpha is a learnable parameter

    Message passing is fully vectorized using adjacency matrix multiplication
    for efficient CPU execution.
    """
    def __init__(self, embed_dim, num_heads, topology=None, learnable_alpha=True):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim

        # Q, K, V projections
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

        self.topology = topology
        self.learnable_alpha = learnable_alpha

        if topology == 'cube':
            adj_list = CUBE_ADJ
        elif topology == 'alltoall':
            adj_list = ALLTOALL_ADJ
        else:
            adj_list = None

        # Precompute normalized adjacency matrix as buffer (moves with device)
        if adj_list is not None:
            adj_matrix = build_adjacency_matrix(adj_list, num_heads)
            self.register_buffer('adj_matrix', adj_matrix)  # (H, H)

            if learnable_alpha:
                self.alpha = nn.Parameter(torch.tensor(PHI_INV_SQ))
            else:
                self.register_buffer('alpha', torch.tensor(PHI_INV_SQ))
        else:
            self.adj_matrix = None

        self.scale = math.sqrt(self.head_dim)

    def forward(self, x):
        """
        x: (batch, seq_len, embed_dim)
        Returns: (batch, seq_len, embed_dim)
        """
        B, S, D = x.shape

        # Compute Q, K, V
        Q = self.q_proj(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_proj(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_proj(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        # Q, K, V: (B, num_heads, S, head_dim)

        # Scaled dot-product attention
        attn_weights = torch.matmul(Q, K.transpose(-2, -1)) / self.scale  # (B, H, S, S)
        attn_weights = F.softmax(attn_weights, dim=-1)
        attn_output = torch.matmul(attn_weights, V)  # (B, H, S, head_dim)

        # Inter-head message passing (if topology specified)
        # Compute R-round diffusion matrix M = ((1-a)*I + a*A)^R as a single 8x8 matmul
        # Then apply: output = M @ output (via einsum over head dimension)
        if self.adj_matrix is not None:
            alpha = torch.clamp(self.alpha, 0.0, 1.0)
            # Build single-step transition: T = (1-alpha)*I + alpha*A
            I = torch.eye(self.num_heads, device=x.device)
            T = (1 - alpha) * I + alpha * self.adj_matrix  # (H, H)
            # R-round diffusion: M = T^R (8x8 matrix power, very cheap)
            M = T
            for _ in range(MESSAGE_ROUNDS - 1):
                M = M @ T
            # Apply diffusion: output[b,i,s,d] = sum_j M[i,j] * output[b,j,s,d]
            attn_output = torch.einsum('ij,bjsd->bisd', M, attn_output)

        # Concatenate heads and project
        attn_output = attn_output.transpose(1, 2).contiguous().view(B, S, D)
        output = self.out_proj(attn_output)
        return output


# ============================================================
# Vision Transformer Components
# ============================================================

class PatchEmbedding(nn.Module):
    """Convert image to sequence of patch embeddings."""
    def __init__(self, patch_size, embed_dim):
        super().__init__()
        self.patch_size = patch_size
        self.proj = nn.Linear(PATCH_DIM, embed_dim)

    def forward(self, x):
        # x: (B, 3, 32, 32)
        B = x.shape[0]
        # Unfold into patches
        patches = x.unfold(2, self.patch_size, self.patch_size).unfold(3, self.patch_size, self.patch_size)
        # patches: (B, 3, H_patches, W_patches, patch_size, patch_size)
        patches = patches.contiguous().view(B, 3, -1, self.patch_size, self.patch_size)
        # patches: (B, 3, num_patches, patch_size, patch_size)
        patches = patches.permute(0, 2, 1, 3, 4).contiguous().view(B, NUM_PATCHES, PATCH_DIM)
        # patches: (B, num_patches, patch_dim)
        return self.proj(patches)


class TransformerBlock(nn.Module):
    """Transformer block with topology-aware attention."""
    def __init__(self, embed_dim, num_heads, topology=None, learnable_alpha=True):
        super().__init__()
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = TopologyMultiHeadAttention(embed_dim, num_heads, topology, learnable_alpha)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 2),
            nn.GELU(),
            nn.Linear(embed_dim * 2, embed_dim),
        )

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        x = x + self.mlp(self.norm2(x))
        return x


class TinyViT(nn.Module):
    """Tiny Vision Transformer for CIFAR-10."""
    def __init__(self, topology=None, learnable_alpha=True):
        super().__init__()
        self.patch_embed = PatchEmbedding(PATCH_SIZE, EMBED_DIM)

        # Learnable positional embedding
        self.pos_embed = nn.Parameter(torch.randn(1, NUM_PATCHES + 1, EMBED_DIM) * 0.02)

        # CLS token
        self.cls_token = nn.Parameter(torch.randn(1, 1, EMBED_DIM) * 0.02)

        # Transformer layers
        self.layers = nn.ModuleList([
            TransformerBlock(EMBED_DIM, NUM_HEADS, topology, learnable_alpha)
            for _ in range(NUM_LAYERS)
        ])

        self.norm = nn.LayerNorm(EMBED_DIM)
        self.head = nn.Linear(EMBED_DIM, NUM_CLASSES)

        self.topology = topology

    def forward(self, x):
        B = x.shape[0]

        # Patch embedding
        x = self.patch_embed(x)  # (B, num_patches, embed_dim)

        # Prepend CLS token
        cls = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls, x], dim=1)  # (B, num_patches+1, embed_dim)

        # Add positional embedding
        x = x + self.pos_embed

        # Transformer layers
        for layer in self.layers:
            x = layer(x)

        # Classification from CLS token
        x = self.norm(x[:, 0])
        return self.head(x)

    def get_alphas(self):
        """Return current alpha values from attention layers."""
        alphas = []
        for layer in self.layers:
            if hasattr(layer.attn, 'alpha'):
                alphas.append(layer.attn.alpha.item())
        return alphas


# ============================================================
# Training and Evaluation
# ============================================================

def train_one_epoch(model, loader, optimizer, criterion):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    for images, labels in loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)
    return total_loss / total, correct / total


def evaluate(model, loader, criterion):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def run_experiment(config_name, topology, learnable_alpha, train_loader, test_loader, seed):
    """Run a single training run and return results."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    model = TinyViT(topology=topology, learnable_alpha=learnable_alpha).to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()

    n_params = count_parameters(model)

    train_losses = []
    train_accs = []
    test_losses = []
    test_accs = []
    alpha_history = []

    best_test_acc = 0.0

    for epoch in range(NUM_EPOCHS):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion)
        test_loss, test_acc = evaluate(model, test_loader, criterion)
        elapsed = time.time() - t0

        train_losses.append(train_loss)
        train_accs.append(train_acc)
        test_losses.append(test_loss)
        test_accs.append(test_acc)

        alphas = model.get_alphas()
        alpha_history.append(alphas)

        if test_acc > best_test_acc:
            best_test_acc = test_acc

        alpha_str = ""
        if alphas:
            alpha_str = f"  alpha=[{', '.join(f'{a:.4f}' for a in alphas)}]"

        print(f"  [{config_name}] Seed {seed} | Epoch {epoch+1:2d}/{NUM_EPOCHS} | "
              f"Train: {train_acc:.4f} | Test: {test_acc:.4f} | "
              f"Time: {elapsed:.1f}s{alpha_str}")

    return {
        'config': config_name,
        'seed': seed,
        'n_params': n_params,
        'best_test_acc': best_test_acc,
        'train_accs': train_accs,
        'test_accs': test_accs,
        'train_losses': train_losses,
        'test_losses': test_losses,
        'alpha_history': alpha_history,
    }


# ============================================================
# Plotting
# ============================================================

def plot_accuracy_bars(all_results, plots_dir):
    """Bar chart of test accuracy for all configs with error bars."""
    configs = ['Standard', 'Cube (learnable)', 'Cube (fixed)', 'All-to-All']

    means = []
    stds = []
    for config in configs:
        accs = [r['best_test_acc'] for r in all_results if r['config'] == config]
        means.append(np.mean(accs))
        stds.append(np.std(accs))

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(configs))
    colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']
    bars = ax.bar(x, means, yerr=stds, capsize=8, color=colors, edgecolor='black', linewidth=0.8)

    # Mark the winner
    best_idx = np.argmax(means)
    ax.bar(x[best_idx], means[best_idx], color=colors[best_idx], edgecolor='gold',
           linewidth=3, label=f'Best: {configs[best_idx]}')

    # Add value labels on bars
    for i, (m, s) in enumerate(zip(means, stds)):
        ax.text(i, m + s + 0.005, f'{m:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=11)
    ax.set_ylabel('Best Test Accuracy', fontsize=12)
    ax.set_title('Multi-Head Attention: Cube Topology vs Standard\n'
                 f'(CIFAR-10, embed_dim={EMBED_DIM}, {NUM_LAYERS} layers, {NUM_HEADS} heads, '
                 f'{NUM_SEEDS} seeds)', fontsize=13)
    ax.set_ylim(0, max(means) + max(stds) + 0.05)
    ax.axhline(y=0.1, color='gray', linestyle='--', alpha=0.5, label='Random chance (10%)')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    # Add parameter counts
    param_counts = {}
    for r in all_results:
        param_counts[r['config']] = r['n_params']
    param_text = "Parameters: " + ", ".join(f"{c}: {param_counts[c]:,}" for c in configs if c in param_counts)
    ax.text(0.5, -0.12, param_text, transform=ax.transAxes, ha='center', fontsize=9, color='gray')

    plt.tight_layout()
    path = os.path.join(plots_dir, 'multihead_cube_attention.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nSaved accuracy bar chart to {path}")


def plot_alpha_convergence(all_results, plots_dir):
    """Track learnable alpha across training epochs."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left plot: Cube topology alphas
    ax = axes[0]
    for r in all_results:
        if r['config'] == 'Cube (learnable)' and r['alpha_history']:
            epochs = range(1, NUM_EPOCHS + 1)
            for layer_idx in range(NUM_LAYERS):
                alphas = [ah[layer_idx] for ah in r['alpha_history']]
                label = f"Seed {r['seed']}, Layer {layer_idx}"
                ax.plot(epochs, alphas, marker='o', markersize=3, label=label, alpha=0.7)

    ax.axhline(y=PHI_INV_SQ, color='red', linestyle='--', linewidth=2,
               label=f'1/phi^2 = {PHI_INV_SQ:.4f}')
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('Alpha', fontsize=11)
    ax.set_title('Cube Topology: Learnable Alpha Convergence', fontsize=12)
    ax.legend(fontsize=8, loc='best')
    ax.grid(alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    # Right plot: All-to-All topology alphas
    ax = axes[1]
    for r in all_results:
        if r['config'] == 'All-to-All' and r['alpha_history']:
            epochs = range(1, NUM_EPOCHS + 1)
            for layer_idx in range(NUM_LAYERS):
                alphas = [ah[layer_idx] for ah in r['alpha_history']]
                label = f"Seed {r['seed']}, Layer {layer_idx}"
                ax.plot(epochs, alphas, marker='s', markersize=3, label=label, alpha=0.7)

    ax.axhline(y=PHI_INV_SQ, color='red', linestyle='--', linewidth=2,
               label=f'1/phi^2 = {PHI_INV_SQ:.4f}')
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('Alpha', fontsize=11)
    ax.set_title('All-to-All Topology: Learnable Alpha Convergence', fontsize=12)
    ax.legend(fontsize=8, loc='best')
    ax.grid(alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()
    path = os.path.join(plots_dir, 'multihead_alpha_convergence.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved alpha convergence plot to {path}")


def plot_training_curves(all_results, plots_dir):
    """Training curves for all configurations."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    configs = ['Standard', 'Cube (learnable)', 'Cube (fixed)', 'All-to-All']
    colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

    for ax_idx, (metric, title) in enumerate([('train_accs', 'Training Accuracy'),
                                                ('test_accs', 'Test Accuracy')]):
        ax = axes[ax_idx]
        for config, color in zip(configs, colors):
            runs = [r for r in all_results if r['config'] == config]
            if not runs:
                continue
            all_curves = np.array([r[metric] for r in runs])
            mean_curve = all_curves.mean(axis=0)
            std_curve = all_curves.std(axis=0)
            epochs = np.arange(1, NUM_EPOCHS + 1)
            ax.plot(epochs, mean_curve, color=color, label=config, linewidth=2)
            ax.fill_between(epochs, mean_curve - std_curve, mean_curve + std_curve,
                          color=color, alpha=0.15)

        ax.set_xlabel('Epoch', fontsize=11)
        ax.set_ylabel('Accuracy', fontsize=11)
        ax.set_title(title, fontsize=12)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)

    plt.suptitle('Training Curves: Cube Topology vs Standard Multi-Head Attention', fontsize=13, y=1.02)
    plt.tight_layout()
    path = os.path.join(plots_dir, 'multihead_training_curves.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved training curves to {path}")


# ============================================================
# Main
# ============================================================

class Tee:
    """Write to both stdout and a log file."""
    def __init__(self, log_path, original_stdout):
        self.log = open(log_path, 'w', encoding='utf-8', errors='replace')
        self.stdout = original_stdout
    def write(self, data):
        self.stdout.write(data)
        self.stdout.flush()
        self.log.write(data)
        self.log.flush()
    def flush(self):
        self.stdout.flush()
        self.log.flush()
    def close(self):
        self.log.close()


def main():
    # Setup log file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, "multihead_cube_attention.log")
    tee = Tee(log_path, sys.stdout)
    sys.stdout = tee

    print("=" * 70)
    print("Multi-Head Cube-Topology Attention Experiment")
    print("=" * 70)
    print(f"\nConstants:")
    print(f"  phi = {PHI:.6f}")
    print(f"  1/phi^2 = {PHI_INV_SQ:.6f}")
    print(f"  embed_dim = {EMBED_DIM}")
    print(f"  num_heads = {NUM_HEADS}, head_dim = {HEAD_DIM}")
    print(f"  num_layers = {NUM_LAYERS}")
    print(f"  patch_size = {PATCH_SIZE}, num_patches = {NUM_PATCHES}")
    print(f"  message_rounds = {MESSAGE_ROUNDS}")
    print(f"  train_size = {TRAIN_SIZE}, test_size = {TEST_SIZE}")
    print(f"  epochs = {NUM_EPOCHS}, batch_size = {BATCH_SIZE}")
    print(f"  seeds = {NUM_SEEDS}, lr = {LR}")
    print(f"  device = {DEVICE}")

    # Setup directories
    plots_dir = os.path.join(script_dir, "plots")
    data_dir = os.path.join(script_dir, "..", "..", "data")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    # Verify cube adjacency
    print("\nVerifying cube adjacency...")
    for i in range(8):
        assert len(CUBE_ADJ[i]) == 3, f"Vertex {i} has {len(CUBE_ADJ[i])} neighbors, expected 3"
        for j in CUBE_ADJ[i]:
            assert i in CUBE_ADJ[j], f"Adjacency not symmetric: {i} -> {j} but not {j} -> {i}"
            # Check Hamming distance = 1
            xor = i ^ j
            assert bin(xor).count('1') == 1, f"Vertices {i} and {j} differ in {bin(xor).count('1')} bits"
    total_edges = sum(len(adj) for adj in CUBE_ADJ) // 2
    assert total_edges == 12, f"Expected 12 edges, got {total_edges}"
    print(f"  Cube: 8 vertices, 12 edges, 3-regular -- OK")

    # Load CIFAR-10
    print("\nLoading CIFAR-10...")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
    ])

    train_dataset = torchvision.datasets.CIFAR10(
        root=data_dir, train=True, download=True, transform=transform
    )
    test_dataset = torchvision.datasets.CIFAR10(
        root=data_dir, train=False, download=True, transform=transform
    )

    # Use fixed subset indices for reproducibility
    rng = np.random.RandomState(42)
    train_indices = rng.choice(len(train_dataset), TRAIN_SIZE, replace=False)
    test_indices = rng.choice(len(test_dataset), TEST_SIZE, replace=False)

    train_subset = Subset(train_dataset, train_indices)
    test_subset = Subset(test_dataset, test_indices)

    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    print(f"  Train: {len(train_subset)} samples, Test: {len(test_subset)} samples")

    # Count params for each config
    print("\nParameter counts:")
    for name, topo, la in [('Standard', None, True), ('Cube (learnable)', 'cube', True),
                            ('Cube (fixed)', 'cube', False), ('All-to-All', 'alltoall', True)]:
        m = TinyViT(topology=topo, learnable_alpha=la)
        n = count_parameters(m)
        print(f"  {name}: {n:,} parameters")

    # Run all experiments
    configs = [
        ('Standard', None, True),
        ('Cube (learnable)', 'cube', True),
        ('Cube (fixed)', 'cube', False),
        ('All-to-All', 'alltoall', True),
    ]

    seeds = list(range(NUM_SEEDS))
    all_results = []

    total_runs = len(configs) * NUM_SEEDS
    run_idx = 0
    experiment_start = time.time()

    for config_name, topology, learnable_alpha in configs:
        print(f"\n{'=' * 60}")
        print(f"Config: {config_name}")
        print(f"{'=' * 60}")

        for seed in seeds:
            run_idx += 1
            print(f"\n--- Run {run_idx}/{total_runs}: {config_name}, seed={seed} ---")
            t0 = time.time()
            result = run_experiment(config_name, topology, learnable_alpha,
                                   train_loader, test_loader, seed)
            elapsed = time.time() - t0
            print(f"  Completed in {elapsed:.1f}s | Best test acc: {result['best_test_acc']:.4f}")
            all_results.append(result)

    total_time = time.time() - experiment_start

    # ============================================================
    # Analysis
    # ============================================================

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    config_names = ['Standard', 'Cube (learnable)', 'Cube (fixed)', 'All-to-All']

    print(f"\n{'Config':<22} {'Mean Acc':>10} {'Std':>8} {'Best':>8} {'Params':>10}")
    print("-" * 62)

    summary = {}
    for config in config_names:
        runs = [r for r in all_results if r['config'] == config]
        accs = [r['best_test_acc'] for r in runs]
        mean_acc = np.mean(accs)
        std_acc = np.std(accs)
        best_acc = np.max(accs)
        n_params = runs[0]['n_params']
        summary[config] = {'mean': mean_acc, 'std': std_acc, 'best': best_acc, 'n_params': n_params}
        print(f"  {config:<20} {mean_acc:>10.4f} {std_acc:>8.4f} {best_acc:>8.4f} {n_params:>10,}")

    # Alpha convergence analysis
    print(f"\n{'=' * 70}")
    print("ALPHA CONVERGENCE ANALYSIS")
    print(f"{'=' * 70}")
    print(f"  Target (1/phi^2): {PHI_INV_SQ:.4f}")

    for config in ['Cube (learnable)', 'All-to-All']:
        runs = [r for r in all_results if r['config'] == config]
        final_alphas = []
        for r in runs:
            if r['alpha_history']:
                for layer_idx in range(NUM_LAYERS):
                    final_alphas.append(r['alpha_history'][-1][layer_idx])
        if final_alphas:
            mean_alpha = np.mean(final_alphas)
            std_alpha = np.std(final_alphas)
            print(f"\n  {config}:")
            print(f"    Final alpha (mean +/- std): {mean_alpha:.4f} +/- {std_alpha:.4f}")
            print(f"    Distance from 1/phi^2: {abs(mean_alpha - PHI_INV_SQ):.4f}")

    # Key findings
    print(f"\n{'=' * 70}")
    print("KEY FINDINGS")
    print(f"{'=' * 70}")

    # Q1: Does cube beat standard?
    cube_mean = summary['Cube (learnable)']['mean']
    std_mean = summary['Standard']['mean']
    diff1 = cube_mean - std_mean
    print(f"\n  1. Cube vs Standard: {'+' if diff1 > 0 else ''}{diff1:.4f} "
          f"({'Cube wins' if diff1 > 0 else 'Standard wins'})")

    # Q2: Does cube beat all-to-all?
    a2a_mean = summary['All-to-All']['mean']
    diff2 = cube_mean - a2a_mean
    print(f"  2. Cube vs All-to-All: {'+' if diff2 > 0 else ''}{diff2:.4f} "
          f"({'Sparse wins' if diff2 > 0 else 'Dense wins'})")

    # Q3: Does fixed alpha match learnable?
    fixed_mean = summary['Cube (fixed)']['mean']
    diff3 = fixed_mean - cube_mean
    print(f"  3. Fixed alpha vs Learnable: {'+' if diff3 > 0 else ''}{diff3:.4f} "
          f"({'Fixed wins' if diff3 > 0 else 'Learnable wins'})")

    # Best overall
    best_config = max(config_names, key=lambda c: summary[c]['mean'])
    print(f"\n  Best overall: {best_config} (mean acc = {summary[best_config]['mean']:.4f})")

    print(f"\n  Total experiment time: {total_time:.1f}s ({total_time/60:.1f} min)")

    # ============================================================
    # Plots
    # ============================================================

    print(f"\n{'=' * 70}")
    print("GENERATING PLOTS")
    print(f"{'=' * 70}")

    plot_accuracy_bars(all_results, plots_dir)
    plot_alpha_convergence(all_results, plots_dir)
    plot_training_curves(all_results, plots_dir)

    print(f"\nAll plots saved to {plots_dir}")
    print("\nExperiment complete!")

    # Restore stdout
    sys.stdout = tee.stdout
    tee.close()
    print(f"Log saved to {log_path}")


if __name__ == "__main__":
    main()
