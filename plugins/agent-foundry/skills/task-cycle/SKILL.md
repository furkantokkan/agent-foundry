---
name: task-cycle
model: inherit
description: Execute the canonical defect lifecycle for one already-resolved tracked task by confirming candidate matches, maintaining the sole defect ledger and linked evidence, running bounded repair and verification, and reopening safely. Use $task-bug first for new user bug feedback.
---

# Task Cycle

`task-cycle` is the canonical defect-lifecycle executor and the sole writer of
the managed defect ledger and linked defect records for a tracked task.
Use `$task-bug [<ID>] "<feedback>"` as the preferred user-facing intake for new
bug evidence; call `$task-cycle <ID>` directly to resume defects already in the
ledger. The cycle owns the task's managed defect ledger plus its linked defect
records and automatically continues safe same-task work; the operator must not
have to invoke `$implement-task` again.

Plain conversational feedback after an implementation or verification handoff
must enter through task-bug first. A defect ID supplied by conversation,
memory, summary, or router context is only a candidate until this cycle checks
the canonical ledger and linked record.

```text
$task-cycle GAME-202
$task-cycle GAME-202 "Dash VFX is absent, the grave spawns at the caster, and the mine is not placed"
```

The contract authority outside `TASK-LIFECYCLE` is immutable. The cycle may
update only that managed block and linked
`production/tasks/<ID>/defects/D-xxx.md` evidence records, and may invoke
bounded work inside already accepted production/test ownership. It never closes
the task, widens authority, approves protected work, commits, or pushes.

Before any lifecycle mutation, read and follow
`references/lifecycle-lock.md`. Resolve it relative to the directory containing
the already loaded `task-cycle/SKILL.md`, never the repository working
directory. It is normative for acquisition, ownership metadata, nested work,
compare/write, release, and stale recovery. If it cannot be read, return
`BLOCKED: TASK_LIFECYCLE_LOCK_UNAVAILABLE`. Read-only task resolution may
happen before acquisition, but no lifecycle read-modify-write may begin until
the exact task's shared lock is held.

Also read `references/reviewed-evidence-identity.md` from the same installed
skill directory. It is normative for contract fingerprint, reviewed revision,
evidence fingerprint, readiness, and closure identity. If unavailable, return
`BLOCKED: EVIDENCE_IDENTITY_PROTOCOL_UNAVAILABLE` before mutation.

## 1. Resolve one exact task

1. Resolve the current repository unless one exact `--repo` or `--project` is
   supplied. Never guess between repositories.
2. Read repository instructions, scoped rules, task conventions, and accepted
   architecture decisions.
3. Resolve a complete ID only as `production/tasks/<ID>/contract.md`; accept an
   explicit in-repository contract path. Never fall back to an epic/story or
   reinterpret a missing ID as prose.
4. Require complete contract authority with readiness `ready`. A closed task is
   valid input; closure is lifecycle state, not contract invalidation.
5. Read lifecycle state from the delimited block. For a legacy task only, read
   sibling `status.md` when the block is absent and migrate on the first genuine
   transition. Never create, update, or delete `status.md`.
6. Compute the contract fingerprint from authority outside the managed block,
   then capture the reviewed code/asset revision and dirty fingerprint.

## 2. Maintain one ledger and linked evidence records

The managed block contains this canonical ledger:

```markdown
### Defect ledger

| ID | Dedupe key | Status | Relation | Maps to | Symptom / repro | Latest evidence | Verified revision |
|---|---|---|---|---|---|---|---|
| [D-001](defects/D-001.md) | ac_failure:ac-1:muzzle-flash-first-frame-white | OPEN | AC_FAILURE | AC-1 | First flash frame is white. | user observation at fixture-r1 | none |
```

Each populated row has exactly eight cells in that order. The dedupe key is one
stable normalized value and must not introduce extra pipe delimiters. Escape a
literal `|` inside evidence text. `Verified revision` is `none` for every
non-`VERIFIED` status; only fresh defect-specific verification may populate it.

Every populated ID cell is a relative link such as
`[D-001](defects/D-001.md)`. Read
`references/defect-record-template.md` before creating or updating a record.
Resolve it from the loaded `task-cycle/SKILL.md` directory as well; never from
the target repository working directory.
Each atomic symptom has exactly one record. The record holds observation,
reproduction, expected/actual behavior, source links, and an append-only
evidence timeline; current status remains canonical only in this ledger.
When a verifier returns an exact machine result token, preserve that token
byte-for-byte in the defect record's evidence timeline, for example
`VERIFY: PASS (3/3)`. Command and revision context may be added around it, but
never replace the token with a prose summary.

