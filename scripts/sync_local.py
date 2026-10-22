"""Merge the Agent Foundry skills into personal skill folders while keeping local edits.

Maintainer utility, the reverse of export_local.py. Each plugin skill is rendered in its
client form: Claude reads references/claude-skill.md as SKILL.md when one exists and
skips Codex agent metadata; Codex uses the folder as published. Every file is merged
three ways against the revision it was last synced from. Local-only files are never
removed, a conflicting file stays untouched until it is resolved by hand and marked
with --resolve, and nothing is written without --apply.
"""
import argparse
import difflib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = 'plugins/agent-foundry/skills'
CLIENTS = {'claude': '.claude/skills', 'codex': '.codex/skills'}
STATE_DIR = '.agent-context/agent-foundry-sync'
WRITES = {'add', 'fast-forward', 'clean-merge'}
SYNCED = WRITES | {'same', 'local-ahead', 'local-removed'}


def git(root, *args):
    run = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    return run.stdout.decode('utf-8') if run.returncode == 0 else None


def read(data):
    return data.decode('utf-8-sig').replace('\r\n', '\n')


def client_files(skill, client):
    """Map each personal file name to its repository path for one client."""
    claude_body = (skill / 'references/claude-skill.md').is_file()
    files = {}
    for path in sorted(skill.rglob('*')):
        name = path.relative_to(skill).as_posix()
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        if client == 'claude' and (name.startswith('agents/') or
                                   (claude_body and name in ('SKILL.md', 'references/claude-skill.md'))):
            continue
        files[name] = f'{SKILLS}/{skill.name}/{name}'
    if client == 'claude' and claude_body:
        files['SKILL.md'] = f'{SKILLS}/{skill.name}/references/claude-skill.md'
    return files


def merge3(local, base, plugin):
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for label, value in (('local', local), ('base', base), ('plugin', plugin)):
            path = Path(tmp) / label
            path.write_text(value, encoding='utf-8', newline='\n')
            paths.append(str(path))
        run = subprocess.run(['git', 'merge-file', '-p', '--diff3', '-L', 'local', '-L', 'base', '-L', 'plugin',
                              *paths], capture_output=True)
    if run.returncode >= 128:
        raise RuntimeError(run.stderr.decode('utf-8', 'replace').strip() or 'git merge-file failed')
    return settle(run.stdout.decode('utf-8'))


def already_local(hunk):
    """True when every plugin change in a conflict hunk is already in its local side."""
    matcher = difflib.SequenceMatcher(None, hunk['base'], hunk['plugin'], autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal' and (any(line not in hunk['local'] for line in hunk['plugin'][j1:j2]) or
                               any(line in hunk['local'] for line in hunk['base'][i1:i2])):
            return False
    return True


def settle(merged):
    """Keep the local side of hunks that only touch a plugin change local already made; count the rest."""
    out, left, hunk, part = [], 0, None, None
    for line in merged.split('\n'):
        if line.startswith('<<<<<<< local'):
            hunk, part = {'local': [], 'base': [], 'plugin': []}, 'local'
        elif hunk is not None and line.startswith('||||||| base'):
            part = 'base'
        elif hunk is not None and line == '=======':
            part = 'plugin'
        elif hunk is not None and line.startswith('>>>>>>> plugin'):
            if already_local(hunk):
                out += hunk['local']
            else:
                left += 1
                out += ['<<<<<<< local', *hunk['local'], '||||||| base', *hunk['base'], '=======',
                        *hunk['plugin'], '>>>>>>> plugin']
            hunk = None
        elif hunk is not None:
            hunk[part].append(line)
        else:
            out.append(line)
    return left, '\n'.join(out)


def plan(local, base, plugin, installed=True):
    """Return (outcome, content to write or stage) for one file."""
    if local is None:
        if base is None or not installed:
            return 'add', plugin
        return ('local-removed', None) if plugin == base else ('conflict', plugin)
    if local == plugin:
        return 'same', None
    if base is None:
        return 'conflict', plugin
    if local == base:
        return 'fast-forward', plugin
    if plugin == base:
        return 'local-ahead', None
    conflicts, merged = merge3(local, base, plugin)
    if conflicts:
        return 'conflict', merged
    return ('local-ahead', None) if merged == local else ('clean-merge', merged)


def load_state(path):
    if path.is_file():
        return json.loads(path.read_text(encoding='utf-8'))
    return {}


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    temporary.replace(path)


