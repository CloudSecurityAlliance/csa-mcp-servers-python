# Prior art

**The question this answers:** how does anyone else run more than one MCP server, and what does that
say about the choices in [`ARCHITECTURE.md`](ARCHITECTURE.md)?

Researched **2026-10-04**. Primary sources where the claim is load-bearing — a repository's own tree
rather than a catalogue's description of it, and the specification rather than a blog post about the
specification. Where the two disagreed, and they did, the disagreement is recorded below because it
is the most useful finding here.

---

## 0. The survey

Measured at source 2026-10-04 — repository trees via the GitHub API, not catalogue descriptions.

| organisation | repository | layout | servers | shared code | dependency resolution |
|---|---|---|---|---|---|
| **AWS** | [`awslabs/mcp`](https://github.com/awslabs/mcp) | `src/` | **62** | none | **one `uv.lock` per server**; no root `pyproject.toml` |
| **Cloudflare** | [`cloudflare/mcp-server-cloudflare`](https://github.com/cloudflare/mcp-server-cloudflare) | `apps/` + `packages/` | 18 apps, 6 shared packages | yes | pnpm workspace + Turborepo |
| **Microsoft** | [`microsoft/mcp`](https://github.com/microsoft/mcp) | **`servers/` + `core/`** | 3 in-repo, plus the Azure server | **yes — `core/`** | not established |
| **MCP project** | [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) | `src/` | 7 | **none** | per-package |
| **GitHub** | [`github/github-mcp-server`](https://github.com/github/github-mcp-server) | single server | **1** | n/a | n/a |
| CSA today | four separate repositories | — | 4 | none | four independent |

### The hypothesis holds: separate repositories per server is over

**Four of four** organisations running more than one MCP server use a single repository. There is no
counter-example in the survey — nobody with a fleet keeps it in separate repositories. CSA is
currently the outlier.

The MCP project also went further than consolidating: `modelcontextprotocol/servers-archived` exists
as an **archived** repository holding servers moved *out* of the main tree. So the direction is
consolidate-and-prune, not merely consolidate.

### But the monorepo they use is not the one this plan described

This is the part that corrects ADR-002, and it is the most useful finding in the survey.

**AWS runs 62 Python MCP servers with no workspace at all.** There is no root `pyproject.toml`.
Every server under `src/` carries its own `pyproject.toml` **and its own `uv.lock`**. Dependency
resolution is deliberately *not* shared.

What AWS shares at the repository root is tooling and writing:

```
.ruff.toml                 one lint configuration for 62 servers
.python-version            one interpreter version
.pre-commit-config.yaml    one hook set
.gitleaks.toml             one secret-scanning baseline
.secrets.baseline
trivy.yaml                 one vulnerability-scanning config
DESIGN_GUIDELINES.md       the convention tier, written down
DEVELOPER_GUIDE.md
```

And that is the direct answer to the drift this repository was created to fix. The divergence
measured in [`EVIDENCE.md`](EVIDENCE.md) and [`MIGRATION.md`](MIGRATION.md) — `ruff>=0.6` against
`>=0.16`, `mypy>=1.11` against `>=2.0` — is **tool configuration drift**, and a root `.ruff.toml`
fixes it directly. A shared lockfile is a different and much heavier instrument that happens to
also constrain it.

At 62 servers, one lockfile would mean one server's unsatisfiable dependency blocking all 62 — which
is presumably why the largest Python MCP fleet in existence does not have one. CSA has five servers,
so the coupling is far more tractable, but **it is a choice with a cost, not the obvious fix.** See
the correction appended to ADR-002.

### Microsoft independently validates the directory naming

`microsoft/mcp` has `servers/` and `core/` at its root — servers alongside a shared core. That is
the same shape this repository restructured to on the strength of Cloudflare's `apps/`+`packages/`
split, with the same noun. Two large organisations, same conclusion, arrived at separately.

C#, 3,727 stars, pushed the day before this survey — actively developed, not a reference artifact.

## 1. Cloudflare — the closest analogue, and it splits apps from packages

[`cloudflare/mcp-server-cloudflare`](https://github.com/cloudflare/mcp-server-cloudflare) is a
monorepo of Cloudflare-maintained MCP servers. Read directly, its top level is:

```
apps/        the servers — 15 visible, including workers-bindings, workers-builds,
             workers-observability, browser-rendering, logpush, ai-gateway, autorag,
             radar, cloudflare-one-casb, dns-analytics, sandbox-container, docs-ai-search
packages/    shared code and utilities
implementation-guides/   documentation for developers
```

with `pnpm-workspace.yaml`, `turbo.json`, and a root `tsconfig.json`.

Three things follow, and two of them are corrections to this plan.

**They separate servers from shared code at the top level.** `apps/` and `packages/` are different
directories. This repository currently puts everything — five servers *and* the shared library —
under one `packages/`. Cloudflare's split makes "is this a server or something servers share?"
structural rather than conventional. **That is a better layout than ours and we should adopt it.**

**They ship an `implementation-guides/` directory.** Documentation for developers building servers
in the repo — which is, structurally, exactly the tier-3 "convention, not code" argument in
[`ARCHITECTURE.md`](ARCHITECTURE.md), independently arrived at by a much larger team. Strong
corroboration for ADR-004.

**They standardise a handler shape, not a base class.** The README states that *"Every server in
this repository exposes the same stateless Streamable HTTP handler at `/mcp`"* and that each uses
*"a fresh SDK v2 server factory"*. A factory per server, with a shared contract — not inheritance.
This is the same conclusion our 10–15% similarity measurement pushed toward, reached from the
opposite direction.

Note the word **stateless**, consistent with revision `2026-07-28` removing sessions.

## 2. The official reference monorepo deliberately has no shared library

[`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) holds the
reference implementations — Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time —
under `src/`, and read directly:

- **Each server is self-contained.** They follow SDK patterns rather than importing a common
  in-repo library.
- **Languages are mixed in one repository.** TypeScript servers publish to npm
  (`@modelcontextprotocol/server-memory`), Python servers to PyPI, from the same monorepo.
- **Publishing is "OIDC trusted publishing from CI — no registry tokens."**

Two consequences for us.

A monorepo **without** a shared library is a legitimate design at scale, chosen by the people who
wrote the protocol. That is the strongest available support for ADR-001's narrow bar — ≥95%
duplication or no incumbent — and for keeping `csa-mcp` at roughly 300 lines. It also means the
burden of proof sits on anyone wanting to grow it.

And **the reference project does not separate by language.** An earlier idea here was a sibling
`csa-mcp-servers-typescript` monorepo; the official project puts both in one tree and lets the
publish target differ per package. That does not settle it — our TypeScript servers are Workers-
deployed rather than npm-published, which is a real difference — but "one repo per language" is not
the obvious answer it looked like. See [`ESTATE.md`](ESTATE.md).

## 3. The published landscape advice is a revision behind, and it matters

Searching for enterprise multi-tenant MCP patterns returns a consistent 2026 consensus: an **MCP
gateway** in front of many servers for token validation, scope-based routing and unified audit;
per-tenant token isolation; cryptographically scoped URLs; least privilege enforced server-side.
Useful framing, and the gateway pattern is worth considering for a hosted CSA fleet.

But the same sources state that remote servers must implement **RFC 7591 Dynamic Client
Registration**, citing spec revision `2025-11-25`.

**Checked against the primary source, that is now wrong.** Revision `2026-07-28`'s authorization
specification says:

> Authorization servers and MCP clients **SHOULD** support OAuth Client ID Metadata Documents […]
> Authorization servers and MCP clients **MAY** support the OAuth 2.0 Dynamic Client Registration
> Protocol (RFC7591). Note that Dynamic Client Registration is **deprecated and retained for
> backwards compatibility** with authorization servers that do not support Client ID Metadata
> Documents.

So DCR has moved from required to deprecated-but-tolerated, and Client ID Metadata Documents are the
`SHOULD`. **Anyone following current blog guidance would build a hosted fleet on a deprecated
mechanism.** This is why [`ARCHITECTURE.md`](ARCHITECTURE.md) says do not build on DCR, and it is
now sourced rather than asserted.

The general lesson, and it is the reason this document exists: secondary sources about a
fast-moving specification lag it by about one revision, and they do not say so.

## 4. The specification independently validates our stdio credential design

The most valuable single sentence found. From
[`2026-07-28` authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization):

> Implementations using an STDIO transport **SHOULD NOT** follow this specification, and instead
> retrieve credentials from the environment.

All five servers here are stdio. CSA arrived at exactly this independently — a stdio server must be
unable to reach an interactive OAuth flow and takes its credential from the environment, with its
own `authenticate` tool rather than the client's sign-in. That is now a **normative** position in
the specification rather than a local convention, which materially strengthens it.

### Other normative points worth having in hand before the hosted phase

| requirement | level |
|---|---|
| MCP server implements RFC 9728 Protected Resource Metadata | **MUST** |
| Client sends RFC 8707 `resource` in authorization *and* token requests | **MUST** |
| Server validates the token's audience is itself | **MUST** |
| Server **MUST NOT** accept or transit any other tokens — no passthrough to upstream APIs | **MUST NOT** |
| Client validates RFC 9207 `iss` before using the authorization code | **MUST** |
| AS includes `iss` | **SHOULD**, expected to become **MUST** |
| Authorization overall | **OPTIONAL** |

The passthrough prohibition is the one to design around: a hosted CSA server cannot forward a
client's token to Google or Zendesk. It must hold its own upstream credential, which is a tenancy
and custody problem rather than a plumbing one.

## 5. The axis this plan never considered: how many servers should there be?

Repository layout is one question. **Server granularity is a different one, and the survey is
split on it in a way that matters for CSA.**

| approach | who | shape |
|---|---|---|
| one server per service | AWS (62), Cloudflare (18) | fine-grained, many servers |
| **one server, many toolsets** | **GitHub** | a single server with `--toolsets` to enable groups, and `--dynamic-toolsets` for runtime discovery |
| one giant plus specialists | **Microsoft** | the Azure MCP Server covers **57 services through 276 tools**, with about a dozen specialised servers beside it |

GitHub's stated reason for toolsets is not packaging. It is the model:

> Enabling only the toolsets that you need can help the LLM with tool choice and reduce the context
> size.

and dynamic discovery exists to avoid *"situations where the model gets confused by the sheer number
of tools available."*

### What that means here, measured

Tool registrations per CSA server, counted 2026-10-04:

| server | tools |
|---|---|
| `csa-skilljar` | **114** |
| `csa-google-workspace` | 59 |
| `csa-google-gmail-calendar` | 50 |
| `csa-zendesk` | 18 |
| **total** | **241** |

All four are commonly connected at once, so **241 CSA tools can be in one client's context
simultaneously** — before any non-CSA server is added. That is the condition GitHub built dynamic
toolsets for, and `csa-skilljar` alone at 114 is larger than many whole fleets.

### And it raises a question about the Google servers specifically

CSA has **three** Google servers — `csa-google-workspace` (59 tools), `csa-google-gmail-calendar`
(50), and `csa-google-workspace-audit` (planned). One vendor, three servers, 109 tools already.
They are also the three that share the 58–60% OAuth trio, *because* they are the same vendor split
across servers. On the GitHub or Microsoft model this would be one Google server with toolsets.

**There is a real counter-argument and it is CSA's own:** one Google app per server means one
revocable application with the narrowest scope set it needs. Merging them means a single OAuth
client holding the union of Docs, Sheets, Slides, Drive, Gmail, Calendar **and** tenant-audit
scopes — a much larger blast radius if that one credential leaks, and a single consent screen asking
for everything.

So it is a genuine trade-off between **context pressure and credential blast radius**, not an
oversight to be corrected. It is not decided here, and it is listed in
[`REVIEW-BRIEF.md`](REVIEW-BRIEF.md).

Worth noting that CSA already has the *mechanism* for toolsets without the name: a capability the
deployment has not enabled **does not appear as a tool at all**. What is missing is per-session
selection and runtime discovery, not the gating.

## 6. Two authorization extensions exist, and one is directly ours

[`modelcontextprotocol/ext-auth`](https://github.com/modelcontextprotocol/ext-auth) lists:

- **Enterprise-Managed Authorization** — *stable*
- **Client Credentials** — *draft*

`csa-skilljar` already uses the OAuth `client_credentials` grant, where the credential *is* the
identity and there is no person to log in as. That now has a draft extension, which is where its
hosted behaviour should be checked against rather than invented.

**Enterprise-Managed Authorization** is the stable extension nearest to the model described for a
hosted CSA fleet — a user authorises once, then nominates which of their agents may use the server.
It should be read before that is designed.

### A discrepancy worth recording

The installed SDK carries identity-assertion machinery — `IdentityAssertionParams`,
`exchange_identity_assertion`, `client/auth/extensions/identity_assertion.py`, RFC 7523 jwt-bearer
ID-JAG, sometimes referenced as SEP-990 — and **no corresponding extension is listed in
`ext-auth`**. The SDK is ahead of, or divergent from, the published extension registry.

This resolves an open question in [`PROTOCOL.md`](PROTOCOL.md) better than "unknown": the mechanism
is in the code we run and is not in the registry, so it should not be built on yet.

## What this changes in the plan

| finding | consequence |
|---|---|
| Cloudflare splits `apps/` from `packages/` | **adopt it** — servers under `apps/`, shared code under `packages/` |
| Cloudflare ships `implementation-guides/` | corroborates ADR-004; the convention tier gets its own directory |
| Cloudflare standardises a server *factory* | tier 2 offers a factory, not a base class |
| Official monorepo has no shared library | supports ADR-001's narrow bar; burden of proof on growth |
| Official monorepo mixes languages | "one repo per language" is not obviously right — reopen in `ESTATE.md` |
| DCR deprecated as of `2026-07-28` | hosted design must not use it; blog guidance is stale |
| stdio **SHOULD NOT** use OAuth | validates the existing credential design, normatively |
| No token passthrough | a hosted server holds its own upstream credential |
| `ext-auth` has Enterprise-Managed Authorization | read before designing agent delegation |
| SDK identity assertion not in `ext-auth` | do not build on it yet |

## What was not researched

- **No hosted MCP fleet was examined in operation**, only repositories and specifications.
- **Enterprise-Managed Authorization was listed, not read.** Its contents are unknown here.
- **No cost or operational comparison** of gateway versus per-server authorization.
- **Secondary sources were used only for framing**, never for a normative claim, after the DCR
  discrepancy showed they lag by a revision. They are not cited individually for that reason.
- **The TypeScript SDK was not examined**, so claims about `@modelcontextprotocol/sdk` behaviour in
  [`ESTATE.md`](ESTATE.md) come from CSA's own records rather than from upstream.
