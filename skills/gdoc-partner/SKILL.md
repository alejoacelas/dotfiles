---
name: gdoc-partner
description: Answer Alejo's square-bracket comments in a Google Doc with a few short grey options placed under the line. Run once per call; Alejo usually runs it on a loop while he writes, e.g. `/loop 1m /gdoc-partner <doc URL>`. Use when he asks for a writing partner, suggestions or alternatives for bracket comments in a Google Doc.
---

# Google Doc writing partner

Alejo drafts in the doc (outreach emails, interview questions, essays, often for
Impact Ops) and types requests to you inline as `[...]`. Requests are terse and
point at the nearby text: "[doing?]" means "is *doing* the right word here?",
"[more options for 2]" refers to your earlier option (b) or sentence 2. When a
request mentions calls or people, read the call notes in `~/best/desk/comms/` or
Granola.

## Each run

1. Read the tab given in the URL: `gog --account alejoacelas@gmail.com docs cat <docId> --tab <tabId>`.
2. Find open requests. If the doc uses `[ai: ...]`, answer only those. Otherwise
   answer brackets that ask for something; leave placeholders and notes such as
   `[link]` or `[2yr]` alone.
3. Skip a request when:
   - your `→` lines already sit under it;
   - you answered it earlier in this session and Alejo deleted your lines (he
     read them; that is his answer);
   - it has no closing `]` yet, or the line is mid-word: he is still typing.
     Answer it on the next run.
4. Answer in the format below, then reply in the terminal with one line saying
   what you answered, or "Nothing new."

Leave Alejo's text and brackets untouched.

## Answer format

Put the options directly under the paragraph holding the comment, so the line he
is reading stays where it is.

```
→ …run AI adoption audits for a few organisations
→ …offer a quick AI adoption check
→ …am running audits; Impact Ops was the first
```

- 2–4 options, one per line, each starting with `→ `.
- Show only the part that changes, with `…` for the untouched rest. Give a full
  sentence only when the whole sentence changes.
- No heading line, no numbering, no rationale. When he asks for your opinion
  ("what's your take?"), the first line gives it in one sentence.
- If the request needs facts you don't have, one `→ ` line saying what is
  missing.
- Style: colour `#999999`, 9 pt, no bullets.

To insert, find the end of the comment's paragraph and write the lines after it:

```bash
D=<docId>; T=<tabId>; A=alejoacelas@gmail.com
END=$(gog docs find-range $D "<end of the comment text>]" --account $A --tab $T | cut -f2)
L=("→ …option one" "→ …option two")
gog docs update $D --account $A --tab $T --index "$END" --text "$(printf '\n%s' "${L[@]}")"
for l in "${L[@]}"; do
  gog docs format $D --account $A --tab $T --match "$l" --text-color '#999999' --font-size 9 --no-bullets
done
```

If the doc changed under the request and the insert fails, read it again and
retry once; otherwise wait for the next run.
