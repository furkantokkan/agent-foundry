---
description: Build or review Firebase Functions game APIs for Unity clients.
argument-hint: [firebase-api-task]
---

# Firebase Game API

The user invoked this command with: $ARGUMENTS

Use `firebase-game-backend`. Also use `javascript-game-tools` for Functions,
Node, Express.js, package, lint, and test work. Use `unity-game-dev` when Unity
request/response client code is part of the task.

Follow these defaults:

- Prefer Firebase Functions Gen2 with JavaScript and Express.js HTTP routes
  unless the repo has a stricter pattern.
- Keep Unity calls behind typed request/response API clients and DTOs.
- Do not put privileged economy, inventory, purchase, reward, leaderboard, or
  anti-cheat-sensitive mutations in Unity/browser clients.
- Keep auth, App Check, validation, response envelopes, stable error codes, and
  DTO compatibility together.
- Add focused handler unit tests for success and failure paths. Emulator/Newman
  tests are integration coverage, not a replacement.
- Add Unity EditMode tests for DTO parsing and `ApiCode`/result mapping when
  contracts change.

Proceed with the Firebase game API task.
