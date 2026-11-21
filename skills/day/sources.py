"""sources.py: readers shared by activity.py, timeline/collect.py and timeline/chrome_export.py. Read-only."""
import datetime as dt
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile

CHROME = os.path.expanduser("~/Library/Application Support/Google/Chrome")
EPOCH = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)  # Chrome's clock starts here


def chrome_profiles():
    """(folder, profile name, account) for every Chrome profile with a history file."""
    try:
        info = json.load(open(os.path.join(CHROME, "Local State")))["profile"]["info_cache"]
    except (OSError, ValueError, KeyError):
        return []
    return [(folder, meta.get("name", folder), meta.get("user_name") or folder) for folder, meta in info.items()
            if os.path.exists(os.path.join(CHROME, folder, "History"))]


def chrome_visits(folder, start, end=None):
    """One profile's visits from `start` (and before `end`), oldest first, as
    (local datetime, seconds on page, url, title)."""
    lo = int((start - EPOCH).total_seconds() * 1e6)
    hi = int((end - EPOCH).total_seconds() * 1e6) if end else 2 ** 63 - 1
    with tempfile.TemporaryDirectory() as tmp:  # Chrome locks the live file
        db = os.path.join(tmp, "History")
        shutil.copy(os.path.join(CHROME, folder, "History"), db)
        rows = sqlite3.connect(db).execute(
            "SELECT v.visit_time, v.visit_duration, u.url, u.title FROM visits v JOIN urls u ON u.id = v.url "
            "WHERE v.visit_time >= ? AND v.visit_time < ? ORDER BY v.visit_time", (lo, hi)).fetchall()
    return [((EPOCH + dt.timedelta(microseconds=when)).astimezone(), dur / 1e6, url, title) for when, dur, url, title in rows]


def is_noise(text):
    """Agent prompts that are harness output rather than something Alejo typed."""
    return not text.strip() or text.lstrip().startswith(
        ("<local-command", "<system-reminder", "<task-notification", "<bash-", "Caveat:", "# AGENTS.md",
         "<environment_context", "<user_instructions", "This session is being continued", "[Request interrupted"))


def git_repos(best):
    """Every git repository under ~/best, sorted."""
    out = subprocess.run(["find", best, "-maxdepth", "6", "-name", ".git", "-type", "d", "-not", "-path",
                          "*/node_modules/*"], capture_output=True, text=True).stdout.split()
    return [os.path.dirname(g) for g in sorted(out)]
