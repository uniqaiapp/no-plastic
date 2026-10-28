"""Unit tests for scripts/lint_prompt.py (stdlib only)."""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import lint_prompt as lp  # noqa: E402

LINT = os.path.join(ROOT, "scripts", "lint_prompt.py")


def run(args, stdin=None):
    return subprocess.run([sys.executable, LINT] + args, cwd=ROOT, input=stdin,
                          capture_output=True, text=True)


GOOD_GEN = (
    "Head-and-shoulders portrait of a man in his forties with a short grey beard and rimless glasses, "
    "wearing a charcoal wool sweater, a neutral friendly expression, face in the upper two thirds of a vertical frame. "
    "85 mm lens at f/2.8, large soft window light from camera left with a gentle fill. True-to-life colour, slightly "
    "lifted blacks. Editorial photograph with natural skin texture, visible pores and stubble, fine film grain, "
    "no retouched plastic look."
)

BAD_GEN = "beautiful woman, perfect skin, 8k, ultra realistic, masterpiece, studio lighting"

GOOD_EDIT = (
    "Remove the metal signpost and fill the space with matching lake, shore and forest. Keep the mountains, the light "
    "and everything else exactly as they are. Do not change the framing, crop, camera angle, or anything not mentioned. "
    "The result must look like an untouched real photograph, with no smudges, repeated textures, halos or visible seams."
)


class TestModeDetection(unittest.TestCase):
    def test_edit_verb_first(self):
        self.assertEqual(lp.detect_mode("Remove the bin by the door."), "edit")
        self.assertEqual(lp.detect_mode("Change her hairstyle to a bob."), "edit")
        self.assertEqual(lp.detect_mode("Turn this selfie into a headshot."), "edit")

    def test_generate_by_default(self):
        self.assertEqual(lp.detect_mode(GOOD_GEN), "generate")
        self.assertEqual(lp.detect_mode(BAD_GEN), "generate")

    def test_force_mode(self):
        self.assertEqual(lp.lint("Remove the bin.", mode="generate")["mode"], "generate")


class TestGenerateScoring(unittest.TestCase):
    def test_good_brief_scores_a(self):
        r = lp.lint(GOOD_GEN)
        self.assertEqual(r["grade"], "A", r)
        self.assertTrue(all(c["ok"] for c in r["coverage"]), [c["id"] for c in r["coverage"] if not c["ok"]])
        self.assertEqual(r["flags"], [])

    def test_bad_prompt_scores_low_and_flags(self):
        r = lp.lint(BAD_GEN)
        self.assertLess(r["score"], 30)
        ids = {f["id"] for f in r["flags"]}
        self.assertIn("superlatives", ids)
        self.assertIn("plastic_skin", ids)
        self.assertIn("vague_light", ids)
        self.assertIn("too_short", ids)

    def test_superlatives_penalise(self):
        base = GOOD_GEN
        worse = base + " Masterpiece, 8k, ultra realistic."
        self.assertLess(lp.lint(worse)["score"], lp.lint(base)["score"])

    def test_tag_soup_detected(self):
        soup = "portrait, woman, 25yo, freckles, red hair, smiling, bokeh, 85mm, cinematic, sharp focus, detailed"
        ids = {f["id"] for f in lp.lint(soup)["flags"]}
        self.assertIn("tag_soup", ids)
        self.assertNotIn("tag_soup", {f["id"] for f in lp.lint(GOOD_GEN)["flags"]})

    def test_boilerplate_negatives_flagged(self):
        r = lp.lint(GOOD_GEN + " Negative: bad anatomy, extra fingers, worst quality, watermark.")
        self.assertIn("boilerplate_negatives", {f["id"] for f in r["flags"]})

    def test_repetition_flagged(self):
        r = lp.lint(GOOD_GEN + " Large soft window light from camera left with a gentle fill.")
        self.assertIn("repetition", {f["id"] for f in r["flags"]})

    def test_score_bounds(self):
        for text in (BAD_GEN, GOOD_GEN, "x", "a " * 400):
            s = lp.lint(text)["score"]
            self.assertTrue(0 <= s <= 100)


