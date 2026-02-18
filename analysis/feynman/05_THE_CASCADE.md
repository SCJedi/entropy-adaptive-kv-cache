# How Signal Dies on the Way to Memory

*A seven-stage cascade, a sub-multiplicative surprise, and the paradox of well-rehearsed memories.*

---

## The Telephone Game

You know the telephone game -- whisper a phrase through a chain of people, and by the end it's unrecognizable. Each person hears a slightly garbled version of the message and passes along their best guess. The errors accumulate.

Now imagine that each person in the chain isn't just hearing a garbled version of the previous person's message. They're hearing that *plus their own internal voice*, which they can't fully distinguish from the incoming message. That's what biological perception looks like -- a cascade of processing stages, each contaminated by its own self-referential feedback, each passing its degraded output to the next.

We modeled this as a cascade of 7 self-referential stages, inspired by the biological pathway from raw sensation to recalled memory:

| Stage | Name | alpha (contamination) | N (channels) | What it does |
|-------|------|----------------------|--------------|-------------|
| 1 | Sensory | 0.05 | many | Retina, cochlea -- raw input |
| 2 | Features | 0.30 | 2 | Edge detection, V1 -- basic patterns |
| 3 | Binding | 0.50 | 2 | Object recognition -- putting features together |
| 4 | Awareness | 0.60 | 1-2 | Conscious perception |
| 5 | Narrative | 0.80 | 1 | Internal monologue -- making sense of it |
| 6 | Memory | 0.90 | 1 | Encoding into long-term storage |
| 7 | Recall | 1.00 | 1 | Retrieval -- almost fully self-generated |

Notice two trends. First, contamination increases as you go higher -- sensory organs are barely self-referential (alpha = 0.05), but recall is almost entirely self-generated (alpha = 1.0). Second, the number of channels decreases -- early stages have binocular processing (two eyes, two ears), but later stages funnel into a single narrative thread.

---

## The Naive Prediction

From Document 1, we know that each stage with contamination alpha preserves R^2 = w(alpha) of the signal, where w satisfies alpha^2 * w^2 + w - 1 = 0. So the natural prediction for the cascade is: just multiply the per-stage R^2 values.

    R^2_total = w(0.05) * w(0.30) * w(0.50) * w(0.60) * w(0.80) * w(0.90) * w(1.00)
              = 0.998 * 0.923 * 0.828 * 0.781 * 0.693 * 0.654 * 0.618
              = 0.167

So we predicted that about 17% of the original signal should survive to recall. That's not great, but it's something.

---

## The Surprise: It's Much Worse

We ran the simulation. Seven stages, each stage's output feeding into the next stage's input, each stage learning its own myopic weight.

The actual R^2 at recall: **0.008**.

Not 16.7%. Less than 1%. The actual signal survival is roughly **20 times worse** than the multiplicative prediction.

| Stage | alpha | Multiplicative prediction | Actual simulated R^2 |
|-------|-------|--------------------------|---------------------|
| 1 (Sensory) | 0.05 | 0.998 | 0.998 |
| 2 (Features) | 0.30 | 0.921 | 0.897 |
| 3 (Binding) | 0.50 | 0.763 | 0.598 |
| 4 (Awareness) | 0.60 | 0.596 | 0.303 |
| 5 (Narrative) | 0.80 | 0.413 | 0.111 |
| 6 (Memory) | 0.90 | 0.270 | 0.033 |
| 7 (Recall) | 1.00 | 0.167 | 0.008 |

By stage 4 (awareness), we've already lost 70% of the signal. By recall, 99.2% is gone.

---

## Why Sub-Multiplicative?

The multiplicative prediction assumed that each stage receives *white noise* -- a clean, uncorrelated signal. The per-stage formula R^2 = w(alpha) was derived under that assumption (see Document 1).

But each stage's output isn't white noise. It's an AR(1) process -- a signal with *temporal correlation*. Stage 1's output at time t is correlated with its output at time t-1, because of the feedback loop y(t) = s(t) + alpha * w * y(t-1). This correlation rho = alpha * w is the temporal fingerprint of self-referential processing.

When stage 2 receives this correlated signal, something nasty happens. Stage 2's self-referential feedback, alpha_2 * w_2 * y_2(t-1), is *correlated with the incoming signal* through the temporal structure. The contamination and the signal share temporal patterns, making them harder to separate. It's as if the echo has learned to mimic the rhythm of the signal.

At low alpha (stage 1, alpha = 0.05), the temporal correlation is negligible, and the multiplicative prediction is accurate. At high alpha (stages 5-7), the correlation is strong, and the sub-multiplicative penalty is severe.

    Degradation factor eta = actual R^2 / predicted R^2

| Cascade depth | alpha per stage | Multiplicative prediction | Actual R^2 | eta |
|---------------|----------------|--------------------------|-----------|-----|
| 3 stages | 0.30 each | 0.787 | 0.540 | 0.69 |
| 3 stages | 0.50 each | 0.569 | 0.276 | 0.49 |
| 3 stages | 0.80 each | 0.333 | 0.105 | 0.32 |
| 5 stages | mixed (bio) | 0.130 | 0.028 | 0.22 |

At low alpha, eta is near 1 (the multiplicative prediction is fine). At high alpha, eta drops to 0.22 -- the actual cascade is almost 5 times worse than multiplication would suggest.

