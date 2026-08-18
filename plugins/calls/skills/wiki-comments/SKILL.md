---
name: wiki-comments
description: Address and resolve the CriticMarkup comments Alejo left on wiki/ pages via Roughdraft (wiki/review) — edit each page per its comments, strip the markup, log every comment verbatim with its diff in wiki/feedback-log.md, and republish. Use when Alejo asks to address or resolve his wiki comments, or after a Roughdraft review session on wiki entries.
---

# Wiki comments — resolve a review pass

Alejo reviews entries with `wiki/review <slug>` (Roughdraft); his comments
and suggested edits are saved into the entry file itself as CriticMarkup,
with metadata in trailing YAML endmatter (`roughdraft help criticmarkup` has
the syntax). This skill is the trigger that turns a review pass into
resolved pages.

## Step 1: Find the comments

`grep -l '{>>\|{++\|{--\|{~~\|{==' wiki/*.md` (README.md and feedback-log.md
don't count). `roughdraft doctor wiki/<slug>.md` counts a file's comments
and suggestions. Nothing found → say so and stop.

## Step 2: Address each page

Work page by page; the call-wiki skill's framing, style, and confidence
rules govern every edit.

- A comment (`{>>…<<}`) is an instruction or question about the anchored
  text. Make the change it asks for — "not general enough" means re-frame
  per the framing rules, not just reword. Research again when a comment
  disputes a fact, and refresh the Last-updated date only when facts were
  rechecked.
- A suggestion (`{++…++}`, `{--…--}`, `{~~old~>new~~}`) is a proposed edit:
  apply it unless it breaks a rule (an unsourced claim, a name in the body);
  when declining, say why in the wrap-up.
- A pure question gets its answer in the feedback-log entry and the wrap-up,
  plus a page edit if the question exposed a gap.
- Leave the page clean: no CriticMarkup, no `{#c1}`/`{id=…}` anchors, no
  comments/suggestions endmatter — `roughdraft doctor` counts zero.

## Step 3: Log, commit, publish

- Per the call-wiki skill's Feedback log section: one `wiki/feedback-log.md`
  entry per comment — the comment verbatim, one line on the change, the
  trimmed diff.
- A pattern recurring across comments gets promoted into the call-wiki
  skill's rules (edit the dotfiles source, run its sync, commit both repos)
  with the promotion noted in the log entry.
- Commit and run `wiki-site/publish`. The publish step scrubs any stray
  CriticMarkup so an unaddressed comment never ships — but one surviving to
  publish means Step 2 missed it.
