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

- [x] **Protect `main`** — done 2026-10-04. PR required, 0 approvals, force-push and deletion
  blocked, enforced on admins. Took two attempts: the first used `enforce_admins: false` and
  **permitted a direct push to `main` while reading back as correct**. Both rules verified by
  attempting them. [`BACKUP-RESOURCES.md`](BACKUP-RESOURCES.md), [`GOALS.md`](GOALS.md) G4.
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

## Opened by the prior-art research (2026-10-04)

- [ ] **Re-run `research/fleet-survey/measure.py`** when a protocol revision ships, when `ext-auth`
  moves (static since 2026-06-18), or before acting on the lockfile or Google-granularity questions
  — both rest on numbers in that survey.
- [ ] **The migration window is dated.** Four of six CSA MCP repos are under 40 days old, so the
  drift appeared in a burst rather than accumulating; the cost of consolidating rises weekly.
  [`research/fleet-survey/TIMELINE.md`](research/fleet-survey/TIMELINE.md).

- [ ] **Decide: one `uv.lock` or one per server?** ADR-002 argued one; its appended correction says
  AWS runs 62 Python MCP servers with none, sharing root tooling config instead. ADR-006 takes the
  root-config half independently so this is not blocking.
- [ ] **Adopt root tooling config** — `.ruff.toml`, `.python-version`, `.pre-commit-config.yaml`,
  `.gitleaks.toml` (ADR-006). This is the direct fix for the `ruff`/`mypy` floor divergence, and it
  is cheaper than the lockfile.
- [ ] **Decide: three Google servers, or one with toolsets?** 241 tools across four servers, 109 of
  them Google, and the 58–60% OAuth duplication exists *because* of the split. Trade-off is context
  pressure against credential blast radius. [`docs/PRIOR-ART.md`](docs/PRIOR-ART.md) §5.
- [ ] **Consider per-session toolset selection.** CSA already gates tools by configured capability —
  an unenabled capability does not appear as a tool at all. What is missing is per-session selection
  and runtime discovery, which is what GitHub's `--dynamic-toolsets` provides.

- [ ] **Decide: one monorepo per language, or one for everything?** The official MCP reference
  monorepo mixes TypeScript and Python in one tree; CSA's TypeScript servers are Workers-deployed
  rather than npm-published. [`docs/ESTATE.md`](docs/ESTATE.md) states both sides.
- [ ] **Read the Enterprise-Managed Authorization extension** before designing hosted agent
  delegation — it is *stable* in `modelcontextprotocol/ext-auth` and is the nearest thing to the
  "user authorises, then nominates which agents may use it" model. Listed, not read.
- [ ] **The Client Credentials extension is in draft** and `csa-skilljar` already uses that grant.
  Check its hosted behaviour against the extension rather than inventing it.
- [ ] **Do not build on SDK identity assertion yet.** `IdentityAssertionParams` /
  `exchange_identity_assertion` ship in `mcp` 2.3.0 but **no matching extension is listed** in
  `ext-auth` — the SDK is ahead of, or divergent from, the registry.
- [ ] **Assess whether a gateway belongs in front of the hosted fleet.** The dominant 2026
  enterprise pattern, entirely unassessed for CSA. Not this repository's scope, but it is nobody's
  right now.
- [ ] **`CSA-MCP-Core` and `csa-mcp` were never inspected** — not cloned, not found by repo search.
  Everything [`docs/ESTATE.md`](docs/ESTATE.md) says about them is CSA's own record rather than
  measurement.

## Orchestration and disclosure (2026-10-04, `research/orchestration/`)

- [ ] **Set `cacheScope: "private"` on every identity- or configuration-filtered list result.**
  Confirmed normative; all four servers filter. A `"public"` list from an authenticated call *"may
  be shared outside of the initial request's authorization context."* Same scope on every page.
- [ ] **Keep enforcing per-tool policy at call time.** The spec: **MUST NOT** rely on `cacheScope`
  alone. Hiding a tool is context management, not protection.
- [ ] **Honour deterministic `tools/list` ordering** — cheap, and it exists for prompt-cache hits.
- [ ] **Measure what 241 tool definitions actually cost in tokens.** Unmeasured, and it decides
  whether progressive disclosure is urgent or theoretical here.
- [ ] **Record the disclosure rule in `docs/ESTATE.md`.** CSA already runs both patterns — `csa-mcp`
  is one endpoint with tiers 1–5 and plugin capabilities; the Python fleet is four servers with no
  disclosure control. Nothing writes down which shape is for what.
- [ ] **Track `modelcontextprotocol/progressive-disclosure-wg`** — grouping is a draft SEP opened
  2026-09-28. Do not build on it. Note issue #15, *"limits of tool search"*.
- [ ] **Read `programmatic tool calling` / code mode** — the second pattern in the same spec
  document, unexamined. Its framing matters for us: *"Tool results from one server are untrusted
  input to another."*

## Enforcement (2026-10-04, `research/enforcement/`)

- [ ] **Extract the untrusted-content wrapping primitive into `csa-mcp`** (ADR-007). Measured at
  **1%/2%/11%** similar across three servers, with a fourth having no module — the least consistent
  control in the fleet, and the only one whose failure lets injected content act with the user's
  credential. This **reverses** an earlier not-an-extraction-candidate call.
- [ ] **Say in the docs what local policy is for**, rather than apologising for it: it binds the
  *model*, not the user, and that is the correct scope. Policy is env-only and three of four servers
  already tell the model it *"cannot be changed from here"* — keep that property.
- [ ] **Test whether the policy actually holds under injection.** 241 tool registrations,
  `destructive_hint` ×37, `confirm=` ×9, `dry_run` ×3. Whether a determined injected instruction can
  route around the allowlists is **untested**, and that is a real gap.
- [ ] **Adopt Off / Monitoring / Enforcing staging** for any new policy, local or hosted — observe
  before blocking. Taken from commercial gateway products.
- [ ] **Read AWS's and Microsoft's agent-governance offerings.** Only Google's Agent Gateway was
  examined, because Google is the vendor CSA depends on most.

## Protocol

- [ ] **Measure which revision each server negotiates** with real clients. Currently unknown, and
  nothing downstream is decidable without it. [`docs/PROTOCOL.md`](docs/PROTOCOL.md).
- [ ] **Decide `cache_scope` per list result** - the one protocol item that fails quietly rather
  than loudly, because all four servers filter their tool surface by configuration.
- [ ] Watch for the SDK dropping `elicit_url`'s `elicitation_id`. Trigger recorded; do not
  pre-port. [`WAITING-FOR.md`](WAITING-FOR.md).

## Smaller

- [ ] **`csa-google-workspace-audit` has no licence.** The other four are Apache-2.0.
- [ ] CI to CSA public-repo standards, once there is something to gate — then add the checks to
  the branch rule, which currently requires **0** status checks because none exist.
