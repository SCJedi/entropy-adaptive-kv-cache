# Evolutionary ML Research: From Cell Soups to KV Cache Compression

## TL;DR

**Key Finding: Entropy-Adaptive KV Cache Compression**

Allocating KV cache budget per attention head based on entropy outperforms uniform strategies by 2.6x (BLEU) at 2x compression. Simple, zero-parameter, calibrate-once.

| Strategy | BLEU | ROUGE-L | Token Match | Perplexity Ratio |
|---|---|---|---|---|
| Entropy-adaptive 2x | 0.407 | 0.542 | 33.3% | 1.13x |
| Sink+recent 2x | 0.158 | 0.227 | 6.2% | 2.52x |
| Entropy-adaptive 5x | 0.158 | 0.287 | 9.0% | 1.88x |
| Sink+recent 5x | 0.080 | 0.110 | 3.3% | 11.25x |

Entropy-adaptive at **5x compression** roughly matches sink+recent at **2x compression** -- meaning you can compress 2.5x more aggressively for the same quality. Head entropy profiles are stable across inputs (rank correlation 0.975), so calibration is a one-time cost.

## The Research Arc

This repository documents a 20+ phase research journey from evolving cell soups to practical ML insights. It started with golden cascade predictors in open thermodynamic systems and ended with validated LLM inference optimization. The research ran over 18 days (Feb-Mar 2026) with roughly 10-15 hours of compute.

The honest summary: our primary hypotheses about self-organizing computation failed. But the failures were instructive, and the pivots they forced led to genuinely useful findings about LLM efficiency.

### Validated Findings

- **Entropy-adaptive KV cache compression**: 23-37 percentage point improvement over best uniform strategy across practical compression ratios (2-10x). Per-head budget allocation exploits the 300x entropy range across attention heads. ([Paper](analysis/KV_CACHE_PAPER.md) | [Confirmation](analysis/KV_CACHE_CONFIRMATION.md))
- **~29% of GPT-2 tokens can skip the last 4 layers** with <2% accuracy loss (adaptive compute). ([Findings](analysis/LLM_EFFICIENCY_FINDINGS.md))
- **85% of attention entries receive <1% weight** -- massive structural sparsity. ([Findings](analysis/LLM_EFFICIENCY_FINDINGS.md))
- **High-loss training samples are noise, not information** -- removing the top 20% highest-loss samples improves accuracy by 0.3%. ([Findings](analysis/ML_INSIGHTS_FINDINGS.md))

### Theoretical Contributions

- First-principles analysis of LLM efficiency from information theory. ([Document](analysis/LLM_FIRST_PRINCIPLES.md))
- Composition thesis: when abstraction beats enumeration, framed via Kolmogorov complexity. ([Document](analysis/LOGIC_PRIMITIVES_VS_ABSTRACTION.md))
- Comprehensive falsification of golden ratio / golden cascade as ML primitives. ([Retrospective](analysis/PROJECT_RETROSPECTIVE.md))

### Methodology Lessons

- **Math first, compute second**: 22 seconds of mathematical viability analysis saved 145 minutes of doomed experiments. ([Cascade Component Math](analysis/CASCADE_COMPONENT_MATH.md))
- **Evolution consistently finds minimum-effort solutions**: organisms evolve toward linear functions and minimum connections, avoiding complexity unless forced.
- **Representation determines search efficiency**: switching from register machines to computational graphs yielded a 10^23x improvement in evolutionary search efficiency. ([Phase 20 Findings](analysis/PHASE20_FINDINGS.md))

### What Failed (and Why It Matters)

- **Surprise-minimization does not produce useful hidden representations**: 43.9% accuracy = random features.
- **The golden ratio (0.618) is not a special decay rate**: 0.9 beats 0.618 and is 50x more stable.
- **Golden cascade cells do not outperform plain tanh**: plain tanh equals or beats cascade in every test.
- **Open thermodynamic cell soup cannot achieve hierarchical computation**: circuit half-life (50-76 steps) < optimization time (200+ steps), a structural 4x deficit.

