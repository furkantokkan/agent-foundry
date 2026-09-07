---
description: Use the smallest relevant personal skill set for a game-dev task.
argument-hint: [task]
---

# Adaptive Personal Skills

The user invoked this command with: $ARGUMENTS

Use skills adaptively for the requested task:

1. Read local repository instructions first: `AGENTS.md`, `CLAUDE.md`, the
   nearest path-scoped instructions (`Assets/CLAUDE.md` in Unity projects when
   present), and relevant docs.
2. Choose the smallest relevant skill set. Combine skills only when the request
   crosses domains.
3. Prefer these mappings:
   - Unity work: `unity-game-dev`
   - SOLID, Clean Code, OOP, DI, naming, architecture: `clean-oop-architecture`
   - Firebase game backend, Functions, rules, Unity API clients:
     `firebase-game-backend`
   - JavaScript/TypeScript tooling, Node scripts, dashboards:
     `javascript-game-tools`
   - Review work: `game-code-review`
   - Game design, systems, GDDs, economy, pacing: `game-design-studio`
4. Apply SOLID, Clean Code, clear English naming, focused unit tests for expected
   behavior, Unity naming conventions, and the existing ServiceLocator/DI
   preference rules.
5. If no skill is needed, say so briefly and follow the repository and global
   instructions.

Proceed with the user's task.
