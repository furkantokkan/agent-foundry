# Tracked production orchestration

This is the tracked-task mode of `agent-orchestration`, migrated from the
`game-studio-orchestration` procedure. It applies to
repositories using `production/tasks/<ID>/contract.md`, including non-game
projects that adopted that contract. It schedules existing lifecycle skills;
it does not replace their state or lock ownership.

For Unity targets, additionally read [game and Unity references](game-and-unity.md).
For a project with another established task system, preserve that system and
use the main orchestration procedure; do not create production contracts just
to run this profile.

## Resolve lifecycle policy

Read the invoking caller's current user/global/repository policy and installed
lifecycle skill before scheduling. This profile's `READY_TO_CLOSE` and
`task-done` next-action examples describe explicit-close mode. A caller with
explicit standing authorization for verified automatic closure instead lets
the existing lifecycle owner close after all gates pass; the scheduler accepts
that verified `TASK_CLOSED`/`closed` handoff and does not add a second handshake.
Forward the resolved policy to each dispatched lifecycle owner as
`Close authority: automatic_verified | explicit_user` so a delegated owner can
close on its own verified test result. The orchestrator itself never writes a
closure or grants authorization the caller lacks.

If applicable rules cannot be reconciled by precedence,
preserve evidence and resolve the conflict before closure, while independent
authorized work continues. Never relax acceptance, defect freshness, identity,
ownership, or target-risk gates to obtain a terminal state.

## Tracked-task mode

Treat a list of complete task IDs or exact task-contract paths as a request to
run the canonical production orchestration without asking the user to restate
the standing policy:

```text
$agent-orchestration GAME-201 GAME-202 GAME-203
```

1. Resolve the current repository, or one exact `--repo`/`--project`, and then
   resolve each ID only as `production/tasks/<ID>/contract.md`. Require `ready`
   for a new initial execution. For active/resumed defect work,
   validate the existing lifecycle and route through `task-cycle` instead of
   resetting it to ready. Never guess by partial ID, timestamp, or similarly
   named epic/story.
2. Load each contract's objective, allowed/forbidden paths, serialized assets,
   risk, verification, handoff, commit constraints, and managed lifecycle
   block. Read legacy `status.md` only when the block is absent; never create or
   update it. Also load handoffs, ownership ledger, worktrees, and VCS state.
3. Build a conflict graph before implementation. Disjoint writers may run in
   parallel. When one exact active predecessor owns an overlapping writable
   path, assembly, serialized asset, or `.meta`, keep the successor
   `QUEUED_AFTER_OWNER` and run it sequentially after the predecessor's stable
   handoff; do not turn a schedulable collision into `OWNERSHIP BLOCKED`.
   Block only when no unique owner/order or safe handoff can be proven.
4. Give independent tasks separate branches/worktrees and run them in parallel
   up to safe available capacity. Do not create extra writers merely to consume
   capacity. A failed or blocked independent task does not stop unrelated tasks.
5. Keep one sequential role chain under one lifecycle owner per task. A direct
   initial lane requires no `CycleContext`, task state `ready`, `Attempt count:
   0`, and a header-only empty defect ledger; `$implement-task` owns its
   implementer -> verifier handoff. On a clean independent pass under
   `Close authority: automatic_verified`, `$implement-task` closes the task in
   the same write and returns `TASK_CLOSED`. Under `explicit_user` it records
   `READY_TO_CLOSE` and returns `$task-done <ID>`. On a
   same-task failure, it releases the direct lock and dispatches `$task-cycle`,
   which records/deduplicates each `D-xxx` row and `defects/D-xxx.md` record
   before optional bugfixer -> verifier work. Populated-ledger or resumed
   defect work starts with `$task-cycle`.
6. Queue Editor-bound mutation and verification through one confirmed Unity
   Editor connection. Parallel Editor operations require separately matched
   Editor instances rooted at their own worktrees. Code-only work may continue
   while the single Editor slot is occupied. During implementation every lane
   uses the Roslyn compile check, which needs no Editor slot. Final-stage Unity
   test runs from several tasks or sessions on one project root go through the
   `unity-cli` shared test batch, which merges them into one Unity launch per
   test platform; do not schedule them as separate Editor-queue slots.
7. For Unity targets, apply the installed `unity-cli` version gate: Unity 6+
   uses CLI/Pipeline; pre-6 live Editor work uses the approved MCP for Unity
   route. Pin exact project/version/instance. Do not ask the user to repeat
   standing policy and never perform one mutation through two transports.
   Non-Unity tasks use their domain's verification and shared-resource queue.
