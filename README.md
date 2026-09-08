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
AGENTS.md                repo-local instructions and subscribed shared context
CLAUDE.md                @AGENTS.md import
```

Claude Code saves settings by replacing the file, which turns the `~/.claude/settings.json`
symlink into a plain copy. `claude/hooks/relink-settings.sh` runs at every session start:
if the link is gone it copies the live file into the repo, relinks, and prints a message
telling you to commit. Don't edit `claude/settings.json` from a session without checking
`ls -l ~/.claude/settings.json` is still a link.

Both Claude and Codex read the one `agents/AGENTS.md`. The Codex app owns
`~/.codex/config.toml`; keep it free of CLI overrides. `codex/cli.config.toml` links to
`~/.codex/cli.config.toml` and loads only when Codex starts with `--profile cli`.
Both tools run `bin/agent-context` at session start. It refreshes declared shared groups
and reports conflicts.
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

## Project-only plugins

Keep public skills that should not load globally under `plugins/`. Projects that must
work in isolated or cloud checkouts carry a generated mirror.

Name each plugin for the whole package, normally with a concise noun; name its skills
for their individual actions. For example, `calls` contains `summarize-call` and
`call-wiki`.

| Public source | Project wiring |
|---|---|
| [`plugins/calls/`](plugins/calls/) | `calls/.claude/skills/{call-wiki,summarize-call}/` |

The marketplace at [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)
also makes the plugin independently installable. Edit the public source here, run
`bin/sync-project-skills`, then commit and push both repos. The dotfiles pre-commit hook
blocks source changes while the calls mirror differs. Run the mirror command explicitly
when changing those plugin sources; installation does not write into an active calls project.
Do not edit the generated mirror or put project-only skills under `claude/skills/`, which
`install.sh` exposes globally. The mirror's ignored `.env` and `.venv` link to the local
source; generated `data/` remains private to `calls`.

The root `AGENTS.md` contains project instructions; `CLAUDE.md` imports it.

## Install (or re-link) on a machine

This repo lives at `~/best/dotfiles`. `best` is an ordinary directory; do not clone
its retired mega-repository over the new workspace.

```sh
mkdir -p ~/best
git clone https://github.com/alejoacelas/dotfiles ~/best/dotfiles
brew bundle --file ~/best/dotfiles/Brewfile
~/best/dotfiles/bin/install.sh
```

The installer requires `uv` and creates an isolated Python environment with pinned PyYAML.
For employer groups, clone the private `agent-context-private` repository into
`~/.local/share/agent-context/private` using an authorized account.

The repo file *is* the live file (via symlink), so edit it here and both the repo and
the tool see the change. `install.sh` is safe to re-run — it repairs links and never
overwrites data.

## Secrets

`settings.json` is tracked and public — credentials don't belong in it. Keep anything
machine-local or secret in `~/.claude/settings.local.json`, which is never tracked. The
`hooks/pre-commit` guard (enabled by `install.sh`) blocks any commit that looks like it
contains a credential; override a false positive with `git commit --no-verify`.

## Shared project instructions

Run `bin/agent-context adopt /path/to/project --groups tools --visibility public` to
subscribe a project. Use `once` for dated one-offs, `wiki` for reference collections,
and `80k` only in private employer projects. Group order in YAML is the composition order.
Use `bin/agent-context sync /path/to/project` for a manual refresh and `check` for a
read-only freshness check. SessionStart calls the same code automatically.

Edit shared text in `agents/groups/`; edit project text outside the generated boundaries.
The checksum detects changes to generated text and refuses to overwrite them. Resolve a
conflict by preserving the local change and incorporating the intended wording into the
shared source; do not reset the checksum to discard an edit. Global instructions remain
one symlinked source and are not copied into every project.

Error logs and installer backups are under
`~/.local/state/agent-context/`. No watcher, recurring context sync, or session-end job runs.
The workspace-migration monitor is temporary and separate.

Run `~/.local/share/agent-context/venv/bin/python -m unittest discover -s tests` to verify
local-text preservation, conflicts, missing sources, moves, privacy and idempotence.

Codex requires each hook definition to be trusted. The installer uses Codex's supported
app-server configuration API to trust only the exact SessionStart command it installs;
it does not disable hook review or trust other hooks. Re-running installation is idempotent.
The CLI profile remains separate from the app's base settings. On an unsupported Codex
version, installation fails visibly; review this hook using `/hooks` after upgrading.
