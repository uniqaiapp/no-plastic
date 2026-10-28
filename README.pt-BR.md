<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="no-plastic by UniqAI" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#instalação)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#instalação)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#instalação)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-pt-br&utm_campaign=no-plastic)

**Corrija a pele de plástico e os retratos de IA com cara de falso: regras de prompt, travas de edição e um linter.**

[Início rápido](#início-rápido) · [Como funciona](#como-funciona) · [Exemplos](#exemplos) · [Instalação](#instalação) · [FAQ](#faq)

</div>

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · Português (BR) · [日本語](README.ja.md) · [한국어](README.ko.md)

# no-plastic: corrija a pele de plástico e os retratos de IA com cara de falso

Retratos de IA parecem falsos por uma lista curta de motivos: pele sem poros, rosto simétrico como um espelho, luz vinda do nada, bokeh pintado por cima, gradação teal-and-orange, nenhum grão. Cada um é o padrão do modelo, e cada um tem uma frase que o sobrescreve. no-plastic é uma skill do Claude Code (com adaptadores para Cursor e Codex) que reescreve o seu prompt de imagem como um briefing fotográfico com essas frases dentro, escreve prompts de edição que mudam uma coisa só e preservam a pessoa, e traz um linter sem dependências que pontua qualquer prompt contra o checklist. Escrito para Flux, Nano Banana, Midjourney e SDXL; o vocabulário é o da fotografia, então ele vale também para o próximo modelo.

| **Briefing, não tags** | **Edições que preservam o rosto** | **Lint antes de renderizar** |
|:---|:---|:---|
| Sujeito, enquadramento, câmera, luz, paleta, textura, época, negativos: oito campos, três a cinco frases, com as regras antiplástico já embutidas. | Uma mudança mais quatro travas (identidade, realismo, enquadramento, emendas), com modelos para remover, fundo, roupa, cabelo, melhorar e selfie para headshot. | `scripts/lint_prompt.py` pontua a cobertura, marca as palavras que causam o aspecto plástico e imprime um esqueleto de briefing para as lacunas. Só a biblioteca padrão do Python 3. |

## Início rápido

```bash
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
cd ~/.claude/skills/no-plastic
python3 scripts/lint_prompt.py examples/01-linkedin-headshot/before.txt examples/01-linkedin-headshot/after.txt
```

Você deve ver o primeiro prompt ("professional headshot of a beautiful woman, perfect skin, 8k...") pontuar 0/100 com a lista das palavras que o afundam, e o briefing reescrito pontuar 100/100. Depois, no Claude Code, digite `/no-plastic` e cole um prompt, ou apenas diga "isso parece plástico" com o prompt anexado.

## Demo

<img alt="no-plastic demo: linting a plastic prompt and its rewrite" src="assets/demo.svg" width="820">

## Como funciona

1. **Classificar.** Um prompt de *geração* (texto para imagem) ou um prompt de *edição* (uma instrução sobre uma foto existente: remover, trocar a roupa, melhorar, selfie para headshot). O linter detecta automaticamente pelo verbo inicial.
2. **Lint.** `python3 scripts/lint_prompt.py --brief prompt.txt` imprime o briefing de oito campos com as frases que encontrou e `?` onde o prompt não diz nada; o relatório simples lista as palavras marcadas (`8k`, `masterpiece`, `flawless skin`, `cinematic lighting`, sopa de tags, o ritual de negativos do SD1.5) e o que cada uma custa.
3. **Criticar e reescrever.** A skill nomeia as três maiores lacunas em termos fotográficos e reescreve o prompt como um briefing: sujeito e ação; enquadramento; câmera e luz; paleta, textura e época; negativos. As regras antiplástico entram sempre: `natural skin texture with visible pores`, `slight asymmetry`, uma fonte de luz nomeada com decaimento, `fine film grain`, `not over-processed, no retouched plastic look`.
4. **Adaptar por modelo.** Flux e Nano Banana recebem prosa com o que evitar formulado de forma positiva (eles ignoram listas negativas); o Midjourney recebe `--style raw`, um `--stylize` mais baixo e um `--no` curto; o SDXL recebe o briefing com sujeito, luz e textura nos primeiros 77 tokens e um campo negativo curto. Veja [references/model-notes.md](references/model-notes.md).
5. **Piloto, depois lote.** Renderize uma imagem, faça a revisão de cinco segundos (textura da testa a 100 %, sombra do nariz, reflexos nos olhos, linha do cabelo, decaimento do fundo), corrija o briefing em vez de rolar de novo, então renderize o conjunto. Foi esse o fluxo que a UniqAI usou para produzir as ilustrações do próprio site; [references/pilot-review.md](references/pilot-review.md) tem o formato da lista de jobs e a regra de decisão.

```
loose request ──▶ lint (gaps + flags) ──▶ brief / edit with locks ──▶ per-model variant ──▶ re-lint ≥ 85 ──▶ pilot ──▶ review ──▶ batch
```

As pontuações deste README são produzidas por `python3 scripts/lint_prompt.py` sobre os arquivos em `examples/`; `tests/test_examples.py` falha se elas mudarem. O linter lê palavras, não pixels: um 100 é um briefing completo, não uma imagem garantida. É para isso que serve o piloto.

## Exemplos

Nove pares com relatórios em [examples/](examples/README.md). Dois deles na íntegra:

<details open>
<summary><b>Headshot: "8k masterpiece" → briefing de 85 mm (0 → 100)</b></summary>

**Antes** (`examples/01-linkedin-headshot/before.txt`, pontuação 0/100)

```text
Professional headshot of a beautiful woman, perfect skin, studio lighting, 8k, ultra realistic, masterpiece, sharp focus
```

**Depois** (`examples/01-linkedin-headshot/after.txt`, pontuação 100/100)

```text
Head-and-shoulders business headshot of a woman in her early fifties with pale skin, a silver-grey bob and small hoop earrings, wearing a dark tailored blazer over a white top, a small relaxed smile, shoulders turned slightly off camera. A bright modern office with glass partitions and plants blurred softly behind her, face in the upper two thirds of a vertical frame. The look of an 85 mm lens at f/2.8: one large soft key light from camera left with a gentle fill and a subtle rim on the hair, clean catchlights, crisp focus on the eyes. Clean neutral daylight with no colour cast. Natural skin texture with visible pores and fine lines, a few flyaway hairs, no retouched plastic look, not over-processed.
```

</details>

<details>
<summary><b>Edição: "remove the guy in the background" → remoção com travas (5 → 100)</b></summary>

**Antes** (`examples/07-edit-remove-stranger/before.txt`, pontuação 5/100)

```text
Remove the guy in the background
```

**Depois** (`examples/07-edit-remove-stranger/after.txt`, pontuação 100/100)

```text
Remove the stranger walking in the background behind her shoulder and fill the space with matching sand, sea and sky so nothing looks patched. Keep the woman, her pose, the lighting and everything else exactly as they are. Output the full original frame at exactly the same zoom and position; do not crop, zoom in or recompose. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.
```

</details>

<details>
<summary><b>O que briefings assim produzem</b></summary>

Ilustrações que a UniqAI gerou para o próprio site com briefings escritos desta forma (sem fotos de banco de imagens, sem pessoas reais; modelo e prompt guardados como procedência). À esquerda: um briefing de geração com as frases de textura e de negativos. No meio e à direita: um par de edição, com o cabelo trocado sob as travas de identidade e enquadramento, e todo o resto preservado.

| Briefing de geração | Edição: antes | Edição: depois |
|:---:|:---:|:---:|
| <img src="https://uniqai.app/examples/gen/nano-banana-outfit.webp" alt="Waist-up portrait of a man in a green wool overcoat on a wet European side street, natural skin texture (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-before.webp" alt="Beauty-editorial portrait of a woman with long straight brown hair on an off-white backdrop (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-after.webp" alt="The same portrait with a chin-length bob; face, light and backdrop unchanged (AI-generated illustration)" width="260"> |
| `...50 mm lens at f/2, soft natural light, gentle filmic colour grade with creamy highlights and slightly lifted blacks, natural skin texture with visible pores, no retouched plastic look.` | `...85 mm lens at f/4, large soft window light from camera left with a gentle fill, warm off-white seamless backdrop, natural skin texture...` | `Change her hairstyle to a chin-length curtain bob... Keep her face, skin, expression, clothes, the background and the light exactly as they are... no smudges, repeated textures, halos or visible seams.` |

</details>

## Instalação

Funciona com qualquer agente que leia arquivos de instrução. Escolha o seu. Requisitos: Python 3.9+ para o linter. Nenhum pacote para instalar.

<details open>
<summary><b>Claude Code</b></summary>

```bash
# user-level (available in every project)
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
# or project-level
git clone https://github.com/uniqaiapp/no-plastic .claude/skills/no-plastic
```

Depois, `/no-plastic` em qualquer sessão, ou apenas descreva a tarefa; a `description` da skill a aciona. CLIs de diretórios de skills que aceitam `owner/repo` também funcionam: `npx skills add uniqaiapp/no-plastic`. Como plugin, quando o marketplace uniqaiapp for publicado: `/plugin marketplace add uniqaiapp/skills` e então `/plugin install no-plastic@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

Copie `SKILL.md`, `scripts/`, `references/` e [`.cursor/rules/no-plastic.mdc`](.cursor/rules/no-plastic.mdc) para o seu projeto. O arquivo de regra incorpora a skill com `@SKILL.md`.

</details>

<details>
<summary><b>Codex / qualquer agente que leia AGENTS.md</b></summary>

Copie `SKILL.md`, `scripts/` e `references/` para `.agents/skills/no-plastic/` e adicione o snippet de [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) ao seu `AGENTS.md`. O [`AGENTS.md`](AGENTS.md) deste repositório é a versão genérica.

</details>

<details>
<summary><b>Prompt puro, ou sem agente nenhum</b></summary>

Cole [`SKILL.md`](SKILL.md) no system prompt de qualquer modelo; ele não tem sintaxe específica de agente fora do frontmatter. O checklist em [`references/checklist.md`](references/checklist.md) funciona no papel, e o linter roda sozinho:

```bash
python3 scripts/lint_prompt.py --help
echo "portrait of a woman, 8k, flawless skin" | python3 scripts/lint_prompt.py -
python3 scripts/lint_prompt.py --strict --min-score 70 prompts/*.txt   # exit 1 if any prompt is below 70
```

</details>

## FAQ

<details>
<summary><b>Por que meus retratos de IA ficam com cara de plástico mesmo com "realistic" no prompt?</b></summary>

Porque "realistic", "photorealistic" e "8k" são rótulos vindos do canto de renders e CGI dos dados de treino, não de legendas de fotos. Eles puxam para o visual ao qual estavam colados. Fotografias são legendadas com lentes, luz e filme, então esse é o vocabulário que te coloca do lado fotográfico: `85 mm at f/2.8`, `window light from camera left`, `fine film grain`, `natural skin texture with visible pores`.

</details>

<details>
<summary><b>Um prompt negativo como "smooth skin, airbrushed" ajuda?</b></summary>

No SDXL e no Midjourney (`--no`), sim, se for curto e nomear um visual que você realmente viu. No Flux e no Nano Banana não existe campo negativo; uma lista no final é ignorada. Coloque a mesma ideia na última frase, em prosa: `natural skin texture, no retouched plastic look, not over-processed`. A lista herdada do SD1.5 (`bad anatomy, extra fingers, worst quality...`) não faz nada nos modelos atuais, e o linter a marca.

</details>

<details>
<summary><b>O linter consegue dizer se a imagem vai parecer real?</b></summary>

Não. Ele lê o prompt, não os pixels. Um 100 significa que o briefing cobre os oito campos e não contém nenhuma das palavras problemáticas conhecidas. Se o render fica bom depende do modelo, da seed e das configurações, e é por isso que o último passo da skill é um piloto de uma imagem revisado com o check de cinco segundos.

</details>

<details>
<summary><b>Como mantenho a mesma pessoa ao editar uma foto?</b></summary>

Liste pelo nome o que precisa sobreviver e diga "exactly as they are": `Keep the face, features, skin tone, hair edges, expression and identity exactly as they are`, depois trave o enquadramento: `Do not change the framing, crop, camera angle, or anything not mentioned`. As três coisas que costumam escapar são a distância entre os olhos, a linha do cabelo e a exposição do fundo; se uma delas se moveu, nomeie-a na trava e rode de novo. Os modelos por tipo de edição estão em [references/edit-prompts.md](references/edit-prompts.md).

</details>

<details>
<summary><b>E para deixar alguém mais jovem ou mais magro?</b></summary>

Isso é retoque, e estas regras apontam na direção contrária. A skill recusa pedidos de "ficar mais bonito" em pessoas reais e oferece a versão honesta no lugar: luz melhor, lente mais longa, fundo mais limpo. Não a use para editar fotos de pessoas sem o consentimento delas.

</details>

## Limites e honestidade

- Baseado em regex e só em inglês. Sinônimos que o linter não conhece contam como ausentes; adicione-os e mande um PR.
- As notas por modelo são observações das nossas próprias rodadas de ilustração, não benchmarks. Sem contagem de imagens, sem "X % mais realista". As versões mudam; faça o piloto de novo.
- Os únicos números deste README são pontuações do lint, reproduzíveis com `python3 scripts/lint_prompt.py examples/*/before.txt examples/*/after.txt`.
- Se você quer o visual editorial retocado de propósito, a skill diz quais regras está deixando de lado em vez de aplicar o checklist em silêncio.

## Projetos relacionados

- [video-director](https://github.com/uniqaiapp/video-director): transforma uma ideia de uma linha em um prompt plano a plano para modelos de vídeo por IA (Kling, Veo, Sora e outros), com vocabulário de câmera, luz e movimento. O mesmo vocabulário fotográfico, em imagens em movimento.
- [awesome-ai-video-prompts](https://github.com/uniqaiapp/awesome-ai-video-prompts): prompts selecionados e categorizados para modelos de vídeo por IA, com as configurações que os produziram.
- [skill-shrinker](https://github.com/uniqaiapp/skill-shrinker): enxuga qualquer SKILL.md ou arquivo de instruções de agente; o layout de references/ deste repositório segue o conselho dele.

Precisa de um enhancer que preserve os poros? As mesmas regras movem o [enhancer de fotos da UniqAI](https://uniqai.app/tools/upscaler-enhancer?utm_source=github&utm_medium=readme-pt-br&utm_campaign=no-plastic).

## Como contribuir

Issues e pull requests são bem-vindos. Mantenha as mudanças pequenas e inclua um par de prompts antes/depois na descrição do PR. Veja [CONTRIBUTING.md](CONTRIBUTING.md) para as verificações locais (`python3 tests/run.py`, sem dependências).

## Licença

[MIT](LICENSE) © UniqAI

---

<div align="center">

<sub>Feito por <a href="https://uniqai.app/?utm_source=github&utm_medium=readme-pt-br&utm_campaign=no-plastic">UniqAI</a> — Kling 3.0, Veo 3, Flux, Nano Banana e GPT-5/Claude/Gemini/Grok em um só app. Escrevemos estas regras para produzir as ilustrações do nosso próprio site e depois continuamos usando.</sub>

</div>
