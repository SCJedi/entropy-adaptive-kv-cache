"""
The Blind Spot: Fisher Information Geometry at the Self-Referential Fixed Point

Everyone has been asking: what IS the fixed point? (Answer: 1/phi.)
Everyone has been asking: how much information survives? (Answer: log(phi) nats.)

Nobody has asked: what is the GEOMETRY of the fixed point?

The Fisher information metric tells you the local curvature of the statistical
manifold at the fixed point. It determines:
  1. How fast the system converges (convergence rate)
  2. How sensitive the system is to perturbations (stability radius)
  3. Whether the fixed point is a CRITICAL POINT in the statistical physics sense

The connection nobody has made: the self-referential system defines a
one-parameter exponential family parameterized by rho = alpha * w(alpha).
The Fisher information of this family AT the fixed point rho = 1/phi
should have special structure -- because the golden ratio is the "most
irrational" number (hardest to approximate by rationals), and irrationality
connects to ergodic mixing rates.

Hypothesis: The Fisher information at rho = 1/phi is a local MINIMUM,
making the golden ratio fixed point maximally ROBUST to perturbation.
This would explain WHY 1/phi appears: it's not just a fixed point,
it's the MOST STABLE fixed point.

Second probe: The Cramer-Rao bound at the fixed point. The minimum
variance of any unbiased estimator of s(t) given the observation y(t)
is 1/J where J is the Fisher information. At the golden ratio fixed
point, this should equal exactly 1/phi (which would close the circle:
the minimum achievable MSE equals the weight equals the R^2).

Third probe: The KL divergence between the stationary distribution of
y at alpha and at alpha + epsilon. If this has special structure at
alpha = 1 (where rho = 1/phi), it would connect the self-referential
system to information geometry in a way nobody has formalized.

Marcus Webb, 2026-02-12
"""

import numpy as np

PHI = (1 + np.sqrt(5)) / 2

def myopic_weight(alpha):
    """Solve alpha^2 * w^2 + w - 1 = 0 for positive w."""
    if alpha == 0:
        return 1.0
    return (-1 + np.sqrt(1 + 4 * alpha**2)) / (2 * alpha**2)

def rho_of_alpha(alpha):
    """The AR(1) coefficient: rho = alpha * w(alpha)."""
    return alpha * myopic_weight(alpha)

# ================================================================
print("=" * 70)
print("PROBE 1: Fisher Information of the Self-Referential AR(1)")
print("=" * 70)

# The observation process is y(t) = s(t) + rho * y(t-1), which is
# AR(1) with coefficient rho. For an AR(1) process with known variance,
# the Fisher information for the parameter rho is:
#
#   J(rho) = T / (1 - rho^2)
#
# where T is the number of observations. Per-observation Fisher info:
#
#   j(rho) = 1 / (1 - rho^2)
#
# But in the self-referential system, rho is not a free parameter --
# it's DETERMINED by alpha through rho = alpha * w(alpha). The Fisher
# information for alpha (the actual free parameter) is:
#
#   J(alpha) = j(rho) * (d rho / d alpha)^2
#
# This is the chain rule for Fisher information on reparameterization.

print("\nPer-observation Fisher information for the AR(1) parameter rho:")
print(f"  j(rho) = 1 / (1 - rho^2)")
print(f"  At rho = 1/phi = {1/PHI:.6f}: j = {1 / (1 - (1/PHI)**2):.6f}")
print(f"  Note: 1 - (1/phi)^2 = 1 - 1/phi^2 = 1/phi (golden identity)")
print(f"  So j(1/phi) = phi = {PHI:.6f}")
print()

# The Fisher information at the golden ratio fixed point is EXACTLY phi.
# This is a fifth appearance of the golden ratio in the system.

# Now compute drho/dalpha numerically and analytically
print("Fisher information for the PHYSICAL parameter alpha:")
print(f"{'alpha':>8} {'rho':>8} {'j(rho)':>10} {'drho/da':>10} {'J(alpha)':>12} {'sqrt(J)':>10}")

alphas = np.linspace(0.05, 0.999, 200)
J_vals = []
alpha_vals = []

