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

## Session records

Use short titles in `REPLICATE.md`. Open each entry with one sentence stating what
the human wanted, then a few bullets pairing concrete work with findings or outputs.
Keep roadblocks that changed the approach or still limit the result. Use numbers
when they convey scale or improvement. Omit routine steps; do not backfill old entries.

Commit substantive changes first. In a metadata-only follow-up commit, end the entry
with `Agent session [session ID] · Commits [commit hash]`. List every substantive
change hash when needed; label hashes by repository for work spanning repositories.

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
