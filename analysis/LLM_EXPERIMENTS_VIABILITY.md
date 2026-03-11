# LLM Experiments: Mathematical Viability Analysis

**Date:** 2026-03-10
**Method:** Information theory, literature comparison, empirical feasibility
**Hardware:** Laptop, CPU only (no GPU), Python + PyTorch + HuggingFace
**Time budget:** 30 minutes per experiment

---

## 1. Opportunity 1: Adaptive Compute per Token

### 1.1 Theoretical Ceiling

**Bound:** Token difficulty (measured by entropy H_i of next-token distribution) varies ~10x across positions in natural text. Rate-distortion theory says optimal compute allocation is proportional to H_i. Uniform allocation wastes:

```
waste_fraction = 1 - E[H_i] / max(H_i)
```

Empirically, ~30-50% of tokens in English text are highly predictable (H < 1 bit out of ~8 bits max). These tokens need ~10-25% of full model compute. The theoretical ceiling for compute savings from perfect adaptive allocation is **2-4x**.

**Information-theoretic bound on layer skipping specifically:**

For a token where the model is already 99% confident in the prediction after layer L, the remaining layers contribute at most:
```
I_remaining <= H(Y | representation_L) <= h(0.01) ≈ 0.08 bits
```

where h() is binary entropy. If the model needs 8 bits total and gets 7.92 by layer L, layers L+1 through L_max contribute 0.08 bits -- negligible.

### 1.2 What's Already Achieved

| Method | Speedup | Quality Loss | Year |
|--------|---------|-------------|------|
| DeeBERT (early exit for BERT) | 1.5-2x | <1% on GLUE | 2020 |
| CALM (confident adaptive language modeling) | 2-3x | <1% on generation | 2022 |
| Mixture of Depths (Raposo et al.) | 1.5x | <0.5% perplexity | 2024 |
| Universal Transformers (adaptive depth) | 1.3-1.5x | Matched | 2019 |
| SkipDecode | 2-5x | <2% quality | 2024 |

### 1.3 Gap Analysis

- **Theoretical ceiling:** 2-4x compute savings
- **Best achieved:** 2-3x (CALM) for generation, 1.5x (MoD) for training
- **Remaining gap:** ~30-50% of the theoretical ceiling is already captured
- **What's left:** Better routing decisions (current routers are simple thresholds on confidence)

The ceiling is relatively close. But validating the PRINCIPLE (easy tokens need fewer layers) on small models is entirely feasible and informative.

### 1.4 CPU Feasibility

**GPT-2 small (124M params) on CPU:**
- Forward pass: ~100-200ms per token (batch=1)
- WikiText-2 validation: ~3,760 tokens
- Full analysis (record per-layer activations): ~3,760 * 0.2s = ~12 minutes
- With intermediate extraction per layer: ~3,760 * 12 * 0.05s = ~38 minutes (TOO SLOW)
- **Optimization:** Process in batches, extract layer outputs via hooks = ~15-20 minutes

**DistilGPT-2 (82M, 6 layers) on CPU:**
- Forward pass: ~50-80ms per token
- Full analysis: ~3,760 * 0.08s = ~5 minutes
- But only 6 layers -- less informative for layer-skipping analysis

**Decision:** Use GPT-2 small with batched processing and PyTorch hooks. Subsample WikiText-2 if needed (1,000-2,000 tokens sufficient for statistics).

### 1.5 Novelty Check

**Already published:** The exact experiment (measure per-layer contribution vs token difficulty) has been done:
- Elbayad et al. 2020: measured layer-wise confidence in BERT
- Schuster et al. 2022 (CALM): measured per-layer exit decisions for GPT
- Fan et al. 2020: measured layer importance by depth

**What we can contribute:** We're not going to discover something new. But we CAN validate the first-principles predictions:
1. Does the 98.5% attention sparsity estimate hold for GPT-2 small?
2. Does the "30-50% of tokens can skip later layers" estimate hold?
3. Is there a clean correlation between token entropy and later-layer contribution?

These are **validation experiments**, not discovery experiments. That's fine -- the first-principles analysis made specific quantitative predictions that should be tested.

### 1.6 GO/NO-GO

**GO** -- as a validation experiment. Clear measurable outcome, feasible runtime, informative regardless of result.

