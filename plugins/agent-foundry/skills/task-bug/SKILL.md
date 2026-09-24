---
name: task-bug
model: sonnet
description: Automatically intake explicit commands or raw post-implementation bug feedback, resolve the one tracked task that owns the failed behavior, and dispatch it to task-cycle without pre-classifying a defect; when natural-language feedback has no task match, route it once to create-task.
---

# Task Bug

`task-bug` is the user-facing repair-intake skill for new bug evidence. Use it
automatically when the operator reports an observable failure after an
implementation, verifier, playtest, or closed-task handoff, even when they do
not type `$task-bug`. It resolves one owning task and forwards the exact
observation to `$task-cycle`.
When natural-language feedback has no plausible owner, it forwards that same
intake once to `$create-task` so the independent repair receives a tracked
contract. It never writes lifecycle state, contracts, or defect records itself;
the selected downstream skill remains the only writer for its artifact.

Under `../task-cycle/references/lifecycle-lock.md`, this router never acquires a
lifecycle lock, creates or writes the authoritative `.lock.claim` file or
`owner.json`, or releases, renames, deletes, or recovers a lock. It may inspect
existing lock metadata read-only for routing
or a blocker report. The selected `task-cycle` performs authoritative
acquisition and every lifecycle write.

```text
$task-bug GAME-202 "Muzzle flash is white on its first frame"
$task-bug "Dash VFX is absent; the grave is off-target; the mine is not placed"
```

## 1. Parse the intake read-only

1. Preserve quoted feedback, attachments, paths, URLs, logs, screenshots, and
   the optional exact `--repo`/`--project` selector byte-for-byte.
2. Treat a first positional value as an identity only when it is a complete
   task ID that resolves exactly or an explicit in-repository contract path.
   Otherwise treat the complete positional text as feedback.
3. Require at least one observable symptom or attached evidence. With no new
   evidence, return `BUG INPUT REQUIRED`; use `$task-cycle <ID>` only to resume
   defects that are already recorded.
### Semantic intent gate

Before resolving an owning task, classify the intake intent. A bug requires an
observable failure of an existing accepted or preserved behavior (for example
wrong, missing, broken, crash, regression, or reproducible mismatch). A
proposal, architecture/schema improvement, balance/design revision, deployment
status question, or request to make a system more flexible is not defect
evidence, even when it overlaps an open task.

- For a revision/status request with an explicit task, return
  `CONTRACT_CHANGE_REQUIRED` or `STATUS_QUERY`, perform zero writes, and do
  not invoke $task-cycle. Recommend design review/status inspection followed by a
  contract update or separate task.
- For a natural-language revision with no owning task, route once to
  `create-task` as a planned change, not as a defect; preserve the raw request
  and do not create a defect record.
- Only observable failure evidence may enter the normal task-bug ->
  $task-cycle defect route. Path or area overlap alone never overrides this gate.

4. Use only read-only shell/VCS inspection here. Do not edit a contract,
   defect record, source, Unity asset, VCS state, or external tracker.
5. Treat a `D-xxx` mentioned in conversation, a summary, or a handoff as a
   `CANDIDATE_DEFECT`, never as canonical proof of reuse or recurrence.

## 2. Resolve the exact repository and candidates

Read repository instructions, task conventions, current conversation context,
branch/worktree mapping, retained handoffs, and task contracts. Never guess
between repositories.

With an explicit ID/path, resolve exactly as
`production/tasks/<ID>/contract.md` or the supplied in-repository path. A
missing explicit identity is `TASK NOT FOUND`, not natural-language fallback.

Without an explicit identity, search in this order:

1. `in_progress`, `reopened`, `blocked`, and `ready_to_close` tasks;
2. ready tasks named by the current implementation/verifier handoff;
3. closed tasks whose accepted or preserved behavior may have regressed.

If a candidate is closed with `Closure mode: superseded`, validate its
`Superseded by` link and continue matching against that current contract. The
historical task is audit evidence, not an active blocker. Never reopen or route
to a superseded contract while its valid replacement owns the behavior.

Compare the observation with objective, acceptance, preserved behavior,
changed/owned systems, existing ledger rows, linked defect records, current
conversation, branch/worktree, and recent handoff evidence. Path or area overlap
alone is never enough. Require one unique high-confidence candidate supported
by both a behavior relation and task-identity evidence.

Conversation and handoff evidence may nominate a candidate task or defect, but
the router must not announce a confirmed `D-xxx`, reuse, recurrence, reopen,
root cause, or chosen code fix. Canonical defect matching requires task-cycle
to read the current contract ledger, linked record, contract fingerprint, and
reviewed revision under its lifecycle-writer rules.

## 3. Choose one safe route

Do not predeclare `$task-cycle`, `$create-task`, `unity-game-dev`, a defect ID,
or a repair plan before candidate resolution. Until then report the route as
unresolved and keep inspection read-only. After resolution, announce and invoke
exactly one downstream route. A `NO_TASK_MATCH` route lets `$create-task` load
`unity-game-dev` for Unity domain planning; an existing-task route lets
`$task-cycle` require it in the implementation/verification handoff.

- A revision/status request is not a defect: with an explicit task return
  `CONTRACT_CHANGE_REQUIRED` or `STATUS_QUERY` and dispatch neither the
  $task-cycle nor a defect writer. With no owning task, use $create-task once as a
  planned change and preserve the raw request.
- One unique high-confidence task that is not the pre-implementation case
  below: continue automatically.
