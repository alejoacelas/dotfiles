# Global agent instructions

## Communication

Lead with the answer. Select important details rather than compressing everything.
Use plain, precise language and primary-source links. Disagree when warranted.
Report outcomes, evidence, and limitations relevant to my decisions. Number items
we may discuss individually. Keep instruction files simple and unambiguous.

## Protect my work

Commit before making further changes. Report failures. Get explicit confirmation
before permanently deleting anything. Keep repositories public unless they contain
credentials, internal employer information (80,000 Hours), or others' non-public
information. Never publish secrets or private material.

Keep API keys in 1Password, including newly obtained keys. Explicitly verify the
account and vault. Retrieve keys on demand with `op` into the project's `.env`;
first ensure it is Git-ignored, untracked, and owner-only (`chmod 600`). Never print
or commit values. Document each variable's purpose and 1Password account, vault,
item and field in the README. Reuse `.env`; no SecretSpec or upfront key declarations.

For Google Docs and Drive, default to `gdoc`; start with `gdoc --help`.
Before every cloud write, verify and explicitly select the identity; never rely on
cached defaults. Use `gcloud --configuration` and `--project`, `gdoc --account`,
`gog --account`, and `FLY_80K_TOKEN` or `FLY_PERSONAL_TOKEN`. Google identities are
`alejandro.acelas-contractor@80000hours.org` and `alejoacelas@gmail.com`.

## Project conventions

Keep behavior and workflow instructions in `AGENTS.md`, human-facing overviews in
`README.md`. Do not duplicate instructions in `CLAUDE.md`; preserve distinct content
such as call indexes. Before adding an import shim, verify the need using the
[compatibility notes](/Users/alejo/best/dotfiles/agents/workflows.md#claude-instruction-compatibility).

`~/best/` is a container, not a repository. Give projects and coherent note
collections their own repositories and remotes; keep lifecycle and topic folders
as ordinary directories. Folder names use lowercase words separated by dashes.
Before creating or moving anything, read the destination's `AGENTS.md` and
[workspace procedures](/Users/alejo/best/dotfiles/agents/workflows.md#creating-or-moving-projects).

Only the `80k` shared group is currently approved. Select it explicitly for relevant
private employer repositories with `~/best/dotfiles/bin/agent-context adopt`;
do not add other shared groups without asking. Never infer membership from parent folders. The startup hook reads shared sources without changing project files.
Keep project-essential rules in its own AGENTS.md; private shared sources and
selections live in `~/.local/share/agent-context/private/`.

Use `REPLICATE.md` to record substantial sessions: what I wanted, concrete outcomes,
and roadblocks. Commit the substantive work first, then record its hash in a
metadata-only follow-up commit. Follow the
[session-record format](/Users/alejo/best/dotfiles/agents/workflows.md#session-records).

## Tools

Don't use Orca to create tabs, terminals or worktrees for sub-agents unless asked.
Prefer native browser and computer-use tools over Orca control. When rendering
Markdown in Orca, read the
[Markdown rules](/Users/alejo/best/dotfiles/agents/workflows.md#orca-markdown).

Before declaring a skill unavailable, search `~/best/dotfiles/{claude,codex}/skills`
and `~/{.agents,.claude,.codex}/skills`; `codex/skills` is the explicit Codex-compatible
list and may point into `claude/skills`.
