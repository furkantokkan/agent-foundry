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
- provider/session or process identity;
- host;
- absolute worktree path;
- acquisition UTC timestamp;
- contract fingerprint and reviewed revision observed before acquisition.

After the claim succeeds, create the inspection metadata directory and write
the same metadata to `owner.json`. Re-read both the claim file and `owner.json`
and confirm that both tokens match before any lifecycle write. If
`FileMode.CreateNew` reports that the claim exists, read claim metadata and
return `BUSY: TASK_LIFECYCLE_BUSY` to the caller without writing. Do not steal,
overwrite, delete, or run a second writer. A live claim is a scheduling
dependency, not a persistent task blocker: an owning orchestrator must surface
`WAITING_FOR_OWNER`, retain the authorized work in its queue, and wait for the
owner-completion or claim-release signal before retrying acquisition.

If metadata-directory materialization fails after the claim succeeds, treat
the attempt as blocked. Remove the claim only after re-reading it and proving
that its token matches the current holder; otherwise leave it for explicit
stale recovery.

## Parent and nested work

`task-cycle` owns the lock for its complete transition, including the
implementer/verifier handoff. Pass the owner token and lock path in
`CycleContext`. `implement-task` called from that cycle reuses the parent lock;
it never acquires a nested lock. A direct tracked `implement-task` call must
acquire the same protocol before changing lifecycle state.

`task-bug` is read-only. It may inspect and report the shared lock, but
`task-cycle` performs authoritative acquisition. Orchestration must schedule at
most one lifecycle writer per task and must never bypass or remove a lock.

## Queue and release signalling

The claim file itself is the cross-terminal release signal. A scheduler that
encounters a live claim must keep the invocation active and:

1. record the waiting task, owner task/session, collision, and FIFO dependency
   in its in-memory orchestration plan;
2. prefer the provider's agent/thread completion signal when it owns the active
   writer; otherwise re-read the exact claim read-only at intervals no longer
   than 30 seconds;
3. provide a short progress heartbeat at least once per minute while waiting;
4. when the owner completes or the claim disappears, re-read task state,
   ownership, paths, dirty fingerprints, and risk gates before dispatch;
5. preserve the waiting task's original execution authorization—no second
   `continue` or `implement-task` command is required.

For overlapping paths across different task IDs, the orchestrator also waits
for the predecessor's stable handoff (`READY_TO_CLOSE`, `closed`, or another
explicit release state) and then runs the successor sequentially in the same
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

## Stale recovery

Age alone never proves staleness. Recovery requires:

1. the acquisition timestamp exceeds the repository's stale threshold;
2. the owner process/session is proven absent on the same host, or the operator
   explicitly authorizes recovery of the exact lock;
3. the contract fingerprint and reviewed revision are re-read;
4. the stale claim file is atomically renamed to an audit name containing its
   prior owner token and recovery UTC before its metadata directory is renamed
   and a new acquisition is attempted.

If any check is unavailable or ambiguous, retain `WAITING_FOR_OWNER` and report
the exact stale-recovery evidence gap. Never silently delete a stale-looking
lock or ask for recovery while the recorded owner is proven live.
