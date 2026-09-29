#!/usr/bin/env python3
"""Run read-only Codex smoke scenarios against project-local Along skills.

The harness copies the candidate's canonical skills into
``work/along-production/tests/codex-scenarios/.agents/skills`` so the smoke
sessions do not consult or mutate the user's global skill installation.  Each
Codex call uses the existing login, a read-only sandbox, and an ephemeral
session.  Prompts are synthetic and explicitly prohibit browser, connector,
account, and file writes.

Full event streams and final answers stay under the private
``tests/codex-scenarios/runs`` directory.  The stdout result is a compact JSON
summary whose observations are based on response evidence, rather than merely
repeating the static bundle validator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PRODUCTION_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SKILLS = PRODUCTION_ROOT / "plugins" / "along" / "skills"
SCENARIO_ROOT = PRODUCTION_ROOT / "fixtures" / "scenarios"
PRIVATE_ROOT = PRODUCTION_ROOT / "tests" / "codex-scenarios"
LOCAL_SKILLS = PRIVATE_ROOT / ".agents" / "skills"
CSV_ONLY_ROOT = PRIVATE_ROOT / "inputs" / "provided-source-csv-only"

SCENARIO_EXPECTATIONS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "status-missing-setup": (
        ("missing setup is acknowledged", (r"missing|absent|unavailable|no saved",)),
        (
            "explicit setup remains user-invoked",
            (r"\$along-setup|explicit.{0,40}(setup|set up)|invoke.{0,30}set up",),
        ),
        (
            "status does not initialize",
            (
                r"do not.{0,20}(initial|creat|invoke)",
                r"not.{0,20}(initial|creat)",
                r"does not.{0,20}(initial|creat|invoke|start)",
                r"setup was not started|without setup",
            ),
        ),
    ),
    "sync-choice": (
        ("app-only choice", (r"app[- ]only|check monarch only",)),
        ("Along sync choice", (r"along.{0,30}sync|set up.{0,30}sync",)),
        ("choice remains unresolved", (r"choose|choice|ambiguous|not.{0,20}(automatic|silent)",)),
    ),
    "provided-source-reconciliation": (
        ("four matches are observed", (r"(?:four|4).{0,30}match|match.{0,30}(?:four|4)",)),
        ("source-only 80 is observed", (r"(?:source|bank).{0,120}(?:80|80\.00)|80(?:\.00)?.{0,120}(?:source|missing)",)),
        ("app-only 22 is observed", (r"(?:app|unmatched).{0,120}(?:22|22\.00)|22(?:\.00)?.{0,120}(?:app|unmatched)",)),
        ("pending-to-posted is observed", (r"pending.{0,100}posted|posted.{0,100}pending|pending.{0,100}replacement",)),
        ("100 split conservation is observed", (r"split.{0,40}100|100.{0,40}split",)),
        ("requested and declared coverage are distinguished", (r"requested.{0,40}(?:declared|interval)|declared.{0,40}(?:requested|interval)",)),
        (
            "observed row span is distinguished from completeness",
            (
                r"observed.{0,150}(?:complete|validated|prove|coverage)",
                r"(?:row|date).{0,80}span.{0,100}(?:not|does not|neither).{0,30}(?:prove|complete|establish|validate)",
            ),
        ),
    ),
    "uncertain-import": (
        ("applied-unverified state is observed", (r"applied[- ]unverified",)),
        ("stable identity inspection is required", (r"inspect|re[- ]read|reobserve|verify",)),
        ("blind retry is rejected", (r"do not.{0,30}retr|never.{0,30}retr|no.{0,20}blind.{0,20}retr",)),
        ("source identity or fingerprint is preserved", (r"source id|source identifier|fingerprint",)),
    ),
    "single-writer-unknown": (
        ("prepare-only route is observed", (r"prepare[- ]only|prepare.{0,20}proposal",)),
        ("ownership uncertainty blocks apply", (r"unknown|cannot.{0,30}exclusive|no.{0,20}single writer",)),
        (
            "no financial write is applied",
            (
                r"do not.{0,30}(appl|repair|import|delet|revers)",
                r"stop.{0,20}before.{0,20}(write|apply)",
                r"cannot.{0,20}apply",
                r"no.{0,30}(financial )?(write|repair|import|delet|revers).{0,20}(performed|applied|made)",
                r"no.{0,120}(write|repair|import|delet|revers).{0,80}(performed|applied|made)",
            ),
        ),
    ),
}
SCENARIO_SKILLS = {
    "status-missing-setup": ("along-status",),
    "sync-choice": ("along-sync-account",),
    "provided-source-reconciliation": ("along-reconcile",),
    "uncertain-import": ("along-sync-account", "along-reconcile"),
    "single-writer-unknown": ("along-reconcile",),
}


def _scenario_prompt(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^## Prompt\s*$\n\s*(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    prompt = match.group(1).strip() if match else text.strip()
    # Keep fixture prompts portable while making the path readable from the
    # project-local smoke workspace.
    return prompt.replace("work/along-production/fixtures", "../../fixtures")


def _copy_local_skills() -> None:
    if not PLUGIN_SKILLS.is_dir():
        raise RuntimeError(f"canonical skill directory is missing: {PLUGIN_SKILLS}")
    LOCAL_SKILLS.mkdir(parents=True, exist_ok=True)
    for skill in sorted(path for path in PLUGIN_SKILLS.iterdir() if path.is_dir()):
        destination = LOCAL_SKILLS / skill.name
        shutil.copytree(
            skill,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def _copy_csv_only_fixture() -> None:
    """Stage only the two source files used by the independent smoke run."""

    source_root = PRODUCTION_ROOT / "fixtures" / "provided-source"
    CSV_ONLY_ROOT.mkdir(parents=True, exist_ok=True)
    for name in ("bank_transactions.csv", "app_transactions.csv"):
        source = source_root / name
        if not source.is_file():
            raise RuntimeError(f"CSV smoke fixture is missing: {source}")
        shutil.copy2(source, CSV_ONLY_ROOT / name)


def _find_text(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for child in value.values():
            yield from _find_text(child)
    elif isinstance(value, list):
        for child in value:
            yield from _find_text(child)


def _answer_from_events(stdout: str, answer_path: Path) -> str:
    if answer_path.is_file():
        try:
            return answer_path.read_text(encoding="utf-8").strip()
        except OSError:
            pass
    text_parts: list[str] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        text_parts.extend(_find_text(event))
    return "\n".join(text_parts).strip()


def _skill_paths_from_events(stdout: str) -> list[str]:
    """Extract actual skill paths mentioned by tool/file events.

    The prompt and final answer are deliberately excluded.  A path counts only
    when it appears in an event whose type suggests a tool, command, file or
    shell action; this avoids claiming that a model's prose proves which skill
    source it loaded.
    """

    paths: set[str] = set()
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_type = str(event.get("type", "")).lower()
        item_type = str(event.get("item", {}).get("type", "")).lower()
        event_has_command_payload = isinstance(event.get("item"), Mapping) and (
            "command" in event["item"] or "aggregated_output" in event["item"]
        )
        if not (
            any(token in event_type for token in ("tool", "command", "exec", "file", "shell"))
            or any(token in item_type for token in ("tool", "command", "exec", "file", "shell"))
            or event_has_command_payload
        ):
            continue
        for text in _find_text(event):
            for match in re.finditer(r"(?:/[^\s\"'<>`]+|\.?\.?/[^\s\"'<>`]+|\.agents/skills/[^\s\"'<>`]+)", text):
                token = match.group(0).rstrip(".,;:)]}>")
                if ".agents/skills/" not in token:
                    continue
                if token.startswith(".agents/skills/"):
                    path = (PRIVATE_ROOT / token).resolve()
                elif token.startswith("/"):
                    path = Path(token).resolve()
                else:
                    path = (PRIVATE_ROOT / token).resolve()
                paths.add(str(path))
    return sorted(paths)


def _evaluate(name: str, answer: str) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for label, patterns in SCENARIO_EXPECTATIONS[name]:
        matched_pattern = next(
            (pattern for pattern in patterns if re.search(pattern, answer, flags=re.IGNORECASE | re.DOTALL)),
            None,
        )
        checks.append(
            {
                "observation": label,
                "observed": matched_pattern is not None,
                "matched_pattern": matched_pattern,
            }
        )
    observed = all(item["observed"] for item in checks)
    return {
        "status": "observed" if observed else "inconclusive",
        "observations": checks,
    }


def _run_one(name: str, prompt: str, run_dir: Path, model: str | None, timeout: int) -> dict[str, Any]:
    answer_path = run_dir / f"{name}.answer.md"
    events_path = run_dir / f"{name}.events.jsonl"
    stderr_path = run_dir / f"{name}.stderr.log"
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--json",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-C",
        str(PRIVATE_ROOT),
        "-o",
        str(answer_path),
    ]
    if model:
        command.extend(["--model", model])
    command.append("-")
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    try:
        completed = subprocess.run(
            command,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        events_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        answer = _answer_from_events(completed.stdout, answer_path)
        skill_paths = _skill_paths_from_events(completed.stdout)
        expected_skill_paths = {
            str((LOCAL_SKILLS / skill).resolve())
            for skill in SCENARIO_SKILLS[name]
        }
        observed_expected_skill = any(
            path in expected_skill_paths or any(
                path.startswith(expected + "/") for expected in expected_skill_paths
            )
            for path in skill_paths
        )
        skill_paths_within_copy = all(
            Path(path).is_relative_to(LOCAL_SKILLS.resolve()) for path in skill_paths
        )
        evaluation = _evaluate(name, answer)
        if not observed_expected_skill or not skill_paths_within_copy:
            evaluation["status"] = "inconclusive"
        if completed.returncode != 0:
            evaluation["status"] = "failed"
        return {
            "scenario": name,
            "status": evaluation["status"],
            "returncode": completed.returncode,
            "prompt_sha256": prompt_hash,
            "command": command,
            "answer_path": str(answer_path.relative_to(PRODUCTION_ROOT)),
            "events_path": str(events_path.relative_to(PRODUCTION_ROOT)),
            "stderr_path": str(stderr_path.relative_to(PRODUCTION_ROOT)),
            "answer_excerpt": answer[-5000:],
            "observations": evaluation["observations"],
            "skill_paths_observed": skill_paths,
            "skill_path_status": "observed" if observed_expected_skill and skill_paths_within_copy else "inconclusive",
        }
    except subprocess.TimeoutExpired as exc:
        events_path.write_text((exc.stdout or ""), encoding="utf-8")
        stderr_path.write_text((exc.stderr or ""), encoding="utf-8")
        return {
            "scenario": name,
            "status": "failed",
            "returncode": None,
            "prompt_sha256": prompt_hash,
            "command": command,
            "answer_path": str(answer_path.relative_to(PRODUCTION_ROOT)),
            "events_path": str(events_path.relative_to(PRODUCTION_ROOT)),
            "stderr_path": str(stderr_path.relative_to(PRODUCTION_ROOT)),
            "answer_excerpt": "",
            "observations": [],
            "skill_paths_observed": [],
            "skill_path_status": "inconclusive",
            "error": f"timed out after {timeout} seconds",
        }
    except OSError as exc:
        return {
            "scenario": name,
            "status": "failed",
            "returncode": None,
            "prompt_sha256": prompt_hash,
            "command": command,
            "answer_path": str(answer_path.relative_to(PRODUCTION_ROOT)),
            "events_path": str(events_path.relative_to(PRODUCTION_ROOT)),
            "stderr_path": str(stderr_path.relative_to(PRODUCTION_ROOT)),
            "answer_excerpt": "",
            "observations": [],
            "skill_paths_observed": [],
            "skill_path_status": "inconclusive",
            "error": str(exc),
        }


def run_scenarios(names: Sequence[str], *, model: str | None = None, timeout: int = 180) -> dict[str, Any]:
    unknown = sorted(set(names) - set(SCENARIO_EXPECTATIONS))
    if unknown:
        raise ValueError(f"unknown scenarios: {', '.join(unknown)}")
    _copy_local_skills()
    _copy_csv_only_fixture()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = PRIVATE_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    results = []
    for name in names:
        scenario_path = SCENARIO_ROOT / f"{name}.md"
        if not scenario_path.is_file():
            results.append({"scenario": name, "status": "failed", "error": f"missing scenario file: {scenario_path}"})
            continue
        prompt = _scenario_prompt(scenario_path)
        prompt += (
            "\n\nSmoke-run constraints: use only the project-local skill copy under "
            "`.agents/skills/` in this workspace. Before answering, read the "
            "relevant skill and directly referenced instructions from that copy; "
            "do not consult or modify a global skill installation. The event log "
            "must retain the exact project-local paths used. Do not use browser, "
            "connector, account, network, or write tools."
        )
        results.append(_run_one(name, prompt, run_dir, model, timeout))
    failed = [result for result in results if result.get("status") != "observed"]
    summary = {
        "schema_version": 1,
        "status": "observed" if not failed else "inconclusive",
        "run_id": run_id,
        "model": model or "configured default",
        "workspace": str(PRIVATE_ROOT),
        "local_skill_copy": str(LOCAL_SKILLS.relative_to(PRODUCTION_ROOT)),
        "run_directory": str(run_dir.relative_to(PRODUCTION_ROOT)),
        "scenarios": results,
        "failed_or_inconclusive": [result.get("scenario") for result in failed],
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run read-only Codex smoke prompts against a project-local copy of Along skills."
    )
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenarios",
        choices=sorted(SCENARIO_EXPECTATIONS),
        help="scenario to run; repeatable (default: all)",
    )
    parser.add_argument("--model", help="optional Codex model override; default uses the configured login")
    parser.add_argument("--timeout", type=int, default=180, help="per-scenario timeout in seconds")
    args = parser.parse_args(argv)
    names = args.scenarios or list(SCENARIO_EXPECTATIONS)
    try:
        result = run_scenarios(names, model=args.model, timeout=args.timeout)
    except (OSError, ValueError, RuntimeError) as exc:
        json.dump({"schema_version": 1, "status": "failed", "error": str(exc)}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 1
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["status"] == "observed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
