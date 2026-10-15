"""Tests for tools/install_skills.py. Every test works in temporary directories and never
writes into the repository. Run from the repository root:
    python3 -m unittest discover -s tests/python -v
"""
import importlib.util
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
INSTALLER = REPO / "tools" / "install_skills.py"
SOURCE = REPO / "skills"
SUITE = [
    "rust-enterprise-best-practices",
    "rust-enterprise-implement",
    "rust-enterprise-harden",
    "rust-enterprise-audit",
    "rust-enterprise-frameworks",
]


def load_installer():
    spec = importlib.util.spec_from_file_location("install_skills", INSTALLER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstallSkillsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.source = self.root / "source"
        shutil.copytree(SOURCE, self.source, ignore=shutil.ignore_patterns("__pycache__", "INSTALLATION.md"))
        self.project = self.root / "project"
        self.project.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *args):
        proc = subprocess.run(
            [sys.executable, str(INSTALLER), "--source", str(self.source), *args],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout + proc.stderr

    def dest_for(self, relative):
        return self.project / relative

    def test_list_shows_agents_and_evidence(self):
        proc = subprocess.run([sys.executable, str(INSTALLER), "--list"], capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for agent in ("claude-code", "codex", "opencode", "gemini-cli", "antigravity", "cursor", "freebuff", "zcode"):
            self.assertIn(agent, proc.stdout)

    def test_dry_run_writes_nothing(self):
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project))
        self.assertEqual(code, 0, out)
        self.assertIn("DRY RUN", out)
        self.assertFalse(self.dest_for(".agents/skills").exists())

    def test_apply_installs_full_suite_and_verifies(self):
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project), "--apply")
        self.assertEqual(code, 0, out)
        self.assertIn("INSTALLED AND VERIFIED", out)
        dest = self.dest_for(".agents/skills")
        for name in SUITE:
            self.assertTrue((dest / name / "SKILL.md").is_file(), name)
        installer = load_installer()
        for name in SUITE:
            self.assertEqual(installer.tree_digest(dest / name), installer.tree_digest(self.source / name), name)

    def test_peer_links_resolve_after_install(self):
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project), "--apply")
        self.assertEqual(code, 0, out)
        installer = load_installer()
        self.assertEqual(installer.verify(self.source, self.dest_for(".agents/skills"), "copy"), [])

    def test_unknown_agent_is_usage_error(self):
        code, out = self.run_cli("--agent", "does-not-exist")
        self.assertEqual(code, 2, out)
        self.assertIn("unknown agent", out)

    def test_missing_agent_is_usage_error(self):
        code, out = self.run_cli()
        self.assertEqual(code, 2, out)

    def test_zcode_is_refused_without_explicit_acceptance_of_conflicting_docs(self):
        code, out = self.run_cli("--agent", "zcode", "--scope", "project",
                                 "--project-root", str(self.project), "--apply")
        self.assertEqual(code, 1, out)
        self.assertIn("conflicts", out)
        self.assertFalse((self.project / ".zcode").exists())

    def test_zcode_installs_when_conflict_is_explicitly_accepted(self):
        code, out = self.run_cli("--agent", "zcode", "--scope", "project", "--project-root", str(self.project),
                                 "--accept-conflicting", "--apply")
        self.assertEqual(code, 0, out)
        dest = self.project / ".zcode" / "skills"
        for name in SUITE:
            self.assertTrue((dest / name / "SKILL.md").is_file(), name)
        self.assertIn("INSTALLED AND VERIFIED", out)

    def test_zcode_registry_entry_is_graded_conflicting_not_official(self):
        installer = load_installer()
        self.assertEqual(installer.load_targets()["zcode"]["evidence"], "conflicting")

    def test_shared_official_paths_are_the_default_for_compatible_agents(self):
        installer = load_installer()
        targets = installer.load_targets()
        for agent in ("codex", "opencode", "gemini-cli", "zed", "cursor", "copilot", "kimi"):
            with self.subTest(agent=agent):
                self.assertEqual(targets[agent]["scope"]["project"][0], ".agents/skills")
                self.assertEqual(targets[agent]["scope"]["user"][0], ".agents/skills")
        self.assertEqual(targets["antigravity"]["scope"]["project"][0], ".agents/skills")
        self.assertEqual(targets["antigravity"]["scope"]["user"][0], ".gemini/config/skills")

    def test_conflicting_target_is_refused_without_explicit_acceptance(self):
        code, out = self.run_cli("--agent", "kimi", "--scope", "project", "--project-root", str(self.project), "--apply")
        self.assertEqual(code, 1, out)
        self.assertIn("conflicts", out)
        self.assertFalse((self.project / ".agents" / "skills").exists())

    def test_conflicting_target_installs_when_explicitly_accepted(self):
        code, out = self.run_cli("--agent", "kimi", "--scope", "project", "--project-root", str(self.project),
                                 "--accept-conflicting", "--apply")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.project / ".agents" / "skills" / SUITE[0] / "SKILL.md").is_file())

    def test_missing_skill_in_source_refuses_and_writes_nothing(self):
        shutil.rmtree(self.source / SUITE[2])
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project), "--apply")
        self.assertEqual(code, 1, out)
        self.assertIn("missing", out)
        self.assertFalse(self.dest_for(".agents/skills").exists())

    def test_differing_existing_copy_refuses_without_force(self):
        dest = self.dest_for(".agents/skills")
        shutil.copytree(self.source / SUITE[0], dest / SUITE[0])
        (dest / SUITE[0] / "SKILL.md").write_text("locally edited\n", encoding="utf-8")
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project), "--apply")
        self.assertEqual(code, 1, out)
        self.assertIn("re-run with --force", out)
        self.assertEqual((dest / SUITE[0] / "SKILL.md").read_text(encoding="utf-8"), "locally edited\n")
        self.assertFalse((dest / SUITE[1]).exists(), "a refused run must not write any sibling skill")

    def test_force_replaces_differing_copy(self):
        dest = self.dest_for(".agents/skills")
        shutil.copytree(self.source / SUITE[0], dest / SUITE[0])
        (dest / SUITE[0] / "SKILL.md").write_text("locally edited\n", encoding="utf-8")
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project),
                                 "--apply", "--force")
        self.assertEqual(code, 0, out)
        installer = load_installer()
        self.assertEqual(installer.tree_digest(dest / SUITE[0]), installer.tree_digest(self.source / SUITE[0]))

    def test_identical_existing_copy_is_left_unchanged(self):
        dest = self.dest_for(".agents/skills")
        shutil.copytree(self.source / SUITE[0], dest / SUITE[0])
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project),
                                 "--apply")
        self.assertEqual(code, 0, out)
        self.assertIn("unchanged", out)

    def test_symlink_mode_links_sources_and_verifies(self):
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project),
                                 "--mode", "symlink", "--apply")
        self.assertEqual(code, 0, out)
        link = self.dest_for(".agents/skills") / SUITE[0]
        self.assertTrue(link.is_symlink())

    def test_user_scope_resolves_under_home(self):
        code, out = self.run_cli("--agent", "claude-code", "--scope", "user", "--home", str(self.home), "--apply")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.home / ".claude" / "skills" / SUITE[4] / "SKILL.md").is_file())

    def test_explicit_destination_overrides_registry(self):
        dest = self.root / "custom-skills"
        code, out = self.run_cli("--agent", "codex", "--dest-dir", str(dest), "--apply")
        self.assertEqual(code, 0, out)
        self.assertTrue((dest / SUITE[0] / "SKILL.md").is_file())

    def test_verification_detects_tampering_after_install(self):
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project), "--apply")
        self.assertEqual(code, 0, out)
        dest = self.dest_for(".agents/skills")
        (dest / SUITE[1] / "SKILL.md").write_text("tampered\n", encoding="utf-8")
        installer = load_installer()
        failures = installer.verify(self.source, dest, "copy")
        self.assertTrue(any("differs from the source" in f for f in failures), failures)

    def test_verification_detects_a_peer_skill_missing_after_install(self):
        code, out = self.run_cli("--agent", "codex", "--scope", "project", "--project-root", str(self.project), "--apply")
        self.assertEqual(code, 0, out)
        dest = self.dest_for(".agents/skills")
        shutil.rmtree(dest / SUITE[0])
        installer = load_installer()
        failures = installer.verify(self.source, dest, "copy")
        self.assertTrue(any("is not installed beside it" in f for f in failures), failures)


if __name__ == "__main__":
    unittest.main()
