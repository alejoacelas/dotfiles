What's the way to engage with AI?

My machine and my AI tooling — how it's set up, and the standing work of making it do more. Everything else here is the work; this is the work *on the tools that do the work*.

The test for what belongs: it's meta. Not a thing I make, a person I know, or who I'm becoming — it's about the machine itself. My agent instructions, dotfiles, skills, hooks, the infrastructure map, the "here's a better way to run this" ideas.

## What lives here
- `infrastructure.md` — the map: how the setup actually fits together. Keep it true; when the wiring changes, change it here.
- `improvements.md` — the backlog of ways to make the setup better. The home for "make this better" ideas, so they stop scattering across the root and `later/`.
- `recurring-checkups.md` — reference for graduating the `machine-checkup` skill to a scheduled run. Deferred until on-demand proves it out; nothing scheduled yet.
- `checkups/` — dated `machine-checkup` reports, the audit trail.

## How to work here
- Understand before you change: the setup embeds decisions, so recover *why* before replacing a considered one (global's *Finish, don't ask* — inspect before you run over it).
- Edit the source of truth (`~/best/ai/dotfiles`), not the live symlink — same file, but committing from the repo keeps the fresh-Mac path working.
- Leave the reasoning behind, not just the diff.
- Config is shared with Codex (`AGENTS.md`, `codex/rules`, skills). Run `dotfiles/bin/check-agent-config` when you touch instructions or skills: it fails on dangling links (fix those) and reminds you where `CLAUDE.md`/`AGENTS.md` or Claude/Codex skills have drifted (reconcile only if you want — divergence is allowed).

## Neighbors
- `work/tools` — the private, credentialed CLI tooling this meta-work maintains; "make it better" ideas for it usually start here before landing there.
- `questions/technical/agent-cli-dive` — the empirical map of what Claude Code / Codex can actually do; the deep backing for the naive-model claims in `infrastructure.md`.
- `ai/dotfiles` — the nested source-of-truth repo this folder documents; editing there edits the live config, so keep `infrastructure.md` honest to it.

## Live questions
- Set up the first scheduled routine — the `schedule`/`loop` skills are still unused; a weekly "what drifted in dotfiles / what's stale" run could seed `improvements.md`. *(easy win)*
- Brewfile audit — `doppler` was installed-but-undeclared drift; sweep `brew leaves` for other undeclared tools. *(easy win)*
- Fresh-Mac dry run — the clone→`install.sh`→`brew bundle` path is reproducible on paper but never tested in a throwaway VM. *(gap)*
- Re-auth the Google Calendar connector via `/mcp`; it fails silently until then. *(unstarted — your action)*
