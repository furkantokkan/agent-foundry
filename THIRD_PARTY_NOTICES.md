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

Scope: 30 newly added specialist skill folders under
`plugins/agent-foundry/skills/`, plus the expanded `unity-cli` references and
upstream baseline. Agent Foundry adaptations add CLI-first routing, exact-project
identity checks, explicit risk/approval gates, safer installer handling, and
integration with the existing task/preflight workflow. Unity Technologies
retains ownership of the upstream material; the Agent Foundry MIT license does
not relicense it.
## Personal additions and packaging

The local domain skills, task-workflow extensions, command adapters, Unity role adaptations, and repository packaging are distributed under the root MIT license, subject to upstream rights where applicable. `docs/export-manifest.json` records each exported file's local source category and public-content hash; it is not proof of independent authorship or an exact upstream revision.

## Blender Skills

Source: https://github.com/arjun988/blender-skills

License: MIT. The Blender & Texture Foundry plugin includes the following
skill folders and their shared Markdown references: `blender-modeler`,
`hard-surface`, `materials`, `texture-workflow`, `uv-workflow`, `lookdev`,
`lighting`, `camera-cinematography`, `rendering`, `geometry-nodes`,
`asset-optimization`, `export-pipeline`, `unity-export`, and
`hand-painted-style`.

MIT License

Copyright (c) 2026 blender-skills contributors

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

## dcc-asset-ambientcg

Source: https://github.com/dcc-mcp/dcc-asset-ambientcg

License: MIT. The Blender & Texture Foundry plugin includes the
`ambientcg-assets` skill, its API helper scripts, tool schema, and smoke test.

MIT License

Copyright (c) 2026 dcc-mcp

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

## Blender SuperSkill

Source: https://github.com/powerhouse90/Blender-Superskill

License: MIT. AI 3D Foundry includes the `blender-superskill` skill, its
reference library, orchestration script, and Codex agent metadata.

MIT License

Copyright (c) 2026 powerhouse90

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

## Alpha3D Scene Generation Skill

Source: https://github.com/ig-shadow-walker/BlenderXAlpha-3DGenSkill

License: MIT. AI 3D Foundry includes the `alpha-scene-gen` skill, its provider
adapters, and Blender helper references. Provider accounts, keys, paid credits,
and MCP connections are not included.

MIT License

Copyright (c) 2026 Alpha3D

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

## Hunyuan3D skill

Source: https://github.com/Sheshiyer/skill-clusters

License: MIT. AI 3D Foundry includes the `hunyuan3d` skill, its reference, and
an adapted script for Tencent's hosted Hunyuan3D Space. The adaptation removes
the command-line token option and accepts only the `HF_TOKEN` environment
variable when authentication is needed.

MIT License

Copyright (c) 2026 Sheshnarayan Iyer

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

## Liquid UI Kit (godot-liquid-ui)

Source: https://github.com/Miisan-png/godot-liquid-ui

Unity guide revision reviewed on 2026-09-20 against upstream commit
`91311f7c4535ca29619add25a1ff72b0f9c6fa1b`. The Unity/UI Toolkit guides are
behavioral adaptations, not a compiled Unity runtime or a redistribution of
the upstream bundled assets.

License: MIT, declared in the upstream README ("MIT. Do whatever you want
with it."). When the adaptation was made on 2026-09-11 the upstream
repository published no separate LICENSE file, so the standard MIT text is
reproduced below with the author's published name. The `game-feel-polish`
skill in the core plugin adapts the kit's system design, tuning values, and
condensed GDScript excerpts from `scripts/core` and `scripts/ui`. The kit's
bundled assets are not included: sounds by Kenney (CC0), the Bungee font
(SIL Open Font License), and brand icons from Simple Icons (CC0) remain with
their owners. Preserve this notice when redistributing the skill.

MIT License

Copyright (c) 2026 Miisan

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

## Linked references and separate integrations

The Steam marketing skill includes a pointer index to [How To Market A Game](https://howtomarketagame.com/blog/), not a redistributed article archive. Linked articles, commercial books, optional local PDF libraries, Unity/Onity documentation, and other external resources retain their respective owners' rights; the repository license does not license those external works.

OpenAI/Anthropic system skills, third-party marketplace caches, commercial connectors, MCP credentials and account configuration are not included. Codex, Claude Code, Unity, Firebase and Steam are references to their respective products, not endorsements or included services.
