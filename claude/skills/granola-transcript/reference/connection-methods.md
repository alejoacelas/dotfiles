# Connecting to Granola — methods explored

Four ways to get raw transcripts out of Granola were evaluated. **The MCP connector
won.** Notes below so the choice is reproducible and the fallback is documented.

## 1. ✅ Granola MCP connector (chosen)

The official Granola connector in Claude (`mcp__claude_ai_Granola__*`). Returns
verbatim transcripts, attendees, and folders directly.

- **Pros:** No decryption, no Keychain prompts, no parsing of app internals.
  Officially maintained, so it survives Granola app updates. Returns exactly the
  verbatim transcript we want, with `Me:` / `Them:` speaker labels.
- **Cons:** Requires the claude.ai Granola connector to be enabled. May be absent in
  headless/cron runs.
- **Verdict:** Default. Reliable and durable.

## 2. ⚠️ Local encrypted cache (offline fallback)

Current Granola builds (macOS) store everything under
`~/Library/Application Support/Granola/`, but it is **encrypted** now — the old
plaintext `cache-v3.json` is gone. What's there:

- `cache-v6.json` — small plaintext UI state (no transcripts).
- `cache-v6.json.enc` — the real cache (documents + transcripts), encrypted.
- `supabase.json.enc` — auth tokens, encrypted.
- `granola.db` — encrypted (not a plain SQLite file).
- `storage.dek` — a data-encryption key, itself wrapped with Electron `safeStorage`
  (note the `v10` prefix).

Decryption recipe (use only if the MCP connector is unavailable):

1. Read the `safeStorage` master key from the macOS Keychain:
   `security find-generic-password -w -s "Granola Safe Storage"`
   (service `Granola Safe Storage`, account `Granola Key`). This may pop a Keychain
   permission dialog.
2. Derive an AES-128 key: `PBKDF2-HMAC-SHA1(master_key, salt=b"saltysalt",
   iterations=1003, dklen=16)` (Chromium `safeStorage` scheme).
3. Decrypt `storage.dek` (strip the 3-byte `v10` prefix) with AES-128-CBC, IV =
   16 × `0x20` (space) bytes, then PKCS#7-unpad → this yields the DEK.
4. Use the DEK to decrypt `cache-v6.json.enc` / `supabase.json.enc`. These have **no
   `v10` prefix** — they're a DEK-encrypted blob (AEAD: leading bytes are the nonce,
   trailing bytes the auth tag). The exact AEAD framing must be confirmed against
   the installed build before relying on it.

- **Cons:** Brittle — Granola changes this format between versions (v3 → v6 added
  encryption). Needs a crypto library and Keychain access. Step 4's framing is
  version-specific and unverified here.
- **Verdict:** Fallback only. If you build this, verify end-to-end against the
  current build and pin the Granola version.

## 3. ❌ Granola cloud REST API via extracted token

`https://api.granola.ai/...` with the bearer token from `supabase.json`. Clean once
you have the token — but the token now lives in `supabase.json.enc`, so it requires
the same decryption as method 2 first. No advantage over the MCP connector.

## 4. ❌ Plaintext `cache-v3.json`

The classic community approach (read the unencrypted JSON cache). **Dead** on
current builds — the cache is encrypted (`cache-v6.json.enc`).
