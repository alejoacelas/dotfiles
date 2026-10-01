---
name: native-mockups
description: Render native-looking Before, Expected and Observed panels from HTML/CSS. Use only when the user explicitly invokes native-mockups by name.
disable-model-invocation: true
---
# Native mockups

A reader should recognize the surface and see the failure before reading any
explanation. Text reports of visual output hide the failure: "166 literal
Markdown links" and "bold preserved" both described pages the user found broken
at a glance.

## When to draw

Activate only when the user explicitly invokes `native-mockups` by name. The
following cases guide the work after invocation; they are not automatic triggers.

1. **Explaining a visual bug.** Draw Before, Expected and Observed.
2. **Before building UI from a verbal request.** Draw Expected, and Current when
   something exists, and get a yes before writing the code. "Scroll to see more
   results" can mean one page scrollbar or four scrolling columns.
3. **Before reporting that output on a visual surface is correct.** Capture or
   render what the reader will see and look at it yourself first.

Prefer a real screenshot when you can reach the surface (browser tools, computer
use, `gdoc export`). Reconstruct when the state is historical, cannot be
reproduced safely, or needs simplifying to isolate the trigger. Label every
reconstruction as one.

## Drawing

1. Copy [`frame.css`](frame.css) next to one HTML file per case. Stack the panels
   vertically at the same scale inside `<main>`. Use the state labels
   `.before`, `.expected`, `.observed` and a short subtitle saying which surface
   or moment each panel shows. [`example-slack.html`](example-slack.html) shows
   the structure.
2. Replicate the surface's native conventions: its fonts, colors, spacing,
   chrome (sidebars, toolbars, banners, scrollbars, avatars), and how it shows
   links, comments, suggestions, tables and lists. Draw only the chrome that
   helps the reader recognize the surface or that the failure involves.
3. Use CSS for layout and static appearance. JavaScript is fine for generating
   repetitive markup; the output is a still image.
4. Simplify the content, but keep whatever triggers the failure: a touching style
   boundary, a nested list, a missing scope, a second tab. Quote verbatim what the
   evidence gives verbatim, and mark invented text as illustrative.
5. Put API calls, logs, codepoints, counts and cause notes in a `.diag` block
   under the panel. They are not part of the surface.
6. Render: `uv run --with playwright python <skill-dir>/render.py case.html`.
7. Open every PNG and check it: no overflow or clipped text, Expected and Observed
   differ visibly where the bug is, and nothing unrelated differs.

## Delivering

Send the images where the reader will look at them. For a set, create a Google
Doc with one heading per case, the image at 468 pt wide, and one or two sentences
beneath naming the failure and the condition that triggers it, plus a source
link. Use `gdoc new` and `gdoc insert-image --width 468` with the account that
matches the project. For a single case in chat, give the PNG path or publish it.
