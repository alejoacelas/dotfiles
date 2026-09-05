# Migration verification

Validated on this Mac on 2026-09-05 with Codex 0.153.0 and Claude Code 2.1.261.

- The full installer completed successfully; the configuration check reports no hard failures.
  Existing differences inside deferred projects remain for their later migration.
- All 3,293 entries in the original best Git tree have a live destination or an explicit
  preservation location. Original human-edit history is preserved verbatim, including whitespace.
- Fifteen tests cover context composition, local-text preservation, edited generated text,
  missing sources, private-source refusal, folder moves, atomic replacement checks and
  marked-edit evidence in ordinary and newly initialized Git folders.
- Freshness probes started with an old generated value and a newer shared source. Codex
  with the separate CLI profile, Codex with Orca's account home, Claude Code, and Codex's
  app-server thread/turn API all returned the new value without reading files or using tools.
- The app-server probe checks the app protocol, not clicks through each desktop UI.
- Codex initially skipped the new untrusted hook. The installer now uses the supported
  hooks/list and config/value/write APIs to trust only its exact installed handler.
- Orca's migration automation completed its first scheduled precheck in 237 ms and skipped
  launching an agent because sessions were still open.

Detailed probe transcripts, original Git bundles, dirty-work snapshots and move/repository
ledgers are private local records at `~/.local/state/best-migration/2026-09-05/`.
The private shared-source repository holds the deferred migration plan and archive record.
