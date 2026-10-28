<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="no-plastic by UniqAI" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#instalación)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#instalación)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#instalación)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-es&utm_campaign=no-plastic)

**Corrige la piel de plástico y los retratos IA que parecen falsos: reglas de prompt, bloqueos de edición y un linter.**

[Inicio rápido](#inicio-rápido) · [Cómo funciona](#cómo-funciona) · [Ejemplos](#ejemplos) · [Instalación](#instalación) · [FAQ](#faq)

</div>

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · Español · [Português (BR)](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# no-plastic: corrige la piel de plástico y los retratos IA que parecen falsos

Los retratos generados con IA parecen falsos por una lista corta de motivos: piel sin poros, una cara simétrica como un espejo, luz que no viene de ningún sitio, bokeh pintado encima, etalonaje teal-and-orange, nada de grano. Cada uno es el valor por defecto del modelo, y cada uno tiene una frase que lo anula. no-plastic es un skill de Claude Code (con adaptadores para Cursor y Codex) que reescribe tu prompt de imagen como un brief fotográfico con esas frases dentro, escribe prompts de edición que cambian una sola cosa y conservan a la persona, e incluye un linter sin dependencias que puntúa cualquier prompt contra la lista de comprobación. Escrito para Flux, Nano Banana, Midjourney y SDXL; el vocabulario es el de la fotografía, así que también sirve para el modelo que venga después.

| **Brief, no etiquetas** | **Ediciones que conservan la cara** | **Lint antes de renderizar** |
|:---|:---|:---|
| Sujeto, encuadre, cámara, luz, paleta, textura, época, negativos: ocho campos, de tres a cinco frases, con las reglas antiplástico integradas. | Un cambio más cuatro bloqueos (identidad, realismo, encuadre, costuras), con plantillas para eliminar, fondo, ropa, pelo, mejorar y de selfie a headshot. | `scripts/lint_prompt.py` puntúa la cobertura, señala las palabras que provocan el aspecto plástico e imprime un esqueleto de brief para los huecos. Solo biblioteca estándar de Python 3. |

## Inicio rápido

```bash
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
cd ~/.claude/skills/no-plastic
python3 scripts/lint_prompt.py examples/01-linkedin-headshot/before.txt examples/01-linkedin-headshot/after.txt
```

Deberías ver que el primer prompt ("professional headshot of a beautiful woman, perfect skin, 8k...") obtiene 0/100, con la lista de palabras que lo hunden, y que el brief reescrito obtiene 100/100. Después, en Claude Code escribe `/no-plastic` y pega un prompt, o simplemente di "this looks plastic" con el prompt adjunto.

## Demo

<img alt="no-plastic demo: linting a plastic prompt and its rewrite" src="assets/demo.svg" width="820">

## Cómo funciona

1. **Clasificar.** Un prompt de *generación* (texto a imagen) o un prompt de *edición* (una instrucción sobre una foto existente: eliminar, cambiar la ropa, mejorar, de selfie a headshot). El linter lo detecta automáticamente por el verbo inicial.
2. **Lint.** `python3 scripts/lint_prompt.py --brief prompt.txt` imprime el brief de ocho campos con las frases que ha encontrado y `?` donde el prompt no dice nada; el informe normal lista las palabras señaladas (`8k`, `masterpiece`, `flawless skin`, `cinematic lighting`, la sopa de etiquetas, el ritual de negativos de SD1.5) y lo que cuesta cada una.
3. **Criticar y reescribir.** El skill nombra los tres huecos más grandes en términos fotográficos y reescribe el prompt como un brief: sujeto y acción; encuadre; cámara y luz; paleta, textura y época; negativos. Las reglas antiplástico van siempre dentro: `natural skin texture with visible pores`, `slight asymmetry`, una fuente de luz con nombre y con caída, `fine film grain`, `not over-processed, no retouched plastic look`.
4. **Adaptar a cada modelo.** Flux y Nano Banana reciben prosa con las cosas a evitar formuladas en positivo (ignoran las listas negativas); Midjourney recibe `--style raw`, un `--stylize` más bajo y un `--no` corto; SDXL recibe el brief con sujeto, luz y textura en los primeros 77 tokens y un campo negativo corto. Consulta [references/model-notes.md](references/model-notes.md).
5. **Piloto y después lote.** Renderiza una imagen, haz la revisión de cinco segundos (textura de la frente al 100 %, sombra de la nariz, reflejos en los ojos, línea del pelo, caída del fondo), corrige el brief en lugar de volver a tirar los dados y después renderiza la serie. Este es el flujo que UniqAI usó para producir las ilustraciones de su propio sitio; [references/pilot-review.md](references/pilot-review.md) tiene el formato de la lista de trabajos y la regla de decisión.

```
loose request ──▶ lint (gaps + flags) ──▶ brief / edit with locks ──▶ per-model variant ──▶ re-lint ≥ 85 ──▶ pilot ──▶ review ──▶ batch
```

Las puntuaciones de este README las produce `python3 scripts/lint_prompt.py` sobre los archivos de `examples/`; `tests/test_examples.py` falla si se desvían. El linter lee palabras, no píxeles: un 100 es un brief completo, no una imagen garantizada. Para eso está el piloto.

## Ejemplos

Nueve pares con sus informes en [examples/](examples/README.md). Dos de ellos completos:

<details open>
<summary><b>Headshot: de "8k masterpiece" a un brief de 85 mm (0 → 100)</b></summary>

**Antes** (`examples/01-linkedin-headshot/before.txt`, puntuación 0/100)

```text
Professional headshot of a beautiful woman, perfect skin, studio lighting, 8k, ultra realistic, masterpiece, sharp focus
```

**Después** (`examples/01-linkedin-headshot/after.txt`, puntuación 100/100)

```text
Head-and-shoulders business headshot of a woman in her early fifties with pale skin, a silver-grey bob and small hoop earrings, wearing a dark tailored blazer over a white top, a small relaxed smile, shoulders turned slightly off camera. A bright modern office with glass partitions and plants blurred softly behind her, face in the upper two thirds of a vertical frame. The look of an 85 mm lens at f/2.8: one large soft key light from camera left with a gentle fill and a subtle rim on the hair, clean catchlights, crisp focus on the eyes. Clean neutral daylight with no colour cast. Natural skin texture with visible pores and fine lines, a few flyaway hairs, no retouched plastic look, not over-processed.
```

</details>

<details>
<summary><b>Edición: de "remove the guy in the background" a una eliminación con bloqueos (5 → 100)</b></summary>

**Antes** (`examples/07-edit-remove-stranger/before.txt`, puntuación 5/100)

```text
Remove the guy in the background
```

**Después** (`examples/07-edit-remove-stranger/after.txt`, puntuación 100/100)

```text
Remove the stranger walking in the background behind her shoulder and fill the space with matching sand, sea and sky so nothing looks patched. Keep the woman, her pose, the lighting and everything else exactly as they are. Output the full original frame at exactly the same zoom and position; do not crop, zoom in or recompose. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.
```

</details>

<details>
<summary><b>Lo que producen briefs como estos</b></summary>

Ilustraciones que UniqAI generó para su propio sitio con briefs escritos así (sin fotos de stock, sin personas reales; el modelo y el prompt se conservan como procedencia). Izquierda: un brief de generación con las frases de textura y de negativos. Centro y derecha: un par de edición, el pelo cambiado con los bloqueos de identidad y encuadre, todo lo demás conservado.

| Brief de generación | Edición: antes | Edición: después |
|:---:|:---:|:---:|
| <img src="https://uniqai.app/examples/gen/nano-banana-outfit.webp" alt="Waist-up portrait of a man in a green wool overcoat on a wet European side street, natural skin texture (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-before.webp" alt="Beauty-editorial portrait of a woman with long straight brown hair on an off-white backdrop (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-after.webp" alt="The same portrait with a chin-length bob; face, light and backdrop unchanged (AI-generated illustration)" width="260"> |
| `...50 mm lens at f/2, soft natural light, gentle filmic colour grade with creamy highlights and slightly lifted blacks, natural skin texture with visible pores, no retouched plastic look.` | `...85 mm lens at f/4, large soft window light from camera left with a gentle fill, warm off-white seamless backdrop, natural skin texture...` | `Change her hairstyle to a chin-length curtain bob... Keep her face, skin, expression, clothes, the background and the light exactly as they are... no smudges, repeated textures, halos or visible seams.` |

</details>

## Instalación

Funciona con cualquier agente que lea archivos de instrucciones. Elige el tuyo. Requisitos: Python 3.9+ para el linter. Sin paquetes que instalar.

<details open>
<summary><b>Claude Code</b></summary>

```bash
# user-level (available in every project)
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
# or project-level
git clone https://github.com/uniqaiapp/no-plastic .claude/skills/no-plastic
```

Después escribe `/no-plastic` en cualquier sesión, o simplemente describe la tarea; la `description` del skill lo activa. Las CLIs de directorios de skills que aceptan `owner/repo` también funcionan: `npx skills add uniqaiapp/no-plastic`. Como plugin, cuando se publique el marketplace de uniqaiapp: `/plugin marketplace add uniqaiapp/skills` y después `/plugin install no-plastic@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

Copia `SKILL.md`, `scripts/`, `references/` y [`.cursor/rules/no-plastic.mdc`](.cursor/rules/no-plastic.mdc) a tu proyecto. El archivo de regla incrusta el skill con `@SKILL.md`.

</details>

<details>
<summary><b>Codex / cualquier agente con AGENTS.md</b></summary>

Copia `SKILL.md`, `scripts/` y `references/` a `.agents/skills/no-plastic/` y añade el fragmento de [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) a tu `AGENTS.md`. El [`AGENTS.md`](AGENTS.md) del propio repositorio es la versión genérica.

</details>

<details>
<summary><b>Prompt plano, o sin agente</b></summary>

Pega [`SKILL.md`](SKILL.md) en el system prompt de cualquier modelo; no tiene sintaxis específica de ningún agente fuera del frontmatter. La lista de comprobación de [`references/checklist.md`](references/checklist.md) funciona en papel, y el linter se ejecuta por sí solo:

```bash
python3 scripts/lint_prompt.py --help
echo "portrait of a woman, 8k, flawless skin" | python3 scripts/lint_prompt.py -
python3 scripts/lint_prompt.py --strict --min-score 70 prompts/*.txt   # exit 1 if any prompt is below 70
```

</details>

## FAQ

<details>
<summary><b>¿Por qué mis retratos con IA parecen de plástico aunque ponga "realistic" en el prompt?</b></summary>

Porque "realistic", "photorealistic" y "8k" son etiquetas que vienen del rincón de renders y CGI de los datos de entrenamiento, no de pies de foto. Tiran hacia el aspecto al que estaban pegadas. Las fotografías se describen con objetivos, luz y película, así que ese es el vocabulario que te deja en el lado fotográfico: `85 mm at f/2.8`, `window light from camera left`, `fine film grain`, `natural skin texture with visible pores`.

</details>

<details>
<summary><b>¿Ayuda un prompt negativo como "smooth skin, airbrushed"?</b></summary>

En SDXL y Midjourney (`--no`), sí, si es corto y nombra un aspecto que hayas visto de verdad. En Flux y Nano Banana no hay campo negativo; una lista al final se ignora. Pon la misma idea en la última frase como prosa: `natural skin texture, no retouched plastic look, not over-processed`. La lista heredada de SD1.5 (`bad anatomy, extra fingers, worst quality...`) no hace nada en los modelos actuales y el linter la señala.

</details>

<details>
<summary><b>¿Puede el linter decirme si la imagen va a parecer real?</b></summary>

No. Lee el prompt, no los píxeles. Un 100 significa que el brief cubre los ocho campos y no contiene ninguna de las palabras problemáticas conocidas. Que el render sea bueno depende del modelo, la semilla y los ajustes, y por eso el último paso del skill es un piloto de una sola imagen revisado con la comprobación de cinco segundos.

</details>

<details>
<summary><b>¿Cómo mantengo a la misma persona al editar una foto?</b></summary>

Enumera por su nombre lo que debe sobrevivir y di "exactly as they are": `Keep the face, features, skin tone, hair edges, expression and identity exactly as they are`, y después bloquea el encuadre: `Do not change the framing, crop, camera angle, or anything not mentioned`. Las tres cosas que se mueven son la distancia entre los ojos, la línea del pelo y la exposición del fondo; si alguna se ha movido, nómbrala en el bloqueo y vuelve a ejecutar. Las plantillas por tipo de edición están en [references/edit-prompts.md](references/edit-prompts.md).

</details>

<details>
<summary><b>¿Y para que alguien parezca más joven o más delgado?</b></summary>

Eso es retoque, y estas reglas apuntan en la dirección contraria. El skill rechaza las peticiones de "que salga más guapo" sobre personas reales y ofrece la versión honesta en su lugar: mejor luz, un objetivo más largo, un fondo más limpio. No lo uses para editar fotos de personas sin su consentimiento.

</details>

## Límites y honestidad

- Basado en expresiones regulares y solo en inglés. Los sinónimos que el linter no conoce cuentan como ausentes; añádelos y envía un PR.
- Las notas por modelo son observaciones de nuestras propias tandas de ilustraciones, no benchmarks. Sin recuentos de imágenes, sin "X % más realista". Las versiones cambian; vuelve a hacer el piloto.
- Los únicos números de este README son puntuaciones del lint, reproducibles con `python3 scripts/lint_prompt.py examples/*/before.txt examples/*/after.txt`.
- Si quieres el aspecto retocado editorial a propósito, el skill te dice qué reglas está dejando de lado en lugar de aplicar la lista de comprobación en silencio.

## Relacionados

- [video-director](https://github.com/uniqaiapp/video-director): convierte una idea de una línea en un prompt plano a plano para modelos de video con IA (Kling, Veo, Sora y otros), con vocabulario de cámara, iluminación y movimiento. El mismo vocabulario fotográfico, en imágenes en movimiento.
- [awesome-ai-video-prompts](https://github.com/uniqaiapp/awesome-ai-video-prompts): prompts seleccionados y clasificados para modelos de video con IA, con los ajustes que los produjeron.
- [skill-shrinker](https://github.com/uniqaiapp/skill-shrinker): reduce cualquier SKILL.md o archivo de instrucciones para agentes; la estructura de references/ de este repositorio sigue sus consejos.

¿Necesitas un mejorador que conserve los poros? Las mismas reglas mueven el [mejorador de fotos de UniqAI](https://uniqai.app/tools/upscaler-enhancer?utm_source=github&utm_medium=readme-es&utm_campaign=no-plastic).

## Contribuir

Los issues y pull requests son bienvenidos. Haz cambios pequeños e incluye un par de prompts de antes y después en la descripción del PR. Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para las comprobaciones locales (`python3 tests/run.py`, sin dependencias).

## Licencia

[MIT](LICENSE) © UniqAI

---

<div align="center">

<sub>Hecho por <a href="https://uniqai.app/?utm_source=github&utm_medium=readme-es&utm_campaign=no-plastic">UniqAI</a> — Kling 3.0, Veo 3, Flux, Nano Banana y GPT-5/Claude/Gemini/Grok en una sola app. Escribimos estas reglas para producir las ilustraciones de nuestro propio sitio y después seguimos usándolas.</sub>

</div>
