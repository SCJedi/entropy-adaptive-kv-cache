# Damped Meta-Optimizer: A Trader's Lab Notebook

**Author:** Hobbyist trader / algorithmic developer
**Date:** 2026-02-12
**Status:** Complete -- ran the experiment, all three strategies tested at alpha=1.0

---

## The Setup

I trade for a living (well, on the side). I have lived the exact problem this meta-optimizer has. You build a signal. The signal says buy. You buy. Your buy moves the price. Now the signal is partly reading your own order flow. You know this. So you scale back. But how much?

I read the Feynman piece and immediately recognized the see-saw. At alpha=1.0 the naive meta-optimizer goes: 0.618 -> 0.382 -> 0.729 -> 0.219 -> 0.906 -> 0.032. That is a blown-up trading account. That is what happens when your algo says "I'm moving the market too much" and cuts size to zero, then says "wait, now I have no impact" and goes full size, then panics again. I have literally watched this happen on a live account at 2am.

Marcus derived the critical damping bound: beta < 2/(phi + 2) = 0.553. That is position sizing. You never go full size on a self-referential signal. You cap your step at 55% of what the raw signal tells you. Makes perfect sense.

But the question was: does it actually work? And which damping strategy is best? I tried three.

---

## What Actually Happened

### Strategy 1: Fixed Beta (Position Size Cap)

Simplest possible approach. Instead of w_new = f(w), use w_new = (1-beta)*w + beta*f(w). Just blend the old position with what the signal says. Swept beta from 0.1 to 1.0.

The results knocked me over.

| beta | Converges? | Iterations | Final w |
|------|-----------|------------|---------|
| 0.1  | YES       | 36         | 0.5249  |
| 0.2  | YES       | 17         | 0.5249  |
| 0.3  | YES       | 9          | 0.5249  |
| **0.4** | **YES** | **4**      | **0.5249** |
| 0.5  | YES       | 10         | 0.5249  |
| 0.55 | YES       | 14         | 0.5249  |
| 0.6  | YES       | 19         | 0.5249  |
| 0.7  | YES       | 46         | 0.5249  |
| 0.8  | NO        | 500        | 0.6217  |
| 1.0  | NO        | 500        | 0.9990  |

Every single beta from 0.1 to 0.7 converges to the system-aware optimum w=0.525, closing 100% of the MSE gap. The sweet spot is beta=0.4 -- four iterations. Four. Not "approximately two" like the cross-feed round claimed, but four with damping, starting from the myopic attractor.

The divergence boundary is between 0.7 and 0.8, which is above the Marcus bound of 0.553. Marcus was conservative. The actual stability boundary is wider than the linear analysis predicts. (This happens in trading too -- your worst-case risk models are usually more conservative than reality, because they linearize around the worst point.)

Beta=0.4 being optimal is suspicious. It is close to 1/phi^2 = 0.382. Might be coincidence, might be the geometry again. I did not dig into this.

### Strategy 2: Adaptive Beta (Cut Size on Whipsaw)

This is how I actually trade. Start with a reasonable position size (beta=0.5). Every time the correction flips sign -- which means you overshot and are now correcting the other way -- cut beta by 20%. Like reducing your position size after a whipsaw.

Result: converges in 6 iterations, final beta=0.32. The trajectory is beautiful:

```
0.618 -> 0.500 -> 0.525 -> 0.525 (converged)
```

It overshoots once (0.618 to 0.500), detects the sign flip on the next correction, cuts beta from 0.5 to 0.4, and on the next step it is already within tolerance. The sign-flip detection catches the oscillation before it develops. This is the strategy I would actually deploy in production because it does not require knowing the Marcus bound in advance. It self-tunes.

### Strategy 3: Momentum (Smoothed Signal)

Instead of using the raw correction, take an exponential moving average. This is standard in machine learning (SGD with momentum) and in trading (EMA-smoothed signals). Used a base learning rate of 0.4 and swept the momentum parameter gamma.

| gamma | Converges? | Iterations |
|-------|-----------|------------|
| 0.3   | YES       | 19         |
| 0.5   | YES       | 28         |
| 0.7   | YES       | 54         |
| 0.9   | YES       | 136        |

All converge. All hit w=0.525. But they are all slower than fixed beta=0.4, and much slower than adaptive. The momentum smoothing works but adds lag, just like an EMA on a trading signal adds lag. You avoid whipsaws but you also respond slower to the actual correction. For this problem, where the target is a fixed point, the lag is pure cost with no benefit.

---

## The Punchline

All three strategies reach w=0.525 at alpha=1.0. The system-aware optimum is not just theoretically optimal -- it is practically reachable with trivially simple damping. The entire gap (15.6% MSE) is closed. Every penny of the "stability tax" can be recovered.

The ranking:

1. **Adaptive beta: 6 iterations.** Self-tuning, no parameters to set, production-ready.
2. **Fixed beta=0.4: 4 iterations.** Fastest but you need to know the right beta.
3. **Momentum: 19-136 iterations.** Works but overkill. Solving the wrong problem (noisy gradients) for this problem (deterministic oscillation).

---

## Trading Analogies (For My Own Notes)

- **Fixed beta** = hard position limit. Works if you know your market impact. Fragile if impact changes.
- **Adaptive beta** = dynamic position sizing based on realized slippage. Robust, self-correcting.
- **Momentum** = smoothed signal. Kills noise but also kills speed. Good for noisy environments, wasteful for deterministic ones.

The meta-optimizer divergence is exactly market impact feedback: your trade moves the price, you see the moved price, you trade more. The fix is the same in both domains: scale back your response to your own signal. The mathematics says scale back to about 40% (beta=0.4) for optimal speed, or start at 50% and let the whipsaws tell you when to cut further.

---

## Files

- **Script:** `python/experiments/damped_hobbyist.py` (98 lines, <1s runtime)
- **All results verified:** every converging run hits w=0.5249 and MSE=0.3305
