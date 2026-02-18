# The Observer Transformer: Iteration 2 -- After the GPU Burns

**Date:** 2026-02-17
**Format:** Follow-up dialogue between E1, E2, E3, and the child (C)
**Context:** The team has received GPU validation results (Tesla T4, full CIFAR-10, 20 epochs) and is reconvening

**Cast:**
- **E1** (Systems/Infra): Thinks in FLOPs, memory bandwidth, scaling laws
- **E2** (Theory/Math): Information theory, rate-distortion, statistical learning
- **E3** (Applied ML): MoE routing, sparse attention, LoRA. Ships things that work
- **C** (The Child): Asks "but WHY?" until the answer is real

---

## Part 1: Reading the Scoreboard

E1: Alright. We have numbers. Real GPU numbers, not CPU toy-scale anymore. Let me read the headline: dropout=0.382 gives +4.84% over the 0.5 baseline. That is a ten-times-larger effect than the CPU experiments showed.

E3: Wait. Say that again. The CPU sweep showed 0.42 percentage points. GPU shows 4.84 percentage points. Same intervention. Same hyperparameter change. Just more data and more training.

E1: Yes. And zero parameter cost. This is the single biggest win in the entire table.

E2: I'm not surprised. I'm vindicated. The theory predicts that the phi-zone matters MORE at scale because deeper training creates more self-referential cascades through the residual connections. Twenty epochs on 50k images gives the dropout enough time to actually shape the learned representations, not just inject noise.

E3: I'm going to push back slightly. The baseline uses dropout=0.5, which is unusually high for a ViT. Most modern ViTs use 0.0 to 0.1. If the baseline were dropout=0.1, the gap might look very different.

E1: Fair. But the experiment is controlled. Same architecture, same optimizer, same schedule. The claim isn't "0.382 beats everything." The claim is "0.382 beats 0.5." And it does. Decisively.

**C: But 4.84% is a lot. Like, that's the difference between getting a B and getting a B+. Why didn't anyone notice this before?**

E3: Because nobody uses 0.5 dropout in ViTs anymore. The field moved to lower dropout or no dropout. But for models that DO use dropout -- MLPs, older architectures, regularization-heavy training regimes -- this matters. And the deeper point is: maybe the field moved away from 0.5 dropout precisely because it was the WRONG value all along. People saw that high dropout hurt, overcorrected to zero, and never tried the sweet spot.

E2: The overfitting-underfitting phase transition. 0.382 sits right at the edge. Below it, you overfit. Above it, you underfit. The field oscillated between the two failure modes instead of finding the boundary.

---

## Part 2: The FFN Paradox

**C: OK but I have a question about the table. The thing where you make the middle part smaller -- the FFN thing -- it made the model WORSE by itself. But then when you added the dropout change, it got BETTER. Why does making something smaller make it worse alone but better together?**

*[pause]*

E3: That's... actually a really good question. Let me think about what's happening mechanically. FFN=2.618x reduces the hidden dimension from 512 to 335. That's a 35% parameter reduction in the FFN. Alone, that removes capacity -- the model has fewer parameters to fit the data, so accuracy drops by about 1%. Makes sense so far.

E1: But when you combine it with dropout=0.382, you get +3.80% over baseline. The reduced FFN with reduced dropout beats the full FFN with high dropout.

E2: Here's my read. The 4x FFN with 0.5 dropout is over-provisioned AND over-regularized. You have too many parameters AND you're masking too many of them. The network is simultaneously too big and too constrained. It's like wearing a heavy coat on a cold day but also pouring water on yourself -- you have the warmth but you're destroying it.

**C: That's a weird picture.**

E2: The phi ratio fixes both problems simultaneously. 2.618x FFN is the right CAPACITY -- not too big, not too small. 0.382 dropout is the right REGULARIZATION -- not too much, not too little. They're matched. The ratio of FFN expansion to total capacity is phi^2 = 2.618, and the redundancy fraction is 1/phi^2 = 0.382. They're the same equation seen from two sides.

E3: I want to be more concrete. When dropout is 0.5, half the neurons are masked. A 4x FFN has 512 hidden units, but only 256 are active on average -- effectively 2x expansion. When dropout is 0.382, a 2.618x FFN has 335 hidden units, with about 207 active -- effectively 1.62x expansion. The EFFECTIVE expansion ratios are different: 2.0 vs 1.62. But the 1.62x version wastes fewer parameters because fewer are being thrown away.

