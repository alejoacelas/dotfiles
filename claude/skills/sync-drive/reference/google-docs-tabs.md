# Google Docs tabs → markdown: mechanics & limits

Notes that explain why `sync-drive` works the way it does. Read this when setting up a
new manifest or when a sync looks wrong.

## How the export behaves
- `download_file_content` with `exportMimeType: text/markdown` exports the **whole
  document**: every tab (including nested child tabs) concatenated in document order.
- Each tab's **title renders as a top-level `# ` heading** at the start of its block.
  Nested tabs are flattened — a parent tab's title H1 is immediately followed by its
  children's title H1s.
- The export is base64-encoded inside the MCP result's `content` field. Large docs are
  spilled to a tool-results JSON file; pass that path as `--from-mcp-json`.
- `read_file_content` (the "natural language" reader) returns similar text but is meant
  for reading, not faithful round-tripping. Prefer the markdown export for syncing.

## Why splitting is title-based (and the main limitation)
The export contains **no machine-readable delimiter** between tabs — no tab IDs, no
horizontal rules. The only reliable boundary is the tab's title heading. So the manifest
stores `tab_order` = the ordered list of **every top-level tab title**, and the splitter
bounds each wanted tab by the next title in that list. Content can contain its own `# `
headings (e.g. a form titled `# Follow-up Call Questionnaire`); those are ignored as
boundaries because they are not in `tab_order`.

**Limitation:** if someone **renames or adds a tab** in the doc, `tab_order` goes stale
and a block may be mis-bounded or a form may be reported `MISSING`. Fix: update
`tab_order` (and any `forms` entry) in the manifest. The script exits non-zero and names
the missing tab so this is visible, not silent.

Tab IDs (the `tab=t.xxxx` in a Doc URL) would make this robust, but they require the
Google **Docs** API (`documents.get?includeTabsContent=true`), which the Drive MCP
connector does not expose. Title-based splitting is the pragmatic option available here.

## Cleaning applied to each tab body (deterministic, byte-stable)
1. Drop the leading tab-title `# ` heading (it's captured in frontmatter).
2. Unescape Google-Docs markdown escapes: `\-` `\.` `\!` `\&` `\*` `\(` `\)` `\[` `\]`
   `\#` `\@` `\_` `\>` `\~` `` \` `` `\+` → the bare character.
3. Strip trailing whitespace on every line.
4. Drop empty bullet lines (`* ` with nothing after).
5. Collapse 3+ blank lines to one blank line; trim ends; end with a single newline.

Keep this stable: changing it rewrites every mirror file on the next sync.

## Trimming a tab to answers-only (optional)
A `forms` entry may set `clip_start` and/or `clip_end` (exact heading text, unescaped).
After the tab title is dropped, the body is clipped to `[first heading == clip_start,
first heading == clip_end)` before cleaning. Use this to keep only the filled
questionnaire and drop template chrome (intro, table-of-contents, appendices). A missing
anchor is a no-op on that side. This is deterministic, so re-syncs stay byte-stable.

## What goes where
- **Stable provenance** (doc id, tab, form, who filled it, call date) → file frontmatter.
- **Volatile sync state** (`last_synced`, `last_modified_time`, per-form `sha256`) →
  the manifest only. This keeps file git-diffs limited to real content changes.

## Setting up a new doc in the manifest
1. `get_file_metadata` → `title`, `modifiedTime`.
2. `download_file_content` (markdown) → list the top-level `# ` headings in order to read
   off the tab structure; record them as `tab_order`.
3. Decide which tabs to mirror and where; add a `forms` entry for each.
4. Run a sync; confirm the files and a clean re-run (`current`, no `MISSING`).
