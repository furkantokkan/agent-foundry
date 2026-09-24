---
name: task-status
model: sonnet
description: Show a fast read-only snapshot for one or more tracked tasks from each contract's managed lifecycle block, including phase, changed paths, evidence, blockers, decisions, and next command. Use for progress checks without running tests, writing status files, changing task state, or starting a cycle.
---

# Task Status

Report recorded task state without implementing, verifying, fixing, closing, or
updating it.

```text
$task-status GAME-201 GAME-202 GAME-203
$task-status
```

## 1. Resolve tasks

1. Resolve the current repository unless one exact `--repo` or `--project` is
   supplied. Read repository task conventions first.
2. Resolve complete IDs only as `production/tasks/<ID>/contract.md`; accept
   explicit in-repository contract paths. Preserve order and deduplicate IDs.
3. Never fall back to epics, stories, display names, timestamps, or partial IDs.
4. With no IDs, include lifecycle states `in_progress`, `reopened`, or
   `ready_to_close`, plus `draft` tasks with a non-empty `Action required`
   and tasks named by active orchestration.
   Do not list untouched `ready` backlog or `closed` tasks.

## 2. Read state without creating it

Read the `TASK-LIFECYCLE` block in each `contract.md`, role handoffs,
ownership/worktree ledgers, attributable diffs, retained verification evidence,
and commit metadata. For legacy tasks without the block, read sibling
`status.md` as compatibility input. Never create, update, migrate, or delete a
state artifact from this read-only command.

Read the entire defect ledger and report counts plus stable IDs grouped as
unresolved (`OPEN`, `REPRODUCING`, `FIXING`, `FIXED_UNVERIFIED`, `VERIFYING`,
`BLOCKED`) and `VERIFIED`. Do not infer resolution from code changes or a green
acceptance summary. If a `VERIFIED` row's evidence revision does not match the
reviewed revision, label it `STALE` in the snapshot without rewriting it.
Resolve every linked ID path read-only. Report missing/mismatched child records
as an evidence-integrity blocker and route to `task-cycle`; never backfill here.

Do not run tests/builds, refresh Unity, mutate Editor state, start agents, or
use Unity transports to manufacture fresh evidence. Mark checks `PASS`, `FAIL`,
`NOT_RUN`, `STALE`, or `UNKNOWN`; claims without retained sources are `UNKNOWN`.

Use phases:

```text
planning | implementation | verification | bugfix | review |
ready_to_close | waiting | closed | not_started | unknown
```

Prefer newer attributable handoffs over older state, but report contradictions
as blockers. Never attribute unrelated dirty paths to a task.

## 3. Choose one next action

- `ready_to_close`: `$task-done <ID>`;
- new unrecorded bug feedback: `$task-bug [<ID>] "<feedback>"`;
- any populated defect-ledger row, or a lifecycle/handoff that records a
  reopened or resumable cycle: `$task-cycle <ID>`;
- an empty defect ledger with initial ready work or incomplete initial
  implementation/evidence: `$implement-task <ID>`;
- `closed`: `None` unless new feedback exists, then `$task-bug <ID> "<feedback>"`;
- `closed` with `Closure mode: superseded`: report `Superseded by: <ID>`
  and route status/continuation to `$task-status <replacement-id>`; never
  revive or list the superseded task as an active blocker.
- new unrecorded bug feedback with uncertain task identity:
  `$task-bug "<feedback>"`;
- identity, ownership, stale contradiction, or approval gate: one focused
  unblock action;
- active work: `Wait for <phase>`.

Do not send a defect-free initial implementation result through `task-cycle`
merely because an implementation handoff exists. Conversely, once any defect
row exists or the task has entered a reopened/resumed cycle, keep continuation
on `task-cycle` unless `ready_to_close` takes precedence. If a workflow already
owns the task and is actively running, report `Wait for <phase>` instead of
suggesting a duplicate invocation.

Report a user decision only for a genuine product, architecture, risk,
ownership, or scope choice. Do not emit new lifecycle verdicts.

## 4. Report compactly

```text
TASK STATUS

<ID>
State: <state> [recorded | legacy | inferred]
Phase: <phase> [recorded | inferred]
Changed paths: <paths | None | UNKNOWN>
Tests: <check=result with source/revision>
Defects: <n unresolved [IDs]> | <n verified [IDs]> | <stale IDs>
Defect records: <n linked | missing/mismatched IDs>
Waiting reason: <reason | None>
Queue: WAITING_FOR_OWNER <predecessor-id> | None
Automatic wake-up: armed | unavailable | not applicable
Action required: <one action | None>
Decision required: <one decision | None>
Next: <one command | action | None>
```

State the snapshot revision/time. Never write `contract.md`, `status.md`, source,
tests, VCS, Unity, or external trackers.
