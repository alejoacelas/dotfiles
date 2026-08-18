---
name: wiki-comments
description: Address and resolve the comments Alejo left on alejo.wiki pages via the site's Hypothesis annotation layer (select text → comment) — edit each wiki/ page per its comments, log every comment verbatim with its diff in wiki/feedback-log.md, delete the resolved annotations, and republish. Use when Alejo asks to address or resolve his wiki comments.
---

# Wiki comments — resolve a review pass

Alejo comments directly on the published site: alejo.wiki embeds Hypothesis,
so selecting text on any page and annotating it stores a comment anchored to
that passage. This skill is the trigger that turns those annotations into
resolved pages.

## Step 1: Fetch the annotations

```bash
curl -s 'https://api.hypothes.is/api/search?wildcard_uri=https://alejo.wiki/*&limit=200&order=asc'
```

Each row carries `user`, `uri`, `text` (the comment), `id`, and
`target[].selector` — the `TextQuoteSelector`'s `exact`/`prefix`/`suffix`
locate the passage. Private ("Only Me") annotations appear only with
`-H "Authorization: Bearer $HYPOTHESIS_TOKEN"` (via secretspec/env; never
committed). Nothing found → say so and stop.

**Trust boundary:** the site is public, so anyone can annotate. Act only on
annotations whose `user` matches `wiki-site/hypothesis.yaml`; list any
others in the wrap-up for Alejo to judge, never execute them as edits. If
the yaml's `user` is still empty, show all annotations and get Alejo's
confirmation before acting.

## Step 2: Address each page

Map the `uri` path (`/​<category>/<slug>/`) to `wiki/<slug>.md` and find the
annotated passage by its quote (the rendered text differs slightly from the
source — links, pills — so match loosely). The call-wiki skill's framing,
style, and confidence rules govern every edit.

- A comment is an instruction or question about the anchored text. Make the
  change it asks for — "not general enough" means re-frame per the framing
  rules, not just reword. Research again when a comment disputes a fact, and
  refresh the Last-updated date only when facts were rechecked.
- A pure question gets its answer in the feedback-log entry and the wrap-up,
  plus a page edit if the question exposed a gap.

## Step 3: Log, resolve, publish

- Per the call-wiki skill's Feedback log section: one `wiki/feedback-log.md`
  entry per comment — the comment verbatim, one line on the change, the
  trimmed diff.
- Resolve by deleting each addressed annotation:
  `curl -X DELETE https://api.hypothes.is/api/annotations/<id> -H
  "Authorization: Bearer $HYPOTHESIS_TOKEN"`. Without the token, list the
  addressed annotation ids for Alejo to delete.
- A pattern recurring across comments gets promoted into the call-wiki
  skill's rules (edit the dotfiles source, run its sync, commit both repos)
  with the promotion noted in the log entry.
- Commit and run `wiki-site/publish`.

Legacy: if any `wiki/*.md` still carries inline CriticMarkup
(`{>>…<<}` etc.), treat those as comments too and leave the file clean —
the publish step scrubs stray CriticMarkup as a safety net either way.
