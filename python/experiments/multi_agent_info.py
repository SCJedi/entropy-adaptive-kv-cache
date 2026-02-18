"""
Multi-agent information theory for self-referential observers.

Each agent observes y_i(t) = s(t) + alpha_i * w_i * y_i(t-1).
At the myopic fixed point: alpha_i^2 * w_i^2 + w_i - 1 = 0.

Key insight: agents with the SAME alpha observing the SAME signal produce
IDENTICAL observations (deterministic function of shared s). So perspective
"difference" must come from different alphas or different noise.

We use analytical covariance matrices (exact for this linear Gaussian system)
and handle numerical conditioning carefully.

Marcus Webb, 2026-02-12
"""
import numpy as np

PHI = (1 + np.sqrt(5)) / 2

def myopic_weight(alpha):
    """Solve alpha^2 * w^2 + w - 1 = 0 for positive w."""
    if alpha == 0:
        return 1.0
    return (-1 + np.sqrt(1 + 4 * alpha**2)) / (2 * alpha**2)

def build_cov_analytical(alphas, sigma_s=1.0):
    """
    Build covariance matrix of (s(t), y_1(t), ..., y_N(t)) analytically.

    y_i(t) = s(t) + rho_i * y_i(t-1),  rho_i = alpha_i * w_i

    At stationarity, y_i is an AR(1) driven by shared s(t):
      y_i(t) = sum_{k=0}^{inf} rho_i^k * s(t-k)

    Therefore:
      Var(y_i) = sigma_s^2 / (1 - rho_i^2)
      Cov(s(t), y_i(t)) = sigma_s^2  [only the k=0 term contributes]
      Cov(y_i(t), y_j(t)) = sum_{k=0}^{inf} rho_i^k * rho_j^k * sigma_s^2
                           = sigma_s^2 / (1 - rho_i * rho_j)

    When rho_i = rho_j, Cov(y_i, y_j) = Var(y_i) -- perfect correlation.
    """
    N = len(alphas)
    ws = [myopic_weight(a) for a in alphas]
    rhos = [alphas[i] * ws[i] for i in range(N)]

    C = np.zeros((N + 1, N + 1))
    C[0, 0] = sigma_s**2

    for i in range(N):
        C[0, i+1] = sigma_s**2
        C[i+1, 0] = sigma_s**2
        C[i+1, i+1] = sigma_s**2 / (1 - rhos[i]**2)

        for j in range(i+1, N):
            C[i+1, j+1] = sigma_s**2 / (1 - rhos[i] * rhos[j])
            C[j+1, i+1] = C[i+1, j+1]

    return C

def mi_from_cov(C, s_idx, y_idx):
    """I(S; Y) from joint covariance matrix via Gaussian formula."""
    s_idx = np.array(s_idx)
    y_idx = np.array(y_idx)

    Sigma_S = C[np.ix_(s_idx, s_idx)]
    Sigma_Y = C[np.ix_(y_idx, y_idx)]
    Sigma_SY = C[np.ix_(s_idx, y_idx)]

    # I(S;Y) = 0.5 * log(det(Sigma_S) * det(Sigma_Y) / det(Sigma_{S,Y}))
    full_idx = np.concatenate([s_idx, y_idx])
    Sigma_full = C[np.ix_(full_idx, full_idx)]

    sign_S, logdet_S = np.linalg.slogdet(Sigma_S)
    sign_Y, logdet_Y = np.linalg.slogdet(Sigma_Y)
    sign_F, logdet_F = np.linalg.slogdet(Sigma_full)

    if sign_S <= 0 or sign_Y <= 0 or sign_F <= 0:
        return 0.0

    return 0.5 * (logdet_S + logdet_Y - logdet_F)

# ============================================================
print("=" * 65)
print("EXPERIMENT 1: Two-agent MI as function of perspective difference")
print("=" * 65)

alpha_base = 0.5
ds = np.linspace(0.001, 0.48, 100)

