#!/usr/bin/env python3
"""Inject diffs for dirty Markdown files that track human edits."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


DEFAULT_NAMES = {"README.md", "AGENTS.md", "CLAUDE.md"}
MAX_CONTEXT_CHARS = 9_000
FRONT_MATTER = re.compile(r"\A---\r?\n(?P<body>.*?)(?:\r?\n)---(?:\r?\n|\Z)", re.DOTALL)
TRACKING_ENABLED = re.compile(
    r"(?ms)^human_edit_tracking\s*:\s*(?:#.*)?$.*?^\s+enabled\s*:\s*true\s*(?:#.*)?$"
)


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


def reads_tracking_enabled(path: Path) -> bool:
    try:
        prefix = path.read_text(errors="replace")[:100_000]
    except OSError:
        return False
    match = FRONT_MATTER.match(prefix)
    return bool(match and TRACKING_ENABLED.search(match.group("body")))


def is_tracked_document(root: Path, relative_path: str) -> bool:
    path = root / relative_path
    return path.name in DEFAULT_NAMES or reads_tracking_enabled(path)


def file_diff(root: Path, relative_path: str) -> str:
    tracked = git(root, "ls-files", "--error-unmatch", "--", relative_path, check=False)
    if tracked.returncode == 0:
        return git(
            root,
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--word-diff=plain",
            "--word-diff-regex=[^[:space:]]+",
            "HEAD",
            "--",
            relative_path,
        ).stdout

    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "diff",
            "--no-index",
            "--no-ext-diff",
            "--no-color",
            "--word-diff=plain",
            "/dev/null",
            relative_path,
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def evidence(root: Path) -> list[tuple[str, str]]:
    items = []
    seen_real_paths: set[Path] = set()
    for relative_path in changed_markdown(root):
        if not is_tracked_document(root, relative_path):
            continue
        path = root / relative_path
        real_path = path.resolve()
        if real_path in seen_real_paths:
            continue
        seen_real_paths.add(real_path)
        diff = file_diff(root, relative_path)
        if diff:
            items.append((relative_path, diff))
    return items


def render_context(root: Path, items: list[tuple[str, str]]) -> str:
    preamble = (
        "Human-edit tracking evidence: the Markdown files below differ from HEAD at "
        "the start of this user turn. This proves that the edits are uncommitted, not "
        "who made them. Compare the diffs with your actions and the conversation. If a "
        "diff is clearly Alejo's, use $human-edit-tracking to record every changed "
        "passage verbatim and mention the record in your response. If authorship is "
        "unclear, ask `Was this change by you?` and do not record it before he answers.\n"
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
