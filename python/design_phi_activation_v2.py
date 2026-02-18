"""
Design Neural Network Activations that Hit Exactly (3-phi) = 1.3820 in DEEP NETWORKS

INSIGHT FROM V1:
- Theoretical single-layer analysis gives one critical scale
- Deep network dynamics give a DIFFERENT (shifted) critical scale
- Standard GELU: theory = 1.481, experiment = 1.391 (shift ~ 0.09)
- Standard Mish: theory = 1.445, experiment = 1.383 (shift ~ 0.06)

NEW APPROACH:
- Sweep parameters directly in neural networks, not just theory
- Find parameters where EXPERIMENTAL critical scale = (3-phi)
- This accounts for the deep network correction factor

Author: Claude (Anthropic)
Date: 2026-02-08
"""

import numpy as np
from scipy.special import erf
from scipy.optimize import brentq, minimize_scalar, minimize
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
import json
from pathlib import Path

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ~ 1.618034
THREE_MINUS_PHI = 3 - PHI   # ~ 1.381966
TARGET_CRITICAL = THREE_MINUS_PHI

print("=" * 70)
print("DESIGN PHI-OPTIMAL ACTIVATION FUNCTIONS (DEEP NETWORK VERSION)")
print("=" * 70)
print(f"\nTarget critical scale in deep networks: (3-phi) = {TARGET_CRITICAL:.10f}")
print()

# ============================================================================
# NEURAL NETWORK UTILITIES
# ============================================================================

def measure_lyapunov(model, width, batch_size=32):
    """Measure Lyapunov exponent from gradient flow."""
    model.train()
    x = torch.randn(batch_size, width, requires_grad=True)
    y = model(x)
    loss = y.sum()
    loss.backward()

    grad_norms = []
    for layer in model:
        if isinstance(layer, nn.Linear):
            if layer.weight.grad is not None:
                grad_norms.append(layer.weight.grad.norm().item())

    if len(grad_norms) < 2:
        return float('-inf')

    valid_norms = [g for g in grad_norms if g > 1e-20]
    if len(valid_norms) < 2:
        return float('-inf')

    log_norms = np.log(np.array(valid_norms) + 1e-30)
    return float(np.mean(np.diff(log_norms)))

def find_critical_scale_for_activation(activation_factory, depth=30, width=256,
                                        scale_range=(0.5, 2.5), n_scales=80, n_seeds=8):
    """Find critical scale through neural network experiments."""
    scales = np.linspace(scale_range[0], scale_range[1], n_scales)
    critical_points = []

    for seed in range(n_seeds):
        torch.manual_seed(seed)
        np.random.seed(seed)

        lyapunovs = []
        for scale in scales:
            torch.manual_seed(seed)

            # Create network
            layers = []
            for i in range(depth):
                layer = nn.Linear(width, width, bias=False)
                nn.init.normal_(layer.weight, std=scale / np.sqrt(width))
                layers.append(layer)
                layers.append(activation_factory())
            model = nn.Sequential(*layers)

            lyap = measure_lyapunov(model, width)
            lyapunovs.append(lyap)

        lyapunovs = np.array(lyapunovs)
        valid_mask = np.isfinite(lyapunovs)
        valid_scales = scales[valid_mask]
        valid_lyapunovs = lyapunovs[valid_mask]

        if len(valid_lyapunovs) < 2:
            continue

        signs = np.sign(valid_lyapunovs)
        sign_changes = np.where(np.diff(signs) != 0)[0]

        if len(sign_changes) > 0:
            idx = sign_changes[0]
            s1, s2 = valid_scales[idx], valid_scales[idx + 1]
            l1, l2 = valid_lyapunovs[idx], valid_lyapunovs[idx + 1]
            if l2 - l1 != 0:
                critical = s1 - l1 * (s2 - s1) / (l2 - l1)
                critical_points.append(critical)
        else:
            idx = np.argmin(np.abs(valid_lyapunovs))
            critical_points.append(valid_scales[idx])

    if critical_points:
        return np.mean(critical_points), np.std(critical_points) / np.sqrt(len(critical_points))
    return None, None

# ============================================================================
# PARAMETRIC ACTIVATION MODULES
# ============================================================================

