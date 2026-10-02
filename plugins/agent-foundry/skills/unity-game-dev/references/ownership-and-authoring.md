# Unity Ownership and Authoring

Use the relevant sections for runtime lifecycle, persistence, scene flow,
authored data, UI, editor tooling, pooling, or rendering work. These are reusable
engineering rules; repository decisions set the actual state names, capacities,
resolutions, packages and assets. Follow the caller's approval policy and
`unity-cli` transport/version gate before Unity operations.

## Lifetimes and transitions

- Keep domain rules in plain C# and MonoBehaviours as lifecycle/view adapters.
  Assembly dependencies point toward stable domain contracts; split assemblies
  only for real ownership boundaries. Match services to application, scene,
  attempt or view lifetime and dispose child scopes on replacement/unload.
- One explicit session owner decides whether gameplay runs. Every loop,
  timer, subscription, tween, input callback and async task has an owner and
  stop point. Suspend/teardown disables input and clocks before opening its UI;
  teardown also cancels work, disposes subscriptions and returns pooled objects.
  Use the project's owned pause path rather than global `Time.timeScale`.
- Domain outcomes do not wait for animation callbacks. Any terminal visual
  finish is bounded, foreground-aware and owned; it cannot alter the outcome,
  rewards or gameplay state. Backgrounding/unload can force its cleanup.
- Publish observable transitions after owned setup/cleanup is ready. A
  synchronous observer may immediately restart, navigate or dispose the owner.
  Reject calls after disposal and prevent the old transition from touching a
  replacement attempt. Test reentrant observers explicitly.
- Pass the actual owner's cancellation token and retain/await async work;
  no `async void` or untracked fire-and-forget. Shared saves, transitions and
  preloads may outlive a requesting scene: cancelling that caller's wait must
  not cancel the operation. Its owner still observes faults and completion,
  and teardown cancels it when appropriate. Late results check owner generation.

## Authored data and persistence

- Give each dataset one editable authority: ScriptableObject by default, or
  JSON when volume/patching/tooling favors it. Keep authored assets under the
  project data root, scripts in their owning assemblies, and player saves
  separate. Derived formats have a documented one-way conversion.
- Copy mutable values into scope-owned plain models. Do not mutate shared
  authored assets during play. Editor and runtime readers own separate parsed
  catalogs, including when domain reload is disabled.
- Distinguish content validity from currently supported runtime mechanics.
  Designers may author a valid future mechanic while playback reports that it
  is unsupported. Do not silently discard it or pretend to simulate it.
- For large ordered collections, consider a stable-ID manifest and bounded
  chunks. Load only needed runtime content; choose chunk sizes from content and
  update costs. Validate before writing, detect prior external edits, retain
  recovery data, and write changed chunks before publishing their manifest.
  Document recovery from partial writes; several file writes are not one atomic
  transaction merely because the manifest is written last.
- One application-scoped typed save service serializes versioned snapshots
  under its own token. Write a temporary file, flush, replace atomically and
  retain a backup. Publish values only after commit. Failed commits change
  nothing; corrupt reads try the backup before defaults, and newer unknown
  formats are never overwritten.
- Capture validated immutable transaction intent before saving. Commit a
  spend/reward before applying it, block duplicate pending submissions, and
  retry that same intended snapshot rather than adding the reward again.
  Specify background/navigation and crash recovery behavior in the project;
  save completion never resumes a departed or paused attempt by itself.
- Persist stable string IDs, register explicit JSON converters, avoid
  type-name-driven deserialization, and preserve reflection-only DTOs for
  IL2CPP. Serialization and file I/O stay outside gameplay ticks.

## UI authoring and scene input

- Humans edit the real modular UXML/USS template. Keep layout, typography,
  static content and fixed slots there; runtime binds stable names and replaces
  only dynamic data/state. Clone templates for variable-length lists.
- Standalone screens/widgets load their common styles/font and preview visibly
  with clearly identified representative text/icons. Samples never become
  gameplay/economy defaults. Embedded overlays start closed before the first
  frame, including delayed binding and document re-enable; scoped host rules
  must not hide the standalone template.
- Match each UI Builder document's canvas to its PanelSettings reference
  resolution. Save through UI Builder, reopen each document and read back its
  dimensions. Fit Canvas changes zoom only. Do not edit `Library/UIBuilder`
  settings while the Editor's in-memory document can overwrite them.
- Verify standalone styling, unbound host safety, sample replacement and
  open/close behavior. Runtime screenshots and UI Builder previews establish
  different properties; one does not replace the other.
- When persistent panels overlap additive/preloaded scenes, give the
  EventSystem/input owner a lifetime spanning scene replacement. Check panel
  handler parenting, duplicate owners, unload/re-enable and actual touch input.
  Distinguish concurrent copies of the same scene by handles. Verify normal
  startup and supported direct scene entry.

## Editor writes, drafts and previews

- Save only operation-owned assets. Avoid global `AssetDatabase.SaveAssets`
  and vendor convenience methods that implicitly save unrelated dirty assets.
  Move assets with their `.meta` files through the actual VCS to retain GUIDs;
  preserve serialized type identities during rename/migration.
- Editor tests use isolated settings/subassets and exact scratch paths, account
  for automatic import callbacks, and preserve user windows/unsaved drafts.
  Compare protected disk fingerprints and an unrelated dirty sentinel before
  and after. Side effects fail verification even when assertions pass; report
  protective skips separately from passing cases.
- Preserve drafts across reload and test-play round trips. Recovery state is
  transient and never a second editable content authority. Restore prior Play
  Mode scene settings and release the tool's own listeners and temporary data.
- Scene previews consume validated snapshots in a transient `DontSave`
  hierarchy. Invalid drafts keep the last valid preview and show an actionable
  error. Clean up on relevant window/scene/Play Mode boundaries; preview playback
  never mutates authored data, Undo history or scene dirty state.
- Solvers/validators reuse runtime domain predicates and commands. Cover
  conversion and legal-command parity, deterministic results, unsupported
  mechanics and cancellation. A time/state budget hit means inconclusive,
  never proof that no solution exists.

## Pools and measured rendering

- Keep immutable checkout/pool identity even if an object's runtime shape/type
  changes. Define reset hooks, warmup/capacity and exhaustion policy, return all
  checkouts at teardown, and distinguish factory registration from pool lifetime
  ownership. Measure allocations and instantiation on the actual interaction.
- One view owner composes each renderer's cached `MaterialPropertyBlock`.
  Effects change owned values without erasing unrelated properties; pooling
  resets stale state before reuse. Avoid per-object material clones.
- Compare shared-material/instancing and SRP Batcher alternatives on matching
  content, quality and hardware. Use Frame Debugger batching evidence, SetPass
  counts and CPU/GPU measurements. Fewer materials or a compile pass does not
  prove a faster frame; keep one measured path instead of speculative variants.

## Verification and transfer

- Follow `unity-cli`'s Roslyn-first development checks and final-stage focused
  tests. Verify owner teardown, cancellation, reentrancy, save failures, dirty
  asset preservation and runtime/editor rule parity when those boundaries change.
- Separate source inspection, compiled assemblies, executed tests, visual
  evidence and device/build evidence. Report unavailable channels explicitly.
  Development-tool assemblies stay out of players; builds remain subject to
  target approval. Do not install packages or change serialized assets merely
  to apply these guidelines.
- This reference generalizes reviewed production patterns. Adding it verifies
  documentation and routing, not runtime behavior in every consuming project.
  Project-specific tuning, identities, private paths and historical acceptance
  claims are intentionally left with their owning repository.
