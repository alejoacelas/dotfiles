# Projects

Start every new project in `live/`. Name it `YYYY-MM-project-name`, give it its
own Git repository and remote, and state its scope in `AGENTS.md`. Topic folders
are ordinary directories whose shared files live in dotfiles.

## Review and organize

The session-start hook reports `live/` projects untouched for two weeks. When it
does, or when asked: read the project, commit pending work, check for running
sessions, then move it to its topic folder, or to `<topic>/archive/` if it is
unlikely to be revisited. Preserve Git history and privacy, record the move and
its reason in the archive's `DECISIONS.md`, and update links and indexes. Move a
project back to its topic folder when work resumes. If no folder fits, suggest a
structural change.
