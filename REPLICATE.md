# REPLICATE

## Isolate Codex CLI configuration

The human wanted the Codex app to use clean defaults while preserving personal CLI
settings behind `codex --profile cli`.

- Replaced the stale app-config snapshot with a tracked CLI profile containing the
  current model, reasoning, service-tier, review, history, feature, and plugin choices.
- Removed those explicit choices from the app-owned base config while retaining its
  generated project trust, desktop, bundled-plugin, and runtime MCP state.
- Linked the profile into `~/.codex` and verified that Codex 0.147 loads it; the
  Developer Docs MCP remained available as a built-in default without an override.

Agent session 01a05d9c-7599-7c63-9113-11721e0a764f · Commits b4acf91

## Default Google Docs work to gdoc

The human wanted the global Codex instructions to default Google Docs interactions to
the `gdoc` CLI.

- Added the `gdoc` default to the canonical global `AGENTS.md`; `~/.codex/AGENTS.md`
  receives it through its existing symlink.

Agent session unavailable · Commits 0eb16df
