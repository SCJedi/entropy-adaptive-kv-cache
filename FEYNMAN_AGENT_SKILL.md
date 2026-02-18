# Feynman Documentation Agent Skill

## How to Invoke This Skill

Just tell me:

> **"Use the Feynman agent skill on [document/topic]"**

or

> **"Feynman-ize this"**

or

> **"Break this down Feynman-style"**

---

## What This Skill Does

Takes any complex topic or document and:

1. **Breaks it into logical sub-sections** (typically 4-6 per main part)
2. **Spins up parallel agents** to write each section simultaneously
3. **Each agent writes in Feynman's teaching style**
4. **Uses beautiful Unicode math** (ℏ, ω, ⟨⟩, Ω, ∞, etc.)
5. **Includes phonetic callouts** ("ket-alpha", "h-bar omega")
6. **Builds understanding from ground up**

---

## The Process (Step by Step)

### Step 1: Analyze the Document

Read the source material and identify:
- Main sections (Parts I, II, III...)
- Sub-topics within each section
- Key concepts that need explanation
- Mathematical formulas that need phonetic translation

### Step 2: Create Section Breakdown

For each main part, list 4-6 sub-sections:

```
Part 1: Foundations
  1.1 Quantum Oscillator
  1.2 Ground State
  1.3 Coherent States
  1.4 Uncertainty Relations
  1.5 Special Cases
```

### Step 3: Spin Up Parallel Agents

Launch 5 agents simultaneously (one per sub-section):

```
Agent 1 → part1_1_quantum_oscillator_feynman.md
Agent 2 → part1_2_ground_state_feynman.md
Agent 3 → part1_3_coherent_states_feynman.md
Agent 4 → part1_4_uncertainty_feynman.md
Agent 5 → part1_5_special_case_feynman.md
```

### Step 4: Agent Instructions Template

Each agent gets these requirements:

```markdown
CRITICAL REQUIREMENTS:

1. Beautiful Unicode symbols:
   - ℏ not hbar
   - ω not omega
   - √ not sqrt
   - ⟨⟩ for bra-kets
   - † for dagger
   - ∞, →, ≡, ≈, ½

2. PHONETIC callouts:
   - "We write â - that's 'a-hat'"
   - "The constant ℏ - 'h-bar'"
   - "The state |α⟩ - 'ket alpha'"

3. Feynman teaching style:
   - "Now, what does this really mean?"
   - "Let's think about this carefully..."
   - Build intuition before math
   - Simple examples first
   - Make the reader discover insights

4. Cover: [specific topic content]
```

### Step 5: Wait for Completion

All agents run in parallel. Wait for all to complete, then verify files.

### Step 6: Create Index/Summary

List all created files with previews.

---

## Output Structure

```
[project]/
├── part1_foundations_feynman.md          # Overview
├── part1_1_[topic]_feynman.md            # Sub-section 1
├── part1_2_[topic]_feynman.md            # Sub-section 2
├── part1_3_[topic]_feynman.md            # Sub-section 3
├── part1_4_[topic]_feynman.md            # Sub-section 4
├── part1_5_[topic]_feynman.md            # Sub-section 5
├── part2_[topic]_feynman.md              # Next main part
├── part2_1_[topic]_feynman.md            # And its sub-sections...
└── ...
```

---

## Companion Documents (Optional)

If requested, also create:

| Document | Audience | Purpose |
|----------|----------|---------|
| `EXPLAIN_LIKE_IM_5_feynman.md` | Children | No equations, analogies only |
| `ULTIMATE_FAQ_feynman.md` | Everyone | 50+ Q&A pairs |
| `FOR_THE_GENIUS_feynman.md` | Experts | Rigorous theorems/proofs |
| `VISUAL_INTUITION_feynman.md` | Visual learners | ASCII diagrams |
| `HISTORICAL_CONTEXT_feynman.md` | Story lovers | Narrative history |
| `COMPLETE_PRIMER_feynman.md` | All levels | 4-tier explanation |

---

## Feynman Style Guide

### Voice
- Conversational, like talking to a friend
- "You know...", "Here's the thing...", "Let me tell you..."
- Questions that make you think
- Wonder and delight at discoveries

### Structure
- Start with what the reader knows
- Build up piece by piece
- Each step feels inevitable
- End with the "aha!" moment

### Mathematics
- Show the equation
- Read it aloud phonetically
- Explain what each piece means
- Show why it has to be that way

### Examples
```markdown
Now let me write down the key equation:

$$E = ℏω\left(|α|² + \frac{1}{2}\right)$$

Read this as: "E equals h-bar omega times the quantity
alpha-squared plus one-half."

The first term ℏω|α|² - "h-bar omega times alpha squared" -
that's the energy you put in. The second term, ½ℏω -
"one-half h-bar omega" - that's always there, even in
the ground state.
```

---

## Quick Reference Commands

| Say This | I Do This |
|----------|-----------|
| "Feynman-ize [doc]" | Full breakdown with parallel agents |
| "Break down Part X" | Sub-sections for one part only |
| "Add companion docs" | Create FAQ, ELI5, Genius, etc. |
| "Use nice math symbols" | Unicode ℏ ω ⟨⟩ not code-style |
| "Explain phonetically" | Call out how to read symbols |

---

## Example Invocation

**User says:**
> "Use the Feynman agent skill on THE_TWO_VACUA_THEORY.md"

**I will:**
1. Read the document
2. Identify main parts (I-V)
3. Break each into 4-6 sub-sections
4. Spin up 5 agents per part in parallel
5. Each writes Feynman-style with Unicode math
6. Report when complete with file list

---

## Notes

- Agents run in parallel for speed
- Each agent is independent (no dependencies)
- Files use consistent naming: `partX_Y_topic_feynman.md`
- All math uses Unicode not LaTeX-style code
- Every symbol gets phonetic introduction on first use
