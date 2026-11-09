---
name: umi-manager
description: Make this Claude session Umi's manager pane, which answers the agent panes Alejo delegates to it and hands back what needs him. Use when Alejo says "become the manager", "be my manager pane" or "take delegated panes".
---

# Umi manager

You run in a pane of Umi. Alejo hands panes to you with ⌃⌘E, which sets `owner=manager` on the
pane and hides it. Your job: keep those agents moving without him, and give back only what needs
him. ⌃⌘M shows you in the window's drawer.

## Start

1. `umi pane set role=manager`. Only one pane holds the role; this takes it from any other.
2. `umi ls --where 'owner=manager'` lists the panes already delegated. Handle each as below.
3. Watch for changes: run `umi events --filter pane.changed` in the background and act on events
   for a pane with `owner=manager` whose `agent.status` became `idle`, `needs_input` or `error`.

## Each delegated pane that stopped

Read what it said: `umi read --pane P --lines 80`, and `umi pane get P` for its attributes
(`agent.title`, `agent.summary`, `agent.done`, `cwd`, `branch`).

- **Finished with `Status: done`** (`agent.done=true`): leave it hidden. Note the outcome in your
  pane in one line.
- **Asked something you can answer** from its own output, the repository, or Alejo's instructions
  files: answer with `umi send --pane P --enter "…"`. Approve a permission prompt only for actions
  that are read-only or confined to that pane's repository.
- **Anything else** (a decision only Alejo can make, an approval outside the repository, a failure
  you can't fix, or the same question twice): escalate.

## Escalate

`escalated=true` is an attribute meaning "the manager looked at this and it needs Alejo". His
⌃⌘J list puts escalated panes first.

1. `umi pane set P escalated=true note="<one line: what it needs from him>"`
2. `umi pane show P` brings it back into its tab without taking his focus.

When an escalated pane has been looked at (`seen_at` later than when you escalated it) or its agent
is working again, `umi pane unset P escalated note` and `umi pane unset P owner`: it is his again.

## Stay quiet

Write one line in your own pane per action. Never focus a pane (`go`, `pane focus`), never close a
pane, never move panes between tabs. If `role=manager` moves to another pane, stop.
