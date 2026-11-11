#!/usr/bin/env python3
"""collect.py: raw, timestamped activity for a range of days, as JSON for the timeline page. Read-only.

Usage: collect.py FIRST_DAY [LAST_DAY] [--out FILE]   (days as YYYY-MM-DD or -N; LAST_DAY defaults to FIRST_DAY)
Per day: agent sessions with every prompt and when each agent turn ended, Umi focus stretches, commits
(marked when an automation committed them), Chrome visits, calendar events with their filed call
summaries, and the plans app's page. Times are local "HH:MM:SS"-free minutes since midnight (floats).
"""
import datetime as dt
import glob
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from collections import defaultdict
from urllib.parse import urlparse

HOME = os.path.expanduser("~")
BEST = os.path.join(HOME, "best")
CHROME = os.path.join(HOME, "Library/Application Support/Google/Chrome")
PLANS_HOST = "agent-server"
PLANS_DIR = "~/.local/share/daily-plans"
ACCOUNT = "alejoacelas@gmail.com"
ME = {"Alejandro Acelas", "Alejo Acelas"}  # committers that are Alejo's own sessions
TEMP = ("/tmp/", "/private/", "/var/folders/")


def parse_day(arg):
    if arg.startswith("-") and arg[1:].isdigit():
        return dt.date.today() - dt.timedelta(days=int(arg[1:]))
    return dt.date.fromisoformat(arg)


def local(ts):
    if isinstance(ts, (int, float)):
        return dt.datetime.fromtimestamp(ts).astimezone()
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()


def short(text, n=400):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def where(path):
    return path.replace(BEST + "/", "").replace(HOME, "~") if path else ""


def project(path):
    """The repository under ~/best holding `path` (worktrees count as their main repository), else its folder."""
    if not path:
        return ""
    if path.startswith(TEMP):
        return "(temporary)"
    if "/.claude/worktrees/" in path or "/.worktrees/" in path:
        path = re.split(r"/\.(?:claude/)?worktrees/", path)[0]
    d = path if os.path.isdir(path) else os.path.dirname(path)
    while d.startswith(BEST + "/"):
        if os.path.exists(os.path.join(d, ".git")):
            return d.replace(BEST + "/", "")
        d = os.path.dirname(d)
    return where(path) or path


class Days:
    def __init__(self, first, last):
        self.days = [first + dt.timedelta(n) for n in range((last - first).days + 1)]
        self.start = dt.datetime.combine(first, dt.time()).astimezone()
        self.end = dt.datetime.combine(last + dt.timedelta(1), dt.time()).astimezone()
        self.out = {d.isoformat(): {"date": d.isoformat(), "weekday": f"{d:%a %d %b %Y}", "sessions": [],
                                    "focus": [], "commits": [], "visits": [], "events": [], "calls": [],
                                    "scripted": defaultdict(int), "plans": ""} for d in self.days}

    def key(self, t):
        """(day key, minutes since that day's midnight) or (None, None) outside the range."""
        if not (self.start <= t < self.end):
            return None, None
        return t.date().isoformat(), t.hour * 60 + t.minute + t.second / 60

    def day(self, k):
        return self.out[k]


def is_noise(text):
    return not text.strip() or text.lstrip().startswith(
        ("<local-command", "<system-reminder", "<task-notification", "<bash-", "Caveat:", "# AGENTS.md",
         "<environment_context", "<user_instructions", "This session is being continued", "[Request interrupted"))


def add_session(D, s):
    """Split one session's prompts and turn ends by day."""
    s["prompts"].sort(key=lambda p: p["t"])
    acts = sorted(s["acts"])
    per = defaultdict(lambda: {"prompts": []})
    for i, p in enumerate(s["prompts"]):
        # a turn ends at its last agent activity before the next prompt or the first 10-minute silence
        nxt = s["prompts"][i + 1]["t"] if i + 1 < len(s["prompts"]) else None
        end = p["t"]
        for a in acts:
            if a < p["t"]:
                continue
            if (nxt and a >= nxt) or (a - end).total_seconds() > 600:
                break
            end = a
        k, m = D.key(p["t"])
        if not k:
            continue
        ek, em = D.key(end)
        per[k]["prompts"].append({"m": round(m, 2), "end": round(em if ek == k else 24 * 60, 2), "text": p["text"]})
    for k, v in per.items():
        D.day(k)["sessions"].append({"tool": s["tool"], "id": s["id"], "title": s["title"] or "(untitled)",
                                     "cwd": where(s["cwd"]), "project": project(s["cwd"]),
                                     "prompts": v["prompts"], "last_reply": s["last_reply"]})


