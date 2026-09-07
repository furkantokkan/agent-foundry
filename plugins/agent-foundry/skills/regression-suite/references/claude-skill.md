---
name: regression-suite
description: "Map Unity EditMode/PlayMode regression coverage to acceptance criteria and fixed bugs, then report gaps without inventing execution evidence."
argument-hint: "[system | sprint | all] [--record]"
user-invocable: true
allowed-tools: Read Glob Grep Write
model: sonnet
---

# Unity Regression Suite

## Phase 1 — Collect Sources

Read relevant stories, acceptance criteria, completed bug reports, and test files
under `Assets/Tests/EditMode/**`, `Assets/Tests/PlayMode/**`, and documented
feature-local Unity test assemblies. Also read NUnit XML/results from the most
recent valid run when available.

## Phase 2 — Build Traceability

For every blocking criterion and fixed bug, identify the exact test type and
method that protects it. A similar filename is not sufficient; inspect the
assertion and scenario.

```text
| Priority | System | Test path and method | Covers | Last execution |
|---|---|---|---|---|
| HIGH | Combat | Assets/Tests/EditMode/Combat/DamageTests.cs::ZeroArmor_BaseDamage | BUG-123 | [XML/date] |
```

Classify gaps:

- HIGH: fixed production bug or critical acceptance criterion has no focused test.
- MEDIUM: behavior has only broad/indirect coverage.
- LOW: advisory/manual behavior lacks a documented walkthrough.

Suggest Unity paths such as
`Assets/Tests/EditMode/[System]/[BugName]RegressionTests.cs` or the appropriate
PlayMode assembly. Do not create tests in this read/report workflow.

## Phase 3 — Validate Boundaries

Flag runtime asmdefs that reference test/editor assemblies, tests coupled to
unrelated systems, nondeterministic timing/random/external I/O, and missing
failure-path assertions. State whether each mapped test was actually executed;
source inspection alone is `NOT RUN`.

## Phase 4 — Verdict

- `PASS`: all high-priority requirements/bugs have focused passing evidence.
- `CONCERNS`: only medium/low gaps remain.
- `FAIL`: any high-priority regression gap or known failing regression exists.
- `BLOCKED`: stories/bugs/tests cannot be mapped because required context is missing.

Without `--record`, return the report only. With `--record`, write/update
`production/qa/regression-suite.md`; this is the only approved mutation.

Recommended next step: create ready stories for HIGH gaps, then verify through
`/smoke-check` and `/test-evidence-review`.
