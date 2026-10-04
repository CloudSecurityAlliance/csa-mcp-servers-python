# csa-google-gmail-calendar

MCP server for Gmail and Google Calendar — messages, threads, drafts, labels, events and free/busy.

> **The code is not here yet.** This directory is a placeholder in a planned monorepo. `csa-google-gmail-calendar` is published on PyPI at **0.5.1** and developed at [CloudSecurityAlliance/csa-google-gmail-calendar](https://github.com/CloudSecurityAlliance/csa-google-gmail-calendar) — file issues and pull requests there.

## Notes for the migration

- Carries a **100% coverage gate with branches** — as do all four published servers, measured
  2026-10-04. Per-package gates stay per-package through the migration; step 5 verifies by running
  them, not by reading the config. A threshold below the measured number cannot fail, which is the
  whole point of the gate.
- Holds the second `elicit_url` call site affected by the `2026-07-28` removals.
- Its `_markdown.py` is the tracked copy of `csa-zendesk`'s, carrying the provenance comment a
  deliberate copy was required to have — *"Ported from csa-zendesk's `_markdown.py` (same problem,
  same fix)"*. Diffing the two shows 19 changed lines, **all in the docstring**. This is the clearest
  extraction candidate in the fleet.
- The sharpest content-safety surface of the five: mail bodies are untrusted input from outside the
  organisation.

## Before the code can move here

[`../../docs/MIGRATION.md`](../../docs/MIGRATION.md), in order. The two steps that fail silently if
skipped are qualifying the bare `#NN` issue references **before** any file moves, and reconfiguring
Trusted Publishing **before** the first release from here.

The PyPI name and version do not change.
