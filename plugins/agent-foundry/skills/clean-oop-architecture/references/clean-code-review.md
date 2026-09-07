# Clean Code Review Checklist

## Naming

- Class names are nouns that describe responsibility.
- Method names are verbs that describe observable behavior.
- Boolean names read as predicates: `IsReady`, `CanAfford`, `HasSave`.
- Code symbols use clear English. Avoid Turkish, mixed-language, vague, or
  over-formal names.
- Prefer simple method verbs such as `Set`, `Get`, `Add`, `Remove`, `Create`,
  `Update`, `Load`, `Save`, `Open`, `Close`, `Start`, `Stop`, `Enable`,
  `Disable`, `Show`, `Hide`, `Apply`, `Calculate`, and `Validate`.
- Avoid inflated verbs such as `Ensure`, `Perform`, `Execute`, `Process`, or
  `Manage` when a simpler verb states the action. Use `Ensure` only when the
  method truly guarantees a postcondition, such as get-or-create behavior,
  repair-if-missing, or invariant validation.
- Avoid vague names: `Manager`, `Handler`, `Data`, `Helper`, `Util` unless the
  context is genuinely narrow and established.

## Functions

- One level of abstraction per function.
- No hidden mode switches via boolean parameters.
- Prefer parameter objects when values travel together.
- Return values instead of mutating distant state when possible.
- Push side effects to boundaries.

## Classes

- High cohesion: fields are used by most methods.
- Low coupling: collaborators are explicit and narrow.
- Constructors do not perform expensive work, I/O, or Unity object lookup.
- Public API is smaller than private implementation.

## Error Handling

- Do not swallow exceptions silently.
- Distinguish recoverable errors from programming errors.
- Convert infrastructure errors into domain-level results at boundaries.
- Log with enough context to debug without leaking secrets or player data.

## Tests

- Test domain logic without Unity scenes where possible.
- Mock interfaces, not concrete Unity components.
- Cover boundary values and edge cases from the design doc.
- Add regression tests for fixed bugs.

## Review Severity

- P1: correctness, security, data loss, crash, exploit, major performance risk.
- P2: broken architecture boundary, untestable core behavior, likely regression.
- P3: maintainability issue, naming, duplication, local complexity.
