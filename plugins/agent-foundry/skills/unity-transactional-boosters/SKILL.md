---
name: unity-transactional-boosters
description: Implement Unity consumable boosters with inventory-backed targeting, immutable use intents, atomic save debits, cancellation-safe completion, starting-booster selection, opening phases, and pause/restart rules. Use when a booster must be paid for durably before changing gameplay.
---

# Unity Transactional Boosters

Use `unity-cli` and `unity-game-dev` for project setup and verification. Read
[the transactional recipe](references/mechanics.md) before connecting save,
session, UI or command code. Use the existing typed save/API boundary.
For a server-authoritative economy, load `firebase-game-backend` when relevant
and let the server commit inventory; client-side debits are not authority.

## Capture product policies

Inspect inventory IDs, save transactions, session states, board predicates,
target UI and opening flow. Specify:

- Eligibility for each booster and exact domain command/effect it produces.
- Selection/cancellation behavior, time-freeze semantics and backgrounding.
- Whether leaving after a committed debit consumes the item, refunds it, or
  resumes a durably recorded intent. Do not silently infer refund policy.
- Starting-booster failure policy: plain play without effects or blocked
  launch. Choose seed/targets once and retain them across pause and resume.
- Purchase success UI behavior belongs to the host; buying adds stock and
  does not automatically select or use a booster.

Declare owned code and asset paths. Respect existing contracts, save-format
approval and serialized-asset gates. Reuse the current async and UI stack.

## Implement the transaction lane

1. Separate stock/configuration, transient targeting mode and immutable intent.
   Selecting, switching, cancelling or refusing a target never debits stock.
2. Use one pure target predicate from input and command execution. Capture
   the committed target, booster ID, command/effect and attempt generation.
3. On acceptance, clear held/parked moves and enter the existing session's
   saving suspension, such as Paused with a Saving reason. Use its single
   gameplay owner rather than a parallel pause flag. Return before outcomes,
   countdown and view synchronization in that tick. Yield out of the tick
   before persistence if the store may complete synchronously.
4. Prepare the debit under the single save writer's lock from the latest
   committed snapshot. Persist before publishing balances. Copy caller-owned
   debit collections before awaiting.
5. Keep started work under its real owner token. A caller can stop waiting;
   it cannot cancel a committed or active shared write. Track faults and
   completion even if the originating view leaves.
6. Retain a successful intent for the next eligible command phase, discard a
   failed one, and reject stale-generation completion. Clear an intent before
   applying it so reentrant observers cannot replay it. Background completion
   waits for an explicit permitted resume.
7. Prepare starting boosters only after board validation and warmup. Filter
   unavailable/invalid candidates, choose once, and debit the eligible set in
   one transaction. Apply their effects in an owned opening phase.

## Verify and deliver

Use compile checks during development and focused tests once at the final
stage. Cover no-charge selection/refusal, one debit and one use, failure
rollback, queued versus started cancellation, stale completion, background
resume, restart after debit, deterministic starting choices, combined debit
and pause during opening. Test a synchronous store to prove no I/O runs in
the Playing tick. Report the navigation/refund/failure policies and actual
verification. In-memory deduplication is not durable idempotency across crashes.
