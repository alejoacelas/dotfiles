# Case record

Use this structure for `case.md`, omitting empty sections. Keep artifacts beside it. After collecting the current case and saving and presenting its first draft, add a short entry to `~/best/dotfiles/skill-cases/README.md` with the idea, status and link. The record should let another agent resume without repeating the original investigation.

## Idea and current state

- User's description and what they want to reuse.
- Current state: captured, draft ready, running, awaiting review, or reviewed.
- Next decision, unresolved questions and known missing evidence.

## Evidence

For each consequential source, record its role, durable locator and relevant passage:

| ID | Role and why it matters | Exact locator | Preserved copy |
| --- | --- | --- | --- |

Roles include starting input, instruction, correction, output and acceptance. For repository files, include remote, full commit and path. For transcripts, include provider, session ID, message ID or timestamp, local path and a distinctive search phrase. For reviews, include the comment link and the artifact revision it concerns. Line numbers alone are fragile.

Quote the actual instructions and commands, with attribution and chronology. Include the agent's context and constraints where they affect the result. Distinguish a command supplied by the user from a command chosen by the agent. Save resolved comments that explain changes, not only the latest document. Retain the relevant before/after output as well as the final state.

## Draft and proposed criteria

Link `draft/SKILL.md`. List its main proposed decisions, supporting evidence IDs, and whether each is an explicit requirement, an inference or an open question.

For each grading dimension, save the exact question, artifact or excerpt to inspect, response choices or observable pass condition, and space for the user's rationale. Preserve earlier criteria when they have already been used to grade a run.

## Suggested cases

For each candidate, record:

- Repository/artifact and pinned starting state; retrieval or reconstruction instructions.
- Proposed task and why the case is informative; whether it informed the draft.
- Skill versions to compare and required environment or services.
- Expected output, review location and relevant cost or access limits.
- Run status, and the user's exact adjustments when given.

## Runs and review

Use a separate folder for each run. Preserve the full skill bundle and supplied instructions, exact rendered prompt and command, model/settings, input snapshot, environment constraints, agent transcript, raw output and diff. Record completion or failure, checks actually performed, and any unverified behavior. Link published artifacts to immutable revisions when possible.

Link each user judgment to its run, output revision and criterion version. Keep a corrected output separate from the original. Record subsequent draft changes and which feedback motivated them.

## Related cases

Link independent cases and the evidence for shared behavior. Keep a proposed broader skill separate from the captured case and its first draft until the user decides to combine them.
