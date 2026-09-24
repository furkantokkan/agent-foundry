---
name: task-done
model: inherit
description: Close one or more exact tracked tasks. Invoke automatically for an explicit user close order in a tool command or ordinary language; use --strict to require satisfied acceptance criteria.
argument-hint: "<TASK-ID|contract-path>... [--strict] [--superseded-by <TASK-ID>]"
user-invocable: true
allowed-tools: Read Glob Grep Edit Write Bash
---

# Task Done

Close one or more exactly resolved tracked tasks. Do not implement, rerun tests,
mutate Unity, commit, check in, push, deploy, or publish.

```text
$task-done GAME-202
$task-done GAME-202 GAME-203
$task-done production/tasks/GAME-202/contract.md --strict
```

## Automatic invocation from an explicit user order

Treat an unambiguous ordinary-language instruction to close an exact task as
an immediate invocation of this workflow; the user does not need to type
`$task-done`. For example, “Close GAME-202”, “GAME-202'i kapat”, or “Kapanışa
hazır GAME-202 görevini kapat” is equivalent to `$task-done GAME-202`.

“Close this task” is equivalent only when the current conversation has exactly
one unambiguous retained task. Resolve its exact ID before taking any write.
Do not infer a close order from a conditional, question, status statement, or
generic execution phrase such as “continue”, “finish”, or “go ahead”. Ask for
the exact target only when it cannot be resolved safely.

The plain command or a recognized ordinary-language close instruction is
explicit authority to close the resolved tasks. Do not ask for redundant
confirmation. Unmet or unverified acceptance criteria change the closure mode;
they do not cancel a direct user close order. An explicit user close order must
not trigger a request for a test log, screenshot, artifact, or other proof.

`--strict` retains criteria-gated behavior and closes only a current
`READY_TO_CLOSE` task.

## 1. Scope, risk, and authority

Allowed low-risk writes:

- the delimited lifecycle block in each exact
  `production/tasks/<TASK-ID>/contract.md`;
- appending one managed lifecycle block to that contract when it is legacy and
  has no lifecycle block;
- operational lifecycle lock metadata outside versioned project content.

Forbidden writes and actions:

- production code, tests, serialized assets, `status.md`, defect records,
  epics, stories, sprints, external issues, packages, project settings, save
  formats, generated output, VCS history, commits, checkins, pushes, deployments,
  releases, or unrelated task files;
- changing a `FAIL`, `UNPROVEN`, `STALE`, `NOT_RUN`, unresolved defect, or
  ownership finding into `PASS`/`VERIFIED`;
- deleting or rewriting retained acceptance criteria, their verification
  records, or defect-ledger rows.

Risk contract:

- lifecycle-only closure explicitly named by the user is low risk and
  authorized by the invocation;
- widening task authority or changing another workflow contract is medium risk
  and requires a separate explicit instruction;
- destructive operations, source/asset changes, dependency changes, VCS
  history changes, and external publishing are high risk and forbidden here.

Serialized-asset ownership: none. This skill never writes a Unity serialized
asset. `task-done` is the sole writer of the closure transition;
`task-cycle` remains the sole writer of defect-ledger state.

## 2. Resolve and lock exactly

1. Resolve every complete ID only as
   `production/tasks/<ID>/contract.md`; accept an exact in-repository contract
   path. Never use a partial match or close a containing epic/story.
2. Reject an empty target list, duplicate aliases for the same contract, a
   missing contract, a path outside `production/tasks/`, or a task ID that does
   not match its parent directory.
3. Read
   `../task-cycle/references/lifecycle-lock.md` and
   `../task-cycle/references/reviewed-evidence-identity.md` relative to this
   installed skill before any write. These identities protect existing review
   state; they do not require new proof for an explicit user close order.
4. In Git, use the shared lock protocol exactly as documented. Outside Git,
   prefer the repository's documented atomic lock service. If none exists,
   manually serialize this host through an atomic `FileMode.CreateNew` claim
   under the Codex state root that owns this installed skill:
   `task-lifecycle-locks/<repository-root-sha256>/<TASK-ID>.lock.claim`.
   Store the same owner metadata and use the same token-safe release rules from
   `lifecycle-lock.md`. Record the mode as `host_local_manual`.
5. A busy claim is a hard `TASK_LIFECYCLE_BUSY` stop for that task. Never steal,
   overwrite, or delete another writer's claim. Continue independently with
   other exact IDs in the same invocation.
6. Under the acquired lock, re-read the canonical contract, lifecycle block,
   sibling legacy `status.md` when present, complete ledger, linked records,
   ownership, current provider revision, and commit state.

## Supersede mode for orphan reconciliation

`--superseded-by <NEW-ID>` is accepted only from a validated create-task
reconciliation handoff or an explicit user command. Require the replacement
contract to exist, be ready, link `Supersedes: <OLD-ID>`, and describe the
same high-confidence outcome. Also require no active lifecycle lock/owner,
worktree/handoff, attributable implementation changes, attempts, or defect
rows on the old planning task. Age alone is insufficient.

Under the normal lifecycle lock, preserve all evidence and update only the old
managed block to `Task state: closed`, `Current phase: closed`,
`Last cycle verdict: SUPERSEDED`, `Closure mode: superseded`,
`Superseded by: <NEW-ID>`, `Closed by: task_reconciliation`, a current UTC
closed timestamp/revision, and `Next action: None`. Append one transition
entry. Never delete the old directory, contract, ledger, or evidence.

