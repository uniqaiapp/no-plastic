<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="no-plastic by UniqAI" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#インストール)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#インストール)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#インストール)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-ja&utm_campaign=no-plastic)

**プラスチックみたいな肌と作り物に見える AI ポートレートを直す：プロンプトのルール、編集ロック、そして linter。**

[クイックスタート](#クイックスタート) · [仕組み](#仕組み) · [例](#例) · [インストール](#インストール) · [FAQ](#faq)

</div>

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português (BR)](README.pt-BR.md) · 日本語 · [한국어](README.ko.md)

# no-plastic：AI ポートレートのプラスチック肌と不自然さを直す

AI ポートレートが作り物に見える理由は、短いリストに収まります。毛穴のない肌、鏡のように左右対称な顔、どこから来たのか分からない光、描き足されたボケ、ティール＆オレンジのグレーディング、粒子のなさ。どれもモデルのデフォルトで、どれにもそれを上書きする一文があります。no-plastic は Claude Code のスキル（Cursor と Codex のアダプター付き）で、画像プロンプトをそうした文を含む写真的なブリーフに書き換え、1 か所だけ変えて人物はそのまま保つ編集プロンプトを書き、任意のプロンプトをチェックリストに照らして採点する依存関係ゼロの linter を同梱しています。Flux、Nano Banana、Midjourney、SDXL 向けに書かれていますが、語彙は写真のものなので、次のモデルにもそのまま持ち越せます。

| **タグではなくブリーフ** | **顔を保つ編集** | **レンダリング前に lint** |
|:---|:---|:---|
| 被写体、フレーミング、カメラ、光、パレット、質感、時代、ネガティブ。8 つのフィールドを 3 〜 5 文にまとめ、アンチプラスチックのルールを織り込みます。 | 変更 1 つと 4 つのロック（アイデンティティ、リアリズム、フレーミング、継ぎ目）。削除、背景、服装、髪、エンハンス、自撮りからヘッドショットへのテンプレート付き。 | `scripts/lint_prompt.py` がカバー率を採点し、プラスチック感の原因になる単語にフラグを立て、足りない部分のためのブリーフの骨組みを出力します。Python 3 の標準ライブラリのみ。 |

## クイックスタート

```bash
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
cd ~/.claude/skills/no-plastic
python3 scripts/lint_prompt.py examples/01-linkedin-headshot/before.txt examples/01-linkedin-headshot/after.txt
```

最初のプロンプト（"professional headshot of a beautiful woman, perfect skin, 8k..."）が 0/100 で、スコアを下げている単語が列挙され、書き換えたブリーフが 100/100 になるはずです。次に Claude Code で `/no-plastic` と入力してプロンプトを貼り付けるか、プロンプトを添えて「これ、プラスチックっぽい」と伝えるだけでも構いません。

## デモ

<img alt="no-plastic demo: linting a plastic prompt and its rewrite" src="assets/demo.svg" width="820">

## 仕組み

1. **分類。** *生成*プロンプト（テキストから画像）か、*編集*プロンプト（既存の写真への指示：削除、服装の変更、エンハンス、自撮りからヘッドショット）かを判別します。linter は冒頭の動詞で自動判定します。
2. **Lint。** `python3 scripts/lint_prompt.py --brief prompt.txt` は、見つかった表現を当てはめた 8 フィールドのブリーフを出力し、プロンプトが触れていない箇所には `?` を置きます。通常のレポートは、フラグの立った単語（`8k`、`masterpiece`、`flawless skin`、`cinematic lighting`、タグの羅列、SD1.5 時代のネガティブの定型文）と、それぞれの代償を列挙します。
3. **批評と書き換え。** スキルは最大の欠落 3 つを写真の用語で指摘し、プロンプトをブリーフとして書き換えます。被写体と動作、フレーミング、カメラと光、パレットと質感と時代、ネガティブ。アンチプラスチックのルールは常に入ります：`natural skin texture with visible pores`、`slight asymmetry`、減衰のある名前付きの光源、`fine film grain`、`not over-processed, no retouched plastic look`。
4. **モデルごとの調整。** Flux と Nano Banana には、避けたいことを肯定形で表現した散文を渡します（ネガティブのリストは無視されます）。Midjourney には `--style raw`、低めの `--stylize`、短い `--no` を。SDXL には被写体、光、質感を最初の 77 トークンに入れたブリーフと短いネガティブフィールドを渡します。[references/model-notes.md](references/model-notes.md) を参照してください。
5. **パイロット、それからバッチ。** 1 枚レンダリングし、5 秒レビュー（100 % 表示での額の質感、鼻の影、キャッチライト、生え際、背景の減衰）を行い、再抽選ではなくブリーフを直してから、セットをレンダリングします。これは UniqAI が自社サイトのイラストを制作するときに使ったワークフローです。[references/pilot-review.md](references/pilot-review.md) にジョブリストの形式と判断ルールがあります。

