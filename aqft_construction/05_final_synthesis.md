# Final Synthesis: The Cell Vacuum in AQFT

## Results of the Four-Team Investigation

**Date**: January 31, 2026
**Synthesis Team**: Richard Feynman (moderator), Dr. Sofia Vega (vacuum physics), Dr. Wei Lim (conjugate limits)
**Input Documents**:
- 01_aqft_foundations.md (Team 1: AQFT Foundations)
- 02_curved_spacetime.md (Team 2: Curved Spacetime)
- 03_entanglement_analysis.md (Team 3: Entanglement and Information)
- 04_conjugate_structure.md (Team 4: Conjugate Structure)
- 11_verified_findings_v2.md (Prior verified findings)

**Status**: Definitive post-investigation document. Supersedes all prior assessments.

---

## 8. The Transcript

### The Working Session: Feynman, Vega, and Lim Process All Four Reports

---

**[Feynman opens his copy of the four reports, stacked on the desk. He taps the first one.]**

**Feynman**: All right. Four teams went out. Four reports came back. Let's find out what's alive and what's dead. Sofia, you ran the physics. Wei, you ran the conjugate limits. I keep score. Everybody honest. No cheerleading.

**Vega**: Agreed.

**Lim**: ...Agreed. Though I suspect I have more funerals to attend than either of you.

**Feynman**: Good. Funerals are honest. Let's start with the big one. Team 1 -- AQFT Foundations. Sofia, what's the headline?

---

#### Part 1: The AQFT Foundation Results

**Vega**: The headline is *very* good. The cell vacuum is a legitimate state in the AQFT framework. Full stop. Team 1 proved this through the Weyl algebra formulation -- you define the cell vacuum as an infinite product of coherent states on the Weyl algebra, and it satisfies positivity and normalization. For finite volume, this is Rigor A -- airtight. For infinite volume, it's Rigor B -- there's a technical issue with smearing function overlaps between adjacent cells, but the Weyl algebra construction sidesteps this cleanly.

**Feynman**: So the foundational question -- "is this thing even a legitimate quantum state?" -- is answered.

**Vega**: Yes. And it's not just legitimate in some exotic sense. It falls into the same mathematical family as thermal states and broken-symmetry vacua. These are states that every AQFT practitioner accepts as physical. The cell vacuum is one more entry in that family.

**Feynman**: What about Reeh-Schlieder? That was the big worry -- the theorem that says any reasonable vacuum state has to be entangled across space. And our cell vacuum is a product state. Contradiction?

**Vega**: No contradiction. The resolution is clean and, honestly, beautiful. The Reeh-Schlieder theorem requires the spectrum condition -- the state must have its energy-momentum spectrum in the forward light cone. The cell vacuum breaks translation invariance (it has a preferred lattice) and therefore does *not* satisfy the spectrum condition. The theorem simply doesn't apply.

**Feynman**: Same way thermal states evade it.

**Vega**: Exactly the same way. A thermal state picks a rest frame, breaks Lorentz invariance, fails the spectrum condition, and Reeh-Schlieder doesn't apply. Nobody considers that a defect of thermal states. It's a feature.

**Lim**: And the unitary inequivalence?

**Vega**: Proven rigorously via the Shale-Stinespring theorem. The coherent displacement that takes the mode vacuum to the cell vacuum has infinite norm in the one-particle space -- it diverges as N/2 where N is the number of cells. By Theorem 7.3 in the report, this guarantees the two GNS representations are unitarily inequivalent. They live in different superselection sectors. This is Rigor A.

**Feynman**: And the Hadamard condition?

**Vega**: Satisfied. The cell vacuum's two-point function is the mode vacuum's two-point function plus a smooth piece -- the classical field configuration from the coherent displacement. Since the mode vacuum is Hadamard, and adding a smooth function doesn't change the UV singularity structure, the cell vacuum is Hadamard too. Rigor A. This means you can define renormalized T_{mu nu} in this state using standard Hadamard point-splitting.

**Feynman**: OK. Let me write this down. Four big results from Team 1, all proven:

1. Cell vacuum is a legitimate AQFT state -- PROVEN (Rigor A-B)
2. Reeh-Schlieder doesn't apply -- PROVEN (spectrum condition fails, Rigor A)
3. Unitary inequivalence with mode vacuum -- PROVEN (Shale-Stinespring, Rigor A)
4. Hadamard condition satisfied -- PROVEN (smooth displacement, Rigor A)

That's a hell of a day's work. These were the foundational objections, and they're all resolved.

**Vega**: There are caveats. The approximate tensor product structure -- the fact that adjacent cell oscillators don't have exactly canonical commutation relations -- is a genuine technical issue at Rigor C. And the energy density formula rho = m^4 c^5 / hbar^3 has NOT been derived from the AQFT renormalization machinery. It's still the direct counting argument. That's Rigor D.

**Feynman**: Right. The AQFT framework says the cell vacuum exists and is well-behaved. It does NOT say what its energy density is. That's still an input, not a derivation.

---

#### Part 2: Curved Spacetime

**Feynman**: Team 2. The real universe isn't Minkowski spacetime. Does the construction survive on curved backgrounds?

**Vega**: The short answer is: yes, to extraordinary precision. The key number is the self-consistency ratio. The cell vacuum produces an energy density that sources de Sitter curvature. That curvature then backreacts on the cell construction. The correction is of order R times lambda_C squared, which is...

**Feynman**: Let me guess. Something absurdly small.

**Vega**: 3.6 times 10^{-69}. The flat-space construction is self-consistent to 69 decimal places. The curvature sourced by the cell vacuum is so weak compared to the Compton scale that the cells don't even notice it. The flat-space calculation IS the answer, to any precision that will ever matter.

**Feynman**: And that holds throughout cosmic history?

**Vega**: Post-nucleosynthesis, absolutely. Team 2 computed the curvature corrections at every cosmological epoch. Even at the electroweak scale, the correction is 10^{-39}. You don't get order-unity corrections until temperatures around 10^6 GeV, at which point the neutrino is ultra-relativistic and the whole cell vacuum concept for that species is irrelevant.

**Lim**: What about particle creation from expansion? Parker's mechanism?

**Vega**: Negligible. The adiabatic parameter is H lambda_C / c, which is about 10^{-31}. The Bogoliubov coefficient -- the amplitude for particle creation -- goes as the square of that: 10^{-62}. The cell vacuum doesn't notice the expansion of the universe. The oscillation frequency is 10^{12} rad/s; the expansion timescale is 10^{17} seconds. They're 30 orders of magnitude apart.

