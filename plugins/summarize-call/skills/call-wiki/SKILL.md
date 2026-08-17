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

One entry per topic, `wiki/<topic-slug>.md`, ≤500 words, in the house wiki
style (the model is `~/best/80k/08-10-mcp-ops-session/wiki/`):

```markdown
---
title: <The question, as a question>
sidebar: <short sidebar name, 2–3 words, distinct within its category>
category: <group slug — see below>
calls:
  - "[<YYYY-MM-DD> <Person> <slug>](../once/<org-name>/<file>-sum.md)"
---

<One-line answer a reader could act on without reading further.>

<Body: short sections headed by the reader's next question. Facts with the
primary source hyperlinked inline in prose — never a bare URL or footnote
list. Where docs don't answer, prescribe the experiment instead of hedging.
Weave cross-links to other entries into sentences, as [text](<slug>.md).>

---
*Checked <YYYY-MM-DD> — <docs read; what was verified live; what stays
inferred>.*
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
  Checked line.

Research rules:

- No claim from memory. Every fact traces to a page actually fetched this
  session (official docs, changelogs, help centers) or is marked unverified
  with the concrete check that would settle it.
- For claims about UI — where a setting lives, what a screen shows — verify in
  the live product with the browser tools when available, and say so in the
  Checked line. Docs lag interfaces.
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
  question): one line per entry — `- [slug.md](slug.md) — one-line answer` —
  under a `## <Category>` heading matching the entry's category.
- In the call summary's Appendix 1, append ` → [wiki](../../wiki/<slug>.md)`
  to each question that now has an entry. Claims verified wrong get a
  correction in the summary text itself, not just a link.
- Commit `wiki/` together with the call files.

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
