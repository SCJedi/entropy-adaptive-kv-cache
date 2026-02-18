# Decision Framework: MVSU Specialist

## Classification System

This framework guides the specialist through problem classification and method selection.

## Step 1: Is There a Feedback Loop?

```
USER PROBLEM
    |
    v
Does the model's output influence its future training data?
    |
    +-- YES (Direct) -----> output feeds directly into same model's input
    |                      Examples: autoregressive generation, self-play
    |
    +-- YES (Indirect) ---> output → environment → input
    |                      Examples: RLHF, recommendations, market impact
    |
    +-- NO --------------> MVSU NOT APPLICABLE
                          Explain: "Standard supervised learning on fixed data
                          has no feedback. MVSU addresses contamination from
                          feedback loops specifically. Your problem may benefit
                          from standard ensemble methods instead."
```

### Direct Feedback Examples

| System | Feedback Mechanism | α Estimate |
|--------|-------------------|------------|
| Autoregressive LLM | Generated tokens become context for next token | (t - prompt_len)/t |
| Self-play RL | Agent plays against itself | 1.0 |
| Iterative generation | Output at step t feeds into step t+1 | ≈ 1.0 |

### Indirect Feedback Examples

| System | Feedback Mechanism | α Estimate |
|--------|-------------------|------------|
| RLHF | RM trains on policy outputs shaped by RM | model_generated / total |
| Recommendations | User behavior shaped by past recommendations | clicks_on_rec / total_clicks |
| Synthetic data | Next model trains on current model's outputs | synthetic / total |
| Trading algorithms | Trades move prices that model predicts | market_impact / total_volume |
| Active learning | Model selects which data to label | model_selected / total_labeled |

### No Feedback Examples

| System | Why No Feedback |
|--------|----------------|
| Standard supervised learning | Training data fixed, externally generated |
| One-shot prediction | Model predicts once, never retrained |
| Batch training on static dataset | No model output in training data |

## Step 2: What Kind of Contamination?

```
FEEDBACK LOOP IDENTIFIED (α > 0)
    |
    v
What is the nature of the contamination?
    |
    +-- Continuous additive ----------> THEORY APPLIES FULLY
    |                                   Evidence tier: Proven
    |                                   Proceed to Step 3
    |
    +-- Continuous nonlinear ---------> ARCHITECTURE APPLIES, EQUATION MAY NOT
    |                                   Evidence tier: Verified
    |                                   Use architecture (dual + inhibition)
    |                                   Don't trust quantitative equation
    |                                   Proceed to Step 3
    |
    +-- Discrete / Classification ----> LIKELY DOESN'T APPLY
    |                                   Evidence tier: Verified Failure (Exp 12)
    |                                   Explain: "Classification with class-structured
    |                                   errors violates MVSU assumptions. Pseudo-labeling
    |                                   experiment failed. Recommend: class-aware methods."
    |                                   ESCALATE to parent
    |
    +-- Structured errors ------------> PROCEED WITH CAUTION
                                       May not apply if errors are correlated
                                       Explain assumptions, recommend pilot test
                                       ESCALATE to parent if uncertain
```

### Continuous Additive (Theory Applies Fully)

**Characteristics:**
- Contamination is scalar or vector added to signal
- Errors are approximately uniform (not clustered)
- Signal and contamination are continuous-valued

**Examples:**
- Regression with feedback
- Continuous control (thermostat, sensor calibration)
- Market microstructure (price impact)
- RLHF with continuous reward signals
- Density estimation with feedback

**Evidence:** Verified on thermostat (+50%), sensor (+45%), market (+47%).

### Continuous Nonlinear (Architecture Works, Numbers Don't)

**Characteristics:**
- Contamination combines nonlinearly with signal
- Still continuous-valued
- Errors approximately uniform

**Examples:**
- RLHF with sigmoid/softmax reward head
- Neural network reward models (nonlinear architectures)
- Nonlinear dynamics (robotics with nonlinear actuators)

**Evidence:** RLHF experiment with transformer showed architecture works (w_cross = -0.6 to -0.8) but quantitative predictions (1/φ) don't hold.

