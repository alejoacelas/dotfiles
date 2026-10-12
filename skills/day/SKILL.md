---
name: day
description: Gather what Alejo did on a given day from agent sessions, commits, the plans app, Chrome history, calendar and calls. Use when he asks what he worked on, where his time went, or wants a summary, log or update covering one or more days.
---

# Day

1. Run `activity.py [YYYY-MM-DD | -N]` from this skill's folder (default today,
   `-1` yesterday) once per day asked about. It prints:
   - Claude Code and Codex sessions: start folder, title, first and last prompt.
     Scripted `claude -p` runs appear only as counts per folder.
   - Commits in every repository under `~/best`.
   - That day's file from the plans app: the plan, then notes.
   - Chrome history for every profile, by site, with page titles and rough time.
2. Add what the script can't reach:
   - Calendar events from every calendar the Google Calendar connector lists.
   - Call summaries filed that day: `find ~/best/calls -name 'YYYY-MM-DD-*-sum.md'`.
3. Answer the question Alejo asked, in the form he asked for. Without a stated
   form, lead with the main threads of work, then meetings, then everything else.

The output includes private browsing and personal notes. Show it to Alejo, but
write it into a file only when he asks, and only into a private repository.
