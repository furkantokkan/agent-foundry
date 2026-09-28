# Unity Automation Policy

## Transport Order

1. Use the installed Unity CLI as the mandatory control plane for every Unity
   task, including preflight for source-only work.
2. If `unity` is missing, install the official CLI under the user's standing
   authorization, inspect the downloaded installer, and verify the binary. Do
   not substitute a legacy MCP connection.
3. Verify `unity --version`, inspect relevant help, and apply `unity-cli`'s
   repository version gate. Unity 6+ uses `unity status --json`, full
   `--project-path`, and an exact canonical-root/complete-version match.
   Pre-Unity-6 uses
   [the exact MCP identity gate](../../../unity-cli/SKILL.md#exact-mcp-identity-gate)
   before selecting even one instance, then verifies pinned project-info readback.
4. Use direct CLI/Pipeline commands first. When MCP protocol is required, use
   built-in `unity mcp` configured and targeted through the CLI.
5. Legacy standalone Unity MCP and UnitySkills REST are opt-in only when the
   user explicitly requests them for the current task. The exception is MCP for
   Unity under the `unity-cli` pre-Unity-6 version gate.
6. Use exactly one mutation path. Check the applicable live transport before
   safe file-only work; empty CLI status does not invalidate proven pre-Unity-6
   MCP identity. Unproven identity blocks Editor work. File inspection cannot
   substitute for required live evidence or bypass serialized-asset approval.
   Manual Unity YAML editing is the last resort.

## Mutation Safety

- Use read/query operations before mutations.
- Use dry-run and inspect the diff before medium- or high-risk mutations.
- Keep UnitySkills in approval mode for scene, prefab, ScriptableObject,
  Addressables, package, and project-setting writes.
- Never enable or select bypass automatically.
- Use exactly one transport for each mutation. Do not repeat a write through
  UnitySkills and MCP.
- Wait for compilation, asset import, and domain reload to settle before
  verification.
- Verify Console state, affected assets, and dirty/save state after writes.

## Permission Alignment

The repository uses Claude `acceptEdits` for low-risk in-scope code/tests and
explicit `ask` rules for package, project-setting, serialized-asset, and git
publication mutations. Project settings disable Claude `auto` and bypass modes.
UnitySkills approval remains a second independent boundary. The stricter
effective gate wins; neither layer's approval silently authorizes the other.
