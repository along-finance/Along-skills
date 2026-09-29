#!/usr/bin/env python3
"""Build the supported Codex bundle, with optional experimental host output.

The canonical source is the plugin tree under ``plugins/along``.  This module
does not install or publish anything; it materializes two host-specific trees
and a ZIP/checksum pair for each host.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Sequence


VERSION = "0.1.0"
SKILL_NAMES = (
    "along-manage-budget",
    "along-plan-cash",
    "along-reconcile",
    "along-report-money",
    "along-review-transactions",
    "along-setup",
    "along-status",
    "along-sync-account",
)

_ROOT_FILES = {"LICENSE", "README.md", "NOTICE", "CHANGELOG.md"}
_SKILL_DIRS = {"agents", "references", "scripts", "assets"}
_IGNORED_NAMES = {"__pycache__", ".DS_Store"}
_SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials",
    "credentials.json",
    "secrets.json",
    "id_rsa",
    "id_ed25519",
}
_ABSOLUTE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.:/-])(?:/(?:Users|home|private|tmp|var|etc|opt|root|Volumes)/[^\s)`\"']+|[A-Za-z]:[\\/][^\s)`\"']+)"
)
_PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
_TOKEN_RE = re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b|\b(?:ghp|github_pat|xox[baprs]-|sk-)[A-Za-z0-9_-]{16,}")
_ASSIGNMENT_SECRET_RE = re.compile(
    r"(?i)\b(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*['\"]?([^\s'\"`]+)"
)
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


class BuildError(RuntimeError):
    """Raised when canonical input cannot produce a safe bundle."""


def _default_source() -> Path:
    return Path(__file__).resolve().parent / "plugins" / "along"


def _marketplace_template() -> Path:
    return Path(__file__).resolve().parent / ".agents" / "plugins" / "marketplace.json"


def _default_output() -> Path:
    return Path(__file__).resolve().parent / "dist"


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _is_ignored(relative: Path) -> bool:
    return any(part in _IGNORED_NAMES for part in relative.parts)


def _reject_name(relative: Path) -> None:
    for part in relative.parts:
        lower = part.lower()
        if lower in _SECRET_NAMES or lower.startswith("credentials") or lower.startswith("secret"):
            raise BuildError(f"secret-like source entry is not distributable: {relative.as_posix()}")
        if lower.endswith((".pem", ".p12", ".pfx", ".key")):
            raise BuildError(f"credential/key source entry is not distributable: {relative.as_posix()}")
        if lower.endswith(".pyc"):
            raise BuildError(f"compiled cache entry is not distributable: {relative.as_posix()}")
        if part.startswith(".") and part not in {".codex-plugin"}:
            raise BuildError(f"unsupported hidden source entry: {relative.as_posix()}")


def _scan_text(relative: Path, data: bytes) -> None:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return
    if _ABSOLUTE_PATH_RE.search(text):
        raise BuildError(f"absolute user/system path found in {relative.as_posix()}")
    if _PRIVATE_KEY_RE.search(text) or _TOKEN_RE.search(text):
        raise BuildError(f"credential material found in {relative.as_posix()}")
    for match in _ASSIGNMENT_SECRET_RE.finditer(text):
        value = match.group(1).strip().lower().strip(".,;)")
        if value not in {
            "never",
            "none",
            "null",
            "redacted",
            "placeholder",
            "example",
            "example-value",
            "your-token",
            "your_password",
            "<value>",
            "<redacted>",
        }:
            raise BuildError(f"credential-like assignment found in {relative.as_posix()}")


def _walk_files(root: Path) -> list[Path]:
    """Validate source safety and return regular files relative to root."""

    if root.is_symlink():
        raise BuildError("canonical source must not be a symlink")
    files: list[Path] = []
    for directory, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        directory_path = Path(directory)
        kept_dirs: list[str] = []
        for name in sorted(directory_names):
            relative = (directory_path / name).relative_to(root)
            path = directory_path / name
            if path.is_symlink():
                raise BuildError(f"symlink is not allowed: {relative.as_posix()}")
            if name in _IGNORED_NAMES:
                continue
            _reject_name(relative)
            kept_dirs.append(name)
        directory_names[:] = kept_dirs
        for name in sorted(file_names):
            relative = (directory_path / name).relative_to(root)
            path = directory_path / name
            if path.is_symlink():
                raise BuildError(f"symlink is not allowed: {relative.as_posix()}")
            if _is_ignored(relative):
                continue
            _reject_name(relative)
            if not path.is_file():
                raise BuildError(f"unsupported non-file source entry: {relative.as_posix()}")
            _scan_text(relative, path.read_bytes())
            files.append(relative)
    return sorted(files, key=lambda item: item.as_posix())


def _validate_layout(source: Path, files: Sequence[Path]) -> dict:
    if not source.is_dir():
        raise BuildError(f"canonical source directory does not exist: {source}")
    relative_entries = {path for path in source.iterdir() if path.name not in _IGNORED_NAMES}
    expected_root = {source / ".codex-plugin", source / "skills"}
    for optional in _ROOT_FILES:
        if (source / optional).exists():
            expected_root.add(source / optional)
    unknown_root = relative_entries - expected_root
    if unknown_root:
        names = ", ".join(sorted(item.name for item in unknown_root))
        raise BuildError(f"unsupported canonical root entries: {names}")

    codex_dir = source / ".codex-plugin"
    if not codex_dir.is_dir() or codex_dir.is_symlink():
        raise BuildError("canonical source requires a real .codex-plugin directory")
    codex_entries = {item.name for item in codex_dir.iterdir() if item.name not in _IGNORED_NAMES}
    if codex_entries != {"plugin.json"}:
        raise BuildError(".codex-plugin must contain only plugin.json")
    plugin_path = codex_dir / "plugin.json"
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BuildError(f"invalid .codex-plugin/plugin.json: {exc}") from exc
    if not isinstance(plugin, dict):
        raise BuildError(".codex-plugin/plugin.json must contain an object")
    for key in ("name", "version", "description", "skills"):
        if not plugin.get(key):
            raise BuildError(f"Codex plugin metadata is missing {key!r}")
    if plugin["name"] != "along":
        raise BuildError("canonical plugin name must be along")
    if plugin["version"] != VERSION:
        raise BuildError(f"canonical plugin version must be {VERSION}")
    if not isinstance(plugin["skills"], str) or not plugin["skills"].startswith("./"):
        raise BuildError("Codex plugin skills must be a relative path")

    skills_dir = source / "skills"
    if not skills_dir.is_dir() or skills_dir.is_symlink():
        raise BuildError("canonical source requires a real skills directory")
    skill_names = {item.name for item in skills_dir.iterdir() if item.name not in _IGNORED_NAMES}
    if skill_names != set(SKILL_NAMES):
        missing = sorted(set(SKILL_NAMES) - skill_names)
        extra = sorted(skill_names - set(SKILL_NAMES))
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise BuildError("canonical skill inventory mismatch: " + "; ".join(details))
    for skill_name in SKILL_NAMES:
        skill_dir = skills_dir / skill_name
        if not skill_dir.is_dir() or skill_dir.is_symlink():
            raise BuildError(f"skill must be a real directory: {skill_name}")
        if not (skill_dir / "SKILL.md").is_file():
            raise BuildError(f"skill is missing SKILL.md: {skill_name}")
        for entry in skill_dir.iterdir():
            if entry.name in _IGNORED_NAMES:
                continue
            if entry.name == "SKILL.md":
                continue
            if entry.is_symlink():
                raise BuildError(f"symlink is not allowed: skills/{skill_name}/{entry.name}")
            if entry.name not in _SKILL_DIRS:
                raise BuildError(f"unsupported entry in {skill_name}: {entry.name}")
        agents = skill_dir / "agents"
        if agents.exists():
            entries = {item.name for item in agents.iterdir() if item.name not in _IGNORED_NAMES}
            if entries != {"openai.yaml"}:
                raise BuildError(f"{skill_name}/agents must contain only openai.yaml")

    if "skills/along-setup/agents/openai.yaml" not in {path.as_posix() for path in files}:
        raise BuildError("along-setup must include agents/openai.yaml for Codex")
    setup_metadata = (source / "skills" / "along-setup" / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if not re.search(r"(?m)^\s*allow_implicit_invocation:\s*false\s*$", setup_metadata):
        raise BuildError("along-setup Codex metadata must disable implicit invocation")
    return plugin


def _read_marketplace_template() -> bytes:
    path = _marketplace_template()
    if path.is_symlink() or not path.is_file():
        raise BuildError(f"Codex marketplace metadata template is missing: {path}")
    relative = Path(".agents/plugins/marketplace.json")
    data = path.read_bytes()
    _scan_text(relative, data)
    try:
        metadata = json.loads(data)
    except (UnicodeDecodeError, ValueError) as exc:
        raise BuildError(f"invalid Codex marketplace metadata template: {exc}") from exc
    if not isinstance(metadata, dict) or metadata.get("name") != "along":
        raise BuildError("Codex marketplace metadata must have name 'along'")
    plugins = metadata.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1 or not isinstance(plugins[0], dict):
        raise BuildError("Codex marketplace metadata must list exactly one plugin")
    entry = plugins[0]
    if entry.get("name") != "along":
        raise BuildError("Codex marketplace plugin entry must have name 'along'")
    source_spec = entry.get("source")
    if not isinstance(source_spec, dict) or source_spec.get("source") != "local":
        raise BuildError("Codex marketplace plugin must use a local source")
    if source_spec.get("path") != "./plugins/along":
        raise BuildError("Codex marketplace plugin path must be ./plugins/along")
    return data


def _with_claude_setup_frontmatter(text: str) -> str:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise BuildError("along-setup/SKILL.md must have YAML frontmatter")
    lines = [line for line in match.group(1).splitlines() if not line.strip().startswith("disable-model-invocation:")]
    lines.append("disable-model-invocation: true")
    frontmatter = "---\n" + "\n".join(lines).rstrip() + "\n---\n"
    return frontmatter + text[match.end() :]


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


def _copy_host_tree(source: Path, files: Sequence[Path], destination: Path, host: str) -> None:
    for relative in files:
        if host == "claude" and (
            relative.parts[0] == ".codex-plugin"
            or (len(relative.parts) >= 3 and relative.parts[0] == "skills" and relative.parts[2] == "agents")
        ):
            continue
        source_path = source / relative
        target_path = destination / relative
        data = source_path.read_bytes()
        if host == "claude" and relative == Path("skills/along-setup/SKILL.md"):
            data = _with_claude_setup_frontmatter(data.decode("utf-8")).encode("utf-8")
        _write_bytes(target_path, data)


def _write_json(path: Path, value: dict) -> None:
    _write_bytes(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _write_marketplace_metadata(destination: Path, data: bytes) -> None:
    _write_bytes(destination / ".agents" / "plugins" / "marketplace.json", data)


def _write_claude_adapter(destination: Path) -> None:
    text = """# Claude host adapter

