# Observational Constraints on Omega_Lambda / Omega_DM

## The Central Question

Two theoretical predictions compete:
- **DOF prediction**: 5/2 = 2.500 (from degrees of freedom analysis)
- **Golden ratio squared**: phi^2 = 2.618033988...

Which does observation favor?

---

## Planck 2018 Official Values

### Primary Parameters (68% confidence)

From Planck Collaboration 2018 (arXiv:1807.06209):

| Parameter | Value | Uncertainty (1-sigma) |
|-----------|-------|----------------------|
| Omega_c h^2 | 0.1200 | 0.0012 |
| Omega_b h^2 | 0.02237 | 0.00015 |
| H_0 | 67.36 km/s/Mpc | 0.54 |
| h = H_0/100 | 0.6736 | 0.0054 |

### Derived Parameters (68% confidence)

| Parameter | Value | Uncertainty (1-sigma) |
|-----------|-------|----------------------|
| Omega_m | 0.3153 | 0.0073 |
| Omega_Lambda | 0.6847 | 0.0073 |

Note: Omega_Lambda = 1 - Omega_m (assuming flat universe, Omega_K = 0.001 +/- 0.002)

---

## Deriving Individual Density Parameters

From h = 0.6736 +/- 0.0054, we get h^2 = 0.4537 +/- 0.0073

### Cold Dark Matter Density

```
Omega_c = (Omega_c h^2) / h^2
        = 0.1200 / 0.4537
        = 0.2645
```

**Error propagation:**
```
(sigma_Omega_c / Omega_c)^2 = (sigma_(Omega_c h^2) / (Omega_c h^2))^2 + (2 * sigma_h / h)^2
                            = (0.0012/0.1200)^2 + (2 * 0.0054/0.6736)^2
                            = (0.0100)^2 + (0.0160)^2
                            = 0.000356

sigma_Omega_c = 0.2645 * sqrt(0.000356) = 0.0050
```

**Result: Omega_c = 0.2645 +/- 0.0050**

### Baryon Density

```
Omega_b = (Omega_b h^2) / h^2
        = 0.02237 / 0.4537
        = 0.0493
```

**Error propagation (same method):**
```
sigma_Omega_b = 0.0493 * sqrt((0.00015/0.02237)^2 + (0.0160)^2)
              = 0.0493 * sqrt(0.000045 + 0.000256)
              = 0.0493 * 0.0173
              = 0.00085
```

**Result: Omega_b = 0.0493 +/- 0.0009**

### Cross-check: Omega_m

```
Omega_m = Omega_c + Omega_b = 0.2645 + 0.0493 = 0.3138
```

This is consistent with Planck's direct measurement of Omega_m = 0.3153 +/- 0.0073.

---

## Calculating the Ratios

### Ratio 1: Omega_Lambda / Omega_c (Dark Energy to CDM only)

```
R1 = Omega_Lambda / Omega_c = 0.6847 / 0.2645 = 2.589
```

**Error propagation:**
```
(sigma_R1 / R1)^2 = (sigma_Lambda / Omega_Lambda)^2 + (sigma_c / Omega_c)^2
                  = (0.0073/0.6847)^2 + (0.0050/0.2645)^2
                  = (0.0107)^2 + (0.0189)^2
                  = 0.000472

sigma_R1 = 2.589 * sqrt(0.000472) = 0.056
```

**Result: Omega_Lambda / Omega_c = 2.589 +/- 0.056**

### Ratio 2: Omega_Lambda / Omega_m (Dark Energy to Total Matter)

```
R2 = Omega_Lambda / Omega_m = 0.6847 / 0.3153 = 2.172
```

**Error propagation:**
```
(sigma_R2 / R2)^2 = (0.0073/0.6847)^2 + (0.0073/0.3153)^2
                  = 0.000114 + 0.000536
                  = 0.000650

sigma_R2 = 2.172 * sqrt(0.000650) = 0.055
```

**Result: Omega_Lambda / Omega_m = 2.172 +/- 0.055**