Template availability is a write precondition. If the installed reference
cannot be read, stop `BLOCKED: DEFECT_TEMPLATE_UNAVAILABLE` before creating a
row or record; never invent a reduced schema. A valid child record contains
both `DEFECT-METADATA` markers, both `DEFECT-EVIDENCE` markers, linked `Parent
task` and `Ledger` fields, `Relation`, `Maps to`, and the expected/actual
sections. It must not contain generated current-status, dedupe-key, attempt,
close-readiness, or next-action fields because those belong to the ledger.

`task-cycle` is the only lifecycle command allowed to create defect records or
add, deduplicate, reopen, and transition ledger rows. `task-bug` only resolves
and dispatches; `create-task` initializes an empty table. Implementers,
verifiers, status, handoff, and closure commands report evidence but do not
write defect state or records.

Before ingesting new feedback or judging closure, reconcile ledger links and
child records under the same single-writer lock:

1. A populated ledger ID with a missing record is legacy/incomplete state, not
   a new defect. Recreate that exact `D-xxx.md` from retained ledger, handoff,
   and source evidence; preserve the ID, dedupe key, status, and attempt count.
2. A plain or malformed ID cell may be changed only to the canonical relative
   link for that same verified record. Never allocate a new ID for backfill.
3. Repair parent, ledger, relation, mapping, and source fields only inside the
   record's `DEFECT-METADATA` block when provenance is unique. For a legacy
   record without markers, wrap only the generated metadata once and preserve
   manual prose and the evidence timeline byte-for-byte.
4. If two records claim one ID, a record claims another task, or provenance is
   ambiguous, stop `BLOCKED: DEFECT_RECORD_INTEGRITY`; do not guess or close.

Reconciliation is idempotent, consumes no implementation attempt, and is
confirmed by re-reading the ledger link plus record before continuing.

Allowed statuses are:

```text
OPEN | REPRODUCING | FIXING | FIXED_UNVERIFIED | VERIFYING | VERIFIED | BLOCKED
```

Allowed relations are:

```text
AC_FAILURE | PRESERVATION_FAILURE | TASK_REGRESSION
```

Only `VERIFIED` is terminal. A code change or implementer claim can produce at
most `FIXED_UNVERIFIED`; independent fresh evidence is required for `VERIFIED`.

## 3. Ingest feedback relation-first

When feedback or new evidence is present:

If the input is an explicit user acceptance of one or more named acceptance
criteria, treat it as a verification result rather than defect evidence. Under
the lifecycle lock, record the named criteria—or all criteria when the user
unambiguously accepts all—as `PASS` with `Verification: explicit user
acceptance` at the current reviewed revision. Require no log, screenshot,
artifact, or additional proof; preserve every defect row and continue directly
to close-readiness evaluation. Generic praise, a question, or a conditional
statement is not acceptance.

Before reporting reuse or recurrence, acquire the task lifecycle-writer lock
and re-read the current contract fingerprint, reviewed revision, complete
ledger row, and linked `D-xxx.md` record. Compare relation, `Maps to`, normalized
observable symptom/repro, latest evidence, status, and verified revision. Do
not treat wording, area/path overlap, a conversation summary, or an earlier
assistant claim as canonical defect identity.

1. Split it into atomic, independently observable symptoms. Do not merge
   several failures because they may share one suspected root cause.
2. Classify relation before checking write authority:
   - failure of an existing acceptance criterion -> `AC_FAILURE`;
   - failure of preserved behavior -> `PRESERVATION_FAILURE`;
   - regression caused by this task's changes -> `TASK_REGRESSION`, even when
     the exact symptom was not written as an acceptance row.
3. A separate player-facing outcome, explicit non-goal, or unrelated
   pre-existing defect is new scope. Do not add it to this ledger; report it as
   `NEW_TASK_REQUIRED` after retaining any separable same-task defects.
4. Map each same-task symptom to the narrowest criterion, preserved behavior,
   or task-caused regression seam. Create the next stable `D-xxx` ID and its
   linked `defects/D-xxx.md` record only when no semantic match exists. Create
   one record per atomic symptom even when several symptoms share a root cause.
