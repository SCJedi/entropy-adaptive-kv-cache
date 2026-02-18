"""
Diagnostic: Investigating the correct mean-field formulation.

FINDING: Without bias (sigma_b=0), self-gating activations f(x)=x*g(x)
have ONLY q=0 as a forward fixed point (when sigma_b=0). Chi_1=1 at q=0
gives sigma_w = 1/|f'(0)| = 2.0 for GELU/Swish. This is not interesting.

HYPOTHESIS: The interesting critical point arises when sigma_b > 0, OR
when we use the standard formulation with both mean and variance tracking.

Let me try the FULL mean-field theory:
  mu^{l+1} = sigma_w * E[f(z)]  (mean propagation, but typically 0 by symmetry argument)
  q^{l+1} = sigma_w^2 * E[f(z)^2] + sigma_b^2  (second moment propagation)

Actually, for networks: the pre-activation is h = W*x + b where W has
i.i.d. entries ~ N(0, sigma_w^2/n). If inputs have mean 0 and variance q,
then h ~ N(0, sigma_w^2 * q + sigma_b^2) (by CLT).

Wait, no. The output is y = f(h), and the next layer pre-activation is
h' = W' * y + b'. The variance of h' is:
  Var(h') = sigma_w^2 * E[f(h)^2] + sigma_b^2
  (using E[f(h)] can be nonzero, but Var(h') = sw^2/n * sum E[f(h_i)^2])

Actually it's: Var(h'_j) = sigma_w^2 * (1/n) * sum_i E[y_i^2] + sigma_b^2
                          = sigma_w^2 * E[f(h)^2] + sigma_b^2

And E[h^2] = sigma_w^2 * E[f(h_prev)^2] + sigma_b^2.

So with sigma_b > 0, q* is the solution of:
  q = sigma_w^2 * E[f(z)^2] + sigma_b^2

This ALWAYS has a solution for sigma_b > 0.

Let me explore: for sigma_b = 0, the critical point is at q=0. But perhaps
we should instead look at the problem as: given that we want sigma_w near
some target, what sigma_b gives chi_1 = 1?

OR: Perhaps the script is using a different convention where sigma_w^2
multiplies E[(f(z)/z)^2 * z^2] = E[g(z)^2 * z^2] differently.

Actually, let me re-read the Poole et al. (2016) "Exponential expressivity"
paper and the Schoenholz et al. (2017) mean field theory.

The standard formulation from those papers:
  q^{l+1} = sigma_w^2 * integral phi(z)^2 * Dz + sigma_b^2
where Dz = N(0, q^l) measure, and phi is the activation.

chi_1 = sigma_w^2 * integral phi'(z)^2 * Dz

At the fixed point q* (with sigma_b^2 > 0):
  q* = sigma_w^2 * E[phi(z)^2] + sigma_b^2  where z ~ N(0, q*)
  chi_1 = sigma_w^2 * E[phi'(z)^2]  where z ~ N(0, q*)

For edge of chaos: chi_1 = 1.

So the system IS:
  q = sw^2 * E[f^2] + sb^2
  sw^2 * E[f'^2] = 1

Two equations, three unknowns (sw, sb, q). Need to fix one.

Common approach: fix sigma_b (e.g., sigma_b = 0), then sweep sigma_w.
With sigma_b = 0: only q=0 fixed point for self-gating. Boring.

OR: parameterize by (sigma_w, sigma_b) and find the manifold where chi_1=1.

Actually, in practice people often use sigma_b > 0. Let me try sigma_b = 0.1
or parameterize it.

ALTERNATIVE: Maybe the paper uses the convention where the weight matrix
is W ~ N(0, sigma_w^2) (not sigma_w^2/n), and the activation includes
the 1/sqrt(n) factor? That changes the equations.

Actually I think the real issue may be simpler. Let me check: does the
original code's fsolve fail because of the scipy.integrate.quad being slow
and inaccurate, causing the Jacobian approximation to be garbage? The
Gauss-Hermite approach should fix that.

Let me just try: replace the `expect` function with Gauss-Hermite in the
original code's `find_critical_point` and see if fsolve works.

Wait - I already showed that A(q) < B(q) for ALL q. This means at any
fixed point q* (satisfying sw^2 * A(q*) = 1), we have chi_1 = sw^2 * B(q*) > 1.
There is NO sigma_w that gives both chi_1 = 1 and a nontrivial fixed point
without bias.

So the system as formulated in the original code is UNSOLVABLE for sigma_b=0.

Let me try with sigma_b > 0.
"""

import numpy as np
from scipy import optimize
from scipy.special import erf

# ---- Gauss-Hermite quadrature ----
GH_DEGREE = 100
GH_NODES, GH_WEIGHTS = np.polynomial.hermite.hermgauss(GH_DEGREE)

