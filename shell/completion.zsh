# Warp-style completion for zsh. ~/.zshrc sources this file.
#   Tab   opens a filterable menu of subcommands, flags and files, with descriptions (fzf-tab, carapace)
#   →     accepts the grey suggestion from history (zsh-autosuggestions)
# Needs: brew install fzf fzf-tab carapace zsh-autosuggestions

autoload -Uz compinit && compinit

# Descriptions for ~1,000 command-line tools; tools carapace doesn't know fall back to zsh's own.
export CARAPACE_BRIDGES='zsh,fish,bash,inshellisense'
source <(carapace _carapace zsh)

zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
# With `menu yes` the first Tab opens the menu; otherwise it first fills in the start all matches share.
zstyle ':completion:*' menu yes
zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}

# fzf-tab must load after compinit and before zsh-autosuggestions.
source "$HOMEBREW_PREFIX/share/fzf-tab/fzf-tab.zsh"
zstyle ':fzf-tab:*' fzf-flags --height=12 --layout=reverse --info=hidden --no-separator --border=rounded
zstyle ':fzf-tab:*' show-group none
zstyle ':fzf-tab:*' prefix ''
# Start the filter from what the matches share: carapace's paths never match the typed folder (`/usr/`).
zstyle ':fzf-tab:*' query-string prefix
zstyle ':fzf-tab:*' group-colors ''
zstyle ':fzf-tab:*' switch-group '<' '>'

source "$HOMEBREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
ZSH_AUTOSUGGEST_STRATEGY=(history)
