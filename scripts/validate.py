"""Validate the distributable package with the Python standard library."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/agent-foundry'
BLENDER_PLUGIN = ROOT / 'plugins/blender-texture-foundry'
AI_3D_PLUGIN = ROOT / 'plugins/ai-3d-foundry'
PACKAGED_PLUGINS = [PLUGIN, BLENDER_PLUGIN, AI_3D_PLUGIN]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def description(path):
    text = path.read_text(encoding='utf-8')
    front = text.split('---', 2)[1]
    match = re.search(r'^description:\s*(.*)', front, re.M)
    check(match is not None, f'Missing description: {path}')
    value = match.group(1).strip()
    if value in {'>-', '>', '|', '|-'}:
        following = front[match.end():].splitlines()
        value = ' '.join(line.strip() for line in following if line.startswith('  '))
    return value.strip('"\'').replace('|', '\\|')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Refresh export hashes and generated catalog after intentional edits')
    args = parser.parse_args()
    skills = sorted((PLUGIN / 'skills').glob('*/SKILL.md'))
    blender_skills = sorted((BLENDER_PLUGIN / 'skills').glob('*/SKILL.md'))
    ai_3d_skills = sorted((AI_3D_PLUGIN / 'skills').glob('*/SKILL.md'))
    names = {p.parent.name for p in skills}
    commands = sorted((ROOT / 'commands').glob('*.md'))
    aliases = sorted((PLUGIN / 'commands').glob('*.md'))
    agents = sorted((PLUGIN / 'agents').glob('*.md'))
    check(len(skills) == 92, 'Expected 92 skills; update documented inventory for an intentional change')
    check(len(blender_skills) == 16, 'Expected 16 Blender & Texture Foundry skills; update documented inventory for an intentional change')
    check(len(ai_3d_skills) == 3, 'Expected 3 AI 3D Foundry skills; update documented inventory for an intentional change')
    check(len(commands) == 93 and len(aliases) == 7 and len(agents) == 3, 'Unexpected command/agent inventory')
    check(not names.intersection(p.stem for p in aliases), 'Alias shadows a skill')
    for skill in skills:
        text = skill.read_text(encoding='utf-8')
        check(text.startswith('---\n'), f'Missing frontmatter: {skill}')
        check(re.search(r'^name:\s*' + re.escape(skill.parent.name) + r'\s*$', text, re.M), f'Name mismatch: {skill}')
        description(skill)
        for target in re.findall(r'`(references/[^`\n]+)`', text):
            if not any(char in target for char in '*<> ') and not target.endswith('/'):
                check((skill.parent / target).exists(), f'Missing bundled reference: {skill.parent.name}/{target}')
    for skill in blender_skills + ai_3d_skills:
        text = skill.read_text(encoding='utf-8')
        check(text.startswith('---\n'), f'Missing frontmatter: {skill}')
        check(re.search(r'^name:\s*' + re.escape(skill.parent.name) + r'\s*$', text, re.M), f'Name mismatch: {skill}')
        description(skill)
        for target in re.findall(r'`(references/[^`\n]+)`', text):
            if not any(char in target for char in '*<> ') and not target.endswith('/'):
                check((skill.parent / target).exists(), f'Missing bundled reference: {skill.parent.name}/{target}')
    for path in ROOT.rglob('*.json'):
        if '.git' not in path.parts and '.validation' not in path.parts:
            json.loads(path.read_text(encoding='utf-8'))
    for plugin in PACKAGED_PLUGINS:
        codex = json.loads((plugin / '.codex-plugin/plugin.json').read_text())
        claude = json.loads((plugin / '.claude-plugin/plugin.json').read_text())
        check(codex['name'] == claude['name'] == plugin.name, f'Plugin names disagree: {plugin.name}')
        check(codex['version'] == claude['version'], f'Plugin versions disagree: {plugin.name}')
    for rel in ['.agents/plugins/marketplace.json', '.claude-plugin/marketplace.json']:
        market = json.loads((ROOT / rel).read_text())
        entries = {entry['name']: entry for entry in market['plugins']}
        check(set(entries) == {plugin.name for plugin in PACKAGED_PLUGINS}, f'Marketplace entries disagree: {rel}')
        for plugin in PACKAGED_PLUGINS:
            source = entries[plugin.name]['source']
            target = source['path'] if isinstance(source, dict) else source
            check((ROOT / target).resolve() == plugin, f'Marketplace points elsewhere: {rel}/{plugin.name}')
    manifest_path = ROOT / 'docs/export-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    patterns = {
        'absolute user directory': r'[A-Za-z]:[\\/]+Users[\\/]',
        'GitHub token': r'gh[pousr]_[A-Za-z0-9]{25,}',
        'Google API key': r'AIza[0-9A-Za-z_-]{30,}',
        'private key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'live provider key': r'(?:sk|rk)_live_[A-Za-z0-9]{16,}',
        'JWT credential': r'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}',
    }
    for plugin in PACKAGED_PLUGINS:
        for path in plugin.rglob('*'):
            if path.is_file() and path.suffix in {'.json', '.md', '.py', '.yaml', '.yml'}:
                text = path.read_text(encoding='utf-8')
                for label, pattern in patterns.items():
                    check(not re.search(pattern, text), f'{label} detected in {path.relative_to(ROOT)}')
    seen = set()
    for item in manifest:
        path = (ROOT / item['path']).resolve()
        check(path.is_relative_to(ROOT) and path.is_file(), 'Manifest path missing or outside package')
        check(item['path'] not in seen, 'Duplicate manifest path')
        seen.add(item['path'])
        text = path.read_text(encoding='utf-8')
        for label, pattern in patterns.items():
            check(not re.search(pattern, text), f'{label} detected in {item["path"]}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if args.refresh:
            item['sha256'] = digest
        check(item['sha256'] == digest, f'Export hash changed: {item["path"]}; review then use --refresh')
    catalog = '# Skill catalog\n\n92 skills from the public v0.1.0 snapshot. Descriptions come from each skill\'s frontmatter. See [installation notes](INSTALLATION.md) for optional tools and project setup.\n\n| Skill | When to use it |\n| --- | --- |\n'
    for skill in skills:
        target = '../' + skill.relative_to(ROOT).as_posix()
        catalog += f'| [{skill.parent.name}]({target}) | {description(skill)} |\n'
    catalog += '\n## Command definitions\n\n[Browse all 93 command adapters](../commands). The plugin activates seven aliases; the remaining names are exposed by skills.\n'
    catalog_path = ROOT / 'docs/CATALOG.md'
    if args.refresh:
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
        catalog_path.write_text(catalog, encoding='utf-8', newline='\n')
    check(catalog_path.exists() and catalog_path.read_text(encoding='utf-8') == catalog, 'Catalog is stale; run --refresh')
    print(f'PASS: {len(skills)} core skills, {len(blender_skills)} Blender skills, {len(ai_3d_skills)} AI 3D skills, {len(commands)} commands, {len(aliases)} aliases, {len(agents)} roles, {len(manifest)} export hashes')


if __name__ == '__main__':
    main()
