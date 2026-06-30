---
name: granola-transcript
description: Fetch a Granola meeting transcript, clean up transcription errors (misspellings, garbled proper nouns / tool names), and save it under the right person's dated call folder. Use when the user wants to pull, clean, or archive Granola call transcripts — e.g. "save my Granola calls with X", "clean the transcript from my last meeting", "archive my Granola notes".
---

# Granola transcript → clean → save

Pull raw transcripts from Granola, fix the transcription errors, and file each under
the call's dated folder: `<person>/calls/<YYYY-MM-DD>/transcript.md` (the person
folder and the date folder carry the identity, so the file is just `transcript.md`).

## 1. Connect to Granola

**Use the Granola MCP connector.** This is the chosen connection method (see
`reference/connection-methods.md` for why, and for the offline fallback). The
connector exposes these tools (load schemas with ToolSearch
`select:mcp__claude_ai_Granola__...` if they aren't already available):

- `mcp__claude_ai_Granola__get_account_info` — confirm which account is connected;
  this tells you who **"me"** is (the note creator / the user). Everyone else is a
  potential "person they called".
- `mcp__claude_ai_Granola__list_meetings` — enumerate meetings. Supports
  `time_range` (`this_week` | `last_week` | `last_30_days` | `custom`). For a full
  history use `custom` with a wide `custom_start`/`custom_end` (ISO dates). The
  result can be large and may be spilled to a file — search it for the person's
  name rather than reading it whole.
- `mcp__claude_ai_Granola__get_meeting_transcript` — `meeting_id` → the **verbatim
  transcript** (this is the raw text you clean). Speakers are labelled `Me:` (the
  account holder) and `Them:` (everyone else).
- `mcp__claude_ai_Granola__list_meeting_folders` / `get_meetings` /
  `query_granola_meetings` — folders, summaries/attendees, and natural-language
  search, when useful.

If the connector is unavailable (e.g. headless/cron, or claude.ai not connected),
fall back to the local-cache method in `reference/connection-methods.md`.

## 2. Find the right meetings

1. `get_account_info` to learn who "me" is (note creator email/name).
2. `list_meetings` over the needed range. Match meetings where the **person** (not
   "me") appears in the title or `known_participants`. Match on first name /
   nickname too (e.g. a `sam/` folder ↔ "Samantha"), but verify against the
   participant list so you don't grab a different person who shares a name.
3. For each match, `get_meeting_transcript` to get the raw text.

## 3. Clean the transcript

Apply `reference/cleaning_prompt.md` to the raw transcript. It fixes transcription
errors (especially garbled proper nouns and tool names), normalizes speaker labels
to real names, and tidies punctuation — **without** summarizing or dropping content.

For long transcripts or several at once, dispatch **one sub-agent per transcript**
so cleaning doesn't consume the main context. Give each sub-agent: the raw
transcript, the contents of `reference/cleaning_prompt.md`, the speaker mapping
(who is `Me` / `Them`), and the exact output path. Have it write the cleaned file
directly and report back only the path.

## 4. Save it (default location logic)

By default, resolve the save location relative to the **current working directory**:

1. If a folder named after the person exists (nickname-aware, e.g. `sam/` for
   Samantha) → save in `<that-folder>/about/calls/<YYYY-MM-DD-slug>/` (or its legacy
   `sources/calls/` / `calls/` if that folder still uses the old layout).
2. Else if an `about/calls/` (or legacy `sources/calls/` / `calls/`) folder exists at
   the cwd → save there.
3. Else → there's no obvious home; create `about/calls/<YYYY-MM-DD-slug>/` at the cwd
   **and tell the user where you saved it** (or ask first if it's ambiguous).

The call folder follows the `YYYY-MM-DD-<slug>` grammar — pass `--slug` with a short
topic (`--slug donor-circle`). Pick the slug from what the call was about.

Use the helper to resolve the path and write deterministically:

```bash
python3 scripts/save_transcript.py \
  --person "Samantha" \
  --date 2026-06-19 --slug donor-circle \
  --content-file /tmp/cleaned.md          # or pipe cleaned text via stdin
# prints the absolute path it wrote (…/sam/about/calls/2026-06-19-donor-circle/transcript.md)
```

The script applies the resolution rules above and writes `transcript.md` inside the
dated call folder. Pass `--base-dir` to override the search root, `--dry-run` to just
print the resolved path, `--slug` for the folder topic, and `--name` for a second file
in the same folder.

## Conventions

- **Path:** `<person>/about/calls/<YYYY-MM-DD-slug>/transcript.md`. The person folder
  and the dated folder carry the call's identity, so the file is just `transcript.md`.
  (`calls/` is one source under `about/`; see the people repo's `present/CLAUDE.md`.)
- **One file per call.** If the same call was recorded twice, keep the longer one. For
  two *different* calls with the person on one day, give each its own `--slug`.
- **Don't summarize.** These are cleaned verbatim transcripts, not notes.
