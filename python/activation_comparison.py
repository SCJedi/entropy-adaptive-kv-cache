#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Activation Comparison: OuroborosExact vs Swish vs Mish vs ReLU

Comprehensive comparison of activation functions measuring:
1. Critical initialization scale (where Lyapunov exponent = 0)
2. E[f'(x)^2] - expected squared derivative under N(0,1)
3. Gradient flow stability at various depths
4. Signal propagation (forward pass variance preservation)

Target critical scale: (3 - phi) = 1.381966...
Target E[f'(x)^2]: 1/(3-phi)^2 = 0.523607...

Author: Claude (Anthropic)
Date: 2026-02-08
"""

import numpy as np
from scipy import integrate
from scipy.special import erf
import torch
import torch.nn as nn
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio = 1.618033988749895
THREE_MINUS_PHI = 3 - PHI   # Target critical scale = 1.3819660112501051
TARGET_E_FPRIME_SQ = 1 / THREE_MINUS_PHI ** 2  # = 0.5236067977499789

# Lambda for OuroborosExact (from ouroboros_exact.py derivation)
# This is the value that makes E[f'(x)^2] = 1/(3-phi)^2 exactly
OUROBOROS_LAMBDA = 0.375706395625264  # Computed via numerical optimization (brentq)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sigmoid(x):
    """Numerically stable sigmoid."""
    return np.where(x >= 0,
                    1 / (1 + np.exp(-x)),
                    np.exp(x) / (1 + np.exp(x)))

def softplus(x):
    """Numerically stable softplus."""
    return np.where(x > 20, x, np.log1p(np.exp(x)))

def gaussian_expectation(f, limit=10):
    """Compute E[f(x)] for x ~ N(0, 1) using numerical integration."""
    def integrand(x):
        return f(x) * np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
    result, _ = integrate.quad(integrand, -limit, limit, limit=500)
    return result

# ============================================================================
# ACTIVATION FUNCTIONS AND DERIVATIVES
# ============================================================================

# ----- OuroborosExact (Leaky Swish with optimal lambda) -----

def ouroboros_exact(x, lam=OUROBOROS_LAMBDA):
    """f(x) = x * (lam + (1-lam) * sigmoid(x))"""
    s = sigmoid(x)
    return x * (lam + (1 - lam) * s)

def ouroboros_exact_derivative(x, lam=OUROBOROS_LAMBDA):
    """Derivative of OuroborosExact."""
    s = sigmoid(x)
    g = lam + (1 - lam) * s
    gp = (1 - lam) * s * (1 - s)
    return g + x * gp

# ----- Standard Swish (SiLU) -----

def swish(x, beta=1.0):
    """f(x) = x * sigmoid(beta * x)"""
    return x * sigmoid(beta * x)

def swish_derivative(x, beta=1.0):
    """Derivative of Swish."""
    s = sigmoid(beta * x)
    return s + beta * x * s * (1 - s)

# ----- Mish -----

def mish(x):
    """f(x) = x * tanh(softplus(x))"""
    return x * np.tanh(softplus(x))

def mish_derivative(x):
    """Derivative of Mish."""
    sp = softplus(x)
    tanh_sp = np.tanh(sp)
    # d/dx[tanh(softplus(x))] = sech^2(softplus(x)) * sigmoid(x)
    sech_sq = 1 - tanh_sp ** 2
    return tanh_sp + x * sech_sq * sigmoid(x)

# ----- ReLU -----

def relu(x):
    """f(x) = max(0, x)"""
    return np.maximum(0, x)

def relu_derivative(x):
    """Derivative of ReLU."""
    return np.where(x > 0, 1.0, 0.0)

# ----- GELU -----

def gelu(x):
    """f(x) = x * Phi(x) where Phi is Gaussian CDF"""
    return x * 0.5 * (1 + erf(x / np.sqrt(2)))

def gelu_derivative(x):
    """Derivative of GELU."""
    phi_x = 0.5 * (1 + erf(x / np.sqrt(2)))
    phi_prime = np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
    return phi_x + x * phi_prime

# ============================================================================
# COMPUTE E[f'(x)^2] FOR EACH ACTIVATION
# ============================================================================

def compute_efprime_sq(derivative_fn, name=""):
    """Compute E[f'(x)^2] using numerical integration."""
    return gaussian_expectation(lambda x: derivative_fn(x) ** 2)

# ============================================================================
# PYTORCH ACTIVATION MODULES
# ============================================================================

class OuroborosExactModule(nn.Module):
    """OuroborosExact activation with optimal lambda."""
    def __init__(self):
        super().__init__()
        self.lam = OUROBOROS_LAMBDA

    def forward(self, x):
        s = torch.sigmoid(x)
        gate = self.lam + (1 - self.lam) * s
        return x * gate

class SwishModule(nn.Module):
    """Standard Swish/SiLU activation."""
    def __init__(self, beta=1.0):
        super().__init__()
        self.beta = beta

    def forward(self, x):
        return x * torch.sigmoid(self.beta * x)

class MishModule(nn.Module):
    """Mish activation."""
    def forward(self, x):
        return x * torch.tanh(nn.functional.softplus(x))

class ReLUModule(nn.Module):
    """ReLU activation."""
    def forward(self, x):
        return torch.relu(x)

class GELUModule(nn.Module):
    """GELU activation."""
    def forward(self, x):
        return nn.functional.gelu(x)

# ============================================================================
# MONTE CARLO VERIFICATION OF E[f'(x)^2]
# ============================================================================

def monte_carlo_efprime_sq(activation_module, n_samples=500000):
    """Compute E[f'(x)^2] using Monte Carlo with autodiff."""
    torch.manual_seed(42)
    x = torch.randn(n_samples, requires_grad=True)
    y = activation_module(x)
    fprime = torch.autograd.grad(y.sum(), x)[0]
    return (fprime ** 2).mean().item()

# ============================================================================
# GRADIENT FLOW STABILITY TEST
# ============================================================================

def test_gradient_flow(activation_class, critical_scale, n_layers, hidden_dim=256, n_trials=50):
    """
    Test gradient flow stability by measuring gradient variance across layers.

    Returns:
        grad_norms: list of gradient norms at each layer
        grad_var: variance of gradient norms
        stable: True if gradient norms don't explode/vanish
    """
    torch.manual_seed(42)

    grad_norms_per_trial = []

    for trial in range(n_trials):
        # Build deep network
        layers = []
        for i in range(n_layers):
            linear = nn.Linear(hidden_dim, hidden_dim, bias=False)
            # Initialize with critical scale
            nn.init.normal_(linear.weight, mean=0, std=critical_scale / np.sqrt(hidden_dim))
            layers.append(linear)
            layers.append(activation_class())

        model = nn.Sequential(*layers)

        # Forward pass
        x = torch.randn(32, hidden_dim)
        y = model(x)
        loss = y.sum()

        # Backward pass
        loss.backward()

        # Collect gradient norms at each layer
        layer_grad_norms = []
        for i, layer in enumerate(model):
            if hasattr(layer, 'weight') and layer.weight.grad is not None:
                grad_norm = layer.weight.grad.norm().item()
                layer_grad_norms.append(grad_norm)

        grad_norms_per_trial.append(layer_grad_norms)

    # Average across trials
    grad_norms_per_trial = np.array(grad_norms_per_trial)
    mean_grad_norms = grad_norms_per_trial.mean(axis=0)

    # Compute variance of final layer gradient norm across trials
    final_layer_grads = grad_norms_per_trial[:, -1] if grad_norms_per_trial.shape[1] > 0 else [0]
    grad_var = np.var(final_layer_grads)

    # Check stability: gradient shouldn't explode (>1e3) or vanish (<1e-6)
    stable = 1e-6 < np.mean(final_layer_grads) < 1e3

    return mean_grad_norms, grad_var, stable

# ============================================================================
# SIGNAL PROPAGATION TEST
# ============================================================================

def test_signal_propagation(activation_class, critical_scale, n_layers, hidden_dim=256, n_trials=100):
    """
    Test signal propagation by measuring variance at each layer.

    At criticality, variance should be preserved across layers.
    """
    torch.manual_seed(42)

    variances_per_trial = []

    for trial in range(n_trials):
        # Build network
        layers = []
        for i in range(n_layers):
            linear = nn.Linear(hidden_dim, hidden_dim, bias=False)
            nn.init.normal_(linear.weight, mean=0, std=critical_scale / np.sqrt(hidden_dim))
            layers.append(linear)
            layers.append(activation_class())

        model = nn.Sequential(*layers)

        # Forward pass, collecting activations
        x = torch.randn(64, hidden_dim)
        layer_variances = [x.var().item()]

        with torch.no_grad():
            h = x
            for i, layer in enumerate(model):
                h = layer(h)
                if i % 2 == 1:  # After each activation
                    layer_variances.append(h.var().item())

        variances_per_trial.append(layer_variances)

    # Average across trials
    variances_per_trial = np.array(variances_per_trial)
    mean_variances = variances_per_trial.mean(axis=0)

    return mean_variances

# ============================================================================
# MAIN COMPARISON
# ============================================================================

def main():
    print("=" * 70)
    print("ACTIVATION COMPARISON: OuroborosExact vs Swish vs Mish vs ReLU")
    print("=" * 70)
    print()

    # -------------------------------------------------------------------------
    # Part 1: E[f'(x)^2] and Critical Scale Analysis
    # -------------------------------------------------------------------------

    print("-" * 70)
    print("PART 1: E[f'(x)^2] and Critical Scale Analysis")
    print("-" * 70)
    print()
    print(f"Target E[f'(x)^2] = 1/(3-phi)^2 = {TARGET_E_FPRIME_SQ:.10f}")
    print(f"Target Critical Scale = (3-phi) = {THREE_MINUS_PHI:.10f}")
    print()

    activations = [
        ("OuroborosExact", ouroboros_exact_derivative, OuroborosExactModule),
        ("Swish (SiLU)", swish_derivative, SwishModule),
        ("Mish", mish_derivative, MishModule),
        ("ReLU", relu_derivative, ReLUModule),
        ("GELU", gelu_derivative, GELUModule),
    ]

    results = {}

    print("Computing E[f'(x)^2] (numerical integration)...")
    print()

    for name, deriv_fn, module_class in activations:
        # Numerical integration
        efprime_sq_theory = compute_efprime_sq(deriv_fn, name)
        critical_scale = 1 / np.sqrt(efprime_sq_theory)
        error_from_target = abs(critical_scale - THREE_MINUS_PHI)

        # Monte Carlo verification
        module = module_class()
        efprime_sq_mc = monte_carlo_efprime_sq(module)

        results[name] = {
            'efprime_sq_theory': efprime_sq_theory,
            'efprime_sq_mc': efprime_sq_mc,
            'critical_scale': critical_scale,
            'error_from_target': error_from_target,
            'module_class': module_class,
        }

    # Print comparison table
    print("=" * 80)
    print("CRITICAL SCALE COMPARISON")
    print("=" * 80)
    print()
    print(f"{'Activation':<18} {'E[f\'(x)^2]':>12} {'E[f\'(x)^2]':>12} {'Critical':>12} {'Error from':>12} {'Status':>10}")
    print(f"{'':<18} {'(theory)':>12} {'(MC)':>12} {'Scale':>12} {'(3-phi)':>12} {'':<10}")
    print("-" * 80)

    for name in ["OuroborosExact", "Swish (SiLU)", "Mish", "ReLU", "GELU"]:
        r = results[name]
        err = r['error_from_target']
        if err < 1e-8:
            status = "EXACT"
        elif err < 0.01:
            status = "close"
        elif err < 0.1:
            status = "off"
        else:
            status = "far"

        print(f"{name:<18} {r['efprime_sq_theory']:>12.6f} {r['efprime_sq_mc']:>12.6f} "
              f"{r['critical_scale']:>12.6f} {r['error_from_target']:>12.6f} {status:>10}")

    print("-" * 80)
    print()

    # -------------------------------------------------------------------------
    # Part 2: Gradient Flow Stability
    # -------------------------------------------------------------------------

    print("-" * 70)
    print("PART 2: Gradient Flow Stability (using optimal critical scale for each)")
    print("-" * 70)
    print()

    depths = [10, 30, 50, 100]

    print("Testing gradient flow at various depths...")
    print("(Each activation uses its own optimal critical scale)")
    print()

    print("=" * 90)
    print("GRADIENT FLOW STABILITY")
    print("=" * 90)
    print()

    for depth in depths:
        print(f"--- Depth: {depth} layers ---")
        print(f"{'Activation':<18} {'Critical Scale':>14} {'Final Grad Norm':>16} {'Grad Variance':>14} {'Stable?':>10}")
        print("-" * 72)

        for name in ["OuroborosExact", "Swish (SiLU)", "Mish", "ReLU", "GELU"]:
            r = results[name]
            crit_scale = r['critical_scale']
            module_class = r['module_class']

            grad_norms, grad_var, stable = test_gradient_flow(
                module_class, crit_scale, depth, hidden_dim=128, n_trials=20
            )

            final_grad = grad_norms[-1] if len(grad_norms) > 0 else 0
            stable_str = "Yes" if stable else "No"

            results[name][f'grad_var_{depth}'] = grad_var
            results[name][f'final_grad_{depth}'] = final_grad
            results[name][f'stable_{depth}'] = stable

            print(f"{name:<18} {crit_scale:>14.6f} {final_grad:>16.6f} {grad_var:>14.6f} {stable_str:>10}")

        print()

    # -------------------------------------------------------------------------
    # Part 3: Signal Propagation
    # -------------------------------------------------------------------------

    print("-" * 70)
    print("PART 3: Signal Propagation (Variance Preservation)")
    print("-" * 70)
    print()

    print("Testing signal propagation at 50 layers...")
    print("(Each activation uses its own optimal critical scale)")
    print("(Values should stay near 1.0 for good preservation)")
    print()

    depth = 50
    print("=" * 90)
    print("SIGNAL PROPAGATION (50 layers)")
    print("=" * 90)
    print()
    print(f"{'Activation':<18} {'Input Var':>12} {'Layer 10':>12} {'Layer 25':>12} {'Layer 40':>12} {'Layer 50':>12}")
    print("-" * 78)

    for name in ["OuroborosExact", "Swish (SiLU)", "Mish", "ReLU", "GELU"]:
        r = results[name]
        crit_scale = r['critical_scale']
        module_class = r['module_class']

        variances = test_signal_propagation(module_class, crit_scale, depth, hidden_dim=128, n_trials=30)

        # Get variances at key checkpoints
        v_input = variances[0]
        v_10 = variances[10] if len(variances) > 10 else variances[-1]
        v_25 = variances[25] if len(variances) > 25 else variances[-1]
        v_40 = variances[40] if len(variances) > 40 else variances[-1]
        v_50 = variances[-1]

        results[name]['variances_50'] = variances

        print(f"{name:<18} {v_input:>12.4f} {v_10:>12.4f} {v_25:>12.4f} {v_40:>12.4f} {v_50:>12.4f}")

    print()

    # -------------------------------------------------------------------------
    # Part 4: Comparison with (3-phi) Target
    # -------------------------------------------------------------------------

    print("-" * 70)
    print("PART 4: Distance from Golden Ratio Critical Scale (3-phi)")
    print("-" * 70)
    print()

    print(f"Target: (3-phi) = {THREE_MINUS_PHI:.10f}")
    print(f"Target: E[f'(x)^2] = 1/(3-phi)^2 = {TARGET_E_FPRIME_SQ:.10f}")
    print()

    print("=" * 70)
    print("SUMMARY: HOW FAR IS EACH ACTIVATION FROM THE (3-phi) TARGET?")
    print("=" * 70)
    print()
    print(f"{'Activation':<18} {'Critical Scale':>14} {'Error':>12} {'% Error':>10} {'Efprime_sq Error':>18}")
    print("-" * 72)

    for name in ["OuroborosExact", "Swish (SiLU)", "Mish", "ReLU", "GELU"]:
        r = results[name]
        crit_scale = r['critical_scale']
        err = r['error_from_target']
        pct_err = err / THREE_MINUS_PHI * 100
        efp_err = abs(r['efprime_sq_theory'] - TARGET_E_FPRIME_SQ)

        print(f"{name:<18} {crit_scale:>14.6f} {err:>12.8f} {pct_err:>10.4f}% {efp_err:>18.8f}")

    print("-" * 72)
    print()

    # -------------------------------------------------------------------------
    # Final Summary
    # -------------------------------------------------------------------------

    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print()
    print("KEY FINDING:")
    print("-" * 40)

    ouro_err = results["OuroborosExact"]['error_from_target']
    swish_err = results["Swish (SiLU)"]['error_from_target']
    mish_err = results["Mish"]['error_from_target']
    relu_err = results["ReLU"]['error_from_target']
    gelu_err = results["GELU"]['error_from_target']

    print(f"OuroborosExact hits the (3-phi) target with error: {ouro_err:.2e}")
    print(f"Swish is off by: {swish_err:.6f} ({swish_err/THREE_MINUS_PHI*100:.2f}%)")
    print(f"Mish is off by: {mish_err:.6f} ({mish_err/THREE_MINUS_PHI*100:.2f}%)")
    print(f"ReLU is off by: {relu_err:.6f} ({relu_err/THREE_MINUS_PHI*100:.2f}%)")
    print(f"GELU is off by: {gelu_err:.6f} ({gelu_err/THREE_MINUS_PHI*100:.2f}%)")
    print()

    print("INTERPRETATION:")
    print("-" * 40)
    print("1. OuroborosExact is specifically designed to hit critical scale = (3-phi)")
    print("2. Standard Swish/Mish have E[f'(x)^2] too LOW, giving critical scales too HIGH")
    print("3. ReLU is closer to target because E[f'(x)^2] = 0.5 is close to 0.5236")
    print("4. The (3-phi) critical point is accessible only through careful tuning")
    print()

    print("WHY (3-phi) MATTERS:")
    print("-" * 40)
    print("(3-phi) = 1 + 1/phi^2 encodes the structure of D^2 - 3D + 1 = 0")
    print("This is the Ouroboros equation connecting golden ratio physics to")
    print("optimal neural network initialization at the edge of chaos.")
    print()

    return results

if __name__ == "__main__":
    results = main()
