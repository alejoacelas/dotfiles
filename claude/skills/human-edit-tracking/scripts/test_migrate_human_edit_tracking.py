from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("migrate_human_edit_tracking.py")
SPEC = importlib.util.spec_from_file_location("migrate_human_edit_tracking", SCRIPT)
assert SPEC and SPEC.loader
MIGRATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATE)


class MigrateTextTest(unittest.TestCase):
    def test_adds_front_matter_and_removes_prose_markers(self):
        source = "<!--me-->Mine\n\nTheirs<!--ai-->\n"
        expected = (
            "---\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\n"
            "Mine\n\nTheirs\n"
        )
        self.assertEqual(MIGRATE.migrate_text(source), expected)

    def test_preserves_existing_front_matter(self):
        source = "---\ntitle: Example\ntags: [one]\n---\n<!--ai--># Title\n"
        expected = (
            "---\ntitle: Example\ntags: [one]\n"
            "human_edit_tracking:\n  enabled: true\n  history: []\n"
            "---\n# Title\n"
        )
        self.assertEqual(MIGRATE.migrate_text(source), expected)

    def test_does_not_duplicate_complete_tracking_metadata(self):
        source = (
            "---\nhuman_edit_tracking:\n  enabled: false\n  history:\n    - old\n---\n"
            "<!--me-->Text\n"
        )
        expected = source.replace("<!--me-->", "")
        self.assertEqual(MIGRATE.migrate_text(source), expected)

    def test_completes_existing_tracking_metadata(self):
        source = "---\nhuman_edit_tracking:\n  enabled: true\ntitle: Test\n---\nText\n"
        expected = (
            "---\nhuman_edit_tracking:\n  enabled: true\n  history: []\n"
            "title: Test\n---\nText\n"
        )
        self.assertEqual(MIGRATE.migrate_text(source), expected)

    def test_preserves_markers_in_fenced_and_inline_code(self):
        source = (
            "<!--ai-->Text `<!--me-->` and ``x ` <!--ai--> x``.\n"
            "~~~html\n<!--ai-->\n~~~\n"
            "````\n```\n<!--me-->\n```\n````\n"
            "<!--me-->End\n"
        )
        migrated = MIGRATE.remove_attribution_markers(source)
        self.assertEqual(
            migrated,
            "Text `<!--me-->` and ``x ` <!--ai--> x``.\n"
            "~~~html\n<!--ai-->\n~~~\n"
            "````\n```\n<!--me-->\n```\n````\n"
            "End\n",
        )

    def test_preserves_multiline_inline_code(self):
        source = "Before `code\n<!--ai--> still code` <!--me-->after\n"
        expected = "Before `code\n<!--ai--> still code` after\n"
        self.assertEqual(MIGRATE.remove_attribution_markers(source), expected)

    def test_unmatched_backticks_do_not_hide_markers(self):
        source = "Unmatched ` tick <!--ai-->then attribution\n"
        expected = "Unmatched ` tick then attribution\n"
        self.assertEqual(MIGRATE.remove_attribution_markers(source), expected)

    def test_preserves_crlf_and_bom(self):
        source = "\ufeff---\r\ntitle: Test\r\n---\r\n<!--ai-->Body\r\n"
        migrated = MIGRATE.migrate_text(source)
        self.assertTrue(migrated.startswith("\ufeff---\r\ntitle: Test\r\nhuman_edit_tracking:"))
        self.assertNotIn("<!--ai-->Body", migrated)
        self.assertNotIn("\n", migrated.replace("\r\n", ""))


class MigrationCliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def tearDown(self):
        self.temp.cleanup()

    def add(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        subprocess.run(["git", "-C", str(self.root), "add", relative], check=True)
        return path

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), "--git-root", str(self.root), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_default_scope_migrates_default_names_and_marker_files_only(self):
        readme = self.add("docs/README.md", "# Readme\n")
        legacy = self.add("notes.md", "<!--ai-->Legacy\n")
        ordinary = self.add("ordinary.md", "Ordinary\n")
        example = self.add("example.md", "Example: `<!--ai-->`\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("human_edit_tracking:", readme.read_text())
        self.assertIn("human_edit_tracking:", legacy.read_text())
        self.assertNotIn("<!--ai-->", legacy.read_text())
        self.assertEqual(ordinary.read_text(), "Ordinary\n")
        self.assertEqual(example.read_text(), "Example: `<!--ai-->`\n")

    def test_check_and_dry_run_do_not_write(self):
        readme = self.add("README.md", "# Readme\n")
        check = self.run_cli("--check")
        self.assertEqual(check.returncode, 1)
        self.assertEqual(readme.read_text(), "# Readme\n")
        dry_run = self.run_cli("--dry-run")
        self.assertEqual(dry_run.returncode, 0)
        self.assertEqual(readme.read_text(), "# Readme\n")

    def test_check_passes_after_migration(self):
        self.add("README.md", "# Readme\n")
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.run_cli("--check").returncode, 0)

    def test_explicit_target_migrates_ordinary_tracked_markdown(self):
        notes = self.add("notes.md", "Notes\n")
        result = self.run_cli("notes.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("human_edit_tracking:", notes.read_text())

    def test_cli_preserves_crlf(self):
        path = self.root / "README.md"
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write("<!--me--># Readme\r\n")
        subprocess.run(["git", "-C", str(self.root), "add", "README.md"], check=True)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        with path.open("r", encoding="utf-8", newline="") as handle:
            migrated = handle.read()
        self.assertIn("history: []\r\n", migrated)
        self.assertNotIn("\n", migrated.replace("\r\n", ""))

    def test_refuses_untracked_and_out_of_root_targets(self):
        (self.root / "untracked.md").write_text("No\n")
        self.assertNotEqual(self.run_cli("untracked.md").returncode, 0)
        self.assertNotEqual(self.run_cli("../outside.md").returncode, 0)

    def test_never_replaces_symlink(self):
        target = self.add("AGENTS.md", "# Rules\n")
        link = self.root / "CLAUDE.md"
        link.symlink_to(target.name)
        subprocess.run(["git", "-C", str(self.root), "add", "CLAUDE.md"], check=True)
        result = self.run_cli("CLAUDE.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(link.is_symlink())
        self.assertEqual(target.read_text(), "# Rules\n")
        self.assertIn("SKIP symlink CLAUDE.md", result.stdout)

    def test_requires_exact_git_root(self):
        self.add("sub/README.md", "# Readme\n")
        result = subprocess.run(
            ["python3", str(SCRIPT), "--git-root", str(self.root / "sub")],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be the repository root", result.stderr)


if __name__ == "__main__":
    unittest.main()
