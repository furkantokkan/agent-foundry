# Unity Worktree and Asset Ownership Policy

## Story Isolation

- Run independent implementation stories in separate branches and worktrees.
- A story contract MUST declare allowed paths, forbidden paths, owned serialized
  assets, required tests, and its handoff destination before implementation.
- Do not run concurrent writers against overlapping paths.
- Implementation, verification, and bug fixing for one story proceed through
  explicit sequential handoffs unless their file ownership is disjoint.

## Serialized Assets

- A scene, prefab, ScriptableObject, `.inputactions` asset, Addressables group,
  or project setting has exactly one active writer.
- Do not concurrently edit an asset and its `.meta` file from different
  worktrees.
- Inspect scene/prefab stage and current asset ownership before mutation.
- Preserve GUIDs and `.meta` files. Do not regenerate or replace them casually.

## Agent Contract

Every code- or asset-writing handoff MUST include:

- Branch/worktree and base commit.
- Allowed and forbidden paths.
- Serialized assets owned or touched.
- Changed files and assemblies.
- Unity compilation and test evidence.
- Known risks and the next role allowed to write.

If ownership is missing or the active owner/order cannot be proven, stop with
`OWNERSHIP BLOCKED` and report the collision. If one exact live predecessor
owns the overlap and exposes a stable handoff/release signal, keep one writer,
queue the successor as `WAITING_FOR_OWNER`, and dispatch it automatically after
revalidation. Never run the overlapping writers concurrently.
