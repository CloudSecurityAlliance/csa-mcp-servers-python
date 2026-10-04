# Migration

**The question this answers:** what has to happen, in what order, to move four published servers
into this repository without losing anything — and which steps fail *silently* if skipped.

Nothing below has been done. This is the plan.

---

## What is cheap, measured first

Two fears turned out to be unfounded, and knowing that changes the risk profile.

**Nothing installs these from Git.** Searching the two installer repositories (`DesktopSetup`,
`CSA-Plugins`) for `github.com/CloudSecurityAlliance/csa-*` URLs returns **zero matches**. All 44
references are PyPI package names. Since the package names do not change, **a repository move is
invisible to everyone who installs these servers.**

**The licences already agree.** All four published servers declare `Apache-2.0` in `pyproject.toml`
and ship a matching `LICENSE`. Packages sharing a repository have to agree on this, and they do.
(`csa-google-workspace-audit` has no licence at all — it is specs only. It needs one before it is
built.)

## The two steps that fail silently

Everything else in this plan announces its own failure. These two do not.

### 1. Roughly 2,982 bare `#NN` issue references

| repository | bare `#NN` in files | full URLs | commit messages citing `#NN` |
|---|---|---|---|
| `csa-zendesk` | 337 | 8 | 98 |
| `csa-google-workspace` | 1,770 | 123 | 761 |
| `csa-google-gmail-calendar` | 383 | 7 | 44 |
| `csa-skilljar` | 492 | 48 | 105 |
| **total** | **2,982** | **186** | **1,008** |

The subtlety is worth stating precisely, because the obvious version of this worry is wrong.
Transferring an issue does **not** break links to it — GitHub leaves a redirect at the original
issue URL.

The breakage comes from **the files moving.** A bare `#42` in `csa-zendesk/README.md` means
`csa-zendesk#42`. The moment that file lives at
`csa-mcp-servers-python/packages/csa-zendesk/README.md`, the same `#42` renders against *this*
repository — where issue 42 is a different issue entirely. Silent, wrong, and about three thousand
instances.

**Mitigation, and it must come before any code moves:** mechanically rewrite `#42` to
`CloudSecurityAlliance/csa-zendesk#42`. That form survives both the move and the transfer redirect.
One scripted PR per repository, landed on `main`, with a spot-check — boring, load-bearing, and
irreversible in the wrong order.

The 1,008 references in **commit messages cannot be fixed**, and should not be. History is
immutable, rewriting it would destroy the provenance the move is trying to preserve, and a reader of
`csa-zendesk`'s own log has the context to resolve `#42` correctly.

### 2. Trusted Publishing

Each PyPI project's publisher is bound to a repository **and** a workflow filename. All four servers
already use `release.yml`, so only the repository changes — but all four must be reconfigured on
PyPI before the first post-move release.

Skip it and the failure arrives *after* the tag exists, at the publish step, on a release somebody
is waiting for. See [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/).

## The ordered steps

| # | step | reversible? |
|---|---|---|
| 1 | Create this repository: README, CLAUDE.md, docs, stub package READMEs | yes |
| 2 | **Qualify ~2,982 bare `#NN` references** in the four repos, on `main` | yes |
| 3 | `git filter-repo` each server into `packages/<name>/`, preserving history | yes — originals untouched |
| 4 | One `uv.lock`; resolve the tool and dependency divergence as explicit choices | yes |
| 5 | Run every suite; confirm the two 100% coverage gates still read 100% | — |
| 6 | Reconfigure four Trusted Publishers; prove it with a patch release | yes |
| 7 | Transfer 79 issues; archive the originals as redirect stubs | **no** |
| 8 | Seed `csa-mcp`; convert servers to it **one at a time** | yes |
| 9 | Build `csa-google-workspace-audit` from the tier-3 scaffold | yes |

Steps 1–6 are reversible: the four original repositories still exist and still work. **Step 7 is the
commitment point.** Nothing before it needs to be got right first time.

