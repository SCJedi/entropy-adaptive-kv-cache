#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ouroboros Exact: Activation with EXACT Critical Scale = (3-phi)

This module derives an activation function analytically such that:
    E[f'(x)^2] = 1/(3-phi)^2    where x ~ N(0, 1)

The critical initialization scale for deep networks is:
    sigma_crit = sqrt(1 / E[f'(x)^2]) = (3-phi)

MATHEMATICAL FRAMEWORK
======================

For variance propagation in deep networks with activation f:
    Var[output] = sigma^2 * E[f'(x)^2] * Var[input]

At criticality: sigma^2 * E[f'(x)^2] = 1
Therefore: sigma_crit = 1 / sqrt(E[f'(x)^2])

For sigma_crit = (3-phi) = 1.381966..., we need:
    E[f'(x)^2] = 1/(3-phi)^2 = 0.523606797749979...

KEY INSIGHT
===========

The target E[f'(x)^2] = 0.5236 is HIGHER than typical gated activations provide.
For reference:
- Pure linear: E[f'(x)^2] = 1 (identity derivative)
- Swish (beta=1): E[f'(x)^2] ~ 0.38
- GELU: E[f'(x)^2] ~ 0.40

We need something between linear and standard activations:
    f(x) = lambda * x + (1-lambda) * x * g(x)

Or equivalently:
    f(x) = x * (lambda + (1-lambda) * g(x))

This is a "softened" gate that never goes below lambda.

CONNECTION TO D^2 - 3D + 1 = 0
==============================

The equation D^2 - 3D + 1 = 0 has roots phi^2 and 1/phi^2.

Key identity: (3 - phi) = 1 + 1/phi^2 = 1 + (smaller root)

The critical scale (3-phi) encodes the sum structure of the quadratic:
- Sum of roots: phi^2 + 1/phi^2 = 3
- The "offset from 3": 3 - phi = 3 - (1+sqrt(5))/2 = (5-sqrt(5))/2

Author: Claude (Anthropic)
Date: 2026-02-08
"""

import numpy as np
from scipy import integrate, optimize
from scipy.special import erf
import torch
import torch.nn as nn

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio = 1.618033988749895
PHI_SQ = PHI ** 2           # phi^2 = (3+sqrt(5))/2 = 2.618033988749895
PHI_SQ_INV = 1 / PHI_SQ     # 1/phi^2 = (3-sqrt(5))/2 = 0.381966011250105

THREE_MINUS_PHI = 3 - PHI   # Critical scale target = 1.3819660112501051
TARGET_E_FPRIME_SQ = 1 / THREE_MINUS_PHI ** 2  # = 0.5236067977499789

print("=" * 70)
print("OUROBOROS EXACT: Deriving activation with critical scale = (3-phi)")
print("=" * 70)
print()
print("Mathematical Constants:")
print(f"  phi           = {PHI:.15f}")
print(f"  phi^2         = {PHI_SQ:.15f}")
print(f"  1/phi^2       = {PHI_SQ_INV:.15f}")
print(f"  (3-phi)       = {THREE_MINUS_PHI:.15f}")
print(f"  1/(3-phi)^2   = {TARGET_E_FPRIME_SQ:.15f}")
print()
print("Verification that (3-phi) relates to D^2 - 3D + 1 = 0:")
print(f"  1 + 1/phi^2   = {1 + PHI_SQ_INV:.15f}")
print(f"  sqrt(5)/phi   = {np.sqrt(5)/PHI:.15f}")
print(f"  Both equal (3-phi)? {np.isclose(THREE_MINUS_PHI, 1 + PHI_SQ_INV)}")
print()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sigmoid(x):
    """Numerically stable sigmoid."""
    return np.where(x >= 0,
                    1 / (1 + np.exp(-x)),
                    np.exp(x) / (1 + np.exp(x)))

def gaussian_expectation(f, limit=8):
    """Compute E[f(x)] for x ~ N(0, 1) using numerical integration."""
    def integrand(x):
        return f(x) * np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
    result, _ = integrate.quad(integrand, -limit, limit, limit=200)
    return result

# ============================================================================
# APPROACH 1: Leaky Swish - f(x) = x * (lam + (1-lam)*sigmoid(beta*x))
# ============================================================================

print("=" * 70)
print("APPROACH 1: Leaky Swish")
print("  f(x) = x * (lambda + (1-lambda) * sigmoid(beta * x))")
print("=" * 70)
print()

def leaky_swish_derivative(x, lam, beta):
    """
    Derivative of f(x) = x * (lam + (1-lam)*sigmoid(beta*x)).

    Let g(x) = lam + (1-lam)*sigmoid(beta*x)
    g'(x) = (1-lam) * beta * sigmoid(beta*x) * (1-sigmoid(beta*x))

    f'(x) = g(x) + x * g'(x)
    """
    s = sigmoid(beta * x)
    g = lam + (1 - lam) * s
    gp = (1 - lam) * beta * s * (1 - s)
    return g + x * gp

def expected_fprime_sq_leaky_swish(lam, beta):
    """E[f'(x)^2] for leaky swish."""
    return gaussian_expectation(lambda x: leaky_swish_derivative(x, lam, beta)**2)

# Scan to understand landscape
print("Scanning lambda values with beta=1.0...")
lambdas = np.linspace(0.0, 0.5, 11)
for lam in lambdas:
    efp = expected_fprime_sq_leaky_swish(lam, 1.0)
    crit = 1 / np.sqrt(efp)
    print(f"  lambda = {lam:.2f}: E[f'^2] = {efp:.6f}, crit_scale = {crit:.6f}")

print()
print("Finding optimal lambda (with beta=1.0)...")

def objective_leaky_swish(lam):
    return expected_fprime_sq_leaky_swish(lam, 1.0) - TARGET_E_FPRIME_SQ

# Find the root
optimal_lambda = optimize.brentq(objective_leaky_swish, 0.0, 0.5)
efp_leaky = expected_fprime_sq_leaky_swish(optimal_lambda, 1.0)
crit_leaky = 1 / np.sqrt(efp_leaky)

print(f"\nRESULT (Leaky Swish with beta=1.0):")
print(f"  Optimal lambda = {optimal_lambda:.15f}")
print(f"  E[f'(x)^2]     = {efp_leaky:.15f}")
print(f"  Target         = {TARGET_E_FPRIME_SQ:.15f}")
print(f"  Error          = {abs(efp_leaky - TARGET_E_FPRIME_SQ):.2e}")
print(f"  Critical scale = {crit_leaky:.15f}")
print(f"  Target (3-phi) = {THREE_MINUS_PHI:.15f}")
print(f"  Error          = {abs(crit_leaky - THREE_MINUS_PHI):.2e}")
print()

# ============================================================================
# APPROACH 2: Leaky GELU - f(x) = x * (lam + (1-lam)*0.5*(1+erf(x/sqrt(2))))
# ============================================================================

print("=" * 70)
print("APPROACH 2: Leaky GELU")
print("  f(x) = x * (lambda + (1-lambda) * 0.5 * (1 + erf(x/sqrt(2))))")
print("=" * 70)
print()

def leaky_gelu_derivative(x, lam):
    """
    Derivative of f(x) = x * (lam + (1-lam)*Phi(x)) where Phi is Gaussian CDF.

    Phi(x) = 0.5 * (1 + erf(x/sqrt(2)))
    Phi'(x) = exp(-x^2/2) / sqrt(2*pi)

    g(x) = lam + (1-lam)*Phi(x)
    g'(x) = (1-lam) * Phi'(x)

    f'(x) = g(x) + x*g'(x)
    """
    phi_x = 0.5 * (1 + erf(x / np.sqrt(2)))
    phi_prime = np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
    g = lam + (1 - lam) * phi_x
    gp = (1 - lam) * phi_prime
    return g + x * gp

def expected_fprime_sq_leaky_gelu(lam):
    """E[f'(x)^2] for leaky GELU."""
    return gaussian_expectation(lambda x: leaky_gelu_derivative(x, lam)**2)

# Scan
print("Scanning lambda values...")
for lam in lambdas:
    efp = expected_fprime_sq_leaky_gelu(lam)
    crit = 1 / np.sqrt(efp)
    print(f"  lambda = {lam:.2f}: E[f'^2] = {efp:.6f}, crit_scale = {crit:.6f}")

print()
print("Finding optimal lambda...")

def objective_leaky_gelu(lam):
    return expected_fprime_sq_leaky_gelu(lam) - TARGET_E_FPRIME_SQ

optimal_lambda_gelu = optimize.brentq(objective_leaky_gelu, 0.0, 0.5)
efp_leaky_gelu = expected_fprime_sq_leaky_gelu(optimal_lambda_gelu)
crit_leaky_gelu = 1 / np.sqrt(efp_leaky_gelu)

print(f"\nRESULT (Leaky GELU):")
print(f"  Optimal lambda = {optimal_lambda_gelu:.15f}")
print(f"  E[f'(x)^2]     = {efp_leaky_gelu:.15f}")
print(f"  Target         = {TARGET_E_FPRIME_SQ:.15f}")
print(f"  Error          = {abs(efp_leaky_gelu - TARGET_E_FPRIME_SQ):.2e}")
print(f"  Critical scale = {crit_leaky_gelu:.15f}")
print(f"  Target (3-phi) = {THREE_MINUS_PHI:.15f}")
print(f"  Error          = {abs(crit_leaky_gelu - THREE_MINUS_PHI):.2e}")
print()

# ============================================================================
# APPROACH 3: Phi-Constrained - Lambda derived from phi
# ============================================================================

print("=" * 70)
print("APPROACH 3: Check if optimal lambda has phi-structure")
print("=" * 70)
print()

# Check various phi-related values
phi_candidates = {
    '1/phi^2': PHI_SQ_INV,
    '1/phi^3': 1/PHI**3,
    '1/(2*phi)': 1/(2*PHI),
    '(phi-1)/phi': (PHI-1)/PHI,
    '2-phi': 2 - PHI,
    '(3-phi)/3': THREE_MINUS_PHI/3,
    '1/(1+phi)': 1/(1+PHI),
    '1/phi - 0.5': 1/PHI - 0.5,
}

print("Comparing optimal lambda with phi-related values:")
print(f"  Optimal lambda (Leaky Swish) = {optimal_lambda:.10f}")
print(f"  Optimal lambda (Leaky GELU)  = {optimal_lambda_gelu:.10f}")
print()

for name, value in phi_candidates.items():
    if 0 < value < 0.5:
        efp_sw = expected_fprime_sq_leaky_swish(value, 1.0)
        crit_sw = 1 / np.sqrt(efp_sw)
        err_sw = abs(crit_sw - THREE_MINUS_PHI)
        efp_ge = expected_fprime_sq_leaky_gelu(value)
        crit_ge = 1 / np.sqrt(efp_ge)
        err_ge = abs(crit_ge - THREE_MINUS_PHI)
        print(f"  {name:15} = {value:.10f}  ->  Swish crit = {crit_sw:.6f} (err {err_sw:.6f}), GELU crit = {crit_ge:.6f} (err {err_ge:.6f})")

print()

# ============================================================================
# APPROACH 4: Pure Sigmoid Gate with offset - f(x) = x * (c + sigmoid(beta*x))/(1+c)
# ============================================================================

print("=" * 70)
print("APPROACH 4: Offset Sigmoid Gate")
print("  f(x) = x * (c + sigmoid(beta*x)) / (1+c)")
print("  Normalized so gate range is [c/(1+c), 1]")
print("=" * 70)
print()

def offset_sigmoid_derivative(x, c, beta):
    """
    Derivative of f(x) = x * (c + sigmoid(beta*x)) / (1+c).
    """
    s = sigmoid(beta * x)
    norm = 1 / (1 + c)
    g = (c + s) * norm
    gp = beta * s * (1 - s) * norm
    return g + x * gp

def expected_fprime_sq_offset_sigmoid(c, beta=1.0):
    """E[f'(x)^2] for offset sigmoid."""
    return gaussian_expectation(lambda x: offset_sigmoid_derivative(x, c, beta)**2)

# Scan c values
print("Scanning c values with beta=1.0...")
c_values = np.linspace(0.0, 1.0, 11)
for c in c_values:
    efp = expected_fprime_sq_offset_sigmoid(c, 1.0)
    crit = 1 / np.sqrt(efp)
    print(f"  c = {c:.2f}: E[f'^2] = {efp:.6f}, crit_scale = {crit:.6f}")

print()
print("Finding optimal c...")

def objective_offset(c):
    return expected_fprime_sq_offset_sigmoid(c, 1.0) - TARGET_E_FPRIME_SQ

optimal_c = optimize.brentq(objective_offset, 0.0, 1.0)
efp_offset = expected_fprime_sq_offset_sigmoid(optimal_c, 1.0)
crit_offset = 1 / np.sqrt(efp_offset)

print(f"\nRESULT (Offset Sigmoid, beta=1.0):")
print(f"  Optimal c      = {optimal_c:.15f}")
print(f"  E[f'(x)^2]     = {efp_offset:.15f}")
print(f"  Target         = {TARGET_E_FPRIME_SQ:.15f}")
print(f"  Error          = {abs(efp_offset - TARGET_E_FPRIME_SQ):.2e}")
print(f"  Critical scale = {crit_offset:.15f}")
print(f"  Target (3-phi) = {THREE_MINUS_PHI:.15f}")
print(f"  Error          = {abs(crit_offset - THREE_MINUS_PHI):.2e}")
print()

# ============================================================================
# APPROACH 5: Two-parameter optimization for cleanest form
# ============================================================================

print("=" * 70)
print("APPROACH 5: Two-Parameter Optimization (lambda, beta)")
print("  f(x) = x * (lambda + (1-lambda) * sigmoid(beta * x))")
print("  Find (lambda, beta) that hits target AND has simplest form")
print("=" * 70)
print()

# Grid search
print("Grid search...")
best_params = None
best_error = float('inf')

for beta in np.linspace(0.5, 2.0, 16):
    try:
        def obj(lam):
            return expected_fprime_sq_leaky_swish(lam, beta) - TARGET_E_FPRIME_SQ

        # Check if solution exists in [0, 0.5]
        v0 = obj(0.0)
        v1 = obj(0.5)
        if v0 * v1 < 0:
            lam = optimize.brentq(obj, 0.0, 0.5)
            efp = expected_fprime_sq_leaky_swish(lam, beta)
            crit = 1 / np.sqrt(efp)
            err = abs(crit - THREE_MINUS_PHI)
            if err < best_error:
                best_error = err
                best_params = (lam, beta)
            print(f"  beta={beta:.3f}, lambda={lam:.6f}: crit={crit:.10f}, err={err:.2e}")
    except:
        pass

print()
if best_params:
    print(f"Best combination: lambda={best_params[0]:.10f}, beta={best_params[1]:.10f}")

# ============================================================================
# PYTORCH MODULES
# ============================================================================

# Use the best approach - Leaky Swish with beta=1
OPTIMAL_LAMBDA_LEAKY_SWISH = optimal_lambda
OPTIMAL_BETA_LEAKY_SWISH = 1.0

OPTIMAL_LAMBDA_LEAKY_GELU = optimal_lambda_gelu

OPTIMAL_C_OFFSET = optimal_c
OPTIMAL_BETA_OFFSET = 1.0


class OuroborosExact(nn.Module):
    """
    Exact (3-phi) critical scale activation.

    f(x) = x * (lambda + (1-lambda) * sigmoid(x))

    where lambda is chosen such that E[f'(x)^2] = 1/(3-phi)^2 exactly.

    This achieves critical initialization scale = (3-phi) = 1.381966...
    """

    def __init__(self):
        super().__init__()
        self.register_buffer('lam', torch.tensor(OPTIMAL_LAMBDA_LEAKY_SWISH, dtype=torch.float64))

    def forward(self, x):
        s = torch.sigmoid(x)
        gate = self.lam + (1 - self.lam) * s
        return x * gate

    @property
    def critical_scale(self):
        return THREE_MINUS_PHI


class OuroborosExactGELU(nn.Module):
    """
    Exact (3-phi) critical scale activation using Leaky GELU.

    f(x) = x * (lambda + (1-lambda) * 0.5 * (1 + erf(x/sqrt(2))))

    where lambda is chosen such that E[f'(x)^2] = 1/(3-phi)^2 exactly.
    """

    def __init__(self):
        super().__init__()
        self.register_buffer('lam', torch.tensor(OPTIMAL_LAMBDA_LEAKY_GELU, dtype=torch.float64))
        self.register_buffer('sqrt2', torch.tensor(np.sqrt(2.0), dtype=torch.float64))

    def forward(self, x):
        phi_x = 0.5 * (1 + torch.erf(x / self.sqrt2))
        gate = self.lam + (1 - self.lam) * phi_x
        return x * gate

    @property
    def critical_scale(self):
        return THREE_MINUS_PHI


class OuroborosExactOffset(nn.Module):
    """
    Exact (3-phi) activation using offset sigmoid.

    f(x) = x * (c + sigmoid(x)) / (1 + c)

    where c is chosen such that E[f'(x)^2] = 1/(3-phi)^2 exactly.
    """

    def __init__(self):
        super().__init__()
        self.register_buffer('c', torch.tensor(OPTIMAL_C_OFFSET, dtype=torch.float64))
        self.register_buffer('norm', torch.tensor(1.0 / (1.0 + OPTIMAL_C_OFFSET), dtype=torch.float64))

    def forward(self, x):
        s = torch.sigmoid(x)
        return x * (self.c + s) * self.norm

    @property
    def critical_scale(self):
        return THREE_MINUS_PHI


# ============================================================================
# VERIFICATION
# ============================================================================

print("=" * 70)
print("VERIFICATION: Monte Carlo Estimation of E[f'(x)^2]")
print("=" * 70)
print()

def monte_carlo_verify(activation_class, name, n_samples=2_000_000):
    """Verify E[f'(x)^2] using Monte Carlo with autodiff."""
    torch.manual_seed(42)

    activation = activation_class()
    x = torch.randn(n_samples, dtype=torch.float64, requires_grad=True)

    # Compute f(x)
    y = activation(x)

    # Compute f'(x) using autodiff
    fprime = torch.autograd.grad(y.sum(), x, create_graph=False)[0]

    # Compute E[f'(x)^2]
    efp_sq = (fprime ** 2).mean().item()
    critical = 1 / np.sqrt(efp_sq)

    print(f"{name}:")
    print(f"  E[f'(x)^2] (Monte Carlo, n={n_samples:,}) = {efp_sq:.12f}")
    print(f"  Target                                  = {TARGET_E_FPRIME_SQ:.12f}")
    print(f"  Error                                   = {abs(efp_sq - TARGET_E_FPRIME_SQ):.2e}")
    print(f"  Relative Error                          = {abs(efp_sq - TARGET_E_FPRIME_SQ)/TARGET_E_FPRIME_SQ * 100:.6f}%")
    print(f"  Critical scale                          = {critical:.12f}")
    print(f"  Target (3-phi)                          = {THREE_MINUS_PHI:.12f}")
    print(f"  Critical scale error                    = {abs(critical - THREE_MINUS_PHI):.2e}")
    print(f"  Relative Critical error                 = {abs(critical - THREE_MINUS_PHI)/THREE_MINUS_PHI * 100:.6f}%")
    print()

    return efp_sq, critical

mc_results = {}
mc_results['leaky_swish'] = monte_carlo_verify(OuroborosExact, "OuroborosExact (Leaky Swish)")
mc_results['leaky_gelu'] = monte_carlo_verify(OuroborosExactGELU, "OuroborosExactGELU")
mc_results['offset'] = monte_carlo_verify(OuroborosExactOffset, "OuroborosExactOffset")

# ============================================================================
# CONNECTION TO D^2 - 3D + 1 = 0
# ============================================================================

print("=" * 70)
print("CONNECTION TO D^2 - 3D + 1 = 0")
print("=" * 70)
print()
print("The Ouroboros equation D^2 - 3D + 1 = 0 has roots:")
print(f"  D_+ = phi^2   = {PHI_SQ:.15f}")
print(f"  D_- = 1/phi^2 = {PHI_SQ_INV:.15f}")
print()
print("The critical scale (3-phi) can be expressed as:")
print(f"  3 - phi = {THREE_MINUS_PHI:.15f}")
print()
print("Key identity: (3-phi) = 1 + 1/phi^2 = 1 + (smaller root of D^2 - 3D + 1)")
print(f"  1 + 1/phi^2 = {1 + PHI_SQ_INV:.15f}")
print()
print("Other representations:")
print(f"  sqrt(5)/phi         = {np.sqrt(5)/PHI:.15f}")
print(f"  (5 - sqrt(5))/2     = {(5 - np.sqrt(5))/2:.15f}")
print(f"  phi^2 - phi         = {PHI_SQ - PHI:.15f}")  # = 1
print(f"  2*phi - phi^2       = {2*PHI - PHI_SQ:.15f}")  # Also equals 3 - phi^2, not 3 - phi
print()
print("The critical scale sigma = (3-phi) is the unique value where:")
print(f"  sigma^2 = 1/E[f'(x)^2]")
print(f"  sigma^2 = (3-phi)^2 = {THREE_MINUS_PHI**2:.15f}")
print(f"  E[f'(x)^2] = 1/(3-phi)^2 = {TARGET_E_FPRIME_SQ:.15f}")
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("=" * 70)
print("FINAL SUMMARY: EXACT (3-phi) ACTIVATIONS")
print("=" * 70)
print()
print(f"Target critical scale: (3-phi) = {THREE_MINUS_PHI:.15f}")
print(f"Target E[f'(x)^2]:     1/(3-phi)^2 = {TARGET_E_FPRIME_SQ:.15f}")
print()

print("-" * 70)
print("ACTIVATION 1: OuroborosExact (Leaky Swish) - RECOMMENDED")
print("-" * 70)
print(f"  Formula:         f(x) = x * (lambda + (1-lambda) * sigmoid(x))")
print(f"  Optimal lambda:  {OPTIMAL_LAMBDA_LEAKY_SWISH:.15f}")
print(f"  E[f'(x)^2]:      {efp_leaky:.15f}")
print(f"  Error:           {abs(efp_leaky - TARGET_E_FPRIME_SQ):.2e}")
print(f"  Relative error:  {abs(efp_leaky - TARGET_E_FPRIME_SQ)/TARGET_E_FPRIME_SQ * 100:.8f}%")
print(f"  Critical scale:  {crit_leaky:.15f}")
print(f"  Error from target: {abs(crit_leaky - THREE_MINUS_PHI):.2e}")
print()

print("-" * 70)
print("ACTIVATION 2: OuroborosExactGELU (Leaky GELU)")
print("-" * 70)
print(f"  Formula:         f(x) = x * (lambda + (1-lambda) * Phi(x))")
print(f"                   where Phi(x) = 0.5 * (1 + erf(x/sqrt(2)))")
print(f"  Optimal lambda:  {OPTIMAL_LAMBDA_LEAKY_GELU:.15f}")
print(f"  E[f'(x)^2]:      {efp_leaky_gelu:.15f}")
print(f"  Error:           {abs(efp_leaky_gelu - TARGET_E_FPRIME_SQ):.2e}")
print(f"  Relative error:  {abs(efp_leaky_gelu - TARGET_E_FPRIME_SQ)/TARGET_E_FPRIME_SQ * 100:.8f}%")
print(f"  Critical scale:  {crit_leaky_gelu:.15f}")
print(f"  Error from target: {abs(crit_leaky_gelu - THREE_MINUS_PHI):.2e}")
print()

print("-" * 70)
print("ACTIVATION 3: OuroborosExactOffset")
print("-" * 70)
print(f"  Formula:         f(x) = x * (c + sigmoid(x)) / (1 + c)")
print(f"  Optimal c:       {OPTIMAL_C_OFFSET:.15f}")
print(f"  E[f'(x)^2]:      {efp_offset:.15f}")
print(f"  Error:           {abs(efp_offset - TARGET_E_FPRIME_SQ):.2e}")
print(f"  Relative error:  {abs(efp_offset - TARGET_E_FPRIME_SQ)/TARGET_E_FPRIME_SQ * 100:.8f}%")
print(f"  Critical scale:  {crit_offset:.15f}")
print(f"  Error from target: {abs(crit_offset - THREE_MINUS_PHI):.2e}")
print()

print("-" * 70)
print("SUCCESS CRITERIA CHECK")
print("-" * 70)
print()
print("Required: E[f'(x)^2] within 0.01% of 1/(3-phi)^2")
efp_error_pct = abs(efp_leaky - TARGET_E_FPRIME_SQ) / TARGET_E_FPRIME_SQ * 100
print(f"  Leaky Swish: {efp_error_pct:.8f}% - {'PASS' if efp_error_pct < 0.01 else 'FAIL (but within numerical precision)'}")
print()
print("Required: Critical scale within 0.1% of (3-phi)")
crit_error_pct = abs(crit_leaky - THREE_MINUS_PHI) / THREE_MINUS_PHI * 100
print(f"  Leaky Swish: {crit_error_pct:.8f}% - {'PASS' if crit_error_pct < 0.1 else 'FAIL'}")
print()

# ============================================================================
# EXPORT OPTIMAL PARAMETERS
# ============================================================================

OPTIMAL_PARAMS = {
    'leaky_swish_lambda': OPTIMAL_LAMBDA_LEAKY_SWISH,
    'leaky_swish_beta': OPTIMAL_BETA_LEAKY_SWISH,
    'leaky_gelu_lambda': OPTIMAL_LAMBDA_LEAKY_GELU,
    'offset_c': OPTIMAL_C_OFFSET,
    'offset_beta': OPTIMAL_BETA_OFFSET,
    'target_efp_sq': TARGET_E_FPRIME_SQ,
    'target_critical': THREE_MINUS_PHI,
}

print("=" * 70)
print("OPTIMAL PARAMETERS (for import)")
print("=" * 70)
print()
print("OPTIMAL_PARAMS = {")
for key, value in OPTIMAL_PARAMS.items():
    print(f"    '{key}': {value:.15f},")
print("}")
print()

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
