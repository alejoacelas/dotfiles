---
name: slack-80000-hours
description: Connect to and work with the 80,000 Hours Slack workspace using the signed-in user's Slack web-session credentials. Use for 80,000 Hours Slack setup, authentication checks, channel and DM lookup, message search and history, thread retrieval, permalinks, or user-approved message sending.
---

# 80,000 Hours Slack

Use `scripts/slack.py` for every Slack command. It pins the bundled client to the
`80000hours` workspace so another configured workspace cannot be selected by
accident.

Set `SKILL_DIR` to the directory containing this file, then run commands as:

```bash
python3 "$SKILL_DIR/scripts/slack.py" auth
python3 "$SKILL_DIR/scripts/slack.py" channels "public_channel,private_channel"
python3 "$SKILL_DIR/scripts/slack.py" search "in:using-ai after:2026-07-01" 20
```

## Setup

Never ask the user to paste Slack tokens into chat or pass them as command-line
arguments. They are equivalent to the user's signed-in Slack session.

For Codex setup:

1. Read and use the available Chrome-control skill. Open or claim a regular Chrome
   tab at `https://app.slack.com/client/T02GR4NPU/` and let the user sign in if needed.
2. Focus that Slack tab before opening DevTools. A console showing
   `https://www.google.com/search/warmup.html` is attached to the wrong target.
3. Do not inspect cookies or local storage through browser-control APIs. Hand the
   signed-in Slack tab back to the user for credential extraction.
4. Tell the user to run `location.href` in DevTools and verify that it begins with
   `https://app.slack.com/client/T02GR4NPU/`.
5. Tell the user to run this reviewed expression in the Console and copy its
   `xoxc-…` result without posting it in chat:

   ```javascript
   JSON.parse(localStorage.getItem('localConfig_v2')).teams['T02GR4NPU'].token
   ```

6. Tell the user to copy the `d` cookie's `xoxd-…` value from DevTools → Application
   → Cookies → `https://app.slack.com`. If `d` is absent, reload the signed-in Slack
   tab and check the same cookie store again.
7. Tell the user to run `navigator.userAgent` in the Console and copy the result.
8. Ask the user to run the following in their own terminal. The prompts hide both
   values and write them only to the ignored local config:

   ```bash
   python3 "$SKILL_DIR/scripts/setup.py"
   ```

9. After setup, ask the user to clear the current macOS clipboard with
   `pbcopy </dev/null` and remove the entries from any clipboard-history manager
   they use.
10. After the user says setup is complete, verify it:

   ```bash
   python3 "$SKILL_DIR/scripts/slack.py" auth
   ```

Expected identity: team `80,000 Hours`, team ID `T02GR4NPU`, workspace URL
`https://80000hours.slack.com/`. Stop if authentication resolves to another team.
If Slack denies access, confirm that the user is a member of this workspace. If auth
fails after saving, rerun `setup.py`, answer `y` to replace the config, and extract
fresh values from the same signed-in Chrome tab.

If `localConfig_v2` is missing, first check `location.href`. If the URL is correct,
list only matching key names with
`Object.keys(localStorage).filter(k => /localConfig/i.test(k))`; do not expose
storage values while diagnosing. If exactly one versioned `localConfig` key is
returned, substitute that exact key for `localConfig_v2` in the reviewed expression.
Do not guess among multiple keys. If the `d` cookie remains absent after a reload,
sign out and back into the 80,000 Hours workspace in the same Chrome profile, then
check again; stop if it is still absent because Slack's session shape may have
changed.

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