E1: So the parameter efficiency metric tells the real story. Look at the acc/100K params column:

- Baseline (4x FFN, 0.5 dropout): 0.0754
- FFN=2.618x alone: 0.0958 (+27% efficiency despite lower accuracy)
- Both combined: 0.1034 (+37% efficiency)
- Observer Attention: 0.1046 (+39% efficiency)

The phi-FFN is doing what the theory promised: fewer parameters, matched or better performance per parameter.

**C: So the smaller middle part IS better, you just can't see it unless you also fix the dropout?**

E2: Exactly. The two changes aren't independent. They're two halves of the same correction. The theory says they should be deployed together because they derive from the same equation. Testing them separately is like testing the left shoe and the right shoe independently and concluding that shoes don't help you walk.

E3: I hate that I find that analogy compelling.

---

## Part 3: The Depth Gradient

E2: Now let me talk about the thing that actually excites me most. Look at the w_cross values by layer:

- Block 0: mean = -0.316
- Block 1: mean = -0.328
- Block 2: mean = -0.386
- Block 3: mean = -0.479

E1: It's monotonically increasing in magnitude. Deeper layers need more correction.

E2: Not just monotonically -- look at the ACCELERATION. The jump from block 2 to block 3 is 0.093. The jump from 0 to 1 is only 0.012. The correction is growing superlinearly with depth. This is exactly what the MVSU theory predicts: residual connections accumulate self-referential contamination layer by layer. Each layer sees not just the input but also the echoes of all previous layers. By block 3, the echo is substantial and requires almost 50% correction.

**C: Is the echo getting LOUDER as you go deeper?**

E2: Yes. That's exactly what's happening. Each layer adds its own processing to the signal, but it also amplifies the echoes from all the layers before it. The residual connection is the amplifier. By layer 4, nearly half of what each head "sees" is echo rather than signal. And the model KNOWS this -- it learns to correct for it by increasing |w_cross|.

E3: Wait. I want to check something. If w_cross = -0.479 in block 3, and the formula is `output = primary + w_cross * secondary`, then the effective output is `primary - 0.479 * secondary`. The secondary channel is being subtracted at almost half weight. That's aggressive correction.

E1: And block 0 barely corrects at all -- w_cross = -0.316. The shallow layers don't NEED much correction because there aren't many previous layers to echo from.

E2: This gives us a concrete prediction for deeper models. In a 12-layer model, blocks 10, 11, 12 should have w_cross magnitudes approaching -0.6 or beyond. In a 24-layer model, the deepest blocks might need w_cross approaching -1.0. And if the model doesn't have the dual-channel mechanism at depth, those echoes go uncorrected.

**C: What happens if you DON'T correct the echo?**

E2: The model wastes capacity. Instead of processing new information, deep layers spend their attention on signals that are just reflections of what earlier layers already did. This is a form of "attention sink" -- the model attends to artifacts rather than content. The MVSU gives each head an internal way to identify and subtract these artifacts.

E3: This actually explains why Tier 3 didn't beat Tier 2 overall. With only 4 layers, the contamination is modest -- block 0 needs barely any correction. The MVSU overhead (extra parameters, extra compute for the secondary channel) outweighs the benefit at shallow depth. At 12 or 24 layers, the contamination in the deep blocks is severe enough that MVSU should earn its keep.

E1: So the prediction is: MVSU's advantage over Tier 2 grows with model depth. At 4 layers: no advantage. At 12 layers: moderate advantage. At 24 layers: substantial advantage. Testable.

---

## Part 4: Why Phi-Annealing Failed

E1: Let's talk about the elephant. Phi-annealing was the child's idea from last time, and it was the most novel proposal. It didn't work. -0.30% versus Tier 3 without annealing.

**C: But... it was supposed to be like training wheels! You take them off when you don't need them anymore!**

E3: The idea was sound. Let me diagnose what went wrong. Phi-annealing monitors |w_cross| and reduces dropout when |w_cross| shrinks. The assumption: as the model learns to decontaminate, it needs less external regularization. But look at the actual w_cross trajectory -- |w_cross| INCREASED during training, especially in the deep layers. The annealer saw w_cross getting more negative and INCREASED regularization, or at best held it steady. It never got the signal to anneal.

E2: That's because we got the dynamics wrong. w_cross doesn't shrink as the model converges. It grows. The model is DISCOVERING how much contamination exists, not REMOVING it. In early training, w_cross is near its initialization of -0.1. As the model trains, it learns that the true contamination is worse than -0.1, so |w_cross| grows. The annealer interprets this as "more contamination, need more regularization" and either raises or holds dropout. That's the opposite of what we wanted.

