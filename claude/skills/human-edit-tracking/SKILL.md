---
name: human-edit-tracking
description: Preserve handwritten changes to AGENTS.md, CLAUDE.md, README.md and files marked with two semicolons, using separate history records.
---
# Human edit tracking

Before editing AGENTS.md, CLAUDE.md or README.md, inspect its uncommitted diff and read
its `human_edit_history` reference, if present. Also consult relevant records in
`.agent-history/`. Preserve handwritten wording unless Alejo authorizes changing it.

The session-start `agent-context` hook saves diffs containing newly added `;;` markers
under `.agent-history/observed/`. These are evidence, not an authorship verdict.
For edits during an existing session, inspect the Git diff directly.

- If a change is clearly Alejo's, record the complete before and after passages verbatim
  in `.agent-history/<filename>.yaml`, without the `;;` markers. Then remove the markers.
- If authorship is unclear, ask `Was this change by you?` before attributing it to him.
- Add a `human_edit_history` reference in the document's front matter. Do not embed history.
- Commit the record with the document so the next edit has a clean baseline.

Existing inline histories must be moved verbatim to the referenced record before editing.
Do not truncate or discard old history records.
