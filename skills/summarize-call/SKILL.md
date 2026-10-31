---
name: summarize-call
description: Fetch a Granola call transcript from the API, clean it, and file a tidied transcript plus a structured summary in ~/best/desk, following that repository's AGENTS.md. Use when the user wants to pull, clean, summarize, or archive Granola calls — "summarise my call", "save my last Granola call", "archive these calls".
---

# Granola call → tidied transcript + summary

Adapted from [HartreeWorks/skill--summarise-granola](https://github.com/HartreeWorks/skill--summarise-granola),
rewired to file into `~/best/desk`. Reads transcripts over Granola's
[public API](https://docs.granola.ai) with a personal key (`scripts/granola.py`).

## Where to run

Run this workflow from a session whose working directory is inside `~/best/desk`.
When triggered anywhere else, hand the job to a headless Claude started there and
carry on with the current task:

```bash
cd ~/best/desk && nohup claude -p "<request>" --dangerously-skip-permissions > <log> 2>&1 &
```

Write the request so it stands on its own: ask for this skill, name the call and
the person, and pass on every link, id or detail the user gave (save a pasted
transcript to a file and give its path). Say the run is headless, so it must not
guess names or emails, must share the doc only as Step 4 describes, and must end
by reporting the doc link, the files written, the participant's email, whether it
shared the doc, and any open questions. Keep the log outside the repository, such
as in the scratchpad. When the run finishes, relay the doc link, the sharing
result and its questions; if the run couldn't confirm an email, ask Alejo for it
and share the doc yourself.

## Destination and paths

Always save calls in `~/best/desk`. Before fetching or writing, read `~/best/desk/AGENTS.md` and any `README.md`
or `AGENTS.md` in the destination person's folder. That repository defines the exact filing paths,
folder conventions, indexes and sync requirements. If it is missing, stop and
report that; do not create an archive in the current project.

Resolve this skill's directory from the `SKILL.md` you loaded and set
`CALL_SKILL` to that absolute directory. Run archive operations from `~/best/desk`;
run the bundled helpers by their absolute paths as shown below. References are
relative to this skill, not the working directory. Temporary transcripts and
garble inventories stay in `$CALL_SKILL/data/`.

## Setup (once)

`granola.py` uses `GRANOLA_API_KEY` for Granola's public API. Reuse an existing
valid key. Store new keys in 1Password, explicitly verifying the account and vault.
Retrieve the key on demand with `op` into `$CALL_SKILL/.env` after confirming the
file is Git-ignored, untracked, and owner-only (`chmod 600`). Keep values out of
terminal output and chat. Record the variable's purpose and the verified
1Password account, vault, item, and field in the repository's README.

The environment variable overrides the `.env` file. The helper uses Python's
standard library; no additional packages are needed.

## Commands

```bash
python3 "$CALL_SKILL/scripts/granola.py" list [n]      # n most recent meetings (default 20; paginates)
python3 "$CALL_SKILL/scripts/granola.py" check         # recent-call / selection JSON
python3 "$CALL_SKILL/scripts/granola.py" get <doc_id>  # print transcript markdown for one call
python3 "$CALL_SKILL/scripts/granola.py" recent [n]    # nth most recent transcript
```

`get <doc_id>` prints the raw transcript to stdout (also saved under
`$CALL_SKILL/data/transcripts/`). Speakers are `**Me**:` (the account holder, Alejandro)
and `**Other**:` (everyone else).

These commands are the default path for every call. But the public API index
is sometimes incomplete: a call the app shows can be absent from `list`/
`check` even though its summary and transcript exist server-side (verified —
not an account, pagination, or folder issue; a Granola-side indexing gap).
`GET /v1/notes/{id}` only takes `not_…` ids, so there is no way to reach such
a note through the API using its desktop ID.

When a call is missing, recover it yourself before involving the user:

1. Ask for the note's share link (Granola app → copy link). The share page
   HTML embeds the full summary unauthenticated (parse the `self.__next_f`
   payload), but not the transcript.
2. For the transcript, open the share link in Chrome with the claude-in-chrome
   tools and read the transcript off the rendered page — it loads client-side
   with the share token, which curl can't replay.
3. If the browser extension isn't connected, ask the user to nudge the note in
   the app (edit the title or regenerate the summary) to trigger a re-sync,
   then re-run `list`; failing that, ask them to paste the transcript.

The API orders by `created_at`, which for calendar-scheduled calls is when the
note was pre-created, not when the call happened.

## Workflow

### Step 1: Pick the call

```bash
python3 "$CALL_SKILL/scripts/granola.py" check
```

Returns JSON in one of two modes:

- **Auto** (`{"mode": "auto", "id": ..., "title": ..., "minutes_ago": ...}`) —
  a call ended within 30 minutes; proceed with it directly.
- **Select** (`{"mode": "select", "meetings": [...]}`) — no recent call;
  present the numbered list and let the user pick.

If the user already named a call or gave a doc id, skip the check.

### Step 2: Extract the transcript

```bash
python3 "$CALL_SKILL/scripts/granola.py" get <doc_id>   # or: recent <n>
```

### Step 3: Confirm participant names

The transcript only labels speakers `Me`/`Other`. Take the other participant's
name from the meeting title when it's clearly there; if the title is generic
("Weekly sync"), ask the user. **Never guess names.**

### Step 4: Create the Google Doc and hand over the link

Create the mirror doc *before* cleaning anything, so the link can be shared
while the transcript and summary are still being written. Title it
`<YYYY-MM-DD> Alejo-<Other> <Two Word Slug>` — names capitalized, dash between
(e.g. `Alejo-Jørgen`), slug in Title Case; pick a provisional slug from the
meeting title and a skim of the transcript (Step 8 may rename it).

```bash
printf 'Being written — check back shortly.\n' > /tmp/placeholder.md
gog -a <email> -j docs create "<title>" --file /tmp/placeholder.md   # → file.id, file.webViewLink
gog -a <email> docs add-tab <id> --title Transcript
gog -a <email> docs rename-tab <id> --tab t.0 --title Summary      # first tab is born "Tab 1"
```

Post the doc URL (`.../document/d/<id>/edit`) in the reply as soon as it
exists, before continuing.

Keep the doc private while it's being written, and check that creating it
didn't share it automatically. Find the other participant's email in this
order, stopping at the first hit:

1. The calendar event for the call — its attendees' emails. Check the personal
   calendar first, then the Impact Ops one:
   ```bash
   gog -a alejoacelas@gmail.com -j calendar events --from <iso> --to <iso>
   gog -a alejo@impact-ops.org -j calendar events --from <iso> --to <iso>
   ```
2. Recent email with them, same two accounts:
   `gog -a <account> -j gmail search "<first> <last>"` — take the address the
   person actually wrote from.

When the doc is finished (after Step 9), share it with that email as a writer
and send the Drive invitation email. `--notify` is what sends it; without the
flag the person gets access silently:

```bash
gog -a <email> drive share <id> --to user --email <participant-email> --role writer --notify
```

Skip sharing only when Alejo asks to keep the doc private. If none of the
sources yields an email, say so and ask for the address — never guess one. The
Drive invitation is the only email the participant gets.

Two tabs, **Summary** then **Transcript** — the Docs API supports tabs now, so
no more two-section single body. Pass `-a <email>` to every `gog` call, choosing
by the call's context: Impact Ops → `alejo@impact-ops.org`, personal →
`alejoacelas@gmail.com`; ask if unclear.
Create archive docs with `gog`, not the Google Drive MCP `create_file` tool, so
the chosen account owns them.

### Step 5: Garble inventory, then tidied transcript

Before writing the transcript, write a temporary garble inventory to
`$CALL_SKILL/data/garbles/<YYYY-MM-DD>-<person>.md`: one line per span where the
transcription seems garbled — the raw text, plus the likely reading when one
is guessable from the call itself.

Then clean the raw transcript following
[`references/tidying-instructions.md`](references/tidying-instructions.md) —
remove filler and false starts, fix transcription errors (garbled proper
nouns, tool names), relabel speakers with real first names, add headings at
topic shifts, preserve exact wording for the categories listed there. Repaired
garbles are fixed silently — no bracket note; only unresolved ones stay marked
`[unclear]` / `[name unclear]`.

Save to the person's `calls/` folder, at the path `~/best/desk/AGENTS.md` specifies, with the `-trans.md` suffix.

### Step 6: Summary

Write a chronological summary following
[`references/summary-format.md`](references/summary-format.md).

Save next to the transcript with the `-sum.md` suffix.

### Step 7: Cross-call clarification pass

Reread the finished transcript and summary against the garble inventory and
try to resolve what the single call couldn't — by reading previous calls with
the **same person** (their folder, plus git history). These files get shared
with the other participant, so never import content from calls with other
people; the wider archive may only confirm the spelling of a name or tool
already spoken in this call. Remove `[unclear]` markers as garbles resolve
(no resolution note — just the fixed text), then delete the inventory file.

### Step 8: Check slug distinctiveness

After writing, list every call file in the archive (`rg --files -g '*-trans.md' -g '*-sum.md'`). If
the new slug is generic ("intro-call", "uplift-consulting") or overlaps too
much with an earlier call's slug — in any folder — rename the new pair to
something more distinctive of this call's content, and consider renaming the
earlier colliding pair too (use `git mv` when the old files are committed).
The test: from the slug alone, could you tell the calls apart? If the slug
changed, retitle the doc: `gog -a <email> drive rename <id> "<new title>"`.

### Step 9: Fill the Google Doc + folder index

Push the finished files into the doc from Step 4 and record the call in the
folder index using the rules below. These also apply when an existing call or
summary is edited or renamed:

1. Fill both tabs. `gog` would write YAML frontmatter into the doc as text, so
   strip it first; `--tab` leaves the sibling tab alone. The tab title already
   names the section, so don't prepend a `# Summary` / `# Transcript` heading.
   The Summary tab opens with one attribution line linking this skill (update
   the URL if the repo moves):
   ```bash
   ATTR='*Summary and transcript created with the shared skill available [here](https://github.com/alejoacelas/dotfiles/blob/main/skills/summarize-call/SKILL.md).*'
   strip_fm() { awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' "$1"; }
   { printf '%s\n\n' "$ATTR"; strip_fm <sum.md>; } > /tmp/sum-doc.md
   strip_fm <trans.md> > /tmp/trans-doc.md
   gog -a <email> docs write <id> --tab Summary    --file /tmp/sum-doc.md   --markdown --replace
   gog -a <email> docs write <id> --tab Transcript --file /tmp/trans-doc.md --markdown --replace
   ```
2. Add two fields to the summary's frontmatter: `doc:` with the doc link
   (`.../document/d/<id>/edit`, by ID so a rename can't break it) and `gist:` with
   a one-or-two-sentence gist in double quotes.
3. Link client calls to client projects. For a call filed under a company's folder in
   `~/best/desk/`, make sure `~/best/clients/<company>/desk` is a symlink to that
   folder, creating it if missing. If the call is
   about project work for a company with no folder in `~/best/clients/`, ask
   whether to create `~/best/clients/<company>/` with the symlink and a short
   `AGENTS.md` naming the company and where its people's folders are.

## Batch runs

For a batch, dispatch one subagent per call so cleaning stays off the main
context. Give each: the doc id, the confirmed participant names, the full
contents of both reference files (subagents can also Read them from this
skill folder), and the exact output paths. Create every doc (Step 4) and post
all links first, then have each agent run its own Steps 5–7 (earlier
same-person calls are already committed); run Steps 8–9 once at the end, over
the whole batch — parallel agents can't see each other's slugs.