def run(root, home, clients, skills_filter, base_default, apply, pins, resolves, out=print):
    head = (git(root, 'rev-parse', 'HEAD') or '').strip()
    if not head:
        raise SystemExit(f'Not a git checkout: {root}')
    if apply and git(root, 'status', '--porcelain', '--', SKILLS):
        raise SystemExit(f'{SKILLS} has uncommitted changes; commit them before syncing.')
    state_path = home / STATE_DIR / 'state.json'
    state = load_state(state_path)
    for item in pins:
        client, _, skill = item.partition(':')
        state.setdefault('pinned', {}).setdefault(client, [])
        if skill not in state['pinned'][client]:
            state['pinned'][client].append(skill)
    for item in resolves:
        client, _, key = item.partition(':')
        if client not in CLIENTS or '/' not in key:
            raise SystemExit(f'Use --resolve <client>:<skill>/<file>, not {item}')
        state.setdefault(client, {})[key] = head
        staged = home / STATE_DIR / 'conflicts' / client / key
        if staged.is_file():
            staged.unlink()
    stamp = time.strftime('%Y%m%d-%H%M%S')
    totals, conflicts = {}, []
    plugin_root = root / SKILLS
    for client in clients:
        target = home / CLIENTS[client]
        pinned = set(state.get('pinned', {}).get(client, []))
        records = state.setdefault(client, {})
        counts = {}
        for skill in sorted(p for p in plugin_root.iterdir() if (p / 'SKILL.md').is_file()):
            if skills_filter and skill.name not in skills_filter:
                continue
            if skill.name in pinned:
                counts['pinned'] = counts.get('pinned', 0) + 1
                continue
            local_dir = target / skill.name
            writes = []
            for name, rel in client_files(skill, client).items():
                key = f'{skill.name}/{name}'
                plugin = read((root / rel).read_bytes())
                local_path = local_dir / name
                local_bytes = local_path.read_bytes() if local_path.is_file() else None
                local = read(local_bytes) if local_bytes is not None else None
                base_rev = records.get(key) or base_default
                if base_rev is None and local_dir.exists():
                    raise SystemExit(f'No recorded base for {client}:{key}; pass --base <rev> for the first sync.')
                base_text = git(root, 'show', f'{base_rev}:{rel}') if base_rev else None
                base = base_text.replace('\r\n', '\n').lstrip('﻿') if base_text is not None else None
                outcome, content = plan(local, base, plugin, local_dir.exists())
                counts[outcome] = counts.get(outcome, 0) + 1
                if outcome != 'same':
                    out(f'{client} {outcome:13} {key}')
                if outcome in WRITES:
                    crlf = local_bytes is not None and b'\r\n' in local_bytes
                    writes.append((local_path, content.replace('\n', '\r\n') if crlf else content))
                if outcome == 'conflict':
                    conflicts.append(f'{client}:{key}')
                    if apply:
                        staged = home / STATE_DIR / 'conflicts' / client / key
                        staged.parent.mkdir(parents=True, exist_ok=True)
                        staged.write_text(content, encoding='utf-8', newline='\n')
                elif apply and outcome in SYNCED:
                    records[key] = head
            if apply and writes:
                if local_dir.exists():
                    shutil.copytree(local_dir, home / STATE_DIR / 'backups' / stamp / client / skill.name,
                                    ignore=shutil.ignore_patterns('__pycache__'))
                for path, content in writes:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content.encode('utf-8'))
        totals[client] = counts
    if apply or pins or resolves:
        save_state(state_path, state)
    out(json.dumps({'revision': head[:12], 'applied': apply, 'totals': totals, 'conflicts': len(conflicts)}, indent=1))
    if conflicts:
        where = home / STATE_DIR / 'conflicts'
        out(f'Unresolved: merge each file by hand (markers staged under {where} after --apply), '
            'then mark it with --resolve <client>:<skill>/<file>.')
    return 1 if conflicts else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--client', action='append', choices=sorted(CLIENTS), help='Default: both clients')
    parser.add_argument('--skill', action='append', default=[], help='Limit the run to these skills')
    parser.add_argument('--base', help='Revision personal copies were last synced from, for files with no record')
    parser.add_argument('--apply', action='store_true', help='Write merges, back up touched skills, record bases')
    parser.add_argument('--pin', action='append', default=[], help='<client>:<skill> kept local-only, never synced')
    parser.add_argument('--resolve', action='append', default=[],
                        help='<client>:<skill>/<file> already merged by hand; record the current revision')
    args = parser.parse_args()
    clients = args.client or sorted(CLIENTS)
    sys.exit(run(ROOT, args.home.resolve(), clients, set(args.skill), args.base, args.apply, args.pin, args.resolve))


if __name__ == '__main__':
    main()
