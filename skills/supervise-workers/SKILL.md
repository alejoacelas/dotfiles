---
name: supervise-workers
description: Launch and supervise separate Claude Code or Codex worker sessions in Orca or Warp terminals. Use when the task calls for separate worker sessions, workers in separate worktrees, or agents from a different family (such as Claude from Codex). Ordinary in-session subagents, generic delegation or parallelism, and worktree management alone do not trigger this skill.
---

# Supervise workers

Use this workflow once separate workers are called for. For ordinary in-session
subagents, use the host's native delegation tools. A request to "fan out" or
"delegate" alone does not require separate terminal sessions.

You own the outcome. Workers do the work in terminal sessions; you decide when it
is done by checking evidence yourself. A worker saying "done" is not evidence, and
a quiet worker is not necessarily working.

Pick the track from where you are running:

- **Orca**: `ORCA_TERMINAL_HANDLE` is set. Use the `orca` CLI.
- **Warp**: `TERM_PROGRAM=WarpTerminal`. Use
  [`warp-agent`](https://github.com/alejoacelas/2026-10-warp-agent), which opens each
  worker as a tab in a Warp tab group and tracks it through agent hooks.

## Delegate

For each task, pick a short slug and write `.supervise/<slug>/task.md` in the
worktree (add `.supervise/` to `.git/info/exclude`). The task file states:

1. The goal and context the worker cannot infer.
2. Done means: evidence you can check — a passing command, a commit, a file. Do not
   accept less than this later.
3. "When you finish or get blocked, write `.supervise/<slug>/report.md`: what you
   did, the evidence, and anything left or your question. Then stop."

Launch every worker with full permissions so it never stalls on an approval
prompt, and give it only a pointer to the file: Claude workers distrust long
pasted instructions, so never paste the task itself.

### Orca

```sh
h=$(orca terminal create --worktree current --title "<slug>" --json \
      --command "claude --dangerously-skip-permissions --model <id>" \
      | jq -r .result.terminal.handle)
# Codex: --command "codex --dangerously-bypass-approvals-and-sandbox --profile cli -m <id> -c model_reasoning_effort=<level>"
orca terminal wait --terminal "$h" --for tui-idle --timeout-ms 90000
since=$(date +%s)000
orca terminal send --terminal "$h" --text "Do the task in .supervise/<slug>/task.md" --enter
```

Workers that edit code in parallel each get their own worktree
(`orca worktree create --name <slug> --json`, then pass it as `--worktree`).

### Warp

```sh
id=$(warp-agent new --group <project> --dir "$PWD" --name <slug> --model <id> \
       "Do the task in .supervise/<slug>/task.md")
# Codex: add --agent codex --agent-args "--profile cli -c model_reasoning_effort=<level>"
```

`warp-agent` skips approvals by default, accepts the folder-trust prompt for the
directory you pass, and starts the worker with the pointer as its first prompt.
`--group` names the Warp tab group the worker's tab joins; use the project name so
a project's workers sit together. Workers that edit code in parallel each get their
own worktree (`git worktree add ../<repo>-<slug> -b <slug>`, then pass it as `--dir`).

## Wait

It returns when the worker's turn ends (`DONE`), it needs an answer (`WAITING`),
its session ends (`GONE` in Orca, `EXITED` in Warp), or the timeout passes
(`TIMEOUT`), and prints the worker's last message.

```sh
~/.agents/skills/supervise-workers/wait-worker.sh "$h" "$since" 1200   # Orca
warp-agent wait "$id" --timeout 1200                                    # Warp
```

`warp-agent wait` counts only turns that started after your latest
`warp-agent send` to that worker, so it needs no `since`.

- Claude Code: run it in the background; you are re-invoked when it exits. With
  several workers, run one background wait per worker.
- Codex: start a detached watcher per worker, then end your turn:

  ```sh
  ~/.agents/skills/supervise-workers/watch-worker.sh "$h" "$since" <slug>   # Orca
  ~/.agents/skills/supervise-workers/watch-worker.sh "$id" - <slug>         # Warp
  ```

  When the wait ends, the watcher saves its output to `.supervise/<slug>/wait.out`
  and types a "Watcher:" message into your terminal, which starts your next turn.
  Messages that arrive while you are busy are queued. Start a new watcher whenever
  you send a worker a follow-up, and end your turn only while every unverified
  worker has a live watcher. In Warp, the watcher can type into your session only
  if `warp-agent` launched you (`WARP_AGENT_ID` is set); otherwise run
  `warp-agent wait` in the foreground.

  In Orca, track the handle of any extra terminal you open for a watch command,
  separately from the worker and supervisor handles. Once that terminal's watch
  command has finished and its output is saved, close it with
  `orca terminal close --terminal "$watch_terminal"`. Clean up these terminals
  after failures and cancellations too; before finishing, verify that none remain
  open. Close only terminals you opened for watching, not the supervisor or a
  worker whose result still needs checking.

## Check

1. `DONE`: read the report and verify the evidence yourself. Accept, or move the
   report to `report-<n>.md`, send a follow-up in the same session, and wait again
   (in Orca, with a new `since`). Follow-ups: `orca terminal send --terminal "$h"
   --text "..." --enter` or `warp-agent send "$id" "..."`.
2. `DONE` without a report, or `WAITING`: read the last message, then answer the
   question or ask for the report. Read the screen with
   `orca terminal read --terminal "$h"` or `warp-agent read "$id" --log`. In Warp,
   `WAITING` names what is pending (a permission or a trust prompt); answer a menu
   with keys, such as `warp-agent send "$id" --key 1` or `--key enter`.
3. `TIMEOUT`: read the screen. An error such as a failed login is a failure, not
   progress; relaunch the task. Otherwise wait again.
4. `GONE` or `EXITED`: relaunch the task. `ERR` (Orca): fall back to checking for
   the report file and reading the screen at each timeout.

When you accept a task, end its session: `orca terminal close --terminal "$h"` or
`warp-agent stop "$id"` (which also closes its tab). Finish only when every task is
accepted, then report to the user.

## Resume

After a restart, rebuild state from `.supervise/*/` and the session list:
`orca terminal list --json` (terminal titles are the slugs) or `warp-agent ls`
(session IDs start with the slug). In Orca, use `since=0` for a worker whose send
time you no longer know, then check its report.

On a remote Orca server, run the supervisor on that server.
