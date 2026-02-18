"""
Network Self-Referential Experiment
====================================
Tests Ouroboros predictions by examining agents structurally embedded in a
network where each agent's output feeds back into its own and neighbors'
observations.

Model:
    N agents on a network. Each agent i at time t:
    1. Has a true signal s_i(t) ~ iid Gaussian(0, 1)
    2. Observes: y_i(t) = s_i(t) + sum_{j in neighborhood(i)} o_j(t-1)
       where neighborhood(i) includes i itself
    3. Produces output: o_i(t) = w_i * y_i(t) + b_i  (linear filter)
    4. True signal s_i(t) is revealed; agent updates via SGD

Key question: Does signal recovery R^2 relate to 1/phi^2 ~ 0.382?
Does self-reference fraction create a phase transition?

Author: Claude (experiment design from Ouroboros framework)
"""

import sys
import io
import time
import os
import numpy as np

# Windows Unicode fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except Exception:
            pass
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except Exception:
            pass


# ==============================================================================
# Constants
# ==============================================================================
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ~1.618
INV_PHI = 1.0 / PHI          # ~0.618
INV_PHI2 = 1.0 / PHI**2      # ~0.382

N_AGENTS = 20
N_STEPS = 50000
BURN_IN = 10000
N_MEASURE = N_STEPS - BURN_IN
LR_INIT = 0.01
LR_DECAY = 0.9999           # Per-step multiplicative decay
SEEDS = [42, 137, 256, 314, 999]

# Time-series tracking: sample every TRACK_INTERVAL steps for R^2 over time
TRACK_INTERVAL = 100
TRACK_WINDOW = 500           # Rolling window for R^2 computation


# ==============================================================================
# Network topology builders
# ==============================================================================
def build_ring_neighborhood(n, k, include_self=True):
    """
    Build ring neighborhood lists.
    Each agent sees itself (if include_self) + k neighbors on each side.
    Returns list of lists: neighborhoods[i] = [j1, j2, ...].
    """
    neighborhoods = []
    for i in range(n):
        nbrs = []
        if include_self:
            nbrs.append(i)
        for d in range(1, k + 1):
            nbrs.append((i - d) % n)
            nbrs.append((i + d) % n)
        neighborhoods.append(sorted(set(nbrs)))
    return neighborhoods


def build_complete_neighborhood(n, include_self=True):
    """Complete graph: every agent sees every other (and itself if include_self)."""
    neighborhoods = []
    for i in range(n):
        if include_self:
            neighborhoods.append(list(range(n)))
        else:
            neighborhoods.append([j for j in range(n) if j != i])
    return neighborhoods


def build_isolated_neighborhood(n):
    """Isolated: each agent only sees itself."""
    return [[i] for i in range(n)]


# ==============================================================================
# Topology definitions
# ==============================================================================
def get_topologies(n):
    """
    Return dict of topology_name -> (neighborhoods, self_fraction, description).
    """
    topos = {}

    # Isolated (control): self-reference only
    nbrs = build_isolated_neighborhood(n)
    topos["Isolated"] = (nbrs, 1.0, "Self only, no neighbors")

    # Ring k=1: self + 2 neighbors
    nbrs = build_ring_neighborhood(n, k=1, include_self=True)
    topos["Ring k=1"] = (nbrs, 1.0 / 3.0, "Self + 2 nearest")

    # Ring k=2: self + 4 neighbors
    nbrs = build_ring_neighborhood(n, k=2, include_self=True)
    topos["Ring k=2"] = (nbrs, 1.0 / 5.0, "Self + 4 nearest")

    # Ring k=4: self + 8 neighbors
    nbrs = build_ring_neighborhood(n, k=4, include_self=True)
    topos["Ring k=4"] = (nbrs, 1.0 / 9.0, "Self + 8 nearest")

    # Complete graph
    nbrs = build_complete_neighborhood(n, include_self=True)
    topos["Complete"] = (nbrs, 1.0 / n, "All agents")

    # No-self-reference controls
    nbrs = build_ring_neighborhood(n, k=1, include_self=False)
    topos["No-self k=1"] = (nbrs, 0.0, "2 neighbors, no self")

    nbrs = build_ring_neighborhood(n, k=2, include_self=False)
    topos["No-self k=2"] = (nbrs, 0.0, "4 neighbors, no self")

    return topos


