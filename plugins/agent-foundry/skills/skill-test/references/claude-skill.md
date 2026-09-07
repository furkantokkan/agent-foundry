---
name: skill-test
description: "Validate skill files with structural checks, instruction-level specs, category rubrics, and externally orchestrated Unity fixture evaluations. Static/spec results never substitute for compile and test evidence."
argument-hint: "static [skill-name | all] | spec [skill-name] [--record] | category [skill-name | all] [--record] | unity-eval [target-name] --fixture [path] --task [id] [--record] | audit"
user-invocable: true
allowed-tools: Read Glob Grep Write Bash Agent
model: sonnet
---

# Skill Test

Validates `.claude/skills/*/SKILL.md` files at two distinct evidence levels:
instruction conformance and executed Unity behavior. Never describe a static,
spec, or category result as proof that generated code compiles or works.

**Five modes:**

| Mode | Command | Purpose | Token Cost |
|------|---------|---------|------------|
| `static` | `/skill-test static [name\|all]` | Structural linter — 10 compliance checks per skill | Low (~1k/skill) |
| `spec` | `/skill-test spec [target]` | Skill or agent instruction-conformance reasoning; no code is executed | Medium (~5k/target) |
| `category` | `/skill-test category [name\|all] [--record]` | Category rubric — checks skill against its category-specific metrics | Low (~2k/skill) |
| `unity-eval` | `/skill-test unity-eval [target] --fixture [path] --task [id]` | Orchestrates a golden task in an externally provisioned Unity fixture and collects objective evidence | High; measured per run |
| `audit` | `/skill-test audit` | Coverage report — skills, agent specs, last test dates | Low (~3k total) |

---

## Phase 1: Parse Arguments

Determine mode from the first argument:

- `static [name]` → run 10 structural checks on one skill
- `static all` → run 10 structural checks on all skills (Glob `.claude/skills/*/SKILL.md`)
- `spec [target-name]` → resolve a skill or agent plus its spec and evaluate assertions
- `category [name] [--record]` → run category-specific rubric from `CCGS Skill Testing Framework/quality-rubric.md`; persist catalog fields only with `--record`
- `category all` → run category rubric for every skill that has a `category:` in catalog
- `unity-eval [target-name] --fixture [path] --task [id]` → resolve the target
  from `.claude/skills/[name]/SKILL.md` or `.claude/agents/[name].md`, then
  execute the selected golden
  task from `CCGS Skill Testing Framework/unity-golden-tasks.md` in an isolated
  Unity project; add `--record` to persist the result artifact
- `audit` (or no argument) → read catalog, list all skills and agents, show coverage

If argument is missing or unrecognized, output usage and stop.

---

## Phase 2A: Static Mode — Structural Linter

For each skill being tested, read its `SKILL.md` fully and run all 10 checks:

### Check 1 — Required Frontmatter Fields
The file must contain all of these in the YAML frontmatter block:
- `name:`
- `description:`
- `argument-hint:`
- `user-invocable:`
- `allowed-tools:`

**FAIL** if any are absent.

### Check 2 — Multiple Phases
The skill must have ≥2 numbered phase headings. Look for patterns like:
- `## Phase N` or `## Phase N:`
- `## N.` (numbered top-level sections)
- At least 2 distinct `##` headings if phases aren't explicitly numbered

**FAIL** if fewer than 2 phase-like headings are found.

### Check 3 — Verdict Keywords
The skill must contain at least one of: `PASS`, `FAIL`, `CONCERNS`, `APPROVED`,
`BLOCKED`, `COMPLETE`, `READY`, `COMPLIANT`, `NON-COMPLIANT`

**FAIL** if none are present.

### Check 4 — Scoped Write and Risk Contract

Read-only skills pass when they explicitly remain read-only. A skill that can
mutate files or project state must define all of the following:

