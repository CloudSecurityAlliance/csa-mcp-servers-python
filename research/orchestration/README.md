# Many endpoints or one? Orchestration and progressive disclosure

**Status:** first pass, 2026-10-04. Follows [`../METHOD.md`](../METHOD.md).

**The question:** are people running 10–100 MCP servers at separate endpoints, or one large server
with progressive disclosure keyed on who is connecting — not just which user, but which *agent*? And
is this the same consolidation that happened to web properties twenty-five years ago, where many
hosts became one `example.org` with central routing?

**Short answer:** the analogy is half right, and the half that breaks is the useful part. The
ecosystem is not consolidating endpoints. It is making **connection lazy** — many servers, with the
*host* deciding what enters the model's context and when.

---

## Why the web analogy breaks

`[inferred]` Web properties consolidated because consolidation was **free at the point of use**. A
browser fetches only the URL it asks for; a site with ten thousand pages costs a visitor nothing
until they follow a link. Virtual hosting and path routing made one origin cheaper to operate with
no per-request penalty.

MCP inverts exactly that. A client must be **told the whole tool surface up front**, and every tool
definition costs tokens on every request. The spec's own numbers:

> ~150,000 tokens consumed on definitions alone, versus ~2,000 tokens with progressive discovery.

`[measured]` So consolidating endpoints does not reduce the cost that matters. Putting 500 tools
behind one URL produces one connection and 500 tools in context. The web never had this problem,
which is why its answer — one origin, central routing — is not this ecosystem's answer.

What MCP is trying to recover is the thing the web had for free: **laziness.** Following a link
rather than being handed the sitemap.

## What the official guidance actually says

`[measured]` From [Client Best
Practices](https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices),
revision `2026-07-28`. **Progressive disclosure is a host responsibility, not a server one:**

> The host fetches tool definitions via `tools/list` as normal, but **defers injecting them into the
> model's context**. The host provides a lightweight `search_tools` meta-tool to the model. The host
> loads full definitions into context only as needed.

A three-layer pattern — **Catalog** (`search_tools` returns names and one-line descriptions),
**Inspect** (`get_tool_details` fetches one full schema), **Execute**. With a recommended trigger:

> Implement a threshold as a percentage of the context window. For example, 1%-5%.

Retrieval strategies offered: keyword (BM25/regex), embedding, **subagent** (a small fast model
picks the tools), or hybrid. Both OpenAI and Anthropic now expose native tool search.

**So a server does not need to be large or clever for this to work.** It keeps exposing its tools;
the host decides what the model sees. A mega-server is not required to solve the context problem.

### And the user's actual question has a named answer: Dynamic Server Management

`[measured]` The same document addresses many-servers directly:

> Rather than connecting to every configured server at startup, a host can: maintain a registry of
> available servers and their high-level descriptions; connect to a server only when the model
> determines it needs that server's capabilities; **disconnect servers that are no longer relevant to
> the current task, freeing context.**

The documented sequence is `search_available_servers` → `enable_server` → `server/discover` →
`tools/list` → … → `disable_server`. Agent Skills can declare which servers they need, and the host
connects them only when that skill is invoked.

**That is many endpoints plus a registry, not one endpoint.** The discovery problem the web solved
with DNS and one origin, MCP solves with a host-side registry and lazy connection.

## The constraint nobody mentions until they have shipped it

`[measured]` This is the sharpest practical finding, and it cuts against dynamic disclosure:

> Most providers cache the prompt prefix, **including the `tools` array**. Adding or removing tool
> definitions mid-conversation **invalidates that cache**, and the resulting miss can cost more
> tokens than the definitions you removed.

Mitigations given: append new definitions *after* the cache breakpoint rather than re-sorting the
array; **or route every call through a single stable `call_tool({name, args})` meta-tool so the
array never changes**; and treat server disconnection as a conversation-boundary operation rather
than a per-turn one.

`[inferred]` Two things follow. First, naive progressive disclosure can be *more* expensive than
loading everything — the saving is real only if prompt-cache behaviour is respected. Second, this
explains an otherwise odd item in the `2026-07-28` changelog: **`tools/list` SHOULD now be
deterministically ordered**, and the stated reason is prompt-cache hits. The protocol revision is
already optimising for this pattern.

## Identity-keyed disclosure: the mechanism exists, with a sharp edge

`[measured]` A server *may* return a different `tools/list` per caller — all four CSA servers
already do, filtered by configured capability. The protocol mechanism that makes this safe is
`cacheScope`, which has exactly two values:

| value | meaning |
|---|---|
| `"public"` | no user-specific data; any client, **shared gateway or caching proxy** may serve it to **any** user |
| `"private"` | **"Caches MUST NOT be shared across authorization contexts (e.g. a different access token requires a different cache)"** |

And `"private"` is explicitly the right choice *"for filtered list results that vary per user."*

`[measured]` The security note states the failure directly:

> the Result from an authenticated `tools/list` call with a `"public"` `cacheScope` may be cached by
> a client and **may be shared outside of the initial request's authorization context** (i.e.
> different access tokens can leverage the same cache).

So the risk flagged in [`../../docs/PROTOCOL.md`](../../docs/PROTOCOL.md) as *"the one item that can
be quietly wrong rather than loudly broken"* is confirmed and normative. Servers **MUST** include
caching hints on `tools/list` and `server/discover` results, and **MUST** apply the same
`cacheScope` to every page of a paginated list.

`[measured]` One more sentence worth pinning to the wall, because it is the same lesson as
server-side authorization versus scopes:

> Servers ... **MUST NOT rely on `cacheScope` alone** to prevent unauthorized access to primitives.

