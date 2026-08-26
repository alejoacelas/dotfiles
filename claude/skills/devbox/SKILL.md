---
name: devbox
description: Delegate long or heavy work to my Hetzner box via the `devbox` CLI (~/best/work/tools/devbox). Use when a job would run for many minutes, needs to survive the laptop sleeping, needs Linux, or should run in parallel with local work — builds, scrapes, batch LLM calls, test suites, agent runs.
---

# devbox — my cloud box

`devbox` (on PATH) wraps a persistent Ubuntu VM. Day-to-day commands need no secrets; `up/down/status/types` prompt 1Password once.

## Delegate a job

1. Get code there: `devbox push <dir>` (rsync, honours .gitignore) or `devbox clone owner/repo`.
2. Start it detached: `devbox run <name> "<command>"` — runs in tmux under a login shell (uv, node, claude, codex, gh on PATH); output to `~/jobs/<name>.log`, ending in `EXIT:<code>`.
3. Poll with `devbox log <name>` (or `-f`); `devbox jobs` lists running sessions. Use the Monitor tool with `devbox log`, not a sleep loop.
4. Bring results back: `devbox pull <remote-path> [local-dir]`.
5. `devbox kill <name>` if it went wrong; `devbox attach <name>` for the live tmux pane.

## Run an agent there

`devbox run review "cd repo && claude -p 'review the last commit' --output-format text"` — Claude and Codex on the box use the same dotfiles instructions as here, once the user has logged them in (`devbox login` prints how). If a command fails with an auth error, stop and ask the user to run `devbox login`; never copy tokens or `.env` files to the box.

## Rules

- One job per `devbox run`; name it after the task. Check `devbox jobs` first so names don't collide.
- The box is a pet, not cattle: don't `devbox down` without the user asking. Its disk is the only copy of unpulled results.
- `devbox ssh <cmd>` for quick one-offs (`devbox ssh df -h`).
