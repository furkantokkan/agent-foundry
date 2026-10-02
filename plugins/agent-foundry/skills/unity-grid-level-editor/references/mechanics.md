# Grid level authoring recipe

## Data, drafts and Undo

Use plain level data and pure edit commands. Every operation returns a cloned
candidate or a reason for refusal. Check occupied cells against floor, bounds,
other pieces and closed authoring gates; never mutate the original on refusal.
Assign the lowest free stable piece ID when that is the project's authoring
policy, preserving IDs, color and effect metadata through transforms.

One transient `ScriptableObject` with `HideAndDontSave` can supply serialized
bindings and Undo without becoming an authored asset. Keep a saved content
baseline distinct from the last synchronized binding state. Include pending
template footprint edits in dirty detection when they are intended to save;
presentation choices such as palette order need not dirty level content.

Independent gestures open/register their own Undo group and close it once.
A child tool participating in an existing gesture joins that group instead of
creating another. Record level and accompanying metadata on the same owned
target. Identical commands do not generate Undo noise. Saving moves the saved
baseline but need not replace the draft or destroy its Undo history.

For domain reload recovery, keep a window-scoped temporary record containing
draft, metadata, selected level identity, source GUID/path and source content
fingerprint. `SessionState` can cover reload/test-play in one Editor session;
it is not persistent recovery after an Editor restart. Restore only if source
identity, selection and fingerprint still match; otherwise discard with a
clear warning. Restore before rebinding. Unbind, dispose the serialized wrapper,
clear Undo for the owned transient object, then destroy it on replacement.

## Coordinates, rotation and ghost placement

Centralize board-to-canvas and canvas-to-board conversion. With data Y upward
and UI Y downward, top-row conversion uses `height - 1 - y`. Rendering and hit
testing share cell size, pan origin, zoom and edge-control margins.

Normalize occupied-cell offsets without losing their absolute origin. A
quarter-turn rotates about the chosen pivot, normalizes the result and shifts
the piece origin by the corresponding correction. Doubled integer coordinates
represent cell-center and grid-corner pivots without float rounding. If the
bounding center is unsuitable, choose a nearest occupied-cell pivot with a
stable tie-break. Four turns on open space must restore absolute occupancy.

When rotating an already placed piece at a board edge, compute the minimal
translation bringing its rotated extents inside. This kick still must pass
occupied-cell legality; it cannot waive a void, barrier or another piece, and
an oversized shape remains refused.

An armed palette ghost retains a grip point under the pointer when rotated.
Its relative cells can be negative. Normalizing them without compensating
origin moves the ghost away from the pointer. Do not apply the placed-piece
edge kick to this ghost: show/refuse illegal placement while preserving grip,
unless the design separately chooses a snapping policy. Tool state does not
write the level until placement succeeds.

For reusable piece catalog identity, normalize translation and choose the
smallest stable encoding among the eight rotation/mirror variants when the
design treats those variants as one shape. Validate nonempty, unique,
edge-connected cells and configured extents first. Keep the actual oriented
footprint for placement; canonical identity intentionally loses orientation.
Persist the documented encoding, never a display name or `GetHashCode()`.

## Board resizing

Produce a candidate plus a destructive-change summary before committing.
Adding/removing on the left or bottom shifts origins and edge coordinates so
remaining pieces keep their intended spatial relationship. Added cells become
floor according to the chosen board policy. Shrinking removes affected piece
records or refuses the resize according to the product rule; do not silently
truncate a footprint into a different mechanic.

Move gates with their owning board edge and clip their spans on resized
perpendicular edges; remove empty spans. Update outer void/outline corners
consistently. Report removed pieces/gates/cells before a destructive UI
confirmation. Dimension limits are configuration.

## Exact source saving

Keep editor and runtime catalogs separate, including when domain reload is
disabled. For a large ordered JSON dataset, a stable-ID manifest can index
bounded packs; runtime loads only required packs and editor loads its own
editable catalog. Pack size is configurable. All address/catalog projections
have one documented one-way derivation from the source.

Validate the candidate, stable-ID uniqueness and supported structure. Compare
the loaded fingerprint with the current source to detect external edits.
Write only changed owned files/assets. Preserve a recoverable previous version
and define failure recovery for a multi-file save; atomic single-file writes
alone do not make a pack-plus-manifest batch atomic. Write packs before their
referencing manifest, and do not mark clean or transfer pending template edits
until every required write succeeds. Avoid global save helpers.

## Validation and solving

Structural validity and runtime support are distinct. Reject unsupported
mechanics before searching. Convert to the same domain model as play and reuse
placement, legal movement, exit sweep and effect semantics. Cached tables can
precompute legal origins and swept blocker masks, but must preserve irregular
cells and contextual gates. A simplified bounding-box solver proves nothing
about runtime behavior.

Return explicit verdicts:

| Result | Meaning |
| --- | --- |
| Solvable | a valid command path was found |
| Unsolvable | an exhaustive sound search proved no path |
| Inconclusive | time/position/memory budget ran out |
| Not checked | unsupported, cancelled or invalid input |

Use deterministic order, bounded memory/time and cancellation. A separate
solution-listing pass can be cancelled after a solvable verdict without
erasing that verdict. Cross-check optimized search against a simple reference
on bounded fixtures and validate every returned command with runtime rules.

## Preview, test play and sentinel checks

Preview consumes validated snapshots and owns all temporary objects and
subscriptions. Keep the last valid display on invalid drafts. Release on
window close, scene replacement and Play Mode boundaries; do not leave a
scene dirty or authoring Undo entry after playback.

Test play starts from a validated/saved snapshot or explicitly isolated draft,
never an accidental stale source. Carry exact database/level identity in a
temporary test intent, use an isolated save/wallet, temporarily change the
start-scene setting only under its approved owner, and restore it on return.

Before an editor test, dirty an unrelated owned scratch sentinel and record
its disk bytes. After the operation, require both bytes and dirty state to
remain unchanged. Also check source bytes, selection, draft history, preview
objects, settings and test-play cleanup. Passing functional assertions with
unexpected authoring side effects is a failed verification.
