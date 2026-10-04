# Business case

**The question this answers:** why spend time moving four working servers, and what does not
happening cost?

The framing matters: this is a capability question that has already been answered, so the
remaining question is *should we*, not *can we*. The measurement is done, the migration path is
mapped, and both are in this repository. What is left is a decision.

## What the current arrangement costs

Four repositories drifted in ways nobody chose, and the drift was **invisible** rather than
tolerated. One session of measurement found:

- `markdownify` pinned `>=1.2` in one server and `>=0.13` in another - a **major-version gap on a
  library DEC-018 mandates fleet-wide**. Neither repository could see the other.
- Linting floors split two and two: `ruff>=0.6`/`mypy>=1.11` against `>=0.16`/`>=2.0`.
- A user-facing extra named `[server]` in one of four, appearing in error messages.
- Four different shapes for the decision log, in four servers.
- `_markdown.py` duplicated at 96%, which was *known and tracked* - and the fifth server would
  have copied it again.

None of these were caused by negligence. They were caused by comparison being expensive: it meant
cloning four repositories and diffing by hand. Nobody does that monthly.

### And the drift is five weeks old, not five years

The most consequential number the survey produced is about CSA rather than anyone else. Measured
2026-10-04: **four of six CSA MCP repositories are under 40 days old.**
`csa-google-workspace` ran alone for roughly fourteen months (created 2025-05-27), and then **three
servers appeared within seven days** of each other in late August 2026.

So this divergence did not accumulate slowly — it appeared in a burst, when three repositories were
created in a week and each made its own defaults. That changes the character of the work: the
migration corrects a structural choice made last month, before which there was only one server and
therefore no choice to make.

It also dates the opportunity. The cost of consolidating rises with every week those four
repositories accumulate commits, issues and external references — 2,982 bare issue references
already. This is near its cheapest now. See
[`research/fleet-survey/TIMELINE.md`](research/fleet-survey/TIMELINE.md).

## What the change buys

**One lockfile makes the divergent state unrepresentable** rather than merely discouraged. That is
the whole argument, and it is a structural fix rather than a process one - it does not depend on
anyone remembering.

Second: co-location is what makes extraction honest. [`docs/EVIDENCE.md`](docs/EVIDENCE.md) exists
because four trees could be compared in one command. Without that, deciding what a shared library
should contain means reasoning about what *ought* to be common, which is how frameworks nobody
wants get built.

## What it costs

Measured rather than feared, which changed the answer twice:

- **Nothing installs these from Git.** All 44 references in the installer repositories are PyPI
  names, so a repository move is invisible to anyone installing a server.
- **The licences already agree** - Apache-2.0, four of four.
- ~2,982 bare issue references need qualifying first, scripted.
- Four Trusted Publishers need reconfiguring.
- 79 issues transfer once, irreversibly, last.

Steps one through six of [`docs/MIGRATION.md`](docs/MIGRATION.md) are reversible. The commitment
point is step seven, and nothing before it needs to be right first time.

## The option not taken

Separate repositories plus a shared library on PyPI is the conventional answer, and it fails the
actual problem: it addresses *code* duplication while leaving *configuration* drift untouched -
which is where the measured divergence is. A shared library does not unify `ruff` floors.
