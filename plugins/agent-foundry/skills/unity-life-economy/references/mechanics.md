# Timed currency and attempt charging recipe

## Pure refill arithmetic

Inputs are amount `a`, maximum `m`, positive interval `d`, current UTC `now`
and optional start `s`, all using documented consistent time units. Validate
configuration and saved amounts at the boundary. Keep intermediates wide
enough for long elapsed durations; check arithmetic rather than overflowing.

```text
if d <= 0 or a >= m:
    return (a, no timer)
if start missing or s > now:
    return (a, start = now)
gained = floor((now - s) / d)
if gained >= m - a:
    return (m, no timer)
return (a + gained, start = s + gained * d)
```

Advancing start by whole intervals retains partial progress. A future start
resets the timer without granting currency; this is a clock-rollback policy,
not cheat detection. When below maximum, countdown is
`max(0, s + d - now)` after advancing. A full resource shows no countdown.

Example with maximum 5, amount 1, interval 60 seconds, start 100 and now 250:
two lives accrue, amount becomes 3, start becomes 220, and 30 seconds remain.
At now 400 the amount reaches 5 and the timer stops.

## Transactions

Advance the relevant regenerating resources before reading affordability or
applying changes. Add/take operates on the advanced candidate. Dropping from
full starts the timer at now; spending again while below maximum retains its
current progress. Clamp permitted deductions at zero according to the domain
contract, or reject unaffordable spending; do not confuse the two policies.

Paid refill refuses full wallets, invalid offers and insufficient payment.
Debit the payment currency and restore the life maximum in the same snapshot,
clearing its timer. Regenerating payment currencies must be advanced too. One
commit yields one revision. A failed commit changes neither currency and
publishes no reactive balance update.

Use one app-scoped writer. Acquire its lock before deriving from latest state;
preparing before the lock can lose a concurrent update. Persist then replace
committed snapshot and publish. Store explicit zero values so empty stock is
not re-seeded from configuration defaults. Keep authored settings read-only.

The queued caller token can cancel its wait before a write starts. Once
started, the save owner's token governs the operation; the caller may leave
without cancelling persistence. The writer tracks faults and completion.
Views check current generation before handling the result.

## Projection and UI

An availability query can apply the pure rule to committed state without
writing, while subscribers observe only committed values. Label these roles
clearly so projected refill is not mistaken for a persisted revision. Save
transactions always recalculate with injected current time under the lock.

Use the active view's owned refresh loop or time signal. Update labels only
when the displayed seconds/balance changes; stop on disable/disposal. A
countdown refresh is not a reason to write a save each second. Expose pending
purchase/refill state and block duplicate submissions until completion.

## Attempt life cost

A useful reference policy is: leaving before gameplay starts is free; a won
attempt is free; a failed attempt costs one life and retrying that failed
attempt does not charge another. Define what counts as gameplay starting and
when a new attempt re-arms charging. These are product policies, not universal
life-system rules.

Track uncharged, pending and completed charge ownership. Decide failure
behavior explicitly. Retaining an attempted latch after a failed save gives
at-most-one submission but may grant free failed play; retrying the write
requires a safe pending/error state and duplicate protection. Never label a
failed write "charged." Durability across crashes requires persisted attempt
identity or a server transaction; an in-memory latch only covers a live flow.

Insufficient lives routes to the refill flow before the next eligible attempt.
Keep the originating attempt and navigation generation identifiable. A stale
refill result cannot open or restart gameplay that has been replaced.

## Verification matrix

Pure math: just before/at/after interval, several intervals, fractional
remainder, full, missing start, future start and very long elapsed duration.
Transactions: spending from full, another spend during partial progress,
payment currency refill, insufficient funds, failed storage, concurrency,
explicit zero stock, queued cancellation and started-write survival.
Flows: first press/start, loss, retry, win, home before start, home after loss,
failed life save, failed attempt launch, refill cancellation and late success.
