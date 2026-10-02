# Grid drag and exit recipe

## State and ownership

Use integer cell coordinates with one documented axis convention. Keep floor
mask, gate definitions and authored footprints immutable. A fresh attempt
owns occupancy, piece origin/status, effects, input and commands. Index a flat
board as `y * width + x`; validate dimensions and all cells before indexing.

A footprint is a list of occupied relative cells plus cached extents, not a
filled rectangle. Keep committed integer origin, validated preview origin and
continuous visual origin separate. A preview reader returns the dragged
piece at its preview cells, treats its old cells as empty, and preserves all
other occupancy. Reuse scratch storage or stamped arrays after capacity is
known; do not infer that the whole input stack allocates nothing.

## Pointer to preview

1. Acquire one pointer on press. Reject UI hits, projection failure and presses
   outside the interaction region. A rejected press stays inert until release;
   another finger cannot replace the active pointer.
2. Project a camera ray onto the board plane. Pick by projected occupied-cell
   quads: containment first, otherwise squared screen-edge distance. Use a
   stable ID tie-break. Distance tolerance is an explicit design choice;
   perspective screen distance and board-space distance are not equivalent.
3. Capture `grabOffset = pointerBoard - integerOrigin`. Intersect all permitted
   axes once for the gesture; do not change the drag's axes halfway through.
4. Compute desired origin from pointer minus grab offset. Round each component
   half away from zero. The rounded target controls completion and step signs.
   At every step compare the unrounded desired origin minus the current
   preview origin to choose the greater displacement first (X on a tie), then
   try the other axis if blocked. Stop when neither moves or a bounded step
   limit is reached. Never teleport directly to a distant legal destination.
5. Placement tests every occupied cell for bounds, floor, other pieces and
   effect cell gates. For each query, the reader must show the piece at the
   origin it currently occupies, not the original press position.
6. Draw fractional lead only toward legal neighboring placements. Suppress
   blocked-axis lead. When both leads are individually legal but their
   diagonal is blocked, suppress the smaller lead with a deterministic tie.
   Verify continuity across the rounding boundary using the chosen lead cap.

## Exit predicate

Evaluate against the proposed reader without changing the board:

- The piece is flush with the requested board side.
- A single matching-color gate covers the complete perpendicular extent of
  the footprint. Adjacent same-color gates remain separate spans.
- Axis constraints and exit hooks permit this side.
- Sweep every occupied cell outward until clear of the board. Other pieces,
  voids and closed gated cells in the swept region block the exit; the moving
  piece's own cells do not. An interior notch can contain a blocker even when
  the boundary row is clear. Treat crossings at the selected gate as legal;
  do not demand floor beyond the board.

For immediate-contact exits, evaluate before movement and after every legal
unit step. The integer preview under a fitting gate is sufficient even when
the fractional rendering is still beside it. If two sides fit at a corner,
rank the outward pointer displacement with a fixed side tie-break and consume
the press after one exit. Push/release alternatives require a separately
specified predicate; they are not extra checks on this contact rule.

## Commands and session order

Release queues a move only if the preview differs. Contact queues a combined
move-and-exit. The handler rejects stale origin/status, denied drag permission,
disallowed axes and unreachable targets before writing. Direct/replayed moves
cannot bypass Ice; booster commands have their separate permission contract.
If direct moves can traverse multiple
cells, use bounded BFS over legal unit origins with a reusable queue and
visited stamps. Mark a neighbor visited after its entry is accepted, since
cell gates can depend on the origin represented by the reader.

A combined command validates exit using the target preview and releases the
old committed cells only after all predicates succeed. Log accepted commands
at their logical tick/time. A true removal emits one removal/exit event; a
permitted non-removing exit must not emit a clear event or free the piece.

Run commands, then outcome decisions, then countdown, then presentation. This
lets a valid final clear beat a timeout reached in the same tick. The chosen
timer-start rule can be first accepted press, first successful move, or another
explicit policy; even a frozen piece can receive a press, so define it.

Pause can retain a legal preview by queuing it for the next Playing command
phase. Consume the current press until release. Restart/teardown clears old
input, queued commands and previews; an attempt generation guards late work.
Views align and animate already accepted state. Give every input subscription,
tween and callback one owner and stop point.

## Regression matrix

Test narrow and irregular pieces, all four sides, floor holes, neighboring
gate spans, corner ties, long pointer jumps, diagonal obstruction and blocked
notches. Cross-check live drag results against the command validator. Verify
that evaluation never writes occupancy and that move-plus-exit uses the target
origin. Test primary-pointer loss, a second touch, UI rejection, interrupted
drag, disposal and restart. Keep physics/rendering scale outside domain tests.
