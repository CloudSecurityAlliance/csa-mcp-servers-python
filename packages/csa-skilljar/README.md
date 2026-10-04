# csa-skilljar

MCP server for Skilljar — courses, lessons, quizzes, learners, groups and enrolment, across two Skilljar APIs.

> **The code is not here yet.** This directory is a placeholder in a planned monorepo. `csa-skilljar` is published on PyPI at **0.16.1** and developed at [CloudSecurityAlliance/csa-skilljar](https://github.com/CloudSecurityAlliance/csa-skilljar) — file issues and pull requests there.

## Notes for the migration

- Carries a **100% coverage gate**, verified at 100.00% including on Windows. Must survive the move
  intact.
- The only server with **no interactive sign-in by design** — v2 uses the OAuth
  `client_credentials` grant, where the credential *is* the identity, so there is no browser step
  and no person to log in as. Its `check_access` tool is the model the shared status vocabulary
  should learn from rather than replace.
- Holds two independent credentials across two APIs, so *"v2 works but v1 does not"* is a normal
  state rather than a fault. Any shared status type has to be able to express that.
- `backend.py` is **2,239 lines** — the largest single module in the fleet, at 1% similarity to its
  siblings.
- The empty `[mcp]` extra here is a deliberate, commented compatibility alias, **not** a defect. It
  is the pattern `csa-zendesk`'s `[server]` should be retired with.
- The only server with a drift detector (`check_upstream.py`) and upstream-drift issues to show for
  it. Four of five have nothing watching upstream.

## Before the code can move here

[`../../docs/MIGRATION.md`](../../docs/MIGRATION.md), in order. The two steps that fail silently if
skipped are qualifying the bare `#NN` issue references **before** any file moves, and reconfiguring
Trusted Publishing **before** the first release from here.

The PyPI name and version do not change.
