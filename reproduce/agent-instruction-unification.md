# Agent instruction unification

On 2026-08-16, Alejo asked to make the agent-instruction setup legible without adding
anything recurrent or invisible.

The canonical global source moved from `claude/CLAUDE.md` to `agents/AGENTS.md`.
`bin/install.sh` links it to both paths the tools read:

- `~/.codex/AGENTS.md`
- `~/.claude/CLAUDE.md`

Project instructions now use the same rule: real instructions live in `AGENTS.md`, and
`CLAUDE.md` links to it. The `best` root was migrated; `80k` already followed the rule.
Nested Git repositories remain separate instruction roots, so they inherit the global
file but not `best/AGENTS.md`.

The existing on-demand `bin/check-agent-config` was left unchanged. No scheduled job,
hook, or other recurrent behavior was added.

Checks:

- Resolve the two global live links to `agents/AGENTS.md`.
- Confirm `best/CLAUDE.md` and `80k/CLAUDE.md` resolve to their local `AGENTS.md`.
- Run `bin/check-agent-config`, `best/ai/sync-repos.py --check`, and
  `bin/sync-project-skills --check`.
- Search maintained files for the superseded `claude/CLAUDE.md` source path.