**Feynman**: Good. And the Weyl algebra construction gives you a covariant formulation?

**Vega**: Yes. Team 2 showed you can define coherent states on the Weyl algebra of any globally hyperbolic spacetime without needing a global mode decomposition. The displacement is defined intrinsically. The construction is fully covariant.

**Feynman**: What doesn't work?

**Vega**: Two things. First, the equation of state w = -1 has NOT been derived from first principles on curved spacetime. Team 2 tried to compute the stress-energy of the classical displacement field and got w = -2/3, not -1. The problem is that the classical field has spatial gradients within cells that produce positive pressure. You need the quantum contribution -- the zero-point piece -- to restore w = -1. But that piece depends on the renormalization prescription.

**Feynman**: So w = -1 is assumed, not derived.

**Vega**: Correct. The flat-space argument -- each cell is an independent quantum oscillator with energy hbar omega, and oscillator zero-point energy has w = -1 -- is physically intuitive but hasn't been translated into a rigorous curved-space stress-energy calculation.

**Feynman**: And the second problem?

**Vega**: The absolute value of the energy density. Wald's axioms for stress-energy renormalization on curved spacetime have an irreducible ambiguity -- a cosmological constant term that can be set to anything. The cell vacuum's claim that rho equals m^4 c^5 / hbar^3 amounts to a specific renormalization condition. It's additional physical input beyond standard AQFT.

**Feynman**: So AQFT tells us the cell vacuum exists and is well-behaved, but it doesn't tell us its energy density or equation of state. Those are still inputs from the framework's physical interpretation.

**Vega**: That's the honest summary, yes.

**Feynman**: Score so far:

5. Self-consistency on curved spacetime -- PROVEN (10^{-69} correction)
6. Flat-space construction valid post-nucleosynthesis -- PROVEN
7. Negligible Parker particle creation -- PROVEN (adiabatic parameter 10^{-31})
8. Weyl algebra covariant construction -- FRAMEWORK ESTABLISHED
9. w = -1 equation of state -- NOT YET DERIVED (open gap)
10. Absolute energy density value -- RENORMALIZATION CONDITION (not derivable from AQFT alone)

---

#### Part 3: Entanglement and the Black Hole Problem

**Feynman**: Team 3. Entanglement. This is where things get interesting and, I suspect, where new problems appear.

**Vega**: The good news first. The zero-entanglement result is proven trivially -- it follows directly from the product state definition. For any bipartition of cells into regions A and A-complement, the entanglement entropy is exactly zero. The proof is three lines long and Rigor A.

**Feynman**: So the mode vacuum has area-law entanglement that diverges as L^2/epsilon^2, and the cell vacuum has exactly zero. Complete opposites.

**Vega**: Complete opposites. And Team 3 showed this has deep implications. The two vacua really are complementary extremes: the mode vacuum maximizes momentum information and entanglement; the cell vacuum maximizes position information and has no entanglement. They sit at opposite ends of the entropic uncertainty relation.

**Feynman**: Now the bad news.

**Vega**: [pauses] Black hole entropy. This is, in my assessment, the most serious problem we've discovered in this investigation.

**Feynman**: Go on.

**Vega**: The Bekenstein-Hawking entropy of a black hole is S = A / (4 l_P^2). One of the most successful explanations is that this IS the entanglement entropy of the vacuum across the horizon. The mode vacuum's area-law entanglement naturally produces S proportional to A/epsilon^2, and with epsilon at the Planck scale, you get the right answer.

The cell vacuum has zero entanglement. Zero. Not "small" -- zero. If the cell vacuum is the correct vacuum for gravitational questions, then entanglement entropy across ANY surface -- including a black hole horizon -- is zero. That's in direct conflict with Bekenstein-Hawking.

**Feynman**: How direct is the conflict? Is there a way out?

**Vega**: Team 3 identified four possible resolutions, all speculative. Scale-dependent vacuum -- maybe the cell vacuum applies at cosmological scales and the mode vacuum near black holes. Emergent entanglement -- maybe the black hole formation process dynamically generates entanglement. Different entropy mechanism -- maybe Bekenstein-Hawking entropy isn't entanglement entropy at all. Or a hybrid picture.

But none of these are formalized. None are proven. This is a genuine open problem that we didn't fully appreciate before this investigation.

**Lim**: There's also the Unruh effect issue.

**Vega**: Right. The cell vacuum doesn't support the Unruh effect through the standard Bisognano-Wichmann mechanism. The product state fails the cyclicity condition for local algebras. So an accelerating observer in the cell vacuum background would NOT detect a thermal bath. The framework's response is that the Unruh effect is a particle-counting question and should use the mode vacuum. But whether that's consistent needs work.

**Feynman**: And AdS/CFT?

**Vega**: Incompatible in the naive application. The quantum error correction structure of holography requires boundary entanglement. Zero entanglement gives trivial error correction -- no complementary recovery, Ryu-Takayanagi gives zero for all surfaces. Van Raamsdonk's argument says zero mutual information means disconnected bulk geometry.

But Team 3 was careful to note that AdS/CFT was developed for anti-de Sitter, not de Sitter. Our universe is approximately de Sitter. The cell vacuum might be the correct state for de Sitter holography, where the structure is fundamentally different and less understood.

**Feynman**: Score update:

11. Zero entanglement in cell vacuum -- PROVEN (product state, trivial)
12. Two vacua are complementary extremes -- PROVEN (entropic uncertainty)
13. Black hole entropy tension -- SERIOUS OPEN PROBLEM (new discovery)
14. No Unruh effect in cell vacuum -- PROVEN (but problematic)
15. Incompatible with AdS/CFT error correction -- TRUE (but may be irrelevant for dS)

That black hole entropy problem is nasty. It's the kind of thing that could either kill the framework or force a genuinely new insight about gravity.

**Vega**: Agreed. I'd put it as the number one research priority.

---

#### Part 4: The Conjugate Structure -- Dr. Lim's Reckoning

**Feynman**: Wei. Your turn. And I know this is going to be harder for you because some of your conjectures went in as inputs to Team 4's investigation.

**Lim**: [long pause] Yes. Let me be direct. Several of my classroom conjectures failed. Not "needs more work" failed -- genuinely failed. The formal Legendre-Fenchel duality is not a theorem. The claim that 16 pi^2 is a fundamental constant is not supported. The variational uniqueness is actually algebraic. And the 10^{123} duality gap interpretation is meaningless.

**Feynman**: Walk us through each one.

