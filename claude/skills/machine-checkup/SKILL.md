---
name: machine-checkup
description: Scan the whole machine for loose ends, conflicting instructions, and things worth promoting to global, and file everything as findings you act on. Use when the user wants a periodic health check / audit of their setup, or says "run a machine checkup / scan my machine / what's left hanging / what's drifted / anything to clean up" — and on a recurring schedule.
---

# machine-checkup — a recurring health check for the whole setup

Sweep the machine for four kinds of problem and write them up as clean findings. The
deterministic facts come from a script; you do the reasoning and the report.

**Posture: report only.** This skill changes nothing except the report it writes and the
backlog it appends to. Every finding — even the trivially fixable — is proposed, not
applied. (If the posture ever changes to auto-fix, it still stops at anything
irreversible; see *Guard the irreversible* in the global CLAUDE.md.)

## What it looks for
1. **Loose ends** — uncommitted/unpushed work, no-upstream or no-remote repos, dangling
   symlinks, Homebrew drift.
2. **Instruction conflicts** — contradictions, duplication, or drift across the
   `CLAUDE.md` / `AGENTS.md` files and skills.
3. **Promote to global** — a local pattern, prompt, config, or one-off skill worth
   lifting into `ai/dotfiles` or the global `CLAUDE.md` so it applies everywhere.
4. **Security & what's running** — secret-pattern hits in tracked files, over-broad
   permissions, connectors needing re-auth, and an inventory of cron / LaunchAgents.

## 1. Gather the facts
```sh
python3 ~/best/ai/dotfiles/claude/skills/machine-checkup/scripts/scan.py
~/best/ai/dotfiles/bin/check-agent-config   # instruction/skill drift + dangling links
```
The first prints a markdown report of the deterministic findings (repos, symlinks, secret
hits, instruction-file inventory, brew drift, scheduled jobs). The second reports where
paired `CLAUDE.md`/`AGENTS.md` or Claude/Codex skills have diverged (a reminder to
reconcile, never enforced) and fails loudly on any dangling config symlink. Both change
nothing.

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

## 3. Report only — change nothing
Do not fix, commit, push, or move anything. For each finding, write down *what* it is
and the *proposed action* (with the fastest way to do it), so the user can act in
seconds — but leave the acting to them. This keeps every run safe to trigger unattended.

## 4. Write the report and feed the backlog
- Write a dated report to `~/best/ai/checkups/<YYYY-MM-DD>.md` with two sections:
  **Needs your call** (each finding + proposed action) and **Clean** (what you checked
  that was fine — so a clean run still shows its work).
- Append any new, actionable items to the **Open** section of
  `~/best/ai/improvements.md`, so the backlog stays the single to-do list.
- Reply with the short version: the top few things that need a decision.

## Notes
- The only writes are the report (step 4) and the backlog append — nothing else.
- To scan a different tree, pass a base path to `scan.py` (defaults to `~/best`).
- For running this on a schedule, see `machine/recurring-checkups.md`.
