---
name: verification-before-completion
description: Use when preparing to say a change is complete, a defect is fixed, checks pass, or a commit or release is ready.
---

# Verification Before Completion

Match each completion claim to fresh evidence from the current revision. This
skill checks the claim; it does not replace a task contract, QA plan, or the
project's test procedure.

## Check the claim

1. Write down the exact behavior or state you intend to report.
2. Select the smallest relevant verification channel: automated test, build,
   manual reproduction, artifact inspection, or explicit user acceptance.
3. Run or inspect that channel after the last relevant edit. Record the command
   or manual steps, target revision, result, and any skipped scope.
4. Compare the result with the claim. A passing linter does not prove a build;
   a passing build does not prove behavior; a changed file does not prove a bug
   is fixed.
5. Report only what the evidence supports. If verification is unavailable,
   identify the unverified claim and the specific blocker.

For a defect, repeat the original failing scenario after the fix. For a tracked
task, check each required acceptance criterion and use its owning lifecycle
skill for status changes. User acceptance is valid evidence when the workflow
allows it; do not demand a log or screenshot to replace it.

## Completion gate

Before a commit, push, PR, release, or handoff, inspect the diff and the latest
results for the claimed scope. Stop a completion claim when a required check
failed, was not run, or predates the relevant edit. State the observed result
and remaining work instead of extrapolating from a partial check.

This skill is read-only. It does not authorize new tests, external publishing,
or a lifecycle transition. Follow repository instructions and the relevant
task, Unity, or release skill for those actions.

## Output

- **Claim:** the precise result being reported.
- **Evidence:** command or manual steps, result, and revision or time.
- **Limit:** required checks not covered and any blocker.
- **Verdict:** verified for the stated scope, partially verified, or unverified.
