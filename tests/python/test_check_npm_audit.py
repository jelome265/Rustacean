"""Tests for tools/check_npm_audit.py. Pure-function tests; no network. Run from the repo root:
    python3 -m unittest discover -s tests/python -v
"""
import datetime
import importlib.util
import pathlib
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("check_npm_audit", REPO / "tools" / "check_npm_audit.py")
check_npm_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_npm_audit)

D = datetime.date


def advisory(name, severity, ghsa):
    return {
        "name": name,
        "severity": severity,
        "via": [{"source": 1, "name": name, "severity": severity,
                 "url": f"https://github.com/advisories/{ghsa}"}],
    }


def audit(*entries):
    return {"vulnerabilities": {e["name"]: {"name": e["name"], "severity": e["severity"],
                                            "via": e["via"]} for e in entries}}


def allowlist(expires="2026-12-31", review_by="2026-12-31", exceptions=None):
    if exceptions is None:
        exceptions = [{"ghsa": "GHSA-aaaa-bbbb-cccc", "package": "brace-expansion",
                       "severity": "high", "expires": expires, "reason": "test"}]
    return {"review_by": review_by, "exceptions": exceptions}


class CheckNpmAuditTest(unittest.TestCase):
    def test_accepted_exception_within_dates_passes(self):
        a = audit(advisory("brace-expansion", "high", "GHSA-aaaa-bbbb-cccc"))
        violations, stale = check_npm_audit.check(a, allowlist(), D(2026, 10, 15))
        self.assertEqual(violations, [])
        self.assertEqual(stale, [])

    def test_unlisted_high_advisory_fails(self):
        a = audit(advisory("undici", "high", "GHSA-zzzz-zzzz-zzzz"))
        violations, _ = check_npm_audit.check(a, allowlist(), D(2026, 10, 15))
        self.assertEqual(len(violations), 1)
        self.assertIn("undici high GHSA-zzzz-zzzz-zzzz is not an accepted exception", violations[0])

    def test_critical_advisory_is_blocking_too(self):
        a = audit(advisory("left-pad", "critical", "GHSA-crit-crit-crit"))
        violations, _ = check_npm_audit.check(a, allowlist(), D(2026, 10, 15))
        self.assertTrue(any("critical" in v for v in violations), violations)

    def test_moderate_advisory_does_not_block(self):
        a = audit(advisory("ip-address", "moderate", "GHSA-mod-mod-mod"))
        violations, _ = check_npm_audit.check(a, allowlist(), D(2026, 10, 15))
        self.assertEqual(violations, [])

    def test_expired_exception_fails(self):
        a = audit(advisory("brace-expansion", "high", "GHSA-aaaa-bbbb-cccc"))
        violations, _ = check_npm_audit.check(a, allowlist(), D(2027, 1, 5))
        self.assertTrue(any("exception expired on 2026-12-31" in v for v in violations), violations)

    def test_passed_review_date_fails_even_when_exceptions_are_current(self):
        a = audit(advisory("brace-expansion", "high", "GHSA-aaaa-bbbb-cccc"))
        violations, _ = check_npm_audit.check(a, allowlist(review_by="2026-12-31"), D(2027, 1, 5))
        self.assertTrue(any("review date" in v for v in violations), violations)

    def test_advisory_without_ghsa_identifier_fails(self):
        entry = {"name": "mystery", "severity": "high", "via": [{"severity": "high", "url": ""}]}
        violations, _ = check_npm_audit.check(audit(entry), allowlist(), D(2026, 10, 15))
        self.assertTrue(any("no GHSA identifier" in v for v in violations), violations)

    def test_exception_not_reported_by_audit_is_stale_but_not_fatal(self):
        violations, stale = check_npm_audit.check(audit(), allowlist(), D(2026, 10, 15))
        self.assertEqual(violations, [])
        self.assertEqual(len(stale), 1)

    def test_string_via_entries_are_ignored(self):
        entry = {"name": "parent", "severity": "high", "via": ["brace-expansion"]}
        violations, _ = check_npm_audit.check(audit(entry), allowlist(), D(2026, 10, 15))
        self.assertEqual(violations, [])

    def test_duplicate_advisories_are_reported_once(self):
        a = audit(advisory("undici", "high", "GHSA-dup-dup-dup"), advisory("undici", "high", "GHSA-dup-dup-dup"))
        found = list(check_npm_audit.blocking_advisories(a))
        self.assertEqual(len(found), 1)


if __name__ == "__main__":
    unittest.main()