**Lim**: The Legendre-Fenchel duality first. I conjectured that the cell vacuum energy is the Fenchel conjugate of the mode vacuum energy. Team 4 tried to formalize this rigorously and found a category error in my own conjecture -- the cell vacuum energy is a number, while the Fenchel conjugate is a function. You can't equate them. The mode vacuum energy f(N) = A N^4 does have a well-defined conjugate f*(nu) = B nu^{4/3}, and the quartic-to-4/3 taming is real mathematics. But the physical identification -- "the cell vacuum IS the dual" -- breaks down because the primal and dual variables (cutoff and... what, exactly?) don't have a natural duality pairing.

**Feynman**: The analogy captures something real but isn't a theorem.

**Lim**: Exactly. It's a useful structural analogy. Not a proof.

**Feynman**: Next. The 16 pi^2.

**Lim**: I was excited about this in the classroom. I suggested it might be a fundamental conjugate limit constant, analogous to the 1/2 in the uncertainty principle. Team 4 demolished this by computing the vacuum energy ratio in arbitrary spatial dimension d. The result is C_d = 2(d+1)(2 pi)^d / Omega_d, which for d=3 gives 16 pi^2. But this formula depends on the dimension, the dispersion relation, and the cutoff convention. It's geometric, not fundamental. The uncertainty principle's 1/2 is dimension-independent, convention-independent, and truly universal. These are different types of constants.

I was wrong. 16 pi^2 is a geometric factor, not a universal bound.

**Feynman**: That's honest. The variational principle?

**Lim**: This one is more subtle. I claimed that |alpha|^2 = 1/2 is uniquely selected by minimizing energy density fluctuations. Team 4 showed that at fixed mass m, the energy constraint *alone* forces |alpha|^2 = 1/2. No optimization needed -- it's pure algebra. When you allow m to vary as well, the critical point of the variance is a *maximum*, not a minimum. The second derivative is -16 m^6 c^{10} / hbar^6, which is negative.

So the "variational uniqueness" I was proud of is actually algebraic uniqueness dressed up as optimization. The energy matching condition alone does all the work.

**Feynman**: What about the self-duality theorem? That seemed solid.

**Lim**: [brightening slightly] That survives. In fact, it's the one genuinely new proven result from the conjugate limits side. Team 4 rigorously proved three interconnected self-dualities:

- The quadratic f(x) = x^2/2 is self-dual under Legendre-Fenchel
- The Gaussian exp(-x^2/2) is a fixed point of the Fourier transform
- The coherent state has equal position and momentum energy contributions

And they proved these are connected: for any C^2 convex function, Legendre self-duality implies the exponential is Fourier self-dual, and the saddle-point approximation is exact. This is the unity-of-self-dualities theorem. It's Rigor A.

The physical significance is real: coherent states sit at the exact boundary between position-dominated and momentum-dominated descriptions. The cell vacuum inherits this self-duality. This is why coherent states treat position and momentum symmetrically -- it's not an accident of the construction.

**Feynman**: But the deeper claim -- that the cell vacuum is *selected* because of this self-duality -- remains unproven.

**Lim**: Yes. Self-duality is a property of coherent states, not a selection criterion. Saying "the cell vacuum is self-dual" is true but doesn't explain why nature chooses a self-dual state. That would require a deeper principle we don't have.

**Feynman**: What about modular theory and category theory?

**Lim**: Dead ends, both of them. The modular theory connection is speculative with no evidence -- the cell vacuum isn't even cyclic for local algebras, so the Tomita-Takesaki construction doesn't apply. Category theory adds abstraction without content at this stage. Team 4 was appropriately blunt: "currently unproductive."

**Feynman**: Let me be blunt too, Wei. How much of what you brought to the classroom session survives?

