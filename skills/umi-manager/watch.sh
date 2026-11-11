#!/bin/sh
# Prints one line per event the manager must act on:
#   STOPPED <pane> <status>   a pane with owner=manager stopped (idle, needs_input or error)
#   OWNER <pane> <new owner>  a pane's owner changed (handed over with ⌃⌘E, or given back)
# Status events don't carry the pane's owner, so each one is checked with `umi pane get`.
# Extra arguments go to `umi events` (for example --since 10m to replay the log first).
umi events --filter pane.changed "$@" | while IFS= read -r l; do
  key=$(printf '%s' "$l" | sed -nE 's/.*"data":\{.*"key":"([^"]+)".*/\1/p')
  new=$(printf '%s' "$l" | sed -nE 's/.*"data":\{.*"new":"?([^",}]*)"?.*/\1/p')
  pane=$(printf '%s' "$l" | sed -nE 's/.*"data":\{.*"pane":"([^"]+)".*/\1/p')
  case "$key:$new" in
    agent.status:idle|agent.status:needs_input|agent.status:error)
      umi pane get "$pane" 2>/dev/null | grep -qx 'owner=manager' && echo "STOPPED $pane $new" ;;
    owner:*) echo "OWNER $pane $new" ;;
  esac
done
