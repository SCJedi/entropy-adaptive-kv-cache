# What We Missed: Non-Stationary Alpha

*Sarah Chen, ML Systems -- The Blind Spot Probe*

---

## The Gap in Our Evidence

Twenty-one experiments. Every single one uses **fixed alpha**. The contamination level is set at the start of the run and stays there. We sweep alpha across experiments, sure. We test alpha=0.1 and alpha=1.0 and everything between. But we never let alpha *move*.

This matters because no real ML system has stationary contamination. In RLHF, the fraction of model-generated data in the reward model's training pool grows with each iteration -- alpha drifts upward as the pipeline matures. In web-scraped training data, the synthetic fraction increases year over year as more AI-generated content floods the internet. In recommendation systems, the feedback loop tightens as user behavior adapts to recommendations. Alpha is not a parameter you set. It is a quantity that evolves while your system runs.

I ran five sub-experiments to characterize what happens when alpha drifts. The results contain a genuine surprise that undermines one of our headline claims.

---

## What I Found

### 1. The Monocular System Tracks Remarkably Well

This was not the result I expected. A simple single-channel SGD agent, faced with alpha drifting slowly from 0.1 to 1.0, maintains a mean tracking error of just 0.049 -- the weight stays within 5% of the theoretical optimum w*(alpha) at every point along the drift. The self-consistency equation w^2 + w - 1 = 0 does not just describe a fixed point; it describes a **moving attractor** that SGD tracks in near real-time.

Even at medium drift rates (alpha traversing 0.1 to 1.0 in 10K steps), the tracking error is only 0.094. The system does not catastrophically fail under non-stationary contamination. It adapts.

The critical drift rate -- where tracking genuinely breaks down -- is approximately 0.0018 per step (alpha traversing the full range in 500 steps). Below this rate, SGD tracks. Above it, the system cannot adapt fast enough and the error spikes to 0.137. For most real-world systems where alpha changes over thousands or millions of training steps, this suggests tracking is not the bottleneck.

### 2. MVSU Is Worse Under Non-Stationary Alpha

Here is the surprise, and I want to be honest about it: **the MVSU loses to monocular at every drift rate tested.** Not by a little. By 39-49%.

At slow drift: monocular tracking error 0.049, MVSU 0.073. At instant transition: monocular 0.105, MVSU 0.145. The MVSU's inhibitory cross-connections, which provide decontamination at fixed alpha, become a liability when alpha moves. The cross-weight w_cross needs time to adapt to the new contamination level, and during that adaptation period it is actively applying the wrong correction.

This makes mechanical sense. The MVSU has three parameters to adapt (w_a, w_b, w_cross) where the monocular has one (w). More parameters means slower adaptation to regime changes. The inhibitory coupling that provides stability at equilibrium creates inertia during transitions. The MVSU is optimized for the stationary case -- the case we tested -- and pays for that optimization when stationarity breaks.

**This does not invalidate the MVSU.** At fixed alpha, the MVSU still wins decisively (45-54% improvement on real tasks, as demonstrated in Experiments 15-16 and 21). The finding is that the MVSU's advantage is *conditional on approximate stationarity*. When alpha is stable or slowly drifting, use MVSU. When alpha is changing rapidly, the monocular system's simplicity is an advantage.

### 3. No Hysteresis -- The Good News

The system does not carry permanent scars from past contamination. When alpha drifts up and then back down (0.1 -> 1.0 -> 0.1), the weight recovers to within 0.038 of its original value. There is a slight lag (recovery gap), but no permanent damage. Rising alpha produces slightly more tracking error than falling alpha (+4.7% asymmetry), but the difference is minor.

The practical implication: if your system goes through a period of high contamination and then you clean up the data pipeline, the optimizer will recover. The self-consistency attractor is not a trap; it adjusts to current conditions.

### 4. w_cross Tracks Alpha (Correlation -0.84)