def expect_gh(func, q):
    """E[func(z)] where z ~ N(0, q), using Gauss-Hermite quadrature."""
    z = np.sqrt(2 * q) * GH_NODES
    values = func(z)
    return np.sum(GH_WEIGHTS * values) / np.sqrt(np.pi)

# ---- Basic functions ----
def gaussian_cdf(x):
    return 0.5 * (1 + erf(x / np.sqrt(2)))
def gaussian_pdf(x):
    return np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
def sigmoid(x):
    return np.where(x >= 0,
                    1 / (1 + np.exp(np.where(x >= 0, -x, 0))),
                    np.exp(np.where(x < 0, x, 0)) / (1 + np.exp(np.where(x < 0, x, 0))))
def sigmoid_deriv(x):
    s = sigmoid(x)
    return s * (1 - s)
def softplus(x):
    return np.where(x > 20, x, np.log1p(np.exp(np.minimum(x, 20.0))))
def mish_gate(x):
    return np.tanh(softplus(x))

PHI = (1 + np.sqrt(5)) / 2
THREE_MINUS_PHI = 3 - PHI

# ---- Activations ----
def gelu(x): return x * gaussian_cdf(x)
def gelu_prime(x): return gaussian_cdf(x) + x * gaussian_pdf(x)

def swish_(x): return x * sigmoid(x)
def swish_prime_(x):
    s = sigmoid(x)
    return s + x * s * (1 - s)

def mish_(x): return x * mish_gate(x)
def mish_prime_(x):
    h = 1e-5
    return (mish_(x + h) - mish_(x - h)) / (2 * h)

lam_o = 0.3757
def ouro(x): return x * (lam_o + (1 - lam_o) * sigmoid(x))
def ouro_prime(x):
    s = sigmoid(x)
    return lam_o + (1 - lam_o) * (s + x * s * (1 - s))

# ============================================================
# Approach 1: Include sigma_b^2 > 0
# System: q = sw^2 * E[f^2] + sb^2, sw^2 * E[f'^2] = 1
# Fix sb, solve for (sw, q).
# ============================================================
print("=" * 70)
print("APPROACH 1: With sigma_b > 0")
print("  q = sw^2 * E[f^2] + sb^2")
print("  sw^2 * E[f'^2] = 1")
print("=" * 70)

def find_critical_with_bias(f, fp, sb, name=""):
    """Find (sigma_w, q*) given sigma_b."""

    def system(log_q):
        """Given q, compute sw from chi_1=1, then check forward eq."""
        q = np.exp(log_q)
        Efp2 = expect_gh(lambda z: fp(z)**2, q)
        if Efp2 <= 0:
            return 1e10
        sw2 = 1.0 / Efp2  # from chi_1 = 1
        Ef2 = expect_gh(lambda z: f(z)**2, q)
        # Forward: q = sw^2 * Ef2 + sb^2
        return q - sw2 * Ef2 - sb**2

    # Sweep to find bracket
    lqs = np.linspace(-3, 8, 500)
    vals = [system(lq) for lq in lqs]

    for i in range(len(vals)-1):
        if vals[i] * vals[i+1] < 0:
            lq_sol = optimize.brentq(system, lqs[i], lqs[i+1], xtol=1e-14)
            q = np.exp(lq_sol)
            Efp2 = expect_gh(lambda z: fp(z)**2, q)
            sw = np.sqrt(1.0 / Efp2)
            chi1 = sw**2 * Efp2
            Ef2 = expect_gh(lambda z: f(z)**2, q)
            fwd = sw**2 * Ef2 + sb**2
            return sw, q, chi1, fwd
    return None, None, None, None

activations = [
    (gelu, gelu_prime, "GELU"),
    (swish_, swish_prime_, "Swish"),
    (mish_, mish_prime_, "Mish"),
    (ouro, ouro_prime, "Ouroboros"),
]

for sb in [0.0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0]:
    print(f"\n  sigma_b = {sb}")
    for f, fp, name in activations:
        sw, q, chi1, fwd = find_critical_with_bias(f, fp, sb, name)
        if sw is not None:
            print(f"    {name:12s}: sw={sw:.6f}, q*={q:.6f}, chi1={chi1:.6f}, fwd_check={fwd:.6f} (q*={q:.6f})")
        else:
            print(f"    {name:12s}: FAILED")

# ============================================================
# Approach 2: sigma_b = 0, but check if there's a different formulation
# For networks without bias, maybe we should track the CENTERED second moment.
# Or perhaps the convention is q = sw^2 * Var[f(z)] (not E[f^2]).
# ============================================================
print("\n" + "=" * 70)
print("APPROACH 2: Using VARIANCE instead of second moment")
print("  q = sw^2 * Var[f(z)]  where Var = E[f^2] - (E[f])^2")
print("  sw^2 * E[f'^2] = 1")
print("=" * 70)

