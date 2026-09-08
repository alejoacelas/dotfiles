# gdoc

Google Docs tools for agents: the upstream CLI and an MCP wrapper built on it.

- Install: `uv tool install git+https://github.com/LucaDeLeo/gdoc.git`
- OAuth client: `~/.config/gdoc/credentials.json` → symlink to
  `~/.config/credentials/google-oauth-client-mac-air-2020-personal.json`
- Auth: `gdoc auth --account <email>`; tokens land in `~/.config/gdoc/accounts/<email>/`.
  Authorized: alejoacelas@gmail.com (default) and alejo@habere.org (via
  `GDOC_CLIENT_CREDENTIALS=~/.config/credentials/google-oauth-client-mac-air-2020-habere.json`).
- `cli/` is an up-to-date clone of https://github.com/LucaDeLeo/gdoc, kept here to
  patch behavior or send PRs.
- `mcp/` wraps the CLI as typed MCP tools and a macOS desktop extension, following
  https://github.com/jpaddison3/dharma.

- `notes/` keeps comparison, improvement and integration research in its own repository.
