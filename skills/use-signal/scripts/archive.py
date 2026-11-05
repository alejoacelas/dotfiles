#!/usr/bin/env python3
"""Print messages from the Signal archive copied from the agent server.

  archive.py                      # every message, oldest first
  archive.py --chat Lydia         # one person (name or number) or group (name or id)
  archive.py --since 2026-11-03 --json
"""
import argparse, datetime, glob, json, os

ARCHIVE = os.path.expanduser("~/.local/share/signal-archive")

def envelopes():
    for path in sorted(glob.glob(f"{ARCHIVE}/messages-*.jsonl")):
        with open(path) as f:
            for line in f:
                yield json.loads(line)["envelope"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chat")
    p.add_argument("--since", help="YYYY-MM-DD, local time")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    since = datetime.datetime.fromisoformat(a.since).timestamp() * 1000 if a.since else 0

    envs = list(envelopes())
    names = {e["sourceNumber"]: e["sourceName"] for e in envs if e.get("sourceNumber") and e.get("sourceName")}
    rows = []
    for e in envs:
        dm, sent = e.get("dataMessage"), (e.get("syncMessage") or {}).get("sentMessage")
        if dm:
            msg, frm = dm, e.get("sourceName") or e.get("sourceNumber")
            peer = e.get("sourceNumber")
        elif sent:
            msg, frm = sent, "Alejo"
            peer = sent.get("destinationNumber")
        else:
            continue  # receipts, typing, read markers
        group = (msg.get("groupInfo") or {})
        chat = group.get("groupName") or group.get("groupId") or names.get(peer, peer)
        text = msg.get("message")
        if not text:
            if msg.get("reaction"):
                text = f"[reacted {msg['reaction']['emoji']}]"
            elif msg.get("attachments"):
                text = f"[{len(msg['attachments'])} attachment(s)]"
            else:
                continue
        ts = msg.get("timestamp") or e["timestamp"]
        if ts < since:
            continue
        if a.chat and a.chat.lower() not in " ".join(str(x) for x in (chat, peer, group.get("groupId"))).lower():
            continue
        rows.append({"time": datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M"),
                     "chat": chat, "from": frm, "text": text})
    rows.sort(key=lambda r: r["time"])
    for r in rows:
        print(json.dumps(r, ensure_ascii=False) if a.json else f"{r['time']} | {r['chat']} | {r['from']}: {r['text']}")

main()
