# Cross-agent skill installation

On 2026-08-16, Alejo found that Codex could load Orca's skill while Claude could not.
The community installer had correctly placed Orca under `~/.agents/skills`, but its
Claude compatibility link was dangling because `~/.claude/skills` was itself a link
into this repository. The child link resolved relative to the repository instead of
the home directory the installer expected.

The durable rule is that agent-owned skills directories remain real directories.
`bin/install.sh` now links tracked dotfiles skills into `~/.claude/skills` one at a
time, leaving standard installers free to add their own entries. Codex's
`~/.codex/skills` already followed this pattern.

Checks:

- `~/.claude/skills` is a real directory.
- Every entry under it resolves to a `SKILL.md`.
- Orca's normal installer targets `claude-code`, `codex`, and `universal`.
- Claude and Codex both expose `orca-cli` and `orchestration` after installation.
- Re-running `bin/install.sh` preserves installer-owned entries.

Validation used Orca's normal command:

```sh
orca skills install --skill orca-cli --skill orchestration
```

It installed both skills for `claude-code`, `codex`, and `universal`. A fresh Claude
Code 2.1.233 process then reported both skills available. Re-running `bin/install.sh`
left both links intact, and no skill link under the three user registries was dangling.

## Update test

The same day, a real update tested the path that future Orca releases will use:

```sh
orca skills update --skill orca-cli --skill orchestration
```

The command updated `orca-cli` from source hash `a5a90c9` to `ee3a35c` and correctly
left the already-current `orchestration` unchanged. Afterward:

- both Claude links still resolved to the canonical directories under
  `~/.agents/skills`;
- fresh Claude Code 2.1.233 and Codex CLI 0.147.0 processes both reported
  `orca-cli` and `orchestration` available;
- `bin/install.sh` preserved both installer-owned links;
- `bin/check-agent-config` exited successfully; and
- no link under `~/.claude/skills`, `~/.agents/skills`, or `~/.codex/skills` was
  dangling.

This exercises a real replacement, not only a reinstall or dry run.
