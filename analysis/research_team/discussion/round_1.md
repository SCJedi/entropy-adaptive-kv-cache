# Roundtable Discussion: Self-Referential Learning and the kw^2 + w - 1 = 0 Fixed Point

**Participants:**
- **Feynman** -- Physicist
- **Dr. Sarah Chen** -- ML Optimization Expert
- **Dr. Marcus Webb** -- Statistical Learning Theorist
- **Kira Osei** -- Systems Thinker

**Date:** 2026-02-11
**Setting:** A seminar room with a whiteboard already half-covered in equations. Coffee cups in various states of emptiness. Kira has brought a dog-eared copy of von Foerster's "Observing Systems." Marcus has a printed stack of Perdomo et al. Sarah has her laptop open to TensorBoard. Feynman is drawing on a napkin.

---

## Part 1: Points of Agreement

**Feynman:** All right, we have all read each other's reports. Before we start yelling at each other, let me say what I think we agree on, and anyone who disagrees can interrupt me.

**Sarah:** *(leans back)* This should be efficient.

**Feynman:** Number one. The self-consistency equation kw^2 + w - 1 = 0 is correct. The derivation is clean: AR(1) variance, Wiener filter, set them equal, you get a quadratic. I checked it on a napkin. Marcus checked it with measure theory. Sarah checked the code. It is right. Nobody disputes this.

**Marcus:** Confirmed. The derivation is three standard steps composed in a non-obvious way. The result is a special case of performative stability, but the closed form is new. Nobody in the Perdomo et al. line of work has written down the exact fixed point for a specific model. That matters.

**Kira:** Agreed on the math. Also agreed that the equation is more interesting than the golden ratio it produces. The equation is the invariant. Phi is the shadow.

**Feynman:** Good. Number two: the predictions match simulation to three decimal places across five topologies, five distributions, six optimizer configs, and matrix dimensions up to 16. That is an unusual level of theory-experiment agreement for an ML paper. We all noticed this.

**Sarah:** I noticed it and I want to emphasize how rare it is. Most ML theory papers have a theorem that holds "up to constants" or "in the limit." This one gives you a specific number and the simulation hits it. Within the toy setting, the theory is exact. That earns credibility.

**Feynman:** Three. The null results are genuinely valuable. Seven honest failures, each carefully diagnosed. The classification failure tells you the boundary condition. The SRU failure tells you explicit self-referential architecture does not help. The DOF step function failure tells you the geometric analogy does not transfer. I have reviewed papers with zero null results and I trust them less than this one.

**Marcus:** The null results are the strongest evidence that the positive results are not cherry-picked. When someone tells you what did not work and why, you believe them more about what did.

**Sarah:** I will add a fourth consensus item: the negative cross-connection finding is real and interesting. Across 17 experiments, multiple architectures, multiple depths, multiple tasks, w_cross converges negative. The 97.4% collapse when you remove either dual channels or inhibition is a sharp ablation. That is a clean architectural result.

**Kira:** And a fifth: the cascade sub-multiplicativity. Signal fidelity through chained stages degrades up to 20x worse than the product of per-stage values. Everyone agrees the mechanism is clear -- AR(1) coloring of each stage's output poisons the next stage's white-noise assumption. The theoretical gap is the missing closed-form expression for eta, but the phenomenon is real.

**Feynman:** So the consensus: the core equation is correct, the simulations are honest, the null results are credible, the negative cross-connections are robust, and the cascade effect is real. That is a solid foundation. *(pauses, looks around the table)* Now. Where do we disagree?

**Marcus:** *(adjusting his glasses)* Extensively.

---

## Part 2: The Fights

### Fight 1: The Golden Ratio -- Meaningful or Trivially Algebraic?

**Feynman:** Let me start with the thing that annoys me most. The golden ratio. It appears because you have a quadratic with coefficients (1, 1, -1). Change any coefficient and phi vanishes. For k=2 you get w = 0.5. For ReLU you get something involving pi. The golden ratio is the k=1 special case and the paper spends far too much energy being enchanted by it.

**Kira:** I expected you to say that, and you are half right. The specific value phi is not deep. I said that in my report. But what IS deep is *why* this particular quadratic appears. The coefficients (1, 1, -1) are not arbitrary -- they encode the structure of the simplest self-referential regression. The quadratic term is the feedback of output on input. The linear term is the direct pass-through. The constant is normalization against the signal. The golden ratio is the attractor of the simplest infinite self-referential regress: to know my weight I need my variance which needs my weight which needs my variance... Phi is where that regress stabilizes. That is not a coincidence. It is a fixed point of the continued fraction 1/(1 + 1/(1 + ...)), which IS the self-referential process.