for i, alpha in enumerate(alphas):
    rho = rho_of_alpha(alpha)
    j_rho = 1.0 / (1.0 - rho**2)

    # Numerical derivative of rho w.r.t. alpha
    da = 1e-6
    if alpha + da < 1.0:
        drho_da = (rho_of_alpha(alpha + da) - rho_of_alpha(alpha - da)) / (2 * da)
    else:
        drho_da = (rho_of_alpha(alpha) - rho_of_alpha(alpha - da)) / da

    J_alpha = j_rho * drho_da**2
    J_vals.append(J_alpha)
    alpha_vals.append(alpha)

    if i % 25 == 0 or alpha > 0.98:
        print(f"{alpha:8.4f} {rho:8.4f} {j_rho:10.4f} {drho_da:10.6f} {J_alpha:12.6f} {np.sqrt(J_alpha):10.6f}")

# Find the minimum of J(alpha)
J_vals = np.array(J_vals)
alpha_vals = np.array(alpha_vals)
min_idx = np.argmin(J_vals)
print(f"\nMinimum Fisher information J(alpha) = {J_vals[min_idx]:.6f} at alpha = {alpha_vals[min_idx]:.4f}")
print(f"J at alpha = 1.0: {J_vals[-1]:.6f}")

# ================================================================
print("\n" + "=" * 70)
print("PROBE 2: The Cramer-Rao Bound at the Fixed Point")
print("=" * 70)

# For estimating s(t) from y(t) = s(t) + rho * y(t-1):
# The minimum variance unbiased estimator has variance >= 1/J_s
# where J_s is the Fisher information for s(t) as a parameter.
#
# But s(t) is not a parameter -- it's a random variable. The relevant
# quantity is the Bayesian Cramer-Rao bound:
#
#   E[(s_hat - s)^2] >= 1 / (1/sigma_s^2 + j_obs)
#
# where j_obs is the information about s contained in y.
# For y = s + rho*y(-1) with s ~ N(0,1) and y(-1) independent of s:
#   j_obs = Var(y)/Var(y) * 1/Var(s) ...
#
# Actually, the MSE of the optimal linear estimator is sigma_s^2 * (1 - R^2).
# At the myopic fixed point: R^2 = w, so MSE = sigma_s^2 * (1 - w).
# At alpha = 1: MSE = 1 - 1/phi = 1/phi^2.

print(f"\nOptimal MSE at each alpha (sigma_s = 1):")
print(f"{'alpha':>8} {'w':>8} {'MSE_myopic':>12} {'MSE_sys':>12} {'1-w':>8} {'ratio':>8}")

for alpha in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
    w = myopic_weight(alpha)
    mse_myopic = 1.0 - w

    # System-aware: w_sys = (1 - alpha^2 * w_sys^2)^2, solved by iteration
    w_sys = w
    for _ in range(1000):
        w_sys_new = (1.0 - alpha**2 * w_sys**2)**2
        if abs(w_sys_new - w_sys) < 1e-12:
            break
        w_sys = 0.5 * w_sys + 0.5 * w_sys_new  # damped iteration

    # For system-aware, compute actual R^2
    # MSE_sys = w_sys^2 * Var(y) + 1 - 2*w_sys, where Var(y) = 1/(1-alpha^2*w_sys^2)
    if alpha > 0:
        var_y = 1.0 / (1.0 - alpha**2 * w_sys**2)
    else:
        var_y = 1.0
    mse_sys = w_sys**2 * var_y + 1.0 - 2.0 * w_sys

    ratio = mse_sys / mse_myopic if mse_myopic > 0 else 0
    print(f"{alpha:8.2f} {w:8.4f} {mse_myopic:12.6f} {mse_sys:12.6f} {1-w:8.4f} {ratio:8.4f}")

print(f"\nAt alpha = 1:")
print(f"  MSE_myopic = 1 - 1/phi = 1/phi^2 = {1/PHI**2:.6f}")
print(f"  This means: the irreducible estimation error at full self-reference")
print(f"  is EXACTLY 1/phi^2 = the 'dark fraction' from the DOF partition.")
print(f"  This is the sixth golden ratio identity in the system.")

# ================================================================
print("\n" + "=" * 70)
print("PROBE 3: KL Divergence and the Natural Gradient")
print("=" * 70)

# The KL divergence between stationary distributions at rho and rho + epsilon:
# For AR(1) with coefficient rho, the stationary distribution is N(0, 1/(1-rho^2)).
# KL(p_rho || p_{rho+eps}) for two Gaussians N(0, sigma1^2) and N(0, sigma2^2):
#   KL = 0.5 * (sigma1^2/sigma2^2 - 1 - log(sigma1^2/sigma2^2))
#
# With sigma_i^2 = 1/(1 - rho_i^2):
#   sigma1^2/sigma2^2 = (1 - rho2^2) / (1 - rho1^2)