---

## Statistical Comparison with Theory

### Theoretical Values

| Theory | Value |
|--------|-------|
| 5/2 (DOF) | 2.500 |
| phi^2 (Golden) | 2.618 |

### Comparison with Ratio 1 (Omega_Lambda / Omega_c = 2.589 +/- 0.056)

**Distance from 5/2:**
```
delta_1 = 2.589 - 2.500 = 0.089
N_sigma = 0.089 / 0.056 = 1.59 sigma
```

**Distance from phi^2:**
```
delta_2 = 2.618 - 2.589 = 0.029
N_sigma = 0.029 / 0.056 = 0.52 sigma
```

### Comparison with Ratio 2 (Omega_Lambda / Omega_m = 2.172 +/- 0.055)

**Distance from 5/2:**
```
delta_1 = 2.500 - 2.172 = 0.328
N_sigma = 0.328 / 0.055 = 5.96 sigma
```

**Distance from phi^2:**
```
delta_2 = 2.618 - 2.172 = 0.446
N_sigma = 0.446 / 0.055 = 8.11 sigma
```

---

## Summary: Which Definition Matters?

| Ratio | Observed | From 5/2 | From phi^2 | Closer to |
|-------|----------|----------|------------|-----------|
| Omega_Lambda / Omega_c | 2.589 +/- 0.056 | 1.6 sigma | **0.5 sigma** | **phi^2** |
| Omega_Lambda / Omega_m | 2.172 +/- 0.055 | 6.0 sigma | 8.1 sigma | Neither |

### Critical Observation

**Using Omega_c alone (CDM only):**
- Observation is 0.52 sigma from phi^2 = 2.618
- Observation is 1.59 sigma from 5/2 = 2.500
- **phi^2 is clearly favored** (not excluded even at 1 sigma)
- 5/2 is not excluded at 2 sigma (marginal)

**Using Omega_m (CDM + baryons):**
- Both predictions are excluded at >5 sigma
- This ratio is not the relevant one for these theories

---

## Confidence Intervals and Exclusion

For Omega_Lambda / Omega_c = 2.589 +/- 0.056:

| Confidence Level | Interval |
|------------------|----------|
| 68% (1 sigma) | [2.533, 2.645] |
| 95% (2 sigma) | [2.477, 2.701] |
| 99.7% (3 sigma) | [2.421, 2.757] |

### Exclusion Status

| Theory | Value | Within 1 sigma? | Within 2 sigma? | Within 3 sigma? |
|--------|-------|-----------------|-----------------|-----------------|
| phi^2 | 2.618 | **YES** | YES | YES |
| 5/2 | 2.500 | NO | **YES** | YES |

**Neither is excluded at 3 sigma.**
**phi^2 is consistent at 1 sigma; 5/2 requires 2 sigma tolerance.**

---

## Redshift Evolution of the Ratio

The ratio Omega_Lambda(z) / Omega_DM(z) evolves with redshift.

In a flat Lambda-CDM universe:
```
Omega_Lambda(z) = Omega_Lambda / [Omega_Lambda + Omega_m (1+z)^3]
Omega_m(z) = Omega_m (1+z)^3 / [Omega_Lambda + Omega_m (1+z)^3]
```

Therefore:
```
R(z) = Omega_Lambda(z) / Omega_m(z) = Omega_Lambda / [Omega_m (1+z)^3]
```

### Present Day (z = 0)

```
R(0) = 0.6847 / 0.2645 = 2.589  (using CDM only)
```

### At z = 0.5

```
R(0.5) = 0.6847 / [0.2645 * (1.5)^3]
       = 0.6847 / [0.2645 * 3.375]
       = 0.6847 / 0.893
       = 0.767
```

### At z = 1.0

```
R(1.0) = 0.6847 / [0.2645 * (2.0)^3]
       = 0.6847 / [0.2645 * 8]
       = 0.6847 / 2.116
       = 0.324
```

### Finding z where R(z) = 5/2 or phi^2

