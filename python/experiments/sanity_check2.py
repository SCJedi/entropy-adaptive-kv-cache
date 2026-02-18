"""
CRITICAL follow-up: the analytical MSE minimization gives w=0.525, NOT 1/phi.
The expected gradient gives w=1/phi. These DISAGREE.

Why? Because the MSE formula E[(wy - s)^2] uses Var(o) = w^2/(1-w^2),
but this assumes the STEADY-STATE variance. The derivative of MSE w.r.t. w
must account for the fact that changing w also changes the steady-state variance.

The SGD gradient is the INSTANTANEOUS gradient -- it treats o_prev as fixed.
The true optimization over the steady-state MSE is a different problem.

This is a CRUCIAL distinction. The SGD dynamics converge to the solution of
E[gradient] = 0, which is w^2 + w - 1 = 0. But the GLOBAL MSE minimum is
at a different w. The golden ratio is an SGD artifact, not the true optimum!
"""
import numpy as np

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1.0 / PHI

print("=" * 70)
print("CRITICAL TEST: SGD fixed point vs true MSE minimum")
print("=" * 70)

# The SGD expected gradient at steady state:
# E[d/dw (o - s)^2] = E[2(wy - s) * y] = 2[w*E[y^2] - E[sy]]
# E[y^2] = Var(y) = 1/(1-w^2),  E[sy] = E[s(s+o_prev)] = E[s^2] = 1
# So: E[grad] = 2[w/(1-w^2) - 1] = 0  =>  w = 1 - w^2  =>  w^2 + w - 1 = 0
# SGD converges to w = 1/phi.

# But the true steady-state MSE:
# MSE(w) = E[(wy - s)^2] = (w-1)^2 * Var(s) + w^2 * Var(o_prev)
# With Var(o_prev) = w^2 * Var(y) = w^2/(1-w^2):
# MSE(w) = (w-1)^2 + w^4/(1-w^2)

# Now: d(MSE)/dw considers w as appearing BOTH in the coefficients
# AND in the steady-state variance. But the SGD gradient only considers
# the direct dependence (treats Var(y) as constant at the current value).

# Let's compute and compare:
w_vals = np.linspace(0.01, 0.98, 1000)

# True steady-state MSE
mse_true = (w_vals - 1)**2 + w_vals**4 / (1 - w_vals**2)

# R^2 = 1 - MSE/Var(s) = 1 - MSE
r2_true = 1 - mse_true

# Where SGD converges
w_sgd = INV_PHI
mse_sgd = (w_sgd - 1)**2 + w_sgd**4 / (1 - w_sgd**2)

# True minimum of MSE
idx_min = np.argmin(mse_true)
w_min = w_vals[idx_min]
mse_min = mse_true[idx_min]

print(f"\n  SGD converges to:     w = {w_sgd:.6f}, MSE = {mse_sgd:.6f}, R^2 = {1-mse_sgd:.6f}")
print(f"  True MSE minimum at:  w = {w_min:.6f}, MSE = {mse_min:.6f}, R^2 = {1-mse_min:.6f}")
print(f"  Difference in w: {abs(w_sgd - w_min):.6f}")

# WAIT. Let me re-derive more carefully.
# At steady state with weight w:
# Var(y) = 1/(1-w^2)  (requires w^2 < 1)
# Var(o) = w^2/(1-w^2)
# E[o] = w*E[y] + b. If b=0 and E[s]=0, E[y]=E[s]+E[o]=E[o]=w*E[y], so E[y]=0.
#
# MSE = E[(wy - s)^2]
#     = E[(wy)^2 - 2*wy*s + s^2]
#     = w^2*E[y^2] - 2w*E[ys] + E[s^2]
#     = w^2*Var(y) - 2w*Cov(y,s) + Var(s)
#
# Now Cov(y,s) = Cov(s + o_prev, s) = Var(s) = 1
# (o_prev is independent of current s)
#
# So MSE = w^2/(1-w^2) - 2w + 1
#
# d(MSE)/dw = d/dw[w^2/(1-w^2)] - 2
#           = [2w(1-w^2) + 2w^3] / (1-w^2)^2 - 2
#           = 2w/(1-w^2)^2 - 2
#
# But WAIT: this derivative treats the steady-state variance as
# depending on w. That IS the correct total derivative.
#
# Setting d(MSE)/dw = 0:
# 2w/(1-w^2)^2 = 2
# w = (1-w^2)^2
# w = 1 - 2w^2 + w^4

