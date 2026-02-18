# Problem Selection Committee Report

**Date**: February 1, 2026
**Committee**: Problem Selection Committee
**Input Documents**: 03_works_and_doesnt.md, 05_evaluation.md, 05_final_synthesis.md (AQFT), knowledge-base.md, learnings.md
**Purpose**: Select the single highest-priority problem for the next research effort

---

## 1. Scoring Table

Each problem scored on three axes (1-10):

- **Impact**: If solved, how much does it strengthen the framework?
- **Tractability**: Can we make concrete progress with available tools and knowledge?
- **Urgency**: Does the framework survive without solving this? (10 = cannot survive)

Composite score = Impact x Tractability (higher is better), modulated by urgency.

| # | Problem | Impact | Tractability | Urgency | I x T | Dependencies | Notes |
|---|---------|--------|-------------|---------|-------|-------------|-------|
| 1 | Mass selection catastrophe | 10 | 2 | 9 | 20 | None | No known attack vector. "Potentially fatal." Framework wrong by >10^35 without it. |
| 2 | Black hole entropy tension | 8 | 3 | 7 | 24 | None | Existential but depends on which interpretation of BH entropy is correct. |
| 3 | w = -1 not derived | 9 | 7 | 8 | **63** | None | Well-defined AQFT calculation. Classical part gives w=-2/3. Quantum piece computable. |
| 4 | QCD/Higgs finite contributions | 7 | 2 | 6 | 14 | Partially depends on #1 | Shared with ALL CC approaches. Requires interacting QFT extension. |
| 5 | Category error precision | 4 | 5 | 3 | 20 | None | Reframing, not solving. Framework survives with weaker claim. |
| 6 | Energy density as renormalization condition | 6 | 6 | 4 | 36 | Benefits from #3 | Same AQFT machinery as w=-1 computation. |
| 7 | DESI tension (Sum 60.9 vs <53 meV) | 3 | 1 | 5 | 3 | None (experimental) | Cannot be "solved" theoretically. Must wait for data. |

---

## 2. Dependency Analysis

```
                  ┌──────────────────────────────────┐
                  │  #1 Mass Selection (HARD)         │
                  │  No known path. Needs new ideas.  │
                  └──────────┬───────────────────────┘
                             │ partially informs
                             v
               ┌─────────────────────────────┐
               │  #4 QCD/Higgs Contributions │
               │  Requires interacting QFT   │
               └─────────────────────────────┘

  ┌─────────────────────────────┐      ┌──────────────────────────────┐
  │  #3 w = -1 Derivation       │─────>│  #6 Energy Density from AQFT │
  │  Well-defined calculation    │shares│  Same machinery, deeper      │
  │  Hadamard point-splitting    │tools │  interpretation question     │
  └─────────────────────────────┘      └──────────────────────────────┘

  ┌─────────────────────────────┐
  │  #2 Black Hole Entropy      │  Independent. Requires quantum
  │  Scale-dependent vacuum?    │  gravity expertise.
  └─────────────────────────────┘

  ┌─────────────────────────────┐
  │  #5 Category Error Framing  │  Independent. Mostly philosophical.
  └─────────────────────────────┘

  ┌─────────────────────────────┐
  │  #7 DESI Tension            │  Experimental. Cannot be solved
  │  Wait for DR3+ (2026-2028)  │  by theoretical work.
  └─────────────────────────────┘
```

**Key dependency insight**: Problems #3 and #6 share the same AQFT computational machinery (Hadamard point-splitting on curved spacetime). Solving #3 provides most of the technical infrastructure needed for #6. These should be attacked together, with #3 as the primary target and #6 as a natural follow-on.

Problems #1 and #2 are independent of everything else but are both extremely hard (tractability 2-3). Neither has a clear attack vector.

Problem #7 is purely experimental and cannot be addressed by theoretical work.

---

## 3. Detailed Assessment of Top Candidates

### Problem #3: w = -1 Not Derived (RECOMMENDED)

**Why it scores highest on I x T**: Impact is 9 (a successful derivation would be transformative -- it would show the cell vacuum actually behaves as a cosmological constant, which is the entire physical claim). Tractability is 7 (the computation is well-defined using existing AQFT technology: Hadamard point-splitting or adiabatic regularization on FRW spacetime).

**The specific problem**: On curved spacetime, the classical displacement field in the cell vacuum produces spatial gradients within cells. These gradients generate positive pressure, giving w = -2/3 for the classical part alone. The quantum zero-point contribution is needed to restore w = -1. This quantum piece depends on the renormalization prescription but is, in principle, computable. The Hadamard condition has been proven (Section 2.4 of the AQFT synthesis), so the computation is well-defined.

