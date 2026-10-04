# Adversarial review: disproving the 30-day rule

**Status:** 2026-10-04. Written to break the rule, not to defend it.

**The claim under test.** Carried over from cloud — *knowledge more than three years old was probably
wrong, not factually but because a better way existed by then* — and compressed for AI to three
months, then **thirty days**.

**Verdict: the number does not survive. The instinct does, and so does something better than a
number.** Four disproofs follow, in increasing order of how much damage they do.

---

## The name, first, because it already exists

The term is **half-life**, and in this sense it is 66 years old: **Burton and Kebler (1960)**,
in library and information science, who defined it as *"the time during which one-half of the
currently active literature was published."*

Their framing is more precise than the physics metaphor usually gets credit for, and it is exactly
the intuition behind the medieval-literature analogy:

> Burton and Kebler pointed out that literature becomes **obsolescent rather than disintegrating**,
> so that "half-life" means **"half the active life."**

That is the distinction. A 2022 finding about GPT-3.5's limitations has not become *false* — it is
still true about GPT-3.5. It has become **obsolescent**: the thing it describes is no longer
something anyone builds on, so the finding has left the active literature even though its truth
value never changed.

Related established vocabulary: **Gross and Gross (1927)** introduced *obsolescence* as the
phenomenon; **citation half-life** (or *cited half-life*) is the measured quantity, published
per-journal in Journal Citation Reports; **Line (1970)** decomposed it, arguing half-life is
*"obsolescence rate and the literature growth rate"* together — which matters below. Samuel
Arbesman's *The Half-Life of Facts* (2012) is the popular treatment.

**What does not appear to have a settled name** is the AI-specific case where the *substrate*
changed rather than the facts. "Half-life" describes the symptom; it does not name the mechanism.
If CSA wants a term, **substrate obsolescence** is the honest one: the claim remains true and its
object stopped mattering. Worth distinguishing from plain staleness, because the remedies differ —
a stale fact needs re-measuring, an obsolescent one needs the *question* re-asked.

## Disproof 1 — far too long for three layers

| layer | measured | a 30-day-old claim is |
|---|---|---|
| installed dependency version | `mcp` 2.3.0 shipped **the day before** review; `oauthlib` 4.0.0 five days before | ~3 Python releases stale, **~21 TypeScript releases** stale |
| TypeScript SDK | **1.4 days** in the last 90 days — up from 3.1 in the prior quarter | spans ~21 releases |
| frontier model identity | `[reported]` ~7 days in the last month: Fable 5.1 and Mythos 5.1 on Sep 1, Opus 5.5 on Sep 22, Sonnet 5.5 on Sep 28 | superseded ~4 times |

For these, 30 days is not conservative — it is a month of being confidently wrong.

`[inferred]` And this quantifies the medieval-literature point. GPT-3.5 shipped around November 2022,
roughly 1,430 days before this review. At the *current* frontier cadence that is on the order of
**70–200 model generations**. The problem with four-year-old AI research is not that four years is a
long time; it is that the substrate underneath it was replaced a hundred times over.

## Disproof 2 — far too short for two layers, and the gap is widening

**The protocol is decelerating.** Five revisions, verified individually:

| from → to | days |
|---|---|
| 2024-11-05 → 2025-03-26 | 141 |
| 2025-03-26 → 2025-06-18 | **84** |
| 2025-06-18 → 2025-11-25 | 160 |
| 2025-11-25 → 2026-07-28 | **245** |

Mean **158 days**. First two gaps average **112**; last two average **202**. The current revision is
**68 days old**. So the protocol is slowing as it matures, and a 30-day cycle means re-reading the
specification roughly **five times per revision, four of which find nothing** — a ratio that is
getting worse, not better.

**Architectural patterns are slower still.** Monorepo-for-fleets settled inside a **36-day window in
spring 2025** — GitHub 2025-03-04, AWS 2025-03-21, Microsoft 2025-04-09 — and has not moved in the
19 months since, at 4-of-4 adoption. A monthly review of that decision is pure waste.

