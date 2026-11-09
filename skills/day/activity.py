#!/usr/bin/env python3
"""activity.py: what Alejo did on one day, as a markdown timeline. Read-only.

Usage: activity.py [YYYY-MM-DD | -N] [--json]   (default today; -1 is yesterday)
Umi's focus time, then per project (the repository under ~/best): agent sessions (Claude Code,
Codex) with their focus time and how they ended, other focus, commits. Then the plans app's day and
Chrome history for every profile. Prints markdown (or --json) to stdout and saves nothing.
"""
import datetime as dt
import glob
import json
import os
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


def parse_day(arg):
    today = dt.date.today()
    if not arg:
        return today
    if arg.startswith("-") and arg[1:].isdigit():
        return today - dt.timedelta(days=int(arg[1:]))
    return dt.date.fromisoformat(arg)


DAY = parse_day(next((a for a in sys.argv[1:] if a != "--json"), ""))
START = dt.datetime.combine(DAY, dt.time()).astimezone()
END = START + dt.timedelta(days=1)


def local(ts):
    """ISO timestamp (UTC 'Z') to local datetime."""
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()


def in_day(t):
    return START <= t < END


def short(text, n=240):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def touched_today(path):
    return os.path.getmtime(path) >= START.timestamp()


def where(cwd):
    return cwd.replace(BEST + "/", "").replace(HOME, "~") if cwd else "?"


def is_noise(text):
    return not text.strip() or text.lstrip().startswith(
        ("<local-command", "<system-reminder", "<task-notification", "<bash-", "Caveat:", "# AGENTS.md",
         "<environment_context", "<user_instructions", "This session is being continued"))


