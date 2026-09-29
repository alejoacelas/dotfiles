---
name: save-skill-case
description: Save a concrete piece of work as evidence for a future skill, preserving instructions, outputs and source snapshots; draft a skill and propose evaluation cases. Use when the user says “save this as a skill idea”, “make a skill from what we did”, or wants to resume a saved skill case.
---

# Save a skill case

Make the idea cheap to capture and possible to resume without the original conversation. Preserve the concrete case before trying to discover its general form. A first draft is a hypothesis; another independent case is needed before proposing a broader skill.

## Keep the first draft independent

Until you have finished collecting the current case and saved and presented its first skill draft, use only the current conversation and the source files, transcripts and examples relevant to the user's request. Do not read or search previous skill cases, their index, derived skill drafts, evaluation results or cross-case summaries. Scope searches to the current case's sources so earlier interpretations do not bias the draft. The blank case template is safe to read. When explicitly resuming a saved case, read that case, but defer other cases until this checkpoint.

Defer updating the shared case index and searching for related cases until after presenting the first draft. Preserve that draft before incorporating anything learned from previous cases. If earlier case material is already in context, record that exposure rather than claiming the draft is independent.

## Capture the case

Start from what the user points to and their reason for saving it. Give a short provisional suggestion for what the skill would teach and what observable choices the user could grade. Save the available evidence immediately; refine these suggestions as you recover the relevant context.

Save each case as one self-contained folder, `~/best/dotfiles/skill-cases/<short-name>/`, whatever the current project. That folder is the private `alejoacelas/skill-cases` repository; if it is missing, clone it there. Keep everything about the case in its folder: the record, evidence, draft skill, trial runs, review data and the user's feedback. The case must still work if the original project is moved, rewritten or deleted, so copy in what it needs or cite GitHub URLs pinned to full commits; never depend on local project paths, temporary directories or moving branches. Add the idea, status and link to `~/best/dotfiles/skill-cases/README.md`. Save a proposed skill inside the case, separate from installed skills, until the user chooses to adopt it. Commit and push the case repository after each step.

Use [the case record](references/case-record.md) to retain:

- The user's idea and intended outcome, in their words where possible.
- Pointers to the relevant files, transcripts, review comments and outputs, with enough explanation to find the consequential passages.
- Exact quoted requests, follow-up corrections, prompts and commands given to agents, including relevant tool arguments and context files. These help specify the desired behavior; summaries alone lose constraints.
- The starting state, consequential intermediate versions and resulting artifacts. Distinguish the original output, the user's feedback, subsequent revisions and anything explicitly accepted. Producing an output does not establish approval.

Pin repository files to full commit IDs and paths. For uncommitted work, retain the base commit plus patch and relevant untracked files, or a durable snapshot with a checksum. For mutable documents or comments, retain an export of the relevant state. A checksum detects change; it does not preserve the content. Preserve disappearing transcript segments, quoted instructions and outputs in the case's evidence folder; retain original locators and message IDs or timestamps. In Claude Code transcripts, the user's instructions are not only typed prompts: messages sent mid-turn are stored as `queued_command` attachments, and answers to questions as `AskUserQuestion` tool results. Collect all three. Redact secrets and record the omission.

Follow only the context needed to understand the case. Mark unavailable evidence and uncertain reconstructions explicitly. Check that a future agent can resume from the case folder alone.

## Draft and propose evaluation

Write a first `draft/SKILL.md` addressing the user's named task. Extract the decisions that made the result useful, linking each proposed principle to supporting evidence in the case record. Keep project-specific facts in the case. Separate user requirements from inferred lessons and unresolved choices. With one case, keep the draft narrow rather than filling it with speculative general rules.

Grading is what the user does by reading outputs, so reserve it for judgments only they can make. Rules an agent can check reliably, such as “no code blocks in the README”, belong in the skill itself as checks, not in the grading. By default, grade by comparison and highlighting: put the same key excerpt from each version side by side, such as the first block of a README, and let the user highlight passages as bad writing, would cut, or really good. State what the reviewer will inspect and how to respond. Save the criteria and the user's changes to them.

Find a small set of evaluation candidates. For each, give a repository or artifact, an exact starting snapshot, the task to give the agent, why this case is informative, and where the user would review the result. Prefer states from before the relevant work was completed. Identify cases used to draft the skill so the user can distinguish those from new tests. Note consequential runtime, cost or access requirements.

Present the saved case, draft, criteria and proposed runs together, then run the trials without waiting for approval and save their outputs for the user to review when they return. Ask first only when a run needs significant cost, credentials the user must supply, or actions outside isolated checkouts, such as publishing or messaging people. Apply any changes the user makes to the cases, versions or criteria in later runs.

## Run the cases

Freeze the skill versions, case snapshots, task and criteria. Give each version on each case a fresh agent context and isolated checkout. Supply only its assigned skill, task and permitted inputs; omit the drafting discussion, comparison hypothesis, competing versions and other agents' outputs. Keep model, tools and task conditions comparable, recording unavoidable differences. Describe actual isolation honestly.

Run agents in temporary checkouts, then save everything into `runs/<date>/` in the case: the frozen skill versions, the exact rendered prompt and launch method, each run's base and result commits, diff, changed files and full transcript. Preserve failures and coordinator corrections separately.

Set up the review in `runs/<date>/review/` with the [review tool](../../skill-cases/review-tool/README.md) at `~/best/dotfiles/skill-cases/review-tool/`: write the manifest, build the page, and give the user the one command that opens it. Hide which version is A or B, and don't let one condition always be A. The user's feedback saves to `review/feedback.json`; commit it with the case so judgments stay linked to the exact outputs and criteria.

## Look for a broader skill afterward

Once collection of the current case is complete, its first draft is saved and presented, and its trials are dispatched, you may look for other skill candidates in relevant existing records. Keep this search bounded and secondary to the capture. Look for shared decisions or recurring corrections, rather than shared subject matter or visual style.

After finding at least one other independent case, suggest a common skill supported by both. Show the shared behavior, differences that must remain conditional, and what would test the proposed generalization. Record it as a proposal; preserve the original cases and drafts so the user can decide what to combine.
