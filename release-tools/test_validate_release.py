import json
import os
import tempfile
import unittest
from pathlib import Path

from validate_release import (
    EXPECTED_SKILLS,
    CAPABILITY_NAMES,
    check_fixtures,
    check_host_build,
    check_references,
    check_sensitive_content,
    check_symlinks,
    validate_release,
)


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "along"
FIXTURES = ROOT / "fixtures"


class ReleaseBundleTests(unittest.TestCase):
    def test_current_bundle_and_release_fixtures_pass(self):
        result = validate_release(
            PLUGIN,
            fixtures_root=FIXTURES,
            host_builds=[
                FIXTURES / "host-builds" / "codex-desktop.json",
                FIXTURES / "host-builds" / "claude-code-cli.json",
            ],
        )
        self.assertEqual(result["status"], "passed", result["issues"])
        self.assertEqual(set(result["checks"]["bundle"]["actual_skills"]), EXPECTED_SKILLS)
        self.assertEqual(result["checks"]["host_builds"]["build_count"], 2)
        self.assertEqual(result["checks"]["fixtures"]["observed_summary"]["matched_pairs"], 4)
        self.assertGreater(result["checks"]["references"]["relative_links_checked"], 0)
        self.assertGreater(result["checks"]["python_helpers"]["runs"][0]["tests_run"], 0)

    def test_fixture_cases_cover_real_duplicate_missing_pending_and_split_rows(self):
        result = check_fixtures(FIXTURES)
        self.assertEqual(result["status"], "passed", result["issues"])
        summary = result["observed_summary"]
        self.assertEqual(summary["bank_rows"], 6)
        self.assertEqual(summary["app_rows"], 7)
        self.assertEqual(summary["source_only"], 1)
        self.assertEqual(summary["app_unmatched"], 1)
        self.assertEqual(summary["pending_replacements"], 1)
        self.assertEqual(summary["split_children"], 2)


class ContainmentAndSecretTests(unittest.TestCase):
    def test_relative_reference_escape_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            root.mkdir()
            (root / "inside.md").write_text("[escape](../../outside.md)\n", encoding="utf-8")
            result = check_references(root)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("outside the bundle" in issue["message"] for issue in result["issues"]))

    def test_private_path_and_credential_like_value_are_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "bad.md").write_text(
                "path=/Users/example/private.json\napi_key=1234567890123456\n",
                encoding="utf-8",
            )
            result = check_sensitive_content(root)
            self.assertEqual(result["status"], "failed")
            self.assertEqual(len(result["issues"]), 2)

    def test_symlink_escape_is_reported_without_following_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "bundle"
            outside = Path(temp) / "outside.txt"
            root.mkdir()
            outside.write_text("synthetic", encoding="utf-8")
            os.symlink(outside, root / "escape.txt")
            result = check_symlinks(root)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("outside" in issue["message"] for issue in result["issues"]))


class HostBuildTests(unittest.TestCase):
    def test_host_build_requires_user_only_setup_and_all_capabilities(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad-host.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "host": "synthetic-host",
                        "setup": {"invocation": "setup", "user_only": False},
                        "runtime": {
                            name: {"status": "unknown", "tools": []}
                            for name in CAPABILITY_NAMES[:-1]
                        },
                    }
                ),
                encoding="utf-8",
            )
            result = check_host_build(path)
            self.assertEqual(result["status"], "failed")
            messages = {issue["message"] for issue in result["issues"]}
            self.assertIn("setup must be explicitly user-only", messages)
            self.assertTrue(any("capability record is missing" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
