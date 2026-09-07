---
paths:
  - "Assets/Prototypes/**"
  - "production/prototypes/**"
---

# Prototype Artifact Standards (Relaxed)

Prototypes are throwaway artifacts for validating ideas. Unity prototype code
lives inside the repository's existing Unity project under
`Assets/Prototypes/**`; HTML/Paper sandboxes and all reports/evidence live under
`production/prototypes/**`. Never create a nested Unity project.

## What's Allowed in Prototypes
- Hardcoded values (no need for data-driven config)
- Minimal or no doc comments
- Simple architecture (no dependency injection required)
- Singletons and global state
- Copy-pasted code (no need for abstraction)
- Debug output left in place
- Placeholder art and audio
- Quick-and-dirty solutions

## What's Still Required
- Unity implementations live in a declared
  `Assets/Prototypes/[Name]Concept/**` or
  `Assets/Prototypes/[Name]VerticalSlice/**` root inside the existing project.
- Focused automated tests live under `Assets/Tests/EditMode/**` or
  `Assets/Tests/PlayMode/**`, never inside a second Unity project.
- HTML/Paper sandboxes live under
  `production/prototypes/[name]-concept/sandbox/**`; reports and decisions live
  beside them under `production/prototypes/**`.
- Every prototype MUST have a `README.md` with:
  - What hypothesis is being tested
  - How to run the prototype
  - Current status (in-progress / concluded)
  - Findings (updated when prototype concludes)
- No production code may reference or import from `Assets/Prototypes/**` or a
  `production/prototypes/**/sandbox/**` implementation.
- Prototype writers must not modify files outside their declared prototype root.
- Prototypes must not be deployed or shipped

## When a Prototype Succeeds
If a prototype validates a concept and the feature moves to production:
1. The prototype code is NOT migrated directly — it is rewritten to production standards
2. The prototype `README.md` findings inform the production design document
3. The prototype directory is preserved for reference but never extended

## Cleanup
Concluded prototypes should be archived or deleted after findings are captured.
Never let prototype code grow into production code through incremental "cleanup."
