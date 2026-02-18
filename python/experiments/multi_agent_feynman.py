"""
Multi-Agent Self-Referential Probe (Feynman)
=============================================
N agents all contaminate a shared signal. Each agent i observes:
    y_i(t) = s(t) + eps_i(t) + (alpha/N) * sum_j w_j * y_j(t-1)

Each agent learns its own w_i via SGD on (w_i * y_i(t) - s(t))^2.

Questions:
1. What does w converge to as N grows?
2. Is there a phase transition?
3. Does 1/phi survive?
4. Do two MVSU-paired agents outperform inside the crowd?
5. What's the optimal diversity between two observers?

Runtime target: <30 seconds.
"""

import sys, io, time
import numpy as np

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except: pass

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1.0 / PHI  # 0.6180...

def run_multi_agent(N, alpha_total=1.0, steps=3000, lr=0.01, seed=42, sigma_eps=0.3):
    """N agents, total coupling alpha_total spread as alpha_total/N per agent."""
    rng = np.random.RandomState(seed)
    alpha_per = alpha_total / N
    w = rng.randn(N) * 0.1 + 0.5
    y_prev = np.zeros(N)
    burn = steps // 2
    mse_sum = np.zeros(N)
    var_sum = 0.0
    count = 0

    for t in range(steps):
        s_t = rng.randn()
        eps = rng.randn(N) * sigma_eps
        contam = alpha_per * np.sum(w * y_prev)
        y_all = s_t + eps + contam
        pred = w * y_all
        error = pred - s_t
        grad = 2 * error * y_all
        w -= lr * np.clip(grad, -5, 5)
        if t > burn:
            mse_sum += error**2
            var_sum += s_t**2
            count += 1
        y_prev = y_all.copy()

    mse = mse_sum / count
    r2 = 1 - mse / (var_sum / count)
    return w, np.mean(r2), np.std(r2)


def run_mvsu_pair_in_crowd(N, alpha_total=1.0, steps=3000, lr=0.01, seed=42):
    """Two special agents use MVSU (learned cross-subtraction), rest are standard."""
    rng = np.random.RandomState(seed)
    alpha_per = alpha_total / N
    w = rng.randn(N) * 0.1 + 0.5
    w_cross = rng.randn() * 0.05  # LEARNED cross-connection
    y_prev = np.zeros(N)
    burn = steps // 2
    mse_sum = np.zeros(N)
    var_sum = 0.0
    count = 0

    for t in range(steps):
        s_t = rng.randn()
        eps = rng.randn(N) * 0.3
        contam = alpha_per * np.sum(w * y_prev)
        y_all = s_t + eps + contam

        pred = w * y_all
        # MVSU agents 0,1: subtract each other's contamination
        pred[0] = w[0] * y_all[0] + w_cross * y_all[1]
        pred[1] = w[1] * y_all[1] + w_cross * y_all[0]

        error = pred - s_t

        # SGD for w
        grad_w = 2 * error * y_all
        w -= lr * np.clip(grad_w, -5, 5)

        # SGD for w_cross (gradient from agents 0,1 only)
        grad_cross = 2 * error[0] * y_all[1] + 2 * error[1] * y_all[0]
        w_cross -= lr * np.clip(grad_cross, -5, 5)

        if t > burn:
            mse_sum += error**2
            var_sum += s_t**2
            count += 1
        y_prev = y_all.copy()

    mse = mse_sum / count
    r2 = 1 - mse / (var_sum / count)
    mvsu_r2 = np.mean(r2[:2])
    crowd_r2 = np.mean(r2[2:]) if N > 2 else np.nan
    return mvsu_r2, crowd_r2, w_cross


def run_two_agent_corr(rho, alpha=1.0, steps=3000, seed=42):
    """Two agents with correlated observation noise."""
    rng = np.random.RandomState(seed)
    w = np.array([0.5, 0.5])
    y_prev = np.zeros(2)
    sigma = 0.3
    L = np.array([[1, 0], [rho, np.sqrt(max(1-rho**2, 1e-12))]]) * sigma
    burn = steps // 2
    mse_sum = np.zeros(2)
    var_sum = 0.0
    count = 0

    for t in range(steps):
        s_t = rng.randn()
        z = rng.randn(2)
        eps = L @ z
        contam = 0.5 * np.sum(w * y_prev)
        y_all = s_t + eps + contam
        pred = w * y_all
        error = pred - s_t
        grad = 2 * error * y_all
        w -= 0.01 * np.clip(grad, -5, 5)
        if t > burn:
            mse_sum += error**2
            var_sum += s_t**2
            count += 1
        y_prev = y_all.copy()

    r2 = 1 - mse_sum / var_sum
    return np.mean(w), np.mean(r2)


