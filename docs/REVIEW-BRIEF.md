# Review brief

**If you are reviewing this plan, start here.**

This repository contains a plan and no code. The plan proposes moving four published Python MCP
servers into a monorepo, extracting a small shared library from them, and building a fifth server
from the result.

What follows is written to be attacked. It names the weak points rather than waiting for you to find
them, because a review that rediscovers known problems spends its budget badly.

---

## The one unresolved contradiction

**ADR-003 says `csa-mcp` is not published to PyPI. The servers are published to PyPI. A published
wheel cannot depend on a workspace path.**

This is a genuine conflict and it was found while writing the decision, not resolved. Three ways
out, none chosen:

1. **Vendor `csa-mcp` into each wheel at build time.** Keeps it unpublished and keeps wheels
   installable, at the cost of build complexity and four copies on disk at install time — which is
   uncomfortably close to the duplication being eliminated.
2. **Publish `csa-mcp` after all**, accepting the API-stability obligations ADR-003 declines.
3. **Do not let published servers depend on it yet** — extract only into servers' *internal* use and
   defer the dependency until a release where publishing `csa-mcp` is acceptable.

Option 3 may collapse into "do nothing", which would undermine ADR-001. **This is the first thing to
review.**

## What the plan claims, and how to check it

Every number in these documents is reproducible. Do not take them on trust.

| claim | where | how to verify |
|---|---|---|
| `_markdown.py` is 96% identical, 19 changed lines, all docstring | [`EVIDENCE.md`](EVIDENCE.md) | `diff` the two files in `csa-zendesk` and `csa-google-gmail-calendar` |
| `backend.py` is 1% similar across four servers | [`EVIDENCE.md`](EVIDENCE.md) | the script is in that document; re-run it |
| ~2,982 bare `#NN` references | [`MIGRATION.md`](MIGRATION.md) | `grep -rhoE '(^\|[^A-Za-z0-9/_-])#[0-9]{1,4}\b'` per repo |
| Nothing installs these from Git | [`MIGRATION.md`](MIGRATION.md) | grep `DesktopSetup` and `CSA-Plugins` for `github.com/CloudSecurityAlliance/csa-` |
| SDK negotiates `2025-03-26` by default | [`PROTOCOL.md`](PROTOCOL.md) | `python -c "import mcp.types as t; print(t.DEFAULT_NEGOTIATED_VERSION)"` |
| `server/discover` comes for free | [`PROTOCOL.md`](PROTOCOL.md) | construct a bare `MCPServer` and inspect `_lowlevel_server._request_handlers` |
| All four licences are Apache-2.0 | [`README.md`](../README.md) | check each `pyproject.toml` and `LICENSE` |

If a number is wrong, the conclusion resting on it probably is too. Say which.

## Known weaknesses, in order of how much they worry me

1. **The contradiction above.**
2. **ADR-001 overrides a dated, reasoned decision** (`ROADMAP.md`, 2026-09-25, "foundation last").
   The original reasoning is good. Judge whether "four built servers instead of three, and the
   duplication is now measured" genuinely changes it, or whether that is motivated reasoning
   dressed in a similarity table.
3. **Step 2 of the migration is ~3,000 mechanical edits across four public repositories** and must
   land before any code moves. It is boring, load-bearing, and wrong-ordered is silent. Is there a
   cheaper correct approach? Is there a reason not to rewrite them at all?
4. **"Convert servers one at a time" (step 8) is the discipline most likely to be compressed** under
   time pressure. If `csa-mcp` grows past the four seeded modules before a second server has
   consumed them, the plan has reproduced the failure it cites (`CSA-MCP-Core`: a foundation with
   one consumer, moving faster than it). There is no mechanism in this plan that *prevents* that —
   only a stated rule. Should there be one?
5. **Issue transfer (step 7) is irreversible** and the plan leans on it being last. Check that
   nothing earlier depends on it.
6. **Tier 3 (convention, not code) will look like under-engineering** to a reviewer who prefers
   abstractions. The measurement is the argument: 10–15% similarity. If you disagree, argue with the
   number.
7. **The protocol revision the servers actually speak is unknown**, not measured. Several decisions
   downstream of [`PROTOCOL.md`](PROTOCOL.md) would change if the answer is surprising.

## What the research changed, so a reviewer can check the reasoning

