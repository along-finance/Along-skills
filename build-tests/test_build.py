from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "plugins" / "along"
SPEC = importlib.util.spec_from_file_location("along_build", HERE / "build.py")
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class BuildTests(unittest.TestCase):
    def test_default_output_is_local_to_builder(self) -> None:
        self.assertEqual(BUILD._default_output(), HERE / "dist")

    def _assert_archive_safe(self, archive: zipfile.ZipFile) -> None:
        names = archive.namelist()
        self.assertTrue(names)
        self.assertEqual(names, sorted(names))
        for name in names:
            path = PurePosixPath(name)
            self.assertTrue(name.startswith("along/"), name)
            self.assertFalse(path.is_absolute(), name)
            self.assertNotIn("..", path.parts, name)
            self.assertNotIn("__pycache__", path.parts, name)
            self.assertFalse(name.endswith(".pyc"), name)
            data = archive.read(name)
            self.assertNotIn(b"/Users/", data, name)
            self.assertNotIn(b"/home/", data, name)
            self.assertNotIn(b"\\Users\\", data, name)

    def _skill_entries(self, archive: zipfile.ZipFile, prefix: str = "along/skills/") -> set[str]:
        return {
            name[len(prefix) :].split("/", 1)[0]
            for name in archive.namelist()
            if name.startswith(prefix) and name.endswith("/SKILL.md")
        }

    def test_builds_both_host_archives_with_expected_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "release"
            result = BUILD.build_release(SOURCE, output)
            self.assertEqual(set(result), {"codex", "claude"})
            expected_skills = set(BUILD.SKILL_NAMES)
            for host, (zip_path, checksum_path) in result.items():
                self.assertEqual(zip_path.parent, (output / host).resolve())
                self.assertTrue(zip_path.is_file())
                self.assertTrue(checksum_path.is_file())
                with zipfile.ZipFile(zip_path) as archive:
                    self._assert_archive_safe(archive)
                    prefix = "along/plugins/along/skills/" if host == "codex" else "along/skills/"
                    self.assertEqual(self._skill_entries(archive, prefix), expected_skills)
                    self.assertTrue(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist()))
                    self.assertTrue(all(name.startswith("along/") for name in archive.namelist()))
                digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
                self.assertEqual(checksum_path.read_text(), f"{digest}  {zip_path.name}\n")

            codex_zip = result["codex"][0]
            with zipfile.ZipFile(codex_zip) as archive:
                self.assertIn("along/.agents/plugins/marketplace.json", archive.namelist())
                self.assertIn("along/plugins/along/.codex-plugin/plugin.json", archive.namelist())
                self.assertNotIn("along/.codex-plugin/plugin.json", archive.namelist())
                self.assertNotIn("along/.claude-plugin/plugin.json", archive.namelist())
                marketplace = json.loads(archive.read("along/.agents/plugins/marketplace.json"))
                self.assertEqual(marketplace["name"], "along")
                self.assertEqual(marketplace["plugins"][0]["name"], "along")
                self.assertEqual(marketplace["plugins"][0]["source"], {"source": "local", "path": "./plugins/along"})
                setup_metadata = archive.read("along/plugins/along/skills/along-setup/agents/openai.yaml").decode()
                self.assertIn("allow_implicit_invocation: false", setup_metadata)
                self.assertTrue(any(name.endswith("/agents/openai.yaml") for name in archive.namelist()))

            claude_zip = result["claude"][0]
            with zipfile.ZipFile(claude_zip) as archive:
                self.assertIn("along/.claude-plugin/plugin.json", archive.namelist())
                self.assertNotIn("along/.codex-plugin/plugin.json", archive.namelist())
                self.assertNotIn("along/.agents/plugins/marketplace.json", archive.namelist())
                self.assertNotIn("along/plugins/along/.codex-plugin/plugin.json", archive.namelist())
                self.assertFalse(any("/agents/" in name for name in archive.namelist()))
                metadata = json.loads(archive.read("along/.claude-plugin/plugin.json"))
                self.assertEqual(metadata["name"], "along")
                self.assertEqual(metadata["version"], "0.1.0")
                self.assertEqual(metadata["author"], {"name": "Along contributors"})
                self.assertEqual(metadata["license"], "MIT")
                self.assertEqual(metadata["skills"], "./skills/")
                setup = archive.read("along/skills/along-setup/SKILL.md").decode()
                self.assertIn("disable-model-invocation: true", setup)
                adapter = archive.read("along/HOST-ADAPTER.md").decode()
                self.assertIn("Claude Desktop", adapter)
                self.assertIn("upload", adapter)
                self.assertIn("/along:along-setup", adapter)
                for name in archive.namelist():
                    if name.startswith("along/skills/"):
                        self.assertNotIn(b"/along:along-setup", archive.read(name))

    def test_archives_are_byte_for_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = BUILD.build_release(SOURCE, Path(temp) / "first")
            second = BUILD.build_release(SOURCE, Path(temp) / "second")
            for host in ("codex", "claude"):
                first_zip, first_checksum = first[host]
                second_zip, second_checksum = second[host]
                self.assertEqual(first_zip.read_bytes(), second_zip.read_bytes(), host)
                self.assertEqual(first_checksum.read_bytes(), second_checksum.read_bytes(), host)

    def test_rejects_unknown_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "plugin"
            shutil.copytree(SOURCE, fixture, symlinks=True)
            (fixture / "unsupported.txt").write_text("not part of the plugin", encoding="utf-8")
            with self.assertRaises(BUILD.BuildError):
                BUILD.build_release(fixture, Path(temp) / "release")

    def test_rejects_secrets_absolute_paths_and_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            secret_fixture = Path(temp) / "secret"
            shutil.copytree(SOURCE, secret_fixture, symlinks=True)
            (secret_fixture / "README.md").write_text("TOKEN=real-secret-value\n", encoding="utf-8")
            with self.assertRaises(BUILD.BuildError):
                BUILD.build_release(secret_fixture, Path(temp) / "secret-release")

            path_fixture = Path(temp) / "absolute"
            shutil.copytree(SOURCE, path_fixture, symlinks=True)
            (path_fixture / "README.md").write_text("Private path: /Users/alice/finance\n", encoding="utf-8")
            with self.assertRaises(BUILD.BuildError):
                BUILD.build_release(path_fixture, Path(temp) / "absolute-release")

            symlink_fixture = Path(temp) / "symlink"
            shutil.copytree(SOURCE, symlink_fixture, symlinks=True)
            link = symlink_fixture / "skills" / "along-status" / "references" / "linked.md"
            link.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(symlink_fixture / "LICENSE", link)
            with self.assertRaises(BUILD.BuildError):
                BUILD.build_release(symlink_fixture, Path(temp) / "symlink-release")

    def test_rejects_output_inside_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "plugin"
            shutil.copytree(SOURCE, fixture, symlinks=True)
            with self.assertRaises(BUILD.BuildError):
                BUILD.build_release(fixture, fixture / "release")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
