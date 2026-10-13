"""Tests for tools/validate_skills.py.

The repository's own skills must pass. Each defect class must be detected in a temporary
package. Run from the repository root:  python3 -m unittest discover -s tests/python -v
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
VALIDATOR = REPO / "tools" / "validate_skills.py"

GOOD_SKILL = """---
name: {name}
description: A valid test skill for the validator. It triggers on test requests.
---

# {name}

- **TST-01 (BLOCKER).** A defined rule.

See `references/notes.md` for detail. Cites TST-01.
"""


class ValidateSkillsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write_skill(self, folder, text, extra=None):
        skill_dir = self.root / folder
        (skill_dir / "references").mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
        (skill_dir / "references" / "notes.md").write_text("notes\n", encoding="utf-8")
        for rel, body in (extra or {}).items():
            (skill_dir / rel).parent.mkdir(parents=True, exist_ok=True)
            (skill_dir / rel).write_text(body, encoding="utf-8")

    def validate(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout + proc.stderr

    def test_repository_skills_pass(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), str(REPO / "skills")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("VALIDATION PASSED", proc.stdout)

    def test_valid_package_passes(self):
        self.write_skill("alpha", GOOD_SKILL.format(name="alpha"))
        code, out = self.validate()
        self.assertEqual(code, 0, out)

    def test_missing_frontmatter_fails(self):
        self.write_skill("alpha", "# no frontmatter\n")
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn("missing frontmatter", out)

    def test_colon_space_in_description_breaks_yaml(self):
        text = GOOD_SKILL.format(name="alpha").replace(
            "A valid test skill for the validator.", "A valid test skill: broken yaml."
        )
        self.write_skill("alpha", text)
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn("frontmatter does not parse", out)

    def test_name_must_equal_folder(self):
        self.write_skill("alpha", GOOD_SKILL.format(name="beta"))
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn("does not equal folder", out)

    def test_description_over_limit_fails(self):
        long_desc = "x" * 1025
        text = f"---\nname: alpha\ndescription: {long_desc}\n---\n\n- **TST-01 (BLOCKER).** rule\n"
        self.write_skill("alpha", text)
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn("description length 1025", out)

    def test_missing_referenced_file_fails(self):
        text = GOOD_SKILL.format(name="alpha").replace("references/notes.md", "references/missing.md")
        self.write_skill("alpha", text)
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn("referenced file does not exist: references/missing.md", out)

    def test_undefined_rule_id_fails(self):
        text = GOOD_SKILL.format(name="alpha") + "\nAlso cites BP-XX-99 which is undefined.\n"
        self.write_skill("alpha", text)
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn("'BP-XX-99' is cited but never defined", out)


if __name__ == "__main__":
    unittest.main()
