# REPLICATE

## Finish the ready 80k migration batch

The human wanted deferred workspace moves completed only after their live sessions closed.

- Flattened the private 80k lifecycle folders and moved 14 inactive units into the shared archive with preserved Git history.
- Created 11 missing private remotes, retained three existing archive remotes, and repaired project paths and instruction imports.
- Verified 206,844 inventoried entries, 20 Git repositories, remote parity, symlinks and process working directories; no work was missing or unexpectedly changed.
- Left `tools` and `once` pending because live sessions still use them. The temporary automation remains enabled until that list is empty.

Agent session 01a07b94-25c7-7301-b3b3-fbf948e76581 · Commits 80k: 4fd52e3, 8a04923, 50a6034; agent-context-private: 711c35b, 267a3a8; archived and nested repositories: `~/.local/share/agent-context/private/migration/COMMITS.md`

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

## Ordinary folders and session-start context

The human wanted a smaller folder and shared-instruction system, preserving handwriting and leaving active sessions alone.

- Made best an ordinary container; moved dotfiles to its root, writing sites into me, reference material into wiki, and the requested collections into others. One-offs receive individual repositories and remotes.
- Consolidated safe-to-move retired work under best/archive. Preserved original Git history in private local recovery storage; active tools, once, 80k and calls migrations are deferred to a temporary Orca monitor.
- Installed one context script on SessionStart for Claude and both Codex configurations. Ordered YAML groups refresh automatically; edited generated text blocks overwrites, and local project wording stays editable.
- Moved global handwritten-edit history verbatim out of routinely loaded instructions. Added separate marked-edit evidence and explicit destination-instruction reading.
- Passed 15 tests, full installation and fresh-context probes through both Codex configurations, Claude and the Codex app-server protocol. Desktop UI clicks were not tested.

Project-specific commits are recorded in their REPLICATE files. The complete migration ledger is in ~/.local/share/agent-context/private/migration/COMMITS.md.

Agent session 01a072fe-84d6-73f3-b37e-3bb912088c38 · Commits dotfiles: 1a4a26b, cd85a78, f64a22e, b44c5f1
