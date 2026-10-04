#!/usr/bin/env python3
"""Re-derive every number in SURVEY.md and TIMELINE.md.

A survey nobody can re-run is a claim about an unknown moment. This takes about twenty seconds
and needs an authenticated `gh`.

    python research/fleet-survey/measure.py

Two things worth knowing if you change it:

* `encoding="utf-8", errors="replace"` on every subprocess call is load-bearing, not decoration.
  Without it this script dies on Windows with a cp1252 UnicodeDecodeError part-way through a large
  JSON response - the default console encoding cannot decode bytes GitHub returns. It failed
  exactly that way on the first run.
* `AS_OF` is fixed rather than `date.today()`. Re-running on a later date should produce ages
  measured from the same reference point as the written survey, so the two can be compared. Change
  it deliberately when writing a new survey, and say so in the document.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, datetime

AS_OF = date(2026, 10, 4)

FLEETS = [
    ("awslabs/mcp", "AWS", "src"),
    ("cloudflare/mcp-server-cloudflare", "Cloudflare", "apps"),
    ("microsoft/mcp", "Microsoft", "servers"),
    ("modelcontextprotocol/servers", "MCP project", "src"),
    ("github/github-mcp-server", "GitHub - one server", None),
]

ECOSYSTEM = [
    ("modelcontextprotocol/modelcontextprotocol", "the specification"),
    ("modelcontextprotocol/python-sdk", "Python SDK"),
    ("modelcontextprotocol/typescript-sdk", "TypeScript SDK"),
    ("modelcontextprotocol/servers", "reference servers"),
    ("modelcontextprotocol/servers-archived", "servers pruned OUT"),
    ("modelcontextprotocol/ext-auth", "authorization extensions"),
    ("cloudflare/mcp-server-cloudflare", "Cloudflare monorepo"),
    ("github/github-mcp-server", "GitHub"),
    ("awslabs/mcp", "AWS"),
    ("microsoft/mcp", "Microsoft"),
]

CSA = [
    "CloudSecurityAlliance/csa-google-workspace",
    "CloudSecurityAlliance/csa-skilljar",
    "CloudSecurityAlliance/csa-zendesk",
    "CloudSecurityAlliance/csa-google-gmail-calendar",
    "CloudSecurityAlliance/csa-google-workspace-audit",
    "CloudSecurityAlliance/csa-mcp-servers-python",
]

ANNOUNCEMENT = date(2024, 11, 25)  # Anthropic announced MCP publicly


def api(path: str, jq: str | None = None) -> str | None:
    """`gh api`, returning None on any failure rather than raising."""
    cmd = ["gh", "api", path] + (["--jq", jq] if jq else [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout else None


def ago(iso: str) -> int:
    d = datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
    return (AS_OF - d).days


def count_dirs(repo: str, path: str) -> str:
    raw = api(f"repos/{repo}/contents/{path}", '[.[] | select(.type=="dir")] | length')
    return raw if raw and raw.isdigit() else "-"


def root_files(repo: str) -> list[str]:
    raw = api(f"repos/{repo}/contents", '.[] | select(.type=="file") | .name')
    return raw.splitlines() if raw else []


def main() -> int:
    if api("user") is None:
        print("gh is not authenticated - run `gh auth login`", file=sys.stderr)
        return 1

    print(f"Measured as of {AS_OF.isoformat()}  (MCP announced {ANNOUNCEMENT.isoformat()}, "
          f"{(AS_OF - ANNOUNCEMENT).days} days earlier)\n")

    print("=" * 96)
    print("STRUCTURE - how many servers, and where")
    print("=" * 96)
    for repo, who, srv_dir in FLEETS:
        raw = api(f"repos/{repo}")
        if not raw:
            print(f"  {who:22s} {repo:46s} NO ACCESS")
            continue
        d = json.loads(raw)
        n = count_dirs(repo, srv_dir) if srv_dir else "1"
        extra = ""
        if repo == "cloudflare/mcp-server-cloudflare":
            extra = f"  packages/={count_dirs(repo, 'packages')}"
        print(f"  {who:22s} {repo:46s} {srv_dir or '(single)':9s} n={n:>3s}{extra}")

    print("\n" + "=" * 96)
    print("TIMELINE - creation dates bound the trend")
    print("=" * 96)
    rows = []
    for repo, note in ECOSYSTEM:
        raw = api(f"repos/{repo}")
        if not raw:
            continue
        d = json.loads(raw)
        rows.append((d["created_at"][:10], ago(d["created_at"]), repo, note,
                     d["stargazers_count"], d["pushed_at"][:10], d["archived"]))
    for created, age, repo, note, stars, pushed, arch in sorted(rows):
        flag = " [ARCHIVED]" if arch else ""
        print(f"  {created}  {age:>4d}d ago  {repo:46s} {stars:>6d}*  pushed {pushed}{flag}")
        print(f"              {note}{flag}")

    print("\n" + "=" * 96)
    print("CADENCE - how fast the ground moves")
    print("=" * 96)
    for repo in ("modelcontextprotocol/python-sdk", "modelcontextprotocol/typescript-sdk"):
        raw = api(f"repos/{repo}/releases?per_page=100")
        if not raw:
            continue
        rel = json.loads(raw)
        if len(rel) < 2:
            continue
        span = ago(rel[-1]["published_at"]) - ago(rel[0]["published_at"])
        print(f"  {repo}")
        print(f"    {len(rel)} releases over {span}d -> one every {span / (len(rel) - 1):.1f} days")
        print(f"    newest {rel[0]['tag_name']} {rel[0]['published_at'][:10]}")

    print("\n" + "=" * 96)
    print("WHAT AWS SHARES AT THE ROOT (62 servers, no workspace)")
    print("=" * 96)
    for f in root_files("awslabs/mcp"):
        print(f"    {f}")
    print(f"    root pyproject.toml present: "
          f"{api('repos/awslabs/mcp/contents/pyproject.toml') is not None}")

    print("\n" + "=" * 96)
    print("CSA's OWN - the polyrepo state is weeks old, not years")
    print("=" * 96)
    for repo in CSA:
        raw = api(f"repos/{repo}")
        if not raw:
            print(f"  {repo:52s} NO ACCESS")
            continue
        d = json.loads(raw)
        print(f"  {repo:52s} created {d['created_at'][:10]}  {ago(d['created_at']):>4d}d")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