class ParametricMish(nn.Module):
    """f(x) = x * tanh(beta * softplus(x))"""
    def __init__(self, beta):
        super().__init__()
        self.beta = beta
    def forward(self, x):
        return x * torch.tanh(self.beta * torch.nn.functional.softplus(x))

class ParametricGELU(nn.Module):
    """f(x) = x * 0.5 * (1 + erf(x / (alpha * sqrt(2))))"""
    def __init__(self, alpha):
        super().__init__()
        self.alpha = alpha
    def forward(self, x):
        return x * 0.5 * (1 + torch.erf(x / (self.alpha * np.sqrt(2))))

class BlendActivation(nn.Module):
    """f(x) = alpha * GELU(x) + (1-alpha) * Mish(x)"""
    def __init__(self, alpha):
        super().__init__()
        self.alpha = alpha
    def forward(self, x):
        gelu = x * 0.5 * (1 + torch.erf(x / np.sqrt(2)))
        mish = x * torch.tanh(torch.nn.functional.softplus(x))
        return self.alpha * gelu + (1 - self.alpha) * mish

class ScaledTanh(nn.Module):
    """f(x) = x * tanh(x / tau)"""
    def __init__(self, tau):
        super().__init__()
        self.tau = tau
    def forward(self, x):
        return x * torch.tanh(x / self.tau)

class ParametricSwish(nn.Module):
    """f(x) = x * sigmoid(beta * x)"""
    def __init__(self, beta):
        super().__init__()
        self.beta = beta
    def forward(self, x):
        return x * torch.sigmoid(self.beta * x)

class CustomGate(nn.Module):
    """f(x) = x * sigmoid(gamma * x + delta)"""
    def __init__(self, gamma, delta):
        super().__init__()
        self.gamma = gamma
        self.delta = delta
    def forward(self, x):
        return x * torch.sigmoid(self.gamma * x + self.delta)

# ============================================================================
# PART 1: PARAMETRIC MISH SWEEP
# ============================================================================

print("=" * 70)
print("PART 1: PARAMETRIC MISH SWEEP")
print("f(x) = x * tanh(beta * softplus(x))")
print("Standard Mish (beta=1) gives experimental critical ~ 1.383")
print("=" * 70)

beta_values = [0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2]
mish_results = []

print("\nSweeping beta...")
for beta in beta_values:
    print(f"  beta={beta:.2f}...", end=" ", flush=True)
    crit, err = find_critical_scale_for_activation(lambda b=beta: ParametricMish(b), n_seeds=5)
    if crit:
        diff = abs(crit - TARGET_CRITICAL)
        mish_results.append({'beta': beta, 'critical': crit, 'error': err, 'diff': diff})
        print(f"critical = {crit:.6f}, diff from (3-phi) = {diff:.6f}")
    else:
        print("N/A")

# Find best beta
if mish_results:
    best_mish = min(mish_results, key=lambda x: x['diff'])
    print(f"\nBest Mish: beta = {best_mish['beta']:.2f}, critical = {best_mish['critical']:.6f}")
    print(f"  Error from (3-phi): {best_mish['diff']:.6f}")

# ============================================================================
# PART 2: BLEND SWEEP (GELU + Mish)
# ============================================================================

print("\n" + "=" * 70)
print("PART 2: BLEND SWEEP (GELU + Mish)")
print("f(x) = alpha * GELU(x) + (1-alpha) * Mish(x)")
print("Standard GELU gives ~1.391, Standard Mish gives ~1.383")
print("=" * 70)

alpha_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
blend_results = []

print("\nSweeping alpha (weight on GELU)...")
for alpha in alpha_values:
    print(f"  alpha={alpha:.1f}...", end=" ", flush=True)
    crit, err = find_critical_scale_for_activation(lambda a=alpha: BlendActivation(a), n_seeds=5)
    if crit:
        diff = abs(crit - TARGET_CRITICAL)
        blend_results.append({'alpha': alpha, 'critical': crit, 'error': err, 'diff': diff})
        print(f"critical = {crit:.6f}, diff from (3-phi) = {diff:.6f}")
    else:
        print("N/A")

# Find best blend
if blend_results:
    best_blend = min(blend_results, key=lambda x: x['diff'])
    print(f"\nBest Blend: alpha = {best_blend['alpha']:.1f}, critical = {best_blend['critical']:.6f}")
    print(f"  Error from (3-phi): {best_blend['diff']:.6f}")

