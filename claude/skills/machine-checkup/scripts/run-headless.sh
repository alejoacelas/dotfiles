#!/bin/zsh -l
# Non-interactive machine checkup, for a scheduler (launchd/cron) to call.
# `-l` loads the login shell so PATH finds `claude`, `git`, `gh`, `brew`.
#
# Runs Claude in headless mode to execute the machine-checkup skill, which scans,
# fixes the reversible findings, writes a dated report, and updates the backlog.
# Not installed anywhere by default — see machine/recurring-checkups.md to schedule it.
set -euo pipefail

cd "$HOME/best"
mkdir -p "$HOME/best/ai/checkups"
LOG="$HOME/best/ai/checkups/.last-run.log"

claude -p "Run the machine-checkup skill: scan, write today's dated report under \
ai/checkups/, and append new items to ai/improvements.md. Report only — \
change nothing else. Then stop." \
  --permission-mode acceptEdits \
  > "$LOG" 2>&1

echo "machine-checkup finished; report in ai/checkups/, log in $LOG"
