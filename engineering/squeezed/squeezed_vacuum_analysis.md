# Squeezed Cell Vacuum — Equation of State Analysis

**Date**: 2026-02-04
**Status**: Complete
**Evidence Tier**: [PROVEN] — exact operator identity, no approximations
**Result**: w = 0 for ALL values of squeezing parameter r

---

## 1. Setup

The cell vacuum in the Two Vacua framework is a product of coherent states |alpha> with |alpha|^2 = 1/2 on Compton-scale cells. This gives w = 0 (pressureless dust).

**Question**: Can squeezing the cell states — replacing |alpha> with S(r)|alpha> — change the equation of state?

**Answer**: No. w = 0 for all r, for all alpha, for all squeezing angles. This is an exact result.

---

## 2. Derivation

### 2.1 Field Operators

For a massive scalar field in a single Compton cell, the mode decomposition gives:

```
phi = sqrt(hbar/(2*m*omega)) * (a + a^dag)
pi  = -i*sqrt(m*omega*hbar/2) * (a - a^dag)
```

where omega = mc^2/hbar is the Compton frequency.

### 2.2 Squeezed Coherent State Expectation Values

For |psi> = S(r)D(alpha)|0> with real squeezing parameter r:

```
<a^dag a> = |alpha|^2 + sinh^2(r)           [total particle number]
<a^2>     = alpha^2 - (1/2)sinh(2r)          [anomalous correlator]
```

### 2.3 Time Evolution (Heisenberg Picture)

```
a(t) = a * e^{-i*omega*t}
```

Therefore:

```
<phi^2(t)> = (hbar/(2m*omega)) * [2n + 1 + 2*Re(C*e^{-2i*omega*t})]
<pi^2(t)>  = (m*omega*hbar/2)  * [2n + 1 - 2*Re(C*e^{-2i*omega*t})]
```

where n = |alpha|^2 + sinh^2(r) and C = <a^2> = alpha^2 - (1/2)sinh(2r).

**Critical observation**: The oscillating term has OPPOSITE signs in phi^2 and pi^2.

### 2.4 Stress-Energy Tensor

```
rho(t) = <pi^2>/(2m) + (1/2)*m*omega^2*<phi^2>
p(t)   = <pi^2>/(2m) - (1/2)*m*omega^2*<phi^2>
```

Computing the prefactors:
- Kinetic: <pi^2>/(2m) = (hbar*omega/4) * [2n + 1 - 2*Re(C*e^{-2iwt})]
- Potential: (1/2)*m*omega^2*<phi^2> = (hbar*omega/4) * [2n + 1 + 2*Re(C*e^{-2iwt})]

**Both prefactors are identical**: hbar*omega/4. This is not a coincidence — it is the defining property of the harmonic oscillator that makes kinetic and potential energy equal on average.

### 2.5 The Result

**Energy density (time-independent)**:
```
rho = (hbar*omega/4) * [(2n+1) - osc + (2n+1) + osc]
    = (hbar*omega/2) * (2n + 1)
    = hbar*omega * (|alpha|^2 + sinh^2(r) + 1/2)
```

The oscillating terms **cancel exactly** in rho. Energy density is constant in time.

**Pressure (purely oscillating)**:
```
p(t) = (hbar*omega/4) * [(2n+1) - osc - (2n+1) - osc]
     = -(hbar*omega/2) * 2*Re(C * e^{-2i*omega*t})
     = -hbar*omega * Re(C * e^{-2i*omega*t})
```

The constant terms **cancel exactly** in p. Pressure is purely oscillatory.

**Time average**:
```
<p>_t = -hbar*omega * <Re(C * e^{-2i*omega*t})>_t = 0
```

because the time average of cos(2*omega*t + phase) over any integer number of periods is zero.

**Therefore**: w = <p>_t / <rho> = 0 / [hbar*omega*(n + 1/2)] = **0**.

---

## 3. Why This Result Is Exact

This is the **quantum virial theorem for the harmonic oscillator**.

For H = hbar*omega*(a^dag*a + 1/2), the pressure operator is:

```
P(t) = -(hbar*omega/2) * (a^2 * e^{-2iwt} + a^{dag 2} * e^{2iwt})
```

For ANY density matrix rho:

```
<P(t)> = -hbar*omega * Re(Tr[rho * a^2] * e^{-2iwt})
```

The quantity Tr[rho * a^2] is just a complex number — call it C. It can be anything. The time average of Re(C * e^{-2iwt}) is always zero.

**No approximations were used.** This is an exact operator identity.

---

## 4. Universality: w = 0 for ALL QHO States

| State | <a^2> = C | Pressure behavior | w |
|-------|-----------|-------------------|---|
| Coherent |alpha> | alpha^2 | Oscillates, averages to 0 | 0 |
| Squeezed S(r)|alpha> | alpha^2 - (1/2)sinh(2r) | Oscillates, averages to 0 | 0 |
| Fock |n> | 0 | Identically zero | 0 |
| Thermal rho_T | 0 | Identically zero | 0 |
| Cat state | nonzero | Oscillates, averages to 0 | 0 |
| Arbitrary |psi> | <psi|a^2|psi> | Oscillates, averages to 0 | 0 |
| Arbitrary mixed rho | Tr[rho*a^2] | Oscillates, averages to 0 | 0 |

**w = 0 is a property of the Hamiltonian (QHO), not of the state.**

---

## 5. What Squeezing DOES Change

While w is unaffected, squeezing changes other physical quantities:

### 5.1 Energy Density

```
rho(r) = hbar*omega * (|alpha|^2 + sinh^2(r) + 1/2)
```

