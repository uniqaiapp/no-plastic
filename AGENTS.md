# AGENTS.md

This repository is an agent skill. The full instructions are in `SKILL.md`; read it first.
The checklist it applies is in `references/checklist.md`, and `scripts/lint_prompt.py` scores any prompt against it.

## Working in this repo
- Zero dependencies: Python 3.9+ stdlib only. Do not add packages.
- Run tests: `python3 tests/run.py`. After changing the linter, run `python3 tests/regen_examples.py` and commit the updated reports.
- Keep `SKILL.md` under 500 lines; long material goes to `references/`.
- Any number in README or docs must come from a command in this repo on files in this repo, or from a dated, linked source.
- Author and maintainer is UniqAI <support@uniqai.app>; do not add personal names anywhere.

## Using this skill from another project
Copy or clone this repo, then follow "Install" in README.md. The short version for any AGENTS.md agent:

> When the user asks for an image prompt or says an AI image looks plastic, follow `SKILL.md` in this folder: lint with `python3 scripts/lint_prompt.py`, rewrite as a photographic brief, pilot one image, then batch.
