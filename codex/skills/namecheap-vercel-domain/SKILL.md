---
name: namecheap-vercel-domain
description: Configure and verify Namecheap BasicDNS for Vercel deployments. Use when the user asks to connect, deploy, repeat, or troubleshoot a Vercel custom domain whose DNS is managed in Namecheap, including adding domains with the Vercel CLI, extracting Vercel's required A/CNAME records, changing Namecheap host records in the dashboard, removing Namecheap parking or redirect records, and validating HTTP/HTTPS.
---

# Namecheap Vercel Domain

## Rule

Use Vercel as the source of truth for DNS records. Do not guess the required A or CNAME values when `vercel domains verify` can report them.

## Tools

- Use the Vercel CLI for deploys, project linking, domain attachment, and verification.
- Use browser control for Namecheap. If the user is not logged in, ask them to log in; do not enter or store credentials.
- Use `dig`, `curl`, and the bundled verifier script for outside-the-dashboard checks.

## Vercel

1. Deploy or identify the production Vercel project.
   - New static folder: `npx --yes vercel@latest deploy <path> --prod --yes`
   - Existing linked project: run from the project directory or pass `--cwd`.
2. Add the apex and `www` domains unless the user asks for only one host.
   - `npx --yes vercel@latest domains add example.com <project>`
   - `npx --yes vercel@latest domains add www.example.com <project>`
3. Ask Vercel for DNS requirements.
   - `npx --yes vercel@latest domains verify example.com`
   - `npx --yes vercel@latest domains verify www.example.com`
4. Follow the `recommended.records` from `verify`.
   - Prefer `verify` over `inspect`; `inspect` can show generic fallback advice.
   - Common apex pattern: two `A` records for `@`.
   - Common `www` pattern: one `CNAME` record for `www`.

## Namecheap

1. Open `https://ap.www.namecheap.com/domains/domaincontrolpanel/<domain>/domain`.
2. Confirm the domain uses Namecheap BasicDNS before editing Host Records.
   - If it uses Custom DNS or another nameserver set, stop and decide whether to change nameservers or edit DNS at the current provider.
3. On the Domain tab, clear Namecheap product features that conflict with Vercel.
   - Turn off Parking Page if it is on.
   - Remove Redirect Domain entries here, not from the Host Records table. Namecheap may show a URL Redirect Record in Advanced DNS, but deleting it there can fail with `Failed to retrieve the record!`.
4. Open Advanced DNS: `https://ap.www.namecheap.com/domains/domaincontrolpanel/<domain>/advancedns`.
5. In Host Records, make the records match Vercel exactly.
   - Edit the existing `www` parking CNAME if present, or remove it and add the Vercel CNAME.
   - Add the Vercel apex `A` records for host `@`.
   - Remove duplicate/conflicting records for the same host/type.
   - Leave Mail Settings, email forwarding, SPF/TXT, MX, DNSSEC, Dynamic DNS, and personal nameservers alone unless the user specifically asks.
6. Save each modal with `Save Changes`.
   - After the modal closes, check whether a table-level `Save All Changes` link is visible in Host Records; click it if it is active.
   - When confirming a record deletion, click plain `Yes`; do not click the "do not show this message again" option.

## Verify

Run the bundled verifier after Namecheap changes:

```bash
/Users/alejo/.codex/skills/namecheap-vercel-domain/scripts/verify-vercel-namecheap-domain.sh example.com
```

Also run the direct Vercel checks:

```bash
npx --yes vercel@latest domains verify example.com
npx --yes vercel@latest domains verify www.example.com
```

Success criteria:

- Authoritative DNS returns the Vercel records from Namecheap's nameservers.
- Vercel reports `configured_correctly` for each attached domain.
- `http://example.com` and `http://www.example.com` serve the deployment.
- `https://example.com` and `https://www.example.com` return `200` after Vercel finishes certificate issuance.

## SSL timing

If DNS verifies but HTTPS fails, treat it as certificate provisioning until proven otherwise.

- Retry for a few minutes.
- Use `curl -k -I https://example.com` to confirm the request reaches Vercel.
- Use `openssl s_client -connect example.com:443 -servername example.com` to inspect the served certificate.
- Once the certificate SAN includes the domain, retry strict `curl -I https://example.com`.

## Failure modes

- **Namecheap login page:** ask the user to log in in the browser and tell you when ready.
- **Codex Chrome Extension unavailable:** use the in-app browser if the user is logged in there; otherwise ask the user to enable the extension or sign in where browser control works.
- **`Failed to retrieve the record!` deleting a URL redirect:** remove the redirect on the Domain tab, then return to Advanced DNS.
- **Vercel project not linked:** run `vercel link --cwd <dir> --yes` or pass the project name explicitly.
- **Git or repo state is irrelevant to DNS:** keep source/deploy commits tidy if code changed, but do not block DNS work on repository metadata.
