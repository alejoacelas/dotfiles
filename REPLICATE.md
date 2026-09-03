# REPLICATE

## Merge Vercel deployment and custom-domain setup

The human wanted every Vercel deployment and its optional Namecheap domain setup handled
by one skill.

- Made `deploy-vercel` trigger for every Vercel deployment and route requests containing
  a domain into a directly linked Namecheap reference after the production alias works.
- Moved domain attachment, live-record lookup, BasicDNS edits, HTTPS checks, and the
  verifier script into the deployment skill's progressively loaded resources.
- Exposed the consolidated skill to Claude and Codex, removed both obsolete skill names,
  and preserved the old browser cache outside the discovery registries.

Agent session unavailable · Commits c188695, 55dff99, b4c9637

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

## Delegate tasks to Claude Cloud

The human wanted a very small global skill that lets Codex or Claude Code delegate a
task to Claude Cloud.

- Added one shared skill that commits and pushes the target repository, then runs
  `claude --cloud "<task>"` from an interactive terminal or PTY.
- Linked the skill into the global Claude, Codex, and universal skill registries and
  validated its metadata and cross-agent availability.

Agent session unavailable · Commits a351c7f

## Route Fly deployments by account

The human wanted a minimal skill that selects the personal or 80,000 Hours Fly account without replacing the cached login.

- Added account inference, cross-account deployment discovery, migration-preservation, and health-verification instructions.
- Declared separate personal and work Fly tokens backed by the 1Password Developer-Credentials vault through Secretspec.

Agent session 01a062e9-f966-7570-81f2-cb3923baf5c4 · Commits d270134

## Standardize shared project instructions

The human wanted new project guidance to default to `AGENTS.md` while remaining
available to Claude Code.

- Added a global convention that `AGENTS.md` is the project instruction source and
  `CLAUDE.md` imports it with `@AGENTS.md` instead of duplicating it.
- Kept human-facing overviews in README files and agent behavior in `AGENTS.md`.

Agent session 01a066be-9d3f-7272-a7fd-c9ca1c982a6e · Commits 71449f8
