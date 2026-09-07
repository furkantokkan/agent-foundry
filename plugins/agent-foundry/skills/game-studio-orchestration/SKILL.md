---
name: game-studio-orchestration
description: Coordinate Claude Code Game Studios style workflows in Codex, including several tracked production task IDs, conflict graphs, worktrees, sequential role handoffs, Unity Editor queuing, safe parallelism, studio hierarchy, quality gates, hooks, rules, and templates. Use when the user invokes $game-studio-orchestration, requests parallel independent tasks, or needs multi-discipline game-development coordination beyond one bounded implementation.
---

# Game Studio Orchestration

This is the Codex port of the Claude Code Game Studios studio layer.

Use this skill when the task is larger than a single implementation change and
needs studio-style coordination: design, architecture, production, QA, release,
multi-discipline work, or role-based review.

## Tracked-task mode

Treat a list of complete task IDs or exact task-contract paths as a request to
run the canonical production orchestration without asking the user to restate
the standing policy:

```text
$game-studio-orchestration GAME-201 GAME-202 GAME-203
```

1. Resolve the current repository, or one exact `--repo`/`--project`, and then
   resolve each ID only as `production/tasks/<ID>/contract.md`. Require every
   selected contract to be `ready`; never guess by partial ID, timestamp, or
   similarly named epic/story.
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
   implementer -> verifier handoff. On a clean independent pass,
   `$implement-task` records `READY_TO_CLOSE` and `$task-done <ID>`. On a
   same-task failure, it releases the direct lock and dispatches `$task-cycle`,
   which records/deduplicates each `D-xxx` row and `defects/D-xxx.md` record
   before optional bugfixer -> verifier work. Populated-ledger or resumed
   defect work starts with `$task-cycle`.
6. Queue Editor-bound mutation and verification through one confirmed Unity
   Editor connection. Parallel Editor operations require separately matched
   Editor instances rooted at their own worktrees. Code-only work may continue
   while the single Editor slot is occupied.
7. Apply the canonical matching-Unity-MCP-first transport policy automatically.
   Do not ask the user to repeat it and never perform one mutation through two
   transports.
8. Default to implementation, contract-required verification, automatic safe
   parallelism, isolated worktrees for parallel writers, and no commit or push.
   Never close a task automatically. A clean direct lane becomes close-ready
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
`../task-cycle/references/lifecycle-lock.md`. Resolve `..` from the directory
containing the loaded `game-studio-orchestration/SKILL.md`, never from the
target repository working directory. Worktrees, branches, role ownership, and
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

## Codex Adaptation

- Claude custom agents are available here as role references, not as Codex
  custom agents.
- Use parallel sub-agents only for concrete independent work with disjoint
  ownership. Keep same-story implementer/verifier/bugfixer work sequential.
- Use `adaptive-skills` first when the right workflow is unclear.
- Use the ported workflow skills for slash-command style jobs such as `start`,
  `game-code-review`, `qa-plan`, `release-checklist`, or `team-combat`.
  `create-stories` belongs only to repositories that explicitly retain the
  legacy epic/story pipeline; task-first repositories go from optional epic
  grouping directly to `create-task`.
- Follow repository-local `AGENTS.md`, `CLAUDE.md`, path rules, and task-specific
  instructions before these references.
- For Unity work, first load `references/rules/unity-architecture.md`,
  `references/rules/unity-automation.md`, and
  `references/rules/unity-ownership.md`. These are canonical; legacy
  multi-engine examples or package catalogs cannot override them.

## Studio References

Load only the files needed for the task:

- Agent index: `references/agents-index.md`
- Agent write/ownership matrix: `references/agent-write-contracts.md`
- Hook index: `references/hooks-index.md`
- Rule index: `references/rules-index.md`
- Template index: `references/templates-index.md`
- Agent definitions: `references/agents/`
- Hook definitions/scripts: `references/hooks/`
- Path-scoped rules: `references/rules/`
- Document templates: `references/templates/`
- Unity three-agent workflow and local PDF-derived reference index:
  `optional local reference library (not included; skip if unavailable)`

## Operating Defaults

- Keep the user in control of product/design decisions.
- For code tasks, implement directly when the request is clear and local context
  is enough.
- Low-risk work inside an approved story and allowed paths is autonomous.
  Assemblies/public contracts need plan approval; serialized assets, packages,
  project settings, save formats, destructive operations, commits/pushes, and
  publishing need explicit approval.
- Parallel writers require independent stories, disjoint paths, and separate
  worktrees. One serialized Unity asset has one writer; implementer, verifier,
  and bugfixer for one story hand off sequentially.
- For selected tracked tasks, apply the tracked-task defaults above. The user
  normally supplies only the task IDs; do not require a repeated policy prompt.
- Return every verifier handoff to the invoking lifecycle owner with assigned
  defect IDs, exact repros, latest evidence, and the reviewed revision. A
  direct initial clean pass returns to `$implement-task`; a failure is
  dispatched to `$task-cycle` only after the direct lock is released. Under
  `CycleContext`, return evidence to the parent cycle. Only `$task-cycle` writes
  defect-ledger rows or linked records before the bugfixer. A bugfixer may
  report `FIXED_UNVERIFIED` but never self-promotes a row to `VERIFIED`.
- Surface cross-discipline tradeoffs when design, code, QA, release, or content
  requirements conflict.
- Preserve Clean Code, SOLID, dependency boundaries, clear English naming, and
  focused tests for new or changed expected behavior.
- For Unity, Firebase, JavaScript, review, or design-specific work, combine this
  skill with the relevant focused Codex skill.
