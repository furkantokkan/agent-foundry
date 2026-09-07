---
name: firebase-game-backend
description: Use when building or reviewing Firebase-backed game features for Unity or JavaScript, including Firebase Auth, Cloud Firestore, Realtime Database, Cloud Functions Gen2, Express.js HTTP APIs, Unity request/response clients, Cloud Storage, Remote Config, Analytics, App Check, security rules, local emulators, deployment, data modeling, and client/server boundaries.
---

# Firebase Game Backend

Use this skill for Firebase features that support a Unity game, web dashboard,
companion app, or JavaScript service.

## First Read

Inspect whichever files exist:

- `firebase.json`
- `.firebaserc`
- `firestore.rules`
- `firestore.indexes.json`
- `storage.rules`
- `functions/package.json`
- `functions/src/` or `functions/index.js`
- Web app Firebase config files
- Unity Firebase wrapper code under `Assets/`

## Core Rules

- Client SDKs are untrusted. Security rules and Cloud Functions enforce policy.
- Do not put privileged operations in Unity or browser code.
- Keep Firestore rules restrictive by default.
- Rules are not filters: queries must match the rule constraints.
- Use Firebase Auth UID as the primary ownership boundary.
- Validate writes in security rules and again in trusted server code.
- Use Cloud Functions or another trusted backend for economy mutations,
  anti-cheat-sensitive rewards, purchases, inventory grants, and leaderboards.
- Use Firebase Emulator Suite for rules and function testing when available.
- Keep Firebase code behind interfaces in Unity.
- For this game backend style, prefer Firebase Functions Gen2 with JavaScript
  and Express.js HTTP routes. Unity should call those routes through typed
  request/response client wrappers, not by scattering raw HTTP calls through
  gameplay code.
- New or changed game API behavior needs focused unit tests for the expected
  success path and important failure paths. Emulator/Newman coverage complements
  handler unit tests; it does not replace them.

## Workflow

1. Identify the feature: auth, save, leaderboard, inventory, economy, matchmaking,
   remote config, analytics, storage, or admin tooling.
2. Decide which operations are safe on the client and which require trusted code.
3. Check data model, indexes, rules, and Cloud Functions together.
4. Add unit tests for expected behavior when changing routes, authorization,
   validation, response contracts, or write behavior.
5. For Unity, expose Firebase through game-facing interfaces.
6. For JavaScript, use the modular Web SDK for browser code and Admin SDK only
   in trusted server environments.
7. For Functions HTTP APIs, keep Express routing, request validation, auth/App
   Check guards, response envelopes, and Unity DTO alignment together.

## Reference Loading

- Data modeling and products: `references/firebase-stack.md`
- Functions Gen2 + Express + Unity request/response:
  `references/functions-express-unity.md`
- Security rules: `references/security-rules.md`
- Unity integration: `references/unity-firebase.md`

Official docs to verify current setup details:

- Unity SDK: https://firebase.google.com/docs/unity/setup
- Web SDK: https://firebase.google.com/docs/web/setup
- Security Rules: https://firebase.google.com/docs/rules/
- Firestore Rules: https://firebase.google.com/docs/firestore/security/get-started
