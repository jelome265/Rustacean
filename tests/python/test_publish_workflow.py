"""Regression tests for the publish path. npm trusted publishing validates the workflow
file that contains `npm publish`, so the publish must stay in release.yml and must not
use a reusable workflow or an npm token. Run from the repository root:
python3 -m unittest discover -s tests/python -v
"""
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def load(name):
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


class PublishPath(unittest.TestCase):
    def setUp(self):
        self.release = load("release.yml")
        self.publish = self.release["jobs"]["publish"]

    def test_publish_is_in_release_yml_not_a_reusable_workflow(self):
        # npm checks the calling workflow's filename, so the publish step must live in the
        # file the trusted publisher is configured for: release.yml.
        self.assertNotIn("uses", self.publish)
        self.assertFalse((WORKFLOWS / "publish-npm.yml").exists(),
                         "publish-npm.yml must not exist; the trusted publisher names release.yml")

    def test_publish_job_uses_the_npm_publish_environment(self):
        self.assertEqual(self.publish["environment"], "npm-publish")

    def test_publish_job_has_oidc_permission_and_nothing_broader(self):
        self.assertEqual(self.publish["permissions"], {"contents": "read", "id-token": "write"})

    def test_publish_runs_only_after_release_is_created(self):
        self.assertEqual(self.publish["needs"], "release-please")
        self.assertIn("release_created", self.publish["if"])

    def test_no_npm_token_is_used_anywhere_in_release_yml(self):
        text = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")
        self.assertNotIn("NODE_AUTH_TOKEN", text)
        self.assertNotIn("secrets.NPM_TOKEN", text)

    def test_publish_step_publishes_and_checks_policy(self):
        runs = [s.get("run", "") for s in self.publish["steps"]]
        self.assertTrue(any("npm publish --access public --provenance" in r for r in runs))
        self.assertTrue(any("tools/check_release.py" in r and "--tag" in r for r in runs))

    def test_release_please_job_keeps_its_own_permissions(self):
        job = self.release["jobs"]["release-please"]
        self.assertEqual(job["permissions"], {"contents": "write", "pull-requests": "write"})
        self.assertNotIn("id-token", job["permissions"])

    def test_top_level_permissions_are_empty(self):
        self.assertEqual(self.release["permissions"], {})


if __name__ == "__main__":
    unittest.main()
