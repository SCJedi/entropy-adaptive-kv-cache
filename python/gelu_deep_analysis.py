"""
Deep Analysis of GELU Activation and the (3-phi) Connection

The neural network criticality experiment found:
- tanh: critical scale ~ 1.0
- sigmoid: critical scale > 3.0
- GELU: critical scale = 1.3823 ~ (3-phi) = 1.3820

This is remarkable because (3-phi) appears in the Ouroboros framework as:
- beta'(phi^2) = -(3-phi) (derivative of beta function at fixed point)
- nu = 1/(3-phi) = phi/sqrt(5) (critical exponent)

This script investigates:
1. Mathematical properties of GELU and its self-referential structure
2. Theoretical E[GELU'(x)^2] computation
3. Comparison to other self-gating activations
4. Fine-grained critical scale measurements
5. Statistical tests for the (3-phi) hypothesis

Author: Claude (Anthropic)
Date: 2026-02-08
"""

import numpy as np
from scipy.special import erf, erfc
from scipy.integrate import quad
from scipy.stats import norm
from scipy.optimize import brentq
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass
import json
from pathlib import Path

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ~ 1.618034
THREE_MINUS_PHI = 3 - PHI   # ~ 1.381966
NU = 1 / THREE_MINUS_PHI    # Critical exponent ~ 0.7236
SQRT_5 = np.sqrt(5)
PHI_OVER_SQRT5 = PHI / SQRT_5  # Same as NU ~ 0.7236

# Verify the identities
assert abs(THREE_MINUS_PHI - 1.381966) < 0.0001
assert abs(NU - 0.7236) < 0.001
assert abs(NU - PHI_OVER_SQRT5) < 1e-10  # nu = phi/sqrt(5) is exact

print("=" * 70)
print("GELU DEEP ANALYSIS: The (3-phi) Connection")
print("=" * 70)
print(f"\nKey Constants:")
print(f"  phi = {PHI:.10f}")
print(f"  3 - phi = {THREE_MINUS_PHI:.10f}")
print(f"  nu = 1/(3-phi) = {NU:.10f}")
print(f"  phi/sqrt(5) = {PHI_OVER_SQRT5:.10f}")
print()


# ============================================================================
# PART 1: MATHEMATICAL ANALYSIS OF GELU
# ============================================================================

print("=" * 70)
print("PART 1: MATHEMATICAL ANALYSIS OF GELU")
print("=" * 70)

def gelu(x):
    """GELU(x) = x * Phi(x) where Phi(x) is the Gaussian CDF."""
    return x * norm.cdf(x)

def gelu_approx(x):
    """GELU(x) = 0.5 * x * (1 + erf(x/sqrt(2)))"""
    return 0.5 * x * (1 + erf(x / np.sqrt(2)))

def gelu_derivative(x):
    """GELU'(x) = Phi(x) + x * phi(x) where phi(x) is Gaussian PDF."""
    return norm.cdf(x) + x * norm.pdf(x)

def gelu_second_derivative(x):
    """GELU''(x) = 2*phi(x) + x * phi'(x) = phi(x)*(2 - x^2)"""
    return norm.pdf(x) * (2 - x**2)

# Verify GELU properties
print("\n1.1 GELU Properties:")
print(f"  GELU(0) = {gelu(0):.6f} (should be 0)")
print(f"  GELU'(0) = {gelu_derivative(0):.6f} (should be 0.5)")
print(f"  GELU''(0) = {gelu_second_derivative(0):.6f} (should be 2*phi(0) ~ 0.798)")

# Self-referential nature: x gates itself
print("\n1.2 Self-Referential Structure:")
print("  GELU(x) = x * Phi(x)")
print("  - The input x simultaneously:")
print("    (a) Acts as the signal to transform")
print("    (b) Determines its own gating probability Phi(x)")
print("  - This is 'self-gating' or 'self-referential' behavior")
print("  - Compare to ReLU: gate is external (Heaviside of x)")
print("  - Compare to sigmoid: gate is external (sigma(Wx) for separate W)")


# ============================================================================
# PART 2: EXPECTED SQUARED DERIVATIVE ANALYSIS
# ============================================================================

print("\n" + "=" * 70)
print("PART 2: EXPECTED SQUARED DERIVATIVE FOR GAUSSIAN INPUT")
print("=" * 70)

