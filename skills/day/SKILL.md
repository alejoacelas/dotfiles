---
name: day
description: Gather what Alejo did on a given day from agent sessions, Umi's focus log, commits, the plans app, Chrome history, calendar and calls. Use when he asks what he worked on, where his time went, or wants a summary, log or update covering one or more days.
---

# Day

1. Run `activity.py [YYYY-MM-DD | -N]` from this skill's folder (default today,
   `-1` yesterday) once per day asked about. Add `--json` for the same data as
   JSON. It prints:
   - Umi's focus for the day: total minutes of keyboard focus in Umi, first and
     last focus, and breaks of 30 minutes or more. Focus is the best measure of
     where his attention went. Umi computes it (`umi focus-log --by session`).
   - Per project (the repository under `~/best`), largest focus first: agent
     sessions with their title, first and last prompt, focus minutes and the
     agent's last summary ("ended with"); other focus, such as files, pages and
     plain terminals; commits. Sessions in temporary folders and scripted
     `claude -p` runs appear only as counts.
   - That day's page from the plans app: his priorities, then notes and his
     evening reflection.
   - Chrome history for every profile, by site, with page titles and rough time.

   The day timeline at https://agent-server.tail622085.ts.net/day shows the last 14 days by topic and task;
   `timeline/publish` rebuilds it (launchd runs it hourly).

   For a page of the last days, run `view.py [--days N]`: it writes
   `~/.local/share/day/index.html` and opens it (← → between days, T today, E
   expands prompts).
2. Add what the script can't reach:
   - Calendar events from every calendar the Google Calendar connector lists.
   - Call summaries filed that day: `find ~/best/desk -name 'YYYY-MM-DD-*-sum.md'`.
3. Answer the question Alejo asked, in the form he asked for. Without a stated
   form, lead with the main threads of work, then meetings, then everything else.
   When the plans page lists priorities, say how much focus each one got, by
   matching it to projects and sessions, and name the work that took time
   without being a priority.
4. When he asks for a draft of his evening reflection, answer the plans page's
   first question ("What did you work on today?") in his voice from the data:
   what he worked on, in order of time, and how it compared with his
   priorities. Show the draft to him; the plans page is his to edit.

Focus covers only Umi. Time in Chrome, Slack or calls shows up only through
Chrome history, the calendar and call summaries.

The output includes private browsing and personal notes. Show it to Alejo, but
write it into a file only when he asks, and only into a private repository.
