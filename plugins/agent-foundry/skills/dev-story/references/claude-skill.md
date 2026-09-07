---
name: dev-story
description: "Read a story file and implement it. Loads the full context (story, GDD requirement, ADR guidelines, control manifest), routes through the Unity implementer/verifier/bugfixer handoff, implements code and tests, and confirms each acceptance criterion. Run after /story-readiness, before /game-code-review and /story-done."
argument-hint: "[story-path]"
user-invocable: true
allowed-tools: Read Glob Grep Write Bash Agent AskUserQuestion
model: sonnet
---

# Dev Story

This skill bridges planning and code. It reads a story file in full, assembles
all the context a programmer needs, routes to the correct specialist agent, and
drives implementation to completion — including writing the test.

**The loop for every story:**
```
/qa-plan sprint           ← define test requirements before sprint begins
/story-readiness [path]   ← validate before starting
/dev-story [path]         ← implement it  (this skill)
/game-code-review [files] ← review it
/story-done [path]        ← verify and close it
```

**After all sprint stories are done:** run `/team-qa sprint` to execute the full QA cycle and get a sign-off verdict before advancing the project stage.

**Output:** Unity source and focused tests in story-approved `Assets/` paths.

---

## Phase 1: Find the Story

**If a path is provided**: read that file directly.

**If no argument**: check `production/session-state/active.md` for the active
story. If found, confirm: "Continuing work on [story title] — is that correct?"
If not found, ask: "Which story are we implementing?" Glob
`production/epics/**/*.md` and list stories with Status: Ready.

---

## Phase 2: Load Full Context

**Before loading any context, verify required files exist.** Extract the ADR path from the story's `ADR Governing Implementation` field, then check:

| File | Path | If missing |
|------|------|------------|
| TR registry | `docs/architecture/tr-registry.yaml` | **STOP** — "TR registry not found at `docs/architecture/tr-registry.yaml`. Run `/architecture-review` to bootstrap the registry from your GDDs and ADRs." |
| Governing ADR | path from story's ADR field | **STOP** — "ADR file [path] not found. Run `/architecture-decision` to create it, or correct the filename in the story's ADR field." |
| Control manifest | `docs/architecture/control-manifest.md` | **WARN and continue** — "Control manifest not found — layer rules cannot be checked. Run `/create-control-manifest`." |

If the TR registry or governing ADR is missing, set the story status to **BLOCKED** in the session state and do not spawn any programmer agent.

Read all of the following simultaneously — these are independent reads. Do not start implementation until all context is loaded:

### The story file
Extract and hold:
- **Story title, ID, layer, type** (Logic / Integration / Visual/Feel / UI / Config/Data)
- **TR-ID** — the GDD requirement identifier
- **Governing ADR** reference
- **Manifest Version** embedded in story header
- **Acceptance Criteria** — every checkbox item, verbatim
- **Implementation Notes** — the ADR guidance section in the story
- **Out of Scope** boundaries
- **Test Evidence** — the required test file path
- **Dependencies** — what must be DONE before this story

### The TR registry
Read `docs/architecture/tr-registry.yaml`. Look up the story's TR-ID.
Read the current `requirement` text — this is the source of truth for what the
GDD requires now. Do not rely on any inline text in the story file (may be stale).

### The governing ADR
Read `docs/architecture/[adr-file].md`. Extract:
- The full Decision section
- The Implementation Guidelines section (this is what the programmer follows)
- The Engine Compatibility section (post-cutoff APIs, known risks)
- The ADR Dependencies section

### The control manifest
Read `docs/architecture/control-manifest.md`. Extract the rules for this story's layer:
- Required patterns
- Forbidden patterns
- Performance guardrails

Check: does the story's embedded Manifest Version match the current manifest header date?
If they differ, use `AskUserQuestion` before proceeding:
- Prompt: "Story was written against manifest v[story-date]. Current manifest is v[current-date]. New rules may apply. How do you want to proceed?"
- Options:
  - `[A] Update story manifest version and implement with current rules (Recommended)`
  - `[B] Implement with old rules — I accept the risk of non-compliance`
  - `[C] Stop here — I want to review the manifest diff first`

