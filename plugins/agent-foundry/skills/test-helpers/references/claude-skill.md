---
name: test-helpers
description: "Create minimal reusable Unity Test Framework helpers for repeated EditMode/PlayMode setup while preserving asmdef boundaries and deterministic cleanup."
argument-hint: "[system-or-repeated-test-pattern]"
user-invocable: true
allowed-tools: Read Glob Grep Write Edit Bash AskUserQuestion
model: sonnet
---

# Unity Test Helpers

Helpers reduce repeated test setup; they must not become a second framework or
hide the behavior under test.

## Phase 1 — Inspect Repetition

Read repository rules, relevant runtime/test `.asmdef` files, and tests under
`Assets/Tests/EditMode/**`, `Assets/Tests/PlayMode/**`, plus feature-local test
assemblies. Identify at least two concrete repetitions. If only one test needs
the code, keep it local and return `CONCERNS` rather than creating abstraction.

## Phase 2 — Select the Smallest Helper

Allowed helper types include:

- pure C# builders with explicit defaults and fluent overrides;
- fake/test-double implementations of existing interfaces;
- GameObject/component factories whose ownership is explicit;
- deterministic cleanup scopes or NUnit setup/teardown utilities;
- assertion helpers for a domain concept when they improve failure messages.

Do not add a generic base test class, service-locator reset that mutates global
production state, reflection access to private members, scene-wide searches,
wall-clock waits, random data without a fixed local seed, or external I/O.

## Phase 3 — Plan Scope and Risk

Default path: `Assets/Tests/Shared/` or the owning feature's existing test
assembly. Present one plan listing:

- exact helper and call sites;
- allowed/forbidden paths;
- asmdef references;
- cleanup/lifetime behavior;
- tests that prove the helper itself where non-trivial.

Adding code to an existing approved test assembly is low risk. A new test
assembly or public runtime seam is medium risk and needs plan approval. Package,
project-setting, scene, prefab, or ScriptableObject changes are high risk and
outside this skill unless explicitly approved.

## Phase 4 — Implement

After the plan is approved, write all low-risk helper/call-site changes without
per-file prompts. Follow canonical `m_camelCase`, `s_camelCase`, and
`k_camelCase` naming. Keep helpers internal unless cross-assembly use requires a
reviewed contract.

For Unity objects, track every object created by the helper and destroy it in
the appropriate teardown. Keep EditMode and PlayMode lifecycle assumptions
separate. Never edit Unity YAML manually.

## Phase 5 — Verify

Use the installed Unity CLI as the mandatory control plane with exact
`unity status --json` identity. Install it when missing. Use built-in
`unity mcp` when needed, then pinned file evidence. Legacy MCP and UnitySkills
require an explicit user request. Use exactly one mutation path.
Require:

- compilation success;
- affected EditMode/PlayMode tests passing with XML/log evidence;
- no runtime-to-test/editor asmdef reference;
- no unexpected serialized/project/package diff;
- `git diff --check` and allowed-path containment.

## Phase 6 — Result

Report repeated code removed, helper API, changed paths, assembly references,
test counts/results, cleanup guarantees, and residual risks.

Verdict: `PASS`, `CONCERNS`, `FAIL`, or `BLOCKED`.

Recommended next step: run `/regression-suite [system]` to confirm the helper
improves coverage without obscuring requirement traceability.
