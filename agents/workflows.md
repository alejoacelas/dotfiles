# Workspace procedures

Read only the section relevant to the task.

## Creating or moving projects

- Put one-offs in `~/best/projects/`, named `YYYY-MM-project-name`, with their own
  repository and GitHub remote. Read `~/best/projects/AGENTS.md` for current placement.
- Keep essays and reference collections in `~/best/writing/`; employer and aim work
  in `~/best/work/{80k,aim}/`. Draft skills live in the separate private repository
  `~/best/dotfiles/skill-drafts/`.
- Read the destination's `AGENTS.md` before creating or moving anything there.
- Only the `80k` shared group is approved. Select it for relevant private employer
  work with `~/best/dotfiles/bin/agent-context adopt`; do not recreate other groups.
  No group is automatic. Membership lives in `agents/projects.json` or the private
  context repository, not project YAML. Update the selection when moving a project.
  Startup and compaction read shared sources without rewriting project files.
- Archive retired work in `~/best/archive/`. Project topic folders may use their
  own `archive/` for unfinished or insubstantial work. Record the old path and reason
  in the destination archive's `REPLICATE.md`. Preserve repository history and privacy.

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

## Claude instruction compatibility

Claude Code 2.1.277+ can load `AGENTS.md` natively when no ancestor or project
`CLAUDE.md` or `CLAUDE.local.md` suppresses fallback. Keep an `@AGENTS.md` shim only
for a verified compatibility need; preserve files with distinct content, such as
call indexes.
