# Architecture

**The question this answers:** what are the layers, what belongs in each, and — the part that
matters more — what must never be shared.

Read [`EVIDENCE.md`](EVIDENCE.md) first. Every boundary here was placed by a measurement, and the
numbers are there.

---

## Four tiers, not three

The obvious design is three layers: the official SDK at the bottom, a CSA library above it, vendor
servers on top. That is right about the bottom and the top and wrong in the middle, because it has
no place to put the largest category the measurement found.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 4. VENDOR SERVERS                       servers/<name>/                  │
│    csa-zendesk · csa-google-workspace · csa-google-gmail-calendar        │
│    csa-skilljar · csa-google-workspace-audit                             │
│    backend.py (1020–2239 lines, 1% similar) · policy.py · _schemas.py    │
│    Most of the code lives here. It is supposed to.                       │
├──────────────────────────────────────────────────────────────────────────┤
│ 3. CONVENTION  — documentation and a scaffold, NOT importable code       │
│    the shape of server.py (11%), cli.py (10%), _tools/_base.py (15%)     │
│    layout, naming, tool-registration pattern, where policy is checked    │
├──────────────────────────────────────────────────────────────────────────┤
│ 2. csa-mcp  — ours, extracted, deliberately small   packages/csa-mcp/    │
│    markdown · oauth success page · discover/self-test · status vocabulary│
├──────────────────────────────────────────────────────────────────────────┤
│ 1. mcp  — the official Python SDK, pinned with a ceiling                 │
│    MCPServer, transports, auth primitives, protocol types                │
└──────────────────────────────────────────────────────────────────────────┘
```

## Tier 1 — the official SDK

[`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk), used
directly. Not wrapped, not abstracted behind our own interface.

Two reasons, both learned rather than assumed. FastMCP — the third-party framework these servers
could have standardised on — *became* the official SDK (`FastMCP` is now
`mcp.server.mcpserver.MCPServer`), so building on the wrapper would have meant later migrating onto
the thing we already had. And the SDK ships a deliberate tombstone when it breaks a major:
`mcp/server/fastmcp.py` in the installed 2.3.0 exists solely to raise a `ModuleNotFoundError`
naming the migration guide, *"because the bare 'No module named' gave v1 code no hint that the
installed SDK is a different major version."* That is a maintainer who thinks about upgrades, and
the standard to meet when we publish.

