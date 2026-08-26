#!/bin/bash
# ~/.claude/settings.json must stay a symlink into this repo. Claude Code rewrites
# settings by replacing the file, which drops the link. If that happened, take the
# live copy as truth, put it in the repo, relink, and tell the user to commit.
set -u
repo="$HOME/best/ai/dotfiles/claude/settings.json"
live="$HOME/.claude/settings.json"
[ -L "$live" ] && exit 0
cp "$live" "$repo" && ln -sf "$repo" "$live" || {
  echo '{"systemMessage":"dotfiles: ~/.claude/settings.json is not a symlink and relinking failed"}'; exit 0; }
echo '{"systemMessage":"dotfiles: ~/.claude/settings.json had been replaced by a plain file; copied it into the repo and relinked. Commit ai/dotfiles."}'
