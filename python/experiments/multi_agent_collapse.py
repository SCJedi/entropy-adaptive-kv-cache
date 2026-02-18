"""
Multi-agent model collapse: chain of generative agents, each training on
the previous agent's synthetic data. Tests whether MVSU-style dual-channel
inhibitory intervention slows or reverses the collapse.

True signal: mixture of 3 Gaussians (structured, not noise).
Each agent: fit mean+std from data, resample (simple parametric model).
Quality metric: Wasserstein-1 distance from true CDF (fast, 1D).
MVSU intervention: two models with different inductive biases fit the same
  data; cross-inhibitory weighting produces consensus estimate that is
  closer to the true signal than either channel alone.

Runtime target: <30 seconds.  Pure numpy.
"""
import numpy as np
import time

# ── True distribution: mixture of 3 Gaussians ──────────────────────────
MU = np.array([-3.0, 0.0, 4.0])
SIG = np.array([0.5, 1.0, 0.7])
W = np.array([0.3, 0.4, 0.3])

def sample_true(n, rng):
    c = rng.choice(3, size=n, p=W)
    return MU[c] + SIG[c] * rng.randn(n)

# ── Quality metric: Wasserstein-1 (earth mover's distance in 1D) ─────
def wasserstein1(x, y):
    """W1 distance between 1D samples. Fast: just sort and compare CDFs."""
    xs, ys = np.sort(x), np.sort(y)
    # Resample to same size for comparison
    n = min(len(xs), len(ys), 500)
    xq = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(xs)), xs)
    yq = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(ys)), ys)
    return np.mean(np.abs(xq - yq))

# ── Agent: KDE-based generative model ────────────────────────────────
def kde_generate(data, n, rng, bw_factor=1.0):
    """Generate n samples from KDE fitted to data."""
    bw = bw_factor * 1.06 * np.std(data) * len(data)**(-0.2)
    idx = rng.choice(len(data), size=n)
    return data[idx] + bw * rng.randn(n)

# ── MVSU intervention ────────────────────────────────────────────────
def mvsu_generate(data, n, rng):
    """Dual-channel generation with cross-inhibitory decontamination.

    Channel A: narrow KDE (low bw) -- preserves sharp features, more noise
    Channel B: wide KDE (high bw)  -- smoother, loses detail

    Key insight from MVSU theory: the channels have DIFFERENT contamination
    patterns (different bandwidth = different inductive bias). By comparing
    their density estimates and weighting samples by agreement, we suppress
    channel-specific artifacts while preserving features both agree on.

    This is the generative analog of inhibitory cross-connections:
    subtract B's error pattern from A, and vice versa.
    """
    n_cand = n * 4  # oversample
    sA = kde_generate(data, n_cand, rng, bw_factor=0.5)   # narrow
    sB = kde_generate(data, n_cand, rng, bw_factor=2.0)   # wide

    # Estimate density under each model (KDE density at each sample point)
    bw_a = 0.5 * 1.06 * np.std(data) * len(data)**(-0.2)
    bw_b = 2.0 * 1.06 * np.std(data) * len(data)**(-0.2)

    # For speed, evaluate density of sA samples under both KDEs
    # Using a random subset of data as kernel centers
    nc = min(200, len(data))
    centers = data[rng.choice(len(data), nc, replace=False)]

    # Log-density of each candidate under narrow KDE
    diff_a = sA[:, None] - centers[None, :]
    logp_a = np.log(np.mean(np.exp(-0.5*(diff_a/bw_a)**2), axis=1) + 1e-30)
    # Log-density of each candidate under wide KDE
    logp_b = np.log(np.mean(np.exp(-0.5*(diff_a/bw_b)**2), axis=1) + 1e-30)

    # Cross-inhibitory scoring: select samples where BOTH models agree
    # Agreement = small |logp_a - logp_b| means both assign similar density
    disagreement = np.abs(logp_a - logp_b)
    # Inhibitory: weight = exp(-lambda * disagreement)
    # This suppresses samples where the two models disagree most
    lam = 2.0 / (np.std(disagreement) + 1e-8)
    weights = np.exp(-lam * disagreement)
    weights /= weights.sum()

    idx = rng.choice(n_cand, size=n, p=weights, replace=True)
    return sA[idx]

