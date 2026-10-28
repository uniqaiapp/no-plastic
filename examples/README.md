# Examples

Nine before/after pairs. "Before" is the kind of prompt people actually type; "after" is the rewrite the skill produces. Each folder holds the two prompts and the two lint reports exactly as `scripts/lint_prompt.py` prints them. `tests/test_examples.py` re-runs the linter and fails if a report drifts, so the scores below are reproducible, not typed in.

Reproduce every row from the repo root:

```bash
python3 scripts/lint_prompt.py examples/*/before.txt examples/*/after.txt
```

| Example | Mode | What it shows | Before | After |
|---|---|---|---|---|
| [01-linkedin-headshot](01-linkedin-headshot) | generate | "8k masterpiece" headshot into an 85 mm brief with window light and skin texture | 0 (F) | 100 (A) |
| [02-couple-golden-hour](02-couple-golden-hour) | generate | "two people hugging, beautiful lighting" into a golden-hour candid with falloff and grain | 0 (F) | 100 (A) |
| [03-film-era-1970s](03-film-era-1970s) | generate | "retro vibes" into a 1974 Kodachrome slide with period objects and hard sun | 19 (F) | 100 (A) |
| [04-product-teapot](04-product-teapot) | generate | "octane render, 4k" product shot into a catalogue photograph with real glaze texture | 0 (F) | 100 (A) |
| [05-tag-soup-sdxl](05-tag-soup-sdxl) | generate | SDXL tag soup with `(flawless skin:1.2)` and the inherited negative list into prose plus a short negative | 0 (F) | 100 (A) |
| [06-edit-outfit](06-edit-outfit) | edit | "make him wear a green coat" into one change with identity, light-continuity and framing locks | 5 (F) | 100 (A) |
| [07-edit-remove-stranger](07-edit-remove-stranger) | edit | "remove the guy in the background" into a removal that says what fills the hole | 5 (F) | 100 (A) |
| [08-edit-enhance](08-edit-enhance) | edit | "make it HD and smooth the skin" into an enhance that keeps pores and stubble | 7 (F) | 100 (A) |
| [09-edit-selfie-to-headshot](09-edit-selfie-to-headshot) | edit | "turn my selfie into a LinkedIn headshot" into the selfie-to-headshot template with the identity lock | 15 (F) | 100 (A) |

Scores are the output of `scripts/lint_prompt.py` version 0.1.0 on these files. They measure what the prompt tells the model, not how the image came out; the skill's last step is always a pilot render reviewed against [references/checklist.md](../references/checklist.md).

## Where the "after" prompts come from

The generate briefs and the edit templates mirror the prompts UniqAI used to produce the illustrations on its own site: a shared photographic suffix (`50 mm lens at f/2, soft natural light, gentle filmic colour grade with creamy highlights and slightly lifted blacks, natural skin texture with visible pores, no retouched plastic look`) and a shared edit closing (`Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.`). Both were pilot fixes once; see [references/pilot-review.md](../references/pilot-review.md).

## Adding a pair

1. Create `examples/<nn>-<slug>/before.txt` and `after.txt`. Edit examples need `-edit-` in the folder name (the tests use it to assert the detected mode).
2. Run `python3 tests/regen_examples.py` to write the two reports.
3. Add a row above. `after.txt` must score 85 or more with no red flags, or the tests fail.
