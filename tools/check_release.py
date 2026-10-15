#!/usr/bin/env python3
"""Enforce the Rustacean versioning and changelog policy (see RELEASING.md).

Checks, in order:
  1. All version sources agree: Cargo.toml [workspace.package], package.json,
     and .claude-plugin/plugin.json.
  2. CHANGELOG.md is well formed: an [Unreleased] section, released sections
     with valid SemVer and ISO dates, no duplicate versions.
  3. --require-release: CHANGELOG.md has a dated section for the current version.
  4. --tag vX.Y.Z: the tag equals v<version>.
  5. --base <git-ref>: if release-relevant paths changed since <ref>, CHANGELOG.md
     must also change in the same range.
  6. Version ordering: the current version is never lower than the newest dated
     release in CHANGELOG.md. With --require-release it must be strictly newer
     than every earlier dated release, and with --published <v> strictly newer
     than the version already on npm.

Standard library only. Exit 0 on pass, 1 on any violation, 2 on usage error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
HEADING = re.compile(r"^## \[([^\]]+)\](?: - (\S+))?\s*$", re.MULTILINE)

# Paths whose changes are user-visible or release-relevant. Docs-only, CI-only,
# and test-only changes do not require a changelog entry.
RELEASE_RELEVANT = (
    "bin/",
    "tools/install_skills.py",
    "tools/validate_skills.py",
    "tools/agent_skill_targets.json",
    "tools/check_npm_audit.py",
    "skills/",
    "crates/",
    ".claude-plugin/",
    "package.json",
    "Cargo.toml",
)


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
    return {
        "Cargo.toml [workspace.package]": cargo_version,
        "package.json": npm["version"],
        ".claude-plugin/plugin.json": plugin["version"],
    }


def check_versions_agree(versions: dict[str, str]) -> str:
    distinct = set(versions.values())
    if len(distinct) != 1:
        detail = ", ".join(f"{src}={ver}" for src, ver in versions.items())
        raise ReleaseError(f"version sources disagree: {detail}")
    version = distinct.pop()
    if not SEMVER.match(version):
        raise ReleaseError(f"version {version!r} is not valid SemVer 2.0.0")
    return version


def parse_changelog(root: Path) -> dict[str, str | None]:
    """Return {heading_version: date_or_None}, in file order, after validation."""
    path = root / "CHANGELOG.md"
    if not path.is_file():
        raise ReleaseError("CHANGELOG.md is missing")
    text = path.read_text(encoding="utf-8")
    entries: dict[str, str | None] = {}
    for match in HEADING.finditer(text):
        label, date = match.group(1), match.group(2)
        if label == "Unreleased":
            if date is not None:
                raise ReleaseError("[Unreleased] must not have a date")
        else:
            if not SEMVER.match(label):
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
    if "Unreleased" not in entries:
        raise ReleaseError("CHANGELOG.md has no [Unreleased] section")
    return entries


def check_release_entry(entries: dict[str, str | None], version: str) -> None:
    if version not in entries or entries[version] is None:
        raise ReleaseError(
            f"CHANGELOG.md has no dated section for [{version}]; "
            "add it in the release commit (see RELEASING.md)"
        )


def version_key(version: str) -> tuple[int, int, int, int]:
    """Precedence key for SemVer core versions. A pre-release sorts below its release.

    Pre-release identifiers are not compared with full SemVer precedence rules;
    publish-time releases should therefore be plain X.Y.Z.
    """
    match = SEMVER.match(version)
    if match is None:
        raise ReleaseError(f"{version!r} is not valid SemVer")
    major, minor, patch = (int(match.group(i)) for i in (1, 2, 3))
    prerelease = "-" in version.split("+", 1)[0]
    return (major, minor, patch, 0 if prerelease else 1)


def check_not_behind(entries: dict[str, str | None], version: str) -> None:
    dated = [v for v, d in entries.items() if d is not None]
    if not dated:
        return
    newest = max(dated, key=version_key)
    if version_key(version) < version_key(newest):
        raise ReleaseError(
            f"version {version} is lower than the released version {newest}; versions never go backwards"
        )


def check_strictly_newer(entries: dict[str, str | None], version: str, published: str | None) -> None:
    prior = [v for v, d in entries.items() if d is not None and v != version]
    for old in prior:
        if version_key(version) <= version_key(old):
            raise ReleaseError(f"version {version} must be greater than released version {old}")
    if published is not None and version_key(version) <= version_key(published):
        raise ReleaseError(f"version {version} must be greater than {published}, which is already on npm")


def check_tag(tag: str, version: str) -> None:
    if tag != f"v{version}":
        raise ReleaseError(f"tag {tag!r} does not equal v{version}")


def changed_files(root: Path, base: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise ReleaseError(f"git diff against {base!r} failed: {result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line]


def check_changelog_touched(root: Path, base: str) -> None:
    files = changed_files(root, base)
    relevant = [f for f in files if f.startswith(RELEASE_RELEVANT)]
    if relevant and "CHANGELOG.md" not in files:
        sample = ", ".join(relevant[:5])
        raise ReleaseError(
            f"release-relevant changes ({sample}) need a CHANGELOG.md entry under [Unreleased]"
        )


def run(root: Path, *, tag: str | None, require_release: bool, base: str | None,
        published: str | None = None) -> str:
    version = check_versions_agree(read_versions(root))
    entries = parse_changelog(root)
    check_not_behind(entries, version)
    if require_release or tag is not None:
        check_release_entry(entries, version)
        check_strictly_newer(entries, version, published)
    if tag is not None:
        check_tag(tag, version)
    if base is not None:
        check_changelog_touched(root, base)
    return version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--tag", help="release tag being published, e.g. v0.1.0")
    parser.add_argument("--require-release", action="store_true",
                        help="require a dated CHANGELOG section for the current version")
    parser.add_argument("--base", help="git ref to diff against for the changelog-touched rule")
    parser.add_argument("--published", help="version currently on npm, if any; the release must be newer")
    args = parser.parse_args(argv)
    try:
        version = run(args.root, tag=args.tag, require_release=args.require_release,
                      base=args.base, published=args.published or None)
    except ReleaseError as exc:
        print(f"RELEASE CHECK FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"RELEASE CHECK PASSED: version {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
