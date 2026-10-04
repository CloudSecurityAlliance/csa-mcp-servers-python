# CI and release

**The question this answers:** what runs on a pull request, what runs on a release, and how that
composes once five packages share one repository.

This pipeline is **derived, not designed.** The four published servers already carry 15 workflow
files between them, and the common spine was measured rather than chosen. Measured 2026-10-04.

---

## What the four servers already run

Seven job names appear in **four of four** servers. That is the spine.

| job | in | what it does today |
|---|---|---|
| `lint` | 4/4 | `ruff` |
| `test` | 4/4 | `pytest` on `ubuntu-latest` |
| `test-windows` | 4/4 | the same suite on `windows-latest` |
| `security` | 4/4 | `bandit` + `pip-audit` |
| `build` | 4/4 | wheel and sdist |
| `release` | 4/4 | tag-triggered |
| `publish` | 4/4 | PyPI Trusted Publishing, OIDC, no tokens |

Uniform across all four, with no exceptions to reconcile:

- **Python 3.14 only.** No version matrix anywhere in the fleet.
- **Two operating systems**, `ubuntu-latest` and `windows-latest`.
- **`mypy`** in all four alongside `ruff`.
- **`fail_under = 100` with `branch = true`** in all four `pyproject.toml` files, and coverage wired
  into CI in all four.

That last one is the fleet's strongest existing property and the easiest thing to lose in a
migration. 100% is the standard because **a gate below the measured number cannot fail**; an
exception is a `# pragma: no cover` carrying its reason at the line, never a lowered threshold.

### And what is genuinely per-package

| job | where | why it does not generalise |
|---|---|---|
| `claims` | `csa-google-workspace` | documentation-drift check against its own docs |
| `drift` | `csa-skilljar` | upstream API drift detector — the only server with one |
| `controls` | `csa-zendesk`, `csa-google-workspace` | control battery over its policy surface |
| `relock`, `auto-merge` | `csa-google-workspace` | Dependabot handling |
| `docs` | `csa-skilljar` | docs build |

Six workflows are `schedule`-triggered and five accept `workflow_dispatch`. The scheduled ones are
drift and audit jobs, not tests, and they stay with their packages.

## The monorepo shape

```
.github/workflows/
├─ tests.yml      path-filtered matrix over packages + the aggregator gate
├─ release.yml    tag-prefix dispatch, one Trusted Publisher per package
└─ scheduled.yml  the per-package drift and audit jobs, on their own cadence
```

### Path filters, and the one thing that must be got right

A change to one server must not run four test suites. The filter is per package:

```
packages/csa-zendesk/**          → the zendesk matrix
packages/csa-google-workspace/** → the workspace matrix
packages/csa-mcp/**              → EVERY package, because everything depends on it
uv.lock, pyproject.toml          → EVERY package
```

> ### The trap: a path-filtered job cannot be a required status check
>
> This is the thing that fails in a way nobody expects. If `test (csa-zendesk)` is a **required**
> check on `main`, and a pull request touches only `packages/csa-skilljar/`, then the zendesk job
> never runs — and GitHub does not treat a required check that never ran as passed. It treats it as
> **pending**, so the pull request can never merge. The repository deadlocks on its own protection.
>
> The fix is an **aggregator**: one job that always runs, depends on every conditional job, and
> passes when each dependency either succeeded or was skipped. Only the aggregator is a required
> check. `csa-skilljar` already has a `gates` job of roughly this shape, so the pattern is in the
> fleet.
>
> This is why `main` currently requires **zero** status checks. Adding the per-package jobs
> directly, which is the obvious thing to do, is the wrong thing to do.

### Coverage composes per package, never globally

Each package keeps its own `fail_under = 100` and is measured against **its own** configuration.

The failure mode to avoid is averaging: a global coverage number over five packages lets one
package's regression hide behind another's headroom, and a 100% gate becomes a 97% gate without
anyone editing a threshold. Coverage also applies **per level** — unit, recording double, live
probe, and the demonstration plan — so a tool missing from `demonstration_plan` has never been seen
to work end to end even at 100% line coverage.

Verification at migration step 5 is *running* the four gates and reading 100.00%, not inspecting the
config.

## Release

Tag-prefix dispatch, so one workflow serves five packages while versions stay independent:

```
csa-zendesk-v0.3.2                → builds and publishes packages/csa-zendesk
csa-google-workspace-v0.56.0      → builds and publishes packages/csa-google-workspace
```

Every package stays on `0.X.Y`. `1.0.0` is a claim about API stability made on purpose, not a
milestone drifted into.

### Trusted Publishing is the migration's quiet failure

Each PyPI project's publisher is bound to a **repository and a workflow filename**. All four
servers already use `release.yml`, so only the repository changes — but all four must be
reconfigured on PyPI *before* the first release from here, or the failure arrives after the tag
exists, at the publish step, on a release somebody is waiting for.

OIDC, no registry tokens. This matches the official MCP reference monorepo, which states
*"OIDC trusted publishing from CI — no registry tokens"* — see
[`PRIOR-ART.md`](PRIOR-ART.md).

A stored PyPI token anywhere in this flow would defeat the point; the publish job's identity is the
workflow, and that is what the PyPI configuration trusts.

### `csa-mcp` is not published

It is a workspace path dependency (ADR-003), so it has no Trusted Publisher and no release tag.
**And a published wheel cannot depend on a workspace path** — the unresolved contradiction in
[`REVIEW-BRIEF.md`](REVIEW-BRIEF.md). Whatever resolves it changes this section, which is why the
release design is not final.

## What this repository has today

**No CI at all**, and that is correct for now — there is no code to gate. The branch rule requires
zero status checks for the same reason.

The order is: plan reviewed → code migrated → workflows added → **then** the aggregator becomes a
required check. Adding a required check before the job exists is the deadlock above, arrived at from
the other direction.

## What is not decided

- **Whether `uv` or `pip` drives CI.** The servers predate the workspace; a uv workspace makes
  `uv sync` the obvious entry point, but none of the four currently uses it in CI.
- **Whether the scheduled jobs stay four separate workflows or become one matrix.** They have
  different cadences and only one server has a drift detector, so merging them may be premature.
- **Caching strategy.** Not measured, not designed. A monorepo makes cache keys a real question
  rather than an afterthought.
- **Whether `csa-google-workspace`'s `relock` and `auto-merge` survive.** One lockfile for five
  packages changes what Dependabot does, and that was not investigated.
