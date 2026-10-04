# Is this a new trend? Dating it

**The question this answers:** how old is the practice of keeping many MCP servers in one
repository, and is CSA late, early, or on time?

Measured **2026-10-04**, every date from the GitHub API. Dates are repository creation dates, which
are facts rather than estimates.

---

## Nothing here can be older than two years

Anthropic announced the Model Context Protocol publicly on **2024-11-25**. The specification and
both SDK repositories were created **2024-09-24**, two months earlier, during pre-announcement
development.

So **the entire history of running multiple MCP servers is at most 740 days long** — about 24
months. Any claim that something is "established practice" has that ceiling.

## The timeline

| date | days ago | event |
|---|---|---|
| 2024-09-24 | 740 | `modelcontextprotocol/modelcontextprotocol`, `python-sdk`, `typescript-sdk` created |
| 2024-11-19 | 684 | `modelcontextprotocol/servers` created — **6 days before the public announcement** |
| **2024-11-25** | **678** | **MCP announced publicly** |
| 2024-11-27 | 676 | `cloudflare/mcp-server-cloudflare` created — **2 days after the announcement** |
| 2025-03-04 | 579 | `github/github-mcp-server` created |
| 2025-03-21 | 562 | `awslabs/mcp` created |
| 2025-04-09 | 543 | `microsoft/mcp` created |
| 2025-05-28 | 494 | `modelcontextprotocol/servers-archived` created **and archived the same day** |
| 2025-10-01 | 368 | `modelcontextprotocol/ext-auth` created |
| 2026-07-28 | 433 → | the current protocol revision |

## Three findings, and the first one reframes the question

### 1. The monorepo was never a migration. It was the starting shape.

This is the important one. **Cloudflare created its MCP monorepo two days after the protocol was
announced** — 676 days ago, only 8 days after the official `servers` repository itself.

Nobody in this survey tried separate repositories per server and consolidated later. There was no
period during which polyrepo was the norm for MCP fleets. The first organisation to run several
servers put them in one repository immediately, and everyone who followed did the same.

So the framing "the old days of many repos are over" does not quite fit: **for MCP there were no old
days.** The pattern did not win an argument; it was never contested.

What that means for CSA is more useful than a trend claim. Four separate repositories is not the
legacy approach that the ecosystem has moved on from — it is an approach the ecosystem never
adopted.

### 2. The pattern formed in a 36-day window in spring 2025

GitHub (2025-03-04), AWS (2025-03-21) and Microsoft (2025-04-09) created their MCP server
repositories within **36 days of each other**, about four months after the announcement. All three
chose a single repository; GitHub went further and chose a single *server*.

That cluster is when the question stopped being open. It is **19 months old** as of this survey —
long enough to be settled practice, recent enough that nobody has a decade of operational
experience with it.

### 3. The project prunes, not just consolidates

`modelcontextprotocol/servers-archived` was created **and archived on the same day**, 2025-05-28.
It exists to hold servers removed from the main tree — `modelcontextprotocol/servers` now carries 7
server directories where it once carried many more.

So the mature behaviour is not only "put them together" but "take them out again when they stop
earning their place." A monorepo makes removal visible and cheap, which is the half of the argument
that gets forgotten.

## How fast the ground moves underneath

| SDK | releases | span | cadence | current |
|---|---|---|---|---|
| `python-sdk` | 73 | 681 days | **one every 9.5 days** | v2.3.0, 2026-10-02 |
| `typescript-sdk` | 100 (page 1) | 184 days | **one every 1.9 days** | v2.3.0, 2026-10-02 |

Both reached v2.3.0 on the same day. TypeScript ships roughly **five times** as often.

Two consequences. A dependency releasing every 9.5 days needs an upper bound, not a floor — which is
why [`../../docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) pins `mcp` with a ceiling. And a
protocol whose revisions arrive on this cadence makes a *dated* survey mandatory: this document is
accurate on 2026-10-04 and makes no claim about any later date.

`ext-auth`, by contrast, was created 368 days ago and **last pushed 2026-06-18 — 108 days before
this survey.** That matters for one finding: the SDK ships identity-assertion machinery with no
matching entry in `ext-auth`, and a registry that has not moved in three and a half months is a
weaker signal of "this does not exist" than it first appeared.

## And CSA's own dates, which change the migration's character

| repository | created | age |
|---|---|---|
| `csa-google-workspace` | 2025-05-27 | **495 days** |
| `csa-skilljar` | 2026-08-26 | 39 days |
| `csa-zendesk` | 2026-08-31 | 34 days |
| `csa-google-gmail-calendar` | 2026-09-02 | 32 days |
| `csa-google-workspace-audit` | 2026-09-15 | 19 days |
| `csa-mcp-servers-python` | 2026-10-04 | 0 days |

**Four of CSA's six MCP repositories are less than 40 days old.** `csa-google-workspace` ran alone
for roughly fourteen months, and then **three servers appeared within seven days** of each other in
late August 2026.

This substantially changes what the migration is. The drift measured in
[`../../docs/EVIDENCE.md`](../../docs/EVIDENCE.md) — two `ruff` floors, a `markdownify` major-version
gap, a differently-named extra, a 96%-identical module — did not accumulate over years. **It
appeared in a burst five weeks ago, when three repositories were created in a week.**

So the migration is not undoing years of entrenched divergence. It is correcting a structural choice
made last month, before which there was only one server and therefore no choice to make. That makes
it cheaper and less risky than the plan currently implies, and it is worth saying plainly: the
window in which this is nearly free is open now and closes as each of those four repositories
accumulates history and external references.

## What this timeline does not establish

- **Why** each organisation chose a monorepo. Creation dates show *what* and *when*, never *why*.
  No design document was found stating the reasoning.
- **Whether anyone tried polyrepo and abandoned it quietly.** Absence from this survey is not
  evidence of absence; a deleted or private repository leaves no trace here.
- **Any date after 2026-10-04.** The SDK cadence above is the reason to re-run rather than trust
  this.
- **Commit-level history.** First-commit dates were not retrieved (the API's pagination trick for
  the oldest commit failed), so creation dates are used throughout. A repository can be created
  before work starts or after it starts elsewhere.
