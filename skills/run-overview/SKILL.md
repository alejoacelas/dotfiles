---
name: run-overview
description: Create a concise OVERVIEW.md and live RUN-LOG.md when the user requests a run overview or run log, or delegates a project expected to span multiple work sessions with several independently reviewable deliverables. Do not trigger merely because a task involves several steps, tools, agents, or a deployment.
---
# Run overview

Create `OVERVIEW.md` and `RUN-LOG.md` beside the authoritative plan before execution.

In the overview, link the plan, state the concrete goals, and divide work into
stages. Give each stage a descriptive title, one goal, numbered steps, and
prerequisites that affect execution. Each step should produce something
independently useful or reviewable. End with what the user will be able to
inspect, use, or decide.

Initialize the log with those stages and unchecked steps. Check steps as they
finish. Beneath each, link outputs with short descriptions and record material
surprises, failures, or deviations as `Unexpected:`.

Write complete, concrete sentences. Use numbered lists and lettered subitems.
Mark optional steps `[optional]`. Include estimates or measured elapsed time
when they help scheduling or explain delays.
