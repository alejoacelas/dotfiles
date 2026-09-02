---
name: delegate-claude-cloud
description: Delegate a task to Claude Code on the cloud. Use when the user asks to send, delegate, hand off, or run work in Claude Cloud with `claude --cloud`.
---

# Delegate to Claude Cloud

From the target Git repository:

1. Inspect the working tree. Commit the intended changes and push the current branch to its Git remote.
2. Run `claude --cloud "<task>"` in an interactive terminal or PTY. For Codex shell tools, enable `tty: true`; `--cloud` fails in non-interactive invocations.
3. Return the cloud session link and note any files or nested repositories that were not pushed.

If Claude reports that the repository is too large to teleport, connect its GitHub repository at <https://claude.ai/code>, then retry.
