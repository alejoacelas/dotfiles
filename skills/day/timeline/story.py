#!/usr/bin/env python3
"""story.py: label one day's activity with topics and tasks, using Claude through the subscription (claude -p).

Usage: story.py RAW_JSON DAY [DAY...] [--force]
Reads the day from collect.py's output, builds one chronological stream (prompts, page visits, calls,
non-agent focus, commits), and asks Claude to group it into topics and tasks, assign every event,
and pick verbatim highlights. Writes ~/.local/share/day/timeline/story/DAY.json; skips a day whose
stream hasn't changed since its last story unless --force.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import subprocess
import sys

OUT = os.path.expanduser("~/.local/share/day/timeline/story")
KINDS = ["building", "calls", "comms", "admin", "learning", "personal", "leisure"]


def hm(m):
    return f"{int(m // 60):02d}:{int(m % 60):02d}"


def stream(day):
    """Events with short ids, in time order. Consecutive visits to one page within 10 minutes collapse into one."""
    ev = []
    for s in day["sessions"]:
        for i, p in enumerate(s["prompts"]):
            ev.append({"m": p["m"], "type": "prompt", "sid": s["id"], "pi": i, "session": s["title"],
                       "folder": s["project"], "text": p["text"]})
    last = None
    for v in day["visits"]:
        if last and last["title"] == v["title"] and v["m"] - last["m2"] <= 10:
            last["m2"], last["n"] = v["m"], last["n"] + 1
            continue
        last = {"m": v["m"], "m2": v["m"], "n": 1, "type": "page", "host": v["host"], "title": v["title"]}
        ev.append(last)
    for e in day["events"]:
        if e["kind"] != "sleep":
            ev.append({"m": e["a"], "m2": e["b"], "type": "call" if e["kind"] == "call" else "calendar",
                       "title": e["title"], "gist": (e.get("summary") or {}).get("gist", "")})
    for f in day["focus"]:
        if not f.get("session") and f["b"] - f["a"] >= 1:
            ev.append({"m": f["a"], "m2": f["b"], "type": "focus", "title": f["title"], "path": f["path"]})
    for c in day["commits"]:
        if not c["auto"]:
            ev.append({"m": c["m"], "type": "commit", "repo": c["repo"], "msg": c["msg"]})
    ev.sort(key=lambda e: e["m"])
    for i, e in enumerate(ev):
        e["id"] = f"{ {'prompt': 'p', 'page': 'w', 'call': 'c', 'calendar': 'k', 'focus': 'f', 'commit': 'g'}[e['type']]}{i}"
    return ev


def line(e):
    t = hm(e["m"])
    if e["type"] == "prompt":
        return f"{e['id']} {t} PROMPT [{e['folder'].split('/')[-1]} · {e['session'][:60]}] {e['text'][:420]}"
    if e["type"] == "page":
        span = f"–{hm(e['m2'])} ×{e['n']}" if e["n"] > 1 else ""
        return f"{e['id']} {t}{span} PAGE {e['host']} | {e['title'][:140]}"
    if e["type"] in ("call", "calendar"):
        return f"{e['id']} {t}–{hm(e['m2'])} {e['type'].upper()} {e['title']}" + (f" | summary: {e['gist'][:400]}" if e["gist"] else "")
    if e["type"] == "focus":
        return f"{e['id']} {t}–{hm(e['m2'])} FOCUS {e['title'][:80]} ({e['path'][-80:]})"
    return f"{e['id']} {t} COMMIT {e['repo'].split('/')[-1]}: {e['msg'][:160]}"


PROMPT = """You are reconstructing what one person did on {weekday}: where their attention went, in topics and tasks.

The stream below is everything recorded on their computer that day, in time order:
- PROMPT: a message they typed to a coding agent (Claude Code or Codex). [folder · session title] shows where the session ran; the folder is often NOT what the prompt is about, so judge by the words.
- PAGE: a Chrome page they opened (×N = reopened N times within minutes of each other). Page titles usually tell what the page served.
- CALL / CALENDAR: calendar events they attended, with a call summary when one was filed.
- FOCUS: time with a file or terminal focused in their terminal app, outside agent sessions.
- COMMIT: a commit their agents (or they) made. Commits show what agents produced; they are not the person's attention.

Their priorities for the day, from their planning page:
{priorities}

