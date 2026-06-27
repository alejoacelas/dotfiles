---
name: sync-drive
description: Pull a Google Doc's tabs into local markdown mirror files (pull-only, never writes back). Splits configured tabs into per-file mirrors, cleans the export, and tracks freshness via a manifest. Use when the user wants to download / refresh / sync a Google Doc (e.g. intake forms, questionnaires) into a local folder, or check whether the local copies are stale — e.g. "sync the drive doc", "pull Samantha's forms", "are these forms up to date".
---

# sync-drive — Google Doc tabs → local markdown (pull-only)

Mirror selected tabs of a Google Doc into local markdown files. **Pull-only**: this
skill never writes back to Google Docs. Which doc/tabs map to which files lives in a
per-folder manifest (`<folder>/sync-manifest.json`); this skill reads it, refreshes the
files, and records freshness.

## When to run
- "sync / pull / refresh / download the drive doc", "update the intake forms".
- Before relying on a mirrored file — a Read hook may nudge you to run `--check` first.
- `--check` is a cheap freshness probe (one metadata call, no writing).

## 0. Find the manifest
Locate `sync-manifest.json` (look in the cwd and in the relevant person folder, e.g.
`sam/sync-manifest.json`). It holds, per doc:
- `title`, and ordered `tab_order` — **all top-level tab titles**, used as split
  boundaries (the markdown export has no machine markers between tabs).
- freshness state: `last_modified_time`, `last_synced`.
- a `forms` list: each has `tab` (the split marker = the tab's title), `tab_path` (the
  parent/child path shown in frontmatter), `out` (output file path), `form`,
  `call_date`, `filled_by`, and `sha256` of the last-written body.

If there is no manifest, ask the user which doc and which tabs map to which files, then
create one (schema + mechanics in `reference/google-docs-tabs.md`).

## 1. Connect to Google Drive
Use the Google Drive MCP connector (load schemas with ToolSearch
`select:mcp__claude_ai_Google_Drive__get_file_metadata,mcp__claude_ai_Google_Drive__download_file_content`
if they are not already available):
- `get_file_metadata` (fileId) → `modifiedTime` (the freshness signal) + `title`.
- `download_file_content` (fileId, `exportMimeType: text/markdown`) → base64 markdown of
  the **whole doc, all tabs concatenated** in document order. Large docs spill to a
  tool-results file — pass that file's path to the script.

## 2. Freshness check (`--check`)
1. `get_file_metadata` → `modifiedTime`.
2. Run:
   ```bash
   python3 scripts/sync_doc.py --check \
     --manifest sam/sync-manifest.json --doc-id <id> --modified-time "<modifiedTime>"
   ```
   Prints `OK` (exit 0) if unchanged since the last sync, or `STALE` (exit 3) if the doc
   moved on. On `OK`, stop — the mirror is current. On `STALE`, do a full sync (§3).

## 3. Full sync
1. `download_file_content` (`exportMimeType: text/markdown`). Note the spilled JSON path.
2. Run:
   ```bash
   python3 scripts/sync_doc.py \
     --manifest sam/sync-manifest.json --doc-id <id> \
     --from-mcp-json <download-result.json> --modified-time "<modifiedTime>"
   ```
   The script splits each configured tab out of the export using `tab_order` as
   boundaries, cleans it (unescape Google-Docs markdown escapes, drop the leading
   tab-title heading, strip trailing whitespace and empty bullets), writes each `out`
   file with stable provenance frontmatter, and refreshes the manifest's freshness
   state. It rewrites a file **only when its content actually changed** (so git diffs
   stay clean).
3. Report which files changed vs were already current, and flag any configured tab the
   splitter could not find — that usually means the tab was renamed (fix `tab_order` /
   `forms` in the manifest).

## Conventions & limits
- **Pull-only.** Never edit the Google Doc. Mirror files carry `sync: pull-only` and
  must not be hand-edited — local edits are overwritten on the next sync.
- **Tab boundaries are title-based.** The export has no markers between tabs, so the
  script splits on the known titles in `tab_order`. If a tab is renamed or added, update
  the manifest. Details and rationale in `reference/google-docs-tabs.md`.
- **Volatile state lives in the manifest** (`last_synced`, `last_modified_time`,
  `sha256`), not in the files — a file changes only when its body changes.
- **Only sync what's asked.** By default mirror the tabs listed in `forms`; do not pull
  transcripts/summaries that already live elsewhere (e.g. `*/transcripts/`).
