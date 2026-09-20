# Dotfiles decisions

## Core decisions

### Keep private work out of public configuration

- [Keep employer guidance and private skills in separate private repositories](#keep-private-sources-separate), even when their checkout sits inside dotfiles.
- [Load the 80k guidance only for explicitly selected repositories](#select-shared-guidance-explicitly); starting an agent must not rewrite project files.

### Let each tool read the right files

- [Keep the Codex app's settings separate from CLI overrides](#separate-app-and-cli-settings), and preserve unrelated hooks during installation.
- [Keep ordinary workspace folders out of Git](#version-projects-and-container-configuration-separately); version their shared configuration here and each project in its own repository.
- [Select skills separately for Claude Code and Codex](#select-skills-for-each-client), with one maintained source for shared skills.

### Make instructions worth rereading

- [Write project rules in AGENTS.md and explanations in README.md](#give-instructions-one-home); add a Claude import only after checking the installed client's need.
- [Keep current decisions rather than accumulating session reports](#record-choices-that-future-work-must-preserve), and express their meaning directly.

## Details

### Keep private sources separate

Dotfiles is public. Employer guidance and repository selections belong in
`~/.local/share/agent-context/private`; private skill sources belong in the ignored,
independently versioned `private-skills/` checkout. Moving files into a convenient
folder does not make their contents or history suitable for publication.

The [installer](bin/install.sh) accepts an absent private-skills checkout and reads
its client lists when present. Public-only installation must continue to work.
Credentials belong in 1Password and ignored, owner-only project `.env` files, never
in tracked settings. See [README](README.md#private-skills) and commits `06378da`,
`4bd4cb9`, and `5f56fef`.

### Select shared guidance explicitly

Only the 80k group remains approved. [agent-context](bin/agent-context) reads explicit
repository selections, including the main checkout's selection for linked worktrees.
A new sibling or nested repository does not acquire membership merely through its
location. Essential project rules remain in that project's own AGENTS.md.

This replaced copied instruction blocks and later removed the tools, once and wiki
groups. Restoring them would bring back maintenance the user deliberately removed.
Startup and compaction read guidance; they do not regenerate project instructions.
Claude exclusions must preserve unrelated user exclusions and restore the selected
folder's own instructions. The [context tests](tests/test_agent_context.py) cover
these boundaries. See `0a5bbdb` and `113f708`.

### Separate app and CLI settings

The Codex app owns its base `config.toml`; personal CLI overrides live in
[codex/cli.config.toml](codex/cli.config.toml) and apply through `codex --profile cli`.
Replacing the app's generated file with a tracked snapshot would undo that split
(`b4acf91`).

The installer preserves unrelated hooks and trusts only its exact Codex hook.
Claude can replace its settings symlink when saving; check the installed file before
editing the tracked source. The existing relinking hook preserves that saved copy.
See [maintenance instructions](AGENTS.md) and [installation](bin/install.sh).

### Version projects and container configuration separately

`~/best` and lifecycle/topic folders are ordinary directories. Projects and coherent
note collections have independent repositories; moves must preserve their history
and privacy. The [workspace tree](workspace/) supplies configuration through links,
so only folders with actual shared rules need an AGENTS.md. It is not a second set
of project repositories.

The installer mirrors that tree into the workspace and backs up conflicting real
files. Keep this mapping simple when adding a folder; do not restore the retired
container snapshots or a repository spanning the entire workspace. See `54fb63c`
and [move procedures](agents/workflows.md#creating-or-moving-projects).

### Select skills for each client

[claude/skills](claude/skills/) and [codex/skills](codex/skills/) explicitly select
compatible skills. Installation in one client does not establish compatibility with
the other. Installed registries remain real directories so independent installers
can add entries. [check-agent-config](bin/check-agent-config) reports unmanaged
skills separately from broken links and drift (`8aa6412`).

Edit plugin sources, then regenerate project mirrors with
[bin/sync-project-skills](bin/sync-project-skills). `summarize-call` is the sole
maintained call-summary workflow; the duplicate Granola skill was retired. Call
records stay in calls, while call-derived guides belong in writing/ai-guides.
Installing dotfiles must not modify those repositories. See `173f3fa` and `10eab14`.

### Give instructions one home

AGENTS.md holds behavior and workflow rules; README.md explains the project to a
human. Do not duplicate those rules in CLAUDE.md. Preserve distinct content such as
call indexes, and check [client compatibility requirements](AGENTS.md)
before adding an import shim. Native loading made many former shims redundant;
compatibility must follow the installed client, not an old setup recipe.

### Record choices that future work must preserve

DECISIONS.md starts with grouped, linked choices and expands only reasons and
exceptions that affect future work. Read the implementation and substantive history
before updating it. Prune superseded details; Git retains prior accounts. Do not
append test totals, session narratives or an exhaustive feature inventory.

The user chose the mistake-prevention prompt after comparing rewrites (`d76bd1f`)
and approved this filename (`a9183b9`). The [format](agents/workflows.md#decision-records)
is authoritative. The [writing instructions](agents/AGENTS.md#write-things-i-want-to-read)
likewise favor concrete actions and consequences over abstract labels that the
reader has to decipher (`34263de`).
