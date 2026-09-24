---
name: unity-preflight
model: sonnet
description: Run a read-only readiness check before Unity development. Use before implementing, debugging, testing, profiling, or mutating Editor state to verify the exact repository, Unity version, instructions, dirty work, automation target, permission mode, compilation/import/play state, and available verification path.
---

# Unity Preflight

Establish trustworthy starting evidence without changing files, Editor state,
Play Mode, tests, permissions, selections, scenes, or assets.

Read `references/checklist.md` for every run. Read
`references/unityskills-identity.md` when UnitySkills REST is available or
expected.

## Resolve the target

1. Use an explicit repository path when provided; otherwise resolve the current
   repository. Never guess between multiple matches.
2. Require `Assets/`, `Packages/manifest.json`, and
   `ProjectSettings/ProjectVersion.txt` for a Unity verdict.
3. Read repository `AGENTS.md`, `CLAUDE.md`, their declared precedence, and the
   nearest path-scoped instructions for the proposed work.
4. Record Git/Plastic root, branch/workspace, nested repositories, and existing
   changes. Do not clean or modify them.

## Verify live Unity identity

Use the installed Unity CLI as the mandatory preflight control plane. Verify the
live command and use `unity status --json --non-interactive --no-banner` to
match the exact project root and Unity version before Editor-dependent
inspection or later mutation. When several Editors are ready, require the exact
`--project-path`.

If the CLI is missing, install the official Unity CLI first under the user's
standing authorization, verify `unity --version`, then restart this read-only
preflight. The installation bootstrap is a machine-level prerequisite outside
the read-only preflight itself. Do not substitute a legacy MCP connection merely
because the CLI was absent.

If direct CLI/Pipeline commands cannot expose required live state, use the
built-in `unity mcp` server through the verified CLI and pin the exact project.
Legacy Unity MCP connections and UnitySkills REST are allowed only when the user
explicitly requests them for the current task. If the verified CLI and its
built-in MCP mode still cannot prove the same repository, use pinned
Editor/file inspection and mark live Editor evidence unavailable.

## Safety boundary

Preflight never:

- enters or exits Play Mode;
- starts, cancels, creates, or rewrites tests;
- changes UnitySkills mode or allowlist;
- clears the Console;
- saves or opens scenes/prefabs;
- edits packages, project settings, files, or serialized assets.

Focused tests and compile/recompile checks belong to verification after
preflight. A user request to implement, fix, or verify Unity behavior
authorizes those checks without separate contract or command approval once
the exact project is confirmed. Preserve unsaved Editor work.
Test-template creation must pass the canonical folder explicitly; UnitySkills
defaults may not match `Assets/.../Tests/EditMode` and `PlayMode` conventions.

## Verdict

Return exactly one:

- `READY`: exact repo identity proven, no blocking editor state, instructions
  resolved, ownership clear, and required verification is available.
- `READY WITH WARNINGS`: safe work can begin, but non-blocking evidence or
  automation is missing.
- `BLOCKED`: target is ambiguous/mismatched, ownership overlaps, Unity is in a
  disruptive state, or the requested task requires an unavailable protected
  path.

Report target repo, Unity version, instruction files, VCS/dirty state,
automation transport and identity, mode/allowlist implications, compilation and
Console state, proposed allowed/forbidden paths, serialized ownership, and the
exact next action. Never silently turn a warning into permission to mutate.
