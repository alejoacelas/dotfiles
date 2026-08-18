# Project-only call skills

The public `calls` plugin contains the `summarize-call` and `call-wiki` skills.
`bin/sync-project-skills` mirrors their tracked files into
`calls/.claude/skills/`; the dotfiles pre-commit hook blocks source commits while
either mirror differs. The plugin uses the package noun; each skill names its action.

Checks:

- Git tracks the skill and marketplace here; `calls` tracks the generated mirror.
- `.env`, `.venv/`, and `data/` remain ignored.
- `bin/sync-project-skills --check` reports an exact mirror.
- The mirrored Granola script still reads the ignored local key.
- Fresh local and calls-only-clone Claude sessions load `/summarize-call`.
- `summarize-call` is absent from the global `~/.claude/skills` namespace.

A cloud verification was dispatched from the same pushed calls revision:
[`session_01SBntx9YngxDPpFa6KdMnvH`](https://claude.ai/code/session_01SBntx9YngxDPpFa6KdMnvH).
The CLI and browser use different Claude accounts, so its response was not inspectable
from this machine; the isolated clone test covers the same missing-sibling-repo case.
