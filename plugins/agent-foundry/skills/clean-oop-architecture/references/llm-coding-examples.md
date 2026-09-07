# LLM Coding Examples

Use these examples as pattern reminders. Do not copy the code literally unless
the target project matches the example.

## Think Before Coding

### Hidden Assumptions

Request: "Add a feature to export user data."

Wrong response pattern:

- Exports all users without asking about scope or privacy.
- Assumes output format, file location, and fields.
- Ignores expected volume and security implications.

Better response pattern:

- Ask whether the export is all users or a filtered subset.
- Clarify whether this is an API response, browser download, background job, or
  admin tool.
- Ask which fields are allowed.
- Ask about volume and privacy constraints before choosing the implementation.

### Multiple Interpretations

Request: "Make search faster."

Wrong response pattern:

- Adds caching, async processing, and indexes without knowing which performance
  problem matters.

Better response pattern:

- Distinguish response time, throughput, and perceived UX speed.
- Measure or inspect current behavior.
- Pick the smallest change for the actual bottleneck.

## Simplicity First

### Over-Abstraction

Request: "Add a function to calculate discount."

Wrong response pattern:

- Adds strategies, factories, config classes, and multiple discount types before
  there is a real variant.

Better response pattern:

```python
def calculate_discount(amount: float, percent: float) -> float:
    return amount * (percent / 100)
```

Add more structure only when multiple discount types are actually required.

### Speculative Features

Request: "Save user preferences to database."

Wrong response pattern:

- Adds cache, validator, merge modes, notifications, and optional flags before
  those behaviors are requested.

Better response pattern:

- Save the provided preferences through the existing persistence pattern.
- Add validation, merge behavior, or notifications only when a requirement or
  failing test demands it.

## Surgical Changes

### Drive-By Refactoring

Request: "Fix the bug where empty emails crash the validator."

Wrong response pattern:

- Rewrites unrelated username validation.
- Changes comments and docstrings.
- Expands email validation beyond the reported bug.

Better response pattern:

- Only normalize/check the email value enough to fix empty-email handling.
- Leave unrelated validation unchanged.
- Add the smallest test that reproduces the crash.

### Style Drift

Request: "Add logging to the upload function."

Wrong response pattern:

- Adds type hints and docstrings in a file that does not use them.
- Changes quote style and control flow while adding logging.

Better response pattern:

- Add logging using the file's current quote style, structure, and return
  pattern.
- Avoid changing unrelated formatting.

## Goal-Driven Execution

### Vague Task

Request: "Fix authentication."

Wrong response pattern:

- "I'll review and improve auth" followed by broad edits.

Better response pattern:

- Ask which auth failure is being fixed.
- Convert it into a reproducible test or scenario.
- Make that check pass, then run existing auth tests.

### Multi-Step Work

Request: "Add rate limiting to the API."

Better response pattern:

1. Add the smallest rate-limit behavior for one endpoint.
   Verify: limit exceeded returns the expected status.
2. Extract/apply it through the existing middleware pattern.
   Verify: affected endpoint tests pass.
3. Add distributed storage only when multi-instance deployment requires it.
   Verify: behavior is shared across instances.

The key is timing: patterns are useful when the problem needs them, not before.
