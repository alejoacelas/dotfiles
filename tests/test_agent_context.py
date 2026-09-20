import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import contextlib
import io
import json
import os
import subprocess
import time

script = Path(__file__).resolve().parents[1] / 'bin/agent-context'
loader = importlib.machinery.SourceFileLoader('context', str(script))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)

class ContextTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.dotfiles = self.root / 'dotfiles'
        self.groups = self.dotfiles / 'agents/groups'
        self.private = self.root / '.local/share/agent-context/private'
        self.groups.mkdir(parents=True)
        (self.private / 'groups').mkdir(parents=True)
        (self.groups / 'tools.md').write_text('Shared tools instruction.\n')
        self.project = self.root / 'project'
        self.project.mkdir()
        self.path = self.project / 'AGENTS.md'
        self.path.write_text('# Mine\n\nExact  spacing.\n')
        for patcher in (patch.object(m, 'DOTFILES', self.dotfiles),
                        patch.object(Path, 'home', return_value=self.root),
                        patch.dict(os.environ, {'HOME': str(self.root)}),
                        patch.object(m, 'STATE', self.root / '.state')):
            patcher.start()
            self.addCleanup(patcher.stop)

    def register(self, groups=None, visibility='public'):
        m.adopt(self.path, ['tools'] if groups is None else groups, visibility)

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}

    def hook(self, source='startup', cwd=None):
        output = io.StringIO()
        payload = {'cwd': str(cwd or self.project),
                   'hook_event_name': 'SessionStart', 'source': source}
        with patch('sys.argv', ['agent-context', 'hook']), \
             patch('sys.stdin', io.StringIO(json.dumps(payload))), \
             contextlib.redirect_stdout(output):
            result = m.main()
        self.assertEqual(0, result)
        return json.loads(output.getvalue()) if output.getvalue().strip() else {}

    def test_registration_is_external_and_removal_preserves_project(self):
        before = self.path.read_bytes()
        self.register()
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual({'groups': ['tools'], 'visibility': 'public'},
                         m.load_projects()[self.project])
        self.assertTrue((self.dotfiles / 'agents/projects.json').is_file())
        self.register([])
        self.assertNotIn(self.project, m.load_projects())
        self.assertEqual(before, self.path.read_bytes())

    def test_only_selected_sources_are_injected_in_order(self):
        (self.groups / 'other.md').write_text('Selected second instruction.\n')
        (self.groups / 'unused.md').write_text('DO NOT LOAD THIS.\n')
        (self.root / 'AGENTS.md').write_text('UNSELECTED PARENT.\n')
        self.register(['tools', 'other'])
        context = m.shared_context(self.project)
        self.assertLess(context.index('Shared tools instruction.'),
                        context.index('Selected second instruction.'))
        self.assertNotIn('DO NOT LOAD THIS', context)
        self.assertNotIn('UNSELECTED PARENT', context)
        self.assertNotIn('Exact  spacing.', context)
        self.assertIn('tools.md', context)

    def test_unregistered_project_does_not_read_parent_agents(self):
        (self.root / 'AGENTS.md').write_text('Never selected.\n')
        self.assertEqual('', m.shared_context(self.project))
        self.assertFalse(self.hook().get('hookSpecificOutput', {}).get('additionalContext'))

    def test_nested_directories_and_repository_boundary(self):
        self.register()
        nested = self.project / 'src/package'
        nested.mkdir(parents=True)
        self.assertEqual(self.project, m.locate(nested, m.load_projects()))
        (self.project / 'src/.git').mkdir()
        self.assertIsNone(m.locate(nested, m.load_projects()))
        self.assertEqual('', m.shared_context(nested))

    def test_archives_and_fixtures_do_not_inherit_registration(self):
        self.register()
        for directory in ('archive', 'archives', 'fixtures', 'test-fixtures', 'vendor', 'node_modules'):
            with self.subTest(directory=directory):
                child = self.project / directory / 'example'
                child.mkdir(parents=True)
                self.assertEqual('', m.shared_context(child))

    def test_hook_lifecycle_is_read_only_and_source_changes_are_immediate(self):
        self.register()
        for source in ('startup', 'resume', 'clear', 'compact'):
            with self.subTest(source=source):
                before = self.snapshot()
                output = self.hook(source)
                specific = output['hookSpecificOutput']
                self.assertEqual('SessionStart', specific['hookEventName'])
                self.assertIn('Shared tools instruction.', specific['additionalContext'])
                self.assertEqual(before, self.snapshot())
        (self.groups / 'tools.md').write_text('Fresh instruction.\n')
        context = self.hook('compact')['hookSpecificOutput']['additionalContext']
        self.assertIn('Fresh instruction.', context)
        self.assertNotIn('Shared tools instruction.', context)
        self.assertNotIn('agent-context:begin', self.path.read_text())

    def test_check_prints_current_context_without_writes(self):
        self.register()
        before = self.snapshot()
        output = io.StringIO()
        with patch('sys.argv', ['agent-context', 'check', str(self.path)]), \
             contextlib.redirect_stdout(output):
            self.assertEqual(0, m.main())
        self.assertIn('Shared tools instruction.', output.getvalue())
        self.assertEqual(before, self.snapshot())

    def test_private_source_cannot_enter_public_registry(self):
        (self.private / 'groups/employer.md').write_text('Private employer instruction.\n')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            self.register(['employer'])
        self.assertEqual(before, self.snapshot())
        self.register(['employer'], 'private')
        self.assertIn('Private employer instruction.', m.shared_context(self.project))
        self.assertTrue((self.private / 'projects.json').is_file())
        self.assertEqual('private', m.load_projects()[self.project]['visibility'])
        public = self.dotfiles / 'agents/projects.json'
        self.assertNotIn('employer', public.read_text() if public.exists() else '')

    def test_invalid_registration_does_not_change_files(self):
        (self.private / 'groups/tools.md').write_text('Ambiguous tools source.\n')
        for groups in (['missing'], ['tools'], ['tools', 'tools'], ['../secret']):
            with self.subTest(groups=groups):
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.register(groups)
                self.assertEqual(before, self.snapshot())

    def test_deleted_or_oversized_source_fails_visibly(self):
        self.register()
        source = self.groups / 'tools.md'
        source.unlink()
        with self.assertRaises(ValueError):
            m.shared_context(self.project)
        source.write_text('x' * (25 * 1024))
        with self.assertRaises(ValueError):
            m.shared_context(self.project)

    def test_registry_rejects_malformed_configuration(self):
        registry = self.dotfiles / 'agents/projects.json'
        bad = [
            {'version': 2, 'projects': {}},
            {'version': 1, 'projects': {str(self.project): {'groups': ['tools', 'tools'], 'visibility': 'public'}}},
            {'version': 1, 'projects': {str(self.project): {'groups': ['tools'], 'visibility': 'unknown'}}},
        ]
        for data in bad:
            with self.subTest(data=data):
                registry.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    m.load_projects()

    def test_claude_local_only_instructions_do_not_cross_project_boundaries(self):
        parent = self.root / 'AGENTS.md'
        parent.write_text('Container-only instruction.\n')
        registry = self.dotfiles / 'agents/projects.json'
        registry.write_text(json.dumps({'version': 1, 'projects': {},
                                       'local_only': [str(parent), str(self.path)]}))
        self.assertIn('Container-only instruction.', m.local_context(self.root))
        self.assertIn('Exact  spacing.', m.local_context(self.project))
        self.assertNotIn('Container-only instruction.', m.local_context(self.project))
        (self.project / '.git').mkdir()
        nested = self.project / 'src'
        nested.mkdir()
        self.assertIn('Exact  spacing.', m.local_context(nested))
        self.assertNotIn('Container-only instruction.', m.local_context(nested))
        (nested / '.git').mkdir()
        self.assertEqual('', m.local_context(nested))

    def test_claude_exclusions_reconcile_owned_paths_and_symlink_targets(self):
        link = self.root / 'AGENTS.md'
        link.symlink_to(self.path)
        registry = self.dotfiles / 'agents/projects.json'
        def select(*paths):
            registry.write_text(json.dumps({'version': 1, 'projects': {},
                                           'local_only': [str(p) for p in paths]}))
        target = self.root / '.claude/settings.json'
        independent = '/independent/**/AGENTS.md'
        data = {'claudeMdExcludes': [independent, str(link)], 'unrelated': True}
        select(link)
        state, owned = m.claude_exclusions(data, target)
        self.assertEqual([independent, str(link), str(self.path)], data['claudeMdExcludes'])
        self.assertEqual([str(link), str(self.path)], owned)
        self.assertTrue(data['unrelated'])
        self.assertFalse(state.exists())  # Installer persists ownership only after settings succeed.
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(owned))
        again = dict(data)
        self.assertEqual((state, owned), m.claude_exclusions(data, target))
        self.assertEqual(again, data)
        replacement = self.root / 'replacement/AGENTS.md'
        select(replacement)
        returned_state, new_owned = m.claude_exclusions(data, target)
        self.assertEqual(state, returned_state)
        self.assertEqual([independent, str(replacement)], data['claudeMdExcludes'])
        self.assertEqual([str(replacement)], new_owned)
        state.write_text(json.dumps(new_owned))
        select()
        self.assertEqual((state, []), m.claude_exclusions(data, target))
        self.assertEqual([independent], data['claudeMdExcludes'])

    def test_claude_exclusions_preserve_independent_path_when_it_becomes_selected(self):
        registry = self.dotfiles / 'agents/projects.json'
        registry.write_text(json.dumps({'version': 1, 'projects': {}, 'local_only': []}))
        target = self.root / '.claude/settings.json'
        data = {'claudeMdExcludes': [str(self.path)]}
        state, owned = m.claude_exclusions(data, target)
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(owned))
        registry.write_text(json.dumps({'version': 1, 'projects': {},
                                       'local_only': [str(self.path)]}))
        self.assertEqual((state, []), m.claude_exclusions(data, target))
        registry.write_text(json.dumps({'version': 1, 'projects': {}, 'local_only': []}))
        self.assertEqual((state, []), m.claude_exclusions(data, target))
        self.assertEqual([str(self.path)], data['claudeMdExcludes'])

    def test_linked_worktree_uses_registered_main_repository(self):
        def git(*args):
            subprocess.run(['git', '-C', str(self.project), *args], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        git('init')
        git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
            'commit', '--allow-empty', '-m', 'Initial')
        self.register()
        worktree = self.root / 'worktree'
        git('worktree', 'add', '--detach', str(worktree))
        self.assertIn('Shared tools instruction.', m.shared_context(worktree))

