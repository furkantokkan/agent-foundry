---
name: smoke-check
description: >-
  Run the critical path smoke test gate before QA hand-off. Executes the automated test suite, verifies core functionality, and produces a PASS/FAIL report. Run after a sprint's stories are implemented and before manual QA begins. A failed smoke check means the build is not ready for QA.
---

# Smoke Check

Codex port of Claude Code Game Studios /smoke-check.

Use this skill when the task matches the workflow described below. Keep the
Codex version lightweight: load `references/claude-skill.md` only when the
original detailed Claude workflow is needed.

## Codex Workflow

1. Read repository-local instructions first: `AGENTS.md`, `CLAUDE.md`, the
   nearest path-scoped instructions (`Assets/CLAUDE.md` for Unity when present),
   and any referenced project docs.
2. Use this workflow's intent, but follow Codex tool and collaboration rules.
3. Apply SOLID, Clean Code, clear English naming, dependency boundaries, and
   focused tests for new or changed expected behavior.
4. When a Claude workflow mentions a custom agent, treat it as a role reference.
   Do the work locally unless the user explicitly asks for sub-agents or
   parallel agent work.
5. This is verification-only. Never repair production code or task lifecycle
   state from smoke-check.
6. Route an owned failure to `task-bug`, an unowned report-only finding to
   `bug-report`, and an unowned bounded repair request to `create-task`.

## Defect Routing

- Exact active or closed task owner: record `$task-bug <ID> "<raw evidence>"`.
- No owner plus backlog intent: record `$bug-report "<raw evidence>"`.
- No owner plus bounded repair intent: record `$create-task "<observable fix>"`.
- Several plausible owners: report `TASK MATCH AMBIGUOUS` and allocate nothing.

Smoke-check does not invoke repair. Passing evidence can support `$task-done`
only after the task is already `READY_TO_CLOSE`.

## Original Workflow Summary

Run the critical path smoke test gate before QA hand-off. Executes the automated test suite, verifies core functionality, and produces a PASS/FAIL report. Run after a sprint's stories are implemented and before manual QA begins. A failed smoke check means the build is not ready for QA.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
