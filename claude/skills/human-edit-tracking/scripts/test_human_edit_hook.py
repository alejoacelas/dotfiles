from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("human_edit_hook.py")
SPEC = importlib.util.spec_from_file_location("human_edit_hook", SCRIPT)
assert SPEC and SPEC.loader
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)


class HumanEditHookTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.email", "test@example.com"],
            check=True,
        )

    def tearDown(self):
        self.temp.cleanup()

    def commit(self, files: dict[str, str]):
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "base"], check=True)

    def test_default_names_only_emit_when_dirty(self):
        self.commit({"README.md": "# Read me\n", "notes.md": "# Notes\n"})
        (self.root / "README.md").write_text("# Read me\n\nHuman words.\n")
        (self.root / "notes.md").write_text("# Notes\n\nIgnored.\n")
        items = HOOK.evidence(self.root)
        self.assertEqual([name for name, _ in items], ["README.md"])
        self.assertIn("Human words.", items[0][1])

    def test_front_matter_opts_in_other_markdown(self):
        self.commit(
            {
                "notes.md": (
                    "---\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\n# Notes\n"
                )
            }
        )
        (self.root / "notes.md").write_text(
            "---\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\n# Notes\n\nEdit.\n"
        )
        self.assertEqual([name for name, _ in HOOK.evidence(self.root)], ["notes.md"])

    def test_untracked_readme_is_reported(self):
        self.commit({"base.txt": "base\n"})
        (self.root / "docs").mkdir()
        (self.root / "docs/README.md").write_text("# New\n")
        self.assertEqual([name for name, _ in HOOK.evidence(self.root)], ["docs/README.md"])

    def test_clean_files_emit_nothing(self):
        self.commit({"AGENTS.md": "# Rules\n"})
        self.assertEqual(HOOK.evidence(self.root), [])


if __name__ == "__main__":
    unittest.main()
