# Learnings: MVSU Specialist

Append-only. Max 200 lines. Archive older entries to archive/ when approaching limit.

## 2026-02-11 — Specialist initialized

**Core framework established:** 17 experiments completed, RLHF bridge test validated, 3 real continuous tasks verified.

**Key learning 1: Architecture principle transfers, quantitative equation does not**
- The self-consistency equation kw² + w - 1 = 0 is exact for linear case (k=1, w = 1/φ = 0.618)
- For nonlinear activations: equation form survives, specific values change (ReLU: w ≈ 0.394)
- For RLHF (nonlinear): w_cross learned to -0.6 to -0.8 (much stronger than -0.26 from linear theory)
- **Implication:** Use the architectural principle (dual + inhibition), let w_cross learn. Don't hard-code values from linear theory.

**Key learning 2: w_cross reliably converges to negative values**
- Linear toy setting: -0.26 typical
- RLHF setting: -0.6 to -0.8
- Real continuous tasks: -0.13 to -0.23
- All depths tested (1-layer, 2-layer, 3-layer): negative at every layer
- Deeper layers: stronger negative weights (layer 3 in 3-layer network: -0.189 vs layer 1: -0.083)
- **Implication:** Negative w_cross is a robust universal pattern across settings. If w_cross stays positive or near zero, something is wrong (no contamination, or models too similar).

**Key learning 3: Same-seed diversity FAILS for linear models**
- Experiment 16 tested same-architecture different-seed on three real tasks
- Result: -53% to -83% performance degradation vs single model (WORSE than no MVSU at all)
- Reason: linear loss landscape has single basin, different inits converge to same optimum
- Both "eyes" end up seeing identically — zero parallax
- **Implication:** For linear components, architectural diversity is mandatory. Different seeds provide no benefit and actively harm.

**Key learning 4: Architecture-split provides "free diversity"**
- Linear + MLP on same three tasks: +45-50% improvement
- Different inductive biases create different error patterns even at convergence
- Both models see full data, full features (no competence penalty)
- **Implication:** The parallax-competence tradeoff is solved by architectural diversity. Feature-split and data-split cripple individual models; architecture-split does not.

**Key learning 5: MVSU advantage beats ensemble average by +0.027 in RLHF**
- Single model: baseline
- Ensemble average (w_cross = 0): +0.010
- MVSU (learned w_cross): +0.037
- The +0.027 gap is specifically from inhibition (not just capacity)
- **Implication:** Always run the ensemble baseline. If MVSU ≈ ensemble, inhibition isn't helping (contamination may not be uniform/additive).

**Key learning 6: Classification with structured errors is a validated failure case**
- Experiment 12: pseudo-labeling on digits classification
- Contamination confirmed (accuracy degrades with more pseudo-label rounds)
- All fixes failed: over-relaxation, dual-model cross-labeling, forced viewpoint diversity
- Reason: class-structured errors (confuse 3 with 8) violate uniform contamination assumption
- **Implication:** Do not recommend MVSU for classification tasks. Escalate to parent and suggest class-aware methods instead. Cite Experiment 12.

**Key learning 7: Sub-multiplicative cascade compounds faster than predicted**
- 7-stage biological cascade: product of per-stage R² predicts 0.16, actual R² is 0.008 (~20x worse)
- Reason: each stage's AR(1) output (temporally correlated) makes next stage's decontamination harder
- Penalty compounds through cascade
- Binocular stages provide ~8x improvement over monocular (R² = 0.065 vs 0.008)
- **Implication:** Multi-stage ML pipelines (retrieval→ranking→generation, iterative RLHF with multiple RM updates) may degrade much worse than per-stage analysis suggests. Each RM update cycle is a new self-referential stage.

**Key learning 8: MVSU requires only 2 components (Tier 1)**
- Dual channels (N ≥ 2): removal causes 97.4% collapse
- Inhibitory cross-connections (w_cross < 0): removal causes 97.4% collapse
- These two are inseparable: dual channels WITHOUT inhibition perform identically to monocular
- Predictive coding (Tier 2): adds 60% improvement but not structurally necessary (system stable without)
- External grounding (Tier 3): redundant when Tier 1-2 present (actually hurts by 0.6%)
- **Implication:** The minimal prescription is simple: two architecturally different channels + learned negative cross-weight. Everything else is optimization on top.

**Key learning 9: w_cross is a contamination diagnostic**
- w_cross < -0.1: contamination detected and being removed
- w_cross ≈ 0: either no contamination OR models too similar (try more architectural diversity)
- w_cross < -0.6: heavy contamination (RLHF level)
- Magnitude indicates severity of contamination overlap
- **Implication:** Use w_cross trajectory as primary success signal. It tells you if the feedback loop is real and how severe it is.

**Key learning 10: Improvement scales with α (contamination strength)**
- Thermostat task: +19% at α=0, +55% at α=1.0
- MVSU advantage increases with feedback strength
- At low α: MVSU ≈ ensemble (little contamination to remove)
- At high α: MVSU advantage maximizes
- **Implication:** If possible, test across multiple α values. The scaling pattern confirms whether contamination is the bottleneck.

**Key learning 11: Evidence tiers matter for credibility**
- Proven: 17+ experiments, robust across distributions/optimizers
- Verified: tested in specific experiments, clear results
- Established: theory + partial experiments
- Conjectured: theoretical prediction, untested or context-dependent
- **Implication:** Always cite evidence tier when making recommendations. Overclaiming hurts credibility. Honest null results strengthen it.

