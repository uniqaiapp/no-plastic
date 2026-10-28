## What changed

<!-- One paragraph. If a rule changed, include a before/after prompt pair. -->

## How to test

```bash
python3 tests/run.py
```

<!-- If you changed the linter, regenerate the committed reports and include the diff:
     python3 tests/regen_examples.py -->

## Honesty check

- Any new numbers in README or docs? Where do they come from (command in this repo, or dated source URL)?
- Any model-specific claim? Which model, which version, which prompt reproduces it?

## Checklist

- [ ] Tests pass locally (`python3 tests/run.py`)
- [ ] No personal names, personal accounts or secrets added
- [ ] No new dependencies (Python 3 stdlib only)
- [ ] `SKILL.md` is still under 500 lines; long material went to `references/`