```
loose request ──▶ lint (gaps + flags) ──▶ brief / edit with locks ──▶ per-model variant ──▶ re-lint ≥ 85 ──▶ pilot ──▶ review ──▶ batch
```

この README のスコアは `python3 scripts/lint_prompt.py` を `examples/` のファイルに対して実行して得たもので、ずれがあれば `tests/test_examples.py` が失敗します。linter が読むのは単語であってピクセルではありません。100 は完全なブリーフを意味するのであって、画像の保証ではありません。そのためのパイロットです。

## 例

[examples/](examples/README.md) にレポート付きの 9 ペアがあります。そのうち 2 つを全文で：

<details open>
<summary><b>ヘッドショット：「8k masterpiece」→ 85 mm のブリーフ（0 → 100）</b></summary>

**ビフォー**（`examples/01-linkedin-headshot/before.txt`、スコア 0/100）

```text
Professional headshot of a beautiful woman, perfect skin, studio lighting, 8k, ultra realistic, masterpiece, sharp focus
```

**アフター**（`examples/01-linkedin-headshot/after.txt`、スコア 100/100）

```text
Head-and-shoulders business headshot of a woman in her early fifties with pale skin, a silver-grey bob and small hoop earrings, wearing a dark tailored blazer over a white top, a small relaxed smile, shoulders turned slightly off camera. A bright modern office with glass partitions and plants blurred softly behind her, face in the upper two thirds of a vertical frame. The look of an 85 mm lens at f/2.8: one large soft key light from camera left with a gentle fill and a subtle rim on the hair, clean catchlights, crisp focus on the eyes. Clean neutral daylight with no colour cast. Natural skin texture with visible pores and fine lines, a few flyaway hairs, no retouched plastic look, not over-processed.
```

</details>

<details>
<summary><b>編集：「remove the guy in the background」→ ロック付きの削除（5 → 100）</b></summary>

**ビフォー**（`examples/07-edit-remove-stranger/before.txt`、スコア 5/100）

```text
Remove the guy in the background
```

**アフター**（`examples/07-edit-remove-stranger/after.txt`、スコア 100/100）

```text
Remove the stranger walking in the background behind her shoulder and fill the space with matching sand, sea and sky so nothing looks patched. Keep the woman, her pose, the lighting and everything else exactly as they are. Output the full original frame at exactly the same zoom and position; do not crop, zoom in or recompose. Do not change the framing, crop, camera angle, or anything not mentioned. The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams.
```

</details>

<details>
<summary><b>こうしたブリーフから何ができるか</b></summary>

UniqAI がこの方法で書いたブリーフを使って自社サイト向けに生成したイラストです（ストックフォトも実在の人物もなし。モデルとプロンプトは来歴として保管しています）。左：質感とネガティブの文を含む生成ブリーフ。中央と右：編集ペアで、アイデンティティとフレーミングのロックを掛けて髪だけ変え、それ以外はそのまま保ったものです。

