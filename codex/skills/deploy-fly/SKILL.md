---
name: deploy-fly
description: Deploy, migrate, inspect, or troubleshoot Fly.io apps using the correct personal or 80,000 Hours account.
---

# Deploy to Fly

Use `FLY_PERSONAL_TOKEN` or `FLY_80K_TOKEN` from `secretspec.toml`; never replace the cached Fly login.

For an existing deployment, identify its account before changing it. If unclear, inspect apps in both accounts. For a new deployment, infer personal versus 80,000 Hours from the project and folder path; ask the user if still ambiguous.

Preserve existing hostnames, secrets, volumes, and behavior when migrating. Verify health after every change.
