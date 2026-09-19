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

## Retire the Vercel skill

The human wanted the custom Vercel deployment skill removed and the remaining personal skills inventoried.

- Archived the source from `~/best/dotfiles/claude/skills/deploy-vercel` at `~/best/archive/2026-09-deploy-vercel-skill/deploy-vercel` so it remains recoverable.
- Removed the compatibility entry and three active installation links; future dotfiles installs will no longer install it.
- Found separate Granola skill copies with different filing instructions; other skills were left unchanged.

Agent session 01a0b651-6484-7a93-9a8f-a5f49c31162a · Commits dotfiles: ebd0476

## Retire unused custom skills

The human wanted five custom skills removed, any Fly custom-domain component retained, and run-overview’s scope discussed.

- Archived `my-vm`, `deploy-fly`, `delegate-claude-cloud`, `sync-drive`, and `machine-checkup` from dotfiles skill directories and active registries under `~/best/archive/2026-09-retired-agent-skills/`; `LOCATIONS.md` records each original location.
- Fly had no custom-domain component to preserve and still referenced the superseded SecretSpec workflow.
- Left `run-overview` unchanged pending discussion of its broad automatic trigger.

Agent session 01a0b651-6484-7a93-9a8f-a5f49c31162a · Commits dotfiles: 9d5b892

## Narrow run overview scope

The human wanted run-overview to trigger less often and let the model decide when timing is useful.

- Limited automatic use to projects spanning multiple work sessions with several independently reviewable deliverables; explicit requests still trigger it.
- Made estimates and actual-time tracking independently optional, with guidance to use them only when useful and supported by evidence.
- Updated the default log example to omit timing; the shared source updates both Claude and Codex through existing links.

Agent session 01a0b651-6484-7a93-9a8f-a5f49c31162a · Commits dotfiles: 9492beb

## Work, projects and draft skills

Alejo wanted employer work grouped under work, one-offs consolidated into projects, and draft skills nested under dotfiles.

- Moved aim and 80k beneath work, renamed once to projects, and moved nine repositories from other into dated project folders. Preserved their Git histories and existing changes.
- Moved the separate private skills repository to ignored skill-drafts; updated global instructions, workspace indexes and installer destinations. Kept the existing once context-group ID for compatibility.
- Repaired affected symlinks and a Git worktree; verified all 71 moved repository heads and working-tree states before the archive-link documentation correction. Shell syntax and diff checks passed.
- Proposed five topic groups of 11–12 projects, including archived candidates; the full proposal and move manifest live in the private context repository. Retained old other container notes in the shared archive.

Agent session 01a0b905-404c-7231-916c-024f887eb815 · Commits dotfiles: 621edd5 (pre-existing configuration checkpoint), 971fe1e; 80k: 75d2401d; agent-context-private: f8f8efe (pre-existing archive checkpoint), 7c6d764

## Simplify the personal workspace

The human wanted to remove unstarted personal projects and simplify the remaining folders.

- Deleted the local placeholder repositories at `me/past` and `me/relationships` as explicitly requested. Moved writing and style into wiki, merged body and mind into health, and grouped blog and website under `me/sites`; updated container indexes. Existing GitHub repositories were not deleted or renamed.

Agent session 01a0b90b-7ae3-7ed1-bb2f-fde3ad5d78d3 · Commits me/health: 122d3c3, wiki/style: 7ed0f68, wiki/peter-hartree-ai-journal: 27824a8, wiki: 22e3c6a, dotfiles: 5ceaed4, health merge: 14f68bb

## Topic groups, local archives and writing

Alejo wanted project topic folders, personal administration under me, upcoming tools sorted into projects, local archives for unfinished work, and wiki renamed to writing.

- Applied the proposed topic groups as agent-workflows, connectors, research-evaluations and ai-community; added others. Moved personal projects into me/admin and six upcoming-tool repositories into the relevant topics.
- Parked six unfinished proposals or handoffs in topic-local archives and recorded the reasons in private archive logs. Updated global and project instructions to permit these archives and map durable homes for finished work.
- Renamed wiki to writing and moved five standalone essay/reference collections there as ignored independent repositories. Updated workspace indexes and installer paths; preserved the wiki shared-context group ID.
- Verified all 30 project repository states through the moves, repaired email/Slack sibling links, checked affected symlinks and shell syntax, and confirmed that private nested repositories remain untracked by their public parent. Exact moves and classifications live in the private context repository.

Agent session 01a0b905-404c-7231-916c-024f887eb815 · Commits dotfiles: e8847b4, a299e1e; writing: 63a54e5; agent-context-private: 59d7a34, 8752c3c; email: 4c6692a; slack: 71f220f

## Personal homes and work strategy

