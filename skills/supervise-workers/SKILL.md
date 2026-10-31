---
name: supervise-workers
description: Launch and supervise separate Claude Code or Codex worker sessions in Warp terminals. Use when the task calls for separate worker sessions, workers in separate worktrees, or agents from a different family (such as Claude from Codex). Ordinary in-session subagents, generic delegation or parallelism, and worktree management alone do not trigger this skill.
---

# Supervise workers

Use this workflow once separate workers are called for. For ordinary in-session
subagents, use the host's native delegation tools. A request to "fan out" or
"delegate" alone does not require separate terminal sessions.

You own the outcome. Workers do the work in terminal sessions; you decide when it
is done by checking evidence yourself. A worker saying "done" is not evidence, and
a quiet worker is not necessarily working.

Workers run in Warp through
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

```sh
id=$(warp-agent new --agent claude --group <project> --dir "$PWD" --name <slug> --model <id> \
       "Do the task in .supervise/<slug>/task.md")
# Codex: --agent codex --agent-args "--profile cli -c model_reasoning_effort=<level>"
```

`warp-agent` skips approvals by default, accepts the folder-trust prompt for the
directory you pass, and starts the worker with the pointer as its first prompt.
`--group` names the Warp tab group the worker's tab joins; use the project name so
a project's workers sit together. Workers that edit code in parallel each get their
own worktree (`git worktree add ../<repo>-<slug> -b <slug>`, then pass it as `--dir`).

## Wait

`warp-agent wait` returns when the worker's turn ends (`DONE`), it needs an answer
(`WAITING`), its session ends (`EXITED`), or the timeout passes (`TIMEOUT`), and
prints the worker's last message. It counts only turns that started after your
latest `warp-agent send` to that worker.

```sh
warp-agent wait "$id" --timeout 1200
```

- Claude Code: run it in the background; you are re-invoked when it exits. With
  several workers, run one background wait per worker.
- Codex: start a detached watcher per worker, then end your turn:

  ```sh
  ~/.agents/skills/supervise-workers/watch-worker.sh "$id" <slug>
  ```

  When the wait ends, the watcher saves its output to `.supervise/<slug>/wait.out`
  and types a "Watcher:" message into your terminal, which starts your next turn.
  Messages that arrive while you are busy are queued. Start a new watcher whenever
  you send a worker a follow-up, and end your turn only while every unverified
  worker has a live watcher. The watcher can type into your session only if
  `warp-agent` launched you (`WARP_AGENT_ID` is set); otherwise run
  `warp-agent wait` in the foreground.

## Check

1. `DONE`: read the report and verify the evidence yourself. Accept, or move the
   report to `report-<n>.md`, send a follow-up with `warp-agent send "$id" "..."`
   in the same session, and wait again.
2. `DONE` without a report, or `WAITING`: read the last message, then answer the
   question or ask for the report. Read the screen with
   `warp-agent read "$id" --log`. `WAITING` names what is pending (a permission or
   a trust prompt); answer a menu with keys, such as `warp-agent send "$id" --key 1`
   or `--key enter`.
3. `TIMEOUT`: read the screen. An error such as a failed login is a failure, not
   progress; relaunch the task. Otherwise wait again.
4. `EXITED`: relaunch the task.

When you accept a task, end its session with `warp-agent stop "$id"`, which also
closes its tab. Finish only when every task is accepted, then report to the user.

## Resume

After a restart, rebuild state from `.supervise/*/` and `warp-agent ls` (session
IDs start with the slug).
