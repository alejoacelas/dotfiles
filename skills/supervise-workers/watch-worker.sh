#!/usr/bin/env bash
# watch-worker.sh <worker> <since-epoch-ms> <slug> [timeout-seconds]
# Starts a detached watcher: it waits for the worker, saves the result to
# .supervise/<slug>/wait.out, then types a wake-up message into this supervisor's
# session, which starts a new turn. Run from the worktree root.
# <worker> is an Orca terminal handle (term_...) or a warp-agent session ID; for
# warp-agent pass "-" as <since>, because `warp-agent wait` tracks it itself.
set -u
worker=$1 since=$2 slug=$3 timeout=${4:-14400}
out="$PWD/.supervise/$slug/wait.out"
msg="Watcher: wait for worker $slug ended; see .supervise/$slug/wait.out"
if [[ $worker == term_* ]]; then
  me=${ORCA_TERMINAL_HANDLE:?not running in an Orca terminal}
  wait="$(cd "$(dirname "$0")" && pwd)/wait-worker.sh"
  nohup sh -c '"$1" "$2" "$3" "$4" > "$5" 2>&1; orca terminal send --terminal "$6" --text "$7" --enter' \
    watcher "$wait" "$worker" "$since" "$timeout" "$out" "$me" "$msg" >/dev/null 2>&1 &
else
  me=${WARP_AGENT_ID:?this session was not launched by warp-agent, so nothing can wake it; run warp-agent wait in the foreground}
  nohup sh -c 'warp-agent wait "$1" --timeout "$2" > "$3" 2>&1; warp-agent send "$4" "$5"' \
    watcher "$worker" "$timeout" "$out" "$me" "$msg" >/dev/null 2>&1 &
fi
echo "watching $slug"