These are documented honestly because negative results save other researchers time.

## Key Documents

### KV Cache & LLM Efficiency (the publishable work)

| Document | Description |
|---|---|
| [KV_CACHE_PAPER.md](analysis/KV_CACHE_PAPER.md) | Formal paper: entropy-adaptive KV cache compression method and results |
| [KV_CACHE_CONFIRMATION.md](analysis/KV_CACHE_CONFIRMATION.md) | Independent confirmation on text generation with BLEU/ROUGE metrics |
| [KV_CACHE_FINDINGS.md](analysis/KV_CACHE_FINDINGS.md) | Initial experimental findings and head entropy analysis |
| [LLM_FIRST_PRINCIPLES.md](analysis/LLM_FIRST_PRINCIPLES.md) | First-principles LLM efficiency analysis from information theory |
| [LLM_EFFICIENCY_FINDINGS.md](analysis/LLM_EFFICIENCY_FINDINGS.md) | Layer skip, attention sparsity, and data curation experiments |

### Research Arc & Retrospectives

| Document | Description |
|---|---|
| [RESEARCH_ARC_COMPLETE.md](analysis/RESEARCH_ARC_COMPLETE.md) | Full chronological narrative of all 20+ phases |
| [PROJECT_RETROSPECTIVE.md](analysis/PROJECT_RETROSPECTIVE.md) | Honest retrospective with lessons learned |
| [ML_INSIGHTS_FINDINGS.md](analysis/ML_INSIGHTS_FINDINGS.md) | 6 practical ML tests: 2 survived, 4 failed |
| [LOGIC_PRIMITIVES_VS_ABSTRACTION.md](analysis/LOGIC_PRIMITIVES_VS_ABSTRACTION.md) | When composition beats enumeration (Kolmogorov complexity framework) |

### Theoretical Foundations

| Document | Description |
|---|---|
| [GOLDEN_CASCADE_PAPER.md](analysis/GOLDEN_CASCADE_PAPER.md) | Original golden cascade mathematical framework |
| [ML_PRACTITIONER_GUIDE.md](analysis/ML_PRACTITIONER_GUIDE.md) | Practical guide distilling actionable findings |

For a complete index of all ~120 analysis documents, see [analysis/INDEX.md](analysis/INDEX.md).

## Reproducing Results

### Requirements

```bash
pip install torch torchvision transformers datasets nltk rouge-score matplotlib numpy
```

Python 3.8+ required. GPU optional (all experiments run on CPU; the KV cache experiments took ~10 minutes total on CPU).

### Key Experiments

**KV Cache Compression** (the main finding):
```bash
# Run the full KV cache analysis (~6 minutes on CPU)
python python/experiments/kv_cache_compression.py

# Run the confirmation test with text generation (~4 minutes on CPU)
python python/experiments/kv_cache_confirm.py
```

**LLM Efficiency Analysis**:
```bash
python python/experiments/llm_efficiency.py
```

**ML Insights Tests** (surprise-gated LR, settling, etc.):
```bash
python python/experiments/ml_insights_test.py
```

**Cell Soup Evolution** (the original research line):
```bash
python python/experiments/cell_soup.py
python python/experiments/graph_soup.py
```

Results are saved to `python/experiments/plots/` as JSON data and PNG plots.

## Repository Structure

```
analysis/                    -- Research documents, findings, team discussions (~120 files)
  KV_CACHE_PAPER.md          -- Formal KV cache compression paper
  KV_CACHE_CONFIRMATION.md   -- Confirmation results
  PROJECT_RETROSPECTIVE.md   -- Full project retrospective
  LLM_FIRST_PRINCIPLES.md    -- First-principles LLM analysis
  RESEARCH_ARC_COMPLETE.md   -- Complete research arc narrative
  PHASE{N}_FINDINGS.md       -- Per-phase experiment findings
  TEAM_CONVERSATION_V{N}.md  -- Team discussion transcripts (V1-V21)
  INDEX.md                   -- Complete index of all documents

python/experiments/          -- All experiment code
  kv_cache_compression.py    -- KV cache sparsity and strategy comparison
  kv_cache_confirm.py        -- Confirmation on actual text generation
  llm_efficiency.py          -- Layer skip, attention sparsity, data curation
  ml_insights_test.py        -- 6 practical ML insight tests
  graph_soup.py              -- Evolutionary graph computation
  cell_soup.py               -- Original cell soup evolution
  cell_soup_consensus.py     -- Consensus neural network
  cascade_components.py      -- Cascade component ML tests
  signal_conditioner_test.py -- Signal conditioning tests
  plots/                     -- All experiment output (JSON + PNG)
```

