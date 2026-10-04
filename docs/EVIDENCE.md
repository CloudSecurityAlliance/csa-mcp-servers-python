# What is actually shared, measured

**The question this answers:** which code is genuinely duplicated across the fleet, and which code
merely has the same filename?

Everything here was measured on **2026-10-03** against the four servers as they stood on `main`,
with `mcp` 2.3.0 installed. The method is at the bottom so the numbers can be re-derived rather than
believed.

This document exists because the alternative — deciding what a shared library should contain by
reasoning about what *ought* to be common — is how frameworks get built that nobody wants to use.

---

## The method

For every module path appearing in more than one server, compare the file contents pairwise and
average the ratios. `difflib.SequenceMatcher` on raw text, so comments and docstrings count: two
files that do the same thing by different means *should* score low, because sharing them would mean
choosing a winner.

```python
import difflib, pathlib
from itertools import combinations

REPOS = ["csa-zendesk", "csa-google-workspace",
         "csa-google-gmail-calendar", "csa-skilljar"]

def modules(repo):
    src = pathlib.Path(repo) / "src"
    out = {}
    for pkg in (p for p in src.iterdir() if p.is_dir() and not p.name.endswith(".egg-info")):
        for f in pkg.rglob("*.py"):
            if "__pycache__" not in f.parts:
                out[f.relative_to(pkg).as_posix()] = f
    return out

mods = {r: modules(r) for r in REPOS}
shared = {}
for r, m in mods.items():
    for name in m:
        shared.setdefault(name, []).append(r)

for name, repos in sorted(shared.items()):
    if len(repos) < 2 or name.endswith("__init__.py"):
        continue
    text = {r: mods[r][name].read_text(encoding="utf-8", errors="replace") for r in repos}
    ratios = [difflib.SequenceMatcher(None, text[a], text[b]).ratio()
              for a, b in combinations(repos, 2)]
    print(f"{name:34s} {len(repos)} {sum(ratios)/len(ratios)*100:5.0f}%",
          {r: len(text[r].splitlines()) for r in repos})
```

`zd` = csa-zendesk, `ws` = csa-google-workspace, `gc` = csa-google-gmail-calendar,
`sj` = csa-skilljar.

## The result

| module | servers | similarity | lines each | reading |
|---|---|---|---|---|
| `mcp/__main__.py` | 2 | **100%** | ws:3 gc:3 | identical, and trivial |
| `_markdown.py` | 2 | **96%** | gc:222 zd:219 | real duplication |
| `mcp/_success_page.py` | 2 | **95%** | ws:68 gc:68 | real duplication |
| `mcp/_logging.py` | 2 | 60% | ws:101 gc:86 | diverged sibling |
| `mcp/_auth_flow.py` | 2 | 59% | gc:184 ws:182 | diverged sibling |
| `mcp/_login.py` | 2 | 58% | ws:165 gc:148 | diverged sibling |
| `mcp/_tools/auth.py` | 2 | 38% | ws:321 gc:314 | diverged, and the vocabulary problem |
| `_environment.py` | 2 | 21% | ws:305 zd:183 | same shape |
| `mcp/_tools/feedback.py` | 3 | 20% | gc:138 ws:123 sj:51 | same shape |
| `auth.py` | 3 | 16% | gc:765 ws:563 sj:176 | same shape |
| `mcp/_tools/_base.py` | 3 | 15% | gc:320 ws:157 sj:125 | same shape |
| `mcp/_untrusted.py` | 2 | 11% | gc:142 ws:119 | same shape |
| `mcp/server.py` | 3 | 11% | gc:173 ws:161 sj:105 | same shape |
| `mcp/cli.py` | 3 | 10% | ws:199 gc:197 sj:99 | same shape |
| `mcp/_capabilities.py` | 2 | 8% | ws:152 gc:113 | vendor |
| `mcp/_flavours.py` | 2 | 8% | gc:154 ws:152 | vendor |
| `mcp/_config.py` | 3 | 7% | ws:453 sj:245 gc:149 | vendor |
| `exceptions.py` | 4 | 6% | zd:183 ws:114 sj:54 gc:38 | vendor |
| `_errors.py` | 2 | 5% | zd:155 ws:105 | vendor |
| `client.py` | 2 | 4% | sj:506 zd:183 | vendor |
| `mcp/_tools/config.py` | 2 | 4% | ws:192 gc:180 | vendor |
| `policy.py` | 4 | **3%** | ws:643 zd:543 sj:416 gc:236 | vendor |
| `mcp/_tools/demo.py` | 3 | 3% | sj:536 gc:420 ws:92 | vendor |
| `scopes.py` | 2 | 1% | sj:105 gc:101 | vendor |
| `backend.py` | 4 | **1%** | sj:2239 ws:1173 gc:1070 zd:1020 | vendor |
| `mcp/_schemas.py` | 2 | 1% | ws:1049 sj:613 | vendor |