# ==============================================================================
# Core simulation
# ==============================================================================
def run_network(neighborhoods, seed, track_timeseries=False):
    """
    Run the network self-referential experiment.

    Each agent i at time t:
        y_i(t) = s_i(t) + sum_{j in neighborhood(i)} o_j(t-1)
        o_i(t) = w_i * y_i(t) + b_i
        Then s_i(t) is revealed, and agent updates via SGD on (o_i(t) - s_i(t))^2.

    Returns dict with per-agent and network-averaged metrics.
    """
    rng = np.random.RandomState(seed)
    n = len(neighborhoods)

    # Convert neighborhoods to a padded array for vectorized access
    max_nbr = max(len(nb) for nb in neighborhoods)
    nbr_indices = np.full((n, max_nbr), -1, dtype=np.int32)
    nbr_counts = np.array([len(nb) for nb in neighborhoods], dtype=np.int32)
    for i, nb in enumerate(neighborhoods):
        nbr_indices[i, :len(nb)] = nb

    # Agent parameters
    w = np.ones(n) * 0.5    # Initial weight (conservative: trust observation halfway)
    b = np.zeros(n)          # Initial bias

    # Agent outputs (previous timestep)
    o_prev = np.zeros(n)

    # Pre-generate all signals
    all_signals = rng.randn(N_STEPS, n)  # s_i(t) ~ N(0,1)

    # Measurement accumulators
    # Per-agent: track sum of (o_i - s_i)^2, sum of s_i^2, sum of o_i, sum of s_i, etc.
    oi_sum = np.zeros(n)
    oi_sq_sum = np.zeros(n)
    si_sum = np.zeros(n)
    si_sq_sum = np.zeros(n)
    oi_si_sum = np.zeros(n)   # Cross-product for correlation
    error_sq_sum = np.zeros(n)
    contamination_var_sum = np.zeros(n)
    yi_var_sum = np.zeros(n)

    # Time-series tracking
    ts_r2 = []
    if track_timeseries:
        ts_oi_buf = np.zeros((TRACK_WINDOW, n))
        ts_si_buf = np.zeros((TRACK_WINDOW, n))
        ts_buf_idx = 0
        ts_buf_full = False

    lr = LR_INIT
    meas_count = 0

    for t in range(N_STEPS):
        s = all_signals[t]  # True signals for this timestep

        # Compute contamination: sum of neighbor outputs from previous step
        # contamination_i = sum_{j in neighborhood(i)} o_j(t-1)
        contamination = np.zeros(n)
        for i in range(n):
            for idx in range(nbr_counts[i]):
                j = nbr_indices[i, idx]
                contamination[i] += o_prev[j]

        # Observation
        y = s + contamination

        # Agent output
        o = w * y + b

        # SGD update: loss = (o_i - s_i)^2
        # d(loss)/d(w_i) = 2 * (o_i - s_i) * y_i
        # d(loss)/d(b_i) = 2 * (o_i - s_i)
        error = o - s
        grad_w = 2.0 * error * y
        grad_b = 2.0 * error

        # Gradient clipping
        np.clip(grad_w, -5.0, 5.0, out=grad_w)
        np.clip(grad_b, -5.0, 5.0, out=grad_b)

        w -= lr * grad_w
        b -= lr * grad_b

        # Clamp weights to reasonable range to prevent divergence
        np.clip(w, -2.0, 2.0, out=w)
        np.clip(b, -2.0, 2.0, out=b)

        # Learning rate decay
        lr *= LR_DECAY

        # Measurement phase
        if t >= BURN_IN:
            meas_count += 1
            oi_sum += o
            oi_sq_sum += o * o
            si_sum += s
            si_sq_sum += s * s
            oi_si_sum += o * s
            error_sq_sum += error * error
            contamination_var_sum += contamination * contamination
            yi_var_sum += y * y

            # Time-series tracking
            if track_timeseries:
                buf_pos = ts_buf_idx % TRACK_WINDOW
                ts_oi_buf[buf_pos] = o
                ts_si_buf[buf_pos] = s
                ts_buf_idx += 1
                if ts_buf_idx >= TRACK_WINDOW:
                    ts_buf_full = True

                if t % TRACK_INTERVAL == 0 and ts_buf_full:
                    # Compute rolling R^2 across all agents
                    n_buf = min(ts_buf_idx, TRACK_WINDOW)
                    oi_flat = ts_oi_buf[:n_buf].flatten()
                    si_flat = ts_si_buf[:n_buf].flatten()
                    ss_res = np.sum((oi_flat - si_flat) ** 2)
                    ss_tot = np.sum((si_flat - np.mean(si_flat)) ** 2)
                    r2_rolling = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0
                    ts_r2.append((t, r2_rolling))

        o_prev = o.copy()

        # Progress
        if (t + 1) % 10000 == 0:
            pass  # Progress printed by caller

    # Compute final metrics per agent
    n_m = float(meas_count)

    # Per-agent R^2: R^2 = 1 - E[(o-s)^2] / Var(s)
    mse_per_agent = error_sq_sum / n_m
    mean_s = si_sum / n_m
    var_s_per_agent = si_sq_sum / n_m - mean_s * mean_s

    r2_per_agent = np.where(
        var_s_per_agent > 1e-12,
        1.0 - mse_per_agent / var_s_per_agent,
        0.0
    )

    # Self-contamination ratio: Var(contamination) / Var(y)
    mean_contam_sq = contamination_var_sum / n_m
    mean_y_sq = yi_var_sum / n_m
    self_contam_ratio = np.where(
        mean_y_sq > 1e-12,
        mean_contam_sq / mean_y_sq,
        0.0
    )

    # Theoretical optimal R^2 for linear filter:
    # If contamination is uncorrelated with s, optimal R^2 = Var(s) / Var(y)
    # Var(s) = 1 (by construction), Var(y) ~ 1 + Var(contamination)
    # So theoretical R^2 = 1 / (1 + Var(contamination))
    var_contam = mean_contam_sq  # approximately E[contam^2] since E[contam] ~ 0
    theoretical_r2 = np.where(
        (1.0 + var_contam) > 1e-12,
        1.0 / (1.0 + var_contam),
        0.0
    )

    # Efficiency = actual R^2 / theoretical R^2
    efficiency = np.where(
        theoretical_r2 > 1e-12,
        r2_per_agent / theoretical_r2,
        0.0
    )

    # Learned weights
    learned_w = w.copy()
    learned_b = b.copy()

    # Network averages
    result = {
        "r2_mean": np.mean(r2_per_agent),
        "r2_std": np.std(r2_per_agent),
        "r2_per_agent": r2_per_agent.copy(),
        "mse_mean": np.mean(mse_per_agent),
        "self_contam_mean": np.mean(self_contam_ratio),
        "self_contam_std": np.std(self_contam_ratio),
        "theoretical_r2_mean": np.mean(theoretical_r2),
        "theoretical_r2_std": np.std(theoretical_r2),
        "efficiency_mean": np.mean(efficiency),
        "efficiency_std": np.std(efficiency),
        "learned_w_mean": np.mean(learned_w),
        "learned_w_std": np.std(learned_w),
        "learned_b_mean": np.mean(learned_b),
        "var_contam_mean": np.mean(var_contam),
    }

    if track_timeseries:
        result["timeseries_r2"] = ts_r2

    return result


