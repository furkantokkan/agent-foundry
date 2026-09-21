# Unity Operating Model

## Daily loop

1. Preflight: exact repository, instructions, Unity version, VCS state, live
   Editor identity through Unity CLI first, then matching MCP and UnitySkills,
   compilation/import/play state, and ownership.
2. Contract: objective, allowed/forbidden paths, serialized owner, acceptance,
   verification, risk, commit policy, and handoff target.
3. Implement: one writer, smallest change, focused tests.
4. Verify: focused checks -> Unity compilation -> EditMode/PlayMode as required ->
   manual/built-player/profiler evidence where the behavior demands it.
5. On a direct tracked initial execution whose defect ledger is still empty,
   `implement-task` records fresh acceptance/preservation evidence and
   `READY_TO_CLOSE` itself when every required gate passes. This clean path goes
   directly to `/task-done`; it does not invoke `task-cycle`.
6. Intake new bugs through `/task-bug [<ID>] "<feedback>"`; it resolves the
   owner and dispatches to task-cycle. Resume already-recorded defects with
   `/task-cycle <ID>`. Acceptance, preservation, and task-regression failures
   remain on the same contract. Natural-language feedback with no plausible
   owner routes once to `create-task`; implementation starts only after that
   contract is ready and the returned `implement-task` command is invoked.
7. Review containment, linked defect records when present, the ledger, and
   evidence freshness.
8. Handoff, or explicitly close with `/task-done` only after all required
   evidence is fresh and the ledger is either empty or entirely verified.

Never repeat a mutation across transports. If the UnitySkills fallback reports
Bypass, use it read-only and ask the user to select Approval in its panel before
mutation; REST/chat must not change the mode.

## Risk gates

- Low: approved-scope code, tests, docs, and read-only inspection can proceed.
- Medium: new assembly, module, public interface, or cross-system contract needs
  a decision-ready plan before writing.
- High: dependencies, packages, save/network schemas, migrations, scene/prefab/
  ScriptableObject/project settings, destructive Git/VCS, deploy, or release need
  exact explicit approval.

## Architecture default

Preserve the established composition model inside its bounded context. Existing
ServiceLocator/container usage may stay within that context. For a genuinely new
greenfield system, Onity is the preferred stack only when the repository's
accepted ADR says so and the package is installed or its installation is
explicitly approved. Do not start new Zenject/Extenject, VContainer, UniRx, R3,
or MessagePipe usage by convenience.

Plain C# domain code receives dependencies through constructors or methods.
Composition roots resolve dependencies; MonoBehaviours adapt lifecycle,
serialization, and Unity APIs.

## Parallelism

- Same story: implementer, verifier, bugfixer, verifier are sequential.
- Independent tasks: separate branch/worktree and disjoint paths.
- Read-only research can run in parallel.
- Every serialized Unity asset and `.meta` pair has one active writer.

## Evidence standard

Prompt linting proves only that instructions exist. Production readiness also
needs realistic golden tasks, path-containment checks, compilation, relevant
EditMode/PlayMode results, serialized diff review, idempotency where applicable,
and human-intervention/retry/cost measurements for the workflow itself.

## Same-task defect invariant

`task-bug` is the read-only task-matching intake. `task-cycle` alone writes the
contract's defect ledger and linked `defects/D-xxx.md` evidence histories. It
assigns stable semantic `D-xxx` IDs, deduplicates paraphrases, and reopens the
same row/record when a verified symptom recurs. Current status exists only in
the ledger. A fix is not complete until its original repro or
regression channel passes at the current reviewed revision. Any non-`VERIFIED`
row blocks `READY_TO_CLOSE`; tasks never auto-close. A clean direct
`implement-task` may finalize only while the ledger remains empty, and must
preserve that header-only table. Only a distinct
player-facing outcome, explicit non-goal, or unrelated pre-existing bug becomes
a new task. For repair-intent input, `task-bug` delegates that new contract to
`create-task`; ambiguity or a missing supplied identity still writes nothing.
