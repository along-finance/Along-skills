#!/usr/bin/env python3
"""Validate an Along plugin bundle and its synthetic release fixtures.

This validator is intentionally release-local and read-only.  It inspects the
candidate plugin, optionally validates host-build metadata, runs bundled Python
unit tests, and emits JSON evidence to stdout.  It never reads household data,
uses the network, installs packages, or changes the candidate bundle.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import unquote


EXPECTED_SKILLS = frozenset(
    {
        "along-setup",
        "along-sync-account",
        "along-status",
        "along-review-transactions",
        "along-reconcile",
        "along-report-money",
        "along-plan-cash",
        "along-manage-budget",
    }
)
CAPABILITY_NAMES = (
    "file_read",
    "ui_read",
    "ui_write",
    "connector_read",
    "python3_10",
    "scheduler",
)
CAPABILITY_STATUSES = frozenset({"passed", "blocked", "unknown"})

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\n]+)\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
PRIVATE_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home|private|var/folders|tmp)/[^\s<>'\"`)\]]+"),
    re.compile(r"(?<![A-Za-z0-9_])~/(?:[^\s<>'\"`)\]]+)") ,
    re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/][^\s<>'\"`)\]]+"),
    re.compile(r"(?<![A-Za-z0-9_])\\\\[^\\\s]+\\[^\s<>'\"`)\]]+"),
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(
        r"(?i)\b(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|password|session[_ -]?token|cookie)\s*[:=]\s*[\"']?(?!reference\b|placeholder\b|unknown\b|none\b|redacted\b)[A-Za-z0-9_./+=-]{8,}"
    ),
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
)


def _issue(check: str, message: str, **details: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"check": check, "message": message}
    item.update(details)
    return item


def _within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve(strict=False).relative_to(root.resolve(strict=False)))
    except ValueError:
        return str(path)


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return ()
    return (path for path in root.rglob("*") if path.is_file() and not path.is_symlink())


def _slugify_heading(heading: str) -> str:
    heading = heading.strip().lower()
    heading = re.sub(r"[`*_~]", "", heading)
    heading = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
    return re.sub(r"\s+", "-", heading).strip("-")


def _markdown_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    counts: Counter[str] = Counter()
    for match in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, flags=re.MULTILINE):
        base = _slugify_heading(match.group(1))
        ordinal = counts[base]
        counts[base] += 1
        anchors.add(base if ordinal == 0 else f"{base}-{ordinal}")
    return anchors


def check_symlinks(root: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    if not root.exists():
        issues.append(_issue("symlinks", "plugin root does not exist", path=str(root)))
        return {"status": "failed", "symlinks": records, "issues": issues}
    for path in root.rglob("*"):
        if not path.is_symlink():
            continue
        target = path.resolve(strict=False)
        inside = _within(target, root)
        exists = target.exists()
        records.append(
            {
                "path": _relative(path, root),
                "target": _relative(target, root) if inside else str(target),
                "inside_bundle": inside,
                "target_exists": exists,
            }
        )
        if not inside:
            issues.append(
                _issue(
                    "symlinks",
                    "symlink resolves outside the bundle",
                    path=_relative(path, root),
                    target=str(target),
                )
            )
        elif not exists:
            issues.append(
                _issue(
                    "symlinks",
                    "symlink target does not exist",
                    path=_relative(path, root),
                    target=_relative(target, root),
                )
            )
    return {
        "status": "passed" if not issues else "failed",
        "symlink_count": len(records),
        "symlinks": records,
        "issues": issues,
    }


def check_references(root: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    markdown_count = 0
    link_count = 0
    anchor_cache: dict[Path, set[str]] = {}
    for path in _files(root):
        if path.suffix.lower() != ".md":
            continue
        text = _read_text(path)
        if text is None:
            issues.append(_issue("references", "Markdown file is not readable UTF-8", path=_relative(path, root)))
            continue
        markdown_count += 1
        for raw_target in LINK_RE.findall(text):
            target_text = raw_target.strip()
            if target_text.startswith("<") and ">" in target_text:
                target_text = target_text[1 : target_text.index(">")] 
            else:
                target_text = target_text.split(None, 1)[0]
            if not target_text or target_text.startswith("//") or SCHEME_RE.match(target_text):
                continue
            link_count += 1
            target_text, _, fragment = target_text.partition("#")
            target_text = unquote(target_text).split("?", 1)[0]
            resolved = (path.parent / target_text).resolve() if target_text else path.resolve()
            if not _within(resolved, root):
                issues.append(
                    _issue(
                        "references",
                        "relative reference resolves outside the bundle",
                        source=_relative(path, root),
                        target=raw_target,
                    )
                )
                continue
            if not resolved.exists():
                issues.append(
                    _issue(
                        "references",
                        "relative reference target does not exist",
                        source=_relative(path, root),
                        target=raw_target,
                    )
                )
                continue
            if fragment and resolved.suffix.lower() == ".md":
                if resolved not in anchor_cache:
                    target_text_content = _read_text(resolved) or ""
                    anchor_cache[resolved] = _markdown_anchors(target_text_content)
                if fragment not in anchor_cache[resolved]:
                    issues.append(
                        _issue(
                            "references",
                            "Markdown reference anchor does not exist",
                            source=_relative(path, root),
                            target=raw_target,
                        )
                    )
    return {
        "status": "passed" if not issues else "failed",
        "markdown_files": markdown_count,
        "relative_links_checked": link_count,
        "issues": issues,
    }


def check_sensitive_content(root: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    scanned = 0
    for path in _files(root):
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        scanned += 1
        for pattern in PRIVATE_PATH_PATTERNS:
            match = pattern.search(text)
            if match:
                issues.append(
                    _issue(
                        "sensitive_content",
                        "distributed file contains a private machine path",
                        path=_relative(path, root),
                        evidence=match.group(0)[:120],
                    )
                )
                break
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                issues.append(
                    _issue(
                        "sensitive_content",
                        "distributed file contains a credential-like value",
                        path=_relative(path, root),
                        evidence=match.group(0)[:80],
                    )
                )
                break
    return {
        "status": "passed" if not issues else "failed",
        "text_files_scanned": scanned,
        "issues": issues,
    }


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    values: dict[str, str] = {}
    for line in text[3:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip().strip("'\"")
    return values


def check_bundle_shape(root: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    manifest_path = root / ".codex-plugin" / "plugin.json"
    manifest: dict[str, Any] = {}
    if not manifest_path.is_file():
        issues.append(_issue("bundle", "plugin manifest is missing", path=str(manifest_path)))
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(_issue("bundle", "plugin manifest is not valid JSON", error=str(exc)))
        if manifest.get("name") != "along":
            issues.append(_issue("bundle", "plugin manifest name is not along"))
        if manifest.get("skills") != "./skills/":
            issues.append(_issue("bundle", "plugin manifest skills path is not ./skills/"))

    skills_root = root / "skills"
    actual: set[str] = set()
    if not skills_root.is_dir():
        issues.append(_issue("bundle", "skills directory is missing", path="skills"))
    else:
        actual = {
            path.name
            for path in skills_root.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        }
    missing = sorted(EXPECTED_SKILLS - actual)
    unexpected = sorted(actual - EXPECTED_SKILLS)
    if missing:
        issues.append(_issue("bundle", "expected skills are missing", skills=missing))
    if unexpected:
        issues.append(_issue("bundle", "unexpected skill directories are present", skills=unexpected))

    frontmatter: dict[str, str] = {}
    for skill in sorted(EXPECTED_SKILLS & actual):
        skill_path = skills_root / skill / "SKILL.md"
        if not skill_path.is_file():
            issues.append(_issue("bundle", "skill entry file is missing", skill=skill))
            continue
        text = _read_text(skill_path)
        metadata = _frontmatter(text or "")
        frontmatter[skill] = metadata.get("name", "")
        if metadata.get("name") != skill:
            issues.append(
                _issue(
                    "bundle",
                    "skill frontmatter name does not match its directory",
                    skill=skill,
                    observed=metadata.get("name"),
                )
            )
    return {
        "status": "passed" if not issues else "failed",
        "expected_skills": sorted(EXPECTED_SKILLS),
        "actual_skills": sorted(actual),
        "missing_skills": missing,
        "unexpected_skills": unexpected,
        "frontmatter_names": frontmatter,
        "manifest": {
            "name": manifest.get("name"),
            "skills": manifest.get("skills"),
        },
        "issues": issues,
    }


def _json_object(path: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [_issue("host_build", "host build is not valid JSON", path=str(path), error=str(exc))]
    if not isinstance(value, dict):
        return None, [_issue("host_build", "host build root must be an object", path=str(path))]
    return value, []


def _first(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def check_host_build(path: Path) -> dict[str, Any]:
    data, issues = _json_object(path)
    if data is None:
        return {"status": "failed", "path": str(path), "issues": issues}
    if (
        isinstance(data.get("schema_version"), bool)
        or not isinstance(data.get("schema_version"), int)
        or data.get("schema_version") != 1
    ):
        issues.append(_issue("host_build", "schema_version must be 1", path=str(path)))
    host = _first(data, "host", "host_id")
    if not isinstance(host, str) or not host.strip():
        issues.append(_issue("host_build", "host is required", path=str(path)))

    setup_value = data.get("setup")
    setup = setup_value if isinstance(setup_value, Mapping) else {}
    invocation = _first(setup, "invocation", "setup_invocation")
    if invocation is None:
        invocation = _first(data, "setup_invocation", "setupInvocation")
    user_only = _first(setup, "user_only", "userOnly")
    if user_only is None:
        user_only = _first(data, "setup_user_only", "setupUserOnly")
    if not isinstance(invocation, str) or not invocation.strip():
        issues.append(_issue("host_build", "setup invocation is required", path=str(path)))
    if user_only is not True:
        issues.append(_issue("host_build", "setup must be explicitly user-only", path=str(path)))
    for key in ("automatic", "auto_setup", "auto_invoked", "setup_automatic"):
        if setup.get(key) is True or data.get(key) is True:
            issues.append(_issue("host_build", "setup cannot be automatic", path=str(path), field=key))

    runtime_value = _first(data, "runtime", "capabilities")
    runtime = runtime_value if isinstance(runtime_value, Mapping) else {}
    observed_runtime: dict[str, Any] = {}
    for capability in CAPABILITY_NAMES:
        value = runtime.get(capability)
        if not isinstance(value, Mapping):
            issues.append(
                _issue(
                    "host_build",
                    "host capability record is missing",
                    path=str(path),
                    capability=capability,
                )
            )
            continue
        status = value.get("status")
        tools = value.get("tools")
        if status not in CAPABILITY_STATUSES:
            issues.append(
                _issue(
                    "host_build",
                    "host capability status is invalid",
                    path=str(path),
                    capability=capability,
                    status=status,
                )
            )
        if not isinstance(tools, list) or any(not isinstance(tool, str) or not tool for tool in tools):
            issues.append(
                _issue(
                    "host_build",
                    "host capability tools must be a list of names",
                    path=str(path),
                    capability=capability,
                )
            )
        if status == "passed" and not tools:
            issues.append(
                _issue(
                    "host_build",
                    "a passed capability must name at least one tool",
                    path=str(path),
                    capability=capability,
                )
            )
        observed_runtime[capability] = {"status": status, "tools": tools}
    return {
        "status": "passed" if not issues else "failed",
        "path": str(path),
        "host": host,
        "setup": {"invocation": invocation, "user_only": user_only},
        "runtime": observed_runtime,
        "issues": issues,
    }


def check_host_builds(paths: Sequence[Path]) -> dict[str, Any]:
    results = [check_host_build(path) for path in paths]
    issues = [issue for result in results for issue in result.get("issues", [])]
    hosts = [result.get("host") for result in results if result.get("host")]
    duplicates = sorted(host for host, count in Counter(hosts).items() if count > 1)
    if duplicates:
        issues.append(_issue("host_build", "host build names must be unique", hosts=duplicates))
    return {
        "status": "passed" if not issues else "failed",
        "build_count": len(results),
        "hosts": hosts,
        "builds": results,
        "issues": issues,
    }


def _run_helper_test(script_dir: Path) -> dict[str, Any]:
    command = [sys.executable, "-m", "unittest", "discover", "-s", str(script_dir), "-p", "test_*.py", "-q"]
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            command,
            cwd=script_dir,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "script_dir": str(script_dir),
            "command": command,
            "status": "failed",
            "issues": [_issue("python_helpers", "helper test command failed to start or timed out", error=str(exc))],
        }
    output = (completed.stdout + "\n" + completed.stderr).strip()
    match = re.search(r"Ran\s+(\d+)\s+tests?", output)
    test_count = int(match.group(1)) if match else 0
    issues: list[dict[str, Any]] = []
    if completed.returncode != 0:
        issues.append(_issue("python_helpers", "bundled helper tests failed", returncode=completed.returncode))
    if test_count <= 0:
        issues.append(_issue("python_helpers", "bundled helper test discovery found no tests"))
    return {
        "script_dir": str(script_dir),
        "command": command,
        "status": "passed" if not issues else "failed",
        "returncode": completed.returncode,
        "tests_run": test_count,
        "output_tail": output[-2000:],
        "issues": issues,
    }


def check_python_helpers(root: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    script_dirs = sorted(
        {
            path.parent
            for path in _files(root)
            if path.name == "finance_checks.py" and path.parent.name == "scripts"
        }
    )
    for script_dir in script_dirs:
        tests = sorted(script_dir.glob("test_*.py"))
        if not tests:
            issues.append(
                _issue(
                    "python_helpers",
                    "finance helper has no discoverable unittest file",
                    script_dir=_relative(script_dir, root),
                )
            )
            continue
        result = _run_helper_test(script_dir)
        results.append(result)
        issues.extend(result.get("issues", []))
    if not script_dirs:
        issues.append(_issue("python_helpers", "no finance helper was found"))
    return {
        "status": "passed" if not issues else "failed",
        "helper_directories": [_relative(path, root) for path in script_dirs],
        "runs": results,
        "issues": issues,
    }


def _csv_rows(path: Path, required: set[str]) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or [])
            missing = sorted(required - headers)
            if missing:
                issues.append(_issue("fixtures", "CSV is missing required columns", path=str(path), columns=missing))
            rows = [dict(row) for row in reader]
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        return [], [_issue("fixtures", "CSV could not be read", path=str(path), error=str(exc))]
    return rows, issues


def _minor(amount: str, exponent: int, field: str) -> int:
    try:
        value = Decimal(amount)
    except InvalidOperation as exc:
        raise ValueError(f"{field} is not decimal") from exc
    if not value.is_finite():
        raise ValueError(f"{field} is not finite")
    scaled = value * (Decimal(10) ** exponent)
    if scaled != scaled.to_integral_value():
        raise ValueError(f"{field} has precision beyond exponent")
    return int(scaled)


def _string_id_set(value: Any, field: str, issues: list[dict[str, Any]]) -> set[str]:
    if not isinstance(value, list):
        return set()
    result: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item:
            issues.append(_issue("fixtures", f"{field} entries must be non-empty strings"))
            continue
        result.add(item)
    return result


def check_fixtures(fixtures_root: Path) -> dict[str, Any]:
    required_files = {
        "bank_csv": fixtures_root / "provided-source" / "bank_transactions.csv",
        "app_csv": fixtures_root / "provided-source" / "app_transactions.csv",
        "expected": fixtures_root / "provided-source" / "expected-reconciliation.json",
    }
    issues: list[dict[str, Any]] = []
    for label, path in required_files.items():
        if not path.is_file():
            issues.append(_issue("fixtures", "required fixture is missing", fixture=label, path=str(path)))
    if issues:
        return {"status": "failed", "fixtures_root": str(fixtures_root), "issues": issues}

    bank_required = {
        "source_id",
        "account_id",
        "date",
        "status",
        "amount",
        "currency",
        "merchant",
        "transaction_group",
        "duplicate_ordinal",
    }
    app_required = {
        "app_id",
        "account_id",
        "date",
        "status",
        "amount",
        "currency",
        "merchant",
        "transaction_group",
        "row_type",
        "parent_id",
        "duplicate_ordinal",
    }
    bank_rows, bank_issues = _csv_rows(required_files["bank_csv"], bank_required)
    app_rows, app_issues = _csv_rows(required_files["app_csv"], app_required)
    issues.extend(bank_issues)
    issues.extend(app_issues)
    try:
        expected = json.loads(required_files["expected"].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(_issue("fixtures", "expected fixture is not valid JSON", error=str(exc)))
        expected = {}
    if not isinstance(expected, dict):
        issues.append(_issue("fixtures", "expected fixture root must be an object"))
        expected = {}
    if (
        isinstance(expected.get("schema_version"), bool)
        or not isinstance(expected.get("schema_version"), int)
        or expected.get("schema_version") != 1
    ):
        issues.append(_issue("fixtures", "expected fixture schema_version must be 1"))

    exponents = expected.get("currency_exponents", {})
    if not isinstance(exponents, Mapping):
        issues.append(_issue("fixtures", "currency_exponents must be an object"))
        exponents = {}
    bank_by_id = {row.get("source_id"): row for row in bank_rows}
    app_by_id = {row.get("app_id"): row for row in app_rows}
    if len(bank_by_id) != len(bank_rows):
        issues.append(_issue("fixtures", "bank source IDs must be unique"))
    if len(app_by_id) != len(app_rows):
        issues.append(_issue("fixtures", "app IDs must be unique"))

    def amount(row: Mapping[str, str], key: str) -> int | None:
        currency = row.get("currency")
        exponent = exponents.get(currency)
        if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 0:
            issues.append(_issue("fixtures", "row currency lacks a valid exponent", row_id=row.get(key), currency=currency))
            return None
        try:
            return _minor(row.get("amount", ""), exponent, f"{key}={row.get(key)}")
        except ValueError as exc:
            issues.append(_issue("fixtures", "row amount is invalid", row_id=row.get(key), error=str(exc)))
            return None

    bank_minor = {row.get("source_id"): amount(row, "source_id") for row in bank_rows}
    app_minor = {row.get("app_id"): amount(row, "app_id") for row in app_rows}

    def row_span(rows: Sequence[Mapping[str, str]], key: str) -> dict[str, str] | None:
        dates: list[date] = []
        for row in rows:
            value = row.get("date", "")
            try:
                dates.append(date.fromisoformat(value))
            except ValueError:
                issues.append(_issue("fixtures", "row date is not ISO calendar date", row_id=row.get(key), date=value))
        if not dates:
            return None
        return {"start": min(dates).isoformat(), "end": max(dates).isoformat()}

    observed_bank_span = row_span(bank_rows, "source_id")
    observed_app_span = row_span(app_rows, "app_id")
    coverage = expected.get("coverage")
    observed_coverage: dict[str, Any] = {
        "bank_row_span": observed_bank_span,
        "app_row_span": observed_app_span,
    }
    if not isinstance(coverage, Mapping):
        issues.append(_issue("fixtures", "expected coverage must be an object"))
    else:
        for field in (
            "requested_interval",
            "declared_source_interval",
            "observed_bank_row_span",
            "observed_app_row_span",
        ):
            interval = coverage.get(field)
            if not isinstance(interval, Mapping) or not isinstance(interval.get("start"), str) or not isinstance(interval.get("end"), str):
                issues.append(_issue("fixtures", "coverage interval must have start and end dates", field=field))
                continue
            try:
                start = date.fromisoformat(interval["start"])
                end = date.fromisoformat(interval["end"])
                if start > end:
                    issues.append(_issue("fixtures", "coverage interval start is after end", field=field))
            except ValueError:
                issues.append(_issue("fixtures", "coverage interval contains an invalid date", field=field))
        if coverage.get("observed_bank_row_span") != observed_bank_span:
            issues.append(
                _issue(
                    "fixtures",
                    "declared bank row span does not match CSV rows",
                    expected=coverage.get("observed_bank_row_span"),
                    observed=observed_bank_span,
                )
            )
        if coverage.get("observed_app_row_span") != observed_app_span:
            issues.append(_issue("fixtures", "declared app row span does not match CSV rows", expected=coverage.get("observed_app_row_span"), observed=observed_app_span))
        if not isinstance(coverage.get("interpretation"), str) or not coverage.get("interpretation", "").strip():
            issues.append(_issue("fixtures", "coverage interpretation is required"))
        observed_coverage["requested_interval"] = coverage.get("requested_interval")
        observed_coverage["declared_source_interval"] = coverage.get("declared_source_interval")

    matches = expected.get("matches", [])
    source_only = expected.get("source_only", [])
    app_unmatched = expected.get("app_unmatched", [])
    pending_replacements = expected.get("pending_replacements", [])
    splits = expected.get("splits", [])
    duplicate_groups = expected.get("duplicate_groups", [])
    for name, value in (
        ("matches", matches),
        ("source_only", source_only),
        ("app_unmatched", app_unmatched),
        ("pending_replacements", pending_replacements),
        ("splits", splits),
        ("duplicate_groups", duplicate_groups),
    ):
        if not isinstance(value, list):
            issues.append(_issue("fixtures", f"expected {name} must be an array"))

    match_source_ids: set[str] = set()
    match_app_ids: set[str] = set()
    for item in matches if isinstance(matches, list) else []:
        if not isinstance(item, Mapping):
            issues.append(_issue("fixtures", "match entry must be an object"))
            continue
        source_id = item.get("source_id")
        app_id = item.get("app_id")
        if not isinstance(source_id, str) or not source_id:
            issues.append(_issue("fixtures", "match source_id must be a non-empty string"))
            continue
        if not isinstance(app_id, str) or not app_id:
            issues.append(_issue("fixtures", "match app_id must be a non-empty string"))
            continue
        match_source_ids.add(source_id)
        match_app_ids.add(app_id)
        source = bank_by_id.get(source_id)
        app = app_by_id.get(app_id)
        if source is None or app is None:
            issues.append(_issue("fixtures", "match references an unknown row", source_id=source_id, app_id=app_id))
            continue
        for field in ("account_id", "date", "currency", "merchant"):
            if source.get(field) != app.get(field):
                issues.append(_issue("fixtures", "matched rows disagree on identity field", source_id=source_id, app_id=app_id, field=field))
        if bank_minor.get(source_id) != app_minor.get(app_id):
            issues.append(_issue("fixtures", "matched rows do not conserve amount", source_id=source_id, app_id=app_id))

    source_only_set = _string_id_set(source_only, "source_only", issues)
    app_unmatched_set = _string_id_set(app_unmatched, "app_unmatched", issues)
    if not source_only_set.issubset(bank_by_id):
        issues.append(_issue("fixtures", "source_only references unknown source rows"))
    if not app_unmatched_set.issubset(app_by_id):
        issues.append(_issue("fixtures", "app_unmatched references unknown app rows"))

    pending_source_ids: set[str] = set()
    pending_posted_ids: set[str] = set()
    for item in pending_replacements if isinstance(pending_replacements, list) else []:
        if not isinstance(item, Mapping):
            issues.append(_issue("fixtures", "pending replacement entry must be an object"))
            continue
        pending_id = item.get("pending_source_id")
        posted_id = item.get("posted_source_id")
        app_id = item.get("app_id")
        if not isinstance(pending_id, str) or not pending_id:
            issues.append(_issue("fixtures", "pending_source_id must be a non-empty string"))
            continue
        if not isinstance(posted_id, str) or not posted_id:
            issues.append(_issue("fixtures", "posted_source_id must be a non-empty string"))
            continue
        if not isinstance(app_id, str) or not app_id:
            issues.append(_issue("fixtures", "pending replacement app_id must be a non-empty string"))
            continue
        pending_source_ids.add(pending_id)
        pending_posted_ids.add(posted_id)
        pending = bank_by_id.get(pending_id)
        posted = bank_by_id.get(posted_id)
        app = app_by_id.get(app_id)
        if not pending or not posted or not app:
            issues.append(_issue("fixtures", "pending replacement references an unknown row", item=dict(item)))
            continue
        if pending.get("status") != "pending" or posted.get("status") != "posted" or app.get("status") != "posted":
            issues.append(_issue("fixtures", "pending replacement statuses are inconsistent", item=dict(item)))
        if pending.get("transaction_group") != posted.get("transaction_group"):
            issues.append(_issue("fixtures", "pending and posted rows lack a shared transaction group", item=dict(item)))
        if bank_minor.get(pending_id) != bank_minor.get(posted_id) or bank_minor.get(posted_id) != app_minor.get(app_id):
            issues.append(_issue("fixtures", "pending replacement amounts do not conserve", item=dict(item)))

    split_parent_ids: set[str] = set()
    split_child_ids: set[str] = set()
    for item in splits if isinstance(splits, list) else []:
        if not isinstance(item, Mapping):
            issues.append(_issue("fixtures", "split entry must be an object"))
            continue
        source_id = item.get("source_id")
        parent_id = item.get("parent_app_id")
        children = item.get("children")
        if not isinstance(source_id, str) or not source_id:
            issues.append(_issue("fixtures", "split source_id must be a non-empty string"))
            continue
        if not isinstance(parent_id, str) or not parent_id:
            issues.append(_issue("fixtures", "split parent_app_id must be a non-empty string"))
            continue
        split_parent_ids.add(parent_id)
        if not isinstance(children, list):
            issues.append(_issue("fixtures", "split children must be an array", source_id=source_id))
            continue
        if any(not isinstance(child_id, str) or not child_id for child_id in children):
            issues.append(_issue("fixtures", "split child IDs must be non-empty strings", parent_app_id=parent_id))
            continue
        split_child_ids.update(children)
        source = bank_by_id.get(source_id)
        parent = app_by_id.get(parent_id)
        if not source or not parent:
            issues.append(_issue("fixtures", "split references an unknown parent/source", source_id=source_id, parent_app_id=parent_id))
            continue
        if parent.get("row_type") != "split_parent":
            issues.append(_issue("fixtures", "split parent has the wrong row type", parent_app_id=parent_id))
        if bank_minor.get(source_id) != app_minor.get(parent_id):
            issues.append(_issue("fixtures", "source and split parent amounts differ", source_id=source_id, parent_app_id=parent_id))
        child_sum = 0
        for child_id in children:
            child = app_by_id.get(child_id)
            if not child:
                issues.append(_issue("fixtures", "split references an unknown child", child_app_id=child_id))
                continue
            if child.get("row_type") != "split_child" or child.get("parent_id") != parent_id:
                issues.append(_issue("fixtures", "split child relationship is invalid", child_app_id=child_id, parent_app_id=parent_id))
            child_sum += app_minor.get(child_id) or 0
        if child_sum != app_minor.get(parent_id):
            issues.append(_issue("fixtures", "split children do not conserve parent amount", parent_app_id=parent_id, child_sum_minor=child_sum, parent_minor=app_minor.get(parent_id)))

    for item in duplicate_groups if isinstance(duplicate_groups, list) else []:
        if not isinstance(item, Mapping):
            issues.append(_issue("fixtures", "duplicate group entry must be an object"))
            continue
        source_ids = item.get("source_ids")
        app_ids = item.get("app_ids")
        if not isinstance(source_ids, list) or not isinstance(app_ids, list) or len(source_ids) != len(app_ids) or len(source_ids) < 2:
            issues.append(_issue("fixtures", "duplicate group must contain equal arrays of at least two IDs"))
            continue
        if any(not isinstance(value, str) or not value for value in source_ids + app_ids):
            issues.append(_issue("fixtures", "duplicate group IDs must be non-empty strings"))
            continue
        source_rows = [bank_by_id.get(value) for value in source_ids]
        app_rows_group = [app_by_id.get(value) for value in app_ids]
        if any(row is None for row in source_rows + app_rows_group):
            issues.append(_issue("fixtures", "duplicate group references an unknown row"))
            continue
        if len({row.get("amount") for row in source_rows}) != 1 or len({row.get("amount") for row in app_rows_group}) != 1:
            issues.append(_issue("fixtures", "duplicate group rows do not share the same amount"))
        if len(set(source_ids)) != len(source_ids) or len(set(app_ids)) != len(app_ids):
            issues.append(_issue("fixtures", "duplicate group IDs are not distinct"))
        if set(source_ids) & pending_source_ids or set(app_ids) & split_child_ids:
            issues.append(_issue("fixtures", "duplicate group overlaps a different fixture relationship"))

    expected_source_coverage = match_source_ids | source_only_set | pending_source_ids
    expected_app_coverage = match_app_ids | app_unmatched_set | split_child_ids
    if expected_source_coverage != set(bank_by_id):
        issues.append(_issue("fixtures", "expected results do not cover every bank row", missing=sorted(set(bank_by_id) - expected_source_coverage), extra=sorted(expected_source_coverage - set(bank_by_id))))
    if expected_app_coverage != set(app_by_id):
        issues.append(_issue("fixtures", "expected results do not cover every app row", missing=sorted(set(app_by_id) - expected_app_coverage), extra=sorted(expected_app_coverage - set(app_by_id))))

    summary = expected.get("summary", {})
    observed_summary = {
        "bank_rows": len(bank_rows),
        "app_rows": len(app_rows),
        "matched_pairs": len(matches) if isinstance(matches, list) else 0,
        "source_only": len(source_only_set),
        "app_unmatched": len(app_unmatched_set),
        "pending_replacements": len(pending_replacements) if isinstance(pending_replacements, list) else 0,
        "split_children": len(split_child_ids),
    }
    if isinstance(summary, Mapping):
        for field, observed in observed_summary.items():
            if summary.get(field) != observed:
                issues.append(_issue("fixtures", "expected summary does not match fixture rows", field=field, expected=summary.get(field), observed=observed))
    else:
        issues.append(_issue("fixtures", "expected summary must be an object"))
    return {
        "status": "passed" if not issues else "failed",
        "fixtures_root": str(fixtures_root),
        "bank_rows": len(bank_rows),
        "app_rows": len(app_rows),
        "coverage": observed_coverage,
        "observed_summary": observed_summary,
        "issues": issues,
    }


def validate_release(
    plugin_root: Path,
    *,
    fixtures_root: Path | None = None,
    host_builds: Sequence[Path] = (),
) -> dict[str, Any]:
    plugin_root = plugin_root.resolve()
    checks: dict[str, Any] = {}
    checks["bundle"] = check_bundle_shape(plugin_root)
    checks["references"] = check_references(plugin_root)
    checks["symlinks"] = check_symlinks(plugin_root)
    checks["sensitive_content"] = check_sensitive_content(plugin_root)
    checks["python_helpers"] = check_python_helpers(plugin_root)
    if host_builds:
        checks["host_builds"] = check_host_builds(host_builds)
    else:
        checks["host_builds"] = {
            "status": "skipped",
            "build_count": 0,
            "issues": [],
            "reason": "no host-build metadata supplied",
        }
    if fixtures_root is not None:
        checks["fixtures"] = check_fixtures(fixtures_root.resolve())
    else:
        checks["fixtures"] = {
            "status": "skipped",
            "issues": [],
            "reason": "no fixtures directory supplied",
        }
    issues = [issue for check in checks.values() for issue in check.get("issues", [])]
    failed_checks = [name for name, check in checks.items() if check.get("status") == "failed"]
    return {
        "schema_version": 1,
        "status": "passed" if not issues else "failed",
        "plugin_root": str(plugin_root),
        "checks": checks,
        "failed_checks": failed_checks,
        "issues": issues,
    }


def _default_path(name: str) -> Path:
    return Path(__file__).resolve().parents[1] / name


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate an Along plugin bundle, supplied host-build metadata, "
            "synthetic source/app fixtures, references, and bundled Python tests."
        )
    )
    parser.add_argument(
        "plugin_root",
        nargs="?",
        type=Path,
        default=_default_path("plugins/along"),
        help="candidate plugin directory (default: ../plugins/along)",
    )
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=_default_path("fixtures"),
        help="release fixtures directory (default: ../fixtures)",
    )
    parser.add_argument(
        "--host-build",
        dest="host_builds",
        action="append",
        type=Path,
        default=[],
        help="host-build JSON metadata; repeat for each host build",
    )
    args = parser.parse_args(argv)
    result = validate_release(
        args.plugin_root,
        fixtures_root=args.fixtures,
        host_builds=args.host_builds,
    )
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
