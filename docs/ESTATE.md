# The estate

**The question this answers:** where does this repository sit among all of CSA's MCP servers, and
which rules are fleet-wide rather than local to it?

[`ARCHITECTURE.md`](ARCHITECTURE.md) is the detailed design for the **Python stdio** fleet — the five
servers planned for this repository. This is the layer above it: everything CSA runs, and why it
divides the way it does.

State recorded 2026-10-04 from CSA's own roster.

**On the links below:** five of them point to repositories that are **private** — `CSA-MCP-Server`,
`CSA-MCP-Core`, `csa-hive-mcp`, `mcp-server-starwatch` and CINO-Platform-Engineering. Verified
private with an authenticated check on 2026-10-04, so they return 404 to the public rather than
being broken. They are kept because the alternative is describing systems without saying where they
are.

---

## The division is by delivery, not by language

| | **local stdio** | **hosted HTTP** |
|---|---|---|
| **what** | a binary on a colleague's laptop | a Worker or container on the internet |
| **servers** | the five in this repository | `csa-mcp`, `csa-hive-mcp`, Customer360 |
| **language** | Python | mostly TypeScript; Customer360 is Python |
| **credential** | from the environment, per the specification | OAuth resource server; server holds upstream credentials |
| **who it serves** | one person, their own access | many, with tenancy |
| **distribution** | PyPI, installed per user | deployed; "always latest" is automatic |

Language correlates with delivery here but does not cause it. The real split is **whose credential
is in play and how many tenants exist** — which is why the two halves cannot share an architecture,
and why this repository is scoped to one of them.

### The specification agrees with the split

> Implementations using an STDIO transport **SHOULD NOT** follow [the authorization] specification,
> and instead retrieve credentials from the environment.

A local stdio server is *normatively* not an OAuth client. See [`PRIOR-ART.md`](PRIOR-ART.md) §4 —
CSA reached this independently and the specification now states it.

## The hosted fleet, as it stands

| server | where | state | notes |
|---|---|---|---|
| [`CSA-MCP-Server`](https://github.com/CloudSecurityAlliance-Internal/CSA-MCP-Server) / [`CSA-MCP-Core`](https://github.com/CloudSecurityAlliance-Internal/CSA-MCP-Core) | `cloudsecurityalliance.org/mcp` | **live**, 1.0.0 | tiered auth — anonymous-by-IP through `mcptok_` tokens, tiers 1–5. Capabilities load as plugins |
| [`csa-hive-mcp`](https://github.com/CSA-Hive/csa-hive-mcp) | `pod.cloudsecurityalliance.org/mcp` | **live**, 1.0.0 | API key at the edge. Holds **no backend credentials** — reaches data by Cloudflare service binding, Worker-to-Worker |
| Customer360 | internal | live | Python, container — the exception to TypeScript-on-Workers |
| [`mcp-server-starwatch`](https://github.com/CloudSecurityAlliance/mcp-server-starwatch) | documented only | **abandoned**, never deployed | the STAR Watch API is read-only. Two commits, no DNS record for its hostname, and the npm package its README tells users to `npx` is unpublished |

Three things in that table are the fleet's live problems, and none is this repository's to fix:

- **`CSA-MCP-Core` has one consumer.** It centralises auth, rate limiting, observability and the
  error envelope, and the only server using it is `csa-mcp`. This is the in-house counter-example
  ADR-001 is written against — *do not build a foundation before its second consumer* — and it is
  cited in [`ARCHITECTURE.md`](ARCHITECTURE.md) for that reason.
- **TypeScript SDK versions have drifted** across three servers. The same class of divergence this
  repository exists to fix on the Python side, unaddressed on the other.
- **`csa-hive-mcp` holds no backend credentials** and reaches data by service binding. That is the
  best credential posture in the estate and the pattern a hosted Python server should copy.

## Which rules are fleet-wide

These apply to every CSA MCP server regardless of language or delivery, and are maintained in
[CINO-Platform-Engineering](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering)
under `surfaces/mcp/` rather than here:

- **Vendor content reaching a model is untrusted data, never instructions.**
- **One vocabulary across the family** — a consumer holding several CSA servers should not learn a
  dialect per server. Currently violated: four servers, three shapes for "am I authenticated?"
- **Introspection is owed** — what am I, what may I do, what would you refuse, how do I report a
  problem.
- **`0.X.Y` until we mean it.** `1.0.0` is a claim about API stability, not a milestone.
- **100% coverage with branches**, per package, measured per level.
- **Do not build a foundation before its second consumer.**
- **No token passthrough** — a hosted server must not forward a client's token upstream
  (**MUST NOT**, `2026-07-28`).

## Where this repository fits

It covers **the five Python stdio servers and nothing else.** Concretely out of scope: the
TypeScript Workers servers, Customer360, and the hosted posture beyond two constraints recorded in
[`ARCHITECTURE.md`](ARCHITECTURE.md) so the hosted design is not built wrong (no DCR; credentials
keyed by issuer).

## The question this reopens

An earlier assumption was a sibling `csa-mcp-servers-typescript` monorepo — one repository per
language.

[`PRIOR-ART.md`](PRIOR-ART.md) §2 undercuts that. The **official** MCP reference monorepo mixes
TypeScript and Python in one tree, publishing each package to its own registry from the same
repository. So "one repo per language" is not the obvious answer it appeared to be.

The honest counter-argument, and it may still win: CSA's TypeScript servers are **Workers-deployed,
not npm-published**, so they share almost nothing with a PyPI package beyond being MCP servers —
no common build, no common release, no common runtime. Cloudflare's own monorepo is all-Workers and
all-TypeScript, so it is not evidence either way on mixing.

**Not decided.** It does not block this repository, because the Python fleet needs its own home
regardless. It is flagged in [`REVIEW-BRIEF.md`](REVIEW-BRIEF.md) as a question for a reviewer,
rather than settled by default.

## What was not established

- **`CSA-MCP-Core` and `csa-mcp` were not inspected.** Not cloned locally, and not found by repo
  search under either organisation — the roster supplied their locations. Everything above about
  them is CSA's own record, not measurement, and it is the kind of claim
  [`OPERATIONAL-RESOURCES.md`](../OPERATIONAL-RESOURCES.md) warns goes stale unchecked.
- **The exact TypeScript SDK versions** are recorded as drifted without the current numbers.
- **Customer360 was not examined at all**; it is internal and out of scope here.
- **Whether a gateway belongs in front of the hosted fleet** — the dominant 2026 enterprise pattern
  per [`PRIOR-ART.md`](PRIOR-ART.md) §3, and entirely unassessed for CSA.
