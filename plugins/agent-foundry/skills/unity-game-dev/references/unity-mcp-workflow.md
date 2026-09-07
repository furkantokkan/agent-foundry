# Unity Automation Workflow

Use this reference when UnitySkills REST or Unity MCP is available, or when a
task depends on live Unity Editor state, scene/prefab context, Console output,
package state, or project-specific Unity guidelines.

## Preflight

1. Confirm a connected Unity MCP project root matches the exact target and use
   MCP as the first-choice Unity transport.
2. If MCP is unavailable or points elsewhere, query UnitySkills `GET /health`,
   prove exact project identity separately with `project_get_info`, and keep it
   read-only when the mode is Bypass until the user selects Approval in-panel.
3. Load Unity user/project guidelines through the selected transport when available.
4. Check editor state before making assumptions:
   - Do not trigger disruptive actions while compiling or updating assets.
   - Do not enter or stop Play Mode unless the task requires it.
5. Read recent Console errors and warnings before debugging or after edits.
6. Prefer transport-aware inspection for scene/object/package/project state. Use filesystem
   reads for source files, docs, and assets when MCP does not add context.

## Safe Transport Use

- Use read/query actions before write actions.
- Use UnitySkills dry-run, diff, transaction, audit, and panel approval for
  protected writes. Never enable bypass automatically.
- Use one transport per mutation; do not repeat a write through MCP and REST.
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
