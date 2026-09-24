---
name: texture-discovery
model: sonnet
effort: high
description: Find free, shippable PBR texture sets and HDRIs from Poly Haven and ambientCG. Use for texture research, material references, CC0 asset selection, map/format choices, or when a Blender scene needs a surface library before look development.
license: MIT
metadata:
  domain: blender
  role: asset-research
  triggers: texture, material, PBR, HDRI, Poly Haven, ambientCG, normal map, roughness, albedo, CC0
  related-skills: materials, texture-workflow, lookdev, ambientcg-assets
---

# Texture Discovery

Find the smallest suitable CC0 asset set before making a material. Use this
skill for discovery and selection; use `materials` or `texture-workflow` once
the asset is chosen.

## Sources

| Source | Best for | License |
| --- | --- | --- |
| [Poly Haven](https://polyhaven.com/textures) | Blender-ready PBR sets, HDRIs, and models | CC0 |
| [ambientCG](https://ambientcg.com/) | Broad material, decal, atlas, terrain, and HDRI library | CC0 |

Both sources provide assets that can be used commercially. Preserve the source
URL with the selected asset in a project asset manifest. A product that shows
live Poly Haven API search results must visibly credit Poly Haven; downloaded
assets themselves do not require attribution.

## Selection workflow

1. Identify the surface, scale, art direction, target renderer/engine, and
   maximum texture resolution.
2. Search both sources with concrete terms: `weathered oak boards`, `painted
   metal panel`, `mossy stone wall`, or `overcast forest HDRI`.
3. Inspect the selected asset's available files before transfer. Start at 1K or
   2K for ordinary game assets; use 4K only for close-up assets with a budget.
4. Prefer a complete PBR set: base color/albedo, roughness, normal, and only
   the extra maps the material needs. In Blender use an OpenGL normal map
   (`nor_gl`) when the source provides a choice.
5. Record the asset ID, source URL, license, chosen resolution, and selected
   maps. Then hand off to `materials`, `texture-workflow`, or `lookdev`.

## Quick API inspection

Poly Haven has a public read-only API. This PowerShell example lists metadata
for all texture assets, then narrows locally by name, description, tags, and
category:

```powershell
$assets = Invoke-RestMethod 'https://api.polyhaven.com/assets?type=textures'
$assets.GetEnumerator() |
  Where-Object { ($_.Key + ' ' + ($_.Value | ConvertTo-Json -Compress)) -match 'wood|oak' } |
  Select-Object -First 10 Key, Value
```

Inspect one asset's exact variants before downloading:

```powershell
Invoke-RestMethod 'https://api.polyhaven.com/files/wood_floor' |
  ConvertTo-Json -Depth 12
```

For ambientCG, use the bundled `ambientcg-assets` skill. It queries the
official v3 API and lists the archive sizes for an exact asset before download.

## Map handling

| Map | Blender color space | Notes |
| --- | --- | --- |
| Base color / diffuse | sRGB | Do not bake ambient occlusion into it. |
| Roughness / metallic / AO | Non-Color | Pack channels only when the target engine expects it. |
| Normal (`nor_gl`) | Non-Color | Pass through a Normal Map node. |
| Height / displacement | Non-Color | Use only when silhouette/detail justifies the cost. |
| HDRI | Linear | Prefer `.hdr` unless the pipeline needs `.exr`. |

## Do not

- Download a full library "just in case".
- Mix DirectX and OpenGL normal-map conventions.
- Treat an image found in a web search as a production texture without checking
  its license.
- Choose a texture resolution before checking the asset's screen size and
  memory budget.
