---
name: clean-oop-architecture
description: Use when designing, implementing, refactoring, or reviewing object-oriented code with SOLID, Clean Code, design patterns, dependency injection, ServiceLocator, Onity, testability, code smells, naming, class/function boundaries, Unity C# architecture, maintainability concerns, hidden assumptions, overengineering, surgical-change discipline, or goal-driven verification.
---

# Clean OOP Architecture

Use this skill for code quality decisions that go beyond syntax: boundaries,
responsibilities, coupling, cohesion, naming, refactoring, and testability.

## Core Principle

Prefer code that is easy to change safely:

- One clear reason to change per class or module.
- Behavior grouped by responsibility, not by convenience.
- Dependencies point inward toward stable abstractions.
- Domain logic is testable without Unity scenes, Firebase, network, or UI.
- Framework code adapts the domain; it does not become the domain.

## First Read

Before changing code, inspect:

1. Existing project conventions.
2. The target class/module and direct collaborators.
3. Tests around the behavior.
4. Composition root / dependency injection setup if present.
5. Any ADR, design doc, or task file that names the pattern.

## SOLID Checks

- **SRP**: Does this class have one reason to change?
- **OCP**: Can likely variants be added without editing core logic?
- **LSP**: Can subclasses/implementations replace the base contract safely?
- **ISP**: Are interfaces small and role-specific?
- **DIP**: Does high-level policy depend on abstractions, not concrete services?

Do not force patterns mechanically. A small direct implementation is better than
an abstraction that hides nothing and makes testing harder.

## Clean Code Checks

- Names reveal intent and domain meaning.
- Functions are short enough to understand and test.
- Arguments are few and cohesive.
- Boolean flags do not hide multiple behaviors.
- Errors are explicit and handled at the right layer.
- Comments explain why, not what obvious code does.
- Duplication is removed when it represents the same concept, not merely the
  same shape.

## Refactoring Workflow

1. Characterize current behavior with tests or a precise reading.
2. Identify the code smell and the reason it matters.
3. Make one small structural change at a time.
4. Preserve behavior unless the user asked for a behavior change.
5. Run tests after meaningful steps.
6. Stop before broad rewrites that are not needed for the current goal.

## Reference Loading

Load only the relevant reference:

- `references/clean.md` as the first index for Clean Code, SOLID, refactoring,
  LLM coding discipline, Unity OOP, Dive Into Refactoring, and design-pattern
  routing.
- `references/solid-oop.md` for SOLID and OOP heuristics.
- `references/clean-code-review.md` for review checklists.
- `references/refactoring-smells.md` for smell-to-refactor mapping.
- `references/unity-oop.md` for Unity-specific architecture.
- `references/llm-coding-guidelines.md` when starting non-trivial
  implementation, bug fixing, refactoring, or review work that risks hidden
  assumptions, overengineering, drive-by edits, or weak verification.
- `references/llm-coding-examples.md` when the task shows one of those failure
  modes and concrete before/after examples would help steer the implementation.
- `optional local reference library (not included; skip if unavailable)` when a
  Unity task needs extra local PDF-derived context on game programming patterns,
  refactoring discipline, performance, testing, or handoff workflow. Search with
  `rg` and load only the relevant extracted Markdown sections.

If the local project contains
`docs/reference/private/coding/README.md`, read that index and grep targeted
terms only. Do not bulk-load full books.
