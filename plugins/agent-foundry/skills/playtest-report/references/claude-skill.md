---
name: playtest-report
description: "Generates a structured playtest report template or analyzes existing playtest notes into a structured format. Use this to standardize playtest feedback collection and analysis."
argument-hint: "[new|analyze path-to-notes] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read Glob Grep Write Task AskUserQuestion
model: sonnet
---

## Phase 1: Parse Arguments

Resolve the review mode (once, store for all gate spawns this run):
1. If `--review [full|lean|solo]` was passed → use that
2. Else read `production/review-mode.txt` → use that value
3. Else → default to `lean`

See `.claude/docs/director-gates.md` for the full check pattern.

Determine the mode:

- `new` → generate a blank playtest report template
- `analyze [path]` → read raw notes and fill in the template with structured findings

---

## Phase 2A: New Template Mode

Generate this template and output it to the user:

```markdown
# Playtest Report

## Session Info
- **Date**: [Date]
- **Build**: [Version/Commit]
- **Duration**: [Time played]
- **Tester**: [Name/ID]
- **Platform**: [PC/Console/Mobile]
- **Input Method**: [KB+M / Gamepad / Touch]
- **Session Type**: [First time / Returning / Targeted test]

## Test Focus
[What specific features or flows were being tested]

## First Impressions (First 5 minutes)
- **Understood the goal?** [Yes/No/Partially]
- **Understood the controls?** [Yes/No/Partially]
- **Emotional response**: [Engaged/Confused/Bored/Frustrated/Excited]
- **Notes**: [Observations]

## Gameplay Flow
### What worked well
- [Observation 1]

### Pain points
- [Issue 1 -- Severity: High/Medium/Low]

### Confusion points
- [Where the player was confused and why]

### Moments of delight
- [What surprised or pleased the player]

## Bugs Encountered
| # | Description | Severity | Reproducible | Owning task | Route | Reference |
|---|-------------|----------|--------------|-------------|-------|-----------|

## Feature-Specific Feedback
### [Feature 1]
- **Understood purpose?** [Yes/No]
- **Found engaging?** [Yes/No]
- **Suggestions**: [Tester suggestions]

## Quantitative Data (if available)
- **Deaths**: [Count and locations]
- **Time per area**: [Breakdown]
- **Items used**: [What and when]
- **Features discovered vs missed**: [List]

## Overall Assessment
- **Would play again?** [Yes/No/Maybe]
- **Difficulty**: [Too Easy / Just Right / Too Hard]
- **Pacing**: [Too Slow / Good / Too Fast]
- **Session length preference**: [Shorter / Good / Longer]

## Top 3 Priorities from this session
1. [Most important finding]
2. [Second priority]
3. [Third priority]
```

---

## Phase 2B: Analyze Mode

Read the raw notes at the provided path. Cross-reference with existing design
documents, `production/tasks/**/contract.md`, legacy task locations when present,
existing linked `defects/D-xxx.md` records, and standalone
`production/qa/bugs/BUG-*.md` reports. Fill in the template above with structured
findings. Flag observations that conflict with design intent.

---

## Phase 3: Action Routing

Categorize all findings into four buckets:

- **Design changes needed** — fun issues, player confusion, broken mechanics, observations that conflict with the GDD's intended experience
- **Balance adjustments** — numbers feel wrong, difficulty too spiked or too flat
- **Bug reports** — clear implementation defects that are reproducible
- **Polish items** — not blocking progress, but friction or feel issues for later

Preserve every tester observation in the tester's own words together with its
build/revision and evidence source. This reporting workflow records the route; it
does not invoke a repair workflow or mutate production code, task lifecycle
state, defect ledgers, or linked defect records.

Before routing an implementation defect, resolve ownership from the exact task
contract, acceptance criteria, preserved behavior, handoff, changed systems,
and defect ledger. Include closed tasks in the search.

- **Tracked-task defect:** When one exact active or closed task owns a failed
  acceptance criterion, preserved behavior, or task-caused regression, record
  `/task-bug <TASK-ID> "<raw observation>"`. Link an existing `D-xxx` record when
  one already represents the same symptom. Do not create a standalone
  `production/qa/bugs/BUG-*.md` file.
- **Unowned backlog capture:** When no tracked task owns the issue and the
  operator wants a report for later triage, record `/bug-report "<observation>"`.
- **Unowned bounded repair:** When no tracked task owns the issue and the
  operator explicitly wants a bounded repair, record
  `/create-task "<observable fix>"`.
- **Ambiguous ownership:** Report `TASK MATCH AMBIGUOUS`, list the plausible task
  IDs, and ask one task-identity question. Do not allocate a task-linked defect,
  standalone bug, or repair task until ownership is resolved.
- **Existing standalone report:** Link it and do not create a duplicate.

Present the categorized list, then route:

- **Design changes:** "Run `/propagate-design-change [path]` on the affected design document to find downstream impacts before making changes."
- **Balance adjustments:** "Run `/balance-check [system]` to verify the full balance picture before tuning values."
- **Bugs:** use the ownership routing above; never send every finding blindly to
  one bug lane.
- **Polish items:** "Add to the polish backlog in `production/` when the team reaches that phase."

---

## Phase 3b: Creative Director Player Experience Review

**Review mode check** — apply before spawning CD-PLAYTEST:
- `solo` → skip. Note: "CD-PLAYTEST skipped — Solo mode." Proceed to Phase 4 (save the report).
- `lean` → skip (not a PHASE-GATE). Note: "CD-PLAYTEST skipped — Lean mode." Proceed to Phase 4 (save the report).
- `full` → spawn as normal.

After categorising findings, spawn `creative-director` via Task using gate **CD-PLAYTEST** (`.claude/docs/director-gates.md`).

Pass: the structured report content, game pillars and core fantasy (from `design/gdd/game-concept.md`), the specific hypothesis being tested.

Present the creative director's assessment before saving the report. If CONCERNS or REJECT, add a `## Creative Director Assessment` section to the report capturing the verdict and feedback. If APPROVE, note the approval in the report.

---

## Phase 4: Save Report

Write the report to
`production/qa/playtests/playtest-[date]-[tester].md` as the declared output.
The invocation authorizes this low-risk report output. Create the directory if
needed and show the resulting diff; do not ask for per-file approval.

---

## Phase 5: Next Steps

Verdict: **COMPLETE** — playtest report generated.

- Act on the highest-priority finding category first.
- After addressing design changes: re-run `/design-review` on the updated GDD.
- Tracked defects: run the recorded `/task-bug` command; it automatically enters
  `task-cycle`. Use `/task-done <ID>` only after `READY_TO_CLOSE`.
- Standalone backlog reports: run `/bug-triage` after capture.
- Newly created repair tasks: run `/implement-task <ID>`.
