# Can the Anthropic platform even use these servers?

**Status:** first pass, 2026-10-04. Reconciliation of an external research synthesis against primary
sources, per [`../METHOD.md`](../METHOD.md).

**Origin.** A research document — *"Building AI Agents on the Anthropic Platform: Integration
Architecture and Agent Authorization"*, dated 2026-10-03, prepared for CSA — was supplied for
cross-checking. It overlaps this repository's own surveys substantially. This records what survived
verification, what it closes, where it conflicts with CSA's existing documentation, and what it is
missing.

The source document labels its own evidence and names its biases, including that some of its
sources are vendor marketing. That is why it was worth reconciling rather than either adopting or
discarding.

---

## The finding that changes this plan

`[measured]` From the
[MCP connector reference](https://platform.claude.com/docs/en/managed-agents/mcp-connector), read
2026-10-04:

> | `type` | Required. **Must be `"url"`**. |
> | `url` | Required. **The endpoint of the remote MCP server** |

**All five servers planned for this repository are `stdio`. None of them can attach to a Claude
Managed Agents agent directly.** Not a configuration problem — the field accepts one value and it is
not ours.

`[inferred]` And the reason is structural rather than an omission, which the two facts together
explain better than either alone. The specification says a stdio transport **SHOULD NOT** follow the
authorization spec and should *"retrieve credentials from the environment"* — a stdio server is
designed for a local human with a local environment. A managed agent has neither. There is no
environment to read a credential from and no human at a browser to consent.

So "local stdio" and "managed agent" are not two deployment options for the same server. They are
different products.

### What that does to the roadmap

[`../../docs/ESTATE.md`](../../docs/ESTATE.md) divides the estate by delivery and treats hosted as a
later phase. If CSA standardises agents on Managed Agents, hosted stops being phase three and
becomes **a precondition for using these servers at all** from that platform.

Four documented ways across the gap, from the source document's §6.2 — `[reported]`, since only the
connector constraint itself was verified here:

| pattern | mechanism | cost |
|---|---|---|
| Hosted remote MCP + vault | the supported path | requires making our servers remote HTTP — the hosted phase |
| MCP tunnels | outbound relay from our network | research preview, access by request |
| Self-hosted sandbox worker as MCP client | a worker connects to the internal server and re-exposes its tools | the worker becomes the client; our server stays stdio |
| CLI/SDK in the sandbox | credentials injected at egress; use `gh`, `psql` | **bypasses any gateway policy entirely** |

That last row is worth stating as a rule rather than an option: **if the sandbox holds raw
credentials, the agent can route around every control the MCP server implements.** It is the
cheapest path and it discards the 1,838 lines of policy measured in
[`../enforcement/`](../enforcement/).

## Platform facts verified at source

Everything in this table was checked against the connector documentation rather than taken from the
synthesis. All of it held.

| claim | verified |
|---|---|
| Only `type: "url"`, remote MCP over Streamable HTTP | yes |
| 20 MCP servers per agent maximum | yes |
| Tool output over 100,000 characters (~25,000 tokens) spills to a sandbox file | yes |
| MCP toolsets default to `always_ask` | yes |
| **All server tools are enabled by default**; `default_config.enabled: false` then explicit allowlist | yes — and the docs give the reason: *"when you want tools added by the server operator to stay off until you review them"* |
| Credentials matched by **normalized URL**; if none matches, **the connection is attempted unauthenticated** | yes |
| Session creation does **not** validate MCP connectivity or credentials | yes — `mcp_connection_failed_error`, `mcp_authentication_failed_error`, retried on idle→running |
| A `limited` environment blocks MCP servers unless `allow_mcp_servers: true` or `allowed_hosts` | yes |
| Vaults are workspace-scoped and referenceable by anyone with a workspace API key | `[reported]` — not verified; the vaults page was not read |

`[inferred]` Two of these matter more for CSA than their placement in a reference table suggests.

**All tools enabled by default** meets the 241-tool measurement from
[`../orchestration/`](../orchestration/) badly: attaching `csa-skilljar` to an agent adds **114
tools** unless someone writes an explicit allowlist. The platform offers the client-side half of
tool curation; nothing makes anyone use it.

**Silent fallback to unauthenticated** on a URL mismatch is the same class of failure as a guard
that cannot fail. A trailing slash is tolerated; a different path or subdomain is not — and the
consequence is a working session with an unauthenticated server rather than an error.

## Three of this repository's open questions, closed

| question | answer from the synthesis |
|---|---|
| *"SEP-990 identity assertion is in the SDK; which revision introduced it was not established"* ([`../../docs/PROTOCOL.md`](../../docs/PROTOCOL.md)) | **None.** ID-JAG is an IETF **Internet-Draft (-04)**, not an RFC; OAuth Identity Chaining is at draft -12. So the SDK ships ahead of a draft, which is why `ext-auth` has no entry — `[reported]` |
| *"Enterprise-Managed Authorization was listed, not read"* (twice) | It is the path by which **Okta Cross App Access / ID-JAG reaches MCP servers**. So the stable extension and the agent-identity standard are the same thread — `[reported]` |
| *"Whether a determined injected instruction can route around the allowlists is untested"* ([`../enforcement/`](../enforcement/)) | A base rate exists: **MCPHunt measured policy-violating data propagation in 11.5%–41.3% of runs** across agents and providers **in multi-server setups** — `[reported]`, arXiv |

`[inferred]` That last one is the most actionable thing in the synthesis. CSA runs **four servers
simultaneously** — the exact configuration measured — so the question is not whether cross-server
leakage applies to us but where in that range we sit. It makes the untested gap in
[`../enforcement/`](../enforcement/) a measurable experiment rather than an open worry.

## Where it conflicts with CSA's own documentation

`[measured]` The synthesis §7.2 recommends *"per-agent Google service accounts limited to shared
folders, **never domain-wide delegation**."*

CINO-PE says the opposite for one server, in three places: `surfaces/mcp/CREDENTIALS.md`,
`GOALS.md` and `ROSTER.md` all record `csa-google-workspace-audit` as using **a service account with
domain-wide delegation**, and ROSTER.md notes it *"has no such ceiling: it can read every mailbox."*
An insight file names it outright as *"a service-account credential with domain-wide delegation and
no ACL ceiling beneath it."*

`[inferred]` **This is probably not a contradiction, and it should still be reconciled explicitly.**
The two are answering different questions: "never DWD" is advice for *per-agent workload identity*
reaching ordinary resources, while CSA's DWD is for a *tenant-audit* server whose entire purpose is
reading everything. Both can be true.

But they give opposite guidance on the same mechanism with neither acknowledging the other, and
`csa-google-workspace-audit` is exactly where they meet — the one server not yet built. That is the
shape of failure CINO-PE's own guidance warns about: not staleness but **disagreement**, with both
documents reading as authoritative and neither marked as the loser. It needs a sentence in the audit
server's ADR saying why DWD is correct *there* despite being wrong generally.

## What the synthesis is missing, that this repository has

`[measured]` **`cacheScope` appears nowhere in it**, and its §7.7 reference architecture puts a
gateway in the path. That is precisely where the omission bites: `cacheScope: "public"` on an
authenticated `tools/list` means the result *"may be shared outside of the initial request's
authorization context"* — and the specification names *"shared gateway or caching proxy"* as the
things permitted to do so. A gateway in front of identity-filtered servers is the exact deployment
where getting this wrong leaks one caller's tool surface to another. See
[`../orchestration/`](../orchestration/).

`[measured]` **The protocol-version measurement.** The synthesis asks twice (§5.3, §11) which
revision the Managed Agents connector negotiates. Worth pairing with what this repository measured:
**our own servers do not assert one either** — the SDK's `DEFAULT_NEGOTIATED_VERSION` is
`2025-03-26` while `LATEST_PROTOCOL_VERSION` is `2026-07-28`, and a search of all four `src/` trees
found one hit, in a docstring. So the question is two-sided, and our side is answerable without
asking Anthropic anything.

`[measured]` **Filtering is not authorization.** The synthesis quotes WorkOS — *"gateways reduce
where access is configured but do not remove the need for authorization in the MCP server itself"* —
which is correct and is also in the specification normatively, twice: servers **MUST NOT** rely on
`cacheScope` alone, and *"treating claimed scopes in token as sufficient without server-side
authorization logic"* is listed as a common mistake. Worth citing the spec rather than a vendor.

## What this reconciliation did not do

- **Only the MCP connector page was verified.** Vaults, permission policies, self-hosted sandboxes,
  environments and `ant apply` were not read. Everything about them here is `[reported]`.
- **No competitor platform was checked.** The synthesis's §4 table — AWS AgentCore, Microsoft Entra
  Agent ID, Google Agent Platform, OpenAI — is unverified here, though
  [`../enforcement/`](../enforcement/) independently verified Google's Agent Gateway.
- **No arXiv paper was read.** FIDES, MCPHunt, APPA and FlowSeal are cited as `[reported]`. The
  MCPHunt range is the one worth reading properly, because it bears on a gap we have.
- **Rule of Two was not traced to its source.** Attributed to Meta, October 2025, via Simon
  Willison.
- **Nothing about cost, retention terms, or A2A support** was checked.
- **The synthesis's §7.3 per-session credential minting is labelled by its own author as a proposed,
  untested design.** It is not evidence of practice and is not treated as such here.
