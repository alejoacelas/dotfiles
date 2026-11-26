"""focus.py: read the focus logs of Umi, Umi Next and BB, for activity.py and timeline/collect.py.

Both apps write the same log format. `umi-next focus-log` reads either app's log when pointed at that
app's state directory, so Umi's log stays readable after Umi is quit (`umi focus-log` needs Umi running).
"""
import datetime as dt
import glob
import json
import os
import shutil
import subprocess

# BB's log is written by the Later plugin (~/best/systems/bb-plugin): one "view" line whenever what a
# window shows changes, repeated every minute while it stays the same.
BB_LOG = os.path.expanduser("~/.local/share/bb-later/activity.jsonl")
BB_VIEW_CAP = 90  # seconds one "view" line can stand for: the repeat is 60 s apart
SUPPORT = os.path.expanduser("~/Library/Application Support")
APPS = {"Umi": os.path.join(SUPPORT, "Umi"), "Umi Next": os.path.join(SUPPORT, "Umi-next")}
RETIRE_AFTER_DAYS = 7
BREAK_SECONDS = 30 * 60  # the apps' own threshold for a break


def read(app, since, until, by_session=False):
    """`focus-log --json` for one app between two datetimes: a dict, None when the app has no log, or
    {"error": ...}."""
    if not glob.glob(os.path.join(APPS[app], "logs/focus/*.jsonl")):
        return None
    if not shutil.which("umi-next"):
        return {"error": "umi-next isn't installed, so the focus logs can't be read"}
    # Panes inside either app export their own state directory; drop it so each read hits the app named.
    env = {k: v for k, v in os.environ.items() if k not in ("UMI_STATE_DIR", "UMI_NEXT_STATE_DIR")}
    env["UMI_NEXT_STATE_DIR"] = APPS[app]
    cmd = ["umi-next", "focus-log", "--since", since.isoformat(), "--until", until.isoformat(), "--json"]
    try:
        r = subprocess.run(cmd + (["--by", "session"] if by_session else []), capture_output=True, text=True,
                           timeout=120, env=env)
    except subprocess.TimeoutExpired:
        return {"error": f"{app}'s focus log didn't load within 120 seconds"}
    if r.returncode != 0:
        return {"error": f"{app}: " + (r.stderr or r.stdout).strip()[:200]}
    return json.loads(r.stdout)


def bb(since, until):
    """BB's focus between two datetimes, in the shape of `focus-log --by session`: None without a log."""
    if not os.path.exists(BB_LOG):
        return None
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
    out = {"by": "session", "total_seconds": 0, "groups": [], "breaks": []}
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


def by_session(since, until):
    """Both apps' `focus-log --by session`, merged into one day: one total, first and last focus and breaks
    across both (one person's attention), and every group from either app tagged with its "app"."""
    logs, errors = {}, []
    for app in APPS:
        d = read(app, since, until, by_session=True)
        if d and "error" in d:
            errors.append(d["error"])
        elif d and d.get("first"):
            logs[app] = d
    d = bb(since, until)
    if d and d.get("first"):
        logs["BB"] = d
    out = {"total_seconds": sum(d["total_seconds"] for d in logs.values()),
           "seconds_by_app": {app: d["total_seconds"] for app, d in logs.items()},
           "groups": [{**g, "app": app} for app, d in logs.items() for g in d["groups"]],
           "breaks": [], "errors": errors}
    if not logs:
        return out
    first, last = min(_t(d["first"]) for d in logs.values()), max(_t(d["last"]) for d in logs.values())
    out["first"], out["last"] = _iso(first), _iso(last)
    # A break is a stretch of 30 minutes or more inside [first, last] with no focus in either app: the
    # intersection of each app's idle time (its breaks, and before its first or after its last focus).
    idle = [(first, last)]
    for d in logs.values():
        own = [(dt.datetime.min.replace(tzinfo=dt.timezone.utc), _t(d["first"]))]
        own += [(_t(b["start"]), _t(b["end"])) for b in d["breaks"]]
        own.append((_t(d["last"]), dt.datetime.max.replace(tzinfo=dt.timezone.utc)))
        idle = [(max(a, c), min(b, e)) for a, b in idle for c, e in own if max(a, c) < min(b, e)]
    out["breaks"] = [{"start": _iso(a), "end": _iso(b), "seconds": round((b - a).total_seconds())}
                     for a, b in sorted(idle) if (b - a).total_seconds() >= BREAK_SECONDS]
    return out


def umi_unused_seconds():
    """Seconds since Umi last logged focus, while Umi is still installed and its log exists; else None."""
    if not (shutil.which("umi") or os.path.exists("/Applications/Umi.app")):
        return None
    files = sorted(glob.glob(os.path.join(APPS["Umi"], "logs/focus/*.jsonl")))
    for path in reversed(files):
        with open(path) as f:
            lines = [l for l in f.read().splitlines() if l.strip()]
        for line in reversed(lines):
            try:
                end = json.loads(line)["end_ts"]
            except (ValueError, KeyError):
                continue
            return dt.datetime.now().timestamp() - end
    return None


def retire_note():
    age = umi_unused_seconds()
    if age is not None and age > RETIRE_AFTER_DAYS * 86400:
        return f"Umi unused for {int(age // 86400)} days: retire it?"
    return None
