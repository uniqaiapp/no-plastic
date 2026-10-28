# Pilot, review, then batch

The workflow that produced the illustration sets this repo is based on. It exists because a bad brief costs one image to discover and forty images to regret.

## 1. Group the jobs

List every image you need as a job with: an id, the prompt, the aspect, and one line on *why* it exists (which page, which claim it illustrates). Mark one job per prompt *family* as the pilot: the headshot family, the product family, the 1970s family. The pilot is the job whose failure teaches the most, usually the one with a face.

A minimal job file:

```json
{
  "id": "headshot-business",
  "kind": "generate",
  "aspect": "3:4",
  "pilot": true,
  "prompt": "...the full brief...",
  "why": "Headshot page, first card. Face at the top of the frame because the tile crops the bottom."
}
```

For edits, add `"from": "<id of the source image>"` and keep the before and after as a pair; a before/after that was not produced from the same source is not a before/after.

## 2. Add the shared suffix once

Rules that apply to every job (adults only, no text, no logos, no brand marks, aspect handling) live in one shared suffix appended by the script that runs the jobs, not in each prompt. Keeps the prompts readable and the rule changeable in one place. The suffix we use is short:

> No text, no logos, no brand marks. Adults only.

## 3. Lint every prompt before any render

```bash
python3 scripts/lint_prompt.py --strict --min-score 70 jobs/*.txt
```

A prompt under 70 does not get rendered. Fix the brief, not the seed.

## 4. Render the pilots only

One image per pilot. Lowest cost tier that still shows skin texture (medium quality is enough to judge pores; preview tiers are not).

## 5. Review against the checklist

Open each pilot at 100 % and run the five-second review in `checklist.md`. Write the result next to the job:

```
headshot-business   pilot  PASS   pores visible, catchlight matches key, hairline ok
product-teapot      pilot  FAIL   glaze reads as CGI; no speckle. Add "visible glaze speckle and tiny pits", re-pilot
1974-picnic         pilot  FIX    modern bottle on table; add "no modern objects anywhere", one re-roll
```

Decision rule: **two or more tells, fix the brief; one tell, add one line and re-roll once; zero, batch.** Never re-roll more than twice on the same brief; a third failure means the brief is wrong, not the seed.

## 6. Propagate the fix to the family

What fixed the pilot goes into every prompt in that family, verbatim, before the batch runs. That is how a shared phrase like `natural skin texture with visible pores, no retouched plastic look` ends up in every portrait prompt: it was a pilot fix once.

## 7. Batch, then spot-check

Render the rest. Spot-check one in five at 100 %, and every image with a face. Log what you rejected and why; the log is the next version of the checklist.

## 8. Provenance

Keep the model id and the exact prompt next to each image you publish (a `generated.json` or similar). When you show the image, say what it is: "AI-generated illustration" is honest, "sample output of our app" is a claim you must be able to back with the real pipeline. Do not show a generated image as a photo of a real person or a real product.

## Cost note

A pilot-first run spends a handful of extra images per family and typically saves a batch. We do not publish a percentage because it depends entirely on how wrong the first brief was; in our own runs, the families that needed a second pilot were the ones with faces and the ones with glossy materials.
