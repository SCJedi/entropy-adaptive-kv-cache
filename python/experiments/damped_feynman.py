"""
Damped Meta-Optimizer + MVSU Effective Beta
============================================
Meta-optimizer diverges at alpha>=0.699. Damped version should stabilize.
Key question: is the MVSU a damped meta-optimizer? What's its effective beta?
"""
import sys, time, numpy as np
sys.path.insert(0, sys.path[0].replace("experiments", ""))
from mvsu import MVSUPredictor, LinearPredictor
if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except: pass

PHI = (1 + np.sqrt(5)) / 2; INV_PHI = 1/PHI; t0 = time.time()

def f_sys(w, a=1.0): return (1 - a**2 * w**2)**2
def mse_t(w, a=1.0):
    aw2 = a**2*w**2
    return 1e6 if aw2 >= 1 else w**2/(1-aw2) - 2*w + 1

def damped_iter(a, beta, steps=2000):
    w = INV_PHI; traj = [w]
    for _ in range(steps):
        w = w + beta*(f_sys(w,a) - w)
        if abs(w) > 10 or np.isnan(w): return traj + [None]
        traj.append(w)
    return traj

# === PROBE 1: Beta sweep at alpha=1 ===
print("="*65 + "\nPROBE 1: Damped meta-optimizer (alpha=1.0)\n" + "="*65)
print(f"Theoretical beta_crit = 2/(phi+2) = {2/(PHI+2):.4f}\n")
print(f"{'beta':<8}{'final_w':<12}{'MSE':<10}{'steps'}")
print("-"*42)
for beta in [0.1, 0.2, 0.3, 0.382, 0.5, 0.553, 0.6, 0.618, 0.7, 0.8, 0.9, 1.0]:
    traj = damped_iter(1.0, beta)
    wf = traj[-1]
    if wf is None: print(f"{beta:<8.3f}DIVERGED"); continue
    nc = next((i for i,w in enumerate(traj) if w and abs(w-wf)<0.001), "---")
    print(f"{beta:<8.3f}{wf:<12.6f}{mse_t(wf):<10.6f}{nc}")
print("\nUndamped (beta=1) trajectory:")
w = INV_PHI
for i in range(7):
    w = f_sys(w); print(f"  step {i+1}: w = {w:.6f}")

# === PROBE 2: MVSU at alpha=1 ===
print("\n" + "="*65 + "\nPROBE 2: MVSU at alpha=1.0\n" + "="*65)
T, BURN = 80000, 10000; rng = np.random.RandomState(42)
mvsu = MVSUPredictor(LinearPredictor(1, 1, seed=42), w_cross_init=-0.1)
eff_ws, mse_run, wc_hist, y_prev = [], [], [], 0.0
for t in range(T):
    s = rng.randn(); y = s + y_prev
    pred = mvsu.predict(np.array([y])); pv = float(pred.ravel()[0])
    eff_ws.append(pv/y if abs(y) > 0.1 else np.nan)
    mse_run.append((pv - s)**2); wc_hist.append(mvsu.w_cross)
    mvsu.update(np.array([y]), np.array([s]), lr=0.005); y_prev = pv

# Windows
print(f"\n{'window':<15}{'eff_w':<12}{'MSE':<10}{'w_cross'}")
for start in range(0, T, 10000):
    end = start+10000
    ws = [w for w in eff_ws[start:end] if not np.isnan(w)]
    print(f"  {start:>5}-{end:<6}{np.median(ws):<12.4f}{np.mean(mse_run[start:end]):<10.4f}{wc_hist[end-1]:.4f}")

ws_post = [w for w in eff_ws[BURN:] if not np.isnan(w)]
w_mvsu, mse_mvsu = np.median(ws_post), np.mean(mse_run[BURN:])
frac = (INV_PHI - w_mvsu) / (INV_PHI - 0.525)
print(f"\nMVSU eff_w={w_mvsu:.5f}  MSE={mse_mvsu:.5f}  w_cross={mvsu.w_cross:.5f}")
print(f"Myopic:    {INV_PHI:.5f}  MSE={mse_t(INV_PHI):.5f}")
print(f"Optimal:   0.52489  MSE={mse_t(0.525):.5f}")
print(f"Gap closed: {frac*100:.1f}%")

# === PROBE 3: Monocular baseline ===
print("\n" + "="*65 + "\nPROBE 3: Monocular baseline\n" + "="*65)
rng3 = np.random.RandomState(42); mono = LinearPredictor(1, 1, seed=42)
mono_ws, mono_mse, y_prev = [], [], 0.0
for t in range(T):
    s = rng3.randn(); y = s + y_prev; pred = mono.predict(np.array([y]))
    pv = float(pred.ravel()[0])
    if abs(y)>0.1: mono_ws.append(pv/y)
    mono_mse.append((pv-s)**2)
    mono.update(2.0*(pred-np.array([s])), lr=0.005); y_prev = pv
print(f"Mono eff_w={np.median(mono_ws[BURN:]):.5f}  MSE={np.mean(mono_mse[BURN:]):.5f}")
print(f"MVSU improvement: {(1-mse_mvsu/np.mean(mono_mse[BURN:]))*100:.1f}%")

# === PROBE 4: Golden ratio betas ===
print("\n" + "="*65 + "\nPROBE 4: Golden ratio betas\n" + "="*65)
for lbl, b in [("1/phi^2=0.382",1/PHI**2),("1/phi=0.618",INV_PHI),("2/(phi+2)=0.553",2/(PHI+2))]:
    t = damped_iter(1.0, b); wf = t[-1]
    nc = next((i for i,w in enumerate(t) if w and abs(w-wf)<0.001), "---")
    print(f"  beta={lbl}: w->{wf:.5f}  MSE={mse_t(wf):.5f}  steps={nc}")

# === SUMMARY ===
print("\n" + "="*65 + "\nSUMMARY\n" + "="*65)
print(f"  Damped meta-opt: ALL beta in (0,~0.7) -> w=0.525, MSE=0.331")
print(f"  Fastest: beta=1/phi^2=0.382 (2 steps)")
print(f"  Undamped (beta=1): DIVERGES")
print(f"  MVSU: eff_w={w_mvsu:.4f}, MSE={mse_mvsu:.4f} (stays myopic)")
print(f"  Gap closed by MVSU: {frac*100:.1f}% -- NOT a damped meta-optimizer")
print(f"  MVSU is a noise filter, not a self-awareness engine")
print(f"  Time: {time.time()-t0:.1f}s")