def claude_sessions(D):
    for path in glob.glob(os.path.join(HOME, ".claude/projects/*/*.jsonl")):
        if os.path.getmtime(path) < D.start.timestamp():
            continue
        s = {"tool": "Claude", "id": os.path.basename(path)[:-6], "title": "", "cwd": "", "prompts": [], "acts": [],
             "last_reply": ""}
        scripted = False
        with open(path, errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") == "ai-title":
                    s["title"] = d.get("aiTitle", "")
                    continue
                if "timestamp" not in d or d.get("isSidechain"):
                    continue
                t = local(d["timestamp"])
                if d.get("entrypoint") == "sdk-cli":
                    scripted = True
                    k, _ = D.key(t)
                    if k:
                        cwd = d.get("cwd") or ""
                        D.day(k)["scripted"][project(cwd) if not cwd.startswith(TEMP) else "(temporary)"] += 1
                    break
                if d.get("type") == "assistant":
                    s["acts"].append(t)
                    msg = d.get("message", {}).get("content")
                    if isinstance(msg, list):
                        txt = " ".join(b.get("text", "") for b in msg if b.get("type") == "text")
                        if txt.strip() and D.start <= t < D.end:
                            s["last_reply"] = short(txt, 600)
                    continue
                if d.get("type") != "user":
                    continue
                s["acts"].append(t)
                if d.get("isMeta") or d.get("promptSource") == "system":
                    continue
                content = d.get("message", {}).get("content")
                if isinstance(content, list):
                    if any(b.get("type") == "tool_result" for b in content):
                        continue
                    content = " ".join(b.get("text", "") for b in content if b.get("type") == "text")
                if not isinstance(content, str) or is_noise(content):
                    continue
                if "<command-name>" in content:
                    content = content.split("<command-name>")[1].split("</command-name>")[0]
                s["cwd"] = s["cwd"] or d.get("cwd", "")
                s["prompts"].append({"t": t, "text": short(content)})
        if s["prompts"] and not scripted:
            add_session(D, s)


def codex_sessions(D):
    names = {}
    index = os.path.join(HOME, ".codex/session_index.jsonl")
    if os.path.exists(index):
        for line in open(index, errors="replace"):
            try:
                d = json.loads(line)
                names[d["id"]] = d.get("thread_name", "")
            except (ValueError, KeyError):
                pass
    paths = glob.glob(os.path.join(HOME, ".codex/sessions/*/*/*/*.jsonl"))
    paths += glob.glob(os.path.join(HOME, ".codex/archived_sessions/*.jsonl"))
    for path in paths:
        if os.path.getmtime(path) < D.start.timestamp():
            continue
        s = {"tool": "Codex", "id": "", "title": "", "cwd": "", "prompts": [], "acts": [], "last_reply": ""}
        with open(path, errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                p = d.get("payload") or {}
                if d.get("type") == "session_meta":
                    s["cwd"], s["id"] = p.get("cwd", ""), p.get("id", "")
                    s["title"] = names.get(s["id"], "")
                    continue
                if "timestamp" not in d:
                    continue
                t = local(d["timestamp"])
                if d.get("type") == "response_item":
                    s["acts"].append(t)
                    if p.get("type") == "message" and p.get("role") == "assistant" and D.start <= t < D.end:
                        txt = " ".join(c.get("text", "") for c in p.get("content", []) if isinstance(c, dict))
                        if txt.strip():
                            s["last_reply"] = short(txt, 600)
                    continue
                if d.get("type") != "event_msg":
                    continue
                if p.get("type") == "user_message":
                    text = p.get("message", "")
                else:
                    continue
                if is_noise(text):
                    continue
                s["prompts"].append({"t": t, "text": short(text)})
        if s["prompts"]:
            add_session(D, s)


def umi_focus(D):
    if not shutil.which("umi"):
        return "Umi isn't installed"
    try:
        r = subprocess.run(["umi", "focus-log", "--since", D.start.isoformat(), "--until", D.end.isoformat(), "--json"],
                           capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return "Umi didn't answer within 120 seconds"
    if r.returncode != 0:
        return short(r.stderr or r.stdout, 200)
    for st in json.loads(r.stdout).get("stretches", []):
        a, b = local(st["start_ts"]), local(st["end_ts"])
        k, m0 = D.key(a)
        if not k:
            continue
        k2, m1 = D.key(b)
        m1 = m1 if k2 == k else 24 * 60
        attrs = st.get("attributes", {})
        path = st.get("file") or attrs.get("file") or st.get("cwd") or ""
        D.day(k)["focus"].append({"a": round(m0, 2), "b": round(m1, 2), "kind": st.get("kind"),
                                  "session": (st.get("agent") or {}).get("session"),
                                  "title": short(st.get("title", ""), 120), "project": project(path),
                                  "path": where(path)})
    return None


def commits(D):
    repos = subprocess.run(["find", BEST, "-maxdepth", "6", "-name", ".git", "-type", "d", "-not", "-path",
                            "*/node_modules/*"], capture_output=True, text=True).stdout.split()
    seen = set()
    for git in sorted(repos):
        repo = os.path.dirname(git)
        log = subprocess.run(["git", "-C", repo, "log", "--all", "--no-merges", f"--since={D.start.isoformat()}",
                              f"--until={D.end.isoformat()}", "--format=@@%h|%ct|%cn|%s", "--shortstat"],
                             capture_output=True, text=True).stdout
        cur = None
        for line in log.splitlines():
            if line.startswith("@@"):
                h, ct, cn, subj = line[2:].split("|", 3)
                if h in seen:
                    cur = None
                    continue
                seen.add(h)
                k, m = D.key(local(int(ct)))
                cur = None
                if k:
                    cur = {"m": round(m, 2), "repo": repo.replace(BEST + "/", ""), "hash": h, "msg": short(subj, 200),
                           "auto": None if cn in ME else cn, "files": 0, "add": 0, "del": 0}
                    D.day(k)["commits"].append(cur)
            elif cur and "changed" in line:
                n = [int(x) for x in re.findall(r"(\d+) (?:files? changed|insertions?|deletions?)", line)]
                kinds = re.findall(r"(files? changed|insertion|deletion)", line)
                for v, kind in zip(n, kinds):
                    cur["files" if "file" in kind else "add" if kind == "insertion" else "del"] = v


def chrome(D):
    try:
        info = json.load(open(os.path.join(CHROME, "Local State")))["profile"]["info_cache"]
    except (OSError, ValueError, KeyError):
        return
    epoch = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)
    lo, hi = (int((x - epoch).total_seconds() * 1e6) for x in (D.start, D.end))
    for folder, meta in info.items():
        src = os.path.join(CHROME, folder, "History")
        if not os.path.exists(src):
            continue
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "History")
            shutil.copy(src, db)
            rows = sqlite3.connect(db).execute(
                "SELECT v.visit_time, v.visit_duration, u.url, u.title FROM visits v JOIN urls u ON u.id = v.url "
                "WHERE v.visit_time >= ? AND v.visit_time < ? ORDER BY v.visit_time", (lo, hi)).fetchall()
        for when, dur, url, title in rows:
            k, m = D.key((epoch + dt.timedelta(microseconds=when)).astimezone())
            if not k:
                continue
            host = (urlparse(url).hostname or url.split(":")[0]).removeprefix("www.")
            D.day(k)["visits"].append({"m": round(m, 2), "dur": round(min(dur / 6e7, 120), 2), "host": host,
                                       "title": short(title or url, 140), "profile": meta.get("name", folder)})


def calendar(D):
    try:
        r = subprocess.run(["gog", "calendar", "events", "--account", ACCOUNT, "--all", "--all-pages", "--max", "250",
                            "--from", D.start.isoformat(), "--to", D.end.isoformat(), "--json", "--results-only"],
                           capture_output=True, text=True, timeout=60)
        events = json.loads(r.stdout or "[]")
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError) as e:
        return f"calendar: {e}"
    for e in events:
        st, en = e.get("start", {}).get("dateTime"), e.get("end", {}).get("dateTime")
        if not st or e.get("status") == "cancelled":
            continue
        me = next((a for a in e.get("attendees", []) if a.get("self")), {})
        if me.get("responseStatus") == "declined":
            continue
        a, b = local(st), local(en)
        for day in D.days:  # an event can cross midnight (sleep)
            d0 = dt.datetime.combine(day, dt.time()).astimezone()
            lo, hi = max(a, d0), min(b, d0 + dt.timedelta(1))
            if lo >= hi:
                continue
            k = day.isoformat()
            D.day(k)["events"].append({
                "a": round((lo - d0).total_seconds() / 60, 2), "b": round((hi - d0).total_seconds() / 60, 2),
                "title": short(e.get("summary", ""), 120),
                "people": [x.get("email", "") for x in e.get("attendees", []) if not x.get("self")],
                "kind": "sleep" if e.get("summary", "").strip().lower() == "sleep" else
                        "call" if e.get("attendees") or e.get("conferenceData") else "block",
                "summary": None})
    return None


