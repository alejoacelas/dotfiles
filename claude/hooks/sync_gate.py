#!/usr/bin/env python3
"""PreToolUse(Read) freshness gate for sync-drive mirror files (people repo).

This is a GLOBAL hook (registered in ~/.claude/settings.json) but scoped to the
people repo: the settings.json command only invokes it when CLAUDE_PROJECT_DIR is
~/people, so it never runs for other projects.

Fires before a Read. If the file being read is a Google-Doc *mirror* listed in any
present person's `present/all/<person>/sync-manifest.json` AND it has not been
freshness-checked today, it injects a non-blocking note nudging the agent to run the
sync-drive skill in `--check` mode (one Drive metadata call) and pull only if the
source actually changed. Otherwise it stays silent.

This shell-side gate deliberately does NOT call Google Drive: the Drive MCP connector
is not available to hooks. So it only throttles (once per day per doc) and nudges; the
agent performs the actual one-call freshness check. Any error -> silent allow; this hook
never blocks a Read.
"""
import json
import os
import sys
from datetime import date
from pathlib import Path


def emit(additional_context, system_message):
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "additionalContext": additional_context,
        },
        "systemMessage": system_message,
    }
    print(json.dumps(out))


def main():
    data = json.loads(sys.stdin.read())
    if data.get("tool_name") != "Read":
        return
    fp = data.get("tool_input", {}).get("file_path")
    if not fp:
        return

    proj = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    target = os.path.realpath(fp)
    today = date.today().isoformat()

    # One manifest per present person: present/all/<person>/sync-manifest.json.
    # (vip/ holds symlinks into all/, so scanning all/ covers every present person.)
    for manifest_path in sorted(Path(proj).glob("present/all/*/sync-manifest.json")):
        try:
            manifest = json.loads(manifest_path.read_text())
        except Exception:
            continue
        for doc_id, doc in manifest.get("docs", {}).items():
            for form in doc.get("forms", []):
                out_abs = os.path.realpath(os.path.join(proj, form["out"]))
                if out_abs != target:
                    continue
                if doc.get("last_synced") == today:
                    return  # already verified today -> stay silent
                emit(
                    additional_context=(
                        f"This file is a pull-only mirror of Google Doc {doc_id} "
                        f"(tab '{form.get('tab')}' of \"{doc.get('title')}\"), last synced "
                        f"{doc.get('last_synced')}. The source may have changed since. Before "
                        f"relying on its contents, run the sync-drive skill in --check mode for "
                        f"doc {doc_id} (a single get_file_metadata call); if it reports STALE, do "
                        f"a full sync, otherwise proceed. Do not hand-edit this file."
                    ),
                    system_message=(
                        f"sync-drive: {form['out']} last synced {doc.get('last_synced')} — "
                        f"consider a /sync-drive --check before trusting it."
                    ),
                )
                return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never block a Read because of this hook
    sys.exit(0)
