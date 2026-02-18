#!/usr/bin/env python3
"""
Gradient Flow Test: Quick depth scaling comparison without training.

Tests whether activations maintain stable gradient flow at initialization
across extreme depths. This directly tests critical initialization theory.

Runtime: ~30 seconds on CPU for all activations across all depths.
"""

import numpy as np
import torch
import torch.nn as nn

# ============================================================================
# CONSTANTS (same as activation_benchmark.py)
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2
THREE_MINUS_PHI = 3 - PHI
OUROBOROS_LAMBDA = 0.375706395625264

CRITICAL_SCALES = {
    'OuroborosExact': THREE_MINUS_PHI,
    'ReLU': np.sqrt(2),
    'Swish': 1.6233,
    'Mish': 1.4448,
    'GELU': 1.4811,
}

# ============================================================================
# ACTIVATIONS
# ============================================================================

class OuroborosExact(nn.Module):
    def __init__(self):
        super().__init__()
        self.lam = OUROBOROS_LAMBDA
    def forward(self, x):
        return x * (self.lam + (1 - self.lam) * torch.sigmoid(x))

class Swish(nn.Module):
    def forward(self, x):
        return x * torch.sigmoid(x)

class Mish(nn.Module):
    def forward(self, x):
        return x * torch.tanh(nn.functional.softplus(x))

class ReLUActivation(nn.Module):
    def forward(self, x):
        return torch.relu(x)

class GELUActivation(nn.Module):
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
# MODEL CREATION
# ============================================================================

def create_mlp(depth, width, activation_name, input_dim=784, output_dim=10):
    activation_class = ACTIVATION_CLASSES[activation_name]
    critical_scale = CRITICAL_SCALES[activation_name]

    layers = []

    # Input layer
    layer = nn.Linear(input_dim, width)
    nn.init.normal_(layer.weight, mean=0, std=critical_scale / np.sqrt(input_dim))
    nn.init.zeros_(layer.bias)
    layers.extend([layer, activation_class()])

    # Hidden layers
    for _ in range(depth - 1):
        layer = nn.Linear(width, width)
        nn.init.normal_(layer.weight, mean=0, std=critical_scale / np.sqrt(width))
        nn.init.zeros_(layer.bias)
        layers.extend([layer, activation_class()])

    # Output layer
    layer = nn.Linear(width, output_dim)
    nn.init.normal_(layer.weight, mean=0, std=1.0 / np.sqrt(width))
    nn.init.zeros_(layer.bias)
    layers.append(layer)

    return nn.Sequential(*layers)

# ============================================================================
# GRADIENT FLOW TEST
# ============================================================================

def test_gradient_flow(activation_name, depths, width=256, n_trials=10):
    """
    Test gradient flow at initialization across multiple depths.

    Returns dict with depth -> {grad_norm, output_std, grad_ratio}
    """
    results = {}

    for depth in depths:
        grad_norms = []
        output_stds = []

        for trial in range(n_trials):
            torch.manual_seed(trial)
            model = create_mlp(depth, width, activation_name)

            # Forward pass
            x = torch.randn(64, 784)
            x.requires_grad = True
            out = model(x)

            # Backward pass
            grad_out = torch.randn_like(out)
            out.backward(grad_out)

            grad_norms.append(x.grad.norm().item())
            output_stds.append(out.std().item())

        results[depth] = {
            'grad_norm_mean': np.mean(grad_norms),
            'grad_norm_std': np.std(grad_norms),
            'output_std_mean': np.mean(output_stds),
            'output_std_std': np.std(output_stds),
        }

    return results

def compute_gradient_ratio(results, baseline_depth=10):
    """Compute gradient decay/growth ratio relative to baseline depth."""
    baseline = results[baseline_depth]['grad_norm_mean']
    for depth, data in results.items():
        data['grad_ratio'] = data['grad_norm_mean'] / baseline if baseline > 0 else float('inf')
    return results

# ============================================================================
# MAIN
# ============================================================================

