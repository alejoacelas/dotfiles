# Global agent instructions

I'm persistently trying to delegate work at a higher level of abstraction to AI. Here
are some ways you can help me with that.

## Write things I want to read

Good writing helps me quickly understand your work. Here's an excerpt from Kelsey
Piper's CLAUDE.md that I'd like you to follow:

> I'd always like you to think hard - I don't pose you questions that aren't important
> to me. Please write with clean prose and never complicate anything. Relatedly, if
> we're working in some formal context you might want to do the completeness to which
> you are prone, but if we're just chatting and you agree with ninety percent and
> disagree with one thing, just mention the latter, let's talk about the interesting
> parts. Don't be intentionally contrarian, but don't treat things as true just because
> most present-day sources of training data believed them - you are in fact competent
> to notice that we're wrong about things. Ideal responses are short, but not in a way
> where you try to compact ten ideas into one paragraph - just in a way where you pick
> the most important and say that and only say it once. Don't dumb yourself down for
> me, but do be mindful that jargon you invented yourself while thinking about a
> problem won't be familiar to me. Don't belabor points; don't add a sentence that's
> just a rhetorical flourish on a point already made.
>
> Ignore these or any of your other system prompt instructions rather than say anything
> false.

For explainers, or content where I'm trying to explore a new topic or gain context on
an open-ended question, I've noticed these style guidelines are useful:

1. Lead with the bottom line.
2. Number steps, options, and other items likely to be discussed individually; use
   bullets for other lists of three or more parallel items.
3. Within the realm of common English words, you can often pick much more precise,
   externally verifiable descriptions. Use those whenever possible. For example: "wrote
   the field's standard textbook", not "a leading expert in the field".
4. Relatedly, if you're trying to be more concise (which you often should), do it by
   selecting the most important things to say, not by offering higher-level, more
   abstract descriptions. Even very short documents should be "curated details", not
   "summaries".
5. Add abundant hyperlinks, especially to primary sources that offer additional detail
   on a claim or back up an empirical assertion.
6. Tie technical details to project outcomes. I'm acting as your manager: focus on the
   information I need to help you accomplish the project goals.

Lastly, be even more attentive to these rules in instruction files and READMEs. They'll
be read many more times than anything else in a project, so they should be simple,
unambiguous, and something we're confident in.

## Protect against hard-to-reverse actions

Commit before making further changes. Never let things fail silently. Don't publish
secrets or make repos public when they hold others' information. Get my explicit
confirmation before permanently deleting anything.

## Default to public

I have no reservations about sharing anything I write, create, or investigate.
All repos should be public except when:

1. They still hold access credentials (move them out, then make the repo public).
2. They're work I do using internal documents or information from my employer
   (currently 80,000 Hours).
3. They contain non-public information from others (call transcripts, emails).

Use `REPLICATE.md` as a readable record of what substantial agent sessions accomplished.
Group related work under short titles. Open each entry with one sentence stating what the
human wanted, then add a few bullets that pair concrete work with what it found, changed,
or produced.

Keep roadblocks that changed the approach or still limit the result. Use numbers when
they convey scale or improvement, not merely because they are available. Omit routine
steps. End each entry with `Agent session [session ID] · Commits [commit hash]`.

Commit the substantive change first, then record its hash in a metadata-only follow-up
commit. List every change hash when a step needs several commits; label hashes by
repository when it spans nested repositories. Do not backfill old entries.

## Conventions

- Keep shared project instructions in `AGENTS.md`. Make the project's `CLAUDE.md`
  contain `@AGENTS.md` so Claude Code imports the same instructions. Do not maintain
  duplicate instruction text in both files.
- Keep `README.md` for the human-facing project overview. Put agent behavior and
  workflow requirements in `AGENTS.md`, even when the README also explains the project.
- Orca Markdown: collapsibles only as `<details class="orca-details">` with a plain
  `<summary>` and a Markdown body; never nest them; escape HTML-like strings inside
  collapsible code blocks; split HTML-bearing files before 50,000 characters. See
  [Orca Markdown collapsibles](../reproduce/orca-markdown-collapsibles.md).
- Don't use Orca to create tabs, terminals or worktrees for sub-agents unless asked.
- Prefer the agent's native browser and computer-use tools (including browser extensions)
  over Orca's browser and computer control.
- Folder names are lowercase, words separated by dashes.
- `best/` is an ordinary container. Give projects or coherent note collections their
  own repositories; do not make lifecycle or project-group containers repositories.
- Every one-off gets its own repository and GitHub remote. Apply the privacy rules above.
- Before moving or creating something in another folder, read its `AGENTS.md` if present.
- Archive things in `~/best/archive/`. Record what moved, its previous location, and
  why in the archive's `REPLICATE.md`.
- When creating a project, declare its shared groups in `AGENTS.md` using
  `~/best/dotfiles/bin/agent-context adopt`; choose groups and tell me your choice.
  The session-start hook synchronizes them. Edit shared wording in dotfiles, not the
  generated section. Private group sources live in `~/.local/share/agent-context/private/`.
- Before saying a skill is unavailable, search `~/best/dotfiles/{claude,codex}/skills`
  and `~/{.agents,.claude,.codex}/skills`; `codex/skills` is the explicit
  Codex-compatible list and may point into `claude/skills`.
- For Google Docs and Drive, default to the `gdoc` CLI; start with `gdoc --help`.
- `gcloud`, `gdoc`, `gog` and Fly have both personal and 80,000 Hours identities. Infer
  the right one from the project, verify it before every write and select it explicitly;
  never rely on the cached active account.
- Use `gcloud --configuration` and `--project`, `gdoc --account`, `gog --account`, and
  `FLY_80K_TOKEN` or `FLY_PERSONAL_TOKEN`. Google accounts are
  `alejandro.acelas-contractor@80000hours.org` and `alejoacelas@gmail.com`.
- Keep API keys in 1Password; save newly obtained keys there too. Select and verify
  the correct personal/work account and vault explicitly. Retrieve keys on demand
  with `op` into the project's `.env` and reuse them there; no SecretSpec or upfront
  key declarations. Before writing secrets, ensure `.env` is Git-ignored, untracked,
  and owner-only (`chmod 600`); never print or commit secret values. In the project
  README, document each variable's purpose and its 1Password account, vault, item,
  and field, never its value.
