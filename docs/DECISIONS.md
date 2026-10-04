# Decisions

Decisions specific to this repository. Each carries its rejected alternatives, because the rejected
option is where the reasoning lives — and because an unmarked loser read as authoritative is how two
decisions end up disagreeing in a corpus for months.

Cross-project engineering decisions (DEC-NNN) live in
[CINO-Platform-Engineering](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering/blob/main/DECISIONS.md)
and are referenced here by number, never restated.

---

## ADR-001: the shared library is extracted from measurement, not deferred to five servers

**Date:** 2026-10-03 · **Status:** proposed, pending review

**Supersedes:** `surfaces/mcp/ROADMAP.md`, section *"Why the foundation moved to last"*
(2026-09-25).

### Context

The roadmap set an explicit order: **five servers to a usable internal standard first, the shared
foundation last, built from what those five actually needed.** Its reasoning was good and should be
read before this is accepted. Foundation-first means extracting from three servers, two of which
were the only ones with a complete surface, and guessing at the needs of the two unbuilt ones — mail
and the tenant-audit server — which is precisely what CSA's core principle forbids. It even named
the cost it was accepting: *"some duplication will happen, and we are choosing it."*

Since then, four servers are built and published rather than three, and the duplication the roadmap
predicted can be **measured** instead of forecast. See [`EVIDENCE.md`](EVIDENCE.md).

### Decision

Extraction begins now, driven by measured duplication, with a hard eligibility bar: **a module
enters `csa-mcp` only when it is already duplicated at ≥95%, or when it has no implementation in any
server at all.**

That admits exactly four modules today, about 300 lines. Everything at 1–60% similarity stays where
it is.

### Rationale

The roadmap's principle is not being set aside; it is being satisfied by different means. It
deferred extraction because the evidence did not exist yet. The evidence now exists for a narrow
slice, and only that slice moves.

Three specific supports:

1. **The ≥95% tier is the copy the roadmap authorised.** It required a deliberate copy to carry a
   comment naming its source and to be tracked for retirement. `_markdown.py` does exactly that —
   *"Ported from csa-zendesk's `_markdown.py` (same problem, same fix)"* — and diffing the two copies
   shows **19 changed lines, all in the docstring**, with byte-identical transform code. This is a
   tracked copy reaching its scheduled retirement, not a shortcut.
2. **The two new modules have no incumbent.** `server/discover` and a shared status vocabulary
   cannot be extracted from implementations that do not exist. Nothing has to be reconciled to adopt
   them, which is the test.
3. **The measurement constrains the library more tightly than the deferral did.** "Extract later
   from five" has no size limit. "≥95% or no incumbent" admits 300 lines and makes every future
   addition argue against a number.

### Rejected alternatives

- **Keep the roadmap unchanged and extract nothing until all five servers are built.** Not wrong,
  and it was right when written — but it now defers a 96%-identical module whose own comment says it
  is waiting to be retired, and it leaves `server/discover` to be written four times because the
  rule that forbids designing also forbids the thing with no incumbent. Rejected as *unwarranted
  here*, not as mistaken.
- **Treat this as mere execution of the existing roadmap, with no decision recorded.** Defensible —
  retiring an authorised, tracked copy is arguably what the roadmap planned for. Rejected because
  the roadmap's text says "foundation last" and this starts it early; a reader comparing the two
  would find a contradiction with nothing marking which won. That failure has already cost this
  organisation five months once.
- **Extract the OAuth trio too (58–60%).** Rejected: that range is the most dangerous, not the most
  promising. Adopting either copy silently discards the other's behaviour. Reconcile as a decision
  first, extract second.
- **Build a server base class covering `server.py`/`cli.py`/`_tools/_base.py`.** Rejected on the
  measurement — 10–15% similarity is a structural resemblance, not shared behaviour. See ADR-004.

### Affects

`surfaces/mcp/ROADMAP.md` gains a pointer to this ADR. `csa-mcp` can be created. The servers
convert one at a time.