**Key learning 12: T=2 depth is signal-dependent, not universal**
- Original finding: T=2 (balanced) beats both deep (T=10) and wide (T=1)
- Follow-up: T=2 wins for structured signals, T=1 wins for stochastic signals
- What's robust: depth beyond T=2 is always wasteful (deep is always worst)
- **Implication:** For continuous feedback systems, start with T=1 or T=2. Don't go deeper. More integration steps compound contamination without adding decontamination capability.

**Key learning 13: The 8.3% gap is for k=1, α=1 specifically**
- Myopic optimum: w = 1/φ = 0.618, R² = 0.618
- System-aware optimum: w = 0.525, R² = 0.670
- Gap: 8.3% in explained variance
- This is the theoretical maximum for the simplest case
- For k > 1 (multiple neighbors), the gap changes
- For nonlinear systems, the exact percentage is unknown
- **Implication:** Cite 8.3% as "toy setting result" not "guaranteed improvement at scale". The qualitative finding (myopic ≠ optimal) is robust; the quantitative value is setting-specific.

**Key learning 14: Honest failures strengthen the framework**
- Experiment 12 (pseudo-labeling): all fixes failed, documented clearly
- Experiment 13 (staged binocular): feature-split and data-split failed
- Experiment 16: same-seed diversity failed
- These null results define the boundary conditions precisely
- **Implication:** When MVSU doesn't apply, say so clearly. Cite the relevant failure experiment. This builds trust for the cases where MVSU does work.

**Key learning 15: The three baselines are mandatory**
1. Single model (parameter-matched: 2x hidden units) — controls for capacity
2. Ensemble average (w_cross = 0) — controls for diversity without inhibition
3. MVSU (learned w_cross) — the full method
- Without these, you can't separate capacity effects from decontamination effects
- **Implication:** Always specify all three baselines in recommendations. If user can only run one comparison, make it ensemble vs MVSU (this isolates the inhibition benefit).

**Key learning 16: Practical recipe works for continuous tasks**
- Thermostat control: real feedback (heater responds to prediction), +50% improvement
- Sensor calibration: real drift (auto-calibration feedback), +45% improvement
- Market microstructure: real impact (trades move prices), +47% improvement
- Linear + MLP pairing works well for all three
- **Implication:** For continuous control/regression tasks, the recipe is validated. Start here for new domains with similar structure.

**Key learning 17: Read-all-sources-first protocol is essential**
- Agent prompt requires reading: knowledge-base, learnings, decision-framework, notepad
- This ensures context from prior invocations is available
- Notepad provides crash recovery if interrupted
- **Implication:** First action after invocation: read all four sources. Do not proceed until loaded. This is the "semi-persistence" mechanism.

**Key learning 18: Parallax requires free diversity, not restricted views**
- Feature-split: excellent parallax (low error correlation), crippled competence → ensemble loses -8.4%
- Data-split: maximum parallax (negative error correlation), weak competence → ensemble loses -1.5%
- Architecture-split: moderate parallax, full competence → ensemble wins +0.6%
- **Implication:** Diversity achieved by restricting model access (features or data) destroys competence. Only architectural diversity provides free parallax.

**Key learning 19: Iterative RLHF is a cascade**
- Each RM update cycle = new self-referential stage
- Sub-multiplicative cascade theorem applies
- After k update cycles: R²(k) ≲ w^k, often much worse due to temporal correlation buildup
- MVSU mitigates but doesn't eliminate (still a cascade)
- **Implication:** For iterative RLHF, track reward accuracy across RM update cycles. If degradation appears, it's the cascade effect. MVSU provides ~8x improvement but signal still degrades.

**Key learning 20: The rehearsal paradox**
- Each memory recall = new processing stage at high α (≈ 1.0)
- After 5 recalls, ~0.3% of original signal survives
- Well-rehearsed memories feel vivid (low per-recall effort) but are highly confabulated (many stages)
- **Implication:** For systems with repeated processing of same signal (e.g., iterative refinement, multi-pass editing), warn about signal degradation. Each pass is a new contamination stage.

## Next Patterns to Watch For

**Pattern 1: Transformer attention spontaneous inhibition**
- Hypothesis: trained transformers may develop negative coupling between attention heads that process self-generated vs external tokens
- Test: analyze GPT-2/GPT-3 attention patterns, look for negative weights between heads
- If found: validates that MVSU structure emerges naturally in large models

**Pattern 2: Scaling behavior of the gap**
- 8.3% gap measured in toy setting (scalar, linear)
- Open question: does it persist, grow, or shrink at scale (>1B parameters)?
- Test: run RLHF experiment at GPT-2 scale (planned but not yet executed)
- Expected: gap may change in magnitude but qualitative finding (myopic ≠ optimal) should persist

**Pattern 3: Continuous vs discrete phase transition**
- Classification fails, regression works
- Is there a "continuity threshold" for contamination structure?
- Test: mixed discrete/continuous tasks (e.g., language modeling with continuous embeddings)
- Expected: MVSU may work in continuous representation space even if output is discrete

**Pattern 4: Nonstationary α(t)**
- Current theory assumes constant α
- Real systems: α changes over training (early RLHF: low α, late RLHF: high α)
- Test: time-varying α in toy setting, measure tracking behavior
- Expected: MVSU can track slowly-varying α, but rapid changes may break convergence

**Pattern 5: Active vs passive decontamination**
- Current MVSU: passive (learns to subtract contamination from observations)
- Alternative: active (one model generates, other filters before training)
- Test: synthetic data with active cross-filtering (Model A generates, Model B filters for Model A's training)
- Expected: active filtering may be more effective than passive subtraction for data contamination

## Archive Policy

When this file approaches 200 lines:
1. Create `archive/learnings-YYYY-MM-DD.md`
2. Move entries older than 3 months to archive
3. Keep most recent learnings in main file
4. Include pointer to archive in header
