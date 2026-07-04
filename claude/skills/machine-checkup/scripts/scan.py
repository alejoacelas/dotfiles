#!/usr/bin/env python3
"""Deterministic half of the machine checkup: gather the facts a scan needs, fast.

Read-only. Prints a markdown report to stdout; the skill (Claude) interprets it,
handles the fuzzy checks (instruction conflicts, promote-to-global), fixes the
reversible findings, and writes the report. Stdlib only.

Usage: scan.py [BASE]   # BASE defaults to ~/best
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
BASE = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else HOME / "best"

SECRET_RE = (
    r"gh[opsu]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
    r"xox[baprs]-[A-Za-z0-9-]+|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"(?i)(api_key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9/+_-]{16,}"
)
SECRET_IGNORE = re.compile(r"example|placeholder|your[-_]|red_?acted|xxx|\.env\.example|<[^>]+>", re.I)


def run(cmd, cwd=None, timeout=30):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return 1, "", ""


def find_repos(base):
    repos = []
    for root, dirs, _ in os.walk(base):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", "node_modules"}]
        if ".git" in os.listdir(root):
            repos.append(Path(root))
            dirs[:] = [d for d in dirs if d != ".git"]  # don't descend into .git, but keep nested repos
    return sorted(repos)


def repo_state(repo):
    _, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo)
    branch = branch.strip()
    _, dirty, _ = run(["git", "status", "--porcelain"], cwd=repo)
    dirty_n = len([l for l in dirty.splitlines() if l.strip()])
    code, up, _ = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=repo)
    _, remotes, _ = run(["git", "remote"], cwd=repo)
    has_remote = bool(remotes.strip())
    ahead = behind = 0
    no_upstream = False
    if code == 0 and up.strip():
        _, counts, _ = run(["git", "rev-list", "--left-right", "--count", "@{u}...HEAD"], cwd=repo)
        parts = counts.split()
        if len(parts) == 2:
            behind, ahead = int(parts[0]), int(parts[1])
    elif has_remote:
        no_upstream = True
    return {
        "path": str(repo.relative_to(HOME)) if repo.is_relative_to(HOME) else str(repo),
        "branch": branch, "dirty": dirty_n, "ahead": ahead, "behind": behind,
        "has_remote": has_remote, "no_upstream": no_upstream,
    }


def dangling_symlinks():
    out = []
    for d in [HOME, HOME / ".claude", HOME / ".codex"]:
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if p.is_symlink() and not p.exists():
                tgt = os.readlink(p)
                out.append((str(p).replace(str(HOME), "~"), tgt))
    return out


def instruction_files(base):
    # Only your authored tree. The global ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md
    # symlink into base/ai/dotfiles, so they're covered here; plugin caches and
    # job scratch under ~/.claude are noise and stay out.
    files = {}
    names = {"CLAUDE.md", "AGENTS.md"}
    skip = {".git", "node_modules", "__pycache__", ".venv"}
    for r, dirs, fs in os.walk(base):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in fs:
            if f in names:
                p = Path(r) / f
                real = p.resolve()
                try:
                    lines = len(real.read_text(errors="ignore").splitlines())
                except OSError:
                    lines = 0
                files[str(real)] = (str(p).replace(str(HOME), "~"), lines)
    return sorted(files.values())


def brew_drift():
    code, leaves, _ = run(["brew", "leaves", "--installed-on-request"])
    if code != 0:
        code, leaves, _ = run(["brew", "leaves"])
    if code != 0:
        return None
    installed = {l.strip() for l in leaves.splitlines() if l.strip()}
    bf = BASE / "machine" / "dotfiles" / "Brewfile"
    declared = set()
    if bf.exists():
        for line in bf.read_text().splitlines():
            m = re.match(r'\s*brew\s+"([^"]+)"', line)
            if m:
                declared.add(m.group(1).split("/")[-1])
    undeclared = sorted(n for n in installed if n.split("/")[-1] not in declared)
    return undeclared


def secret_hits(repos):
    hits = []
    for repo in repos:
        code, out, _ = run(["git", "grep", "-nIE", SECRET_RE], cwd=repo, timeout=45)
        if code != 0:
            continue
        for line in out.splitlines():
            if line and not SECRET_IGNORE.search(line):
                rel = str(repo.relative_to(HOME)) if repo.is_relative_to(HOME) else str(repo)
                hits.append(f"{rel}: {line[:160]}")
    return hits


def background_jobs():
    info = {}
    _, cron, _ = run(["crontab", "-l"])
    info["crontab"] = cron.strip() or "(none)"
    la = HOME / "Library" / "LaunchAgents"
    third = []
    if la.exists():
        for p in sorted(la.glob("*.plist")):
            third.append(p.name)
    info["user_launchagents"] = third
    return info


def auth_needs():
    p = HOME / ".claude" / "mcp-needs-auth-cache.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def main():
    print(f"# Machine checkup — raw scan\n\nBase: `{BASE}`\n")

    repos = find_repos(BASE)
    states = [repo_state(r) for r in repos]
    loose = [s for s in states if s["dirty"] or s["ahead"] or s["no_upstream"]]
    print("## Loose ends — repos needing attention\n")
    if not loose:
        print("All repos clean, pushed, and tracking a remote. ✅\n")
    else:
        for s in loose:
            flags = []
            if s["dirty"]:
                flags.append(f"{s['dirty']} uncommitted")
            if s["ahead"]:
                flags.append(f"{s['ahead']} unpushed")
            if s["behind"]:
                flags.append(f"{s['behind']} behind")
            if s["no_upstream"]:
                flags.append("no upstream set")
            if not s["has_remote"]:
                flags.append("no remote (unpublished)")
            print(f"- `{s['path']}` ({s['branch']}): {', '.join(flags)}")
        print()
    unpublished = [s for s in states if not s["has_remote"]]
    if unpublished:
        print("Repos with no remote at all (candidates to publish or intentional-local):")
        for s in unpublished:
            print(f"- `{s['path']}`")
        print()

    print("## Dangling symlinks\n")
    dang = dangling_symlinks()
    if not dang:
        print("None. ✅\n")
    else:
        for path, tgt in dang:
            print(f"- `{path}` → `{tgt}` (target missing)")
        print()

    print("## Secret-pattern hits in tracked files\n")
    hits = secret_hits(repos)
    if not hits:
        print("None. ✅\n")
    else:
        print("⚠️ Review each — could be a real credential or a false positive:")
        for h in hits[:40]:
            print(f"- {h}")
        print()

    print("## Instruction files (for conflict / duplication review)\n")
    print("Compare these for contradictions, duplication, and drift:\n")
    for path, lines in instruction_files(BASE):
        print(f"- `{path}` — {lines} lines")
    print()

    print("## Homebrew drift\n")
    drift = brew_drift()
    if drift is None:
        print("(brew not available)\n")
    elif not drift:
        print("Brewfile matches installed leaves. ✅\n")
    else:
        print("Installed but not in Brewfile:")
        for d in drift:
            print(f"- `{d}`")
        print()

    print("## What's running / scheduled\n")
    bg = background_jobs()
    print(f"- crontab: {bg['crontab'] if bg['crontab']=='(none)' else 'HAS ENTRIES (see below)'}")
    if bg["crontab"] != "(none)":
        for line in bg["crontab"].splitlines():
            print(f"    {line}")
    print(f"- user LaunchAgents: {', '.join(bg['user_launchagents']) or '(none)'}")
    auth = auth_needs()
    if auth:
        print(f"- MCP connectors flagged for re-auth: {json.dumps(auth)}")
    print()

    print("---\nRaw scan complete. Now interpret, fix the reversible, and write the report.")


if __name__ == "__main__":
    main()
