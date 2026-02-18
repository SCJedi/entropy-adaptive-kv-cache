"""
Multi-Dimensional Self-Referential Consistency Check
=====================================================
Tests whether the scalar self-consistency equation k*w^2 + w - 1 = 0
extends to the matrix case when w is a d x d weight matrix W.

For a d-dimensional agent:
    Signal s(t) in R^d, iid standard normal per component
    Weight W is a d x d matrix (learnable)
    Observation: y(t) = s(t) + alpha * W @ y(t-1)
    Prediction: pred(t) = W @ y(t)
    Loss: ||pred(t) - s(t)||^2
    SGD update on W

Key question: Do the eigenvalues of converged W satisfy lambda^2 + lambda - 1 = 0?
Is the spectral radius 1/phi? Is Tr(W) = d/phi?

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
PHI = (1 + np.sqrt(5)) / 2   # Golden ratio ~1.618
INV_PHI = 1.0 / PHI           # ~0.618
INV_PHI2 = 1.0 / PHI**2       # ~0.382

N_STEPS = 50000
BURN_IN = 10000
LR = 0.001                    # Smaller than scalar due to matrix
GRAD_CLIP = 1.0               # Gradient clipping threshold
SEEDS = [42, 137, 256]
DIMS = [1, 2, 4, 8, 16]
ALPHAS = [0.0, 0.3, 0.6, 1.0]


# ==============================================================================
# Covariance matrix builders for structured signals
# ==============================================================================
def exponential_cov(d, rho=0.7):
    """
    Build an exponentially decaying covariance matrix.
    Sigma[i,j] = rho^|i-j|
    """
    idx = np.arange(d)
    return rho ** np.abs(idx[:, None] - idx[None, :])


def cholesky_factor(cov):
    """Return the Cholesky factor L such that L @ L^T = cov."""
    return np.linalg.cholesky(cov)


# ==============================================================================
# Core simulation: single run
# ==============================================================================
def run_single(d, alpha, seed, cov_chol=None):
    """
    Run d-dimensional self-referential agent.

    Args:
        d: signal dimension
        alpha: self-reference strength (y(t) = s(t) + alpha * W @ y(t-1))
        seed: random seed
        cov_chol: Cholesky factor for correlated signals (None = identity)

    Returns:
        dict with converged W, eigenvalues, spectral radius, trace, etc.
    """
    rng = np.random.RandomState(seed)

    # Initialize W as small random matrix
    W = rng.randn(d, d) * 0.1

    # Previous observation
    y_prev = np.zeros(d)

    # Measurement accumulators
    mse_sum = 0.0
    signal_var_sum = 0.0
    meas_count = 0

    # Track W evolution at checkpoints
    W_history = []
    checkpoints = [1000, 5000, 10000, 25000, 50000]

    for t in range(1, N_STEPS + 1):
        # Generate signal
        z = rng.randn(d)
        if cov_chol is not None:
            s = cov_chol @ z
        else:
            s = z

        # Observation: y(t) = s(t) + alpha * W @ y(t-1)
        y = s + alpha * (W @ y_prev)

        # Prediction: pred(t) = W @ y(t)
        pred = W @ y

        # Loss: ||pred - s||^2
        error = pred - s  # d-vector
        loss = np.dot(error, error)

        # Gradient: d(loss)/dW = 2 * (pred - s) @ y^T  (outer product)
        # dloss/dW_ij = 2 * error_i * y_j
        grad = 2.0 * np.outer(error, y)

        # Gradient clipping (element-wise)
        np.clip(grad, -GRAD_CLIP, GRAD_CLIP, out=grad)

        # SGD update
        W -= LR * grad

        # Measurement phase
        if t > BURN_IN:
            mse_sum += loss
            signal_var_sum += np.dot(s, s)
            meas_count += 1

        # Record W at checkpoints
        if t in checkpoints:
            W_history.append((t, W.copy()))

        y_prev = y.copy()

    # Final metrics
    mse = mse_sum / meas_count
    signal_var = signal_var_sum / meas_count
    r2 = 1.0 - mse / signal_var if signal_var > 1e-12 else 0.0

    # Eigenvalue analysis of converged W
    eigenvalues = np.linalg.eigvals(W)
    spectral_radius = np.max(np.abs(eigenvalues))
    trace_W = np.trace(W)
    frob_norm = np.linalg.norm(W, 'fro')

    # Check self-consistency: do eigenvalues satisfy lambda^2 + lambda - 1 = 0?
    # For each eigenvalue, compute |lambda^2 + lambda - 1|
    sc_residuals = np.abs(eigenvalues**2 + eigenvalues - 1.0)

    # Check if W is approximately diagonal
    diag_part = np.diag(np.diag(W))
    off_diag_norm = np.linalg.norm(W - diag_part, 'fro')
    diag_norm = np.linalg.norm(diag_part, 'fro')
    off_diag_ratio = off_diag_norm / (diag_norm + 1e-12)

    # Check k*W^2 + W - I = 0 (matrix version with k=1)
    # For k neighbors, k*W^2 + W - I should be zero matrix
    # With alpha controlling feedback, for the single-agent case k=1
    matrix_residual = W @ W + W - np.eye(d)
    matrix_residual_norm = np.linalg.norm(matrix_residual, 'fro')

    return {
        "W": W.copy(),
        "eigenvalues": eigenvalues,
        "spectral_radius": spectral_radius,
        "trace": trace_W,
        "frob_norm": frob_norm,
        "sc_residuals": sc_residuals,  # |lambda^2 + lambda - 1| for each eigenvalue
        "off_diag_ratio": off_diag_ratio,
        "matrix_residual_norm": matrix_residual_norm,
        "mse": mse,
        "r2": r2,
        "W_history": W_history,
        "d": d,
        "alpha": alpha,
    }


# ==============================================================================
# Aggregate results across seeds
# ==============================================================================
def aggregate_seeds(seed_results):
    """Aggregate results across seeds for same (d, alpha) configuration."""
    agg = {}

    # Scalar metrics: mean and std
    for key in ["spectral_radius", "trace", "frob_norm", "off_diag_ratio",
                "matrix_residual_norm", "mse", "r2"]:
        vals = [r[key] for r in seed_results]
        agg[f"{key}_mean"] = np.mean(vals)
        agg[f"{key}_std"] = np.std(vals)

    # Self-consistency residuals: mean of mean residual per seed
    mean_sc = [np.mean(np.abs(r["sc_residuals"])) for r in seed_results]
    max_sc = [np.max(np.abs(r["sc_residuals"])) for r in seed_results]
    agg["sc_residual_mean"] = np.mean(mean_sc)
    agg["sc_residual_max"] = np.mean(max_sc)

    # Eigenvalue details from first seed
    agg["eigenvalues_first"] = seed_results[0]["eigenvalues"]
    agg["W_first"] = seed_results[0]["W"]
    agg["W_history_first"] = seed_results[0]["W_history"]

    agg["d"] = seed_results[0]["d"]
    agg["alpha"] = seed_results[0]["alpha"]

    return agg


# ==============================================================================
# Main experiment
# ==============================================================================
def run_experiment():
    """Run the full multi-dimensional self-referential experiment."""

    print("=" * 78)
    print("MULTI-DIMENSIONAL SELF-REFERENTIAL CONSISTENCY CHECK")
    print("=" * 78)
    print(f"  Model: y(t) = s(t) + alpha * W @ y(t-1)")
    print(f"         pred(t) = W @ y(t)")
    print(f"         Loss: ||pred(t) - s(t)||^2, updated by SGD")
    print(f"  Dimensions: {DIMS}")
    print(f"  Alpha values: {ALPHAS}")
    print(f"  Seeds: {SEEDS}")
    print(f"  Time steps: {N_STEPS} (burn-in: {BURN_IN})")
    print(f"  Learning rate: {LR}, grad clip: {GRAD_CLIP}")
    print(f"  phi constants: 1/phi = {INV_PHI:.6f}, 1/phi^2 = {INV_PHI2:.6f}")
    n_runs = len(DIMS) * len(ALPHAS) * len(SEEDS)
    print(f"  Total runs (identity cov): {n_runs}")
    print(f"  Total runs (correlated): {len(DIMS) * len(SEEDS)} (alpha=1.0 only)")
    print()
    sys.stdout.flush()

    t_start = time.time()
    results = {}

    # === Part 1: Identity covariance sweep ===
    print("--- Part 1: Identity covariance (iid signals) ---")
    sys.stdout.flush()

    for d in DIMS:
        for alpha in ALPHAS:
            seed_results = []
            for seed in SEEDS:
                r = run_single(d, alpha, seed, cov_chol=None)
                seed_results.append(r)

            agg = aggregate_seeds(seed_results)
            results[("iid", d, alpha)] = agg

            elapsed = time.time() - t_start
            print(f"  d={d:2d}, alpha={alpha:.1f}: "
                  f"spec_rad={agg['spectral_radius_mean']:.4f}, "
                  f"trace={agg['trace_mean']:.4f}, "
                  f"SC_resid={agg['sc_residual_mean']:.4f}, "
                  f"R^2={agg['r2_mean']:.4f} "
                  f"({elapsed:.1f}s)")
            sys.stdout.flush()

    # === Part 2: Correlated signals (alpha=1.0 only) ===
    print("\n--- Part 2: Correlated signals (exponential cov, rho=0.7, alpha=1.0) ---")
    sys.stdout.flush()

    for d in DIMS:
        if d == 1:
            # For d=1, correlation is trivial
            cov = np.array([[1.0]])
        else:
            cov = exponential_cov(d, rho=0.7)
        chol = cholesky_factor(cov)

        seed_results = []
        for seed in SEEDS:
            r = run_single(d, 1.0, seed, cov_chol=chol)
            seed_results.append(r)

        agg = aggregate_seeds(seed_results)
        results[("correlated", d, 1.0)] = agg

        elapsed = time.time() - t_start
        print(f"  d={d:2d}: "
              f"spec_rad={agg['spectral_radius_mean']:.4f}, "
              f"trace={agg['trace_mean']:.4f}, "
              f"SC_resid={agg['sc_residual_mean']:.4f}, "
              f"R^2={agg['r2_mean']:.4f} "
              f"({elapsed:.1f}s)")
        sys.stdout.flush()

    total_time = time.time() - t_start
    print(f"\nAll runs completed in {total_time:.1f}s")
    print()
    sys.stdout.flush()

    return results


# ==============================================================================
# Analysis
# ==============================================================================
def analyze_results(results):
    """Print detailed analysis tables."""

    # =========================================================================
    # Table 1: Spectral radius vs dimension and alpha
    # =========================================================================
    print("=" * 78)
    print("TABLE 1: Spectral Radius of Converged W")
    print("=" * 78)
    print(f"  Prediction: spectral radius should approach 1/phi = {INV_PHI:.6f}")
    print()
    header = f"{'d':>4s}"
    for alpha in ALPHAS:
        header += f" | {'alpha=' + str(alpha):>16s}"
    header += f" | {'1/phi':>8s}"
    print(header)
    print("-" * len(header))

    for d in DIMS:
        row = f"{d:>4d}"
        for alpha in ALPHAS:
            m = results[("iid", d, alpha)]
            row += f" | {m['spectral_radius_mean']:>7.4f}+/-{m['spectral_radius_std']:.4f}"
        row += f" | {INV_PHI:>8.4f}"
        print(row)

    # =========================================================================
    # Table 2: Trace of W
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 2: Trace of Converged W")
    print("=" * 78)
    print(f"  Prediction: Tr(W) should approach d/phi")
    print()
    header = f"{'d':>4s}"
    for alpha in ALPHAS:
        header += f" | {'alpha=' + str(alpha):>16s}"
    header += f" | {'d/phi':>8s}"
    print(header)
    print("-" * len(header))

    for d in DIMS:
        row = f"{d:>4d}"
        for alpha in ALPHAS:
            m = results[("iid", d, alpha)]
            row += f" | {m['trace_mean']:>7.4f}+/-{m['trace_std']:.4f}"
        row += f" | {d / PHI:>8.4f}"
        print(row)

    # =========================================================================
    # Table 3: Self-consistency residual |lambda^2 + lambda - 1|
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 3: Self-Consistency Residual: mean |lambda^2 + lambda - 1|")
    print("=" * 78)
    print(f"  If eigenvalues satisfy the golden ratio equation, residual -> 0")
    print()
    header = f"{'d':>4s}"
    for alpha in ALPHAS:
        header += f" | {'alpha=' + str(alpha):>16s}"
    print(header)
    print("-" * len(header))

    for d in DIMS:
        row = f"{d:>4d}"
        for alpha in ALPHAS:
            m = results[("iid", d, alpha)]
            row += f" |     mean={m['sc_residual_mean']:>7.4f}"
        print(row)

    # =========================================================================
    # Table 4: Off-diagonal structure
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 4: Off-Diagonal Structure of W")
    print("=" * 78)
    print(f"  off_diag_ratio = ||W - diag(W)||_F / ||diag(W)||_F")
    print(f"  If W is diagonal, ratio -> 0. If off-diagonal structure emerges, ratio > 0.")
    print()
    header = f"{'d':>4s}"
    for alpha in ALPHAS:
        header += f" | {'alpha=' + str(alpha):>16s}"
    print(header)
    print("-" * len(header))

    for d in DIMS:
        row = f"{d:>4d}"
        for alpha in ALPHAS:
            m = results[("iid", d, alpha)]
            row += f" | {m['off_diag_ratio_mean']:>7.4f}+/-{m['off_diag_ratio_std']:.4f}"
        print(row)

    # =========================================================================
    # Table 5: Matrix equation residual ||W^2 + W - I||_F
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 5: Matrix Equation Residual ||W^2 + W - I||_F")
    print("=" * 78)
    print(f"  If the matrix equation W^2 + W - I = 0 holds, residual -> 0")
    print(f"  This is the matrix generalization of w^2 + w - 1 = 0")
    print()
    header = f"{'d':>4s}"
    for alpha in ALPHAS:
        header += f" | {'alpha=' + str(alpha):>16s}"
    print(header)
    print("-" * len(header))

    for d in DIMS:
        row = f"{d:>4d}"
        for alpha in ALPHAS:
            m = results[("iid", d, alpha)]
            row += f" | {m['matrix_residual_norm_mean']:>7.4f}+/-{m['matrix_residual_norm_std']:.4f}"
        print(row)

    # =========================================================================
    # Table 6: Frobenius norm
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 6: Frobenius Norm of Converged W")
    print("=" * 78)
    print(f"  If W ~ (1/phi)*I, then ||W||_F = sqrt(d)/phi")
    print()
    header = f"{'d':>4s}"
    for alpha in ALPHAS:
        header += f" | {'alpha=' + str(alpha):>16s}"
    header += f" | {'sqrt(d)/phi':>11s}"
    print(header)
    print("-" * len(header))

    for d in DIMS:
        row = f"{d:>4d}"
        for alpha in ALPHAS:
            m = results[("iid", d, alpha)]
            row += f" | {m['frob_norm_mean']:>7.4f}+/-{m['frob_norm_std']:.4f}"
        row += f" | {np.sqrt(d) / PHI:>11.4f}"
        print(row)

    # =========================================================================
    # Table 7: Eigenvalue details (alpha=1.0, first seed)
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 7: Eigenvalue Details (alpha=1.0, first seed)")
    print("=" * 78)
    print(f"  Golden ratio equation: lambda^2 + lambda - 1 = 0 => lambda = 1/phi = {INV_PHI:.6f}")
    print()

    for d in DIMS:
        m = results[("iid", d, 1.0)]
        eigs = m["eigenvalues_first"]
        print(f"  d = {d}:")
        print(f"    {'Eigenvalue':>20s} {'|lambda|':>10s} {'lambda^2+lambda-1':>20s} {'|resid|':>10s}")
        print(f"    " + "-" * 65)
        for i, lam in enumerate(eigs):
            resid = lam**2 + lam - 1.0
            if np.isreal(lam):
                print(f"    {lam.real:>20.6f} {abs(lam):>10.6f} {resid.real:>20.6f} {abs(resid):>10.6f}")
            else:
                print(f"    {lam.real:>9.6f}{lam.imag:+.6f}i {abs(lam):>10.6f} "
                      f"{resid.real:>9.6f}{resid.imag:+.6f}i {abs(resid):>10.6f}")
        print()

    # =========================================================================
    # Table 8: Correlated vs iid signals
    # =========================================================================
    print("=" * 78)
    print("TABLE 8: Correlated vs IID Signals (alpha=1.0)")
    print("=" * 78)
    print(f"  Does the self-consistency equation hold with correlated inputs?")
    print()
    print(f"  {'d':>4s} | {'IID spec_rad':>14s} | {'Corr spec_rad':>14s} | "
          f"{'IID SC_resid':>14s} | {'Corr SC_resid':>14s} | "
          f"{'IID off_diag':>14s} | {'Corr off_diag':>14s}")
    print("  " + "-" * 100)

    for d in DIMS:
        m_iid = results[("iid", d, 1.0)]
        m_corr = results[("correlated", d, 1.0)]
        print(f"  {d:>4d} | {m_iid['spectral_radius_mean']:>14.4f} | {m_corr['spectral_radius_mean']:>14.4f} | "
              f"{m_iid['sc_residual_mean']:>14.4f} | {m_corr['sc_residual_mean']:>14.4f} | "
              f"{m_iid['off_diag_ratio_mean']:>14.4f} | {m_corr['off_diag_ratio_mean']:>14.4f}")

    # =========================================================================
    # Table 9: R^2 summary
    # =========================================================================
    print("\n" + "=" * 78)
    print("TABLE 9: R^2 (Prediction Quality) Summary")
    print("=" * 78)
    print()
    header = f"{'d':>4s}"
    for alpha in ALPHAS:
        header += f" | {'alpha=' + str(alpha):>16s}"
    print(header)
    print("-" * len(header))

    for d in DIMS:
        row = f"{d:>4d}"
        for alpha in ALPHAS:
            m = results[("iid", d, alpha)]
            row += f" | {m['r2_mean']:>7.4f}+/-{m['r2_std']:.4f}"
        print(row)

    # =========================================================================
    # Honest assessment
    # =========================================================================
    print("\n" + "=" * 78)
    print("HONEST ASSESSMENT")
    print("=" * 78)

    # 1. Does spectral radius -> 1/phi?
    print(f"\n1. SPECTRAL RADIUS:")
    for d in DIMS:
        m = results[("iid", d, 1.0)]
        diff = abs(m["spectral_radius_mean"] - INV_PHI)
        print(f"   d={d:2d}: spectral_radius = {m['spectral_radius_mean']:.6f}, "
              f"diff from 1/phi = {diff:.6f}")

    # Overall check
    diffs = [abs(results[("iid", d, 1.0)]["spectral_radius_mean"] - INV_PHI) for d in DIMS]
    mean_diff = np.mean(diffs)
    if mean_diff < 0.02:
        print(f"\n   --> Spectral radius is CLOSE to 1/phi across dimensions (mean diff = {mean_diff:.4f})")
        print(f"       The largest eigenvalue magnitude converges to the golden ratio.")
    elif mean_diff < 0.10:
        print(f"\n   --> Spectral radius is MODERATELY close to 1/phi (mean diff = {mean_diff:.4f})")
        print(f"       Approximate convergence, possibly needs more steps or smaller LR.")
    else:
        print(f"\n   --> Spectral radius DIFFERS from 1/phi (mean diff = {mean_diff:.4f})")
        print(f"       The matrix generalization may not simply extend the scalar case.")

    # 2. Does Trace -> d/phi?
    print(f"\n2. TRACE:")
    for d in DIMS:
        m = results[("iid", d, 1.0)]
        expected = d / PHI
        diff = abs(m["trace_mean"] - expected)
        print(f"   d={d:2d}: Tr(W) = {m['trace_mean']:.6f}, d/phi = {expected:.6f}, diff = {diff:.6f}")

    trace_diffs = [abs(results[("iid", d, 1.0)]["trace_mean"] - d / PHI) for d in DIMS]
    mean_trace_diff = np.mean(trace_diffs)
    if mean_trace_diff < 0.1:
        print(f"\n   --> Trace closely matches d/phi (mean diff = {mean_trace_diff:.4f})")
    else:
        print(f"\n   --> Trace deviates from d/phi (mean diff = {mean_trace_diff:.4f})")

    # 3. Does W become diagonal?
    print(f"\n3. DIAGONAL STRUCTURE (alpha=1.0):")
    for d in DIMS:
        m = results[("iid", d, 1.0)]
        ratio = m["off_diag_ratio_mean"]
        if ratio < 0.1:
            verdict = "NEARLY DIAGONAL"
        elif ratio < 0.5:
            verdict = "MOSTLY DIAGONAL"
        else:
            verdict = "SIGNIFICANT OFF-DIAGONAL STRUCTURE"
        print(f"   d={d:2d}: off_diag_ratio = {ratio:.4f} => {verdict}")

    # 4. Matrix equation
    print(f"\n4. MATRIX EQUATION W^2 + W - I = 0 (alpha=1.0):")
    for d in DIMS:
        m = results[("iid", d, 1.0)]
        norm = m["matrix_residual_norm_mean"]
        # Normalize by sqrt(d) to get per-element scale
        per_element = norm / d if d > 0 else norm
        print(f"   d={d:2d}: ||W^2+W-I||_F = {norm:.6f} "
              f"(per-element ~ {per_element:.6f})")

    resid_norms = [results[("iid", d, 1.0)]["matrix_residual_norm_mean"] / d for d in DIMS]
    mean_mat_resid = np.mean(resid_norms)
    if mean_mat_resid < 0.05:
        print(f"\n   --> Matrix equation W^2 + W - I = 0 holds WELL (mean per-elem = {mean_mat_resid:.4f})")
    elif mean_mat_resid < 0.2:
        print(f"\n   --> Matrix equation holds APPROXIMATELY (mean per-elem = {mean_mat_resid:.4f})")
    else:
        print(f"\n   --> Matrix equation does NOT hold well (mean per-elem = {mean_mat_resid:.4f})")

    # 5. Eigenvalue self-consistency
    print(f"\n5. EIGENVALUE SELF-CONSISTENCY (alpha=1.0):")
    for d in DIMS:
        m = results[("iid", d, 1.0)]
        print(f"   d={d:2d}: mean |lambda^2 + lambda - 1| = {m['sc_residual_mean']:.6f}, "
              f"max = {m['sc_residual_max']:.6f}")

    sc_means = [results[("iid", d, 1.0)]["sc_residual_mean"] for d in DIMS]
    if np.mean(sc_means) < 0.05:
        print(f"\n   --> Individual eigenvalues satisfy lambda^2 + lambda - 1 = 0 WELL")
    elif np.mean(sc_means) < 0.2:
        print(f"\n   --> Individual eigenvalues APPROXIMATELY satisfy the equation")
    else:
        print(f"\n   --> Individual eigenvalues do NOT satisfy the equation well")

    # 6. Effect of alpha
    print(f"\n6. EFFECT OF ALPHA:")
    print(f"   alpha=0 means no self-reference (y(t)=s(t)), so W just learns W @ s ~ s => W ~ I")
    print(f"   alpha=1 is full self-reference, where the self-consistency equation should matter")
    for d in [1, 4, 16]:
        print(f"\n   d={d}:")
        for alpha in ALPHAS:
            m = results[("iid", d, alpha)]
            print(f"     alpha={alpha:.1f}: spec_rad={m['spectral_radius_mean']:.4f}, "
                  f"trace={m['trace_mean']:.4f}, "
                  f"SC_resid={m['sc_residual_mean']:.4f}")

    # 7. Correlated signals
    print(f"\n7. CORRELATED SIGNALS (alpha=1.0):")
    print(f"   With correlated input (Sigma != I), does the self-consistency still hold?")
    for d in DIMS:
        m_iid = results[("iid", d, 1.0)]
        m_corr = results[("correlated", d, 1.0)]
        sr_diff = abs(m_iid["spectral_radius_mean"] - m_corr["spectral_radius_mean"])
        sc_diff = abs(m_iid["sc_residual_mean"] - m_corr["sc_residual_mean"])
        print(f"   d={d:2d}: spec_rad diff (iid vs corr) = {sr_diff:.4f}, "
              f"SC_resid diff = {sc_diff:.4f}, "
              f"corr off_diag_ratio = {m_corr['off_diag_ratio_mean']:.4f}")

    corr_sr = [results[("correlated", d, 1.0)]["spectral_radius_mean"] for d in DIMS]
    corr_diffs = [abs(sr - INV_PHI) for sr in corr_sr]
    mean_corr_diff = np.mean(corr_diffs)
    if mean_corr_diff < 0.05:
        print(f"\n   --> Correlated signals: spectral radius STILL close to 1/phi (mean diff = {mean_corr_diff:.4f})")
        print(f"       Self-consistency equation extends to correlated inputs!")
    else:
        print(f"\n   --> Correlated signals: spectral radius differs from 1/phi (mean diff = {mean_corr_diff:.4f})")
        print(f"       Input correlations modify the fixed point.")

    # 8. Overall verdict
    print(f"\n8. OVERALL VERDICT:")
    all_close = (mean_diff < 0.05 and mean_trace_diff < 0.5 and np.mean(sc_means) < 0.1)
    if all_close:
        print(f"   The self-consistency equation W^2 + W - I = 0 DOES extend to matrices.")
        print(f"   Key findings:")
        print(f"   - Spectral radius converges to 1/phi across dimensions")
        print(f"   - Trace converges to d/phi")
        print(f"   - Individual eigenvalues satisfy lambda^2 + lambda - 1 ~ 0")
        print(f"   - This is because with iid signals, the optimal W is ~ (1/phi)*I")
        print(f"     (a scaled identity), reducing the matrix equation to the scalar one.")
        print(f"   - With correlated signals, W adapts its eigenvectors but the")
        print(f"     eigenvalue magnitudes still reflect the self-consistency constraint.")
    else:
        print(f"   Results are MIXED. The matrix generalization is non-trivial:")
        print(f"   - Spectral radius mean diff from 1/phi: {mean_diff:.4f}")
        print(f"   - Trace mean diff from d/phi: {mean_trace_diff:.4f}")
        print(f"   - Mean eigenvalue SC residual: {np.mean(sc_means):.4f}")
        print(f"   The multi-dimensional case may require a different self-consistency")
        print(f"   equation that accounts for matrix structure and cross-dimensional coupling.")

    return results


# ==============================================================================
# Plotting
# ==============================================================================
def make_plots(results):
    """Generate multi-panel plot."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not available, skipping plots.")
        return

    fig, axes = plt.subplots(3, 3, figsize=(18, 16))
    fig.suptitle("Multi-Dimensional Self-Referential Consistency Check",
                 fontsize=14, fontweight="bold")

    dim_colors = {1: "#E91E63", 2: "#2196F3", 4: "#4CAF50", 8: "#FF9800", 16: "#9C27B0"}

    # ------------------------------------------------------------------
    # Panel 1: Spectral radius vs dimension (alpha=1.0)
    # ------------------------------------------------------------------
    ax = axes[0, 0]
    for d in DIMS:
        m = results[("iid", d, 1.0)]
        ax.bar(str(d), m["spectral_radius_mean"], yerr=m["spectral_radius_std"],
               color=dim_colors[d], alpha=0.8, capsize=3, edgecolor="black", linewidth=0.5)
    ax.axhline(INV_PHI, color="red", linestyle="--", alpha=0.7, label=f"1/phi={INV_PHI:.4f}")
    ax.set_xlabel("Dimension d")
    ax.set_ylabel("Spectral Radius")
    ax.set_title("Spectral Radius (alpha=1.0)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # ------------------------------------------------------------------
    # Panel 2: Spectral radius vs alpha for each d
    # ------------------------------------------------------------------
    ax = axes[0, 1]
    for d in DIMS:
        srs = [results[("iid", d, a)]["spectral_radius_mean"] for a in ALPHAS]
        ax.plot(ALPHAS, srs, "o-", color=dim_colors[d], label=f"d={d}", markersize=5)
    ax.axhline(INV_PHI, color="red", linestyle="--", alpha=0.7, label=f"1/phi")
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Spectral Radius")
    ax.set_title("Spectral Radius vs Alpha")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Panel 3: Trace vs dimension
    # ------------------------------------------------------------------
    ax = axes[0, 2]
    actual_traces = [results[("iid", d, 1.0)]["trace_mean"] for d in DIMS]
    expected_traces = [d / PHI for d in DIMS]
    x_pos = np.arange(len(DIMS))
    width = 0.35
    ax.bar(x_pos - width/2, actual_traces, width, label="Actual Tr(W)", color="#2196F3",
           alpha=0.8, edgecolor="black", linewidth=0.5)
    ax.bar(x_pos + width/2, expected_traces, width, label="d/phi", color="#FF5722",
           alpha=0.8, edgecolor="black", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(d) for d in DIMS])
    ax.set_xlabel("Dimension d")
    ax.set_ylabel("Trace")
    ax.set_title("Trace of W vs d/phi (alpha=1.0)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # ------------------------------------------------------------------
    # Panel 4: Self-consistency residual vs dimension
    # ------------------------------------------------------------------
    ax = axes[1, 0]
    for d in DIMS:
        sc_means = [results[("iid", d, a)]["sc_residual_mean"] for a in ALPHAS]
        ax.plot(ALPHAS, sc_means, "o-", color=dim_colors[d], label=f"d={d}", markersize=5)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Mean |lambda^2 + lambda - 1|")
    ax.set_title("Self-Consistency Residual")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Panel 5: Off-diagonal ratio vs dimension
    # ------------------------------------------------------------------
    ax = axes[1, 1]
    for alpha in ALPHAS:
        ratios = [results[("iid", d, alpha)]["off_diag_ratio_mean"] for d in DIMS]
        ax.plot([str(d) for d in DIMS], ratios, "o-", label=f"alpha={alpha}", markersize=5)
    ax.set_xlabel("Dimension d")
    ax.set_ylabel("Off-Diagonal Ratio")
    ax.set_title("Off-Diagonal Structure")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Panel 6: Matrix equation residual
    # ------------------------------------------------------------------
    ax = axes[1, 2]
    for d in DIMS:
        norms = [results[("iid", d, a)]["matrix_residual_norm_mean"] for a in ALPHAS]
        ax.plot(ALPHAS, norms, "o-", color=dim_colors[d], label=f"d={d}", markersize=5)
    ax.set_xlabel("Alpha")
    ax.set_ylabel("||W^2 + W - I||_F")
    ax.set_title("Matrix Equation Residual")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Panel 7: Eigenvalue spectrum (alpha=1.0, d=8)
    # ------------------------------------------------------------------
    ax = axes[2, 0]
    # Show eigenvalues in complex plane for multiple dimensions
    for d in [2, 4, 8, 16]:
        m = results[("iid", d, 1.0)]
        eigs = m["eigenvalues_first"]
        ax.scatter(eigs.real, eigs.imag, color=dim_colors[d], s=40, alpha=0.7,
                   edgecolors="black", linewidth=0.5, label=f"d={d}", zorder=5)

    # Draw circle at radius 1/phi
    theta = np.linspace(0, 2 * np.pi, 100)
    ax.plot(INV_PHI * np.cos(theta), INV_PHI * np.sin(theta), "r--", alpha=0.5,
            label=f"|lambda|=1/phi")
    ax.axhline(0, color="gray", linewidth=0.3)
    ax.axvline(0, color="gray", linewidth=0.3)
    ax.set_xlabel("Re(lambda)")
    ax.set_ylabel("Im(lambda)")
    ax.set_title("Eigenvalue Spectrum (alpha=1.0)")
    ax.legend(fontsize=6)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # ------------------------------------------------------------------
    # Panel 8: IID vs correlated (spectral radius)
    # ------------------------------------------------------------------
    ax = axes[2, 1]
    sr_iid = [results[("iid", d, 1.0)]["spectral_radius_mean"] for d in DIMS]
    sr_corr = [results[("correlated", d, 1.0)]["spectral_radius_mean"] for d in DIMS]
    x_pos = np.arange(len(DIMS))
    width = 0.35
    ax.bar(x_pos - width/2, sr_iid, width, label="IID signals", color="#2196F3",
           alpha=0.8, edgecolor="black", linewidth=0.5)
    ax.bar(x_pos + width/2, sr_corr, width, label="Correlated signals", color="#FF9800",
           alpha=0.8, edgecolor="black", linewidth=0.5)
    ax.axhline(INV_PHI, color="red", linestyle="--", alpha=0.7, label=f"1/phi")
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(d) for d in DIMS])
    ax.set_xlabel("Dimension d")
    ax.set_ylabel("Spectral Radius")
    ax.set_title("IID vs Correlated (alpha=1.0)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis="y")

    # ------------------------------------------------------------------
    # Panel 9: Frobenius norm vs sqrt(d)/phi
    # ------------------------------------------------------------------
    ax = axes[2, 2]
    actual_frob = [results[("iid", d, 1.0)]["frob_norm_mean"] for d in DIMS]
    expected_frob = [np.sqrt(d) / PHI for d in DIMS]
    ax.plot(DIMS, actual_frob, "o-", color="#2196F3", label="Actual ||W||_F", markersize=6)
    ax.plot(DIMS, expected_frob, "s--", color="#FF5722", label="sqrt(d)/phi", markersize=6)
    ax.set_xlabel("Dimension d")
    ax.set_ylabel("Frobenius Norm")
    ax.set_title("Frobenius Norm vs sqrt(d)/phi")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "multidim_selfref_results.png")
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
