#!/usr/bin/env python3
"""chrome_export.py: the last few days of Chrome history, every profile, as JSON on stdout. Read-only.

Usage: chrome_export.py [--days 3]
publish runs it hourly and copies the result to the agent server
(/srv/agent-share/chrome-history/visits.json), where clerk's desk-links job files the pages Alejo
read into ~/best/systems/desk/links/. Each visit: t (local ISO time), url, title, dur (seconds, capped at
30 minutes), profile.
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sources import chrome_profiles, chrome_visits  # noqa: E402  (the skill's folder)


def visits(days):
    start = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    out = []
    for folder, name, _ in chrome_profiles():
        for t, dur, url, title in chrome_visits(folder, start):
            out.append({"t": t.isoformat(timespec="seconds"), "url": url, "title": title or "",
                        "dur": round(min(dur, 1800)), "profile": name})
    return sorted(out, key=lambda v: v["t"])


if __name__ == "__main__":
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 3
    json.dump({"generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "days": days,
               "visits": visits(days)}, sys.stdout, ensure_ascii=False)
