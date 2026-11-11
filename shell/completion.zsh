# zsh completion. ~/.zshrc sources this file.
#   Tab   fills in the start all matches share; Tab again lists them and cycles through them (carapace adds descriptions)
#   →     accepts the grey suggestion from history (zsh-autosuggestions)
# Needs: brew install carapace zsh-autosuggestions

# Warp has its own completion, and these need a terminal to draw in.
[[ $TERM_PROGRAM == WarpTerminal || ! -t 0 || ! -t 1 ]] && return

autoload -Uz compinit && compinit

# Descriptions for ~1,000 command-line tools; tools carapace doesn't know fall back to zsh's own.
export CARAPACE_BRIDGES='zsh,fish,bash,inshellisense'
source <(carapace _carapace zsh)

zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}

source "/opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
ZSH_AUTOSUGGEST_STRATEGY=(history)
