"""sources.py: readers shared by activity.py, timeline/collect.py and timeline/chrome_export.py. Read-only."""
import datetime as dt
import glob
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile

CHROME = os.path.expanduser("~/Library/Application Support/Google/Chrome")
DAYFLOW = os.path.expanduser("~/Library/Application Support/Dayflow/chunks.sqlite")
PRESENT = 300  # a Dayflow screenshot counts as "at the Mac" when the last keyboard or mouse input was this many seconds ago or less
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


def best_project(best, path):
    """The project under ~/best that `path` is in, named by its top folder and child: work/coaching,
    systems/projects/2026-11-22-claude-rotate, orgs/aim/2026-10-novah-demo, archive/x. Worktrees count
    as their main checkout. None outside ~/best."""
    path = re.split(r"/\.(?:claude/)?worktrees/", path)[0]
    if not path.startswith(best + "/"):
        return None
    parts = path[len(best) + 1:].split("/")
    if parts[0] == "orgs" or (len(parts) > 2 and parts[1] == "projects"):
        return "/".join(parts[:3])
    return "/".join(parts[:2])


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


def dayflow(start, end):
    """Dayflow's screen record between two datetimes, or None when Dayflow isn't installed. Dayflow screenshots the
    screen every 10 s, and every 15 minutes Claude turns the screenshots into observations (what was on screen,
    minute by minute) and timeline cards (a titled, categorised activity). Returns
    {"cards": [...], "observations": [...], "present": [(start, end) local datetimes when input was recent],
     "apps": [(start, end, app, window title) for the frontmost window, from the accessibility recorder, cut to `present`]}."""
    if not os.path.exists(DAYFLOW):
        return None
    lo, hi = int(start.timestamp()), int(end.timestamp())
    db = sqlite3.connect(f"file:{DAYFLOW}?mode=ro", uri=True)
    t = lambda ts: dt.datetime.fromtimestamp(ts).astimezone()
    cards = []
    for a, b, title, summ, detail, cat, sub, meta in db.execute(
            "SELECT start_ts, end_ts, title, summary, detailed_summary, category, subcategory, metadata FROM timeline_cards "
            "WHERE is_deleted = 0 AND batch_id IS NOT NULL AND end_ts > ? AND start_ts < ? ORDER BY start_ts", (lo, hi)):
        try:
            meta = json.loads(meta or "{}")
        except ValueError:
            meta = {}
        sites = meta.get("appSites") or {}
        cards.append({"start": t(a), "end": t(b), "title": title, "summary": summ or "", "detail": detail or "",
                      "category": cat, "subcategory": sub or "",
                      "apps": [x for x in (sites.get("primary"), sites.get("secondary")) if x],
                      "distractions": [{"title": d.get("title", ""), "summary": d.get("summary", ""), "start": d.get("startTime"),
                                        "end": d.get("endTime")} for d in meta.get("distractions") or []]})
    obs = [{"start": t(a), "end": t(b), "text": text} for a, b, text in db.execute(
        "SELECT start_ts, end_ts, observation FROM observations WHERE end_ts > ? AND start_ts < ? ORDER BY start_ts", (lo, hi))]
    present, gap = [], 30  # screenshots come every 10 s; a longer gap means recording stopped (sleep, lock, pause)
    for ts, idle in db.execute("SELECT captured_at, idle_seconds_at_capture FROM screenshots "
                               "WHERE captured_at >= ? AND captured_at < ? ORDER BY captured_at", (lo, hi)):
        if idle is None or idle > PRESENT:
            continue
        a = ts - idle  # the input happened `idle` seconds before the screenshot
        if present and a <= present[-1][1] + gap:
            present[-1][1] = max(present[-1][1], ts)
        else:
            present.append([a, ts])
    db.close()
    return {"cards": cards, "observations": obs, "present": [(t(a), t(b)) for a, b in present],
            "apps": app_stretches(start, end, present)}


def app_stretches(start, end, present):
    """Which app was in front, from the window events of Dayflow's accessibility recorder (one JSONL file per
    10 minutes). Only the app and window title are read; the recorder's screen text and typing stay out of the timeline."""
    root = os.path.join(os.path.dirname(DAYFLOW), "accessibility")
    lo, hi = start.timestamp(), end.timestamp()
    events = []
    day = start.date() - dt.timedelta(1)
    while day <= end.date():
        for path in sorted(glob.glob(os.path.join(root, day.isoformat(), "*.jsonl"))):
            for line in open(path, errors="replace"):
                try:
                    e = json.loads(line)
                    ts = dt.datetime.fromisoformat(e["time"].replace("Z", "+00:00")).timestamp()
                except (ValueError, KeyError):
                    continue
                if e.get("kind") == "window" and e.get("app"):
                    events.append((ts, e["app"], e.get("window") or ""))
                elif e.get("kind") == "session_start":
                    events.append((ts, None, ""))  # Dayflow restarted: the front app is unknown until the next switch
        day += dt.timedelta(1)
    events.sort()
    out, t = [], lambda ts: dt.datetime.fromtimestamp(ts).astimezone()
    for (a, app, win), (b, *_) in zip(events, events[1:] + [(min(hi, dt.datetime.now().timestamp()), None, "")]):
        if not app:
            continue
        for p0, p1 in present:  # only while keyboard or mouse input was recent
            x, y = max(a, p0, lo), min(b, p1, hi)
            if y - x >= 5:
                out.append((t(x), t(y), app, win))
    return out