Claude Desktop: upload `along-claude-0.1.0.zip` through Customize > Plugins >
Add plugin > Upload plugin. Keep the complete bundle installed so shared files
remain available. Start a new Cowork task after installing or updating.

Claude Code: load this bundle with Claude Code's plugin loader. Invoke Along setup
explicitly with:

`/along:along-setup`

Setup remains user-invoked and does not authorize sync, reconciliation, source login,
connector changes, imports, payments or transfers.
"""
    _write_bytes(destination / "HOST-ADAPTER.md", text.encode("utf-8"))


def _set_deterministic_times(root: Path) -> None:
    epoch = 315532800  # 1980-01-01 00:00:00 UTC, also valid for ZIP timestamps.
    paths = sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True)
    for path in paths + [root]:
        if path.is_symlink():
            raise BuildError(f"generated output contains a symlink: {path}")
        os.utime(path, (epoch, epoch), follow_symlinks=False)


def _zip_tree(root: Path, zip_path: Path) -> None:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise BuildError(f"generated output contains a symlink: {path}")
        if path.is_file():
            files.append(path)
    files.sort(key=lambda item: item.relative_to(root).as_posix())
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(root)
            parts = relative.parts
            if any(part in {"", ".", ".."} for part in parts):
                raise BuildError(f"unsafe generated archive path: {relative}")
            archive_name = PurePosixPath("along", *parts).as_posix()
            info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    os.chmod(zip_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    os.utime(zip_path, (315532800, 315532800))


def _write_checksum(zip_path: Path) -> Path:
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    checksum_path = zip_path.with_name(zip_path.name + ".sha256")
    _write_bytes(checksum_path, f"{digest}  {zip_path.name}\n".encode("ascii"))
    return checksum_path


def _prepare_host(
    source: Path,
    files: Sequence[Path],
    plugin: dict,
    marketplace_metadata: bytes,
    output_root: Path,
    host: str,
) -> tuple[Path, Path]:
    host_dir = output_root / host
    if host_dir.exists() or host_dir.is_symlink():
        if host_dir.is_symlink():
            raise BuildError(f"refusing to replace symlinked output directory: {host_dir}")
        shutil.rmtree(host_dir)
    bundle_root = host_dir / "along"
    bundle_root.mkdir(parents=True, exist_ok=True)
    plugin_root = bundle_root / "plugins" / "along" if host == "codex" else bundle_root
    _copy_host_tree(source, files, plugin_root, host)
    if host == "codex":
        codex_metadata = plugin_root / ".codex-plugin" / "plugin.json"
        if not codex_metadata.is_file():
            raise BuildError("Codex output is missing plugins/along/.codex-plugin/plugin.json")
        _write_marketplace_metadata(bundle_root, marketplace_metadata)
        for name in ("README.md", "LICENSE", "CHANGELOG.md"):
            if (source / name).is_file():
                _write_bytes(bundle_root / name, (source / name).read_bytes())
    else:
        claude_metadata = {
            "name": "along",
            "version": VERSION,
            "description": plugin["description"],
            "author": {"name": "Along contributors"},
            "license": "MIT",
            "skills": "./skills/",
        }
        _write_json(bundle_root / ".claude-plugin" / "plugin.json", claude_metadata)
        _write_claude_adapter(bundle_root)
        if list(bundle_root.glob("skills/*/agents")):
            raise BuildError("Claude output must not contain agents/openai.yaml metadata")
        setup = bundle_root / "skills" / "along-setup" / "SKILL.md"
        if "disable-model-invocation: true" not in setup.read_text(encoding="utf-8"):
            raise BuildError("Claude setup skill must disable model invocation")
    _set_deterministic_times(bundle_root)
    zip_path = host_dir / f"along-{host}-{VERSION}.zip"
    _zip_tree(bundle_root, zip_path)
    checksum_path = _write_checksum(zip_path)
    return zip_path, checksum_path


def build_release(source: Path | str | None = None, output: Path | str | None = None, *, include_experimental_claude: bool = False) -> dict[str, tuple[Path, Path]]:
    """Build Codex and explicitly requested experimental bundles."""

    source_path = Path(source) if source is not None else _default_source()
    output_path = Path(output) if output is not None else _default_output()
    source_path = source_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    if _is_within(output_path, source_path):
        raise BuildError("release output must not be inside canonical source")
    files = _walk_files(source_path)
    plugin = _validate_layout(source_path, files)
    marketplace_metadata = _read_marketplace_template()
    output_path.mkdir(parents=True, exist_ok=True)
    results: dict[str, tuple[Path, Path]] = {}
    for host in (("codex", "claude") if include_experimental_claude else ("codex",)):
        results[host] = _prepare_host(source_path, files, plugin, marketplace_metadata, output_path, host)
    return results


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=_default_source())
    parser.add_argument("--output", type=Path, default=_default_output())
    parser.add_argument("--include-experimental-claude", action="store_true", help="Also build unsupported Claude contributor scaffolding")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        results = build_release(args.source, args.output, include_experimental_claude=args.include_experimental_claude)
    except BuildError as exc:
        print(f"along build failed: {exc}", file=sys.stderr)
        return 2
    for host, (zip_path, checksum_path) in results.items():
        print(f"{host}: {zip_path}")
        print(f"{host}: {checksum_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