If [A]: edit the story file's `Manifest Version:` field to the current manifest date before spawning the programmer. Then read the manifest carefully for new rules.
If [B]: edit the story file's `Manifest Version:` field to the current manifest date AND add a `Manifest-Note: Proceeded with old manifest rules on [date] — non-compliance risk accepted.` line to the story header. Read the manifest for new rules anyway. Note the decision in the Phase 6 summary under "Deviations". `/story-done` will include the Manifest-Note in its deviations section without re-checking staleness.
If [C]: stop. Do not spawn any agent. Let the user review and re-run `/dev-story`.

### Dependency validation

After extracting the **Dependencies** list from the story file, validate each:

1. Glob `production/epics/**/*.md` to find each dependency story file.
2. Read its `Status:` field.
3. If any dependency has Status other than `Complete` or `Done`:
   - Use `AskUserQuestion`:
     - Prompt: "Story '[current story]' depends on '[dependency title]' which is currently [status], not Complete. How do you want to proceed?"
     - Options:
       - `[A] Proceed anyway — I accept the dependency risk`
       - `[B] Stop — I'll complete the dependency first`
       - `[C] The dependency is done but status wasn't updated — mark it Complete and continue`
   - If [B]: set story status to **BLOCKED** in session state and stop. Do not spawn any programmer agent.
   - If [C]: obtain the dependency-completion decision, then update its Status
     as part of that decision; do not add a separate file prompt.
   - If [A]: note in Phase 6 summary under "Deviations": "Implemented with incomplete dependency: [dependency title] — [status]."

If a dependency file cannot be found: warn "Dependency story not found: [path]. Verify the path or create the story file."

---

### Engine reference
Read `.claude/docs/technical-preferences.md`:
- `Engine:` value — determines which programmer agents to use
- Naming conventions (class names, file names, signal/event names)
- Performance budgets (frame budget, memory ceiling)
- Forbidden patterns

Read `.claude/docs/reference-libraries.md` if present. If
`docs/reference/private/coding/README.md` exists, read the index and note any
targeted local references relevant to the story's implementation domain
(patterns, refactoring, Unity editor tooling, and approved package usage). These
references may inform implementation quality but never override the ADR,
control manifest, or engine-reference docs.

### Mark Story In Progress

Silently update two things before spawning any agent:

1. **`production/sprint-status.yaml`** (if it exists): find the entry matching this story's file path and set `status: in_progress`. Update the top-level `updated` field to today's date. If the file does not exist, skip silently.

2. **The story file itself**: edit the `Last Updated:` field in the story header to today's date (format: `YYYY-MM-DD`). If the field does not exist in the story header, add it after the `Status:` line. This enables sprint-status staleness detection for this story.

---

## Phase 3: Select the Domain Role and Writer

All Unity code stories use `unity-feature-implementer` as the production writer.
Use the story's **Layer**, **Type**, and system name to select domain guidance;
the domain role does not become a second overlapping writer.

**Config/Data stories:** Plain JSON or non-serialized documentation data may be
edited directly within the story contract. ScriptableObjects, Addressables data,
Input Actions, or other Unity serialized assets require the Unity single-writer
policy and high-risk approval.

### Domain role routing table

| Story context | Domain role supplied to the implementer |
|---|---|
| Foundation layer — any type | `engine-programmer` |
| Any layer — Type: UI | `ui-programmer` |
| Any layer — Type: Visual/Feel | `gameplay-programmer` (implements) |
| Core or Feature — gameplay mechanics | `gameplay-programmer` |
| Core or Feature — AI behaviour, pathfinding | `ai-programmer` |
| Core or Feature — networking, replication | `network-programmer` |
| Config/Data — plain text/JSON | `unity-feature-implementer` inside approved paths |
| Config/Data — Unity serialized asset | `unity-specialist` is the named single writer |

### Unity specialist review

Use `unity-specialist`, `unity-ui-specialist`, or `unity-shader-specialist` as a
read-only planning/review role when engine-specific APIs or HIGH engine risk are
involved. Run the review before implementation or after the writer handoff;
never allow it to mutate the implementer's files concurrently.

**When engine risk is HIGH** (from the ADR or VERSION.md): always spawn the engine
specialist, even for non-engine-facing stories. High risk means the ADR records
assumptions about post-cutoff engine APIs that need expert verification.

