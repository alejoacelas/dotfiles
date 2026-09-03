---
name: deploy-vercel
description: Deploy or redeploy a site, app, or folder to Vercel production and verify the production URL. Use for every Vercel deployment. When the request includes or suggests a custom domain, also attach it, configure its Namecheap BasicDNS records when Namecheap hosts its DNS, and verify DNS and HTTPS.
---

# Deploy to Vercel

Deploy the requested project to Vercel production, then configure any requested custom
domain.

## Deploy

1. Inspect the project for an existing `.vercel/project.json` and Vercel configuration.
2. Deploy production with the current project link when it exists:

   ```bash
   npx --yes vercel@latest deploy --cwd <path> --prod --yes
   ```

3. If the project is not linked, link it to the intended Vercel project, then deploy:

   ```bash
   npx --yes vercel@latest link --cwd <path> --yes --project <project>
   npx --yes vercel@latest deploy --cwd <path> --prod --yes
   ```

4. Read the deployment output and identify the stable production alias. Verify that URL,
   not only the immutable deployment URL:

   ```bash
   curl -fsSIL https://<production-alias>/
   ```

Treat a non-successful HTTP response, Vercel build failure, or protected production alias
as an incomplete deployment. Report the exact failure instead of describing it as live.

## Custom domains

If the user names or proposes a domain anywhere in the request, continue with
[`references/namecheap-domain.md`](references/namecheap-domain.md) after the production
alias works. Read the reference before attaching the domain or changing DNS; it contains
the complete workflow, boundaries, verification, and recovery steps. Do not guess DNS
records.

## Boundaries

- Preserve the existing Vercel project, environment variables, build settings, and aliases
  unless the user asks to change them.
- Keep `.vercel/` and `.env.local` out of public repositories.
- Do not enter account credentials. If Vercel requires login, ask the user to complete it.
