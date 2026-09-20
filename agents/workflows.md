# Workspace procedures

Read only the section relevant to the task.

## Creating or moving projects

- Follow [projects/AGENTS.md](/Users/alejo/best/projects/AGENTS.md) for starting,
  reviewing and organizing projects.
- Read the destination's `AGENTS.md` before creating or moving anything there.
- Only the `80k` shared group is approved. Select it for relevant private employer
  work with `~/best/dotfiles/bin/agent-context adopt`; do not recreate other groups.
  No group is automatic. Membership lives in `agents/projects.json` or the private
  context repository, not project YAML. Update the selection when moving a project.
  Startup and compaction read shared sources without rewriting project files.
- Follow the folder's archive rules; Alejo decides them case by case. There is no
  workspace-wide archive destination. Record moves with their old path and reason;
  preserve repository history and privacy.

## Decision records

Use `REPLICATE.md` to prevent important decisions from being accidentally undone.
Select choices that answer a real recurring tension or a costly mistake supported
by the project and its history. Group choices that protect the same outcome. Expand
each with the current rule, its reason and only the exceptions that affect future
work. Discard history that no longer changes what someone should do.

Use a short title, then “Core decisions”, then “Details”. Under Core decisions,
group related choices under descriptive headings, with individual decisions as
concise bullets. Each bullet links to its matching subsection under Details. Aim
for 3–5 groups and 6–10 decision bullets; do not pad a small project to meet a count.
The core section should make sense on its own. Do not add an appendix of omitted
material.

Read the existing record, relevant instructions and README, and the actual code,
configuration and tests. Follow substantive commits and diffs to understand reasons,
reversals and constraints; do not rely on commit titles or merely summarize the old
log. Use implementation to establish current behavior and history to establish
reasons. Distinguish recorded intentions, observed behavior and inference. Do not
invent motivations or treat passing tests as proof of live production behavior.

Keep only decisions whose loss could lead to a consequential mistake. Omit routine
implementation facts, feature inventories, setup recipes, repeated test counts and
incidental session activity. Keep past failures only when they explain a current
constraint or prevent recurrence. Link to relative source files and relevant commit
hashes instead of reproducing recoverable mechanics. Never include credentials or
raw private user data.

Update decisions in place and remove superseded details; Git preserves history.
Do not add an entry merely because a session happened. Commit substantive work
first, then update the decision record in a metadata-only follow-up commit, citing
the relevant substantive hashes. Rewriting an existing chronological record needs
the same investigation as a new one; do not install a stale experimental draft.

## Orca Markdown

Use collapsibles only as `<details class="orca-details">` with a plain `<summary>`
and a Markdown body. Never nest them. Escape HTML-like strings inside collapsible
code blocks. Split HTML-bearing files before 50,000 characters.

## Local macOS applications

Sign apps requiring Accessibility, Screen Recording, microphone, camera or similar
grants with a stable local identity. Ad-hoc signatures change identity on each build,
leaving enabled privacy toggles that the rebuilt app cannot use. Fail the build when
its expected signing identity is missing; never silently fall back to ad-hoc signing.

## Markdown review

Use Zed by default to open Markdown for human review.
Open files with `open -a Zed "/absolute/path/to/file.md"` on macOS.
After the user reviews or edits a document, reread it before making further changes.
