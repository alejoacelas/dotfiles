---
name: machine-checkup
description: Scan the whole machine for loose ends, conflicting instructions, and things worth promoting to global — then fix the reversible ones and file the rest as findings. Use when the user wants a periodic health check / audit of their setup, or says "run a machine checkup / scan my machine / what's left hanging / what's drifted / anything to clean up" — and on a recurring schedule.
---

# machine-checkup — a recurring health check for the whole setup

Sweep the machine for four kinds of problem, fix what's safely reversible, and leave
the judgment calls as clean findings. The deterministic facts come from a script; you
do the reasoning, the fixing, and the report.

Runs read-only until the fix step. Default posture: **fix the reversible, flag the
rest** (see *Guard the irreversible* in the global CLAUDE.md — never do an irreversible
thing here without asking).

## What it looks for
1. **Loose ends** — uncommitted/unpushed work, no-upstream or no-remote repos, dangling
   symlinks, Homebrew drift.
2. **Instruction conflicts** — contradictions, duplication, or drift across the
   `CLAUDE.md` / `AGENTS.md` files and skills.
3. **Promote to global** — a local pattern, prompt, config, or one-off skill worth
   lifting into `machine/dotfiles` or the global `CLAUDE.md` so it applies everywhere.
4. **Security & what's running** — secret-pattern hits in tracked files, over-broad
   permissions, connectors needing re-auth, and an inventory of cron / LaunchAgents.

## 1. Gather the facts
```sh
python3 ~/best/machine/dotfiles/claude/skills/machine-checkup/scripts/scan.py
```
This prints a markdown report of the deterministic findings (repos, symlinks, secret
hits, instruction-file inventory, brew drift, scheduled jobs). It changes nothing.

## 2. Do the reasoning the script can't
- **Instruction conflicts:** read the `CLAUDE.md`/`AGENTS.md` files the scan listed
  (skip the 1-line pointers) and look for rules that fight each other, say the same
  thing twice, or have drifted apart (e.g. a domain file contradicting the root, or an
  `AGENTS.md` that no longer matches its `CLAUDE.md`).
- **Promote to global:** skim recent work for something reusable stuck in one place —
  a prompt you keep re-typing, a per-project setting that should be a default, a script
  that belongs in a skill. Flag it with where it should move.
- **Security judgment:** for each secret-pattern hit, decide real credential vs. false
  positive. Check `settings.json` permissions for anything broader than needed.

## 3. Fix the reversible; leave the rest
Do, without asking (all reversible, all traceable through git):
- Commit and push found work once you've checked nothing private rides along
  (*Default to public*). Use clear messages.
- Repair dangling symlinks by re-running `~/best/machine/dotfiles/bin/install.sh`.
- Add genuinely-installed Homebrew leaves to the `Brewfile`.

Do **not** auto-do (leave as findings, or ask first):
- Anything irreversible or outward-facing beyond a normal push (deleting untracked
  files, revoking access, publishing a private repo).
- Overwriting a file carrying a `GUARDED-JUDGMENT` marker — recover the reasoning first.
- Resolving an instruction conflict by rewriting a considered file — propose the fix.

## 4. Write the report and feed the backlog
- Write a dated report to `~/best/machine/checkups/<YYYY-MM-DD>.md` with three sections:
  **Fixed** (what you changed + why), **Needs your call** (findings with a proposed
  action and the fastest way to act), and **Clean** (what you checked that was fine —
  so a clean run still shows its work).
- Append any new, actionable *Needs your call* items to the **Open** section of
  `~/best/machine/improvements.md`, so the backlog stays the single to-do list.
- Reply with the short version: what you fixed, and the top few things that need a
  decision.

## Notes
- Safe to run anytime; the only writes are the fixes in step 3 and the report in step 4.
- To scan a different tree, pass a base path to `scan.py` (defaults to `~/best`).
- For running this on a schedule, see `machine/recurring-checkups.md`.
