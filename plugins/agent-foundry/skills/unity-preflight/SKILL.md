---
name: unity-preflight
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

Use the installed Unity CLI first. Verify the live command and use
`unity status --json --non-interactive --no-banner` to match the exact project
root and Unity version before Editor-dependent inspection or later mutation.
When several Editors are ready, require the exact `--project-path`.

If the CLI is unavailable, mismatched, or cannot expose the required state, use
a matching Unity MCP connection and confirm the same project identity. If
neither CLI nor MCP can prove the target, fall back to UnitySkills:

1. Call `GET /health` to learn availability, `currentMode`, approval channel,
   pending grants, and service state.
2. Do not use `/health` alone as repository identity. Execute the read-only
   `project_get_info` skill and compare `result.projectPath` with the exact target
   after normalizing a trailing `Assets` segment and path case.
3. Compare the live Unity version with `ProjectVersion.txt`.
4. Read compilation/import/domain-reload/Play Mode and recent Console evidence
   using read-only endpoints or skills only.
5. If `currentMode` is `bypass`, keep UnitySkills read-only and report that the
   user must switch the panel to Approval before any later mutation. REST/chat
   must not change that mode.

If no live transport can prove the same repository, fall back to pinned
Editor/file inspection and mark live Editor evidence unavailable.

## Safety boundary

Preflight never:

- enters or exits Play Mode;
- starts, cancels, creates, or rewrites tests;
- changes UnitySkills mode or allowlist;
- clears the Console;
- saves or opens scenes/prefabs;
- edits packages, project settings, files, or serialized assets.

Running tests belongs to verification after the task contract is accepted.
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
