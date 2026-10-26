# Global agent instructions

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

Prefer wording that makes the meaning immediately apparent over compact, abstract
labels. Don’t make the reader unpack abstract nouns to understand what you mean.
State the underlying action, relationship, or consequence directly, even if that
takes a few more words. Keep established technical terms when they make the
explanation clearer.

Write the final output around the chosen approach. When we discuss an option and
then reject or drop it, omit it from the final output unless remembering that
decision will prevent a plausible mistake. Discussion history alone is no reason
to turn a discarded option into a prohibition or an explanation of what we won't
do. More generally, state the intended action or actual behavior directly; include
negative clarifications only when they change the reader's decision or prevent a
likely misunderstanding.

Lastly, be even more attentive to these rules in instruction files and READMEs. They'll
be read many more times than anything else in a project, so they should be simple,
unambiguous, and something we're confident in.

## Protect my work

Commit before making further changes. Push after every commit.
Get explicit confirmation before permanently
deleting anything. Keep repositories public unless they contain credentials,
employer or client information, or others' non-public information.

Keep API keys in 1Password and load them on demand with `op` into the project's
ignored `.env`. Record in `AGENTS.md` where each variable lives in 1Password
(account, vault, item, field) so the file can be rebuilt.

For personal credentials approved for agent access, use
`~/best/dotfiles/bin/op-agent` on the Mac (`~/.local/bin/op-agent` on the server).
It authenticates without prompts to `mac-agents` or `server-agents` in the
personal 1Password account. Use `op-agent run` with secret references to inject
credentials into a command, or `op-agent inject` for an ignored `.env`.
Authenticate for authorized tasks without asking again; never print, commit,
or disclose secret values. Existing action-specific approval rules still apply.
Use ordinary `op --account my.1password.com` for items outside these vaults.

On the agent server, run agent work as the `agent` user (`sudo -iu agent`). It
has no sudo or `op-agent`; `gh`, `gog` and git pushes go through a credential
broker that never returns the tokens. To give it an API key, add a broker
route ([agent user setup](/Users/alejo/best/projects/2026-09-26-agent-server/docs/setup.md#agent-user)).

I have a personal Google identity (`alejoacelas@gmail.com`) and an Impact Ops one
(`alejo@impact-ops.org`). `gcloud` and Fly (`FLY_PERSONAL_TOKEN`) use the personal
identity. Pick the identity from the project's context and pass it explicitly on every
cloud write. Use `gog --account <email>` for Google Docs and Drive; it is signed in to
both identities and to `alejo@habere.org`.

To replace a whole Google Docs tab, write the new content into a new tab, compare it
with the original, carrying over any edits made there since your last write, then
delete the original. Writing over an existing tab can keep its old formatting, such
as turning every paragraph into a bullet.

## Project conventions

Put agent instructions in `AGENTS.md` and human-facing overviews in `README.md`.

All our work lives in `~/best/`, a plain folder of independent repositories. Give
projects and coherent note collections their own repositories and remotes; keep
lifecycle and topic folders as ordinary directories. Folder names use lowercase
words separated by dashes. Before creating or moving anything, read the
destination's `AGENTS.md` and the
[workspace procedures](/Users/alejo/best/dotfiles/agents/workflows.md#creating-or-moving-projects).

Keep `DECISIONS.md` as a concise record of current decisions that future work
should not accidentally undo. Put grouped core decisions first, with linked reasons
and consequential exceptions below.

When we make or change a decision worth preserving, add a dated entry to a log at
the bottom. Record only the decision and enough context to explain why; skip session
progress and routine implementation details.

When you notice substantial changes accumulating, rewrite the document to reflect
the current decisions and fold in the log. Remove superseded decisions, merge
overlapping explanations, and clear entries whose useful content is now incorporated.
Preserve relevant reasons and exceptions; rely on Git for history.

Prefer updating an existing explanation over adding another. The document should
grow only when there are more distinct decisions or necessary reasons to preserve.
Follow the
[decision-record format](/Users/alejo/best/dotfiles/agents/workflows.md#decision-records).

## Model APIs

For application and script model calls, use Anthropic directly: `claude-opus-5-5`
by default, or `claude-haiku-5-5` for fast turnaround or jobs with more than 20
parallel model calls. Personal projects should use the Claude Console organization
linked to the personal plan's monthly API credits. Keep client billing
separate. Preserve specialized capabilities and project privacy requirements when
choosing a replacement.

## Tools

When opening any Claude Code or Codex session, use
`claude --dangerously-skip-permissions` or
`codex --dangerously-bypass-approvals-and-sandbox`, unless I explicitly request
restricted permissions.

The two Macs SSH into each other and into the agent server over Tailscale:
`ssh mac-air-2` (the other MacBook Air), `ssh alejo-m4` (the main Mac) and
`ssh agent-server`.
SSH sessions on a Mac can't read the keychain, so start Claude there inside
`tmux` with `CLAUDE_CODE_OAUTH_TOKEN` injected by `op-agent run` from
`op://mac-agents/6drosdmzu2qb3jefhsh3d5b7dy/credential`.

At the start of project execution, check access to the services the work will need.
Try existing sessions, saved logins, and credentials available through the browser
or terminal. Collect any remaining steps that require my involvement and ask me
upfront, specifying the action needed. Continue independent work while waiting.

When rendering Markdown in Orca, read the
[Markdown rules](/Users/alejo/best/dotfiles/agents/workflows.md#orca-markdown).

Create custom skills in `~/best/dotfiles/skills/` so Claude Code and Codex share one
source, or in the private `~/best/dotfiles/private-skills/` checkout, then run
dotfiles' `bin/install.sh`. The [dotfiles README](/Users/alejo/best/dotfiles/README.md)
covers client-specific exceptions and install locations.
