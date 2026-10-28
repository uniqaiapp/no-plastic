# Edit prompts: change one thing, keep the person

An edit prompt (image-to-image, "edit this photo", Nano Banana conversational edits, Flux Kontext, inpainting with a text instruction) has a different failure mode from a generate prompt. The model does not invent a plastic face from nothing; it drifts: a slightly different jaw, a cleaner skin, a tighter crop, a re-lit background. The fix is a prompt with four locks around one change.

## The shape

```
1. The change     one verb, one target, the specifics of the new state
2. Identity lock  "Keep <list> exactly as they are"
3. Realism        how the new element must look real; "untouched real photograph"
4. Framing lock   "Do not change the framing, crop, camera angle, or anything not mentioned"
5. Seam rule      "no smudges, repeated textures, halos or visible seams"
```

The canonical closing pair, used verbatim in every edit example in this repo:

> Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.

`scripts/lint_prompt.py` detects an edit prompt by its opening verb and scores these five parts (identity lock and framing lock carry the most weight).

## Templates by edit type

### Remove an object or a person

> Remove the **stranger walking in the background behind her shoulder** and fill the space with **matching sand, sea and sky** so nothing looks patched. Keep the woman, her pose, the lighting and everything else exactly as they are. Output the full original frame at exactly the same zoom and position; do not crop, zoom in or recompose. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.

Always say what fills the hole. "Remove X" alone invites a smear or a repeated texture. Large objects that touch the subject get softer fills; say so in the review notes rather than fighting it.

### Replace the background

> Remove the entire background and replace it with **a plain, evenly lit pure white studio backdrop**. Keep **the man, his face, hair edges, sweater and position** exactly as they are. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.

Name the hair edges and fur edges explicitly; they are where the halo appears. For a coloured backdrop, add `with a soft natural shadow under it` so the object is grounded.

### Change clothes

> Change his outfit to **a tailored bottle-green wool overcoat over a cream cable-knit scarf**. Keep his face, skin, hair, expression, pose, the background and the light exactly as they are. The coat must look real: **visible wool weave, natural folds at the elbows, fabric that sits on the shoulders the way the original jacket did, light falling on it from the same direction as on his face**. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.

The sentence that makes or breaks clothing edits is the light continuity one: the new garment must be lit by the scene's light, not by a catalogue softbox.

### Change hair

> Change her hairstyle to **a chin-length curtain bob with soft waves, keeping the same brown hair colour**. Keep her face, skin, expression, clothes, the background and the light exactly as they are. The new hair must look real and salon-fresh: individual strands, natural hairline, realistic shine and volume, believable from every angle. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.

Say what stays (colour) as well as what changes (length, shape). Hair edits are where models most like to "improve" the face; the identity lock has to list `face, skin, expression`.

### Selfie to headshot

> Turn this selfie into **a professional business headshot: a dark navy blazer over a white top, a plain dark teal seamless background, sharp focus**. Keep the face, features, skin tone, hair, expression and identity exactly as they are. Professional headshot quality: the look of an 85 mm lens at f/2.8, one large soft key light with a gentle fill and a subtle rim, clean catchlights, natural skin texture with no plastic smoothing, crisp focus on the eyes, well-fitted clothes. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.

The risk is double: identity drift from the clothes change, and skin smoothing from the word "professional". The phrase `natural skin texture with no plastic smoothing` is doing real work here. Never add "make them look better", "younger", "slimmer"; that is a different (and ethically different) request.

### Restore, enhance, unblur

> Enhance this photo: **sharpen soft detail, reduce noise and grain, and balance the exposure so the face is clearly lit**. Keep the man, his expression, the colors and the composition exactly as they are. Make it look like the same photo taken with a much better camera, natural and not over-processed, natural skin texture with pores and stubble still visible, no plastic skin, no oversharpening halos. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.

"Enhance" is the most plastic-prone verb there is: every enhancer was trained on smoothing. `the same photo taken with a much better camera` is the sentence that steers it toward detail rather than wax. For old-photo restoration, add `keep it black and white as a clean, sharp print` or the model will colourise.

### Scene changes (season, time of day, weather)

> Change the season to **late autumn: amber and rust leaves on the trees and the ground, low backlit sun, thin mist in the distance, long soft shadows**. Keep the people, their clothes, poses and faces exactly as they are. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.

Decide whether the clothes change with the season. Leaving summer linen in an autumn scene is a deliberate choice (it tells the viewer what was edited); say it either way.

## What never goes in an edit prompt

- `8k`, `ultra realistic`, `masterpiece`, `photorealistic`: generation vocabulary; in an edit it increases drift.
- `smooth the skin`, `flawless`, `glowing`, `beautify`: the plastic look, requested explicitly.
- `reimagine`, `completely new`, `a different`: you no longer have an edit, you have a generation with a reference.
- A second change. One prompt, one change. Chain edits if you need two, and re-lint the chain's last prompt against the first image's facts.

## Review after an edit

Open the before and the after at the same zoom and flip between them. Three things move when an edit has drifted: the distance between the eyes, the hairline, and the exposure of the background. If any of them moved and the prompt did not ask for it, strengthen the identity lock (list the thing that moved by name) and run again. Do not accept "close enough" on faces of real people.
