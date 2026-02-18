"""
Design Neural Network Activations that Hit Exactly (3-phi) = 1.3820

GOAL: Find activation functions where critical initialization scale = (3-phi) exactly.

CONTEXT:
- Mish: critical scale = 1.3852 (off by 0.0033)
- GELU: critical scale = 1.3941 (off by 0.0122)
- Target: (3-phi) = 1.381966...

APPROACHES:
1. Parametric GELU: f(x) = x * Phi(x/alpha) - sweep alpha
2. Parametric Mish: f(x) = x * tanh(beta * softplus(x)) - sweep beta
3. Blend: alpha * GELU + (1-alpha) * Mish - sweep alpha
4. Custom gate: f(x) = x * sigmoid(gamma*x + delta) - sweep gamma, delta
5. Scaled self-gating: f(x) = x * tanh(x/tau) - sweep tau

Author: Claude (Anthropic)
Date: 2026-02-08
"""

import numpy as np
from scipy.special import erf
from scipy.integrate import quad
from scipy.stats import norm
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
NU = 1 / THREE_MINUS_PHI    # Critical exponent ~ 0.7236

print("=" * 70)
print("DESIGN PHI-OPTIMAL ACTIVATION FUNCTIONS")
print("=" * 70)
print(f"\nTarget critical scale: (3-phi) = {TARGET_CRITICAL:.10f}")
print(f"Required E[f'(x)^2] = 1/(3-phi)^2 = {1/TARGET_CRITICAL**2:.10f}")
print()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def compute_E_f_prime_squared(f_derivative, sigma_input=1.0):
    """Compute E[f'(x)^2] for x ~ N(0, sigma^2)."""
    def integrand(x):
        pdf = np.exp(-x**2 / (2 * sigma_input**2)) / (np.sqrt(2 * np.pi) * sigma_input)
        return f_derivative(x)**2 * pdf
    result, _ = quad(integrand, -10*sigma_input, 10*sigma_input)
    return result

def get_theoretical_critical_scale(f_derivative):
    """Compute theoretical critical scale from E[f'(x)^2]."""
    E_prime_sq = compute_E_f_prime_squared(f_derivative)
    if E_prime_sq > 0:
        return 1.0 / np.sqrt(E_prime_sq)
    return float('inf')

def softplus(x):
    """Numerically stable softplus."""
    return np.where(x > 20, x, np.log1p(np.exp(x)))

def sigmoid(x):
    """Numerically stable sigmoid."""
    return np.where(x >= 0,
                    1 / (1 + np.exp(-x)),
                    np.exp(x) / (1 + np.exp(x)))

def sigmoid_derivative(x):
    """Derivative of sigmoid."""
    s = sigmoid(x)
    return s * (1 - s)

# ============================================================================
# PART 1: PARAMETRIC GELU
# ============================================================================

print("=" * 70)
print("PART 1: PARAMETRIC GELU")
print("f(x) = x * 0.5 * (1 + erf(x / (alpha * sqrt(2))))")
print("=" * 70)

def parametric_gelu(x, alpha):
    """GELU with tunable sharpness."""
    return x * 0.5 * (1 + erf(x / (alpha * np.sqrt(2))))

def parametric_gelu_derivative(x, alpha):
    """Derivative of parametric GELU."""
    cdf_part = 0.5 * (1 + erf(x / (alpha * np.sqrt(2))))
    pdf_part = np.exp(-x**2 / (2 * alpha**2)) / (np.sqrt(2 * np.pi) * alpha)
    return cdf_part + x * pdf_part

def find_alpha_for_target(target_scale=TARGET_CRITICAL):
    """Find alpha that gives target critical scale."""
    def objective(alpha):
        if alpha <= 0:
            return float('inf')
        deriv = lambda x: parametric_gelu_derivative(x, alpha)
        scale = get_theoretical_critical_scale(deriv)
        return (scale - target_scale)**2

    # Search in reasonable range
    result = minimize_scalar(objective, bounds=(0.5, 3.0), method='bounded')
    return result.x

alpha_optimal = find_alpha_for_target()
deriv_opt = lambda x: parametric_gelu_derivative(x, alpha_optimal)
scale_opt = get_theoretical_critical_scale(deriv_opt)

