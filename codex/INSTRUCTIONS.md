# no-plastic for Codex

Paste the block below into your project's `AGENTS.md` (or Codex custom instructions),
and copy `SKILL.md`, `scripts/` and `references/` from https://github.com/uniqaiapp/no-plastic into `.agents/skills/no-plastic/`.

---
When the user asks for an image-generation prompt (portrait, headshot, product, lifestyle, edit of an existing photo), or says an AI image looks plastic, waxy, too smooth or fake, follow `.agents/skills/no-plastic/SKILL.md`: lint the prompt with `python3 .agents/skills/no-plastic/scripts/lint_prompt.py`, rewrite it as a photographic brief, and run one pilot image before any batch.
---
