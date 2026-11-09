---
name: review-page
description: Build a web page where Alejo reviews a batch of items (outputs, findings, test results, emails, options) and records picks, grades or comments for the agent to act on. Use when he asks for a review page, review site, review artifact or gallery, or when he will pick, grade or comment on many items.
---

# Review page

The page lets Alejo make many judgments quickly and get them back to the agent in a
form it can act on. A good page lets him get through every item fast, without
leaving the page, and keeps every decision he makes.

## Principles

- **Make each item one thing he decides on.** Group or split the source records so
  each item is a single decision, described in a plain sentence or short paragraph.
  Do the grouping yourself: related records (an order's shipping emails, one bug's
  failing tests) become one item even when nothing in the data links them. Link to
  the underlying records from inside the item.
- **Show everything he needs to judge, in place.** Give the full snippet, quote or
  screenshot each decision needs. When he judges whole outputs, such as reports,
  documents or prompt versions, show the full documents, rendered, side by side,
  with the check results and other data that bear on them; don't reduce them to
  excerpts or scores. Cut only what doesn't bear on the decision, such as pipeline
  steps or internal labels. When he judges by taste, as with readings, show a
  passage long enough to tell whether he'd enjoy it, usually a few paragraphs.
- **Keep evidence one step away.** Put the source excerpt, example output or detail
  behind a hover, link or expand on the item it supports. Point links at the exact
  spot, such as a `#:~:text=` fragment, a timestamp or a line number.
- **Keep the layout still.** Give the page one simple spatial structure and keep every
  element where it is while he works. Moving between items moves a highlight, not the
  page; scroll only when the focused item would leave the screen, and only as far as
  needed. Open detail directly below the item or in a side panel, so nothing above it
  moves.
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
- **Show a realistic mock first when a long run will fill the page.** Show it with a
  few real or faithful items before the run, then show results as they arrive.

## Conventions

- Default to light mode.
- For a desk item, put the page in the item's folder
  (`~/best/desk/generated/YYYY-MM/<item>/page.html`, or `requested/`) and link it on /o as
  `https://agent-server.tail622085.ts.net/o?p=desk/<path to page.html>&run=1`. Keep it
  self-contained: inline scripts and styles, no external scripts, no `onclick=` attributes
  (use `addEventListener`). Save his decisions as JSON with
  `fetch('/o' + location.search.replace('run=1', 'answers=1'), {method: 'POST', headers:
  {'Content-Type': 'application/json'}, body: JSON.stringify(answers)})`; /o writes them to
  `answers.json` beside the page and commits it, so the next run reads that file. Load
  earlier answers from `/o?p=<item folder>/answers.json&raw=1`. Details: the "Item pages"
  paragraph of `~/work/clerk/docs/desk-pipeline.md`.
- Outside desk, write local HTML and open it in his browser. Publish a claude.ai
  artifact only when he explicitly asks for one.
