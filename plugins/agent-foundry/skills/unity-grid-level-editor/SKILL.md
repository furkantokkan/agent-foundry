---
name: unity-grid-level-editor
description: Implement a Unity UI Toolkit grid level editor with pure edit commands, irregular-piece transforms, grouped Undo, reload-safe transient drafts, exact-source saving, bounded solver validation, and isolated test play. Use for puzzle authoring tools that share rules with runtime.
---

# Unity Grid Level Editor

Use `unity-cli` and `unity-game-dev` for repository readiness and tooling.
Read [the authoring recipe](references/mechanics.md) before changing draft,
geometry, save, preview or solver behavior. Inspect the runtime board rules
and existing authoring authority first.

## Establish ownership

Choose one authored data authority per dataset. A draft, recovery record,
runtime catalog and scene preview are separate owned projections, never
additional editable sources. Follow the current JSON/ScriptableObject choice;
do not add import/merge/export round trips without a request.

Name allowed code paths, exact writable datasets/settings and test scratch
paths. Save only owned assets, never globally with `AssetDatabase.SaveAssets`
or a vendor helper that saves all dirty assets. Asset/schema/scene/settings
changes retain their target approval. Tests must leave unrelated dirty assets
and production data untouched.

## Build the authoring lane

1. Use pure edit commands: clone validated level data, apply one requested
   edit, return a candidate or a refusal, and leave the input unchanged.
2. Keep UI tool/selection/ghost state outside authored data. Use one shared
   geometry service for rendering, coordinate conversion and hit testing.
3. Own one transient serialized draft for Undo and editor bindings. Store
   saved baseline and pending template edits separately. Group each user
   gesture and join a caller's group when the gesture is already owned.
4. Preserve draft recovery across reload under a window-scoped identity.
   Restore only when database identity, selected level and source fingerprint
   match. Unbind before disposing the old draft.
5. Validate the save candidate and compare external source changes before
   writing. Write exact canonical data successfully before marking saved or
   transferring pending template edits. Use one-way runtime derivation.
6. Build previews in a transient `DontSave` hierarchy from validated snapshots.
   Invalid edits retain the last valid preview. Preview/playback does not
   write authored data, Undo history or scene dirty state.
7. Reuse runtime predicates/commands for support checks and solving. Separate
   unsupported, cancelled and budget-exhausted results from proven unsolvable.
8. Isolate test play with a temporary intent, test save and restored start-scene
   setting. Teardown preview before entering Play Mode and clean up on return.

## Verify and deliver

At the final stage, test pure command refusal, four rotations, pivot and edge
kick, ghost grip, resizing, Undo/Redo per gesture, reload restoration, changed
source rejection, exact-save failure and an unrelated dirty sentinel. Check
solver/runtime parity, determinism, unsupported content, cancellation and
budget exhaustion. Verify preview/test-play cleanup without wallet changes.

Use compile checks during development. Report the authority map, exact saved
targets, supported mechanics, solver verdict limits and actually executed
verification. Capacity and chunk sizes are project choices, not this recipe's
requirements.
