---
name: summarize-call
description: Fetch a Granola call transcript from the API, clean it, and file a tidied transcript plus a structured summary under the person's once/many call folder. Use when the user wants to pull, clean, summarize, or archive Granola calls — "summarise my call", "save my last Granola call", "archive these calls".
---

# Granola call → tidied transcript + summary

Adapted from [HartreeWorks/skill--summarise-granola](https://github.com/HartreeWorks/skill--summarise-granola),
rewired to file into this repo's call archive. Reads transcripts over Granola's
[public API](https://docs.granola.ai) with a personal key — no cache, no connector.

## Setup (once)

`granola.py` authenticates with a Granola public API key. Generate one in the
Granola app (**Settings → API**) — it looks like `grn_…` — then put it in a
gitignored `.env` beside the script so it never lands in shell history or a chat
transcript:

```bash
cp .env.example .env   # then paste your grn_ key into .env
```

A bare `grn_…` line works too; `$GRANOLA_API_KEY` in the environment overrides
the file. That's the whole setup — the public API returns JSON, so no extra
packages are needed.

Legacy fallback: with no key set, the script tries to decrypt Granola's local
desktop token store, which needs the `cryptography` package in a skill-local
`.venv/` (`python3 -m venv .venv && .venv/bin/pip install cryptography`; the
script re-execs under it automatically). This path broke with Granola 7.4x,
which moved the decryption key into an app-scoped macOS Keychain item that only
Granola-signed code can read — hence the public-API key above.

## Commands

```bash
python3 scripts/granola.py list [n]      # n most recent meetings (default 20; paginates)
python3 scripts/granola.py check         # recent-call / selection JSON
python3 scripts/granola.py get <doc_id>  # print transcript markdown for one call
python3 scripts/granola.py recent [n]    # nth most recent transcript
```

`get <doc_id>` prints the raw transcript to stdout (also saved under
`data/transcripts/`). Speakers are `**Me**:` (the account holder, Alejandro)
and `**Other**:` (everyone else).

These commands are the default path for every call. But the public API index
is sometimes incomplete: a call the app shows can be absent from `list`/
`check` even though its summary and transcript exist server-side (verified —
not an account, pagination, or folder issue; a Granola-side indexing gap).
`GET /v1/notes/{id}` only takes `not_…` ids, so there is no way to reach such
a note through the API, and the desktop-token fallback is dead (see above).

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
python3 scripts/granola.py check
```

Returns JSON in one of two modes:

- **Auto** (`{"mode": "auto", "id": ..., "title": ..., "minutes_ago": ...}`) —
  a call ended within 30 minutes; proceed with it directly.
- **Select** (`{"mode": "select", "meetings": [...]}`) — no recent call;
  present the numbered list and let the user pick.

If the user already named a call or gave a doc id, skip the check.

### Step 2: Extract the transcript

```bash
python3 scripts/granola.py get <doc_id>   # or: recent <n>
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
gdoc --json new "<title>" --file /tmp/placeholder.md      # → id, url
gdoc --json add-tab <id> "Transcript"
GDOC_PY=$(head -1 "$(which gdoc)" | cut -c3-)             # gdoc's interpreter
$GDOC_PY scripts/rename_tab.py <id> t.0 "Summary"        # first tab is born "Tab 1"
```

Post the doc URL (`.../document/d/<id>/edit`) in the reply as soon as it
exists, before continuing.

Then share it with the other participant, finding their email in this order
and stopping at the first hit:

1. The calendar event for the call — its attendees' emails. Check the 80k
   calendar first, then the personal one (`gog` picks the right OAuth client
   from the account):
   ```bash
   gog -a alejandro.acelas-contractor@80000hours.org -j calendar events --from <iso> --to <iso>
   gog -a alejoacelas@gmail.com -j calendar events --from <iso> --to <iso>
   ```
2. Recent email with them, same two accounts:
   `gog -a <account> -j gmail search "<first> <last>"` — take the address the
   person actually wrote from.

If `gog` reports no auth for a service, the Google Calendar / Gmail MCP
connectors (80k account) are the fallback.

```bash
gdoc share <id> <email> --role writer
```

Say in the reply who the doc was shared with. If neither source yields an
email, say so and skip sharing — never guess an address. (Mirror docs are
shared, never emailed: the link in the reply is for Alejo to send.)

Two tabs, **Summary** then **Transcript** — the Docs API supports tabs now, so
no more two-section single body. Pass `--account <email>` to every `gdoc` call
(and `GDOC_ACCOUNT=<email>` to `rename_tab.py`), choosing by the call's context:
80,000 Hours work → `alejandro.acelas-contractor@80000hours.org`, personal →
`alejoacelas@gmail.com`; ask if unclear. Never use the Google Drive MCP
`create_file` tool for archive docs — `gdoc diff`/`write` need a doc the chosen
`gdoc` account owns.

### Step 5: Garble inventory, then tidied transcript

Before writing the transcript, write a temporary garble inventory to
`data/garbles/<YYYY-MM-DD>-<person>.md`: one line per span where the
transcription seems garbled — the raw text, plus the likely reading when one
is guessable from the call itself.

Then clean the raw transcript following
[`references/tidying-instructions.md`](references/tidying-instructions.md) —
remove filler and false starts, fix transcription errors (garbled proper
nouns, tool names), relabel speakers with real first names, add headings at
topic shifts, preserve exact wording for the categories listed there. Repaired
garbles are fixed silently — no bracket note; only unresolved ones stay marked
`[unclear]` / `[name unclear]`.

Save to the filing path below with the `-trans.md` suffix.

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

After writing, list every call file in the archive (`ls once/*/ many/*/`). If
the new slug is generic ("intro-call", "uplift-consulting") or overlaps too
much with an earlier call's slug — in any folder — rename the new pair to
something more distinctive of this call's content, and consider renaming the
earlier colliding pair too (use `git mv` when the old files are committed).
The test: from the slug alone, could you tell the calls apart? If the slug
changed, retitle the doc: `gdoc rename <id> "<new title>"`.

### Step 9: Fill the Google Doc + folder index + NOTES.md

Push the finished files into the doc from Step 4 and record the call in the
folder index (see the archive `CLAUDE.md` → **Folder index + Google Doc
mirror** and **Per-person NOTES.md** for the canonical rules):

1. Fill both tabs (`write` strips YAML frontmatter itself; `--tab` leaves the
   sibling tab alone; `cat` sets the read baseline `write` requires). The tab
   title already names the section, so don't prepend a `# Summary` /
   `# Transcript` heading. The Summary tab opens with one attribution line
   linking this skill (update the URL if the repo moves):
   ```bash
   ATTR='*Summary and transcript created with the Claude skill available [here](https://github.com/alejoacelas/dotfiles/blob/main/plugins/calls/skills/summarize-call/SKILL.md).*'
   { printf '%s\n\n' "$ATTR"; awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' <sum.md>; } > /tmp/sum-doc.md  # frontmatter must not sit below the line
   gdoc cat <id> > /dev/null
   gdoc write <id> /tmp/sum-doc.md --tab Summary
   gdoc write <id> <trans.md>      --tab Transcript
   ```
2. Add a bullet to the person's folder `CLAUDE.md` (create it on the first call):
   `**<date> · <slug>**` + a `[gdoc]` link (`.../document/d/<id>/edit`, by ID so a
   rename can't break it) + a one-or-two-sentence gist, newest first.
3. Update the person's `NOTES.md` (create it on the first call): add a
   `## <YYYY-MM-DD> <Slug In Title Case>` section, newest first, with 3–10 bullets
   of under 12 words each — written for the people who were on the call, so each
   bullet brings back a moment rather than explains itself. Then sync its mirror
   doc: on first creation, `gdoc new "Alejo-<Other> Call Notes" --file
   NOTES.md`, append `---` + `Google Doc: <link>` to the file, and push once so
   the doc includes the footer; on later calls, `gdoc diff <id> NOTES.md` first
   and fold any remote edits into the local file, then
   `gdoc cat <id> > /dev/null && gdoc write <id> NOTES.md`. Never recreate the
   doc — the link must stay stable.

### Step 10 (off by default): Wiki pass

Do **not** run this unless the user asks for a wiki pass. Kept here so it can
be re-enabled later: follow the `call-wiki` skill (sibling to this one) —
harvest the call's "I looked into / I'm not sure" moments, research each
against primary sources, and file grounded entries in the archive's `wiki/`,
linked from the summary's open questions. It runs last so the Google Doc
snapshot stays free of repo-relative links.

## Filing rule

```
people/work/<once|many>/<org-firstname>/<YYYY-MM-DD>-<two-word-slug>-trans.md
people/work/<once|many>/<org-firstname>/<YYYY-MM-DD>-<two-word-slug>-sum.md
```

- **org-firstname** — a short org identifier (usually three letters, from
  their email domain), then lowercase first name: 80,000 hours → `80k`,
  impact ops → `iops`, catalyze impact → `cat`, ambitious impact → `aim`,
  coefficient giving → `cg`, anthropic → `ant`, independent / no clear org →
  `ind`. One folder per person; reuse it across calls.
- **once/** — people with a single recorded call. **many/** — repeat people
  only (a suggested follow-up doesn't count); move a `once/` folder over when
  a second call lands.
- **two-word-slug** — a short two-word description of the call (e.g.
  `agentic-coaching`, `career-advice`). Two calls with one person on the same
  day get distinct slugs.

## Batch runs

For a batch, dispatch one subagent per call so cleaning stays off the main
context. Give each: the doc id, the confirmed participant names, the full
contents of both reference files (subagents can also Read them from this
skill folder), and the exact output paths. Create every doc (Step 4) and post
all links first, then have each agent run its own Steps 5–7 (earlier
same-person calls are already committed); run Steps 8–9 once at the end, over
the whole batch — parallel agents can't see each other's slugs. A wiki pass,
if requested, must dedupe topics across the batch's calls.