During oscillating alpha, the learned cross-weight w_cross correlates strongly with the contamination level (r = -0.84). When alpha rises, w_cross becomes more negative (stronger inhibition). When alpha falls, w_cross relaxes toward zero. The MVSU's cross-connections are a real-time contamination barometer.

This is actually useful even if the MVSU's tracking is worse. The magnitude of w_cross tells you how contaminated your system currently is, without needing to measure alpha directly. In a production system where alpha is hard to observe, monitoring w_cross gives you a live contamination estimate for free.

The w_cross values ranged from -0.17 (low alpha, early in slow drift) to -0.33 (high alpha, late in run). They stayed consistently negative -- no sign flip to positive was observed. The contamination topology (independent between arch-diverse channels) does not change when alpha drifts, only the magnitude changes. This is consistent with Feynman's finding that positive w_cross requires shared contamination (same-alpha agents), which our architecture-diverse MVSU does not produce.

### 5. A Critical Drift Rate Exists

Tracking fails at approximately 0.0018 alpha-units per step. For a system where alpha goes from 0.1 to 1.0:
- Over 50K steps: fine (tracking error 0.049)
- Over 10K steps: fine (tracking error 0.052)
- Over 2K steps: fine (tracking error 0.072)
- Over 1K steps: borderline (tracking error 0.096)
- Over 500 steps: fails (tracking error 0.137)

The failure threshold corresponds roughly to the SGD learning rate. When alpha changes faster than the optimizer can respond (drift rate > effective lr), the system cannot track. In real RLHF systems with typical learning rates around 1e-5 to 1e-3, this means alpha can drift substantially within a single training run without tracking failure -- but a sudden pipeline change (e.g., switching from human to fully synthetic data in one step) will cause transient mis-adaptation.

---

## What This Means for Practitioners

**The ML Practitioner Guide (Section 3, Fix 2) needs a caveat.** We recommend dual models with cross-subtraction as the primary fix for alpha > 0.6. That recommendation holds when alpha is approximately stable. But if your alpha is rapidly changing -- if you are ramping up synthetic data fraction, or your feedback loop is tightening quickly -- the simpler monocular over-relaxation (Fix 1) may actually track better during the transition.

The practical recipe should be:

1. **During pipeline changes** (alpha shifting quickly): Use Fix 1 (over-relaxation with swept omega). Simpler systems adapt faster.
2. **At steady state** (alpha approximately fixed): Switch to Fix 2 (MVSU dual models). The equilibrium decontamination advantage dominates.
3. **Monitor w_cross** as a live contamination signal. If it is changing rapidly, you are in the non-stationary regime and should rely on Fix 1.

This is actually a pattern that recurs in engineering: robust simple systems beat optimal complex systems during regime transitions, then lose at equilibrium. The MVSU is the optimal steady-state architecture. The monocular over-relaxation is the robust transition architecture. A production system should know which regime it is in.

---

## What This Probe Changes About the Theory

The self-consistency equation kw^2 + w - 1 = 0 is not just a fixed point -- it is a *continuously tracked moving attractor*. SGD follows it in real time as alpha drifts, with a tracking lag proportional to (drift rate / learning rate). This is a stronger result than "the system converges to 1/phi at alpha=1." The attractor is not a destination; it is a moving equilibrium that the system rides.

The MVSU's advantage is conditional on approximate stationarity. This constrains the practical recommendation: use MVSU for steady-state decontamination, not for rapid regime adaptation. The w_cross signal (-0.84 correlation with alpha) is a free contamination diagnostic even when the MVSU is not the best architecture for the current regime.

We tested 21 experiments at fixed alpha and found the MVSU wins. We needed this 22nd experiment at drifting alpha to find where it loses. The blind spot was stationarity itself.

---

*Experiment: `python/experiments/sarah_whats_missing.py` -- 50K steps, 5 seeds, 5 drift patterns. Runtime: ~45 seconds.*
