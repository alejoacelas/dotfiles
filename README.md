# dotfiles

My machine config in one place: AI-agent instructions, shell, git, and the Homebrew
package list. The repo holds the real files; `bin/install.sh` symlinks them into the
paths each tool reads from. Inspired by [benthamite/dotfiles](https://github.com/benthamite/dotfiles).

## Layout

```
claude/CLAUDE.md      global Claude Code instructions   ->  ~/.claude/CLAUDE.md
claude/settings.json  permissions / model / theme       ->  ~/.claude/settings.json
claude/skills/        reusable Claude skills            ->  ~/.claude/skills
codex/AGENTS.md       global Codex instructions         ->  ~/.codex/AGENTS.md
codex/config.toml     Codex settings                    ->  ~/.codex/config.toml
codex/rules/          Codex rules                       ->  ~/.codex/rules
shell/zprofile        PATH + dev environment            ->  ~/.zprofile
git/gitconfig         git identity                      ->  ~/.gitconfig
Brewfile              every Homebrew tap/formula/cask
bin/install.sh        creates and repairs the symlinks
hooks/pre-commit      blocks committing obvious secrets
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

## Secrets

`settings.json` is tracked and public — credentials don't belong in it. Keep anything
machine-local or secret in `~/.claude/settings.local.json`, which is never tracked. The
`hooks/pre-commit` guard (enabled by `install.sh`) blocks any commit that looks like it
contains a credential; override a false positive with `git commit --no-verify`.
