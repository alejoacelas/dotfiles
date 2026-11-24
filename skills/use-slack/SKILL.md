---
name: use-slack
description: Connect to and work with the AI Uplift for EA Slack workspace using the signed-in user's Slack web-session credentials. Also reads the Impact Ops workspace, which Alejo has left. Use for setup, authentication checks, channel and DM lookup, message search and history, thread retrieval, permalinks, or user-approved message sending.
---

# Slack workspaces

Use `scripts/slack.py` for every Slack command. It defaults to `ai-uplift`. The client
checks the exact team identity before authentication or sent-DM queries.

Alejo left Impact Ops in early November 2026 and no longer uses its Slack. `-w impact-ops`
stays only for reading old history when he asks, while its saved session still works.
Never send there, and don't ask him to sign in again or refresh that session.

Set `SKILL_DIR` to the directory containing this file, then run commands as:

```bash
python3 "$SKILL_DIR/scripts/slack.py" auth
python3 "$SKILL_DIR/scripts/slack.py" sent-dms 5
```

## Setup

Run `auth` for the selected workspace. If authentication fails or credentials
are missing, follow [setup](references/setup.md), then rerun `auth`. Verify the
returned team matches the selected workspace before continuing.

## Reading Slack

Resolve Slack user IDs before presenting or attributing messages:

```bash
python3 "$SKILL_DIR/scripts/slack.py" user-lookup
```

Use the resulting ID-to-name map for history, replies, and search results. Slack
Connect users may not appear in that map; use the `user_profile` embedded in shared
channel messages and state any unresolved identity rather than guessing.

Useful commands:

```bash
python3 "$SKILL_DIR/scripts/slack.py" history CHANNEL_ID 50
python3 "$SKILL_DIR/scripts/slack.py" replies CHANNEL_ID THREAD_TS
python3 "$SKILL_DIR/scripts/slack.py" search "QUERY" 50
python3 "$SKILL_DIR/scripts/slack.py" permalink CHANNEL_ID MESSAGE_TS
python3 "$SKILL_DIR/scripts/slack.py" sent-dms 5
```

## Sending Slack

Treat sending as an external side effect. Show the exact destination and final
message to the user and obtain confirmation immediately before running:

```bash
python3 "$SKILL_DIR/scripts/slack.py" send CHANNEL_ID "MESSAGE"
python3 "$SKILL_DIR/scripts/slack.py" send CHANNEL_ID "REPLY" THREAD_TS
```

The connection method was learned from the
[HartreeWorks Slack skill](https://github.com/HartreeWorks/skill--slack); this
package uses its own minimal standard-library client because upstream declares no
redistribution license. Browser tokens use Slack's unofficial web client interface
and can stop working when Slack changes it.
