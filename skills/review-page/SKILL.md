---
name: review-page
description: Build a web page where Alejo reviews a batch of items (outputs, findings, test results, emails, options) and records picks, grades or comments for the agent to act on. Use when he asks for a review page, review site, review artifact or gallery, or when he will pick, grade or comment on many items.
---

# Review page

The page lets Alejo make many judgments quickly and get them back to the agent in a
form it can act on. A good page lets him get through every item fast, without
leaving the page, and keeps every decision he makes.

## Principles

- **Keep evidence one step away.** Put the source excerpt, example output or detail
  behind a hover, link or expand on the item it supports. Point links at the exact
  spot, such as a `#:~:text=` fragment, a timestamp or a line number.
- **Keep the layout still.** Give the page one simple spatial structure and keep every
  element where it is while he works.
- **Make it keyboard-first.** Arrow keys move between items, and single keys record a
  pick or grade. Show the keys on the page.
- **Send his decisions back to the agent.** Save picks and comments where the agent
  can read them, tied to the item they belong to. Items he commented on get handled
  on the next pass.
- **Put the most important items first.** Sort by surprise, risk or disagreement so
  stopping early loses the least. Dim the items that need no judgment.
- **Let the layout show the structure.** Use bullets for parallel items and paragraph
  breaks between ideas. Aim for a calm, readable page, like a reader or Gmail, with
  one accent colour.
- **Show a realistic mock first when a long run will fill the page.** Show it with a
  few real or faithful items before the run, then show results as they arrive.

## Conventions

- Default to light mode.
- Write local HTML and open it in his browser. Publish a claude.ai
  artifact only when he explicitly asks for one.