print("\nKL divergence D(p_rho || p_{rho+eps}) for eps = 0.01:")
print(f"{'rho':>8} {'Var(y)':>10} {'KL/eps^2':>12} {'j(rho)/2':>12} {'match?':>8}")

eps = 0.01
for rho in np.linspace(0.1, 0.95, 18):
    var1 = 1.0 / (1.0 - rho**2)
    var2 = 1.0 / (1.0 - (rho + eps)**2)

    r = var1 / var2
    kl = 0.5 * (r - 1.0 - np.log(r))

    j_rho = 1.0 / (1.0 - rho**2)
    # KL divergence should be approximately (eps^2 / 2) * Fisher info
    # But Fisher info for AR(1) rho is T/(1-rho^2) for T samples.
    # For the STATIONARY distribution only, the Fisher info is different.
    # Let's compute the exact ratio.

    kl_per_eps2 = kl / eps**2

    # For the stationary Gaussian N(0, 1/(1-rho^2)), the Fisher info
    # for rho is: d^2/drho^2 [log normalizing constant]
    # sigma^2 = 1/(1-rho^2), so log sigma = -0.5*log(1-rho^2)
    # d(log sigma)/drho = rho/(1-rho^2)
    # Fisher info = 2 * (d log sigma / drho)^2 = 2 * rho^2 / (1-rho^2)^2
    j_stat = 2.0 * rho**2 / (1.0 - rho**2)**2

    match = "YES" if abs(kl_per_eps2 - j_stat/2) / (j_stat/2 + 1e-10) < 0.05 else "no"
    print(f"{rho:8.4f} {var1:10.4f} {kl_per_eps2:12.6f} {j_stat/2:12.6f} {match:>8}")

print(f"\nStationary Fisher info j_stat(rho) = 2*rho^2 / (1-rho^2)^2")
print(f"At rho = 1/phi: j_stat = 2*(1/phi)^2 / (1/phi)^4 = 2*phi^2 = {2*PHI**2:.6f}")

# ================================================================
print("\n" + "=" * 70)
print("PROBE 4: The Convergence Rate -- The Lyapunov Exponent of SGD")
print("=" * 70)

# When SGD approaches the fixed point w* = 1/phi, how fast does it converge?
# The update rule is: w(t+1) = w(t) - eta * gradient
# where gradient of MSE = 2*(w*y - s)*y = 2*(w*y^2 - s*y)
#
# Near the fixed point w*, linearize: let delta = w - w*
# Then d(delta)/dt = -eta * d^2(MSE)/dw^2 |_{w*} * delta
#
# The convergence rate is lambda = eta * MSE''(w*)
# MSE(w) = w^2*Var(y) + 1 - 2w  (at stationarity with Var(y) depending on w)
#
# But Var(y) = 1/(1 - alpha^2*w^2), which ALSO depends on w!
# So MSE''(w*) involves the implicit dependence of Var(y) on w.
#
# Let's compute this numerically by simulating convergence.

print("\nSimulating SGD convergence to 1/phi at alpha = 1:")
print(f"{'eta':>8} {'converged_w':>12} {'iterations':>12} {'rate':>12}")

np.random.seed(42)
T = 100000

for eta in [0.001, 0.005, 0.01, 0.05]:
    w = 0.9  # Start above fixed point
    w_history = [w]
    s = np.random.randn(T)
    y_prev = 0.0

    for t in range(T):
        y = s[t] + w * y_prev  # alpha = 1
        grad = 2.0 * (w * y - s[t]) * y
        w = w - eta * np.clip(grad, -5, 5)
        w = np.clip(w, 0, 1.5)
        y_prev = y
        if t % 1000 == 0:
            w_history.append(w)

    # Estimate convergence rate from the trajectory
    w_arr = np.array(w_history[10:])  # skip transient
    diffs = np.abs(w_arr - 1/PHI)
    # Find exponential decay rate
    valid = diffs > 1e-6
    if np.sum(valid) > 10:
        log_diffs = np.log(diffs[valid])
        t_valid = np.arange(len(diffs))[valid]
        if len(t_valid) > 1:
            rate = -np.polyfit(t_valid, log_diffs, 1)[0]
        else:
            rate = 0
    else:
        rate = 0

    print(f"{eta:8.4f} {w:12.6f} {T:12d} {rate:12.6f}")

