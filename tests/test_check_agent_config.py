import os
from pathlib import Path
import subprocess
import tempfile
import unittest


CHECKER = Path(__file__).resolve().parents[1] / 'bin/check-agent-config'


class SkillInstallationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)

    def skill(self, directory, name, content='skill'):
        path = self.home / directory / name / 'SKILL.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def check(self):
        return subprocess.run(
            ['python3', str(CHECKER)], env=dict(os.environ, HOME=str(self.home)),
            capture_output=True, text=True,
        )

    def test_client_specific_skills_are_not_drift(self):
        self.skill('best/dotfiles/claude/skills', 'claude-only')
        self.skill('.claude/skills', 'claude-only')
        self.skill('best/dotfiles/codex/skills', 'codex-only')
        for root in ('.agents/skills', '.codex/skills'):
            self.skill(root, 'codex-only')
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('DRIFT', result.stdout)
        self.assertNotIn('UNMANAGED', result.stdout)

    def test_missing_installations_fail_for_each_registry(self):
        self.skill('best/dotfiles/claude/skills', 'claude-only')
        self.skill('best/dotfiles/codex/skills', 'codex-only')
        self.skill('.agents/skills', 'codex-only')
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('missing tracked skill claude-only', result.stdout)
        self.assertIn('~/.codex/skills', result.stdout)
        self.assertNotIn('~/.agents/skills', result.stdout)

    def test_one_correct_codex_copy_does_not_hide_other_copy_drift(self):
        self.skill('best/dotfiles/codex/skills', 'shared')
        self.skill('.agents/skills', 'shared')
        self.skill('.codex/skills', 'shared', 'stale')
        self.skill('.claude/skills', 'external')
        result = self.check()
        self.assertEqual(result.returncode, 0)
        self.assertIn('~/.codex/skills: shared: installed SKILL.md differs', result.stdout)
        self.assertIn('UNMANAGED', result.stdout)
        self.assertIn('~/.claude/skills: external', result.stdout)

    def test_broken_source_links_fail_even_without_installed_copy(self):
        source = self.home / 'best/dotfiles/claude/skills'
        source.mkdir(parents=True)
        (source / 'broken').symlink_to(self.home / 'missing')
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('dangling symlink', result.stdout)

    def test_private_compatibility_lists_are_optional_and_checked(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.skill('best/dotfiles/private-skills/claude/skills', 'private-only')
        self.skill('.claude/skills', 'private-only')
        self.skill('best/dotfiles/private-skills/codex/skills', 'private-shared')
        self.skill('.agents/skills', 'private-shared')
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('~/.codex/skills: missing tracked skill private-shared', result.stdout)
        self.assertNotIn('UNMANAGED', result.stdout)
        self.skill('.codex/skills', 'private-shared')
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('DRIFT', result.stdout)

    def test_public_and_private_name_collision_is_reported(self):
        self.skill('best/dotfiles/claude/skills', 'same')
        self.skill('best/dotfiles/private-skills/claude/skills', 'same')
        self.skill('.claude/skills', 'same')
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('duplicate source for tracked skill same', result.stdout)


if __name__ == '__main__':
    unittest.main()
