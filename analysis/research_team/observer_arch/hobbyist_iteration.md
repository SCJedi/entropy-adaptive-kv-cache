# GOLDEN CUBE NET v2: Post-GPU Iteration

**Team:** Weekend Builders Collective
**Date:** 2026-02-17
**Status:** Redesign based on GPU validation data
**Vibe:** Humbled but not defeated. Some of our guesses were *really* good. Some were wrong. Let's build the better thing.

---

## 1. What We Got Right

Let's be honest: we nailed some of this.

**Dropout = 0.382 is the single biggest win in the entire experiment suite.** We said "free improvement, zero tuning cost." GPU says: +4.84 percentage points over the 0.5 default. That's not noise. That's not a rounding error. That's a nearly 5-point jump from changing one number. We put it in our architecture table as row 6 and it turned out to be row 1 in importance. We'll take the W.

**w_cross stays negative. In ALL 32 heads. Across ALL 4 layers.** We initialized at -0.1 and said "the experiments say inhibitory." The GPU didn't just confirm it -- it showed w_cross getting MORE negative with depth. Block 0 averages -0.316, block 3 averages -0.479. Not a single head out of 32 went positive. Our "negative hint" initialization was conservative -- the network wants to go way more negative than -0.1.

**Fixed alpha matches learnable alpha.** We hardcoded alpha = 0.382 and said "the experiments say this ties learnable." GPU confirmed: no benefit to learning it. Free hyperparameter, zero tuning cost. Exactly what we predicted.

**The inverted-U is real everywhere.** CNN overlap, dropout, alpha sweep -- all show the characteristic peak-then-decline. The phi-zone (0.30-0.40) is the right neighborhood in every single experiment. Our architecture was designed around this shape and the shape held up.

**Observer Attention (structured inter-head communication) works.** +4.57% over baseline. We bet on inter-head messaging being important and it is.

---

## 2. What Surprised Us

**FFN = 2.618x alone HURTS.** We had "Hidden dim multiplier: 1.618x" in our hyperparameter table like it was a free win. It's not. Standalone, the reduced FFN drops accuracy by nearly a full point (-0.97%). We thought smaller-but-phi-tuned would just work. It doesn't -- unless you also drop the dropout to 0.382. The *combination* works beautifully (best parameter efficiency at 0.1034 acc/100K params), but the FFN reduction is not a standalone move. This is a genuine surprise. The phi-expansion ratio needs the phi-dropout rate as its partner. They're co-dependent.

**Full OT (Tier 3 dual-channel MVSU) didn't beat simpler Tier 2.** We had a whole stretch goal about running TWO complete GCNs with cross-inhibition. The GPU says: don't bother. Tier 2 Observer Attention (65.60%) beats Tier 3 Full OT (65.36%) while using fewer parameters. The dual-channel mechanism adds complexity without improving accuracy. Our "MVSU-Style Dual Architecture" stretch goal? Dead on arrival.

**Alpha peaks at 0.3, not 0.382.** We hardcoded 0.382 and called it settled science. The GPU alpha sweep shows 0.300 as the actual peak, with 0.382 sitting on the downslope. The difference is 0.0048 in accuracy -- small but consistent. We were in the right neighborhood but we were wrong about the exact center.

**w_cross magnitude increases with depth.** We didn't predict this at all. We initialized every block's cross-weights to the same -0.1 and expected them to stay roughly uniform. Instead, the network learns a depth gradient: -0.316 (block 0) to -0.479 (block 3). Deeper layers want STRONGER inhibition. This is a signal we completely missed in our original design.

**Phi-annealing doesn't help.** We didn't propose this explicitly, but it's related to our "Dynamic Alpha" stretch goal. The GPU says adaptive regularization scheduling provides no benefit at this scale. Another complexity-for-nothing result.

---

## 3. What We'd Change

Based on the evidence, here's what changes in GCN v2.

### Change 1: Initialize w_cross with a depth schedule
Don't use -0.1 everywhere. Use a linear schedule matching the observed gradient:
- Block 0: w_cross_init = -0.25
- Block 1: w_cross_init = -0.30
- Block 2: w_cross_init = -0.35
- Block 3: w_cross_init = -0.45

The network is going to learn this gradient anyway. Let's start it closer to where it wants to end up.

### Change 2: Alpha = 0.30, not 0.382
The GPU data is clear. 0.300 > 0.382 in the alpha sweep. We're builders, not zealots. Use the number that works. (We still think 0.382 is the theoretical attractor for large N, but we're not at large N.)