def find_critical_variance(f, fp, name=""):
    """Use Var[f(z)] instead of E[f(z)^2] in the forward equation."""

    def system(log_q):
        q = np.exp(log_q)
        Ef = expect_gh(lambda z: f(z), q)
        Ef2 = expect_gh(lambda z: f(z)**2, q)
        Var_f = Ef2 - Ef**2
        Efp2 = expect_gh(lambda z: fp(z)**2, q)
        if Efp2 <= 0:
            return 1e10
        sw2 = 1.0 / Efp2
        return q - sw2 * Var_f

    lqs = np.linspace(-3, 8, 500)
    vals = [system(lq) for lq in lqs]

    for i in range(len(vals)-1):
        if vals[i] * vals[i+1] < 0:
            lq_sol = optimize.brentq(system, lqs[i], lqs[i+1], xtol=1e-14)
            q = np.exp(lq_sol)
            Efp2 = expect_gh(lambda z: fp(z)**2, q)
            sw = np.sqrt(1.0 / Efp2)
            chi1 = sw**2 * Efp2
            Ef = expect_gh(lambda z: f(z), q)
            Ef2 = expect_gh(lambda z: f(z)**2, q)
            Var_f = Ef2 - Ef**2
            fwd = sw**2 * Var_f
            return sw, q, chi1, fwd
    return None, None, None, None

print("\nUsing Var[f(z)] = E[f^2] - E[f]^2:")
for f, fp, name in activations:
    sw, q, chi1, fwd = find_critical_variance(f, fp, name)
    if sw is not None:
        print(f"  {name:12s}: sw={sw:.10f}, q*={q:.10f}, chi1={chi1:.10f}, var_check={fwd:.10f}")
        print(f"  {'':12s}  3-phi={THREE_MINUS_PHI:.10f}, diff={abs(sw-THREE_MINUS_PHI):.6e}")
    else:
        print(f"  {name:12s}: FAILED")

# Check: for GELU, E[f(z)] = E[z*Phi(z)]. Since GELU is not odd, E[f] != 0.
print("\nE[f(z)] for GELU at various q:")
for q in [0.1, 1.0, 5.0, 20.0]:
    Ef = expect_gh(lambda z: gelu(z), q)
    Ef2 = expect_gh(lambda z: gelu(z)**2, q)
    Var = Ef2 - Ef**2
    print(f"  q={q:.1f}: E[f]={Ef:.6f}, E[f^2]={Ef2:.6f}, Var={Var:.6f}, Var/q={Var/q:.6f}")


# ============================================================
# Approach 3: Check if maybe the mean field uses:
# q = sw^2 * (E[f^2] - E[f]^2)  (centered)
# OR with mean propagation:
# mu = sw * E[f(z)] (mean)
# v = sw^2 * (E[f^2] - E[f]^2) (variance)
# q = mu^2 + v (total second moment)
# ============================================================
print("\n" + "=" * 70)
print("APPROACH 3: Full mean + variance propagation")
print("  mu = sw * E[f(z)]  where z ~ N(mu, v)")
print("  v  = sw^2 * Var[f(z)]")
print("  q  = mu^2 + v  (total pre-activation second moment)")
print("  z ~ N(mu, v) at fixed point")
print("=" * 70)

def expect_gh_nonzero_mean(func, mu, v):
    """E[func(z)] where z ~ N(mu, v)."""
    if v < 1e-15:
        return func(np.array([mu]))[0] if hasattr(func(np.array([mu])), '__len__') else func(mu)
    z = mu + np.sqrt(2 * v) * GH_NODES
    values = func(z)
    return np.sum(GH_WEIGHTS * values) / np.sqrt(np.pi)

