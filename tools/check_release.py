#!/usr/bin/env python3
"""Verify release metadata for Rustacean (see RELEASING.md).

Versions are not edited by hand. release-please computes the next version from
conventional commits and updates every source listed below in its release pull
request. This checker verifies that the result is consistent:

  1. Version sources agree: Cargo.toml [workspace.package], package.json,
     .claude-plugin/plugin.json, and .release-please-manifest.json.
  2. The version is valid SemVer and never lower than the newest dated release
     in CHANGELOG.md.
  3. --require-release: CHANGELOG.md has a dated section for the current version,
     and the version is strictly newer than every earlier dated release.
  4. --published <v>: the version is strictly newer than the version on npm.
  5. --tag vX.Y.Z: the tag equals v<version>.

Standard library only. Exit 0 on pass, 1 on violation, 2 on usage error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tomllib
from pathlib import Path

SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
# release-please writes "## 0.2.0 (2026-10-20)" (the dry run shows this form), and a
# linked form "## [0.2.0](compare-url) (2026-10-20)" when configured. The Keep a Changelog
# form "## [0.2.0] - 2026-10-20" is also accepted. "## [Unreleased]" is optional.
HEADING_PLAIN = re.compile(r"^## ([0-9][^\s\[\]()]*) \((\d{4}-\d{2}-\d{2})\)\s*$")
HEADING_LINKED = re.compile(r"^## \[([^\]]+)\]\([^)]*\) \((\d{4}-\d{2}-\d{2})\)\s*$")
HEADING_KAC = re.compile(r"^## \[([^\]]+)\](?: - (\S+))?\s*$")


class ReleaseError(Exception):
    pass


def read_versions(root: Path) -> dict[str, str]:
    cargo = tomllib.loads((root / "Cargo.toml").read_text(encoding="utf-8"))
    try:
        cargo_version = cargo["workspace"]["package"]["version"]
    except KeyError as exc:
        raise ReleaseError("Cargo.toml has no [workspace.package] version") from exc
    npm = json.loads((root / "package.json").read_text(encoding="utf-8"))
    plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / ".release-please-manifest.json").read_text(encoding="utf-8"))
    return {
        "Cargo.toml [workspace.package]": cargo_version,
        "package.json": npm["version"],
        ".claude-plugin/plugin.json": plugin["version"],
        ".release-please-manifest.json": manifest["."],
    }


def check_versions_agree(versions: dict[str, str]) -> str:
    if len(set(versions.values())) != 1:
        detail = ", ".join(f"{src}={ver}" for src, ver in versions.items())
        raise ReleaseError(f"version sources disagree: {detail}")
    version = next(iter(versions.values()))
    if SEMVER.match(version) is None:
        raise ReleaseError(f"version {version!r} is not valid SemVer 2.0.0")
    return version


def version_key(version: str) -> tuple[int, int, int, int]:
    """Precedence for SemVer core numbers. A pre-release sorts below its release.

    Pre-release identifiers are not compared with full SemVer precedence rules.
    """
    match = SEMVER.match(version)
    if match is None:
        raise ReleaseError(f"{version!r} is not valid SemVer")
    major, minor, patch = (int(match.group(i)) for i in (1, 2, 3))
    prerelease = "-" in version.split("+", 1)[0]
    return (major, minor, patch, 0 if prerelease else 1)


def _parse_heading(line: str) -> tuple[str, str | None] | None:
    if not line.startswith("## "):
        return None
    for pattern in (HEADING_PLAIN, HEADING_LINKED, HEADING_KAC):
        match = pattern.match(line)
        if match is not None:
            label = match.group(1)
            date = match.group(2) if match.re.groups >= 2 else None
            return label, date
    raise ReleaseError(f"unrecognised changelog heading: {line!r}")


def parse_changelog(root: Path) -> dict[str, str | None]:
    """Return {version: date_or_None}. [Unreleased] maps to None and is optional."""
    path = root / "CHANGELOG.md"
    if not path.is_file():
        raise ReleaseError("CHANGELOG.md is missing")
    entries: dict[str, str | None] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_heading(line)
        if parsed is None:
            continue
        label, date = parsed
        if label == "Unreleased":
            if date is not None:
                raise ReleaseError("[Unreleased] must not have a date")
        else:
            if SEMVER.match(label) is None:
                raise ReleaseError(f"changelog heading [{label}] is not valid SemVer")
            if date is None:
                raise ReleaseError(f"changelog release [{label}] has no date")
            try:
                dt.date.fromisoformat(date)
            except ValueError as exc:
                raise ReleaseError(f"changelog release [{label}] has invalid date {date!r}") from exc
        if label in entries:
            raise ReleaseError(f"changelog heading [{label}] appears more than once")
        entries[label] = date
    return entries


def check_not_behind(entries: dict[str, str | None], version: str) -> None:
    dated = [v for v, d in entries.items() if d is not None]
    if dated and version_key(version) < version_key(max(dated, key=version_key)):
        newest = max(dated, key=version_key)
        raise ReleaseError(
            f"version {version} is lower than the released version {newest}; versions never go backwards"
        )


def check_release_entry(entries: dict[str, str | None], version: str) -> None:
    if entries.get(version) is None:
        raise ReleaseError(
            f"CHANGELOG.md has no dated section for [{version}]; "
            "the release-please release pull request writes it"
        )


def check_strictly_newer(entries: dict[str, str | None], version: str, published: str | None) -> None:
    for old, date in entries.items():
        if date is not None and old != version and version_key(version) <= version_key(old):
            raise ReleaseError(f"version {version} must be greater than released version {old}")
    if published is not None and version_key(version) <= version_key(published):
        raise ReleaseError(f"version {version} must be greater than {published}, which is already on npm")


def check_tag(tag: str, version: str) -> None:
    if tag != f"v{version}":
        raise ReleaseError(f"tag {tag!r} does not equal v{version}")


def run(root: Path, *, tag: str | None, require_release: bool, published: str | None = None) -> str:
    version = check_versions_agree(read_versions(root))
    entries = parse_changelog(root)
    check_not_behind(entries, version)
    if require_release or tag is not None:
        check_release_entry(entries, version)
        check_strictly_newer(entries, version, published)
    if tag is not None:
        check_tag(tag, version)
    return version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--tag", help="release tag being published, e.g. v0.1.0")
    parser.add_argument("--require-release", action="store_true",
                        help="require a dated CHANGELOG section for the current version")
    parser.add_argument("--published", help="version currently on npm, if any; the release must be newer")
    args = parser.parse_args(argv)
    try:
        version = run(args.root, tag=args.tag, require_release=args.require_release,
                      published=args.published or None)
    except ReleaseError as exc:
        print(f"RELEASE CHECK FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"RELEASE CHECK PASSED: version {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
