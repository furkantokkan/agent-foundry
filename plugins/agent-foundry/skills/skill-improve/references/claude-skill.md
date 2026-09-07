---
name: skill-improve
description: "Improve one skill with a scoped test-fix-retest loop. Analysis is read-only unless --apply is supplied; the target skill is the only writable source file."
argument-hint: "[skill-name] [--apply]"
user-invocable: true
allowed-tools: Read Glob Grep Write Edit
model: sonnet
---

# Skill Improve

Runs an improvement loop on a single skill:
test → fix → retest → keep or revert.

---

## Phase 1: Parse Argument

Read the skill name from the first argument. If missing, output usage and stop:

```
Usage: /skill-improve [skill-name]
Example: /skill-improve tech-debt --apply
```

Verify `.claude/skills/[name]/SKILL.md` exists. If not, stop with:
"Skill '[name]' not found."

---

## Phase 2: Baseline Test

Run `/skill-test static [name]` and record the baseline score:
- Count of FAILs
- Count of WARNs
- Which specific checks failed (Check 1–10)

Display to the user:
```
Static baseline:   [N] failures, [M] warnings
Failing: Check 4 (no scoped risk/ownership contract), Check 5 (no handoff)
```

If baseline is 0 FAILs and 0 WARNs, note it and proceed to Phase 2b.

### Phase 2b: Category Baseline

Look up the skill's `category:` field in `CCGS Skill Testing Framework/catalog.yaml`.

If no `category:` field is found, display:
"Category: not yet assigned — skipping category checks."
and skip to Phase 3.

If category is found, run `/skill-test category [name]` and record the category baseline:
- Count of FAILs
- Count of WARNs
- Which specific category rubric metrics failed

Display to the user:
```
Category baseline: [N] failures, [M] warnings  ([category] rubric)
```

Do not claim the skill needs no improvement from static/category checks alone.

### Phase 2c: Current Spec Baseline

Resolve the skill's catalog spec. If it has matching `spec-contract: 2`, run
`/skill-test spec [name]` without `--record` and capture failed/partial
assertions. If the spec is missing or stale, state:

`No structural/category gaps found; current spec/runtime behavior was not evaluated.`

When static/category have no gaps and a current spec also passes, stop with:

`No instruction-level gaps found. Unity runtime behavior is still NOT RUN; use unity-eval where applicable.`

---

## Phase 3: Diagnose

Read the full skill file at `.claude/skills/[name]/SKILL.md`.

For each failing or warning **static** check, identify the exact gap:

- **Check 1 fail** → which frontmatter field is missing
- **Check 2 fail** → how many phases found vs. minimum required
- **Check 3 fail** → no verdict keywords anywhere in the skill body
- **Check 4 fail** → mutation tools exist without exact allowed/forbidden scope,
  risk gates, or serialized-asset ownership where applicable
- **Check 5 warn** → no follow-up or next-step section at the end
- **Check 6 warn** → `context: fork` set but fewer than 5 phases found
- **Check 7 warn** → argument-hint is empty or doesn't match documented modes
- **Check 8 fail/warn** → success or stop conditions are not observable,
  bounded, or evidence-aware
- **Check 9 fail/warn** → duplicated procedures or multiple writers compete for
  the same authority instead of routing to one owner
- **Check 10 fail/warn** → invocation policy, progressive disclosure, or
  instruction hygiene is ambiguous; stale aliases, no-op steps, repetition, or
  superseded sediment can change behavior

For each failing or warning **category** check (if category was assigned in Phase 2b),
identify the exact gap in the skill's text. For example:
- If G2 fails (gate mode, full directors not spawned): skill body never references all 4
  PHASE-GATE director prompts
- If A2 fails (authoring decision boundary): the skill writes a material design
  decision without the rubric's required approval, or asks repeatedly for
  low-risk writes already authorized by an approved scope
- If T3 fails (team, BLOCKED not surfaced): skill doesn't halt dependent work on blocked agent

