---
description: Review game code, architecture, tests, security, and hot paths.
argument-hint: [review-scope]
---

# Game Code Review

The user invoked this command with: $ARGUMENTS

Use `game-code-review`. Add `unity-game-dev`, `firebase-game-backend`,
`javascript-game-tools`, or `clean-oop-architecture` when the reviewed code
touches those domains.

Review stance:

- Findings first, ordered by severity.
- Prioritize bugs, security, regressions, missing tests, maintainability, and
  performance hot paths.
- Check Unity hot-path allocations, lifecycle, async cancellation, DI, and
  package usage.
- Check Firebase auth, App Check, rules, stable error codes, idempotency, and
  server/client boundaries.
- Check that expected behavior has focused unit tests for success and failure
  paths.

Proceed with the review.
