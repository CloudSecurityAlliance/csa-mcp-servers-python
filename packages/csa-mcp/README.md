# csa-mcp

The shared library for CSA's Python MCP servers. **It does not exist yet, anywhere.**

> This is the only package here that is not a migration. There is no repository to move it from —
> it will be *extracted* from the four published servers, and the evidence for what it should contain
> is in [`../../docs/EVIDENCE.md`](../../docs/EVIDENCE.md).

## It starts at about 300 lines, and the bar is explicit

ADR-001 in [`../../docs/DECISIONS.md`](../../docs/DECISIONS.md): a module enters this package only
when it is **already duplicated at ≥95%**, or when it has **no implementation in any server at all**.

| module | provenance | why it qualifies |
|---|---|---|
| `markdown.py` | extracted | 96% identical across two servers; 19 changed lines, all docstring |
| `oauth_success_page.py` | extracted | 95% identical, 68 lines each |
| `discover.py` | new | the `server/discover` handler and live self-test — no incumbent to diverge from |
| `status.py` | new | one status vocabulary; four servers currently give three answers |

## What it must never contain

`backend.py`, `policy.py`, `_schemas.py`, `client.py`, `exceptions.py`, `_config.py` — measured at
1–7% similarity and 236–2,239 lines each. That is vendor surface and it stays with its vendor.

Most of the fleet's code lives there, which is why this package stays small no matter how long it is
worked on. **Anyone proposing to grow it should name the measured number that justifies it.**

## The second tranche, after reconciliation

The OAuth trio — `_auth_flow` (59%), `_login` (58%), `_logging` (60%) — belongs entirely to the two
Google servers. Fifty-eight percent is the number to be most careful about: close enough that
sharing looks obvious, different enough that adopting either copy silently discards the other's
behaviour. Reconcile as a decision first.

## The rule that keeps this honest

**Nothing enters this package until a second server has actually consumed it.** Not "will
consume" — has.

This is the rule `CSA-MCP-Core` broke: it centralised auth, rate limiting, observability and the
error envelope while having exactly one consumer, and was pushed more often than the server it
served. A foundation moving faster than its only consumer is being built on theory.

## Not published, and that is unresolved

ADR-003 keeps this unpublished — a workspace path dependency, free to churn, no API stability
promise. **A published wheel cannot depend on a workspace path**, and that contradiction is the first
item in [`../../docs/REVIEW-BRIEF.md`](../../docs/REVIEW-BRIEF.md). It is not resolved.
