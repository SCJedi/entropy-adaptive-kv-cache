"""
Quick test: if we used a system-aware optimizer (one that accounts for the
steady-state dependency of Var(y) on w), would it converge to the true
MSE minimum at w=0.525 instead of 1/phi?
"""
import numpy as np

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1.0 / PHI

print("=" * 70)
print("TEST: What R^2 does the TRUE optimum achieve?")
print("=" * 70)

# True MSE(w) = w^2/(1-w^2) - 2w + 1 for the isolated self-referential agent
# True optimum at w ~= 0.5249
# MSE there ~= 0.3305, R^2 ~= 0.6695

# At w=1/phi:
# MSE = (1/phi)^2/(1-(1/phi)^2) - 2/phi + 1
#     = (1/phi^2)/(1/phi) - 2/phi + 1     [since 1-1/phi^2 = 1/phi]
#     = 1/phi - 2/phi + 1
#     = -1/phi + 1 = 1/phi^2
# R^2 = 1 - 1/phi^2 = 1/phi

w_opt = 0.524889
w_phi = INV_PHI

mse_phi = w_phi**2/(1-w_phi**2) - 2*w_phi + 1
mse_opt = w_opt**2/(1-w_opt**2) - 2*w_opt + 1

print(f"\n  At w = 1/phi = {w_phi:.6f}:")
print(f"    MSE = {mse_phi:.6f}")
print(f"    R^2 = {1-mse_phi:.6f}")
print(f"    Note: MSE = 1/phi^2 = {1/PHI**2:.6f}, R^2 = 1/phi = {INV_PHI:.6f}")
print(f"    So R^2 = w at this point (self-consistency!)")

print(f"\n  At w = {w_opt:.6f} (true optimum):")
print(f"    MSE = {mse_opt:.6f}")
print(f"    R^2 = {1-mse_opt:.6f}")
print(f"    This is {(1-mse_opt)/(1-mse_phi)*100 - 100:.1f}% better R^2 than SGD's solution")

print(f"\n  THE PUNCHLINE:")
print(f"  SGD converges to w=1/phi because it ignores that changing w changes Var(y).")
print(f"  The golden ratio is a PROPERTY OF NAIVE SGD in a self-referential loop,")
print(f"  not a property of optimal self-referential filtering.")
print(f"  A system-aware optimizer would achieve R^2 = {1-mse_opt:.4f}, not 1/phi.")
print(f"")
print(f"  The beautiful identity R^2 = w = 1/phi is real, but it's the signature")
print(f"  of SGD's myopia (treating y as exogenous), not of optimal self-reference.")
