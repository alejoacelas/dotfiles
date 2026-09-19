# dotfiles

My machine config in one place: AI-agent instructions, shell, git, and the Homebrew
package list. The repo holds the real files; `bin/install.sh` symlinks them into the
paths each tool reads from. Inspired by [benthamite/dotfiles](https://github.com/benthamite/dotfiles).

## Layout

```
agents/AGENTS.md         agent instructions (shared)    ->  ~/.claude/CLAUDE.md  &  ~/.codex/AGENTS.md
claude/settings.json     permissions / model / theme    ->  ~/.claude/settings.json
claude/hooks/            Claude hook scripts (referenced by settings.json)
claude/skills/           Claude-compatible skills       ->  ~/.claude/skills/<skill>
plugins/                 public Claude plugins enabled by selected projects
codex/skills/            Codex-compatible skills        ->  ~/.agents/skills/<skill> & ~/.codex/skills/<skill>
codex/hooks.json         Codex lifecycle hooks           ->  ~/.codex/hooks.json
codex/rules/             Codex rules                    ->  ~/.codex/rules
codex/cli.config.toml     CLI-only settings used with `codex --profile cli`
shell/zprofile           PATH + dev environment         ->  ~/.zprofile
git/gitconfig            git identity + gh credentials  ->  ~/.gitconfig
Brewfile                 every Homebrew tap/formula/cask
bin/install.sh           creates links and installs the session-start hook
bin/sync-project-skills  updates/checks private project mirrors
hooks/pre-commit         blocks secrets and stale project-skill mirrors
AGENTS.md                repo-local instructions (shared context stays separate)
```

Claude Code saves settings by replacing the file, which turns the `~/.claude/settings.json`
symlink into a plain copy. `claude/hooks/relink-settings.sh` runs at every session start:
if the link is gone it copies the live file into the repo, relinks, and prints a message
telling you to commit. Don't edit `claude/settings.json` from a session without checking
`ls -l ~/.claude/settings.json` is still a link.

Both Claude and Codex read the one `agents/AGENTS.md`. The Codex app owns
`~/.codex/config.toml`; keep it free of CLI overrides. `codex/cli.config.toml` links to
`~/.codex/cli.config.toml` and loads only when Codex starts with `--profile cli`.
Both tools run `bin/agent-context` at startup, resume and after compaction. It reads
explicitly selected shared groups without rewriting project files.
The installer includes Orca account-specific Codex homes without changing the CLI profile.

The product directories are compatibility lists, not necessarily canonical sources.
A shared skill may live under `claude/skills` and have a relative link under
`codex/skills`; `use-slack` does this. Put a skill in both lists only after it
works in both agents. `bin/check-agent-config` reports one-sided skills and fails if a
Codex-compatible skill is absent from either Codex registry.

`~/.claude/skills`, `~/.agents/skills`, and `~/.codex/skills` remain real directories
so standard installers can add entries. `bin/install.sh` links Claude-compatible
skills into the first and Codex-compatible skills into both Codex registries. The
universal registry matters when a host such as Orca gives Codex an account-specific
home instead of `~/.codex`. For example, `orca skills install --skill orca-cli` uses
the community installer to target Claude Code, Codex, and the universal registry.
The installer also removes dangling dotfiles-owned links left by skill renames.

Draft skills live in `skill-drafts/`, a separate private repository ignored by this repo.

## Project-only plugins

Keep public skills that should not load globally under `plugins/`. Projects that must
work in isolated or cloud checkouts carry a generated mirror.

Name each plugin for the whole package, normally with a concise noun; name its skills
for their individual actions. For example, `calls` contains `summarize-call` and
`call-wiki`.

| Public source | Project wiring |
|---|---|
| [`plugins/calls/`](plugins/calls/) | `calls/.claude/skills/` and `writing/ai-guides/.claude/skills/{call-wiki,wiki-comments}/` |

The marketplace at [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)
also makes the plugin independently installable. Edit the public source here, run
`bin/sync-project-skills`, then commit and push the affected repos. The dotfiles pre-commit hook
blocks source changes while a calls or ai-guides mirror differs. Run the mirror command explicitly
when changing those plugin sources; installation does not write into an active calls project.
Do not edit the generated mirror or put project-only skills under `claude/skills/`, which
`install.sh` exposes globally. The mirror's ignored `.env` and `.venv` link to the local
source; generated `data/` remains private to `calls`.

The root `AGENTS.md` contains project instructions. Claude Code 2.1.277+ reads it
natively when no project or ancestor Claude instruction file suppresses fallback.
See [Anthropic’s loading rules](https://code.claude.com/docs/en/memory#agents-md);
older versions and sessions without the built-in feature need an import shim.
The global `~/.claude/CLAUDE.md` remains the user-level instruction entrypoint.

## Install (or re-link) on a machine

This repo lives at `~/best/dotfiles`. `best` is an ordinary directory; do not clone
its retired mega-repository over the new workspace.

```sh
mkdir -p ~/best
git clone https://github.com/alejoacelas/dotfiles ~/best/dotfiles
brew bundle --file ~/best/dotfiles/Brewfile
~/best/dotfiles/bin/install.sh
```

The installer requires `uv` and creates an isolated Python environment; the hook uses
only the standard library.
For employer groups, clone the private `agent-context-private` repository into
`~/.local/share/agent-context/private` using an authorized account.

The repo file *is* the live file (via symlink), so edit it here and both the repo and
the tool see the change. `install.sh` is safe to re-run — it repairs links and never
overwrites data.

## Secrets

I keep API keys in 1Password and retrieve them on demand into each project's ignored,
owner-only `.env`. Project READMEs list variable names, purposes, and 1Password
locations without values. Neither `settings.json` nor `settings.local.json` is a
credential store; `settings.json` is tracked and public. The
`hooks/pre-commit` guard (enabled by `install.sh`) blocks any commit that looks like it
contains a credential; override a false positive with `git commit --no-verify`.

## Shared project instructions

Codex loads project instructions from the local Git root down to its starting directory.
Outside a repository it checks only that directory; GitHub hosting is not required.
Container instructions therefore do not automatically reach independent child repos.
Select shared groups explicitly for each repository. Neither parent folders nor a
new sibling repository grant membership. Essential build, privacy and behavior rules
belong in the project's own AGENTS.md so they also travel with standalone clones.
See [Codex discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Run `bin/agent-context adopt /path/to/project --groups tools --visibility public` to
register a choice. Use `--visibility private` for private repositories, and an empty
`--groups` to remove a selection. Public selections live in `agents/projects.json`;
private selections live in `~/.local/share/agent-context/private/projects.json`.
Update entries explicitly when moving a project. Linked Git worktrees reuse the
main checkout's selection. Unregistered nested repos, archives, fixtures and vendored
trees receive no shared groups.

The four short sources are `tools` (maintained software), `once` (one-off projects),
`wiki` (reference collections), and private `80k` (employer work). They contain curated
rules rather than whole parent instruction files. Edit public text in `agents/groups/`
and private text in the private clone's `groups/`. There are no generated copies,
YAML subscriptions, synchronization command or project-file writes at startup.
`bin/agent-context check /path/to/project` shows the selected context without writing.

Claude normally reads ancestor AGENTS.md files. The registry's explicit `local_only`
list identifies container files that must not leak into independent children. The
installer excludes their exact paths (and symlink targets) through `claudeMdExcludes`;
the Claude hook restores them only in their own directory or Git repository. Add a
new container to this list and rerun `install` when needed. Project-local and nested
instruction discovery otherwise stays native. Existing independent exclusions are
preserved. See [Claude loading rules](https://code.claude.com/docs/en/memory#agents-md).

Both clients use `SessionStart`, including `source: compact`, to reread selected
sources before the next response. The hook reports missing sources and privacy
conflicts visibly; errors and installer backups are in `~/.local/state/agent-context/`.
It does not watch files or rewrite project instructions. These machine-local choices
do not accompany an unrelated cloud clone.

For sessions in `projects/` or at the `best/` root, SessionStart also flags projects
in `projects/live/` with no substantive activity for 14 days. It reports candidates;
the agent chooses a destination using `projects/AGENTS.md` before moving them.

Run `~/.local/share/agent-context/venv/bin/python -m unittest discover -s tests` to verify
explicit selection, startup/compaction output, nested-repository boundaries, private
source protection, worktrees and the absence of project-file writes.

Codex requires each hook definition to be trusted. The installer uses Codex's supported
app-server configuration API to trust only the exact SessionStart command it installs;
it does not disable hook review or trust other hooks. Re-running installation is idempotent.
The CLI profile remains separate from the app's base settings. On an unsupported Codex
version, installation fails visibly; review this hook using `/hooks` after upgrading.
