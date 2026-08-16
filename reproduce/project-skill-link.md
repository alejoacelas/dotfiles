# Project-only skill link

The public `summarize-call` source moved from the private calls repo to
`plugins/summarize-call/skills/summarize-call/`. `bin/sync-project-skills` mirrors its
tracked files into `calls/.claude/skills/summarize-call/`; the dotfiles pre-commit hook
blocks source commits while that mirror differs.

Checks:

- Git tracks the skill and marketplace here; `calls` tracks the generated mirror.
- `.env`, `.venv/`, and `data/` remain ignored.
- Fresh local and cloud Claude Code sessions can discover and read the skill.
- `summarize-call` is absent from the global `~/.claude/skills` namespace.
