# JavaScript And TypeScript Patterns

## Project Detection

- Vite: `vite.config.*`
- Next.js: `next.config.*`
- Firebase Functions: `functions/package.json`
- Node scripts: `scripts/`, `tools/`, or package scripts
- ESM: `"type": "module"` or `.mjs`
- CommonJS: `.cjs` or older Node configs

Follow the detected style.

## Browser Firebase

Use modular imports:

```ts
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
```

Do not use Admin SDK in browser code.

## Node / Functions

- Keep secrets in environment config, Secret Manager, or Firebase config,
  depending on the deployed environment.
- Validate callable/HTTP inputs.
- Check auth context before trusted mutations.
- Return stable error codes that Unity/web clients can handle.

## Tests

- Use the project's existing runner first: `npm test`, `node --test`, Vitest,
  Jest, or the package manager's equivalent.
- New or changed behavior should include focused unit tests for the expected
  success path and important failure paths.
- For Cloud Functions handlers, test method guards, auth/App Check guards,
  schema validation, stable response envelopes, error codes, and mutation
  effects.
- Mock Firebase Admin, Firestore, Auth, App Check, and clock/random/id services
  at the boundary where possible. Use emulator tests for integration behavior;
  do not rely on them as the only coverage for business logic.
- Prefer behavior assertions over implementation details. A route test should
  prove what the Unity or web client observes.

## Quality

- Prefer explicit async functions over nested promise chains.
- Avoid broad `any`; define DTOs for Firebase documents and API payloads.
- Keep data conversion at boundaries:
  - Firestore document -> DTO
  - DTO -> domain model
  - domain model -> view model
- Keep generated files out of hand-written source unless the project already
  uses generation.

## Commands

Use existing scripts first:

```bash
npm run typecheck
npm run lint
npm test
npm run build
```

If the project uses pnpm, yarn, or bun, use that package manager consistently.
