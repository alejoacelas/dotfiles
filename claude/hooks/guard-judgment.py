#!/usr/bin/env python3
"""PreToolUse guard for files that hold hard-won judgment.

On a full-file `Write` to a guarded file, turn the overwrite into an "ask" so a
wholesale run-over can never happen silently. Surgical `Edit`s and unmarked files
stay friction-free.

A file is guarded if EITHER:
  - it contains the token GUARDED-JUDGMENT (a one-line marker that lives in the file
    and states how much effort is banked), or
  - its path matches a line in ~/.claude/hooks/guarded-paths.txt (a list you append
    to without having to touch the file).
"""
import fnmatch
import json
import os
import sys

TOKEN = "GUARDED-JUDGMENT"
LIST_PATH = os.path.expanduser("~/best/machine/dotfiles/claude/hooks/guarded-paths.txt")


def allow():
    sys.exit(0)


def ask(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()

    if data.get("tool_name") != "Write":
        allow()

    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path:
        allow()
    rpath = os.path.realpath(os.path.expanduser(path))

    # 1) explicit list — paths or globs, one per line, # comments allowed
    listed = False
    try:
        with open(LIST_PATH) as f:
            for line in f:
                pat = line.strip()
                if not pat or pat.startswith("#"):
                    continue
                pat = os.path.expanduser(pat)
                if (rpath == os.path.realpath(pat)
                        or fnmatch.fnmatch(rpath, pat)
                        or fnmatch.fnmatch(path, pat)):
                    listed = True
                    break
    except FileNotFoundError:
        pass

    # 2) in-file marker — a "GUARDED-JUDGMENT: <one sentence>" COMMENT line near the top
    #    states how much effort is banked. Must be comment-prefixed and in the first 20
    #    lines, so prose that merely mentions the token doesn't trip the guard.
    marker_note = ""
    marker = TOKEN + ":"
    comment_prefixes = ("#", "<!--", "//", "/*", "*", ";", "--", "%", '"""', "'''")
    if os.path.exists(rpath):
        try:
            with open(rpath, errors="ignore") as f:
                for i, ln in enumerate(f):
                    if i >= 20:
                        break
                    s = ln.strip()
                    if marker in s and s.startswith(comment_prefixes):
                        marker_note = s.split(marker, 1)[1].strip()
                        for closer in ("-->", "*/", "#}", "}}"):
                            if marker_note.endswith(closer):
                                marker_note = marker_note[:-len(closer)].strip()
                        break
        except Exception:
            pass

    if listed or marker_note:
        note = marker_note or "It is on the guarded list."
        ask(f'Guarded file — holds hard-won judgment: "{note}" '
            "Recover why it's this way (`git log`/`git blame`) before overwriting, and "
            "replace a considered choice only with a more considered one.")

    allow()


main()
