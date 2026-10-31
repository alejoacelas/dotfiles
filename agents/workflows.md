# Workspace procedures

Read only the section relevant to the task.

## Creating or moving projects

- Follow [projects/AGENTS.md](/Users/alejo/best/projects/AGENTS.md) for starting,
  reviewing and organizing projects.
- Read the destination's `AGENTS.md` before creating or moving anything there.
- Follow the folder's archive rules. Record moves with their old path and reason;
  preserve repository history and privacy.

## Machines and credentials

For personal credentials approved for agent access, use
`~/best/dotfiles/bin/op-agent` on the Mac (`~/.local/bin/op-agent` on the server).
It authenticates without prompts to `mac-agents` or `server-agents` in the
personal 1Password account. Use `op-agent run` with secret references to inject
credentials into a command, or `op-agent inject` for an ignored `.env`.
Authenticate for authorized tasks without asking again; never print, commit,
or disclose secret values. Existing action-specific approval rules still apply.
Use ordinary `op --account my.1password.com` for items outside these vaults.

On the agent server, run agent work as the `agent` user (`sudo -iu agent`). It
has no sudo or `op-agent`; `gh`, `gog` and git pushes go through a credential
broker that never returns the tokens. To give it an API key, add a broker
route ([agent user setup](/Users/alejo/best/projects/2026-09-26-agent-server/docs/setup.md#agent-user)).

The two Macs SSH into each other and into the agent server over Tailscale:
`ssh mac-air-2` (the other MacBook Air), `ssh alejo-m4` (the main Mac) and
`ssh agent-server`.

SSH sessions on a Mac can't read the keychain, so start Claude there inside
`tmux` with `CLAUDE_CODE_OAUTH_TOKEN` injected by `op-agent run --no-masking`
(masking breaks Claude's terminal UI) from
`op://mac-agents/6drosdmzu2qb3jefhsh3d5b7dy/credential`.

## Replacing a Google Docs tab

To replace a whole Google Docs tab, write the new content into a new tab, compare it
with the original, carrying over any edits made there since your last write, then
delete the original. Writing over an existing tab can keep its old formatting, such
as turning every paragraph into a bullet.

## Orca Markdown

Use collapsibles only as `<details class="orca-details">` with a plain `<summary>`
and a Markdown body. Never nest them. Escape HTML-like strings inside collapsible
code blocks. Split HTML-bearing files before 50,000 characters.

## Local macOS applications

Sign apps requiring Accessibility, Screen Recording, microphone, camera or similar
grants with a stable local identity. Ad-hoc signatures change identity on each build,
leaving enabled privacy toggles that the rebuilt app cannot use. Fail the build when
its expected signing identity is missing; never silently fall back to ad-hoc signing.

## Markdown review

Use Zed by default to open Markdown for human review.
Open files with `open -a Zed "/absolute/path/to/file.md"` on macOS.
After the user reviews or edits a document, reread it before making further changes.
