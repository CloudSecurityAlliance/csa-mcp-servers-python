# csa-zendesk

MCP server for Zendesk — tickets, comments, attachments, and a policy-gated write surface.

> **The code is not here yet.** This directory is a placeholder in a planned monorepo. `csa-zendesk` is published on PyPI at **0.3.1** and developed at [CloudSecurityAlliance/csa-zendesk](https://github.com/CloudSecurityAlliance/csa-zendesk) — file issues and pull requests there.

## Notes for the migration

- The MCP extra is called **`[server]`** here and `[mcp]` in the other three. It is user-facing and
  appears in error messages. ADR-002 converges on `[mcp]`, with `[server]` retained as a documented
  no-op alias rather than renamed out from under anyone — the pattern `csa-skilljar` already uses.
- `markdownify` is pinned `>=1.2` here and `>=0.13` in `csa-google-gmail-calendar` — a
  major-version gap on a library DEC-018 mandates fleet-wide. One `uv.lock` forces this to be
  decided.
- `_markdown.py` here is the **origin** of the 96%-identical copy in
  `csa-google-gmail-calendar`. Its docstring records a measurement worth preserving through
  extraction: Zendesk's own plain-text rendering is a naive tag strip, and all five CSS-hidden
  probes survived into `body` while the CSS that revealed them did not.
- `ruff>=0.6` / `mypy>=1.11` here against `>=0.16` / `>=2.0` in the two Google servers.

## Before the code can move here

[`../../docs/MIGRATION.md`](../../docs/MIGRATION.md), in order. The two steps that fail silently if
skipped are qualifying the bare `#NN` issue references **before** any file moves, and reconfiguring
Trusted Publishing **before** the first release from here.

The PyPI name and version do not change.
