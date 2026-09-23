---
name: skill-improve
description: >-
  Improve one skill with a predictable scoped test-fix-retest loop. Diagnose completion, routing, invocation, duplication, and instruction hygiene as well as structural checks; apply only when explicitly requested.
---

# Skill Improve

Codex port of Claude Code Game Studios /skill-improve.

Use this skill for one named skill at a time. Load
`references/claude-skill.md` when the original static, category, or spec rubric
is available in the host. Do not treat a passing structural check as proof that
the instructions work in a real scenario.

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

## Scoped improvement loop

1. Record the target skill's current text and its single purpose, trigger,
   allowed output, writer, completion condition, and stop conditions.
2. Establish a baseline with `skill-test` when available. Trace one ordinary
   request, one missing-context case, one repeated invocation, and one
   out-of-scope request. Record actual ambiguity or failure; do not invent a
   failing score to justify an edit.
3. Inspect a proposed public source's full skill, license, required tools, and
   overlap before adapting it. Prefer a small local pattern to a copied
   competing workflow. Credit retained third-party material.
4. Edit only the named skill and its necessary bundled references within the
   authorized repository scope. Resolve contradictions and duplicate authority
   before adding instructions. Keep the entry point concise and move optional
   detail into a reference.
5. Recheck the same four traces and available structural checks after the edit.
   Keep the change only if it improves the observed issue without a new failure
   or wider write authority. Report before/after evidence and any runtime
   behavior that was not exercised.

When invoked in analysis-only mode, stop after diagnosis and a concrete
proposed patch. A user's direct request to improve the skill authorizes the
scoped edit; no extra `--apply` phrase is required. Follow repository and host
approval rules for changes outside that scope.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
