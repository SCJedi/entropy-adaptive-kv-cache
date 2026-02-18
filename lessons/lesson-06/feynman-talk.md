# The Numbers -- Predictions and the 16pi^2 Factor
### A Feynman-Voice Lecture

---

Now we get to the numbers. And I have to tell you up front: the first principle is that you must not fool yourself, and you are the easiest person to fool. This lesson is where that principle gets tested hardest, because there is a circularity hiding in plain sight, and if I don't point it out clearly, I'm not doing my job.

Let's start with what's solid.

## The Only Formula You Can Write Down

Here's a question: given a particle of mass $m$, the speed of light $c$, and Planck's constant $\hbar$, how many ways can you build an energy density?

One. Exactly one.

Write $\rho = m^a \, c^b \, \hbar^d$ and demand $[\rho] = M L^{-1} T^{-2}$. You get three equations:

$$
a + d = 1, \quad b + 2d = -1, \quad -b - d = -2
$$

Solve them. The determinant of the coefficient matrix is $-1$, so the solution is unique: $a = 4$, $b = 5$, $d = -3$. **[PROVEN]**. That's just linear algebra. A freshman could do it.

$$
\rho = K \cdot \frac{m^4 c^5}{\hbar^3}
$$

where $K$ is some dimensionless number that dimensional analysis can't fix. The cell vacuum construction gives $K = 1$ -- one quantum $mc^2$ per Compton cell. That's a physical input, not a mathematical necessity. But the scaling -- the fourth power of mass -- that's locked in.

Now here's what makes this interesting. If you plug in a mass of about 2.3 meV, you get the observed dark energy density. And 2.3 meV is exactly the right ballpark for the lightest neutrino mass.

Suggestive? Yes. Proof? No. Let me show you why.

## The Circularity Trap

Here's the chain of reasoning, laid out honestly:

**Step 1.** Observe $\rho_\Lambda \approx 5.96 \times 10^{-10}$ J/m$^3$. That's the dark energy density. Measured by astronomers. **[PROVEN]**.

**Step 2.** Hypothesize: $\rho_\Lambda = m^4 c^5/\hbar^3$. That's the cell vacuum formula. **[FRAMEWORK]** -- it's a proposal, not established physics.

**Step 3.** Solve for $m$:

$$
m = \left(\frac{\rho_\Lambda \hbar^3}{c^5}\right)^{1/4} \approx 2.31 \text{ meV}
$$

**Step 4.** Compute $\rho_{\text{cell}} = m^4 c^5/\hbar^3$ and discover -- miracle! -- it equals $\rho_\Lambda$.

Except it's not a miracle. It's algebra. Step 3 *defined* $m$ to make Step 4 true. You put $\rho_\Lambda$ into the formula, extracted $m$, put $m$ back into the same formula, and got $\rho_\Lambda$ back. Of course you did. That's what solving an equation means.

I've seen this mistake before. Someone gets excited about a "0.4% match" between their calculated density and the observed one. But if you extracted your parameter from the observation, the match is guaranteed. You could do the same trick with any formula that has one free parameter. It tells you nothing.

**The "0.4% match" claim has been retired.** It was circular, and presenting circular reasoning as evidence is exactly the kind of self-fooling I warned you about. **[FRAMEWORK]**

## When Does It Stop Being Circular?

Good question. The circularity breaks when you have independent evidence for the value of $m_1$.

See, right now $m_1 = 2.31$ meV is *extracted* from $\rho_\Lambda$. It's not independently measured. But neutrino physics gives us something to work with: the mass-squared differences from oscillation experiments. Those are independently measured to high precision:

$$
\Delta m_{21}^2 = 7.53 \times 10^{-5} \text{ eV}^2, \qquad \Delta m_{31}^2 = 2.453 \times 10^{-3} \text{ eV}^2
$$

**[PROVEN]** -- these come from decades of solar, atmospheric, reactor, and accelerator neutrino experiments.

Now take our extracted $m_1 = 2.31$ meV and use it:

$$
m_2 = \sqrt{m_1^2 + \Delta m_{21}^2} \approx 9.0 \text{ meV}
$$

$$
m_3 = \sqrt{m_1^2 + \Delta m_{31}^2} \approx 49.6 \text{ meV}
$$

$$
\Sigma m_\nu = m_1 + m_2 + m_3 \approx 60.9 \text{ meV}
$$

**[FRAMEWORK]** for the prediction. The oscillation data that goes into it is **[PROVEN]**.

That sum -- 60.9 meV -- is a real prediction. It doesn't suffer from the circularity because it combines the extracted $m_1$ with independent data. If cosmological surveys measure $\Sigma \approx 61$ meV, that's evidence. If they measure $\Sigma < 50$ meV, the specific value $m_1 = 2.31$ meV is dead.

## The DESI Pressure

And here's where I have to be honest about the current situation. DESI DR2 -- that's the Dark Energy Spectroscopic Instrument, second data release -- gives:

$$
\Sigma m_\nu < 53 \text{ meV at 95% CL}
$$

Our prediction is 61 meV. That's 1.5 to 2 sigma tension. **[TENSION]**