---

## Phase 4: Implement

Spawn `unity-feature-implementer` via Agent with the full context package and
the selected domain role.
Implementation and engine verification for the same files run sequentially;
never launch overlapping writers in parallel.

Brief the agent with file paths and targeted reading instructions — do not serialize document content into the Task prompt. The agent reads what it needs directly:

1. **Story file**: `[story-path]` — read in full
2. **GDD requirement**: look up TR-ID `[TR-XXX-NNN]` in `docs/architecture/tr-registry.yaml` — use the `requirement` field as source of truth
3. **ADR**: `docs/architecture/[adr-file].md` — read the **Decision** and **Implementation Guidelines** sections only
4. **Control manifest**: `docs/architecture/control-manifest.md` — read rules for the **[layer]** layer only
5. **Engine preferences**: `.claude/docs/technical-preferences.md` — read naming conventions and performance budgets
6. **Reference library index**: `docs/reference/private/coding/README.md` if it exists — use only targeted reads relevant to the implementation; do not bulk-load full books.
7. **Ownership contract**: base commit, branch/worktree, allowed paths,
   forbidden paths, and serialized assets with their single writer
8. **Test file path**: `[path from story's Test Evidence section]` — create it as part of implementation
9. **Test requirement** (Logic and Integration): create Unity Test Framework
   coverage at the story path. Map each acceptance criterion to a focused test
   or an explicit justified manual/deferred check. Avoid external I/O, global
   random state, and time-dependent assertions.
10. **Risk instruction**: low-risk code/tests inside the ready story may be
    written without per-file approval. Stop for medium/high-risk changes defined
    by the root collaboration protocol.

The agent should:
- Create or modify files only in the story's Unity `Assets/`, `Packages/`, or
  documentation allowed paths
- Respect all Required and Forbidden patterns from the control manifest
- Stay within the story's Out of Scope boundaries (do not touch unrelated files)
- Write clean, doc-commented public APIs

### Config/Data stories

For plain text/JSON Config/Data stories, edit only the declared data paths and
report before/after values. For ScriptableObjects, Addressables settings,
`.inputactions`, scenes, prefabs, or project settings, use `unity-specialist` as
the single writer and obtain explicit high-risk approval.

### Visual/Feel stories

Brief `unity-feature-implementer` with the gameplay-programmer domain role for
code/animation calls. Note that
Visual/Feel acceptance criteria cannot be auto-verified — the "does it feel right?"
check happens in `/story-done` via manual confirmation.

---

## Phase 5: Test Evidence Requirements

After the implementer handoff, run the roles sequentially:

1. Spawn `unity-test-verifier` against the exact implementation branch/commit or
   patch. It may write only approved test/evidence paths and must not fix
   production code.
2. If verification fails, require a reproducible bug report, then spawn
   `unity-bugfixer` with the same story boundary and exact failing path.
3. Return the bugfix result to `unity-test-verifier` for the focused regression
   rerun. Never run implementer, verifier, and bugfixer as overlapping writers.
4. If the same failure survives two scoped fix/verify cycles, stop and surface
   the blocker instead of broadening architecture or ownership.

Each handoff records base commit, branch/worktree, changed paths, allowed and
forbidden paths, serialized assets, raw Unity evidence, and unresolved risks.

The test requirement was included in the Phase 4 programmer agent brief (item 7). This phase summarizes what evidence each story type requires — used when collecting the Phase 6 summary.

| Story Type | Required Evidence | Notes |
|---|---|---|
| **Logic** | Unity EditMode test at path from story's Test Evidence section | BLOCKING — included in Phase 4 agent brief |
| **Integration** | Unity PlayMode/EditMode integration test OR documented playtest record | BLOCKING — included in Phase 4 agent brief |
| **Visual/Feel** | Evidence doc at `production/qa/evidence/[slug]-evidence.md` | ADVISORY — note in Phase 6 summary |
| **UI** | Manual walkthrough doc or interaction test | ADVISORY — note in Phase 6 summary |
| **Config/Data** | None — smoke check serves as evidence | N/A |

For Visual/Feel and UI stories, include in the Phase 6 summary: "Manual evidence required at `production/qa/evidence/[slug]-evidence.md` before this story can be fully closed."

---

