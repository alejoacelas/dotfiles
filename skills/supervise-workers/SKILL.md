---
name: supervise-workers
description: Delegate tasks to long-running Claude Code or Codex workers in Orca terminals and supervise them until each result is verified done. Use when you own a process and hand parts of it to other agents — "delegate this to workers", "spawn a claude/codex worker", "fan out", "hand this off and make sure it gets done", "supervise the workers".
---

# Supervise workers

You own the outcome. Workers do the work in Orca terminals; you decide when it is
done by checking evidence yourself. A worker saying "done" is not evidence, and a
quiet worker is not necessarily working.

## Delegate

For each task, pick a short slug and write `.supervise/<slug>/task.md` in the
worktree (add `.supervise/` to `.git/info/exclude`). The task file states:

1. The goal and context the worker cannot infer.
2. Done means: evidence you can check — a passing command, a commit, a file. Do not
   accept less than this later.
3. "When you finish or get blocked, write `.supervise/<slug>/report.md`: what you
   did, the evidence, and anything left or your question. Then stop."

Launch every worker with full permissions (the flags below, which match Orca's own
defaults) so it never stalls on an approval prompt. Wait for its prompt, then send
only a pointer to the file: Claude workers distrust long pasted instructions, so
never paste the task itself.

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

## Wait

```sh
~/.agents/skills/supervise-workers/wait-worker.sh "$h" "$since" 1200
```

It returns when the worker's turn ends (`DONE`), it needs an answer (`WAITING`),
its terminal closes (`GONE`), or the timeout passes (`TIMEOUT`), and prints the
worker's last message.

- Claude Code: run it in the background; you are re-invoked when it exits. With
  several workers, run one background wait per worker.
- Codex: start a detached watcher per worker, then end your turn:

  ```sh
  ~/.agents/skills/supervise-workers/watch-worker.sh "$h" "$since" <slug>
  ```

  When the wait ends, the watcher saves its output to `.supervise/<slug>/wait.out`
  and types a "Watcher:" message into your terminal, which starts your next turn.
  Messages that arrive while you are busy are queued. Start a new watcher whenever
  you send a worker a follow-up, and end your turn only while every unverified
  worker has a live watcher.

## Check

1. `DONE`: read the report and verify the evidence yourself. Accept, or move the
   report to `report-<n>.md`, send a follow-up in the same terminal, and wait again
   with a new `since`.
2. `DONE` without a report, or `WAITING`: read the last message (or
   `orca terminal read --terminal "$h"`), then answer the question or ask for the
   report.
3. `TIMEOUT`: read the screen. An error such as a failed login is a failure, not
   progress; relaunch the task. Otherwise wait again.
4. `GONE`: relaunch the task. `ERR`: fall back to checking for the report file and
   reading the screen at each timeout.

When you accept a task, close its terminal with `orca terminal close --terminal "$h"`.
Finish only when every task is accepted, then report to the user.

## Resume

After a restart, rebuild state from `.supervise/*/` and
`orca terminal list --json` (terminal titles are the slugs). Use `since=0`
for a worker whose send time you no longer know, then check its report.

On a remote Orca server, run the supervisor on that server.
