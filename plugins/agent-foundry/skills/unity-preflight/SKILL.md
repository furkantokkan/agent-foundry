---
name: unity-preflight
model: sonnet
description: Run a read-only readiness check before Unity development. Use before implementing, debugging, testing, profiling, or mutating Editor state to verify the exact repository, Unity version, instructions, dirty work, automation target, permission mode, compilation/import/play state, and available verification path.
---

# Unity Preflight

Establish trustworthy starting evidence without changing files, Editor state,
Play Mode, tests, permissions, object selections, scenes, or assets.

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

Use the installed Unity CLI as the mandatory preflight control plane. Verify
the command and read the requested repository's `ProjectVersion.txt` before
choosing the live transport under `unity-cli`'s version gate:

- Unity 6+: use `unity status --json --non-interactive --no-banner` and the
  full `--project-path`. Independently compare the returned canonical absolute
  project root and complete Unity version; a substring filter or one returned
  instance is not proof.
- Pre-Unity-6: follow
  [the exact MCP identity gate](../unity-cli/SKILL.md#exact-mcp-identity-gate).
  Before selecting even a single instance, require fresh evidence tying its
  full ID to the exact canonical project root and complete Unity version.
  Missing, ambiguous, stale, or mismatched evidence blocks live work.
  Only then pin the full ID, verify `mcpforunity://project/info` readback, and
  inspect Editor state. Session-local routing after identity proof is allowed;
  it does not authorize an Editor or asset mutation.

If the CLI is missing, install the official Unity CLI first under the user's
standing authorization, verify `unity --version`, then restart this read-only
preflight. The installation bootstrap is a machine-level prerequisite outside
the read-only preflight itself. Do not substitute a legacy MCP connection merely
because the CLI was absent.

For Unity 6+, use built-in `unity mcp` when direct CLI/Pipeline commands cannot
expose required live state, pinned to the same proven project. Legacy MCP and
UnitySkills REST still require an explicit current-task request, except MCP
for Unity under the pre-Unity-6 gate. Record that gate and the full identity
evidence instead of requiring CLI status to succeed on an older Editor.

Check the applicable transport before considering pinned source/file
inspection. Valid pre-Unity-6 MCP proof can satisfy live preflight even with
`STATUS_NO_INSTANCES` from the CLI. If required live identity/state cannot be
proven, return `BLOCKED`; source-only work that can be verified without the
Editor may use `READY WITH WARNINGS`, explicitly marking live evidence
unavailable. File inspection never authorizes an unproven Editor or bypasses
serialized-asset approval. Revalidate identity after reconnect, restart,
reload, or routing/instance changes.

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
