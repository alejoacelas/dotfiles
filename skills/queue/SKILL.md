---
name: queue
description: Put something from the current session on Alejo's next morning docket, as a queued item in ~/best/systems/desk/requested/ with links to the work and a link that reopens this session in BB or Umi. Use when Alejo says "queue this", "add this to my docket", "put it on tomorrow's docket" or "remind me on the docket".
---

# Queue for the docket

The docket is the 08:00 London Slack DM from Clerk, the agent server's pipeline
(`~/best/systems/clerk`; see "Queued items" in its `docs/desk-pipeline.md`).
It lists every `requested/` item whose `queued:` date has arrived until the item has
`closed:`.

## Recurring work is a watch, not a queued item or a loop

When Alejo asks to keep doing something ("keep adding …", "in the background", "every day / every N
hours check …"), don't start a session loop, `/loop` or CronCreate: they die unseen when the session
ends or the Mac sleeps. Make it a watch on the agent server instead: a folder
`/home/agent/.local/share/gmail-review/watches/<short random hex>/` with `task.md` (frontmatter
`every:`, `ends:`, `started:`; then what to check, what it may do, when it is finished) and `log.md`,
written as user `agent` (from the Mac, through `ssh agent-server "sudo -u agent -H tee <path>"`). The
format is in `~/work/clerk/mail/agent-brief.md` under "Watches" on the server. The errands timer runs it,
and the docket lists it and raises it when it fails or stops. Tell Alejo in one line it is a watch, how
often it runs and when it ends.

## Write the item

Read `~/best/systems/desk/AGENTS.md` for the shared frontmatter and naming rules. Then write
`~/best/systems/desk/requested/YYYY-MM/<today>-<slug>.md`:

```markdown
---
people: [<slugs from ~/best/systems/desk/people/, [] if none>]
projects: [<the project folder, if any: coaching, 2026-11-04-access-form, aim>]
why: Alejo asked on <date> to queue <what>, in one line
next: <the decision to take, verb-first> (do|skip|defer)
queued: <YYYY-MM-DD>
bb: <BB link, for a session in BB>
umi: <umi link, for any other session>
umi_page: <page link, with umi>
---

Queued by Alejo from a <Claude Code|Codex> session on <machine> on <date>.

- <links: artifacts, docs, PRs, repositories, files>
- Session: [work on this in BB](<BB link>), or [work on this in Umi](<page link>)

<two to five lines: what was done, what's left, what the decision depends on>
```

- `queued:` is today's date unless Alejo names a later one; the next docket shows any
  item whose date has arrived.
- `next:` is a recommendation he can take with one key, like a docket line.
- Session link in a BB thread (`$BB_THREAD_ID` is set): `bb later link` prints it. Write
  it as `bb:` and leave out `umi:` and `umi_page:`. It opens the thread in the BB app on
  the Mac that runs BB.
- Session link anywhere else: make it with `umi-link` on the agent server. Its JSON output
  has the `umi` and `page` links.

  ```bash
  q() { printf '%q' "$1"; }  # ssh runs the arguments through a shell on the server
  ssh agent-server "sudo -u agent -H /home/agent/.local/bin/umi-link new --json \
    --title $(q "<title>") --folder $(q "<working directory relative to ~/best>") \
    --remote $(q "<origin URL>") --branch $(q "<branch>") --agent <claude|codex> \
    --resume <session id> --where mac --from $(hostname -s)"
  ```

  - Session id: for Claude Code, the newest `.jsonl` in
    `~/.claude/projects/<working directory with / and . replaced by ->/`; for Codex, the
    newest file under `~/.codex/sessions/`.
  - Leave out `--remote` and `--branch` when the folder isn't a git checkout.
  - On the agent server as `agent`, run `umi-link new` directly, with `--where server`.
- Link to files by their GitHub URL when the repository has a remote; a local path only
  opens on that machine.

## Commit

```bash
cd ~/best/systems/desk && git pull --rebase -q && git add requested && git commit -qm "Queue <slug> for the docket" && git push -q
```

Tell Alejo in one line what you queued and for which docket.