---

## 2. Opportunity 2: Information-Optimal Data Curation

### 2.1 Theoretical Ceiling

**Bound:** If training samples have information content I_i (bits of new information for the model), optimal curation selects the top-k by I_i. The ceiling depends on the distribution of I_i.

Assuming I_i follows a power law (common for natural data):
```
P(I_i > x) ~ x^{-alpha}
```

With alpha ≈ 1.5 (empirical from training loss distributions), the top 10% of samples by information content contain:
```
fraction_info(top 10%) = integral from x_90 to inf of x * f(x) dx / E[I]
```

For alpha=1.5: top 10% contains ~45% of total information. For alpha=2.0: top 10% contains ~32%.

**Theoretical ceiling:** Training on the top 10% by information could achieve 30-50% of the learning from the full dataset, meaning 3-5x data efficiency for that fraction. But there's a catch: the "easy" samples (low information) still provide distributional coverage. Removing them entirely may cause distributional gaps.

### 2.2 What's Already Achieved

| Method | Efficiency Gain | Quality | Year |
|--------|----------------|---------|------|
| D4 (data distillation) | 2-3x subset matches full | Matched on CIFAR | 2023 |
| SemDeDup (semantic dedup) | 1.5-2x | Matched | 2023 |
| DCLM (data curation) | 2x data efficiency | Matched on benchmarks | 2024 |
| FineWeb-Edu | 1.5-2x | Matched on knowledge tasks | 2024 |
| Influence functions | Oracle baseline | Matched in theory | 2017+ |

### 2.3 Gap Analysis

- **Theoretical ceiling:** 3-5x data efficiency (top 10% captures 30-50% of info)
- **Best achieved:** 2-3x (D4 on CIFAR, DCLM on web text)
- **Remaining gap:** ~50% of theoretical ceiling captured
- **Key question:** Does information-theoretic scoring (model loss on sample) beat simpler quality heuristics?

### 2.4 CPU Feasibility

**DistilBERT on SST-2:**
- Fine-tuning: ~30s/epoch on CPU for 67K samples
- Full fine-tune (3 epochs): ~90 seconds
- Recording per-sample loss: adds ~10% overhead
- Running 4-5 variants: 4 * 90s = ~6 minutes
- Total with overhead: ~15-20 minutes

**This is very feasible on CPU.**

**Alternative: GPT-2 small on WikiText-2:**
- Perplexity evaluation: ~12 minutes for full validation set
- Per-sample loss recording: same pass
- Training GPT-2 from scratch: NOT feasible on CPU
- Fine-tuning: ~30 min for 1 epoch on subset -- borderline

**Decision:** Use DistilBERT on SST-2 for classification (fast, well-understood baseline). The experiment measures whether information-theoretic sample selection beats random selection.

### 2.5 Novelty Check

**Already published:**
- Curriculum learning (Bengio et al. 2009): train on easy samples first, then hard
- Self-paced learning (Kumar et al. 2010): similar idea
- D4 (2023): selects diverse, difficult samples for training
- Loss-based data pruning (Sorscher et al. 2022): exactly our proposed method

**Critical finding:** Sorscher et al. 2022 ("Beyond neural scaling laws") already did THIS EXACT EXPERIMENT. They showed that pruning low-loss samples and training on high-loss samples outperforms random subsampling, and that the improvement follows power-law scaling. Their result: pruning to top 30% by difficulty achieves ~90% of full-dataset performance.

**What we can contribute:** Validate their finding on a different model/dataset (DistilBERT/SST-2 vs their CIFAR/ResNet). This is pure replication, not novelty.

### 2.6 GO/NO-GO

**GO** -- as a replication/validation experiment. The method is published, but confirming the principle on NLP classification adds confidence. Fast to run, clear success criteria.

---

## 3. Opportunity 3: KV Cache Compression

### 3.1 Theoretical Ceiling

**Bound from first-principles analysis:** The KV cache stores full key-value vectors for all tokens at all layers. Information-theoretic analysis shows:

```
KV_stored = 2 * n_layers * n_heads * n * d_head * precision
           = 2 * 12 * 12 * 1024 * 64 * 2 bytes  (GPT-2 small, 1K context)
           = 37.7 MB

KV_useful ≈ n * H_effective * d_head * n_layers
           ≈ 1024 * 5 bits * 64 * 12
           ≈ 3.9M bits ≈ 0.49 MB
```

