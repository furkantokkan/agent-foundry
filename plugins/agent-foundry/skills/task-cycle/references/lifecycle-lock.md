# Task Lifecycle Lock Protocol

This protocol is normative for every write to a tracked task lifecycle block or
linked `defects/D-xxx.md` record. It serializes one task across terminals,
agents, branches, and Git worktrees.

## Shared lock location

1. Resolve the exact repository root and task ID.
2. In Git, resolve the absolute common directory with
   `git rev-parse --path-format=absolute --git-common-dir`.
3. Use the shared namespace:
   - authoritative claim file:
     `<git-common-dir>/ccgs/task-lifecycle-locks/<TASK-ID>.lock.claim`;
   - inspection metadata directory:
     `<git-common-dir>/ccgs/task-lifecycle-locks/<TASK-ID>.lock/`.
   The Git common directory is shared by every worktree. The claim file, not
   directory existence, decides ownership.
4. Outside Git, use the repository's documented atomic lock service. If none
   exists, do not claim cross-terminal safety; serialize manually or return
   `BLOCKED: TASK_LIFECYCLE_LOCK_UNAVAILABLE`.

The lock directory is operational metadata. Never stage or commit it.

## Atomic acquisition

Generate a cryptographically random owner token and complete owner metadata in
memory. Acquire by opening the exact claim file once with
`FileMode.CreateNew`, `FileAccess.Write`, and `FileShare.None`, then write and
flush that metadata through the returned handle before closing it.
`FileMode.CreateNew` must fail when the claim exists. A prior existence check,
ordinary create/overwrite, `New-Item -ItemType Directory`, or
`Directory.CreateDirectory` is not acquisition.

The claim metadata contains:

- schema version;
- task ID;
- owner token;
- provider and session identity;
- the owner process ID and its start time: the long-lived agent process that
  owns the conversation (see Liveness and takeover), or `unknown`;
- host;
- absolute worktree path;
- acquisition UTC timestamp and last heartbeat UTC;
- contract fingerprint and reviewed revision observed before acquisition.

After the claim succeeds, create the inspection metadata directory and write
the same metadata to `owner.json`. Re-read both the claim file and `owner.json`
and confirm that both tokens match before any lifecycle write. If
`FileMode.CreateNew` reports that the claim exists, read claim metadata. If its
owner has stopped (see Liveness and takeover), take the task over. Otherwise
return `BUSY: TASK_LIFECYCLE_BUSY` to the caller without writing. Never steal a
live claim, overwrite, delete, or run a second writer. A live claim is a scheduling
dependency, not a persistent task blocker: an owning orchestrator must surface
`WAITING_FOR_OWNER`, retain the authorized work in its queue, and wait for the
owner-completion or claim-release signal before retrying acquisition.

If metadata-directory materialization fails after the claim succeeds, treat
the attempt as blocked. Remove the claim only after re-reading it and proving
that its token matches the current holder; otherwise leave it for the takeover
rules below.

## Parent and nested work

`task-cycle` owns the lock for its complete transition, including the
implementer/verifier handoff, except while it waits for a submitted test
result (see below). Pass the owner token and lock path in
`CycleContext`. `implement-task` called from that cycle reuses the parent lock;
it never acquires a nested lock. A direct tracked `implement-task` call must
acquire the same protocol before changing lifecycle state.

`task-bug` is read-only. It may inspect and report the shared lock, but
`task-cycle` performs authoritative acquisition. Orchestration must schedule at
most one lifecycle writer per task and must never bypass or remove a lock.

## Release while waiting for tests

A task waiting for a submitted final-stage test result holds no lock, so other
agents can work on the same files in the meantime.

1. Submit the request without waiting (`unity_test_batch.py submit --no-wait`)
   and keep the printed request ID and files digest.
2. While still holding the lock, write one lifecycle transition:
   `Current phase: awaiting_tests` and
   `Pending test request: <request-id> <files-digest>`, with every result and
   defect row unchanged. Then release the lock normally. Report
   `AWAITING_TESTS` to the orchestrator: it is a stable handoff that frees the
   task's writable paths for queued agents.
3. Wait with `wait --id <request-id>` while holding no lock. A role agent that
   submits tests returns `AWAITING_TESTS` with the request ID to the lock
   holder instead of waiting inside the role.
4. When the result arrives, acquire the lock again as a new owner (a live
   owner means `WAITING_FOR_OWNER`, then retry). Re-read the contract, ledger,
   and records. Confirm `Pending test request` still names this request. Read
   the result again under the lock (`wait --id` re-hashes the files) and
   recompute the reviewed revision. Clear `Pending test request` in the next
   lifecycle write.