print(f"\n1.1 Optimal Parametric GELU:")
print(f"  alpha = {alpha_optimal:.10f}")
print(f"  Theoretical critical scale = {scale_opt:.10f}")
print(f"  Target (3-phi) = {TARGET_CRITICAL:.10f}")
print(f"  Error = {abs(scale_opt - TARGET_CRITICAL):.2e}")

# Verify: alpha=1 should give standard GELU
std_gelu_scale = get_theoretical_critical_scale(lambda x: parametric_gelu_derivative(x, 1.0))
print(f"\n1.2 Verification: alpha=1 gives scale = {std_gelu_scale:.6f} (should be ~1.481)")

# Store result
parametric_gelu_result = {
    'alpha': alpha_optimal,
    'theoretical_scale': scale_opt,
    'error': abs(scale_opt - TARGET_CRITICAL)
}

# ============================================================================
# PART 2: PARAMETRIC MISH
# ============================================================================

print("\n" + "=" * 70)
print("PART 2: PARAMETRIC MISH")
print("f(x) = x * tanh(beta * softplus(x))")
print("=" * 70)

def parametric_mish(x, beta):
    """Mish with tunable beta."""
    return x * np.tanh(beta * softplus(x))

def parametric_mish_derivative(x, beta):
    """Derivative of parametric Mish."""
    sp = softplus(x)
    tsp = np.tanh(beta * sp)
    sig = sigmoid(x)
    sech2 = 1 - tsp**2
    return tsp + x * beta * sech2 * sig

def find_beta_for_target(target_scale=TARGET_CRITICAL):
    """Find beta that gives target critical scale."""
    def objective(beta):
        if beta <= 0:
            return float('inf')
        deriv = lambda x: parametric_mish_derivative(x, beta)
        scale = get_theoretical_critical_scale(deriv)
        return (scale - target_scale)**2

    result = minimize_scalar(objective, bounds=(0.1, 5.0), method='bounded')
    return result.x

beta_optimal = find_beta_for_target()
deriv_opt_mish = lambda x: parametric_mish_derivative(x, beta_optimal)
scale_opt_mish = get_theoretical_critical_scale(deriv_opt_mish)

print(f"\n2.1 Optimal Parametric Mish:")
print(f"  beta = {beta_optimal:.10f}")
print(f"  Theoretical critical scale = {scale_opt_mish:.10f}")
print(f"  Target (3-phi) = {TARGET_CRITICAL:.10f}")
print(f"  Error = {abs(scale_opt_mish - TARGET_CRITICAL):.2e}")

# Verify: beta=1 should give standard Mish
std_mish_scale = get_theoretical_critical_scale(lambda x: parametric_mish_derivative(x, 1.0))
print(f"\n2.2 Verification: beta=1 gives scale = {std_mish_scale:.6f} (should be ~1.445)")

parametric_mish_result = {
    'beta': beta_optimal,
    'theoretical_scale': scale_opt_mish,
    'error': abs(scale_opt_mish - TARGET_CRITICAL)
}

# ============================================================================
# PART 3: BLEND ACTIVATION
# ============================================================================

print("\n" + "=" * 70)
print("PART 3: BLEND ACTIVATION")
print("f(x) = alpha * GELU(x) + (1-alpha) * Mish(x)")
print("=" * 70)

def gelu(x):
    return x * 0.5 * (1 + erf(x / np.sqrt(2)))

def gelu_derivative(x):
    return 0.5 * (1 + erf(x / np.sqrt(2))) + x * np.exp(-x**2/2) / np.sqrt(2*np.pi)

def mish(x):
    return x * np.tanh(softplus(x))

def mish_derivative(x):
    sp = softplus(x)
    tsp = np.tanh(sp)
    sig = sigmoid(x)
    sech2 = 1 - tsp**2
    return tsp + x * sech2 * sig

def blend_activation(x, alpha):
    """Blend between GELU and Mish."""
    return alpha * gelu(x) + (1 - alpha) * mish(x)

def blend_derivative(x, alpha):
    """Derivative of blend activation."""
    return alpha * gelu_derivative(x) + (1 - alpha) * mish_derivative(x)

def find_blend_alpha(target_scale=TARGET_CRITICAL):
    """Find alpha that gives target critical scale."""
    def objective(alpha):
        if alpha < 0 or alpha > 1:
            return float('inf')
        deriv = lambda x: blend_derivative(x, alpha)
        scale = get_theoretical_critical_scale(deriv)
        return (scale - target_scale)**2

    result = minimize_scalar(objective, bounds=(0, 1), method='bounded')
    return result.x

