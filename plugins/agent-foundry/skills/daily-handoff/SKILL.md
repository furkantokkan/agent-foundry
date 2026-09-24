---
name: daily-handoff
model: sonnet
description: Create a concise, durable end-of-day handoff for one or more tracked production tasks, covering status, completed work, changed systems, verification evidence, blockers, next commands, and commit state. Use when the user invokes $daily-handoff, asks for today's multi-task handoff, or needs a compact file-backed recovery checkpoint without changing task lifecycle state, running tests, mutating Unity, or committing work.
---

# Daily Handoff

Create one compact multi-task recovery checkpoint. Do not implement, verify,
review, close, commit, or change task authority.

Canonical usage:

```text
$daily-handoff GAME-201 GAME-202 GAME-203 GAME-204
$daily-handoff
```

## 1. Resolve tasks exactly

1. Use the current repository unless `--repo` or `--project` identifies one
   exact path or unique repository name. Never guess between repositories.
2. Read repository `AGENTS.md`, `CLAUDE.md`, their declared order, task/session
   conventions, and existing `production/session-state/active.md`.
3. Resolve each complete ID only as `production/tasks/<ID>/contract.md` and an
   explicit in-repository `contract.md` path directly. Preserve input order and
   deduplicate exact IDs. Never fall back to similarly named stories or partial
   IDs.
4. With no task arguments, use the same active-task selection as `task-status`:
   lifecycle state `in_progress`, `reopened`, `blocked`, or `ready_to_close`
   plus tasks named by active orchestration. Do not include untouched ready
   backlog or closed tasks.
5. A missing or ambiguous task receives a `BLOCKED` handoff section with the
   exact identity problem; it is not reinterpreted as prose.

## 2. Collect attributable evidence read-only

Read each contract's managed lifecycle block, implementation/verification/
bugfix handoffs, ownership/worktree ledgers, associated branch/base revision and
diff, retained verification artifacts, the complete managed defect ledger, and
Git/Plastic metadata. For a legacy
task without the block, read sibling `status.md` only as compatibility input;
never create, update, migrate, or delete it.

For every task report exactly:

- `Status`: recorded lifecycle status and current phase, labeling inference;
- `Completed work`: only outcomes proven by a handoff, diff, or closure record;
  for defect work, include only rows with fresh `VERIFIED` evidence;
- `Changed systems`: contract area plus attributable paths/assemblies/assets;
- `Verification evidence`: check, result, source, revision, and freshness;
- `Defects`: unresolved and verified counts, stable IDs, linked-record integrity,
  and stale proof;
- `Remaining blocker`: one concrete blocker or `None`;
- `Next command`: one short ID-first command or focused unblock action;
- `Commit status`: `uncommitted`, `committed <revision>`, `none`, or `UNKNOWN`.

Do not attribute root dirty work to a task without worktree/branch/handoff proof.
Mark unsupported claims `UNKNOWN` and outdated evidence `STALE`. Do not run
tests/builds, refresh/import Unity, use Unity MCP/UnitySkills to manufacture
evidence, mutate Editor state, start or interrupt agents, create commits, push,
close tasks, or change external trackers.

Use short navigation:

- recorded `ready_to_close`: `$task-done <ID>`;
- new unrecorded post-implementation bug feedback: `$task-bug [<ID>] "<feedback>"`;
- any populated defect-ledger row, or a lifecycle/handoff that records a
  reopened or resumable cycle: `$task-cycle <ID>`;
- an empty defect ledger with initial ready work or incomplete initial
  implementation/evidence: `$implement-task <ID>`;
- active normal work: `Wait for <phase>`;
- blocked: one exact decision or unblock action.

Do not route a defect-free initial implementation handoff to `task-cycle`
merely because implementation evidence exists. Once a defect row exists or the
task has entered a reopened/resumed cycle, keep its continuation on
`task-cycle` unless `ready_to_close` takes precedence. When a workflow is
already actively writing the task, use `Wait for <phase>` rather than a
duplicate invocation.

## 3. Update only the managed session checkpoint

Write only the managed daily-handoff block in
`production/session-state/active.md`:

```markdown
<!-- DAILY-HANDOFF:START -->
# Daily Handoff — <YYYY-MM-DD>

- Repository: <exact root>
- Snapshot revision: <revision plus dirty fingerprint>
- Snapshot fingerprint: <task/revision/evidence/commit fingerprint>
- Updated at: <timestamp and timezone>

## <TASK-ID>

- Status: <status and phase>
- Completed work: <evidence-backed summary>
- Changed systems: <systems and paths>
- Verification evidence: <result, source, revision, freshness>
- Defects: <n unresolved [IDs]> | <n verified [IDs]> | <stale IDs>
- Defect records: <n linked | missing/mismatched IDs>
- Remaining blocker: <blocker | None>
- Next command: `<short command or action>`
- Commit status: <state>
<!-- DAILY-HANDOFF:END -->
```

Preserve the status-line block, manual notes, session extracts, and all content
outside these markers. Create the file/directories when absent. Keep exactly one
managed block and update only requested task sections while retaining unselected
task sections from the same active checkpoint.

Before writing, compare the rendered task state and snapshot fingerprint with
the existing managed block. If unchanged, preserve the file byte-for-byte,
including timestamp. If changed, replace the managed block atomically and
re-read it. The checkpoint is recovery state, not authority: never edit a
contract or its lifecycle block, legacy `status.md`, production/tests/assets,
ownership, VCS, or trackers.

## 4. Report

Return the same concise task blocks in chat and finish with:

```text
DAILY HANDOFF
Tasks: <IDs>
Checkpoint: production/session-state/active.md | unchanged | not written
Snapshot: <revision/fingerprint>
Decisions required: <count and exact tasks>
Next: <first actionable command, or "Resume from checkpoint">
```

Do not start a `task-cycle` or claim completion from missing/stale
evidence. Project documentation is English unless repository rules say otherwise.
