---
name: review-page
description: Build a web page where Alejo reviews a batch of items (outputs, findings, test results, emails, options) and records picks, grades or comments for the agent to act on. Use when he asks for a review page, review site, review artifact or gallery, or when he will pick, grade or comment on many items.
---

# Review page

The page lets Alejo make many judgments quickly and get them back to the agent in a
form it can act on. A good page lets him get through every item fast, without
leaving the page, and keeps every decision he makes.

## Principles

- **Make the first view the home.** Everything on the page is reached from the
  first view and returns to it: it shows what he needs to choose where to look,
  and the rest opens from it in place, in a side panel or over the page, on click
  or hover. Not everything has to be visible on landing. Toggles may change what
  the first view shows.
- **Keep evidence one step away.** Put the source excerpt, example output or detail
  behind that click or hover, on the item it supports. Point links at the exact
  spot in the source.
- **Make it keyboard-first.** Give the arrow keys a role where you can. Assign
  three to six other hotkeys when there are actions he'll repeat, and show the
  keys on the page.
- **Give items and views persistent links.** Ideally each item and each view has its
  own address, so a link reopens the page on that item in that view.
- **Send his decisions back to the agent.** Save picks and comments where the agent
  can read them, tied to the item they belong to. Items he commented on get handled
  on the next pass.
- **Put the most important items first.** Sort by surprise, risk or disagreement so
  stopping early loses the least.
- **Show a realistic mock first when a long run will fill the page.** Show it with a
  few real or faithful items before the run, then show results as they arrive.

## Conventions

- Hardcode light mode: the page looks the same whatever the system theme.
- Publish a claude.ai artifact only when he explicitly asks for one.
