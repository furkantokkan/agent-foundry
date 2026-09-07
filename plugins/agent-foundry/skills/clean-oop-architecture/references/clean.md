# Clean Code And Refactoring Index

This is the main clean-code routing file for the `clean-oop-architecture`
skill. Search and load the specific reference needed for the task.

## Core References

- `solid-oop.md`: SOLID and OOP responsibility boundaries.
- `clean-code-review.md`: clean-code review checklist.
- `refactoring-smells.md`: code smells and targeted refactoring moves.
- `llm-coding-guidelines.md`: guardrails against hidden assumptions,
  overengineering, drive-by edits, and weak verification.
- `llm-coding-examples.md`: concrete before/after examples for those failure
  modes.
- `unity-oop.md`: Unity-specific OOP boundaries, MonoBehaviour adapters,
  ScriptableObject config, and testable domain logic.

## External Local PDF Context

- `optional local reference library (not included; skip if unavailable)`
  for refactoring concepts and code-smell vocabulary.
- `optional local reference library (not included; skip if unavailable)`
  for pattern selection and game-pattern routing.

## Use Rules

- Keep changes surgical and scoped to the task.
- Prefer simple code over speculative abstraction.
- Add an abstraction only when it removes real duplication, clarifies a stable
  boundary, or improves testability.
- For bug fixes, reproduce or precisely characterize behavior before changing
  code when practical.
