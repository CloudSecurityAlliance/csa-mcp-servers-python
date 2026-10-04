# Who are these servers for?

**Status:** first pass, 2026-10-04. The gap this fills was found by being asked, not by analysis —
which is itself the finding recorded in §1.

---

## 1. CORE RESEARCH FINDING: the largest consumer is undefined, and we are not going to pretend otherwise

> **C6 — the future agent fleet.**
> Reachability: **unknown.** Credential model: **unknown.** Policy enforcement: **unknown.**
> Population: **unknown**, and plausibly larger than every other consumer combined.
>
> **We do not know what this looks like. Nothing in this repository or in CINO-PE describes it, and
> no amount of further research in October 2026 will produce a reliable description.**

This is logged as a finding in its own right rather than as a gap to be closed, because the honest
state of knowledge *is* the result. Three reasons it will not yield to more work right now:

- **The protocol is moving underneath it.** Sessions were removed, `initialize` was removed, tasks
  became an extension, and progressive-disclosure grouping is a draft SEP opened six days before
  this was written. Agent-identity standards are Internet-Drafts (ID-JAG `-04`, OAuth Identity
  Chaining `-12`), not RFCs.
- **The commercial layer is younger than the question.** The agent-runtime products this fleet would
  run on shipped during 2026 and are changing monthly.
- **The population is the part nobody can forecast.** "Thousands of logical agents against a small
  number of execution credentials" is the shape the industry expects; the actual distribution,
  lifetime, and privilege spread of CSA's agents is not knowable from here.

**What this means in practice.** C6 does not get a design. It gets **invariants** — things not to
bake in — because an assumption that holds for C1 and quietly fails for C6 is the expensive kind.
Every invariant below is derived from something measured elsewhere in `research/`, not from
speculation:

| don't assume | because | measured in |
|---|---|---|
| a human is present | `csa-skilljar` already runs with none — `client_credentials`, the credential *is* the identity | the fleet |
| the credential names the actor | no vendor ever sees the actor; Google logs the execution principal only | [`../service-identity/`](../service-identity/) |
| `stdio` is available | Claude Managed Agents accepts `type: "url"` **only** | [`../managed-agents/`](../managed-agents/) |
| one agent per user, or that a user's agents are equivalent | the whole point of per-agent authorization | [`../service-identity/`](../service-identity/) |
| the tool list is static or shared | identity-filtered lists need `cacheScope: "private"`, normatively | [`../orchestration/`](../orchestration/) |
| a session exists | `2026-07-28` removed protocol sessions entirely | [`../../docs/PROTOCOL.md`](../../docs/PROTOCOL.md) |
| you can ask a question mid-call | elicitation may be unavailable, and its `elicitationId` was deleted after one revision | [`../../docs/PROTOCOL.md`](../../docs/PROTOCOL.md) |
| policy is runtime-mutable | env-only is deliberate and is what makes local policy bind the model | [`../enforcement/`](../enforcement/) |
| all tools should be in context | a tool absent from context is one an injected instruction cannot name | [`../orchestration/`](../orchestration/) |

An invariant list is the correct artifact for a consumer you cannot describe. A persona would be
fiction.

## 2. That nothing defined any of this is the second finding

`[measured]` Searched CINO-PE and all five server repositories 2026-10-04. **No use-case, persona,
or consumer definition exists anywhere.**

- CINO-PE's `surfaces/mcp/GOALS.md` "three tiers" are **standards** tiers — what every server owes.
  Its three classes are **build** classes.
- `csa-mcp`'s audience model (anonymous, tiers 1–5) is an **authorization** ladder for one hosted
  server.
- The only actor definitions in the fleet are per-server `THREAT_MODEL.md` files, which name
  **attackers**.
- **The word "consumer" was already taken.** In this repository's own ADR-001 it means *"second
  consumer of a shared library."* That is how unoccupied this ground was: the term was in use for
  something else and nobody noticed the collision.

`[inferred]` So every architectural decision here — the four tiers, the extraction bar, the CI
spine, the enforcement model, the orchestration posture, the service-identity fork — was made
**consumer-blind.** `ROADMAP.md` commits five servers to "a usable internal standard" without
saying usable *by whom*. `BUILD-FOR-YOURSELF-FIRST` answers it for version one — "you" — and that
answer expires the moment a working-group member appears.

