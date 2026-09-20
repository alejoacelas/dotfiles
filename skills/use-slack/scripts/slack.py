#!/usr/bin/env python3
"""Minimal Slack web-session client for explicitly configured EA workspaces."""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"
API_ROOT = "https://slack.com/api/"
WORKSPACES = {
    "80000hours": {
        "team_id": "T02GR4NPU",
        "team": "80,000 Hours",
        "url": "https://80000hours.slack.com/",
    },
    "ai-uplift": {
        "team_id": "T094GSSSF3M",
        "team": "AI Uplift for EA",
        "url": "https://ai-uplift.slack.com/",
    },
}


class SlackError(RuntimeError):
    pass


def load_config(workspace: str | None) -> tuple[dict, dict, str]:
    if not CONFIG_PATH.exists():
        raise SlackError(f"Missing config: run {SKILL_DIR / 'scripts' / 'setup.py'}")
    with CONFIG_PATH.open() as handle:
        config = json.load(handle)
    workspace = workspace or config.get("default_workspace") or "80000hours"
    if workspace not in WORKSPACES:
        raise SlackError(
            f"Unknown workspace {workspace!r}; choose one of: {', '.join(WORKSPACES)}"
        )
    credentials = config.get("workspaces", {}).get(workspace)
    if not credentials:
        raise SlackError(f"Config has no {workspace!r} workspace")
    for key, prefix in (("xoxc_token", "xoxc-"), ("xoxd_token", "xoxd-")):
        if not str(credentials.get(key, "")).startswith(prefix):
            raise SlackError(f"Invalid {key}: expected a value beginning with {prefix}")
    return config, credentials, workspace


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
    return """Usage: slack.py [-w WORKSPACE] COMMAND [ARGS]

Workspaces:
  80000hours (default)
  ai-uplift

Commands:
  auth
  channels [types]
  users
  user-lookup
  history CHANNEL_ID [limit]
  replies CHANNEL_ID THREAD_TS
  search QUERY [count]
  sent-dms [count]
  permalink CHANNEL_ID MESSAGE_TS
  send CHANNEL_ID MESSAGE [THREAD_TS]
"""


def require_args(args: list[str], minimum: int, command_usage: str) -> None:
    if len(args) < minimum:
        raise SlackError(f"Usage: slack.py {command_usage}")


def parse_command(argv: list[str]) -> tuple[str | None, str, list[str]]:
    workspace = None
    args = list(argv)
    if args and args[0] in {"-w", "--workspace"}:
        if len(args) < 2:
            raise SlackError("Missing value after --workspace")
        workspace = args[1]
        del args[:2]
    if not args:
        return workspace, "help", []
    return workspace, args[0], args[1:]


def display_name(member: dict) -> str:
    profile = member.get("profile", {})
    return (
        profile.get("display_name")
        or profile.get("real_name")
        or member.get("real_name")
        or member.get("name")
        or member.get("id")
    )


def user_lookup(client: SlackClient) -> dict[str, str]:
    result = client.collect("users.list", "members", limit=200)
    lookup = {}
    for member in result["members"]:
        lookup[member["id"]] = display_name(member)
    return lookup


def resolve_user(client: SlackClient, user_id: str, lookup: dict[str, str]) -> str:
    if user_id in lookup:
        return lookup[user_id]
    try:
        member = client.call("users.info", user=user_id).get("user", {})
    except SlackError:
        return user_id
    name = display_name(member)
    lookup[user_id] = name
    return name


def authenticated_identity(client: SlackClient, workspace: str) -> dict:
    result = client.call("auth.test")
    expected = WORKSPACES[workspace]
    identity = (result.get("team_id"), result.get("team"), result.get("url"))
    expected_identity = (expected["team_id"], expected["team"], expected["url"])
    if identity != expected_identity:
        raise SlackError(
            "Unexpected Slack identity: expected "
            f"{expected['team']} ({expected['team_id']}, {expected['url']}), got "
            f"{identity[1]} ({identity[0]}, {identity[2]})"
        )
    return result


def main() -> None:
    workspace_arg, command, args = parse_command(sys.argv[1:])
    if command in {"-h", "--help", "help"}:
        print(usage())
        return

    config, credentials, workspace = load_config(workspace_arg)
    client = SlackClient(credentials)

    if command == "auth":
        result = authenticated_identity(client, workspace)
        output(
            {
                "ok": True,
                "url": result.get("url"),
                "team": result.get("team"),
                "user": result.get("user"),
                "team_id": result.get("team_id"),
                "user_id": result.get("user_id"),
                "is_enterprise_install": result.get("is_enterprise_install", False),
                "_workspace": workspace,
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
        if command == "users":
            output(client.collect("users.list", "members", limit=200))
        else:
            output(user_lookup(client))
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
    elif command == "sent-dms":
        count = min(int(args[0]) if args else 5, 100)
        if count < 1:
            raise SlackError("Count must be at least 1")
        identity = authenticated_identity(client, workspace)
        lookup = user_lookup(client)
        direct_messages = client.collect(
            "conversations.list", "channels", types="im", limit=200
        )["channels"]
        recipients = {
            channel["id"]: channel.get("user")
            for channel in direct_messages
            if channel.get("id") and channel.get("user")
        }
        found = []
        page = 1
        while len(found) < count:
            result = client.call(
                "search.messages",
                query=f"from:{identity['user']}",
                count=100,
                page=page,
                sort="timestamp",
                sort_dir="desc",
            )
            matches = result.get("messages", {}).get("matches", [])
            for match in matches:
                channel_id = match.get("channel", {}).get("id")
                recipient_id = recipients.get(channel_id)
                if not recipient_id:
                    continue
                found.append(
                    {
                        "to": resolve_user(client, recipient_id, lookup),
                        "to_id": recipient_id,
                        "text": match.get("text", ""),
                        "ts": match.get("ts"),
                        "channel_id": channel_id,
                        "permalink": match.get("permalink"),
                    }
                )
                if len(found) == count:
                    break
            paging = result.get("messages", {}).get("paging", {})
            if not matches or page >= int(paging.get("pages", page)):
                break
            page += 1
        output({"ok": True, "messages": found, "_workspace": workspace})
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
