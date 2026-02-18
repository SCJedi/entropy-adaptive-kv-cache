# Part 5: Cosmology Basics

## The Universe at Large

You've glimpsed cosmology before. Maybe you remember something about the Big Bang, dark matter, that famous photo of the cosmic microwave background. Fifteen years is a long time. Let's rebuild it from scratch—but properly this time, with the actual numbers and equations that make it real.

Here's the remarkable thing about cosmology: we can actually measure the universe. Not philosophize about it. Measure it. And the measurements tell us something disturbing: we don't know what 95% of the universe is made of.

That's not a failure of cosmology—it's its greatest discovery.

---

## 1. The Expanding Universe

### Hubble's Discovery

In 1929, Edwin Hubble made one of the most profound observations in the history of science. He was measuring the distances to galaxies (itself a recent discovery—that those fuzzy "nebulae" were entire galaxies like our own) and comparing them to how fast each galaxy was moving toward or away from us.

The way you measure whether something is coming or going is through the Doppler shift. Light from an approaching source is shifted toward blue (shorter wavelengths). Light from a receding source is shifted toward red (longer wavelengths). The amount of shift tells you the velocity.

Hubble found something astonishing: almost every galaxy is moving away from us. And there's a pattern:

**The farther away a galaxy is, the faster it's receding.**

This is Hubble's Law:

$$v = H_0 d$$

Where:
- **v** is the recession velocity (how fast the galaxy is moving away)
- **d** is the distance to the galaxy
- **H₀** is Hubble's constant (the proportionality factor)

The modern value of Hubble's constant is approximately:

$$H_0 \approx 70 \text{ km/s/Mpc}$$

(There's actually a tension between different measurement methods giving values around 67-73 km/s/Mpc. This "Hubble tension" is an active research problem. We'll use 70 as a round number.)

What does this mean physically? A galaxy 1 megaparsec away (about 3.26 million light-years) is receding at 70 km/s. A galaxy 10 megaparsecs away is receding at 700 km/s. A galaxy 100 megaparsecs away is receding at 7,000 km/s.

Double the distance, double the velocity.

### Not What You Think

Your first instinct might be: "So we're at the center of some explosion, and everything is flying away from us?"

No. That's wrong. Here's how you know it's wrong:

If we were at the center of an explosion, galaxies on one side would be flying away in one direction, galaxies on the other side flying in the opposite direction. They'd all be moving through space, away from a special point (us).

But Hubble's law says something different. It says velocity is proportional to distance. And here's the key: **this same relationship holds no matter where you are in the universe**.

If you were in that distant galaxy 100 megaparsecs away, you'd observe exactly the same thing: all galaxies receding, velocity proportional to distance. You'd think YOU were at the center.

Everyone thinks they're at the center. Which means no one is.

### Space Itself Is Expanding

The resolution is startling: galaxies aren't moving through space. Space itself is expanding, carrying the galaxies along.

Think of the surface of a balloon being inflated. Put dots on the balloon with a marker. As the balloon expands, every dot moves away from every other dot. No dot is special. No dot is the "center of the expansion"—the center of the expansion isn't on the balloon's surface at all.

Or think of raisin bread dough. Scatter raisins through the dough. As the bread rises, every raisin moves away from every other raisin. The "velocity" of recession is proportional to the separation—raisins that start farther apart end up receding faster because there's more expanding dough between them.

This is what's happening to space. The metric of space—the relationship that defines distances—is changing with time. Space is stretching.

### The Scale Factor

We describe this with the **scale factor** a(t). This is a dimensionless function that tells us how much space has stretched relative to some reference time (usually now, when we set a = 1).

If a = 0.5, distances were half what they are today. If a = 2, distances will be double. The scale factor is the "size" of the universe in a meaningful sense.

Hubble's constant is related to the rate of change of the scale factor:

$$H = \frac{\dot{a}}{a}$$

Where ȧ (pronounced "a-dot") is the time derivative of a—the rate at which a is changing.

The current value H₀ tells us how fast the universe is currently expanding. But H isn't actually constant in time—it's been changing throughout cosmic history. More on that shortly.

### Redshift

