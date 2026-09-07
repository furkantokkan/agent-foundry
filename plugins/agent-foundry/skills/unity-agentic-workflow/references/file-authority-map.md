# File Authority Map

Put durable facts at the narrowest layer that must own them. Avoid copying the
same rule into several prompts.

| File or layer | Owns | Must not own |
|---|---|---|
| Machine `AGENTS.md` / global `CLAUDE.md` | Personal defaults and cross-project safety | Project architecture facts |
| Repository `AGENTS.md` | Codex entry order and repo-wide constraints | Step-by-step workflow prose |
| Repository `CLAUDE.md` | Claude entry order, canonical links, repo-wide constraints | Giant reference libraries |
| Nested `CLAUDE.md` or `AGENTS.md` | Rules for one bounded path/subsystem | Rules for unrelated paths |
| `.claude/rules/*.md` | Small enforceable policies, optionally path-scoped | Tutorials and role biographies |
| `docs/architecture/*.md` / ADR | Accepted decisions and rationale | Invocation syntax |
| `.claude/skills/<name>/SKILL.md` | A reusable procedure, gates, and output contract | Permanent project state |
| `.claude/agents/*.md` | Role, ownership, tools, forbidden actions, handoff | A second architecture policy |
| Command adapter | Description, argument hint, exact skill routing, raw arguments | Duplicated workflow logic |
| Skill `references/*.md` | Detailed examples/checklists loaded on demand | Higher-priority policy |
| `production/tasks/<id>/contract.md` | Immutable task authority plus one delimited lifecycle block containing canonical state, evidence, and the same-task defect ledger | A duplicate story, standalone QA bug, or sibling status file for new work |
| `production/tasks/<id>/defects/D-xxx.md` | One linked symptom/repro/source record and append-only evidence timeline | Current status, close readiness, task authority, or a replacement task |
| `production/...` handoff/evidence | Attributable role handoffs and retained proof | Global defaults or duplicate lifecycle authority |

Recommended precedence inside a repository:

1. Current user request and explicit task contract.
2. Accepted ADR and repository authority files.
3. Nearest path-scoped instructions.
4. Skill procedure and agent role contract.
5. References, examples, memories, and historical context.

Current code, manifests, tests, and live runtime evidence outrank stale roadmap
claims. If two authority files disagree, stop at the decision boundary and fix
the canonical source instead of choosing whichever file was discovered first.

## Unity path examples

- `Assets/Game/Combat/CLAUDE.md`: combat-only architecture and test paths.
- `.claude/rules/unity-ownership.md`: serialized asset ownership for all Unity work.
- `docs/architecture/ADR-0001-*.md`: approved DI/messaging choice.
- `production/tasks/<id>/contract.md`: exact paths/acceptance plus managed
  lifecycle state and stable linked `D-xxx` defect rows for one task; it is also
  the executable story. `task-bug` resolves new intake; only `task-cycle` writes
  rows and `defects/D-xxx.md` evidence records. `task-done` explicitly closes
  after every row is freshly `VERIFIED` and every link is valid.
- `production/tasks/<id>/handoff.md`: immutable evidence between roles.
