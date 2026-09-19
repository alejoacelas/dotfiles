---
agent_context:
  version: 1
  groups:
  - tools
  visibility: public
---
<!-- agent-context:begin sha256=1291866189f269b15cc8e9788ea267003e00712aebd50c20837f6e35d5d2bf71 -->
<!-- shared group: tools -->
# Maintained tools

Build for repeated use. Keep changes small. Commit in the project's own repository
and push after committing. Apply the global privacy rules when creating its remote.

Keep the README short, in the user's first-person voice; preserve their wording
where possible. Before building a macOS app that needs privacy permissions, read
[signing requirements](https://github.com/alejoacelas/dotfiles/blob/main/agents/workflows.md#local-macos-applications).
For human Markdown review, follow
[the Roughdraft workflow](https://github.com/alejoacelas/dotfiles/blob/main/agents/workflows.md#markdown-review).
<!-- agent-context:end -->

# Dotfiles

Read README.md for installation and ownership. Keep shared project prompts in agents/groups.
Keep employer-specific instructions in the separately cloned private source.

Preserve existing hooks when installing the session-start hook. The Codex app owns its base
config; CLI overrides stay in codex/cli.config.toml. Run the context tests before changing
bin/agent-context, and verify that generated edits never overwrite project-specific wording.
