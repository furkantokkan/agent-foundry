# Composable board effect recipe

## Contract seams

Keep a fixed per-attempt collection of small rule interfaces:

| Hook | Result | Composition |
| --- | --- | --- |
| Drag permission | allow/refuse | all allow |
| Axis constraint | permitted X/Y mask | intersect |
| Cell entry | allow/refuse at proposed origin | all allow |
| Exit | refuse / allow and leave / allow and stay | refusal wins; stay prevents removal |
| Board event | accepted state transition | deterministic delivery |
| Booster target | allow/refuse by command kind | all allow |

Empty hook collections preserve baseline board behavior. Evaluate permissions
without side effects. Pass a preview reader and the necessary piece identity;
do not let hooks reach into a scene singleton or input component.

A module owns typed metadata parsing, validation, state construction and hook
registration, with optional view construction. The registry rejects duplicate
type IDs. Build a candidate context only after clearing previous ownership,
and publish it only when every module is ready. A failure clears candidate
resources and leaves no usable previous context. Matching IDs alone cannot
authorize a different level object or attempt; check identity and generation.

## Arrow

Author an axis mask, such as horizontal or vertical. Apply it both to drag
steps and gate exit side selection. Multiple constraints intersect; an empty
mask permits neither movement nor exit. A piece produced by splitting retains
the authored source identity and arrow restriction. Do not invent independent
mutable copies of immutable axis metadata.

## Ice

Author a non-negative clear count. Fresh attempt state copies it into remaining
counts indexed by runtime piece ID. While remaining is positive, refuse drag
and exit but retain occupancy. Advance a piece's ice once for each distinct
actual removal of another piece; never advance on ordinary movement,
non-removing gate interaction, split notification or animation completion.
Clamp at zero, and specify how duplicate events are deduplicated.

On a footprint split, every child inherits the parent's current remaining
count, not the authored starting count or zero. Reserve slots before play or
explicitly handle capacity exhaustion. Splitting itself thaws nobody. Decide
as a product rule whether two children subsequently removed count as two
removals; encode that choice in the semantic event identity.

## Booster restrictions

Drag permission and booster permission are separate contracts. A frozen piece
can remain eligible for a particular booster when the design allows it. Build
a type-by-command restriction table at initialization, then query active
effects for the target. Use command kinds such as remove-cell, remove-piece or
remove-color rather than one generic "can boost" flag.

A remove-cell command preserves at least one occupied cell and can split the
remaining cells into connected components. Publish footprint/child events so
effects propagate correctly; do not pretend the parent was cleared. For
category removal, filter each member by the same restrictions used for direct
targeting. Some matching pieces can survive because they are ineligible.

## Barrier extension

Treat barriers as cell-entry restrictions. For a closing cell underneath an
already occupying piece, distinguish entering from leaving: when the reader
shows that piece currently on the cell, it can leave or move within its own
occupancy if that is the specified rule. Therefore every reachability step
must query with the piece shown at the explored origin.

If barriers alternate after clears, define initial open/closed state, removals
per flip, number of flips and exhaustion state. Advance only on actual removal
events; deterministically apply multiple flips if one event can represent
several removals. Authoring metadata and dormant classes are insufficient:
register the runtime module, validate the solver adapter, expose support and
test composition before accepting a Barrier level for playback.

## Verification cases

- No hooks produce the original movement and exit results.
- A permissive later hook cannot undo an earlier denial.
- Ice decrements for distinct other removals only, never below zero.
- Splitting copies the current counter and axis restriction to every child.
- Restart and domain-reload configurations leave no shared mutable state.
- A failed later module never publishes partial or previous-attempt state.
- Same level ID with different identity cannot reuse prepared context.
- Enter/leave tests for a closed cell agree between live drag and reachability.
- Unsupported modules are refused before play; editor support is not mistaken
  for runtime support.
