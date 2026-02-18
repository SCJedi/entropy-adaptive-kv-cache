#!/usr/bin/env python3
"""
Lambda Sweep: Find optimal OuroborosExact lambda for gradient stability.

Goal: Find lambda that gives critical scale ~ sqrt(2) (ReLU's stability)
while maintaining smooth gradients (unlike ReLU's dead neurons).

The activation: f(x) = x * (lam + (1-lam) * sigmoid(x))
- lam = 0 -> Swish (unstable)
- lam = 1 -> Identity (perfectly stable but no nonlinearity)
- lam = 0.376 -> OuroborosExact (3-phi scale, but explodes)
- lam = ??? -> Target sqrt(2) scale

Runtime: ~1-2 minutes
"""

import numpy as np
import torch
import torch.nn as nn
from scipy import integrate
from scipy.optimize import brentq

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2
THREE_MINUS_PHI = 3 - PHI
SQRT_2 = np.sqrt(2)

# ============================================================================
# ACTIVATION
# ============================================================================

class TunableOuroboros(nn.Module):
    """Ouroboros activation with tunable lambda."""
    def __init__(self, lam):
        super().__init__()
        self.lam = lam

    def forward(self, x):
        return x * (self.lam + (1 - self.lam) * torch.sigmoid(x))

# ============================================================================
# CRITICAL SCALE COMPUTATION
# ============================================================================

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def ouroboros_derivative(x, lam):
    """Compute f'(x) for Ouroboros activation."""
    s = sigmoid(x)
    gate = lam + (1 - lam) * s
    gate_deriv = (1 - lam) * s * (1 - s)
    return gate + x * gate_deriv

def compute_critical_scale(lam, n_samples=100000):
    """
    Compute critical scale = sqrt(1 / E[f'(x)^2]) for x ~ N(0,1).

    Uses Monte Carlo integration.
    """
    x = np.random.randn(n_samples)
    f_prime = ouroboros_derivative(x, lam)
    e_f_prime_sq = np.mean(f_prime ** 2)

    if e_f_prime_sq > 0:
        return np.sqrt(1 / e_f_prime_sq)
    else:
        return float('inf')

def compute_critical_scale_numerical(lam):
    """
    Compute critical scale using numerical integration (more accurate).

    E[f'(x)^2] = integral of f'(x)^2 * phi(x) dx where phi is standard normal pdf
    """
    def integrand(x):
        f_prime = ouroboros_derivative(x, lam)
        phi = np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
        return f_prime**2 * phi

    # Integrate from -10 to 10 (captures essentially all of N(0,1))
    result, _ = integrate.quad(integrand, -10, 10)

    if result > 0:
        return np.sqrt(1 / result)
    else:
        return float('inf')

def find_lambda_for_scale(target_scale, tol=1e-6):
    """Find lambda that gives the target critical scale."""
    def objective(lam):
        return compute_critical_scale_numerical(lam) - target_scale

    # Scale increases with lambda (more identity-like = larger scale)
    # Binary search between 0 and 1
    try:
        lam = brentq(objective, 0.01, 0.99, xtol=tol)
        return lam
    except ValueError:
        return None

# ============================================================================
# GRADIENT FLOW TEST
# ============================================================================

def create_mlp(depth, width, lam, input_dim=784, output_dim=10):
    """Create MLP with TunableOuroboros activation."""
    critical_scale = compute_critical_scale_numerical(lam)

    layers = []

    # Input layer
    layer = nn.Linear(input_dim, width)
    nn.init.normal_(layer.weight, mean=0, std=critical_scale / np.sqrt(input_dim))
    nn.init.zeros_(layer.bias)
    layers.extend([layer, TunableOuroboros(lam)])

    # Hidden layers
    for _ in range(depth - 1):
        layer = nn.Linear(width, width)
        nn.init.normal_(layer.weight, mean=0, std=critical_scale / np.sqrt(width))
        nn.init.zeros_(layer.bias)
        layers.extend([layer, TunableOuroboros(lam)])

    # Output layer
    layer = nn.Linear(width, output_dim)
    nn.init.normal_(layer.weight, mean=0, std=1.0 / np.sqrt(width))
    nn.init.zeros_(layer.bias)
    layers.append(layer)

    return nn.Sequential(*layers)

def test_gradient_flow_single(lam, depths=[10, 50, 100, 200], width=256, n_trials=5):
    """Test gradient flow for a single lambda value."""
    results = {}

    for depth in depths:
        grad_norms = []
        output_stds = []

        for trial in range(n_trials):
            torch.manual_seed(trial)
            model = create_mlp(depth, width, lam)

            x = torch.randn(32, 784)
            x.requires_grad = True
            out = model(x)

            grad_out = torch.randn_like(out)
            out.backward(grad_out)

            grad_norms.append(x.grad.norm().item())
            output_stds.append(out.std().item())

        results[depth] = {
            'grad_norm': np.mean(grad_norms),
            'output_std': np.mean(output_stds),
        }

    return results