When we observe a distant galaxy, the light from it was emitted long ago. That light has been traveling through space that's been expanding the whole time. The expansion stretches the wavelength of light itself.

The redshift z is defined by:

$$1 + z = \frac{\lambda_{\text{observed}}}{\lambda_{\text{emitted}}} = \frac{a_{\text{now}}}{a_{\text{then}}}$$

If z = 1, the universe has doubled in size since that light was emitted. The wavelength has doubled. We're seeing that galaxy as it was when the universe was half its current size.

The cosmic microwave background has redshift z ≈ 1100. The universe has expanded by a factor of 1100 since that light was emitted. Those photons started as hot visible light and have been stretched into microwaves.

---

## 2. The Big Bang

### Run the Movie Backward

If the universe is expanding now, it was smaller in the past. Run the movie backward. Go back far enough and the universe was much smaller, much denser, much hotter.

Keep going back. Everything gets closer together. The density increases without bound. The temperature rises without limit.

At some point—we can't actually go all the way back to "zero size" without our theories breaking down—the universe was unimaginably hot and dense. This initial state, and the subsequent expansion from it, is what we call the Big Bang.

**The Big Bang was not an explosion in space. It was the expansion of space itself.**

There was no "outside" for the universe to explode into. There was no "before" in any clear sense (time itself behaves strangely when spacetime is that curved). The Big Bang happened everywhere at once—because every point in our current universe was the Big Bang.

### Evidence for the Big Bang

This isn't speculation. We have multiple independent lines of evidence:

**1. The Expansion Itself**

We see the universe expanding. Run it backward mathematically, and you get a hot dense beginning about 13.8 billion years ago. (We know this number quite precisely from the cosmic microwave background.)

**2. The Cosmic Microwave Background (CMB)**

About 380,000 years after the Big Bang, the universe cooled enough for atoms to form. Before that, photons were constantly scattering off free electrons—the universe was opaque, like being inside a star. When atoms formed, the photons were suddenly free to travel unimpeded.

Those photons are still traveling. They fill the universe. They've been redshifted from hot visible light down to microwaves at temperature T ≈ 2.725 K.

This is the oldest light we can see. It comes from every direction because the hot dense state was everywhere. The CMB is the afterglow of the Big Bang.

Penzias and Wilson discovered it accidentally in 1965 while trying to eliminate noise from their radio antenna. They won the Nobel Prize. (The noise turned out to be the birth cry of the universe.)

**3. Primordial Nucleosynthesis**

In the first few minutes after the Big Bang, the universe was hot enough for nuclear reactions but cool enough for nuclei to survive. This is when the light elements were forged:

- About 75% hydrogen (by mass)
- About 25% helium-4
- Trace amounts of deuterium, helium-3, lithium-7

We can calculate exactly what abundances should emerge based on the physics of that era. The predictions match observations throughout the universe. The helium abundance, in particular, is nearly uniform everywhere we look—it's primordial, baked in from the beginning.

Heavier elements (carbon, oxygen, iron, everything you're made of) came later, forged in stars and supernovae. But the light element ratios tell us about the first minutes.

**4. Cosmic Evolution**

We see the universe changing with time. Distant galaxies (which we see as they were in the past) are different from nearby galaxies. The universe looked different when it was younger.

We see galaxies forming, evolving, merging. We see a cosmic history that's consistent with expansion from a hot dense state.

### What the Big Bang Was NOT

- It was not an explosion at a point in space. There was no "center" of the explosion.
- It was not matter flying outward into pre-existing empty space.
- It was not the creation of the universe from nothing (that's a separate question we can't currently answer).

The Big Bang is the statement that the universe, at a finite time in the past, was in an extremely hot, dense state, and has been expanding and cooling since then.

---

## 3. The Friedmann Equations

### Einstein's Gift (and Mistake)

When Einstein developed general relativity, he tried to apply it to the universe as a whole. He wanted a static, eternal universe—that was the philosophical assumption of his time.

But his equations didn't give him one. They described a universe that would either expand or contract. To force a static solution, he added a term: the cosmological constant Λ.

Then Hubble discovered the expansion. Einstein reportedly called Λ his "biggest blunder"—he'd added a fudge factor to prevent his equations from giving him the correct answer.

Irony: we now know Λ (or something like it) is real. But Einstein added it for the wrong reason and got the wrong value.

### The Friedmann Equations

Alexander Friedmann (and independently Georges Lemaître) worked out the dynamics of an expanding universe using general relativity. The key result is:

$$\left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G\rho}{3} - \frac{k}{a^2} + \frac{\Lambda}{3}$$