def call_summaries(D):
    """Filed call summaries in ~/best/desk, joined to that day's calendar event by a shared name."""
    for day in D.days:
        k = day.isoformat()
        for path in glob.glob(os.path.join(BEST, "desk", "**", f"{k}-*-sum.md"), recursive=True):
            text = open(path, errors="replace").read()
            fm = text.split("---", 2)[1] if text.startswith("---") else ""
            people = re.findall(r"[\w-]+", (re.search(r"^people:\s*\[(.*)\]", fm, re.M) or [None, ""])[1])
            gist = (re.search(r'^gist:\s*"?(.*?)"?\s*$', fm, re.M) or [None, ""])[1]
            link = (re.search(r"^link:\s*(\S+)", fm, re.M) or [None, ""])[1]
            title = (re.search(r"^#\s+(.*)$", text, re.M) or [None, os.path.basename(path)])[1]
            summ = {"title": short(title, 160), "gist": short(gist, 700), "link": link, "path": where(path),
                    "people": people}
            names = {w for p in people for w in p.split("-") if len(w) > 2}
            ev = next((e for e in D.day(k)["events"] if e["kind"] == "call" and not e["summary"] and
                       names & set(re.findall(r"[a-z]+", (e["title"] + " " + " ".join(e["people"])).lower()))), None)
            if ev:
                ev["summary"] = summ
            else:
                D.day(k)["calls"].append(summ)


