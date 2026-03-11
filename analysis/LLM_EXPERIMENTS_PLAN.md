# LLM Experiments: Complete Execution Plan

**Date:** 2026-03-10
**Hardware:** Laptop CPU, Python 3.x, PyTorch, HuggingFace transformers
**Time budget:** 30 minutes per experiment, ~90 minutes total
**Goal:** Validate or falsify quantitative predictions from LLM_FIRST_PRINCIPLES.md

---

## Preamble: What These Experiments Are and Are Not

**They ARE:** Validation of specific quantitative predictions made by first-principles analysis. The analysis predicted:
1. 30-50% of tokens can skip later layers without changing the prediction
2. ~90-96% of attention entries in GPT-2 are effectively zero
3. Training samples vary ~10x in information content, and selection by information beats random

**They ARE NOT:** Novel research contributions. Every phenomenon measured here has been published. The value is in testing whether our analytical framework produces correct quantitative predictions.

**Success criterion for the overall effort:** If 2/3 predictions are within 2x of measured values, the analytical framework is validated as a useful tool for reasoning about LLM efficiency.

---

## Experiment A: Adaptive Compute — Layer Importance by Token Difficulty

### A.1 Hypothesis

**Prediction from first-principles analysis:** For tokens where the model is already >95% confident, later transformer layers contribute negligibly. Specifically, 30-50% of tokens in natural English text should be classifiable correctly using only the first 8 of 12 layers in GPT-2 small.

**Null hypothesis:** All 12 layers contribute equally regardless of token difficulty. Layer 12 changes the prediction for easy and hard tokens at similar rates.

### A.2 Mathematical Framework

For token position i, let p_i^L = P(correct token | hidden state at layer L). The contribution of layers L+1 through L_max is:

```
delta_p_i(L) = p_i^{L_max} - p_i^L
```

A token is "skippable at layer L" if:
```
argmax(logits_i^L) == argmax(logits_i^{L_max})
```

The **skippable fraction at layer L** is:
```
F_skip(L) = (1/N) * sum_i [argmax(logits_i^L) == argmax(logits_i^{L_max})]
```

**First-principles prediction:**
```
F_skip(8) ≈ 0.30 - 0.50    (30-50% of tokens match at layer 8)
F_skip(10) ≈ 0.50 - 0.70   (50-70% at layer 10)
F_skip(12) = 1.0            (trivially, final layer)
```

### A.3 Method

```python
# PSEUDOCODE — experiment_a_adaptive_compute.py

import torch
import numpy as np
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from datasets import load_dataset

# 1. Load model and data
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model.eval()

# Load WikiText-2 validation
dataset = load_dataset('wikitext', 'wikitext-2-raw-v1', split='validation')

# 2. Register hooks to capture hidden states at each layer
hidden_states = {}
def make_hook(layer_idx):
    def hook_fn(module, input, output):
        # output[0] is the hidden state
        hidden_states[layer_idx] = output[0].detach()
    return hook_fn

for i, block in enumerate(model.transformer.h):
    block.register_forward_hook(make_hook(i))

# 3. Process sequences
lm_head = model.lm_head  # Linear(768, 50257)
results = []

for seq in tokenized_sequences[:20]:  # 20 sequences of 512 tokens
    input_ids = seq.unsqueeze(0)  # [1, 512]

    with torch.no_grad():
        outputs = model(input_ids)

    final_logits = outputs.logits[0]  # [512, 50257]
    final_preds = final_logits.argmax(dim=-1)  # [512]
    final_probs = torch.softmax(final_logits, dim=-1)

    for layer_idx in range(12):
        # Project hidden state through LM head
        layer_logits = lm_head(model.transformer.ln_f(hidden_states[layer_idx][0]))
        layer_preds = layer_logits.argmax(dim=-1)
        layer_probs = torch.softmax(layer_logits, dim=-1)

        # Metrics
        match = (layer_preds == final_preds).float()
        top1_prob = layer_probs.max(dim=-1).values

        results.append({
            'layer': layer_idx,
            'match_fraction': match.mean().item(),
            'mean_top1_prob': top1_prob.mean().item(),
            'match_when_confident': ...  # match rate for tokens with top1 > 0.9
        })

# 4. Analysis
# - Plot F_skip(L) vs layer
# - Plot mean confidence vs layer
# - Scatter: per-token final confidence vs earliest matching layer
# - Stratify: F_skip by token difficulty quintile
```

