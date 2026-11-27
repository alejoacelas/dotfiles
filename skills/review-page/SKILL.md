---
name: review-page
description: Build a web page where Alejo reviews a batch of items (outputs, findings, test results, emails, options) and records picks, grades or comments for the agent to act on. Use when he asks for a review page, review site, review artifact or gallery, or when he will pick, grade or comment on many items.
---

# Review page

The page lets Alejo make many judgments quickly and get them back to the agent in a
form it can act on. A good page lets him get through every item fast, without
leaving the page, and keeps every decision he makes.

## Principles

- **Land on a still overview.** The first view shows everything he needs to choose
  where to look, and he stays on it. More detail appears in place on click or
  hover, in a side panel or over the page, and never moves him down the page or to
  another one. Toggles may change what the overview shows.
- **Keep evidence one step away.** Put the source excerpt, example output or detail
  behind that click or hover, on the item it supports. Point links at the exact
  spot in the source.
- **Make it keyboard-first.** Arrow keys move between items. Add at most a handful
  of other keys, for picks, grades or toggles, and show them on the page.
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
- Write local HTML and open it in his browser. Publish a claude.ai
  artifact only when he explicitly asks for one.
