---
name: soak-test
description: >-
  Generate a soak test protocol for extended play sessions. Defines what to observe, measure, and log during long play sessions to surface slow leaks, fatigue effects, and edge cases that only appear after sustained play. Primarily used in Polish and Release phases.
---

# Soak Test

Codex port of Claude Code Game Studios /soak-test.

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
5. This skill generates an observation protocol; it does not implement issues
   found during the later human soak session.
6. Route a task-owned observation to `task-bug`, unowned backlog capture to
   `bug-report`, and an unowned bounded repair request to `create-task`.

## Defect Routing

- Exact active or closed task owner: record `$task-bug <ID> "<raw evidence>"`.
- No owner plus backlog intent: record `$bug-report "<raw evidence>"`.
- No owner plus bounded repair intent: record `$create-task "<observable fix>"`.
- Several plausible owners: report `TASK MATCH AMBIGUOUS` and allocate nothing.

`SOAK-xxx` remains an observation ID in the aggregate protocol, not a second
canonical bug store. The protocol skill does not invoke repair.

## Original Workflow Summary

Generate a soak test protocol for extended play sessions. Defines what to observe, measure, and log during long play sessions to surface slow leaks, fatigue effects, and edge cases that only appear after sustained play. Primarily used in Polish and Release phases.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