## The Journey (for the curious)

This project followed a winding path. Here is the compressed timeline:

**Phases 1-3: Mathematical Foundation.** Built a 3-cell golden cascade system. Beautiful math -- all eigenvalues are phi-powers, exact phase transitions at {1/phi, phi, phi^2}, conserved quantities. Mathematical elegance does not imply practical utility.

**Phases 4-8: Cell Soup Evolution.** Placed golden cascade cells in an open thermodynamic environment with food, metabolism, birth, and death. Evolution works (103 births, 63 deaths). Within-lifetime learning fails in every form tested. Evolution IS the learning algorithm.

**Phases 9-14: The Circuit Half-Life Wall.** Connection inheritance was the single biggest breakthrough (860% improvement). But hierarchical (L2+) computation remained impossible: cell turnover destroys multi-layer circuits faster than they can form. Seven phases of increasingly complex mechanisms failed to change this ratio by more than 2x.

**Phases 15-17: Organism-Level Selection.** Shifted from individual cells to 4-cell organisms. Evolution perfectly learns linear functions (r=0.9997) but never discovers nonlinear ones. Gradient control proves the architecture CAN compute nonlinear functions -- the bottleneck is evolutionary search, not architecture.

**Phases 18-20: Graph Soup.** Switched from register machines to computational graphs. This one representation change improved search efficiency by 10^23x. Evolution discovers ADD, MULTIPLY, ABS. MI-based fitness kills degenerate solutions. The biggest lesson of the project: **representation matters more than algorithm**.

**Phase A: Consensus Network.** Attempted to use golden cascade dynamics as an ML component. Surprise-minimization produces random features (43.9% accuracy). The golden cascade is mathematically interesting but computationally inert for ML.

**ML Insights Tests.** Extracted 6 candidate insights from the research, tested rigorously. 2 survived: surprise-gated learning rate (stabilizes training) and settling for stateful neurons (free accuracy boost). 4 failed.

**Cascade Component Tests.** Mathematical viability analysis (22 seconds) eliminated 3 of 5 proposed components before any compute was spent. The survivors performed at parity with baselines.

**LLM First-Principles Analysis.** Applied lessons from the project (representation matters, composition thesis, minimum-effort principle) to analyze LLM efficiency from information theory. Identified structural waste in dense attention, uniform compute-per-token, and training FLOP allocation.

**KV Cache Compression.** The analysis predicted that attention head entropy should vary widely. It does -- by 300x. This led to entropy-adaptive KV cache compression, which outperforms uniform strategies by 23-37 percentage points. Confirmed on text generation with 2.6x BLEU improvement. The most practically valuable finding of the entire project, discovered in the final phase.

## Citation

If you use the entropy-adaptive KV cache compression idea:

```bibtex
@misc{vacuum_physics_kv_cache_2026,
  title={Entropy-Adaptive KV Cache Compression: Per-Head Budget Allocation for Efficient LLM Inference},
  author={Eric L. and Claude},
  year={2026},
  howpublished={\url{https://github.com/ericl/vacuum_physics}},
  note={Experimental validation on GPT-2 small. See analysis/KV\_CACHE\_PAPER.md}
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*This research was conducted collaboratively between a human researcher and Claude (Anthropic). The repository documents the full arc honestly, including the many things that didn't work. Research is a search process; most paths are dead ends. The value is in what you learn from them.*
