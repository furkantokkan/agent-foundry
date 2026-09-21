---
name: test-setup
description: "Scaffold and verify Unity Test Framework structure for this Unity 6.3 template: EditMode/PlayMode paths, asmdef boundaries, a focused smoke test, and CI guidance."
argument-hint: "[system-or-feature]"
user-invocable: true
allowed-tools: Read Glob Grep Write Edit Bash AskUserQuestion
model: sonnet
---

# Unity Test Setup

Configure tests around the repository's real Unity project structure. Never
create a parallel root `tests/` tree.

## Phase 1 — Inspect Before Planning

Read `CLAUDE.md`, `.claude/rules/unity-architecture.md`,
`.claude/rules/unity-automation.md`, `.claude/rules/unity-ownership.md`, and:

- `ProjectSettings/ProjectVersion.txt`
- `Packages/manifest.json` and `Packages/packages-lock.json`
- all relevant `Assets/**/*.asmdef`
- existing `Assets/Tests/**` and feature-local test assemblies
- the repository CI workflow, if present

Confirm whether Unity Test Framework is already installed and whether the
project uses central or feature-local tests. Preserve the established pattern.

## Phase 2 — Classify Risk and Present One Plan

- Low risk: focused tests inside an existing approved test assembly.
- Medium risk: a new `.asmdef`, new public test seam, or CI contract. Present
  the plan and obtain one approval before applying it.
- High risk: package manifest/lock changes, project settings, scenes, prefabs,
  or other serialized assets. Obtain explicit approval for the exact target.

The plan must list allowed paths, forbidden paths, expected assembly references,
and verification commands. After approval, do not ask once per file.

## Phase 3 — Create the Minimal Unity Structure

Use the project's convention. The default is:

```text
Assets/Tests/
  EditMode/[System]/
  PlayMode/[System]/
```

For new test assemblies:

- EditMode asmdefs use `optionalUnityReferences: ["TestAssemblies"]`, reference
  only the runtime assemblies under test, and include the Editor platform when
  appropriate.
- PlayMode asmdefs use the TestAssemblies reference and only the runtime
  dependencies required by the scenario.
- Runtime assemblies never reference test or Editor assemblies.
- Follow `m_camelCase`, `s_camelCase`, and `k_camelCase` naming.

Create one deterministic example test for the selected system. Use NUnit
`[Test]` for pure C# behavior and `[UnityTest]` only when a frame/lifecycle is
part of the requirement. Avoid external I/O, global random state, and timing
assertions.

If Unity Test Framework is missing, stop and propose the exact package change;
do not edit package files without high-risk approval.

## Phase 4 — Verify in Unity

Follow `.claude/rules/unity-automation.md`:

1. Use the installed Unity CLI as the mandatory control plane and prove the
   target with `unity status --json` plus exact `--project-path`.
2. If it is missing, install the official CLI under the standing authorization
   before continuing.
3. Use built-in `unity mcp` when MCP protocol is needed. Legacy MCP and
   UnitySkills require an explicit user request. If requested, prove the exact
   repository separately; otherwise use pinned file evidence as the final
   fallback.

Require compilation to succeed, then run the affected EditMode and/or PlayMode
tests. Preserve editor logs and NUnit XML. Do not report PASS from source
inspection alone.

## Phase 5 — CI Guidance

If CI does not run Unity tests, propose a medium-risk workflow change that:

- uses the pinned Unity version;
- runs EditMode and PlayMode separately;
- uploads XML and editor logs;
- fails on compilation or test failures;
- caches only safe Unity/package artifacts and never commits `Library/`.

Do not assume a Unity license secret name; follow the repository's provider and
secret-storage convention.

## Phase 6 — Result

Report:

- files changed;
- asmdef references added/removed;
- compilation result;
- EditMode/PlayMode counts and XML/log paths;
- approved paths and forbidden-path violations;
- package/project/serialized changes, normally none;
- residual blockers.

Verdict: `PASS`, `CONCERNS`, `FAIL`, or `BLOCKED`.

Recommended next step: run `/qa-plan sprint`, then `/dev-story` with the focused
test path embedded in each story.