def solve_theory(N, sigma_eps=0.3):
    """Solve the self-consistency equation for N agents numerically."""
    sig2 = sigma_eps**2
    for w_try in np.linspace(0.01, 0.99, 100000):
        if w_try**2 >= 1: continue
        var_ybar = (1 + sig2/N) / (1 - w_try**2)
        var_yi = 1 + sig2 + w_try**2 * var_ybar
        w_opt = 1.0 / var_yi
        if abs(w_opt - w_try) < 0.0001:
            return w_try
    return float('nan')


# ============================================================
# Main experiment
# ============================================================
print("=" * 70)
print("MULTI-AGENT SELF-REFERENTIAL PROBE")
print("Feynman's napkin, checked by computer")
print("=" * 70)
print()

t0 = time.time()
Ns = [1, 2, 3, 5, 8, 13, 21, 34, 50]
seeds = [42, 137, 256, 314, 999]

# --- Experiment 1: w vs N ---
print("EXPERIMENT 1: What does w converge to as N grows?")
print(f"{'N':>4s}  {'w_obs':>8s}  {'w_std':>8s}  {'R2':>8s}  {'w_theory':>9s}  {'1/phi':>8s}")
print("-" * 60)

exp1 = {}
for N in Ns:
    ws_all, r2s_all = [], []
    for seed in seeds:
        wf, r2m, r2s = run_multi_agent(N, steps=3000, seed=seed)
        ws_all.extend(wf.tolist())
        r2s_all.append(r2m)
    wm, ws = np.mean(ws_all), np.std(ws_all)
    r2m = np.mean(r2s_all)
    wt = solve_theory(N)
    exp1[N] = (wm, ws, r2m)
    print(f"{N:>4d}  {wm:>8.4f}  {ws:>8.4f}  {r2m:>8.4f}  {wt:>9.4f}  {INV_PHI:>8.4f}")

# Also run with sigma=0 to confirm pure golden ratio
print("\n  Sanity check: sigma_eps=0 (no observation noise):")
for N in [1, 5, 50]:
    ws_all = []
    for seed in seeds:
        wf, _, _ = run_multi_agent(N, steps=3000, seed=seed, sigma_eps=0.0)
        ws_all.extend(wf.tolist())
    print(f"    N={N:>3d}: w = {np.mean(ws_all):.4f} (should be {INV_PHI:.4f})")

print()

# --- Experiment 2: Phase transition check ---
print("EXPERIMENT 2: Is there a phase transition?")
print(f"{'N':>4s}  {'R2':>8s}  {'dR2':>8s}  {'w_per_agent':>12s}")
print("-" * 40)
prev = None
for N in Ns:
    wm, ws, r2m = exp1[N]
    dr = f"{r2m-prev:+8.4f}" if prev is not None else "     ---"
    print(f"{N:>4d}  {r2m:>8.4f}  {dr}  {wm/N:>12.5f}")
    prev = r2m

print()

# --- Experiment 3: MVSU pair in crowd ---
print("EXPERIMENT 3: Two MVSU agents (learned w_cross) in crowd of N")
print(f"{'N':>4s}  {'MVSU_R2':>8s}  {'Crowd_R2':>9s}  {'Advantage':>10s}  {'w_cross':>8s}")
print("-" * 50)

for N in [5, 10, 20, 50]:
    mr2s, cr2s, wcs = [], [], []
    for seed in seeds:
        mr2, cr2, wc = run_mvsu_pair_in_crowd(N, steps=3000, seed=seed)
        mr2s.append(mr2)
        wcs.append(wc)
        if not np.isnan(cr2): cr2s.append(cr2)
    mr2m = np.mean(mr2s)
    cr2m = np.mean(cr2s) if cr2s else np.nan
    adv = (mr2m - cr2m) / abs(cr2m) * 100 if cr2s else np.nan
    print(f"{N:>4d}  {mr2m:>8.4f}  {cr2m:>9.4f}  {adv:>+9.1f}%  {np.mean(wcs):>8.4f}")

