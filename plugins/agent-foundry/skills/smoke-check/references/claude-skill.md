---
name: smoke-check
description: "Run critical Unity compilation, EditMode, PlayMode, console, and task-evidence checks for tracked tasks, a feature, sprint, or release candidate."
argument-hint: "[feature | sprint | release] [--record]"
user-invocable: true
allowed-tools: Read Glob Grep Bash Write
model: sonnet
---

# Unity Smoke Check

This is a verification workflow. It does not fix production code or mutate
Unity serialized assets.

## Phase 1 — Resolve Scope and Baseline

Read canonical `production/tasks/<TASK-ID>/contract.md` files for the requested
task/feature/sprint, their acceptance criteria, preserved behavior, defect
ledgers, and evidence paths, plus Unity architecture, automation, and ownership
rules. Legacy story files are references only when no canonical contract exists.
Record the current commit and `git status`. If unrelated dirty state prevents a
reliable diff, return `BLOCKED` with the exact conflict.

Expected test locations are `Assets/Tests/EditMode/**`,
`Assets/Tests/PlayMode/**`, or documented feature-local Unity test assemblies.

## Phase 2 — Connect to the Correct Unity Project

Use the installed Unity CLI first and prove the exact target with
`unity status --json` plus `--project-path`. If CLI/Pipeline is unavailable or
insufficient, use matching Unity MCP, then matching UnitySkills. If no runner can
produce compiler/test evidence, return `BLOCKED`; do not infer success.

## Phase 3 — Run Critical Checks

1. Import/compile the project and capture the editor log.
2. Run the scope's required EditMode tests and retain NUnit XML.
3. Run required PlayMode tests and retain NUnit XML.
4. Query the Unity Console after the run; report new errors/exceptions.
5. For each Logic/Integration task, map every acceptance criterion to an
   executed test or a clearly identified manual evidence item.
6. Check expected asmdef dependencies and flag runtime-to-test/editor references.
7. Confirm no unexpected scene, prefab, ScriptableObject, Input Actions,
   Addressables, package, or project-setting diff was introduced during checking.

## Phase 4 — Coverage Report

```text
| Task / criterion | Evidence | Result |
|---|---|---|
| [task / AC] | Assets/Tests/EditMode/[System]/[Name]Tests.cs + XML | PASS |
| [task / AC] | Assets/Tests/PlayMode/[System]/[Name]Tests.cs + XML | PASS |
| [task / AC] | production/qa/evidence/[slug].md | MANUAL |
```

Missing executable evidence for a blocking Logic/Integration criterion is a
failure, not a warning.

## Phase 5 — Verdict and Optional Record

- `PASS`: compilation, required tests, console, and coverage gates pass.
- `PASS WITH CONCERNS`: executable gates pass; only advisory/manual evidence remains.
- `FAIL`: compiler error, test failure, blocking evidence gap, assembly violation,
  or unexpected serialized/project change.
- `BLOCKED`: no valid runner, wrong project connection, or invalid baseline.

Without `--record`, return the report only. With `--record`, writing one report
under `production/qa/` is the approved low-risk output. Do not modify product
files or test results to make the check pass.

Preserve every reproducible failure with its exact task/criterion, build,
revision, runner, log/XML path, expected result, and actual result. This
verification workflow does not invoke repair:

- One exact active or closed task owns the failure: record
  `/task-bug <TASK-ID> "<raw failure evidence>"` and do not create a standalone
  QA bug.
- No task owns it and the operator wants backlog capture: record `/bug-report`.
- No task owns it and the operator wants bounded repair: record `/create-task`.
- Ownership is ambiguous: report `TASK MATCH AMBIGUOUS`, list candidates, and
  allocate nothing.

When all blocking evidence passes, use `/task-done <TASK-ID>` only for a task
that is already `READY_TO_CLOSE`; smoke success alone never closes it.
