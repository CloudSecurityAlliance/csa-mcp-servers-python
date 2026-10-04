# RACI

| role | who |
|---|---|
| Responsible | Kurt Seifried |
| Accountable | Kurt Seifried |
| Consulted | external review, pending - see [`WAITING-FOR.md`](WAITING-FOR.md) |
| Informed | - |

## What one name costs, and what is being done about it

One person holds every role across this repository, the four servers it plans to absorb, and the
engineering practice all of it answers to. That is the real constraint, and it has a specific
failure mode worth naming: **nothing structural separates a measurement from a plausible
sentence.** The same person writes the claim and reviews it.

Two things in this repository exist because of that, not despite it:

- **Every number is reproducible**, with the method published and a one-line check per claim in
  [`docs/REVIEW-BRIEF.md`](docs/REVIEW-BRIEF.md). A reader can disagree with evidence rather than
  with authority.
- **The review brief names the weak points first**, including one unresolved contradiction. A
  document that only argues for its own plan cannot be checked by a reader who lacks the context
  to argue back.

The Consulted row is the mitigation, and it is the reason this repository was created as a plan
with no code: an external reviewer is the first thing here that is not the author.

Until that review lands, treat `accepted` as unavailable. Every ADR says `proposed`.
