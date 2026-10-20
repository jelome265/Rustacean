"""Regression tests for release-please configuration. Run from the repository root:
python3 -m unittest discover -s tests/python -v
"""
import json
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "release-please-config.json").read_text(encoding="utf-8"))
PACKAGE = CONFIG["packages"]["."]


def workspace_crate_names():
    names = set()
    for manifest in (ROOT / "crates").glob("*/Cargo.toml"):
        names.add(tomllib.loads(manifest.read_text(encoding="utf-8"))["package"]["name"])
    return names


class ReleasePleaseConfig(unittest.TestCase):
    def test_every_extra_file_exists(self):
        for extra in PACKAGE["extra-files"]:
            self.assertTrue((ROOT / extra["path"]).is_file(), f"extra-file missing: {extra['path']}")

    def test_tags_are_bare_version_tags(self):
        # The publish job requires the tag to equal v<version>, so no component prefix.
        self.assertEqual(PACKAGE.get("component"), "")
        self.assertIs(PACKAGE.get("include-component-in-tag"), False)

    def test_release_type_is_node_so_package_json_is_updated(self):
        self.assertEqual(CONFIG["release-type"], "node")

    def test_cargo_lock_filter_targets_the_workspace_crate(self):
        lock_entries = [e for e in PACKAGE["extra-files"] if e["path"] == "Cargo.lock"]
        self.assertEqual(len(lock_entries), 1, "Cargo.lock must be listed exactly once")
        match = re.fullmatch(r"\$\.package\[\?\(@\.name\.value=='([^']+)'\)\]\.version", lock_entries[0]["jsonpath"])
        self.assertIsNotNone(match, "Cargo.lock jsonpath must use the parsed-name form")
        crate = match.group(1)
        self.assertIn(crate, workspace_crate_names(), "filter must name a workspace crate")
        lock = tomllib.loads((ROOT / "Cargo.lock").read_text(encoding="utf-8"))
        self.assertTrue(any(p["name"] == crate for p in lock["package"]), "crate must be present in Cargo.lock")

    def test_cargo_lock_matches_workspace_version(self):
        # release-please updates Cargo.lock on every release; the file must agree before the first one.
        version = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))["workspace"]["package"]["version"]
        lock = tomllib.loads((ROOT / "Cargo.lock").read_text(encoding="utf-8"))
        crate = next(e for e in PACKAGE["extra-files"] if e["path"] == "Cargo.lock")["jsonpath"]
        name = re.search(r"'([^']+)'", crate).group(1)
        entry = next(p for p in lock["package"] if p["name"] == name)
        self.assertEqual(entry["version"], version)


class ChangelogSource(unittest.TestCase):
    """release-please rewrites CHANGELOG.md. Its input must be one of two valid shapes:
    empty (before the first release), or the "# Changelog" title followed only by release
    sections. Any other text is carried into the next release and corrupts it. For example,
    a "# Changelog" title without a release heading is rewritten to "## Changelog".
    """

    VERSION = r"\d+\.\d+\.\d+(?:-\S+)?"
    RELEASE_HEADING = re.compile(
        rf"^## (?:{VERSION}|\[{VERSION}\]\([^)]+\)) \(\d{{4}}-\d{{2}}-\d{{2}}\)$"
    )

    def test_release_heading_accepts_plain_and_linked_formats(self):
        headings = (
            "## 0.1.0 (2026-10-15)",
            "## [0.2.0](https://example.invalid/compare/v0.1.0...v0.2.0) (2026-10-20)",
        )
        for heading in headings:
            with self.subTest(heading=heading):
                self.assertRegex(heading, self.RELEASE_HEADING)

    def test_changelog_is_empty_or_title_plus_release_sections(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        if not text.strip():
            return
        lines = text.splitlines()
        first = next(l for l in lines if l.strip())
        self.assertEqual(first, "# Changelog", "CHANGELOG.md must start with the '# Changelog' title")
        for line in lines:
            if line.startswith("## "):
                self.assertRegex(line, self.RELEASE_HEADING, f"unexpected level-2 heading: {line!r}")

    def test_no_stray_level_two_changelog_heading(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertNotIn("## Changelog", text.splitlines())


if __name__ == "__main__":
    unittest.main()
