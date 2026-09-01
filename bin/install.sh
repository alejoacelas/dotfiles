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

real_dir() {  # real_dir <absolute path>; replace an old whole-directory link safely
  local dst="$1"
  if [ -L "$dst" ]; then
    local b="$dst.pre-directory.$(date +%Y%m%d%H%M%S)"
    mv "$dst" "$b"
    mkdir -p "$dst"
    printf '  backed  %s\n' "${b/#$HOME/~}"
  elif [ -e "$dst" ] && [ ! -d "$dst" ]; then
    local b="$dst.pre-directory.$(date +%Y%m%d%H%M%S)"
    mv "$dst" "$b"
    mkdir -p "$dst"
    printf '  backed  %s\n' "${b/#$HOME/~}"
  else
    mkdir -p "$dst"
  fi
}

prune_stale_dotfiles_skill_links() {  # prune_stale_dotfiles_skill_links <registry>
  local root="$1" skill target
  [ -d "$root" ] || return
  for skill in "$root"/*; do
    [ -L "$skill" ] || continue
    target="$(readlink "$skill")"
    case "$target" in
      "$DOTFILES"/claude/skills/*|"$DOTFILES"/codex/skills/*)
        if [ ! -e "$skill" ]; then
          unlink "$skill"
          printf '  pruned  %s (stale dotfiles skill)\n' "${skill/#$HOME/~}"
        fi
        ;;
    esac
  done
}

echo "Linking dotfiles from $DOTFILES"
link agents/AGENTS.md   "$HOME/.claude/CLAUDE.md"
# Keep the personal skills directory real. Standard skill installers place their own
# entries here; tracked dotfiles skills join them as per-skill links.
real_dir "$HOME/.claude/skills"
for skill in "$DOTFILES"/claude/skills/*; do
  [ -e "$skill" ] || continue
  name="$(basename "$skill")"
  link "claude/skills/$name" "$HOME/.claude/skills/$name"
done
for skill in "$HOME"/.claude/skills/*; do
  if [ -L "$skill" ] && [ ! -e "$skill" ]; then
    printf '  broken  %s -> %s\n' "${skill/#$HOME/~}" "$(readlink "$skill")" >&2
    exit 1
  fi
done
# Both tools read the same canonical agent instructions.
link agents/AGENTS.md   "$HOME/.codex/AGENTS.md"
link codex/hooks.json   "$HOME/.codex/hooks.json"
link codex/rules        "$HOME/.codex/rules"
# Codex owns ~/.codex/skills/.system, so link each compatible skill without replacing
# the directory. ~/.agents/skills is the universal root used by account-scoped Codex
# runtimes such as Orca. Shared skills can be symlinked into codex/skills from
# claude/skills; that entry is the explicit compatibility decision.
real_dir "$HOME/.agents/skills"
for skill in "$DOTFILES"/codex/skills/*; do
  [ -e "$skill" ] || continue
  name="$(basename "$skill")"
  link "codex/skills/$name" "$HOME/.agents/skills/$name"
  link "codex/skills/$name" "$HOME/.codex/skills/$name"
done
link claude/skills/human-edit-tracking "$HOME/.codex/skills/human-edit-tracking"
prune_stale_dotfiles_skill_links "$HOME/.claude/skills"
prune_stale_dotfiles_skill_links "$HOME/.agents/skills"
prune_stale_dotfiles_skill_links "$HOME/.codex/skills"
for root in "$HOME"/Library/Application\ Support/orca/codex-accounts/*/home/skills; do
  prune_stale_dotfiles_skill_links "$root"
done
# The app owns config.toml; CLI-only overrides live in the explicit cli profile.
link codex/cli.config.toml "$HOME/.codex/cli.config.toml"
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

# Keep project-only skills available in clean/cloud checkouts without installing them
# globally. This is a no-op when the private calls repo is not cloned.
"$DOTFILES/bin/sync-project-skills"

# Keep machine-local or secret settings in ~/.claude/settings.local.json (untracked) —
# never in the tracked settings.json linked above.
echo "Done."