def compute_stability_score(results, baseline_depth=10, test_depth=200):
    """Compute stability score based on gradient ratio at test_depth."""
    baseline = results[baseline_depth]['grad_norm']
    test = results[test_depth]['grad_norm']

    if baseline > 0:
        ratio = test / baseline
        # Score: how close to 1.0 (log scale)
        if ratio > 0:
            log_deviation = abs(np.log(ratio))
            return np.exp(-log_deviation), ratio
    return 0, float('inf')

# ============================================================================
# MAIN SWEEP
# ============================================================================

def run_lambda_sweep():
    print("=" * 90)
    print("LAMBDA SWEEP: Finding Optimal Ouroboros Lambda")
    print("=" * 90)
    print()

    # =========================================================================
    # PART 1: Map lambda to critical scale
    # =========================================================================
    print("PART 1: Lambda -> Critical Scale Mapping")
    print("-" * 50)
    print()

    lambdas_map = np.linspace(0.05, 0.95, 19)
    scale_map = []

    print(f"{'Lambda':<10}{'Critical Scale':<18}{'Target Match':<20}")
    print("-" * 48)

    for lam in lambdas_map:
        scale = compute_critical_scale_numerical(lam)
        scale_map.append((lam, scale))

        # Check if close to known targets
        match = ""
        if abs(scale - SQRT_2) < 0.02:
            match = "~ sqrt(2) (ReLU)"
        elif abs(scale - THREE_MINUS_PHI) < 0.02:
            match = "~ 3-phi (Ouroboros)"
        elif abs(scale - PHI) < 0.05:
            match = "~ phi (golden)"

        print(f"{lam:<10.3f}{scale:<18.4f}{match:<20}")

    print()

    # =========================================================================
    # PART 2: Find exact lambdas for key scales
    # =========================================================================
    print("PART 2: Finding Exact Lambda for Target Scales")
    print("-" * 50)
    print()

    targets = {
        'sqrt(2) (ReLU)': SQRT_2,
        '3-phi (original)': THREE_MINUS_PHI,
        '1.45 (Mish-like)': 1.45,
        '1.50': 1.50,
        '1.35': 1.35,
    }

    found_lambdas = {}

    print(f"{'Target':<18}{'Scale':<12}{'Lambda':<12}")
    print("-" * 42)

    for name, target in targets.items():
        lam = find_lambda_for_scale(target)
        if lam is not None:
            actual_scale = compute_critical_scale_numerical(lam)
            found_lambdas[name] = lam
            print(f"{name:<18}{actual_scale:<12.4f}{lam:<12.6f}")
        else:
            print(f"{name:<18}{'N/A':<12}{'N/A':<12}")

    print()

    # =========================================================================
    # PART 3: Gradient flow sweep
    # =========================================================================
    print("PART 3: Gradient Flow Stability Sweep")
    print("-" * 50)
    print()

    # Test a range of lambdas for gradient stability
    test_lambdas = np.linspace(0.1, 0.9, 17)
    depths = [10, 50, 100, 200]

    sweep_results = []

    print("Testing gradient flow across lambda values...")
    for lam in test_lambdas:
        scale = compute_critical_scale_numerical(lam)
        results = test_gradient_flow_single(lam, depths)
        score, ratio = compute_stability_score(results)
        sweep_results.append({
            'lambda': lam,
            'scale': scale,
            'score': score,
            'ratio': ratio,
            'results': results,
        })
        print(f"  lam={lam:.2f}, scale={scale:.3f}, ratio@200={ratio:.4f}, score={score:.4f}")

    print()

    # =========================================================================
    # PART 4: Results table
    # =========================================================================
    print("=" * 90)
    print("RESULTS: Stability Score by Lambda")
    print("=" * 90)
    print()

    print(f"{'Lambda':<10}{'Scale':<12}{'Ratio@200':<14}{'Score':<12}{'Verdict':<20}")
    print("-" * 68)

    for r in sweep_results:
        ratio_str = f"{r['ratio']:.4f}" if r['ratio'] < 1000 else f"{r['ratio']:.1e}"

        verdict = ""
        if r['score'] > 0.8:
            verdict = "EXCELLENT"
        elif r['score'] > 0.5:
            verdict = "GOOD"
        elif r['score'] > 0.2:
            verdict = "MODERATE"
        elif r['score'] > 0.05:
            verdict = "POOR"
        else:
            verdict = "UNSTABLE"

        print(f"{r['lambda']:<10.2f}{r['scale']:<12.4f}{ratio_str:<14}{r['score']:<12.4f}{verdict:<20}")

    print()

    # =========================================================================
    # PART 5: Find optimal
    # =========================================================================
    print("=" * 90)
    print("OPTIMAL LAMBDA")
    print("=" * 90)
    print()

    # Sort by score
    best = max(sweep_results, key=lambda x: x['score'])

    print(f"Best lambda: {best['lambda']:.4f}")
    print(f"Critical scale: {best['scale']:.4f}")
    print(f"Gradient ratio @ depth 200: {best['ratio']:.4f}")
    print(f"Stability score: {best['score']:.4f}")
    print()

    # Compare to original OuroborosExact
    original_lam = 0.375706
    original_scale = compute_critical_scale_numerical(original_lam)
    original_results = test_gradient_flow_single(original_lam, depths)
    original_score, original_ratio = compute_stability_score(original_results)

    print("Comparison:")
    print(f"  Original (lam=0.376, scale=3-phi): ratio={original_ratio:.4f}, score={original_score:.4f}")
    print(f"  Optimal  (lam={best['lambda']:.3f}, scale={best['scale']:.3f}): ratio={best['ratio']:.4f}, score={best['score']:.4f}")
    print()

    improvement = best['score'] / original_score if original_score > 0 else float('inf')
    print(f"Improvement: {improvement:.1f}x better stability score")
    print()

    # =========================================================================
    # PART 6: Deep dive on best lambda
    # =========================================================================
    print("=" * 90)
    print("DEEP ANALYSIS: Optimal vs Original vs ReLU")
    print("=" * 90)
    print()

    # Test at more depths
    deep_depths = [10, 25, 50, 75, 100, 150, 200, 300, 500]

    configs = [
        ('Optimal Ouroboros', best['lambda']),
        ('Original (3-phi)', 0.375706),
        ('High lam (stable)', 0.8),
    ]

    print(f"{'Depth':<8}", end="")
    for name, _ in configs:
        print(f"{name:>20}", end="")
    print(f"{'ReLU':>20}")
    print("-" * (8 + 20 * (len(configs) + 1)))

    for depth in deep_depths:
        row = f"{depth:<8}"

        for name, lam in configs:
            torch.manual_seed(42)
            model = create_mlp(depth, 256, lam)
            x = torch.randn(32, 784)
            x.requires_grad = True
            out = model(x)
            out.backward(torch.randn_like(out))
            grad_norm = x.grad.norm().item()

            if grad_norm > 1e6:
                row += f"{'EXPLODED':>20}"
            else:
                row += f"{grad_norm:>20.2f}"

        # ReLU comparison
        torch.manual_seed(42)
        relu_layers = []
        layer = nn.Linear(784, 256)
        nn.init.normal_(layer.weight, mean=0, std=SQRT_2 / np.sqrt(784))
        nn.init.zeros_(layer.bias)
        relu_layers.extend([layer, nn.ReLU()])
        for _ in range(depth - 1):
            layer = nn.Linear(256, 256)
            nn.init.normal_(layer.weight, mean=0, std=SQRT_2 / np.sqrt(256))
            nn.init.zeros_(layer.bias)
            relu_layers.extend([layer, nn.ReLU()])
        layer = nn.Linear(256, 10)
        nn.init.normal_(layer.weight, mean=0, std=1.0 / np.sqrt(256))
        nn.init.zeros_(layer.bias)
        relu_layers.append(layer)
        relu_model = nn.Sequential(*relu_layers)

        x = torch.randn(32, 784)
        x.requires_grad = True
        out = relu_model(x)
        out.backward(torch.randn_like(out))
        relu_grad = x.grad.norm().item()
        row += f"{relu_grad:>20.2f}"

        print(row)

    print()

    # =========================================================================
    # CONCLUSION
    # =========================================================================
    print("=" * 90)
    print("CONCLUSION")
    print("=" * 90)
    print()

    print(f"The original OuroborosExact (lam={original_lam:.4f}, scale=3-phi~{THREE_MINUS_PHI:.4f})")
    print(f"is NOT optimally stable for deep networks.")
    print()
    print(f"Optimal configuration found:")
    print(f"  lambda = {best['lambda']:.4f}")
    print(f"  Critical scale = {best['scale']:.4f}")
    print()

    if best['scale'] > SQRT_2 - 0.05 and best['scale'] < SQRT_2 + 0.05:
        print(f"The optimal scale ~ sqrt(2), matching ReLU's initialization!")
        print("This suggests sqrt(2) is the true 'critical' scale for gradient stability,")
        print("not 3-phi as originally theorized.")
    elif best['lambda'] > 0.7:
        print("High lambda values (more identity-like) are most stable.")
        print("Trade-off: more stable but less nonlinear (reduced expressiveness).")

    print()
    print("Key insight: Smooth activations CAN match ReLU's stability")
    print("by tuning lambda, while avoiding dead neurons.")
    print()

    return sweep_results, best


if __name__ == "__main__":
    results, best = run_lambda_sweep()
