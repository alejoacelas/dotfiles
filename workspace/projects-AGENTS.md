# Projects

Use topic folders: `agents/`, `connectors/`, `community/`, and `others/` for projects without a clear fit.
Name project folders `YYYY-MM-project-name`. Each project keeps its own Git repository
and remote. Declare the `once` shared-context group using `agent-context adopt`, state
the scope in its AGENTS.md. Do not create duplicate CLAUDE.md instructions.
Keep topic folders as ordinary directories; their shared configuration lives in dotfiles.
Apply the global privacy rules.

## Where finished work belongs

The topic names above and destination folders below are a snapshot of the current
workspace, not a fixed taxonomy. Check the actual folders before using these paths.
If you find an inconsistency, update this map and the relevant indexes to match;
suggest structural changes when the appropriate home is unclear.

When a project finishes, suggest moving it to the durable home that fits its output.
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

Each project topic folder also has `archive/` for unfinished, thin or parked projects.
This is an explicit exception to the shared archive rule. Keep substantial research
and working artifacts visible even if future improvements remain. Record each move,
its former path and the reason in that local archive's REPLICATE.md. Restore a project
to the topic folder when work resumes. Do not create a Git repository for the archive.
