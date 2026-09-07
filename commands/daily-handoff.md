---
description: Create a durable task handoff with defect counts/IDs and verification freshness, without changing lifecycle state or VCS.
argument-hint: '[task-id | contract-path ...] [--repo <path>]'
---

# Daily Handoff

Use the `daily-handoff` Codex skill for this request.

Treat the complete block below as one raw daily-handoff input. Preserve exact
task IDs, contract paths, ordering, and the repository selector.

<daily-handoff-input>
$ARGUMENTS
</daily-handoff-input>

Report status, completed work, changed systems, verification evidence,
unresolved/verified defect counts and IDs, evidence freshness, remaining
blocker, one short task-ID-first next command, and commit status for each
selected task. List only freshly verified defects as completed; route an
already-recorded unresolved, blocked, or stale defect to `/task-cycle <ID>` and
new feedback to `/task-bug [<ID>] "<feedback>"`. Update only the
managed `DAILY-HANDOFF` block in `production/session-state/active.md`,
idempotently. Do not run tests/builds, mutate Unity, edit task lifecycle state,
start/interrupt agents, commit, or push.
