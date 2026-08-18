---
name: call-wiki
description: Turn a call's "I looked into X" / "I'm not sure about Y" moments into grounded wiki entries under the archive's wiki/ folder — modular ~300-word explainers with every claim traced to a primary source and tagged by confidence, linked from the call summary. Use after filing a call, or when the user asks to "build the wiki" for a call or research a call's open questions.
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
claims if its Last-updated date is old, append the new call to its
frontmatter — instead of writing a near-duplicate. Slugs follow the archive rule: distinctive across
the whole wiki, no generic names.

## Step 3: Research and write

One entry per topic, `wiki/<topic-slug>.md`, roughly 250–350 words plus the
Sources list:

```markdown
---
title: <The question, as a question>
sidebar: <short sidebar name, 2–3 words, distinct within its category>
category: <group slug — see below>
calls:
  - "[<YYYY-MM-DD> <Person> <slug>](../once/<org-name>/<file>-sum.md)"
---

*Last updated <YYYY-MM-DD> · Confidence: <rung> — <short provenance clause;
name any deviating claims, e.g. "documented — Slack's help center and
developer docs; the channel-reminder silence is inferred">.*

<One-line answer a reader could act on without reading further.>

<Body: short sections. Facts with the primary source hyperlinked inline in
prose. Where docs don't answer, prescribe the experiment instead of hedging.
Weave cross-links to other entries into sentences, as [text](<slug>.md).>

## Q&A from calls

<Only when the page generalizes past the call's question — see framing
rules. **The question as asked.** The direct answer.>

## Sources

- <one bullet per page read: [<page title>](<url>) — <site>>
```

Frontmatter rules:

- `title`, `sidebar`, and `category` are the only fields that go public;
  everything else — `calls` provenance included — stays in the private repo
  (the publish step drops unknown fields by default, so new metadata is safe
  to add).
- `category` drives the published sidebar's groups and the URL
  (`alejo.wiki/<category>/<slug>/`). List the existing ones
  (`grep -h '^category:' wiki/*.md | sort -u`) and reuse the group that fits;
  create a new one only when none does, and name any new category in your
  wrap-up so Alejo can review the grouping.
- An updated entry appends the new call to `calls:` and refreshes the
  Last-updated line.

Framing rules:

- Write for the underlying problem, not the literal question. When the
  literal answer is thin or a dead end, go up one level of abstraction to
  the page a broader audience would search for ("Granola vs Fireflies", not
  "where is Granola's auto-join setting") — and still answer the call's
  question explicitly, in the `## Q&A from calls` section when it no longer
  fits the main narrative.
- The lead paragraph headlines what solves the problem, not the dead end:
  "Cowork only schedules, but routines take event triggers" — never "no,
  scheduled tasks only".
- Section headings must be self-explanatory standing alone: a short category
  label ("Sources") or a TLDR of the section ("Cowork: scheduled tasks,
  hourly at most"). Never a phrase the reader needs the section to decode.

Style rules:

- Short paragraphs, 1–3 sentences, one idea each.
- Three or more parallel items — triggers, source pages, feature lists — are
  bullets, one item per bullet, never a comma-run in prose.
- Say each fact once. In a ~300-word page nothing repeats; at most a
  one-line recap at the end.
- Cross-link text is the target entry's `sidebar` name or a natural phrase,
  never the filename: "see [Event triggers](claude-event-triggers.md)", not
  "see claude-event-triggers.md".
- Link over quote: when a short, targeted source carries the detail, state
  the conclusion and link. Quote only where the exact wording is the
  evidence. Cut plan tiers, beta labels, and platform footnotes unless they
  change what the reader does.
- No recommendations unless Alejo made one on the call — then attribute it
  ("Alejo recommends…"). Otherwise describe features neutrally: no "worth
  it", "best", or "bottom line" verdicts. Alejo is the one name allowed in
  a body; call participants never appear.

Confidence ladder — every claim sits on a rung:

- `tried` — someone ran it recently and it worked: verified live this
  session, or a dated first-hand report from the user or a call participant.
- `reported` — a dated first-hand account from someone else (forum thread,
  issue tracker).
- `documented` — the vendor's current docs state it.
- `inferred` — stated nowhere; follows from documented behavior. Always
  pair with the test that settles it: "(inferred — a one-minute test
  reminder settles it)".

State the page's default rung in the Last-updated line; tag inline, in
parentheses, only the claims that deviate — exactly `(inferred — <note>)` or
`(reported — <note>)`, since the publish step turns that pattern into a
hover-underline on the claim and rung words in the header line into pills
linking the /confidence/ ladder page (`wiki-site/pages/confidence.md`).

Research rules:

- Before drafting, skim the existing wiki entries to calibrate scope and
  level of detail against neighbors and catch overlaps. For pages comparing
  products or surfaces, also pull the vendor's own feature list — a
  comparison that misses a major feature (a whole browser extension, say)
  fails review.
- No claim from memory. Every fact traces to a page actually fetched this
  session (official docs, changelogs, help centers) or is marked unverified
  with the concrete check that would settle it.
- For claims about UI — where a setting lives, what a screen shows — verify in
  the live product with the browser tools when available — that claim earns
  the `tried` rung. Docs lag interfaces.
- Self-contained: a reader landing on any entry needs other pages only to go
  deeper, not to act.
- No names or personal information anywhere in the body — general-purpose
  wording only, even when describing the question a call raised. Provenance
  lives solely in the `calls:` frontmatter, which never leaves the private
  repo.

Dispatch one research subagent per topic (they run in parallel); give each the
question, the claim made on the call, the format above, and the research rules
verbatim. Then edit their drafts into one voice and spot-check the links.

## Step 4: Link the entries

- `wiki/README.md` (create if missing; first line is the folder's standing
  question): one line per entry — `- [<sidebar name>](<slug>.md) — <one-line
  answer>` — under a `## <Category>` heading matching the entry's category.
  Never use a filename as link text: everywhere a reader sees an entry it
  goes by its `sidebar` name (same rule as cross-links).
- In the call summary's Appendix 1, append ` → [wiki](../../wiki/<slug>.md)`
  to each question that now has an entry. Claims verified wrong get a
  correction in the summary text itself, not just a link.
- Commit `wiki/` together with the call files.

## Feedback log

`wiki/feedback-log.md` (private; the publish step skips it) collects Alejo's
feedback on existing wiki pages and what changed in response — the raw
material for improving this skill. Whenever he critiques a page ("not general
enough", "too dense"), append an entry as part of acting on it: date and
scope heading, his comment **verbatim** (never paraphrased), one line on what
changed, and the diff trimmed to the hunks the feedback caused. One entry per
comment, chronological. When a pattern recurs across entries, promote it into
this skill's rules and note the promotion in the entry.

## Step 5: Publish

First make sure the call's participant has a row in `wiki-site/people.yaml`
— slug is their first name plus last-name initial (e.g. `katym`), `folders`
their archive folders. That gives them a public short link,
`alejo.wiki/<person-slug>`, listing every entry derived from calls with them
(first name only appears on the page; it stays out of the sidebar and site
search).

Then run `wiki-site/publish` (archive root). It sanitizes every entry —
keeping private frontmatter and names off the public site — rebuilds the
Astro site, and deploys to [alejo.wiki](https://alejo.wiki). End the wrap-up
with the person's short link — that's what to send them.