8. Default to implementation, contract-required verification, automatic safe
   parallelism, isolated worktrees for parallel writers, and no commit or push.
   Never close a task from the scheduler. In explicit-close mode, a clean direct lane becomes close-ready
   with next action `$task-done <ID>`; use `$task-cycle` only for
   active/resumed defects or a verifier failure, where it continues same-scope
   work automatically until a stop gate.

### Automatic split dispatch

When `task-cycle` reports a distinct out-of-scope outcome and exactly one
new contract is returned `ready`, accept both IDs automatically. Release the
parent cycle lock, validate both contracts, then build the conflict graph and
dispatch both lanes. Disjoint paths use separate worktrees/branches and run in
parallel; each task keeps implementer -> verifier sequential. A single matched
Unity Editor is a queue, so code-only work may continue while Editor-bound work
waits. A proven path/serialized/dirty-worktree predecessor creates
`QUEUED_AFTER_OWNER`, not `PARALLEL BLOCKED`; run the successor in the same
worktree when it must inherit uncommitted predecessor changes. Return
`PARALLEL BLOCKED` only for an ambiguous owner/order, unattributable dirty
state, or a project/Editor collision with no safe queue. Same-task defects
remain in the parent ledger and are never split.

### Dependency queue and automatic wake-up

An authorized ready task never becomes `draft` merely because another live
writer currently owns its paths. Register a FIFO dependency:

```text
Queue state: WAITING_FOR_OWNER
Predecessor: <task-id and owner session>
Successor: <task-id>
Wake signal: provider completion event | lifecycle claim release
```

Keep the orchestration invocation alive. Prefer the provider-native
agent/thread completion event when this orchestrator owns the predecessor;
otherwise monitor the exact lifecycle claim read-only at intervals no longer
than 30 seconds and publish a short heartbeat at least once per minute. After
the predecessor reaches `READY_TO_CLOSE`, `closed`, or another explicit stable
handoff and releases ownership, re-read both contracts, current diffs,
fingerprints, risk gates, and Unity project identity. Then dispatch the
successor automatically without asking for another `continue`.

If the predecessor exits without a safe handoff, keep the successor waiting and
report the predecessor's real stop gate. Ask for stale recovery only when the
recorded owner is proven absent and the lock protocol's stale conditions pass.
If this provider cannot remain active or observe a wake signal, say that
automatic wake-up is not armed and return `WAITING_FOR_OWNER`; never pretend a
background scheduler exists.

Before scheduling any tracked lifecycle writer, load and follow
[the installed lifecycle lock](../../task-cycle/references/lifecycle-lock.md). Resolve it from this packaged skill directory, never the target repository.
Worktrees, branches, role ownership, and
the Unity Editor queue never substitute for the shared Git-common-dir lock.
Serialize each task ID to exactly one current lifecycle owner: direct
`$implement-task` or `$task-cycle`. The direct owner holds its lock through
implementer -> verifier and releases it before dispatching a verifier failure
to `$task-cycle`. An active cycle holds its one parent lock through implementer
-> verifier -> optional bugfixer -> verifier and passes its validated
`CycleContext` lock token to nested work. Never bypass, steal, overwrite, or
remove a lock. If the task is busy and its live owner/order is proven, return
the non-terminal `WAITING_FOR_OWNER` scheduler state and wait/retry
automatically; use `BLOCKED: TASK_LIFECYCLE_BUSY` only for an ambiguous or
unrecoverable ownership condition. Different task IDs may still run in
parallel when their normal ownership checks pass.

Same-task defects never receive a new task, branch, worktree, or standalone QA
bug report. They remain in the original contract's managed defect ledger and
linked child evidence records. A separate
player-facing outcome may be routed to `create-task` only after `task-cycle`
retains all separable same-task observations. No task becomes close-ready until
every ledger row is fresh `VERIFIED` and every other required evidence channel
passes.

Before writing, report the resolved contracts, ownership/conflict result,
worktree plan, role chains, Editor queue, verification gates, and any approval
needed. Then execute without file-by-file permission prompts inside approved
low-risk scope.

Invocation-only overrides may select one exact repository, use plan-only mode,
cap parallelism, force one agent, raise verification, or explicitly authorize a
post-pass local commit. They may increase safety but may not widen a contract,
weaken verification/ownership, override a contract prohibition, authorize push,
or lower a risk gate. Commit remains `none` unless the current invocation says
`--commit after-pass` and the contract permits it.
