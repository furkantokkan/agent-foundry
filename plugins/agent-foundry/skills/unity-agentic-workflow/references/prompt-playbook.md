# Prompt Playbook

Good prompts define observable behavior and boundaries without prescribing a
speculative architecture. Production prompts should also avoid repeating the
task contract.

## Planning before execution

Use the smallest durable planning layer:

```text
unclear player behavior -> quick-design/design-system -> design-review
architecture/dependency decision -> ADR
several independently closable outcomes -> optional epic
one implementable outcome -> create-task
```

The task contract is also the executable story. Do not run `create-stories` in
a task-first repository. An epic groups task IDs; it is never passed to
`implement-task`.

## Create a production task

Do not open `contract.md` manually:

```text
/create-task GAME-123 "Fix the example weapon hit VFX"
```

Without an existing issue ID:

```text
/create-task "Fix the example weapon hit VFX"
```

When extra detail helps, add any subset of four optional sections. Do not invent
empty sections just to fill a template:

```text
/create-task GAME-124 --repo "C:\Projects\GAME-Game-2"

Context:
- The first muzzle-flash frame is white in the current build.

Task:
- Start the existing flash with its configured color.

Constraints:
- Preserve hit timing and reuse existing VFX assets.

Acceptance:
- No rendered flash frame is white.
```

`Context`, `Task`, `Constraints`, and `Acceptance` are all optional and may
appear in any order. The skill infers missing low-risk facts from the repository
and saves `draft` when a real product, architecture, ownership, or evidence
decision remains. In structured input, put the ID and `--repo`/`--project`
before the first heading; selector-like text inside sections, logs, references,
or Windows paths is data. Structured fields can narrow a contract but cannot
authorize implementation, widen repository authority, lower risk, or grant a
commit.

The command writes `production/tasks/<ID>/contract.md` and returns readiness,
risk, ownership, the selected domain-planning skill, and the next command. It
does not implement production code during its planning action. Unity targets
run `unity-preflight` first, then use `unity-game-dev` in read-only planning
scope.

For exactly one task retained by the same conversation, `devam et`, `continue`,
or another unambiguous affirmative is execution authorization. If a
repository-grounded resolution changes that task from draft to ready in the
same turn, continue directly into `implement-task`; do not stop at
`TASK UPDATED` and ask again. If one exact live predecessor owns overlapping
paths, keep the task ready, route both IDs to `game-studio-orchestration`, and
wait/start it automatically after stable handoff. Genuine unanswered
product/architecture decisions, multiple candidates, and another conversation
do not use this shortcut.

## Implement a contract-first production task

```text
/implement-task GAME-123
```

Resolve an ID only as `production/tasks/GAME-123/contract.md`. Explicit legacy
story paths remain supported by legacy commands, but ID lookup never falls back
to an epic or story.

A recognized task ID with no match also stops; it is not reinterpreted as an
ad-hoc sentence.

Use an exact path when useful:

```text
/implement-task production/tasks/GAME-123/contract.md
```

The contract owns objective, kind, area, paths, serialized writer, acceptance,
preserved behavior, references, tests, workflow, risk, and handoff. Do not copy
those fields into the command.

Use `implement-task` for the initial execution. New post-implementation bug
feedback belongs to `task-bug`; if it reaches `implement-task` directly, the
router forwards it internally before any new write.
Contractless ad-hoc follow-ups may continue inside their execution-local
contract. Feedback for a closed tracked task routes through `task-bug`; its
downstream cycle reopens automatically only when existing acceptance fails.
For Unity work, `implement-task` invokes `unity-preflight` first and
`unity-game-dev` after it passes, before Unity-specific diagnosis,
production/test mutation, or verification, and reports both results in its
handoff.

For a direct initial task with attempt zero and an empty defect ledger, fresh
independent PASS evidence is finalized in the same `implement-task` turn:
reviewed/evidence identities and acceptance rows are refreshed, the task becomes
`READY_TO_CLOSE`, and the next command is `task-done <ID>`. Do not run an empty
task-cycle merely to reclassify that clean result.

