---
name: create-stories
description: >-
  Legacy-only workflow that breaks an epic into separate story files when a repository explicitly retains the old epic/story pipeline. Do not use in the canonical task-first workflow, where create-task already produces the implementable and closable contract.
---

# Create Stories

This is a compatibility workflow, not a canonical daily command. If repository
instructions select the task-first model, do not create story files. Explain
that each independently closable outcome should be created directly with
`create-task`, optionally referencing an epic grouping document.

Codex port of Claude Code Game Studios /create-stories.

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

## Original Workflow Summary

For an explicitly legacy repository only, break a single epic into implementable
story files using the existing GDD, ADR, and control-manifest traceability.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
