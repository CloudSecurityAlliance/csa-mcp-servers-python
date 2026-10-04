# Which protocol revision these servers speak

**The question this answers:** what revision of the Model Context Protocol the fleet actually
negotiates, and what the current revision changes for it.

Measured **2026-10-03** against `mcp` 2.3.0 — the version installed in all four servers' shipped
environments, checked one by one rather than assumed uniform.

## Specification

| | |
|---|---|
| Current revision | [`2026-07-28`](https://modelcontextprotocol.io/specification/2026-07-28) |
| What changed | [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) |
| How revisions work | [versioning policy](https://modelcontextprotocol.io/specification/versioning) |
| Lifecycle | [basic/lifecycle](https://modelcontextprotocol.io/specification/2026-07-28/basic/lifecycle) |
| Transports | [basic/transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports) |
| Authorization | [basic/authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) |
| Tools | [server/tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) |
| Elicitation | [client/elicitation](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation) |
| Source, and the SEPs | [modelcontextprotocol/modelcontextprotocol](https://github.com/modelcontextprotocol/modelcontextprotocol) · [SEP process](https://modelcontextprotocol.io/community/sep-guidelines) |
| Python SDK | [python-sdk](https://github.com/modelcontextprotocol/python-sdk) · [`mcp` on PyPI](https://pypi.org/project/mcp/) |

---

## The number that reorders the work

| SDK constant | value |
|---|---|
| `LATEST_PROTOCOL_VERSION` | `2026-07-28` |
| `DEFAULT_NEGOTIATED_VERSION` | **`2025-03-26`** |
| `MODERN_PROTOCOL_VERSIONS` | `('2026-07-28',)` — exactly one |

The SDK's default negotiated revision is **four revisions behind its own latest**, and in the SDK's
own vocabulary exactly one revision counts as `MODERN` — so everything else, including what we
probably speak, is legacy by that definition.

And no server has an opinion. Searching all four `src/` trees for a pinned or asserted protocol
version returns **one hit, in a docstring**. Nothing in the fleet negotiates, pins, asserts or logs
a protocol version.

> **So the first task is a measurement, not a port.** `DEFAULT_NEGOTIATED_VERSION` is the SDK's
> fallback — it is not evidence of what Claude Code or Claude Desktop actually asks our servers for.
> The negotiated revision is **unknown**. It is listed first in the work below for that reason, and
> this document does not claim to know it.

## What `2026-07-28` removes that the fleet uses

Two things, in the same file, in both Google servers.

| removed | our call sites |
|---|---|
| `elicitationId` on URL-mode elicitation | `csa-google-workspace/.../mcp/_tools/auth.py:236,239,243` · `csa-google-gmail-calendar/.../mcp/_tools/auth.py:231,234,238` |
| `notifications/elicitation/complete` | `csa-google-workspace/.../auth.py:270` · `csa-google-gmail-calendar/.../auth.py:262` |

Both were introduced in revision `2025-11-25` and deleted in `2026-07-28`. They existed for one
revision.

**Nothing is broken today.** The SDK still ships both, and `elicit_url`'s signature is
`(self, message, url, elicitation_id)` with `elicitation_id` **required**. When the SDK drops it,
the failure is a `TypeError` at four known call sites rather than a silent change of behaviour —
which is the good version of this problem.

The replacement is **MRTR** (Multi Round-Trip Requests, SEP-2322): rather than the server issuing a
request back at the client, a tool returns an `InputRequiredResult` carrying `inputRequests`, and
the client re-issues the same call with `inputResponses`. Correlation moves from a protocol-defined
`elicitationId` to an id the server puts in `requestState` itself. `InputRequiredResult` is already
present in the installed SDK.

**This is a recorded trigger, not work.** The SDK retains the working path and offers no migrated
`elicit_url`. Act when the SDK removes the parameter or ships the MRTR equivalent — whichever comes
first.

## What it removes that the fleet does not use

A revision deprecating three capabilities reads alarming until it is checked.

| deprecated or removed | in the fleet |
|---|---|
| Roots | **none** — a word-boundary search matched only English prose and an xlsx comment parse |
| Sampling / `createMessage` | **none** |
| Logging / `logging/setLevel` / `notifications/message` | **none** |
| `ping` | **none of ours call it**; the SDK still registers a handler |
| HTTP+SSE transport | not used; all five are `stdio` |

Three of this revision's four deprecations cost the Python fleet nothing, and that is measured
rather than hoped.

The one that is not free is **Logging**, prospectively: the suggested migration is stderr on
`stdio`, or OpenTelemetry. Nothing to undo, but it closes off `notifications/message` for any future
server — worth knowing before someone reaches for it.

## What arrives for free

A bare `MCPServer(name="probe")` already registers ten request handlers:

```
ping  prompts/get  prompts/list  resources/list  resources/read
resources/templates/list  server/discover  subscriptions/listen  tools/call  tools/list
```

`server/discover` is **MUST-implement** in `2026-07-28` and it is inherited, not written.
`subscriptions/listen` likewise.

## The removal that improves a design

Worth reading twice, because the obvious reading is backwards.

A CSA server is expected to answer "am I configured, and does that configuration work?" at three
levels — present (no I/O), coherent (local parse), accepted (one bounded call). Only the first two
could be announced up front, for a structural reason: under `initialize`, a server's `instructions`
were a **snapshot fixed at construction**. `MCPServer.instructions` is a read-only property that
raises `AttributeError` on assignment — measured. Nothing could be recomputed later, so a
credential's live status could never reach a client's first impression of the server.

Removing the handshake sounds like it would make that worse. It makes it better. The default
`server/discover` handler is, in the SDK's own words, *"auto-derived from server state at call
time"*; it returns `instructions=self.instructions`; and operators *"can replace it wholesale via
`add_request_handler`"*.

So a server can compute its real status **when asked** and return it there. The stateless revision
makes a server's self-description live rather than frozen.

The mechanism matters: `instructions` is still read-only, so this is done by **replacing the
discover handler**, not by mutating the attribute. One handler calling each server's own self-test
is precisely a tier-2 concern — see [`ARCHITECTURE.md`](ARCHITECTURE.md).

## What becomes a design question

- **Statelessness.** No `initialize`, no `Mcp-Session-Id`. Cross-call state becomes server-minted
  handles passed as ordinary tool arguments. The five `stdio` servers hold little per-session state,
  so this lands mostly on hosting.
- **Required caching metadata — now confirmed normative.** Servers **MUST** include `ttlMs` and
  `cacheScope` on `tools/list`, `server/discover` and the other list results. `cacheScope` has two
  values, and `"private"` means *"Caches **MUST NOT** be shared across authorization contexts (e.g.
  a different access token requires a different cache)"* — explicitly the right choice *"for
  filtered list results that vary per user."*

  **This is the item that can be quietly wrong rather than loudly broken**, and the specification
  says so: a `"public"` result from an authenticated `tools/list` *"may be shared outside of the
  initial request's authorization context."* All four servers filter their tool surface by
  configured capability, so every one of them needs `"private"`.

  Two corollaries. Servers **MUST** apply the same `cacheScope` to every page of a paginated list.
  And servers **MUST NOT** rely on `cacheScope` alone to prevent unauthorized access — **filtering
  a tool list is not authorization**; the per-tool check still has to run at call time. See
  [`../research/orchestration/`](../research/orchestration/).
- **OAuth DCR (RFC 7591) is deprecated** in favour of Client ID Metadata Documents — so the hosted
  design must not be built on it.
- **Credentials keyed by issuer** (SEP-2352): never reuse a registration across authorization
  servers.
- **RFC 9207 `iss` validation**, and deterministic `tools/list` ordering. Both small, both testable.

## Work, in order

1. **Measure what each server actually negotiates**, with the clients in real use. Nothing else here
   is decidable without it.
2. **Decide `cache_scope` per list result** — the one item that fails silently.
3. **Leave the elicitation pair alone**; the trigger is recorded above.
4. **Put `server/discover` in `csa-mcp`**, once, as the home of the live self-test.
5. **Keep DCR out of the hosted design.**

## What was not checked

- **No live handshake was performed.** The negotiated revision is unknown, not assumed.
- **No server was run against a `2026-07-28` client.**
- **The TypeScript SDK was not examined.** CSA's Cloudflare Workers servers are a separate
  assessment; the HTTP+SSE deprecation lands there, not on these five.
- **Worked from the changelog plus SDK source**, not a full read of the revision. Where the two
  disagreed, the SDK source was treated as what we actually run.
- **SEP-990 identity assertion** is present in the SDK's auth surface; which revision introduced it
  was not established.
