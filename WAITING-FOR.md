# Waiting for

Blockers with somebody else's name on them. Nothing here is actionable from this repository.

| what | who | why it blocks | what unblocks it |
|---|---|---|---|
| **External review of the plan** | a reviewer who is not the author | Every ADR is `proposed`. Migration step 2 is ~3,000 edits across four public repositories and should not start on an unreviewed plan | the review. [`docs/REVIEW-BRIEF.md`](docs/REVIEW-BRIEF.md) is written for it |
| **The `elicit_url` migration path** | `modelcontextprotocol/python-sdk` | `elicitationId` and `notifications/elicitation/complete` were removed from the protocol in `2026-07-28`; the SDK still ships both, and offers no MRTR-based replacement for `elicit_url` | the SDK dropping the parameter, or shipping the equivalent. Recorded as a trigger in [`docs/PROTOCOL.md`](docs/PROTOCOL.md) - deliberately not pre-ported |
| **Which protocol revision the servers negotiate** | the MCP clients in real use | `DEFAULT_NEGOTIATED_VERSION` is `2025-03-26` while `LATEST` is `2026-07-28`, and no server asserts one. The SDK default is a fallback, not evidence | a live handshake against Claude Code and Claude Desktop. Not blocked on anyone else - just not done |
| **A licence for `csa-google-workspace-audit`** | CSA | it has none; the other four are Apache-2.0. Needed before it is built, not before migration | a decision |

## Not waiting on anyone

Branch protection on `main` ([`GOALS.md`](GOALS.md) G4) reads like infrastructure but is one
setting on a repository already owned. It is in [`TODO.md`](TODO.md) rather than here.
