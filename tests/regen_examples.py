#!/usr/bin/env python3
"""Maintainer helper: regenerate the committed lint reports in examples/ after changing the linter.

    python3 tests/regen_examples.py

Writes examples/<name>/before.report.txt and after.report.txt by running scripts/lint_prompt.py
from the repo root with the same relative paths the tests use. Review the diff before committing.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples")
LINT = os.path.join("scripts", "lint_prompt.py")


def main():
    for name in sorted(os.listdir(EX)):
        d = os.path.join(EX, name)
        if not os.path.isdir(d):
            continue
        for side in ("before", "after"):
            rel = os.path.join("examples", name, side + ".txt")
            if not os.path.exists(os.path.join(ROOT, rel)):
                continue
            out = subprocess.run([sys.executable, LINT, rel], cwd=ROOT, capture_output=True, text=True)
            if out.returncode not in (0, 1):
                print(out.stderr, file=sys.stderr)
                return out.returncode
            with open(os.path.join(d, side + ".report.txt"), "w", encoding="utf-8") as fh:
                fh.write(out.stdout)
            print("wrote", os.path.join("examples", name, side + ".report.txt"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