Both claims are from the installed package rather than from documentation about it —
[`python-sdk`](https://github.com/modelcontextprotocol/python-sdk),
[`mcp` on PyPI](https://pypi.org/project/mcp/).

**Pinned with a ceiling, not a floor.** Measured 2026-10-03 from
[PyPI](https://pypi.org/project/mcp/): `mcp` was at 2.3.0, released the **previous day**, across 73
releases. A dependency moving that fast needs an upper bound.

The strongest external support for keeping this tier thin is that the
[official reference monorepo](https://github.com/modelcontextprotocol/servers) holds seven servers
with **no shared in-repo library at all** — each self-contained on the SDK. See
[`PRIOR-ART.md`](PRIOR-ART.md) §2.

See [`PROTOCOL.md`](PROTOCOL.md) for which revision it actually speaks, which is not the one its
`LATEST_PROTOCOL_VERSION` advertises.

## Tier 2 — `csa-mcp`

The shared library. It does not exist yet, and when it does it starts at roughly 300 lines.

### What it contains on day one

| module | provenance | why it qualifies |
|---|---|---|
| `markdown.py` | extracted | 96% identical, docstring-only differences, mandated fleet-wide by DEC-018 |
| `oauth_success_page.py` | extracted | 95% identical, 68 lines each |
| `discover.py` | **new** | the `server/discover` handler and live self-test. No incumbent in any server, so there is nothing to diverge from |
| `status.py` | **new** | one status type for "am I configured, and does it work?" Four servers currently give three answers |

The two new modules are the exception to "only extract, never design", and the exception is narrow
and deliberate: **a module with no existing implementations cannot be extracted from them.** The
test is whether anything would have to be *reconciled* to adopt it. For these two, nothing would.

### What it must not contain

`backend.py`, `policy.py`, `_schemas.py`, `client.py`, `exceptions.py`, `_config.py`. Measured at
1–7% similarity, 236–2239 lines each. This is vendor surface and it stays with its vendor.

### The second tranche, after reconciliation

The OAuth trio — `_auth_flow` (59%), `_login` (58%), `_logging` (60%) — belongs entirely to the two
Google servers. Fifty-eight percent is the number to be most careful about: close enough that
sharing looks obvious, different enough that adopting either copy silently discards the other's
behaviour. Reconcile the difference as a decision, *then* extract the agreed result.

### The rule that keeps this honest

**Nothing enters `csa-mcp` until a second server has actually consumed it.** Not "will consume
it" — has. This is the rule that `CSA-MCP-Core` broke: it centralised auth, rate limiting,
observability and the error envelope while having exactly one consumer, and was being pushed more
often than the server it served. A foundation moving faster than its only consumer is being built
on theory.

Anyone proposing to grow `csa-mcp` should be able to name the measured number that justifies it.

## Tier 3 — convention

This tier is the architectural finding, and it is the one most likely to be designed away by a
reviewer who prefers code to documentation.

`server.py`, `cli.py` and `_tools/_base.py` exist in three servers each and score **10–15%**
similarity. They do corresponding jobs. Almost no text survives between them.

The instinct is a base class or a framework entry point. That would be abstracting a *structural
resemblance* rather than any shared behaviour — the servers would then write code to work around
the abstraction, which is how a 300-line library becomes a 3000-line framework that every server
fights.

So this tier ships:

- **A documented layout** — where tools are registered, where policy is checked, where the untrusted
  boundary is drawn, what `cli.py` is responsible for.
- **A `scaffold/` template** — a new server starts by copying it. `csa-google-workspace-audit` is the
  first server that will.
- **No importable code.**

A convention that is copied and then diverges is working correctly. A base class that is inherited
and then worked around is not.

**Independently corroborated.** Cloudflare's MCP monorepo ships an `implementation-guides/`
directory — developer documentation for building servers in the repo — and standardises *"the same
stateless Streamable HTTP handler at `/mcp`"* built from *"a fresh SDK v2 server factory"* per
server. A shared factory and a written contract, not inheritance, across fifteen servers. See
[`PRIOR-ART.md`](PRIOR-ART.md) §1.

## Tier 4 — the vendor servers

Where the work is. `backend.py` alone runs 1020–2239 lines per server at 1% similarity, and that
number should never improve.

Each server owns its vendor API surface, its policy, its schemas, its exceptions, and its
`demonstration_plan` — which at 3% similarity across three servers turns out to be far more
server-specific than its generic-sounding name suggests.

## Packaging

A [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/): one `uv.lock` at the
root, each package resolving against it.

This is the mechanism that fixes the measured drift, and it is worth being precise about why. The
problem was never that four repositories *could* diverge; it is that divergence was **invisible**.
One lockfile makes the divergent state unrepresentable — `markdownify>=1.2` in one package and
`>=0.13` in another stops being a thing that can quietly be true.

### This does not conflict with one-environment-per-server

DEC-012 in CINO-Platform-Engineering requires **one isolated environment per installed server**,
after a `uv` rebuild turned four working servers into husks in a single run. It governs
*installation*: end users run `uv tool install csa-zendesk`, and a bad resolve in one server cannot
reach another.

A uv workspace is a *development* arrangement — one lockfile, one dev environment, four published
packages that still install independently. The two are compatible, and this is written down because
it reads like a conflict and will otherwise be re-litigated.

## Hosting, later

Everything above describes local `stdio` servers, which is what all five are. Hosted servers are a
separate posture — the server becomes an OAuth resource server, tenancy appears, and an agent's
access has to be distinguishable from its owner's.

Two constraints already apply to the design and are recorded now so they are not discovered later:

- **Do not build on OAuth Dynamic Client Registration.** RFC 7591 DCR is `MAY` and explicitly
  *"deprecated and retained for backwards compatibility"* in
  [`2026-07-28` authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization);
  Client ID Metadata Documents are the `SHOULD`. Note that current third-party guidance still
  recommends DCR, because it is written against the previous revision —
  [`PRIOR-ART.md`](PRIOR-ART.md) §3.
- **No token passthrough.** A hosted server **MUST NOT** *"accept or transit any other tokens"*, so
  it cannot forward a client's token to Google or Zendesk and must hold its own upstream credential.
- **Credentials are keyed by issuer**, and a registration is never reused across authorization
  servers (SEP-2352).
- **RFC 9728 Protected Resource Metadata is a `MUST`** for the server; RFC 8707 `resource` on both
  authorization and token requests is a `MUST` for the client.

`csa-google-workspace-audit` is the likeliest first hosted server, because it reads a whole tenant
and is the one where centralised logging and policy earn the most.
