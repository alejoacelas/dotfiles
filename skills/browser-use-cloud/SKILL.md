---
name: browser-use-cloud
description: Default browser control for website interaction, authenticated browsing, screenshots, and web UI testing using Browser Use Cloud and Playwright. Use local browser tools when the task needs localhost, local extensions, or an existing desktop tab.
---

# Browser Use Cloud

Use `~/best/dotfiles/bin/bu-cloud` for direct control of a managed Chrome through
the v4 SDK. It loads the API key from personal 1Password into an ignored `.env`.
Profile mappings and session connection details stay local and Git-ignored.

Choose `personal`, `work`, or `clean` explicitly from the task's account context.
`work` is the employer identity. Ask if the required identity is ambiguous.
Use a unique session name per task; never share a live profile between tasks
that could overwrite its state. Profile cookies grant account access, but do not
expand the user's authorization to send messages, buy things, or change accounts.

```sh
~/best/dotfiles/bin/bu-cloud start my-task --profile personal
~/best/dotfiles/bin/bu-cloud exec my-task <<'PY'
page.goto('https://example.com')
print(page.title())
print(page.locator('body').inner_text()[:3000])
PY
~/best/dotfiles/bin/bu-cloud stop my-task
```

`exec` exposes Playwright's synchronous `browser`, existing `context`, and `page`.
Use locators and targeted reads; save screenshots with `page.screenshot(path=...)`.
Page globals do not survive separate calls, but tabs and browser state do.
`start` returns a live-view URL for watching or completing a login.
Use `status` to list sessions, and `profiles` to check local profile mappings.

Stop the task's session when finished, including after errors. `stop` calls the
v4 stop endpoint, ending billing and saving profile changes. Disconnecting
Playwright does neither. Sessions have a 15-minute timeout as a backstop;
set `start --timeout MINUTES` when the task needs longer. Do not leave a browser
running after your turn unless the user needs it kept open. Sessions use a UK
proxy by default; `--country` selects a different country or `none` disables it.

The installed `browser-use` CLI supports local Chrome, but its current cloud
daemon uses v3. Use `bu-cloud` for v4 cloud control. For natural-language hosted
Agent tasks or advanced SDK work, read the [current Cloud docs](https://docs.browser-use.com/cloud/llms.txt)
and use `browser_use_sdk.v4`; a hosted agent is separate from direct browser control.

## Refresh logins

The official `profile-use` helper imports cookies, not passwords, extensions,
local storage, or passkeys. Expired or device-bound logins may require sign-in
through the live view. Keep passwords and MFA in 1Password and retrieve only
the credential needed for the requested task.

After the user requests a profile refresh, use `bu-cloud sync personal` or
`bu-cloud sync work`. This updates the mapped cloud profile from local Chrome.
It uploads all cookies in that selected local profile. Stop its cloud sessions
before syncing and start a new session afterward. Initial setup authorization
does not authorize future unattended uploads of newly acquired logins.