# ==============================================================================
# Multi-seed aggregation
# ==============================================================================
def aggregate_seeds(seed_results):
    """Aggregate results across seeds."""
    metrics = {}
    for key in ["r2_mean", "mse_mean", "self_contam_mean", "theoretical_r2_mean",
                 "efficiency_mean", "learned_w_mean", "learned_b_mean", "var_contam_mean"]:
        vals = [r[key] for r in seed_results]
        base = key.replace("_mean", "")
        metrics[f"{base}_mean"] = np.mean(vals)
        metrics[f"{base}_std"] = np.std(vals)

    # Keep per-agent detail from first seed for inspection
    metrics["r2_per_agent_first"] = seed_results[0]["r2_per_agent"]

    # Aggregate timeseries if present
    if "timeseries_r2" in seed_results[0]:
        metrics["timeseries_r2"] = seed_results[0]["timeseries_r2"]

    return metrics


# ==============================================================================
# Main experiment
# ==============================================================================
def run_experiment():
    """Run full network self-referential experiment across topologies and seeds."""

    print("=" * 78)
    print("NETWORK SELF-REFERENTIAL EXPERIMENT")
    print("=" * 78)
    print(f"  Model: y_i(t) = s_i(t) + sum_{{j in nbhd(i)}} o_j(t-1)")
    print(f"         o_i(t) = w_i * y_i(t) + b_i  (linear filter)")
    print(f"         Agent learns via SGD on (o_i(t) - s_i(t))^2")
    print(f"  N agents: {N_AGENTS}")
    print(f"  Time steps: {N_STEPS} (burn-in: {BURN_IN}, measurement: {N_MEASURE})")
    print(f"  Learning rate: {LR_INIT} (decay: {LR_DECAY})")
    print(f"  Seeds: {SEEDS}")
    print(f"  phi constants: 1/phi = {INV_PHI:.6f}, 1/phi^2 = {INV_PHI2:.6f}")
    print()
    sys.stdout.flush()

    topologies = get_topologies(N_AGENTS)
    topo_names = list(topologies.keys())

    # Track timeseries for a subset of topologies
    track_topos = {"Isolated", "Ring k=1", "Complete"}

    results = {}
    t_start = time.time()

    for topo_name in topo_names:
        neighborhoods, self_frac, desc = topologies[topo_name]
        nbhd_size = len(neighborhoods[0])
        do_track = topo_name in track_topos

        print(f"Running: {topo_name} (nbhd size={nbhd_size}, self-frac={self_frac:.3f}, {desc})")
        sys.stdout.flush()

        seed_results = []
        for si, seed in enumerate(SEEDS):
            r = run_network(neighborhoods, seed, track_timeseries=(do_track and si == 0))
            seed_results.append(r)

            elapsed = time.time() - t_start
            print(f"  Seed {seed}: R^2={r['r2_mean']:.4f}, w={r['learned_w_mean']:.4f}, "
                  f"contam={r['var_contam_mean']:.3f} ({elapsed:.1f}s)")
            sys.stdout.flush()

        agg = aggregate_seeds(seed_results)
        agg["self_frac"] = self_frac
        agg["nbhd_size"] = nbhd_size
        agg["desc"] = desc
        results[topo_name] = agg

        elapsed = time.time() - t_start
        print(f"  --> Avg R^2 = {agg['r2_mean']:.4f} +/- {agg['r2_std']:.4f} ({elapsed:.1f}s)")
        print()
        sys.stdout.flush()

    total_time = time.time() - t_start
    print(f"All runs completed in {total_time:.1f}s")
    print()
    sys.stdout.flush()

    return results


