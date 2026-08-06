#!/usr/bin/env python3
"""Tests for the ;;-marker human-edit hook."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import human_edit_hook as hook

SCRIPT = Path(__file__).resolve().parent / "human_edit_hook.py"


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_hook(cwd: Path, event: str = "UserPromptSubmit") -> dict | None:
    payload = json.dumps({"hook_event_name": event, "cwd": str(cwd)})
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=payload,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else None


def context_of(output: dict | None) -> str:
    assert output is not None, "expected hook output"
    return output["hookSpecificOutput"]["additionalContext"]


class HookTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        run_git(self.root, "init", "-q")
        run_git(self.root, "config", "user.email", "test@example.com")
        run_git(self.root, "config", "user.name", "Test")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def commit_file(self, name: str, text: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        run_git(self.root, "add", str(path.relative_to(self.root)))
        run_git(self.root, "commit", "-qm", f"add {name}")
        return path

    def test_marked_change_is_reported(self) -> None:
        path = self.commit_file("notes.md", "First line.\n")
        path.write_text("First line.\nA thought I typed myself. ;;\n")
        context = context_of(run_hook(self.root))
        self.assertIn("notes.md", context)
        self.assertIn("A thought I typed myself.", context)

    def test_unmarked_change_is_silent(self) -> None:
        path = self.commit_file("notes.md", "First line.\n")
        path.write_text("First line.\nAn agent-made change.\n")
        self.assertIsNone(run_hook(self.root))

    def test_clean_file_with_marker_is_silent(self) -> None:
        self.commit_file("code.md", "```lisp\n;; a committed comment\n```\n")
        self.assertIsNone(run_hook(self.root))

    def test_legacy_marker_in_context_lines_is_silent(self) -> None:
        path = self.commit_file("code.md", "```lisp\n;; a committed comment\n```\nOld line.\n")
        path.write_text("```lisp\n;; a committed comment\n```\nRewritten line.\n")
        self.assertIsNone(run_hook(self.root))

    def test_untracked_file_with_marker_is_reported(self) -> None:
        self.commit_file("seed.md", "seed\n")
        (self.root / "draft.md").write_text("Fresh draft. ;;\n")
        self.assertIn("draft.md", context_of(run_hook(self.root)))

    def test_untracked_file_without_marker_is_silent(self) -> None:
        self.commit_file("seed.md", "seed\n")
        (self.root / "draft.md").write_text("Fresh draft.\n")
        self.assertIsNone(run_hook(self.root))

    def test_non_markdown_change_is_silent(self) -> None:
        path = self.commit_file("script.py", "x = 1\n")
        path.write_text("x = 2  # ;;\n")
        self.assertIsNone(run_hook(self.root))

    def test_tracking_front_matter_is_excluded_from_diff(self) -> None:
        original = (
            "---\nhuman_edit_tracking:\n  history: []\n---\n\nBody.\n"
        )
        path = self.commit_file("README.md", original)
        path.write_text(
            "---\nhuman_edit_tracking:\n  history:\n    - date: 2026-08-05\n---\n"
            "\nBody.\nMarked addition. ;;\n"
        )
        context = context_of(run_hook(self.root))
        self.assertIn("Marked addition.", context)
        self.assertNotIn("history", context)

    def test_other_hook_events_are_ignored(self) -> None:
        path = self.commit_file("notes.md", "First line.\n")
        path.write_text("Changed. ;;\n")
        self.assertIsNone(run_hook(self.root, event="PreToolUse"))

    def test_outside_git_repository_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as plain:
            self.assertIsNone(run_hook(Path(plain)))

    def test_long_diffs_are_truncated(self) -> None:
        path = self.commit_file("notes.md", "First line.\n")
        path.write_text("First line. ;;\n" + "filler\n" * 4000)
        context = context_of(run_hook(self.root))
        self.assertLessEqual(len(context), hook.MAX_CONTEXT_CHARS + 200)
        self.assertIn("truncated", context)

    def test_show_prints_full_diff(self) -> None:
        path = self.commit_file("notes.md", "First line.\n")
        path.write_text("First line.\nSecond line. ;;\n")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--show", str(path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("+Second line.", result.stdout)


class MarkerDetectionTest(unittest.TestCase):
    def test_added_line_with_marker(self) -> None:
        self.assertTrue(hook.marker_in_added_lines("+new text ;;\n-old\n"))

    def test_marker_only_in_removed_line(self) -> None:
        self.assertFalse(hook.marker_in_added_lines("-old text ;;\n+new\n"))

    def test_marker_in_file_header_does_not_count(self) -> None:
        self.assertFalse(hook.marker_in_added_lines("+++ b/;; notes.md\n+plain\n"))


if __name__ == "__main__":
    unittest.main()
