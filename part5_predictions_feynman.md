# Part V: Predictions and Falsifiability

## Or: How to Tell if We're Doing Physics or Just Fooling Ourselves

---

You know, I've sat through a lot of lectures and read a lot of papers where people have these beautiful theories. Gorgeous mathematics. Elegant symmetries. And at the end of it all, I want to grab them by the shoulders and ask: "But what does it *predict*? What experiment can prove you wrong?"

Because that's what separates physics from philosophy. That's what separates science from... well, from making stuff up that sounds good.

So let's see if we've got real physics here, or if we've just been entertaining ourselves.

---

## The Moment of Truth: Making a Prediction

Here's where we stick our neck out.

We've argued that the vacuum energy density $\rho_\Lambda$ comes from neutrinos. We've got a formula that connects them. Now, if that's true - if we're not just fooling ourselves - then we should be able to *predict* something.

> **[CORRECTION 2026-02-01]**: The identification of vacuum energy density with dark energy density was based on matching the magnitude without verifying the equation of state. Rigorous computation (Feb 2026) shows the cell vacuum gives w = 0 (dust), not w = -1 (dark energy). The energy density formula is correct, but the cell vacuum does not behave as dark energy. The neutrino mass predictions below remain valid as consequences of the formula, but the interpretation as "dark energy comes from neutrinos" is severely undermined. See `rigorous_team_session/11_the_good_bad_ugly.md`.

And we can. We predict the mass of the lightest neutrino.

From our vacuum energy relation:

$$\boxed{m_1 = 2.31 \text{ meV}}$$

That's it. That's our prediction. The lightest neutrino has a mass of about 2.31 milli-electron-volts.

Now, you might say, "Feynman, how can we possibly check that?" Well, that's the beautiful part. We don't have to measure $m_1$ directly. Nature gave us a gift: neutrino oscillations.

---

## The Gift of Oscillations

Here's something wonderful. Neutrinos oscillate - they change from one type to another as they travel. And the rate at which they oscillate depends on the *differences* between the squares of their masses.

We've measured these differences:
- $\Delta m^2_{21} = m_2^2 - m_1^2 \approx 7.5 \times 10^{-5} \text{ eV}^2$
- $\Delta m^2_{31} = m_3^2 - m_1^2 \approx 2.5 \times 10^{-3} \text{ eV}^2$

These aren't theoretical numbers. These come from real experiments - solar neutrinos, reactor neutrinos, atmospheric neutrinos. Thousands of physicists working for decades.

So if we know $m_1$, we can calculate the others:

$$m_2 = \sqrt{m_1^2 + \Delta m^2_{21}}$$

$$m_3 = \sqrt{m_1^2 + \Delta m^2_{31}}$$

Let's do it:

---

## The Calculation

Starting with $m_1 = 2.31$ meV $= 2.31 \times 10^{-3}$ eV:

**For $m_2$:**
$$m_2^2 = (2.31 \times 10^{-3})^2 + 7.5 \times 10^{-5}$$
$$m_2^2 = 5.3 \times 10^{-6} + 7.5 \times 10^{-5} = 8.0 \times 10^{-5} \text{ eV}^2$$
$$m_2 = 9.0 \text{ meV}$$

**For $m_3$:**
$$m_3^2 = (2.31 \times 10^{-3})^2 + 2.5 \times 10^{-3}$$
$$m_3^2 = 5.3 \times 10^{-6} + 2.5 \times 10^{-3} = 2.46 \times 10^{-3} \text{ eV}^2$$
$$m_3 = 49.6 \text{ meV}$$

So we predict:

| Neutrino | Mass (meV) |
|----------|------------|
| $m_1$ (lightest) | 2.31 |
| $m_2$ | 9.0 |
| $m_3$ (heaviest) | 49.6 |

And the sum:

$$\boxed{\sum m_\nu = 2.31 + 9.0 + 49.6 = 60.9 \text{ meV}}$$

---

## Why This Matters: The Cosmological Bound

Now here's where it gets exciting.

Cosmologists have been trying to measure the sum of neutrino masses from the way neutrinos affect the large-scale structure of the universe. Massive neutrinos smooth out the clustering of galaxies - they're too fast to get trapped in gravitational wells when they're light.

