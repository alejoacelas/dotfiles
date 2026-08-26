---
name: hut
description: Delegate long or heavy work to my Hetzner box via the `hut` CLI (~/best/work/tools/hut). Use when a job would run for many minutes, needs to survive the laptop sleeping, needs Linux, or should run in parallel with local work — builds, scrapes, batch LLM calls, test suites, agent runs.
---

# hut — my cloud box

`hut` (on PATH) wraps a persistent Ubuntu VM. Day-to-day commands need no secrets; `up/down/status/types` prompt 1Password once.

## Delegate a job

1. Get code there: `hut push <dir>` (rsync, honours .gitignore) or `hut clone owner/repo`.
2. Start it detached: `hut run <name> "<command>"` — runs in tmux under a login shell (uv, node, claude, codex, gh on PATH); output to `~/jobs/<name>.log`, ending in `EXIT:<code>`.
3. Poll with `hut log <name>` (or `-f`); `hut jobs` lists running sessions. Use the Monitor tool with `hut log`, not a sleep loop.
4. Bring results back: `hut pull <remote-path> [local-dir]`.
5. `hut kill <name>` if it went wrong; `hut attach <name>` for the live tmux pane.

## Run an agent there

`hut run review "cd repo && claude -p 'review the last commit' --output-format text"` — Claude and Codex on the box use the same dotfiles instructions as here, once the user has logged them in (`hut login` prints how). If a command fails with an auth error, stop and ask the user to run `hut login`; never copy tokens or `.env` files to the box.

## Rules

- One job per `hut run`; name it after the task. Check `hut jobs` first so names don't collide.
- The box is a pet, not cattle: don't `hut down` without the user asking. Its disk is the only copy of unpulled results.
- `hut ssh <cmd>` for quick one-offs (`hut ssh df -h`).
