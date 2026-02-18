"""
Damped meta-optimization: does partial correction fix divergence?

The idea: a self-referential system lands at w = 1/phi = 0.618 (myopic).
The "real" best answer is w = 0.525 (system-aware). A meta-optimizer tries
to correct toward 0.525 but DIVERGES when echo strength alpha >= 0.7.

What if we only correct PARTWAY? That's the damping factor beta.
Theory says beta < 2/(phi+2) = 0.553 should work. Let's test it.
"""
import numpy as np

phi = (1 + np.sqrt(5)) / 2  # golden ratio ~1.618
w_myopic = 1 / phi           # ~0.618, the "echo" answer
w_aware  = 0.525             # the "system-aware" optimum

def meta_step(w, alpha):
    """One step of the self-referential recurrence: w -> (1 - alpha^2 * w^2)^2"""
    return (1 - alpha**2 * w**2)**2

def damped_iterate(alpha, beta, steps=200):
    """Run damped meta-optimization: w_new = (1-beta)*w_old + beta*f(w_old)
    Returns final w, or None if it diverged (went outside [0, 2])."""
    w = w_myopic  # start at the myopic fixed point
    for _ in range(steps):
        w_next = meta_step(w, alpha)
        w = (1 - beta) * w + beta * w_next  # partial correction!
        if abs(w) > 10 or np.isnan(w):
            return None  # diverged
    return w

# --- Run the experiment ---
alphas = [0.3, 0.5, 0.7, 0.9, 1.0]
betas  = np.arange(0.1, 1.05, 0.05)
beta_crit = 2 / (phi + 2)  # theoretical threshold ~0.553

print(f"phi = {phi:.4f}")
print(f"1/phi = {w_myopic:.4f} (myopic)")
print(f"w_aware = {w_aware}")
print(f"beta_crit = 2/(phi+2) = {beta_crit:.4f}")
print()

# Sweep results
print(f"{'alpha':<6} {'beta':<6} {'final_w':<10} {'converged?':<12} {'near_aware?'}")
print("-" * 50)

results = {}  # (alpha, beta) -> final_w or None
for alpha in alphas:
    for beta in betas:
        w_final = damped_iterate(alpha, round(beta, 2))
        results[(alpha, round(beta, 2))] = w_final
        tag = "DIVERGED" if w_final is None else f"{w_final:.5f}"
        conv = "" if w_final is None else ("YES" if abs(w_final - w_aware) < 0.05 else "no")
        if round(beta, 2) in [0.1, 0.3, 0.5, 0.55, 0.6, 0.8, 1.0]:
            print(f"{alpha:<6.1f} {beta:<6.2f} {tag:<12} {conv}")
    print()

# --- The golden ratio beta idea ---
beta_phi = 1 / phi  # ~0.618 -- above the theoretical threshold!
print(f"\n=== BONUS: beta = 1/phi = {beta_phi:.4f} ===")
for alpha in alphas:
    w_final = damped_iterate(alpha, beta_phi)
    tag = "DIVERGED" if w_final is None else f"{w_final:.5f}"
    print(f"  alpha={alpha:.1f}  ->  {tag}")

# --- What beta actually works best at each alpha? ---
print(f"\n=== Best beta per alpha (closest to w_aware={w_aware}) ===")
for alpha in alphas:
    best_beta, best_dist = None, 999
    for beta in betas:
        w = results[(alpha, round(beta, 2))]
        if w is not None and abs(w - w_aware) < best_dist:
            best_dist = abs(w - w_aware)
            best_beta = round(beta, 2)
    if best_beta:
        print(f"  alpha={alpha:.1f}: best beta={best_beta:.2f}, "
              f"w={results[(alpha, best_beta)]:.5f}, gap={best_dist:.5f}")
    else:
        print(f"  alpha={alpha:.1f}: ALL DIVERGED")