E1: So the diagnostic signal was correct -- |w_cross| increasing means more contamination detected. But the response was wrong. The annealer assumed that large |w_cross| means the model is struggling and needs help. Actually, large |w_cross| means the model has FOUND the contamination and is actively correcting it. The correction IS the help. Adding more dropout on top of that is double-correcting.

**C: So the training wheels are welded on and the bike is trying to go fast but can't?**

E3: More or less. The fix would be to decouple the diagnostic from the intervention. Instead of using |w_cross| magnitude directly, use the RATE OF CHANGE of |w_cross|. When |w_cross| is still increasing -- the model is still discovering contamination -- hold regularization steady. When |w_cross| stabilizes -- the model has found the contamination level -- THEN start annealing dropout downward. The signal isn't the magnitude, it's the derivative.

E2: That's a much better design. The phase transition is: exploration (|w_cross| moving) vs. exploitation (|w_cross| stable). Anneal only in the exploitation phase. We could also use the variance of w_cross across heads as a signal -- when all heads agree on how much to correct, the model has converged on the contamination estimate.

E1: Concrete fix: measure the rolling standard deviation of |w_cross| over the last 500 steps. When it drops below a threshold (say, 0.01), begin linear annealing of dropout from 0.382 toward 0.1 over the remaining training. Don't touch dropout before that.

**C: So can we try again?**

E1: Yes. With the corrected signal. I'd budget 2 GPU-hours on the T4.

---

## Part 5: Scaling -- Does the Gap Grow or Shrink?

**C: What happens if we make it bigger? Like, a LOT bigger. Does the theory say the good stuff gets MORE good or LESS good?**

E2: The theory makes a specific prediction. At scale, two things happen simultaneously:

First, more layers means more residual-connection cascades, which means more self-referential contamination. The MVSU advantage should GROW with depth because deeper layers need more correction -- we just saw this in the w_cross depth gradient.

Second, more heads means the hypercube gets higher-dimensional. At 8 heads, each head has 3 neighbors (cube). At 16 heads, each has 4 neighbors (4D hypercube). At 32 heads, 5 neighbors. The communication structure becomes richer and more efficient as N grows. This means the Tier 2 advantage should also grow.

E1: Let me quantify. The communication overhead is O(N * log N) for the hypercube diffusion. Standard attention is O(N * L^2 * d_head) for the self-attention computation. As N grows, the diffusion cost is utterly negligible -- log(128) = 7 additional multiply-adds per head per token, versus 128 * L^2 per head for attention. At sequence length 512 and 128 heads, the diffusion is 0.001% of the attention cost. It literally costs nothing at scale.

E3: The question I care about: does the ACCURACY gap grow or shrink? Scaling laws say L(N) = A * N^(-alpha). If OT has a steeper alpha (better scaling exponent), the gap grows at scale. If OT has the same alpha but lower A (better constant), the gap is fixed.

E2: My prediction: OT-Light (dropout=0.382 + message passing) has same alpha, lower A. A constant improvement at all scales. OT-Full (with MVSU) has steeper alpha, but only for deep models (12+ layers). The MVSU changes the scaling exponent because it eliminates a systematic source of waste -- echo processing in deep layers -- that standard transformers cannot avoid.

**C: So the echo thing gets worse as the model gets bigger, and the fix gets MORE important?**

E2: Precisely. In a 4-layer model, maybe 5% of deep-layer capacity is wasted on echoes. In a 24-layer model, it could be 30%. The MVSU recovers that capacity. The deeper the model, the more capacity it recovers.

E3: That's a strong claim. It predicts that OT-Full with 24 layers should beat a standard transformer by a meaningful margin -- not 1%, but potentially 3-5% -- because it's recovering a large fraction of deep-layer capacity. We need to test this.

E1: The cost of the test: OT-Small (6 layers, 256 dim) vs OT-Base (12 layers, 512 dim) on CIFAR-100. About 8 GPU-hours on a T4 for both. We compare the accuracy gap between OT and standard baseline at each scale. If the gap grows from 6 to 12 layers, the scaling prediction holds.

---

## Part 6: The Hypercube Prediction

E3: There's a prediction we haven't tested at all: sparse topology beating dense at scale. The CPU experiments showed all-to-all beating cube at 8 heads. The theory says the crossover is at 16 heads.