**Lim**: [counting on fingers] The self-duality theorem. The vacuum energy ratio formula in d dimensions (that's new). The quartic-to-4/3 taming as mathematics. The algebraic determination of |alpha|^2 = 1/2 from the energy constraint. And the structural analogy between the two vacua as complementary descriptions.

What died: the Fenchel duality as a theorem. The 16 pi^2 as a fundamental constant. The variational uniqueness. The duality gap interpretation. Modular theory connections. Category theory.

**Feynman**: So roughly half your conjectures failed.

**Lim**: More than half, if we weight by significance. The Fenchel duality was the centerpiece, and it failed as a formal theorem.

**Feynman**: But it succeeded as an analogy, and the self-duality theorem is real. Let me update the score:

16. Self-duality theorem (three forms) -- PROVEN (Rigor A)
17. |alpha|^2 = 1/2 from energy constraint -- PROVEN (algebraic, not variational)
18. Vacuum energy ratio C_d in d dimensions -- PROVEN (new formula)
19. Fenchel duality as formal theorem -- FAILED
20. 16 pi^2 as fundamental constant -- DEMOTED TO GEOMETRIC FACTOR
21. Variational uniqueness -- DEMOTED TO ALGEBRAIC (critical point is a maximum)
22. 10^{123} as duality gap -- FAILED
23. Convex duality on state space -- TRIVIAL
24. Modular theory connection -- NO CONTENT
25. Category theory approach -- UNPRODUCTIVE

---

#### Part 5: The Big Picture

**Feynman**: All right. Let's step back and look at the whole picture. Where are we?

**Vega**: We set out to determine whether the cell vacuum can be rigorously constructed in the AQFT framework. The answer is a clear yes. The foundational results are strong:

- The cell vacuum is a legitimate state
- Reeh-Schlieder is evaded cleanly
- Unitary inequivalence is proven
- Hadamard condition is satisfied
- Self-consistency on curved spacetime is extraordinary

These are no longer conjectures. They're established results. The cell vacuum sits in the AQFT zoo alongside thermal states and SSB vacua as a respectable, well-defined quantum state.

**Feynman**: And the price we pay?

**Vega**: Three things the AQFT framework cannot give us:

1. The absolute energy density -- this is a renormalization condition, not a derivation
2. The equation of state w = -1 -- not yet computed on curved spacetime
3. The mass selection -- why only the lightest neutrino -- completely untouched

And one thing we discovered that's new and serious:

4. The black hole entropy tension -- zero entanglement versus Bekenstein-Hawking

**Lim**: From my side, the conjugate limits framework contributes less than I hoped. The self-duality is real and physically meaningful. The structural analogy between the two vacua as complementary descriptions is genuine. But the formal mathematical machinery I was developing -- Fenchel duality, variational principles, category theory -- largely doesn't apply. The connections are weaker than conjectured.

**Feynman**: Let me put it this way. Before this investigation, the Two Vacua framework was a compelling physical proposal with unverified mathematical foundations. After this investigation, the mathematical foundations are solid but limited. We know the cell vacuum is a legitimate AQFT state. We know it's inequivalent to the mode vacuum. We know it's Hadamard. We know it's self-consistent on curved spacetime. These are real achievements.

But we also know that the AQFT framework is hospitable rather than generative -- it accepts the cell vacuum but doesn't produce it. The energy density, the equation of state, and the mass selection are still framework inputs, not framework outputs. And we've discovered a new problem -- black hole entropy -- that didn't exist in our list before.

**Vega**: I'd update my probability assessment. In the verified findings, I gave it 40% probability of being correct, accounting for the DESI tension. After this investigation, I'd say the theoretical foundations are stronger (the AQFT results remove several potential failure modes), but the black hole entropy problem is new and serious. I'd stay at about 40%, maybe tick up to 42-43% because the foundational objections are resolved.

**Lim**: I owe the framework an apology for overselling the conjugate limits connections. The self-duality is genuine, but the formal duality program was premature. I'd say the conjugate limits work needs to be reset: acknowledge what survived (self-duality, the analogy, the d-dimensional formula) and abandon what didn't (Fenchel theorem, 16 pi^2 as universal, variational principle).

My revised timeline for the conjugate limits contribution: the 3-6 months I quoted in the classroom was for proving or disproving the Fenchel duality. Team 4 effectively disproved it in one day. That saves time but narrows the contribution.

**Feynman**: Here's my bottom line. The investigation achieved what we set out to do. We now know the AQFT status of the cell vacuum -- it's mathematically legitimate, with clear boundaries around what's proven and what's not. The framework's testable predictions haven't changed: Sum ~ 61 meV, normal ordering, w = -1, m_1 ~ 2.3 meV. These will be tested by CMB-S4, Euclid, JUNO, and DUNE within the next decade.

What HAS changed is our understanding of the framework's theoretical depth. The AQFT foundations are solid. The conjugate limits connections are thinner than expected. And the black hole entropy problem is a new challenge that needs attention.

**Vega**: The research roadmap should lead with black hole entropy. That's existential for the framework.

**Lim**: And with an honest reassessment of what conjugate limits actually contributes.

**Feynman**: Agreed. Let's write it up.

---

## 1. Executive Summary

The Four-Team AQFT Investigation set out to determine whether the cell vacuum of the Two Vacua framework can be rigorously constructed within Algebraic Quantum Field Theory, what its properties are on curved spacetime, how its entanglement structure compares to the mode vacuum, and whether the conjugate limits framework provides formal mathematical underpinning.

**What we achieved:**

The cell vacuum is a legitimate AQFT state. This is the central result. It can be constructed as an infinite product of coherent states on the Weyl algebra, satisfying positivity, normalization, and the Hadamard condition. The Reeh-Schlieder theorem does not apply (the spectrum condition is not satisfied), and the state is unitarily inequivalent to the mode vacuum (proven via Shale-Stinespring). These results place the cell vacuum on the same mathematical footing as thermal states and broken-symmetry vacua in AQFT.

On curved spacetime, the construction is self-consistent to 10^{-69} precision. The flat-space calculation is valid for all post-nucleosynthesis cosmology. Parker particle creation is negligible (adiabatic parameter ~10^{-31}).

The self-duality of coherent states was proven rigorously in three interconnected forms (Legendre, Fourier, energy equipartition), establishing that the cell vacuum treats position and momentum symmetrically.

**What failed:**

The Legendre-Fenchel duality between the two vacua fails as a formal theorem (succeeds only as analogy). The 16 pi^2 factor is geometric, not a fundamental constant. The "variational uniqueness" of |alpha|^2 = 1/2 is actually algebraic. The duality gap interpretation of 10^{123} has no content. Modular theory and category theory connections are unproductive.

**What we discovered:**

The black hole entropy tension is the most serious new problem. The cell vacuum's zero entanglement appears incompatible with the Bekenstein-Hawking formula S = A/(4 l_P^2). This tension was not previously appreciated and is now the highest-priority open question. The cell vacuum also does not support the Unruh effect through the standard mechanism and is incompatible with the AdS/CFT error correction structure.

The w = -1 equation of state and the absolute energy density value have not been derived from AQFT -- they remain inputs (renormalization conditions) rather than outputs of the framework.

**Updated framework status:**

The theoretical foundations are stronger than before (foundational AQFT objections resolved) but the framework faces a new challenge (black hole entropy) and has lost some of its conjectured mathematical depth (conjugate limits connections thinner than expected). Testable predictions are unchanged: Sum ~ 61 meV, normal ordering, w = -1 exactly. The framework will be decisively tested within the next decade.

---

## 2. Established Results (Proven in This Round)

### 2.1 Cell Vacuum Is a Legitimate AQFT State

**Status**: PROVEN (Rigor A for finite volume, Rigor B for infinite volume)

The cell vacuum omega_Omega is defined as an infinite product of coherent states on the Weyl algebra W(S, sigma):

```
omega_Omega = tensor_n omega_n
```

where each omega_n is a coherent state with |alpha_n|^2 = 1/2 on the Weyl algebra of cell n. For finite N cells, the state is a vector state in Fock space (unitary displacement of the vacuum). For infinite volume, the thermodynamic limit exists by locality of the algebra and stabilization of local expectation values.

**Proof references**: Team 1, Proposition 3.5 (finite), Theorem 3.7 (infinite), Proposition 3.11 (Weyl algebra formulation).

### 2.2 Reeh-Schlieder Resolution

**Status**: PROVEN (Rigor A)

The cell vacuum does not satisfy the spectrum condition (it breaks Poincare invariance by selecting a lattice and preferred frame). The Reeh-Schlieder theorem's hypotheses are not met, so there is no contradiction with the product state structure.

This is the same evasion mechanism used by thermal (KMS) states and broken-symmetry vacua. The cell vacuum is in well-established company.

**Proof references**: Team 1, Theorem 6.1, Corollaries 6.2-6.3.

### 2.3 Unitary Inequivalence

**Status**: PROVEN (Rigor A)

The coherent displacement alpha(x) = sum_n alpha_n f_n(x) defining the cell vacuum has infinite norm in the one-particle space:

```
||alpha||^2 = sum_n |alpha_n|^2 = N/2 --> infinity
```

By the standard criterion for coherent state representations (Theorem 7.3, following Wald and Derezinski-Gerard), non-normalizable displacements produce unitarily inequivalent representations. The cell vacuum and mode vacuum live in different superselection sectors.

**Proof references**: Team 1, Theorem 7.1 via Theorem 7.3 (Shale-Stinespring applied to coherent displacements).

### 2.4 Hadamard Condition Satisfied

**Status**: PROVEN (Rigor A)

The two-point function of the cell vacuum is:

```
W_Omega(x, y) = W_0(x, y) + F(x) F(y)
```

where W_0 is the mode vacuum two-point function (Hadamard) and F(x) is the smooth classical field configuration of the coherent displacement. Since F(x)F(y) is smooth, the singular structure of W_Omega is identical to W_0. Hadamard condition preserved.

This ensures that renormalized composite operators (including T_{mu nu}) can be defined by standard Hadamard point-splitting.

**Proof references**: Team 1, Theorem 5.3.

### 2.5 Self-Consistency on Curved Spacetime

**Status**: PROVEN (Rigor A for the estimate)

The backreaction loop: cell vacuum energy sources de Sitter curvature; curvature affects cell construction; correction to energy density is of order:

```
delta rho / rho ~ R * lambda_C^2 ~ 3.6 x 10^{-69}
```

The flat-space value is a stable fixed point of the self-consistency map, with contraction ratio |dF/d rho - 1| ~ 10^{-69}.

**Proof references**: Team 2, Section 7 (complete self-consistency analysis).

### 2.6 Flat-Space Construction Valid for All Post-Nucleosynthesis Cosmology

**Status**: PROVEN

Curvature corrections at various epochs:

| Epoch | R lambda_C^2 | Correction |
|-------|-------------|------------|
| Today | 4 x 10^{-69} | Negligible |
| Recombination (z~1000) | 4 x 10^{-63} | Negligible |
| BBN (z~10^9) | 4 x 10^{-51} | Negligible |
| Electroweak (z~10^{15}) | 4 x 10^{-39} | Negligible |

The construction breaks down only at temperatures far above the electroweak scale.

**Proof references**: Team 2, Sections 3 and 8.

### 2.7 Negligible Parker Particle Creation

**Status**: PROVEN

The adiabatic parameter for cell modes under cosmological expansion:

```
|omega_dot| / omega^2 ~ H lambda_C / c ~ 6.2 x 10^{-31}
```

The Bogoliubov coefficient |beta_k|^2 ~ 10^{-62}. Particle creation from expansion is utterly negligible.

**Proof references**: Team 2, Section 6.4.

### 2.8 Self-Duality Theorem (Three Forms)

**Status**: PROVEN (Rigor A)

Three interconnected self-dualities:

(a) **Legendre**: f(x) = x^2/2 is its own Fenchel conjugate: f*(p) = p^2/2.

(b) **Fourier**: The Gaussian exp(-x^2/2) is a fixed point of the Fourier transform.

(c) **Energetic**: Coherent states have equal position and momentum energy contributions: E_x = E_p = hbar omega / 4.

These are connected: Legendre self-duality of f implies Fourier self-duality of exp(-f) when the saddle-point approximation is exact (which it is for quadratics). The coherent state, whose wavefunction is Gaussian, inherits all three self-dualities.

The quadratic f(x) = x^2/2 is the UNIQUE self-dual convex function under Legendre-Fenchel among power functions. The Gaussian is the UNIQUE self-dual Schwartz function under Fourier.

**Proof references**: Team 4, Theorem 5.1 and Theorem 5.2.

### 2.9 |alpha|^2 = 1/2 from Energy Constraint

**Status**: PROVEN (algebraic, Rigor A)

For coherent product states with frequency omega = mc^2/hbar in Compton cells of volume lambda_C^3:

```
rho = m^4 c^5 (|alpha|^2 + 1/2) / hbar^3
```

Setting rho = m^4 c^5 / hbar^3 uniquely determines |alpha|^2 = 1/2. This is an algebraic consequence of the energy constraint, not a variational result.

**Proof references**: Team 4, Theorem 3.1.

### 2.10 Zero Entanglement in Cell Vacuum

**Status**: PROVEN (Rigor A, trivial)

For any bipartition of cells into sets A and A^c:

```
|Omega> = |Omega_A> tensor |Omega_{A^c}>
```

The reduced density matrix rho_A = |Omega_A><Omega_A| is pure, giving S_A = 0. The mutual information I(A:B) = 0 for all disjoint cell sets A, B.

**Proof references**: Team 3, Section 2.2.

### 2.11 Weyl Algebra Covariant Construction

**Status**: FRAMEWORK ESTABLISHED

Coherent states can be defined on the Weyl algebra of any globally hyperbolic spacetime without a global mode decomposition. The displacement is defined via the causal propagator. The construction is fully diffeomorphism covariant.

**Proof references**: Team 2, Section 4.

### 2.12 Vacuum Energy Ratio in d Dimensions

**Status**: PROVEN (new result)

For a free scalar field with massless dispersion in d spatial dimensions:

```
C_d = rho_cell / rho_mode(Compton) = 2(d+1)(2 pi)^d / Omega_d
```

where Omega_d = 2 pi^{d/2} / Gamma(d/2) is the solid angle of S^{d-1}.

Explicit values: C_1 = 4 pi, C_2 = 12 pi, C_3 = 16 pi^2, verified for d = 1, 2, 3.

**Proof references**: Team 4, Theorem 2.1.

---

## 3. Demoted Claims (Classroom Conjectures That Failed)

### 3.1 Legendre-Fenchel Duality as Formal Theorem

**Claimed**: The cell vacuum energy is the Fenchel conjugate of the mode vacuum energy. The two vacuum constructions are related by convex duality.

**What failed**: The cell vacuum energy is a single number rho_cell for a given mass m. The Fenchel conjugate f*(nu) is a function of the dual variable nu. A number cannot equal a function. The primal variable N (mode count) and dual variable nu have no natural physical identification in the cell vacuum framework. The duality pairing <nu, N> = nu * N has no physical interpretation connecting the two vacuum constructions.

**What survives**: The mode vacuum energy f(N) = A N^4 does have a well-defined Fenchel conjugate f*(nu) = B nu^{4/3}. The quartic-to-4/3 taming is real mathematics. The structural analogy -- momentum-space divergence is tamed by moving to position space -- captures real physics. But the analogy does not constitute a formal duality theorem.

**Assessment**: Useful metaphor. Not a theorem. The search for a precise mathematical duality relating the two vacua remains open.

### 3.2 16 pi^2 as a Fundamental Constant

**Claimed**: 16 pi^2 is a "conjugate limit constant" C_3, analogous to the 1/2 in the uncertainty principle. It represents a fundamental bound on the ratio of position-space to momentum-space vacuum energy densities.

**What failed**: The ratio C_d = 2(d+1)(2 pi)^d / Omega_d depends on spatial dimension d, dispersion relation, and cutoff convention. In d = 1, it is 4 pi; in d = 2, it is 12 pi; in d = 3, it is 16 pi^2. The uncertainty principle bound 1/2 is dimension-independent and convention-independent. These are fundamentally different types of constants.

For massive fields (the physically relevant case), the ratio is not 16 pi^2 but approximately 103 (correction factor ~1.53 from the dispersion relation).

**What replaces it**: 16 pi^2 is the exact geometric factor arising from the 3D phase-space integration with massless dispersion. It decomposes as: 2 pi^2 (angular/density-of-states) times 2 (zero-point factor) times 4 (quartic integral). It is a well-understood geometric quantity, not a mysterious fundamental constant.

### 3.3 Variational Uniqueness

**Claimed**: |alpha|^2 = 1/2 is uniquely selected by minimizing energy density fluctuations subject to constraints.

**What failed**: At fixed mass m, the energy constraint alone forces |alpha|^2 = 1/2 with no freedom to minimize anything. When m is treated as a free parameter, the critical point of the variance is a MAXIMUM (second derivative = -16 m^6 c^{10} / hbar^6 < 0), not a minimum.

**What replaces it**: The determination of |alpha|^2 = 1/2 is algebraic, not variational. It follows directly from setting the energy per cell to hbar omega = mc^2. This is a cleaner and more honest characterization. The earlier classroom result on variational uniqueness among minimum-uncertainty product states (verified findings Section 1.10) remains valid but is narrower than originally claimed -- it selects coherent states over squeezed states, given that the energy is already fixed.

### 3.4 10^{123} as a Duality Gap

**Claimed**: The 10^{123} discrepancy between mode vacuum energy (at Planck cutoff) and observed dark energy is a "duality gap" in the sense of convex optimization.

**What failed**: No formal primal-dual optimization structure exists. No primal problem has optimum rho_mode(Planck). No dual problem has optimum rho_cell. The 10^{123} ratio depends on the arbitrary choice of Planck cutoff and changes with any other cutoff choice. A true duality gap is a property of the optimization problem, independent of such choices.

**What replaces it**: The 10^{123} discrepancy is the cosmological constant problem -- the mismatch between naive zero-point energy estimates and observation. The cell vacuum framework proposes a resolution (use a different state), but this resolution is not naturally expressed as a convex duality gap.

### 3.5 Convex Duality on State Space

**Claimed**: There is a nontrivial convex duality structure on the space of quantum states, with mode and cell vacua as primal/dual minimizers.

**What failed**: The energy density functional rho(omega) = omega(T_00) is linear on the state space. The Fenchel conjugate of a linear functional is the indicator function of a singleton -- trivial. For nonlinear functionals (like the variance), there is no natural pair of primal/dual optimization problems whose solutions are the mode and cell vacua.

### 3.6 Modular Theory Connection

**Claimed**: The mode-to-cell vacuum transition might be related to modular conjugation in Tomita-Takesaki theory.

**What failed**: Modular conjugation J acts on the algebra (M --> M'), preserves the state, and is antiunitary. The mode-to-cell transition changes the state, preserves the algebra, and is not a Hilbert space map (the states are in inequivalent representations). These are fundamentally different operations. Furthermore, the cell vacuum fails the cyclicity condition needed for the Tomita-Takesaki construction.

**Assessment**: No evidence for any connection. Would require the full AQFT construction to be completed before even attempting.

### 3.7 Category Theory Approach

**Claimed**: The two-vacuum structure might be naturally expressed as a categorical duality (adjoint functors, natural transformations, or topos-theoretic formulation).

**What failed**: The "category of physical questions" is not well-defined. The functors F_mode and F_cell give different numbers for the same observable and do not admit a natural transformation. The topos-theoretic approach (contextual quantum theory) has not been applied to this problem and would require substantial development.

**Assessment**: Adds abstraction without content at the current stage. May become useful after AQFT construction is complete, but premature now.

---

## 4. New Problems Discovered

### 4.1 Black Hole Entropy Tension (CRITICAL)

**The problem**: The Bekenstein-Hawking entropy S = A/(4 l_P^2) is one of the most established results in quantum gravity. A leading explanation is that it equals the entanglement entropy of the vacuum across the horizon. The mode vacuum's area-law entanglement naturally produces S proportional to A/epsilon^2.

The cell vacuum has exactly zero entanglement entropy for any bipartition. If the cell vacuum is the correct vacuum for gravitational questions, then the entanglement entropy across a black hole horizon is zero -- in direct conflict with Bekenstein-Hawking.

**Possible resolutions** (all speculative):
- Scale-dependent vacuum: cell vacuum at cosmological curvatures, mode vacuum near black holes
- Emergent entanglement: black hole formation dynamically generates entanglement
- Different entropy mechanism: Bekenstein-Hawking entropy is not entanglement entropy
- Hybrid picture: transition governed by local curvature R lambda_C^2 ~ O(1)

**Priority**: HIGHEST. This is existential for the framework.

### 4.2 Absence of Unruh Effect

**The problem**: The cell vacuum does not support the Unruh effect through the standard Bisognano-Wichmann mechanism. The product state fails the cyclicity condition for local algebras. An accelerating observer in the cell vacuum would not detect a thermal bath at the Unruh temperature.

**Framework response**: The Unruh effect is a particle-counting question (how many particles does an accelerating detector register?) and should use the mode vacuum. The cell vacuum answers energy density questions, not particle-counting questions.

**Assessment**: This response is philosophically consistent with the framework's two-vacuum philosophy, but the transition criterion between the two descriptions is not formalized.

### 4.3 AdS/CFT Incompatibility

**The problem**: The quantum error correction structure of AdS/CFT requires boundary entanglement. Zero entanglement gives trivial error correction, and Van Raamsdonk's argument says zero mutual information implies disconnected bulk geometry.

**Mitigating factor**: AdS/CFT applies to anti-de Sitter space. Our universe is approximately de Sitter. The cell vacuum may be appropriate for dS holography, where the structure is fundamentally different and less understood.

**Priority**: Moderate. The incompatibility with AdS/CFT may be a feature rather than a bug if the cell vacuum is specific to de Sitter cosmology.

### 4.4 Equation of State w = -1 Not Derived

**The problem**: On curved spacetime, the classical displacement field in the cell vacuum has spatial gradients within cells that produce w = -2/3, not w = -1. The quantum contribution (zero-point energy) is needed to restore w = -1, but this contribution depends on the renormalization prescription.

**What's needed**: A complete stress-energy computation <T_{ij}> for the cell vacuum on FRW spacetime using Hadamard point-splitting or adiabatic regularization.

**Priority**: High. Without w = -1, the cell vacuum cannot serve as a cosmological constant.

### 4.5 Absolute Energy Density as Renormalization Condition

**The problem**: Wald's axioms for stress-energy renormalization on curved spacetime leave the cosmological constant term ambiguous. The cell vacuum framework's prediction rho = m^4 c^5 / hbar^3 amounts to fixing this ambiguity -- a renormalization condition, not a derivation.

**Interpretation**: Either (a) the cell vacuum provides a new physical principle that fixes the renormalization ambiguity (which would be a significant result), or (b) the cell vacuum's prediction is a renormalization condition in disguise (the conservative interpretation).

**Priority**: Conceptually important but not blocking. The framework's testable predictions don't depend on resolving this philosophical question.

### 4.6 Mass Selection Still Unexplained

**The problem**: Why does only the lightest neutrino determine the cosmological constant? On curved spacetime, all massive fields are present simultaneously. The framework does not explain why the cell vacuum for heavier species does not contribute. This was identified in the verified findings as the "biggest conceptual gap" and remains so.

**Priority**: High. This is the most significant unexplained assumption of the framework.

---

## 5. The Conjugate Limits Contribution -- Honest Assessment

### What Conjugate Limits Actually Contributes

**Self-duality (real, proven)**: The most substantive contribution. The three interconnected self-dualities (Legendre, Fourier, energy equipartition) are rigorously proven and physically meaningful. They establish that coherent states -- and hence the cell vacuum -- treat position and momentum symmetrically. This is a genuine structural insight.

**The analogy (useful, not a theorem)**: The analogy between the two vacua and conjugate descriptions (position vs momentum, Fourier duals) correctly identifies the core physics: the mode vacuum is a momentum-space construction; the cell vacuum is a position-space construction; using one for the other's natural domain is a category error. This analogy guided the framework's development and remains a valuable organizing principle. But it is an analogy, not a formal mathematical duality.

**The d-dimensional formula (new, proven)**: C_d = 2(d+1)(2 pi)^d / Omega_d is a new general result for the vacuum energy ratio in arbitrary dimension. While it demotes 16 pi^2 from "fundamental" to "geometric," the formula itself is a clean, verified result.

### What the Formal Machinery Doesn't Provide

The Legendre-Fenchel duality program does not produce a theorem connecting the two vacua. The convex analysis framework is the wrong tool: the relevant objects (vacuum states on infinite-dimensional algebras) are not naturally described by finite-dimensional convex functions and their conjugates. The attempt to force them into this framework produced only trivial results (linear functionals have trivial conjugates) or category errors (confusing numbers with functions).

Modular theory, category theory, and other abstract frameworks were explored and found unproductive at the current stage. This is not necessarily permanent -- after the AQFT construction is complete, some of these may become relevant -- but they contribute nothing now.

### Dr. Lim's Assessment

The conjugate limits framework is best understood as providing *language and intuition* for the Two Vacua, not *theorems*. The language of complementary descriptions, self-duality, and position-momentum trade-offs is accurate and useful. The attempt to elevate this language to formal mathematical theorems was premature and largely failed.

The honest contribution is:
1. Self-duality theorem (proven, significant)
2. Structural analogy (genuine, guides intuition)
3. The d-dimensional formula (proven, minor)

The honest non-contribution is:
4. Formal Fenchel duality (failed)
5. Fundamental constants (demoted)
6. Variational selection (algebraic, not variational)
7. Category theory / modular theory (no content)

---

## 6. Updated Framework Status

### On Solid Ground

- **Cell vacuum is a legitimate AQFT state** (Rigor A-B). This was the foundational question and it is answered positively.
- **Reeh-Schlieder is not an obstacle** (Rigor A). The product state structure is consistent with AQFT.
- **Unitary inequivalence with mode vacuum** (Rigor A). The two states are in different superselection sectors.
- **Hadamard condition satisfied** (Rigor A). Renormalized T_{mu nu} is well-defined.
- **Self-consistency on curved spacetime** (Rigor A). Flat-space calculation is justified to 10^{-69}.
- **Stability under expansion** (Rigor A). Parker particle creation is negligible.
- **Self-duality of coherent states** (Rigor A). The building blocks are the unique self-dual objects.
- **Dimensional analysis** (Rigor A). rho = m^4 c^5 / hbar^3 is unique.
- **Numerical predictions** (verified). Sum ~ 61 meV, normal ordering, w = -1.

### On Shaky Ground

- **w = -1 equation of state**: Assumed from the quantum oscillator interpretation. Not derived from curved-space stress-energy computation. The classical field analysis gives w = -2/3.
- **Absolute energy density**: Amounts to a renormalization condition beyond standard AQFT. Not derivable from the axioms alone.
- **Mass selection**: "Only the lightest neutrino contributes" is the framework's biggest assumption with no supporting mechanism.
- **Conjugate limits formal structure**: Self-duality survives, but the broader duality program failed.

### What Has Fallen

- **Fenchel duality as a theorem** between the two vacua
- **16 pi^2 as a fundamental constant** (geometric factor only)
- **Variational uniqueness** of |alpha|^2 = 1/2 (it's algebraic)
- **10^{123} as a duality gap** (no formal structure)
- **Modular theory / category theory connections** (no content)
- **De Sitter entropy from Compton counting** (10^{60} not 10^{122}, confirmed failure)

### New and Serious

- **Black hole entropy tension**: Zero entanglement vs Bekenstein-Hawking. This is the most critical new problem discovered in this investigation. It must be addressed for the framework's internal consistency.
- **Unruh effect absence**: The cell vacuum doesn't support the standard thermal detection mechanism for accelerating observers.
- **AdS/CFT incompatibility**: The product state structure is prima facie incompatible with holographic error correction (though AdS/CFT may be irrelevant for de Sitter).

### Updated Probability Assessment

| Assessor | Pre-investigation | Post-investigation | Rationale |
|----------|-------------------|-------------------|-----------|
| Vega | 40% | 40-43% | Foundations strengthened; black hole entropy problem is new and serious; net roughly neutral |
| Lim | "3-6 months to prove or disprove" | Conjugate limits narrower than expected; self-duality survives | Formal program accelerated (mostly resolved, mostly negative) |
| Feynman | "Promising, check back in 5 years" | Still promising; foundations now solid; new problems identified | The framework is more rigorous but also more constrained than before |

The DESI DR2 tension (Sum < 53 meV at 95% CL vs prediction 60.5-61 meV) remains the primary experimental pressure. The framework has no free parameters to adjust.

---

## 7. Research Roadmap

Ordered by priority (most critical first):

### Priority 1: Black Hole Entropy (Critical, Existential)

**Problem**: Zero entanglement in the cell vacuum appears to conflict with Bekenstein-Hawking entropy.

**Approaches**:
- Investigate whether black hole formation dynamically generates entanglement from a product state background
- Develop the "scale-dependent vacuum" proposal: cell vacuum for R lambda_C^2 << 1, mode vacuum for R lambda_C^2 ~ O(1)
- Explore whether Bekenstein-Hawking entropy can be derived without vacuum entanglement (microstate counting, Euclidean path integral approaches)
- Determine whether the cell vacuum near a black hole differs from the cosmological cell vacuum

**Estimated difficulty**: Hard. Requires understanding of black hole physics in the cell vacuum representation.

### Priority 2: Equation of State Computation (High)

**Problem**: w = -1 is assumed from the quantum oscillator interpretation but not derived from curved-space stress-energy.

**Approaches**:
- Compute <T_{ij}> for the cell vacuum on FRW using Hadamard point-splitting
- Alternatively, use adiabatic regularization to compute the full <T_{mu nu}>
- Determine whether the quantum and classical contributions combine to give w = -1

**Estimated difficulty**: Substantial but tractable. This is a well-defined calculation using existing AQFT technology.

### Priority 3: Mass Selection Mechanism (High)

**Problem**: Why only the lightest neutrino? No mechanism exists.

**Approaches**:
- Investigate whether heavier particle cell vacua are dynamically unstable
- Explore whether the cell vacuum for heavier species decouples from gravity
- Consider whether the IR dominance argument (lightest mass = largest cells = dominant at cosmological scales) can be formalized
- Examine the phase transition interpretation (heavier species' cell vacua may correspond to different phases that don't survive cosmological evolution)

**Estimated difficulty**: Very hard. May require new physical ideas beyond AQFT.

### Priority 4: AQFT Energy Density Derivation (Important)

**Problem**: The energy density rho = m^4 c^5 / hbar^3 is a direct counting argument, not derived from AQFT renormalization.

**Approaches**:
- Compute omega_Omega(T_{00}^{ren}) using Hadamard subtraction
- Determine whether the renormalization condition can be motivated by an additional physical principle (minimum uncertainty, locality, etc.)
- Compare with other renormalization prescriptions (adiabatic, zeta function, dimensional regularization)

**Estimated difficulty**: Substantial. The computation is well-defined but the interpretation of the renormalization condition is conceptually challenging.

### Priority 5: Experimental Monitoring (Ongoing)

**Timeline and targets**:
- DESI DR3+ (2026-2028): Sum ~ 40 meV sensitivity. Could confirm or exclude.
- Euclid (2025-2030): Complementary cosmological constraints.
- JUNO (2025-2030): Mass ordering determination at >3 sigma.
- CMB-S4 (2030s): Definitive test -- will detect Sum ~ 61 meV or exclude it at high significance.
- DUNE (2030s): Definitive ordering test at 5 sigma.

**The framework predicts**: Sum = 60.5-61.0 meV, normal ordering, w = -1 exactly. No adjustable parameters.

### Priority 6: Transition Between Descriptions (Long-term)

**Problem**: If the cell vacuum applies for some questions and the mode vacuum for others, what governs the transition?

**Approaches**:
- Develop the curvature criterion: R lambda_C^2 ~ O(1) as the transition scale
- Investigate the connection between the vacuum choice and the type of observable being computed
- Formalize the "category error" as a statement about which state is appropriate for which subalgebra

**Estimated difficulty**: Hard. May require conceptual advances in the foundations of QFT.

### Priority 7: Conjugate Limits -- What Remains (Lower)

**After the failed conjectures, the remaining open questions are**:
- Is there a mathematical duality connecting the two vacua, even if not Fenchel? (Possibly in the AQFT framework, not convex analysis)
- Does the self-duality of coherent states play a selective role, or is it merely a property of the selected construction?
- Can the analogy between the two vacua and complementary descriptions be sharpened into a theorem?

**Estimated difficulty**: Moderate. The search space has been significantly narrowed by knowing what doesn't work.

---

## References

### AQFT Foundations
1. Haag, R. (1996). *Local Quantum Physics*. Springer.
2. Haag, R. and Kastler, D. (1964). J. Math. Phys. 5, 848-861.
3. Bratteli, O. and Robinson, D.W. (1987/1997). *Operator Algebras and QSM*, Vols. 1-2. Springer.

### Curved Spacetime QFT
4. Wald, R.M. (1994). *QFT in Curved Spacetime and Black Hole Thermodynamics*. Chicago.
5. Brunetti, R., Fredenhagen, K., and Verch, R. (2003). Commun. Math. Phys. 237, 31-68.
6. Kay, B.S. and Wald, R.M. (1991). Phys. Rep. 207, 49-136.
7. Hollands, S. and Wald, R.M. (2001). Commun. Math. Phys. 223, 289-326.

### Coherent States and Inequivalence
8. Shale, D. (1962). Trans. Amer. Math. Soc. 103, 149-167.
9. Derezinski, J. and Gerard, C. (2013). *Mathematics of Quantization and Quantum Fields*. Cambridge.
10. Manuceau, J. et al. (1973). Commun. Math. Phys. 32, 231-243.

### Entanglement and Black Holes
11. Bombelli, L. et al. (1986). Phys. Rev. D 34, 373.
12. Srednicki, M. (1993). Phys. Rev. Lett. 71, 666.
13. Bisognano, J.J. and Wichmann, E.H. (1975). J. Math. Phys. 16, 985.
14. Almheiri, A., Dong, X., and Harlow, D. (2015). JHEP 04, 163.
15. Van Raamsdonk, M. (2010). Gen. Rel. Grav. 42, 2323-2329.

### Convex Analysis
16. Rockafellar, R.T. (1970). *Convex Analysis*. Princeton.

---

**Document prepared**: January 31, 2026
**Synthesis team**: Feynman, Vega, Lim
**Status**: DEFINITIVE. This document supersedes all prior assessments of the AQFT construction. It incorporates all results from the four-team investigation and the verified findings v2.
