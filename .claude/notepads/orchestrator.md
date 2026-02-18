# Orchestrator Notepad

## Current State
31 experiments complete (2026-02-18). Echo subspace analysis done. All docs updated. Research spans self-referential optimization theory, MVSU architecture, multi-agent probes, damped meta-optimization, numerical simulation validation, and discrete observer theory with ML architecture experiments.

## Key Files
- `analysis/WHITEPAPER_DRAFT.md` — Exploratory paper (31 experiments, Sections 1-3.14)
- `analysis/FULL_SESSION_FINDINGS.md` — Comprehensive write-up (33 sections)
- `analysis/DISCRETE_OBSERVER_ML_EXPERIMENTS.md` — ML experiments (Exps 28-31): stride, dropout, attention, echo subspace
- `analysis/OBSERVER_TRANSFORMER_SPEC.md` — Complete implementation spec (now includes Tier 2.5)
- `notebooks/observer_transformer_experiments.ipynb` — Runnable Colab notebook (all tiers)
- `python/mvsu.py` — Reusable MVSU module (231 lines, pure numpy)
- `python/experiments/` — 31 experiment scripts with plots

## Experiment 31: Echo Subspace Analysis (NEW)
**Platform:** Tesla T4 GPU, full CIFAR-10, 20 epochs

**Phase 1 — Dual-channel training:**
- 817,294 params, best acc: 66.79%
- w_cross ALL negative across 4 layers (confirmed again)
- Depth gradient present (-0.32 to -0.48)

**Phase 2 — PCA of echo patterns:**
- Top-4 variance: 52% across all layers (NOT low-rank, threshold is 80%)
- Echo is high-dimensional, spread across most dims

**Phase 3 — Four-model comparison:**
| Model | Params | Best Acc | vs Baseline |
|-------|--------|----------|-------------|
| Baseline | 809,098 | 67.00% | — |
| Tier 3 (dual) | 817,294 | 67.11% | +0.11% |
| Tier 2.5 Fixed | 809,130 | 66.22% | -0.78% (FAILED) |
| Tier 2.5 Learnable | 811,178 | 67.13% | +0.13% (SUCCESS) |

**Key finding:** Tier 2.5 Learnable MATCHES Tier 3 with fewer params. The learnable rank-4 projector finds task-specific correction directions that differ from PCA's max-variance directions.

**Phase 4 — Self-similarity analysis:**
- Cross-layer similarity: 0.012 (essentially random)
- Echo is NOT self-similar. Per-layer correction required.

**Conclusions:**
1. Echo is NOT low-rank (~52% in top-4, not 80%+)
2. Echo is NOT self-similar (0.012 cross-layer similarity)
3. Tier 2.5 Learnable matches Tier 3 (67.13% vs 67.11%)
4. Tier 2.5 Fixed fails (66.22%) — PCA directions ≠ correction directions
5. "Smart eraser" hypothesis PARTIALLY confirmed: cheap projector works IF learned per-layer end-to-end

**Architecture update:** Tier 2.5 is now a validated tier. Same accuracy as Tier 3, slightly fewer params. Do NOT freeze PCA basis. Do NOT share across layers.

## Core Proven Results (Updated)
All 18 prior results hold. Add:
19. Echo is NOT low-rank (52% variance in top-4 components)
20. Echo is NOT self-similar across layers (0.012 similarity)
21. Tier 2.5 Learnable matches Tier 3 performance with rank-4 projector
22. Maximum variance ≠ maximum correction utility (PCA init helps, must learn end-to-end)

## What User Might Want Next
- Scale Tier 2.5 to larger models/datasets (ImageNet, language tasks)
- Implement two-stage architecture (MVSU + damped recurrence)
- Test whether echo subspace structure holds in other domains (NLP, audio, RL)
- Investigate why PCA directions differ from task-optimal correction directions
- Try different projector ranks (2, 8, 16) to find sweet spot

## Priority Experiments (from 3 teams, pre-Exp 31)
**Architecture team (child/ML experts):**
1. Attention head ablation — which heads matter most?
2. Layer-wise phi sweep — does optimal redundancy vary by depth?
3. Generalization to other modalities (text, audio)

**Numerical team (Feynman):**
4. MVSU for tensor decomposition errors (CP, Tucker)
5. Multi-fidelity simulation combining cheap/expensive models

**Optimization team (hobbyist/meta):**
6. Two-stage MVSU + damped recurrence (proposed but not built)
7. Online alpha estimation from w_cross dynamics

*Updated 2026-02-18 after Experiment 31.*