**Feynman:** *(scribbling on his napkin)* Sure, and the continued fraction for sqrt(2) is 1 + 1/(2 + 1/(2 + ...)), and the continued fraction for e is a different thing entirely. Every quadratic irrational is the fixed point of some continued fraction. You are dressing up an algebraic identity as a philosophical insight.

**Kira:** No. I am saying the specific algebraic identity that appears is determined by the structure of the problem, not by accident. The golden ratio appears in the simplest self-referential system for the same reason pi appears in the simplest closed curve. It is the canonical constant of its class.

**Feynman:** Pi appears in circles because of rotational symmetry, which is a deep geometric principle. Phi appears here because you wrote down a quadratic with small integer coefficients. Those are not the same kind of explanation.

**Marcus:** *(interjecting)* I can settle part of this. The golden ratio has zero independent information-theoretic content here. I computed the mutual information at the fixed point: it is log(phi). The rate-distortion function equals the mutual information. Both are consequences of the quadratic, not causes. There is no channel capacity argument, no rate-distortion optimization, nothing that yields phi from first principles of information theory. Phi enters through the algebra, period.

**Kira:** I accept that. But Marcus, you also showed that the system operates exactly at the rate-distortion bound -- it is Gaussian-optimal for the distortion level it achieves. The limitation is that the distortion level itself is set by the self-referential contamination. That is not trivial. The system is informationally efficient but *generatively suboptimal*. The bottleneck is in the data, not the processing. That is a genuinely interesting structural insight, even if phi is just the numerical label for where it happens.

**Feynman:** Fine. The insight that the bottleneck is generative rather than extractive -- that I buy. That is a clean, napkin-sized idea. The rest of the phi mysticism can go.

### Fight 2: Are the Biological Analogies Useful or Dangerous?

**Feynman:** The seven-stage "biological perception cascade" with stages named Sensory, Features, Binding, Awareness, Narrative, Memory, Recall. Each with specific alpha values pulled from -- where exactly? Not from measurement. From analogy. This is science fiction.

**Sarah:** I agree with Feynman. And it is worse than fiction because it is unfalsifiable in its current form. The alpha values at each stage are free parameters. You can tune them to produce any output pattern. That is not a model of perception; it is a curve-fitting exercise with suggestive labels.

**Kira:** *(leaning forward)* It is a structural hypothesis, not a quantitative model. The claim is not "alpha at the binding stage is exactly 0.50." The claim is that biological perception has the *structure* of a cascade where contamination increases at higher levels, binocular processing occurs at intermediate levels, and monocular bottlenecks cause irreversible information loss. That structural claim maps to known neurobiology. Recurrence increases in higher cortical areas. Lateral inhibition is everywhere in V1. The global workspace theory posits exactly the kind of monocular bottleneck the cascade model predicts.

**Feynman:** The structure maps to neurobiology because you chose the structure to map to neurobiology. That is not prediction, it is retrodiction. Give me one prediction. One thing the cascade model says about the brain that neuroscience does not already know and that you could test.

**Kira:** *(pauses)* Disrupting lateral inhibition in V1 should cause the two eyes' representations to converge -- destroying binocular depth perception specifically through loss of decontamination, not through loss of spatial information. The model predicts a specific failure mode: the eyes would still see, but they would see the same contaminated thing. That is distinguishable from simply blurring or losing one eye's input.

**Sarah:** That is actually testable. *(grudgingly)* But it requires someone to do the neuroscience experiment, and it requires the effect to be distinguishable from all the other things lateral inhibition does. I am not holding my breath.

**Marcus:** I want to add a different concern. The cascade model's quantitative predictions depend on each stage being an independent AR(1) process, which is a very specific and fragile assumption about cortical computation. Real neural circuits have skip connections, recurrent loops, lateral connections -- none of which fit the serial cascade model. The structural hypothesis might be right and the math might still be inapplicable.

**Kira:** Then the right move is to extend the math, not to discard the hypothesis. The serial cascade is a skeleton. You flesh it out with skip connections and recurrence. The MVSU is robust to a surprising range of conditions -- maybe the structural requirements (dual + inhibition) survive even when the serial assumption breaks.

