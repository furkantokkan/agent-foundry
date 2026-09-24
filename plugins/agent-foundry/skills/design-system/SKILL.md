---
name: design-system
model: opus
effort: high
description: >-
  Guided, section-by-section GDD authoring for a single game system. Gathers context from existing docs, walks through each required section collaboratively, cross-references dependencies, and writes incrementally to file.
---

# Design System

Codex port of Claude Code Game Studios /design-system.

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

Guided, section-by-section GDD authoring for a single game system. Gathers context from existing docs, walks through each required section collaboratively, cross-references dependencies, and writes incrementally to file.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
