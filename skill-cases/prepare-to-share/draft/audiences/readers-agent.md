# Reader's agent

The Claude Code, Codex or Cowork session a reader points at the repository. It reads `AGENTS.md` automatically and follows it literally.

## Knows

- Standard tools, languages and commands, and how to read code.
- How to search documentation and the web.

## Explain

- Where things live in the project, which commands to run, and how to check they worked.
- Constraints it can't infer: what must never be committed, what needs the user's approval, which files must stay consistent.
- What to hand back to the human, such as signing in, paying, or approving access.

## Looks for first

`AGENTS.md`, then the README. Keep both correct for any user, not just the author.
