---
name: javascript-game-tools
description: Use when building JavaScript or TypeScript tooling around a game project, including Firebase web apps, admin dashboards, build tools, data editors, content pipelines, Node scripts, Cloud Functions, React/Vite/Next frontends, package setup, linting, tests, and browser tooling.
---

# JavaScript Game Tools

Use this skill for web tooling, dashboards, Firebase web clients, Node scripts,
Cloud Functions, editor utilities, and TypeScript refactors around the game.

## First Read

Inspect:

- `package.json`
- lockfile (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, or `bun.lockb`)
- `tsconfig.json`
- `vite.config.*`, `next.config.*`, or other build config
- `src/`
- `functions/` if Firebase Functions are involved
- `.env.example` and config docs, but never print secrets

## Core Rules

- Prefer TypeScript for production tooling.
- Use the existing package manager and module style.
- Use Firebase modular Web SDK in browser code.
- Use Firebase Admin SDK only in trusted server code.
- For Firebase Functions game APIs in this workspace, prefer JavaScript Gen2
  Functions with Express.js route registration unless the target project already
  uses another explicit pattern.
- Keep environment-specific config outside source.
- Validate input at boundaries with the project's existing schema library if
  present; otherwise choose a small, explicit validator only when needed.
- Do not introduce a framework or state library for a small script.
- Add tests for data transforms, rules-sensitive code, and Cloud Functions.

## Workflow

1. Identify whether the target is browser, Node, Cloud Functions, or static tooling.
2. Read existing scripts and package conventions.
3. Make the smallest compatible change.
4. Run available checks: typecheck, lint, unit tests, build.
5. If checks cannot run, explain the missing dependency or command.

## Reference Loading

- JavaScript/TypeScript patterns: `references/javascript-patterns.md`
- Firebase web/client boundaries: use `firebase-game-backend`
