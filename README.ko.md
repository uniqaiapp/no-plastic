<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="no-plastic by UniqAI" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#설치)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#설치)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#설치)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-ko&utm_campaign=no-plastic)

**AI 인물 사진의 플라스틱 피부와 가짜 같은 느낌을 고칩니다: 프롬프트 규칙, 편집 잠금, 린터.**

[빠른 시작](#빠른-시작) · [동작 방식](#동작-방식) · [예제](#예제) · [설치](#설치) · [FAQ](#faq)

</div>

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português (BR)](README.pt-BR.md) · [日本語](README.ja.md) · 한국어

# no-plastic: AI 인물 사진의 플라스틱 피부와 어색함 고치기

AI 인물 사진이 가짜처럼 보이는 이유는 몇 가지로 정리됩니다: 모공 없는 피부, 거울처럼 좌우 대칭인 얼굴, 출처 없는 빛, 그려 넣은 듯한 보케, 틸 앤 오렌지 색보정, 그레인 없음. 하나하나가 모델의 기본값이고, 하나하나를 덮어쓰는 문장이 있습니다. no-plastic은 Claude Code 스킬(Cursor와 Codex 어댑터 포함)로, 이미지 프롬프트를 그 문장들이 들어간 사진 브리프로 다시 쓰고, 한 가지만 바꾸면서 인물은 그대로 유지하는 편집 프롬프트를 쓰며, 어떤 프롬프트든 체크리스트 기준으로 점수를 매기는 의존성 없는 린터를 함께 제공합니다. Flux, Nano Banana, Midjourney, SDXL을 기준으로 작성했지만, 어휘가 사진 용어이므로 다음 모델에도 그대로 통합니다.

| **태그가 아니라 브리프** | **얼굴을 지키는 편집** | **렌더링 전에 lint** |
|:---|:---|:---|
| 피사체, 프레이밍, 카메라, 빛, 팔레트, 질감, 시대, 네거티브: 여덟 개 필드, 세 문장에서 다섯 문장, 안티 플라스틱 규칙이 녹아 있습니다. | 변경 하나에 잠금 네 개(정체성, 사실감, 프레이밍, 이음새). 제거, 배경, 의상, 헤어, 보정, 셀카를 헤드샷으로 바꾸는 템플릿 포함. | `scripts/lint_prompt.py`가 커버리지를 점수로 매기고, 플라스틱 느낌을 만드는 단어를 표시하며, 빠진 부분을 위한 브리프 뼈대를 출력합니다. Python 3 표준 라이브러리만 사용합니다. |

## 빠른 시작

```bash
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
cd ~/.claude/skills/no-plastic
python3 scripts/lint_prompt.py examples/01-linkedin-headshot/before.txt examples/01-linkedin-headshot/after.txt
```

첫 번째 프롬프트("professional headshot of a beautiful woman, perfect skin, 8k...")는 0/100점을 받고 점수를 깎는 단어들이 나열되며, 다시 쓴 브리프는 100/100점을 받는 것을 볼 수 있습니다. 그다음 Claude Code에서 `/no-plastic`을 입력하고 프롬프트를 붙여 넣거나, 프롬프트를 첨부한 채 "이거 플라스틱 같아요"라고만 말해도 됩니다.

## 데모

<img alt="no-plastic demo: linting a plastic prompt and its rewrite" src="assets/demo.svg" width="820">

## 동작 방식

