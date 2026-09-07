# Unity Automation Policy

## Transport Order

1. Use a matching Unity MCP connection first for Unity Editor/project inspection
   and mutations.
2. Confirm the MCP project root and Unity version match the exact target before
   relying on Editor state or writing anything.
3. If MCP is unavailable or mismatched, query UnitySkills `GET /health`, then
   prove exact identity separately with `project_get_info.result.projectPath`.
4. Use UnitySkills fallback reads and its dry-run/diff/batch/transaction/audit/
   approval flow. If it reports Bypass, keep it read-only and ask the user to
   select Approval in-panel; REST/chat must not change the mode.
5. If neither transport is usable, continue with pinned Unity CLI/file inspection for
   work that does not require live Editor state.
6. Treat manual Unity YAML editing as a last resort and explain why Editor-safe
   automation is unavailable.

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