| 生成ブリーフ | 編集：ビフォー | 編集：アフター |
|:---:|:---:|:---:|
| <img src="https://uniqai.app/examples/gen/nano-banana-outfit.webp" alt="Waist-up portrait of a man in a green wool overcoat on a wet European side street, natural skin texture (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-before.webp" alt="Beauty-editorial portrait of a woman with long straight brown hair on an off-white backdrop (AI-generated illustration)" width="260"> | <img src="https://uniqai.app/examples/gen/hairstyle-bob-after.webp" alt="The same portrait with a chin-length bob; face, light and backdrop unchanged (AI-generated illustration)" width="260"> |
| `...50 mm lens at f/2, soft natural light, gentle filmic colour grade with creamy highlights and slightly lifted blacks, natural skin texture with visible pores, no retouched plastic look.` | `...85 mm lens at f/4, large soft window light from camera left with a gentle fill, warm off-white seamless backdrop, natural skin texture...` | `Change her hairstyle to a chin-length curtain bob... Keep her face, skin, expression, clothes, the background and the light exactly as they are... no smudges, repeated textures, halos or visible seams.` |

</details>

## インストール

指示ファイルを読むエージェントならどれでも使えます。お使いのものを選んでください。要件：linter には Python 3.9 以上。インストールするパッケージはありません。

<details open>
<summary><b>Claude Code</b></summary>

```bash
# user-level (available in every project)
git clone https://github.com/uniqaiapp/no-plastic ~/.claude/skills/no-plastic
# or project-level
git clone https://github.com/uniqaiapp/no-plastic .claude/skills/no-plastic
```

その後、任意のセッションで `/no-plastic` と入力するか、タスクを説明するだけで、スキルの `description` がトリガーになります。`owner/repo` を受け取るスキルディレクトリの CLI でも動きます：`npx skills add uniqaiapp/no-plastic`。プラグインとしては、uniqaiapp マーケットプレイスの公開後に `/plugin marketplace add uniqaiapp/skills` に続けて `/plugin install no-plastic@uniqaiapp` を実行してください。

</details>

<details>
<summary><b>Cursor</b></summary>

`SKILL.md`、`scripts/`、`references/`、[`.cursor/rules/no-plastic.mdc`](.cursor/rules/no-plastic.mdc) をプロジェクトにコピーしてください。ルールファイルは `@SKILL.md` でスキルを埋め込みます。

</details>

<details>
<summary><b>Codex / AGENTS.md を読む任意のエージェント</b></summary>

