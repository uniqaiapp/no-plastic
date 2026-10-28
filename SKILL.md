---
name: no-plastic
description: Rewrites image-generation prompts into photographic briefs that avoid the plastic AI look (natural skin texture, asymmetry, real light falloff, lens and film choices, honest negatives), writes edit prompts that keep identity and framing, and lints any prompt against the anti-plastic checklist with scripts/lint_prompt.py. Use when the user asks for a portrait, headshot, product or lifestyle image prompt for Flux, Nano Banana, Midjourney or SDXL, says an AI image looks fake, waxy, too smooth, plastic or "like AI", wants to fix skin texture, pastes a prompt to improve, or writes an edit prompt (remove, replace, change outfit, enhance) that must keep the person and the crop. Not for illustration, anime or 3D-render styles, for video prompts, or for editing photos of real people without their consent.
license: MIT
metadata:
  version: 0.1.0
  author: UniqAI
  homepage: https://github.com/uniqaiapp/no-plastic
---

# no-plastic: photographic briefs instead of plastic prompts

AI images look like AI for a short list of reasons: poreless skin, symmetric faces, light from nowhere, bokeh painted on, teal-and-orange grade, no grain, everything new. Each of those is the model's default, and each has a sentence that overrides it. This skill turns a loose request ("professional headshot of a woman, 8k") into a brief a photographer could shoot, or turns a loose edit ("remove the guy in the back") into an instruction that changes one thing and keeps everything else. The most common trigger is a user pasting a prompt or a result and saying it looks fake.

## When to use

- The user wants a prompt for a portrait, headshot, couple, lifestyle, product or interior image and wants it to read as a photograph.
- The user shows or describes a result that is "too smooth", "waxy", "plastic", "fake", "looks like AI", "too perfect".
- The user pastes an existing prompt (any model) and asks to improve it.
- The user writes an edit instruction for an existing photo: remove, replace background, change outfit or hair, enhance, restore, selfie to headshot.
- The user is about to render a batch of images and wants them consistent.

## When NOT to use

- Illustration, anime, 3D, concept art, logos: the "plastic" look is often the goal there, and the checklist would fight it.
- Video prompts: the vocabulary overlaps, but motion, duration and shot lists are a different skill.
- Edits of photos of real people the user has no right to edit, or edits meant to deceive (a "photo" of someone doing something they did not do). Decline those.
- Requests to make a real person look younger, thinner or "better": that is retouching, and this skill's rules point the other way. Say so and offer the honest version (better light, better crop).

## How it works

1. **Classify.** Decide whether the request is a *generate* prompt (text to image) or an *edit* prompt (instruction on an existing image). Edits start with a verb (remove, change, turn this selfie into, enhance). When unclear, ask one question.
2. **Lint what exists.** If the user gave a prompt, run it: `python3 scripts/lint_prompt.py --brief prompt.txt` for generate prompts (prints the eight-field brief with the gaps), `python3 scripts/lint_prompt.py prompt.txt` for edits (prints the five locks and what is missing). Read the flags; they name the words that cause the plastic look.
3. **Critique in one paragraph.** Tell the user what the prompt is missing in photographic terms (no light direction, no texture, "8k masterpiece" pulling toward CGI) and which tells that will produce. Keep it to the three most important gaps.
4. **Rewrite as a brief.** For generate prompts, write three to five sentences in this order: subject and action; framing; camera and light; palette, texture and era; negatives. For edit prompts, write one change plus the four locks (identity, realism, framing, seams). The templates and vocabulary are in [references/brief-template.md](references/brief-template.md) and [references/edit-prompts.md](references/edit-prompts.md). Always include the anti-plastic rules below unless the user explicitly wants a stylised result.
5. **Adapt to the model.** Flux and Nano Banana take prose and ignore negative lists (phrase avoidances positively in the last sentence). Midjourney gets `--style raw`, a lower `--stylize`, and a short `--no`. SDXL gets the brief with subject, light and texture first (77-token limit) and a short negative field. Details per model in [references/model-notes.md](references/model-notes.md).
6. **Re-lint and show the score.** Run `python3 scripts/lint_prompt.py` on the rewrite; aim for 85 or higher with no red flags. Show the user before and after scores; they are the output of the script, not an opinion.
7. **Pilot, then batch.** Tell the user to render one image, review it with the five-second check in [references/checklist.md](references/checklist.md) (forehead texture, nose shadow, catchlights, hairline, background falloff), and only then render the rest. For sets, follow [references/pilot-review.md](references/pilot-review.md).

