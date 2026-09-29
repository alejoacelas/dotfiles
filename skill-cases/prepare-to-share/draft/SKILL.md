---
name: prepare-to-share
description: Prepare a repository for peers to adopt, focusing on the README and setup documentation. Use when asked to make a project public, shareable, or ready for others to reuse — "make a public version", "prepare this repo for sharing", "write a README other people can follow".
---

# Prepare a repository to share

The readers are peers: people with the same need who could use the project themselves, such as another organisation with a similar team, or someone who wants the same app. A repo written for yourself answers "how do I run this again?". A shared repo answers "what will this do for me, what will it cost, and how do I get it running?"

Focus on documentation and the changes needed for someone else to run the project, such as making a personal value configurable. Check claims against the implementation; correct an overstated claim rather than building the feature to justify it. Keep broader product improvements separate.

## Know your readers

Infer the readers from the project and request, using the [audience profiles](audiences/README.md) as starting assumptions. Establish what they already use, what this project adds, and what they must decide or do. Explain project-specific facts even when the underlying tools are familiar. Update a profile when feedback teaches something reusable about that role; keep individual circumstances in the receiver record.

If the user names specific receivers, check what has already passed between you and them: their original request, messages and threads, document comments, and call notes. Keep a gitignored `receivers.local.md` at the repository root, with one section per person:

- Their audience profile.
- What they asked for, with a link.
- What they have been told or shown, with the date and a link.
- Decisions they made, and questions still open.

Record only exchanges you can point to, so a tailored handover can skip known context and answer what they asked. Update the record after each new exchange. Public docs must still make sense to a peer who has never spoken with the author.

## Remove what isn't yours to share

Follow the global rule: share nothing about other people, organisations or clients that they haven't approved sharing. That includes names, internal links, message threads, and examples that reveal who the project was built for. Replace your own machine-specific details (local paths, personal tools, account and project IDs, password-manager items) with what a peer would use: standard tools, settings with defaults, and where to get their own keys and what they cost.

Peers will often point their own agents at the repo, and those agents read `AGENTS.md`. Write it for any agent working on the project. Put shareable rebuild notes in a "Maintainer notes" section at the end; keep private infrastructure and credential locations in private instructions.

Old commits keep whatever the current files no longer show. When the history contains something that can't be shared, publish a copy with fresh history, and say that you did.

## Write so every sentence earns its place

Spend the effort on selection and structure before polishing sentences. Decide what the reader needs to understand, decide or do, then draft around that. Cut a paragraph if removing it changes none of those things.

- Lead with what becomes possible for this reader. For someone who already uses an AI assistant, “search your files” says little; an example of analysing their entire history explains the added capability.
- Group by useful outcomes, not implementation components. Several imports may together mean “your full history in one place”; list individual sources where coverage matters.
- Make examples central and self-explanatory. Example prompts should express the user's question and leave the method to the agent. Add clarification requests when useful, rather than prescribing an elaborate workflow.
- Translate technical facts into consequences or actions. “The data directory is replaced monthly” becomes “Save work in this folder; files in that one are replaced monthly.” Explain mechanisms when they help the reader make a decision or carry out a step.
- Assume competence in familiar tools. Keep unfamiliar project details, but cut generic advice and reminders the audience already knows.
- Make each sentence add something. Shorten by choosing what matters, not by compressing it into abstract labels. Use concrete names and actions, and link to the exact primary-source pages readers need.

## README

Choose the structure around the reader's decision to try or adopt the project. The [team agent server](https://github.com/alejoacelas/team-agent-server) leads with a use case, then benefits and effort for members and owners, then technical detail. Use that as an example of attention order, not a template.

- Make the first screen explain what the project does and why the reader would want it, with a representative prompt, command and output, or screenshot.
- Put adoption-relevant facts before architecture: prerequisites, setup effort, cost and limitations that would change the decision. Separate audiences when their benefits or responsibilities differ; skip audience labels that add no useful information.
- Give costs with assumptions and dated sources, including existing subscriptions where relevant. Separate initial setup, per-person setup and maintenance when they create different burdens. Use measured setup times when available; label estimates and say what the human still has to do when an agent helps.
- Distinguish implemented, tested live, tested only in automation, and not yet available. A successful import using the author's credentials does not establish that a new user can connect their own account. Put consequential gaps beside the capability they qualify.
- Link to setup and reference material rather than reproducing it. Keep history and exhaustive inventories only where they help adoption.

## Setup documentation

If one prompt to the reader's agent can complete setup, give it in the README. Check this from the reader's actual starting point: the agent's app or environment must have the required access, and human sign-ins, payments and approvals still need explaining. Otherwise, provide setup docs.

- Split by task and responsibility when that saves readers from irrelevant instructions. An owner may need an overview for approval and separate execution steps; a member needs their own path. A small project may need only one section.
- Present a recommended default with a brief reason and its consequences. Distinguish decisions already made from choices the adopter must make. Explain who can access data, where it goes and what persists when those facts affect approval. Keep optional additions out of the default path, and name when they are useful.
- Start each path where that reader actually begins. Say what another person has already prepared and what remains for this reader. Remove obsolete manual steps when setup already handles them.
- Make handoffs explicit: who creates each account or key, supplies each value, fills each placeholder, and sends the finished instructions. Define placeholders once, with their source; replace them before a named recipient needs to act.
- State where to act, what to do and how to recognize success. Write conditional instructions as “If X, do Y” and restrictions as explicit rules. Where apps or environments differ, branch at the point of difference. Put likely mistakes and misleading screens before the action that exposes the reader to them.
- For ordinary troubleshooting in an AI-assisted workflow, start with asking the agent; use a screenshot when it cannot see the error. Preserve specific stop or escalation instructions where guessing would be harmful.
- Put machine-executable details in the instructions the reader's agent will actually load. Give humans the actions and rules they need, and explain how to resume later if the first session establishes context that would otherwise be lost.
- Refer to sections by name, since numbers shift as documents change.

## Before publishing

Read through each reader's path from first encounter to first useful result, without relying on the author's accounts, local files or conversation history. Check claims against the code and coverage against the original request. Where practical, have a fresh agent follow setup from a clone using ordinary adopter access, and distinguish that evidence from administrator or pilot tests. Check that README promises, setup steps and agent instructions agree.

Review the files and history for private material. Check the reuse license; if none has been chosen, ask the user which to apply. When publishing is part of the request, open the published page in the user's browser.