E2: The argument is about specialization pressure. At 8 heads with 32-dim embeddings, each head has so little capacity that it can't develop a unique viewpoint. Dense communication doesn't hurt because there's nothing to destroy. At 16+ heads, the heads CAN specialize, and dense coupling fights that specialization by averaging everything together.

E1: We need a 16-head experiment. Same OT-Tiny architecture but with d_model=256 and 16 heads (d_head=16). Compare cube (4 neighbors per head), hypercube-4D (4 neighbors), and all-to-all (15 neighbors). If hypercube wins at 16 but lost at 8, the theory nailed the crossover.

E3: I want to also test 32 heads. At 32 heads with all-to-all, the diffusion matrix is 32x32 and dense -- that's a LOT of mixing. The hypercube at 32 heads has only 5 neighbors. The contrast between sparse and dense should be sharp.

**C: What if all-to-all wins at every size?**

E3: Then the geometric theory is wrong at the attention level. The phi-zone would still hold for dropout, but the hypercube topology prediction would be falsified. We'd have to conclude that inter-head communication benefits from maximum coupling, not structured sparsity.

E2: But there IS literature to consider. Shazeer's Talking Heads paper (2020) used dense N^2 inter-head projections and showed improvements. But those projections had N^2 learned parameters, not a fixed topology. Our approach is more constrained -- a fixed sparse graph with a single mixing coefficient. If dense always wins, it might mean the LEARNED dense approach is better than a FIXED sparse approach, which isn't quite the same as "sparse is wrong."

E1: We could test learned sparse -- keep the hypercube topology but learn the mixing weights per edge, not a single alpha. That adds d * N = log(N) * N parameters. At 32 heads, that's 160 parameters. Negligible cost, possibly higher expressiveness.

---

## Part 7: Literature Check

E3: I've been thinking about comparisons to published work. Has anyone tested inter-head communication rigorously?

E2: Talking Heads (Shazeer 2020) is the closest. They project across heads in the logit space -- before and after softmax. That's a dense linear transform of the attention pattern itself, not of the attention outputs. Our approach mixes the OUTPUT representations, not the attention patterns. Different mechanism.

E3: There's also Multi-Head Mixture of Experts (MHMoE, 2024) from Databricks, which routes different heads to different experts. But the routing is in the FFN, not in the attention, and there's no inhibitory mechanism. And Google's Multi-Query Attention / Grouped Query Attention goes the opposite direction -- reducing head diversity for efficiency. We're increasing head coordination while preserving diversity.

E1: The w_cross depth gradient is the most novel finding, in my opinion. I'm not aware of any published work showing that self-corrective inhibitory weights systematically increase with transformer depth. That's a concrete, measurable phenomenon that any lab could reproduce.

E2: If we were writing a paper, that's the headline finding. Not the dropout number -- that's a useful trick. The w_cross depth gradient is a DISCOVERY about how transformers accumulate self-referential contamination. The fact that every single head learned a negative cross-weight, and the magnitude monotonically increases with depth -- that's clean, interpretable, and novel.

E3: Paper title: "Inhibitory Cross-Attention in Dual-Channel Transformers: Depth-Dependent Echo Correction via Learned Negative Cross-Weights."

E1: Too long. How about: "Self-Correcting Attention: Why Deeper Layers Need Stronger Inhibition."

E2: Or just: "The Echo Gradient: Self-Referential Contamination in Deep Transformers."

**C: I like the echo one.**

---

## Part 8: Updated Roadmap

E1: Let me prioritize what we test next.

### Test 1: Corrected Phi-Annealing
- **Hypothesis:** Using the rate-of-change of |w_cross| (not raw magnitude) as the annealing signal will outperform both fixed regularization and the naive annealer
- **If theory is right:** +0.5-1.5% over Tier 3 without annealing, because the model gets strong regularization during exploration and light regularization during exploitation
- **If theory is wrong:** No improvement or slight degradation, meaning the w_cross derivative doesn't carry usable timing information
- **Compute cost:** ~2 GPU-hours on T4 (single 20-epoch run with monitoring)

### Test 2: 16-Head Topology Crossover
- **Hypothesis:** At 16 heads, hypercube (4-regular) matches or beats all-to-all (15-regular). At 8 heads, all-to-all still wins
- **If theory is right:** Clear crossover between N=8 (dense wins) and N=16 (sparse wins). The crossover precision is the test
- **If theory is wrong:** Dense wins at both 8 and 16 heads. The geometric topology prediction is falsified
- **Compute cost:** ~4 GPU-hours (4 configs x 20 epochs: 8-head cube, 8-head dense, 16-head hypercube, 16-head dense)