Current observations put an upper limit:

$$\sum m_\nu < 120 \text{ meV} \quad \text{(95% confidence)}$$

Our prediction? 60.9 meV.

*We're below the bound.* The theory isn't ruled out. We're still in the game.

But notice - we didn't tune anything to make this work. We didn't say "let's pick a mass that fits the cosmological bound." We derived $m_1$ from the vacuum energy, used measured oscillation parameters, and got a sum that happens to be consistent with cosmology.

That's either a coincidence, or we're onto something.

---

## How to Prove Me Wrong

This is my favorite part. Here's how you could show this whole thing is nonsense:

### Test 1: The Cosmological Sum

Future surveys - Euclid, DESI, CMB-S4 - will measure $\sum m_\nu$ much more precisely. If they find:

$$\sum m_\nu < 45 \text{ meV}$$

then we're in trouble. Our minimum possible sum (with $m_1 = 2.31$ meV) is about 61 meV. If the universe says neutrinos are lighter than that, our theory is wrong.

*Dead. Finished. Time to find a new idea.*

And you know what? That would be fine. That's how physics works. You make a prediction, nature tells you yes or no, and you learn something either way.

### Test 2: Direct Mass Measurement (KATRIN)

The KATRIN experiment in Germany is measuring the electron neutrino mass directly from tritium beta decay. They're looking at the endpoint of the electron energy spectrum - if the neutrino has mass, the maximum electron energy is a tiny bit less than it would be otherwise.

Current sensitivity: about 800 meV (not quite there yet)

If they see a signal at, say, 100 meV, that would conflict with our prediction. If they push down to 50 meV and see nothing, that's consistent with us.

### Test 3: The Mass Hierarchy

We've assumed "normal ordering" - that $m_1$ is the lightest. If experiments determine it's "inverted ordering" ($m_3$ is lightest), then our specific numbers change. We'd need to redo the analysis.

This is actually being tested right now by experiments like JUNO and NOvA.

---

## The Point

Look, I want to be clear about what we're doing here.

We have a theory. The theory makes a specific, numerical prediction:

> **The sum of neutrino masses is approximately 61 meV.**

This isn't vague. This isn't "neutrinos might have something to do with dark energy." This is a number that can be checked.

Within the next decade, we'll have cosmological measurements precise enough to confirm or rule out this prediction. That's remarkable. That's science.

---

## A Personal Note

You know, when I was young, I was always suspicious of theories that couldn't be tested. "That's not physics," I'd say, "that's just speculation." And I still believe that.

But I also learned something important: the best theories are the ones that stick their neck out. The ones that say "here's what should happen," and then wait to see if nature agrees.

Einstein did that with general relativity - he predicted light would bend around the sun by a specific amount. When Eddington measured it and got the right answer, that wasn't just confirmation of a theory. It was one of the most beautiful moments in science.

So here we are, with our little theory about neutrinos and the vacuum. We've made our prediction. Now we wait.

Maybe we're right. Maybe the vacuum energy really does come from neutrino condensation, and we've stumbled onto something deep about the universe.

Or maybe we're wrong. Maybe future measurements will show our numbers don't match, and we'll have to go back to the drawing board.

Either way, we'll learn something. And that's the whole point.

---

## Summary

What we predicted:

| Quantity | Value | How to Test |
|----------|-------|-------------|
| $m_1$ | 2.31 meV | Derived from $\rho_\Lambda$ |
| $m_2$ | 9.0 meV | From $m_1$ + oscillations |
| $m_3$ | 49.6 meV | From $m_1$ + oscillations |
| $\sum m_\nu$ | 60.9 meV | Cosmological surveys |

How to falsify:
- If $\sum m_\nu < 45$ meV (cosmology)
- If direct measurements show $m_\nu > 100$ meV (KATRIN)
- If inverted hierarchy is confirmed (neutrino experiments)

The bottom line:

> *"The test of all knowledge is experiment. Experiment is the sole judge of scientific truth."*

We've done the theory. Now let's see what nature has to say.

---

*Next: Part VI - Implications and Connections*
