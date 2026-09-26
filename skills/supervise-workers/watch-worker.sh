#!/usr/bin/env bash
# watch-worker.sh <terminal-handle> <since-epoch-ms> <slug> [timeout-seconds]
# Starts a detached watcher: it runs wait-worker.sh, saves the result to
# .supervise/<slug>/wait.out, then types a wake-up message into this supervisor's
# Orca terminal, which starts a new turn. Run from the worktree root.
set -u
h=$1 since=$2 slug=$3 timeout=${4:-14400}
me=${ORCA_TERMINAL_HANDLE:?not running in an Orca terminal}
out="$PWD/.supervise/$slug/wait.out"
wait="$(cd "$(dirname "$0")" && pwd)/wait-worker.sh"
msg="Watcher: wait for worker $slug ended; see .supervise/$slug/wait.out"
nohup sh -c '"$1" "$2" "$3" "$4" > "$5" 2>&1; orca terminal send --terminal "$6" --text "$7" --enter' \
  watcher "$wait" "$h" "$since" "$timeout" "$out" "$me" "$msg" >/dev/null 2>&1 &
echo "watching $slug"