def claude_sessions():
    """Interactive sessions, plus a count of scripted `claude -p` runs per folder."""
    out, scripted = [], defaultdict(int)
    for path in glob.glob(os.path.join(HOME, ".claude/projects/*/*.jsonl")):
        if not touched_today(path):
            continue
        s = {"tool": "Claude", "id": os.path.basename(path)[:-6], "title": "", "cwd": "", "prompts": [],
             "first": None, "last": None}
        with open(path, errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") == "ai-title":
                    s["title"] = d.get("aiTitle", "")
                if d.get("type") != "user" or d.get("isSidechain") or d.get("isMeta") or d.get("promptSource") == "system":
                    continue
                if d.get("entrypoint") == "sdk-cli":
                    if in_day(local(d["timestamp"])):
                        cwd = d.get("cwd") or ""
                        if cwd.startswith(("/tmp/", "/private/", "/var/folders/")):
                            cwd = "/".join(cwd.split("/")[:4])  # one count per test harness
                        scripted[where(cwd)] += 1
                    break
                content = d.get("message", {}).get("content")
                if isinstance(content, list):
                    content = " ".join(b.get("text", "") for b in content if b.get("type") == "text")
                if not isinstance(content, str) or is_noise(content):
                    continue
                if "<command-name>" in content:  # a slash command
                    content = content.split("<command-name>")[1].split("</command-name>")[0]
                t = local(d["timestamp"])
                if not in_day(t):
                    continue
                s["cwd"] = s["cwd"] or d.get("cwd", "")  # where the session started
                s["prompts"].append(content)
                s["first"] = s["first"] or t
                s["last"] = t
        if s["prompts"]:
            out.append(s)
    return out, scripted


def codex_sessions():
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
    out = []
    for path in paths:
        if not touched_today(path):
            continue
        s = {"tool": "Codex", "id": "", "title": "", "cwd": "", "prompts": [], "first": None, "last": None}
        with open(path, errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                p = d.get("payload") or {}
                if d.get("type") == "session_meta":
                    s["cwd"] = p.get("cwd", "")
                    s["id"] = p.get("id", "")
                    s["title"] = names.get(p.get("id"), "")
                    continue
                if d.get("type") != "event_msg":
                    continue
                if p.get("type") == "item_completed" and p.get("item", {}).get("type") == "UserMessage":
                    text = " ".join(c.get("text", "") for c in p["item"].get("content", []) if c.get("type") == "text")
                elif p.get("type") == "user_message":
                    text = p.get("message", "")
                else:
                    continue
                t = local(d["timestamp"])
                if is_noise(text) or not in_day(t):
                    continue
                s["prompts"].append(text)
                s["first"] = s["first"] or t
                s["last"] = t
        if s["prompts"]:
            out.append(s)
    return out


def commits():
    repos = subprocess.run(
        ["find", BEST, "-maxdepth", "6", "-name", ".git", "-type", "d", "-not", "-path", "*/node_modules/*"],
        capture_output=True, text=True).stdout.split()
    out = []
    for git in sorted(repos):
        repo = os.path.dirname(git)
        log = subprocess.run(
            ["git", "-C", repo, "log", "--all", "--no-merges", "--date=format-local:%H:%M",
             f"--since={START.isoformat()}", f"--until={END.isoformat()}", "--format=%ad %s"],
            capture_output=True, text=True).stdout.strip()
        if log:
            out.append((repo.replace(BEST + "/", ""), sorted(log.splitlines())))
    return out


def plans():
    cmd = (f"cd {PLANS_DIR}/days 2>/dev/null || exit 0; "
           f"{{ grep -q '\"{DAY}\"' ../page.json 2>/dev/null && cat ../page.md; }} || cat {DAY}.md 2>/dev/null; for f in {DAY}/*.md; do [ -f \"$f\" ] && "
           f"printf '\\n## Tab: %s\\n' \"$(basename \"$f\" .md)\" && cat \"$f\"; done; true")
    try:
        r = subprocess.run(["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", PLANS_HOST, cmd],
                           capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else f"(unreachable: {short(r.stderr, 120)})"
    except subprocess.TimeoutExpired:
        return "(unreachable: timed out)"


def chrome():
    """Per profile: sites by time on page, each with its distinct page titles."""
    try:
        info = json.load(open(os.path.join(CHROME, "Local State")))["profile"]["info_cache"]
    except (OSError, ValueError, KeyError):
        return []
    epoch = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)
    lo = int((START - epoch).total_seconds() * 1e6)
    hi = int((END - epoch).total_seconds() * 1e6)
    out = []
    for folder, meta in info.items():
        src = os.path.join(CHROME, folder, "History")
        if not os.path.exists(src):
            continue
        with tempfile.TemporaryDirectory() as tmp:  # Chrome locks the live file
            db = os.path.join(tmp, "History")
            shutil.copy(src, db)
            rows = sqlite3.connect(db).execute(
                "SELECT v.visit_time, v.visit_duration, u.url, u.title FROM visits v "
                "JOIN urls u ON u.id = v.url WHERE v.visit_time >= ? AND v.visit_time < ? "
                "ORDER BY v.visit_time", (lo, hi)).fetchall()
        sites = defaultdict(lambda: {"visits": 0, "secs": 0, "first": None, "last": None, "titles": []})
        for when, dur, url, title in rows:
            host = urlparse(url).hostname or url.split(":")[0]
            host = host.removeprefix("www.")
            t = (epoch + dt.timedelta(microseconds=when)).astimezone()
            s = sites[host]
            s["visits"] += 1
            s["secs"] += min(dur / 1e6, 1800)  # cap tabs left open at 30 min a visit
            s["first"] = s["first"] or t
            s["last"] = t
            title = short(title or url, 90)
            if title not in s["titles"]:
                s["titles"].append(title)
        label = f"{meta.get('name', folder)} ({meta.get('user_name') or folder})"
        out.append((label, len(rows), sorted(sites.items(), key=lambda kv: -kv[1]["secs"])))
    return out


def umi_focus():
    """Umi's focus time for the day, summed per agent session, file, page or plain-terminal folder."""
    if not shutil.which("umi"):
        return {"error": "Umi isn't installed."}
    out = subprocess.run(["umi", "focus-log", "--since", START.isoformat(), "--until", END.isoformat(),
                          "--by", "session", "--json"], capture_output=True, text=True, timeout=20)
    if out.returncode != 0:  # Umi before focus-log --by
        return {"error": short(out.stderr or out.stdout, 200)}
    return json.loads(out.stdout)


def project(path):
    """The repository under ~/best holding `path` (worktrees count as their main repository), else its folder."""
    if not path:
        return "other"
    if path.startswith(("/tmp/", "/private/", "/var/folders/")):
        return TEMP
    d = path if os.path.isdir(path) else os.path.dirname(path)
    while d.startswith(BEST + "/"):
        if os.path.isdir(os.path.join(d, ".git")):
            return d.replace(BEST + "/", "")
        d = os.path.dirname(d)
    return where(path)


TEMP = "temporary folders"  # scripted tests and scratch runs: shown as a count


def hm(t):
    return f"{t:%H:%M}" if t else None


def build():
    """Everything the script finds for DAY, as one JSON-ready dict."""
    sessions, scripted = claude_sessions()
    sessions += codex_sessions()
    focus = umi_focus()
    groups = focus.get("groups", [])
    by_session = {g["agent"]["session"]: g for g in groups if g.get("agent", {}).get("session")}

    projects = defaultdict(lambda: {"focus_seconds": 0, "sessions": [], "focus": [], "commits": []})
    for s in sorted(sessions, key=lambda s: s["first"]):
        g = by_session.pop(s["id"], None)
        item = {"tool": s["tool"], "id": s["id"], "title": s["title"] or "(untitled)", "cwd": where(s["cwd"]),
                "first": hm(s["first"]), "last": hm(s["last"]), "prompt_count": len(s["prompts"]),
                "first_prompt": short(s["prompts"][0]), "last_prompt": short(s["prompts"][-1], 160),
                "focus_seconds": g["seconds"] if g else 0, "summary": (g or {}).get("summary")}
        p = projects[project(s["cwd"])]
        p["sessions"].append(item)
        p["focus_seconds"] += item["focus_seconds"]
    for g in groups:  # focus not matched to a session prompted that day
        if g.get("agent", {}).get("session") and g["agent"]["session"] not in by_session:
            continue
        p = projects[project(g.get("file") or g.get("cwd"))]
        p["focus"].append({"kind": g["agent"]["kind"] + " session" if g.get("agent") else g["kind"],
                           "label": g["label"], "seconds": g["seconds"], "summary": g.get("summary"),
                           "first": hm(local(g["first"])), "last": hm(local(g["last"]))})
        p["focus_seconds"] += g["seconds"]
    for repo, lines in commits():
        projects[repo]["commits"] = lines
    for p in projects.values():
        p["sessions"].sort(key=lambda s: -s["focus_seconds"])
    ordered = sorted(projects.items(), key=lambda kv: (-kv[1]["focus_seconds"], -len(kv[1]["sessions"]),
                                                          -len(kv[1]["commits"])))

    shape = None
    if "error" not in focus and focus.get("first"):
        shape = {"total_seconds": focus["total_seconds"], "first": hm(local(focus["first"])),
                 "last": hm(local(focus["last"])),
                 "breaks": [{"start": hm(local(b["start"])), "end": hm(local(b["end"])), "seconds": b["seconds"]}
                            for b in focus["breaks"]]}

    browsing = []
    for label, n, sites in chrome():
        browsing.append({"profile": label, "visits": n, "sites": [
            {"host": host, "visits": v["visits"], "minutes": round(v["secs"] / 60),
             "first": hm(v["first"]), "last": hm(v["last"]), "titles": v["titles"]} for host, v in sites]})

    return {"date": DAY.isoformat(), "weekday": f"{DAY:%a %d %b %Y}", "focus": shape,
            "focus_error": focus.get("error"),
            "projects": [{"name": name, **p} for name, p in ordered],
            "scripted_runs": dict(sorted(scripted.items(), key=lambda kv: -kv[1])),
            "plans": plans(), "chrome": browsing}


def mins(seconds):
    m = round(seconds / 60)
    return f"{m // 60}h{m % 60:02d}m" if m >= 60 else f"{m} min"


def render(d):
    print(f"# Activity for {d['weekday']}\n")
    f = d["focus"]
    if f:
        line = f"Umi focus: {mins(f['total_seconds'])}, {f['first']}–{f['last']}"
        if f["breaks"]:
            line += "; breaks " + ", ".join(f"{b['start']}–{b['end']}" for b in f["breaks"])
        print(line + ". Focus counts keyboard focus in Umi while Alejo was active in the last 3 minutes.\n")
    else:
        print(f"Umi focus: {d['focus_error'] or 'none recorded'}.\n")

    print("## By project\n")
    for p in d["projects"]:
        if p["name"] == TEMP:
            print(f"Sessions in temporary folders (scripted tests, scratch runs): {len(p['sessions'])}.\n")
            continue
        if not p["sessions"] and not p["commits"] and p["focus_seconds"] < 60:
            continue
        head = f"### `{p['name']}`"
        if p["focus_seconds"] >= 60:
            head += f": {mins(p['focus_seconds'])} focus"
        print(head + "\n")
        for s in p["sessions"]:
            focus = f", {mins(s['focus_seconds'])} focus" if s["focus_seconds"] >= 60 else ""
            n = s["prompt_count"]
            print(f"- {s['first']}–{s['last']} **{s['title']}** ({s['tool']}, `{s['cwd']}`, "
                  f"{n} prompt{'s' * (n != 1)}{focus})")
            print(f"  - {s['first_prompt']}")
            if n > 1:
                print(f"  - last: {s['last_prompt']}")
            if s["summary"]:
                print(f"  - ended with: {short(s['summary'], 200)}")
        for g in p["focus"]:
            if g["seconds"] >= 60:
                print(f"- {mins(g['seconds'])} focus on {g['kind']} {g['label']}, {g['first']}–{g['last']}")
        if p["commits"]:
            print(f"- {len(p['commits'])} commit{'s' * (len(p['commits']) != 1)}:")
            for line in p["commits"]:
                print(f"  - {line}")
        print()
    if d["scripted_runs"]:
        runs = ", ".join(f"{n} in `{k}`" for k, n in d["scripted_runs"].items())
        print(f"Scripted `claude -p` runs: {runs}.\n")

    print("## Plans app\n")
    print(d["plans"] or "No day file.")

    print("\n## Chrome history\n")
    print("Time is Chrome's visit duration, capped at 30 minutes a visit; background tabs inflate it.\n")
    for prof in d["chrome"]:
        print(f"### {prof['profile']}: {prof['visits']} visits\n")
        for s in prof["sites"]:
            titles = "; ".join(s["titles"][:4]) + (f"; +{len(s['titles']) - 4} more" if len(s["titles"]) > 4 else "")
            print(f"- {s['host']}: {s['visits']} visits, ~{s['minutes']} min, {s['first']}–{s['last']}. {titles}")
        print()


if __name__ == "__main__":
    data = build()
    print(json.dumps(data, ensure_ascii=False, indent=1)) if "--json" in sys.argv else render(data)