## The anti-plastic rules

Fold these into every photographic brief; they are the sentences that override the model's defaults.

| Default the model has | Rule to add |
|---|---|
| Poreless, waxy skin | `natural skin texture with visible pores` (+ `fine lines`, `freckles`, `stubble`, `peach fuzz` where true) |
| Mirror-symmetric face | `slight asymmetry: head tilted a few degrees, a half smile with one side higher` |
| Even light with no direction | name the source and side: `large soft window light from camera left with a gentle fill` |
| No falloff | `light falls off toward the background`, `shadow side of the face visible` |
| Digital-clean | `fine film grain` or `a little high-ISO noise in the shadows` |
| Over-processed | `not over-processed, no oversharpening halos, no retouched plastic look` |
| Everything new | one imperfection per material: `wool with visible weave`, `scuffs`, `lived-in` |
| Render vocabulary | delete `8k`, `masterpiece`, `ultra realistic`, `cinematic lighting`, `flawless`, `glowing`; they are the plastic look by name |

## Edit prompts: one change, four locks

```
<verb> <one target> to <specific new state>.
Keep <face, skin tone, hair edges, expression, clothes, background, light> exactly as they are.
<how the new element must look real; light falling on it from the same direction>.
Do not change the framing, crop, camera angle, or anything not mentioned.
The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.
```

For removals, say what fills the hole (`matching sand, sea and sky`). For enhance and restore, add `the same photo taken with a much better camera, natural and not over-processed, no plastic skin`. Full templates per edit type: [references/edit-prompts.md](references/edit-prompts.md).

## Inputs / outputs

| Input | Output |
|---|---|
| A loose request ("headshot of a woman in a blazer") | A brief of 40-120 words, the model-specific variant if a model was named, and the lint score |
| An existing prompt | Critique (three gaps), flagged words, rewritten brief, before/after scores |
| An edit request + description of the source photo | The edit instruction with the four locks, and what to check after the render |
| A set of images to produce | A job list with pilots marked, the shared suffix, and the review log format |

## Examples

Nine before/after pairs with their lint reports live in [examples/](examples/README.md). Reproduce any of them from the repo root:

```bash
python3 scripts/lint_prompt.py examples/01-linkedin-headshot/before.txt examples/01-linkedin-headshot/after.txt
python3 scripts/lint_prompt.py --brief examples/05-tag-soup-sdxl/before.txt
python3 scripts/lint_prompt.py --json examples/07-edit-remove-stranger/after.txt
```

## Limits

- The linter reads words, not pixels. A prompt can score 100 and still render badly on a given seed; the pilot step exists because of that. A prompt can also score low and work, if the model's defaults happen to suit it.
- It is English-only and regex-based. Synonyms it does not know count as missing; add them in `scripts/lint_prompt.py` and send a PR.
- Model notes are observations from our own illustration runs on the versions available at the time, not benchmarks. Versions change; re-pilot.
- It does not detect or prevent misuse (deepfakes, non-consensual edits). The "When NOT to use" rules are the agent's responsibility.
- Stylised looks (editorial beauty retouching, fashion gloss) are legitimate; if the user wants them, say which rules you are dropping rather than quietly applying the checklist.

## References

- [references/checklist.md](references/checklist.md): the AI tells, the fix for each, and the five-second review.
- [references/brief-template.md](references/brief-template.md): the eight fields and the vocabulary per field.
- [references/edit-prompts.md](references/edit-prompts.md): templates per edit type and the four locks.
- [references/model-notes.md](references/model-notes.md): Flux, Nano Banana, Midjourney, SDXL delivery notes.
- [references/pilot-review.md](references/pilot-review.md): the job-list, pilot and review workflow for sets.
