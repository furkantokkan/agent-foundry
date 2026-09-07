# Linked Defect Record

Create one record for each atomic observable same-task symptom at:

```text
production/tasks/<TASK-ID>/defects/<DEFECT-ID>.md
```

The record owns durable intake, reproduction detail, source links, and an
append-only evidence timeline. It does not own current status, attempt count,
close readiness, or the next action; those remain canonical in the parent
contract's managed defect ledger.

Do not create a reduced substitute when this template cannot be read. Stop
`BLOCKED: DEFECT_TEMPLATE_UNAVAILABLE`. Generated lines such as `Status`,
`Dedupe key`, `Attempt count`, `Close readiness`, and `Next action` are forbidden
in this child record because they would create a second lifecycle source.

```markdown
# <DEFECT-ID> — <observable symptom>

<!-- DEFECT-METADATA:START -->
- Parent task: [<TASK-ID>](../contract.md)
- Ledger: [Defect ledger](../contract.md#defect-ledger)
- Relation: AC_FAILURE | PRESERVATION_FAILURE | TASK_REGRESSION
- Maps to: <criterion, preserved behavior, or regression seam>
- First observed: <UTC timestamp and reviewed revision>
- Source: <conversation, handoff, log, screenshot, URL, or attachment path>
<!-- DEFECT-METADATA:END -->

## Observation

<Smallest player/tester-visible symptom. Do not substitute a guessed root cause.>

## Reproduction

1. <Setup>
2. <Action>
3. <Observed result>

## Expected and actual

- Expected: <contract-backed behavior>
- Actual: <observed failure>

## Evidence timeline (managed by task-cycle)

<!-- DEFECT-EVIDENCE:START -->
- <UTC timestamp> — INTAKE — <evidence and revision>
<!-- DEFECT-EVIDENCE:END -->
```

Link attachments in place. Do not copy or move binary evidence unless the user
or repository policy requires a durable repository artifact. Preserve content
outside the evidence markers after creation. Append one entry only for a
material new reproduction, hypothesis/fix transition, verification result, or
recurrence. The same input, revision, and evidence must preserve both this file
and the parent lifecycle block byte-for-byte.

`task-cycle` may repair only the generated metadata block when reconciling a
legacy/missing link. It must preserve the first-observed value and all manual
content when provenance is unambiguous; otherwise it stops with an evidence
integrity blocker.
