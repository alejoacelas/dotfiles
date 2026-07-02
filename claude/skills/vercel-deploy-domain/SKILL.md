---
name: vercel-deploy-domain
description: Deploy a folder to Vercel production and point a Namecheap custom domain at it. Use when the user wants to ship a site/app to Vercel and connect a domain they own at Namecheap — e.g. "deploy this app to Vercel on mydomain.com", "put this on Vercel and hook up my Namecheap domain".
---

# Deploy to Vercel + connect a Namecheap domain

Two halves: **Vercel** is pure CLI (already authed as `alejoacelas-7294`); **Namecheap**
DNS is a browser step, automated by `scripts/namecheap-dns.mjs`. Apex domains use an
A record to `76.76.21.21` + `CNAME www → cname.vercel-dns.com` — the setup every one of
the user's domains (`alejo.ink`, `alejoacelas.com`, …) already uses.

## 1. Deploy to Vercel (production)
From the folder you want to serve (a static site needs no build config):

```bash
APP=/abs/path/to/app
npx vercel project add <project>                         # once; skip if it exists
npx vercel link  --cwd "$APP" --yes --project <project>
npx vercel deploy --cwd "$APP" --prod --yes              # prints the production URL
```

Verify against the **production alias** (`*.vercel.app`), not the immutable deploy URL
(that one sits behind deployment-protection and returns a "Redirecting…" auth page):

```bash
curl -sI https://<project>-<hash>.vercel.app/ | head -3   # expect 200
```

Re-run `vercel deploy --prod` to ship again — it's cheap and idempotent.

## 2. Attach the domain
```bash
npx vercel domains add <domain> <project>     # assigns the domain to the project
npx vercel domains inspect <domain>           # shows the required records / the A-record IP
```
Vercel warns "not configured properly" until DNS is set, and recommends *either* an A
record *or* switching nameservers. **Use the A record** (keeps Namecheap as DNS host) —
that's option 3. The nameserver "✘" in the output is the path you're *not* taking; ignore it.

## 3. Set the Namecheap DNS records
```bash
cd ~/.claude/skills/vercel-deploy-domain/scripts
npm install && npx playwright install chromium     # once
node namecheap-dns.mjs --domain <domain>           # --ip / --cname to override defaults
```
A Chrome window opens; **log into Namecheap the first time** (the session is saved to
`.namecheap-profile/`, gitignored, so reruns are silent). The script removes the parking
records, sets `A @ → 76.76.21.21` and `CNAME www → cname.vercel-dns.com`, then reloads and
verifies. Namecheap's UI sometimes flashes a benign "Failed to retrieve the record!" — the
change still lands; the script reloads to confirm.

Doing it by hand instead is ~1 minute: Domain List → **Advanced DNS** → set those two
records, delete the `URL Redirect @` and `CNAME www → parkingpage`.

## 4. Confirm it's live
```bash
dig +short <domain> A            # → 76.76.21.21
dig +short www.<domain> CNAME    # → cname.vercel-dns.com.
curl -sI http://<domain>/        # → 200 once DNS propagates (usually minutes)
curl -sI https://<domain>/       # → 200 after Vercel auto-issues the TLS cert (a few min later)
```

## Notes
- `vercel link` writes `.vercel/` and `.env.local` into the app folder and gitignores them
  — keep them out of any public repo (they hold project/org IDs + an OIDC token).
- Vercel may hand back a different apex IP in `domains inspect`; pass it via `--ip`.
- Auth (login/passwords) is always the user's to do — the skill never enters credentials.