def find_critical_full_mf(f, fp, name=""):
    """Full mean-field: track (mu, v) fixed point with chi_1 = 1."""

    def system(params):
        mu, log_v = params
        v = np.exp(log_v)

        Ef = expect_gh_nonzero_mean(f, mu, v)
        Ef2 = expect_gh_nonzero_mean(lambda z: f(z)**2, mu, v)
        Efp2 = expect_gh_nonzero_mean(lambda z: fp(z)**2, mu, v)

        Var_f = Ef2 - Ef**2

        # From chi_1 = sw^2 * Efp2 = 1:
        if Efp2 <= 0:
            return [1e10, 1e10]
        sw2 = 1.0 / Efp2

        # Mean: mu = sw * E[f(z)]  -- but wait, in mean field without bias,
        # pre-activation h = W*y, and E[h] = 0 by symmetry of W.
        # Unless there's a bias. Without bias, mu = 0 always.
        # So the mean propagation doesn't help.

        # With mu = 0:
        # v = sw^2 * E[f^2]  (since Var = E[f^2] when E[f]=0... but E[f]!=0 for GELU!)

        # Actually, in mean field: each pre-activation h_i = sum_j W_ij * f(h_j^{prev})
        # E[h_i] = sum_j E[W_ij] * E[f(h_j)] = 0 (since E[W_ij] = 0)
        # So mu = 0 always, regardless of activation symmetry.
        # Then Var[h_i] = E[h_i^2] = sum_j E[W_ij^2] * E[f(h_j)^2] = sw^2 * E[f(z)^2]
        # where z ~ N(0, q) and q = Var[h] at fixed point.

        # So the correct equation IS q = sw^2 * E[f(z)^2], z~N(0,q).
        # And this has no nontrivial solution for self-gating without bias.

        return [0, 0]  # placeholder

    # The mean-field theory with zero-mean weights forces mu = 0.
    # So we're back to q = sw^2 * E[f^2] with z ~ N(0,q).
    print(f"  {name}: Mean field with zero-mean weights forces mu=0.")
    print(f"  This means q = sw^2 * E[f(z)^2] where z~N(0,q).")
    print(f"  For self-gating without bias, only q=0 is a fixed point.")
    return None, None

# Don't run approach 3 - it's the same as approach with sigma_b = 0

# ============================================================
# Approach 4: Maybe the CORRECT formulation uses sigma_b > 0
# and the script simply forgot to include it. In practice,
# PyTorch/TensorFlow layers have biases by default.
# Let me find what sigma_b makes sigma_w = 3-phi.
# ============================================================
print("\n" + "=" * 70)
print("APPROACH 4: What sigma_b gives sigma_w = 3-phi at criticality?")
print("=" * 70)

for f, fp, name in activations:
    print(f"\n--- {name} ---")
    print(f"  {'sb':>8} | {'sw':>10} | {'q*':>10} | {'diff(sw, 3-phi)':>16}")
    print(f"  {'-'*55}")

    target_sw = THREE_MINUS_PHI

    for sb in np.linspace(0.01, 2.0, 100):
        sw, q, chi1, fwd = find_critical_with_bias(f, fp, sb, name)
        if sw is not None:
            diff = sw - target_sw
            marker = " <--" if abs(diff) < 0.02 else ""
            if abs(diff) < 0.1 or sb < 0.05 or sb > 1.9:
                print(f"  {sb:8.4f} | {sw:10.6f} | {q:10.6f} | {diff:16.6f}{marker}")

# ============================================================
# FINAL: Try the original formulation but with sigma_b as a free parameter.
# The system becomes: 3 equations, 3 unknowns (sw, sb, q):
#   q = sw^2 * E[f^2] + sb^2
#   sw^2 * E[f'^2] = 1
#   sw = 3 - phi  (constrain to golden ratio)
# ============================================================
print("\n" + "=" * 70)
print("APPROACH 5: Does sigma_b = 0 work if we DON'T require nontrivial q*?")
print("  At q=0: chi_1 = sw^2 * f'(0)^2")
print("  f'(0) values for each activation:")
print("=" * 70)

for f, fp, name in activations:
    fp0 = fp(np.array([0.0]))[0] if hasattr(fp(np.array([0.0])), '__len__') else fp(0.0)
    sw_crit = 1.0 / abs(fp0)
    print(f"  {name:12s}: f'(0) = {fp0:.6f}, sw_crit = 1/|f'(0)| = {sw_crit:.6f}")

print(f"\n  3 - phi = {THREE_MINUS_PHI:.6f}")
print(f"  All give sw_crit = 2.0, not 3-phi. So sigma_b > 0 is needed.")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("""
The original script's find_critical_point function fails because:

1. It uses q = sw^2 * E[f(z)^2] with sigma_b = 0.
2. For self-gating activations f(x) = x*g(x), the ONLY fixed point
   at sigma_b = 0 is q = 0 (the trivial fixed point).
3. At q = 0, chi_1 = sw^2 * f'(0)^2, giving sw_crit = 2.0 for all
   these activations (since f'(0) = g(0) = 0.5).
4. The system of equations has NO solution with finite q > 0.

The fix: Include sigma_b^2 in the forward equation:
   q = sw^2 * E[f(z)^2] + sb^2

With sigma_b > 0, nontrivial fixed points exist and interesting
critical sigma_w values emerge.

For a physically meaningful setup, we can either:
  (a) Fix sigma_b to some value and find critical (sw, q)
  (b) Parameterize by (sw, sb) and find the criticality manifold
  (c) Use the convention sigma_b = sigma_w (common in some papers)
""")
