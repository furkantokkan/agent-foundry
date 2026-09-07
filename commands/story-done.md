---
description: Compatibility alias to task-done for task IDs/contracts; explicit story paths retain the legacy story completion review.
argument-hint: '[task-id | contract-path | story-file-path] [--review <path>]'
---

# /story-done

Use the `story-done` Codex skill for this request. If this workflow references
Claude-only agents, treat those names as role guidance and follow Codex's active
skills, global instructions, and local repository rules.

Treat the complete block below as one raw story-done input. Preserve exact task
IDs, paths, and review references.

<story-done-input>
$ARGUMENTS
</story-done-input>

A complete task ID or exact task contract forwards to `task-done` with no
second confirmation. Only an explicit story-file path enters the legacy lane.
Do not read/write per-task `status.md`, commit, or push.