print(f"\nBase alpha = {alpha_base}")
print(f"{'d':>6} {'a1':>6} {'a2':>6} {'I(s;y1)':>8} {'I(s;y2)':>8} {'I(s;y1,y2)':>11} {'gain over best':>14}")

results_1 = []
for d in ds:
    a1 = alpha_base - d/2
    a2 = alpha_base + d/2
    if a1 < 0.001 or a2 > 0.999:
        continue

    C = build_cov_analytical([a1, a2])
    mi1 = mi_from_cov(C, [0], [1])
    mi2 = mi_from_cov(C, [0], [2])
    mi_j = mi_from_cov(C, [0], [1, 2])
    best = max(mi1, mi2)
    gain = mi_j - best
    results_1.append((d, a1, a2, mi1, mi2, mi_j, gain))

# Print every 10th
for i, r in enumerate(results_1):
    if i % 10 == 0:
        print(f"{r[0]:6.3f} {r[1]:6.3f} {r[2]:6.3f} {r[3]:8.4f} {r[4]:8.4f} {r[5]:11.4f} {r[6]:14.4f}")

# Find peak of I(s; y1, y2)
mi_joints = [r[5] for r in results_1]
gains = [r[6] for r in results_1]
best_joint_idx = np.argmax(mi_joints)
best_gain_idx = np.argmax(gains)

r = results_1[best_joint_idx]
print(f"\nPeak I(s; y1,y2) at d = {r[0]:.4f}: MI = {r[5]:.4f}")
r = results_1[best_gain_idx]
print(f"Peak gain over best single at d = {r[0]:.4f}: gain = {r[6]:.4f}")

# ============================================================
print("\n" + "=" * 65)
print("EXPERIMENT 2: Optimal d* for max joint MI across base alphas")
print("=" * 65)

print(f"\n{'alpha':>6} {'d* (max MI)':>12} {'d*/alpha':>10} {'MI(joint)':>10} {'MI(single)':>11} {'gain':>8}")
for ab in [0.1, 0.2, 0.3, 0.5, 0.7, 0.9]:
    best_mi = -np.inf
    best_d = 0
    best_single = 0
    for d in np.linspace(0.001, min(2*ab - 0.002, 2*(1-ab) - 0.002), 500):
        a1 = ab - d/2
        a2 = ab + d/2
        C = build_cov_analytical([a1, a2])
        mi1 = mi_from_cov(C, [0], [1])
        mi2 = mi_from_cov(C, [0], [2])
        mi_j = mi_from_cov(C, [0], [1, 2])
        if mi_j > best_mi:
            best_mi = mi_j
            best_d = d
            best_single = max(mi1, mi2)
    gain = best_mi - best_single
    print(f"{ab:6.1f} {best_d:12.4f} {best_d/ab:10.4f} {best_mi:10.4f} {best_single:11.4f} {gain:8.4f}")

# ============================================================
print("\n" + "=" * 65)
print("EXPERIMENT 3: N-agent MI saturation (evenly spaced alphas)")
print("=" * 65)

print(f"\nAgents with alphas in [0.1, 0.9]")
print(f"{'N':>4} {'I(s; all y)':>12} {'marginal':>10}")

prev_mi = 0
for N in [1, 2, 3, 4, 5, 6, 7, 8]:
    alphas = list(np.linspace(0.1, 0.9, N))
    C = build_cov_analytical(alphas)
    mi = mi_from_cov(C, [0], list(range(1, N+1)))
    print(f"{N:4d} {mi:12.4f} {mi - prev_mi:10.4f}")
    prev_mi = mi

# ============================================================
print("\n" + "=" * 65)
print("EXPERIMENT 4: Single-agent information content")
print("=" * 65)

