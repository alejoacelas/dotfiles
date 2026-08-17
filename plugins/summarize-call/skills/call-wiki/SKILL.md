---
name: call-wiki
description: Turn a call's "I looked into X" / "I'm not sure about Y" moments into grounded wiki entries under the archive's wiki/ folder — modular ~500-word explainers with every claim traced to a primary source, linked from the call summary. Use after filing a call, or when the user asks to "build the wiki" for a call or research a call's open questions.
---

# Call wiki — ground what was said on calls

On calls I often say "I looked into this" or "I'm not sure how that works". Each
such moment becomes a wiki entry: a short file I can read to actually know the
thing, grounded in primary sources instead of my memory of them.

Entries live in `wiki/` at the archive root, shared across all calls — the same
question comes up with different people, so one entry serves them all and gets
refreshed instead of duplicated.

## Step 1: Harvest topics

Read the call's summary (Appendix 1 "Open questions" is the seed list, but scan
the whole transcript). A topic qualifies when a stranger could answer it from
public primary sources or a reproducible experiment. Harvest three kinds:

- Things I said I'd check or look into ("I'll check whether the desktop app is
  worth switching to").
- Claims I made from memory that the other person will act on ("Granola is
  private by default").
- Genuine uncertainty about a tool or fact ("not sure how often connected docs
  refresh").

Skip personal or situational questions ("what rate will Wolfie set?"), matters
of preference, and anything only a specific human can answer.

## Step 2: Check for an existing entry

`ls wiki/` and grep for the topic. If an entry exists, update it — recheck its
claims if the Checked date is old, append the new call to its footer — instead
of writing a near-duplicate. Slugs follow the archive rule: distinctive across
the whole wiki, no generic names.

## Step 3: Research and write

One entry per topic, `wiki/<topic-slug>.md`, ≤500 words:

```markdown
# <The question, as a question>

<One-line answer.>

<Body: facts with inline links to the primary source behind each claim.
Where docs don't answer, prescribe the experiment instead of hedging.>

---
Calls: [<YYYY-MM-DD> <Person> <slug>](../once/<org-name>/<file>-sum.md)
Related: [<other-entry>.md](<other-entry>.md)
Checked: <YYYY-MM-DD> — <which docs were read; what was verified live>
```

Research rules:

- No claim from memory. Every fact traces to a page actually fetched this
  session (official docs, changelogs, help centers) or is marked unverified
  with the concrete check that would settle it.
- For claims about UI — where a setting lives, what a screen shows — verify in
  the live product with the browser tools when available, and say so in the
  Checked line. Docs lag interfaces.
- Keep the body free of call content beyond the question itself. Entries are
  person-independent and safe to paste to the other participant.
- Drop the Related line when nothing relates; link liberally when it does.

Dispatch one research subagent per topic (they run in parallel); give each the
question, the claim made on the call, the format above, and the research rules
verbatim. Then edit their drafts into one voice and spot-check the links.

## Step 4: Link the entries

- `wiki/README.md` (create if missing; first line is the folder's standing
  question): one line per entry — `- [Question](slug.md) — one-line answer`.
- In the call summary's Appendix 1, append ` → [wiki](../../wiki/<slug>.md)`
  to each question that now has an entry. Claims verified wrong get a
  correction in the summary text itself, not just a link.
- Commit `wiki/` together with the call files.
