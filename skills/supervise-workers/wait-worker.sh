#!/usr/bin/env bash
# wait-worker.sh <terminal-handle> <since-epoch-ms> [timeout-seconds]
# Waits until the agent in an Orca terminal finishes its turn ("done") or needs an
# answer ("waiting"), using the state Orca's agent hooks record. Only states that
# started after <since-epoch-ms> count, so the previous turn's "done" is ignored.
# Prints one line: DONE|WAITING|TIMEOUT|GONE|ERR, then the worker's last message.
# Exit codes: 0 done/waiting, 1 timeout, 2 hook state unreadable, 3 terminal gone.
set -u
h=$1 since=$2 timeout=${3:-1200}
f="${ORCA_USER_DATA_PATH:-$HOME/Library/Application Support/orca}/agent-hooks/last-status.json"
pane=$(orca terminal list --json | jq -r --arg h "$h" \
  '.result.terminals[] | select(.handle == $h) | "\(.tabId):\(.leafId)"')
[ -n "$pane" ] || { echo "GONE terminal $h not found"; exit 3; }
end=$(( $(date +%s) + timeout ))
while :; do
  row=$(jq -c --arg k "$pane" '.entries[$k] // {} |
    {state: .payload.state, at: .stateStartedAt, msg: (.payload.lastAssistantMessage // "")}' "$f" 2>/dev/null) \
    || { echo "ERR cannot read $f (Orca may have changed its format)"; exit 2; }
  state=$(jq -r .state <<<"$row"); at=$(jq -r '.at // 0' <<<"$row")
  if [ "$at" -ge "$since" ] && { [ "$state" = done ] || [ "$state" = waiting ]; }; then
    echo "$(tr a-z A-Z <<<"$state")"; jq -r '.msg | .[0:2000]' <<<"$row"; exit 0
  fi
  if [ "$(date +%s)" -ge "$end" ]; then
    orca terminal list --json | jq -e --arg h "$h" '.result.terminals[] | select(.handle == $h)' >/dev/null \
      || { echo "GONE terminal $h closed"; exit 3; }
    echo "TIMEOUT state=$state"; exit 1
  fi
  sleep 5
done
