<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="no-plastic by UniqAI" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#install)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#install)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#install)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme&utm_campaign=no-plastic)

**Fix plastic skin and fake-looking AI portraits: prompt rules, edit locks, and a linter.**

[Quickstart](#quickstart) · [How it works](#how-it-works) · [Examples](#examples) · [Install](#install) · [FAQ](#faq)

</div>

English · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português (BR)](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# no-plastic: fix plastic skin and fake-looking AI portraits

AI portraits look fake for a short list of reasons: poreless skin, a mirror-symmetric face, light from nowhere, bokeh painted on, teal-and-orange grade, no grain. Each one is the model's default, and each has a sentence that overrides it. no-plastic is a Claude Code skill (with Cursor and Codex adapters) that rewrites your image prompt into a photographic brief with those sentences in it, writes edit prompts that change one thing and keep the person, and ships a zero-dependency linter that scores any prompt against the checklist. Written for Flux, Nano Banana, Midjourney and SDXL; the vocabulary is photography, so it carries to the next model too.

| **Brief, not tags** | **Edits that keep the face** | **Lint before you render** |
|:---|:---|:---|
| Subject, framing, camera, light, palette, texture, era, negatives: eight fields, three to five sentences, the anti-plastic rules folded in. | One change plus four locks (identity, realism, framing, seams), with templates for remove, background, outfit, hair, enhance and selfie-to-headshot. | `scripts/lint_prompt.py` scores coverage, flags the words that cause the plastic look, and prints a brief skeleton for the gaps. Python 3 stdlib only. |

## Quickstart

```bash
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
cd ~/.claude/skills/no-plastic
python3 scripts/lint_prompt.py examples/01-linkedin-headshot/before.txt examples/01-linkedin-headshot/after.txt
```

You should see the first prompt ("professional headshot of a beautiful woman, perfect skin, 8k...") score 0/100 with the words that sink it listed, and the rewritten brief score 100/100. Then in Claude Code type `/no-plastic` and paste a prompt, or just say "this looks plastic" with the prompt attached.

## Demo

<img alt="no-plastic demo: linting a plastic prompt and its rewrite" src="assets/demo.svg" width="820">

## How it works

1. **Classify.** A *generate* prompt (text to image) or an *edit* prompt (an instruction on an existing photo: remove, change outfit, enhance, selfie to headshot). The linter auto-detects by the opening verb.
2. **Lint.** `python3 scripts/lint_prompt.py --brief prompt.txt` prints the eight-field brief with the phrases it found and `?` where the prompt is silent; the plain report lists the flagged words (`8k`, `masterpiece`, `flawless skin`, `cinematic lighting`, tag soup, the SD1.5 negative ritual) and what each costs.
3. **Critique and rewrite.** The skill names the three biggest gaps in photographic terms and rewrites the prompt as a brief: subject and action; framing; camera and light; palette, texture and era; negatives. The anti-plastic rules are always in: `natural skin texture with visible pores`, `slight asymmetry`, a named light source with falloff, `fine film grain`, `not over-processed, no retouched plastic look`.
4. **Adapt per model.** Flux and Nano Banana get prose with the avoidances phrased positively (they ignore negative lists); Midjourney gets `--style raw`, a lower `--stylize` and a short `--no`; SDXL gets the brief with subject, light and texture in the first 77 tokens and a short negative field. See [references/model-notes.md](references/model-notes.md).
5. **Pilot, then batch.** Render one image, run the five-second review (forehead texture at 100 %, nose shadow, catchlights, hairline, background falloff), fix the brief rather than re-rolling, then render the set. This is the workflow UniqAI used to produce the illustrations on its own site; [references/pilot-review.md](references/pilot-review.md) has the job-list format and the decision rule.

```
loose request ──▶ lint (gaps + flags) ──▶ brief / edit with locks ──▶ per-model variant ──▶ re-lint ≥ 85 ──▶ pilot ──▶ review ──▶ batch
```

The scores in this README are produced by `python3 scripts/lint_prompt.py` on the files in `examples/`; `tests/test_examples.py` fails if they drift. The linter reads words, not pixels: a 100 is a complete brief, not a guaranteed image. That is what the pilot is for.

## Examples

Nine pairs with reports in [examples/](examples/README.md). Two of them in full:

<details open>
<summary><b>Headshot: "8k masterpiece" → 85 mm brief (0 → 100)</b></summary>

**Before** (`examples/01-linkedin-headshot/before.txt`, score 0/100)

```text
Professional headshot of a beautiful woman, perfect skin, studio lighting, 8k, ultra realistic, masterpiece, sharp focus
```

**After** (`examples/01-linkedin-headshot/after.txt`, score 100/100)

```text
Head-and-shoulders business headshot of a woman in her early fifties with pale skin, a silver-grey bob and small hoop earrings, wearing a dark tailored blazer over a white top, a small relaxed smile, shoulders turned slightly off camera. A bright modern office with glass partitions and plants blurred softly behind her, face in the upper two thirds of a vertical frame. The look of an 85 mm lens at f/2.8: one large soft key light from camera left with a gentle fill and a subtle rim on the hair, clean catchlights, crisp focus on the eyes. Clean neutral daylight with no colour cast. Natural skin texture with visible pores and fine lines, a few flyaway hairs, no retouched plastic look, not over-processed.
```

</details>

<details>
<summary><b>Edit: "remove the guy in the background" → removal with locks (5 → 100)</b></summary>

**Before** (`examples/07-edit-remove-stranger/before.txt`, score 5/100)

```text
Remove the guy in the background
```

**After** (`examples/07-edit-remove-stranger/after.txt`, score 100/100)

```text
Remove the stranger walking in the background behind her shoulder and fill the space with matching sand, sea and sky so nothing looks patched. Keep the woman, her pose, the lighting and everything else exactly as they are. Output the full original frame at exactly the same zoom and position; do not crop, zoom in or recompose. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.
```

</details>

<details>
<summary><b>What briefs like these produce</b></summary>

Illustrations UniqAI generated for its own site with briefs written this way (no stock photos, no real people; model and prompt kept as provenance). Left: a generate brief with the texture and negative sentences. Middle and right: an edit pair, the hair changed with the identity and framing locks, everything else kept.

| Generate brief | Edit: before | Edit: after |
|:---:|:---:|:---:|
| <img src="https://uniqai.app/examples/gen/nano-banana-outfit.webp" alt="Waist-up portrait of a man in a green wool overcoat on a wet European side street, natural skin texture (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-before.webp" alt="Beauty-editorial portrait of a woman with long straight brown hair on an off-white backdrop (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-after.webp" alt="The same portrait with a chin-length bob; face, light and backdrop unchanged (AI-generated illustration)" width="260"> |
| `...50 mm lens at f/2, soft natural light, gentle filmic colour grade with creamy highlights and slightly lifted blacks, natural skin texture with visible pores, no retouched plastic look.` | `...85 mm lens at f/4, large soft window light from camera left with a gentle fill, warm off-white seamless backdrop, natural skin texture...` | `Change her hairstyle to a chin-length curtain bob... Keep her face, skin, expression, clothes, the background and the light exactly as they are... no smudges, repeated textures, halos or visible seams.` |

</details>

## Install

Works with every agent that reads instruction files. Pick yours. Requirements: Python 3.9+ for the linter. No packages to install.

<details open>
<summary><b>Claude Code</b></summary>

```bash
# user-level (available in every project)
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
# or project-level
git clone https://github.com/uniqaiapp/no-plastic .claude/skills/no-plastic
```

Then `/no-plastic` in any session, or just describe the task; the skill's `description` triggers it. Skills-directory CLIs that take an `owner/repo` work too: `npx skills add uniqaiapp/no-plastic`. As a plugin, once the uniqaiapp marketplace is published: `/plugin marketplace add uniqaiapp/skills` then `/plugin install no-plastic@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

Copy `SKILL.md`, `scripts/`, `references/` and [`.cursor/rules/no-plastic.mdc`](.cursor/rules/no-plastic.mdc) into your project. The rule file embeds the skill with `@SKILL.md`.

</details>

<details>
<summary><b>Codex / any AGENTS.md agent</b></summary>

Copy `SKILL.md`, `scripts/` and `references/` into `.agents/skills/no-plastic/` and add the snippet from [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) to your `AGENTS.md`. The repo's own [`AGENTS.md`](AGENTS.md) is the generic version.

</details>

<details>
<summary><b>Plain prompt, or no agent at all</b></summary>

Paste [`SKILL.md`](SKILL.md) into the system prompt of any model; it has no agent-specific syntax outside the frontmatter. The checklist in [`references/checklist.md`](references/checklist.md) works on paper, and the linter runs standalone:

```bash
python3 scripts/lint_prompt.py --help
echo "portrait of a woman, 8k, flawless skin" | python3 scripts/lint_prompt.py -
python3 scripts/lint_prompt.py --strict --min-score 70 prompts/*.txt   # exit 1 if any prompt is below 70
```

</details>

## FAQ

<details>
<summary><b>Why do my AI portraits look plastic even with "realistic" in the prompt?</b></summary>

Because "realistic", "photorealistic" and "8k" are labels from the training data's render and CGI corner, not from photo captions. They pull toward the look they were attached to. Photographs are captioned with lenses, light and film, so that is the vocabulary that lands you on the photographic side: `85 mm at f/2.8`, `window light from camera left`, `fine film grain`, `natural skin texture with visible pores`.

</details>

<details>
<summary><b>Does a negative prompt like "smooth skin, airbrushed" help?</b></summary>

On SDXL and Midjourney (`--no`), yes, if it is short and names a look you have actually seen. On Flux and Nano Banana there is no negative field; a trailing list is ignored. Put the same idea in the last sentence as prose: `natural skin texture, no retouched plastic look, not over-processed`. The inherited SD1.5 list (`bad anatomy, extra fingers, worst quality...`) does nothing on current models and the linter flags it.

</details>

<details>
<summary><b>Can the linter tell me if the image will look real?</b></summary>

No. It reads the prompt, not the pixels. A 100 means the brief covers the eight fields and contains none of the known trouble words. Whether the render is good depends on the model, the seed and the settings, which is why the skill's last step is a one-image pilot reviewed with the five-second check.

</details>

<details>
<summary><b>How do I keep the same person when editing a photo?</b></summary>

List what must survive by name and say "exactly as they are": `Keep the face, features, skin tone, hair edges, expression and identity exactly as they are`, then lock the frame: `Do not change the framing, crop, camera angle, or anything not mentioned`. The three things that drift are the distance between the eyes, the hairline and the background exposure; if one moved, name it in the lock and run again. Templates per edit type are in [references/edit-prompts.md](references/edit-prompts.md).

</details>

<details>
<summary><b>What about making someone look younger or thinner?</b></summary>

That is retouching, and these rules point the other way. The skill declines "better looking" requests on real people and offers the honest version instead: better light, a longer lens, a cleaner background. Do not use it to edit photos of people without their consent.

</details>

## Limits and honesty

- Regex-based and English-only. Synonyms the linter does not know count as missing; add them and send a PR.
- Model notes are observations from our own illustration runs, not benchmarks. No image counts, no "X % more realistic". Versions change; pilot again.
- The only numbers in this README are lint scores, reproducible with `python3 scripts/lint_prompt.py examples/*/before.txt examples/*/after.txt`.
- If you want the editorial-retouched look on purpose, the skill tells you which rules it is dropping instead of quietly applying the checklist.

## Related

- [video-director](https://github.com/uniqaiapp/video-director): turn a one-line idea into a shot-by-shot prompt for AI video models (Kling, Veo, Sora and others), with camera, lighting and motion vocabulary. Same photographic vocabulary, moving pictures.
- [awesome-ai-video-prompts](https://github.com/uniqaiapp/awesome-ai-video-prompts): curated, categorised prompts for AI video models with the settings that produced them.
- [skill-shrinker](https://github.com/uniqaiapp/skill-shrinker): shrink any SKILL.md or agent instruction file; this repo's references/ layout follows its advice.

Need an enhancer that keeps pores? The same rules drive the [UniqAI photo enhancer](https://uniqai.app/tools/upscaler-enhancer?utm_source=github&utm_medium=readme&utm_campaign=no-plastic).

## Contributing

Issues and pull requests are welcome. Keep changes small and include a before/after prompt pair in the PR description. See [CONTRIBUTING.md](CONTRIBUTING.md) for the local checks (`python3 tests/run.py`, no dependencies).

## License

[MIT](LICENSE) © UniqAI

---

<div align="center">

<sub>Made by <a href="https://uniqai.app/?utm_source=github&utm_medium=readme&utm_campaign=no-plastic">UniqAI</a> — Kling 3.0, Veo 3, Flux, Nano Banana and GPT-5/Claude/Gemini/Grok in one app. We wrote these rules to produce our own site illustrations, then kept using them.</sub>

</div>