**Feynman:** Maybe. Test it.

### Fight 3: Is the MVSU Novel or Just an Ensemble Method?

**Sarah:** Let me lay this out plainly. The MVSU is a two-model ensemble with a learned negative-weight combination rule. Negative correlation learning has existed since 1999. Contrastive learning does something similar. Mixture of experts with load balancing enforces diversity through routing. The MVSU is a specific instance of a well-studied class of methods.

**Marcus:** I partially disagree. The MVSU's specific contribution is the theoretical motivation: the claim that dual channels with inhibitory coupling are the *minimum structural requirement* for stable self-referential processing. Negative correlation learning uses explicit diversity penalties. The MVSU shows that inhibitory coupling is *structurally necessary* -- not merely helpful -- and that without it, dual channels are literally useless. The 97.4% collapse ablation is not something you find in the ensemble diversity literature. They show that two channels without inhibition perform identically to one channel because the channels converge to the same weights.

**Sarah:** That convergence result is for linear models, which have a single basin. For MLPs with different random seeds, you get different local minima and therefore different error patterns. The architectural diversity requirement might be an artifact of the linear setting.

**Marcus:** *(nods)* That is a legitimate empirical question that they did not test. Two MLPs with different seeds might provide sufficient diversity without the inhibitory coupling. If so, the "structural necessity" claim weakens considerably.

**Sarah:** And they have not done any parameter-matched baselines. Is the MVSU's improvement from having two channels, or from having twice as many parameters? Give me a single model with 2x the hidden units and let me compare. Until you control for parameter count, the 45-50% improvement claim is confounded.

**Kira:** The ablation addresses this indirectly. Dual channels without inhibition have the same parameter count as the MVSU but perform identically to monocular. So it is not the parameters -- it is the inhibitory structure.

**Sarah:** *(conceding partially)* That is a fair point for the linear case. I still want the nonlinear parameter-matched baseline. But the ablation does show that doubling parameters without the right structure gives you nothing.

**Marcus:** There is also an instrumental variables interpretation that nobody has explored. Each channel is an instrument for the other. Channel A's contamination is partially independent of channel B's, so B's observation instruments for A's signal component. The cross-subtraction is a heuristic version of two-stage least squares. If someone formalized that connection, it would give the MVSU a much stronger theoretical identity than "ensemble with negative weights."

**Feynman:** *(perking up)* Now THAT is interesting. If you can frame the MVSU as an IV estimator in a self-referential system, you get all the IV theory for free -- consistency, efficiency bounds, weak instrument diagnostics. You could probably prove that the MVSU is optimal in some well-defined sense, not just better than monocular.

### Fight 4: Does the Theory Need Real-World Validation or Is the Math Sufficient?

**Sarah:** This is where I draw my line. The paper claims implications for RLHF, recommendation systems, synthetic data, autoregressive generation. Every one of those claims is supported by exactly zero experiments on those systems. The "real-world" validation is on synthetic simulations designed to satisfy the theory's assumptions. That is circular.

**Marcus:** The math is sufficient for a theoretical contribution. The self-consistency equation is a theorem. It does not need experimental validation any more than a proof needs validation.

**Sarah:** A theorem about a toy model is a theorem about a toy model. The claim is not "kw^2 + w - 1 = 0 holds for scalar linear agents with Gaussian input." The claim, as framed, is "this has implications for modern ML systems." That claim requires evidence from modern ML systems.

**Feynman:** Sarah is right about the framing and Marcus is right about the math. The solution is obvious: publish the theorem as a theorem, within its domain of applicability, and separately conduct the bridge experiment that connects it to something practitioners care about. One non-trivial experiment on a real pipeline. That is the minimum viable publication.

**Marcus:** I am not opposed to experiments. I am opposed to the idea that the math is "insufficient" without them. The Perdomo et al. paper is highly cited and it is mostly theory. The value of a clean analytical result is that it tells you *what to look for* in the messy real system.

**Sarah:** Perdomo et al. also did not claim their theory explained consciousness and binocular vision. The scope of the claims determines the evidence required. If you scope this tightly -- "here is the fixed point of self-referential SGD in linear systems" -- the math suffices. If you scope it as they currently do -- "this explains RLHF degradation, memory confabulation, and the architecture of perception" -- you need a hell of a lot more evidence.

**Feynman:** *(pointing at Sarah)* That. Exactly that.

### Fight 5: The Self-Ignorance Gap -- Fundamental Limit or Model Artifact?