blend_alpha = find_blend_alpha()
deriv_blend = lambda x: blend_derivative(x, blend_alpha)
scale_blend = get_theoretical_critical_scale(deriv_blend)

print(f"\n3.1 Optimal Blend:")
print(f"  alpha = {blend_alpha:.10f} (weight on GELU)")
print(f"  (1-alpha) = {1-blend_alpha:.10f} (weight on Mish)")
print(f"  Theoretical critical scale = {scale_blend:.10f}")
print(f"  Target (3-phi) = {TARGET_CRITICAL:.10f}")
print(f"  Error = {abs(scale_blend - TARGET_CRITICAL):.2e}")

blend_result = {
    'alpha': blend_alpha,
    'theoretical_scale': scale_blend,
    'error': abs(scale_blend - TARGET_CRITICAL)
}

# ============================================================================
# PART 4: CUSTOM GATE - x * sigmoid(gamma*x + delta)
# ============================================================================

print("\n" + "=" * 70)
print("PART 4: CUSTOM GATE")
print("f(x) = x * sigmoid(gamma * x + delta)")
print("=" * 70)

def custom_gate(x, gamma, delta):
    """Custom gate with two parameters."""
    return x * sigmoid(gamma * x + delta)

def custom_gate_derivative(x, gamma, delta):
    """Derivative of custom gate."""
    s = sigmoid(gamma * x + delta)
    ds = s * (1 - s)
    return s + x * gamma * ds

def find_custom_gate_params(target_scale=TARGET_CRITICAL):
    """Find gamma, delta that give target critical scale."""
    def objective(params):
        gamma, delta = params
        if gamma <= 0:
            return float('inf')
        deriv = lambda x: custom_gate_derivative(x, gamma, delta)
        scale = get_theoretical_critical_scale(deriv)
        return (scale - target_scale)**2

    # Start from Swish (gamma=1, delta=0)
    result = minimize(objective, x0=[1.0, 0.0], method='Nelder-Mead',
                     options={'xatol': 1e-8, 'fatol': 1e-10})
    return result.x

gamma_opt, delta_opt = find_custom_gate_params()
deriv_custom = lambda x: custom_gate_derivative(x, gamma_opt, delta_opt)
scale_custom = get_theoretical_critical_scale(deriv_custom)

print(f"\n4.1 Optimal Custom Gate:")
print(f"  gamma = {gamma_opt:.10f}")
print(f"  delta = {delta_opt:.10f}")
print(f"  Theoretical critical scale = {scale_custom:.10f}")
print(f"  Target (3-phi) = {TARGET_CRITICAL:.10f}")
print(f"  Error = {abs(scale_custom - TARGET_CRITICAL):.2e}")

# Verify: gamma=1, delta=0 is Swish
swish_scale = get_theoretical_critical_scale(lambda x: custom_gate_derivative(x, 1.0, 0.0))
print(f"\n4.2 Verification: gamma=1, delta=0 (Swish) gives scale = {swish_scale:.6f}")

custom_gate_result = {
    'gamma': gamma_opt,
    'delta': delta_opt,
    'theoretical_scale': scale_custom,
    'error': abs(scale_custom - TARGET_CRITICAL)
}

# ============================================================================
# PART 5: SCALED SELF-GATING - x * tanh(x/tau)
# ============================================================================

print("\n" + "=" * 70)
print("PART 5: SCALED SELF-GATING")
print("f(x) = x * tanh(x / tau)")
print("=" * 70)

def scaled_tanh(x, tau):
    """Scaled self-gating with tanh."""
    return x * np.tanh(x / tau)

def scaled_tanh_derivative(x, tau):
    """Derivative of scaled tanh."""
    t = np.tanh(x / tau)
    sech2 = 1 - t**2
    return t + (x / tau) * sech2

def find_tau_for_target(target_scale=TARGET_CRITICAL):
    """Find tau that gives target critical scale."""
    def objective(tau):
        if tau <= 0:
            return float('inf')
        deriv = lambda x: scaled_tanh_derivative(x, tau)
        scale = get_theoretical_critical_scale(deriv)
        return (scale - target_scale)**2

    result = minimize_scalar(objective, bounds=(0.1, 5.0), method='bounded')
    return result.x