---

## ADR-002: one monorepo for the Python servers

**Date:** 2026-10-03 · **Status:** proposed, pending review

### Context

Four published servers in four repositories, built sequentially, each learning from the last. They
diverged in ways nobody chose: linting floors split two-and-two, a major-version gap on a library
mandated fleet-wide, and a user-facing extra named differently in one of four.

### Decision

A single repository, `csa-mcp-servers-python`, as a [uv
workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) with one `uv.lock`. Published
package names and versions stay independent and unchanged.

### Rationale

**One lockfile makes the divergent state unrepresentable** rather than merely discouraged. The
problem was never that four repositories *could* drift; it is that drift was invisible, because
comparing them meant cloning them.

Co-location is also what makes extraction honest — four copies side by side turn "what is actually
shared?" into one command, which is how [`EVIDENCE.md`](EVIDENCE.md) exists at all.

And the migration is cheaper than feared, measured rather than assumed: **nothing installs these
from Git.** All 44 references in the installer repositories are PyPI names, so a repository move is
invisible to anyone installing a server.

### Rejected alternatives

- **Separate repositories plus a shared library on PyPI.** The conventional answer, and it fails the
  specific problem: it fixes *code* duplication while leaving *configuration* drift untouched, which
  is where the measured divergence actually is. A shared library does not unify `ruff` floors.
- **Monorepo for the two Google servers only.** They share the most (the entire 58–60% OAuth tier is
  theirs). Rejected because the drift being fixed is fleet-wide, and a half-migration means
  maintaining two CI conventions and two release conventions indefinitely.
- **Start with only the unbuilt audit server, migrate the four later once proven.** Genuinely
  attractive — fully reversible, no disruption to four working servers. Rejected deliberately: it
  defers every hygiene fix behind building a whole new server, and the measured drift is live now.
  The risk is accepted because steps 1–6 of [`MIGRATION.md`](MIGRATION.md) are all reversible; only
  issue transfer is not.

### Affects

Everything. See [`MIGRATION.md`](MIGRATION.md).

### Correction (2026-10-04): the monorepo is right, the single lockfile is not obviously right

The survey in [`PRIOR-ART.md`](PRIOR-ART.md) §0 confirms the monorepo and **undercuts the mechanism
this ADR argued for.**

Four of four organisations running multiple MCP servers use one repository, so that part stands
without qualification. But **AWS runs 62 Python MCP servers with no workspace and a `uv.lock` per
server.** There is no root `pyproject.toml`. Dependency resolution is deliberately not shared, and
at that scale the reason is clear: one lockfile means one server's unsatisfiable dependency blocks
all 62.

What AWS shares at the root is tooling and writing — a single `.ruff.toml`, `.python-version`,
`.pre-commit-config.yaml`, `.gitleaks.toml`, `trivy.yaml`, plus `DESIGN_GUIDELINES.md` and
`DEVELOPER_GUIDE.md`.

**And that is the direct fix for the drift this ADR cited as its evidence.** `ruff>=0.6` against
`>=0.16` and `mypy>=1.11` against `>=2.0` are *tool configuration* divergence. A root `.ruff.toml`
addresses them head-on; a shared lockfile addresses them as a side effect of coupling everything
else too. The right problem, a heavier instrument than needed.

The `markdownify>=1.2` against `>=0.13` gap is the one genuinely about *runtime* dependency floors,
and it is one library mandated by one decision — a dependency policy question rather than an
argument for shared resolution.

**What stands:** the monorepo, and the claim that invisible drift was the problem.
**What is now open:** one `uv.lock` or five. Five servers make the coupling tractable where 62 do
not, so this is not settled by AWS's choice — but it can no longer be presented as the obvious one.
Listed in [`REVIEW-BRIEF.md`](REVIEW-BRIEF.md) and superseded in part by ADR-006.

---

