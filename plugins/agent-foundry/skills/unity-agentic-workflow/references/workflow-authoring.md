# Workflow Authoring

Use a single canonical procedure and thin provider adapters.

## 1. Define the contract

Write before implementation:

- trigger and non-trigger examples;
- required/optional inputs and safe defaults;
- repository and instruction discovery;
- allowed mutations and risk gates;
- deterministic steps and stop conditions;
- output/evidence contract;
- persistent-state ownership, semantic deduplication, and idempotency rules;
- explicit completion criteria that distinguish fixed from freshly verified;
- realistic forward-test cases.

## 2. Choose the canonical source

Keep provider-neutral semantics in one maintained `SKILL.md` plus shallow
references. Mirror only when the providers cannot share the same discovery root.
Record which copy is canonical and how parity is checked.

## 3. Claude Code adapter

- Project skill: `.claude/skills/<name>/SKILL.md`.
- Optional thin slash command: `.claude/commands/<alias>.md`.
- Role only when ownership/tools/handoff differ: `.claude/agents/<role>.md`.
- Deterministic safety enforcement only: `.claude/hooks/`.
- Durable project policy belongs in `CLAUDE.md`, rules, or an ADR—not the
  command prompt.

## 4. Codex adapter/plugin

- Skill package: `skills/<name>/SKILL.md`, optional `references/`, and
  `agents/openai.yaml`.
- Thin command adapter must name the exact skill and pass `$ARGUMENTS` raw.
- Plugin manifest declares `commands`/`skills` directories and UI metadata.
- Update an installed marketplace plugin through its marketplace source,
  cachebuster/version helper, validation, and reinstall; do not hand-edit cache.

## 5. Validate

1. Static: frontmatter/schema, no TODO/placeholders, every command resolves to an
   installed skill, argument forwarding works, and catalogs match files.
2. Collision: global and plugin aliases either match byte-for-byte or one source
   is retired deliberately.
3. Forward tests: minimal request, flags/quoted paths, continuation, ambiguous
   repo, dirty overlap, high-risk mutation, automation mismatch, and verification
   failure.
4. Unity evidence: allowed-path containment, compile/test result, serialized diff
   policy, and rerun/idempotency where relevant.
5. Lifecycle: repeated/paraphrased feedback reuses one defect ID, partial fixes
   cannot close, recurrence reopens the same row, mixed feedback separates a
   new outcome, and only fresh verification permits explicit closure.

Never use prompt tests alone as evidence that the workflow can develop a game.

For tracked Unity work, keep one lifecycle authority: `/task-bug` may resolve
the owning task but remains a direct-write-free router. It invokes `/task-cycle`
for one existing owner or `/create-task` for a natural-language no-match, never
both as independent routes. `/task-cycle` is the sole
defect-ledger and linked-record writer. It owns stable semantic `D-xxx` IDs and
`defects/D-xxx.md` evidence timelines; adapters route raw feedback through the
intake instead of creating replacement QA bugs, duplicate state, or `status.md`.
`/create-task` is the sole new-contract writer and does not auto-implement.
`/task-done` performs the explicit close only after all rows are `VERIFIED` and
required acceptance/preservation evidence is fresh.