### On step 3 — history

560 commits across the four (`csa-google-workspace` 375, `csa-skilljar` 77, `csa-zendesk` 73,
`csa-google-gmail-calendar` 35). Preserve all of it with `git filter-repo`, rewriting paths into
`packages/<name>/`, rather than re-importing a snapshot.

The reasoning is not sentiment. For a repository like this one the valuable artifact is often the
*reasoning*, and for these servers much of the reasoning lives in commit messages and in the
1,008 issue citations within them. A snapshot import would discard it.

### On step 4 — the divergence to resolve

Four decisions, currently made differently in different repositories and never compared:

| | zendesk | workspace | gmail-calendar | skilljar |
|---|---|---|---|---|
| `ruff` | `>=0.6` | `>=0.16` | `>=0.16` | `>=0.6` |
| `mypy` | `>=1.11` | `>=2.0` | `>=2.0` | `>=1.11` |
| MCP extra name | **`[server]`** | `[mcp]` | `[mcp]` | `[mcp]` |
| `markdownify` | `>=1.2` | — | **`>=0.13`** | — |

The `markdownify` gap matters most: a major-version spread on a library that DEC-018 mandates
fleet-wide. The extra name matters because it is user-facing and appears in error messages — one of
the four is wrong and it should be `[mcp]`, which means `csa-zendesk` gets a deprecation path rather
than a rename.

One thing that looks like a defect here and **is not**, recorded so it does not get "fixed":
`csa-skilljar` declares an empty `[mcp]` extra while `mcp` sits in its core dependencies. Reading
the file rather than the summary shows it is deliberate and says so —

```toml
# Kept as a no-op alias so `csa-skilljar[mcp]` keeps working for anyone who
# copied it from an early README. mcp itself is now a required dependency.
mcp = []
```

That is a compatibility alias with its reason attached, which is the behaviour we want, not an extra
that installs nothing by accident. It is the model for how `csa-zendesk`'s `[server]` should be
retired: keep the old name working as a documented no-op alias rather than renaming it out from
under anyone.

### On step 5 — the gates that must survive

`csa-skilljar` and `csa-google-gmail-calendar` both hold **100% coverage with branches**, enforced
in `pyproject.toml`. A monorepo makes it easy to accidentally loosen a per-package gate into a
global average, which is exactly the failure mode a coverage gate exists to prevent: a threshold
below the measured number cannot fail.

Per-package gates stay per-package, and step 5 verifies by running them, not by reading the config.

### On step 7 — the irreversible one

Transfer renumbers issues. The 186 full URLs survive by redirect; the bare references are already
qualified by step 2. Labels and milestones do not always carry across a transfer and should be
checked on one issue before all 79 go.

Archive the originals rather than deleting them. A deleted repository takes its redirects with it.

## CI

Path-filtered, so a change to one server does not run four test suites:

```
packages/csa-zendesk/**              → zendesk job
packages/csa-google-workspace/**     → workspace job
packages/csa-mcp/**                  → every job, because everything depends on it
```

Releases dispatch on tag prefix — `csa-zendesk-v0.3.2` — so one workflow serves five packages while
each version stays independent. Versioning stays `0.X.Y` for every package; `1.0.0` is a claim about
API stability made on purpose, not a milestone drifted into.

## What this plan does not cover

- **Which order servers convert to `csa-mcp`** at step 8, beyond one at a time.
- **Whether `csa-mcp` is ever published.** Deliberately not, to begin with — it is a path dependency
  inside the workspace, free to churn while it is being extracted, with no public API promise. It
  gets a PyPI release when a server outside this repository needs it.
- **Branch protection and the required CI gates** for this repository. CSA's public-repo standards
  apply, and cannot be fully satisfied until there is code and CI to gate.
- **Hosting.** Separate posture, separate plan. See [`ARCHITECTURE.md`](ARCHITECTURE.md).
