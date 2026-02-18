# UV Structure: A Complete Lesson Plan

**Scope:** 6 lessons covering ultraviolet structure in quantum field theory -- what it is, why it causes problems, how physics has handled it, and how it connects to the Alpha Framework's axioms (A1/F).

**Audience:** Advanced undergraduates, graduate students in theoretical physics, or physicists seeking to understand the UV foundations of vacuum selection.

**Evidence tiers used throughout:**
- **[PROVEN]** -- Mathematically demonstrated or experimentally confirmed
- **[FRAMEWORK]** -- Logically coherent construction, not independently verified
- **[ESTABLISHED]** -- Standard results in quantum mechanics and quantum field theory
- **[OPEN]** -- Unresolved; active area of investigation
- **[TENSION]** -- In conflict with observation or with other parts of the theory

---

## Course Overview

The term "UV" (ultraviolet) refers to short wavelengths, high energies, and small distances. The "UV problem" in quantum field theory is that summing contributions from arbitrarily short wavelengths produces divergent integrals -- infinities that must somehow be tamed.

This course examines UV structure from first principles:
1. What UV and IR mean, and why small-scale physics matters
2. Why summing zero-point energies over all modes diverges
3. How physics has attempted to handle this (cutoffs, regularization, renormalization)
4. Natural UV scales where physics itself provides a cutoff
5. The deep connection between UV structure and axiom choice (A1/F/Lorentz)
6. The Alpha Framework's specific proposal: Compton wavelength as UV scale

The central result is an equivalence theorem:

**(No UV scale) ⟺ (A1 fails) ⟺ (F fails) ⟺ (Exact Lorentz invariance)**

This means the question of UV structure is not technical -- it is a fundamental choice that determines the entire axiomatic structure of the theory.

---

## Prerequisites

**Required:**
- Basic quantum mechanics (wave-particle duality, uncertainty principle)
- Comfort with dimensional analysis
- Elementary calculus (integrals, limits)

**Helpful but not required:**
- Exposure to quantum field theory
- Basic special relativity
- Familiarity with the cosmological constant problem

---

## Lesson Summaries

### Lesson 1: What Is UV Structure?

**Summary:** Establishes the UV-IR vocabulary. UV = short wavelength = high energy = small distance. IR = long wavelength = low energy = large distance. The fundamental relation E = hc/λ connects energy and wavelength. Physics operates across 61 orders of magnitude (Planck to cosmic), with different effective theories at different scales. The concept of "UV completion" -- what happens as you probe smaller scales -- is central to quantum field theory.

**Key equations:**
- E = hc/λ (energy-wavelength relation)
- λ_Planck = √(ℏG/c³) ≈ 1.62 × 10⁻³⁵ m
- λ_Compton = ℏ/(mc)
- λ_deBroglie = h/p

**Evidence tier:** [ESTABLISHED]

---

### Lesson 2: Why Does the UV Cause Problems?

**Summary:** Derives the UV divergence explicitly. Each field mode has zero-point energy ℏω/2. Summing over all modes gives ∫d³k ω_k/2, which diverges quartically. The divergence arises from two effects: more modes at high k (density ~ k²), and more energy per mode at high k (energy ~ k). Product gives k³ dk → ∫k³dk = ∞. This is not a calculational artifact but a fundamental feature of standard QFT. The discrepancy with observation is 10¹²³ -- the worst prediction in physics.

**Key equations:**
- ρ = ∫d³k/(2π)³ · ℏω_k/2
- For ω_k = ck: ρ ~ ∫k³dk → ∞
- With cutoff Λ: ρ = ℏcΛ⁴/(16π²)
- At Planck cutoff: ρ ~ 10¹¹³ J/m³

**Evidence tier:** [PROVEN]

---

### Lesson 3: How Physics Has Handled the UV Problem

**Summary:** Surveys four strategies. (1) Hard cutoff -- simple but arbitrary, breaks Lorentz invariance. (2) Dimensional regularization -- preserves symmetries but hides the infinity. (3) Renormalization -- works for differences (F-weak) but fails for absolute values (F-strong). (4) Natural UV scales -- physics itself provides cutoffs (lattice spacing, Compton wavelength, Planck scale). The key distinction: renormalization solves F-weak problems completely, but the vacuum energy is an F-strong problem.

**Key equations:**
- Hard cutoff: ρ = ℏcΛ⁴/(16π²)
- Renormalized difference: ΔE = E_n - E_0 = finite
- Absolute value: ⟨T_μν⟩ requires regularization

**Evidence tier:** [ESTABLISHED]

---

### Lesson 4: Natural UV Scales in Physics

**Summary:** Examines specific scales where physics changes. The Planck scale (10⁻³⁵ m) is where quantum gravity matters -- spacetime becomes quantum. The Compton wavelength (ℏ/mc) is where pair creation prevents localization -- QFT becomes necessary. The de Broglie wavelength (h/p) is where quantum effects appear for a particle. The string scale (~10⁻³⁴ m, speculative) is where point particles become strings. The neutrino Compton wavelength (~0.1 mm) is the largest natural scale and may serve as the vacuum's UV cutoff.

**Key equations:**
- λ_Planck = √(ℏG/c³) ≈ 1.62 × 10⁻³⁵ m
- E_Planck = √(ℏc⁵/G) ≈ 1.22 × 10¹⁹ GeV
- λ_Compton = ℏ/(mc)
- λ_deBroglie = h/p

**Evidence tier:** [ESTABLISHED] for Planck/Compton/deBroglie, [FRAMEWORK] for string scale

---

