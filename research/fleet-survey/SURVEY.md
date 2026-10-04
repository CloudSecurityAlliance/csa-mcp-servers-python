# The survey: who runs many MCP servers, and how

Measured **2026-10-04** from repository trees via the GitHub API. Not from catalogue sites, not from
blog posts — see [`SOURCES.md`](SOURCES.md) for why that distinction turned out to matter.

Re-run with [`measure.py`](measure.py).

---

## Structure

| organisation | repository | layout | servers | shared code | dependency resolution | language |
|---|---|---|---|---|---|---|
| **AWS** | [`awslabs/mcp`](https://github.com/awslabs/mcp) | `src/` | **62** | none found | **one `uv.lock` per server**; no root `pyproject.toml` | Python |
| **Cloudflare** | [`cloudflare/mcp-server-cloudflare`](https://github.com/cloudflare/mcp-server-cloudflare) | `apps/` + `packages/` | 18 apps, 6 packages | yes, `packages/` | pnpm workspace + Turborepo | TypeScript |
| **Microsoft** | [`microsoft/mcp`](https://github.com/microsoft/mcp) | **`servers/` + `core/`** | 3 in-repo + the Azure server | yes, `core/` | not established | C# |
| **MCP project** | [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) | `src/` | 7 | **none** | per-package | TS + Python |
| **GitHub** | [`github/github-mcp-server`](https://github.com/github/github-mcp-server) | single server | **1** | n/a | n/a | Go |
| CSA today | four separate repositories | — | 4 | none | four independent | Python |

**Four of four organisations with more than one MCP server keep them in one repository.** No
counter-example was found. See [`TIMELINE.md`](TIMELINE.md) for the finding that this was never a
migration from anything.

## Reach, as a proxy for how much scrutiny each has had

| repository | stars | last push | created |
|---|---|---|---|
| `modelcontextprotocol/servers` | 90,989 | 2026-10-04 | 2024-11-19 |
| `github/github-mcp-server` | 33,350 | 2026-10-03 | 2025-03-04 |
| `modelcontextprotocol/python-sdk` | 24,475 | 2026-10-02 | 2024-09-24 |
| `modelcontextprotocol/typescript-sdk` | 13,509 | 2026-10-02 | 2024-09-24 |
| `awslabs/mcp` | 9,750 | 2026-10-04 | 2025-03-21 |
| `modelcontextprotocol/modelcontextprotocol` | 9,376 | 2026-10-03 | 2024-09-24 |
| `cloudflare/mcp-server-cloudflare` | 4,352 | 2026-10-01 | 2024-11-27 |
| `microsoft/mcp` | 3,727 | 2026-10-03 | 2025-04-09 |
| `modelcontextprotocol/ext-auth` | 164 | **2026-06-18** | 2025-10-01 |

Every repository except `ext-auth` was pushed within three days of this survey. `ext-auth` has not
moved in **108 days**, which is a caveat on treating its contents as the current state of
authorization extensions.

## What AWS shares, at 62 servers

The most informative single data point, because it is the largest Python MCP fleet in existence and
it does **not** do what this plan originally proposed.

There is no root `pyproject.toml` and no workspace. Each server under `src/` carries its own
`pyproject.toml` **and its own `uv.lock`**. A representative server directory
(`src/dynamodb-mcp-server/`):

```
.gitignore  .python-version  AGENTS.md  CHANGELOG.md  Dockerfile
LICENSE  NOTICE  README.md  awslabs/  docker-healthcheck.sh
pyproject.toml  tests/  uv-requirements.txt  uv.lock
```

What is shared sits at the repository root, and it is **tooling and writing, not resolution**:

```
.ruff.toml                 one lint configuration for 62 servers
.python-version            one interpreter version
.pre-commit-config.yaml    one hook set
.gitleaks.toml             secret scanning
.secrets.baseline
trivy.yaml                 vulnerability scanning
DESIGN_GUIDELINES.md       the convention tier, written down
DEVELOPER_GUIDE.md
CONTRIBUTING.md
VIBE_CODING_TIPS_TRICKS.md
```

Note `AGENTS.md` **per server** and `DESIGN_GUIDELINES.md` at the root — the convention tier exists
as documentation in the largest fleet, which is the independent support for ADR-004.

At 62 servers a single lockfile would mean one server's unsatisfiable dependency blocking all 62.
That is presumably the reason, though no document was found stating it — see *What this does not
establish*.

## What Cloudflare shares

`apps/` (18) and `packages/` (6) are separate top-level directories, with `pnpm-workspace.yaml`,
`turbo.json` and a root `tsconfig.json` — so a genuine shared workspace, unlike AWS.

Also present: `implementation-guides/`, described as documentation for developers, and
`.changeset/` for changelog management.

The README states that *"Every server in this repository exposes the same stateless Streamable HTTP
handler at `/mcp`"* and that each uses *"a fresh SDK v2 server factory"* — a shared contract
realised as a **factory per server** rather than inheritance.

## What Microsoft shares

Root directories: `servers/` (3), **`core/`**, `eng/`, `tools/`, `docs/`, `Resources/`,
`.devcontainer/`.

`servers/` plus `core/` is the same shape and the same noun this repository restructured to, arrived
at independently. Beyond the directory listing, Microsoft's internals were not examined.

Separately, the Azure MCP Server reportedly covers **57 Azure services through 276 tools** — a
secondary-source figure, not verified here, and flagged as such in [`SOURCES.md`](SOURCES.md).

## Server granularity: the axis that is genuinely contested

Repository layout is settled. **How many servers there should be is not.**

| approach | who | shape |
|---|---|---|
| one server per service | AWS (62), Cloudflare (18) | fine-grained |
| **one server, many toolsets** | GitHub | `--toolsets` to enable groups, `--dynamic-toolsets` for runtime discovery |
| one giant plus specialists | Microsoft | Azure server covering 57 services, plus ~a dozen specialised |

GitHub's stated reason is the model, not packaging: enabling only needed toolsets *"can help the LLM
with tool choice and reduce the context size"*, and dynamic discovery exists to avoid *"situations
where the model gets confused by the sheer number of tools available."*

### CSA's own numbers, for comparison

Tool registrations counted from source, 2026-10-04:

| server | tools |
|---|---|
| `csa-skilljar` | **114** |
| `csa-google-workspace` | 59 |
| `csa-google-gmail-calendar` | 50 |
| `csa-zendesk` | 18 |
| **total** | **241** |

All four are commonly connected simultaneously — they are, in the session that produced this
survey — so 241 CSA tools can occupy one client's context before any third-party server is added.
`csa-skilljar` alone at 114 exceeds the whole surface of many published fleets.

Three of those servers are **the same vendor**: `csa-google-workspace` (59),
`csa-google-gmail-calendar` (50) and `csa-google-workspace-audit` (planned). 109 tools across two
built servers, and they are the pair sharing the 58–60% OAuth trio *because* of the split.

The counter-argument against consolidating them is CSA's own and it is not weak: one Google
application per server is one revocable credential carrying the narrowest scope set it needs.
Merging means a single OAuth client holding the union of Docs, Sheets, Slides, Drive, Gmail,
Calendar and tenant-audit scopes, and one consent screen asking for all of it. **Context pressure
against credential blast radius**, undecided.

## What this does not establish

- **Why** anyone chose what they chose. Trees show structure; none of these repositories contained a
  document explaining the monorepo decision or AWS's per-server lockfiles. Every "presumably" above
  is inference.
- **Whether AWS has a shared runtime library.** No shared package was found at the root, but 62
  server directories were not individually inspected — one may import a common internal package.
- **Microsoft's `core/` contents.** Listed, not read.
- **The 276-tool Azure figure.** Secondary source, unverified.
- **Any private or internal fleet.** Only public repositories are visible here, which biases the
  survey toward organisations that publish.
- **Operational experience.** Nothing here says whether a monorepo worked well, only that it was
  chosen.
