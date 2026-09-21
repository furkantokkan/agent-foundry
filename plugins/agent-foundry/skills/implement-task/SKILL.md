---
name: implement-task
description: Resolve and initially execute a task ID, contract path, story path, or bounded ad-hoc request with focused verification. Automatically route raw post-implementation bug feedback through task-bug. Treat an explicit user acceptance of named criteria as a verification continuation for the exact or sole retained task; it needs no artifact. Treat an immediate plain continue phrase as execution only for the sole newly returned ready task.
---

# Implement Task

Treat the full user request as one raw `TaskInput`. Preserve quoted paths,
pasted logs, images, URLs, and natural-language constraints. Never interpolate
it directly into a shell command.

The canonical interface is:

```text
$implement-task <task-id | contract-path | natural-language> [execution-overrides]
```

Prefer a task ID or exact contract path for production work. The contract is
the durable source for scope and acceptance; the invocation starts one
execution. Read `references/argument-contract.md` before parsing flags or
resolving a task ID, and apply its conflict and safety-order rules exactly.

Unity execution hard gate: after resolving the exact task/repository and before
any lifecycle, production, test, or evidence mutation, invoke
`unity-preflight`; only a non-blocking result may proceed to
`unity-game-dev`. Load that domain skill before diagnosis or mutation. Reading
the contract and owned files is allowed before this gate, but patching is not.
Then acquire or reuse the task lifecycle lock required in Section 2 before the
first mutation.

## 0. Route lifecycle feedback first

Before planning writes, determine whether the input is an initial execution or
post-implementation feedback for a durable tracked task.

Before applying bug-feedback routing, treat an immediately following plain
`devam et`, `continue`, or `go ahead` as an explicit invocation of the exact
task only when the immediately preceding assistant result newly returned
exactly one tracked task with `Contract status: ready` and its exact ID/path.
Resolve that task as initial execution. Do not auto-select when that result
contains zero or multiple ready tasks, an unrelated user request intervened, or
the exact identity is unavailable; require an ID/path or use normal routing.

Before classifying bug feedback, treat an unambiguous statement such as
`AC-1'i onaylıyorum`, `kriterleri onaylıyorum`, or `I accept the criteria` as a
verification continuation when it names an exact task or the conversation
retains exactly one unambiguous task. Record the named criteria, or all criteria
when the statement unambiguously covers all of them, as `PASS` with
`Verification: explicit user acceptance` at the current reviewed revision. Do
not require a test log, screenshot, artifact, reproduction, or additional
proof, and do not alter defect rows. When the ledger is populated or a
`CycleContext` exists, forward the accepted criteria to `task-cycle` under its
existing lifecycle ownership instead of writing a competing direct
transition. Generic praise, a question, or a conditional statement is not
acceptance.

1. Treat an observation such as `still broken`, a failed manual/playtest check,
   or a new screenshot/log after an implementation or verifier handoff as
   post-implementation feedback when it names or uniquely resolves an active
   `production/tasks/<ID>/contract.md`. This trigger applies to plain chat
   feedback; the operator does not need to type a slash command.
2. On direct feedback, do not edit, create a replacement task, or decide
   same-task scope yourself. Invoke `$task-bug [<ID>] <raw-feedback>` internally
   while preserving every observation and attachment. The intake skill owns
   exact/automatic task matching; `task-cycle` alone splits, relates,
   deduplicates, links `defects/D-xxx.md`, and writes defect ledger rows.
   Any `D-xxx` found in conversation or a prior summary is a candidate only.
   Do not announce confirmed reuse, recurrence, reopen, root cause, or a chosen
   code fix before task-cycle returns canonical evidence.
3. If that tracked task is `closed`, forward the feedback to `task-bug` too.
   Its downstream cycle reopens it automatically only when the observation fails existing
   acceptance/preserved behavior and remains inside accepted ownership and
   risk. New scope still returns `NEW_TASK_REQUIRED`; wider authority returns
   `CONTRACT_CHANGE_REQUIRED`.
4. Proceed directly only for initial execution, a contractless ad-hoc task, or
   an internal task-cycle handoff carrying CycleContext: ID, attempt,
   fingerprints, every unresolved `D-xxx` ID with its exact repro, and
   failed/unproven criteria. Return defect-specific evidence directly to the
   active cycle in the last case; do not transition ledger rows yourself.

