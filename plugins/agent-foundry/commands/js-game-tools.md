---
description: Work on JavaScript or TypeScript game tooling and Firebase code.
argument-hint: [javascript-task]
---

# JavaScript Game Tools

The user invoked this command with: $ARGUMENTS

Use `javascript-game-tools`. Add `firebase-game-backend` for Firebase Functions,
rules, or Unity API contracts. Add `game-code-review` if this is a review.

Follow these defaults:

- Use the existing package manager and module style.
- Prefer TypeScript for production tooling when the repo already supports it.
- Use Firebase modular Web SDK in browser code and Admin SDK only in trusted
  server code.
- Validate API/function inputs at boundaries.
- Return stable error codes that Unity or web clients can handle.
- Use the existing test runner first: `npm test`, `node --test`, Vitest, Jest,
  or the package manager equivalent.
- Add unit tests for observable expected behavior and important failure paths.

Proceed with the JavaScript/TypeScript task.
