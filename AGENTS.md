# Dotfiles

Read README.md for installation and ownership. The only approved shared group is
80k; keep its instructions in the separately cloned private source.

Preserve existing hooks when installing the session-start hook. The Codex app owns its base
config; CLI overrides stay in codex/cli.config.toml. Run the context tests before changing
bin/agent-context. Startup must not rewrite project files or inherit groups across
unregistered repository boundaries. Verify both clients with fresh sessions after hook changes.

Before editing Claude settings, check that `~/.claude/settings.json` still links to
this repo; Claude can replace that link when saving settings. Neither settings file
is a credential store. Keep secrets in 1Password and ignored, owner-only `.env` files.

Create custom skills in `skills/` by default; the installer exposes them to both
Claude Code and Codex from one maintained source. Use `private-skills/skills/`
for private skills and a shared symlink for plugin-owned sources. Reserve
`claude/skills/` and `codex/skills/` for skills that require a particular client.
Run `bin/install.sh` after adding a skill. Keep installed skill
registries as real directories. `summarize-call` is the official call workflow;
do not restore the retired `granola-transcript` skill.

Edit plugin sources under `plugins/`. Name plugins for the package and skills for
their actions. Installation must not write into calls.

Update context selections explicitly when moving repositories. Keep employer
guidance in the private clone's `groups/80k.md`. Add new container instruction paths
to `agents/projects.json`'s `local_only` list and rerun installation when needed;
preserve independent Claude exclusions. The installer must trust only its own
exact Codex hook, never disable hook review.
