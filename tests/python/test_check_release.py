"""Tests for tools/check_release.py (release-please era). Run from the repository root:
python3 -m unittest discover -s tests/python -v
"""
import json
import tempfile
import unittest
from pathlib import Path

import tools.check_release as cr

ROOT = Path(__file__).resolve().parents[2]


def make_repo(version="0.1.0", npm=None, plugin=None, manifest=None, changelog=None, cargo=None):
    d = Path(tempfile.mkdtemp(prefix="release-test-"))
    (d / "Cargo.toml").write_text(
        cargo if cargo is not None else f'[workspace]\nmembers = []\n\n[workspace.package]\nversion = "{version}"\n',
        encoding="utf-8")
    (d / "package.json").write_text(json.dumps({"name": "x", "version": npm or version}), encoding="utf-8")
    (d / ".claude-plugin").mkdir()
    (d / ".claude-plugin/plugin.json").write_text(json.dumps({"name": "x", "version": plugin or version}), encoding="utf-8")
    (d / ".release-please-manifest.json").write_text(json.dumps({".": manifest or version}), encoding="utf-8")
    (d / "CHANGELOG.md").write_text(changelog if changelog is not None else "# Changelog\n", encoding="utf-8")
    return d


def with_releases(version, releases):
    """releases: list of (version, date) written in release-please's heading format."""
    body = "".join(
        f"\n## [{v}](https://github.com/x/y/compare/v0.0.0...v{v}) ({d})\n\n### Features\n\n* thing\n"
        for v, d in releases
    )
    return make_repo(version=version, changelog="# Changelog\n" + body)


class VersionSources(unittest.TestCase):
    def test_all_four_sources_agree(self):
        self.assertEqual(cr.run(make_repo(), tag=None, require_release=False), "0.1.0")

    def test_manifest_mismatch_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, "disagree"):
            cr.run(make_repo(manifest="0.2.0"), tag=None, require_release=False)

    def test_package_json_mismatch_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, "disagree"):
            cr.run(make_repo(npm="0.2.0"), tag=None, require_release=False)

    def test_plugin_mismatch_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, "disagree"):
            cr.run(make_repo(plugin="0.1.1"), tag=None, require_release=False)

    def test_invalid_semver_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, "not valid SemVer"):
            cr.run(make_repo(version="1.0", npm="1.0", plugin="1.0", manifest="1.0"), tag=None, require_release=False)

    def test_missing_workspace_version_fails(self):
        with self.assertRaisesRegex(cr.ReleaseError, r"\[workspace.package\]"):
            cr.run(make_repo(cargo="[workspace]\nmembers = []\n"), tag=None, require_release=False)


class ChangelogFormat(unittest.TestCase):
    def test_empty_changelog_is_valid_before_first_release(self):
        cr.run(make_repo(version="0.0.0"), tag=None, require_release=False)

    def test_release_please_heading_is_parsed(self):
        d = with_releases("0.2.0", [("0.2.0", "2026-10-20"), ("0.1.0", "2026-10-15")])
        self.assertEqual(cr.parse_changelog(d), {"0.2.0": "2026-10-20", "0.1.0": "2026-10-15"})

    def test_keep_a_changelog_heading_is_parsed(self):
        d = make_repo(changelog="## [Unreleased]\n\n## [0.1.0] - 2026-10-15\n")
        self.assertEqual(cr.parse_changelog(d), {"Unreleased": None, "0.1.0": "2026-10-15"})

    def test_release_without_date_fails(self):
        d = make_repo(changelog="## [0.1.0]\n")
        with self.assertRaisesRegex(cr.ReleaseError, "has no date"):
            cr.run(d, tag=None, require_release=False)

    def test_bad_date_fails(self):
        d = make_repo(changelog="## [0.1.0] - 2026-13-40\n")
        with self.assertRaisesRegex(cr.ReleaseError, "invalid date"):
            cr.run(d, tag=None, require_release=False)

    def test_unrecognised_heading_fails(self):
        d = make_repo(changelog="## [0.1.0] released sometime\n")
        with self.assertRaisesRegex(cr.ReleaseError, "unrecognised"):
            cr.run(d, tag=None, require_release=False)

    def test_duplicate_version_fails(self):
        d = make_repo(changelog="## [0.1.0] - 2026-10-15\n\n## [0.1.0] - 2026-10-16\n")
        with self.assertRaisesRegex(cr.ReleaseError, "more than once"):
            cr.run(d, tag=None, require_release=False)

    def test_missing_changelog_fails(self):
        d = make_repo()
        (d / "CHANGELOG.md").unlink()
        with self.assertRaisesRegex(cr.ReleaseError, "missing"):
            cr.run(d, tag=None, require_release=False)


