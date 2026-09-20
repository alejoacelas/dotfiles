# dotfiles

My shell, Git, agent configuration and skills. The files live here;
[`bin/install.sh`](bin/install.sh) links them into the locations each tool reads.
Inspired by [benthamite/dotfiles](https://github.com/benthamite/dotfiles).

## Install or repair links

```sh
mkdir -p ~/best
git clone https://github.com/alejoacelas/dotfiles ~/best/dotfiles
brew bundle --file ~/best/dotfiles/Brewfile
~/best/dotfiles/bin/install.sh
```

On an existing machine, run just the last command. The installer links configuration
and skills, sets up workspace container files, enables the repository's commit guard,
and installs the shared-context startup hook. It backs up conflicting real files.
It requires `uv`, creates an isolated Python environment, and includes Orca's
account-specific Codex homes. The Codex app retains ownership of its base config.

Employer context comes from a separate private clone at
`~/.local/share/agent-context/private`.

## Where things live

| Source | Used by |
|---|---|
| `agents/AGENTS.md` | Global Claude and Codex instructions |
| `agents/workflows.md` | Workspace procedures linked from those instructions |
| `claude/settings.json`, `claude/hooks/` | Claude settings and hooks |
| `skills/` | Shared custom skills for Claude Code and Codex |
| `claude/skills/`, `codex/skills/` | Client-specific exceptions |
| `codex/hooks.json`, `codex/rules/` | Codex hooks and rules |
| `codex/cli.config.toml` | CLI settings for `codex --profile cli` |
| `plugins/` | Public plugin sources and shared skills |
| `shell/zprofile`, `git/gitconfig`, `Brewfile` | Shell, Git and Homebrew configuration |
| `workspace/` | Live configuration for ordinary folders under `~/best/` |

`workspace/` mirrors `~/best/`: for example, `workspace/tools/AGENTS.md` supplies
`~/best/tools/AGENTS.md` through a symlink. Individual repositories keep their own
instructions; this tree manages ordinary container folders.

Create custom skills in `skills/<name>/SKILL.md`, then run `bin/install.sh`.
They install into `~/.claude/skills/`, `~/.agents/skills/` and `~/.codex/skills/`
from one source. For a plugin-owned skill, add a symlink in `skills/` to its source.
Reserve `claude/skills/` and `codex/skills/` for client-specific exceptions;
each skill name should appear in only one source directory per client.
Installed registries remain real directories so other installers can add skills.

`bin/check-agent-config` checks each installed registry against the shared sources
and its client-specific additions. Missing skills and broken links fail; changed
skill text is reported as drift. Other installed skills are listed as unmanaged.

[`stripe-projects`](skills/stripe-projects/SKILL.md) is our locally maintained
workflow for Stripe's CLI. It reuses projects and credentials where possible and
skips generated agent instructions. Update it against CLI help and Stripe's
reference; installing an upstream skill is unnecessary.

[`summarize-call`](plugins/calls/skills/summarize-call/SKILL.md) is the official
call workflow for both agents. It files in `~/best/calls` under that repository's
instructions. The calls plugin also supplies `call-wiki` and `wiki-comments`,
mirrored into `writing/ai-guides` for standalone checkouts. The older synced
`summarise-granola` skill is disabled through Claude's `skillOverrides`, including
its `anthropic-skills:` name, so account sync cannot reactivate it locally. The
[marketplace](.claude-plugin/marketplace.json) exposes the plugin independently.

Historical instruction snapshots remain in Git history. Archived workspace files
live independently under `~/best/archive/`. Current decisions and their reasons live in
[`DECISIONS.md`](DECISIONS.md).

Repository tests live in `tests/`; skill-specific tests travel with their skill
in its own `tests/` directory.

## Private skills

Private skill sources live in an optional, independent repository. To install them:

```sh
gh repo clone alejoacelas/private-skills ~/best/dotfiles/private-skills
~/best/dotfiles/bin/install.sh
```

`private-skills/` is Git-ignored here and retains its own history and private remote.
Create private custom skills in its `skills/` directory for both clients. The
installer also supports its `claude/skills/` and `codex/skills/` exceptions.
Public-only installations work without that checkout. Make private-skill changes
and commits inside it; the parent repository tracks installation code only.

## Common maintenance

```sh
bin/check-agent-config                    # broken links, missing skills, differences
bin/sync-project-skills                   # refresh ai-guides plugin mirrors
bin/sync-project-skills --check           # check mirrors without writing
bin/agent-context check /path/to/project  # inspect selected context
~/.local/share/agent-context/venv/bin/python -m unittest discover -s tests
~/.local/share/agent-context/venv/bin/python -m unittest discover -s plugins/calls/skills/summarize-call/tests
```

Shared context is selected explicitly per repository with
`bin/agent-context adopt /path/to/project --groups 80k --visibility private`.
An empty `--groups` removes a selection. Public selections live in
`agents/projects.json`; private selections live in the private clone's
`projects.json`. Linked worktrees reuse the main checkout's selection.
Startup reads context without rewriting project files. Errors and installer
backups live in `~/.local/state/agent-context/`.

Claude's settings-saving behavior can replace its symlink with a copy. The
session-start relinking hook preserves that copy in this repo and restores the
link, reporting when a commit is needed.

API keys live in 1Password and are retrieved into ignored, owner-only `.env` files.
The commit guard detects common credential patterns and stale plugin mirrors.
Maintenance rules are in [`AGENTS.md`](AGENTS.md).
