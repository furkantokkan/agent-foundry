# Unity mechanic recipe verification

Date: 2026-10-03. Scope: five original reconstruction skills, their supporting
references, interface metadata, routing and distribution inventory.

## Review method

- Inspect current domain, input, save, session, authoring and test source.
  Separate implemented behavior from dormant support and stale documentation.
- Independently apply the draft recipes to new reconstruction requests.
  Reviewers do not modify production code or run the Editor.
- Repair concrete recipe ambiguities, then recheck those findings.

## Scenarios and findings

| Recipe | Reconstruction scenario | Result |
| --- | --- | --- |
| Grid drag | Fast U-piece drag, neighboring gates, notch blocker, contextual closed cell | Explicit drag-gate command validation and continuous axis-priority calculation added; recheck passed |
| Board effects | Split an iced Arrow piece; restart with a later module construction failure | Fresh state, inheritance, semantic events and atomic context publication are covered |
| Level editor | Armed L ghost at an edge; dirty unrelated asset; externally changed source on reload | Placed-piece kick distinguished from ghost grip; scoped saves and fingerprint rejection covered; recheck passed |
| Boosters | Synchronous store, started-write cancellation, background completion and restart | Existing session suspension distinguished from transaction phases; ownership/policy recheck passed |
| Life economy | Two spends during partial refill followed by failed paid refill | Amounts and timestamps preserve partial progress; failed write changes nothing |
| Reward/charge boundary | Failed life charge and win submission after relaunch | Failure policy remains explicit; memory latches are not claimed as durable idempotency |

Arithmetic fixture: maximum 5, amount 1, start 100, interval 60, now 250 gives
amount 3 and start 220. Spending at 250 and 270 gives amount 1/start 220. A
failed paid refill changes neither currency nor revision. Advancing at 400
then gives amount 4/start 400.

## Structural checks and limits

- All five skill-creator frontmatter checks pass. Interface prompts name the
  exact skill; short descriptions meet the 25-64 character requirement.
- Package validation passes with 98 core skills, 16 Blender skills, 3 AI 3D
  skills, 94 command adapters, 7 aliases, 3 roles and 470 export hashes.
- Reviews found no private project paths or names in the new skills.
- Source inspection and scenario review do not establish executed NUnit,
  live input, build, device performance or crash-recovery results. Each future
  implementation must verify its own selected policies and final code.
