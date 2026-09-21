# Unity Automation Policy

## Transport Order

1. Use the installed Unity CLI as the mandatory control plane for every Unity
   task, including preflight for source-only work.
2. If `unity` is missing, install the official CLI under the user's standing
   authorization, inspect the downloaded installer, and verify the binary. Do
   not substitute a legacy MCP connection.
3. Verify `unity --version`, inspect relevant command help, and confirm the
   exact project root/version with `unity status --json`. Pass `--project-path`
   whenever multiple Editors may exist.
4. Use direct CLI/Pipeline commands first. When MCP protocol is required, use
   built-in `unity mcp` configured and targeted through the CLI.
5. Legacy standalone Unity MCP and UnitySkills REST are opt-in only when the
   user explicitly requests them for the current task.
6. Use exactly one mutation path. If the verified CLI cannot expose required
   live state, continue with pinned Editor/file inspection where safe. Manual
   Unity YAML editing is the last resort.

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
