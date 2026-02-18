# Knowledge Base Update: w = -1 Investigation Results

**Date**: February 1, 2026
**Triggered by**: Cross-evaluation of Team Alpha and Team Beta w = -1 investigation
**Status**: Ready for incorporation into knowledge-base.md

---

## 1. Evidence Tier Changes

### DEMOTIONS (claims that must be downgraded)

**1a. w = -1 equation of state**
- **Current tier**: [FRAMEWORK] (implicit -- never explicitly tagged, treated as a core claim)
- **New tier**: [DEMOTED]
- **Reason**: Both independent teams prove w = 0 (time-averaged) for the k=0 coherent state of a massive scalar field. The Wald ambiguity cannot restore w = -1 (proven algebraically). No massive KG solution gives T_{mu nu} ~ g_{mu nu} (proven as theorem).
- **What to say**: "The cell vacuum gives time-averaged w = 0 (dust/cold dark matter), NOT w = -1 (dark energy). This was established by two independent calculations using canonical quantization and Hadamard/Weyl algebra methods, February 2026."

**1b. The previous w = -2/3 result**
- **Current tier**: [FRAMEWORK] (in 02_curved_spacetime.md, Section 5.7)
- **New tier**: [DEMOTED]
- **Reason**: Was computed for a static, spatially varying massive field, which is not a solution of the Klein-Gordon equation. A massive field must oscillate. The corrected result for the physical (oscillating) field is w = 0 (homogeneous) or w > 0 (localized).
- **What to say**: "The earlier result w = -2/3 was based on an unphysical static field assumption. Corrected to w = 0 for the physical oscillating configuration."

**1c. "Cell vacuum as dark energy" core claim**
- **Current tier**: [FRAMEWORK]
- **New tier**: [FRAMEWORK] with added caveat: "severely undermined by w != -1 finding"
- **Reason**: The cell vacuum energy density matches observed dark energy, but the equation of state does not. Without w = -1, the cell vacuum cannot be the cosmological constant.

### CONFIRMATIONS (claims that are strengthened)

**1d. AQFT legitimacy of the cell vacuum**
- **Current tier**: [PROVEN]
- **Remains**: [PROVEN]
- **Note**: The w investigation used and relied upon the AQFT construction. It worked perfectly. The Hadamard condition, the stress-energy decomposition, the Wald ambiguity analysis -- all confirmed as correct and useful.

**1e. Energy density formula rho = m^4 c^5/hbar^3**
- **Current tier**: [PROVEN as dimensional analysis + construction]
- **Remains**: [PROVEN as dimensional analysis + construction]
- **Note**: The formula itself is not affected by the w result. The energy per cell IS mc^2. The density IS m^4 c^5/hbar^3. What changed is the physical interpretation (matter, not dark energy).

**1f. The 50/50 energy split**
- **Current tier**: [VERIFIED]
- **Strengthened to**: [PROVEN]
- **Reason**: Both teams independently verify E_displacement = E_zero-point = mc^2/2 as an algebraic identity for |alpha|^2 = 1/2.

### NEW ENTRIES (findings to add)

**1g. Virial theorem for k=0 mode** [PROVEN]
- For a massive scalar field k=0 mode in a box, <kinetic energy> = <potential energy> (virial theorem). This makes the time-averaged pressure exactly zero.

**1h. Algebraic impossibility of w = -1 with Wald ambiguity** [PROVEN]
- If the state-dependent contribution has w_state != -1, then no Wald ambiguity term Lambda_0 g_{mu nu} can make w_total = -1. Proof: w_total = -1 requires p_state = -rho_state, i.e., w_state = -1. Contradiction.

**1i. No massive KG solution gives T_{mu nu} ~ g_{mu nu}** [PROVEN]
- For a real massive scalar field (m > 0), the only solution with T_{mu nu} = -rho g_{mu nu} is the trivial F = 0 solution. Requires both spatial and temporal derivatives to vanish, forcing F = constant, which requires m = 0 or F = 0.