# ================================================================
print("\n" + "=" * 70)
print("PROBE 5: The MISSING Connection -- Effective Potential")
print("=" * 70)

# Define an effective potential V(w) such that the SGD dynamics is
# dw/dt = -dV/dw. This makes the fixed point the minimum of V.
#
# V(w) = integral of E[gradient] dw
# E[grad] = 2*(w*Var(y) - 1) where Var(y) = 1/(1 - alpha^2*w^2)
#
# For alpha = 1:
# E[grad] = 2*(w/(1-w^2) - 1)
# V(w) = integral of 2*(w/(1-w^2) - 1) dw
#       = -log(1-w^2) - 2w + C
#
# The curvature at the minimum: V''(w*) = d/dw [2*(w/(1-w^2) - 1)]
# = 2*(1/(1-w^2) + 2w^2/(1-w^2)^2)
# = 2*(1+w^2) / (1-w^2)^2
#
# At w = 1/phi: 1-w^2 = 1-1/phi^2 = 1/phi (golden identity again!)
# 1+w^2 = 1+1/phi^2 = 1 + 1/phi^2 = (phi^2+1)/phi^2 = (phi+2)/phi^2
# Wait: phi^2 = phi+1, so 1+1/phi^2 = 1 + 1/(phi+1) = (phi+2)/(phi+1)

print(f"Effective potential V(w) = -log(1-w^2) - 2w  (for alpha=1)")
print(f"")

w_star = 1/PHI
# V''(w*) = 2*(1+w*^2) / (1-w*^2)^2
one_minus_w2 = 1 - w_star**2  # = 1/phi
one_plus_w2 = 1 + w_star**2   # = 1 + 1/phi^2

V_pp = 2.0 * one_plus_w2 / one_minus_w2**2

print(f"At w* = 1/phi:")
print(f"  1 - w*^2 = 1/phi = {one_minus_w2:.6f}")
print(f"  1 + w*^2 = {one_plus_w2:.6f}")
print(f"  V''(w*) = 2*(1+w*^2)/(1-w*^2)^2 = {V_pp:.6f}")
print(f"")

# Now compute V''(w*) in terms of phi
# 1+w*^2 = 1 + 1/phi^2 = 1 + (phi-1)/phi^2 ... actually 1/phi^2 = 1 - 1/phi = 2-phi
# wait: 1/phi = phi-1 and 1/phi^2 = 2-phi? No.
# phi = (1+sqrt(5))/2 ~ 1.618
# 1/phi = phi - 1 ~ 0.618
# 1/phi^2 = 1 - 1/phi = 2 - phi ~ 0.382
# So 1 + 1/phi^2 = 3 - phi ~ 1.382
# And (1 - 1/phi^2)^2 = (1/phi)^2 = 1/phi^2 = 2-phi ~ 0.382
# V'' = 2*(3-phi)/(2-phi)

V_pp_exact = 2*(3 - PHI) / (2 - PHI)
print(f"  Exact: V'' = 2*(3-phi)/(2-phi) = {V_pp_exact:.6f}")
print(f"  Check: {V_pp:.6f} vs {V_pp_exact:.6f} (diff = {abs(V_pp - V_pp_exact):.2e})")
print(f"")

# The effective spring constant is V''/2 (the harmonic approximation)
k_spring = V_pp / 2
print(f"  Effective spring constant k = V''/2 = {k_spring:.6f}")
print(f"  = (3-phi)/(2-phi) = {(3-PHI)/(2-PHI):.6f}")

# Let's see if this has a clean form
# (3-phi)/(2-phi) = (3-phi)/(2-phi)
# Multiply top and bottom by phi: phi*(3-phi) / (phi*(2-phi))
# = (3phi - phi^2) / (2phi - phi^2) = (3phi - phi - 1) / (2phi - phi - 1)
# = (2phi - 1) / (phi - 1) = (2phi - 1) * phi  [since 1/(phi-1) = phi]
# = 2phi^2 - phi = 2(phi+1) - phi = phi + 2