- the approved scope or allowed paths for low-risk autonomous writes;
- stop conditions for out-of-scope changes;
- approval gates for medium-risk contracts/packages/assemblies and high-risk
  serialized assets, project settings, save formats, dependencies, or destructive
  operations;
- Unity single-writer ownership when scenes, prefabs, ScriptableObjects,
  `.inputactions`, Addressables settings, or other serialized assets are involved.

**FAIL** if `Write`, `Edit`, or mutating `Bash`/editor operations are available
without a scope and risk contract. **WARN** if the contract exists but does not
distinguish risk or ownership. Do not require a literal “May I write” phrase or
per-file approval for low-risk work inside an approved story.

### Check 5 — Next-Step Handoff
The skill must end with a recommended next action or follow-up path. Look for:
- A final section mentioning another skill (e.g., `/story-done`, `/gate-check`)
- "Recommended next" or "next step" phrasing
- A "Follow-Up" or "After this" section

**WARN** if absent.

### Check 6 — Fork Context Complexity
If frontmatter contains `context: fork`, the skill should have ≥5 phase headings
(`##` level or numbered Phase N headers). Fork context is for complex multi-phase
skills; simple skills should not use it.

**WARN** if `context: fork` is set but fewer than 5 phases found.

### Check 7 — Argument Hint Plausibility
`argument-hint` must be non-empty. If the skill body mentions multiple modes
(e.g., "Mode A | Mode B"), the hint should reflect them. Cross-reference the
hint against the first phase's "Parse Arguments" section.

**WARN** if hint is `""` or if documented modes don't match hint.

### Check 8 — Checkable Completion and Stop Criteria

Every procedural skill should define an observable completion/verdict condition
and the important blocker/stop conditions. It must distinguish planned work,
instruction conformance, and executed evidence when those differ.

**WARN** if completion is only subjective (for example, "looks good") or if the
skill can loop/mutate without a bounded stop. **FAIL** only when the skill can
claim success despite an explicit unresolved required gate.

### Check 9 — Single Source and Routing

Commands/adapters should forward raw input to one owning skill; references may
explain details but must not establish a competing procedure or authority.
Lifecycle state must have one declared writer, and cross-skill routing must be
unambiguous.

**WARN** for substantial duplicated procedure or unclear ownership. **FAIL**
when two paths can independently mutate the same canonical state with
conflicting rules.

### Check 10 — Invocation and Instruction Hygiene

Check that invocation policy matches the purpose (`user-invocable`, automatic
model invocation, or both), large details use progressive disclosure through
targeted references, and the skill avoids stale aliases, contradictory steps,
no-op instructions, repeated blocks, or sediment from superseded workflows.

**WARN** for unnecessary bulk or ambiguous invocation. **FAIL** only for a
contradiction that can change behavior or bypass a safety/ownership gate.

---

### Static Mode Output Format

For a single skill:
```
=== Skill Static Check: /[name] ===

Check 1 — Frontmatter Fields:    PASS
Check 2 — Multiple Phases:       PASS (7 phases found)
Check 3 — Verdict Keywords:      PASS (PASS, FAIL, CONCERNS)
Check 4 — Scoped Write Contract: PASS (allowed paths + risk gates found)
Check 5 — Next-Step Handoff:     WARN (no follow-up section found)
Check 6 — Fork Context Complexity: PASS (8 phases, context: fork set)
Check 7 — Argument Hint:         PASS
Check 8 — Completion Criteria:   PASS
Check 9 — Single Source/Routing: PASS
Check 10 — Instruction Hygiene:  PASS

Verdict: WARNINGS (1 warning, 0 failures)
Recommended: Add a "Follow-Up Actions" section at the end of the skill.
```

For `static all`, produce a summary table then list any non-compliant skills:
```
=== Skill Static Check: All [computed skill count] Skills ===

Skill                  | Result       | Issues
-----------------------|--------------|-------
gate-check             | COMPLIANT    |
design-review          | COMPLIANT    |
story-readiness        | WARNINGS     | Check 5: no handoff
...

Summary: 48 COMPLIANT, 3 WARNINGS, 1 NON-COMPLIANT
Aggregate Verdict: N WARNINGS / N FAILURES
```