1. **분류.** *생성* 프롬프트(텍스트에서 이미지)인지 *편집* 프롬프트(기존 사진에 대한 지시: 제거, 의상 변경, 보정, 셀카를 헤드샷으로)인지 나눕니다. 린터는 첫 동사로 자동 감지합니다.
2. **Lint.** `python3 scripts/lint_prompt.py --brief prompt.txt`는 찾은 문구와 함께 여덟 필드 브리프를 출력하고, 프롬프트가 말하지 않은 자리에는 `?`를 넣습니다. 기본 리포트는 표시된 단어(`8k`, `masterpiece`, `flawless skin`, `cinematic lighting`, 태그 나열, SD1.5식 네거티브 주문)와 각각이 치르는 대가를 나열합니다.
3. **비평과 다시 쓰기.** 스킬이 가장 큰 빈틈 세 가지를 사진 용어로 짚고, 프롬프트를 브리프로 다시 씁니다: 피사체와 동작, 프레이밍, 카메라와 빛, 팔레트·질감·시대, 네거티브. 안티 플라스틱 규칙은 항상 들어갑니다: `natural skin texture with visible pores`, `slight asymmetry`, 감쇠가 있는 이름 붙은 광원, `fine film grain`, `not over-processed, no retouched plastic look`.
4. **모델별 적용.** Flux와 Nano Banana에는 피해야 할 것을 긍정형으로 바꿔 쓴 산문을 줍니다(네거티브 목록을 무시하기 때문입니다). Midjourney에는 `--style raw`, 낮은 `--stylize`, 짧은 `--no`를 줍니다. SDXL에는 피사체, 빛, 질감을 처음 77토큰 안에 넣은 브리프와 짧은 네거티브 필드를 줍니다. [references/model-notes.md](references/model-notes.md)를 참고하세요.
5. **파일럿 후 일괄 생성.** 이미지 한 장을 렌더링하고, 5초 점검(100 % 확대에서 이마 질감, 코 그림자, 캐치라이트, 헤어라인, 배경 감쇠)을 거친 뒤, 다시 돌리는 대신 브리프를 고치고, 그다음 세트를 렌더링합니다. UniqAI가 자사 사이트의 일러스트를 만들 때 쓴 워크플로가 바로 이것입니다. [references/pilot-review.md](references/pilot-review.md)에 작업 목록 형식과 판단 규칙이 있습니다.

```
loose request ──▶ lint (gaps + flags) ──▶ brief / edit with locks ──▶ per-model variant ──▶ re-lint ≥ 85 ──▶ pilot ──▶ review ──▶ batch
```

이 README의 점수는 `examples/`의 파일에 `python3 scripts/lint_prompt.py`를 실행해 얻은 것이며, 값이 달라지면 `tests/test_examples.py`가 실패합니다. 린터는 픽셀이 아니라 단어를 읽습니다. 100점은 브리프가 완전하다는 뜻이지, 이미지가 보장된다는 뜻이 아닙니다. 그래서 파일럿이 있습니다.

## 예제

[examples/](examples/README.md)에 리포트가 포함된 아홉 쌍이 있습니다. 그중 두 개의 전문:

<details open>
<summary><b>헤드샷: "8k masterpiece" → 85 mm 브리프(0 → 100)</b></summary>

**Before**(`examples/01-linkedin-headshot/before.txt`, 점수 0/100)

```text
Professional headshot of a beautiful woman, perfect skin, studio lighting, 8k, ultra realistic, masterpiece, sharp focus
```

**After**(`examples/01-linkedin-headshot/after.txt`, 점수 100/100)

```text
Head-and-shoulders business headshot of a woman in her early fifties with pale skin, a silver-grey bob and small hoop earrings, wearing a dark tailored blazer over a white top, a small relaxed smile, shoulders turned slightly off camera. A bright modern office with glass partitions and plants blurred softly behind her, face in the upper two thirds of a vertical frame. The look of an 85 mm lens at f/2.8: one large soft key light from camera left with a gentle fill and a subtle rim on the hair, clean catchlights, crisp focus on the eyes. Clean neutral daylight with no colour cast. Natural skin texture with visible pores and fine lines, a few flyaway hairs, no retouched plastic look, not over-processed.
```

</details>

<details>
<summary><b>편집: "remove the guy in the background" → 잠금이 있는 제거 프롬프트(5 → 100)</b></summary>

**Before**(`examples/07-edit-remove-stranger/before.txt`, 점수 5/100)

```text
Remove the guy in the background
```

**After**(`examples/07-edit-remove-stranger/after.txt`, 점수 100/100)

```text
Remove the stranger walking in the background behind her shoulder and fill the space with matching sand, sea and sky so nothing looks patched. Keep the woman, her pose, the lighting and everything else exactly as they are. Output the full original frame at exactly the same zoom and position; do not crop, zoom in or recompose. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.
```

</details>

<details>
<summary><b>이런 브리프로 만든 결과</b></summary>

UniqAI가 이런 방식으로 쓴 브리프로 자사 사이트용 일러스트를 생성한 결과입니다(스톡 사진 없음, 실존 인물 없음, 모델과 프롬프트는 출처로 보관). 왼쪽: 질감 문장과 네거티브 문장이 들어간 생성 브리프. 가운데와 오른쪽: 편집 쌍으로, 정체성 잠금과 프레이밍 잠금을 걸고 헤어만 바꾸고 나머지는 모두 유지했습니다.

