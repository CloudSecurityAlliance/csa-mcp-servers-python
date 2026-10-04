# How other people run many MCP servers

**Status:** first pass, 2026-10-04. Complete enough to have changed the plan; not complete.

**The question:** CSA is about to put five MCP servers in one repository. Who else has done this,
what did they choose, and how old is the practice?

---

## Read in this order

| | |
|---|---|
| [`TIMELINE.md`](TIMELINE.md) | **Is this a new trend?** Dates, bounded by the protocol's own age. The headline finding is here |
| [`SURVEY.md`](SURVEY.md) | Who runs what, how it is laid out, what is shared, and the tool-count numbers |
| [`SOURCES.md`](SOURCES.md) | Every source with its date and a reliability tier — and why the tiers are not politeness |
| [`measure.py`](measure.py) | Re-derives every number. Needs an authenticated `gh`, takes ~20 seconds |

## Findings, tagged

`[measured]` — from a repository tree, an API response, or installed source.
`[reported]` — from a secondary source, not verified.
`[inferred]` — reasoning on top of measurement; the weakest tier here.

### On repository layout

- `[measured]` **Four of four** organisations running more than one MCP server keep them in one
  repository. No counter-example found: AWS (62 servers), Cloudflare (18), Microsoft (3 + Azure),
  the MCP project (7).
- `[measured]` **The monorepo was never a migration.** Cloudflare created its monorepo **two days
  after MCP was announced** — 8 days after the official `servers` repository existed. Nobody in this
  survey tried separate repositories and consolidated.
- `[measured]` **The pattern formed in a 36-day window**: GitHub 2025-03-04, AWS 2025-03-21,
  Microsoft 2025-04-09. That is 19 months before this survey.
- `[measured]` **The MCP project prunes as well as consolidates** —
  `modelcontextprotocol/servers-archived` was created *and archived* on 2025-05-28 to hold servers
  removed from the main tree.
- `[measured]` `microsoft/mcp` uses **`servers/` + `core/`** — independently the same shape and noun
  this repository restructured to.

### On what is actually shared

- `[measured]` **AWS shares no dependency resolution.** 62 servers, no root `pyproject.toml`, a
  `uv.lock` per server. What is shared is `.ruff.toml`, `.python-version`,
  `.pre-commit-config.yaml`, `.gitleaks.toml`, `trivy.yaml`, `DESIGN_GUIDELINES.md`,
  `DEVELOPER_GUIDE.md`.
- `[inferred]` At 62 servers one lockfile would mean one server's unsatisfiable dependency blocking
  all 62. No document states this; it is the obvious reading and it is still inference.
- `[measured]` **The official reference monorepo has no shared library at all** — seven
  self-contained servers, mixed TypeScript and Python in one tree.
- `[measured]` Cloudflare *does* share a workspace (pnpm + Turborepo) and ships
  `implementation-guides/`; its servers use *"a fresh SDK v2 server factory"* behind a common
  handler contract — a factory, not inheritance.

### On how many servers there should be

- `[measured]` This axis is **genuinely contested**, unlike layout. GitHub ships **one** server with
  `--toolsets` and `--dynamic-toolsets`, stating that it helps tool choice and *"reduce[s] the
  context size"*.
- `[reported]` Microsoft's Azure server covers 57 services in 276 tools. Not verified.
- `[measured]` CSA has **241 tool registrations** across four servers — skilljar 114, workspace 59,
  gmail-calendar 50, zendesk 18 — commonly all connected at once.
- `[measured]` Three of CSA's servers are the **same vendor** (Google), 109 tools across the two
  built, and they are the pair carrying the 58–60% OAuth duplication *because* of the split.

### On the protocol, where it bears on all this

- `[measured]` **RFC 7591 DCR is deprecated** as of `2026-07-28` — `MAY`, *"retained for backwards
  compatibility"*. Secondary sources still call it required.
- `[measured]` **A stdio transport SHOULD NOT use the authorization spec** and should take
  credentials from the environment. CSA reached this independently.
- `[measured]` Python SDK ships every **9.5 days**; TypeScript SDK every **1.9 days**. Both at
  v2.3.0 on 2026-10-02.

### On CSA itself — the finding that changes the migration

- `[measured]` **Four of CSA's six MCP repositories are under 40 days old.**
  `csa-google-workspace` ran alone for ~14 months, then three servers appeared within **seven
  days** in late August 2026.
- `[inferred]` So the measured drift did not accumulate over years — it appeared in a burst five
  weeks ago. The migration is correcting a month-old structural choice, not unwinding entrenched
  divergence, which makes it cheaper than the plan implies and cheapest right now.

## What changed in the plan because of this

| finding | consequence |
|---|---|
| Cloudflare splits servers from shared code | layout changed to `servers/` + `packages/` |
| AWS shares config, not a lockfile | **ADR-002 corrected**; ADR-006 added for root tooling config |
| Official monorepo has no shared library | supports ADR-001's narrow extraction bar |
| Official monorepo mixes languages | "one repo per language" reopened |
| GitHub's toolsets, and 241 CSA tools | new open question on Google server granularity |
| DCR deprecated | hosted design must not use it; now sourced, not asserted |
| stdio SHOULD NOT use OAuth | validates the existing credential design, normatively |

## What this does not cover

- **No private or internal fleet is visible**, which biases the survey toward organisations that
  publish.
- **No operational experience.** Every finding is about what was *chosen*, never whether it worked.
- **No stated reasoning.** None of these repositories contained a document explaining its monorepo
  decision, so every "why" here is inference.
- **AWS's 62 server directories were not individually inspected** — one may import a shared internal
  package that the root listing does not reveal.
- **Microsoft's `core/` was listed, not read.**
- **The TypeScript SDK was not examined**, only its release cadence.

## When to re-run

Re-run `measure.py` and re-read the specification pages in [`SOURCES.md`](SOURCES.md) when:

- a new protocol revision ships — the current one is `2026-07-28`;
- `ext-auth` moves (it has not since 2026-06-18, 108 days before this survey);
- before acting on the Google-granularity or lockfile questions, because both rest on numbers here.

`AS_OF` in `measure.py` is pinned to 2026-10-04 deliberately so a later run is comparable with this
document. Change it when writing a new survey, and say so.