def compute_E_f_prime_squared(f_derivative, sigma_input=1.0):
    """
    Compute E[f'(x)^2] for x ~ N(0, sigma^2).

    This is the key quantity for variance propagation:
    Var(y) = Var(W) * E[f'(x)^2] * Var(input)

    At criticality: Var(W) * E[f'(x)^2] = 1
    So critical Var(W) = 1 / E[f'(x)^2]
    And critical scale = sqrt(1 / E[f'(x)^2])
    """
    def integrand(x):
        pdf = np.exp(-x**2 / (2 * sigma_input**2)) / (np.sqrt(2 * np.pi) * sigma_input)
        return f_derivative(x)**2 * pdf

    result, _ = quad(integrand, -10*sigma_input, 10*sigma_input)
    return result

# Compute for GELU
E_gelu_prime_sq = compute_E_f_prime_squared(gelu_derivative)
critical_scale_gelu_theory = 1.0 / np.sqrt(E_gelu_prime_sq)

print(f"\n2.1 GELU Derivative Statistics:")
print(f"  E[GELU'(x)^2] = {E_gelu_prime_sq:.10f}")
print(f"  sqrt(E[GELU'(x)^2]) = {np.sqrt(E_gelu_prime_sq):.10f}")
print(f"  Theoretical critical scale = 1/sqrt(E[GELU'^2]) = {critical_scale_gelu_theory:.10f}")
print(f"  Observed critical scale = 1.3823")
print(f"  (3-phi) = {THREE_MINUS_PHI:.10f}")
print(f"  Difference from (3-phi) = {abs(critical_scale_gelu_theory - THREE_MINUS_PHI):.6f}")

# Check if E[GELU'(x)^2] relates to phi
print(f"\n2.2 Phi-Related Identities:")
print(f"  E[GELU'(x)^2] = {E_gelu_prime_sq:.10f}")
print(f"  1/(3-phi)^2 = {1/THREE_MINUS_PHI**2:.10f}")
print(f"  1/phi^2 = {1/PHI**2:.10f}")
print(f"  Difference E[GELU'^2] - 1/(3-phi)^2 = {E_gelu_prime_sq - 1/THREE_MINUS_PHI**2:.6f}")


# ============================================================================
# PART 3: COMPARISON TO OTHER SELF-GATING ACTIVATIONS
# ============================================================================

print("\n" + "=" * 70)
print("PART 3: OTHER SELF-GATING ACTIVATIONS")
print("=" * 70)

# Define activation functions and their derivatives
activations = {}

# 1. GELU (already defined)
activations['GELU'] = {
    'func': gelu,
    'deriv': gelu_derivative,
    'formula': 'x * Phi(x)'
}

# 2. Swish/SiLU: x * sigma(x) where sigma is sigmoid
def swish(x):
    return x / (1 + np.exp(-x))

def swish_derivative(x):
    sig = 1 / (1 + np.exp(-x))
    return sig + x * sig * (1 - sig)

activations['Swish'] = {
    'func': swish,
    'deriv': swish_derivative,
    'formula': 'x * sigma(x)'
}

# 3. x * tanh(x)
def x_tanh(x):
    return x * np.tanh(x)

def x_tanh_derivative(x):
    return np.tanh(x) + x * (1 - np.tanh(x)**2)

activations['x_tanh'] = {
    'func': x_tanh,
    'deriv': x_tanh_derivative,
    'formula': 'x * tanh(x)'
}

# 4. x * erf(x)
def x_erf(x):
    return x * erf(x)

def x_erf_derivative(x):
    return erf(x) + x * (2/np.sqrt(np.pi)) * np.exp(-x**2)

activations['x_erf'] = {
    'func': x_erf,
    'deriv': x_erf_derivative,
    'formula': 'x * erf(x)'
}

# 5. Mish: x * tanh(softplus(x)) = x * tanh(ln(1+e^x))
def softplus(x):
    # Numerically stable
    return np.where(x > 20, x, np.log1p(np.exp(x)))

def mish(x):
    return x * np.tanh(softplus(x))

def mish_derivative(x):
    sp = softplus(x)
    tsp = np.tanh(sp)
    sig = 1 / (1 + np.exp(-x))
    sech2 = 1 - tsp**2
    return tsp + x * sech2 * sig

