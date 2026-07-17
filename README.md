<!--ai-->
# dotfiles
<!--/ai-->

<!--ai-->
My machine config in one place: AI-agent instructions, shell, git, and the Homebrew
package list. The repo holds the real files; `bin/install.sh` symlinks them into the
paths each tool reads from. Inspired by [benthamite/dotfiles](https://github.com/benthamite/dotfiles).
<!--/ai-->

<!--ai-->
## Layout
<!--/ai-->

<!--ai-->
```
claude/CLAUDE.md         agent instructions (shared)    ->  ~/.claude/CLAUDE.md  &  ~/.codex/AGENTS.md
claude/settings.json     permissions / model / theme    ->  ~/.claude/settings.json
claude/skills/           reusable Claude skills         ->  ~/.claude/skills
codex/skills/            personal and shared skills     ->  ~/.codex/skills/<skill>
codex/rules/             Codex rules                    ->  ~/.codex/rules
codex/config.reference.toml  snapshot of Codex settings (Codex owns the live file)
shell/zprofile           PATH + dev environment         ->  ~/.zprofile
git/gitconfig            git identity + gh credentials  ->  ~/.gitconfig
Brewfile                 every Homebrew tap/formula/cask
bin/install.sh           creates and repairs the symlinks
hooks/pre-commit         blocks committing obvious secrets
```
<!--/ai-->

<!--ai-->
Both Claude and Codex read the one `claude/CLAUDE.md`. Codex rewrites its
`~/.codex/config.toml` constantly, so it owns that file directly (not symlinked);
`codex/config.reference.toml` is the snapshot to seed a fresh machine from.
<!--/ai-->

<!--ai-->
## Install (or re-link) on a machine
<!--/ai-->

<!--ai-->
This repo lives inside the `best` workspace at `~/best/ai/dotfiles`. On a fresh
machine, clone `best` first, then this repo into it:
<!--/ai-->

<!--ai-->
```sh
git clone https://github.com/alejoacelas/best ~/best
git clone https://github.com/alejoacelas/dotfiles ~/best/ai/dotfiles
~/best/ai/dotfiles/bin/install.sh   # idempotent; backs up anything in the way
brew bundle --file ~/best/ai/dotfiles/Brewfile
```
<!--/ai-->

<!--ai-->
The repo file *is* the live file (via symlink), so edit it here and both the repo and
the tool see the change. `install.sh` is safe to re-run — it repairs links and never
overwrites data.
<!--/ai-->

<!--ai-->
## Secrets
<!--/ai-->

<!--ai-->
`settings.json` is tracked and public — credentials don't belong in it. Keep anything
machine-local or secret in `~/.claude/settings.local.json`, which is never tracked. The
`hooks/pre-commit` guard (enabled by `install.sh`) blocks any commit that looks like it
contains a credential; override a false positive with `git commit --no-verify`.
<!--/ai-->