**Why urgency is high (8/10)**: Without w = -1, the cell vacuum cannot serve as a cosmological constant. The framework predicts w = -1 exactly, but the only justification is the flat-space oscillator argument ("zero-point energy of a confined field has negative pressure"). If the rigorous curved-space calculation gives w != -1, this is not merely a gap -- it falsifies the framework's most observable prediction. Current data show w = -1.03 +/- 0.03, consistent with -1 but not with -2/3.

**Why tractability is high (7/10)**:
- The cell vacuum satisfies the Hadamard condition (proven, Rigor A)
- Standard Hadamard point-splitting gives a well-defined recipe for <T_ij>
- Adiabatic regularization is an alternative, well-understood method
- The computation is on FRW spacetime (maximally symmetric spatial sections), which simplifies the analysis considerably
- The classical part (w = -2/3) has already been computed -- only the quantum piece remains
- Existing AQFT literature (Wald 1994, Hollands-Wald 2001, Kay-Wald 1991) provides the framework

**Why it beats the other high-urgency problems**:
- Problem #1 (mass selection, urgency 9) has tractability 2. No one has identified even a promising approach. All proposed mechanisms (IR dominance, phase transitions, hierarchical decoupling) are "hand-waving" per the team's own assessment. Working on it now would likely produce nothing.
- Problem #2 (BH entropy, urgency 7) has tractability 3. It requires quantum gravity expertise that the current investigation team does not have. The scale-dependent vacuum idea is interesting but needs formalization that is far from straightforward.

### Problem #1: Mass Selection (runner-up for urgency, not recommended)

**Why not recommended despite urgency 9**: Tractability is 2/10. The team's own documents say "no mechanism exists" and all proposed explanations are "unformalized hand-waving." The quantitative analysis showed m_3 contributes 200,000x more than m_1. This is devastating, but there is no identified path to a solution. Attempting this now would be speculative exploration without a clear strategy. It needs a creative new idea, not systematic computation.

**When to revisit**: After solving #3 and #6. If the AQFT computation reveals something about how different mass species contribute to the stress-energy tensor, it might suggest a selection mechanism.

### Problem #2: Black Hole Entropy (runner-up for impact, not recommended)

**Why not recommended**: While existential (S=0 vs S=A/4l_P^2), the evaluation team (05_evaluation.md) noted this depends on which interpretation of BH entropy is correct. The entanglement interpretation is one among several. Furthermore, the evaluation team rated the team's treatment as "treating the most damaging interpretation as the default without justification." Tractability is 3/10 -- it requires deep quantum gravity expertise and there's no clear computational path.

**When to revisit**: After #3. If the stress-energy computation provides new insight about the cell vacuum on strongly curved backgrounds, the BH entropy question may become more tractable.

---

## 4. Recommendation

**SELECTED PROBLEM: #3 -- Derive w = -1 for the cell vacuum on curved spacetime**

### Justification Summary

| Criterion | Assessment |
|-----------|-----------|
| I x T Score | **63** (highest by a factor of 1.75x over next-best) |
| Urgency | 8/10 -- framework's most testable prediction at stake |
| Dependencies | None -- can be attacked immediately |
| Side benefits | Infrastructure for #6 (energy density derivation) |
| Risk | If w != -1, framework is falsified. But knowing this is better than not knowing. |
| Expertise needed | AQFT on curved spacetime (available in literature) |
| Estimated scope | Well-defined calculation, substantial but not open-ended |

### What "Success" Looks Like

