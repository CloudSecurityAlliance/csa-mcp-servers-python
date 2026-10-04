# Sources, dated and rated

Every source used, with its date and how much weight it carries. The rating is not politeness — one
category of source in this list was **wrong about a normative requirement**, and separating the
tiers is what caught it.

Compiled **2026-10-04**.

---

## Why this file has a rating column

While researching, secondary sources were consistently clear that remote MCP servers must implement
**RFC 7591 Dynamic Client Registration**, citing protocol revision `2025-11-25`.

The primary source says the opposite as of `2026-07-28`:

> Authorization servers and MCP clients **MAY** support the OAuth 2.0 Dynamic Client Registration
> Protocol (RFC7591). Note that Dynamic Client Registration is **deprecated and retained for
> backwards compatibility** with authorization servers that do not support Client ID Metadata
> Documents.

Anyone following the secondary consensus would build a hosted fleet on a deprecated mechanism.

**The lesson, and it is the reason this file exists:** secondary sources about a fast-moving
specification lag it by roughly one revision and do not say so. With the Python SDK shipping every
9.5 days and the TypeScript SDK every 1.9 days, a six-month-old article is describing a different
protocol.

So: **tier 1 for anything acted on; tier 2 for framing only; tier 3 never.**

---

## Tier 1 — primary, and the only tier used for a normative claim

### The specification

