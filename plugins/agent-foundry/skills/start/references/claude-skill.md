---
name: start
description: "First-time onboarding for the Unity studio template. Detects project maturity, selects review intensity, records minimal workflow state, and routes to the next skill without choosing an engine."
argument-hint: "[no arguments]"
user-invocable: true
allowed-tools: Read Glob Grep Write AskUserQuestion
model: sonnet
---

# Unity Studio Onboarding

This repository is already a Unity template. `/start` never asks the user to
choose Godot/Unity/Unreal and never writes project code/assets/packages/settings.

## Phase 1 — Detect State

Read enough context to tailor the route:

- Unity identity: `Assets/`, `Packages/manifest.json`,
  `ProjectSettings/ProjectVersion.txt`, and `Assets/CLAUDE.md`.
- Concept/design: `design/gdd/game-concept.md`, systems index, GDD count.
- Architecture: architecture document, accepted ADRs, control manifest.
- Production: stage/review mode, epics/stories/sprints, C# under `Assets/Game/`.
- Prototype evidence: `Assets/Prototypes/**` and `production/prototypes/**`.

Classify Unity as `VALIDATED`, `TEMPLATE ONLY`, or `MISMATCH/MISSING`. Do not
claim compilation merely because directories exist.

## Phase 2 — Ask the Starting Point

Use `AskUserQuestion` once:

- `No concept yet` — route to `/brainstorm open`.
- `Vague idea` — route to `/brainstorm [hint]` after collecting the hint.
- `Clear concept` — route to `/brainstorm [concept]` to formalize, or
  `/design-review [existing concept path]` when a document already exists.
- `Existing project/work` — route first to `/project-stage-detect`, then
  `/adopt`; add `/setup-engine unity --audit` when Unity identity/configuration
  is not validated.

Explain the shortest relevant sequence. Do not auto-run the next skill.

## Phase 3 — Record Minimal Workflow State

After the user selects a path, this invocation may write only:

- `production/stage.txt`
- `production/review-mode.txt`

These are low-risk, direct consequences of the selected onboarding choices and
do not need per-file approval. Every other path—including `Assets/**`,
`Packages/**`, `ProjectSettings/**`, `.claude/**`, git state, and external
systems—is forbidden.

Stage defaults:

- no/vague/clear concept without approved downstream docs → `Concept`;
- existing GDDs without architecture → `Systems Design`;
- validated architecture before production → `Technical Setup`;
- otherwise preserve an existing explicit valid stage and route to
  `/project-stage-detect` rather than guessing.

If review mode is absent, ask once:

- `full` — director review at defined workflow/gate points;
- `lean` — phase gates only (recommended default);
- `solo` — no director gates.

Do not overwrite an existing valid value without telling the user and receiving
the replacement choice.

## Phase 4 — Handoff

Confirm the selected next workflow and return one concrete command. If the
Unity project is missing/mismatched, route to `/setup-engine unity --audit`; do
not offer another engine inside this template.

Verdict:

- `COMPLETE` — user is oriented and stage/review state reflects their choices.
- `BLOCKED` — required Unity/project context conflicts or the user declines the
  only needed choice.

Next step is the one selected in Phase 2; never start it implicitly.
