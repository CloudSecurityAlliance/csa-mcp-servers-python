# Where policy actually gets enforced

**Status:** first pass, 2026-10-04. Follows [`../METHOD.md`](../METHOD.md) — stated best practice
first, then what the big players ship.

**The question:** vendors do not offer fine-grained per-agent permissions — not Google (Gmail,
Calendar, Docs, Drive), not Skilljar, not Airtable. So the controls have to live in the MCP server.
On a local `stdio` server the user owns the process, so is that enforcement or only a strong
suggestion? And what does everyone else do about it?

---

## The premise is correct, and it is now sourced rather than assumed

`[measured]` Google's own Agent Gateway documentation, read 2026-10-04, says the quiet part:

> Agent Gateway ... effectively creating a governance layer **above** SaaS APIs, though the
> underlying APIs **still lack true per-agent granularity**.

That is the vendor with the most to gain from fixing it in the API, describing a product that works
around it instead. Treat per-agent IAM in vendor APIs as **not coming**, and design for a layer
above.

## But "strong suggestion" undersells local policy, because it names the wrong adversary

This is the central finding and it reframes the question.

A local server runs as the user, with the user's credential. **Policy there cannot bind the user —
and it was never the thing protecting the vendor from the user.** The user can already open Gmail in
a browser. Nothing an MCP server does changes what a human with valid credentials may do.

What local policy binds is **the agent acting on the user's behalf** — including an agent that has
been prompt-injected by content it just read. Against *that* adversary local policy is real
enforcement, for a structural reason:

`[measured]` **CSA policy is set in the environment, never through a tool.** 40 distinct `CSA_*`
environment variables across the fleet, and three of four servers tell the model in their
instructions that the policy *"cannot be changed from here"*. The model cannot edit an environment
variable or restart a process. The user can — but the user is not who the control is for.

So the honest framing is not "advisory versus enforcing". It is:

| control | binds the model? | binds the user? | defends against |
|---|---|---|---|
| in-server policy, local | **yes** | no | the agent: bad tool choice, prompt injection |
| client/host consent + sandboxing | partly | partly (they click) | a malicious or buggy *server* |
| hosted server or gateway | yes | **yes** | the agent **and** the user |

### The specification agrees, by omission and by assertion

`[measured]` The security best-practices document has a **"Local MCP Server Compromise"** section,
and it is entirely about malicious *servers* attacking the user — not about users circumventing
their own server's policy. Its mitigations are client-side: a consent dialog showing the exact
command (`MUST`), sandboxing, restricted filesystem access, least privilege.

There is **no section** on enforcing policy against the local user, because it is not a coherent
goal. The absence is the answer.

And where the spec does speak to server-side policy, it is emphatic. Under scope minimization, it
lists as a **common mistake**:

> Treating claimed scopes in token as sufficient **without server-side authorization logic**

So server-side policy is required *in addition to* OAuth scopes, not as a substitute for the IAM the
vendor does not offer.

## What the big players actually ship

