from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


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

    def stage(self, *names: str):
        subprocess.run(["git", "-C", str(self.root), "add", "--", *names], check=True)

    def hook_output(self, payload: dict | None = None) -> str:
        stdin = io.StringIO(json.dumps(payload or {"hook_event_name": "UserPromptSubmit", "cwd": str(self.root)}))
        stdout = io.StringIO()
        with mock.patch.object(HOOK.sys, "stdin", stdin), mock.patch.object(HOOK.sys, "stdout", stdout):
            self.assertEqual(HOOK.hook_main(), 0)
        return stdout.getvalue()

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

    def test_staged_only_change_is_reported(self):
        self.commit({"README.md": "# Before\n"})
        (self.root / "README.md").write_text("# After\n")
        self.stage("README.md")
        self.assertIn("# After", HOOK.evidence(self.root)[0][1])

    def test_staged_and_unstaged_changes_are_both_reported(self):
        self.commit({"README.md": "# Start\n"})
        (self.root / "README.md").write_text("# Staged\n")
        self.stage("README.md")
        (self.root / "README.md").write_text("# Current\n\nMore.\n")
        diff = HOOK.evidence(self.root)[0][1]
        self.assertIn("# Current", diff)
        self.assertIn("More.", diff)

    def test_deleted_default_document_is_reported(self):
        self.commit({"docs/README.md": "# Gone\n"})
        (self.root / "docs/README.md").unlink()
        items = HOOK.evidence(self.root)
        self.assertEqual([name for name, _ in items], ["docs/README.md"])
        self.assertIn("-# Gone", items[0][1])

    def test_disabled_and_incidental_keys_do_not_opt_in(self):
        self.commit(
            {
                "disabled.md": "---\nhuman_edit_tracking:\n  enabled: false\n---\n# Old\n",
                "incidental.md": "# human_edit_tracking:\n#   enabled: true\n\nOld.\n",
            }
        )
        (self.root / "disabled.md").write_text("---\nhuman_edit_tracking:\n  enabled: false\n---\n# New\n")
        (self.root / "incidental.md").write_text("# human_edit_tracking:\n#   enabled: true\n\nNew.\n")
        self.assertEqual(HOOK.evidence(self.root), [])

    def test_enabled_field_in_following_yaml_mapping_does_not_opt_in(self):
        self.commit(
            {
                "notes.md": (
                    "---\nhuman_edit_tracking:\n  enabled: false\nother_feature:\n"
                    "  enabled: true\n---\nOld.\n"
                )
            }
        )
        (self.root / "notes.md").write_text(
            "---\nhuman_edit_tracking:\n  enabled: false\nother_feature:\n"
            "  enabled: true\n---\nNew.\n"
        )
        self.assertEqual(HOOK.evidence(self.root), [])

    def test_inline_yaml_mapping_opts_in(self):
        self.commit({"notes.md": "---\nhuman_edit_tracking: {enabled: true, history: []}\n---\nOld.\n"})
        (self.root / "notes.md").write_text("---\nhuman_edit_tracking: {enabled: true, history: []}\n---\nNew.\n")
        self.assertEqual([name for name, _ in HOOK.evidence(self.root)], ["notes.md"])

    def test_removing_opt_in_still_reports_body_change(self):
        self.commit({"notes.md": "---\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\nOld.\n"})
        (self.root / "notes.md").write_text("New.\n")
        self.assertEqual([name for name, _ in HOOK.evidence(self.root)], ["notes.md"])

    def test_tracking_history_only_change_is_silent(self):
        base = "---\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\n# Same\n"
        self.commit({"notes.md": base})
        (self.root / "notes.md").write_text(
            "---\nhuman_edit_tracking:\n  enabled: true\n  history:\n    - date: 2026-08-05\n      changes:\n        - added: Human.\n---\n# Same\n"
        )
        self.assertEqual(HOOK.evidence(self.root), [])

    def test_body_and_history_change_reports_only_body(self):
        self.commit({"README.md": "---\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\n# Old\n"})
        (self.root / "README.md").write_text(
            "---\nhuman_edit_tracking:\n  enabled: true\n  history:\n    - date: 2026-08-05\n      changes:\n        - added: Human.\n---\n# New\n"
        )
        diff = HOOK.evidence(self.root)[0][1]
        self.assertIn("# New", diff)
        self.assertNotIn("added: Human", diff)

    def test_other_front_matter_changes_remain_visible(self):
        self.commit({"README.md": "---\ntitle: Old\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\n# Same\n"})
        (self.root / "README.md").write_text("---\ntitle: New\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\n# Same\n")
        self.assertIn("title: New", HOOK.evidence(self.root)[0][1])

    def test_spaces_and_unicode_in_filename(self):
        self.commit({"docs/README.md": "Old.\n", "notes café.md": "---\nhuman_edit_tracking:\n  enabled: true\n---\nOld.\n"})
        (self.root / "docs/README.md").rename(self.root / "docs/README old.md")
        (self.root / "notes café.md").write_text("---\nhuman_edit_tracking:\n  enabled: true\n---\nNew.\n")
        names = [name for name, _ in HOOK.evidence(self.root)]
        self.assertIn("docs/README.md", names)
        self.assertIn("notes café.md", names)

    def test_multiple_documents_are_sorted(self):
        self.commit({"z/README.md": "Old.\n", "a/AGENTS.md": "Old.\n"})
        (self.root / "z/README.md").write_text("New.\n")
        (self.root / "a/AGENTS.md").write_text("New.\n")
        self.assertEqual([name for name, _ in HOOK.evidence(self.root)], ["a/AGENTS.md", "z/README.md"])

    def test_hook_is_silent_outside_git(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(self.hook_output({"hook_event_name": "UserPromptSubmit", "cwd": directory}), "")

    def test_other_hook_event_is_silent(self):
        self.commit({"README.md": "Old.\n"})
        (self.root / "README.md").write_text("New.\n")
        self.assertEqual(self.hook_output({"hook_event_name": "PostToolUse", "cwd": str(self.root)}), "")

    def test_invalid_input_warns_without_injecting_context(self):
        stdout = io.StringIO()
        with mock.patch.object(HOOK.sys, "stdin", io.StringIO("not json")), mock.patch.object(
            HOOK.sys, "stdout", stdout
        ):
            self.assertEqual(HOOK.hook_main(), 0)
        output = json.loads(stdout.getvalue())
        self.assertIn("hook failed", output["systemMessage"])
        self.assertNotIn("hookSpecificOutput", output)

    def test_git_failure_warns_without_injecting_context(self):
        with mock.patch.object(HOOK, "evidence", side_effect=OSError("simulated")):
            output = json.loads(self.hook_output())
        self.assertIn("hook failed", output["systemMessage"])
        self.assertNotIn("hookSpecificOutput", output)

    def test_output_is_structured_evidence_without_authorship_claim(self):
        self.commit({"README.md": "Old.\n"})
        (self.root / "README.md").write_text("New.\n")
        output = json.loads(self.hook_output())
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        self.assertIn("not who made them", context)
        self.assertNotIn("these are Alejo's edits", context)

    def test_large_diff_is_bounded_and_has_recovery_command(self):
        self.commit({"README.md": "Old.\n"})
        (self.root / "README.md").write_text("\n".join(f"line {i}: " + "x" * 80 for i in range(400)))
        context = HOOK.render_context(self.root, HOOK.evidence(self.root))
        self.assertLessEqual(len(context), HOOK.MAX_CONTEXT_CHARS + 300)
        self.assertIn("--show <file>", context)

    def test_untracked_non_target_is_silent(self):
        self.commit({"base.txt": "base\n"})
        (self.root / "scratch.md").write_text("Untracked but not opted in.\n")
        self.assertEqual(HOOK.evidence(self.root), [])

    def test_untracked_opt_in_document_is_reported(self):
        self.commit({"base.txt": "base\n"})
        (self.root / "draft.md").write_text(
            "---\nhuman_edit_tracking:\n  enabled: true\n  history: []\n---\nDraft.\n"
        )
        self.assertEqual([name for name, _ in HOOK.evidence(self.root)], ["draft.md"])

    def test_malformed_front_matter_does_not_accidentally_opt_in(self):
        self.commit({"broken.md": "---\nhuman_edit_tracking:\n  enabled: true\n# no closing delimiter\nOld.\n"})
        (self.root / "broken.md").write_text(
            "---\nhuman_edit_tracking:\n  enabled: true\n# no closing delimiter\nNew.\n"
        )
        self.assertEqual(HOOK.evidence(self.root), [])

    def test_default_name_is_reported_even_with_malformed_yaml(self):
        self.commit({"README.md": "---\n[invalid yaml\n---\nOld.\n"})
        (self.root / "README.md").write_text("---\n[invalid yaml\n---\nNew.\n")
        self.assertEqual([name for name, _ in HOOK.evidence(self.root)], ["README.md"])

    def test_rename_of_default_document_includes_both_paths(self):
        self.commit({"README.md": "# Kept text\n"})
        (self.root / "README.md").rename(self.root / "guide.md")
        names = [name for name, _ in HOOK.evidence(self.root)]
        self.assertEqual(names, ["README.md", "guide.md"])

    def test_nested_repository_context_does_not_leak_parent_changes(self):
        self.commit({"README.md": "Parent old.\n"})
        nested = self.root / "nested"
        nested.mkdir()
        subprocess.run(["git", "init", "-q", str(nested)], check=True)
        subprocess.run(["git", "-C", str(nested), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(nested), "config", "user.email", "test@example.com"], check=True)
        (nested / "README.md").write_text("Nested old.\n")
        subprocess.run(["git", "-C", str(nested), "add", "."], check=True)
        subprocess.run(["git", "-C", str(nested), "commit", "-qm", "base"], check=True)
        (self.root / "README.md").write_text("Parent new.\n")
        (nested / "README.md").write_text("Nested new.\n")
        nested_root = HOOK.repo_root(nested)
        self.assertEqual(nested_root, nested.resolve())
        diff = HOOK.evidence(nested_root)[0][1]
        self.assertIn("Nested new.", diff)
        self.assertNotIn("Parent new.", diff)

    def test_crlf_front_matter_bookkeeping_is_silent(self):
        self.commit({"README.md": "---\r\nhuman_edit_tracking:\r\n  enabled: true\r\n  history: []\r\n---\r\nSame.\r\n"})
        (self.root / "README.md").write_bytes(
            b"---\r\nhuman_edit_tracking:\r\n  enabled: true\r\n  history:\r\n    - date: 2026-08-05\r\n      changes: []\r\n---\r\nSame.\r\n"
        )
        self.assertEqual(HOOK.evidence(self.root), [])

    def test_file_mode_only_change_is_silent(self):
        self.commit({"README.md": "Same.\n"})
        (self.root / "README.md").chmod(0o755)
        self.assertEqual(HOOK.evidence(self.root), [])

    def test_conflict_markers_are_shown_as_evidence_not_interpreted(self):
        self.commit({"README.md": "Original.\n"})
        (self.root / "README.md").write_text(
            "<<<<<<< ours\nAgent text.\n=======\nHuman text.\n>>>>>>> theirs\n"
        )
        diff = HOOK.evidence(self.root)[0][1]
        self.assertIn("<<<<<<< ours", diff)
        self.assertIn("Human text.", diff)


if __name__ == "__main__":
    unittest.main()