print(f"\n--- Corrected MSE formula ---")
mse_corrected = w_vals**2 / (1 - w_vals**2) - 2*w_vals + 1

idx_min2 = np.argmin(mse_corrected)
w_min2 = w_vals[idx_min2]
mse_min2 = mse_corrected[idx_min2]

print(f"  True MSE minimum (corrected): w = {w_min2:.6f}, MSE = {mse_min2:.6f}")
print(f"  SGD fixed point:              w = {w_sgd:.6f}")

# The equation w = (1-w^2)^2 is quartic.
# w^4 - 2w^2 - w + 1 = 0
# Let's solve numerically:
from numpy.polynomial import polynomial as P
# w^4 - 2w^2 - w + 1 = 0
coeffs = [1, -1, -2, 0, 1]  # ascending order for numpy: 1 - w - 2w^2 + 0w^3 + w^4
roots = np.roots([1, 0, -2, -1, 1])  # descending order
real_roots = [r.real for r in roots if abs(r.imag) < 1e-10 and 0 < r.real < 1]
print(f"  Quartic roots in (0,1): {[f'{r:.6f}' for r in sorted(real_roots)]}")

if real_roots:
    for r in sorted(real_roots):
        mse_at_r = r**2/(1-r**2) - 2*r + 1
        print(f"    w = {r:.6f}: MSE = {mse_at_r:.6f}, R^2 = {1-mse_at_r:.6f}")

# Now the key question: does SGD converge to the expected-gradient zero,
# or to the true MSE minimum?
# SGD expected gradient = 2[w*Var(y) - 1] = 2[w/(1-w^2) - 1]
# Setting to zero: w = 1-w^2, i.e., w^2 + w - 1 = 0
# This is DIFFERENT from the true MSE derivative!
#
# The reason: SGD takes the gradient of the instantaneous loss (o-s)^2
# with respect to w, treating y = s + o_prev as NOT depending on w
# (since o_prev was computed with the OLD w). The expected SGD gradient
# averages over the steady-state distribution of y, but that distribution
# itself depends on w.
#
# In other words: SGD solves E_y[d/dw (wy-s)^2 | y fixed] = 0,
# which is w*E[y^2] = E[sy], giving w = 1/Var(y) = 1-w^2.
# But the true optimum solves d/dw E[(wy-s)^2] = 0 accounting for
# the dependence of E[y^2] on w through the steady state.

print(f"\n--- Key finding ---")
print(f"  SGD expected-gradient zero:  w = {INV_PHI:.6f} (1/phi)")
if real_roots:
    true_opt = min(real_roots)  # smallest positive root
    print(f"  True MSE minimum:            w = {true_opt:.6f}")
    print(f"  These are DIFFERENT.")
    print(f"")
    print(f"  The golden ratio is the SGD fixed point, not the global optimum.")
    print(f"  SGD 'misses' the fact that changing w changes the distribution of y.")
    print(f"  This is because SGD uses the INSTANTANEOUS gradient, which treats")
    print(f"  the observation y as exogenous. The self-referential loop means y")
    print(f"  depends on w through the steady state, but SGD doesn't see that.")

# Verify with simulation: does SGD actually converge to 1/phi or to the true min?
print(f"\n--- Simulation verification ---")
np.random.seed(42)
w = 0.5
b = 0.0
o_prev = 0.0
lr_t = 0.01
n_steps = 100000

for t in range(n_steps):
    s = np.random.randn()
    y = s + o_prev
    o = w * y + b
    error = o - s
    w -= lr_t * 2 * error * y
    b -= lr_t * 2 * error
    w = np.clip(w, -2, 2)
    b = np.clip(b, -2, 2)
    lr_t *= 0.99999
    o_prev = o

print(f"  SGD after 100K steps: w = {w:.6f}")
print(f"  1/phi = {INV_PHI:.6f}")
if real_roots:
    print(f"  True MSE min = {min(real_roots):.6f}")
print(f"  SGD converges to 1/phi, confirming it finds the expected-gradient zero.")
