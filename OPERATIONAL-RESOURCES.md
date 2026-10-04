# Operational resources

**The question this answers:** what does this repository depend on outside itself, and what
depends on it?

Nothing here is hosted. There is no service, no credential, no scheduled job, no CI. The honest
answer looked like "none" - and investigating anyway produced the finding below, which is why this
file is written rather than closed as not-applicable.

## The outward surface is citational, and nothing checks it

This repository contains no code. What it contains is roughly **160 factual claims about four other
repositories**, measured in one working tree on one day:

| claim type | count | fragility |
|---|---|---|
| similarity percentages | 91 | invalidated by any edit to either file |
| line counts of other repos' modules | 65 | invalidated by any edit |
| published version numbers | 4 | invalidated by any release |
| **line-number-precise call sites** | **4** | **invalidated by any edit *above* them** |

The four precise ones:

```
csa-google-workspace/.../mcp/_tools/auth.py:236,239,243   and  auth.py:270
csa-google-gmail-calendar/.../mcp/_tools/auth.py:231,234,238  and  auth.py:262
```

**Nothing verifies any of this.** The numbers are dated at the top of each document, and
[`docs/EVIDENCE.md`](docs/EVIDENCE.md) publishes the script so they can be re-derived - but
re-derivation is a thing a person must decide to do. A reviewer reading this in a month gets stale
numbers with no warning that they are stale, and the conclusions resting on them look equally
sound either way.

This is the same shape as the finding in CINO-PE's own `OPERATIONAL-RESOURCES.md`: two installer
scripts there cite `DEC-012` and `DEC-013` **by number, in comments, where nothing checks them**. A
citation that cannot fail is indistinguishable from a citation that is wrong.

**Mitigation, not yet built:** the measurement script is already published and deterministic. A
check that re-runs it and fails when a published number has moved would convert ~160 unverified
claims into a gate. It needs the four repositories present, which is true after migration and
awkward before it. See [`TODO.md`](TODO.md).

## What this repository depends on

| dependency | why it matters |
|---|---|
| the four servers' current `main` | every measurement is a snapshot of them |
| `mcp` 2.3.0 specifically | the protocol findings are SDK-version-specific, and it shipped a minor the day before measurement |
| the MCP specification, revision `2026-07-28` | links are verified resolving as of 2026-10-03 |
| PyPI | four Trusted Publisher configurations must be changed before the first release from here |
| GitHub issue transfer | migration step 7, and the only irreversible step |

## What depends on this repository

Nothing automated. One human decision depends on it: whether to migrate. If the plan is wrong,
four published servers get migrated wrongly - which is the argument for the review in
[`WAITING-FOR.md`](WAITING-FOR.md) rather than for a faster start.

No installer, script or CI job in any CSA repository references this repository. Verified: all 44
references to these servers across `DesktopSetup` and `CSA-Plugins` are PyPI package names, and
none is a Git URL.