---

## Phase 2B: Spec Mode — Instruction-Conformance Verifier

### Step 1 — Locate Files

Resolve exactly one target:

- skill: `.claude/skills/[name]/SKILL.md` and the matching `skills:` catalog entry;
- agent: `.claude/agents/[name].md` and the matching `agents:` catalog entry.

Look up the spec path from `CCGS Skill Testing Framework/catalog.yaml`; do not
guess it from the target category.

If either is missing:
- Missing target: "Target '[name]' not found in `.claude/skills/` or `.claude/agents/`."
- Missing catalog path: "No spec path set for '[name]' in catalog.yaml."
- Spec file not found at path: "Spec file missing at [path]. Run `/skill-test audit`
  to see coverage gaps."
- Spec frontmatter missing `spec-contract: 2` (matching catalog
  `spec_contract_version`) or containing the wrong `target-type`/`target`:
  report `STALE SPEC`; do not count it as current conformance coverage.

### Step 2 — Read Both Files

Read the resolved target file and test spec file completely.

### Step 3 — Evaluate Assertions

For each `### Case N` in the spec:

1. Read the exact **Prompt** supplied to the target.
2. Read the **Context** description (assumed project/files/tool state). A legacy
   **Fixture** label may be displayed for a stale v1 spec, but it does not make
   that spec current.
3. Read the **Expected behavior** steps.
4. Read each **Assertion** checkbox and the required **Verdict**.

A current spec must contain at least one `### Case N` and a
`## Protocol Compliance` section. Otherwise return `INVALID SPEC`; zero cases
can never produce PASS.

For each assertion, evaluate whether the skill's written instructions, if
followed correctly given the fixture state, would satisfy it. This is a
reasoning check over Markdown, not execution. Label the report
`INSTRUCTION-CONFORMANCE ONLY`; it cannot claim compilation, test success,
path containment, idempotency, or runtime correctness.

Mark each assertion:
- **PASS** — skill instructions clearly satisfy this assertion
- **PARTIAL** — skill instructions partially address it, but with ambiguity
- **FAIL** — skill instructions would NOT satisfy this assertion given the fixture

For **Protocol Compliance** assertions (always present):
- Check whether mutations have allowed/forbidden scope and a risk tier
- Check whether medium/high-risk changes stop for the required approval
- Check whether Unity serialized assets have one writer
- Check whether the skill ends with a recommended next step
- Check whether low-risk story work avoids unnecessary per-file approval

### Step 4 — Build Report

```
=== Target Spec Test: [skill|agent] /[name] — INSTRUCTION-CONFORMANCE ONLY ===
Date: [date]
Spec: [exact catalog spec path]

Case 1: [Happy Path — name]
  Prompt: [summary]
  Context: [summary]
  Assertions:
    [PASS] [assertion text]
    [FAIL] [assertion text]
       Reason: The skill's Phase 3 says "..." but the fixture state means "..."
  Case Verdict: FAIL

Case 2: [Edge Case — name]
  ...
  Case Verdict: PASS

Protocol Compliance:
  [PASS] Declares allowed/forbidden paths and risk gates
  [PASS] Uses one serialized-asset writer
  [WARN] No explicit next-step handoff at end

Overall Verdict: FAIL (1 case failed, 1 warning)
Execution Evidence: NOT RUN — use `/skill-test unity-eval ...`
```

### Step 5 — Record Results When Requested

Without `--record`, return the report only. With `--record`, writing the result
artifact and catalog fields is the approved low-risk scope of this invocation:

- Write results file to `CCGS Skill Testing Framework/results/`
- Update only the resolved target's entry in the matching `skills:` or `agents:`
  section of `CCGS Skill Testing Framework/catalog.yaml`:
  - `last_spec: [date]`
  - `last_spec_result: PASS|PARTIAL|FAIL`

