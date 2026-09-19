#!/usr/bin/env python3
"""Drop the startup status lines the codex and hive plugins print.

Both plugins emit a `systemMessage` from their SessionStart hook every session
("codex: available", "hive: run /hive:align for setup recommendations"). The
hooks also do work worth keeping — codex puts `codex-companion` on PATH and
injects its help text, hive registers the transcript dir for retrieval — so the
hooks stay and only their `systemMessage` is filtered out.

Claude Code loads hooks.json at session start, so a patch applies from the next
session on. Plugin updates install a fresh hooks.json; this re-applies then.
"""

import json
import pathlib
import sys

FILTER = " | jq -c 'del(.systemMessage) | select(length > 0)'"
PLUGINS = ("codex@codex-plugin-cc", "hive@alignment-hive")

installed = pathlib.Path.home() / ".claude/plugins/installed_plugins.json"
try:
    plugins = json.loads(installed.read_text())["plugins"]
except (OSError, ValueError, KeyError):
    sys.exit(0)

for name in PLUGINS:
    for install in plugins.get(name, []):
        hooks_file = pathlib.Path(install["installPath"]) / "hooks" / "hooks.json"
        try:
            data = json.loads(hooks_file.read_text())
        except (OSError, ValueError):
            continue
        patched = False
        for group in data.get("hooks", {}).get("SessionStart", []):
            for hook in group.get("hooks", []):
                command = hook.get("command", "")
                if "session-start.sh" in command and FILTER not in command:
                    hook["command"] = command + FILTER
                    patched = True
        if patched:
            hooks_file.write_text(json.dumps(data, indent=2) + "\n")
