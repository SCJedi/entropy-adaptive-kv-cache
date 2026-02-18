# The Smallest Thing That Can Perceive

*What you must have, what helps, and what you don't need -- the ablation study that tells us exactly which parts matter.*

---

## The Question

After the cascade model (Document 5), we know the problem: self-referential processing destroys signal, and it compounds worse than you'd expect. The monocular cascade retains less than 1% of the original signal after 7 stages.

After the binocular experiments (Document 4), we know part of the solution: two eyes with subtractive cross-connections. But the binocular system had many knobs -- dual channels, inhibitory cross-connections, predictive coding (system-aware optimization), and external grounding (periodic exposure to uncontaminated signal). Which of these knobs are essential? Which are nice-to-have? Which are irrelevant?

We answered this the old-fashioned way: take the full system, remove one component at a time, and measure how badly things break.

---

## The Ablation

We started with the complete architecture -- dual channels (N = 2), inhibitory cross-connections (w_cross < 0), predictive coding (system-aware weights), and external grounding (periodic ground truth exposure) -- running through the full 7-stage biological cascade. Then we removed each component in turn.

| Component removed | Final R^2 | Degradation from full system | Status |
|------------------|----------|------------------------------|--------|
| Nothing (full system) | 0.802 | -- | STABLE |
| Dual channels (N = 2 to N = 1) | 0.017 | 97.8% collapse | **NECESSARY** |
| Inhibitory cross-connections | 0.017 | 97.8% collapse | **NECESSARY** |
| Predictive coding | 0.610 | 24.0% degradation | HELPFUL |
| External grounding | 0.810 | -1.0% (actually improved) | REDUNDANT |
| Forced positive cross-connections | 0.007 | 99.2% collapse | CATASTROPHIC |

Let's walk through what each result tells us.

---

## The Two Things You Must Have

**Dual channels: removing them collapses the system by 97.8%.** Going from two channels to one drops R^2 from 0.802 to 0.017. That's going from perceiving 80% of the signal to perceiving less than 2%. The reason is what we established in Documents 1 and 4: a single channel has one equation (its observation y(t) = s(t) + contamination) and two unknowns (the signal and the contamination). There's no way to separate them. With two channels, you have two equations for two unknowns -- not because you've doubled your data, but because the two contamination terms are different, giving you leverage to solve the system.

**Inhibitory cross-connections: removing them collapses the system by 97.8%.** This is the same number as removing dual channels, which is not a coincidence. Dual channels *without* inhibitory cross-connections produce R^2 = 0.017 -- identical to a single channel. Why? Because two channels that don't interact learn the exact same weights. They receive the same signal, compute the same gradient, and converge to the same solution. Two identical eyes are the same as one eye. The inhibition is what *forces* the channels to develop different behaviors, creating the diversity that makes parallax possible.

**Forced positive cross-connections are worse than nothing.** R^2 = 0.007, compared to 0.017 for no cross-connections at all. Positive coupling amplifies contamination instead of removing it. If one channel is slightly off, the other channel incorporates that error, amplifying it further. This is groupthink in two-unit form: the channels reinforce each other's mistakes.

So the first critical finding is: **dual naive equals monocular**. Having two eyes pointed at the same thing with the same brain is the same as having one eye. The cross-connections don't merely help the dual channels -- they are the mechanism that *creates* the benefit of having dual channels.

---

## The Thing That Helps

**Predictive coding (system-aware optimization): removing it costs 24%, but the system stays stable.** R^2 drops from 0.802 to 0.610. Substantial, but not catastrophic. The system still works -- it's just not as good.

Predictive coding corresponds to using the system-aware weight w_sys = (1 - alpha^2 * w^2)^2 instead of the myopic weight from alpha^2 * w^2 + w - 1 = 0. As we discussed in Document 2, this corrects the myopic overestimate of signal strength at each stage. The improvement compounds through the cascade: a 9.5% per-stage improvement at alpha = 1.0, compounded over 7 stages, gives roughly 60% total improvement in final R^2.

This is the SOR (successive over-relaxation) fix from Document 2, applied at every stage. It's valuable, but the system doesn't depend on it for survival.

---

## The Thing You Don't Need

**External grounding: removing it actually *improves* R^2 by 1%.** This was the surprise. We expected periodic exposure to uncontaminated signal to be essential -- surely you need some anchor to reality?

