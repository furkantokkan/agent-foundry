# Third-party notices

Agent Foundry is a curated personal workflow collection and adaptation layer. It does not claim original authorship of the upstream studio framework.

## Claude Code Game Studios

Source: https://github.com/Donchitos/Claude-Code-Game-Studios

License: MIT. The license below was verified against the upstream repository on 2026-09-07. The local snapshot does not retain an exact upstream commit; no exact revision match is claimed.

Scope: the ported studio workflow skills (identified by their “Codex port of Claude Code Game Studios” introductions), their `references/claude-skill.md` files, and the studio role/rule/template/hook reference library in `plugins/agent-foundry/skills/game-studio-orchestration/references/`. Local adaptations include task-contract lifecycle rules, Unity transport and ownership policies, provider adapters, and sanitized examples. Preserve this notice when redistributing those files.

MIT License

Copyright (c) 2026 Donchitos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Unity Technologies skills

Source: https://github.com/Unity-Technologies/skills

Upstream revision: `8d85172945197ee8bacbbfea44d6d64cad782004`
(reviewed 2026-09-21).

License: Unity Companion License for Unity-dependent projects. The upstream
license notice is preserved in `plugins/agent-foundry/UNITY_COMPANION_LICENSE.md`.

Scope: retained `unity-cli` reference material and upstream baseline under
`plugins/agent-foundry/skills/unity-cli/`. The 30 specialist skills are no
longer redistributed here; install the separate official
[Unity agent plugin](https://github.com/Unity-Technologies/unity-agent-plugin)
for Claude Code or Codex. Agent Foundry's CLI adaptations add exact-project
identity checks, risk/approval gates, safer installer handling, and task/preflight
integration. Unity Technologies retains ownership of the upstream material;
the Agent Foundry MIT license does not relicense it.

## Personal additions and packaging

The local domain skills, task-workflow extensions, command adapters, Unity role adaptations, and repository packaging are distributed under the root MIT license, subject to upstream rights where applicable. `docs/export-manifest.json` records each exported file's local source category and public-content hash; it is not proof of independent authorship or an exact upstream revision.

## Linked references and separate integrations

The Steam marketing skill includes a pointer index to [How To Market A Game](https://howtomarketagame.com/blog/), not a redistributed article archive. Linked articles, commercial books, optional local PDF libraries, Unity/Onity documentation, and other external resources retain their respective owners' rights; the repository license does not license those external works.

OpenAI/Anthropic system skills, third-party marketplace caches, commercial connectors, MCP credentials and account configuration are not included. Codex, Claude Code, Unity, Firebase and Steam are references to their respective products, not endorsements or included services.