For |alpha|^2 = 1/2:
| r | sinh^2(r) | rho/rho_coherent | Extra particles |
|---|-----------|------------------|-----------------|
| 0 | 0 | 1.0 | 0 |
| 0.5 | 0.274 | 1.274 | 0.274 |
| 1.0 | 1.381 | 2.381 | 1.381 |
| 2.0 | 13.10 | 14.10 | 13.10 |
| 3.0 | 100.4 | 101.4 | 100.4 |

Energy density grows exponentially with squeezing: rho ~ (1/4)*e^{2r} for large r.

### 5.2 Uncertainty Distribution

```
Delta_phi(r) = Delta_phi(0) * e^{-r}    [squeezed]
Delta_pi(r)  = Delta_pi(0)  * e^{+r}    [anti-squeezed]
```

The uncertainty product Delta_phi * Delta_pi = hbar/2 is preserved (minimum uncertainty).

### 5.3 Pressure Oscillation Amplitude

```
|p|_max = hbar*omega * |C| = hbar*omega * |alpha^2 - (1/2)sinh(2r)|
```

The pressure oscillation amplitude changes with r, but its time average remains zero.

---

## 6. Physical Interpretation

### 6.1 Why Squeezing Cannot Change w

The harmonic oscillator has an exact symmetry between kinetic and potential energy. Over one full oscillation cycle, the field spends equal "time" in kinetic-dominated and potential-dominated phases, and these average exactly.

Squeezing changes the SHAPE of the oscillation in phase space (making the Wigner function elliptical rather than circular), but it does not break the symmetry between kinetic and potential energies on average. The QHO dynamics rotates the squeezing ellipse at frequency omega, ensuring perfect time-averaged equipartition.

### 6.2 Comparison to Classical Mechanics

In classical mechanics, the virial theorem for the harmonic oscillator V(x) = (1/2)*k*x^2 gives <T> = <V> regardless of amplitude or initial conditions. This is the same result — the quantum version inherits it exactly because the QHO preserves the harmonic structure.

### 6.3 What WOULD Change w?

To get w != 0, one must break the QHO structure:

1. **Spatial gradients** (k != 0 modes): Add positive pressure, pushing w toward +1/3
2. **Anharmonic potential**: e.g., phi^4 theory. Virial theorem gives <T> = (n/2)<V> for V ~ phi^n, so w != 0 for n != 2
3. **Time-dependent mass**: Breaks stationarity, allows parametric effects
4. **Multi-field interactions**: Additional terms in stress-energy tensor
5. **Massless fields**: omega = |k|, pure kinetic, gives w = +1/3 (radiation)

---

## 7. Implications for the Dark Energy Problem

### 7.1 w = 0 Is MORE Robust Than Previously Thought

The original cell vacuum derivation showed w = 0 for coherent states. One might have hoped that a different quantum state (such as a squeezed state) could yield w = -1.

**This is impossible.** [PROVEN]

The w = 0 result follows from the QHO virial theorem, which is state-independent. No manipulation of the quantum state of a single massive oscillating mode can produce w = -1. The equation of state is determined by the Hamiltonian, not the state.

### 7.2 The Cell Vacuum Describes Dust, Not Dark Energy

This reinforces the conclusion from prior work:

- Cell vacuum: w = 0 (dust / dark matter candidate) [PROVEN]
- Dark energy: w = -1 (cosmological constant)
- The cell vacuum CANNOT be dark energy, regardless of state preparation

### 7.3 Only the Wald Ambiguity Can Introduce w = -1

The only mechanism in the framework that produces w = -1 behavior is the Wald renormalization ambiguity Lambda_0 * g_uv. The total equation of state is:

```
w_total = -Lambda_0 / (rho_state + Lambda_0)
```

This interpolates between w = 0 (Lambda_0 = 0) and w -> -1 (Lambda_0 >> rho_state), but never reaches w = -1 exactly for finite Lambda_0 when rho_state > 0.

### 7.4 Can ANY Single-Mode Massive Field State Give w != 0?

**No.** [PROVEN]

This was proven in Section 3. The result holds for arbitrary pure states, mixed states, and density matrices. The only assumptions are:
1. Single mode (no spatial gradients)
2. Harmonic oscillator Hamiltonian (massive free field)
3. Time averaging over complete oscillation cycles

---

## 8. Evidence Tier Classification

| Claim | Tier | Justification |
|-------|------|---------------|
| w = 0 for coherent states | [PROVEN] | Direct calculation, matches prior work |
| w = 0 for squeezed coherent states | [PROVEN] | QHO virial theorem, exact operator identity |
| w = 0 for ALL QHO states | [PROVEN] | General operator argument, no state-dependent assumptions |
| Energy density grows as sinh^2(r) | [PROVEN] | Direct calculation from expectation values |
| Squeezed states preserve minimum uncertainty | [PROVEN] | Standard result in quantum optics |
| Only non-QHO effects can give w != 0 | [PROVEN] | Follows from generality of the virial theorem argument |
| Cell vacuum cannot be dark energy | [PROVEN] | w = 0 != -1, and no state change can fix this |

---

## 9. Numerical Verification Summary

All results verified numerically with the test suite (68 tests, all passing):

- w computed by explicit time integration over 200-1000 periods
- |w| < 10^{-4} for all tested values of r from 0 to 3
- Energy density matches analytic formula to < 10^{-8} relative error
- Virial theorem <T>_t = <V>_t verified to < 10^{-6} relative error
- Energy density time-independence verified to < 10^{-10} relative variation
- Pressure analytic formula matches direct computation to < 10^{-10}
- Uncertainty product hbar/2 preserved to < 10^{-12} relative error

---

## 10. Files

- `squeezed_vacuum.py`: Full computation module (8 classes, ~500 lines)
- `test_squeezed_vacuum.py`: Test suite (68 tests across 9 categories)
- `squeezed_vacuum_analysis.md`: This document
