#!/bin/bash
# Silence the "codex: available" and "hive: run /hive:align" SessionStart banners.
# Patches the cached plugin scripts idempotently; run from settings.json SessionStart
# so plugin updates get re-patched on the next session.
set -u
cache="$HOME/.claude/plugins/cache"

for f in "$cache"/codex-plugin-cc/codex/*/hooks/session-start.sh; do
  [ -f "$f" ] || continue
  grep -q 'del(.systemMessage)' "$f" && continue
  sed -i '' 's|^echo "\$result"$|echo "$result" \| jq -c '"'"'del(.systemMessage)'"'"' 2>/dev/null \|\| echo "$result"|' "$f"
done

for f in "$cache"/alignment-hive/hive/*/hooks/session-start.sh; do
  [ -f "$f" ] || continue
  grep -q 'hive:align' "$f" && continue
  sed -i '' 's|^echo "\$HOOK_INPUT" \| "\${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.sh" session-start 2>>"\$ERROR_LOG" \|\| true$|out=$(echo "$HOOK_INPUT" \| "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.sh" session-start 2>>"$ERROR_LOG" \|\| true); [ -n "$out" ] \&\& { echo "$out" \| jq -c '"'"'if (.systemMessage // "" \| test("hive:align")) then del(.systemMessage) else . end'"'"' 2>/dev/null \|\| echo "$out"; }|' "$f"
done
exit 0
