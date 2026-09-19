import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class ProjectSkillSyncTests(unittest.TestCase):
    def test_selection_drift_and_private_runtime_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "dotfiles/bin/sync-project-skills"
            script.parent.mkdir(parents=True)
            shutil.copy(Path(__file__).resolve().parents[1] / "bin/sync-project-skills", script)
            source = root / "dotfiles/plugins/calls/skills"
            for skill in ("call-wiki", "wiki-comments", "summarize-call"):
                folder = source / skill
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text("original")
            for project in ("calls", "writing/ai-guides"):
                (root / project / ".git").mkdir(parents=True)
            def run(*args):
                return subprocess.run(["bash", str(script), *args], capture_output=True, text=True)
            self.assertNotEqual(run("--check").returncode, 0)
            self.assertEqual(run().returncode, 0)
            self.assertEqual(run("--check").returncode, 0)
            guides = root / "writing/ai-guides/.claude/skills"
            self.assertEqual({p.name for p in guides.iterdir()}, {"call-wiki", "wiki-comments"})
            calls = root / "calls/.claude/skills"
            self.assertEqual({p.name for p in calls.iterdir()}, {"summarize-call"})
            runtime = guides / "call-wiki/.env"
            runtime.write_text("private fixture")
            (source / "call-wiki/SKILL.md").write_text("changed")
            self.assertNotEqual(run("--check").returncode, 0)
            self.assertEqual(run().returncode, 0)
            self.assertEqual(runtime.read_text(), "private fixture")
            self.assertEqual((guides / "call-wiki/SKILL.md").read_text(), "changed")
            self.assertEqual(run("--check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
