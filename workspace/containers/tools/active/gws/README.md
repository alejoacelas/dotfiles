# gws

Google Workspace from the terminal via `gog` (https://gogcli.sh) — one CLI for Gmail,
Calendar, Drive, Docs, Sheets, Contacts, Tasks, and more. Upstream:
https://github.com/openclaw/gogcli

- Install: `brew install openclaw/tap/gogcli`
- OAuth clients (from `~/.config/credentials/google-oauth-client-mac-air-2020-*.json`):
  - `default` → personal; authorized as alejoacelas@gmail.com with
    gmail, calendar, drive, docs, sheets, contacts, tasks.
  - `habere` → authorized as alejo@habere.org with the same services; use
    `gog --client habere -a alejo@habere.org …`.
- Config: `~/Library/Application Support/gogcli/`; client secrets + tokens in the keyring.
- Check health: `gog auth list --check`
- `gogcli/` is a clone of the upstream repo, kept here to patch behavior or send PRs.