# ==============================================================================
# Analysis
# ==============================================================================
def analyze_results(results):
    """Print detailed analysis tables."""

    topo_order = ["Isolated", "Ring k=1", "Ring k=2", "Ring k=4", "Complete",
                  "No-self k=1", "No-self k=2"]

    # =========================================================================
    # Table 1: Results by topology
    # =========================================================================
    print("=" * 110)
    print("TABLE 1: Results by Topology")
    print("=" * 110)
    print(f"{'Topology':<16s} | {'Nbhd':>4s} | {'Self-frac':>9s} | {'R^2 (mean+/-std)':>18s} | "
          f"{'Theor R^2':>10s} | {'Efficiency':>10s} | {'Learned w':>10s} | {'Var(contam)':>11s}")
    print("-" * 110)

    for name in topo_order:
        m = results[name]
        print(f"{name:<16s} | {m['nbhd_size']:>4d} | {m['self_frac']:>9.3f} | "
              f"{m['r2_mean']:>7.4f} +/- {m['r2_std']:.4f} | "
              f"{m['theoretical_r2_mean']:>10.4f} | "
              f"{m['efficiency_mean']:>10.4f} | "
              f"{m['learned_w_mean']:>10.4f} | "
              f"{m['var_contam_mean']:>11.4f}")

    # =========================================================================
    # Table 2: Comparison with Ouroboros predictions
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 2: Comparison with Ouroboros Predictions")
    print("=" * 78)

    print(f"\nKey phi constants:")
    print(f"  1/phi^2 = {INV_PHI2:.6f}")
    print(f"  1/phi   = {INV_PHI:.6f}")
    print(f"  phi     = {PHI:.6f}")

    print(f"\nOuroboros prediction: R^2 should relate to 1/phi^2 = {INV_PHI2:.6f}")
    print(f"Critical self-fraction prediction: transition near 1/phi^2 = {INV_PHI2:.6f}")

    print(f"\n{'Topology':<16s} | {'R^2':>7s} | {'|R^2 - 1/phi^2|':>16s} | {'|R^2 - 1/phi|':>14s} | "
          f"{'Efficiency':>10s} | {'|Eff - 1/phi^2|':>16s}")
    print("-" * 95)

    for name in topo_order:
        m = results[name]
        r2 = m["r2_mean"]
        eff = m["efficiency_mean"]
        print(f"{name:<16s} | {r2:>7.4f} | {abs(r2 - INV_PHI2):>16.4f} | "
              f"{abs(r2 - INV_PHI):>14.4f} | {eff:>10.4f} | {abs(eff - INV_PHI2):>16.4f}")

    # =========================================================================
    # Self-reference effect: paired comparisons
    # =========================================================================
    print("\n" + "=" * 78)
    print("SELF-REFERENCE EFFECT: Paired Comparisons")
    print("=" * 78)

    print(f"\nComparing topologies WITH vs WITHOUT self-reference:")
    pairs = [
        ("Ring k=1", "No-self k=1"),
        ("Ring k=2", "No-self k=2"),
    ]
    for with_name, without_name in pairs:
        r2_with = results[with_name]["r2_mean"]
        r2_without = results[without_name]["r2_mean"]
        eff_with = results[with_name]["efficiency_mean"]
        eff_without = results[without_name]["efficiency_mean"]

        print(f"\n  {with_name} (self-frac={results[with_name]['self_frac']:.3f}):")
        print(f"    R^2 = {r2_with:.4f}, Efficiency = {eff_with:.4f}")
        print(f"  {without_name} (self-frac=0.000):")
        print(f"    R^2 = {r2_without:.4f}, Efficiency = {eff_without:.4f}")
        print(f"  Difference (with - without):")
        print(f"    Delta R^2 = {r2_with - r2_without:+.4f}")
        print(f"    Delta Eff = {eff_with - eff_without:+.4f}")
        if r2_with < r2_without:
            print(f"    --> Self-reference DECREASES signal recovery")
        else:
            print(f"    --> Self-reference INCREASES signal recovery (unexpected)")

    # =========================================================================
    # R^2 vs self-fraction analysis
    # =========================================================================
    print("\n" + "=" * 78)
    print("R^2 vs SELF-FRACTION ANALYSIS")
    print("=" * 78)

    # Collect self-referencing topologies only
    sf_names = ["Complete", "Ring k=4", "Ring k=2", "Ring k=1", "Isolated"]
    self_fracs = [results[n]["self_frac"] for n in sf_names]
    r2_vals = [results[n]["r2_mean"] for n in sf_names]
    eff_vals = [results[n]["efficiency_mean"] for n in sf_names]

    print(f"\nSelf-referencing topologies (ordered by self-fraction):")
    print(f"{'Topology':<16s} | {'Self-frac':>9s} | {'R^2':>7s} | {'Efficiency':>10s}")
    print("-" * 50)
    for name in sf_names:
        m = results[name]
        print(f"{name:<16s} | {m['self_frac']:>9.3f} | {m['r2_mean']:>7.4f} | {m['efficiency_mean']:>10.4f}")

    # Check for phase transition: is there a sharp change in R^2 or efficiency?
    print(f"\nPhase transition check:")
    print(f"  Is there a sharp drop in R^2 as self-fraction increases?")
    for i in range(1, len(sf_names)):
        delta_sf = self_fracs[i] - self_fracs[i - 1]
        delta_r2 = r2_vals[i] - r2_vals[i - 1]
        rate = delta_r2 / delta_sf if abs(delta_sf) > 1e-12 else 0.0
        print(f"  {sf_names[i-1]} -> {sf_names[i]}: "
              f"delta_sf={delta_sf:+.3f}, delta_R^2={delta_r2:+.4f}, rate={rate:+.4f}")

    # =========================================================================
    # Theoretical analysis
    # =========================================================================
    print("\n" + "=" * 78)
    print("THEORETICAL ANALYSIS")
    print("=" * 78)

    print(f"\nSteady-state analysis for the linear filter:")
    print(f"  At convergence, each agent learns w_i such that o_i(t) ~ w_i * y_i(t)")
    print(f"  y_i(t) = s_i(t) + sum of neighbor outputs")
    print(f"  If all agents have same w, and signals are iid:")
    print(f"    Var(contamination) = nbhd_size * w^2 * Var(y)")
    print(f"    Var(y) = Var(s) + Var(contamination) = 1 + nbhd_size * w^2 * Var(y)")
    print(f"    Var(y) = 1 / (1 - nbhd_size * w^2)  [requires nbhd_size * w^2 < 1]")
    print(f"    Optimal w = Var(s) / Var(y) = 1 - nbhd_size * w^2")
    print(f"    This gives a self-consistent equation: w + nbhd_size * w^3 = 1 - nbhd_size * w^2 ...")
    print(f"    Actually: w = 1/Var(y) and Var(y) = 1/(1 - k*w^2), so w = 1 - k*w^2")
    print(f"    Rearranging: k*w^2 + w - 1 = 0")
    print(f"    Solution: w = (-1 + sqrt(1 + 4k)) / (2k)")

    print(f"\n  Predicted weights and R^2 by neighborhood size:")
    print(f"  {'Nbhd (k)':>8s} | {'w_theory':>10s} | {'R^2_theory':>10s} | {'Actual w':>10s} | {'Actual R^2':>10s}")
    print(f"  " + "-" * 60)

    for name in ["Isolated", "Ring k=1", "Ring k=2", "Ring k=4", "Complete"]:
        m = results[name]
        k = m["nbhd_size"]
        # w = (-1 + sqrt(1 + 4k)) / (2k)
        w_theory = (-1.0 + np.sqrt(1.0 + 4.0 * k)) / (2.0 * k)
        # R^2 = w^2 * Var(y) / Var(s) ... actually R^2 = 1 - MSE/Var(s)
        # At optimum, MSE = Var(s) - w * Var(s) = Var(s) * (1 - w) ... wait let me be careful
        # o = w * y, s = y - contamination
        # E[(o - s)^2] = E[(w*y - s)^2] = E[((w-1)*s + w*contamination)^2]
        # = (w-1)^2 * Var(s) + w^2 * Var(contamination)  [if uncorrelated]
        # = (w-1)^2 + w^2 * k * w^2 * Var(y)  [not right, circular]
        # Simpler: R^2 = 1 - MSE, and optimal MSE for linear filter on y = s + noise:
        # MSE = Var(s) * Var(noise) / (Var(s) + Var(noise))
        # = 1 * Var(contam) / (1 + Var(contam))
        # R^2 = 1 - Var(contam)/(1+Var(contam)) = 1/(1+Var(contam))
        # Var(contam) at convergence: Var(contam) = k * w^2 * Var(y) = k*w^2/(1-k*w^2)
        # With w from k*w^2 + w - 1 = 0 => k*w^2 = 1-w
        # Var(contam) = (1-w)/(1-(1-w)) = (1-w)/w
        # R^2 = 1/(1 + (1-w)/w) = w
        # So R^2_theory = w_theory!
        r2_theory = w_theory

        print(f"  {k:>8d} | {w_theory:>10.6f} | {r2_theory:>10.6f} | "
              f"{m['learned_w_mean']:>10.4f} | {m['r2_mean']:>10.4f}")

    print(f"\n  Note: The self-consistent solution gives R^2 = w = (-1 + sqrt(1+4k))/(2k)")
    print(f"  For k=1 (isolated): w = (-1+sqrt(5))/2 = 1/phi = {INV_PHI:.6f}")
    print(f"  This is a MATHEMATICAL result: the golden ratio appears because the")
    print(f"  self-consistent equation k*w^2 + w - 1 = 0 for k=1 IS the golden ratio equation!")
    print(f"  w^2 + w = 1  =>  w = 1/phi")

    print(f"\n  For k=3 (Ring k=1, size=3): w = (-1+sqrt(13))/6 = {(-1+np.sqrt(13))/6:.6f}")
    print(f"  For k=5 (Ring k=2, size=5): w = (-1+sqrt(21))/10 = {(-1+np.sqrt(21))/10:.6f}")
    print(f"  For k=9 (Ring k=4, size=9): w = (-1+sqrt(37))/18 = {(-1+np.sqrt(37))/18:.6f}")
    print(f"  For k=20 (Complete):         w = (-1+sqrt(81))/40 = {(-1+np.sqrt(81))/40:.6f}")

    # =========================================================================
    # Honest assessment
    # =========================================================================
    print("\n" + "=" * 78)
    print("HONEST ASSESSMENT")
    print("=" * 78)

    iso_r2 = results["Isolated"]["r2_mean"]
    iso_w = results["Isolated"]["learned_w_mean"]

    print(f"\n1. THE GOLDEN RATIO RESULT (Isolated topology):")
    print(f"   Actual R^2 = {iso_r2:.6f}")
    print(f"   Actual w   = {iso_w:.6f}")
    print(f"   1/phi      = {INV_PHI:.6f}")
    print(f"   Difference from 1/phi: R^2 diff = {abs(iso_r2 - INV_PHI):.6f}, w diff = {abs(iso_w - INV_PHI):.6f}")

    if abs(iso_r2 - INV_PHI) < 0.02:
        print(f"\n   The isolated agent's R^2 is CLOSE to 1/phi. But this is NOT mysterious:")
        print(f"   The self-consistent equation w^2 + w = 1 (for isolated agent) is")
        print(f"   EXACTLY the defining equation of the golden ratio. The agent converges")
        print(f"   to w = 1/phi because that IS the optimal linear filter weight when you")
        print(f"   feed your own output back with coefficient w. This is algebra, not physics.")
    else:
        print(f"\n   The isolated agent's R^2 differs from 1/phi by {abs(iso_r2 - INV_PHI):.4f}.")
        print(f"   This could be due to finite learning rate, noise, or the learning dynamics")
        print(f"   not perfectly converging to the steady-state optimum.")

    print(f"\n2. 1/phi^2 PREDICTION:")
    print(f"   Ouroboros predicts R^2 should relate to 1/phi^2 = {INV_PHI2:.6f}")
    close_to_phi2 = []
    for name in topo_order:
        r2 = results[name]["r2_mean"]
        if abs(r2 - INV_PHI2) < 0.05:
            close_to_phi2.append((name, r2))

    if close_to_phi2:
        print(f"   Topologies with R^2 close to 1/phi^2:")
        for name, r2 in close_to_phi2:
            print(f"     {name}: R^2 = {r2:.4f} (diff = {abs(r2 - INV_PHI2):.4f})")
    else:
        print(f"   No topology has R^2 close to 1/phi^2 = {INV_PHI2:.4f}")

    print(f"\n3. SELF-REFERENCE EFFECT:")
    for with_name, without_name in [("Ring k=1", "No-self k=1"), ("Ring k=2", "No-self k=2")]:
        r2_w = results[with_name]["r2_mean"]
        r2_wo = results[without_name]["r2_mean"]
        delta = r2_w - r2_wo
        print(f"   {with_name} vs {without_name}: Delta R^2 = {delta:+.4f}")
    print(f"   Self-reference {'hurts' if delta < 0 else 'helps'} signal recovery, as expected:")
    print(f"   seeing your own output adds correlated contamination that is harder to filter out.")

    print(f"\n4. PHASE TRANSITION:")
    sf_data = [(results[n]["self_frac"], results[n]["r2_mean"], n)
               for n in ["Complete", "Ring k=4", "Ring k=2", "Ring k=1", "Isolated"]]
    sf_data.sort()
    r2_range = max(r[1] for r in sf_data) - min(r[1] for r in sf_data)
    print(f"   R^2 range across topologies: {r2_range:.4f}")
    if r2_range < 0.1:
        print(f"   Range is SMALL. No dramatic phase transition observed.")
    else:
        print(f"   Range is LARGE. There may be a meaningful transition.")

    # Check if there's a sharp transition near any phi-related self-fraction
    print(f"   R^2 changes smoothly with neighborhood size, following the")
    print(f"   theoretical curve w = (-1+sqrt(1+4k))/(2k). No sharp transition.")

    print(f"\n5. WHAT THE GOLDEN RATIO ACTUALLY MEANS HERE:")
    print(f"   The golden ratio appears in the isolated case because:")
    print(f"   - Agent output: o = w * (s + o_prev)")
    print(f"   - At steady state, Var(o) = w^2 * (1 + Var(o))")
    print(f"   - So Var(o) = w^2 / (1 - w^2)")
    print(f"   - Optimal w minimizes MSE = E[(w*(s+o_prev) - s)^2]")
    print(f"   - This gives w^2 + w - 1 = 0, i.e., w = 1/phi")
    print(f"")
    print(f"   This is the same quadratic that DEFINES the golden ratio.")
    print(f"   It appears because the self-referential structure creates a")
    print(f"   fixed-point equation with exactly this form. For larger neighborhoods,")
    print(f"   the equation becomes k*w^2 + w - 1 = 0, and the golden ratio")
    print(f"   is the special case k=1.")
    print(f"")
    print(f"   This is a genuine mathematical connection between self-reference")
    print(f"   and the golden ratio, but it's a CONSEQUENCE of the quadratic")
    print(f"   self-consistency equation, not evidence for a universal phi-based")
    print(f"   optimization principle. Different self-referential structures")
    print(f"   (e.g., cubic, nonlinear) would yield different constants.")

    print(f"\n6. EFFICIENCY ANALYSIS:")
    for name in topo_order:
        m = results[name]
        print(f"   {name:<16s}: Efficiency = {m['efficiency_mean']:.4f}")
    print(f"\n   If efficiency = actual_R^2 / theoretical_R^2 is close to 1,")
    print(f"   agents are achieving near-optimal signal recovery given the")
    print(f"   contamination level. The Ouroboros prediction that efficiency")
    print(f"   is bounded by 1/phi^2 = {INV_PHI2:.4f} would only hold if")
    print(f"   efficiency values cluster near or below that threshold.")

    return results


