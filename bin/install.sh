#!/usr/bin/env bash
# Symlink tracked dotfiles into the locations each tool reads from.
#
# Idempotent and safe to re-run:
#   - already linked correctly        -> no-op
#   - real file/dir in the way, repo doesn't track it yet -> move it into the repo (first-run migration)
#   - real file/dir in the way, repo already tracks it    -> back it up as <path>.pre-symlink.<timestamp>
set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

link() {  # link <repo-relative source> <absolute home target>
  local src="$DOTFILES/$1" dst="$2"
  mkdir -p "$(dirname "$src")" "$(dirname "$dst")"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    printf '  ok      %s\n' "${dst/#$HOME/~}"; return
  fi
  [ -L "$dst" ] && unlink "$dst"
  if [ -e "$dst" ] && [ ! -e "$src" ]; then
    mv "$dst" "$src";  printf '  moved   %s -> repo\n' "${dst/#$HOME/~}"
  elif [ -e "$dst" ]; then
    local b="$dst.pre-symlink.$(date +%Y%m%d%H%M%S)"
    mv "$dst" "$b";    printf '  backed  %s\n' "${b/#$HOME/~}"
  fi
  ln -s "$src" "$dst"; printf '  linked  %s\n' "${dst/#$HOME/~}"
}

echo "Linking dotfiles from $DOTFILES"
link claude/CLAUDE.md   "$HOME/.claude/CLAUDE.md"
link claude/skills      "$HOME/.claude/skills"
link codex/AGENTS.md    "$HOME/.codex/AGENTS.md"
link codex/config.toml  "$HOME/.codex/config.toml"
link codex/rules        "$HOME/.codex/rules"
link shell/zprofile     "$HOME/.zprofile"
link git/gitconfig      "$HOME/.gitconfig"

# Intentionally NOT linked: ~/.claude/settings.json
# Claude Code rewrites it, which would clobber a symlink. Kept a real file in place.
echo "Done."
