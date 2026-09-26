---
description: Coordinate independent work with ownership, worktrees, sequential roles, and verification through agent-orchestration.
argument-hint: '[task-id ... | request] [--mode plan|implement] [--max-parallel N] [--agents auto|single] [--verify auto|full] [--commit none|after-pass] [--repo <path>]'
---

# /agent-orchestration

Use the `agent-orchestration` skill in this invocation. Preserve all raw arguments and existing authorization; do not add a second scheduler. If the skill is unavailable, report it and stop coordination.

User arguments: $ARGUMENTS
