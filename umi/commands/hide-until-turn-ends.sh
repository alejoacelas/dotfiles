#!/bin/sh
# Hide the calling pane; it comes back, without taking focus, when its agent's turn ends (finished,
# asks for something, or fails). If the turn already ended, the next one counts. Bound to ⌃⌘H in
# ../umi.config.
set -eu
umi="${UMI_CLI:-umi}"
pane="${UMI_PANE:?run from the Umi palette or a key}"
if [ -z "$("$umi" pane get "$pane" agent.kind)" ]; then
  echo "This pane has no agent; nothing would bring it back" >&2; exit 1
fi
now="$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"
"$umi" pane hide "$pane" --until "(agent.status=idle or agent.status=needs_input or agent.status=error or agent.status=stopped) and status_since>$now" >/dev/null
echo "Hidden until its turn ends"