tau_optimal = find_tau_for_target()
deriv_tau = lambda x: scaled_tanh_derivative(x, tau_optimal)
scale_tau = get_theoretical_critical_scale(deriv_tau)

print(f"\n5.1 Optimal Scaled Tanh:")
print(f"  tau = {tau_optimal:.10f}")
print(f"  Theoretical critical scale = {scale_tau:.10f}")
print(f"  Target (3-phi) = {TARGET_CRITICAL:.10f}")
print(f"  Error = {abs(scale_tau - TARGET_CRITICAL):.2e}")

# tau=1 gives x*tanh(x)
std_xtanh_scale = get_theoretical_critical_scale(lambda x: scaled_tanh_derivative(x, 1.0))
print(f"\n5.2 Verification: tau=1 (x*tanh(x)) gives scale = {std_xtanh_scale:.6f}")

scaled_tanh_result = {
    'tau': tau_optimal,
    'theoretical_scale': scale_tau,
    'error': abs(scale_tau - TARGET_CRITICAL)
}

# ============================================================================
# PART 6: ADDITIONAL FAMILIES
# ============================================================================

print("\n" + "=" * 70)
print("PART 6: ADDITIONAL PARAMETRIC FAMILIES")
print("=" * 70)

# 6.1 Parametric Swish: x * sigmoid(beta * x)
print("\n6.1 Parametric Swish: f(x) = x * sigmoid(beta * x)")

def parametric_swish_derivative(x, beta):
    s = sigmoid(beta * x)
    return s + beta * x * s * (1 - s)

def find_swish_beta(target_scale=TARGET_CRITICAL):
    def objective(beta):
        if beta <= 0:
            return float('inf')
        deriv = lambda x: parametric_swish_derivative(x, beta)
        scale = get_theoretical_critical_scale(deriv)
        return (scale - target_scale)**2
    result = minimize_scalar(objective, bounds=(0.1, 10.0), method='bounded')
    return result.x

swish_beta = find_swish_beta()
scale_swish = get_theoretical_critical_scale(lambda x: parametric_swish_derivative(x, swish_beta))
print(f"  beta = {swish_beta:.10f}")
print(f"  Scale = {scale_swish:.10f}, Error = {abs(scale_swish - TARGET_CRITICAL):.2e}")

parametric_swish_result = {
    'beta': swish_beta,
    'theoretical_scale': scale_swish,
    'error': abs(scale_swish - TARGET_CRITICAL)
}

# 6.2 Generalized GELU: x * Phi(x/a)^b
print("\n6.2 Generalized GELU: f(x) = x * Phi(x/a)^b")

def generalized_gelu(x, a, b):
    cdf = 0.5 * (1 + erf(x / (a * np.sqrt(2))))
    return x * np.power(np.clip(cdf, 1e-10, 1-1e-10), b)

def generalized_gelu_derivative(x, a, b):
    cdf = 0.5 * (1 + erf(x / (a * np.sqrt(2))))
    cdf_clipped = np.clip(cdf, 1e-10, 1-1e-10)
    pdf = np.exp(-x**2 / (2 * a**2)) / (np.sqrt(2 * np.pi) * a)
    return cdf_clipped**b + x * b * cdf_clipped**(b-1) * pdf

def find_generalized_gelu_params(target_scale=TARGET_CRITICAL):
    def objective(params):
        a, b = params
        if a <= 0 or b <= 0:
            return float('inf')
        deriv = lambda x: generalized_gelu_derivative(x, a, b)
        try:
            scale = get_theoretical_critical_scale(deriv)
            return (scale - target_scale)**2
        except:
            return float('inf')

    result = minimize(objective, x0=[1.0, 1.0], method='Nelder-Mead',
                     options={'xatol': 1e-8, 'fatol': 1e-10})
    return result.x

gen_gelu_a, gen_gelu_b = find_generalized_gelu_params()
scale_gen_gelu = get_theoretical_critical_scale(lambda x: generalized_gelu_derivative(x, gen_gelu_a, gen_gelu_b))
print(f"  a = {gen_gelu_a:.10f}, b = {gen_gelu_b:.10f}")
print(f"  Scale = {scale_gen_gelu:.10f}, Error = {abs(scale_gen_gelu - TARGET_CRITICAL):.2e}")

