# csa-mcp-servers-python

A planned monorepo for Cloud Security Alliance's Python [Model Context
Protocol](https://modelcontextprotocol.io) servers, and for the small shared library extracted from
them.

> ## Status: plan only. No code has moved here yet.
>
> Every directory under `packages/` holds a `README.md` and nothing else. The five existing servers
> still live in their own repositories and are still the places to file issues and send pull
> requests. This repository currently exists to hold **the plan, the evidence behind it, and the
> reasoning** so both can be reviewed before anything is migrated.
>
> Created 2026-10-03.

## Why a monorepo

Four published servers already exist. They were built one after another, each learning from the
last, and they drifted — not in ways anyone chose, but in ways nobody could see, because comparing
four repositories means cloning four repositories.

The drift is measured, not asserted. See [`docs/EVIDENCE.md`](docs/EVIDENCE.md):

- `_markdown.py` is **96% identical** across two servers, 222 and 219 lines. It implements
  HTML→Markdown conversion, which a ratified decision mandates fleet-wide.
- Linting floors split two and two: `ruff>=0.6`/`mypy>=1.11` against `ruff>=0.16`/`mypy>=2.0`.
- `markdownify` is pinned `>=1.2` in one server and `>=0.13` in another — a major-version gap on a
  library every server is required to use.
- The optional dependency that installs the MCP server is called `[server]` in one repository and
  `[mcp]` in the other three. It is a user-facing name and it appears in error messages.

Co-location does not fix drift by itself. **One lockfile does**, by making the divergent state
unrepresentable rather than merely discouraged.

The second reason is that co-location is what makes extraction honest. A shared library should be
*extracted from* working servers, never designed *for* hypothetical ones — and you cannot extract
from evidence you cannot see side by side.

## What goes here

| package | what it is | state |
|---|---|---|
| [`csa-mcp`](packages/csa-mcp) | the shared library, extracted from the servers | does not exist yet |
| [`csa-zendesk`](packages/csa-zendesk) | Zendesk tickets, comments, attachments | published, lives elsewhere |
| [`csa-google-workspace`](packages/csa-google-workspace) | Docs, Sheets, Slides, Drive comments | published, lives elsewhere |
| [`csa-google-gmail-calendar`](packages/csa-google-gmail-calendar) | Gmail and Google Calendar | published, lives elsewhere |
| [`csa-skilljar`](packages/csa-skilljar) | Skilljar courses, learners, enrolment | published, lives elsewhere |
| [`csa-google-workspace-audit`](packages/csa-google-workspace-audit) | tenant-wide audit reads | specs only, never built |

Package names on PyPI do not change. Nothing that installs these servers today references a Git
URL — verified, all 44 references across the installer repositories are PyPI names — so moving the
code is invisible to anyone installing it.

## How to read this repository

Read in this order. Each document assumes the one before it.

| document | what it answers |
|---|---|
| [`docs/EVIDENCE.md`](docs/EVIDENCE.md) | What is actually duplicated, measured rather than guessed, with the method so it can be re-run |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | The four tiers, what belongs in each, and what must never be shared |
| [`docs/PROTOCOL.md`](docs/PROTOCOL.md) | Which protocol revision the servers speak, what `2026-07-28` changes, and links to the specification |
| [`docs/MIGRATION.md`](docs/MIGRATION.md) | The ordered steps, and the two that fail silently if skipped |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | The decisions this plan makes, each with its rejected alternatives |
| [`docs/REVIEW-BRIEF.md`](docs/REVIEW-BRIEF.md) | **Start here if you are reviewing this plan.** What to attack, and what is deliberately absent |

### The project's own files

The CINO core set, written from this project rather than from a template. Two of them produced
findings, which is why they are worth reading before trusting anything else here.

| document | what it answers |
|---|---|
| [`GOALS.md`](GOALS.md) | What *done* means — six properties, **four of them not met** and saying so |
| [`BUSINESS-CASE.md`](BUSINESS-CASE.md) | Why move four working servers; what the invisible drift already cost |
| [`OPERATIONAL-RESOURCES.md`](OPERATIONAL-RESOURCES.md) | Nothing is hosted, so the surface turned out **citational**: ~160 claims about four other repositories, four of them line-number-precise, and **nothing checks any of them** |
| [`BACKUP-RESOURCES.md`](BACKUP-RESOURCES.md) | The inversion — this is the only record of a 2026-10-03 measurement that cannot be re-derived later, and `main` is the one repository in the fleet with **no force-push protection** |
| [`SECURITY-RESOURCES.md`](SECURITY-RESOURCES.md) | What must never land in a public repository, and what is deliberately deferred to each server's own file |
| [`RACI.md`](RACI.md) | One name in every role, and what that costs |
| [`FRICTION.md`](FRICTION.md) | What cost time — including two of my own wrong premises that measurement caught before publication |
| [`WAITING-FOR.md`](WAITING-FOR.md) | Blockers with someone else's name on them |
| [`TODO.md`](TODO.md) | Index of all open work, one line per item |

There is deliberately **no `DECISIONS-ADR.md`** — [`docs/DECISIONS.md`](docs/DECISIONS.md) is the
decision log, and a second one is how two decisions end up disagreeing with neither marked as the
loser.

## Upstream

This fleet is built on the official Python SDK, not a wrapper around it.

- [Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [`mcp` on PyPI](https://pypi.org/project/mcp/)
- [Specification, revision `2026-07-28`](https://modelcontextprotocol.io/specification/2026-07-28) · [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) · [versioning policy](https://modelcontextprotocol.io/specification/versioning)
- [Specification repository](https://github.com/modelcontextprotocol/modelcontextprotocol) · [SEP process](https://modelcontextprotocol.io/community/sep-guidelines)

## Context

Engineering practice for this fleet is maintained in
[CINO-Platform-Engineering](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering)
(internal; links below will not resolve for everyone). The MCP-specific material lives under
`surfaces/mcp/` there — `LIFECYCLE.md` is the router, `ROADMAP.md` sets the order servers are built
in, `CONFORMANCE.md` is what every server owes, and `PROTOCOL-REVISIONS.md` tracks what each
protocol revision costs us.

## Licence

[Apache-2.0](LICENSE). Checked rather than assumed before proposing a monorepo, because packages
that share a repository have to agree: all four published servers already declare `Apache-2.0` in
`pyproject.toml` and ship a matching `LICENSE`. There is no conflict to resolve.

The one gap is `csa-google-workspace-audit`, which has **no licence at all** — it is specs only. It
needs one before it is built, not at migration time.
