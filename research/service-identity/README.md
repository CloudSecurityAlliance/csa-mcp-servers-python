# Shared execution identities: subject, actor, execution principal

**Status:** first pass, 2026-10-04. Reconciliation per [`../METHOD.md`](../METHOD.md).

**Origin.** *"Shared Service Identities for MCP and AI Agents"*, 2026-10-03, prepared for CSA. A
companion to the synthesis reconciled in [`../managed-agents/`](../managed-agents/) and dated the
same day. This one is more precise, and it **resolves a conflict that one left open**.

---

## It separates three identities, which is sharper than anything here had

The core move: **do not make downstream credentials the identity model for the agent platform.**
Every request preserves at least three principals:

| principal | who | example |
|---|---|---|
| **Subject** | the human or org principal whose authority caused the action | `kurt@…` |
| **Actor** | the agent or workload that actually selected and invoked the tool | `agent:research-writer-8372` |
| **Execution principal** | the identity the downstream SaaS actually sees | a Google service account |

`[inferred]` This answers a question asked earlier in this work — *"not just the user, but which
agent?"* — better than the protocol does. The answer is that **the agent is the actor, and no vendor
will ever see it.** Google's audit log records the execution principal and nothing else. So the
agent's identity cannot be recovered downstream at all; it exists only if CSA's own control plane
records it.

That reframes agent identity from a protocol feature we are waiting for into **a provenance
obligation we already have.** It maps onto RFC 8693's `sub`/`act`, and onto the ID-JAG draft the
other synthesis dated at Internet-Draft `-04`.

It is also the sharpest available statement of the enforcement conclusion in
[`../enforcement/`](../enforcement/), from its §8.3: **"model output is not authorization."**

## The resolution of the conflict flagged last turn

[`../managed-agents/`](../managed-agents/) recorded a tension: the other synthesis said *"never
domain-wide delegation"*, while CINO-PE records `csa-google-workspace-audit` as using exactly that.

`[measured]` This report settles it, consistently in three places:

> **Default:** direct service identity + Google ACL/group entitlement.
> **Exception:** DWD where user impersonation materially improves functionality, ownership
> semantics, or audit requirements.

and *"use DWD only when downstream named-user identity has a concrete benefit"*, and for attribution
*"where downstream named-user attribution is a hard requirement, use Domain-Wide Delegation."*

`[inferred]` So there was never a contradiction — the first document stated the default as an
absolute. **A tenant-audit server is the textbook exception**: reading every mailbox cannot be
expressed as group-ACL membership, so the only mechanism that works is impersonation. CINO-PE is
right, and the requirement is narrower than "justify DWD": the audit server's ADR should name the
**concrete benefit that cannot be achieved with a service identity.** That is a sentence, and it
closes the issue rather than leaving two live answers.

## The critical path is a Google primitive nobody has tested

`[measured]` The whole architecture rests on one fact that may not hold in CSA's tenant:

> A service account is **not a member of the Google Workspace domain**, even when the Cloud project
> and Workspace domain belong to the same organization.

and consequently *"service agents cannot be added to Google Groups unless external members are
allowed."*

The design reuses CSA's existing Google Groups as the resource-entitlement graph — which is what
makes it cheap, because the messy Research Drive hierarchy never has to be reorganised. But that
only works if a service account can **join a CSA group and inherit its Drive ACLs**, and the report
is explicit that this must be validated locally first. It supplies a ten-step test and an exit
criterion.

`[inferred]` **This is the most actionable item across both documents, and it is a precondition
rather than a task.** It is also exactly the case for *run it before you read about it*: the
architecture is elegant, the industry convergence behind it is real, and if external group
membership is disabled in CSA's Workspace — or if propagation is unreliable — then the
entitlement-reuse premise fails and the design needs a different resource-authorization layer.
Nothing downstream should be built until Phase 0 passes.

## The fork this creates for the monorepo plan

`[measured]` Every CSA server today is the opposite shape. `csa-google-workspace` authenticates with
`InstalledAppFlow` and `from_client_secrets`, refreshes per-user tokens, and handles token material
across 22 files. **No CSA server uses a service account anywhere** — the string does not appear in
any of the four `src/` trees.

`[inferred]` So this is not an enhancement to the existing servers. It is **a different product**:

| | today | proposed |
|---|---|---|
| credential | the user's own Google OAuth token | a shared service account |
| custody | the user's machine, in the environment | a server-side credential broker |
| who the vendor sees | the user | the execution principal |
| who may configure it | the user | CSA's control plane |
| transport | local `stdio` | necessarily remote |