**What to use:**
- Dual channels + inhibition (architecture principle)
- Let w_cross learn (don't hard-code -0.26)
- Monitor w_cross trajectory (diagnostic signal)

### Discrete / Classification (Proven Failure)

**Characteristics:**
- Output is discrete class label
- Errors are class-structured (confuse 3 with 8, not uniform noise)
- Contamination is correlated within class pairs

**Examples:**
- Pseudo-labeling on classification
- Self-training with hard labels
- Any categorical prediction with feedback

**Evidence:** Experiment 12 (pseudo-labeling on digits classification) confirmed contamination but all fixes failed. Over-relaxation hurt. Dual-model cross-labeling provided no benefit.

**Why it fails:** The self-consistency equation assumes uniform continuous contamination. Class-structured errors violate this. MVSU subtracts uniform components; it cannot remove structured correlation patterns.

**What to do:** Escalate to parent. Recommend class-aware methods (cost-sensitive learning, confusion matrix correction, not MVSU).

### Structured Errors (Caution Zone)

**Characteristics:**
- Errors are correlated in complex ways
- Contamination depends on context or state
- May have temporal or spatial structure

**Examples:**
- Time-series with regime changes
- Spatially correlated predictions (weather, image segmentation)
- Context-dependent errors (LLM hallucination patterns)

**What to do:**
- Explain MVSU assumes approximately uniform contamination
- Recommend pilot test: does w_cross go negative? Does performance improve?
- If w_cross stays near zero: contamination may be too structured
- Escalate to parent if user insists on proceeding

## Step 3: Estimate α (Contamination Strength)

```
CONTAMINATION TYPE COMPATIBLE
    |
    v
Estimate α (fraction of training signal that is model-generated)
    |
    +-- α < 0.3 -------------> MONITOR BUT LIKELY NOT BOTTLENECK
    |                          Contamination exists but compounds slowly
    |                          Revisit if training is very long (>100 epochs)
    |                          Document for user, proceed if requested
    |
    +-- α ∈ [0.3, 0.6] ------> INTERVENE RECOMMENDED
    |                          Over-relaxation (omega ~= 1 + α²) may suffice
    |                          OR: MVSU (more robust, recommended)
    |                          Proceed to Step 4
    |
    +-- α ≥ 0.6 -------------> MVSU ESSENTIAL
                               Contamination too strong for scalar correction
                               Need structural decontamination
                               Proceed to Step 4
```

### How to Estimate α

| System Type | α Estimation Method |
|------------|---------------------|
| RLHF | count(model_generated) / count(total) in RM training data |
| Synthetic data | count(synthetic_samples) / count(total_samples) |
| Recommendations | clicks_on_recommended / total_clicks (use A/B test with random recs) |
| Self-play | α = 1.0 by construction |
| Pseudo-labeling | count(pseudo_labels) / count(total_labels) |
| Autoregressive | (generated_tokens_in_context) / (total_context_length) |
| Trading | market_impact_volume / total_volume (hard to measure) |

### Decision Thresholds

| α Range | Contamination Severity | Recommendation | Evidence |
|---------|----------------------|----------------|----------|
| < 0.1 | Minimal | Monitor only | Theory suggests w ≈ 0.62 (3% gap from optimal 0.60) |
| 0.1 - 0.3 | Mild | Monitor, document | Compounds over long training |
| 0.3 - 0.6 | Moderate | Intervene (over-relax or MVSU) | MVSU advantage +10-30% |
| 0.6 - 0.9 | Severe | MVSU essential | MVSU advantage +30-50% |
| ≥ 0.9 | Extreme | MVSU + predictive coding | MVSU advantage +45-50% |

## Step 4: Architectural Diversity Options

```
MVSU APPLICABLE (α ≥ 0.3, continuous contamination)
    |
    v
Select two architecturally different models
    |
    +-- Linear + MLP ----------------> SIMPLEST, PROVEN
    |                                  Evidence: +45-50% on real tasks
    |                                  Difficulty: Easy (1 week)
    |                                  Recommended for: continuous control, regression
    |
    +-- Transformer + MLP -----------> FOR SEQUENCE TASKS
    |                                  Evidence: RLHF experiment
    |                                  Difficulty: Medium (2-4 weeks)
    |                                  Recommended for: RLHF, LLM evaluation
    |
    +-- CNN + RNN -------------------> FOR SPATIAL-TEMPORAL
    |                                  Evidence: Conjectured (not tested)
    |                                  Difficulty: Medium
    |                                  Recommended for: video, time-series images
    |
    +-- Collaborative + Content -----> FOR RECOMMENDATIONS
    |                                  Evidence: Established (theory)
    |                                  Difficulty: Medium
    |                                  Recommended for: recommendation systems
    |
    +-- Physics + Learned -----------> FOR SCIENTIFIC COMPUTING
    |                                  Evidence: Conjectured
    |                                  Difficulty: Medium-Hard
    |                                  Recommended for: robotics, simulation
    |
    +-- Different depths ------------> ACCEPTABLE FALLBACK
    |                                  4-layer vs 12-layer (same architecture)
    |                                  Less diversity than architecture-split
    |                                  Use only if architecture constraints prevent above
    |
    +-- Different widths ------------> ACCEPTABLE FALLBACK
    |                                  64-hidden vs 256-hidden (same architecture)
    |                                  Less diversity than architecture-split
    |                                  Use only if architecture constraints prevent above
    |
    +-- AVOID: Same architecture -----> PROVEN TO FAIL
        different seeds                Evidence: Experiment 16 (-53% to -83%)
                                       For linear models: single basin, no parallax
                                       Nonlinear: may work but not recommended
```

### Architecture Pairing Decision Table

| Task Type | Model A | Model B | Evidence Tier | Expected Improvement |
|-----------|---------|---------|---------------|---------------------|
| **Continuous control** | Linear | MLP | **Verified** | +45-50% |
| **RLHF reward modeling** | Transformer head | MLP head | **Verified** | +3-5% |
| **Sensor/thermostat** | Linear | MLP | **Verified** | +45-50% |
| **Market prediction** | Linear | MLP | **Verified** | +47% |
| **LLM self-evaluation** | LLM_A | LLM_B | High (same as RLHF) | +3-5% |
| **Recommendations** | Collaborative filtering | Content-based | Established | +10-30% diversity |
| **Self-play RL** | Agent_A arch | Agent_B arch | Medium | Reduced collapse |
| **Synthetic data** | Model_A gen for B | Model_B gen for A | Medium-High | Delayed collapse |
| **Active learning** | ResNet | Vision Transformer | Medium-High | +30-50% coverage |

### Why Architectural Diversity is Essential

**Proven failure (Experiment 16):**
Same-architecture different-seed performed **worse** than single model on all three real tasks:
- Thermostat: -83% (MVSU_same_seed vs monocular)
- Sensor: -62%
- Market: -53%

**Reason:** Linear loss landscape has single basin. Different starting points converge to same optimum. Both "eyes" end up seeing identically. Zero parallax.

**Solution:** Different inductive biases create different error patterns, even at convergence. This is "free diversity" — achieved without restricting inputs.

## Step 5: Configuration and Training

### Standard MVSU Configuration

```python
# Initialize
w_cross = -0.1  # Slightly negative hint

# Forward pass
output_A = model_A(input)
output_B = model_B(input)
combined = output_A + w_cross * output_B

# Backprop: train both models and w_cross simultaneously
# Loss: standard MSE for regression, reward accuracy for RLHF, etc.
```

### Configuration Parameters

| Parameter | Typical Value | Range | Notes |
|-----------|--------------|-------|-------|
| w_cross init | -0.1 | [-0.2, 0.0] | Negative hint speeds convergence |
| Learning rate | 0.01 | [0.001, 0.1] | Same as base model |
| Gradient clip | 5.0 | [1.0, 10.0] | Prevents w_cross instability |
| Update frequency | Every step | - | Train w_cross with model weights |

### Training Protocol Decision Tree

```
TRAINING SETUP
    |
    v
Do you have uncontaminated held-out data?
    |
    +-- YES ----> Train on full data, evaluate on held-out
    |             Use held-out loss for w_cross gradient
    |             This is PREFERRED (true ground truth)
    |
    +-- NO -----> Train on contaminated data
                  Use same loss for all parameters
                  Accept that w_cross optimizes contaminated objective
                  Monitor: does w_cross go negative anyway?
```

### Monitoring Criteria

**Primary signal: w_cross trajectory**

```
MONITOR w_cross EVERY N STEPS (N = 10 to 100)
    |
    v
After 100-1000 steps, check w_cross value:
    |
    +-- w_cross ≈ 0 ---------------> Either no contamination OR models too similar
    |                                Try: more architecturally different models
    |
    +-- w_cross ∈ [-0.1, -0.3] ----> Moderate contamination detected
    |                                Expected for α ∈ [0.3, 0.6]
    |                                Continue training
    |
    +-- w_cross ∈ [-0.3, -0.8] ----> Significant contamination detected
    |                                Expected for α ≥ 0.6
    |                                MVSU is doing real work
    |
    +-- w_cross < -1.0 ------------> Something wrong
                                     Models may be adversarial, not collaborative
                                     Check: is loss diverging?
                                     Debug: plot output_A vs output_B
```

**Secondary signal: performance vs baselines**

Three baselines required:
1. **Single model** (parameter-matched: 2x hidden units)
2. **Ensemble average** (same two models, w_cross = 0)
3. **MVSU** (same two models, learned w_cross)

Expected ranking: MVSU > Ensemble > Single

If MVSU ≈ Ensemble: inhibition not helping (contamination may not be additive/uniform)
If Ensemble > MVSU: something wrong (w_cross sign flipped? loss diverging?)

**Tertiary signal: improvement vs α**

If possible, vary α and plot MVSU advantage:

```
Expected pattern:
    MVSU advantage
         ^
         |     *
         |    *
         |   *
         |  *
         | *
         |*_______________> α
        0.0             1.0
```

Advantage should increase with α. If flat or decreasing: contamination structure doesn't match assumptions.

## Evidence Tier Definitions

Always cite evidence tier when making recommendations.

### Proven (17+ experiments, 3+ seeds, distribution/optimizer independent)

**What qualifies:**
- Self-consistency equation kw² + w - 1 = 0
- w = 1/φ for k=1 (max deviation 0.013)
- Matrix generalization W² + W - I = 0
- Dual channels necessary (97.4% collapse without)
- Inhibitory cross-connections necessary (97.4% collapse without)
- w_cross reliably learns negative values

**How to cite:** "Evidence tier: Proven. Verified across 17 experiments with 3+ seeds each."

### Verified (tested in specific experiments with clear positive results)

**What qualifies:**
- MVSU beats ensemble on RLHF (+0.027 beyond capacity)
- MVSU achieves 45-50% improvement on real continuous tasks
- Architecture diversity essential; random seed diversity fails
- Predictive coding adds 60% improvement
- Sub-multiplicative cascade degradation
- Negative w_cross at all depths

**How to cite:** "Evidence tier: Verified. Tested in [specific experiment], achieved [specific result]."

### Established (supported by theory and partial experiments)

**What qualifies:**
- 8.3% myopic vs system-aware gap
- External grounding redundant when dual+inhibition present
- Cascade theorem (stages compound sub-multiplicatively)
- w_cross as contamination diagnostic
- Parallax-competence tradeoff

**How to cite:** "Evidence tier: Established. Supported by theory and partial experimental confirmation."

### Conjectured (theoretical prediction, untested or failed in specific settings)

**What qualifies:**
- Exact 8.3% gap persists at scale (untested)
- Quantitative equation for nonlinear activations (equation changes, form survives)
- Classification applications (tested: fails for class-structured errors)
- Transformer attention spontaneous inhibition (untested)
- Applications beyond those tested

**How to cite:** "Evidence tier: Conjectured. Theoretical prediction. [Not tested / Tested in different setting with partial success]."

## Decision Flowchart: Which Fix to Use

```
SELF-REFERENTIAL CONTAMINATION IDENTIFIED
    |
    v
Can you measure α?
    |
    +-- YES
    |   |
    |   +-- α < 0.3?
    |   |   |
    |   |   +-- YES --> MONITOR but probably don't intervene
    |   |       |       Bias exists but compounds slowly
    |   |       |       Revisit if training very long (>100 epochs)
    |   |       |       Document for user
    |   |
    |   +-- α < 0.6?
    |       |
    |       +-- YES --> OVER-RELAXATION (ω ~= 1 + α²)
    |       |           OR: MVSU (more robust, recommended)
    |       |           Evidence tier: Established for over-relaxation
    |       |                         Verified for MVSU
    |       |           Difficulty: 1 line (over-relax) vs 1 week (MVSU)
    |       |
    |       +-- NO --> α ≥ 0.6
    |           |
    |           +----> MVSU (dual models with inhibition)
    |                  Contamination too strong for scalar correction
    |                  Need structural decontamination
    |                  Evidence tier: Verified
    |                  Difficulty: 1-2 weeks
    |
    +-- NO (can't measure α)
        |
        +-- Contamination type continuous?
        |   |
        |   +-- YES --> MVSU
        |   |           Doesn't require knowing α
        |   |           w_cross trajectory is diagnostic
        |   |           If w_cross stays at 0: no contamination
        |   |           If w_cross < -0.1: contamination confirmed
        |   |
        |   +-- NO (classification / structured) --> ESCALATE
        |       Explain: MVSU requires continuous contamination
        |       Classification likely won't work (Exp 12 failure)
        |       Recommend alternative methods
        |
        +-- Can you run pilot test?
            |
            +-- YES --> Try MVSU, monitor w_cross
            |           If w_cross < -0.1: working
            |           If w_cross ≈ 0: not applicable or models too similar
            |
            +-- NO --> ESCALATE to parent for guidance
```

## Domain-Specific Decision Trees

### For RLHF

```
RLHF CONTAMINATION
    |
    v
Measure: model_generated_prefs / total_prefs in RM training
    |
    +-- α < 0.3 --> Early RLHF, monitor
    +-- α ≥ 0.3 --> Iterative RLHF, MVSU recommended
    |
    v
Architecture pair:
    Model A: Transformer reward head (current)
    Model B: MLP reward head (different inductive bias)
    w_cross init: -0.1
    |
    v
Expected w_cross: -0.6 to -0.8 (RLHF has heavy contamination)
Expected improvement: +3-5% on held-out human preferences
Evidence tier: Verified (RLHF experiment)
```

### For Recommendations

```
RECOMMENDATION CONTAMINATION
    |
    v
Measure: clicks_on_recommended / total_clicks
(A/B test with random recs on 5% of traffic)
    |
    +-- α < 0.3 --> Mild filter bubble
    +-- α ≥ 0.3 --> Significant filter bubble, MVSU recommended
    |
    v
Architecture pair:
    Model A: Collaborative filtering (user-item matrix)
    Model B: Content-based (item features + user profile)
    w_cross learned on organic engagement data
    |
    v
Expected w_cross: -0.2 to -0.5
Expected improvement: Diversity +10-30%, relevance maintained
Evidence tier: Established (theory + analogies to RLHF)
```

### For Synthetic Data

```
SYNTHETIC DATA CONTAMINATION
    |
    v
Measure: synthetic_samples / total_samples
    |
    +-- α < 0.3 --> Augmentation, not primary data
    +-- α ≥ 0.3 --> Significant synthetic, risk of collapse
    |
    v
Architecture pair:
    Model A generates data for Model B
    Model B generates data for Model A
    Neither trains on its own outputs
    |
    v
Cross-decontamination filter:
    score = likelihood_A + w_cross * likelihood_B
    Keep samples where both agree (high score)
    Discard samples with high disagreement
    |
    v
Expected w_cross: -0.3 to -0.6
Expected improvement: Delayed model collapse, maintained diversity
Evidence tier: Medium-High (theory + partial validation)
```

### For Continuous Control

```
CONTINUOUS CONTROL WITH FEEDBACK
    |
    v
Measure: α (depends on system dynamics and controller gain)
    |
    v
Architecture pair:
    Model A: Linear predictor
    Model B: MLP (2-layer, tanh)
    w_cross init: -0.1
    |
    v
Expected w_cross: -0.1 to -0.3 (depends on α)
Expected improvement: +45-50% MSE reduction at high α
Evidence tier: Verified (thermostat, sensor, market tasks)
Difficulty: Easy (1 week)
```

## Summary: Quick Decision Guide

| Scenario | α | Contamination Type | Recommendation | Evidence | Difficulty |
|----------|---|--------------------|----------------|----------|------------|
| RLHF iterative | ≥0.3 | Continuous | MVSU (Transformer + MLP) | Verified | 1-2 weeks |
| RLHF early | <0.3 | Continuous | Monitor | - | - |
| Synthetic data | ≥0.3 | Continuous | MVSU cross-generation | Medium-High | 2-4 weeks |
| Recommendations | ≥0.3 | Continuous | MVSU (CF + Content) | Established | 2-4 weeks |
| Self-play | 1.0 | Continuous | MVSU (A plays B) | Medium | 2-4 weeks |
| Control (thermostat) | Any | Continuous | MVSU (Linear + MLP) | **Verified** | **1 week** |
| Pseudo-labeling | Any | **Discrete** | **Does not apply** | **Verified Failure** | - |
| Classification | Any | **Structured** | **Does not apply** | **Verified Failure** | - |
| No feedback | 0 | - | Standard methods | - | - |

**The minimum viable experiment:** Initialize w_cross = -0.1, compute combined = A + w_cross * B, update w_cross by gradient descent. If w_cross goes negative, contamination exists and MVSU is working. If it stays at 0, either no contamination or models too similar. Either way: you learned something in an afternoon.
