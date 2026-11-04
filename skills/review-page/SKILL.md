---
name: review-page
description: Build a web page where Alejo reviews a batch of items (outputs, findings, test results, emails, options) and records picks, grades or comments for the agent to act on. Use when he asks for a review page, review site, review artifact or gallery, or when he will judge many items and a page would make that faster than reading Markdown.
---

# Review page

The page lets Alejo make many judgments quickly and get them back to the agent in a
form it can act on. A good page lets him get through every item fast, without
leaving the page, and keeps every decision he makes.

## Principles

- **Make each item one thing he decides on.** Group or split the source records so
  each item is a single decision, described in a plain sentence or short paragraph.
  Link to the underlying records (emails, runs, files) from inside the item.
- **Show enough to judge in place.** Give the full snippet, quote or screenshot he
  needs to decide, and cut everything else, such as pipeline steps or internal labels.
- **Keep evidence one step away.** Put the source excerpt, example output or detail
  behind a hover, link or expand on the item it supports.
- **Make it keyboard-first.** Arrow keys move between items, single keys record a
  pick or grade, and one key opens a comment box on the focused item. Show the keys
  on the page.
- **Send his decisions back to the agent.** Save picks and comments where the agent
  can read them, tied to the item they belong to. Items he commented on get handled
  on the next pass.
- **Put the most important items first.** Sort by surprise, risk or disagreement so
  stopping early loses the least. Dim the items that need no judgment.
- **Let the layout show the structure.** Use bullets for parallel items and paragraph
  breaks between ideas. Aim for a calm, readable page, like a reader or Gmail, with
  one accent colour.
- **Show a realistic mock first.** Before filling the page at scale, show it with a
  few real or faithful items. For long runs, show results as they arrive.

## Conventions

- Default to light mode.
- Publish as a private claude.ai artifact, or write local HTML and open it in his
  browser.