Show the full combined diagnosis to the user before proposing any changes.
Include current spec failures/partials when a v2 spec exists. Never edit the
spec to make an unchanged skill appear to pass.

Also diagnose predictability beyond the score:

- identify the skill's one-sentence purpose, canonical input, allowed outputs,
  lifecycle/state writer, completion condition, and stop gates;
- trace one happy path, one missing-context path, one repeated invocation, and
  one out-of-scope request;
- remove contradictions and obsolete residue before adding more prose;
- prefer one owning procedure with thin adapters and targeted references;
- flag overlapping instructions that are individually reasonable but produce
  different results depending on read order.

---

## Phase 4: Propose Fix

Write a targeted fix for each failure and warning. Show the proposed changes
as clearly marked before/after blocks. Preserve passing behavior, but remove
duplicated, no-op, contradictory, or superseded instructions when they are the
cause of unpredictability. Move large optional detail into a purpose-specific
reference only through an approved multi-file plan; do not hide canonical
authority in a reference that callers may skip.

When adapting a public third-party skill, inspect its full source, license,
runtime/install requirements, and overlap with local authority. Prefer
paraphrasing a useful pattern over copying a competing workflow. Record source
and license when substantial text or code is retained, and never install or
overwrite public material silently.

If `--apply` is absent, stop after the proposed patch and explain that
`/skill-improve [name] --apply` authorizes only the named skill file. If
`--apply` is present, continue without per-file approval prompts.

The write contract for `--apply` is:

- Allowed source path: `.claude/skills/[name]/SKILL.md` only.
- Forbidden: every other skill, agent, hook, project source/asset, package,
  project setting, serialized Unity asset, and git history operation.
- Low risk: targeted wording/frontmatter changes needed for failing checks.
- Medium risk: changing the public command contract, cross-skill routing, or
  workflow semantics requires presenting a plan and receiving explicit approval.
- High risk: dependencies, Unity serialized assets/settings, destructive
  operations, commits, or pushes are outside this skill and must stop.

---

## Phase 5: Write and Retest

Record the exact current content of the skill file in memory (for restoration
of only this invocation's edit if needed).

Write the improved skill to `.claude/skills/[name]/SKILL.md`.

Re-run `/skill-test static [name]` and record the new static score.
If a category was assigned, also re-run `/skill-test category [name]` and record the new category score.
If a current v2 spec was used at baseline, rerun `/skill-test spec [name]`
without recording and compare the same assertions.

Retest the same happy, missing-context, repeated-invocation, and out-of-scope
traces used during diagnosis. A structural score improvement does not justify a
new routing ambiguity, broadened write surface, or weaker completion gate.

Display the comparison:
```
Static:   Before [N] failures, [M] warnings  →  After [N'] failures, [M'] warnings
Category: Before [N] failures, [M] warnings  →  After [N'] failures, [M'] warnings  (if applicable)
Spec:     Before [N] failures, [M] partials  →  After [N'] failures, [M'] partials  (if current)
Change: improved / no change / worse
```

---

## Phase 6: Verdict

Compare lexicographically, not by treating a warning as equal to a failure:

1. No new FAIL may appear in any check/assertion.
2. Prefer fewer total FAILs.
3. If FAIL count is equal, prefer fewer WARN/PARTIAL results.
4. If both are equal, the score did not improve.

**If the score improved under that ordering:**
Report: "Score improved. Changes kept."
Show a summary of what was fixed in each dimension.

**If any new FAIL appears or the score is the same/worse:**
Report: "Combined score did not improve."
Show what changed and why it may not have helped.
Restore the exact pre-edit content with `Edit`; do not use `git checkout`,
`git reset`, or any operation that could discard pre-existing user changes.

---

## Phase 7: Next Steps

- Run `/skill-test static all` to find the next skill with failures.
- Run `/skill-improve [next-name]` to continue the loop on another skill.
- Run `/skill-test audit` to see overall coverage progress.
- Use `/skill-test unity-eval` for applicable code-writing behavior; this loop
  never proves Unity compilation or runtime correctness.