5. Only a fresh `PASS` for unchanged bytes counts as evidence. `STALE` means
   another agent changed the files: queue behind that agent while it owns them
   (`WAITING_FOR_OWNER`), then resubmit after its handoff. On `FAIL`, resume
   the same verifier with the result when its classification is needed, then
   continue the normal repair path once the paths are free.

A task found in `awaiting_tests` with no live waiter is resumed by its
lifecycle skill from step 4. The new owner passes its new token in any later
`CycleContext`; the token from before the release is void.

## Queue and release signalling

The claim file itself is the cross-terminal release signal. A scheduler that
encounters a live claim must keep the invocation active and:

1. record the waiting task, owner task/session, collision, and FIFO dependency
   in its in-memory orchestration plan;
2. prefer the provider's agent/thread completion signal when it owns the active
   writer; otherwise re-read the exact claim read-only at intervals no longer
   than 30 seconds. At each read, apply the liveness rules: take over a stopped
   owner instead of waiting for it;
3. provide a short progress heartbeat at least once per minute while waiting;
4. when the owner completes or the claim disappears, re-read task state,
   ownership, paths, dirty fingerprints, and risk gates before dispatch;
5. preserve the waiting task's original execution authorization—no second
   `continue` or `implement-task` command is required.

For overlapping paths across different task IDs, the orchestrator also waits
for the predecessor's stable handoff (`AWAITING_TESTS`, `READY_TO_CLOSE`,
`closed`, or another explicit release state) and then runs the successor sequentially in the same
worktree when it must inherit uncommitted predecessor changes. It must not
create parallel worktrees for logically dependent overlapping writers.

If the provider cannot keep a scheduler alive or observe either signal, it must
say so and return `WAITING_FOR_OWNER` with the exact owner identity; it must not
claim that automatic wake-up is armed. This limitation is operational, not a
reason to change the task contract to `draft` or `blocked`.

## Compare, write, and release

While holding the lock:

1. Re-read the canonical contract, full ledger, linked records, contract
   fingerprint, and reviewed revision.
2. Reconcile against that current state.
3. Write one logical transition.
4. Re-read every changed lifecycle artifact and validate invariants.

Release in a `finally`/guaranteed-cleanup path. Before removal, re-read both the
claim file and `owner.json`; proceed only when both owner tokens exactly match
the current holder. Remove the inspection metadata directory first and the
exact claim file last. If either token is absent or mismatched, remove neither.
A process must never remove another owner's lock.

## Liveness and takeover

A claim blocks other agents only while its owner is live. A task whose owning
session stopped is not locked: another agent takes it over and continues it.

The owner is live while both hold:

1. its session process runs: the recorded owner process on this host still
   exists with the recorded start time. The owner process is the long-lived
   agent process that owns the conversation, never the short-lived shell that
   ran the lock command;
2. it shows activity: the claim heartbeat or a lifecycle write to the contract
   is younger than the lease window. The window is 30 minutes unless repository
   instructions set another. The owner renews the heartbeat at every step
   boundary (an edit batch, a handoff, a test submission) and at least every
   10 minutes while it works.

The owner has stopped, and the task is takeover-able, when its recorded process
is gone (or the PID now belongs to a process with another start time), or when
no activity was seen for the lease window. The second rule also covers a
session that is still open but no longer working (usage limit, crash loop,
abandoned prompt). When the process is unknown or on another host, only the
activity rule applies.

A waiting agent with authorized work in the same place takes over without
asking. The user's standing order for stopped sessions is the authorization.

1. Re-read the claim and confirm the same token and the stopped verdict.
2. Atomically rename the claim file to an audit name containing its prior
   owner token and the takeover UTC, then move its metadata directory the same
   way. If the rename fails, another agent won the race: re-read and retry as a
   waiter.
3. Acquire normally with `FileMode.CreateNew`.
4. Re-read the contract, ledger, records, and the stopped owner's uncommitted
   changes. Keep every one of them; never discard or revert the stopped
   owner's work.
5. Record one lifecycle history entry:
   `Taken over from <prior session or token>: <process gone | idle N min>`.
   Then continue the task from its recorded state through its lifecycle skill:
   `task-cycle` for defect or resumed work, the `implement-task` continuation
   for an empty-ledger direct lane, or the release-while-waiting steps for
   `awaiting_tests`.

A task in `in_progress`, `reopened`, or `awaiting_tests` with no claim at all
has no owner. It never blocks another agent, which may take it over the same
way from step 3.

An owner that pauses (waiting for the user, a long step, a resumed session)
re-reads its token in the claim and `owner.json` before its next write of any
kind. A mismatch means the task was taken over: it writes nothing more, reports
`LOCK_TAKEN_OVER`, and queues behind the new owner as `WAITING_FOR_OWNER`.
