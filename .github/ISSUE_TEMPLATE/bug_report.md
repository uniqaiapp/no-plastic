---
name: Bug report
about: The linter scores something wrongly, a rule produces worse images, or a test fails
title: "bug: "
labels: bug
---

## What happened

<!-- One or two sentences. -->

## Prompt that triggered it

```text
<!-- paste the prompt you linted or rewrote -->
```

## Command and output

```text
python3 scripts/lint_prompt.py ...
```

## Expected

<!-- What score, flag or rewrite you expected instead, and why. -->

## Model and settings (if the issue is about image results)

- Model (Flux, Nano Banana, Midjourney, SDXL, other):
- Mode (generate / edit), aspect, any parameters:
- Did you run a pilot (one image) before the batch?

## Checklist

- [ ] `python3 tests/run.py` result pasted above
- [ ] No personal data or real people's photos attached