**Compression opportunity: ~77x** for GPT-2 small at 1K context.

For larger models (32 layers, 32 heads, 8K context): the first-principles analysis estimates **~150x** compression opportunity.

### 3.2 What's Already Achieved

| Method | Compression | Quality Loss | Year |
|--------|------------|-------------|------|
| GQA (grouped query attention) | 4-8x | <0.5% | 2023 |
| MQA (multi-query attention) | 8-32x | 1-2% | 2019 |
| H2O (heavy hitter oracle) | 5-10x | <1% | 2023 |
| StreamingLLM | 100x+ (fixed window) | 2-5% for long context | 2023 |
| KV quantization (INT4) | 4x | <0.5% | 2023 |
| Scissorhands | 5x | <1% | 2023 |
| PyramidKV | 6-12x | <1% | 2024 |

### 3.3 Gap Analysis

- **Theoretical ceiling:** 77-150x compression
- **Best achieved (compound):** GQA (8x) * INT4 (4x) = ~32x combined
- **Remaining gap:** 2-5x improvement still possible beyond current best
- **Key question:** Where does quality break down as we approach the theoretical limit?

Importantly, GQA/MQA require architecture changes at training time. For inference-time compression (eviction/quantization), the best is ~10x. The gap to the 77-150x theoretical limit is substantial.

### 3.4 CPU Feasibility

**GPT-2 small generation on CPU:**
- Generation speed: ~0.5-2 tokens/sec (batch=1)
- 100 sequences of 256 tokens: 100 * 256 / 1 = ~25,600 seconds = **7+ hours (WAY TOO SLOW)**

**Revised plan -- analysis, not generation:**
- Run GPT-2 small on WikiText-2 validation (prefill, not generation)
- Record full attention matrices for all layers/heads
- Analyze attention sparsity patterns
- Simulate eviction by zeroing low-attention KV entries and measuring output change
- Prefill on 1024-token sequences: ~1024 * 0.15s = ~2.5 minutes per sequence
- 10-20 sequences: ~25-50 minutes

**Further optimization:** Don't generate -- just measure attention patterns during prefill. No need for actual token generation.

- Forward pass on 20 sequences of 512 tokens (batch=1): 20 * 512 * 0.05s = ~8.5 minutes
- This extracts all attention matrices needed

**Decision:** Analyze attention sparsity during prefill (not generation). Measure what fraction of KV entries receive meaningful attention. Simulate eviction by masking and re-running. 20 sequences of 512 tokens, ~15-20 minutes total.

### 3.5 Novelty Check

**Already published:**
- H2O (2023): exactly measures attention sparsity and evicts low-attention entries
- StreamingLLM (2023): keeps only attention sinks + recent window
- Scissorhands (2023): analyzes attention patterns for pivotal tokens
- PyramidKV (2024): layer-aware KV budget allocation

**The attention sparsity measurement itself** has been done many times (Clark et al. 2019, Voita et al. 2019, etc.).

**What we can contribute:** Validate first-principles prediction (98.5% sparsity, 150x compression ceiling) against actual GPT-2 measurements. Check if the information-theoretic bound is realistic or optimistic.

### 3.6 GO/NO-GO

**GO** -- as a validation experiment. The key value is testing whether the information-theoretic bound (150x) matches reality. If attention is less sparse than predicted, the bound is wrong and the first-principles analysis needs correction.

---

## 4. Opportunity 4: Separating Competence from Knowledge

### 4.1 Theoretical Ceiling

**Bound:** If competence (linguistic rules + reasoning) requires K_c ≈ 10^11 bits and knowledge (facts) requires K_k ≈ 10^12 bits, separating them enables a competence-only model that is:
```
size_competence / size_full = K_c / (K_c + K_k) ≈ 1/11 ≈ 9%
```

A model 10x smaller for reasoning tasks (with retrieval for factual tasks).

### 4.2 CPU Feasibility

**Testing this requires comparing:**
- Small model + retrieval vs. large model on reasoning tasks
- The smallest usable LLMs on CPU are GPT-2 small (124M) and DistilGPT-2 (82M)
- These models are too weak for meaningful reasoning benchmarks
- Even DistilBERT on NLI is marginal

