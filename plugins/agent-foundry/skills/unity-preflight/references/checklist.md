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

- Installed Unity CLI verified; `unity status --json` target and exact
  `--project-path` recorded as the mandatory control plane.
- If the CLI was missing, official installation completed and `unity --version`
  verified before preflight resumed.
- Built-in `unity mcp` used only when MCP protocol was needed. Any legacy MCP or
  UnitySkills use has an explicit current-task user request recorded, or, for
  MCP for Unity in a project below Unity 6, the `unity-cli` version gate.
- When UnitySkills was explicitly requested, its exact project path was proven
  separately with `project_get_info`, and Bypass was recorded as read-only until
  the user selected Approval in the panel.
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
