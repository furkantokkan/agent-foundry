---
name: team-qa
description: >-
  Orchestrate an evidence-backed QA cycle for tracked tasks, a sprint, or a feature. Route failures to task-bug, bug-report, or create-task without duplicating defect ownership.
---

# Team Qa

Codex port of Claude Code Game Studios /team-qa.

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
5. QA does not implement failures directly. Route tracked-task feedback through
   `task-bug`, unowned report-only backlog findings through `bug-report`, and an
   unowned bounded repair request through `create-task`.
6. Verify only QA documentation and evidence produced by this workflow;
   downstream repair verification belongs to `task-cycle`/`implement-task`.

## Defect Routing

Before creating any standalone QA bug artifact, resolve ownership from the exact
task contract, acceptance/preservation rules, handoff, changed systems, and
defect ledger. Include closed tasks.

- Exact tracked owner: record `$task-bug <ID> "<raw failure>"`.
- No owner plus capture/triage intent: use `$bug-report "<raw failure>"`.
- No owner plus bounded repair intent: use `$create-task "<observable fix>"`.
- Several plausible owners: ask one identity question and perform zero defect,
  bug, or repair-task writes.

Never create both a task-linked defect and
`production/qa/bugs/BUG-*.md` for the same observation. QA records repair routes
but does not invoke production mutation automatically.

## Original Workflow Summary

Orchestrate the QA team through a full testing cycle using task contracts as the
canonical scope. Produce strategy, tests, evidence routing, and sign-off without
turning QA reports into a second task lifecycle.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
