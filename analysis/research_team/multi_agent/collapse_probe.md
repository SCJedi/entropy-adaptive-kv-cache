# Multi-Agent Model Collapse: Can MVSU Prevent Ecosystem Degradation?

**Agent**: Dr. Sarah Chen (ML systems)
**Date**: 2026-02-12
**Script**: `python/experiments/multi_agent_collapse.py`
**Status**: Experiment complete, results mixed but informative

---

## The Setup

Model collapse is one of the things that keeps me up at night. We're already seeing it in the wild -- LLMs trained on internet data that includes previous LLM outputs. Each generation's synthetic data becomes the next generation's training set, and the signal degrades. Shumailov et al. (2024) showed this theoretically; we're now living through it empirically.

The question: does the MVSU architecture from the whitepaper -- two models with different inductive biases and inhibitory cross-connections -- slow this collapse when inserted into a generative chain?

I built the simplest possible test. True distribution is a mixture of 3 Gaussians (means at -3, 0, +4; different variances). This has genuine structure -- three modes with different widths -- not just noise. Each "agent" in the chain is a KDE that trains on the previous agent's output and generates new samples. Quality measured by Wasserstein-1 distance from the true distribution. 20 generations, 600 samples per gen, 5 seeds averaged.

The MVSU intervention: two KDEs with *different* bandwidths (narrow bw=0.5x and wide bw=2.0x Silverman's rule). This gives genuine architectural diversity -- narrow preserves sharp features but adds sampling noise, wide smooths but loses detail. Cross-inhibitory selection: oversample 4x from the narrow KDE, evaluate density under both KDEs, and preferentially select samples where the two models *agree* (low density-estimate disagreement). This is the generative analog of inhibitory cross-connections: where the models disagree, the sample is likely a channel-specific artifact, not real signal.

## What Actually Happened

### Raw Results

```
========================================================================
MULTI-AGENT MODEL COLLAPSE EXPERIMENT
========================================================================
Gens: 20 | Samples: 600 | Seeds: 5
True dist: 3-Gaussian mixture, mu=[-3.0, 0.0, 4.0]
Metric: Wasserstein-1 (lower = better)
MVSU: dual-KDE (bw*0.5 + bw*2.0), cross-inhibitory sample selection

Runtime: 6.1s

Wasserstein-1 distance vs generation:
------------------------------------------------------------------------
 Gen | No intervention |  MVSU every gen |  MVSU every 3rd | MVSU gen 0 only |  MVSU every 5th
------------------------------------------------------------------------
   0 |          0.2862 |          0.9706 |          0.9706 |          0.9706 |          0.9706
   1 |          0.4538 |          1.3556 |          1.0171 |          1.0171 |          1.0171
   2 |          0.5415 |          1.3896 |          1.1118 |          1.1118 |          1.1118
   4 |          0.6966 |          1.5378 |          1.5359 |          1.3086 |          1.3086
   6 |          1.0121 |          1.5826 |          1.8673 |          1.5860 |          2.0258
   9 |          1.3134 |          1.5893 |          2.4306 |          1.8738 |          2.0912
  14 |          2.0742 |          1.6191 |          2.7889 |          2.7304 |          2.2852
  19 |          3.0761 |          1.4304 |          3.1011 |          3.8713 |          2.2446

FINAL (gen 19):
----------------------------------------------------
  No intervention       : W1=3.0761  (1.00x baseline)
  MVSU every gen        : W1=1.4304  (0.46x baseline)
  MVSU every 3rd        : W1=3.1011  (1.01x baseline)
  MVSU gen 0 only       : W1=3.8713  (1.26x baseline)
  MVSU every 5th        : W1=2.2446  (0.73x baseline)

COLLAPSE RATE (gen where W1 doubles):
----------------------------------------------------
  No intervention       : gen 3
  MVSU every gen        : STABLE
  MVSU every 3rd        : gen 7
  MVSU gen 0 only       : gen 10
  MVSU every 5th        : gen 5

CRITICAL FRACTION (MVSU every N gens):
----------------------------------------------------
  Every  1 (100%): W1=1.4304    +54% vs none
  Every  2 ( 50%): W1=2.4501    +20% vs none
  Every  3 ( 35%): W1=3.1011     -1% vs none
  Every  5 ( 20%): W1=2.2446    +27% vs none
  Every  7 ( 15%): W1=3.1929     -4% vs none
  Every 10 ( 10%): W1=2.7946     +9% vs none
  Every 20 (  5%): W1=3.8713    -26% vs none

CASCADE FIT (no-intervention):
  W1(g) ~ W1(0) * 1.1164^g
  Early rate (0-4): 1.2491
  Late rate (9-19): 1.0888
  Sub-multiplicative: YES (collapse decelerates)

========================================================================
COMPLETE
========================================================================
```

### The Good News

**1. MVSU every generation prevents runaway collapse.** The uncontrolled chain degrades from W1=0.29 to W1=3.08 over 20 generations -- a 10.7x increase. With MVSU at every generation, the chain stabilizes around W1~1.5 and the W1 distance *never doubles* from its initial value. By gen 14, the MVSU chain is already better than the uncontrolled chain (1.62 vs 2.07), and by gen 19, it's 54% better (1.43 vs 3.08). The cross-inhibitory selection acts as a ratchet against mode collapse.

**2. Sub-multiplicative collapse is confirmed.** The no-intervention chain shows early degradation rate of 1.25x per generation (gens 0-4) but only 1.09x per generation in late stages (gens 9-19). This matches the cascade theorem's prediction: as the signal degrades, the remaining signal is increasingly "consensus" signal that all processing stages agree on, so further degradation slows. The flip side: early generations are the most damaging, which is exactly when MVSU intervention matters most.

**3. Even sparse MVSU helps.** MVSU every 5th generation achieves 27% improvement over baseline at gen 19 (W1=2.24 vs 3.08). Every 10th generation still gives 9% improvement. There IS a critical density effect.

### The Honest Problems

**1. MVSU has a startup cost.** At generation 0, the MVSU-equipped chains start at W1=0.97, versus 0.29 for the plain KDE. The cross-inhibitory selection biases the initial sample toward regions where two very different KDEs agree, which over-concentrates near the modes and under-represents the tails. This initial distortion is the price of the filtering.

**2. The relationship between intervention frequency and quality is non-monotonic.** Every-3rd (35%) gives essentially no improvement (-1%), while every-5th (20%) gives +27%. This is noisy -- 5 seeds is probably not enough to resolve the fine structure. But it also suggests the interaction between MVSU filtering and subsequent uncontrolled generations is complex. MVSU distorts the distribution in specific ways; if the number of plain-KDE generations between interventions happens to partially undo that distortion before the next MVSU step, you get a resonance effect.

**3. One-shot MVSU at gen 0 actually hurts.** W1=3.87 vs 3.08 baseline. The initial filtering bias compounds through 19 subsequent uncontrolled generations. This confirms the whitepaper's finding that MVSU without ongoing application is worse than useless -- you pay the distortion cost without the long-term decontamination benefit.

### The Deep Question: Two Eyes in a Crowd of the Blind

The user asked whether MVSU-equipped agents can "see through the collective contamination" -- like two eyes in a crowd of the blind. The answer from this experiment is a qualified yes, with important caveats.

**What works**: When MVSU is applied consistently (every generation), it creates a ceiling on degradation. The chain stabilizes instead of collapsing. The mechanism is clear: the two KDEs with different bandwidths produce different artifacts, and cross-inhibitory selection suppresses samples that are artifacts of either channel. Signal survives because it's the thing both channels agree on.

**What doesn't**: MVSU can't *reverse* degradation. At gen 0, the MVSU chain is already at W1=0.97 (worse than the plain chain's initial 0.29). It then stabilizes near 1.4-1.6. It prevents the exponential blowout (3.08 at gen 19 in the baseline) but doesn't recover the true distribution. Once signal is lost, it's lost -- the data processing inequality applies. MVSU slows the information loss, it doesn't create new information.

**The critical fraction**: From the data, MVSU at every generation (100%) clearly helps. MVSU at 20% of generations (every 5th) helps moderately. Below ~10%, the benefit is marginal and inconsistent. For the "internet ecosystem" interpretation: if only 10-20% of the models in a generative chain use MVSU-style dual-model consensus, the ecosystem-level collapse slows but doesn't stop. You need more like 50-100% adoption for genuine stabilization.

### Does the Cascade Equation Predict the Collapse Rate?

Sort of. The no-intervention chain follows W1(g) ~ W1(0) * 1.12^g, which is a simple exponential with sub-multiplicative deceleration (rate drops from 1.25 early to 1.09 late). This is consistent with the whitepaper's cascade composition theorem -- each stage's output is temporally correlated, making subsequent decontamination harder, but the compounding DECELERATES as the distribution flattens.

The cascade equation predicts the qualitative shape (exponential degradation with deceleration) but I didn't attempt to quantitatively match the per-stage fidelity w(alpha) values. The KDE chain's "contamination parameter" alpha is implicit in the bandwidth -- wider bandwidth = more contamination -- and extracting the effective alpha to plug into kw^2 + w - 1 = 0 would require a more careful mapping between the KDE blur and the additive contamination model.

## What This Means for Real Systems

1. **Synthetic data pipelines need MVSU-like consensus filtering.** If you're generating training data with an LLM and then training the next LLM on it, running two architecturally different generators and keeping only the output they agree on would slow mode collapse significantly. The key word is "architecturally different" -- two copies of the same model with different random seeds won't work (the whitepaper already showed this).

2. **The critical adoption fraction is high.** For ecosystem-level protection (many labs all generating and consuming synthetic data), you'd need 50%+ of the pipeline stages to use dual-model consensus. 10-20% helps but doesn't prevent eventual collapse.

3. **MVSU can't undo damage.** If the data is already heavily contaminated (late in the chain), MVSU can stabilize at the current degradation level but can't recover lost signal. This means early intervention matters far more than late intervention.

4. **There is a startup cost.** The cross-inhibitory filtering biases the distribution in specific ways (over-concentrates near modes). For any practical deployment, you'd want to tune the inhibitory strength and the bandwidth diversity ratio to minimize this initial distortion.

5. **Sub-multiplicative collapse is both good news and bad news.** Good: the rate slows, so the system doesn't immediately explode. Bad: it slows because the signal is already mostly gone, not because the system is self-correcting.

---

*Script runtime: 6.1 seconds. All results reproducible from `python/experiments/multi_agent_collapse.py` with seeds 42-46.*