print()

# --- Experiment 4: Optimal diversity ---
print("EXPERIMENT 4: Optimal diversity between two agents")
print("  rho = correlation of observation noise (rho=1: identical, rho=-1: opposite)")
print(f"{'rho':>6s}  {'w':>8s}  {'R2':>8s}  {'R2_gain':>8s}")
print("-" * 36)

baseline_r2 = None
for rho in [1.0, 0.8, 0.5, 0.2, 0.0, -0.2, -0.5, -0.8, -1.0]:
    ws, r2s = [], []
    for seed in seeds:
        wm, r2m = run_two_agent_corr(rho, seed=seed)
        ws.append(wm)
        r2s.append(r2m)
    r2_avg = np.mean(r2s)
    if baseline_r2 is None: baseline_r2 = r2_avg
    gain = (r2_avg - baseline_r2) / abs(baseline_r2) * 100
    print(f"{rho:>6.1f}  {np.mean(ws):>8.4f}  {r2_avg:>8.4f}  {gain:>+7.2f}%")

print()

# --- Experiment 5: Theory ---
print("EXPERIMENT 5: Napkin Math")
print("=" * 60)
print()
print("THE SELF-CONSISTENCY EQUATION FOR N AGENTS")
print()
print("Setup: N agents, each observes y_i(t) = s(t) + eps_i(t) + contam(t)")
print("  where contam = (alpha/N) * sum_j w_j * y_j(t-1)")
print("  and eps_i ~ N(0, sigma^2) is agent-specific noise")
print()
print("In symmetric equilibrium (all w_i = w):")
print("  Var(y_bar) = (1 + sigma^2/N) / (1 - w^2)")
print("  Var(y_i) = 1 + sigma^2 + w^2 * Var(y_bar)")
print("  Self-consistency: w = 1 / Var(y_i)")
print()
print("Key insight: contam = alpha*w*y_bar(t-1), which is the SAME")
print("for all agents! The 1/N per-agent coupling x N agents = constant.")
print("So adding more agents does NOT increase total contamination.")
print()
print("What DOES change with N: Var(y_bar) decreases because the")
print("per-agent noise eps_i averages out. This makes the contamination")
print("term MORE predictable (lower variance), which slightly HELPS.")
print()
print("Theoretical predictions vs observations:")
print(f"{'N':>6s}  {'w_theory':>9s}  {'w_observed':>10s}  {'diff':>8s}")
print("-" * 40)
for N in Ns:
    wt = solve_theory(N)
    wm, _, _ = exp1[N]
    print(f"{N:>6d}  {wt:>9.4f}  {wm:>10.4f}  {abs(wt-wm):>8.4f}")

print()
print("Limits:")
print(f"  N=1:       w = {solve_theory(1):.4f}  (noise is part of self-feedback)")
print(f"  N->inf:    w = {solve_theory(10000):.4f}  (noise averages out of feedback)")
print(f"  sigma=0:   w = {INV_PHI:.4f}  (pure golden ratio)")
print()
print("THE GOLDEN RATIO SURVIVES.")
print("It's the sigma=0 limit. With observation noise, w shifts down")
print("slightly because the noise inflates Var(y_i), pushing the optimal")
print("filter weight lower. But the shift is bounded and small:")
sig2 = 0.3**2
print(f"  For sigma={0.3}: w shifts from {INV_PHI:.4f} to ~{solve_theory(10000):.4f}")
print(f"  That's a {abs(INV_PHI - solve_theory(10000))/INV_PHI*100:.1f}% shift.")
print()
print("THERE IS NO PHASE TRANSITION.")
print("N enters only through sigma^2/N in Var(y_bar).")
print("As N grows: sigma^2/N -> 0 smoothly.")
print("No critical N. No discontinuity. Just smooth convergence.")

elapsed = time.time() - t0
print(f"\nTotal runtime: {elapsed:.1f}s")
