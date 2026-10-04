# csa-google-workspace

MCP server for Google Docs, Sheets, Slides and Drive — comments, content, permissions, and export.

> **The code is not here yet.** This directory is a placeholder in a planned monorepo. `csa-google-workspace` is published on PyPI at **0.55.1** and developed at [CloudSecurityAlliance/csa-google-workspace](https://github.com/CloudSecurityAlliance/csa-google-workspace) — file issues and pull requests there.

## Notes for the migration

- The largest of the five by history: **375 commits**, and 1,770 bare `#NN` issue references plus
  123 full URLs. Step 2 of [`../../docs/MIGRATION.md`](../../docs/MIGRATION.md) is mostly this
  repository.
- Holds one of the two `elicit_url` call sites that depend on `elicitationId` and
  `notifications/elicitation/complete`, both **removed in protocol revision `2026-07-28`**. Nothing
  is broken today; see [`../../docs/PROTOCOL.md`](../../docs/PROTOCOL.md) for the recorded trigger.
- Shares the 58–60% OAuth trio (`_auth_flow`, `_login`, `_logging`) with
  `csa-google-gmail-calendar`. That tier is reconciled before it is extracted, never during.
- `backend.py` is 1,173 lines at 1% similarity to its siblings — correctly vendor-specific, and it
  stays here.

## Before the code can move here

[`../../docs/MIGRATION.md`](../../docs/MIGRATION.md), in order. The two steps that fail silently if
skipped are qualifying the bare `#NN` issue references **before** any file moves, and reconfiguring
Trusted Publishing **before** the first release from here.

The PyPI name and version do not change.