Alejo wanted meals and relationship projects out of admin, strategy under work, and a proposal for tidying calls.

- Moved meals to me/health/meals; moved advice, love and Mutual Yes to me/relationships. Admin now contains four paperwork/travel projects. Updated indexes and kept meals ignored by its parent repository.
- Moved strategy to work/strategy, retaining its private repository and correcting call-reference links. All five moved repositories preserved their history and existing state.
- Inspected calls without changing it: 67 article files, nine Slack-derived drafts, a publishing pipeline and video-blur tooling. Recommended a private writing collection for articles/drafts/site, with coordinated path updates because publishing and call skills depend on the current layout.

Agent session 01a0b905-404c-7231-916c-024f887eb815 · Commits dotfiles: 2a008f7; health: 606d2e2; strategy: 30aa1fd; agent-context-private: 6455bd2

## Simplify project topics

The human wanted shorter topic names and research evaluations grouped under others.

- Renamed `projects/agent-workflows/` to `projects/agents/` and `projects/ai-community/` to `projects/community/`.
- Dissolved `projects/research-evaluations/` into `projects/others/`, preserving the archived project and its archive record.
- Updated topic instructions, indexes and symlinks; verified the moved repositories retain their original HEAD commits.

Agent session 01a0b90b-7ae3-7ed1-bb2f-fde3ad5d78d3 · Commits dotfiles: 52620a4; agent-context-private: 9aabadb

## Agent instructions cleanup — 2026-09-19

Alejo asked to refresh project instructions and remove redundant Claude instruction files where native AGENTS.md loading is available.

- Updated the applicable instructions and removed redundant local Claude copies; distinct content and preserved snapshots remain.
- Checked instruction references and shared-context freshness; native Claude loading requires 2.1.277+ with the built-in feature enabled.

Agent session 01a0b915-3eb2-78b2-9add-6ba48ad9a3b1 · Commits cb25805c2c343a18f532d98ef054f9c6d5e3c485, c70f47ba8f4fd13757134cdfa09c2fc585920ffd

## Keep project navigation current

The human wanted the grouping proposal removed, the folder map treated as a snapshot, and the Matt Pocock trial parked.

- Deleted the proposal and its index links; instructed agents to check actual folders and repair inconsistent maps and indexes.
- Moved `projects/agents/2026-08-mattpocock-skills` to `projects/agents/archive/2026-08-mattpocock-skills`, preserving its private repository.

Agent session 01a0b90b-7ae3-7ed1-bb2f-fde3ad5d78d3 · Commits dotfiles: 6f2e88f; agent-context-private: 44905fe

## Route call-derived writing to its own repository

Alejo wanted guides and publishing separated from calls, and video-blur tooling extracted into tools.

- Updated call-wiki, wiki-comments and the optional summarize-call writing pass to use the private writing/ai-guides repository. Cross-repository links and commits now explicitly separate guides from call records.
- Extended sync-project-skills to mirror the two writing skills into ai-guides while keeping all three in calls. Added a test covering skill selection, drift detection, idempotence and private runtime-file preservation; validated all three skills and their mirrors.
- Indexed video-blur under active tools. New repositories declare wiki and tools context groups respectively. All checks passed; the publication output matched 88 pre-move files and built locally without deployment.

Agent session 01a0b905-404c-7231-916c-024f887eb815 · Commits dotfiles: cb25805 (pre-existing instruction checkpoint), 10eab14; calls: 6d01da1 (pre-existing instruction checkpoint), 1b6bd33; ai-guides: 8389b11; video-blur: 66b5f62; writing: 32198bf

## Put people beside relationship projects

Alejo wanted the empty love/advice placeholders archived and people grouped with relationships.

- Moved people to me/relationships/people as an intact repository alongside mutual-yes. Kept admire, discover and places together; updated workspace indexes and installation so the old top-level people folder will not return.
- Archived the two placeholder repositories in the shared archive, preserving their history and separate privacy settings. Repaired calls-to-people and people-to-workspace links; shell syntax and local-link checks passed.

Agent session 01a0b905-404c-7231-916c-024f887eb815 · Commits dotfiles: b1291b2; people: d2d72f9; calls: 6c6f480; agent-context-private: 2e62f46

## Archive Mutual Yes under community

Alejo wanted Mutual Yes moved out of relationships into the community archive.

- Moved the intact repository to projects/community/archive/2026-09-mutual-yes and removed it from the relationships index. Recorded its former location and reason in the destination archive.

Agent session 01a0b905-404c-7231-916c-024f887eb815 · Commits 9a8ffc7

## Flag inactive live projects

The human wanted a live project folder and a startup reminder for projects untouched for two weeks.

