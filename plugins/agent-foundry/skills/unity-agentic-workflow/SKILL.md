---
name: unity-agentic-workflow
description: Design, teach, audit, or bootstrap a professional Claude Code and Codex workflow for a Unity repository. Use when deciding which Markdown file owns a rule, writing prompts or slash commands, choosing single-agent versus sequential role handoffs or worktrees, reconciling provider instructions, or finding gaps in an existing Unity agent setup.
---

# Unity Agentic Workflow

Build one provider-neutral operating contract and expose it through thin Claude
Code and Codex entry points. This skill teaches and audits the workflow; create
tracked contracts through `create-task`, then route actual implementation
through `implement-task`, inspect running tasks through read-only `task-status`,
submit new bug feedback through `task-bug`, progress recorded defects through
`task-cycle`, close through `task-done <ID>`, and
persist end-of-day recovery through `daily-handoff <ID...>`. In this task-first
model the task contract is the implementable story; separate story files are
legacy-only.

`task-bug [<ID>] "<feedback>"` is the user-facing bug intake. It can discover
the one owning active or closed task, then dispatches raw evidence to
`task-cycle`. The cycle remains the sole defect-ledger and linked-record writer:
it splits multi-symptom feedback, records stable linked `D-xxx` rows plus
`defects/D-xxx.md` evidence histories, deduplicates repeats, runs bounded
repair/verification, and reopens accepted behavior. Do not create a replacement
task or standalone QA bug for the same outcome.

The command is optional syntax, not an intake requirement. Plain
post-implementation feedback such as "still broken" or a new screenshot/log is
an implicit `task-bug` invocation. Route it there automatically; do not jump
directly to `task-cycle`, declare a remembered `D-xxx` recurrence, or announce
a root cause/fix before the cycle confirms canonical ledger/record evidence.

When natural-language bug feedback has no plausible active or closed task,
`task-bug` invokes `create-task` exactly once and returns that contract's
readiness and dispatch result. Ambiguous matches and supplied-but-missing IDs
stop without writing.

If the same unchanged intake is repeated before that ready task has any
implementation attempt, `task-bug` returns `READY_TASK_EXISTS`, preserves the
contract byte-for-byte, and returns its `implement-task` next command. It does
not redispatch `create-task`/`task-cycle` or record a false recurrence.

For exactly one retained task, an unambiguous affirmative in the same
conversation (`continue`, `devam et`, or `go ahead`) is execution
authorization. If the task is ready, invoke `implement-task` immediately. If
the same turn resolves its draft and makes it ready, cascade directly into
`implement-task`; never consume the affirmative on `TASK UPDATED` and wait for
another message. A still-unanswered product decision, multiple candidates, or
a new conversation does not use this shortcut. Implementation still enforces
all risk, ownership, transport, and approval gates.

If one exact live predecessor owns the authorized task's writable paths, the
affirmative remains valid. Route both IDs to `game-studio-orchestration`, mark
the successor `WAITING_FOR_OWNER`, wait for the stable handoff/lock-release
signal, and dispatch it automatically. Do not convert a schedulable ownership
collision into `draft`/persistent blocked state or ask for another affirmative.

A direct initial `implement-task` with attempt zero and an empty defect ledger
may finalize its own non-defect acceptance lifecycle after independent fresh
verification: it records `READY_TO_CLOSE` and returns `task-done <ID>`. It does
not invoke an empty task-cycle. Any populated ledger, CycleContext, reopened
task, or resumed repair remains task-cycle-owned.

## Choose the operation

Infer one operation from the request:

- `learn`: explain the mental model and give a short practice path.
- `audit`: inspect current instructions, skills, commands, ownership, and proof.
- `daily`: choose the smallest safe execution lane for today's task.
- `design`: propose a provider-neutral workflow or command contract.
- `bootstrap`: create or update workflow files after one decision-ready plan is
  approved.

If no operation is explicit, use `audit` when a repository exists and `learn`
otherwise. Read only the references needed for the selected operation:

- `references/file-authority-map.md` for Markdown placement and precedence.
- `references/prompt-playbook.md` for prompts and command examples.
- `references/unity-operating-model.md` for risk, ownership, and Unity gates.
- `references/workflow-authoring.md` when creating or synchronizing a workflow.

## Inspect before advising

1. Resolve the exact repository and read `AGENTS.md`, `CLAUDE.md`, and nearest
   path-scoped instructions.
2. Detect Unity from `Assets/`, `Packages/manifest.json`, and
   `ProjectSettings/ProjectVersion.txt`; do not assume a generic engine layout.
3. Find existing `.claude/rules`, `.claude/skills`, `.claude/agents`, commands,
   Codex skills/plugins, task templates, hooks, and CI/test entry points.
4. Identify contradictions, duplicated authority, unresolved placeholders,
   global-only dependencies, and commands that fail to forward arguments.
5. Preserve the current bounded-context architecture. A greenfield preference
   is not proof that its package is installed.

## Produce one canonical model