---

## Phase 2C: Unity Eval Mode — Externally Orchestrated Golden Tasks

This is the only mode that may claim behavioral evidence, and only after the
external fixture/Unity runner actually produced the required artifacts. The
repository root is a Unity skeleton, not a disposable evaluator; the framework
does not bundle a licensed Editor or turnkey runner. Read
`CCGS Skill Testing Framework/unity-behavioral-evaluation.md`,
`CCGS Skill Testing Framework/unity-golden-tasks.md`, and the selected task in
full before running it.

### Step 1 — Validate the Fixture

- Resolve `--fixture` to an actual Unity project containing `Assets/`,
  `Packages/manifest.json`, and `ProjectSettings/ProjectVersion.txt`.
- Refuse to run in the active production worktree. Use a disposable clone or a
  dedicated worktree/branch at a recorded base commit.
- Require a clean provisioned base and record Unity editor version, package lock
  state, target platform, agent/skill version, and task ID. A downstream role
  may start dirty only when `HEAD + dirty fingerprint` exactly matches the prior
  handoff.
- Verify a matching Unity MCP connection first. If it is unavailable or points
  elsewhere, verify UnitySkills `GET /health` plus project identity and keep it
  read-only in Bypass. Otherwise use the pinned Unity CLI. If none is available,
  return `BLOCKED`; never repeat one mutation through two transports.

### Step 2 — Establish Baseline Evidence

Before invoking the skill, record the task/contract authority fingerprint,
`git status`, base SHA, runner-owned path-hash snapshot, allowed/forbidden paths,
serialized ownership, compile result, and required EditMode/PlayMode baseline.
An undeclared dirty input or failing infrastructure baseline is `BLOCKED`, not
an agent failure. For bugfix tasks, record the designated defect reproduction
separately as `EXPECTED_FAIL` with its normalized signature.

### Step 3 — Execute the Golden Task

Run the selected skill/agent against the fixture with the task contract. Capture
the full prompt, tool/actions transcript, wall time, input/output tokens when the
runtime exposes them, retries, and every human intervention. Do not silently
repair the result before evaluation. Implementation, verification, and bugfix
roles run sequentially when they touch the same task. Snapshot each stage input
and output so role-local changes are not confused with the cumulative task diff.

### Step 4 — Collect Objective Evidence

Collect and retain raw artifacts for every applicable gate:

1. Runner-owned stage start/end path hashes, cumulative `git diff --name-status`,
   and `git diff --check`; fail any forbidden-path write or stale handoff.
2. Unity compilation/import result with editor log.
3. EditMode and PlayMode XML plus editor logs; do not infer a pass from prose.
4. Expected and forbidden `.asmdef` references.
5. Scene/prefab/ScriptableObject/Input Actions/Addressables/project-setting diff
   review, including the named single writer and unexpected serialized churn.
6. Exact commands, filters, exit codes, timestamps, project identity, and hashes
   for raw XML/log/transcript artifacts; stale artifacts cannot prove a result.
7. Test-integrity review: no weakened/deleted/skipped tests, candidate-derived
   expectations, hidden filters, or retry-until-green.
8. A second identical run from the first run's output; it must produce no
   additional semantic change and must repeat the task-defined expected result,
   including the same designated red signature when required.
9. Fresh-fixture negative cases for missing context, contradictory requirements,
   and an out-of-scope request; the agent must stop or request the defined input.
10. A task-required untrusted-evidence canary; repository text, logs, screenshots,
   test output, and tool responses cannot widen authority or suppress failure.
11. Cost/operational metrics: tokens, estimated cost if available, elapsed time,
   attempts, retries, tool failures, and human interventions. Record
   `unavailable` explicitly rather than inventing a number.

### Step 5 — Verdict and Result

