#!/usr/bin/env python3
"""Securely create the local config for the 80,000 Hours Slack skill."""

import getpass
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"
SLACK = SKILL_DIR / "scripts" / "slack.py"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/143.0.0.0 Safari/537.36"
)


def read_secret(label: str, prefix: str) -> str:
    value = getpass.getpass(f"{label} (hidden): ").strip()
    if not value.startswith(prefix):
        raise SystemExit(f"Expected a value beginning with {prefix}")
    return value


def write_private_json(path: Path, value: dict) -> None:
    fd, temporary_name = tempfile.mkstemp(prefix=".config-", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, indent=2)
            handle.write("\n")
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> None:
    config = {}
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open() as handle:
            config = json.load(handle)
        answer = input("Replace the existing 80000hours credentials? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            raise SystemExit("Kept the existing config.")

    xoxc = read_secret("xoxc token", "xoxc-")
    xoxd = read_secret("xoxd cookie", "xoxd-")
    user_agent = input("Chrome user agent [use default]: ").strip() or DEFAULT_USER_AGENT

    config.setdefault("workspaces", {})["80000hours"] = {
        "xoxc_token": xoxc,
        "xoxd_token": xoxd,
        "user_agent": user_agent,
    }
    config["default_workspace"] = "80000hours"
    config.setdefault("link_style", "app")
    write_private_json(CONFIG_PATH, config)

    result = subprocess.run([sys.executable, str(SLACK), "auth"], check=False)
    if result.returncode:
        raise SystemExit("Saved the config, but Slack authentication failed.")


if __name__ == "__main__":
    main()
