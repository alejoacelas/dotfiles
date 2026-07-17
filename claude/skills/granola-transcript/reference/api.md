# Granola API

Use `scripts/granola_api.py`; do not reimplement requests ad hoc.

## Authentication

Set `GRANOLA_ACCESS_TOKEN` to a current Granola bearer token. Inject it through the
repository's secret manager. Never print it, place it in a command line, commit it,
or read Granola's encrypted token cache.

The script also requires a supported client version. It discovers the installed
macOS app version, or accepts `GRANOLA_CLIENT_VERSION` / `--client-version`.

## Operations

```bash
# List meeting metadata as JSON. Dates are inclusive and interpreted in local time.
python3 scripts/granola_api.py meetings --from 2026-07-01 --to 2026-07-31

# Fetch raw chunks as JSON.
python3 scripts/granola_api.py transcript <document-id> --format json

# Group adjacent chunks into speaker turns for cleaning.
python3 scripts/granola_api.py transcript <document-id> --format text
```

The script calls Granola's current application API:

- `POST https://api.granola.ai/v2/get-documents`
- `POST https://api.granola.ai/v1/get-document-transcript`

Both use `Authorization: Bearer`, `X-Client-Version`, and
`X-Granola-Platform` headers. These are application endpoints rather than a
documented public API; an endpoint or schema change must fail visibly and prompt a
script update.

## Failures

- `401` or `403`: refresh the injected token; then retry once.
- `Unsupported client`: update Granola or pass its current version.
- Unexpected JSON shape: inspect the response without exposing tokens, then update
  the script. Do not guess fields.
- Empty transcript: verify the document ID and recording state. Do not use the
  generated meeting summary as a transcript.