def plans(D):
    keys = " ".join(d.isoformat() for d in D.days)
    cmd = (f"cd {PLANS_DIR} 2>/dev/null || exit 0; cur=$(grep -o '\"date\": *\"[0-9-]*\"' page.json | grep -o '[0-9-]\\{{10\\}}'); "
           f"for d in {keys}; do printf '\\n@@@%s\\n' \"$d\"; if [ \"$d\" = \"$cur\" ]; then cat page.md; "
           f"else cat days/$d.md 2>/dev/null; fi; done")
    try:
        r = subprocess.run(["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", PLANS_HOST, cmd],
                           capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return "plans: timed out"
    for part in r.stdout.split("\n@@@")[1:]:
        k, _, body = part.partition("\n")
        if k in D.out:
            D.day(k)["plans"] = body.strip()
    return None if r.returncode == 0 else f"plans: {short(r.stderr, 120)}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    if out in args:
        args.remove(out)
    first = parse_day(args[0]) if args else dt.date.today()
    last = parse_day(args[1]) if len(args) > 1 else first
    D = Days(first, last)
    errors = [umi_focus(D), calendar(D), plans(D)]
    claude_sessions(D)
    codex_sessions(D)
    commits(D)
    chrome(D)
    call_summaries(D)
    for d in D.out.values():
        d["sessions"].sort(key=lambda s: s["prompts"][0]["m"])
        for x in ("commits", "visits"):
            d[x].sort(key=lambda c: c["m"])
        d["focus"].sort(key=lambda f: f["a"])
        d["events"].sort(key=lambda e: e["a"])
        d["scripted"] = dict(d["scripted"])
    result = {"generated": dt.datetime.now().astimezone().isoformat(timespec="minutes"),
              "today": dt.date.today().isoformat(), "errors": [e for e in errors if e],
              "days": [D.out[d.isoformat()] for d in D.days]}
    text = json.dumps(result, ensure_ascii=False)
    if out:
        open(out, "w").write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
