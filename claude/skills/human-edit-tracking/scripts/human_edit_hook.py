#!/usr/bin/env python3
"""Inject diffs for dirty Markdown files whose uncommitted changes carry the § marker."""

from __future__ import annotations

import argparse
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


MARKER = "§"
MAX_CONTEXT_CHARS = 9_000
FRONT_MATTER = re.compile(r"\A---\r?\n(?P<body>.*?)(?:\r?\n)---(?:\r?\n|\Z)", re.DOTALL)


def git(root_or_cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root_or_cwd), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def repo_root(cwd: Path) -> Path | None:
    result = git(cwd, "rev-parse", "--show-toplevel", check=False)
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else None


def changed_markdown(root: Path) -> list[str]:
    changed = git(root, "diff", "--name-only", "-z", "HEAD", "--", "*.md").stdout
    untracked = git(
        root, "ls-files", "--others", "--exclude-standard", "-z", "--", "*.md"
    ).stdout
    return sorted(set(filter(None, (changed + untracked).split("\0"))))


def head_text(root: Path, relative_path: str) -> str | None:
    result = git(root, "show", f"HEAD:{relative_path}", check=False)
    return result.stdout if result.returncode == 0 else None


def worktree_text(root: Path, relative_path: str) -> str | None:
    try:
        return (root / relative_path).read_text(errors="replace")
    except OSError:
        return None


def without_tracking_metadata(text: str | None) -> str:
    """Remove only the tracking mapping, leaving other YAML and Markdown intact."""
    if text is None:
        return ""
    match = FRONT_MATTER.match(text)
    if not match:
        return text
    lines = match.group("body").splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if re.match(r"^human_edit_tracking\s*:", line)), None)
    if start is None:
        return text
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and not line[0].isspace() and not line.lstrip().startswith("#"):
            break
        end += 1
    body_without_tracking = "".join(lines[:start] + lines[end:])
    return text[: match.start("body")] + body_without_tracking + text[match.end("body") :]


def file_diff(root: Path, relative_path: str) -> str:
    before = without_tracking_metadata(head_text(root, relative_path))
    after = without_tracking_metadata(worktree_text(root, relative_path))
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{relative_path}",
            tofile=f"b/{relative_path}",
        )
    )


def marker_in_added_lines(diff: str) -> bool:
    """A marker only counts when it is part of the uncommitted change itself, so
    legacy occurrences (legal citations, old notes) never trigger the hook."""
    return any(
        line.startswith("+") and not line.startswith("+++") and MARKER in line
        for line in diff.splitlines()
    )


def evidence(root: Path) -> list[tuple[str, str]]:
    items = []
    seen_real_paths: set[Path] = set()
    for relative_path in changed_markdown(root):
        text = worktree_text(root, relative_path)
        if text is None or MARKER not in text:
            continue
        real_path = (root / relative_path).resolve()
        if real_path in seen_real_paths:
            continue
        seen_real_paths.add(real_path)
        diff = file_diff(root, relative_path)
        if diff and marker_in_added_lines(diff):
            items.append((relative_path, diff))
    return items


def render_context(root: Path, items: list[tuple[str, str]]) -> str:
    preamble = (
        f"Human-edit evidence: the Markdown files below have uncommitted changes "
        f"whose added lines carry the `{MARKER}` marker Alejo types inside his own "
        "edits. Compare each diff with your actions and the conversation. If a diff "
        "is clearly Alejo's, use $human-edit-tracking to record every changed "
        f"passage verbatim, remove the `{MARKER}` markers, and mention the record in "
        "your response. If authorship is unclear, ask `Was this change by you?` and "
        "do not record it before he answers.\n"
    )
    chunks = [preamble]
    for relative_path, diff in items:
        chunks.append(f"\nFILE: {relative_path}\n```diff\n{diff.rstrip()}\n```\n")
    full = "".join(chunks)
    if len(full) <= MAX_CONTEXT_CHARS:
        return full
    return (
        full[:MAX_CONTEXT_CHARS]
        + "\n[Diff context truncated. Run "
        + str(
            Path.home()
            / "best/ai/dotfiles/claude/skills/human-edit-tracking/scripts/human_edit_hook.py"
        )
        + " --show <file> for a complete diff.]"
    )


def hook_main() -> int:
    try:
        payload = json.load(sys.stdin)
        if payload.get("hook_event_name") not in (None, "UserPromptSubmit"):
            return 0
        cwd = Path(
            payload.get("cwd")
            or os.environ.get("CLAUDE_PROJECT_DIR")
            or os.getcwd()
        )
        root = repo_root(cwd)
        if root is None:
            return 0
        items = evidence(root)
        if not items:
            return 0
        context = render_context(root, items)
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": context,
                    }
                }
            )
        )
    except Exception:
        print(
            json.dumps(
                {
                    "systemMessage": (
                        "Human-edit tracking hook failed; no authorship evidence "
                        "was injected."
                    )
                }
            )
        )
        return 0
    return 0


def cli_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", metavar="FILE")
    args = parser.parse_args(argv)
    if args.show:
        path = Path(args.show).resolve()
        root = repo_root(path.parent)
        if root is None:
            parser.error("file is not inside a Git repository")
        try:
            relative = str(path.relative_to(root))
        except ValueError:
            parser.error("file is outside the Git repository")
        sys.stdout.write(file_diff(root, relative))
        return 0
    return hook_main()


if __name__ == "__main__":
    raise SystemExit(cli_main(sys.argv[1:]))
