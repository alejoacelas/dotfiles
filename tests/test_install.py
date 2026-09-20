import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class InstallTests(unittest.TestCase):
    def test_optional_private_skills_install_for_selected_clients(self):
        source = Path(__file__).resolve().parents[1] / 'bin/install.sh'
        phase = source.read_text().split('# The app owns config.toml;')[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            repo = root / 'dotfiles'
            (repo / 'bin').mkdir(parents=True)
            (repo / 'agents').mkdir()
            (repo / 'agents/AGENTS.md').write_text('Instructions')
            (repo / 'codex/rules').mkdir(parents=True)
            (repo / 'codex/hooks.json').write_text('{}')
            script = repo / 'bin/install.sh'
            script.write_text(phase.replace('$HOME', '$TEST_HOME'))
            home = root / 'home'
            env = dict(os.environ, TEST_HOME=str(home))
            result = subprocess.run(['bash', str(script)], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            private = repo / 'private-skills'
            for name in ('shared', 'claude-only'):
                skill = private / 'claude/skills' / name
                skill.mkdir(parents=True)
                (skill / 'SKILL.md').write_text(name)
            (private / 'codex/skills').mkdir(parents=True)
            (private / 'codex/skills/shared').symlink_to('../../claude/skills/shared')
            for _ in range(2):
                result = subprocess.run(['bash', str(script)], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                for client in ('.claude', '.agents', '.codex'):
                    self.assertEqual((home / client / 'skills/shared').resolve(),
                                     private / 'claude/skills/shared')
                self.assertTrue((home / '.claude/skills/claude-only').is_symlink())
                self.assertFalse((home / '.codex/skills/claude-only').exists())
                self.assertFalse((home / '.agents/skills/claude-only').exists())

    def test_prunes_retired_skills_before_checking_external_links(self):
        source = Path(__file__).resolve().parents[1] / 'bin/install.sh'
        # Run the actual Claude installation phase in an isolated directory.
        phase = source.read_text().split('# Both tools read the same canonical agent instructions.')[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            repo = root / 'dotfiles'
            (repo / 'bin').mkdir(parents=True)
            (repo / 'agents').mkdir()
            (repo / 'agents/AGENTS.md').write_text('Instructions')
            skill = repo / 'claude/skills/current'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('Current skill')
            script = repo / 'bin/install.sh'
            script.write_text(phase.replace('$HOME', '$TEST_HOME'))
            home = root / 'home'
            registry = home / '.claude/skills'
            registry.mkdir(parents=True)
            retired = registry / 'retired'
            retired.symlink_to(repo / 'claude/skills/retired')
            external = root / 'external'
            external.mkdir()
            (registry / 'external').symlink_to(external)
            env = dict(os.environ, TEST_HOME=str(home))
            result = subprocess.run(['bash', str(script)], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(retired.is_symlink())
            self.assertEqual((registry / 'current').resolve(), skill)
            self.assertEqual((registry / 'external').resolve(), external)
            broken = registry / 'broken-external'
            broken.symlink_to(root / 'missing-external')
            result = subprocess.run(['bash', str(script)], env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('broken-external', result.stderr)
            self.assertTrue(broken.is_symlink())

    def test_workspace_tree_maps_to_live_paths_and_preserves_existing_files(self):
        import shutil
        source = Path(__file__).resolve().parents[1]
        installer = (source / 'bin/install.sh').read_text()
        functions = installer.split('echo "Linking dotfiles')[0]
        phase = installer.split('# Ordinary container configuration lives here;')[1]
        phase = phase.split('if [ -d "$HOME/.local/share/agent-context/private/workspace/once/.agents"')[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            repo = root / 'dotfiles'
            shutil.copytree(source / 'workspace', repo / 'workspace')
            (repo / 'DECISIONS.md').write_text('Current decisions')
            (repo / 'bin').mkdir()
            script = repo / 'bin/install.sh'
            script.write_text((functions + '\n# Ordinary container configuration lives here;' + phase)
                              .replace('$HOME', '$TEST_HOME'))
            home = root / 'home'
            best = home / 'best'
            best.mkdir(parents=True)
            (best / 'README.md').write_text('Existing local file')
            env = dict(os.environ, TEST_HOME=str(home))
            for _ in range(2):
                result = subprocess.run(['bash', str(script)], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((best / 'DECISIONS.md').resolve(), repo / 'DECISIONS.md')
                for file in (repo / 'workspace').rglob('*'):
                    if file.is_file():
                        live = best / file.relative_to(repo / 'workspace')
                        self.assertTrue(live.is_symlink(), live)
                        self.assertEqual(live.resolve(), file)
            backups = list(best.glob('README.md.pre-symlink.*'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), 'Existing local file')
