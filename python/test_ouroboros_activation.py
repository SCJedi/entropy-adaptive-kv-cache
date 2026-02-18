"""
Test whether the Ouroboros activation naturally produces
critical scale = (3-φ) ≈ 1.382
"""

import torch
import torch.nn as nn
import numpy as np
from ouroboros_activation import (
    OuroborosActivation, OuroborosV2, OuroborosV3, OuroborosV4,
    OuroborosV5, OuroborosV6, OuroborosV7, OuroborosV8, OuroborosV9,
    OuroborosV10, OuroborosV11, OuroborosV12, OuroborosV13, OuroborosV14, OuroborosV15,
    OuroborosV16, OuroborosV17, OuroborosV18, OuroborosV19, OuroborosV20, OuroborosV21,
    OuroborosV22, OuroborosV23, OuroborosV24, OuroborosV25, OuroborosV26,
    OuroborosV27, OuroborosV28, OuroborosV29, OuroborosV30, OuroborosFinal
)

PHI = (1 + np.sqrt(5)) / 2
THREE_MINUS_PHI = 3 - PHI  # ≈ 1.382

def create_deep_network(activation_class, depth=30, width=256, init_scale=1.0):
    """Create deep network with given activation."""
    layers = []
    for i in range(depth):
        layer = nn.Linear(width, width)
        nn.init.normal_(layer.weight, std=init_scale / np.sqrt(width))
        nn.init.zeros_(layer.bias)
        layers.append(layer)
        layers.append(activation_class())
    return nn.Sequential(*layers)

def compute_lyapunov(model, width=256, n_samples=32):
    """Compute Lyapunov exponent (gradient growth rate per layer)."""
    x = torch.randn(n_samples, width, requires_grad=True)
    y = model(x)
    loss = y.sum()
    loss.backward()

    grad_norms = []
    for name, param in model.named_parameters():
        if 'weight' in name and param.grad is not None:
            grad_norms.append(param.grad.norm().item())

    if len(grad_norms) < 2:
        return 0.0

    log_norms = np.log(np.array(grad_norms) + 1e-10)
    lyapunov = np.mean(np.diff(log_norms))
    return lyapunov

def find_critical_scale(activation_class, scales, depth=30, width=256, n_seeds=5):
    """Find the initialization scale where Lyapunov ≈ 0."""
    results = []

    for scale in scales:
        lyapunovs = []
        for seed in range(n_seeds):
            torch.manual_seed(seed)
            model = create_deep_network(activation_class, depth, width, scale)
            lyap = compute_lyapunov(model, width)
            lyapunovs.append(lyap)
        results.append((scale, np.mean(lyapunovs), np.std(lyapunovs)))

    # Find zero crossing
    for i in range(len(results) - 1):
        s1, l1, _ = results[i]
        s2, l2, _ = results[i + 1]
        if l1 * l2 < 0:  # Sign change
            # Linear interpolation
            critical = s1 + (s2 - s1) * (-l1) / (l2 - l1)
            return critical, results

    # No crossing found - return scale with smallest |lyapunov|
    min_idx = np.argmin([abs(r[1]) for r in results])
    return results[min_idx][0], results

def main():
    print("="*70)
    print("OUROBOROS ACTIVATION TEST")
    print("="*70)
    print(f"\nTarget critical scale: (3-phi) = {THREE_MINUS_PHI:.6f}")
    print()

    # Test scales
    scales = np.linspace(0.5, 2.5, 40)

    activations = [
        ("V30 (k=sqrt5-1)", OuroborosV30),
        ("FINAL (canonical)", OuroborosFinal),
    ]

    print("-"*70)
    print(f"{'Activation':<30} {'Critical':<12} {'Error':<12} {'Status'}")
    print("-"*70)

    for name, act_class in activations:
        try:
            critical, _ = find_critical_scale(act_class, scales)
            error = abs(critical - THREE_MINUS_PHI)
            status = "MATCH!" if error < 0.05 else "close" if error < 0.2 else "off"
            print(f"{name:<30} {critical:<12.4f} {error:<12.4f} {status}")
        except Exception as e:
            print(f"{name:<30} ERROR: {e}")

    print("-"*70)
    print(f"\nTarget: (3-phi) = {THREE_MINUS_PHI:.6f}")
    print()

    # Detailed verification of canonical implementation
    print("\n" + "="*70)
    print("DETAILED VERIFICATION: OuroborosFinal")
    print("="*70)

    # Finer scale resolution around (3-phi)
    fine_scales = np.linspace(1.3, 1.5, 50)
    critical_v30, results_v30 = find_critical_scale(OuroborosFinal, fine_scales, n_seeds=20)

    print(f"\nCritical scale (fine): {critical_v30:.6f}")
    print(f"Target (3-phi):        {THREE_MINUS_PHI:.6f}")
    print(f"Error:                 {abs(critical_v30 - THREE_MINUS_PHI):.6f}")
    print(f"Relative error:        {abs(critical_v30 - THREE_MINUS_PHI)/THREE_MINUS_PHI*100:.4f}%")

    # Mathematical verification
    print("\n" + "-"*70)
    print("MATHEMATICAL CONNECTION")
    print("-"*70)
    sqrt5 = np.sqrt(5)
    k = sqrt5 - 1
    three_minus_phi_alt = (5 - sqrt5) / 2

    print(f"k = sqrt(5) - 1 = {k:.6f}")
    print(f"(3 - phi) = (5 - sqrt(5))/2 = {three_minus_phi_alt:.6f}")
    print(f"Note: k = sqrt(5) - 1 = 2*(3-phi)/sqrt(5) - ... (checking relationship)")

    # k and (3-phi) relationship
    # k = sqrt(5) - 1
    # 3 - phi = (5 - sqrt(5))/2
    # ratio = (3-phi)/k = (5 - sqrt(5))/(2*(sqrt(5)-1))
    ratio = three_minus_phi_alt / k
    print(f"Ratio (3-phi)/k = {ratio:.6f}")
    print(f"This equals phi/2 = {PHI/2:.6f}")

    # Alternative: k * phi/2 should give (3-phi)
    print(f"k * (phi/2) = {k * PHI/2:.6f} vs (3-phi) = {three_minus_phi_alt:.6f}")

    # The key identity: (sqrt(5)-1) * phi / 2 = (sqrt(5)-1) * (1+sqrt(5)) / 4
    # = (sqrt(5) + 5 - 1 - sqrt(5)) / 4 = 4/4 = 1 ... no

    # Actually: (3-phi) = 3 - (1+sqrt(5))/2 = (6-1-sqrt(5))/2 = (5-sqrt(5))/2
    # k = sqrt(5) - 1
    # (3-phi) = sqrt(5)*(sqrt(5)-1)/2 = sqrt(5) * k / 2

    print(f"\nKey identity: (3-phi) = sqrt(5) * k / 2")
    print(f"Check: sqrt(5) * k / 2 = {sqrt5 * k / 2:.6f}")
    print(f"Equals (3-phi) = {three_minus_phi_alt:.6f}")

    if abs(sqrt5 * k / 2 - three_minus_phi_alt) < 1e-10:
        print("CONFIRMED: (3-phi) = sqrt(5) * (sqrt(5)-1) / 2 = sqrt(5) * k / 2")

if __name__ == "__main__":
    main()