## 3. The consumers, as far as they are known

| | consumer | reachability | credential | policy is | status |
|---|---|---|---|---|---|
| **C1** | CSA staff at their own laptop | unconstrained — admin rights | theirs | **advisory** | `[proven]` — all four servers |
| **C2** | an agent on C1's laptop | inherits C1 | C1's | **enforcing on the model** | `[proven]` |
| **C3** | WG member on a locked-down corporate endpoint | **set by their employer** | CSA's, shared | enforcing | **`[absent]`** |
| **C4** | hosted agent (Managed Agents, etc.) | remote HTTP only | CSA's, brokered | enforcing | `[measured]` — stdio excluded |
| **C5** | AI developer agent modifying a server | unconstrained | **should be a test tenant** | mutable by design | **`[absent]`** |
| **C6** | the future agent fleet | **unknown** | **unknown** | **unknown** | **§1 — invariants only** |

### C1 and C2 are the only ones actually served today

And the distinction between them is the one that was missed for longest: **C1 will route around the
server.** A competent human with a good CLI finds an MCP server a downgrade — `gh` does more than
the GitHub MCP server, which is why it gets used instead. The local server's value is structure and
constraint *for a model*, so **C2, not C1, is its real audience.** C1 is the person who installs it.

### C3 is the one with a constraint nobody can negotiate

`[inferred]` A working-group member at a bank, insurer, or government department plausibly cannot
install Python or `uv` (no admin rights, application allowlisting), cannot run an unsigned binary
(MDM/AppLocker), may not reach `claude.ai` at all (egress policy), and may be prevented by DLP from
letting document content leave the endpoint. Their desktop client may be corporate-managed or
forbidden.

**For C3, local stdio is not less safe — it is impossible.** And hosted may also be impossible,
depending on their employer.

This is a category of constraint absent from every other document here: **the consumer's environment
is governed by a third party who is neither CSA nor the user.** It lands squarely on CSA's core
constituency, because working groups are staffed by people at precisely the organisations that lock
endpoints down hardest.

`[inferred]` Which inverts the priority order. C3 is the consumer we have analysed least and may be
the one that determines the architecture — because everyone else has *preferences* and C3 has a
*constraint*. It also means the OAuth-handover problem could be solved perfectly and C3 still fails,
for reasons that have nothing to do with OAuth.

**Open and blocking for C3:** can WG members realistically install anything, or is *browser-only*
the design floor? Nobody has asked them. Until somebody does, C3's row is speculation and is marked
`[absent]` rather than `[inferred]`.

### C5 is the maximal-privilege configuration, by accident

`[measured]` A developer agent running a server locally to modify it holds the credential **and** can
edit the policy, because policy is environment variables and it controls the environment. That is
correct and harmless on C1's own laptop. As a pattern it is the most privileged configuration in the
estate.

`[measured]` **No test tenant exists.** So today a dev agent experimenting against any of these
servers does so with production credentials against production data — Zendesk tickets, Google Drive,
Skilljar learners. That is a gap in test infrastructure, not in architecture, and it has no owner.

## 4. What this changes

| finding | consequence |
|---|---|
| C6 is undefined and will stay that way | design to **invariants**, not to a persona; revisit when the drafts become RFCs |
| Everything so far was decided consumer-blind | each ADR should name which consumers it serves — most currently imply C1/C2 without saying so |
| C2 is the local server's real audience, not C1 | stop justifying local servers by human convenience; justify them by model guardrails |
| C3 has a non-negotiable reachability constraint | **ask actual WG members before designing for them**; treat browser-only as plausible |
| C5 has production credentials | a test tenant is a prerequisite for AI-assisted development on these servers |
| "Consumer" is overloaded in our own docs | ADR-001's sense is *library consumer*; this document's is *human or agent user*. Disambiguate on sight |

## 5. What this does not establish

- **C3 has not been validated with a single real working-group member.** Every constraint listed is
  plausible and none is confirmed. This is the most important unverified claim in the document.
- **C6's invariants are derived from today's protocol.** They are a floor, not a forecast, and a
  revision could remove one.
- **No consumer was counted.** There are no population estimates for any row, which means nothing
  here supports prioritising by volume.
- **The hosted TypeScript fleet's consumers were not analysed** — `csa-mcp` serves anonymous
  tiers 1–5, which is a sixth shape this table does not cover.