5. Build the dedupe key from the relation, mapped behavior, and normalized
   observable symptom/repro—not the reporter's exact wording or a guessed root
   cause. Exact repeats and paraphrases reuse the same ID and record. Update
   neither unless material evidence was added. The same input, revision, and
   evidence must preserve the lifecycle block and record byte-for-byte.
6. If a `VERIFIED` symptom has materially new failing observation evidence at
   the current or later reviewed revision, confirm recurrence, reopen the same
   ID as `OPEN`, mark its old proof stale, and append one recurrence entry to
   the same record plus one lifecycle transition. Repeated wording without new
   failing evidence is idempotent and does not reopen the row.
7. Record one explicit match result before repair:
   `CONFIRMED_REUSE <D-xxx>`, `CONFIRMED_RECURRENCE <D-xxx>`,
   `NEW_DEFECT <D-xxx>`, or `AMBIGUOUS`. `AMBIGUOUS` performs no defect write
   and requests the smallest missing evidence; never guess from conversation.

If same-task relation is clear but current paths, ownership, architecture, or
risk do not authorize the repair, still create/reuse the linked evidence record,
keep the ledger row on this task as `BLOCKED`, and return
`CONTRACT_CHANGE_REQUIRED`. This low-risk lifecycle documentation is not repair
authority. Relation is never reclassified as new scope merely because
production authority is insufficient.

## 4. Reopen closed tasks safely

For lifecycle state `closed`:

- no new failing evidence -> `TASK_CLOSED`, byte-for-byte unchanged;
- same-task feedback -> reopen the task, retain/reopen the matching ledger row,
  mark affected evidence `FAIL` or `STALE`, and continue;
- same-task feedback requiring wider authority -> reopen as `blocked`, record
  the defect as `BLOCKED`, and return `CONTRACT_CHANGE_REQUIRED`;
- only distinct scope -> `NEW_TASK_REQUIRED` without reopening.

Reopening is idempotent for the same defect/evidence/revision. Closure alone is
never a reason to create a duplicate task or a second record.

## 5. Classify evidence and completion

Inspect the contract, current diff/revision, handoffs, retained test/build
reports, screenshots, playtest/profiler evidence, ownership, and every ledger
row. Mark required acceptance channels `PASS`, `FAIL`, `UNPROVEN`, or `STALE`.

Automated success never substitutes for a required manual visual, real-scene
PlayMode, built-player, device, audio, feel, or profiler check. A user-observed
runtime failure is `FAIL` even when nearby automation passes.

For each unresolved defect, prefer this evidence loop:

```text
capture -> reproduce -> minimise -> hypothesise -> targeted instrument
-> regression signal -> surgical fix -> original repro -> regression checks
```

Use a deterministic failing signal at the correct public/runtime seam when
practical. Do not accept a different green test as proof, add broad permanent
logging, or leave temporary instrumentation behind.

Keep diagnosis claims at separate evidence levels:

- `OBSERVED`: the exact externally visible failure and reproduction channel;
- `CANDIDATE_MAPPING`: the possible criterion and defect ID before canonical
  confirmation;
- `ROOT_CAUSE_HYPOTHESIS`: a falsifiable suspected mechanism and the check that
  could disprove it;
- `CONFIRMED_ROOT_CAUSE`: supported by reproduction, instrumentation, or a
  regression signal that distinguishes it from plausible alternatives.

Never promise a particular code change before the reproduction differentiates
the competing paths. For example, a suspected input focus/rebind ordering issue
remains `ROOT_CAUSE_HYPOTHESIS` until the arrow-key and dropdown paths are
observed at the same public seam.

Choose the effective outcome using these gates:

1. identity, transport, ownership, protected-risk, or manual-evidence blocker;
2. same-task authority conflict -> `CONTRACT_CHANGE_REQUIRED`;
3. unresolved same-task defect -> `CONTINUE_SAME_TASK` when safely actionable;
4. distinct outcome only -> `NEW_TASK_REQUIRED`;
5. `READY_TO_CLOSE` only when all conditions below hold.

Close readiness requires all of the following at the current reviewed revision:

