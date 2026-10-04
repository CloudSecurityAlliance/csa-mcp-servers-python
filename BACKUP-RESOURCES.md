# Backup resources

**The question this answers:** if this repository were lost or silently rewritten, what would be
gone, and what would notice?

## The inversion: this is not "just a plan"

The instinct is that a documentation repository at plan stage needs no backup story - it can be
rewritten. That is wrong here for a specific reason.

The valuable content is **a measurement of four other repositories as they stood on 2026-10-03**:
91 similarity percentages, 65 line counts, a diff characterised down to "19 changed lines, all in
the docstring". Those four repositories are live and will change. **Once they do, this repository
is the only record of what they looked like**, and the measurement cannot be re-derived from a
later state.

So the destructive act is not deletion - a deletion is obvious. It is a **force-push or a silent
replacement** of a document whose numbers nobody can independently recompute.

## What exists, and where

| copy | state |
|---|---|
| GitHub, `CloudSecurityAlliance/csa-mcp-servers-python` | 1 commit, 0 forks, 0 watchers |
| one local clone | the machine it was authored on |

That is **two copies and one commit**, with no third party holding either.

## And `main` is unprotected

| repository | `main` protection |
|---|---|
| `csa-zendesk` | protected, 5 required checks, force-push disabled |
| `csa-google-workspace` | protected, 4 required checks, force-push disabled |
| `csa-google-gmail-calendar` | protected, 4 required checks, force-push disabled |
| `csa-skilljar` | protected, 5 required checks, force-push disabled |
| **`csa-mcp-servers-python`** | **not protected** |

Four of four published servers disable force-push on `main`. This repository does not, so the one
destructive act that matters here is **entirely unopposed**, on the repository with the fewest
copies and no reviewer.

This is CINO-PE#98 repeating: that issue found `main` unprotected on a repository whose value was
its history. The pattern is that protection gets configured when a repository starts shipping
artifacts, and a repository whose output is *reasoning* never crosses that threshold.

**It is one setting.** See [`TODO.md`](TODO.md), and [`GOALS.md`](GOALS.md) G4.

## What recovery looks like

Git, from either copy, for anything committed. There is no state outside Git - no database, no
hosted artifact, no credential to re-provision, nothing to restore in order.

The gap is not recovery. It is **detection**: with no branch protection, no CI and no second
reader, a rewritten claim in a 1,575-line plan would not be noticed, and the numbers it replaced
could no longer be recomputed.
