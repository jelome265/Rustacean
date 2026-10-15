import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import tools.check_release as cr

ROOT = Path(__file__).resolve().parents[2]


def make_repo(version="0.1.0", npm=None, plugin=None, changelog=None, cargo=None):
    d = Path(tempfile.mkdtemp(prefix="release-test-"))
    (d / "Cargo.toml").write_text(
        cargo if cargo is not None else f'[workspace]\nmembers = []\n\n[workspace.package]\nversion = "{version}"\n',
        encoding="utf-8")
    (d / "package.json").write_text(json.dumps({"name": "x", "version": npm or version}), encoding="utf-8")
    (d / ".claude-plugin").mkdir()
    (d / ".claude-plugin/plugin.json").write_text(json.dumps({"name": "x", "version": plugin or version}), encoding="utf-8")
    (d / "CHANGELOG.md").write_text(
        changelog if changelog is not None else
        "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-10-15\n\n### Added\n- thing\n",
        encoding="utf-8")
    return d


class VersionAgreement(unittest.TestCase):
    def test_all_sources_agree(self):
        self.assertEqual(cr.run(make_repo(), tag=None, require_release=True, base=None), "0.1.0")

    def test_package_json_mismatch_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, "disagree"):
            cr.run(make_repo(npm="0.2.0"), tag=None, require_release=False, base=None)

    def test_plugin_mismatch_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, "disagree"):
            cr.run(make_repo(plugin="0.1.1"), tag=None, require_release=False, base=None)

    def test_invalid_semver_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, "not valid SemVer"):
            cr.run(make_repo(version="1.0", npm="1.0", plugin="1.0"), tag=None, require_release=False, base=None)

    def test_missing_workspace_version_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, r"\[workspace.package\]"):
            cr.run(make_repo(cargo="[workspace]\nmembers = []\n"), tag=None, require_release=False, base=None)


class ChangelogFormat(unittest.TestCase):
    def test_missing_unreleased_fails(self):
        d = make_repo(changelog="# Changelog\n\n## [0.1.0] - 2026-10-15\n")
        with self.assertRaisesRegex(cr.ReleaseError, "no \\[Unreleased\\]"):
            cr.run(d, tag=None, require_release=False, base=None)

    def test_release_without_date_fails(self):
        d = make_repo(changelog="## [Unreleased]\n\n## [0.1.0]\n")
        with self.assertRaisesRegex(cr.ReleaseError, "has no date"):
            cr.run(d, tag=None, require_release=False, base=None)

    def test_bad_date_fails(self):
        d = make_repo(changelog="## [Unreleased]\n\n## [0.1.0] - 2026-13-40\n")
        with self.assertRaisesRegex(cr.ReleaseError, "invalid date"):
            cr.run(d, tag=None, require_release=False, base=None)

    def test_unreleased_with_date_fails(self):
        d = make_repo(changelog="## [Unreleased] - 2026-10-15\n")
        with self.assertRaisesRegex(cr.ReleaseError, "must not have a date"):
            cr.run(d, tag=None, require_release=False, base=None)

    def test_duplicate_version_fails(self):
        d = make_repo(changelog="## [Unreleased]\n\n## [0.1.0] - 2026-10-15\n\n## [0.1.0] - 2026-10-16\n")
        with self.assertRaisesRegex(cr.ReleaseError, "more than once"):
            cr.run(d, tag=None, require_release=False, base=None)

    def test_missing_changelog_fails(self):
        d = make_repo()
        (d / "CHANGELOG.md").unlink()
        with self.assertRaisesRegex(cr.ReleaseError, "missing"):
            cr.run(d, tag=None, require_release=False, base=None)


class ReleaseEntry(unittest.TestCase):
    def test_require_release_passes_with_dated_section(self):
        cr.run(make_repo(), tag=None, require_release=True, base=None)

    def test_require_release_fails_without_section(self):
        d = make_repo(changelog="## [Unreleased]\n\n## [0.0.9] - 2026-10-01\n")
        with self.assertRaisesRegex(cr.ReleaseError, "no dated section for \\[0.1.0\\]"):
            cr.run(d, tag=None, require_release=True, base=None)

    def test_tag_must_match_version(self):
        with self.assertRaisesRegex(cr.ReleaseError, "does not equal v0.1.0"):
            cr.run(make_repo(), tag="v0.1.1", require_release=False, base=None)

    def test_matching_tag_passes(self):
        cr.run(make_repo(), tag="v0.1.0", require_release=False, base=None)


