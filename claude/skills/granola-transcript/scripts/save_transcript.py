#!/usr/bin/env python3
"""Resolve the right folder for a cleaned Granola transcript and write it.

Default location logic (relative to --base-dir, default: current working dir).
Calls live under the person's ``sources/`` channel folder; a legacy top-level
``calls/`` is honored if that's what the person folder already uses.
  1. A folder named after the person (nickname-aware, e.g. ``sam/`` for
     "Samantha")  ->  save in ``<that-folder>/sources/calls/<YYYY-MM-DD>/``
     (or ``<that-folder>/calls/`` if the folder still uses the legacy layout).
  2. Else an existing ``sources/calls/`` or ``calls/`` at the base  ->  save there.
  3. Else create ``sources/calls/<YYYY-MM-DD>/`` at the base and save there (and say so).

The file is named ``transcript.md`` — the dated folder carries the call's identity.
For a second call with the same person on the same day, pass --name to disambiguate
(e.g. ``--name transcript-strategy`` -> ``transcript-strategy.md``).
"""
import argparse
import re
import sys
from pathlib import Path

# Folders that name a content bucket, not a person — never treated as a person dir.
RESERVED_DIRS = {"sources", "calls", "transcripts", "notes", "deliverables", "wiki",
                 "node_modules", "__pycache__"}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def find_person_dir(base: Path, person: str):
    """Return a directory under ``base`` that names this person, or None."""
    person = person.lower().strip()
    first = person.split()[0] if person.split() else person
    for d in sorted(base.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        n = d.name.lower()
        if n in RESERVED_DIRS or len(n) < 3:
            continue
        # exact, or one is a prefix of the other (handles "sam" <-> "samantha")
        if n == person or n == first or first.startswith(n) or n.startswith(first) \
                or person.startswith(n):
            return d
    return None


def _calls_root(folder: Path) -> Path:
    """Where calls live inside ``folder``: ``sources/calls/`` by default, but the
    legacy top-level ``calls/`` if that folder already uses it (and has no sources/)."""
    if (folder / "calls").is_dir() and not (folder / "sources" / "calls").is_dir():
        return folder / "calls"
    return folder / "sources" / "calls"


def resolve_dir(base: Path, person: str, date: str):
    """Return (target_dir, note): the dated call folder following the location logic."""
    person_dir = find_person_dir(base, person)
    if person_dir is not None:
        root = _calls_root(person_dir)
        return root / date, f"person folder '{person_dir.name}/' ({root.relative_to(person_dir)}/)"
    root = _calls_root(base)
    if root.is_dir():
        return root / date, f"existing {root.relative_to(base)}/ folder"
    return root / date, f"created new {root.relative_to(base)}/ folder (no person folder found)"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--person", required=True, help="Person the call was with (e.g. 'Samantha')")
    p.add_argument("--date", required=True, help="Call date, YYYY-MM-DD")
    p.add_argument("--name", default="transcript",
                   help="Base filename (default: 'transcript'); use for a same-day second call")
    p.add_argument("--content-file", help="File with the cleaned transcript (default: stdin)")
    p.add_argument("--base-dir", default=".", help="Where to search for the folder (default: cwd)")
    p.add_argument("--dry-run", action="store_true", help="Print the resolved path, don't write")
    args = p.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        p.error(f"--date must be YYYY-MM-DD, got {args.date!r}")

    base = Path(args.base_dir).expanduser().resolve()
    if not base.is_dir():
        p.error(f"--base-dir does not exist: {base}")

    target_dir, note = resolve_dir(base, args.person, args.date)
    name = slugify(args.name) or "transcript"
    out = target_dir / f"{name}.md"

    if args.dry_run:
        print(f"[dry-run] would write to: {out}")
        print(f"[dry-run] reason: {note}")
        return 0

    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8")
    else:
        content = sys.stdin.read()
    if not content.strip():
        p.error("no transcript content provided (use --content-file or pipe via stdin)")

    target_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(str(out))
    print(f"(location: {note})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
