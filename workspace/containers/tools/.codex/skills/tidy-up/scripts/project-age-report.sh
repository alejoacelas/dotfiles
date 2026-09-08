#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
now_epoch="$(date +%s)"
stale_days=14

cd "$root"

printf "%-10s %-24s %-12s %-12s %-8s %-8s %s\n" \
  "status" "project" "start" "last" "age" "remote" "note"

for status in active upcoming stable; do
  [ -d "$status" ] || continue
  for dir in "$status"/*/; do
    [ -d "$dir" ] || continue
    project="${dir%/}"
    name="${project##*/}"

    if [ -e "$project/.git" ]; then
      first="$(git -C "$project" log --reverse --date=short --format=%ad 2>/dev/null | head -1 || true)"
    last="$(git -C "$project" log -1 --date=short --format=%ad 2>/dev/null || true)"
    if git -C "$project" remote get-url origin >/dev/null 2>&1 || [ -n "$(git -C "$project" remote 2>/dev/null)" ]; then
      remote="yes"
    else
      remote="missing"
    fi
  else
    printf "%-10s %-24s %-12s %-12s %-8s %-8s %s\n" \
      "$status" "$name" "—" "—" "—" "group" "inspect child repositories"
    continue
    fi

    if [ -z "$last" ]; then
      printf "%-10s %-24s %-12s %-12s %-8s %-8s %s\n" \
        "$status" "$name" "${first:-unknown}" "unknown" "unknown" "$remote" "no commits found"
      continue
    fi

    last_epoch="$(date -j -f "%Y-%m-%d" "$last" +%s 2>/dev/null || date -d "$last" +%s 2>/dev/null || echo 0)"
    age_days="$(( (now_epoch - last_epoch) / 86400 ))"

    case "$status" in
      active)
        if [ "$age_days" -gt "$stale_days" ]; then
          note="review stale active status"
        else
          note="current"
        fi
        ;;
      upcoming) note="deferred" ;;
      stable) note="maintain when needed" ;;
    esac

    printf "%-10s %-24s %-12s %-12s %-8s %-8s %s\n" \
      "$status" "$name" "${first:-unknown}" "$last" "${age_days}d" "$remote" "$note"
  done
done
