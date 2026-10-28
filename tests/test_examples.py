"""Every example pair reproduces its committed report byte-for-byte, and every 'after' beats its 'before'.

This is how the numbers in README stay honest: the reports are the output of
`python3 scripts/lint_prompt.py examples/<name>/<side>.txt` run from the repo root.
Regenerate them with `python3 tests/regen_examples.py` after changing the linter.
"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples")
LINT = os.path.join("scripts", "lint_prompt.py")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import lint_prompt as lp  # noqa: E402


def example_dirs():
    return sorted(d for d in os.listdir(EX) if os.path.isdir(os.path.join(EX, d)))


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


class TestExamples(unittest.TestCase):
    def test_there_are_examples(self):
        self.assertGreaterEqual(len(example_dirs()), 6)

    def test_each_example_is_complete(self):
        for name in example_dirs():
            for f in ("before.txt", "after.txt", "before.report.txt", "after.report.txt"):
                self.assertTrue(os.path.exists(os.path.join(EX, name, f)), "%s/%s missing" % (name, f))

    def test_reports_reproduce_byte_for_byte(self):
        for name in example_dirs():
            for side in ("before", "after"):
                rel = os.path.join("examples", name, side + ".txt")
                p = subprocess.run([sys.executable, LINT, rel], cwd=ROOT, capture_output=True, text=True)
                self.assertIn(p.returncode, (0, 1), p.stderr)
                expected = read(os.path.join(EX, name, side + ".report.txt"))
                self.assertEqual(p.stdout, expected, "stale report: %s/%s.report.txt (run tests/regen_examples.py)" % (name, side))

    def test_after_beats_before(self):
        for name in example_dirs():
            before = lp.lint(read(os.path.join(EX, name, "before.txt")))
            after = lp.lint(read(os.path.join(EX, name, "after.txt")))
            self.assertGreater(after["score"], before["score"], name)
            self.assertGreaterEqual(after["score"], 85, "%s after.txt scores %d, expected A" % (name, after["score"]))
            self.assertEqual([f for f in after["flags"] if f["severity"] == 2], [], "%s after.txt has red flags" % name)

    def test_edit_examples_detected_as_edit(self):
        for name in example_dirs():
            is_edit = "-edit-" in name
            for side in ("before", "after"):
                mode = lp.lint(read(os.path.join(EX, name, side + ".txt")))["mode"]
                self.assertEqual(mode, "edit" if is_edit else "generate", "%s/%s" % (name, side))

    def test_examples_readme_lists_every_example(self):
        readme = read(os.path.join(EX, "README.md"))
        for name in example_dirs():
            self.assertIn(name, readme, "examples/README.md does not mention %s" % name)


if __name__ == "__main__":
    unittest.main()
