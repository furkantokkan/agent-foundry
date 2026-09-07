---
name: playtest-report
description: >-
  Generates a structured playtest report template or analyzes existing playtest notes into a structured format. Use this to standardize playtest feedback collection and analysis.
---

# Playtest Report

Codex port of Claude Code Game Studios /playtest-report.

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
5. Do not implement playtest findings directly. Route each reproducible defect
   by ownership and operator intent: tracked-task feedback to `task-bug`, an
   unowned report-only backlog item to `bug-report`, and an unowned bounded
   repair request to `create-task`.
6. This workflow changes only the declared playtest report. Downstream repair
   and verification belong to `task-cycle` and `implement-task`.

## Defect Routing

- One exact active or closed task owns the failed behavior: record
  `$task-bug <ID> "<raw observation>"`; do not create a standalone QA bug.
- No owner and capture/triage intent: record `$bug-report "<observation>"`.
- No owner and bounded repair intent: record `$create-task "<observable fix>"`.
- Several plausible owners: ask one identity question and perform no defect,
  bug, or repair-task write.

The detailed reference is canonical for dedupe, linked records, and report
format. This reporting skill does not invoke the repair command automatically.

## Original Workflow Summary

Generates a structured playtest report template or analyzes existing playtest notes into a structured format. Use this to standardize playtest feedback collection and analysis.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