Separate the layers clearly:

1. Repository authority: durable architecture, naming, safety, and precedence.
2. Path-scoped rules: constraints that apply only to matching Unity paths.
3. Skills: reusable procedures with inputs, gates, and output contracts.
4. Agents: roles with allowed paths, forbidden paths, and handoff boundaries.
5. Commands: thin argument-forwarding adapters; never duplicate the procedure.
6. Tools/transports: UnitySkills, Unity MCP, CLI, Git, or Plastic.
7. Task artifacts: one `contract.md` containing immutable authority plus a
   delimited managed lifecycle block, one durable defect ledger, ownership
   handoffs, and retained evidence.

Keep shared semantics provider-neutral. Claude- or Codex-specific files should
only adapt discovery, invocation, and UI metadata.

## Separate planning from execution

Planning defines durable intent before code:

1. Clarify player-facing behavior in a GDD/quick design when needed.
2. Record architectural decisions in ADRs when boundaries or dependencies
   change.
3. Create an epic only when one large outcome contains several independently
   closable tasks. An epic is grouping, never an execution unit.
4. Run `create-task` directly for each implementable outcome. Do not insert a
   story layer; readiness is part of the task contract.

Execution consumes ready task authority and may not redesign it silently.

## Select the execution lane

- New tracked task: `create-task` -> `implement-task` -> `task-done` on a fully
  verified clean pass; if a defect is observed, `task-bug` -> `task-cycle`
  internally/resume -> `task-done`. Use `task-status` only for read-only snapshots and
  `daily-handoff` only for a recovery checkpoint.
- Raw feedback after implementation/verifier/playtest: implicit `task-bug` ->
  candidate task/defect -> canonical `task-cycle` confirmation -> automatic
  bounded repair/verification. The operator need not restate a command.
- Unowned natural-language repair feedback: `task-bug` -> `create-task`
  internally -> ready/draft/action-required result. When the same turn carries
  explicit execution authorization and yields one ready task, dispatch
  `implement-task` immediately.
- Small bounded ad-hoc task: one writer through `implement-task`.
- Ready production task: implementer -> verifier -> task done on a clean pass;
  otherwise task-bug -> task-cycle -> bugfixer only when needed -> verifier ->
  task done.
- Independent tracked tasks: invoke `game-studio-orchestration <ID...>`; it
  resolves ready contracts, assigns separate branches/worktrees to disjoint
  writers, queues a proven overlapping successor behind its active
  predecessor, queues single-Editor work, runs disjoint tasks in parallel, and
  keeps each implementer/verifier/bugfixer chain sequential.
- Architecture, dependency, public contract, save/network schema, or serialized
  Unity asset: plan and explicit approval before the protected mutation.

Domain skills layer under lifecycle skills rather than competing with them. In
a Unity-shaped target, `create-task` invokes `unity-preflight` first, then
`unity-game-dev` read-only to plan topology, ownership, risk, and evidence.
`implement-task` and every Unity repair dispatched by `task-cycle` also require
`unity-preflight` before `unity-game-dev`, Unity diagnosis, production/test
mutation, or verification, then report both the preflight result and
`Domain workflow: unity-game-dev`. `task-bug` remains only the read-only
resolver/router and selects no downstream domain workflow until task matching
finishes. Add another specialist only when the task requires it.

Parallelize research and independent tasks, not writers inside one task. One
scene, prefab, ScriptableObject, `.inputactions`, Addressables group, or project
setting has one active writer.

Never create per-task `status.md` for new work. Lifecycle commands update only
the managed block in `contract.md`; task-cycle may also append linked child
defect evidence records whose current status remains in the ledger. Legacy
`status.md` is read-only migration input. Tasks never auto-close; explicit
`task-done` closes them. New same-scope failure evidence may make task-bug's
downstream cycle reopen a closed task automatically.

Classify feedback relation-first: failure of accepted behavior, preserved
behavior, or a task-caused regression stays in the original task even when the
repair needs an authority decision. A separate player-facing outcome becomes a
new task. `READY_TO_CLOSE` requires every same-task defect to be fresh
`VERIFIED`, every other required channel to pass, and no unclassified feedback.

## Bootstrap gate

For `bootstrap`, first present a compact plan containing:

- canonical source files and generated/mirrored adapters;
- files to create or change;
- provider synchronization strategy;
- validation and forward-test cases;
- migration or collision risks.

Do not write instruction, skill, command, hook, or plugin files until that plan
is approved. After approval, make surgical changes, validate every surface, and
show the changed-file/diff summary.

## Output contract

Lead with a verdict, then provide:

- the chosen lane and why;
- the authority/file map;
- a copy-ready prompt or command;
- ownership, risk, and approval boundaries;
- verification evidence and remaining gaps;
- for audits, a prioritized `P0/P1/P2` remediation list.

Do not claim a workflow is production-ready based only on prompt linting. Require
at least one realistic forward test with path containment and Unity compilation
or an explicit evidence gap.
