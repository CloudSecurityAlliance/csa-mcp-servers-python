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

## `main` is protected, as of 2026-10-04 — and the first attempt did not work

| repository | `main` protection |
|---|---|
| `csa-zendesk` | protected, 5 required checks, force-push disabled |
| `csa-google-workspace` | protected, 4 required checks, force-push disabled |
| `csa-google-gmail-calendar` | protected, 4 required checks, force-push disabled |
| `csa-skilljar` | protected, 5 required checks, force-push disabled |
| **`csa-mcp-servers-python`** | protected: PR required, **0** approvals, force-push and deletion blocked, enforced on admins |

It was unprotected at creation, which was CINO-PE#98 repeating — that issue found `main`
unprotected on a repository whose value was its history. The pattern is that protection gets
configured when a repository starts shipping artifacts, and a repository whose output is
*reasoning* never crosses that threshold.

### Why this is recorded rather than just fixed

**The first configuration read back as correct and was not.** It was applied with
`enforce_admins: false`, on the reasoning that a solo maintainer should not be able to lock
themselves out. The read-back showed `PR required: true`. A direct push to `main` then **succeeded**
anyway, because `enforce_admins: false` exempts the repository owner from the rule — so the PR
requirement applied to everyone except the only person working here.

Re-applied with `enforce_admins: true`, the same push is refused —
`Changes must be made through a pull request` — and a force-push is refused with
`GH006: Cannot force-push to this branch`. Both verified by attempting them.

The cost is deliberate and small: **0 required approvals** means a pull request can be opened and
merged immediately by one person, so the only thing enforced is that changes arrive *as* a pull
request. That matches the standing rule for this work — land through a PR, never a direct commit to
`main` — and it is what makes the force-push protection above real rather than advisory.

To undo, if it ever gets in the way:

```bash
gh api -X PATCH repos/CloudSecurityAlliance/csa-mcp-servers-python/branches/main/protection/enforce_admins
```

**The general lesson:** a protection setting that has not been tested by attempting the thing it
forbids is a claim, not a control. Reading the configuration back confirms what was *sent*, not
what is *enforced*.

## What recovery looks like

Git, from either copy, for anything committed. There is no state outside Git - no database, no
hosted artifact, no credential to re-provision, nothing to restore in order.

The gap is not recovery. It is **detection**: with no branch protection, no CI and no second
reader, a rewritten claim in a 1,575-line plan would not be noticed, and the numbers it replaced
could no longer be recomputed.
