# Security resources

**The question this answers:** what could go wrong security-wise here, and where is that already
answered?

This repository is public, contains no code, and holds no credentials. That makes its own surface
small and mostly about what must never arrive.

## What must never land here

- **No customer or member data** - not a corpus, not a sample, not an illustrative excerpt.
- **No credentials, tokens, client secrets or OAuth client files**, including in future test
  fixtures. Synthetic values only, and obviously synthetic.
- **No local filesystem paths** identifying a person's machine.

Checked before first publication: no credential, token, Airtable-identifier, email-address or
local-path pattern appears anywhere in the tree. That check is a thing somebody ran once, not a
gate - which is the same weakness recorded in
[`OPERATIONAL-RESOURCES.md`](OPERATIONAL-RESOURCES.md), and the reason CSA's public-build guard
exists elsewhere in the fleet.

## Deferred, deliberately, to avoid a second answer

Most of what matters is already written where the code is, and duplicating it here would create two
places recording one thing - the failure mode where two documents disagree for months with neither
marked as the loser.

| concern | where it is answered |
|---|---|
| credential custody, file modes, token storage | each server's own `SECURITY-RESOURCES.md` (`csa-zendesk` and `csa-skilljar` carry the detailed ones) |
| how a credential reaches a machine | CINO-PE `surfaces/mcp/CREDENTIALS.md` |
| what a server owes regardless of maturity | CINO-PE `surfaces/mcp/CONFORMANCE.md` |
| reversibility and blast radius per capability | CINO-PE `surfaces/mcp/CONSEQUENCE.md` |
| vulnerability reporting for a published server | each server's own `SECURITY.md` |

Those files move into this repository with their packages at migration, and they stay
package-scoped. Nothing in this file should grow to restate them.

## The one security-relevant thing this repository decides

**Vendor content reaching a model is untrusted data, never instructions.** A ticket body, a mail
subject, a document comment or a learner-submitted field may contain text shaped like a command.
Every server here draws that boundary, and the shared library planned in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) must not weaken it: `mcp/_untrusted.py` measures 11%
similar across two servers and is explicitly **not** an extraction candidate.

Two protocol-level constraints are also recorded in [`docs/PROTOCOL.md`](docs/PROTOCOL.md) because
they bind the hosted design before it is written: **do not build on OAuth Dynamic Client
Registration** (deprecated in `2026-07-28`), and **key credentials by issuer**, never reusing a
registration across authorization servers.

## Current gaps

- **No branch protection on `main`** - see [`BACKUP-RESOURCES.md`](BACKUP-RESOURCES.md).
- **No CI, so no secret-scanning gate.** CSA's public-repo standards apply and cannot be satisfied
  before there is a workflow to run them in.
- **`csa-google-workspace-audit` has no licence**, which is a publication question rather than a
  security one, but it is unresolved and listed in [`TODO.md`](TODO.md).
