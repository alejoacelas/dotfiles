---
name: tidy-up
description: Audit /Users/alejo/best/tools projects by attention state, git remote, and first and last commit dates.
---

# Tidy Up

When working in `/Users/alejo/best/tools`:

- Treat `/tidy-up` as the shorthand for this workflow.
- Distinguish projects from topic groups under `active/`, `upcoming/`, and `stable/`.
- For a topic group, inspect its child repositories; the group itself is not a repository.
- Keep workspace config in dotfiles; lifecycle and topic folders are not repositories.
- Confirm each project has its own git remote.
- Commit meaningful edits in the project repo; push when a remote exists.
- Classify by required attention, not commit recency: `active` is being developed,
  `upcoming` is deferred, and `stable` only needs attention when it breaks.

## Project Age Check

Run:

```bash
.codex/skills/tidy-up/scripts/project-age-report.sh
```

Use the first commit date as the project start date and the last commit date as the
activity date. Flag an `active` project after 14 days without a substantive commit so
its status is reconsidered; do not move it automatically.

Moving a folder between the three state directories changes its status.
