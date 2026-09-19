# Dotfiles

Read README.md for installation and ownership. The only approved shared group is
80k; keep its instructions in the separately cloned private source.

Preserve existing hooks when installing the session-start hook. The Codex app owns its base
config; CLI overrides stay in codex/cli.config.toml. Run the context tests before changing
bin/agent-context. Startup must not rewrite project files or inherit groups across
unregistered repository boundaries. Verify both clients with fresh sessions after hook changes.