**Filtering the tool list is not authorization.** Hiding a tool is a context-management and
usability measure; the per-primitive access control still has to be enforced when the tool is
called.

## "Which agent, not just which user" — the genuinely unsolved part

`[measured]` This is where the protocol is thinnest, and CSA had already identified it: an insight
in CINO-PE is titled *a vendor credential names the human, not the agent.*

- The installed SDK ships identity-assertion machinery — `IdentityAssertionParams`,
  `exchange_identity_assertion`, RFC 7523 jwt-bearer ID-JAG (sometimes referenced as SEP-990).
- **No corresponding extension is listed** in `modelcontextprotocol/ext-auth`, which last moved
  **2026-06-18**, 108 days before this survey.
- `ext-auth` does carry **Enterprise-Managed Authorization** (*stable*) — the nearest thing to
  "a user authorises once, then nominates which of their agents may use this server" — and
  **Client Credentials** (*draft*), which is the grant `csa-skilljar` already uses.

`[inferred]` So per-agent identity is available in code, absent from the published extension
registry, and adjacent to a stable extension nobody here has read. That is the opposite of settled,
and it is the part of the user's question the ecosystem has least to offer on.

## How new is any of this?

`[measured]` `modelcontextprotocol/progressive-disclosure-wg` — an official working group — was
created **2026-02-11** (235 days before this survey), last pushed **2026-09-28**, 10 open issues.
Recent items:

| issue | opened | title |
|---|---|---|
| #19 | 2026-09-28 | **sep: add progressive disclosure via groups proposal** |
| #18 | 2026-09-22 | case study: a marketplace of **70K+ tools** |
| #16 | 2026-09-03 | Doris findings and deterministic grouping reference experiment |
| #15 | 2026-08-31 | **docs: add limits of tool search document** |
| #13 | 2026-05-11 | Skills-as-Groups approach draft |
| #11 | 2026-03-04 | grouping extension implementation |

So: **the client-side pattern is documented and stable; the protocol-level mechanism is a live
proposal opened six days ago.** Note #15 — "limits of tool search" — meaning search-as-the-answer
has internal skeptics. Anyone adopting a grouping mechanism now is adopting a draft.

## What the big players actually ship

| | shape | endpoints |
|---|---|---|
| **AWS** | 62 separate servers, distributed as packages | per-server, mostly local |
| **Cloudflare** | 18 apps, each its own Worker | **many endpoints** |
| **Microsoft** | one Azure server (57 services, 276 tools) + ~a dozen specialists | few, large |
| **GitHub** | **one** server, `--toolsets` + `--dynamic-toolsets` | one |
| **CSA, hosted** | `csa-mcp` at one `/mcp`, capabilities as plugins, tiers 1–5 | **one, already tiered** |
| **CSA, local** | 4 stdio servers, 241 tools | per-server |

`[inferred]` Nobody is consolidating 100 servers to one endpoint. The large-server examples
(Microsoft, GitHub) are large **per domain**, and both added disclosure controls rather than
splitting. The many-server examples added none, because the host handles it.

### CSA already runs both patterns and has not written down which is for what

`[measured]` `csa-mcp` tells connecting clients: *"You are connected as tier `anonymous` … alongside
tiers 1-4 … Authenticated users will eventually see (a) higher or guaranteed rate limits, and (b)
**additional tools** that require specific membership in a working group, chapter, or staff role."*
Capabilities load as plugins.

That is the one-endpoint, identity-keyed progressive-disclosure design in the user's question —
already live at `cloudsecurityalliance.org/mcp`, in TypeScript. Meanwhile the Python fleet is the
opposite shape: four stdio servers, 241 tools, no disclosure control.

`[inferred]` **That is the actual finding for CSA.** Not which pattern to pick — the estate already
contains both, chosen for defensible reasons (hosted multi-tenant versus local single-user), and
nothing records the rule. `docs/ESTATE.md` divides by delivery; it should also divide by disclosure
strategy.

## What this means for the plan

| finding | consequence |
|---|---|
| Progressive disclosure is a **host** responsibility | CSA servers do not need to become mega-servers; keep exposing tools and let hosts defer |
| `cacheScope` must be `"private"` on any identity-filtered list | **confirmed normative** — all four servers filter, so this is a correctness requirement, not an optimisation |
| Filtering ≠ authorization (`MUST NOT rely on cacheScope alone`) | keep enforcing per-tool policy at call time; hiding is not protecting |
| Deterministic `tools/list` order exists for prompt caching | cheap to honour, and it makes any future disclosure work |
| Dynamic disclosure can cost more than it saves | if CSA ever adds it, respect the cache breakpoint; consider the stable `call_tool` meta-tool shape |
| Protocol-level grouping is a **draft** opened 6 days ago | do not build on it; track the WG |
| Per-agent identity is in the SDK, not in `ext-auth` | do not build on it yet; read Enterprise-Managed Authorization first |
| CSA runs both patterns already | record the rule in `ESTATE.md` |

## What this does not establish

- **No measurement of CSA's own token cost.** 241 tool definitions have a real size in tokens and it
  was not measured. That number would decide whether disclosure is urgent or theoretical.
- **No gateway or host was tested.** The 150,000-vs-2,000 figures are the spec's, not ours.
- **`csa-mcp`'s tiering was read from its client-facing instructions**, not from its code — the
  repository is private and was not inspected.
- **Enterprise-Managed Authorization was listed, not read**, for the second survey running.
- **Programmatic tool calling / code mode** is a whole second pattern in the same document — the
  model writes code in a sandbox and only the result enters context (~100K tokens → ~200-token
  script plus a ~15-token summary). Relevant to CSA and **not examined here**, except to note its
  security framing: *"Tool results from one server are untrusted input to another."*
