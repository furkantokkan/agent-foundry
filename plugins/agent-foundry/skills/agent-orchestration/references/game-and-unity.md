# Game and Unity specialization

This is a domain reference of `agent-orchestration`, not a second workflow.
Apply it only for game/studio or Unity work. Web/SaaS/tooling work uses its own
domain skills with the same generic ownership, delegation, and evidence rules.

The existing personal studio reference libraries remain installed so old
commands and links continue to work. Resolve `studioRoot` for the active
provider, never from the target project working directory:

- Packaged studio root: `../../game-studio-orchestration/references/`, resolved from this reference directory.

The `SKILL.md` in that old folder only redirects here. Do not invoke it again.
Read only the needed references below from `studioRoot`:

| Need | Reference |
| --- | --- |
| Role selection | `agents-index.md`, then the relevant `agents/` file |
| Exact role write/handoff authority | `agent-write-contracts.md` |
| Hooks, path rules, templates | `hooks-index.md`, `rules-index.md`, `templates-index.md`, then the relevant item |
| Unity architecture, execution and ownership | `rules/unity-architecture.md`, `rules/unity-automation.md`, `rules/unity-ownership.md` |

These files supply domain procedures and roles. Current user/global/repository
policy and this unified entry govern routing; legacy transport/model examples
cannot override them. If a required reference is missing, discover its exact
installed equivalent before proceeding; do not invent a role or weaken a gate.

For actual Unity work, first load all three canonical rules from `studioRoot`:
`rules/unity-architecture.md`, `rules/unity-automation.md`, and
`rules/unity-ownership.md`. This requirement is preserved from the former
studio workflow; the optional-reference selection above applies to other items.
Then run the installed `unity-cli` project-readiness check and execution
contract before implementation or verification. Check the exact Editor/project
and version gate: Unity 6+ CLI/Pipeline, pre-6 live Editor through approved MCP
for Unity. Source-only work still follows the CLI contract. Workflow-document
maintenance is not a live Editor task.

Use a game-designer role where available for player-facing mechanics; otherwise
the relevant design skill. Add only the relevant domain procedure:
`unity-game-dev`, `unity-optimization`, `firebase-game-backend`,
`javascript-game-tools`, `game-design-studio`, `game-code-review`, or a focused
specialist. Preserve current UI/backend/DI/branding choices.

Same-task implementer, verifier, and bugfixer stay sequential. Every handoff
returns to its invoking lifecycle owner with the reviewed revision and real
evidence. Only `task-cycle` writes defect rows and linked records; a bugfixer
cannot promote its own fix to VERIFIED. See the
[tracked production profile](tracked-production.md) for scheduling.
