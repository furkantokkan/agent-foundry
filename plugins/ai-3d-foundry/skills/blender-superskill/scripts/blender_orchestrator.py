#!/usr/bin/env python3
"""Stepwise Codex orchestrator for reference-driven Blender modeling.

The orchestrator owns the state machine. Codex owns one bounded worker task at a
time: plan, build one step, repair one step, or run the final review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def slugify(value: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return (slug or "blender-task")[:limit].strip("-") or "blender-task"


def read_text_or_value(value: str | None, file_path: str | None) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if value:
        return value
    raise SystemExit("Provide --task or --task-file.")


def default_run_root(workspace: Path) -> Path:
    return workspace / ".codex" / "blender-runs"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def resolve_run_dir(run: str, run_root: Path) -> Path:
    if run == "latest":
        candidates = [p for p in run_root.glob("*") if (p / "state.json").exists()]
        if not candidates:
            raise SystemExit(f"No runs found under {run_root}")
        return max(candidates, key=lambda p: p.stat().st_mtime)
    path = Path(run)
    if path.exists():
        return path.resolve()
    candidate = run_root / run
    if candidate.exists():
        return candidate.resolve()
    raise SystemExit(f"Run not found: {run}")


def load_state(run_dir: Path) -> dict[str, Any]:
    return load_json(run_dir / "state.json")


def save_state(run_dir: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    write_json(run_dir / "state.json", state)


def write_schema(run_dir: Path, phase: str) -> Path:
    schemas = {
        "plan": {
            "type": "object",
            "required": ["status", "view_analysis", "anatomy", "proportions", "steps", "risks"],
            "properties": {
                "status": {"type": "string", "enum": ["ok", "blocked"]},
                "blocker": {"type": "string"},
                "focused_references": {"type": "array", "items": {"type": "string"}},
                "view_analysis": {"type": "object", "additionalProperties": False},
                "anatomy": {"type": "object", "additionalProperties": False},
                "proportions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "target", "evidence"],
                        "properties": {
                            "name": {"type": "string"},
                            "target": {"type": "string"},
                            "evidence": {"type": "string"},
                            "tolerance": {"type": "string"},
                        },
                        "additionalProperties": False,
                    },
                },
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": [
                            "id",
                            "title",
                            "objective",
                            "reference_features",
                            "anchors",
                            "forbidden",
                            "required_inspections",
                            "pass_criteria",
                        ],
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "objective": {"type": "string"},
                            "reference_features": {"type": "array", "items": {"type": "string"}},
                            "anchors": {"type": "array", "items": {"type": "string"}},
                            "forbidden": {"type": "array", "items": {"type": "string"}},
                            "required_inspections": {"type": "array", "items": {"type": "string"}},
                            "pass_criteria": {"type": "array", "items": {"type": "string"}},
                        },
                        "additionalProperties": False,
                    },
                },
                "risks": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        },
        "build": {
            "type": "object",
            "required": [
                "status",
                "step_id",
                "attempt",
                "objects_created",
                "objects_modified",
                "anchors_used",
                "inspections_done",
                "screenshots",
                "reference_comparison",
                "remaining_differences",
                "coverage_updates",
                "next_action",
            ],
            "properties": {
                "status": {"type": "string", "enum": ["pass", "needs_repair", "blocked"]},
                "step_id": {"type": "string"},
                "attempt": {"type": "integer"},
                "objects_created": {"type": "array", "items": {"type": "string"}},
                "objects_modified": {"type": "array", "items": {"type": "string"}},
                "anchors_used": {"type": "array", "items": {"type": "string"}},
                "inspections_done": {"type": "array", "items": {"type": "string"}},
                "screenshots": {"type": "array", "items": {"type": "string"}},
                "reference_comparison": {
                    "type": "object",
                    "required": ["matches", "mismatches", "proportion_checks"],
                    "properties": {
                        "matches": {"type": "array", "items": {"type": "string"}},
                        "mismatches": {"type": "array", "items": {"type": "string"}},
                        "proportion_checks": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
                    },
                    "additionalProperties": False,
                },
                "remaining_differences": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                "coverage_updates": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                "why_acceptable_to_continue": {"type": "string"},
                "next_action": {"type": "string", "enum": ["advance", "retry", "ask_user"]},
            },
            "additionalProperties": False,
        },
        "final_review": {
            "type": "object",
            "required": [
                "status",
                "top_differences",
                "missing_features",
                "repair_steps",
                "final_checks",
                "next_action",
            ],
            "properties": {
                "status": {"type": "string", "enum": ["complete", "needs_repair", "blocked"]},
                "top_differences": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                "missing_features": {"type": "array", "items": {"type": "string"}},
                "repair_steps": {"type": "array", "items": {"type": "object", "additionalProperties": False}},
                "final_checks": {"type": "array", "items": {"type": "string"}},
                "next_action": {"type": "string", "enum": ["complete", "add_repairs", "ask_user"]},
            },
            "additionalProperties": False,
        },
    }
    schema = schemas[phase]
    path = run_dir / "schemas" / f"{phase}.schema.json"
    write_json(path, schema)
    return path


def json_block_from_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise ValueError("empty final message")
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))

    start = stripped.find("{")
    if start == -1:
        raise ValueError("no JSON object found")
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(stripped[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(stripped[start : i + 1])
    raise ValueError("unterminated JSON object")


def validate_plan(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("status") == "blocked":
        return errors
    if result.get("status") != "ok":
        errors.append("plan status must be ok or blocked")
    if not isinstance(result.get("anatomy"), dict) or not result["anatomy"]:
        errors.append("plan must include a non-empty anatomy object")
    if not isinstance(result.get("proportions"), list) or len(result["proportions"]) < 3:
        errors.append("plan must include at least three proportion estimates")
    steps = result.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("plan must include at least one construction step")
    else:
        for index, step in enumerate(steps, start=1):
            for key in ("id", "title", "objective", "reference_features", "required_inspections", "pass_criteria"):
                if key not in step or step[key] in ("", [], None):
                    errors.append(f"step {index} is missing {key}")
    return errors


def validate_build(result: dict[str, Any], expected_step_id: str) -> list[str]:
    errors: list[str] = []
    if result.get("step_id") != expected_step_id:
        errors.append(f"result step_id must be {expected_step_id}")
    if result.get("status") not in {"pass", "needs_repair", "blocked"}:
        errors.append("status must be pass, needs_repair, or blocked")
    if result.get("next_action") not in {"advance", "retry", "ask_user"}:
        errors.append("next_action must be advance, retry, or ask_user")
    if not isinstance(result.get("anchors_used"), list):
        errors.append("anchors_used must be a list")
    if not result.get("inspections_done"):
        errors.append("inspections_done must not be empty")
    if not result.get("screenshots"):
        errors.append("screenshots must not be empty")
    comparison = result.get("reference_comparison")
    if not isinstance(comparison, dict):
        errors.append("reference_comparison must be an object")
    else:
        for key in ("matches", "mismatches", "proportion_checks"):
            if key not in comparison:
                errors.append(f"reference_comparison is missing {key}")
    if "remaining_differences" not in result:
        errors.append("remaining_differences must be present")
    if result.get("status") == "pass" and not result.get("remaining_differences") and not result.get("why_acceptable_to_continue"):
        errors.append("pass with no remaining_differences requires why_acceptable_to_continue")
    return errors


def validate_final_review(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("status") not in {"complete", "needs_repair", "blocked"}:
        errors.append("status must be complete, needs_repair, or blocked")
    if result.get("next_action") not in {"complete", "add_repairs", "ask_user"}:
        errors.append("next_action must be complete, add_repairs, or ask_user")
    for key in ("top_differences", "missing_features", "repair_steps", "final_checks"):
        if key not in result:
            errors.append(f"final review is missing {key}")
    if result.get("status") == "complete" and not result.get("top_differences"):
        errors.append("complete final review must still list inspected differences, even if minor")
    return errors


def summarize_completed_steps(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": item.get("step_id"),
            "title": item.get("title"),
            "status": item.get("status"),
            "objects_created": item.get("objects_created", []),
            "objects_modified": item.get("objects_modified", []),
            "remaining_differences": item.get("remaining_differences", []),
        }
        for item in state.get("completed_steps", [])
    ]


def planning_prompt(state: dict[str, Any], run_dir: Path) -> str:
    return (
        "You are the planning worker for one orchestrated Blender reference-modeling run.\n"
        "Do not run blender_orchestrator.py. Do not create Blender geometry in this step.\n\n"
        "Task:\n"
        f"{state['task']}\n\n"
        "Reference files:\n"
        f"{json.dumps(state['references'], indent=2)}\n\n"
        "Run directory:\n"
        f"{run_dir}\n\n"
        "Required behavior:\n"
        "- Inspect the reference before planning.\n"
        "- If the target object is small or buried in a busy scene, create or request a focused crop and list it in focused_references.\n"
        "- Build an anatomy inventory of visible parts. For buildings include masses, roof parts, openings, facade details, signs, site/base parts, and repeated patterns.\n"
        "- Estimate proportions as ratios or fractions from the reference. Include evidence, not just guesses.\n"
        "- Convert the anatomy into ordered construction steps.\n"
        "- Each step must build only one visible unit or one tightly related module.\n"
        "- Each step must include reference_features, anchors, forbidden additions, required_inspections, and pass_criteria.\n"
        "- Include specific inspection views such as front orthographic, side, top, close-up contact, or six-side inspection where relevant.\n\n"
        "Return JSON only. The JSON must match the output schema supplied by the caller."
    )


def build_prompt(state: dict[str, Any], run_dir: Path) -> str:
    plan = state["plan"]
    step = plan["steps"][state["current_step_index"]]
    last_errors = state.get("last_validation_errors", [])
    last_result = state.get("last_result_summary")
    attempt = state.get("current_attempt", 1)
    mode = "repair" if attempt > 1 or last_result else "build"

    return (
        "You are the single-step Blender worker for an orchestrated reference-modeling run.\n"
        "Do not run blender_orchestrator.py. Do not advance to another step. Do not add extra details.\n\n"
        "Task:\n"
        f"{state['task']}\n\n"
        "Reference files:\n"
        f"{json.dumps(state['references'], indent=2)}\n\n"
        "Run directory:\n"
        f"{run_dir}\n\n"
        "Mode:\n"
        f"{mode}\n\n"
        "Current step:\n"
        f"{json.dumps(step, indent=2)}\n\n"
        "Attempt:\n"
        f"{attempt}\n\n"
        "Full anatomy checklist:\n"
        f"{json.dumps(plan.get('anatomy', {}), indent=2)}\n\n"
        "Proportion targets:\n"
        f"{json.dumps(plan.get('proportions', []), indent=2)}\n\n"
        "Completed steps summary:\n"
        f"{json.dumps(summarize_completed_steps(state), indent=2)}\n\n"
        "Previous validation errors to fix before this step can advance:\n"
        f"{json.dumps(last_errors, indent=2)}\n\n"
        "Previous result summary:\n"
        f"{json.dumps(last_result, indent=2)}\n\n"
        "Required behavior:\n"
        "- Inspect the reference again before touching Blender.\n"
        "- State internally what existing face, edge, object, socket, or plane anchors this step.\n"
        "- Build or repair only the current step.\n"
        "- Derive placement from existing dimensions, bounding boxes, face centers, or named anchors.\n"
        "- Do not create preview cameras. Use viewport inspection.\n"
        "- Use Solid viewport shading for form/proportion inspection.\n"
        "- Capture or record the required inspection views for this step.\n"
        "- Compare the result back to the reference after building.\n"
        "- Include mismatches and remaining differences even if you decide the step can advance.\n"
        "- If there are material proportion/detail issues, set status to needs_repair and next_action to retry.\n"
        "- If blocked by an ambiguous reference or unavailable tool, set status to blocked and next_action to ask_user.\n\n"
        "Return JSON only. The JSON must match the output schema supplied by the caller."
    )


def final_review_prompt(state: dict[str, Any], run_dir: Path) -> str:
    return (
        "You are the final review worker for an orchestrated Blender reference-modeling run.\n"
        "Do not run blender_orchestrator.py. Do not add or modify geometry unless asked in a later repair step.\n\n"
        "Task:\n"
        f"{state['task']}\n\n"
        "Reference files:\n"
        f"{json.dumps(state['references'], indent=2)}\n\n"
        "Run directory:\n"
        f"{run_dir}\n\n"
        "Anatomy checklist:\n"
        f"{json.dumps(state['plan'].get('anatomy', {}), indent=2)}\n\n"
        "Proportion targets:\n"
        f"{json.dumps(state['plan'].get('proportions', []), indent=2)}\n\n"
        "Completed steps:\n"
        f"{json.dumps(summarize_completed_steps(state), indent=2)}\n\n"
        "Required behavior:\n"
        "- Inspect the model from front, back, left, right, top, bottom/underside, and the reference-matching angle.\n"
        "- Compare silhouette, major proportions, detail count, repeated pattern spacing, roof shape, openings, anchors, and missing parts against the reference.\n"
        "- Assume the model is worse than it first appears. Look for the top differences instead of praising the result.\n"
        "- If important visible differences remain, return needs_repair and propose repair_steps.\n"
        "- Each repair step must be bounded, specific, and safe to insert after the existing plan.\n"
        "- If complete, still list the inspected differences and explain why they are minor or acceptable in final_checks.\n\n"
        "Return JSON only. The JSON must match the output schema supplied by the caller."
    )


def prompt_for_state(state: dict[str, Any], run_dir: Path) -> tuple[str, str]:
    phase = state["phase"]
    if phase == "plan":
        return "plan", planning_prompt(state, run_dir)
    if phase == "build":
        return "build", build_prompt(state, run_dir)
    if phase == "final_review":
        return "final_review", final_review_prompt(state, run_dir)
    raise SystemExit(f"Run is not executable in phase: {phase}")


def image_args(references: list[str]) -> list[str]:
    args: list[str] = []
    for ref in references:
        path = Path(ref)
        if path.exists() and path.suffix.lower() in IMAGE_SUFFIXES:
            args.extend(["-i", str(path.resolve())])
    return args


def run_codex_worker(
    run_dir: Path,
    state: dict[str, Any],
    workspace: Path,
    model: str | None,
    extra_codex_args: list[str],
    poll_seconds: int,
) -> tuple[int, Path, Path]:
    phase, prompt = prompt_for_state(state, run_dir)
    prompt_dir = run_dir / "prompts"
    result_dir = run_dir / "step-results"
    log_dir = run_dir / "logs"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    serial = len(state.get("history", [])) + 1
    step_part = phase
    if phase == "build":
        step = state["plan"]["steps"][state["current_step_index"]]
        step_part = f"{step['id']}-attempt-{state.get('current_attempt', 1)}"
    stamp = f"{serial:03d}-{step_part}"
    prompt_path = prompt_dir / f"{stamp}.txt"
    final_path = result_dir / f"{stamp}.json"
    log_path = log_dir / f"{stamp}.log"
    schema_path = write_schema(run_dir, phase)
    prompt_path.write_text(prompt + "\n", encoding="utf-8")

    codex_executable = shutil.which("codex.cmd") if os.name == "nt" else None
    codex_executable = codex_executable or shutil.which("codex") or "codex"

    command = [
        codex_executable,
        "exec",
        "-C",
        str(workspace),
        "--full-auto",
        "--skip-git-repo-check",
        "-o",
        str(final_path),
    ]
    if model:
        command.extend(["-m", model])
    command.extend(image_args(state.get("references", [])))
    command.extend(extra_codex_args)
    command.append("-")

    print(f"[orchestrator] running {stamp}")
    print(f"[orchestrator] prompt: {prompt_path}")
    print(f"[orchestrator] final:  {final_path}")

    started = time.monotonic()
    with prompt_path.open("rb") as stdin, log_path.open("wb") as log:
        process = subprocess.Popen(command, stdin=stdin, stdout=log, stderr=subprocess.STDOUT)
        while True:
            code = process.poll()
            if code is not None:
                return code, final_path, log_path
            if poll_seconds > 0:
                elapsed = int(time.monotonic() - started)
                print(f"[orchestrator] worker still running after {elapsed}s")
                time.sleep(poll_seconds)
            else:
                time.sleep(1)


def apply_result(run_dir: Path, state: dict[str, Any], final_path: Path, log_path: Path, return_code: int) -> dict[str, Any]:
    phase = state["phase"]
    history_item: dict[str, Any] = {
        "time": now_iso(),
        "phase": phase,
        "return_code": return_code,
        "result_path": str(final_path),
        "log_path": str(log_path),
    }

    if return_code != 0:
        history_item["status"] = "worker_failed"
        state.setdefault("history", []).append(history_item)
        state["last_validation_errors"] = [f"codex worker exited with code {return_code}; see {log_path}"]
        return state

    try:
        result = json_block_from_text(final_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        history_item["status"] = "parse_failed"
        state.setdefault("history", []).append(history_item)
        state["last_validation_errors"] = [f"could not parse worker JSON: {exc}"]
        return state

    history_item["worker_status"] = result.get("status")

    if phase == "plan":
        errors = validate_plan(result)
        history_item["validation_errors"] = errors
        if errors:
            state["current_attempt"] = state.get("current_attempt", 1) + 1
            state["last_validation_errors"] = errors
            state["last_result_summary"] = result
        elif result.get("status") == "blocked":
            state["phase"] = "blocked"
            state["blocker"] = result.get("blocker", "planning worker blocked")
        else:
            state["plan"] = result
            write_json(run_dir / "plan.json", result)
            state["phase"] = "build"
            state["current_step_index"] = 0
            state["current_attempt"] = 1
            state["completed_steps"] = []
            state["last_validation_errors"] = []
            state["last_result_summary"] = None

    elif phase == "build":
        step = state["plan"]["steps"][state["current_step_index"]]
        expected_step_id = step["id"]
        errors = validate_build(result, expected_step_id)
        history_item["step_id"] = expected_step_id
        history_item["validation_errors"] = errors

        retry = errors or result.get("status") == "needs_repair" or result.get("next_action") == "retry"
        blocked = result.get("status") == "blocked" or result.get("next_action") == "ask_user"
        if blocked:
            state["phase"] = "blocked"
            state["blocker"] = result.get("blocker", "build worker blocked")
            state["last_result_summary"] = result
            state["last_validation_errors"] = errors
        elif retry:
            state["current_attempt"] = state.get("current_attempt", 1) + 1
            state["last_result_summary"] = result
            state["last_validation_errors"] = errors or result.get("reference_comparison", {}).get("mismatches", [])
            if state["current_attempt"] > state.get("max_retries_per_step", 3):
                state["phase"] = "blocked"
                state["blocker"] = f"{expected_step_id} exceeded max retries"
        else:
            completed = {
                "step_id": expected_step_id,
                "title": step.get("title"),
                "status": result.get("status"),
                "objects_created": result.get("objects_created", []),
                "objects_modified": result.get("objects_modified", []),
                "anchors_used": result.get("anchors_used", []),
                "remaining_differences": result.get("remaining_differences", []),
                "result_path": str(final_path),
            }
            state.setdefault("completed_steps", []).append(completed)
            state["current_step_index"] += 1
            state["current_attempt"] = 1
            state["last_validation_errors"] = []
            state["last_result_summary"] = None
            if state["current_step_index"] >= len(state["plan"]["steps"]):
                state["phase"] = "final_review"

    elif phase == "final_review":
        errors = validate_final_review(result)
        history_item["validation_errors"] = errors
        if errors:
            state["current_attempt"] = state.get("current_attempt", 1) + 1
            state["last_validation_errors"] = errors
            state["last_result_summary"] = result
        elif result.get("status") == "blocked" or result.get("next_action") == "ask_user":
            state["phase"] = "blocked"
            state["blocker"] = result.get("blocker", "final review blocked")
            state["last_result_summary"] = result
        elif result.get("status") == "needs_repair" or result.get("next_action") == "add_repairs":
            repairs = result.get("repair_steps", [])
            if not repairs:
                state["phase"] = "blocked"
                state["blocker"] = "final review requested repair but provided no repair_steps"
            else:
                start = len(state["plan"]["steps"]) + 1
                normalized = []
                for offset, repair in enumerate(repairs):
                    normalized.append(
                        {
                            "id": repair.get("id") or f"R{start + offset:02d}",
                            "title": repair.get("title") or repair.get("issue") or f"Repair {start + offset}",
                            "objective": repair.get("objective") or repair.get("fix") or json.dumps(repair),
                            "reference_features": repair.get("reference_features", repair.get("evidence", [])),
                            "anchors": repair.get("anchors", []),
                            "forbidden": repair.get("forbidden", ["unrelated new details"]),
                            "required_inspections": repair.get("required_inspections", ["reference-matching view", "close-up repaired area"]),
                            "pass_criteria": repair.get("pass_criteria", ["visible mismatch is reduced without harming completed geometry"]),
                        }
                    )
                state["plan"]["steps"].extend(normalized)
                write_json(run_dir / "plan.json", state["plan"])
                state["phase"] = "build"
                state["current_step_index"] = len(state["plan"]["steps"]) - len(normalized)
                state["current_attempt"] = 1
                state["last_validation_errors"] = []
                state["last_result_summary"] = None
        else:
            state["phase"] = "complete"
            state["final_review"] = result
            state["last_validation_errors"] = []
            state["last_result_summary"] = None

    state.setdefault("history", []).append(history_item)
    return state


def cmd_init(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    run_root = Path(args.run_root).resolve() if args.run_root else default_run_root(workspace)
    task = read_text_or_value(args.task, args.task_file).strip()
    run_id = args.name or f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(task)}"
    run_dir = (run_root / run_id).resolve()
    if run_dir.exists() and not args.force:
        raise SystemExit(f"Run already exists: {run_dir}. Use --force to overwrite.")
    if run_dir.exists():
        shutil.rmtree(run_dir)
    for child in ("prompts", "step-results", "logs", "schemas", "screenshots", "references"):
        (run_dir / child).mkdir(parents=True, exist_ok=True)

    references: list[str] = []
    for ref in args.reference:
        ref_path = Path(ref)
        if ref_path.exists():
            references.append(str(ref_path.resolve()))
        else:
            references.append(ref)

    state = {
        "schema_version": SCHEMA_VERSION,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "task": task,
        "references": references,
        "workspace": str(workspace),
        "run_dir": str(run_dir),
        "phase": "plan",
        "plan": None,
        "current_step_index": None,
        "current_attempt": 1,
        "max_retries_per_step": args.max_retries_per_step,
        "completed_steps": [],
        "history": [],
        "last_validation_errors": [],
        "last_result_summary": None,
    }
    save_state(run_dir, state)
    print(run_dir)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    run_root = Path(args.run_root).resolve() if args.run_root else default_run_root(Path(args.workspace).resolve())
    run_dir = resolve_run_dir(args.run, run_root)
    state = load_state(run_dir)
    print(json.dumps({
        "run_dir": str(run_dir),
        "phase": state.get("phase"),
        "current_step_index": state.get("current_step_index"),
        "current_attempt": state.get("current_attempt"),
        "completed_steps": len(state.get("completed_steps", [])),
        "total_steps": len((state.get("plan") or {}).get("steps", [])),
        "last_validation_errors": state.get("last_validation_errors", []),
        "blocker": state.get("blocker"),
    }, indent=2))
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    run_root = Path(args.run_root).resolve() if args.run_root else default_run_root(Path(args.workspace).resolve())
    run_dir = resolve_run_dir(args.run, run_root)
    state = load_state(run_dir)
    _, prompt = prompt_for_state(state, run_dir)
    print(prompt)
    return 0


def cmd_run_step(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    run_root = Path(args.run_root).resolve() if args.run_root else default_run_root(workspace)
    run_dir = resolve_run_dir(args.run, run_root)
    state = load_state(run_dir)
    if state.get("phase") in {"complete", "blocked"}:
        print(f"[orchestrator] run is {state.get('phase')}")
        return 0 if state.get("phase") == "complete" else 2
    return_code, final_path, log_path = run_codex_worker(
        run_dir=run_dir,
        state=state,
        workspace=workspace,
        model=args.model,
        extra_codex_args=args.codex_arg,
        poll_seconds=args.poll_seconds,
    )
    state = apply_result(run_dir, state, final_path, log_path, return_code)
    save_state(run_dir, state)
    print(f"[orchestrator] phase: {state.get('phase')}")
    if state.get("last_validation_errors"):
        print("[orchestrator] validation errors:")
        for error in state["last_validation_errors"]:
            print(f"  - {error}")
    if state.get("blocker"):
        print(f"[orchestrator] blocker: {state['blocker']}")
    return 0 if state.get("phase") != "blocked" else 2


def cmd_continue(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve()
    run_root = Path(args.run_root).resolve() if args.run_root else default_run_root(workspace)
    run_dir = resolve_run_dir(args.run, run_root)
    for _ in range(args.max_worker_runs):
        state = load_state(run_dir)
        if state.get("phase") == "complete":
            print("[orchestrator] complete")
            return 0
        if state.get("phase") == "blocked":
            print(f"[orchestrator] blocked: {state.get('blocker')}")
            return 2
        step_args = argparse.Namespace(
            workspace=str(workspace),
            run_root=str(run_root),
            run=str(run_dir),
            model=args.model,
            codex_arg=args.codex_arg,
            poll_seconds=args.poll_seconds,
        )
        code = cmd_run_step(step_args)
        if code != 0:
            return code
    print(f"[orchestrator] stopped after {args.max_worker_runs} worker runs")
    return 1


def cmd_run(args: argparse.Namespace) -> int:
    init_args = argparse.Namespace(
        workspace=args.workspace,
        run_root=args.run_root,
        task=args.task,
        task_file=args.task_file,
        reference=args.reference,
        name=args.name,
        force=args.force,
        max_retries_per_step=args.max_retries_per_step,
    )
    cmd_init(init_args)
    workspace = Path(args.workspace).resolve()
    run_root = Path(args.run_root).resolve() if args.run_root else default_run_root(workspace)
    run_dir = resolve_run_dir(args.name or "latest", run_root)
    cont_args = argparse.Namespace(
        workspace=str(workspace),
        run_root=str(run_root),
        run=str(run_dir),
        model=args.model,
        codex_arg=args.codex_arg,
        poll_seconds=args.poll_seconds,
        max_worker_runs=args.max_worker_runs,
    )
    return cmd_continue(cont_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orchestrate stepwise Codex workers for Blender reference modeling.")
    parser.add_argument("--workspace", default=os.getcwd(), help="Workspace/repo for codex exec. Defaults to current directory.")
    parser.add_argument("--run-root", default=None, help="Directory that stores orchestrated runs. Defaults to <workspace>/.codex/blender-runs.")

    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a run directory and state file.")
    init.add_argument("--task", default=None)
    init.add_argument("--task-file", default=None)
    init.add_argument("--reference", action="append", default=[])
    init.add_argument("--name", default=None)
    init.add_argument("--force", action="store_true")
    init.add_argument("--max-retries-per-step", type=int, default=3)
    init.set_defaults(func=cmd_init)

    status = sub.add_parser("status", help="Print compact run status.")
    status.add_argument("run", nargs="?", default="latest")
    status.set_defaults(func=cmd_status)

    prompt = sub.add_parser("prompt", help="Print the prompt for the current phase without running Codex.")
    prompt.add_argument("run", nargs="?", default="latest")
    prompt.set_defaults(func=cmd_prompt)

    run_step = sub.add_parser("run-step", help="Run exactly one Codex worker step.")
    run_step.add_argument("run", nargs="?", default="latest")
    run_step.add_argument("--model", default=None)
    run_step.add_argument("--poll-seconds", type=int, default=10)
    run_step.add_argument("--codex-arg", action="append", default=[], help="Additional raw argument passed to codex exec. Repeat as needed.")
    run_step.set_defaults(func=cmd_run_step)

    cont = sub.add_parser("continue", help="Run workers until complete, blocked, or max-worker-runs is reached.")
    cont.add_argument("run", nargs="?", default="latest")
    cont.add_argument("--model", default=None)
    cont.add_argument("--poll-seconds", type=int, default=10)
    cont.add_argument("--max-worker-runs", type=int, default=50)
    cont.add_argument("--codex-arg", action="append", default=[], help="Additional raw argument passed to codex exec. Repeat as needed.")
    cont.set_defaults(func=cmd_continue)

    run = sub.add_parser("run", help="Initialize and continue a run.")
    run.add_argument("--task", default=None)
    run.add_argument("--task-file", default=None)
    run.add_argument("--reference", action="append", default=[])
    run.add_argument("--name", default=None)
    run.add_argument("--force", action="store_true")
    run.add_argument("--max-retries-per-step", type=int, default=3)
    run.add_argument("--model", default=None)
    run.add_argument("--poll-seconds", type=int, default=10)
    run.add_argument("--max-worker-runs", type=int, default=50)
    run.add_argument("--codex-arg", action="append", default=[], help="Additional raw argument passed to codex exec. Repeat as needed.")
    run.set_defaults(func=cmd_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
