---
description: Show a read-only task snapshot including unresolved/verified defect counts, evidence freshness, blockers, and the next command.
argument-hint: '[task-id | contract-path ...] [--repo <path>]'
---

# Task Status

Use the `task-status` Codex skill for this request.

Treat the complete block below as one raw task-status input. Preserve exact task
IDs, contract paths, ordering, and the repository selector.

<task-status-input>
$ARGUMENTS
</task-status-input>

Report current phase, task-owned changed paths, recorded test evidence and
freshness, unresolved and verified defect counts/IDs, one blocker, any genuine
user decision, and one next command per task. Any already-recorded unresolved,
blocked, or stale defect points to `/task-cycle <ID>`; new unrecorded feedback
points to `/task-bug [<ID>] "<feedback>"`. Read lifecycle state from `contract.md`;
legacy `status.md` is read-only compatibility input. Do not run tests/builds,
mutate Unity, start or interrupt agents, write state, start a task cycle, close
tasks, or change VCS/external tracker state.
