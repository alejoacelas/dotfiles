#!/usr/bin/env python3
"""
Granola transcript extraction utility.

Usage:
    python granola.py check             # Check for recent call or list 5 most recent
    python granola.py list [n]          # List the n most recent meetings (default: 20)
    python granola.py get <doc_id>      # Get transcript for a specific meeting
    python granola.py recent [n]        # Get transcript for nth most recent meeting (default: 1)

Transcripts are saved under the skill-local data/transcripts/ directory.
"""

import os
import sys
from pathlib import Path

import json
import re
import subprocess
from datetime import datetime, timezone

PUBLIC_API_BASE = "https://public-api.granola.ai/v1"
SKILL_DIR = Path(__file__).resolve().parent.parent
TRANSCRIPTS_DIR = SKILL_DIR / "data" / "transcripts"
RECENT_THRESHOLD_MINUTES = 30


def _read_api_key() -> str | None:
    """Return the Granola public API key, or None if not configured.

    Looks first at $GRANOLA_API_KEY, then a `GRANOLA_API_KEY=` line in a
    gitignored `.env` beside the skill. Keeping the key in `.env` means it never
    lands in the shell history or this session's transcript."""
    key = os.environ.get("GRANOLA_API_KEY")
    if key and key.strip():
        return key.strip()
    env_file = SKILL_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("GRANOLA_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'") or None
            # Tolerate a bare `grn_...` key pasted with no KEY= prefix.
            if line.startswith("grn_"):
                return line.strip('"').strip("'")
    return None


def public_get(path: str, params: dict | None = None) -> any:
    """GET an authenticated request against the public API (Bearer grn_ key)."""
    key = _read_api_key()
    if not key:
        print("Error: Set GRANOLA_API_KEY in the environment or the skill's .env file.",
              file=sys.stderr)
        sys.exit(1)
    args = [
        'curl', '-s', '--compressed', '-G', f'{PUBLIC_API_BASE}{path}',
        '-H', f'Authorization: Bearer {key}',
        '-H', 'Accept: application/json',
    ]
    for k, v in (params or {}).items():
        args += ['--data-urlencode', f'{k}={v}']

    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: API call failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON response: {result.stdout[:200]}", file=sys.stderr)
        sys.exit(1)

    # Public API surfaces failures as {"error": ...} or {"message": ...}.
    if isinstance(parsed, dict) and (parsed.get('error') or set(parsed.keys()) == {'message'}):
        msg = parsed.get('error') or parsed.get('message')
        hint = " (check GRANOLA_API_KEY in the skill's .env)" if 'key' in str(msg).lower() or 'auth' in str(msg).lower() else ""
        print(f"Error: Granola API: {msg}{hint}", file=sys.stderr)
        sys.exit(1)

    return parsed


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.replace('&', 'and')
    text = re.sub(r'[^a-z0-9]+', '-', text.lower())
    text = text.strip('-')
    return text[:50]


def parse_iso_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    ts = ts.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def _effective_timestamp(doc: dict) -> str:
    """Return the most recent activity timestamp for a doc.

    Granola pre-creates documents for recurring calendar events, so ``created_at``
    can point to when the series was first scheduled rather than when the call
    actually happened. ``updated_at`` tracks the most recent edit (including
    transcript ingestion), so it is a better proxy for "when did this meeting
    really take place".
    """
    return doc.get('updated_at') or doc.get('created_at') or ''


def get_recent_documents(limit: int = 5) -> list[dict]:
    """Fetch recent documents from the Granola API, sorted by most-recent activity.

    Note: the public API lists only notes whose AI summary + transcript exist
    server-side — a call still processing (or whose summary was never
    generated) is silently absent, even though the desktop app shows it.
    """
    # Public API: ordered by created_at desc, 30 per page; paginate until we
    # have `limit` notes, then re-sort by updated_at so a re-dated older call
    # surfaces at the top like the app does.
    notes: list[dict] = []
    cursor = None
    while len(notes) < limit:
        params = {'page_size': 30}
        if cursor:
            params['cursor'] = cursor
        resp = public_get('/notes', params)
        page = resp.get('notes', []) if isinstance(resp, dict) else []
        notes.extend(page)
        if not (isinstance(resp, dict) and resp.get('hasMore') and page):
            break
        cursor = resp.get('cursor')
    notes.sort(key=_effective_timestamp, reverse=True)
    return notes[:limit]


