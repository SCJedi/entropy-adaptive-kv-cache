"""
Fine-Grained Search for Phi-Optimal Activations

Results from v2:
- Standard Mish (beta=1.00): critical = 1.385 (error 0.0032)
- Parametric Swish (beta=2.0): critical = 1.388 (error 0.0056)

Target: (3-phi) = 1.381966

This script does fine-grained sweeps to find the EXACT parameters.

Author: Claude (Anthropic)
Date: 2026-02-08
"""

import numpy as np
from scipy.special import erf
import torch
import torch.nn as nn
from typing import Dict, List, Tuple
import json
from pathlib import Path

PHI = (1 + np.sqrt(5)) / 2
THREE_MINUS_PHI = 3 - PHI
TARGET = THREE_MINUS_PHI

print("=" * 70)
print("FINE-GRAINED SEARCH FOR PHI-OPTIMAL ACTIVATIONS")
print("=" * 70)
print(f"Target: (3-phi) = {TARGET:.10f}")
print()

# ============================================================================
# UTILITIES
# ============================================================================

def measure_lyapunov(model, width, batch_size=32):
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

def find_critical_scale(activation_factory, depth=30, width=256,
                        scale_range=(0.5, 2.5), n_scales=100, n_seeds=10):
    scales = np.linspace(scale_range[0], scale_range[1], n_scales)
    critical_points = []

    for seed in range(n_seeds):
        torch.manual_seed(seed)
        np.random.seed(seed)

        lyapunovs = []
        for scale in scales:
            torch.manual_seed(seed)
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

    if critical_points:
        return np.mean(critical_points), np.std(critical_points) / np.sqrt(len(critical_points))
    return None, None

# ============================================================================
# ACTIVATION MODULES
# ============================================================================

class ParametricMish(nn.Module):
    def __init__(self, beta):
        super().__init__()
        self.beta = beta
    def forward(self, x):
        return x * torch.tanh(self.beta * torch.nn.functional.softplus(x))

class ParametricSwish(nn.Module):
    def __init__(self, beta):
        super().__init__()
        self.beta = beta
    def forward(self, x):
        return x * torch.sigmoid(self.beta * x)

class BlendActivation(nn.Module):
    def __init__(self, alpha):
        super().__init__()
        self.alpha = alpha
    def forward(self, x):
        gelu = x * 0.5 * (1 + torch.erf(x / np.sqrt(2)))
        mish = x * torch.tanh(torch.nn.functional.softplus(x))
        return self.alpha * gelu + (1 - self.alpha) * mish

# ============================================================================
# PART 1: FINE SEARCH AROUND MISH beta=1.0
# ============================================================================

print("=" * 70)
print("PART 1: FINE SEARCH AROUND MISH (beta ~ 1.0)")
print("=" * 70)

# From v2: beta=1.00 gives critical=1.385, beta=1.05 gives critical=1.374
# Target is 1.382, so optimal beta is between 1.00 and 1.05

mish_betas = np.linspace(1.00, 1.05, 11)
mish_results = []

print("\nFine sweep of beta...")
for beta in mish_betas:
    print(f"  beta={beta:.3f}...", end=" ", flush=True)
    crit, err = find_critical_scale(lambda b=beta: ParametricMish(b), n_seeds=10)
    if crit:
        diff = abs(crit - TARGET)
        mish_results.append({'beta': beta, 'critical': crit, 'error': err, 'diff': diff})
        print(f"critical = {crit:.6f}, diff = {diff:.6f}")

