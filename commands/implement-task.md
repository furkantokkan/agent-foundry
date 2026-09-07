---
description: Initially execute a task contract or bounded ad-hoc request; automatically route raw tracked-task bug feedback through task-bug.
argument-hint: '<task-id | contract-path | "request"> [--mode implement|plan|diagnose] [--verify auto|focused|full|built-player]'
---

# Implement Task

Use the `implement-task` Codex skill for this request.

Treat the complete block below as one raw task input. Preserve quoted paths,
logs, references, constraints, and natural-language flags; do not shell-tokenize
it.

<task-input>
$ARGUMENTS
</task-input>

Resolve a recognized task ID only as `production/tasks/<id>/contract.md`; a
missing ID blocks and never falls back to an epic/story. Only non-ID input may
become a natural-language ad-hoc task.
An existing contract supplies persistent scope, ownership, acceptance, tests,
workflow, and risk. Command arguments may only apply invocation-local choices
or increase safety; a scope/ownership conflict must stop before mutation.
Default to preserving dirty work and making no commit.

Before mutation, detect post-implementation feedback for an existing tracked
task. Route it internally to `task-bug [<ID>] <raw-feedback>` instead of
starting a fresh implementation or deciding same-task scope. Only proceed
directly when this is initial execution, contractless ad-hoc work, or an
explicit CycleContext handoff from task-cycle. Automated passes never replace
required manual/visual evidence. Closed-task feedback follows the same route;
the downstream cycle may reopen it inside unchanged authority.

For a direct initial tracked task, require task state `ready`, attempt zero, an
empty defect ledger, and no CycleContext. For Unity, load `unity-preflight`
first and `unity-game-dev` second before mutation. If independent verification
passes every required channel, compute the canonical reviewed/evidence
identities, write fresh acceptance evidence, set `READY_TO_CLOSE`, and return
the exact `task-done <ID>` next command without invoking an empty task-cycle.
Any populated/resumed defect lifecycle remains task-cycle-owned.
If a proven live owner prevents direct acquisition, do not fail the authorized
task as blocked. Queue it through `game-studio-orchestration`, wait for the
owner completion/lock-release signal, then revalidate and resume automatically.

Do not pre-announce a remembered defect ID, recurrence/reopen, root cause, or
chosen code fix. Conversation IDs are candidates until task-cycle confirms the
current canonical ledger and linked record.

Preserve all raw feedback so task-cycle can split multiple observable defects,
deduplicate recurrences, update the contract's managed defect ledger, and
continue until every same-task defect has fresh verification or a stop gate is
reached. Do not create a replacement task or standalone bug file for those
defects.