print(f"\n{'alpha':>6} {'w':>8} {'rho=aw':>8} {'I(s;y) nats':>12} {'I(s;y) bits':>12} {'R^2':>6}")
for alpha in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]:
    w = myopic_weight(alpha)
    rho = alpha * w
    R2 = w  # Proved: R^2 = w at myopic fixed point
    mi = -0.5 * np.log(1 - R2) if R2 < 1 else float('inf')
    mi_bits = mi / np.log(2) if mi < float('inf') else float('inf')
    print(f"{alpha:6.1f} {w:8.4f} {rho:8.4f} {mi:12.4f} {mi_bits:12.4f} {R2:6.3f}")

# ============================================================
print("\n" + "=" * 65)
print("EXPERIMENT 5: Does max joint MI peak at d related to phi?")
print("=" * 65)

# The joint MI is always maximized at max d (one agent at low alpha = high quality).
# But the DECONTAMINATION SYNERGY is different.
# Define synergy: S = I(s; y1, y2) - I(s; y1) - I(s; y2) + I(y1; y2) ... no,
# Better: the "multi-agent advantage" = I(s; y1, y2) - max(I(s; y1), I(s; y2))
# Or: "decontamination gain" = I(s; y1, y2) / (I(s; y1) + I(s; y2))
# which measures how much of the sum is non-redundant.

print(f"\nSynergy analysis: I(s;y1,y2) vs I(s;y1)+I(s;y2)")
print(f"Non-redundancy ratio = I(s;y1,y2) / (I(s;y1)+I(s;y2))")
print(f"= 1 means fully non-redundant, = 0.5 means fully redundant")

ab = 0.5
print(f"\nalpha_base = {ab}")
print(f"{'d':>6} {'I(joint)':>9} {'I1+I2':>9} {'ratio':>7} {'synergy':>9}")

best_ratio = 0
best_d_ratio = 0
for d in np.linspace(0.001, 0.48, 200):
    a1 = ab - d/2
    a2 = ab + d/2
    if a1 < 0.01:
        continue
    C = build_cov_analytical([a1, a2])
    mi1 = mi_from_cov(C, [0], [1])
    mi2 = mi_from_cov(C, [0], [2])
    mi_j = mi_from_cov(C, [0], [1, 2])
    mi_sum = mi1 + mi2
    ratio = mi_j / mi_sum if mi_sum > 0 else 0
    synergy = mi_j - mi_sum  # interaction information (negative = redundancy)
    if ratio > best_ratio:
        best_ratio = ratio
        best_d_ratio = d

# Print selected values
for d in np.linspace(0.001, 0.48, 20):
    a1 = ab - d/2
    a2 = ab + d/2
    if a1 < 0.01:
        continue
    C = build_cov_analytical([a1, a2])
    mi1 = mi_from_cov(C, [0], [1])
    mi2 = mi_from_cov(C, [0], [2])
    mi_j = mi_from_cov(C, [0], [1, 2])
    mi_sum = mi1 + mi2
    ratio = mi_j / mi_sum if mi_sum > 0 else 0
    synergy = mi_j - mi_sum
    print(f"{d:6.3f} {mi_j:9.4f} {mi_sum:9.4f} {ratio:7.4f} {synergy:9.4f}")

print(f"\nMax non-redundancy ratio: {best_ratio:.4f} at d = {best_d_ratio:.4f}")
print(f"d/alpha = {best_d_ratio/ab:.4f}")

# ============================================================
print("\n" + "=" * 65)
print("EXPERIMENT 6: Correlation structure between agents")
print("=" * 65)

print(f"\n{'d':>6} {'rho(y1,y2)':>11} {'rho_1':>7} {'rho_2':>7}")
for d in np.linspace(0.01, 0.48, 20):
    a1 = ab - d/2
    a2 = ab + d/2
    C = build_cov_analytical([a1, a2])
    # Correlation between y1 and y2
    r12 = C[1,2] / np.sqrt(C[1,1] * C[2,2])
    rho1 = a1 * myopic_weight(a1)
    rho2 = a2 * myopic_weight(a2)
    print(f"{d:6.3f} {r12:11.6f} {rho1:7.4f} {rho2:7.4f}")