### A.4 Key Implementation Details

**Layer norm:** GPT-2 applies a final LayerNorm (`model.transformer.ln_f`) before the LM head. We MUST apply this to intermediate hidden states before projecting through the LM head, otherwise the logits will be poorly scaled.

**Tokenization:** Use non-overlapping windows of 512 tokens from WikiText-2 validation. Skip empty articles. Total tokens needed: 20 * 512 = 10,240 (WikiText-2 validation has ~36K tokens).

**Memory:** Hidden states for all 12 layers at 512 tokens: 12 * 512 * 768 * 4 bytes = 18 MB. Trivial.

**LM head projection:** 512 * 768 * 50,257 multiplies per layer = ~20B FLOPs per layer. At ~10 GFLOPS on CPU, this is ~2 seconds per layer, 24 seconds per sequence, 480 seconds for 20 sequences. **This is the bottleneck.**

**Optimization:** Compute only argmax, not full softmax. Use `logits.argmax(dim=-1)` which only needs a single pass, not the full softmax computation. For confidence, compute only `logits.max(dim=-1)` and apply softmax only to the top-k (or approximate with logit value).

**Revised runtime estimate:** ~8-10 minutes for 20 sequences.

### A.5 Success and Kill Criteria

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| **Success** | F_skip(8) >= 0.30 | Prediction validated |
| **Strong success** | F_skip(8) >= 0.50 | Prediction validated, adaptive compute ceiling is high |
| **Weak result** | F_skip(8) = 0.15-0.30 | GPT-2 small may be too shallow; effect likely stronger in deeper models |
| **Failure** | F_skip(8) < 0.15 | Prediction falsified at this model scale |
| **Kill: too slow** | First sequence takes >3 min | Reduce to 256-token sequences or 10 sequences |
| **Kill: no signal** | First 5 sequences show F_skip(8) within 2% of F_skip(1) | No layer stratification; abort |

### A.6 What We Learn

| Outcome | Interpretation | Implication for First-Principles Framework |
|---------|---------------|-------------------------------------------|
| F_skip(8) ≈ 0.40 | Prediction accurate | Framework gives correct quantitative predictions |
| F_skip(8) ≈ 0.15 | Prediction optimistic for small models | Framework may only apply at scale (>32 layers) |
| F_skip(8) ≈ 0.70 | Prediction conservative | GPT-2 small has massive layer redundancy |
| No correlation between confidence and early matching | Fundamental prediction wrong | Layers don't specialize by difficulty in GPT-2 |

### A.7 Red Team

**What could go wrong (technical):**
- The LM head projection dominates runtime → mitigate by computing argmax only
- Final LayerNorm missing from intermediate projections → explicit check in code
- WikiText-2 has unusual token distribution (many rare tokens) → also test on simple English text

**What existing paper already showed this:**
- Elbayad et al. 2020: measured layer-wise confidence in BERT (encoder, not decoder)
- Schuster et al. 2022 (CALM): measured per-layer exit for T5 and GPT-like models
- Our experiment is a replication with GPT-2 small and an explicit comparison to theoretical predictions

**What wouldn't transfer to larger models:**
- The absolute F_skip values will differ (likely higher for deeper models)
- The correlation between confidence and layer importance should transfer (fundamental property)

---

## Experiment B: Information Gain Per Training Sample

### B.1 Hypothesis

**Prediction from first-principles analysis:** Training samples vary ~10x in information content. Selecting the top-k samples by information (measured as model loss) should dramatically outperform random selection of the same size.

**Specific prediction:** Fine-tuning DistilBERT on the top 10% of SST-2 samples (ranked by initial loss) should achieve >85% accuracy, while random 10% achieves ~80% and bottom 10% achieves ~75%.

**Published baseline (Sorscher et al. 2022):** On CIFAR, top-30% by difficulty matches full-dataset performance. We predict a similar pattern for NLP classification.

### B.2 Mathematical Framework

Information content of sample x_i for model theta:

```
I(x_i; theta) = -log P(y_i | x_i; theta)  = loss(x_i)
```

