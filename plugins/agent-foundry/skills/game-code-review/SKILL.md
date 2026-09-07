---
name: game-code-review
description: Use when reviewing game code or architecture, especially Unity C#, Firebase rules/functions, JavaScript/TypeScript tooling, gameplay systems, UI code, async code, dependency injection, tests, performance hot paths, and security-sensitive backend code.
---

# Game Code Review

This workflow is read-only: do not edit code, tests, assets, packages,
settings, reports, lifecycle state, or git state. Add `unity-game-dev`,
`firebase-game-backend`, `javascript-game-tools`, or
`clean-oop-architecture` as read-only domain context when relevant.

## Phase 1 — Resolve scope and one review point

Read repository instructions, nearest path-scoped rules, the requested
files/diff, mapped task acceptance and defect ledger, relevant ADRs/design docs,
and affected tests. If no concrete scope is supplied, review the current
user-provided changeset; do not silently expand to the entire repository.

Record one fixed review point: base revision, head/reviewed revision, dirty
fingerprint, and exact paths. Findings and evidence claims apply only to that
point; later changes make the review stale. When parallel read-only sub-agents
materially help, give them disjoint review axes against the same fixed point and
merge findings only after all return. Never let a review agent edit or review a
moving diff.

For Unity code, verify `Assets/**`, `Packages/**`, `ProjectSettings/**`, asmdef,
and EditMode/PlayMode boundaries as applicable. Existing ServiceLocator/Onity
composition and repository naming are canonical unless a stricter local rule
exists. Do not introduce a competing DI/reactive/event stack through review
advice.

## Phase 2 — Review four independent axes

A pass on one axis does not substitute for another:

1. **Contract/spec compliance** — acceptance, preserved behavior, non-goals,
   ownership, current defect IDs, and declared evidence.
2. **Project standards/architecture** — repository rules, boundaries, naming,
   dependency direction, API contracts, and security policy.
3. **Unity integration and runtime risk** — serialization, lifecycle, async
   cancellation, hot-path allocations, DI/package ownership, Editor/runtime
   seams, and serialized-asset single-writer containment.
4. **Verification and regression evidence** — focused tests, original repro,
   NUnit/build artifacts, revision freshness, negative cases, and required
   manual/real-scene/device/profiler checks.

Return findings first, ordered by severity. Prioritize concrete bugs, security,
regressions, missing evidence, maintainability, and performance hot paths.
For Firebase also check auth/App Check/rules/stable error codes/idempotency. For
JavaScript/TypeScript check validation, secrets, external-data types, and
observable failure-path tests.

Every actionable finding must cite an exact file and line when available,
explain the concrete failure/risk, and state the smallest safe correction.
Distinguish test source from executed NUnit XML; absence of execution evidence
is not a passing test. Do not invent findings to fill a template.

## Phase 3 — Verdict and lifecycle handoff

Use `NEEDS CHANGES` for blocking correctness/security/regression issues,
`CONCERNS` for non-blocking risks, and `APPROVED` only when no actionable
findings remain. If scope or context is missing, return `BLOCKED`.

The reviewer never applies a fix. Route concrete fixes to the owning
implementer/bugfixer, then independent verification, and review the resulting
fixed revision again.

When a finding belongs to a tracked task's acceptance, preserved behavior, or
task-caused regression, hand off its task ID, atomic observation, repro, line
evidence, and reviewed revision to `$task-bug <ID> "<feedback>"`. Do not file
a second task or standalone QA bug. `task-bug` dispatches and `task-cycle`
alone owns linked records, defect dedupe, and lifecycle state. Only a genuinely
separate player-facing outcome uses
`NEW_TASK_REQUIRED`.

Report findings, open questions, summary, commands/evidence actually inspected,
and residual risk. If no finding exists, state that clearly without upgrading
missing runtime evidence to a pass.
