# Granola connection methods

## 1. API (default)

Use `scripts/granola_api.py` with an injected bearer token. It returns the meeting
metadata and verbatim transcript chunks needed by this skill, works headlessly, and
fails visibly when authentication or the application API changes.

## 2. MCP connector (fallback)

Use the official Granola MCP connector when API credentials are unavailable. It
returns transcripts and attendee metadata but may be absent or unauthenticated in a
given runtime.

## 3. Local cache (do not use)

Current Granola builds store transcripts in encrypted `granola.db` and
`cache-v6.json.enc`. The database key is held by an app-scoped macOS Keychain
entitlement: a normal Node or Python process cannot retrieve it, even when running
as the signed-in user. Earlier `storage.dek` and Chromium `safeStorage` recipes no
longer describe the current build.

Do not weaken permissions, scrape secrets from the running app, or reverse-engineer
the cache during a transcript task. Use the API or MCP fallback.