`[measured]` **Google — Agent Gateway** (Gemini Enterprise Agent Platform). An explicit enforcement
layer, in two directions: client-to-agent ingress and **agent-to-anywhere egress**, the latter
covering *"external tools, MCP servers, and APIs"*. It parses MCP traffic to extract attributes.
Controls: IAM Unified Access Policies binding agent identity to resources, **default-deny** (*"all
connections are blocked unless an explicit IAM policy grants access"*), an Agent Registry of
approved agents and endpoints, mTLS, **Model Armor** scanning prompts and outgoing tool payloads for
prompt injection and data leakage, *"Semantic Governance Policies"* enforcing business rules at
runtime *"to prevent agents from taking unintended actions"*, and network-layer telemetry for all
interactions.

`[reported]` **The gateway pattern is the dominant enterprise answer** as of late 2026 — a proxy in
front of many servers doing authentication, authorization, audit and policy. Commercial entrants
offer managed detection for prompt injection, secrets and PII, with one notable design detail:
**Off / Monitoring / Enforcing modes**, so a policy is observed before it blocks. That staging idea
is worth stealing regardless of whether a gateway is.

`[measured]` **A default-deny proxy for local servers exists** — `sw1tchdev/mcp-restrictor`
describes itself as *"a policy-based, default-deny MCP proxy that controls which tools clients can
discover and invoke on existing stdio servers."* So the gateway pattern has been pulled down to the
laptop by someone who wanted the local half enforced too.

`[reported]` One contrary position worth noting rather than dismissing: *"MCP Server Governance:
Enforce at the Client, Not the Registry."* The argument is that allowlisting which servers exist is
weaker than controlling what the client may invoke. Unverified, but it points at the same gap CSA
has.

## Where CSA already stands, measured

`[measured]` **1,838 lines of policy across four servers** — `csa-google-workspace` 643,
`csa-zendesk` 543, `csa-skilljar` 416, `csa-google-gmail-calendar` 236. Allowlists, capability
gating, refusal paths. A capability the deployment has not enabled **does not appear as a tool at
all**, which is stronger than a tool that exists and refuses.

That is substantially the "governance layer above the vendor API" the gateway products sell, already
written, already per-vendor, and already env-configured so the model cannot reach it.

### The gap, and it is the uncomfortable one

`[measured]` **The control that actually defends against the real adversary is the least consistent
thing in the fleet.**

| server | untrusted-content handling | lines |
|---|---|---|
| `csa-zendesk` | `csa_zendesk/_untrusted.py` — at package root | **404** |
| `csa-google-gmail-calendar` | `csa_google_gmail_calendar/mcp/_untrusted.py` | 142 |
| `csa-google-workspace` | `csa_google_workspace/mcp/_untrusted.py` | 119 |
| `csa-skilljar` | **no module** — handled inline, 7 files mention it | — |

Pairwise similarity of the three dedicated modules: **1%, 2%, 11%.** Four servers, four independent
implementations, one of them at a different architectural layer than the other two, and one with no
module at all.

Compare: `_markdown.py` is 96% shared, `auth.py` 16%, `policy.py` 3%. **The prompt-injection
boundary is less consistent than any of them** — and it is the only control on this list whose
failure lets injected content act with the user's credential.

`[inferred]` This is a **missed abstraction rather than genuine vendor variation**, and that
distinction matters because it reverses an earlier judgement in this repository. `SECURITY-RESOURCES.md`
previously recorded `_untrusted.py` at 11% as *"explicitly not an extraction candidate"*, on the same
reasoning that keeps `server.py` at 10% out of the shared library.

The test that separates them: **is there a single correct behaviour?** For *"what should my CLI
do?"* — legitimately varies per server. For *"how do I mark vendor content so a model treats it as
data and not instructions?"* — there is one right answer, and four servers each found their own. Low
similarity is evidence of divergence in the first case and of a missing shared primitive in the
second.

So the wrapping mechanism belongs in `csa-mcp`; the vendor content *shapes* stay with their vendors.
That is a correction to ADR-004's reach, recorded in [`../../docs/DECISIONS.md`](../../docs/DECISIONS.md).

### And the surface is large

`[measured]` **241 tool registrations** across four servers, all commonly connected at once. Every
one is a path an injected instruction could try. `destructive_hint` appears 37 times, `confirm=`
9 times, `dry_run` 3 — so human-in-the-loop gating exists but is thin relative to the surface.

## What this means for the plan

| finding | consequence |
|---|---|
| Vendor per-agent IAM is not coming | design for a layer above; stop waiting |
| Local policy binds the model, not the user | **it is not a weaker control, it is a differently-scoped one** — say so in the docs rather than apologising for it |
| Policy is env-only, three servers say so | keep that property; it is what makes local policy real |
| Hosted changes *who* it binds, not *what* it says | the same `policy.py` serves both; an argument for policy in the server rather than only in a gateway |
| `_untrusted` is 1–11% across four servers | the wrapping primitive goes in `csa-mcp`; **reverses** the earlier not-an-extraction-candidate call |
| Off / Monitoring / Enforcing staging | adopt the idea for any new policy, local or hosted |
| Token passthrough is `MUST NOT` | a hosted CSA server holds its own upstream credential; it cannot forward the client's |

## What this does not establish

- **No gateway product was tested**, only documented. The Off/Monitoring/Enforcing design is
  `[reported]`.
- **Microsoft's and AWS's enforcement stories were not examined** — this looked at Google's because
  it is the vendor CSA depends on most. AWS and Microsoft both have agent-governance offerings that
  were not read.
- **No measurement of whether CSA's policy actually holds** under an injection attempt. The fleet
  has `destructive_hint` annotations and allowlists; whether a determined injected instruction can
  route around them is untested, and that is a real gap rather than a theoretical one.
- **Nothing about cost.** A gateway is infrastructure, and no comparison was made.
- **The contrary "enforce at the client" position is unverified** tier 2.