---

## The Monocular Bottleneck

Now look at what happens when we give stages 2-4 binocular processing (N = 2, with the negative cross-connections from Document 4):

| Stage | alpha | N | R^2 (monocular cascade) | R^2 (binocular stages 2-4) |
|-------|-------|---|------------------------|-----------------------------|
| 1 (Sensory) | 0.05 | 1 | 0.998 | 0.998 |
| 2 (Features) | 0.30 | 2 | 0.897 | 0.998 |
| 3 (Binding) | 0.50 | 2 | 0.598 | 0.998 |
| 4 (Awareness) | 0.60 | 2 | 0.303 | 0.981 |
| 5 (Narrative) | 0.80 | 1 | 0.111 | 0.600 |
| 6 (Memory) | 0.90 | 1 | 0.033 | 0.228 |
| 7 (Recall) | 1.00 | 1 | 0.008 | 0.065 |

Binocular processing holds the signal nearly intact through stages 2-4. The R^2 at stage 4 is 0.981 instead of 0.303. That's more than 3x better.

But look at stage 5 -- the narrative stage. This is where the number of channels drops from 2 to 1. The binocular parallax is gone. And the signal drops from 0.981 to 0.600 in a single stage. From there, the monocular degradation resumes.

Final R^2 with binocular stages: 0.065. Without: 0.008. That's an **8x improvement** -- but still only 6.5% of the original signal survives to recall.

The transition from N = 2 to N = 1 is the critical bottleneck. By the data processing inequality, once information is lost at a monocular stage, no subsequent processing can recover it. It doesn't matter how sophisticated stages 6 and 7 are -- they're working with signal that was already degraded at stage 5.

This is why the bottleneck *position* matters. An early bottleneck (monocular at stage 2) is catastrophic -- all subsequent stages operate on degraded input. A late bottleneck (monocular at stage 5, after binocular stages have preserved the signal) is much less damaging.

---

## The Rehearsal Paradox

Every time you recall a memory, you're running the signal through another self-referential processing stage. Each recall is a new instance of stage 7, with alpha near 1.0.

The cascade theorem predicts geometric decay:

    R^2 after n recalls <= R^2_cascade * w(alpha_recall)^n

For alpha_recall = 1 (strongly reconstructive recall):

| Recalls | R^2 upper bound (w^n) | Actual simulated R^2 |
|---------|----------------------|---------------------|
| 1 | 0.618 | 0.37 |
| 2 | 0.382 | 0.08 |
| 3 | 0.236 | 0.02 |
| 5 | 0.090 | 0.003 |
| 8 | 0.021 | 0.0001 |

After 5 recalls: 0.3% of the original signal remains. After 8 recalls: essentially zero.

And the actual decay is *faster* than the geometric upper bound, because of the same sub-multiplicative effect -- each recall's output is temporally correlated, making the next recall's job harder.

Here's the paradox: **well-rehearsed memories feel more vivid but are less accurate.** Each recall strengthens the neural pathways involved (lowering the retrieval effort, making it feel easier and more confident), while simultaneously replacing original signal with self-generated content. Your confidence in the memory goes up, but the memory's accuracy goes down.

This is like photocopying a photocopy. Each generation looks crisp and clean to the copier, but each generation has degraded a little from the original. By the tenth copy, the image looks clear but bears little resemblance to the original. The copier doesn't know this because it only sees the current page, not the original.

The psychological literature confirms this. Elizabeth Loftus's 30-year program on memory malleability showed that frequently recalled memories are among the most distorted. "Flashbulb memories" -- those vivid, confident recollections of where you were during a dramatic event -- degrade despite their subjective vividness. Our cascade model gives a quantitative explanation: each vivid, confident recall is another self-referential processing stage, and the signal loss is sub-multiplicative.

---

## What This Means

The cascade model makes three concrete predictions:

1. **Multi-stage ML pipelines (retrieval -> ranking -> generation, or iterative RLHF) suffer compounding degradation** that is worse than you'd estimate by analyzing each stage separately. The product of per-stage R^2 values is an optimistic upper bound, not a prediction.

2. **Binocular processing is most valuable at intermediate stages** -- not at the input (where contamination is low and not worth decontaminating) and not at the output (where the signal is already lost). The sweet spot is where contamination is moderate (alpha = 0.3-0.6) and the marginal benefit of decontamination has the longest downstream reach.

3. **Iterative self-referential processes (repeated RLHF updates, recursive synthetic data generation) face exponential signal decay.** Each iteration is a new cascade stage. The sub-multiplicative penalty means the degradation after k iterations is much worse than the product of k single-iteration analyses would suggest.

The cascade is the bridge between the single-stage algebra of Documents 1-2 and the architectural solutions of Documents 6-8. A single stage loses signal; the cascade shows how that loss compounds; and the MVSU (Documents 6-8) is the architecture that prevents the compounding from becoming catastrophic.

---

**The key insight:** Self-referential signal loss through a cascade is sub-multiplicative -- dramatically worse than the product of per-stage losses, because each stage's temporally correlated output makes subsequent decontamination progressively harder. The monocular bottleneck (where channels drop from two to one) is the critical failure point: once parallax is lost, the information is gone forever.
