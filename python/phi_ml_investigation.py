"""
Golden Ratio in Neural Network Criticality: Corrected Analysis
==============================================================
Tests three regimes of criticality for self-gating activations:
  A. Simplified critical scale (chi=1 at fixed q=1)
  B. Full MFT with forward self-consistency
  C. Finite-depth Lyapunov trajectory

Key hypothesis: self-gating f(x) = x*g(x) produces special structure
related to the golden ratio phi.
"""

import numpy as np
from scipy import optimize
from scipy.special import erf

# ============================================================
# Golden ratio constants
# ============================================================
PHI = (1 + np.sqrt(5)) / 2          # 1.6180339887...
PHI_SQ = PHI ** 2                    # 2.6180339887...
THREE_MINUS_PHI = 3 - PHI            # 1.3819660113...
INV_PHI_SQ = 1 / PHI_SQ             # 0.3819660113...
PHI_SQ_OVER_5 = PHI_SQ / 5          # 0.5236067977...
SQRT_2 = np.sqrt(2)                  # 1.4142135624...

print("=" * 70)
print("GOLDEN RATIO CONSTANTS")
print("=" * 70)
print(f"phi           = {PHI:.10f}")
print(f"phi^2         = {PHI_SQ:.10f}")
print(f"3 - phi       = {THREE_MINUS_PHI:.10f}")
print(f"phi^2/5       = {PHI_SQ_OVER_5:.10f}")
print(f"sqrt(2)       = {SQRT_2:.10f}")
print()

# ============================================================
# Gauss-Hermite quadrature (fast, accurate)
# ============================================================
N_QUAD = 100
xh, wh = np.polynomial.hermite.hermgauss(N_QUAD)
wh_norm = wh / np.sqrt(np.pi)

def expect_gh(func, q):
    """E[func(z)] where z ~ N(0, q), using Gauss-Hermite quadrature."""
    if q < 1e-30:
        return float(func(np.array([0.0]))[0])
    z = np.sqrt(2.0 * q) * xh
    return np.sum(wh_norm * func(z))

# ============================================================
# Gate functions (vectorized, numerically stable)
# ============================================================

def sigmoid(x):
    x = np.asarray(x, dtype=np.float64)
    pos = 1.0 / (1.0 + np.exp(-np.minimum(x, 500.0)))
    neg_exp = np.exp(np.maximum(x, -500.0))
    neg = neg_exp / (1.0 + neg_exp)
    return np.where(x >= 0, pos, neg)

def sigmoid_deriv(x):
    s = sigmoid(x)
    return s * (1 - s)

def gaussian_cdf(x):
    return 0.5 * (1 + erf(np.asarray(x, dtype=np.float64) / np.sqrt(2)))

def gaussian_pdf(x):
    x = np.asarray(x, dtype=np.float64)
    return np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)