class VersionOrdering(unittest.TestCase):
    def test_release_newer_than_prior_passes(self):
        d = with_releases("0.2.0", [("0.2.0", "2026-10-20"), ("0.1.0", "2026-10-15")])
        cr.run(d, tag=None, require_release=True)

    def test_release_older_than_prior_fails(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-20"), ("0.2.0", "2026-10-25")])
        with self.assertRaisesRegex(cr.ReleaseError, "never go backwards"):
            cr.run(d, tag=None, require_release=False)

    def test_release_needs_its_own_dated_section(self):
        d = with_releases("0.2.0", [("0.1.0", "2026-10-15")])
        with self.assertRaisesRegex(cr.ReleaseError, "no dated section for \\[0.2.0\\]"):
            cr.run(d, tag=None, require_release=True)

    def test_version_already_on_npm_fails(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        with self.assertRaisesRegex(cr.ReleaseError, "already on npm"):
            cr.run(d, tag=None, require_release=True, published="0.1.0")

    def test_version_older_than_npm_fails(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        with self.assertRaisesRegex(cr.ReleaseError, "already on npm"):
            cr.run(d, tag=None, require_release=True, published="0.2.0")

    def test_newer_than_npm_passes(self):
        d = with_releases("0.2.0", [("0.2.0", "2026-10-20")])
        cr.run(d, tag=None, require_release=True, published="0.1.0")

    def test_first_release_passes_without_npm_data(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        cr.run(d, tag=None, require_release=True, published=None)

    def test_feature_change_at_released_version_passes(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        cr.run(d, tag=None, require_release=False)

    def test_prerelease_sorts_below_release(self):
        d = with_releases("1.0.0", [("1.0.0", "2026-10-20"), ("1.0.0-rc.1", "2026-10-01")])
        cr.run(d, tag=None, require_release=True)
        d2 = with_releases("1.0.0-rc.1", [("1.0.0-rc.1", "2026-10-20"), ("1.0.0", "2026-10-01")])
        with self.assertRaisesRegex(cr.ReleaseError, "never go backwards"):
            cr.run(d2, tag=None, require_release=True)

    def test_numeric_not_string_ordering(self):
        d = with_releases("0.10.0", [("0.10.0", "2026-10-20"), ("0.9.0", "2026-10-01")])
        cr.run(d, tag=None, require_release=True)


class Tags(unittest.TestCase):
    def test_tag_must_equal_version(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        with self.assertRaisesRegex(cr.ReleaseError, "does not equal v0.1.0"):
            cr.run(d, tag="v0.1.1", require_release=True)

    def test_matching_tag_passes(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        cr.run(d, tag="v0.1.0", require_release=True)


class CommandLine(unittest.TestCase):
    def test_published_flag_fails_when_not_newer(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        self.assertEqual(cr.main(["--root", str(d), "--require-release", "--published", "0.1.0"]), 1)

    def test_published_flag_passes_when_older(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        self.assertEqual(cr.main(["--root", str(d), "--require-release", "--published", "0.0.9"]), 0)

    def test_tag_flag_rejects_mismatch(self):
        d = with_releases("0.1.0", [("0.1.0", "2026-10-15")])
        self.assertEqual(cr.main(["--root", str(d), "--require-release", "--tag", "v0.1.1"]), 1)


class RealRepository(unittest.TestCase):
    def test_current_repository_passes(self):
        cr.run(ROOT, tag=None, require_release=False)


if __name__ == "__main__":
    unittest.main()
