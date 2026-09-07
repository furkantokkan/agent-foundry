# Implement Task Argument Contract

## Canonical interface

```text
$implement-task <task-id | contract-path | natural-language> [execution-overrides]
```

Production work is contract-first. Prefer the shortest invocation:

```text
$implement-task GAME-123
```

An exact path is also valid:

```text
$implement-task production/tasks/GAME-123/contract.md
```

Do not repeat objective, scope, ownership, acceptance, or verification fields
that already exist in the contract. The Markdown contract is the durable source;
the command is only the trigger and invocation-local override layer.

## Resolution order

Resolve the repository first, then classify the positional input.

1. Existing repository-relative or absolute file path: use that exact file.
2. Task ID such as `GAME-123`: resolve only
   `production/tasks/GAME-123/contract.md`.
3. Anything else: treat as a natural-language ad-hoc task.

If the task contract is missing, return `CONTEXT BLOCKED` for the
missing task instead of treating the ID text as an ad-hoc request. Match the
complete task ID so `GAME-12` does not select `GAME-123`.

An explicit legacy story path may still derive an execution-local contract, but
ID lookup never falls back to a story/epic. In task-first repositories the task
contract is itself the executable story.

Use `$create-task [<id>] "<request>"` when no durable contract exists and the
operator wants one created automatically. `$implement-task` consumes the
result; it must not implement a `draft` contract. Legacy `blocked` is read as
`draft` plus one action-required result.

## Field ownership

| Field | Canonical location | Invocation behavior |
|---|---|---|
| Contract status | `contract.md` | only `ready` can be implemented; legacy `blocked` is `draft` |
| Objective, kind, area | `contract.md` | Legacy only when no contract exists |
| Scope, allowed/forbidden paths | `contract.md` | Cannot widen an existing contract |
| Serialized assets and sole writer | `contract.md` | Cannot change ownership |
| Acceptance | Story plus `contract.md` mapping | Cannot weaken or replace |
| Preserved behavior | `contract.md` | Cannot remove |
| References, tests, workflow, handoff | `contract.md` | Legacy only when no contract exists |
| Risk | Contract plus automatic detection | Invocation may only raise caution |
| Defect ledger and linked records | Managed `TASK-LIFECYCLE` block plus `defects/D-xxx.md` | `task-bug` resolves intake; `task-cycle` alone captures, deduplicates, links records, reopens, and transitions rows |
| Repository | Current repo | `--repo`/`--project` only for another repo |
| Mode | Current invocation | May reduce mutation, never bypass contract |
| Verification depth | Contract minimum plus current invocation | May only keep or raise |
| Context breadth | Current invocation | History is evidence, not authority |
| Dirty-worktree isolation | Contract minimum plus current invocation | May only keep or raise isolation |
| Commit/checkin | Current invocation only | `after-pass` must be typed now |

Post-implementation symptoms are evidence, not persistent invocation flags.
Pass their raw wording, screenshots, logs, and references to:

```text
$task-bug [<ID>] "<feedback>"
```

`task-bug` resolves one owning task and dispatches the raw observation;
`task-cycle` decides whether each atomic observation is an acceptance failure,
preservation failure, task-caused regression, or distinct new outcome and
creates/reuses its linked record. No
`--defect`, `--bug`, or ledger-editing argument is accepted by
`implement-task`. During an internal repair loop, CycleContext supplies stable
`D-xxx` IDs and exact repro/evidence requirements; those values narrow work but
never grant new authority.

## Execution overrides

| Argument | Values | Default | Rule |
|---|---|---|---|
| `--repo`, `--project` | Exact path or unique name | Current repo | Selects a repository; grants no scope |
| `--mode` | `implement`, `plan`, `diagnose` | `implement` | `plan`/`diagnose` do not mutate production code |
| `--verify` | `auto`, `focused`, `full`, `built-player` | `auto` | May only meet or raise the contract minimum |
| `--context` | `auto`, `current`, `history` | `auto` | Current repository reality always wins |
| `--dirty-policy` | `preserve`, `worktree` | `preserve` | `worktree` raises isolation; never relax a required worktree |
| `--commit` | `none`, `after-pass` | `none` | One local commit/checkin only after all required checks pass |

Typical override use:

```text
$implement-task GAME-123 --mode diagnose
$implement-task GAME-123 --verify built-player
$implement-task GAME-123 --dirty-policy worktree
$implement-task GAME-123 --commit after-pass
```

Several overrides can be combined when needed:

```text
$implement-task GAME-123 --mode implement --verify full \
  --context current --dirty-policy worktree --commit none
```

Most calls should still be `$implement-task GAME-123`.

