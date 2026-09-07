---
name: team-qa
description: "Orchestrate the QA team through a full testing cycle. Coordinates qa-lead (strategy + test plan) and qa-tester (test case writing + evidence routing) to produce a complete QA package for tracked tasks, a sprint, or a feature."
argument-hint: "[task-id... | sprint | feature: system-name] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read Glob Grep Write Task Skill AskUserQuestion
model: sonnet
agent: qa-lead
---

When this skill is invoked, orchestrate the QA team through a structured testing cycle.

**Decision Points:** At each phase transition, use `AskUserQuestion` to present
the user with the subagent's proposals as selectable options. Write the agent's
full analysis in conversation, then capture the decision with concise labels.
The user must approve before moving to the next phase.

## Phase 0: Resolve Review Mode

1. If `--review [mode]` was passed as an argument, use that mode.
2. Else read `production/review-mode.txt` — use whatever is written there.
3. Else default to `lean`.

Modes:
- `full` — spawn all director and lead gates as described
- `lean` — skip director gates unless they are PHASE-GATE type (CD-PHASE-GATE, TD-PHASE-GATE, PR-PHASE-GATE, AD-PHASE-GATE)
- `solo` — skip all director gate spawning entirely; run the skill without any agent gates

Store the resolved mode for use in all subsequent phases.

## Team Composition

- **qa-lead** — QA strategy, test plan generation, story classification, sign-off report
- **qa-tester** — Test case writing, reproducible failure evidence, manual QA
  documentation, and standalone backlog reports when no tracked task owns a bug

## How to Delegate

Use the Task tool to spawn each team member as a subagent:
- `subagent_type: qa-lead` — Strategy, planning, classification, sign-off
- `subagent_type: qa-tester` — Test case writing and bug report writing

Always provide full context plus base/worktree, allowed/forbidden paths, and
output contract. Independent stories may be verified in parallel only in
separate worktrees; implementer, verifier, and bugfixer for one story hand off
sequentially. QA does not fix production code by default.

## Pipeline

### Phase 1: Load Context

Before doing anything else, gather the full scope:

Canonical QA scope units are task contracts at
`production/tasks/<TASK-ID>/contract.md`. A contract is also the executable
story. Read legacy story files only when the repository has no canonical task
contract for that work; never create a sibling `status.md`.

1. Resolve scope from the argument:
   - Exact task IDs or contract paths: resolve each contract exactly, including
     closed tasks when the user explicitly names them.
   - Sprint/epic/feature selector: scan canonical task contracts by declared
     epic, area, tags, objective, and lifecycle; use legacy sprint/story indexes
     only as references to those contracts.
   - No argument: infer candidates from the current branch/worktree, recent
     handoff, and managed lifecycle blocks. Session-state or sprint-status files
     may provide hints but are never a second task-state authority. If the
     result is not unique, ask for task IDs or a selector.

2. Read `production/stage.txt` to confirm the current project phase.

3. Count task contracts found and report to the user:
   > "QA cycle starting for [scope]. Found [N] task contracts. Current stage: [stage]. Ready to begin QA strategy?"

### Phase 2: QA Strategy (qa-lead)

Spawn `qa-lead` via Task to review all in-scope task contracts and produce a QA strategy.

Prompt the qa-lead to:
- Read each task contract and its linked defect records
- Classify each task by type: **Logic** / **Integration** / **Visual/Feel** / **UI** / **Config/Data**
- Identify which tasks require automated test evidence vs. manual QA
- Flag any tasks with missing acceptance criteria or missing test evidence that would block QA
- Estimate manual QA effort (number of test sessions needed)
- **Before assessing smoke status, check for an existing smoke check report**: Glob `production/qa/smoke-*.md` and read the most recently modified file (if found). If a report exists, use its verdict and findings directly — do not re-interview the user. If no report exists, note: "No prior smoke check report found — run `/smoke-check sprint` before proceeding." and set smoke check status to UNKNOWN (treat as PASS WITH WARNINGS for the purpose of continuing). Produce a smoke check verdict: **PASS** / **PASS WITH WARNINGS [list]** / **FAIL [list of failures]** / **UNKNOWN (no report found)**
- Produce a strategy summary table and smoke check result:

  | Task | Type | Automated Required | Manual Required | Blocker? |
  |-------|------|--------------------|-----------------|----------|

  **Smoke Check**: [PASS / PASS WITH WARNINGS / FAIL / UNKNOWN] — [source: `production/qa/smoke-[date].md` or "no report found"] — [details if not PASS]

If the smoke check result is **FAIL**, the qa-lead must list the failures prominently. QA cannot proceed past the strategy phase with a failed smoke check.

Present the qa-lead's full strategy to the user, then use `AskUserQuestion`:

```
question: "QA Strategy Review"
options:
  - "Looks good — proceed to test plan"
  - "Adjust story types before proceeding"
  - "Skip blocked stories and proceed with the rest"
  - "Smoke check failed — fix issues and re-run /team-qa"
  - "Cancel — resolve blockers first"
```

If smoke check **FAIL**: do not proceed to Phase 3. Surface the failures from the smoke check report and stop. The user must fix them, re-run `/smoke-check sprint`, and then re-run `/team-qa`.
If smoke check **UNKNOWN**: surface a warning — "No smoke check report found. Recommend running `/smoke-check sprint` before QA. Proceeding with caution."
If smoke check **PASS WITH WARNINGS**: note the warnings for the sign-off report and continue.
If blockers are present: list them explicitly. The user may choose to skip blocked stories or cancel the cycle.

### Phase 3: Test Plan Generation

Using the strategy from Phase 2, produce a structured test plan document.

The test plan should cover:
- **Scope**: task IDs/sprint/feature name, task count, dates
- **Task Classification Table**: from Phase 2 strategy
- **Automated Test Requirements**: which tasks need Unity EditMode/PlayMode
  tests and the exact `Assets/Tests/**` or feature-local test asmdef paths
- **Manual QA Scope**: which tasks need manual walkthrough and what to validate
- **Out of Scope**: what is explicitly not being tested this cycle and why
- **Entry Criteria**: what must be true before QA can begin. Always include:
  (1) a current smoke report is PASS or PASS WITH WARNINGS, (2) the build is
  stable, and (3) every in-scope task contract has an executable lifecycle state
  and no blocking ownership conflict. Do not require or create a sibling
  `status.md`.
- **Exit Criteria**: what constitutes a completed QA cycle (all stories PASS or
  every failure has an attributable tracked-defect, standalone-backlog, or new
  repair-task route)

Present the QA plan and obtain one plan approval. That approval authorizes the
low-risk write to `production/qa/qa-plan-[sprint]-[date].md`; do not ask again
for each report file inside the approved QA cycle.

### Phase 4: Test Case Writing (qa-tester)

> **Smoke check** is performed as part of Phase 2 (QA Strategy). If the smoke check returned FAIL in Phase 2, the cycle was stopped there. This phase only runs when the Phase 2 smoke check was PASS, PASS WITH WARNINGS, or UNKNOWN.

For each task requiring manual QA (Visual/Feel, UI, Integration without automated tests):

Spawn `qa-tester` via Task for each story (run in parallel where possible), providing:
- The task contract path
- The relevant section of the QA plan for that task
- The GDD acceptance criteria for the system being tested (if available)
- Instructions to write detailed test cases covering all acceptance criteria

Each test case set should include:
- **Preconditions**: game state required before testing begins
- **Steps**: numbered, unambiguous actions
- **Expected Result**: what should happen
- **Actual Result**: field left blank for the tester to fill in
- **Pass/Fail**: field left blank

Present the test cases to the user for review before execution. Group by story.

Use `AskUserQuestion` per story group (batched 3-4 at a time):

```
question: "Test cases ready for [Story Group]. Review before manual QA begins?"
options:
  - "Approved — begin manual QA for these stories"
  - "Revise test cases for [story name]"
  - "Skip manual QA for [story name] — not ready"
```

### Phase 5: Manual QA Execution

Walk through each story in the approved manual QA list.

Batch stories into groups of 3-4 and use `AskUserQuestion` for each:

```
question: "Manual QA — [Story Title]\n[brief description of what to test]"
options:
  - "PASS — all acceptance criteria verified"
  - "PASS WITH NOTES — minor issues found (describe after)"
  - "FAIL — criteria not met (describe after)"
  - "BLOCKED — cannot test yet (reason)"
```

After each FAIL, collect the raw failure description, exact reproduction steps,
expected and actual behavior, build/revision, screenshots or logs, severity, and
affected test. Resolve ownership before writing any standalone bug artifact by
checking exact task contracts (including closed tasks), acceptance/preservation
rules, handoffs, changed systems, and defect ledgers.

Route each atomic failure exactly once:

1. **One tracked owner:** Record
   `/task-bug <TASK-ID> "<raw failure evidence>"` as the repair command. If an
   existing `D-xxx` record matches, link it. Do not create a standalone
   `production/qa/bugs/BUG-*.md`. `task-bug`/`task-cycle` owns dedupe, reopening,
   repair, and verification after QA hands off.
2. **No tracked owner, backlog intent:** Spawn one `qa-tester` writer to run the
   standalone `bug-report` workflow. `bug-report`, not `team-qa`, owns
   deterministic `BUG-xxx` allocation under `production/qa/bugs/`.
3. **No tracked owner, bounded repair intent:** Record
   `/create-task "<observable fix>"`; do not disguise implementation as a QA
   report.
