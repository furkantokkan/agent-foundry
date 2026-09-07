---
description: Route raw bug feedback without pre-classifying a defect; resolve its owning task, or create one tracked task when natural-language feedback has no match.
argument-hint: '[<task-id | contract-path>] "<bug feedback>" [--repo <path>]'
---

# Task Bug

Use the `task-bug` Codex skill for this request.

Forward the complete block as one raw intake. Preserve the optional identity,
quoted feedback, attachments, logs, references, and repository selector.

<task-bug-input>
$ARGUMENTS
</task-bug-input>

The adapter performs no task matching, lifecycle mutation, document creation,
implementation, verification, closure, commit, or push itself. The skill owns
routing: confirmed observable failures go to `task-cycle`; revision/status
feedback is not a defect. With an explicit task it returns
`CONTRACT_CHANGE_REQUIRED` or `STATUS_QUERY` without lifecycle dispatch;
without an owner it may go once to `create-task` as a planned change.
If a proven live writer already owns the matched task or the new task's paths,
route through `game-studio-orchestration` as `WAITING_FOR_OWNER`; retain the
raw feedback and execution authorization, then resume automatically after the
owner releases.

A `D-xxx` mentioned in conversation or a handoff is only a candidate. Neither
this adapter nor the intake may announce confirmed reuse, recurrence, reopen,
root cause, or a chosen fix before task-cycle checks canonical records.