def check_recent():
    """
    Check if there's a recent call (within 30 minutes).

    If yes, output JSON indicating auto-summarise mode.
    If no, output a numbered list of the 5 most recent calls for selection.
    """
    docs = get_recent_documents(limit=5)

    if not docs:
        print("No meetings found.")
        return

    # Check if most recent meeting was active within threshold
    most_recent = docs[0]
    effective_ts = _effective_timestamp(most_recent)

    if effective_ts:
        meeting_time = parse_iso_timestamp(effective_ts)
        now = datetime.now(timezone.utc)
        minutes_ago = (now - meeting_time).total_seconds() / 60

        if minutes_ago <= RECENT_THRESHOLD_MINUTES:
            result = {
                'mode': 'auto',
                'id': most_recent['id'],
                'title': most_recent.get('title', 'Untitled'),
                'minutes_ago': round(minutes_ago, 1),
            }
            print(json.dumps(result))
            return

    # No recent call - show selection list
    result = {
        'mode': 'select',
        'meetings': [],
    }

    for i, doc in enumerate(docs, 1):
        effective = _effective_timestamp(doc)
        date_str = effective[:10] if effective else 'Unknown'
        result['meetings'].append({
            'number': i,
            'id': doc['id'],
            'title': doc.get('title', 'Untitled'),
            'date': date_str,
        })

    print(json.dumps(result))


def list_meetings(limit: int = 20):
    """List recent meetings."""
    docs = get_recent_documents(limit=limit)

    print(f"Found {len(docs)} recent meeting(s):\n")
    for i, doc in enumerate(docs, 1):
        effective = _effective_timestamp(doc)
        date_str = effective[:10] if effective else 'Unknown date'
        print(f"{i}. [{date_str}] {doc.get('title', 'Untitled')}")
        print(f"   ID: {doc['id']}")
        print()


def build_transcript(note_id: str) -> tuple[str, str, str]:
    """Build transcript markdown from the public API's single get-note call.

    ``GET /notes/{id}?include=transcript`` returns the note metadata and the
    transcript segments together. Each segment carries ``speaker.source``
    (``microphone`` = the account holder, ``speaker`` = system audio / everyone
    else), ``text`` and ``start_time``.
    """
    note = public_get(f'/notes/{note_id}', {'include': 'transcript'})
    if not isinstance(note, dict) or 'id' not in note:
        print(f"Error: Note not found: {note_id}", file=sys.stderr)
        sys.exit(1)

    title = note.get('title') or 'Untitled'
    effective = _effective_timestamp(note)
    date_str = effective[:10] if effective else 'unknown-date'

    segments = note.get('transcript') or []
    if not segments:
        print(f"Error: No transcript found for note ID: {note_id}", file=sys.stderr)
        sys.exit(1)

    segments.sort(key=lambda s: s.get('start_time', ''))

    lines = [f"# {title}", f"Date: {date_str}", ""]
    current_speaker = None
    current_text: list[str] = []

    for seg in segments:
        text = (seg.get('text') or '').strip()
        if not text:
            continue
        source = (seg.get('speaker') or {}).get('source', '')
        speaker = 'Me' if source == 'microphone' else 'Other'

        if speaker != current_speaker:
            if current_text:
                lines.append(f"**{current_speaker}**: {' '.join(current_text)}")
                lines.append("")
            current_speaker = speaker
            current_text = [text]
        else:
            current_text.append(text)

    if current_text:
        lines.append(f"**{current_speaker}**: {' '.join(current_text)}")

    return '\n'.join(lines), title, date_str


def get_transcript(doc_id: str):
    """Get and save the full transcript for a specific document."""
    markdown, title, date_str = build_transcript(doc_id)

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{date_str}-{slugify(title or 'untitled')}.md"
    filepath = TRANSCRIPTS_DIR / filename

    with open(filepath, 'w') as f:
        f.write(markdown)

    print(markdown)
    print(f"\n---\nTranscript saved to: {filepath}", file=sys.stderr)


def get_recent_transcript(n: int = 1):
    """Get transcript for the nth most recent meeting."""
    docs = get_recent_documents(limit=max(n, 5))

    if n < 1 or n > len(docs):
        print(f"Error: Only {len(docs)} meeting(s) available", file=sys.stderr)
        sys.exit(1)

    doc_id = docs[n - 1]['id']
    get_transcript(doc_id)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'check':
        check_recent()
    elif command == 'list':
        list_meetings(int(sys.argv[2]) if len(sys.argv) > 2 else 20)
    elif command == 'get':
        if len(sys.argv) < 3:
            print("Error: Document ID required", file=sys.stderr)
            sys.exit(1)
        get_transcript(sys.argv[2])
    elif command == 'recent':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        get_recent_transcript(n)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
