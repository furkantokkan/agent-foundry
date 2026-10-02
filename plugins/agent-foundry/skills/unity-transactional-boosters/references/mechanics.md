# Durable consumable use recipe

## Boundaries

Use stable string IDs for booster stock and payment currencies. Keep inventory
in the save snapshot, authored offer/configuration in its own authority, and
targeting/intent in the attempt owner. UI observes committed stock and sends
requests; it does not mutate board state or balances.

Targeting mode is disposable state. Pressing the selected booster can toggle
it off; selecting another can switch; an empty board press can cancel. An
ineligible occupied target can retain selection and show feedback. These are
explicit interaction policies; every case before acceptance costs nothing.

## Eligibility and intent

Use the same domain predicates at pointer selection, starting-candidate
selection and command validation. Remove-cell requires at least one cell to
remain and may split connected components. Remove-piece and remove-category
must honor command-specific effect restrictions; some same-color pieces can
survive a category effect. Precompute candidate storage when useful.

Accept only in Playing with no unresolved save or opening intent. Snapshot an
immutable command/effect against the committed board, not an uncommitted drag
preview. Include attempt generation and stable target identity. Discard held
input and parked move commands so a pre-save drag cannot replay after resume.

## Transaction phases

`accept use -> suspend for saving -> ready or failed intent -> eligible command phase`

These are transaction phases, not required session enum values. Reuse the
existing session's saving suspension, such as Paused with a Saving reason,
under its single gameplay owner. It blocks gameplay, navigation and conflicting
uses. Its accepting tick returns before win checks, timer and presentation
sync. An async method can run synchronously until its first incomplete await,
so explicitly yield/schedule persistence outside that tick. A fake synchronous
store is a useful regression test.

Under a single app-scoped save lock, read the latest snapshot, validate funds,
apply all debits to a candidate, persist, then replace committed state and
publish one revision. Failure publishes nothing. Atomic local replacement
with recoverable backup is a storage implementation; server transactions use
their trusted equivalent. Clone a caller's debit list before the first await.

A queued caller may cancel before obtaining the writer. Once a write starts,
the app/save owner's token governs it, while a departing caller may stop
waiting. The owner still handles completion and faults. Apply a completion
once only if its attempt is current. Clear the retained intent before domain
execution. Backgrounding sets a resume latch; late success cannot resume play
by itself. Keep committed intent and opening phase through a permitted pause.

If navigation discards a committed intent, decide and document consumption or
refund. A generation check prevents stale application; it cannot recover an
item already spent. Crash-safe resume/refund needs a persisted intent or
transaction protocol, which is outside the in-memory recipe and must be
designed when required.

## Starting boosters and opening

Carry immutable player selections to the destination without spending during
launch navigation. Validate/load the board, create attempt state and warm
resources before choosing candidates. Filter unsupported/ineligible targets
and unavailable stock. Use an injected seed and deterministic candidate order;
choose once, then copy all eligible debits into one transaction.

On success, retain the prepared opening. On failure, the reference policy is
plain play with no starting effects or debit; a product may instead block
launch. Do not reuse a failed candidate list as if it was committed.

Separate presentation introduction, domain application and optional visual
hold. Apply accepted time effects followed by board commands in one defined
command phase. Pause retains which phase has run; resume neither re-samples
targets nor debits/reapplies. Teardown cancels the opening owner. Presentation
completion can release a hold, but cannot decide gameplay outcomes.

## Freeze and purchases

Implement time freeze in the session countdown model. Consume frozen duration
first, then subtract any leftover delta from the ordinary timer. Do not use
`Time.timeScale` or secretly pause input. A time effect need not appear in a
board command log, but it must be recorded in the appropriate replay/evidence
channel if the project requires replay.

Buying stock is one payment-plus-stock transaction. Refuse duplicate pending
buy, and ignore stale offer/view completion. The host decides whether success
closes the popup; purchase does not auto-select or cast the item. Treat old UI
tests or docs that disagree with current behavior as unresolved evidence,
never as a passed verification.

## Rewards and idempotency

If rewards share the save boundary, commit reward and progression together.
Block result navigation while unresolved and retry only failed writes. A local
"already submitted" flag prevents repeats in one live flow, but a successful
method called twice may still pay twice. Exactly-once rewards across relaunch
or retry require a durable transaction/attempt ID, deduplication and a trusted
commit protocol. Do not claim this property from a single atomic file write.

## Failure matrix

Verify insufficient stock, save failure, list mutation during await, queued
cancellation, caller departure after write begins, old-attempt completion,
background during save, successful late completion, conflicting navigation,
discard-after-commit policy, no eligible starting target, deterministic seed,
combined debit, failed starting commit and pause in each opening phase.
