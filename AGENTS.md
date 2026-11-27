# Dotfiles

`bin/op-agent` loads the Mac’s `OP_SERVICE_ACCOUNT_TOKEN` from
`~/.config/mac-agents/.env` (directory 700, file 600). Its recovery reference is
1Password account `my.1password.com`, vault `Personal`, item
`1Password service account mac-agents (read-write)`, field `credential`. The service
account `mac-agents-rw` can read and write `mac-agents`. The server's token in
`~/.config/agent-server/op.env` is recovered from item
`1Password service account agent-server (read-write)`; its service account
`server-agents-rw` can read and write `server-agents`. Keep these bootstrap tokens
outside the agent vaults.

`summarize-call` reads `GRANOLA_API_KEY` from its ignored `.env`: account `my.1password.com`,
vault `server-agents`, item `GRANOLA_API_KEY — desk-pipeline`, field `credential`.

Three CLIs keep a token in their own owner-only config, set once with `auth set-token` or
`auth login`. All are in account `my.1password.com`, vault `mac-agents`, field `credential`
unless noted: `exa-pp-cli` uses item `EXA_API_KEY — 2026-09-life-wiki`
(`5ddc3jcbqlhok53vy2buyzhxdy`); `dharma` uses `ASANA_TOKEN — dharma`
(`7gf4h2vxe7u4mz6ftcy5hhmkqu`); `slack-pp-cli` uses field `user_token` of
`AI Uplift Slack API` (`ifyve5el5crjmu3kbvaq2od6ui`). Give `slack-pp-cli` only the user
token: with the bot token also set it calls Slack as the bot, which is in almost no channels
and cannot search.

Archive all files retired from dotfiles in `~/best/archive/2026-11/systems/dotfiles/`.

`codex/config.toml` is the one Codex configuration; Codex writes changes such as
folder trust through its link, so commit them. Verify both clients with fresh sessions after hook changes.

Before editing Claude settings, check that `~/.claude/settings.json` still links to
this repo; Claude can replace that link when saving settings. Neither settings file
is a credential store. Keep secrets in 1Password and ignored, owner-only `.env` files.

Create custom skills in `skills/` by default; the installer exposes them to both
Claude Code and Codex from one maintained source. Use `private-skills/skills/`
for private skills. Reserve
`claude/skills/` and `codex/skills/` for skills that require a particular client.
Run `bin/install.sh` after adding a skill. Keep installed skill
registries as real directories. `summarize-call` is the official call workflow;
do not restore the retired `granola-transcript` skill.
