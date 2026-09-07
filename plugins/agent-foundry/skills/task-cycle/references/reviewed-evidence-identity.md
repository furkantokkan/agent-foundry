# Reviewed State and Evidence Identity

This reference is normative for `implement-task`, `task-cycle`, and
`task-done`. Resolve it from the installed `task-cycle/SKILL.md` directory,
never from the target repository.

## Contract fingerprint

Hash the UTF-8 task-contract authority outside the complete
`TASK-LIFECYCLE` managed block with SHA-256. Store it as `sha256:<64 hex>`.
Lifecycle-only edits must not change this value.

## Reviewed revision

Build one deterministic review set after the final production/test edit and
before the terminal lifecycle write:

1. the full current VCS revision (`HEAD`, changeset, or equivalent);
2. every existing or explicitly missing file selected by the contract's owned
   production, test, serialized-asset, and verification-input paths;
3. every additional runtime dependency file explicitly cited by the final
   verification evidence.

Normalize repository-relative paths to forward slashes, sort them ordinally,
and hash each path plus its raw file bytes (or the literal `<missing>` marker).
Exclude the contract's managed lifecycle block, lifecycle lock files, temporary
logs, caches, and build outputs unless a retained artifact is itself cited as
required evidence.

Store a space-free identity:

```text
git:<full-head>+owned-sha256:<64-hex>
vcs:<full-provider-revision>+owned-sha256:<64-hex>
```

Uncommitted task work is valid: the owned digest identifies the exact reviewed
bytes. Do not substitute a planning base revision, timestamp, branch name,
`dirty`, `current`, or a prose label.

## Evidence fingerprint

Build a canonical UTF-8 line stream in this order:

1. contract fingerprint;
2. reviewed revision;
3. every acceptance/preservation criterion row in contract order;
4. every defect ID, status, mapping, and verified revision in ID order;
5. each required verification channel, result, and any retained command,
   artifact, or reference that the chosen channel produces.

Hash that stream with SHA-256 and store `sha256:<64-hex>`. An automated-test
or manual-verification record must identify its channel, result, and freshness.
An explicit user acceptance is a sufficient verification channel when it
identifies the accepted criterion(s) and the user order; do not require a test
log, screenshot, artifact, or additional model proof.

## Acceptance criteria freshness cells

The `Freshness` column is an identity column, not a result, status, or time
column. In every acceptance/preservation evidence row, its `Freshness` cell
MUST equal the complete top-level `Reviewed revision` value byte-for-byte,
including the full VCS revision and owned digest. The comparison is exact and
case-sensitive.

When `Reviewed revision` is `none`, every acceptance-criteria `Freshness` cell
must also be exactly `none`. After computing a reviewed revision, copy that
complete space-free token into every row. Do not shorten it, add a prefix or
suffix, or substitute literals such as `fresh`, `current`, `pass`, `PASS`, a
timestamp, a branch name, or a bare commit hash.

Keep evidence outcome in the separate `Result` cell as `PASS`, `FAIL`,
`UNPROVEN`, `STALE`, or `NOT_RUN`. Any `Freshness` cell that is not byte-for-byte
equal to `Reviewed revision` is stale identity evidence and blocks readiness,
regardless of its `Result`.

## Readiness and closure

Re-read the review set after writing the lifecycle block; because the managed
block is excluded, the reviewed revision must remain stable. `READY_TO_CLOSE`
requires:

- non-`none` contract, reviewed-revision, and evidence fingerprints;
- every required acceptance-criteria row has `Result` `PASS` and a `Freshness` cell equal
  to the complete `Reviewed revision` token byte-for-byte;
- every defect row `VERIFIED` at that same revision;
- a recomputation equal to the stored identities.

`task-done` recomputes and compares these identities without rerunning tests.
If an identity cannot be computed deterministically, do not claim readiness;
return `BLOCKED: EVIDENCE_IDENTITY_UNAVAILABLE` with the exact missing input.
