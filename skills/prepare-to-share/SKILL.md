---
name: prepare-to-share
description: Prepare a repository for peers to adopt, focusing on the README and setup documentation. Use when asked to make a project public, shareable, or ready for others to reuse — "make a public version", "prepare this repo for sharing", "write a README other people can follow".
---

# Prepare a repository to share

The readers are peers: people with the same need who could use the project themselves, such as another organisation with a similar team, or someone who wants the same app. A repo written for yourself answers "how do I run this again?". A shared repo answers "what will this do for me, what will it cost, and how do I get it running?"

Improve the documentation, not the project. Change code only where a documented claim would otherwise be false, or where a personal value needs to become a setting.

## Know your readers

Match the readers to the [audience profiles](audiences/README.md). Each profile lists what that kind of reader already knows, so documents can skip it, and what needs explaining. Write only what falls outside what they know. When feedback shows a profile is wrong, update the profile as well as the document.

If the user names specific receivers, check what has already passed between you and them: their original request, messages and threads, document comments, and call notes. Keep a gitignored `receivers.local.md` at the repository root, with one section per person:

- Their audience profile.
- What they asked for, with a link.
- What they have been told or shown, with the date and a link.
- Decisions they made, and questions still open.

Record only exchanges you can point to, so later documents can rely on them: skip what they already know, and answer what they asked. Update the record after each new exchange.

## Remove what isn't yours to share

Follow the global rule: share nothing about other people, organisations or clients that they haven't approved sharing. That includes names, internal links, message threads, and examples that reveal who the project was built for. Replace your own machine-specific details (local paths, personal tools, account and project IDs, password-manager items) with what a peer would use: standard tools, settings with defaults, and where to get their own keys and what they cost.

Peers will often point their own agents at the repo, and those agents read `AGENTS.md`. Write it for any agent working on the project. Put your own rebuild notes, such as where secrets live, in a "Maintainer notes" section at the end.

Old commits keep whatever the current files no longer show. When the history contains something that can't be shared, publish a copy with fresh history, and say that you did.

## Write so every sentence earns its place

These documents get read more than anything else in the project, so spend the effort. Draft, then cut.

- Make each sentence say something the reader needs. Drop any sentence that only restates the one before it or explains what the reader already knows.
- Assume the reader is competent and knows their tools, as described in their audience profile. Explain what's specific to this project, not the basics.
- Lead with the value, and give each audience what it needs first. The first screen should answer "why would I want this?"; mechanics come after.
- Be direct and unambiguous. State each decision briefly with its reason. Write instructions as "If X, do Y", and state limits as explicit rules.
- Replace vague phrases with concrete ones. If a reviewer could ask "what does this mean?", say the underlying fact instead.
- Merge items that describe one idea, and remove steps readers don't need to take.
- Show capabilities with concrete examples. Good example prompts state the central idea and leave the method to the agent; some can end with "Ask me questions to clarify."
- Link to primary sources and to the exact pages readers will need.

## README

Choose the structure for the project. What worked for the [team agent server](https://github.com/alejoacelas/team-agent-server) was this order: one sentence on what it does for the reader, one self-explanatory example, what each audience gets, cost and effort, and only then how it works. Principles that carry over:

- Order sections by the reader's attention: what they decide on first goes near the top, and implementation detail goes lower or into other documents.
- Pick an example that explains the project without a caption, such as a prompt, a command with its output, or a screenshot.
- Give cost and effort as numbers with dated sources. Setup times come from actual runs.
- Say what was tested, what wasn't, and what could be added, without blurring them.
- Prune history, anecdotes and exhaustive tables. Point to other documents instead.

## Setup documentation

If one prompt to the reader's agent (Claude Code, Codex, Cowork) can do the setup, give that prompt in the README and stop there. Otherwise, write setup docs:

- Write one document per audience. The person running a server and the person using it need different ones.
- Separate the overview from the steps. The overview says what the thing is, the decisions to make or approve, and their consequences. The steps say how to proceed once those decisions are made.
- Start from a minimal default. Put extras in a separate optional section, and handle concerns in one line each: "If you're concerned about X, do Y."
- State each step and what the reader should see when it worked. Anticipate likely mistakes, and warn about screens that look like failures before the reader reaches them.
- Make the first fix for any problem "ask your AI", with a screenshot if the agent can't see the error.
- List every placeholder once, and say who fills it in.
- Refer to other sections by name, because numbers shift when documents change.

## Before publishing

Check that the documents match the code, rather than trusting your memory of it. Check them against the original request too, so nothing it asked for went missing. Where you can, have a fresh agent follow the setup from a clone. Search again for anything from the first section. A public repo without a license can't legally be reused, so ask which license to use. Open the published page in the user's browser.
