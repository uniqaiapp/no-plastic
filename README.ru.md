<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="no-plastic by UniqAI" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#установка)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#установка)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#установка)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-ru&utm_campaign=no-plastic)

**Убираем пластиковую кожу и неестественность в ИИ-портретах: правила для промптов, замки для правок и линтер.**

[Быстрый старт](#быстрый-старт) · [Как это работает](#как-это-работает) · [Примеры](#примеры) · [Установка](#установка) · [FAQ](#faq)

</div>

[English](README.md) · Русский · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português (BR)](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# no-plastic: убираем пластиковую кожу и неестественность в ИИ-портретах

ИИ-портреты выглядят неестественно по короткому списку причин: кожа без пор, зеркально симметричное лицо, свет ниоткуда, нарисованное боке, теал-оранжевая цветокоррекция, отсутствие зерна. Каждая из них — поведение модели по умолчанию, и для каждой есть предложение, которое его переопределяет. no-plastic — это скилл Claude Code (с адаптерами для Cursor и Codex), который переписывает ваш промпт для картинки в фотографический бриф с этими предложениями внутри, пишет промпты для правок, которые меняют одну вещь и сохраняют человека, и поставляется с линтером без зависимостей, который оценивает любой промпт по чеклисту. Написан для Flux, Nano Banana, Midjourney и SDXL; словарь здесь фотографический, поэтому он переносится и на следующую модель.

| **Бриф, а не теги** | **Правки, сохраняющие лицо** | **Линт до рендера** |
|:---|:---|:---|
| Объект, кадрирование, камера, свет, палитра, фактура, эпоха, негативы: восемь полей, три–пять предложений, правила против пластика уже внутри. | Одно изменение плюс четыре замка (личность, реализм, кадрирование, швы), с шаблонами для удаления, фона, одежды, причёски, улучшения и селфи-в-деловой-портрет. | `scripts/lint_prompt.py` оценивает покрытие, помечает слова, из-за которых получается пластик, и печатает скелет брифа для пробелов. Только stdlib Python 3. |

## Быстрый старт

```bash
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
cd ~/.claude/skills/no-plastic
python3 scripts/lint_prompt.py examples/01-linkedin-headshot/before.txt examples/01-linkedin-headshot/after.txt
```

Вы увидите, что первый промпт («professional headshot of a beautiful woman, perfect skin, 8k...») получает 0/100 со списком слов, которые его топят, а переписанный бриф — 100/100. Дальше в Claude Code введите `/no-plastic` и вставьте промпт, или просто скажите «выглядит как пластик» и приложите промпт.

## Демо

<img alt="no-plastic demo: linting a plastic prompt and its rewrite" src="assets/demo.svg" width="820">

## Как это работает

1. **Классификация.** Промпт на *генерацию* (текст в картинку) или на *правку* (инструкция к существующему фото: удалить, сменить одежду, улучшить, сделать из селфи деловой портрет). Линтер определяет тип сам по первому глаголу.
2. **Линт.** `python3 scripts/lint_prompt.py --brief prompt.txt` печатает бриф из восьми полей с найденными фразами и `?` там, где промпт молчит; обычный отчёт перечисляет помеченные слова (`8k`, `masterpiece`, `flawless skin`, `cinematic lighting`, свалка тегов, ритуальный негатив из SD1.5) и чего стоит каждое.
3. **Разбор и переписывание.** Скилл называет три главных пробела в фотографических терминах и переписывает промпт как бриф: объект и действие; кадрирование; камера и свет; палитра, фактура и эпоха; негативы. Правила против пластика есть всегда: `natural skin texture with visible pores`, `slight asymmetry`, названный источник света со спадом, `fine film grain`, `not over-processed, no retouched plastic look`.
4. **Адаптация под модель.** Flux и Nano Banana получают прозу, где нежелательное сформулировано утвердительно (списки негативов они игнорируют); Midjourney — `--style raw`, пониженный `--stylize` и короткий `--no`; SDXL — бриф с объектом, светом и фактурой в первых 77 токенах и короткое негативное поле. См. [references/model-notes.md](references/model-notes.md).
5. **Пилот, затем серия.** Отрендерите одну картинку, проведите пятисекундную проверку (фактура лба на 100 %, тень от носа, блики в глазах, линия волос, спад фона), поправьте бриф вместо перебора сидов и только потом рендерите серию. Именно так UniqAI делал иллюстрации для своего сайта; формат списка задач и правило принятия решения — в [references/pilot-review.md](references/pilot-review.md).

```
loose request ──▶ lint (gaps + flags) ──▶ brief / edit with locks ──▶ per-model variant ──▶ re-lint ≥ 85 ──▶ pilot ──▶ review ──▶ batch
```

Оценки в этом README получены командой `python3 scripts/lint_prompt.py` на файлах из `examples/`; `tests/test_examples.py` падает, если они расходятся. Линтер читает слова, а не пиксели: 100 означает полный бриф, а не гарантированную картинку. Для этого и нужен пилот.

## Примеры

Девять пар с отчётами в [examples/](examples/README.md). Две из них целиком:

<details open>
<summary><b>Деловой портрет: «8k masterpiece» → бриф под 85 мм (0 → 100)</b></summary>

**До** (`examples/01-linkedin-headshot/before.txt`, оценка 0/100)

```text
Professional headshot of a beautiful woman, perfect skin, studio lighting, 8k, ultra realistic, masterpiece, sharp focus
```

**После** (`examples/01-linkedin-headshot/after.txt`, оценка 100/100)

```text
Head-and-shoulders business headshot of a woman in her early fifties with pale skin, a silver-grey bob and small hoop earrings, wearing a dark tailored blazer over a white top, a small relaxed smile, shoulders turned slightly off camera. A bright modern office with glass partitions and plants blurred softly behind her, face in the upper two thirds of a vertical frame. The look of an 85 mm lens at f/2.8: one large soft key light from camera left with a gentle fill and a subtle rim on the hair, clean catchlights, crisp focus on the eyes. Clean neutral daylight with no colour cast. Natural skin texture with visible pores and fine lines, a few flyaway hairs, no retouched plastic look, not over-processed.
```

</details>

<details>
<summary><b>Правка: «убери парня на фоне» → удаление с замками (5 → 100)</b></summary>

**До** (`examples/07-edit-remove-stranger/before.txt`, оценка 5/100)

```text
Remove the guy in the background
```

**После** (`examples/07-edit-remove-stranger/after.txt`, оценка 100/100)

```text
Remove the stranger walking in the background behind her shoulder and fill the space with matching sand, sea and sky so nothing looks patched. Keep the woman, her pose, the lighting and everything else exactly as they are. Output the full original frame at exactly the same zoom and position; do not crop, zoom in or recompose. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.
```

</details>

<details>
<summary><b>Что получается из таких брифов</b></summary>

Иллюстрации, которые UniqAI сгенерировал для своего сайта по брифам, написанным таким способом (без стоковых фото и реальных людей; модель и промпт сохранены как происхождение). Слева: бриф на генерацию с предложениями про фактуру и негативы. В центре и справа: пара до/после правки, причёска изменена с замками на личность и кадрирование, всё остальное сохранено.

| Бриф на генерацию | Правка: до | Правка: после |
|:---:|:---:|:---:|
| <img src="https://uniqai.app/examples/gen/nano-banana-outfit.webp" alt="Waist-up portrait of a man in a green wool overcoat on a wet European side street, natural skin texture (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-before.webp" alt="Beauty-editorial portrait of a woman with long straight brown hair on an off-white backdrop (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-after.webp" alt="The same portrait with a chin-length bob; face, light and backdrop unchanged (AI-generated illustration)" width="260"> |
| `...50 mm lens at f/2, soft natural light, gentle filmic colour grade with creamy highlights and slightly lifted blacks, natural skin texture with visible pores, no retouched plastic look.` | `...85 mm lens at f/4, large soft window light from camera left with a gentle fill, warm off-white seamless backdrop, natural skin texture...` | `Change her hairstyle to a chin-length curtain bob... Keep her face, skin, expression, clothes, the background and the light exactly as they are... no smudges, repeated textures, halos or visible seams.` |

</details>

## Установка

Работает с любым агентом, который читает файлы инструкций. Выберите свой. Требования: Python 3.9+ для линтера. Пакеты устанавливать не нужно.

<details open>
<summary><b>Claude Code</b></summary>

```bash
# user-level (available in every project)
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
# or project-level
git clone https://github.com/uniqaiapp/no-plastic .claude/skills/no-plastic
```

Дальше `/no-plastic` в любой сессии или просто опишите задачу; скилл срабатывает по своему `description`. CLI каталогов скиллов, принимающие `owner/repo`, тоже подходят: `npx skills add uniqaiapp/no-plastic`. Как плагин, когда будет опубликован маркетплейс uniqaiapp: `/plugin marketplace add uniqaiapp/skills`, затем `/plugin install no-plastic@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

Скопируйте `SKILL.md`, `scripts/`, `references/` и [`.cursor/rules/no-plastic.mdc`](.cursor/rules/no-plastic.mdc) в проект. Файл правила встраивает скилл через `@SKILL.md`.

</details>

<details>
<summary><b>Codex / любой агент с AGENTS.md</b></summary>

Скопируйте `SKILL.md`, `scripts/` и `references/` в `.agents/skills/no-plastic/` и добавьте фрагмент из [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) в свой `AGENTS.md`. Собственный [`AGENTS.md`](AGENTS.md) репозитория — универсальная версия.

</details>

<details>
<summary><b>Обычный промпт или вообще без агента</b></summary>

Вставьте [`SKILL.md`](SKILL.md) в системный промпт любой модели; кроме фронтматтера в нём нет синтаксиса, привязанного к агенту. Чеклист в [`references/checklist.md`](references/checklist.md) работает и на бумаге, а линтер запускается сам по себе:

```bash
python3 scripts/lint_prompt.py --help
echo "portrait of a woman, 8k, flawless skin" | python3 scripts/lint_prompt.py -
python3 scripts/lint_prompt.py --strict --min-score 70 prompts/*.txt   # exit 1 if any prompt is below 70
```

</details>

## FAQ

<details>
<summary><b>Почему мои ИИ-портреты выглядят как пластик, даже если в промпте есть «realistic»?</b></summary>

Потому что «realistic», «photorealistic» и «8k» — это подписи из того угла обучающих данных, где живут рендеры и CGI, а не подписи к фотографиям. Они тянут к тому виду, к которому были привязаны. Фотографии подписывают объективами, светом и плёнкой, поэтому именно этот словарь выводит на фотографическую сторону: `85 mm at f/2.8`, `window light from camera left`, `fine film grain`, `natural skin texture with visible pores`.

</details>

<details>
<summary><b>Помогает ли негативный промпт вроде «smooth skin, airbrushed»?</b></summary>

На SDXL и Midjourney (`--no`) — да, если он короткий и называет вид, который вы действительно видели. У Flux и Nano Banana негативного поля нет; список в конце игнорируется. Выразите ту же мысль последним предложением в прозе: `natural skin texture, no retouched plastic look, not over-processed`. Унаследованный список из SD1.5 (`bad anatomy, extra fingers, worst quality...`) на современных моделях ничего не делает, и линтер его помечает.

</details>

<details>
<summary><b>Может ли линтер сказать, будет ли картинка выглядеть настоящей?</b></summary>

Нет. Он читает промпт, а не пиксели. 100 означает, что бриф покрывает восемь полей и не содержит ни одного известного проблемного слова. Хорош ли рендер, зависит от модели, сида и настроек, поэтому последний шаг скилла — пилот из одной картинки с пятисекундной проверкой.

</details>

<details>
<summary><b>Как сохранить того же человека при правке фото?</b></summary>

Перечислите по имени всё, что должно уцелеть, и скажите «exactly as they are»: `Keep the face, features, skin tone, hair edges, expression and identity exactly as they are`, затем зафиксируйте кадр: `Do not change the framing, crop, camera angle, or anything not mentioned`. Чаще всего уплывают три вещи: расстояние между глазами, линия волос и экспозиция фона; если что-то сдвинулось, назовите это в замке и запустите снова. Шаблоны по типам правок — в [references/edit-prompts.md](references/edit-prompts.md).

</details>

<details>
<summary><b>А если нужно сделать человека моложе или стройнее?</b></summary>

Это ретушь, а эти правила направлены в другую сторону. Скилл отказывает в запросах «сделать красивее» на реальных людях и предлагает честный вариант: лучший свет, более длинный объектив, более чистый фон. Не используйте его для правки фотографий людей без их согласия.

</details>

## Ограничения и честность

- На регулярных выражениях и только для английского. Синонимы, которых линтер не знает, считаются отсутствующими; добавьте их и пришлите PR.
- Заметки по моделям — наблюдения из наших собственных прогонов иллюстраций, а не бенчмарки. Без количества картинок, без «на X % реалистичнее». Версии меняются; делайте пилот заново.
- Единственные числа в этом README — оценки линта, воспроизводимые командой `python3 scripts/lint_prompt.py examples/*/before.txt examples/*/after.txt`.
- Если глянцевая ретушь нужна вам намеренно, скилл скажет, какие правила он отбрасывает, вместо того чтобы молча применять чеклист.

## Похожие проекты

- [video-director](https://github.com/uniqaiapp/video-director): превращает идею в одну строку в покадровый промпт для видеомоделей (Kling, Veo, Sora и другие) со словарём камеры, света и движения. Тот же фотографический словарь, только в движении.
- [awesome-ai-video-prompts](https://github.com/uniqaiapp/awesome-ai-video-prompts): отобранные и разложенные по категориям промпты для видеомоделей с настройками, которые их породили.
- [skill-shrinker](https://github.com/uniqaiapp/skill-shrinker): сжимает любой SKILL.md или файл инструкций для агента; структура references/ в этом репозитории следует его советам.

Нужен улучшатель, который сохраняет поры? Те же правила лежат в основе [улучшения фото в UniqAI](https://uniqai.app/tools/upscaler-enhancer?utm_source=github&utm_medium=readme-ru&utm_campaign=no-plastic).

## Как помочь проекту

Issues и pull request приветствуются. Делайте изменения небольшими и прикладывайте пару промптов до/после в описании PR. Локальные проверки описаны в [CONTRIBUTING.md](CONTRIBUTING.md) (`python3 tests/run.py`, без зависимостей).

## Лицензия

[MIT](LICENSE) © UniqAI

---

<div align="center">

<sub>Сделано <a href="https://uniqai.app/?utm_source=github&utm_medium=readme-ru&utm_campaign=no-plastic">UniqAI</a> — Kling 3.0, Veo 3, Flux, Nano Banana и GPT-5/Claude/Gemini/Grok в одном приложении. Мы написали эти правила, чтобы делать иллюстрации для своего сайта, и продолжаем ими пользоваться.</sub>

</div>
