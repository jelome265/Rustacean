"""Tests for skills/rust-enterprise-frameworks/scripts/check_frameworks.py.

Each rule is exercised with a seeded violation, and a compliant workspace must pass.
Run from the repository root:  python3 -m unittest discover -s tests/python -v
"""
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "skills" / "rust-enterprise-frameworks" / "scripts" / "check_frameworks.py"
POLICY = REPO / "skills" / "rust-enterprise-frameworks" / "references" / "frameworks-policy.toml"

COMPLIANT_PACKAGES = {
    "tokio": "1.53.2",
    "axum": "0.8.9",
    "axum-core": "0.5.6",
    "tower-http": "0.7.1",
    "hyper": "1.12.0",
    "serde": "1.0.229",
    "tracing-opentelemetry": "0.34.0",
    "opentelemetry": "0.33.1",
    "sqlx": "0.9.0",
}

COMPLIANT_MANIFEST = textwrap.dedent(
    """\
    [workspace]
    members = []

    [workspace.package]
    rust-version = "1.98.1"
    """
)


def lock_text(packages):
    chunks = ["version = 4\n"]
    for name, version in packages:
        chunks.append(f'\n[[package]]\nname = "{name}"\nversion = "{version}"\n')
    return "".join(chunks)


class FrameworkGateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.src = self.root / "src"
        self.src.mkdir()
        (self.src / "lib.rs").write_text("pub fn f() {}\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_gate(self, packages, manifest=COMPLIANT_MANIFEST):
        lock = self.root / "Cargo.lock"
        lock.write_text(lock_text(packages.items() if isinstance(packages, dict) else packages), encoding="utf-8")
        manifest_path = self.root / "Cargo.toml"
        manifest_path.write_text(manifest, encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--lock",
                str(lock),
                "--policy",
                str(POLICY),
                "--manifest",
                str(manifest_path),
                "--src-root",
                str(self.root),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout + proc.stderr

    def test_compliant_workspace_passes(self):
        code, out = self.run_gate(COMPLIANT_PACKAGES)
        self.assertEqual(code, 0, out)
        self.assertIn("FRAMEWORK GATE PASSED", out)

    def test_banned_crate_fails_fgate_01(self):
        packages = dict(COMPLIANT_PACKAGES, **{"actix-web": "4.16.0"})
        code, out = self.run_gate(packages)
        self.assertEqual(code, 1, out)
        self.assertIn("BANNED crate 'actix-web'", out)

    def test_transitive_legacy_hyper_fails(self):
        packages = [(k, v) for k, v in COMPLIANT_PACKAGES.items()] + [("hyper", "0.14.32")]
        code, out = self.run_gate(packages)
        self.assertEqual(code, 1, out)
        self.assertIn("'hyper' 0.14.32 is outside approved major 1", out)

    def test_duplicate_versions_fail_fgate_03(self):
        packages = [(k, v) for k, v in COMPLIANT_PACKAGES.items()] + [("tokio", "1.60.0")]
        code, out = self.run_gate(packages)
        self.assertEqual(code, 1, out)
        self.assertIn("DUPLICATE 'tokio'", out)

    def test_below_floor_fails_fgate_02(self):
        packages = dict(COMPLIANT_PACKAGES, tokio="1.40.0")
        code, out = self.run_gate(packages)
        self.assertEqual(code, 1, out)
        self.assertIn("below the policy floor 1.53.2", out)

    def test_prerelease_version_is_rejected(self):
        packages = dict(COMPLIANT_PACKAGES, **{"tower-http": "0.7.1-rc.1"})
        code, out = self.run_gate(packages)
        self.assertEqual(code, 1, out)
        self.assertIn("unparseable or pre-release version", out)

    def test_repo_msrv_below_framework_floor_fails_fgate_04(self):
        manifest = COMPLIANT_MANIFEST.replace('"1.98.1"', '"1.90"')
        code, out = self.run_gate(COMPLIANT_PACKAGES, manifest=manifest)
        self.assertEqual(code, 1, out)
        self.assertIn("below the framework floor 1.94.0", out)

    def test_missing_rust_version_fails(self):
        manifest = "[workspace]\nmembers = []\n"
        code, out = self.run_gate(COMPLIANT_PACKAGES, manifest=manifest)
        self.assertEqual(code, 1, out)
        self.assertIn("rust-version is not declared", out)

    def test_sqlx_macros_without_offline_cache_fail_fgate_05(self):
        (self.src / "db.rs").write_text(
            'pub async fn f(p: &sqlx::PgPool) { let _ = sqlx::query_scalar!("select 1").fetch_one(p); }\n',
            encoding="utf-8",
        )
        code, out = self.run_gate(COMPLIANT_PACKAGES)
        self.assertEqual(code, 1, out)
        self.assertIn("no offline cache", out)

    def test_sqlx_macros_with_offline_cache_pass(self):
        (self.src / "db.rs").write_text(
            'pub async fn f(p: &sqlx::PgPool) { let _ = sqlx::query_scalar!("select 1"); }\n',
            encoding="utf-8",
        )
        cache = self.root / ".sqlx"
        cache.mkdir()
        (cache / "query-abc.json").write_text('{"query":"select 1"}', encoding="utf-8")
        code, out = self.run_gate(COMPLIANT_PACKAGES)
        self.assertEqual(code, 0, out)

    def test_missing_lockfile_is_a_usage_error_not_a_pass(self):
        manifest_path = self.root / "Cargo.toml"
        manifest_path.write_text(COMPLIANT_MANIFEST, encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--lock",
                str(self.root / "missing.lock"),
                "--policy",
                str(POLICY),
                "--manifest",
                str(manifest_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)


if __name__ == "__main__":
    unittest.main()
