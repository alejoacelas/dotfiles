#!/usr/bin/env python3
"""Migrate legacy Markdown attribution markers to human-edit tracking metadata."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys
from typing import NamedTuple


DEFAULT_NAMES = {"README.md", "AGENTS.md", "CLAUDE.md"}
MARKERS = ("<!--ai-->", "<!--/ai-->", "<!--me-->", "<!--/me-->")
CLOSING_MARKER_LINE = re.compile(
    r"(?m)(?:^[ \t]*\r?\n)?^[ \t]*(?:(?:<!--/(?:ai|me)-->)\s*)+(?:\r?\n|\Z)"
)
MARKER_ONLY_LINE = re.compile(
    r"(?m)^[ \t]*(?:(?:<!--/?(?:ai|me)-->)\s*)+(?:\r?\n|\Z)"
)
FRONT_MATTER_END = re.compile(r"^---[ \t]*(?:\r?\n|$)", re.MULTILINE)
FENCE = re.compile(r"^(?P<indent> {0,3})(?P<run>`{3,}|~{3,})(?P<rest>.*)$")


class Migration(NamedTuple):
    path: Path
    original: str
    migrated: str


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def validate_git_root(root: Path) -> Path:
    root = root.resolve()
    result = git(root, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        raise ValueError(f"not a Git repository: {root}")
    actual = Path(result.stdout.strip()).resolve()
    if actual != root:
        raise ValueError(f"--git-root must be the repository root ({actual})")
    return root


def tracked_markdown(root: Path) -> list[Path]:
    result = git(root, "ls-files", "-z", "--", "*.md")
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "could not list Git-tracked Markdown")
    return [root / name for name in result.stdout.split("\0") if name]


def front_matter_bounds(text: str) -> tuple[int, int] | None:
    offset = 1 if text.startswith("\ufeff") else 0
    if not text.startswith("---\n", offset) and not text.startswith("---\r\n", offset):
        return None
    first_newline = text.find("\n", offset) + 1
    match = FRONT_MATTER_END.search(text, first_newline)
    if match is None:
        return None
    return first_newline, match.start()


def has_tracking_front_matter(text: str) -> bool:
    bounds = front_matter_bounds(text)
    if bounds is None:
        return False
    body = text[bounds[0] : bounds[1]]
    return re.search(r"(?m)^human_edit_tracking\s*:", body) is not None


def _complete_tracking_block(front_matter: str, newline: str) -> str:
    match = re.search(r"(?m)^human_edit_tracking\s*:[^\r\n]*(?:\r?\n|$)", front_matter)
    if match is None:
        return front_matter
    block_end = match.end()
    while block_end < len(front_matter):
        line_end = front_matter.find("\n", block_end)
        line_end = len(front_matter) if line_end == -1 else line_end + 1
        line = front_matter[block_end:line_end]
        if line.strip() and not line.startswith((" ", "\t", "#")):
            break
        block_end = line_end
    block = front_matter[match.start() : block_end]
    additions = ""
    if re.search(r"(?m)^\s+enabled\s*:", block) is None:
        additions += f"  enabled: true{newline}"
    if re.search(r"(?m)^\s+history\s*:", block) is None:
        additions += f"  history: []{newline}"
    return front_matter[:block_end] + additions + front_matter[block_end:]


def add_tracking_front_matter(text: str) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    block = (
        f"human_edit_tracking:{newline}"
        f"  enabled: true{newline}"
        f"  history: []{newline}"
    )
    bounds = front_matter_bounds(text)
    if bounds is None:
        bom = "\ufeff" if text.startswith("\ufeff") else ""
        body = text[len(bom) :]
        return f"{bom}---{newline}{block}---{newline}{body}"

    start, end = bounds
    front_matter = text[start:end]
    if re.search(r"(?m)^human_edit_tracking\s*:", front_matter):
        complete = _complete_tracking_block(front_matter, newline)
        return text[:start] + complete + text[end:]
    return text[:end] + block + text[end:]


def read_markdown(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _strip_markers_from_noncode(text: str) -> str:
    # Most legacy wrappers occupy their own lines. Remove those lines rather
    # than leaving hundreds of artificial blank lines, including at EOF.
    text = CLOSING_MARKER_LINE.sub("", text)
    text = MARKER_ONLY_LINE.sub("", text)
    output: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "`":
            end = index + 1
            while end < len(text) and text[end] == "`":
                end += 1
            run = end - index
            closing_start = end
            while closing_start < len(text):
                closing_start = text.find("`", closing_start)
                if closing_start == -1:
                    break
                closing_end = closing_start + 1
                while closing_end < len(text) and text[closing_end] == "`":
                    closing_end += 1
                if closing_end - closing_start == run:
                    output.append(text[index:closing_end])
                    index = closing_end
                    break
                closing_start = closing_end
            else:
                closing_start = -1
            if closing_start != -1:
                continue
            output.append(text[index:end])
            index = end
            continue
        marker = next(
            (candidate for candidate in MARKERS if text.startswith(candidate, index)),
            None,
        )
        if marker is not None:
            index += len(marker)
            continue
        output.append(text[index])
        index += 1
    return "".join(output)


def remove_attribution_markers(text: str) -> str:
    output: list[str] = []
    nonfenced: list[str] = []
    fence_char: str | None = None
    fence_length = 0

    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        fence = FENCE.match(content)
        if fence_char is not None:
            output.append(line)
            if (
                fence
                and fence.group("run")[0] == fence_char
                and len(fence.group("run")) >= fence_length
                and not fence.group("rest").strip()
            ):
                fence_char = None
                fence_length = 0
            continue
        if fence:
            output.append(_strip_markers_from_noncode("".join(nonfenced)))
            nonfenced.clear()
            fence_char = fence.group("run")[0]
            fence_length = len(fence.group("run"))
            output.append(line)
            continue
        nonfenced.append(line)
    output.append(_strip_markers_from_noncode("".join(nonfenced)))
    return "".join(output)


def migrate_text(text: str) -> str:
    return add_tracking_front_matter(remove_attribution_markers(text))


def resolve_targets(root: Path, requested: list[str]) -> list[Path]:
    tracked = tracked_markdown(root)
    tracked_set = {path.resolve() for path in tracked}
    if not requested:
        targets = []
        for path in tracked:
            if path.is_symlink():
                continue
            text = read_markdown(path)
            if path.name in DEFAULT_NAMES or remove_attribution_markers(text) != text:
                targets.append(path)
        return targets

    targets = []
    for value in requested:
        path = (root / value).absolute() if not Path(value).is_absolute() else Path(value).absolute()
        try:
            path.relative_to(root)
        except ValueError as error:
            raise ValueError(f"target is outside --git-root: {value}") from error
        if path.resolve() not in tracked_set:
            raise ValueError(f"target is not a Git-tracked Markdown file: {value}")
        targets.append(path)
    return sorted(set(targets))


def plan_migrations(root: Path, requested: list[str]) -> tuple[list[Migration], list[Path]]:
    migrations = []
    skipped_symlinks = []
    for path in resolve_targets(root, requested):
        if path.is_symlink():
            skipped_symlinks.append(path)
            continue
        original = read_markdown(path)
        migrated = migrate_text(original)
        if migrated != original:
            migrations.append(Migration(path, original, migrated))
    return migrations, skipped_symlinks


def cli_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-root", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit 1 if migration is needed")
    mode.add_argument("--dry-run", action="store_true", help="print changes without writing")
    parser.add_argument("paths", nargs="*", help="tracked Markdown paths relative to the Git root")
    args = parser.parse_args(argv)

    try:
        root = validate_git_root(args.git_root)
        migrations, skipped = plan_migrations(root, args.paths)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

    for path in skipped:
        print(f"SKIP symlink {path.relative_to(root)}")
    for migration in migrations:
        action = "WOULD MIGRATE" if args.check or args.dry_run else "MIGRATE"
        print(f"{action} {migration.path.relative_to(root)}")

    if args.check:
        return 1 if migrations else 0
    if args.dry_run:
        return 0
    for migration in migrations:
        migration.path.write_text(migration.migrated, encoding="utf-8", newline="")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli_main(sys.argv[1:]))