generalized_gelu_result = {
    'a': gen_gelu_a,
    'b': gen_gelu_b,
    'theoretical_scale': scale_gen_gelu,
    'error': abs(scale_gen_gelu - TARGET_CRITICAL)
}

# 6.3 Phi-Linear Activation: f(x) = x * (phi*sigmoid(x) + (1-phi)*0.5)
print("\n6.3 Phi-Weighted Gate: f(x) = x * (w * sigmoid(x) + (1-w) * 0.5)")

def phi_gate(x, w):
    return x * (w * sigmoid(x) + (1 - w) * 0.5)

def phi_gate_derivative(x, w):
    s = sigmoid(x)
    return (w * s + (1 - w) * 0.5) + x * w * s * (1 - s)

def find_phi_gate_weight(target_scale=TARGET_CRITICAL):
    def objective(w):
        if w < 0 or w > 1:
            return float('inf')
        deriv = lambda x: phi_gate_derivative(x, w)
        scale = get_theoretical_critical_scale(deriv)
        return (scale - target_scale)**2
    result = minimize_scalar(objective, bounds=(0, 1), method='bounded')
    return result.x

phi_gate_w = find_phi_gate_weight()
scale_phi_gate = get_theoretical_critical_scale(lambda x: phi_gate_derivative(x, phi_gate_w))
print(f"  w = {phi_gate_w:.10f}")
print(f"  Scale = {scale_phi_gate:.10f}, Error = {abs(scale_phi_gate - TARGET_CRITICAL):.2e}")

phi_gate_result = {
    'w': phi_gate_w,
    'theoretical_scale': scale_phi_gate,
    'error': abs(scale_phi_gate - TARGET_CRITICAL)
}

# ============================================================================
# PART 7: NEURAL NETWORK VERIFICATION
# ============================================================================

print("\n" + "=" * 70)
print("PART 7: NEURAL NETWORK VERIFICATION")
print("=" * 70)

# Define PyTorch modules for the optimal activations

class ParametricGELU(nn.Module):
    def __init__(self, alpha):
        super().__init__()
        self.alpha = alpha
    def forward(self, x):
        return x * 0.5 * (1 + torch.erf(x / (self.alpha * np.sqrt(2))))

class ParametricMish(nn.Module):
    def __init__(self, beta):
        super().__init__()
        self.beta = beta
    def forward(self, x):
        return x * torch.tanh(self.beta * torch.nn.functional.softplus(x))

class BlendActivation(nn.Module):
    def __init__(self, alpha):
        super().__init__()
        self.alpha = alpha
    def forward(self, x):
        gelu = x * 0.5 * (1 + torch.erf(x / np.sqrt(2)))
        mish = x * torch.tanh(torch.nn.functional.softplus(x))
        return self.alpha * gelu + (1 - self.alpha) * mish

class CustomGate(nn.Module):
    def __init__(self, gamma, delta):
        super().__init__()
        self.gamma = gamma
        self.delta = delta
    def forward(self, x):
        return x * torch.sigmoid(self.gamma * x + self.delta)

class ScaledTanh(nn.Module):
    def __init__(self, tau):
        super().__init__()
        self.tau = tau
    def forward(self, x):
        return x * torch.tanh(x / self.tau)

class ParametricSwish(nn.Module):
    def __init__(self, beta):
        super().__init__()
        self.beta = beta
    def forward(self, x):
        return x * torch.sigmoid(self.beta * x)

def create_network(activation_module, depth, width, init_scale):
    """Create a deep network with specified activation."""
    layers = []
    for i in range(depth):
        layer = nn.Linear(width, width, bias=False)
        nn.init.normal_(layer.weight, std=init_scale / np.sqrt(width))
        layers.append(layer)
        layers.append(activation_module)
    return nn.Sequential(*layers)

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

def find_critical_scale_nn(activation_factory, depth=30, width=256,
                           scale_range=(0.5, 2.5), n_scales=100, n_seeds=10):
    """Find critical scale through neural network experiments."""
    scales = np.linspace(scale_range[0], scale_range[1], n_scales)
    critical_points = []

    for seed in range(n_seeds):
        torch.manual_seed(seed)
        np.random.seed(seed)

        lyapunovs = []
        for scale in scales:
            torch.manual_seed(seed)
            activation = activation_factory()
            model = create_network(activation, depth, width, scale)
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