At initialization (or early training), loss varies across samples. The distribution of losses is typically:
```
P(loss > L) ~ L^{-alpha}    with alpha ≈ 1.2 - 2.0
```

For a power-law distribution with alpha=1.5:
- Top 10% by loss contains ~45% of total information
- Bottom 10% by loss contains ~2% of total information
- Random 10% contains ~10% of total information

**Predicted accuracy ordering:** top-10% >> random-10% >> bottom-10%

### B.3 Method

```python
# PSEUDOCODE — experiment_b_data_curation.py

import torch
import numpy as np
from transformers import (DistilBertForSequenceClassification,
                         DistilBertTokenizer, Trainer, TrainingArguments)
from datasets import load_dataset

# 1. Load model and SST-2
model_name = 'distilbert-base-uncased'
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
dataset = load_dataset('glue', 'sst2')

# Tokenize
def tokenize(examples):
    return tokenizer(examples['sentence'], truncation=True,
                     padding='max_length', max_length=128)

train_data = dataset['train'].map(tokenize, batched=True)
val_data = dataset['validation'].map(tokenize, batched=True)

# 2. Phase 1: Score samples by loss
# Fine-tune for 1 epoch to get non-trivial per-sample losses
scorer_model = DistilBertForSequenceClassification.from_pretrained(
    model_name, num_labels=2)

# Train for 1 epoch
trainer = Trainer(
    model=scorer_model,
    args=TrainingArguments(
        output_dir='./scorer',
        num_train_epochs=1,
        per_device_train_batch_size=32,
        learning_rate=2e-5,
    ),
    train_dataset=train_data,
)
trainer.train()

# Compute per-sample loss
per_sample_losses = []
for sample in train_data:
    with torch.no_grad():
        outputs = scorer_model(**{k: torch.tensor([sample[k]])
                                  for k in ['input_ids', 'attention_mask']},
                               labels=torch.tensor([sample['label']]))
        per_sample_losses.append(outputs.loss.item())

# 3. Phase 2: Select subsets
losses = np.array(per_sample_losses)
n = len(losses)

# Sort by loss (high = hard = high information)
sorted_indices = np.argsort(losses)[::-1]  # descending

top_10pct = sorted_indices[:n//10]
bottom_10pct = sorted_indices[-n//10:]
random_10pct = np.random.choice(n, n//10, replace=False)

subsets = {
    'top_10pct': top_10pct,
    'bottom_10pct': bottom_10pct,
    'random_10pct': random_10pct,
    'full': np.arange(n),
}

# 4. Phase 3: Fine-tune on each subset, evaluate
results = {}
for name, indices in subsets.items():
    for seed in [42, 123, 456]:
        model = DistilBertForSequenceClassification.from_pretrained(
            model_name, num_labels=2)

        subset = train_data.select(indices)

        trainer = Trainer(
            model=model,
            args=TrainingArguments(
                output_dir=f'./{name}_{seed}',
                num_train_epochs=3,
                per_device_train_batch_size=32,
                learning_rate=2e-5,
                seed=seed,
            ),
            train_dataset=subset,
            eval_dataset=val_data,
        )
        trainer.train()
        eval_result = trainer.evaluate()
        results[f'{name}_seed{seed}'] = eval_result['eval_accuracy']

# 5. Report
for name in subsets:
    accs = [results[f'{name}_seed{s}'] for s in [42, 123, 456]]
    print(f"{name}: {np.mean(accs):.3f} ± {np.std(accs):.3f}")
```

### B.4 Key Implementation Details

**Scorer phase:** We train for 1 epoch (not 0) because at epoch 0 the model is random and all losses are similar (~log(2) = 0.693). After 1 epoch, the model has learned the easy samples, and high-loss samples are genuinely harder.

**Batch scoring:** Instead of per-sample forward passes, use a DataLoader with batch_size=128 to score all samples efficiently. This should take ~30 seconds.

**SST-2 size:** 67,349 training samples. Top 10% = 6,735 samples. Fine-tuning on 6,735 samples for 3 epochs with batch_size=32 = ~630 steps ≈ 30 seconds on CPU.

**Memory:** DistilBERT is 66M parameters = ~260MB. Fits comfortably in CPU memory with room for data.

