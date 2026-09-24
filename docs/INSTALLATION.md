# Installation and compatibility

## Plugin installation

The README uses GitHub marketplace installation. Agent Foundry's marketplace exposes three plugins: `agent-foundry` for task-first game-development workflows (including `game-feel-polish`), `blender-texture-foundry` for Blender and CC0 texture production, and `ai-3d-foundry` for AI-assisted 3D creation. Both runtimes share the same skill sources.

Unity Technologies' [official Unity agent plugin](https://github.com/Unity-Technologies/unity-agent-plugin) is a separate marketplace install for both runtimes:

| Runtime | Install commands | Specialist invocation |
| --- | --- | --- |
| Codex | `codex plugin marketplace add Unity-Technologies/unity-agent-plugin` then `codex plugin add unity@unity-agent-plugin` | `unity:<skill-name>` |
| Claude Code | `claude plugin marketplace add Unity-Technologies/unity-agent-plugin` then `claude plugin install unity@unity-agent-plugin` | `/unity:<skill-name>` |

Check installation with `codex plugin list` or `claude plugin list`, then restart the agent session. The [Claude marketplace listing](https://claude.com/marketplace/plugins/unity) and [Unity's Codex announcement](https://unity.com/blog/unity-plugin-codex) provide the product context. Agent Foundry does not install or bundle the official plugin. Use Agent Foundry for task contracts, Unity CLI policy, ownership, verification, and handoffs; use the official plugin for its 30 specialist procedures. Both have a `unity-cli` skill name: Agent Foundry carries the operating contract and Unity's namespaced skill carries the vendor procedure. Do not repeat an Editor mutation through both.

Install the optional Blender companion when you need visual-production skills:

```bash
codex plugin add blender-texture-foundry@agent-foundry
# or
claude plugin install blender-texture-foundry@agent-foundry
```

See [Blender & Texture Foundry](BLENDER_TEXTURES.md) for its skill catalog and requirements, and [AI 3D Foundry](AI_3D.md) for the optional AI 3D companion.

For local inspection:

```bash
git clone https://github.com/furkantokkan/agent-foundry.git
cd agent-foundry
python scripts/validate.py
```

Codex CLI command syntax was checked against the installed CLI's `plugin marketplace add --help` and `plugin add --help`. If those commands are missing, use a CLI version supporting plugins, or install individual skill folders through the skill discovery mechanism supported by your version.

Claude Code discovers the plugin's `skills`, `commands`, and `agents` directories. Skills are namespaced as `/agent-foundry:<skill-name>`. When an instruction uses a bare skill name or a historical slash command, resolve it within this plugin first. Namespacing also applies to its three agent roles.

Codex does not load Claude agent declarations. Treat the bundled roles as references and use the collaboration facilities allowed by the running host. A workflow must not invent an unavailable tool or bypass its host policy.

## Liquid UI for Unity

The core plugin includes `game-feel-polish`; no separate Liquid UI plugin is
needed. Claude Code and Codex share the canonical skill.

| Installation | Example invocation |
| --- | --- |
| Claude Code plugin | `/agent-foundry:game-feel-polish Add Liquid UI feedback to this Unity menu` |
| Codex | `Use game-feel-polish to add Liquid UI feedback to this Unity menu.` |
| Standalone | Ask for `game-feel-polish` in the host where the folder is installed |

For standalone use, copy the whole
[game-feel-polish folder](../plugins/agent-foundry/skills/game-feel-polish),
including references, metadata and THIRD_PARTY_NOTICES.md, into
`~/.codex/skills/` or `~/.claude/skills/`. Restart the agent session afterward.
Check workflow dependencies before implementation: the core plugin bundles
unity-preflight and implement-task; Editor transports are separate.
Avoid maintaining both standalone and plugin copies unless you deliberately
manage which version is invoked.

Read the [Unity guide](../plugins/agent-foundry/skills/game-feel-polish/references/unity-port.md)
for system responsibilities and the
[UI Toolkit guide](../plugins/agent-foundry/skills/game-feel-polish/references/unity-ui-toolkit.md)
for widgets, input, cancellation and acceptance scenarios. Godot excerpts are
source references, not C# code to paste into Unity. New screen-space UI defaults
to UI Toolkit; existing UGUI contexts retain their project stack.

Installation does not import art/audio, install Unity packages or connect an
Editor. Package checks do not prove rendering, input or runtime performance;
verify those in the target Unity project.

## Commands and aliases

The root `commands/` directory archives 94 local command definitions for inspection or manual adaptation. The installed Claude plugin adds only these seven aliases, because the other names are already exposed by skills:

| Alias | Skill |
| --- | --- |
| `ada` | `adaptive-skills` |
| `clean-oop` | `clean-oop-architecture` |
| `code-review` | `game-code-review` |
| `firebase-game-api` | `firebase-game-backend` |
| `game-design` | `game-design-studio` |
| `js-game-tools` | `javascript-game-tools` |
| `unity-dev` | `unity-game-dev` |

Do not install the archive on top of the plugin unless you deliberately want duplicate command names. A reference to a “Codex skill” in an older command adapter means the bundled skill of that name; its procedure is also available to Claude, subject to the host's own tools and policies.

## Project setup

1. Establish your repository's `AGENTS.md` and/or `CLAUDE.md`, allowed paths, architecture, and verification commands.
2. Start with `adaptive-skills`, `start`, or `unity-agentic-workflow` to inspect what your project needs.
3. Let task creation use your repository's ID format and write its contract under `production/tasks/<ID>/contract.md`.
4. Review required tools before implementation. Unity CLI, Firebase tooling, and Steam access are not bundled. For every Unity task, verify the official CLI and install it when missing; use CLI/Pipeline or built-in `unity mcp`. Legacy standalone Unity MCP and UnitySkills are explicit-request-only, not fallback transports.

The studio references include templates, rules and hook examples. They are reference material, not files automatically installed into your project's `.claude/` tree. If a workflow requires one, locate the corresponding bundled reference, review it and adapt it to the target repository with the appropriate authority. Do not silently activate hook scripts.

## Portability notes

- This is a sanitized snapshot of a personal setup, not a synchronized copy of the maintainer's machine.
- Private paths and project examples were generalized. Optional local PDF/reference libraries are not distributed and must be skipped when unavailable. Use your pinned project docs or official documentation instead.
- References to other globally installed web/security/design skills are optional extension points, not included capabilities. Install them from their original sources if needed.
- Unity architecture defaults are opinionated: an established ServiceLocator takes precedence; Onity is the preferred new composition option. Adapt this policy to your project. Installing this plugin does not install Unity packages.
- CLI flags and API recommendations can age. Installed-version help and current official docs override old reference examples.
- No credentials, MCP server configuration, shell hooks, project assets, or commercial marketplace caches are included.

## Updating or removing

Use your runtime's marketplace update and plugin removal commands; consult `codex plugin --help` or `claude plugin --help` for your installed version. Removing a plugin does not undo task documents or project code created while using it.

## Verification scope

`scripts/validate.py` checks expected inventory, manifests, entry-point names, command alias collisions, private-path/credential patterns, and export hashes. It does not run the workflows against an LLM or certify Unity behavior. Runtime manifest validators are useful additional checks. Report the exact CLI version and failing command when filing an installation issue.

For the initial release, local Codex marketplace registration and plugin installation succeeded in an isolated test profile. The Codex plugin validator and Claude plugin manifest validator also passed. This proves package discovery and installation structure, not end-to-end execution of all 93 Agent Foundry core skills or the separately installed Unity plugin.
