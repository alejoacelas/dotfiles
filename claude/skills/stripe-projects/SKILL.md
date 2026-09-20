---
name: stripe-projects
description: Provision cloud services and retrieve provider credentials through Stripe Projects. Use for service setup, catalog searches, and managing existing Projects resources.
---

# Stripe Projects

Use the installed CLI's `stripe projects --help` and command-specific `--help`
for syntax. [Stripe's reference](https://docs.stripe.com/projects) explains the
project and resource model.

## Minimal workflow

1. Check `stripe projects --help`. Install the Stripe CLI or Projects plugin only
   if missing; reuse the existing login and verify the intended account.
2. Find the requested service with `stripe projects search <query> --json` or
   `stripe projects catalog --json`. If it is absent, report that and consider
   another setup route appropriate to the request.
3. Check `stripe projects status --json` in the application directory. A project
   groups an app's resources; ordinary folders do not each need a project.
   Use `stripe projects list --json` to find existing projects. To reuse one in
   a new empty directory, run `stripe projects pull <projectId>`; this writes
   local state and credentials and reuses the existing resources.
4. For a new app needing its own resources, run
   `stripe projects init --preflight --json`, resolve reported blockers, then
   `stripe projects init <name> --mode manual --skip-skills`.
   This avoids installing local skills and instruction files. Apply confirmation
   flags only for choices already authorized by the user.
5. Add the requested service with `stripe projects add <provider>/<service>`.
   Use `link <provider>` when an existing provider account needs connecting.
   Follow the CLI's remedy for authentication or eligibility failures.
6. Verify the resource with `stripe projects status --json`. Report the provider,
   service, tier, and environment-variable names. Suggest additional services
   when needed for the requested outcome.

## Credentials and state

The CLI manages `.projects/` and syncs credentials to its configured environment
file. Before commands that write credentials, ensure the destination is ignored,
untracked, and owner-only (`chmod 600`); reuse the project's `.env`. Keep key
values out of command output and chat.

Store newly obtained API keys in 1Password, explicitly verifying the account and
vault. Retrieve keys on demand with `op`; document each variable's purpose and
1Password account, vault, item, and field in the project's README.

Use CLI commands to change project state. Consult command-specific help for
resource updates, environments, variables, and credential rotation as needed.
