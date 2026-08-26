---
name: my-vm
description: Delegate long or heavy work to my Hetzner box via the `my-vm` CLI (~/best/work/tools/my-vm). Use when a job would run for many minutes, needs to survive the laptop sleeping, needs Linux, or should run in parallel with local work — builds, scrapes, batch LLM calls, test suites, agent runs.
---

# my-vm — my cloud box

`my-vm` (on PATH) wraps a persistent Ubuntu VM. Day-to-day commands need no secrets; `up/down/status/types` prompt 1Password once.

## Delegate a job

1. Get code there: `my-vm push <dir>` (rsync, honours .gitignore) or `my-vm clone owner/repo`.
2. Start it detached: `my-vm run <name> "<command>"` — runs in tmux under a login shell (uv, node, claude, codex, gh on PATH); output to `~/jobs/<name>.log`, ending in `EXIT:<code>`.
3. Poll with `my-vm log <name>` (or `-f`); `my-vm jobs` lists running sessions. Use the Monitor tool with `my-vm log`, not a sleep loop.
4. Bring results back: `my-vm pull <remote-path> [local-dir]`.
5. `my-vm kill <name>` if it went wrong; `my-vm attach <name>` for the live tmux pane.

## Run an agent there

`my-vm run review "cd repo && claude -p 'review the last commit' --output-format text"` — Claude and Codex on the box use the same dotfiles instructions as here, once the user has logged them in (`my-vm login` prints how). If a command fails with an auth error, stop and ask the user to run `my-vm login`; never copy tokens or `.env` files to the box.

## Rules

- One job per `my-vm run`; name it after the task. Check `my-vm jobs` first so names don't collide.
- The box is a pet, not cattle: don't `my-vm down` without the user asking. Its disk is the only copy of unpulled results.
- `my-vm ssh <cmd>` for quick one-offs (`my-vm ssh df -h`).
