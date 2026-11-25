---
name: day
description: Gather what Alejo did on a given day from agent sessions, the focus logs of Umi and Umi Next, commits, the plans app, Chrome history, calendar and calls. Use when he asks what he worked on, where his time went, or wants a summary, log or update covering one or more days.
---

# Day

1. Run `activity.py [YYYY-MM-DD | -N]` from this skill's folder (default today,
   `-1` yesterday) once per day asked about. Add `--json` for the same data as
   JSON. It prints:
   - Focus for the day across Umi and Umi Next: total minutes of keyboard
     focus, first and last focus, and breaks of 30 minutes or more. Focus is
     the best measure of where his attention went. Each app's log is read with
     `umi-next focus-log --by session`; on days with focus in both apps, rows
     name their app.
   - Per project (the repository under `~/best`), largest focus first: agent
     sessions with their title, first and last prompt, focus minutes and the
     agent's last summary ("ended with"); other focus, such as files, pages and
     plain terminals; commits. Sessions in temporary folders and scripted
     `claude -p` runs appear only as counts.
   - That day's page from the plans app: his priorities, then notes and his
     evening reflection.
   - Dayflow's screen record (from 25 Nov 2026): minutes at the Mac and its activity cards, which describe the
     screen in any app every 15 minutes. Use it for time the other sources miss, such as Slack, docs or video.
   - Chrome history for every profile, by site, with page titles and rough time.
   - Last, "Umi unused for N days: retire it?" once Umi has logged no focus for
     over 7 days. Pass that line on to Alejo.

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

Focus covers only Umi and Umi Next. Time in other apps shows up through Dayflow's screen
record, Chrome history, the calendar and call summaries. Dayflow's cards are Claude's reading of
screenshots: trust them for what app and subject were on screen, less for exact times or results.

The output includes private browsing and personal notes. Show it to Alejo, but
write it into a file only when he asks, and only into a private repository.