- every required acceptance and preservation channel is fresh `PASS`;
- every defect ledger row is `VERIFIED` with original-repro/regression evidence;
- every populated ledger ID links to one existing child record whose ID,
  parent task, relation, and mapping agree with the ledger;
- zero rows are `OPEN`, `REPRODUCING`, `FIXING`, `FIXED_UNVERIFIED`,
  `VERIFYING`, or `BLOCKED`;
- no feedback remains unclassified;
- scope containment, serialized ownership, and required risk gates pass.

All defects being verified is necessary but not sufficient when another
required channel remains unproven. Likewise, green acceptance rows never hide
an unresolved defect.

Use the installed Unity CLI first for exact-project inspection: verify the
command, prove identity with `unity status --json`, and pass `--project-path`
when needed. If the CLI is missing, install it under the standing authorization.
Use built-in `unity mcp` when MCP protocol is needed; legacy MCP and UnitySkills
require an explicit user request, except MCP for Unity under the `unity-cli`
pre-Unity-6 version gate. Never repeat one mutation through two paths.

## 6. Record transitions and evidence idempotently

Edit only `TASK-LIFECYCLE` plus the managed metadata and evidence blocks of
linked defect records. Record task state, phase, fingerprints, reviewed revision, cycle
verdict, attempt count, normalized feedback, acceptance criteria and their
verification channels, defect rows,
blocker, next action, closure data, and compact history. Record documents append
only material defect-specific intake, reproduction, fix, verification, or
recurrence evidence; they never duplicate the current ledger status.

New contracts name the acceptance table and third column `Acceptance criteria`
and `Verification`. Treat legacy `Acceptance evidence` and `Evidence` labels as
the same managed structure and do not rename them during lifecycle-only writes.

- new failures start `OPEN`;
- active diagnosis/fix may move through `REPRODUCING` and `FIXING`;
- an implementer-supported fix becomes `FIXED_UNVERIFIED`;
- independent verification uses `VERIFYING`, then `VERIFIED` only with fresh
  defect-specific proof;
- a later relevant code/asset change stales `VERIFIED` proof and returns the
  affected row to `FIXED_UNVERIFIED`;
- a safety/authority stop uses `BLOCKED` without deleting evidence.

Map ordinary continuation to task state `in_progress`; a reopened task remains
`reopened` until close-ready or blocked. Map close readiness to
`ready_to_close`. Preserve the block byte-for-byte when nothing semantic
changed and append one history entry per genuine transition.

Compute the terminal `Reviewed revision` and `Evidence fingerprint` only after
the final relevant production/test change or recorded user acceptance, using
`references/reviewed-evidence-identity.md`. Every `PASS` acceptance row and
every `VERIFIED` defect row must name that exact reviewed revision. A planning
base revision, prior-cycle fingerprint, timestamp, or child-agent claim is
stale evidence and cannot support `READY_TO_CLOSE`.

Serialize all lifecycle writes for one task. Before the first lifecycle
read-modify-write, atomically acquire the authoritative
`<git-common-dir>/ccgs/task-lifecycle-locks/<TASK-ID>.lock.claim` file with
`FileMode.CreateNew`, then materialize the companion `<TASK-ID>.lock/`
metadata directory and confirm the tokens in both the claim and `owner.json`
exactly as the loaded lock protocol requires.
Then re-read the current contract, complete ledger, linked records,
fingerprints, and reviewed revision. Hold that same ownership through every
transition and the complete implementer -> verifier -> optional bugfixer ->
verifier loop. If acquisition reports a live owner, perform no write and emit
the non-terminal scheduling state `WAITING_FOR_OWNER`. When this invocation or
its parent orchestrator can observe the owner, keep the authorized work queued,
wait for the provider completion event or claim-file release, then re-read and
retry automatically. Never ask for another command, steal, overwrite, or start
a second writer. If no monitor can remain active, report that exact operational
limitation and owner identity; do not label the task persistently blocked.

Pass the exact lock path and owner token in `CycleContext` to each nested
`implement-task`. The child validates and reuses the parent lock; it never
reacquires or releases it. Wrap the owned cycle in a `finally`/guaranteed
cleanup path. On every exit, re-read the claim and `owner.json`; only when both
tokens exactly match this cycle may it remove the metadata directory first and
the authoritative claim file last. Leave a mismatched lock intact and report
the ownership failure; never remove another owner's lock.