### Safety ordering

- Verification: contract/repository minimum, then `focused < full < built-player`.
  `auto` means select that effective minimum.
- Isolation: a required worktree cannot be changed to `preserve`.
- Risk: automatic detection and contract risk may only be raised.
- Mutation: `plan` and `diagnose` are less permissive than `implement`.
- Commit: `none` is always safe. `after-pass` is permission for this invocation,
  not a durable contract value.

A contract may say commits are forbidden or constrained. It must never grant
future `after-pass` permission. `after-pass` authorizes no push, PR, deploy,
publish, migration apply, or Remote Config change.

## Contract conflicts

With an existing contract, persistent flags are either redundant or conflicting.
An exact restatement is a no-op; do not create a second source of truth. A change
or expansion must stop before mutation.

```text
# contract.md
Allowed paths: Assets/Game/Combat/**

# Invocation
$implement-task GAME-123 --allowed "Assets/Game/UI/**"
```

Required result:

```text
CONTRACT CONFLICT:
Command attempts to expand allowed paths.
Contract: Assets/Game/Combat/**
Command: Assets/Game/UI/**
Update the contract before implementation.
```

The same rule applies to forbidden paths, serialized ownership, acceptance,
preserved behavior, workflow, handoff, and risk. Never silently union path sets
or let command discovery order choose a value.

## Contractless tasks

Natural language alone is enough:

```text
$implement-task "Projectile double spawn hatasını düzelt"
```

Inspect the repository, infer a bounded execution contract, and show a compact
summary before the first edit. For a durable production task, prefer:

```text
$create-task "Projectile double spawn hatasını düzelt"
```

For another repository:

```text
$create-task "Projectile double spawn hatasını düzelt" \
  --repo "C:\Projects\GAME-Game-2"
```

Legacy `--save-contract auto` remains supported for backward-compatible
automation. `$create-task` is the primary operator workflow. If a contract
already exists, update it through the repository's normal review flow rather
than using command flags to rewrite it.

## Legacy contractless arguments

These remain supported for backward-compatible automation and one-off tasks
without a contract. They are not the primary production interface.

| Argument | Values/meaning |
|---|---|
| `--kind`, `--type` | `feature`, `bug`, `perf`, `refactor`, `migration`, `ui` |
| `--area` | Owning bounded context |
| `--scope` | Affected paths/systems; does not grant write ownership |
| `--allowed` | Writable repository-relative path/glob; repeatable |
| `--forbidden` | Forbidden path/action; repeatable |
| `--serialized` | `none` or an exact asset path with one writer; repeatable |
| `--accept` | Observable scenario; repeatable |
| `--preserve` | Existing behavior that must remain; repeatable |
| `--reference` | File, image, URL, log, or document; repeatable |
| `--exclude`, `--out-of-scope` | Explicit non-goal; repeatable |
| `--platform` | Target platform/runtime scenario |
| `--test` | Focused test path, filter, or command; repeatable |
| `--workflow` | `direct` or sequential `trio` |
| `--handoff` | Required next role/artifact |
| `--risk` | `auto`, `low`, `medium`, `high`; may only raise |
| `--save-contract` | `none`, `auto`, or an in-repository path |

Legacy `--agents single` maps to `--workflow direct`. Do not use
`--agents auto`; choose an explicit workflow after preflight. Independent
stories use separate contracts and worktrees, not one `trio` invocation.

## Examples

### Production task

```text
$implement-task GAME-123
```

### Exact contract

```text
$implement-task production/tasks/GAME-123/contract.md
```

### Cross-repository production task

```text
$implement-task GAME-123 --repo "~\Documents\Repos\GAME-Game-2"
```

### Create a durable Minimalist Desktop bug

```text
$create-task MD-42 "Delete All sonrası restart'ta workspace boş kalmalı" \
  --repo "~\Documents\Repos\Minimalist Desktop"
```

### Backward-compatible contractless automation

```text
$implement-task "Basic attack projectile vuruş frame'inde bir kez spawn olsun" \
  --repo "~\Documents\Repos\GAME-Game-2" --kind bug \
  --area "combat/basic-attack" \
  --allowed "Assets/Game/Combat/BasicAttack/**" \
  --allowed "Assets/Game/Tests/EditMode/Combat/**" \
  --forbidden "Packages/**" --serialized none \
  --accept "Bir accepted attack tam bir projectile üretir" \
  --preserve "Dead Eye timing değişmez" --test "BasicAttackTests" \
  --workflow trio --risk low --commit none
```

Use the long form only because no accepted contract exists. Once saved, invoke
that task by ID or exact path.
