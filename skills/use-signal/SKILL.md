---
name: use-signal
description: Read Alejo's Signal messages on the Mac, from the archive copied from the agent server (2 Nov 2026 onward) and the Signal Desktop database (older history). Use when he asks what someone said or asked on Signal, wants a Signal conversation found or summarised, or a task needs to check Signal before saying a message wasn't sent or answered.
---

# Signal

Two read-only sources. Set `SKILL_DIR` to the directory containing this file.

## From 2 Nov 2026: the archive

The agent server is a linked device of Alejo's account and archives every message it
receives. The Mac's launchd job `com.alejoacelas.clerk.mirror-archives` copies that archive
to `~/.local/share/signal-archive/messages-YYYY-MM.jsonl` every 15 minutes, so it is at
most about 30 minutes behind. It includes messages Alejo sent from his phone.

```bash
python3 "$SKILL_DIR/scripts/archive.py" --chat Lydia
python3 "$SKILL_DIR/scripts/archive.py" --since 2026-11-03 --json
```

`--chat` matches a person's name or number, or a group's name or id. Messages Alejo sent
show as from `Alejo`. Each line of the raw files is one signal-cli envelope.

## Before 2 Nov 2026: Signal Desktop

`scripts/desktop.py` runs SQL on a copy of the Signal Desktop database, decrypting it with
the key in the macOS keychain. It needs `sqlcipher` (`brew install sqlcipher`). The app
only has what it synced while open, so it can lag days behind; use the archive for
anything recent.

```bash
python3 "$SKILL_DIR/scripts/desktop.py" "SELECT id, name, profileFullName FROM conversations WHERE name LIKE '%Lydia%'"
python3 "$SKILL_DIR/scripts/desktop.py" "SELECT datetime(sent_at/1000,'unixepoch','localtime'), type, body FROM messages WHERE conversationId='<id>' AND body IS NOT NULL ORDER BY sent_at DESC LIMIT 30"
```

`type` is `incoming` or `outgoing`.

Neither source can send. Setup and relinking are in
[clerk's signal/README.md](/Users/alejo/best/inbox/2026-11-clerk/signal/README.md).