**Full success** (probability ~40%): Complete computation of <T_mu_nu> for the cell vacuum on FRW spacetime showing that the combined classical + quantum contributions give w = -1 exactly (or to the precision needed for cosmological observation). This would:
- Validate the framework's most observable prediction
- Establish the cell vacuum as a genuine cosmological constant candidate
- Provide the computational infrastructure for deriving the energy density value (#6)
- Substantially increase the framework's probability assessment (evaluators said: "would raise to 30-35%")

**Partial success** (probability ~35%): Compute the quantum contribution and show it modifies w from -2/3 toward -1, with the exact value depending on a renormalization prescription choice. This would:
- Identify which renormalization prescription gives w = -1
- Determine whether w = -1 is a natural or fine-tuned outcome
- Clarify the relationship between the cell vacuum construction and the Wald ambiguity

**Informative failure** (probability ~25%): Show rigorously that w != -1 for any reasonable renormalization prescription. This would:
- Definitively identify a fatal flaw in the framework
- Save years of work on other problems that would be moot
- Represent honest, valuable scientific progress (killing a wrong theory is productive)

### What Resources/Expertise Are Needed

1. **AQFT on curved spacetime**: The primary technical skill. Hadamard point-splitting and/or adiabatic regularization methods. Key references: Wald (1994), Hollands-Wald (2001), Kay-Wald (1991), Brunetti-Fredenhagen-Verch (2003).

2. **Coherent state stress-energy**: Computing <alpha|T_mu_nu|alpha> in curved backgrounds. The classical part (c-number displacement field) is already done (gives w=-2/3). The quantum fluctuation part is the target.

3. **FRW spacetime QFT**: Mode decomposition on spatially flat FRW, time-dependent Bogoliubov coefficients, adiabatic expansion. Standard material in Parker-Toms (2009) and Birrell-Davies (1982).

4. **Renormalization prescription expertise**: Understanding of Wald's axioms, the cosmological constant ambiguity, and how different prescriptions (Hadamard subtraction, adiabatic, DeWitt-Schwinger) relate to each other.

5. **Computational tools**: The calculation may require numerical evaluation of mode sums or integrals. Python with scipy/numpy is sufficient.

### Concrete Steps

1. **Set up the problem**: Write the cell vacuum stress-energy as <T_mu_nu> = <T_mu_nu>_classical + <T_mu_nu>_quantum. The classical part is known (w=-2/3 from spatial gradients).

2. **Compute the quantum part**: Use Hadamard point-splitting to compute <T_mu_nu>_quantum for coherent states on FRW. The two-point function is W_Omega = W_0 + F*F (proven Hadamard). The renormalized expectation value is:
   ```
   <T_mu_nu>_ren = lim_{x'->x} D_mu_nu [W_Omega(x,x') - H(x,x')]
   ```
   where H is the Hadamard parametrix and D_mu_nu is the appropriate differential operator.

3. **Combine and compute w**: Add classical and quantum contributions. Compute w = P/rho where P = <T_ii>/3 (spatial average) and rho = <T_00>.

4. **Assess renormalization dependence**: Determine how sensitive the result is to the choice of Hadamard parametrix (which contains the Wald ambiguity).

5. **Verify**: Independent computation using adiabatic regularization as a cross-check.

---

## 5. Problems NOT Selected -- Disposition

| Problem | Disposition | When to Revisit |
|---------|------------|-----------------|
| #1 Mass selection | **PARKED** -- no attack vector. Monitor for creative insights. | After #3/#6 provide new computational tools |
| #2 BH entropy | **PARKED** -- needs QG expertise, interpretation-dependent | After #3; or when QG expert is available |
| #4 QCD/Higgs | **PARKED** -- shared with all CC approaches, needs interacting QFT | After #1 provides mass selection mechanism |
| #5 Category error | **LOW PRIORITY** -- reframing exercise, not blocking | Anytime, but not urgent |
| #6 Energy density | **NEXT AFTER #3** -- shares computational infrastructure | Immediately after #3 |
| #7 DESI tension | **MONITOR** -- wait for DR3+ data (2026-2028) | When new data releases |

---

## 6. Strategic Rationale

The committee considered three possible strategies:

**Strategy A: Attack the hardest problem first (#1 mass selection)**
- Pro: If solved, biggest single advance
- Con: No identified approach. High risk of producing nothing.
- Verdict: REJECTED -- not tractable

**Strategy B: Attack the most existential problem (#2 BH entropy)**
- Pro: If resolved, removes existential threat
- Con: Requires expertise we don't have. Multiple possible interpretations of BH entropy itself.
- Verdict: REJECTED -- not tractable with current team

**Strategy C: Attack the most tractable high-impact problem (#3 w = -1)** (SELECTED)
- Pro: Well-defined calculation. Existing tools. High impact. Natural follow-on to #6. Either validates or falsifies a core prediction.
- Con: If it fails (w != -1), the framework may be dead, making other problems moot.
- Verdict: SELECTED -- the "falsifies or validates" outcome is EXACTLY what we want. In science, answering the question is always better than avoiding it.

The selected strategy follows the principle: **solve the problem that maximally reduces uncertainty about the framework's viability, subject to the constraint that it must be tractable.** Problem #3 is the unique problem that scores high on all three criteria simultaneously.

---

**Committee Decision**: Proceed with Problem #3 (w = -1 derivation on curved spacetime).

**Expected outcome**: Either the cell vacuum is shown to behave as a cosmological constant (w = -1), substantially strengthening the framework, or it is shown not to, which is equally valuable as it identifies a definitive failure mode. Either way, uncertainty is reduced.