# ============================================================================
# PART 3: FINE SEARCH AROUND BEST BLEND
# ============================================================================

print("\n" + "=" * 70)
print("PART 3: FINE SEARCH AROUND BEST BLEND")
print("=" * 70)

if blend_results:
    # Look at blend results to find where critical crosses TARGET
    sorted_blend = sorted(blend_results, key=lambda x: x['alpha'])

    # Find crossing point
    for i in range(len(sorted_blend) - 1):
        c1, c2 = sorted_blend[i]['critical'], sorted_blend[i+1]['critical']
        a1, a2 = sorted_blend[i]['alpha'], sorted_blend[i+1]['alpha']

        # Check if TARGET is between c1 and c2
        if (c1 - TARGET_CRITICAL) * (c2 - TARGET_CRITICAL) < 0:
            # Linear interpolation
            alpha_target = a1 + (TARGET_CRITICAL - c1) * (a2 - a1) / (c2 - c1)
            print(f"\nPredicted optimal alpha (interpolation): {alpha_target:.4f}")

            # Fine search around this point
            fine_alphas = np.linspace(max(0, alpha_target - 0.1), min(1, alpha_target + 0.1), 11)
            fine_results = []

            print("\nFine sweep around predicted optimal...")
            for alpha in fine_alphas:
                print(f"  alpha={alpha:.3f}...", end=" ", flush=True)
                crit, err = find_critical_scale_for_activation(lambda a=alpha: BlendActivation(a), n_seeds=8)
                if crit:
                    diff = abs(crit - TARGET_CRITICAL)
                    fine_results.append({'alpha': alpha, 'critical': crit, 'error': err, 'diff': diff})
                    print(f"critical = {crit:.6f}, diff = {diff:.6f}")
                else:
                    print("N/A")

            if fine_results:
                best_fine = min(fine_results, key=lambda x: x['diff'])
                print(f"\nBest fine blend: alpha = {best_fine['alpha']:.4f}")
                print(f"  Critical scale = {best_fine['critical']:.6f}")
                print(f"  Target (3-phi) = {TARGET_CRITICAL:.6f}")
                print(f"  Error = {best_fine['diff']:.6f}")
            break

# ============================================================================
# PART 4: SCALED TANH SWEEP
# ============================================================================

print("\n" + "=" * 70)
print("PART 4: SCALED TANH SWEEP")
print("f(x) = x * tanh(x / tau)")
print("=" * 70)

tau_values = [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
tanh_results = []

print("\nSweeping tau...")
for tau in tau_values:
    print(f"  tau={tau:.1f}...", end=" ", flush=True)
    crit, err = find_critical_scale_for_activation(lambda t=tau: ScaledTanh(t), n_seeds=5)
    if crit:
        diff = abs(crit - TARGET_CRITICAL)
        tanh_results.append({'tau': tau, 'critical': crit, 'error': err, 'diff': diff})
        print(f"critical = {crit:.6f}, diff from (3-phi) = {diff:.6f}")
    else:
        print("N/A")

if tanh_results:
    best_tanh = min(tanh_results, key=lambda x: x['diff'])
    print(f"\nBest Scaled Tanh: tau = {best_tanh['tau']:.1f}, critical = {best_tanh['critical']:.6f}")
    print(f"  Error from (3-phi): {best_tanh['diff']:.6f}")

# ============================================================================
# PART 5: PARAMETRIC SWISH SWEEP
# ============================================================================

print("\n" + "=" * 70)
print("PART 5: PARAMETRIC SWISH SWEEP")
print("f(x) = x * sigmoid(beta * x)")
print("Standard Swish (beta=1) gives critical ~ 1.49")
print("=" * 70)

swish_betas = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0]
swish_results = []

print("\nSweeping beta...")
for beta in swish_betas:
    print(f"  beta={beta:.1f}...", end=" ", flush=True)
    crit, err = find_critical_scale_for_activation(lambda b=beta: ParametricSwish(b), n_seeds=5)
    if crit:
        diff = abs(crit - TARGET_CRITICAL)
        swish_results.append({'beta': beta, 'critical': crit, 'error': err, 'diff': diff})
        print(f"critical = {crit:.6f}, diff from (3-phi) = {diff:.6f}")
    else:
        print("N/A")

