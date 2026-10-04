# Prior art

**The question this answers:** how does anyone else run more than one MCP server, and what does that
say about the choices in [`ARCHITECTURE.md`](ARCHITECTURE.md)?

Researched **2026-10-04**. Primary sources where the claim is load-bearing — a repository's own tree
rather than a catalogue's description of it, and the specification rather than a blog post about the
specification. Where the two disagreed, and they did, the disagreement is recorded below because it
is the most useful finding here.

---

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

## 5. Two authorization extensions exist, and one is directly ours

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