## Phase 6: Collect and Summarise

After the implementer/verifier/bugfixer chain completes, collect:

- Files created or modified (with paths)
- Test file created (path and number of test functions written)
- Any deviations from the story's Out of Scope boundary (flag these)
- Any questions or blockers the agent surfaced
- Any engine-specific risks the specialist flagged
- Branch/worktree, base commit, allowed/forbidden paths, and serialized assets touched
- Verifier verdict, raw Unity result paths, and any bugfix/reverification cycles

Present a concise implementation summary:

```
## Implementation Complete: [Story Title]

**Files changed**:
- `Assets/Game/[path]` — created / modified ([brief description])
- `Assets/Tests/EditMode/[path]` — test file ([N] test methods)

**Acceptance criteria covered**:
- [x] [criterion] — implemented in [file:function]
- [x] [criterion] — covered by test [test_name]
- [ ] [criterion] — DEFERRED: requires playtest (Visual/Feel)

**Deviations from scope**: [None] or [list files touched outside story boundary]
**Engine risks flagged**: [None] or [specialist finding]
**Blockers**: [None] or [describe]

**Verification handoff**: [verifier verdict, XML/log paths, bugfix cycles]

Ready for: `/story-done [story-path]` (optional additional `/game-code-review [files]` for high-risk code)
```

---

## Phase 7: Update Session State

Silently append to `production/session-state/active.md`:

```
## Session Extract — /dev-story [date]
- Story: [story-path] — [story title]
- Files changed: [comma-separated list]
- Test written: [path, or "None — Visual/Feel/Config story"]
- Blockers: [None, or description]
- Next: /game-code-review [files] then /story-done [story-path]
```

Create `active.md` if it does not exist. Confirm: "Session state updated."

---

## Error Recovery Protocol

If any spawned agent returns BLOCKED, errors, or cannot complete:

1. **Surface immediately**: Report "[AgentName]: BLOCKED — [reason]" to the user before continuing to dependent phases
2. **Assess dependencies**: Check whether the blocked agent's output is required by subsequent phases. If yes, do not proceed past that dependency point without user input.
3. **Offer options** via AskUserQuestion with choices:
   - Skip this agent and note the gap in the final report
   - Retry with narrower scope
   - Stop here and resolve the blocker first
4. **Always produce a partial report** — output whatever was completed. Never discard work because one agent blocked.

Common blockers:
- Input file missing (story not found, GDD absent) → redirect to the skill that creates it
- ADR status is Proposed → do not implement; run `/architecture-decision` first
- Scope too large → split into two stories via `/create-stories`
- Conflicting instructions between ADR and story → surface the conflict, do not guess
- Manifest version mismatch → show diff to user, ask whether to proceed with old rules or update story first

## Collaborative Protocol

- **File writes follow the story contract** — low-risk code, tests, and evidence
  inside approved paths are autonomous. Medium/high-risk changes pause for the
  required approval. Serialized Unity assets remain single-writer.
- **Load before implementing** — do not start coding until all context is loaded
  (story, TR-ID, ADR, manifest, engine prefs). Incomplete context produces code
  that drifts from design.
- **The ADR is the law** — implementation must follow the ADR's Implementation
  Guidelines. If the guidelines conflict with what seems "better," flag it in the
  summary rather than silently deviating.
- **Stay in scope** — the Out of Scope section is a contract. If implementing
  the story requires touching an out-of-scope file, stop and surface it:
  "Implementing [criterion] requires modifying [file], which is out of scope.
  Shall I proceed or create a separate story?"
- **Test is not optional for Logic/Integration** — do not mark implementation
  complete without the test file existing
- **Visual/Feel criteria are deferred, not skipped** — mark them as DEFERRED
  in the summary; they will be manually verified in `/story-done`
- **Ask before large structural decisions** — if the story requires an
  architectural pattern not covered by the ADR, surface it before implementing:
  "The ADR doesn't specify how to handle [case]. My plan is [X]. Proceed?"

---

## Recommended Next Steps

- Run `/game-code-review [file1] [file2]` before closing the story
- Run `/story-done [story-path]` to verify acceptance criteria and mark the story complete
- After all sprint stories are done: run `/team-qa sprint` for the full QA cycle before advancing the project stage