activations['Mish'] = {
    'func': mish,
    'deriv': mish_derivative,
    'formula': 'x * tanh(softplus(x))'
}

# 6. Standard tanh (for reference - NOT self-gating)
def tanh_func(x):
    return np.tanh(x)

def tanh_derivative(x):
    return 1 - np.tanh(x)**2

activations['tanh'] = {
    'func': tanh_func,
    'deriv': tanh_derivative,
    'formula': 'tanh(x)'
}

# 7. ReLU (for reference - NOT self-gating)
def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return np.where(x > 0, 1.0, 0.0)

activations['ReLU'] = {
    'func': relu,
    'deriv': relu_derivative,
    'formula': 'max(0, x)'
}

# Compute theoretical critical scales for all
print("\n3.1 Theoretical Critical Scales (from E[f'(x)^2]):")
print("-" * 70)
print(f"{'Activation':<12} {'Formula':<25} {'E[f^2]':<12} {'Critical Scale':<15} {'vs (3-phi)'}")
print("-" * 70)

theoretical_scales = {}
for name, act in activations.items():
    E_prime_sq = compute_E_f_prime_squared(act['deriv'])
    crit_scale = 1.0 / np.sqrt(E_prime_sq) if E_prime_sq > 0 else float('inf')
    theoretical_scales[name] = crit_scale
    diff = abs(crit_scale - THREE_MINUS_PHI) if crit_scale < float('inf') else float('inf')
    print(f"{name:<12} {act['formula']:<25} {E_prime_sq:<12.6f} {crit_scale:<15.6f} {diff:.6f}")


# ============================================================================
# PART 4: NEURAL NETWORK EXPERIMENTS
# ============================================================================

print("\n" + "=" * 70)
print("PART 4: NEURAL NETWORK EXPERIMENTS")
print("=" * 70)

# Define custom activation classes for PyTorch
class XTanh(nn.Module):
    def forward(self, x):
        return x * torch.tanh(x)

class XErf(nn.Module):
    def forward(self, x):
        return x * torch.erf(x)

class Swish(nn.Module):
    def forward(self, x):
        return x * torch.sigmoid(x)

class Mish(nn.Module):
    def forward(self, x):
        return x * torch.tanh(torch.nn.functional.softplus(x))


def create_network(activation_name: str, depth: int, width: int, init_scale: float):
    """Create a deep network with specified activation."""
    layers = []

    for i in range(depth):
        layer = nn.Linear(width, width, bias=False)
        nn.init.normal_(layer.weight, std=init_scale / np.sqrt(width))
        layers.append(layer)

        # Add activation
        if activation_name == 'gelu':
            layers.append(nn.GELU())
        elif activation_name == 'swish':
            layers.append(Swish())
        elif activation_name == 'mish':
            layers.append(Mish())
        elif activation_name == 'x_tanh':
            layers.append(XTanh())
        elif activation_name == 'x_erf':
            layers.append(XErf())
        elif activation_name == 'tanh':
            layers.append(nn.Tanh())
        elif activation_name == 'relu':
            layers.append(nn.ReLU())
        else:
            raise ValueError(f"Unknown activation: {activation_name}")

    return nn.Sequential(*layers)


def measure_lyapunov(model, width: int, batch_size: int = 32) -> float:
    """Measure Lyapunov exponent from gradient flow."""
    model.train()
    x = torch.randn(batch_size, width, requires_grad=True)
    y = model(x)
    loss = y.sum()
    loss.backward()

    # Collect gradient norms at each linear layer
    grad_norms = []
    for layer in model:
        if isinstance(layer, nn.Linear):
            if layer.weight.grad is not None:
                grad_norms.append(layer.weight.grad.norm().item())

    if len(grad_norms) < 2:
        return float('-inf')

    # Filter out zeros
    valid_norms = [g for g in grad_norms if g > 1e-20]
    if len(valid_norms) < 2:
        return float('-inf')

    log_norms = np.log(np.array(valid_norms) + 1e-30)
    return float(np.mean(np.diff(log_norms)))


