---
name: run-overview
description: Create a concise OVERVIEW.md and live RUN-LOG.md when the user requests a run overview or run log, or delegates a project expected to span multiple work sessions with several independently reviewable deliverables. Do not trigger merely because a task involves several steps, tools, agents, or a deployment.
---
# Run overview

Create `OVERVIEW.md` before the run starts and keep `RUN-LOG.md` updated while it runs. Put them beside the main plan unless the project already has a clear location for run documents.

The plan remains authoritative. The overview is a short, concrete map of the plan, not a second implementation plan.

## Writing rules

Write every substantive goal and step as one clear sentence.

Treat a step as a meaningful unit of work, not as a single verb or atomic action. Keep related actions together when they produce the same immediate result or naturally happen in one working period. Split them when they can usefully be scheduled, completed, reviewed, or discussed independently.

- Give each sentence enough context to be understood without reconstructing its relationship to nearby items.
- Use concrete verbs and named objects, while preserving conjunctions and subordinate clauses that explain how actions relate.
- Use numbered lists for multi-item sections and lowercase `a.`, `b.`, `c.` labels for nested items so every item is easy to reference.
- Keep each stage goal as one unnumbered bullet by default, and do not number section titles within a stage.
- Give stages descriptive titles that say what they accomplish.
- List each run goal separately; give each stage one goal unless it genuinely needs more.
- Add the literal `[optional]` tag to a step only when the run can deliver its intended result without it.
- Nest links to generated artifacts beneath the step that produces them, using `link — contents`
- Focus artifact descriptions on the parts most likely to deserve the user's attention, without telling the user how to review them.

## `OVERVIEW.md`

Begin with an “at a glance” title and a link to the authoritative plan. State the run's concrete goals, then divide the work into stages.

Give each stage:

1. A descriptive title.
2. One clear goal.
3. A numbered list of meaningful steps.
4. Links to relevant plan sections or generated artifacts where they help explain the work.
5. Assumptions or prerequisites that materially affect whether the stage can proceed as described.

Omit headings that add no useful information, but retain the distinction between the stage's intended result and the work used to achieve it.

End with the concrete things the user will be able to inspect, use, or decide after the run.

## `RUN-LOG.md`

Create the log with the overview's stages and unchecked steps before execution, then update it as work finishes.

```markdown
# Run log

## Stage 1: <Descriptive accomplishment>

1. [x] <Completed step.>
   a. [<Output>](<path>) — <Contents most likely to deserve attention.>
   b. Unexpected: <Material surprise, deviation, failure, or new work.>
2. [ ] <Pending step.>
```

- Check off steps as they finish and link their outputs underneath.
- Add `Unexpected:` only for a material surprise, deviation, failure, or new piece of work.
- Keep the log short enough to understand from the checked steps, output links, and unexpected events.

## Optional timing

Time estimates and actual-time tracking are optional. Decide independently whether each helps the user schedule work, compare approaches, or understand a material delay; no explicit request is needed. Omit timing when it would add bookkeeping or imply precision the available evidence does not support.

When useful:

- Add estimates to relevant steps or stages, using `m` and `h` without decimals, such as `[20m]` or `[1–2h]`.
- Add serial step estimates for a stage total; explain overlapping work rather than adding its times.
- Record actual elapsed time only when it can be measured reliably. If an estimate exists, preserve it beside the actual time, such as `[est 30m | actual 42m]`.
