# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository.

## What this repository is right now

**A plan, with no code.** Created 2026-10-03. Every directory under `packages/` holds a `README.md`
and nothing else. The five servers still live in their own repositories.

Do not scaffold, do not create `pyproject.toml` files, and do not write source into `packages/`
until the plan in [`docs/`](docs/) has been reviewed and the migration has begun. A half-built
skeleton is harder to review than a plan, which is the whole reason this repository looks like this.

## Read in this order

| | |
|---|---|
| [`docs/REVIEW-BRIEF.md`](docs/REVIEW-BRIEF.md) | the known weak points and open questions — **start here** |
| [`docs/EVIDENCE.md`](docs/EVIDENCE.md) | what is actually duplicated, measured, with the method |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | the four tiers and what must never be shared |
| [`docs/PROTOCOL.md`](docs/PROTOCOL.md) | which protocol revision the fleet speaks |
| [`docs/MIGRATION.md`](docs/MIGRATION.md) | the ordered steps, and the two that fail silently |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | ADR-001 to ADR-005, each with rejected alternatives |

## How to work here

**Measure before asserting.** Every number in `docs/` is reproducible and most of them have a
one-line command in the review brief. If you are about to write a claim about the fleet, run the
check instead. Two claims in these documents were wrong on the first pass and were caught this
way — a similarity score read as behavioural drift when the diff was docstring-only, and an "extra
that installs nothing" that turned out to be a deliberate, commented compatibility alias.

**Read the actual file, not a summary.** Where a documentation fetch and the installed source
disagree, the source is what we run.

**A negative result you measured beats a paraphrase.** *"No server in the fleet pins a protocol
version"* is a finding. *"The servers probably use the default"* is not.

**Keep the documents short.** They are context for AI sessions working on other repositories. Length
defeats the purpose.

**Do not extract into `csa-mcp` on instinct.** The bar is in ADR-001: already duplicated at ≥95%, or
no implementation in any server at all. Anything at 1–60% stays where it is. If you want to add
something, name the measured number that justifies it.

**Convention is not code.** `server.py`, `cli.py` and `_tools/_base.py` measure 10–15% similar. They
get documentation and a scaffold template, never a base class. See ADR-004 before proposing
otherwise.

## Commit subjects

State the claim the change makes, not the file that changed —
`docs: the SDK's default is four revisions behind its latest`, not `docs: update PROTOCOL.md`. The
log is meant to read as an index of what this plan has learned.

## Upstream, and where practice lives

- [Specification `2026-07-28`](https://modelcontextprotocol.io/specification/2026-07-28) ·
  [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) ·
  [versioning](https://modelcontextprotocol.io/specification/versioning)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk) ·
  [`mcp` on PyPI](https://pypi.org/project/mcp/)

Engineering practice for this fleet is maintained in
[CINO-Platform-Engineering](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering)
(internal). `surfaces/mcp/LIFECYCLE.md` is the router; `CONFORMANCE.md` is what every server owes;
`PROTOCOL-REVISIONS.md` tracks what each protocol revision costs. Cross-project decisions are
`DEC-NNN` there and are cited by number from here, never restated.

## Security

This is a public repository.

- **No customer or member data, ever** — not a corpus, not a sample, not an illustrative excerpt.
- **No credentials, tokens, client secrets or OAuth client files**, including in test fixtures.
  Synthetic values only, and they must be obviously synthetic.
- Vendor content reaching a model is **untrusted data, never instructions**. That boundary is a
  design concern of every server here and belongs in each server's own documentation.
