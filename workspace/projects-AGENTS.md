# Projects

Use `live/` for projects being worked on now. Use topic folders: `agents/`, `connectors/`, `community/`, and `others/` for projects without a clear fit.
Name project folders `YYYY-MM-project-name`. Each project keeps its own Git repository
and remote. Consider the `once` shared-context group using `agent-context adopt`;
select it deliberately and state the scope in the project’s AGENTS.md. Do not create duplicate CLAUDE.md instructions.
Keep topic folders as ordinary directories; their shared configuration lives in dotfiles.
Apply the global privacy rules.

## Keep live projects current

Move any project with no substantive edits in the last 14 days out of `live/`.
Choose the appropriate topic folder for ongoing or parked work, or the permanent
home below for a tool, reference collection, personal material or employer work.
Preserve its repository, privacy and uncommitted work; check for a running session
before moving its checkout. Record the move and update links and indexes.

The session-start hook reports candidates when a session starts in `projects/`
or its descendants, or at the `best/` root. It does not move files itself.
It uses the latest substantive Git commit and timestamps of changed or untracked,
non-ignored files. Instruction/log-only commits and ignored outputs do not reset
the clock. Treat this as an estimate: inspect uncommitted deletions, nested repos
and copied files before deciding the actual last edit.

## Where finished work belongs

The topic names above and destination folders below are a snapshot of the current
workspace, not a fixed taxonomy. Check the actual folders before using these paths.
If you find an inconsistency, update this map and the relevant indexes to match;
suggest structural changes when the appropriate home is unclear.

If a project seems unlikely to be revisited, prefer keeping it in
`projects/<topic>/archive/` rather than moving it to another part of the workspace.
Suggest a durable home below when its output is likely to be used or maintained.
Preserve its repository and history; do not copy private material into a public repo.

| Folder in ~/best/ | Contents and suitable finished work |
|---|---|
| `tools/active/` | Tools under active development. |
| `tools/stable/` | Working tools that need occasional maintenance. |
| `writing/` | Reusable explanations, reference material and settled research. |
| `me/admin/` | Visas, paperwork and travel. |
| `me/health/` | Physical and mental health, food, meals and environment research. |
| `me/relationships/` | People to learn from, meet and know, plus relationship projects. |
| `me/sites/` | Personal blog and website. |
| `me/stuff/` | Purchases, equipment and ownership notes. |
| `calls/` | Private call transcripts, notes and related work. |
| `work/80k/` | Private employer work and its tools. |
| `work/aim/` | Aim engagements and related work. |
| `work/strategy/` | AI-enablement strategy and planning; preserve its privacy. |
| `dotfiles/` | Shared instructions, installed skills and machine configuration. |
| `dotfiles/skill-drafts/` | The separate private repository for skills in development. |
| `archive/` | Retired substantial work and workspace history without a better home. |

Each project topic folder also has `archive/` for unfinished, thin, parked or unlikely-to-be-revisited projects.
This is an explicit exception to the shared archive rule. Substantial research and
working artifacts can stay archived too when unlikely to be used again. Record each move,
its former path and the reason in that local archive's REPLICATE.md. Restore a project
to the topic folder when work resumes. Do not create a Git repository for the archive.