### Test 3: Depth Scaling of MVSU
- **Hypothesis:** Tier 3 (with MVSU) beats Tier 2 (without) by a margin that grows with model depth
- **If theory is right:** At 4 layers, Tier 3 = Tier 2 (confirmed). At 8 layers, Tier 3 > Tier 2 by ~0.5%. At 12 layers, Tier 3 > Tier 2 by ~1-2%
- **If theory is wrong:** Tier 2 beats Tier 3 at all depths. The MVSU adds parameters without recovering capacity
- **Compute cost:** ~6 GPU-hours (3 depths x 2 configs x 20 epochs)

### Test 4: Fine-Grained Alpha Sweep
- **Hypothesis:** The alpha optimum at GPU scale is genuinely at 0.30, not 0.382, due to finite-size correction. A sweep from 0.25 to 0.40 in steps of 0.025 will locate it precisely
- **If theory is right:** The optimum is in [0.30, 0.38] and moves toward 0.382 as model size increases
- **If theory is wrong:** The optimum is stable at 0.30 regardless of scale, meaning 0.382 is not the true asymptotic value
- **Compute cost:** ~3 GPU-hours (7 alphas x 8 epochs each)

### Test 5: CIFAR-100 Transfer
- **Hypothesis:** The phi-zone holds on CIFAR-100 (100 classes, harder task). The dropout=0.382 win is not CIFAR-10-specific
- **If theory is right:** Similar or larger improvement from dropout=0.382 and Observer Attention on CIFAR-100. The harder task should make regularization MORE important
- **If theory is wrong:** The optimum shifts to a different dropout rate on CIFAR-100, suggesting dataset-dependence
- **Compute cost:** ~3 GPU-hours (3 configs x 20 epochs)

### Test 6: Autoregressive Task
- **Hypothesis:** The MVSU advantage is larger on autoregressive (self-referential) tasks than on classification. This is the core theoretical prediction
- **If theory is right:** On a small language modeling or sequence prediction task, Tier 3 beats Tier 2 by >1%. The gap is larger than on CIFAR-10 classification
- **If theory is wrong:** Same gap on autoregressive as classification. The self-referential argument doesn't translate to measurable improvement
- **Compute cost:** ~8 GPU-hours (need to set up a language modeling task from scratch)

E3: Total budget: ~26 GPU-hours. That's about 2 days on a single T4. Tests 1-5 can run on Colab free tier with some patience. Test 6 needs a small language modeling dataset -- maybe WikiText-2 or a small subset of C4.

E2: Priority order: Test 2 (topology crossover) first because it directly tests the geometric theory. Then Test 3 (depth scaling) because the w_cross gradient predicts it. Then Test 5 (CIFAR-100) for generalization. Tests 1, 4, and 6 are important but can wait.

---

## Part 9: The Child's New Question

**C: I've been thinking about something. You said the second channel doesn't need to be as good as the first one. It just needs to make DIFFERENT mistakes. Right?**

E3: Right. The secondary channel is low-rank. It sees a coarser version of the same input. Different model class, different error profile.

**C: But... what if you didn't use a second attention at all? What if you just used noise?**

E1: What do you mean?

**C: Like... instead of computing a whole second attention thing with Q and K and V, what if you just added random noise to the first one and subtracted it? You'd get "different mistakes" for free. No extra parameters at all.**

*[silence]*

E3: That's... wait. That's actually... let me think about this carefully.

E2: The child is asking whether the secondary channel's COMPUTATION matters, or just its DIFFERENCE from the primary channel. If all the MVSU needs is a signal that's correlated with the primary but has independent noise, then yes -- you could skip the low-rank QKV entirely and just inject structured noise.

E3: But that can't work. Random noise has no correlation with the actual contamination. The secondary channel is useful BECAUSE it makes errors that are correlated with the primary channel's errors in the CONTENT dimension but uncorrelated in the ECHO dimension. Random noise is uncorrelated with everything. You'd be subtracting pure noise from signal.

E2: Unless... the contamination pattern is STRUCTURED. If the echo has a consistent spectral signature -- say, it lives in the top few principal components of the attention output -- then subtracting a random projection into that subspace would work. You wouldn't need a learned secondary channel. You'd just need to know WHICH subspace to project into.