`SKILL.md`、`scripts/`、`references/` を `.agents/skills/no-plastic/` にコピーし、[`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) のスニペットを `AGENTS.md` に追加してください。このリポジトリ自身の [`AGENTS.md`](AGENTS.md) が汎用版です。

</details>

<details>
<summary><b>プレーンなプロンプト、またはエージェントなし</b></summary>

[`SKILL.md`](SKILL.md) を任意のモデルのシステムプロンプトに貼り付けてください。フロントマター以外にエージェント固有の構文はありません。[`references/checklist.md`](references/checklist.md) のチェックリストは紙の上でも使え、linter は単体で動きます：

```bash
python3 scripts/lint_prompt.py --help
echo "portrait of a woman, 8k, flawless skin" | python3 scripts/lint_prompt.py -
python3 scripts/lint_prompt.py --strict --min-score 70 prompts/*.txt   # exit 1 if any prompt is below 70
```

</details>

## FAQ

<details>
<summary><b>プロンプトに「realistic」と書いても AI ポートレートがプラスチックっぽくなるのはなぜですか</b></summary>

「realistic」「photorealistic」「8k」は、学習データのレンダリングや CGI の片隅から来たラベルであって、写真のキャプションから来たものではないからです。これらは、もともと付いていた先の見た目に引っ張ります。写真にはレンズ、光、フィルムでキャプションが付いているので、写真側に着地させる語彙はそちらです：`85 mm at f/2.8`、`window light from camera left`、`fine film grain`、`natural skin texture with visible pores`。

</details>

<details>
<summary><b>「smooth skin, airbrushed」のようなネガティブプロンプトは効きますか</b></summary>

SDXL と Midjourney（`--no`）では効きます。短く、実際に見たことのある見た目を名指しする限りは。Flux と Nano Banana にはネガティブのフィールドがなく、末尾のリストは無視されます。同じ意図を最後の一文に散文として入れてください：`natural skin texture, no retouched plastic look, not over-processed`。SD1.5 から受け継がれたリスト（`bad anatomy, extra fingers, worst quality...`）は現行モデルでは何の効果もなく、linter がフラグを立てます。

</details>

<details>
<summary><b>linter は画像がリアルに見えるかどうかを教えてくれますか</b></summary>

いいえ。読むのはプロンプトであってピクセルではありません。100 は、ブリーフが 8 つのフィールドを網羅し、既知の問題語を含まないという意味です。レンダリングが良いかどうかはモデル、シード、設定次第で、だからこそスキルの最後のステップは、5 秒チェックでレビューする 1 枚のパイロットなのです。

</details>

<details>
<summary><b>写真を編集するとき、同じ人物のまま保つには</b></summary>

残すべきものを名指しで列挙し、「exactly as they are」と言います：`Keep the face, features, skin tone, hair edges, expression and identity exactly as they are`。次にフレームをロックします：`Do not change the framing, crop, camera angle, or anything not mentioned`。ずれやすいのは目の間の距離、生え際、背景の露出の 3 つです。どれかが動いたら、ロックにそれを名指しして再実行してください。編集タイプごとのテンプレートは [references/edit-prompts.md](references/edit-prompts.md) にあります。

</details>

<details>
<summary><b>誰かを若く、あるいは痩せて見せるのは</b></summary>

それはレタッチで、このルールは逆の方向を向いています。スキルは実在の人物に対する「もっと良く見せて」という依頼を断り、代わりに正直な版を提案します。より良い光、より長いレンズ、より整った背景です。本人の同意なしに人物写真の編集に使わないでください。

</details>

## 制限事項と正直な注記

- 正規表現ベースで英語のみです。linter が知らない同義語は欠落として数えられます。追加して PR を送ってください。
- モデルノートは私たち自身のイラスト制作から得た観察で、ベンチマークではありません。画像の枚数も「X % リアルに」もありません。バージョンは変わります。改めてパイロットしてください。
- この README にある数字は lint スコアだけで、`python3 scripts/lint_prompt.py examples/*/before.txt examples/*/after.txt` で再現できます。
- 雑誌のレタッチ風の見た目を意図的に求めるなら、スキルは黙ってチェックリストを適用するのではなく、どのルールを外すかを伝えます。

## 関連プロジェクト

- [video-director](https://github.com/uniqaiapp/video-director)：1 行のアイデアを AI 動画モデル（Kling、Veo、Sora など）向けのショットごとのプロンプトに変換します。カメラ、ライティング、動きの語彙付き。同じ写真の語彙を、動く絵に。
- [awesome-ai-video-prompts](https://github.com/uniqaiapp/awesome-ai-video-prompts)：AI 動画モデル向けの、生成時の設定付きで分類されたキュレーション済みプロンプト集。
- [skill-shrinker](https://github.com/uniqaiapp/skill-shrinker)：SKILL.md やエージェントの指示ファイルを圧縮します。このリポジトリの references/ の構成はその助言に従っています。

毛穴を残すエンハンサーが必要ですか。同じルールが [UniqAI のフォトエンハンサー](https://uniqai.app/tools/upscaler-enhancer?utm_source=github&utm_medium=readme-ja&utm_campaign=no-plastic) を動かしています。

## コントリビュート

Issue とプルリクエストを歓迎します。変更は小さく保ち、PR の説明にビフォー／アフターのプロンプトのペアを含めてください。ローカルでのチェック（`python3 tests/run.py`、依存関係なし）については [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ライセンス

[MIT](LICENSE) © UniqAI

---

<div align="center">

<sub>制作：<a href="https://uniqai.app/?utm_source=github&utm_medium=readme-ja&utm_campaign=no-plastic">UniqAI</a> — Kling 3.0、Veo 3、Flux、Nano Banana、そして GPT-5/Claude/Gemini/Grok をひとつのアプリで。このルールは自社サイトのイラストを制作するために書き、その後も使い続けています。</sub>

</div>
