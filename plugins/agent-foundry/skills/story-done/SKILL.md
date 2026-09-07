---
name: story-done
description: Backward-compatible alias for task-done when given a task ID or task contract path, plus the legacy completion review for an explicit story file. Use only for compatibility; canonical tracked-task closure is $task-done.
---

# Story Done (Compatibility)

Codex port of Claude Code Game Studios /story-done.

Canonical task usage is now:

```text
$task-done GAME-202
```

Resolve a complete task ID only as `production/tasks/<ID>/contract.md`; never
guess by partial ID or similarly named story. An exact task contract path is
also valid. Preserve an explicit story-file path for the legacy story lane.

## Task contract closure lane

For a task ID or task contract path, invoke `task-done` internally with the raw
input and stop. Do not add a second confirmation, read/write `status.md`, or run
the legacy story phases. The `task-done` lifecycle and evidence gates are the
single canonical closure procedure.

Task closure does not imply a containing story or epic is complete. Recommend
`$daily-handoff <ID>` when a recovery checkpoint is useful.

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
5. Never fix implementation or manufacture evidence during closure. Return a
   failed/stale task to `$task-cycle <ID>` or the exact legacy story unblock.
6. For an explicit legacy story path, load `references/claude-skill.md`, run its
   evidence gates, and preserve its one explicit close decision.

## Original Workflow Summary

End-of-story completion review. Reads the story file, verifies each acceptance criterion against the implementation, checks for GDD/ADR deviations, prompts code review, updates story status to Complete, and surfaces the next ready story from the sprint.

## Detailed Reference

- Original Claude skill: `references/claude-skill.md`
