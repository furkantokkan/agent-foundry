---
name: adaptive-skills
description: Use when a task may span multiple personal skills and Codex should choose the smallest relevant skill set across Unity, Unity performance, Clean OOP, Firebase backend, JavaScript tooling, game design/UX, tracked task lifecycle, Steam launch, code review, and web/SaaS work.
---

# Adaptive Skills

Use this skill when the best skill choice is not obvious or the task crosses
multiple game-development domains.

## Selection Rules

Choose the smallest relevant skill set:

- Unity implementation, debugging, refactoring, setup, or tests:
  use `unity-game-dev`.
- Unity profiling, optimization, CPU/GPU/GC bottlenecks, hot paths, UI/physics/
  rendering/loading/memory performance, or mobile thermal/battery constraints:
  use `unity-optimization`.
- SOLID, Clean Code, naming, dependency boundaries, DI, ServiceLocator, Onity,
  or testability: use `clean-oop-architecture`.
- Firebase Auth, Firestore, Realtime Database, Functions Gen2, Express.js game
  APIs, App Check, rules, emulators, or Unity request/response clients: use
  `firebase-game-backend`.
- JavaScript/TypeScript tooling, Node scripts, Cloud Functions, dashboards,
  packages, linting, tests, or browser tooling: use `javascript-game-tools`.
- Code or architecture review: use `game-code-review`.
- Game design, GDDs, systems, core loops, economy, pacing, UX, or acceptance
  criteria: use `game-design-studio`.
- Steam Coming Soon/store page, wishlist campaign, press/creator CRM, festival
  planning, Steam Next Fest, announcement posts, or indie launch marketing:
  use `steam-store-launch`.
- Read-only readiness check before Unity Editor work: use `unity-preflight`.
- Full system GDD authoring: use `design-system`; small tuning/mechanic specs:
  use `quick-design`; GDD validation: use `design-review`.
- Screens, HUD, flows, onboarding, feedback, accessibility: use `ux-design` or
  `ux-review`.
- Game feel, juice, impact feedback, screen shake, hitstop, punch tweens, hit
  flash, damage numbers, toasts, SFX banks, or CRT screen looks for a menu,
  HUD, or hit: use `game-feel-polish`. For Liquid UI-style Unity widgets,
  follow its Unity system and UI Toolkit references; Godot excerpts are source
  references, not the Unity implementation route.
- Tracked task lifecycle: use `create-task`, `implement-task`, `task-status`,
  `task-bug`, `task-cycle`, `task-done`, or `daily-handoff`; several ready
  tasks: use `game-studio-orchestration`.
- Web/SaaS work: use the installed web stack (React/Next.js, NestJS/ASP.NET
  Core, Supabase, shadcn/Radix, Playwright/webapp-testing, security,
  Vercel/Render deploy) as indexed in the global instructions.

This list is a common-route summary, not the authority. The Personal Skill
Index in the global `AGENTS.md`/`CLAUDE.md` owns the full domain map: when the
task matches an installed skill not listed above, route to that skill instead
of declaring that no skill applies.

Combine skills only when the request actually spans domains. Do not force a
skill when repository instructions and global rules are enough.

## Baseline Defaults

- Follow repository-local instructions first.
- Apply SOLID, Clean Code, testability, clear English naming, and simple method
  verbs by default.
- Keep Unity MonoBehaviours thin and domain logic testable.
- Use an existing ServiceLocator before adding dependencies; otherwise prefer
  Onity for new Unity DI/reactive/events work.
- Add focused unit tests for new or changed expected behavior.
- For Firebase game APIs, prefer Functions Gen2 with JavaScript and Express.js
  routes plus typed Unity request/response DTOs.
- For Unity tasks that need extra pattern, performance, UI/widget, testing,
  handoff, or refactoring context, start from the local PDF-derived index:
  `optional local reference library (not included; skip if unavailable)`.
  Search it with `rg` and load only relevant sections.
