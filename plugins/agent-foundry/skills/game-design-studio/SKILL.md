---
name: game-design-studio
description: Use when designing a game or game feature, writing or reviewing GDDs, mapping systems, defining core loops, player fantasy, MDA, economy, pacing, risk/reward, fail states, UX requirements, acceptance criteria, or turning a rough idea into implementable design docs.
---

# Game Design Studio

This skill ports the Claude game design workflow into Codex. It is optimized for
Unity-first game projects, but the design process is engine-neutral.

## Workflow

1. Understand the player fantasy and target experience.
2. Define the core verb and core loop.
3. Map systems and dependencies.
4. Write the smallest useful design document.
5. Convert design into testable acceptance criteria.
6. Flag scope, production, and implementation risks.

## GDD Sections

Every system GDD should cover:

1. Overview
2. Player Fantasy
3. Detailed Rules
4. Formulas
5. Edge Cases
6. Dependencies
7. Tuning Knobs
8. Acceptance Criteria

## Design Checks

- Mechanics produce the intended dynamics and aesthetics.
- The 30-second loop is fun without meta-progression.
- The 5-minute loop creates meaningful short-term decisions.
- The session loop has a clear start, peak, recovery, and exit.
- Rewards create new decisions, not only bigger numbers.
- Failure teaches and redirects; it does not only punish.
- UI/readability supports the design under stress.
- Scope matches team size and timeline.

## Reference Loading

- Use `references/design-checklists.md` for detailed review prompts.
- Use `optional local reference library (not included; skip if unavailable)`
  when a task needs local PDF-derived design lenses, player-experience framing,
  mechanic critique, playtest questions, or GDD review prompts. Search with
  `rg` and load only relevant sections.
- If a project contains `docs/reference/private/game-design/README.md`, read
  that index and grep specific terms only. Do not bulk-load books or OCR JSON.
