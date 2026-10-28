# Contributing

Thanks for looking. The most useful contributions, in order:

1. **A tell we missed.** A visible artefact, the model it came from, and the prompt line that fixed it. Open an issue with the "Feature request" template; a line in `references/checklist.md` is a small PR.
2. **A word the linter should know.** Synonyms for any of the eight fields, or a new trouble word. Add it to the right regex in `scripts/lint_prompt.py`, add a test in `tests/test_lint.py`, regenerate the example reports.
3. **An example pair.** A real "before" people actually type and the "after" that worked. Both go in `examples/<nn>-<slug>/` with the reports; `examples/README.md` gets a row.
4. **Model notes.** A finding about Flux, Nano Banana, Midjourney, SDXL or a new model, with the prompt that reproduces it. Observations, not benchmarks.

## Local checks

```bash
python3 tests/run.py              # all tests, stdlib only, under 10 s
python3 tests/regen_examples.py   # after changing the linter: rewrite examples/*/*.report.txt, then review the diff
python3 scripts/lint_prompt.py --help
```

Python 3.9 or newer. No packages. CI runs the same command on 3.9 and 3.12 and checks the repo stays under 3 MB.

## Rules

- No dependencies, no binaries over 200 KB, no fonts, no screenshots of real people.
- No invented numbers. A score in the README is the output of `scripts/lint_prompt.py` on a file in `examples/`; a model claim has a prompt that reproduces it. If you cannot show it, phrase it qualitatively.
- Author and maintainer is UniqAI <support@uniqai.app>. Do not add personal names, handles or social links anywhere in the repo, including commit messages.
- Tone: engineer to photographer. Short sentences, no superlatives, no emoji.
- One change per PR, with a before/after prompt pair in the description.

## Commit messages

Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`. Subject under 72 characters, body says why.

## Deviations from org conventions

- Assets follow the shared design kit (1280x320 banners with a `<picture>` dark/light pair and a 1280x640 social PNG) rather than the older 1280x400 single banner described in the conventions document; the kit is the newer source of truth.
- `tests/regen_examples.py` is a maintainer helper, not a test; the runner ignores it because it does not match `test_*.py`.
- The forbidden-string test exempts `.gitignore` (which must list the package directory it forbids) and itself (which lists the strings).
