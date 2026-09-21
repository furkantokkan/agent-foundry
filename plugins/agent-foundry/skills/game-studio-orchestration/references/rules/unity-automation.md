# Unity Automation Policy

## Transport Order

1. Use the installed Unity CLI first for Unity Editor/project inspection and
   supported mutations.
2. Verify `unity --version`, inspect the relevant command help, and confirm the
   exact project root/version with `unity status --json`. Pass `--project-path`
   whenever multiple Editors may exist.
3. Use CLI/Pipeline commands or built-in `unity mcp` for supported operations.
4. If CLI/Pipeline is unavailable, mismatched, or insufficient, use a matching
   Unity MCP connection. If MCP is also unavailable, query UnitySkills
   `GET /health` and prove identity with `project_get_info.result.projectPath`.
5. Follow the selected transport's risk/approval flow and use exactly one
   transport for each mutation.
6. If no live transport is usable, continue with pinned Editor/file inspection
   only for work that does not require live state. Manual Unity YAML editing is
   the last resort.

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
