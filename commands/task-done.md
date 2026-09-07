---
description: Close one current READY_TO_CLOSE task from a clean implementation or defect cycle when all required evidence is fresh.
argument-hint: '<task-id | contract-path> [--strict] [--superseded-by <task-id>]'
---

# Task Done

Use the `task-done` Codex skill for this request.

<task-done-input>
$ARGUMENTS
</task-done-input>

Resolve a complete ID only to `production/tasks/<ID>/contract.md`. Require
fresh `READY_TO_CLOSE` evidence, zero unresolved or blocked defect-ledger rows,
and fresh `VERIFIED` evidence for every known defect. The close-ready state may
come from a clean direct implementation with an empty ledger or from
`task-cycle`; do not require a defect cycle when no defect exists. Refuse
contradictory or stale lifecycle state. Under the shared lifecycle lock, recompute the canonical
reviewed/evidence identities without rerunning tests. Preserve the defect ledger
while updating only the managed lifecycle block, and do not ask for a second
close confirmation. Never run implementation/tests, mutate Unity, commit, or
push. A later same-scope defect enters through `/task-bug <ID> "<feedback>"`;
its downstream cycle reopens the same task and defect record safely.

For validated orphan reconciliation, `--superseded-by <NEW-ID>` closes the old
planning task with `Closure mode: superseded` only after proving the ready
replacement links back to it and the old task has no active owner or progress.
Preserve all evidence and return `STALE_TASK_RECONCILIATION_REQUIRED` on any
conflict; never delete the old task.
