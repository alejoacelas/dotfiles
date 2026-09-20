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
7. When comparing options, explain how their differences affect the result I care
   about. Give defensible estimates for relevant costs, time, or performance, and say
   what would change your recommendation. Where estimates are unavailable, identify
   what to measure.

Lastly, be even more attentive to these rules in instruction files and READMEs. They'll
be read many more times than anything else in a project, so they should be simple,
unambiguous, and something we're confident in.

## Protect my work

Commit before making further changes. Report failures. Get explicit confirmation
before permanently deleting anything. Keep repositories public unless they contain
credentials, internal employer information (80,000 Hours), or others' non-public
information. Never publish secrets or private material.

Keep API keys in 1Password, including newly obtained keys. Explicitly verify the
account and vault. Retrieve keys on demand with `op` into the project's `.env`;
first ensure it is Git-ignored, untracked, and owner-only (`chmod 600`). Never print
or commit values. Document each variable's purpose and 1Password account, vault,
item and field in the README. Reuse `.env`; no SecretSpec or upfront key declarations.

For Google Docs and Drive, default to `gdoc`; start with `gdoc --help`.
Choose the personal or work identity from the project's context and instructions.
Verify and explicitly select it before every cloud write.
Use `gcloud --configuration` and `--project`, `gdoc --account`,
`gog --account`, and `FLY_80K_TOKEN` or `FLY_PERSONAL_TOKEN`. Google identities are
`alejandro.acelas-contractor@80000hours.org` and `alejoacelas@gmail.com`.

## Project conventions

Always use `AGENTS.md` for agent instructions; do not create `CLAUDE.md` files or
compatibility shims. Keep human-facing overviews in `README.md`. When migrating
existing `CLAUDE.md` files, preserve distinct content such as call indexes.

All our work lives in `~/best/`. It is a container, not a repository.
Give projects and coherent note
collections their own repositories and remotes; keep lifecycle and topic folders
as ordinary directories. Folder names use lowercase words separated by dashes.
Before creating or moving anything, read the destination's `AGENTS.md` and
[workspace procedures](/Users/alejo/best/dotfiles/agents/workflows.md#creating-or-moving-projects).

Only the `80k` shared group is currently approved. Select it explicitly for relevant
private employer repositories with `~/best/dotfiles/bin/agent-context adopt`;
do not add other shared groups without asking. Never infer membership from parent folders. The startup hook reads shared sources without changing project files.
Keep project-essential rules in its own AGENTS.md; private shared sources and
selections live in `~/.local/share/agent-context/private/`.

Use `REPLICATE.md` to record substantial sessions: what I wanted, concrete outcomes,
and roadblocks. Commit the substantive work first, then record its hash in a
metadata-only follow-up commit. Follow the
[session-record format](/Users/alejo/best/dotfiles/agents/workflows.md#session-records).

## Tools

At the start of project execution, check access to the services the work will need.
Try existing sessions, saved logins, and credentials available through the browser
or terminal. Collect any remaining steps that require my involvement and ask me
upfront, specifying the action needed. Continue independent work while waiting.

Don't use Orca to create tabs, terminals or worktrees for sub-agents unless asked.
Prefer native browser and computer-use tools over Orca control. When rendering
Markdown in Orca, read the
[Markdown rules](/Users/alejo/best/dotfiles/agents/workflows.md#orca-markdown).

Before declaring a skill unavailable, search `~/best/dotfiles/{claude,codex}/skills`
and `~/{.agents,.claude,.codex}/skills`; `codex/skills` is the explicit Codex-compatible
list and may point into `claude/skills`.