**Fundamental problem:** We can't meaningfully test competence-knowledge separation with models this small. The smallest models where "reasoning" is meaningful are ~1-3B parameters, which are too slow on CPU.

### 4.3 GO/NO-GO

**NO-GO.** Cannot be meaningfully tested on our hardware. Models small enough to run on CPU don't have separable competence and knowledge -- they barely have either.

---

## 5. Opportunity 5: Non-Autoregressive Generation

### 5.1 Theoretical Ceiling

**Bound:** Autoregressive generation requires O(n) serial steps for n tokens. Perfect parallel generation would be O(1) serial steps. The theoretical speedup is n (the sequence length).

In practice, parallel generation requires refinement because tokens depend on each other. With k refinement steps:
```
speedup = n / k
```

Current speculative decoding achieves k ≈ n/3 (3x speedup). Medusa achieves similar. The question is whether k can be reduced to O(log n) or O(1).

### 5.2 CPU Feasibility

**Testing parallel generation requires:**
- Training or fine-tuning a parallel generation head
- Comparing generation quality to autoregressive baseline
- Running generation for many sequences

On CPU, generation is already slow (~0.5-2 tok/s for GPT-2). Implementing and testing a parallel head would require significant engineering and long runtimes.

### 5.3 GO/NO-GO

**NO-GO.** Too engineering-heavy for our constraints, low probability of novel contribution, and the generation-speed bottleneck on CPU makes timing comparisons meaningless.

---

## 6. Summary: GO/NO-GO Table

| # | Opportunity | GO/NO-GO | Expected Runtime | Novelty | What We Learn |
|---|-----------|----------|-----------------|---------|---------------|
| 1 | Adaptive compute (layer importance) | **GO** | ~20 min | Validation | Confirm/deny 30-50% skippable prediction |
| 2 | Data curation (info gain) | **GO** | ~20 min | Replication | Confirm/deny info-sorted > random on NLP |
| 3 | KV cache compression (sparsity) | **GO** | ~20 min | Validation | Confirm/deny 98.5% sparsity bound |
| 4 | Competence-knowledge separation | **NO-GO** | N/A | N/A | Models too small for meaningful test |
| 5 | Non-autoregressive generation | **NO-GO** | N/A | N/A | Too engineering-heavy, low ROI |

### Priority Order

1. **Experiment A (Adaptive Compute)** -- Highest expected information value. Tests a specific quantitative prediction from the first-principles analysis. Cleanest experimental design.

2. **Experiment C (KV Cache Sparsity)** -- Tests another specific prediction. Simpler analysis (just measure attention patterns). No training required.

3. **Experiment B (Data Curation)** -- Replicates a published result. Still valuable for confirming the principle transfers to NLP classification, but we already know the answer.

---

## 7. Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| GPT-2 too slow on CPU | 20% | Delays | Use DistilGPT-2 or subsample aggressively |
| HuggingFace version incompatibility | 10% | Blocks | Pin versions, use simple API |
| Results are trivially expected | 40% | Low novelty | Focus on quantitative validation, not discovery |
| Memory overflow extracting attention matrices | 30% | Blocks | Process sequence by sequence, not batched |
| Already published exactly this | 50% | Low novelty | Accept validation role, not novelty |

---

## 8. Applying Retrospective Lessons

### MATH FIRST
Done. This document IS the math-first step. No code until the analysis is complete.

### Kill Early
Each experiment has explicit kill criteria (Section in experiment plan). If the first 100 tokens of Experiment A show no correlation between confidence and layer importance, we kill it.

### Viability Check
Each experiment has been checked against:
1. Theoretical ceiling (is the effect large enough to measure?)
2. CPU feasibility (can we run it in 30 minutes?)
3. Literature (what's already known?)
4. Novelty (what new thing do we learn?)

### Don't Tune Against Structural Barriers
The three GO experiments measure structure, not tune parameters. We're asking "is the phenomenon real?" not "can we optimize it?"

### Test Beautiful Ideas Against Boring Alternatives
Each experiment compares the information-theoretic prediction against baselines (random eviction, random sampling, uniform layer importance).
