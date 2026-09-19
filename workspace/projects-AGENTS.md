# Projects

Use topic folders: `agent-workflows/`, `connectors/`, `research-evaluations/`,
`ai-community/`, and `others/` for projects without a clear fit.
Name project folders `YYYY-MM-project-name`. Each project keeps its own Git repository
and remote. Declare the `once` shared-context group using `agent-context adopt`, state
the scope in its AGENTS.md, and make CLAUDE.md contain `@AGENTS.md`.
Keep topic folders as ordinary directories; their shared configuration lives in dotfiles.
Apply the global privacy rules.

## Where finished work belongs

When a project finishes, suggest moving it to the durable home that fits its output.
Preserve its repository and history; do not copy private material into a public repo.

| Folder in ~/best/ | Contents and suitable finished work |
|---|---|
| `tools/active/` | Tools under active development. |
| `tools/stable/` | Working tools that need occasional maintenance. |
| `wiki/` | Reusable explanations, reference material and settled research. |
| `me/admin/` | Personal administration, paperwork, travel and related projects. |
| `me/health/` | Physical and mental health, food and environment research. |
| `me/sites/` | Personal blog and website. |
| `me/stuff/` | Purchases, equipment and ownership notes. |
| `people/` | People to learn from, meet and know. |
| `calls/` | Private call transcripts, notes and related work. |
| `work/80k/` | Private employer work and its tools. |
| `work/aim/` | Aim engagements and related work. |
| `strategy/` | AI-enablement strategy and planning; preserve its privacy. |
| `dotfiles/` | Shared instructions, installed skills and machine configuration. |
| `dotfiles/skill-drafts/` | The separate private repository for skills in development. |
| `archive/` | Retired substantial work and workspace history without a better home. |

Each project topic folder also has `archive/` for unfinished, thin or parked projects.
This is an explicit exception to the shared archive rule. Keep substantial research
and working artifacts visible even if future improvements remain. Record each move,
its former path and the reason in that local archive's REPLICATE.md. Restore a project
to the topic folder when work resumes. Do not create a Git repository for the archive.