This router is automatic. Do not ask the operator to type another command for
feedback that can be safely forwarded.

## 1. Resolve repository and input

1. Use the current repository unless `--repo` or `--project` identifies one
   other exact path or unique repository name. This selects the repository; it
   grants no write scope. Never guess between ambiguous repositories.
2. Read repository-local `AGENTS.md`, `CLAUDE.md`, their declared reading order,
   and nearest path-scoped instructions before planning edits.
3. Classify the first positional value as one of:
   - an existing repository file path;
   - a task ID matching the repository's established ID format (for example
     `GAME-123`), normally a compact key containing a project prefix and digit;
   - natural-language work.
4. Resolve a task ID such as `GAME-123` only as
   `production/tasks/GAME-123/contract.md`. Match the complete ID, not a loose
   numeric substring. A missing recognized ID returns `CONTEXT BLOCKED`; do not
   fall back to an epic/story or reinterpret it as natural language.
5. An explicit file path wins over ID search. Keep it inside the resolved
   repository. If it is a story rather than a task contract, load the story and
   derive a bounded execution contract without weakening story requirements.
6. Detect the real project topology, engine/runtime version, manifests,
   version-control system, nested repositories, and verification commands.
   Snapshot dirty work and preserve unrelated changes.

Code, manifests, tests, and current runtime evidence outrank stale roadmaps or
memories. Report material documentation drift instead of implementing an
aspirational architecture that the owning subsystem does not use.

## 2. Load the canonical task contract

When `production/tasks/<id>/contract.md` or an explicit contract exists, load
these fields from it rather than asking the operator to repeat them:

- objective, kind, area, baseline, and expected behavior;
- allowed/forbidden paths, exclusions, and serialized-asset sole writer;
- acceptance criteria and behavior to preserve;
- references, tests, workflow, risk, approval gates, and handoff.

Read `Contract status` before implementation. `draft` contracts may be
inspected in `plan`/`diagnose` mode but must return `ACTION_REQUIRED`
before production mutation. For a legacy contract without a status field,
validate that objective, ownership, acceptance, preserved behavior, risk, and
verification are complete; do not assume an incomplete artifact is ready.
Treat legacy `blocked` contracts as `draft` and report their exact
`Waiting reason` plus `Action required`; never create a new blocked state.

Read current execution state from the contract's delimited `TASK-LIFECYCLE`
block. For a legacy task without that block, read a sibling `status.md` only as
migration context; never create or update `status.md`. `CONTINUE_SAME_TASK`
identifies remaining work inside the current authority. `READY_TO_CLOSE` means
implementation should not resume without new evidence; direct the operator to
`$task-done <ID>`. `NEW_TASK_REQUIRED`, `CONTRACT_CHANGE_REQUIRED`, or
`BLOCKED` must not be bypassed. A `closed` task with new feedback routes through
Section 0 instead of being rejected. If code/evidence changed after review,
treat prior evidence as stale and continue only within unchanged authority.

Read the managed defect ledger as execution context, never as additional
authority. Initial implementation may proceed with an empty ledger. During an
internal cycle call, work only on the supplied unresolved defect IDs and their
accepted seams. `FIXED_UNVERIFIED` is the strongest defect state an implementer
claim can support; `task-cycle` owns state transitions and independent verifier
evidence is required for `VERIFIED`.

The direct-initial lane requires all four conditions: no `CycleContext`, task
state `ready`, `Attempt count: 0`, and a header-only empty defect ledger. A
populated ledger or a resumed `in_progress`/`reopened` task with recorded
defect work belongs to `$task-cycle`; dispatch it there rather than mutating
production in a second direct lane. An empty-ledger task whose only remaining
channel is required user/environment verification stays in the direct
non-defect lane: a verification continuation may reacquire this task's lock,
run or record the missing verification or explicit user acceptance, and
finalize it without changing
production. If that continuation produces a real acceptance failure, route
the raw observation through `$task-bug` and let `$task-cycle` own the defect.

