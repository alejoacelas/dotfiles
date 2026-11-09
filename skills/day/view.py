#!/usr/bin/env python3
"""view.py: a local page showing activity.py's days, today and the ones before it.

Usage: view.py [--days N] [--no-open]   (default 7 days)
Writes ~/.local/share/day/index.html (private: it holds browsing and notes) and opens it.
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser("~/.local/share/day/index.html")


def day(n):
    r = subprocess.run([sys.executable, os.path.join(HERE, "activity.py"), f"-{n}", "--json"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        return {"date": f"-{n}", "error": r.stderr.strip()[-400:]}
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args()
    with ThreadPoolExecutor(max_workers=4) as pool:
        days = list(pool.map(day, range(a.days)))
    data = json.dumps(days, ensure_ascii=False).replace("</", "<\\/")
    with open(os.path.join(HERE, "view.html")) as f:
        page = f.read().replace("/*DATA*/[]", data)
    os.makedirs(os.path.dirname(OUT), mode=0o700, exist_ok=True)
    with open(OUT, "w") as f:
        f.write(page)
    os.chmod(OUT, 0o600)
    print(OUT)
    if not a.no_open:
        subprocess.run(["open", OUT])


if __name__ == "__main__":
    main()
