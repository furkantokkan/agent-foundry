"""Tests for sync_local.py against a throwaway git repository and home folder."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_local  # noqa: E402

LINES = ''.join(f'line {n}\n' for n in range(1, 9))
ALPHA = f'---\nname: alpha\ndescription: Alpha.\n---\n{LINES}'
BETA_WRAPPER = '---\nname: beta\ndescription: Beta.\n---\nCodex port.\n'
BETA_CLAUDE = f'---\nname: beta\ndescription: Beta.\nallowed-tools: Read\n---\n{LINES}'


def quiet(*_):
    pass


class SyncLocalTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.repo, self.home = base / 'repo', base / 'home'
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        self.base = self.commit({
            'alpha/SKILL.md': ALPHA,
            'beta/SKILL.md': BETA_WRAPPER,
            'beta/references/claude-skill.md': BETA_CLAUDE,
            'beta/agents/openai.yaml': 'interface: {}\n',
        })
        self.write_local('codex', 'alpha/SKILL.md', ALPHA)
        self.write_local('claude', 'alpha/SKILL.md', ALPHA)

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, files):
        for rel, text in files.items():
            path = self.repo / sync_local.SKILLS / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')
        subprocess.run(['git', '-C', str(self.repo), 'add', '-A'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=test', '-c', 'user.email=test@example.com',
                        'commit', '-qm', 'update'], check=True)
        return sync_local.git(self.repo, 'rev-parse', 'HEAD').strip()

    def local(self, client, rel):
        return self.home / sync_local.CLIENTS[client] / rel

    def write_local(self, client, rel, text, newline='\n'):
        path = self.local(client, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline=newline)

    def sync(self, clients=('codex',), apply=True, pins=(), resolves=(), base='use-base'):
        return sync_local.run(self.repo, self.home, list(clients), set(), self.base if base == 'use-base' else base,
                              apply, list(pins), list(resolves), out=quiet)

    def state(self):
        return json.loads((self.home / sync_local.STATE_DIR / 'state.json').read_text(encoding='utf-8'))

    def test_dry_run_writes_nothing(self):
        self.commit({'alpha/SKILL.md': ALPHA.replace('line 2', 'line two')})
        self.assertEqual(self.sync(apply=False), 0)
        self.assertEqual(self.local('codex', 'alpha/SKILL.md').read_text(encoding='utf-8'), ALPHA)
        self.assertFalse((self.home / sync_local.STATE_DIR).exists())

    def test_unchanged_local_copy_fast_forwards_and_new_files_are_added(self):
        head = self.commit({'alpha/SKILL.md': ALPHA.replace('line 2', 'line two'),
                            'alpha/references/extra.md': 'extra\n'})
        self.assertEqual(self.sync(), 0)
        self.assertIn('line two', self.local('codex', 'alpha/SKILL.md').read_text(encoding='utf-8'))
        self.assertEqual(self.local('codex', 'alpha/references/extra.md').read_text(encoding='utf-8'), 'extra\n')
        self.assertEqual(self.state()['codex']['alpha/SKILL.md'], head)
        backups = list((self.home / sync_local.STATE_DIR / 'backups').glob('*/codex/alpha/SKILL.md'))
        self.assertEqual(backups[0].read_text(encoding='utf-8'), ALPHA)

    def test_local_edit_is_kept_and_merged_with_a_separate_plugin_edit(self):
        self.write_local('codex', 'alpha/SKILL.md', ALPHA.replace('line 1', 'local line 1'))
        self.commit({'alpha/SKILL.md': ALPHA.replace('line 7', 'plugin line 7')})
        self.assertEqual(self.sync(), 0)
        text = self.local('codex', 'alpha/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('local line 1', text)
        self.assertIn('plugin line 7', text)

    def test_local_only_edit_and_local_only_file_survive(self):
        edited = ALPHA.replace('line 4', 'local line 4')
        self.write_local('codex', 'alpha/SKILL.md', edited)
        self.write_local('codex', 'alpha/scripts/local.ps1', 'Write-Output 1\n')
        self.commit({'beta/SKILL.md': BETA_WRAPPER + 'More.\n'})
        self.assertEqual(self.sync(), 0)
        self.assertEqual(self.local('codex', 'alpha/SKILL.md').read_text(encoding='utf-8'), edited)
        self.assertTrue(self.local('codex', 'alpha/scripts/local.ps1').is_file())

    def test_conflict_stays_untouched_until_resolved(self):
        edited = ALPHA.replace('line 3', 'local line 3')
        self.write_local('codex', 'alpha/SKILL.md', edited)
        head = self.commit({'alpha/SKILL.md': ALPHA.replace('line 3', 'plugin line 3')})
        self.assertEqual(self.sync(), 1)
        self.assertEqual(self.local('codex', 'alpha/SKILL.md').read_text(encoding='utf-8'), edited)
        staged = self.home / sync_local.STATE_DIR / 'conflicts/codex/alpha/SKILL.md'
        self.assertIn('<<<<<<< local', staged.read_text(encoding='utf-8'))
        self.assertNotIn('alpha/SKILL.md', self.state()['codex'])
        self.assertEqual(self.sync(resolves=['codex:alpha/SKILL.md']), 0)
        self.assertEqual(self.state()['codex']['alpha/SKILL.md'], head)
        self.assertFalse(staged.exists())

    def test_plugin_change_already_made_next_to_a_local_edit_is_not_a_conflict(self):
        front = '---\nname: gamma\nmodel: sonnet\ndescription: Old.\n---\n' + LINES
        self.base = self.commit({'gamma/SKILL.md': front})
        local = front.replace('model: sonnet\ndescription: Old.', 'model: inherit\neffort: high\ndescription: New.')
        self.write_local('codex', 'gamma/SKILL.md', local)
        self.commit({'gamma/SKILL.md': front.replace('Old.', 'New.')})
        self.assertEqual(self.sync(), 0)
        self.assertEqual(self.local('codex', 'gamma/SKILL.md').read_text(encoding='utf-8'), local)
        self.assertFalse(list((self.home / sync_local.STATE_DIR / 'backups').glob('*/codex/gamma')))

    def test_different_plugin_change_next_to_a_local_edit_still_conflicts(self):
        front = '---\nname: gamma\nmodel: sonnet\ndescription: Old.\n---\n' + LINES
        self.base = self.commit({'gamma/SKILL.md': front})
        local = front.replace('model: sonnet\ndescription: Old.', 'model: inherit\ndescription: Local.')
        self.write_local('codex', 'gamma/SKILL.md', local)
        self.commit({'gamma/SKILL.md': front.replace('Old.', 'Plugin.')})
        self.assertEqual(self.sync(), 1)
        self.assertEqual(self.local('codex', 'gamma/SKILL.md').read_text(encoding='utf-8'), local)

    def test_claude_reads_the_claude_body_and_skips_codex_metadata(self):
        self.assertEqual(self.sync(clients=('claude', 'codex')), 0)
        self.assertEqual(self.local('claude', 'beta/SKILL.md').read_text(encoding='utf-8'), BETA_CLAUDE)
        self.assertFalse(self.local('claude', 'beta/agents').exists())
        self.assertFalse(self.local('claude', 'beta/references/claude-skill.md').exists())
        self.assertEqual(self.local('codex', 'beta/SKILL.md').read_text(encoding='utf-8'), BETA_WRAPPER)
        self.assertTrue(self.local('codex', 'beta/agents/openai.yaml').is_file())

    def test_crlf_copy_keeps_its_line_endings(self):
        self.write_local('codex', 'alpha/SKILL.md', ALPHA, newline='\r\n')
        self.commit({'alpha/SKILL.md': ALPHA.replace('line 2', 'line two')})
        self.assertEqual(self.sync(), 0)
        data = self.local('codex', 'alpha/SKILL.md').read_bytes()
        self.assertIn(b'line two\r\n', data)
        self.assertNotIn(b'\n', data.replace(b'\r\n', b''))

    def test_pinned_skill_is_never_synced(self):
        self.commit({'alpha/SKILL.md': ALPHA.replace('line 2', 'line two')})
        self.assertEqual(self.sync(pins=['codex:alpha']), 0)
        self.assertEqual(self.local('codex', 'alpha/SKILL.md').read_text(encoding='utf-8'), ALPHA)

    def test_first_sync_of_existing_copies_requires_a_base(self):
        with self.assertRaises(SystemExit):
            self.sync(base=None)

    def test_apply_refuses_uncommitted_plugin_changes(self):
        (self.repo / sync_local.SKILLS / 'alpha/SKILL.md').write_text('dirty\n', encoding='utf-8')
        with self.assertRaises(SystemExit):
            self.sync()


if __name__ == '__main__':
    unittest.main()
