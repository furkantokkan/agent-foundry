# Changelog

## 0.2.0 - 2026-09-21

- Add 30 Unity specialist skills from `Unity-Technologies/skills` at revision
  `8d85172945197ee8bacbbfea44d6d64cad782004`, preserving Unity Companion
  License attribution and bundled references/resources.
- Expand `unity-cli` from the official baseline and keep Agent Foundry's exact
  project identity, explicit risk approval, machine-readable automation, and
  safer download-inspect-run installation rules.
- Make Unity CLI the mandatory control plane across preflight, implementation,
  verification, orchestration, roles, and global installation guidance. Install
  the official CLI when missing, use built-in `unity mcp` when needed, and keep
  legacy MCP/UnitySkills explicit-request-only instead of automatic fallbacks.
- Expand adaptive routing and package metadata to 123 core skills / 142 total
  skills. Validation covers inventory, manifests, references, JSON, provenance,
  private-path patterns, and installed CLI smoke checks.
## 0.1.4 - 2026-09-20

- Document Unity Liquid UI invocation, standalone installation, source-reference
  boundaries and adaptive routing; keep the generated catalog version current.

- Adapt the existing `game-feel-polish` skill to Unity UI Toolkit with widget,
  input, lifetime and reduced-motion guidance for Claude Code and Codex.
- Replace incomplete Unity code sketches with scoped system mappings; preserve
  time/camera ownership and cover cancellation, pooling and build checks.
- Record the upstream revision and update core plugin metadata to 0.1.3.
- Validation: package/frontmatter checks; no Unity runtime package or Editor
  behavior is claimed by this documentation release.

## 0.1.3 — 2026-09-11

- Add `game-feel-polish`, a core skill that packages the Liquid UI juice-kit architecture and tuned numbers (trauma screen shake, wall-clock hitstop and slow motion, rest-state tween helpers, hit flash, pooled damage numbers, pooled SFX banks, toast stacks, animated counters and lag bars, staggered menu intros, CRT screen looks) for Godot 4, with a Unity port guide and an A/B verification checklist.
- Add the `game-feel-polish` command adapter, Codex/ChatGPT interface metadata, catalog entry, adaptive-skills routing, and MIT attribution for the upstream kit.
- Bump the core plugin to 0.1.2 (93 skills) and correct the installation notes to list all three plugins.

## 0.1.2 — 2026-09-07

- Add AI 3D Foundry, an optional three-skill plugin for reference-first Blender modeling, image-to-textured-3D generation, and cost-aware AI scene assembly.
- Add local environment-token guidance and remove the Hunyuan script's command-line token parameter so credentials are not placed in shell history.
- Add marketplace entries, installation documentation, validation coverage, and MIT notices for the included upstream components.

## 0.1.1 — 2026-09-07

- Add Blender & Texture Foundry, an optional 16-skill plugin for modeling, PBR materials, UVs, baking, look development, rendering, Unity export, and CC0 texture research.
- Add install guidance, a Blender/texture catalog, plugin manifests, validation coverage, and MIT notices for the included upstream components.
- Add original texture-discovery guidance for choosing Poly Haven and ambientCG assets without copying unlicensed Poly Haven source code.

## 0.1.0 — 2026-09-07

- Publish a curated snapshot of 92 skills and 93 command adapters.
- Package shared skills for Codex and Claude Code, with seven Claude aliases and three Unity agent roles.
- Add a searchable catalog, install guidance, provenance manifest, and upstream MIT notices.
- Generalize local paths and project examples; exclude account configuration and marketplace caches.
- Add automated package validation. Full workflow behavior across runtimes remains an open verification area.
