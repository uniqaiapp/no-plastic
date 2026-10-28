# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-28

### Added

- `SKILL.md`: the skill (classify, lint, critique, rewrite as a photographic brief, adapt per model, re-lint, pilot then batch), with the anti-plastic rules and the edit-prompt shape.
- `scripts/lint_prompt.py`: zero-dependency linter that scores generate prompts on eight brief fields and edit prompts on five locks, flags the words that cause the plastic look, understands `Negative:` lines and Midjourney `--no`, and prints a brief skeleton with `--brief`. JSON output and `--strict` exit codes.
- `references/`: the AI-tells checklist with the five-second review, the brief template and vocabulary, edit-prompt templates per edit type, model notes for Flux, Nano Banana, Midjourney and SDXL, and the pilot-review workflow.
- `examples/`: nine before/after pairs (five generate, four edit) with committed lint reports that the tests reproduce byte-for-byte.
- Adapters for Claude Code (`.claude-plugin/plugin.json`), Cursor (`.cursor/rules/no-plastic.mdc`), Codex (`codex/INSTRUCTIONS.md`) and any `AGENTS.md` agent.
- Tests (`python3 tests/run.py`), CI workflow, issue and PR templates, repo metadata, banner, terminal demo and social preview assets.