# Test each optimal activation
print("\n7.1 Testing Optimal Activations in Deep Networks:")
print("-" * 70)
print(f"{'Activation':<25} {'Theory Scale':<15} {'NN Scale':<15} {'Error from (3-phi)'}")
print("-" * 70)

nn_results = {}

# Test Parametric GELU
print(f"Testing Parametric GELU (alpha={alpha_optimal:.4f})...", end=" ", flush=True)
crit, err = find_critical_scale_nn(lambda: ParametricGELU(alpha_optimal), n_seeds=5, n_scales=50)
if crit:
    nn_results['parametric_gelu'] = {'critical': crit, 'std_err': err}
    print(f"\rParametric GELU        {scale_opt:<15.6f} {crit:<15.6f} {abs(crit - TARGET_CRITICAL):.6f}")
else:
    print(f"\rParametric GELU        {scale_opt:<15.6f} N/A")

# Test Parametric Mish
print(f"Testing Parametric Mish (beta={beta_optimal:.4f})...", end=" ", flush=True)
crit, err = find_critical_scale_nn(lambda: ParametricMish(beta_optimal), n_seeds=5, n_scales=50)
if crit:
    nn_results['parametric_mish'] = {'critical': crit, 'std_err': err}
    print(f"\rParametric Mish        {scale_opt_mish:<15.6f} {crit:<15.6f} {abs(crit - TARGET_CRITICAL):.6f}")
else:
    print(f"\rParametric Mish        {scale_opt_mish:<15.6f} N/A")

# Test Blend
print(f"Testing Blend (alpha={blend_alpha:.4f})...", end=" ", flush=True)
crit, err = find_critical_scale_nn(lambda: BlendActivation(blend_alpha), n_seeds=5, n_scales=50)
if crit:
    nn_results['blend'] = {'critical': crit, 'std_err': err}
    print(f"\rBlend (GELU+Mish)      {scale_blend:<15.6f} {crit:<15.6f} {abs(crit - TARGET_CRITICAL):.6f}")
else:
    print(f"\rBlend (GELU+Mish)      {scale_blend:<15.6f} N/A")

# Test Custom Gate
print(f"Testing Custom Gate (gamma={gamma_opt:.4f}, delta={delta_opt:.4f})...", end=" ", flush=True)
crit, err = find_critical_scale_nn(lambda: CustomGate(gamma_opt, delta_opt), n_seeds=5, n_scales=50)
if crit:
    nn_results['custom_gate'] = {'critical': crit, 'std_err': err}
    print(f"\rCustom Gate            {scale_custom:<15.6f} {crit:<15.6f} {abs(crit - TARGET_CRITICAL):.6f}")
else:
    print(f"\rCustom Gate            {scale_custom:<15.6f} N/A")

# Test Scaled Tanh
print(f"Testing Scaled Tanh (tau={tau_optimal:.4f})...", end=" ", flush=True)
crit, err = find_critical_scale_nn(lambda: ScaledTanh(tau_optimal), n_seeds=5, n_scales=50)
if crit:
    nn_results['scaled_tanh'] = {'critical': crit, 'std_err': err}
    print(f"\rScaled Tanh            {scale_tau:<15.6f} {crit:<15.6f} {abs(crit - TARGET_CRITICAL):.6f}")
else:
    print(f"\rScaled Tanh            {scale_tau:<15.6f} N/A")

# Test Parametric Swish
print(f"Testing Parametric Swish (beta={swish_beta:.4f})...", end=" ", flush=True)
crit, err = find_critical_scale_nn(lambda: ParametricSwish(swish_beta), n_seeds=5, n_scales=50)
if crit:
    nn_results['parametric_swish'] = {'critical': crit, 'std_err': err}
    print(f"\rParametric Swish       {scale_swish:<15.6f} {crit:<15.6f} {abs(crit - TARGET_CRITICAL):.6f}")
else:
    print(f"\rParametric Swish       {scale_swish:<15.6f} N/A")

# Test standard GELU and Mish for comparison
print(f"\nTesting Standard GELU...", end=" ", flush=True)
crit, err = find_critical_scale_nn(lambda: nn.GELU(), n_seeds=5, n_scales=50)
if crit:
    nn_results['std_gelu'] = {'critical': crit, 'std_err': err}
    print(f"\rStandard GELU          1.4810          {crit:<15.6f} {abs(crit - TARGET_CRITICAL):.6f}")

