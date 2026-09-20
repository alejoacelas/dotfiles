# Projects

Start every new project in `live/`. Organize it after two weeks or on demand into
`agents/`, `connectors/`, `community/`, `others/`, or a home below.
Name projects `YYYY-MM-project-name`,
give each its own Git repository and remote, and state its scope in `AGENTS.md`.
Topic folders are ordinary directories; their shared configuration lives in dotfiles.

## Review and organize projects

After two weeks in `live/`, or when asked, read the project, commit pending work,
and sort it. Check for running sessions before moving it; preserve Git history,
uncommitted work and privacy. Record the move and update links and indexes.

The session-start hook only notifies; it neither moves projects nor recommends
destinations. It uses folder creation time as an estimate of time in `live/`
(modification time if creation time is unavailable); moved folders may appear older.

## Archive or keep for reuse

Prefer `projects/<topic>/archive/` for work unlikely to be revisited, including
substantial research and working artifacts. Do not make the archive itself a Git
repository. Record each move's
former path and reason in the archive's `REPLICATE.md`; restore projects to the topic folder
when work resumes.

Suggest a durable home for work likely to be reused or maintained. Check that these
folders still exist, correct this map and relevant indexes when needed, and suggest
structural changes if the right home is unclear. Never copy private material into a
public repository.

| Folder in `~/best/` | Contents |
|---|---|
| `tools/active/` | Tools under active development. |
| `tools/stable/` | Tools needing occasional maintenance. |
| `writing/` | Explanations, references and settled research. |
| `me/admin/` | Visas, paperwork and travel. |
| `me/health/` | Health, food, meals and environment research. |
| `me/relationships/` | People and relationships. |
| `me/sites/` | Personal blog and website. |
| `me/stuff/` | Purchases and equipment. |
| `calls/` | Private call transcripts and notes. |
| `work/80k/` | Private employer work and its tools. |
| `work/aim/` | Aim engagements. |
| `work/strategy/` | Private AI-enablement strategy and planning. |
| `dotfiles/` | Shared instructions, skills and machine configuration. |
