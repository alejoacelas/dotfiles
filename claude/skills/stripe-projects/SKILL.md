---
name: stripe-projects
description: Find and provision cloud services, retrieve provider credentials, and manage existing resources through Stripe Projects.
---

# Stripe Projects

Use `stripe projects --help` and command-specific `--help` for current syntax.
Install the CLI or Projects plugin only if missing. Reuse existing logins and
verify the intended Stripe account before changing resources.

Choose the work needed for the request:

- **Find a service:** `stripe projects search <query> --json` or
  `stripe projects catalog --json`. Report alternatives if the service is absent.
- **Inspect or reuse resources:** `stripe projects status --json` in the app
  directory, or `stripe projects list --json` to find existing projects.
- **Provision:** select the app's existing project, then run
  `stripe projects add <provider>/<service>`. Use `link <provider>` when an
  existing provider account needs connecting.

A project groups an app's resources. Create one only when the app needs its own
resource group: run `stripe projects init --preflight --json`, resolve reported
blockers, then `stripe projects init <name> --mode manual --skip-skills`.
This keeps setup limited to the project, without generated agent instructions.
To connect an existing project in a new empty directory, use
`stripe projects pull <projectId>`; it writes local state and credentials while
reusing existing resources. A folder that only consumes an existing API key can
retrieve that key from 1Password without initializing Stripe Projects.

The CLI manages `.projects/` and writes credentials to the configured environment
file. Before credential writes, ensure the destination is Git-ignored, untracked,
and owner-only (`chmod 600`); reuse `.env`. Store newly obtained keys in 1Password,
verifying the account and vault. Retrieve keys with `op` and document variable
purposes and 1Password account, vault, item, and field in the project's README.
Keep secret values out of command output and chat.

Apply confirmation flags to choices already authorized by the user. Follow the
CLI's remedy for authentication and eligibility failures. Verify provisioning
with `status --json`; report the resource, tier, and variable names. Recommend
additional services when the requested outcome needs them.

For less common operations, consult command help or
[Stripe's reference](https://docs.stripe.com/projects).
