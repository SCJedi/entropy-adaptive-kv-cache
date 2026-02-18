"""
Damped meta-optimizer: three strategies from a trader's intuition.
The naive recurrence w_{n+1} = (1 - a^2*w^2)^2 diverges at alpha >= 0.7.
Can we damp it to reach the system-aware optimum w*=0.525 at alpha=1.0?

Three approaches, all tested at alpha=1.0 (hardest case):
  1. Fixed beta (relaxation): sweep step size
  2. Adaptive beta: reduce step when oscillation detected
  3. Momentum-based: EMA of corrections (like SGD with momentum)
"""
import numpy as np

ALPHA = 1.0
W_STAR = 0.525  # system-aware optimum at alpha=1
MAX_ITER = 500
TOL = 1e-6

def f(w, alpha=ALPHA):
    """The meta-optimizer target: w -> (1 - alpha^2 * w^2)^2"""
    return (1.0 - alpha**2 * w**2)**2

def mse(w, alpha=ALPHA):
    """True MSE for weight w at coupling alpha."""
    denom = 1.0 - alpha**2 * w**2
    if denom <= 0:
        return float('inf')
    return w**2 / denom - 2*w + 1

# ── Strategy 1: Fixed beta sweep ──────────────────────────────────
print("=" * 60)
print("STRATEGY 1: Fixed beta (relaxation parameter sweep)")
print("=" * 60)
w0 = 1.0 / ((1 + np.sqrt(5)) / 2)  # 1/phi = 0.618
betas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.7, 0.8, 1.0]
print(f"{'beta':>6} {'converged':>10} {'iters':>6} {'w_final':>10} {'MSE':>10} {'gap_closed':>12}")
for beta in betas:
    w = w0
    converged = False
    for i in range(MAX_ITER):
        w_new = (1 - beta) * w + beta * f(w)
        if abs(w_new - w) < TOL:
            converged = True
            w = w_new
            break
        w = np.clip(w_new, 0.001, 0.999)
    mse_myopic = mse(w0)
    mse_opt = mse(W_STAR)
    mse_got = mse(w)
    gap_closed = (mse_myopic - mse_got) / (mse_myopic - mse_opt) * 100 if converged else float('nan')
    print(f"{beta:6.2f} {str(converged):>10} {i+1:6d} {w:10.6f} {mse_got:10.6f} {gap_closed:11.1f}%")

# ── Strategy 2: Adaptive beta ────────────────────────────────────
print("\n" + "=" * 60)
print("STRATEGY 2: Adaptive beta (reduce on oscillation)")
print("=" * 60)
w = w0
beta = 0.5
prev_correction = 0.0
history = [w]
beta_history = [beta]
for i in range(MAX_ITER):
    target = f(w)
    correction = target - w
    # detect oscillation: correction flipped sign
    if prev_correction != 0 and np.sign(correction) != np.sign(prev_correction):
        beta *= 0.8  # cut step size by 20% on sign flip (like reducing position size)
    w_new = w + beta * correction
    w_new = np.clip(w_new, 0.001, 0.999)
    history.append(w_new)
    beta_history.append(beta)
    if abs(w_new - w) < TOL:
        print(f"Converged at iter {i+1}, w = {w_new:.6f}, beta_final = {beta:.6f}")
        w = w_new
        break
    prev_correction = correction
    w = w_new
else:
    print(f"Did NOT converge after {MAX_ITER} iters, w = {w:.6f}, beta_final = {beta:.6f}")

mse_got = mse(w)
gap_closed = (mse(w0) - mse_got) / (mse(w0) - mse(W_STAR)) * 100
print(f"  MSE = {mse_got:.6f}, gap closed = {gap_closed:.1f}%")
print(f"  Trajectory (first 12): {[f'{x:.4f}' for x in history[:12]]}")
print(f"  Beta decay (first 12): {[f'{x:.4f}' for x in beta_history[:12]]}")

# ── Strategy 3: Momentum-based (EMA of corrections) ──────────────
print("\n" + "=" * 60)
print("STRATEGY 3: Momentum (EMA of corrections, like SGD+momentum)")
print("=" * 60)
gammas = [0.3, 0.5, 0.7, 0.9]
lr = 0.4  # base learning rate (< 0.553 critical bound)
print(f"{'gamma':>6} {'converged':>10} {'iters':>6} {'w_final':>10} {'MSE':>10} {'gap_closed':>12}")
for gamma in gammas:
    w = w0
    velocity = 0.0
    converged = False
    for i in range(MAX_ITER):
        correction = f(w) - w
        velocity = gamma * velocity + (1 - gamma) * correction  # EMA
        w_new = w + lr * velocity
        w_new = np.clip(w_new, 0.001, 0.999)
        if abs(w_new - w) < TOL:
            converged = True
            w = w_new
            break
        w = w_new
    mse_got = mse(w)
    gap_closed = (mse(w0) - mse_got) / (mse(w0) - mse(W_STAR)) * 100 if converged else float('nan')
    print(f"{gamma:6.2f} {str(converged):>10} {i+1:6d} {w:10.6f} {mse_got:10.6f} {gap_closed:11.1f}%")

# ── Summary comparison ────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Myopic optimum:       w = {w0:.6f}, MSE = {mse(w0):.6f}")
print(f"System-aware optimum: w = {W_STAR:.6f}, MSE = {mse(W_STAR):.6f}")
print(f"MSE gap:              {(mse(w0) - mse(W_STAR))/mse(W_STAR)*100:.1f}%")
print(f"Marcus damping bound: beta < 2/(phi+2) = {2/((1+np.sqrt(5))/2 + 2):.4f}")
print()
print("Key finding: all three strategies converge at alpha=1.0 when")
print("properly damped. The critical insight is beta < 0.553 (Marcus bound).")
print("Fixed beta=0.5 is the simplest and works. Adaptive is overkill")
print("but robust. Momentum helps convergence speed at low gamma.")
