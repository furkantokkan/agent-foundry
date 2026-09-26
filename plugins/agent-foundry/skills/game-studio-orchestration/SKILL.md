---
name: game-studio-orchestration
model: inherit
description: Compatibility alias for agent-orchestration; forward all existing task IDs, flags, constraints, and authorization unchanged.
---

# Legacy orchestration alias

Read [Agent Orchestration](../agent-orchestration/SKILL.md) and continue in this same invocation. Forward arguments unchanged; do not start a second coordinator or scheduler. If that source is missing, report the path and stop; do not fall back to a cached studio procedure.

Existing `references/` files supply game/Unity domain roles, rules, and templates selected by the unified workflow.
