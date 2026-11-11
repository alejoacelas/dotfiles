#!/usr/bin/env python3
"""build.py: collect the last days and write the timeline pages, then open the timeline.

Usage: build.py [--days N] [--from YYYY-MM-DD] [--no-open] [--serve]
Writes index.html (the timeline) and choices.html (display alternatives) into ~/.local/share/day/timeline/.
--serve keeps a local server running so choices.html can save picks to answers.json beside it.
"""
import datetime as dt
import http.server
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser("~/.local/share/day/timeline")
PORT = 8781


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def page(template, data):
    html = open(os.path.join(HERE, template)).read()
    css, js = open(os.path.join(HERE, "timeline.css")).read(), open(os.path.join(HERE, "timeline.js")).read()
    blob = "const DATA = " + data.replace("</", "<\\/") + ";"
    return html.replace("/*CSS*/", css).replace("/*JS*/", js).replace("/*DATA*/", blob)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=OUT, **k)

    def do_POST(self):
        if self.path != "/answers":
            self.send_error(404)
            return
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        json.loads(body)  # refuse anything that isn't JSON
        with open(os.path.join(OUT, "answers.json"), "wb") as f:
            f.write(body)
        self.send_response(204)
        self.end_headers()

    def log_message(self, *a):
        pass


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--serve-only" not in sys.argv:
        last = dt.date.today()
        first = dt.date.fromisoformat(arg("--from")) if arg("--from") else last - dt.timedelta(int(arg("--days", 14)) - 1)
        raw = os.path.join(OUT, "raw.json")
        subprocess.run([sys.executable, os.path.join(HERE, "collect.py"), first.isoformat(), last.isoformat(), "--out", raw],
                       check=True)
        data = open(raw).read()
        for tpl in [t for t in ("index.html", "choices.html") if os.path.exists(os.path.join(HERE, t))]:
            open(os.path.join(OUT, tpl), "w").write(page(tpl, data))
        print(os.path.join(OUT, "index.html"))
    if "--serve" in sys.argv or "--serve-only" in sys.argv:
        print(f"http://127.0.0.1:{PORT}/choices.html")
        if "--no-open" not in sys.argv:
            subprocess.run(["open", f"http://127.0.0.1:{PORT}/index.html"])
        http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    elif "--no-open" not in sys.argv:
        subprocess.run(["open", os.path.join(OUT, "index.html")])


if __name__ == "__main__":
    main()