class ChangelogTouched(unittest.TestCase):
    def _git_repo(self):
        d = make_repo()
        g = lambda *a: subprocess.run(["git", *a], cwd=d, check=True, capture_output=True, text=True)
        g("init", "-q")
        g("config", "user.email", "t@example.com")
        g("config", "user.name", "t")
        g("add", "-A")
        g("commit", "-q", "-m", "base")
        return d, g

    def test_release_relevant_change_without_changelog_fails(self):
        d, g = self._git_repo()
        g("checkout", "-q", "-b", "feature")
        (d / "skills").mkdir()
        (d / "skills/new.md").write_text("x", encoding="utf-8")
        g("add", "-A")
        g("commit", "-q", "-m", "feat")
        with self.assertRaisesRegex(cr.ReleaseError, "need a CHANGELOG.md entry"):
            cr.run(d, tag=None, require_release=False, base="HEAD~1")

    def test_release_relevant_change_with_changelog_passes(self):
        d, g = self._git_repo()
        g("checkout", "-q", "-b", "feature")
        (d / "skills").mkdir()
        (d / "skills/new.md").write_text("x", encoding="utf-8")
        (d / "CHANGELOG.md").write_text((d / "CHANGELOG.md").read_text() + "\n", encoding="utf-8")
        g("add", "-A")
        g("commit", "-q", "-m", "feat")
        cr.run(d, tag=None, require_release=False, base="HEAD~1")

    def test_docs_only_change_needs_no_changelog(self):
        d, g = self._git_repo()
        g("checkout", "-q", "-b", "docs")
        (d / "docs").mkdir()
        (d / "docs/notes.md").write_text("x", encoding="utf-8")
        g("add", "-A")
        g("commit", "-q", "-m", "docs")
        cr.run(d, tag=None, require_release=False, base="HEAD~1")


class VersionOrdering(unittest.TestCase):
    """Versions must increase. The release's own dated section is always present at release time."""

    def repo_with(self, version, released):
        sections = "".join(f"\n## [{v}] - {d}\n\n### Added\n- x\n" for v, d in released)
        return make_repo(version=version, changelog=f"# Changelog\n\n## [Unreleased]\n{sections}")

    def test_release_newer_than_prior_release_passes(self):
        d = self.repo_with("0.2.0", [("0.2.0", "2026-10-20"), ("0.1.0", "2026-10-15")])
        cr.run(d, tag=None, require_release=True, base=None)

    def test_release_not_newer_than_prior_release_fails(self):
        d = self.repo_with("0.1.0", [("0.1.0", "2026-10-20"), ("0.2.0", "2026-10-25")])
        with self.assertRaisesRegex(cr.ReleaseError, "never go backwards"):
            cr.run(d, tag=None, require_release=True, base=None)

    def test_release_with_only_its_own_section_passes_without_npm_data(self):
        d = self.repo_with("0.1.0", [("0.1.0", "2026-10-15")])
        cr.run(d, tag=None, require_release=True, base=None)

    def test_version_already_on_npm_fails(self):
        d = self.repo_with("0.1.0", [("0.1.0", "2026-10-15")])
        with self.assertRaisesRegex(cr.ReleaseError, "already on npm"):
            cr.run(d, tag=None, require_release=True, base=None, published="0.1.0")

    def test_version_older_than_npm_fails(self):
        d = self.repo_with("0.1.0", [("0.1.0", "2026-10-15")])
        with self.assertRaisesRegex(cr.ReleaseError, "already on npm"):
            cr.run(d, tag=None, require_release=True, base=None, published="0.2.0")

    def test_newer_than_npm_version_passes(self):
        d = self.repo_with("0.2.0", [("0.2.0", "2026-10-20")])
        cr.run(d, tag=None, require_release=True, base=None, published="0.1.0")

    def test_feature_pr_at_released_version_passes(self):
        d = self.repo_with("0.1.0", [("0.1.0", "2026-10-15")])
        cr.run(d, tag=None, require_release=False, base=None)

    def test_lower_than_newest_release_fails_on_every_run(self):
        d = self.repo_with("0.1.0", [("0.2.0", "2026-10-15")])
        with self.assertRaisesRegex(cr.ReleaseError, "never go backwards"):
            cr.run(d, tag=None, require_release=False, base=None)

    def test_prerelease_sorts_below_release(self):
        d = self.repo_with("1.0.0", [("1.0.0", "2026-10-20"), ("1.0.0-rc.1", "2026-10-01")])
        cr.run(d, tag=None, require_release=True, base=None)
        d2 = self.repo_with("1.0.0-rc.1", [("1.0.0-rc.1", "2026-10-20"), ("1.0.0", "2026-10-01")])
        with self.assertRaisesRegex(cr.ReleaseError, "never go backwards"):
            cr.run(d2, tag=None, require_release=True, base=None)

    def test_numeric_not_string_ordering(self):
        d = self.repo_with("0.10.0", [("0.10.0", "2026-10-20"), ("0.9.0", "2026-10-01")])
        cr.run(d, tag=None, require_release=True, base=None)

    def test_cli_published_flag(self):
        d = self.repo_with("0.1.0", [("0.1.0", "2026-10-15")])
        self.assertEqual(cr.main(["--root", str(d), "--require-release", "--published", "0.1.0"]), 1)
        self.assertEqual(cr.main(["--root", str(d), "--require-release", "--published", "0.0.9"]), 0)


class RealRepository(unittest.TestCase):
    def test_current_repository_passes_release_checks(self):
        cr.run(ROOT, tag=None, require_release=False, base=None)


if __name__ == "__main__":
    unittest.main()