Return `TASK SUPERSEDED` idempotently when the same link already exists. If
any identity, ownership, lock, progress, or replacement check fails, write
nothing and return `STALE_TASK_RECONCILIATION_REQUIRED`.

## 3. Choose the closure mode

### Strict criteria closure

With `--strict`, require all of the following:

- contract readiness `ready`;
- task state `ready_to_close`;
- last cycle verdict `READY_TO_CLOSE`;
- exact current contract, reviewed-revision, and evidence fingerprints as
  defined by `reviewed-evidence-identity.md`;
- every required acceptance/preservation criterion has result `PASS` and a
  recorded verification channel of an automated test, manual verification, or
  explicit user acceptance;
- every defect `VERIFIED` at the current reviewed revision with a valid linked
  record;
- scope/ownership containment `PASS`;
- no blocker or relevant post-review change.

An explicit user acceptance may satisfy one named criterion or all criteria. It
needs no test run, artifact, screenshot, or model-generated proof. In strict
mode it must already be recorded as the criterion's verification channel by
`implement-task` or `task-cycle`; `task-done` does not reclassify criteria. New contracts use `### Acceptance
criteria`; treat a legacy `### Acceptance evidence` block as the same preserved
table and do not rename it during closure.

Missing, stale, contradictory, or changed criteria state returns
`TASK CLOSURE BLOCKED (STRICT)` and routes to `$task-cycle <ID>`. Strict mode
does not repair, migrate, or rerun checks.

### Direct user confirmation closure

Without `--strict`, the exact user close order authorizes closure regardless of
the current lifecycle state, contract readiness, incomplete acceptance
criteria, blocker, legacy status, or unresolved defect rows. This is the
user's completion decision, not a request for the model to collect proof.

Before writing:

- inventory unmet or unverified acceptance criteria, their recorded
  verification channels, unresolved defects, ownership findings, and the prior
  blocker for the report;
- preserve all of them byte-for-byte;
- classify the transition as `user_confirmed`;
- never state or imply that closure proves correctness, acceptance, testing, or
  defect resolution.

An already closed task returns `TASK ALREADY CLOSED`. A missing/corrupt
contract, ambiguous target, or active lifecycle writer remains a hard blocker;
user confirmation does not authorize guessing a target or overwriting concurrent
work.

## 4. Write the closure

For an existing managed block, update only closure-owned fields:

- `Task state: closed`;
- `Phase` or `Current phase: closed`;
- `Last cycle verdict: USER_CONFIRMED` in user-confirmation mode; retain
  `READY_TO_CLOSE` in strict mode;
- `Closure mode: user_confirmed | criteria_verified`;
- `Closure status: closed`;
- `Closed revision`: unchanged complete reviewed revision when available,
  otherwise the exact current provider revision labeled as unreviewed;
- `Closed at`: current UTC timestamp;
- `Closed by: explicit_user_confirmation`;
- `Next action: None`;
- one compact transition-history entry stating the closure mode.

For a legacy contract without a managed block, append one delimited managed
lifecycle block containing those fields plus:

- the contract fingerprint calculated before the append;
- `Reviewed revision: none` and `Evidence fingerprint: none` unless exact
  deterministic identities already exist;
- `Prior evidence status: preserved in status.md` when a sibling status exists;
- an empty defect-ledger table only when no canonical ledger exists;
- one transition-history entry recording explicit user confirmation closure.

Never modify or delete a legacy `status.md`.

After the write:

1. Re-read the complete contract and confirm exactly one valid lifecycle block.
2. Confirm state/phase/closure status are `closed`, `Next action` is `None`, and
   retained acceptance-criteria/verification and ledger bytes are unchanged.
3. In strict mode, recompute reviewed/evidence identities and require them to
   remain unchanged. In user-confirmation mode, recompute the contract-authority
   fingerprint and require it to remain unchanged.
4. Release the lifecycle lock only when claim and metadata owner tokens still
   match.
5. If post-write validation fails, report `TASK CLOSURE WRITE INVALID`; do not
   claim closure or edit production/defect evidence to compensate.

## 5. Report

Report every requested task independently:

```text
TASK CLOSED (USER CONFIRMED) | TASK CLOSED | TASK ALREADY CLOSED | TASK CLOSURE BLOCKED
ID: <ID>
Contract: production/tasks/<ID>/contract.md
State: closed | <current-state>
Closure mode: user_confirmed | criteria_verified | none
Closed revision: <revision | none>
Acceptance criteria: <preserved pass/unmet/unverified summary; verification channels>
Defects: <preserved verified/unresolved summary>
Scope/ownership: PASS | <preserved finding>
Commit status: <uncommitted | committed revision | none | UNKNOWN>
Next: $daily-handoff <ID> | $task-bug <ID> "<feedback>" | <unblock action>
```

For user-confirmation closures, say explicitly that incomplete or unverified
criteria and unresolved defects were preserved rather than verified.

## 6. Follow-up actions

- Use `$daily-handoff <ID...>` for a durable checkpoint after closure.
- Route later bug evidence through `$task-bug <ID> "<feedback>"`; its owning
  cycle may reopen the closed task when the evidence fits unchanged authority.
- Use `$task-done <ID> --strict` when closure must remain criteria-gated.