| 생성 브리프 | 편집: 전 | 편집: 후 |
|:---:|:---:|:---:|
| <img src="https://uniqai.app/examples/gen/nano-banana-outfit.webp" alt="Waist-up portrait of a man in a green wool overcoat on a wet European side street, natural skin texture (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-before.webp" alt="Beauty-editorial portrait of a woman with long straight brown hair on an off-white backdrop (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-after.webp" alt="The same portrait with a chin-length bob; face, light and backdrop unchanged (AI-generated illustration)" width="260"> |
| `...50 mm lens at f/2, soft natural light, gentle filmic colour grade with creamy highlights and slightly lifted blacks, natural skin texture with visible pores, no retouched plastic look.` | `...85 mm lens at f/4, large soft window light from camera left with a gentle fill, warm off-white seamless backdrop, natural skin texture...` | `Change her hairstyle to a chin-length curtain bob... Keep her face, skin, expression, clothes, the background and the light exactly as they are... no smudges, repeated textures, halos or visible seams.` |

</details>

## 설치

지시 파일을 읽는 모든 에이전트에서 동작합니다. 쓰는 것을 고르세요. 요구 사항: 린터용 Python 3.9+. 설치할 패키지는 없습니다.

<details open>
<summary><b>Claude Code</b></summary>

```bash
# user-level (available in every project)
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
# or project-level
git clone https://github.com/uniqaiapp/no-plastic .claude/skills/no-plastic
```

