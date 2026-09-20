# Projects

Start every new project in `live/`. Name projects `YYYY-MM-project-name`,
give each its own Git repository and remote, and state its scope in `AGENTS.md`.
Topic folders are ordinary directories; their shared configuration lives in dotfiles.

## Review and organize projects

After two weeks without edits in `live/`, or when asked, read the project, commit
pending work, and choose an appropriate home under `~/best/`. Check for running
sessions before moving it; preserve Git history,
uncommitted work and privacy. Record the move and update links and indexes.

The session-start hook identifies projects with at least two weeks of inactivity
and reports days since their last edit. Use its notices to select projects for review.

## Archive or keep for reuse

Prefer `projects/<topic>/archive/` for work unlikely to be revisited, including
substantial research and working artifacts. Keep archives as ordinary directories
containing project repositories. Record each move's former path and reason in the archive's `REPLICATE.md`;
restore projects to the topic folder when work resumes.

Suggest a durable home for work likely to be reused or maintained. Inspect the
existing folders and their instructions; suggest structural changes if the right
home is unclear.