## ADR-006: shared tooling configuration at the root, independent of the lockfile question

**Date:** 2026-10-04 · **Status:** proposed, pending review

### Context

The measured divergence that motivated this repository is mostly *tool configuration*: two
different `ruff` floors, two different `mypy` floors, and a user-facing extra named differently in
one of four servers. ADR-002 proposed to fix this with a single workspace lockfile. The survey shows
the largest Python MCP fleet fixes it with root configuration files instead, and keeps resolution
per-server.

### Decision

Adopt root tooling configuration regardless of how the lockfile question resolves:

```
.ruff.toml                 one lint configuration for every package
.python-version            3.14, which all four already use
.pre-commit-config.yaml    one hook set
.gitleaks.toml             secret scanning, matching the public-repo standard
docs/CONVENTIONS.md        the tier-3 convention document
```

Per-package `pyproject.toml` keeps only what is genuinely per-package: the dependency set, the
coverage gate, the entry points.

### Rationale

It is the cheaper instrument for the measured problem, it is independent of the lockfile decision
so it cannot be blocked by it, and it is what AWS does at twelve times our server count. It also
gives the convention tier (ADR-004) a concrete home rather than leaving it an argument — Cloudflare
has `implementation-guides/`, AWS has `DESIGN_GUIDELINES.md` and `DEVELOPER_GUIDE.md`, Microsoft has
`core/` plus `eng/`.

### Rejected alternatives

- **Rely on the shared lockfile to constrain tool versions.** That is ADR-002's original position.
  Rejected as indirect: a lockfile pins what is installed, while the divergence is in declared
  floors, and it couples five packages' resolution to fix a lint-config problem.
- **Leave tool config per-package and review it periodically.** Rejected — that is exactly the
  state that drifted, and the drift was invisible rather than tolerated.

---

## ADR-003: `csa-mcp` is not published to PyPI to begin with

**Date:** 2026-10-03 · **Status:** proposed, pending review

### Decision

`csa-mcp` lives in the workspace as a path dependency. No PyPI project, no version number offered to
anyone, no API stability claim. It gets published when a server **outside** this repository needs
it.

### Rationale

It is being extracted, which means its shape is still being discovered. Publishing converts every
early guess into a public contract: a stability statement, a tombstone obligation on every major, a
version number people pin.

CSA's own standard for publishing a library is demanding on purpose — *"the same questions, pointed
at us"*. Meeting it for a 300-line library with four in-repo consumers buys nothing and costs the
freedom to change it.

### Rejected alternatives

- **Publish from day one.** Would let the servers install independently of the monorepo and force
  API discipline early. Rejected as premature: there is no consumer that needs it, and the
  discipline it forces is discipline about decisions not yet made.
- **Vendor it into each server instead.** That is the status quo — it is what the 96% copy *is*.
  Rejected; the point is to stop.

### Affects

Servers depend on `csa-mcp` by workspace path. Their published wheels must not reference it until it
is published — so extraction has to keep `csa-mcp` code *inside* each published distribution, or the
publish step has to wait. **This is an open question flagged in
[`REVIEW-BRIEF.md`](REVIEW-BRIEF.md).**

---

## ADR-004: the convention tier ships documentation and a scaffold, never importable code

**Date:** 2026-10-03 · **Status:** proposed, pending review

### Context

`server.py`, `cli.py` and `_tools/_base.py` appear in three servers each, do corresponding jobs, and
measure **10–15%** similar.

### Decision

A documented layout plus a `scaffold/` template a new server is copied from. No base class, no
framework entry point, no importable abstraction over this tier.

### Rationale

10–15% similarity means the resemblance is *structural*, not behavioural. An abstraction over it
abstracts the shape rather than any shared logic, and servers then write code to escape it — which
is how a small library becomes a framework its own authors fight.

A convention that is copied and then diverges is working correctly: the divergence is the server
expressing something true about its vendor. A base class that is inherited and then worked around is
not.