### Lesson 5: The UV Choice and Its Consequences

**Summary:** Proves the central equivalence theorem: (No UV scale) ⟺ (A1 fails) ⟺ (F fails) ⟺ (Exact Lorentz). If you want finite vacuum energy (F satisfied), you must accept a UV scale, which breaks Lorentz at small scales. If you want exact Lorentz invariance, you must accept infinite vacuum energy. There are exactly two consistent packages: Standard QFT (exact Lorentz, infinite ρ) or Cell vacuum (broken Lorentz at UV, finite ρ). No hybrid is possible.

**Key equations:**
- ρ(a) = ℏcπ²/(16a⁴) → ∞ as a→0 (no UV scale)
- ρ = m⁴c⁵/ℏ³ (with UV scale at λ_C)
- Equivalence: (No UV) ⟺ (A1 fail) ⟺ (F fail) ⟺ (Exact Lorentz)

**Evidence tier:** [PROVEN] for the equivalence, [FRAMEWORK] for which choice nature makes

---

### Lesson 6: UV Structure and the Alpha Framework

**Summary:** The Alpha Framework chooses: natural UV scale at the Compton wavelength. This selects the cell vacuum over the mode vacuum. Consequences: ρ = m⁴c⁵/ℏ³ ≈ 6×10⁻¹⁰ J/m³ (matching dark matter), w = 0 (dark matter, not dark energy), Lorentz invariance emergent at scales >> λ_C. The framework explains why renormalization works (probes scales << λ_C) and why the "10¹²³ problem" isn't what it seems (wrong vacuum). It does NOT explain dark energy (Λ remains geometric) or why m_ν has its value. Prediction: Σm_ν ≈ 60 meV (testable, currently in tension with bounds).

**Key equations:**
- ρ_cell = m⁴c⁵/ℏ³
- w = p/ρ = 0 (virial theorem)
- m₁ = (ρ_CDM ℏ³/c⁵)^(1/4) ≈ 1.77 meV
- Σm_ν ≈ 60 meV

**Evidence tier:** [PROVEN] for mathematical results, [FRAMEWORK] for physical interpretation, [TENSION] for neutrino mass prediction

---

## Key Equations Reference

| Equation | Meaning |
|----------|---------|
| E = hc/λ | Energy-wavelength relation |
| λ_C = ℏ/(mc) | Compton wavelength |
| λ_P = √(ℏG/c³) | Planck length |
| E_P = √(ℏc⁵/G) | Planck energy |
| ρ = ∫d³k/(2π)³ · ℏω_k/2 | Vacuum energy density (integral form) |
| ρ = ℏcΛ⁴/(16π²) | Vacuum energy with cutoff Λ |
| ρ = m⁴c⁵/ℏ³ | Cell vacuum energy density |
| w = p/ρ = 0 | Cell vacuum equation of state |

---

## Evidence Tier Summary

| Claim | Tier |
|-------|------|
| UV = high energy = short wavelength | [ESTABLISHED] |
| Zero-point energy per mode = ℏω/2 | [ESTABLISHED] |
| Sum over modes diverges (∫k³dk → ∞) | [PROVEN] |
| Planck-scale cutoff gives ρ ~ 10¹¹³ J/m³ | [PROVEN] |
| Observed dark energy ρ ~ 10⁻¹⁰ J/m³ | [ESTABLISHED] |
| Renormalization works for F-weak | [ESTABLISHED] |
| Renormalization fails for F-strong | [ESTABLISHED] |
| Compton wavelength marks pair creation threshold | [ESTABLISHED] |
| Equivalence: (No UV) ⟺ (A1 fail) ⟺ (F fail) ⟺ (Exact Lorentz) | [PROVEN] |
| Cell vacuum satisfies A1 and F | [PROVEN] |
| Mode vacuum fails A1 and F | [PROVEN] |
| w = 0 for cell vacuum | [PROVEN] |
| ρ_cell = m⁴c⁵/ℏ³ | [PROVEN] |
| Cell vacuum is physical vacuum | [FRAMEWORK] |
| Cell vacuum = dark matter | [FRAMEWORK] |
| Σm_ν ≈ 60 meV | [FRAMEWORK, TENSION] |

---

## Prerequisite Map

```
Lesson 1 (What Is UV Structure?)
    |
    v
Lesson 2 (Why UV Causes Problems)
    |
    v
Lesson 3 (How Physics Handles UV)
    |
    v
Lesson 4 (Natural UV Scales)
    |
    v
Lesson 5 (The UV Choice)
    |
    v
Lesson 6 (UV and the Alpha Framework)
```

All lessons are sequential. Each builds on the previous.

---

## Reading Recommendations

**For physicists familiar with QFT:**
Start with Lesson 5 (the equivalence theorem), then Lesson 6 (the Alpha Framework). Reference earlier lessons as needed.

**For students learning QFT:**
Follow lessons 1-6 in order. Work through the exercises.

**For philosophers of physics:**
Focus on Lesson 1 (foundations), Lesson 5 (the choice structure), and Lesson 6 (what's proven vs framework).

**For experimentalists:**
Lesson 6 gives the testable predictions. Lesson 4 gives the relevant scales.

---

## Exercises by Lesson

Each lesson contains 5 exercises testing comprehension and calculation skills. The exercises progress from verifying key equations to applying concepts to new situations.

Total exercises: 30

---

*This course presents UV structure with intellectual honesty: the mathematics is proven, the physical interpretation is framework, and the open questions are clearly marked. The central insight -- that UV structure, axiom choice, and symmetry structure are the same thing in different languages -- is established by proof.*