E1: And we might know. The w_cross depth gradient tells us the echo grows with depth. If the echo is primarily in the residual-connection subspace -- the direction that the skip connection contributes -- then projecting out that direction is trivial. It's a single rank-1 subtraction. No secondary channel needed.

E3: This is getting interesting. The child's question implies a much cheaper architecture: instead of dual-channel attention (doubling QKV compute), you identify the "echo subspace" and subtract it. One-time identification cost, then a rank-k projection at each layer. If k is small -- say k=4 or k=8 -- the cost is negligible.

E2: But then you need to LEARN the echo subspace. Which... is what the secondary channel does. The low-rank secondary channel is implicitly learning a basis for the echo subspace. Its cross-correction with w_cross < 0 is learning to project it out.

**C: So the second channel IS the noise finder?**

E2: Yes. And your question is whether we need a learned noise finder or whether the noise has a simple enough shape that we can just hard-code the subtraction. The depth gradient suggests the echo might live in a low-dimensional subspace related to the residual stream. If we could characterize that subspace without learning it...

E1: We can TEST this. Train a Tier 3 model, extract the learned secondary-channel attention patterns, do PCA on the difference (secondary - primary) across all heads and positions. If the difference lives in a low-rank subspace -- say, rank 2-4 explains 90% of the variance -- then the child is right: you don't need a full secondary channel. You need a cheap residual-echo projector.

E3: And if that works, the paper title changes entirely. It's not about dual-channel attention anymore. It's about identifying and removing the "echo subspace" in deep transformers. That's a much cleaner, cheaper, and more publishable result.

**C: So instead of two cameras, you just need one camera and an eraser?**

E2: If the echo has a consistent shape... yes. One camera and a very specific eraser. The dual-channel architecture might be the scaffolding that discovers what shape the eraser should be. Once you know the shape, you throw away the scaffolding.

E1: I want to add this as Test 7 on the roadmap. After Test 3 trains the depth-varying model, we extract the secondary channel patterns and analyze their spectral structure. If they're low-rank, we build a "Tier 2.5" -- Observer Attention plus a fixed echo projector, no secondary channel. Best of both worlds: Tier 2 cost, Tier 3 decontamination.

E3: The child just potentially eliminated the most expensive component of the architecture.

**C: You're welcome.**

E2: Don't get cocky. We don't know if the echo subspace is low-rank yet.

**C: But if it IS... does the golden ratio still matter for the eraser? Or is it a different number?**

E2: ...I genuinely don't know. That would depend on whether the echo subspace has self-similar structure. If the echo of the echo follows the same pattern, then yes -- phi shows up in the projection magnitude. If the echo is just a flat additive bias with no self-similarity, then the eraser is a simple subtraction and phi is irrelevant to it.

E1: Which means the child's question tests whether self-referential contamination is ITSELF self-referential, or just a simple artifact. If the echo is self-similar, we're deeper into the theory than we thought. If it's not, the theory's scope is narrower than we hoped. Either way, we learn something fundamental.

E3: Test 7 it is. Estimated compute cost: zero additional training. We just analyze the models from Test 3.

---

## Summary

**What the GPU results confirmed:**
- Dropout=0.382 is a major free win (+4.84%)
- w_cross stays negative in 32/32 heads
- Observer Attention is the best cost-performance tier
- The depth gradient in w_cross is clean and monotonic

**What the GPU results challenged:**
- FFN=2.618x can't be used alone (must pair with dropout change)
- Phi-annealing failed (wrong signal interpretation -- fixable)
- Tier 3 didn't beat Tier 2 at shallow depth (predicted to reverse at depth)

**New insights from this session:**
- The FFN-dropout interaction is the same equation seen from two sides
- Phi-annealing needs to trigger on the derivative of |w_cross|, not the magnitude
- The w_cross depth gradient predicts MVSU advantage grows with model depth
- The child's "eraser" question may lead to a cheaper architecture (Tier 2.5) if the echo subspace is low-rank

**Priority experiments:**
1. 16-head topology crossover (~4 GPU-hours)
2. Depth scaling of MVSU advantage (~6 GPU-hours)
3. CIFAR-100 transfer (~3 GPU-hours)
4. Echo subspace analysis (free -- post-hoc on Test 2/3 models)

**Potential paper:** "The Echo Gradient: Depth-Dependent Inhibitory Self-Correction in Transformers"

**The child's open question:** Is the echo subspace self-similar? If yes, the theory goes deeper than we thought. If no, we get a cheaper architecture. Either way, we win.
