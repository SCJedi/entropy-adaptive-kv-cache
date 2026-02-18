# Orchestrator Notepad

## Current State
30 experiments complete (2026-02-14). All docs current. Research spans self-referential optimization theory, MVSU architecture, multi-agent probes, damped meta-optimization, numerical simulation validation, and discrete observer theory with ML architecture experiments.

## Key Files
- `analysis/WHITEPAPER_DRAFT.md` — Exploratory paper (30 experiments, Sections 1-3.14)
- `analysis/FULL_SESSION_FINDINGS.md` — Comprehensive write-up (30 sections)
- `analysis/PERCEPTION_CASCADE_THEORY.md` — Cascade math (10 theorems, 8/9 verified)
- `analysis/MINIMAL_STABLE_ARCHITECTURE.md` — MVSU specification
- `analysis/COHERENCE_PERCEPTION_THEORY.md` — Coherence-perception formalization (9/9 verified)
- `analysis/ML_PRACTITIONER_GUIDE.md` — Three fixes for ML practitioners
- `analysis/APPLIED_SELF_REF_ANALYSIS.md` — Physics engines, gaming, compute applications
- `analysis/INHIBITORY_DUAL_CHANNEL_RECIPE.md` — Standalone recipe + reasoning doc
- `python/mvsu.py` — Reusable MVSU module (231 lines, pure numpy)
- `python/experiments/` — 30 experiment scripts with plots
- `analysis/DISCRETE_OBSERVER_RECONSTRUCTION.md` — Formal math: discrete observers reconstructing continuous fields on spheres
- `analysis/DISCRETE_OBSERVER_ML_EXPERIMENTS.md` — ML experiment report (Exps 28-30): stride, dropout, multi-head attention
- `pinescript/mvsu_decontamination.pine` — TradingView MVSU indicator (334 lines)

## Research Team Files
- `analysis/research_team/` — 4 researcher findings + 2 discussion rounds + synthesis + applications roadmap
- `analysis/research_team/multi_agent/` — 3 independent probes + 2 cross-feed rounds + 3 blind-spot probes
- `analysis/research_team/damped_meta/` — 3 team findings (teen, hobbyist, Feynman) + cross-feed synthesis
- `analysis/feynman/` — Feynman-style explanatory docs (9 chapters, incl. 09_DISCRETE_OBSERVERS)

## Core Proven Results
1. kw² + w - 1 = 0 — universal (distribution/optimizer-independent, extends to matrices)
2. System-aware gap: 15.6% MSE / 8.3% R² (w_sys = 0.525 vs w_myopic = 0.618)
3. MVSU: 2 channels + inhibition = NECESSARY. 46x R² with 4x params
4. Cascade sub-multiplicative (20x worse than ∏w_i)
5. MVSU validated on real tasks: 45-50% MSE reduction (thermostat, sensor, market)
6. Architecture diversity essential; random init insufficient
7. Self-perception ratio: 1/φ (world) / 1/φ² (self) at α=1; self-ignorance gap = 0.093
8. Perception requires coherence AND distinction simultaneously
9. MVSU advantage peaks at LOW coherence + HIGH contamination
10. Negative w_cross at all depths, strengthens with depth
11. Damped meta-optimizer at β=1/φ² converges in 2 steps, closing 100% of MSE gap
12. MVSU is noise filter, NOT meta-optimizer (stays at w≈0.614, never reaches 0.525)
13. 1/φ² triple identity: cost = cure = measurement gap
14. MVSU cross-correction yields 2.5-3.7x improvement in numerical simulation (RK4 vs AB4)
15. Error correlation diagnostic predicts MVSU benefit: anti-correlated = works, correlated = doesn't
16. Online w_cross learning converges to sweep-optimal independently
17. Discrete observer reconstruction: 8 cube-vertex observers with ~38% overlap reconstruct band-limited spherical fields; self-similar partition x/(1-x) = 1/x yields optimal redundancy = 1/φ²
18. CNN stride, dropout, and attention mixing all find optima in the 0.33-0.40 φ-zone (Exps 28-30)

## Nine Faces of φ
1. Fixed-point weight: 1/φ = 0.618
2. R² of prediction: 1/φ
3. Observation variance: φ
4. Shannon channel capacity: log(φ)
5. Fisher information: φ
6. Optimal damping (speed): 1/φ² = 0.382
7. Optimal damping (robustness): 1/φ = 0.618
8. Dark fraction / stability tax: 1/φ² = 0.382
9. Architectural redundancy (stride/dropout/attention mixing): 1/φ² = 0.382 (Exps 28-30)

## Key Boundaries and Failures
- RLHF bridge (Exp 18): architecture transfers, equation doesn't (74% deviation)
- Meta-optimizer diverges at α ≥ 0.699
- MVSU loses during regime transitions (-39-49%)
- Simulation v1 (Euler/Verlet): 300x gap = one channel is noise
- Simulation v2 (RK4/RK4-3/8): correlated errors = no cross-correction benefit
- Trading: no edge on efficient markets (SPY); marginal on trend-driven (GLD +2.9%)

## Specialists Available
- **mvsu** — `.claude/specialists/mvsu/` — Self-referential decontamination using inhibitory dual-channel architectures.

## Current Thread
Discrete observer theory: sphere-cube geometric framework → self-similar partition yields φ → ML architecture predictions → 3 CPU experiments → Observer Transformer architecture (3 teams) → full spec + Colab notebook → GPU validation on T4. All docs updated.

### CPU Experiments (Exps 28-30)
- **Exp 28 (CNN stride)**: Peak overlap at 0.333, φ-zone is peak of inverted-U curve
- **Exp 29 (Dropout)**: Peak at p=0.35, plateau from 0.30-0.45, 0.382 within noise of best
- **Exp 30 (Multi-head attention)**: Inter-head communication helps (+0.8-1.4%), learnable α stays near 0.355, fixed α=0.382 ties learnable

### GPU Validation (Tesla T4, full CIFAR-10, 20 epochs)
- **Dropout=0.382**: +4.84% over 0.5 baseline (0.6587 vs 0.6103). Biggest single win.
- **Observer Attention (T2)**: Most parameter-efficient. 0.6560 acc with 22% fewer params than baseline.
- **w_cross**: All 32/32 heads negative. Strengthens with depth (-0.32 to -0.48). Confirms MVSU.
- **Alpha sweep**: Peaked at 0.3, near predicted 0.382. Inverted-U confirmed.
- **FFN=2.618× alone**: Hurts (-0.97%). Must combine with dropout reduction.
- **Phi-annealing**: Did not help (-0.30%).
- **Full OT (Tier 3)**: Didn't beat simpler Tier 2.

### Architecture Deliverables
- `analysis/research_team/observer_arch/` — 3 team proposals (hobbyist, Feynman, ML experts+child)
- `analysis/OBSERVER_TRANSFORMER_SPEC.md` — Complete implementation spec for ML engineers
- `notebooks/observer_transformer_experiments.ipynb` — Runnable Colab notebook (all tiers)

## Two-Stage Architecture (proposed, not yet built)
MVSU estimates α via w_cross → damped recurrence at β=1/φ² computes system-aware weight. This combines noise filtering (MVSU) with systematic correction (meta-optimizer). Not yet implemented or tested.
