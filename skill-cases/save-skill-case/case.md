# Saving cases for future skill development

## Idea and current state

Preserve how `save-skill-case` was developed so the user can update it later from the original requests, outputs and corrections. **Captured for later; no trials approved or run.**

The user wanted to record a concrete idea and enough context to resume it, draft a skill and propose tests, then defer finding a more general skill until another case exists. Exact requests and commands are preserved in the [private evidence bundle](https://github.com/alejoacelas/private-skills/tree/54eee30a19dce6f2c6778b835d035e19034604a7/skill-cases/save-skill-case/evidence).

The [frozen draft](draft/SKILL.md) is the existing skill at the end of this conversation, with its [case template](draft/references/case-record.md). It is a baseline for future revision, not a newly inferred replacement. The installed skill was not changed by this capture.

## Evidence and versions

| Evidence | Meaning | Pinned source |
| --- | --- | --- |
| E1 | User's core specification: preserve cases, source pointers, outputs and quoted agent instructions; draft and propose tests; generalize afterward | Private `user-instructions.md`, 2026-09-29T19:02:05.078Z |
| E2 | Concrete grading and selection feedback | Same file, earlier requests from 17:39–18:05 UTC |
| E3 | Initial implemented skill and template | [823d304](https://github.com/alejoacelas/dotfiles/blob/823d30426792a55e37a64ddeece74e823ecf39d8/skills/save-skill-case/SKILL.md) |
| E4 | Central storage in dotfiles | [e1516c9](https://github.com/alejoacelas/dotfiles/blob/e1516c9b1418955b20c9d6e1e026173c8e2dfdd7/skills/save-skill-case/SKILL.md); user request at 19:07:37.338Z |
| E5 | Remove redundant overview pointer | [a9f4798](https://github.com/alejoacelas/dotfiles/blob/a9f479867016029348e7ff9cd5b68b871fab9e98/README.md); user correction at 19:08:02.531Z |
| E6 | Finish collecting and present the first draft before reading previous cases | [9a6f4ae](https://github.com/alejoacelas/dotfiles/blob/9a6f4aef814b3ca9ff669ffce727eb4584bc6bad/skills/save-skill-case/SKILL.md); user correction at 19:35:05.279Z |

Full commit IDs are also in [versions.json](versions.json). Git preserves the intermediate outputs; the frozen draft preserves the final skill bundle locally. The private JSONL retains the development segment's exact user and assistant messages, tool calls, shell commands and returned results. The accompanying provenance file records the original transcript path, session ID, timestamps, selection boundaries and checksum. It is an excerpt, not the full conversation.

## Requirements versus implementation choices

- **Explicit (E1):** preserve original instructions and outputs, along with recoverable source snapshots; make an initial draft and propose evaluation cases; run only approved trials; defer broader synthesis until another case supports it.
- **Explicit (E2):** use narrow, answerable grading questions and passage-level feedback rather than nebulous quality scores. The earlier document-review example motivated these choices; its exact interface is not a required template.
- **Explicit (E4–E5):** store cases centrally in dotfiles and avoid duplicating the location in the root README.
- **Explicit (E6):** previous cases must not influence the first capture and draft.
- **Implementation choices:** folder layout, status names and the record template are agent choices. Private storage follows repository visibility rules. They remain revisable.

## Exposure and limits

This is a retrospective self-capture, not an independent test. The drafting conversation and installed skill are already in context. The agent previously saw the case index, including the interface-judgment entry, and knows about the prepare-to-share experiments from this same conversation. No other saved case contents were opened for this capture. Do not count these related topics as independent validation of the meta-skill.

The supplied Claude conversation excerpt reported a potential contamination problem. Its actual subsequent behavior was not inspected here. The restart/rewind advice is preserved as conversation evidence, not verified proof of an uncontaminated run.

## Proposed grading questions

These are suggestions for a later comparison; the user has not approved a rubric.

1. **Can another agent recover the case without the original chat?** Check each consequential source pointer against a pinned revision or preserved copy. Grade yes / partly / no, naming missing evidence.
2. **Did it preserve what was asked and what was produced?** Inspect verbatim user instructions, corrections, rendered agent prompts/commands and corresponding outputs. Mark missing or misattributed items.
3. **Did it keep the first draft independent?** Inspect the agent's read/search trace up to the saved and presented draft. Grade no prior-case reads / prior-case reads / cannot verify. Record pre-existing exposure separately.
4. **Can the user approve a concrete test plan?** Check for task, starting snapshot, skill versions, grading question and review destination. Mark missing fields; verify that no trial ran without approval.
5. **Which record needs less editing before you would trust it for later work?** Choose A / B / combine / neither and highlight unsupported requirements, unnecessary text or missing context.

## Suggested evaluations for later

Both are replays of this development case, not held-out tests. Run in a disposable checkout with private evidence accessible only to the coordinator. Supply workers only the selected user messages; do not expose this case record, later assistant answers, competing skill versions or the whole transcript bundle.

| Candidate | Exact input and task | What it tests |
| --- | --- | --- |
| Initial capture | Private evidence commit `54eee30a19dce6f2c6778b835d035e19034604a7`, `user-instructions.md`: use the 19:02:05.078Z message and the earlier user messages only. Ask the agent to capture that idea, draft a skill and propose evaluations. | Whether instructions and outputs are preserved and the plan is concrete without launching trials. This is a partial replay: missing original artifacts must be disclosed rather than invented. |
| Avoid prior-case influence | Same private commit, user messages through 19:35:05.279Z. Use an isolated dotfiles fixture with the assigned skill version and a case index plus unrelated case files present but unopened. Ask for a fresh capture from the supplied messages. | Whether it completes and presents a first draft before reading the index or earlier cases. Build and pin the exact fixture before requesting run approval. |

Suggested comparison: initial skill `823d30426792a55e37a64ddeece74e823ecf39d8` versus final baseline `9a6f4aef814b3ca9ff669ffce727eb4584bc6bad`, with matching task, model and tools. Review generated `case.md`, draft and read/search trace side by side, with terminal grading using the questions above. No paid services or live project changes are needed; normal agent usage still applies. Case 2 is not ready to dispatch until its fixture is pinned.

## Resume later

Read this record and the private evidence, choose the change to test, then approve or revise the candidate inputs and grading questions. Preserve this baseline and record future drafts separately. No broader skill proposal is needed for this capture.