For a direct tracked invocation, before any contract, lifecycle, production,
test, or evidence mutation, read and follow
`../task-cycle/references/lifecycle-lock.md`. Resolve `..` from the directory
containing the already loaded `implement-task/SKILL.md`, never from the target
repository working directory. Atomically acquire the exact
task's shared Git-common-dir lock, confirm its owner token, re-read canonical
state under the lock, hold it through the complete direct
implementation/verifier handoff, and release it from a `finally` path only when
both the authoritative `.lock.claim` file and `owner.json` still contain that
exact token. If direct acquisition finds one proven live owner, perform no
write and hand the still-authorized invocation to `game-studio-orchestration`
as `WAITING_FOR_OWNER`. It must wait for owner completion/claim release,
revalidate, and retry automatically without another user command. Do not turn a
live, ordered owner into a persistent blocked task or request stale recovery.
For an internal `task-cycle`
handoff, require the lock path and owner token in `CycleContext`, re-read and
validate them, and reuse the parent lock. Never acquire, replace, or release a
nested lock; a missing or mismatched token is
`BLOCKED: TASK_LIFECYCLE_BUSY`.

Also read
`../task-cycle/references/reviewed-evidence-identity.md` from that same installed
skill directory. It is the canonical algorithm for contract fingerprint,
reviewed revision, evidence fingerprint, readiness, and later closure checks.
If it is unavailable, a direct tracked execution may inspect but must stop
before mutation with `BLOCKED: EVIDENCE_IDENTITY_PROTOCOL_UNAVAILABLE`.

The contract is canonical for this execution boundary. A referenced story/GDD
remains canonical for product intent; the contract may narrow execution but may
not contradict or weaken that intent.

Command flags that restate contract fields are redundant. Treat an exact
restatement as a no-op. If a command flag changes or expands persistent scope,
ownership, acceptance, workflow, or risk, stop before mutation:

```text
CONTRACT CONFLICT:
Command attempts to expand or weaken the accepted task contract.
Update the contract before implementation.
```

List the conflicting contract value and command value. Never merge them by
guessing. Invocation overrides may only preserve or increase safety.

## 3. Apply execution overrides

Only these normally belong on a contract-backed invocation:

- `--repo`/`--project`: choose another repository before contract resolution;
- `--mode implement|plan|diagnose`: select this run's behavior;
- `--verify auto|focused|full|built-player`: keep or raise evidence depth;
- `--context auto|current|history`: choose this run's context breadth;
- `--dirty-policy preserve|worktree`: preserve current work or raise isolation;
- `--commit none|after-pass`: invocation-local local-commit permission.

Safe defaults are `implement`, `auto`, `auto`, `preserve`, and `none`. A stricter
contract or detected risk wins. Verification order is
`focused < full < built-player`; `auto` means the contract/repository minimum.
`built-player` adds applicable cheaper checks rather than replacing them.

`--commit after-pass` is valid only when supplied in the current invocation,
all required checks pass, and repository/contract policy does not forbid a
local commit/checkin. A stored contract can constrain commits but can never
grant future `after-pass` permission. No flag authorizes push, PR creation,
deploy, publishing, migration apply, or Remote Config changes.

Legacy persistent flags such as `--kind`, `--area`, `--scope`, `--allowed`,
`--forbidden`, `--serialized`, `--accept`, `--preserve`, `--reference`,
`--exclude`, `--test`, `--workflow`, `--handoff`, and `--risk` remain accepted
for contractless automation. With an existing contract they cannot alter it;
`--risk` may only raise caution.

## 4. Build a contract only when missing

For natural language or a story without a task contract, inspect the repository
and assemble the smallest safe execution contract. Before editing, show a short
summary containing objective, baseline, expected/preserved behavior, exact
allowed/forbidden paths, serialized ownership, acceptance, verification,
workflow, risk, dirty policy, and commit status.

Infer missing low-risk details and proceed. Ask one focused question only when
a product, architecture, ownership, or data choice would materially change the
result. Prefer `$create-task [<id>] "<request>"` when the work should become a
durable production contract. Legacy `--save-contract auto` remains supported;
an explicit save path must remain inside the target repository. Without either,
the inferred contract is execution-local.

Only follow-ups to a contractless execution-local task may revise its inferred
contract. Keep earlier constraints and add new evidence instead of starting a
new architecture. Follow-up feedback for a durable tracked task always uses the
lifecycle router in Section 0 and never mutates its immutable contract.

## 5. Enforce ownership and risk

- Low risk: scoped source, focused tests, and evidence may be edited
  autonomously within the accepted contract.
- Medium risk: a new assembly/module, public contract, or cross-system boundary
  requires a concise plan decision before writing.