- One unique `ready` task whose lifecycle is still `planning`, `Attempt count`
  is `0`, and whose baseline is the same unchanged intake that created it:
  preserve the contract byte-for-byte. With an explicit same-conversation
  `continue`, `devam et`, or `go ahead`, dispatch `$implement-task <ID>`
  immediately and return `READY_TASK_DISPATCHED`; do not merely print its next
  command. Without execution authorization, return `READY_TASK_EXISTS`,
  dispatch neither `$task-cycle` nor `$create-task`, and return its
  `$implement-task` next command. The result block MUST contain exactly
  `Task creation: TASK EXISTS — <ID>` (never `not run`) so this outcome is
  deterministic. The original pre-implementation symptom is not a defect
  recurrence.
- Several plausible tasks: return `TASK MATCH AMBIGUOUS`, list each ID/title
  and matching evidence, ask one identity question, perform zero writes, and do
  not invoke `$create-task`.
- No plausible task from a natural-language intake: record `NO_TASK_MATCH` as
  the routing result, then invoke `$create-task` exactly once with the unchanged
  feedback/evidence and exact repository selector. Using `$task-bug` expresses
  repair intent, so do not pause merely to ask whether a low-risk task contract
  may be created.
- A supplied complete ID/path that does not resolve remains `TASK NOT FOUND`.
  Perform zero writes and do not reinterpret or auto-create that identity.

`bug-report` remains the separate report-only backlog lane when the operator
explicitly asks to capture rather than repair an unowned issue. Do not silently
switch to that lane.

Do not decide final defect relation, defect identity, recurrence, root cause,
or repair authority in this router. Those decisions belong to `task-cycle`,
which confirms canonical records and classifies relation before scope/risk.

## 4. Dispatch exactly one downstream workflow

For the resolved task, invoke `$task-cycle` exactly once with the exact ID, raw
feedback/evidence, repository selector, and any conversation-derived candidate
ID explicitly labelled non-authoritative. Load and follow its installed skill;
do not copy or reimplement its dedupe, document, repair, verification, reopen,
or closure logic.

Only one downstream `task-cycle` lifecycle writer may run for the same task at
a time. Do not acquire the shared lock on its behalf. If another cycle owns it,
return the non-terminal route `WAITING_FOR_OWNER` when the live owner and order
are proven. Hand the raw feedback to `game-studio-orchestration`, which keeps it
queued, waits for the owner completion/claim-release signal, then re-dispatches
`task-cycle` automatically. Do not ask the operator to repeat the feedback or
type another command. Use `BLOCKED: TASK_LIFECYCLE_BUSY` only when owner
identity/order is ambiguous or no safe wake signal exists. Different tasks may
proceed independently after normal ownership checks.

`task-cycle` creates or reuses
`production/tasks/<ID>/defects/D-xxx.md`, links the ledger ID to that record,
and automatically continues safe repair/verification. Return its terminal
result without asking the operator to type `$implement-task`.

For a natural-language `NO_TASK_MATCH`, invoke `$create-task` exactly once.
Forward the raw observation, attachments, references, and `--repo`/`--project`
selector without inventing an ID, ownership, scope, or acceptance criteria.
Load and follow the installed skill; `$create-task` owns duplicate/same-task
checks, ID allocation, contract readiness, and the only contract write.

Honor `$create-task` results such as `TASK CREATED`, `TASK UPDATED`,
`TASK DISPATCHED`, `TASK QUEUED`, `TASK EXISTS`, `SAME_TASK_DEFECT`,
`POSSIBLE DUPLICATE`, or `ACTION_REQUIRED` for an actual
`NO_TASK_MATCH` dispatch; never force a new ID or bypass its question/gate. A
repeated identical intake that resolves the ready pre-implementation task uses
`READY_TASK_EXISTS` above and must not redispatch `$create-task` or create a
second contract. Do not invoke `$implement-task` after initial task creation
without execution authorization. When an explicit same-conversation
affirmative resolves that one task from draft to ready, cascade into
`$implement-task` in the same turn instead of returning another next command.
If that ready task has one exact active predecessor on its writable paths,
cascade into `$game-studio-orchestration <predecessor> <new-id>` instead. It
must retain the execution authorization, wait, and start the successor after
the stable handoff without another `continue`.
Never invoke both `$task-cycle` and `$create-task` as independent routes for
one intake.

## 5. Report routing and next action

```text
TASK BUG
Routing result: UNIQUE_MATCH | READY_TASK_EXISTS | READY_TASK_DISPATCHED |
                WAITING_FOR_OWNER | TASK MATCH AMBIGUOUS | NO_TASK_MATCH |
                TASK NOT FOUND | CONTRACT_CHANGE_REQUIRED | STATUS_QUERY
Task match: <ID and evidence | AMBIGUOUS | NONE>
Contract: production/tasks/<ID>/contract.md | none
Feedback: <atomic observation summary without losing raw evidence>
Candidate defect: <D-xxx from conversation/handoff | none>
Defect match authority: task-cycle | not run
Dispatch: task-cycle <ID> | create-task | game-studio-orchestration <IDs> |
          not dispatched
Defect records: <linked D-xxx paths returned by task-cycle | none>
Cycle result: <terminal task-cycle verdict | not run>
Task creation: <create-task result and ID/path | TASK EXISTS — ID | not run>
Unity preflight: <forwarded create-task verdict | returned by cycle | not run>
Domain planning/workflow: <forwarded downstream result | not run>
Next: <task-cycle result, create-task/implement-task next command, or one identity correction>
```

Never implement without explicit execution authorization, auto-close, commit,
push, widen contract authority, or create a second lifecycle source. A
same-conversation affirmative is authorization for the one resolved task,
including a draft-to-ready transition in that turn. A close-ready result still
ends at `$task-done <ID>`.
