---
name: unity-optimization
model: inherit
description: Use when profiling, diagnosing, optimizing, or reviewing Unity performance, including CPU/GPU bottlenecks, GC allocations, Update/Input/UI hot paths, physics cost, rendering, shaders, batching, Addressables/loading, mobile thermal/battery constraints, memory, and before/after performance evidence.
---

# Unity Optimization

Use this skill for Unity performance work. Prefer measured fixes over generic
"optimization" changes.

## First Read

Before changing code or settings:

1. Read repository instructions: `AGENTS.md`, `CLAUDE.md`, `Assets/CLAUDE.md`,
   nearest path-scoped instructions, Unity style docs, and project performance
   notes when present.
2. Inspect `ProjectSettings/ProjectVersion.txt`, `Packages/manifest.json`, and
   relevant `Assets/` code/settings.
3. Use the installed Unity CLI first for Editor/profiling discovery and
   machine-readable evidence; prove the exact target with `unity status --json`
   and `--project-path`. If the CLI is missing, install it under the standing
   authorization. Use built-in `unity mcp` when needed; otherwise use pinned
   evidence. Legacy MCP and UnitySkills require an explicit user request,
   except MCP for Unity under the `unity-cli` pre-Unity-6 version gate.
4. Identify target platform, target frame rate, device class, and the exact
   symptom before editing.

## Optimization Workflow

1. Define the budget: frame time, memory, load time, draw calls, build size, or
   device target.
2. Reproduce the issue and collect evidence: profiler markers, logs, snapshots,
   screenshots, device notes, or a concrete scenario.
3. Classify the bottleneck:
   - CPU scripting/main thread
   - GC/memory allocation
   - GPU/rendering/fill-rate/shaders
   - UI layout/rebuild/input path
   - Physics/fixed timestep/colliders/raycasting
   - Asset loading/Addressables/instantiation
   - Mobile thermal/battery/platform settings
4. Remove or reduce measured work with the smallest scoped change.
5. Re-measure and document before/after evidence.

## Default Fix Priorities

- Avoid allocations in `Update`, `LateUpdate`, `FixedUpdate`, physics callbacks,
  input callbacks, UI loops, and render paths.
- Avoid LINQ, boxing, string building, closures, iterator allocations, and new
  collections in hot paths.
- Cache component references; do not use scene-wide queries or repeated
  `GetComponent` calls in frame loops.
- Prefer event-driven or reactive flow over unnecessary polling.
- Use pooling for frequently spawned/despawned objects.
- Keep UI updates dirty-state driven; avoid rebuilding layouts every frame.
- Use Addressables and async loading for runtime asset work; release handles.
- Prefer simple data structures and predictable iteration over abstraction that
  hides cost.
- For mobile, watch fill-rate, overdraw, texture size, memory spikes, battery,
  thermal throttling, and real-device performance.

## Guardrails

- Do not optimize blindly. If there is no evidence, first add measurement or
  state the assumption clearly.
- Do not rewrite architecture for a small hot path unless measurement justifies
  the blast radius.
- Do not add legacy fallback paths unless the user explicitly asks or production
  compatibility requires it.
- Preserve behavior unless the user asked for a behavior change.
- For bug/performance fixes, explain root cause, changed files, and verification.

## Reference Loading

Load only what is relevant:

- Unity general implementation rules: use `unity-game-dev`.
- SOLID/refactoring boundaries: use `clean-oop-architecture`.
- Performance code review: use `game-code-review`.
- Local optimization PDF index:
  `optional local reference library (not included; skip if unavailable)`
- Broader Unity/game programming PDF index:
  `optional local reference library (not included; skip if unavailable)`

Search the PDF-derived Markdown with `rg` and load only relevant sections. The
repository, current Unity docs, and measured profiler evidence override older
PDF examples.

## Output Contract

For every optimization task, report:

- Bottleneck classification.
- Evidence before the change, or what evidence was unavailable.
- Changed files/settings.
- Work removed or reduced.
- Verification run and before/after result.
- Residual risk or follow-up measurement.