| source | accessed | what it settled |
|---|---|---|
| [Specification `2026-07-28`](https://modelcontextprotocol.io/specification/2026-07-28) | 2026-10-04 | the current revision |
| [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) | 2026-10-03 | what changed from `2025-11-25` |
| [Versioning policy](https://modelcontextprotocol.io/specification/versioning) | 2026-10-03 | how revisions and deprecations work |
| [`basic/authorization`](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) | 2026-10-04 | **DCR deprecated**; stdio **SHOULD NOT** use OAuth; no token passthrough; RFC 9728 **MUST**; RFC 8707 **MUST**; RFC 9207 `iss` validation |
| [`basic/lifecycle`](https://modelcontextprotocol.io/specification/2026-07-28/basic/lifecycle) | 2026-10-03 | statelessness |
| [`basic/transports`](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports) | 2026-10-03 | HTTP+SSE deprecated |
| [`server/tools`](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) | 2026-10-03 | tool result contract |
| [`client/elicitation`](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation) | 2026-10-03 | elicitation after the MRTR change |
| [`modelcontextprotocol/ext-auth`](https://github.com/modelcontextprotocol/ext-auth) | 2026-10-04 | two extensions: Enterprise-Managed Authorization (*stable*), Client Credentials (*draft*). **Last pushed 2026-06-18 — 108 days stale** |

### Repository trees, via the GitHub API

Structure and dates below are facts, not descriptions of facts. Script:
[`measure.py`](measure.py).

| repository | accessed | created | role in the survey |
|---|---|---|---|
| [`awslabs/mcp`](https://github.com/awslabs/mcp) | 2026-10-04 | 2025-03-21 | 62 servers, no workspace, per-server `uv.lock` |
| [`cloudflare/mcp-server-cloudflare`](https://github.com/cloudflare/mcp-server-cloudflare) | 2026-10-04 | 2024-11-27 | `apps/` + `packages/`, pnpm + Turborepo |
| [`microsoft/mcp`](https://github.com/microsoft/mcp) | 2026-10-04 | 2025-04-09 | `servers/` + `core/` |
| [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) | 2026-10-04 | 2024-11-19 | 7 servers, no shared library, mixed languages |
| [`modelcontextprotocol/servers-archived`](https://github.com/modelcontextprotocol/servers-archived) | 2026-10-04 | 2025-05-28 | created **and archived the same day** — the prune |
| [`github/github-mcp-server`](https://github.com/github/github-mcp-server) | 2026-10-04 | 2025-03-04 | one server, toolsets |
| [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk) | 2026-10-04 | 2024-09-24 | 73 releases / 681 days |
| [`modelcontextprotocol/typescript-sdk`](https://github.com/modelcontextprotocol/typescript-sdk) | 2026-10-04 | 2024-09-24 | 100 releases / 184 days |

### The installed package

The strongest tier, because it is what actually runs. `mcp` **2.3.0**, inspected 2026-10-03 in all
four servers' shipped environments:

- `LATEST_PROTOCOL_VERSION = 2026-07-28`, `DEFAULT_NEGOTIATED_VERSION = 2025-03-26`,
  `MODERN_PROTOCOL_VERSIONS = ('2026-07-28',)`
- `server/discover` and `subscriptions/listen` registered by default on a bare `MCPServer`
- `elicit_url(self, message, url, elicitation_id)` — `elicitation_id` still **required**
- `MCPServer.instructions` is a read-only property; the `server/discover` handler derives
  `instructions` *at call time*
- identity-assertion machinery present, with **no matching entry in `ext-auth`**

Where documentation and installed source disagreed, the source was treated as authoritative. That
happened twice.

### CSA's own code and repositories

Measured, with the method published in [`../../docs/EVIDENCE.md`](../../docs/EVIDENCE.md): module
similarity across four servers, 241 tool registrations, 2,982 bare issue references, four
`fail_under = 100` gates, and repository creation dates.

---

## Tier 2 — secondary, framing only, never cited for a requirement

Used to find out *what questions people are asking*. Not used for any claim in the plan.

| source | published / accessed | what it contributed | caveat |
|---|---|---|---|
| [MCP Server Patterns for Enterprise AI Agents in 2026](https://www.digitalapplied.com/blog/mcp-server-patterns-enterprise-ai-agents) | accessed 2026-10-04 | the "MCP gateway" framing; four enterprise topologies | written against `2025-11-25` |
| [How to Architect a Multi-Tenant MCP Server](https://truto.one/blog/how-to-architect-a-multi-tenant-mcp-server-for-enterprise-b2b-saas/) | accessed 2026-10-04 | per-tenant token isolation, scoped URLs | — |
| [OAuth for MCP — Emerging Enterprise Patterns](https://blog.gitguardian.com/oauth-for-mcp-emerging-enterprise-patterns-for-agent-authorization/) | accessed 2026-10-04 | agent-authorization framing | — |
| [Best MCP server authentication providers (WorkOS)](https://workos.com/blog/best-mcp-server-authentication-providers) | accessed 2026-10-04 | vendor landscape | vendor-published |
| [OAuth 2.1 for Remote MCP Servers](https://mcp.directory/blog/oauth-21-for-remote-mcp-servers-streamable-http-explained-2026) | accessed 2026-10-04 | transport + OAuth overview | **asserts DCR is required — now wrong** |
| [Remote MCP Servers: Hosting, Authentication](https://www.kapa.ai/blog/remote-mcp-servers-hosting-authentication-best-practices) | accessed 2026-10-04 | hosting options | vendor-published |
| [Multi-Tenant MCP for SaaS (Albato)](https://albato.com/blog/publications/embedded-multi-tenant-mcp-saas) | accessed 2026-10-04 | isolation framing | vendor-published |
| [Model Context Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Model_Context_Protocol) | accessed 2026-10-04 | **the 2024-11-25 announcement date**; authorship | corroborated by repository creation dates |

The Microsoft figure of **57 Azure services across 276 tools** is secondary and **was not verified**.
It is used only as an order-of-magnitude comparison, never as a basis for a decision.

---

## Tier 3 — not used

MCP catalogue and aggregator sites (`glama.ai`, `mcpservers.org`, `playbooks.com`, `lobehub`,
`archestra.ai`, `deepwiki`, and similar) appeared throughout search results and are **not cited**.

Early in this research an aggregator description of Cloudflare's monorepo was read first. It was
roughly right — `apps/` and `packages/` — and omitted `pnpm-workspace.yaml`, `turbo.json`, the
`implementation-guides/` directory and the "fresh SDK v2 server factory" statement, which is where
the actually useful finding was. Fetching the repository replaced a vague summary with three
specific, citable facts.

They also frequently describe **forks** rather than the upstream project, which is how a search for
`github-mcp-server` returns a dozen mirrors of varying age.

---

## Re-running this

```bash
python research/fleet-survey/measure.py
```

Requires an authenticated `gh`. Everything in [`SURVEY.md`](SURVEY.md) and
[`TIMELINE.md`](TIMELINE.md) comes from it plus the specification pages above.

**This survey is accurate on 2026-10-04 and makes no claim about any later date.** With the Python
SDK shipping every 9.5 days and the TypeScript SDK every 1.9 days, that is a real caveat rather than
a formality.
