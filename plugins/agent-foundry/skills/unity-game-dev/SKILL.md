---
name: unity-game-dev
model: inherit
description: Use when working on Unity game projects, especially Unity 6, C# gameplay systems, UI Toolkit or UGUI, Addressables, Input System, UniTask, Onity, ServiceLocator, tests, performance, project structure, package setup, and Unity-specific architecture decisions.
---

# Unity Game Dev

This skill adapts the Claude Game Studios Unity agents into a shared Claude
Code and Codex workflow.
Use it for Unity implementation, architecture, debugging, refactoring, setup,
testing, and performance work.

For specialist Unity procedures, load the exact matching skill from the
separately installed official `unity@unity-agent-plugin` marketplace plugin:
`/unity:<name>` in Claude Code or `unity:<name>` in Codex. Examples include
`unity:ui-uitk`, `unity:physics-3d-collision`, and
`unity:unity-package-management`. Agent Foundry owns task scope, Unity CLI
transport and safety policy, verification, and handoff; it does not bundle
those 30 official specialist skills. Install the official plugin when missing.

## First Read

Before editing, inspect the project shape:

1. `ProjectSettings/ProjectVersion.txt`
2. `Packages/manifest.json`
3. `Assets/`
4. `Assets/Scripts/`, `Assets/Tests/`, and existing `.asmdef` files if present
5. Any local design docs, ADRs, stories, or task files the user mentions

Use the installed Unity CLI for every Unity task. Verify it with
`unity --version`, prove the exact project with `unity status --json`, and pass
`--project-path` whenever multiple Editors may be running. If the CLI is
missing, install the official CLI under the user's standing authorization
before continuing. Use direct CLI/Pipeline commands first and built-in
`unity mcp` when an AI client needs MCP. Do not switch to a legacy standalone
Unity MCP or UnitySkills fallback unless the user explicitly requests it.
Before reasoning about live Unity state, confirm project identity, Unity
version, compilation, asset import, Play Mode, and recent Console status
through the CLI control plane.

If this is not a Unity project yet, help create a Unity-friendly structure only
after the user asks for scaffolding.

## Unity Automation Integration

Use the installed Unity CLI as the mandatory Unity-specific control plane:

1. Run `unity --version` and the relevant `unity <command> --help`; installed
   help overrides bundled examples.
2. If the command is missing, install the official Unity CLI under the user's
   standing authorization, then verify it before any Unity work. Do not replace
   this bootstrap with a legacy MCP connection.
3. Run `unity status --json` and match the exact project root and Unity version.
   Pass `--project-path` whenever more than one Editor may be available.
4. Use direct CLI/Pipeline commands for supported Editor operations. For AI MCP
   clients, use the server/configuration provided by built-in `unity mcp`.
5. When the installed CLI cannot expose an operation, continue through its
   built-in MCP mode or a pinned source/file workflow. Legacy standalone Unity
   MCP and UnitySkills are opt-in only for an explicit user request.
6. Never perform the same write through multiple transports. Verify through an
   independent read when practical.
7. Package, Pipeline, Editor/module, and other dependency installs still follow
   their normal approval gates. The standing authorization applies only to a
   missing Unity CLI installation.

When UnitySkills is explicitly requested, load its root skill plus only the relevant module
and follow its dry-run, diff, permission, workflow, and Domain Reload rules.

## Repository Instructions

Follow instruction priority in this order:

1. User task and explicit constraints.
2. Repository-local `AGENTS.md`, `CLAUDE.md`, `Assets/CLAUDE.md` for Unity when
   present, nearest path-scoped instructions, and referenced engine docs.
3. Project-pinned Unity docs under `docs/engine-reference/unity/`.
4. This skill and its references.
5. Optional local PDF-derived Unity context.

If local instructions conflict with this skill, follow the local project unless
it would break correctness, security, or the user's explicit request.

## Core Rules

- Prefer composition over deep MonoBehaviour inheritance.
- Use ScriptableObjects for data-driven content and config.
- Use interfaces for gameplay contracts, not global singletons.
- Use `[SerializeField] private` instead of public inspector fields.
- Cache component references in `Awake`; avoid `GetComponent` in hot paths.
- Avoid allocations in `Update`, physics callbacks, render callbacks, and UI loops.
- Use the new Input System, not legacy `Input.*`, for new work.
- Use UI Toolkit for screen-space UI unless UGUI is clearly required.
- Use Addressables for runtime asset loading; avoid `Resources.Load`.
- Prefer an existing ServiceLocator; otherwise use Onity for new DI, reactive
  state, and typed events. Do not introduce new Zenject/Extenject, VContainer,
  UniRx, R3, or MessagePipe usage unless the repository already depends on that
  stack and migration is outside the current task.
- Unless told otherwise, do not add legacy fallback implementations for old
  systems in new code. Preserve existing legacy paths only when production
  compatibility or the user explicitly requires it.
