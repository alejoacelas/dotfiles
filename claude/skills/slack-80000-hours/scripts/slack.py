#!/usr/bin/env python3
"""Minimal Slack web-session client pinned to the 80,000 Hours workspace."""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"
WORKSPACE = "80000hours"
EXPECTED_TEAM_ID = "T02GR4NPU"
EXPECTED_TEAM = "80,000 Hours"
EXPECTED_URL = "https://80000hours.slack.com/"
API_ROOT = "https://slack.com/api/"


class SlackError(RuntimeError):
    pass


def load_config() -> tuple[dict, dict]:
    if not CONFIG_PATH.exists():
        raise SlackError(f"Missing config: run {SKILL_DIR / 'scripts' / 'setup.py'}")
    with CONFIG_PATH.open() as handle:
        config = json.load(handle)
    credentials = config.get("workspaces", {}).get(WORKSPACE)
    if not credentials:
        raise SlackError(f"Config has no {WORKSPACE!r} workspace")
    for key, prefix in (("xoxc_token", "xoxc-"), ("xoxd_token", "xoxd-")):
        if not str(credentials.get(key, "")).startswith(prefix):
            raise SlackError(f"Invalid {key}: expected a value beginning with {prefix}")
    return config, credentials


class SlackClient:
    def __init__(self, credentials: dict):
        self.token = credentials["xoxc_token"]
        self.cookie = credentials["xoxd_token"]
        self.user_agent = credentials.get("user_agent") or "Mozilla/5.0"

    def call(self, endpoint: str, **data) -> dict:
        payload = urllib.parse.urlencode(
            {
                "token": self.token,
                "_x_reason": "api-call",
                "_x_mode": "online",
                "_x_sonic": "true",
                "_x_app_name": "client",
                **{key: str(value) for key, value in data.items() if value is not None},
            }
        ).encode()
        request = urllib.request.Request(
            API_ROOT + endpoint,
            data=payload,
            headers={
                "Cookie": f"d={self.cookie}",
                "User-Agent": self.user_agent,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            raise SlackError(f"Slack HTTP error {error.code}") from error
        except urllib.error.URLError as error:
            raise SlackError(f"Could not reach Slack: {error.reason}") from error
        except json.JSONDecodeError as error:
            raise SlackError("Slack returned a non-JSON response") from error
        if not result.get("ok"):
            raise SlackError(f"Slack API error: {result.get('error', 'unknown_error')}")
        return result

    def collect(self, endpoint: str, result_key: str, **data) -> dict:
        items = []
        cursor = ""
        while True:
            result = self.call(endpoint, cursor=cursor, **data)
            items.extend(result.get(result_key, []))
            cursor = result.get("response_metadata", {}).get("next_cursor", "")
            if not cursor:
                return {"ok": True, result_key: items}


def output(value) -> None:
    json.dump(value, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def usage() -> str:
    return """Usage: slack.py COMMAND [ARGS]

Commands:
  auth
  channels [types]
  users
  user-lookup
  history CHANNEL_ID [limit]
  replies CHANNEL_ID THREAD_TS
  search QUERY [count]
  permalink CHANNEL_ID MESSAGE_TS
  send CHANNEL_ID MESSAGE [THREAD_TS]
"""


def require_args(args: list[str], minimum: int, command_usage: str) -> None:
    if len(args) < minimum:
        raise SlackError(f"Usage: slack.py {command_usage}")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help", "help"}:
        print(usage())
        return

    config, credentials = load_config()
    client = SlackClient(credentials)
    command, args = sys.argv[1], sys.argv[2:]

    if command == "auth":
        result = client.call("auth.test")
        identity = (result.get("team_id"), result.get("team"), result.get("url"))
        expected = (EXPECTED_TEAM_ID, EXPECTED_TEAM, EXPECTED_URL)
        if identity != expected:
            raise SlackError(
                "Unexpected Slack identity: expected "
                f"{EXPECTED_TEAM} ({EXPECTED_TEAM_ID}, {EXPECTED_URL}), got "
                f"{identity[1]} ({identity[0]}, {identity[2]})"
            )
        output(
            {
                "ok": True,
                "url": result.get("url"),
                "team": result.get("team"),
                "user": result.get("user"),
                "team_id": result.get("team_id"),
                "user_id": result.get("user_id"),
                "is_enterprise_install": result.get("is_enterprise_install", False),
                "_workspace": WORKSPACE,
            }
        )
    elif command == "channels":
        types = args[0] if args else "public_channel,private_channel,im,mpim"
        output(
            client.collect(
                "conversations.list",
                "channels",
                types=types,
                limit=200,
                exclude_archived="true",
            )
        )
    elif command in {"users", "user-lookup"}:
        result = client.collect("users.list", "members", limit=200)
        if command == "users":
            output(result)
        else:
            lookup = {}
            for member in result["members"]:
                profile = member.get("profile", {})
                name = (
                    profile.get("display_name")
                    or profile.get("real_name")
                    or member.get("real_name")
                    or member.get("name")
                    or member.get("id")
                )
                lookup[member["id"]] = name
            output(lookup)
    elif command == "history":
        require_args(args, 1, "history CHANNEL_ID [limit]")
        limit = min(int(args[1]) if len(args) > 1 else 50, 100)
        output(client.call("conversations.history", channel=args[0], limit=limit))
    elif command == "replies":
        require_args(args, 2, "replies CHANNEL_ID THREAD_TS")
        output(
            client.collect(
                "conversations.replies",
                "messages",
                channel=args[0],
                ts=args[1],
                limit=200,
            )
        )
    elif command == "search":
        require_args(args, 1, "search QUERY [count]")
        count = min(int(args[1]) if len(args) > 1 else 20, 100)
        output(
            client.call(
                "search.messages",
                query=args[0],
                count=count,
                sort="timestamp",
                sort_dir="desc",
            )
        )
    elif command == "permalink":
        require_args(args, 2, "permalink CHANNEL_ID MESSAGE_TS")
        output(client.call("chat.getPermalink", channel=args[0], message_ts=args[1]))
    elif command == "send":
        require_args(args, 2, "send CHANNEL_ID MESSAGE [THREAD_TS]")
        output(
            client.call(
                "chat.postMessage",
                channel=args[0],
                text=args[1],
                thread_ts=args[2] if len(args) > 2 else None,
                unfurl_links="true",
                unfurl_media="true",
            )
        )
    else:
        raise SlackError(f"Unknown command {command!r}\n\n{usage()}")


if __name__ == "__main__":
    try:
        main()
    except (SlackError, ValueError) as error:
        output({"ok": False, "error": str(error)})
        raise SystemExit(1)
