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
   with someone who has a folder in `~/best/calls/`, read their latest summary and
   `NOTES.md`; for client calls, also read `~/best/clients/<company>/AGENTS.md`.
3. Present one short list, most urgent first:
   - **Calls today:** who, when, and what was promised or left open last time.
   - **Unsaved work:** offer to commit and push.
   - **To file:** for each stale inbox item or project, suggest its home:
     `projects/`, `projects/in-use/`, `clients/<company>/`, `trials/`, or an
     archive.
   - **Still running or billing:** ask whether each should keep running.
   - **Trials still running.**
4. Change nothing until Alejo picks what to act on. Follow the destination's
   `AGENTS.md` when moving anything.

## New work

Pick the home:

- Work for a client: `clients/<company>/`.
- Testing a tool: `trials/`, as a folder in that repository; follow its `AGENTS.md`.
- Alejo's own project: `projects/`. It moves to `projects/in-use/` once he relies on it.
- Unsure: `inbox/`.

Create it with `proj <folder>/<name> [--claude|--codex]` (plain `<name>` means
`projects/`). It adds a `YYYY-MM-DD-` prefix in `projects/` and `YYYY-MM-`
elsewhere, runs `git init` and writes an
`AGENTS.md` stub; inside `trials/` it copies the template instead. Fill in the
stub:

- **Scope:** what the project is for and what done looks like.
- **Visibility:** public unless it holds credentials, employer information or
  other people's non-public information. Client projects are private.
- **Google account:** pass it explicitly on every cloud write.
- **Still running or billing:** deployments, servers, scheduled jobs and paid
  APIs, so archiving can shut them down.

On the first commit, create the remote with
`gh repo create alejoacelas/<name> --private|--public --source . --push`.
