# Damped Meta-Optimization: A Teenager Pokes at the Math

*Date: 2026-02-12*
*Script: `python/experiments/damped_teen.py`*

---

## What I Was Testing

So the deal is: a self-referential system "hears its own echo" and lands at w = 1/phi = 0.618 (the "myopic" answer). The REAL best answer is w = 0.525 (system-aware). There's a meta-optimizer that tries to correct toward 0.525, but it DIVERGES when the echo is too strong (alpha >= 0.7). The researchers said: "what if you only correct partway?" -- use a damping factor beta. Theory predicts beta < 2/(phi+2) = 0.553 keeps things stable.

Simple enough. I swept beta from 0.1 to 1.0 at five echo strengths (alpha = 0.3, 0.5, 0.7, 0.9, 1.0) and watched what happened.

## What Actually Happened

OK so three things blew my mind.

### Thing 1: Beta barely matters (until it kills you)

At each alpha, the system converges to the SAME fixed point no matter what beta you use. beta=0.1? Same answer. beta=0.5? Same answer. beta=0.55? Same answer. The damping factor doesn't change WHERE you end up, it just changes WHETHER you get there. Below some critical beta, you always converge to the same place. Above it, boom, divergence.

Wait, WHAT? I expected a smooth tradeoff. Nope. The fixed point is the fixed point. Damping just determines if you can reach it without blowing up.

This actually makes sense: if w_new = (1-beta)*w + beta*f(w) converges to w*, then w* = (1-beta)*w* + beta*f(w*), which simplifies to w* = f(w*). The fixed point of the damped iteration IS the fixed point of the original. Beta doesn't change the destination. It just changes the ride.

### Thing 2: Alpha pushes you toward 0.525 automatically

Here's the fixed point at each alpha:

| alpha | fixed point | gap to 0.525 |
|-------|------------|---------------|
| 0.3   | 0.86876    | 0.344         |
| 0.5   | 0.74301    | 0.218         |
| 0.7   | 0.63944    | 0.114         |
| 0.9   | 0.55851    | 0.034         |
| 1.0   | 0.52489    | 0.00011       |

The stronger the echo, the CLOSER the fixed point is to the system-aware optimum! At alpha=1.0, the meta-optimizer's fixed point is 0.52489 -- within 0.01% of 0.525. The recurrence w -> (1-alpha^2 w^2)^2 naturally lands closer to the "correct" answer when alpha is high. The divergence at alpha >= 0.7 wasn't because the answer is wrong -- it's because the PATH there is unstable. The damping fixes the path, and the answer was good all along.

This is like... the system already "knows" the right answer at high alpha, it just can't get there without tripping over itself. Damping is just saying "take smaller steps, dude."

### Thing 3: Beta = 1/phi works EVERYWHERE

OK so this was my dumb idea. I thought "1/phi keeps showing up, what if the damping factor is also 1/phi?" Note: 1/phi = 0.618, which is ABOVE the theoretical threshold of 0.553.

It converged at every single alpha. Every one. Including alpha=0.9 and alpha=1.0 where the undamped version should be diverging.

| alpha | beta=1/phi result |
|-------|-------------------|
| 0.3   | 0.86876 (converged) |
| 0.5   | 0.74301 (converged) |
| 0.7   | 0.63944 (converged) |
| 0.9   | 0.55851 (converged) |
| 1.0   | 0.52489 (converged) |

The theoretical bound says beta < 0.553. But 1/phi = 0.618 > 0.553. It "shouldn't" work. But it does. The bound is derived from linearization at the fixed point -- maybe the actual nonlinear basin of attraction is wider? Or maybe 1/phi is special as a damping factor for a system whose fixed points are already governed by phi?

I don't have the math to prove why. But it's suspicious. The golden ratio is everywhere in this system.

## The Big Takeaway

The question was: "does partial correction fix divergence?" YES. Unambiguously yes. But the interesting part isn't that -- it's that the correction doesn't change the answer, only the stability of the path. And the answer was already really good at high alpha. At alpha=1.0, the fixed point of the meta-optimizer is essentially the system-aware optimum (0.525).

The divergence at alpha >= 0.7 was never about the math "getting the wrong answer." It was a TRANSPORTATION problem: the system knew where to go but kept overshooting. Damping solves transportation, not destination.

And yeah, beta = 1/phi. I can't explain it yet. But I'm going to keep poking at it.

## Numbers for the Record

- Divergence boundary at alpha=1.0: somewhere between beta=0.75 and beta=0.80
- Divergence boundary at alpha=0.9: somewhere between beta=0.85 and beta=0.90
- At alpha=0.7: even beta=1.0 barely changes things (0.63944 -> 0.60936)
- Theoretical threshold: beta_crit = 2/(phi+2) = 0.5528
- Golden-ratio damping: beta = 1/phi = 0.6180 -- above threshold, still works
- Best result: alpha=1.0, any beta <= 0.75 gives w = 0.52489 (gap = 0.00011 from 0.525)