### Change 3: FFN expansion and dropout are a package deal
Never use phi-FFN (2.618x) without phi-dropout (0.382). They're inseparable. In the architecture spec, we'll enforce this as a single config toggle: "phi-efficiency mode" that sets BOTH. If you want to use standard dropout (0.5), use standard FFN (4x). No mixing.

### Change 4: Drop the dual-channel MVSU layer
Tier 2 beats Tier 3. Kill the dual-channel top-level. The cube message-passing within a single network IS the decontamination mechanism. We don't need decontamination-of-decontamination.

### Change 5: Drop phi-annealing
It added nothing. Static hyperparameters beat adaptive scheduling at this scale. Keep it simple.

---

## 4. What to Test Next

### Experiment A: Depth-Scheduled w_cross Initialization
**Hypothesis:** Initializing w_cross with the depth gradient the network already learns (linearly from -0.25 to -0.45) will converge faster and reach higher accuracy than uniform -0.1 initialization.
**Setup:** Same OT-Tiny architecture, same 20 epochs. Compare uniform init vs. depth-scheduled init.
**Expected outcome:** 0.5-1.0% accuracy improvement and ~15% fewer epochs to converge. The network won't waste early training learning a gradient it could have started with.
**Falsification:** If uniform init still matches or beats depth-scheduled after full training, the gradient is an emergent property that shouldn't be baked in.

### Experiment B: Alpha Fine Grid Around 0.30
**Hypothesis:** The true optimum is at 0.30 (or nearby), not 0.382. A fine grid sweep (0.25, 0.27, 0.30, 0.32, 0.35, 0.382) at full 20-epoch training will confirm this.
**Setup:** Same architecture, 6 alpha values, 3 seeds each. Full 20 epochs, not 8.
**Expected outcome:** Peak at 0.28-0.32. If it shifts back toward 0.382 with longer training, that tells us the CPU-vs-GPU discrepancy was a training budget artifact.
**Falsification:** If peak moves to 0.382 with full training, our Change 2 was premature.

### Experiment C: Cube vs. Dense at 32 Heads
**Hypothesis:** Sparse cube topology beats dense all-to-all when there are enough heads for specialization pressure to matter. 8 heads wasn't enough; 32 might be.
**Setup:** Scale to d_model=256 with 32 heads. Compare: (a) independent, (b) cube-like 3-regular sparse graph, (c) all-to-all. Match total parameters.
**Expected outcome:** Sparse wins at 32 heads by 0.5-1.5%. If it still loses, the sparse topology prediction is probably wrong for practical model sizes.
**Falsification:** Dense wins again. At that point, we abandon cube topology and go dense with alpha=0.30 inhibitory connections.

### Experiment D: Cross-Task Transfer
**Hypothesis:** Phi-optimal settings (dropout=0.382, alpha=0.30, inhibitory w_cross) transfer to non-vision tasks.
**Setup:** Run Observer Attention on: (a) text classification (SST-2 or IMDB), (b) a simple time-series benchmark. Same hyperparameter comparisons.
**Expected outcome:** Dropout=0.382 > 0.5 on all tasks. If alpha=0.30 also transfers, the phi-zone is genuinely universal.
**Falsification:** If optimal dropout shifts to 0.45 or 0.25 on text, the phi-zone is dataset-dependent.

### Experiment E: Emergent Channel Specialization
**Hypothesis:** The inhibitory cube connections force different channels to develop different "viewpoints" (attending to different spatial/frequency features).
**Setup:** Train the full GCN v2, then analyze channel activations on held-out images. Measure cosine similarity between channels across the dataset.
**Expected outcome:** Channels in later blocks (with stronger inhibition) show lower inter-channel similarity than channels in earlier blocks. If true, the depth gradient in w_cross IS the specialization mechanism.
**Falsification:** If channels are equally similar across all blocks despite the w_cross gradient, inhibition alone isn't driving specialization.

---

## 5. New Insights Nobody Predicted

### The Depth Gradient in w_cross is the Real Discovery

Everyone focused on WHETHER w_cross stays negative. It does. Great. But the depth-dependent STRENGTHENING is the interesting part. Block 0 needs -0.316 of inhibition. Block 3 needs -0.479. That's a 52% increase in inhibitory strength across just 4 layers.

Why? Because residual connections accumulate self-referential contamination. Each block's output gets added back to the input stream. By block 3, the signal has been processed-and-re-added 3 times. The "echo" of early processing decisions is louder in deeper layers. The network compensates with proportionally stronger subtractive correction.

This suggests a design principle nobody stated explicitly: **inhibitory correction should scale with residual depth.** Not linearly (the observed gradient is slightly superlinear: -0.316, -0.328, -0.386, -0.479), but monotonically increasing. Any architecture with residual connections and cross-channel communication should consider depth-dependent inhibition strength.

