# Model notes

How the same brief is delivered to each model family. These are working notes from producing illustration sets, not benchmarks: where we say "tends to", we mean "in the images we reviewed", and your results will differ by version and settings. Corrections with a reproducing prompt are welcome as issues.

## Summary

| Model | Negative field | Prompt style that works | Where the plastic comes from |
|---|---|---|---|
| Flux (dev / pro, Kontext for edits) | none in most pipelines; "no X" inside the sentence is understood | natural sentences, the full eight-field brief | over-clean skin and symmetric faces when the prompt has no texture sentence; "cinematic" vocabulary |
| Nano Banana (Gemini image) | none; conversational | natural sentences; edits as instructions on the uploaded image | enhancer-style smoothing on edits unless told "natural skin texture, no plastic smoothing" |
| Midjourney (v6 and later) | `--no a, b` | shorter sentences; `--style raw` keeps it photographic; lower `--stylize` | the house "MJ look" (glow, symmetry, painterly skin) at default stylize |
| SDXL and fine-tunes | separate negative prompt, weights `(x:1.2)` | the brief fits in 77 tokens if the subject/light/texture sentences come first | tag soup and the "masterpiece, best quality" ritual; over-weighted `flawless skin` |

## Flux

- Write the brief as prose. Flux reads full sentences well and keyword lists poorly.
- Negatives: there is no negative prompt in the common Flux pipelines (guidance-distilled). Put the avoidances in the last sentence as short clauses: `no retouched plastic look, not over-processed, not a render`. Long negative lists are ignored.
- Texture must be asked for. Without `natural skin texture with visible pores` Flux returns smooth, well-lit, symmetric faces by default.
- Guidance: lower guidance values keep skin more natural; high guidance pushes toward saturated, over-defined images. Treat the pipeline default as the ceiling, not the floor.
- Edits (Kontext): one change per prompt, the four locks from `edit-prompts.md`. Kontext respects "keep X exactly" well when X is listed by name.

## Nano Banana (Gemini image models)

- Conversational: you can say `Turn this selfie into a business headshot...` and refer to "the man", "her hair", "the background" directly. The templates in `edit-prompts.md` were written for this model and work as-is.
- Identity is strong on edits; the drift to watch is skin smoothing and exposure "correction". The sentence `natural skin texture with no plastic smoothing` fixes most of it.
- No negative field. "No X" inside a sentence works; a trailing list does not.
- Output is square in some products; say `Square frame, subject centred` or ask for the aspect you need explicitly, because the crop is part of the composition field.
- Text, logos and brand marks: say `no text, no logos` in the prompt; it is one of the few negatives worth keeping.

## Midjourney

- Add `--style raw` for anything meant to look like a photograph; the default style layer is where the glow and the painterly skin come from.
- Lower `--stylize` (for example `--s 50`) keeps the brief in charge; the default adds "MJ aesthetic".
- `--no smooth skin, airbrushed, render, text` is honoured but short lists work better than long ones.
- Keep the prose but trim it: Midjourney weights early words more, so subject and light go first, era and negatives last.
- Aspect goes in `--ar 4:5`; do not also write "vertical frame" in the prose, pick one.
- The linter strips `--ar`, `--style`, `--s` before scoring and treats `--no` as the negative part.

## SDXL and fine-tunes (Juggernaut, RealVis, etc.)

- The brief fits: subject, framing, camera, light, texture sentences first, era and palette after. CLIP truncates at 77 tokens, so what comes after the first ~55 words is weak.
- Negative prompt: `smooth skin, airbrushed, doll-like, symmetrical face, render, 3d, text, logo`. Drop the inherited ritual (`bad anatomy, extra fingers, worst quality, watermark...`): it was written for SD1.5 and spends tokens without moving an SDXL result.
- Do not weight `(flawless skin:1.2)`; that is the plastic look with a multiplier. If you weight anything, weight the texture: `(natural skin texture, visible pores:1.1)`.
- Tag soup (`portrait, woman, 25yo, freckles, bokeh, 85mm`) still works on SDXL but reads as "render" to the model's photo priors; sentences get you closer to the photographic manifold. `examples/05-tag-soup-sdxl` shows the rewrite.
- Upscalers and face-restoration passes (GFPGAN, CodeFormer at high fidelity weight) add their own plastic; run them at low strength or not at all on portraits that already have texture.

## Upscaling and enhancement (any model)

Enhancers were trained on "before: noisy, after: smooth". Every enhance prompt needs the realism clause from `edit-prompts.md` (`the same photo taken with a much better camera, natural and not over-processed`), and the review step should compare skin at 100 % before and after. If the after has fewer pores than the before, it is not enhanced, it is retouched.