The ratio R(z) = Omega_Lambda / [Omega_c (1+z)^3] decreases with redshift.

At z = 0, R = 2.589. Both target values (2.500 and 2.618) are close.

**For R(z_1) = 2.500:**
```
2.500 = 0.6847 / [0.2645 * (1+z_1)^3]
(1+z_1)^3 = 0.6847 / (2.500 * 0.2645) = 1.035
1+z_1 = 1.0115
z_1 = 0.012
```

**For R(z_2) = 2.618:**
```
2.618 = 0.6847 / [0.2645 * (1+z_2)^3]
(1+z_2)^3 = 0.6847 / (2.618 * 0.2645) = 0.989
1+z_2 = 0.996
z_2 = -0.004 (i.e., slightly in the future)
```

### Redshift Interpretation

- R(z) = 5/2 occurred at z = 0.012 (about 160 million years ago)
- R(z) = phi^2 will occur at z = -0.004 (about 55 million years in the future)

**We are currently between these two values, slightly closer to phi^2.**

---

## Physical Interpretation

### If 5/2 is Fundamental

The DOF theory predicts Omega_Lambda / Omega_c = 5/2 = 2.500.

Current observation: 2.589 +/- 0.056

Tension: 1.6 sigma (8.9% of values would be this extreme or more)

This is **not statistically significant tension**. The prediction is consistent within 2 sigma.

However, the observation is systematically HIGH by 3.6%. If systematic errors favor higher values, this could explain the deviation.

### If phi^2 is Fundamental

The golden ratio theory predicts Omega_Lambda / Omega_c = phi^2 = 2.618.

Current observation: 2.589 +/- 0.056

Tension: 0.5 sigma (62% of values would be this extreme or more)

This is **excellent agreement**. The observation is only 1.1% below the prediction.

---

## Likelihood Ratio

Assuming Gaussian errors, the relative probability is:

```
P(5/2) / P(phi^2) = exp(-0.5 * [(2.589-2.500)^2 - (2.589-2.618)^2] / 0.056^2)
                  = exp(-0.5 * [0.00792 - 0.00084] / 0.00314)
                  = exp(-0.5 * 2.25)
                  = exp(-1.13)
                  = 0.323
```

**phi^2 is about 3x more likely than 5/2 given current data.**

---

## Conclusions

1. **The relevant ratio is Omega_Lambda / Omega_c** (dark energy to CDM only, excluding baryons). This gives R = 2.589 +/- 0.056.

2. **phi^2 = 2.618 is the better fit** at 0.52 sigma deviation, compared to 5/2 = 2.500 at 1.59 sigma.

3. **Neither value is excluded** at 3 sigma (or even 2 sigma).

4. **Current data favor phi^2 by factor of ~3** in likelihood ratio.

5. **Redshift evolution shows**:
   - R = 5/2 occurred at z = 0.012 (~160 Myr ago)
   - R = phi^2 will occur at z = -0.004 (~55 Myr in future)
   - We are currently traversing between these values

6. **Future precision**: To distinguish 5/2 from phi^2 at 3 sigma would require reducing the error from 0.056 to about 0.039 (a 30% improvement in precision).

---

## Data Sources

- Planck Collaboration (2020). "Planck 2018 results. VI. Cosmological parameters."
  Astronomy & Astrophysics, 641, A6. arXiv:1807.06209
- Base LCDM model with TT,TE,EE+lowE+lensing combined analysis

---

## Appendix: Error Propagation Details

For ratio R = A/B with independent Gaussian errors:

```
sigma_R / R = sqrt[(sigma_A/A)^2 + (sigma_B/B)^2]
```

For derived Omega_c from Omega_c h^2 and h:

```
Omega_c = (Omega_c h^2) / h^2

sigma_Omega_c / Omega_c = sqrt[(sigma_(Omega_c h^2) / (Omega_c h^2))^2 + (2 * sigma_h / h)^2]
```

The factor of 2 arises because d(h^2)/dh = 2h, so relative error in h^2 is twice the relative error in h.