**Runtime estimate:**
1. Scoring phase (1 epoch train + full eval): ~2 minutes
2. Each subset fine-tune (3 epochs): ~30 seconds for 10% subsets, ~5 minutes for full
3. 4 subsets * 3 seeds = 12 runs: ~(3*30s + 3*30s + 3*30s + 3*300s) = ~20 minutes

**Total: ~22 minutes.** Within budget.

### B.5 Success and Kill Criteria

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| **Success** | top_10% acc > random_10% acc by >5pp | Information-based curation works |
| **Strong success** | top_10% acc > 85% (vs full ~90%) | Top 10% captures most information |
| **Failure** | top_10% ≈ random_10% (within 2pp) | Loss at epoch 1 isn't predictive of information |
| **Reverse** | top_10% < random_10% | High-loss = mislabeled/noise, not information |
| **Kill: baseline bad** | Full-dataset accuracy < 85% | Model/data loading broken |
| **Kill: too slow** | Scoring phase takes > 10 min | Reduce to 50% of training data |

### B.6 What We Learn

| Outcome | Interpretation | Implication |
|---------|---------------|-------------|
| top_10% ≈ 87%, random ≈ 81% | 6pp gap confirms information-based curation | Sorscher et al. finding transfers to NLP |
| top_10% ≈ 82%, random ≈ 81% | No meaningful gap | Either SST-2 is too easy or epoch-1 loss is a poor scorer |
| top_10% ≈ 78%, random ≈ 81% | High-loss = noise | Need robust information metrics (e.g., loss variance across epochs) |
| All subsets > 87% | SST-2 is saturated | 10% of ANY subset is enough; try harder task |

### B.7 Red Team

**What could go wrong (technical):**
- DistilBERT on CPU may be slower than estimated if HuggingFace Trainer has overhead → use manual training loop as fallback
- SST-2 validation set is small (872 samples) → accuracy estimates have ~2-3pp noise

**What existing paper already showed this:**
- Sorscher et al. 2022: exact same method on CIFAR. We're replicating on NLP.
- DCLM 2024: data quality scoring (different method, same principle)
- Our experiment is an explicit cross-domain replication

**What wouldn't transfer to larger models:**
- The absolute accuracy numbers don't transfer
- The RELATIVE ordering (high-info > random > low-info) should transfer universally
- For pretraining (vs fine-tuning), the loss distribution is different; results may not apply directly

**Kill criteria:**
- If baseline full-dataset accuracy < 85%: abort (something is broken)
- If first seed of each condition shows no ordering: likely no effect, run remaining seeds to confirm, then kill

---

## Experiment C: KV Cache Compression via Attention Sparsity Analysis

### C.1 Hypothesis