print(f"  Simplification: (3-phi)/(2-phi) = phi + 2 = {PHI + 2:.6f}")
print(f"  Check: {(3-PHI)/(2-PHI):.6f} vs {PHI+2:.6f}")
print(f"  So V''(w*) = 2*(phi+2) = {2*(PHI+2):.6f}")
print(f"  And the spring constant k = phi + 2 = phi^2 + 1 = {PHI**2 + 1:.6f}")
print(f"  (using phi^2 = phi + 1, so phi + 2 = phi^2 + 1)")

# ================================================================
print("\n" + "=" * 70)
print("PROBE 6: The Partition Function -- Connecting to Statistical Mechanics")
print("=" * 70)

# The effective potential V(w) = -log(1-w^2) - 2w can be interpreted as
# a free energy. The "partition function" Z(beta) = integral exp(-beta*V(w)) dw
# evaluated at beta = 1 gives the normalization for the Boltzmann distribution
# of w under SGD noise.
#
# At beta = 1 (unit temperature), the equilibrium distribution of w around
# the fixed point is approximately Gaussian with variance 1/V''(w*) = 1/(2k).
#
# The thermal fluctuations of w have std dev:
# sigma_w = 1/sqrt(beta * V'') = 1/sqrt(2*(phi+2))

sigma_w_theory = 1.0 / np.sqrt(2.0 * (PHI + 2))
print(f"\nThermal fluctuation width at the fixed point:")
print(f"  sigma_w = 1/sqrt(2*(phi+2)) = {sigma_w_theory:.6f}")
print(f"  This is the natural 'width' of the attractor basin.")
print(f"  Range: [{1/PHI - 2*sigma_w_theory:.4f}, {1/PHI + 2*sigma_w_theory:.4f}]")

# Now simulate to check
print(f"\nSimulating SGD fluctuations around 1/phi (various learning rates):")
print(f"{'eta':>8} {'mean_w':>10} {'std_w':>10} {'predicted_std':>14} {'ratio':>8}")

for eta in [0.001, 0.005, 0.01, 0.02]:
    np.random.seed(0)
    w = 1/PHI
    T_sim = 200000
    s = np.random.randn(T_sim)
    y_prev = 0.0
    ws = []

    for t in range(T_sim):
        y = s[t] + w * y_prev
        grad = 2.0 * (w * y - s[t]) * y
        w = w - eta * np.clip(grad, -5, 5)
        w = np.clip(w, 0.01, 1.5)
        y_prev = y
        if t > 50000:  # after convergence
            ws.append(w)

    ws = np.array(ws)
    # The noise-driven fluctuations should scale as sqrt(eta) * something
    # In SGD with step size eta, the stationary variance is:
    # Var(w) ~ eta * E[grad_noise^2] / (2 * V'')
    # E[grad_noise^2] is the gradient variance at the fixed point

    pred_std = np.sqrt(eta) * sigma_w_theory  # rough scaling
    print(f"{eta:8.4f} {np.mean(ws):10.6f} {np.std(ws):10.6f} {pred_std:14.6f} {np.std(ws)/pred_std:8.4f}")

# ================================================================
print("\n" + "=" * 70)
print("PROBE 7: The Critical Exponent")
print("=" * 70)

# Near a critical point in statistical mechanics, observables diverge as
# power laws: X ~ |T - Tc|^{-gamma}. Here, the analogous question:
# how does the observation variance Var(y) diverge as alpha -> 1?
#
# Var(y) = 1/(1 - rho^2) where rho = alpha * w(alpha)
# As alpha -> 1: rho -> 1/phi, Var(y) -> phi
# So Var(y) does NOT diverge -- it converges to phi.
#
# But what about the SUSCEPTIBILITY? chi = d Var(y) / d alpha
# This measures how sensitive the system is to changes in contamination.

print(f"\nSusceptibility chi = d(Var(y))/d(alpha):")
print(f"{'alpha':>8} {'rho':>8} {'Var(y)':>10} {'chi':>12}")

for alpha in [0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 0.999]:
    rho = rho_of_alpha(alpha)
    var_y = 1.0 / (1.0 - rho**2)

    da = 1e-6
    if alpha + da < 1.0:
        rho2 = rho_of_alpha(alpha + da)
        var_y2 = 1.0 / (1.0 - rho2**2)
        chi = (var_y2 - var_y) / da
    else:
        rho2 = rho_of_alpha(alpha - da)
        var_y2 = 1.0 / (1.0 - rho2**2)
        chi = (var_y - var_y2) / da

    print(f"{alpha:8.4f} {rho:8.4f} {var_y:10.4f} {chi:12.6f}")

