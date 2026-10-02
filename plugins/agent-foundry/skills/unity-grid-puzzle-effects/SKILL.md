---
name: unity-grid-puzzle-effects
description: Implement composable Unity grid puzzle effects such as movement arrows, ice counters, cell barriers, and booster restrictions using typed metadata, per-attempt state, shared rule hooks, and semantic board events. Use when extending a grid puzzle without putting effect logic in input or views.
---

# Unity Grid Puzzle Effects

Use `unity-cli` and `unity-game-dev` for the project's operating contract.
Inspect its board predicates, commands, effect schema and tests. Read
[the composition recipe](references/mechanics.md) before adding a module.
Use `unity-grid-drag-puzzle` only when building or changing its movement system.

## Define support and behavior

Separate authored validity, registered modules and runtime support. A schema
entry or editor icon does not prove that a mechanic is playable. The source
recipe demonstrates Arrow and Ice behavior; Barrier is an extension design
whose runtime support must be implemented and verified before it is enabled.
Reject unsupported playback explicitly.

For the requested effect, capture movement/exit rules, stacking, booster
eligibility, split inheritance and the exact events that advance it. Decide
whether a permitted gate interaction removes the piece or leaves it on board.
Use stable type IDs and explicit metadata converters; avoid type-name-driven
deserialization. Do not introduce a new DI/reactive/async library for effects.

Declare code/schema ownership and serialized assets before writes. Follow the
task and asset gates, including approval for serialized schema migrations.

## Build one module

1. Parse and validate immutable typed metadata. Register one module per stable
   type ID with deterministic composition order.
2. Create fresh mutable state for the attempt, including reserved split-piece
   slots. Keep metadata, runtime state and visual state separately owned.
3. Register hooks for drag permission, allowed axes, cell entry, exit,
   semantic board events and booster targeting. Combine restrictions with
   AND/intersection; no module can reopen a permission another rejected.
4. Build all modules successfully before publishing the attempt context.
   Clear stale context first. Bind it to exact level identity and generation,
   not just an equal numeric/string level ID.
5. Drive state changes from accepted domain events, then refresh owned views.
   A split is a footprint change; movement or animation completion is not a
   removal. Make duplicate removal delivery harmless where relevant.
6. Use the same predicates from input, commands, boosters, editor validation
   and solver adapters. Do not duplicate a weaker interpretation in the UI.

## Verify composition

At the final implementation stage, test no-effect parity, combined denials,
axis intersection, frozen occupancy, distinct removals, split inheritance,
booster restrictions, contextual cell entry and non-removing exits. Restart
must create fresh state without modifying authored metadata. A later module's
construction failure must publish neither partial state nor the old attempt.

Compile during development with the project procedure. Report inspected
scenarios separately from executed tests. Include support gating and teardown
in the handoff, and keep visual polish under its own presentation owner.
