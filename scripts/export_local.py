"""Build a sanitized publication snapshot from explicitly selected local sources.

Maintainer utility: never copies auth, settings, caches, histories or plugin binaries.
Run only in a fresh checkout before editing the exported content.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sanitize(text, home):
    for prefix in (str(home), home.as_posix(), str(home).replace('\\', '\\\\')):
        text = text.replace(prefix, '~')
    text = text.replace('BRN-', 'GAME-').replace('Santica', 'Example Weapon')
    text = text.replace('Santica hit VFX sorunlarını düzelt', 'Fix the example weapon hit VFX')
    text = text.replace('Example Weapon hit VFX sorunlarını düzelt', 'Fix the example weapon hit VFX')
    text = text.replace('e-fur', 'maintainer')
    # No private reading library is required by the public edition.
    text = re.sub(r'`~[\\/]\.agent-context[^`]+`',
                  '`optional local reference library (not included; skip if unavailable)`', text)
    text = re.sub(r'"~/\.agent-context/[^"\n]+"',
                  '"<optional-local-reference-path>"', text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True)
    args = parser.parse_args()
    home = args.home.resolve()
    plugin = ROOT / 'plugins/agent-foundry'
    if (plugin / 'skills').exists():
        raise SystemExit('Refusing to overwrite an existing export.')
    commands = home / 'plugins/personal-game-commands/commands'
    names = {p.stem for p in commands.glob('*.md')}
    names.update('''
        clean-oop-architecture game-design-studio unity-game-dev
        firebase-game-backend javascript-game-tools
        2d-pixel-perfect audio-setup-mixers build-live-game
        generate-editor-search-query implement-in-app-purchases
        initialize-ai-navigation levelplay-unity-integration localization
        manage-sprite-atlas migrate-birp-to-urp new-unity-project optimize-audio
        optimize-text-mesh-pro optimize-web physics-3d-collision
        setup-multiplayer-services setup-vivox-voice-chat
        shader-graph-create-custom-node sprite-editor sprite-segment-3x3grid
        tilemap-palette-create tilemap-ruletile-createempty
        tilemap-ruletile-createfromsegment ui ui-imgui ui-ugui ui-uitk
        unity-cli unity-package-management urp-postprocessing
        validate-urp-render-graph-renderer-feature
    '''.split())
    sources = []

    def copy(source, target, label):
        if source.is_symlink():
            raise ValueError(f'Symlink not allowed: {label}')
        text = sanitize(source.read_text(encoding='utf-8-sig'), home)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8', newline='\n')
        sources.append({'path': target.relative_to(ROOT).as_posix(), 'source': label,
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})

    selected = []
    for name in sorted(names):
        source = home / '.codex/skills' / name
        if not (source / 'SKILL.md').is_file():
            continue
        selected.append(name)
        for path in sorted(source.rglob('*')):
            if path.is_file() and path.suffix in {'.md', '.yaml', '.sh'}:
                relative = path.relative_to(source)
                copy(path, plugin / 'skills' / name / relative,
                     f'local Codex skill: {name}/{relative.as_posix()}')
    for path in sorted(commands.glob('*.md')):
        copy(path, ROOT / 'commands' / path.name, f'local personal-game-commands: {path.name}')
        if path.stem not in selected:
            copy(path, plugin / 'commands' / path.name, f'local command alias: {path.name}')
    for name in ['unity-feature-implementer', 'unity-test-verifier', 'unity-bugfixer']:
        copy(home / '.claude/agents' / f'{name}.md', plugin / 'agents' / f'{name}.md',
             f'local Claude role: {name}')
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'docs/export-manifest.json').write_text(json.dumps(sources, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'skills': len(selected), 'commands': len(list(commands.glob('*.md'))),
                      'aliases': len(list((plugin / 'commands').glob('*.md'))),
                      'files': len(sources)}, indent=2))


if __name__ == '__main__':
    main()