## Continue a tracked task through feedback

Use `task-cycle` for recorded defects and resumed/reopened repair work. For a
new tester/player observation, use `task-bug`; an ID is optional
when current context can identify one task:

```text
/task-cycle GAME-123
/task-bug GAME-123 "Muzzle flash'in ilk frame'i hala beyaz"
/task-bug "Dash VFX yok; mezar yanlış yerde; mayın oluşmuyor"
```

`task-bug` selects one route. A unique existing owner goes to `task-cycle`.
Natural-language feedback with no plausible owner goes once to `create-task`,
which performs duplicate checks and returns a ready or draft/action-required contract.
It runs `implement-task` only when the same conversation has explicit execution
authorization; a proven active predecessor queues it through orchestration. An
ambiguous match or a supplied complete ID/path that is missing stops without
writing and asks only for identity correction.

Repeating the same unchanged intake before the new ready task has an
implementation attempt returns `READY_TASK_EXISTS`; it reuses the task
byte-for-byte and returns `implement-task <ID>` without creating a defect or
redispatching `create-task`.

The command stops on one terminal verdict:

- `CONTINUE_SAME_TASK`: internally invoke `implement-task`, verify the result,
  and classify again. The operator does not enter another command.
- `READY_TO_CLOSE`: run `/task-done GAME-123`.
- `NEW_TASK_REQUIRED`: create a separate bounded task.
- `CONTRACT_CHANGE_REQUIRED`: approve the named contract decision first.
- `WAITING_FOR_OWNER`: no second writer; orchestration waits and resumes after
  the live predecessor's stable handoff/lock-release signal.
- `BLOCKED`: resolve the one reported blocker.

`task-bug` only resolves and dispatches; it writes neither contracts nor defect
state itself. During an active defect cycle, `task-cycle` records current state only
in the delimited `TASK-LIFECYCLE` block inside `contract.md` and writes linked
`defects/D-xxx.md` evidence histories; current defect status is never duplicated
there. Authority outside the block remains immutable. New tasks never create
`status.md`; legacy status files are read-only migration input. The cycle is the
sole writer for the managed defect ledger and linked records. Existing acceptance
failures, preserved-behavior failures, and regressions caused by the task stay
under stable semantic `D-xxx` IDs; paraphrases deduplicate and recurrence
reopens the same row. Classify that relation before applying scope/risk gates,
so insufficient authority blocks the same task instead of creating a new one.
Separate player-facing outcomes, explicit non-goals, and unrelated pre-existing
bugs return `NEW_TASK_REQUIRED`.
Automated passes do not replace required manual visual, real-scene PlayMode,
built-player, device, audio, feel, or profiler evidence. Unperformed required
checks remain `UNPROVEN`; observed runtime defects are `FAIL`.
One invocation permits at most three implementation attempts, stops early when
two attempts make no relevant progress, and pauses at every risk, ownership,
transport, or contract-change gate. Repeating the same terminal classification
with the same revision/evidence preserves the lifecycle block byte-for-byte.
The command never closes the task, changes contract authority, commits, or
pushes. Same-scope feedback may reopen a closed task; new scope remains a new
task. `READY_TO_CLOSE` requires fresh acceptance/preservation proof and every
known defect row at `VERIFIED`; fixed-but-unverified, blocked, stale, or
unclassified feedback keeps the cycle open. The operator still closes
explicitly with `/task-done <TASK-ID>`.

## Check task progress without changing state

For a fast snapshot of one or several tracked tasks:

```text
/task-status GAME-201 GAME-202 GAME-203
```

With no IDs, `/task-status` reports only active recorded tasks. It reads
contracts, status, handoffs, worktrees, diffs, and retained test evidence, then
reports phase, task-owned paths, test freshness, blocker, user decision, and one
next command. It does not run tests/builds, mutate Unity, start agents, write
state, or start a task cycle.