Immediately before a ledger or record write, re-read the contract lifecycle
fingerprint and target record. If another writer changed them, deduplicate from
the latest state or stop `BLOCKED: TASK_LIFECYCLE_BUSY`; never overwrite stale
state. One logical transition updates the ledger link and new record together,
then re-reads both to confirm consistency. Validate that every populated ledger
row still has exactly eight cells and that unresolved rows have `Verified
revision: none`. Also validate the required record markers/fields and absence
of duplicated lifecycle fields. Repair a just-created invalid record before
reporting, or stop `BLOCKED: DEFECT_RECORD_INTEGRITY`. Different tasks may use
separate lifecycle writers.

## 7. Continue automatically

For `CONTINUE_SAME_TASK`:

1. Invoke `implement-task <ID>` internally with `CycleContext` containing the
   lifecycle lock path and owner token, task ID, attempt, contract/revision
   fingerprints, all unresolved defect IDs, exact repros, feedback,
   failed/unproven criteria, and the detected project domain.
2. For a Unity-shaped repository or Unity contract, require `implement-task` to
   invoke `unity-preflight` first and `unity-game-dev` after it passes, before
   Unity diagnosis, production/test mutation, or verification. Do not run a
   competing preflight inside the cycle; preserve the handoff result from the
   implementation lane. `task-bug` remains a read-only router and does not
   replace or pre-run either workflow. A Unity handoff that omits
   a safe `Unity preflight: READY`/`READY WITH WARNINGS` verdict or
   `Domain workflow: unity-game-dev` is incomplete evidence and cannot advance
   a defect to `FIXED_UNVERIFIED` or `VERIFIED`.
3. Treat feedback and defect rows as evidence, never new authority. Do not
   widen scope, ownership, acceptance, architecture, or risk.
4. Force `commit: none`. Keep implementer -> verifier -> optional bugfixer ->
   verifier sequential for one task. Bugfixer output never self-verifies.
5. Require each role to return defect IDs, root cause or hypothesis, changed
   paths, exact checks, revision, and defect-specific evidence.
   A root cause may be labelled confirmed only when the returned evidence
   distinguishes it from plausible alternatives; otherwise retain the explicit
   hypothesis label and run the next bounded evidence action.
6. Resume this cycle without another operator command, transition rows, and
   classify all remaining defects—not only the last one mentioned.

After every internal `implement-task` and verifier handoff, the parent cycle
must finish the lifecycle work before returning:

7. Do not forward the child skill's final answer or its suggested next command.
   Re-read the owned bytes, current contract, complete ledger, linked records,
   and independent verifier evidence while retaining the same lock.
8. Move an implementer-supported repair only to `FIXED_UNVERIFIED`; move it to
   `VERIFIED` only after fresh defect-specific verification of the original
   repro and required regressions. Reclassify every acceptance/preservation
   criterion at the same reviewed revision. A criterion may be verified by an
   automated test, manual verification, or explicit user acceptance; do not
   demand extra artifacts for the user-acceptance channel.
9. If all close-readiness gates pass, compute the canonical reviewed revision
   and evidence fingerprint, then atomically record:
   - `Task state: ready_to_close`;
   - `Current phase: verification`;
   - `Last cycle verdict: READY_TO_CLOSE`;
   - fresh `PASS` acceptance-criteria rows and current-revision `VERIFIED` rows;
   - `Blocker: none`;
   - `Next action: $task-done <ID>`, replacing any earlier verification, rerun,
     implementation, or cycle command;
   - one transition-history entry.
   Keep closure fields `none`, re-read and validate the identities, then return
   the complete canonical `TASK CYCLE` block from section 8. In that block, the
   close fields must be exactly `Terminal verdict: READY_TO_CLOSE` and
   `Next: $task-done <ID>`; do not substitute prose or a child workflow's
   result schema.
10. If any gate remains unresolved, continue the bounded loop or record the
    exact blocker. Never return `$task-cycle <ID>` as the next command from an
    already active cycle and never leave a passing child result merely
    `in_progress`.

Run at most three implementation attempts and stop after two genuine
no-progress attempts with `BLOCKED: NO_PROGRESS`; after three incomplete
attempts use `BLOCKED: AUTO_CYCLE_LIMIT`. An identical duplicate report or a
still-blocked defect with no new evidence does not consume an attempt. Preserve
all ledger rows at either stop and never create a replacement task.