**Prediction from first-principles analysis:** ~90-96% of attention entries in GPT-2 small are effectively zero (adjusting the 98.5% estimate for 8K context down to GPT-2's 1K context).

**Derived prediction:** The effective number of attended positions per query is:
```
n_effective = 2^{H(attention)} ≈ 32-128 positions
```

out of 512 total positions per sequence. This implies 75-94% of KV entries could be evicted without significant quality loss.

### C.2 Mathematical Framework

For each attention head h at layer l, position i:

**Attention distribution:** a_{i,j}^{l,h} = softmax(q_i^T k_j / sqrt(d_k))

**Entropy:** H_i^{l,h} = -sum_j a_{i,j} * log2(a_{i,j})

**Effective positions:** n_eff = 2^{H_i}

**Sparsity at threshold tau:** S(tau) = fraction of entries with a_{i,j} < tau

**Cumulative weight of top-k:** CW(k) = sum of top-k attention weights

The first-principles prediction:
```
Mean H across all heads ≈ 5-7 bits
Mean n_eff ≈ 32-128
Mean S(0.01) ≈ 0.90-0.96
```

### C.3 Method

```python
# PSEUDOCODE — experiment_c_kv_sparsity.py

import torch
import numpy as np
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from datasets import load_dataset

# 1. Load model
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model.eval()

# 2. Process WikiText-2 sequences
dataset = load_dataset('wikitext', 'wikitext-2-raw-v1', split='validation')

# Tokenize into 512-token chunks
all_tokens = tokenizer.encode(full_text)
sequences = [all_tokens[i:i+512] for i in range(0, len(all_tokens)-512, 512)]

# 3. Extract attention matrices
all_attention_stats = []

for seq_idx, seq in enumerate(sequences[:20]):
    input_ids = torch.tensor([seq])

    with torch.no_grad():
        outputs = model(input_ids, output_attentions=True)

    # outputs.attentions is a tuple of 12 tensors, each [1, 12, 512, 512]
    for layer_idx, attn in enumerate(outputs.attentions):
        attn = attn[0]  # [12, 512, 512] — 12 heads

        for head_idx in range(12):
            a = attn[head_idx]  # [512, 512]

            # Causal mask: only lower triangle is valid
            # For position i, attention is over positions 0..i

            for pos in [64, 128, 256, 511]:  # Sample positions
                row = a[pos, :pos+1]  # Valid attention weights

                # Entropy
                row_nonzero = row[row > 1e-10]
                entropy = -(row_nonzero * torch.log2(row_nonzero)).sum().item()

                # Effective positions
                n_eff = 2 ** entropy

                # Sparsity at various thresholds
                s_001 = (row < 0.01).float().mean().item()
                s_0001 = (row < 0.001).float().mean().item()

                # Cumulative top-k weight
                sorted_row, _ = row.sort(descending=True)
                cum_weight = sorted_row.cumsum(0)
                # k for 90% of weight
                k_90 = (cum_weight < 0.9).sum().item() + 1
                k_95 = (cum_weight < 0.95).sum().item() + 1
                k_99 = (cum_weight < 0.99).sum().item() + 1

                all_attention_stats.append({
                    'layer': layer_idx,
                    'head': head_idx,
                    'position': pos,
                    'context_length': pos + 1,
                    'entropy': entropy,
                    'n_effective': n_eff,
                    'sparsity_1pct': s_001,
                    'sparsity_01pct': s_0001,
                    'k_for_90pct': k_90,
                    'k_for_95pct': k_95,
                    'k_for_99pct': k_99,
                })

# 4. Analysis
# - Distribution of entropy across heads/layers
# - Mean sparsity at each threshold
# - Per-head characterization (sparse vs broad)
# - Layer-wise trends
# - Cumulative weight curves (how many entries capture 90/95/99% of weight)
```

### C.4 Key Implementation Details

**Causal attention:** GPT-2 uses causal masking. Position i attends to positions 0 through i only. For position 0, there's only 1 entry (self-attention = 1.0, entropy = 0). For position 511, there are 512 entries. We sample at positions 64, 128, 256, 511 to capture the range.

**Memory:** `output_attentions=True` returns attention matrices for all layers. For 512-token sequences: 12 layers * 12 heads * 512 * 512 * 4 bytes = 150 MB per sequence. Fine for one at a time.

**Runtime:** Forward pass with attention output for 512 tokens: ~200-400ms. Statistics computation per sequence: ~100ms. Total for 20 sequences: ~10 seconds for forward passes, plus analysis time.

**Total estimated runtime: 5-10 minutes including plotting.**

### C.5 Simulated Eviction Experiment

After characterizing attention sparsity, simulate what happens when KV entries are evicted:

```python
# For each sequence, for each layer:
# 1. Get original output logits
# 2. Mask attention to keep only top-k entries per row
# 3. Recompute output with masked attention
# 4. Compare predictions

# This requires modifying the attention computation, which is harder
# with HuggingFace's API.

# ALTERNATIVE: Approximate by measuring how much the output changes
# when we zero out low-attention KV entries in the attention matrix
# and renormalize.

# For each retention rate r in [0.01, 0.05, 0.10, 0.20, 0.50]:
#   Keep only top r*n entries in each attention row
#   Renormalize to sum to 1
#   Compute modified attention output
#   Compare to original output (cosine similarity)
```

**Implementation note:** This is harder than it looks because HuggingFace doesn't expose an easy API for modifying attention mid-forward-pass. Options:
1. Extract attention weights, modify, and recompute attention output manually
2. Use `attn_weights` parameter if available
3. Just report the sparsity statistics without simulating eviction

**Decision:** Start with sparsity analysis only (Phase 1). If results are interesting and time permits, add simulated eviction (Phase 2). The sparsity analysis alone validates the first-principles prediction.

### C.6 Success and Kill Criteria

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| **Success** | Mean sparsity(0.01) >= 0.85 | First-principles prediction validated |
| **Strong success** | Mean sparsity(0.01) >= 0.93 | Prediction highly accurate |
| **Weak result** | Mean sparsity(0.01) = 0.70-0.85 | Prediction optimistic but direction correct |
| **Failure** | Mean sparsity(0.01) < 0.70 | First-principles estimate badly wrong |
| **Kill: memory** | OOM on attention extraction | Reduce to 256-token sequences |
| **Kill: trivial** | All heads have sparsity > 0.99 | Result is obvious, no information gained |

### C.7 What We Learn

| Outcome | Interpretation | Implication |
|---------|---------------|-------------|
| Sparsity ≈ 93% | Matches prediction | ~14x compression possible, 77x ceiling with quantization |
| Sparsity ≈ 80% | Prediction 2x optimistic | ~5x compression, still meaningful but less dramatic |
| High variance across heads | Head-specific compression needed | Uniform eviction wastes budget; per-head allocation essential |
| Sparsity increases with depth | Later layers more compressible | Progressive KV budget (more for early layers, less for late) |
| Sparsity increases with position | Longer contexts more compressible | Compression improves at scale — good news for long-context |

### C.8 Red Team

**What could go wrong (technical):**
- `output_attentions=True` may be slow or memory-intensive → fallback to extracting a single layer at a time
- Causal mask handling: attention values below the diagonal should be exactly 0, not small → verify masking

**What existing paper already showed this:**
- Clark et al. 2019: characterized GPT-2 attention head types
- Voita et al. 2019: measured head importance and pruning
- H2O 2023: measured attention sparsity for KV eviction
- Our contribution: comparison to first-principles prediction, not just measurement

**What wouldn't transfer to larger models:**
- Absolute sparsity values change with model size and context length
- The TREND (most entries carry negligible weight) should transfer and likely strengthen
- Larger models with 128-256 heads may have more specialized (sparser) heads

---

## Execution Decision Tree

```
START
│
├── Timing test: forward pass on 1 sequence (512 tokens) with GPT-2 small
│   ├── < 1 second → proceed with 20 sequences
│   ├── 1-5 seconds → proceed with 10 sequences
│   └── > 5 seconds → use DistilGPT-2 or reduce to 256 tokens
│
├── Run Experiment A (Adaptive Compute) — ~15-20 min
│   ├── Check F_skip(8) after 5 sequences
│   │   ├── F_skip(8) varies < 2% from F_skip(1) → KILL (no signal)
│   │   └── Clear signal → complete remaining 15 sequences
│   ├── Record results
│   └── Plot: F_skip vs layer, confidence vs layer, per-token scatter
│
├── Run Experiment C (KV Sparsity) — ~10 min
│   ├── Check memory after 1 sequence
│   │   ├── OOM → reduce to 256 tokens
│   │   └── OK → proceed
│   ├── Record attention statistics for 20 sequences
│   └── Plot: entropy histogram, sparsity by head/layer, cumulative weight
│
├── Run Experiment B (Data Curation) — ~20 min
│   ├── Baseline check: full SST-2 fine-tune accuracy
│   │   ├── < 85% → KILL (broken setup)
│   │   └── >= 85% → proceed
│   ├── Score all samples by epoch-1 loss
│   ├── Fine-tune 4 subsets * 3 seeds = 12 runs
│   └── Report accuracy ± std for each condition
│
└── SYNTHESIS
    ├── Compare predictions vs measurements for all 3 experiments
    ├── Compute prediction error (predicted value / measured value)
    ├── Verdict: framework validated (errors < 2x) or needs calibration
    └── Write results summary
```

---

## Runtime Budget

| Phase | Task | Estimated Time | Cumulative |
|-------|------|---------------|------------|
| 0 | Setup (install packages, load models) | 5 min | 5 min |
| 1a | Experiment A: data loading + timing test | 2 min | 7 min |
| 1b | Experiment A: full analysis (20 sequences) | 12 min | 19 min |
| 1c | Experiment A: statistics + plots | 3 min | 22 min |
| 2a | Experiment C: attention extraction (20 sequences) | 5 min | 27 min |
| 2b | Experiment C: statistics + plots | 3 min | 30 min |
| 3a | Experiment B: scoring phase (1 epoch fine-tune) | 3 min | 33 min |
| 3b | Experiment B: subset fine-tuning (12 runs) | 15 min | 48 min |
| 3c | Experiment B: evaluation + plots | 2 min | 50 min |
| 4 | Synthesis: compare predictions vs measurements | 10 min | 60 min |

**Total: ~60 minutes.** Within the 90-minute budget with margin for debugging.

---

## Package Requirements

```
torch (CPU)
transformers >= 4.30
datasets
numpy
matplotlib
scipy (for correlation statistics)
```

All available via pip. No GPU-specific packages needed.

**Model downloads:**
- `gpt2` (GPT-2 small, 124M): ~500 MB download
- `distilbert-base-uncased` (66M): ~250 MB download
- WikiText-2: ~4 MB
- SST-2 (via GLUE): ~7 MB

Total: ~760 MB. Pre-download before starting timer.

---

## Output Artifacts

### Per-Experiment Output

**Experiment A:**
- `python/experiments/plots/llm_adaptive_compute.png` — F_skip vs layer, confidence curves
- `python/experiments/plots/llm_adaptive_compute_results.json` — raw statistics
- Console output: predicted vs measured F_skip values

**Experiment B:**
- `python/experiments/plots/llm_data_curation.png` — accuracy by condition
- `python/experiments/plots/llm_data_curation_results.json` — per-seed results
- Console output: accuracy ± std for each condition

**Experiment C:**
- `python/experiments/plots/llm_kv_sparsity.png` — entropy histograms, sparsity by head
- `python/experiments/plots/llm_kv_sparsity_results.json` — per-head/layer statistics
- Console output: mean sparsity, predicted vs measured

### Synthesis Output

- `analysis/LLM_EXPERIMENTS_RESULTS.md` — comparison of predictions vs measurements
  - Table: predicted value, measured value, ratio
  - Verdict: framework validated / needs calibration / falsified
  - Lessons for future first-principles analyses

---

## Appendix: Literature References

### Experiment A (Adaptive Compute)
- Schwartz et al. 2020. "The Right Tool for the Job: Matching Model and Instance Complexities." (Early exit)
- Elbayad et al. 2020. "Depth-Adaptive Transformer." (Layer skipping in encoder)
- Schuster et al. 2022. "Confident Adaptive Language Modeling." (CALM — early exit for generation)
- Raposo et al. 2024. "Mixture of Depths." (Routing tokens to skip layers during training)

### Experiment B (Data Curation)
- Sorscher et al. 2022. "Beyond neural scaling laws: beating power law scaling via data pruning." (Core reference)
- Kumar et al. 2010. "Self-paced learning." (Curriculum by difficulty)
- Li et al. 2024. "DCLM: DataComp for Language Models." (Quality-based data curation)

### Experiment C (KV Cache Sparsity)
- Clark et al. 2019. "What Does BERT Look At?" (Attention pattern analysis)
- Voita et al. 2019. "Analyzing Multi-Head Self-Attention." (Head pruning, importance)
- Zhang et al. 2023. "H2O: Heavy-Hitter Oracle." (KV eviction by attention)
- Xiao et al. 2023. "Efficient Streaming Language Models with Attention Sinks." (StreamingLLM)
- Cai et al. 2024. "PyramidKV: Dynamic KV Cache Compression." (Per-layer KV budget)

---

## Appendix: Applying Project Retrospective Lessons

| Lesson from Retrospective | How Applied Here |
|--------------------------|-----------------|
| MATH FIRST before code | Viability analysis completed before experiment design |
| Kill early when signal is absent | Explicit kill criteria after first 5 sequences / first seed |
| Don't tune against structural barriers | Measuring structure, not optimizing parameters |
| Test beautiful ideas against boring alternatives | Each experiment includes random/naive baselines |
| Representation > tuning | We're testing whether the right MEASUREMENT reveals the phenomenon, not tuning algorithms |
| Viability analysis saves orders of magnitude of compute | This document IS the viability analysis; ~2 hours of analysis before ~1 hour of compute |
| 40-50% of compute was avoidable | Kill criteria prevent runaway experiments |
| Additive bonuses dilute selection | Not applicable (no evolutionary selection) but analogous: don't add metrics that dilute the primary signal |
| Evolution finds minimum effort | Applied to us: these experiments measure the minimum-effort phenomena (sparsity, redundancy, information distribution) |