[`PRIOR-ART.md`](PRIOR-ART.md) was written after the architecture and **altered it in three places**
rather than confirming it. That is worth checking, because a prior-art document that only agrees
with the plan it follows is not evidence.

1. **The layout changed.** Cloudflare's MCP monorepo separates `apps/` (servers) from `packages/`
   (shared code); everything here had been under one `packages/`. Adopted as `servers/` +
   `packages/` — the same structural split, with the accurate noun for packages we publish rather
   than Workers we deploy.
2. **"One repository per language" was reopened.** The official reference monorepo mixes TypeScript
   and Python in one tree. See [`ESTATE.md`](ESTATE.md) — not decided, and it does not block this
   repository.
3. **The DCR warning became sourced rather than asserted**, and the secondary literature turned out
   to be a revision behind on it.

Two findings strengthened existing decisions instead: the official monorepo has **no shared library
at all**, which supports ADR-001's narrow bar; and the specification says a stdio server
**SHOULD NOT** use OAuth and should take credentials from the environment, which is what CSA already
does.

## Questions I would most like answered

- Does the ≥95%-or-no-incumbent bar in ADR-001 hold up, or is it a rule invented to make the answer
  come out at four modules?
- Is a uv workspace the right mechanism, or does it buy less than claimed? Specifically: does one
  lockfile actually prevent the drift measured, or just relocate it?
- `cache_scope` on policy-filtered `tools/list` results is identified as the one protocol item that
  can be *quietly* wrong. Is that assessment right, and is there a test that would catch it?
- Is there a category of duplication the method in [`EVIDENCE.md`](EVIDENCE.md) cannot see? It
  compares same-named files only, so two servers solving one problem in differently-named modules
  are invisible to it. How much is hiding there?
- Should `csa-google-workspace-audit` be built *before* the migration rather than after, as the
  first consumer of the scaffold and a test of whether the conventions are real?
- **One monorepo per language, or one for everything?** The official reference monorepo mixes
  TypeScript and Python. The counter-argument is that CSA's TypeScript servers are Workers-deployed
  rather than npm-published, so they share no build, release or runtime with a PyPI package.
  [`ESTATE.md`](ESTATE.md) states both sides and settles neither.
- **Is the CI aggregator pattern right?** [`CI-CD.md`](CI-CD.md) argues that path-filtered jobs
  cannot be required status checks directly — a required check that never runs reads as *pending*
  forever and deadlocks the branch rule — so one always-runs aggregator job becomes the only
  required check. Is there a cleaner approach?

## Deliberately absent

Not oversights:

- **No code.** No `pyproject.toml`, no workflows, no `uv.lock`, no source. Those encode decisions
  not yet approved, and a half-built skeleton is harder to review than a plan.
- **No `csa-mcp` implementation**, not even stubs. Its contents are the subject of ADR-001.
- **No CI.** Nothing to gate yet; the plan is in [`CI-CD.md`](CI-CD.md) and `main` requires zero
  status checks until the jobs exist. Branch protection itself **is** now configured — PR required,
  0 approvals, force-push blocked — see [`../BACKUP-RESOURCES.md`](../BACKUP-RESOURCES.md).
- **No timeline.** Sequencing is specified; dates are not.
- **No TypeScript.** CSA's Cloudflare Workers MCP servers are a separate assessment with a different
  SDK and a different deprecation exposure.
- **`csa-google-workspace-audit` has no licence.** Noted rather than fixed; it needs one before it is
  built.

## Context a reviewer may lack

The engineering practice these decisions answer to is internal to CSA
([CINO-Platform-Engineering](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering),
links will not resolve for everyone). The parts load-bearing here:

- **Do not create structure in advance of the experience that would fill it.** The test is whether
  you can name the projects behind each item. ADR-001 lives or dies on this.
- **Do not build a foundation before its second consumer.** `CSA-MCP-Core` is the in-house
  counter-example.
- **Run it before you read about it.** Dependency failures that cost real time were invisible in
  READMEs. It is why these documents lead with measurements.
- **A rejected alternative carries the reasoning**, and must distinguish "wrong" from "unwarranted
  here".
- **Coverage gates are per-package and 100% is the standard**, because a threshold below the
  measured number cannot fail.

You are not required to agree with any of it. If a principle is being applied where it does not fit,
that is a finding worth more than a correction to a number.
