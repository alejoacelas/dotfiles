---
name: human-edit-tracking
description: Preserve Alejo's uncommitted edits to AGENTS.md, CLAUDE.md, and README.md before an agent continues editing; use for other Markdown only when Alejo explicitly asks or a UserPromptSubmit hook reports a new ;; marker. Also use when creating or updating human_edit_tracking history.
---

# Human edit tracking

Human-edit tracking is off by default. Track only `AGENTS.md`, `CLAUDE.md`, and
`README.md`; files Alejo explicitly asks to track; or files whose new edits contain
`;;`. Before changing one of the three instruction files, inspect its uncommitted diff.
For a marked edit, the user-prompt hook reports the diff. Treat the diff as evidence,
not an authorship verdict: compare it with your own actions and the conversation.

- If the changes are clearly Alejo's, record every addition, deletion, and replacement
  verbatim under `human_edit_tracking.history` — without the `;;` markers themselves —
  then delete the markers from the file and say what you recorded.
- If authorship is unclear, ask `Was this change by you?` Do not record it until Alejo
  confirms. If he says no, leave the history unchanged.
- Commit the file after recording so the next marked edit diffs against a clean
  baseline.

Use this schema, adding the front matter only when a file records its first entry.
Never add or retain an empty tracking block.

```yaml
---
human_edit_tracking:
  history:
    - date: 2026-08-05
      changes:
        - added: |-
            Exact added text.
        - removed: |-
            Exact deleted text.
        - replaced:
            before: |-
              Exact replaced text.
            after: |-
              Exact replacement text.
---
```

One dated entry may contain changes in many parts of the file. Preserve complete changed
passages rather than summarizing them. After adding an entry, keep `history` at or below
2,000 words by removing the oldest complete entries first. Never truncate the newest entry;
keep it whole even when it alone exceeds the limit.

Run `scripts/human_edit_hook.py --show <file>` when the hook's injected diff was truncated.
