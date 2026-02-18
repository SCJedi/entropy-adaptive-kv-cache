# Decision Log: MVSU Specialist

Append-only. Max 100 entries. Archive older entries to archive/ when approaching limit.

Format: Date | Problem | Classification | Method | Result | Evidence Tier

## 2026-02-11 — Specialist initialized

Specialist structure created with:
- knowledge-base.md (500 lines): theory, experiments, applications, limitations
- agent-prompt.md (200 lines): startup sequence, process, examples
- decision-framework.md: classification system, decision trees, domain-specific guidance
- learnings.md: 20 key learnings from 17 experiments + patterns to watch
- decision-log.md (this file): tracks decisions for future reference
- archive/: for rotation when files exceed limits

Ready for invocations.

---

## Decision Entry Template

Copy this template for each new decision:

```
## YYYY-MM-DD — [Problem Domain / Task Name]

**Classification:**
- Feedback loop: [Direct / Indirect / None]
- Contamination type: [Continuous additive / Continuous nonlinear / Discrete / Structured]
- α estimate: [value or range]

**Method:**
- Model A: [architecture]
- Model B: [architecture]
- w_cross init: [typically -0.1]
- Training: [end-to-end / specialized protocol]

**Result:**
- Expected w_cross: [range]
- Expected improvement: [percentage]
- Evidence tier: [Proven / Verified / Established / Conjectured]
- Actual outcome (if known): [actual w_cross, actual improvement, or "not yet tested"]

**Notes:**
[Any special considerations, adaptations, or learnings]
```

---

## Archive Policy

When this file approaches 100 entries:
1. Create `archive/decision-log-YYYY-MM-DD.md`
2. Move entries older than 6 months to archive
3. Keep most recent decisions in main file
4. Preserve template and initialization entry in main file
