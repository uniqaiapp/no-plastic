# The photographic brief

A prompt that avoids the plastic look is a brief a photographer could shoot. It has eight fields, written as three to five sentences in this order. `scripts/lint_prompt.py --brief prompt.txt` prints this skeleton with whatever the prompt already covers filled in.

```
1. Subject       who or what, age range, two or three physical facts, what they are doing
2. Composition   framing, where the subject sits, aspect / orientation
3. Camera        focal length, aperture, or the device ("phone main camera, 24 mm equivalent")
4. Light         source, direction, size / quality, fill, time of day
5. Palette       grade, film stock or "true-to-life colour", contrast behaviour
6. Texture       skin, hair, fabric, material, grain: the imperfections you want
7. Era / medium  "editorial lifestyle photograph", "1974 Kodachrome slide", "honest phone selfie"
8. Negatives     the looks to avoid, phrased positively where the model ignores negatives
```

A worked example (from `examples/01-linkedin-headshot/after.txt`):

> **[Subject]** Head-and-shoulders business headshot of a woman in her early fifties with pale skin, a silver-grey bob and small hoop earrings, wearing a dark tailored blazer over a white top, a small relaxed smile, shoulders turned slightly off camera. **[Composition]** A bright modern office with glass partitions and plants blurred softly behind her, face in the upper two thirds of a vertical frame. **[Camera + Light]** The look of an 85 mm lens at f/2.8: one large soft key light from camera left with a gentle fill and a subtle rim on the hair, clean catchlights, crisp focus on the eyes. **[Palette]** Clean neutral daylight with no colour cast. **[Texture + Negatives]** Natural skin texture with visible pores and fine lines, a few flyaway hairs, no retouched plastic look, not over-processed.

## Vocabulary

Words the models respond to because they occur in real photo captions and EXIF-tagged archives. Pick one or two per field; stacking does not help.

### Camera and lens

| Intent | Say |
|---|---|
| Classic headshot | `85 mm lens at f/2.8`, `105 mm at f/4` |
| Environmental portrait | `35 mm at f/2.8`, `50 mm at f/2` |
| Lifestyle, candid | `50 mm lens at f/2, shallow depth of field` |
| Selfie, honest | `front-camera phone selfie at arm's length, 26 mm equivalent, slight wide-angle perspective` |
| Everyday phone photo | `shot on a modern flagship phone main camera, 24 mm equivalent, natural HDR` |
| Product, catalogue | `90 mm lens at f/8, everything in focus` |
| Film era | `35 mm film camera`, `point-and-shoot with on-camera flash`, `medium format, 80 mm` |
| Soft vintage | `slight vignette and soft focus at the edges` |

### Light

| Intent | Say |
|---|---|
| Studio, flattering | `one large soft key light from camera left with a gentle fill and a subtle rim` |
| Window | `large soft window light from camera left`, `north-facing window, overcast` |
| Golden hour | `low golden sun from behind rimming the hair, warm bounce on the shadow side` |
| Flat daylight | `overcast soft light`, `open shade, no squinting` |
| Hard | `midday sun from high left with dappled shade`, `harsh on-camera flash, slightly overexposed` |
| Night | `a small lamp, underexposed, high-ISO noise in the shadows`, `candlelight behind her` |
| Falloff | `light falls off toward the background`, `background a stop darker than the face` |

### Palette and grade

`true-to-life colour, no colour cast` · `gentle filmic colour grade with creamy highlights and slightly lifted blacks` · `muted palette of camel, concrete grey and black` · `Kodachrome: saturated reds and teal greens, warm faded highlights` · `clean black and white, soft film grain` · `neutral daylight` · `warm tones from the tungsten lamp`

### Texture

`natural skin texture with visible pores` · `fine lines around the eyes` · `freckles` · `peach fuzz along the jaw` · `stubble` · `a few flyaway hairs, natural hairline` · `individual strands` · `wool with visible weave` · `creased linen` · `fine film grain` · `a little high-ISO noise` · `weathered wood grain` · `glaze speckle and tiny pits` · `scuffs`, `dust`, `fingerprints` · `a light sheen of sweat`

### Era and medium

`editorial lifestyle photograph` · `beauty-editorial portrait` · `honest everyday photo rather than a staged ad` · `candid snapshot` · `authentic 1974 Kodachrome slide` · `late-1990s point-and-shoot with flash` · `1950s studio portrait` · `high-end catalogue product photograph` · `documentary street photograph` · `family photo album print`

### Negatives

For models that take a negative field (SDXL, Midjourney `--no`), keep it short and specific: `smooth skin, airbrushed, doll-like, symmetrical face, render, text, logo`.

For models that ignore negatives (Flux, Nano Banana), phrase the same thing positively at the end of the prompt: `natural skin texture with visible pores, no retouched plastic look, not over-processed, not a render`. Short "no X" clauses inside a sentence work; a list of twenty negatives does not.

## Anti-plastic rules (the part you can paste)

These sentences appear, in some form, in every prompt that produced a usable image for us. They are the "rules" the skill adds when the user has not.

- `natural skin texture with visible pores, no retouched plastic look`
- `slight asymmetry: head tilted a few degrees, a half smile with one side higher`
- `light falls off toward the background; shadow side of the face visible`
- `fine film grain` or `a little high-ISO noise in the shadows`
- `not over-processed, no oversharpening halos`
- `honest everyday photo rather than a staged ad` (for anything that should look real rather than editorial)

## Lengths

A working brief is 40 to 120 words. Under 15 the model fills every gap with its defaults (which are the plastic look). Over about 180, later clauses lose weight, and SDXL's text encoder truncates at 77 tokens, so put the subject, light and texture sentences first.
