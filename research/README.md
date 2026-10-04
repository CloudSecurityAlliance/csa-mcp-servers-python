# Research

Working material: surveys, measurements and notes that the documents in
[`../docs/`](../docs/) are built on.

**The split.** `docs/` holds decisions and plans — what we will do and why. `research/` holds the
evidence those rest on, including the parts that did not make it into a conclusion. Research stays
here after a decision is made, as the backing material the decision can be checked against.

---

## Current topics

**The method is [`METHOD.md`](METHOD.md), and it is the standard for every topic here:** find the
stated best practice, then measure what the big players actually ship. The gap between the two is
usually the finding.

| topic | question | status | last measured |
|---|---|---|---|
| [`fleet-survey/`](fleet-survey/) | How do other organisations run many MCP servers, and how old is the practice? | first pass — changed the plan in four places | **2026-10-04** |
| [`enforcement/`](enforcement/) | Vendors have no per-agent IAM, so where does policy actually get enforced — and is local policy real? | first pass — reversed one earlier decision | **2026-10-04** |
| [`orchestration/`](orchestration/) | Many endpoints or one mega-server? Progressive disclosure, identity-keyed tool lists, and whether this is the web's consolidation again | first pass — confirmed a `cacheScope` correctness requirement | **2026-10-04** |
| [`managed-agents/`](managed-agents/) | Can the Anthropic platform even use these servers? Reconciliation of an external research synthesis against primary sources | first pass — **found that none of the five stdio servers can attach** | **2026-10-04** |

## How research here is written

[`METHOD.md`](METHOD.md) is the full standard. The short version, all of it learned the hard way
during the first two surveys.

**0. Find the best practice, then measure what the big players actually do.** Two different
findings. Reporting only the first is how you end up recommending RFC 7591 Dynamic Client
Registration four months after the specification deprecated it.

**1. Date everything, and say what the date means.** A survey without a date is a claim about an
unknown moment. The Python SDK ships a release every 9.5 days and the TypeScript SDK every 1.9 —
a six-month-old statement about this ecosystem describes a different one.

**2. Tag each finding by how it was obtained.** `[measured]` from a repository tree, API response or
installed source. `[reported]` from a secondary source, unverified. `[inferred]` reasoning on top of
measurement. The tags exist because the three get read as equally solid otherwise, and they are not.

**3. Publish the method, and run it.** Every number in `fleet-survey/` is reproduced by
[`fleet-survey/measure.py`](fleet-survey/measure.py). It is run before the document is written, not
after — the first survey's script failed on Windows with a `cp1252` decode error part-way through,
which would have gone unnoticed if the numbers had been collected by hand.

### And one about sources specifically

**Primary for anything you will act on; secondary for framing only.** This is not fastidiousness.
The first survey found secondary sources unanimously stating that remote MCP servers must implement
RFC 7591 Dynamic Client Registration — which the current specification **deprecates**. Anyone
following that consensus would build on a deprecated mechanism. Aggregator and catalogue sites are
not cited at all; one of them described Cloudflare's monorepo accurately but omitted the three
details that turned out to matter.

See [`fleet-survey/SOURCES.md`](fleet-survey/SOURCES.md) for the tiering applied in practice.

## What a finding here has to carry

- **Its date.**
- **Its tag** — measured, reported, or inferred.
- **What it did not establish.** The cheapest way for a survey to mislead is to read as complete.
- **Its consequence, or the absence of one.** A finding that changed nothing is still worth keeping;
  a finding presented as neutral that quietly drove a decision is not.

## Graduation

A research topic becomes a document in [`../docs/`](../docs/) when it is settled enough to decide
from, and the research directory **stays** as backing material rather than being deleted. The
decision cites the research; the research is the evidence.

`fleet-survey/` has already graduated in part — it produced
[`../docs/PRIOR-ART.md`](../docs/PRIOR-ART.md), a correction appended to ADR-002, and ADR-006 — and
it remains open, because two questions it raised are not answered: whether there should be one
`uv.lock` or five, and whether three Google servers should be one.
