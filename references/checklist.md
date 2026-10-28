# The AI-tells checklist

What makes an AI image read as "AI" at a glance, and the prompt line that fixes each tell. Use it twice: when writing the brief (fold the fixes in) and when reviewing the pilot image (tick what you see). `scripts/lint_prompt.py` tests the prompt side of this list; the image side is your eyes.

The underlying rule: models are rewarded for the average of what people liked, and people liked smooth, even, symmetrical, glowing. A real photograph is none of those. Every fix below adds one specific imperfection or one specific physical constraint.

## Skin and face

| Tell | What you see | Prompt fix |
|---|---|---|
| Plastic skin | No pores, no fine lines, a waxy sheen, the same texture on forehead and cheek | `natural skin texture with visible pores`, `fine lines around the eyes`, `peach fuzz along the jaw`; never `flawless`, `smooth`, `glowing`, `porcelain` |
| Dead symmetry | Both eyes identical, both brows at the same height, the smile perfectly centred | `a half smile with one side higher`, `slight asymmetry`, `head tilted a few degrees`, `one eyebrow slightly raised` |
| Catchlight clone | A single bright catchlight placed identically in both eyes, or none at all | Name the light source; a `large soft window` or `softbox` gives a natural shaped catchlight. Add `clean catchlights` once, not `sparkling eyes` |
| Uniform tone | One skin colour from hairline to collar, no blush, no redness | `uneven blush on the cheeks`, `slight redness around the nose`, `sun-flushed`, `a little shine on the forehead` |
| Teeth and lips | Veneer-white teeth, lip gloss everywhere | `natural off-white teeth`, `matte lips`, or close the mouth: `relaxed closed-mouth expression` |
| Hair helmet | Every strand in place, a glossy continuous sheet | `a few flyaway hairs`, `individual strands`, `natural hairline with baby hairs`, `hair slightly tangled in the collar` |
| Age blur | "Woman" renders as 25 with no history | Give an age range and a trace of it: `in her early fifties`, `grey at the temples`, `laugh lines` |

## Light

| Tell | What you see | Prompt fix |
|---|---|---|
| Light from nowhere | Face evenly lit, no shadow side, no direction | `one large soft key light from camera left with a gentle fill`, `window light from the right` |
| No falloff | Background as bright as the face; everything at the same exposure | `light falls off toward the background`, `background a stop darker`, `vignette from the lens` |
| Hero rim everywhere | A glowing outline on every edge, hair on fire | At most `a subtle rim on the hair and one shoulder`; never `rim light` unqualified |
| Golden hour syrup | Everything orange, including the shadows | `golden-hour backlight with cool bounce on the shadow side`, or pick `overcast` or `open shade` instead |
| Impossible shadows | Shadows pointing two ways, or none under the chin | Name one source and its height: `low sun from behind`, `midday sun from high left`, `overhead softbox` |
| Volumetric fog | God rays indoors, haze in a kitchen | Delete `volumetric`, `god rays`, `cinematic lighting`. Describe the room's real light |

## Lens and camera

| Tell | What you see | Prompt fix |
|---|---|---|
| No perspective | Faces with zero distortion, everything at infinity | Name the focal length and distance: `85 mm at f/2.8` for headshots, `35 mm` for environment, `26 mm front camera at arm's length` for selfies |
| Bokeh paint | Perfectly creamy blur at every depth, no transition | `shallow depth of field, ears slightly softer than the eyes`, `background blurred into soft shapes, not a painted wash` |
| Everything sharp | Eyes, hair, background and hands all equally crisp | Give the aperture a job: `f/2 so only the eyes and nose are sharp`; for product work `f/8, everything in focus` is a real choice, say it |
| Phone vs camera | Phone-style HDR on a studio shot, or studio depth on a phone shot | Decide and say: `honest phone photo, natural HDR, true-to-life colour` or `editorial photograph, 50 mm, f/2` |

## Colour and grade

| Tell | What you see | Prompt fix |
|---|---|---|
| Teal-and-orange | Every image graded like a trailer | `true-to-life colour`, `neutral daylight, no colour cast`, or a named film: `Kodachrome reds and teal greens, warm faded highlights` |
| Crushed blacks, blown whites | Contrast dialled to the end | `slightly lifted blacks`, `creamy highlights`, `gentle filmic grade` |
| Saturation | Skin tones orange, greens neon | `muted palette`, `desaturated greens`, `natural skin tones` |
| Plastic white | Pure white backdrops with no gradient | `warm off-white seamless`, `mid-grey seamless with a soft gradient`, `one soft shadow under the object` |

## Texture and material

| Tell | What you see | Prompt fix |
|---|---|---|
| Smooth everything | Wool like plastic, wood like laminate, stone like foam | Name the material and its flaw: `wool with visible weave`, `weathered wood with grain and knots`, `stoneware with speckle and tiny pits` |
| No grain | Digital-clean at every ISO | `fine film grain`, `a little high-ISO noise in the shadows` |
| Fabric that floats | Clothes with no weight or folds | `fabric sits on the shoulders`, `natural folds at the elbows`, `creased linen` |
| New everything | No wear, no dust, no fingerprints | `lived-in`, `a little real-life clutter`, `scuffs on the sneaker`, `dust on the slide` |

## Composition and scene

| Tell | What you see | Prompt fix |
|---|---|---|
| Centred bullseye | Subject dead centre, eye level, every time | `subject slightly off-centre on the left third`, `face in the upper two thirds of a vertical frame`, `slightly tilted horizon` |
| Stock-photo pose | Arms crossed, head tilted, laughing at salad | Give an action: `mid-stretch`, `looking just past the camera`, `reading the menu`, `eyes closed` |
| Props with no story | A coffee cup because it is a cafe | Tie props to the subject: `a thermos and glass soda bottles on the table`, `a kettle out of focus behind her` |
| Era leakage | A 1970s scene with a modern car | `no modern buildings or objects anywhere`, name period clothes and objects |
| Text and logos | Garbled lettering, invented brands | `no text, no logos, no brand marks` (one of the few negatives worth keeping) |

## Words that cause tells (remove them)

`masterpiece`, `best quality`, `8k`, `4k`, `ultra realistic`, `hyperrealistic`, `highly detailed`, `intricate`, `award winning`, `trending on artstation`, `octane render`, `unreal engine`, `photorealistic`, `flawless`, `perfect skin`, `smooth skin`, `glowing skin`, `porcelain`, `symmetrical face`, `cinematic lighting`, `dramatic lighting`, `studio lighting` (unqualified), `volumetric`, `beautiful`, `stunning`, `gorgeous`, `aesthetic`, `vibes`.

`scripts/lint_prompt.py` flags all of these.

## The five-second review

When the pilot image comes back, look at these in order and stop at the first failure:

1. Forehead and cheek at 100 %: is there pore texture, and does it differ between the two?
2. Shadow side of the nose: is there one, and does it agree with the stated light?
3. Eyes: one catchlight shape, matching the stated source, with slightly different highlights in each eye?
4. Hair edges and hairline: individual strands, or a sheet?
5. Background: does it fall off in light and sharpness, or is it as crisp and bright as the face?

Two or more failures: fix the brief, do not re-roll. One failure: re-roll once with the specific fix added. Zero: batch.