## Disproof 3 — the structural one, which breaks the model rather than tuning it

A half-life assumes **memoryless exponential decay**: constant hazard per unit time, independent of
age. That is the defining property of radioactive decay, and it is false here in two different ways.

**It is event-driven, not continuous.** Between protocol revisions the hazard is approximately
**zero**. On revision day an entire cluster invalidates simultaneously — on 2026-07-28, protocol
sessions, `initialize`, `elicitationId`, `notifications/elicitation/complete`, Roots, Sampling and
Logging all died together. The hazard function is spiky, and a half-life fitted to it is an average
of nothing-happening and everything-happening. It describes neither state.

**For architecture the correlation inverts — the Lindy effect.** For non-perishable things, survival
is evidence of durability: the monorepo pattern is **more** trustworthy at 19 months than it was at
one month, because it has now survived two protocol revisions and four independent adoptions. **Age
increases confidence.** No half-life constant can describe a quantity whose reliability rises with
age, because that is the opposite of decay.

`[inferred]` So the two phenomena coexist in one stack: **half-life is the right model for
perishable implementation facts and the wrong model for architectural patterns.** Any single number
must therefore be wrong for at least one of them — not mis-tuned, but categorically misapplied.

## Disproof 4 — the rule over-corrects, per Line (1970)

Half-life is *obsolescence rate plus literature growth rate*. AI's apparent short half-life is
substantially the second term: the literature is exploding, not merely rotting.

`[inferred]` A 30-day rule cannot tell those apart, so it discards still-valid older findings
because newer ones arrived. That is **recency bias**, a different failure from the staleness the
rule exists to prevent, and arguably a worse one — staleness is visible when it bites, whereas
discarding a sound three-year-old result leaves no trace.

The session that produced this review contains an example of the sound-old-result category: the
`2026-07-28` specification's instruction that a stdio transport **SHOULD NOT** use OAuth validates a
CSA credential design reached independently and much earlier. A 30-day lens has nothing to say about
why that held.

## What survives

**Not the number.** What survives is sharper than it was:

1. **Per-layer, and per-*direction*.** Three of our layers trend differently — the protocol is
   decelerating, the Python SDK is flat at 8–12 days, the TypeScript SDK is accelerating and has
   roughly doubled in a quarter. A single constant cannot track quantities moving in opposite
   directions.
2. **Triggers beat intervals.** Because decay is event-driven, *"re-check when a revision ships"*
   strictly dominates *"re-check every N days"* — it fires exactly when the hazard does, and never
   when it doesn't. Every claim should carry a trigger, not a date.
3. **Lindy for architecture.** Treat age as evidence **for** an architectural pattern and
   **against** an implementation detail. The same month of elapsed time means opposite things at the
   two ends of the stack.
4. **The instinct was right about the layers that actually bit us.** Thirty days is close to the
   measured cadence for vendor capability (~30), our own repository state (~30, with 4 of 6 repos
   under 40 days old), and frontier model identity (faster). Those are precisely where this session
   made errors. The rule was over-generalised from a correct observation.

### The revised rule

> **Half-life by layer, Lindy for architecture, and a trigger instead of a timer.**
>
> For anything you will act on, record what event would invalidate it — not when you will look
> again.

## What this review did not establish

- **The model-cadence figures are `[reported]`**, from secondary sources, and by this document's own
  standard that makes them the weakest evidence here. Verifying against Anthropic's own release
  notes would settle it and was not done.
- **The TypeScript SDK's oldest bucket is a measurement artifact.** A 180–365-day window containing
  only four days of actual release history produced a nonsense rate; it is excluded above rather
  than reported. The last two quarters are sound.
- **No half-life was computed in the bibliometric sense.** Burton–Kebler half-life is derived from
  citation-age distributions; everything here is release-interval arithmetic, which is a proxy.
- **Lindy is asserted, not fitted.** 19 months and four adoptions is suggestive, not a survival
  curve.
- **"Substrate obsolescence" is a proposed term, not a found one.** A targeted literature search
  might turn up an existing name; one general search did not.