# ============================================================
print("\n" + "=" * 65)
print("EXPERIMENT 7: Information-theoretic decontamination capacity")
print("=" * 65)

# For a single agent: contamination = rho*y(t-1), which carries MI about s
# through the shared history. The "contamination information" is:
# I(s(t); rho*y(t-1)) = I(s(t); y(t-1)) since y(t-1) depends on s(t-1),
# and s(t) is independent of s(t-1). So I(s(t); rho*y(t-1)) = 0!
# The contamination carries NO information about the CURRENT signal.
# But it adds variance, reducing the SNR.

print(f"\nSNR analysis: how contamination degrades signal-to-noise")
print(f"{'alpha':>6} {'w':>7} {'Var(y)':>8} {'SNR':>8} {'SNR_dB':>8} {'I(s;y)':>8}")
for alpha in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
    w = myopic_weight(alpha)
    rho = alpha * w
    var_y = 1.0 / (1 - rho**2) if rho < 1 else float('inf')
    # SNR = Var(signal component in y) / Var(noise component in y)
    # y = s + rho*y(-1). Signal power = 1. Noise power = rho^2 * Var(y)
    noise_var = rho**2 * var_y
    snr = 1.0 / noise_var if noise_var > 0 else float('inf')
    snr_db = 10 * np.log10(snr) if snr > 0 and snr < float('inf') else float('inf')
    mi = -0.5 * np.log(1 - w) if w < 1 else float('inf')
    print(f"{alpha:6.1f} {w:7.4f} {var_y:8.3f} {snr:8.3f} {snr_db:8.2f} {mi:8.4f}")

# ============================================================
print("\n" + "=" * 65)
print("EXPERIMENT 8: Two-agent decontamination - the REAL question")
print("=" * 65)

# The actual question: given two agents, how much more information about s
# can we extract compared to a SINGLE agent at the SAME total SNR?
# Agent 1 at alpha1, Agent 2 at alpha2.
# The advantage comes from the fact that their contaminations are independent
# (each y_i(t-1) is different) but their signal is shared.

# For two agents with the same alpha but INDEPENDENT noise added:
# y_i(t) = s(t) + alpha*w*y_i(t-1) + sigma_n * n_i(t)
# Now they see the same signal but with different total observations.

print("\nModel: y_i(t) = s(t) + alpha*w*y_i(t-1) + sigma_n * n_i(t)")
print("Independent observation noise sigma_n creates genuine diversity")

for alpha in [0.3, 0.5, 0.7, 1.0]:
    w = myopic_weight(alpha)
    rho = alpha * w
    print(f"\nalpha = {alpha}, w = {w:.4f}, rho = {rho:.4f}")
    print(f"  {'sigma_n':>8} {'I(s;y1)':>9} {'I(s;y1,y2)':>11} {'gain':>8} {'ratio':>7}")

    for sigma_n in [0.01, 0.1, 0.3, 0.5, 1.0]:
        # With independent noise: Var(y_i) = (1 + sigma_n^2) / (1 - rho^2)
        # Cov(s, y_i) = 1
        # Cov(y_i, y_j) = 1 / (1 - rho^2)  [noise is independent]
        var_y = (1 + sigma_n**2) / (1 - rho**2)
        cov_sy = 1.0
        cov_yy = 1.0 / (1 - rho**2)  # Only shared signal contributes

        # Build 3x3 covariance: (s, y1, y2)
        C = np.array([
            [1.0, cov_sy, cov_sy],
            [cov_sy, var_y, cov_yy],
            [cov_sy, cov_yy, var_y]
        ])

        mi1 = mi_from_cov(C, [0], [1])
        mi_j = mi_from_cov(C, [0], [1, 2])
        gain = mi_j - mi1
        ratio = mi_j / mi1

        print(f"  {sigma_n:8.2f} {mi1:9.4f} {mi_j:11.4f} {gain:8.4f} {ratio:7.4f}")