### Rejected alternatives

- **An abstract `CSAServer` base class.** The instinctive design. Rejected on the measurement.
- **Nothing at all — let each server do as it likes.** Rejected: the shapes *are* similar, and a new
  server (the audit server, next) benefits from being told the layout. Documentation captures that
  without forcing it.

---

## ADR-007: low similarity means different things for a convention and for a safety control

**Date:** 2026-10-04 · **Status:** proposed, pending review

**Partially supersedes:** ADR-004's reach, and a claim in `SECURITY-RESOURCES.md`.

### Context

ADR-004 reads low similarity as evidence *against* extraction: `server.py` at 10% is a structural
resemblance, so sharing it would abstract the resemblance rather than any behaviour. That is right
for `server.py`.

Applying the same rule to `_untrusted.py` gave the wrong answer. Measured 2026-10-04, the
untrusted-content boundary is **1%, 2% and 11%** similar across three servers, with a fourth having
no module at all and one of the three sitting at a different architectural layer. It is the least
consistent control in the fleet — less consistent than `auth.py` (16%) or `policy.py` (3%) — and it
is the only one whose failure lets injected content act with the user's credential.

### Decision

Low similarity is not self-interpreting. The test is: **does a single correct behaviour exist?**

- **No** — the variation is legitimate and the code stays put. *"What should my CLI do?"*,
  *"how is this server configured?"* Extraction would force unlike things into one mould.
- **Yes** — low similarity is evidence of a **missing shared primitive**, and the cost of leaving
  it is highest exactly where the control is safety-critical. *"How do I mark vendor content so a
  model treats it as data rather than instructions?"* has one right answer.

So `csa-mcp` takes the untrusted-content **wrapping primitive**. Vendor content *shapes* — what a
Zendesk comment or a Gmail MIME part looks like — stay with their vendors.

### Rationale

ADR-001's ≥95%-or-no-incumbent bar is a good default and it is a *floor on evidence*, not a ceiling
on judgement. A control implemented four ways where one way is correct is not four pieces of
evidence that it should stay split; it is four chances to have got it wrong, and 241 tool
registrations' worth of surface behind it.

### Rejected alternatives

- **Keep the ≥95% bar absolute.** Consistent and simple. Rejected: it would leave the fleet's
  most safety-critical control as four independent implementations, which is the outcome the bar
  exists to prevent, reached by obeying the bar.
- **Extract `policy.py` too, by the same argument.** Rejected — policy at 3% is genuinely
  vendor-specific: Zendesk allowlists and Skilljar capability gates are not the same control wearing
  different clothes. The *vocabulary* for reporting a refusal should converge; the rules should not.
- **Rewrite all four to match before extracting.** Rejected as the expensive order. Extract the
  primitive, then converge onto it one server at a time, per ADR-001.

### Affects

`csa-mcp` gains a fifth seeded module. `SECURITY-RESOURCES.md` carries the correction.
[`research/enforcement/`](../research/enforcement/) is the evidence.

---

## ADR-005: a uv workspace does not contradict one-environment-per-server

**Date:** 2026-10-03 · **Status:** proposed, pending review

### Context

DEC-012 requires one isolated environment per server, after a `uv` rebuild turned four working
servers into husks in a single run. A shared workspace reads like a direct contradiction.

### Decision

It is not one, and the distinction is recorded so it is not re-litigated: **DEC-012 governs
installation, this governs development.** End users run `uv tool install csa-zendesk` and get four
isolated runtime environments; a bad resolve in one still cannot reach another. The workspace is one
lockfile and one *dev* environment for people working in this repository.

### Rejected alternatives

- **Four independent dev environments inside the monorepo.** Would satisfy the letter of DEC-012 and
  discard the entire benefit — the single lockfile *is* the fix for the measured drift.
- **Ask for DEC-012 to be amended.** Unnecessary; it already says what it means. Only the apparent
  conflict needed recording.
