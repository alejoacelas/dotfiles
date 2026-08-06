---
name: human-edit-tracking
description: Preserve a person's uncommitted edits to tracked Markdown before an agent continues editing. Use when a UserPromptSubmit hook reports changes to README.md, AGENTS.md, CLAUDE.md, or a Markdown file whose human_edit_tracking.enabled field is true, and when creating or updating those files' full-text human-edit history.
---

# Human edit tracking

Treat the hook's diff as evidence, not an authorship verdict. Compare it with your own
actions and the conversation.

- If the changes are clearly Alejo's, record every addition, deletion, and replacement
  verbatim under `human_edit_tracking.history`, then say what you recorded.
- If authorship is unclear, ask `Was this change by you?` Do not record it until Alejo
  confirms. If he says no, leave the history unchanged.
- Before returning work that changes a tracked `README.md`, `AGENTS.md`, or `CLAUDE.md`,
  commit those files so the next diff has a clean baseline.

Use this schema:

```yaml
---
human_edit_tracking:
  enabled: true
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

`README.md`, `AGENTS.md`, and `CLAUDE.md` are tracked by default. Other Markdown files opt
in through `human_edit_tracking.enabled: true`.

Run `scripts/human_edit_hook.py --show <file>` when the hook's injected diff was truncated.
