#!/usr/bin/env python3
"""activity.py: what Alejo did on one day, as a markdown timeline. Read-only.

Usage: activity.py [YYYY-MM-DD | -N]   (default today; -1 is yesterday)
Sections: agent sessions (Claude Code, Codex), commits in ~/best, plans app day,
Chrome history for every profile. Prints to stdout and saves nothing.
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


DAY = parse_day(sys.argv[1] if len(sys.argv) > 1 else "")
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


def print_sessions(sessions):
    for s in sorted(sessions, key=lambda s: s["first"]):
        n = len(s["prompts"])
        print(f"- {s['first']:%H:%M}–{s['last']:%H:%M} **{s['title'] or '(untitled)'}** "
              f"({s['tool']}, `{where(s['cwd'])}`, {n} prompt{'s' * (n != 1)})")
        print(f"  - {short(s['prompts'][0])}")
        if n > 1:
            print(f"  - last: {short(s['prompts'][-1], 160)}")


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
        s = {"tool": "Claude", "title": "", "cwd": "", "prompts": [], "first": None, "last": None}
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
                        scripted[where(d.get("cwd"))] += 1
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
        s = {"tool": "Codex", "title": "", "cwd": "", "prompts": [], "first": None, "last": None}
        with open(path, errors="replace") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                p = d.get("payload") or {}
                if d.get("type") == "session_meta":
                    s["cwd"] = p.get("cwd", "")
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
        ["find", BEST, "-maxdepth", "6", "-name", ".git", "-not", "-path", "*/node_modules/*"],
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
           f"cat {DAY}.md 2>/dev/null; for f in {DAY}/*.md; do [ -f \"$f\" ] && "
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


def main():
    print(f"# Activity for {DAY:%a %d %b %Y}\n")

    print("## Agent sessions\n")
    sessions, scripted = claude_sessions()
    sessions += codex_sessions()
    print_sessions(sessions) if sessions else print("None.")
    if scripted:
        runs = ", ".join(f"{n} in `{d}`" for d, n in sorted(scripted.items(), key=lambda kv: -kv[1]))
        print(f"\nScripted `claude -p` runs: {runs}.")

    print("\n## Commits\n")
    found = commits()
    for repo, lines in found:
        print(f"- `{repo}`")
        for line in lines:
            print(f"  - {line}")
    if not found:
        print("None.")

    print("\n## Plans app\n")
    print(plans() or "No day file.")

    print("\n## Chrome history\n")
    print("Time is Chrome's visit duration, capped at 30 minutes a visit; background tabs inflate it.\n")
    for label, n, sites in chrome():
        print(f"### {label}: {n} visits\n")
        for host, s in sites:
            mins = round(s["secs"] / 60)
            titles = "; ".join(s["titles"][:4]) + (f"; +{len(s['titles']) - 4} more" if len(s["titles"]) > 4 else "")
            print(f"- {host}: {s['visits']} visits, ~{mins} min, {s['first']:%H:%M}–{s['last']:%H:%M}. {titles}")
        print()


if __name__ == "__main__":
    main()