Group the day into:
1. topics: the 4–12 coherent pieces of work or life the day was about, named as the person would name them, with a short form of at most 14 characters (e.g. "Sharing prompts", "Call with Simon (CeSIA)", "Umi app", "Groceries and errands", "Social media"). A topic is defined by subject, never by folder or website. Give each a kind from {kinds}, the number of the priority it serves (or null), and one plain sentence saying what happened in it.
2. tasks: within each topic, the concrete things they worked on or got done (e.g. "Prepare for the Simon call", "Fix a missing calendar booking", "Make the work-map output docs readable"). Name each with a verb, as a to-do item would read. Give each task one sentence on its outcome as far as the stream shows it (done, left mid-way, or unclear), never inventing results.
3. assign every event id to exactly one task. Pages go to the task they served, judged by title and by what was happening around them; sign-in pages, redirects and other navigation join the surrounding task. Leisure and personal browsing get their own topics and tasks. Commits go to the task their message belongs to.
4. highlights: for each task, 1–4 event ids whose verbatim text best shows what that task was about: prefer the person's own prompts that state intent, a decision or feedback; then telling page titles or a call summary. Never pick a short command like "go", "status" or "yes".

Be faithful to the record. Do not merge unrelated work to make a neater story, and do not invent work that isn't in the stream.

STREAM ({n} events):
{stream}
"""

SCHEMA = {
    "type": "object", "required": ["topics", "tasks", "assign"],
    "properties": {
        "topics": {"type": "array", "items": {"type": "object", "required": ["id", "label", "short", "kind", "priority", "summary"], "properties": {
            "id": {"type": "string"}, "label": {"type": "string"}, "short": {"type": "string", "description": "the label in at most 14 characters"}, "kind": {"type": "string", "enum": KINDS},
            "priority": {"type": ["integer", "null"]}, "summary": {"type": "string"}}}},
        "tasks": {"type": "array", "items": {"type": "object", "required": ["id", "topic", "label", "outcome", "highlights"], "properties": {
            "id": {"type": "string"}, "topic": {"type": "string"}, "label": {"type": "string"}, "outcome": {"type": "string"},
            "highlights": {"type": "array", "items": {"type": "string"}}}}},
        "assign": {"type": "array", "description": "One entry per task: the task id and every event id assigned to it",
                   "items": {"type": "object", "required": ["task", "events"], "properties": {
                       "task": {"type": "string"}, "events": {"type": "array", "items": {"type": "string"}}}}},
    }}


def priorities(md):
    out, on = [], False
    for l in (md or "").splitlines():
        if l.lower().startswith("## current priorities"):
            on = True
            continue
        if on and l.startswith("## "):
            break
        if on and l.strip().lstrip("-*0123456789. ").strip():
            out.append(l.strip().lstrip("-* ").strip())
    return out


def tell(day, force=False):
    ev = stream(day)
    if not ev:
        return day["date"], "empty"
    pr = priorities(day["plans"])
    text = PROMPT.format(weekday=day["weekday"], kinds=", ".join(KINDS), n=len(ev),
                         priorities="\n".join(f"{i + 1}. {p.lstrip('0123456789. ')}" for i, p in enumerate(pr)) or "(none listed)",
                         stream="\n".join(line(e) for e in ev))
    digest = hashlib.sha256(text.encode()).hexdigest()[:16]
    path = os.path.join(OUT, f"{day['date']}.json")
    if not force and os.path.exists(path) and json.load(open(path)).get("digest") == digest:
        return day["date"], "unchanged"
    r = subprocess.run(["claude", "-p", "--model", "opus", "--output-format", "json", "--json-schema", json.dumps(SCHEMA),
                        "--disallowedTools", "Bash,Edit,Write,Read,Glob,Grep,WebFetch,WebSearch,Agent,NotebookEdit"],
                       input=text, capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        return day["date"], f"claude failed: {(r.stderr or r.stdout)[-300:]}"
    res = json.loads(r.stdout)
    story = res.get("structured_output") or json.loads(res["result"])
    ids = {e["id"] for e in ev}
    got = {x for a in story["assign"] for x in a["events"]}
    story.update({"digest": digest, "date": day["date"], "missing": sorted(ids - got), "unknown": sorted(got - ids),
                  "events": [{k: e[k] for k in ("id", "type", "m", "m2", "sid", "pi", "title", "repo", "msg", "text", "host", "gist", "session") if k in e} for e in ev]})
    os.makedirs(OUT, exist_ok=True)
    json.dump(story, open(path, "w"), ensure_ascii=False)
    return day["date"], f"{len(story['topics'])} topics, {len(story['tasks'])} tasks, {len(ids - got)} events unassigned"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    raw = json.load(open(args[0]))
    want = set(args[1:])
    days = [d for d in raw["days"] if not want or d["date"] in want]
    with cf.ThreadPoolExecutor(6) as pool:
        for date, msg in pool.map(lambda d: tell(d, "--force" in sys.argv), days):
            print(date, msg, flush=True)


if __name__ == "__main__":
    main()
