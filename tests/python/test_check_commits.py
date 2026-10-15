"""Tests for tools/check_commits.py. Run from the repository root:
python3 -m unittest discover -s tests/python -v
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

import tools.check_commits as cc


class SubjectPattern(unittest.TestCase):
    def test_accepts_conventional_subjects(self):
        good = [
            "feat(frameworks): add rule",
            "fix: correct link",
            "security(npm): record exceptions",
            "ci(publish): explain id-token",
            "feat!: remove the --dest-dir flag",
            "docs: update installer guide",
            'revert: "feat: add thing"',
        ]
        self.assertEqual(cc.violations([(str(i), s) for i, s in enumerate(good)]), [])

    def test_rejects_non_conventional_subjects(self):
        bad = ["release: enforce policy", "fix:", "Feat: capital type", "add a thing", "feat(): empty scope", "chore(): x"]
        flagged = cc.violations([(str(i), s) for i, s in enumerate(bad)])
        self.assertEqual(len(flagged), len(bad))

    def test_rejects_type_without_space(self):
        self.assertEqual(len(cc.violations([("a", "feat:nospace")])), 1)


class AgainstGit(unittest.TestCase):
    def _repo(self, subjects):
        d = Path(tempfile.mkdtemp(prefix="commit-test-"))
        run = lambda *a: subprocess.run(["git", *a], cwd=d, check=True, capture_output=True, text=True)
        run("init", "-q")
        run("config", "user.email", "t@example.com")
        run("config", "user.name", "t")
        (d / "f").write_text("0", encoding="utf-8")
        run("add", "-A")
        run("commit", "-q", "-m", "chore: base")
        base = run("rev-parse", "HEAD").stdout.strip()
        for i, subject in enumerate(subjects):
            (d / "f").write_text(str(i + 1), encoding="utf-8")
            run("commit", "-q", "-am", subject)
        return d, base

    def test_checks_every_commit_in_range(self):
        d, base = self._repo(["feat: ok", "wip stuff"])
        self.assertEqual(cc.main(["--root", str(d), "--base", base]), 1)

    def test_passes_when_all_commits_conform(self):
        d, base = self._repo(["feat: one", "fix(ci): two"])
        self.assertEqual(cc.main(["--root", str(d), "--base", base]), 0)

    def test_unknown_base_is_reported_not_passed(self):
        d, _ = self._repo(["feat: one"])
        self.assertEqual(cc.main(["--root", str(d), "--base", "0000000000000000000000000000000000000000"]), 1)


if __name__ == "__main__":
    unittest.main()
