# Project-only skill link

The public `summarize-call` source moved from the private calls repo to
`plugins/summarize-call/skills/summarize-call/`. The calls repo retains a relative
symlink at `.claude/skills/summarize-call` for immediate local edits and enables the
public plugin in project settings for clean and cloud checkouts.

Checks:

- Git tracks the skill and marketplace here; `calls` tracks its link and project settings.
- `.env`, `.venv/`, and `data/` remain ignored.
- Fresh local and cloud Claude Code sessions can discover and read the skill.
- `summarize-call` is absent from the global `~/.claude/skills` namespace.