- High risk: dependencies, Unity serialized assets, project/global settings,
  save/network schemas, migrations, destructive operations, deployment, and
  releases require exact authorization.
- Independent tasks use separate branches/worktrees and disjoint ownership.
- One task's implementer, verifier, and bugfixer hand off sequentially.
- A Unity serialized asset has exactly one writer.

Use subagents only for useful read-only work or independent disjoint changes.
Never let orchestration expand the contract.

## 6. Inspect, implement, and verify

1. Reproduce a bug or capture a comparable performance baseline when practical.
   For cycle work, establish a deterministic failing signal for each supplied
   defect at its original public/runtime seam before changing code when that
   seam is available.
2. Select the smallest relevant installed skills and role guidance.
   A Unity-shaped repository or a contract that targets Unity runtime, Editor,
   C#, assets, tests, UI, input, animation, physics, or build behavior must first
   invoke the installed `unity-preflight` skill. Stop before mutation when its
   exact-repository, transport, ownership, dirty-work, or verification-readiness
   result blocks execution. After preflight passes, invoke the installed
   `unity-game-dev` skill before Unity-specific diagnosis, planning,
   production/test mutation, or verification. Both remain mandatory when the
   call came from `task-cycle`; lifecycle skills do not replace preflight or
   domain expertise. Add `unity-optimization` for measured performance work or
   another specialized skill only when the task actually needs it. Do not load
   every Unity skill by default.
3. Preserve established architecture and naming; do not introduce a competing
   framework or migrate adjacent systems incidentally.
4. Make surgical edits only inside the accepted contract and add focused tests
   for changed expected behavior where supported.
5. On the first genuine execution transition, update only the contract's
   managed lifecycle block to `in_progress` while holding the direct invocation
   lock; do not create `status.md`. When called by `task-cycle`, let the cycle
   own lifecycle transitions and keep using its validated parent lock.
6. Run focused checks first, then compilation/build and broader checks required
   by the effective verification depth and risk.
7. Separate pre-existing failures from regressions. Do not regenerate golden
   fixtures merely to force a pass. A nearby green test does not prove a
   reported runtime symptom; rerun the original repro and required regression
   channel after the fix.
8. For Unity, use the installed CLI first, prove the exact target with
   `unity status --json`, and pass `--project-path` when needed. If CLI/Pipeline
   is unavailable or insufficient, use exact-project Unity MCP, then
   target-matched UnitySkills. Never duplicate a mutation across transports,
   and edit Unity YAML manually only as a last resort.
9. Inspect the final diff for containment, generated churn, secrets, and
   acceptance coverage.
10. Build an acceptance-to-verification matrix using each channel required by
   the contract. A criterion may be verified by an automated test, manual
   verification, or explicit user acceptance. Automated tests cannot
   substitute for a criterion that specifically requires visual, real-scene
   PlayMode, built-player, device, audio, feel, or profiler judgment.

Mark every required criterion `PASS`, `FAIL`, `UNPROVEN`, or `STALE`. A green
test suite with an unperformed required manual check is `UNPROVEN`, not
complete. Explicit user acceptance may turn the named criterion into `PASS`
without an artifact. User-observed runtime failure is `FAIL` even when all
automated tests pass. If user judgment remains, name the criterion to approve;
do not spend another implementation attempt merely to manufacture proof.

Keep every acceptance-criteria row's `Result` and `Freshness` cells separate.
New contracts name the third column `Verification`; treat a legacy `Evidence`
column as the same verification field and do not rename it during a lifecycle
write.
At every lifecycle write, each `Freshness` cell must equal the complete
top-level `Reviewed revision` token byte-for-byte. If `Reviewed revision` is
`none`, the cell is exactly `none`; after review, copy the full VCS-plus-owned
digest token. Never write `fresh`, `current`, `pass`, `PASS`, a timestamp, a
branch, or a bare commit hash in `Freshness`.

### Finalize a direct tracked execution

An initial direct tracked invocation owns non-defect acceptance finalization
while it holds its direct lifecycle lock. It must not require a redundant
`task-cycle` pass merely to compute close readiness.

After the implementer -> independent verifier handoff:

1. Re-read the contract, owned diff, complete acceptance matrix, and confirm
   that the defect ledger is still header-only and empty.
