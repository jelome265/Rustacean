#!/usr/bin/env python3
"""Require Conventional Commits subjects for every non-merge commit in base..HEAD.

release-please derives release versions and the changelog from these subjects,
so a malformed subject would silently change what gets released. This check runs
on pull requests, where a bad subject can still be fixed before merge.

Usage: check_commits.py --base <git-ref> [--root <path>]
Exit 0 when every subject conforms, 1 on any violation, 2 on usage error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TYPES = (
    "feat", "fix", "perf", "refactor", "docs", "test", "build", "ci",
    "chore", "style", "revert", "security",
)
SUBJECT = re.compile(
    rf"^({'|'.join(TYPES)})(\([a-z0-9][a-z0-9._/-]*\))?!?: \S.*$"
)


def commit_subjects(root: Path, base: str) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "log", "--no-merges", "--format=%H%x00%s", f"{base}..HEAD"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git log {base}..HEAD failed: {result.stderr.strip()}")
    pairs = []
    for line in result.stdout.splitlines():
        sha, _, subject = line.partition("\x00")
        pairs.append((sha[:12], subject))
    return pairs


def violations(pairs: list[tuple[str, str]]) -> list[str]:
    bad = []
    for sha, subject in pairs:
        if not SUBJECT.match(subject):
            bad.append(f"{sha} {subject!r}")
    return bad


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True, help="base ref, e.g. the pull request base SHA")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    try:
        pairs = commit_subjects(args.root, args.base)
    except RuntimeError as exc:
        print(f"COMMIT CHECK FAILED: {exc}", file=sys.stderr)
        return 1
    bad = violations(pairs)
    if bad:
        print("COMMIT CHECK FAILED: subjects must be Conventional Commits, for example "
              "'feat(frameworks): add rule' or 'fix: correct link':", file=sys.stderr)
        for line in bad:
            print(f"  {line}", file=sys.stderr)
        return 1
    print(f"COMMIT CHECK PASSED: {len(pairs)} commit(s) conform")
    return 0


if __name__ == "__main__":
    sys.exit(main())