if swish_results:
    best_swish = min(swish_results, key=lambda x: x['diff'])
    print(f"\nBest Swish: beta = {best_swish['beta']:.1f}, critical = {best_swish['critical']:.6f}")
    print(f"  Error from (3-phi): {best_swish['diff']:.6f}")

# ============================================================================
# PART 6: SUMMARY AND PHI-OPTIMAL ACTIVATION
# ============================================================================

print("\n" + "=" * 70)
print("SUMMARY: ACTIVATIONS CLOSEST TO (3-phi) IN DEEP NETWORKS")
print("=" * 70)

all_best = []
if mish_results:
    best = min(mish_results, key=lambda x: x['diff'])
    all_best.append({'name': 'Parametric Mish', 'params': f'beta={best["beta"]:.2f}',
                    'critical': best['critical'], 'diff': best['diff']})
if blend_results:
    best = min(blend_results, key=lambda x: x['diff'])
    all_best.append({'name': 'Blend (GELU+Mish)', 'params': f'alpha={best["alpha"]:.2f}',
                    'critical': best['critical'], 'diff': best['diff']})
if tanh_results:
    best = min(tanh_results, key=lambda x: x['diff'])
    all_best.append({'name': 'Scaled Tanh', 'params': f'tau={best["tau"]:.2f}',
                    'critical': best['critical'], 'diff': best['diff']})
if swish_results:
    best = min(swish_results, key=lambda x: x['diff'])
    all_best.append({'name': 'Parametric Swish', 'params': f'beta={best["beta"]:.2f}',
                    'critical': best['critical'], 'diff': best['diff']})

# Also add standard activations
print("\nAdding standard activations for comparison...")
for name, factory in [('Standard GELU', lambda: nn.GELU()),
                      ('Standard Mish', lambda: ParametricMish(1.0))]:
    print(f"  {name}...", end=" ", flush=True)
    crit, err = find_critical_scale_for_activation(factory, n_seeds=8)
    if crit:
        diff = abs(crit - TARGET_CRITICAL)
        all_best.append({'name': name, 'params': 'default', 'critical': crit, 'diff': diff})
        print(f"critical = {crit:.6f}")
    else:
        print("N/A")

# Sort by closeness to target
all_best_sorted = sorted(all_best, key=lambda x: x['diff'])

print(f"\nTarget: (3-phi) = {TARGET_CRITICAL:.6f}")
print("-" * 80)
print(f"{'Rank':<6} {'Activation':<25} {'Parameters':<15} {'Critical':<12} {'Error'}")
print("-" * 80)
for rank, item in enumerate(all_best_sorted, 1):
    print(f"{rank:<6} {item['name']:<25} {item['params']:<15} {item['critical']:<12.6f} {item['diff']:.6f}")

# ============================================================================
# PART 7: THE PHI-OPTIMAL ACTIVATION
# ============================================================================

print("\n" + "=" * 70)
print("THE PHI-OPTIMAL ACTIVATION")
print("=" * 70)

if all_best_sorted:
    winner = all_best_sorted[0]
    print(f"""
BEST ACTIVATION FOR (3-phi) CRITICAL SCALE:

  Activation: {winner['name']}
  Parameters: {winner['params']}
  Critical Scale: {winner['critical']:.6f}
  Target (3-phi): {TARGET_CRITICAL:.6f}
  Error: {winner['diff']:.6f}

This activation achieves critical initialization scale within {winner['diff']*100/TARGET_CRITICAL:.2f}% of (3-phi).
""")

# Save results
output = {
    'target': TARGET_CRITICAL,
    'phi': PHI,
    'mish_sweep': mish_results,
    'blend_sweep': blend_results,
    'tanh_sweep': tanh_results,
    'swish_sweep': swish_results,
    'summary': all_best_sorted,
}

def convert(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, dict):
        return {k: convert(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert(v) for v in obj]
    return obj

output_path = Path(__file__).parent / 'phi_activation_nn_results.json'
with open(output_path, 'w') as f:
    json.dump(convert(output), f, indent=2)
print(f"Results saved to: {output_path}")

print("\n" + "=" * 70)
print("EXPERIMENT COMPLETE")
print("=" * 70)
