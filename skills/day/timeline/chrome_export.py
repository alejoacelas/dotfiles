#!/usr/bin/env python3
"""chrome_export.py: the last few days of Chrome history, every profile, as JSON on stdout. Read-only.

Usage: chrome_export.py [--days 3]
publish runs it hourly and copies the result to the agent server
(/srv/agent-share/chrome-history/visits.json), where clerk's desk-links job files the pages Alejo
read into ~/best/desk/links/. Each visit: t (local ISO time), url, title, dur (seconds, capped at
30 minutes), profile.
"""
import datetime as dt
import json
import os
import shutil
import sqlite3
import sys
import tempfile

CHROME = os.path.expanduser("~/Library/Application Support/Google/Chrome")
EPOCH = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)


def visits(days):
    try:
        info = json.load(open(os.path.join(CHROME, "Local State")))["profile"]["info_cache"]
    except (OSError, ValueError, KeyError):
        return []
    lo = int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days) - EPOCH).total_seconds() * 1e6)
    out = []
    for folder, meta in info.items():
        src = os.path.join(CHROME, folder, "History")
        if not os.path.exists(src):
            continue
        with tempfile.TemporaryDirectory() as tmp:  # Chrome locks the live file
            db = os.path.join(tmp, "History")
            shutil.copy(src, db)
            rows = sqlite3.connect(db).execute(
                "SELECT v.visit_time, v.visit_duration, u.url, u.title FROM visits v JOIN urls u ON u.id = v.url "
                "WHERE v.visit_time >= ? ORDER BY v.visit_time", (lo,)).fetchall()
        for when, dur, url, title in rows:
            t = (EPOCH + dt.timedelta(microseconds=when)).astimezone()
            out.append({"t": t.isoformat(timespec="seconds"), "url": url, "title": title or "",
                        "dur": round(min(dur / 1e6, 1800)), "profile": meta.get("name", folder)})
    return sorted(out, key=lambda v: v["t"])


if __name__ == "__main__":
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 3
    json.dump({"generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "days": days,
               "visits": visits(days)}, sys.stdout, ensure_ascii=False)
