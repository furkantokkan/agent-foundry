---
description: Coordinate tracked tasks or multi-discipline game-development work with automatic ownership, worktree, handoff, Unity transport, and verification defaults.
argument-hint: '[task-id ... | studio-task] [--mode plan|implement] [--max-parallel N] [--agents auto|single] [--verify auto|full] [--commit none|after-pass] [--repo <path>]'
---

# /game-studio-orchestration

Use the `game-studio-orchestration` skill. Load role, hook, rule, or template
references only as needed. If the task maps to a narrower workflow, combine with
`adaptive-skills` and the relevant focused skill.

For complete task IDs or exact contract paths, apply tracked-task mode. Resolve
contracts, check readiness and ownership conflicts, isolate independent writers
in worktrees, keep same-task roles sequential, queue single-Editor work, use the
matching Unity MCP-first policy, and default to no commit/push. Do not require
the user to repeat those standing rules.

When task-cycle returns one ready contract for a distinct out-of-scope
outcome, accept both IDs automatically: build the conflict graph, isolate
disjoint writers in separate worktrees, run the two implementer -> verifier
chains in parallel, and queue single-Editor operations. Return PARALLEL BLOCKED
only when owner/order or a safe handoff cannot be proven. A uniquely owned
path, serialized-asset, or attributable dirty-worktree overlap becomes
QUEUED_AFTER_OWNER: keep one writer, wait for its stable handoff/lock-release
signal, revalidate, then start the successor automatically in the same
worktree when it inherits uncommitted changes.

For defects found after implementation, keep the handoff inside the owning task:
`verifier -> task-cycle intake/deduplication -> bugfixer -> verifier`. Do not
spawn a new task, bug file, or parallel same-task writer. Repeat the bounded
sequence until every same-task defect is freshly verified or task-cycle reaches
a declared stop gate.

User arguments: $ARGUMENTS