def run_gradient_flow_test():
    depths = [10, 25, 50, 75, 100, 150, 200]
    width = 256
    activation_names = ['OuroborosExact', 'Swish', 'Mish', 'ReLU', 'GELU']

    print("=" * 90)
    print("GRADIENT FLOW TEST: Depth Scaling at Initialization")
    print("=" * 90)
    print()
    print(f"Width: {width}")
    print(f"Depths tested: {depths}")
    print(f"Trials per config: 10")
    print()

    all_results = {}

    for act_name in activation_names:
        print(f"Testing {act_name}...", end=" ", flush=True)
        results = test_gradient_flow(act_name, depths, width)
        results = compute_gradient_ratio(results, baseline_depth=10)
        all_results[act_name] = results
        print("done")

    print()

    # =========================================================================
    # OUTPUT STANDARD DEVIATION TABLE
    # =========================================================================
    print("=" * 90)
    print("OUTPUT STD (forward signal - should stay ~1.0 for critical init)")
    print("=" * 90)
    print()

    header = f"{'Depth':<8}"
    for act_name in activation_names:
        header += f"{act_name:>14}"
    print(header)
    print("-" * (8 + 14 * len(activation_names)))

    for depth in depths:
        row = f"{depth:<8}"
        for act_name in activation_names:
            val = all_results[act_name][depth]['output_std_mean']
            if val > 100:
                row += f"{'EXPLODED':>14}"
            elif val < 0.01:
                row += f"{'VANISHED':>14}"
            else:
                row += f"{val:>14.4f}"
        print(row)

    print()

    # =========================================================================
    # GRADIENT NORM TABLE
    # =========================================================================
    print("=" * 90)
    print("GRADIENT NORM (backward signal - should stay stable)")
    print("=" * 90)
    print()

    print(header)
    print("-" * (8 + 14 * len(activation_names)))

    for depth in depths:
        row = f"{depth:<8}"
        for act_name in activation_names:
            val = all_results[act_name][depth]['grad_norm_mean']
            if val > 1e6:
                row += f"{'EXPLODED':>14}"
            elif val < 1e-6:
                row += f"{'VANISHED':>14}"
            else:
                row += f"{val:>14.4f}"
        print(row)

    print()

    # =========================================================================
    # GRADIENT RATIO TABLE (relative to depth 10)
    # =========================================================================
    print("=" * 90)
    print("GRADIENT RATIO (relative to depth 10 - ideal = 1.0)")
    print("=" * 90)
    print()

    print(header)
    print("-" * (8 + 14 * len(activation_names)))

    for depth in depths:
        row = f"{depth:<8}"
        for act_name in activation_names:
            val = all_results[act_name][depth]['grad_ratio']
            if val > 100:
                row += f"{'>>1':>14}"
            elif val < 0.01:
                row += f"{'<<1':>14}"
            else:
                row += f"{val:>14.4f}"
        print(row)

    print()

    # =========================================================================
    # STABILITY SCORE
    # =========================================================================
    print("=" * 90)
    print("STABILITY SCORE (how close to ideal ratio=1.0 at depth 200)")
    print("=" * 90)
    print()

    scores = []
    for act_name in activation_names:
        ratio_200 = all_results[act_name][200]['grad_ratio']
        # Score: how close to 1.0 (log scale, so 0.5 and 2.0 are equally bad)
        if ratio_200 > 0:
            log_deviation = abs(np.log(ratio_200))
            score = np.exp(-log_deviation)  # 1.0 = perfect, 0 = bad
        else:
            score = 0
        scores.append((act_name, ratio_200, score))

    scores.sort(key=lambda x: x[2], reverse=True)

    print(f"{'Rank':<6}{'Activation':<18}{'Ratio@200':<14}{'Score':<10}")
    print("-" * 48)
    for i, (name, ratio, score) in enumerate(scores, 1):
        ratio_str = f"{ratio:.4f}" if 0.0001 < ratio < 10000 else f"{ratio:.2e}"
        print(f"{i:<6}{name:<18}{ratio_str:<14}{score:.4f}")

    print()
    print("=" * 90)
    print("CONCLUSION")
    print("=" * 90)
    print()

    winner = scores[0]
    print(f"Most stable at extreme depth: {winner[0]}")
    print(f"  - Gradient ratio at depth 200: {winner[1]:.4f}")
    print(f"  - Stability score: {winner[2]:.4f}")
    print()

    # Check if OuroborosExact wins
    ouro_rank = next(i for i, (name, _, _) in enumerate(scores, 1) if name == 'OuroborosExact')
    if ouro_rank == 1:
        print("OuroborosExact (critical scale = 3-phi) shows BEST gradient stability!")
    else:
        print(f"OuroborosExact ranked #{ouro_rank} for gradient stability.")
        print(f"Winner: {winner[0]}")

    print()

    return all_results


if __name__ == "__main__":
    results = run_gradient_flow_test()