# ── Run chain ─────────────────────────────────────────────────────────
N_GEN = 20; N_SAMP = 600; N_SEEDS = 5

def run_chain(mvsu_sched, seed):
    rng = np.random.RandomState(seed)
    ref = sample_true(3000, rng)
    data = sample_true(N_SAMP, rng)
    dists = []
    for g in range(N_GEN):
        if g in mvsu_sched:
            data = mvsu_generate(data, N_SAMP, rng)
        else:
            data = kde_generate(data, N_SAMP, rng)
        dists.append(wasserstein1(data, ref))
    return np.array(dists)

# ── Conditions ────────────────────────────────────────────────────────
conds = {
    "No intervention":  set(),
    "MVSU every gen":   set(range(N_GEN)),
    "MVSU every 3rd":   set(range(0, N_GEN, 3)),
    "MVSU gen 0 only":  {0},
    "MVSU every 5th":   set(range(0, N_GEN, 5)),
}

print("=" * 72)
print("MULTI-AGENT MODEL COLLAPSE EXPERIMENT")
print("=" * 72)
print(f"Gens: {N_GEN} | Samples: {N_SAMP} | Seeds: {N_SEEDS}")
print(f"True dist: 3-Gaussian mixture, mu={list(MU)}")
print(f"Metric: Wasserstein-1 (lower = better)")
print(f"MVSU: dual-KDE (bw*0.5 + bw*2.0), cross-inhibitory sample selection")
print()

t0 = time.time()
results = {}
for name, sched in conds.items():
    runs = [run_chain(sched, 42+s) for s in range(N_SEEDS)]
    results[name] = np.mean(runs, axis=0)
elapsed = time.time() - t0
print(f"Runtime: {elapsed:.1f}s\n")

# ── Table ─────────────────────────────────────────────────────────────
base = results["No intervention"]
print("Wasserstein-1 distance vs generation:")
print("-" * 72)
h = f"{'Gen':>4}"
for nm in conds:
    h += f" | {nm[:15]:>15}"
print(h); print("-" * 72)
for g in [0, 1, 2, 4, 6, 9, 14, 19]:
    row = f"{g:>4}"
    for nm in conds:
        row += f" | {results[nm][g]:>15.4f}"
    print(row)

print()
print("FINAL (gen 19):")
print("-" * 52)
for nm in conds:
    f = results[nm][-1]
    r = f / base[-1]
    print(f"  {nm:<22}: W1={f:.4f}  ({r:.2f}x baseline)")

print()
print("COLLAPSE RATE (gen where W1 doubles):")
print("-" * 52)
for nm in conds:
    d = results[nm]
    dd = np.where(d > 2*d[0])[0]
    if len(dd): print(f"  {nm:<22}: gen {dd[0]}")
    else:       print(f"  {nm:<22}: STABLE")

print()
print("CRITICAL FRACTION (MVSU every N gens):")
print("-" * 52)
for every_n in [1, 2, 3, 5, 7, 10, 20]:
    sc = set(range(0, N_GEN, every_n))
    rs = [run_chain(sc, 42+s) for s in range(N_SEEDS)]
    f = np.mean([r[-1] for r in rs])
    frac = len(sc)/N_GEN
    imp = 1 - f/base[-1]
    print(f"  Every {every_n:>2} ({frac:>4.0%}): W1={f:.4f}  {imp:>+6.0%} vs none")

print()
print("CASCADE FIT (no-intervention):")
lr = np.log(base/base[0])
sl = np.polyfit(np.arange(N_GEN), lr, 1)[0]
print(f"  W1(g) ~ W1(0) * {np.exp(sl):.4f}^g")
e_rate = (base[4]/base[0])**(1/4)
l_rate = (base[19]/base[9])**(1/10)
print(f"  Early rate (0-4): {e_rate:.4f}")
print(f"  Late rate (9-19): {l_rate:.4f}")
if l_rate < e_rate:
    print("  Sub-multiplicative: YES (collapse decelerates)")
else:
    print("  Sub-multiplicative: NO (collapse steady or accelerating)")

print()
print("=" * 72)
print("COMPLETE")
print("=" * 72)