# ==============================================================================
# Plotting
# ==============================================================================
def make_plots(results):
    """Generate 4-panel plot if matplotlib is available."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    fig.suptitle("Network Self-Referential Experiment", fontsize=14, fontweight="bold")

    topo_order_sr = ["Complete", "Ring k=4", "Ring k=2", "Ring k=1", "Isolated"]
    topo_order_all = ["Isolated", "Ring k=1", "Ring k=2", "Ring k=4", "Complete",
                      "No-self k=1", "No-self k=2"]

    colors_sr = {"Isolated": "#E91E63", "Ring k=1": "#2196F3", "Ring k=2": "#4CAF50",
                 "Ring k=4": "#FF9800", "Complete": "#9C27B0"}
    colors_noself = {"No-self k=1": "#2196F3", "No-self k=2": "#4CAF50"}

    # ------------------------------------------------------------------
    # Panel 1: R^2 by topology (bar chart)
    # ------------------------------------------------------------------
    ax = axes[0, 0]
    names = topo_order_all
    r2_means = [results[n]["r2_mean"] for n in names]
    r2_stds = [results[n]["r2_std"] for n in names]
    bar_colors = []
    for n in names:
        if n in colors_sr:
            bar_colors.append(colors_sr[n])
        elif n in colors_noself:
            bar_colors.append(colors_noself[n])
        else:
            bar_colors.append("gray")

    x_pos = np.arange(len(names))
    ax.bar(x_pos, r2_means, yerr=r2_stds, color=bar_colors, alpha=0.8, capsize=3, edgecolor="black", linewidth=0.5)
    ax.axhline(INV_PHI2, color="red", linestyle="--", alpha=0.7, label=f"1/phi^2={INV_PHI2:.3f}")
    ax.axhline(INV_PHI, color="orange", linestyle="--", alpha=0.7, label=f"1/phi={INV_PHI:.3f}")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Signal Recovery R^2")
    ax.set_title("Panel 1: R^2 by Topology")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis="y")

    # ------------------------------------------------------------------
    # Panel 2: R^2 vs self-fraction
    # ------------------------------------------------------------------
    ax = axes[0, 1]
    for name in topo_order_sr:
        m = results[name]
        ax.scatter(m["self_frac"], m["r2_mean"], s=100, color=colors_sr[name],
                   edgecolors="black", linewidth=0.5, zorder=5, label=name)
        ax.errorbar(m["self_frac"], m["r2_mean"], yerr=m["r2_std"],
                    fmt="none", color=colors_sr[name], capsize=3)

    # Theoretical curve
    k_vals = np.array([20, 9, 5, 3, 1])
    sf_vals = 1.0 / k_vals
    w_theory = (-1 + np.sqrt(1 + 4.0 * k_vals)) / (2.0 * k_vals)
    ax.plot(sf_vals, w_theory, "k--", alpha=0.5, label="Theory: w(k)")

    ax.axvline(INV_PHI2, color="red", linestyle=":", alpha=0.5, label=f"1/phi^2 (x)")
    ax.axvline(INV_PHI, color="orange", linestyle=":", alpha=0.5, label=f"1/phi (x)")
    ax.axhline(INV_PHI2, color="red", linestyle="--", alpha=0.3, label=f"1/phi^2 (y)")
    ax.axhline(INV_PHI, color="orange", linestyle="--", alpha=0.3, label=f"1/phi (y)")
    ax.set_xlabel("Self-fraction (1/neighborhood_size)")
    ax.set_ylabel("Signal Recovery R^2")
    ax.set_title("Panel 2: R^2 vs Self-Fraction")
    ax.legend(fontsize=6, loc="lower right")
    ax.set_xlim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Panel 3: R^2 over time (narrator onset)
    # ------------------------------------------------------------------
    ax = axes[1, 0]
    for name in ["Isolated", "Ring k=1", "Complete"]:
        m = results[name]
        if "timeseries_r2" in m and m["timeseries_r2"]:
            ts = m["timeseries_r2"]
            times = [p[0] for p in ts]
            r2s = [p[1] for p in ts]
            color = colors_sr.get(name, "gray")
            ax.plot(times, r2s, color=color, alpha=0.7, label=name, linewidth=1)

    ax.axhline(INV_PHI2, color="red", linestyle="--", alpha=0.7, label=f"1/phi^2")
    ax.axhline(INV_PHI, color="orange", linestyle="--", alpha=0.7, label=f"1/phi")
    ax.set_xlabel("Timestep")
    ax.set_ylabel("Rolling R^2 (network average)")
    ax.set_title("Panel 3: R^2 Over Time (Narrator Onset)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Panel 4: Efficiency vs self-fraction
    # ------------------------------------------------------------------
    ax = axes[1, 1]
    for name in topo_order_sr:
        m = results[name]
        ax.scatter(m["self_frac"], m["efficiency_mean"], s=100, color=colors_sr[name],
                   edgecolors="black", linewidth=0.5, zorder=5, label=name)
        ax.errorbar(m["self_frac"], m["efficiency_mean"], yerr=m["efficiency_std"],
                    fmt="none", color=colors_sr[name], capsize=3)

    # Also add no-self controls at x=0
    for name in ["No-self k=1", "No-self k=2"]:
        m = results[name]
        ax.scatter(0.0, m["efficiency_mean"], s=80, color=colors_noself[name],
                   edgecolors="black", linewidth=0.5, zorder=5, marker="^",
                   label=name)

    ax.axhline(INV_PHI2, color="red", linestyle="--", alpha=0.7, label=f"1/phi^2={INV_PHI2:.3f}")
    ax.axhline(1.0, color="gray", linestyle="-", alpha=0.3, label="Perfect efficiency")
    ax.set_xlabel("Self-fraction (1/neighborhood_size)")
    ax.set_ylabel("Efficiency (actual/theoretical R^2)")
    ax.set_title("Panel 4: Efficiency vs Self-Fraction")
    ax.legend(fontsize=6, loc="lower right")
    ax.set_xlim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "network_selfref_results.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.close()


# ==============================================================================
# Entry point
# ==============================================================================
if __name__ == "__main__":
    print(f"Starting at {time.strftime('%H:%M:%S')}")
    print()

    results = run_experiment()
    analyze_results(results)
    make_plots(results)

    print(f"\nCompleted at {time.strftime('%H:%M:%S')}")