## Save the end-of-day handoff

Use task IDs only; the command derives contracts and retained evidence:

```text
/daily-handoff GAME-201 GAME-202 GAME-203 GAME-204
```

It reports status, completed work, changed systems, verification evidence,
remaining blocker, next command, and commit state. It updates only the managed
checkpoint block in `production/session-state/active.md`; it does not run work,
change task state, commit, or push. With no IDs, it selects active recorded tasks.

## Orchestrate independent tracked tasks

Task IDs are the complete normal prompt:

```text
/game-studio-orchestration GAME-201 GAME-202 GAME-203
```

The skill derives readiness, objective, paths, serialized ownership, risk,
verification, handoff, worktrees, Unity MCP-first transport, Editor queuing, and
`commit: none` from canonical policy and the contracts. Do not repeat these in
the prompt. Disjoint tasks proceed independently. A uniquely owned overlap
creates `QUEUED_AFTER_OWNER`; orchestration waits for the predecessor's stable
handoff and starts the successor automatically. Use `OWNERSHIP BLOCKED` only
when the owner/order or safe handoff is ambiguous. Same-task implementer,
verifier, and optional bugfixer remain sequential.

## Invocation overrides

Only execution-time choices normally belong after a production task ID:

```text
/implement-task GAME-123 --mode implement --verify full \
  --context current --dirty-policy worktree --commit none
```

Defaults are `implement`, `auto`, `auto`, `preserve`, and `none`. Use
`--repo` only for another repository. `--verify` may raise the contract minimum,
`--dirty-policy worktree` may raise isolation, and `--commit after-pass` grants
one local commit only for the current run after every required check passes.

A command never widens allowed paths, changes serialized ownership, weakens
acceptance, or lowers risk. Update the contract through review instead.

## Ad-hoc task

Natural language is enough when no contract exists:

```text
/implement-task "Projectile double spawn hatasını düzelt"
```

The agent inspects the repository and shows a compact execution contract before
editing. If it should become production work, create it separately:

```text
/create-task "Projectile double spawn hatasını düzelt"
```

Cross-repository example:

```text
/create-task MD-42 "Delete All sonrası restart'ta workspace boş kalmalı" \
  --repo "~\Documents\Repos\Minimalist Desktop"
```

## Compact grammar for the contract itself

```text
Goal + current evidence + expected behavior + scope/ownership + preserve +
acceptance scenarios + references + verification depth + forbidden actions.
```

## Feature contract

```text
Implement <player-visible outcome>. Current state: <evidence>. Keep <behavior>
unchanged. Own only <paths>; do not touch <paths/assets>. Acceptance: Given...
When... Then.... Verify with <EditMode/PlayMode/manual/build>. Commit forbidden
unless the current invocation explicitly supplies --commit after-pass.
```

## Bug contract

```text
Reproduce <symptom> using <steps/log>. Find the root cause before fixing. Limit
changes to <paths>. Add a regression test for <scenario>. Preserve <behavior>.
Do not regenerate fixtures or suppress unrelated errors.
```

## Performance contract

```text
Profile <scenario/platform>. Capture baseline CPU/GC/GPU/memory evidence before
editing. Change only the measured hot path. Report comparable before/after data;
do not claim improvement from code inspection alone.
```

## UI or serialized-asset contract

Name the exact scene, prefab, UXML/USS, ScriptableObject, or `.inputactions`
asset and declare its only writer. Require a dry-run/diff before protected writes
and include manual visual evidence in the acceptance contract.

## Weak versus strong

Weak contract: `Combat sistemini düzelt ve optimize et.`

Strong contract: `AttackState double-fire üretiyor. Reproduce with the attached
log, own only Assets/Game/Combat/Attack/** and its EditMode tests, preserve Dead
Eye timing, change no scenes/packages, and prove one projectile per accepted
attack.`

After saving the strong contract as `production/tasks/GAME-123/contract.md`, the
operator prompt becomes only `/implement-task GAME-123`.