4. **Several plausible owners:** Report `TASK MATCH AMBIGUOUS`, list candidates,
   ask one task-identity question, and allocate no defect, bug, or repair task.

QA may invoke only the low-risk standalone `bug-report` lane when no task owns
the issue and backlog intent is explicit. It records but does not invoke
`task-bug` or `create-task`, because those begin production repair or new task
scope. Multiple failures belonging to one task remain serialized behind that
task's single lifecycle writer.

After collecting all results, summarize:
- Stories PASS: [count]
- Stories PASS WITH NOTES: [count]
- Stories FAIL: [count]
- Tracked defects routed: [task IDs / linked D-xxx references]
- Standalone backlog reports filed: [BUG-xxx references]
- Repair tasks requested: [task IDs or pending create-task commands]
- Ambiguous/unrouted failures: [items]
- Stories BLOCKED: [count]

### Phase 6: QA Sign-Off Report

Spawn `qa-lead` via Task to produce the sign-off report using all results from Phases 4–6.

The sign-off report format:

```markdown
## QA Sign-Off Report: [Sprint/Feature]
**Date**: [date]

### Test Coverage Summary
| Story | Type | Auto Test | Manual QA | Result |
|-------|------|-----------|-----------|--------|
| [title] | Logic | PASS | — | PASS |
| [title] | Visual | — | PASS | PASS |

### Failures Found
| Reference | Owning task | Route | Severity | Status / evidence |
|-----------|-------------------|-------|----------|-------------------|
| GAME-202/D-001 | GAME-202 | task-bug | S2 | OPEN |
| BUG-014 | none | bug-report | S3 | Open |
| GAME-305 | new repair task | create-task | S2 | Ready |

### Verdict: APPROVED / APPROVED WITH CONDITIONS / NOT APPROVED

**Conditions** (if any): [list what must be fixed before the build advances]

### Next Step
[guidance based on verdict]
```

Verdict rules:
- **APPROVED**: All stories PASS or PASS WITH NOTES; no unresolved failure in
  any route
- **APPROVED WITH CONDITIONS**: Only documented S3/S4 backlog conditions or
  PASS WITH NOTES issues remain; no S1/S2 or ambiguous failure remains
- **NOT APPROVED**: Any S1/S2 tracked defect, standalone bug, unverified repair
  task, or unrouted failure remains. `FIXED_UNVERIFIED` is unresolved, and
  `READY_TO_CLOSE` is not closed until `/task-done` succeeds.

Next step guidance by verdict:
- APPROVED: "Build is ready for the next phase. Run `/gate-check` to validate advancement."
- APPROVED WITH CONDITIONS: "Resolve conditions before advancing. S3/S4 backlog items may be deferred to polish."
- NOT APPROVED: "For tracked defects run the recorded `/task-bug` command; for
  standalone reports run `/bug-triage`; for created repair tasks run
  `/implement-task <ID>`. Then re-run targeted QA or `/team-qa`."

Write the final sign-off report to
`production/qa/qa-signoff-[sprint]-[date].md` as the approved QA cycle output
and show the diff. Do not modify production code or serialized assets.

## Error Recovery Protocol

If any spawned agent (via Task) returns BLOCKED, errors, or cannot complete:

1. **Surface immediately**: Report "[AgentName]: BLOCKED — [reason]" to the user before continuing to dependent phases
2. **Assess dependencies**: Check whether the blocked agent's output is required by subsequent phases. If yes, do not proceed past that dependency point without user input.
3. **Offer options** via AskUserQuestion with choices:
   - Skip this agent and note the gap in the final report
   - Retry with narrower scope
   - Stop here and resolve the blocker first
4. **Always produce a partial report** — output whatever was completed. Never discard work because one agent blocked.

Common blockers:
- Input file missing (task contract not found, GDD absent) → redirect to `create-task` or the relevant design workflow
- ADR status is Proposed → do not implement; run `/architecture-decision` first
- Scope too large → propose multiple bounded `/create-task` contracts
- Conflicting instructions between ADR and task contract → surface the conflict, do not guess

## Output

A summary covering: stories in scope, smoke check result, manual QA results,
tracked task/D-record routes, standalone BUG files, new repair task IDs,
ambiguous failures, and the final APPROVED / APPROVED WITH CONDITIONS /
NOT APPROVED verdict.

Verdict: **COMPLETE** — QA cycle finished.
Verdict: **BLOCKED** — smoke check failed or critical blocker prevented cycle completion; partial report produced.

## Session State Update

After the final phase completes (sign-off report written or BLOCKED verdict reached), silently append to `production/session-state/active.md`:

```
<!-- QA RUN: [date] | Sprint: [sprint identifier or "ad-hoc"] | Verdict: [PASS/FAIL/CONCERNS] | Report: production/qa/qa-[date].md -->
```
