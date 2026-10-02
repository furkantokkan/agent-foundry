---
name: unity-life-economy
description: Implement Unity lives or energy regeneration with UTC refill arithmetic, offline progress, atomic paid refills, stable save IDs, attempt-level life charging, and cancellation-safe UI flows. Use for timed consumable currencies, not general economy balancing or anti-cheat.
---

# Unity Life Economy

Use `unity-cli` and `unity-game-dev` for the project operating contract. Read
[the economy recipe](references/mechanics.md) before changing refill math,
save transactions or retry/navigation flow. Use game-design skills when the
life-cost or pricing rules are undecided; this skill supplies implementation.

## Capture the rules

Inspect currency configuration, save schema/writer, attempt outcomes, retry,
home navigation and current tests. Record maximum, starting amount, refill
interval, paid-refill cost/currency, timer-start semantics and when an attempt
begins charging. Never copy a source game's numeric tuning.

Choose what happens when a life-charge write fails, and whether a failed
attempt's retry is free. An attempt latch set before persistence prevents
duplicate calls but can also suppress retry after failure; it does not prove
that a life was durably charged. Define the intended failure behavior.

Declare owned paths and follow save-format and serialized-asset gates. Reuse
the single app-scoped writer and typed services instead of a UI-owned wallet.
For a trusted economy, use authoritative server time and transactions; device
UTC enables offline arithmetic but is not anti-cheat.

## Implement

1. Store stable resource IDs, committed amounts and optional UTC timer starts
   in one versioned snapshot. Preserve explicit zero stock when migrating or
   loading; zero must not be mistaken for an absent/default entry.
2. Implement a pure refill function with injected time. Clamp gains at the
   maximum, retain fractional progress and stop the timer when full.
3. Advance regeneration on load and inside relevant save transactions. Keep
   a projected available amount distinct from the committed observed snapshot.
4. After spending from full, start a timer at the transaction time. Further
   spends while refilling preserve progress. Apply paid refill's payment and
   restored lives together in one candidate and one durable commit.
5. Prepare candidates under the writer lock from the latest committed state.
   Publish balances and revision only after persistence succeeds. Caller
   cancellation does not abort an already-started shared write.
6. Give attempt charging an explicit owner and phase. Prevent failure, retry
   and home from charging the same attempt again. Re-arm only when the new
   attempt is ready; route insufficient lives to the refill flow.
7. Refresh visible countdown only when its displayed value changes under the
   active view owner. No synchronous save or serialization in a gameplay tick.

## Verify and deliver

Use compile checks during development and focused tests at the final stage.
Test interval boundaries, partial progress, long offline periods, full-wallet
behavior, missing/future timestamps, spend from full, further spend, atomic
refill failure, concurrent writes and queued/started cancellation. Test life
charging across loss, failed retry, home, win, restart and persistence failure.

Report tuning, clock trust, charge-failure policy, snapshot/attempt/UI owners
and actual verification. Do not report an inspected test as a test run.
