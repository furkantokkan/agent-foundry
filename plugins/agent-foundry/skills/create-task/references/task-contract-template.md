# Canonical Task Contract Template

Use this schema for every tracked task. Headings, field labels, lifecycle
delimiters, and table headers are normative. Do not rename or collapse them.
Use `none`, `not applicable`, or a named evidence gap when an optional value is
unavailable. A `ready` task cannot contain placeholders.

```markdown
# <TASK-ID> — <title>

## Identity

- Contract status: draft | ready
- Waiting reason: none | user_input | approval | ownership | dependency | repository | environment
- Action required: none | <one focused action>
- Task ID: <TASK-ID>
- Supersedes: none | <TASK-ID>
- Title: <title>
- Repository (absolute path): <path>
- Branch/worktree or Plastic workspace: <identity>
- Base revision: <revision>
- Task kind: feature | bug | performance | refactor | UI | migration
- Area: <bounded system>
- Workflow: direct | trio | independent-worktree

## Objective and baseline

- Observable objective: <one outcome>
- Current behavior/evidence: <evidence>
- Expected behavior: <expected result>
- Behavior that must remain unchanged: <preservation>

## Ownership

- Owner/writer role: <role>
- Allowed paths (exact or narrow globs):
  - <path>
- Forbidden paths/actions:
  - <path or action>
- Serialized assets: none | exact paths below
  - Asset: <path>
    Sole writer: <role>
    Matching `.meta` owner: <role>
- Other active writers/worktrees checked: <result>
- Execution dependency: none | <predecessor task and stable handoff condition>
- Queue policy: none | auto-dispatch-after-owner-release

## Acceptance scenarios

1. Given <state>, when <action>, then <observable result>.

## References and constraints

- Story/GDD/ADR/design/log/image: <references or none>
- Unity version/platform: <version/platform or not applicable>
- Package/architecture constraints: <constraints>
- Explicit out of scope: <non-goals>

## Verification and risk

- Focused test path/command: <test>
- Required execution preflight: `unity-preflight` | not applicable
- Required Unity domain workflow: `unity-game-dev` | not applicable
- Unity compilation/Console evidence: <required evidence or not applicable>
- EditMode: <required evidence or not applicable>
- PlayMode: <required evidence or not applicable>
- Manual/built-player/profiler/device evidence: <required evidence or not applicable>
- Risk: low | medium | high
- Approval already granted (exact target only): <scope or none>
- Commit/checkin constraint: allowed-on-explicit-invocation | forbidden
- Current invocation permission: none
- Handoff destination: <role or command>

## Stop conditions

- <specific stop condition>

<!-- TASK-LIFECYCLE:START -->
## Lifecycle (managed)

- Task state: draft | ready
- Current phase: planning
- Last cycle verdict: none
- Contract fingerprint: <authority fingerprint>
- Evidence fingerprint: none
- Reviewed revision: none
- Attempt count: 0
- Last feedback: none
- Blocker: none
- Next action: <provider implement-task command or focused unblock action>
- Closed revision: none
- Closed at: none
- Closure mode: none
- Closed by: none
- Superseded by: none

### Acceptance criteria

| Criterion | Result | Verification | Freshness |
|---|---|---|---|
| AC-1 | UNPROVEN | none | not run |

Each criterion may be verified by an automated test, manual verification, or
explicit user acceptance. Record the channel in `Verification`; explicit user
acceptance does not require a test log, screenshot, artifact, or extra proof.

### Defect ledger

| ID | Dedupe key | Status | Relation | Maps to | Symptom / repro | Latest evidence | Verified revision |
|---|---|---|---|---|---|---|---|

### Transition history

- Created — planning — contract authored
<!-- TASK-LIFECYCLE:END -->
```

Add one acceptance-evidence row for every acceptance criterion. The initial
defect ledger has only its header and separator. The command sigil in
`Next action` and `Handoff destination` follows the active provider.

Write every enforceable path/glob as its own ownership-list item. For Unity
tasks that do not explicitly own protected configuration, include separate
`Packages/**` and `ProjectSettings/**` forbidden entries. On creation,
`Evidence fingerprint`, `Reviewed revision`, `Closed revision`, and `Closed at`
remain `none`, while `Attempt count` remains `0`; the planning base revision is
not verification evidence.