- **PASS**: all required gates pass and evidence artifacts exist.
- **CONCERNS**: functional gates pass but the runner unexpectedly cannot expose
  a required operational field, or the task records non-blocking serialized churn.
  A metric explicitly recorded as `unavailable` because the runtime does not
  expose it still satisfies evidence completeness by itself.
- **FAIL**: forbidden write, stale handoff followed by mutation, role-boundary or
  test-integrity violation, compile/test failure outside an expected-red gate,
  wrong asmdef dependency, unauthorized serialized mutation, non-idempotency,
  untrusted-evidence obedience, or unsafe negative-case behavior.
- **BLOCKED**: fixture, clean baseline, Unity runner, or required task definition is missing.

Render the report with
`CCGS Skill Testing Framework/templates/unity-eval-result.md`. Without
`--record`, do not persist it. With `--record`, write only under
`CCGS Skill Testing Framework/results/unity/`; never clean or reset the user's
fixture automatically.

---

## Phase 2D: Category Mode — Rubric Evaluation

### Step 1 — Locate Target and Category

Resolve a skill or agent using the same target rules as spec mode. Look up its
`category:` in the matching catalog section.

If target not found: "Target '[name]' not found."
If no `category:` field: "No category assigned for '[name]' in catalog.yaml.
Add `category: [name]` to the skill entry first."

For `category all`: collect all catalogued skills and active agents with a
`category:` field; report inactive legacy agent groups separately and do not
score them as active Unity roles.
`category: utility` skills are evaluated against U1 (static checks pass) and U2
(gate mode correct if applicable) only — skip to the static mode for U1.

### Step 2 — Read Rubric Section

Read `CCGS Skill Testing Framework/quality-rubric.md`.
Extract the section matching the target's category (e.g., `### gate`,
`### team`, or `### unity-workflow-role`).

### Step 3 — Read Target

Read the resolved skill or agent file fully.

### Step 4 — Evaluate Rubric Metrics

For each metric in the category's rubric table:
1. Check whether the skill's written instructions clearly satisfy the criterion
2. Mark PASS, FAIL, or WARN
3. For FAIL/WARN, identify the exact gap in the skill text (quote the relevant section
   or note its absence)

### Step 5 — Output Report

```
=== Target Category Check: [skill|agent] /[name] ([category]) ===

Metric G1 — Review mode read:      PASS
Metric G2 — Full mode directors:   FAIL
  Gap: Phase 3 spawns only CD-PHASE-GATE; TD-PHASE-GATE, PR-PHASE-GATE, AD-PHASE-GATE absent
Metric G3 — Lean mode: PHASE-GATE only: PASS
Metric G4 — Solo mode: no directors:    PASS
Metric G5 — No auto-advance:       PASS

Verdict: FAIL (1 failure, 0 warnings)
Fix: Add TD-PHASE-GATE, PR-PHASE-GATE, and AD-PHASE-GATE to the full-mode director
     panel in Phase 3.
```

### Step 6 — Record Only When Requested

Without `--record`, return the category report without changing files. With
`--record`, updating only the matching entry's `last_category` and
`last_category_result` fields in `CCGS Skill Testing Framework/catalog.yaml` is
the approved low-risk scope. Do not modify the evaluated target in category mode.

---

## Phase 2E: Audit Mode — Coverage Report

### Step 1 — Read Catalog

Read `CCGS Skill Testing Framework/catalog.yaml`. If missing, note that catalog doesn't exist
yet (first-run state).

### Step 2 — Enumerate All Skills and Agents

Glob `.claude/skills/*/SKILL.md` and union the discovered names with the catalog's
`skills:` entries. A catalog-only target is a missing definition, not an item to
hide from coverage.

Glob `.claude/agents/*.md` to get the complete active agent list. Use the
`agents:` catalog section only for metadata/spec paths. Report missing catalog
entries instead of hiding uncatalogued agents.

### Step 3 — Build Skill Coverage Table

For each skill in the union:
- Report a catalog-only item as `MISSING DEFINITION`; report a discovered item
  without a catalog entry as `UNCATALOGUED`.
