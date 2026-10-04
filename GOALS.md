# Goals

What *done* means for this repository, and which of these are not met.

This repository is at plan stage. "Done" has two meanings and they are sequential: first the plan
is reviewed and decided, then the migration it describes is complete. The properties below are
about the first.

| | property | met? |
|---|---|---|
| G1 | **A reviewer with no prior context can assess the plan.** [`docs/REVIEW-BRIEF.md`](docs/REVIEW-BRIEF.md) names the weak points, lists the open questions, and says what is deliberately absent | yes |
| G2 | **Every number is reproducible.** The measurement method is published in [`docs/EVIDENCE.md`](docs/EVIDENCE.md), and the brief gives a one-line check per claim | yes |
| G3 | **Claims about other repositories are checkable by something other than a person.** ~160 of them, 4 citing line numbers | **no** |
| G4 | **`main` cannot be rewritten.** PR required, force-push and deletion blocked, enforced on admins — verified by attempting both | yes, 2026-10-04 |
| G5 | **The decisions are decided.** ADR-001 to ADR-005 are all `proposed, pending review` | **no** |
| G6 | **One decision-log convention across the fleet.** Four servers use four different shapes | **no** |
| G7 | **Claims about the outside world are dated, tagged and reproducible.** `research/` carries dates, `[measured]`/`[reported]`/`[inferred]` tags, and a script that re-derives every number | yes, 2026-10-04 |

## Why the unmet ones are stated rather than fixed

G3 was a finding from writing [`OPERATIONAL-RESOURCES.md`](OPERATIONAL-RESOURCES.md) and has a
line in [`TODO.md`](TODO.md). **G4 was the same and is now met** — see
[`BACKUP-RESOURCES.md`](BACKUP-RESOURCES.md), including why the first attempt at it silently did not
work.

G5 is the point of the current stage, not a defect: the repository exists so the plan can be
reviewed before anything moves. An ADR marked `accepted` before review would be the defect.

G6 is a fleet-wide finding this repository happens to have surfaced, and it becomes urgent at
migration rather than now - see [`FRICTION.md`](FRICTION.md).

## What is explicitly not a goal

- **Not a framework.** The convention tier ships documentation and a scaffold, never importable
  code (ADR-004). Growth of `csa-mcp` past its measured justification is a failure, not progress.
- **Not a new home for issues yet.** The five servers' own repositories remain the place to file
  until migration step 7.
