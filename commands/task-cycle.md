---
description: Resume one resolved task's recorded defects through the sole ledger writer, confirming candidate matches before bounded repair or reopen.
argument-hint: '<task-id | contract-path> ["additional evidence"] [--repo <path>]'
---

# Task Cycle

Use the `task-cycle` Codex skill for this request.

Treat the complete block below as one raw task-cycle input. Preserve the exact
ID/path, evidence, references, and repository selector.

<task-cycle-input>
$ARGUMENTS
</task-cycle-input>

The adapter performs no lifecycle mutation, document creation, implementation,
verification, closure, commit, or push itself. Use `/task-bug [<ID>]
"<feedback>"` as the preferred intake for a new user-observed bug; use this
command directly to resume defects already recorded for one exact task.
If the feedback also contains a distinct out-of-scope outcome, retain
same-task defects, invoke create-task once for that outcome, and—when exactly
one ready contract is returned—automatically hand both IDs to
game-studio-orchestration. That orchestration must conflict-check first, use
separate worktrees for disjoint writers, keep each task's role chain
sequential, and queue single-Editor work. On any ownership/path/serialized or
Editor collision with no proven owner/order, return PARALLEL BLOCKED without
creating a writer. A proven live predecessor instead produces
WAITING_FOR_OWNER/QUEUED_AFTER_OWNER; wait for its stable handoff and release,
then resume automatically without another operator command.
The skill must check the canonical ledger, linked record, fingerprint, and
revision before reporting reuse/reopen; suspected causes remain hypotheses
until reproduction evidence confirms them.
After its internal implementer/verifier handoff, the parent cycle must resume,
refresh reviewed/evidence identities, transition every defect from verified
evidence, and record either `READY_TO_CLOSE` with `task-done <ID>` or one exact
blocker. It must not forward a child's next command or ask for task-cycle again.
