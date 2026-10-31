#!/usr/bin/env bash
# watch-worker.sh <session-id> <slug> [timeout-seconds]
# Starts a detached watcher: it waits for the warp-agent worker, saves the result to
# .supervise/<slug>/wait.out, then types a wake-up message into this supervisor's
# session, which starts a new turn. Run from the worktree root.
set -u
worker=$1 slug=$2 timeout=${3:-14400}
out="$PWD/.supervise/$slug/wait.out"
msg="Watcher: wait for worker $slug ended; see .supervise/$slug/wait.out"
me=${WARP_AGENT_ID:?this session was not launched by warp-agent, so nothing can wake it; run warp-agent wait in the foreground}
nohup sh -c 'warp-agent wait "$1" --timeout "$2" > "$3" 2>&1; warp-agent send "$4" "$5"' \
  watcher "$worker" "$timeout" "$out" "$me" "$msg" >/dev/null 2>&1 &
echo "watching $slug"
