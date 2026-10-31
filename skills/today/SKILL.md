---
name: today
description: Start-of-day review of ~/best, and where to put new work. Use when Alejo runs /today, asks what needs attention, wants to file inbox items or stale projects, or starts a new project and needs to know where it goes.
---

# Today

## Review

1. Run `scan.sh` from this skill's folder. It lists unsaved work, inbox items and
   projects untouched for two weeks, projects still running or billing, and
   trials still running.
2. List today's calendar events on Alejo's personal Google account. For each call
   with someone who has a file in `~/best/desk/people/`, read it and their latest
   summary in `~/best/desk/comms/` (the items whose `people:` lists them); for client
   calls, also read `~/best/clients/<company>/AGENTS.md`.
3. Present one short list, most urgent first:
   - **Calls today:** who, when, and what was promised or left open last time.
   - **Unsaved work:** offer to commit and push.
   - **To file:** for each stale inbox item or project, suggest its home:
     `projects/`, `clients/<company>/`, `desk/`, `stash/` or `archive/`.
   - **Still running or billing:** ask whether each should keep running.
   - **Trials still running.**
4. Change nothing until Alejo picks what to act on. Follow the destination's
   `AGENTS.md` when moving anything.

## New work

Pick the home:

- Work for a client: `clients/<company>/`.
- Loose or one-off work for someone outside: `desk/requested/`; follow its `AGENTS.md`.
- Testing a tool: a folder in `stash/trials/`; follow its `AGENTS.md`.
- Alejo's own project: `projects/`. Once he uses it regularly, propose moving
  it to `stash/` without its date prefix; move it only once he approves.
- Unsure: `inbox/`.

Create it with `proj <folder>/<name> [--claude|--codex]` (plain `<name>` means
`projects/`). It adds a `YYYY-MM-DD-` prefix in `projects/` and `YYYY-MM-`
elsewhere, runs `git init` and writes an `AGENTS.md` stub. For
`proj stash/trials/<tool>` it copies the trials template instead.
Fill in the stub:

- **Scope:** what the project is for and what done looks like.
- **Visibility:** public unless it holds credentials, employer information or
  other people's non-public information. Client projects are private.
- **Google account:** pass it explicitly on every cloud write.
- **Still running or billing:** deployments, servers, scheduled jobs and paid
  APIs, so archiving can shut them down.

On the first commit, create the remote with
`gh repo create alejoacelas/<name> --private|--public --source . --push`.