class LiveProjectTest(unittest.TestCase):
    def test_edit_age_scope_and_notice_only_for_both_clients(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            project = root / 'projects/live/example'
            project.mkdir(parents=True)
            draft = project / 'draft.md'
            draft.write_text('Uncommitted work.\n')
            edited = draft.stat().st_mtime
            (project.parent / 'linked').symlink_to(project, target_is_directory=True)
            (project.parent / '.hidden').mkdir()
            (project.parent / 'notes.txt').write_text('Not a project.')
            expected = 'Project live/example has not been edited in 14 days.'
            with patch.object(m, 'DOTFILES', root / 'dotfiles'), \
                 patch.object(m, 'STATE', root / '.state'):
                with patch.object(m.time, 'time', return_value=edited + 14 * 86400 - 1):
                    self.assertEqual('', m.live_project_reminder(project))
                with patch.object(m.time, 'time', return_value=edited + 14 * 86400):
                    self.assertEqual(expected, m.live_project_reminder(project))
                    self.assertEqual(expected, m.live_project_reminder(root))
                    self.assertEqual('', m.live_project_reminder(root / 'writing'))
                    for client in ('codex', 'claude'):
                        output = io.StringIO()
                        with patch('sys.argv', ['agent-context', 'hook', '--client', client]), \
                             patch('sys.stdin', io.StringIO(json.dumps({'cwd': str(root)}))), \
                             contextlib.redirect_stdout(output):
                            self.assertEqual(0, m.main())
                        self.assertEqual(expected, json.loads(output.getvalue())[
                            'hookSpecificOutput']['additionalContext'])
                    self.assertEqual('Uncommitted work.\n', draft.read_text())
                    self.assertFalse((project / '.git').exists())
                    self.assertFalse((root / '.state').exists())
                    os.utime(draft, (edited + 86400, edited + 86400))
                    self.assertEqual('', m.live_project_reminder(project))
                    os.utime(draft, (edited, edited))
                    # Git metadata and ignored outputs do not count as project edits.
                    subprocess.run(['git', 'init', str(project)], check=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    ignore = project / '.gitignore'
                    ignore.write_text('cache/\n')
                    os.utime(ignore, (edited, edited))
                    (project / 'cache').mkdir()
                    (project / 'cache/output.txt').write_text('Generated.')
                    self.assertEqual(expected, m.live_project_reminder(project))
                    subprocess.run(['git', '-C', str(project), 'add', 'draft.md'], check=True)
                    self.assertEqual(expected, m.live_project_reminder(project))
                    os.utime(draft, (edited + 86400, edited + 86400))
                    self.assertEqual('', m.live_project_reminder(project))


if __name__ == '__main__': unittest.main()