The last row matters most. **A credential broker that keeps credentials away from the agent cannot
exist in a local stdio server** — the credential is in the user's environment by design, and the
user is the one running the process. Brokering requires a server the user does not control.

### Which makes this the third independent argument for hosting

Three separate lines of research have now converged on the same conclusion from different
directions:

1. **Platform reach** — Claude Managed Agents accepts only `type: "url"`, so no stdio server can
   attach ([`../managed-agents/`](../managed-agents/)).
2. **Enforcement** — hosting changes *who* the policy binds, not what it says
   ([`../enforcement/`](../enforcement/)).
3. **Credential custody** — brokered execution identities are structurally impossible locally
   (this document).

`[inferred]` That is a stronger case for bringing the hosted work forward than any one of them, and
it is an argument for designing `csa-google-workspace-audit` — the unbuilt server, and the one whose
credential is the most dangerous in the estate — remote-first and brokered from the start.

## What this says belongs in the shared library

`[inferred]` Two things, and both fall under ADR-001's narrow exception for modules with **no
incumbent** rather than needing the ≥95% bar:

**Execution-profile resolution.** The report's §11 Phase 5 extends the same abstraction across
vendors — `google-research-editor`, `github-research-writer`, `zendesk-support-worker` — so an agent
requests a *profile* and a broker resolves it to the current principal. That indirection is
identical across servers by construction; only the resolution target differs. Reimplementing it per
server is how the `_untrusted.py` 1–11% spread happened (ADR-007).

**The provenance record.** §6.5 specifies a minimum audit record: trace, subject, actor, client,
MCP server and tool, requested capability, policy decision, execution profile and principal,
resource id, result with before/after revision. That is a **vocabulary**, and "one vocabulary across
the family" is already a standing principle — a consumer correlating actions across several CSA
servers should not meet a different record shape per server. This is the same class of problem as
the three different answers to *"am I authenticated?"*

## A new synthesis: progressive disclosure is a security control

`[measured]` The report's §8.2 mitigation list for *"MCP policy bug turns into cross-project
access"* ends with: *"use deny-by-default tool exposure and **progressive discovery**."*

`[inferred]` That connects two threads that had been separate here.
[`../orchestration/`](../orchestration/) treats progressive disclosure as a **context-cost**
measure — 150,000 tokens against 2,000. This adds a second rationale: **it is also a blast-radius
measure.** A tool not in context is a tool an injected instruction cannot name.

Which sharpens the Managed Agents finding considerably. That platform **enables all server tools by
default**, so attaching `csa-skilljar` exposes 114 tools to every session. Under the token argument
that is wasteful. Under this argument it is a security decision being made by a default.

## What I would push back on

`[inferred]` **The group-union problem is acknowledged but not solved.** §8.6 notes that adding a
service identity to a widely used group *"may grant it access to more files than operators realize"*,
and the mitigations are *"inventory group-derived access before membership changes"* and
*"periodically enumerate effective access."* Both are real work, neither has named tooling, and the
effective access of a principal across a messy Drive hierarchy is precisely what is hard to
enumerate. The design's cheapness comes from reusing an ACL graph nobody fully understands — which
is a reasonable trade, stated less plainly than the rest of the document states things.

`[inferred]` **It does not mention `cacheScope`**, same as the companion document. A brokered
architecture with shared execution identities and per-actor policy is exactly where an
identity-filtered `tools/list` marked `"public"` leaks one actor's surface to another. See
[`../orchestration/`](../orchestration/).

## What this reconciliation did not do

- **No Google documentation was independently verified.** The service-account/Workspace-domain
  distinction, the external-member constraint, and the Workload Identity Federation path are all
  `[reported]` from the document's own citations.
- **Phase 0 was not run.** The central premise remains untested, which is the point of the section
  above.
- **No vendor platform was checked** — AgentCore outbound auth, Entra Agent ID blueprints, Descope,
  Auth0 Token Vault, Nango. The architectural convergence they are cited for is plausible and
  unverified here; Google's Agent Gateway was verified independently in
  [`../enforcement/`](../enforcement/).
- **AAIF's October 2026 guidance was not read**, only quoted.
- **One loose end was closed rather than left.** Four `subject=` occurrences in
  `csa-google-workspace` looked like they might be `google-auth`'s DWD impersonation parameter. They
  are not: all four are in file-inventory export code (`files.py`, `_inventory.py`) and refer to the
  *subject of a report*. `[measured]` — the server has **no impersonation path**, which confirms the
  fork above rather than softening it.
