# dotfiles

My macOS environment setup — shell, git, and the full Homebrew package list.

## What's here
- `Brewfile` — every Homebrew tap, formula, and cask I have installed.
- `zprofile` — PATH and dev-environment setup (Homebrew, Python 3.13, Rust) → `~/.zprofile`
- `gitconfig` — git identity → `~/.gitconfig`

## Install
These are copies, not symlinks. Put each where it belongs, then load the packages:

```sh
cp zprofile  ~/.zprofile
cp gitconfig ~/.gitconfig
brew bundle --file Brewfile      # install everything in the Brewfile
```

Refresh the package snapshot anytime with `brew bundle dump --force --file Brewfile`.