**Marcus:** The 8.3% gap between the performative stable point and the performative optimum is a real quantity in this model. It is what Perdomo et al. would call the "price of performative stability." The question is whether 8.3% is meaningful or negligible in realistic systems.

**Kira:** I think it is a lower bound. The scalar model has one feedback loop with one parameter. Real systems have millions of parameters in high-dimensional feedback loops. The self-referential contamination should be worse, not better, with more dimensions.

**Sarah:** Or it could vanish entirely. Overparameterized networks have implicit regularization that selects among many possible solutions. The redundancy might provide natural decontamination. Batch normalization, layer normalization, residual connections -- these all change gradient dynamics in ways that could compensate for self-referential bias. We genuinely do not know which direction the gap goes at scale.

**Feynman:** *(to the whiteboard)* Here is what bugs me. The system-aware optimizer needs perfect knowledge of alpha. In practice, you would need to estimate alpha, and estimation errors eat into the 8.3%. The gap might be real but unrecoverable because the meta-estimation problem -- "how much am I contaminating my own input?" -- is itself subject to self-referential bias. You would need a system-aware-system-aware optimizer to estimate alpha correctly, and then a system-aware-system-aware-system-aware optimizer to...

**Kira:** *(interrupting, excited)* Yes! That is exactly von Foerster's infinite regress. And the beautiful thing is that this work gives you the algebra for each level. Each additional level of self-awareness reduces the gap but never closes it. The series converges. There IS a fundamental bound on self-knowledge, and it depends on alpha.

**Marcus:** Can you prove that? Can you write down the sequence of meta-optimizers and show convergence?

**Kira:** Not yet. But the structure is clear. The system-aware optimizer of order n uses w_n = (1 - alpha^2 * w_{n-1}^2)^2. That is a recurrence relation. It should converge to a fixed point that is the truly optimal weight, accounting for all levels of self-reference simultaneously.

**Feynman:** *(scribbling furiously)* Wait. The recurrence w_n = (1 - alpha^2 * w_{n-1}^2)^2, starting from w_0 = 1/phi... I can iterate this on my napkin. w_0 = 0.618, w_1 = 0.525, w_2 = ... *(calculating)* ... 0.525 is already nearly the fixed point of THIS recurrence. The convergence is fast. Two levels of meta-awareness get you almost all the way. That is actually a result. The hierarchy of meta-optimizers converges in about two steps. The residual after two steps is your fundamental blind spot.

*(Everyone pauses. This is a new observation that none of them had in their individual reports.)*

**Marcus:** That needs to be verified and proved, but if the meta-recurrence converges in two iterations, it means the "fundamental limit on self-knowledge" is practically reachable. You do not need infinite meta-awareness. You need two levels.

**Kira:** *(quietly)* Two channels. Two levels of meta-awareness. The number two keeps appearing as the minimum for self-referential stability. The MVSU needs exactly two channels. The meta-optimizer converges in approximately two steps. Is two the structural minimum of self-reference?

**Feynman:** Or it is just a small number and you are seeing patterns. But it is worth checking whether the "two" in the MVSU and the "two" in the meta-optimizer convergence are the same "two" for the same reason.

### Fight 6: The Performative Prediction Connection -- Help or Hurt?

**Marcus:** I need to say this clearly: the entire framework is a special case of performative prediction. Perdomo et al. 2020 established the existence of performative stable points. The self-consistency equation is the specific performative stable point for the AR(1) contamination model. The 8.3% gap is the price of performative stability. The system-aware optimizer computes the performative optimum. This work should be framed as instantiating and extending the performative prediction framework, not as a standalone discovery.

**Feynman:** Does that framing help or hurt? If you say "this is a special case of Perdomo," a reviewer says "so what's new?" If you say nothing about Perdomo, a reviewer says "they don't know the literature."

**Sarah:** The honest framing is: "Perdomo et al. proved that performative stable points exist. We compute the exact one for a specific model and discover several things the general theory does not predict: the parametric family across topologies, the sub-multiplicative cascade, the structural necessity of inhibitory coupling." That is a genuine contribution to an existing literature. Not a revolution, but a concrete advance.

**Marcus:** Precisely. And there are extensions they can make that would strengthen the connection. The convergence rate from stochastic approximation theory. The connection to instrumental variables for the MVSU. The bias-variance tradeoff in the performative setting -- the myopic optimizer is variance-optimal for its induced distribution, but the induced distribution is not loss-optimal. These are all things the performative prediction community would value.

