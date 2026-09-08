import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import contextlib
import io
import json

script = Path(__file__).resolve().parents[1] / 'bin/agent-context'
loader = importlib.machinery.SourceFileLoader('context', str(script))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)

class ContextTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.previous = m.DOTFILES
        m.DOTFILES = self.root / 'dotfiles'
        self.groups = m.DOTFILES / 'agents/groups'
        self.groups.mkdir(parents=True)
        (self.groups / 'tools.md').write_text('Shared text.\n')
        self.project = self.root / 'project'
        self.project.mkdir()
        self.path = self.project / 'AGENTS.md'
        self.local = '# Mine\n\nExact  spacing.\n'
        self.path.write_text(self.local)
    def tearDown(self):
        m.DOTFILES = self.previous
        self.tmp.cleanup()
    def adopt(self):
        m.adopt(self.path, ['tools'], 'public')
    def test_adopt_preserves_local_text(self):
        self.adopt()
        self.assertTrue(self.path.read_text().endswith(self.local))
    def test_source_change_and_idempotence(self):
        self.adopt()
        (self.groups / 'tools.md').write_text('New shared text.\n')
        self.assertTrue(m.sync_project(self.path)[0])
        self.assertFalse(m.sync_project(self.path)[0])
    def test_local_edit_survives(self):
        self.adopt()
        self.path.write_text(self.path.read_text() + 'Handwritten addition.\n')
        (self.groups / 'tools.md').write_text('Updated.\n')
        m.sync_project(self.path)
        self.assertTrue(self.path.read_text().endswith('Handwritten addition.\n'))
    def test_generated_edit_blocks_overwrite(self):
        self.adopt()
        self.path.write_text(self.path.read_text().replace('Shared text.', 'My edit.'))
        before = self.path.read_text()
        with self.assertRaisesRegex(ValueError, 'was edited'): m.sync_project(self.path)
        self.assertEqual(before, self.path.read_text())
    def test_missing_source_leaves_file_untouched(self):
        before = self.path.read_text()
        with self.assertRaisesRegex(ValueError, 'requires a private project'): m.adopt(self.path, ['missing'], 'public')
        self.assertEqual(before, self.path.read_text())
    def test_move_does_not_change_subscription(self):
        self.adopt()
        moved = self.root / 'moved'
        self.project.rename(moved)
        (self.groups / 'tools.md').write_text('After move.\n')
        m.sync_project(moved / 'AGENTS.md')
        self.assertIn('After move.', (moved / 'AGENTS.md').read_text())
    def test_check_does_not_write(self):
        self.adopt()
        before = self.path.read_text()
        (self.groups / 'tools.md').write_text('After.\n')
        self.assertTrue(m.sync_project(self.path, check=True)[0])
        self.assertEqual(before, self.path.read_text())
    def test_invalid_yaml_fails(self):
        self.path.write_text('---\nagent_context: [\n---\n')
        with self.assertRaises(Exception): m.sync_project(self.path)
    def test_symlink_is_not_overwritten(self):
        real = self.project / 'real.md'
        self.path.rename(real)
        self.path.symlink_to(real)
        with self.assertRaisesRegex(ValueError, 'symlink'): self.adopt()
        self.assertEqual(self.local, real.read_text())
    def test_compare_before_replace(self):
        before = self.path.read_text()
        self.path.write_text('Another writer.\n')
        with self.assertRaisesRegex(ValueError, 'changed during sync'): m.atomic(self.path, 'lost', before)
        self.assertEqual('Another writer.\n', self.path.read_text())
    def test_group_order(self):
        (self.groups / 'other.md').write_text('Second.\n')
        m.adopt(self.path, ['tools', 'other'], 'public')
        text = self.path.read_text()
        self.assertLess(text.index('Shared text.'), text.index('Second.'))
    def test_private_cannot_enter_public_project(self):
        self.adopt()
        before = self.path.read_text()
        (self.groups / 'tools.md').rename(self.groups / 'saved.md')
        with self.assertRaisesRegex(ValueError, 'requires a private project'): m.sync_project(self.path)
        self.assertEqual(before, self.path.read_text())

class HookTest(unittest.TestCase):
    def test_hook_does_not_track_marked_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'AGENTS.md'
            path.write_text('Handwritten ;;\n')
            m.adopt(path, [], 'public')
            before = path.read_text()
            output = io.StringIO()
            payload = json.dumps({'cwd': str(root), 'hook_event_name': 'SessionStart'})
            with patch.object(m, 'STATE', root / '.state'), \
                 patch('sys.argv', ['agent-context', 'hook']), \
                 patch('sys.stdin', io.StringIO(payload)), contextlib.redirect_stdout(output):
                self.assertEqual(0, m.main())
            context = json.loads(output.getvalue())['hookSpecificOutput']['additionalContext']
            self.assertIn('Current shared instructions', context)
            self.assertNotIn('human_edit_history', context)
            self.assertNotIn('human-edit-tracking', context)
            self.assertFalse((root / '.agent-history').exists())
            self.assertFalse((root / '.state/snapshots').exists())
            self.assertEqual(before, path.read_text())

    def test_existing_private_source_is_refused_in_public(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private = root / '.local/share/agent-context/private/groups'
            private.mkdir(parents=True)
            (private / 'employer.md').write_text('Employer-only wording.\n')
            project = root / 'project'
            project.mkdir()
            path = project / 'AGENTS.md'
            path.write_text('Mine.\n')
            with patch.object(Path, 'home', return_value=root):
                with self.assertRaisesRegex(ValueError, 'private group'):
                    m.adopt(path, ['employer'], 'public')
                self.assertEqual('Mine.\n', path.read_text())
                m.adopt(path, ['employer'], 'private')
                self.assertIn('Employer-only wording.', path.read_text())

if __name__ == '__main__': unittest.main()
