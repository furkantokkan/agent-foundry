---
name: ambientcg-assets
description: Search, inspect, and download ambientCG CC0 assets as validated AssetDescriptors.
license: MIT
compatibility: "dcc-mcp-core 0.19+, Python 3.10+"
metadata:
  dcc-mcp:
    version: v0.2.0
    dcc: python
    layer: domain
    tags:
      - asset
      - ambientcg
      - pbr
      - materials
      - hdris
      - models
      - download
    search-hint: "ambientcg, free pbr materials, texture archive, material download, hdri download, 3d model download"
    produces: [asset_descriptor]
    tools: tools.yaml
---

# ambientCG Assets

Use this skill for ambientCG asset discovery and archive downloads. It uses the
official v3 assets endpoint and does not require an ambientCG account.

`download_ambientcg_asset` returns an `asset_descriptor` with the local archive, CC0 attribution,
and source download metadata. Pass that descriptor to a DCC adapter import skill.
