---
name: build-walkthrough
description: Write a shareable walkthrough of how the user built an AI setup (an app, skill, tool, automation or workflow), quoting their own prompts from session history, so a colleague can build their own version. Use when the user asks for a walkthrough, write-up, guide or "how I built it" document for something they made with AI.
---

# Build walkthrough

Turn the history of something the user built with AI into a document a colleague can
follow to build their own version. The user names the setup; if they haven't, ask
which one.

## 1. Find its history

Search every place the work may have happened, not only the setup's own folder:
work on one project often ran in sessions started elsewhere.

- Claude Code transcripts in `~/.claude/projects/*/` (JSONL; search for the setup's
  name, files and paths). Prompts typed while Claude was working can appear as
  queued commands rather than plain user messages.
- Codex sessions in `~/.codex/sessions/`.
- The setup's files and their version history, and its issues if it has a remote.
- Past claude.ai chats, if a past-chat search tool is available.

If one short question would make finding the right material much more likely, ask
it in at most three lines and stop. Otherwise go straight on.

## 2. Write the walkthrough

- Title it with a name that tells a reader what the thing is, and say it's about
  building it with AI.
- Open with a sentence or two a reader can take in at a glance: what it is and what
  it does for them, even at the cost of detail. Then say in one sentence what the
  document contains, and add fuller detail only if it's needed. Link to its current
  instructions or files if they're shareable.
- If the result is something people can see, show an image of it right after the
  opening.
- Next, give a starter prompt a reader can paste to build a first version in one go,
  labelled as written for the walkthrough rather than taken from the user's history.
- Then walk through the stages in the order the setup grew: the first version that
  worked, then each change that stuck. Leave out dead ends, unless knowing about one
  would stop a reader from making the same mistake.
- At each decision point, quote the prompts the user actually typed, word for word,
  with cuts marked "…" and typos kept. Never invent or reconstruct a prompt, and
  don't present prompts an agent wrote as the user's. Make the quotes easy to tell
  apart from the surrounding text, without loud styling.
- Around the quotes, write declaratively and only what the quotes don't already say:
  why a change was made, how it connects to earlier stages, and what it does. If the
  history doesn't show why something changed, don't guess; leave the reason out and
  list it at the end.
- End each stage with what the reader has working at that point.
- Write for colleagues who use AI but may have different tools or less technical
  comfort than the user. Where a stage depends on something they may not have, say
  so and give the closest way to do it with what they're likely to have.
- Keep it as short as covering every stage allows.

## 3. Keep private things out

Replace other people's names with [name] in quotes and text, leave out the contents
of calls, messages or documents beyond what's needed to explain a stage, and leave
out passwords, keys and other credentials.

## 4. Publish and check

Put the walkthrough in a document the user can share, a Google Doc by default, in
the account that matches the setup's context. Then open the final document and check
that it reads as intended, fixing anything that didn't survive the move.

## 5. Report

Give the link, and list any facts you couldn't pin down, such as reasons for a
change or whether a step works in tools you couldn't test.
