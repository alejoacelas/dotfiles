# Workspace procedures

Read only the section relevant to the task.

## Creating or moving projects

- Follow [projects/AGENTS.md](/Users/alejo/best/projects/AGENTS.md) for starting,
  reviewing and organizing projects.
- Read the destination's `AGENTS.md` before creating or moving anything there.
- Follow the folder's archive rules. Record moves with their old path and reason;
  preserve repository history and privacy.

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
