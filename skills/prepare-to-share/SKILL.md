---
name: prepare-to-share
description: Prepare a repository for peers to adopt, focusing on the README and setup documentation. Use when asked to make a project public, shareable, or ready for others to reuse — "make a public version", "prepare this repo for sharing", "write a README other people can follow".
---

# Prepare a repository to share

The readers are peers: people with the same need who could use the project themselves, such as another organisation with a similar team, or someone who wants the same app. A repo written for yourself answers "how do I run this again?". A shared repo answers "what will this do for me, what will it cost, and how do I get it running?"

Improve the documentation, not the project. Change code only where a documented claim would otherwise be false, or where a personal value needs to become a setting.

## Remove what isn't yours to share

Follow the global rule: share nothing about other people, organisations or clients that they haven't approved sharing. That includes names, internal links, message threads, and examples that reveal who the project was built for. Replace your own machine-specific details (local paths, personal tools, account and project IDs, password-manager items) with what a peer would use: standard tools, settings with defaults, and where to get their own keys and what they cost. Keep your own rebuild notes in `AGENTS.md`.

Old commits keep whatever the current files no longer show. When the history contains something that can't be shared, publish a copy with fresh history, and say that you did.

## README

Choose the structure for the project. What worked for the [team agent server](https://github.com/alejoacelas/team-agent-server) was this order: one sentence on what it does for the reader, one self-explanatory example, what each audience gets, cost and effort, and only then how it works. Principles that carry over:

- Lead with value. Mechanics come after the reader knows why they'd want it.
- Order by the reader's attention: what they decide on first goes near the top, and implementation detail goes lower or into other documents.
- Pick an example that explains the project without a caption, such as a prompt, a command with its output, or a screenshot.
- Give cost and effort as numbers with dated sources. Setup times come from actual runs.
- Say what was tested, what wasn't, and what could be added, without blurring them.
- Prune history, anecdotes and exhaustive tables. Point to other documents instead.

## Setup documentation

If one prompt to the reader's agent (Claude Code, Codex, Cowork) can do the setup, give that prompt in the README and stop there. Otherwise, write setup docs:

- Write one document per audience. The person running a server and the person using it need different ones.
- Start from a minimal default. Put extras in a separate optional section, and handle concerns in one line each: "If you're concerned about X, do Y."
- Be direct. State each step and what the reader should see when it worked. Warn about screens that look like failures before the reader reaches them.
- Refer to other sections by name, because numbers shift when documents change.

## Before publishing

Check that the documents match the code, rather than trusting your memory of it. Where you can, have a fresh agent follow the setup from a clone. Search again for anything from the first section. A public repo without a license can't legally be reused, so ask which license to use. Open the published page in the user's browser.
