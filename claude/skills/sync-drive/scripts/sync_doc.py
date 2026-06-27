#!/usr/bin/env python3
"""Pull-only sync of Google Doc tabs -> local markdown mirror files.

The Drive calls (get_file_metadata, download_file_content) are made by the agent via
the Google Drive MCP connector. This script does only the deterministic local work:
split configured tabs out of the exported markdown, clean them, write the mirror files,
and track freshness in the manifest. It never touches Google Docs.

Modes
  (default) sync : split + clean + write configured tabs, refresh manifest state.
  --check        : compare a supplied Drive modifiedTime against the manifest and report
                   OK (exit 0, unchanged) or STALE (exit 3). Does no writing.

Manifest schema (<folder>/sync-manifest.json):
  {
    "docs": {
      "<doc_id>": {
        "title": "...",
        "tab_order": ["<every top-level tab title, in order>", ...],
        "last_modified_time": "<RFC3339 from Drive metadata, or null>",
        "last_synced": "<YYYY-MM-DD or null>",
        "forms": [
          {"tab": "Pre-call - May19",
           "tab_path": "May19-all-the-context / Pre-call - May19",
           "out": "sam/intake-forms/2026-05-19-intake-questions.md",
           "form": "Intake questions (first call)",
           "call_date": "2026-05-19",
           "filled_by": "Samantha Kagel",
           "sha256": "<body hash, filled by this script>"}
        ]
      }
    }
  }
"""
import argparse
import base64
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

# --- cleaning: must stay byte-stable so re-syncs produce clean diffs ----------
_ESC = re.compile(r"\\([-.!&*()\[\]#@_>~`+])")   # unescape Google-Docs md escapes
_EMPTY_BULLET = re.compile(r"(?m)^\s*\*\s*$\n?")  # drop empty "* " bullet lines
_BLANK_RUNS = re.compile(r"\n{3,}")


def _heading_text(line):
    """Unescaped text of a markdown heading line, or None if not a heading."""
    s = line.strip()
    if not s.startswith("#"):
        return None
    return _ESC.sub(r"\1", s.lstrip("#").strip())


def clip(lines, start, end):
    """Keep [first heading == start, first heading == end). Either may be None.
    A missing anchor is a no-op on that side (whole content kept)."""
    if start:
        for i, l in enumerate(lines):
            if _heading_text(l) == start:
                lines = lines[i:]
                break
    if end:
        for i, l in enumerate(lines):
            if _heading_text(l) == end:
                lines = lines[:i]
                break
    return lines


def normalize(lines):
    s = "\n".join(lines)
    s = _ESC.sub(r"\1", s)                                  # unescape gdoc md escapes
    s = "\n".join(line.rstrip() for line in s.split("\n"))  # strip trailing ws
    s = _EMPTY_BULLET.sub("", s)                            # drop empty bullets
    s = _BLANK_RUNS.sub("\n\n", s)                          # collapse blank runs
    return s.strip() + "\n"


def render_body(block_lines, clip_start=None, clip_end=None):
    """Drop the leading tab-title heading, optionally clip to an answers-only
    sub-range, then normalize. Deterministic so re-syncs stay byte-stable."""
    body = block_lines[1:] if block_lines and block_lines[0].lstrip().startswith("# ") else list(block_lines)
    body = clip(body, clip_start, clip_end)
    return normalize(body)


def frontmatter(doc_id, doc_title, form):
    """Stable provenance only — volatile sync state stays in the manifest."""
    return (
        "---\n"
        f"source_doc_id: {doc_id}\n"
        f'source_doc_title: "{doc_title}"\n'
        f'source_tab: "{form.get("tab_path", form["tab"])}"\n'
        f'form: "{form["form"]}"\n'
        f'filled_by: {form.get("filled_by", "")}\n'
        f'call_date: {form.get("call_date", "")}\n'
        "sync: pull-only   # mirror of the Google Doc tab; do not edit by hand\n"
        "---\n\n"
    )