- Added `projects/live/`, the 14-day relocation rule, and a read-only reminder in the existing SessionStart hook for projects sessions and the workspace root. Uses substantive Git history plus uncommitted file timestamps, excluding bookkeeping and ignored artifacts. All 16 tests pass, including scope, staging, ignored activity and the exact deadline.

Agent session 01a0b90b-7ae3-7ed1-bb2f-fde3ad5d78d3 · Commits dotfiles: 82ab903

## Prefer local archives for unlikely revisits

Alejo wanted projects unlikely to be revisited kept in their topic archive rather than relocated elsewhere.

- Updated projects/AGENTS.md to prefer projects/<topic>/archive/ and reserve durable-home suggestions for outputs likely to be used or maintained. Removed the conflicting instruction to keep substantial artifacts visible regardless of expected use.

Agent session 01a0b905-404c-7231-916c-024f887eb815 · Commits 4df5189

## Shorten standing agent instructions

Alejo wanted the global instructions, shared groups and article reviewer simplified, then a review of what tools/AGENTS.md should contain.

- Reduced global instructions from 1,186 to 391 words and moved occasional procedures to a linked guide, preserving identity, privacy and secret-handling rules.
- Reduced tools and one-off groups to 63 and 51 words; refreshed this repository's generated block. Other subscribers receive source changes through session-start sync.
- Checked local links, section anchors, generated-context freshness and whitespace. Left the tools container instructions unchanged for discussion.

Agent session 01a0b921-9a6a-76c1-9000-c63b1c0cb909 · Commits dotfiles: d4f25b2; agent-context-private: 2dffb3b; web-article-reviewer: 1be9638

## Explicit shared instructions at startup

Alejo wanted selective shared context at startup and after compaction, without automatic parent inheritance or copied instructions.

- Replaced project YAML/generated blocks with explicit public/private registries; startup only reads selected short sources. Migrated 57 live instruction files, reducing their combined length from 2,038 to 515 lines.
- Selected 41 repositories deliberately. New siblings and nested repositories do not inherit membership; archived and fixture files remain unchanged. Private memberships stay in the private context repository.
- Configured Claude ancestor exclusions with local-scope restoration, preserving native project instructions. Fixed exclusion ownership and first-install symlink ordering after independent review.
- Passed 17 automated tests, fresh Codex/Claude startup probes, and an actual Codex manual compaction/continuation check. Claude and automatic token-triggered compaction were not exercised end-to-end.
- Full selections, cross-repository hashes and sanitized startup evidence are in the private context repository under migration/2026-09-19-explicit-context/.

Agent session 01a0b915-3eb2-78b2-9add-6ba48ad9a3b1 · Commits dotfiles 0a5bbdb

## Keep only employer shared context

Alejo reviewed the shared sources and wanted only the 80k case retained.

- Removed tools, once and wiki subscriptions and retired their public source files; nine explicitly selected employer repositories retain 80k guidance. Local project instructions and container exclusions remain in place.
- Updated live instructions so agents do not recreate the retired groups. All 17 context tests pass.

Agent session 01a0b915-3eb2-78b2-9add-6ba48ad9a3b1 · Commits 113f708

## Remove personal hook overhead

Alejo wanted guarded-file checks, automatic review reminders and people-sync removed, and the banner silencer simplified.

- Removed all five registrations and their six supporting files: guarded-file protection, two review reminders, people-sync, and the cache-patching silencer.
- Retired the silencer instead of maintaining plugin patches; restored three cached plugin scripts with backups. Routine banners and setup warnings can now appear normally.
- Verified unrelated settings and hooks were preserved exactly, JSON remains valid, and restored shell scripts pass syntax checks.

Agent session 01a0b915-3eb2-78b2-9add-6ba48ad9a3b1 · Commits 7fcaef4

## Keep the writing experiment registration private

Alejo wanted an employer technical recommendation included in the blind writing experiment.

- Moved the experiment's context registration out of the public registry when its source material required a private repository.

Agent session 01a0b921-9a6a-76c1-9000-c63b1c0cb909 · Commits dotfiles 6c350de; agent-context-private b1a6801

## Restore the original writing guidance

Alejo preferred the old writing instructions in blind comparisons and wanted the writing-relevant parts restored.

- Restored the original writing section, including the Piper excerpt, examples of concrete details, hyperlinks and guidance for instruction files. Kept the current workflow, privacy and shared-context sections intact.
- Verified the Claude, Codex and active Orca account instruction entrypoints all resolve to this file. The separate writing experiment continues to use frozen old/new snapshots, so this live change does not contaminate its comparisons.

Agent session 01a0b921-9a6a-76c1-9000-c63b1c0cb909 · Commits e4971cf
