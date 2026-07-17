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
# Codex reads AGENTS.md; point it at the one CLAUDE.md so there's a single source.
link claude/CLAUDE.md   "$HOME/.codex/AGENTS.md"
link codex/rules        "$HOME/.codex/rules"
# Codex owns ~/.codex/skills/.system, so link each personal skill without replacing
# the directory. Shared skills can be symlinked into codex/skills from claude/skills.
for skill in "$DOTFILES"/codex/skills/*; do
  [ -e "$skill" ] || continue
  name="$(basename "$skill")"
  link "codex/skills/$name" "$HOME/.codex/skills/$name"
done
# codex/config.toml is NOT linked: Codex rewrites it constantly (trust entries,
# timestamps), so it owns ~/.codex/config.toml directly. codex/config.reference.toml
# is a tracked snapshot to seed a fresh machine from.
link shell/zprofile       "$HOME/.zprofile"
link git/gitconfig        "$HOME/.gitconfig"
link claude/settings.json "$HOME/.claude/settings.json"

# Enable the repo's tracked git hooks (the secret-scan pre-commit guard).
git -C "$DOTFILES" config core.hooksPath hooks

# Enable the best workspace's tracked git hooks (the sync-repos drift guard), when this
# dotfiles repo is nested inside best (best/ai/dotfiles) rather than cloned standalone.
BEST="$(cd "$DOTFILES/../.." && pwd)"
if [ -e "$BEST/ai/sync-repos.py" ] && git -C "$BEST" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "$BEST" config core.hooksPath ai/githooks
  echo "  hooks   best -> ai/githooks"
fi

# Keep machine-local or secret settings in ~/.claude/settings.local.json (untracked) —
# never in the tracked settings.json linked above.
echo "Done."