If only user judgment remains and no explicit user acceptance has been given,
stop `ACTION_REQUIRED: USER_ACCEPTANCE` without spending an implementation
attempt. Name the exact criterion to approve; do not demand a log, screenshot,
artifact, or other proof. A subsequent explicit acceptance may satisfy the
criterion, while an explicit close order routes directly to `task-done`.

## 8. Independent outcome split and dispatch

When feedback contains a second independently closable outcome outside the
current contract, retain all same-task evidence first and split it
automatically. Do not make the current contract absorb the new outcome or stop
at a manual `create-task` suggestion.

1. Write the current cycle evidence and release its lifecycle lock.
2. Invoke `$create-task` exactly once with the bounded independent outcome.
3. If creation returns exactly one `ready` task, invoke
   `$game-studio-orchestration <current-id> <new-id>` automatically. It must
   build the conflict graph first, use separate worktrees/branches for
   disjoint writers, keep each implementer -> verifier chain sequential, and
   queue single-Editor work.
4. If one exact live predecessor owns overlapping writable paths, serialized
   assets, or required dirty changes, register the new task as
   `QUEUED_AFTER_OWNER`, keep one writer, and wait for its stable handoff plus
   lock release. Then revalidate and dispatch the successor automatically in
   the same worktree when it must inherit uncommitted changes. Use
   `PARALLEL BLOCKED` only when the owner/order cannot be proven, dirty changes
   cannot be attributed, or another safety gate has no deterministic handoff.
   If creation is ambiguous or not ready, return `NEW_TASK_REQUIRED` without
   guessing an ID.

Only a distinct outcome may split. Accepted/preserved behavior failures remain
defects in this task and continue through its ledger; they never become a
parallel child task.

An automatic split report includes:

```text
Split: <current-id> + <new-id | creation result>
Orchestration: DISPATCHED_PARALLEL | QUEUED_AFTER_OWNER | QUEUED_EDITOR |
               PARALLEL_BLOCKED | NOT_DISPATCHED
```

## 9. Stop gates and report

- `READY_TO_CLOSE` -> `$task-done <ID>`;
- distinct new outcome -> automatic split-and-dispatch above; use
  `NEW_TASK_REQUIRED` only when creation or orchestration cannot safely proceed;
- `CONTRACT_CHANGE_REQUIRED` -> one exact authority/approval decision;
- `WAITING_FOR_OWNER` scheduling result -> write no lifecycle state without the
  lock; retain the authorized invocation in the orchestrator queue and resume
  automatically after the exact owner releases;
- `BLOCKED` terminal verdict -> persist task state `waiting`, one
  `Waiting reason`, and one `Action required`. Never persist task state
  `blocked`; the verdict describes this attempt, not a dead task.

Never automatically invoke `task-done`.

Every terminal return must use the complete canonical `TASK CYCLE` block below.
Do not return only a verdict/next pair or forward a child workflow's schema.

```text
TASK CYCLE
ID: <id>
Contract: production/tasks/<id>/contract.md
Previous state: <state>
Current state: in_progress | reopened | ready_to_close | waiting | closed
Reopened: yes | no
Attempts: <0-3>
Terminal verdict: READY_TO_CLOSE | NEW_TASK_REQUIRED |
                  CONTRACT_CHANGE_REQUIRED | WAITING_FOR_OWNER | BLOCKED |
                  TASK_CLOSED
Acceptance criteria: <PASS/FAIL/UNPROVEN/STALE summary; verification channels>
Defect match: CONFIRMED_REUSE <ID> | CONFIRMED_RECURRENCE <ID> |
              NEW_DEFECT <ID> | AMBIGUOUS | none
Defects: <n unresolved [IDs]> | <n verified [IDs]>
Defect records: <relative linked paths | none>
Diagnosis: <OBSERVED; ROOT_CAUSE_HYPOTHESIS; CONFIRMED_ROOT_CAUSE or none>
Unity preflight: READY | READY WITH WARNINGS | BLOCKED | NOT_APPLICABLE
Domain workflow: unity-game-dev | <other skills> | none
Changed paths: <task-attributable paths | none>
Verification: <fresh defect-specific evidence and gaps>
Scope/ownership: PASS | <finding>
State record: contract.md#TASK-LIFECYCLE | unchanged | not written
Next: <one command or exact unblock action>
```