def softplus(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(x > 20, x, np.log1p(np.exp(np.minimum(x, 20.0))))

def mish_gate(x):
    return np.tanh(softplus(x))

def mish_gate_deriv(x):
    sp = softplus(x)
    t = np.tanh(sp)
    s = sigmoid(x)
    return (1 - t**2) * s

# ============================================================
# Activation definitions
# ============================================================

def make_gelu():
    def f(x): return x * gaussian_cdf(x)
    def fp(x): return gaussian_cdf(x) + x * gaussian_pdf(x)
    def g(x): return gaussian_cdf(x)
    def gp(x): return gaussian_pdf(x)
    return f, fp, g, gp, "GELU"

def make_swish():
    def f(x): return x * sigmoid(x)
    def fp(x):
        s = sigmoid(x)
        return s + x * s * (1 - s)
    def g(x): return sigmoid(x)
    def gp(x): return sigmoid_deriv(x)
    return f, fp, g, gp, "Swish"

def make_mish():
    def f(x): return x * mish_gate(x)
    def fp(x):
        mg = mish_gate(x)
        return mg + x * mish_gate_deriv(x)
    def g(x): return mish_gate(x)
    def gp(x): return mish_gate_deriv(x)
    return f, fp, g, gp, "Mish"

def make_ouroboros(lam=0.3757):
    def f(x): return x * (lam + (1 - lam) * sigmoid(x))
    def fp(x):
        s = sigmoid(x)
        return lam + (1 - lam) * (s + x * s * (1 - s))
    def g(x): return lam + (1 - lam) * sigmoid(x)
    def gp(x): return (1 - lam) * sigmoid_deriv(x)
    return f, fp, g, gp, f"Ouroboros(lam={lam})"

# ============================================================
# REGIME A: Simplified critical scale (chi=1 at fixed q)
# ============================================================

def find_critical_simplified(f, fp, q_ref=1.0):
    """
    Simplified critical point: at fixed q, find sigma_w such that
    chi_1 = sigma_w^2 * E[f'(z)^2 | z~N(0,q)] = 1

    Returns: sigma_w_crit
    """
    Efp2 = expect_gh(lambda z: fp(z)**2, q_ref)
    if Efp2 <= 1e-30:
        return None
    sw = np.sqrt(1.0 / Efp2)
    return sw

# ============================================================
# REGIME B: Full MFT with forward self-consistency
# ============================================================

def find_forward_fixed_point(f, sigma_w, sigma_b=0.0):
    """
    Find q* such that: q = sigma_w^2 * E[f(z)^2 | z~N(0,q)] + sigma_b^2

    Uses root-finding in log-space to avoid overflow.
    Returns q* or None if not found.
    """
    sw2 = sigma_w ** 2
    sb2 = sigma_b ** 2

    def residual(log_q):
        q = np.exp(log_q)
        Ef2 = expect_gh(lambda z: f(z)**2, q)
        return q - sw2 * Ef2 - sb2

    # Search for non-trivial fixed point (avoid q=0)
    # For zero-bias self-gating, the only fixed point is q=0 (trivial)
    # For sigma_w near sqrt(2), q* can be very large

    # Try to bracket the solution
    log_q_min = -10
    log_q_max = 20

    try:
        # Check if there's a sign change
        val_min = residual(log_q_min)
        val_max = residual(log_q_max)

        if val_min * val_max > 0:
            # No sign change - might be trivial case
            return None

        log_q_sol = optimize.brentq(residual, log_q_min, log_q_max,
                                     xtol=1e-12, rtol=1e-12)
        q_star = np.exp(log_q_sol)

        # Verify it's non-trivial
        if q_star < 1e-8:
            return None

        return q_star

    except (ValueError, RuntimeError):
        return None

def find_critical_full_mft(f, fp):
    """
    Full MFT critical point: find sigma_w such that
    1. q* = sigma_w^2 * E[f(z)^2 | z~N(0,q*)]  (forward fixed point)
    2. chi_1 = sigma_w^2 * E[f'(z)^2 | z~N(0,q*)] = 1  (criticality)

    For zero-bias self-gating, this is degenerate (q*->inf, sigma_w->sqrt(2))
    """

    def objective(sigma_w):
        """Return chi_1 - 1"""
        q_star = find_forward_fixed_point(f, sigma_w, sigma_b=0.0)
        if q_star is None:
            return -1.0  # Failed to find fixed point

        Efp2 = expect_gh(lambda z: fp(z)**2, q_star)
        chi_1 = sigma_w**2 * Efp2
        return chi_1 - 1.0

    # Search for sigma_w in [1.0, sqrt(2)]
    # As sigma_w -> sqrt(2), q* -> infinity for self-gating activations
    try:
        # Try to bracket
        sw_min = 1.0
        sw_max = 1.41  # Just below sqrt(2)

        val_min = objective(sw_min)
        val_max = objective(sw_max)

        if val_min * val_max > 0:
            # No crossing - likely degenerate
            return None, None

        sw_crit = optimize.brentq(objective, sw_min, sw_max, xtol=1e-8)
        q_star = find_forward_fixed_point(f, sw_crit, sigma_b=0.0)

        return sw_crit, q_star

    except (ValueError, RuntimeError):
        return None, None

# ============================================================
# REGIME C: Finite-depth Lyapunov trajectory
# ============================================================

def iterate_variance_map(f, sigma_w, q0, num_layers):
    """
    Iterate the variance map: q_{l+1} = sigma_w^2 * E[f(z)^2 | z~N(0, q_l)]

    Returns: final q_L, list of log(chi_l) values
    """
    q = q0
    log_chis = []
    sw2 = sigma_w ** 2

    for _ in range(num_layers):
        if q > 1e20:  # Overflow protection
            return None, None

        Ef2 = expect_gh(lambda z: f(z)**2, q)
        q_next = sw2 * Ef2

        # Compute chi at this layer (local expansion factor)
        # chi_l = dq_{l+1}/dq_l ~ sigma_w^2 * d/dq E[f(z)^2]
        # Use numerical derivative
        h = max(q * 1e-6, 1e-10)
        Ef2_plus = expect_gh(lambda z: f(z)**2, q + h)
        Ef2_minus = expect_gh(lambda z: f(z)**2, max(q - h, 1e-12))
        dEf2_dq = (Ef2_plus - Ef2_minus) / (2 * h)

        chi_l = sw2 * dEf2_dq

        if chi_l > 1e-30:
            log_chis.append(np.log(chi_l))
        else:
            log_chis.append(-100.0)

        q = q_next

    return q, log_chis

def find_critical_finite_depth(f, fp, num_layers):
    """
    Find sigma_w such that average log(chi) over L layers is zero.

    Starting condition: q0 = sigma_w^2 (unit variance input through first layer)
    """

    def objective(sigma_w):
        q0 = sigma_w ** 2
        q_final, log_chis = iterate_variance_map(f, sigma_w, q0, num_layers)

        if q_final is None or log_chis is None:
            return 1.0  # Overflow

        avg_log_chi = np.mean(log_chis)
        return avg_log_chi

    try:
        # Search in reasonable range
        sw_min = 0.5
        sw_max = 1.5

        val_min = objective(sw_min)
        val_max = objective(sw_max)

        if val_min * val_max > 0:
            # Try wider range
            sw_min = 0.3
            sw_max = 1.8
            val_min = objective(sw_min)
            val_max = objective(sw_max)

            if val_min * val_max > 0:
                return None

        sw_crit = optimize.brentq(objective, sw_min, sw_max, xtol=1e-6)
        return sw_crit

    except (ValueError, RuntimeError):
        return None

# ============================================================
# Derived quantities
# ============================================================

def compute_derived_quantities(f, fp, g, gp, sigma_w, q_star):
    """
    Compute all derived quantities at a critical point.

    Returns dict with:
      - T: gated variance fraction E[u^2 g(sqrt(q)*u)^2]
      - D_eff: 1/T
      - Palindromic tests
      - Phi_prime: forward map stability
      - Distance to golden ratio values
    """
    # T = E[u^2 g(sqrt(q)*u)^2] where u ~ N(0,1)
    sq = np.sqrt(q_star)
    T = expect_gh(lambda u: u**2 * g(sq * u)**2, 1.0)

    # D_eff
    D_eff = 1.0 / T if T > 1e-15 else np.inf

    # Palindromic tests
    palin = D_eff**2 - 3*D_eff + 1
    D_plus_inv = D_eff + 1/D_eff if D_eff > 0 else np.inf

    # 5*T test
    five_T = 5 * T

    # Forward map stability: Phi'(q*) = d/dq[sigma_w^2 * E[f(z)^2]]
    sw2 = sigma_w ** 2
    h = max(q_star * 1e-6, 1e-10)
    Ef2_plus = expect_gh(lambda z: f(z)**2, q_star + h)
    Ef2_minus = expect_gh(lambda z: f(z)**2, max(q_star - h, 1e-12))
    dEf2_dq = (Ef2_plus - Ef2_minus) / (2 * h)
    Phi_prime = sw2 * dEf2_dq

    # Chi_1 check
    Efp2 = expect_gh(lambda z: fp(z)**2, q_star)
    chi_1 = sw2 * Efp2

    return {
        'sigma_w': sigma_w,
        'q_star': q_star,
        'T': T,
        'D_eff': D_eff,
        'palin': palin,
        'D_plus_inv': D_plus_inv,
        'five_T': five_T,
        'Phi_prime': Phi_prime,
        'chi_1': chi_1,
        'dist_3_phi': abs(sigma_w - THREE_MINUS_PHI),
        'dist_sqrt2': abs(sigma_w - SQRT_2),
        'dist_T_phi2_5': abs(T - PHI_SQ_OVER_5),
        'dist_5T_phi2': abs(five_T - PHI_SQ),
    }

# ============================================================
# MAIN ANALYSIS
# ============================================================

activations = [
    make_gelu(),
    make_swish(),
    make_mish(),
    make_ouroboros(lam=0.3757),
]

print("=" * 70)
print("REGIME A: SIMPLIFIED CRITICAL SCALE (chi=1 at q=1)")
print("=" * 70)
print()

results_A = []

for f, fp, g, gp, name in activations:
    print(f"--- {name} ---")

    sw_crit = find_critical_simplified(f, fp, q_ref=1.0)

    if sw_crit is None:
        print(f"  FAILED to find critical point")
        print()
        continue

    # Compute derived quantities at q=1
    derived = compute_derived_quantities(f, fp, g, gp, sw_crit, 1.0)
    results_A.append((name, derived))

    print(f"  sigma_w_crit = {sw_crit:.6f}")
    print(f"  q (fixed)    = 1.000000")
    print(f"  chi_1        = {derived['chi_1']:.6f}  (should = 1)")
    print(f"  T            = {derived['T']:.6f}")
    print(f"  D_eff        = {derived['D_eff']:.6f}")
    print(f"  D^2-3D+1     = {derived['palin']:.6f}")
    print(f"  D+1/D        = {derived['D_plus_inv']:.6f}")
    print(f"  5*T          = {derived['five_T']:.6f}")
    print(f"  Phi'(q)      = {derived['Phi_prime']:.6f}")
    print(f"  |sw - (3-phi)| = {derived['dist_3_phi']:.6f}")
    print(f"  |sw - sqrt(2)| = {derived['dist_sqrt2']:.6f}")
    print(f"  |T - phi^2/5|  = {derived['dist_T_phi2_5']:.6f}")
    print()

print("=" * 70)
print("REGIME B: FULL MFT WITH FORWARD SELF-CONSISTENCY")
print("=" * 70)
print()
print("NOTE: For zero-bias self-gating activations, this is degenerate.")
print("      As sigma_w -> sqrt(2), q* -> infinity.")
print()

results_B = []

for f, fp, g, gp, name in activations:
    print(f"--- {name} ---")

    sw_crit, q_star = find_critical_full_mft(f, fp)

    if sw_crit is None:
        print(f"  FAILED (degenerate regime)")
        print()
        continue

    derived = compute_derived_quantities(f, fp, g, gp, sw_crit, q_star)
    results_B.append((name, derived))

    print(f"  sigma_w_crit = {sw_crit:.6f}")
    print(f"  q*           = {q_star:.6f}")
    print(f"  chi_1        = {derived['chi_1']:.6f}")
    print(f"  T            = {derived['T']:.6f}")
    print(f"  D_eff        = {derived['D_eff']:.6f}")
    print(f"  Phi'(q*)     = {derived['Phi_prime']:.6f}")
    print(f"  |sw - sqrt(2)| = {derived['dist_sqrt2']:.6f}")
    print()

print("=" * 70)
print("REGIME C: FINITE-DEPTH LYAPUNOV TRAJECTORY")
print("=" * 70)
print()

depths = [5, 10, 20, 30, 50, 100, 200]
results_C = {depth: [] for depth in depths}

for depth in depths:
    print(f"--- Depth L = {depth} ---")
    print()

    for f, fp, g, gp, name in activations:
        sw_crit = find_critical_finite_depth(f, fp, depth)

        if sw_crit is None:
            print(f"  {name:20s}: FAILED")
            continue

        # Compute final q and derived quantities
        q0 = sw_crit ** 2
        q_final, log_chis = iterate_variance_map(f, sw_crit, q0, depth)

        if q_final is None:
            print(f"  {name:20s}: OVERFLOW")
            continue

        avg_log_chi = np.mean(log_chis)
        derived = compute_derived_quantities(f, fp, g, gp, sw_crit, q_final)
        results_C[depth].append((name, derived, avg_log_chi))

        print(f"  {name:20s}: sw = {sw_crit:.6f}, q_final = {q_final:.6e}, "
              f"avg_log_chi = {avg_log_chi:.6f}, |sw-(3-phi)| = {derived['dist_3_phi']:.6f}")

    print()

# ============================================================
# SUMMARY TABLE
# ============================================================

print("=" * 70)
print("SUMMARY TABLE: REGIME A (Simplified)")
print("=" * 70)
print()
print(f"{'Activation':20s} {'sigma_w':>10s} {'|d(3-phi)|':>12s} {'T':>10s} "
      f"{'|d(phi2/5)|':>12s} {'5T':>10s} {'D+1/D':>10s}")
print("-" * 86)

for name, d in results_A:
    print(f"{name:20s} {d['sigma_w']:10.6f} {d['dist_3_phi']:12.6f} {d['T']:10.6f} "
          f"{d['dist_T_phi2_5']:12.6f} {d['five_T']:10.6f} {d['D_plus_inv']:10.6f}")

print()
print(f"Reference: 3-phi = {THREE_MINUS_PHI:.6f}, phi^2/5 = {PHI_SQ_OVER_5:.6f}, "
      f"phi^2 = {PHI_SQ:.6f}")
print()

print("=" * 70)
print("SUMMARY TABLE: REGIME C (Finite Depth)")
print("=" * 70)
print()

print(f"{'Activation':20s} ", end="")
for depth in depths:
    print(f"{'L='+str(depth):>10s} ", end="")
print()
print("-" * (22 + 11 * len(depths)))

for f, fp, g, gp, name in activations:
    print(f"{name:20s} ", end="")
    for depth in depths:
        # Find result for this activation at this depth
        found = False
        for n, d, _ in results_C[depth]:
            if n == name:
                print(f"{d['sigma_w']:10.6f} ", end="")
                found = True
                break
        if not found:
            print(f"{'---':>10s} ", end="")
    print()

print()
print(f"Reference: 3-phi = {THREE_MINUS_PHI:.6f}, sqrt(2) = {SQRT_2:.6f}")
print()

print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