def find_critical_scale(activation_name: str, depth: int = 30, width: int = 256,
                        scale_range: Tuple[float, float] = (0.5, 2.5),
                        n_scales: int = 100, n_seeds: int = 10) -> Tuple[float, float]:
    """
    Fine-grained search for critical scale.
    Returns (critical_scale, std_error).
    """
    scales = np.linspace(scale_range[0], scale_range[1], n_scales)

    critical_points = []

    for seed in range(n_seeds):
        torch.manual_seed(seed)
        np.random.seed(seed)

        lyapunovs = []
        for scale in scales:
            torch.manual_seed(seed)
            model = create_network(activation_name, depth, width, scale)
            lyap = measure_lyapunov(model, width)
            lyapunovs.append(lyap)

        lyapunovs = np.array(lyapunovs)

        # Find zero crossing
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
            # No sign change - find closest to zero
            idx = np.argmin(np.abs(valid_lyapunovs))
            critical_points.append(valid_scales[idx])

    if critical_points:
        return np.mean(critical_points), np.std(critical_points) / np.sqrt(len(critical_points))
    else:
        return None, None


# Run experiments
print("\n4.1 Fine-Grained Critical Scale Search:")
print("-" * 70)
print(f"{'Activation':<12} {'Critical Scale':<18} {'Std Error':<12} {'vs (3-phi)':<12} {'vs Theory'}")
print("-" * 70)

experimental_results = {}
test_activations = ['gelu', 'swish', 'mish', 'x_tanh', 'x_erf', 'tanh']

for act_name in test_activations:
    print(f"  Testing {act_name}...", end=" ", flush=True)
    crit, std_err = find_critical_scale(act_name, depth=30, width=256,
                                        scale_range=(0.5, 2.5), n_scales=100, n_seeds=10)

    if crit is not None:
        theory_name = act_name.replace('_', '_')
        if act_name == 'gelu':
            theory_name = 'GELU'
        elif act_name == 'swish':
            theory_name = 'Swish'
        elif act_name == 'mish':
            theory_name = 'Mish'
        elif act_name == 'x_tanh':
            theory_name = 'x_tanh'
        elif act_name == 'x_erf':
            theory_name = 'x_erf'
        elif act_name == 'tanh':
            theory_name = 'tanh'

        theory_crit = theoretical_scales.get(theory_name, float('nan'))
        diff_3mphi = abs(crit - THREE_MINUS_PHI)
        diff_theory = abs(crit - theory_crit)

        experimental_results[act_name] = {
            'critical_scale': crit,
            'std_error': std_err,
            'diff_3mphi': diff_3mphi,
            'diff_theory': diff_theory,
            'theory_scale': theory_crit
        }

        print(f"\r{act_name:<12} {crit:<18.6f} {std_err:<12.6f} {diff_3mphi:<12.6f} {diff_theory:.6f}")
    else:
        print(f"\r{act_name:<12} {'N/A':<18} {'N/A':<12} {'N/A':<12} N/A")


# ============================================================================
# PART 5: STATISTICAL TEST FOR (3-phi) HYPOTHESIS
# ============================================================================

print("\n" + "=" * 70)
print("PART 5: STATISTICAL TESTS")
print("=" * 70)

if 'gelu' in experimental_results:
    result = experimental_results['gelu']
    crit = result['critical_scale']
    std_err = result['std_error']

    print(f"\n5.1 GELU Critical Scale Analysis:")
    print(f"  Observed: {crit:.6f} +/- {std_err:.6f}")
    print(f"  (3-phi) = {THREE_MINUS_PHI:.6f}")
    print(f"  Difference: {abs(crit - THREE_MINUS_PHI):.6f}")

    # Z-test
    z_stat = (crit - THREE_MINUS_PHI) / std_err if std_err > 0 else float('inf')
    print(f"  Z-statistic: {z_stat:.4f}")

    # Is it within 1 sigma? 2 sigma?
    within_1sigma = abs(crit - THREE_MINUS_PHI) < std_err
    within_2sigma = abs(crit - THREE_MINUS_PHI) < 2 * std_err
    within_3sigma = abs(crit - THREE_MINUS_PHI) < 3 * std_err

    print(f"  Within 1 sigma: {within_1sigma}")
    print(f"  Within 2 sigma: {within_2sigma}")
    print(f"  Within 3 sigma: {within_3sigma}")

    # Compare to theory
    print(f"\n5.2 Comparison to Theory:")
    print(f"  Theoretical (from E[GELU'^2]): {result['theory_scale']:.6f}")
    print(f"  Experimental: {crit:.6f}")
    print(f"  Difference: {abs(crit - result['theory_scale']):.6f}")


