---
name: save-skill-case
description: Save a concrete piece of work as evidence for a future skill, preserving instructions, outputs and source snapshots; draft a skill and propose evaluation cases. Use when the user says “save this as a skill idea”, “make a skill from what we did”, or wants to resume a saved skill case.
---

# Save a skill case

Make the idea cheap to capture and possible to resume without the original conversation. Preserve the concrete case before trying to discover its general form. A first draft is a hypothesis; another independent case is needed before proposing a broader skill.

## Capture the case

Start from what the user points to and their reason for saving it. Give a short provisional suggestion for what the skill would teach and what observable choices the user could grade. Save the available evidence immediately; refine these suggestions as you recover the relevant context.

Use an existing case collection when available. Otherwise create `skill-cases/<short-name>/` in the current repository if its visibility is appropriate, and link it from `skill-cases/README.md`. Keep private evidence in a private repository. Save a proposed skill inside the case, separate from installed skills, until the user chooses to adopt it.

Use [the case record](references/case-record.md) to retain:

- The user's idea and intended outcome, in their words where possible.
- Pointers to the relevant files, transcripts, review comments and outputs, with enough explanation to find the consequential passages.
- Exact quoted requests, follow-up corrections, prompts and commands given to agents, including relevant tool arguments and context files. These help specify the desired behavior; summaries alone lose constraints.
- The starting state, consequential intermediate versions and resulting artifacts. Distinguish the original output, the user's feedback, subsequent revisions and anything explicitly accepted. Producing an output does not establish approval.

Pin repository files to full commit IDs and paths. For uncommitted work, retain the base commit plus patch and relevant untracked files, or a durable snapshot with a checksum. For mutable documents or comments, retain an export of the relevant state. A checksum detects change; it does not preserve the content. Preserve disappearing transcript segments, quoted instructions and outputs in the case's access-controlled evidence folder; retain original locators and message IDs or timestamps. Redact secrets and record the omission.

Follow only the context needed to understand the case. Mark unavailable evidence and uncertain reconstructions explicitly. Check that a future agent can retrieve the saved inputs and outputs without relying on a temporary directory, moving branch, or the current conversation.

## Draft and propose evaluation

Write a first `draft/SKILL.md` addressing the user's named task. Extract the decisions that made the result useful, linking each proposed principle to supporting evidence in the case record. Keep project-specific facts in the case. Separate user requirements from inferred lessons and unresolved choices. With one case, keep the draft narrow rather than filling it with speculative general rules.

Propose a few grading questions the user can actually answer from the output. Prefer a concrete choice such as “Which opening would you keep?” or a check such as “Are executable setup instructions in a linked file?” when that is the user's stated preference. State what the reviewer will inspect and how to respond. Offer passage tags or comments where a score would hide the reason. Save the criteria and the user's changes to them.

Find a small set of evaluation candidates. For each, give a repository or artifact, an exact starting snapshot, the task to give the agent, why this case is informative, and where the user would review the result. Prefer states from before the relevant work was completed. Identify cases used to draft the skill so the user can distinguish those from new tests. Note consequential runtime, cost or access requirements.

Present the saved case, draft, criteria and proposed runs together. Ask the user to approve or change the cases, versions and grading dimensions before running evaluations. Existing explicit approval for those runs is sufficient. Capturing an idea or drafting a skill does not authorize running trials.

## Run approved cases

Freeze the approved skill versions, case snapshots, task and criteria. Give each version on each case a fresh agent context and isolated checkout. Supply only its assigned skill, task and permitted inputs; omit the drafting discussion, comparison hypothesis, competing versions and other agents' outputs. Keep model, tools and task conditions comparable, recording unavoidable differences. Describe actual isolation honestly.

Save the exact rendered agent prompt, launch command, supplied instructions, skill files and inputs, alongside the agent's transcript, raw outputs, diff and verification report. Preserve failures and coordinator corrections separately. Give the user direct links to the resulting documents and diffs, and a simple place to grade using the agreed questions. Use an existing review interface when suitable; terminal replies are sufficient. Keep judgments linked to the exact output and criterion versions.

## Look for a broader skill afterward

Once the case is durably saved and any approved trials are dispatched, you may look for other skill candidates in relevant existing records. Keep this search bounded and secondary to the capture. Look for shared decisions or recurring corrections, rather than shared subject matter or visual style.

After finding at least one other independent case, suggest a common skill supported by both. Show the shared behavior, differences that must remain conditional, and what would test the proposed generalization. Record it as a proposal; preserve the original cases and drafts so the user can decide what to combine.
