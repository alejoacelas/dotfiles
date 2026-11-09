#!/bin/sh
# Hand the calling pane to the manager pane (role=manager) and hide it. The umi-manager skill
# answers what it can and brings the pane back, marked escalated=true, when it needs Alejo.
set -eu
umi="${UMI_CLI:-umi}"
pane="${UMI_PANE:?run from the Umi palette or a key}"
if ! "$umi" ls --where 'role=manager' | grep -q ' pane '; then
  echo "No manager pane: run the umi-manager skill in one first" >&2; exit 1
fi
"$umi" pane set "$pane" owner=manager >/dev/null
"$umi" pane hide "$pane" >/dev/null
echo "Delegated to the manager"