- Add or preserve assembly definitions for clear compile boundaries.
- Put tests in Unity-compatible EditMode/PlayMode locations.
- For player-facing mechanics, capture the intended rule/edge case before
  coding. Use `quick-design`, `game-design-studio`, or `design-review` when
  design intent is unclear or the change affects balance, progression, UX, or
  onboarding.
- For UI work, keep gameplay/domain state out of UI components. UI sends
  commands/events and observes state through project-standard services,
  stores, or bindings.
- For animation, avatar, camera, input, and scene-object work, avoid hard-coded
  transform paths, Animator parameter strings, tag names, layer names, and input
  action names. Centralize them as constants, config assets, or adapter maps.
- For external services, local model runtimes, Firebase, HTTP clients, file I/O,
  and platform APIs, keep typed service boundaries and DTOs. Gameplay code
  should not scatter raw URLs, JSON, credentials, or vendor SDK calls.

## Workflow

1. Gather context and identify the affected systems.
2. Check whether the change is gameplay, UI, asset loading, Firebase/backend,
   editor tooling, animation/avatar, input, persistence, or performance-sensitive
   code.
3. For bugs, reproduce the issue first when practical with a focused test,
   console evidence, scene/prefab inspection, or a concrete manual scenario.
4. Define success criteria before editing: behavior, affected scenes/assets,
   tests, and any manual Unity verification needed.
5. Propose the file-level approach before large edits.
6. Implement narrowly, following existing project conventions.
7. Add or update tests when logic changes.
8. Run available tests or explain exactly why they cannot run here.
9. Re-check Unity Console when MCP is connected.
10. Summarize changed files, verification, and residual risks.

## Task Routing

Use the smallest supporting skill set:

- Performance, allocations, rendering, physics, loading, UI hot paths, mobile
  thermal/battery: use `unity-optimization`.
- SOLID, maintainability, dependency boundaries, ServiceLocator/Onity design,
  refactoring: use `clean-oop-architecture`.
- Firebase Auth, Firestore, Realtime Database, Functions, Unity API clients,
  App Check, rules, emulators: use `firebase-game-backend`.
- JavaScript/TypeScript tooling, local sidecars, dashboards, Firebase Functions:
  use `javascript-game-tools`.
- Code or architecture review: use `game-code-review`.
- UI/UX specs, HUDs, menus, onboarding, accessibility: use `ui-ux` or
  `ux-design` as appropriate.
- Test scaffolding/helpers, regression mapping, flaky tests, QA plans: use
  `test-setup`, `test-helpers`, `regression-suite`, `test-flakiness`, or
  `qa-plan`.
- Story implementation or completion checks: use `dev-story` and `story-done`
  when the user provides story files or asks for story workflow.

Do not load every related skill by default. Load only the one needed for the
current decision.

## Verification Matrix

Choose verification that matches the change:

- Plain C# domain logic: EditMode tests.
- MonoBehaviour lifecycle, physics, scene wiring, UI interaction, input, or
  animation integration: PlayMode tests or Unity MCP/manual scene evidence.
- Asset loading and Addressables: handle tracking, release path, load failure,
  and missing address tests where practical.
- API clients and local services: DTO serialization/parsing, result/error code
  mapping, timeout/cancellation, and important failure paths.
- Editor tooling: compile, menu/tool existence, idempotent behavior, and
  Undo/dirty asset handling where relevant.
- Performance fixes: profiler or measured before/after evidence where feasible;
  otherwise state exactly what hot-path work was removed.

Always report what was run. If tests cannot run in the current environment,
state the exact blocker and the best remaining evidence.

## Reference Loading

Load only what is relevant:

- Unity MCP and verification workflow:
  `references/unity-mcp-workflow.md`
- Unity architecture and patterns: `references/unity-patterns.md`
- Unity C# naming, lifecycle order, UI Toolkit style, async/reactive choices,
  and ServiceLocator/DI precedence: `references/unity-csharp-style-guide.md`
- Onity package selection, install notes, DI, reactive state, and messaging:
  `references/onity.md`
- Cysharp package selection for UniTask, MessagePipe, R3, ZLinq, ZString,
  MemoryPack, and MagicOnion: `references/cysharp-packages.md`
- Unity project layout and tests: `references/unity-project-layout.md`
- Local Unity PDF-derived context index for optional pattern, performance,
  UI/widget, testing, handoff, and refactoring reference:
  `optional local reference library (not included; skip if unavailable)`
- Unity profiling and performance optimization: use `unity-optimization`,
  especially for CPU/GPU/GC hot paths, UI, physics, rendering, loading, memory,
  mobile thermal/battery, and before/after evidence.
- SOLID, OOP, refactoring, and maintainability: use the
  `clean-oop-architecture` skill
- Firebase bridge from Unity: use the `firebase-game-backend` skill
- JavaScript/Web tooling: use the `javascript-game-tools` skill

If the repository contains `docs/engine-reference/unity/`, treat that as the
project's pinned Unity source of truth. Otherwise use current official Unity docs
for unstable API details.