## What the numbers mean

The distribution is bimodal, and that is the useful part. There is almost nothing between 21% and
38%. The fleet divides cleanly.

### Real duplication — extract

Three modules, around 290 lines in total. `_markdown.py` at 96% is the most consequential: it
implements the HTML→Markdown conversion that [DEC-018 in
CINO-Platform-Engineering](https://github.com/CloudSecurityAlliance-Internal/CINO-Platform-Engineering/blob/main/DECISIONS.md)
mandates fleet-wide. The roadmap that deferred extraction **predicted this specific copy** and
authorised it as a tracked, deliberate duplication.

Diffing the two copies is sharper than the similarity score. There are **19 changed lines and every
one of them is in the module docstring** — the transform itself is byte-identical. And the later
copy opens with *"Ported from csa-zendesk's `_markdown.py` (same problem, same fix)"*, which is the
provenance comment the roadmap required a deliberate copy to carry.

So this is not drift that needs investigating. It is a copy that recorded its own reason for
existing and is now ready to be retired on schedule. Two notes survive extraction as real content:
the Zendesk copy documents a measurement (*"Measured 2026-09-22: Zendesk's own plain-text rendering
is a naive tag strip — all five CSS-hidden probes survived into `body` while the CSS that reveals
them did not"*), and the Gmail copy documents which MIME part it is given. Both are callers'
concerns, not the transform's, and belong where the callers are.

### Diverged siblings — reconcile, then extract

The OAuth trio (`_auth_flow`, `_login`, `_logging`) sits at 58–60%, and all of it belongs to the two
Google servers. Fifty-eight percent is the dangerous number: close enough that sharing looks
obvious, different enough that one of the two behaviours would be silently discarded. **The
divergence is unresolved work, not a packaging problem.** Reconcile first, deliberately, then
extract the agreed result.

### Same shape, different content — convention, not code

`server.py` at 11%, `cli.py` at 10%, `_tools/_base.py` at 15%. Every server has these files and
they do corresponding jobs, but almost no text survives between them.

**This is the finding that shapes the architecture.** A base class over a 10%-similar structural
resemblance abstracts the *resemblance* rather than any shared behaviour, and every server then
writes code to escape it. What these want is a documented layout and a scaffolding template — see
[`ARCHITECTURE.md`](ARCHITECTURE.md), tier 3.

### Vendor surface — never extract

`backend.py` is 1020–2239 lines per server at **1%** similarity. `policy.py` is 236–643 lines at 3%.
This is where most of the code lives, and the measurement confirms it is correctly separate. No
amount of work on the shared library will make these smaller.

A useful consequence: **the shared library will stay small.** Anyone proposing to grow it past a few
hundred lines should be asked which measured number justifies it.

## One more measured thing: the vocabulary

`mcp/_tools/auth.py` at 38% understates the problem, because only two servers have the file at all.
The other two answer "am I authenticated?" from inside `server.py`, under different tool names, in
different shapes — one of them prose. Four servers, three answers, for the single question every
client asks first.

That is not duplication and extracting code will not fix it. It needs **one agreed status type**, so
a consumer holding several CSA servers does not have to learn a dialect per server. This is the one
item in the shared library that is a *contract* rather than a refactor.

## What was not measured

- **Tests.** Only `src/` was compared. Test duplication is likely higher and was not quantified.
- **`csa-google-workspace-audit`** has no code, so it contributed nothing — which is the limitation
  the original roadmap was built around. See [`DECISIONS.md`](DECISIONS.md) ADR-001.
- **Semantic duplication under different filenames.** Two servers solving the same problem in
  differently-named modules would not appear here at all. This method finds same-name pairs only,
  so the table is a floor on duplication, not a ceiling.
- **The other two "real duplication" pairs were not diffed line by line.** `_markdown.py` was, and
  the result changed the conclusion — the similarity score alone would have left open whether a bug
  fix had reached only one copy. `mcp/_success_page.py` (95%) deserves the same check before it
  moves.
- **Behavioural equivalence anywhere.** Text similarity is not behaviour. Two files can be 96%
  identical and differ in the 4% that matters; that is why extraction starts with a diff rather than
  a copy.
