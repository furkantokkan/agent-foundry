# Unity Preflight Checklist

## Repository

- Exact absolute root and repository identity.
- `Assets/`, `Packages/manifest.json`, `ProjectSettings/ProjectVersion.txt`.
- Pinned Unity version and package manifest.
- Git/Plastic root, branch/workspace, nested repos, dirty paths.

## Instructions

- Machine and repository `AGENTS.md`/`CLAUDE.md` precedence.
- Nearest path-scoped instructions for proposed files.
- Accepted ADR for architecture/package decisions.
- Existing naming, asmdef, test, and bounded-context conventions.

## Ownership

- Proposed exact allowed and forbidden paths.
- Current writers/worktrees touching those paths.
- Exact scene, prefab, ScriptableObject, `.inputactions`, Addressables, project
  setting, and `.meta` ownership, or `serialized: none`.

## Editor and automation

- Matching Unity MCP target proven as the first-choice transport.
- If MCP is unavailable/mismatched, UnitySkills `/health` reachable and current
  mode recorded.
- UnitySkills exact project path proven separately with `project_get_info`.
- UnitySkills Bypass recorded as read-only until the user selects Approval in
  the panel.
- Unity version matches `ProjectVersion.txt`.
- Compilation, import/update, domain reload, Play Mode, Console, and active test
  job state captured without mutation.

## Verification readiness

- Focused test location/command known.
- EditMode versus PlayMode decision justified.
- Manual, built-player, profiler, or device evidence named when required.
- Approval/allowlist needs identified without changing either.

## Blocking examples

- REST/MCP points to a different repository and the task needs Editor mutation.
- Allowed paths overlap another active writer.
- A serialized asset has no single owner.
- Unity is compiling/importing/reloading and live state is required.
- Required package/settings/asset mutation lacks explicit authorization.

No live automation is only a warning for source-only work that file/CLI checks
can verify. It is blocking when acceptance requires Editor state that cannot be
observed safely.
