# dotfiles

My machine config in one place: AI-agent instructions, shell, git, and the Homebrew
package list. The repo holds the real files; `bin/install.sh` symlinks them into the
paths each tool reads from. Inspired by [benthamite/dotfiles](https://github.com/benthamite/dotfiles).

## Layout

```
agents/AGENTS.md         agent instructions (shared)    ->  ~/.claude/CLAUDE.md  &  ~/.codex/AGENTS.md
claude/settings.json     permissions / model / theme    ->  ~/.claude/settings.json
claude/skills/           Claude-compatible skills       ->  ~/.claude/skills/<skill>
plugins/                 public Claude plugins enabled by selected projects
codex/skills/            Codex-compatible skills        ->  ~/.agents/skills/<skill> & ~/.codex/skills/<skill>
codex/hooks.json         Codex lifecycle hooks           ->  ~/.codex/hooks.json
codex/rules/             Codex rules                    ->  ~/.codex/rules
codex/config.reference.toml  snapshot of Codex settings (Codex owns the live file)
shell/zprofile           PATH + dev environment         ->  ~/.zprofile
git/gitconfig            git identity + gh credentials  ->  ~/.gitconfig
Brewfile                 every Homebrew tap/formula/cask
bin/install.sh           creates links and refreshes project-skill mirrors
bin/sync-project-skills  updates/checks private project mirrors
hooks/pre-commit         blocks secrets and stale project-skill mirrors
AGENTS.md                link to this README for repo-local agent instructions
CLAUDE.md                link to AGENTS.md
```

Both Claude and Codex read the one `agents/AGENTS.md`. Codex rewrites its
`~/.codex/config.toml` constantly, so it owns that file directly (not symlinked);
`codex/config.reference.toml` is the snapshot to seed a fresh machine from.
Both tools run the shared human-edit tracker on user prompts; it stays silent unless a
Markdown file's uncommitted changes carry the `;;` marker.

The product directories are compatibility lists, not necessarily canonical sources.
A shared skill may live under `claude/skills` and have a relative link under
`codex/skills`; `use-slack` does this. Put a skill in both lists only after it
works in both agents. `bin/check-agent-config` reports one-sided skills and fails if a
Codex-compatible skill is absent from either Codex registry.

`~/.claude/skills`, `~/.agents/skills`, and `~/.codex/skills` remain real directories
so standard installers can add entries. `bin/install.sh` links Claude-compatible
skills into the first and Codex-compatible skills into both Codex registries. The
universal registry matters when a host such as Orca gives Codex an account-specific
home instead of `~/.codex`. For example, `orca skills install --skill orca-cli` uses
the community installer to target Claude Code, Codex, and the universal registry.
The installer also removes dangling dotfiles-owned links left by skill renames.

## Project-only plugins

Keep public skills that should not load globally under `plugins/`. Projects that must
work in isolated or cloud checkouts carry a generated mirror.

Name each plugin for the whole package, normally with a concise noun; name its skills
for their individual actions. For example, `calls` contains `summarize-call` and
`call-wiki`.

| Public source | Project wiring |
|---|---|
| [`plugins/calls/`](plugins/calls/) | `calls/.claude/skills/{call-wiki,summarize-call}/` |

The marketplace at [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)
also makes the plugin independently installable. Edit the public source here, run
`bin/sync-project-skills`, then commit and push both repos. The dotfiles pre-commit hook
blocks source changes while the calls mirror differs; `bin/install.sh` also refreshes it.
Do not edit the generated mirror or put project-only skills under `claude/skills/`, which
`install.sh` exposes globally. The mirror's ignored `.env` and `.venv` link to the local
source; generated `data/` remains private to `calls`.

The root `AGENTS.md` links to this README and `CLAUDE.md` links to `AGENTS.md`, so agents
editing this repo see the ownership map automatically.

## Install (or re-link) on a machine

This repo lives inside the `best` workspace at `~/best/ai/dotfiles`. On a fresh
machine, clone `best` first, then this repo into it:

```sh
git clone https://github.com/alejoacelas/best ~/best
git clone https://github.com/alejoacelas/dotfiles ~/best/ai/dotfiles
~/best/ai/dotfiles/bin/install.sh   # idempotent; backs up anything in the way
brew bundle --file ~/best/ai/dotfiles/Brewfile
```

The repo file *is* the live file (via symlink), so edit it here and both the repo and
the tool see the change. `install.sh` is safe to re-run — it repairs links and never
overwrites data.

## Secrets

`settings.json` is tracked and public — credentials don't belong in it. Keep anything
machine-local or secret in `~/.claude/settings.local.json`, which is never tracked. The
`hooks/pre-commit` guard (enabled by `install.sh`) blocks any commit that looks like it
contains a credential; override a false positive with `git commit --no-verify`.
