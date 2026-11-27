"""focus.py: read where Alejo's keyboard focus was in BB, for activity.py and timeline/collect.py.

The Later plugin (~/best/systems/bb-plugin) writes the log: one "view" line whenever what a BB window shows
changes, repeated every minute while it stays the same. Umi and Umi Next kept their own focus logs until
they were retired on 27 Nov 2026; those days have no focus here.
"""
import datetime as dt
import json
import os

BB_LOG = os.path.expanduser("~/.local/share/bb-later/activity.jsonl")
BB_VIEW_CAP = 90  # seconds one "view" line can stand for: the repeat is 60 s apart
BREAK_SECONDS = 30 * 60


def _spans(since, until):
    """Each stretch of BB focus between two datetimes, oldest first: (start, end, the view line)."""
    if not os.path.exists(BB_LOG):
        return []
    windows = {}
    with open(BB_LOG) as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") == "view" and e.get("at"):
                windows.setdefault(e.get("window"), []).append((_t(e["at"]), e))
    # A view line counts from its time to the window's next one, while the window was in front, Alejo
    # had typed or clicked recently ("active") and it showed a thread.
    spans = []
    for views in windows.values():
        views.sort(key=lambda v: v[0])
        for (at, e), (nxt, _) in zip(views, views[1:]):
            end = min(nxt, at + dt.timedelta(seconds=BB_VIEW_CAP), until)
            start = max(at, since)
            if e.get("active") and e.get("threadId") and start < end:
                spans.append((start, end, e))
    spans.sort(key=lambda s: s[0])
    return spans


def stretches(since, until):
    """The same stretches as dicts, for the day timeline."""
    return [{"start_ts": a.timestamp(), "end_ts": b.timestamp(), "kind": "BB thread", "title": e.get("title") or "",
             "cwd": e.get("cwd"), "thread": e.get("threadId")} for a, b, e in _spans(since, until)]


def by_session(since, until):
    """The day's BB focus by thread: total seconds, first and last focus, breaks of 30 minutes or more, and
    one group per thread, largest first."""
    spans = _spans(since, until)
    out = {"total_seconds": 0, "groups": [], "breaks": []}
    if not spans:
        return out
    groups, last_thread, last_end = {}, None, None
    for start, end, e in spans:
        if last_end and (start - last_end).total_seconds() >= BREAK_SECONDS:
            out["breaks"].append({"start": _iso(last_end), "end": _iso(start),
                                  "seconds": round((start - last_end).total_seconds())})
        g = groups.setdefault(e["threadId"], {"key": "bb:" + e["threadId"], "kind": "BB thread", "seconds": 0,
                                              "stretches": 0, "first": _iso(start)})
        g["seconds"] += (end - start).total_seconds()
        g["stretches"] += e["threadId"] != last_thread or (start - last_end).total_seconds() > 1
        g["last"], g["label"], g["cwd"] = _iso(end), e.get("title") or e["threadId"], e.get("cwd")
        last_thread, last_end = e["threadId"], max(last_end or end, end)
    for g in groups.values():
        g["seconds"] = round(g["seconds"])
    out["groups"] = sorted(groups.values(), key=lambda g: -g["seconds"])
    out["total_seconds"] = sum(g["seconds"] for g in out["groups"])
    out["first"], out["last"] = _iso(spans[0][0]), _iso(max(s[1] for s in spans))
    return out


def _t(iso):
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _iso(t):
    return t.astimezone(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