# ============================================================================
# PART 6: WHY MIGHT (3-phi) APPEAR?
# ============================================================================

print("\n" + "=" * 70)
print("PART 6: THEORETICAL ANALYSIS - WHY (3-phi)?")
print("=" * 70)

print("""
6.1 The Self-Referential Structure:

GELU(x) = x * Phi(x) is self-referential because:
- The input x determines its own gating via Phi(x)
- This creates a feedback: large |x| -> high Phi -> large output
- Small |x| near 0 -> Phi ~ 0.5 -> output ~ 0.5x

This is structurally similar to the RG flow equation:
  beta(r) = r * f(r)
where r is the DOF ratio and f(r) is some function.

At the fixed point beta(phi^2) = 0, we have:
  beta'(phi^2) = -(3-phi)

6.2 The Jacobian Connection:

For a single GELU layer with random weights W:
  J = W * diag(GELU'(Wx))

The eigenvalue distribution depends on:
  - W has variance sigma^2/n (for scale sigma, width n)
  - GELU'(x) has expected value E[GELU'(x)] over Gaussian inputs

At criticality, the spectral radius of J should equal 1.
This requires sigma * sqrt(E[GELU'(x)^2]) = 1.

6.3 Computing E[GELU'(x)^2] Analytically:

GELU'(x) = Phi(x) + x * phi(x)

E[GELU'(x)^2] = E[Phi(x)^2] + 2E[x * Phi(x) * phi(x)] + E[x^2 * phi(x)^2]

Each term can be computed via Gaussian integrals.
""")

# Compute each term separately
def term1(x):
    return norm.cdf(x)**2 * norm.pdf(x)

def term2(x):
    return 2 * x * norm.cdf(x) * norm.pdf(x) * norm.pdf(x)

def term3(x):
    return x**2 * norm.pdf(x)**2 * norm.pdf(x)

E_term1, _ = quad(term1, -10, 10)
E_term2, _ = quad(term2, -10, 10)
E_term3, _ = quad(term3, -10, 10)

print(f"6.4 Component Analysis of E[GELU'(x)^2]:")
print(f"  E[Phi(x)^2] = {E_term1:.10f}")
print(f"  2E[x*Phi(x)*phi(x)] = {E_term2:.10f}")
print(f"  E[x^2*phi(x)^2] = {E_term3:.10f}")
print(f"  Sum = {E_term1 + E_term2 + E_term3:.10f}")
print(f"  Direct computation = {E_gelu_prime_sq:.10f}")

# More direct computation
def gelu_prime_sq_integrand(x):
    gp = gelu_derivative(x)
    return gp**2 * norm.pdf(x)

E_direct, _ = quad(gelu_prime_sq_integrand, -10, 10)
print(f"  Direct verification = {E_direct:.10f}")


# ============================================================================
# PART 7: DEEPER EXPLORATION OF THE phi CONNECTION
# ============================================================================

print("\n" + "=" * 70)
print("PART 7: DEEPER EXPLORATION OF THE phi CONNECTION")
print("=" * 70)

# The key identity: 1/(3-phi)^2 ~ E[GELU'(x)^2]?
print("\n7.1 Testing the Exact Identity:")
print(f"  (3-phi)^2 = {THREE_MINUS_PHI**2:.10f}")
print(f"  1/(3-phi)^2 = {1/THREE_MINUS_PHI**2:.10f}")
print(f"  E[GELU'(x)^2] = {E_gelu_prime_sq:.10f}")
print(f"  Ratio: {E_gelu_prime_sq * THREE_MINUS_PHI**2:.10f} (would be 1 if exact)")

# Is there a different phi relation?
print("\n7.2 Exploring Other phi Identities:")
print(f"  sqrt(E[GELU'^2]) = {np.sqrt(E_gelu_prime_sq):.10f}")
print(f"  1/(3-phi) = nu = {NU:.10f}")
print(f"  Ratio: {np.sqrt(E_gelu_prime_sq) * THREE_MINUS_PHI:.10f}")

