import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class InstallTests(unittest.TestCase):
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
