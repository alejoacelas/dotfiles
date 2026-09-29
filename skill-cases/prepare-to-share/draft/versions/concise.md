---
name: prepare-to-share
description: Prepare a repository for peers to adopt, focusing on the README and setup documentation. Use when asked to make a project public, shareable, or ready for others to reuse — "make a public version", "prepare this repo for sharing", "write a README other people can follow".
---

# Prepare a repository to share

Help a peer answer three questions: **What does this add for me? What must I decide? What must I do?** Focus on documentation and the small changes needed for another person to run the project, such as making personal values configurable. Keep broader product improvements separate.

1. **Write from the reader's starting point.** Establish what they already know, use and have available. Use the [audience profiles](../audiences/README.md) as starting assumptions. If recipients are named, check prior exchanges and keep a linked, gitignored `receivers.local.md` record of their requests, known context and open questions. Put reusable lessons in the profiles and individual circumstances in that record. Public docs must also make sense to someone who has never spoken with the author.

2. **Explain the value through a representative use.** Show what becomes possible, then give the cost, effort and limitations that affect adoption. For someone who already uses an AI assistant, “search your files” says little; analysing their entire history explains the added capability. Choose examples that express the user's goal without prescribing the agent's method. Let implementation details follow when they help.

3. **Organize around decisions and actions.** Choose the document structure by reader needs. Separate approval from execution when useful. Recommend a default, explain consequential trade-offs, and make responsibilities and handoffs clear. Keep optional additions out of the default path. A small project may need only a README; a team deployment may need different paths for owners and members.

4. **Make the path executable.** Readers should know where to act, what to do and how to recognize success. Account for what their agent can access and what still requires a human. If one prompt can complete setup from that starting point, provide it; otherwise write the necessary steps. Anticipate likely mistakes where they occur. Put agent instructions where the reader's agent will load them. Check the path to a first useful result using ordinary adopter access where practical, without relying on the author's accounts, files or conversation history.

5. **Make every detail earn its place.** Keep information that changes understanding, a decision or an action. Translate technical facts into consequences: “monthly replacement” becomes “save work in this folder; files in that one are replaced monthly.” Remove repetition and familiar advice. Shorten by selecting what matters, not by compressing it into abstract labels. Check claims against the code and coverage against the request; distinguish what works from what was actually tested. Link to evidence and exact pages readers need, and keep the README, setup and agent instructions consistent.

Share only material the owner is entitled to publish. Replace private and machine-specific details with what a peer would use; check history as well as current files, and use a fresh public copy when history cannot be shared. Keep private rebuild notes outside the public repo. Check the reuse license and ask if none has been chosen. When publication is requested, inspect the published result.
