# Unity Automation Workflow

Use this reference whenever a task depends on live Unity Editor state,
scene/prefab context, Console output, package state, or project-specific Unity
guidelines. The Unity CLI is the mandatory control plane.

## Default Sequence

1. Verify the installed Unity CLI and relevant command help. If it is missing,
   install the official CLI under the standing authorization before continuing.
2. Match the exact project with `unity status --json`; pass `--project-path`
   when needed.
3. Use direct CLI/Pipeline commands. When MCP protocol is required, use the
   built-in `unity mcp` server configured and targeted by the CLI.
4. Legacy standalone Unity MCP and UnitySkills REST require an explicit user
   request for the current task; they are not fallback transports.
5. Load Unity user/project guidelines through the CLI-controlled route when available.
6. Check editor state before making assumptions:
   - Do not trigger disruptive actions while compiling or updating assets.
   - Do not enter or stop Play Mode unless the task requires it.
7. Read recent Console errors and warnings before debugging or after edits.
8. Prefer CLI-aware inspection for scene/object/package/project state. Use
   filesystem reads for source files, docs, and assets when the CLI adds no context.

## Safe Transport Use

- Use read/query actions before write actions.
- When UnitySkills is explicitly requested, use its dry-run, diff, transaction,
  audit, and panel approval for protected writes. Never enable bypass automatically.
- Use one transport per mutation; do not repeat a write through CLI, MCP, or REST.
- For scenes and prefabs, inspect selection, prefab stage, and relevant objects
  before editing files that depend on serialized references.
- For package questions, inspect installed packages before proposing dependency
  changes.
- For Unity assets, preserve `.meta` files and GUID stability.
- Do not use expensive scene screenshots unless the task needs visual scene
  validation.

## Console Discipline

Use Console output as evidence, not as noise:

- Capture errors before a bug fix when practical.
- Re-check after code or asset changes when Unity is connected.
- Treat unrelated Unity Services/network warnings separately from compile or
  runtime errors.
- If the Console already contains old warnings, filter by timestamp or clear it
  only when doing so will not hide useful context.

## Verification Choices

- EditMode tests for plain C# logic, validators, formulas, adapters, DTOs, and
  state machines.
- PlayMode tests for MonoBehaviour lifecycle, physics, Animator, scene wiring,
  UI Toolkit/UGUI interaction, input, and Addressables integration.
- Manual Unity evidence for visual layout, animation timing, scene placement,
  package import behavior, or platform-specific editor workflows.
- Profiler/device evidence for performance claims whenever feasible.

## Handoff Note

For Unity changes, include a short completion note:

- What changed and why.
- Affected files, scenes, prefabs, assets, and assemblies.
- Tests or Unity checks run.
- Console status after verification when MCP was connected.
- Follow-up risks, especially missing PlayMode evidence, asset references, or
  platform-specific behavior.
