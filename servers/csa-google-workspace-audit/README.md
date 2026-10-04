# csa-google-workspace-audit

MCP server for read-only auditing of a Google Workspace tenant — who exists, who is privileged, what is shared with whom, and what happened.

> **The code is not here yet.** This directory is a placeholder in a planned monorepo. [CloudSecurityAlliance/csa-google-workspace-audit](https://github.com/CloudSecurityAlliance/csa-google-workspace-audit) holds the specifications. There is no code anywhere yet.

## Status: never built

Specs only. The API surface is enumerated and **390 mutating methods are classified
never-implement**, which is the defining design decision: this server reads a whole tenant and must
be unable to change it.

## Why it is last, and why that matters

This is the **first server that will be built from the tier-3 scaffold** rather than from the
previous server, which makes it the real test of whether the conventions in
[`../../docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) are genuine or merely described.

It is also the likeliest first **hosted** server: it reads an entire tenant, so centralised logging,
policy and an agent-versus-owner distinction earn more here than anywhere else in the fleet. The
constraints already recorded for that — no OAuth DCR, credentials keyed by issuer — are in
[`../../docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md).

## Two things it needs before any code

- **A licence.** It has none. The other four are all Apache-2.0.
- **A decision on admin credentials.** Tenant-wide reads use domain-wide delegation rather than a
  per-user OAuth app, which is where CSA's one-Google-app-per-server rule stops applying.

## Before the code can move here

[`../../docs/MIGRATION.md`](../../docs/MIGRATION.md), in order. The two steps that fail silently if
skipped are qualifying the bare `#NN` issue references **before** any file moves, and reconfiguring
Trusted Publishing **before** the first release from here.

The PyPI name and version do not change.
