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

- Installed Unity CLI verified; repository version gate recorded before
  choosing live evidence. Unity 6+ uses `unity status --json` with full
  `--project-path`, then exact canonical-root and complete-version comparison.
- If the CLI was missing, official installation completed and `unity --version`
  verified before preflight resumed.
- Built-in `unity mcp` used only when MCP protocol was needed. Any legacy MCP or
  UnitySkills use has an explicit current-task user request recorded, or, for
  MCP for Unity in a project below Unity 6, the `unity-cli` version gate.
- For pre-Unity-6 MCP, exactly one full instance ID is bound to the requested
  canonical absolute root and complete Unity version before selection, even
  with one connected Editor. Missing path/version, ambiguity, or mismatch
  blocks live work; HTTP discovery without a path needs independent evidence
  bound to that same instance/session.
- Full-ID selection is followed by `mcpforunity://project/info` readback
  before Editor-state reads, tests, or mutations. Record root, version, full ID,
  session when available, and evidence source. Reconnect, restart, reload, or
  routing changes invalidate that proof.
- Valid gated MCP evidence is accepted even when CLI status has no instances;
  check this route before file-only fallback or an unavailable-runner verdict.
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