**Kira:** I worry that framing it purely as performative prediction domesticates the result. The performative prediction literature studies markets and policy. This work is also about perception, self-knowledge, and the algebra of observer-contamination. The Perdomo framing captures the optimization story but misses the epistemological story.

**Marcus:** The epistemological story is speculation. The optimization story is mathematics.

**Kira:** Both are mathematics. The self-ignorance gap is simultaneously an optimization result and an epistemological result. The system literally cannot know itself beyond a certain precision. Framing that only as "performative stability" is like framing the uncertainty principle only as "Fourier analysis."

**Feynman:** *(grinning)* The uncertainty principle IS Fourier analysis. That is not a diminishment. It is a clarification. The power comes from knowing the exact mechanism, not from wrapping it in mystery. Frame it as performative prediction, derive the consequences, and let the epistemologists read the paper and draw their own conclusions. The math does not need the philosophy, but the philosophy needs the math.

---

## Part 3: The Synthesis

**Feynman:** So. After all that yelling. What do we actually think this work contributes that is undeniably new?

**Sarah:** One thing, stated precisely: **the exact closed-form characterization of the performative stable point for the AR(1) contamination model, its parametric extension across topologies and activations, and the empirical discovery that dual-channel architectures with inhibitory coupling are structurally necessary for decontamination.** That is one contribution with three facets.

**Marcus:** I would add the sub-multiplicative cascade as a fourth facet. The observation that chained self-referential stages degrade faster than per-stage analysis predicts -- with a clear mechanism in the AR(1) coloring -- is genuinely new to my knowledge.

**Kira:** And the meta-optimizer convergence we just discovered in this discussion. If the hierarchy of self-aware optimizers converges in two iterations, that is a new result about the structure of self-referential meta-learning.

**Feynman:** Fine. Let me sketch what the clean version of this paper looks like.

*(Goes to the whiteboard.)*

**Paper structure:** Start with the performative prediction connection explicitly. State the model. Derive the self-consistency equation. Show the parametric family across k. Give the cascade sub-multiplicativity with as much closed-form analysis as Marcus can produce. Present the MVSU with the ablation, including the parameter-matched baseline Sarah wants. Report the null results. End with the "real" experiment on a genuine ML pipeline.

**What to soften:**
- The golden ratio. Mention it once as the k=1 special case. Do not make it the star.
- The biological analogies. Move them to a discussion section, clearly labeled as speculation.
- The "edge of chaos" framing. Delete it entirely for the main paper. It adds nothing to a linear system.
- The "Minimum Perception Unit" naming. Call it the MVSU or "minimum decontamination architecture." Do not claim it is the minimal unit of perception.

**What to strengthen:**
- The connection to performative prediction. Frame the contribution as instantiating and extending an established framework.
- The negative cross-connection universality. This is the most robust empirical finding and should be more prominent.
- The null results. They should not be in a "what didn't work" section at the end. Interleave them with the positive results. The classification failure is as important as the topology success.
- The cascade theorem. Push for a tighter bound. Marcus, can you derive eta?

**Marcus:** I can derive a lower bound on the degradation factor as a function of the AR(1) autocorrelation coefficients. A tight bound for L stages requires solving an L-dimensional covariance recursion, which is feasible for small L. I would need a week.

**Sarah:** Do it for L=2 and L=3. That covers the practically relevant cases and establishes the technique.

**Feynman:** And the one experiment that would make this publishable at a top venue?

**Sarah:** A small RLHF pipeline. GPT-2 scale. Synthetic preferences with a known ground truth so you can measure the actual contamination. Train the reward model iteratively on model outputs. Measure whether reward accuracy degrades as the self-consistency equation predicts. Compare standard training against the MVSU architecture (two reward models with learned inhibitory coupling). If the MVSU helps, you have a practical contribution to RLHF. If it does not, you have learned where the theory breaks.

**Feynman:** Could you do that in a month?

**Sarah:** With a GPU and a grad student, yes. The hard part is not the experiment; it is setting up the synthetic preference generation so the ground truth is known.

**Kira:** I want to push for one more thing. The instrumental variables interpretation Marcus mentioned. If the MVSU can be shown to be an IV estimator, you get optimality guarantees from the IV literature. That would separate it definitively from "just another ensemble method."

