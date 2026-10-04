# How research is done here

**The standard, as of 2026-10-04.** Every topic under `research/` follows it.

> **Find the best practice, then measure what the big players actually do.**
> Those are two different findings and they disagree often enough that reporting only the first is
> misleading.

---

## The two halves, and why both

**Half one: what is the stated best practice?** From the primary source — a specification, an RFC,
a vendor's own documentation. Normative language (`MUST`, `SHOULD`, `MUST NOT`) carries weight; a
blog post asserting the same thing does not.

**Half two: what do the big players actually do?** Measured from what they ship — repository trees,
configuration files, installed packages, API responses. Not from their marketing, not from a
conference talk, and not from a catalogue site's description of their repository.

The gap between the halves is usually the most useful output. Three worked examples from this
repository's first two surveys:

| stated | actual | the finding |
|---|---|---|
| Secondary sources: remote MCP servers **must** implement RFC 7591 DCR | The specification **deprecates** DCR as of `2026-07-28` | the literature is a revision behind, and following it builds on a deprecated mechanism |
| A monorepo needs one workspace and one lockfile (this repo's own ADR-002) | AWS runs **62** Python MCP servers with **no workspace** and a `uv.lock` per server, sharing `.ruff.toml` instead | right problem, heavier instrument than needed — ADR-002 corrected, ADR-006 added |
| Vendors will add fine-grained per-agent permissions | Google's own Agent Gateway docs: *"creates a governance layer above SaaS APIs, though the underlying APIs still lack true per-agent granularity"* | the gap is structural, not a roadmap item |

None of those three would have been found by reading best-practice guidance alone.

## Who counts as a big player

For a question about running MCP servers: AWS (`awslabs/mcp`), Cloudflare
(`cloudflare/mcp-server-cloudflare`), Microsoft (`microsoft/mcp`), GitHub (`github/github-mcp-server`),
and the MCP project itself (`modelcontextprotocol/*`). For a question about enforcement, add the
hyperscalers' agent-governance products, because they are the ones who have had to answer it
commercially.

Pick by **what they have had to solve at scale**, not by brand. A company running 62 servers has
been forced into decisions that one running two has not.

## Source tiers

Used in every topic. The tiers are not politeness — tier 2 was wrong about a normative requirement.

| tier | what | may be used for |
|---|---|---|
| **1** | specifications, RFCs, repository trees via API, installed source, first-party vendor docs | anything, including a normative claim |
| **2** | blog posts, vendor marketing, conference write-ups, news | framing and finding the question only |
| **3** | MCP catalogue/aggregator sites, wiki-style summaries of repositories | **nothing** — not cited |

Where tier 1 and tier 2 disagree, tier 1 wins and **the disagreement is recorded**, because it tells
you how stale the literature is.

Where documentation and installed source disagree, **the source wins** — it is what actually runs.
That happened twice in the first survey.

## Tag every finding

`[measured]` — from a tree, an API response, or installed source. Reproducible.
`[reported]` — from a secondary source, not verified. Say so inline.
`[inferred]` — reasoning on top of measurement. The weakest tier, and the one most likely to be
read as fact.

Untagged, all three read as equally solid, and they are not.

## Date everything

A survey without a date is a claim about an unknown moment. For this ecosystem that is not
pedantry: the Python SDK ships a release every **9.5 days** and the TypeScript SDK every **1.9**,
so a six-month-old statement describes a different protocol.

Each topic states when it was measured, and `AS_OF` in any measurement script is **pinned** rather
than `date.today()`, so a later run is comparable with what was written.

## Publish the method and run it

Every number must be re-derivable by someone else. `research/fleet-survey/measure.py` is the
pattern: a script that reproduces the whole survey in about twenty seconds.

**Run it before writing the document, not after.** The first survey's script died on Windows with
a `cp1252` decode error part-way through a large response — which would have gone unnoticed if the
numbers had been collected by hand, and would have made the published method false.

## Say what you did not check

The cheapest way for a survey to mislead is to read as complete. Every topic ends with what it does
not establish. Recurring honest gaps worth stating explicitly:

- **Repository trees show *what*, never *why*.** None of the surveyed repositories contained a
  document explaining its monorepo choice. Every "presumably" is `[inferred]`.
- **Only public repositories are visible**, which biases toward organisations that publish.
- **Choice is not outcome.** Finding that four organisations chose a monorepo says nothing about
  whether it worked well for them.

## Grep is a measurement and can be wrong

Two findings in this repository's research were wrong on the first pass because a pattern was
narrower or broader than the property being tested:

- Searching for `ping` matched **117 files** — it is a substring of "mapping" and "shipping".
- Searching for the exact phrase `untrusted data` reported that `csa-zendesk` never mentions
  untrusted content. It mentions it in **seven files**, worded differently.

Both were caught by the result being implausible. **When a count surprises you, suspect the
pattern before the codebase**, and prefer a measurement whose failure is visible — a diff, a
similarity ratio, an API response — over a grep whose silence looks like an answer.

## What a finding carries

- its **date**
- its **tag** — measured, reported, inferred
- **what it did not establish**
- **its consequence, or the explicit absence of one.** A finding that changed nothing is still
  worth keeping. A finding presented as neutral that quietly drove a decision is not.
