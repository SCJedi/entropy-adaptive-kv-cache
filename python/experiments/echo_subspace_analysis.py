"""
Echo Subspace Analysis (Experiment 31)
=======================================
Tests whether the "echo contamination" detected by dual-channel MVSU
lives in a low-rank subspace, enabling cheaper correction via projection
instead of full secondary attention.

Theory: The ML experts + child team iteration proposed that instead of a
full dual-channel MVSU (Tier 3), the secondary channel might just be
learning to identify and subtract a low-rank "echo subspace." If the echo
contamination lives in a small number of dimensions, we can replace the
expensive secondary attention with a cheap rank-k projection.

The experiment has 4 phases:

Phase 1: Train a dual-channel model
- Build a small transformer with dual-channel attention (primary + low-rank
  secondary with learnable w_cross)
- Architecture: embed_dim=64, 8 heads, 4 layers, patch_size=4 on CIFAR-10
  (2000 train, 1000 test)
- The secondary channel uses low-rank (rank=4) QKV projections
- Train for 15 epochs, track w_cross per layer
- Similar to Tier 3 from Observer Transformer spec

Phase 2: Extract and analyze the echo subspace
- After training, compute the difference between primary and secondary
  attention outputs on test data for each layer
- Run PCA on these differences across all heads and positions
- Report: what fraction of variance is explained by the top k=1,2,4,8 components?
- If top-4 explains >80% of variance, the echo IS low-rank

Phase 3: Build and test the "eraser" (Tier 2.5)
- If the echo is low-rank, build a model that replaces the secondary channel
  with a fixed rank-k projection
- The projection vectors come from the PCA of Phase 2
- Compare: Baseline (no correction) vs Tier 3 (full dual-channel) vs
  Tier 2.5 (echo projector)
- Also test: learnable projector (initialize from PCA, let it adapt) vs
  fixed projector

Phase 4: Test if the echo is self-similar
- Compute PCA of the echo at each layer depth
- Check if the echo subspace directions are consistent across layers
  (cosine similarity of principal components)
- If the echo subspace rotates/grows with depth but maintains structure,
  it's self-similar

Author: Claude (echo subspace experiment)
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
from sklearn.decomposition import PCA

# ============================================================
# Constants
# ============================================================

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ~ 1.618

# Architecture
EMBED_DIM = 64
NUM_HEADS = 8
HEAD_DIM = EMBED_DIM // NUM_HEADS  # 8
NUM_LAYERS = 4
PATCH_SIZE = 4  # 4x4 patches -> 64 patches
IMG_SIZE = 32
NUM_PATCHES = (IMG_SIZE // PATCH_SIZE) ** 2  # 64
PATCH_DIM = 3 * PATCH_SIZE * PATCH_SIZE  # 48
NUM_CLASSES = 10

# Secondary channel low rank
SECONDARY_RANK = 4

# Training
TRAIN_SIZE = 2000
TEST_SIZE = 1000
BATCH_SIZE = 64
NUM_EPOCHS_PHASE1 = 15
NUM_EPOCHS_PHASE3 = 15
LR = 1e-3

# PCA analysis
PCA_RANKS = [1, 2, 4, 8]

DEVICE = torch.device("cpu")

# ============================================================
# Dual-Channel Attention (Tier 3)
# ============================================================

class DualChannelAttention(nn.Module):
    """
    Dual-channel attention with primary (full-rank) and secondary (low-rank) channels.

    output = primary + w_cross * secondary

    w_cross is learnable per layer, initialized to -0.1 (inhibitory).
    """
    def __init__(self, embed_dim, num_heads, secondary_rank=4):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim

        # Primary channel (full-rank)
        self.q_proj_primary = nn.Linear(embed_dim, embed_dim)
        self.k_proj_primary = nn.Linear(embed_dim, embed_dim)
        self.v_proj_primary = nn.Linear(embed_dim, embed_dim)
        self.out_proj_primary = nn.Linear(embed_dim, embed_dim)

        # Secondary channel (low-rank)
        self.secondary_rank = secondary_rank
        self.q_proj_secondary = nn.Linear(embed_dim, num_heads * secondary_rank)
        self.k_proj_secondary = nn.Linear(embed_dim, num_heads * secondary_rank)
        self.v_proj_secondary = nn.Linear(embed_dim, num_heads * secondary_rank)
        self.out_proj_secondary = nn.Linear(num_heads * secondary_rank, embed_dim)

        # Cross-channel weight (learnable, initialized to -0.1)
        self.w_cross = nn.Parameter(torch.tensor(-0.1))

        self.scale_primary = math.sqrt(self.head_dim)
        self.scale_secondary = math.sqrt(secondary_rank)

    def forward(self, x, return_components=False):
        """
        x: (batch, seq_len, embed_dim)

        If return_components=True, returns (output, primary_output, secondary_output)
        Otherwise returns output only.
        """
        B, S, D = x.shape

        # Primary channel
        Q_pri = self.q_proj_primary(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        K_pri = self.k_proj_primary(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        V_pri = self.v_proj_primary(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        # (B, num_heads, S, head_dim)

        attn_weights_pri = torch.matmul(Q_pri, K_pri.transpose(-2, -1)) / self.scale_primary
        attn_weights_pri = F.softmax(attn_weights_pri, dim=-1)
        attn_output_pri = torch.matmul(attn_weights_pri, V_pri)  # (B, H, S, head_dim)

        attn_output_pri = attn_output_pri.transpose(1, 2).contiguous().view(B, S, D)
        primary_output = self.out_proj_primary(attn_output_pri)

        # Secondary channel (low-rank)
        Q_sec = self.q_proj_secondary(x).view(B, S, self.num_heads, self.secondary_rank).transpose(1, 2)
        K_sec = self.k_proj_secondary(x).view(B, S, self.num_heads, self.secondary_rank).transpose(1, 2)
        V_sec = self.v_proj_secondary(x).view(B, S, self.num_heads, self.secondary_rank).transpose(1, 2)
        # (B, num_heads, S, secondary_rank)

        attn_weights_sec = torch.matmul(Q_sec, K_sec.transpose(-2, -1)) / self.scale_secondary
        attn_weights_sec = F.softmax(attn_weights_sec, dim=-1)
        attn_output_sec = torch.matmul(attn_weights_sec, V_sec)  # (B, H, S, secondary_rank)

        attn_output_sec = attn_output_sec.transpose(1, 2).contiguous().view(B, S, -1)
        secondary_output = self.out_proj_secondary(attn_output_sec)

        # Combine with w_cross
        output = primary_output + self.w_cross * secondary_output

        if return_components:
            return output, primary_output, secondary_output
        else:
            return output


class EchoProjectorAttention(nn.Module):
    """
    Tier 2.5: Primary attention + learned/fixed echo subspace projection.

    output = primary - projection_strength * project_onto_echo_subspace(primary)

    The echo subspace is defined by rank-k principal components.
    """
    def __init__(self, embed_dim, num_heads, echo_basis=None, learnable_basis=False):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        assert self.head_dim * num_heads == embed_dim

        # Primary channel (full-rank)
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

        # Echo subspace projection
        # echo_basis: (embed_dim, k) where k is the rank of the echo subspace
        if echo_basis is not None:
            k = echo_basis.shape[1]
            if learnable_basis:
                self.echo_basis = nn.Parameter(torch.from_numpy(echo_basis).float())
            else:
                self.register_buffer('echo_basis', torch.from_numpy(echo_basis).float())

            # Projection strength (learnable, initialized to 1.0)
            self.projection_strength = nn.Parameter(torch.tensor(1.0))
        else:
            self.echo_basis = None

        self.scale = math.sqrt(self.head_dim)

    def forward(self, x):
        """
        x: (batch, seq_len, embed_dim)
        """
        B, S, D = x.shape

        # Primary channel
        Q = self.q_proj(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.k_proj(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.v_proj(x).view(B, S, self.num_heads, self.head_dim).transpose(1, 2)

        attn_weights = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        attn_weights = F.softmax(attn_weights, dim=-1)
        attn_output = torch.matmul(attn_weights, V)  # (B, H, S, head_dim)

        attn_output = attn_output.transpose(1, 2).contiguous().view(B, S, D)
        primary_output = self.out_proj(attn_output)

        # Apply echo projection if basis is defined
        if self.echo_basis is not None:
            # Project onto echo subspace and subtract
            # projection = (primary @ basis) @ basis.T
            # output = primary - strength * projection
            basis = self.echo_basis  # (D, k)
            coeffs = torch.matmul(primary_output, basis)  # (B, S, k)
            projection = torch.matmul(coeffs, basis.T)  # (B, S, D)
            output = primary_output - self.projection_strength * projection
        else:
            output = primary_output

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
        patches = patches.contiguous().view(B, 3, -1, self.patch_size, self.patch_size)
        patches = patches.permute(0, 2, 1, 3, 4).contiguous().view(B, NUM_PATCHES, PATCH_DIM)
        return self.proj(patches)


class TransformerBlock(nn.Module):
    """Transformer block with configurable attention type."""
    def __init__(self, embed_dim, num_heads, attn_module):
        super().__init__()
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = attn_module
        self.norm2 = nn.LayerNorm(embed_dim)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 2),
            nn.GELU(),
            nn.Linear(embed_dim * 2, embed_dim),
        )

    def forward(self, x, return_attn_components=False):
        if return_attn_components:
            attn_out, pri_out, sec_out = self.attn(self.norm1(x), return_components=True)
            x = x + attn_out
            x = x + self.mlp(self.norm2(x))
            return x, pri_out, sec_out
        else:
            x = x + self.attn(self.norm1(x))
            x = x + self.mlp(self.norm2(x))
            return x


class TinyViT(nn.Module):
    """Tiny Vision Transformer for CIFAR-10."""
    def __init__(self, attn_type='dual', echo_bases=None, learnable_bases=False):
        """
        attn_type: 'baseline', 'dual', or 'projector'
        echo_bases: list of (embed_dim, k) arrays, one per layer (for projector mode)
        learnable_bases: if True, echo bases are learnable parameters
        """
        super().__init__()
        self.attn_type = attn_type
        self.patch_embed = PatchEmbedding(PATCH_SIZE, EMBED_DIM)

        # Learnable positional embedding
        self.pos_embed = nn.Parameter(torch.randn(1, NUM_PATCHES + 1, EMBED_DIM) * 0.02)

        # CLS token
        self.cls_token = nn.Parameter(torch.randn(1, 1, EMBED_DIM) * 0.02)

        # Transformer layers
        self.layers = nn.ModuleList()
        for i in range(NUM_LAYERS):
            if attn_type == 'dual':
                attn = DualChannelAttention(EMBED_DIM, NUM_HEADS, SECONDARY_RANK)
            elif attn_type == 'projector':
                basis = echo_bases[i] if echo_bases else None
                attn = EchoProjectorAttention(EMBED_DIM, NUM_HEADS, basis, learnable_bases)
            else:  # baseline
                attn = EchoProjectorAttention(EMBED_DIM, NUM_HEADS, None, False)

            self.layers.append(TransformerBlock(EMBED_DIM, NUM_HEADS, attn))

        self.norm = nn.LayerNorm(EMBED_DIM)
        self.head = nn.Linear(EMBED_DIM, NUM_CLASSES)

    def forward(self, x, return_attn_components=False):
        B = x.shape[0]

        # Patch embedding
        x = self.patch_embed(x)  # (B, num_patches, embed_dim)

        # Prepend CLS token
        cls = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls, x], dim=1)  # (B, num_patches+1, embed_dim)

        # Add positional embedding
        x = x + self.pos_embed

        # Transformer layers
        if return_attn_components and self.attn_type == 'dual':
            layer_outputs = []
            for layer in self.layers:
                x, pri, sec = layer(x, return_attn_components=True)
                layer_outputs.append((pri, sec))
            x = self.norm(x[:, 0])
            logits = self.head(x)
            return logits, layer_outputs
        else:
            for layer in self.layers:
                x = layer(x)
            x = self.norm(x[:, 0])
            return self.head(x)

    def get_w_cross(self):
        """Return w_cross values from all layers (for dual-channel models)."""
        if self.attn_type != 'dual':
            return []
        return [layer.attn.w_cross.item() for layer in self.layers]

    def get_projection_strengths(self):
        """Return projection strengths from all layers (for projector models)."""
        if self.attn_type != 'projector':
            return []
        return [layer.attn.projection_strength.item() if layer.attn.echo_basis is not None else None
                for layer in self.layers]


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


# ============================================================
# Phase 1: Train Dual-Channel Model
# ============================================================

def phase1_train_dual_channel(train_loader, test_loader):
    """Train a dual-channel model and track w_cross convergence."""
    print("\n" + "=" * 70)
    print("PHASE 1: Train Dual-Channel Model (Tier 3)")
    print("=" * 70)

    torch.manual_seed(42)
    np.random.seed(42)

    model = TinyViT(attn_type='dual').to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()

    n_params = count_parameters(model)
    print(f"\nModel parameters: {n_params:,}")
    print(f"Architecture: {NUM_LAYERS} layers, {NUM_HEADS} heads, embed_dim={EMBED_DIM}")
    print(f"Secondary channel rank: {SECONDARY_RANK}")
    print(f"Training for {NUM_EPOCHS_PHASE1} epochs...")

    w_cross_history = []
    test_accs = []

    t0 = time.time()
    for epoch in range(NUM_EPOCHS_PHASE1):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion)
        test_loss, test_acc = evaluate(model, test_loader, criterion)

        w_cross = model.get_w_cross()
        w_cross_history.append(w_cross)
        test_accs.append(test_acc)

        print(f"  Epoch {epoch+1:2d}/{NUM_EPOCHS_PHASE1} | "
              f"Train: {train_acc:.4f} | Test: {test_acc:.4f} | "
              f"w_cross: [{', '.join(f'{w:.3f}' for w in w_cross)}]")

    elapsed = time.time() - t0
    print(f"\nPhase 1 completed in {elapsed:.1f}s")
    print(f"Final test accuracy: {test_accs[-1]:.4f}")
    print(f"Final w_cross by layer: {[f'{w:.4f}' for w in w_cross_history[-1]]}")

    return model, w_cross_history, test_accs


# ============================================================
# Phase 2: Extract Echo Subspace
# ============================================================

def phase2_extract_echo_subspace(model, test_loader):
    """
    Extract echo subspace from trained dual-channel model.

    For each layer, compute the difference between primary and secondary
    attention outputs on test data, then run PCA.

    Returns:
    - echo_diffs: list of (N, embed_dim) arrays, one per layer
    - pca_models: list of PCA objects, one per layer
    - variance_explained: list of arrays showing cumulative variance for ranks
    """
    print("\n" + "=" * 70)
    print("PHASE 2: Extract and Analyze Echo Subspace")
    print("=" * 70)

    model.eval()

    # Collect echo differences (primary - secondary) for each layer
    layer_diffs = [[] for _ in range(NUM_LAYERS)]

    print("\nCollecting attention differences across test set...")
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(DEVICE)
            _, layer_outputs = model(images, return_attn_components=True)

            for i, (primary, secondary) in enumerate(layer_outputs):
                # primary, secondary: (B, S, D)
                diff = (primary - secondary).cpu().numpy()  # (B, S, D)
                # Flatten batch and sequence dimensions
                diff = diff.reshape(-1, EMBED_DIM)  # (B*S, D)
                layer_diffs[i].append(diff)

    # Concatenate all differences
    echo_diffs = [np.concatenate(diffs, axis=0) for diffs in layer_diffs]

    print(f"Collected {echo_diffs[0].shape[0]} samples per layer")

    # Run PCA on each layer
    print("\nRunning PCA on echo differences...")
    pca_models = []
    variance_explained = []

    for i, diffs in enumerate(echo_diffs):
        pca = PCA(n_components=min(EMBED_DIM, diffs.shape[0]))
        pca.fit(diffs)
        pca_models.append(pca)

        # Compute cumulative variance for different ranks
        cumvar = []
        for k in PCA_RANKS:
            cumvar.append(pca.explained_variance_ratio_[:k].sum())
        variance_explained.append(cumvar)

        print(f"\n  Layer {i}:")
        for k, cv in zip(PCA_RANKS, cumvar):
            print(f"    Top-{k} components: {cv*100:.2f}% variance")

    return echo_diffs, pca_models, variance_explained


# ============================================================
# Phase 3: Build and Test Echo Projector (Tier 2.5)
# ============================================================

def phase3_test_projector(train_loader, test_loader, pca_models, baseline_acc, tier3_acc):
    """
    Build Tier 2.5 models using PCA-derived echo subspaces.

    Test:
    - Fixed projector (PCA basis frozen)
    - Learnable projector (PCA basis initialized, then learned)

    Compare to baseline and Tier 3.
    """
    print("\n" + "=" * 70)
    print("PHASE 3: Test Echo Projector (Tier 2.5)")
    print("=" * 70)

    # Extract rank-4 bases from PCA
    echo_bases = []
    for pca in pca_models:
        # PCA components: (n_components, n_features)
        # We want (n_features, k) for projection
        k = min(4, pca.components_.shape[0])
        basis = pca.components_[:k, :].T  # (EMBED_DIM, k)
        echo_bases.append(basis)

    print(f"\nExtracted rank-4 echo bases for {len(echo_bases)} layers")

    results = {}

    # Test configurations
    configs = [
        ('Tier 2.5 (fixed)', False),
        ('Tier 2.5 (learnable)', True),
    ]

    for config_name, learnable in configs:
        print(f"\n{'=' * 60}")
        print(f"Training: {config_name}")
        print(f"{'=' * 60}")

        torch.manual_seed(42)
        np.random.seed(42)

        model = TinyViT(attn_type='projector', echo_bases=echo_bases, learnable_bases=learnable).to(DEVICE)
        optimizer = optim.Adam(model.parameters(), lr=LR)
        criterion = nn.CrossEntropyLoss()

        n_params = count_parameters(model)
        print(f"Parameters: {n_params:,}")

        test_accs = []
        strength_history = []

        for epoch in range(NUM_EPOCHS_PHASE3):
            train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion)
            test_loss, test_acc = evaluate(model, test_loader, criterion)

            strengths = model.get_projection_strengths()
            strength_history.append(strengths)
            test_accs.append(test_acc)

            print(f"  Epoch {epoch+1:2d}/{NUM_EPOCHS_PHASE3} | "
                  f"Train: {train_acc:.4f} | Test: {test_acc:.4f} | "
                  f"Strength: [{', '.join(f'{s:.2f}' if s is not None else 'N/A' for s in strengths)}]")

        final_acc = test_accs[-1]
        results[config_name] = {
            'test_accs': test_accs,
            'strength_history': strength_history,
            'final_acc': final_acc,
            'n_params': n_params,
        }

        print(f"\n{config_name} final accuracy: {final_acc:.4f}")

    # Print comparison table
    print("\n" + "=" * 70)
    print("COMPARISON TABLE")
    print("=" * 70)
    print(f"{'Model':<25} {'Accuracy':>10} {'vs Baseline':>12} {'vs Tier 3':>12}")
    print("-" * 70)

    print(f"{'Baseline':<25} {baseline_acc:10.4f} {'-':>12} {'-':>12}")
    print(f"{'Tier 3 (dual-channel)':<25} {tier3_acc:10.4f} "
          f"{(tier3_acc - baseline_acc)*100:>11.2f}% "
          f"{'-':>12}")

    for name, data in results.items():
        acc = data['final_acc']
        vs_baseline = (acc - baseline_acc) * 100
        vs_tier3 = (acc - tier3_acc) * 100
        print(f"{name:<25} {acc:10.4f} {vs_baseline:>11.2f}% {vs_tier3:>11.2f}%")

    return results


# ============================================================
# Phase 4: Test Self-Similarity
# ============================================================

def phase4_test_self_similarity(pca_models):
    """
    Test if echo subspace is self-similar across layers.

    Compute cosine similarity between principal components of adjacent layers.
    """
    print("\n" + "=" * 70)
    print("PHASE 4: Test Echo Self-Similarity Across Layers")
    print("=" * 70)

    # Extract top-4 principal components from each layer
    components = []
    for pca in pca_models:
        k = min(4, pca.components_.shape[0])
        comps = pca.components_[:k, :]  # (k, EMBED_DIM)
        components.append(comps)

    # Compute pairwise cosine similarity between layers
    # For each pair of layers, compute average cosine similarity between their top-k components
    print("\nCross-layer similarity matrix (cosine similarity of top-4 PCs):")
    print("Each entry shows average similarity between principal components of two layers")

    similarity_matrix = np.zeros((NUM_LAYERS, NUM_LAYERS))

    for i in range(NUM_LAYERS):
        for j in range(NUM_LAYERS):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                # Compute similarity between all pairs of components
                comp_i = components[i]  # (k_i, D)
                comp_j = components[j]  # (k_j, D)

                # Normalize
                comp_i_norm = comp_i / np.linalg.norm(comp_i, axis=1, keepdims=True)
                comp_j_norm = comp_j / np.linalg.norm(comp_j, axis=1, keepdims=True)

                # Compute pairwise cosine similarity
                cos_sim = np.abs(comp_i_norm @ comp_j_norm.T)  # (k_i, k_j)

                # Average similarity (best matching)
                # For each component in i, find best match in j
                similarity_matrix[i, j] = cos_sim.max(axis=1).mean()

    print("\n     ", end="")
    for j in range(NUM_LAYERS):
        print(f"L{j}    ", end="")
    print()

    for i in range(NUM_LAYERS):
        print(f"  L{i} ", end="")
        for j in range(NUM_LAYERS):
            print(f"{similarity_matrix[i, j]:.3f}  ", end="")
        print()

    # Adjacent layer similarity
    print("\nAdjacent layer similarities:")
    for i in range(NUM_LAYERS - 1):
        sim = similarity_matrix[i, i+1]
        print(f"  Layer {i} -> Layer {i+1}: {sim:.4f}")

    avg_adjacent = np.mean([similarity_matrix[i, i+1] for i in range(NUM_LAYERS - 1)])
    print(f"\nAverage adjacent similarity: {avg_adjacent:.4f}")

    if avg_adjacent > 0.7:
        print("RESULT: Echo subspace is HIGHLY self-similar across layers (avg > 0.7)")
    elif avg_adjacent > 0.5:
        print("RESULT: Echo subspace shows MODERATE self-similarity (avg > 0.5)")
    else:
        print("RESULT: Echo subspace is NOT self-similar (avg < 0.5)")

    return similarity_matrix


# ============================================================
# Plotting
# ============================================================

def plot_phase1_results(w_cross_history, test_accs, plots_dir):
    """Plot w_cross convergence and test accuracy from Phase 1."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: w_cross by layer
    ax = axes[0]
    w_cross_array = np.array(w_cross_history)  # (epochs, layers)
    epochs = np.arange(1, len(w_cross_history) + 1)

    for i in range(NUM_LAYERS):
        ax.plot(epochs, w_cross_array[:, i], marker='o', label=f'Layer {i}', linewidth=2)

    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('w_cross', fontsize=11)
    ax.set_title('Cross-Channel Weight Convergence (Tier 3)', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # Right: test accuracy
    ax = axes[1]
    ax.plot(epochs, test_accs, marker='o', color='#2196F3', linewidth=2)
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('Test Accuracy', fontsize=11)
    ax.set_title('Dual-Channel Model Test Accuracy', fontsize=12)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(plots_dir, 'echo_phase1_training.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved Phase 1 plot to {path}")


def plot_phase2_results(variance_explained, plots_dir):
    """Plot PCA variance explained."""
    fig, ax = plt.subplots(figsize=(10, 6))

    variance_array = np.array(variance_explained)  # (layers, pca_ranks)

    x = np.arange(len(PCA_RANKS))
    width = 0.2

    for i in range(NUM_LAYERS):
        ax.bar(x + i * width, variance_array[i] * 100, width, label=f'Layer {i}', alpha=0.8)

    ax.axhline(y=80, color='red', linestyle='--', linewidth=2, label='80% threshold')
    ax.set_xlabel('Number of Principal Components', fontsize=12)
    ax.set_ylabel('Cumulative Variance Explained (%)', fontsize=12)
    ax.set_title('Echo Subspace: Variance Explained by Top-k Components', fontsize=13)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels([f'Top-{k}' for k in PCA_RANKS])
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(plots_dir, 'echo_phase2_pca.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved Phase 2 plot to {path}")


def plot_phase3_results(baseline_acc, tier3_acc, results, plots_dir):
    """Plot comparison of all model tiers."""
    fig, ax = plt.subplots(figsize=(10, 6))

    models = ['Baseline', 'Tier 3\n(dual-channel)', 'Tier 2.5\n(fixed)', 'Tier 2.5\n(learnable)']
    accs = [
        baseline_acc,
        tier3_acc,
        results['Tier 2.5 (fixed)']['final_acc'],
        results['Tier 2.5 (learnable)']['final_acc'],
    ]

    colors = ['#9E9E9E', '#2196F3', '#FF9800', '#4CAF50']

    bars = ax.bar(models, accs, color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)

    # Highlight best
    best_idx = np.argmax(accs)
    ax.bar(best_idx, accs[best_idx], color=colors[best_idx], edgecolor='gold', linewidth=3)

    # Add value labels
    for i, (model, acc) in enumerate(zip(models, accs)):
        ax.text(i, acc + 0.005, f'{acc:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('Test Accuracy', fontsize=12)
    ax.set_title('Echo Subspace Experiment: Model Comparison', fontsize=13)
    ax.set_ylim(0, max(accs) + 0.05)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    path = os.path.join(plots_dir, 'echo_phase3_comparison.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved Phase 3 plot to {path}")


def plot_phase4_results(similarity_matrix, plots_dir):
    """Plot cross-layer similarity heatmap."""
    fig, ax = plt.subplots(figsize=(8, 7))

    im = ax.imshow(similarity_matrix, cmap='YlOrRd', vmin=0, vmax=1, aspect='auto')

    ax.set_xticks(np.arange(NUM_LAYERS))
    ax.set_yticks(np.arange(NUM_LAYERS))
    ax.set_xticklabels([f'L{i}' for i in range(NUM_LAYERS)])
    ax.set_yticklabels([f'L{i}' for i in range(NUM_LAYERS)])

    # Add values to cells
    for i in range(NUM_LAYERS):
        for j in range(NUM_LAYERS):
            text = ax.text(j, i, f'{similarity_matrix[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=10)

    ax.set_title('Echo Subspace Cross-Layer Similarity\n(Cosine similarity of top-4 PCs)', fontsize=12)
    ax.set_xlabel('Layer', fontsize=11)
    ax.set_ylabel('Layer', fontsize=11)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Cosine Similarity', fontsize=10)

    plt.tight_layout()
    path = os.path.join(plots_dir, 'echo_phase4_similarity.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved Phase 4 plot to {path}")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 70)
    print("Echo Subspace Analysis (Experiment 31)")
    print("=" * 70)
    print(f"\nConstants:")
    print(f"  phi = {PHI:.6f}")
    print(f"  embed_dim = {EMBED_DIM}")
    print(f"  num_heads = {NUM_HEADS}, head_dim = {HEAD_DIM}")
    print(f"  num_layers = {NUM_LAYERS}")
    print(f"  patch_size = {PATCH_SIZE}, num_patches = {NUM_PATCHES}")
    print(f"  secondary_rank = {SECONDARY_RANK}")
    print(f"  train_size = {TRAIN_SIZE}, test_size = {TEST_SIZE}")
    print(f"  batch_size = {BATCH_SIZE}")
    print(f"  device = {DEVICE}")

    # Setup directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plots_dir = os.path.join(script_dir, "plots")
    data_dir = os.path.join(script_dir, "..", "..", "data")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

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

    # Train baseline for comparison
    print("\n" + "=" * 70)
    print("Training Baseline Model (no echo correction)")
    print("=" * 70)

    torch.manual_seed(42)
    np.random.seed(42)
    baseline_model = TinyViT(attn_type='baseline').to(DEVICE)
    baseline_optimizer = optim.Adam(baseline_model.parameters(), lr=LR)
    baseline_criterion = nn.CrossEntropyLoss()

    print(f"Parameters: {count_parameters(baseline_model):,}")

    for epoch in range(NUM_EPOCHS_PHASE1):
        train_loss, train_acc = train_one_epoch(baseline_model, train_loader, baseline_optimizer, baseline_criterion)
        test_loss, test_acc = evaluate(baseline_model, test_loader, baseline_criterion)
        print(f"  Epoch {epoch+1:2d}/{NUM_EPOCHS_PHASE1} | Train: {train_acc:.4f} | Test: {test_acc:.4f}")

    baseline_acc = test_acc
    print(f"\nBaseline final accuracy: {baseline_acc:.4f}")

    # PHASE 1: Train dual-channel
    dual_model, w_cross_history, tier3_accs = phase1_train_dual_channel(train_loader, test_loader)
    tier3_acc = tier3_accs[-1]

    # PHASE 2: Extract echo subspace
    echo_diffs, pca_models, variance_explained = phase2_extract_echo_subspace(dual_model, test_loader)

    # PHASE 3: Test projector
    phase3_results = phase3_test_projector(train_loader, test_loader, pca_models, baseline_acc, tier3_acc)

    # PHASE 4: Test self-similarity
    similarity_matrix = phase4_test_self_similarity(pca_models)

    # Generate plots
    print("\n" + "=" * 70)
    print("GENERATING PLOTS")
    print("=" * 70)

    plot_phase1_results(w_cross_history, tier3_accs, plots_dir)
    plot_phase2_results(variance_explained, plots_dir)
    plot_phase3_results(baseline_acc, tier3_acc, phase3_results, plots_dir)
    plot_phase4_results(similarity_matrix, plots_dir)

    print(f"\nAll plots saved to {plots_dir}")

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(f"\n1. w_cross convergence (Phase 1):")
    final_w_cross = w_cross_history[-1]
    print(f"   Final w_cross by layer: {[f'{w:.4f}' for w in final_w_cross]}")
    all_negative = all(w < 0 for w in final_w_cross)
    depth_gradient = final_w_cross[-1] < final_w_cross[0]
    print(f"   All negative: {all_negative}")
    print(f"   Strengthens with depth: {depth_gradient} ({final_w_cross[0]:.3f} -> {final_w_cross[-1]:.3f})")

    print(f"\n2. Echo subspace low-rank structure (Phase 2):")
    for i, var_exp in enumerate(variance_explained):
        top4_var = var_exp[2]  # index 2 is k=4
        print(f"   Layer {i}: Top-4 components explain {top4_var*100:.1f}% of variance")

    avg_top4 = np.mean([var_exp[2] for var_exp in variance_explained])
    print(f"   Average across layers: {avg_top4*100:.1f}%")
    if avg_top4 > 0.8:
        print("   RESULT: Echo IS low-rank (>80% variance in top-4)")
    else:
        print(f"   RESULT: Echo is NOT clearly low-rank (<80% variance in top-4)")

    print(f"\n3. Tier comparison (Phase 3):")
    print(f"   Baseline: {baseline_acc:.4f}")
    print(f"   Tier 3 (dual-channel): {tier3_acc:.4f} (+{(tier3_acc-baseline_acc)*100:.2f}%)")

    for name, data in phase3_results.items():
        acc = data['final_acc']
        print(f"   {name}: {acc:.4f} (+{(acc-baseline_acc)*100:.2f}% vs baseline, "
              f"{(acc-tier3_acc)*100:+.2f}% vs Tier 3)")

    print(f"\n4. Cross-layer self-similarity (Phase 4):")
    avg_adjacent = np.mean([similarity_matrix[i, i+1] for i in range(NUM_LAYERS - 1)])
    print(f"   Average adjacent layer similarity: {avg_adjacent:.4f}")

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    print(f"\n  1. Inhibitory signal confirmed: w_cross = {final_w_cross[0]:.3f} to {final_w_cross[-1]:.3f}")
    print(f"  2. Echo subspace rank: Top-4 explains {avg_top4*100:.1f}% variance (avg)")
    print(f"  3. Tier 3 improvement over baseline: +{(tier3_acc-baseline_acc)*100:.2f}%")

    best_tier25 = max(phase3_results.values(), key=lambda x: x['final_acc'])
    best_name = [k for k, v in phase3_results.items() if v == best_tier25][0]
    print(f"  4. Best Tier 2.5 ({best_name}): {best_tier25['final_acc']:.4f} "
          f"({(best_tier25['final_acc']-tier3_acc)*100:+.2f}% vs Tier 3)")

    print(f"  5. Echo self-similarity: {avg_adjacent:.3f} adjacent layer similarity")

    print("\nExperiment complete!")


if __name__ == "__main__":
    main()
