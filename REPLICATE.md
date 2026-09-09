# REPLICATE

## Make large-run plans easy to inspect

The human wanted a short overview before large runs and a live record of what the run actually did.

- Added `run-overview`, which keeps the detailed plan authoritative while summarizing each stage with a concrete goal, linked guidance, timed steps, likely review artifacts and prerequisites.
- Limited step annotations to elapsed-time estimates and the literal `[optional]` tag, with descriptive stage titles and one sentence per bullet.
- Added a matching `RUN-LOG.md` format that checks off work, compares estimated and actual clock time, links outputs and records unexpected developments.
- Exposed the same canonical skill to Claude Code and both Codex skill registries.

Agent session unavailable · Commits b6d8bed

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

## Give each overview action its own bullet

The human wanted run overviews to stop compressing several processes into noun lists.

- Added the agreed writing rule to the shared run-overview skill, distinguishing independently reviewable actions from multiple inputs to one action.
- Preserved the existing timing and formatting rules and passed skill validation and the whitespace check.

Agent session 01a07bce-4d78-75c1-a3f9-aa21c8e26f6a · Commits dc7582b

## Finish the deferred folder reorganization

The human wanted the remaining moves finished and authorized interrupting conflicting sessions.

- Made tools and once ordinary root folders, retained active/upcoming/stable, moved Roughdraft into stable, and retired the old work and ai containers.
- Moved folder instructions into central sources and subscribed owned projects to tools or once, preserving local wording and repository privacy.
- Repaired installed command paths, campaign entrypoints, linked Git checkouts and the existing launchd check; the installer and 15 context tests pass.
- Consolidated the remaining archives, created the missing project remotes, and disabled the migration monitor. Full preservation and commit records are in the private migration folder.

Agent session 01a072fe-84d6-73f3-b37e-3bb912088c38 · Commits dotfiles: 994ec3b, f7f00f8, 6db9df9

## Remove human edit tracking

The human wanted human edit tracking removed from both Codex and Claude Code.

- Removed both installed skill links, the shared skill source, the installer entry, and global instructions invoking tracking.
- Removed session-start marked-diff capture while preserving shared-context synchronization; all 14 tests pass, including the no-tracking hook check.
- Preserved existing Orca hook changes in a separate baseline commit and archived the retired skill at `~/best/archive/human-edit-tracking`; existing history records remain intact.

Agent session 01a08168-5534-7543-9ec3-57520c0810fe · Commits 3199f7d (existing hooks), ca2b884 (tracking removal)

## Centralize API keys in 1Password

The human wanted API keys stored in 1Password and retrieved on demand into project `.env` files.

- Replaced the global SecretSpec instruction with direct `op` retrieval, reuse of local keys, explicit account and vault selection, and saving new keys to 1Password.
- Required ignored, untracked, owner-only `.env` files and README documentation of variable purposes and 1Password locations without secret values.
- Removed the README's recommendation to store credentials in Claude settings; preserved the existing model setting in a baseline commit.
- Centralized credentials in 1Password and verified exact readback, retaining local copies for existing workflows. After the personal account was connected, saved 27 personal credentials there and kept the old Fly reference working.

Agent session 01a086c8-c0fd-75a1-a1c3-77c04ab1e1f5 · Commits bba2d49 (existing model setting), 5f56fef (credential instructions)
