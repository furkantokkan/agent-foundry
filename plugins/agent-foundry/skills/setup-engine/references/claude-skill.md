---
name: setup-engine
description: "Configure or audit this template as a real Unity project. Pins the repository's existing Unity version, canonical paths/stack, automation order, ownership, and risk gates; it does not offer other engines."
argument-hint: "[unity | version] [--audit | --apply]"
user-invocable: true
allowed-tools: Read Glob Grep Write Edit WebSearch WebFetch Task AskUserQuestion
model: sonnet
---

# Unity Engine Setup

This template is Unity-only. `/setup-engine`, `/setup-engine unity`, and
`/setup-engine [Unity-version]` all use this workflow. A Godot, Unreal, or
multi-engine request is `BLOCKED` here and requires a separate repository
migration/template decision; never activate legacy branches inside this project.

## Phase 1 — Discover the Actual Unity Project

Read, in order:

1. `CLAUDE.md`, `AGENTS.md`, `Assets/CLAUDE.md` when present.
2. `ProjectSettings/ProjectVersion.txt`.
3. `Packages/manifest.json` and `Packages/packages-lock.json`.
4. `.claude/docs/technical-preferences.md`, `.claude/rules/**`, active hooks,
   and `docs/engine-reference/unity/VERSION.md`.

Require `Assets/`, `Packages/`, and `ProjectSettings/` for a real project. If
they are absent, setup may configure the Markdown template but must report Unity
compilation/editor verification as `BLOCKED`.

The project file is authoritative for the Unity editor version. If the user
supplies a different version, stop and require a separate upgrade plan. Do not
silently edit `ProjectVersion.txt`. Verify version-sensitive claims against the
pinned official Unity/package docs; current official sources override training
data and older local PDF extracts.

## Phase 2 — Audit Canonical Unity Configuration

The following invariants are mandatory:

- Production roots are `Assets/**`, `Packages/**`, and `ProjectSettings/**`.
  Tests use `Assets/Tests/EditMode/**`, `Assets/Tests/PlayMode/**`, or documented
  feature-local Unity test assemblies. Lowercase `src/`, `assets/`, and root
  `tests/` are not active production roots.
- Path-scoped rules target real Unity paths such as `Assets/Game/**`.
- Private instance/static/constant fields use `m_camelCase`, `s_camelCase`, and
  `k_camelCase` unless a stricter bounded-context rule is already documented.
- Preserve the bounded context's existing composition model. If an established
  ServiceLocator exists, use it. Otherwise Onity is the greenfield default.
  Do not start Zenject/Extenject, VContainer, UniRx, R3, or MessagePipe in a
  context that does not already own that stack.
- Prefer Input System, Addressables, and UI Toolkit for suitable new
  screen-space UI while preserving justified existing systems.
- `docs/architecture/ADR-0001-unity-agentic-stack.md` is the canonical decision;
  lower-level documents may refine it but may not contradict it.
- Independent stories use separate branches/worktrees and disjoint paths. Work
  on one story flows sequentially from implementer to verifier to bugfixer to
  verifier. Exactly one active writer owns each serialized Unity asset.

Report every mismatch with exact file/line and the proposed replacement. Do not
edit in `--audit` mode.

## Phase 3 — Automation Route and Safety

Use one Unity transport per mutation:

1. Use the installed Unity CLI as the mandatory control plane and prove the
   target with `unity status --json` plus exact `--project-path`.
2. If it is missing, install the official CLI under the standing authorization
   before continuing.
3. Use built-in `unity mcp` when MCP protocol is needed. Legacy MCP and
   UnitySkills require an explicit user request, except MCP for Unity under the
   `unity-cli` pre-Unity-6 version gate. If requested, prove identity
   with `project_get_info`; otherwise use direct file inspection as the final
   fallback.
4. Manual Unity YAML editing is a last resort and high risk; default to
   `BLOCKED` for scenes, prefabs, ScriptableObjects, `.inputactions`,
   Addressables/global settings, and other serialized assets.

This workflow never changes UnitySkills mode through REST/chat. If Bypass is
reported, the user changes it to Approval in the UnitySkills panel before any
mutation.

## Phase 4 — Plan and Apply by Risk

Without `--apply`, return the audit and one consolidated patch plan. With
`--apply`, the invocation authorizes low-risk Markdown/config corrections in the
listed plan; do not ask once per file.

- **Low risk:** `CLAUDE.md`, `AGENTS.md`, `Assets/CLAUDE.md`, `.claude/**`, and
  `docs/**` changes that only align documented paths, naming, routing, risk, and
  ownership with this canonical policy.
- **Medium risk:** new asmdefs, public interfaces/contracts, cross-system
  boundaries, or ownership expansion require explicit plan approval even with
  `--apply`.
- **High risk:** `Packages/**`, `ProjectSettings/**`, save formats/migrations,
  scenes, prefabs, ScriptableObjects, `.inputactions`, Addressables/global
  settings, dependency installation, destructive/git operations, commits,
  pushes, or releases require exact approval and are not part of default setup.

Never add a dependency merely because the canonical policy names it. Package
recommendations must cite the pinned reference, explain why existing code cannot
solve the current requirement, and stop before package-file mutation.

## Phase 5 — Validate the Result

After `--apply`:

1. Show the changed-file list and focused diff.
2. Confirm active rules/hooks/workflows use Unity roots and C# examples.
3. Confirm canonical naming and stack wording agree across global, repository,
   agent, skill, and template layers.
4. Confirm the risk/ownership model includes allowed paths, forbidden paths,
   worktree/branch, tests/evidence, and one serialized writer.
5. Confirm no `Packages/**`, `ProjectSettings/**`, save data, or serialized Unity
   asset changed unless separately approved.
6. If a valid Unity runner exists, compile and run the relevant EditMode/
   PlayMode smoke tests and retain logs/XML. Otherwise state `NOT RUN`.

Use `PASS` only when the documentation/config audit is clean and all claimed
verification has raw evidence. Use `CONCERNS` for non-blocking legacy reference
material, `FAIL` for contradictory active rules, and `BLOCKED` for missing
project identity/runner or an unapproved medium/high-risk requirement.

Next step: run `/architecture-review`, `/test-setup --audit`, and a disposable
`/skill-test unity-eval` before trusting code-writing agents on production work.
