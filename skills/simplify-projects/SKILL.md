---
name: simplify-projects
description: Simplify project organization and maintenance. Use when asked to organize project folders, retire unused projects, consolidate duplicates, shorten agent instructions, or simplify tools and hooks that take effort to track.
---

# Simplify projects

Apply the relevant rules within the requested scope:

1. **Group work into folders with simple names.** Move files out of the project root
   where practical. Suggest a revised folder structure when it would make things
   easier to find.
2. **Retire work we're unlikely to revisit.** Identify incomplete projects, stubs,
   and abandoned experiments. Suggest deletion or archiving based on what remains
   worth preserving.
3. **Delete or merge duplicates.** Consolidate overlapping files, projects, and
   instructions into one clear home, preserving distinct useful content.
4. **Simplify instructions by choosing what matters.** Remove repetition.
   Instructions "not to do something" and explanations that "tool X doesn't do Y"
   are often unnecessary: figure out the information you actually want to state
   and remove those negative clarifications. Shorten by selecting what to say,
   and leave room for judgment.
5. **Simplify machinery that takes effort to track.** Review tools, hooks, and
   instructions that run in the background or have accumulated multiple purposes.
   Suggest removing them, narrowing their purpose, or replacing them with an
   explicit action.
6. **Propose guards against recurrence.** For findings that would come back
   without intervention, propose the smallest durable fix. One sentence in the
   folder's `AGENTS.md`, or in the skill that produced the clutter, is often
   enough; a very simple check is sometimes worth it.

All changes require the user's approval, either upfront for a defined scope or
after reviewing concrete suggestions. Where approval is needed, present numbered
proposals naming the affected files or folders, the change, and why it helps.
Show replacement wording for instruction edits. Execute approved proposals and
check affected links, references, and behavior.