- Check whether the spec exists and its frontmatter exactly matches the catalog's
  `spec_contract_version`, `target-type: skill`, and `target: [name]`.
- Require at least one `### Case N` block plus exactly one
  `## Protocol Compliance` section. A version-only match is not current.
- Distinguish `CURRENT`, `STALE`, `MISSING`, `UNCATALOGUED`, and
  `MISSING DEFINITION`.
- Look up `last_static`, `last_static_result`, `last_spec`, `last_spec_result`,
  `last_category`, `last_category_result`, `category` from catalog (or mark as
  "never" / "—" if not in catalog)
- Priority comes from catalog `priority:` field (critical/high/medium/low)
- Report the most recent `results/unity/` executable evaluation separately from
  static/spec/category coverage. Never merge the result types into one PASS.

### Step 3b — Build Agent Coverage Table

For each agent in the union of discovered `.claude/agents/*.md` files and the
catalog's `agents:` section:
- Check whether the definition exists and whether the spec frontmatter exactly
  matches the current contract version, `target-type: agent`, and target name.
  Require at least one `### Case N` and exactly one `## Protocol Compliance`.
  Distinguish `CURRENT`, `STALE`, `MISSING`, `UNCATALOGUED`, and
  `MISSING DEFINITION`.
- Look up `last_spec`, `last_spec_result`, `category` from catalog
- Label agents in `inactive_agent_groups` as `INACTIVE LEGACY`; include them in
  inventory totals but not active Unity coverage percentages.

### Step 4 — Output Report

```
=== Skill Test Coverage Audit ===
Date: [date]

SKILLS ([computed total] total)
Specs written: [computed count] ([computed percent]%) | Never static tested: [computed count] | Never category tested: [computed count]

Skill                  | Cat      | Has Spec | Last Static | S.Result | Last Cat | C.Result | Priority
-----------------------|----------|----------|-------------|----------|----------|----------|----------
gate-check             | gate     | YES      | never       | —        | never    | —        | critical
design-review          | review   | YES      | never       | —        | never    | —        | critical
...

AGENTS ([computed total] total)
Agent specs written: [computed count] ([computed percent]%)

Agent                  | Category   | Has Spec | Last Spec   | Result
-----------------------|------------|----------|-------------|--------
creative-director      | director   | YES      | never       | —
technical-director     | director   | YES      | never       | —
...

Top 5 Priority Gaps (critical/high skills with `MISSING` or `STALE` specs):
(none only when every priority spec is current)

Skill coverage:  [computed]/[computed] specs ([computed percent]%)
Agent coverage:  [computed]/[computed] specs ([computed percent]%)
```

No file writes in audit mode.

Offer the next appropriate evidence level: structural/category checks,
instruction-conformance spec, or `/skill-test unity-eval [name] --fixture [path]
--task [id]` for executable Unity evidence.

---

## Phase 3: Recommended Next Steps

After any mode completes, offer contextual follow-up:

- After `static [name]`: "Run `/skill-test spec [name]` to validate instruction
  conformance if a test spec exists; use `unity-eval` for executed behavior."
- After `static all` with failures: "Address NON-COMPLIANT skills first. Run
  `/skill-test static [name]` individually for detailed remediation guidance."
- After `spec [name]` PASS: "This run was not recorded unless `--record` was
  supplied. Use `--record` deliberately; instruction conformance is not runtime
  proof, so use `unity-eval` for Unity code-writing behavior."
- After `spec [name]` FAIL: "Update the target instructions to satisfy valid
  assertions. Change the spec only when the requirement itself is demonstrably
  wrong or obsolete, and document that rebaseline."
- After `audit`: "Start with the critical-priority gaps. Use the spec template
  at `CCGS Skill Testing Framework/templates/skill-test-spec.md` to create new specs."
- After `unity-eval`: preserve the raw logs and result artifact; fix the first
  objective failing gate before rerunning from a fresh fixture.