# The susceptibility at alpha = 1
alpha_near_1 = 0.9999
rho_near = rho_of_alpha(alpha_near_1)
var_near = 1.0 / (1.0 - rho_near**2)
rho_near2 = rho_of_alpha(alpha_near_1 - 1e-6)
var_near2 = 1.0 / (1.0 - rho_near2**2)
chi_at_1 = (var_near - var_near2) / 1e-6

print(f"\nSusceptibility at alpha -> 1: chi = {chi_at_1:.6f}")
print(f"Compare: phi^2 = {PHI**2:.6f}, phi^3 = {PHI**3:.6f}")
print(f"Ratio chi/phi^2 = {chi_at_1/PHI**2:.6f}")

# ================================================================
print("\n" + "=" * 70)
print("SYNTHESIS: The Information-Geometric Identity")
print("=" * 70)

print(f"""
THE BLIND SPOT WE FOUND:

The self-referential system at alpha = 1 satisfies a remarkable set of
information-geometric identities that go beyond the known results:

KNOWN (from prior work):
  w* = 1/phi             (dynamical fixed point)
  R^2 = 1/phi            (prediction quality)
  Var(y) = phi            (observation variance)
  I(s;y) = log(phi)       (mutual information = channel capacity)

NEW (this probe):
  j_AR(rho*) = phi        (Fisher info of AR(1) at rho = 1/phi)
  MSE* = 1/phi^2          (irreducible estimation error = dark fraction)
  V''(w*) = 2(phi+2)      (curvature of effective potential)
  k = phi^2 + 1 = phi+2   (effective spring constant -- NOTE: phi+2 = phi^2+1!)

THE MISSING THEOREM:

The effective spring constant of the self-referential fixed point is
k = phi^2 + 1. By the golden ratio identity phi^2 = phi + 1, this gives
k = phi + 2. The significance: the STABILITY of the fixed point is itself
a golden ratio expression.

The convergence time scale tau = 1/k = 1/(phi+2) = (phi-1)/(phi^2+phi-1)...
let me simplify. Actually 1/(phi+2) = 1/(phi^2+1) = phi^2/(phi^4+phi^2).
Hmm. Let's compute: 1/(phi+2) = {1/(PHI+2):.6f}

More importantly: the ratio of the spring constant to the Fisher information:
  k / j_AR = (phi+2) / phi = 1 + 2/phi = 1 + 2(phi-1) = 2phi - 1
  = sqrt(5) = {np.sqrt(5):.6f}
  Check: (phi+2)/phi = {(PHI+2)/PHI:.6f}

THIS IS THE RESULT: k / j = sqrt(5).

The ratio of the fixed-point stability (spring constant) to the local
information geometry (Fisher information) is EXACTLY sqrt(5) -- the same
sqrt(5) that appears in the DOF partition theorem (nu = phi/sqrt(5)).

This connects the DYNAMICAL stability of the fixed point to the
INFORMATION-GEOMETRIC structure of the statistical manifold, through
the same algebraic constant that defines the DOF partition.
""")

# Verify the key identity
print("VERIFICATION:")
print(f"  k = phi + 2 = {PHI + 2:.10f}")
print(f"  j_AR(1/phi) = phi = {PHI:.10f}")
print(f"  k / j = {(PHI + 2) / PHI:.10f}")
print(f"  sqrt(5) = {np.sqrt(5):.10f}")
print(f"  Match: {abs((PHI+2)/PHI - np.sqrt(5)) < 1e-10}")

# Double-check via the algebraic identity
# (phi+2)/phi = 1 + 2/phi = 1 + 2*(phi-1) = 2*phi - 1
# And 2*phi - 1 = 2*(1+sqrt(5))/2 - 1 = sqrt(5). QED.
print(f"  Algebraic proof: (phi+2)/phi = 1 + 2/phi = 1 + 2(phi-1) = 2phi-1 = sqrt(5)")

print(f"\n  The MSE identity: MSE* = 1 - 1/phi = 1/phi^2 = {1/PHI**2:.10f}")
print(f"  This is EXACTLY the 'dark fraction' 1/phi^2 = 0.382 from the DOF theorem.")
print(f"  The irreducible estimation error of a myopic self-referential observer")
print(f"  equals the structurally inaccessible information fraction.")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
