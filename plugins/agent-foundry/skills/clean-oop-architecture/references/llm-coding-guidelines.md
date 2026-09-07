# LLM Coding Guidelines

Use these guidelines to reduce common LLM coding mistakes. They bias toward
caution over speed; for trivial one-line tasks, use judgment.

## 1. Think Before Coding

Do not assume or hide confusion. Surface tradeoffs before implementation.

- State assumptions explicitly.
- If multiple interpretations exist, present them instead of picking silently.
- If a simpler approach exists, say so.
- Push back when the requested direction is likely to create unnecessary
  complexity or risk.
- If something is unclear enough to affect the implementation, stop and ask.

## 2. Simplicity First

Write the minimum code that solves the current problem.

- Do not add features beyond what was asked.
- Do not add abstractions for single-use code.
- Do not add flexibility, configurability, or extension points that are not
  required now.
- Do not add error handling for impossible scenarios.
- If the solution is much longer than the problem justifies, simplify before
  presenting it.

## 3. Surgical Changes

Touch only what the task requires. Clean up only the mess created by the current
change.

- Do not improve adjacent code, comments, formatting, or naming as a drive-by
  change.
- Do not refactor unrelated code.
- Match the local style even if a different style would be preferred elsewhere.
- If unrelated dead code is found, mention it instead of deleting it.
- Remove imports, variables, functions, or files made unused by the current
  change.
- Every changed line should trace back to the user's request.

## 4. Goal-Driven Execution

Convert tasks into verifiable goals and loop until checked.

- "Add validation" becomes: write invalid-input tests, then make them pass.
- "Fix the bug" becomes: reproduce it with a test or concrete scenario, then
  make it pass.
- "Refactor X" becomes: verify behavior before and after.
- For multi-step tasks, state a short plan where every step has a verification
  check.

## Success Signals

These guidelines are working when:

- Diffs contain fewer unrelated changes.
- The solution is simpler on the first pass.
- Clarifying questions happen before implementation mistakes.
- Tests or concrete checks define when the task is done.
