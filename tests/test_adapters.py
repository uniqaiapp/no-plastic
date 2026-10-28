"""Structure tests required by the uniqaiapp conventions: adapters point at SKILL.md,
versions match, and no file contains a forbidden string."""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "no-plastic"

# Personal handles are stored as code points so the list itself never spells them out.
_HANDLES = [bytes([97, 101, 111, 114, 105, 97]).decode(), bytes([114, 105, 99, 104, 112, 101, 97, 99, 104]).decode()]
FORBIDDEN = _HANDLES + [
    "/Users/", "/Volumes/", "node_modules", "sk-ant-", "sk_live",
    "api_key=", "API_KEY=<real", "TODO: fill", "lorem ipsum",
]
TEXT_EXT = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".mdc", ".svg", ".cff", ".toml", ".cfg", ""}
SKIP_DIRS = {".git", "__pycache__"}


def read(rel):
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as fh:
        return fh.read()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md has no YAML frontmatter"
    data, stack = {}, None
    for line in m.group(1).split("\n"):
        if not line.strip():
            continue
        if line.startswith("  ") and stack is not None:
            k, _, v = line.strip().partition(":")
            data[stack][k.strip()] = v.strip()
        else:
            k, _, v = line.partition(":")
            if v.strip() == "":
                data[k.strip()] = {}
                stack = k.strip()
            else:
                data[k.strip()] = v.strip()
                stack = None
    return data


def tracked_text_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXT or fn in ("LICENSE",):
                yield os.path.relpath(os.path.join(dirpath, fn), ROOT)


class TestSkill(unittest.TestCase):
    def setUp(self):
        self.skill = read("SKILL.md")
        self.fm = frontmatter(self.skill)

    def test_name_equals_repo(self):
        self.assertEqual(self.fm["name"], REPO)
        self.assertRegex(self.fm["name"], r"^[a-z0-9-]{1,64}$")

    def test_description_single_line_and_length(self):
        d = self.fm["description"]
        self.assertTrue(1 <= len(d) <= 1024, len(d))
        self.assertNotIn("\n", d)
        for phrase in ("plastic", "Use when", "Not for"):
            self.assertIn(phrase, d)

    def test_body_under_500_lines(self):
        self.assertLess(len(self.skill.split("\n")), 500)

    def test_no_host_specific_keys(self):
        self.assertNotIn("allowed-tools", self.skill.split("\n---\n")[0])

    def test_references_exist(self):
        for rel in re.findall(r"\(((?:references|scripts|examples)/[\w./-]+)\)", self.skill):
            self.assertTrue(os.path.exists(os.path.join(ROOT, rel)), rel)


class TestAdapters(unittest.TestCase):
    def test_plugin_json_matches_skill(self):
        fm = frontmatter(read("SKILL.md"))
        plugin = json.loads(read(".claude-plugin/plugin.json"))
        self.assertEqual(plugin["name"], fm["name"])
        self.assertEqual(plugin["version"], fm["metadata"]["version"])
        self.assertEqual(plugin["author"]["name"], "UniqAI")
        self.assertEqual(plugin["skills"], ["./"])

    def test_changelog_top_entry_matches_version(self):
        fm = frontmatter(read("SKILL.md"))
        m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", read("CHANGELOG.md"), re.M)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), fm["metadata"]["version"])

    def test_cursor_rule(self):
        rule = read(".cursor/rules/%s.mdc" % REPO)
        self.assertIn("@SKILL.md", rule)
        self.assertTrue(rule.startswith("---\ndescription:"))

    def test_agents_and_codex_mention_skill(self):
        self.assertIn("SKILL.md", read("AGENTS.md"))
        self.assertIn("SKILL.md", read("codex/INSTRUCTIONS.md"))

    def test_repo_json(self):
        meta = json.loads(read(".github/repo.json"))
        self.assertEqual(meta["name"], REPO)
        self.assertLessEqual(len(meta["topics"]), 20)
        self.assertIn("utm_campaign=" + REPO, meta["homepage"])


class TestHygiene(unittest.TestCase):
    def test_no_forbidden_strings(self):
        for rel in tracked_text_files():
            # this file lists the strings; .gitignore must name node_modules/ to exclude it
            if rel in ("tests" + os.sep + "test_adapters.py", ".gitignore"):
                continue
            text = read(rel)
            for line in text.split("\n"):
                if "conventions-allow: abs-path" in line:
                    continue
                low = line.lower()
                for bad in FORBIDDEN:
                    self.assertNotIn(bad.lower(), low, "%s contains %r" % (rel, bad))

    def test_copyright_lines_are_brand_only(self):
        for rel in tracked_text_files():
            if rel == "tests" + os.sep + "test_adapters.py":
                continue
            for line in read(rel).split("\n"):
                if "Copyright (c)" in line:
                    self.assertIn("UniqAI", line, rel)

    def test_readme_utm_and_footer(self):
        readme = read("README.md")
        links = re.findall(r"https://uniqai\.app[^\s)\"<>]*", readme)
        self.assertTrue(links)
        page_links = [u for u in links if not u.startswith("https://uniqai.app/examples/gen/")]
        for url in page_links:
            self.assertIn("utm_source=github", url)
            self.assertIn("utm_campaign=" + REPO, url)
        self.assertLessEqual(len(page_links), 3, "at most three UniqAI links per README")
        self.assertEqual(readme.count("Made by <a href="), 1, "exactly one Made by UniqAI footer")

    def test_required_files_exist(self):
        for rel in ("README.md", "SKILL.md", "AGENTS.md", "LICENSE", "CONTRIBUTING.md", "CHANGELOG.md",
                    ".gitignore", ".gitattributes", ".editorconfig", ".github/workflows/ci.yml",
                    ".github/ISSUE_TEMPLATE/bug_report.md", ".github/ISSUE_TEMPLATE/feature_request.md",
                    ".github/ISSUE_TEMPLATE/config.yml", ".github/PULL_REQUEST_TEMPLATE.md",
                    "assets/banner.svg", "assets/banner-light.svg", "assets/demo.svg", "assets/social-preview.png",
                    "assets/icon.svg", "examples/README.md", "references/checklist.md"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, rel)), rel)

    def test_no_large_binaries(self):
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                size = os.path.getsize(os.path.join(dirpath, fn))
                self.assertLess(size, 200 * 1024, "%s is %d bytes" % (fn, size))


if __name__ == "__main__":
    unittest.main()
