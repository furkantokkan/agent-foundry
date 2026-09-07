---
name: test-flakiness
description: "Detect nondeterministic Unity EditMode/PlayMode tests from comparable NUnit XML history, classify likely causes, and maintain an evidence-backed quarantine registry."
argument-hint: "[results-path | scan | registry] [--record]"
user-invocable: true
allowed-tools: Read Glob Grep Write
model: sonnet
---

# Unity Test Flakiness Detection

This workflow is evidence review. It never changes production code, test code,
assembly definitions, scenes, prefabs, packages, or project settings.

## Phase 1 — Resolve Comparable Runs

Accept one of:

- `/test-flakiness [results-path]` — inspect a directory or manifest of NUnit XML.
- `/test-flakiness scan` — discover recorded Unity test results under
  `production/qa/test-results/`, CI artifact manifests, and documented
  feature-local evidence paths.
- `/test-flakiness registry` — review the existing quarantine table in
  `production/qa/regression-suite.md`.

For every run, record commit SHA, Unity version, package-lock hash, platform,
EditMode/PlayMode target, seed when exposed, and result-file timestamp. Runs are
comparable only when code and dependency state match. Do not combine unrelated
commits to manufacture a flaky classification.

At least three comparable runs are required for `CONFIRMED FLAKY`; five or more
are preferred. With fewer than three, report `INSUFFICIENT EVIDENCE`.

## Phase 2 — Parse Objective Evidence

Parse Unity Test Framework NUnit XML and retain the raw artifact path. Build:

```text
test full name -> run ID -> PASS | FAIL | SKIPPED | INCONCLUSIVE | MISSING
```

A console summary, agent statement, or test file existing on disk is not an
execution result. Treat malformed/incomplete XML as a runner failure, not a test
failure. Separate EditMode and PlayMode runs.

## Phase 3 — Detect and Classify

A test is `CONFIRMED FLAKY` only when it both passes and fails across comparable
runs without a semantic code/dependency change. Otherwise classify it as
`CONSISTENT FAILURE`, `CONSISTENT PASS`, `SUSPECTED`, or `BLOCKED`.

Inspect the exact test and fixture code for common Unity causes:

| Cause | Evidence to inspect | Fix direction |
|---|---|---|
| Async/frame timing | fixed delays, unawaited task/coroutine, arbitrary frame counts | wait on observable state with a bounded timeout |
| Static/domain state | static fields, disabled domain reload, singleton leakage | reset state explicitly in setup/teardown |
| Object/scene cleanup | leaked GameObjects, scenes, subscriptions, temp assets | deterministic teardown and disposal |
| Order dependency | passes alone, fails after a named test | isolate fixture state and remove shared mutation |
| Randomness | unrecorded `UnityEngine.Random` or custom RNG seed | inject and record a deterministic seed |
| Time/physics | `Time.timeScale`, fixed-step assumptions, uncontrolled simulation | own and restore time/physics state |
| External/editor state | network, filesystem, selection, active scene, global settings | replace with controlled boundary or fixture |
| Float comparison | exact equality on computed floats | use a justified tolerance |

Do not diagnose from filename alone. Cite exact methods/lines or mark the cause
`UNKNOWN`.

## Phase 4 — Decide Action

- Critical-path or release-gate tests: fix immediately; quarantine requires an
  explicit owner, bug/story ID, reason, expiry/review date, and release impact.
- Confirmed flaky non-critical tests: create a focused bug/story and consider a
  temporary quarantine only with the same ownership fields.
- Suspected tests: collect more comparable runs; do not quarantine yet.
- Consistent failures: route as normal defects, not flakiness.

This skill does not add `[Ignore]` or edit the test. Route implementation to
`unity-bugfixer`, then rerun verification with `unity-test-verifier`.

## Phase 5 — Report and Verdict

```text
| Test | Mode | Comparable runs | Fail rate | Classification | Cause | Action |
|---|---|---:|---:|---|---|---|
```

- `PASS`: no confirmed/suspected flaky tests and evidence is sufficient.
- `CONCERNS`: suspected flakiness or limited-but-usable evidence remains.
- `FAIL`: confirmed flakiness affects a blocking test or quarantine lacks owner/expiry.
- `BLOCKED`: no parseable evidence or fewer than three comparable runs for the
  requested confirmation.

Without `--record`, return the report only. With `--record`, the invocation may
write `production/qa/flakiness-report-[date].md` and update only the quarantine
table in `production/qa/regression-suite.md`. Those documentation writes are the
complete low-risk scope; all source/test/serialized paths remain forbidden.

Next step: assign each confirmed item to `unity-bugfixer`, then require a fresh
multi-run result set from `unity-test-verifier` before removing quarantine.