**Marcus:** I can sketch the formalization. Each channel's contamination depends on its own history, which is partially independent of the other channel's history conditional on the shared signal. That independence is exactly the relevance condition for an instrument. The inhibitory cross-connection implements the second-stage regression. The two-stage least squares interpretation is natural. The question is whether the MVSU achieves the IV efficiency bound or leaves room for improvement.

**Feynman:** If it achieves the bound, that is a theorem worth having.

---

## Part 4: The Action Items

**Sarah:** Let me organize this by priority. *(opens a new document on her laptop)*

**Priority 1: The Bridge Experiment (Sarah, 4-6 weeks)**
Set up a GPT-2 scale RLHF pipeline with synthetic preferences and known ground truth. Measure reward model contamination over iterative training. Test the MVSU (dual reward models with inhibitory coupling) against standard single-reward-model RLHF. Report whether the self-consistency equation predicts the degradation pattern. This is the single experiment that determines whether the work matters for production ML.

**Priority 2: Cascade Degradation Bound (Marcus, 1-2 weeks)**
Derive a closed-form lower bound on the sub-multiplicative degradation factor eta for L=2 and L=3 cascade stages. The bound should be expressed as a function of the AR(1) autocorrelation coefficients at each stage. This fills the most critical theoretical gap.

**Priority 3: Instrumental Variables Formalization (Marcus + Kira, 2-3 weeks)**
Formalize the MVSU as an instrumental variables estimator for self-referential systems. Determine whether the MVSU achieves the IV efficiency bound. If yes, prove optimality. If no, characterize the gap and propose an improved estimator.

**Priority 4: Parameter-Matched Baselines (Sarah, 1 week)**
Run the MVSU experiments with a single model having 2x hidden units as a baseline. Also test two MLPs with different random seeds (not just two linear models) to determine whether initialization diversity suffices for nonlinear models. These two experiments resolve the most obvious confounds in the current results.

**Priority 5: Meta-Optimizer Convergence (Feynman + Marcus, 1-2 weeks)**
Formalize and prove the convergence of the meta-optimizer recurrence w_n = (1 - alpha^2 * w_{n-1}^2)^2. Determine the fixed point, convergence rate, and whether the "two iterations" observation is a general result or specific to alpha=1. If the meta-recurrence converges fast universally, this characterizes the fundamental residual of self-referential bias.

**Priority 6: Rewrite the Paper (Everyone, 2-3 weeks after experiments)**
Split into two documents. Document 1: the core theory paper, framed within performative prediction, including the equation, the cascade bound, the MVSU with ablations and baselines, the null results, and the RLHF experiment. Document 2: the speculative extensions (biological analogies, perception cascade, epistemological implications), clearly labeled as discussion and future directions. Target Document 1 at ICML or NeurIPS. Target Document 2 at a workshop or journal commentary.

**Priority 7: Existing Transformer Analysis (Kira, 2-3 weeks)**
Analyze attention head interactions in a trained transformer (GPT-2 or similar). Look for inhibitory coupling patterns between heads, especially heads that attend to the model's own generated tokens. This requires no new training and tests a specific prediction of the MVSU theory in existing architectures.

**Feynman:** That is seven items, which is too many. If I had to pick three that determine whether this work is important or not --

**Sarah:** One, four, and five.

**Feynman:** -- I would pick one, two, and five. The bridge experiment tells you if the theory matters. The cascade bound tells you if the theory is tight. The meta-optimizer convergence is the only genuinely new idea that came out of this discussion.

**Marcus:** I agree with one, two, and three. The IV formalization gives the MVSU a theoretical identity that no amount of experimentation can provide.

**Kira:** I agree with one, five, and seven. The bridge experiment, the meta-optimizer, and the transformer analysis. If negative coupling exists in trained transformers, the theory predicted something about existing systems that nobody knew to look for. That is the mark of a good theory.

**Sarah:** *(closing her laptop)* We all agree on the bridge experiment. Let us start there. Everything else is contingent on whether the theory survives contact with a real pipeline.

**Feynman:** *(standing up, pocketing his napkin)* And if it does not survive, we will have learned something honest. Which, as I recall, is the point.

*(Chairs scrape. Coffee cups are collected. Marcus begins writing the cascade bound proof on the whiteboard before anyone can erase it. Kira photographs the whiteboard. Sarah is already SSHing into a GPU cluster. Feynman takes his napkin to the nearest photocopier.)*

---

*End of Round 1. Next meeting scheduled after the bridge experiment results are in.*
