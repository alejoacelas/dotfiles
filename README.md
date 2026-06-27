# dotfiles

My machine config in one place: AI-agent instructions, shell, git, and the Homebrew
package list. The repo holds the real files; `bin/install.sh` symlinks them into the
paths each tool reads from. Inspired by [benthamite/dotfiles](https://github.com/benthamite/dotfiles).

## Layout

```
claude/CLAUDE.md      global Claude Code instructions   ->  ~/.claude/CLAUDE.md
claude/skills/        reusable Claude skills            ->  ~/.claude/skills
codex/AGENTS.md       global Codex instructions         ->  ~/.codex/AGENTS.md
codex/config.toml     Codex settings                    ->  ~/.codex/config.toml
codex/rules/          Codex rules                       ->  ~/.codex/rules
shell/zprofile        PATH + dev environment            ->  ~/.zprofile
git/gitconfig         git identity                      ->  ~/.gitconfig
Brewfile              every Homebrew tap/formula/cask
bin/install.sh        creates and repairs the symlinks
```

## Install (or re-link) on a machine

```sh
git clone https://github.com/alejoacelas/dotfiles ~/.dotfiles
~/.dotfiles/bin/install.sh          # idempotent; backs up anything already in the way
brew bundle --file ~/.dotfiles/Brewfile
```

The repo file *is* the live file (via symlink), so edit it here and both the repo and
the tool see the change. `install.sh` is safe to re-run — it repairs links and never
overwrites data.

## Not symlinked, on purpose

`~/.claude/settings.json` stays a real file in place: Claude Code rewrites it and would
clobber a symlink. It isn't tracked here.