print(f"Testing Standard Mish...", end=" ", flush=True)
class StdMish(nn.Module):
    def forward(self, x):
        return x * torch.tanh(torch.nn.functional.softplus(x))
crit, err = find_critical_scale_nn(lambda: StdMish(), n_seeds=5, n_scales=50)
if crit:
    nn_results['std_mish'] = {'critical': crit, 'std_err': err}
    print(f"\rStandard Mish          1.4448          {crit:<15.6f} {abs(crit - TARGET_CRITICAL):.6f}")

# ============================================================================
# PART 8: SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("PART 8: SUMMARY OF RESULTS")
print("=" * 70)

print(f"\nTarget: (3-phi) = {TARGET_CRITICAL:.10f}")
print(f"\nActivations designed to hit (3-phi) theoretically:")
print("-" * 70)

all_results = {
    'Parametric GELU': {'param': f'alpha={alpha_optimal:.6f}', 'theory': scale_opt, 'error': abs(scale_opt - TARGET_CRITICAL)},
    'Parametric Mish': {'param': f'beta={beta_optimal:.6f}', 'theory': scale_opt_mish, 'error': abs(scale_opt_mish - TARGET_CRITICAL)},
    'Blend (GELU+Mish)': {'param': f'alpha={blend_alpha:.6f}', 'theory': scale_blend, 'error': abs(scale_blend - TARGET_CRITICAL)},
    'Custom Gate': {'param': f'gamma={gamma_opt:.4f}, delta={delta_opt:.4f}', 'theory': scale_custom, 'error': abs(scale_custom - TARGET_CRITICAL)},
    'Scaled Tanh': {'param': f'tau={tau_optimal:.6f}', 'theory': scale_tau, 'error': abs(scale_tau - TARGET_CRITICAL)},
    'Parametric Swish': {'param': f'beta={swish_beta:.6f}', 'theory': scale_swish, 'error': abs(scale_swish - TARGET_CRITICAL)},
    'Generalized GELU': {'param': f'a={gen_gelu_a:.4f}, b={gen_gelu_b:.4f}', 'theory': scale_gen_gelu, 'error': abs(scale_gen_gelu - TARGET_CRITICAL)},
    'Phi-Weighted Gate': {'param': f'w={phi_gate_w:.6f}', 'theory': scale_phi_gate, 'error': abs(scale_phi_gate - TARGET_CRITICAL)},
}

sorted_results = sorted(all_results.items(), key=lambda x: x[1]['error'])

print(f"{'Rank':<6} {'Activation':<20} {'Parameters':<30} {'Theory Scale':<15} {'Error'}")
print("-" * 100)
for rank, (name, res) in enumerate(sorted_results, 1):
    print(f"{rank:<6} {name:<20} {res['param']:<30} {res['theory']:<15.10f} {res['error']:.2e}")

# ============================================================================
# PART 9: THE PHI-OPTIMAL ACTIVATION
# ============================================================================

print("\n" + "=" * 70)
print("PART 9: THE PHI-OPTIMAL ACTIVATION")
print("=" * 70)

best_name, best_result = sorted_results[0]
print(f"\nBest theoretical match: {best_name}")
print(f"Parameters: {best_result['param']}")
print(f"Theoretical critical scale: {best_result['theory']:.10f}")
print(f"Error from (3-phi): {best_result['error']:.2e}")

# Save all results
output_data = {
    'target': TARGET_CRITICAL,
    'phi': PHI,
    'three_minus_phi': THREE_MINUS_PHI,
    'theoretical_results': {
        'parametric_gelu': parametric_gelu_result,
        'parametric_mish': parametric_mish_result,
        'blend': blend_result,
        'custom_gate': custom_gate_result,
        'scaled_tanh': scaled_tanh_result,
        'parametric_swish': parametric_swish_result,
        'generalized_gelu': generalized_gelu_result,
        'phi_gate': phi_gate_result,
    },
    'nn_results': nn_results,
    'all_results_ranked': [{'name': name, **res} for name, res in sorted_results],
}

# Convert numpy to native Python types
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

output_path = Path(__file__).parent / 'phi_activation_design_results.json'
with open(output_path, 'w') as f:
    json.dump(convert(output_data), f, indent=2)
print(f"\nResults saved to: {output_path}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