그다음 아무 세션에서나 `/no-plastic`을 입력하거나, 그냥 작업을 설명하면 됩니다. 스킬의 `description`이 트리거합니다. `owner/repo`를 받는 스킬 디렉터리 CLI도 동작합니다: `npx skills add uniqaiapp/no-plastic`. uniqaiapp 마켓플레이스가 공개되면 플러그인으로도 설치할 수 있습니다: `/plugin marketplace add uniqaiapp/skills` 다음 `/plugin install no-plastic@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

`SKILL.md`, `scripts/`, `references/`, [`.cursor/rules/no-plastic.mdc`](.cursor/rules/no-plastic.mdc)를 프로젝트에 복사합니다. 규칙 파일이 `@SKILL.md`로 스킬을 포함합니다.

</details>

<details>
<summary><b>Codex / AGENTS.md를 읽는 모든 에이전트</b></summary>

`SKILL.md`, `scripts/`, `references/`를 `.agents/skills/no-plastic/`에 복사하고, [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md)의 스니펫을 `AGENTS.md`에 추가합니다. 이 저장소의 [`AGENTS.md`](AGENTS.md)가 범용 버전입니다.

</details>

<details>
<summary><b>일반 프롬프트, 또는 에이전트 없이</b></summary>

[`SKILL.md`](SKILL.md)를 아무 모델의 시스템 프롬프트에 붙여 넣으면 됩니다. 프런트매터를 제외하면 에이전트 전용 문법이 없습니다. [`references/checklist.md`](references/checklist.md)의 체크리스트는 종이 위에서도 쓸 수 있고, 린터는 단독으로 실행됩니다:

```bash
python3 scripts/lint_prompt.py --help
echo "portrait of a woman, 8k, flawless skin" | python3 scripts/lint_prompt.py -
python3 scripts/lint_prompt.py --strict --min-score 70 prompts/*.txt   # exit 1 if any prompt is below 70
```

</details>

## FAQ

<details>
<summary><b>프롬프트에 "realistic"을 넣어도 AI 인물 사진이 왜 플라스틱처럼 보이나요?</b></summary>

"realistic", "photorealistic", "8k"는 사진 캡션이 아니라 학습 데이터의 렌더링·CGI 쪽에서 온 라벨이기 때문입니다. 그 단어들은 자기가 붙어 있던 룩 쪽으로 결과를 끌어당깁니다. 사진은 렌즈, 빛, 필름으로 캡션이 달려 있으므로, 사진 쪽에 착지하려면 그 어휘를 써야 합니다: `85 mm at f/2.8`, `window light from camera left`, `fine film grain`, `natural skin texture with visible pores`.

</details>

<details>
<summary><b>"smooth skin, airbrushed" 같은 네거티브 프롬프트가 도움이 되나요?</b></summary>

SDXL과 Midjourney(`--no`)에서는 짧고 실제로 본 적 있는 룩을 지칭한다면 도움이 됩니다. Flux와 Nano Banana에는 네거티브 필드가 없어서 뒤에 붙인 목록은 무시됩니다. 같은 뜻을 마지막 문장에 산문으로 넣으세요: `natural skin texture, no retouched plastic look, not over-processed`. SD1.5에서 물려받은 목록(`bad anatomy, extra fingers, worst quality...`)은 현재 모델에서 아무 효과가 없고, 린터가 표시합니다.

</details>

<details>
<summary><b>린터가 이미지가 진짜처럼 보일지 알려 줄 수 있나요?</b></summary>

아니요. 린터는 픽셀이 아니라 프롬프트를 읽습니다. 100점은 브리프가 여덟 필드를 모두 다루고 알려진 문제 단어가 하나도 없다는 뜻입니다. 렌더링이 좋을지는 모델, 시드, 설정에 달려 있고, 그래서 스킬의 마지막 단계가 5초 점검으로 검토하는 한 장짜리 파일럿입니다.

</details>

<details>
<summary><b>사진을 편집할 때 같은 사람을 유지하려면 어떻게 하나요?</b></summary>

유지해야 할 것을 이름으로 나열하고 "exactly as they are"라고 말하세요: `Keep the face, features, skin tone, hair edges, expression and identity exactly as they are`, 그다음 프레임을 잠급니다: `Do not change the framing, crop, camera angle, or anything not mentioned`. 흔히 틀어지는 세 가지는 두 눈 사이 거리, 헤어라인, 배경 노출입니다. 하나라도 움직였다면 잠금 문장에 그 이름을 적고 다시 실행하세요. 편집 유형별 템플릿은 [references/edit-prompts.md](references/edit-prompts.md)에 있습니다.

</details>

<details>
<summary><b>더 젊거나 날씬하게 만드는 것은요?</b></summary>

그것은 리터칭이고, 이 규칙들은 반대 방향을 가리킵니다. 스킬은 실존 인물을 "더 잘생기게" 해 달라는 요청을 거절하고 대신 정직한 버전을 제안합니다: 더 좋은 빛, 더 긴 렌즈, 더 깨끗한 배경. 당사자 동의 없이 다른 사람의 사진을 편집하는 데 쓰지 마세요.

</details>

## 한계와 정직한 안내

- 정규식 기반이고 영어 전용입니다. 린터가 모르는 동의어는 빠진 것으로 집계됩니다. 추가해서 PR을 보내 주세요.
- 모델 노트는 저희 일러스트 작업에서 관찰한 내용이지 벤치마크가 아닙니다. 이미지 수도, "X % 더 사실적"이라는 주장도 없습니다. 버전은 바뀌니 다시 파일럿하세요.
- 이 README에 있는 숫자는 lint 점수뿐이며, `python3 scripts/lint_prompt.py examples/*/before.txt examples/*/after.txt`로 재현할 수 있습니다.
- 에디토리얼 리터칭 룩을 일부러 원한다면, 스킬은 체크리스트를 조용히 적용하는 대신 어떤 규칙을 빼는지 알려 줍니다.

## 관련 프로젝트

- [video-director](https://github.com/uniqaiapp/video-director): 한 줄 아이디어를 AI 영상 모델(Kling, Veo, Sora 등)용 샷 단위 프롬프트로 바꿉니다. 카메라, 조명, 모션 용어 포함. 같은 사진 어휘를 움직이는 그림에 적용합니다.
- [awesome-ai-video-prompts](https://github.com/uniqaiapp/awesome-ai-video-prompts): AI 영상 모델용으로 선별하고 분류한 프롬프트와, 그 결과를 만든 설정.
- [skill-shrinker](https://github.com/uniqaiapp/skill-shrinker): SKILL.md나 에이전트 지시 파일을 줄입니다. 이 저장소의 references/ 구조가 그 조언을 따릅니다.

모공을 지키는 보정 도구가 필요하신가요? 같은 규칙이 [UniqAI 사진 보정 도구](https://uniqai.app/tools/upscaler-enhancer?utm_source=github&utm_medium=readme-ko&utm_campaign=no-plastic)를 움직입니다.

## 기여하기

이슈와 풀 리퀘스트를 환영합니다. 변경은 작게 유지하고, PR 설명에 전후 프롬프트 쌍을 넣어 주세요. 로컬 검사 방법(`python3 tests/run.py`, 의존성 없음)은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 라이선스

[MIT](LICENSE) © UniqAI

---

<div align="center">

<sub><a href="https://uniqai.app/?utm_source=github&utm_medium=readme-ko&utm_campaign=no-plastic">UniqAI</a> 제작 — Kling 3.0, Veo 3, Flux, Nano Banana, 그리고 GPT-5/Claude/Gemini/Grok를 하나의 앱에서. 자사 사이트 일러스트를 만들려고 이 규칙을 썼고, 그 뒤로도 계속 쓰고 있습니다.</sub>

</div>
