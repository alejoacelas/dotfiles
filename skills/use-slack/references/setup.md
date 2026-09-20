# Slack setup

Never ask the user to paste Slack tokens into chat or pass them as command-line
arguments. They are equivalent to the user's signed-in Slack session.

For Codex setup:

1. Choose the workspace and team ID: `80000hours` / `T02GR4NPU`, or `ai-uplift` /
   `T094GSSSF3M`.
2. Read and use the available Chrome-control skill. Open or claim a regular Chrome
   tab at `https://app.slack.com/client/TEAM_ID/` and let the user sign in if needed.
3. Focus that Slack tab before opening DevTools. A console showing
   `https://www.google.com/search/warmup.html` is attached to the wrong target.
4. Do not inspect cookies or local storage through browser-control APIs. Hand the
   signed-in Slack tab back to the user for credential extraction.
5. Tell the user to run `location.href` in DevTools and verify that its team ID is
   the one selected above.
6. Tell the user to run this reviewed expression in the Console, replacing `TEAM_ID`,
   and copy its `xoxc-…` result without posting it in chat:

   ```javascript
   JSON.parse(localStorage.getItem('localConfig_v2')).teams['TEAM_ID'].token
   ```

7. Tell the user to copy the `d` cookie's `xoxd-…` value from DevTools → Application
   → Cookies → `https://app.slack.com`. If `d` is absent, reload the signed-in Slack
   tab and check the same cookie store again.
8. Tell the user to run `navigator.userAgent` in the Console and copy the result.
9. Ask the user to run the matching command in their own terminal. The prompts hide
   both values and write them only to the ignored local config:

   ```bash
   python3 "$SKILL_DIR/scripts/setup.py" --workspace ai-uplift
   ```

10. After setup, ask the user to clear the current macOS clipboard with
   `pbcopy </dev/null` and remove the entries from any clipboard-history manager
   they use.
11. After the user says setup is complete, verify it:

   ```bash
   python3 "$SKILL_DIR/scripts/slack.py" --workspace ai-uplift auth
   ```

Expected identities are `80,000 Hours` / `T02GR4NPU` /
`https://80000hours.slack.com/`, and `AI Uplift for EA` / `T094GSSSF3M` /
`https://ai-uplift.slack.com/`. Stop if authentication resolves to another team.
If Slack denies access, confirm that the user is a member of this workspace. If auth
fails after saving, rerun `setup.py --workspace WORKSPACE`, answer `y` to replace
the config, and extract fresh values from the same signed-in Chrome tab.

If `localConfig_v2` is missing, first check `location.href`. If the URL is correct,
list only matching key names with
`Object.keys(localStorage).filter(k => /localConfig/i.test(k))`; do not expose
storage values while diagnosing. If exactly one versioned `localConfig` key is
returned, substitute that exact key for `localConfig_v2` in the reviewed expression.
Do not guess among multiple keys. If the `d` cookie remains absent after a reload,
sign out and back into the selected workspace in the same Chrome profile, then
check again; stop if it is still absent because Slack's session shape may have
changed.

