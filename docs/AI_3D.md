# AI 3D Foundry

`ai-3d-foundry` is the optional companion for AI-assisted 3D creation. It
contains three focused skills: reference-first Blender modeling, local-image
to textured-3D generation through Hunyuan3D, and controlled assembly of
provider-generated assets in Blender.

## Install

```bash
codex plugin marketplace add furkantokkan/agent-foundry
codex plugin add ai-3d-foundry@agent-foundry
```

```bash
claude plugin marketplace add furkantokkan/agent-foundry
claude plugin install ai-3d-foundry@agent-foundry
```

Restart the agent session after installation.

## Choose the right path

| Goal | Skill | What it needs |
| --- | --- | --- |
| Build or repair a Blender asset from reference | `blender-superskill` | Blender plus a compatible Blender MCP bridge for scene actions |
| Convert an image into a textured mesh | `hunyuan3d` | Python 3.8+, `gradio_client`, network access; a Hugging Face token only if the Space requires one |
| Generate paid-provider assets and arrange them in Blender | `alpha-scene-gen` | A supported 3D-provider MCP connection and a running Blender MCP bridge |

The Hunyuan3D path accepts one source image or front/back/left/right views and
can export GLB, OBJ, PLY, or STL. Prefer GLB for Blender and game-engine
handoff. Start with a clean object image, then inspect scale, topology,
materials, and unseen surfaces before shipping the result.

`alpha-scene-gen` is deliberately cost-aware: it checks provider and Blender
connections, makes a scene plan, and requires explicit confirmation before a
credit-spending generation request. It does not install a provider account,
API key, Blender, or an MCP bridge.

## A practical Astra prompt

```text
Use image-to-3d to turn this product image into a textured GLB. First verify
the available generator, then produce a game-ready result under 20k triangles
and report any areas that need Blender cleanup.
```

The skills are model-agnostic: Astra can use them once they are available in a
new agent session. They provide workflow and tool guidance; they do not add a
3D-generation model to Astra itself.

See [third-party notices](../THIRD_PARTY_NOTICES.md) for source attribution
and licensing.