Turns out, when the dual-channel inhibitory architecture is working properly, the internal decontamination mechanism is self-sufficient. The two channels, subtracting each other's contamination, provide their own "reality check." Adding periodic ground-truth exposure slightly disrupts the steady-state learning dynamics, causing a tiny performance dip.

This doesn't mean grounding is never useful. For a *monocular* system (single channel, no cross-connections), grounding is the only defense against drift. Without it, a monocular system at alpha = 1.0 needs grounding at g >= 0.25 just to maintain stability. But when the architecture is correct, grounding is a fallback, not a requirement.

---

## The Architecture Taxonomy

Putting it all together:

| Architecture | Dual (N >= 2) | Inhibition (w < 0) | Predictive | Grounding | Final R^2 | Status |
|-------------|--------------|-------------------|-----------|----------|----------|--------|
| Raw Monocular | No | No | No | No | 0.008 | COLLAPSED |
| Dual Naive | Yes | No | No | No | 0.008 | COLLAPSED |
| Dual Inhibitory | Yes | Yes | No | No | 0.433 | STABLE |
| Dual + Predictive | Yes | Yes | Yes | No | 0.810 | STABLE |
| Full MVSU | Yes | Yes | Yes | Yes | 0.802 | STABLE |

The jump from row 2 to row 3 is the critical transition: adding inhibitory cross-connections to dual channels transforms a collapsing system (R^2 = 0.008) into a stable one (R^2 = 0.433). This is a **54x improvement** from the single architectural change that matters most.

And look at the efficiency: the MVSU has 4 parameters per stage (2 w_self + 2 w_cross). The monocular system has 1 parameter. With 4x the parameters, the MVSU achieves **46x the R^2**. The improvement is super-linear because the cross-connections create qualitatively new capability -- decontamination -- that cannot be achieved by making a single-channel system bigger or training it longer.

---

## The Biological Mapping

This architecture has direct biological counterparts:

| Component | In the brain | In AI/ML | When it's missing |
|-----------|-------------|---------|-------------------|
| Dual channels | Two hemispheres, two eyes, two ears | Dual reward models, ensemble methods | Echo chamber -- single viewpoint amplifies its own errors |
| Inhibitory cross-connections | Inhibitory interneurons (20-30% of cortical neurons) | Negative correlation training, adversarial components | Groupthink -- channels converge to identical behavior |
| Predictive coding | Prediction error neurons (layer 2/3 pyramidal cells) | System-aware training, meta-learning | Rigid models -- no adaptation to self-influence |
| External grounding | Sensory input, proprioception | Human labels, holdout benchmarks | Psychosis (if monocular) -- untethered from reality |

The percentage of cortical neurons that are inhibitory -- 20 to 30% -- now makes more sense. These aren't merely regulatory circuits. They're *structurally necessary* for stable information processing in any self-referential system. Without inhibition, recurrent circuits collapse into echo chambers. The brain doesn't have inhibitory interneurons as a luxury; it has them because the mathematics of self-referential processing demands them.

And consider the failure modes:

- Remove dual channels: you get monocular vision, hemineglect -- a single perspective that can't distinguish its own biases from reality.
- Remove inhibition: you get runaway excitation -- epilepsy at the neural level, mode collapse at the AI level, groupthink at the organizational level.
- Remove predictive coding: you get sensory flooding, inability to adapt to your own influence -- rigidity.
- Remove grounding (when monocular): you get psychosis, derealization, confabulation -- a system generating its own reality without external constraint.

Each clinical pathology maps to a missing component of the MVSU. The architecture isn't just mathematically minimal; it's biologically minimal. Evolution converged on the same answer.

---

## The MVSU Specification

The Minimum Viable Stable Unit, in its simplest form:

    For each processing stage:
      - 2 channels, each independently processing the full signal
      - Cross-connections with learned negative weights (w_cross, optimal near -0.26)
      - T = 2 processing depth (one step to receive, one to integrate)
      - Total: 4 learnable parameters per stage

    Recommended addition:
      - System-aware weight optimization (predictive coding): +60% R^2

    Not needed when architecture is correct:
      - External grounding (only needed as fallback for monocular systems)

---

**The key insight:** The architecture matters more than the algorithm. Two channels with inhibitory coupling preserve nearly 50x more signal than a single channel, regardless of how sophisticated the single channel is. This is not an optimization tip -- it's a structural requirement imposed by the mathematics of self-referential processing. You can't solve the self-reference problem by making a single channel smarter. You need a second viewpoint and a subtraction operator.
