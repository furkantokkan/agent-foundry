---
description: Learn, audit, design, or bootstrap a professional Claude Code and Codex workflow for a Unity repository.
argument-hint: '[learn|audit|daily|design|bootstrap] [repository or goal]'
---

# Unity Agentic Workflow

Use the `unity-agentic-workflow` Codex skill for this request.

Treat the complete block below as one raw input. Preserve quoted paths and
provider-specific constraints:

<workflow-input>
$ARGUMENTS
</workflow-input>

Teach or audit by default. For `bootstrap`, present one decision-ready plan and
wait for approval before writing instruction, skill, command, hook, or plugin
files.

Treat `/task-bug [<ID>] "<feedback>"` as the canonical user-facing bug intake.
It resolves the owning task and dispatches `/task-cycle`, the optional defect
lane and sole defect-ledger/linked-record writer. Same-task defects are
deduplicated and repaired automatically within authority and block `/task-done`
until every defect has fresh verification. A clean direct `implement-task` with
an empty ledger instead records fresh evidence and `READY_TO_CLOSE` itself; it
does not invoke `task-cycle`. Use `/task-cycle <ID>` directly only to resume
already-recorded defects. Do not recommend a separate fix task, story, or
`status.md` for this case.