Let me decode this piece by piece.

**Left side: (ȧ/a)²**

This is H², the Hubble parameter squared. It measures how fast the universe is expanding.

**First term on right: 8πGρ/3**

This is the contribution from energy density ρ. More energy density means faster expansion (gravity pulling everything together slows the expansion, but the density also tells us about the initial "momentum" of the expansion—it's complicated, but higher density generally means the universe had to be expanding faster in the past).

**Second term: -k/a²**

This is the curvature term. The constant k can be:
- k = +1: positive curvature (like a sphere)
- k = 0: flat (Euclidean geometry)
- k = -1: negative curvature (like a saddle)

The curvature affects how the expansion proceeds. Our universe appears to have k ≈ 0 (flat) to high precision.

**Third term: Λ/3**

The cosmological constant. A constant energy density of empty space itself. This is what we now call dark energy.

### Different Contents, Different Fates

Different types of stuff dilute differently as the universe expands:

**Radiation (photons, relativistic particles):**
- Energy density ρ ∝ a⁻⁴
- The number density goes as a⁻³ (volume increases), plus each photon loses energy as it's redshifted (another factor of a⁻¹)
- Equation of state: w = 1/3

**Matter (non-relativistic, including dark matter):**
- Energy density ρ ∝ a⁻³
- Just dilution—the number density drops as volume increases
- Equation of state: w = 0

**Cosmological constant (dark energy, if it's Λ):**
- Energy density ρ = constant
- Doesn't dilute at all. New space comes with its own energy density built in.
- Equation of state: w = -1

The equation of state w relates pressure to energy density: P = wρc². Negative w means negative pressure, which in general relativity causes accelerated expansion.

### The History of the Universe in Terms of Domination

Early universe: radiation dominated. The universe was hot, photons were everywhere, their energy dominated.

Middle era: matter dominated. As the universe expanded, radiation diluted faster (∝ a⁻⁴) than matter (∝ a⁻³). Eventually matter took over. This happened about 50,000 years after the Big Bang.

Recent era: dark energy dominated. As the universe continued expanding, matter diluted (∝ a⁻³) while dark energy stayed constant. Eventually dark energy took over. This happened a few billion years ago.

We live in the dark energy dominated era. The expansion is accelerating.

---

## 4. The Contents of the Universe

### What's in the Box?

Modern cosmology has measured the contents of the universe with remarkable precision, primarily through the cosmic microwave background (Planck satellite) and observations of large-scale structure.

Here's what we find:

| Component | Symbol | Fraction |
|-----------|--------|----------|
| Ordinary matter (baryons) | Ω_b | ~5% |
| Dark matter | Ω_DM | ~27% |
| Dark energy | Ω_Λ | ~68% |
| Radiation | Ω_r | ~0.01% |

The precise Planck 2018 values are:
- Ω_b h² = 0.0224 → Ω_b ≈ 0.049
- Ω_DM h² = 0.120 → Ω_DM ≈ 0.265
- Ω_Λ ≈ 0.685

(Here h ≈ 0.674 is the dimensionless Hubble parameter, H₀ = 100h km/s/Mpc.)

### Let That Sink In

We don't know what 95% of the universe is made of.

The stuff you're made of—protons, neutrons, electrons, atoms—is about 5% of the universe's energy content. Everything you can see with telescopes, every star, every galaxy, every cloud of gas: 5%.

27% is dark matter. We know it's there because of its gravitational effects. We don't know what it is.

68% is dark energy. We know it's there because the expansion is accelerating. We don't know what it is.

This isn't a failure of physics. This is physics telling us there's vastly more to understand.

---

## 5. Dark Matter

### Evidence: Things Don't Add Up

**1. Galaxy Rotation Curves**

Vera Rubin and Kent Ford (1970s) measured how fast stars orbit in spiral galaxies at different distances from the center.

For the solar system, we know how this works: planets further from the Sun orbit slower (Kepler's laws). Mercury zooms around; Neptune crawls. This is because most of the mass is concentrated in the Sun.

For galaxies, if most of the mass were in the visible stars near the center, we'd expect the same pattern: stars far from the center should orbit slower.

They don't. The rotation curves are flat—stars at large radii orbit at nearly the same speed as stars closer in.

This means there must be more mass at large radii than we can see. A lot more. Galaxies are embedded in vast halos of invisible matter.

**2. Gravitational Lensing**

General relativity tells us mass bends light. A massive object between us and a distant source will distort and magnify the source's image.

We can measure the total mass of galaxy clusters by how much they bend light from background galaxies. The answer: there's about 5× more mass than we can see in visible matter.

**3. The Cosmic Microwave Background**

The precise pattern of fluctuations in the CMB depends on the total matter content of the universe. The acoustic peaks in the power spectrum are sensitive to both ordinary matter and total matter separately.

The CMB tells us: total matter is about 32%, ordinary matter is about 5%. The difference—dark matter—is about 27%.

**4. Large-Scale Structure**

How galaxies cluster today depends on the growth of structure from small initial perturbations. The pattern of clustering we observe requires dark matter. Without it, the math doesn't work—structures wouldn't have had time to form.

### What We Know About Dark Matter

- It interacts gravitationally (that's how we see it).
- It doesn't interact electromagnetically (it doesn't emit, absorb, or scatter light—hence "dark").
- It doesn't interact via the strong force (otherwise we'd see it in nuclear reactions).
- It might or might not interact via the weak force (that's an open question).
- It's "cold"—meaning the particles move slowly compared to light.
- It's stable over cosmic timescales (it's still around).

### What We DON'T Know

- What particle(s) constitute dark matter
- Whether it's one type of particle or several
- What interactions it has beyond gravity
- Its mass (could range from 10⁻²² eV to many solar masses, depending on the model)

Leading candidates include:
- **WIMPs** (Weakly Interacting Massive Particles): particles with weak-force interactions and masses around 10-1000 GeV. Many experiments have searched; none have found anything.
- **Axions**: very light particles originally proposed to solve a different problem (CP violation in QCD). Mass around 10⁻⁵ eV. Active experimental searches ongoing.
- **Primordial black holes**: black holes formed in the early universe. Constrained but not ruled out in certain mass ranges.
- **Sterile neutrinos**: neutrinos that only interact gravitationally. Various mass scales possible.

### Equation of State

For cosmological purposes, dark matter behaves like ordinary matter: pressureless dust with equation of state w = 0. Its energy density dilutes as ρ ∝ a⁻³.

This is important: dark matter dominated the universe's evolution during the matter-dominated era, setting up the conditions for structure formation.

---

## 6. Dark Energy

### The Accelerating Universe

In 1998, two independent teams (the Supernova Cosmology Project and the High-Z Supernova Search Team) measured the distances to Type Ia supernovae at various redshifts.

Type Ia supernovae are "standard candles"—they have nearly uniform intrinsic brightness, so you can measure their distances by how bright they appear. Combine distance with redshift, and you can map the expansion history of the universe.

The expectation: the expansion should be slowing down. All that matter pulling on itself gravitationally should decelerate the expansion.

The observation: the expansion is speeding up.

Distant supernovae are fainter than they should be if the expansion were decelerating (or even constant). The universe has been expanding faster and faster.

Saul Perlmutter, Brian Schmidt, and Adam Riess shared the 2011 Nobel Prize for this discovery.

### What Could Cause This?

Something with negative pressure. General relativity says that pressure gravitates—positive pressure increases gravitational attraction, negative pressure causes repulsion.

For acceleration, we need:

$$w < -\frac{1}{3}$$

The simplest possibility is Einstein's cosmological constant Λ: a constant energy density of empty space with w = -1 exactly.

### The Cosmological Constant

If Λ is a fundamental constant, then empty space has a constant energy density:

$$\rho_\Lambda = \frac{\Lambda c^2}{8\pi G}$$

This doesn't dilute as the universe expands. New space comes with its own vacuum energy. As the universe gets bigger, there's more dark energy—not in density, but in total.

Eventually (and we're already in this era), dark energy dominates. The universe expands exponentially:

$$a(t) \propto e^{Ht}$$

This is de Sitter expansion. In the far future, all galaxies outside our local group will recede beyond our cosmic horizon. The observable universe will grow dark and empty.

### Or Something Else?

The data are consistent with w = -1 (cosmological constant), but there's room for other possibilities:

- **w slightly different from -1**: Maybe w = -0.95 or w = -1.05. Current measurements constrain w to be within a few percent of -1.

- **w changing with time**: Maybe w(a) varies as the universe evolves. This is called dynamical dark energy.

- **Quintessence**: A scalar field slowly rolling down its potential, similar to what's proposed for cosmic inflation. The value of w depends on how fast the field is rolling.

- **Modified gravity**: Maybe it's not dark energy at all—maybe general relativity needs modification on cosmological scales.

Current observations slightly favor w < -1 (the "phantom" regime), but not at high statistical significance. We don't know.

### The Coincidence Problem

Here's something strange: dark energy and matter have comparable densities right now.

Why is that strange? Because they scale differently. Dark matter dilutes as a⁻³. Dark energy stays constant. Their ratio changes dramatically with time.

In the early universe, dark matter dominated by factors of billions. In the far future, dark energy will dominate by factors of billions. But right now, at this particular moment in cosmic history, they're within a factor of 3 of each other.

Is this a coincidence? Or is there something we don't understand?

---

## 7. The Critical Density

### The Key Threshold

There's a special density that determines the geometry of the universe. It comes straight from the Friedmann equation.

Set k = 0 (flat) and Λ = 0 (no dark energy). The Friedmann equation becomes:

$$H^2 = \frac{8\pi G\rho}{3}$$

Solving for ρ:

$$\rho_{\text{crit}} = \frac{3H^2}{8\pi G}$$

This is the critical density: the energy density that makes the universe flat.

With current values (H₀ ≈ 70 km/s/Mpc):

$$\rho_{\text{crit}} \approx 9.5 \times 10^{-27} \text{ kg/m}^3$$

That's about 5.7 protons per cubic meter. Nearly empty. But on cosmic scales, it determines everything.

### Density Parameters

We express everything as fractions of critical density:

$$\Omega = \frac{\rho}{\rho_{\text{crit}}}$$

For each component:
- Ω_b ≈ 0.049 (baryons)
- Ω_DM ≈ 0.265 (dark matter)
- Ω_Λ ≈ 0.685 (dark energy)
- Ω_r ≈ 0.00009 (radiation, negligible today)

Total:

$$\Omega_{\text{total}} = \Omega_b + \Omega_{DM} + \Omega_\Lambda + \Omega_r \approx 1.00$$

The universe is flat (or extremely close to it). This isn't a coincidence—it's predicted by cosmic inflation, which drives the universe toward flatness.

### What Flatness Means

If Ω_total = 1 exactly, space is Euclidean on large scales. Parallel lines stay parallel. The interior angles of a triangle sum to 180°. Light travels in straight lines (except when curved by local mass concentrations).

If Ω_total > 1, space has positive curvature like the surface of a sphere. The universe is finite but unbounded (like the sphere's surface). Parallel lines eventually meet. Triangles have more than 180°.

If Ω_total < 1, space has negative curvature like a saddle. Parallel lines diverge. Triangles have less than 180°.

Observations of the CMB constrain:

$$\Omega_{\text{total}} = 1.000 \pm 0.002$$

Flat to better than 1%.

---

## 8. The Ratio That Matters

### Ω_Λ/Ω_DM

Let's compute a ratio that will become important:

$$\frac{\Omega_\Lambda}{\Omega_{DM}} = \frac{0.685}{0.265} \approx 2.58$$

Or using Planck 2018 values more precisely:

$$\frac{\Omega_\Lambda}{\Omega_{DM}} = \frac{0.685}{0.265} = 2.585$$

This is the ratio of dark energy to dark matter in the present universe.

### Why Does This Matter?

This ratio is not predicted by standard cosmology. The cosmological constant could be anything. Dark matter density depends on particle physics we don't understand. There's no reason these should have any particular relationship.

And yet:

$$\frac{\Omega_\Lambda}{\Omega_{DM}} \approx 2.58$$

Note that:
- 5/2 = 2.5
- φ² = (1.618...)² ≈ 2.618

The observed ratio falls between these two simple mathematical values.

Is this a coincidence?

### What Standard Cosmology Says

Standard cosmology treats Λ and dark matter density as independent parameters. We measure them. We don't predict them.

The near-integer nature of this ratio is not explained. The proximity to φ² is not explained. Standard cosmology says: "It's probably a coincidence. There are lots of numbers in physics; some will look special by chance."

Maybe. But in physics, when dimensionless ratios come out close to simple numbers, it often means we're missing something.

### The Foreshadowing

In the framework we're building toward, this ratio is NOT a coincidence.

The ratio Ω_Λ/Ω_DM ≈ 2.58 will emerge from deeper principles. Dark matter and dark energy will be related to each other—both connected to the neutrino mass scale and ultimately to the structure of the quantum vacuum.

For now, just note it: **2.58**. Remember that number.

---

## 9. What We'll Need Later

### Setting Up the Problem

We've laid out standard cosmology. Now let me tell you what's strange about it—the things that will connect to our Edge of Chaos framework.

### The 10¹²² Problem

Quantum field theory predicts that empty space should have a vacuum energy density. We calculated this in Part 4:

$$\rho_{\text{vacuum}}^{(QFT)} \sim 10^{113} \text{ J/m}^3$$

The observed value (from dark energy/cosmological constant) is:

$$\rho_\Lambda \approx 6 \times 10^{-10} \text{ J/m}^3$$

The ratio:

$$\frac{\rho_{\text{vacuum}}^{(QFT)}}{\rho_\Lambda} \sim 10^{122}$$

This is the cosmological constant problem. It's arguably the worst prediction in the history of physics.

Either we're calculating the vacuum energy wrong, or something cancels it to fantastic precision, or we're missing something fundamental about how gravity couples to vacuum energy.

### The Ratio Connection

Here's a hint about where we're going:

If dark energy and dark matter both trace to the same underlying physics—specifically, to the neutrino mass scale—then their ratio wouldn't be a coincidence.

The golden ratio φ emerges from optimal packing, minimal energy configurations, recursive self-organization. If the vacuum itself has φ-based structure, observable quantities might inherit φ-related ratios.

$$\phi^2 = 2.618...$$

$$\frac{\Omega_\Lambda}{\Omega_{DM}} = 2.58 \pm 0.02$$

The match isn't perfect. But it's close enough to be interesting.

### The Neutrino Mass Scale

We'll see later that the neutrino mass scale plays a special role. Neutrino masses are tiny—around 0.01-0.1 eV—but they're not zero. This scale, combined with the golden ratio and the Compton wavelength of the electron, seems to generate both:

1. The correct dark energy density
2. The correct dark matter density
3. Their ratio

If that sounds too good to be true, reserve judgment until you see the actual numbers.

### The Coincidence Problem Revisited

We mentioned that Ω_Λ and Ω_DM are comparable today. In standard cosmology, this is a 1-in-a-billion fine-tuning problem—we just happen to live at the exact cosmic epoch when they're similar.

But if they're related—if they come from the same physics—then perhaps we don't live at a special time. Perhaps the ratio is always of order unity for some deep reason.

### What's Coming

In subsequent parts, we'll:

1. **Part 6-10**: Develop the mathematical structure (continued fractions, φ-sequences, renormalization)
2. **Part 11-15**: Build the Edge of Chaos framework (self-organized criticality, φ as the critical coupling)
3. **Part 16-20**: Apply to the vacuum (predicting Λ, connecting to neutrino masses)
4. **Part 21-25**: Apply to dark matter (explaining Ω_DM)
5. **Part 26-28**: The full synthesis (explaining all three values and their relationships)

The payoff: not arbitrary parameters measured from observation, but values derived from first principles.

---

## Summary

### What We Covered

1. **The Expanding Universe**: Galaxies recede with v = H₀d. Not motion through space—space itself expanding. Scale factor a(t).

2. **The Big Bang**: Running expansion backward gives a hot dense initial state 13.8 billion years ago. Evidence from CMB, nucleosynthesis, expansion.

3. **Friedmann Equations**: (ȧ/a)² = 8πGρ/3 - k/a² + Λ/3 governs cosmic dynamics. Different components (radiation, matter, Λ) dominate at different epochs.

4. **Cosmic Contents**: Baryons ~5%, Dark matter ~27%, Dark energy ~68%. We don't know what 95% of the universe is.

5. **Dark Matter**: Evidence from rotation curves, lensing, CMB. We know it's there but not what it is. Behaves as w = 0 matter.

6. **Dark Energy**: Evidence from accelerating expansion (1998). Could be Λ (w = -1) or something else. Causes cosmic acceleration.

7. **Critical Density**: ρ_crit = 3H²/8πG. Ω = ρ/ρ_crit. Universe is flat: Ω_total ≈ 1.

8. **The Ratio**: Ω_Λ/Ω_DM ≈ 2.58. This is close to φ² ≈ 2.618. Unexplained in standard cosmology.

9. **What's Coming**: The 10¹²² problem, the near-φ² ratio, and the coincidence problem all point to missing physics. The Edge of Chaos framework will address all three.

### Key Numbers to Remember

| Quantity | Value | Significance |
|----------|-------|--------------|
| H₀ | ~70 km/s/Mpc | Current expansion rate |
| Age | 13.8 Gyr | Time since Big Bang |
| Ω_b | 0.049 | Baryon fraction |
| Ω_DM | 0.265 | Dark matter fraction |
| Ω_Λ | 0.685 | Dark energy fraction |
| Ω_Λ/Ω_DM | 2.58 | The ratio that matters |
| φ² | 2.618 | Close to the ratio |
| 10¹²² | - | The vacuum energy discrepancy |

### The Tension

Standard cosmology is incredibly successful. It fits the data beautifully. The ΛCDM model (Λ + Cold Dark Matter) is the "standard model of cosmology."

But it has free parameters we can't explain:
- Why this value of Λ?
- Why this dark matter density?
- Why is their ratio close to simple numbers?

These aren't questions standard cosmology can answer. The answer is: "We measured them."

Physics shouldn't just measure. Physics should explain.

---

## Looking Ahead

Next in Part 6, we'll develop the mathematical tools needed for the Edge of Chaos framework. We'll see how the golden ratio emerges from continued fractions, how recursive sequences generate φ, and why this particular number appears throughout mathematics and nature.

The connection to cosmology will come later. First, we need the math.

---

## Appendix: The Friedmann Equation Derivation (Sketch)

For those who want to see where the Friedmann equation comes from:

Start with a homogeneous, isotropic universe. The metric is:

$$ds^2 = -c^2 dt^2 + a(t)^2 \left[ \frac{dr^2}{1-kr^2} + r^2 d\Omega^2 \right]$$

This is the Friedmann-Lemaître-Robertson-Walker (FLRW) metric. Homogeneous = same everywhere. Isotropic = same in all directions.

Plug this into Einstein's field equations:

$$G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$$

The 00 component gives the Friedmann equation. The ii components give the acceleration equation:

$$\frac{\ddot{a}}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3P}{c^2}\right) + \frac{\Lambda}{3}$$

This tells us acceleration depends on ρ + 3P/c². For w = -1 (Λ), this combination is negative, giving positive acceleration.

Combining the two equations with energy conservation:

$$\dot{\rho} + 3H(\rho + P/c^2) = 0$$

We get the full dynamics of the expanding universe.

The Friedmann equation is exact for homogeneous, isotropic spacetimes. It's the foundation of physical cosmology.

---

*Next: Part 6 - Mathematical Foundations (Continued Fractions, Fibonacci Sequences, and the Golden Ratio)*