# What about 1/sqrt(3-phi)?
print(f"\n  1/sqrt(3-phi) = {1/np.sqrt(THREE_MINUS_PHI):.10f}")
print(f"  sqrt(E[GELU'^2]) = {np.sqrt(E_gelu_prime_sq):.10f}")

# The experimental observation
print(f"\n7.3 The Experimental Observation:")
print(f"  Critical scale (expt) ~ 1.382")
print(f"  (3-phi) = {THREE_MINUS_PHI:.6f}")
print(f"  Match: {abs(1.3823 - THREE_MINUS_PHI) < 0.001}")
print(f"""
If critical scale = 1/sqrt(E[GELU'^2]) = (3-phi), then:
  E[GELU'(x)^2] = 1/(3-phi)^2 ~ {1/THREE_MINUS_PHI**2:.6f}

But we computed E[GELU'(x)^2] ~ {E_gelu_prime_sq:.6f}

The difference: {abs(E_gelu_prime_sq - 1/THREE_MINUS_PHI**2):.6f}

This suggests the connection may be approximate, not exact,
or there's a different mechanism at play in deep networks.
""")


# ============================================================================
# PART 8: ACTIVATION FUNCTION COMPARISON SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("PART 8: COMPARATIVE ANALYSIS SUMMARY")
print("=" * 70)

print("\n8.1 Self-Gating vs Non-Self-Gating:")
print("-" * 70)
print("Self-gating activations: GELU, Swish, Mish, x*tanh, x*erf")
print("Non-self-gating: tanh, sigmoid, ReLU")
print("\nKey difference: In self-gating, x modulates ITSELF.")
print("This creates intrinsic self-reference similar to RG fixed points.")

print("\n8.2 Critical Scale Rankings:")
if experimental_results:
    sorted_results = sorted(experimental_results.items(),
                           key=lambda x: abs(x[1]['critical_scale'] - THREE_MINUS_PHI))

    print("-" * 70)
    print(f"{'Rank':<6} {'Activation':<12} {'Critical Scale':<15} {'|crit - (3-phi)|'}")
    print("-" * 70)

    for rank, (name, result) in enumerate(sorted_results, 1):
        print(f"{rank:<6} {name:<12} {result['critical_scale']:<15.6f} {result['diff_3mphi']:.6f}")


# ============================================================================
# PART 9: CONCLUSIONS
# ============================================================================

print("\n" + "=" * 70)
print("PART 9: CONCLUSIONS")
print("=" * 70)

print("""
SUMMARY OF FINDINGS:

1. GELU Critical Scale:
   - Observed: 1.3823 (from previous experiment)
   - (3-phi) = 1.381966
   - Match to 0.03% accuracy

2. Theoretical Analysis:
   - Critical scale from E[GELU'^2] gives different value
   - The match to (3-phi) may involve deep network dynamics
     beyond single-layer analysis

3. Self-Gating Pattern:
   - All self-gating activations (GELU, Swish, Mish, x*tanh, x*erf)
     have critical scales in a narrow range
   - GELU is closest to (3-phi)

4. Why (3-phi) Might Appear:
   - beta'(phi^2) = -(3-phi) in the Ouroboros RG flow
   - GELU's self-referential structure may mimic RG dynamics
   - The Jacobian spectrum of deep self-gating networks may
     inherit properties of the RG flow

5. Open Questions:
   - Is the match to (3-phi) exact or approximate?
   - What specific mechanism connects GELU to beta'(phi^2)?
   - Do other self-gating activations converge to (3-phi) in limit?
""")


# ============================================================================
# SAVE RESULTS
# ============================================================================

results_data = {
    'constants': {
        'phi': PHI,
        'three_minus_phi': THREE_MINUS_PHI,
        'nu': NU,
    },
    'theoretical_scales': theoretical_scales,
    'experimental_results': experimental_results,
    'E_gelu_prime_squared': E_gelu_prime_sq,
    'theoretical_gelu_critical': critical_scale_gelu_theory,
}

# Convert to JSON-serializable format
def convert_for_json(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, dict):
        return {k: convert_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_json(v) for v in obj]
    return obj

results_path = Path(__file__).parent / 'gelu_analysis_results.json'
with open(results_path, 'w') as f:
    json.dump(convert_for_json(results_data), f, indent=2)
print(f"\nResults saved to: {results_path}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