if mish_results:
    best = min(mish_results, key=lambda x: x['diff'])
    print(f"\nBest Parametric Mish:")
    print(f"  beta = {best['beta']:.4f}")
    print(f"  critical = {best['critical']:.6f} +/- {best['error']:.6f}")
    print(f"  error from (3-phi) = {best['diff']:.6f}")

    # Even finer search
    if best['beta'] > mish_betas[0] and best['beta'] < mish_betas[-1]:
        finer_betas = np.linspace(best['beta'] - 0.01, best['beta'] + 0.01, 11)
        finer_results = []
        print(f"\nEven finer sweep around beta={best['beta']:.3f}...")
        for beta in finer_betas:
            if beta > 0.9 and beta < 1.2:
                print(f"  beta={beta:.4f}...", end=" ", flush=True)
                crit, err = find_critical_scale(lambda b=beta: ParametricMish(b), n_seeds=15)
                if crit:
                    diff = abs(crit - TARGET)
                    finer_results.append({'beta': beta, 'critical': crit, 'error': err, 'diff': diff})
                    print(f"critical = {crit:.6f}, diff = {diff:.6f}")

        if finer_results:
            finest = min(finer_results, key=lambda x: x['diff'])
            print(f"\nFinest Mish result:")
            print(f"  beta = {finest['beta']:.5f}")
            print(f"  critical = {finest['critical']:.6f}")
            print(f"  error = {finest['diff']:.6f}")
            mish_results.extend(finer_results)

# ============================================================================
# PART 2: FINE SEARCH WITH BLEND
# ============================================================================

print("\n" + "=" * 70)
print("PART 2: FINE BLEND SEARCH")
print("Since Mish(1.385) > target and can we go lower?")
print("=" * 70)

# Try a slight modification: parametric mish with beta slightly > 1
print("\nTrying Mish with beta in [1.01, 1.04]...")
mish_fine = np.linspace(1.01, 1.04, 7)
for beta in mish_fine:
    print(f"  beta={beta:.3f}...", end=" ", flush=True)
    crit, err = find_critical_scale(lambda b=beta: ParametricMish(b), n_seeds=12)
    if crit:
        diff = abs(crit - TARGET)
        mish_results.append({'beta': beta, 'critical': crit, 'error': err, 'diff': diff})
        print(f"critical = {crit:.6f}, diff = {diff:.6f}")

# ============================================================================
# PART 3: SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("SUMMARY: BEST ACTIVATIONS FOR (3-phi)")
print("=" * 70)

# Collect all results
all_results = []

if mish_results:
    best_mish = min(mish_results, key=lambda x: x['diff'])
    all_results.append({
        'name': 'Parametric Mish',
        'formula': f'x * tanh({best_mish["beta"]:.4f} * softplus(x))',
        'params': f'beta={best_mish["beta"]:.4f}',
        'critical': best_mish['critical'],
        'diff': best_mish['diff']
    })

# Sort by closeness to target
all_results_sorted = sorted(all_results, key=lambda x: x['diff'])

print(f"\nTarget: (3-phi) = {TARGET:.10f}")
print("-" * 80)
for item in all_results_sorted:
    print(f"  {item['name']:<20} {item['params']:<20} critical={item['critical']:.6f}  error={item['diff']:.6f}")

# ============================================================================
# PART 4: THE PHI-OPTIMAL ACTIVATION
# ============================================================================

print("\n" + "=" * 70)
print("THE PHI-OPTIMAL ACTIVATION")
print("=" * 70)

if mish_results:
    final_best = min(mish_results, key=lambda x: x['diff'])
    print(f"""
ACTIVATION: Phi-Optimal Mish

  Formula: f(x) = x * tanh(beta * softplus(x))

  Optimal beta: {final_best['beta']:.5f}

  Critical Scale: {final_best['critical']:.6f}
  Target (3-phi): {TARGET:.6f}
  Error: {final_best['diff']:.6f} ({final_best['diff']/TARGET*100:.2f}%)

  Statistical Uncertainty: +/- {final_best['error']:.6f}

KEY INSIGHT:
  Standard Mish (beta=1) is ALREADY very close to (3-phi)!

  The (3-phi) critical point may be an ATTRACTOR for well-designed
  self-gating activations - Mish's designers may have empirically
  converged to this point without knowing its mathematical significance.
""")

# Save results
output = {
    'target': TARGET,
    'phi': PHI,
    'three_minus_phi': THREE_MINUS_PHI,
    'mish_results': mish_results,
    'best_mish': min(mish_results, key=lambda x: x['diff']) if mish_results else None,
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

output_path = Path(__file__).parent / 'phi_activation_fine_results.json'
with open(output_path, 'w') as f:
    json.dump(convert(output), f, indent=2)
print(f"\nResults saved to: {output_path}")

print("\n" + "=" * 70)
print("EXPERIMENT COMPLETE")
print("=" * 70)