class TestEditScoring(unittest.TestCase):
    def test_good_edit_scores_a(self):
        r = lp.lint(GOOD_EDIT)
        self.assertEqual(r["mode"], "edit")
        self.assertEqual(r["grade"], "A", r)
        self.assertTrue(all(c["ok"] for c in r["coverage"]), [c["id"] for c in r["coverage"] if not c["ok"]])

    def test_bare_edit_misses_locks(self):
        r = lp.lint("Remove the guy in the background")
        missing = {c["id"] for c in r["coverage"] if not c["ok"]}
        self.assertIn("preserve", missing)
        self.assertIn("framing", missing)
        self.assertIn("seams", missing)
        self.assertLess(r["score"], 30)

    def test_smoothing_words_flagged_in_edit(self):
        r = lp.lint("Enhance this photo, smooth the skin and make it flawless.")
        self.assertIn("plastic_skin", {f["id"] for f in r["flags"]})


class TestCli(unittest.TestCase):
    def test_help(self):
        p = run(["--help"])
        self.assertEqual(p.returncode, 0)
        self.assertIn("--brief", p.stdout)

    def test_stdin_and_json(self):
        p = run(["--json", "-"], stdin=GOOD_GEN)
        self.assertEqual(p.returncode, 0)
        data = json.loads(p.stdout)
        self.assertEqual(data["file"], "stdin")
        self.assertEqual(data["grade"], "A")
        self.assertEqual(len(data["coverage"]), 8)

    def test_multiple_files_json_is_list(self):
        p = run(["--json", "examples/01-linkedin-headshot/before.txt", "examples/01-linkedin-headshot/after.txt"])
        self.assertEqual(p.returncode, 0)
        self.assertEqual(len(json.loads(p.stdout)), 2)

    def test_strict_exit_code(self):
        self.assertEqual(run(["--strict", "-"], stdin=BAD_GEN).returncode, 1)
        self.assertEqual(run(["--strict", "-"], stdin=GOOD_GEN).returncode, 0)
        self.assertEqual(run(["--strict", "--min-score", "101", "-"], stdin=GOOD_GEN).returncode, 1)

    def test_negative_section_is_split(self):
        pos, neg = lp.split_negative("A portrait, 85 mm.\nNegative: smooth skin, render")
        self.assertEqual(pos, "A portrait, 85 mm.")
        self.assertEqual(neg, "smooth skin, render")
        pos, neg = lp.split_negative("A portrait, 85 mm --ar 4:5 --style raw --no smooth skin, text --s 50")
        self.assertEqual(pos, "A portrait, 85 mm")
        self.assertEqual(neg, "smooth skin, text")

    def test_negative_words_are_not_plastic_triggers(self):
        r = lp.lint(GOOD_GEN + "\nNegative: smooth skin, airbrushed, doll-like")
        self.assertNotIn("plastic_skin", {f["id"] for f in r["flags"]})
        self.assertTrue(next(c for c in r["coverage"] if c["id"] == "negatives")["ok"])

    def test_negated_trigger_is_ignored(self):
        r = lp.lint(GOOD_GEN.replace("no retouched plastic look", "no retouched plastic look, not airbrushed"))
        self.assertNotIn("plastic_skin", {f["id"] for f in r["flags"]})

    def test_brief_skeleton(self):
        p = run(["--brief", "-"], stdin=BAD_GEN)
        self.assertEqual(p.returncode, 0)
        self.assertIn("Photographic brief", p.stdout)
        self.assertIn("?", p.stdout)
        self.assertIn("Camera / lens:", p.stdout)

    def test_empty_input_is_an_error(self):
        p = run(["-"], stdin="   \n")
        self.assertEqual(p.returncode, 2)

    def test_missing_file_is_an_error(self):
        p = run(["examples/does-not-exist.txt"])
        self.assertEqual(p.returncode, 2)

    def test_report_mentions_every_category(self):
        p = run(["-"], stdin=BAD_GEN)
        for label in ("subject", "composition", "camera / lens", "light", "palette / grade", "texture", "era / medium", "anti-plastic negatives"):
            self.assertIn(label, p.stdout)


if __name__ == "__main__":
    unittest.main()