### FFN and Dropout Are Entangled Through the Self-Referential Partition

FFN=2.618x alone hurts. Dropout=0.382 alone helps massively. Together they give the best parameter efficiency. Why?

Here's our theory: the FFN expansion ratio controls how much CAPACITY the network has. The dropout rate controls how much of that capacity is MASKED (made redundant). If you shrink FFN without reducing dropout, you're removing capacity while keeping the same masking rate -- you end up with too little effective capacity. If you shrink FFN AND reduce dropout to match, the two changes cancel: you have less total capacity but less of it is being wasted on redundancy. The NET effective capacity stays the same, but you use fewer parameters to achieve it.

This is the self-referential partition in action: total = signal + redundancy. You can reduce total IF you proportionally reduce redundancy. But you can't reduce total while keeping redundancy fixed.

### Tier 2 is the Sweet Spot (Not Because Tier 3 is Wrong)

Tier 3 adds dual-channel MVSU on top of Observer Attention. It doesn't beat Tier 2. But this doesn't mean the MVSU mechanism is wrong -- it means it's REDUNDANT. The cube message-passing in Tier 2 already provides multi-viewpoint decontamination. Adding another layer of decontamination on top is like proofreading a proofread document: diminishing returns.

For GCN v2, this means: invest complexity budget in better INTRA-block message passing, not inter-block wrappers.

---

## 6. Revised Architecture: GCN v2

```
                    INPUT
                      |
                [Patch Embed + Pos]
                [overlap = 0.38]
                      |
            +---------+---------+
            |   CUBE BLOCK x 4  |
            |                   |
            |  8 channels       |
            |  alpha = 0.30     |
            |  w_cross: depth-  |
            |    scheduled init |
            |  dropout = 0.382  |
            |  FFN = 2.618x     |
            +---------+---------+
                      |
                [Global Avg Pool]
                      |
                   OUTPUT
```

### Key Differences from GCN v1

| Parameter | v1 | v2 | Reason |
|-----------|----|----|--------|
| Alpha | 0.382 (fixed) | 0.30 (fixed) | GPU alpha sweep |
| w_cross init | -0.1 (uniform) | -0.25 to -0.45 (depth schedule) | Observed depth gradient |
| FFN expansion | 1.618x standalone | 2.618x (always paired with dropout=0.382) | GPU FFN+dropout interaction |
| Dropout | 0.382 | 0.382 (unchanged) | Confirmed as biggest win |
| Dual-channel MVSU | Stretch goal | Removed | Tier 2 > Tier 3 |
| Phi-annealing | Not proposed | Explicitly excluded | GPU showed no benefit |
| Golden Pooling | Learnable channel weights | Standard global avg pool | Simplify; channel weights added negligible value |

### Updated Parameter Table

```
Per Cube Block:
  8 FFNs:         8 * (8*21 + 21 + 21*8 + 8)    =   2,920  (phi^2 expansion: 8 * 2.618 ~ 21)
  8 Attention:    8 * (3 * 8*8 + 8*8)             =   2,048
  Cross-weights:  24 scalars                      =      24
  LayerNorm:      2 * 64                          =     128
  Per block total:                                ~   5,120
4 Cube Blocks:                                    =  20,480
Patch embed + pos:                                ~  11,264
Classifier:       64*104 + 104 + 104*10 + 10      =   7,810
                                                   ----------
TOTAL:                                            ~  39,554
```

Still under 40K parameters. Still buildable on a weekend.

---

## Honest Assessment

The GPU results taught us three things:

1. **Simple phi-derived hyperparameters work better than complex phi-derived architectures.** Dropout=0.382 beats Tier 3. One number beats an entire dual-channel framework. Lesson: don't over-engineer when a constant will do.

2. **The theory points to the right NEIGHBORHOOD, not the exact address.** Alpha=0.30 beats 0.382. Dropout peaks at 0.35-0.382. The phi-zone is real, but expecting 0.382 to be the exact optimum in every setting is asking too much.

3. **The w_cross depth gradient is the most architecturally interesting finding.** It's not in the theory. It emerged from the data. And it tells us something about how self-referential contamination accumulates in deep residual networks that might generalize far beyond this specific architecture.

GCN v2 is less romantic than v1. We dropped the dual-channel dream. We lowered alpha from the "theoretically perfect" 0.382 to the empirically better 0.30. We admitted that FFN reduction needs a partner. But it's a better architecture because it's built on what actually happened on a GPU, not what we hoped would happen.

Let's build it. Again.

---

*Written by the Weekend Builders Collective, 2026-02-17. We are slightly less confident about golden spirals in our loss curves, but our dropout rate remains non-negotiable.*