Is it falsified? Not yet. In physics, you need 3 to 5 sigma to kill something. But it's not comfortable. The framework has zero free parameters to adjust. There's no knob to turn, no "well, if we change this assumption slightly..." The prediction is sharp: 61 meV, take it or leave it.

That's either a virtue or a death sentence, depending on what the data says. We'll know within the decade. CMB-S4 will have sensitivity down to 15-20 meV on the sum. That's definitive either way.

## The 16pi^2 Story -- A Beautiful Idea That Didn't Pan Out

Now let me tell you about something that was once thought to be important and turned out not to be.

In the mode vacuum calculation, you integrate over momentum space and get:

$$
\rho_{\text{mode}} = \frac{\hbar c \Lambda^4}{16\pi^2}
$$

That $16\pi^2 \approx 158$. Someone looked at this and said: "Aha! The ratio between the cell vacuum and the mode vacuum at the Compton cutoff is exactly $16\pi^2$. That must be a fundamental constant!"

It's not. **[DEMOTED]**.

Here's why. That factor comes from the angular integration in three-dimensional $k$-space. The volume element is $d^3k = 4\pi k^2 dk$ (that's the solid angle of the 2-sphere), and the $(2\pi)^3$ in the Fourier transform denominator gives you $1/(2\pi)^3$. Combine them and you get $4\pi / (2\pi)^3 = 1/(2\pi^2)$. Multiply by the radial integral factors and out pops $1/(16\pi^2)$.

But what happens in $d$ dimensions? The general formula is:

$$
C_d = \frac{2(d+1)(2\pi)^d}{\Omega_d}
$$

where $\Omega_d = 2\pi^{d/2}/\Gamma(d/2)$ is the surface area of the unit sphere in $d$ dimensions. **[PROVEN]**.

In one dimension: $C_1 = 4\pi$. In two dimensions: $C_2 = 12\pi$. In three: $C_3 = 16\pi^2$. Each dimension gives a different number. A "fundamental constant" that depends on how many dimensions you're in isn't fundamental -- it's geometric.

And it gets worse. That $16\pi^2$ is exact only for massless dispersion $\omega = ck$. For massive fields, $\omega = \sqrt{k^2 c^2 + m^2 c^4/\hbar^2}$, and the ratio changes. The correction factor is about 1.53, bringing the ratio down from 158 to about 103. **[PROVEN]**.

So $16\pi^2$ is not a deep physical constant connecting two descriptions of the vacuum. It's a solid-angle factor in a specific dimension with a specific dispersion relation. Still useful for calculations, but not the Rosetta Stone it was once advertised as.

## The Fourth-Root Shield

One nice feature of the mass extraction formula: the fourth root.

$$
m = \rho_\Lambda^{1/4} \cdot (\hbar^3/c^5)^{1/4}
$$

Uncertainties get divided by four. The Hubble tension -- which creates a 10-15% uncertainty in $\rho_\Lambda$ depending on which measurement of $H_0$ you trust -- produces only a 2.5-3.5% uncertainty in $m_1$. The robust range is $m_1 = 2.24$-$2.34$ meV.

That's actually reassuring. The prediction isn't fragile to the exact value of the cosmological parameters. **[PROVEN]** as a mathematical property of the fourth root, not as physics.

## What's Real and What's Not

Let me lay it all out, because I think clarity matters more than enthusiasm.

**Real and proven:**
- The 3x3 dimensional analysis giving $m^4 c^5/\hbar^3$ as unique. That's linear algebra.
- The $C_d$ formula. That's calculus.
- The massive field correction. That's a straightforward integral.
- The oscillation mass-squared differences. That's decades of experiments.

**Framework -- testable but not established:**
- The identification $\rho_\Lambda = m^4 c^5/\hbar^3$. A hypothesis.
- The mass $m_1 \approx 2.31$ meV. Extracted circularly.
- The spectrum prediction $\Sigma \approx 61$ meV. Genuinely testable.

**Dead:**
- The "0.4% match." Circular.
- $16\pi^2$ as fundamental. Dimension-dependent.
- Fenchel duality connecting the two vacua. Category error in the conjecture itself.
- Variational uniqueness of $|\alpha|^2 = 1/2$. It's algebraic determination, not optimization.

I know some people want me to be more enthusiastic about this. But I'd rather have a clear-eyed view of what we actually know than a false sense of progress. The numbers will either work or they won't. The experiments will decide. That's how physics is supposed to work.

## What's Next

In Lesson 7, we leave the numbers behind and go to the mathematics. The AQFT construction -- algebraic quantum field theory. This is where the cell vacuum gets put on rigorous mathematical foundations. And unlike the numbers in this lesson, which may or may not survive experimental test, the mathematical results are proven. The cell vacuum is a legitimate state. It satisfies the Hadamard condition. It's unitarily inequivalent to the mode vacuum. Those are theorems, not predictions.

But even here, I want you to keep something in mind: AQFT tells us the cell vacuum *exists* as a mathematical object. It doesn't tell us it's *right* -- that it's the state nature actually chose. That's a different question, and it requires experiment to answer.

---

*Evidence tiers in this lesson: [PROVEN] for dimensional analysis and geometric factors; [FRAMEWORK] for mass extraction and spectrum predictions; [DEMOTED] for 16pi^2 as fundamental and the circular match claim; [TENSION] for the DESI constraint.*
