#!/bin/sh
# Hide the calling pane; it comes back, without taking focus, when its agent's turn ends
# (finished, asks for something, or fails). Bound to ⌃⌘H in ../umi.config.
set -eu
umi="${UMI_CLI:-umi}"
pane="${UMI_PANE:?run from the Umi palette or a key}"
status="$("$umi" pane get "$pane" agent.status)"
until_q='agent.status=idle or agent.status=needs_input or agent.status=error or agent.status=stopped'
case "$status" in
  working)
    "$umi" pane hide "$pane" --until "$until_q" >/dev/null
    echo "Hidden until the turn ends" ;;
  "")
    echo "This pane has no agent; nothing would bring it back" >&2; exit 1 ;;
  *)
    # The turn already ended: wait for the next one to start, then for it to end.
    "$umi" pane hide "$pane" >/dev/null
    nohup sh -c '"$1" wait --pane "$2" --attr agent.status=working --timeout 7d >/dev/null &&
                 "$1" pane hide "$2" --until "$3" >/dev/null' sh "$umi" "$pane" "$until_q" >/dev/null 2>&1 &
    echo "Hidden until its next turn ends" ;;
esac
