#!/usr/bin/env python3
"""Fail on high or critical npm advisories that are not accepted exceptions.

Input:
  --audit-json  output of `npm audit --package-lock-only --json` (exit code ignored here)
  --allowlist   tools/npm-publish/advisory-allowlist.json
  --today       optional YYYY-MM-DD; defaults to the current UTC date (tests pin it)

Rules (fail closed):
  1. A high or critical advisory with no matching exception fails the check.
  2. A matching exception whose `expires` date is before today fails the check.
  3. If `review_by` is before today, the check fails: the whole allow-list is stale.
  4. An exception that matches no current advisory is reported as stale but does not fail.

Exit codes: 0 pass, 1 policy violation, 2 usage or parse error.
"""
import argparse
import datetime
import json
import pathlib
import sys

BLOCKING = {"high", "critical"}


def load_json(path):
    try:
        with pathlib.Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"check_npm_audit: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(2)


def blocking_advisories(audit):
    """Yield (package, severity, ghsa) for each high or critical advisory in the audit."""
    seen = set()
    for package, entry in (audit.get("vulnerabilities") or {}).items():
        for via in entry.get("via", []):
            if not isinstance(via, dict):
                continue  # a string means the vulnerability comes through another package
            severity = via.get("severity") or entry.get("severity")
            if severity not in BLOCKING:
                continue
            url = via.get("url", "")
            ghsa = url.rsplit("/", 1)[-1] if "/advisories/" in url else ""
            name = entry.get("name") or package.rsplit("node_modules/", 1)[-1]
            key = (name, severity, ghsa)
            if key not in seen:
                seen.add(key)
                yield key


def check(audit, allowlist, today):
    """Return (violations, stale). Pure function so that tests can exercise every rule."""
    violations = []
    stale = []
    review_by = datetime.date.fromisoformat(allowlist["review_by"])
    if today > review_by:
        violations.append(f"allow-list review date {review_by} has passed; re-review every exception")

    exceptions = {(e["ghsa"], e["package"], e["severity"]): e for e in allowlist.get("exceptions", [])}
    matched = set()

    for name, severity, ghsa in blocking_advisories(audit):
        key = (ghsa, name, severity)
        if not ghsa:
            violations.append(f"{name} ({severity}) has no GHSA identifier; cannot be checked against the allow-list")
            continue
        exception = exceptions.get(key)
        if exception is None:
            violations.append(f"{name} {severity} {ghsa} is not an accepted exception")
            continue
        matched.add(key)
        expires = datetime.date.fromisoformat(exception["expires"])
        if today > expires:
            violations.append(f"{name} {ghsa} exception expired on {expires}")

    for key in exceptions:
        if key not in matched:
            stale.append(f"{key[1]} {key[0]} is listed but not reported by the audit")
    return violations, stale


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audit-json", required=True)
    parser.add_argument("--allowlist", required=True)
    parser.add_argument("--today")
    args = parser.parse_args(argv)

    audit = load_json(args.audit_json)
    allowlist = load_json(args.allowlist)
    try:
        today = datetime.date.fromisoformat(args.today) if args.today else datetime.datetime.now(datetime.timezone.utc).date()
    except ValueError:
        print("check_npm_audit: --today must be YYYY-MM-DD", file=sys.stderr)
        return 2

    violations, stale = check(audit, allowlist, today)
    for note in stale:
        print(f"note: {note}")
    if violations:
        print(f"NPM ADVISORY CHECK FAILED: {len(violations)} violation(s)")
        for violation in violations:
            print(f"  - {violation}")
        return 1
    print("NPM ADVISORY CHECK PASSED: every high or critical advisory is an unexpired, accepted exception.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
