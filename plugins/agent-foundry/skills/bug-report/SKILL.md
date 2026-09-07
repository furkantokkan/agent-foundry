---
name: bug-report
description: >-
  Creates a structured bug report from a description, or analyzes code to identify potential bugs. Ensures every bug report has full reproduction steps, severity assessment, and context.
---

# Bug Report

Codex port of Claude Code Game Studios /bug-report.

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
5. For implementation tasks, make the change directly when the request is clear;
   ask only when a decision cannot be safely inferred from local context.
6. Verify with the repository's available checks and summarize changed files,
   tests run, and residual risk.

Before filing `production/qa/bugs/BUG-*.md`, search tracked task contracts by
exact ID and by objective, acceptance, preserved behavior, and managed defect
ledger. A failure of an existing task's acceptance/preservation or a regression
caused by that task must be forwarded internally to `$task-bug [<ID>]
"<feedback>"`; do not create a standalone QA bug file. `task-bug` resolves the
owner and `task-cycle` is the sole writer of linked same-task defect records and
ledger state. Ask one identity question only when several
task contracts plausibly own the observation. Continue the standalone report
workflow only for an unrelated pre-existing defect or a bug without a tracked
task owner, and only when the operator is intentionally capturing/triaging a
backlog report. If the operator requested a bounded repair instead, stop
`NO_TASK_MATCH` and suggest `$create-task "<observable fix>"`; do not silently
replace repair execution with a QA report.

## Original Workflow Summary

Creates a structured bug report from a description, or analyzes code to identify potential bugs. Ensures every bug report has full reproduction steps, severity assessment, and context.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
