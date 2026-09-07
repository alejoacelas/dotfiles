---
name: run-overview
description: Create a concise OVERVIEW.md and live RUN-LOG.md before a substantial, long-running, autonomous, multi-stage, or multi-agent run. Use when the user wants a large plan made easy to inspect without replacing the main implementation plan. Do not use for ordinary short tasks.
---

# Run overview

Create `OVERVIEW.md` before the run starts and keep `RUN-LOG.md` updated while it runs. Put them beside the main plan unless the project already has a clear location for run documents.

The plan remains authoritative. The overview is a short, concrete map of the plan, not a second implementation plan.

## Writing rules

- Use bullets for the substantive content, with one sentence per bullet.
- Use concrete verbs and named objects; avoid abstract process language.
- Give stages descriptive titles that say what they accomplish.
- Write times as `m` and `h`, without decimals.
- Prefix every step with its estimated elapsed clock time, such as `[20m]`, `[1h]`, or `[1–2h]`.
- Add the literal `[optional]` tag after the time only when the run can deliver its intended result without that step.
- Add the step estimates to produce the total time shown in each stage title.
- Nest links to generated artifacts beneath the step that produces them, using `link — contents` without phrases such as “will contain.”
- Focus artifact descriptions on the parts most likely to deserve the user's attention, without telling the user how to review them.

## `OVERVIEW.md`

Use this shape, omitting sections that genuinely add nothing:

```markdown
# <Run name> at a glance

The [main plan](PLAN.md) defines the execution rules.

## Goal of the run

- <Concrete result the run should produce.>

## Stage 1: <Descriptive accomplishment> [<total time>]

### Goal

- <Concrete result of this stage.>

### Plan and guidance

- [<Plan file>](<path>) — <Relevant instructions.>

### Steps

- [30m] <Concrete action.>
  - [<Artifact>](<path>) — <Contents most likely to deserve attention.>
- [1h] [optional] <Concrete action that is not required for the intended result.>
  - [<Artifact>](<path>) — <Contents most likely to deserve attention.>

### Assumptions and prerequisites

- <Condition that must hold or problem that could prevent the stage from finishing as planned.>

## Expected outcome

- <Concrete thing the user can inspect, use, or decide after the run.>
```

## `RUN-LOG.md`

Create the log with the overview's stages and unchecked steps before execution, then update it as work finishes.

```markdown
# Run log

## Stage 1: <Descriptive accomplishment> [est 2h | actual 3h]

- [x] [est 30m | actual 42m] <Completed step.>
  - [<Output>](<path>) — <Contents most likely to deserve attention.>
  - Unexpected: <Material surprise, deviation, failure, or new work.>
- [ ] [est 90m | actual —] <Pending step.>
```

- Keep the initial estimate beside the actual elapsed clock time.
- Use the estimate's units for the actual time and round actual times up to avoid decimals.
- Check off steps as they finish and link their outputs underneath.
- Add `Unexpected:` only for a material surprise, deviation, failure, or new piece of work.
- Preserve the original estimates so the user can see where the run took longer or less time than planned.
- Keep the log short enough to understand from the checked steps, output links, and unexpected events.