**1j. Thermodynamic vs. microscopic tension** [OPEN]
- Thermodynamic argument: constant rho -> w = -1 via continuity equation. Microscopic argument: oscillating massive field -> w = 0 via stress tensor. These are contradictory. Resolution requires specifying the microscopic mechanism for maintaining constant density under expansion.

---

## 2. Learnings to Add

### For the specialist's learnings.md:

```
### 2026-02-01: w = -1 Investigation Results

**Finding**: The cell vacuum gives w = 0 (dust), not w = -1 (dark energy).

**Root cause**: A massive scalar field in a coherent state oscillates at frequency mc^2/hbar. The virial theorem makes time-averaged kinetic energy = potential energy, giving zero pressure. This is identical to the physics of axion dark matter.

**Key lesson**: You cannot have both finiteness AND w = -1 for a massive field excitation. The Lorentz invariance that guarantees w = -1 for vacuum energy is the same symmetry that, when preserved, gives the divergent mode sum. Breaking it (via cells) makes energy finite but destroys w = -1.

**Practical rule**: When asked about the equation of state, state clearly that w = -1 is NOT derived. The cell vacuum gives w = 0 microscopically. The thermodynamic argument (constant rho -> w = -1) is in tension with the microscopic result.

**Process lesson**: Two independent teams with different formalisms converging on the same answer provides much stronger evidence than a single calculation. This methodology should be used for all critical framework claims.

**What the specialist should say when asked about w = -1**:
"The equation of state w = -1 was assumed in the original framework but has been rigorously shown NOT to follow from the cell vacuum construction. Two independent calculations (canonical quantization and Hadamard/AQFT) both give w = 0 for the time-averaged stress tensor of the coherent state. The Wald renormalization ambiguity cannot fix this -- proven algebraically. This is a serious problem for the framework's dark energy interpretation. The energy density formula is correct, but the cell vacuum behaves as cold dark matter (w = 0), not dark energy (w = -1)."
```

---

## 3. Claims to Demote in the Knowledge Base

In knowledge-base.md, the following sections need modification:

### Section 1.3 (The Cell Vacuum)
Add after the properties list:
```
**CRITICAL UPDATE (2026-02-01)**: The equation of state of the cell vacuum has been rigorously
computed by two independent teams. Result: w = 0 (dust/cold dark matter), NOT w = -1 (dark energy).
See rigorous_team_session/11_the_good_bad_ugly.md for full analysis. The cell vacuum cannot serve
as a cosmological constant in its current form. [DEMOTED from FRAMEWORK to DEMOTED]
```

### Section 1.4 (The Formula)
Add after "What's not proven":
```
**EQUATION OF STATE UPDATE**: While the energy density is correct (rho = m^4 c^5/hbar^3),
the equation of state is w = 0 (pressureless dust), not w = -1 (cosmological constant).
The cell vacuum energy would dilute as 1/a^3 under expansion, not remain constant.
```

### Any section claiming w = -1
All instances of "the cell vacuum acts as a cosmological constant" or "w = -1" should be annotated with [DEMOTED] and a reference to this investigation.

---

## 4. Updated Framework Probability

| Prior | Post-investigation |
|-------|-------------------|
| 15-20% (as dark energy theory) | 5-10% (as dark energy theory) |
| N/A | ~20% (category error insight has independent value) |
| N/A | ~15% (neutrino mass predictions testable regardless) |

The specialist should present the framework honestly: the energy density formula is correct but the equation of state is wrong. The framework may be pointing at something real (the numerical coincidence, the category error insight) but does not currently constitute a viable dark energy model.

---

## 5. Decision Log Entry

```
### 2026-02-01: w = -1 Cross-Evaluation Complete

**Problem**: Does the cell vacuum give w = -1?
**Method**: Two independent teams (canonical + AQFT)
**Result**: NO. w = 0 (time-averaged) for k=0 coherent state
**Confidence**: VERY HIGH (>99%)
**Impact**: Core claim of framework undermined
**Action**: Demote w = -1 claim. Update all references.
**Follow-up**: Investigate dark matter interpretation. Wait for neutrino mass data.
```

---

**Update prepared**: February 1, 2026
**Status**: Ready for incorporation