2. Compute `Reviewed revision` and `Evidence fingerprint` exactly as
   `reviewed-evidence-identity.md` specifies, after the final relevant
   code/test change or recorded user acceptance.
   Copy the complete `Reviewed revision` token byte-for-byte into every
   acceptance-criteria `Freshness` cell before computing the evidence
   fingerprint.
3. If every required acceptance and preservation row has `Result` `PASS`, every
   `Freshness` cell equals the complete `Reviewed revision` token
   byte-for-byte, the ledger remains empty, ownership/risk gates pass, and no
   feedback is unclassified, update only the managed block:
   - `Task state: ready_to_close`;
   - `Current phase: verification`;
   - `Last cycle verdict: READY_TO_CLOSE`;
   - the computed fingerprints and reviewed revision;
   - `PASS` acceptance `Result` cells whose `Freshness` cells each contain the
     complete reviewed-revision token byte-for-byte;
   - `Blocker: none`;
   - `Next action: $task-done <ID>`;
   - one compact transition-history entry.
   Keep closure fields `none`, release the owned lock safely, and return
   `Terminal verdict: READY_TO_CLOSE` plus `Next: $task-done <ID>`.
4. If the independent verifier finds a same-task acceptance failure or
   task-caused regression, do not create or edit a defect row. Finish the
   current lifecycle write, release the direct lock, then invoke
   `$task-cycle <ID> "<exact evidence>"` automatically in the same turn.
   `task-cycle` remains the sole defect-ledger and defect-record writer.
5. If only user judgment remains and explicit acceptance has not been given,
   retain the exact `UNPROVEN` criterion, set a focused next action, and return
   `ACTION_REQUIRED: USER_ACCEPTANCE`; name the criterion but do not request a
   log, screenshot, artifact, or other proof. A subsequent explicit acceptance
   is consumed automatically by Section 0 and finalizes the task. If an
   environment action rather than judgment is genuinely required, report that
   exact environment blocker. If the
   operator's check observes a failure, that observation is raw feedback for
   `$task-bug [<ID>] "<observation>"`. Never return `$task-cycle <ID>` as the
   next command while the defect ledger is empty.

For an internal `task-cycle` call, skip this direct finalization. Return the
acceptance/defect evidence to the owning cycle; that cycle performs the
authoritative terminal transition while retaining its parent lock.

`--mode plan` stops after a decision-ready contract and plan. `--mode diagnose`
reports evidence and root cause without changing production code. The default
`--mode implement` completes the bounded change and verification.

## 7. Hand off the result

Lead with the outcome. Report the selected domain workflow, changed files,
acceptance-to-verification mapping, exact checks and counts, baseline-only failures,
preserved dirty files, manual gaps, residual risk, and commit/checkin status.
For Unity work, the report must include
`Unity preflight: READY | READY WITH WARNINGS | BLOCKED`, then
`Domain workflow: unity-game-dev` plus any genuinely used supporting skill.
Default to no commit. Write a compact completion note only at the repository's
established location. Never claim completion while a required blocking check
failed or did not run.

Report verification channels separately, for example:

```text
Automated verification: PASS | FAIL | NOT_RUN | STALE
Manual/visual verification: PASS | FAIL | UNPROVEN | STALE | NOT_REQUIRED
Acceptance criteria: COMPLETE | INCOMPLETE | BLOCKED
```

Do not say `no blocking defect`, `complete`, or `done` when any required channel
is `FAIL`, `UNPROVEN`, `STALE`, or `NOT_RUN`. Qualify partial success as
`automated checks passed; required manual verification remains`.

For a direct durable task whose required acceptance-criteria rows have `Result` `PASS` and
`Freshness` exactly equal to the complete `Reviewed revision` token, report the
recorded `READY_TO_CLOSE` result and `$task-done <ID>` directly. Never return
`$task-cycle <ID>` to repeat successful acceptance classification or as the
next command for an empty-ledger task awaiting manual evidence; that
continuation belongs to `$implement-task <ID>`. New
user bug observations use `$task-bug [<ID>] "<feedback>"`; a
verifier-discovered same-task failure is dispatched automatically as described
above.

When invoked from an active task cycle, return the evidence directly to that
cycle instead of asking the operator for another command. Include every handled
defect ID, root cause or hypothesis, changed paths, exact checks, reviewed
revision, and defect-specific evidence. The parent `task-cycle` owns same-task
continuation, defect transitions, and close readiness for that internal lane.
