# TODO

Index of all open work in this repository, one line per item. Detail lives in the linked document;
the index exists so nothing else needs searching.

Created 2026-10-03.

## Blocking the plan

- [ ] **External review of the plan.** Every ADR is `proposed, pending review`. Start at
  [`docs/REVIEW-BRIEF.md`](docs/REVIEW-BRIEF.md) - it leads with the one unresolved contradiction.
- [ ] **Resolve: a published wheel cannot depend on a workspace path.** ADR-003 keeps `csa-mcp`
  unpublished; the servers are published. Three options named in the review brief, none chosen.
  This is the first thing to settle.

## Found while writing the core files

- [ ] **Protect `main`.** Four of four published servers disable force-push with 4-5 required
  checks; this repository has nothing. One setting, on the repository with two copies, one commit
  and no reviewer. [`BACKUP-RESOURCES.md`](BACKUP-RESOURCES.md), [`GOALS.md`](GOALS.md) G4.
- [ ] **~160 claims about other repositories, and nothing checks them** - 91 percentages, 65 line
  counts, 4 line-number-precise call sites. The measurement script is published and deterministic,
  so a check that re-runs it and fails on drift is feasible; it needs the four repositories
  present, which is true after migration. [`OPERATIONAL-RESOURCES.md`](OPERATIONAL-RESOURCES.md).
- [ ] **Four decision-log conventions across four servers**, about to become one tree: a root
  `.md` (`csa-zendesk`, `csa-skilljar`), a file under `docs/` (`csa-google-workspace`), a
  *directory* (`csa-google-gmail-calendar`), plus `docs/DECISIONS.md` here. Converge at migration
  step 4. [`FRICTION.md`](FRICTION.md).

## Migration, when the plan is approved

- [ ] Step 2 - **qualify ~2,982 bare `#NN` references** in the four repositories, before any code
  moves. Scripted, one PR per repository. Silent if done in the wrong order.
- [ ] Step 4 - converge `ruff`, `mypy`, `markdownify` and the `[mcp]`/`[server]` extra name.
- [ ] Step 5 - confirm both 100% coverage gates still read 100% after the move, by running them.
- [ ] Step 6 - **reconfigure four Trusted Publishers** before the first release from here.
- [ ] Step 8 - **a mechanism, not just a rule**, for "convert servers one at a time". Nothing
  currently prevents `csa-mcp` growing past its measured justification.
  [`docs/REVIEW-BRIEF.md`](docs/REVIEW-BRIEF.md) weakness 4.

## Protocol

- [ ] **Measure which revision each server negotiates** with real clients. Currently unknown, and
  nothing downstream is decidable without it. [`docs/PROTOCOL.md`](docs/PROTOCOL.md).
- [ ] **Decide `cache_scope` per list result** - the one protocol item that fails quietly rather
  than loudly, because all four servers filter their tool surface by configuration.
- [ ] Watch for the SDK dropping `elicit_url`'s `elicitation_id`. Trigger recorded; do not
  pre-port. [`WAITING-FOR.md`](WAITING-FOR.md).

## Smaller

- [ ] **`csa-google-workspace-audit` has no licence.** The other four are Apache-2.0.
- [ ] CI and branch protection to CSA public-repo standards, once there is something to gate.
