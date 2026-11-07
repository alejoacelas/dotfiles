---
name: artifact-design
description: Design rules for web pages, including claude.ai Artifacts. Load before writing an Artifact page.
---

# Page design

Follow, in this order: the user's words; the look of whatever the page shows or belongs to (a
product it mocks or prototypes, a screenshot, the project's own styles); then your own choices.
When the page mocks or prototypes an existing product, match that product's look across the whole
page and add no design of your own: no new fonts, no light/dark switching, no decorative layout.

Otherwise keep the page plain and well made:

- System fonts unless asked otherwise; one accent color.
- Lay out with flex or grid and `gap`. The page never scrolls sideways and works about 400px wide.
- Everything meant to be read is visible when the page loads.
- Keyboard focus is visible; motion respects `prefers-reduced-motion`.
- Copy is plain and names things as the reader knows them.
- Numbering, labels and dividers only where they say something true about the content.

## Only when publishing a claude.ai Artifact

The Artifact tool enforces these:

- Write the page without `<!doctype>`, `<html>`, `<head>` or `<body>`; start with `<title>` (a
  two-to-four-word name, no explanation after it) and `<style>`.
- Scripts load only from cdnjs.cloudflare.com (preferred), cdn.jsdelivr.net/npm, unpkg.com,
  cdn.tailwindcss.com or code.jquery.com, pinned to an exact version at least two weeks old;
  stylesheets only from Google Fonts. Inline everything else; embed assets as `data:` URIs.
- `alert`, `confirm`, `prompt`, `print`, download links and iframes of other sites don't work;
  handle forms in script.
- Define colors as tokens on `:root` and give `body` an explicit background. For both themes,
  redefine the tokens under `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }`
  and `:root[data-theme="dark"]`, with `color-scheme: dark`; a single deliberate look sets its
  colors and `color-scheme` on `:root` instead.
- Side gutter: `padding-left: max(16px, env(safe-area-inset-left, 0px))` and the same on the
  right, with `<meta name="claude:viewport-fit-sides" content="cover">` beside the title.
- `localStorage` only for per-viewer conveniences, in try/catch. State that must persist or be
  shared needs the `artifact-capabilities` skill.
- At most 16MB. Pass a one-word generic `icon` on the first publish.
