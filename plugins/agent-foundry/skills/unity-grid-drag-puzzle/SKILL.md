---
name: unity-grid-drag-puzzle
description: Implement or reconstruct a Unity grid drag puzzle with irregular multi-cell pieces, pointer ownership, collision-safe previews, axis constraints, matching exit gates, and validated board commands. Use for block sliding and gate exits, not general drag-and-drop UI.
---

# Unity Grid Drag Puzzle

Build the mechanic from its domain rules before connecting input or animation.
Use `unity-cli` for project readiness and verification, and `unity-game-dev`
for the project's stack and code conventions. Read
[the mechanic recipe](references/mechanics.md) before implementing movement,
picking, exits, or command validation.

## Establish the contract

Inspect existing board models, commands, input, session state and tests. Name
allowed paths, owners and verification channels. Follow existing task and
serialized-asset approval rules; this skill does not authorize package or
asset changes. Reuse the project's dependency and input systems.

Record these player-facing choices from the current design or ask for the
missing choices that affect implementation:

- Which cells are floor, how irregular footprints are represented, and which
  effects can restrict movement or exit.
- Whether exit happens on valid contact, outward push, or release. The recipe
  uses immediate contact at the validated integer preview; do not mix it with
  an old visual-alignment threshold.
- Gate fit and color matching, corner selection, pickup tolerance, axis locks,
  timer start, pause, and cancellation behavior.

Keep board sizes, render scale, thresholds, pool capacity and material choices
as project configuration. They are not portable mechanic requirements.

## Implement in this order

1. Create a plain immutable authored model and per-attempt board state with
   flat occupancy, stable piece IDs and occupied-cell footprints. Validate
   before play. Preserve authored source identity if a piece can split.
2. Implement pure placement, gate fit and outward sweep predicates. A bounding
   box determines the gate span; every occupied cell determines collision.
3. Add validated commands. Recheck drag permission and allowed axes, prove
   reachability through legal unit steps, and validate an exit against the
   target preview before mutating state.
4. Add a drag preview that overlays one proposed piece without changing the
   committed board. Resolve pointer jumps as unit steps and retain a separate
   continuous visual offset for responsive dragging.
5. Add primary-pointer ownership, UI rejection, projection and deterministic
   occupied-cell picking. Capture the grab offset and axis constraints once
   per gesture.
6. Connect the session command phase, pause/teardown and owned presentation.
   Free logical cells before an exit animation. Animation callbacks must not
   decide whether a piece has exited or the puzzle is won.

Use `unity-grid-puzzle-effects` for composable restrictions and
`unity-transactional-boosters` for paid mutations. Load these only when needed.

## Verify the mechanic

During development, use the project's compile-check procedure. At the final
stage, run focused domain/input tests and verify the actual input adapter when
needed. Include:

- Fast pointer movement across an obstacle cannot tunnel; previews never
  mutate committed occupancy; release commits one reachable move.
- An L-shaped piece's empty corner is not selectable footprint or occupancy.
- Adjacent matching gates do not combine; obstacles in a notch block an exit.
- A corner with two fitting gates exits once with deterministic selection.
- Every live drag result is accepted by the command validator, including
  contextual cell gates and move-plus-exit from the target preview.
- Direct/replayed move commands cannot bypass Ice or another drag gate;
  boosters use their separately defined permissions.
- Pause, second touches, rejected presses, restart and late callbacks cannot
  resume or mutate an old attempt. A final clear wins over timeout in the same
  command phase when that is the chosen session rule.

## Deliver

Report the chosen exit/input policies, domain/input/presentation boundaries,
changed files and focused verification. Distinguish inspected test scenarios
from tests actually run, and allocation-aware code from measured device cost.
