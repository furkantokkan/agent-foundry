---
name: test-evidence-review
description: "Review Unity acceptance-criterion evidence using actual EditMode/PlayMode results, manual artifacts, and assembly boundaries."
argument-hint: "[story | sprint | release] [--record]"
user-invocable: true
allowed-tools: Read Glob Grep Write
model: sonnet
---

# Unity Test Evidence Review

## Phase 1 — Resolve Requirements

Read the selected stories verbatim. Extract type, acceptance criteria, required
test path, manual evidence, risk tier, and ownership contract.

## Phase 2 — Locate Evidence

- Logic: `Assets/Tests/EditMode/**` or a feature-local EditMode assembly plus
  matching NUnit XML.
- Integration/lifecycle: `Assets/Tests/PlayMode/**` or a justified EditMode
  integration test plus matching XML.
- UI/Visual/Feel: interaction test or dated manual evidence under
  `production/qa/evidence/`.

Inspect test assertions. A file path, an unchecked test, or an agent summary is
not proof of execution.

## Phase 3 — Review Quality and Boundaries

Check success and important failure paths, deterministic behavior, runtime/test
asmdef direction, forbidden-path changes, and serialized-asset ownership. Map
each criterion to one exact test method or manual evidence item.

## Phase 4 — Report

```text
| Criterion | Evidence | Executed | Result | Gap |
|---|---|---|---|---|
| AC-1 | Assets/Tests/EditMode/...::Method + results.xml | yes | PASS | — |
```

Verdict: `PASS`, `CONCERNS`, `FAIL`, or `BLOCKED`. A missing/failing blocking
Logic or Integration result is `FAIL`.

Without `--record`, return the report only. With `--record`, write one review
under `production/qa/`; do not change tests or production code.

Recommended next step: route concrete gaps to `/create-stories` or close verified
work with `/story-done`.
