# Friction

What cost time, and what it taught. Kept so the same cost is not paid twice.

## Measurement caught two of my own wrong premises before they were published

Both would have survived review, because both were plausible and neither was checkable without
running something.

- **A similarity score read as behavioural drift.** `_markdown.py` measured 96% identical across
  two servers, and 222 against 219 lines. I wrote "3 lines of drift", inferring it from the length
  difference. Diffing showed **19 changed lines, every one in the module docstring**, with
  byte-identical transform code. The correct reading is the opposite of the one I wrote: this is a
  tracked copy reaching its scheduled retirement, not drift needing investigation.
- **A deliberate design read as a defect.** An empty `[mcp]` extra in `csa-skilljar` was
  characterised - in CINO-PE's own dependency review - as an extra that "reads as meaningful and
  does nothing". The file says why it exists: a no-op compatibility alias for anyone who copied
  `csa-skilljar[mcp]` from an early README. It is the model for retiring `csa-zendesk`'s
  `[server]`, not a thing to fix.

**The rule:** for any claim you will act on, read the actual file. A similarity score is not a
diff, and a summary of a config is not the config.

## A grep narrower than the property it was testing

Searching for deprecated protocol features with a loose pattern returned `ping` in **117 files** -
it is a substring of "mapping" and "shipping". Word boundaries turned that into a clean measured
negative: no server uses Roots, Sampling, Logging or `ping`. The loose version would have produced
a false alarm about three deprecations.

## Heredoc quoting, repeatedly

Writing documents containing backticks, apostrophes and mixed quotes through a shell heredoc
failed at parse time and, earlier in the same work, once applied an edit *silently incompletely*
because a Windows path contained a backslash escape. Prose with mixed quoting goes through a file
write, not a heredoc.

## The fleet-wide finding this repository surfaced by accident

Checking which core files the four servers carry revealed **four different shapes for the decision
log**: a root `.md` file (`csa-zendesk`, `csa-skilljar`), a file under `docs/`
(`csa-google-workspace`), and a *directory* of one-ADR-per-file (`csa-google-gmail-calendar`). This
repository adds a fifth convention with `docs/DECISIONS.md`.

It does not matter while they are four repositories. It matters the moment they are one tree, and
it is cheap now and annoying later. It is in [`TODO.md`](TODO.md) and belongs in the migration's
step 4, alongside the dependency convergence.

I also got this wrong on the first pass - I recorded `csa-google-gmail-calendar` as having no
decision log at all, because I looked for a file and it keeps a directory.