# ============================================================
print("\n" + "=" * 65)
print("EXPERIMENT 9: N-agent saturation with observation noise")
print("=" * 65)

alpha = 0.7
sigma_n = 0.3
w = myopic_weight(alpha)
rho = alpha * w

print(f"\nalpha = {alpha}, sigma_n = {sigma_n}")
print(f"{'N':>4} {'I(s; all y)':>12} {'marginal':>10} {'ratio to N=1':>13}")

mi_1 = None
for N in [1, 2, 3, 5, 7, 10, 15, 20, 30, 50]:
    var_y = (1 + sigma_n**2) / (1 - rho**2)
    cov_yy = 1.0 / (1 - rho**2)

    C = np.zeros((N+1, N+1))
    C[0, 0] = 1.0
    for i in range(N):
        C[0, i+1] = 1.0
        C[i+1, 0] = 1.0
        C[i+1, i+1] = var_y
        for j in range(i+1, N):
            C[i+1, j+1] = cov_yy
            C[j+1, i+1] = cov_yy

    mi = mi_from_cov(C, [0], list(range(1, N+1)))
    if mi_1 is None:
        mi_1 = mi
    print(f"{N:4d} {mi:12.4f} {mi - (prev_mi if N > 1 else 0):10.4f} {mi/mi_1:13.4f}")
    prev_mi = mi

# What's the theoretical limit?
# With N -> inf: averaging y_i eliminates noise, gives y_bar -> s + contamination mean
# Var(y_bar) -> cov_yy (common part), and Cov(s, y_bar) = 1
# I(s; y_bar) = -0.5 * log(1 - 1/cov_yy) = -0.5 * log(1 - (1-rho^2))
#             = -0.5 * log(rho^2) = -log(rho)
mi_inf = -np.log(rho) if rho > 0 else float('inf')
print(f"\nTheoretical limit (N->inf): I = -log(rho) = {mi_inf:.4f} nats")
print(f"This equals I(s; y) at alpha=0 with added memory: {mi_inf:.4f}")
print(f"Ratio limit/single = {mi_inf/mi_1:.4f}")

print("\n" + "=" * 65)
print("SUMMARY")
print("=" * 65)
print(f"""
KEY FINDINGS:

1. IDENTICAL AGENTS ARE USELESS: Two agents with the same alpha produce
   identical observations (y1 = y2 exactly). The covariance matrix is
   singular. Zero additional information.

2. THE JOINT MI IS MONOTONE IN d: I(s; y1, y2) increases monotonically
   with perspective difference d, because the lower-alpha agent captures
   more signal. The "optimal d" is always maximal.

3. THE REAL DIVERSITY COMES FROM NOISE: When agents have independent
   observation noise (different measurement errors, different contexts),
   they provide genuine parallax even at the same alpha level.

4. WITH OBSERVATION NOISE, MI SATURATES: For N agents with alpha={alpha},
   sigma_n={sigma_n}, MI saturates. The theoretical limit is
   I = -log(rho) = {mi_inf:.4f} nats. The contamination sets an
   information ceiling that no number of agents can exceed.

5. THE CEILING IS SET BY CONTAMINATION: The information ceiling
   -log(alpha*w(alpha)) depends only on the self-referential
   contamination parameter. At alpha=1: ceiling = -log(1/phi)
   = log(phi) = {np.log(PHI):.4f} nats = {np.log(PHI)/np.log(2):.4f} bits.

6. GOLDEN RATIO IN THE CEILING: The per-agent MI at alpha=1 is
   I(s;y) = -0.5*log(1-1/phi) = {-0.5*np.log(1-1/PHI):.4f} nats.
   The multi-agent ceiling is log(phi) = {np.log(PHI):.4f} nats.
   Ratio: ceiling/single = {np.log(PHI) / (-0.5*np.log(1-1/PHI)):.4f}.
""")

print("=" * 65)
print("DONE")
print("=" * 65)