# --- export loading -----------------------------------------------------------
def load_export(args):
    if args.export_file:
        return Path(args.export_file).read_text()
    if args.from_mcp_json:
        data = json.loads(Path(args.from_mcp_json).read_text())
        content = data.get("content")
        if content is None:
            sys.exit("error: --from-mcp-json file has no 'content' field")
        return base64.b64decode(content).decode("utf-8", "replace")
    sys.exit("error: provide --export-file or --from-mcp-json for a sync")


# --- tab splitting ------------------------------------------------------------
def split_tabs(md, tab_order):
    """Return {tab_title: [lines]} by bounding each known tab title with the next
    known tab title. Content H1s that are not tab titles are ignored as boundaries."""
    lines = md.split("\n")
    titles = set(tab_order)

    def heading_title(line):
        # a tab title renders as "# ...", possibly with escaped punctuation
        s = line.strip()
        if not s.startswith("# "):
            return None
        t = _ESC.sub(r"\1", s[2:].strip())  # unescape before matching
        return t if t in titles else None

    bounds = [i for i, l in enumerate(lines) if heading_title(l) is not None]
    blocks = {}
    for idx, start in enumerate(bounds):
        title = heading_title(lines[start])
        end = bounds[idx + 1] if idx + 1 < len(bounds) else len(lines)
        blocks.setdefault(title, lines[start:end])
    return blocks


def sha(body):
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


# --- modes --------------------------------------------------------------------
def do_check(doc, modified_time):
    last = doc.get("last_modified_time")
    if last and modified_time and modified_time == last:
        print(f"OK  (unchanged since {doc.get('last_synced')})")
        return 0
    print(f"STALE  (manifest: {last!r}  drive: {modified_time!r})")
    return 3


def do_sync(doc, doc_id, md, modified_time, synced):
    blocks = split_tabs(md, doc["tab_order"])
    changed, current, missing = [], [], []
    for form in doc["forms"]:
        tab = form["tab"]
        if tab not in blocks:
            missing.append(tab)
            continue
        body = render_body(list(blocks[tab]), form.get("clip_start"), form.get("clip_end"))
        out = Path(form["out"])
        new_text = frontmatter(doc_id, doc["title"], form) + body
        old_text = out.read_text() if out.exists() else None
        if new_text != old_text:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(new_text)
            changed.append(form["out"])
        else:
            current.append(form["out"])
        form["sha256"] = sha(body)
    if modified_time:
        doc["last_modified_time"] = modified_time
    doc["last_synced"] = synced
    return changed, current, missing


def main():
    ap = argparse.ArgumentParser(description="Pull-only Google Doc tab sync.")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--doc-id", required=True)
    ap.add_argument("--modified-time", default="", help="Drive modifiedTime (RFC3339)")
    ap.add_argument("--check", action="store_true", help="freshness probe only")
    ap.add_argument("--from-mcp-json", help="path to download_file_content result JSON")
    ap.add_argument("--export-file", help="path to already-decoded markdown export")
    ap.add_argument("--synced-date", default=date.today().isoformat())
    args = ap.parse_args()

    mpath = Path(args.manifest)
    manifest = json.loads(mpath.read_text())
    doc = manifest.get("docs", {}).get(args.doc_id)
    if doc is None:
        sys.exit(f"error: doc {args.doc_id} not in {args.manifest}")

    if args.check:
        rc = do_check(doc, args.modified_time)
        if rc == 0:  # verified current today — stamp so the read-hook stops nudging
            doc["last_synced"] = args.synced_date
            mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        sys.exit(rc)

    md = load_export(args)
    changed, current, missing = do_sync(doc, args.doc_id, md, args.modified_time, args.synced_date)

    # `out` paths in the manifest are relative to the repo root; run from there.
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    print(f"synced doc {args.doc_id}  ({doc['title']})")
    for f in changed:
        print(f"  updated  {f}")
    for f in current:
        print(f"  current  {f}")
    for t in missing:
        print(f"  MISSING tab not found in export: {t!r} (renamed? fix tab_order/forms)")
    if missing:
        sys.exit(4)


if __name__ == "__main__":
    main()
