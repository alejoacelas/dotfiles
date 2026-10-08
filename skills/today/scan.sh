#!/usr/bin/env bash
# scan.sh: facts for the start-of-day review of ~/best. Read-only.
set -uo pipefail
BEST="${BEST:-$HOME/best}"
DAYS="${DAYS:-14}"
cutoff=$(( $(date +%s) - DAYS * 86400 ))

last_touch() {  # newest of last commit time and newest file mtime outside .git
  local d="$1" c m
  c=$(git -C "$d" log -1 --format=%ct 2>/dev/null || echo 0)
  m=$(find "$d" -path '*/.git' -prune -o -type f -print0 2>/dev/null | xargs -0 stat -f %m 2>/dev/null | sort -n | tail -1)
  echo $(( ${c:-0} > ${m:-0} ? ${c:-0} : ${m:-0} ))
}
age() { echo $(( ($(date +%s) - $1) / 86400 ))d; }

echo "## Unsaved work"
find "$BEST" -maxdepth 6 -name .git \
  -not -path "$BEST/archive/*" -not -path '*/archive/*' -not -path '*/scratch/*' \
  -not -path '*/.supervise/*' -not -path '*/worktree-archive/*' -not -path '*/node_modules/*' \
  2>/dev/null | sed 's|/.git$||' | sort | while read -r g; do
  dirty=$(git -C "$g" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  if ! git -C "$g" remote | grep -q .; then note="no remote"
  elif ! git -C "$g" rev-parse -q --verify '@{u}' >/dev/null 2>&1; then note="branch not pushed"
  else ahead=$(git -C "$g" rev-list --count '@{u}..HEAD' 2>/dev/null); [ "$ahead" = 0 ] && note="" || note="$ahead unpushed"
  fi
  [ "$dirty" != 0 ] && note="${note:+$note, }$dirty uncommitted"
  [ -n "$note" ] && echo "- ${g#$BEST/}: $note"
done

echo; echo "## Inbox items older than ${DAYS} days"
for d in "$BEST"/inbox/*/; do
  [ -d "$d" ] || continue; t=$(last_touch "$d")
  [ "$t" -lt "$cutoff" ] && echo "- inbox/$(basename "$d"): untouched $(age "$t")"
done

echo; echo "## Projects untouched for ${DAYS} days"
for d in "$BEST"/projects/[0-9][0-9][0-9][0-9]-*/ "$BEST"/clients/*/[0-9][0-9][0-9][0-9]-*/; do
  [ -d "$d" ] || continue; t=$(last_touch "$d")
  [ "$t" -lt "$cutoff" ] && echo "- ${d#$BEST/}: untouched $(age "$t")"
done

echo; echo "## Still running or billing"
find "$BEST" -maxdepth 5 -name AGENTS.md -not -path '*/node_modules/*' -print0 2>/dev/null \
  | xargs -0 grep -H -i '^- Still running or billing:' 2>/dev/null \
  | grep -vi 'billing: *none *$' | sed "s|^$BEST/||; s|/AGENTS.md:- Still running or billing:| —|"

echo; echo "## Trials still running"
grep -E '\| *running *\|' "$BEST/trials/README.md" 2>/dev/null | cut -d'|' -f2 | sed 's/^ */- /'
exit 0
